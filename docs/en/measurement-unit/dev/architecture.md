# Architecture

This page describes how the measurement software is built and how a run proceeds. The states of a run from a usage point of view are shown by the state diagram under [How the unit measures](../usage/measurement-runs.md). Individual classes and functions are under [Code](../../../reference/measurement_software/).

## Entry point

`main.py` first sets the signal handlers, takes over mode files from older versions, loads the `config.toml` into a single configuration tree (`AppConfig`) and sets up logging. It then checks whether an earlier start requested maintenance mode, reads the one-time marker for Manual Mode and the stored command acknowledgements (see [Shutdown, reboot and termination](#shutdown-reboot-and-termination)). `_run()` then builds modem and GNSS receiver, saves data of an interrupted earlier run and takes the run through its states.

If one of these steps before `_run()` fails, the unit goes directly into [maintenance mode](#crashes) without a reboot, because an error this early is usually in a file on the device that a reboot does not change. If the configuration cannot be loaded at all, `run_emergency_link()` only starts the cellular link, from the values that can still be read (`[system] running_on_pi`, `[quectel_cm]`, `[link_watchdog]`, including the values of the last successful start from `last_good_link_settings.json`, as a last resort `vendor/quectel-CM/quectel-CM`). No backend is notified then. Neither persists: once the cause is fixed, the next boot starts normally.

## Configuration

The configuration consists of nested dataclasses (`core/config.py`) that are built from the `config.toml`. The sections for hardware, backend and uploader are mandatory; all others fall back to defaults. All fields are in the [Configuration reference](configuration.md).

`[device] mission_type` is only a marker for the data. The components never distinguish by it. What a drone measurement does differently (no waiting for movement, no end at standstill) results from Manual Mode. Earlier `[profiles.*]` tables in a `config.toml` are ignored with a warning.

## Hardware abstraction

`Modem`, `GNSSReceiver` and `Display` are abstract base classes with fixed methods for opening, closing and querying. Which implementation (e.g. `Quectel`, `NMEASerial`) is built is decided at runtime by a `type` value in the configuration via a small factory. How to add a new implementation is described under [Hardware integration](hardware-integration.md).

## Flow of a run

Every boot goes through a small set of named states (`RunPhaseState`, `core/run_phase.py`): `STARTING_UP`, `RECOVERING_PENDING_DATA`, then depending on the mode the waiting states, `ACTIVE_MEASURING`, `FINALIZING` and `DONE`. In addition there are `STOPPING`, `SHUTTING_DOWN`, `REBOOTING` and `CRITICAL_ERROR`. The heartbeat reports each of these states. In both modes, `quectel-CM` and the heartbeat start immediately at boot, so the unit is reachable during the whole run. After starting `quectel-CM`, the application waits up to 30 seconds for the cellular link before it sends the first heartbeat. It uses more power for this than in the original design, which kept the modem switched off until measuring began.

Every way into measuring leads through `WAITING_FOR_GPS_FIX` (`core/first_fix_wait.py::FirstFixWaiter`), so `ACTIVE_MEASURING` always means that a fix exists. With the first fix, the software sets the system clock from the GNSS time.

**Auto Mode** (`[system] mode = "auto"`, default): The unit waits for a GPS fix, at most `[collector] max_wait_for_first_fix`. If none arrives, the pass ends without a run. Then the movement gate (`core/movement_gate.py`) waits for confirmed movement (`WAITING_FOR_MOVEMENT`). Movement counts as confirmed when the position has moved away from the first fix over several consecutive queries and, if a home position is set, the unit has left it. The run then switches to `ACTIVE_MEASURING`. With `[movement_gate] enabled = false`, the wait for movement is skipped. While waiting, only `shutdown-now` and `reboot-now` take effect.

**Manual Mode** (`[system] mode = "manual"`): The unit boots the same way but then waits in `MANUAL_MODE_IDLE` (`ManualModeLoop`) for a remote command. `start-measuring-now` waits without a time limit for a GPS fix and then starts measuring without regard to movement. `stop-measuring-now` cancels this wait and returns to idle. `run-selftest-now` runs the self-test checks and stays idle. In Manual Mode a run never ends because of standstill. A change of mode (`mode-manual-now`, `mode-auto-now`) only takes effect at the next boot. The earlier name `waiting` is still read as `manual` in `config.toml` and `config_overrides.toml`; `mode-waiting-now` acts like `mode-manual-now`.

**Once manual:** If `stop-measuring-now` ends a run in Auto Mode, it creates the marker `manual_next_boot.json` next to the `config.toml`. The next boot then runs in Manual Mode and removes the marker as soon as it has reached idle. The configured mode does not change.

**Recovery** (`RECOVERY_IDLE`): the one-time boot after the [crash escalation](#crashes). Like Manual Mode, it waits for `start-measuring-now`, but also reports the crash details in the heartbeat. The state is consumed on entry; the boot after that is a normal one.

Whether a remote command is currently applicable is decided by the current run phase, not by the mode at boot. Commands that are not applicable are acknowledged with `not_applicable`.

## Measurement loop

Once measuring, the `Collector` (`core/collector.py`) waits for GPS fixes and records a datapoint (`Datapoint`: cell values, GNSS fix, timestamp, run ID) when the capture gate (`core/capture_gate.py`) allows it:

- `capture_gate = "distance"` (default): after a minimum distance since the last datapoint
- `capture_gate = "time"`: at a fixed time interval

The end at standstill always follows the distance, so the capture gate never changes when a run ends. In Auto Mode a run ends after `[collector] max_idle_time` without real movement; `max_idle_time = 0` switches this off. The clock for this keeps running after the first fix, even if no fixes arrive afterwards. In Manual Mode and in recovery there is no end at standstill. Independently of the mode, a run ends via `stop-measuring-now`. Remote commands are checked after every read of the receiver, even if no fix arrives. A background thread (`KeepModemAliveSender`) keeps the cellular link open with small UDP packets.

## Saving and uploading data

**Power-loss-safe:** Datapoints are appended individually as a JSON line to the run's log and written with `fsync`. An interrupted run loses at most the last, incomplete line. On finalizing, the log is atomically converted into the file that is uploaded. Unfinished logs and temporary files are cleaned up or saved at the next start.

**Run ID:** Every run gets a random UUID4, which the latency tester also uses. Every datapoint and every latency result carries it as `run_id`, also in every log line. A run saved after a power loss thus keeps its ID. The backend treats the field as optional (uploads without an ID end up in a legacy run); it is not in the heartbeat.

**Uploading** (`core/uploader.py`): Pending files go to the backend by HTTPS POST with the headers `X-Device-ID` and `X-Device-Key`, but only if `wlan0` or `wwan0` has an IPv4 address. Measurement files and latency results each have their own endpoint (one request per file or per result), assigned via the prefix of the file name. A run tries to upload at two points where the connection is up anyway: on entering `ACTIVE_MEASURING` and after finalizing (without a run after the wait that ended the pass). In addition there are shutdown, reboot, SIGTERM and `force-upload-now`. A file is only deleted locally after a successful upload.

## Heartbeat, remote commands and remote configuration

The heartbeat (`remote/heartbeat.py`) reports the state of the run to the backend at a fixed interval, including the current run phase (`run_phase`) and the GPS status. The response can contain configuration changes from an allow-list and one-shot commands (e.g. `force-upload-now`, `shutdown-now`). Both are signed with HMAC and are verified and executed by the `RemoteCommandDispatcher`. Configuration changes end up in the local `config_overrides.toml`, which is not checked in.

- **Protection against replay:** Every heartbeat request carries a random `nonce`, which the backend has to return in the signed response body. A response with changes or commands without a matching `nonce` is discarded.
- **Device mode:** `system_mode` (`auto`/`manual`) is one of the changeable fields and, like all others, is reported in `current_config`.
- **Promoting:** `promote-overrides-now` (or `python -m measurement_software.promote_overrides`) writes the current values from `config_overrides.toml` into the `config.toml` as the new base. Comments are preserved because the file is edited with `tomlkit`.
- **Feedback:** The result of every command (`success`, `failed` with an error or `not_applicable`) goes back with the next heartbeat as `executed_commands`. If the backend sends an already executed command again, only the feedback is repeated, not the command. A lost acknowledgement therefore needs no retry logic of its own. When the heartbeat is stopped, pending acknowledgements go out in up to three further heartbeats so that e.g. the confirmation of `stop-measuring-now` is not lost with the end of the process. Commands from these responses are no longer executed.
- **Rejected heartbeats:** If the backend rejects a heartbeat with an HTTP error, the unit logs the reason from the response.

## Shutdown, reboot and termination

| Trigger | Behaviour |
|---|---|
| `shutdown-now`, failed SIM unlock | uniform path via `core/system.py::shutdown()`: finalize and upload pending data, log the reason, power off |
| `reboot-now` | `core/system.py::reboot()`, as above but with a reboot |
| Run ended regularly (`DONE`) | with `[system] running_on_pi = true`, the same path via `shutdown()` |
| `stop-measuring-now` | ends the run like an end at standstill. In Auto Mode it first creates the marker for a one-time start in Manual Mode |
| `SIGTERM` (`systemctl stop`, system shutdown) | sends a last heartbeat with the run phase `stopping`, ends the run, finalizes the log and uploads it if possible, then terminates `quectel-CM`; does not count as a crash |

`shutdown()` and `reboot()` first send a last heartbeat with the run phase `shutting_down` or `rebooting`; on SIGTERM it is `stopping` (with a timeout of at most 3 s so that systemd does not send SIGKILL beforehand). If a remote command triggered them, they acknowledge its ID as `"received"`. They also store the ID next to the `config.toml` (`pending_reboot_ack.toml`/`pending_shutdown_ack.toml`). The next boot then acknowledges it as `success` and does not execute the command again if the backend sends it once more, e.g. because the `"received"` acknowledgement was lost.

## Crashes

An unhandled exception that bubbles all the way up is escalated in stages by `core/crash_policy.py::CrashPolicy`. The state survives reboots.

1. Reboot.
2. If the same error has occurred `[system] crash_same_error_limit` times in a row (or there were `crash_reboot_limit` reboots in a row): reboot into the one-time recovery state (`RECOVERY_IDLE`, see [Flow of a run](#flow-of-a-run)). The configured mode stays unchanged.
3. If an error occurs again after that: reboot into maintenance mode (`core/maintenance_mode.py`).

If a crash cannot be recorded in `crash_state.json`, nothing could detect a reboot loop. The unit then goes into maintenance mode immediately without a reboot and takes over the already running `quectel-CM`.

Maintenance mode is checked early in `main()`, right after loading the configuration. It sends a heartbeat with the run phase `critical_error` and a `critical_error` object (repeated until delivered) and afterwards only operates `quectel-CM` and the monitoring of the cellular link, including the reset of the radio module, so that the unit stays reachable via SSH. GNSS, display and measuring stay off. On SIGTERM it terminates `quectel-CM` itself. It is left by fixing the cause, deleting `crash_state.json` next to the `config.toml` and rebooting. Every crash also leaves `last_crash_report.json` (fingerprint, counter, full traceback), which the next start writes into the log.

## Raspberry Pi

`core/system.py` takes care of the `quectel-CM` process, setting the clock from the GNSS time and shutting down. A signal on a GPIO pin no longer exists. A `shutdown_gpio` in an older `config.toml` is ignored with a warning.

`core/link_watchdog.py` restarts `quectel-CM` if `wwan0` has had no IPv4 address for too long. If several restarts do not help, it resets the modem's radio module (`AT+CFUN`). The modem's serial interface belongs to `core/modem_access.py::ModemAccess` because it is not thread-safe: during measuring the measurement thread takes over the reset at the next query; outside of it, `ModemAccess` opens the interface only briefly for this. If the connection stays away, the wait before every further step doubles up to `max_restart_interval_s`. The watchdog never gives up; the next disturbance starts again at `restart_after_s`.

The software additionally sets the clock via NTP (`core/ntp_clock.py`) as soon as the cellular link is up, because the Pi has no real-time clock and `systemd-timesyncd` only tries before the connection is established. This only runs if `[clock] ntp_server` is set.

## Self-test

`python -m measurement_software.selftest` is a separate entry point that checks every hardware subsystem individually against the real hardware (one AT query, one NMEA sentence, etc.) and reports passed, failed or skipped. No check uploads measurement data or shuts the device down, but `heartbeat` sends a real heartbeat. It is intended for troubleshooting the cabling of a unit over SSH and is independent of the unit tests. Notes on reading the results are under [Setting up a unit](unit-setup.md#checking-the-wiring-before-the-first-run).

## Test patterns

Almost everything in the measurement software is input and output at the edges: serial interfaces, I2C, subprocesses, HTTP, time, threads. The tests therefore replace exactly these boundaries instead of mocking loosely:

- Fakes for `Modem`, `GNSSReceiver` and `Display` implement the real base classes.
- `serial.Serial`, `subprocess` and `urllib.request` are replaced at the point where they are used by fakes that record what was sent.
- Time-dependent logic (`Collector`, `MovementGate`) replaces the clock instead of waiting out real waiting times.

The tests under `tests/` mirror the layout of the package `src/measurement_software`.

## Code style

Readable code takes precedence over comments that explain what it does. Comments are appropriate where a thought cannot be expressed through names or structure alone, but they do not replace that effort.

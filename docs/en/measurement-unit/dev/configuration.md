# Configuration reference

This page describes all fields of the measurement software's `config.toml`. Which settings matter in the field and how to change them in the backend is described under [Configuration](../usage/configuration.md) in the usage documentation.

The `config.toml` is in the root directory of the repository. It is found via a path relative to the installed package, not relative to the working directory, and loaded by `core/config.py::load_config()`. If a section marked **required** is missing, startup aborts with `KeyError`. All other sections and fields fall back to the defaults below.

## Order of sources

Later sources win:

1. Default values of the dataclasses
2. `config.toml`
3. `config.local.toml`: device-specific identity and credentials, set once by hand during setup, see [Setting up a unit](unit-setup.md#device-specific-values)
4. `config_overrides.toml`: changes that the backend sends remotely

A field can only be in one of the last two files: identity and credential fields are excluded from remote configuration. This is checked on import in `core/config_sources.py`.

A value that has proven itself in the `config_overrides.toml` can be made the new base with `python -m measurement_software.promote_overrides` or the remote command `promote-overrides-now`. Every set field is written to its place in the `config.toml` via the mapping `OVERRIDE_FIELD_TARGETS` in `core/config_sources.py` (with `tomlkit`, comments are preserved) and removed from the `config_overrides.toml`. Like any change to the `config_overrides.toml`, this only takes effect at the next `load_config()`, i.e. at the next boot.

## Remote configuration (`config_overrides.toml`)

`FIELD_SPECS` in `core/config_sources.py` is the allow-list: a field can be set remotely exactly if it is listed there with type and value range. Other fields and values with the wrong type or outside the range are discarded with a log line; the rest of the changes are still applied. The types are strict: `bool` fields only accept `true`/`false`, `int` fields no decimal places, floating-point fields no `NaN`/`inf`, choice fields only exactly matching strings.

| Group | Fields |
|---|---|
| Times and triggers | `idle_threshold_s` (`0` = never end because of standstill), `day_end_threshold_s` (accepted, has no effect on the unit yet), `heartbeat_interval_s`, `collector_*` (`capture_gate` `distance`/`time`, `position_threshold`, `capture_interval_s`, `max_wait_for_first_fix`, `wait_log_interval`, `gps_enabled`, `gps_disabled_poll_interval_s`), `movement_gate_*` (`enabled`, `poll_interval_s`, `movement_threshold`, `confirmations_required`, `home_latitude`/`home_longitude`, `home_departure_threshold`), `latency_test_*` (`enabled`, three intervals), `run_status_empty_captures_until_pipeline_broken` |
| Device | `system_mode` (`auto`/`manual`), `device_mission_type` (`ground`/`drone`), `display_enabled`, `display_refresh_interval_s` |
| Modem, GNSS, system | `modem_mode` (`serving_cell`/`sa_scan`), `modem_sim_unlock_poll_attempts`, `modem_sim_unlock_poll_interval`, `gnss_receiver_retries`, `gnss_receiver_retry_delay_s`, `system_running_on_pi` |

The home position may be empty: a JSON `null` resets it. In the file this appears as a list `cleared = ["movement_gate_home_latitude", ...]`, which only accepts fields that may be empty.

`system_mode` is the device mode. The commands `mode-manual-now` and `mode-auto-now` write it here (`mode-waiting-now`, the earlier name, acts like `mode-manual-now`). The backend does not queue it as a configuration change because queued changes are re-sent with every heartbeat and would undo these commands one heartbeat later. `stop-measuring-now` does not change `system_mode` but only creates a marker for a one-time start in Manual Mode (see [Architecture](architecture.md#flow-of-a-run)). A `mode_override.toml` from an older version is taken over once into `system_mode` at startup (an invalid value is discarded, an existing `system_mode` takes precedence) and then deleted. A stored `system_mode = "waiting"` is rewritten once to `"manual"` at startup.

A faulty change never prevents startup. The checks for home position and mode from the [Startup checks](#startup-checks) run again after the changes are applied. If a change violates one of them, the fields involved are discarded and logged, and the value from the `config.toml` remains. A damaged `config_overrides.toml` or a field in it that is no longer valid is likewise ignored.

A heartbeat response with changes or commands is only accepted if its signed text contains the random `nonce` of the corresponding request. An intercepted response therefore cannot be replayed later, and the unit needs neither the time nor a stored counter for this.

## `[modem]` (required)

Serial connection and query mode of the cellular modem.

| Field | Default | Meaning |
|---|---|---|
| `type` | — | selects the `Modem` implementation via the factory in `modems/__init__.py`. So far only `"quectel"` is registered. |
| `port` | empty | Device path of the AT interface, e.g. `/dev/ttyUSB2`. Empty: searched on every open via `/dev/serial/by-id/usb-Quectel_*-if02-port0`. This path stays valid when the modem re-registers on USB and the number of `/dev/ttyUSBn` changes. Opening fails if there is no port or more than one matching port. |
| `baud_rate` | — | Baud rate |
| `timeout` | — | Read timeout in seconds |
| `mode` | `"serving_cell"` | `"serving_cell"` (`AT+QENG`) or `"sa_scan"` (`AT+QSCAN`, NR5G-SA only; band and mode must be set by hand beforehand via the AT console, see the comment in the `config.toml`) |
| `retries` | `3` | Retries of a failed AT query |
| `retry_delay_s` | `0.75` | Pause between the retries |
| `sim_pin_env_var` | `"MODEM_SIM_PIN"` | Name of the environment variable with the SIM PIN, which is read during unlocking. The PIN itself is never in a configuration file. |
| `sim_unlock_poll_attempts` | `10` | how often the SIM's lock status is queried after unlocking |
| `sim_unlock_poll_interval` | `1.0` | Pause between these queries in seconds |

## `[gnss_receiver]` (required)

Serial connection of the GNSS receiver.

| Field | Default | Meaning |
|---|---|---|
| `type` | — | selects the `GNSSReceiver` implementation via `gnss/__init__.py`. So far only `"nmea_serial"` is registered. |
| `port` | — | Device path, e.g. `/dev/serial0` |
| `baud_rate` | — | Baud rate |
| `timeout` | — | Read timeout in seconds |
| `retries` | `3` | Retries of a failed read |
| `retry_delay_s` | `0.75` | Pause between the retries |

## `[device]`

Identifies the unit and the mission type. Both are in every datapoint; the mission type does not change the behaviour of the unit.

| Field | Default | Meaning |
|---|---|---|
| `device_id` | hostname of the Pi | Identifier of the unit in every datapoint. Must match `[heartbeat] device_id`, see [Setting up a unit](unit-setup.md#device-specific-values). |
| `mission_type` | `"ground"` | `"ground"` or `"drone"`. Only a marker for the data. The earlier `[profiles.*]` tables per mission type no longer exist. If one is still in the `config.toml`, it is ignored with a warning. |

## `[collector]`

When a datapoint is recorded and when a run ends.

| Field | Default | Meaning |
|---|---|---|
| `position_threshold` | `15` | Minimum distance in metres (haversine) from the last measurement position before the next datapoint is recorded |
| `max_idle_time` | `1800` | Seconds without real movement after which the run ends. Only works in Auto Mode. `0` switches it off: the run then ends, as it always does in Manual Mode, only via `stop-measuring-now`, `shutdown-now`/`reboot-now` or power loss, and the log grows until then (only `[storage] low_free_space_warning_bytes` warns before a full memory card). |
| `max_wait_for_first_fix` | `300` | Seconds to wait for the first GPS fix in Auto Mode before the pass ends without a run. In Manual Mode the unit waits without a time limit after `start-measuring-now`. |
| `wait_log_interval` | `5` | how often (seconds) “still waiting for fix” is logged |
| `keep_alive_host` | `"8.8.8.8"` | Destination of the UDP packets that keep the cellular link open during measuring |
| `keep_alive_port` | `53` | Port of these packets |
| `keep_alive_interval_s` | `4.0` | Spacing between these packets |
| `gps_enabled` | `true` | `false`: measures without a real GPS fix (placeholder positions), for testing without GNSS hardware |
| `gps_disabled_poll_interval_s` | `5.0` | Query interval with `gps_enabled = false` |
| `capture_gate` | `"distance"` | Capture rule: `"distance"` (after `position_threshold`) or `"time"` (fixed spacing `capture_interval_s`). The end at standstill always follows the distance, so the rule never changes when a run ends. |
| `capture_interval_s` | `15.0` | Seconds between datapoints with `capture_gate = "time"`, otherwise without effect |
| `modem_reconnect_attempts` | `10` | If the connection to the modem is lost during measuring (port gone, I/O error), the datapoint is skipped and the modem is reopened up to this many times before the error ends the run. At least `1`. |
| `modem_reconnect_delay_s` | `3.0` | Pause before each reopening so that a modem that fell off USB can re-register (about 10 s in the field) |

## `[movement_gate]`

Waiting for confirmed movement before measuring begins. Only uses GNSS and rarely; it does not touch the modem and `quectel-CM`. Both are already running at this point for the heartbeat.

| Field | Default | Meaning |
|---|---|---|
| `enabled` | `true` | `false`: no waiting, measuring begins immediately (e.g. for drones that stand or hover on the ground). `quectel-CM` and heartbeat still start at boot. |
| `poll_interval_s` | `45.0` | Query interval of the GNSS while waiting |
| `movement_threshold` | `10.0` | Minimum distance in metres from the position of the first fix that counts as movement |
| `confirmations_required` | `2` | Number of consecutive queries with movement until a run counts as started |
| `home_latitude` / `home_longitude` | empty | optional home position (e.g. garage). Set both or neither; checked at startup. If set, in addition to movement the unit must have left the home position. |
| `home_departure_threshold` | `100.0` | Distance in metres from the home position from which it counts as left |

## `[quectel_cm]`

The connection manager `quectel-CM`, which the software itself starts at boot (via `sudo`), not `systemd`. The cellular link monitoring restarts it if the connection does not come back (see [`[link_watchdog]`](#link_watchdog)).

| Field | Default | Meaning |
|---|---|---|
| `binary` | placeholder | Path to the built `quectel-CM`. Device-specific, set in the `config.local.toml`. The placeholder is deliberately never a real path. |
| `args` | `()` | additional arguments, e.g. `["-s", "web.vodafone.de"]` for the APN |

## `[run_status]`

What the heartbeat reports about the quality of the run. A datapoint counts as “valid” if RSRP, RSRQ and SINR are all in the range that the radio standard allows for the respective radio technology, otherwise as “invalid” (missing, placeholder or nonsensical values). How good a valid signal is is only judged during evaluation, not on the unit.

| Field | Default | Meaning |
|---|---|---|
| `empty_captures_until_pipeline_broken` | `3` | Number of empty datapoints in a row while moving, from which the heartbeat reports the measurement chain as disturbed |

## `[backend]`

Common HTTPS destination and login for everything the unit sends to the backend (heartbeat and uploads). `url` must be `https`: the unit establishes every connection itself, and the backend's response is the way instructions reach the unit. This path must be trustworthy. `[heartbeat]` and `[uploader]` append their own path to this `url` instead of configuring a host of their own.

| Field | Default | Meaning |
|---|---|---|
| `url` | `""` | Base address of the backend. Device-specific, set in the `config.local.toml`. |
| `device_key` | `""` | API key of the unit. Device-specific and secret, set in the `config.local.toml`. |

## `[heartbeat]`

Regular report to the backend on how the run currently stands. The response can contain signed configuration changes and one-shot remote commands.

| Field | Default | Meaning |
|---|---|---|
| `enabled` | `true` | switches the heartbeat on |
| `path` | `"/api/heartbeat"` | Path appended to `[backend] url` |
| `interval_s` | `15.0` | Seconds between two heartbeats |
| `timeout_s` | `10.0` | HTTP timeout of a heartbeat |
| `device_id` | `""` | Identifier with which the unit registers with the backend, separate from `[device] device_id`. Device-specific, set in the `config.local.toml`. |
| `hmac_secret` | `""` | verifies that configuration changes and commands in the response really come from the backend. Empty: remote commands are switched off, a response with commands is discarded and logged. Device-specific and secret, set in the `config.local.toml`. |
| `success_log_interval_s` | `600.0` | Delivered heartbeats are logged at INFO: the first, the first after errors and otherwise one summary per this many seconds. |

## `[selftest]`

Destination in the backend for the results of `python -m measurement_software.selftest`. Login uses `[backend] device_key` and `[heartbeat] device_id`; there are no separate credentials.

| Field | Default | Meaning |
|---|---|---|
| `results_url` | `""` | Address for the results. Empty: the checks only run locally with output on the console. Device-specific (contains the real backend host), set in the `config.local.toml`. |

## `[gps_fix_test]`

Live test of the GPS fix search (`run-gps-fix-test-now` / `stop-gps-fix-test-now`) to find a good position for the antenna. Only executed while idle in Manual Mode (`MANUAL_MODE_IDLE`), otherwise answered with `not_applicable` (see `[system] mode`).

| Field | Default | Meaning |
|---|---|---|
| `status_url` | `""` | Address to which `num_satellites`, `has_fix` and `elapsed_s` are sent about every `report_interval_s`. Device-specific, set in the `config.local.toml`. |
| `report_interval_s` | `2.0` | Spacing of the status reports during the test |
| `timeout_s` | `300.0` | ends the test by itself if `stop-gps-fix-test-now` never arrives |

## `[storage]`

Safety net for the local upload backlog. No upper limit and no deleting, only a clear warning when storage space gets short, in case a connection gap lasts much longer than expected.

| Field | Default | Meaning |
|---|---|---|
| `low_free_space_warning_bytes` | `500_000_000` | free space on the file system of `[uploader] upload_dir` below which a warning is issued |

## `[display]`

Small SSD1306 OLED display over I2C for diagnostics in the field without a terminal. On by default: with `enabled = false` a null display runs and the software works unchanged without a screen. On a unit without a display, therefore set `enabled = false`.

| Field | Default | Meaning |
|---|---|---|
| `enabled` | `true` | switches the display on |
| `type` | `"ssd1306"` | selects the `Display` implementation via `displays/__init__.py`. So far only `"ssd1306"` is registered. |
| `i2c_port` | `1` | Number of the I2C bus |
| `i2c_address` | `0x3C` | I2C address of the display |
| `refresh_interval_s` | `2.0` | Refresh interval of the display |

## `[latency_test]`

Active latency measurements with `flent` against a test server while the vehicle is moving. On by default but without effect without `host`: the tests need a counterpart on the server (`netperf` for the load test, a host that answers ping for the baseline), which lies outside this repository. A unit that has not been set up should never generate test traffic on its own, so only set `host` once the counterpart is reachable. The counterpart is described in [Flent server](../../backend/dev/flent-server.md).

| Field | Default | Meaning |
|---|---|---|
| `enabled` | `true` | switches the latency tests on |
| `host` | `""` | Hostname of the test server. Empty: no tests. Device-specific, set in the `config.local.toml`. |
| `flent_binary` | `"flent"` | Name or path of `flent` |
| `baseline_test` | `"ping"` | `flent` test for the cheap baseline (latency of the unloaded connection) |
| `baseline_interval_s` | `60.0` | Spacing of the baseline measurements |
| `baseline_length_s` | `10` | Duration of a baseline measurement |
| `load_test` | `"rrul"` | `flent` test under load. Fully loads the connection for its whole duration and therefore runs much less often than the baseline. |
| `load_interval_s` | `900.0` | Spacing of the load tests |
| `load_length_s` | `60` | Duration of a load test |
| `poll_interval_s` | `30.0` | how often the tester checks whether one of the tests is due |
| `movement_window_s` | `30.0` | How recent the last movement (datapoints per `[collector] position_threshold`) must be for a due test to run. If the vehicle stands longer, the test waits for the next check. |
| `timeout_s` | `300.0` | Timeout of a single test |

## `[uploader]` (required)

Local storage and HTTPS upload of the saved measurement data. Uploads go by HTTPS POST to the scheme and host of `[backend] url` with the path from this section; there is no upload host of its own. A run tries to upload when measuring begins and after finalizing; at both points the connection is up anyway.

| Field | Default | Meaning |
|---|---|---|
| `upload_dir` | `"upload_queue"` (relative to the working directory) | local directory for measurement files that still have to be uploaded. Device-specific, set the absolute path in the `config.local.toml`. |
| `path` | `"/api/measurements"` | Endpoint for measurement files, one request per *file* (JSON array) |
| `latency_path` | `"/api/latency-results"` | Endpoint for latency results, one request per *result* (single JSON object). The two endpoints have incompatible formats. |
| `debug_upload` | `true` | binds the upload to the IP of `wwan0` (for testing over the cellular link itself) and logs verbosely |
| `timeout_s` | `10.0` | HTTP timeout per upload |

The earlier SCP fields `upload_user`, `upload_host`, `upload_port` and `remote_dir` no longer exist. If they are still in a `config.toml`, they are ignored with a warning.

## `[logging]`

| Field | Default | Meaning |
|---|---|---|
| `level` | `"INFO"` | Log level |
| `log_file` | placeholder | Path of the rotating log file |
| `max_bytes` | `5_000_000` | Size at which the log file rotates |
| `backup_count` | `3` | Number of rotated files kept |

## `[system]`

Raspberry Pi settings: network interfaces, device mode, crash behaviour.

| Field | Default | Meaning |
|---|---|---|
| `running_on_pi` | `true` | starts and monitors `quectel-CM` and shuts the Pi down at the end of a run. A local development checkout sets `false`. |
| `network_interfaces` | `("wlan0", "wwan0")` | Interfaces whose IPv4 addresses are logged at startup |
| `mode` | `"auto"` | `"auto"`: brings up the cellular link at boot, starts the heartbeat and begins measuring as soon as the movement gate confirms movement. `"manual"`: boots the same way but then does nothing until a remote command (`start-measuring-now`) arrives, and never ends a run because of standstill. The earlier value `"waiting"` is read as `"manual"` with a warning. Only takes effect at the next boot. Remote switching is done via `mode-manual-now`/`mode-auto-now`, which write `system_mode` into the `config_overrides.toml` instead of changing this field during operation. |
| `crash_same_error_limit` | `3` | An unhandled error reboots the unit. If the same error (exception type and triggering function) has occurred this many times in a row, it boots once into the recovery state, which only measures after `start-measuring-now`. A further error after that boots it into maintenance mode, in which only the cellular link runs, see [Architecture](architecture.md#crashes). At least `1`. |
| `crash_reboot_limit` | `5` | The same escalation also applies if there were this many reboots in a row because of unhandled errors of any kind. At least `1`. |

## `[link_watchdog]`

Restores a cellular link that does not come back. Only active with `[system] running_on_pi`, because `quectel-CM` is only started then.

| Field | Default | Meaning |
|---|---|---|
| `enabled` | `true` | switches the monitoring on |
| `interface` | `"wwan0"` | Interface whose IPv4 address means “connection is up” |
| `check_interval_s` | `30.0` | Seconds between two checks |
| `restart_after_s` | `180.0` | If the connection is gone this long, `quectel-CM` is restarted. As long as it stays gone, the wait before each further step doubles. |
| `max_restart_interval_s` | `1800.0` | Upper limit for this wait. The watchdog never gives up; the next disturbance starts again at `restart_after_s`. At least `restart_after_s`. |
| `radio_reset_after_restarts` | `2` | After this many unsuccessful restarts, the modem's radio module is reset instead (`AT+CFUN=0`/`1`). If the modem is currently unreachable or a reset is already running, `quectel-CM` is restarted again. |

## `[clock]`

Sets the system clock via NTP (SNTP) as soon as the cellular link is up. The Pi has no real-time clock, and `systemd-timesyncd` only tries before the connection exists. The clock is also set once per boot from the GNSS time.

| Field | Default | Meaning |
|---|---|---|
| `ntp_server` | `""` | IPv4 address or hostname of the NTP server. Empty: no NTP. Queried after every connection setup until it works once. Device-specific, set in the `config.local.toml`. |
| `ntp_timeout_s` | `3.0` | Timeout of a query. Must be positive. |

## Startup checks

`load_config()` aborts at startup with `ValueError`, before anything happens with the hardware, if:

- only one of `[movement_gate] home_latitude`/`home_longitude` is set
- `[system] mode` is neither `"auto"` nor `"manual"` (`"waiting"` is read as `"manual"` beforehand)
- `[collector] modem_reconnect_attempts` is less than 1 or `modem_reconnect_delay_s` is negative
- `[system] crash_same_error_limit` or `crash_reboot_limit` is less than 1
- `[link_watchdog] check_interval_s` or `restart_after_s` is not positive, `max_restart_interval_s` is less than `restart_after_s` or `radio_reset_after_restarts` is negative
- `[clock] ntp_timeout_s` is not positive

After such an abort, the unit only brings up the cellular link so that it stays reachable via SSH (see [Architecture](architecture.md#entry-point)).

After the `config_overrides.toml` is applied, the checks run again. There, however, a violation does not lead to an abort; the affected change is discarded (see [Remote configuration](#remote-configuration-config_overridestoml)).

Missing device-specific values are logged by the software as a warning without aborting: `[backend] url`/`device_key`, `[heartbeat] device_id`, `[quectel_cm] binary` and, with `[heartbeat] enabled`, `[heartbeat] hmac_secret`. Fields and tables that no longer exist (`[system] shutdown_gpio`, the SCP fields under `[uploader]`, `[profiles.*]`) are likewise only ignored with a warning, because an abort would make the unit unreachable before the cellular link is established. A real unit needs these; a local development checkout with `[system] running_on_pi = false` normally does not have them.

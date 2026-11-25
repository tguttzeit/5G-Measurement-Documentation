# Development

This section is for everyone who develops the measurement software of the unit further, adapts it to new hardware or sets up a new unit. How to operate the unit in the field is described under [Usage](../usage/index.md).

## Structure

The measurement software is a Python application that runs on a Raspberry Pi and starts as a `systemd` service at boot. The code lives in the repository [`tguttzeit/5G-Measurement-Software`](https://github.com/tguttzeit/5G-Measurement-Software).

| Part | Location in the code | Purpose |
|---|---|---|
| Entry point and flow | `main.py`, `core/run_phase.py`, `core/first_fix_wait.py`, `core/movement_gate.py` | loads the configuration, builds modem and GNSS receiver, takes a run through its states |
| Measurement loop | `core/collector.py`, `core/capture_gate.py` | records datapoints (cell values, position, time) |
| Hardware | `modems/`, `gnss/`, `displays/` | interchangeable implementations for modem, GNSS receiver and display |
| Saving and uploading | `core/run_log.py`, `core/uploader.py` | writes datapoints away in a power-loss-safe way and uploads them to the backend |
| Backend connection | `remote/heartbeat.py` | heartbeat, remote commands and remote configuration |
| Raspberry Pi | `core/system.py`, `core/link_watchdog.py`, `core/modem_access.py`, `core/ntp_clock.py` | `quectel-CM`, time (GNSS and NTP), shutdown, monitoring of the cellular link |
| Crash handling | `core/crash_policy.py`, `core/maintenance_mode.py` | reboot, recovery and maintenance mode on repeated errors |
| Self-test | `selftest.py`, `selftests/` | checks the hardware piece by piece from the command line |

How the parts work together is described under [Architecture](architecture.md).

## Pages

- [Architecture](architecture.md): flow of a run, crash handling, saving, uploading, remote commands, test patterns
- [Configuration reference](configuration.md): all `config.toml` fields and what can be changed remotely
- [Hardware integration](hardware-integration.md): connecting a new modem, GNSS receiver or display
- [Setting up a unit](unit-setup.md): setting up a new unit, device-specific values, autostart, known pitfalls
- [Local testing](local-testing.md): development environment, tests and lint, starting the application and self-test by hand, testing with the backend on the local network
- [Code](../../../reference/measurement_software/): reference of the modules, classes and functions, generated from the docstrings

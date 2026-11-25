# Local testing

This page describes the development environment of the measurement software, the automated tests, how to start the application and the self-test by hand on a unit and how to test the unit together with the backend. How a new unit is set up is described under [Setting up a unit](unit-setup.md).

## Development environment

Prerequisites: [`uv`](https://docs.astral.sh/uv/) and Python 3.12 or later. Install the dependencies in the root directory of the repository:

```bash
uv sync
```

This also installs the development tools (`pytest`, `pytest-cov`, `ruff`). A local checkout should set `[system] running_on_pi = false` in the `config.toml`; the software then does not start `quectel-CM` and does not shut anything down (see [Configuration reference](configuration.md#system)).

## Tests and lint

```bash
uv run pytest                                                        # all tests
uv run pytest --cov=measurement_software --cov-report=term-missing   # with test coverage
uv run ruff check .                                                  # lint
```

The tests need no hardware: modem, GNSS receiver, display, serial interfaces, HTTP and time are replaced by fakes. How this is built is described under [Test patterns](architecture.md#test-patterns).

## Starting the application by hand

A complete run needs a modem and a GNSS receiver and is therefore started on a unit. First stop the service so that two instances do not access the hardware at the same time:

```bash
sudo systemctl stop 5g-measurement.service
uv run python -m measurement_software.main
```

There is no entry point under `[project.scripts]`; the application is always started as a module. One invocation goes through exactly one run:

1. Save data of an interrupted earlier run.
2. Start `quectel-CM` and the heartbeat.
3. Wait for a GPS fix and confirmed movement (Auto Mode) or for a remote command and then the GPS fix (Manual Mode).
4. Measure until the run ends (standstill in Auto Mode or `stop-measuring-now`).
5. Finalize and upload.
6. With `[system] running_on_pi = true`, shut down the Pi.

The exact flow is described in [Architecture](architecture.md#flow-of-a-run).

## Self-test

To check the wiring of a unit over SSH without starting a whole run, there is the self-test. It reads the `config.toml` just like the application and needs no configuration of its own:

```bash
uv run python -m measurement_software.selftest                  # all checks
uv run python -m measurement_software.selftest modem gps        # only some
uv run python -m measurement_software.selftest --help           # overview
```

| Check | What it does |
|---|---|
| `modem` | opens the modem and queries the cell values once |
| `gps` | opens the GNSS receiver and waits for a fix |
| `collector` | checks whether cell values and fix fit together into a datapoint, without saving it |
| `uploader` | checks whether `wlan0` or `wwan0` has an IPv4 address |
| `heartbeat` | sends a real heartbeat to the backend |
| `keep_modem_alive` | briefly starts the UDP sender that keeps the connection open |
| `display` | shows a test message on the display |
| `latency_tester` | checks whether `flent` runs and a test server is configured, without starting a test |

No check uploads measurement data or shuts the device down. Whether the backend is reachable and the credentials are correct is checked by `heartbeat`, which goes to the same backend with the same key as the uploader.

If `[selftest] results_url` is set, the results of `modem`, `gps`, `collector`, `uploader` and `heartbeat` additionally end up in the backend's [Test visualization](../../backend/test-visualization.md). Which results look like errors the first time but are not is described under [Setting up a unit](unit-setup.md#checking-the-wiring-before-the-first-run).

## Testing together with the backend

The measurement software has no integration tests of its own. The interplay with the backend (heartbeat, uploads, remote commands, self-test results) is checked by running a real unit against a backend on the local network. The setup of the test backend, the test credentials, the `config.local.toml` for the unit, the certificate and the pitfalls on the unit (`debug_upload`, `running_on_pi`, `Promote overrides`) are described under [With a real unit on the local network](../../backend/dev/local-testing.md#with-a-real-unit-on-the-local-network).

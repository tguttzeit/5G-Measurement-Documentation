# Setting up a unit

This page collects what has to be done when first setting up a new unit over SSH without a screen and what you can get stuck on.

## Missing tools

A fresh Pi image does not come with `uv`. It can be installed without a reboot:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

Then first run `uv sync` in the repository.

## Device-specific values

Some fields of the checked-in `config.toml` are deliberately obvious placeholders (`"https://add.your.backend.here"`, `"/add/your/quectel-CM/path/here"`). A fresh checkout should never talk to a real backend by accident or start a program that does not exist. These values belong to the identity of the individual unit and go not into the `config.toml` but into the `config.local.toml` (see below).

| Field | Source | Note |
|---|---|---|
| `[backend] url` | Address of the backend | |
| `[backend] device_key`, `[heartbeat] hmac_secret`, `[heartbeat] device_id` | are created in the backend, see [Device registration](../../backend/dev/device-registration.md) | As long as they are missing, heartbeat and uploader reach the backend but get `401 Unauthorized`. This is expected and not a wiring error. |
| `[device] device_id` | same value as `[heartbeat] device_id` | see warning below |
| `[quectel_cm] binary` | Path after building, see [Building `quectel-CM`](#building-quectel-cm) | |
| `[uploader] upload_dir` | absolute path of the upload queue on this unit | The `config.toml` only contains the relative placeholder `"upload_queue"`. Without a value of its own, measurement data ends up under the checkout. |
| `[selftest] results_url`, `[gps_fix_test] status_url`, `[latency_test] host` | Addresses of backend and latency test server | Stay empty and thus without effect until set. `[heartbeat] enabled` and `[latency_test] enabled`, by contrast, are ordinary default values and stay in the `config.toml`. |
| `[clock] ntp_server` | reachable NTP server | Optional. Sets the clock as soon as the cellular link is up, even without a GPS fix. Empty: the clock is only set from the GNSS time. |

!!! warning "`[device] device_id` must equal `[heartbeat] device_id`"

    The two fields are separate because `[heartbeat] device_id` registers the unit with the backend, while `[device] device_id` is written into every datapoint. If `[device] device_id` stays empty, the software takes the hostname of the Pi. The backend then rejects the upload with `403: Datapoint device_id <hostname> does not match authenticated device <heartbeat device_id>` because the data appears to come from a different device than the one that is logged in.

### `config.local.toml`

Writing device-specific values by hand into the `config.toml` leaves a permanently modified file that cannot be committed and blocks new defaults on `git pull`. Instead, create a `config.local.toml` next to the `config.toml`. It is listed in `.gitignore` and is layered over the `config.toml` at startup:

```toml
[backend]
url = "https://backend.example.org"
device_key = "<API key of the unit>"

[heartbeat]
device_id = "<device ID>"
hmac_secret = "<signing key>"

[device]
# Must match [heartbeat] device_id
device_id = "<device ID>"

[quectel_cm]
binary = "<install directory>/vendor/quectel-CM/quectel-CM"

[uploader]
# Absolute path of the upload queue on this unit
upload_dir = "/path/to/upload_queue"

[selftest]
results_url = "https://backend.example.org/api/testing/results"

[gps_fix_test]
# The path contains your own device ID, insert it by hand
status_url = "https://backend.example.org/api/devices/<device ID>/gps-fix-test/status"

[latency_test]
host = "latencytest.example.org"

[clock]
ntp_server = "ntp.example.org"
```

Only these fields and sections are read from the `config.local.toml`; everything else is logged and ignored. The file contains credentials in plain text, so make it readable only for the user the software runs as:

```bash
chmod 600 config.local.toml
```

On a real unit (`[system] running_on_pi = true`), the software warns at startup for each of these fields that is still missing or still on the placeholder. It is a warning and not an abort, because the fields fail gracefully in operation anyway (failed uploads, `401`, discarded remote commands).

!!! info "Older units with `--skip-worktree`"

    The `config.local.toml` replaces the earlier way `git update-index --skip-worktree config.toml`. That hid the changes to the `config.toml` but also no longer picked up new defaults. On a unit set up like this, run `git update-index --no-skip-worktree config.toml` once, transfer your own values into a new `config.local.toml` and reset the `config.toml` to the state of the repository.

## Building `quectel-CM`

`vendor/quectel-CM` is included as source code, not as a finished program:

```bash
cd vendor/quectel-CM && make release
```

`gcc`, `make` and `pkg-config`, which are present on a standard Pi OS image, are enough for this. The simple `Makefile` does not need `autoconf` and `automake`. Point `[quectel_cm] binary` to the resulting `vendor/quectel-CM/quectel-CM`.

## APN in MBIM mode

If the `quectel-CM` log reports `Modem works in MBIM mode` or `must specify APN with '-s'`, it never brings `wwan0` up without `-s <APN>`. Do not guess the APN or look it up in lists; the SIM's network operator has already told the modem. Query it over the AT interface:

```text
AT+COPS?       # current network operator, e.g. +COPS: 1,0,"vodafone.de",13
AT+CGDCONT?    # PDP contexts stored in the modem, the APN of context 1 is the right one
```

Then pass the APN via `[quectel_cm] args`, e.g. `args = ["-s", "web.vodafone.de"]`.

## Setting up autostart

`systemd/5g-measurement.service` starts the application at boot. The unit does not start `quectel-CM` itself and does not depend on it: the application takes care of that right at startup so that the unit is reachable over cellular during the whole run and not only from the start of measuring. On SIGTERM it also terminates `quectel-CM` again.

The unit sets `KillMode=mixed`: on `systemctl stop` or on system shutdown, only the application gets SIGTERM. This way its last heartbeat and the upload still go out over cellular, after which it terminates `quectel-CM` itself.

The unit file contains the placeholder `@INSTALL_DIR@`. Run this in the checkout and it is replaced by the current directory:

```bash
sed "s|@INSTALL_DIR@|$PWD|g" systemd/5g-measurement.service \
  | sudo tee /etc/systemd/system/5g-measurement.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable 5g-measurement.service
```

Run these commands again if `systemd/5g-measurement.service` has changed in the software repository. Until then, systemd keeps working with the previously installed unit.

## Preparing the latency tests

For the optional latency tests (`[latency_test]`), install `flent` and the tools it calls on the unit:

```bash
sudo apt install flent netperf python3-numpy
```

The tests also need a counterpart on the test server, see [Flent server](../../backend/dev/flent-server.md). Only set `[latency_test] host` once the unit reaches this counterpart. Without `host` no tests run, so a unit that has not been set up never generates test traffic.

## Connecting the OLED display

The SSD1306 display is on the I2C bus. SDA and SCL are fixed to GPIO2 and GPIO3, the hardware I2C pins of the Pi, and are not configurable. On the display of the existing unit, the four pins from left to right are as follows:

| Display pin | Cable colour | Pi, physical pin | Pi, GPIO |
|---|---|---|---|
| GND | white | 6 | Ground |
| VCC | purple | 1 | 3.3 V |
| SCL | blue | 5 | GPIO3 (SCL) |
| SDA | green | 3 | GPIO2 (SDA) |

This matches `[display] i2c_port = 1` and `i2c_address = 0x3C` in the `config.toml`.

!!! warning "Check the pin assignment on the display"

    Pin order and cable colours only apply to the cable set of this unit and are not a standard. On another unit, check the labelling on the display instead of adopting the table.

## Checking the wiring before the first run

The self-test checks each subsystem individually and reports passed, failed or skipped. This is considerably faster than letting `main.py` run completely again and again for a single faulty item:

```bash
uv run python -m measurement_software.selftest                  # all checks
uv run python -m measurement_software.selftest modem uploader   # only some
```

If `[selftest] results_url` is set, the results additionally end up in the backend's [Test visualization](../../backend/test-visualization.md).

Some results look like errors the first time but are not:

- **`uploader` fails although the internet is there:** The check does not upload anything; it only checks whether an interface is ready. Like the real uploader, it only counts `wlan0` and `wwan0`. A connection over `eth0`, such as the SSH session, is not enough. The message `No network interface (wlan0/wwan0) has an IPv4 address` is then correct.
- **`gps` or `collector` fails:** No GNSS receiver is connected to `/dev/serial0`. The check does what it should.
- **`modem` passes with zero cell values:** The radio module is not yet registered on any network, e.g. because `quectel-CM` is not running and there is no data connection. Before troubleshooting in the software, check the connection, via the AT interface with `AT+QENG="servingcell"` or with `ip addr show wwan0`.

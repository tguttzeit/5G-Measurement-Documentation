# Hardware integration

The measurement software talks to three interchangeable hardware roles: modem, GNSS receiver and status display. Each role sits behind an abstract interface with a small factory that builds the matching implementation from a `type` value in the configuration. For a different modem, GNSS receiver or display, you write a new class and register it; nothing else changes.

## The pattern

Each role consists of three parts:

1. **An abstract base class** with the contract, e.g. `modems/modem.py::Modem`.
2. **One or more implementations**, e.g. `modems/quectel.py::Quectel`.
3. **A factory dictionary** with `type` as the key, e.g. `modems/__init__.py::_MODEM_FACTORIES`. `create_modem(config)` builds the configured implementation from it; an unknown `type` raises `ValueError`.

`main.py` only calls `create_modem(config.modem)`, `create_gnss_receiver(config.gnss_receiver)` and `create_display(config.display)` and never imports an implementation directly. A new implementation is thus a new file plus an entry in the factory dictionary.

## New modem

1. If the modem needs more than the existing fields of `ModemConfig` (`port`, `baud_rate`, `timeout`, `mode`, retries), create a dataclass for it. Most serial modems need nothing additional.
2. Implement `Modem` (`modems/modem.py`) in a new file `modems/<name>.py`:
    - `open()` / `close()`: manage the serial connection.
    - `unlock_sim()`: enter the SIM PIN if necessary. On an error, raise the matching subclass of `SimUnlockError` (`SimPinNotConfiguredError`, `SimPinRejectedError`, `SimPukRequiredError`, `SimStatusUnknownError`), not a general exception, so that callers can react appropriately.
    - `query_cell_info() -> list[CellSample]`: return one `CellSample` per active radio technology (RAT). Fill all fields the modem provides and leave the rest as `None`. Anything that cannot be mapped to a common field goes into the open dictionary `vendor_specific_extras`.
    - `reset_radio()`: switch the radio module off and on again so that the modem re-registers on the network. The cellular link monitoring calls this when restarts of `quectel-CM` do not help.
    - `power_down()`: send the modem's power-off command.
3. Register the class in `_MODEM_FACTORIES` in `modems/__init__.py` under a new `type`.
4. In the `config.toml`, set `[modem] type = "<name>"`.
5. Write tests under `tests/modems/test_<name>.py` following the example of `tests/modems/test_quectel.py`: replace `serial.Serial` at the point of use (`measurement_software.modems.<name>.serial.Serial`) with a fake that records what was written and returns scripted responses. A test never touches a real serial port.

!!! danger "Never retry the PIN automatically"

    Never automatically enter a rejected PIN again and never enter a PUK. Either can permanently lock the SIM card. Details are in the docstrings of the exceptions.

## New GNSS receiver

1. Implement `GNSSReceiver` (`gnss/gnss_receiver.py`) in a new file `gnss/<name>.py`:
    - `open()` / `close()`: manage the connection.
    - `read_fix() -> GNSSFix | None`: the latest fix (`Position` and number of satellites used) or `None` if there is none at the moment. Set `GNSSFix.placeholder = True` only for a deliberately fake fix (e.g. in a test run without GPS), never for real data.
    - `read_datetime() -> datetime | None`: the latest UTC time from GNSS, with which the system clock is set.
    - `read_satellites_in_view()` is optional (default: `None`). Only override it if the receiver supplies the number of tracked satellites even without a fix. The GPS fix test shows this number as progress before a fix exists.
    - `read_gnss_diagnostic()` is also optional (default: `None`): raw diagnostic text from the receiver (e.g. NMEA `$GxTXT` with an antenna fault). Before display on the screen and in the backend, it is translated by `updated_gnss_diagnostic()` into a short, fixed message.
2. Register the class in `_GNSS_FACTORIES` in `gnss/__init__.py` under a new `type`.
3. In the `config.toml`, set `[gnss_receiver] type = "<name>"`.
4. Write tests under `tests/gnss/test_<name>.py` following the example of `tests/gnss/test_nmea_serial.py` (replace `serial.Serial` as above).

## New display

1. Implement `Display` (`displays/display.py`) in a new file `displays/<name>.py`. The model for the interface is `displays/ssd1306_display.py`; `displays/null_display.py` shows the empty basic form that every unit without a display falls back to.
2. Register the class in `_DISPLAY_FACTORIES` in `displays/__init__.py` under a new `type`. With `[display] enabled = false`, `create_display()` always returns `NullDisplay()` regardless of `type`, so a new implementation only has to cover the enabled case.
3. In the `config.toml`, set `[display] type = "<name>"` and add new fields the implementation needs to `DisplayConfig` (`core/config.py`), e.g. a different bus or address scheme than `i2c_port`/`i2c_address`.
4. Write tests under `tests/displays/test_<name>.py` following the example of `tests/displays/test_ssd1306_display.py`.

## General notes

- Fields that only concern one hardware implementation belong in the configuration dataclass of its role (`ModemConfig`, `GnssConfig`, `DisplayConfig`) in `core/config.py` and in the [Configuration reference](configuration.md).
- Device-specific values (real hostname, credentials, hardware address that do not belong in the checked-in `config.toml`) go into `config.local.toml`. Which fields are allowed there is in `core/config_sources.py::ALLOWED_LOCAL_FIELDS`, see also [Setting up a unit](unit-setup.md#device-specific-values).
- How the parts fit into the flow of a run and how the tests replace hardware is described under [Architecture](architecture.md) and [Test patterns](architecture.md#test-patterns).

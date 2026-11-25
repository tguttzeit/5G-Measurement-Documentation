# Configuration

The default settings of the unit are designed for measurement drives by car. Usually nothing needs to be changed before a deployment. For measurement flights and for special requirements, many settings can be adjusted in the backend under `Remote Configuration` without having to touch the unit.

## Where settings live

The unit assembles its configuration from several sources. Later sources override earlier ones:

1. **Base configuration** (`config.toml`): the default values of the software.
2. **Device-specific values** (`config.local.toml`): identity and credentials of the individual unit, set by hand once during setup.
3. **Remote configuration** (`config_overrides.toml`): changes from the backend, called `Config Overrides` here.

Not everything can be changed remotely. Device identity, credentials and addresses are permanently excluded from remote configuration. This also applies to the operating mode, which is switched via [remote commands](remote-commands.md#switching-the-mode).

!!! info "Changes only take effect after the next start"

    The unit never applies overrides during a running pass, only at the **next start**. If you change something before a deployment, reboot the unit afterwards, e.g. with the remote command `Reboot`.

## Checking before a deployment

The following settings are the most relevant for deployments. All others can usually stay at their defaults.

| If … | then check |
|---|---|
| the datapoint density is to be adjusted (e.g. for measurement flights) | [Capture interval and grid density](#capture-interval-and-grid-density) |
| standstill (traffic light, traffic jam, breaks) in Auto Mode is not to end the run | `Idle threshold` |
| the unit starts in a garage or on a site with poor GPS reception | `Max wait for first GPS fix` |
| the unit is operated without a display | `Display enabled` |

### Capture interval and grid density

How dense the datapoints are depends on the `Capture gate`:

- With `distance` (default), a measurement is taken after a distance travelled. The distance is set by the `Position threshold`, default 15 m.
- With `time`, a measurement is taken at a fixed time interval, independent of movement. The interval is the `Capture interval`, default 15 s.

For measurement flights, the grid density should be agreed with the remote pilot and the setting matched to it. Two examples:

- If the drone flies a grid with a fixed track spacing and a known speed, `time` with a suitable `Capture interval` is easy to plan.
- If measuring is to be done by distance, the `Position threshold` must match the planned spacing of the datapoints. Very small values are within the range of GPS inaccuracy and then count noise as movement.

Smaller spacings give denser coverage but produce more data and more queries to the modem.

#### Planning the flight

For measurement flights there is a calculator that determines the suitable `Capture interval` or `Position threshold` from flight speed, grid and area, see [Planning the grid](measurement-flight.md#planning-the-grid).

## Remote Configuration in the backend

The `Remote Configuration` page is only accessible to users with superuser rights. At the top it contains the `Command Status` with the `One-Shot Commands` (see [Remote commands](remote-commands.md)), below that the `Config Overrides` and at the bottom a preview with confirmation.

This is how you change settings:

1. Select the device.
2. For the desired settings, enter the value under `New value`. The `Current` column shows what the device is currently using according to its last heartbeat. Fields you do not touch stay unchanged.
3. Under `Preview & Confirmation`, check the changes and submit them with `Send & Confirm`.

The input is checked immediately: every setting has an allowed range (see the tables below). Nothing outside it can be sent.

Settings you need often can be marked as `Favorites` with the star.

!!! warning "Settings under “Advanced - hardware”"

    Wrong values in this group can make the unit unusable so that it can only be repaired on site. The backend therefore additionally asks “Do you know what you are doing?” before sending. Only change these settings if explicitly necessary.

### How changes reach the unit

Changes are queued in the backend and transferred to the unit with the next heartbeat, just like remote commands. The unit checks each setting individually and only accepts valid values; it discards the others. If the unit was set up without a signing key, it discards everything, see [Remote commands](remote-commands.md).

Queued changes stay in the backend until they are replaced or removed. To change a setting again, simply send a new value. With `Remove queued` under `Command Status`, changes and commands that have not yet been delivered can be discarded.

Only the home position can be reset to “not set”. All other settings always get a concrete value.

### Making changes permanent

Overrides are stored on the unit in a separate file and can therefore be undone. Once a value has proven itself, the command `Promote overrides` writes it permanently into the base configuration, see [Overrides](remote-commands.md#overrides).

## Settings at a glance

The “Default” column gives the value of the shipped base configuration. The key names in backticks are the names under which the setting appears on the unit and in logs.

### Measurement cycle

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Capture gate` (`collector_capture_gate`) | `distance` | `distance`, `time` | When to measure: after a distance or at a fixed time interval. The detection of standstill and session end always stays distance-based. |
| `Position threshold` (`collector_position_threshold`) | 15 m | 0.1 to 1000 m | Distance since the last measurement after which a new one is taken with `distance`. |
| `Capture interval` (`collector_capture_interval_s`) | 15 s | 1 to 86400 s | Time between two measurements with `time`. |
| `Idle threshold` (`idle_threshold_s`) | 1800 s | 0 to 86400 s | Time without detected movement after which the run ends. The data is then finalized and uploaded. Values that are too small end runs at traffic lights or in traffic jams. `0` switches off the idle end. Only works in Auto Mode; in Manual Mode a run never ends by itself. |
| `Max wait for first GPS fix` (`collector_max_wait_for_first_fix`) | 300 s | 1 to 3600 s | How long the unit waits for the first GPS fix in Auto Mode. After that the pass ends without measurement data. In Manual Mode it waits without a time limit after `Start measuring`. |
| `Wait log interval` (`collector_wait_log_interval`) | 5 s | 1 to 3600 s | Spacing of the log messages while waiting for the GPS fix. Only affects the size of the log. |
| `GPS enabled` (`collector_gps_enabled`) | `true` | `true`, `false` | With `false` the unit runs without GPS (e.g. with a defective receiver). The measurements then have no position reference. |
| `Poll interval without GPS` (`collector_gps_disabled_poll_interval_s`) | 5 s | 1 to 86400 s | Time between measurements while GPS is disabled. Only has an effect with `GPS enabled = false`. |

### Movement detection before start

In Auto Mode, after booting the unit waits for confirmed movement before it starts measuring. This check only uses the GNSS receiver.

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Poll interval` (`movement_gate_poll_interval_s`) | 45 s | 1 to 86400 s | Spacing of the position checks. Longer spacings save power but delay the start. |
| `Movement threshold` (`movement_gate_movement_threshold`) | 10 m | 0.1 to 1000 m | Distance from the position at the first GPS fix from which a check counts as movement. Must be above the GPS inaccuracy at standstill. |
| `Confirmations required` (`movement_gate_confirmations_required`) | 2 | 1 to 10 | This many checks in a row must show movement. Together with the poll interval this gives the minimum time until the start. |
| `Home latitude` / `Home longitude` (`movement_gate_home_latitude`, `movement_gate_home_longitude`) | not set | −90 to 90 / −180 to 180 | Known location, e.g. the garage. If both are set, a run only starts once the unit has left it. Always set or remove both values together. |
| `Home departure distance` (`movement_gate_home_departure_threshold`) | 100 m | 1 to 10000 m | Distance from which the unit counts as departed. |

### Latency tests

Active latency measurements with `flent`. They need a test server that is entered in the device-specific configuration. Without it the tests have no effect.

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Latency test enabled` (`latency_test_enabled`) | `true` | `true`, `false` | Switches the latency measurements on or off. The load test saturates the connection and consumes data volume and battery. |
| `Baseline interval` (`latency_test_baseline_interval_s`) | 60 s | 1 to 86400 s | Spacing of the ping tests on the unloaded connection. |
| `Load interval` (`latency_test_load_interval_s`) | 900 s | 1 to 86400 s | Spacing of the tests under load. Short spacings consume a lot of data volume and battery. |
| `Poll interval` (`latency_test_poll_interval_s`) | 30 s | 1 to 86400 s | How often it is checked whether a test is due. |

### Backend and operation

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Heartbeat interval` (`heartbeat_interval_s`) | 15 s | 1 to 86400 s | Spacing of the status messages to the backend. Remote commands and changes also arrive this way. Short spacings react faster but cost data volume. |
| `Mission type` (`device_mission_type`) | `ground` | `ground`, `drone` | Written into every datapoint. The backend can use it to separate measurements by deployment type. The mission type does not change the behaviour of the unit: whether it waits for movement and ends at standstill only depends on the [operating mode](measurement-runs.md#operating-modes). |
| `Display enabled` (`display_enabled`) | `true` | `true`, `false` | Switches the OLED display on or off. Set to `false` if no display is connected. |
| `Display refresh interval` (`display_refresh_interval_s`) | 2 s | 0.5 to 3600 s | Spacing at which the display is redrawn. |
| `Day-end threshold` (`day_end_threshold_s`) | – | 0 to 86400 s | Currently has no function on the device. The backend marks the setting accordingly. |

### Pipeline monitoring

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Empty captures until pipeline broken` (`run_status_empty_captures_until_pipeline_broken`) | 3 | 1 to 100 | This many empty measurements in a row while moving until the backend reports the measurement chain as broken. Small values report faults quickly, but also during short dead zones. |

### Advanced – hardware

!!! danger "Only change in exceptional cases"

    These settings affect the hardware of the unit. Wrong values can make it unusable until someone is on site.

| Setting | Default | Range | Effect |
|---|---|---|---|
| `Modem mode` (`modem_mode`) | `serving_cell` | `serving_cell`, `sa_scan` | Query mode of the modem: data of the current cell or scan for 5G SA cells only. For `sa_scan` the modem must be configured by hand beforehand, otherwise it delivers no data. |
| `SIM unlock attempts` (`modem_sim_unlock_poll_attempts`) | 10 | 1 to 100 | How often it is checked after the PIN entry whether the SIM is unlocked. |
| `SIM unlock interval` (`modem_sim_unlock_poll_interval`) | 1 s | 0.1 to 60 s | Spacing between these checks. With the number of attempts this gives the longest wait for the SIM. |
| `GNSS receiver retries` (`gnss_receiver_retries`) | 3 | 0 to 20 | Retries for failed read accesses to the GNSS receiver. |
| `GNSS retry delay` (`gnss_receiver_retry_delay_s`) | 0.75 s | 0 to 60 s | Pause between these retries. |
| `Running on Raspberry Pi` (`system_running_on_pi`) | `true` | `true`, `false` | With `false` the unit does not start the cellular link itself, does not monitor it and does not shut down at the end of a run. Always `true` on a real unit. |

## Only settable on the unit

The following cannot be changed via remote configuration, only directly on the device in `config.toml` or `config.local.toml`:

- Backend address, device ID, API key and signing key (`hmac_secret`), which are created in the backend
- Addresses for the self-test, the GPS fix test and the latency test server
- Path to `quectel-CM` and its arguments (e.g. APN)
- Directory for measurement data that has not yet been uploaded
- Serial interfaces of the modem and GNSS receiver as well as the log settings
- Crash behaviour and monitoring of the cellular link

!!! warning "`device_id` must be identical everywhere"

    The `device_id` in the unit's configuration must match the device ID created in the backend. Otherwise the backend rejects uploaded measurement data with an error.

The complete description of all fields is in the [Configuration reference](../dev/configuration.md).

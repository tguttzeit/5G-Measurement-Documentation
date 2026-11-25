# Usage

This guide walks step by step through a deployment of the unit: preparing, mounting, measuring and checking the data in the backend. This page explains what applies to every deployment. Continue with [Preparing the unit](preparation.md); at the end of that page the path splits into measurement drive (vehicle) and measurement flight (drone). Both end on the page [After use](after-use.md).

!!! info "Read completely before the first deployment"

    Anyone using the unit for the first time should read this page and the preparation in full and open the collapsible sections below. If you already know the unit, you can jump straight to [Preparing the unit](preparation.md).

!!! danger "The unit is not waterproof"

    Deployment is not possible in rain, fog or similar conditions.

## What the unit does

While on the move, the unit measures the quality of the mobile network (5G and LTE) together with the position and, optionally, the latency. The data is sent to the backend. After switch-on it works without any operation on the device:

1. It brings up the cellular link and reports to the backend, so it is visible there before measuring starts.
2. It waits for a GPS fix.
3. It starts measuring: in Auto Mode by itself as soon as it moves, in Manual Mode only on the remote command `Start measuring`.
4. It measures and saves continuously.
5. It stops measuring, uploads the data and shuts down.

Which values are measured and what they tell is described in [What is measured](measured-values.md).

??? info "What you need"

    - Measurement unit with antenna
    - Power bank: `Anker Prime 20000mAh` for the vehicle, `INIU Powerbank` for the drone
    - One USB-A to USB-A cable (power for the modem) and one USB-C to USB-C cable (power for the Raspberry Pi)
    - Vehicle: magnetic antenna mount
    - Drone (DJI Matrice 300 RTK): adapter plate or double mount, M2 and M3 screws, reusable cable ties, suitable tools (hex key or screwdriver for M2 and M3 screws)
    - An account in the backend, with superuser rights for remote commands and configuration (see [Roles](../../backend/index.md#roles))
    - Optional: smartphone with the [ntfy](https://ntfy.sh) app for push notifications
    - Optional: LAN cable to connect the unit to the backend without cellular

??? info "Terms"

    Backend
    :   The web interface for the unit. There you see whether a unit is online, control it remotely and find the measurement data. See [Backend](../../backend/index.md).

    Mission Status
    :   Page in the backend with the current state of every unit and the remote commands.

    Heartbeat
    :   Regular status message from the unit to the backend. Remote commands and configuration changes reach the unit with its next heartbeat, so not immediately.

    GPS fix
    :   The unit knows its position from satellite signals. Without a fix nothing is measured. For this the antenna needs a clear view of the sky.

    Remote command
    :   Command from the backend to the unit, e.g. `Start measuring` or `Shut down`. See [Remote commands](remote-commands.md).

    Remote Configuration
    :   Changing the unit's settings in the backend without having to touch the device. Changes only take effect after the next boot. See [Configuration](configuration.md).

    Run
    :   The data of one measurement from start to end. Found in the backend under `Measurement Runs`.

??? info "Operating modes"

    The unit boots into one of two modes:

    - **Auto Mode** (default, for measurement drives): Measuring starts by itself as soon as the unit moves and ends by itself after a longer standstill.
    - **Manual Mode** (for measurement flights or troubleshooting): The unit connects but only measures after the remote command `Start measuring`, and only until `Stop measuring`.

    The mode is switched by remote command and only takes effect after the next boot. After `Stop measuring` in Auto Mode, the unit boots once into Manual Mode and then returns to Auto Mode. Details under [How the unit measures](measurement-runs.md#operating-modes).

??? info "Status display"

    The display of the unit shows the state, the GPS reception and the number of datapoints. The same states are shown in the backend under `Mission Status`. What the displays mean is described under [Status display](measurement-runs.md#status-display). The information shown on the display can also be read from the Mission Status page, as long as no error affects the internet connection.

??? info "Help with problems"

    What a display means and what you can do on site is described under [Troubleshooting](../troubleshooting/failure-modes.md).

## For reference

These pages are not part of the procedure but explain the background:

- [How the unit measures](measurement-runs.md): operating modes, phases of a run, status display, uploading the data
- [What is measured](measured-values.md): signal values, position, latency and throughput
- [Remote commands](remote-commands.md): all commands from the backend
- [Configuration](configuration.md): all settings and how changes reach the unit

!!! tip "Next"

    Continue with [Preparing the unit](preparation.md).

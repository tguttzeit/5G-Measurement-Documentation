# Remote commands

Remote commands let you control the unit from the backend without being at the device: start and stop measuring, upload data, shut down or reboot the device and switch the mode. How the modes work is described under [How the unit measures](measurement-runs.md#operating-modes).

A command is queued in the backend and arrives with the device's next heartbeat, so not immediately. The device only executes commands that the backend has signed.

!!! warning "Device does not react to any command"

    If no key for the signature check is set up on the device, it discards all commands and configuration changes without this being visible in the backend. If a unit never reacts to commands although it sends heartbeats, this is usually the reason.

## Where to find them

- In the backend under `Mission Status` in the `Remote Commands` section: `Start measuring`, `Stop measuring`, `Force upload`, `Reboot`, `Shut down` and the mode switch (`Auto mode`, `Manual mode`). Buttons that cannot be applied in the current state are greyed out.
- Under `Remote Configuration` in the `One-Shot Commands` section: all commands of the overview except the GPS fix tests. These can be found under `Testing Visualization`.

## Overview

| Command | Effect | When possible |
|---|---|---|
| `Start measuring` | Leaves the waiting loop, waits for a GPS fix and then starts measuring | only in `Idle (manual)` or `Idle (recovery)` |
| `Stop measuring` | Ends the running measurement run. In Auto Mode the unit then boots once into Manual Mode | during `Measuring`; in Manual Mode also while waiting for the GPS fix after `Start measuring` |
| `Force upload` | Uploads all pending measurement files | any time, otherwise the device reports that there is nothing to upload |
| `Shut down` | Shuts the device down. It stays connected to the power supply and only starts again when you disconnect it and reconnect it | any time |
| `Reboot` | Reboots the device | any time |
| `Auto mode` / `Manual mode` | Permanently switches the boot mode; takes effect at the next start | any time |
| `Run self-test` | Checks whether the hardware is reachable without leaving idle | only in `Idle (manual)` |
| `Start GPS fix test` / `Stop GPS fix test` | Live diagnostics for finding a good antenna position | only in `Idle (manual)` |
| `Reset SIM` | Disconnects the control connection to the modem, rebuilds it and unlocks the SIM again. Useful if the modem no longer delivers measured values. The mobile data connection itself is not re-established. If a measurement is running, the command takes effect at the next query | any time |
| `Promote overrides` | Permanently writes the values set via Remote Configuration into the device's configuration file, effective from the next start | any time |

## Stop measuring

`Stop measuring` ends the run in an orderly way, exactly like the idle end in a measurement drive: the device finalizes the measurement data, uploads it and then shuts down the operating system.

If the command arrives in Manual Mode while the unit is still waiting for the GPS fix after `Start measuring`, it cancels the start. The unit then returns to idle (`Idle (manual)`) and does not shut down.

!!! info "The unit stays connected to power"

    Shut down does not mean without power: the unit stays connected to the power bank and draws a small standby current. After the deployment, therefore disconnect the power supply as soon as the unit has shut down, see [After use](after-use.md). To switch it on again, reconnect the power supply. This applies equally to the idle end of a ground drive and to `Shut down`.

!!! warning "Afterwards the unit boots once into Manual Mode"

    If the measurement was stopped in Auto Mode, the unit boots into Manual Mode at the **next** start and only measures after `Start measuring`. This prevents a measurement from starting again right away if the unit is still moved after the stop. From the start after that, Auto Mode applies again. The configured mode itself does not change. If the unit was in Manual Mode anyway, it stays there.

The command only works during a running measurement or, in Manual Mode, while waiting for the GPS fix. Otherwise the device reports `Not applicable`.

## Switching the mode

The mode switch only takes effect at the **next start** of the unit. When switching in the interface, you can tick `Reboot afterwards`: the backend then queues a `Reboot` after the mode switch so that the new mode applies immediately.

## Overrides

Values changed via Remote Configuration (`Config Overrides`) are stored on the device in a separate file, apart from the actual configuration. This makes it possible to undo all changes by removing this file. `Promote overrides` instead writes the values permanently into the device's configuration file. After that they count as the base setting and also survive removing the override file.

## Shutting down

A switched-off device cannot confirm the shutdown. The backend therefore counts the command as successful if no heartbeat arrives for some time after the acknowledgement. Until then the command shows `Sent, waiting for device` or `Still online`. When the unit checks in after the next switch-on, it also confirms the command retroactively as successful.

## Status of a command

In the backend, the `Command status` shows how far a command has progressed:

| Status | Meaning |
|---|---|
| `Waiting for delivery` | The command is in the backend and waits for the next heartbeat |
| `Sent, waiting for device` | The command is on its way |
| `Received` | The device has received it |
| `Success` | The device has executed it |
| `Failed` | Execution failed |
| `Not applicable` | The device was not in a suitable state, e.g. `Stop measuring` without a running measurement |
| `Expired` | The command was not delivered in time |

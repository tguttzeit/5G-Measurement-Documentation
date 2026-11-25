# Measurement drive

Measuring from a vehicle. The unit runs in Auto Mode: it starts measuring by itself as soon as the vehicle moves and ends the measurement by itself when it has been standing for a while.

## What you need

- The prepared unit (see [Preparing the unit](preparation.md)), still connected there and opened in the backend under `Remote Configuration`
- `Anker Prime 20000mAh` power bank, charged, with 4x M2x?? screws [CHECK! length]
- Antenna with magnetic mount
- USB-A to USB-A and USB-C to USB-C cables

## Procedure

### Section I – What to look for in the configuration

The default settings are designed for measurement drives. Mainly check whether something is still switched over from an earlier measurement flight.

1. In `Remote Configuration`, check the following settings (`Current` column):

    | Setting | For the measurement drive | Why |
    |---|---|---|
    | `Mission type` | `ground` | Marks the data as a ground measurement. If it is still `drone`, the data is filed as a drone measurement in the backend. |
    | `Capture gate` and `Position threshold` | `distance`, 15 m | One datapoint every 15 m driven. For denser or looser coverage, change the `Position threshold`, see [Capture interval and grid density](configuration.md#capture-interval-and-grid-density). |
    | `Idle threshold` | 1800 s | How long the vehicle may stand before the measurement ends. If longer stops are planned (breaks, traffic jams), increase the value. |

2. Submit changed values with `Send & Confirm`.
3. In `Mission Status`, check the `Mode` tile. If it shows `Manual Mode` (e.g. after a measurement flight), send the remote command `Auto mode` and tick `Reboot afterwards`. Otherwise the unit would not start measuring by itself. If it already shows `Auto Mode` and values were changed in step 2, send the remote command `Reboot` instead so that they take effect.
4. Wait until the unit is online again and check in the `Current` column that the new values have arrived.
5. Send the remote command `Shut down`. As soon as the display shows `SHUTTING DOWN`, disconnect the power supply.

### Section II – Mounting

1. Screw the power bank onto the unit (4x M2x?? screws) [CHECK!].
2. Attach the antenna to the outside of the bodywork with the magnetic mount.
3. Place the unit in the interior or in another dry and safe place.

### Section III – Cabling and switching on

1. Connect the antenna to the unit:  
![Assignment of the antenna ports on the unit](../../../images/5gmu_antenna_ports.svg)
2. Connect the unit and the power bank with the USB-A to USB-A cable (modem).
3. Connect the unit and the power bank with the USB-C to USB-C cable. The Raspberry Pi starts.
4. After about 10 s the display shows the state.
5. In the backend under `Mission Status`, check that the unit is online. With push notifications, `Measurement box started` arrives.

### Section IV – Measuring

1. Wait until the display shows `Waiting: move` or Mission Status shows `Waiting for movement`. Before that it shows `No GPS fix` (or `Waiting for GPS fix`) as long as the unit has no position yet.
2. Drive off. The unit checks its position every 45 s and needs two checks in a row showing movement. Measuring therefore starts about a minute and a half after departure. The display then shows `Measuring` (`Measuring` in Mission Status); with push notifications, `Measurement started` arrives.
3. Drive. A datapoint is created every 15 m. None are created while standing.
4. Look at the display or at `Mission Status` from time to time:
    - `Valid` should rise with `Tot`. `Inv` greater than 0 is possible.
    - If `PIPELINE BROKEN` is on the display or the push notification `Error` arrives, see [Troubleshooting](../troubleshooting/failure-modes.md).
    - After an error, the unit can reboot itself and then carries on. In case of more serious problems it switches to a maintenance mode, see [Automatic reboot and `CRITICAL ERROR`](../troubleshooting/failure-modes.md#automatic-reboot-and-critical-error).

### Section V – Ending the measurement

1. Stop at the destination and stay there. After 1800 s without movement (default `Idle threshold`), the unit ends the measurement by itself.
2. The unit finalizes the data (`Finalizing`), uploads it and shuts down (`SHUTTING DOWN`). With push notifications, `Measurement finished` and `New runs uploaded` arrive.

!!! warning "Ending the measurement early"

    If you do not want to wait, end the measurement with the remote command [`Stop measuring`](remote-commands.md#stop-measuring). At the next switch-on the unit then boots once into Manual Mode and only measures after `Start measuring`. For the next measurement drive, switch it on once and shut it down again, or send `Start measuring` in Manual Mode. After that, Auto Mode applies again.

!!! tip "Next"

    Continue with [After use](after-use.md).

# Mission status

`Mission Status` shows what a unit is currently doing. It is based on the last heartbeat it sent. The page updates itself; `Refresh` reloads immediately.

At the top you select the unit. It counts as `online` (green circle next to the name) if a heartbeat has arrived in the last 5 minutes.

## Run phase

The bar at the top shows which phase of the run the unit is in. The same phase is in the `State` tile and, shorter, on the unit's display.

| Backend | Display | Meaning |
|---|---|---|
| `Starting up` | `Starting up` | The software is starting and bringing up the cellular link |
| `Recovering pending data` | `Recovering data` | A previous run was interrupted; the unit tidies up its data before continuing |
| `Idle in Manual Mode` | `Idle (manual)` | Manual Mode: waits for `Start measuring` |
| `Idle (recovery)` | `Idle (recovery)` | One-time start after repeated errors: waits for `Start measuring`, see [Automatic reboot](../measurement-unit/troubleshooting/failure-modes.md#automatic-reboot-and-critical-error) |
| `Waiting for GPS fix` | `No GPS fix` | No position yet, see [Known failure modes](../measurement-unit/troubleshooting/failure-modes.md). In Manual Mode only after `Start measuring` |
| `Waiting for movement` | `Waiting: move` | Auto Mode: position available, but the drive is not yet confirmed |
| `Measuring` | `Measuring` | A run is in progress |
| `Finalizing` | `Finalizing` | Measurement data is being finalized and uploaded |
| `Done` | `Done` | Run ended, shutdown is imminent |
| `Stopping` | `STOPPING` | The software is being terminated from outside (e.g. for maintenance via SSH); the device keeps running |

In the recovery state, a notice about the crash additionally appears. Instead of the bar, a notice appears when the unit is shutting down (`SHUTTING DOWN`), rebooting (`REBOOTING`) or in maintenance mode (`CRITICAL ERROR`). For maintenance mode, the notice also states how often the same error occurred and how many reboots in a row there were. What to do then is described under [Automatic reboot and `CRITICAL ERROR`](../measurement-unit/troubleshooting/failure-modes.md#automatic-reboot-and-critical-error).

## Tiles

| Tile | Content |
|---|---|
| `Latest Heartbeat` | Time of the last heartbeat and how long ago it was |
| `GPS Fix` | `Fix acquired` or `No fix`, number of satellites, age of the fix |
| `State` | current run phase, see above |
| `Mode` | `Auto Mode` or `Manual Mode` |
| `Datapoints` | Cell measurements since the start of the current run, split into `Valid` and `Invalid` |
| `Pending Files` | Measurement files that have not yet been uploaded |
| `Disk Free` | free storage space on the unit |

A measurement is invalid if RSRP, RSRQ or SINR is missing or outside the range that the mobile standard allows. The modem then did not deliver a real measured value. A weak signal does not make a measurement invalid. If the share of invalid measurements rises considerably during the drive, something is wrong with the modem, see [Known failure modes](../measurement-unit/troubleshooting/failure-modes.md).

## Remote commands

Below that, superusers see the `Remote Commands` and the `Command status`. Which commands exist and when they take effect is described under [Remote commands](../measurement-unit/usage/remote-commands.md). If the unit is offline, a command stays queued for 24 hours and is delivered with the next heartbeat.

Self-tests and the GPS fix test for finding a good antenna position are described by the [Test visualization](test-visualization.md).

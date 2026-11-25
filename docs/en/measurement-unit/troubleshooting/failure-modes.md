# Known failure modes

The failure modes are sorted by what you see on site: on the display of the unit, in Mission Status in the backend or in missing data. For each failure mode there is the likely cause and what you can do on site. The meaning of the displays is described under [Status display](../usage/measurement-runs.md#status-display).

!!! question "Unknown errors"
    If you encounter failure modes that are not listed below, please document them as precisely as possible with date and time, so that the cause and, ideally, a solution can be found afterwards from the behaviour and the logs.

## No GPS fix, measurement does not start

**What you see:** The display shows `No GPS fix` and `GPS: no fix`; in Mission Status the unit is at `Waiting for GPS fix`. In Auto Mode, the pass ends without measurement data after the `Max wait for first GPS fix` (default 300 s). In Manual Mode, the unit keeps waiting without a time limit after `Start measuring`.

**Cause:** The GNSS receiver finds no or too few satellites.

- The antenna needs a clear view of the sky. Buildings, garages, metal housings and shadowing by the vehicle or drone prevent reception.
- After a cold start, the first fix can take several minutes even with a clear view.
- Electronics near the antenna can disturb reception, especially the modem and USB 3.0 ports.

**What you can do:**

1. Take the unit outside and wait a few minutes before assuming a problem.
2. Place the antenna differently. The GPS fix test helps with this: while idle in Manual Mode (`Idle (manual)`), the satellite count can be watched live in the backend under `Testing Visualization` (superuser rights only), see [Remote commands](../usage/remote-commands.md#overview).
3. If the display shows a diagnostic below the GPS line (e.g. about an antenna fault), check the antenna and its connector.

## Fix available, but measurement does not start

**What you see:** The display shows `Waiting: move`, `Idle (manual)` or `Idle (recovery)`.

**`Waiting: move`:** The unit is in Auto Mode and waits for confirmed movement. It checks the position every 45 s and by default needs two checks in a row in which it is at least 10 m away from the position at the first fix. This means that about a minute and a half passes after departure until measuring starts. If a home position is set, the unit must also have moved far enough away from it. The values are in the [Configuration](../usage/configuration.md#movement-detection-before-start).

!!! info "Values"
    The values mentioned are all configurable, which means the time that passes after departure can also be considerably shorter or longer!

**`Idle (manual)`:** The unit is in [Manual Mode](../usage/measurement-runs.md#manual-mode) and only measures after the remote command `Start measuring`. It is there if you switched it to Manual Mode, or once after `Stop measuring` in Auto Mode.

**`Idle (recovery)`:** The unit rebooted after repeated errors and waits once for `Start measuring`, see [Automatic reboot and `CRITICAL ERROR`](#automatic-reboot-and-critical-error).

**What you can do:**

- Send `Start measuring` in the backend. The command only arrives with the next heartbeat, see [Remote commands](../usage/remote-commands.md). The unit then waits for a GPS fix and starts measuring.
- If the unit is to start by itself again in future, send the remote command `Auto mode`. It takes effect from the next start.

## No cellular connection, unit does not report to the backend

**What you see:** There are no current heartbeats in the backend; remote commands and changes do not arrive.

**Causes and measures:**

- **SIM not inserted or locked.** If the SIM cannot be unlocked, the unit shuts down shortly after starting. Check and reinsert the SIM, check the SIM PIN and the SIM card.
- **Dead zone or hanging connection.** If the connection stays away for longer than 180 s, the unit restarts the connection service itself. If this does not help twice, it additionally resets the radio module. If the connection stays away, it repeats these steps at ever larger intervals (up to 30 min) and never gives up. A running measurement carries on meanwhile; the data stays on the unit and is uploaded later.
- **Modem drops out.** If the connection to the modem breaks (e.g. due to voltage dips), the unit tries up to 10 times to open it again. Only after that does the run end with an error. Check the power supply, see [Power supply](../maintenance/power-supply.md).
- **Backend not reachable.** If the backend does not respond or responds with a server error, the problem is not with the unit. The unit tries again at the next interval.
- **Credentials do not match.** If the device ID or key do not match the backend, the backend rejects the unit with “unauthorized”. This has to be corrected on the unit or in the backend, see [Configuration](../usage/configuration.md#only-settable-on-the-unit).
- **Commands are ignored although heartbeats arrive.** See [Remote commands](../usage/remote-commands.md): without a signing key, the unit discards all commands.

## No data in the backend after a deployment

Measurement data is uploaded when measuring begins and after the run ends, also on shutdown or reboot and by the remote command `Force upload`. If data is missing, these causes are possible:

- **The unit had no connection.** The data stays on the unit and is uploaded as soon as a connection exists again, at the latest at the next start. Switch the unit on with a connection and wait.
- **The unit was not ended properly.** When the power supply is disconnected, at most the last line of datapoints is lost. The rest is saved at the next start (`Recovering data`) and uploaded. It is best to disconnect the power only when the display shows `SHUTTING DOWN`.
- **No measurement was running.** In Manual Mode no run is created without `Start measuring`, and in Auto Mode none without a GPS fix or movement. See above.
- **The backend rejects the data.** If the device ID of the measurement data does not match that of the registered device, the backend rejects it. See [Configuration](../usage/configuration.md#only-settable-on-the-unit).

In the backend you can check under `Measurement Runs` which runs have arrived.

## Unit shuts down or reboots unexpectedly

This can be intended. There are several reasons why the unit ends:

- It ends the run in Auto Mode when no movement was detected for 1800 s (see [Measurement drive](../usage/measurement-drive.md#section-v-ending-the-measurement)). In Manual Mode this never happens.
- It was ended by the remote command `Shut down` or `Reboot`. In the backend the commands are visible in the command status.
- The power supply has failed or is too weak. An empty or overloaded power bank can cause voltage dips without the unit shutting down cleanly. The measurement data is not lost then; the unit saves it at the next start.
- It rebooted itself after an error, see the next section.

## Automatic reboot and `CRITICAL ERROR`

If an unexpected error occurs in the software, the unit reboots instead of stopping. The software remembers how often the same error occurred in a row and escalates in three stages:

1. **Reboot.** On the first error the unit reboots and carries on normally. After the reboot you briefly see `Recovering data` if data has to be saved.
2. **Recovery.** If the same error occurs 3 times in a row (or there were 5 reboots in a row), the unit boots once into the recovery state. The display shows `Idle (recovery)`; in the backend a notice about the crash appears. The unit only measures after the remote command `Start measuring`. The start after that is normal again; the mode stays unchanged.
3. **Maintenance mode.** If an error occurs even then, the unit boots into maintenance mode. It reports a critical error in the backend (`Mission Status`: `Critical error`, push notification `Error`). In this mode the display is no longer driven and stays empty or still shows the last display before the reboot. In this mode it no longer measures. Only the cellular link keeps running so that the unit remains reachable for troubleshooting.

You cannot leave maintenance mode by remote command. It is lifted on the device once the cause has been found.

If the unit's configuration cannot even be loaded or the start fails before measuring, the unit goes directly into maintenance mode without a reboot. Once the cause is fixed, it starts normally again at the next switch-on. If it cannot load the configuration at all, it also does not report to the backend and is only reachable via SSH.

**What you can do:**

- Note down the notice in `Mission Status` (kind of error, number of repetitions) and write down what the unit did last and since when the error has occurred.
- Do not repeatedly switch the unit off and on. The error persists, and the unit remembers its state across reboots.
- Report the unit to the person responsible for the software. The unit automatically stores the error message with the kind of error and sequence on every crash.

## `PIPELINE BROKEN`

**What you see:** The display shows `PIPELINE BROKEN`; the backend reports the measurement chain as broken.

**Cause:** While moving, the unit received several measurements in a row without measured values from the modem (3 by default). This happens in a dead zone, but also with a modem that no longer responds.

**What you can do:**

- Continue the drive or flight briefly: in a dead zone the measurement chain recovers by itself.
- If the display stays, send `Reset SIM` in the backend. The command rebuilds the connection to the modem, see [Remote commands](../usage/remote-commands.md#overview).
- If that does not help, reboot the unit (`Reboot`) and check the power supply.

Individual invalid measurements (`Inv` on the display) are normal. They only become a problem when `PIPELINE BROKEN` appears.

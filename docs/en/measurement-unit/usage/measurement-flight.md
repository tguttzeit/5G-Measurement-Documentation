# Measurement flight

Measuring with the DJI Matrice 300 RTK drone. The unit runs in Manual Mode: it connects and waits until the measurement is started by remote command, and measures until it is stopped by remote command.

## What you need

- The prepared unit (see [Preparing the unit](preparation.md)), still connected there and opened in the backend under `Remote Configuration`
- `INIU Powerbank`, charged, with 4x M2x?? screws [CHECK! length]
- Adapter plate (unit on top) or double mount (unit below), see Section II
- M3x?? screws and washers if needed, reusable cable ties
- USB-A to USB-A and USB-C to USB-C cables
- Agreement with the remote pilot on the area, grid and speed

## Procedure

### Section I – What to look for in the configuration

#### Planning the grid

How dense the datapoints are depends on the flight grid and the capture interval. Before the flight, agree with the remote pilot which area is flown with which track spacing and at which speed. With a fixed track spacing and a known speed, measuring by time (`time`) is the easiest to plan. Background under [Capture interval and grid density](configuration.md#capture-interval-and-grid-density).

Enter the known values below; the rest is calculated as far as possible. Calculated fields are dashed and bold. A calculated field can be overwritten; it then counts as known.

The area is assumed to be a rectangle that is flown in parallel tracks along its length (meander). The flight distance includes the connections between the tracks, but not approach, turns or climbing.

<div class="flugplanung"
     data-msg-invalid="Please enter positive numbers only."
     data-msg-conflict="The entered values do not fit together. Clear one field so that it is calculated."
     data-msg-short-interval="The capture interval must be at least 1 s."
     data-msg-short-distance="Point spacings below about 10 m are within the range of GPS inaccuracy. With distance, the unit then counts noise as movement; time is the better choice here.">
  <fieldset>
    <legend>Measurement along the track</legend>
    <div class="fp-grid">
      <label>Flight speed [m/s]<input type="text" inputmode="decimal" data-var="v"></label>
      <label>Capture interval [s]<input type="text" inputmode="decimal" data-var="t"></label>
      <label>Point spacing along the track [m]<input type="text" inputmode="decimal" data-var="d"></label>
    </div>
  </fieldset>
  <fieldset>
    <legend>Grid and area</legend>
    <div class="fp-grid">
      <label>Track spacing [m]<input type="text" inputmode="decimal" data-var="b"></label>
      <label>Length of the area, along the tracks [m]<input type="text" inputmode="decimal" data-var="L"></label>
      <label>Width of the area, across the tracks [m]<input type="text" inputmode="decimal" data-var="W"></label>
      <label class="fp-check"><input type="checkbox" data-square> Square grid (point spacing = track spacing)</label>
    </div>
  </fieldset>
  <fieldset>
    <legend>Entire flight</legend>
    <div class="fp-grid">
      <label>Flight distance [m]<input type="text" inputmode="decimal" data-var="S"></label>
      <label>Flight time [min]<input type="text" inputmode="decimal" data-var="T" data-scale="60"></label>
      <label>Number of datapoints<input type="text" inputmode="decimal" data-var="N"></label>
    </div>
  </fieldset>
  <p class="fp-result">Speed: <strong data-out="kmh">–</strong> km/h · Tracks: <strong data-out="tracks">–</strong></p>
  <p class="fp-result">Setting for <code>time</code>: <code>Capture interval</code> = <strong data-out="interval">–</strong> s · for <code>distance</code>: <code>Position threshold</code> = <strong data-out="threshold">–</strong> m</p>
  <div class="fp-notes" data-out="notes" hidden></div>
  <button type="button" data-reset>Clear all fields</button>
</div>

Datapoints are counted per capture. With 5G NSA, two datapoints are created per capture (LTE and 5G), see [What is measured](measured-values.md#how-a-datapoint-is-created).

#### Applying the settings

1. In `Remote Configuration`, set the following settings:

    | Setting | For the measurement flight | Why |
    |---|---|---|
    | `Mission type` | `drone` | Marks the data in the backend as a drone measurement. It has no influence on how the measurement runs. |
    | `Capture gate` | `time` (recommended) or `distance` | see [Planning the grid](#planning-the-grid) |
    | `Capture interval` or `Position threshold` | Value from the calculator | determines the spacing of the datapoints |

2. Submit the changes with `Send & Confirm`.
3. In `Mission Status`, send the remote command `Manual mode` and tick `Reboot afterwards`. In Manual Mode the unit does not wait for movement and does not end the measurement when the drone hovers.
4. Wait until the unit is online again. In the `Current` column, check that the new values have arrived. The display now shows `Idle (manual)`.
5. Send the remote command `Shut down`. As soon as the display shows `SHUTTING DOWN`, disconnect the power supply.

!!! warning "Reset after the measurement flight"

    `Mission type` and Manual Mode stay set like this after the flight. Before the next measurement drive they have to be reset, see [Measurement drive](measurement-drive.md#section-i-what-to-look-for-in-the-configuration).

### Section II – Mounting

There are two options for mounting on the drone. With both, first screw the `INIU Powerbank` onto the unit (4x M2x?? screws).

=== "Unit on top, antenna below"

    1. Mount the adapter on the top of the drone (front 2x M3x12 mm, with washers if needed; rear 2x M3x10 mm).
    2. Fasten the unit to the adapter plate with the side screws (4x M3x?? mm [CHECK!]).
    3. Thread the antenna cables through the adapter and fasten the antenna to the adapter.
    4. Fasten antenna and adapter to the underside of the drone (4x M3x?? mm [CHECK!]).

=== "Unit and antenna below"

    1. Thread reusable cable ties into the tabs of the double mount.
    2. Fasten the antenna to the double mount.
    3. Screw the unit onto the double mount (4x M3x?? mm [CHECK!]).
    4. Mount the holder on the underside of the drone (M3x?? mm [CHECK!] with washers).
    5. Additionally fasten the holder to the landing legs of the drone with the cable ties.

!!! danger "Keep cables away from the rotors"

    Route all cables so that they cannot get into the area of the rotors.

### Section III – Cabling and switching on

1. Connect the antenna to the unit:  
![Assignment of the antenna ports on the unit](../../../images/5gmu_antenna_ports.svg)
2. Connect the unit and the power bank with the USB-A to USB-A cable (modem).
3. Connect the unit and the power bank with the USB-C to USB-C cable. The Raspberry Pi starts.
4. After about 10 s the display shows the state.
5. In the backend under `Mission Status`, check that the unit is online. With push notifications, `Measurement box started` arrives.

### Section IV – Starting the measurement

1. Wait until the display shows `Idle (manual)`.
2. Check whether the unit gets a GPS fix. While idle in Manual Mode it does not look for a position by itself, so the display shows `GPS: no fix`. Under `Testing Visualization`, use `Start GPS fix test`, see [Test visualization](../../backend/test-visualization.md). The display then shows `GPS: fix …` as soon as a position is available.
    - If no fix arrives, the antenna needs a clearer view of the sky. The test shows live whether another position is better.
3. As soon as the drone is in position, send the remote command `Start measuring` in `Mission Status`. It arrives with the next heartbeat, so not immediately. A running GPS fix test is ended automatically.
4. Only begin the grid when the display shows `Measuring` or the push notification `Measurement started` arrives.

!!! info "Starting without a GPS fix"

    After `Start measuring`, the unit first waits for a position. In this time the display and the backend show `No GPS fix` or `Waiting for GPS fix`. The wait has no time limit: the unit starts measuring as soon as a fix is available. With `Stop measuring` the start can be cancelled; the unit then returns to idle.

### Section V – During the flight

- On the display or in `Mission Status`, `Valid` should rise with `Tot`. `Inv` greater than 0 is possible.
- If `PIPELINE BROKEN` is on the display or the push notification `Error` arrives, see [Troubleshooting](../troubleshooting/failure-modes.md).
- After an error, the unit can reboot itself, see [Automatic reboot](../troubleshooting/failure-modes.md#automatic-reboot-and-critical-error). Afterwards it waits in Manual Mode for `Start measuring` again. After repeated errors it shows `Idle (recovery)` instead and also waits for `Start measuring`.

### Section VI – Ending the measurement

1. When the grid has been flown, send the remote command `Stop measuring` in `Mission Status`.
2. The unit finalizes the data (`Finalizing`), uploads it and shuts down (`SHUTTING DOWN`). With push notifications, `Measurement finished` and `New runs uploaded` arrive.
    - Alternatively, end the unit with `Shut down` or disconnect the power supply after landing. The data then stays on the unit and is uploaded during a later run.

!!! tip "Next"

    Continue with [After use](after-use.md).

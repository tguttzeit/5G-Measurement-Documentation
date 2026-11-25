# Map and export

The `Map / Heatmap` is the start page of the backend and shows the measurement results by location. It is also visible without login, though with restrictions, see [Guests and logged-in users](#guests-and-logged-in-users).

## Adjusting the display

| Setting | Effect |
|---|---|
| `Metric` | What is coloured: signal values (RSRP, RSRQ, SINR) or latency and throughput (baseline RTT, RTT under load, RTT p99, download, upload) |
| `Mission Type` | `ground` (preselected) or `drone`; both together is not possible |
| `Device ID` | only measurements of one unit; the ID must be known, there is no selection list |
| `Campaign` | one campaign or `All time`, see [Runs and campaigns](runs.md) and the note below |
| `Display style` | `Heatmap` or `Points`, see below |
| `Opacity` | how strongly the measurement data covers the map |

Holding the Ctrl key, you can drag a rectangle to which the map zooms. `Fullscreen` shows the map filling the screen.

## Colours

All metrics use the same scale from red (bad) through yellow to green (good). Values outside the range get the colour of the respective end.

| Metric | Red | Green |
|---|---|---|
| RSRP | -110 dBm | -80 dBm |
| RSRQ | -20 dB | -10 dB |
| SINR | 0 dB | 20 dB |
| Baseline RTT | 100 ms | 10 ms |
| RTT under load | 200 ms | 30 ms |
| RTT p99 | 350 ms | 60 ms |
| Download | 10 Mbit/s | 500 Mbit/s |
| Upload | 5 Mbit/s | 100 Mbit/s |

## Heatmap and points

**`Heatmap`** gives an overview. If the map section contains many signal measurements (from 2000), the backend combines them into grid cells and shows the mean per cell. The grid gets finer when zooming in. With fewer measurements, the heatmap shows the individual points; only almost coinciding points (less than 2.5 m apart) are merged. For latency and throughput, the heatmap always shows grid cells, each test at the midpoint between start and end position.

!!! warning "The heatmap always shows exactly one campaign"

    The heatmap never mixes data of several campaigns. If `All time` is selected, it still only shows the campaign with the most recent datapoint. Only the `Points` display style shows all data at once, including runs without a campaign.

**`Points`** shows every measurement individually. For latency and throughput, each test is a line from the position at the start to the position at the end of the test, because the unit keeps moving during the test.

## Selecting points

In the `Points` display style, measurements can be selected and evaluated.

- A click selects a point; a click with Shift held adds another or removes it again.
- Dragging a rectangle with Shift held selects all points in it.

Below the map, `Selected points` then appear with a `Selection statistics` (count, minimum, maximum, mean, median, standard deviation) and the list of points. Individual points can be removed there again; `Clear` cancels the selection.

## Export

| Export | Content | When available |
|---|---|---|
| `Export CSV`, `Export GEOJSON` | the heatmap data in the current map section: position, value of the selected metric and number of merged measurements | `Heatmap` display style, RSRP, RSRQ and SINR only |
| `Export PNG` | image of the current map section | `Heatmap` display style, RSRP, RSRQ and SINR only |
| `Export selection CSV`, `Export selection GEOJSON` | the selected points with position, RSRP, RSRQ, SINR, mission type and campaign | `Points` display style, RSRP, RSRQ and SINR only |

Only what is currently visible is exported. For more data, zoom out beforehand or move the map section. The exports contain no device IDs and no timestamps, not even for logged-in users.

## Viewing a run

`Show on map` in the [Measurement Runs](runs.md) opens the map with only this run, always in the `Points` display style. A notice above the map shows which run is visible. `Clear run filter` returns to the normal view.

## Guests and logged-in users

| | Guest | Logged in |
|---|---|---|
| Campaign | one campaign, preselected is the one with the most recent datapoint | additionally `All time` (only effective in the `Points` display style) |
| Runs without a campaign | not visible | in the `Points` display style with `All time` |
| `Device ID` | not available | available |
| Points | at most 5000, without device ID and time | limit from the [Settings](settings.md), with device and time in the selection list |
| Viewing a single run | not possible | via `Show on map` in [Measurement Runs](runs.md) |

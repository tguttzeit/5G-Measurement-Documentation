# What is measured

This page describes which values the unit collects, how they come about and what to keep in mind when evaluating them. When measuring happens is described under [How the unit measures](measurement-runs.md), how to set the spacing under [Configuration](configuration.md).

The unit collects two kinds of data:

| Kind | When | What |
|---|---|---|
| Radio measurement (datapoint) | at every capture, by distance or time | Signal values of the current cell, position, time |
| Latency test | at fixed intervals, only while moving and only if enabled | Response time and throughput of the connection to a test server |

## Radio measurement

### How a datapoint is created

At every capture, the unit asks the modem with the AT command `AT+QENG="servingcell"` for the cell it is currently registered on (serving cell). Neighbour cells are not recorded. Together with the latest GPS position and a UTC timestamp, this results in a datapoint.

If the modem reports several radio technologies at the same time, a separate datapoint with the same time and position is created per radio technology. This is the case with 5G NSA (Non-Standalone): there 5G is attached to an LTE anchor cell, and the modem reports one `LTE` line and one `NR5G-NSA` line.

| Radio technology (`rat`) | Meaning |
|---|---|
| `LTE` | 4G |
| `NR5G-NSA` | 5G Non-Standalone, together with an LTE anchor cell |
| `NR5G-SA` | 5G Standalone, without LTE |

A datapoint therefore says nothing about the cell that would be best at this location, but about the cell the modem is currently using. Which cell that is, is decided by the network.

### Signal values

| Value | Unit | Meaning | Valid range LTE / NR |
|---|---|---|---|
| RSRP (Reference Signal Received Power) | dBm | Received power of the cell's reference signal. Measure of signal strength: the higher (closer to 0), the stronger. | −140 to −44 / −156 to −31 |
| RSRQ (Reference Signal Received Quality) | dB | Ratio of the reference signal power to the total received power. Measure of signal quality under load and interference. | −19.5 to 2.5 / −43 to 20 |
| SINR (Signal to Interference plus Noise Ratio) | dB | Margin of the useful signal over interference and noise. Largely determines how fast data can be transmitted. | −20 to 30 / −23 to 40 |
| RSSI (Received Signal Strength Indicator) | dBm | Total received power in the channel, including interference. LTE only. | – |

If RSRP, RSRQ or SINR is outside the valid range or missing, the datapoint counts as invalid (`Inv` on the display). The modem then did not deliver a real measured value, e.g. because it is currently not registered. A weak but valid signal is not an invalid datapoint. Quality is only judged during evaluation, not on the unit.

### Further fields

| Field | Meaning |
|---|---|
| `mcc`, `mnc` | Country and network operator code (e.g. 262 / 02 for Vodafone Germany) |
| `cell_id`, `pci`, `tac` | Cell identity, physical cell identity, tracking area |
| `band`, `channel` | Frequency band and channel number (EARFCN or NR-ARFCN) |
| `vendor_specific_extras` | Further values from the modem, for LTE e.g. duplex mode, CQI, transmit power |

Not every modem and not every radio technology delivers every field. Missing values stay empty.

### Position and time

- **Position:** Latitude, longitude and altitude from the GNSS receiver, plus the number of satellites used. The accuracy is that of a simple GNSS receiver, i.e. a few metres.
- **Time:** UTC timestamp of the capture. The system clock is set from the GNSS time.
- **Run and device:** Every datapoint carries the device ID, the mission type (`ground` or `drone`) and the ID of the run.

!!! note "Altitude during measurement flights"

    The altitude comes from the unit's GNSS receiver, not from the drone. It is the altitude above sea level, not above ground, and considerably less accurate than the horizontal position. For a comparison by flight altitude, use the drone's altitude data.

### How densely it measures

By default, a datapoint is created as soon as the unit is 15 m away from the last datapoint. Anyone standing still creates no new datapoints. Alternatively, a fixed time interval can be set (default 15 s). Which setting suits which deployment is described under [Capture interval and grid density](configuration.md#capture-interval-and-grid-density).

## Latency and throughput

### How testing works

If the latency test is enabled, the unit runs tests against a test server with [`flent`](https://flent.org) as long as it is moving. There are two tests:

| Test | `flent` test | Default | Result |
|---|---|---|---|
| Baseline | `ping` | every 60 s, 10 s long | Response time (RTT) of the unloaded connection |
| Load test | `rrul` | every 15 min, 60 s long | Response time under load, download and upload throughput |

The load test (`rrul`, Realtime Response Under Load) fully loads the connection with several TCP streams in both directions and measures the response time at the same time. It shows how much the latency rises when the connection is saturated and how much throughput it delivers.

### Results

A test lasts several seconds, during which the vehicle moves. A latency result is therefore not a datapoint but has a start and an end time, each with its own position.

| Value | Meaning |
|---|---|
| `baseline_rtt_ms` | Median of the response time in the baseline test |
| `rtt_under_load_ms` | Median of the response time in the load test |
| `rtt_p99_ms` | 99th percentile of the response time: the slowest 1 % of responses |
| `download_mbits_s`, `upload_mbits_s` | Mean throughput in the load test in Mbit/s |

The response time is given as median and 99th percentile because a mean hides exactly the outliers that characterize a loaded connection.

### What latency tells and what it does not

- **The whole path is measured**, not only the radio link: unit → radio cell → operator core network → internet → test server and back. A high latency can also be due to the path through the internet or to the test server. Values from different deployments are only comparable if the same test server was used.
- **The load test influences the radio measurement:** During the 60 s of full load the unit keeps measuring. Radio values from this time, especially the quality, can be influenced by its own load.
- **Data volume:** A load test transfers as much as the connection delivers in 60 s, so roughly 750 MB at 50 Mbit/s in both directions. With a SIM card with limited volume, increase the spacing of the load tests or switch them off.
- **Only while moving:** A due test only runs if the last movement was at most 30 s ago. During longer standstills, no latency results are created.

The counterpart on the server is described in [Flent server](../../backend/dev/flent-server.md); all settings are in the [Configuration reference](../dev/configuration.md#latency_test).

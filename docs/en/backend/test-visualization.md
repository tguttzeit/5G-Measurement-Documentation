# Test visualization

The `Testing Visualization` collects the self-test results of all units. A self-test checks whether the unit's hardware is reachable and working, without starting a measurement. The page is only usable for superusers.

## Triggering a self-test

A self-test is triggered via the [remote command](../measurement-unit/usage/remote-commands.md) `Run self-test`, under `Remote Configuration` in the `One-Shot Commands` section. This only works while idle in Manual Mode (`Idle (manual)`). The unit stays idle meanwhile.

The unit runs all tests one after the other and reports each result as soon as the test is done. After the test, a notification with a link to this page appears.

A self-test started directly on the unit via the command line also ends up here, see [Setting up a unit](../measurement-unit/dev/unit-setup.md#checking-the-wiring-before-the-first-run).

## The tests

| Test | What is checked | Common cause of `failed` |
|---|---|---|
| `modem` | The modem can be opened and returns cell measurements on a query. | Modem not detected, SIM locked or not unlocked |
| `gps` | The GNSS receiver delivers a position within 5 seconds. | Antenna without a clear view of the sky, e.g. indoors; antenna not connected |
| `collector` | Modem and GNSS receiver work together: a cell measurement can be combined with a position. Nothing is saved. | as for `modem` or `gps` |
| `uploader` | The unit has a network connection (WLAN or cellular) with an IP address. Nothing is uploaded by the remote command. | no cellular connection, no WLAN |
| `heartbeat` | The unit can send a heartbeat to the backend. | Backend not reachable, wrong backend address |

If a function is switched off in the unit's configuration, e.g. the heartbeat, the associated test ends with `skipped`. The reason is then in the `Error Message` column.

The unit additionally checks the display, the keep-alive of the cellular link and the latency test. These results are only in the unit's log, not in the backend.

## Reading the results

The `Test Results` table shows every single test with test type, status, unit, time, duration and error message. The filters narrow it down by test type, status, device ID and period.

| Status | Meaning |
|---|---|
| `passed` | The test was successful |
| `failed` | The test failed; the cause is under `Error Message` |
| `skipped` | The test was not executed because the function is switched off |

For unit self-tests, the `Type` column always shows `Testing`. This separates the results from real measurement data.

The `Test Summary` above it shows the pass rate, the results by test type, the recent failures and the recent executions.

With `Delete selected` and `Delete All`, results can be removed. This cannot be undone.

## Finding a GPS fix

The GPS fix test helps to find a good position for the GPS antenna. It only runs while idle in Manual Mode (`Idle (manual)`). In the collapsible section `Find GPS Fix`, select the unit and begin the test with `Start GPS fix test`; end it with `Stop GPS fix test`.

While the test runs, the page continuously shows the number of satellites, whether a fix exists and how long the test has been running. The unit reports about every 2 seconds. All visible satellites are counted, so the number changes even before a fix exists. This way you can move the antenna and see directly whether the new position is better.

After 5 minutes, the unit ends the test by itself. A fix that was found also appears on the display and in `Mission Status`.

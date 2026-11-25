# Settings

Under `Settings` in the menu are the language, the push notifications and, for superusers, two backend settings. Without login only the language is available.

## Language and appearance

The interface is available in German and English. The language is chosen under `Settings` or, without login, at the top right. It only applies to the browser in which it was set.

Light or dark can be switched in the menu under `Theme` (`System`, `Light`, `Dark`).

## Push notifications

The backend can send a message to the smartphone or desktop on certain events. Delivery is via [ntfy](https://ntfy.sh); this requires the ntfy app. Notifications are off until you switch them on, and apply to all units.

### Setting up

1. Switch on `Send me notifications` and choose the desired events, then save.
2. Install the ntfy app and subscribe there to the displayed topic, on the server that the page names. `Copy topic` copies it to the clipboard.
3. Use `Send test notification` to check that the message arrives. After that you have to wait a few seconds before the next one can go.

The same topic can be subscribed on several devices.

### Events

| Event | When |
|---|---|
| `Measurement box started` | A unit reports again after at least three missed heartbeats, i.e. after switch-on or a reboot |
| `Measurement started` | A unit switches to `Measuring` |
| `Measurement finished` | A unit leaves `Measuring` |
| `New runs uploaded` | Measurement data has arrived in the backend |
| `Error` | A unit goes into maintenance mode (`CRITICAL ERROR`), the measurement chain delivers no measurements despite movement, or a remote command has failed |

Only the change is reported. If a unit stays in a state, no second message arrives.

!!! warning "The topic is the password"

    Anyone who knows the topic can read all notifications. They contain device ID, event and time and travel via the ntfy server, not only via the backend. So do not pass the topic on. If it has become known after all, create a new one with `Regenerate topic` and subscribe to it again in the app. The old one no longer works afterwards.

## Superusers only

### Raw datapoint limit

Sets how many individual points the [map](map.md) delivers at most to logged-in users in the `Points` display style. The default is `Unlimited`. A limit helps if the map becomes too slow with large amounts of data. For guests, a fixed limit of 5000 points always applies regardless.

### Shutdown confirmation

A unit that has shut down can no longer report that it is off. The backend therefore counts `Shut down` as successful if no heartbeat arrives for a certain time after the command was acknowledged, see [Remote commands](../measurement-unit/usage/remote-commands.md#shutting-down). This time is set here:

- `Heartbeat intervals`: 1 to 20 intervals of the respective unit, default 4
- `Fixed time span`: 10 to 3600 seconds

If the time span is shorter than a heartbeat interval, the page warns: a unit that is still running could then wrongly count as shut down.

# Backend

The backend receives the heartbeats and measurement data of the units, displays them and sends remote commands and configuration changes to the devices.

## Roles

Without login only the map is visible. Everything else requires an account, and control and administration additionally require superuser rights.

| Area | Guest | Logged in | Superuser |
|---|---|---|---|
| `Map / Heatmap` | one campaign, no device filter, at most 5000 raw datapoints | all campaigns and `All time`, device filter | as logged in |
| `Mission Status` | – | state of the devices | additionally `Remote Commands` and `Command status` |
| `Measurement Runs` | – | view | edit, move to the trash, restore and delete permanently |
| `Testing Visualization` | – | – | yes |
| `Settings` | Language | additionally push notifications | additionally raw datapoint limit and shutdown confirmation |
| `Remote Configuration`, `Campaign Management`, `User Management` | – | – | yes |

Notifications about uploads and command acknowledgements only appear for superusers.

## Logging in

Click `Login` at the top right and enter username and password. After logging in, your own name at the top right opens the menu with all pages that your role allows.

The session expires after some time (default 30 min). The backend then redirects to the login, after which you continue on the page you had open before.

## Changing the password

Under `Change Password` in the menu. The new password needs at least 8 characters. After 5 wrong entries of the current password, the change is locked. A successful login lifts the lock, or a superuser resets the password.

## Managing accounts

Superusers create accounts under `User Management`, make them superusers, deactivate or delete them. You cannot change your own permissions there, and you can neither deactivate nor delete your own account.

Accounts for units are something different: devices are not created in the interface but on the server, see [Device registration](dev/device-registration.md).

## Where to find what

- State of a unit: [Mission status](mission-status.md)
- Self-tests and GPS fix test: [Test visualization](test-visualization.md)
- Checking whether measurement data has arrived: [Runs and campaigns](runs.md)
- Viewing and exporting measurement results: [Map and export](map.md)
- Controlling the unit remotely: [Remote commands](../measurement-unit/usage/remote-commands.md)
- Changing the unit's settings: [Configuration](../measurement-unit/usage/configuration.md#remote-configuration-in-the-backend)
- Push notifications and language: [Settings](settings.md)

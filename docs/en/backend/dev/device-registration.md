# Device registration

Units do not log in with a user account but with a device ID and a key of their own. Every new unit therefore has to be registered once in the backend. This is not possible in the interface, only on the server.

## Registering

On the server, in the backend's directory:

```bash
docker compose exec backend python scripts/register_device.py <device_id>
```

The folder `scripts/` is mounted into the container; a call on the host is not necessary.

The script outputs two values:

| Value | Where on the unit | Purpose |
|---|---|---|
| `API Key` | `[backend] device_key` | The unit identifies itself with it on every request (`X-Device-ID`, `X-Device-Key`). |
| `HMAC Secret` | `[heartbeat] hmac_secret` | The unit uses it to verify the signature of the heartbeat responses. Without it, it discards all remote commands and configuration changes, see [Remote commands](../../measurement-unit/usage/remote-commands.md). |

!!! warning "Both values are only shown once"

    The backend only stores a hash of the key. Copy the values into the unit's configuration immediately. The same ID cannot be registered a second time; the script then aborts with `already exists`. If the values are lost, they can be [rotated](#rotating-the-keys) for the same ID.

The `device_id` on the unit under `[heartbeat] device_id` must be exactly as at registration, see [Configuration of the unit](../../measurement-unit/usage/configuration.md#only-settable-on-the-unit). Otherwise the backend rejects heartbeats and uploads.

## Rotating the keys

If a key has been lost or has fallen into the wrong hands (e.g. unit passed on, SD card set up again), this script creates a new API key and a new HMAC secret for a registered unit:

```bash
docker compose exec backend python scripts/rotate_device_credentials.py <device_id>
```

As with registration, both values are only shown once. There is no transition period: from now on the backend rejects the old key with `401`, and the unit discards the heartbeat responses because they are signed with the new secret. Until both new values are in its `config.local.toml`, the unit is cut off from the backend. Therefore only switch over a unit that you can reach via SSH, in this order:

1. Check that logging in via SSH on the unit works.
2. Run the script and copy both values.
3. On the unit, replace `[backend] device_key` and `[heartbeat] hmac_secret` in the `config.local.toml` and restart the measurement software (`sudo systemctl restart 5g-measurement.service`).
4. In `Mission Status`, check that heartbeats arrive again.

Queued configuration changes and commands are kept. They go out with the next heartbeat and are then signed with the new secret.

## What a unit may do with its key

The device key only opens the endpoints through which a unit delivers:

- `POST /api/heartbeat`: heartbeat
- `POST /api/measurements`: measurement data
- `POST /api/latency-results`: latency results
- `POST /api/testing/results`: self-test results
- `POST /api/devices/<device_id>/gps-fix-test/status`: interim results of the GPS fix test

Reading, deleting and everything else is reserved for user accounts.

## First user account

There is no public registration. The first superuser is also created on the server:

```bash
docker compose exec backend python scripts/create_user.py <username> <password> --superuser
```

This superuser then creates further accounts in the interface under `User Management`, see [Backend](../index.md#managing-accounts).

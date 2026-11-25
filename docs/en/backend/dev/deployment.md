# Deployment

In production, the backend runs entirely via Docker Compose. Only the counterpart for the latency tests runs outside, see [Flent server](flent-server.md).

## Services

| Service | Profile | Purpose |
|---|---|---|
| `postgres` | always | Database, data in the volume `postgres_data` |
| `backend` | always | API, only reachable locally on `127.0.0.1:8000` |
| `frontend-prod` | `prod` | built interface |
| `caddy` | `prod` | HTTPS with an automatic certificate, forwards `/api` to `backend`, `/docs` to this documentation and everything else to `frontend-prod` |

## Prerequisites

- A DNS entry for the domain points to the server.
- Ports 80 and 443 are open for Caddy. Nothing else needs to be publicly reachable.
- A `.env` with real values for `POSTGRES_PASSWORD`, `DATABASE_URL`, `SECRET_KEY` and `SITE_DOMAIN`, see [Configuration](configuration.md).

## Starting

In the backend's directory:

```bash
docker compose --profile prod up -d
```

When the `backend` container starts, the database migrations run automatically (`alembic upgrade head`). By hand it works with:

```bash
docker compose exec backend alembic upgrade head
```

Whether the API is running is shown by `https://<domain>/api/health`; the response is `{"status": "ok"}`.

Afterwards create the first superuser and the units, see [Device registration](device-registration.md).

## Updating

The server runs on a checkout of the public backend repository, branch `main`. New versions arrive there as a release with a tag.

1. **Back up the database. Mandatory before every update.** When the new container starts, the migrations run automatically. If one goes wrong, only the backup helps:

    ```bash
    sudo -u dbbackup deploy/backup-db.sh --pre-update
    ```

    The script runs under the account that owns the backup directory; `sudo -u` is omitted if that is your own. The backup ends up in `pre-update/` in the [backup directory](#data-backup); the three newest are kept. If the script aborts with an error, do not continue.

2. **Fetch the new version:**

    ```bash
    git pull
    ```

3. **Rebuild and start.** The images are built on the server, not pulled from a registry:

    ```bash
    docker compose --profile prod up -d --build
    ```

4. **Check:** `https://<domain>/api/health` answers with `{"status": "ok"}`, the interface loads, and heartbeats arrive again in `Mission Status`.

An update only affects the [Flent server](flent-server.md) if `scripts/start_flent_server.sh` or `deploy/flent-server.service` have changed. Then copy both again as during setup and run `sudo systemctl restart flent-server.service`. If `deploy/5gm-db-backup.service` or `deploy/5gm-db-backup.timer` have changed, copy both to `/etc/systemd/system/` again and run `sudo systemctl daemon-reload`; a drop-in is preserved.

### Going back to the previous version

1. Check out the previous state via Git, e.g. the previous release tag.
2. If the update migrated the database, [restore](#restoring) the backup from before the update before the backend starts again.
3. Rebuild and start as above.

## Data backup

The units delete their files after the upload. The database is then the only copy of all measurement data. `deploy/backup-db.sh` backs it up with `pg_dump` from the running `postgres` container, triggered once a day by `deploy/5gm-db-backup.timer`.

| Directory | Content | Kept |
|---|---|---|
| `daily/` | daily backup | the 7 newest |
| `weekly/` | the first backup of each calendar week | the 4 newest |
| `pre-update/` | backups before an update (`--pre-update`) | the 3 newest |

- The backup directory is `/var/backups/5g-measurement-backend`, changeable via `BACKUP_DIR`.
- Retention is by count, not by age: if the timer did not run for a while, the last backups are kept anyway.
- A backup only replaces older ones once it is complete and can be read with `pg_restore --list`. If it fails, the service ends with an error and the existing backups stay untouched.
- If less than 5 GB is free in the backup directory (`BACKUP_MIN_FREE_MB`), the run writes a warning to the journal.
- The backups are only on the server itself. They help with a failed migration, a broken volume or an operating error, not if the server itself is lost.

### Setting up

1. Create a system account of its own without login for the backup. It needs access to Docker:

    ```bash
    sudo useradd -r -U -s /usr/sbin/nologin -G docker dbbackup
    ```

    Do not use the `appuser` account of the [Flent server](flent-server.md). Being a member of the `docker` group is equivalent to root rights, and `irtt` is reachable from the network.

2. Create the backup directory, readable only for this account:

    ```bash
    sudo install -d -o dbbackup -g dbbackup -m 700 /var/backups/5g-measurement-backend
    ```

3. Copy the units:

    ```bash
    sudo cp deploy/5gm-db-backup.service deploy/5gm-db-backup.timer /etc/systemd/system/
    ```

4. The service starts `deploy/backup-db.sh` in the backend's checkout and expects it under `/opt/5g-measurement-backend`. If the checkout is elsewhere or the backup runs under a different account, enter both in a drop-in (`sudo systemctl edit 5gm-db-backup.service`):

    ```ini
    [Service]
    User=<account>
    Group=<group>
    ExecStart=
    ExecStart=<backend-directory>/deploy/backup-db.sh
    ```

    The empty `ExecStart=` is necessary, otherwise the new command is added to the old one. The backup directory must then belong to this account.

5. Enable the timer and trigger the first backup by hand:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now 5gm-db-backup.timer
    sudo systemctl start 5gm-db-backup.service
    ```

### Checking

```bash
systemctl list-timers 5gm-db-backup.timer                 # next run
journalctl -u 5gm-db-backup.service -n 20                 # latest runs with backup size
journalctl -u 5gm-db-backup.service -p warning --since -7d # errors and warnings
sudo ls -l /var/backups/5g-measurement-backend/daily
```

A failed backup is also shown by `systemctl --failed`.

### Restoring

Restoring is only done by hand. The backend must be stopped meanwhile, otherwise it works with a half-filled database.

1. Stop the backend:

    ```bash
    docker compose stop backend
    ```

2. Empty the database by recreating it. `pg_restore --clean` is not enough for this: it only deletes what occurs in the backup and would leave tables of a failed migration behind.

    ```bash
    docker compose exec -T postgres dropdb -U postgres measurement_backend
    docker compose exec -T postgres createdb -U postgres measurement_backend
    ```

    If the volume `postgres_data` was lost and has been recreated, this step is omitted: the container creates the empty database itself on first start (`docker compose up -d postgres`). However, the role under which the backend logs in is then missing, because `pg_dump` does not back up roles. Name and password are in `DATABASE_URL` in the `.env`:

    ```bash
    docker compose exec postgres psql -U postgres -c "CREATE ROLE <role> LOGIN"
    docker compose exec postgres psql -U postgres -c "\password <role>"
    ```

    `\password` prompts for the password, so it does not end up in the shell history.

3. Restore the backup:

    ```bash
    sudo cat /var/backups/5g-measurement-backend/<directory>/<file>.dump \
      | docker compose exec -T postgres pg_restore -U postgres -d measurement_backend --exit-on-error
    ```

4. Start everything again and check as after an update:

    ```bash
    docker compose --profile prod up -d --build
    ```

!!! warning "Restoring overwrites everything since the backup"

    The database then has the state of the backup. Measurement data uploaded since the backup is lost. The units do not upload it again.

!!! danger "Backups contain everything"

    A backup contains all measurement data, the user accounts with password hashes and the hashes of the device keys. Never put the directory in a path that Caddy serves, and do not give it additional permissions.

## This documentation

Caddy serves this documentation under `/docs` from the directory `DOCS_DIR`. It is built on the same server from its own repository, driven by a `systemd` timer. Setup and procedure are described there in `deploy/README.md`.

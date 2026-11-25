# Local testing

This page describes the backend's development environment, the automated tests and testing with a real unit on the local network.

## Development environment

Prerequisites: [`uv`](https://docs.astral.sh/uv/), Docker with the Compose plugin, Node.js for the interface.

1. Install the dependencies:

    ```bash
    uv sync
    ```

2. Start only the database and apply the migrations:

    ```bash
    docker compose up -d postgres
    uv run alembic upgrade head
    ```

3. Start the API with automatic reloading:

    ```bash
    uv run uvicorn app.main:app --reload
    ```

    `http://localhost:8000/health` answers with `{"status": "ok"}`. The defaults for local development come from `.env.dev`; your own values in `.env` take precedence, see [Configuration](configuration.md).

4. Start the interface in a second terminal. The development server forwards `/api` to the API:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

A local user account is created by `uv run python scripts/create_user.py <username> <password> --superuser`.

## Automated tests

```bash
uv sync --group dev
uv run pytest tests/unit          # unit tests
uv run pytest tests/integration   # integration tests, need Docker
uv run pytest                     # everything
uv run ruff check .               # lint
```

- **Unit tests** only need the Python environment. The exception is `tests/unit/test_latency_results.py`, which needs the local database from the development environment including migrations.
- **Integration tests** start a Postgres container of their own per test run via `testcontainers` and clean it up afterwards. Docker has to be running for this. After every test, all tables are emptied.

For the interface, before every commit:

```bash
cd frontend
npm run build
npm run lint
npm test
```

CI runs lint, migrations, unit and integration tests on every push to `main` and on every pull request.

## Creating migrations

After changes to the models in `app/models/`:

```bash
uv run alembic revision --autogenerate -m "short description"
```

Review the generated migration before committing; `--autogenerate` does not detect everything.

## With a real unit on the local network

The unit only speaks HTTPS. For a test without the production server, the whole backend therefore runs on a machine on the same network as the unit, with a certificate from a local certificate authority. Everything about it is only meant for tests: fixed credentials, a throwaway database, a locally issued certificate.

### Starting

Prerequisites on the machine: Docker with Compose, port `8443` open in the firewall for the unit, the machine's IP address on the local network (e.g. via `ip -4 addr`).

```bash
scripts/lan-dev.sh up <ip-of-the-machine>
```

This builds and starts the stack as a Compose project of its own with its own volumes, applies the migrations, registers a test device, creates a superuser and exports the root certificate to `deploy/lan-dev/lan-dev-root-ca.crt`. The first start takes a few minutes.

| Command | Effect |
|---|---|
| `scripts/lan-dev.sh logs [backend\|caddy\|…]` | Show logs |
| `scripts/lan-dev.sh ca` | Export the certificate again |
| `scripts/lan-dev.sh down` | Stop, data is kept |
| `scripts/lan-dev.sh down -v` | Stop and delete the database |

### Credentials

| What | Value |
|---|---|
| `device_id` | `devbox-1` |
| `device_key` | `lan-dev-device-key-0123456789abcdef0123456789abcdef` |
| `hmac_secret` | `lan-dev-hmac-secret-fedcba9876543210fedcba9876543210` |
| Login in the interface | `admin` / `lan-dev-admin-pw` |

Other values are set by `scripts/seed_dev_device.py <id> --device-key … --hmac-secret …` as well as `ADMIN_USER` and `ADMIN_PASSWORD` for `lan-dev.sh up`. The login is valid for 8 hours in this stack.

### Switching the unit over

On the unit, back up your own `config.local.toml` and, for the test, replace or add the following sections in it; `<host>` is the IP from `up`. The other values (`[quectel_cm] binary`, `[uploader] upload_dir`) stay:

```toml
[backend]
url = "https://<host>:8443"
device_key = "lan-dev-device-key-0123456789abcdef0123456789abcdef"

[heartbeat]
device_id = "devbox-1"
hmac_secret = "lan-dev-hmac-secret-fedcba9876543210fedcba9876543210"

[device]
# Must match [heartbeat] device_id, otherwise the backend rejects uploads with 403
device_id = "devbox-1"

[selftest]
results_url = "https://<host>:8443/api/testing/results"

[gps_fix_test]
status_url = "https://<host>:8443/api/devices/devbox-1/gps-fix-test/status"
```

The unit has to trust the local certificate. To do so, copy the exported root certificate to the unit and install it there:

```bash
sudo cp lan-dev-root-ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
```

If the unit gets through, `scripts/lan-dev.sh logs backend` shows lines with `POST /heartbeat … 200` and `Mission Status` shows the unit `devbox-1` as online. A `401` means a wrong key; a rejected signature on the unit means a wrong `hmac_secret`.

!!! warning "Pitfalls on the unit"

    - With `uploader.debug_upload = true` (default), uploads run over the cellular interface and never reach the local network. For the test, set it to `false` in `config.toml`.
    - With `system.running_on_pi = true`, the unit really shuts down at the end of a run. For testing `Start measuring` and `Stop measuring`, set it to `false`.
    - With `system.running_on_pi = false`, the unit also does not start `quectel-CM` itself. The connection to the local network must then exist via `wlan0`.
    - `Promote overrides` writes values permanently into `config.toml`, and `Auto mode` changes the next start. Back up `config.toml` beforehand and send `Manual mode` again before a reboot.

### Problems

- **TLS error on the unit:** The certificate is not installed, or the address in the configuration differs from the one from `up`. Repeat `up` with the correct address; the certificate is reissued.
- **Nothing arrives:** Firewall on the machine, wrong IP or separated networks. Test from another machine on the network with `curl --cacert lan-dev-root-ca.crt https://<host>:8443/api/health`.
- **`401` on the heartbeat:** Device ID or key wrong. `seed_dev_device.py` resets them to the values from the table.
- **Starting over:** `scripts/lan-dev.sh down -v`, then `up` again.

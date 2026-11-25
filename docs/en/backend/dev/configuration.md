# Configuration

The backend is configured entirely via environment variables. They are in a file `.env` in the root directory of the repository, which is not checked in. The template is `.env.example`. For local development, uncritical default values are in `.env.dev`; values in `.env` take precedence.

## Required values

| Variable | Meaning |
|---|---|
| `POSTGRES_PASSWORD` | Password of the database user in the Postgres container |
| `DATABASE_URL` | Connection to the database, e.g. `postgresql+psycopg://app_user:<password>@postgres:5432/measurement_backend` |
| `SECRET_KEY` | signs the login tokens; in operation a long random value, otherwise tokens can be forged |

## Optional values

| Variable | Default | Meaning |
|---|---|---|
| `SERVER_HOST` | `0.0.0.0` | Address on which the API listens |
| `SERVER_PORT` | `8000` | Port of the API |
| `ENVIRONMENT` | `production` | Environment; some development scripts refuse to start with `production` |
| `ALGORITHM` | `HS256` | Signing algorithm of the tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validity of a login in minutes |
| `SELECTION_EXPORT_MAX_IDS` | `50000` | at most this many points per selection export on the map |
| `NTFY_BASE_URL` | `https://ntfy.sh` | ntfy server for push notifications |
| `NTFY_ACCESS_TOKEN` | empty | Token for a protected ntfy server; never logged or output |

## Production only

| Variable | Meaning |
|---|---|
| `SITE_DOMAIN` | Domain for which Caddy obtains the certificate |
| `DOCS_DIR` | Directory on the server from which Caddy serves this documentation under `/docs` (default `./docs-site`) |

!!! warning "Push notifications and data protection"

    Notifications contain device ID, event and time and go to the ntfy server. On the public `ntfy.sh`, only the user's secret topic protects the messages. For a sensitive deployment, operate your own ntfy server with access control and set `NTFY_BASE_URL` and `NTFY_ACCESS_TOKEN`.

The settings that superusers change in the interface (raw datapoint limit, shutdown confirmation), by contrast, are stored in the database, see [Settings](../settings.md#superusers-only).

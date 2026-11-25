# Development

This section is about operating or further developing the backend server. How to use the interface is described in the other pages under [Backend](../index.md).

## Structure

| Part | Technology | Purpose |
|---|---|---|
| API | Python, `FastAPI`, `SQLAlchemy`, `Alembic` | accepts heartbeats, measurement data and latency results from the units, delivers remote commands and configuration changes, serves the interface |
| Database | `PostgreSQL` | measurement data, runs, campaigns, users, devices, commands |
| Interface | `React`, `Vite`, `TypeScript` | the dashboard in the browser |
| Reverse proxy | `Caddy` | HTTPS with an automatic certificate, forwards `/api` to the API and `/docs` to this documentation |
| Latency counterpart | `netserver`, `irtt` | counterpart for the units' latency tests, runs outside Docker, see [Flent server](flent-server.md) |
| Push notifications | `ntfy` | external service, see [Settings](../settings.md#push-notifications) |

API, database, interface and Caddy run as Docker Compose services. The code is in the repository [`tguttzeit/5G-Measurement-Backend`](https://github.com/tguttzeit/5G-Measurement-Backend).

## Channels to the unit

The unit establishes all connections itself; the backend never reaches it on its own.

- **Heartbeat** (`POST /api/heartbeat`): status message at a fixed interval. The response contains queued remote commands and configuration changes, signed with the unit's key.
- **Measurement data** (`POST /api/measurements`) and **latency results** (`POST /api/latency-results`): uploads after a run or via `Force upload`.
- **Self-tests** and **GPS fix test**: separate endpoints for the results, see [Test visualization](../test-visualization.md).

All endpoints are in the [API reference](api/index.md).

## Pages

- [Configuration](configuration.md): environment variables of the backend
- [Device registration](device-registration.md): creating a new unit
- [Deployment](deployment.md): production operation with Docker Compose
- [Flent server](flent-server.md): counterpart for the latency tests
- [Local testing](local-testing.md): development environment, tests, testing with a real unit on the LAN
- [API](api/index.md): reference of all endpoints, generated from the code

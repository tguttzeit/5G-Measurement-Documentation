# Lokal testen

Diese Seite beschreibt die Entwicklungsumgebung des Backends, die automatischen Tests und den Test mit einer echten Messbox im lokalen Netz.

## Entwicklungsumgebung

Voraussetzungen: [`uv`](https://docs.astral.sh/uv/), Docker mit dem Compose-Plugin, für die Oberfläche Node.js.

1. Abhängigkeiten installieren:

    ```bash
    uv sync
    ```

2. Nur die Datenbank starten und die Migrationen anwenden:

    ```bash
    docker compose up -d postgres
    uv run alembic upgrade head
    ```

3. Die API mit automatischem Neuladen starten:

    ```bash
    uv run uvicorn app.main:app --reload
    ```

    `http://localhost:8000/health` antwortet mit `{"status": "ok"}`. Die Standardwerte für die lokale Entwicklung kommen aus `.env.dev`, eigene Werte in `.env` haben Vorrang, siehe [Konfiguration](konfiguration.md).

4. Die Oberfläche in einem zweiten Terminal starten. Der Entwicklungsserver leitet `/api` an die API weiter:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

Ein lokales Nutzerkonto legt `uv run python scripts/create_user.py <benutzername> <passwort> --superuser` an.

## Automatische Tests

```bash
uv sync --group dev
uv run pytest tests/unit          # Unit-Tests
uv run pytest tests/integration   # Integrationstests, brauchen Docker
uv run pytest                     # alles
uv run ruff check .               # Lint
```

- **Unit-Tests** brauchen nur die Python-Umgebung. Ausnahme ist `tests/unit/test_latency_results.py`, der die lokale Datenbank aus der Entwicklungsumgebung samt Migrationen braucht.
- **Integrationstests** starten pro Testlauf einen eigenen Postgres-Container über `testcontainers` und räumen ihn danach wieder ab. Docker muss dafür laufen. Nach jedem Test werden alle Tabellen geleert.

Für die Oberfläche vor jedem Commit:

```bash
cd frontend
npm run build
npm run lint
npm test
```

Die CI führt Lint, Migrationen, Unit- und Integrationstests bei jedem Push auf `main` und bei jedem Pull Request aus.

## Migrationen anlegen

Nach Änderungen an den Modellen in `app/models/`:

```bash
uv run alembic revision --autogenerate -m "kurze Beschreibung"
```

Die erzeugte Migration vor dem Commit durchsehen, `--autogenerate` erkennt nicht alles.

## Mit einer echten Messbox im lokalen Netz

Die Messbox spricht nur HTTPS. Für einen Test ohne den Produktivserver läuft deshalb das ganze Backend auf einem Rechner im selben Netz wie die Messbox, mit einem Zertifikat aus einer lokalen Zertifizierungsstelle. Alles daran ist nur für Tests gedacht: feste Zugangsdaten, eine Wegwerf-Datenbank, ein lokal ausgestelltes Zertifikat.

### Starten

Voraussetzungen auf dem Rechner: Docker mit Compose, Port `8443` in der Firewall für die Messbox offen, die IP-Adresse des Rechners im lokalen Netz (z. B. über `ip -4 addr`).

```bash
scripts/lan-dev.sh up <ip-des-rechners>
```

Das baut und startet den Stack als eigenes Compose-Projekt mit eigenen Volumes, wendet die Migrationen an, registriert ein Testgerät, legt einen Superuser an und exportiert das Wurzelzertifikat nach `deploy/lan-dev/lan-dev-root-ca.crt`. Der erste Start dauert einige Minuten.

| Befehl | Wirkung |
|---|---|
| `scripts/lan-dev.sh logs [backend\|caddy\|…]` | Logs anzeigen |
| `scripts/lan-dev.sh ca` | Zertifikat erneut exportieren |
| `scripts/lan-dev.sh down` | stoppen, Daten bleiben |
| `scripts/lan-dev.sh down -v` | stoppen und Datenbank löschen |

### Zugangsdaten

| Was | Wert |
|---|---|
| `device_id` | `devbox-1` |
| `device_key` | `lan-dev-device-key-0123456789abcdef0123456789abcdef` |
| `hmac_secret` | `lan-dev-hmac-secret-fedcba9876543210fedcba9876543210` |
| Anmeldung in der Oberfläche | `admin` / `lan-dev-admin-pw` |

Andere Werte setzen `scripts/seed_dev_device.py <id> --device-key … --hmac-secret …` sowie `ADMIN_USER` und `ADMIN_PASSWORD` für `lan-dev.sh up`. Die Anmeldung gilt in diesem Stack 8 Stunden.

### Messbox umstellen

Auf der Messbox die eigene `config.local.toml` sichern und für den Test die folgenden Abschnitte darin ersetzen bzw. ergänzen, `<host>` ist die IP aus `up`. Die übrigen Werte (`[quectel_cm] binary`, `[uploader] upload_dir`) bleiben stehen:

```toml
[backend]
url = "https://<host>:8443"
device_key = "lan-dev-device-key-0123456789abcdef0123456789abcdef"

[heartbeat]
device_id = "devbox-1"
hmac_secret = "lan-dev-hmac-secret-fedcba9876543210fedcba9876543210"

[device]
# Muss mit [heartbeat] device_id übereinstimmen, sonst weist das Backend Uploads mit 403 ab
device_id = "devbox-1"

[selftest]
results_url = "https://<host>:8443/api/testing/results"

[gps_fix_test]
status_url = "https://<host>:8443/api/devices/devbox-1/gps-fix-test/status"
```

Die Messbox muss dem lokalen Zertifikat vertrauen. Dazu das exportierte Wurzelzertifikat auf die Messbox kopieren und dort installieren:

```bash
sudo cp lan-dev-root-ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates
```

Kommt die Messbox an, zeigen `scripts/lan-dev.sh logs backend` Zeilen mit `POST /heartbeat … 200` und der `Missionsstatus` die Messbox `devbox-1` als online. Ein `401` heißt falscher Schlüssel, eine abgelehnte Signatur auf der Messbox heißt falsches `hmac_secret`.

!!! warning "Stolperfallen auf der Messbox"

    - Mit `uploader.debug_upload = true` (Standard) laufen Uploads über die Mobilfunkschnittstelle und erreichen das lokale Netz nie. Für den Test in `config.toml` auf `false` setzen.
    - Mit `system.running_on_pi = true` fährt die Messbox am Ende eines Laufs wirklich herunter. Für Tests von `Messung starten` und `Messung stoppen` auf `false` setzen.
    - Mit `system.running_on_pi = false` startet die Messbox auch `quectel-CM` nicht selbst. Die Verbindung ins lokale Netz muss dann über `wlan0` bestehen.
    - `Overrides übernehmen` schreibt Werte dauerhaft in `config.toml`, und `Automatikmodus` ändert den nächsten Start. Vorher `config.toml` sichern und vor einem Neustart wieder `Manueller Modus` senden.

### Probleme

- **TLS-Fehler auf der Messbox:** Das Zertifikat ist nicht installiert, oder die Adresse in der Konfiguration weicht von der aus `up` ab. `up` mit der richtigen Adresse wiederholen, das Zertifikat wird neu ausgestellt.
- **Es kommt nichts an:** Firewall auf dem Rechner, falsche IP oder getrennte Netze. Von einem anderen Rechner im Netz `curl --cacert lan-dev-root-ca.crt https://<host>:8443/api/health` testen.
- **`401` beim Heartbeat:** Geräte-ID oder Schlüssel falsch. `seed_dev_device.py` setzt sie auf die Werte aus der Tabelle zurück.
- **Neu anfangen:** `scripts/lan-dev.sh down -v`, dann wieder `up`.

# Konfiguration

Das Backend wird vollständig über Umgebungsvariablen konfiguriert. Sie stehen in einer Datei `.env` im Wurzelverzeichnis des Repositorys, die nicht eingecheckt wird. Vorlage ist `.env.example`. Für die lokale Entwicklung liegen unkritische Standardwerte in `.env.dev`, Werte in `.env` haben Vorrang.

## Pflichtwerte

| Variable | Bedeutung |
|---|---|
| `POSTGRES_PASSWORD` | Passwort des Datenbanknutzers im Postgres-Container |
| `DATABASE_URL` | Verbindung zur Datenbank, z. B. `postgresql+psycopg://app_user:<passwort>@postgres:5432/measurement_backend` |
| `SECRET_KEY` | signiert die Anmelde-Tokens; im Betrieb ein langer Zufallswert, sonst lassen sich Tokens fälschen |

## Optionale Werte

| Variable | Standard | Bedeutung |
|---|---|---|
| `SERVER_HOST` | `0.0.0.0` | Adresse, auf der die API lauscht |
| `SERVER_PORT` | `8000` | Port der API |
| `ENVIRONMENT` | `production` | Umgebung; einige Entwicklungsskripte verweigern den Start bei `production` |
| `ALGORITHM` | `HS256` | Signaturverfahren der Tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Gültigkeit einer Anmeldung in Minuten |
| `SELECTION_EXPORT_MAX_IDS` | `50000` | höchstens so viele Punkte pro Auswahl-Export auf der Karte |
| `NTFY_BASE_URL` | `https://ntfy.sh` | ntfy-Server für Push-Benachrichtigungen |
| `NTFY_ACCESS_TOKEN` | leer | Token für einen geschützten ntfy-Server; wird nie geloggt oder ausgegeben |

## Nur für den Produktivbetrieb

| Variable | Bedeutung |
|---|---|
| `SITE_DOMAIN` | Domain, für die Caddy das Zertifikat holt |
| `DOCS_DIR` | Verzeichnis auf dem Server, aus dem Caddy diese Dokumentation unter `/docs` ausliefert (Standard `./docs-site`) |

!!! warning "Push-Benachrichtigungen und Datenschutz"

    Benachrichtigungen enthalten Geräte-ID, Ereignis und Uhrzeit und gehen an den ntfy-Server. Auf dem öffentlichen `ntfy.sh` schützt nur das geheime Thema des Nutzers die Nachrichten. Für einen sensiblen Einsatz einen eigenen ntfy-Server mit Zugriffskontrolle betreiben und `NTFY_BASE_URL` sowie `NTFY_ACCESS_TOKEN` setzen.

Die Einstellungen, die Superuser in der Oberfläche ändern (Limit für Rohdatenpunkte, Herunterfahren bestätigen), liegen dagegen in der Datenbank, siehe [Einstellungen](../einstellungen.md#nur-fur-superuser).

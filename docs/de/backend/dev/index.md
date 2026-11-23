# Development

Dieser Abschnitt dreht sich um das Betreiben oder die Weiterentwicklung des Backend-Servers. Wie man die Oberfläche bedient, steht in den übrigen Seiten unter [Backend](../index.md).

## Aufbau

| Teil | Technik | Aufgabe |
|---|---|---|
| API | Python, `FastAPI`, `SQLAlchemy`, `Alembic` | nimmt Heartbeats, Messdaten und Latenzergebnisse der Messboxen an, liefert Fernbefehle und Konfigurationsänderungen aus, bedient die Oberfläche |
| Datenbank | `PostgreSQL` | Messdaten, Läufe, Kampagnen, Nutzer, Geräte, Befehle |
| Oberfläche | `React`, `Vite`, `TypeScript` | das Dashboard im Browser |
| Reverse Proxy | `Caddy` | HTTPS mit automatischem Zertifikat, leitet `/api` an die API und `/docs` an diese Dokumentation weiter |
| Latenz-Gegenstelle | `netserver`, `irtt` | Gegenstelle für die Latenztests der Messboxen, läuft außerhalb von Docker, siehe [Flent-Server](flent-server.md) |
| Push-Benachrichtigungen | `ntfy` | externer Dienst, siehe [Einstellungen](../einstellungen.md#push-benachrichtigungen) |

API, Datenbank, Oberfläche und Caddy laufen als Docker-Compose-Dienste. Der Code liegt im Repository [`tguttzeit/5G-Measurement-Backend`](https://github.com/tguttzeit/5G-Measurement-Backend).

## Kanäle zur Messbox

Die Messbox baut alle Verbindungen selbst auf, das Backend erreicht sie nie von sich aus.

- **Heartbeat** (`POST /api/heartbeat`): Statusmeldung in festem Abstand. Die Antwort enthält eingereihte Fernbefehle und Konfigurationsänderungen, signiert mit dem Schlüssel der Messbox.
- **Messdaten** (`POST /api/measurements`) und **Latenzergebnisse** (`POST /api/latency-results`): Uploads nach einem Lauf oder per `Upload erzwingen`.
- **Selbsttests** und **GPS-Fix-Test**: eigene Endpunkte für die Ergebnisse, siehe [Testvisualisierung](../testvisualisierung.md).

Alle Endpunkte stehen in der [API-Referenz](api/index.md).

## Seiten

- [Konfiguration](konfiguration.md): Umgebungsvariablen des Backends
- [Gerät registrieren](geraet-registrieren.md): eine neue Messbox anlegen
- [Deployment](deployment.md): Produktivbetrieb mit Docker Compose
- [Flent-Server](flent-server.md): Gegenstelle für die Latenztests
- [Lokal testen](lokal-testen.md): Entwicklungsumgebung, Tests, Test mit einer echten Messbox im LAN
- [API](api/index.md): Referenz aller Endpunkte, aus dem Code erzeugt

# Gerät registrieren

Messboxen melden sich nicht mit einem Nutzerkonto an, sondern mit einer Geräte-ID und einem eigenen Schlüssel. Jede neue Messbox muss deshalb einmal im Backend registriert werden. In der Oberfläche geht das nicht, nur auf dem Server.

## Registrieren

Auf dem Server, im Verzeichnis des Backends:

```bash
docker compose exec backend python scripts/register_device.py <device_id>
```

Der Ordner `scripts/` ist in den Container eingebunden, ein Aufruf auf dem Host ist nicht nötig.

Das Skript gibt zwei Werte aus:

| Wert | Wohin auf der Messbox | Zweck |
|---|---|---|
| `API Key` | `[backend] device_key` | Die Messbox weist sich damit bei jeder Anfrage aus (`X-Device-ID`, `X-Device-Key`). |
| `HMAC Secret` | `[heartbeat] hmac_secret` | Die Messbox prüft damit die Signatur der Heartbeat-Antworten. Ohne ihn verwirft sie alle Fernbefehle und Konfigurationsänderungen, siehe [Fernbefehle](../../messbox/nutzung/fernbefehle.md). |

!!! warning "Beide Werte werden nur einmal angezeigt"

    Das Backend speichert vom Schlüssel nur einen Hash. Die Werte sofort in die Konfiguration der Messbox übernehmen. Dieselbe ID lässt sich nicht ein zweites Mal registrieren, das Skript bricht dann mit `already exists` ab. Gehen die Werte verloren, lassen sie sich für dieselbe ID [erneuern](#schlussel-erneuern).

Die `device_id` muss auf der Messbox unter `[heartbeat] device_id` genau so stehen wie bei der Registrierung, siehe [Konfiguration der Messbox](../../messbox/nutzung/konfiguration.md#nur-an-der-messbox-einstellbar). Sonst weist das Backend Heartbeats und Uploads ab.

## Schlüssel erneuern

Ist ein Schlüssel verloren gegangen oder in falsche Hände geraten (z. B. Messbox weitergegeben, SD-Karte neu aufgesetzt), erzeugt dieses Skript für eine registrierte Messbox einen neuen API-Schlüssel und ein neues HMAC-Secret:

```bash
docker compose exec backend python scripts/rotate_device_credentials.py <device_id>
```

Wie bei der Registrierung werden beide Werte nur einmal angezeigt. Eine Übergangszeit gibt es nicht: Ab sofort weist das Backend den alten Schlüssel mit `401` ab, und die Messbox verwirft die Heartbeat-Antworten, weil sie mit dem neuen Secret signiert sind. Bis beide neuen Werte in ihrer `config.local.toml` stehen, ist die Messbox vom Backend abgeschnitten. Deshalb nur eine Messbox umstellen, die man per SSH erreicht, und zwar in dieser Reihenfolge:

1. Prüfen, dass die Anmeldung per SSH auf der Messbox klappt.
2. Das Skript ausführen und beide Werte kopieren.
3. Auf der Messbox `[backend] device_key` und `[heartbeat] hmac_secret` in der `config.local.toml` ersetzen und die Messsoftware neu starten (`sudo systemctl restart 5g-measurement.service`).
4. Im `Missionsstatus` prüfen, dass wieder Heartbeats ankommen.

Eingereihte Konfigurationsänderungen und Befehle bleiben erhalten. Sie gehen mit dem nächsten Heartbeat raus und sind dann mit dem neuen Secret signiert.

## Was eine Messbox mit ihrem Schlüssel darf

Der Geräteschlüssel öffnet nur die Endpunkte, über die eine Messbox liefert:

- `POST /api/heartbeat`: Heartbeat
- `POST /api/measurements`: Messdaten
- `POST /api/latency-results`: Latenzergebnisse
- `POST /api/testing/results`: Selbsttest-Ergebnisse
- `POST /api/devices/<device_id>/gps-fix-test/status`: Zwischenstände des GPS-Fix-Tests

Lesen, Löschen und alles andere ist Nutzerkonten vorbehalten.

## Erstes Nutzerkonto

Ein öffentliches Registrieren gibt es nicht. Den ersten Superuser legt man ebenfalls auf dem Server an:

```bash
docker compose exec backend python scripts/create_user.py <benutzername> <passwort> --superuser
```

Weitere Konten legt dieser Superuser danach in der Oberfläche unter `Benutzerverwaltung` an, siehe [Backend](../index.md#konten-verwalten).

# Lokal testen

Diese Seite beschreibt die Entwicklungsumgebung der Messsoftware, die automatischen Tests, wie man die Anwendung und den Selbsttest auf einer Messbox von Hand startet und wie man die Messbox zusammen mit dem Backend testet. Wie eine neue Messbox eingerichtet wird, steht unter [Messbox aufsetzen](messbox-aufsetzen.md).

## Entwicklungsumgebung

Voraussetzungen: [`uv`](https://docs.astral.sh/uv/) und Python ab 3.12. Abhängigkeiten im Wurzelverzeichnis des Repositorys installieren:

```bash
uv sync
```

Das installiert auch die Entwicklungswerkzeuge (`pytest`, `pytest-cov`, `ruff`). Ein lokaler Checkout sollte in der `config.toml` `[system] running_on_pi = false` setzen, dann startet die Software kein `quectel-CM` und fährt nichts herunter (siehe [Konfigurationsreferenz](konfiguration.md#system)).

## Tests und Lint

```bash
uv run pytest                                                        # alle Tests
uv run pytest --cov=measurement_software --cov-report=term-missing   # mit Testabdeckung
uv run ruff check .                                                  # Lint
```

Die Tests brauchen keine Hardware: Modem, GNSS-Empfänger, Display, serielle Schnittstellen, HTTP und Uhrzeit werden durch Fakes ersetzt. Wie das aufgebaut ist, steht unter [Testmuster](architektur.md#testmuster).

## Anwendung von Hand starten

Ein vollständiger Lauf braucht Modem und GNSS-Empfänger und wird deshalb auf einer Messbox gestartet. Vorher den Dienst stoppen, damit nicht zwei Instanzen gleichzeitig auf die Hardware zugreifen:

```bash
sudo systemctl stop 5g-measurement.service
uv run python -m measurement_software.main
```

Einen Einstiegspunkt unter `[project.scripts]` gibt es nicht, die Anwendung wird immer als Modul gestartet. Ein Aufruf durchläuft genau einen Lauf:

1. Daten eines unterbrochenen früheren Laufs sichern.
2. `quectel-CM` und den Heartbeat starten.
3. Auf GPS-Fix und bestätigte Bewegung warten (Automatikmodus) bzw. auf einen Fernbefehl und dann auf den GPS-Fix (manueller Modus).
4. Messen, bis der Lauf endet (Stillstand im Automatikmodus oder `stop-measuring-now`).
5. Abschließen und hochladen.
6. Bei `[system] running_on_pi = true` den Pi herunterfahren.

Den genauen Ablauf beschreibt [Architektur](architektur.md#ablauf-eines-laufs).

## Selbsttest

Um die Verkabelung einer Messbox per SSH zu prüfen, ohne einen ganzen Lauf zu starten, gibt es den Selbsttest. Er liest die `config.toml` genauso wie die Anwendung und braucht keine eigene Konfiguration:

```bash
uv run python -m measurement_software.selftest                  # alle Prüfungen
uv run python -m measurement_software.selftest modem gps        # nur einzelne
uv run python -m measurement_software.selftest --help           # Übersicht
```

| Prüfung | Was sie tut |
|---|---|
| `modem` | öffnet das Modem und fragt einmal die Zellwerte ab |
| `gps` | öffnet den GNSS-Empfänger und wartet auf einen Fix |
| `collector` | prüft, ob Zellwerte und Fix zu einem Messpunkt zusammenpassen, ohne ihn zu speichern |
| `uploader` | prüft, ob `wlan0` oder `wwan0` eine IPv4-Adresse hat |
| `heartbeat` | schickt einen echten Heartbeat ans Backend |
| `keep_modem_alive` | startet kurz den UDP-Sender, der die Verbindung offen hält |
| `display` | zeigt eine Testmeldung auf dem Display |
| `latency_tester` | prüft, ob `flent` läuft und ein Testserver eingestellt ist, ohne einen Test zu starten |

Keine Prüfung lädt Messdaten hoch oder fährt das Gerät herunter. Ob das Backend erreichbar ist und die Zugangsdaten stimmen, prüft `heartbeat`, der mit demselben Schlüssel an dasselbe Backend geht wie der Uploader.

Ist `[selftest] results_url` gesetzt, landen die Ergebnisse von `modem`, `gps`, `collector`, `uploader` und `heartbeat` zusätzlich in der [Testvisualisierung](../../backend/testvisualisierung.md) des Backends. Welche Ergebnisse beim ersten Mal wie Fehler aussehen, aber keine sind, steht unter [Messbox aufsetzen](messbox-aufsetzen.md#verkabelung-vor-dem-ersten-lauf-prufen).

## Zusammen mit dem Backend testen

Eigene Integrationstests hat die Messsoftware nicht. Das Zusammenspiel mit dem Backend (Heartbeat, Uploads, Fernbefehle, Selbsttest-Ergebnisse) prüft man, indem man eine echte Messbox gegen ein Backend im lokalen Netz laufen lässt. Aufbau des Test-Backends, die Testzugangsdaten, die `config.local.toml` für die Messbox, das Zertifikat und die Stolperfallen auf der Messbox (`debug_upload`, `running_on_pi`, `Overrides übernehmen`) stehen unter [Mit einer echten Messbox im lokalen Netz](../../backend/dev/lokal-testen.md#mit-einer-echten-messbox-im-lokalen-netz).

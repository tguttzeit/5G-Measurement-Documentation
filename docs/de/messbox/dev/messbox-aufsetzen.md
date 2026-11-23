# Messbox aufsetzen

Diese Seite sammelt, was beim ersten Einrichten einer neuen Messbox per SSH ohne Bildschirm zu tun ist und woran man dabei hängen bleiben kann.

## Fehlende Werkzeuge

Ein frisches Pi-Image bringt `uv` nicht mit. Es lässt sich ohne Neustart installieren:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

Danach im Repository zuerst `uv sync` ausführen.

## Gerätespezifische Werte

Einige Felder der eingecheckten `config.toml` sind absichtlich offensichtliche Platzhalter (`"https://add.your.backend.here"`, `"/add/your/quectel-CM/path/here"`). Ein frischer Checkout soll nie aus Versehen mit einem echten Backend sprechen oder ein Programm starten, das es nicht gibt. Diese Werte gehören zur Identität der einzelnen Messbox und nicht in die `config.toml`, sondern in die `config.local.toml` (siehe unten).

| Feld | Woher | Hinweis |
|---|---|---|
| `[backend] url` | Adresse des Backends | |
| `[backend] device_key`, `[heartbeat] hmac_secret`, `[heartbeat] device_id` | werden im Backend angelegt, siehe [Gerät registrieren](../../backend/dev/geraet-registrieren.md) | Solange sie fehlen, erreichen Heartbeat und Uploader das Backend, bekommen aber `401 Unauthorized`. Das ist erwartet und kein Verkabelungsfehler. |
| `[device] device_id` | gleicher Wert wie `[heartbeat] device_id` | siehe Warnung unten |
| `[quectel_cm] binary` | Pfad nach dem Bauen, siehe [`quectel-CM` bauen](#quectel-cm-bauen) | |
| `[uploader] upload_dir` | absoluter Pfad der Upload-Warteschlange auf dieser Messbox | Die `config.toml` enthält nur den relativen Platzhalter `"upload_queue"`. Ohne eigenen Wert landen Messdaten unter dem Checkout. |
| `[selftest] results_url`, `[gps_fix_test] status_url`, `[latency_test] host` | Adressen von Backend und Latenztest-Server | Bleiben leer und damit wirkungslos, bis sie gesetzt sind. `[heartbeat] enabled` und `[latency_test] enabled` sind dagegen gewöhnliche Standardwerte und bleiben in der `config.toml`. |
| `[clock] ntp_server` | erreichbarer NTP-Server | Optional. Stellt die Uhr, sobald die Mobilfunkverbindung steht, auch ohne GPS-Fix. Leer: Die Uhr wird nur aus der GNSS-Zeit gestellt. |

!!! warning "`[device] device_id` muss gleich `[heartbeat] device_id` sein"

    Die beiden Felder sind getrennt, weil `[heartbeat] device_id` die Messbox beim Backend anmeldet, während `[device] device_id` in jeden Messpunkt geschrieben wird. Bleibt `[device] device_id` leer, nimmt die Software den Hostnamen des Pi. Das Backend weist den Upload dann mit `403: Datapoint device_id <hostname> does not match authenticated device <heartbeat device_id>` ab, weil die Daten von einem anderen Gerät zu stammen scheinen als dem angemeldeten.

### `config.local.toml`

Gerätespezifische Werte von Hand in die `config.toml` zu schreiben, hinterlässt eine dauerhaft geänderte Datei, die sich nicht committen lässt und neue Standardwerte beim `git pull` blockiert. Stattdessen neben der `config.toml` eine `config.local.toml` anlegen. Sie ist in `.gitignore` eingetragen und wird beim Start über die `config.toml` gelegt:

```toml
[backend]
url = "https://backend.example.org"
device_key = "<API-Schlüssel der Messbox>"

[heartbeat]
device_id = "<Geräte-ID>"
hmac_secret = "<Signaturschlüssel>"

[device]
# Muss mit [heartbeat] device_id übereinstimmen
device_id = "<Geräte-ID>"

[quectel_cm]
binary = "<Installationsverzeichnis>/vendor/quectel-CM/quectel-CM"

[uploader]
# Absoluter Pfad der Upload-Warteschlange auf dieser Messbox
upload_dir = "/pfad/zu/upload_queue"

[selftest]
results_url = "https://backend.example.org/api/testing/results"

[gps_fix_test]
# Der Pfad enthält die eigene Geräte-ID, von Hand einsetzen
status_url = "https://backend.example.org/api/devices/<Geräte-ID>/gps-fix-test/status"

[latency_test]
host = "latenztest.example.org"

[clock]
ntp_server = "ntp.example.org"
```

Nur diese Felder und Abschnitte werden aus der `config.local.toml` gelesen, alles andere wird geloggt und ignoriert. Die Datei enthält Zugangsdaten im Klartext, deshalb nur für den Nutzer lesbar machen, unter dem die Software läuft:

```bash
chmod 600 config.local.toml
```

Auf einer echten Messbox (`[system] running_on_pi = true`) warnt die Software beim Start für jedes dieser Felder, das noch fehlt oder auf dem Platzhalter steht. Es ist eine Warnung und kein Abbruch, weil die Felder im Betrieb ohnehin glimpflich ausfallen (fehlgeschlagene Uploads, `401`, verworfene Fernbefehle).

!!! info "Ältere Messboxen mit `--skip-worktree`"

    Die `config.local.toml` ersetzt den früheren Weg `git update-index --skip-worktree config.toml`. Der versteckte die Änderungen an der `config.toml`, übernahm aber auch keine neuen Standardwerte mehr. Auf einer so eingerichteten Messbox einmal `git update-index --no-skip-worktree config.toml` ausführen, die eigenen Werte in eine neue `config.local.toml` übertragen und die `config.toml` auf den Stand des Repositorys zurücksetzen.

## `quectel-CM` bauen

`vendor/quectel-CM` liegt als Quellcode bei, nicht als fertiges Programm:

```bash
cd vendor/quectel-CM && make release
```

Dafür reichen `gcc`, `make` und `pkg-config`, die auf einem Standard-Pi-OS-Image vorhanden sind. `autoconf` und `automake` braucht das einfache `Makefile` nicht. `[quectel_cm] binary` auf das erzeugte `vendor/quectel-CM/quectel-CM` zeigen lassen.

## APN im MBIM-Modus

Meldet das Log von `quectel-CM` `Modem works in MBIM mode` bzw. `must specify APN with '-s'`, bringt es `wwan0` ohne `-s <APN>` nie hoch. Den APN nicht raten oder in Listen nachschlagen, der Netzbetreiber der SIM hat ihn dem Modem schon mitgeteilt. Über die AT-Schnittstelle abfragen:

```text
AT+COPS?       # aktueller Netzbetreiber, z. B. +COPS: 1,0,"vodafone.de",13
AT+CGDCONT?    # im Modem hinterlegte PDP-Kontexte, der APN von Kontext 1 ist der richtige
```

Den APN dann über `[quectel_cm] args` übergeben, z. B. `args = ["-s", "web.vodafone.de"]`.

## Autostart einrichten

`systemd/5g-measurement.service` startet die Anwendung beim Booten. Die Unit startet `quectel-CM` nicht selbst und hängt auch nicht davon ab: Das übernimmt die Anwendung gleich beim Start, damit die Messbox während des ganzen Laufs über Mobilfunk erreichbar ist und nicht erst ab Messbeginn. Bei SIGTERM beendet sie `quectel-CM` auch wieder.

Die Unit setzt `KillMode=mixed`: Bei `systemctl stop` oder beim Herunterfahren des Systems bekommt nur die Anwendung SIGTERM. So gehen ihr letzter Heartbeat und der Upload noch über Mobilfunk raus, danach beendet sie `quectel-CM` selbst.

Die Unit-Datei enthält den Platzhalter `@INSTALL_DIR@`. Im Checkout ausführen, dann wird er durch das aktuelle Verzeichnis ersetzt:

```bash
sed "s|@INSTALL_DIR@|$PWD|g" systemd/5g-measurement.service \
  | sudo tee /etc/systemd/system/5g-measurement.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable 5g-measurement.service
```

Diese Befehle erneut ausführen, wenn sich `systemd/5g-measurement.service` im Software-Repository geändert hat. Bis dahin arbeitet systemd mit der zuvor installierten Unit weiter.

## Latenztests vorbereiten

Für die optionalen Latenztests (`[latency_test]`) `flent` und die Werkzeuge, die es aufruft, auf der Messbox installieren:

```bash
sudo apt install flent netperf python3-numpy
```

Die Tests brauchen außerdem eine Gegenstelle auf dem Testserver, siehe [Flent-Server](../../backend/dev/flent-server.md). `[latency_test] host` erst setzen, wenn die Messbox diese Gegenstelle erreicht. Ohne `host` laufen keine Tests, eine nicht eingerichtete Messbox erzeugt also nie Testverkehr.

## OLED-Display anschließen

Das SSD1306-Display hängt am I2C-Bus. SDA und SCL liegen fest auf GPIO2 und GPIO3, den Hardware-I2C-Pins des Pi, und sind nicht einstellbar. Am Display der bisherigen Messbox liegen die vier Pins von links nach rechts so:

| Display-Pin | Kabelfarbe | Pi, physischer Pin | Pi, GPIO |
|---|---|---|---|
| GND | weiß | 6 | Masse |
| VCC | violett | 1 | 3,3 V |
| SCL | blau | 5 | GPIO3 (SCL) |
| SDA | grün | 3 | GPIO2 (SDA) |

Das passt zu `[display] i2c_port = 1` und `i2c_address = 0x3C` in der `config.toml`.

!!! warning "Belegung am Display prüfen"

    Pin-Reihenfolge und Kabelfarben gelten nur für den Kabelsatz dieser Messbox und sind kein Standard. Bei einer anderen Messbox die Beschriftung am Display prüfen, statt die Tabelle zu übernehmen.

## Verkabelung vor dem ersten Lauf prüfen

Der Selbsttest prüft jedes Teilsystem einzeln und meldet bestanden, fehlgeschlagen oder übersprungen. Das geht deutlich schneller, als `main.py` für einen einzigen fehlerhaften Punkt immer wieder komplett laufen zu lassen:

```bash
uv run python -m measurement_software.selftest                  # alle Prüfungen
uv run python -m measurement_software.selftest modem uploader   # nur einzelne
```

Ist `[selftest] results_url` gesetzt, landen die Ergebnisse zusätzlich in der [Testvisualisierung](../../backend/testvisualisierung.md) des Backends.

Einige Ergebnisse sehen beim ersten Mal wie Fehler aus, sind aber keine:

- **`uploader` schlägt fehl, obwohl Internet da ist:** Die Prüfung lädt nichts hoch, sie prüft nur, ob eine Schnittstelle bereitsteht. Wie der echte Uploader zählt sie nur `wlan0` und `wwan0`. Eine Verbindung über `eth0`, etwa die SSH-Sitzung, reicht nicht. Die Meldung `No network interface (wlan0/wwan0) has an IPv4 address` ist dann korrekt.
- **`gps` oder `collector` schlägt fehl:** Es ist kein GNSS-Empfänger an `/dev/serial0` angeschlossen. Die Prüfung tut, was sie soll.
- **`modem` besteht mit null Zellwerten:** Das Funkmodul ist noch in keinem Netz eingebucht, z. B. weil `quectel-CM` nicht läuft und keine Datenverbindung besteht. Vor der Fehlersuche in der Software die Verbindung prüfen, über die AT-Schnittstelle mit `AT+QENG="servingcell"` oder mit `ip addr show wwan0`.

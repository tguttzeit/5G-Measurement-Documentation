# Konfigurationsreferenz

Diese Seite beschreibt alle Felder der `config.toml` der Messsoftware. Welche Einstellungen im Feld wichtig sind und wie man sie im Backend ändert, steht unter [Konfiguration](../nutzung/konfiguration.md) in der Nutzungsdoku.

Die `config.toml` liegt im Wurzelverzeichnis des Repositorys. Sie wird über einen Pfad relativ zum installierten Paket gefunden, nicht relativ zum Arbeitsverzeichnis, und von `core/config.py::load_config()` geladen. Fehlt ein mit **Pflicht** markierter Abschnitt, bricht der Start mit `KeyError` ab. Alle anderen Abschnitte und Felder fallen auf die Standardwerte unten zurück.

## Reihenfolge der Quellen

Spätere Quellen gewinnen:

1. Standardwerte der Dataclasses
2. `config.toml`
3. `config.local.toml`: gerätespezifische Identität und Zugangsdaten, einmal beim Einrichten von Hand gesetzt, siehe [Messbox aufsetzen](messbox-aufsetzen.md#geratespezifische-werte)
4. `config_overrides.toml`: Änderungen, die das Backend aus der Ferne schickt

Ein Feld kann nur in einer der letzten beiden Dateien stehen: Identitäts- und Zugangsfelder sind von der Fernkonfiguration ausgenommen. Das wird beim Import in `core/config_sources.py` geprüft.

Ein Wert, der sich in der `config_overrides.toml` bewährt hat, lässt sich mit `python -m measurement_software.promote_overrides` oder dem Fernbefehl `promote-overrides-now` zur neuen Grundlage machen. Jedes gesetzte Feld wird über die Zuordnung `OVERRIDE_FIELD_TARGETS` in `core/config_sources.py` an seine Stelle in der `config.toml` geschrieben (mit `tomlkit`, Kommentare bleiben erhalten) und aus der `config_overrides.toml` entfernt. Wie jede Änderung an der `config_overrides.toml` wirkt das erst beim nächsten `load_config()`, also beim nächsten Booten.

## Fernkonfiguration (`config_overrides.toml`)

`FIELD_SPECS` in `core/config_sources.py` ist die erlaubte Liste: Ein Feld lässt sich genau dann aus der Ferne setzen, wenn es dort mit Typ und Wertebereich steht. Andere Felder und Werte mit falschem Typ oder außerhalb des Bereichs werden mit einer Log-Zeile verworfen, der Rest der Änderungen wird trotzdem übernommen. Die Typen sind streng: `bool`-Felder nehmen nur `true`/`false`, `int`-Felder keine Nachkommastellen, Gleitkommafelder kein `NaN`/`inf`, Auswahlfelder nur exakt passende Zeichenketten.

| Gruppe | Felder |
|---|---|
| Zeiten und Auslöser | `idle_threshold_s` (`0` = nie wegen Stillstand beenden), `day_end_threshold_s` (wird angenommen, hat auf der Messbox noch keine Wirkung), `heartbeat_interval_s`, `collector_*` (`capture_gate` `distance`/`time`, `position_threshold`, `capture_interval_s`, `max_wait_for_first_fix`, `wait_log_interval`, `gps_enabled`, `gps_disabled_poll_interval_s`), `movement_gate_*` (`enabled`, `poll_interval_s`, `movement_threshold`, `confirmations_required`, `home_latitude`/`home_longitude`, `home_departure_threshold`), `latency_test_*` (`enabled`, drei Intervalle), `run_status_empty_captures_until_pipeline_broken` |
| Gerät | `system_mode` (`auto`/`manual`), `device_mission_type` (`ground`/`drone`), `display_enabled`, `display_refresh_interval_s` |
| Modem, GNSS, System | `modem_mode` (`serving_cell`/`sa_scan`), `modem_sim_unlock_poll_attempts`, `modem_sim_unlock_poll_interval`, `gnss_receiver_retries`, `gnss_receiver_retry_delay_s`, `system_running_on_pi` |

Die Heimatposition darf leer sein: Ein JSON-`null` setzt sie zurück. In der Datei steht das als Liste `cleared = ["movement_gate_home_latitude", ...]`, die nur Felder annimmt, die leer sein dürfen.

`system_mode` ist der Gerätemodus. Die Befehle `mode-manual-now` und `mode-auto-now` schreiben ihn hierher (`mode-waiting-now`, der frühere Name, wirkt wie `mode-manual-now`). Das Backend reiht ihn nicht als Konfigurationsänderung ein, weil eingereihte Änderungen mit jedem Heartbeat neu geschickt werden und diese Befehle einen Heartbeat später wieder aufheben würden. `stop-measuring-now` ändert `system_mode` nicht, sondern legt nur eine Markierung für einen einmaligen Start im manuellen Modus an (siehe [Architektur](architektur.md#ablauf-eines-laufs)). Eine `mode_override.toml` aus einer älteren Version wird beim Start einmal in `system_mode` übernommen (ein ungültiger Wert wird verworfen, ein vorhandenes `system_mode` hat Vorrang) und danach gelöscht. Ein gespeichertes `system_mode = "waiting"` wird beim Start einmal in `"manual"` umgeschrieben.

Eine fehlerhafte Änderung verhindert nie den Start. Die Prüfungen für Heimatposition und Modus aus der [Startprüfung](#startprufung) laufen nach dem Anwenden der Änderungen erneut. Verletzt eine Änderung eine davon, werden die beteiligten Felder verworfen und geloggt, und der Wert aus der `config.toml` bleibt. Eine beschädigte `config_overrides.toml` oder ein darin nicht mehr gültiges Feld wird ebenso ignoriert.

Eine Heartbeat-Antwort mit Änderungen oder Befehlen wird nur angenommen, wenn ihr signierter Text die zufällige `nonce` der zugehörigen Anfrage enthält. Eine mitgeschnittene Antwort lässt sich damit nicht später erneut einspielen, und die Messbox braucht dafür weder Uhrzeit noch gespeicherten Zähler.

## `[modem]` (Pflicht)

Serielle Verbindung und Abfragemodus des Mobilfunkmodems.

| Feld | Standard | Bedeutung |
|---|---|---|
| `type` | — | wählt die `Modem`-Implementierung über die Factory in `modems/__init__.py`. Registriert ist bisher nur `"quectel"`. |
| `port` | leer | Gerätepfad der AT-Schnittstelle, z. B. `/dev/ttyUSB2`. Leer: wird bei jedem Öffnen über `/dev/serial/by-id/usb-Quectel_*-if02-port0` gesucht. Dieser Pfad bleibt gültig, wenn das Modem sich am USB neu anmeldet und die Nummer von `/dev/ttyUSBn` wechselt. Das Öffnen schlägt fehl, wenn es keinen oder mehr als einen passenden Port gibt. |
| `baud_rate` | — | Baudrate |
| `timeout` | — | Lese-Timeout in Sekunden |
| `mode` | `"serving_cell"` | `"serving_cell"` (`AT+QENG`) oder `"sa_scan"` (`AT+QSCAN`, nur NR5G-SA; Band und Modus müssen vorher von Hand über die AT-Konsole gesetzt werden, siehe Kommentar in der `config.toml`) |
| `retries` | `3` | Wiederholungen einer fehlgeschlagenen AT-Abfrage |
| `retry_delay_s` | `0.75` | Pause zwischen den Wiederholungen |
| `sim_pin_env_var` | `"MODEM_SIM_PIN"` | Name der Umgebungsvariable mit der SIM-PIN, die beim Entsperren gelesen wird. Die PIN selbst steht nie in einer Konfigurationsdatei. |
| `sim_unlock_poll_attempts` | `10` | wie oft nach dem Entsperren der Sperrstatus der SIM abgefragt wird |
| `sim_unlock_poll_interval` | `1.0` | Pause zwischen diesen Abfragen in Sekunden |

## `[gnss_receiver]` (Pflicht)

Serielle Verbindung des GNSS-Empfängers.

| Feld | Standard | Bedeutung |
|---|---|---|
| `type` | — | wählt die `GNSSReceiver`-Implementierung über `gnss/__init__.py`. Registriert ist bisher nur `"nmea_serial"`. |
| `port` | — | Gerätepfad, z. B. `/dev/serial0` |
| `baud_rate` | — | Baudrate |
| `timeout` | — | Lese-Timeout in Sekunden |
| `retries` | `3` | Wiederholungen eines fehlgeschlagenen Lesevorgangs |
| `retry_delay_s` | `0.75` | Pause zwischen den Wiederholungen |

## `[device]`

Kennzeichnet Messbox und Einsatzart. Beides steht in jedem Messpunkt, am Verhalten der Messbox ändert die Einsatzart nichts.

| Feld | Standard | Bedeutung |
|---|---|---|
| `device_id` | Hostname des Pi | Kennung der Messbox in jedem Messpunkt. Muss mit `[heartbeat] device_id` übereinstimmen, siehe [Messbox aufsetzen](messbox-aufsetzen.md#geratespezifische-werte). |
| `mission_type` | `"ground"` | `"ground"` oder `"drone"`. Nur eine Kennzeichnung der Daten. Frühere `[profiles.*]`-Tabellen je Einsatzart gibt es nicht mehr. Steht noch eine in der `config.toml`, wird sie mit einer Warnung ignoriert. |

## `[collector]`

Wann ein Messpunkt aufgenommen wird und wann ein Lauf endet.

| Feld | Standard | Bedeutung |
|---|---|---|
| `position_threshold` | `15` | Mindestabstand in Metern (Haversine) zur letzten Messposition, bevor der nächste Messpunkt aufgenommen wird |
| `max_idle_time` | `1800` | Sekunden ohne echte Bewegung, nach denen der Lauf endet. Wirkt nur im Automatikmodus. `0` schaltet das ab: Der Lauf endet dann, wie im manuellen Modus immer, nur per `stop-measuring-now`, `shutdown-now`/`reboot-now` oder Stromausfall, und das Log wächst bis dahin (vor einer vollen Speicherkarte warnt nur `[storage] low_free_space_warning_bytes`). |
| `max_wait_for_first_fix` | `300` | Sekunden, die im Automatikmodus auf den ersten GPS-Fix gewartet wird, bevor der Durchlauf ohne Lauf endet. Im manuellen Modus wartet die Messbox nach `start-measuring-now` ohne Zeitgrenze. |
| `wait_log_interval` | `5` | wie oft (Sekunden) „warte noch auf Fix“ geloggt wird |
| `keep_alive_host` | `"8.8.8.8"` | Ziel der UDP-Pakete, die die Mobilfunkverbindung während der Messung offen halten |
| `keep_alive_port` | `53` | Port dieser Pakete |
| `keep_alive_interval_s` | `4.0` | Abstand zwischen diesen Paketen |
| `gps_enabled` | `true` | `false`: misst ohne echten GPS-Fix (Platzhalter-Positionen), zum Testen ohne GNSS-Hardware |
| `gps_disabled_poll_interval_s` | `5.0` | Abfrageintervall bei `gps_enabled = false` |
| `capture_gate` | `"distance"` | Aufnahmeregel: `"distance"` (nach `position_threshold`) oder `"time"` (fester Abstand `capture_interval_s`). Das Ende bei Stillstand richtet sich immer nach der Strecke, die Regel ändert also nie, wann ein Lauf endet. |
| `capture_interval_s` | `15.0` | Sekunden zwischen Messpunkten bei `capture_gate = "time"`, sonst ohne Wirkung |
| `modem_reconnect_attempts` | `10` | Geht die Verbindung zum Modem während der Messung verloren (Port weg, Ein-/Ausgabefehler), wird der Messpunkt übersprungen und das Modem bis zu so oft neu geöffnet, bevor der Fehler den Lauf beendet. Mindestens `1`. |
| `modem_reconnect_delay_s` | `3.0` | Pause vor jedem neuen Öffnen, damit sich ein vom USB gefallenes Modem neu anmelden kann (im Feld etwa 10 s) |

## `[movement_gate]`

Warten auf bestätigte Bewegung, bevor die Messung beginnt. Läuft nur mit GNSS und selten, Modem und `quectel-CM` fasst es nicht an. Beide laufen zu diesem Zeitpunkt schon für den Heartbeat.

| Feld | Standard | Bedeutung |
|---|---|---|
| `enabled` | `true` | `false`: kein Warten, die Messung beginnt sofort (z. B. bei Drohnen, die am Boden stehen oder schweben). `quectel-CM` und Heartbeat starten trotzdem beim Booten. |
| `poll_interval_s` | `45.0` | Abfrageintervall des GNSS beim Warten |
| `movement_threshold` | `10.0` | Mindestabstand in Metern zur Position des ersten Fixes, der als Bewegung zählt |
| `confirmations_required` | `2` | Zahl aufeinanderfolgender Abfragen mit Bewegung, bis ein Lauf als gestartet gilt |
| `home_latitude` / `home_longitude` | leer | optionale Heimatposition (z. B. Garage). Beide oder keines setzen, wird beim Start geprüft. Gesetzt: Zusätzlich zur Bewegung muss die Messbox die Heimatposition verlassen haben. |
| `home_departure_threshold` | `100.0` | Abstand in Metern zur Heimatposition, ab dem sie als verlassen gilt |

## `[quectel_cm]`

Der Verbindungsmanager `quectel-CM`, den die Software selbst beim Booten startet (über `sudo`), nicht `systemd`. Die Überwachung der Mobilfunkverbindung startet ihn neu, wenn die Verbindung nicht zurückkommt (siehe [`[link_watchdog]`](#link_watchdog)).

| Feld | Standard | Bedeutung |
|---|---|---|
| `binary` | Platzhalter | Pfad zum gebauten `quectel-CM`. Gerätespezifisch, in der `config.local.toml` setzen. Der Platzhalter ist absichtlich nie ein echter Pfad. |
| `args` | `()` | zusätzliche Argumente, z. B. `["-s", "web.vodafone.de"]` für den APN |

## `[run_status]`

Was der Heartbeat über die Qualität des Laufs meldet. Ein Messpunkt gilt als „gültig“, wenn RSRP, RSRQ und SINR alle in dem Bereich liegen, den der Funkstandard für die jeweilige Funktechnik zulässt, sonst als „ungültig“ (fehlende, Platzhalter- oder unsinnige Werte). Wie gut ein gültiges Signal ist, wird erst bei der Auswertung bewertet, nicht auf der Messbox.

| Feld | Standard | Bedeutung |
|---|---|---|
| `empty_captures_until_pipeline_broken` | `3` | Zahl leerer Messpunkte in Folge während der Bewegung, ab der der Heartbeat die Messkette als gestört meldet |

## `[backend]`

Gemeinsames HTTPS-Ziel und Anmeldung für alles, was die Messbox ans Backend schickt (Heartbeat und Uploads). `url` muss `https` sein: Die Messbox baut jede Verbindung selbst auf, und die Antwort des Backends ist der Weg, auf dem Anweisungen zur Messbox kommen. Dieser Weg muss vertrauenswürdig sein. `[heartbeat]` und `[uploader]` hängen ihren eigenen Pfad an diese `url`, statt einen eigenen Host einzustellen.

| Feld | Standard | Bedeutung |
|---|---|---|
| `url` | `""` | Basisadresse des Backends. Gerätespezifisch, in der `config.local.toml` setzen. |
| `device_key` | `""` | API-Schlüssel der Messbox. Gerätespezifisch und geheim, in der `config.local.toml` setzen. |

## `[heartbeat]`

Regelmäßige Meldung ans Backend, wie der Lauf gerade steht. Die Antwort kann signierte Konfigurationsänderungen und einmalige Fernbefehle enthalten.

| Feld | Standard | Bedeutung |
|---|---|---|
| `enabled` | `true` | schaltet den Heartbeat ein |
| `path` | `"/api/heartbeat"` | Pfad, der an `[backend] url` angehängt wird |
| `interval_s` | `15.0` | Sekunden zwischen zwei Heartbeats |
| `timeout_s` | `10.0` | HTTP-Timeout eines Heartbeats |
| `device_id` | `""` | Kennung, mit der sich die Messbox beim Backend anmeldet, getrennt von `[device] device_id`. Gerätespezifisch, in der `config.local.toml` setzen. |
| `hmac_secret` | `""` | prüft, dass Konfigurationsänderungen und Befehle in der Antwort wirklich vom Backend kommen. Leer: Fernbefehle sind abgeschaltet, eine Antwort mit Befehlen wird verworfen und geloggt. Gerätespezifisch und geheim, in der `config.local.toml` setzen. |
| `success_log_interval_s` | `600.0` | Zugestellte Heartbeats werden mit INFO geloggt: der erste, der erste nach Fehlern und sonst eine Zusammenfassung pro so vielen Sekunden. |

## `[selftest]`

Ziel im Backend für die Ergebnisse von `python -m measurement_software.selftest`. Angemeldet wird mit `[backend] device_key` und `[heartbeat] device_id`, eigene Zugangsdaten gibt es nicht.

| Feld | Standard | Bedeutung |
|---|---|---|
| `results_url` | `""` | Adresse für die Ergebnisse. Leer: Die Prüfungen laufen nur lokal mit Ausgabe auf der Konsole. Gerätespezifisch (enthält den echten Backend-Host), in der `config.local.toml` setzen. |

## `[gps_fix_test]`

Live-Test der GPS-Fix-Suche (`run-gps-fix-test-now` / `stop-gps-fix-test-now`), um eine gute Position für die Antenne zu finden. Wird nur im Leerlauf des manuellen Modus (`MANUAL_MODE_IDLE`) ausgeführt, sonst mit `not_applicable` beantwortet (siehe `[system] mode`).

| Feld | Standard | Bedeutung |
|---|---|---|
| `status_url` | `""` | Adresse, an die etwa alle `report_interval_s` `num_satellites`, `has_fix` und `elapsed_s` geschickt werden. Gerätespezifisch, in der `config.local.toml` setzen. |
| `report_interval_s` | `2.0` | Abstand der Statusmeldungen während des Tests |
| `timeout_s` | `300.0` | beendet den Test von selbst, falls `stop-gps-fix-test-now` nie kommt |

## `[storage]`

Sicherheitsnetz für den lokalen Upload-Rückstau. Keine Obergrenze und kein Löschen, nur eine deutliche Warnung, wenn der Speicherplatz knapp wird, falls eine Verbindungslücke viel länger dauert als erwartet.

| Feld | Standard | Bedeutung |
|---|---|---|
| `low_free_space_warning_bytes` | `500_000_000` | freier Speicher auf dem Dateisystem von `[uploader] upload_dir`, unter dem gewarnt wird |

## `[display]`

Kleines SSD1306-OLED-Display über I2C für die Diagnose im Feld ohne Terminal. Standardmäßig an: Mit `enabled = false` läuft ein Leer-Display, die Software funktioniert ohne Bildschirm unverändert. Auf einer Messbox ohne Display deshalb `enabled = false` setzen.

| Feld | Standard | Bedeutung |
|---|---|---|
| `enabled` | `true` | schaltet das Display ein |
| `type` | `"ssd1306"` | wählt die `Display`-Implementierung über `displays/__init__.py`. Registriert ist bisher nur `"ssd1306"`. |
| `i2c_port` | `1` | Nummer des I2C-Busses |
| `i2c_address` | `0x3C` | I2C-Adresse des Displays |
| `refresh_interval_s` | `2.0` | Aktualisierungsintervall der Anzeige |

## `[latency_test]`

Aktive Latenzmessungen mit `flent` gegen einen Testserver, solange sich das Fahrzeug bewegt. Standardmäßig eingeschaltet, aber ohne `host` wirkungslos: Die Tests brauchen eine Gegenstelle auf dem Server (`netperf` für den Lasttest, ein Host, der auf Ping antwortet, für die Grundmessung), die außerhalb dieses Repositorys liegt. Eine nicht eingerichtete Messbox soll nie von sich aus Testverkehr erzeugen, deshalb `host` erst setzen, wenn die Gegenstelle erreichbar ist. Die Gegenstelle beschreibt [Flent-Server](../../backend/dev/flent-server.md).

| Feld | Standard | Bedeutung |
|---|---|---|
| `enabled` | `true` | schaltet die Latenztests ein |
| `host` | `""` | Hostname des Testservers. Leer: keine Tests. Gerätespezifisch, in der `config.local.toml` setzen. |
| `flent_binary` | `"flent"` | Name oder Pfad von `flent` |
| `baseline_test` | `"ping"` | `flent`-Test für die günstige Grundmessung (Latenz der unbelasteten Verbindung) |
| `baseline_interval_s` | `60.0` | Abstand der Grundmessungen |
| `baseline_length_s` | `10` | Dauer einer Grundmessung |
| `load_test` | `"rrul"` | `flent`-Test unter Last. Lastet die Verbindung für seine ganze Dauer voll aus und läuft deshalb viel seltener als die Grundmessung. |
| `load_interval_s` | `900.0` | Abstand der Lasttests |
| `load_length_s` | `60` | Dauer eines Lasttests |
| `poll_interval_s` | `30.0` | wie oft der Tester prüft, ob einer der Tests fällig ist |
| `movement_window_s` | `30.0` | Wie kurz die letzte Bewegung (Messpunkte nach `[collector] position_threshold`) her sein muss, damit ein fälliger Test läuft. Steht das Fahrzeug länger, wartet der Test auf die nächste Prüfung. |
| `timeout_s` | `300.0` | Timeout eines einzelnen Tests |

## `[uploader]` (Pflicht)

Lokale Ablage und HTTPS-Upload der gespeicherten Messdaten. Uploads gehen per HTTPS-POST an Schema und Host von `[backend] url` mit dem Pfad aus diesem Abschnitt, einen eigenen Upload-Host gibt es nicht. Ein Lauf versucht beim Messbeginn und nach dem Abschließen hochzuladen, an beiden Stellen steht die Verbindung ohnehin.

| Feld | Standard | Bedeutung |
|---|---|---|
| `upload_dir` | `"upload_queue"` (relativ zum Arbeitsverzeichnis) | lokales Verzeichnis für Messdateien, die noch hochgeladen werden müssen. Gerätespezifisch, den absoluten Pfad in der `config.local.toml` setzen. |
| `path` | `"/api/measurements"` | Endpunkt für Messdateien, eine Anfrage pro *Datei* (JSON-Array) |
| `latency_path` | `"/api/latency-results"` | Endpunkt für Latenzergebnisse, eine Anfrage pro *Ergebnis* (einzelnes JSON-Objekt). Die beiden Endpunkte haben unverträgliche Formate. |
| `debug_upload` | `true` | bindet den Upload an die IP von `wwan0` (zum Testen über die Mobilfunkverbindung selbst) und loggt ausführlich |
| `timeout_s` | `10.0` | HTTP-Timeout pro Upload |

Die früheren SCP-Felder `upload_user`, `upload_host`, `upload_port` und `remote_dir` gibt es nicht mehr. Stehen sie noch in einer `config.toml`, werden sie mit einer Warnung ignoriert.

## `[logging]`

| Feld | Standard | Bedeutung |
|---|---|---|
| `level` | `"INFO"` | Log-Level |
| `log_file` | Platzhalter | Pfad der rotierenden Log-Datei |
| `max_bytes` | `5_000_000` | Größe, ab der die Log-Datei rotiert |
| `backup_count` | `3` | Zahl der aufbewahrten rotierten Dateien |

## `[system]`

Raspberry-Pi-Einstellungen: Netzwerkschnittstellen, Gerätemodus, Absturzverhalten.

| Feld | Standard | Bedeutung |
|---|---|---|
| `running_on_pi` | `true` | startet und überwacht `quectel-CM` und fährt den Pi am Ende eines Laufs herunter. Ein lokaler Entwicklungs-Checkout setzt `false`. |
| `network_interfaces` | `("wlan0", "wwan0")` | Schnittstellen, deren IPv4-Adressen beim Start geloggt werden |
| `mode` | `"auto"` | `"auto"`: baut beim Booten die Mobilfunkverbindung auf, startet den Heartbeat und beginnt zu messen, sobald die Bewegungserkennung Bewegung bestätigt. `"manual"`: bootet genauso, tut dann aber nichts, bis ein Fernbefehl (`start-measuring-now`) kommt, und beendet einen Lauf nie wegen Stillstand. Der frühere Wert `"waiting"` wird mit einer Warnung als `"manual"` gelesen. Wirkt erst beim nächsten Booten. Aus der Ferne gewechselt wird über `mode-manual-now`/`mode-auto-now`, die `system_mode` in die `config_overrides.toml` schreiben, statt dieses Feld im laufenden Betrieb zu ändern. |
| `crash_same_error_limit` | `3` | Ein unbehandelter Fehler startet die Messbox neu. Ist derselbe Fehler (Ausnahmetyp und auslösende Funktion) so oft in Folge aufgetreten, startet sie einmalig in den Wiederherstellungszustand, der erst nach `start-measuring-now` misst. Ein weiterer Fehler danach startet sie in den Wartungsmodus, in dem nur die Mobilfunkverbindung läuft, siehe [Architektur](architektur.md#absturze). Mindestens `1`. |
| `crash_reboot_limit` | `5` | Dieselbe Eskalation greift auch, wenn es so viele Neustarts wegen unbehandelter Fehler beliebiger Art in Folge gab. Mindestens `1`. |

## `[link_watchdog]`

Stellt eine Mobilfunkverbindung wieder her, die nicht zurückkommt. Nur aktiv mit `[system] running_on_pi`, weil `quectel-CM` nur dann gestartet wird.

| Feld | Standard | Bedeutung |
|---|---|---|
| `enabled` | `true` | schaltet die Überwachung ein |
| `interface` | `"wwan0"` | Schnittstelle, deren IPv4-Adresse „Verbindung steht“ bedeutet |
| `check_interval_s` | `30.0` | Sekunden zwischen zwei Prüfungen |
| `restart_after_s` | `180.0` | Ist die Verbindung so lange weg, wird `quectel-CM` neu gestartet. Solange sie weg bleibt, verdoppelt sich die Wartezeit vor jedem weiteren Schritt. |
| `max_restart_interval_s` | `1800.0` | Obergrenze für diese Wartezeit. Der Watchdog gibt nie auf, die nächste Störung beginnt wieder bei `restart_after_s`. Mindestens `restart_after_s`. |
| `radio_reset_after_restarts` | `2` | Nach so vielen erfolglosen Neustarts wird stattdessen das Funkmodul des Modems zurückgesetzt (`AT+CFUN=0`/`1`). Ist das Modem gerade nicht erreichbar oder läuft schon eine Rücksetzung, wird `quectel-CM` erneut neu gestartet. |

## `[clock]`

Stellt die Systemuhr per NTP (SNTP), sobald die Mobilfunkverbindung steht. Der Pi hat keine Echtzeituhr, und `systemd-timesyncd` versucht es nur, bevor die Verbindung besteht. Die Uhr wird außerdem einmal pro Boot aus der GNSS-Zeit gestellt.

| Feld | Standard | Bedeutung |
|---|---|---|
| `ntp_server` | `""` | IPv4-Adresse oder Hostname des NTP-Servers. Leer: kein NTP. Wird nach jedem Aufbau der Verbindung abgefragt, bis es einmal klappt. Gerätespezifisch, in der `config.local.toml` setzen. |
| `ntp_timeout_s` | `3.0` | Timeout einer Abfrage. Muss positiv sein. |

## Startprüfung

`load_config()` bricht beim Start mit `ValueError` ab, bevor irgendetwas mit der Hardware passiert, wenn:

- nur eines von `[movement_gate] home_latitude`/`home_longitude` gesetzt ist
- `[system] mode` weder `"auto"` noch `"manual"` ist (`"waiting"` wird vorher als `"manual"` gelesen)
- `[collector] modem_reconnect_attempts` kleiner als 1 oder `modem_reconnect_delay_s` negativ ist
- `[system] crash_same_error_limit` oder `crash_reboot_limit` kleiner als 1 ist
- `[link_watchdog] check_interval_s` oder `restart_after_s` nicht positiv, `max_restart_interval_s` kleiner als `restart_after_s` oder `radio_reset_after_restarts` negativ ist
- `[clock] ntp_timeout_s` nicht positiv ist

Nach einem solchen Abbruch baut die Messbox nur noch die Mobilfunkverbindung auf, damit sie per SSH erreichbar bleibt (siehe [Architektur](architektur.md#einstieg)).

Nach dem Anwenden der `config_overrides.toml` laufen die Prüfungen erneut. Dort führt ein Verstoß aber nicht zum Abbruch, sondern die betroffene Änderung wird verworfen (siehe [Fernkonfiguration](#fernkonfiguration-config_overridestoml)).

Fehlende gerätespezifische Werte loggt die Software als Warnung, ohne abzubrechen: `[backend] url`/`device_key`, `[heartbeat] device_id`, `[quectel_cm] binary` und, bei `[heartbeat] enabled`, `[heartbeat] hmac_secret`. Ebenso nur mit einer Warnung ignoriert werden Felder und Tabellen, die es nicht mehr gibt (`[system] shutdown_gpio`, die SCP-Felder unter `[uploader]`, `[profiles.*]`), weil ein Abbruch die Messbox vor dem Aufbau der Mobilfunkverbindung unerreichbar machen würde. Eine echte Messbox braucht sie, ein lokaler Entwicklungs-Checkout mit `[system] running_on_pi = false` hat sie normalerweise nicht.

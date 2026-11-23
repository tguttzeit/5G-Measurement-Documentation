# Architektur

Diese Seite beschreibt, wie die Messsoftware aufgebaut ist und wie ein Lauf abläuft. Die Zustände eines Laufs aus Sicht der Nutzung zeigt das Zustandsdiagramm unter [Wie die Messbox misst](../nutzung/messung.md). Einzelne Klassen und Funktionen stehen unter [Code](../../../reference/measurement_software/).

## Einstieg

`main.py` setzt zuerst die Signal-Handler, übernimmt Modus-Dateien älterer Versionen, lädt die `config.toml` in einen einzigen Konfigurationsbaum (`AppConfig`) und richtet das Logging ein. Danach prüft es, ob ein früherer Start den Wartungsmodus verlangt hat, liest die einmalige Markierung für den manuellen Modus und die gespeicherten Befehlsbestätigungen (siehe [Herunterfahren, Neustart und Abbruch](#herunterfahren-neustart-und-abbruch)). `_run()` baut dann Modem und GNSS-Empfänger, sichert Daten eines unterbrochenen früheren Laufs und führt den Lauf durch seine Zustände.

Schlägt einer dieser Schritte vor `_run()` fehl, geht die Messbox ohne Neustart direkt in den [Wartungsmodus](#absturze), weil ein Fehler so früh meist in einer Datei auf dem Gerät liegt, die ein Neustart nicht ändert. Lässt sich die Konfiguration gar nicht laden, startet `run_emergency_link()` nur die Mobilfunkverbindung, aus den Werten, die sich noch lesen lassen (`[system] running_on_pi`, `[quectel_cm]`, `[link_watchdog]`, darunter die Werte des letzten erfolgreichen Starts aus `last_good_link_settings.json`, notfalls `vendor/quectel-CM/quectel-CM`). Ein Backend wird dann nicht benachrichtigt. Beides bleibt nicht bestehen: Ist die Ursache behoben, startet der nächste Boot normal.

## Konfiguration

Die Konfiguration besteht aus verschachtelten Dataclasses (`core/config.py`), die aus der `config.toml` gebaut werden. Die Abschnitte für Hardware, Backend und Uploader sind Pflicht, alle anderen fallen auf Standardwerte zurück. Alle Felder stehen in der [Konfigurationsreferenz](konfiguration.md).

`[device] mission_type` ist nur eine Kennzeichnung der Daten. Die Komponenten unterscheiden nie danach. Was eine Drohnenmessung anders macht (kein Warten auf Bewegung, kein Ende bei Stillstand), ergibt sich aus dem manuellen Modus. Frühere `[profiles.*]`-Tabellen in einer `config.toml` werden mit einer Warnung ignoriert.

## Hardware-Abstraktion

`Modem`, `GNSSReceiver` und `Display` sind abstrakte Basisklassen mit festen Methoden zum Öffnen, Schließen und Abfragen. Welche Implementierung (z. B. `Quectel`, `NMEASerial`) gebaut wird, entscheidet zur Laufzeit ein `type`-Wert in der Konfiguration über eine kleine Factory. Wie man eine neue Implementierung ergänzt, steht unter [Hardware-Integration](hardware-integration.md).

## Ablauf eines Laufs

Jeder Bootvorgang durchläuft eine kleine Menge benannter Zustände (`RunPhaseState`, `core/run_phase.py`): `STARTING_UP`, `RECOVERING_PENDING_DATA`, dann je nach Modus die Warte-Zustände, `ACTIVE_MEASURING`, `FINALIZING` und `DONE`. Dazu kommen `STOPPING`, `SHUTTING_DOWN`, `REBOOTING` und `CRITICAL_ERROR`. Der Heartbeat meldet jeden dieser Zustände. In beiden Modi starten `quectel-CM` und der Heartbeat sofort beim Booten, die Messbox ist also während des ganzen Laufs erreichbar. Nach dem Start von `quectel-CM` wartet die Anwendung bis zu 30 Sekunden auf die Mobilfunkverbindung, bevor sie den ersten Heartbeat schickt. Dafür verbraucht sie mehr Strom als in der ursprünglichen Auslegung, die das Modem bis zum Messbeginn ausgeschaltet ließ.

Jeder Weg in die Messung führt über `WAITING_FOR_GPS_FIX` (`core/first_fix_wait.py::FirstFixWaiter`), `ACTIVE_MEASURING` heißt also immer, dass ein Fix vorliegt. Mit dem ersten Fix stellt die Software die Systemuhr nach der GNSS-Zeit.

**Automatikmodus** (`[system] mode = "auto"`, Standard): Die Messbox wartet auf einen GPS-Fix, höchstens `[collector] max_wait_for_first_fix`. Kommt keiner, endet der Durchlauf ohne Lauf. Danach wartet die Bewegungserkennung (`core/movement_gate.py`) auf bestätigte Bewegung (`WAITING_FOR_MOVEMENT`). Bewegung gilt als bestätigt, wenn sich die Position über mehrere aufeinanderfolgende Abfragen vom ersten Fix entfernt hat und, falls eine Heimatposition eingestellt ist, die Messbox diese verlassen hat. Danach wechselt der Lauf nach `ACTIVE_MEASURING`. Mit `[movement_gate] enabled = false` entfällt das Warten auf Bewegung. Während des Wartens wirken nur `shutdown-now` und `reboot-now`.

**Manueller Modus** (`[system] mode = "manual"`): Die Messbox bootet genauso, wartet dann aber in `MANUAL_MODE_IDLE` (`ManualModeLoop`) auf einen Fernbefehl. `start-measuring-now` wartet ohne Zeitgrenze auf einen GPS-Fix und startet dann die Messung, ohne auf Bewegung zu achten. `stop-measuring-now` bricht dieses Warten ab und kehrt in den Leerlauf zurück. `run-selftest-now` führt die Prüfungen des Selbsttests aus und bleibt im Leerlauf. Ein Lauf endet im manuellen Modus nie wegen Stillstand. Ein Wechsel des Modus (`mode-manual-now`, `mode-auto-now`) wirkt erst beim nächsten Booten. Der frühere Name `waiting` wird in `config.toml` und `config_overrides.toml` noch als `manual` gelesen, `mode-waiting-now` wirkt wie `mode-manual-now`.

**Einmal manuell:** Beendet `stop-measuring-now` einen Lauf im Automatikmodus, legt es die Markierung `manual_next_boot.json` neben der `config.toml` an. Der nächste Boot läuft dann im manuellen Modus und entfernt die Markierung, sobald er den Leerlauf erreicht hat. Der eingestellte Modus ändert sich dabei nicht.

**Wiederherstellung** (`RECOVERY_IDLE`): der einmalige Boot nach der [Absturz-Eskalation](#absturze). Er wartet wie der manuelle Modus auf `start-measuring-now`, meldet aber im Heartbeat die Absturzdetails mit. Der Zustand wird beim Eintritt verbraucht, der Boot danach ist ein normaler.

Ob ein Fernbefehl gerade anwendbar ist, entscheidet die aktuelle Laufphase, nicht der Modus beim Booten. Nicht anwendbare Befehle werden mit `not_applicable` bestätigt.

## Messschleife

Sobald gemessen wird, wartet der `Collector` (`core/collector.py`) auf GPS-Fixes und nimmt einen Messpunkt (`Datapoint`: Zellwerte, GNSS-Fix, Zeitstempel, Lauf-ID) auf, wenn die Aufnahmeregel (`core/capture_gate.py`) es erlaubt:

- `capture_gate = "distance"` (Standard): nach einer Mindeststrecke seit dem letzten Messpunkt
- `capture_gate = "time"`: in festem Zeitabstand

Das Ende bei Stillstand richtet sich immer nach der Strecke, die Aufnahmeregel ändert also nie, wann ein Lauf endet. Im Automatikmodus endet ein Lauf nach `[collector] max_idle_time` ohne echte Bewegung, `max_idle_time = 0` schaltet das ab. Die Uhr dafür läuft nach dem ersten Fix weiter, auch wenn danach keine Fixes mehr kommen. Im manuellen Modus und in der Wiederherstellung gibt es kein Ende bei Stillstand. Unabhängig vom Modus endet ein Lauf per `stop-measuring-now`. Fernbefehle werden nach jedem Lesevorgang des Empfängers geprüft, auch wenn kein Fix kommt. Ein Hintergrund-Thread (`KeepModemAliveSender`) hält die Mobilfunkverbindung mit kleinen UDP-Paketen offen.

## Daten sichern und hochladen

**Stromausfallsicher:** Messpunkte werden einzeln als JSON-Zeile an das Log des Laufs angehängt und per `fsync` geschrieben. Ein unterbrochener Lauf verliert höchstens die letzte, unvollständige Zeile. Beim Abschließen wird das Log atomar in die Datei umgewandelt, die hochgeladen wird. Nicht abgeschlossene Logs und temporäre Dateien werden beim nächsten Start aufgeräumt oder gesichert.

**Lauf-ID:** Jeder Lauf bekommt eine zufällige UUID4, die auch der Latenztester verwendet. Jeder Messpunkt und jedes Latenzergebnis trägt sie als `run_id`, auch in jeder Log-Zeile. Ein nach einem Stromausfall gesicherter Lauf behält damit seine ID. Das Backend behandelt das Feld als optional (Uploads ohne ID landen in einem Altlauf), im Heartbeat steht es nicht.

**Hochladen** (`core/uploader.py`): Ausstehende Dateien gehen per HTTPS-POST mit den Headern `X-Device-ID` und `X-Device-Key` ans Backend, aber nur, wenn `wlan0` oder `wwan0` eine IPv4-Adresse hat. Messdateien und Latenzergebnisse haben je einen eigenen Endpunkt (eine Anfrage pro Datei bzw. pro Ergebnis), zugeordnet über das Präfix des Dateinamens. Ein Lauf versucht an zwei Stellen hochzuladen, an denen die Verbindung ohnehin steht: beim Eintritt in `ACTIVE_MEASURING` und nach dem Abschließen (ohne Lauf nach dem Warten, das den Durchlauf beendet hat). Dazu kommen Herunterfahren, Neustart, SIGTERM und `force-upload-now`. Eine Datei wird erst nach erfolgreichem Upload lokal gelöscht.

## Heartbeat, Fernbefehle und Fernkonfiguration

Der Heartbeat (`remote/heartbeat.py`) meldet in festem Abstand den Zustand des Laufs ans Backend, unter anderem die aktuelle Laufphase (`run_phase`) und den GPS-Status. Die Antwort kann Konfigurationsänderungen aus einer erlaubten Liste und einmalige Befehle (z. B. `force-upload-now`, `shutdown-now`) enthalten. Beide sind per HMAC signiert und werden vom `RemoteCommandDispatcher` geprüft und ausgeführt. Konfigurationsänderungen landen in der lokalen, nicht eingecheckten `config_overrides.toml`.

- **Schutz vor Wiedereinspielen:** Jede Heartbeat-Anfrage trägt eine zufällige `nonce`, die das Backend im signierten Antworttext zurückgeben muss. Eine Antwort mit Änderungen oder Befehlen ohne passende `nonce` wird verworfen.
- **Gerätemodus:** `system_mode` (`auto`/`manual`) ist eines der änderbaren Felder und wird wie alle anderen in `current_config` mitgemeldet.
- **Übernehmen:** `promote-overrides-now` (oder `python -m measurement_software.promote_overrides`) schreibt die aktuellen Werte aus `config_overrides.toml` als neue Grundlage in die `config.toml`. Kommentare bleiben dabei erhalten, weil die Datei mit `tomlkit` bearbeitet wird.
- **Rückmeldung:** Das Ergebnis jedes Befehls (`success`, `failed` mit Fehler oder `not_applicable`) geht mit dem nächsten Heartbeat als `executed_commands` zurück. Schickt das Backend einen schon ausgeführten Befehl erneut, wird nur die Rückmeldung wiederholt, nicht der Befehl. Eine verlorene Rückmeldung braucht damit keine eigene Wiederholungslogik. Beim Stoppen des Heartbeats gehen noch ausstehende Rückmeldungen in bis zu drei weiteren Heartbeats raus, damit z. B. die Bestätigung von `stop-measuring-now` nicht mit dem Prozessende verloren geht. Befehle aus diesen Antworten werden nicht mehr ausgeführt.
- **Abgelehnte Heartbeats:** Weist das Backend einen Heartbeat mit einem HTTP-Fehler ab, loggt die Messbox den Grund aus der Antwort.

## Herunterfahren, Neustart und Abbruch

| Auslöser | Verhalten |
|---|---|
| `shutdown-now`, fehlgeschlagene SIM-Entsperrung | einheitlicher Weg über `core/system.py::shutdown()`: ausstehende Daten abschließen und hochladen, Grund loggen, ausschalten |
| `reboot-now` | `core/system.py::reboot()`, wie oben, aber mit Neustart |
| Lauf regulär beendet (`DONE`) | bei `[system] running_on_pi = true` derselbe Weg über `shutdown()` |
| `stop-measuring-now` | beendet den Lauf wie ein Ende bei Stillstand. Im Automatikmodus legt es vorher die Markierung für einen einmaligen Start im manuellen Modus an |
| `SIGTERM` (`systemctl stop`, Herunterfahren des Systems) | schickt einen letzten Heartbeat mit der Laufphase `stopping`, beendet den Lauf, schließt das Log ab und lädt es nach Möglichkeit hoch, beendet danach `quectel-CM`; zählt nicht als Absturz |

`shutdown()` und `reboot()` schicken vorher einen letzten Heartbeat mit der Laufphase `shutting_down` bzw. `rebooting`, bei SIGTERM ist es `stopping` (mit höchstens 3 s Timeout, damit systemd nicht vorher SIGKILL schickt). Hat ein Fernbefehl sie ausgelöst, bestätigen sie dessen ID als `"received"`. Außerdem speichern sie die ID neben der `config.toml` (`pending_reboot_ack.toml`/`pending_shutdown_ack.toml`). Der nächste Boot bestätigt sie dann als `success` und führt den Befehl nicht erneut aus, falls das Backend ihn noch einmal schickt, etwa weil die `"received"`-Bestätigung verloren ging.

## Abstürze

Eine unbehandelte Ausnahme, die bis nach oben durchschlägt, eskaliert `core/crash_policy.py::CrashPolicy` stufenweise. Der Zustand überlebt Neustarts.

1. Neustart.
2. Ist derselbe Fehler `[system] crash_same_error_limit`-mal hintereinander aufgetreten (oder gab es `crash_reboot_limit` Neustarts in Folge): Neustart in den einmaligen Wiederherstellungszustand (`RECOVERY_IDLE`, siehe [Ablauf eines Laufs](#ablauf-eines-laufs)). Der eingestellte Modus bleibt unverändert.
3. Tritt danach erneut ein Fehler auf: Neustart in den Wartungsmodus (`core/maintenance_mode.py`).

Lässt sich ein Absturz nicht in `crash_state.json` festhalten, könnte nichts eine Neustartschleife erkennen. Die Messbox geht dann sofort ohne Neustart in den Wartungsmodus und übernimmt dabei das schon laufende `quectel-CM`.

Der Wartungsmodus wird früh in `main()` geprüft, direkt nach dem Laden der Konfiguration. Er schickt einen Heartbeat mit der Laufphase `critical_error` und einem `critical_error`-Objekt (wiederholt, bis er zugestellt ist) und betreibt danach nur noch `quectel-CM` und die Überwachung der Mobilfunkverbindung, einschließlich der Rücksetzung des Funkmoduls, damit die Messbox per SSH erreichbar bleibt. GNSS, Display und Messung bleiben aus. Bei SIGTERM beendet er `quectel-CM` selbst. Verlassen wird er, indem man die Ursache behebt, `crash_state.json` neben der `config.toml` löscht und neu startet. Jeder Absturz hinterlässt außerdem `last_crash_report.json` (Fingerabdruck, Zähler, vollständiger Traceback), den der nächste Start ins Log schreibt.

## Raspberry Pi

`core/system.py` kümmert sich um den Prozess `quectel-CM`, das Stellen der Uhr aus der GNSS-Zeit und das Herunterfahren. Ein Signal auf einem GPIO-Pin gibt es nicht mehr. Ein `shutdown_gpio` in einer älteren `config.toml` wird mit einer Warnung ignoriert.

`core/link_watchdog.py` startet `quectel-CM` neu, wenn `wwan0` zu lange keine IPv4-Adresse hat. Helfen mehrere Neustarts nicht, setzt er das Funkmodul des Modems zurück (`AT+CFUN`). Die serielle Schnittstelle des Modems gehört dabei `core/modem_access.py::ModemAccess`, weil sie nicht threadsicher ist: Während der Messung übernimmt der Messthread die Rücksetzung bei der nächsten Abfrage, außerhalb öffnet `ModemAccess` die Schnittstelle nur kurz dafür. Bleibt die Verbindung weg, verdoppelt sich die Wartezeit vor jedem weiteren Schritt bis `max_restart_interval_s`. Der Watchdog gibt nie auf, die nächste Störung beginnt wieder bei `restart_after_s`.

Die Uhr stellt die Software zusätzlich über NTP (`core/ntp_clock.py`), sobald die Mobilfunkverbindung steht, weil der Pi keine Echtzeituhr hat und `systemd-timesyncd` es nur vor dem Aufbau der Verbindung versucht. Das läuft nur bei gesetztem `[clock] ntp_server`.

## Selbsttest

`python -m measurement_software.selftest` ist ein eigener Einstiegspunkt, der jedes Hardware-Teilsystem einzeln gegen die echte Hardware prüft (eine AT-Abfrage, ein NMEA-Satz usw.) und bestanden, fehlgeschlagen oder übersprungen meldet. Keine Prüfung lädt Messdaten hoch oder fährt das Gerät herunter, `heartbeat` schickt aber einen echten Heartbeat. Er ist für die Fehlersuche an der Verkabelung einer Messbox per SSH gedacht und unabhängig von den Unit-Tests. Hinweise zum Lesen der Ergebnisse stehen unter [Messbox aufsetzen](messbox-aufsetzen.md#verkabelung-vor-dem-ersten-lauf-prufen).

## Testmuster

Fast alles in der Messsoftware ist Ein- und Ausgabe an den Rändern: serielle Schnittstellen, I2C, Unterprozesse, HTTP, Uhrzeit, Threads. Die Tests ersetzen deshalb gezielt diese Grenzen, statt locker zu mocken:

- Fakes für `Modem`, `GNSSReceiver` und `Display` implementieren die echten Basisklassen.
- `serial.Serial`, `subprocess` und `urllib.request` werden an der Stelle ersetzt, an der sie verwendet werden, durch Fakes, die aufzeichnen, was gesendet wurde.
- Zeitabhängige Logik (`Collector`, `MovementGate`) ersetzt die Uhr, statt echte Wartezeiten abzuwarten.

Die Tests unter `tests/` spiegeln den Aufbau des Pakets `src/measurement_software`.

## Code-Stil

Lesbarer Code geht vor Kommentaren, die erklären, was er tut. Kommentare sind dort angebracht, wo sich ein Gedanke nicht durch Namen oder Struktur allein ausdrücken lässt, ersetzen diese Mühe aber nicht.

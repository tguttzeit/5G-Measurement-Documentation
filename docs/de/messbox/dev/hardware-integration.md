# Hardware-Integration

Die Messsoftware spricht mit drei austauschbaren Hardware-Rollen: Modem, GNSS-Empfänger und Statusdisplay. Jede Rolle steckt hinter einer abstrakten Schnittstelle mit einer kleinen Factory, die anhand eines `type`-Werts in der Konfiguration die passende Implementierung baut. Für ein anderes Modem, einen anderen GNSS-Empfänger oder ein anderes Display schreibt man eine neue Klasse und registriert sie, sonst ändert sich nichts.

## Das Muster

Jede Rolle besteht aus drei Teilen:

1. **Eine abstrakte Basisklasse** mit dem Vertrag, z. B. `modems/modem.py::Modem`.
2. **Eine oder mehrere Implementierungen**, z. B. `modems/quectel.py::Quectel`.
3. **Ein Factory-Dictionary** mit `type` als Schlüssel, z. B. `modems/__init__.py::_MODEM_FACTORIES`. `create_modem(config)` baut daraus die eingestellte Implementierung, ein unbekannter `type` löst `ValueError` aus.

`main.py` ruft nur `create_modem(config.modem)`, `create_gnss_receiver(config.gnss_receiver)` und `create_display(config.display)` auf und importiert nie eine Implementierung direkt. Eine neue Implementierung ist damit eine neue Datei plus ein Eintrag im Factory-Dictionary.

## Neues Modem

1. Braucht das Modem mehr als die vorhandenen Felder von `ModemConfig` (`port`, `baud_rate`, `timeout`, `mode`, Wiederholungen), dafür eine Dataclass anlegen. Die meisten seriellen Modems brauchen nichts zusätzlich.
2. `Modem` (`modems/modem.py`) in einer neuen Datei `modems/<name>.py` implementieren:
    - `open()` / `close()`: serielle Verbindung verwalten.
    - `unlock_sim()`: SIM-PIN eingeben, falls nötig. Bei einem Fehler die passende Unterklasse von `SimUnlockError` auslösen (`SimPinNotConfiguredError`, `SimPinRejectedError`, `SimPukRequiredError`, `SimStatusUnknownError`), keine allgemeine Ausnahme, damit Aufrufer passend reagieren können.
    - `query_cell_info() -> list[CellSample]`: ein `CellSample` pro aktiver Funktechnik (RAT) zurückgeben. Alle Felder füllen, die das Modem liefert, den Rest auf `None` lassen. Was sich keinem gemeinsamen Feld zuordnen lässt, kommt in das offene Dictionary `vendor_specific_extras`.
    - `reset_radio()`: Funkmodul aus- und wieder einschalten, damit sich das Modem neu im Netz anmeldet. Die Überwachung der Mobilfunkverbindung ruft das auf, wenn Neustarts von `quectel-CM` nicht helfen.
    - `power_down()`: Ausschaltbefehl des Modems senden.
3. Die Klasse in `_MODEM_FACTORIES` in `modems/__init__.py` unter einem neuen `type` registrieren.
4. In der `config.toml` `[modem] type = "<name>"` setzen.
5. Tests unter `tests/modems/test_<name>.py` nach dem Vorbild von `tests/modems/test_quectel.py` schreiben: `serial.Serial` an der Verwendungsstelle (`measurement_software.modems.<name>.serial.Serial`) durch einen Fake ersetzen, der aufzeichnet, was geschrieben wurde, und vorgegebene Antworten liefert. Ein Test berührt nie eine echte serielle Schnittstelle.

!!! danger "PIN nie automatisch wiederholen"

    Eine abgelehnte PIN nie automatisch erneut eingeben und nie eine PUK eingeben. Beides kann die SIM-Karte dauerhaft sperren. Details stehen in den Docstrings der Ausnahmen.

## Neuer GNSS-Empfänger

1. `GNSSReceiver` (`gnss/gnss_receiver.py`) in einer neuen Datei `gnss/<name>.py` implementieren:
    - `open()` / `close()`: Verbindung verwalten.
    - `read_fix() -> GNSSFix | None`: den letzten Fix (`Position` und Zahl der genutzten Satelliten) oder `None`, wenn gerade keiner vorliegt. `GNSSFix.placeholder = True` nur für einen absichtlich falschen Fix setzen (z. B. bei einem Testlauf ohne GPS), nie für echte Daten.
    - `read_datetime() -> datetime | None`: die letzte UTC-Zeit aus GNSS, mit der die Systemuhr gestellt wird.
    - `read_satellites_in_view()` ist optional (Standard: `None`). Nur überschreiben, wenn der Empfänger die Zahl der verfolgten Satelliten auch ohne Fix liefert. Diese Zahl zeigt der GPS-Fix-Test als Fortschritt an, bevor ein Fix da ist.
    - `read_gnss_diagnostic()` ist ebenfalls optional (Standard: `None`): roher Diagnosetext des Empfängers (z. B. NMEA `$GxTXT` mit einem Antennenfehler). Er wird vor der Anzeige auf Display und im Backend über `updated_gnss_diagnostic()` in eine kurze, feste Meldung übersetzt.
2. Die Klasse in `_GNSS_FACTORIES` in `gnss/__init__.py` unter einem neuen `type` registrieren.
3. In der `config.toml` `[gnss_receiver] type = "<name>"` setzen.
4. Tests unter `tests/gnss/test_<name>.py` nach dem Vorbild von `tests/gnss/test_nmea_serial.py` schreiben (`serial.Serial` wie oben ersetzen).

## Neues Display

1. `Display` (`displays/display.py`) in einer neuen Datei `displays/<name>.py` implementieren. Vorbild für die Schnittstelle ist `displays/ssd1306_display.py`, `displays/null_display.py` zeigt die leere Grundform, auf die jede Messbox ohne Display zurückfällt.
2. Die Klasse in `_DISPLAY_FACTORIES` in `displays/__init__.py` unter einem neuen `type` registrieren. Bei `[display] enabled = false` liefert `create_display()` unabhängig vom `type` immer `NullDisplay()`, eine neue Implementierung muss also nur den eingeschalteten Fall abdecken.
3. In der `config.toml` `[display] type = "<name>"` setzen und neue Felder, die die Implementierung braucht, in `DisplayConfig` (`core/config.py`) ergänzen, z. B. ein anderes Bus- oder Adressschema als `i2c_port`/`i2c_address`.
4. Tests unter `tests/displays/test_<name>.py` nach dem Vorbild von `tests/displays/test_ssd1306_display.py` schreiben.

## Allgemeine Hinweise

- Felder, die nur eine Hardware-Implementierung betreffen, gehören in die Konfigurations-Dataclass ihrer Rolle (`ModemConfig`, `GnssConfig`, `DisplayConfig`) in `core/config.py` und in die [Konfigurationsreferenz](konfiguration.md).
- Gerätespezifisches (echter Hostname, Zugangsdaten, Hardware-Adresse, die nicht in die eingecheckte `config.toml` gehören) kommt in die `config.local.toml`. Welche Felder dort erlaubt sind, steht in `core/config_sources.py::ALLOWED_LOCAL_FIELDS`, siehe auch [Messbox aufsetzen](messbox-aufsetzen.md#geratespezifische-werte).
- Wie die Teile in den Ablauf eines Laufs passen und wie die Tests Hardware ersetzen, steht unter [Architektur](architektur.md) und [Testmuster](architektur.md#testmuster).

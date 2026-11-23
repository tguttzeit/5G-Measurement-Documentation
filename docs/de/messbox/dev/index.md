# Development

Dieser Abschnitt richtet sich an alle, die die Messsoftware der Messbox weiterentwickeln, an neue Hardware anpassen oder eine neue Messbox aufsetzen. Wie man die Messbox im Feld bedient, steht unter [Nutzung](../nutzung/index.md).

## Aufbau

Die Messsoftware ist eine Python-Anwendung, die auf einem Raspberry Pi läuft und beim Booten als `systemd`-Dienst startet. Der Code liegt im Repository [`tguttzeit/5G-Measurement-Software`](https://github.com/tguttzeit/5G-Measurement-Software).

| Teil | Ort im Code | Aufgabe |
|---|---|---|
| Einstieg und Ablauf | `main.py`, `core/run_phase.py`, `core/first_fix_wait.py`, `core/movement_gate.py` | lädt die Konfiguration, baut Modem und GNSS-Empfänger, führt einen Lauf durch seine Zustände |
| Messschleife | `core/collector.py`, `core/capture_gate.py` | nimmt Messpunkte auf (Zellwerte, Position, Zeit) |
| Hardware | `modems/`, `gnss/`, `displays/` | austauschbare Implementierungen für Modem, GNSS-Empfänger und Display |
| Speichern und Hochladen | `core/run_log.py`, `core/uploader.py` | schreibt Messpunkte stromausfallsicher weg und lädt sie ans Backend |
| Backend-Anbindung | `remote/heartbeat.py` | Heartbeat, Fernbefehle und Fernkonfiguration |
| Raspberry Pi | `core/system.py`, `core/link_watchdog.py`, `core/modem_access.py`, `core/ntp_clock.py` | `quectel-CM`, Uhrzeit (GNSS und NTP), Herunterfahren, Überwachung der Mobilfunkverbindung |
| Absturzbehandlung | `core/crash_policy.py`, `core/maintenance_mode.py` | Neustart, Wiederherstellung und Wartungsmodus bei wiederholten Fehlern |
| Selbsttest | `selftest.py`, `selftests/` | prüft die Hardware einzeln über die Kommandozeile |

Wie die Teile zusammenspielen, steht unter [Architektur](architektur.md).

## Seiten

- [Architektur](architektur.md): Ablauf eines Laufs, Absturzbehandlung, Speichern, Hochladen, Fernbefehle, Testmuster
- [Konfigurationsreferenz](konfiguration.md): alle Felder der `config.toml` und was sich aus der Ferne ändern lässt
- [Hardware-Integration](hardware-integration.md): ein neues Modem, einen neuen GNSS-Empfänger oder ein neues Display anbinden
- [Messbox aufsetzen](messbox-aufsetzen.md): eine neue Messbox einrichten, gerätespezifische Werte, Autostart, bekannte Stolperstellen
- [Lokal testen](lokal-testen.md): Entwicklungsumgebung, Tests und Lint, Anwendung und Selbsttest von Hand starten, Test mit dem Backend im lokalen Netz
- [Code](../../../reference/measurement_software/): Referenz der Module, Klassen und Funktionen, aus den Docstrings erzeugt (englisch)

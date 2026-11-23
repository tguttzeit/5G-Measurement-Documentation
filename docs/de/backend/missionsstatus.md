# Missionsstatus

Der `Missionsstatus` zeigt, was eine Messbox gerade tut. Grundlage ist der letzte Heartbeat, den sie gesendet hat. Die Seite aktualisiert sich selbst, `Aktualisieren` lädt sofort neu.

Oben wird die Messbox gewählt. Als `online` (grüner Kreis neben dem Namen) gilt sie, wenn in den letzten 5 Minuten ein Heartbeat angekommen ist.

## Laufphase

Die Leiste oben zeigt, in welcher Phase des Messlaufs die Messbox ist. Dieselbe Phase steht in der Kachel `Status` und, kürzer, auf dem Display der Messbox.

| Backend | Display | Bedeutung |
|---|---|---|
| `Startet` | `Starting up` | Die Software startet und baut die Mobilfunkverbindung auf |
| `Ausstehende Daten werden wiederhergestellt` | `Recovering data` | Ein vorheriger Lauf wurde unterbrochen, die Messbox räumt dessen Daten auf, bevor es weitergeht |
| `Leerlauf im manuellen Modus` | `Idle (manual)` | Manueller Modus: wartet auf `Messung starten` |
| `Leerlauf (Wiederherstellung)` | `Idle (recovery)` | Einmaliger Start nach wiederholten Fehlern: wartet auf `Messung starten`, siehe [Automatischer Neustart](../messbox/troubleshooting/fehlerbilder.md#automatischer-neustart-und-critical-error) |
| `Warten auf GPS-Fix` | `No GPS fix` | Noch keine Position, siehe [Fehlerbilder](../messbox/troubleshooting/fehlerbilder.md). Im manuellen Modus erst nach `Messung starten` |
| `Warten auf Bewegung` | `Waiting: move` | Automatikmodus: Position da, die Fahrt ist aber noch nicht bestätigt |
| `Messung läuft` | `Measuring` | Ein Messlauf läuft |
| `Abschluss` | `Finalizing` | Messdaten werden abgeschlossen und hochgeladen |
| `Fertig` | `Done` | Lauf beendet, Herunterfahren steht bevor |
| `Wird beendet` | `STOPPING` | Die Software wird von außen beendet (z. B. zur Wartung per SSH), das Gerät läuft weiter |

Im Wiederherstellungszustand erscheint zusätzlich ein Hinweis auf den Absturz. Statt der Leiste erscheint ein Hinweis, wenn die Messbox gerade herunterfährt (`SHUTTING DOWN`), neu startet (`REBOOTING`) oder im Wartungsmodus ist (`CRITICAL ERROR`). Beim Wartungsmodus nennt der Hinweis zusätzlich, wie oft derselbe Fehler aufgetreten ist und wie viele Neustarts in Folge es gab. Was dann zu tun ist, steht unter [Automatischer Neustart und `CRITICAL ERROR`](../messbox/troubleshooting/fehlerbilder.md#automatischer-neustart-und-critical-error).

## Kacheln

| Kachel | Inhalt |
|---|---|
| `Letzter Heartbeat` | Zeitpunkt des letzten Heartbeats und wie lange er her ist |
| `GPS-Fix` | `Fix erhalten` oder `Kein Fix`, Anzahl Satelliten, Alter des Fixes |
| `Status` | aktuelle Laufphase, siehe oben |
| `Modus` | `Automatikmodus` oder `Manueller Modus` |
| `Datenpunkte` | Zellmessungen seit Beginn des laufenden Messlaufs, aufgeteilt in `Gültig` und `Ungültig` |
| `Ausstehende Dateien` | Messdateien, die noch nicht hochgeladen sind |
| `Freier Speicher` | freier Speicherplatz auf der Messbox |

Ungültig ist eine Messung, wenn RSRP, RSRQ oder SINR fehlt oder außerhalb des Bereichs liegt, den der Mobilfunkstandard zulässt. Das Modem hat dann keinen echten Messwert geliefert. Ein schwaches Signal macht eine Messung nicht ungültig. Steigt der Anteil ungültiger Messungen während der Fahrt deutlich, stimmt etwas mit dem Modem nicht, siehe [Fehlerbilder](../messbox/troubleshooting/fehlerbilder.md).

## Fernbefehle

Superuser sehen darunter die `Fernbefehle` und den `Befehlsstatus`. Welche Befehle es gibt und wann sie wirken, steht unter [Fernbefehle](../messbox/nutzung/fernbefehle.md). Ist die Messbox offline, bleibt ein Befehl 24 Stunden eingereiht und wird mit dem nächsten Heartbeat zugestellt.

Selbsttests und den GPS-Fix-Test zur Suche einer guten Antennenposition beschreibt die [Testvisualisierung](testvisualisierung.md).

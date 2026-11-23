# Messfahrt

Messung vom Fahrzeug aus. Die Messbox läuft im Automatikmodus: Sie startet die Messung selbst, sobald das Fahrzeug fährt, und beendet sie selbst, wenn es eine Weile steht.

## Was man braucht

- die vorbereitete Messbox (siehe [Messbox vorbereiten](vorbereitung.md)), dort noch angeschlossen und im Backend unter `Fernkonfiguration` geöffnet
- `Anker Prime 20000mAh` Powerbank, geladen, mit 4x M2x??-Schrauben [PRÜFEN! Länge]
- Antenne mit Magnethalterung
- USB-A-zu-USB-A- und USB-C-zu-USB-C-Kabel

## Anleitung

### Abschnitt I – Worauf in der Konfiguration zu achten ist

Die Standardeinstellungen sind für Messfahrten ausgelegt. Geprüft werden muss vor allem, ob von einem früheren Messflug noch etwas umgestellt ist.

1. In der `Fernkonfiguration` folgende Einstellungen prüfen (Spalte `Aktuell`):

    | Einstellung | Für die Messfahrt | Warum |
    |---|---|---|
    | `Missionsart` | `ground` | Kennzeichnet die Daten als Bodenmessung. Steht sie noch auf `drone`, werden die Daten im Backend als Drohnenmessung einsortiert. |
    | `Aufnahme-Auslöser` und `Positionsschwelle` | `distance`, 15 m | Ein Messpunkt alle 15 m Fahrt. Für eine dichtere oder lockerere Abdeckung die `Positionsschwelle` ändern, siehe [Messintervall und Rasterdichte](konfiguration.md#messintervall-und-rasterdichte). |
    | `Leerlaufschwelle` | 1800 s | So lange darf das Fahrzeug stehen, bevor die Messung endet. Sind längere Stopps geplant (Pausen, Stau), den Wert erhöhen. |

2. Geänderte Werte mit `Senden & Bestätigen` abschicken.
3. Im `Missionsstatus` die Kachel `Modus` prüfen. Steht sie auf `Manueller Modus` (z. B. nach einem Messflug), den Fernbefehl `Automatikmodus` senden und dabei `Anschließend neu starten` anhaken. Sonst würde die Messbox nicht von selbst mit der Messung beginnen. Steht sie schon auf `Automatikmodus` und wurden in Schritt 2 Werte geändert, stattdessen den Fernbefehl `Neustart` senden, damit sie gelten.
4. Warten, bis die Messbox wieder online ist, und in der Spalte `Aktuell` prüfen, ob die neuen Werte angekommen sind.
5. Per Fernbefehl `Herunterfahren`. Sobald das Display `SHUTTING DOWN` zeigt, die Stromversorgung trennen.

### Abschnitt II – Montage

1. Die Powerbank auf der Messbox festschrauben (4x M2x??-Schrauben) [PRÜFEN!].
2. Die Antenne mit der Magnethalterung außen an der Karosserie befestigen.
3. Die Messbox in den Innenraum oder an einen anderen trockenen und sicheren Ort legen.

### Abschnitt III – Verkabeln und Einschalten

1. Die Antenne an der Messbox anschließen:  
![Belegung der Antennenanschlüsse an der Messbox](../../../images/5gmu_antenna_ports.svg)
2. Messbox und Powerbank mit dem USB-A-zu-USB-A-Kabel verbinden (Modem).
3. Messbox und Powerbank mit dem USB-C-zu-USB-C-Kabel verbinden. Der Raspberry Pi startet.
4. Nach etwa 10 s zeigt das Display den Zustand an.
5. Im Backend unter `Missionsstatus` prüfen, ob die Messbox online ist. Mit Push-Benachrichtigungen kommt `Messbox gestartet`.

### Abschnitt IV – Messen

1. Warten, bis das Display `Waiting: move` bzw. der Missionsstatus `Warten auf Bewegung` zeigt. Vorher steht dort `No GPS fix` (bzw. `Warten auf GPS-Fix`), solange die Messbox noch keine Position hat.
2. Losfahren. Die Messbox prüft alle 45 s ihre Position und braucht zwei Prüfungen in Folge mit Bewegung. Die Messung startet deshalb etwa anderthalb Minuten nach der Abfahrt. Das Display zeigt dann `Measuring` (`Messung läuft`), mit Push-Benachrichtigungen kommt `Messung gestartet`.
3. Fahren. Alle 15 m entsteht ein Messpunkt. Im Stand entstehen keine.
4. Ab und zu auf das Display oder in den `Missionsstatus` schauen:
    - `Valid` sollte mit `Tot` steigen. `Inv` größer als 0 ist möglich.
    - Steht `PIPELINE BROKEN` auf dem Display oder kommt die Push-Benachrichtigung `Fehler`, siehe [Troubleshooting](../troubleshooting/fehlerbilder.md).
    - Die Messbox kann sich nach einem Fehler selbst neu starten und macht dann weiter. Bei schwerwiegenderen Problemen wechselt sie in einen Wartungsmodus, siehe [Automatischer Neustart und CRITICAL_ERROR](../troubleshooting/fehlerbilder.md#automatischer-neustart-und-critical-error).

### Abschnitt V – Messung beenden

1. Am Ziel anhalten und stehen bleiben. Nach 1800 s ohne Bewegung (Standardwert `Leerlaufschwelle`) beendet die Messbox die Messung von selbst.
2. Die Messbox schließt die Daten ab (`Finalizing`), lädt sie hoch und fährt herunter (`SHUTTING DOWN`). Mit Push-Benachrichtigungen kommen `Messung beendet` und `Neue Läufe hochgeladen`.

!!! warning "Messung vorzeitig beenden"

    Wer nicht warten will, beendet die Messung mit dem Fernbefehl [`Messung stoppen`](fernbefehle.md#messung-stoppen). Beim nächsten Einschalten startet die Messbox dann einmalig im manuellen Modus und misst erst nach `Messung starten`. Für die nächste Messfahrt sie einmal einschalten und wieder herunterfahren, oder im manuellen Modus `Messung starten` senden. Danach gilt wieder der Automatikmodus.

!!! tip "Weiter"

    Weiter zu [Nach dem Einsatz](abschluss.md).

# Fernbefehle

Mit Fernbefehlen lässt sich die Messbox aus dem Backend steuern, ohne am Gerät zu sein: Messung starten und stoppen, Daten hochladen, Gerät herunterfahren oder neu starten und den Modus umstellen. Wie die Modi funktionieren, steht unter [Wie die Messbox misst](messung.md#betriebsmodi).

Ein Befehl wird im Backend eingereiht und kommt mit dem nächsten Heartbeat des Geräts an, also nicht sofort. Das Gerät führt nur Befehle aus, die das Backend signiert hat.

!!! warning "Gerät reagiert auf keinen Befehl"

    Ist am Gerät kein Schlüssel für die Signaturprüfung eingerichtet, verwirft es alle Befehle und Konfigurationsänderungen, ohne dass das im Backend erkennbar ist. Reagiert eine Messbox nie auf Befehle, obwohl sie Heartbeats sendet, liegt es meist daran.

## Wo man sie findet

- Im Backend unter `Missionsstatus` im Abschnitt `Fernbefehle`: `Messung starten`, `Messung stoppen`, `Upload erzwingen`, `Neustart`, `Herunterfahren` und der Moduswechsel (`Automatikmodus`, `Manueller Modus`). Nicht umsetzbare Schaltflächen im aktuellen Zustand sind ausgegraut.
- Unter `Fernkonfiguration` im Abschnitt `Einmalbefehle`: alle Befehle der Übersicht außer den GPS-Fix-Tests. Diese sind unter `Testvisualisierung` zu finden.

## Übersicht

| Befehl | Wirkung | Wann möglich |
|---|---|---|
| `Messung starten` | Verlässt die Warteschleife, wartet auf einen GPS-Fix und beginnt dann mit der Messung | nur bei `Idle (manual)` oder `Idle (recovery)` |
| `Messung stoppen` | Beendet den laufenden Messlauf. Im Automatikmodus startet die Messbox danach einmalig im manuellen Modus | während `Measuring`, im manuellen Modus auch beim Warten auf den GPS-Fix nach `Messung starten` |
| `Upload erzwingen` | Lädt alle ausstehenden Messdateien hoch | jederzeit, sonst meldet das Gerät, dass nichts hochzuladen ist |
| `Herunterfahren` | Fährt das Gerät herunter. Es bleibt danach an der Stromversorgung und startet erst wieder, wenn man sie trennt und neu ansteckt | jederzeit |
| `Neustart` | Startet das Gerät neu | jederzeit |
| `Automatikmodus` / `Manueller Modus` | Stellt den Startmodus dauerhaft um, gilt erst beim nächsten Start | jederzeit |
| `Selbsttest starten` | Prüft, ob die Hardware erreichbar ist, ohne den Leerlauf zu verlassen | nur bei `Idle (manual)` |
| `GPS-Fix-Test starten` / `stoppen` | Live-Diagnose zur Suche einer guten Antennenposition | nur bei `Idle (manual)` |
| `SIM zurücksetzen` | Trennt die Steuerverbindung zum Modem, baut sie neu auf und entsperrt die SIM erneut. Sinnvoll, wenn das Modem keine Messwerte mehr liefert. Die mobile Datenverbindung selbst wird dabei nicht neu aufgebaut. Läuft gerade eine Messung, greift der Befehl bei der nächsten Abfrage | jederzeit |
| `Overrides übernehmen` | Schreibt die per Fernkonfiguration gesetzten Werte dauerhaft in die Konfigurationsdatei des Geräts, wirksam ab dem nächsten Start | jederzeit |

## Messung stoppen

`Messung stoppen` beendet den Lauf geordnet, genau wie das Stillstandsende bei einer Messfahrt: Das Gerät schließt die Messdaten ab, lädt sie hoch und fährt dann das Betriebssystem herunter.

Kommt der Befehl im manuellen Modus, während die Messbox nach `Messung starten` noch auf den GPS-Fix wartet, bricht er den Start ab. Die Messbox kehrt dann in den Leerlauf (`Idle (manual)`) zurück und fährt nicht herunter.

!!! info "Die Messbox bleibt am Strom"

    Heruntergefahren heißt nicht stromlos: Die Messbox hängt weiter an der Powerbank und zieht einen kleinen Ruhestrom. Nach dem Einsatz deshalb die Stromversorgung trennen, sobald die Messbox heruntergefahren ist, siehe [Nach dem Einsatz](abschluss.md). Zum Wiedereinschalten die Stromversorgung neu anstecken. Das gilt genauso für das Stillstandsende einer Bodenfahrt und für `Herunterfahren`.

!!! warning "Danach startet die Messbox einmal im manuellen Modus"

    Wurde die Messung im Automatikmodus gestoppt, startet die Messbox beim **nächsten** Hochfahren im manuellen Modus und misst erst nach `Messung starten`. So beginnt nicht gleich wieder eine Messung, wenn die Messbox nach dem Stopp noch bewegt wird. Ab dem übernächsten Start gilt wieder der Automatikmodus. Der eingestellte Modus selbst ändert sich dabei nicht. War die Messbox ohnehin im manuellen Modus, bleibt sie es.

Der Befehl geht nur während einer laufenden Messung bzw. im manuellen Modus beim Warten auf den GPS-Fix. Sonst meldet das Gerät `Nicht anwendbar`.

## Modus wechseln

Der Moduswechsel gilt erst beim **nächsten Start** der Messbox. In der Oberfläche lässt sich beim Wechsel `Anschließend neu starten` anhaken: Das Backend reiht dann nach dem Moduswechsel einen `Neustart` ein, sodass der neue Modus sofort gilt.

## Overrides

Per Fernkonfiguration geänderte Werte (`Overrides`) liegen auf dem Gerät in einer eigenen Datei, getrennt von der eigentlichen Konfiguration. Dadurch lassen sich alle Änderungen zurücknehmen, indem man diese Datei entfernt. `Overrides übernehmen` schreibt die Werte stattdessen dauerhaft in die Konfigurationsdatei des Geräts. Danach gelten sie als Grundeinstellung und überstehen auch das Entfernen der Override-Datei.

## Herunterfahren

Ein ausgeschaltetes Gerät kann das Herunterfahren nicht bestätigen. Das Backend wertet den Befehl deshalb als erfolgreich, wenn nach der Bestätigung eine Zeit lang kein Heartbeat mehr eingeht. Bis dahin steht der Befehl auf `Gesendet, wartet auf Gerät` bzw. `Noch online`. Meldet sich die Messbox nach dem nächsten Einschalten, bestätigt sie den Befehl außerdem nachträglich als erfolgreich.

## Status eines Befehls

Im Backend zeigt der `Befehlsstatus`, wie weit ein Befehl ist:

| Status | Bedeutung |
|---|---|
| `Wartet auf Zustellung` | Der Befehl liegt im Backend und wartet auf den nächsten Heartbeat |
| `Gesendet, wartet auf Gerät` | Der Befehl ist unterwegs |
| `Empfangen` | Das Gerät hat ihn erhalten |
| `Erfolgreich` | Das Gerät hat ihn ausgeführt |
| `Fehlgeschlagen` | Die Ausführung ist fehlgeschlagen |
| `Nicht anwendbar` | Das Gerät war nicht im passenden Zustand, z. B. `Messung stoppen` ohne laufende Messung |
| `Abgelaufen` | Der Befehl wurde nicht rechtzeitig zugestellt |

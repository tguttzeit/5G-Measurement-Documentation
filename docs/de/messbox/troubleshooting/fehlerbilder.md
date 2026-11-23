# Fehlerbilder

Die Fehlerbilder sind nach dem sortiert, was man vor Ort sieht: auf dem Display der Messbox, im Missionsstatus im Backend oder an fehlenden Daten. Zu jedem Fehlerbild gibt es die wahrscheinliche Ursache und was man vor Ort tun kann. Die Bedeutung der Anzeigen steht unter [Statusanzeige](../nutzung/messung.md#statusanzeige).

!!! question "Unbekannte Fehler"
    Auftretende Fehlerbilder, die im Folgenden nicht aufgelistet sind, bitte mit Datum und Uhrzeit möglichst genau dokumentieren, damit im Nachhinein anhand des Verhaltens und der Logs die Ursache und im besten Fall auch eine Lösung für das Problem gefunden werden kann.

## Kein GPS-Fix, Messung startet nicht

**Was man sieht:** Das Display zeigt `No GPS fix` und `GPS: no fix`, im Missionsstatus steht die Messbox auf `Warten auf GPS-Fix`. Im Automatikmodus endet der Durchlauf nach der `Max. Wartezeit auf ersten GPS-Fix` (Standard 300 s) ohne Messdaten. Im manuellen Modus wartet die Messbox nach `Messung starten` ohne Zeitgrenze weiter.

**Ursache:** Der GNSS-Empfänger findet keinen oder zu wenige Satelliten.

- Die Antenne braucht freie Sicht zum Himmel. Gebäude, Garagen, Metallgehäuse und Abschattung durch Fahrzeug oder Drohne verhindern den Empfang.
- Nach einem Kaltstart kann der erste Fix auch bei freier Sicht mehrere Minuten dauern.
- Elektronik in der Nähe der Antenne kann den Empfang stören, vor allem das Modem und USB-3.0-Anschlüsse.

**Was man tun kann:**

1. Die Messbox ins Freie bringen und einige Minuten warten, bevor man ein Problem annimmt.
2. Die Antenne anders platzieren. Dabei hilft der GPS-Fix-Test: Im Leerlauf des manuellen Modus (`Idle (manual)`) lässt sich im Backend unter `Testvisualisierung` (nur mit Superuser-Rechten) die Satellitenzahl live beobachten, siehe [Fernbefehle](../nutzung/fernbefehle.md#ubersicht).
3. Zeigt das Display unter der GPS-Zeile eine Diagnose (z. B. zu einem Antennenfehler), die Antenne und ihre Steckverbindung prüfen.

## Fix vorhanden, aber die Messung startet nicht

**Was man sieht:** Das Display zeigt `Waiting: move`, `Idle (manual)` oder `Idle (recovery)`.

**`Waiting: move`:** Die Messbox ist im Automatikmodus und wartet auf bestätigte Bewegung. Sie prüft die Position alle 45 s und braucht standardmäßig zwei Prüfungen in Folge, bei denen sie mindestens 10 m von der Position beim ersten Fix entfernt ist. Das heißt, nach der Abfahrt vergeht ungefähr anderthalb Minuten, bis die Messung startet. Ist eine Heimatposition eingestellt, muss sich die Messbox außerdem weit genug davon entfernt haben. Die Werte stehen in der [Konfiguration](../nutzung/konfiguration.md#bewegungserkennung-vor-dem-start).

!!! info "Werte"
    Die genannten Werte sind alle konfigurierbar, was bedeutet dass die verstreichende Zeit nach Abfahrt auch deutlich kürzer oder länger ausfallen kann!

**`Idle (manual)`:** Die Messbox ist im [manuellen Modus](../nutzung/messung.md#manueller-modus) und misst erst nach dem Fernbefehl `Messung starten`. Dort ist sie, wenn man sie in den manuellen Modus gestellt hat, oder einmalig nach `Messung stoppen` im Automatikmodus.

**`Idle (recovery)`:** Die Messbox hat sich nach wiederholten Fehlern neu gestartet und wartet einmalig auf `Messung starten`, siehe [Automatischer Neustart und `CRITICAL ERROR`](#automatischer-neustart-und-critical-error).

**Was man tun kann:**

- Im Backend `Messung starten` senden. Der Befehl kommt erst mit dem nächsten Heartbeat an, siehe [Fernbefehle](../nutzung/fernbefehle.md). Danach wartet die Messbox auf einen GPS-Fix und beginnt dann zu messen.
- Soll die Messbox künftig wieder von selbst starten, den Fernbefehl `Automatikmodus` senden. Er gilt ab dem nächsten Start.

## Keine Mobilfunkverbindung, Messbox meldet sich nicht im Backend

**Was man sieht:** Im Backend gibt es keine aktuellen Heartbeats, Fernbefehle und Änderungen kommen nicht an.

**Ursachen und Maßnahmen:**

- **SIM nicht eingesetzt oder gesperrt.** Lässt sich die SIM nicht entsperren, fährt die Messbox kurz nach dem Start herunter. SIM prüfen und neu einsetzen, SIM-PIN und SIM-Karte kontrollieren.
- **Funkloch oder hängende Verbindung.** Bleibt die Verbindung länger als 180 s weg, startet die Messbox den Verbindungsdienst selbst neu. Hilft das zweimal nicht, setzt sie zusätzlich das Funkmodul zurück. Bleibt die Verbindung weg, wiederholt sie diese Schritte in immer größeren Abständen (bis zu 30 min) und gibt nie auf. Eine laufende Messung geht währenddessen weiter, die Daten bleiben auf der Messbox und werden später hochgeladen.
- **Modem fällt aus.** Bricht die Verbindung zum Modem ab (z. B. durch Spannungseinbrüche), versucht die Messbox bis zu 10-mal, es wieder zu öffnen. Erst danach endet der Lauf mit einem Fehler. Die Stromversorgung prüfen, siehe [Akku und Stromversorgung](../wartung/stromversorgung.md).
- **Backend nicht erreichbar.** Antwortet das Backend nicht oder mit einem Serverfehler, liegt das Problem nicht an der Messbox. Die Messbox versucht es im nächsten Intervall erneut.
- **Zugangsdaten nicht passend.** Stimmen Geräte-ID oder Schlüssel nicht mit dem Backend überein, weist das Backend die Messbox mit „nicht autorisiert“ ab. Das muss an der Messbox oder im Backend korrigiert werden, siehe [Konfiguration](../nutzung/konfiguration.md#nur-an-der-messbox-einstellbar).
- **Befehle werden ignoriert, obwohl Heartbeats ankommen.** Siehe [Fernbefehle](../nutzung/fernbefehle.md): Ohne Signaturschlüssel verwirft die Messbox alle Befehle.

## Keine Daten im Backend nach einem Einsatz

Messdaten werden bei Beginn der Messung und nach dem Ende des Laufs hochgeladen, außerdem beim Herunterfahren oder Neustart und per Fernbefehl `Upload erzwingen`. Fehlen Daten, kommen diese Ursachen in Frage:

- **Die Messbox hatte keine Verbindung.** Die Daten bleiben auf der Messbox und werden hochgeladen, sobald wieder eine Verbindung besteht, spätestens beim nächsten Start. Messbox mit Verbindung einschalten und warten.
- **Die Messbox wurde nicht ordentlich beendet.** Beim Trennen der Stromzufuhr geht höchstens die letzte Zeile der Messpunkte verloren. Der Rest wird beim nächsten Start gesichert (`Recovering data`) und hochgeladen. Am besten die Stromzufuhr erst trennen, wenn das Display `SHUTTING DOWN` zeigt.
- **Es lief keine Messung.** Im manuellen Modus entsteht ohne `Messung starten` kein Lauf, im Automatikmodus ohne GPS-Fix oder Bewegung ebenfalls nicht. Siehe oben.
- **Das Backend lehnt die Daten ab.** Stimmt die Geräte-ID der Messdaten nicht mit der des angemeldeten Geräts überein, weist das Backend sie ab. Siehe [Konfiguration](../nutzung/konfiguration.md#nur-an-der-messbox-einstellbar).

Im Backend lässt sich unter `Messläufe` prüfen, welche Läufe angekommen sind.

## Messbox schaltet sich unerwartet ab oder startet neu

Das kann gewollt sein. Es gibt mehrere Gründe, warum sich die Messbox beendet:

- Sie beendet den Lauf im Automatikmodus, wenn 1800 s lang keine Bewegung erkannt wurde (siehe [Messfahrt](../nutzung/messfahrt.md#abschnitt-v-messung-beenden)). Im manuellen Modus passiert das nie.
- Sie wurde per Fernbefehl `Herunterfahren` oder `Neustart` beendet. Im Backend sind die Befehle im Befehlsstatus sichtbar.
- Die Stromzufuhr ist weggefallen oder zu schwach. Eine leere oder überlastete Powerbank kann zu Spannungseinbrüchen führen, ohne dass die Messbox sauber herunterfährt. Dann gehen die Messdaten nicht verloren, die Messbox sichert sie beim nächsten Start.
- Sie hat sich nach einem Fehler selbst neu gestartet, siehe nächster Abschnitt.

## Automatischer Neustart und `CRITICAL ERROR`

Tritt in der Software ein unerwarteter Fehler auf, startet sich die Messbox neu, statt stehen zu bleiben. Die Software merkt sich dabei, wie oft derselbe Fehler hintereinander auftrat, und eskaliert in drei Stufen:

1. **Neustart.** Beim ersten Fehler startet die Messbox neu und läuft normal weiter. Nach dem Neustart sieht man kurz `Recovering data`, wenn Daten gesichert werden müssen.
2. **Wiederherstellung.** Tritt derselbe Fehler 3-mal hintereinander auf (oder gab es 5 Neustarts in Folge), startet die Messbox einmalig im Wiederherstellungszustand. Das Display zeigt `Idle (recovery)`, im Backend erscheint ein Hinweis auf den Absturz. Die Messbox misst erst nach dem Fernbefehl `Messung starten`. Der Start danach ist wieder normal, der Modus bleibt unverändert.
3. **Wartungsmodus.** Tritt auch dann ein Fehler auf, startet die Messbox im Wartungsmodus. Im Backend meldet sie einen kritischen Fehler (`Missionsstatus`: `Kritischer Fehler`, Push-Benachrichtigung `Fehler`). Das Display wird in diesem Modus nicht mehr angesteuert und bleibt leer oder zeigt noch die letzte Anzeige vor dem Neustart. In diesem Modus misst sie nicht mehr. Es läuft nur noch die Mobilfunkverbindung, damit die Messbox für die Fehlersuche erreichbar bleibt.

Aus dem Wartungsmodus kommt man nicht per Fernbefehl heraus. Er wird am Gerät aufgehoben, nachdem die Ursache gefunden wurde.

Lässt sich schon die Konfiguration der Messbox nicht laden oder schlägt der Start vor der Messung fehl, geht die Messbox ohne Neustart direkt in den Wartungsmodus. Ist die Ursache behoben, startet sie beim nächsten Einschalten wieder normal. Kann sie die Konfiguration gar nicht laden, meldet sie sich dabei auch nicht im Backend und ist nur per SSH erreichbar.

**Was man tun kann:**

- Den Hinweis im `Missionsstatus` festhalten (Fehlerart, Zahl der Wiederholungen) und notieren, was die Messbox zuletzt gemacht hat und seit wann der Fehler auftritt.
- Die Messbox nicht wiederholt aus- und einschalten. Der Fehler bleibt bestehen, und die Messbox merkt sich ihren Zustand über Neustarts hinweg.
- Die Messbox an die für die Software zuständige Person melden. Die Fehlermeldung mit Fehlerart und Ablauf legt die Messbox bei jedem Absturz automatisch ab.

## `PIPELINE BROKEN`

**Was man sieht:** Das Display zeigt `PIPELINE BROKEN`, das Backend meldet die Messkette als defekt.

**Ursache:** Die Messbox hat bei Bewegung mehrere Messungen in Folge ohne Messwerte vom Modem erhalten (standardmäßig 3). Das passiert in einem Funkloch, aber auch bei einem Modem, das nicht mehr antwortet.

**Was man tun kann:**

- Die Fahrt oder den Flug kurz fortsetzen: Bei einem Funkloch erholt sich die Messkette von selbst.
- Bleibt die Anzeige, im Backend `SIM zurücksetzen` senden. Der Befehl baut die Verbindung zum Modem neu auf, siehe [Fernbefehle](../nutzung/fernbefehle.md#ubersicht).
- Hilft das nicht, die Messbox neu starten (`Neustart`) und die Stromversorgung prüfen.

Einzelne ungültige Messungen (`Inv` auf dem Display) sind normal. Sie sind erst ein Problem, wenn `PIPELINE BROKEN` erscheint.


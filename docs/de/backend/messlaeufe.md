# Messläufe und Kampagnen

Ein Messlauf ist eine Messfahrt oder ein Messflug einer Messbox, vom Start der Messung bis zum Abschluss. Die Messbox vergibt jedem Lauf eine eigene Kennung und schickt sie mit den Messdaten hoch. Das Backend legt den Lauf beim ersten Upload an.

Kampagnen fassen mehrere Läufe zusammen, etwa alle Fahrten eines Messeinsatzes. Die öffentliche Karte zeigt immer genau eine Kampagne, siehe [Karte und Export](karte.md).

## Prüfen, ob die Daten angekommen sind

Nach einem Upload erscheint bei Superusern eine Benachrichtigung mit der Anzahl der Messpunkte. `In Messläufen ansehen` öffnet die Liste.

Ohne Benachrichtigung: Unter `Messläufe` nach der Geräte-ID filtern und nach `Start` sortieren. Der neueste Lauf steht oben. Stimmen Startzeit, Dauer und Anzahl der Punkte mit dem Einsatz überein, sind die Daten vollständig angekommen. Fehlt der Lauf, zeigt der [Missionsstatus](missionsstatus.md) unter `Ausstehende Dateien`, ob die Messbox noch Daten zurückhält.

## Die Liste

`Messläufe` ist für alle angemeldeten Nutzer sichtbar. Jede Zeile ist ein Lauf mit Messbox, Mission (`Boden` oder `Drohne`), Start, Ende, Dauer, Anzahl der Punkte, den Mittelwerten von RSRP, RSRQ und SINR und der Kampagne.

- **Filter:** Geräte-ID, Missionstyp, Kampagne (auch `Nicht zugeordnet`) und Startzeitraum
- **Sortierung:** nach `Start`, `Dauer` oder `Punkte`
- **`Auf Karte zeigen`:** öffnet die Karte mit nur diesem Lauf

Hat ein Lauf einen Namen, steht der Name in der Spalte `Lauf` und die Kennung der Messbox klein darunter.

Läufe mit dem Zusatz `Altbestand` stammen aus Daten, die vor der Einführung von Messläufen hochgeladen wurden. Das Backend hat sie nachträglich pro Messbox, Missionstyp und Tag zusammengefasst. Ein Altbestand-Lauf kann deshalb mehrere echte Fahrten eines Tages enthalten.

## Läufe bearbeiten und löschen

Superuser können Läufe bearbeiten und löschen.

- **`Bearbeiten`:** Name, Missionstyp und Kampagne ändern. Geräte-ID und Lauf-ID vergibt die Messbox, sie lassen sich nicht ändern. Spätere Uploads zum selben Lauf überschreiben die Änderungen nicht.
- **Mehrere Läufe auf einmal:** Läufe über die Kästchen auswählen und `Auswahl bearbeiten` wählen. Geändert werden nur die ausgefüllten Felder, alles auf `Beibehalten` bleibt wie es ist.
- **`Löschen`:** verschiebt den Lauf mit allen Messungen und Latenzergebnissen in den Papierkorb. Er ist dann überall ausgeblendet, auch auf der Karte.

### Papierkorb

Gelöschte Läufe liegen mit allen Daten im `Papierkorb`, erreichbar über die Schaltfläche `Papierkorb` unter `Messläufe`. Dort steht für jeden Lauf, wann und von wem er gelöscht wurde.

- **`Wiederherstellen`:** holt den Lauf mit allen Daten zurück in die Liste.
- **`Endgültig löschen`:** entfernt den Lauf mit allen Messungen und Latenzergebnissen dauerhaft.

Lädt eine Messbox noch Daten zu einem Lauf im Papierkorb hoch, bleiben sie erhalten und landen ebenfalls im Papierkorb.

!!! warning "Endgültiges Löschen lässt sich nicht rückgängig machen"

    Ein endgültig gelöschter Lauf ist mit allen Messdaten weg. Lädt die Messbox danach noch Daten zu diesem Lauf hoch, legt das Backend ihn neu an, aber nur mit diesen neuen Daten.

## Kampagnen verwalten

Kampagnen verwalten Superuser unter `Kampagnenverwaltung`.

- **Anlegen:** nur einen Namen vergeben, z. B. `sommer-2026`. Einen Zeitraum gibt es nicht einzustellen, er ergibt sich aus den Läufen der Kampagne.
- **Läufe zuordnen:** Bei der Kampagne `Läufe verwalten` öffnen. Oben stehen die Läufe der Kampagne, darunter die Läufe, die sich hinzufügen lassen. Standardmäßig sind das nur Läufe ohne Kampagne. Mit `Läufe anderer Kampagnen einbeziehen` lassen sich auch Läufe aus einer anderen Kampagne herüberholen.
- **Umbenennen und Löschen:** über `Bearbeiten` und `Löschen`. Beim Löschen einer Kampagne bleiben ihre Läufe erhalten und sind danach `Nicht zugeordnet`.

Ein Lauf gehört zu höchstens einer Kampagne. Neue Läufe sind zunächst keiner Kampagne zugeordnet. Die Zuordnung geht auch direkt in der Liste über `Bearbeiten` oder `Auswahl bearbeiten`.

!!! info "Auswirkung auf die öffentliche Karte"

    Ohne Anmeldung zeigt die Karte die Kampagne mit dem jüngsten Messpunkt. Wer einen neuen Lauf einer Kampagne zuordnet, kann damit ändern, welche Kampagne Gäste zuerst sehen. Läufe ohne Kampagne erscheinen auf der öffentlichen Karte gar nicht.

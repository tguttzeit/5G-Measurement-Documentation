# Nach dem Einsatz

Hier laufen Messfahrt und Messflug wieder zusammen.

## Anleitung

### Abschnitt I – Messbox vom Strom trennen

1. Warten, bis das Display `SHUTTING DOWN` zeigt. Nach dem Herunterfahren bleibt diese Anzeige oft stehen.
2. Beide Kabel von der Powerbank abziehen. Heruntergefahren heißt nicht stromlos: Solange die Kabel stecken, zieht die Messbox weiter einen kleinen Ruhestrom.

!!! note "Zu früh getrennt?"

    Wird der Strom zu früh getrennt, ist das nicht weiter schlimm. Im Zweifel geht die zuletzt gespeicherte Zeile der Messpunkte verloren. Der Rest bleibt auf der Messbox und wird bei einem späteren Lauf hochgeladen.

### Abschnitt II – Abbauen und laden

1. Messbox, Antenne und Halterungen abbauen.
2. Die Powerbank laden.

### Abschnitt III – Daten prüfen

1. Prüfen, ob die Daten im Backend angekommen sind:
    - Mit Push-Benachrichtigungen kommt `Neue Läufe hochgeladen`.
    - Sonst im Backend unter `Messläufe` nachsehen, siehe [Prüfen, ob die Daten angekommen sind](../../backend/messlaeufe.md#prufen-ob-die-daten-angekommen-sind).
2. Fehlt ein Lauf, liegen die Daten noch auf der Messbox. Eine Datei wird dort erst nach erfolgreichem Upload gelöscht. Hochgeladen wird sie,
    - wenn beim nächsten Einsatz die Messung beginnt oder endet, oder
    - sofort, wenn man die Messbox einschaltet und im Backend den Fernbefehl `Upload erzwingen` sendet.

!!! tip "Fertig"

    Der Einsatz ist abgeschlossen. Vor dem nächsten Einsatz geht es wieder bei [Messbox vorbereiten](vorbereitung.md) los.

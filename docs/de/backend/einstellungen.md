# Einstellungen

Unter `Einstellungen` im Menü liegen die Sprache, die Push-Benachrichtigungen und für Superuser zwei Einstellungen des Backends. Ohne Anmeldung ist nur die Sprache verfügbar.

## Sprache und Darstellung

Die Oberfläche gibt es auf Deutsch und Englisch. Die Sprache wird unter `Einstellungen` oder, ohne Anmeldung, oben rechts gewählt. Sie gilt nur für den Browser, in dem sie eingestellt wurde.

Hell oder dunkel lässt sich im Menü unter `Darstellung` umstellen (`System`, `Hell`, `Dunkel`).

## Push-Benachrichtigungen

Das Backend kann bei bestimmten Ereignissen eine Nachricht aufs Smartphone oder an den Desktop schicken. Zugestellt wird über [ntfy](https://ntfy.sh), dafür braucht es die ntfy-App. Benachrichtigungen sind aus, bis man sie einschaltet, und gelten für alle Messboxen.

### Einrichten

1. `Benachrichtigungen senden` einschalten und die gewünschten Ereignisse wählen, dann speichern.
2. Die ntfy-App installieren und dort das angezeigte Thema abonnieren, auf dem Server, den die Seite nennt. `Thema kopieren` kopiert es in die Zwischenablage.
3. Mit `Testbenachrichtigung senden` prüfen, ob die Nachricht ankommt. Danach muss man einige Sekunden warten, bevor die nächste geht.

Dasselbe Thema lässt sich auf mehreren Geräten abonnieren.

### Ereignisse

| Ereignis | Wann |
|---|---|
| `Messbox gestartet` | Eine Messbox meldet sich nach mindestens drei ausgebliebenen Heartbeats wieder, also nach dem Einschalten oder einem Neustart |
| `Messung gestartet` | Eine Messbox wechselt in `Messung läuft` |
| `Messung beendet` | Eine Messbox verlässt `Messung läuft` |
| `Neue Läufe hochgeladen` | Messdaten sind im Backend angekommen |
| `Fehler` | Eine Messbox geht in den Wartungsmodus (`CRITICAL ERROR`), die Messkette liefert trotz Bewegung keine Messungen mehr, oder ein Fernbefehl ist fehlgeschlagen |

Gemeldet wird nur der Wechsel. Bleibt eine Messbox in einem Zustand, kommt keine zweite Nachricht.

!!! warning "Das Thema ist das Passwort"

    Wer das Thema kennt, kann alle Benachrichtigungen mitlesen. Sie enthalten Geräte-ID, Ereignis und Uhrzeit und laufen über den ntfy-Server, nicht nur über das Backend. Das Thema also nicht weitergeben. Ist es doch bekannt geworden, mit `Thema neu erzeugen` ein neues anlegen und dieses in der App neu abonnieren. Das alte funktioniert danach nicht mehr.

## Nur für Superuser

### Limit für Rohdatenpunkte

Legt fest, wie viele einzelne Punkte die [Karte](karte.md) angemeldeten Nutzern in der Darstellung `Punkte` höchstens liefert. Standard ist `Unbegrenzt`. Ein Limit hilft, wenn die Karte bei großen Datenmengen zu langsam wird. Für Gäste gilt unabhängig davon immer ein festes Limit von 5000 Punkten.

### Herunterfahren bestätigen

Eine heruntergefahrene Messbox kann nicht mehr melden, dass sie aus ist. Das Backend wertet `Herunterfahren` deshalb als erfolgreich, wenn nach der Bestätigung des Befehls eine bestimmte Zeit lang kein Heartbeat mehr kommt, siehe [Fernbefehle](../messbox/nutzung/fernbefehle.md#herunterfahren). Diese Zeit wird hier eingestellt:

- `Heartbeat-Intervalle`: 1 bis 20 Intervalle der jeweiligen Messbox, Standard 4
- `Feste Zeitspanne`: 10 bis 3600 Sekunden

Ist die Zeitspanne kürzer als ein Heartbeat-Intervall, warnt die Seite: Eine Messbox, die noch läuft, könnte dann fälschlich als heruntergefahren gelten.

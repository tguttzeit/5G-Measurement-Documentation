# Backend

Das Backend empfängt die Heartbeats und Messdaten der Messboxen, zeigt sie an und schickt Fernbefehle und Konfigurationsänderungen an die Geräte. 
## Rollen

Ohne Anmeldung ist nur die Karte sichtbar. Alles andere setzt ein Konto voraus, Steuerung und Verwaltung zusätzlich Superuser-Rechte.

| Bereich | Gast | Angemeldet | Superuser |
|---|---|---|---|
| `Karte / Heatmap` | eine Kampagne, ohne Gerätefilter, höchstens 5000 Rohdatenpunkte | alle Kampagnen und `Gesamter Zeitraum`, Gerätefilter | wie angemeldet |
| `Missionsstatus` | – | Zustand der Geräte | zusätzlich `Fernbefehle` und `Befehlsstatus` |
| `Messläufe` | – | ansehen | bearbeiten, in den Papierkorb verschieben, wiederherstellen und endgültig löschen |
| `Testvisualisierung` | – | – | ja |
| `Einstellungen` | Sprache | zusätzlich Push-Benachrichtigungen | zusätzlich Datenpunkt-Limit und Herunterfahren-Bestätigung |
| `Fernkonfiguration`, `Kampagnenverwaltung`, `Benutzerverwaltung` | – | – | ja |

Benachrichtigungen über Uploads und Befehlsbestätigungen erscheinen nur bei Superusern.

## Anmelden

Oben rechts auf `Anmelden` klicken und Benutzername und Passwort eingeben. Nach der Anmeldung öffnet sich über den eigenen Namen oben rechts das Menü mit allen Seiten, die die Rolle erlaubt.

Die Sitzung läuft nach einiger Zeit ab (Standard 30 min). Das Backend leitet dann auf die Anmeldung zurück, danach geht es auf der zuvor geöffneten Seite weiter.

## Passwort ändern

Unter `Passwort ändern` im Menü. Das neue Passwort braucht mindestens 8 Zeichen. Nach 5 falschen Eingaben des aktuellen Passworts ist die Änderung gesperrt. Die Sperre hebt eine erfolgreiche Anmeldung auf, oder ein Superuser setzt das Passwort neu.

## Konten verwalten

Superuser legen unter `Benutzerverwaltung` Konten an, machen sie zu Superusern, deaktivieren oder löschen sie. Die eigenen Rechte lassen sich dort nicht ändern, das eigene Konto weder deaktivieren noch löschen.

Konten für Messboxen sind etwas anderes: Geräte werden nicht in der Oberfläche angelegt, sondern auf dem Server, siehe [Gerät registrieren](dev/geraet-registrieren.md).

## Wo was steht

- Zustand einer Messbox: [Missionsstatus](missionsstatus.md)
- Selbsttests und GPS-Fix-Test: [Testvisualisierung](testvisualisierung.md)
- Prüfen, ob Messdaten angekommen sind: [Messläufe und Kampagnen](messlaeufe.md)
- Messergebnisse ansehen und exportieren: [Karte und Export](karte.md)
- Messbox aus der Ferne steuern: [Fernbefehle](../messbox/nutzung/fernbefehle.md)
- Einstellungen der Messbox ändern: [Konfiguration](../messbox/nutzung/konfiguration.md#fernkonfiguration-im-backend)
- Push-Benachrichtigungen und Sprache: [Einstellungen](einstellungen.md)

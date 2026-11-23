# Testvisualisierung

Die `Testvisualisierung` sammelt die Ergebnisse der Selbsttests aller Messboxen. Ein Selbsttest prüft, ob die Hardware der Messbox erreichbar ist und funktioniert, ohne eine Messung zu starten. Die Seite ist nur für Superuser nutzbar.

## Selbsttest auslösen

Ein Selbsttest wird über den [Fernbefehl](../messbox/nutzung/fernbefehle.md) `Selbsttest starten` ausgelöst, unter `Fernkonfiguration` im Abschnitt `Einmalbefehle`. Das geht nur im Leerlauf des manuellen Modus (`Idle (manual)`). Die Messbox bleibt dabei im Leerlauf.

Die Messbox führt alle Tests nacheinander aus und meldet jedes Ergebnis, sobald der Test fertig ist. Nach dem Test erscheint eine Benachrichtigung mit einem Link auf diese Seite.

Ein Selbsttest, der direkt an der Messbox über die Kommandozeile gestartet wird, landet ebenfalls hier, siehe [Messbox aufsetzen](../messbox/dev/messbox-aufsetzen.md#verkabelung-vor-dem-ersten-lauf-prufen).

## Die Tests

| Test | Was geprüft wird | Häufige Ursache bei `fehlgeschlagen` |
|---|---|---|
| `Modem` | Das Modem lässt sich öffnen und liefert auf eine Abfrage Zellmessungen. | Modem nicht erkannt, SIM gesperrt oder nicht entsperrt |
| `GPS` | Der GNSS-Empfänger liefert innerhalb von 5 Sekunden eine Position. | Antenne ohne freie Sicht zum Himmel, z. B. in Gebäuden; Antenne nicht angeschlossen |
| `Collector` | Modem und GNSS-Empfänger arbeiten zusammen: Eine Zellmessung lässt sich mit einer Position verbinden. Gespeichert wird dabei nichts. | wie bei `Modem` oder `GPS` |
| `Uploader` | Die Messbox hat eine Netzwerkverbindung (WLAN oder Mobilfunk) mit IP-Adresse. Hochgeladen wird beim Fernbefehl nichts. | keine Mobilfunkverbindung, kein WLAN |
| `Heartbeat` | Die Messbox kann einen Heartbeat an das Backend senden. | Backend nicht erreichbar, falsche Backend-Adresse |

Ist eine Funktion in der Konfiguration der Messbox abgeschaltet, etwa der Heartbeat, endet der zugehörige Test mit `übersprungen`. Der Grund steht dann in der Spalte `Fehlermeldung`.

Die Messbox prüft zusätzlich Display, Keep-Alive der Mobilfunkverbindung und Latenztest. Diese Ergebnisse stehen nur im Log der Messbox, nicht im Backend.

## Ergebnisse lesen

Die Tabelle `Testergebnisse` zeigt jeden einzelnen Test mit Testtyp, Status, Messbox, Zeitpunkt, Dauer und Fehlermeldung. Über die Filter lässt sie sich nach Testtyp, Status, Geräte-ID und Zeitraum eingrenzen.

| Status | Bedeutung |
|---|---|
| `bestanden` | Der Test war erfolgreich |
| `fehlgeschlagen` | Der Test ist gescheitert, die Ursache steht unter `Fehlermeldung` |
| `übersprungen` | Der Test wurde nicht ausgeführt, weil die Funktion abgeschaltet ist |

Die Spalte `Typ` zeigt bei Selbsttests der Messbox immer `Test`. Damit sind die Ergebnisse von echten Messdaten getrennt.

Die `Testzusammenfassung` darüber zeigt die Erfolgsquote, die Ergebnisse nach Testtyp, die letzten Fehlschläge und die letzten Ausführungen.

Mit `Auswahl löschen` und `Alle löschen` lassen sich Ergebnisse entfernen. Das lässt sich nicht rückgängig machen.

## GPS-Fix finden

Der GPS-Fix-Test hilft, eine gute Position für die GPS-Antenne zu finden. Er läuft nur im Leerlauf des manuellen Modus (`Idle (manual)`). Im aufklappbaren Abschnitt `GPS-Fix finden` die Messbox wählen und den Test mit `GPS-Fix-Test starten` beginnen, mit `GPS-Fix-Test stoppen` beenden.

Während der Test läuft, zeigt die Seite laufend die Anzahl der Satelliten, ob ein Fix besteht und wie lange der Test schon läuft. Die Messbox meldet etwa alle 2 Sekunden. Gezählt werden alle sichtbaren Satelliten, die Zahl ändert sich also schon, bevor ein Fix besteht. So lässt sich die Antenne umsetzen und direkt sehen, ob die neue Position besser ist.

Nach 5 Minuten beendet die Messbox den Test von selbst. Ein gefundener Fix erscheint auch auf dem Display und im `Missionsstatus`.

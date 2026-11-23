# Messbox vorbereiten

Vor jedem Einsatz wird die Messbox einmal angeschlossen, ihre Verbindung zum Backend geprüft und die Konfiguration auf den Einsatz abgestimmt. Am besten erledigt man das vor der Anfahrt zum Einsatzort. Am Ende dieser Seite wählt man Messfahrt oder Messflug. Die Einstellungen, die nur für eine der beiden Einsatzarten gelten, stehen am Anfang der jeweiligen Seite.

## Was man braucht

- Messbox mit Antenne, Powerbank und beiden USB-Kabeln
- Backend-Konto mit Superuser-Rechten: Nur damit sind `Fernkonfiguration` und `Fernbefehle` zugänglich
- Optional: Smartphone mit der App [ntfy](https://ntfy.sh)
- Optional: LAN-Kabel, wenn die Messbox ohne Mobilfunk ans Netz soll

## Anleitung

### Abschnitt I – Push-Benachrichtigungen einrichten

Einmalig pro Konto und Smartphone. Wer das schon eingerichtet hat, macht mit [Abschnitt II](#abschnitt-ii-messbox-anschlieen) weiter.

Das Backend meldet über ntfy, wenn die Messbox sich meldet, eine Messung startet oder endet, Daten hochgeladen sind oder ein Fehler auftritt. So sieht man im Feld, ohne ins Backend zu schauen, ob alles läuft.

1. Im Backend unter `Einstellungen` die Push-Benachrichtigungen einschalten, siehe [Push-Benachrichtigungen](../../backend/einstellungen.md#push-benachrichtigungen).
2. Das angezeigte Thema in der ntfy-App abonnieren.
3. Mit `Testbenachrichtigung senden` prüfen, ob die Nachricht auf dem Smartphone ankommt.

### Abschnitt II – Messbox anschließen

1. Die Powerbank laden, falls nötig.
2. Die Messbox mit dem Internet verbinden. Dafür gibt es zwei Wege:
    - **Über Mobilfunk:** Die Antenne anschließen. Die Stecker sind wie folgt belegt:

        ![Belegung der Antennenanschlüsse an der Messbox](../../../images/5gmu_antenna_ports.svg)

    - **Über LAN:** Die Messbox aufschrauben (4x M3-Schrauben auf der Seite gegenüber den Anschlüssen) und das LAN-Kabel in den Port des Raspberry Pi stecken. Er ist gut erreichbar, sobald die Box offen ist.
3. Die Messbox an die Powerbank anschließen, zuerst mit dem USB-A-zu-USB-A-Kabel (Stromversorgung des Modems), dann mit dem USB-C-zu-USB-C-Kabel (Raspberry Pi). Es müssen **beide** Kabel stecken. Der Raspberry Pi startet, sobald das USB-C-Kabel steckt.
4. Die Software startet dann automatisch. Warten, bis das Display etwas anzeigt. Das dauert etwa 10 s, ab dann ist die Software gestartet. 
5. Im Backend unter `Missionsstatus` prüfen, ob die Messbox als online angezeigt wird und Heartbeats sendet. Mit Push-Benachrichtigungen kommt außerdem `Messbox gestartet`.
    - Bleibt die Messbox offline, siehe [Troubleshooting](../troubleshooting/fehlerbilder.md).

### Abschnitt III – Allgemeine Einstellungen prüfen

Die Standardeinstellungen passen für die meisten Einsätze. Geändert wird im Backend unter `Fernkonfiguration`, siehe [Fernkonfiguration im Backend](konfiguration.md#fernkonfiguration-im-backend).

1. Im Backend `Fernkonfiguration` öffnen und die Messbox auswählen.
2. In der Spalte `Aktuell` nachsehen, was die Messbox gerade verwendet, und prüfen, ob eine der folgenden Situationen zutrifft:

    | Wenn … | dann anpassen |
    |---|---|
    | die Messbox in einer Garage oder auf einem Gelände mit schlechtem GPS-Empfang startet | `Max. Wartezeit auf ersten GPS-Fix` |
    | die Messbox ohne Display betrieben wird | `Display aktiviert` |

3. Die Seite offen lassen: Am Anfang von Messfahrt bzw. Messflug folgen die Einstellungen für die jeweilige Einsatzart. Erst danach wird die Messbox neu gestartet, damit alle Änderungen gelten.

!!! info "Änderungen gelten erst nach einem Neustart"

    Die Messbox übernimmt Änderungen nie während eines laufenden Durchlaufs. Sie kommen mit dem nächsten Heartbeat an und gelten ab dem nächsten Start. Danach bleiben sie bestehen, auch über Herunterfahren und Stromtrennung hinweg, bis man sie im Backend wieder ändert.

### Abschnitt IV – Einsatzart wählen

<div class="grid cards" markdown>

-   :material-car: **[Messfahrt](messfahrt.md)**

    ---

    Messung vom Fahrzeug aus. Die Messbox startet und beendet die Messung selbst (Automatikmodus).

-   :material-quadcopter: **[Messflug](messflug.md)**

    ---

    Messung mit der DJI Matrice 300 RTK. Die Messung wird per Fernbefehl gestartet und beendet (manueller Modus).

</div>

# Nutzung

Diese Anleitung führt Schritt für Schritt durch einen Einsatz der Messbox: Vorbereiten, Montieren, Messen und Prüfen der Daten im Backend. Diese Seite erklärt, was für jeden Einsatz gilt. Danach geht es mit der [Vorbereitung](vorbereitung.md) weiter, an deren Ende sich der Weg in Messfahrt (Fahrzeug) und Messflug (Drohne) teilt. Beide Wege enden auf der Seite [Nach dem Einsatz](abschluss.md).

!!! info "Vor dem ersten Einsatz vollständig lesen"

    Wer die Messbox zum ersten Mal einsetzt, sollte diese Seite und die Vorbereitung ganz lesen und die aufklappbaren Abschnitte unten öffnen. Wer sie schon kennt, kann direkt zur [Vorbereitung](vorbereitung.md) springen.

!!! danger "Die Messbox ist nicht wasserdicht"

    Bei Regen, Nebel oder ähnlichem ist ein Einsatz nicht möglich.

## Was die Messbox macht

Die Messbox misst unterwegs die Qualität des Mobilfunknetzes (5G und LTE) zusammen mit der Position und optional der Latenz. Die Daten werden an das Backend geschickt. Nach dem Einschalten arbeitet sie ohne Bedienung am Gerät:

1. Sie baut die Mobilfunkverbindung auf und meldet sich beim Backend. Sie ist dort also schon vor dem Messstart sichtbar.
2. Sie wartet auf einen GPS-Fix.
3. Sie startet die Messung: im Automatikmodus von selbst, sobald sie sich bewegt, im manuellen Modus erst auf den Fernbefehl `Messung starten`.
4. Sie misst und speichert fortlaufend.
5. Sie beendet die Messung, lädt die Daten hoch und fährt herunter.

Welche Werte gemessen werden und was sie aussagen, steht unter [Was gemessen wird](messwerte.md).

??? info "Was man braucht"

    - Messbox mit Antenne
    - Powerbank: `Anker Prime 20000mAh` für das Fahrzeug, `INIU Powerbank` für die Drohne
    - ein USB-A-zu-USB-A-Kabel (Stromversorgung des Modems) und ein USB-C-zu-USB-C-Kabel (Stromversorgung des Raspberry Pi)
    - Fahrzeug: Magnethalterung der Antenne
    - Drohne (DJI Matrice 300 RTK): Adapterplatte oder Doppelhalterung, M2- und M3-Schrauben, wiederverwendbare Kabelbinder, passendes Werkzeug (Innensechskant-Schlüssel oder Schraubendreher für M2 und M3 Schrauben)
    - Ein Konto im Backend, für Fernbefehle und Konfiguration mit Superuser-Rechten (siehe [Rollen](../../backend/index.md#rollen))
    - Optional: Smartphone mit der App [ntfy](https://ntfy.sh) für Push-Benachrichtigungen
    - Optional: LAN-Kabel, um die Messbox ohne Mobilfunk mit dem Backend zu verbinden

??? info "Begriffe"

    Backend
    :   Die Weboberfläche zur Messbox. Dort sieht man, ob eine Messbox online ist, steuert sie aus der Ferne und findet die Messdaten. Siehe [Backend](../../backend/index.md).

    Missionsstatus
    :   Seite im Backend mit dem aktuellen Zustand jeder Messbox und den Fernbefehlen.

    Heartbeat
    :   Regelmäßige Statusmeldung der Messbox an das Backend. Fernbefehle und Konfigurationsänderungen kommen mit dem nächsten Heartbeat bei der Messbox an, also nicht sofort.

    GPS-Fix
    :   Die Messbox kennt ihre Position aus Satellitensignalen. Ohne Fix wird nicht gemessen. Dafür braucht die Antenne freie Sicht zum Himmel.

    Fernbefehl
    :   Befehl aus dem Backend an die Messbox, z. B. `Messung starten` oder `Herunterfahren`. Siehe [Fernbefehle](fernbefehle.md).

    Fernkonfiguration
    :   Einstellungen der Messbox im Backend ändern, ohne an das Gerät zu müssen. Änderungen gelten erst nach dem nächsten Start. Siehe [Konfiguration](konfiguration.md).

    Messlauf
    :   Die Daten einer Messung vom Start bis zum Ende. Im Backend unter `Messläufe` zu finden.

??? info "Betriebsmodi"

    Die Messbox startet in einem von zwei Modi:

    - **Automatikmodus** (Standard, für Messfahrten): Die Messung startet von selbst, sobald sich die Messbox bewegt, und endet von selbst nach längerem Stillstand.
    - **Manueller Modus** (für Messflüge oder die Fehlersuche): Die Messbox verbindet sich, misst aber erst nach dem Fernbefehl `Messung starten` und nur bis `Messung stoppen`.

    Der Modus wird per Fernbefehl umgestellt und gilt erst nach dem nächsten Start. Nach `Messung stoppen` im Automatikmodus startet die Messbox einmalig im manuellen Modus, danach wieder im Automatikmodus. Ausführlich unter [Wie die Messbox misst](messung.md#betriebsmodi).

??? info "Statusanzeige"

    Das Display der Messbox zeigt den Zustand, den GPS-Empfang und die Zahl der Messpunkte. Dieselben Zustände stehen im Backend unter `Missionsstatus`. Was die Anzeigen bedeuten, steht unter [Statusanzeige](messung.md#statusanzeige). Die Informationen, die auf dem Display angezeigt werden, sind aber auch der Missionsstatus-Seite zu entnehmen, solange kein Fehler auftritt, der die Internetverbindung beeinträchtigt.

??? info "Hilfe bei Problemen"

    Was eine Anzeige bedeutet und was man vor Ort tun kann, steht unter [Troubleshooting](../troubleshooting/fehlerbilder.md).

## Zum Nachschlagen

Diese Seiten gehören nicht zum Ablauf, erklären aber Hintergründe:

- [Wie die Messbox misst](messung.md): Betriebsmodi, Phasen eines Laufs, Statusanzeige, Hochladen der Daten
- [Was gemessen wird](messwerte.md): Signalwerte, Position, Latenz und Durchsatz
- [Fernbefehle](fernbefehle.md): alle Befehle aus dem Backend
- [Konfiguration](konfiguration.md): alle Einstellungen und wie Änderungen zur Messbox kommen

!!! tip "Weiter"

    Weiter zu [Messbox vorbereiten](vorbereitung.md).

# Konfiguration

Die Standardeinstellungen der Messbox sind für Messfahrten mit dem Auto ausgelegt. Meistens muss vor einem Einsatz nichts geändert werden. Für Messflüge und für besondere Anforderungen lassen sich viele Einstellungen im Backend unter `Fernkonfiguration` anpassen, ohne dass man an die Messbox muss.

## Wo Einstellungen liegen

Die Messbox setzt ihre Konfiguration aus mehreren Quellen zusammen. Spätere Quellen überschreiben frühere:

1. **Grundkonfiguration** (`config.toml`): die Standardwerte der Software.
2. **Geräteeigene Werte** (`config.local.toml`): Identität und Zugangsdaten der einzelnen Messbox, einmalig bei der Einrichtung von Hand gesetzt.
3. **Fernkonfiguration** (`config_overrides.toml`): Änderungen aus dem Backend, hier `Overrides` genannt.

Nicht alles lässt sich aus der Ferne ändern. Geräteidentität, Zugangsdaten und Adressen sind von der Fernkonfiguration dauerhaft ausgenommen. Das gilt auch für den Betriebsmodus, der über [Fernbefehle](fernbefehle.md#modus-wechseln) umgestellt wird.

!!! info "Änderungen gelten erst nach dem nächsten Start"

    Die Messbox übernimmt Overrides nie während eines laufenden Durchlaufs, sondern erst beim **nächsten Start**. Wer vor einem Einsatz etwas ändert, sollte die Messbox danach neu starten, z. B. mit dem Fernbefehl `Neustart`.

## Vor einem Einsatz prüfen

Die folgenden Einstellungen sind für Einsätze am ehesten relevant. Alle anderen können in der Regel bei den Standardwerten bleiben.

| Wenn … | dann prüfen |
|---|---|
| die Messdichte angepasst werden soll (z. B. bei Messflügen) | [Messintervall und Rasterdichte](#messintervall-und-rasterdichte) |
| Stillstand (Ampel, Stau, Pausen) im Automatikmodus nicht zum Ende des Laufs führen soll | `Leerlaufschwelle` |
| die Messbox in einer Garage oder auf einem Gelände mit schlechtem GPS-Empfang startet | `Max. Wartezeit auf ersten GPS-Fix` |
| die Messbox ohne Display betrieben wird | `Display aktiviert` |

### Messintervall und Rasterdichte

Wie dicht die Messpunkte liegen, hängt vom `Aufnahme-Auslöser` ab:

- Bei `distance` (Standard) wird nach einer zurückgelegten Strecke gemessen. Die Strecke legt die `Positionsschwelle` fest, Standard sind 15 m.
- Bei `time` wird in einem festen Zeitabstand gemessen, unabhängig von der Bewegung. Der Abstand ist das `Aufnahmeintervall`, Standard sind 15 s.

Bei Messflügen sollte die Rasterdichte mit dem Fernpiloten abgesprochen und die Einstellung darauf abgestimmt werden. Zwei Beispiele:

- Fliegt die Drohne ein Raster mit festem Abstand der Bahnen und bekannter Geschwindigkeit, ist `time` mit einem passenden `Aufnahmeintervall` einfach zu planen.
- Soll nach Strecke gemessen werden, muss die `Positionsschwelle` zum geplanten Abstand der Messpunkte passen. Sehr kleine Werte liegen im Bereich der GPS-Ungenauigkeit und zählen dann Rauschen als Bewegung.

Kleinere Abstände liefern eine dichtere Abdeckung, erzeugen aber mehr Daten und mehr Abfragen am Modem.

#### Flug planen

Für Messflüge gibt es einen Rechner, der aus Fluggeschwindigkeit, Raster und Gebiet das passende `Aufnahmeintervall` bzw. die `Positionsschwelle` bestimmt, siehe [Raster planen](messflug.md#raster-planen).

## Fernkonfiguration im Backend

Die Seite `Fernkonfiguration` ist nur für Nutzer mit Superuser-Rechten zugänglich. Sie enthält oben den `Befehlsstatus` mit den `Einmalbefehlen` (siehe [Fernbefehle](fernbefehle.md)), darunter die `Konfigurationsüberschreibungen` und unten eine Vorschau mit Bestätigung.

So ändert man Einstellungen:

1. Das Gerät auswählen.
2. Bei den gewünschten Einstellungen unter `Neuer Wert` den Wert eintragen. Die Spalte `Aktuell` zeigt, was das Gerät laut seinem letzten Heartbeat gerade verwendet. Felder, die man nicht anfasst, bleiben unverändert.
3. Unter `Vorschau & Bestätigung` die Änderungen prüfen und mit `Senden & Bestätigen` abschicken.

Die Eingabe wird sofort geprüft: Zu jeder Einstellung gibt es einen erlaubten Bereich (siehe die Tabellen unten). Außerhalb davon lässt sich nichts senden.

Einstellungen, die man häufig braucht, lassen sich mit dem Stern als `Favoriten` markieren.

!!! warning "Einstellungen unter „Erweitert - Hardware“"

    Falsche Werte in dieser Gruppe können die Messbox unbrauchbar machen, sodass sie nur noch vor Ort repariert werden kann. Das Backend fragt deshalb vor dem Senden zusätzlich „Weißt du, was du tust?“. Diese Einstellungen nur ändern, wenn das ausdrücklich nötig ist.

### Wie Änderungen zur Messbox kommen

Änderungen werden im Backend eingereiht und mit dem nächsten Heartbeat an die Messbox übertragen, genau wie Fernbefehle. Die Messbox prüft jede Einstellung einzeln und übernimmt nur gültige Werte, die anderen verwirft sie. Wurde die Messbox ohne Signaturschlüssel eingerichtet, verwirft sie alles, siehe [Fernbefehle](fernbefehle.md).

Eingereihte Änderungen bleiben im Backend, bis sie ersetzt oder entfernt werden. Wer eine Einstellung wieder ändern will, sendet einfach einen neuen Wert. Mit `Eingereihte entfernen` unter `Befehlsstatus` lassen sich noch nicht zugestellte Änderungen und Befehle verwerfen.

Nur die Heimatposition lässt sich auf „nicht gesetzt“ zurücksetzen. Alle anderen Einstellungen bekommen immer einen konkreten Wert.

### Dauerhaft übernehmen

Overrides liegen auf der Messbox in einer eigenen Datei und lassen sich dadurch zurücknehmen. Wenn sich ein Wert bewährt hat, schreibt der Befehl `Overrides übernehmen` ihn dauerhaft in die Grundkonfiguration, siehe [Overrides](fernbefehle.md#overrides).

## Einstellungen im Überblick

Die Spalte „Standard“ nennt den Wert der ausgelieferten Grundkonfiguration. Die Schlüsselnamen in Backticks sind die Namen, unter denen die Einstellung auf der Messbox und in Logs auftaucht.

### Messzyklus

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Aufnahme-Auslöser` (`collector_capture_gate`) | `distance` | `distance`, `time` | Wann gemessen wird: nach Strecke oder im festen Zeitabstand. Die Erkennung von Stillstand und Sessionende bleibt immer streckenbasiert. |
| `Positionsschwelle` (`collector_position_threshold`) | 15 m | 0,1 bis 1000 m | Strecke seit der letzten Messung, nach der bei `distance` neu gemessen wird. |
| `Aufnahmeintervall` (`collector_capture_interval_s`) | 15 s | 1 bis 86400 s | Zeitabstand zwischen zwei Messungen bei `time`. |
| `Leerlaufschwelle` (`idle_threshold_s`) | 1800 s | 0 bis 86400 s | Zeit ohne erkannte Bewegung, nach der der Lauf endet. Dann werden die Daten finalisiert und hochgeladen. Zu kleine Werte beenden Läufe schon an Ampeln oder im Stau. `0` schaltet das Stillstandsende ab. Wirkt nur im Automatikmodus, im manuellen Modus endet ein Lauf nie von selbst. |
| `Max. Wartezeit auf ersten GPS-Fix` (`collector_max_wait_for_first_fix`) | 300 s | 1 bis 3600 s | So lange wartet die Messbox im Automatikmodus auf den ersten GPS-Fix. Danach endet der Durchlauf ohne Messdaten. Im manuellen Modus wartet sie nach `Messung starten` ohne Zeitgrenze. |
| `Log-Intervall beim Warten` (`collector_wait_log_interval`) | 5 s | 1 bis 3600 s | Abstand der Log-Meldungen beim Warten auf den GPS-Fix. Beeinflusst nur die Größe des Logs. |
| `GPS aktiviert` (`collector_gps_enabled`) | `true` | `true`, `false` | Bei `false` läuft die Messbox ohne GPS (z. B. bei defektem Empfänger). Die Messungen haben dann keinen Positionsbezug. |
| `Messintervall ohne GPS` (`collector_gps_disabled_poll_interval_s`) | 5 s | 1 bis 86400 s | Zeitabstand der Messungen bei deaktiviertem GPS. Wirkt nur bei `GPS aktiviert = false`. |

### Bewegungserkennung vor dem Start

Im Automatikmodus wartet die Messbox nach dem Hochfahren auf bestätigte Bewegung, bevor sie zu messen beginnt. Diese Prüfung verwendet nur den GNSS-Empfänger.

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Abfrageintervall` (`movement_gate_poll_interval_s`) | 45 s | 1 bis 86400 s | Abstand der Positionsprüfungen. Längere Abstände sparen Strom, verzögern aber den Start. |
| `Bewegungsschwelle` (`movement_gate_movement_threshold`) | 10 m | 0,1 bis 1000 m | Abstand zur Position beim ersten GPS-Fix, ab dem eine Prüfung als Bewegung zählt. Muss über der GPS-Ungenauigkeit im Stand liegen. |
| `Erforderliche Bestätigungen` (`movement_gate_confirmations_required`) | 2 | 1 bis 10 | So viele Prüfungen in Folge müssen Bewegung zeigen. Zusammen mit dem Abfrageintervall ergibt sich die Mindestzeit bis zum Start. |
| `Heimat-Breitengrad` / `Heimat-Längengrad` (`movement_gate_home_latitude`, `movement_gate_home_longitude`) | nicht gesetzt | −90 bis 90 / −180 bis 180 | Bekannter Standort, z. B. die Garage. Sind beide gesetzt, startet ein Lauf erst, wenn sich die Messbox von dort entfernt hat. Beide Werte immer gemeinsam setzen oder entfernen. |
| `Abfahrtsabstand zur Heimat` (`movement_gate_home_departure_threshold`) | 100 m | 1 bis 10000 m | Abstand, ab dem die Messbox als abgefahren gilt. |

### Latenztests

Aktive Latenzmessungen mit `flent`. Sie brauchen einen Testserver, der in der geräteeigenen Konfiguration eingetragen ist. Ohne ihn bleiben die Tests wirkungslos.

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Latenztest aktiviert` (`latency_test_enabled`) | `true` | `true`, `false` | Schaltet die Latenzmessungen ein oder aus. Der Lasttest sättigt die Verbindung und verbraucht Datenvolumen und Akku. |
| `Basisintervall` (`latency_test_baseline_interval_s`) | 60 s | 1 bis 86400 s | Abstand der Ping-Tests auf der unbelasteten Verbindung. |
| `Lastintervall` (`latency_test_load_interval_s`) | 900 s | 1 bis 86400 s | Abstand der Tests unter Last. Kurze Abstände verbrauchen viel Datenvolumen und Akku. |
| `Abfrageintervall` (`latency_test_poll_interval_s`) | 30 s | 1 bis 86400 s | Wie oft geprüft wird, ob ein Test fällig ist. |

### Backend und Betrieb

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Heartbeat-Intervall` (`heartbeat_interval_s`) | 15 s | 1 bis 86400 s | Abstand der Statusmeldungen ans Backend. Auf diesem Weg kommen auch Fernbefehle und Änderungen an. Kurze Abstände reagieren schneller, kosten aber Datenvolumen. |
| `Missionsart` (`device_mission_type`) | `ground` | `ground`, `drone` | Wird in jedem Datenpunkt mitgeschrieben. Das Backend kann damit Messungen nach Einsatzart trennen. Am Verhalten der Messbox ändert die Missionsart nichts: Ob sie auf Bewegung wartet und bei Stillstand endet, hängt nur vom [Betriebsmodus](messung.md#betriebsmodi) ab. |
| `Display aktiviert` (`display_enabled`) | `true` | `true`, `false` | Schaltet das OLED-Display ein oder aus. Ohne angeschlossenes Display auf `false` setzen. |
| `Display-Aktualisierung` (`display_refresh_interval_s`) | 2 s | 0,5 bis 3600 s | Abstand, in dem das Display neu gezeichnet wird. |
| `Tagesende-Schwelle` (`day_end_threshold_s`) | – | 0 bis 86400 s | Hat aktuell keine Funktion auf dem Gerät. Das Backend markiert die Einstellung entsprechend. |

### Pipeline-Überwachung

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Leere Aufnahmen bis Pipeline als defekt gilt` (`run_status_empty_captures_until_pipeline_broken`) | 3 | 1 bis 100 | So viele leere Messungen in Folge bei Bewegung, bis das Backend die Messkette als defekt meldet. Kleine Werte melden Störungen schnell, aber auch schon bei kurzen Funklöchern. |

### Erweitert – Hardware

!!! danger "Nur im Ausnahmefall ändern"

    Diese Einstellungen betreffen die Hardware der Messbox. Falsche Werte können sie unbrauchbar machen, bis jemand vor Ort ist.

| Einstellung | Standard | Bereich | Wirkung |
|---|---|---|---|
| `Modem-Modus` (`modem_mode`) | `serving_cell` | `serving_cell`, `sa_scan` | Abfragemodus des Modems: Daten der aktuellen Zelle oder Scan nur nach 5G-SA-Zellen. Für `sa_scan` muss das Modem vorher von Hand konfiguriert werden, sonst liefert es keine Daten. |
| `SIM-Entsperr-Versuche` (`modem_sim_unlock_poll_attempts`) | 10 | 1 bis 100 | So oft wird nach der PIN-Eingabe geprüft, ob die SIM entsperrt ist. |
| `SIM-Entsperr-Intervall` (`modem_sim_unlock_poll_interval`) | 1 s | 0,1 bis 60 s | Abstand zwischen diesen Prüfungen. Mit der Versuchszahl ergibt sich die längste Wartezeit auf die SIM. |
| `GNSS-Wiederholungen` (`gnss_receiver_retries`) | 3 | 0 bis 20 | Wiederholungen bei fehlgeschlagenen Lesezugriffen auf den GNSS-Empfänger. |
| `GNSS-Wiederholungspause` (`gnss_receiver_retry_delay_s`) | 0,75 s | 0 bis 60 s | Pause zwischen diesen Wiederholungen. |
| `Läuft auf Raspberry Pi` (`system_running_on_pi`) | `true` | `true`, `false` | Bei `false` startet die Messbox die Mobilfunkverbindung nicht selbst, überwacht sie nicht und fährt am Ende eines Laufs nicht herunter. Auf einer echten Messbox immer `true`. |

## Nur an der Messbox einstellbar

Folgendes lässt sich nicht per Fernkonfiguration ändern, sondern nur direkt am Gerät in `config.toml` bzw. `config.local.toml`:

- Backend-Adresse, Geräte-ID, API-Schlüssel und Signaturschlüssel (`hmac_secret`), die im Backend angelegt werden
- Adressen für Selbsttest, GPS-Fix-Test und Latenztest-Server
- Pfad zu `quectel-CM` und dessen Argumente (z. B. APN)
- Verzeichnis für Messdaten, die noch nicht hochgeladen sind
- serielle Schnittstellen von Modem und GNSS-Empfänger sowie die Log-Einstellungen
- Absturzverhalten und Überwachung der Mobilfunkverbindung

!!! warning "`Geräte-ID` muss überall gleich sein"

    Die `device_id` in der Messbox-Konfiguration muss mit der im Backend angelegten Geräte-ID übereinstimmen. Sonst weist das Backend hochgeladene Messdaten mit einem Fehler ab.

Die vollständige Beschreibung aller Felder steht in der [Konfigurationsreferenz](../dev/konfiguration.md).

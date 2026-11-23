# Was gemessen wird

Diese Seite beschreibt, welche Werte die Messbox erhebt, wie sie zustande kommen und worauf man bei der Auswertung achten sollte. Wann gemessen wird, steht unter [Wie die Messbox misst](messung.md), wie man die Abstände einstellt unter [Konfiguration](konfiguration.md).

Die Messbox erhebt zwei Arten von Daten:

| Art | Wann | Was |
|---|---|---|
| Funkmessung (Messpunkt) | bei jeder Aufnahme, nach Strecke oder Zeit | Signalwerte der aktuellen Funkzelle, Position, Zeit |
| Latenztest | in festen Abständen, nur in Bewegung und nur wenn eingeschaltet | Antwortzeit und Durchsatz der Verbindung zu einem Testserver |

## Funkmessung

### Wie ein Messpunkt entsteht

Bei jeder Aufnahme fragt die Messbox das Modem mit dem AT-Befehl `AT+QENG="servingcell"` nach der Zelle, in der es gerade eingebucht ist (Serving Cell). Nachbarzellen werden nicht erfasst. Zusammen mit der letzten GPS-Position und einem UTC-Zeitstempel entsteht daraus ein Messpunkt.

Meldet das Modem mehrere Funktechniken gleichzeitig, entsteht pro Funktechnik ein eigener Messpunkt mit gleicher Zeit und Position. Das ist bei 5G NSA (Non-Standalone) der Fall: Dort hängt 5G an einer LTE-Ankerzelle, und das Modem meldet eine Zeile `LTE` und eine Zeile `NR5G-NSA`.

| Funktechnik (`rat`) | Bedeutung |
|---|---|
| `LTE` | 4G |
| `NR5G-NSA` | 5G Non-Standalone, zusammen mit einer LTE-Ankerzelle |
| `NR5G-SA` | 5G Standalone, ohne LTE |

Ein Messpunkt sagt also nichts über die Zelle aus, die an diesem Ort am besten wäre, sondern über die Zelle, die das Modem gerade nutzt. Welche Zelle das ist, entscheidet das Netz.

### Signalwerte

| Wert | Einheit | Bedeutung | Gültiger Bereich LTE / NR |
|---|---|---|---|
| RSRP (Reference Signal Received Power) | dBm | Empfangsleistung des Referenzsignals der Zelle. Maß für die Signalstärke: je höher (näher an 0), desto stärker. | −140 bis −44 / −156 bis −31 |
| RSRQ (Reference Signal Received Quality) | dB | Verhältnis der Referenzsignalleistung zur gesamten empfangenen Leistung. Maß für die Signalqualität unter Last und Störungen. | −19,5 bis 2,5 / −43 bis 20 |
| SINR (Signal to Interference plus Noise Ratio) | dB | Abstand des Nutzsignals zu Störungen und Rauschen. Bestimmt maßgeblich, wie schnell Daten übertragen werden können. | −20 bis 30 / −23 bis 40 |
| RSSI (Received Signal Strength Indicator) | dBm | gesamte empfangene Leistung im Kanal, inklusive Störungen. Nur bei LTE. | – |

Liegt RSRP, RSRQ oder SINR außerhalb des gültigen Bereichs oder fehlt, zählt der Messpunkt als ungültig (`Inv` auf dem Display). Das Modem hat dann keinen echten Messwert geliefert, z. B. weil es gerade nicht eingebucht ist. Ein schwaches, aber gültiges Signal ist kein ungültiger Messpunkt. Bewertet wird die Qualität erst bei der Auswertung, nicht auf der Messbox.

### Weitere Felder

| Feld | Bedeutung |
|---|---|
| `mcc`, `mnc` | Länder- und Netzbetreiberkennung (z. B. 262 / 02 für Vodafone Deutschland) |
| `cell_id`, `pci`, `tac` | Kennung der Zelle, physikalische Zellkennung, Tracking Area |
| `band`, `channel` | Frequenzband und Kanalnummer (EARFCN bzw. NR-ARFCN) |
| `vendor_specific_extras` | weitere Werte des Modems, bei LTE z. B. Duplexverfahren, CQI, Sendeleistung |

Nicht jedes Modem und nicht jede Funktechnik liefert jedes Feld. Fehlende Werte bleiben leer.

### Position und Zeit

- **Position:** Breite, Länge und Höhe aus dem GNSS-Empfänger sowie die Zahl der genutzten Satelliten. Die Genauigkeit ist die eines einfachen GNSS-Empfängers, also einige Meter.
- **Zeit:** UTC-Zeitstempel der Aufnahme. Die Systemuhr wird aus der GNSS-Zeit gestellt.
- **Lauf und Gerät:** Jeder Messpunkt trägt die Geräte-ID, die Einsatzart (`ground` oder `drone`) und die ID des Laufs.

!!! note "Höhe bei Messflügen"

    Die Höhe stammt aus dem GNSS-Empfänger der Messbox, nicht aus der Drohne. Sie ist die Höhe über dem Meeresspiegel, nicht über Grund, und deutlich ungenauer als die horizontale Position. Für einen Vergleich nach Flughöhe die Höhenangaben der Drohne heranziehen.

### Wie dicht gemessen wird

Standardmäßig entsteht ein Messpunkt, sobald sich die Messbox 15 m vom letzten Messpunkt entfernt hat. Wer stillsteht, erzeugt keine neuen Messpunkte. Alternativ lässt sich ein fester Zeitabstand einstellen (Standard 15 s). Welche Einstellung für welchen Einsatz passt, steht unter [Messintervall und Rasterdichte](konfiguration.md#messintervall-und-rasterdichte).

## Latenz und Durchsatz

### Wie getestet wird

Ist der Latenztest eingeschaltet, startet die Messbox mit [`flent`](https://flent.org) Tests gegen einen Testserver, solange sie sich bewegt. Es gibt zwei Tests:

| Test | `flent`-Test | Standard | Ergebnis |
|---|---|---|---|
| Grundmessung | `ping` | alle 60 s, 10 s lang | Antwortzeit (RTT) der unbelasteten Verbindung |
| Lasttest | `rrul` | alle 15 min, 60 s lang | Antwortzeit unter Last, Download- und Upload-Durchsatz |

Der Lasttest (`rrul`, Realtime Response Under Load) lastet die Verbindung mit mehreren TCP-Strömen in beide Richtungen voll aus und misst gleichzeitig die Antwortzeit. Er zeigt, wie stark die Latenz steigt, wenn die Verbindung ausgelastet ist, und wie viel Durchsatz sie hergibt.

### Ergebnisse

Ein Test dauert mehrere Sekunden, in denen sich das Fahrzeug bewegt. Ein Latenzergebnis ist deshalb kein Messpunkt, sondern hat einen Start- und einen Endzeitpunkt mit jeweils eigener Position.

| Wert | Bedeutung |
|---|---|
| `baseline_rtt_ms` | Median der Antwortzeit in der Grundmessung |
| `rtt_under_load_ms` | Median der Antwortzeit im Lasttest |
| `rtt_p99_ms` | 99. Perzentil der Antwortzeit: die langsamsten 1 % der Antworten |
| `download_mbits_s`, `upload_mbits_s` | mittlerer Durchsatz im Lasttest in Mbit/s |

Die Antwortzeit wird als Median und 99. Perzentil angegeben, weil ein Mittelwert gerade die Ausreißer verdeckt, die eine belastete Verbindung ausmachen.

### Was die Latenz aussagt und was nicht

- **Gemessen wird die ganze Strecke**, nicht nur die Funkstrecke: Messbox → Funkzelle → Kernnetz des Betreibers → Internet → Testserver und zurück. Eine hohe Latenz kann auch am Weg durchs Internet oder am Testserver liegen. Werte verschiedener Einsätze sind nur vergleichbar, wenn derselbe Testserver verwendet wurde.
- **Der Lasttest beeinflusst die Funkmessung:** Während der 60 s Volllast misst die Messbox weiter. Funkwerte aus dieser Zeit, vor allem die Qualität, können von der eigenen Last beeinflusst sein.
- **Datenvolumen:** Ein Lasttest überträgt so viel, wie die Verbindung in 60 s hergibt, bei 50 Mbit/s in beide Richtungen also grob 750 MB. Bei einer SIM-Karte mit begrenztem Volumen den Abstand der Lasttests vergrößern oder sie abschalten.
- **Nur in Bewegung:** Ein fälliger Test läuft nur, wenn die letzte Bewegung höchstens 30 s her ist. Bei längeren Standzeiten entstehen keine Latenzergebnisse.

Die Gegenstelle auf dem Server beschreibt [Flent-Server](../../backend/dev/flent-server.md), alle Einstellungen stehen in der [Konfigurationsreferenz](../dev/konfiguration.md#latency_test).

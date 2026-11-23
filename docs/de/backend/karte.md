# Karte und Export

Die `Karte / Heatmap` ist die Startseite des Backends und zeigt die Messergebnisse nach Ort. Sie ist auch ohne Anmeldung sichtbar, dann allerdings mit Einschränkungen, siehe [Gäste und Angemeldete](#gaste-und-angemeldete).

## Anzeige einstellen

| Einstellung | Wirkung |
|---|---|
| `Metrik` | Was eingefärbt wird: Signalwerte (RSRP, RSRQ, SINR) oder Latenz und Durchsatz (RTT-Basiswert, RTT unter Last, RTT p99, Download, Upload) |
| `Missionstyp` | `Boden` (vorausgewählt) oder `Drohne`; beides zusammen geht nicht |
| `Geräte-ID` | nur Messungen einer Messbox; die ID muss bekannt sein, eine Auswahlliste gibt es nicht |
| `Kampagne` | eine Kampagne oder `Gesamter Zeitraum`, siehe [Messläufe und Kampagnen](messlaeufe.md) und den Hinweis unten |
| `Darstellung` | `Heatmap` oder `Punkte`, siehe unten |
| `Deckkraft` | wie stark die Messdaten die Karte überdecken |

Mit gedrückter Strg-Taste lässt sich ein Rechteck aufziehen, auf das die Karte zoomt. `Vollbild` zeigt die Karte bildschirmfüllend.

## Farben

Alle Metriken nutzen dieselbe Skala von Rot (schlecht) über Gelb nach Grün (gut). Werte außerhalb des Bereichs bekommen die Farbe des jeweiligen Endes.

| Metrik | Rot | Grün |
|---|---|---|
| RSRP | -110 dBm | -80 dBm |
| RSRQ | -20 dB | -10 dB |
| SINR | 0 dB | 20 dB |
| RTT-Basiswert | 100 ms | 10 ms |
| RTT unter Last | 200 ms | 30 ms |
| RTT p99 | 350 ms | 60 ms |
| Download | 10 Mbit/s | 500 Mbit/s |
| Upload | 5 Mbit/s | 100 Mbit/s |

## Heatmap und Punkte

**`Heatmap`** zeigt einen Überblick. Liegen im Kartenausschnitt viele Signalmessungen (ab 2000), fasst das Backend sie zu Rasterzellen zusammen und zeigt pro Zelle den Mittelwert. Das Raster wird beim Hineinzoomen feiner. Bei weniger Messungen zeigt die Heatmap die einzelnen Punkte, nur fast deckungsgleiche Punkte (unter 2,5 m Abstand) werden zusammengelegt. Latenz und Durchsatz zeigt die Heatmap immer als Rasterzellen, jeder Test an der Mitte zwischen Start- und Endposition.

!!! warning "Heatmap zeigt immer genau eine Kampagne"

    Die Heatmap mischt nie Daten mehrerer Kampagnen. Ist `Gesamter Zeitraum` gewählt, zeigt sie trotzdem nur die Kampagne mit dem jüngsten Messpunkt. Alle Daten auf einmal, auch Läufe ohne Kampagne, zeigt nur die Darstellung `Punkte`.

**`Punkte`** zeigt jede Messung einzeln. Bei Latenz und Durchsatz ist jeder Test eine Linie von der Position zu Beginn zur Position am Ende des Tests, weil die Messbox während des Tests weiterfährt.

## Punkte auswählen

In der Darstellung `Punkte` lassen sich Messungen auswählen und auswerten.

- Ein Klick wählt einen Punkt, ein Klick mit gedrückter Umschalttaste nimmt einen weiteren dazu oder wieder heraus.
- Mit gedrückter Umschalttaste ein Rechteck aufziehen wählt alle Punkte darin.

Unter der Karte erscheinen dann `Ausgewählte Punkte` mit einer `Auswahlstatistik` (Anzahl, Minimum, Maximum, Mittelwert, Median, Standardabweichung) und der Liste der Punkte. Einzelne Punkte lassen sich dort wieder entfernen, `Leeren` hebt die Auswahl auf.

## Export

| Export | Inhalt | Wann verfügbar |
|---|---|---|
| `CSV exportieren`, `GEOJSON exportieren` | die Daten der Heatmap im aktuellen Kartenausschnitt: Position, Wert der gewählten Metrik und Anzahl der zusammengefassten Messungen | Darstellung `Heatmap`, nur RSRP, RSRQ und SINR |
| `PNG exportieren` | Bild des aktuellen Kartenausschnitts | Darstellung `Heatmap`, nur RSRP, RSRQ und SINR |
| `Auswahl als CSV exportieren`, `Auswahl als GeoJSON exportieren` | die ausgewählten Punkte mit Position, RSRP, RSRQ, SINR, Missionstyp und Kampagne | Darstellung `Punkte`, nur RSRP, RSRQ und SINR |

Exportiert wird immer nur, was gerade zu sehen ist. Für mehr Daten vorher herauszoomen oder den Kartenausschnitt verschieben. Die Exporte enthalten keine Geräte-IDs und keine Zeitpunkte, auch nicht für angemeldete Nutzer.

## Einen Messlauf ansehen

`Auf Karte zeigen` in den [Messläufen](messlaeufe.md) öffnet die Karte mit nur diesem Lauf, immer in der Darstellung `Punkte`. Ein Hinweis über der Karte zeigt, welcher Lauf zu sehen ist. `Lauffilter entfernen` kehrt zur normalen Ansicht zurück.

## Gäste und Angemeldete

| | Gast | Angemeldet |
|---|---|---|
| Kampagne | eine Kampagne, vorausgewählt ist die mit dem jüngsten Messpunkt | zusätzlich `Gesamter Zeitraum` (nur in der Darstellung `Punkte` wirksam) |
| Läufe ohne Kampagne | nicht sichtbar | in der Darstellung `Punkte` mit `Gesamter Zeitraum` |
| `Geräte-ID` | nicht verfügbar | verfügbar |
| Punkte | höchstens 5000, ohne Geräte-ID und Zeitpunkt | Limit aus den [Einstellungen](einstellungen.md), mit Gerät und Zeitpunkt in der Auswahlliste |
| Einzelnen Lauf ansehen | nicht möglich | über `Auf Karte zeigen` in [Messläufe](messlaeufe.md) |

# Flent-Server

Die Messboxen messen Latenz und Durchsatz mit `flent`. `flent` selbst läuft nur auf der Messbox und hat keinen Servermodus. Auf dem Server laufen stattdessen die Programme, mit denen die Tests sprechen:

- `netserver` aus [netperf](https://github.com/HewlettPackard/netperf): erzeugt den Durchsatz für die Tests `baseline` und `rrul_be`
- [irtt](https://github.com/heistp/irtt): misst die Latenz unter Last, diesen Port erreichen die Messboxen

Beide laufen bewusst außerhalb von Docker, weil die Ports pro Messbox in der Firewall freigegeben werden müssen. Die Ergebnisse gehen nicht über diese Verbindung, sondern wie alle Messdaten verschlüsselt an `POST /api/latency-results`.

| | Port |
|---|---|
| `irtt` | `8080` (für die Messboxen freigegeben) |
| `netserver` | `12865` (Standard von netperf, nicht öffentlich) |

## Einrichten

1. Ein eigenes Systemkonto ohne Login anlegen, einmal pro Server:

    ```bash
    sudo useradd -r -s /usr/sbin/nologin appuser
    sudo groupadd appgroup
    sudo usermod -aG appgroup appuser
    ```

2. netperf und irtt installieren. Für irtt gibt es kein Paket, es wird nach der [Anleitung von irtt](https://github.com/heistp/irtt#installation) gebaut.

    ```bash
    sudo apt install netperf
    ```

3. Startskript und `systemd`-Unit aus dem Backend-Repository an ihren Platz kopieren und starten:

    ```bash
    sudo cp scripts/start_flent_server.sh /opt/5g-measurement-backend/scripts/
    sudo cp deploy/flent-server.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now flent-server.service
    ```

4. Prüfen, ob beide Prozesse laufen:

    ```bash
    sudo systemctl status flent-server.service
    pgrep -a netserver
    pgrep -a irtt
    ```

5. Von einem Rechner mit `flent` testen:

    ```bash
    flent -H <domain> -p 8080 tcp_nup    # baseline
    flent -H <domain> -p 8080 rrul_be    # RRUL
    ```

Auf der Messbox wird der Latenztest über `Latenztest aktiviert` und die zugehörigen Einstellungen gesteuert, siehe [Konfiguration der Messbox](../../messbox/nutzung/konfiguration.md#latenztests).

## Sicherheit

- `netserver` und `irtt` können kein TLS. Über sie läuft nur Testverkehr, keine Messergebnisse. Das Risiko ist Missbrauch der Bandbreite, nicht das Mitlesen.
- Die Ports nur für bekannte Messboxen freigeben, nie für alle. Offene `netserver`- oder `irtt`-Dienste lassen sich für Bandbreitenmissbrauch und Verstärkungsangriffe nutzen. Beispiel pro Messbox:

    ```bash
    sudo ufw allow from <ip-der-messbox> to any port 8080,12865 proto tcp
    sudo ufw allow from <ip-der-messbox> to any port 8080 proto udp
    ```

- Beide Dienste laufen als `appuser`, nie als root, und speichern nichts auf der Festplatte.

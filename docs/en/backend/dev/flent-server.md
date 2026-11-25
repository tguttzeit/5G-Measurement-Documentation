# Flent server

The units measure latency and throughput with `flent`. `flent` itself only runs on the unit and has no server mode. Instead, the programs that the tests talk to run on the server:

- `netserver` from [netperf](https://github.com/HewlettPackard/netperf): generates the throughput for the tests `baseline` and `rrul_be`
- [irtt](https://github.com/heistp/irtt): measures the latency under load; the units reach this port

Both deliberately run outside Docker because the ports have to be opened in the firewall per unit. The results do not go over this connection but, like all measurement data, encrypted to `POST /api/latency-results`.

| | Port |
|---|---|
| `irtt` | `8080` (opened for the units) |
| `netserver` | `12865` (netperf default, not public) |

## Setting up

1. Create a system account of its own without login, once per server:

    ```bash
    sudo useradd -r -s /usr/sbin/nologin appuser
    sudo groupadd appgroup
    sudo usermod -aG appgroup appuser
    ```

2. Install netperf and irtt. There is no package for irtt; it is built following the [irtt instructions](https://github.com/heistp/irtt#installation).

    ```bash
    sudo apt install netperf
    ```

3. Copy the start script and `systemd` unit from the backend repository into place and start them:

    ```bash
    sudo cp scripts/start_flent_server.sh /opt/5g-measurement-backend/scripts/
    sudo cp deploy/flent-server.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now flent-server.service
    ```

4. Check that both processes are running:

    ```bash
    sudo systemctl status flent-server.service
    pgrep -a netserver
    pgrep -a irtt
    ```

5. Test from a machine with `flent`:

    ```bash
    flent -H <domain> -p 8080 tcp_nup    # baseline
    flent -H <domain> -p 8080 rrul_be    # RRUL
    ```

On the unit, the latency test is controlled via `Latency test enabled` and the associated settings, see [Configuration of the unit](../../measurement-unit/usage/configuration.md#latency-tests).

## Security

- `netserver` and `irtt` cannot do TLS. Only test traffic runs over them, no measurement results. The risk is misuse of the bandwidth, not eavesdropping.
- Only open the ports for known units, never for everyone. Open `netserver` or `irtt` services can be used for bandwidth abuse and amplification attacks. Example per unit:

    ```bash
    sudo ufw allow from <ip-of-the-unit> to any port 8080,12865 proto tcp
    sudo ufw allow from <ip-of-the-unit> to any port 8080 proto udp
    ```

- Both services run as `appuser`, never as root, and store nothing on the disk.

# Preparing the unit

Before every deployment the unit is connected once, its connection to the backend is checked and the configuration is adjusted to the deployment. It is best done before travelling to the site. At the end of this page you choose measurement drive or measurement flight. The settings that only apply to one of the two deployment types are at the top of the respective page.

## What you need

- Measurement unit with antenna, power bank and both USB cables
- Backend account with superuser rights: only with these are `Remote Configuration` and remote commands accessible
- Optional: smartphone with the [ntfy](https://ntfy.sh) app
- Optional: LAN cable, if the unit is to connect to the network without cellular

## Procedure

### Section I – Setting up push notifications

Once per account and smartphone. If you have done this already, continue with [Section II](#section-ii-connecting-the-unit).

The backend reports via ntfy when the unit checks in, a measurement starts or ends, data has been uploaded or an error occurs. In the field you can thus see whether everything is running without looking into the backend.

1. In the backend under `Settings`, switch on the push notifications, see [Push notifications](../../backend/settings.md#push-notifications).
2. Subscribe to the displayed topic in the ntfy app.
3. Use `Send test notification` to check that the message arrives on the smartphone.

### Section II – Connecting the unit

1. Charge the power bank if necessary.
2. Connect the unit to the internet. There are two ways:
    - **Via cellular:** Connect the antenna. The connectors are assigned as follows:

        ![Assignment of the antenna ports on the unit](../../../images/5gmu_antenna_ports.svg)

    - **Via LAN:** Open the unit (4x M3 screws on the side opposite the ports) and plug the LAN cable into the port of the Raspberry Pi. It is easy to reach once the box is open.
3. Connect the unit to the power bank, first with the USB-A to USB-A cable (power for the modem), then with the USB-C to USB-C cable (Raspberry Pi). **Both** cables must be connected. The Raspberry Pi starts as soon as the USB-C cable is plugged in.
4. The software then starts automatically. Wait until the display shows something. This takes about 10 s; from then on the software is running.
5. In the backend under `Mission Status`, check that the unit is shown as online and sends heartbeats. With push notifications, `Measurement box started` arrives as well.
    - If the unit stays offline, see [Troubleshooting](../troubleshooting/failure-modes.md).

### Section III – Checking the general settings

The default settings suit most deployments. Changes are made in the backend under `Remote Configuration`, see [Remote Configuration in the backend](configuration.md#remote-configuration-in-the-backend).

1. Open `Remote Configuration` in the backend and select the unit.
2. In the `Current` column, look up what the unit is currently using and check whether one of the following situations applies:

    | If … | then adjust |
    |---|---|
    | the unit starts in a garage or on a site with poor GPS reception | `Max wait for first GPS fix` |
    | the unit is operated without a display | `Display enabled` |

3. Leave the page open: at the beginning of the measurement drive or measurement flight page, the settings for the respective deployment type follow. Only after that is the unit rebooted so that all changes take effect.

!!! info "Changes only take effect after a reboot"

    The unit never applies changes during a running pass. They arrive with the next heartbeat and take effect from the next start. After that they persist, also across shutdown and power loss, until you change them again in the backend.

### Section IV – Choosing the deployment type

<div class="grid cards" markdown>

-   :material-car: **[Measurement drive](measurement-drive.md)**

    ---

    Measuring from a vehicle. The unit starts and ends the measurement by itself (Auto Mode).

-   :material-quadcopter: **[Measurement flight](measurement-flight.md)**

    ---

    Measuring with the DJI Matrice 300 RTK. The measurement is started and ended by remote command (Manual Mode).

</div>

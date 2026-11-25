# After use

This is where measurement drive and measurement flight come together again.

## Procedure

### Section I – Disconnecting the unit from power

1. Wait until the display shows `SHUTTING DOWN`. After shutdown this display often stays on.
2. Unplug both cables from the power bank. Shut down does not mean without power: as long as the cables are connected, the unit keeps drawing a small standby current.

!!! note "Disconnected too early?"

    Disconnecting the power too early is not a big problem. At worst, the most recently saved line of datapoints is lost. The rest stays on the unit and is uploaded during a later run.

### Section II – Dismantling and charging

1. Dismantle the unit, antenna and mounts.
2. Charge the power bank.

### Section III – Checking the data

1. Check whether the data has arrived in the backend:
    - With push notifications, `New runs uploaded` arrives.
    - Otherwise look in the backend under `Measurement Runs`, see [Checking that the data has arrived](../../backend/runs.md#checking-that-the-data-has-arrived).
2. If a run is missing, the data is still on the unit. A file is only deleted there after a successful upload. It is uploaded
    - when measuring begins or ends during the next deployment, or
    - immediately, if you switch on the unit and send the remote command `Force upload` in the backend.

!!! tip "Done"

    The deployment is complete. Before the next deployment, start again at [Preparing the unit](preparation.md).

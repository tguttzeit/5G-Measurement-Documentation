# Deployment

Im Produktivbetrieb läuft das Backend vollständig über Docker Compose. Nur die Gegenstelle für die Latenztests läuft außerhalb, siehe [Flent-Server](flent-server.md).

## Dienste

| Dienst | Profil | Aufgabe |
|---|---|---|
| `postgres` | immer | Datenbank, Daten im Volume `postgres_data` |
| `backend` | immer | API, nur lokal auf `127.0.0.1:8000` erreichbar |
| `frontend-prod` | `prod` | gebaute Oberfläche |
| `caddy` | `prod` | HTTPS mit automatischem Zertifikat, leitet `/api` an `backend`, `/docs` an diese Dokumentation und alles andere an `frontend-prod` weiter |

## Voraussetzungen

- Ein DNS-Eintrag für die Domain zeigt auf den Server.
- Die Ports 80 und 443 sind für Caddy offen. Sonst muss nichts öffentlich erreichbar sein.
- Eine `.env` mit echten Werten für `POSTGRES_PASSWORD`, `DATABASE_URL`, `SECRET_KEY` und `SITE_DOMAIN`, siehe [Konfiguration](konfiguration.md).

## Starten

Im Verzeichnis des Backends:

```bash
docker compose --profile prod up -d
```

Beim Start des Containers `backend` laufen die Datenbank-Migrationen automatisch (`alembic upgrade head`). Von Hand geht das mit:

```bash
docker compose exec backend alembic upgrade head
```

Ob die API läuft, zeigt `https://<domain>/api/health`, die Antwort ist `{"status": "ok"}`.

Danach den ersten Superuser und die Messboxen anlegen, siehe [Gerät registrieren](geraet-registrieren.md).

## Aktualisieren

Der Server läuft auf einem Checkout des öffentlichen Backend-Repositorys, Branch `main`. Neue Versionen kommen dort als Release mit Tag an.

1. **Datenbank sichern. Pflicht vor jedem Update.** Beim Start des neuen Containers laufen die Migrationen automatisch. Geht eine schief, hilft nur die Sicherung:

    ```bash
    sudo -u dbbackup deploy/backup-db.sh --pre-update
    ```

    Das Script läuft unter dem Konto, dem das Sicherungsverzeichnis gehört; `sudo -u` entfällt, wenn das das eigene ist. Die Sicherung landet in `pre-update/` im [Sicherungsverzeichnis](#datensicherung), die drei neuesten bleiben erhalten. Bricht das Script mit einem Fehler ab, nicht weitermachen.

2. **Neue Version holen:**

    ```bash
    git pull
    ```

3. **Neu bauen und starten.** Die Images werden auf dem Server gebaut, nicht aus einer Registry geladen:

    ```bash
    docker compose --profile prod up -d --build
    ```

4. **Prüfen:** `https://<domain>/api/health` antwortet mit `{"status": "ok"}`, die Oberfläche lädt, und im `Missionsstatus` kommen wieder Heartbeats an.

Den [Flent-Server](flent-server.md) betrifft ein Update nur, wenn sich `scripts/start_flent_server.sh` oder `deploy/flent-server.service` geändert haben. Dann beide wie bei der Einrichtung neu kopieren und `sudo systemctl restart flent-server.service` ausführen. Haben sich `deploy/5gm-db-backup.service` oder `deploy/5gm-db-backup.timer` geändert, beide neu nach `/etc/systemd/system/` kopieren und `sudo systemctl daemon-reload` ausführen; ein Drop-in bleibt dabei erhalten.

### Zurück zur vorigen Version

1. Den vorigen Stand per Git auschecken, z. B. das vorige Release-Tag.
2. Hat das Update die Datenbank migriert, die Sicherung von vor dem Update [zurückspielen](#zuruckspielen), bevor das Backend wieder startet.
3. Wie oben neu bauen und starten.

## Datensicherung

Die Messboxen löschen ihre Dateien nach dem Upload. Die Datenbank ist danach die einzige Kopie aller Messdaten. `deploy/backup-db.sh` sichert sie mit `pg_dump` aus dem laufenden Container `postgres`, angestoßen einmal täglich von `deploy/5gm-db-backup.timer`.

| Verzeichnis | Inhalt | Aufbewahrt |
|---|---|---|
| `daily/` | tägliche Sicherung | die 7 neuesten |
| `weekly/` | die erste Sicherung jeder Kalenderwoche | die 4 neuesten |
| `pre-update/` | Sicherungen vor einem Update (`--pre-update`) | die 3 neuesten |

- Das Sicherungsverzeichnis ist `/var/backups/5g-measurement-backend`, änderbar über `BACKUP_DIR`.
- Aufbewahrt wird nach Anzahl, nicht nach Alter: Lief der Timer eine Weile nicht, bleiben die letzten Sicherungen trotzdem erhalten.
- Eine Sicherung ersetzt ältere erst, wenn sie vollständig ist und sich mit `pg_restore --list` lesen lässt. Schlägt sie fehl, endet der Dienst mit einem Fehler, und die vorhandenen Sicherungen bleiben unberührt.
- Ist im Sicherungsverzeichnis weniger als 5 GB frei (`BACKUP_MIN_FREE_MB`), schreibt der Lauf eine Warnung ins Journal.
- Die Sicherungen liegen nur auf dem Server selbst. Sie helfen bei einer fehlgeschlagenen Migration, einem kaputten Volume oder einem Bedienfehler, nicht wenn der Server selbst verloren geht.

### Einrichten

1. Ein eigenes Systemkonto ohne Login für die Sicherung anlegen. Es braucht Zugriff auf Docker:

    ```bash
    sudo useradd -r -U -s /usr/sbin/nologin -G docker dbbackup
    ```

    Nicht das Konto `appuser` des [Flent-Servers](flent-server.md) verwenden. Mitglied der Gruppe `docker` zu sein entspricht Root-Rechten, und `irtt` ist aus dem Netz erreichbar.

2. Das Sicherungsverzeichnis anlegen, nur für dieses Konto lesbar:

    ```bash
    sudo install -d -o dbbackup -g dbbackup -m 700 /var/backups/5g-measurement-backend
    ```

3. Die Units kopieren:

    ```bash
    sudo cp deploy/5gm-db-backup.service deploy/5gm-db-backup.timer /etc/systemd/system/
    ```

4. Der Dienst startet `deploy/backup-db.sh` im Checkout des Backends und erwartet ihn unter `/opt/5g-measurement-backend`. Liegt der Checkout woanders oder läuft die Sicherung unter einem anderen Konto, beides in einem Drop-in eintragen (`sudo systemctl edit 5gm-db-backup.service`):

    ```ini
    [Service]
    User=<konto>
    Group=<gruppe>
    ExecStart=
    ExecStart=<backend-verzeichnis>/deploy/backup-db.sh
    ```

    Das leere `ExecStart=` ist nötig, sonst kommt der neue Befehl zum alten hinzu. Das Sicherungsverzeichnis muss dann diesem Konto gehören.

5. Timer aktivieren und die erste Sicherung von Hand anstoßen:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now 5gm-db-backup.timer
    sudo systemctl start 5gm-db-backup.service
    ```

### Prüfen

```bash
systemctl list-timers 5gm-db-backup.timer                 # nächster Lauf
journalctl -u 5gm-db-backup.service -n 20                 # letzte Läufe mit Größe der Sicherung
journalctl -u 5gm-db-backup.service -p warning --since -7d # Fehler und Warnungen
sudo ls -l /var/backups/5g-measurement-backend/daily
```

Eine fehlgeschlagene Sicherung zeigt auch `systemctl --failed`.

### Zurückspielen

Zurückgespielt wird nur von Hand. Das Backend muss dabei gestoppt sein, sonst arbeitet es mit einer halb gefüllten Datenbank.

1. Backend stoppen:

    ```bash
    docker compose stop backend
    ```

2. Die Datenbank leeren, indem sie neu angelegt wird. `pg_restore --clean` reicht dafür nicht: Es löscht nur, was in der Sicherung vorkommt, und ließe Tabellen einer fehlgeschlagenen Migration stehen.

    ```bash
    docker compose exec -T postgres dropdb -U postgres measurement_backend
    docker compose exec -T postgres createdb -U postgres measurement_backend
    ```

    Ist das Volume `postgres_data` verloren und wurde neu angelegt, entfällt dieser Schritt: Der Container legt die leere Datenbank beim ersten Start selbst an (`docker compose up -d postgres`). Dann fehlt aber die Rolle, unter der das Backend sich anmeldet, denn `pg_dump` sichert keine Rollen. Name und Passwort stehen in `DATABASE_URL` in der `.env`:

    ```bash
    docker compose exec postgres psql -U postgres -c "CREATE ROLE <rolle> LOGIN"
    docker compose exec postgres psql -U postgres -c "\password <rolle>"
    ```

    `\password` fragt das Passwort ab, so landet es nicht in der Shell-History.

3. Die Sicherung zurückspielen:

    ```bash
    sudo cat /var/backups/5g-measurement-backend/<verzeichnis>/<datei>.dump \
      | docker compose exec -T postgres pg_restore -U postgres -d measurement_backend --exit-on-error
    ```

4. Alles wieder starten und wie nach einem Update prüfen:

    ```bash
    docker compose --profile prod up -d --build
    ```

!!! warning "Zurückspielen überschreibt alles seit der Sicherung"

    Die Datenbank hat danach den Stand der Sicherung. Messdaten, die seit der Sicherung hochgeladen wurden, gehen dabei verloren. Die Messboxen laden sie nicht erneut hoch.

!!! danger "Sicherungen enthalten alles"

    Eine Sicherung enthält alle Messdaten, die Benutzerkonten mit Passwort-Hashes und die Hashes der Geräteschlüssel. Das Verzeichnis nie in einen Pfad legen, den Caddy ausliefert, und nicht mit weiteren Rechten versehen.

## Diese Dokumentation

Caddy liefert diese Dokumentation unter `/docs` aus dem Verzeichnis `DOCS_DIR` aus. Gebaut wird sie auf demselben Server aus ihrem eigenen Repository, gesteuert von einem `systemd`-Timer. Einrichtung und Ablauf stehen dort in `deploy/README.md`.

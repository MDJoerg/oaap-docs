---
title: "Das nächtliche Backup auf der CLI einrichten"
audience: [server_admin, support]
checked_against: "0.1.249"
checked_on: 2026-11-11
lang: de
tags: [backup, sicherung, cli, wiederherstellung]
---
# Das nächtliche Backup auf der CLI einrichten

> Geprüft gegen Referenz **0.1.249** (2026-11-11): am Code gelesen, Nachtlauf
> von Hand und `oaap backup schedule` auf `oaap-test`. Das erstmalige
> Einrichten des Timers (Schritt 2) wurde an diesem Tag nicht neu
> durchgespielt; es läuft so auf vier Knoten der Flotte.

Ein OAAP-Knoten sichert sich **jede Nacht vollständig** in ein `tar.gz`:
Plattform-Zustand, Benutzer, alle Instanzdaten aller Mandanten, Dokumente
und den Store. Diese Anleitung richtet das auf einem Knoten ein, prüft es
und zeigt, wie die Archive auf eine zweite Maschine kommen.

## Voraussetzungen

- Ein installierter Knoten ([Server aufsetzen](server-aufsetzen.md)) und
  eine Shell mit `sudo` darauf.
- Ein **Ziel außerhalb von `/var/lib/oaap`** mit Platz für etwa das
  Doppelte der Nutzdaten (die Daten liegen beim Komprimieren kurz doppelt
  da). Voreinstellung ist `/var/backups/oaap`. Ein Ziel im
  Datenverzeichnis lehnt OAAP ab: Eine Sicherung, die mit der Maschine
  stirbt, ist keine.
- Das Ziel muss **exklusiv berechtigt** sein. Das Archiv ist nicht
  verschlüsselt und enthält alle Geheimnisse der Plattform im Klartext
  (Passwort-Hashes, `.env`, Zugangsschlüssel der Instanzen).

## Schritt 1: Einmal von Hand sichern

```sh
sudo oaap backup create
```

Die App-Container stehen **nur für das Kopieren** still, komprimiert wird
danach mit laufenden Apps. Am Ende nennt der Befehl Datei, Größe, Zahl der
Instanzen und die gemessene Ausfallzeit.

**Prüfen:** Die letzte Zeile lautet `Backup written: /var/backups/oaap/oaap-backup-<knoten>-<datum>.tar.gz (… MB, N app instance(s), app downtime …s …)`.

## Schritt 2: Den nächtlichen Lauf einrichten

Der Zeitplan ist ein **systemd-Timer**, das Gegenstück zu einem
Hintergrundjob in SAP: Eine Unit sagt, *was* läuft, ein Timer sagt,
*wann*. Eingerichtet wird er mit einem Skript aus dem Plattform-Checkout
des Knotens. Wo der liegt, steht in der `.env` der Plattform:

```sh
SRC=$(sudo grep '^OAAP_PLATFORM_SOURCE=' /var/lib/oaap/app/.env | cut -d= -f2)
cd "$SRC"
sudo bash ops/install-backup-timer.sh --at 03:30 --keep 2
```

- `--at` ist die Uhrzeit (24 h), `--keep` die Zahl der Archive, die
  **auf diesem Knoten** liegen bleiben. Ältere löscht der Lauf.
- `--to <verzeichnis>` legt ein anderes Ziel fest. Das Ziel ist bewusst
  **keine** Portal-Einstellung, sondern wird hier auf der Maschine
  festgelegt.

**Prüfen:**

```sh
systemctl list-timers oaap-backup.timer
```

Die Spalte `NEXT` nennt den nächsten Lauf.

## Schritt 3: Den Nachtlauf einmal sofort auslösen

```sh
sudo oaap-backup-nightly
```

Das ist genau der Befehl, den der Timer nachts ausführt: sichern, das
Archiv einmal vollständig zurücklesen, ältere Archive über `--keep` hinaus
entfernen.

**Prüfen:** Die letzte Zeile lautet `OK: oaap-backup-<knoten>-<datum>.tar.gz, … MB, …s`.

## Schritt 4: Den Zustand ansehen

```sh
sudo oaap backup schedule
```

Ausgabe: `on`/`OFF`, Uhrzeit, Zahl der Archive, Ziel, nächster Lauf und
die Ausfallzeit des letzten Laufs. Dasselbe zeigt die **Gesundheitsseite
des Portals**; dort lassen sich auch Uhrzeit und Aufbewahrung ändern.

**Prüfen:** `nightly backup: on`, und `next:` liegt in der kommenden
Nacht.

Später ändern, ohne das Skript noch einmal:

```sh
sudo oaap backup schedule --at 02:00 --keep 3
sudo oaap backup schedule --off      # nichts läuft mehr von selbst
sudo oaap backup schedule --on
```

## Schritt 5: Die Archive auf eine zweite Maschine holen

Ein Archiv auf derselben Platte schützt vor Bedienfehlern, nicht vor dem
Verlust der Maschine. OAAP **holt** ab: Eine zweite Maschine zieht die
Archive per SSH, und der gesicherte Knoten hat keinen Schlüssel zum Ziel.
Wer den Knoten übernimmt, kommt also nicht an die Sicherungen.

Auf der abholenden Maschine, ebenfalls aus ihrem Plattform-Checkout:

```sh
ssh-keygen -t ed25519 -N "" -C "backup-pull@<abholer>" -f ~/.ssh/oaap_backup_pull
# öffentlichen Teil beim gesicherten Knoten in ~/.ssh/authorized_keys eintragen,
# mit Zwang auf genau einen Befehl:
#   command="/usr/local/bin/oaap-backup-serve",restrict ssh-ed25519 AAAA… backup-pull@<abholer>
sudo bash ops/install-backup-pull.sh --node <knoten> --host <adresse> \
     --user oaap-admin --key ~/.ssh/oaap_backup_pull --to /mnt/backup
```

Dort entstehen Generationen: 7 tägliche, 4 wöchentliche (Sonntag) und
6 monatliche (der Erste) — jede ein Vollarchiv.

**Prüfen:** Nach dem ersten Lauf liegt unter `/mnt/backup/<knoten>/daily/`
ein Archiv mit derselben Prüfsumme wie auf dem Knoten.

Mehr dazu, auch zum Tresor (Wechselplatte, RFC-0053) und zum umgekehrten
Weg für Knoten hinter fremder Firewall:
[ops/README.md](https://github.com/MDJoerg/oaap-reference/blob/main/ops/README.md).

## Mandanten: einzeln sichern oder ausnehmen

```sh
sudo oaap backup status                       # wessen Daten im Knotenarchiv stecken
sudo oaap backup create --tenant <mandant>    # Archiv nur dieses Mandanten
sudo oaap backup exclude <mandant> --reason "Der Kunde sichert selbst"
sudo oaap backup include <mandant>
```

Ein **Mandantenarchiv** stellt der Installer nicht wieder her. Mit ihm zieht
ein Mandant auf einen anderen Knoten um (`oaap tenant adopt`). Die
Begründung bei `exclude` landet im Protokoll **des Kunden**: Schreiben Sie
sie so, dass er sie versteht.

## Was nicht im Archiv steckt

Bewusst nicht gesichert: OIDC-Client-Secrets, Zugangsdaten von Destinations
und Tunneln, WireGuard-Schlüssel, Zertifikate. Nach einer Wiederherstellung
trägt man sie neu ein. Zertifikate holt der Knoten selbst neu.

## Wiederherstellen

Auf einer **frischen** Maschine, mit dem Archiv:

```sh
sudo ./install.sh restore <archiv>.tar.gz
```

Das baut alle Instanzen neu auf, ohne Setup-Assistent, mit den alten
Passwörtern. Einzelne Instanzen oder ein einzelner Mandant gehen auf diesem
Weg nicht. **Eine ungeprüfte Sicherung ist keine:** Planen Sie einen
Probelauf auf einer Wegwerf-Maschine ein.

## Wenn es schiefgeht

- **`backup target … lies inside the platform data directory`**: Wählen Sie
  ein Ziel außerhalb von `/var/lib/oaap`.
- **`not enough room in …`**: Der Befehl misst vorher und bricht ab, statt
  nachts die Platte zu füllen. Machen Sie Platz, oder senken Sie `--keep`.
- **`this node has no nightly backup yet`** bei `oaap backup schedule`:
  Schritt 2 fehlt. Das Portal und `schedule` ändern nur einen Timer, den es
  schon gibt.
- **Der Nachtlauf ist gescheitert:** Der Grund steht auf der
  Gesundheitsseite und in `/var/lib/oaap/apps/backup-last.json`
  (`"state": "failed"`, `"message"`), ausführlich in
  `sudo journalctl -u oaap-backup.service` und `/var/log/oaap-backup.log`.
  Seit 0.1.249 nennt die Meldung den Exit-Code und die ersten echten
  Fehlerzeilen. Hinweise auf übersprungene Sockets (`socket ignored`) sind
  harmlos und keine Ursache: Instanzen wie code-server oder webtop legen
  solche Dateien an, und sie lassen sich weder sichern noch brauchen.
- **Die Apps standen länger als erwartet:** Die eigene Zahl steht in
  `backup-last.json` (`downtime_seconds`). Sie wächst mit der Zahl der
  Instanzen, nicht mit der Datenmenge allein.

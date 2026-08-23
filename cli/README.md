# OAAP CLI-Referenz

> Geprüft gegen Referenz **0.1.42** (2026-08-23).

Das Kommando `oaap` liegt auf jedem Knoten unter `/usr/local/bin/oaap`.
Grundsätze:

- **Fast alles braucht `sudo`** — Ausnahmen: `oaap status`,
  `oaap version`, `oaap node show`, `oaap store list`.
- **Das Portal kann das meiste auch.** Die CLI ist der Rettungsweg und
  der Weg für Automatisierung; im Alltag führt der Weg über
  Portal → „Instanzen" → Instanz anklicken.
- **Werte, die geheim sind** (Passwörter, Konfigurationsgeheimnisse),
  fragt die CLI versteckt ab, wenn man sie nicht als Argument angibt —
  so landen sie nicht in der Shell-Historie.

Inhalt: [Knoten](#knoten) · [Apps](#apps) · [Konfiguration &
Adressen](#konfiguration--adressen) · [Deployment](#deployment-test--produktiv) ·
[Store](#store) · [Netz: extern & Edge](#netz-externer-name--edge) ·
[Betrieb](#betrieb-backup-benutzer-flotte) · [Diagnose](#diagnose)

---

## Knoten

### `oaap status`

Gesundheit des Knotens ohne Portal: Version, Profile, Kerndienste,
Apps, Plattenplatz. Endet mit `HEALTHY` oder `DEGRADED` (Exit-Code 1).

```sh
oaap status
```

### `oaap version`

Nur die installierte Plattformversion.

### `sudo oaap setup-token`

Zeigt den Einrichtungs-Token für den ersten Browser-Setup erneut an —
nur solange noch kein Administrator existiert.

### `sudo oaap update [--check]`

Aktualisiert die Plattform aus der **hinterlegten Quelle** (kein
Auslöser kann eine andere Quelle unterschieben). Baut erst die neuen
Images und schaltet dann um — schlägt der Bau fehl, läuft alles Alte
weiter. Führt anschließend Konsistenzschritte (`migrate.sh`) aus, auch
wenn es nichts zu aktualisieren gab.

```sh
sudo oaap update --check   # zeigt nur, was sich ändern würde
sudo oaap update           # wendet an
```

Protokoll: `/var/log/oaap-update.log`. Merksatz: Fixes an der
Update-Engine selbst wirken erst beim **nächsten** Lauf.

### `oaap node show` · `sudo oaap node add-profile|remove-profile <profil>`

Wofür ist dieser Knoten da (RFC-0011)? Profil `dev` macht den Knoten
zur Werkbank: Das Portal darf dort Test-Instanzen anlegen und aus noch
nicht gelisteten Quellen installieren. Wird bewusst **nur an der
Maschine** gesetzt, nie im Portal.

```sh
oaap node show
sudo oaap node add-profile dev
sudo oaap node remove-profile dev
```

### `sudo oaap uninstall [--purge] [--yes]`

Entfernt die Plattform vom Knoten. Ohne `--purge` bleiben die Daten
unter `/var/lib/oaap/data` liegen (Wiederaufsetzen möglich); mit
`--purge` ist **alles weg**.

---

## Apps

### `sudo oaap app install <quelle> [--path <p>] [--ref <branch>] [--name <n>] [--channel test|production]`

Installiert eine App aus einem Git-Repository oder einem lokalen
Verzeichnis. `--path` zeigt in Monorepos auf den App-Ordner, `--name`
erlaubt mehrere Instanzen derselben App, `--channel` wählt Test- oder
Produktiv-Kanal (Standard: production).

```sh
sudo oaap app install https://github.com/MDJoerg/oaap-store --path apps/uptime-kuma
sudo oaap app install https://github.com/MDJoerg/oaap-apps --path apps/studio --channel test
sudo oaap app install <git-url> --name crm-test --channel test
```

Hinweise:

- Auf dem **Produktiv-Kanal** wird die Neuinstallation derselben
  Version abgelehnt — die Version ist die einzige Antwort auf „was
  läuft da?".
- Eine erneute Installation unter gleichem Namen ist das
  **Update** der Instanz: die Daten (Storage) bleiben erhalten.
- Im Portal geht dasselbe per Ein-Klick aus dem Store.

### `sudo oaap app list`

Alle Instanzen: App, Version, Kanal, Gateway-Port, Container.

### `sudo oaap app remove <instanz> [--purge]`

Entfernt eine Instanz. Ohne `--purge` bleibt ihr Storage liegen — eine
spätere Installation gleichen Namens findet die Daten wieder.

### `sudo oaap app visibility <instanz> all|groups <g1,g2>`

Sichtbarkeits-Gruppen (RFC-0007): Die App sehen und erreichen nur noch
Benutzer, die eine der Gruppen tragen. `server_admin` sieht immer
alles. Wird echt am Gateway durchgesetzt, nicht nur im Launchpad
versteckt.

```sh
sudo oaap app visibility finanzen groups buero,finanzen
sudo oaap app visibility finanzen all
```

### `sudo oaap app tile <instanz> [auto|on|off]`

Kachel im Launchpad: `auto` folgt der App-Klasse (Frontends zeigen
eine, Hintergrunddienste nicht), `on`/`off` erzwingen es. Ohne Modus
wird der aktuelle Stand gezeigt.

### `sudo oaap app link …` / `sudo oaap app endpoint …`

Verbindungen zwischen Apps (RFC-0016) und deklarierte Nicht-HTTP-Ports
(RFC-0015). Selten nötig — die üblichen Wege laufen über das Manifest
der App. Details: `sudo oaap app link --help` bzw.
`sudo oaap app endpoint --help`.

### `sudo oaap app convert <compose-datei> [--out <ordner>]`

Werkzeug für Paket-Bauer: erzeugt aus einer docker-compose-Datei ein
OAAP-App-Gerüst (Manifest + Struktur) als Startpunkt.

---

## Konfiguration & Adressen

### `sudo oaap app config list|set|unset <instanz> [<schlüssel>] [<wert>]`

Konfigurationswerte einer Instanz — nur die im Manifest deklarierten
Schlüssel. Geheimnisse werden nie zurückgezeigt (nur „gesetzt"/„leer")
und ohne Wert-Argument versteckt abgefragt. Der Container wird neu
erzeugt (kurz nicht erreichbar); Daten, Adressen und Version bleiben.
**Kein Versions-Bump nötig — auch auf Produktiv.**

```sh
sudo oaap app config list forgejo
sudo oaap app config set registry REGISTRY_PASSWORD        # fragt versteckt
sudo oaap app config unset studio STUDIO_GIT_BASE
```

### `sudo oaap app address set|show|remove <instanz> [<hostname>]`

Eigener öffentlicher Name für eine Instanz (RFC-0009/0018), zusätzlich
zur automatischen Unteradresse `<instanz>.<knotenname>`. Wichtig, wenn
die Adresse in ausgelieferte Software wandert. Der Name muss per DNS
auf den Knoten zeigen; das Zertifikat kommt automatisch.

```sh
sudo oaap app address set bdt-hub hub.beispiel.de
sudo oaap app address show bdt-hub
```

### `sudo oaap app throttle show|set|off <instanz> [<rate>/<sekunden>]`

Mengenbremse für **öffentliche** Routen (`roles: [public]`), Standard
300 Anfragen je 60 Sekunden und Client-Adresse. Ehrlich gesagt: eine
Mengenbremse, keine Zugangskontrolle — die App muss eigene Schlüssel
zusätzlich selbst sperren.

```sh
sudo oaap app throttle set registry 1000/60
sudo oaap app throttle off intern-nur-lan
```

---

## Deployment (Test → Produktiv)

Der rote Faden: Die Projekt-KI (oder das Studio) liefert auf die
**Test**-Instanz; nach Produktiv geht es **nur durch einen Menschen** —
und zwar exakt die getesteten Bytes (RFC-0019/0020).

### `sudo oaap app token create|list|revoke [<instanz>]`

Deploy-Token für eine **Test**-Instanz — der Schlüssel, mit dem eine
Projekt-KI über den Deploy-Hook (`POST /deploy/<instanz>`) neue Stände
liefert. Wird **einmal** angezeigt, gespeichert ist nur eine Prüfsumme.
Produktiv-Instanzen bekommen nie einen.

```sh
sudo oaap app token create crm-test
sudo oaap app token revoke crm-test
```

### `sudo oaap app grant list|revoke [<instanzname>]`

Anlege-Erlaubnisse (RFC-0019): einmal verwendbare, 30 Minuten gültige
Erlaubnis, mit der die **erste** Instanz über den Paket-Weg entstehen
darf. Ausgestellt wird sie im Portal; hier sieht man offene Erlaubnisse
und widerruft sie.

### `sudo oaap app artifact list|rollback <instanz> [<paket>]`

Aufbewahrte Pakete einer Instanz (aktuell + 3 Vorgänger) ansehen und
auf einen Vorgänger **zurückrollen** — der Rückweg, den die Übernahme
bewusst nicht hat.

```sh
sudo oaap app artifact list bdt-hub
sudo oaap app artifact rollback bdt-hub
```

### `sudo oaap app promote <teststand> [--to <produktiv>] [--confirm]`

Übernahme nach Produktiv (RFC-0020): installiert **dasselbe Paket**
(gleiche Prüfsumme) des Teststands auf die Produktiv-Instanz — bestehend
oder neu. Nur höhere Versionen; erweitert das Paket den Rahmen der
Produktiv-Instanz (neue öffentliche Route, neuer Speicher, neuer Port),
bricht der erste Versuch ab und **nennt jeden Grund** — erst dann
bestätigt man mit `--confirm`. Die Produktiv-Instanz behält Daten,
Konfiguration, Adressen und Gruppen.

```sh
sudo oaap app promote bdt-hub-test --to bdt-hub
sudo oaap app promote bdt-hub-test --to bdt-hub --confirm
```

---

## Store

### `oaap store list`

Konfigurierte Quellen mit Vertrauensklasse und Reihenfolge. Auflösung:
höchste Vertrauensklasse gewinnt; innerhalb einer Klasse entscheidet
die Reihenfolge (RFC-0012).

### `sudo oaap store add-source <url> [--name <n>] [--trust verified|unverified]`

```sh
sudo oaap store add-source \
  https://raw.githubusercontent.com/MDJoerg/oaap-apps/main/oaap-store.json \
  --name "OAAP Plattform-Apps"
```

Store-Quellen sind **je Knoten**, nicht flottenweit — bei neuen Knoten
daran denken.

### Weitere: `remove-source` · `enable` · `disable` · `trust` · `rename` · `reconcile`

`trust <quelle> verified|unverified` stuft eine Quelle ein;
`reconcile` gleicht die mitgelieferten Quellen mit dem Stand der
Plattformversion ab (läuft bei jedem `oaap update` automatisch mit).

---

## Netz: externer Name & Edge

### `sudo oaap external show|set|remove [<hostname>] [--behind-edge <edge-ip>]`

Registriert den öffentlichen Namen des Knotens: Zertifikate kommen
automatisch (Let's Encrypt), HTTP leitet auf HTTPS um, jede Instanz
bekommt ihre Unteradresse. Mit `--behind-edge` nimmt der Knoten seine
externen Namen nur noch vom Edge an (RFC-0006) und lässt das
TLS-Beenden dort.

```sh
sudo oaap external set oaap.beispiel.de
sudo oaap external set firma.beispiel.de --behind-edge 192.168.1.20
```

Der Name muss per DNS auf die öffentliche Adresse zeigen —
DynDNS-Aktualisierung gehört in den **Router**, nicht auf den Server.
Achtung Wildcard: `*.beispiel.de` deckt den **nackten Namen nicht** ab;
der Apex braucht seinen eigenen A-Record.

### `sudo oaap edge add|list|remove [<hostname>] [<ziel>] [--port <p>]`

Edge-Knoten (RFC-0006): Ein Knoten mit der einzigen Portfreigabe
routet fremde Hostnamen samt Subdomain-Baum an die zuständige
Plattform weiter. Geteilt wird nur der Eingang — Benutzer, Apps und
Backups bleiben je Plattform autonom.

```sh
sudo oaap edge add firma.beispiel.de 192.168.1.30
```

---

## Betrieb: Backup, Benutzer, Flotte

### `sudo oaap backup create [--to <ziel>]`

Plattform-Schnappschuss (Konfiguration, Registry, Instanz-Daten). Das
Ziel gehört **nie auf dieselbe Platte** — z. B. ein NAS-Mount. Das
Backup enthält alle Plattform-Geheimnisse: das Ziel muss exklusiv
berechtigt sein.

```sh
sudo oaap backup create --to /mnt/backup
```

### `sudo oaap user list` · `sudo oaap user password <benutzer> [<passwort>]`

Der Rettungsweg, wenn das Portal-Login klemmt: Konten mit Rollen und
Gruppen ansehen, Passwort neu setzen (meldet bestehende Sitzungen des
Kontos ab). Oft ist „ausgesperrt" nur ein falscher Benutzername —
erst `user list` ansehen.

### `sudo oaap fleet key issue|list|revoke [<label>]`

Flotten-Schlüssel (RFC-0021): erlaubt **ausschließlich** das Lesen der
Status-Auskunft `GET /fleet/status` dieses Knotens — für die
Flotten-Übersicht (FleetView) auf dem Verwaltungsknoten. Das Label
nennt den Beobachter; pro Beobachter ein eigener Schlüssel, dann bleibt
ein Widerruf gezielt. Der Wert wird **einmal** gezeigt; `revoke` wirkt
sofort.

```sh
sudo oaap fleet key issue fleetview@verwaltungsknoten
sudo oaap fleet key list
sudo oaap fleet key revoke fleetview@verwaltungsknoten
```

---

## Diagnose

```sh
oaap status                                          # Gesamtbild
sudo docker ps                                       # laufende Container
sudo docker logs oaap-identity-1                     # Login/Logout-Protokoll
sudo tail /var/lib/oaap/apps/deploy-log.jsonl        # letzte Deployments
sudo tail /var/log/oaap-update.log                   # letztes Update
sudo docker port oaap-gateway-1                      # fehlen 80/443? → Port-Rennen
nslookup <öffentlicher-name>                         # zeigt der Name noch hierher?
curl -s https://api.ipify.org                        # aktuelle öffentliche IP
```

**Port-Rennen beim Booten:** Belegt ein Fremd-Dienst mit
`restart=always` die Ports 80/443 vor OAAP, läuft das Gateway als „Up"
ohne veröffentlichte Ports. Fremd-Dienst entfernen, dann:
`cd /var/lib/oaap/app && sudo docker compose --project-name oaap up -d --force-recreate gateway`.

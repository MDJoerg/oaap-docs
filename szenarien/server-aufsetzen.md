# Einen OAAP-Server aufsetzen

> Geprüft gegen Referenz **0.1.42** (2026-08-23).
> Dauer: ~15 Minuten auf üblicher Hardware, plus Bauzeit der Container.

**Ausgangslage:** ein frisch installiertes **Debian 13** (64-bit, auch
Raspberry Pi OS 64-bit) mit Netzwerkzugang, ein Benutzerkonto mit
sudo-Recht.

## 1. Installieren

```sh
sudo apt install -y git
git clone https://github.com/MDJoerg/oaap-reference
cd oaap-reference && sudo bash install.sh
```

Der Installer prüft die Bereitschaft der Maschine, richtet die
Container-Laufzeit ein (wenn `OAAP_INSTALL_RUNTIME=1` gesetzt ist,
installiert er sie auch), baut die Kerndienste und startet sie.

- Setup-Daten danach: `~/oaap-setup.txt`
- Diagnose bei Problemen: `/var/log/oaap-install.log`
- WLAN-Maschine? Der Installer richtet einen WLAN-Wächter ein, der
  eine hängende Verbindung nach spätestens zwei Minuten zurückholt.
- Feste IP empfohlen: entweder per Router-Reservierung oder beim
  Installieren über `OAAP_STATIC_IP=<adresse>`.

## 2. Ersten Administrator anlegen

```sh
sudo oaap setup-token
```

Die angezeigte Adresse im Browser öffnen und mit dem Token den ersten
Administrator anlegen. Der Token gilt **einmal**, bis der erste
Administrator existiert. Danach: Anmelden am Portal, fertig.

## 3. Prüfen

```sh
oaap status        # muss mit HEALTHY enden
oaap version
```

Im Portal: Gesundheitsseite ansehen (Navigation oben — sichtbar für
`server_admin`).

## 4. Typische nächste Schritte

| Ziel | Weg |
| ---- | --- |
| Apps installieren | Portal → Store (siehe [App aus dem Store](app-aus-dem-store.md)) |
| Knoten zur Entwickler-Werkbank machen | `sudo oaap node add-profile dev` — nur auf Maschinen ohne echte Daten |
| Öffentlicher Name + HTTPS | DNS-Name auf die öffentliche Adresse zeigen lassen, dann `sudo oaap external set <name>` |
| Backup-Ziel einrichten | NAS-Mount, dann `sudo oaap backup create --to /mnt/backup` |
| Plattform aktuell halten | `sudo oaap update --check`, dann `sudo oaap update` |

## Wenn etwas hakt

- **Portal antwortet nicht:** `oaap status` — laufen 3/3 Kerndienste?
  `sudo docker port oaap-gateway-1` — fehlen 80/443, belegt ein
  Fremd-Dienst die Ports (Anleitung in der [CLI-Referenz →
  Diagnose](../cli/README.md#diagnose)).
- **Store meldet „Quelle nicht lesbar" direkt nach einem Neustart:**
  kurz warten — auf manchen Maschinen ist das Netz beim Start der
  Container noch nicht fertig; seit 0.1.7 wartet die Installation
  darauf, Altinstallationen heilt ein `sudo oaap update`.
- **Setup-Token verlegt:** `sudo oaap setup-token` zeigt ihn erneut,
  solange noch kein Administrator existiert.

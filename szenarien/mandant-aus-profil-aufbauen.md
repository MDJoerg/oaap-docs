# Einen Mandanten aus einem Profil aufbauen

> Geprüft gegen Referenz **0.1.183** (2026-10-03; die Seiten in Abschnitt 6
> gegen 0.1.184 im Test, nicht im Browser), auf `oaap-test`:
> Mandant, Richtlinie, Gesicht, App aus einem Paket, Wartepunkt,
> Fortsetzen nach einem hart beendeten Lauf, Rückbau, Portal-Aktion am
> echten Auftragsspeicher. **Noch nicht an einem echten Knoten gemessen:**
> die Schritte `idp.provision` (Realm), `address.ensure` und `address.wait`
> (echte Außenadresse) — `oaap-test` hat keinen Außennamen. Spezifikation:
> RFC-0055. Platzhalter: `<kürzel>` (Mandant), `<profil>` (Name der
> Profildatei ohne `.json`), `<id>` (Kennung eines Aufbaus).

Ergebnis: ein Mandant, wie ihn [Einen Kunden-Mandanten mit eigenem
Anmeldebereich einrichten](kunden-mandant-anlegen.md) von Hand baut — aber
in **einem Aufruf**, mit sichtbarem Verlauf je Schritt, wiederholbar und
nach einem Abbruch fortsetzbar.

## Wann das Profil, wann von Hand?

- **Profil:** Sie bauen mehrere ähnliche Mandanten (Vereine, Kunden), oder Sie
  wollen den Ablauf festhalten und prüfen lassen.
- **Von Hand:** ein einzelner Sonderfall, oder ein Schritt, den es als
  Schrittart nicht gibt.

## 1. Das Profil

Ein Profil ist eine kleine JSON-Datei in `/var/lib/oaap/profiles/`
(Eigentümer `root`; im Portal lässt sie sich nicht hochladen). Sie nennt
**Parameter** (Werte, die beim Start gefragt werden) und eine geordnete Liste
von **Schritten**.

```json
{
  "profile": "oaap.tenant-profile/1",
  "id": "verein-standard",
  "title": "Verein mit eigenem Anmeldedienst",
  "params": {
    "label": {"kind": "label", "required": true},
    "title": {"kind": "text", "required": true, "max": 60},
    "color": {"kind": "color", "default": null}
  },
  "steps": [
    {"id": "tenant",  "type": "tenant.create", "label": "{label}", "title": "{title}"},
    {"id": "address", "type": "address.ensure"},
    {"id": "reachable", "type": "address.wait", "timeout": 120},
    {"id": "realm",   "type": "idp.provision", "connector": "auth",
                       "idp_label": "Mit dem Vereinskonto anmelden"},
    {"id": "policy",  "type": "tenant.policy", "first_login": "role",
                       "default_role": "user", "self_registration": "off"},
    {"id": "face",    "type": "tenant.face", "title": "{title}",
                       "color_primary": "{color}"},
    {"id": "web",     "type": "app.install", "source": "/srv/pakete/website-starter",
                       "name": "webseite", "channel": "test"},
    {"id": "admin",   "type": "manual",
                       "text": "Ersten Verwalter im Realm anlegen, dann im Portal tenant_admin vergeben.",
                       "done_when": "role.tenant_admin"},
    {"id": "backup",  "type": "backup.check"}
  ]
}
```

**Die Schrittarten** sind eine feste Liste. Ein Profil kann keinen eigenen
Befehl enthalten; mit einer unbekannten Schrittart oder einem unbekannten
Argument wird es **ganz abgelehnt, bevor etwas läuft**.

| Schrittart | Tut | Gilt als erledigt, wenn … |
|---|---|---|
| `tenant.create` | `oaap tenant create` | der Mandant da ist **und von diesem Aufbau angelegt wurde** |
| `address.ensure` | veröffentlicht die Adresse im Gateway | die Gateway-Seiten den Mandantennamen nennen (ohne Außennamen: nichts zu tun) |
| `address.wait` | wartet, bis `https://<kürzel>.<knoten>/` antwortet | 200, 302 oder 303 |
| `idp.provision` | Realm und Client im Anmeldedienst anlegen (`oaap idp provision`) | der Mandant einen Anbieter eingetragen hat |
| `tenant.policy` | `oaap tenant policy` | die Richtlinie wie gewünscht gespeichert ist |
| `tenant.face` | `oaap tenant face` (Titel, Farben) | die gespeicherten Werte stimmen |
| `app.install` | `oaap app install <Quelle> --tenant … --name …` | die Instanz im Mandanten existiert |
| `manual` | nichts — **ein Mensch** | die Lesung `done_when` stimmt (siehe 3.) |
| `backup.check` | nichts | der Mandant im Knotenarchiv enthalten ist (nicht ausgenommen) |

**Ein Schritt gilt erst als erledigt, wenn seine Prüfung es bestätigt** — nicht
schon, weil der Befehl ohne Fehler zurückkam.

**Werte sind Werte.** `{label}` wird durch den Parameter ersetzt, nachdem er
nach seiner Art geprüft wurde (`label` mit den Kürzel-Regeln, `color` als
`#rrggbb`, `text` mit Längengrenze und ohne Steuerzeichen). Nichts davon wird
je als Befehl gedeutet.

## 2. Aufbau starten

```sh
sudo oaap tenant build profiles
sudo oaap tenant build start <profil> --param label=<kürzel> \
     --param title="Klarname des Kunden" --dry-run
sudo oaap tenant build start <profil> --param label=<kürzel> \
     --param title="Klarname des Kunden"
```

- `profiles` zeigt jede Profildatei; eine fehlerhafte steht mit ihrem Grund da.
- `--dry-run` zeigt die Schritte mit den eingesetzten Werten und ändert
  **nichts**. Immer zuerst.
- Ein Parameter, den das Profil nicht kennt, wird abgelehnt (ein Tippfehler
  wird nicht still verschluckt). Ein vergebenes Kürzel wird abgelehnt, bevor
  Schritt 1 etwas anlegt.
- Pro Kürzel läuft **ein** Aufbau zur Zeit.

Die Ausgabe zeigt jeden Schritt mit Zustand und einem Satz; sie endet mit
`DONE`, `WAITING` oder `FAILED`.

```sh
sudo oaap tenant build show             # alle Aufbauten
sudo oaap tenant build show <id>        # einer, mit allen Schritten
sudo oaap tenant build show <id> --json # maschinenlesbar
```

Der Zustand liegt in `data/tenant-builds/<id>.json` (Modus 0600, **ohne
Geheimnisse**). Profil und Werte sind mit einer Prüfsumme **festgehalten**.

## 3. Der Wartepunkt: der erste Verwalter

**OAAP legt nie eine Person im Anmeldedienst des Kunden an.** Den ersten
Verwalter legt ein Mensch an (siehe [Kunden-Mandanten einrichten](kunden-mandant-anlegen.md),
Abschnitt 4). Im Profil steht dafür ein Schritt `manual`; der Aufbau hält dort
an (`WAITING`) und geht weiter, wenn die Lesung stimmt:

| `done_when` | Stimmt, sobald … |
|---|---|
| `user.exists` | es irgendein Konto in diesem Mandanten gibt |
| `role.tenant_admin` | ein Konto des Mandanten `tenant_admin` trägt |
| `confirmed` | ein Mensch es bestätigt hat |

```sh
sudo oaap tenant build continue <id>                      # liest neu, geht weiter
sudo oaap tenant build confirm <id> --step <schritt>      # nur bei done_when "confirmed"
```

## 4. Fehler, Abbruch, Fortsetzen

**Fortsetzen ist der Standard.** Scheitert ein Schritt, steht sein Grund im
Verlauf. Ursache beheben, dann:

```sh
sudo oaap tenant build continue <id>
```

Fertige Schritte werden nur **neu gelesen**, nicht wiederholt. Gemessen: ein
Aufbau, dessen Prozess hart beendet wurde (`kill -9`), blieb im Zustand
`running` und wurde ohne doppelte Arbeit fortgesetzt.

| Befund | Was Sie tun |
|---|---|
| Ein Schritt ist `failed` | Ursache beheben, `continue` |
| `continue` sagt „the profile file changed … digest differs“ | die Datei wiederherstellen — oder den Aufbau zurückbauen und neu starten |
| ein fertiger Schritt ist „no longer in place“ | jemand hat das Ergebnis entfernt; der Aufbau hält an, statt es still neu zu machen. Entscheiden, dann zurückbauen oder von Hand ergänzen |
| „this build is being driven by another process“ | es läuft wirklich einer; ein beendeter Prozess gibt die Sperre sofort frei |
| der Aufbau für das Kürzel ist „not finished“ | `continue` oder `rollback` des offenen Aufbaus, dann neu starten |

## 5. Zurückbauen

```sh
sudo oaap tenant build rollback <id>          # nennt nur, was geschähe
sudo oaap tenant build rollback <id> --yes    # tut es
```

Zurückgebaut wird **nur, was dieser Aufbau selbst angelegt hat**, in
umgekehrter Reihenfolge:

- eine **Instanz** wird entfernt, **ihre Daten bleiben erhalten**. Die Daten
  einer entfernten Instanz halten den Mandanten fest, deshalb stoppt der
  Rückbau dann beim Mandanten und sagt, warum. Wer die Daten bewusst
  mitlöschen will, sagt es: `--purge-instances`.
- ein **leerer** Mandant wird entfernt (`oaap tenant remove`); ein Mandant mit
  Inhalt nie.
- der **Anbieter** wird vom Mandanten gelöst; **der Realm und jede Person
  darin bleiben** (ein Verein verliert seine Mitglieder nicht, weil ein Aufbau
  abgebrochen wurde).
- Ein Mandant, den es **schon vor dem Aufbau** gab, wird nie angefasst — der
  Start lehnt ein vergebenes Kürzel ab.

Ein Rückbau, der nicht fertig wird, bleibt `FAILED` mit dem Rest; `continue`
macht ihn zu Ende.

## 6. Aus dem Portal und über die API

Dieselbe Mechanik steht als **Portal-Aktion** und als **Betreiber-API**
bereit: `/api/v1/operator/tenant-profiles`, `…/tenant-builds`,
`…/tenant-builds/<id>` (lesen), `POST …/tenant-builds` mit
`{"profile": "…", "params": {…}}` und `POST …/tenant-builds/<id>/continue|confirm|rollback`.

- Nur **`server_admin`**, und nur an der Adresse des Knotens selbst (am Ort
  eines Mandanten antworten die Routen mit 404).
- Es muss ein **angemeldeter Mensch** sein (Browser-Sitzung mit dem Kopf
  `X-OAAP-API: 1`). **Ein API-Schlüssel kann die Betreiber-API nie aufrufen**:
  Maschinenkonten bekommen die Rolle `server_admin` nicht (RFC-0027).
- Die Anfrage nennt ihre Rolle nicht selbst; der Knoten liest sie aus dem
  Benutzerspeicher.
- Eine Anfrage ist ein Auftrag (`202`) mit Status unter
  `/api/v1/tenant/jobs/<id>`; die Lese-Aufrufe antworten aus einer
  Sicht-Datei, die der Knoten nach jedem Schritt schreibt.
- Die **Seiten** dazu (Referenz 0.1.184): Menüpunkt **Aufbau** (nur für den
  Betreiber am Knoten selbst) — Liste der Profile und Aufbauten, ein Formular aus
  den Parametern des Profils, und je Aufbau eine Seite. Was auf einen Menschen
  wartet, steht oben mit **Weiter prüfen** (und **Bestätigt**, wo `done_when`
  `confirmed` ist); ein fehlgeschlagener Schritt bietet **Fortsetzen**; ganz
  unten steht **Zurückbauen**, das das Kürzel verlangt und die Daten der
  Instanzen nur mit eigenem Haken mitlöscht. Die Seiten schreiben nichts selbst:
  jede Schaltfläche stellt dieselbe Anfrage wie die API. Noch nicht an einem
  laufenden Portal im Browser gesehen.

## Protokoll

Jeder Schritt steht im **Mandantenprotokoll** (`oaap tenant log <kürzel>`)
und im Protokoll des Standard-Mandanten; ein Kunde sieht dort, was in
seinem Namen getan wurde. Zeilen: `tenant.build.step`, `tenant.build.done`,
`tenant.build.rollback`; abgelehnte Anfragen des Portals als
`tenant.build.denied`.

## Prüfliste

- [ ] `oaap tenant build start … --dry-run` zeigt die erwarteten Schritte und Werte
- [ ] der Aufbau endet in `WAITING` am Schritt für den Verwalter, nicht in `FAILED`
- [ ] `oaap tenant list` zeigt den Mandanten
- [ ] nach dem Verwalter: `continue` endet in `DONE`
- [ ] `oaap tenant log <kürzel>` zeigt die Schritte
- [ ] `oaap backup status` zeigt den Mandanten „in the node backup“
- [ ] danach die Prüfliste aus [Kunden-Mandanten einrichten](kunden-mandant-anlegen.md)
      und [Mandant übergeben](mandant-an-kunden-uebergeben.md) durchgehen

# Neuer Vereinsmandant mit fachlichen Rollen — Checkliste

> Geschrieben für den ersten echten Verein auf **oaapx02** (2026-10-18). Jeder
> Handgriff stammt aus einer Übung auf `oaap-test` mit Referenz **0.1.204**, echtem
> Keycloak 26.7.4 und dem Rollenkatalog des Handball-Vereins. **Auf oaapx02 ist
> nichts davon geprüft** (dort hat Claude keinen Zugang) — wo die Maschine etwas
> anderes sagt, gilt die Maschine, und der Unterschied gehört in
> `CURRENT_STATE.md`. Platzhalter: `<mandant>` (Kürzel), `<app>` (App-ID der Vereinsapp).
> Hintergrund: [Fachliche Rollen einrichten](fachliche-rollen-einrichten.md),
> [Mandant aus einem Profil aufbauen](mandant-aus-profil-aufbauen.md),
> [Vorgänge im Mandanten](vorgaenge-im-mandanten.md).

**Der Weg in einem Satz:** Knoten aktuell → Anmeldedienst als Anbindung → Mandant mit
eigenem Realm → Vereinsapp → Rollen aus den Vorlagen (`setup`) → erster Verwalter →
Gruppen füllen → erster Login.

## 0. Vorher ansehen (zwei Minuten)

```sh
sudo oaap version                     # soll 0.1.204 sein, sonst Schritt 1
sudo oaap status | tail -1            # HEALTHY?
sudo oaap idp list                    # gibt es die Anbindung `auth`? sonst Schritt 2
sudo oaap external show               # der Außenname des Knotens
sudo oaap tenant list
```

Merke dir die Zahl der laufenden Apps und `sudo oaap status`; nach jedem größeren
Schritt vergleichen.

## 1. Knoten aktualisieren

```sh
sudo oaap update
```

Erwartet: `Update complete: … -> 0.1.204`. Es startet nur Identity (und bei Bedarf Portal) neu,
nicht das Gateway. Wirkt sich auf offene Verbindungen nicht aus. Die nächtliche Sicherung
stoppt kurz alle Apps (auf oaapx01 03:33 UTC) — nicht in diese Minuten legen.

## 2. Anmeldedienst als Anbindung eintragen (einmal je Knoten)

Ohne Anbindung kann OAAP keinen Realm für den Verein anlegen.

- Läuft Keycloak (`auth`) schon als App? `sudo oaap app list | grep auth`.
- **Das Dienstkonto `oaap-admin`** im **master**-Realm braucht genau eine Rolle,
  `create-realm` — das ist Handarbeit in der Keycloak-Oberfläche
  (`oaap-apps/apps/keycloak/README.md`, „Das Dienstkonto, das OAAP dafür braucht").
- Eintragen und prüfen:

```sh
sudo oaap idp add auth --url https://auth.<knoten> \
  --admin-id oaap-admin --admin-secret '<Geheimnis des Dienstkontos>' --accept-version 26.7.4
sudo oaap idp check auth
```

Stolperer, die schon passiert sind:

- **Nie `kc.sh` per `docker exec` im laufenden Keycloak-Container starten** (nicht für einen
  Admin, nicht für Export). Es baut den Container still auf eine leere H2-Datenbank um.
  Dafür gibt es Wegwerf-Container (README der Keycloak-App).
- `--accept-version` ist nötig, weil das Dienstkonto zu schmal ist, die Fassung selbst zu lesen.
  Die Ausgabe sagt „STATED by the operator" — das ist dein Wort, nicht eine Messung.

## 2b. Postfach des Knotens (einmal je Knoten, ab 0.1.233)

Ohne Postfach verschickt der Realm des Vereins **keine Mail**: kein „Passwort vergessen“,
keine Bestätigung, keine Einladung. Einmal eintragen, dann bekommt es **jeder neue Realm**
automatisch (Absendername = Name des Vereins, Sprache Deutsch):

```sh
sudo sh -c 'umask 077; cat > /root/mailpw'     # Passwort eintippen, Strg-D
sudo oaap mail set --target smtps://<mailserver>:465 --from <absender@domain> \
  --user <login> --password-file /root/mailpw
sudo oaap mail test <deine adresse>             # kommt sie an (auch im Spam-Ordner nachsehen)?
sudo oaap idp mail auth --all                   # bestehende Realms nachziehen
sudo rm /root/mailpw
```

`smtp://<mailserver>:587` statt `smtps://` heißt STARTTLS. Unverschlüsselt gibt es nicht.
Keycloak muss den Mailserver erreichen können.

**Ab 0.1.234 im Portal:** Menü **Nachrichten → Postausgang**. Als Server-Admin am Knoten
pflegst du dort das Postfach des Knotens und siehst, welcher Mandant womit verschickt. Der
**Mandanten-Admin** eines Vereins kann dort ein **eigenes Postfach** eintragen, mit eigener
Absender-Domain. Speichern meldet sich zuerst probeweise am Server an, dann wird es in den
Realm des Vereins geschrieben. Nur Port 465 oder 587, und der Server muss im Internet stehen.
Entfernen schaltet zurück auf das Postfach des Knotens.

## 3. Mandant mit Realm anlegen

Entweder in einem Aufruf aus einem **Profil** (Verlauf, Fortsetzen, Rückbau) oder von Hand.

**Von Hand:**

```sh
sudo oaap tenant create <mandant> --name "Name des Vereins"
sudo oaap idp provision auth --tenant <mandant> --idp-label "Mit dem Vereinskonto anmelden" --dry-run
sudo oaap idp provision auth --tenant <mandant> --idp-label "Mit dem Vereinskonto anmelden"
sudo oaap tenant policy <mandant> --first-login role --default-role user
```

Zu `--first-login`: `eingang` (neue Person landet im Eingang, ohne Rechte, bis ein Mensch
entscheidet), `role` (bekommt die Standardrolle), `groups`. **Eine Standardrolle gilt für
den ganzen Mandanten.** Sponsoren (`partner`) und Mitglieder unterscheidet nur der
Mandanten-Admin je Person im Portal — eine Gruppe kann keine Plattformrolle geben.

Die Adresse `<mandant>.<knoten>` muss antworten (`address.wait` im Profil prüft das).
Ohne Außennamen des Knotens scheitert `idp provision` — auf oaapx02 sollte das nicht sein.

**Mit Profil:** siehe das Szenario „Mandant aus einem Profil aufbauen". Schritte
`tenant.create`, `address.ensure`, `address.wait`, `idp.provision`, `tenant.policy`,
`tenant.face`, `app.install`, `authz.setup`, `idp.admin_group` (Verwaltergruppe im Realm, ab 0.1.233), `manual` (erster Verwalter), `backup.check`.
Der Schritt `app.install` nimmt nur eine **App des Katalogs** oder einen Pfad/eine Adresse.
**Ab 0.1.233** geht auch die Vereinsapp aus dem **Paketkatalog** (ZIP hochladen und freigeben,
App-Id `hbvp`), auch in einem im Portal hochgeladenen Profil.

**Fertiges Profil:** [`profile/handballverein.json`](profile/handballverein.json): Mandant,
Gesicht, Adresse, Realm (mit dem Postfach des Knotens, deutsch), Verwaltergruppe, Regel für die
erste Anmeldung (`role`/`user`, keine Selbstregistrierung), `hvp-test` und `hvp` (App `hbvp`),
`vorgaenge-test` und `vorgaenge`, Haken „Rollen & Rechte“ (`rechte`, an), Rollen aus den Vorlagen,
erster Verwalter (wartet), Sicherung. Hochladen unter Portal → **Aufbau** → „Profil hochladen“,
dann „Aufbau starten“. Danach von Hand: Deploy-Token für `hvp-test`
(`oaap app token create <kürzel>-hvp-test`), die Partner in den Vorgängen und die
**Konfiguration der Vereinsapp** in beiden Instanzen (Portal → Instanzen → Konfiguration):
`HIB_MODE` = `club` (sonst kommt jeder `admin`/`keyuser` ohne fachliche Rolle hinein),
`HIB_OPERATOR_NAME`, `HIB_CONTACT`, und für Push je Instanz ein eigener
`HIB_FAN_VAPID_PRIVATE` (FAQ F37). Das Profil kann das noch nicht mitgeben (I-42).
Gelaufen am 2026-11-09 auf oaapx02 mit 0.1.246 für den zweiten Vereinsmandanten: alle 15
Schritte grün, neuer Realm mit Postfach, erster Verwalter wie beschrieben. Voraussetzung:
Keycloak-App ≥ 0.1.7 (FAQ F34).

**Der Instanzname bekommt das Mandantenkürzel immer vorangestellt** (`name: verein` im
Mandanten `sgl` ergibt `sgl-verein`); das Kürzel nicht noch einmal in den Namen schreiben.

## 4. Die Vereinsapp installieren

```sh
sudo oaap app install <paket.zip> --tenant <mandant> --name <app>-test --channel test
sudo oaap app token create <mandant>-<app>-test       # EINMAL angezeigt; ihrem CI-Ziel mitgeben
sudo oaap authz declarations --tenant <mandant>       # die Vorlagen der App müssen hier stehen
```

- **Neue Rolle an einer Route** (z. B. `partner` auf `/`) wird gegen das verglichen, was die
  Instanz schon hatte. Die **allererste** Installation hat nichts zum Vergleichen und hält
  **nichts an**, **meldet** aber (ab 0.1.206) am Ende der Ausgabe `NOTE: first installation …`
  mit den Rollen jenseits von `user` und den Routen ohne Anmeldung, und schreibt es ins Protokoll
  des Mandanten. Lies diese Zeilen — dort steht `/ (partner)`, wenn das Manifest es verlangt.
  Jede **spätere** Fassung, die eine Rolle dazunimmt, hält der Deploy-Hook an, bis du im
  Portal bestätigst; der Befehl `oaap app install` verlangt es bei einer Produktiv-Instanz
  mit `--confirm` und zeigt es bei einer Test-Instanz nur als `NOTE:`.
- Der Deploy-Hook gehört zu **dieser** Test-Instanz und hat ein **eigenes** Token. Das CI
  von hbsha braucht dafür ein zweites Ziel (Adresse + Token) neben `hbvp-portal-test`.
- Für `vorgaenge` und die Partner-Einträge: [Vorgänge im Mandanten](vorgaenge-im-mandanten.md).

## 5. Rollen einrichten

```sh
sudo oaap authz setup --tenant <mandant> --app <app> --accept-version 26.7.4 --dry-run
```

Lies den Probelauf Zeile für Zeile:

- `[ready]` — wird gemacht; hinter `group` steht der Pfad und woher er stammt.
- `[conflict]` — ein Name ist belegt. Ausweg: `--name-for <schlüssel>="anderer Name"`.
- `[skipped]` — braucht eine Entscheidung (Vorlage mit Werten) oder wurde abgewählt.
- Eine Vorlage **ohne** Gruppe: `--group-for <schlüssel>=Verein/Name`.

Dann ohne `--dry-run`. Ein zweiter Aufruf muss `Nothing to do.` sagen. Die Gruppen stehen
danach **leer** im Realm (`Verein/Trainer`, …).

Prüfen, unabhängig vom Befehl: In der Keycloak-Oberfläche des Realms → Gruppen → die Gruppe
`Verein` hat die Untergruppen. (Beim Üben: gemessen, indem die Kinder von `/Verein` direkt
gelesen wurden.)

## 6. Der erste Verwalter

OAAP legt **nie** eine Person im Realm des Vereins an. Das ist Absicht (Mitgliederliste ist
Sache des Vereins).

1. Im Realm eine Person anlegen (oder sie meldet sich selbst an, wenn Selbstregistrierung an ist:
   `sudo oaap idp settings auth --tenant <mandant> --self-registration on`).
2. Sie meldet sich einmal am Mandantenort an → die Person erscheint im Portal.
3. Im Portal → **Benutzer → Rollen**: `tenant_admin` vergeben. **Sie muss sich danach neu
   anmelden**, Rollen gelten pro Sitzung.
4. Soll dieser Verwalter auch Personen im Anmeldedienst pflegen:
   `sudo oaap idp admin-group auth --tenant <mandant>` und ihn in die Gruppe `oaap-verwalter` stecken.
5. Wartet ein Aufbau-Profil auf „erster Verwalter", läuft es mit
   `sudo oaap tenant build continue <id>` weiter.

## 7. Gruppen füllen und den ersten Login messen

Das ist die Messung, die uns fehlt.

1. Im Realm eine Person in `Verein/Trainer` stecken.
2. Die Person meldet sich **neu** an (die Gruppen werden bei **jedem** Login gelesen).
3. Rechte ansehen: Installiere die Verwaltungs-App einmal in den Mandanten —

```sh
sudo oaap app install https://github.com/MDJoerg/oaap-apps --path apps/rollen-rechte \
  --tenant <mandant> --name rechte --confirm-administer
```

   — und öffne die Seite der Person: unter „darf zur Zeit" soll `team coach` stehen, bei
   „Woher" **Gruppe `Verein/Trainer` (bei jeder Anmeldung gelesen)**.
4. Austritt: die Person aus der Gruppe nehmen, neu anmelden → die Zeile steht danach als
   „beendet". Entfernt man dagegen die **Abbildung**, endet es sofort.

Sagt die Seite nichts, dann in dieser Reihenfolge nachsehen:

```sh
sudo oaap authz mappings --tenant <mandant>      # steht die Gruppe als Pfad da?
sudo oaap tenant log <mandant> -n 30             # authz.idp-sync beim Login?
sudo oaap tenant idp <mandant>                   # kommt die Anmeldung über den richtigen Realm?
```

Häufigste Ursache nach allem, was wir kennen: Der Pfad stimmt nicht Zeichen für Zeichen
(Groß-/Kleinschreibung), oder die Gruppe wurde umbenannt — die Abbildung gilt nach Pfad.

## 8. Was wir wissen und was nicht

**Belegt (oaap-test, 0.1.204):** Plan und Befehl `setup` mit Probelauf, Wiederholung,
Konflikt und `--name-for`; fünf bis sechs Gruppen entstehen im echten Keycloak, leer;
`oaap user add --tenant <Kürzel>` (vor 0.1.203 abgelehnt); eine neue Rolle an einer Route
hält die Installation an; der Aufbau aus einem Profil läuft bis zum Wartepunkt „erster Verwalter".

**Nicht belegt:** die Anmeldung einer Person mit Gruppe im Browser; der Aufruf von
`…/effective` mit diesen Rollen aus der Vereinsapp; `idp.provision` und `address.*` in der
echten Kette dieses Knotens (Realm und Anbieter wurden auf oaap-test von Hand gesetzt); die
Aufbauseite im Portal mit dem Schritt `authz.setup`.

**Wenn etwas schiefgeht:** Meldung wörtlich festhalten, `sudo oaap tenant log <mandant>` und
`sudo oaap tenant build show <id>` dazulegen — Fehler sind hier ausdrücklich erwünscht, sie
sagen uns, was als Nächstes gebaut werden muss.

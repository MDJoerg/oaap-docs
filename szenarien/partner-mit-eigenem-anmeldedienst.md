---
id: szenario/partner-mit-eigenem-anmeldedienst
title: "Partner und Kunden mit eigenem Anmeldedienst — Broker vor dem Realm des Mandanten"
audience: [server_admin, tenant_admin, support]
applies_from: "0.1.297"
checked_against: "0.1.297"
checked_on: 2026-11-18
lang: de
tags: [anmeldung, keycloak, broker, entra, google, partner, erstanmeldung, idp, sso]
---
# Partner und Kunden mit eigenem Anmeldedienst — Broker vor dem Realm des Mandanten

> Geprüft gegen Referenz **0.1.297** (2026-11-18) auf `oaap-test` mit
> Keycloak 26.7.4: Broker lesen, offen/geschlossen, Ablehnung der
> Erstanmelde-Richtlinie, Quittung, Eintrag im Mandantenlog. **Nicht
> gemessen:** eine echte Anmeldung über einen fremden Dienst (Entra,
> Google) im Browser und der Gruppen-Mapper am Broker. Spezifikation:
> `oaap.core.tenant` 1.8 §2.10.1, RFC-0091. Platzhalter: `<mandant>`,
> `<konnektor>`, `beispiel.de`, `partner.example`.

Ein Beispiel: Eine Beratungsfirma arbeitet auf OAAP im Mandanten
`<mandant>`. Die eigenen Mitarbeitenden haben Konten im Anmeldedienst
des Mandanten. **Partner** sollen sich mit ihrem Firmenkonto (Microsoft
Entra) anmelden, **Kunden** mit ihrem Google-Konto, ohne dass jemand für
sie ein Passwort anlegt.

Das geht über **Broker**: Der Anmeldedienst des Mandanten (ein
Keycloak-Realm) stellt einen fremden Anmeldedienst vor sich. Wer sich
dort anmeldet, kommt als Person im Realm an. OAAP sieht immer nur den
Realm, nie Entra oder Google selbst.

## Wer stellt was ein

| Was | Wo | Wer |
|---|---|---|
| Broker anlegen (Entra, Google, fremdes Keycloak) | Keycloak-Konsole, Realm des Mandanten | Betreiber des Servers |
| Was eine **erste** Anmeldung bekommt | `oaap tenant policy` | `server_admin` |
| Einen Broker als „geschlossen“ quittieren | `oaap tenant policy --broker-closed` | `server_admin` |
| Personen und Gruppen im Realm | Keycloak-Konsole, Gruppe `oaap-verwalter` | Verwaltung des Mandanten |
| Fachliche Rechte je Gruppe | [Fachliche Rollen einrichten](fachliche-rollen-einrichten.md) | Verwaltung des Mandanten |
| Rollen auf der Plattform (`user`, `keyuser`, `admin` …) | Portal, Benutzer | Verwaltung des Mandanten |

Die Verwaltungsgruppe `oaap-verwalter` darf **keine** Broker anlegen. Ein
neuer Broker ist eine neue Tür in den Mandanten, und auf einem Server
mit mehreren Kunden entscheidet das der Betreiber.

## Offen oder geschlossen: die Regel

Ein Broker lässt jeden herein, den der fremde Dienst kennt. OAAP liest
die Broker und sortiert sie so:

| Broker | geschlossen, wenn | sonst |
|---|---|---|
| Google | eine Domäne eingetragen ist (*Hosted domain*, nicht `*`) | offen: jedes Google-Konto |
| Microsoft / Entra | genau ein Verzeichnis eingetragen ist (Verzeichnis-ID oder Domäne) | offen bei `common`, `organizations`, `consumers` |
| GitHub, GitLab, Facebook … | nie | offen |
| fremdes OIDC/SAML, z. B. das Keycloak eines Partners | der Betreiber quittiert es mit Begründung | offen |
| abgeschaltet | — | keine Tür |

**Geschlossen heißt nicht willkommen.** Ein geschlossener Entra-Broker
lässt immer noch alle Mitarbeitenden dieses Verzeichnisses herein. Was
sie dann dürfen, entscheidet die Erstanmelde-Richtlinie.

Ein offener Broker zählt wie die Selbstregistrierung: Eine Richtlinie,
die bei der ersten Anmeldung eine Rolle vergibt (`role` oder `groups`),
lehnt OAAP ohne Begründung ab.

## 1. Voraussetzungen

- Der Mandant meldet über einen eigenen Realm an, angelegt über einen
  Konnektor dieses Servers (siehe
  [Kunden-Mandant anlegen](kunden-mandant-anlegen.md)). Prüfen:
  `sudo oaap tenant policy <mandant>` zeigt eine Zeile `made by
  connector '<konnektor>'`.
- Zugang zur Keycloak-Konsole als Administrator des Servers.
- Vom Partner: eine App-Registrierung in seinem Entra mit
  **Verzeichnis-ID**, Client-ID und Geheimnis; als Weiterleitungsadresse
  trägt der Partner die Adresse ein, die Keycloak beim Anlegen des
  Brokers anzeigt (*Redirect URI*).
- Für Google: ein OAuth-Client in einem Google-Cloud-Projekt, ebenfalls
  mit der Weiterleitungsadresse aus Keycloak.

## 2. Schritte

### Schritt 1: Ansehen, was heute gilt

```sh
sudo oaap tenant policy <mandant>
```

**Prüfen:** Die Zeile `first login` sagt, was eine erste Anmeldung
bekommt. Die Zeile `brokers none in the space` heißt: Bisher ist die
Anmeldeseite die einzige Tür.

### Schritt 2: Den Partner-Broker anlegen (Entra, ein Verzeichnis)

In der Keycloak-Konsole: Realm des Mandanten → *Identity providers* →
*Microsoft*. Eintragen: Client-ID, Geheimnis und bei *Tenant* die
**Verzeichnis-ID** des Partners, nicht `common` oder `organizations`.
Einen kurzen Alias wählen, z. B. `partner-entra`.

*Trust email* bleibt **aus**. Sonst übernimmt der Realm die
E-Mail-Adresse, die der fremde Dienst nennt, ungeprüft als bestätigt.

**Prüfen:** In der Liste der Identity Provider steht `partner-entra`
mit *Enabled*.

### Schritt 3: Den Kunden-Broker anlegen (Google)

*Identity providers* → *Google*. Haben alle Kunden **eine** gemeinsame
Domäne, diese bei *Hosted domain* eintragen, dann ist der Broker
geschlossen. Meist haben Kunden verschiedene Domänen oder private
Konten. Dann bleibt das Feld leer, und der Broker ist **offen**:
Jedes Google-Konto der Welt kommt dann bis in den Realm.

**Prüfen:** `google` steht in der Liste.

### Schritt 4: OAAP lesen lassen

```sh
sudo oaap idp settings <konnektor> --tenant <mandant>
sudo oaap tenant policy <mandant>
```

Der erste Befehl ändert nichts. Er liest den Realm und schreibt die
Antwort in den Datensatz des Mandanten. Ohne diesen Befehl liest OAAP
den Realm einmal täglich ab 05:10 Uhr.

**Prüfen:** Je Broker steht eine Zeile da:

```text
  broker       partner-entra (microsoft): closed
                 the broker 'partner-entra' admits only the directory …
  broker       google (google): OPEN
                 the broker 'google' admits any google account
```

Ist ein Broker neu offen, steht im Mandantenlog `tenant.idp-door`.
Zusätzlich geht die Meldung *Eine neue offene Tür am Anmeldedienst*
an die Verteiler, die sie zugeordnet haben (Kategorie Sicherheit).

### Schritt 5: Festlegen, was eine erste Anmeldung bekommt

Die sichere Wahl, wenn ein offener Broker da ist:

```sh
sudo oaap tenant policy <mandant> --first-login eingang
```

Jede neue Person landet dann im **Eingang** der Benutzerverwaltung, mit
Identität und ohne Rechte. Die Verwaltung des Mandanten gibt Partnern
und Kunden ihre Rolle von Hand.

Soll jede erste Anmeldung trotzdem gleich eine Rolle bekommen, z. B.
`guest`, verlangt OAAP eine Begründung. Die Begründung steht danach im
Mandantenlog:

```sh
sudo oaap tenant policy <mandant> --first-login role --default-role guest \
  --reason "Kunden lesen nur die freigegebenen Projektseiten"
```

**Prüfen:** `sudo oaap tenant log <mandant>` zeigt `tenant.idp-policy`
mit der Begründung.

### Schritt 6: Ein fremdes Keycloak oder SAML als geschlossen quittieren

Bei einem fremden OIDC- oder SAML-Dienst kann OAAP aus der Einstellung
nicht ablesen, wen er hereinlässt. Er gilt deshalb als offen. Wenn Sie
wissen, dass er nur die Leute eines Partners kennt, sagen Sie das mit
Begründung:

```sh
sudo oaap tenant policy <mandant> \
  --broker-closed "partner-kc=Keycloak des Partners, nur dessen Projektteam"
```

Zurücknehmen: `--broker-open partner-kc`. Ist der Broker dann wieder
offen und vergibt die Richtlinie eine Rolle, braucht auch das
Zurücknehmen eine Begründung.

**Prüfen:** In `oaap tenant policy <mandant>` steht der Broker als
`closed` mit Ihrer Begründung.

## 3. Was heute noch nicht geht

- **Eine Plattformrolle je Gruppe oder je Broker.** Heute bekommt jede
  erste Anmeldung dieselbe Rolle, egal über welchen Broker sie kam.
  Fachliche Rechte je Realm-Gruppe gehen schon heute (siehe
  [Fachliche Rollen einrichten](fachliche-rollen-einrichten.md)). Die
  Plattformrolle je Gruppe (nur `guest`, `partner`, `user`) bringt
  RFC-0091 Stufe 2.
- **Forgejo mit Anmeldung über den Realm.** Das Forgejo-Paket hat heute
  eigene Konten. Die Anmeldung über den Anmeldedienst des Mandanten,
  auch für Git über HTTPS, bringt RFC-0091 Stufe 3.
- **Ein Konto über mehrere Mandanten.** Das ist ein eigenes Thema
  (RFC-0047).

## 4. Wenn es schiefgeht

### „brokers not read -- unknown, not none“

OAAP durfte die Broker nicht lesen. Das passiert bei einem Realm, den
nicht der Konnektor dieses Servers angelegt hat (zum Beispiel einem
übernommenen). Gemessen: Im eigenen Realm antwortet Keycloak mit 200,
im fremden mit 403. Abhilfe: dem Dienstkonto des Konnektors in diesem
Realm die Rolle `view-identity-providers` geben. Bis dahin sagt OAAP
„unbekannt“, nie „keiner“.

### Die Richtlinie wird abgelehnt: „the broker '…' admits any … account“

Ein offener Broker und eine Rolle bei der ersten Anmeldung, ohne
Begründung. Drei Wege: den Broker schließen (Domäne oder Verzeichnis
eintragen), ihn als geschlossen quittieren (Schritt 6), oder mit
`--reason` begründen, warum er offen bleiben darf.

### „DIFFERENT: the broker '…' admits …“ in `oaap tenant policy`

Der Broker kam **nach** der Richtlinie dazu. Die Richtlinie wurde
nie gegen ihn geprüft. Gleiche drei Wege wie oben.

### Warnung „trusts the e-mail address it is handed“

Am Broker ist *Trust email* an. Wer beim fremden Dienst ein Konto mit
der Adresse einer Ihrer Personen hat, gilt damit als bestätigt. In der
Keycloak-Konsole am Broker ausschalten.

### Warnung „uses its own first-login flow“

Der Broker oder der Realm benutzt einen eigenen Ablauf für die erste
Anmeldung über einen Broker. Prüfen Sie in der Konsole, dass dieser
Ablauf eine vorhandene Person nie allein über die E-Mail-Adresse
verknüpft, ohne dass sie sich anmeldet. Sonst kann ein fremdes Konto
eine bestehende Person übernehmen.

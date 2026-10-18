# Fachliche Rollen einrichten — aus den Vorlagen einer App

> Geprüft gegen Referenz **0.1.203 + Setup** (oaap-test, 2026-10-18), mit einem
> echten Keycloak 26.7.4 und einem Übungspaket, das die sechs Rollenvorlagen des
> Handball-Vereins trägt. **Nicht gemessen:** die Anmeldung einer Person mit
> Gruppe im Browser (oaap-test hat keinen Außennamen) und der Aufruf der App-Seite
> „Rollen & Rechte“ mit diesen Rollen. Spezifikation: `oaap.core.authorization`
> 0.4 §2.11. Platzhalter: `<mandant>`, `<app>`.

**Grundgedanke:** Eine App *erklärt* im Manifest, welche fachlichen Rollen es gibt
(„Vorlagen“, z. B. *Trainer/in*, *Hallensprecher/in*). Ein Mandant macht daraus
**Rollen** und bündelt sie in **Berechtigungspaketen**. Personen bekommen ein
Paket zugeordnet — von Hand oder, damit niemand daran denken muss, über eine
**Gruppe im Anmeldedienst**: Wer in der Gruppe `Verein/Trainer` ist, bekommt bei
jeder Anmeldung das Paket *Trainer/in*. Das Einrichten dieser Kette ist je Vorlage
dreimal Handarbeit plus eine Gruppe im Anmeldedienst. Dafür gibt es **einen Befehl**.

## 1. Voraussetzungen

- Die App ist im Mandanten **installiert** (ihre Erklärung ist damit bekannt).
  `sudo oaap authz declarations --tenant <mandant>` zeigt die Vorlagen.
- Für die Gruppen im Anmeldedienst: der Mandant meldet sich über einen Realm an,
  der von einem **Konnektor dieses Knotens** angelegt wurde
  (`oaap idp provision …`). Ohne das werden Rollen, Pakete und Abbildungen
  trotzdem eingerichtet, und die Gruppen muss jemand im Anmeldedienst anlegen.

## 2. Erst ansehen: der Probelauf

```sh
sudo oaap authz setup --tenant <mandant> --app <app> --dry-run
```

Der Probelauf **ändert nichts** und nennt je Vorlage, was geschähe:

| Zeile sagt | heißt |
|---|---|
| `[ready]` | wird eingerichtet; dahinter, welche Gruppe und woher der Pfad stammt (`manifest` = Vorschlag der App, `tenant` = von dir genannt) |
| `[present]` | ist schon da, wird nicht angefasst |
| `[skipped]` | braucht eine Entscheidung von dir (Vorlage mit Werten, `$value`) oder ist abgewählt |
| `[conflict]` | der Name ist von etwas anderem belegt; **nur diese Vorlage** wird übergangen |

Vorlagen mit **Kontext** (z. B. „von welcher Mannschaft“) bekommen Rolle und
Paket, aber **keine Gruppe**: eine Gruppe sagt „ist Trainer“, nicht „von
Mannschaft mB“. Die Zuordnung je Mannschaft machst du von Hand.

## 3. Einrichten

```sh
sudo oaap authz setup --tenant <mandant> --app <app> --accept-version 26.7.4
```

Je Vorlage entstehen: die **Rolle**, ein **Berechtigungspaket** mit dieser Rolle,
die **Abbildung** Gruppe → Paket und die **Gruppe im Anmeldedienst** (nur wenn sie
fehlt). Die Reihenfolge ist Absicht: **zuerst die Gruppen im Anmeldedienst.**
Scheitert das, ist in OAAP **nichts** geschrieben.

Wichtige Schalter:

- `--only trainer,editor` / `--skip sponsor` — Vorlagen wählen.
- `--group-for trainer=Verein/Trainer` — den Gruppenpfad selbst nennen. Das geht vor
  dem Vorschlag der App und gibt auch Vorlagen ohne Vorschlag einen Pfad.
- `--name-for sponsor="Sponsor (Verein)"` — den Namen der Rolle und des Pakets selbst
  wählen, statt des Titels aus der Vorlage (der Ausweg bei einem belegten Namen, siehe
  Abschnitt 5).
- `--no-groups` — keine Gruppen im Anmeldedienst anlegen; die Abbildungen werden
  trotzdem geschrieben (dann muss die Gruppe existieren, bevor sie etwas gibt).
- `--accept-version` — nötig, solange der Konnektor die Fassung des
  Anmeldedienstes nicht selbst lesen kann (sein Dienstkonto ist zu schmal dafür).

Der Lauf ist **wiederholbar**: Ein zweiter Aufruf sagt `Nothing to do.`, ruft den
Anmeldedienst nicht und schreibt nichts. Scheitert eine Zeile, laufen die anderen
weiter; der Lauf endet mit Fehler, und ein Wiederholen macht nur den Rest.

## 4. Was der Befehl nie tut

- Er läuft **nie von selbst** — nicht bei der Installation einer App, nicht beim
  Aktualisieren.
- Er legt **keine Person** an und steckt **niemanden in eine Gruppe**. Die Gruppen
  entstehen leer; wer hineinkommt, bestimmt der Verein im Anmeldedienst.
- Er vergibt **nie eine Plattformrolle** (`tenant_admin` & Co. sind über Gruppen
  nicht erreichbar).
- Er **löscht und ändert nichts**, was schon da ist — auch keine Gruppe, ihre
  Mitglieder oder ihre Rollen im Anmeldedienst.
- Er benutzt den Konnektor nur, wenn dessen Adresse zum **Aussteller** des Mandanten
  passt (sonst steht dort „somewhere else“, und die Gruppen bleiben aus).

## 5. Häufige Stolperer

- **`[conflict]` bei einem Namen wie „Sponsor“:** Ein Rollenname gilt im Mandanten
  nur einmal, auch über Apps hinweg, und ausgeblendete Namen bleiben vergeben.
  Der Ausweg: `--name-for <schlüssel>="anderer Name"`. Rolle **und** Paket tragen dann
  diesen Namen. Eine Rolle, die es schon gibt, wird dadurch nicht umbenannt; der Plan
  sagt dann „--name-for not used“.
- **Die App hat gar keinen Vorschlag:** Der Probelauf zeigt „no group path known“ mit
  dem passenden `--group-for`.
- **Pfad im Anmeldedienst umbenannt:** Die Abbildung gilt nach Pfad. Wer eine Gruppe
  umbenennt, muss die Abbildung neu anlegen (`oaap authz map-remove`, danach
  `setup` mit dem neuen Pfad).
- **Wirkt erst beim nächsten Login:** Gruppen werden bei jeder Anmeldung gelesen.

## 6. Im Aufbau-Profil

```json
{"id": "rollen", "type": "authz.setup", "app": "hib"}
```

Mit den Argumenten `only`, `skip` (Komma-getrennte Schlüssel), `groups`
(`schluessel=Pfad,schluessel=Pfad`) und `names` (`schluessel=Name,schluessel=Name`; ein
Name enthält kein Komma). Der Schritt gilt als erledigt, wenn der Plan
nichts mehr zu tun findet — nicht schon, weil der Befehl ohne Fehler zurückkam.
Ein belegter Name hält den Aufbau an (`conflict`), statt ihn zu überspringen. Er
steht **nach** dem Schritt, der die App installiert.

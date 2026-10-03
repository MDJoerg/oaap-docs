# FAQ: Dedizierter Mehrmandanten-Knoten

> Geprüft gegen Referenz **0.1.144** (2026-09-30). Beispiele verwenden
> Platzhalter: `<knoten-name>` (z. B. `knoten01`), `<basisdomain>` (z. B.
> `hsp.beispiel.de`), `<mandant>` (Kürzel eines Mandanten).
> Format je Eintrag: **Frage · Kurzantwort · Schritte · Weiterführend.**
> Stichwörter stehen unter der Frage, damit Suche und KI-Abruf treffen.

## Aufbau und Größenordnung

### F1 – Wie ist ein Knoten aufgebaut, der nur Mandanten (Kunden, Vereine) trägt?
*Stichwörter: Mandant, default, Management, Shared, Rollenaufteilung*

**Kurzantwort:** Der `default`-Mandant bleibt Betreibern vorbehalten
(zentrale Dienste wie der Anmeldedienst). Verwaltungswerkzeuge liegen in
einem eigenen Management-Mandanten, gemeinsam genutzte Dienste mit
eigenem Login (z. B. eine Git-Plattform) in einem Shared-Mandanten. Jeder
Anwender-Mandant bekommt einen eigenen Anmelde-Bereich (Realm) im
zentralen Keycloak.

| Mandant | Zweck | Wer arbeitet dort |
|---|---|---|
| `default` | zentrale Dienste (Anmeldedienst, Portal) | server_admin |
| `<mgmt>` | Verwaltungswerkzeuge des Betreibers | server_admin |
| `<shared>` | Dienste für alle, eigener Login | Nutzer aller Mandanten |
| `<mandant>` | die Anwendungen eines Kunden | tenant_admin + Mitglieder des Kunden |

**Weiterführend:** RFC-0022 (Mandant als Grenze), RFC-0041 (externe
Identitätsanbieter), RFC-0042 (Mandant als Ort).

### F2 – Reichen 4 CPU-Kerne, 8 GB RAM und 240 GB Platte für den Anfang?
*Stichwörter: Dimensionierung, Speicher, Keycloak*

**Kurzantwort:** Für Kernplattform, Keycloak (mit eigener Datenbank),
eine Git-Plattform und einige wenige Mandanten mit je drei leichten
Instanzen ja; RAM ist die erste knappe Größe. Keycloak allein braucht
etwa 1 GB. Vor dem Aufnehmen jedes weiteren Mandanten `free -g` und
`oaap status` ansehen und pro Mandant die Ressourcenbegrenzung setzen
(`oaap resources`).

**Weiterführend:** CLI-Referenz → `oaap resources`.

## Namen und DNS

### F3 – Welche DNS-Einträge braucht ein Knoten, der Mandanten unter eigenen Unteradressen führt?
*Stichwörter: DNS, Wildcard, Mandantenadresse, Zertifikat*

**Kurzantwort:** Zwei Einträge auf die öffentliche Adresse: der Knotenname
selbst und ein Wildcard darunter. Ein Wildcard deckt den nackten Namen
nicht ab. Mandanten antworten dann unter `<mandant>.<basisdomain>`,
Instanzen unter `<instanz>.<mandant>.<basisdomain>`.

```
<basisdomain>      A   <öffentliche IPv4>
*.<basisdomain>    A   <öffentliche IPv4>
```

**Prüfen:** `getent hosts <basisdomain>` und `getent hosts test.<basisdomain>`
müssen dieselbe Adresse liefern.

**Weiterführend:** CLI-Referenz → `oaap external`; RFC-0042 §T1; RFC-0018.

### F4 – Können Kunden später eigene Domains mitbringen?
*Stichwörter: Eigene Domain, Alias, Instanz-Namen*

**Kurzantwort:** Ja, über mehrere Namen je Instanz (Hauptname plus
Aliasse, RFC-0018). Der Kunde zeigt seine Domain per DNS auf den Knoten,
der Betreiber trägt sie als Alias ein. Beim Neu-Ausrollen einer Instanz
bleiben Aliasse erhalten (seit 0.1.127).
*Offen:* Eine Domain für den ganzen Mandanten (nicht je Instanz) ist eine
Anforderung, siehe Ideenspeicher (I-1).

## Eigenes Hosting-Angebot

### F5 – Können Kunden ihre Webseite (auch von einer KI erzeugt) als Testinstanz veröffentlichen und danach im selben Mandanten produktiv setzen?
*Stichwörter: Deployment, Test, Produktiv, KI, ZIP, Promote*

**Kurzantwort:** Die Bausteine gibt es: Paket-Deployment aus einem
ZIP statt Git (RFC-0019), zeitlich begrenzte Anlege-Erlaubnis für einen
Aufrufer, der nicht Betreiber ist, und die Produktivsetzung derselben
geprüften Bytes (RFC-0020). Ob der Ablauf für Kunden ohne
Betreiberprofil `dev` rund läuft, ist offen (Ideenspeicher I-2).

**Weiterführend:** RFC-0019, RFC-0020, RFC-0027 (API-Schlüssel), RFC-0037.

## Sicherung

### F6 – Was sichern wir auf einem Mandantenknoten, und wer sichert was?
*Stichwörter: Backup, Mandantenarchiv, VM-Snapshot*

**Kurzantwort:** Drei Schichten: (1) Plattform-Einstellungen und
Knotenzustand, (2) je Mandant ein eigenes Archiv, das auch einzeln
zurückgespielt oder auf einen anderen Knoten umgezogen werden kann,
(3) das Abbild der ganzen virtuellen Maschine durch den Rechenzentrums-
Betreiber. Schicht 3 ersetzt 1 und 2 nicht: ein VM-Abbild sichert den
Zustand mitten im Betrieb und kann Datenbanken inkonsistent erfassen.
Archive enthalten Geheimnisse (z. B. Realm-Exporte) und gehören verschlüsselt
oder mindestens 0600 abgelegt.

**Weiterführend:** CLI-Referenz → `oaap backup`; RFC-0029.

## Stolpersteine bei der Einrichtung

### F7 – Nach dem Setzen des Hostnamens meldet sudo „Hostname … kann nicht aufgelöst werden". Was tun?
*Stichwörter: hostnamectl, sudo, /etc/hosts, 127.0.1.1*

**Kurzantwort:** `hostnamectl set-hostname` ändert nur den Namen, nicht
die Namensauflösung. Der Rechner findet seinen neuen Namen nicht. Harmlos,
aber jede sudo-Zeile meldet es. Abhilfe: den Namen auf die lokale Adresse
zeigen lassen.

```bash
echo "127.0.1.1 <knoten-name>" | sudo tee -a /etc/hosts
getent hosts <knoten-name>      # muss 127.0.1.1 zeigen
```

Steht in `/etc/hosts` schon eine Zeile `127.0.1.1 <alter-name>`, ersetzt
man den alten Namen dort, statt eine zweite Zeile anzuhängen.

### F8 – Mein DNS-Anbieter lehnt den Wildcard-Eintrag `*.<basisdomain>` ab. Was nun?
*Stichwörter: Wildcard, Strato, Subdomain-Formular, DNS-Anbieter, Let's Encrypt*

**Kurzantwort:** Zuerst prüfen, ob der Anbieter Wildcards nur an anderer
Stelle zulässt: nicht im Formular „Subdomain anlegen", sondern in der
DNS-Verwaltung der (Sub-)Domain als A-Record mit dem Präfix `*`. Geht
auch das nicht, gibt es drei Wege:

1. **Einzelne A-Records** für jeden Namen, den der Knoten führt
   (`<mandant>`, `<instanz>.<mandant>`). Funktioniert sofort, wächst aber
   mit jedem Mandanten und jeder Instanz von Hand.
2. **Zone auslagern:** Die Subdomain per NS-Records an einen DNS-Dienst
   mit Wildcard und API delegieren, sofern der Anbieter NS-Records für
   Subdomains erlaubt.
3. **Die Basisdomain zu einem anderen Anbieter umziehen.**

Zertifikate stellt der Knoten je Name per HTTP-Prüfung aus; ein
Wildcard-Zertifikat ist dafür nicht nötig, nur dass der Name auflöst.
Beachten: Let's Encrypt begrenzt neue Zertifikate je registrierter
Domain (50 pro Woche); bei vielen Mandanten in kurzer Zeit relevant.

**Weiterführend:** F3, Ideenspeicher I-4.

**Ergänzung zu F8 – Erfahrung mit einer Endkunden-Oberfläche (Strato):**
Die Oberfläche bietet je Domain getrennte Seiten für NS, A, AAAA, MX,
TXT/CNAME, SRV und Dynamic DNS. Die A-Seite ändert nur die Adresse der
Hauptdomain; Subdomains legt man über das Subdomain-Formular an, das
keinen Wildcard annimmt. Zwei Wege, die man dort zuerst probiert, bevor
man die Zone auslagert:

1. **Wildcard als CNAME** auf der TXT/CNAME-Seite: Präfix `*.<knoten>`,
   Ziel der Knotenname mit abschließendem Punkt. Ein CNAME-Wildcard löst
   alle Namen auf, die keinen eigenen Eintrag haben, und genügt für
   Zertifikate per HTTP-Prüfung.
2. **Delegation:** Auf der NS-Seite prüfen, ob sich für die Subdomain
   fremde Nameserver eintragen lassen. Dann übernimmt ein DNS-Dienst mit
   Wildcard und API die Zone `<knoten>.<domain>`; die Hauptdomain bleibt
   beim Anbieter.

Eine Aussage über die Oberfläche eines Anbieters gilt nur zum Prüfzeitpunkt.

### F9 – Wie delegiere ich die Zone eines Knotens an einen DNS-Dienst mit Wildcard und API?
*Stichwörter: NS-Delegation, eigener Nameserver, Wildcard, DNS-API, deSEC*

**Kurzantwort:** Beim Anbieter der Hauptdomain lässt sich für die
Subdomain des Knotens meist „Eigener Nameserver" wählen. Die Zone wird
dann bei einem DNS-Dienst geführt, der Wildcards und eine API kann. Die
Reihenfolge ist wichtig: **erst die Zone dort vollständig anlegen und
prüfen, dann umschalten.** Sonst ist der Knoten zwischendurch nicht
erreichbar.

1. Zone `<knoten>.<domain>` beim DNS-Dienst anlegen.
2. Zwei Einträge genügen: `A` für die Zone selbst und `A` für `*`
   (jeweils die öffentliche Adresse). Der Wildcard trägt alle Mandanten
   und Instanzen, auch mehrstufige (`<instanz>.<mandant>.<knoten>…`).
   **Keine** zusätzlichen Einzeleinträge für Mandantennamen anlegen: ein
   vorhandener Name verdeckt den Wildcard für alles unterhalb von ihm.
3. Vor dem Umschalten direkt gegen den neuen Nameserver prüfen:
   ```bash
   dig +short @<nameserver> <knoten>.<domain> A
   dig +short @<nameserver> a.b.<knoten>.<domain> A
   ```
   Beide müssen die öffentliche Adresse liefern.
4. Beim Anbieter der Hauptdomain unter NS-Record der Subdomain
   „Eigener Nameserver" wählen, die Nameserver eintragen, speichern.
   Übernahme dauert Minuten bis Stunden; danach gelten die alten
   Einträge dieser Subdomain beim Anbieter nicht mehr.
5. API-Token anlegen und **wie ein Passwort behandeln** (nicht in Doku,
   Repository oder Chat). Die Onboarding-Automatisierung braucht ihn
   später, um Einträge zu ändern.

**Weiterführend:** F3, F8, Ideenspeicher I-4.

**Häufiger Fehler zu F9:** Nur den Wildcard `*` anzulegen. Er deckt den
Namen der Zone selbst nicht ab; `dig` liefert dann für `<knoten>.<domain>`
nichts, für alle Namen darunter aber die Adresse. Beim DNS-Dienst muss
der Eintrag für die Zone mit **leerem** Subnamen angelegt werden.

### F10 – `oaap tenant list` meldet nach frischer Installation „this node has no tenant store yet – run `oaap update`". Was tun?
*Stichwörter: Mandantenverzeichnis, tenant store, Erstinstallation, oaap update*

**Kurzantwort:** Auf einem frisch installierten Knoten fehlt die
Mandantendatei, bis einmal `sudo oaap update` gelaufen ist (Fassung 0.1.146
beobachtet). Danach zeigt `oaap tenant list` den Mandanten `default`.
Bequemer Ablauf: nach der Installation und dem ersten Administrator
einmal `sudo oaap update` ausführen, dann erst Mandanten anlegen.

## Mandanten anlegen

### F11 – Wie lege ich einen Mandanten an, und was muss ich über sein Kürzel wissen?
*Stichwörter: oaap tenant create, Kürzel, label, Certificate Transparency, Klarname*

**Kurzantwort:**

```bash
sudo oaap tenant create <kürzel> --name "<Klarname des Kunden>"
sudo oaap tenant list
```

Das **Kürzel ist öffentlich**: Es steht in den Adressen aller Instanzen
(`<instanz>.<kürzel>.<knoten>`) und damit in den Zertifikatsprotokollen
(Certificate Transparency), die jeder lesen kann. Der Klarname (`--name`)
bleibt im Haus. Ist ein Kunde vertraulich, ein Kürzel wählen, das nichts
über ihn sagt; umbenennen geht später (`oaap tenant rename`), das alte
Kürzel antwortet noch eine Übergangszeit.

Das Anlegen prüft, ob `probe.<kürzel>.<knoten>` auflöst, und warnt, wenn
nicht. Löst das Kürzel bei Wildcard-DNS auf (siehe F9), kommt keine Warnung.
Ab dem zweiten Mandanten werden Mandanten sichtbar: Benutzer sehen im
Portal nur ihren eigenen. Einen Mandanten zu löschen gibt es bewusst
nicht (erst exportieren, dann gesondert entfernen).

**Danach:** ersten Administrator (`tenant_admin`) für den Mandanten
anlegen, ab dort verwaltet sich der Mandant selbst.

**Weiterführend:** RFC-0022, RFC-0026, RFC-0042.

### F12 – Der neue Mandant antwortet mit `SSL_ERROR_INTERNAL_ERROR_ALERT`. Warum?
*Stichwörter: Mandantenadresse, TLS-Fehler, Zertifikat, Gateway, tenant create*

**Kurzantwort:** In Fassung 0.1.146 legt `oaap tenant create` die
Gateway-Site des Mandanten nicht an; das Zertifikat wird deshalb nie
angefordert, und der Browser bekommt beim TLS-Aufbau einen Fehler. Der
Knoten selbst und seine Instanzen sind nicht betroffen. Behelf: die Sites
neu erzeugen lassen.

```bash
sudo oaap external set <knoten-name-mit-domain>
```

Danach beim ersten Aufruf des Mandantenortes ein paar Sekunden warten
(Zertifikat wird ausgestellt). Ein Aufruf per `curl -sI https://<kürzel>.<knoten>/`
zeigt `200`, `302` oder `303`. Bleibt der Fehler, in die Protokolle des
Gateways sehen (`sudo oaap logs gateway`) und prüfen, ob `<kürzel>.<knoten>`
im DNS auflöst.

## Benutzer und Delegation

### F13 – Wie kommt ein Benutzer aus dem Realm in den Mandanten, und wie heißt er dort?
*Stichwörter: erste Anmeldung, Eingang, Benutzername, Kollision, preferred_username*

**Kurzantwort:** Wer sich zum ersten Mal über den Realm eines Mandanten
anmeldet, bekommt beim Knoten einen Benutzersatz ohne Rechte („Eingang"),
gebunden an (Anbieter, Kennung). Der Name kommt als Vorschlag aus dem
Realm (`preferred_username`, sonst E-Mail-Teil). Ist er auf dem **ganzen
Knoten** schon vergeben, hängt OAAP eine Zahl an (`-2`). Der Name ist ein
Name; der Anker ist die Kennung des Satzes, deshalb sind Umbenennungen
unkritisch. Eine Anmeldung wird nie über Name oder E-Mail einem
bestehenden Benutzer zugeordnet. Bekannte Schwäche: Namen kollidieren über
Mandanten hinweg, siehe Ideenspeicher I-9.

Rechte vergibt anschließend ein `server_admin`, im eigenen Mandanten auch
ein `tenant_admin` (Portal → Benutzer). Knotenweite Rollen (`server_admin`,
`support`) kann ein `tenant_admin` nie vergeben.

### F14 – Kunden verwalten ihre Mitglieder selbst. Muss der Betreiber jeden neuen Benutzer freigeben?
*Stichwörter: Delegation, tenant_admin, first-login, Richtlinie, Selbstregistrierung*

**Kurzantwort:** Nein, wenn der Mandant so eingerichtet ist.

1. Jeder `tenant_admin` verwaltet Benutzer und Rollen **seines** Mandanten
   selbst. Nur der **erste** `tenant_admin` braucht den Betreiber, denn
   diese Rolle wird nie automatisch vergeben.
2. Mit der Richtlinie `role` (Vorgabe-Rolle z. B. `user`) bekommen neue
   Mitglieder die Rolle bei der ersten Anmeldung, ohne Freigabe. Das setzt
   nur der Betreiber, und OAAP lehnt es ab, solange im Realm die
   Selbstregistrierung offen ist: sonst könnte sich jeder Fremde
   Mitglied machen. Menschen legt dann der Kunde im **Realm** an, nicht
   OAAP.
3. Offen: Zugang des Kunden zur Verwaltung nur seines Realms, siehe I-10.

## Sicherung einrichten

### F15 – Wie richte ich auf einem neuen Mandantenknoten die Sicherung ein?
*Stichwörter: backup, Zeitplan, Timer, systemd, Generationen, Mandantenarchiv, Ausnehmen, Abholung*

**Kurzantwort:** In vier Schichten, in dieser Reihenfolge:

1. **Nächtlicher Knotenzeitplan** (lokal, wenige Generationen):
   ```bash
   cd ~/oaap-reference && sudo bash ops/install-backup-timer.sh --at 03:30 --keep 2
   sudo oaap backup schedule            # zeigt Zeit, Ziel, nächsten Lauf
   ```
   Ein Zeitplan-Timer (systemd) ist das Gegenstück zu einem Hintergrundjob:
   er nennt, *was* läuft und *wann*; `systemctl list-timers` zeigt Plan und
   letzten Lauf. Während des Kopierens (nicht des Komprimierens) sind die App-
   Container kurz angehalten, für Anwender sind das Sekunden bis Minuten.
   Standardziel ist `/var/backups/oaap` auf derselben Platte: das schützt
   vor Bedienfehlern, **nicht vor Verlust der Maschine** (Schicht 3).
2. **Erste Probe von Hand**, bevor man dem Zeitplan traut:
   ```bash
   sudo oaap backup create
   sudo ls -lh /var/backups/oaap
   sudo oaap backup status
   ```
3. **Kopie außerhalb der Maschine.** Entweder holt ein anderer Knoten das
   Archiv ab (Abholung, `ops/install-backup-pull.sh` auf dem *holenden*
   Knoten, Quelle bleibt unwissend) oder der Betreiber des Rechenzentrums
   sichert die ganze VM. Beides ergänzt sich; ein VM-Abbild ersetzt das
   OAAP-Archiv nicht (Datenbanken mitten im Betrieb).
4. **Mandantenarchive einzeln:** `sudo oaap backup create --tenant <kürzel> --to <verzeichnis>`.
   Ein Mandantenarchiv lässt sich allein zurückspielen und auf einen
   anderen, leeren Knoten umziehen (`oaap tenant adopt`). Kunden-Mandanten
   lassen sich vom Knotenarchiv **ausnehmen**, mit Begründung, die in *ihr*
   Protokoll geschrieben wird: `sudo oaap backup exclude <kürzel> --reason "…"`.

**Prüfen, ob das Ganze etwas taugt:** Eine Sicherung, die nie
zurückgespielt wurde, ist eine Annahme. Einmal auf einem Wegwerf-Knoten
einspielen. Archive enthalten Geheimnisse; Ziel exklusiv berechtigen (0700).

**Was nicht im Archiv steckt:** Geheimnisse, die Sie von Hand auf dem
Knoten abgelegt haben (Dateien unter `/root`, z. B. das erste
Verwalterpasswort des Anmeldedienstes) gehören in den Passwortmanager.

**Weiterführend:** RFC-0029, CLI-Referenz → `oaap backup`.

**Nachtrag zu F15 – Realm-Daten und Mandantenarchive:** Der Anmeldedienst
gehört zum Knoten (Standard-Mandant). Die Realms *aller* Mandanten liegen
in seiner Datenbank und damit nur im **Knotenarchiv**. Ein Mandantenarchiv
trägt den Anbieter-Eintrag, aber weder Realm noch Client-Geheimnis. Wer
Mandanten einzeln sichern oder umziehen will, sichert den Realm zusätzlich
(`sudo oaap idp export <konnektor> --tenant <kürzel> --out <datei>`, Datei
ist ein Geheimnis: 0600, nach Gebrauch löschen). Erste Probe auf einem
frischen Knoten: Knotenarchiv 6 MB, Mandantenarchiv eines leeren Mandanten
1,5 KB, Anhaltezeit der Apps 2 s.

**Rolle `support` ist kein Sicherungsrecht:** Sie zeigt die
Gesundheitsseite, die die Instanzen **aller** Mandanten auflistet (Namen
der Kunden sind dort sichtbar), und sonst nichts. Das Abholen von Archiven
läuft über einen eigenen, eingeschränkten SSH-Schlüssel, nicht über eine
Rolle.

### F16 – `oaap app config/address/restart` meldet „no instance named …" für eine Instanz in einem Kunden-Mandanten. Warum?
*Stichwörter: Instanzschlüssel, Mandantenkürzel, app list, no instance named*

**Seit 0.1.167** nimmt die CLI auch `<kürzel>/<name>`, `<name> --tenant <kürzel>`
und den Portalnamen, wenn ihn nur eine Instanz trägt
(`sudo oaap app restart shared/forgejo`). Die folgende Antwort gilt für ältere
Knoten und erklärt, woher der Schlüssel kommt.

**Kurzantwort:** Die CLI kennt Instanzen unter ihrem **knotenweiten
Schlüssel**: `<mandantenkürzel>-<name>`. Nur im Standard-Mandanten ist der
Schlüssel gleich dem Namen. Die Instanz `forgejo` im Mandanten `shared`
heißt für die CLI `shared-forgejo`. Den Schlüssel zeigt `sudo oaap app list`.

```bash
sudo oaap app config set <kürzel>-<instanz> <schlüssel> <wert>
sudo oaap app restart <kürzel>-<instanz>
```

Die **Adresse** dagegen folgt dem Muster `<instanz>.<kürzel>.<knoten>`,
ohne den Präfix im Instanznamen. Container und Datenverzeichnisse tragen
ebenfalls den Schlüssel.

## Gemeinsame Dienste (Beispiel Git-Plattform)

### F17 – Wie trenne ich Kunden in einer gemeinsamen Git-Plattform (Forgejo) im Shared-Mandanten?
*Stichwörter: Forgejo, Organisation, eingeschränkter Benutzer, Sichtbarkeit, Explore, DEFAULT_USER_IS_RESTRICTED*

**Kurzantwort:** Je Kunde eine **Organisation** mit dem Mandantenkürzel als
Namen. Konten der Kunden sind **eingeschränkt** (restricted): Sie sehen nur
Organisationen, Teams und Projekte, in die sie aufgenommen wurden. Vorgaben
über die Konfiguration der Instanz (Umgebungsvariablen, wirken nach
Neustart):

```bash
sudo oaap app config set <kürzel>-forgejo FORGEJO__service__DEFAULT_USER_IS_RESTRICTED true
sudo oaap app config set <kürzel>-forgejo FORGEJO__service__DEFAULT_ORG_VISIBILITY private
sudo oaap app config set <kürzel>-forgejo FORGEJO__service__DEFAULT_USER_VISIBILITY private
sudo oaap app restart <kürzel>-forgejo
```

Bereits mitgelieferte Vorgaben der App: keine Selbstregistrierung,
Anmeldung schon zum Lesen (`REQUIRE_SIGNIN_VIEW`). Die Route ist `public`,
weil `git clone` den Portal-Login nicht durchlaufen kann; Forgejo prüft jede
Anfrage selbst.

**Grenze:** Konten anlegen kann in Forgejo nur der Website-Administrator
(oder es gibt offene Registrierung). Ein Organisations-Administrator kann
vorhandene Konten in Teams aufnehmen, aber keine neuen Konten schaffen.
Delegierte Kontenanlage geht deshalb nur über den Betreiber, eine
Automatisierung mit Administrator-Token oder später über „ein Konto überall"
(RFC-0047). Ideenspeicher I-13.

**Immer testen:** Nach der Konfiguration mit einem zweiten, eingeschränkten
Testkonto prüfen, dass es fremde Organisationen und Benutzer weder in
„Erkunden" noch per Direktlink sieht.

### F18 – Was kann ein Realm-Verwalter des Kunden in Keycloak tun und was nicht?
*Stichwörter: manage-users, view-users, Realm-Konsole, Löschen, Rollen*

**Kurzantwort:** Ein Benutzer mit den Realm-Rollen `manage-users` und
`view-users` erreicht `https://<auth>.<knoten>/admin/<kürzel>/console/`,
sieht nur *Users* und *Groups* seines Realms, kann Benutzer anlegen,
Passwörter setzen und Benutzer **löschen**. Clients, Rollen, Einstellungen
und Identitätsanbieter erreicht er nicht; das Vergeben von Admin-Rollen
scheitert (gemessen für ein Dienstkonto mit denselben Rechten, 403).
**Vorsicht beim Löschen:** OAAP erfährt davon nichts. Der Benutzersatz im
Mandanten bleibt aktiv, hat aber keinen Anmeldeweg mehr; wird die Person
neu angelegt, kommt sie als neuer Benutzer an (neue Kennung).

### F19 – Warum sieht ein Mitglied mit der Rolle `user` den Reiter „Zwilling"?
*Stichwörter: Zwilling, Portalreiter, Rolle user, Digitaler Zwilling*

**Kurzantwort:** Das ist so festgelegt: Lesen im Digitalen Zwilling
gehört zu den Rollen `user`, `keyuser`, `admin` und `tenant_admin`;
Schreiben nur `admin`, `keyuser` und `tenant_admin`; Typen anlegen nur
`tenant_admin`. Ob der Zwilling auf einem Knoten überhaupt verfügbar ist,
hängt vom Datenspeicher-Profil ab (ohne das Profil `store` zeigt die Seite
„nicht verfügbar"). Für Mandanten, die den Zwilling nicht brauchen, wäre
ein Ausblenden je Mandant sinnvoll (Ideenspeicher I-17).

### F20 – Nach `oaap app promote` heißt die Produktivinstanz `<mandant>-<mandant>-<name>`. Was ist passiert?
*Stichwörter: promote, --to, Instanzname, Schlüssel, Doppelpräfix, rename*

**Seit 0.1.167** bricht `promote --to <kürzel>-<name>` ab, nennt den Schlüssel, der
entstünde, und die richtige Schreibweise (`--keep-name` erlaubt es bewusst);
die Reparatur unten brauchen Sie nur noch für Altfälle.

**Kurzantwort:** `promote` mischt zwei Schreibweisen. Der **Teststand** (erstes
Argument) ist der knotenweite **Schlüssel** (`<mandant>-<name>-test`), `--to`
ist der **Name innerhalb des Mandanten** (`<name>`). Wird bei `--to` der
Schlüssel angegeben, setzt die Plattform den Mandantenpräfix ein zweites
Mal davor. Am einfachsten `--to` weglassen: ein Teststand mit Endung
`-test` leitet den Produktivnamen selbst ab.

```bash
sudo oaap app promote <mandant>-<name>-test              # → <mandant>-<name>
sudo oaap app promote <mandant>-<name>-test --to <name>  # gleichwertig
```

Reparatur bei falschem Namen (Daten bleiben, die Instanz startet neu):

```bash
sudo oaap app rename <falscher-schlüssel> <name> --grace-days 0        # zeigt nur an
sudo oaap app rename <falscher-schlüssel> <name> --grace-days 0 --yes
```

Konfiguration der Testinstanz wandert bei der Übernahme nicht in die
Produktivinstanz; sie muss dort gesetzt werden.

### F21 – Wie hängen Passwörter im Portal und im Anmeldedienst (Keycloak) zusammen?
*Stichwörter: Passwort, Keycloak, OIDC, Abmelden, Konto-Portal, lokales Konto*

**Kurzantwort:** Es gibt **keine Synchronisation**. Wer über den Anmeldedienst
(Anbieter) angemeldet wird, hat auf dem Knoten **nie ein eigenes Passwort**;
das Passwort liegt ausschließlich beim Anbieter. Die Plattform verknüpft das
Konto über (Anbieter, Kennung `sub`), nicht über den Namen.

- **Passwort ändern / vergessen:** beim Anbieter, im Konto-Portal des Realms
  (`<auth-adresse>/realms/<realm>/account`) oder durch den Mandantenverwalter
  in der Benutzerverwaltung des Realms. Die Passwortseite des Portals gilt nur
  für **lokale** Konten.
- **Lokale Anmeldung eines Anbieter-Kontos:** nicht möglich, solange niemand
  lokal ein Passwort gesetzt hat.
- **Profil (Name, E-Mail):** wird beim Anmelden aus den Angaben des Anbieters
  übernommen; Änderungen macht man beim Anbieter.
- **Abmelden:** meldet derzeit nur beim Portal ab. Die Sitzung beim Anbieter
  bleibt bestehen und meldet beim nächsten Anbieter-Login ohne Passwort wieder
  an. Zum vollständigen Abmelden zusätzlich im Konto-Portal des Anbieters
  abmelden (siehe Ideenspeicher I-20).

### F22 – Brauche ich für jede App eine Test-Instanz? Ich habe versehentlich eine angelegt.
*Stichwörter: Test-Kanal, Produktiv-Kanal, install, --channel, remove --purge, Test-Instanz*

**Kurzantwort:** Nein. Der Kanal `test` ist freiwillig. Neue Instanzen sind
standardmäßig **produktiv**; eine Test-Instanz lohnt sich nur, wenn eine neue
Version vor der Übernahme ausprobiert werden soll (`oaap app promote`, dieselben
Bytes gehen live). Für Anwendungen ohne Risiko (kleine Werkzeuge, noch keine
Daten) installiert man gleich produktiv:

```bash
sudo oaap app install <paket.zip> --name <name> --channel production --tenant <mandant>
```

Eine versehentlich angelegte, noch leere Test-Instanz entfernt man und
installiert neu (spart den Umweg über Umbenennen und Kanalwechsel):

```bash
sudo oaap app remove <mandant>-<name>-test --purge     # löscht die Instanz samt Daten
```

`--purge` löscht die Daten der Instanz unwiderruflich; nur bei leeren oder
entbehrlichen Instanzen verwenden. Spätere Aktualisierungen einer
Produktivinstanz sind Neuinstallationen derselben Instanz mit einer **höheren
Version** (dieselbe Version wird abgelehnt); Daten bleiben erhalten.

### F23 – Der Mandantenverwalter kann sich anmelden, aber eine App sagt „verweigert". Warum?
*Stichwörter: tenant_admin, admin, Rollen, Apps, Routen, 403*

**Kurzantwort:** `tenant_admin` (und `server_admin`) sind **Plattformrollen**:
Sie regeln Benutzer, Rollen und Instanzen eines Mandanten. Eine App fragt sie nie ab (RFC-0008).
Apps schützen ihre Bereiche mit **App-Rollen**: `admin`, `keyuser`, `user`,
`guest`, `partner`, `support` und `public` (kein Konto nötig). Wer eine App
verwalten soll, braucht dort die passende App-Rolle **zusätzlich**.

Vorgehen:

1. In der Manifestdatei der App (`routes:`) steht, welche Rolle einen Pfad
   freischaltet (z. B. `/admin` → `admin`).
2. Ein `tenant_admin` vergibt die Rolle im Portal unter Benutzer → Rollen.
3. Der Benutzer meldet sich **neu** an; Rollen gelten pro Sitzung.

Der Erstanmelder erhält über den Anbieter nur das, was die Richtlinie des
Mandanten vorgibt (`tenant_admin`, `server_admin` und `support` werden nie
automatisch vergeben).

### F24 – Kann die KI eines Kunden neue Versionen ausrollen, ohne dass der Knoten das Profil `dev` hat?
*Stichwörter: dev, Knotenprofil, Deploy-Token, Deploy-Hook, Anlege-Erlaubnis, Test-Instanz, Paket-Weg*

**Kurzantwort:** Ja. Das Profil `dev` erlaubt dem **Portal**, Instanzen aus
beliebigen Quellen anzulegen; auf einem Knoten mit Kundendaten ist das bewusst
aus. Die Aktualisierung einer **bestehenden Test-Instanz** braucht `dev` nicht:

| Vorgang | `dev` nötig? |
|---|---|
| Instanz im Portal anlegen (Test) und Anlege-Erlaubnis für die erste Instanz | ja |
| Erste Test-Instanz per Kommandozeile durch den Betreiber installieren | nein |
| Deploy-Token für eine bestehende Test-Instanz erzeugen | nein |
| Neue Version per Deploy-Hook einspielen (ankündigen, hochladen) | nein |
| Test-Instanz produktiv setzen (`promote`) | nein |

Ablauf ohne `dev`:

```bash
sudo oaap app install <paket.zip> --name <name>-test --channel test --tenant <mandant>
sudo oaap app token create <mandant>-<name>-test      # einmal angezeigt, dem Briefing getrennt beilegen
```

Danach liefert die KI über den Hook neue Stände (Briefing:
`oaap-docs/vorlagen/ki-briefing-test-deployment.md`). **Deploy-Tokens gibt es nur
für Test-Instanzen**; der Weg nach Produktion bleibt ein Mensch
(`oaap app promote`), und es geht genau das getestete Paket live. Was den
Rahmen erweitert (öffentliche Route, neuer Speicher, neuer Port), hält der
Knoten zurück, bis ein Administrator das Manifest bestätigt.

### F25 – Eine Test-Instanz im Portal produktiv setzen: Worauf ist zu achten?
*Stichwörter: promote, Übernehmen, Portal, Schlüssel, Update, Version, Prüfsumme*

**Kurzantwort:** Der Portalweg (Instanzseite der Test-Instanz → Übernehmen) setzt
den Namen der Produktivinstanz selbst: aus `<name>-test` wird `<name>`, der
Schlüssel lautet `<mandant>-<name>`. Die Doppelpräfix-Falle (F20) betrifft nur
die Kommandozeile mit `--to`. Es geht genau das getestete Paket live.

Prüfung danach:

```bash
sudo oaap app list | grep <mandant>-<name>
sudo oaap app artifact list <mandant>-<name>-test
sudo oaap app artifact list <mandant>-<name>
```

Erwartet: Test- und Produktivinstanz zeigen dieselbe Version und dieselbe
Prüfsumme im Dateinamen des laufenden Pakets (`<version>-<sha12>.zip <- running`).
Ein späteres Update ist dieselbe Übernahme mit einer **höheren Version**; das
alte Paket bleibt in der Liste der Produktivinstanz stehen. Ob Einstellungen
der Test-Instanz (z. B. Schalter, die nur dort gelten sollen) mit in die
Produktion gehen, ist nicht geprüft: nach der Übernahme
`sudo oaap app config list <mandant>-<name>` ansehen (F26).

### F26 – Was ist bei einer öffentlich erreichbaren Anwendung vor dem Livegang zu prüfen?
*Stichwörter: public, öffentliche Route, Suchmaschine, noindex, Titel, Test, Anzeigename, Livegang*

**Kurzantwort:** Eine Route mit der Rolle `public` ist ohne Anmeldung für jeden
erreichbar. Eine Test-Instanz trägt häufig Einstellungen, die für Produktion
falsch sind. Vor dem Livegang einer öffentlichen Anwendung:

| Prüfpunkt | Wie |
|---|---|
| Welche Pfade sind `public`? Bewusst? | Manifest (`routes:`), Instanzseite im Portal |
| Suchmaschinen-Sperre (falls die Anwendung einen Schalter hat) | `sudo oaap app config list <mandant>-<name>`: In der Test-Instanz **an**, in Produktion **je nach Absicht**. Zeigt eine Seite unter der echten Domain des Kunden, soll sie meist **aus** sein, sonst taucht sie in Suchmaschinen nicht auf. Umgekehrt gilt: eine Test-Instanz bleibt gesperrt. |
| Titel und Anzeigename ohne „Test" | Der Titel kommt aus dem Manifest der Anwendung und geht mit dem Paket in Produktion. Steht dort „Test", muss die nächste Version das ändern. |
| Adressen | Die dynamisch erzeugte Plattform-Adresse bleibt gültig; eine eigene Domain des Kunden kommt als Alias dazu (F27). |
| Kontaktangaben und Pflichtseiten | Impressum, Datenschutz, Kontakt sind Inhalt der Anwendung; die Plattform prüft sie nicht. |

Eine Suchmaschinen-Sperre ist **keine Zugriffskontrolle**: Wer die Adresse
kennt, sieht die Seite. Was nicht öffentlich sein darf, gehört hinter eine
Rolle.

### F27 – Wie bekommt eine Anwendung die Domain des Kunden (z. B. `www.verein.example`)?
*Stichwörter: Alias, Subdomain, eigene Domain, DNS, Umleitung, Instanz-Name*

**Kurzantwort:** Am Beispiel einer Anwendung geprüft: Die Subdomain des Kunden
wird als weiterer Name in der **Instanz** eingetragen (Aliasse, RFC-0018) und
im DNS des Kunden auf den Knoten gerichtet. Danach antwortet die Instanz unter
beiden Namen; die erzeugte Plattform-Adresse bleibt bestehen. Eine reine
HTTP-Umleitung beim Domain-Anbieter des Kunden ist ein anderer Weg und legt
kein Zertifikat auf dem Knoten an.

Reihenfolge:

1. Zuerst mit einer **Subdomain** der Kundendomain testen, nicht mit der
   Hauptdomain; die Hauptdomain erst nach dem Test umstellen.
2. Name in der Instanz eintragen
   (`sudo oaap app address set <mandant>-<name> <hostname>`, Befehl siehe
   `cli/README.md`), danach im DNS des Kunden den Eintrag setzen, der auf
   den Knoten zeigt. Das Zertifikat kommt automatisch.
3. Im Browser prüfen: gültiges Zertifikat (der Knoten holt es beim ersten
   Aufruf, das dauert einige Sekunden) und die richtige Anwendung.
4. Die Test-Instanz bleibt unter ihrer Plattform-Adresse; sie bekommt keine
   Kundendomain.

Ungeprüft: ob die Übernahme (`promote`) einer neuen Version die eingetragenen
Namen der Produktivinstanz behält. Nach jeder Übernahme `sudo oaap app address
show <mandant>-<name>` ansehen.

### F28 – Wie ändert der Mandantenverwalter das Gesicht seines Mandanten (Titel, Farben, Logo)?

*Stichwörter: Gesicht, Mandant, Titel, Farbe, Logo, Vorschau, tenant_admin*

**Kurzantwort:** Im Portal unter **Mandant → „Das Gesicht ändern“**. Der Mandantenverwalter ändert dort nur den **eigenen** Mandanten; den Mandanten braucht er nicht zu nennen. Titel und Logo sind öffentlich (sie stehen auf der Anmeldeseite), der Klarname nicht.

- **Farben:** neben dem Hex-Feld steht ein Farbwähler; beide bleiben im Gleichstand. „Zurücksetzen“ leert die Farbe (es gilt wieder die der Plattform). Ohne JavaScript bleibt das Hex-Feld, der Farbwähler erscheint dann gar nicht.
- **Vorschau:** zeigt Kopfzeile, Schaltfläche und Textzeile mit dem, was gerade im Formular steht, **ohne zu speichern**. Gerechnet wird auf dem Server mit derselben Rechnung wie auf der Seite selbst: eine zu helle Hauptfarbe dreht die Schrift der Kopfzeile auf dunkel, Text auf Weiß wird abgedunkelt. Ein gewähltes, noch nicht gespeichertes Logo erscheint lokal im Browser, ohne Upload.
- **Logo:** PNG, JPEG, WebP oder GIF, höchstens 512 KB, **kein SVG**.
- Eine Änderung steht im Mandantenprotokoll dieses Mandanten. Auch eine **Ablehnung** steht dort (vor 0.1.182 landete sie beim Standard-Mandanten, den ein Verwalter nicht sieht).

Der Betreiber (`server_admin`) kann einen Mandanten benennen; er sieht die Seite nie im Gesicht eines Kunden, damit er sie nicht mit der eines Kunden verwechselt.

### F29 – Eine Instanz-Adresse öffnen, der Mandant hat einen eigenen Anmeldedienst (Keycloak): Was soll passieren?

*Stichwörter: Anmeldung, Instanz-Adresse, Anmeldedienst, IdP, Weiterleitung, Plattform-Benutzer*

**Kurzantwort:** Wer ohne Sitzung eine Instanz-Adresse öffnet und dessen Mandant einen eigenen Anmeldedienst hat, wird **gleich zum Anmeldedienst** geschickt — nicht auf die Plattform-Anmeldeseite. Danach kommt er an die Instanz-Adresse zurück, mit dem Ziel, das er geöffnet hatte. Die Anmeldeseite der Plattform (für Plattform-Benutzer) erscheint nur **am Ort des Mandanten** (`<mandant>.<knoten>`) und an der Wurzel des Knotens.

- Der Anmeldedienst kennt nur die Rückkehr-Adresse des Mandanten-Ortes. Deshalb startet die Anmeldung dort; die Sitzung gilt anschließend unter der ganzen externen Domain, also auch an der Instanz.
- Zurückgeschickt wird nur an Adressen unter der externen Domain des Knotens; eine fremde Adresse im Parameter wird ignoriert.
- Hat der Mandant **keinen** Anmeldedienst, bleibt es bei der Plattform-Anmeldeseite.
- Ein Betreiber, der sich mit seinem Plattform-Konto anmelden will, geht an die Wurzel des Knotens (oder an den Mandanten-Ort); die Sitzung gilt dort wie an jeder Instanz.

### F30 – Kann ein Mandant automatisch aufgebaut werden, und was passiert bei einem Abbruch?

*Stichwörter: Mandant, Profil, Aufbau, tenant build, Rückbau, Fortsetzen, Wartepunkt, server_admin*

**Kurzantwort:** Ja, seit Referenz **0.1.183** mit einem **Profil** (einer JSON-Datei in `/var/lib/oaap/profiles/`) und `sudo oaap tenant build start <profil> --param label=<kürzel> --param title="…"`. Die Schritte von F1 bis F29 (Mandant, Richtlinie, Gesicht, App aus einem Paket, Realm, Adresse) laufen in einem Aufruf; ein Schritt gilt als erledigt, wenn seine **Prüfung** es bestätigt.

- **Abbruch:** der Aufbau wird **fortgesetzt**, nicht wiederholt: `sudo oaap tenant build continue <id>`. Gemessen auch nach einem hart beendeten Prozess.
- **Rückbau** nur auf Wunsch (`rollback <id> --yes`) und **nur, was dieser Aufbau angelegt hat**. Die Daten einer entfernten Instanz bleiben (und halten den Mandanten fest), außer man sagt `--purge-instances`; ein **Realm und seine Personen bleiben immer**; ein Mandant mit Inhalt wird nie entfernt.
- **Der erste Verwalter** bleibt ein Schritt für einen Menschen (OAAP legt nie eine Person im Anmeldedienst des Kunden an); der Aufbau hält dort an (`WAITING`).
- **Portal und API:** nur ein angemeldeter `server_admin`, nie ein Schlüssel (Maschinenkonten bekommen diese Rolle nicht). Im Portal gibt es ab Referenz 0.1.184 den Menüpunkt **Aufbau** (Assistent: Formular aus dem Profil, Verlauf, Weiter prüfen, Fortsetzen, Zurückbauen).
- **Apps und Profile im Portal:** ein Profil steuert mit `bool`-Parametern und `"when"`, welche Apps ein Mandant bekommt (`app.install` mit `app` = ID aus dem Katalog). Profile lassen sich im Portal unter **Aufbau** hochladen, herunterladen und löschen, mit einer Vorlage als Anfang (ab Referenz 0.1.187); der Knoten prüft jede hochgeladene Datei ganz und lässt darin nur Apps des Katalogs zu, nie Pfade.
- **Ein Interessent, der den Mandanten selbst beantragt:** du gibst ihm einen **Einladungslink** (einmal benutzbar, mit Ablauf, an ein Profil gebunden); er füllt ein Formular aus, daraus wird ein **Antrag**, den du im Portal freigibst oder ablehnst (ab Referenz 0.1.186). Das Formular baut nichts, und OAAP schreibt ihm keine E-Mail.
- **Noch nicht an einem echten Knoten gemessen:** die Schritte für den Realm und die Außenadresse, und der Weg des Einladungslinks durch das echte Gateway.

Schritt für Schritt: [Einen Mandanten aus einem Profil aufbauen](../szenarien/mandant-aus-profil-aufbauen.md). Spezifikation: RFC-0055.

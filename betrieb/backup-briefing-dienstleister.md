# Briefing: Datensicherung eines OAAP-Mandantenknotens durch einen Dienstleister

> Stand: Referenz 0.1.150. Platzhalter: `<knoten>` (der zu sichernde Knoten),
> `<dienstkonto>` (Konto des Dienstleisters auf dem Knoten), `<ziel>` (Ablage
> des Dienstleisters). Enthält keine Zugangsdaten und keine konkreten Adressen.
> Zweck: Dem Dienstleister erklären, **was** gesichert werden muss, **was wir
> erwarten** und **welche Wege** es gibt — unabhängig davon, welche Werkzeuge
> er einsetzt. Als „gebaut" ist nur gekennzeichnet, was es heute gibt;
> Vorschläge sind als solche markiert.

## 1. Worum es geht

Ein Knoten (eine Debian-VM) führt viele Kunden-Mandanten mit eigenen Anwendungen
und einen zentralen Anmeldedienst (Keycloak, als Anwendung des Knotens mit
eigener Datenbank). Alle Daten liegen unter einem Verzeichnisbaum des Knotens
und in Docker-Volumes dieser Anwendungen. Verloren gehen darf weder der Bestand
der Kunden noch der Anmeldedienst mit seinen Benutzern und Geheimnissen.

## 2. Was wir selbst schon tun (gebaut)

| Was | Wie | Ergebnis |
|---|---|---|
| Vollsicherung des Knotens | `oaap backup create`, nächtlich per systemd-Timer (Voreinstellung 03:30) | **ein** Archiv `oaap-backup-<zeitstempel>.tar.gz` plus Prüfsumme `….sha256` in `/var/backups/oaap` (Verzeichnis und Dateien nur für `root`, Modus 0600) |
| Konsistenz | Die Anwendungen stehen **nur für das Kopieren** still (gemessen: Sekunden bis wenige zehn Sekunden), komprimiert wird danach | Datenbanken sind im Archiv konsistent, nicht nur „absturzkonsistent" |
| Aufbewahrung auf dem Knoten | die N neuesten Archive (Voreinstellung 2) | zwei Wiederherstellungspunkte vor Ort |
| Archiv je Mandant | `oaap backup create --tenant <kürzel>` | beweist **Existenz**, ist **nicht** direkt zurückspielbar (siehe 6) |
| Ablehnen von Mandanten | `oaap backup exclude <kürzel> --reason …` | nur mit Begründung, im Begleitblatt und im Mandantenprotokoll sichtbar |
| Eigene Abholung (bei uns im Einsatz) | zweiter Knoten holt per SSH, prüft die Prüfsumme, legt Generationen an (täglich 7, wöchentlich 4, monatlich 6) und schreibt eine Statusdatei | siehe 5 |
| Sichtbarkeit | Gesundheitsseite des Portals zeigt: letzter Lauf (ok/fehlgeschlagen, Größe, Ausfallzeit), Zeitplan, **Abholungen** (angekommen, Prüfsumme bestätigt, Generationen) | siehe 5 |

**Wichtige Eigenschaften**

- Gesichert wird immer **vollständig**. Es gibt keine inkrementellen Ketten; ein
  Archiv ist für sich allein wiederherstellbar. Das ist eine Entscheidung.
- Ein Archiv enthält **alle Geheimnisse des Knotens im Klartext** (Benutzer mit
  Passwort-Hashes, Zugangsschlüssel, Konfigurationen) und die **Daten aller
  Mandanten**. Es ist damit selbst schutzbedürftig wie der Knoten.
- Wiederherstellung: frische Debian-Maschine, Installer im Modus `restore`
  mit dem Archiv. Es werden **alle** Instanzen neu gebaut. Einmal vollständig
  erprobt (Löschen und Neuaufbau, Daten byte-gleich).
- Das Mandanten-Archiv enthält den Realm des Anmeldedienstes nicht gesondert;
  der Realm steckt im **Vollarchiv** (Anwendungsdaten von `auth`).

## 3. Was wir vom Dienstleister erwarten

Fachlich (unabhängig vom Werkzeug):

1. **Getrennt vom Knoten:** Die Kopie liegt außerhalb der Ausfall- und
   Angriffsdomäne des Knotens (andere Hardware/anderer Standort). Wer den
   Knoten übernimmt, darf die Kopien weder lesen noch löschen können.
2. **Wiederherstellungspunkte:** höchstens 24 h Datenverlust (RPO); mehrere
   Generationen, mindestens täglich 7 / wöchentlich 4 / monatlich 6 (oder
   gleichwertig).
3. **Prüfbar:** Die Prüfsumme (`.sha256`) wird nach dem Kopieren verglichen,
   nicht nur das Ankommen gemeldet.
4. **Wiederherstellbar in vereinbarter Zeit (RTO):** Zielwert gemeinsam
   festlegen; **mindestens einmal jährlich** eine echte Wiederherstellung auf
   einer leeren Maschine, mit Protokoll.
5. **Vertraulich:** Zugriff nur für benannte Personen, Verschlüsselung der
   Ablage; die Kopien enthalten Kundendaten (Auftragsverarbeitung nötig).
6. **Meldet Fehler** aktiv (ausgeblieben, unvollständig, Prüfsumme falsch,
   Platz knapp) — und lässt uns den Erfolg **sehen** (siehe 5).
7. **Löschfristen:** Gelöschte Daten bleiben bis zum Ablauf der längsten
   Generation in Kopien. Das ist mit den Mandanten so zu vereinbaren.

Technisch:

- Der Dienstleister **muss unsere Werkzeuge nicht benutzen**. Maßgeblich ist das
  Archiv in `/var/backups/oaap` (oder eine Momentaufnahme der VM, siehe 4a).
- **Nicht** einzelne Verzeichnisse im laufenden Betrieb mit einem Dateiwerkzeug
  kopieren: Datenbanken wären inkonsistent. Konsistent ist das Archiv.
- Zeitfenster: Das Archiv entsteht nachts (Voreinstellung 03:30, Dauer je nach
  Datenmenge einige Minuten). Abholung und VM-Snapshots **danach** legen,
  nicht in das Fenster des Archivlaufs.

## 4. Die Wege (Optionen)

**a) VM-Momentaufnahme auf Hypervisor-Ebene** (Werkzeug des Dienstleisters).
Vorteil: der Dienstleister braucht nichts auf dem Knoten. Nachteil: nur
absturzkonsistent, wenn sie mitten im Archivlauf oder bei laufenden Datenbanken
entsteht; die Wiederherstellung betrifft immer die **ganze** VM. Taugt als
zweite Schicht („schnelles Zurück"), nicht als alleinige Sicherung.

**b) Der Dienstleister holt die Archive mit seinem Werkzeug** (z. B. sein
Backup-Agent oder `rsync`/Backup-Software über SSH mit seinem Dienstkonto).
Vorteil: eigene Werkzeuge, eigene Aufbewahrung, eigene Überwachung. Er braucht
**Leserecht auf `/var/backups/oaap`** — also Zugriff auf alle Geheimnisse.
Empfehlung: **ausschließlich lesend**, ohne Shell auf alles zu erlauben (siehe
„Beschränkter Schlüssel").

**c) Beschränkter Schlüssel (gebaut, bei uns im Einsatz).** Das Dienstkonto
bekommt einen SSH-Schlüssel mit erzwungenem Befehl: er darf genau drei Dinge —
Archive **auflisten**, eine Prüfsumme **lesen**, ein Archiv **senden**. Kein
Schreiben, kein Löschen, keine Shell. Jedes Werkzeug, das `rsync` über SSH
sprechen kann, funktioniert damit. Sicherheitsaussage: Wer die Kopien hat, kann
die Quelle nicht verändern; wer die Quelle übernimmt, kommt nicht an die Kopien.

**d) Wir schieben zum Dienstleister** (Push auf dessen Ablage, z. B. SFTP/S3).
Vorteil: der Dienstleister braucht keinen Zugang zum Knoten. Nachteil: der
Knoten hält dann ein Zugangsrecht nach außen. Bedingung unverhandelbar: dieses
Recht darf **nur anlegen**, nie lesen und nie löschen (Ablage mit
Objektsperre/„append-only"). **Nicht gebaut**, im Entwurf vorgesehen.

**e) Verschlüsselung vor der Übergabe (Vorschlag, nicht gebaut).** Das Archiv
wird auf dem Knoten mit einem Schlüssel verschlüsselt, den **wir** halten
(z. B. `age`/GPG). Der Dienstleister speichert nur Chiffretext und kann den
Inhalt nicht lesen. Das entschärft Punkt 3.5 deutlich; der Preis ist, dass wir
den Schlüssel selbst sicher aufbewahren müssen (ohne Schlüssel keine Rückkehr).

**Empfehlung:** (c) oder (b) für die Archive **plus** (a) als zweite Schicht,
(e) vor allem dann, wenn der Dienstleister den Inhalt nicht sehen soll.
Aufbewahrungsfristen und Generationen kann dabei der Dienstleister mit seinem
Werkzeug verwalten.

## 5. Wie sieht OAAP einen erfolgreichen Backup (Szenario)

Drei Ebenen — **jede Wahrheit entsteht dort, wo sie jemand prüfen kann**:

1. **Der Knoten sichert sich selbst** (gebaut): Das Portal zeigt auf der
   Gesundheitsseite den letzten Lauf mit Ergebnis, Größe, Ausfallzeit, Zeitplan.
   Jeder Lauf wird geschrieben, auch der fehlgeschlagene — „nie eingerichtet"
   ist von „fehlgeschlagen" unterscheidbar.
2. **Der Dienstleister bestätigt die Kopie** (Format gebaut, Weg nicht):
   Das Portal liest je Quelle eine kleine JSON-Datei mit dem Ergebnis der
   Abholung (angekommen, Prüfsumme bestätigt, Zahl der Generationen) und zeigt
   sie an. Nur die abholende Seite weiß, ob die Kopie angekommen ist — deshalb
   schreibt **sie** die Quittung, nicht der gebende Knoten. Der Dienstleister
   muss dazu **nach erfolgreicher Prüfung** eine Datei in der folgenden Form
   ablegen (ein Skript seines Werkzeugs genügt):

   ```json
   {
     "schema": "0.1", "kind": "pull",
     "source_node": "<knoten>", "puller": "<name-des-dienstleisters>",
     "started": "2026-01-01T04:00:00Z", "finished": "2026-01-01T04:03:10Z",
     "result": "ok", "message": "",
     "fetched": "oaap-backup-….tar.gz", "bytes": 123456789,
     "checksum_verified": "yes",
     "generations": {"daily": 7, "weekly": 4, "monthly": 6}
   }
   ```

   Ablage auf dem Knoten: `/var/lib/oaap/apps/backup-pulls/<name>.json`,
   lesbar für alle (Modus 644). Das Portal liest nur; es verändert nichts.
   **Vorschlag, noch nicht gebaut:** Der erzwungene Befehl bekommt eine vierte,
   eng begrenzte Anfrage „Quittung ablegen", sodass das Dienstkonto sonst
   nichts schreiben darf. Bis dahin gibt es zwei Übergangswege: ein einzelner
   `sudo`-Eintrag für genau ein Quittungsskript, oder wir lesen das Ergebnis
   des Dienstleisters selbst und legen die Quittung von Hand ab.
3. **Die Wiederherstellung ist bewiesen** (von Hand, im Kalender): Eine
   ungeprüfte Sicherung ist keine. Mindestens jährlich Wiederherstellung auf
   einer leeren Maschine, Ergebnis (Instanzen, Benutzer, Mandanten, Daten)
   dokumentieren. Bei uns hat der einzige Probelauf drei Lücken gefunden, die
   keine reine Archivprüfung gefunden hätte.

**Ablauf im Betrieb (Sollbild):**

```text
03:30  Knoten: Vollarchiv + Prüfsumme                   -> Portal: "letzter Lauf ok"
04:00  Dienstleister: holt per beschränktem Schlüssel,
       prüft Prüfsumme, legt in seine Ablage / Generationen
04:10  Dienstleister: schreibt Quittung                  -> Portal: "Abholung ok, Prüfsumme bestätigt"
jährlich  Wiederherstellung auf leerer Maschine          -> Protokoll
```

Fehlt die Quittung oder meldet sie `failed`, muss das jemand sehen: heute zeigt
das Portal es (rot), eine aktive Benachrichtigung ist ein Wunsch.

## 6. Grenzen, die man kennen muss

- **Kein Wiederherstellen einzelner Mandanten** in einen laufenden Knoten
  (nicht gebaut). Wiederherstellung = ganzer Knoten aus dem Vollarchiv, oder
  `oaap tenant adopt` des Mandantenarchivs auf einen für diesen Mandanten
  leeren Knoten.
- Mandantenarchive laufen **nicht** nach Zeitplan (Idee vorhanden); sie sind
  keine Ersatz für das Vollarchiv.
- Archive wachsen mit der Zahl der Mandanten; Platz auf dem Knoten
  (2 Generationen plus Arbeitskopie beim Komprimieren) und beim Dienstleister
  planen. Der Befehl prüft den Platz vorher und lehnt laut ab.
- Während des Archivlaufs stehen die Anwendungen kurz still.

## 7. Fragen an den Dienstleister (Fragebogen)

1. Welche Sicherungswerkzeuge setzt ihr ein, und können sie Dateien per SSH
   (`rsync`/SFTP) von einem Dienstkonto holen? Oder nur VM-/Agent-basiert?
2. Wo und wie lange liegen die Kopien, auf welcher Hardware, in welchem Land?
3. Wer hat Zugriff, wie wird protokolliert, und ist die Ablage verschlüsselt?
   Könnt ihr mit **vorverschlüsselten** Archiven (Chiffretext) arbeiten?
4. Welche RPO/RTO bietet ihr an, und wie testet ihr Wiederherstellungen?
5. Wie meldet ihr einen Fehlschlag (E-Mail, Ticket, Webhook)? Könnt ihr nach
   erfolgreicher Sicherung eine kleine Datei auf den Knoten schreiben (siehe 5)?
6. VM-Snapshots: Wie oft, wie lange, mit oder ohne Gast-Quiescing, und lassen
   sie sich außerhalb des Archivfensters legen?
7. Wie läuft die Wiederherstellung: Wer baut die leere Maschine, wer startet
   den Installer, was dürfen wir selbst auslösen?
8. Auftragsverarbeitung: Vertrag, Unterauftragnehmer, Löschung nach Vertragsende.

## 8. Kurzfassung für ein Gespräch

> Wir sichern nachts konsistent per Vollarchiv mit Prüfsumme auf dem Knoten.
> Ihr holt dieses Archiv mit euren Mitteln (lesend, mit beschränktem
> Schlüssel oder Dienstkonto) aus `/var/backups/oaap` in eure getrennte Ablage,
> prüft die Prüfsumme und bestätigt das mit einer kleinen Quittungsdatei, die
> unser Portal anzeigt. Zusätzlich gern Snapshots der VM als schnelle zweite
> Schicht. Einmal im Jahr stellen wir gemeinsam auf einer leeren Maschine
> wieder her.

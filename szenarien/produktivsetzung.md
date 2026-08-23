# Nach Produktiv übernehmen — und notfalls zurück

> Geprüft gegen Referenz **0.1.42** (2026-08-23). Grundlage: RFC-0020.

**Die Zusage, um die es geht:** Produktiv geht **genau das, was getestet
wurde** — nicht dieselbe Versionsnummer, nicht ein neuer Bau desselben
Standes, sondern **dieselben Bytes**, nachweisbar per Prüfsumme. Deshalb
gibt es keinen zweiten Upload: Übernommen wird das aufbewahrte Paket
des Teststands.

## Voraussetzungen

- Eine **Test-Instanz**, die über den **Paket-Weg** (ZIP, RFC-0019)
  beliefert wird — nur dort kann die Plattform „dieselben Bytes"
  beweisen. Eine aus Git installierte Test-Instanz bietet die Übernahme
  **nicht** an; einmal per Paket ausrollen, dann steht sie bereit.
- Du bist **server_admin**: Produktivsetzung ist eine menschliche
  Entscheidung. Deploy-Token spielen hier keine Rolle — Produktiv-
  Instanzen bekommen nie eines.
- Die Version auf dem Teststand ist **höher** als die produktive.

## Der Weg im Portal (der Normalfall)

1. Portal → **Instanzen** → die Test-Instanz (z. B. `meine-app-test`)
   → Reiter **Deployment**.
2. Karte **„Nach Produktiv übernehmen"**: bestehende Produktiv-Instanz
   wählen — *oder* einen neuen Namen eintragen, dann **entsteht** die
   Produktiv-Instanz bei der Übernahme.
3. **Übernehmen** klicken. Fertig ist es, wenn die Produktiv-Instanz
   die neue Version zeigt (Reiter Überblick → Herkunft nennt Teststand
   und Prüfsumme).

Dasselbe an der Maschine: `sudo oaap app promote meine-app-test --to meine-app`.

## Was dabei garantiert ist

- Die Produktiv-Instanz **behält**: ihre Daten, ihre
  Konfigurationswerte (ein Test-Geheimnis reist nie mit), ihre
  Adressen, Sichtbarkeits-Gruppen, Kachel, Drosselung und Ports.
- **Nur höhere Versionen.** Dieselbe oder eine ältere Version wird
  abgelehnt — die Version ist die einzige verlässliche Antwort auf
  „was läuft hier?".
- **Rahmen-Erweiterungen stoppen zuerst.** Will das Paket mehr als die
  Produktiv-Instanz bisher durfte (neue öffentliche Route, neuer
  Speicher, neuer Port), bricht der erste Versuch ab und **nennt jeden
  Grund**. Erst nach Deiner ausdrücklichen Bestätigung läuft die
  Übernahme — die Erweiterung steht damit *vor* der Zustimmung, nie
  dahinter.

## Zurück, wenn es sein muss

Zurück geht es nicht über eine Übernahme (die nimmt nur höhere
Versionen), sondern über den **Rückschritt** auf ein aufbewahrtes
Paket — die Plattform hält das aktuelle plus drei Vorgänger:

- Portal → Instanz → „Hochgeladene Pakete", oder
- `sudo oaap app artifact list meine-app` und
  `sudo oaap app artifact rollback meine-app`

Achtung bei Apps mit eigener Datenmigration (typisch bei wrapped Apps
und Versionssprüngen): Was die **App** beim Start an ihren Daten
umbaut, macht ein Paket-Rückschritt nicht rückgängig. Im Zweifel vor
der Übernahme ein Backup (`sudo oaap backup create --to …`).

## Wenn etwas hakt

- **Die Karte „Nach Produktiv übernehmen" fehlt auf dem Teststand:**
  Die Instanz ist aus Git installiert oder hat noch kein aufbewahrtes
  Paket — einmal über den Paket-Weg (Studio oder Projekt-KI)
  ausrollen.
- **„production takes a higher version only":** Das Paket auf dem
  Teststand trägt keine höhere Version — die Projekt-KI muss
  `app.version` im Manifest bei jedem Paket erhöhen.
- **Die Übernahme nennt Erweiterungen, die Du nicht erwartest:**
  Erst verstehen, dann bestätigen. Jede genannte Zeile ist etwas, das
  produktiv ab jetzt erlaubt wäre.
- **Keine Antwort ist keine Ablehnung:** Auf kleinen Maschinen dauert
  der erste Bau; verbindlich ist das Protokoll des Knotens bzw. die
  Instanzliste im Portal, nicht die wartende Oberfläche.

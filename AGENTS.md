# Repository AGENT

Lies zuerst:
- ../VISION.md
- ../MANIFEST.md
- ../CURRENT_STATE.md

Dieses Repository ist die **Anwender-Dokumentation** von OAAP.

Regeln:
- **Sprache: Deutsch.** Zielgruppe sind Betreiber und Anwender
  (Referenz-Personas Bernd und Lars), nicht die Spec-Leserschaft.
- **Eine Quelle, drei Auslieferungen:** dieses Repo ist die Quelle;
  ausgeliefert wird als Hilfecenter-Store-App (offline, hinter der
  Firewall), als öffentliche Site (GitHub Pages) und als Verweis im
  Portal. Inhalte müssen ohne externe Ressourcen lesbar sein
  (reines Markdown, keine eingebetteten Fremd-Inhalte).
- **Keine Geheimnisse, keine privaten Adressen.** Beispiele verwenden
  Platzhalter (`<adresse>`, `<instanz>`, `beispiel.de`) — niemals echte
  Passwörter, Tokens, LAN-IPs oder Kundennamen.
- **Doku folgt der Referenz.** Jede Seite trägt oben die
  Referenz-Version, gegen die sie geprüft wurde. Bei CLI-Änderungen in
  `oaap-reference` gehört der Doku-Nachtrag zum Patch.
- Struktur: `szenarien/` (Schritt-für-Schritt), `apps/` (je OAAP-App),
  `cli/` (Befehlsreferenz mit Beispielen).

Arbeite nur innerhalb dieses Repositories.

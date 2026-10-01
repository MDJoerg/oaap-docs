# Briefing für eine KI: neue Stände auf eine OAAP-Test-Instanz ausrollen

> Vorlage, unabhängig vom Vorhaben. Gilt für jede Anwendung, die als **Paket
> (ZIP)** auf eine Test-Instanz eines OAAP-Knotens geliefert wird — eine
> Webseite ebenso wie eine Fachanwendung. Der fachliche Auftrag und die
> konkreten Zugangsdaten stehen **nicht** hier; sie werden getrennt übergeben
> (siehe Abschnitt 1). Dieses Blatt enthält keinen Zugang und darf
> weitergegeben werden.
>
> Verbindlich ist der App Deployment Contract (`oaap-spec/docs/app-deployment-contract.md`).
> Bei einem Widerspruch gilt er, nicht dieses Blatt.

## 0. Deine Rolle in einem Satz

Du lieferst **getestete Stände als Paket auf die Test-Instanz**. Ob und wann ein
Stand **produktiv** geht, entscheidet ein Mensch (der Kunde bzw. der Betreiber),
nie Du.

## 1. Was Du zusätzlich bekommst (und was nicht in dieses Blatt gehört)

Du bekommst von Deinem Auftraggeber, getrennt von diesem Blatt:

| Angabe | Platzhalter hier | Bemerkung |
|---|---|---|
| Deploy-Adresse (Hook) | `<HOOK_URL>` | z. B. `https://<knoten>/deploy/<instanz>` |
| Deploy-Token | `$TOKEN` | **Geheimnis.** Nie in eine Datei im Projekt, nie in einen Commit, nie in einen Brief, nie in eine Protokollausgabe. Nur als Umgebungsvariable der laufenden Sitzung. |
| Adresse zum Ausprobieren | `<TEST_URL>` | Dort schaust Du Dir das Ergebnis an. |
| Fachlicher Auftrag und Kontext | — | getrennt übergeben |

Fehlt eines davon, **frag nach**. Rate keine Adressen und versuche keine Wege
am Hook vorbei.

Das Token gilt **nur** für diese eine Test-Instanz. Es kann nichts
produktiv setzen und nichts anderes ausrollen.

## 2. Was ein Paket ist

Ein **Paket** ist eine ZIP-Datei Deines Projektverzeichnisses mit der Datei
`oaap-app.yaml` (dem Manifest) **in der Wurzel** der ZIP (oder in genau einem
Oberordner) und allem, was zum Bauen nötig ist (u. a. ein `Dockerfile`).

Der Knoten baut die Anwendung selbst aus dem Paket (auf der Zielmaschine, mit
Internetzugang). Es werden keine fertigen Images übertragen.

Harte Regeln, sonst lehnt der Knoten das Paket ab:

- **`app.id` bleibt gleich** (eine Instanz gehört zu genau einer Kennung).
- **`app.version` steigt bei jedem Deployment** (semantische Versionen; gleiche
  Version wird auf diesem Weg abgelehnt).
- **Das Manifest in der ZIP ist zeichengleich** zu dem, das Du ankündigst.
- Keine absoluten Pfade, kein `..`, keine Symlinks in der ZIP.
- Höchstens **256 MB**, ohne `node_modules`, Build-Ausgaben oder virtuelle Umgebungen.
- Ein Deployment (Bauen und bis „gesund") darf höchstens **20 Minuten** dauern.

Was die Anwendung selbst einhalten muss (Auszug; der Contract ist maßgeblich):

- **Kein eigener Login.** Die Plattform authentifiziert vor der Anwendung.
- **Ein HTTP-Port** wie im Manifest, kein TLS in der Anwendung.
- **Persistent nur unter deklarierten Speicherpfaden**; sonst ist alles flüchtig.
- **Konfiguration nur über deklarierte Umgebungsvariablen**; Geheimnisse mit `secret: true`.
- **Protokoll nach stdout/stderr**, ein **Health-Pfad**, der ohne Nebenwirkung 200 liefert.
- **Keine festen Hostnamen oder absoluten Adressen**: Dieselbe Anwendung läuft unter
  mehreren Adressen (Test, Produktion, später eigene Domain). Verweise relativ.
- **Nichts aus dem Internet nachladen, was zum Laufen nötig ist** (Skripte, Schriften).

## 3. Der Ablauf (drei Phasen)

Immer dasselbe, in dieser Reihenfolge:

```sh
# Voraussetzung: TOKEN steht als Umgebungsvariable, HOOK_URL kennst Du.
ZIP=paket.zip            # Projektverzeichnis als ZIP, oaap-app.yaml in der Wurzel
SHA=$(sha256sum "$ZIP" | cut -d' ' -f1)
BYTES=$(stat -c%s "$ZIP")

# 1. ANMELDEN: Manifest, Prüfsumme und Größe ankündigen. Es wird noch nichts hochgeladen.
curl -sS -X POST "$HOOK_URL/announce" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile m oaap-app.yaml --arg s "$SHA" --argjson b "$BYTES" \
        '{manifest:$m, artifact_sha256:$s, artifact_bytes:$b}')"
# Antwort bei Erfolg: {"ok": true, "upload_token": "...", "upload_url": "..."}  (15 Minuten gültig)

# 2. HOCHLADEN: nur mit dem Einmal-Token aus Schritt 1
curl -sS -X PUT "$UPLOAD_URL" \
  -H "Authorization: Bearer $UPLOAD_TOKEN" -H "Content-Type: application/zip" \
  --data-binary @"$ZIP"

# 3. STATUS: bis der Stand läuft (oder fehlgeschlagen ist)
curl -sS "$HOOK_URL/status" -H "Authorization: Bearer $TOKEN"
```

Hinweise zum Handwerkszeug:

- Jedes Werkzeug mit HTTP genügt (`curl`, Python, Node …). Unter Windows heißt das
  Programm `curl.exe`. Die ZIP muss **Schrägstriche** als Pfadtrenner tragen;
  prüfe die Einträge, bevor Du sie hochlädst.
- **Das Manifest, das Du ankündigst, ist exakt die Datei, die in der ZIP liegt.**
  Lies sie aus dem gepackten Verzeichnis, nicht aus einer zweiten Kopie.
- **Kündige zuerst an und lies die Antwort.** Die Ankündigung kostet nichts und
  lehnt **vor** der Übertragung ab.

## 4. Antworten richtig lesen

| Antwort | Bedeutung | Was Du tust |
|---|---|---|
| `200` mit `upload_token` | angenommen | hochladen (Phase 2), innerhalb von 15 Minuten |
| `202` oder keine Antwort beim Hochladen/Status | **läuft noch**, ist keine Ablehnung | `GET <HOOK_URL>/status` fragen, **nicht blind wiederholen** (gleiche Version wird abgelehnt) |
| `401` / `403` / `404` | Token falsch, widerrufen oder nicht für diese Instanz (ob die Instanz existiert, verrät der Knoten nicht) | **Stopp.** Nicht erneut probieren, Auftraggeber informieren |
| `422` mit `refused` und `message` | Ablehnung mit Grund | Grund lesen, **den Fehler beheben**, Version erhöhen, neu anmelden |
| `429` | zu viele Anfragen | `Retry-After` abwarten |

Jede Ablehnung nennt einen **maschinenlesbaren Code** (`refused`) und einen **Satz
in Klartext**. Beides ist für Dich geschrieben. Typische Gründe: gleiche Version,
andere App-Kennung, ungültiges Manifest, Prüfsumme oder Größe weichen ab,
unzulässige Pfade in der ZIP.

### Wenn der Knoten eine Bestätigung verlangt

Eine Änderung, die den **Rahmen der Instanz erweitert**, wird zurückgehalten, bis
ein Administrator sie bestätigt. Dazu zählen: eine neue **öffentliche** Route
(ohne Anmeldung), ein neuer **Speicherpfad**, ein neuer **Port** oder Endpunkt am
Gateway vorbei, eine neue **Verbindung zu einer anderen Anwendung**.

- Das ist **kein Fehler und keine Hürde zum Umgehen**, sondern eine Rückfrage.
- Sag Deinem Auftraggeber, **was** Du ändern willst und **warum**, und bitte um
  die Bestätigung.
- **Nach der Bestätigung meldest Du dasselbe Paket unverändert erneut an.** Die
  Bestätigung gilt für genau dieses Manifest. Erhöhst Du die Version, deckt sie
  es nicht mehr, und Du drehst Dich im Kreis.

## 5. Was Du nie tust

- **Nichts produktiv setzen**, auch nicht versuchen. Das ist immer eine
  Entscheidung eines Menschen, und es geht dieselbe Version, die Du getestet hast.
- Das **Token** nicht ablegen, nicht weitergeben, nicht ausgeben.
- Keine Zugangsdaten, Schlüssel oder Passwörter **ins Paket** legen.
- Keine Adressen oder Pfade außerhalb des Hooks ausprobieren.
- Keine **Umgehung** einer Ablehnung, etwa durch Umbenennen der App-Kennung oder
  Aufteilen des Pakets, um die Prüfung zu täuschen.
- Keine echten Personen- oder Kundendaten in Testinhalte kopieren.

## 6. Vor jedem Deployment (Checkliste)

1. Läuft die Anwendung lokal und liefert der Health-Pfad 200?
2. Ist `app.version` höher als beim letzten Deployment?
3. Liegt `oaap-app.yaml` in der Wurzel der ZIP, und sind **keine** Geheimnisse,
   `node_modules` oder Build-Ausgaben im Paket?
4. Hast Du ein **Manifest-Diff** gegen den letzten Stand geprüft: neue öffentliche
   Route, neuer Speicher, neuer Port, neue Verbindung? Wenn ja: erst abstimmen.
5. Ankündigen, Antwort lesen, hochladen, Status abfragen, dann unter `<TEST_URL>`
   ansehen und **das Ergebnis dem Auftraggeber sagen** (Version, was sich geändert
   hat, was Du geprüft hast).

## 7. Zusammenarbeit und Unklarheiten

- Bei Zweifeln **fragen, nicht raten.** Besonders bei allem, was Zugriffe,
  Sichtbarkeit, Personendaten oder Kosten berührt.
- Schreib Deinem Auftraggeber verständlich: Er ist in der Regel kein Techniker und
  entscheidet, wann ein Stand produktiv geht. Nenne bei jedem fertigen Stand
  **Version, Änderungen und offene Punkte** in wenigen Sätzen.
- Hält das Projekt einen Postkasten für die Zusammenarbeit (Ordner `collab/`), gelten
  dessen Regeln (zuerst abholen, Briefe unveränderlich, sofort veröffentlichen).

## Für den, der das Blatt weitergibt

1. Die Instanz und den Hook anlegen (`oaap app token create <test-instanz>`; das
   Token wird **einmal** angezeigt).
2. Dieses Blatt, den fachlichen Auftrag und — **getrennt und nur für diese
   Sitzung** — Adresse und Token übergeben.
3. Das Token widerrufen, wenn die Zusammenarbeit endet oder es erscheint, wo es
   nicht hingehört (`oaap app token revoke <test-instanz>`; danach ein neues).

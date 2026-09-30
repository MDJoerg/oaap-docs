# Ein getestetes Paket vom Referenzknoten auf einen Mandantenknoten bringen

> Geprüft gegen Referenz **0.1.146** (Ziel) und **0.1.150** (Referenzknoten), 2026-09-30.
> Für Anwendungen, die **nicht** im Store liegen (eigene oder private Pakete).
> Platzhalter: `<ref>` (Referenzknoten), `<ziel>` (Mandantenknoten),
> `<mandant>` (Kürzel), `<instanz>` (Name), `<version>`, `<sha12>`.

**Grundgedanke:** Übertragen wird ein **Paket** (ZIP mit Prüfsumme), kein Image.
Der Zielknoten baut die App selbst aus dem Paket. Als „freigegeben" gilt
nur, was auf dem Referenzknoten **getestet und produktiv gesetzt** wurde
(Übernahme, RFC-0020): dieselben Bytes, die dort in Produktion laufen.
Die Testinstanz des Referenzknotens ist oft neuer; sie ist **nicht**
freigegeben.

## 1. Das freigegebene Paket bestimmen (Referenzknoten)

```sh
sudo oaap app list | grep <instanz>                 # produktive Version
sudo oaap app artifact list <schlüssel-produktiv>   # "<- running" = die laufende
```

Der Dateiname enthält Version und die ersten Stellen der Prüfsumme
(`<version>-<sha12>.zip`). Die volle Prüfsumme steht in der Instanzseite
(Portal) und lässt sich mit `sha256sum` nachrechnen.

## 2. Paket herausgeben und übertragen

Über das Portal (Instanzseite → *Hochgeladene Pakete* → Herunterladen) oder
auf dem Referenzknoten:

```sh
sudo cp <pfad>/artifacts/<version>-<sha12>.zip /tmp/paket.zip && sudo chown $USER /tmp/paket.zip
scp <benutzer>@<ref>:/tmp/paket.zip .          # auf den Rechner des Betreibers
scp paket.zip <benutzer>@<ziel>:/tmp/          # und weiter auf den Zielknoten
sha256sum /tmp/paket.zip                       # auf dem Ziel: muss zur Prüfsumme passen
```

Das Paket enthält Code und Dokumentation der Anwendung, **keine Kundendaten**
(Instanzdaten liegen in `storage/`, nicht im Paket). Die Kopien danach
löschen.

## 3. Auf dem Zielknoten: Testinstanz, dann Übernahme

Der Mandant muss bestehen (siehe [Kunden-Mandanten einrichten](kunden-mandant-anlegen.md)).

```sh
sudo oaap app install /tmp/paket.zip --name <instanz>-test --channel test --tenant <mandant>
sudo oaap app config list <mandant>-<instanz>-test        # welche Schlüssel fehlen?
sudo oaap app config set <mandant>-<instanz>-test <SCHLÜSSEL> <wert>
```

Die Instanz heißt für die CLI `<mandant>-<name>` (FAQ F16). Nach dem Setzen
der Konfiguration neu starten (`oaap app restart <mandant>-<instanz>-test`),
Gesundheit und Adresse prüfen (`https://<instanz>-test.<mandant>.<knoten>/`),
dann übernehmen:

```sh
sudo oaap app promote <mandant>-<instanz>-test --to <mandant>-<instanz>
sudo oaap app promote <mandant>-<instanz>-test --to <mandant>-<instanz> --confirm   # wenn der erste Versuch Gründe nennt
```

Die Übernahme installiert **dasselbe Paket** (gleiche Prüfsumme) in die
Produktivinstanz. Sie kann nur höhere Versionen und nennt jeden Grund,
wenn das Paket den Rahmen der Instanz erweitert.

## 4. Was danach festgehalten wird

| Mandant | Instanz | Paket | Version | Prüfsumme | Kanal | Eingespielt am |
|---|---|---|---|---|---|---|

Ein handgeführtes Register genügt für die ersten Mandanten. Mit mehreren
Mandanten braucht es eine Übersicht und einen Update-Ablauf: siehe RFC-0049.

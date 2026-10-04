# Pakete auf einem Mehrmandanten-Knoten bereitstellen — der Paketkatalog

> Geprüft gegen Referenz **0.1.192** (Test auf `oaap-test`, 2026-10-04); App `package-catalog` **0.1.0**.
> Für Pakete, die **nicht** im öffentlichen Store liegen und die Mandanten-Administratoren
> selbst installieren sollen, ohne dass der Betreiber ZIP-Dateien von Hand verschiebt.
> Platzhalter: `<katalog>` (Name der Katalog-Instanz), `<app>`, `<version>`.

**Grundgedanke:** Der Betreiber hat eine kleine App, den **Paketkatalog**. Dort lädt er ZIP-Pakete
hoch und **gibt Versionen frei**. Freigegebenes erscheint im Store jedes Mandanten-Administrators
und wird dort wie jede andere App installiert oder aktualisiert. Hochgeladen heißt **nicht**
freigegeben; was nicht freigegeben ist, sieht kein Mandant.

Nur der Betreiber lädt hoch (Rolle `admin` der Katalog-App). Ein Paket ist Code, den der Knoten
baut und ausführt — wer hier freigibt, bestimmt, was Mandanten installieren können.

## 1. Einmal einrichten (Betreiber)

```sh
# die App installieren, z. B. im Betreiber-Mandanten
sudo oaap app install https://github.com/MDJoerg/oaap-apps --path apps/package-catalog --name <katalog>
# den Katalog zur Store-Quelle des Knotens machen
sudo oaap store add-catalog <katalog> --name "Betreiber-Katalog"
```

`add-catalog` trägt **keine Adresse** ein, sondern verweist auf die Instanz dieses Knotens. Der
Knoten liest Liste und Pakete direkt aus dem Speicher der Instanz — nichts davon ist im Netz
sichtbar, und es gibt keinen Schlüssel. Standard ist die Vertrauensklasse „geprüft"; mit
`--trust unverified` verlangt jede Installation eine ausdrückliche Bestätigung (sinnvoll, wenn
Sie jede Version erst in Ihrem eigenen Test-Portal ausprobieren wollen).

## 2. Ein Paket freigeben (Betreiber)

In der Katalog-App: **Neue Version hochladen** (ZIP, bis 256 MB) → die Seite zeigt die Version als
„nicht freigegeben" → **Freigeben**. Die App liest nur `oaap-app.yaml` aus der ZIP und lehnt schon
beim Hochladen ab, woran der Knoten später scheitern würde (Pfade mit `..`, Verknüpfungen, kein
Manifest, ungültige Version).

- **Eine Version wird nie überschrieben.** Dieselbe App-Id mit derselben Version ist ein Fehler;
  die Version im Manifest muss steigen.
- Im Store steht je App die **höchste freigegebene** Version. **Zurückziehen** nimmt eine Version
  wieder heraus (bereits installierte Instanzen bleiben unberührt).
- **Löschen** einer freigegebenen Version verlangt einen Grund, der im Protokoll der App bleibt.
- Jede gespeicherte ZIP lässt sich wieder **herunterladen** (der Fall „gib mir die ZIP").

## 3. Installieren (Mandanten-Administrator)

Im Store des Portals erscheint die App mit der Quelle „Betreiber-Katalog". Beim **Installieren**
entscheidet der Administrator je App:

- **Direkt in Produktion** — für einen Kurzlink-Dienst, der keine Testinstanz braucht;
- **Mit einer Test-Instanz** (`<app>-test`) — für eine Webseite: erst ausprobieren, dann
  „nach Produktiv übernehmen" (RFC-0020).

Später bietet der Store **Aktualisieren auf v…**, sobald der Betreiber eine höhere Version freigibt.
Für Test-Instanzen gilt weiter der Weg über die Übernahme bzw. den Deploy-Hook.

## 4. Was der Knoten vor jeder Installation selbst prüft

Der Katalog ist eine App, und was sie ins Verzeichnis schreibt, gilt als **Daten**:

1. Der Knoten kopiert das Paket in ein eigenes Verzeichnis und prüft **Größe und SHA-256 der
   Kopie** gegen die Liste — ändert die App die Datei danach, ändert sich nichts an dem, was
   installiert wird.
2. Ein Pfad, der aus dem Speicher hinausführt oder über eine Verknüpfung geht, wird **nicht
   gefolgt**.
3. **App-Id und Version aus der Liste** werden mit dem Manifest im Paket verglichen.
4. Danach gelten die Regeln jeder ZIP-Installation: sicheres Entpacken, Rahmenregel, „Produktion
   nimmt nur eine höhere Version", Kanalregel.

Schlägt eine Prüfung fehl, steht der **Grund** in der Antwort („the package does not match the
checksum in the catalog's list"), nicht „nicht gelistet".

## Grenzen (Stand 0.1.192)

- Eine frisch freigegebene Version erscheint im Store nach der nächsten Zustandsaktualisierung
  (Minuten), nicht sofort.
- Die Sicht ist für alle Mandanten gleich; ein Filter je Mandant ist vorgesehen, aber nicht gebaut.
- Der Katalog **auf einem anderen Knoten** (ein Referenzknoten beliefert Zielknoten) ist Stufe 3
  von RFC-0050 und noch nicht vorhanden.
- „Aktualisieren" im Store gilt für die Instanz mit dem Namen der App.

*Quelle: RFC-0050, Spec `oaap.apps.runtime` 2.6 (0.2.37).*

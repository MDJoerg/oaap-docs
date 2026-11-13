---
id: szenario/ki-gateway-ueber-connector
title: "Ein KI-Gateway im Internet nutzt Modelle aus dem eigenen Netz"
audience: [server_admin, support]
applies_from: "0.1.277"
checked_against: "0.1.277"
checked_on: 2026-11-13
lang: de
tags: [ki, ki-gateway, ollama, connector, connect, tunnel, destination, bezugsquelle, via, modelle]
---
# Ein KI-Gateway im Internet nutzt Modelle aus dem eigenen Netz

> Geprüft gegen Referenz **0.1.277** (2026-11-13). Die Kette wurde auf
> `oaap-test` ganz über das Portal eingerichtet: Schlüssel, Connector,
> Angebot, Destination und ein Aufruf aus einer App bis zum Gateway.
> Danach hat sie ein Betreiber zwischen zwei echten Knoten selbst aufgebaut:
> einem Server im Internet und einem Knoten im eigenen Netz.

Im eigenen Netz läuft ein Knoten mit lokalen Modellen, zum Beispiel Ollama
hinter einem OAAP-KI-Gateway. Ein zweites KI-Gateway auf einem Server im
Internet soll diese Modelle **mit anbieten**, neben externen Anbietern.
Die Daten bleiben dabei im eigenen Netz, und im Router wird **kein Port
geöffnet**: Der innere Knoten wählt sich beim äußeren ein (Connector,
RFC-0033). Der äußere erreicht das innere Gateway nur über diesen Tunnel.

```text
Client ──► KI-Gateway (äußerer Knoten) ──► Destination via:<tunnel>/<angebot>
                                            │  Tunnel, vom inneren Knoten aufgebaut
                                            ▼
                    KI-Gateway (innerer Knoten) ──► Ollama
```

Durchgespielt wird das mit diesen Namen. Ersetze sie durch deine:

| | Beispiel |
|---|---|
| äußerer Knoten (im Internet) | `oaapx01`, Adresse `https://<äußerer-knoten>` |
| innerer Knoten (im eigenen Netz) | `oaapi01` |
| Mandant auf beiden Knoten | `ais` |
| KI-Gateway-Instanz auf beiden Knoten | `mg` |
| Tunnel (Name des Connectors) | `oaapi01` |
| Angebot auf dem inneren Knoten | `mg` |
| Destination auf dem äußeren Knoten | `intern` |

## Voraussetzungen

- Beide Knoten laufen auf Referenz **0.1.277** oder neuer. Erst seit dieser
  Version gibt es die Portalseite **Connector**, und eine Destination lässt
  sich einem KI-Gateway als Bezugsquelle zuordnen.
- Ein Konto mit der Rolle **`server_admin`** auf beiden Knoten. Schlüssel,
  Connectoren und Angebote sind Entscheidungen über das Netz des Knotens;
  ein `tenant_admin` sieht die Seite nicht, `support` sieht sie ohne Formulare.
- Der äußere Knoten hat einen **externen Namen** mit `https`. Dort wählt sich
  der Connector ein.
- Auf dem inneren Knoten läuft das KI-Gateway mit mindestens einem
  Modellnamen, der lokal antwortet (siehe
  [App aus dem Store](app-aus-dem-store.md)).
- Auf dem äußeren Knoten ist das KI-Gateway installiert, in Version
  **0.5.5** oder neuer (Schritt 0).

## Schritt 0: KI-Gateway auf dem äußeren Knoten aktualisieren

Auf dem **äußeren** Knoten im Portal unter **Store** die Instanz `mg` auf
0.5.5 oder neuer aktualisieren. Ältere Fassungen kennen keine Bezugsquelle
aus einer Destination.

**Prüfen:** Die Fußzeile der Gateway-Seite nennt `OAAP KI-Gateway 0.5.5`
oder eine höhere Version.

## Schritt 1: Zugangsschlüssel auf dem äußeren Knoten ausstellen

Auf dem **äußeren** Knoten: **Gesundheit → „Schlüssel, Connectoren und
Angebote einrichten“**, oder direkt die Seite `/connector`. Im Bereich
„äußerer Knoten“ einen Zugangsschlüssel ausstellen:

- Name des Tunnels: `oaapi01`
- Mandant: `ais`. Vorbelegt ist der Mandant der Adresse, auf der du bist.

Der Schlüssel (`oaapc_…`) erscheint **genau einmal** auf der Antwortseite.
Kopiere ihn gleich. Die Seite nennt dazu die Adresse des äußeren Knotens und
den Namen, die du auf dem inneren Knoten einträgst.

**Prüfen:** Die Tabelle der Tunnel auf `/connector` führt `oaapi01` mit dem
Mandanten `ais`, noch nicht verbunden.

## Schritt 2: Connector und Angebot auf dem inneren Knoten anlegen

Auf dem **inneren** Knoten die Seite `/connector`, Bereich „innerer Knoten“:

1. **Connector anlegen:** Name `oaapi01`, Adresse `https://<äußerer-knoten>`,
   Schlüssel aus Schritt 1. Nur `https://` ist erlaubt.
2. **Angebot hinzufügen** beim Connector `oaapi01`:
   - Name: `mg`
   - Ziel: die **öffentliche Adresse** des inneren Gateways **ohne** `/v1`,
     also `https://mg.ais.<innerer-knoten>`.

Das Ziel ist die öffentliche Adresse, weil der Connector-Dienst nicht im Netz
der App steht. Die eigene Anmeldung des Gateways (sein API-Schlüssel) bleibt
dabei in Kraft. Lass `/v1` weg, weil die Plattform Basis des Angebots und
angefragten Pfad aneinanderhängt. Das Gateway auf dem äußeren Knoten fragt
selbst `…/v1/…` an (Schritt 6).

**Prüfen:**
- Auf dem inneren Knoten zeigt `/connector` den Connector als
  „verbunden“ und das Angebot `mg`.
- Auf dem äußeren Knoten steht der Tunnel `oaapi01` jetzt mit „verbunden
  seit …“ und dem Angebot `mg`.

## Schritt 3: API-Schlüssel im inneren Gateway ausstellen

Auf dem **inneren** Knoten im KI-Gateway `mg` einen Schlüssel für den
Verbraucher „äußeres Gateway“ ausstellen, zum Beispiel mit dem Etikett
`oaapx01`. Beschränke ihn auf die Modellnamen und die Ampelfarbe, die nach
außen gehen dürfen.

Auch dieser Schlüssel (`sk-oaap-…`) wird **einmal** angezeigt.

**Prüfen:** Der Schlüssel steht in der Liste des inneren Gateways als
„gültig“.

## Schritt 4: Destination auf dem äußeren Knoten anlegen

Auf dem **äußeren** Knoten im Portal **Destinationen** des Mandanten `ais`
öffnen und eine neue Destination anlegen:

- Name: `intern`
- Ziel: `via:oaapi01/mg`. Das Formular schlägt es vor, sobald der Tunnel
  verbunden ist und ein Angebot trägt; es zeigt nur Tunnel des eigenen
  Mandanten.
- Anmeldung: **Bearer**, mit dem Schlüssel aus Schritt 3.

Die Plattform setzt den Schlüssel unterwegs in die Anfrage. Das äußere
Gateway sieht ihn nie.

**Prüfen:** Die Destination `intern` steht mit „via oaapi01/mg“ und
„Bearer, Geheimnis gesetzt“ in der Liste.

## Schritt 5: Destination der Gateway-Instanz zuordnen

Auf dem **äußeren** Knoten: **Instanz `mg` → Netz**. Das KI-Gateway erklärt
im Manifest eine Familie von Bezugsquellen (`supplier`, beliebig viele
http-Destinationen). In dieser Zeile `intern` auswählen und zuordnen. Die
Instanz startet dabei neu.

**Prüfen:** Unter „Destinationen“ der Instanz steht `intern` als
zugeordnet.

## Schritt 6: Im Gateway als Bezugsquelle anlegen

Im **äußeren** KI-Gateway `mg` unter **Bezugsquellen** steht jetzt der
Abschnitt **„Aus Destinationen der Plattform“** mit einem Formular für
`intern`:

- Die Adresse ist vorbelegt (Adresse der Destination + `v1`). Lass sie so.
- Die Ampel ist mit **gelb** vorbelegt. Sie sagt, was mit den Daten hinter
  dem Ziel geschehen kann. Wähle sie bewusst.
- Ein Feld für Zugangsdaten gibt es nicht, weil die Plattform sich anmeldet.

**„Als Bezugsquelle anlegen“** klicken. Danach unter **Modellnamen** einen
Namen anlegen oder erweitern, der auf diese Quelle zeigt, etwa
`intern:<modellname-des-inneren-gateways>`.

**Prüfen:**
- Die Bezugsquelle `intern` zeigt bei „Zugangsdaten“ den Satz „meldet die
  Plattform an (Destination intern)“.
- Ab KI-Gateway 0.6.0: In ihrer Zeile auf **„testen“** klicken. Das Gateway
  fragt die Modellliste ab, ein Ping durch die ganze Kette, der auch den
  Schlüssel prüft. Grün heißt: Der Weg steht, mit den Modellen des inneren
  Gateways. Im Reiter **Modelle** prüft „testen“ einen Modellnamen mit einer
  Mini-Anfrage (höchstens 1 Token).
- Eine Anfrage an das äußere Gateway mit diesem Modellnamen wird
  beantwortet, und unter „Letzte Anfragen“ steht `intern` als benutzte
  Quelle.

## Dasselbe auf der Kommandozeile

Für kopflose Knoten. Jeder Befehl braucht `sudo`.

```sh
# äußerer Knoten: Zugangsschlüssel (wird EINMAL angezeigt)
sudo oaap connect key issue oaapi01 --tenant ais

# innerer Knoten: Connector, Schlüssel verdeckt von der Standardeingabe
sudo oaap connector add oaapi01 --endpoint https://<äußerer-knoten> --key-stdin
sudo oaap connector offer add oaapi01 mg --to https://mg.ais.<innerer-knoten>
sudo oaap connector list

# äußerer Knoten: Tunnel und Angebot sehen
sudo oaap connect list

# äußerer Knoten: Destination mit Bearer-Schlüssel, dann zuordnen
sudo oaap destination add intern --tenant ais --kind http \
     --target via:oaapi01/mg --auth bearer --secret-stdin
sudo oaap destination bind mg intern --tenant ais
sudo oaap destination bindings mg --tenant ais
```

Den Schlüssel des inneren Gateways stellst du auf dessen Seite aus, oder
im Container mit `python3 /srv/app.py key issue oaapx01`. Das Anlegen der
Bezugsquelle geschieht in jedem Fall auf der Seite des äußeren Gateways.

## Wenn es schiefgeht

Der schnellste Weg zur Ursache ist der Knopf **„testen“** bei der
Bezugsquelle im äußeren Gateway (ab 0.6.0, Reiter **Bezugsquellen**). Er
nennt den Fall in Worten:

| Ergebnis des Tests | bedeutet | weiter bei |
| ------------------ | -------- | ---------- |
| erreichbar, mit Modellen | die Kette steht | — |
| Anmeldung abgelehnt (HTTP 403) | Weg steht, Schlüssel falsch | 403 unten |
| Tunnel steht, Ziel wird nicht angeboten (HTTP 404) | Angebot fehlt | „trägt keinen Aufruf“ |
| Tunnel ist nicht verbunden (HTTP 502) | Connector fehlt, pausiert, Schlüssel widerrufen | „nicht verbunden“ |
| `…/models` unbekannt (HTTP 404) | Pfad falsch, oft `/v1` doppelt | 404 unten |

### Antwort 403 „Kein gültiger API-Schlüssel“ (`invalid_api_key`)

Das ist eine **gute** Nachricht für den Weg: Die Anfrage ist durch den
Tunnel bis zum inneren Gateway gekommen. Falsch ist nur der Schlüssel. Er
wurde in Schritt 3 widerrufen, oder die Destination trägt einen anderen.
Abhilfe: im inneren Gateway einen neuen Schlüssel ausstellen und bei der
Destination `intern` als neues Geheimnis setzen (Portal, oder
`oaap destination set-secret intern --tenant ais --secret-stdin`).

### Der Tunnel ist nicht verbunden

Auf dem inneren Knoten zeigt `/connector` (oder `oaap connector list`) den
Grund. Häufige Ursachen:

- **Schlüssel falsch oder widerrufen:** auf dem äußeren Knoten neu
  ausstellen und auf dem inneren mit „Schlüssel ersetzen“ eintragen
  (`oaap connector set-key oaapi01 --key-stdin`).
- **Falsche Adresse:** Gemeint ist die `https`-Adresse des äußeren Knotens,
  nicht die einer App.
- **Pausiert:** Ein pausierter Connector trägt keine Aufrufe. Fortsetzen.

### Der Tunnel steht, trägt aber keinen Aufruf

`oaap connector list` sagt „offers nothing -- the tunnel carries no call“,
`oaap connect list` auf dem äußeren Knoten „offers: none“. Es fehlt das
Angebot aus Schritt 2. Ohne Angebot antwortet eine Destination
`via:oaapi01/mg` mit 404 „The inner node does not offer 'mg' on this
tunnel“.

Das passiert auch, wenn der Connector **entfernt und neu angelegt** wurde:
Mit dem Connector gehen seine Angebote. Das Angebot dann neu anlegen.

### Ein Angebot wird abgelehnt

Ein Angebot auf einen **Plattformdienst** (Portal, Anmeldung und andere)
lehnt der Knoten ab. Biete die App über ihre öffentliche Adresse an
(Schritt 2).

### Antwort 404 vom inneren Gateway (`unknown_path`)

Der Pfad trägt `/v1` doppelt: Das Angebot zeigt auf `…/v1`, und die
Bezugsquelle hängt noch einmal `v1` an. Nimm eine der beiden Stellen
zurück, am einfachsten das `/v1` im Ziel des Angebots.

### Der Schlüssel aus Schritt 1 ist weg

Er lässt sich nirgends nachlesen. Auf dem äußeren Knoten den alten
widerrufen (nur mit dem Häkchen „wirklich“) und einen neuen ausstellen.
Die Seite nennt beim Widerrufen die Destinationen, die damit abreißen.

### Es klappt aus dem eigenen Netz, aber nicht über den Tunnel

Das Angebot ruft die **öffentliche** Adresse des inneren Gateways auf, also
vom inneren Knoten aus über den eigenen Router zurück in das eigene Netz
(„Hairpin-NAT“). Viele Router können das, nicht alle, und manche nur für
bestimmte Ports. Prüfe auf dem inneren Knoten, ob er seine eigene
öffentliche Adresse erreicht. Eine Anfrage an `…/v1/models` ohne Schlüssel
muss die 403 des Gateways liefern, keinen Zeitablauf.

## Weiterführend

- Ohne zweiten Knoten etwas vom Laptop zeigen:
  [Einen lokalen Dienst freigeben](lokalen-dienst-freigeben.md)
- Spezifikation: `oaap.net.connector` §2.9 (Einrichten im Portal) und
  `oaap.net.destinations` §2.2 (`any: true`) in `oaap-spec`
- RFC-0033 (Destinationen und Connector), RFC-0060 (Tunnel als App)
- Befehle: [`oaap connect`](../cli/generated/connect.md),
  [`oaap connector`](../cli/generated/connector.md),
  [`oaap destination`](../cli/generated/destination.md)

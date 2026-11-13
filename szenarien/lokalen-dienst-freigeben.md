---
title: "Einen lokalen Dienst über die Plattform freigeben (wie ngrok)"
audience: [tenant_admin, server_admin]
checked_against: "0.1.249"
checked_on: 2026-11-11
lang: de
tags: [freigabe, tunnel, ngrok, laptop, expose, connector, connect, localhost, entwicklung]
---
# Einen lokalen Dienst über die Plattform freigeben (wie ngrok)

> Geprüft gegen Referenz **0.1.249** (2026-11-11): Weg A Ende-zu-Ende auf
> `oaap-test` mit dem echten Client von einem Windows-Laptop gemessen
> (Anmeldung, Schlüssel eines Mitglieds, `--public`, Schließen durch den
> Betreiber). Weg B am Code und an der Spezifikation gelesen, an diesem Tag
> nicht neu durchgespielt. Nicht gemessen: das Zertifikat auf Zuruf an einem
> Knoten **ohne** Edge (siehe „Grenzen").

Du hast auf deinem Rechner etwas laufen, zum Beispiel einen
Entwicklungsserver auf `http://localhost:3000`, und willst es für eine Weile
im Internet zeigen. OAAP vergibt dafür eine
**Freigabe**: einen zufälligen Namen wie
`https://k3f9x2mh4a.t.<knoten>/`, eine Ablaufzeit, und standardmäßig die
Anmeldung des Mandanten davor. Dein Rechner wählt sich **nach außen** ein.
Er öffnet keinen Port, braucht keine Portfreigabe im Router, und die
Adresse deines Ziels verlässt ihn nie.

Es gibt **zwei Wege**:

| | Weg A: Laptop-Client | Weg B: innerer Knoten |
|---|---|---|
| Wer | `tenant_admin` des Mandanten | `server_admin` des inneren Knotens |
| Was auf dem Rechner läuft | eine Python-Datei, **kein OAAP-Knoten** | ein installierter OAAP-Knoten |
| Ziel | was auf dem Laptop läuft | jede Adresse, die der innere Knoten erreicht (LAN, Gerät, Container) |
| Typischer Fall | „Ich will meinen Dev-Server kurz zeigen“ | „Ein Gerät im Firmennetz soll von außen erreichbar sein“ |

Für den ngrok-Fall nimmst du **Weg A**.

## Voraussetzungen

- Ein OAAP-Knoten mit **externem Namen** (`oaap external set <name>`).
  Nur dann gibt es die Zone `t.<name>`, unter der die Freigaben liegen.
  Ohne externen Namen lehnt der Knoten jede Freigabe mit einem Satz ab.
  Prüfen kann es der Betreiber mit `sudo oaap connect exposures`, die
  erste Zeile nennt die Zone.
- Für Weg A: ein Konto mit der Rolle **`tenant_admin`** in dem Mandanten,
  dessen Anmeldung vor der Freigabe stehen soll, außerdem Python 3.9+ und
  `aiohttp` auf dem Laptop (Linux, macOS, Windows).
- Für Weg B: ein zweiter, installierter OAAP-Knoten (der „innere“) und
  `sudo` auf beiden Knoten.

## Weg A: vom Laptop, ohne eigenen Knoten

### Schritt 1: API-Schlüssel ausstellen

Im Portal unter **Zugänge → Schlüssel ausstellen**: als Prinzipal dich
selbst, Rolle **`tenant_admin`**, eine kurze Gültigkeit (ein paar Tage).
Der Schlüssel (`oaapk_…`) wird **einmal** angezeigt. Den Schlüssel
**nicht** auf eine Instanz begrenzen: Die Freigabe gehört keiner Instanz.

Auf der Kommandozeile geht dasselbe für den Betreiber:

```sh
sudo oaap key issue <benutzer> --roles tenant_admin --days 3 --label "Freigabe Laptop"
```

Ein Schlüssel kann nie `server_admin` tragen. Ein Betreiber ohne
`tenant_admin`-Konto nimmt deshalb Weg B.

### Schritt 2: den Client holen

Der Knoten bietet den Client selbst an. Es ist eine Datei ohne Geheimnis:

```sh
curl -o oaap-expose.py https://<knoten>/connect/client
python3 -m pip install aiohttp
```

Unter Windows heißt der Aufruf meist `py -3` statt `python3`. Wer sein
System-Python sauber halten will, legt vorher eine venv an.

### Schritt 3: freigeben

```sh
export OAAP_KEY=oaapk_...          # PowerShell: $env:OAAP_KEY = "oaapk_..."
python3 oaap-expose.py expose http://localhost:3000 \
        --server https://<knoten> --tenant <mandant> --ttl 4h
```

Der Schlüssel kommt aus `OAAP_KEY` oder aus einer verdeckten Abfrage, nie
als Argument, damit er in keiner Prozessliste steht. `--server` und
`--tenant` lassen sich auch als `OAAP_SERVER` und `OAAP_TENANT` setzen.

Der Client antwortet mit der Adresse und dem Ablauf:

```text
  http://q0d1kdlx4p.t.<knoten>/
  behind the login of the tenant; open until 2026-11-11T07:34:29Z  (Ctrl-C ends it)
```

**Steht der Knoten hinter einer Edge,** druckt der Client `http://`. Von
außen gilt trotzdem `https://`, die Edge leitet `http` dorthin um. Gib also
die `https`-Adresse weiter.

Das Fenster bleibt offen, solange die Freigabe läuft. Bricht die
Verbindung ab, wählt sich der Client selbst wieder ein und **behält den
Namen**.

### Schritt 4: was Besucher erleben

- **Mit Anmeldung (Vorgabe):** Wer keine Sitzung hat, landet auf der
  Anmeldung **unter demselben Namen**. Hinein kommt jede angemeldete
  Person des Mandanten, ein `server_admin` immer. Dein Dienst bekommt die
  geprüften Identitäts-Kopfzeilen (`X-OAAP-User` und Verwandte) und darf
  ihnen trauen, denn was ein Besucher selbst unter diesen Namen schickt,
  kommt nicht an.
- **`--public`:** keine Anmeldung, leere Identitäts-Kopfzeilen, dafür eine
  Bremse von 120 Aufrufen je 60 Sekunden je Besucheradresse, danach 429.
  Nur ein `tenant_admin` darf `--public`. Läuft trotzdem ab.
- **Was dein Dienst nie bekommt:** das Sitzungs-Cookie der Plattform und
  einen API-Schlüssel. Alle anderen Cookies und den eigenen `Host`
  (`localhost:3000`) bekommt er. Er kann umgekehrt die Sitzung des Knotens
  nicht setzen.

### Schritt 5: beenden, verlängern, kontrollieren

- **Beenden:** `Ctrl-C` im Fenster des Clients. Der Name ist danach ein 404.
  Achtung: Wird der Client **hart** beendet (Fenster geschlossen, Prozess
  abgeschossen), bleibt der Name bis zum Ablauf reserviert. Hängt kein
  Client mehr daran, antwortet er 502. Sofort zu macht ihn dann der
  Betreiber (unten).
- **Verlängern:** Beim Client gibt es kein Verlängern. Ein Neustart mit
  neuer `--ttl` ergibt eine neue Freigabe mit **neuem Namen**. Wähle die
  `--ttl` also gleich passend (höchstens 7 Tage).
- **Widerrufen:** Wird der Schlüssel widerrufen oder verliert das Konto
  `tenant_admin`, endet der Tunnel mit allen Freigaben binnen etwa einer
  Minute, und der Client sagt, warum.
- Ein Konto hält höchstens 5 Laptop-Tunnel gleichzeitig.

## Weg B: über einen inneren Knoten

Der innere Knoten wählt sich beim äußeren ein (RFC-0033), und der äußere
vergibt den Namen.

```sh
# auf dem ÄUSSEREN Knoten (mit externem Namen): einen Verbindungsschlüssel ausstellen
sudo oaap connect key issue werkstatt --tenant <mandant>
#   -> zeigt den Schlüssel EINMAL und den Befehl für die Gegenseite

# auf dem INNEREN Knoten: den Connector anlegen, Schlüssel verdeckt eingeben
sudo oaap connector add werkstatt --endpoint https://<äußerer-knoten> --key-stdin
sudo oaap connector list            # "connected since ..."

# befristet freigeben (Vorgabe 8h, höchstens 7d)
sudo oaap connector expose werkstatt http://192.168.178.20:3000 --ttl 8h [--public]
sudo oaap connector extend werkstatt <ref> --ttl 2d
sudo oaap connector unexpose werkstatt <ref>
```

`oaap connector offer add` ist **etwas anderes**: Das bietet ein Backend
dauerhaft unter einem Namen an, damit eine App auf dem äußeren Knoten es
als Destination nutzt. Ein Browser im Internet erreicht ein Angebot nicht.
Für „im Internet zeigen“ ist `expose` richtig.
Ein durchgespieltes Beispiel für ein Angebot steht in
[Ein KI-Gateway im Internet nutzt Modelle aus dem eigenen Netz](ki-gateway-ueber-connector.md).

Öffnen, Verlängern und Loslassen geht für `server_admin` auch im Portal
auf der Gesundheitsseite des inneren Knotens.

## Für den Betreiber des äußeren Knotens

```sh
sudo oaap connect exposures                 # alle lebenden Freigaben, wer, bis wann, Aufrufe; Laptops
sudo oaap connect exposure close <name>     # sofort beenden; der Name kommt nicht wieder
sudo oaap connect exposure log              # die Aufrufe
```

Jede Entscheidung steht im Prüfprotokoll des Mandanten
(`exposure.open|extend|close|expire`), mit Person, Name und Ablauf, aber
**nie mit der Adresse des Ziels**: Der äußere Knoten erfährt sie nicht.

## Grenzen

- **Kein WebSocket durch die Freigabe** (Antwort 501). Dev-Server mit Hot
  Reload (Vite, Next.js) laden die Seite, aktualisieren sich aber nicht von
  selbst.
- **Nur HTTP(S)**, kein rohes TCP. Für einen einzelnen Port in die
  umgekehrte Richtung (vom Knoten zum Laptop) gibt es
  `oaap-expose.py forward` (RFC-0044).
- **Zertifikate:** Ohne Edge holt der Knoten für jeden neuen Namen beim
  ersten Aufruf ein Zertifikat. Let's Encrypt gibt höchstens 50 je Domain
  und Woche aus. `oaap connect exposures` zählt mit und warnt ab 40. Den
  ersten Aufruf eines frischen Namens kann das ein paar Sekunden kosten.
- Höchstens 10 lebende Freigaben je Tunnel und 100 je Knoten.

## Weiterführend

- Spezifikation: `oaap.net.connector` §2.8 (Freigaben) in `oaap-spec`
- RFC-0033 (Destinationen und Connector), RFC-0027 (API-Schlüssel)
- Befehle: [`oaap connect`](../cli/generated/connect.md),
  [`oaap connector`](../cli/generated/connector.md)

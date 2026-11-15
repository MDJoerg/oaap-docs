---
id: szenario/knoten-koppeln
title: "Einen Knoten mit der Zentrale koppeln — per Kopplungsdatei"
audience: [server_admin, support]
applies_from: "0.1.290"
checked_against: "0.1.290"
checked_on: 2026-11-15
lang: de
tags: [flotte, kopplung, zentrale, eingang, fleet, pair, fleetview, broker]
---
# Einen Knoten mit der Zentrale koppeln — per Kopplungsdatei

> Geprüft gegen Referenz **0.1.290** (2026-11-15). Auf `oaap-test`
> gemessen: die direkte Kopplung im LAN, der Weg über einen Eingang,
> Entfernen und Entkoppeln. Am selben Tag wurde der Eingang `oaapx01`
> per Angebot mit der Zentrale `oaap-demo` gekoppelt (Schritt 1 dieser
> Anleitung, per Kommandozeile).

Eine **Zentrale** sammelt, was die Knoten einer Flotte über sich melden:
Lebenszeichen, Messwerte, Zustand und Ereignisse. Daraus macht sie Lagen
(„Knoten verstummt“), Mails und den Zwilling (RFC-0085). Diese Anleitung
koppelt einen Knoten mit einer Zentrale, ohne Schlüssel oder
Konfigurationsdateien von Hand zu kopieren: Man reicht **eine Datei**
weiter.

## Die Regel: Die Datei geht an den, der anruft

Es gibt zwei Arten Kopplungsdatei (Endung `.oaap-pair`, der Inhalt ist
ein Text, der mit `OAAP-PAIR1.` beginnt):

| Datei | erzeugt an | eingespielt an | wozu |
|---|---|---|---|
| **Kopplungsdatei für einen Knoten** | der Zentrale | dem Knoten | Der Knoten ruft den Eingang an und holt sich seinen Schlüssel. |
| **Angebot eines Eingangs** | dem Eingang | der Zentrale | Die Zentrale ruft den Eingang an und holt sich ihren Brückenschlüssel. |

Jede Datei **gilt 15 Minuten und genau einmal**, auch wenn der eine
Versuch abgelehnt wurde. Sie trägt den Fingerabdruck des
HTTPS-Zertifikats der Gegenseite: Wer die Datei einspielt, spricht nur mit
genau diesem Rechner, auch bei einem selbst signierten Zertifikat.
Behandeln Sie die Datei wie ein Passwort für eine Viertelstunde.

## Zentrale, Eingang, Knoten — wer ist was?

- **Zentrale:** Profil `fleet-hub`. Sie darf in einem Heimnetz stehen,
  in das niemand hineinkommt; sie baut ihre Verbindungen selbst nach
  außen auf.
- **Eingang:** ein Knoten mit einem von außen erreichbaren Broker
  (Profile `broker` und `exposed`, öffentlicher Name über
  `oaap external set`). Er nimmt die Meldungen der Knoten an, die
  Zentrale holt sie über eine Brücke ab. Eine Zentrale, die selbst
  erreichbar ist, ist ihr eigener Eingang („direkt“).
- **Knoten:** jeder Knoten, der seine Meldungen an eine Zentrale schicken
  soll.

## Voraussetzungen

- Alle Beteiligten laufen mit Referenz **0.1.290 oder neuer**
  (`oaap version`). Ältere Knoten kennen die Kopplungsdatei nicht.
- Sie sind `server_admin` auf beiden Seiten. Ein `tenant_admin` sieht
  die Kopplung nicht.
- Die Uhr beider Rechner geht richtig (die Dateien laufen nach 15 Minuten
  ab).
- Ein Weg, eine Datei von einem Rechner zum anderen zu bringen: Download
  und Upload im Browser, oder Text kopieren und einfügen. Zeilenumbrüche,
  die ein Mailprogramm einfügt, stören nicht.

## Schritt 1 (einmalig je Eingang): den Eingang mit der Zentrale koppeln

Nur nötig, wenn Knoten **über einen Eingang** kommen sollen, weil die
Zentrale selbst nicht erreichbar ist. Steht der Knoten im Netz der
Zentrale oder ist die Zentrale erreichbar, weiter mit Schritt 2.

1. **Am Eingang:** Portal → *Flotte* → Karte *Eingang für eine Zentrale* →
   *Angebot für eine Zentrale erzeugen*. Die Seite zeigt das Angebot einmal,
   mit *Datei herunterladen*.
   Auf der Kommandozeile:

   ```sh
   sudo oaap fleet pair offer --out /root/eingang.oaap-pair
   ```

2. **An der Zentrale:** Portal → *Flotte* → Karte *Zentrale: Knoten
   koppeln* → Abschnitt *Eingänge* → Angebot hochladen oder Text einfügen →
   *Eingang koppeln*.
   Auf der Kommandozeile:

   ```sh
   sudo oaap fleet pair entry /root/eingang.oaap-pair
   ```

   Die Zentrale ruft den Eingang an, bekommt ihren Brückenschlüssel,
   schreibt ihre Brücke (`data/broker-conf.d/bridge-<eingang>.conf`) und
   **startet ihren Broker neu**. Eine von Hand geschriebene Brückendatei
   mit demselben Namen wird vorher nach `data/fleet-pair/` gesichert.

**Prüfen:** `sudo oaap fleet hub show` an der Zentrale zeigt unter
*Bridges* den Eingang mit `up since <gerade eben>`. Im Portal steht er in
der Liste *Eingänge*. Wurde vorher ein Brückenschlüssel von Hand
ausgestellt, ist er am Eingang jetzt überflüssig:
`sudo oaap key list` zeigt ihn, `sudo oaap key revoke <id>` widerruft ihn.

> Während des Broker-Neustarts ist die Brücke wenige Sekunden weg. Der
> Eingang hält die Meldungen zurück und liefert sie nach. Wer sehr
> empfindliche Lagen eingerichtet hat (`bridge.down`), kann sie für die
> Minute auf einen Testverteiler legen (`oaap notify route`).

## Schritt 2: an der Zentrale die Kopplungsdatei für den Knoten erzeugen

Portal der Zentrale → *Flotte* → *Zentrale: Knoten koppeln*. Aus
**FleetView** führt der Knopf *Knoten koppeln* direkt dorthin.

- **Name des Knotens:** 2–40 Zeichen, Kleinbuchstaben, Ziffern und `-`.
  Unter diesem Namen erscheint er an der Zentrale.
- **Weg:** *direkt an diese Zentrale* oder *über den Eingang …* (aus
  Schritt 1).
- **Der Knoten steht im selben Netz wie diese Zentrale:** nur bei „direkt“.
  Der Knoten verbindet sich dann über die LAN-Adresse.
- **Als Ersatz:** nur, wenn ein Knoten mit diesem Namen neu installiert
  wurde. Sein alter Schlüssel wird beim Koppeln widerrufen.

*Kopplungsdatei erzeugen* zeigt die Datei **einmal**, mit *Datei
herunterladen*. Auf der Kommandozeile:

```sh
sudo oaap fleet pair code <knoten> --via <eingang> --out /root/<knoten>.oaap-pair
```

(ohne `--via` direkt; `--lan` für das eigene Netz; `--replace` als Ersatz)

**Prüfen:** Unter dem Formular steht *Offene Codes:* der Name *(über …, bis
HH:MM UTC)*.

## Schritt 3: am Knoten die Datei einspielen und prüfen

Portal des Knotens → *Flotte* → Karte *Kopplung: an wen dieser Knoten
sendet* → *Kopplungsdatei einspielen* → Datei wählen oder Text einfügen →
*Prüfen*. Aus FleetView führt auf der Seite eines Knotens der Knopf
*Kopplung* dorthin.

Es passiert noch nichts. Die Seite *Kopplung prüfen* zeigt:

- an welche **Zentrale** und über welchen **Weg** der Knoten senden wird,
- unter welchem **Namen**,
- Häkchen für das, was den Knoten verlässt: **Lebenszeichen** (immer,
  nicht abwählbar), **Messwerte**, **Zustand**, **Ereignisse**.

Das Lebenszeichen ist Pflicht, weil die Zentrale sonst einen ausgefallenen
Knoten nicht von einem entfernten unterscheiden kann. Alles andere
entscheidet der Knoten. Die Zentrale kann nichts verlangen, was er nicht
anbietet.

## Schritt 4: koppeln

*Koppeln* auf der Prüfseite. Der Knoten ruft den Eingang an (oder die
Zentrale, bei „direkt“), weist sich mit der Datei aus und bekommt seinen
eigenen Schlüssel (gültig 365 Tage). Danach richtet er seinen Sender ein.
Auf der Kommandozeile:

```sh
sudo oaap fleet pair apply /root/<knoten>.oaap-pair --classes alive,metrics,status
```

**Prüfen:**

- Am Knoten zeigt die Karte *Kopplung*: *Gekoppelt mit der Zentrale … über
  den Eingang …, als …, seit …*.
- An der Zentrale steht der Knoten **innerhalb von etwa einer Minute** in
  der Liste *Knoten dieser Zentrale*, mit *bietet: …*. Auf der
  Kommandozeile: `sudo oaap fleet hub show` zeigt ihn mit `last alive`
  wenige Sekunden alt.
- Danach die Datei löschen (`shred -u` auf der Kommandozeile). Sie ist
  verbraucht, aber sie ist auch nicht mehr nötig.

## Später: ändern, entfernen, entkoppeln

- **Was gesendet wird, ändern:** am Knoten auf der Karte *Kopplung* die
  Häkchen setzen → *Ändern* (`sudo oaap fleet pair classes --classes …`).
- **An der Zentrale entfernen:** in *Knoten dieser Zentrale* →
  *Entfernen* (`sudo oaap fleet pair remove <knoten>`). Die Zentrale
  widerruft den Schlüssel des Knotens beim Eingang. Der Knoten heißt danach
  **„entfernt“**, nicht „verstummt“, und löst keine Mail aus. Ein neuer
  Code für denselben Namen hebt das wieder auf.
- **Am Knoten entkoppeln:** auf der Karte *Kopplung* → *Kopplung lösen*
  (`sudo oaap fleet pair unpair`). Der Knoten gibt seinen Schlüssel beim
  Eingang zurück und sendet nichts mehr.
- **Stand ansehen:** `sudo oaap fleet pair show` (enthält keine
  Geheimnisse).

## Wenn es schiefgeht

| Meldung | Bedeutung und was hilft |
|---|---|
| *Der Code ist abgelaufen. An der Zentrale einen neuen erzeugen.* | Mehr als 15 Minuten vergangen, oder eine der Uhren geht falsch. |
| *Der Code wurde schon benutzt.* | Jede Datei gilt einmal, auch ein abgelehnter Versuch verbraucht sie. Neue erzeugen. |
| *Der Code ist ungültig.* | Die Datei wurde verändert (oder unvollständig kopiert). Neu herunterladen statt abtippen. |
| *Ein Knoten '…' ist hier schon gekoppelt.* | Der Name ist am Eingang vergeben. Wurde der Knoten neu installiert: an der Zentrale einen Code **als Ersatz** erzeugen. Sonst einen anderen Namen wählen. |
| *… zeigt ein anderes Zertifikat als in der Kopplungsdatei.* | Das HTTPS-Zertifikat der Gegenseite wurde seit dem Erzeugen erneuert, oder jemand steht dazwischen. Neue Datei erzeugen. Kommt es danach wieder, **nicht fortfahren**. |
| *Der Eingang … ist nicht erreichbar.* | Der Eingang ist aus, sein Portal antwortet nicht unter seinem öffentlichen Namen, oder eine Firewall sperrt 443. |
| *Dieser Knoten hat keinen von außen erreichbaren Broker (Profile 'broker' und 'exposed').* | Nur ein solcher Knoten kann Eingang sein. |
| *Dieser Knoten hat keinen öffentlichen Namen ('oaap external set').* | Ohne Namen kann niemand den Eingang erreichen. |
| *Dieser Knoten ist keine Zentrale (Profil 'fleet-hub').* | Codes erzeugt nur eine Zentrale. |
| *Das ist das Angebot eines Eingangs; es gehört an die Zentrale.* / *… kein Angebot eines Eingangs, sondern ein Code …* | Die Datei ist an der falschen Seite gelandet. Siehe die Regel oben. |
| *Der Knoten ist gerade beschäftigt (ein Bau läuft). In ein paar Minuten noch einmal.* | Die Gegenseite baut gerade etwas (ein Update, eine App). Die Anfrage wurde zurückgezogen und die Datei **nicht** verbraucht: innerhalb der 15 Minuten mit derselben Datei noch einmal. |
| *Zu viele Versuche -- eine Minute warten.* | Fünf Fehlversuche in fünf Minuten an derselben Tür. Danach geht ein Versuch je Minute. |

**Der Knoten ist gekoppelt, kommt an der Zentrale aber nicht an:**

1. Am Knoten `sudo oaap fleet pair show`: steht `"paired": true` unter
   `sender`?
2. Über einen Eingang: steht die Brücke? (`sudo oaap fleet hub show` an
   der Zentrale, Abschnitt *Bridges*.)
3. An der Zentrale wird der Knoten als *entfernt* gezeigt: Er wurde dort
   früher entfernt. Ein neuer Code für denselben Namen hebt das auf.

## Siehe auch

- [Server aufsetzen](server-aufsetzen.md)
- CLI-Referenz: [`oaap fleet`](../cli/generated/fleet.md)
- RFC-0085 §17 (Nachtrag A3) in `oaap-spec`: das Format der Datei, die
  Türen, warum das Angebot den umgekehrten Weg geht

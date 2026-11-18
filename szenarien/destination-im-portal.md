---
id: szenario/destination-im-portal
title: "Eine Destination im Portal anlegen und einer App zuordnen"
audience: [tenant_admin, server_admin, support]
applies_from: "0.1.300"
checked_against: "0.1.307"
checked_on: 2026-11-18
lang: de
tags: [destination, portal, zuordnen, binden, proxy, uebergabe, erp, ki-gateway, mailserver, tenant_admin]
---
# Eine Destination im Portal anlegen und einer App zuordnen

> Geprüft gegen Referenz **0.1.307** (2026-11-18) an den Portalseiten
> „Destinationen“ und „Instanz → Netz & Adressen“; der Weg ist im
> Mandanten bec auf oaapx01 so gegangen worden (Destination für ein
> SAP-System, zugeordnet an das MCP-Gateway). Spezifikation:
> `oaap.net.destinations`, RFC-0033. Platzhalter: `<mandant>`,
> `<instanz>`, `<destination>`, `erp.beispiel.de`.

Eine **Destination** ist ein Ziel außerhalb der Apps: ein ERP, ein
KI-Gateway, ein Mailserver, ein fremder Dienst im Internet. Eine App
erreicht so ein Ziel nur, wenn ihr die Destination **zugeordnet** ist.
Die Zugangsdaten (Passwort, Token) liegen bei der Plattform, nicht in
der App — bei der Art *Proxy* sieht die App sie nie.

Dieselbe Handlung heißt an der Kommandozeile `oaap destination bind`
(„binden“), im Portal **Zuordnen**.

## Wer was darf

| Was | Wo | Wer |
|---|---|---|
| Destination anlegen (alle Arten, auch `tcp`, Tunnel, interne Ziele) | Portal → Kommunikation → **Destinationen**, oder `oaap destination add` | `server_admin` |
| Destination anlegen, nur `https` auf öffentliche Adressen | Portal → Kommunikation → **Destinationen** | `tenant_admin`, **wenn** der Betreiber es dem Mandanten erlaubt hat |
| Erlaubnis für den Mandanten ein- und ausschalten | Portal → Destinationen mit `?tenant=<mandant>`, Karte „Einstellung des Mandanten“ | `server_admin` |
| Einer App zuordnen und wieder lösen | Portal → Instanzen → `<instanz>` → Reiter **Netz & Adressen**, Karte „Destinationen“ | Verwaltung der Instanz (`tenant_admin`, `server_admin`) |
| Eine Person durchreichen (Principal Propagation, Zertifikat, SAP) | nur `oaap destination add … --auth principal_propagation` und `oaap destination bind … --propagate` | `server_admin` |

Die Kommandozeile `oaap` gibt es nur auf dem Knoten selbst; darum steht
die [CLI-Seite](../cli/generated/destination.md) nur für `server_admin`.
Alles, was eine Mandanten-Verwaltung selbst tun kann, geht über das
Portal und steht hier.

## Voraussetzungen

- Eine laufende App-Instanz im Mandanten, die eine Destination braucht.
  Die App erklärt ihren **Bedarf** im Manifest (etwa `erp` oder
  `ki-gateway`); das Portal zeigt ihn in der Karte „Destinationen“.
- Die Adresse des Ziels und, falls nötig, seine Anmeldung (Token,
  Benutzer und Passwort, oder eine eigene Kopfzeile wie `X-Api-Key`).
- Als `tenant_admin`: die Erlaubnis des Betreibers (Schritt 1).

## Schritt 1: Prüfen, ob du selbst anlegen darfst

Portal → linke Leiste **Kommunikation → Destinationen**.

- Siehst du die Karte **„Destination anlegen“**, darfst du anlegen.
- Steht unten „Anlegen kann eine Destination der Betreiber des Knotens
  (Server-Admin)“, hat der Betreiber es deinem Mandanten nicht erlaubt.
  Dann bittest du ihn, entweder die Destination anzulegen oder dir das
  Anlegen zu erlauben.

**Prüfen:** Die Tabelle „Ziele dieses Mandanten“ zeigt, was es schon
gibt — vielleicht ist die Destination schon da.

## Schritt 2: Die Destination anlegen

In der Karte **„Destination anlegen“**:

1. **Name** — klein, Ziffern, Bindestrich, z. B. `erp-produktiv`. Unter
   diesem Namen ordnest du sie später zu.
2. **Ziel** — `https://erp.beispiel.de` (mit Port und Basispfad, falls
   nötig: `https://erp.beispiel.de:8443/api`).
3. **Anmeldung** — *keine*, *Bearer-Token*, *Benutzer + Passwort* oder
   *eigene Kopfzeile*.
4. Je nach Anmeldung **Benutzer** bzw. **Name der Kopfzeile**.
5. **Geheimnis** — Passwort, Token oder Wert der Kopfzeile.
6. **Anlegen**.

Ein `server_admin` wählt zusätzlich die **Art**: `http` (über das
Gateway, *Proxy*) oder `tcp` (*Übergabe*: Adresse und Zugangsdaten
liegen in der Umgebung der App, etwa für einen Mailserver oder eine
Datenbank). Eine `tenant_admin`-Destination ist immer `http`.

**Prüfen:** Die Destination steht in der Tabelle, Spalte „Zugeordnet“
sagt *nichts*. Das Geheimnis zeigt die Seite nie wieder; ändern geht
über **Geheimnis setzen** in derselben Zeile.

## Schritt 3: Die Destination der App zuordnen

1. Portal → **Instanzen** → die Instanz der App öffnen.
2. Reiter **Netz & Adressen** → Karte **„Destinationen“**.
3. In der Zeile des Bedarfs (z. B. `erp`) die Destination in der
   Auswahl wählen → **Zuordnen**.

Manche Apps nehmen **beliebig viele** Destinationen eines Bedarfs (etwa
ein MCP-Gateway, das mehrere Systeme anspricht). Dann steht dort
„beliebig viele — jede unter ihrem eigenen Namen“, und jede weitere
ordnest du mit derselben Auswahl zu.

**Prüfen:** In der Zeile steht jetzt der Name der Destination und ihr
Ziel, in der Spalte „Art“ *Proxy* mit dem Namen der Umgebungsvariable,
unter der die App das Gateway findet — oder *Übergabe*. Auf der Seite
„Destinationen“ nennt die Spalte „Zugeordnet“ die Instanz.

## Schritt 4: In der App benutzen

Wie die App die Destination benutzt, sagt ihre eigene Doku. Beispiele:

- **MCP-Gateway:** Server mit der Adresse `destination:<destination>`
  anlegen (Seite des Gateways → Server).
- **KI-Gateway:** Bezugsquelle mit der Destination anlegen.

**Prüfen:** Der erste Aufruf der App an das Ziel geht durch. Antwortet
das Ziel mit 401/403, stimmen Anmeldung oder Geheimnis nicht (Schritt 2,
**Geheimnis setzen**).

## Lösen und entfernen

- **Lösen:** Instanz → Netz & Adressen → Destinationen → **Lösen** in
  der Zeile des Bedarfs.
- **Entfernen:** Seite Destinationen → „wirklich“ ankreuzen →
  **Entfernen**. Das geht erst, wenn die Destination keiner App mehr
  zugeordnet ist („erst lösen, dann entfernen“).
- Eine `tenant_admin`-Verwaltung ändert und entfernt nur, was sie selbst
  angelegt hat; Destinationen des Betreibers stehen mit „vom Betreiber
  angelegt“ in der Tabelle.

## Wenn es schiefgeht

- **„Destination anlegen“ fehlt.** Der Betreiber hat deinem Mandanten
  das Anlegen nicht erlaubt (Schritt 1).
- **Das Speichern wird abgewiesen, das Ziel zeige auf eine interne
  Adresse.** Eine Mandanten-Verwaltung darf nur `https`-Ziele auf
  öffentlichen Adressen anlegen; der Knoten prüft den Namen beim
  Speichern. Ziele im eigenen Netz legt der Betreiber an (oder über
  den Connector, RFC-0033).
- **Die Auswahl beim Zuordnen ist leer** („Dein Mandant hat keine
  Destination der Art …“). Die App braucht eine andere Art (etwa `tcp`
  für einen Mailserver); die legt der Betreiber an.
- **„fehlt auf diesem Knoten“** in der Zeile der Instanz: Die
  zugeordnete Destination wurde entfernt oder umbenannt. Neu anlegen
  oder eine andere zuordnen.
- **Die App soll als die angemeldete Person ins Zielsystem**, etwa SAP
  mit Zertifikat: Das Portal kann diese Art nicht anlegen. Der
  Betreiber legt sie an der Kommandozeile an; die Seite
  [SAP-Benutzer im Anmeldedienst pflegen](sap-benutzer-im-anmeldedienst.md)
  beschreibt den Teil im Keycloak-Realm.
- **Ein Testsystem (Generalprobe) lässt sich nicht zuordnen.** Absicht:
  eine Generalprobe spricht keine echten Ziele an (RFC-0030).

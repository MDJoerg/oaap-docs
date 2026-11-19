---
id: szenario/mandantenlandschaft-einrichten
title: "Eine Mandantenlandschaft einrichten — Hilfe, MCP-Gateway, KI-Gateway und Chat in der richtigen Reihenfolge"
audience: [tenant_admin, server_admin, support]
applies_from: "0.1.309"
checked_against: "0.1.310"
checked_on: 2026-11-19
lang: de
tags: [mandant, landschaft, reihenfolge, chat, mcp-gateway, ki-gateway, help, keycloak, anmeldedienst, destination, sicht, zugangsprofil, schluessel, assistent, leitfaden]
---
# Eine Mandantenlandschaft einrichten

> Geprüft gegen Referenz **0.1.310** (2026-11-19), Apps: help 0.6,
> MCP-Gateway 0.20, KI-Gateway 0.8, Chat 0.7. Der Weg ist am 18.11.2026
> im Mandanten bec gegangen worden (eine Person klickte, alle Lücken auf
> dem Weg sind seither geschlossen). Platzhalter: `<mandant>`,
> `<chat>`, `<tools>` (MCP-Gateway), `<ki>` (KI-Gateway), `<hilfe>`.

Am Ende fragt eine Person im **Chat** ihres Mandanten, und ein
**Assistent** antwortet mit einem Modell aus dem **KI-Gateway** und mit
Werkzeugen aus dem **MCP-Gateway** — zuerst mit der **Hilfe** (OAAP-Doku
und Doku der Apps). Jeder Werkzeugaufruf läuft als die Person, die
gerade schreibt. Diese Seite sagt, was in welcher Reihenfolge entsteht
und wie die Teile zusammenhängen. Die Einzelheiten stehen in den
verlinkten Anleitungen und in den READMEs der Apps.

## Das Bild

```
Person ── Chat <chat> ──(Destination ki, Schlüssel)──> KI-Gateway <ki> ──> Bezugsquelle (z. B. Anthropic)
              │
              └──(Tür der Plattform, als die Person)──> MCP-Gateway <tools> ──> Hilfe <hilfe> ──(Destination docs-origin)──> oaap-docs
                                                                     └──> weitere Server (z. B. SAP, Jira)
```

- Der Chat erreicht das MCP-Gateway **ohne Destination**, über die Tür
  der Plattform. Er braucht dort eine **Sicht** mit dem Zugang
  „Plattform (Chat)“ und ein **Zugangsprofil** für die Gruppe `@<chat>`.
- Das KI-Gateway erreicht der Chat über die **Destination `ki`**, mit
  einem Schlüssel des KI-Gateways als Geheimnis.
- Die Hilfe holt die OAAP-Doku über die **Destination `docs-origin`**.

## Vorher festlegen

1. **Namen der Instanzen.** Das Zugangsprofil im MCP-Gateway nennt den
   Chat beim Namen (`@<chat>`). Den Namen also vorher wählen, z. B.
   `<mandant>-chat`, `<mandant>-tools`, `<mandant>-ki`, `<mandant>-help`.
2. **Ampel.** Welche Daten dürfen wohin? Grün, Gelb, Rot gelten für die
   Bezugsquellen im KI-Gateway und für die Server im MCP-Gateway. Eine
   neue Quelle ist **rot**, bis jemand sie einstuft; Schlüssel und
   Profile reichen in der Vorgabe nur bis **gelb**. Wer nichts einstuft,
   sieht deshalb später nichts.
3. **Wer klickt.** Alles auf dieser Seite darf die Verwaltung des
   Mandanten (tenant_admin), außer wo „Betreiber“ steht.

## Schritt 0: Mandant und Anmeldedienst

Der Mandant steht, die Verwaltung kann sich anmelden:
[Einen Kunden-Mandanten mit eigenem Anmeldebereich einrichten](kunden-mandant-anlegen.md)
oder in einem Aufruf
[aus einem Profil](mandant-aus-profil-aufbauen.md).

Ein eigener Anmeldedienst (Keycloak-Realm) ist für den Chat **nicht
nötig**. Er wird nötig, sobald sich Personen selbst am MCP-Gateway
anmelden sollen (etwa mit Claude Code, Schritt 6) oder eine App sie als
sie selbst bis in ein SAP-System bringen soll (Schritt 7).

## Schritt 1: Die Hilfe

1. Im Store **help** installieren (`<hilfe>`).
2. Eine Destination **`docs-origin`** anlegen und der Hilfe zuordnen:
   Ziel `https://codeload.github.com/MDJoerg/oaap-docs` (direkt das
   Archiv, nicht `github.com` — die Hilfe folgt keiner Weiterleitung),
   Anmeldung keine. Wie das geht:
   [Destination im Portal anlegen und zuordnen](destination-im-portal.md)
   (Seite der Instanz, Reiter Netz & Adressen, „Zuordnen“).
3. Auf `/admin` der Hilfe „Jetzt holen“. Danach zeigt die Seite die Zahl
   der Dokumente.

Ohne `docs-origin` antwortet nur der Stand, der im Paket lag; die
Startseite der Hilfe sagt das. Eine Person mit Rolle **user** sieht nur
Seiten für Anwender — das ist gewollt.

## Schritt 2: Das MCP-Gateway

1. Im Store **mcp-gateway** installieren (`<tools>`).
2. Die Hilfe als Server: Apps der Plattform erscheinen von selbst als
   Server (Name = Instanz), mit Ampel **rot** und in keiner Sicht. Fehlt
   die Hilfe, im Reiter Server „Quellen jetzt einlesen“. Danach
   „Katalog lesen“, dann die **Ampel** des Servers setzen (z. B. gelb).
3. Reiter Sichten, „+ Sicht anlegen“, z. B. `hilfe`. Bei **Zugänge**
   „Plattform (Chat)“ wählen. Mit „Zuordnen“ die Werkzeuge der Hilfe
   ankreuzen (Wirkungsklasse lesen).
4. Reiter Schlüssel & Profile, „+ Schlüssel ausstellen oder
   Zugangsprofil anlegen“: ein **Zugangsprofil** mit der Gruppe
   **`@<chat>`**, den Sichten `hilfe` und einer Obergrenze, die die
   Ampel des Servers einschließt. `*` meint angemeldete Personen, nicht
   Chats — für den Chat ist es immer `@<chat>`.

Ein Schlüssel (`MCPGW_MASTER_KEY`) ist erst nötig, wenn ein Server eigene
Zugangsdaten bekommt (Portal, Seite der Instanz, Konfiguration,
„erzeugen“).

## Schritt 3: Das KI-Gateway

1. Im Store **ai-gateway** installieren (`<ki>`). Auf der Seite der
   Instanz unter Konfiguration `AIGW_MASTER_KEY` „erzeugen“ — ohne ihn
   speichert das Gateway keine Zugangsdaten.
2. Reiter Bezugsquellen, „Bezugsquelle anlegen“: Name, Adresse bis
   `/v1` (Anthropic: `https://api.anthropic.com/v1`), **Ampel**,
   Zugangsdaten. „testen“.
3. Reiter Modelle: „Modellnamen aus einer Bezugsquelle anlegen“,
   „Modelle abrufen“, die gewünschten anhaken, „Angehakte anlegen“. Je
   Modellname „Test“.
4. Reiter Schlüssel, „Schlüssel ausstellen“, z. B. Bezeichnung `<chat>`:
   die Modellnamen, die der Chat benutzen darf, und die Obergrenze
   (Vorgabe bis gelb). Das Geheimnis erscheint **genau einmal** —
   gleich in Schritt 4 verwenden.

Warnt die Seite „erreicht diese Modellnamen nie“, liegt die Bezugsquelle
über der Obergrenze des Schlüssels: Obergrenze heben oder die Namen
weglassen. Weitere Modellnamen später mit „Modellnamen ändern“ — das
Geheimnis bleibt.

## Schritt 4: Der Chat

1. Im Store **chat** installieren, unter dem Namen aus „Vorher
   festlegen“ (`<chat>`).
2. Destination **`ki`** anlegen und dem Chat zuordnen: Ziel die Adresse
   des KI-Gateways bis `/v1` (`https://<ki-adresse>/v1`), Anmeldung
   **Bearer-Token**, Geheimnis = der Schlüssel aus Schritt 3.
3. Rollen im Mandanten (Portal „Rollen & Rechte“ oder `oaap authz`):
   aus den Vorlagen `assistant_user` (benutzen) und `assistant_keyuser`
   (pflegen) des Chats Rollen bauen und Personen mit dem Team als
   Kontext zuordnen. Die Befehle stehen im README des Chats; Hintergrund:
   [Fachliche Rollen einrichten](fachliche-rollen-einrichten.md).
4. Einen Assistenten anlegen („Neuer Assistent“): Sicht `hilfe`,
   Gateway `<tools>`, Modellname aus der Liste (sie zeigt nur, was der
   Schlüssel erreicht). Sichtbar für den Mandanten darf ihn nur die
   Verwaltung machen. Alternativ fest über `CHAT_ASSISTANT` in der
   Konfiguration (siehe README des Chats).
5. Menü ⋯, **„Einrichtung prüfen“**. Die Prüfung geht der Reihe nach
   Client-Schlüssel, Gateway, Sicht, `ki` und Modellname durch und nennt
   bei jedem Fehler den nächsten Schritt.

## Schritt 5: Als Person ausprobieren

Mit einer Person, die nicht Verwaltung ist, im Chat fragen, z. B. „Wie
lege ich eine Destination an?“. Die Antwort soll eine Seite der Hilfe als
Quelle nennen. Im MCP-Gateway, Reiter Aufrufe & Prüfspur, steht der
Aufruf mit der Person und dem Chat.

## Schritt 6 (bei Bedarf): Personen melden sich selbst am MCP-Gateway an

Für Claude Code oder andere MCP-Clients: auf der Seite der Instanz
`<tools>`, Karte **MCP** (erste Karte im Reiter Überblick), „Anmeldung
einrichten“. Die Felder `MCPGW_*` in der Konfiguration dabei leer lassen.
Die Sicht braucht dann zusätzlich den Zugang „Anmeldung“, das Profil eine
Gruppe des Anmeldedienstes oder `*`. Anwenderseite:
[Meine Werkzeuge im MCP-Gateway](../anwender/mcp-gateway-meine-werkzeuge.md).

## Schritt 7 (bei Bedarf): Werkzeuge eines SAP-Systems als die Person

1. [SAP-Benutzer im Anmeldedienst pflegen](sap-benutzer-im-anmeldedienst.md)
   (Verwaltung des Mandanten, Keycloak).
2. [Ein SAP-System für die Anmeldung als Person vorbereiten](sap-fuer-anmeldung-als-person.md)
   (Destination im Portal mit Karte „Person durchreichen“, seit 0.1.311;
   SAP-Basis richtet STRUST, CERTRULE und RZ10 ein). Beim Zuordnen an
   das MCP-Gateway „trägt die angemeldete Person“ ankreuzen.
3. Im MCP-Gateway einen Server mit Adresse `destination:<name>/<pfad>`
   und Zugang `propagate` (Verfahren P), eine eigene Sicht (zuerst nur lesen), die Sicht
   ins Profil `@<chat>`; im Chat einen Assistenten für diese Sicht.

## Wenn es schiefgeht

- **Der Chat meldet „Keine Destination ki zugeordnet“.** Schritt 4.2.
- **400 vom KI-Gateway, Modell nicht erlaubt.** Der Modellname des
  Assistenten steht nicht im Schlüssel: im KI-Gateway „Modellnamen
  ändern“.
- **Der Assistent sieht keine Werkzeuge.** Der Reihe nach: Sicht hat den
  Zugang „Plattform (Chat)“? Profil nennt `@<chat>` (genau der
  Instanzname) und die Sicht? Ampel des Servers nicht über der
  Obergrenze des Profils? „Einrichtung prüfen“ im Chat nennt die Stelle.
- **Einzelne Werkzeuge fehlen nach einem Update einer App.** Hat sich die
  Beschreibung eines Werkzeugs geändert, sperrt das MCP-Gateway es in
  jeder Sicht, bis jemand auf der Seite der Sicht die neue Fassung
  bestätigt (alt und neu stehen nebeneinander).
- **Die Hilfe findet nichts.** Startseite der Hilfe lesen: fehlt
  `docs-origin`, steht es dort. Als Person mit Rolle user gibt es nur die
  Anwenderseiten.
- **Eine Sicht wurde umbenannt, ein Assistent geht nicht mehr.** Profile
  nimmt das Umbenennen mit, Assistenten im Chat nicht: dort die Sicht neu
  wählen.

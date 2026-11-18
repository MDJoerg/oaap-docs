---
id: anwender/mcp-gateway-meine-werkzeuge
title: "Meine Werkzeuge im MCP-Gateway: eigene Aufrufe, Fehler verstehen, eigenen Zugang hinterlegen"
audience: [user, keyuser, admin, partner, tenant_admin, server_admin, support]
applies_from: "0.1.307"
checked_against: "0.1.307"
checked_on: 2026-11-18
lang: de
tags: [mcp-gateway, werkzeuge, me, meine-aufrufe, zugang, token, api-token, jira, atlassian, chat, assistent, fehler, abgelehnt, anwender]
---
# Meine Werkzeuge im MCP-Gateway

> Geprüft gegen Referenz **0.1.307** und MCP-Gateway **0.18.1**
> (2026-11-18), im Mandanten bec auf oaapx01: Seite `/me` als Person,
> Zugang für einen Jira-Server (Atlassian Cloud) hinterlegt, Aufrufe aus
> dem Chat. Spezifikation: `oaap.ai.mcp-gateway` §1a, §1b, §3.12,
> RFC-0095. Platzhalter: `<gateway>` für die Adresse des Gateways.

## Wofür das MCP-Gateway da ist

Wenn ein **Assistent im Chat** etwas nachschlägt — in der Hilfe, in
SAP, in Jira —, ruft er **Werkzeuge** auf. Diese Werkzeuge stellt das
**MCP-Gateway** bereit. Es prüft bei jedem Aufruf, ob du das darfst,
und schreibt eine Zeile ins Protokoll: wer, wann, welches Werkzeug, ob
es geklappt hat. **Was** gefragt und geantwortet wurde, speichert es
nicht.

Deine eigene Seite dort heißt **„Meine Werkzeuge“** (`/me`). Du
erreichst sie über die Kachel des Gateways im Portal.

## Meine Aufrufe: was ist passiert?

Die Karte **„Meine Aufrufe“** zeigt deine Aufrufe der letzten 30 Tage
— aus dem Chat und, wenn eure Plattform das unterstützt, auch aus
Programmen mit eigener Anmeldung (etwa Claude Code).

- **Nur Probleme zeigen / Alle Aufrufe zeigen** schaltet zwischen den
  fehlgeschlagenen und allen Aufrufen.
- Du kannst nach **Sicht** (Werkzeugsammlung eines Assistenten) und
  nach **Tag** filtern.
- Jeder Fehler steht **in Worten** da: was passiert ist, **wer**
  abgelehnt hat und was du tun kannst.

### Wer hat abgelehnt?

| Steht dort | Bedeutet | Was hilft |
|---|---|---|
| **das Gateway** | Die Verwaltung des Gateways hat das Werkzeug nicht für dich freigegeben, es ist gesperrt oder eine Grenze ist erreicht. | Die Verwaltung des Gateways fragen; Zeit und Sicht nennen. |
| **die Plattform** | Deine Anmeldung oder deine Rollen reichen für diesen Weg nicht. | Neu anmelden; sonst die Verwaltung des Mandanten fragen. |
| **die Destination oder das Zielsystem** | Das Zielsystem (etwa SAP) kennt dich nicht oder lässt dich nicht. | Die Verwaltung des Mandanten fragen. |
| **der Server** | Der Dienst hinter dem Werkzeug hat abgelehnt — oft weil dein eigener Zugang abgelaufen ist. | Zugang erneuern (unten). |

**Werkzeugfehler** heißt: Der Dienst hat geantwortet, aber mit einer
Fehlermeldung. Die genaue Meldung siehst du im Chat; das Gateway
speichert sie nicht.

## Meine Zugangsdaten: ein Werkzeug braucht deinen eigenen Zugang

Manche Dienste kennen dich nur mit **deinem eigenen** Zugang, etwa
einem persönlichen API-Token (Jira, Confluence, GitHub). Für sie zeigt
`/me` die Karte **„Meine Zugangsdaten“**.

### Zugang hinterlegen

1. Die Zeile des Servers lesen: Dort steht, **wo** du den Zugang
   bekommst und **welche Rechte** er braucht, oft mit dem Link „Wo du
   ihn bekommst“.
2. Den Token beim Dienst erzeugen. Eine kurze Laufzeit genügt; du
   kannst ihn hier jederzeit ersetzen.
3. Den Token in das Feld eintragen. Verlangt der Server **Benutzer bzw.
   E-Mail und Token** (etwa Atlassian Cloud), gibt es zwei Felder.
4. **Speichern**.

**Prüfen:** In der Zeile steht **„hinterlegt am …“**, nach dem ersten
Aufruf auch „zuletzt benutzt …“.

Was mit deinem Zugang passiert:

- Das Gateway hält ihn **verschlüsselt** und schickt ihn **nur bei
  deinen Aufrufen** an genau diesen Server.
- Es zeigt ihn **nie wieder an** — dir nicht und der Verwaltung nicht.
  Die Verwaltung sieht nur, dass es ihn gibt, und kann ihn löschen.
- Andere Personen bekommen deinen Zugang nie.

### Zugang erneuern oder löschen

- **Ersetzen:** neuen Token eintragen → **Ersetzen**.
- **Löschen:** **Löschen** in der Zeile. Danach kann der Assistent die
  Werkzeuge dieses Servers für dich nicht mehr benutzen.
- Steht **„vom Server abgelehnt – erneuern“**, hat der Dienst deinen
  Zugang beim letzten Aufruf zurückgewiesen (abgelaufen, widerrufen,
  zu wenige Rechte). Neuen Token erzeugen und ersetzen.

### Die erste Werkzeugliste lesen

Ist ein Server ganz neu und hat noch niemand seine Werkzeuge gelesen,
steht nach dem Hinterlegen ein Knopf **„Werkzeugliste für die
Verwaltung lesen“** da. Er holt die Liste mit deinem Zugang, damit die
Verwaltung die Werkzeuge freigeben kann. Benutzen kannst du sie erst
nach der Freigabe.

## Im Chat: „Werkzeuge noch nicht eingerichtet“

Fehlt dir für einen Assistenten noch ein eigener Zugang, zeigt seine
Karte im Chat **„n Werkzeuge noch nicht eingerichtet – einrichten“**.
Der Link führt auf `/me`. Nach dem Hinterlegen verschwindet der
Hinweis, sobald du die Übersicht der Assistenten wieder öffnest; neu
anmelden musst du dich nicht. Auch **„Einrichtung
prüfen“** am Assistenten nennt, was fehlt.

## Wenn es schiefgeht

- **„Für diesen Server hast du noch keinen Zugang hinterlegt.“** Zugang
  auf `/me` eintragen (oben).
- **„… öffne die Seite einmal über die Plattform …“** — du rufst aus
  einem Programm mit eigener Anmeldung (etwa Claude Code). Öffne `/me`
  einmal über die Kachel im Portal; danach weiß das Gateway, dass beide
  Anmeldungen du bist.
- **Der Dienst lehnt ab, obwohl der Token stimmt.** Oft fehlen dem
  Token Rechte, oder der Dienst erlaubt Zugriffe per Token für eure
  Organisation nicht. Ein Beispiel ist Atlassian Cloud mit der Meldung
  „You don't have permission to connect via API token“: Das schaltet
  der Organisations-Admin von Atlassian frei, nicht OAAP.
- **Du siehst die Karte „Meine Zugangsdaten“ nicht.** Kein Server
  dieses Gateways braucht einen eigenen Zugang.
- **Ein Aufruf fehlt in der Liste.** Aufrufe mit einem API-Schlüssel
  (Programme ohne Person) stehen nie dort, und die Liste reicht 30 Tage
  zurück.

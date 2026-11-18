---
id: anwender/erste-schritte
title: "Erste Schritte: anmelden, Apps öffnen, Profil und Passwort"
audience: [user, keyuser, admin, guest, partner, tenant_admin, server_admin, support]
applies_from: "0.1.306"
checked_against: "0.1.307"
checked_on: 2026-11-18
lang: de
tags: [anmelden, login, portal, apps, kachel, profil, passwort, abmelden, anwender, zugriff-verweigert, http-403]
---
# Erste Schritte: anmelden, Apps öffnen, Profil und Passwort

> Geprüft gegen Referenz **0.1.307** (2026-11-18) an der
> Anmeldeseite, dem Benutzermenü und der Seite „Apps“ des Portals.
> Diese Seite ist für alle, die mit OAAP **arbeiten** — nicht für die
> Verwaltung. Platzhalter: `<adresse>` für die Adresse eures Portals.

## Was ist das Portal?

Das **Portal** ist die Startseite eurer Plattform. Es zeigt die Apps,
die du benutzen darfst, als **Kacheln** — etwa einen Chat, eine Hilfe,
Werkzeuge eures Betriebs. Welche Kacheln du siehst, hängt von deinen
**Rollen** ab, die die Verwaltung vergibt.

## Anmelden

Öffne `https://<adresse>/`. Ohne Anmeldung leitet dich jede Seite zur
**Anmeldeseite**.

- **Mit dem Anmeldedienst eures Mandanten:** Gibt es oben einen Knopf
  mit dem Namen eures Anmeldedienstes (oft der Name der Firma oder des
  Vereins), nimm ihn. Du meldest dich dort mit deinem gewohnten Konto
  an und kommst zurück ins Portal.
- **Mit einem Konto dieses Knotens:** Hast du von der Verwaltung einen
  Benutzernamen und ein Passwort bekommen, gib beides ein. Gibt es auch
  den Knopf des Anmeldedienstes, steht das Formular unter „Mit einem
  Konto dieses Knotens anmelden“.

**Prüfen:** Oben rechts steht dein Name, darunter die Kacheln.

Beim ersten Anmelden mit einem ausgegebenen Passwort verlangt das
Portal oft ein **neues Passwort**. Das neue muss sich vom alten
unterscheiden.

## Eine App öffnen

Klick auf eine Kachel. Die App öffnet sich unter ihrer eigenen Adresse;
du bleibst angemeldet.

Eine Kachel führt dich direkt auf den Teil der App, den du mit deinen
Rollen benutzen darfst. Ein Beispiel: Beim MCP-Gateway landet eine
Person mit Rolle *user* auf „Meine Werkzeuge“
([eigene Seite](mcp-gateway-meine-werkzeuge.md)), die Verwaltung auf
der Verwaltungsseite.

## Profil, Passwort, Abmelden

Oben rechts auf deinen Namen klicken. Das **Benutzermenü** zeigt deinen
Namen und deine Rollen und hat drei Einträge:

- **Profil** — deinen **Anzeigenamen** ändern (höchstens 80 Zeichen).
  So erscheinst du in Apps, die Namen zeigen.
- **Passwort** — das Passwort deines Kontos auf diesem Knoten ändern.
  Meldest du dich über den Anmeldedienst eures Mandanten an, änderst du
  dein Passwort dort, nicht hier.
- **Abmelden** — beendet deine Sitzung im Portal und in den Apps.

## Wenn es schiefgeht

- **„Anmeldung nicht möglich“ oder das Passwort stimmt nicht.** Bei
  einem Konto dieses Knotens hilft die Verwaltung eures Mandanten (sie
  kann ein neues Passwort ausgeben). Beim Anmeldedienst des Mandanten
  gilt dessen „Passwort vergessen“.
- **Du siehst eine Kachel nicht, die du erwartest.** Dir fehlt die
  Rolle dafür, oder die App ist nur für die Verwaltung. Frag die
  Verwaltung eures Mandanten.
- **Eine Seite antwortet „Zugriff verweigert“ (403).** Du bist
  angemeldet, aber deine Rolle reicht für diese Seite nicht. Über die
  Kachel im Portal kommst du auf den Teil, der für dich gedacht ist.
- **Du wirst immer wieder zur Anmeldung geschickt.** Die Sitzung ist
  abgelaufen, oder der Browser blockiert Cookies für diese Adresse.
  Neu anmelden; bleibt es so, Cookies für `<adresse>` erlauben.
- **Die Plattform hat neue Rollen für dich, die Apps merken es nicht.**
  Einmal abmelden und neu anmelden — Rollen und Angaben aus dem
  Anmeldedienst übernimmt die Plattform bei der Anmeldung.

## Hilfe bekommen

- Hat euer Mandant eine **Hilfe**-Kachel, kannst du dort suchen oder im
  Chat einen Assistenten fragen, der in der Hilfe nachschlägt.
- Fehler in einer App meldest du über den Feedback-Knopf der App, wenn
  sie einen hat, oder bei der Verwaltung eures Mandanten.

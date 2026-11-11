---
title: "Vorgänge im Mandanten — melden, klären, übergeben"
checked_against: "0.1.202"
checked_on: 2026-10-17
lang: de
---
# Vorgänge im Mandanten — melden, klären, übergeben

> Geprüft gegen Referenz **0.1.202** und App `vorgaenge` **0.2.1** (oaap-test und
> oaapx01, 2026-10-17). Grundlage: RFC-0061 Stufen 1 und 2.
> Platzhalter: `<mandant>`, `<bereich>`, `<partner>`.

**Grundgedanke:** Jeder Mandant hat **eine** Instanz `vorgaenge`. Dort landet alles,
was Benutzer melden: über den Feedback-Knopf in jeder App des Mandanten, als
interner Vorgang oder aus dem Backend einer App. Geklärt wird in **Bereichen**.
Ein Vorgang verlässt den Mandanten nie; an einen anderen Mandanten geht nur eine
**freigegebene Kopie** (Übergabe).

## 1. Einrichten (Betreiber und Mandanten-Admin)

```sh
sudo oaap app install https://github.com/MDJoerg/oaap-apps --path apps/vorgaenge \
  --tenant <mandant> --name vorgaenge
```

Oder im Store des Portals. Eine App meldet in den Eingang **ihres Kanals**;
eine Test-App ersatzweise in den Produktions-Eingang. Eine Test-Instanz
(`--channel test`) ist der Eingang **nur für Test-Apps**: Eine Produktions-App
meldet nie in einen Test-Eingang.
Gibt es im Mandanten nur `vorgaenge-test`, zeigt der Knopf in Produktions-Apps
nichts (`/platform/feedback` antwortet 404). So ist es heute bei `hbvp`.

Danach in der App, als Admin des Mandanten:

1. **Bereiche** anlegen, z. B. `mb` „Mannschaft mB“. Den Bereich `eingang` gibt
   es schon; die Admins des Mandanten bearbeiten ihn.
2. Im Portal unter **Rollen & Rechte**: App *Vorgänge*, Vorlage
   *Bearbeiter/in* oder *Clearing*, Kontext = Kennung des Bereichs.
   *Clearing* darf zusätzlich übergeben.

## 2. Melden (jeder Benutzer)

Eine App bindet den Knopf mit einer Zeile ein:

```html
<script src="/platform/feedback.js" defer></script>
```

Der Knopf erscheint nur, wenn der Benutzer **angemeldet** ist und es im Mandanten
einen passenden Eingang gibt. Der Dialog übernimmt das Hell/Dunkel der App.
Mit `data-oaap-object="team:<uuid>"` geht ein Objektbezug mit, z. B. das Spiel,
auf dessen Seite man gerade ist.

Was automatisch mitgeht: App, Instanz und Version (vom Gateway beglaubigt),
Seite, Browser, der letzte JavaScript-Fehler und der letzte gescheiterte
Abruf (ohne Query-Teil). Der Benutzer sieht seine Meldungen in der App unter
„Von mir gemeldet“.

## 3. Klären (Bearbeiter/in)

Status: `neu` → `Klärung` → `in Arbeit` → `beantwortet` → `geschlossen`.
`abgelehnt` verlangt eine Begründung; `wieder offen` geht aus beiden
Endzuständen. Verschieben in einen anderen Bereich lässt den alten Bereich als
Beobachter lesen und kommentieren. Einträge werden nur angehängt; nichts wird
gelöscht.

## 4. Übergeben an einen anderen Mandanten (Clearing)

**Einmal je Partner, auf beiden Seiten** (Admins, Menü *Partner*):

1. Der **Empfänger** legt im Portal unter *Zugänge* einen Maschinenzugang an
   (Rolle `user`, beschränkt auf seine `vorgaenge`-Instanz), gibt den
   Schlüssel dem Absender und trägt den Zugang bei sich als *eingehend* ein,
   mit dem Bereich, in dem Übergaben landen.
2. Der **Absender** trägt Adresse und Schlüssel des Empfängers ein.
3. Für die **Antworten** dasselbe umgekehrt.

**Übergeben:** *Entwurf öffnen* (Betreff, Text, gewählte Kommentare, technische
Angaben ja/nein) → *Vorschau* zeigt genau die Bytes → *Freigeben und senden*.
Der Vorgang steht dann auf `übergeben`, bis der Partner antwortet; dann
`beantwortet`. **Nie mit geht:** die meldende Person, Benutzer-IDs, Rollen,
Namen von Bearbeitenden, nicht gewählte Kommentare.

## 5. Vorgänge aus dem Backend einer App

Erklärt eine App im Manifest `cases: {submit: true}` (Manifest 0.9), bekommt sie
`OAAP_CASES_URL` und `OAAP_CASES_KEY`. Der Schlüssel gilt nur an dieser Tür;
die Plattform erneuert ihn 30 Tage vor Ablauf selbst (mit Neustart des
Containers). Einzelheiten: [README der App](https://github.com/MDJoerg/oaap-apps/tree/main/apps/vorgaenge).

## 6. Der Knoten meldet seinen Neustart (seit Plattform 0.1.222, App 0.3.0)

Plant der Knoten einen Neustart (RFC-0069: ein Kernel wartet und der
Betreiber hat ein Fenster gesetzt, oder der Betreiber plant von Hand), legt
die Plattform im Eingang **jedes** Mandanten mit einem Posteingang einen
Vorgang an: „Neustart des Knotens *name*: 2026-11-08 04:15 CET (Pflege)“,
gemeldet vom „Knoten *name*“, Art „Intern“. Er sagt wann, wie dringend
(Pflege oder kritisch), warum in Worten und welche Schutze ihn halten oder
überstimmt sind. Jede Änderung kommt als Kommentar des Knotens dazu
(„Verschoben auf …: gehalten durch joerg-desk bis 2026-11-13“, „Der Knoten
startet jetzt neu“); nach dem Neustart schließt der Knoten den Vorgang
selbst („Neustart erfolgt …; der Knoten läuft wieder“), eine Absage schließt
ihn mit der Absage.

Zu tun ist nichts. Wer eine Instanz vor einem Pflege-Neustart schützen
will, sagt es dem Betreiber (`sudo oaap node care protect <instanz>
--reason "…"`, siehe [CLI](../cli/README.md)); der Vorgang zeigt danach die
Verschiebung. Der Vorgang trägt keine Kernel-Version; die steht beim
Betreiber in `oaap status`.

## 7. Löschfrist

12 Monate nach Schließen oder Ablehnen entfernt die App die meldende Person aus
dem Vorgang; der Vorgang bleibt. Einstellbar je Mandant:
`VORGAENGE_RETENTION_MONTHS`.

## Wenn etwas hakt

| Beobachtung | Ursache |
| --- | --- |
| Kein Knopf zu sehen | nicht angemeldet; kein `vorgaenge` im Mandanten; Produktions-App, aber nur ein Test-Eingang; Script mit `data-oaap-feedback="api-only"` eingebunden |
| Vorgang taucht nirgends auf | landet in `eingang`; den sehen nur die Admins des Mandanten |
| Bearbeiter/in sieht den Bereich nicht | in „Rollen & Rechte“ fehlt der Kontext oder er ist falsch geschrieben |
| Status `übergeben` nicht wählbar | richtig so: nur eine freigegebene Übergabe setzt ihn |
| Übergabe bleibt im Ausgang | Partner nicht erreichbar oder Schlüssel falsch; die App wiederholt höchstens stündlich |
| Keine Mail bei neuem Vorgang | gibt es noch nicht; der Posteingang ist die Übersicht |
| Der Knoten plant einen Neustart, aber kein Vorgang im Eingang | App älter als 0.3.0 oder Plattform älter als 0.1.222; nur ein Test-Eingang im Mandanten (ein Knoten meldet nur in Produktion); der Eingang schlief — der Vorgang kommt beim nächsten Ereignis des Plans, das Journal des Minutenlaufs sagt warum |

**Noch nicht da:** Benachrichtigungen, Abstimmung über Ideen (§7), Vorlagen
(§6), eine KI-Sitzung im Posteingang (§5.4).

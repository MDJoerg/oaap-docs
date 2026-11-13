---
id: szenario/ki-schluessel-fuer-schulung
title: "KI-Schlüssel auf Zeit für die Teilnehmer einer Schulung"
audience: [admin, server_admin, support]
applies_from: "0.1.277"
checked_against: "0.1.277"
checked_on: 2026-11-13
lang: de
tags: [ki, ki-gateway, schulung, kohorte, schlüssel, api-key, teilnehmer, ablauf, modelle]
---
# KI-Schlüssel auf Zeit für die Teilnehmer einer Schulung

Für eine Schulung braucht jeder Teilnehmer einen eigenen Schlüssel für das
KI-Gateway, und alle Schlüssel sollen mit dem Kurs enden. Das KI-Gateway
(ab 0.6.0) stellt sie in einem Schritt aus: Du fügst die Teilnehmerliste
ein und bekommst dieselbe Liste mit einer Spalte für den Schlüssel zurück.

Der Begriff ist derselbe wie bei den Schulungsservern: Eine **Kohorte** ist
ein Kurs auf Zeit, jeder Teilnehmer hat eine **Kennung** (`01` … `99`). Ein
Schlüssel heißt `<kohorte>-tn-<kennung>`, also `kurs-2026-11-tn-07`, genau
wie der Benutzer auf dem Schulungsserver.

## Voraussetzungen

- KI-Gateway **0.6.0** oder neuer (Store → Instanz aktualisieren).
- Rolle `admin` auf der Gateway-Instanz.
- Mindestens ein Modellname im Gateway (Reiter **Modelle**). Modellnamen
  legst du am schnellsten mit „Modellnamen aus einer Bezugsquelle anlegen“
  an: Quelle wählen, Modelle anhaken, anlegen.

## Schritt 1: Teilnehmerliste vorbereiten

Eine Zeile je Person. Mindestens der Name, mehr braucht es nicht. Spalten
dürfen mit Tab (aus Excel kopiert), Semikolon oder Komma getrennt sein:

```
Name            Nr   E-Mail
Anna Beispiel
Bernd Muster    07
Carla Probe     12   c@example.org
```

- Eine Überschriftenzeile wird erkannt und kommt ergänzt zurück.
- Ohne Nummer zählt das Gateway ab der „ersten Nummer“ (Vorgabe `01`) und
  überspringt vergebene Nummern.
- Weitere Spalten (E-Mail, Firma) werden nur durchgereicht.
- Der Name wird zum **Verantwortlichen** des Schlüssels und steht damit in
  der Auswertung. Wer das nicht möchte, nimmt Kürzel oder nur Nummern.

## Schritt 2: Kohorte anlegen

Im KI-Gateway den Reiter **Kohorten** öffnen und **„Kohorte anlegen oder
ergänzen“** ausfüllen:

1. **Kohorte:** ein Name wie `kurs-2026-11`. Kleinbuchstaben, Ziffern und
   Bindestrich. Am besten derselbe Name wie bei den Schulungsservern.
2. **gültig bis einschließlich:** der letzte Kurstag. Der Schlüssel endet
   um 23:59 Uhr Ortszeit.
3. **Teilnehmer:** die Liste einfügen.
4. Unter **„Für die Auswertung und Grenzen“**, alles optional:
   - **Projekt** (leer = Name der Kohorte);
   - **Kostenstelle** und **Anwendung**;
   - **Budget je Teilnehmer** in Token, damit kein Experiment den Rahmen
     sprengt;
   - **Ampel-Obergrenze** (Vorgabe gelb);
   - nur bestimmte **Modellnamen**.
5. **„Schlüssel erzeugen“**.

**Prüfen:** Oben steht ein grüner Kasten „Kohorte … — n Schlüssel, jetzt
sichern“ mit der Tabelle und einer Spalte **Schlüssel**.

## Schritt 3: Schlüssel sichern und verteilen

Die Schlüssel stehen **nur auf dieser einen Seite**. Gespeichert ist nur
ihre Prüfsumme, nachlesen lässt sich keiner. Sichere sie sofort:

- **„Als CSV herunterladen“**: Semikolon, UTF-8, öffnet sich direkt in
  Excel.
- Oder das Textfeld darunter markieren und kopieren. Es hat das Format der
  Eingabe, aus Excel eingefügt also mit Tabs, und lässt sich direkt zurück
  nach Excel kopieren.

Jeder Teilnehmer trägt in seinem Werkzeug ein:

```
Basis-Adresse : https://<gateway>/v1
API-Key       : sein Schlüssel aus der Tabelle
Modell        : ein Modellname, z. B. chat-default
```

## Während und nach dem Kurs

Im Reiter **Kohorten** steht jede Kohorte mit Zustand („12 von 12
gültig“), Ende, Aufrufen und Token, und mit einem Link in die
**Auswertung** (gefiltert nach Projekt).

- **Ein Teilnehmer hat seinen Schlüssel verloren:** Unter „n Teilnehmer“
  seinen Sitz **widerrufen** und mit einer **abweichenden Kennung** neu
  ausstellen. Eine Kennung wird nie zweimal vergeben, auch nach einem
  Widerruf nicht. Füge also `Bernd Muster;07b` in dieselbe Kohorte ein.
  Oder schreibe `Bernd Muster;07` und hake **„nächste freie nehmen“** an,
  dann nimmt das Gateway `07b` (dann `07c` …) und nennt die neue Kennung
  in der Tabelle.
- **Ein Teilnehmer kommt dazu:** einfach eine weitere Zeile in dieselbe
  Kohorte einfügen. Die nächste freie Nummer wird genommen.
- **Der Kurs dauert länger:** neues Datum und **„verlängern“**. Das gilt
  für alle nicht widerrufenen Schlüssel, auch für schon abgelaufene.
- **Vorzeitig beenden:** „wirklich“ anhaken, **„alle widerrufen“**.

Nach dem Ende antwortet ein Schlüssel wie ein widerrufener mit
„Kein gültiger API-Schlüssel“ (403). Die Verbrauchszahlen der Kohorte
bleiben in der Auswertung erhalten.

## Wenn es schiefgeht

### „Kennung 07 ist schon vergeben“

Die Zeile bekam keinen Schlüssel. Der Grund steht in der Tabelle, mit
einem Vorschlag. Mit abweichender Kennung (`07b`) oder mit „nächste freie
nehmen“ erneut einfügen. Nur diese Zeile einfügen, nicht die ganze Liste,
sonst sind alle anderen Kennungen auch vergeben.

### Die Schlüssel sind weg, bevor ich sie gesichert habe

Sie lassen sich nirgends nachlesen. Kohorte unter „alle widerrufen“
beenden und unter einem neuen Namen neu anlegen, etwa `kurs-2026-11b`.
Oder einzelne Sitze widerrufen und mit „nächste freie nehmen“
nachgenerieren.

### Ein Teilnehmer bekommt 403

- Ist der Kurs zu Ende? Im Reiter Kohorten steht „abgelaufen“. Dann
  verlängern.
- Ist sein Sitz widerrufen? Dann nachgenerieren wie oben.
- Hat er den Schlüssel vollständig kopiert? Ein Schlüssel beginnt mit
  `sk-oaap-`.

### Ein Teilnehmer bekommt 400 „kein erlaubter Alias“

Die Kohorte ist auf bestimmte Modellnamen beschränkt, und er hat einen
anderen gewählt. Die Antwort nennt die erlaubten Namen.

## Weiterführend

- Schulungsserver für dieselbe Kohorte: `oaap cohort` (RFC-0046),
  [`oaap cohort`](../cli/generated/cohort.md)
- Modelle aus dem eigenen Netz anbinden:
  [Ein KI-Gateway im Internet nutzt Modelle aus dem eigenen Netz](ki-gateway-ueber-connector.md)
- Spezifikation: `oaap.ai.gateway` 0.5 §2.1 (Schlüssel für eine Kohorte)
  in `oaap-spec`

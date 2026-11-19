---
id: szenario/sap-fuer-anmeldung-als-person
title: "Ein SAP-System für die Anmeldung als Person vorbereiten — Checkliste für die SAP-Basis"
audience: [tenant_admin, server_admin, support]
applies_from: "0.1.305"
checked_against: "0.1.311"
checked_on: 2026-11-19
lang: de
tags: [sap, abap, principal-propagation, zertifikat, strust, certrule, rz10, rz11, icm, sicf, basis, kettentest, http-401]
---
# Ein SAP-System für die Anmeldung als Person vorbereiten

> Geprüft gegen Referenz **0.1.311** (2026-11-19). Der Weg ist am
> 27.10. und 18.11.2026 an einem SAP-ABAP-Testsystem gegangen worden
> (Mandant bec, Verfahren P des MCP-Gateways). Spezifikation:
> `oaap.net.destinations` (Principal Propagation), RFC-0066.
> Platzhalter: `<mandant>` (OAAP-Mandant), `<host>:<port>`,
> `<sap-mandant>` (SAP-Mandant, z. B. 001), `MUSTER`.

Eine App soll ein SAP-System **als die angemeldete Person** aufrufen:
SAP sieht den SAP-Benutzer der Person, mit ihren Berechtigungen, ohne
Passwort. Die Plattform stellt dafür bei jedem Aufruf ein kurzlebiges
Client-Zertifikat aus (Vorgabe 10 Minuten). Das SAP-System muss diesem
Zertifikat vertrauen und es einem Benutzer zuordnen. Diese Seite ist die
Checkliste für die **SAP-Basis**; die Plattformseite steht in
[SAP-Benutzer im Anmeldedienst pflegen](sap-benutzer-im-anmeldedienst.md)
(woher die Plattform den SAP-Benutzer kennt).

## Was die Plattform schickt

- Jeder OAAP-Mandant hat **eine eigene Zertifizierungsstelle** (CA),
  drei Jahre gültig. Ihr Schlüssel verlässt den Knoten nie.
- Jedes Zertifikat hat den Inhaber `CN=<SAP-Benutzer>, OU=<mandant>,
  O=OAAP`. `OU` und `O` schreibt die Plattform aus dem Mandanten der
  Destination, nie aus der App oder der Person. Darauf filtert die Regel
  in SAP: das ist die Grenze zwischen den Mandanten im SAP-System.
- Nur Client-Authentifizierung, wenige Minuten gültig, jede Ausgabe steht
  in der Prüfspur der Plattform (Zeit, Destination, Instanz, Person,
  SAP-Name, Seriennummer).

## Wer macht was

| Schritt | Wo | Wer |
|---|---|---|
| Destination anlegen, Server pinnen | Portal (Destinationen) oder `oaap destination add` | Betreiber, oder Verwaltung des Mandanten mit Erlaubnis |
| CA und Musterzertifikat ausgeben | Portal (Destinationen) oder `oaap destination ca` | Betreiber oder Verwaltung des Mandanten |
| CA vertrauen, Regel anlegen, Profilparameter | SAP: STRUST, CERTRULE, RZ11 **und RZ10** | SAP-Basis |
| SAP-Benutzer der Personen eintragen | Anmeldedienst (Keycloak) | Verwaltung des Mandanten |
| Kettentest | Plattform und SAP | Betreiber und SAP-Basis zusammen |

## Voraussetzung: TLS endet beim SAP-System

Das Zertifikat muss bis zum ICM des SAP-Systems kommen. Steht ein
Lastverteiler oder ein Proxy davor, der TLS beendet, geht dieser Weg
nicht. Prüfen, ohne etwas zu ändern:

```sh
openssl s_client -connect <host>:<port> </dev/null 2>/dev/null | grep -A3 "Acceptable client certificate CA names"
```

- Erscheint eine Liste mit Namen von SAP-Zertifikaten, fragt der ICM
  nach einem Client-Zertifikat: der Weg ist offen.
- Fehlt die Liste, oder ist das Serverzertifikat kein SAP-Zertifikat,
  endet TLS vorher. Dann mit dem Netzwerkteam klären, bevor es weitergeht.

Der Profilparameter `icm/HTTPS/verify_client` steht im Auslieferungszustand
auf **1** (Zertifikat erfragen, nicht verlangen). So lassen: mit 2 müsste
jeder Aufrufer ein Zertifikat haben.

## Schritt 1: Destination anlegen und den Server pinnen

**Im Portal** (seit 0.1.311): Seite Destinationen, Karte „Destination mit
Person durchreichen (Zertifikat)“. Name und Ziel eintragen, „1. Zertifikat
des Ziels lesen“ — das speichert nichts und zeigt Fingerabdruck, Inhaber,
Aussteller und Ablauf. Die SAP-Basis vergleicht den Fingerabdruck mit dem
Zertifikat des SSL-Servers in STRUST. Stimmt er, das Kreuz „verglichen“
setzen und „2. Anlegen und Zertifikat pinnen“. Zeigt das Ziel inzwischen
ein anderes Zertifikat, wird nichts angelegt. Die Verwaltung des Mandanten
darf das, wenn der Betreiber ihr das Anlegen von Destinationen erlaubt hat;
das Ziel muss dann im Internet liegen.

**An der Kommandozeile** (Betreiber):

```sh
sudo oaap destination add <name> --tenant <mandant> \
     --target https://<host>:<port> --auth principal_propagation
```

Der erste Versuch zeigt den **Fingerabdruck** (SHA-256) des
Serverzertifikats. Die SAP-Basis vergleicht ihn mit dem Zertifikat des
SSL-Servers in STRUST. Stimmt er, wird gepinnt:

```sh
sudo oaap destination add <name> --tenant <mandant> \
     --target https://<host>:<port> --auth principal_propagation \
     --accept-sha256 <fingerabdruck>
```

Gepinnt heißt: die Plattform redet nur mit genau diesem Server, auch wenn
ein anderer ein öffentlich gültiges Zertifikat für denselben Namen hätte.
Ändert die Basis das Serverzertifikat, muss neu gepinnt werden.

## Schritt 2 (SAP-Basis): Der CA des Mandanten vertrauen

1. Das Zertifikat der CA holen (nur der öffentliche Teil): im Portal,
   Seite Destinationen, „Zertifizierungsstelle laden“ (sobald der Mandant
   eine solche Destination hat), oder der Betreiber mit
   `sudo oaap destination ca --tenant <mandant> > oaap-<mandant>-ca.cer`
2. In **STRUST** das PSE **SSL-Server Standard** öffnen, das Zertifikat
   in die **Zertifikatsliste** importieren, sichern.

Ein Neustart des ICM ist dafür nicht nötig: am Testsystem stand die CA
wenige Minuten nach dem Sichern in der Liste der angenommenen
Aussteller.

## Schritt 3 (SAP-Basis): Die Regel vom Zertifikat auf den Benutzer

CERTRULE bindet jede Regel an den Aussteller eines **Musterzertifikats**.
Darum braucht es ein Muster genau dieser CA:

```sh
sudo oaap destination ca --tenant <mandant> --sample MUSTER > muster.cer
```

Oder im Portal: Seite Destinationen, „Musterzertifikat laden“.

Das Muster ist eine Stunde gültig und hat keinen privaten Schlüssel.
In **CERTRULE**:

1. Das Muster hochladen.
2. Regel anlegen: Zertifikatseintrag **Subjekt**, Attribut **CN**,
   Anmelden als **Benutzername**.
3. **Inhaberfilter `OU,O`** setzen: die Regel greift nur für
   Zertifikate mit genau diesem `OU` (dem OAAP-Mandanten) und `O=OAAP`.
4. Sichern.

**Regel eng fassen.** Wer den Knoten betreibt, kann für jeden Benutzer
ein Zertifikat ausstellen, den die Regel abdeckt. Für ein Demosystem
reicht „alle CN unter diesem OU“. Für ein Kundensystem: die Regel auf
die Benutzer beschränken, die wirklich über die Plattform kommen, und
**keine Benutzer mit SAP_ALL** oder vergleichbaren Rechten abdecken.

## Schritt 4 (SAP-Basis): Regelbasierte Zuordnung einschalten — dauerhaft

Der Profilparameter `login/certificate_mapping_rulebased` steht im
Auslieferungszustand auf **0**. Ohne 1 wertet SAP die Regel aus Schritt 3
nicht aus.

- In **RZ11** auf `1` setzen: wirkt sofort auf allen Servern, ohne
  Neustart. **Aber nur bis zum nächsten Neustart des Systems.**
- **Zusätzlich in RZ10** im Default-Profil `login/certificate_mapping_rulebased = 1`
  eintragen. Erst damit gilt der Wert auch nach einem Neustart.

Das ist der häufigste Grund, warum es nach einem Wochenende nicht mehr
geht: am Testsystem war der Parameter nur in RZ11 gesetzt, nach einem
Neustart stand er wieder auf 0, und SAP antwortete jedem Aufruf mit 401.

## Schritt 5 (SAP-Basis): Der Dienst nimmt das Zertifikat an

Der ICF-Dienst, den die App aufruft, muss die Anmeldung per Zertifikat
zulassen. In **SICF** beim Dienst, Reiter Anmeldedaten: Verfahren
**Standard** schließt das Client-Zertifikat ein. Ein Dienst mit fest
eingetragenem Benutzer oder nur Basic-Anmeldung meldet die Person nicht
an.

## Schritt 6: Kettentest — und nach jedem Neustart wieder

Ein Aufruf, der den angemeldeten SAP-Benutzer zurückgibt, zeigt die
ganze Kette: Anmeldedienst → Plattform → Zertifikat → STRUST → CERTRULE
→ Benutzer.

- **Mit einer Person, über die Plattform:** eine App, der die
  Destination mit „trägt die angemeldete Person“ (`--propagate`) zugeordnet ist, ruft
  `/sap/bc/ui2/start_up?sap-client=<sap-mandant>` auf. Die SSO-Sonde aus
  `oaap-lab/sso-probe` tut genau das und zeigt den SAP-Benutzer. Im Chat
  geht es mit einem Assistenten, dessen Sicht ein Werkzeug „wer bin ich“
  des SAP-Systems enthält.
- **Erwartet:** `200` und der SAP-Benutzer der Person. Eine zweite
  Person ergibt ihren eigenen Benutzer. Eine Person ohne `sap_user`
  bekommt eine lesbare Ablehnung der Plattform, nicht von SAP.

Den Test nach jeder Wartung oder jedem Neustart des SAP-Systems
wiederholen. Er bemerkt einen verlorenen Profilparameter, bevor es die
Personen tun.

## Wenn es schiefgeht

- **TLS-Abbruch, „certificate unknown“.** Der ICM kennt die CA nicht:
  Schritt 2 fehlt, das Zertifikat liegt im falschen PSE, oder es ist die
  CA eines anderen Mandanten.
- **401 mit Anmeldeaufforderung (Basic).** Die Verbindung steht, SAP
  ordnet das Zertifikat aber keinem Benutzer zu. Der Reihe nach:
  1. `login/certificate_mapping_rulebased` in RZ11 ansehen. Steht er auf
     0, war das System neu gestartet und RZ10 fehlt (Schritt 4).
  2. Greift eine Regel in CERTRULE? Der Inhaberfilter muss zu `OU=<mandant>,
     O=OAAP` passen, und die Regel muss aus einem Muster **dieser** CA
     stammen.
  3. Gibt es den Benutzer in diesem SAP-Mandanten, und ist er nicht
     gesperrt?
- **Es lief, und seit einem Neustart kommt 401.** Fast immer Schritt 4:
  der Wert stand nur in RZ11.
- **Die Plattform lehnt ab, bevor SAP gefragt wird.** Dann liegt es nicht
  an SAP: die Person hat keinen `sap_user`, hat sich seit dem Eintragen
  nicht neu angemeldet, oder die Zuordnung der Destination trägt die
  Person nicht (Instanzseite: „Person durchreichen erlauben“, oder `--propagate`). Siehe
  [SAP-Benutzer im Anmeldedienst pflegen](sap-benutzer-im-anmeldedienst.md).
- **Fingerabdruck stimmt nicht mehr.** Das Serverzertifikat in STRUST
  wurde erneuert. Neu vergleichen und pinnen (Schritt 1).

## Wenn die CA abläuft

Die CA eines Mandanten gilt drei Jahre. Vorgesehen ist (RFC-0066 §5):
eine neue CA neben die alte stellen, beide für eine Übergangszeit in
STRUST, dann die alte entfernen; die Regel in CERTRULE braucht ein Muster
der neuen CA. Einen Befehl für den Wechsel hat `oaap destination` noch
nicht (Stand 0.1.310); die erste CA läuft frühestens im Oktober 2029 ab.

---
id: szenario/sap-benutzer-im-anmeldedienst
title: "SAP-Benutzer im Anmeldedienst (Keycloak-Realm) pflegen — für die Anmeldung als Person bis ins SAP"
audience: [tenant_admin, server_admin, support]
applies_from: "0.1.305"
checked_against: "0.1.307"
checked_on: 2026-11-18
lang: de
tags: [sap, keycloak, realm, sap_user, attribut, client-scope, mapper, principal-propagation, zertifikat, sso, evaluate]
---
# SAP-Benutzer im Anmeldedienst (Keycloak-Realm) pflegen

> Geprüft gegen Referenz **0.1.307** (2026-11-18). Der Weg ist am
> 18.11.2026 im Mandanten bec mit Keycloak 26 gegangen worden; danach
> rief der Chat ein SAP-System als die Person auf (Verfahren P,
> Zertifikat für den SAP-Benutzer). Spezifikation: `oaap.net.destinations`
> (Principal Propagation), RFC-0066, RFC-0091. Platzhalter: `<realm>`,
> `<oaap-client>`, `<person>`, `MUSTERMANN`.

Soll eine App eine angemeldete Person **als sie selbst** in ein
SAP-System bringen — der Chat fragt SAP, und SAP sieht den SAP-Benutzer
der Person —, braucht die Plattform zu jeder Person ihren
**SAP-Benutzer**. Er steht als Attribut `sap_user` im Anmeldedienst des
Mandanten (Keycloak-Realm). Die Plattform stellt daraus bei jedem Aufruf
ein kurzlebiges Zertifikat für genau diesen Benutzer aus.

**Wichtig:** Die Plattform nimmt den Wert nur, wenn die Person ihn
**nicht selbst ändern** kann. Sonst könnte sich jeder in SAP als jemand
anderes ausgeben.

## Wer stellt was ein

| Was | Wo | Wer |
|---|---|---|
| Attribut, Client Scope, Mapper (Schritte 1–3, einmal je Realm) | Keycloak-Konsole, Realm des Mandanten | Verwaltung des Realms (oft der Betreiber) |
| SAP-Benutzer je Person eintragen (Schritt 4) | Keycloak-Konsole → Users | Verwaltung des Realms |
| Destination mit Principal Propagation, Zuordnung mit „trägt die Person“ | `oaap destination add/bind` | `server_admin` |
| Zertifikat der Plattform-CA vertrauen, Regel für den Benutzer | SAP: STRUST, CERTRULE (Profilparameter dauerhaft in RZ10) | SAP-Basis |

## Voraussetzungen

- Der Mandant hat einen Anmeldedienst (Keycloak-Realm), und OAAP meldet
  über ihn an. Den Namen des OAAP-Clients im Realm (`<oaap-client>`,
  meist `oaap-<adresse des knotens>`) zeigt die Keycloak-Konsole unter
  **Clients**.
- Du kannst dich an der Keycloak-Konsole anmelden und wählst oben links
  den Realm `<realm>`.
- Der SAP-Benutzer existiert im Zielsystem (höchstens 12 Zeichen).

## Schritt 1: Das Attribut `sap_user` anlegen

1. **Realm settings** → Reiter **User profile** → **Create attribute**.
2. **Attribute [Name]:** `sap_user`. **Display name:** `SAP-Benutzer`.
3. **Required:** aus. **Multivalued:** aus.
4. **Permissions:**
   - *Who can edit:* nur **Admin** — bei *User* **kein** Haken. Das ist
     der entscheidende Punkt.
   - *Who can view:* **Admin**; *User* darf angehakt sein (die Person
     sieht ihren SAP-Benutzer, ändert ihn aber nicht).
5. Optional unter **Validations:** `length` mit Maximum 12 und `pattern`
   mit `^[A-Z0-9_]+$`.
6. **Create**.

**Prüfen:** Das Attribut steht in der Liste des User profile, *edit*
nur Admin.

## Schritt 2: Den Client Scope `sap` mit Mapper anlegen

1. **Client scopes** → **Create client scope**.
2. **Name:** `sap`. **Type:** *Default*. **Protocol:** OpenID Connect.
   *Include in token scope:* an. **Save**.
3. Im neuen Scope Reiter **Mappers** → **Configure a new mapper** →
   **User Attribute**:
   - **Name:** `sap_user`
   - **User Attribute:** `sap_user` (genau so geschrieben)
   - **Token Claim Name:** `sap_user`
   - **Claim JSON Type:** String
   - **Add to ID token**, **Add to access token**, **Add to userinfo:**
     alle drei an
   - **Multivalued:** aus
4. **Save**.

**Prüfen:** Client scopes → `sap` → Mappers zeigt `sap_user` vom Typ
*User Attribute*.

## Schritt 3: Den Scope an den OAAP-Client hängen

1. **Clients** → `<oaap-client>` → Reiter **Client scopes** →
   **Add client scope**.
2. `sap` ankreuzen → **Add** → **Default**.

**Prüfen:** In der Liste des Clients steht `sap` mit *Assigned type*
**Default** — neben dem Scope `<oaap-client>-dedicated`, den Keycloak
selbst anlegt (siehe „Wenn es schiefgeht“).

## Schritt 4: Den SAP-Benutzer bei der Person eintragen

1. **Users** → `<person>` → Reiter **Details**.
2. Im Feld **SAP-Benutzer** den Benutzer eintragen, z. B. `MUSTERMANN`.
3. **Save**.

**Prüfen:** Der Wert steht nach dem Neuladen noch da.

## Schritt 5: Selbst kontrollieren, dann neu anmelden

1. **Clients** → `<oaap-client>` → **Client scopes** → Reiter
   **Evaluate**.
2. Oben unter **Users** die Person wählen, dann rechts **Generated ID
   token** anklicken.
3. Dort muss `"sap_user": "MUSTERMANN"` stehen.
4. Die Person meldet sich in OAAP **einmal ab und wieder an**. Die
   Plattform übernimmt den Wert nur bei der Anmeldung.

**Prüfen:** Der erste Aufruf der App ins SAP geht durch. Fehlt der
Wert, lehnt die Plattform den Aufruf mit 403 ab, bevor etwas zum SAP
geht.

## Was danach noch nötig ist (Betreiber und SAP-Basis)

Diese Schritte sind nicht Sache der Realm-Verwaltung, gehören aber zum
Ganzen:

- **Destination:** Der Betreiber legt sie mit
  `oaap destination add <name> --auth principal_propagation …` an
  (Claim `sap_user` ist die Vorgabe, `--accept-sha256` pinnt das
  Serverzertifikat) und ordnet sie mit `oaap destination bind <instanz>
  <name> --propagate` zu. Das Portal kann diese Art nicht anlegen
  ([Destination im Portal](destination-im-portal.md) beschreibt die
  anderen Arten).
- **Prüfung „nur Admin ändert“:** Die Plattform fragt beim Anlegen über
  den Konnektor des Anmeldedienstes nach, ob nur Administratoren
  `sap_user` ändern dürfen. Steht dort *User* bei *Who can edit*, lehnt
  sie ab.
- **SAP:** die CA der Plattform (`oaap destination ca`) in **STRUST**
  vertrauen, in **CERTRULE** die Regel vom Zertifikat auf den Benutzer,
  und den Profilparameter `login/certificate_mapping_rulebased = 1`
  **dauerhaft in RZ10** setzen. Nur in RZ11 gesetzt ist er nach dem
  nächsten Neustart des SAP-Systems wieder weg, und SAP antwortet 401.

## Wenn es schiefgeht

- **`sap_user` fehlt im Generated ID token.** Drei Stellen prüfen:
  1. Ist bei der Person ein Wert eingetragen (Schritt 4)? Die häufigste
     Ursache.
  2. Hängt `sap` am OAAP-Client mit Typ *Default* (Schritt 3)? **Type
     Default beim Anlegen des Scopes hängt ihn nicht an Clients, die es
     schon gibt** — das muss man von Hand tun.
  3. Ist der Mapper vollständig: *User Attribute* exakt `sap_user`,
     *Add to ID token* an?
- **Evaluate zeigt nur eine Liste, keinen Wert.** Der Reiter *Effective
  protocol mappers* listet die Mapper; den Wert zeigt erst **Generated
  ID token** — mit gewählter Person.
- **Der Mapper landete im falschen Scope.** In der Liste des Clients
  stehen `sap` und `<oaap-client>-dedicated`. Der *dedicated*-Scope
  gehört dem Client selbst; ein Mapper dort wirkt auch, aber nur für
  diesen einen Client. Gemeint ist `sap`. Den *dedicated*-Scope kann man
  nicht entfernen — Keycloak meldet dabei „Cannot read properties of
  undefined“. Den Mapper dort einfach löschen und in `sap` anlegen.
- **Der Anzeigename des Attributs ist grau und heißt
  `${profile.attributes.sap_user}`.** Keycloak 26 trägt beim Anlegen
  einen Übersetzungsschlüssel ein. Für die Funktion egal; ändern lässt er
  sich über das Globus-Symbol neben dem Feld. Bei der Person heißt das
  Feld dann eventuell genau so.
- **Der Wert ist richtig, der Aufruf scheitert trotzdem mit 403 der
  Plattform.** Die Person hat sich seit dem Eintragen nicht neu
  angemeldet (Schritt 5), oder die Zuordnung der Destination trägt die
  Person nicht (`--propagate` fehlt, Betreiber fragen).
- **SAP antwortet 401.** Zertifikat und Benutzer passen auf
  Plattformseite, aber SAP ordnet sie nicht zu: Profilparameter (RZ10),
  STRUST oder CERTRULE prüfen lassen.

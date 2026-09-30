# Einen Kunden-Mandanten mit eigenem Anmeldebereich einrichten

> Geprüft gegen Referenz **0.1.146** (2026-09-30), Keycloak **26.7.4**,
> auf einem Knoten mit Wildcard-DNS (siehe [FAQ: Mehrmandanten-Knoten](../faq/mehrmandanten-knoten.md), F3/F9).
> Platzhalter: `<kürzel>` (Mandant), `<knoten>` (Basisdomain des Knotens),
> `<auth>` (Name der Anmeldedienst-Instanz, hier `auth`).
> Voraussetzung: Der Anmeldedienst läuft und der Konnektor ist eingerichtet
> (`oaap idp check <auth>` ist sauber).

Ergebnis: ein Mandant mit eigener Adresse `<kürzel>.<knoten>`, eigenem Realm,
Anmeldung über das Vereins-/Kundenkonto, einem ersten Verwalter und einer
Verwaltungsmöglichkeit für seine Mitglieder.

## 1. Mandant und Adresse

```sh
sudo oaap tenant create <kürzel> --name "<Klarname des Kunden>"
sudo oaap external set <knoten>          # Behelf (FAQ F12), bis der Fehler behoben ist
sleep 20; curl -sI https://<kürzel>.<knoten>/ | head -3     # 200, 302 oder 303
```

Das Kürzel ist öffentlich (Zertifikatsprotokolle). Bei vertraulichen
Kunden ein Kürzel wählen, das nichts über sie sagt.

## 2. Realm und Client anlegen

```sh
sudo oaap idp provision <auth> --tenant <kürzel> --idp-label "Mit dem Vereinskonto anmelden" --dry-run
sudo oaap idp provision <auth> --tenant <kürzel> --idp-label "Mit dem Vereinskonto anmelden"
sudo oaap idp settings <auth> --tenant <kürzel>       # nur lesen: Selbstregistrierung aus, 2. Faktor aus
```

## 3. Richtlinie für neue Mitglieder

```sh
sudo oaap tenant policy <kürzel> --first-login role --default-role user --self-registration off
sudo oaap tenant policy <kürzel>
```

Mitglieder, die der Kunde im Realm anlegt, bekommen bei der ersten
Anmeldung die Rolle `user`, ohne Freigabe durch den Betreiber. Das setzt
nur der Betreiber, und es ist nur erlaubt, solange die
Selbstregistrierung im Realm aus ist.

## 4. Den ersten Verwalter anlegen (einmal, durch den Betreiber)

1. Keycloak-Konsole (Realm-Wähler → `<kürzel>`) → *Users → Add user*:
   Benutzername, E-Mail, *Email verified* an, Vor- und Nachname setzen;
   Reiter *Credentials* → Passwort, *Temporary* aus.
2. Die Person meldet sich unter `https://<kürzel>.<knoten>/` an
   („Mit dem Vereinskonto anmelden"). Sie erscheint mit der Rolle `user`.
3. Im Portal (als `server_admin`) gibt der Betreiber dem Benutzer die Rolle
   `tenant_admin`. **Das ist der einzige Freigabeschritt, der beim Betreiber
   bleibt**: die Rolle wird nie automatisch vergeben.

Beobachtet: Der Benutzername im Portal kann von dem im Realm abweichen,
wenn der Name auf dem Knoten schon vergeben ist (`name-2`, siehe FAQ F13).

## 5. Verwaltung der Mitglieder durch den Kunden

Bis die Mitglieder-App gebaut ist (RFC-0048), gibt es zwei Möglichkeiten:

- **Der Betreiber legt Mitglieder in der Keycloak-Konsole an.**
- **Ein Mitglied des Kunden bekommt die Realm-Rollen `manage-users` und
  `view-users`** (Konsole → Realm `<kürzel>` → Users → Benutzer →
  *Role mapping* → *Assign role* → *Filter by clients* → `realm-management`).
  Es meldet sich unter `https://<auth>.<knoten>/admin/<kürzel>/console/` an.

Beobachtet für die zweite Möglichkeit: Der Verwalter kommt nur in seinen
Realm, sieht nur *Users* und *Groups*, kann Benutzer anlegen, Passwörter
setzen und Benutzer **löschen**. Das Löschen ist ein Mangel: In OAAP bleibt
der Benutzersatz bestehen (aktiv, ohne Anmeldeweg), siehe Ideenspeicher I-18.
Die Mitglieder-App sperrt nur, sie löscht nie (RFC-0048).

## 6. Mitglieder melden sich an

Ein im Realm angelegtes Mitglied meldet sich unter
`https://<kürzel>.<knoten>/` an und ist ohne Freigabe mit der Rolle `user`
drin. Im Portal sieht es die Reiter, die zu `user` gehören, darunter
„Zwilling" (siehe FAQ F19).

## Prüfliste

- [ ] `oaap tenant list` zeigt den Mandanten
- [ ] `https://<kürzel>.<knoten>/` antwortet mit gültigem Zertifikat
- [ ] `oaap tenant policy <kürzel>` zeigt `role → user`, Selbstregistrierung aus
- [ ] Erster Verwalter hat `tenant_admin` und keine knotenweite Rolle (`oaap user list`)
- [ ] Ein normales Mitglied kommt ohne Freigabe herein

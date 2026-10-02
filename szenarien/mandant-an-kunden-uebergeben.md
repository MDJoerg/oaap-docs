# Einen Kunden-Mandanten an den Kunden übergeben — Checkliste

> Geprüft gegen Referenz **0.1.150** (2026-10-01). Gilt nach
> [Kunden-Mandanten einrichten](kunden-mandant-anlegen.md) und dem Anlegen der
> Anwendungen des Kunden. Platzhalter: `<kürzel>` (Mandant), `<knoten>`
> (Basisdomain), `<auth>` (Anmeldedienst-Instanz), `<verwalter>` (der erste
> Benutzer des Kunden), `<web-test>` (Test-Instanz einer vom Kunden
> entwickelten Anwendung, CLI-Schlüssel `<kürzel>-<name>`).
> Der Betreiber führt die Schritte unter A bis C aus, der Kunde die unter D.

## A. Technische Prüfung vor der Übergabe (Betreiber)

- [ ] **Mandant und Adresse:** `sudo oaap tenant list` zeigt `<kürzel>`;
      `https://<kürzel>.<knoten>/` antwortet mit gültigem Zertifikat. Zeigt der
      Browser `SSL_ERROR_INTERNAL_ERROR_ALERT`: `sudo oaap external set <knoten>`
      (FAQ F12).
- [ ] **Instanzen laufen:** `sudo oaap app list` zeigt jede Instanz des Mandanten
      mit der erwarteten Version und dem erwarteten Kanal. Jede Adresse
      (`https://<name>.<kürzel>.<knoten>/`) im Browser einmal öffnen.
- [ ] **Richtlinie:** `sudo oaap tenant policy <kürzel>` zeigt die gewollte
      Vorgabe (Rolle `user` bei der ersten Anmeldung, Selbstregistrierung aus).
- [ ] **Rollen:** `<verwalter>` hat `tenant_admin` **und** — für jede Anwendung,
      die er verwalten soll — die App-Rolle `admin` (`tenant_admin` ist keine
      App-Rolle, FAQ F23). Mit einem **frischen Anmeldevorgang** prüfen
      (privates Fenster), weil Rollen mit der Sitzung kommen.
- [ ] **Keine knotenweiten Rechte:** `sudo oaap user list` zeigt für `<verwalter>`
      weder `server_admin` noch `support`.
- [ ] **Anmeldung getestet:** Eine Testperson (nicht der Verwalter) legt der
      Betreiber im Realm an; sie meldet sich an und bekommt `user`. Danach im
      Realm sperren oder löschen (Löschen: Ideenspeicher I-18).
- [ ] **Öffentliche Routen bewusst:** Welche Anwendungen haben eine Route
      `public`? Sie sind ohne Anmeldung erreichbar. Testinstanzen mit
      Suchmaschinen-Sperre betreiben, falls die Anwendung das kann.
- [ ] **Öffentliche Anwendung vor dem Livegang:** Suchmaschinen-Sperre der
      **Produktivinstanz** nach Absicht gesetzt (`oaap app config list …`),
      Titel ohne „Test", Adresse des Kunden getestet (FAQ F26, F27).

## B. Sicherung vor der Übergabe (Betreiber)

Ziel: ein Stand „so wurde übergeben", den man später vergleichen kann.
Für den Gesamtprozess gilt als Tor: **Sicherung sichergestellt und getestet**
(Lauf `ok`, Mandantenarchiv vorhanden, Rückholweg einmal durchgespielt oder
bewusst als offen benannt). Wie die Auslagerung im Einzelnen aussieht, wird
getrennt geklärt und hält die Übergabe nicht auf. Kommen nach dem Stand noch
Instanzen dazu, den Stand für den Mandanten neu ziehen.

```sh
sudo oaap backup status                                      # nächtlicher Lauf zuletzt "ok"?
sudo oaap backup create --tenant <kürzel> --to /var/backups/oaap-mandanten
sudo oaap idp export <auth> --tenant <kürzel> --out /root/<kürzel>-realm.json --dry-run
sudo oaap idp export <auth> --tenant <kürzel> --out /root/<kürzel>-realm.json
```

- [ ] Letzter Lauf des Knotens `ok`, mit Zeitpunkt und Größe notiert.
      **Achtung:** `oaap backup status` zeigt nur, ob jeder Mandant **im
      Knotenarchiv enthalten** ist (Liste je Mandant mit Zahl der Instanzen),
      nicht den letzten Lauf. Den Lauf prüft man am Verzeichnis:
      `sudo ls -l /var/backups/oaap | tail -4` — neuestes Archiv mit Zeitstempel
      der letzten Nacht, daneben die Datei `.sha256` und `status.json`. Fehlt die
      Prüfsumme oder ist das Archiv älter als ein Tag, ist der Lauf nicht in
      Ordnung.
- [ ] Mandantenarchiv liegt vor. `backup create --tenant … --to <Ordner>` legt den
      Zielordner selbst an (Modus 0600 für die Datei); er muss nicht vorher
      existieren. Nur die Apps dieses Mandanten stehen dabei kurz (Sekunden).
      Die Ausgabe nennt Zahl der Instanzen und Benutzer — mit dem Realm-Export
      vergleichen (gleiche Zahl Personen). Das Archiv beweist **Existenz**, ist
      nicht direkt zurückspielbar (Mandanten-Restore ist ungebaut) und enthält den
      Realm nicht.
- [ ] Realm-Export liegt vor. **Die Datei ist ein Geheimnis** (Client-Secret und
      Passwort-Hashes aller Mitglieder). Sie liegt mit Modus 0600 bei `root`,
      außerhalb der Plattformdaten und nie in einem Repository oder Brief. Sie
      gehört an einen Ort, den der Betreiber für Geheimnisse nutzt. Der Befehl
      nennt am Ende die Zahl der Personen, gezählt in der
      Datei **und** beim Anbieter; beide Zahlen müssen stimmen. Danach Rechte
      prüfen (`sudo ls -l <Datei>`: `-rw-------`, `root root`). Die Datei liegt
      auf demselben Knoten wie das Original und schützt daher nicht vor dem
      Verlust des Knotens: an den Geheimnisort des Betreibers kopieren und vom
      Knoten entfernen (siehe auch Ideenspeicher I-23).
- [ ] Ist die Auslagerung durch einen Dienstleister eingerichtet, ist die
      Quittung der letzten Abholung zu sehen (Gesundheitsseite des Portals).

## C. Zugänge für die KI des Kunden (falls der Kunde mit KI entwickelt)

- [ ] **Erste Test-Instanz** hat der Betreiber angelegt (`oaap app install …
      --channel test --tenant <kürzel>`); das Profil `dev` ist nicht nötig (FAQ F24).
- [ ] **Deploy-Token** erzeugt (`sudo oaap app token create <kürzel>-<web-test>`),
      **einmal** angezeigt, dem Kunden **getrennt** vom Briefing übergeben
      (anderer Kanal als das Briefing, nie im Repository des Kunden). Notiert:
      Datum, Empfänger, Instanz.
- [ ] **Zugangsdaten für die KI** (Konfigurationsdatei mit Geheimnissen) als
      passwortgeschütztes Archiv übergeben, das Passwort auf einem **anderen**
      Weg; das Briefing nennt es nicht.
- [ ] **Briefing** (`oaap-docs/vorlagen/ki-briefing-test-deployment.md`) und
      optional `oaap-deploy.py` mitgegeben, zusammen mit der Hook-Adresse und
      der Adresse zum Ausprobieren.
- [ ] Dem Kunden gesagt: Der **erste Deploy braucht eine höhere Version** als die
      installierte; **produktiv** setzt ein Mensch (im Portal), nie die KI.
- [ ] Dem Kunden gesagt: Wenn der Knoten eine **Bestätigung** verlangt
      (neue öffentliche Route, neuer Speicher), fragt die KI beim Kunden, und der
      Kunde beim Betreiber, bis es dafür einen Portalweg für den Mandantenverwalter gibt.

## D. Übergabegespräch mit dem Verwalter (Kunde)

**Was übergeben wird**

| Was | Wie |
|---|---|
| Adresse des Portals | `https://<kürzel>.<knoten>/` |
| Zugang | Benutzername im Realm; Startpasswort **auf getrenntem Weg**, mit Pflicht zur Änderung bei der ersten Anmeldung |
| Adressen der Anwendungen | Liste der Instanzen mit Zweck |
| Ansprechperson und Erreichbarkeit | Betreiber bzw. Dienstleister |

**Was der Verwalter selbst tun kann**

| Aufgabe | Wo |
|---|---|
| Mitglieder anlegen, Passwort zurücksetzen, sperren | Konsole des Anmeldedienstes (Realm des Mandanten) oder später die Mitglieder-App |
| Rollen vergeben (`user`, `keyuser`, `admin`, `partner`) | Portal → Benutzer |
| Fachliche Rollen aus Gruppen des Anmeldedienstes | noch nicht vorgesehen (Ideenspeicher I-29) |
| Eine Test-Instanz produktiv setzen | Portal → Instanzseite → Übernehmen |
| Konfiguration der Anwendungen ändern | Portal → Instanz → Konfiguration |

**Was nicht beim Verwalter liegt**

- Neue Instanzen oder Apps anlegen: Betreiber (Store-Pakete gibt es, wenn der
  Mandantenverwalter die Store-Seite sieht; eigene Pakete bringt der Betreiber).
- Rollen `server_admin`, `support` und `tenant_admin` anderer: Betreiber.
- Sicherung und Wiederherstellung: Betreiber.
- Die Richtlinie für neue Mitglieder: Betreiber.

**Bekannte Ecken, die man ansagen sollte**

- **Abmelden** beendet nur die Sitzung im Portal, nicht beim Anmeldedienst
  (Ideenspeicher I-20): Auf gemeinsamen Rechnern zusätzlich im Konto-Portal des
  Anmeldedienstes abmelden oder ein privates Fenster nutzen.
- **Passwort ändern** geht nur dort (Konto-Portal des Anmeldedienstes), nicht
  in der Passwortseite des Portals (FAQ F21, I-21).
- **Mitglieder löschen** im Anmeldedienst lässt ihren Satz im Portal stehen
  (I-18). Besser **sperren**.
- Der Reiter „Zwilling" ist für `user` sichtbar (FAQ F19).
- **Mitglieder anlegen** macht anfangs der Betreiber für wenige Personen. Wie
  der Verwalter es später selbst tut (eigenes Realm-Konto mit eng gefassten
  Rechten, Absprung aus der Mandantenverwaltung), ist offen (Ideenspeicher
  I-28). Im Übergabegespräch ehrlich sagen, welcher Weg gilt.

## E. Nach der Übergabe (Betreiber, erste Woche)

- [ ] Nach einem Tag: nächtliche Sicherung des Knotens `ok`?
- [ ] Mandantenprotokoll (Portal) zeigt die erste Anmeldung des Verwalters und
      Rollenänderungen. Unerwartete Einträge klären.
- [ ] Hat die KI des Kunden schon geliefert? `sudo oaap app artifact list
      <kürzel>-<web-test>` zeigt die Pakete; Deploy-Protokoll im Portal.
- [ ] Was gefragt wurde, im Ideenspeicher/FAQ nachtragen (neue Lücken der Übergabe).

## F. Zurücknehmen (wenn die Zusammenarbeit endet oder ein Geheimnis auftaucht)

```sh
sudo oaap app token revoke <kürzel>-<web-test>     # Deploy-Token der KI
```

- Konto des Verwalters oder einzelner Mitglieder im Anmeldedienst **sperren**;
  Rollen im Portal entziehen.
- Ist ein Realm-Export oder Token an einen falschen Ort geraten: den Ort
  aufräumen, das Geheimnis **erneuern** (neues Token, neues Client-Secret),
  nicht nur löschen.

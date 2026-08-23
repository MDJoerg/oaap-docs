# Eine App aus dem Store installieren und aktuell halten

> Geprüft gegen Referenz **0.1.42** (2026-08-23).

## Installieren (der Normalfall: ein Klick)

1. Portal → **Store**. Die Liste kommt aus den konfigurierten Quellen
   des Knotens; vertrauenswürdigere Quellen gewinnen bei Namensgleichheit.
2. App anklicken → **Installieren**. Der Knoten löst die App-Kennung
   selbst gegen seine Quellen auf, holt das Paket und baut bzw. lädt
   das Image. Der Fortschritt steht auf der Store-Seite.
3. Danach erscheint die App als Kachel im Launchpad (bei Apps mit
   Oberfläche) und unter **Instanzen**.

Dasselbe per CLI:

```sh
sudo oaap app install https://github.com/MDJoerg/oaap-store --path apps/<app-id>
```

## Konfigurieren

Portal → **Instanzen** → Instanz anklicken → Reiter **Konfiguration**.
Nur die von der App deklarierten Schlüssel sind einstellbar; Geheimnisse
werden nie zurückgezeigt. Beim Speichern wird der Container neu erzeugt
(kurz nicht erreichbar) — Daten und Adressen bleiben.

## Aktualisieren

Zeigt die Store-Seite **„Aktualisieren auf vX"**, hat die Quelle eine
neuere Fassung des Pakets veröffentlicht. Ein Klick installiert sie —
**die Daten der Instanz bleiben erhalten**, denn ein Update ist eine
Neuinstallation unter gleichem Namen mit bestehendem Storage.

Per CLI ist es wörtlich dieselbe Installation noch einmal:

```sh
sudo oaap app install https://github.com/MDJoerg/oaap-store --path apps/<app-id>
```

### Besonderheit wrapped Apps (fremde Software im OAAP-Mantel)

Bei wrapped Apps (z. B. Uptime Kuma, Forgejo) bestimmt das Store-Paket,
**welche Fassung der Fremdsoftware** läuft — die Pakete pinnen eine
exakte Version. Meldet die App selbst „neue Version verfügbar", ist das
nur ein Hinweis des Herstellers: Der OAAP-Weg ist immer das
Store-Update, nie ein Update-Knopf in der App.

Zwei Dinge vor einem großen Versionssprung wissen:

- **Datenmigrationen können Einbahnstraßen sein.** Beispiel Uptime
  Kuma 1.x → 2.x: Beim ersten Start wird die Datenbank konvertiert,
  zurück auf 1.x geht es danach nicht mehr. Die Paketbeschreibung im
  Store nennt solche Fälle.
- **Der erste Start nach so einem Sprung dauert länger** (Migration).
  Die Pakete geben der App dafür mehr Anlaufzeit; nicht nervös werden.

Knoten ziehen **nie automatisch** — aktualisiert wird, wenn der
Betreiber klickt. Das ist Absicht.

## Entfernen

Portal → Instanzen → Instanz → Reiter **Verwaltung** → „Instanz
entfernen" (mit Tippbestätigung des Namens). **„Daten behalten" ist
vorausgewählt** — eine spätere Installation gleichen Namens findet die
Daten wieder. Per CLI: `sudo oaap app remove <instanz>` (endgültig
löschen: `--purge`).

## Wenn etwas hakt

- **App-Kachel führt auf eine Fehlerseite:** Rolle prüfen — die Routen
  einer App verlangen bestimmte Rollen; die Gesundheitsseite und
  `sudo oaap app list` zeigen den Zustand.
- **„Aktualisieren" wird nicht angeboten, obwohl es eine neue Fassung
  gibt:** Der Knoten kennt die Quelle vielleicht nicht —
  `oaap store list` zeigt die konfigurierten Quellen je Knoten
  (Quellen sind nicht flottenweit).
- **Nach einem Update bleibt die App „ungesund":** erster Start nach
  einer Migration braucht Zeit; danach Logs ansehen:
  `sudo docker logs oaap-app-<instanz>`.

# Szenarien — Schritt für Schritt

Jede Anleitung führt eine Situation komplett durch, mit allen
Handgriffen und den Stellen, an denen etwas schiefgehen kann.

## Verfügbar

- [Einen OAAP-Server aufsetzen](server-aufsetzen.md) — vom frischen
  Debian zum laufenden Portal
- [Eine App aus dem Store installieren und aktuell halten](app-aus-dem-store.md)
  — Ein-Klick-Installation, Konfiguration, Updates (auch wrapped Apps)
- [Nach Produktiv übernehmen — und notfalls zurück](produktivsetzung.md)
  — dieselben Bytes gehen live (RFC-0020), Rückschritt inklusive
- [Einen Kunden-Mandanten übergeben — Checkliste](mandant-an-kunden-uebergeben.md)
  — Prüfung, Sicherungsstand, Zugänge der KI, Übergabegespräch
- [Einen Mandanten aus einem Profil aufbauen](mandant-aus-profil-aufbauen.md)
  — die Schritte von „Kunden-Mandanten einrichten“ in einem Aufruf, mit
  Verlauf, Fortsetzen und Rückbau (RFC-0055)
- [Pakete auf einem Mehrmandanten-Knoten bereitstellen](paketkatalog-pakete-bereitstellen.md)
  — der Paketkatalog: ZIP hochladen, Version freigeben, Mandanten installieren
  im Store, direkt oder mit Test-Instanz (RFC-0050)
- [Neuer Vereinsmandant mit fachlichen Rollen — Checkliste](neuer-vereinsmandant-checkliste.md)
  — Reihenfolge, Stolperer und Fehlersuche für den ersten echten Verein
- [Fachliche Rollen einrichten — aus den Vorlagen einer App](fachliche-rollen-einrichten.md)
  — Rollen, Berechtigungspakete, Abbildungen und die Gruppen im Anmeldedienst
  mit einem Befehl, mit Probelauf (oaap.core.authorization 0.4)
- [Vorgänge im Mandanten — melden, klären, übergeben](vorgaenge-im-mandanten.md)
  — Feedback-Knopf, Bereiche und Rechte, Übergabe an einen anderen Mandanten,
  Löschfrist (RFC-0061)
- [Das nächtliche Backup auf der CLI einrichten](backup-cli-einrichten.md)
  — von Hand sichern, Timer, Zustand, Abholen auf eine zweite Maschine,
  Mandanten einzeln, Wiederherstellen
- [Einen lokalen Dienst über die Plattform freigeben (wie ngrok)](lokalen-dienst-freigeben.md)
  — vom Laptop mit `oaap-expose.py` ohne eigenen Knoten, oder über einen
  inneren Knoten; Anmeldung, `--public`, beenden, Grenzen (RFC-0033)

## Geplant

- App-Projekt mit einer KI: Vorhaben im Studio, Briefing, Deploy-Hook,
  Paket-Weg (RFC-0019) — inkl. der Windows-Falle `git archive`/autocrlf
- Einen externen Server anbinden (headless, Fernwartung)
- Die Flotte im Blick: FleetView und Flotten-Schlüssel (RFC-0021)
- Einen Umzug durchspielen (Wiederherstellen auf einer frischen Maschine)
- Internet-Zugang: externer Name, Edge-Knoten, DynDNS und
  DNS-Stolperfallen

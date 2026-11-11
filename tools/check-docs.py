#!/usr/bin/env python3
"""Prüft die Kopfzeilen (Front Matter) der Doku nach RFC-0078 §4.

Fehler (Exit 1):
  - Kopf lässt sich nicht lesen, unbekannte Felder, falsche Typen
  - `audience` nennt eine Rolle, die es nicht gibt (oaap.core.identity)
  - Versionen nicht in der Form 1.2.3, Datum nicht JJJJ-MM-TT
  - `checked_against` ohne `checked_on` oder umgekehrt
  - eine `id` kommt zweimal vor (auch die Voreinstellung: Pfad ohne .md)

Hinweise (Exit 0, mit --strict Exit 1):
  - „> Geprüft gegen“ als Zitat im Text, aber kein Feld `checked_against`
  - absolute Links auf die eigenen Repositories (RFC-0078 §7: die Quelle
    zieht um; aufgeräumt wird mit dem Umzug, nicht hier)

Aufruf:  python3 tools/check-docs.py [--strict] [Verzeichnis]
Braucht PyYAML.
"""
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("check-docs: braucht PyYAML (pip install pyyaml)")

FIELDS = {"id", "title", "audience", "applies_from", "applies_until",
          "checked_against", "checked_on", "lang", "tags"}
ROLES = {"server_admin", "tenant_admin", "support", "admin", "keyuser",
         "user", "guest", "partner", "public"}
LANGS = {"de", "en"}
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
ID = re.compile(r"^[a-z0-9][a-z0-9/_.-]*$")
STAMP = "Geprüft gegen"
# Der Vermerk steht als Zitat oben auf der Seite; ein Satz, der nur
# DARÜBER spricht (AGENTS.md), ist keiner.
STAMP_LINE = re.compile(r"^>\s*" + STAMP, re.M)
OWN_LINK = re.compile(r"https?://github\.com/MDJoerg/oaap-[a-z-]+", re.I)
SKIP_DIRS = {".git", "node_modules"}


def front_matter(text):
    """(dict or None, error or None, body)."""
    if not text.startswith("---\n"):
        return None, None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, "Kopf beginnt mit --- und endet nie", text
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as e:
        return None, f"Kopf ist kein YAML: {e}", text
    if not isinstance(data, dict):
        return None, "Kopf ist keine Zuordnung key: value", text
    return data, None, text[end + 5:]


def as_date(v):
    if isinstance(v, datetime.date):
        return True
    try:
        datetime.date.fromisoformat(str(v))
        return True
    except ValueError:
        return False


def check_fields(fm):
    errs = []
    unknown = sorted(set(fm) - FIELDS)
    if unknown:
        errs.append(f"unbekannte Felder: {', '.join(unknown)}")
    if "id" in fm and not (isinstance(fm["id"], str) and ID.match(fm["id"])):
        errs.append(f"id {fm['id']!r}: nur a-z 0-9 / _ . -")
    if "title" in fm and not isinstance(fm["title"], str):
        errs.append("title ist kein Text")
    if "audience" in fm:
        aud = fm["audience"]
        if not (isinstance(aud, list) and aud and all(isinstance(r, str) for r in aud)):
            errs.append("audience ist keine nicht-leere Liste")
        else:
            bad = sorted(set(aud) - ROLES)
            if bad:
                errs.append(f"audience: unbekannte Rollen {', '.join(bad)}")
    for k in ("applies_from", "checked_against"):
        if k in fm and not (isinstance(fm[k], str) and VERSION.match(fm[k])):
            errs.append(f"{k} {fm[k]!r}: Version als Text, z. B. \"0.1.248\"")
    if "applies_until" in fm and fm["applies_until"] not in ("", None) and not (
            isinstance(fm["applies_until"], str) and VERSION.match(fm["applies_until"])):
        errs.append(f"applies_until {fm['applies_until']!r}: Version oder leer")
    if "checked_on" in fm and not as_date(fm["checked_on"]):
        errs.append(f"checked_on {fm['checked_on']!r}: Datum JJJJ-MM-TT")
    if ("checked_against" in fm) != ("checked_on" in fm):
        errs.append("checked_against und checked_on nur zusammen")
    if "lang" in fm and fm["lang"] not in LANGS:
        errs.append(f"lang {fm['lang']!r}: de oder en")
    if "tags" in fm and not (isinstance(fm["tags"], list)
                             and all(isinstance(t, str) for t in fm["tags"])):
        errs.append("tags ist keine Liste von Wörtern")
    return errs


def main(argv):
    strict = "--strict" in argv
    args = [a for a in argv if not a.startswith("--")]
    root = os.path.abspath(args[0] if args else
                           os.path.join(os.path.dirname(__file__), ".."))
    errors, hints, ids = [], [], {}
    count = with_fm = 0
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(d, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            count += 1
            with open(path, encoding="utf-8") as f:
                text = f.read().replace("\r\n", "\n")
            fm, err, body = front_matter(text)
            if err:
                errors.append(f"{rel}: {err}")
                continue
            if fm is not None:
                with_fm += 1
                errors += [f"{rel}: {e}" for e in check_fields(fm)]
            doc_id = (fm or {}).get("id") or rel[:-3]
            if doc_id in ids:
                errors.append(f"{rel}: id {doc_id!r} schon in {ids[doc_id]}")
            else:
                ids[doc_id] = rel
            if STAMP_LINE.search(body) and "checked_against" not in (fm or {}):
                hints.append(f"{rel}: „{STAMP}“ im Text, aber kein checked_against")
            links = sorted(set(OWN_LINK.findall(body)))
            if links:
                hints.append(f"{rel}: {len(OWN_LINK.findall(body))} absolute "
                             f"Links auf eigene Repositories ({', '.join(links)})")
    for e in errors:
        print(f"FEHLER   {e}")
    for h in hints:
        print(f"HINWEIS  {h}")
    print(f"\n{count} Dokumente, {with_fm} mit Kopf, {len(errors)} Fehler, "
          f"{len(hints)} Hinweise")
    return 1 if errors or (strict and hints) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

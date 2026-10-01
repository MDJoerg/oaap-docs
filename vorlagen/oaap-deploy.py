#!/usr/bin/env python3
"""Ein Paket (ZIP) über den Deploy-Hook auf eine OAAP-Test-Instanz ausrollen.

Nur Python-Standardbibliothek. Das Token kommt aus der Umgebungsvariable
OAAP_DEPLOY_TOKEN und wird nie ausgegeben.

  export OAAP_DEPLOY_TOKEN=...            # nur in dieser Sitzung
  python3 oaap-deploy.py <HOOK_URL> <paket.zip>

Der Ablauf ist der Drei-Phasen-Weg des Contracts (RFC-0019):
  1. anmelden (Manifest, Prüfsumme, Größe)  -> Antwort mit Einmal-Token
  2. hochladen (nur mit dem Einmal-Token)
  3. Status abfragen, bis der Stand läuft oder fehlgeschlagen ist

Ausgang 0 = Stand läuft, 2 = vom Knoten abgelehnt, 3 = fehlgeschlagen
oder keine Antwort, 1 = falsche Aufrufe.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

UA = "oaap-deploy/1"
POLL_SECONDS = 5
POLL_LIMIT = 25 * 60          # ein Deployment bricht nach 20 Minuten ab


def call(method, url, token, body=None, content_type=None):
    headers = {"Authorization": "Bearer " + token, "User-Agent": UA}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, str(e).encode()


def as_json(raw):
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return {"message": raw.decode("utf-8", "replace")[:500]}


def manifest_from(zip_path):
    """Das Manifest wird aus der ZIP gelesen, nicht aus einer zweiten Kopie:
    Es muss zeichengleich zu dem sein, was angekündigt wird."""
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        for n in names:
            if n.lstrip("./") == "oaap-app.yaml":
                return z.read(n).decode("utf-8")
        tops = {n.lstrip("./").split("/", 1)[0] for n in names}
        if len(tops) == 1:
            top = tops.pop()
            for n in names:
                if n.lstrip("./") == top + "/oaap-app.yaml":
                    return z.read(n).decode("utf-8")
    sys.exit("oaap-app.yaml liegt weder in der Wurzel der ZIP noch in genau einem Oberordner.")


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    hook, zip_path = sys.argv[1].rstrip("/"), sys.argv[2]
    token = os.environ.get("OAAP_DEPLOY_TOKEN", "").strip()
    if not token:
        print("OAAP_DEPLOY_TOKEN ist nicht gesetzt.", file=sys.stderr)
        return 1
    with open(zip_path, "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()
    manifest = manifest_from(zip_path)

    print(f"1/3 anmelden: {len(data)} Bytes, sha256 {sha[:12]}…")
    body = json.dumps({"manifest": manifest, "artifact_sha256": sha,
                       "artifact_bytes": len(data)}).encode()
    status, raw = call("POST", hook + "/announce", token, body, "application/json")
    ans = as_json(raw)
    if status != 200 or not ans.get("ok"):
        print(f"ABGELEHNT ({status}): {ans.get('refused', '')}", file=sys.stderr)
        for d in ans.get("details") or []:
            print(f"  - {d}", file=sys.stderr)
        print(ans.get("message", ""), file=sys.stderr)
        return 2 if status in (422, 413) else 3
    upload_url = urllib.parse.urljoin(hook + "/", ans["upload_url"])

    print("2/3 hochladen …")
    status, raw = call("PUT", upload_url, ans["upload_token"], data, "application/zip")
    res = as_json(raw)
    if status == 202:
        rid = res.get("deployment", "")
        print(f"3/3 läuft noch (Kennung {rid[:8]}), frage den Status …")
        waited = 0
        while waited < POLL_LIMIT:
            time.sleep(POLL_SECONDS)
            waited += POLL_SECONDS
            status, raw = call("GET", f"{hook}/status?deployment={rid}", token)
            res = as_json(raw)
            if res.get("state") == "done":
                break
        else:
            print("Keine Rückmeldung innerhalb der Frist.", file=sys.stderr)
            return 3
    elif status == 0:
        print(f"Keine Antwort: {res.get('message', '')}\n"
              f"Das ist keine Ablehnung. Frage `GET {hook}/status` und wiederhole "
              "nicht blind.", file=sys.stderr)
        return 3
    ok = bool(res.get("ok"))
    print(("LÄUFT" if ok else "FEHLGESCHLAGEN")
          + f": Version {res.get('version', '?')}, {res.get('message', '')}")
    if res.get("url"):
        print("Ansehen unter:", res["url"])
    return 0 if ok else (2 if status == 422 else 3)


if __name__ == "__main__":
    sys.exit(main())

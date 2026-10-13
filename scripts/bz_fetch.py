#!/usr/bin/env python3
"""Fetch the Substantive Laws of Belize, Revised Edition 2020, from the
Attorney General's Ministry (agm.gov.bz).

The /laws/law_substantive page loads chapter lists per volume via
POST /api-laws/ {action: 1000, volume: N}. Each row links to a chapter PDF.
PDFs are saved to _raw/bz/pdf/.
"""
import json, os, re, subprocess, sys, time
import requests

BASE = "https://www.agm.gov.bz"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "bz")
DELAY = 1.0
VOLUMES = range(1, 19)
s = requests.Session()
s.headers["User-Agent"] = UA


def req(method, url, **kw):
    for i in range(5):
        try:
            r = s.request(method, url, timeout=300, **kw)
            if r.status_code in (200, 404, 403):
                return r
        except requests.RequestException as e:
            print("  retry", url, e, file=sys.stderr)
        time.sleep(5 * (i + 1))
    raise RuntimeError("failed " + url)


def pdf_ok(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, size - 4096))
        tail = f.read()
    if head != b"%PDF-" or b"%%EOF" not in tail:
        return False
    return subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    lp = os.path.join(RAW, "list.json")
    if os.path.exists(lp):
        items = json.load(open(lp))
    else:
        req("GET", BASE + "/laws/law_substantive")
        items = []
        for v in VOLUMES:
            r = req("POST", BASE + "/api-laws/", data={"action": 1000, "volume": v},
                    headers={"X-Requested-With": "XMLHttpRequest"})
            rows = r.json().get("data", [])
            for row in rows:
                m = re.search(r'href="([^"]+)"[^>]*>([^<]*)', row[0])
                if m:
                    items.append({"volume": v, "href": m.group(1), "label": m.group(2).strip()})
            print("volume", v, len(rows), flush=True)
            time.sleep(DELAY)
        json.dump(items, open(lp, "w"), indent=1)
    print(len(items), "items", flush=True)
    for n, it in enumerate(items):
        fn = it["href"].split("/")[-1]
        p = os.path.join(RAW, "pdf", fn)
        if pdf_ok(p):
            continue
        try:
            r = req("GET", BASE + it["href"])
        except RuntimeError as e:
            print(n, fn, "FAILED", e, flush=True)
            continue
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            cl = r.headers.get("content-length")
            if not cl or int(cl) == len(r.content):
                open(p, "wb").write(r.content)
        print(n, fn, pdf_ok(p), r.status_code, flush=True)
        time.sleep(DELAY)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Convert the Substantive Laws of Belize, Revised Edition 2020 PDFs (_raw/bz) to Markdown."""
import datetime, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bz_pdfmd as pm

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.abspath(os.path.join(ROOT, "..", "_raw", "bz"))
BASE = "https://www.agm.gov.bz"
PAGE = BASE + "/laws/law_substantive"
JUNK = [r"^THE SUBSTANTIVE LAWS OF BELIZE(\s+REVISED EDITION \d{4})?$", r"^REVISED EDITION \d{4}$",
        r"^Printed by Authority of the$", r"^Government of Belize$", r"^\[\s*\]$", r"^[\[\]]$"]


def slugify(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80].strip("-")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def front(d):
    out = ["---"]
    for k, v in d.items():
        if v is None or v == "":
            continue
        out.append(f"{k}: {v if isinstance(v, (int, float)) or k in ('date', 'last_amended', 'retrieved', 'type', 'jurisdiction', 'language', 'status') else q(v)}")
    out.append("---")
    return "\n".join(out) + "\n\n"


def pdf_ok(path):
    if not os.path.exists(path):
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 4096))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def main():
    retrieved = datetime.date.today().isoformat()
    for d in ("chapters", "constitution"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    items = json.load(open(os.path.join(RAW, "list.json")))
    report = {"converted": [], "gaps": []}
    used = set()
    for it in items:
        fn = it["href"].split("/")[-1]
        pdf = os.path.join(RAW, "pdf", fn)
        label = it["label"].strip()
        if not pdf_ok(pdf):
            report["gaps"].append({"title": label, "reason": "PDF not downloadable / incomplete", "source": BASE + it["href"]})
            continue
        body, st = pm.pdf_to_md(pdf, extra_header_patterns=JUNK, anywhere_patterns=JUNK, tmpdir=RAW)
        if st["chars_per_page"] < 150:
            report["gaps"].append({"title": label, "reason": "PDF has no text layer (scan)", "source": BASE + it["href"]})
            continue
        cm = re.match(r"cap\.?\s*(\d+)(?:[._:](\d+))?\.?\s+(.*)$", label, re.I)
        if cm:
            major, minor, name = int(cm.group(1)), cm.group(2), cm.group(3)
            cap = f"{major}" + (f":{minor}" if minor else "")
            fname = f"cap-{major:03d}" + (f"-{minor}" if minor else "") + "-" + slugify(name)
        else:
            cap, name = None, label
            fname = slugify(label)
        # the portal's labels encode "(...)" as double spaces
        name = re.sub(r"\s{2}(.+?)\s{2}", r" (\1) ", name)
        name = re.sub(r"\s{2}(.+?)$", r" (\1)", name).strip()
        name = re.sub(r"\s+", " ", name)
        is_const = cap == "4"
        p1 = subprocess.run(["pdftotext", "-l", "2", pdf, "-"], capture_output=True, text=True).stdout
        am = re.search(r"AS AT\s+(\d+)\s*(?:ST|ND|RD|TH)?\s+([A-Z]+),?\s+(\d{4})", p1, re.I)
        asat = None
        if am:
            try:
                asat = datetime.datetime.strptime(f"{am.group(1)} {am.group(2).title()} {am.group(3)}", "%d %B %Y").date().isoformat()
            except ValueError:
                pass
        while fname in used:
            fname += "-2"
        used.add(fname)
        rel = ("constitution/" if is_const else "chapters/") + fname + ".md"
        fm = {
            "title": name,
            "identifier": f"Cap. {cap}" if cap else None,
            "type": "constitution" if is_const else "act",
            "jurisdiction": "bz", "language": "en",
            "last_amended": asat,
            "status": "in_force",
            "edition": "Substantive Laws of Belize, Revised Edition 2020",
            "volume": it.get("volume"),
            "source": PAGE,
            "source_pdf": BASE + it["href"],
            "pages": st["pages"],
            "retrieved": retrieved,
        }
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
            f.write(front(fm) + f"# {name}\n\n" + body)
        report["converted"].append({"title": label, "file": rel, "quality": st["quality"]})
        print(rel, st["quality"], flush=True)
    json.dump(report, open(os.path.join(RAW, "convert_report.json"), "w"), indent=1)
    print(len(report["converted"]), "converted;", len(report["gaps"]), "gaps")


if __name__ == "__main__":
    main()

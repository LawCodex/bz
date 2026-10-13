# Belize — Substantive Laws of Belize (LawCodex)

Consolidated primary legislation of **Belize** as plain Markdown, converted from the official
**Substantive Laws of Belize, Revised Edition 2020** chapter PDFs published by the Attorney General's
Ministry (Law Revision Commissioner) at <https://www.agm.gov.bz/laws/law_substantive>.

Retrieved: 2026-10-13.

## Contents

| Directory | What | Files |
|---|---|---|
| `constitution/` | Belize Constitution Act, Cap. 4 (the Constitution is its Schedule) | 1 |
| `chapters/` | All other chapters of the Revised Edition 2020 (Caps 1–339 incl. sub-numbered chapters such as Cap. 10:01) | 412 |

Total: **413 chapters**, i.e. every chapter listed in the 18 volumes on the official portal.
Each file has YAML front matter (`title`, `identifier` = Cap. number, `type`, `last_amended` = the
"as at" date of the revised edition printed on the cover, `volume`, `source`, `source_pdf`, `pages`,
`retrieved`). File names: `cap-NNN[-SS]-<slug>.md`.

Chapter PDFs also reproduce, where applicable, the amendment history notes and marginal notes. Marginal
notes (section headings / amendment references printed in the margin) are rendered as *italic* lines
placed before the paragraph they sit beside; section numbers are rendered in **bold**.

## Not covered

- **Subsidiary Laws (R.E. 2020)** and **Statutory Instruments** — also published on agm.gov.bz but not
  included (secondary legislation; optional under LawCodex conventions).
- **Acts passed after the 2020 revision** (the portal's "Acts" section) — the chapters here are the
  consolidated text as at 31 December 2020; later amending Acts are not merged in.
- Tables and forms are flattened to text paragraphs (PDF text extraction); complex tables may need
  checking against the PDF.

## Source and licence

Official texts of the Government of Belize, published by the Attorney General's Ministry. Legislation is
published for public information; no restrictive terms of use were found on the portal. This repository
is an unofficial conversion — the official PDFs remain authoritative.

## Method / regenerate

```
python3 scripts/bz_fetch.py     # lists volumes 1-18 via POST /api-laws/ and downloads PDFs to ../_raw/bz/pdf
python3 scripts/bz_convert.py   # pdftotext -bbox-layout -> Markdown (scripts/bz_pdfmd.py)
```

Requires poppler (`pdftotext`, `pdfinfo`) and the Python packages in `scripts/requirements.txt`.
Downloaded PDFs are verified (header, `%%EOF`, `pdfinfo`, Content-Length) before conversion.
Running headers/footers ("THE SUBSTANTIVE LAWS OF BELIZE / REVISED EDITION 2020 / Printed by
Authority…") are removed.

#!/usr/bin/env python3
"""
Assemble the self-contained browser app.

Reads app/template.html and inlines the vendored pdf.js library + worker,
producing quickbooks-iif/TD-to-IIF.html — a single file employees open in a
browser and drag a PDF onto. No network, no install.

Run:  python3 app/build.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

template = (HERE / "template.html").read_text(encoding="utf-8")
lib = (HERE / "vendor" / "pdf.min.js").read_text(encoding="utf-8")
worker = (HERE / "vendor" / "pdf.worker.min.js").read_text(encoding="utf-8")

# Neither vendored file contains the literal "</script" (verified), so direct
# inlining is safe; guard anyway.
for name, blob in (("pdf.min.js", lib), ("pdf.worker.min.js", worker)):
    if "</script" in blob.lower():
        raise SystemExit(f"{name} contains </script — embedding would break the HTML")

html = template.replace("/*__PDFJS_LIB__*/", lib).replace("/*__PDFJS_WORKER__*/", worker)

out = ROOT / "TD-to-IIF.html"
out.write_text(html, encoding="utf-8")
print(f"Wrote {out}  ({out.stat().st_size/1024:.0f} KB)")

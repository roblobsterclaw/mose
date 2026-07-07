#!/usr/bin/env python3
"""
watch_inbox.py — the "drop a PDF, get an IIF" app for staff.

Leave this running (double-click the .command/.bat wrapper, or run it in a
terminal). Any TD Bank PDF statement dropped into the `inbox/` folder is
automatically converted:

    inbox/statement.pdf
        -> output/statement.iif           (import this into QuickBooks)
        -> output/statement.summary.txt   (what was categorized + review list)
        -> processed/statement.pdf        (the original, moved out of the way)

If a statement does NOT reconcile, the PDF is moved to `failed/` instead and the
reason is printed — nothing bad ever silently reaches QuickBooks.

No extra dependencies beyond PyMuPDF (used by td_to_iif). Pure polling, so it
works anywhere without installing a file-watcher library.
"""

import shutil
import sys
import time
from pathlib import Path

import td_to_iif as converter

HERE = Path(__file__).resolve().parent
INBOX = HERE / "inbox"
OUTPUT = HERE / "output"
PROCESSED = HERE / "processed"
FAILED = HERE / "failed"
POLL_SECONDS = 3


def _stable(path, checks=2, gap=0.6):
    """Wait until a file's size stops changing (finished copying)."""
    last = -1
    stable = 0
    while stable < checks:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        stable = stable + 1 if size == last else 0
        last = size
        time.sleep(gap)
    return True


def process(pdf):
    for d in (OUTPUT, PROCESSED, FAILED):
        d.mkdir(exist_ok=True)
    # Name the output by the statement's own period (e.g. valet-box-2026-07.iif)
    # rather than the PDF's filename. Re-dropping the same month overwrites the
    # same file instead of making "june (2).iif", so staff can't accidentally
    # end up with two importable copies of one month.
    try:
        meta, _txns, _ = converter.parse_statement(str(pdf))
        slug = meta.get("period_slug", pdf.stem)
    except Exception:
        slug = pdf.stem
    iif_path = OUTPUT / f"valet-box-{slug}.iif"
    print(f"\n[{time.strftime('%H:%M:%S')}] Converting {pdf.name} ...")
    try:
        converter.convert(str(pdf), str(iif_path))
    except SystemExit as e:
        # convert() calls sys.exit on reconciliation failure / bad PDF
        print(f"  -> FAILED ({e}). Moving to failed/", file=sys.stderr)
        shutil.move(str(pdf), str(FAILED / pdf.name))
        return
    except Exception as e:  # noqa: BLE001 - keep the watcher alive for staff
        print(f"  -> ERROR: {e}. Moving to failed/", file=sys.stderr)
        shutil.move(str(pdf), str(FAILED / pdf.name))
        return
    shutil.move(str(pdf), str(PROCESSED / pdf.name))
    print(f"  -> Done. Import {iif_path.name} into QuickBooks.")


def main():
    for d in (INBOX, OUTPUT, PROCESSED, FAILED):
        d.mkdir(exist_ok=True)
    print("Watching for TD Bank PDFs in:", INBOX)
    print("Drop a statement PDF in there. Press Ctrl+C to stop.\n")
    seen = set()
    try:
        while True:
            for pdf in sorted(INBOX.glob("*.pdf")):
                if pdf in seen:
                    continue
                if _stable(pdf):
                    process(pdf)
                seen.discard(pdf)
            # forget files that were moved out so re-dropping the same name works
            seen = {p for p in seen if p.exists()}
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

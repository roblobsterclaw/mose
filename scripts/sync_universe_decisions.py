#!/usr/bin/env python3
"""Close the approval loop: read Joe's Universe-tab decisions from Firebase and
apply them to reference-data/cik-map.json.

  approved candidate  -> appended to cik-map.json (tier 1, source_type 13F, status "approved")
  rejected candidate  -> nothing (stays out)
  rejected tracked    -> kept in cik-map.json with status "pruned" (history preserved, stops voting)
  undo (no decision)  -> a previously approved entry stays until removed by hand

Never removes an entry. Prints what it did. Run from the Action or by hand:
  python3 scripts/sync_universe_decisions.py [--dry-run]
"""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIKMAP = ROOT / "reference-data" / "cik-map.json"
UNIVERSE = ROOT / "reference-data" / "investor-universe.json"
FB = "https://jfl-ttd-default-rtdb.firebaseio.com/mose/universeDecisions.json"

def main(dry: bool) -> None:
    with urllib.request.urlopen(FB, timeout=20) as r:
        decisions = json.load(r) or {}
    if not isinstance(decisions, dict):
        print("no decisions in Firebase"); return
    cand = {c["cik"]: c for c in json.load(open(UNIVERSE)).get("candidates", [])}
    data = json.load(open(CIKMAP))
    rows = data if isinstance(data, list) else data.setdefault("investors", [])
    by_cik = {str(r.get("cik")).lstrip("0"): r for r in rows if isinstance(r, dict) and r.get("cik")}
    added, pruned, unchanged = [], [], 0
    for cik, d in decisions.items():
        cik = str(cik).lstrip("0"); status = (d or {}).get("status")
        c = cand.get(cik, {})
        if status == "approved" and cik not in by_cik:
            entry = {"name": c.get("name") or d.get("name") or cik, "fund": c.get("name") or "", "tier": 1,
                     "source_type": "13F", "cik": cik, "status": "approved",
                     "note": f"Approved in MOSE Universe tab {d.get('date','')} (fit {c.get('fit','?')}, {c.get('positions','?')} positions, ${(c.get('total_value_usd') or 0)/1e9:.1f}B)."}
            rows.append(entry); by_cik[cik] = entry; added.append(entry["name"])
        elif status == "rejected" and cik in by_cik and by_cik[cik].get("status") != "pruned":
            by_cik[cik]["status"] = "pruned"; by_cik[cik]["pruned_at"] = d.get("date", ""); pruned.append(by_cik[cik]["name"])
        else:
            unchanged += 1
    if not dry:
        json.dump(data, open(CIKMAP, "w"), indent=1)
    print(f"{datetime.now(timezone.utc).isoformat()} decisions={len(decisions)} added={added} pruned={pruned} unchanged={unchanged}{' (dry run)' if dry else ''}")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)

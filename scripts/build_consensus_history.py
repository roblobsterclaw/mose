#!/usr/bin/env python3
"""Consensus leaderboard with momentum — every stock the voting filers own,
ranked, with holder counts per quarter so rising and falling names surface
themselves.

Writes consensus-history.json:
  { generated_at, quarters[], investors[], buy_list[], rows: [ {
      ticker, company, now, prior, yr_ago, d_q, d_y, series[],
      holders[], added[], dropped[], avg_pct, sum_pct, adding, trimming,
      first_seen, in_buy_list, status } ] }

Same voting rule and share-class folding as the guard rail, so the numbers here
always agree with the ✓N chips on the Buy tab.
"""
from __future__ import annotations
import json, collections
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# reference-data/cik-map.json is the roster's source of truth for `status`.
# The filings file only carries a copy taken at pull time, so a prune made in
# cik-map.json must win here — otherwise a pruned filer keeps voting until the
# next full SEC pull, which is exactly the bug this closes.
_CIKMAP_STATUS = {}
try:
    import json as _json
    _cm = _json.load(open(ROOT / "reference-data" / "cik-map.json"))
    for _r in (_cm if isinstance(_cm, list) else _cm.get("investors", [])):
        if _r.get("cik"):
            _CIKMAP_STATUS[str(_r["cik"]).lstrip("0")] = str(_r.get("status") or "approved").lower()
except Exception:
    pass


def roster_status(inv: dict) -> str:
    cik = str(inv.get("cik") or "").lstrip("0")
    return _CIKMAP_STATUS.get(cik) or str(inv.get("status") or "active").lower()
RAW = ROOT / "data" / "sec-13f-filings.json"
CUSIP = ROOT / "reference-data" / "cusip-map.json"
OUT = ROOT / "consensus-history.json"

SHARE_CLASS = {"BRK-A": "BRK.B", "BRK-B": "BRK.B", "GOOG": "GOOGL",
               "UHAL-B": "UHAL", "LEN-B": "LEN", "HEI-A": "HEI"}
VOTING = {"active", "approved", ""}
# The Buy-tab list (Forever + Toll booths). Kept here so "not on my list" is
# computed, not hand-maintained.
BUY_LIST = ["GOOGL", "AMZN", "META", "MSFT", "AAPL", "BRK.B", "NFLX", "TSM", "NVDA",
            "ASML", "TSLA", "UBER", "SPCX", "V", "MA", "MCO", "SPGI"]


def cn(t: str) -> str:
    return SHARE_CLASS.get(t, t)


def main() -> None:
    raw = json.load(open(RAW))
    cmap = json.load(open(CUSIP))["map"]
    voting = [i for i in raw["investors"] if roster_status(i) in VOTING]
    quarters = sorted({f["quarter"] for i in voting for f in i["filings"]})
    latest, prior = quarters[-1], quarters[-2]
    yr_ago = quarters[-5] if len(quarters) >= 5 else quarters[0]

    holders = collections.defaultdict(lambda: collections.defaultdict(set))
    pct = collections.defaultdict(dict)          # ticker -> investor -> % of book
    company = {}
    moves = collections.defaultdict(lambda: {"adding": 0, "trimming": 0})
    for inv in voting:
        by_q = {f["quarter"]: f for f in inv["filings"]}
        for q, f in by_q.items():
            agg = collections.defaultdict(float)
            shares = collections.defaultdict(float)
            for h in f["holdings"]:
                c = h.get("cusip")
                t = (cmap.get(c) or {}).get("ticker") if c else None
                if not t:
                    continue
                t = cn(t)
                holders[t][q].add(inv["name"])
                agg[t] += h.get("pct_portfolio") or 0
                shares[t] += h.get("shares") or 0
                company.setdefault(t, h.get("company") or "")
            if q == latest:
                for t, p in agg.items():
                    pct[t][inv["name"]] = round(p, 2)
                prev = by_q.get(prior)
                if prev:
                    psh = collections.defaultdict(float)
                    for h in prev["holdings"]:
                        c = h.get("cusip")
                        t2 = (cmap.get(c) or {}).get("ticker") if c else None
                        if t2:
                            psh[cn(t2)] += h.get("shares") or 0
                    for t, sh in shares.items():
                        if psh.get(t):
                            if sh > psh[t] * 1.02:
                                moves[t]["adding"] += 1
                            elif sh < psh[t] * 0.98:
                                moves[t]["trimming"] += 1

    rows = []
    for t, byq in holders.items():
        now = sorted(byq.get(latest, ()))
        pr = byq.get(prior, set())
        yr = byq.get(yr_ago, set())
        if not now and not pr:
            continue
        seen = [q for q in quarters if byq.get(q)]
        rows.append({
            "ticker": t, "company": company.get(t, ""),
            "now": len(now), "prior": len(pr), "yr_ago": len(yr),
            "d_q": len(now) - len(pr), "d_y": len(now) - len(yr),
            "series": [len(byq.get(q, ())) for q in quarters],
            "holders": now,
            "added": sorted(set(now) - pr), "dropped": sorted(pr - set(now)),
            "sum_pct": round(sum(pct.get(t, {}).values()), 1),
            "avg_pct": round(sum(pct.get(t, {}).values()) / len(now), 2) if now else 0,
            "adding": moves[t]["adding"], "trimming": moves[t]["trimming"],
            "first_seen": seen[0] if seen else None,
            "in_buy_list": t in BUY_LIST,
        })
    rows.sort(key=lambda r: (-r["now"], -r["sum_pct"]))
    OUT.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "data/sec-13f-filings.json, voting filers only, share classes folded",
        "quarters": quarters, "latest": latest, "prior": prior, "yr_ago": yr_ago,
        "investor_count": len(voting),
        "investors": sorted(i["name"] for i in voting),
        "buy_list": BUY_LIST,
        "rows": rows,
    }, indent=1))
    rising = [r for r in rows if not r["in_buy_list"] and r["now"] >= 4 and r["d_y"] >= 2]
    falling = [r for r in rows if r["yr_ago"] >= 4 and r["d_y"] <= -2]
    print(f"{len(rows)} tickers over {len(quarters)} quarters, {len(voting)} voting filers")
    print(f"rising & not on the buy list: {len(rising)} | losing consensus: {len(falling)}")
    for r in sorted(rising, key=lambda r: -r["d_y"])[:8]:
        print(f"  UP   {r['ticker']:7} {r['yr_ago']:>2} -> {r['now']:>2} ({r['d_y']:+d})")
    for r in sorted(falling, key=lambda r: r["d_y"])[:8]:
        print(f"  DOWN {r['ticker']:7} {r['yr_ago']:>2} -> {r['now']:>2} ({r['d_y']:+d})")


if __name__ == "__main__":
    main()

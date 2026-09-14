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

Core vs All-in (added 14 Sep 2026, Joe's roster review): every voting filer
carries a `wing` in reference-data/cik-map.json — `core` (the Buffett/Munger
school, the names Joe wants to dictate his top 15) or `bench` (looser value,
watched for ideas). Each row carries both counts. The conviction score is
holders x average % of book, i.e. `sum_pct` — one filer at 20% of the book
outweighs three at 1%. `core_15` and `all_15` are the two top-15 rankings and
`agree` is their overlap; `bench_watch` is the rail of names the bench is
piling into that the core does not yet hold.
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
_CIKMAP_WING = {}
try:
    import json as _json
    _cm = _json.load(open(ROOT / "reference-data" / "cik-map.json"))
    for _r in (_cm if isinstance(_cm, list) else _cm.get("investors", [])):
        if _r.get("cik"):
            _k = str(_r["cik"]).lstrip("0")
            _CIKMAP_STATUS[_k] = str(_r.get("status") or "approved").lower()
            _CIKMAP_WING[_k] = str(_r.get("wing") or "bench").lower()
except Exception:
    pass


def roster_status(inv: dict) -> str:
    cik = str(inv.get("cik") or "").lstrip("0")
    return _CIKMAP_STATUS.get(cik) or str(inv.get("status") or "active").lower()


def roster_wing(inv: dict) -> str:
    """'core' or 'bench'. A voter with no wing recorded is bench — it can
    surface ideas but never sets the top 15 on its own."""
    cik = str(inv.get("cik") or "").lstrip("0")
    return _CIKMAP_WING.get(cik) or "bench"
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
    core_names = {i["name"] for i in voting if roster_wing(i) == "core"}
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
        c_now = [n for n in now if n in core_names]
        c_pr = pr & core_names
        c_yr = yr & core_names
        c_pct = [v for n, v in pct.get(t, {}).items() if n in core_names]
        c_add = sorted((set(now) - pr) & core_names)
        c_drop = sorted((pr - set(now)) & core_names)
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
            # Core wing only — the filers Joe lets dictate the top 15.
            "core_now": len(c_now), "core_prior": len(c_pr), "core_yr_ago": len(c_yr),
            "core_d_q": len(c_now) - len(c_pr), "core_d_y": len(c_now) - len(c_yr),
            "core_series": [len(byq.get(q, set()) & core_names) for q in quarters],
            "core_holders": c_now, "core_added": c_add, "core_dropped": c_drop,
            "core_sum_pct": round(sum(c_pct), 1),
            "core_avg_pct": round(sum(c_pct) / len(c_now), 2) if c_now else 0,
            "bench_now": len(now) - len(c_now),
        })
    rows.sort(key=lambda r: (-r["now"], -r["sum_pct"]))
    # Conviction rankings: holders x avg % of book == sum of % of book. A name
    # needs at least 3 holders in the wing to rank, so one 40% position can't
    # put an obscure micro-cap into a top 15 by itself.
    core_rank = sorted([r for r in rows if r["core_now"] >= 3],
                       key=lambda r: (-r["core_sum_pct"], -r["core_now"]))
    all_rank = sorted([r for r in rows if r["now"] >= 3],
                      key=lambda r: (-r["sum_pct"], -r["now"]))
    for i, r in enumerate(core_rank):
        r["core_rank"] = i + 1
    for i, r in enumerate(all_rank):
        r["all_rank"] = i + 1
    core_15 = [r["ticker"] for r in core_rank[:15]]
    all_15 = [r["ticker"] for r in all_rank[:15]]
    agree = [t for t in core_15 if t in all_15]
    # Bench watch: the bench is piling in (4+ bench holders, gaining over the
    # year) and the core has not caught up. Idea rail, never a buy signal.
    bench_watch = [r["ticker"] for r in sorted(
        [r for r in rows if r["bench_now"] >= 4 and r["d_y"] >= 2 and r["core_now"] <= 2
         and r["ticker"] not in core_15],
        key=lambda r: (-r["d_y"], -r["bench_now"]))[:12]]
    OUT.write_text(json.dumps({
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "data/sec-13f-filings.json, voting filers only, share classes folded",
        "quarters": quarters, "latest": latest, "prior": prior, "yr_ago": yr_ago,
        "investor_count": len(voting),
        "core_count": len(core_names),
        "bench_count": len(voting) - len(core_names),
        "investors": sorted(i["name"] for i in voting),
        "core_investors": sorted(core_names),
        "buy_list": BUY_LIST,
        "core_15": core_15, "all_15": all_15, "agree": agree, "bench_watch": bench_watch,
        "rows": rows,
    }, indent=1))
    print(f"core {len(core_names)} / bench {len(voting) - len(core_names)}")
    print("CORE 15:", " ".join(core_15))
    print("ALL  15:", " ".join(all_15))
    print("agree:", len(agree), "| bench watch:", " ".join(bench_watch))
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

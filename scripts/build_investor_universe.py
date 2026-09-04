#!/usr/bin/env python3
"""Layer 1 — universe builder. Screens every 13F filer in the SEC bulk
"Form 13F Data Sets" for Buffett-style behaviour and writes
reference-data/investor-universe.json (see docs/CODEX-HANDOFF-2026-09.md §6).

Usage: python3 scripts/build_investor_universe.py <dataset_dir> [<dataset_dir> ...]
Each dataset_dir is an unzipped SEC window (SUBMISSION.tsv, COVERPAGE.tsv,
SUMMARYPAGE.tsv, INFOTABLE.tsv). Pass several windows (oldest..newest) to get
turnover and hold-duration; one window gives the static screen only.

Screen (defaults; all tunable at the top):
  positions 8..60, total value $300M..$60B, top-10 >= 50% of book,
  put/call rows < 5% of value, no bank/trust/pension/index/insurance names.
Tracked filers (reference-data/cik-map.json) are always kept and flagged.
Memory-light: streams INFOTABLE row by row (3-4M rows/window).
"""
from __future__ import annotations
import csv, json, re, sys, collections, statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reference-data" / "investor-universe.json"
CIKMAP = ROOT / "reference-data" / "cik-map.json"

MIN_POS, MAX_POS = 8, 60
MIN_VAL, MAX_VAL = 300e6, 60e9
MIN_TOP10 = 0.50
MAX_OPT_SHARE = 0.05
MAX_TURNOVER = 0.30          # avg (adds+exits)/positions per quarter, when history exists
EXCLUDE = re.compile(r"\b(BANK|BANCORP|TRUST CO|TRUST COMPANY|PENSION|RETIREMENT|INSURANCE|ASSURANCE|INDEX|QUANT|"
                     r"CAPITAL MARKETS|SECURITIES|BROKER|MUTUAL|ANNUITY|ENDOWMENT|FOUNDATION|UNIVERSITY|"
                     r"STATE OF|TREASURER|COUNTY|BOARD OF|NATIONAL ASSOCIATION|N\.A\.|FEDERAL|CREDIT UNION|"
                     r"WEALTH ADVISORS|WEALTH MANAGEMENT|FINANCIAL PLANNING|FINANCIAL SERVICES|LIFE)\b", re.I)

FUNDNAME = re.compile(r"(ISHARES|VANGUARD|SPDR|INVESCO EXCH|INVESCO QQQ|SSGA|DIREXION|PROSHARES|SELECT SECTOR|\bETF\b|INDEX F|TRUST SHS|MORGAN STANLEY ETF|JPMORGAN EQUITY PR|DIMENSIONAL)", re.I)

def read_tsv(path: Path):
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        yield from csv.DictReader(fh, delimiter="\t")

def load_tracked() -> dict[str, dict]:
    if not CIKMAP.exists(): return {}
    d = json.load(open(CIKMAP))
    rows = d if isinstance(d, list) else (d.get("investors") or list(d.values()))
    out = {}
    for r in rows:
        if isinstance(r, dict) and r.get("cik") is not None:
            out[str(r["cik"]).lstrip("0")] = r
    return out

def table_dir(d: Path) -> Path:
    """Some SEC zips unpack into a nested folder; find the one holding SUBMISSION.tsv."""
    if (d / "SUBMISSION.tsv").exists(): return d
    for sub in d.iterdir():
        if sub.is_dir() and (sub / "SUBMISSION.tsv").exists(): return sub
    raise FileNotFoundError(f"no SUBMISSION.tsv under {d}")

def scan_window(d: Path):
    """Return {(cik, period): stats} for original 13F-HR filings in this window."""
    d = table_dir(d)
    subs = {}
    for r in read_tsv(d / "SUBMISSION.tsv"):
        if r["SUBMISSIONTYPE"] not in ("13F-HR", "13F-HR/A"): continue
        subs[r["ACCESSION_NUMBER"]] = r
    cover = {r["ACCESSION_NUMBER"]: r for r in read_tsv(d / "COVERPAGE.tsv") if r["ACCESSION_NUMBER"] in subs}
    # one accession per (cik, period): prefer the original, else the latest amendment that restates
    chosen: dict[tuple, str] = {}
    for acc, s in subs.items():
        c = cover.get(acc, {})
        key = (s["CIK"].lstrip("0"), s["PERIODOFREPORT"])
        is_amend = s["SUBMISSIONTYPE"].endswith("/A")
        if is_amend and (c.get("AMENDMENTTYPE") or "").upper() != "RESTATEMENT": continue
        prev = chosen.get(key)
        if prev is None or (not is_amend) or subs[prev]["FILING_DATE"] < s["FILING_DATE"]:
            chosen[key] = acc
    acc2key = {acc: key for key, acc in chosen.items()}
    hold: dict[str, dict[str, float]] = collections.defaultdict(lambda: collections.defaultdict(float))
    optval: collections.Counter = collections.Counter()
    names: dict[str, dict[str, str]] = collections.defaultdict(dict)
    implied: dict[str, list[float]] = collections.defaultdict(list)   # value/share samples per filing
    for r in read_tsv(d / "INFOTABLE.tsv"):
        acc = r["ACCESSION_NUMBER"]
        if acc not in acc2key: continue
        try: v = float(r["VALUE"] or 0)
        except ValueError: continue
        if r.get("PUTCALL"):
            optval[acc] += v; continue
        cusip = r["CUSIP"].strip().upper()
        hold[acc][cusip] += v
        if cusip not in names[acc]: names[acc][cusip] = r["NAMEOFISSUER"]
        if (r.get("SSHPRNAMTTYPE") or "SH") == "SH" and len(implied[acc]) < 40:
            try:
                sh = float(r["SSHPRNAMT"] or 0)
                if sh > 0 and v > 0: implied[acc].append(v / sh)
            except ValueError: pass
    # A filing whose median implied share price is under $2 is still reporting in
    # thousands (Baupost does this in 2026). Scale it to dollars.
    for acc in list(hold):
        if implied[acc] and statistics.median(implied[acc]) < 2.0:
            for cu in hold[acc]: hold[acc][cu] *= 1000.0
            optval[acc] *= 1000.0
    out = {}
    for acc, key in acc2key.items():
        c = cover.get(acc, {})
        vals = sorted(hold[acc].values(), reverse=True)
        tot = sum(vals)
        if tot <= 0: continue
        top10 = sum(vals[:10]) / tot
        out[key] = {
            "cik": key[0], "period": key[1], "accession": acc,
            "name": (c.get("FILINGMANAGER_NAME") or "").strip(),
            "state": c.get("FILINGMANAGER_STATEORCOUNTRY", ""),
            "filing_date": subs[acc]["FILING_DATE"],
            "positions": len(vals), "total_value_usd": tot,
            "top10_pct": round(top10 * 100, 1), "top1_pct": round(vals[0] / tot * 100, 1),
            "options_pct": round(optval[acc] / (tot + optval[acc]) * 100, 2) if (tot + optval[acc]) else 0.0,
            "cusips": set(hold[acc].keys()),
            "values": dict(hold[acc]),
            "top_names": [names[acc][c] for c in sorted(hold[acc], key=lambda k: -hold[acc][k])[:5]],
        }
    return out

def period_key(p: str) -> str:   # '31-MAR-2026' -> '2026-03-31'
    try: return datetime.strptime(p, "%d-%b-%Y").strftime("%Y-%m-%d")
    except ValueError: return p

def main(dirs: list[str]) -> None:
    tracked = load_tracked()
    allq: dict[str, dict[str, dict]] = collections.defaultdict(dict)   # cik -> period -> stats
    for d in dirs:
        w = scan_window(Path(d))
        for (cik, per), st in w.items():
            allq[cik][period_key(per)] = st
        print(f"scanned {d}: {len(w)} filer-periods", file=sys.stderr)
    latest_period = max(p for c in allq.values() for p in c)
    # "Same mentality" signal: CUSIPs held by >=2 tracked filers at the latest period.
    tracked_hold: collections.Counter = collections.Counter()
    for cik, byq in allq.items():
        if cik in tracked and latest_period in byq:
            for cu in byq[latest_period]["cusips"]: tracked_hold[cu] += 1
    consensus_cusips = {cu for cu, n in tracked_hold.items() if n >= 2}
    rows = []
    for cik, byq in allq.items():
        if latest_period not in byq: continue
        st = byq[latest_period]
        periods = sorted(byq)
        # turnover + hold duration across the history we have
        churn, hold_q = [], None
        if len(periods) >= 2:
            for a, b in zip(periods, periods[1:]):
                A, B = byq[a]["cusips"], byq[b]["cusips"]
                churn.append((len(B - A) + len(A - B)) / max(1, len(B)))
            # median number of consecutive periods each current holding has been present
            spans = []
            for cu in st["cusips"]:
                n = 0
                for p in reversed(periods):
                    if cu in byq[p]["cusips"]: n += 1
                    else: break
                spans.append(n)
            hold_q = statistics.median(spans) if spans else None
        turnover = statistics.mean(churn) if churn else None
        is_tracked = cik in tracked
        name = st["name"]
        # share of this filer's book (by value) sitting in names >=2 tracked filers also own
        overlap_val = sum(v for cu, v in byq[latest_period]["values"].items() if cu in consensus_cusips)
        overlap_pct = round(overlap_val / st["total_value_usd"] * 100, 1) if st["total_value_usd"] else 0.0
        overlap_names = sum(1 for cu in st["cusips"] if cu in consensus_cusips)
        # self-dealing: top holding shares a distinctive word with the filer's own name
        fw = {w for w in re.findall(r"[A-Z]{4,}", name.upper()) if w not in ("CAPITAL","MANAGEMENT","PARTNERS","INVESTMENT","INVESTMENTS","ADVISORS","ADVISERS","GROUP","FUND","HOLDINGS","COMPANY","GLOBAL","ASSET","LLC","CORP","INC")}
        top1 = st["top_names"][0].upper() if st["top_names"] else ""
        self_dealing = any(w in top1 for w in fw)
        reasons = []
        if not (MIN_POS <= st["positions"] <= MAX_POS): reasons.append(f"positions {st['positions']}")
        if not (MIN_VAL <= st["total_value_usd"] <= MAX_VAL): reasons.append(f"value ${st['total_value_usd']/1e9:.1f}B")
        if st["top10_pct"] < MIN_TOP10 * 100: reasons.append(f"top10 {st['top10_pct']}%")
        if st["options_pct"] > MAX_OPT_SHARE * 100: reasons.append(f"options {st['options_pct']}%")
        if EXCLUDE.search(name): reasons.append("name pattern")
        if self_dealing: reasons.append("top holding is own vehicle")
        if sum(1 for n in st["top_names"] if FUNDNAME.search(n)) >= 3: reasons.append("ETF allocator")
        if turnover is not None and turnover > MAX_TURNOVER: reasons.append(f"turnover {turnover*100:.0f}%/q")
        passed = not reasons
        # 0-100 score: concentration 40, patience 40 (or neutral 20 if unknown), size-band 20
        conc = min(1.0, max(0.0, (st["top10_pct"] - 40) / 50)) * 25 + min(1.0, max(0.0, (60 - st["positions"]) / 50)) * 15
        pat = (min(1.0, max(0.0, (0.35 - turnover) / 0.30)) * 25 + min(1.0, (hold_q or 0) / 8) * 15) if turnover is not None else 20
        size = 20 if MIN_VAL <= st["total_value_usd"] <= MAX_VAL else (10 if st["total_value_usd"] > MAX_VAL else 0)
        score = round(conc + pat + size)
        if not passed and not is_tracked and (len(reasons) > 1 or "name pattern" in reasons or "ETF allocator" in reasons): continue   # keep near-misses only
        rows.append({
            "cik": cik, "name": name, "state": st["state"], "period": latest_period, "filing_date": st["filing_date"],
            "positions": st["positions"], "total_value_usd": round(st["total_value_usd"]),
            "top10_pct": st["top10_pct"], "top1_pct": st["top1_pct"], "options_pct": st["options_pct"],
            "turnover_q": round(turnover * 100, 1) if turnover is not None else None,
            "median_hold_q": hold_q, "history_periods": len(periods),
            "top_names": st["top_names"], "score": score,
            "overlap_pct": overlap_pct, "overlap_names": overlap_names,
            "fit": round(score * (0.4 + 0.6 * min(1.0, overlap_pct / 60))),
            "screen": "pass" if passed else "near-miss", "screen_notes": reasons,
            "tracked": is_tracked, "tracked_as": tracked[cik]["name"] if is_tracked else None,
            "status": "tracked" if is_tracked else "candidate",
        })
    rows.sort(key=lambda r: (-int(r["tracked"]), -r["fit"], -r["total_value_usd"]))
    OUT.write_text(json.dumps({
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "SEC Form 13F Data Sets (bulk) via scripts/build_investor_universe.py",
        "period": latest_period, "windows": [str(Path(d).name) for d in dirs],
        "screen": {"positions": [MIN_POS, MAX_POS], "value_usd": [MIN_VAL, MAX_VAL], "min_top10_pct": MIN_TOP10 * 100,
                   "max_options_pct": MAX_OPT_SHARE * 100, "max_turnover_q": MAX_TURNOVER * 100},
        "filers_scanned": sum(1 for c in allq.values() if latest_period in c),
        "candidates": rows,
    }, indent=1))
    n_pass = sum(1 for r in rows if r["screen"] == "pass" and not r["tracked"])
    print(f"period {latest_period}: {sum(1 for c in allq.values() if latest_period in c)} filers scanned, "
          f"{n_pass} new candidates pass, {sum(1 for r in rows if r['tracked'])} tracked found")
    print("\nTracked filers vs the screen:")
    for r in rows:
        if r["tracked"]:
            print(f"  {r['tracked_as']:26} {r['screen']:9} score {r['score']:3}  pos {r['positions']:4}  ${r['total_value_usd']/1e9:6.1f}B  top10 {r['top10_pct']:5.1f}%  {', '.join(r['screen_notes'])}")
    print("\nTop 40 new candidates by FIT (score x overlap with your tracked filers' books):")
    for r in [x for x in rows if not x["tracked"] and x["screen"] == "pass"][:40]:
        print(f"  fit {r['fit']:3} sc {r['score']:3} ovl {r['overlap_pct']:4.0f}%  {r['name'][:36]:36} {r['state']:3} pos {r['positions']:3} ${r['total_value_usd']/1e9:5.1f}B t/o {str(r['turnover_q'])+'%':>6}  {', '.join(n[:16] for n in r['top_names'][:3])}")

if __name__ == "__main__":
    main(sys.argv[1:] or ["/tmp/claude-0/-home-user-mose/5660ff5e-6a0c-546b-9acc-1f8b592bac9b/scratchpad/13f-bulk/2026q1"])

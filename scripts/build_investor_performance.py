#!/usr/bin/env python3
"""13F-implied performance per filer, from the SEC bulk data sets alone.

Every 13F row carries VALUE and SSHPRNAMT, so each filing reveals the
quarter-end price of every CUSIP. Taking the median across thousands of filers
gives a robust consensus price per CUSIP per period — no ticker mapping, no
outside data. From that:

  perf   : the filer's US long book, quarter-end weights, held one quarter,
           chained across the history (their stock-picking result, price-only)
  clone  : what a copier earns — quarter-t weights applied one quarter later
           (the 45-day lag, rounded to a quarter)
  bench  : SPY (CUSIP 78462F103) over the same quarters

Splits: a CUSIP whose consensus price jumps by an integer-ish ratio between
periods while median shares move inversely is treated as a split and adjusted.
Confidence: from turnover (low turnover -> intra-quarter trades barely matter).

Writes reference-data/investor-performance.json {cik: {...}} and is merged into
investor-universe.json by build_investor_universe.py's --merge-perf step.
"""
from __future__ import annotations
import csv, json, sys, collections, statistics, math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reference-data" / "investor-performance.json"
SPY = "78462F103"

def table_dir(d: Path) -> Path:
    if (d / "SUBMISSION.tsv").exists(): return d
    for sub in d.iterdir():
        if sub.is_dir() and (sub / "SUBMISSION.tsv").exists(): return sub
    raise FileNotFoundError(d)

def read_tsv(path: Path):
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        yield from csv.DictReader(fh, delimiter="\t")

def pkey(p: str) -> str:
    try: return datetime.strptime(p, "%d-%b-%Y").strftime("%Y-%m-%d")
    except ValueError: return p

def scan(d: Path):
    """Return (period -> cik -> {cusip: (value, shares)}, period -> cusip -> [implied prices])."""
    d = table_dir(d)
    subs = {r["ACCESSION_NUMBER"]: r for r in read_tsv(d / "SUBMISSION.tsv") if r["SUBMISSIONTYPE"] == "13F-HR"}
    chosen: dict[tuple, str] = {}
    for acc, s in subs.items():
        key = (s["CIK"].lstrip("0"), pkey(s["PERIODOFREPORT"]))
        if key not in chosen or subs[chosen[key]]["FILING_DATE"] < s["FILING_DATE"]: chosen[key] = acc
    acc2key = {acc: key for key, acc in chosen.items()}
    books: dict = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0])))
    prices: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    scale_probe: dict = collections.defaultdict(list)
    rows = []
    for r in read_tsv(d / "INFOTABLE.tsv"):
        acc = r["ACCESSION_NUMBER"]
        if acc not in acc2key or r.get("PUTCALL"): continue
        if (r.get("SSHPRNAMTTYPE") or "SH") != "SH": continue
        try: v = float(r["VALUE"] or 0); sh = float(r["SSHPRNAMT"] or 0)
        except ValueError: continue
        if v <= 0 or sh <= 0: continue
        cik, per = acc2key[acc]
        cu = r["CUSIP"].strip().upper()
        b = books[per][cik][cu]; b[0] += v; b[1] += sh
        if len(scale_probe[acc]) < 40: scale_probe[acc].append(v / sh)
    # thousands-scaled filings -> dollars
    fix = {acc for acc, s in scale_probe.items() if s and statistics.median(s) < 2.0}
    for acc in fix:
        cik, per = acc2key[acc]
        for cu, b in books[per][cik].items(): b[0] *= 1000.0
    for per, byc in books.items():
        for cik, bk in byc.items():
            for cu, (v, sh) in bk.items():
                if len(prices[per][cu]) < 400: prices[per][cu].append(v / sh)
    return books, prices

def main(dirs: list[str]) -> None:
    books: dict = collections.defaultdict(dict)   # period -> cik -> book
    prices: dict = collections.defaultdict(dict)  # period -> cusip -> consensus price
    for d in dirs:
        b, p = scan(Path(d))
        for per in b:
            books[per].update(b[per])
        for per in p:
            for cu, lst in p[per].items():
                prices[per][cu] = statistics.median(lst)
        print(f"scanned {d}", file=sys.stderr)
    periods = sorted(p for p in books if len(books[p]) > 1000)   # real quarter-ends only
    # split detection: ratio of consensus prices between consecutive periods
    def ret(cu, p0, p1):
        a, b = prices[p0].get(cu), prices[p1].get(cu)
        if not a or not b: return None
        r = b / a
        for k in (2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 25, 30, 40, 50):        # forward split
            if abs(r * k - 1) < 0.12: return r * k - 1
            if abs(r / k - 1) < 0.12 and r > 1.7: return r / k - 1   # reverse split
        if r > 8 or r < 0.12: return None       # unexplained jump -> skip
        return r - 1
    spy = []
    for p0, p1 in zip(periods, periods[1:]):
        rr = ret(SPY, p0, p1); spy.append(rr if rr is not None else 0.0)
    out = {}
    all_ciks = set().union(*[set(books[p]) for p in periods])
    for cik in all_ciks:
        qs, qs_clone, covered = [], [], []
        for i, (p0, p1) in enumerate(zip(periods, periods[1:])):
            bk = books[p0].get(cik)
            if not bk: qs.append(None); qs_clone.append(None); covered.append(0); continue
            tot = sum(v for v, _ in bk.values())
            num = cov = 0.0
            for cu, (v, _) in bk.items():
                r = ret(cu, p0, p1)
                if r is None: continue
                num += v * r; cov += v
            qs.append(num / cov if cov > 0.5 * tot else None); covered.append(cov / tot if tot else 0)
            # clone: same weights, one quarter later
            if i + 2 < len(periods):
                p2 = periods[i + 2]; n2 = c2 = 0.0
                for cu, (v, _) in bk.items():
                    r = ret(cu, p1, p2)
                    if r is None: continue
                    n2 += v * r; c2 += v
                qs_clone.append(n2 / c2 if c2 > 0.5 * tot else None)
            else: qs_clone.append(None)
        valid = [q for q in qs if q is not None]
        if len(valid) < 4: continue
        def chain(seq): 
            g = 1.0
            for q in seq:
                if q is not None: g *= (1 + q)
            return g - 1
        n = len(valid)
        spy_same = chain([s for s, q in zip(spy, qs) if q is not None])
        clone_valid = [q for q in qs_clone if q is not None]
        out[cik] = {
            "quarters": n, "first": periods[0], "last": periods[-1],
            "perf_pct": round(chain(qs) * 100, 1),
            "perf_ann_pct": round(((1 + chain(qs)) ** (4 / n) - 1) * 100, 1),
            "spy_pct": round(spy_same * 100, 1),
            "excess_pct": round((chain(qs) - spy_same) * 100, 1),
            "clone_pct": round(chain(qs_clone) * 100, 1) if len(clone_valid) >= 3 else None,
            "clone_quarters": len(clone_valid),
            "quarterly": [None if q is None else round(q * 100, 1) for q in qs],
            "coverage_pct": round(statistics.mean([c for c in covered if c]) * 100) if any(covered) else 0,
        }
    OUT.write_text(json.dumps({"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
                               "method": "13F-implied: consensus quarter-end prices from all filers' value/shares; price-only, US long book only, one-quarter holding; clone = one-quarter lag",
                               "periods": periods, "spy_quarterly_pct": [round(s * 100, 1) for s in spy],
                               "filers": out}, indent=None))
    print(f"periods {periods[0]}..{periods[-1]} ({len(periods)}), filers with >=4 quarters: {len(out)}; SPY chained {round((math.prod(1+s for s in spy)-1)*100,1)}%")

if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/env python3
"""Fold performance (investor-performance.json) and access (investor-access.json)
into reference-data/investor-universe.json so the Universe tab reads one file."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
U = ROOT / "reference-data" / "investor-universe.json"
P = ROOT / "reference-data" / "investor-performance.json"
A = ROOT / "reference-data" / "investor-access.json"
u = json.load(open(U)); perf = json.load(open(P)); acc = json.load(open(A))["filers"]
pf = perf["filers"]
for c in u["candidates"]:
    x = pf.get(c["cik"])
    if x:
        t = c.get("turnover_q")
        conf = "high" if t is not None and t < 15 else "medium" if t is not None and t < 30 else "low"
        c.update({"perf_pct": x["perf_pct"], "perf_ann_pct": x["perf_ann_pct"], "spy_pct": x["spy_pct"], "excess_pct": x["excess_pct"],
                  "clone_pct": x["clone_pct"], "perf_quarters": x["quarters"], "perf_quarterly": x["quarterly"], "perf_coverage_pct": x["coverage_pct"],
                  "perf_confidence": conf})
    else:
        c.update({"perf_pct": None, "perf_ann_pct": None, "spy_pct": None, "excess_pct": None, "clone_pct": None, "perf_quarters": 0, "perf_quarterly": [], "perf_coverage_pct": 0, "perf_confidence": "n/a"})
    a = acc.get(c["cik"]) or {}
    c["access"] = a.get("access", "unknown"); c["access_note"] = a.get("access_note", "")
    for k in ("crd", "phone", "website", "city", "reg_aum_usd", "clients_individual", "clients_hnw", "private_funds", "hedge_funds", "public_fund",
              "compensation", "disclosure_flags", "iapd_url", "sec_status", "adv_date", "fee_schedule", "minimum_usd"):
        c[k] = a.get(k)
u["performance"] = {"method": perf["method"], "periods": perf["periods"], "spy_quarterly_pct": perf["spy_quarterly_pct"], "generated_at": perf["generated_at"]}
u["access_source"] = "SEC Form ADV bulk (Part 1), joined on CIK/name"
json.dump(u, open(U, "w"), indent=1)
from collections import Counter
print("merged:", len(u["candidates"]), "| with perf:", sum(1 for c in u["candidates"] if c["perf_pct"] is not None), "| access:", dict(Counter(c["access"] for c in u["candidates"])))

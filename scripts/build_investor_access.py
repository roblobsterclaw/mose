#!/usr/bin/env python3
"""Join the investor universe to SEC Form ADV bulk data (registered + exempt
advisers) and classify how each filer could actually work for Joe.

Sources: SEC "Information About Registered Investment Advisers and Exempt
Reporting Advisers" monthly CSVs (Form ADV Part 1). Join on CIK# (the bulk
file carries it), fallback exact normalised name.

Per filer: CRD, SEC status, latest ADV date, phone, website, city/state,
regulatory AUM, client counts by type (individuals, high-net-worth, pooled
vehicles, pensions...), compensation types (asset-based / performance /
commissions), services (portfolio management for individuals), private funds
(count, hedge funds, gross assets), disclosure flags (Item 11).

access classification:
  SMA-open       : takes individual / HNW clients AND offers portfolio mgmt for individuals
  private-fund   : advises private funds, no individual clients
  institutional  : clients are institutions/pensions/other advisers only
  exempt-reporting: files as ERA (private fund/VC adviser, no retail)
  not-an-adviser : no ADV match (holding company, family office, foreign fund, bank)

Fees and minimums live in Part 2A brochures (PDF) — added separately.
Writes reference-data/investor-access.json {cik: {...}}.
"""
from __future__ import annotations
import csv, json, re, glob, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "reference-data" / "investor-universe.json"
OUT = ROOT / "reference-data" / "investor-access.json"
ADV_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/claude-0/-home-user-mose/5660ff5e-6a0c-546b-9acc-1f8b592bac9b/scratchpad/adv")

def norm(s: str) -> str:
    s = re.sub(r"[^A-Z0-9 ]", " ", (s or "").upper())
    s = re.sub(r"\b(LLC|L L C|LP|L P|LLP|INC|LTD|LIMITED|CO|CORP|CORPORATION|MANAGEMENT|CAPITAL|PARTNERS|ADVISORS|ADVISERS|INVESTMENT|INVESTMENTS|ASSET|GROUP|THE|COMPANY|HOLDINGS|FUND|FUNDS|MGMT|II|III)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def num(x):
    try: return float(str(x).replace(",", "").replace("$", "")) if str(x).strip() not in ("", "N", "Y") else 0.0
    except ValueError: return 0.0

def load_adv(kind: str):
    rows = {}
    for f in glob.glob(str(ADV_DIR / kind / "*.CSV")):
        with open(f, encoding="latin-1", newline="") as fh:
            for r in csv.DictReader(fh):
                r["_kind"] = kind
                rows[r["Organization CRD#"]] = r
    return rows

def main():
    reg, era = load_adv("registered"), load_adv("exempt")
    by_cik, by_name = {}, {}
    for r in list(reg.values()) + list(era.values()):
        for c in re.split(r"[;,\s]+", (r.get("CIK#") or "").strip()):
            c = c.lstrip("0")
            if c and c not in by_cik: by_cik[c] = r
        for n in (r.get("Primary Business Name"), r.get("Legal Name")):
            k = norm(n)
            if k and k not in by_name: by_name[k] = r
    uni = json.load(open(UNIVERSE))
    out, stats = {}, {"cik": 0, "name": 0, "none": 0}
    for c in uni["candidates"]:
        r = by_cik.get(c["cik"])
        how = "cik"
        if not r:
            r = by_name.get(norm(c["name"])); how = "name" if r else "none"
        stats[how] += 1
        if not r:
            out[c["cik"]] = {"matched": None, "access": "not-an-adviser", "access_note": "No Form ADV on file — holding company, family office, bank, or non-US fund. Not available as an adviser."}
            continue
        g = lambda k: (r.get(k) or "").strip()
        # 5D(x)(1) = number of clients of type x; 5D(1)(x) = Y/N checkbox (older form); use count, fall back to flag
        def cnt(letter):
            n = num(g(f"5D({letter})(1)"))
            return n if n else (1.0 if g(f"5D(1)({letter})") == "Y" else 0.0)
        ind = cnt("a"); hnw = cnt("b"); pooled = cnt("f"); pension = cnt("g"); ric = cnt("d")
        inst = cnt("c") + ric + cnt("e") + pension + cnt("h") + cnt("i") + cnt("j") + cnt("k") + cnt("l")
        pm_individuals = g("5G(2)") == "Y"
        public_fund = g("5G(3)") == "Y" or ric > 0   # runs a registered fund (mutual fund / ETF) you could buy
        pf = num(g("Count of Private Funds - 7B(1)")); hf = num(g("Total number of Hedge funds"))
        aum = num(g("5F(2)(c)")) or num(g("5F(2)(a)"))
        comp = [lbl for k, lbl in [("5E(1)", "% of AUM"), ("5E(2)", "hourly"), ("5E(3)", "subscription"), ("5E(4)", "fixed"), ("5E(5)", "commissions"), ("5E(6)", "performance fee"), ("5E(7)", "other")] if g(k) == "Y"]
        disclosures = sum(1 for k in r if k.startswith("Count of 11") and num(r[k]) > 0)
        if r["_kind"] == "exempt": access, note = "exempt-reporting", "Exempt reporting adviser (private funds / VC only). No retail accounts."
        elif (ind + hnw) > 0 and pm_individuals: access, note = "SMA-open", f"Takes individual clients: {int(ind + hnw)} individual/HNW accounts on file. Offers portfolio management for individuals."
        elif pf > 0 and (ind + hnw) == 0: access, note = "private-fund", f"Advises {int(pf)} private fund{'s' if pf != 1 else ''}{' (' + str(int(hf)) + ' hedge)' if hf else ''}; no individual accounts on file — you'd invest in the fund, if open."
        elif (ind + hnw) > 0: access, note = "SMA-possible", f"{int(ind + hnw)} individual/HNW clients on file but portfolio management for individuals not ticked — ask."
        else: access, note = "institutional", "Institutional and pooled clients only on file."
        out[c["cik"]] = {
            "matched": how, "crd": g("Organization CRD#"), "sec_number": g("SEC#"), "kind": r["_kind"], "sec_status": g("SEC Current Status"),
            "adv_date": g("Latest ADV Filing Date"), "legal_name": g("Legal Name"), "phone": g("Main Office Telephone Number"),
            "website": g("Website Address").split(",")[0].strip(), "city": g("Main Office City"), "state": g("Main Office State"), "country": g("Main Office Country"),
            "reg_aum_usd": aum, "clients_individual": int(ind), "clients_hnw": int(hnw), "clients_pooled": int(pooled), "clients_pension": int(pension), "clients_institutional": int(inst),
            "pm_for_individuals": pm_individuals, "public_fund": public_fund, "clients_registered_funds": int(ric), "private_funds": int(pf), "hedge_funds": int(hf), "pf_gross_assets_usd": num(g("Total Gross Assets of Private Funds")),
            "compensation": comp, "disclosure_flags": disclosures, "iapd_url": f"https://adviserinfo.sec.gov/firm/summary/{g('Organization CRD#')}",
            "access": access, "access_note": note, "fee_schedule": None, "minimum_usd": None,
        }
    OUT.write_text(json.dumps({"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "source": "SEC Form ADV bulk CSV (registered + exempt), joined on CIK then name", "filers": out}, indent=1))
    from collections import Counter
    print("matched:", stats, "| access:", dict(Counter(v["access"] for v in out.values())))
    for c in uni["candidates"][:60]:
        v = out[c["cik"]]
        if v.get("matched"): print(f"  {c['name'][:34]:34} {v['access']:16} ind/hnw {v['clients_individual']}/{v['clients_hnw']:<5} PF {v['private_funds']:<3} RIC {v['clients_registered_funds']:<2} AUM ${v['reg_aum_usd']/1e9:5.1f}B  {v['phone'][:15]:15} {v['website'][:30]}")
        else: print(f"  {c['name'][:34]:34} {v['access']}")

if __name__ == "__main__":
    main()

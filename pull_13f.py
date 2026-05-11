#!/usr/bin/env python3
"""Pull recent 13F filings from SEC EDGAR and rebuild MOSE convergence data.

This script is intentionally conservative: it only writes data parsed from SEC
filings and preserves existing records for investors that cannot be refreshed.
Create reference-data/cik-map.json with investor CIKs before running a full pull.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent
REFERENCE_DIR = ROOT / "reference-data"
MASTER_PATH = REFERENCE_DIR / "convergence-master.json"
CIK_MAP_PATH = REFERENCE_DIR / "cik-map.json"
TICKER_MAP_PATH = REFERENCE_DIR / "ticker-map.json"
SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
USER_AGENT = "MOSE Dashboard joe@example.com"


@dataclass(frozen=True)
class InvestorConfig:
    name: str
    fund: str
    tier: int
    cik: str


def request_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/xml,text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=False)
        handle.write("\n")
    tmp.replace(path)


def load_cik_map() -> list[InvestorConfig]:
    raw = load_json(CIK_MAP_PATH, [])
    configs: list[InvestorConfig] = []
    for item in raw:
        cik = str(item.get("cik", "")).strip().lstrip("0")
        if not cik:
            continue
        configs.append(
            InvestorConfig(
                name=str(item["name"]),
                fund=str(item.get("fund", item["name"])),
                tier=int(item.get("tier", 1)),
                cik=cik,
            )
        )
    return configs


def load_ticker_map() -> dict[str, str]:
    raw = load_json(TICKER_MAP_PATH, {})
    return {str(key).upper().strip(): str(value).upper().strip() for key, value in raw.items() if value}


def search_latest_13f(cik: str, start_date: str) -> dict[str, Any] | None:
    params = urllib.parse.urlencode(
        {
            "q": f'"{cik}"',
            "dateRange": "custom",
            "startdt": start_date,
            "forms": "13F-HR",
        }
    )
    data = request_json(f"{SEC_SEARCH_URL}?{params}")
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        return None
    hits.sort(key=lambda hit: hit.get("_source", {}).get("file_date", ""), reverse=True)
    return hits[0].get("_source", {})


def filing_index_url(cik: str, accession: str) -> str:
    accession_clean = accession.replace("-", "")
    return f"{SEC_ARCHIVES_URL}/{cik}/{accession_clean}/index.json"


def find_information_table_url(cik: str, accession: str) -> str | None:
    index = request_json(filing_index_url(cik, accession))
    items = index.get("directory", {}).get("item", [])
    accession_clean = accession.replace("-", "")
    for item in items:
        name = item.get("name", "")
        lower = name.lower()
        if lower.endswith(".xml") and ("infotable" in lower or "form13f" in lower or "primary_doc" not in lower):
            return f"{SEC_ARCHIVES_URL}/{cik}/{accession_clean}/{name}"
    return None


def text_of(node: ElementTree.Element, local_name: str) -> str:
    for child in node.iter():
        if child.tag.split("}")[-1] == local_name and child.text:
            return child.text.strip()
    return ""


def parse_information_table(xml_text: str, ticker_map: dict[str, str]) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(xml_text)
    holdings: list[dict[str, Any]] = []
    for info in root.iter():
        if info.tag.split("}")[-1] != "infoTable":
            continue
        issuer = text_of(info, "nameOfIssuer")
        cusip = text_of(info, "cusip").upper()
        ticker = ticker_map.get(cusip) or ticker_map.get(issuer.upper())
        value_thousands = float(text_of(info, "value") or 0)
        shares = float(text_of(info, "sshPrnamt") or 0)
        holdings.append(
            {
                "ticker": ticker,
                "cusip": cusip,
                "company": issuer,
                "value": value_thousands * 1000,
                "shares": shares,
            }
        )
    return holdings


def build_investor_record(config: InvestorConfig, filing: dict[str, Any], holdings: list[dict[str, Any]]) -> dict[str, Any]:
    total_value = sum(item["value"] for item in holdings)
    enriched = []
    for item in holdings:
        pct = (item["value"] / total_value * 100) if total_value else 0
        enriched.append({**item, "pct": round(pct, 2)})
    enriched.sort(key=lambda item: item["value"], reverse=True)
    return {
        "name": config.name,
        "fund": config.fund,
        "tier": config.tier,
        "filing_date": filing.get("file_date"),
        "accession": filing.get("adsh") or filing.get("accession_number"),
        "cik": config.cik,
        "total_value": total_value,
        "num_holdings": len(enriched),
        "top_10": enriched[:10],
        "source": "SEC EDGAR 13F-HR",
    }


def score_for_holder(tier: int, is_top5: bool) -> int:
    base = 20 if tier == 1 else 10 if tier == 2 else 5
    return base + (10 if is_top5 else 0)


def build_convergence(investors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_ticker: dict[str, dict[str, Any]] = {}
    for investor in investors:
        top = investor.get("top_10", [])
        for holding in top:
            identifier = holding.get("ticker") or f"CUSIP:{holding.get('cusip', '')}"
            if not identifier or identifier == "CUSIP:":
                continue
            entry = by_ticker.setdefault(
                identifier,
                {
                    "ticker": identifier,
                    "cusip": holding.get("cusip"),
                    "company": holding.get("company", identifier),
                    "convergence_score": 0,
                    "total_investor_count": 0,
                    "tier1_count": 0,
                    "tier2_count": 0,
                    "tier3_count": 0,
                    "total_conviction_pct": 0,
                    "total_value_held": 0,
                    "top5_bonus_count": 0,
                    "investors": [],
                },
            )
            is_top5 = top.index(holding) < 5
            tier = int(investor.get("tier", 1))
            pct = float(holding.get("pct", 0))
            entry["convergence_score"] += score_for_holder(tier, is_top5)
            entry["total_investor_count"] += 1
            entry[f"tier{min(tier, 3)}_count"] += 1
            entry["total_conviction_pct"] += pct
            entry["total_value_held"] += float(holding.get("value", 0))
            entry["top5_bonus_count"] += 1 if is_top5 else 0
            entry["investors"].append(
                {
                    "name": investor.get("name"),
                    "fund": investor.get("fund"),
                    "tier": tier,
                    "shares": holding.get("shares"),
                    "value": holding.get("value"),
                    "pct_of_portfolio": pct,
                    "is_top5": is_top5,
                }
            )
    return sorted(by_ticker.values(), key=lambda item: (item["convergence_score"], item["total_conviction_pct"]), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh MOSE 13F convergence data from SEC EDGAR.")
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    existing = load_json(MASTER_PATH, {})
    configs = load_cik_map()
    ticker_map = load_ticker_map()
    if not configs:
        print(
            "No CIK map found. Create reference-data/cik-map.json with entries like "
            '{"name":"Warren Buffett","fund":"Berkshire Hathaway","tier":1,"cik":"1067983"}.',
            file=sys.stderr,
        )
        return 2

    refreshed: list[dict[str, Any]] = []
    failed: list[str] = []
    for config in configs:
        try:
            print(f"Pulling {config.name} ({config.cik})...")
            filing = search_latest_13f(config.cik, args.start_date)
            if not filing:
                raise RuntimeError("No 13F-HR filing found")
            accession = filing.get("adsh") or filing.get("accession_number")
            if not accession:
                raise RuntimeError("SEC search result did not include an accession number")
            table_url = find_information_table_url(config.cik, accession)
            if not table_url:
                raise RuntimeError("Could not locate information table XML")
            holdings = parse_information_table(request_text(table_url), ticker_map)
            refreshed.append(build_investor_record(config, filing, holdings))
            time.sleep(0.25)
        except (urllib.error.URLError, RuntimeError, ElementTree.ParseError, KeyError, ValueError) as exc:
            print(f"Failed: {config.name}: {exc}", file=sys.stderr)
            failed.append(config.name)

    if not refreshed:
        print("No investors refreshed; existing convergence file was not modified.", file=sys.stderr)
        return 1

    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "sprint": "MOSE SEC EDGAR refresh",
        "investors_pulled": len(refreshed),
        "investors_failed": len(failed),
        "total_unique_stocks": 0,
        "investors": refreshed,
        "convergence_rankings": build_convergence(refreshed),
        "failed_investor_names": failed,
    }
    output["total_unique_stocks"] = len(output["convergence_rankings"])

    if args.dry_run:
        print(json.dumps(output, indent=2)[:4000])
        return 0

    backup = MASTER_PATH.with_suffix(f".json.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    if MASTER_PATH.exists():
        backup.write_text(MASTER_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    write_json(MASTER_PATH, output)
    print(f"Wrote {MASTER_PATH}")
    print(f"Backup: {backup if backup.exists() else 'none'}")
    print(f"Refreshed {len(refreshed)} investors; failed {len(failed)}")
    if existing:
        print("Existing file was replaced only after a successful refresh.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

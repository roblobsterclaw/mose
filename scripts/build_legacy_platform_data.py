#!/usr/bin/env python3
"""Build fallback JSON files used by the original MOSE platform UI.

The clean MOSE dashboard expects root-level JSON files. This script derives a
conservative set from the current convergence master so the original platform
layout can run on GitHub Pages without fabricating research conclusions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "reference-data" / "convergence-master.json"


def load_master() -> dict:
    return json.loads(MASTER.read_text(encoding="utf-8"))


def build_holdings(master: dict) -> dict:
    rankings = master.get("convergence_rankings", [])
    by_ticker = {str(r.get("ticker", "")).upper(): r for r in rankings}
    holdings = []
    for ranking in rankings:
        ticker = str(ranking.get("ticker", "")).upper()
        for investor in ranking.get("investors", []):
            holdings.append(
                {
                    "ticker": ticker,
                    "company": ranking.get("company") or ticker,
                    "investor": investor.get("name") or "Unknown",
                    "fund": investor.get("fund") or "",
                    "pct_portfolio": investor.get("pct_of_portfolio"),
                    "current_price": None,
                    "entry_quarter": None,
                    "entry_price": None,
                    "entry_price_45d": None,
                    "unrealized_pct": None,
                    "pct_change_since_entry": None,
                    "trend": "HOLDING",
                    "hold_duration": None,
                    "conviction": min(int(ranking.get("total_investor_count") or 1), 5),
                    "convergence": int(ranking.get("total_investor_count") or 1),
                    "convergence_score": ranking.get("convergence_score") or 0,
                    "reported_value": investor.get("value"),
                    "shares": investor.get("shares"),
                }
            )
    return {
        "generated_at": master.get("generated") or datetime.now(timezone.utc).isoformat(),
        "source": "reference-data/convergence-master.json",
        "holdings": holdings,
        "summary": {
            "unique_stocks": len(by_ticker),
            "holdings": len(holdings),
        },
    }


def build_dcf(master: dict) -> dict:
    rows = []
    for ranking in master.get("convergence_rankings", []):
        ticker = str(ranking.get("ticker", "")).upper()
        rows.append(
            {
                "ticker": ticker,
                "company": ranking.get("company") or ticker,
                "current_price": None,
                "bear_iv": None,
                "base_iv": None,
                "bull_iv": None,
                "base_mos": None,
                "graham_number": None,
                "owner_earnings_billions": None,
                "revenue_cagr_pct": None,
                "maintenance_capex_pct": None,
                "signal": "NO DATA",
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "placeholder from convergence universe; valuation engine not loaded",
        "valuations": rows,
    }


def build_indices() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "indices": [
            {"name": "S&P 500", "price": 0, "change_pct": 0, "vs_exit": None},
            {"name": "Dow Jones", "price": 0, "change_pct": 0, "vs_exit": None},
            {"name": "NASDAQ", "price": 0, "change_pct": 0, "vs_exit": None},
            {"name": "Russell 2000", "price": 0, "change_pct": 0, "vs_exit": None},
            {"name": "VIX", "price": 0, "change_pct": 0, "vs_exit": None},
        ],
    }


def build_joes_holdings() -> dict:
    return {
        "as_of": "2026-05-11",
        "total_value": 0,
        "summary": {
            "by_category": {},
            "top_equity_positions": [],
        },
        "accounts": [],
        "note": "Brokerage statement data not loaded into this repo yet.",
    }


def build_research_library() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reports": [],
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path.name}")


def main() -> int:
    master = load_master()
    write_json(ROOT / "holdings-latest.json", build_holdings(master))
    write_json(ROOT / "dcf-latest.json", build_dcf(master))
    write_json(ROOT / "indices-latest.json", build_indices())
    write_json(ROOT / "joes-holdings.json", build_joes_holdings())
    write_json(ROOT / "research-library.json", build_research_library())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

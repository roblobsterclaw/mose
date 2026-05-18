#!/usr/bin/env python3
"""Build the MOSE 13F tracker export used by the static dashboard.

The current holdings feed already carries SEC-derived investor positions. This
export reshapes that data into an investor/quarter/change view so the UI can
show what changed now, and later consume the same shape from SQLite/Supabase.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOLDINGS_PATH = ROOT / "holdings-latest.json"
OUTPUT_PATH = ROOT / "filing-changes-latest.json"
CIK_MAP_PATH = ROOT / "reference-data" / "cik-map.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    tmp.replace(path)


def quarter_sort_key(value: str | None) -> tuple[int, int]:
    if not value or "-Q" not in value:
        return (0, 0)
    year, quarter = value.split("-Q", 1)
    try:
        return (int(year), int(quarter))
    except ValueError:
        return (0, 0)


def prior_quarter(value: str | None) -> str | None:
    year, quarter = quarter_sort_key(value)
    if not year or not quarter:
        return None
    if quarter == 1:
        return f"{year - 1}-Q4"
    return f"{year}-Q{quarter - 1}"


def change_type(holding: dict[str, Any], latest_quarter: str | None) -> str:
    trend = str(holding.get("trend") or "").upper()
    entry_quarter = holding.get("entry_quarter")
    if entry_quarter == latest_quarter or trend == "NEW":
        return "new"
    if trend == "ADDING":
        return "add"
    if trend == "TRIMMING":
        return "trim"
    if trend == "EXITED":
        return "exit"
    return "hold"


def pct_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build() -> dict[str, Any]:
    source = load_json(HOLDINGS_PATH, {})
    holdings = source.get("holdings") or []
    latest_quarter = source.get("latest_quarter") or "Unknown"
    previous_quarter = prior_quarter(latest_quarter) or "Prior quarter"
    cik_registry = {item.get("name"): item for item in load_json(CIK_MAP_PATH, []) if item.get("name")}

    by_investor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    changes: list[dict[str, Any]] = []

    for holding in holdings:
        investor = holding.get("investor") or "Unknown"
        ticker = holding.get("ticker") or "UNKNOWN"
        ctype = change_type(holding, latest_quarter)
        row = {
            "ticker": ticker,
            "company": holding.get("company") or ticker,
            "investor": investor,
            "fund": holding.get("fund") or "",
            "quarter": latest_quarter,
            "previous_quarter": previous_quarter,
            "change_type": ctype,
            "trend": holding.get("trend") or "HOLDING",
            "shares": holding.get("shares"),
            "market_value": holding.get("value_usd") or holding.get("reported_value"),
            "pct_portfolio": holding.get("pct_portfolio"),
            "rank": None,
            "filing_date": holding.get("filing_date"),
            "source": holding.get("data_source") or "13F-HR (SEC EDGAR)",
            "convergence": holding.get("convergence") or 1,
        }
        by_investor[investor].append(row)
        by_ticker[ticker].append(row)
        if ctype != "hold":
            changes.append(row)

    investor_summaries = []
    for investor, rows in by_investor.items():
        rows.sort(key=lambda r: pct_float(r.get("pct_portfolio")), reverse=True)
        total_value = sum(pct_float(r.get("market_value")) for r in rows)
        registry = cik_registry.get(investor, {})
        counts = defaultdict(int)
        for row in rows:
            counts[row["change_type"]] += 1
        for rank, row in enumerate(rows, start=1):
            row["rank"] = rank
        investor_summaries.append(
            {
                "name": investor,
                "fund": rows[0].get("fund") or registry.get("fund") or "",
                "cik": registry.get("cik"),
                "tier": registry.get("tier", 1),
                "source_type": registry.get("source_type", "13F"),
                "latest_quarter": latest_quarter,
                "previous_quarter": previous_quarter,
                "filing_date": rows[0].get("filing_date"),
                "total_positions": len(rows),
                "total_value": total_value,
                "new_positions": counts["new"],
                "adds": counts["add"],
                "trims": counts["trim"],
                "exits": counts["exit"],
                "positions": rows,
                "top_positions": rows[:10],
            }
        )

    ticker_summaries = []
    for ticker, rows in by_ticker.items():
        rows.sort(key=lambda r: (r["change_type"] != "hold", pct_float(r.get("pct_portfolio"))), reverse=True)
        add_like = [r for r in rows if r["change_type"] in {"new", "add"}]
        trim_like = [r for r in rows if r["change_type"] in {"trim", "exit"}]
        ticker_summaries.append(
            {
                "ticker": ticker,
                "company": rows[0].get("company") or ticker,
                "investor_count": len({r["investor"] for r in rows}),
                "buyers": len({r["investor"] for r in add_like}),
                "sellers": len({r["investor"] for r in trim_like}),
                "total_value": sum(pct_float(r.get("market_value")) for r in rows),
                "changes": rows,
            }
        )

    changes.sort(
        key=lambda r: (
            {"new": 4, "add": 3, "trim": 2, "exit": 1}.get(r["change_type"], 0),
            pct_float(r.get("pct_portfolio")),
        ),
        reverse=True,
    )
    investor_summaries.sort(key=lambda r: (r["new_positions"] + r["adds"] + r["trims"] + r["exits"], r["total_positions"]), reverse=True)
    ticker_summaries.sort(key=lambda r: (r["buyers"], r["investor_count"], r["total_value"]), reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(HOLDINGS_PATH.name),
        "latest_quarter": latest_quarter,
        "previous_quarter": previous_quarter,
        "note": "Change classifications use available MOSE trend fields until full quarter-by-quarter EDGAR history is populated.",
        "investor_count": len(investor_summaries),
        "holding_count": len(holdings),
        "change_count": len(changes),
        "investors": investor_summaries,
        "changes": changes,
        "tickers": ticker_summaries,
    }


def main() -> int:
    if not HOLDINGS_PATH.exists():
        raise SystemExit(f"Missing {HOLDINGS_PATH}")
    output = build()
    write_json(OUTPUT_PATH, output)
    print(f"Wrote {OUTPUT_PATH} with {output['investor_count']} investors and {output['change_count']} changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

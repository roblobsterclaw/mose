#!/usr/bin/env python3
"""Sync the generated MOSE 13F tracker export into Supabase/PostgREST.

Required env vars:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACKER_PATH = ROOT / "filing-changes-latest.json"


class SupabaseClient:
    def __init__(self, url: str, key: str) -> None:
        self.base = url.rstrip("/") + "/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates",
        }

    def upsert(self, table: str, rows: list[dict[str, Any]], conflict: str) -> list[dict[str, Any]]:
        if not rows:
            return []
        query = urllib.parse.urlencode({"on_conflict": conflict})
        req = urllib.request.Request(
            f"{self.base}/{table}?{query}",
            data=json.dumps(rows).encode("utf-8"),
            headers=self.headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8") or "[]")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Supabase upsert failed for {table}: HTTP {exc.code}: {body}") from exc


def load_tracker() -> dict[str, Any]:
    with TRACKER_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

    tracker = load_tracker()
    client = SupabaseClient(url, key)

    investors_payload = [
        {
            "name": inv["name"],
            "fund": inv.get("fund"),
            "tier": inv.get("tier") or 1,
            "source_type": inv.get("source_type") or "13F",
            "cik": inv.get("cik"),
            "status": "active",
        }
        for inv in tracker.get("investors", [])
    ]
    investor_rows = client.upsert("investors", investors_payload, "name")
    investor_ids = {row["name"]: row["id"] for row in investor_rows}

    securities_payload = []
    seen_tickers = set()
    for item in tracker.get("tickers", []):
        ticker = str(item.get("ticker") or "").upper()
        if not ticker or ticker in seen_tickers:
            continue
        seen_tickers.add(ticker)
        securities_payload.append(
            {
                "ticker": ticker,
                "company": item.get("company") or ticker,
                "display_name": item.get("company") or ticker,
                "asset_type": "equity",
                "active": True,
            }
        )
    security_rows = client.upsert("securities", securities_payload, "ticker")
    security_ids = {row["ticker"]: row["id"] for row in security_rows}

    changes_payload = []
    quarter = tracker.get("latest_quarter")
    previous_quarter = tracker.get("previous_quarter")
    for change in tracker.get("changes", []):
        investor_id = investor_ids.get(change.get("investor"))
        security_id = security_ids.get(str(change.get("ticker") or "").upper())
        if not investor_id or not security_id:
            continue
        changes_payload.append(
            {
                "investor_id": investor_id,
                "security_id": security_id,
                "quarter": quarter,
                "previous_quarter": previous_quarter,
                "change_type": change.get("change_type") or "hold",
                "shares_current": change.get("shares"),
                "market_value_current": change.get("market_value"),
                "pct_portfolio_current": change.get("pct_portfolio"),
                "source": "filing-changes-latest.json",
            }
        )
    client.upsert("holding_changes", changes_payload, "investor_id,security_id,quarter,source")
    print(
        "Synced 13F tracker to Supabase: "
        f"{len(investor_ids)} investors, {len(security_ids)} securities, {len(changes_payload)} changes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

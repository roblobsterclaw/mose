#!/usr/bin/env python3
"""MOSE local truth-store tooling.

SQLite is the source of truth for filings, holdings, rankings, portfolio lots,
signals, and audit events. The static dashboard still reads JSON exported from
this database so GitHub Pages remains simple.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "mose.db"
SCHEMA_PATH = ROOT / "db" / "schema.sql"
DEFAULT_IMPORT_PATH = ROOT / "reference-data" / "convergence-master.json"
DEFAULT_EXPORT_PATH = ROOT / "reference-data" / "convergence-master.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(args: argparse.Namespace) -> None:
    with connect(args.db) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    print(f"Initialized {args.db}")


def upsert_security(conn: sqlite3.Connection, ticker: str, company: str | None = None, cusip: str | None = None) -> int:
    normalized = (ticker or "").strip().upper()
    if not normalized:
        raise ValueError("Cannot upsert security without a ticker or identifier")
    conn.execute(
        """
        INSERT INTO securities (ticker, company, cusip, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(ticker) DO UPDATE SET
          company = COALESCE(excluded.company, securities.company),
          cusip = COALESCE(excluded.cusip, securities.cusip),
          updated_at = CURRENT_TIMESTAMP
        """,
        (normalized, company, cusip),
    )
    return int(conn.execute("SELECT id FROM securities WHERE ticker = ?", (normalized,)).fetchone()["id"])


def upsert_investor(conn: sqlite3.Connection, item: dict[str, Any]) -> int:
    name = str(item.get("name") or "").strip()
    if not name:
        raise ValueError("Cannot upsert investor without a name")
    conn.execute(
        """
        INSERT INTO investors (name, fund, tier, cik, source_type, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(name) DO UPDATE SET
          fund = COALESCE(excluded.fund, investors.fund),
          tier = excluded.tier,
          cik = COALESCE(excluded.cik, investors.cik),
          source_type = excluded.source_type,
          updated_at = CURRENT_TIMESTAMP
        """,
        (
            name,
            item.get("fund"),
            int(item.get("tier") or 1),
            item.get("cik"),
            item.get("source") or "13F",
        ),
    )
    return int(conn.execute("SELECT id FROM investors WHERE name = ?", (name,)).fetchone()["id"])


def filing_key(investor: dict[str, Any], investor_id: int) -> tuple[int, str, str]:
    source = str(investor.get("source") or "convergence-master.json")
    accession = str(investor.get("accession") or f"snapshot:{investor.get('filing_date') or 'unknown'}:{investor_id}")
    return investor_id, source, accession


def import_snapshot(args: argparse.Namespace) -> None:
    path = args.input
    data = json.loads(path.read_text(encoding="utf-8"))
    generated = data.get("generated") or utc_now()
    investors = data.get("investors") if isinstance(data.get("investors"), list) else list((data.get("investors") or {}).values())
    rankings = data.get("convergence_rankings") or []

    with connect(args.db) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO source_events (source, event_type, status, summary, payload) VALUES (?, ?, ?, ?, ?)",
            (
                str(path),
                "import_snapshot",
                "started",
                f"Importing snapshot generated {generated}",
                json.dumps({"generated": generated, "sprint": data.get("sprint")}),
            ),
        )

        for investor in investors:
            investor_id = upsert_investor(conn, investor)
            key = filing_key(investor, investor_id)
            conn.execute(
                """
                INSERT INTO filings (
                  investor_id, source, accession, filing_date, total_value, num_holdings, raw_payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(investor_id, source, accession) DO UPDATE SET
                  filing_date = excluded.filing_date,
                  total_value = excluded.total_value,
                  num_holdings = excluded.num_holdings,
                  raw_payload = excluded.raw_payload
                """,
                (
                    *key,
                    investor.get("filing_date"),
                    investor.get("total_value"),
                    investor.get("num_holdings"),
                    json.dumps(investor, sort_keys=True),
                ),
            )
            filing_id = int(
                conn.execute(
                    "SELECT id FROM filings WHERE investor_id = ? AND source = ? AND accession = ?",
                    key,
                ).fetchone()["id"]
            )
            for rank, holding in enumerate(investor.get("top_10") or [], start=1):
                ticker = holding.get("ticker") or f"CUSIP:{holding.get('cusip', '')}"
                if not ticker or ticker == "CUSIP:":
                    continue
                security_id = upsert_security(conn, ticker, holding.get("company"), holding.get("cusip"))
                conn.execute(
                    """
                    INSERT INTO holdings (
                      filing_id, investor_id, security_id, shares, market_value,
                      pct_of_portfolio, rank_in_portfolio, is_top5, source
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(filing_id, security_id) DO UPDATE SET
                      shares = excluded.shares,
                      market_value = excluded.market_value,
                      pct_of_portfolio = excluded.pct_of_portfolio,
                      rank_in_portfolio = excluded.rank_in_portfolio,
                      is_top5 = excluded.is_top5,
                      source = excluded.source
                    """,
                    (
                        filing_id,
                        investor_id,
                        security_id,
                        holding.get("shares"),
                        holding.get("value"),
                        holding.get("pct"),
                        rank,
                        1 if rank <= 5 else 0,
                        str(path),
                    ),
                )

        for ranking in rankings:
            ticker = ranking.get("ticker") or f"CUSIP:{ranking.get('cusip', '')}"
            if not ticker or ticker == "CUSIP:":
                continue
            security_id = upsert_security(conn, ticker, ranking.get("company"), ranking.get("cusip"))
            conn.execute(
                """
                INSERT INTO convergence_rankings (
                  security_id, generated_at, convergence_score, total_investor_count,
                  tier1_count, tier2_count, tier3_count, total_conviction_pct,
                  total_value_held, top5_bonus_count, raw_investors
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(security_id, generated_at) DO UPDATE SET
                  convergence_score = excluded.convergence_score,
                  total_investor_count = excluded.total_investor_count,
                  tier1_count = excluded.tier1_count,
                  tier2_count = excluded.tier2_count,
                  tier3_count = excluded.tier3_count,
                  total_conviction_pct = excluded.total_conviction_pct,
                  total_value_held = excluded.total_value_held,
                  top5_bonus_count = excluded.top5_bonus_count,
                  raw_investors = excluded.raw_investors
                """,
                (
                    security_id,
                    generated,
                    ranking.get("convergence_score") or 0,
                    ranking.get("total_investor_count") or 0,
                    ranking.get("tier1_count") or 0,
                    ranking.get("tier2_count") or 0,
                    ranking.get("tier3_count") or 0,
                    ranking.get("total_conviction_pct") or 0,
                    ranking.get("total_value_held") or 0,
                    ranking.get("top5_bonus_count") or 0,
                    json.dumps(ranking.get("investors") or []),
                ),
            )

        conn.execute(
            "INSERT INTO source_events (source, event_type, status, summary, payload) VALUES (?, ?, ?, ?, ?)",
            (
                str(path),
                "import_snapshot",
                "completed",
                f"Imported {len(investors)} investors and {len(rankings)} rankings",
                json.dumps({"generated": generated}),
            ),
        )
    print(f"Imported {len(investors)} investors and {len(rankings)} rankings into {args.db}")


def latest_generated_at(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT generated_at FROM convergence_rankings ORDER BY generated_at DESC LIMIT 1").fetchone()
    return str(row["generated_at"]) if row else None


def export_dashboard_json(args: argparse.Namespace) -> None:
    with connect(args.db) as conn:
        generated = args.generated_at or latest_generated_at(conn)
        if not generated:
            raise SystemExit("No convergence rankings found. Run import-snapshot first.")

        investor_rows = conn.execute(
            """
            SELECT i.*, f.filing_date, f.total_value, f.num_holdings, f.accession, f.source
            FROM investors i
            LEFT JOIN filings f ON f.id = (
              SELECT id FROM filings f2
              WHERE f2.investor_id = i.id
              ORDER BY COALESCE(f2.filing_date, '' ) DESC, f2.id DESC
              LIMIT 1
            )
            ORDER BY i.tier, i.name
            """
        ).fetchall()

        investors: list[dict[str, Any]] = []
        for row in investor_rows:
            top_rows = conn.execute(
                """
                SELECT s.ticker, s.company, s.cusip, h.shares, h.market_value, h.pct_of_portfolio
                FROM holdings h
                JOIN securities s ON s.id = h.security_id
                WHERE h.investor_id = ?
                ORDER BY h.rank_in_portfolio ASC, h.market_value DESC
                LIMIT 10
                """,
                (row["id"],),
            ).fetchall()
            investors.append(
                {
                    "name": row["name"],
                    "fund": row["fund"],
                    "tier": row["tier"],
                    "filing_date": row["filing_date"],
                    "accession": row["accession"],
                    "cik": row["cik"],
                    "total_value": row["total_value"],
                    "num_holdings": row["num_holdings"],
                    "top_10": [
                        {
                            "ticker": top["ticker"],
                            "cusip": top["cusip"],
                            "company": top["company"],
                            "shares": top["shares"],
                            "value": top["market_value"],
                            "pct": top["pct_of_portfolio"],
                        }
                        for top in top_rows
                    ],
                    "source": row["source"] or row["source_type"],
                }
            )

        ranking_rows = conn.execute(
            """
            SELECT r.*, s.ticker, s.company, s.cusip
            FROM convergence_rankings r
            JOIN securities s ON s.id = r.security_id
            WHERE r.generated_at = ?
            ORDER BY r.convergence_score DESC, r.total_conviction_pct DESC
            """,
            (generated,),
        ).fetchall()
        rankings = [
            {
                "ticker": row["ticker"],
                "cusip": row["cusip"],
                "company": row["company"],
                "convergence_score": row["convergence_score"],
                "total_investor_count": row["total_investor_count"],
                "tier1_count": row["tier1_count"],
                "tier2_count": row["tier2_count"],
                "tier3_count": row["tier3_count"],
                "total_conviction_pct": row["total_conviction_pct"],
                "total_value_held": row["total_value_held"],
                "top5_bonus_count": row["top5_bonus_count"],
                "investors": json.loads(row["raw_investors"] or "[]"),
            }
            for row in ranking_rows
        ]

        output = {
            "generated": generated,
            "sprint": "MOSE SQLite export",
            "investors_pulled": len([item for item in investors if item.get("filing_date")]),
            "investors_failed": 0,
            "total_unique_stocks": len(rankings),
            "investors": investors,
            "convergence_rankings": rankings,
            "exported_from": str(args.db),
            "exported_at": utc_now(),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        conn.execute(
            """
            INSERT INTO export_runs (export_path, investor_count, security_count, ranking_count, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(args.output), len(investors), len(rankings), len(rankings), f"generated_at={generated}"),
        )
    print(f"Exported dashboard JSON to {args.output}")


def status(args: argparse.Namespace) -> None:
    with connect(args.db) as conn:
        counts = {
            "investors": conn.execute("SELECT COUNT(*) AS n FROM investors").fetchone()["n"],
            "filings": conn.execute("SELECT COUNT(*) AS n FROM filings").fetchone()["n"],
            "securities": conn.execute("SELECT COUNT(*) AS n FROM securities").fetchone()["n"],
            "holdings": conn.execute("SELECT COUNT(*) AS n FROM holdings").fetchone()["n"],
            "rankings": conn.execute("SELECT COUNT(*) AS n FROM convergence_rankings").fetchone()["n"],
            "portfolio_lots": conn.execute("SELECT COUNT(*) AS n FROM portfolio_lots").fetchone()["n"],
            "signals": conn.execute("SELECT COUNT(*) AS n FROM signals").fetchone()["n"],
        }
        print(json.dumps({"db": str(args.db), "latest_generated_at": latest_generated_at(conn), "counts": counts}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MOSE SQLite truth-store CLI")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create or migrate the SQLite database")
    init.set_defaults(func=init_db)

    imp = sub.add_parser("import-snapshot", help="Import existing convergence JSON into SQLite")
    imp.add_argument("--input", type=Path, default=DEFAULT_IMPORT_PATH)
    imp.set_defaults(func=import_snapshot)

    exp = sub.add_parser("export-dashboard-json", help="Export dashboard JSON from SQLite")
    exp.add_argument("--output", type=Path, default=DEFAULT_EXPORT_PATH)
    exp.add_argument("--generated-at")
    exp.set_defaults(func=export_dashboard_json)

    stat = sub.add_parser("status", help="Print database counts")
    stat.set_defaults(func=status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

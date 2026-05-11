# MOSE Architecture

MOSE is moving from a static dashboard toward a reliable investment intelligence system.

## Phase 1: SQLite Truth Store

SQLite is the canonical local store for investors, filings, securities, holdings, convergence rankings, portfolio lots, signals, prices, and source events.

Primary files:
- `db/schema.sql` creates the local schema.
- `scripts/mose_db.py` initializes, imports, exports, and reports on the database.
- `data/mose.db` is the local working database and should not be committed.

## Phase 2: Static Dashboard Export

The GitHub Pages dashboard remains simple. It reads `reference-data/convergence-master.json`, but that JSON should now be treated as an export artifact, not the source of truth.

Build command:

```bash
bash scripts/build_dashboard_data.sh
```

## Watchlist And Research

The dashboard now treats watchlist and research as one shared ticker universe.

- Watchlist controls are local-first and persist in `localStorage`.
- Flat mode sorts by priority, ticker, date added, convergence, 52-week discount, Joe holdings first, or needs deep dive first.
- Group mode groups by status, conviction, portfolio role, or investor overlap.
- Research has three lanes: Needs Deep Dive, Research Queue, and Research Library.
- `research_items` and `research_reports` are in the database schema so this local workflow can be promoted into SQLite/Supabase storage later.

## Phase 3: Supabase Later

`supabase/migrations/001_initial_truth_store.sql` mirrors the SQLite schema in Postgres form. We should migrate to Supabase when we need always-on jobs, multi-device state, auth, or a hosted API.

## Phase 4: IBKR Later

Brokerage integration starts read-only. The adapter contract in `adapters/brokerage.py` supports accounts, positions, and trades. `adapters/ibkr.py` is a placeholder for TWS API / IB Gateway or Client Portal Web API integration after portfolio lots are stable.

No automated trading should be added until MOSE has explicit confirmations, risk limits, audit logging, and rollback procedures.

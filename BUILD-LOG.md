# 🦞 MOSE Dashboard — BUILD LOG
**Project:** MOSE — Margin of Safety Engine  
**Owner:** Joe Lynch  
**Kicked off by:** Hermes (via Telegram), May 7, 2026  
**Codex model:** GPT-5.5  

---

## Session 4 — May 11, 2026
**Goal:** Improve Watchlist sorting/grouping and add the first Research module without making Joe enter the same stock twice.

**What was built:**
- Watchlist now has Flat mode and Group mode.
- Flat mode can sort by priority, ticker, date added, convergence score, 52-week discount, Joe holdings first, or needs-deep-dive first.
- Group mode can group by status, conviction, portfolio role, or investor overlap.
- Watchlist rows now include manual priority, convergence score, research status, and buttons to flag/approve/dismiss deep dives.
- Added a new `Research` tab with Needs Deep Dive, Research Queue, and Research Library lanes.
- Research pulls from the same ticker universe as Watchlist plus auto-flagged high-convergence names, so stocks do not need to be added twice.
- Added `research_items` and `research_reports` tables to both SQLite and Supabase schemas for the future persisted version.

**Current behavior:**
- Watchlist and Research state persist in browser `localStorage`.
- Auto deep dive flags are generated from loaded convergence data when a stock has 3+ investors and a convergence score of 60+.
- Approving a deep dive moves it into the Research Queue.
- Saving notes and marking reviewed moves it into the Research Library.

---

## Session 1 — May 7, 2026
**Goal:** Build the full MOSE dashboard as a live GitHub Pages site with all 22 Tier 1 investors, real-time stock prices, watchlist management, and convergence scoring.

**Reference data available:**
- `reference-data/convergence-master.json` — 11 investors already pulled, 263 unique stocks, top 30 convergence rankings
- `reference-data/convergence-summary.md` — human-readable summary
- `reference-data/MOSE-DATA-PROTOCOL.md` — full data protocol and investor list
- `reference-data/MOSE.md` — full product spec

**Architecture decided:** Single-file HTML dashboard (no build tools, no npm, vanilla JS/CSS). Pulls live stock prices from Yahoo Finance unofficial API. Data stored in embedded JSON updated by a companion Python script.

**Status:** Completed initial single-file build

---

## Session 2 — May 7, 2026
**Goal:** Produce the hosted GitHub Pages dashboard files requested in `CODEX-PROMPT.md`.

**What was built:**
- `index.html` — single-file vanilla HTML/CSS/JS dashboard with six tabs, dark MOSE styling, mobile-responsive layouts, localStorage watchlist, live Yahoo Finance price hooks, source labels, stale-data warnings, and safe placeholder states.
- `pull_13f.py` — conservative SEC EDGAR refresh script that uses the SEC full-text search endpoint, parses 13F information tables when a verified CIK map is supplied, backs up the old convergence file, and refuses to fabricate missing data.
- `deploy.sh` — GitHub Pages deploy script using the requested `git subtree split --prefix . main` flow.

**Tab-by-tab status:**
- Convergence Score — working from `reference-data/convergence-master.json`; live price cells fetch Yahoo Finance when the page is served over HTTP.
- Investor Profiles — working for all protocol investors; loaded investors show real filing data, unloaded investors show `13F Not Yet Loaded`.
- My Watchlist — working with add/remove, notes, holding badges, and `localStorage`; Yahoo quoteSummary is used for 52-week range and P/E when available.
- Signals — partially working; consensus and high-conviction monitor items are derived from loaded data. Add/trim/exit/new-position signals are explicitly marked unavailable because historical trend fields are not present in the current JSON.
- Data Status — working for the 22 Tier 1 protocol investors with freshness based on real filing dates and the May 15, 2026 deadline.
- Portfolio Tracker — working as a source-labeled tracker for Joe's nine known holdings. Gain/loss remains unavailable because March/April 2026 execution prices are not present in the repo data.

**Architecture decisions:**
- No build tools, npm packages, or frameworks were added.
- The dashboard fetches `./reference-data/convergence-master.json` at startup, so it should be served over HTTP rather than opened directly from disk.
- The app treats the current JSON schema as authoritative. It handles the actual `investors` array and numeric `investors_pulled` / `investors_failed` fields present in the file.
- No placeholder investment positions or entry prices were invented.

**Known issues:**
- Yahoo Finance unofficial endpoints may block browser requests from some origins or rate-limit bursts; failed cells remain visibly unavailable rather than being shown as current.
- The SEC refresh script requires a user-maintained `reference-data/cik-map.json` before it can safely identify each manager's CIK. Because raw 13F XML does not reliably include tickers, `reference-data/ticker-map.json` is also needed for clean ticker output; otherwise unresolved holdings are labeled by CUSIP.
- Current convergence data contains some issuer-name strings where ticker symbols should be, inherited from the existing JSON.

**Verification steps:**
- Validate JavaScript syntax by loading `index.html` in a browser or serving locally with `python3 -m http.server 8000`.
- Validate Python syntax with `python3 -m py_compile pull_13f.py`.
- Confirm dashboard data loading at `http://localhost:8000/`.

**How to deploy:**
- Run `chmod +x deploy.sh` once if needed.
- Run `./deploy.sh` from the repository root.
- Live URL: `https://roblobsterclaw.github.io/mose/`

---

## Session 3 — May 7, 2026
**Goal:** Move MOSE toward a stronger, more accurate, live architecture without overbuilding the cloud layer too early.

**Decision:** Use SQLite first as the canonical local truth store, then migrate to Supabase/Postgres after the schema is proven and MOSE needs always-on hosted jobs, auth, multi-device state, or a hosted API.

**What was built:**
- `db/schema.sql` — local SQLite schema for investors, filings, securities, holdings, convergence rankings, price snapshots, Joe's portfolio lots, signals, source events, and export runs.
- `scripts/mose_db.py` — CLI for initializing the database, importing the current convergence JSON, exporting dashboard JSON, and checking DB status.
- `scripts/build_dashboard_data.sh` — one-command pipeline that initializes SQLite, imports the current snapshot, exports `reference-data/convergence-master.json`, and prints counts.
- `supabase/migrations/001_initial_truth_store.sql` — Supabase/Postgres migration mirroring the SQLite schema for the later hosted phase.
- `adapters/brokerage.py` — read-only brokerage adapter contract for accounts, positions, and recent trades.
- `adapters/ibkr.py` — read-only IBKR placeholder for future TWS API / IB Gateway or Client Portal Web API integration.
- `docs/ARCHITECTURE.md` — phase-by-phase architecture note.
- `.gitignore` — excludes local DB files and Python caches.

**Phase status:**
- Phase 1, SQLite truth store — working locally. Current data imported into `data/mose.db`.
- Phase 2, dashboard JSON export — working. The dashboard still reads static JSON, but that JSON is now an export artifact.
- Phase 3, Supabase path — scaffolded with a migration; not applied to Supabase yet.
- Phase 4, IBKR path — scaffolded read-only; no account connection or trading logic added.

**Verification steps run:**
- `bash scripts/build_dashboard_data.sh`
- `python3 scripts/mose_db.py status`
- `python3 -m py_compile scripts/mose_db.py pull_13f.py adapters/brokerage.py adapters/ibkr.py`
- Embedded JavaScript syntax check for `index.html`

**Current DB counts after import:**
- Investors: 11
- Filings: 11
- Securities: 264
- Holdings: 102
- Rankings: 263
- Portfolio lots: 0
- Signals: 0

**Known issues / next work:**
- `reference-data/cik-map.json` and `reference-data/ticker-map.json` are still required before the 13F puller can safely refresh all Tier 1 investors.
- Holdings imported from the current snapshot are top-10 only. Full 13F history still needs to be pulled and stored quarter-by-quarter.
- Joe's actual portfolio lots are not loaded yet, so portfolio value and gain/loss are not authoritative.
- Browser-side Yahoo Finance remains fragile and should be replaced by a backend price snapshot job.

---

# MOSE — context & handoff for Claude Code sessions

MOSE ("Margin of Safety Engine") is a static single-file stock dashboard
(`index.html`, vanilla JS/CSS, GitHub Pages). Owner: Joe (Joe Lynch / "J
lobster"). Wife: **Keli**. This file is auto-context for new sessions — read
it first.

## Deploy / workflow rules (standing)
- Develop on **`main`**. Deploy by triggering the **`update-live-market-data.yml`**
  GitHub Action (force-pushes `main` → `gh-pages`).
- **Never open a PR** unless Joe explicitly asks.
- Never push to other branches without permission. Don't expose the model ID in
  commits/code.
- The app syncs cross-device via Firebase (`https://jfl-ttd-default-rtdb.firebaseio.com/mose`),
  which is **unreachable from the sandbox** (only the GitHub Action runner can
  reach Firebase/SEC/Stooq/Nasdaq). So the app can't be driven from here — it's a
  static site; research is hand-authored and committed.

## The 4-bucket taxonomy (rebuilt 9 Sep 2026 — Joe's call)
The Buy tab is the ONE place Joe decides what to purchase. Eight buckets became
four; the buy list is the 15 highest-consensus names across the 47 voting filers
plus UBER and SPCX. Retired: Hard assets, AI core, Opportunistic, AI bench, Radar.

1. **Forever compounders** (60%) — GOOGL, AMZN, META, MSFT, AAPL, BRK.B, NFLX, TSM, NVDA, ASML, TSLA, UBER, SPCX
2. **Toll booths** (20%) — V, MA, MCO, SPGI
3. **Dry powder** (20%) — VOO, VTV, QQQ, SGOV
4. **Other positions** (0%) — owned but NOT a buy target; exists so nothing he holds
   disappears from view. **No dollar goals** — Buy More stays blank. 38 names.

Percentages are starting points; Joe changes them in-app (⚙️ Edit goals) and by
per-stock weight. `targetsData` is at **v16**; the migration preserves every
`owned`/`plan` value and drops anything owned-but-untargeted into Other positions.

**Guard rail exemptions:** `dry` and `other` (cash management and a record of what
he already owns — neither is a stock pick).

**Watchlist = names he does NOT own and is only watching.** Its tab sits FAR RIGHT
(tab order: Buy → My Holdings → Super Investors → Valuation → Research → Watchlist).

## The account model (implemented in the Buy Targets page, v7 data)
- Three accounts, all sharing the 8 buckets: **Joe's IRA** ($950k, key `his`),
  **Keli's IRA** ($200k, key `hers`), **Joint Cash** ($344k, key `joint`).
- One list, "feels like one account." Each account's per-stock $ target =
  `account size × bucket% × stock's share of bucket` — an **auto proportional
  split** (Joe ~63.6% / Keli ~13.4% / Joint ~23%). Override per stock via the
  lock/% control. **No per-bucket routing** — every account gets the same names
  by default (Joe's explicit call).
- IRAs and the joint taxable account are **legally separate**; the app just lets
  him plan them as one. Data model: `targetsData.ira.accounts.{his,hers,joint}` +
  shared `targetsData.ira.buckets`; owned/plan keyed `account|ticker`. Migration
  is versioned (currently v7); preserve owned/plan on any change.

## Buy-day workflow (the core use case)
Joe decides buys on MOSE → **prints the buy list** (landscape, per-account order
sheet) → signs into each IBKR account separately and enters orders manually
(his login sees his IRA + Joint; Keli's is a separate login). The printout must
show the per-account $ breakdown. Keep it aligned to this.

## IBKR connector (Interactive Brokers)
- Connected via claude.ai Connectors → tools appear as `mcp__Interactive_Brokers_IBKR__*`.
  Flaky mid-session; a fresh session picks it up reliably after a global reconnect.
- **The connector sees ONE account only — Joe's IRA (~$948k net liquidation).**
  Verified 9 Sep 2026 two ways: `get_account_summary` returns a single
  net_liquidation, and `get_pa_performance_all_periods` returns a single
  `accounts.account` entry. No tool takes an account_id, so there is no selector.
- **The Joint account is NOT visible, and neither is Keli's IRA.** Proof it isn't
  just stale data: 90 days of `get_account_trades` show only BUYS (plus two small
  SGOV sells to raise cash) — no sales of GOOGL, NVDA, AMZN or AAPL — yet the app's
  `his` figures are far larger than this account holds (NVDA 5 shares here vs
  ~$18.9k recorded; AAPL absent here but $1,135 recorded). Those extra shares live
  in an account the connector cannot reach, almost certainly the Joint.
- **Therefore: never mirror IBKR onto `owned` wholesale.** `scripts/sync_ibkr_owned.py`
  is additive by default and must stay that way; `--update-all` / `--prune` are only
  safe if the API view is ever confirmed to cover every account. Joint and Keli's
  IRA continue to come in via the paste-based import on the Buy tab.

### NEXT TASK when the connector is live: create 8 IBKR watchlists (Option A)
Names = the 8 buckets above; contents = the ticker lists above. **Pull existing
watchlists first** (`get_watchlists`) and extend rather than duplicate. No
account prefixes (Joe & Keli IRAs share targets; watchlists aren't account-tied).
Ticker gotchas: `BRK.B` → **"BRK B"** on IBKR; **CSU** = Constellation Software
(Toronto/TSE, CAD; US OTC line is CNSWF); **SPCX** may now be **SPCK**; confirm
the **MBGL** (Mercedes-Benz ADR) contract. Resolve each via contract search.

### Stage 2 (parked, wanted "shortly")
Connect Keli's IRA (needs auth), then a **"tee up the trades" staging flow**: MOSE
buy list → Joe approves → agent **stages** orders in each account via
`create_order_instruction` (stage, never execute) → Joe verifies vs printout →
**Joe** submits. Hard rule: the agent never auto-executes. Guardrails + dry-run
first. Multi-account reach is the open question (separate logins).

## Research library
Deep dives are hand-authored HTML in `deep-dives/`, indexed in
`research-library.json` (versioned per ticker). ~77 reports. Write full,
GOOGL-quality reports; group the library by broad industry. Never publish broken
model numbers as fact — flag caveats.

## Known data caveats (do NOT present as fact)
- **CVNA & ROP**: the app's live price feed conflicts with the DCF reference
  price — reconcile before trusting any upside %.
- **KMX**: model IV (~$9) is not credible — judge qualitatively.
- **ASM** in the watchlist = **Avino Silver & Gold Mines** (a miner), NOT ASM
  International (that's ASMIY). Verify if a chip-tool name was intended.
- Some DCF IVs are broken (TSM/BABA ADR-FX mis-scale, TSLA auto-only). Written
  qualitatively with ⚠️ caveats.

## Interaction notes
- Joe dislikes repeated questions — lock in standing answers, act on sensible
  defaults, don't tack "want me to…?" onto every message.
- Automated snapshots are ON HOLD until Joe says go.

## Guard rail + feed (added 2 Sep 2026) — see docs/CODEX-HANDOFF-2026-09.md
- **Joe's rule:** only stocks a tracked 13F filer owns may go into a bucket. Source of
  truth: `eligible-universe.json` (built by `scripts/build_cusip_map.py` from
  `data/sec-13f-filings.json`, latest quarter). Names outside it need a logged override
  (`targetsData.overrides`). Dry powder bucket is exempt. Buy Targets shows an audit banner.
- `reference-data/cusip-map.json` = offline CUSIP→ticker bootstrap (99%+ of value). Codex's
  OpenFIGI pass should extend it, not replace the format.
- **Filer roster**: `cik-map.json` carries `status` — `approved` votes, `pruned`/`dormant` keep history but are excluded from holdings, consensus and eligibility by `votes_now()` in `build_holdings_from_13f.py` / `build_cusip_map.py`. Pruned 9 Sep 2026: Leopold Aschenbrenner, Whale Rock, Michael Burry. Roster is 50 filers / 47 voting.
- Universe tab data: `reference-data/investor-universe.json` (screen + fit + 13F-implied perf + Form ADV access), built by `build_investor_universe.py` → `build_investor_performance.py` → `build_investor_access.py` → `merge_universe_enrichment.py`; dossiers in `investor-dossiers.json`. Decisions sync via Firebase → `sync_universe_decisions.py` → `cik-map.json`.
- `signals/feed-latest.json` = between-quarter signal feed (📡 Feed tab). Contract in the
  handoff §6. **Words raise a watch flag; only filings move a score.**
- A second builder (ChatGPT Codex) works the pipeline side on `codex/*` branches; Claude owns
  `index.html`, research, email, this file. Log every session in `BUILD-LOG.md`.
- Sandbox network: Joe is switching the cloud environment to Full access + LunarCrush
  connector. Running sessions keep the old policy — start a fresh session for SEC-direct work.

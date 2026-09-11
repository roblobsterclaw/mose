# 🦞 MOSE Dashboard — BUILD LOG
**Project:** MOSE — Margin of Safety Engine  
**Owner:** Joe Lynch  
**Kicked off by:** Hermes (via Telegram), May 7, 2026  
**Codex model:** GPT-5.5  

---

## Session 18 — September 10-11, 2026 (Claude) — all four IBKR accounts sync automatically
Joe: "every time I trade one of these accounts, I'm gonna have to swap amongst the three of them to get an updated version to you. Is there a workaround?" His idea was three AI models each bound to one account, writing files to a Mac mini. There was a simpler route.

**The constraint, established first.** IBKR's AI connector authorizes **one account per connection**, chosen on IBKR's own consent screen at authorization time. No tool takes an `account_id`, so there is no selector to switch. Linking Joint under the same username does not widen it, and authorizing a second AI platform disconnects the first. Confirmed against IBKR's own documentation, not inferred.

**The workaround: Flex Web Service.** A separate read-only reporting API with no one-account limit — a token taken from the master account of a linked structure covers every account included in the query. Two tokens (Joe's login, Keli's) cover all four accounts with zero swapping, and it runs unattended in the Action.
- **`scripts/pull_ibkr_flex.py`** — async SendRequest/GetStatement handshake, polls through the 1019 "generation in progress" warning, folds every FlexStatement into one snapshot. Drops non-equity rows and closed positions, sums lots, spells class shares the way the app stores them (`BRK B` → `BRK-B`). One login failing never discards the other's data; an empty pull leaves the existing snapshot untouched. Read-only — it cannot stage or place anything.
- **`.github/workflows/sync-ibkr-positions.yml`** — weekday 08:15 ET plus manual. Deliberately not folded into the five-minute quote job: Flex is a rate-limited statement service, not a quote feed. Query ids are workflow defaults (**1633580** Joe, **1633600** Keli), so the two tokens are the only secrets.
- **`reference-data/ibkr-accounts.json`** — account id → MOSE column. Unmapped accounts are reported loudly, never guessed; a silent misfile would move six figures into the wrong account's plan.

**Privacy correction caught before the first run.** The workflow originally committed the snapshot. The repo is **public**, so that would have published account numbers, balances and every holding into permanent git history. Commit step removed, `data/ibkr-positions.json` gitignored, snapshot PUT to Firebase `mose/ibkrPositions` where the app already reads its synced state.

**Result — all four accounts, 74 positions, $1,450,568** (11 Sep, prior-day close):

| IBKR id | MOSE key | Login | Equities | Positions |
|---|---|---|---|---|
| U25747451 | `his` Joe's IRA | token 1 | $937,697 | 53 |
| U25995036 | `joint` Joint Cash | token 1 | $318,732 | 4 |
| U25767390 | `hers` Keli's IRA | **token 2** | $191,304 | 15 |
| U25302175 | `schwab` Schwab transfer | token 1 | $2,835 | 2 |

**Two open questions closed by real data.** The NVDA discrepancy flagged in Session 17 — ~$18.9k recorded under `his` against 5 shares visible — is the **Joint's 85 shares ($19,012)**. Nothing was ever sold, and the additive-only sync was the right call. And U25302175, absent from Joe's aggregator export, is the **in-flight Schwab transfer**: an individual, taxable account holding $2,835 so far.

**Fourth account column (targets v17).** Joe's call: the Schwab account gets its own column rather than folding into Joint, because Joint is jointly owned and this one is solely his, so ownership and tax treatment differ. Its total starts at **0** — spreading $2,835 across seventeen names produces targets too small to act on — and until Joe sets it in ⚙️ Edit goals the panel reads "transfer in flight" and stays off the stat bar and the printed buy list. Render, print, CSV and import now derive from `TARG_ACCTS`/`TARG_TAXABLE` instead of naming accounts inline, so a fifth account is a one-line change.

**Two repo facts learned the hard way, now in CLAUDE.md.** The default branch is **`gh-pages`, not `main`** — GitHub only exposes `workflow_dispatch` for workflows on the default branch, so a new workflow 404s until a deploy run copies it across. And the repo is **public**, which governs what may ever be committed.

**The number this surfaced:** **86.6% of the book ($1,256,250 of $1,450,568) is sitting in SGOV.** Only ~$194k is in equities. First time that figure has come from the accounts rather than an estimate.

**Verification:** `node --check` OK; headless render — all four account tables build, zero unrendered templates, Schwab panel shows the in-flight state. Flex error path verified against the live endpoint (bad token → `Fail`/`1020`). Final run: zero unmapped, both logins succeeded. `APP_BUILD` → `2026-09-10a`.

**Open:** Keli's Flex token was visible in a screenshot and should be rotated (read-only, cannot trade). The Schwab total needs setting once the transfer settles. The Buy tab still reads `owned` from the older sync path rather than this feed, and the account totals are still the estimates ($950k/$200k/$344k) rather than the actuals.

---

## Session 17 — September 9, 2026 (Claude) — the simplification: 4 buckets, consensus leaderboard
Joe's brief: "I really just want to use my Buy tab as my guide to purchase stocks." Eight buckets → four, plus a consensus page that surfaces names moving in and out of favour.

**Buy tab**
- `canonTargetsBuckets()` rebuilt: **Forever compounders 60%** (13 names), **Toll booths 20%** (4), **Dry powder 20%** (VOO, VTV, QQQ, SGOV), **Other positions 0%** (38 owned-but-untargeted names). Buy list = the 15 highest-consensus names across the 47 voting filers + UBER + SPCX, per Joe's pick. TSLA/UBER/SPCX sit inside Forever at his instruction — he'll set weights by hand.
- **targets v16** migration preserves every `owned` and `plan` value; anything owned that isn't a target is swept into Other positions so nothing disappears. Existing per-stock weights and locks carry over.
- Guard rail now exempts `other` as well as `dry`. Result: **all 17 buy-list names are held by at least one voting filer.**
- Tab order changed — Watchlist moved to the **far right**; 18 non-owned names (FICO, SOLS, DASH, LLY, DE, VRSN, ORLY, TXN, RACE, HHH, LOAR, TPL, DIS, TDG, ROP, MU, AMD, IDGT) moved into `customWatchlist` in Firebase.

**Consensus Leaderboard** (replaces the old Consensus tab — no new tab, since the brief was to simplify)
- **`scripts/build_consensus_history.py`** → `consensus-history.json`: all **1,548 tickers** the voting filers own across **9 quarters**, with holder count per quarter, quarter and year deltas, who joined/left this quarter, average % of book, add/trim counts, and share-class folding so Alphabet and Berkshire count each investor once.
- Page shows the full ranking with an 8-quarter sparkline per name, filters (Rising / Falling / Not on my list / I own it), and two computed alert rails: **⭐ coming into favour** (gaining holders, not on the buy list) and **📉 falling out of favour**.
- Live output: rising — INTC 1→6, CBRS 0→5, NU 5→8, NTRA 2→5, AVGO 5→7, AMAT/UNP/CME 4→6. Falling — INTU 8→2, ADBE 7→2, Z 7→2, CSGP 6→2, PYPL and BAC 8→5, NKE 7→4.

**Owned data fixed (Joe's Q5)** — **`scripts/sync_ibkr_owned.py`**. SGOV was missing entirely; recorded holdings went **$138,717 → $995,730** with SGOV at **$844,087**. Two safeguards worth keeping: Firebase rejects `.` in keys, so class shares must be written the way `canonicalTicker` stores them (`BRK-B`, not `BRK.B`) or the PUT 400s; and the connector is bound to **one account view** (net liquidation $948,158 = the IRA), so the script is **additive by default** — it adds and renames but never deletes, because a ticker missing from the API may simply live in an account it cannot see. `--update-all` / `--prune` are opt-in.

**Resolved 9 Sep:** the connector sees only Joe's IRA. `get_pa_performance_all_periods` returns a single `accounts.account` entry, and 90 days of trades are all BUYS — no sales of GOOGL, NVDA, AMZN or AAPL — so the larger recorded values are real positions in the Joint account the API cannot see. The additive-only default was the right call; nothing was lost.

**Verification:** `node --check` OK; headless render — tab order correct with Watchlist last, 108 consensus rows with sparklines, both alert rails populated, guard rail clean, Buy tab showing exactly the four new buckets. `APP_BUILD` → `2026-09-09c`.

*(Note: a first attempt at the consensus rewrite sliced out `escapeHtml`, `canonicalTicker`, `normalizeBucket` and other shared helpers along with the old consensus functions. Caught by the headless render — the page failed to initialise — and redone against a clean checkout with exact function boundaries.)*

---

## Session 16 — September 9, 2026 (Claude) — NFLX to Radar, deep dive, share-class fix
- **Dual-class eligibility bug fixed.** `build_cusip_map.py` counted share classes separately, so the guard-rail chip read **BRK.B = 1 holder** when 15 filers own Berkshire, and GOOGL = 29 when 33 do. Added `SHARE_CLASS`/`company_ticker()` folding (BRK-A/BRK-B→BRK.B, GOOG→GOOGL, UHAL-B, LEN-B, HEI-A) so a filer counts once per company. BRK.B now 15, GOOGL 33.
- **NFLX added to Radar** (targets **v15**, skipped if already placed on a device) and to the IBKR Radar watchlist. 11 of 47 voting filers hold it; four opened NEW in Q2-2026 — Ackman 4.8% of book, Terry Smith 3.7%, Tom Gayner, JIA 2.1% — while the stock sat ~39% below its 52-week high.
- **Deep dive published**: `deep-dives/nflx-deep-dive-2026-09-09.html`, indexed in `research-library.json` (78 reports). Verdict BUY THE DRAWDOWN, half-size on the September tranche. Fundamentals from Q2-2026 results (revenue $12.56B +13.4%, op margin 33.4%, FY guidance $51.0–51.4B / 31.5% margin / ~$12.5B FCF, ads doubling to ~$3B); price and range from IBKR ($76.81; $65.08–$126.70). Valuation figures are marked **estimated** — share count is derived from reported EPS and net income, and Netflix did a 10-for-1 split, so historical prices need adjusting.
- Counter-signal recorded in the dive: Barton (22.1% of its book) and Coatue both **trimmed** into the drawdown while the newcomers bought.
- `APP_BUILD` → `2026-09-09b`.

---

## Session 15 — September 9, 2026 (Claude) — NLR and SMH out; guard rail clean
Joe: "remove NLR and SMH." Both were VanEck sector ETFs that no voting filer owns.

- `canonTargetsBuckets()`: NLR out of Hard assets, SMH out of AI core. **targets v14** migration removes them from whichever bucket they have drifted into on a device (live state had SMH in `aibench`, not `aicore`).
- **Joe owns $612 of SMH in his IRA.** Unlike the CODI removal, this migration runs even where a position exists but leaves `owned` untouched, so the position keeps its value and simply reads as an outside-plan holding rather than being silently deleted.
- IBKR watchlists updated to match: Hard assets (110) 9 → 8 names, AI core (111) 6 → 5.
- CLAUDE.md taxonomy updated. `APP_BUILD` → `2026-09-09a`.

**Guard rail is now clean: all 58 bucket names are held by at least one of the 47 voting filers** (2026-Q2). Dry powder exempt, CSU exempt as a TSX listing.

---

## Session 14 — September 9, 2026 (Claude) — roster settled at 47 voting filers
**Goal:** Joe: "remove Leopold and Whale Rock from the list and approve the rest."

**What changed:**
- **Pruned:** Leopold Aschenbrenner (Situational Awareness — July 2026 forced liquidation, see Session 13) and Whale Rock. Michael Burry too, via his existing dormant flag (last 13F 30-SEP-2025). History is kept in `data/sec-13f-filings.json`; they no longer vote.
- **Pruning is now enforced, not just recorded.** No builder honoured a status before, so a "pruned" filer would have carried on driving consensus. Added `status` to the puller's investor records (carried from `cik-map.json`) and a shared `votes_now()` rule to `build_holdings_from_13f.py` and `build_cusip_map.py`: `pruned` and `dormant` filers are excluded from holdings, consensus, eligibility and the guard rail, while their history stays intact. In `build_cusip_map.py` the filter is deliberately applied only to the eligibility pass — the CUSIP→ticker seed maps still read every filer, since that is ticker resolution, not a vote.
- **Joe's 21 candidate approvals applied** via `sync_universe_decisions.py`: Wedgewood, Steginsky, Spruce House, Strategy Capital, Cryder, Greenbrier, Gobi, Gavilan, Greenlea Lane, Manitou, Hyperion, MayTech, Barton, Nellore, Foxhaven, Saybrook, Allen Holding, Wellcome Trust, Hikari, Milestone, JIA. Roster: **50 filers, 47 voting, 3 pruned**. Full 8-quarter history pulled for the new names.
- Decisions written to Firebase `mose/universeDecisions` so the Universe tab matches (Joe's 21 candidate decisions and the 29 roster decisions merged with no conflicts).

**Pull completed (50 filers, 394 filings, 0 failures).** After rebuilding on the 47 voting filers: holdings 283 rows / 44 investors, filing-changes 2,817 rows / 49 investors, eligible universe **1,469 tickers**. **KVYO is recovered** — Barton Investment Management, one of Joe's new approvals, holds it. The guard rail now flags only **NLR** and **SMH**, both VanEck sector ETFs that no concentrated value manager on the roster owns; CSU stays exempt as a TSX listing. `eligible-universe.json` now lists voting filers only, so the app's banner counts 47 rather than 50. Only Burry (pruned) and Tom Bancroft lack a 2026-Q2 filing — Makaira's Q1 shows a single holding, worth a look next session.

**Consequence Joe needs to see:** with Whale Rock gone, **KVYO (Klaviyo)** loses its only tracked holder and now fails the guard rail, joining **NLR** and **SMH** (both only ever "eligible" through Ancora, the wrong-entity Greenblatt mapping fixed in Session 13). CSU stays exempt as a foreign listing.

---

## Session 13 — September 7, 2026 (Claude) — dossiers, and three filer-identity fixes
**Goal:** finish what Session 12 started — research write-ups per firm — and repair the investor identity errors the research surfaced.

**What was built:**
- **`reference-data/investor-dossiers.json`** — 86 firms (27 tracked + top-60 by fit), researched by 8 parallel agents: who runs it, vehicles/fees/minimums, long-term track record, the good, the bad, the ugly, how to engage at ~$1.5M, plus sources and a confidence rating (11 high / 58 medium / 17 low). 50 carry an "ugly" finding. Every claim is tied to a listed URL; agents were told to write null rather than guess.
- **Universe tab**: firm names now show 📄 when a dossier exists and **⚠📄** when it contains a regulatory action, lawsuit or blow-up (hover for the summary). Clicking expands the write-up.

**Identity fixes the research forced (all were polluting holdings/consensus):**
- **Joel Greenblatt** was mapped to CIK 1446114 = **Ancora Advisors**, a Cleveland wealth manager with 2,454 positions. Gotham Asset Management is **1510387**. The wrong entity had been voting on consensus and eligibility.
- **Bill Ackman** — Pershing Square *moved its filing entity mid-year*: CIK 1336528 (the fund) filed the book through Q1-2026, then filed a **13F-NT** (notice, no holdings) for Q2-2026 while CIK 2026053 (Pershing Square Inc., the holdco) filed the real report. Neither CIK alone gives a complete history. Added **`alt_ciks`** support to `pull_sec_13f_history.py`: every CIK a manager has filed under is pulled and merged by quarter, fuller book wins.
- **David Einhorn** — old CIK 1079114 stopped filing; the adviser now files as **DME Capital Management, CIK 1489933**. **Michael Burry** — Scion's last 13F is 30-SEP-2025; marked `dormant`, kept for history, no longer expected to file.
- `build_investor_access.py` name-fallback tightened (it had matched **Strategy Capital LLC**, Hamilton Helmer's Bay Area fund, to *Asset Strategy Advisors* in Wayland MA and wrongly reported it as taking 481 individual clients).
- `pull_sec_13f_history.py` hardened: retry/backoff on SEC reads (the sandbox proxy truncates the ~35MB full-index files with `IncompleteRead`), per-index fault tolerance, alt CIKs included in the index scan.

**Finding worth acting on:** **Situational Awareness (Leopold Aschenbrenner)** — after +439% in H1-2026, margin calls in July 2026 forced liquidation of essentially the whole public book, Citadel reported to have bought it at a discount; assets ~$45B → ~$10B (CNBC, Yahoo Finance, 30 Jul 2026). His 13F is a snapshot of a book that no longer exists.

**Verification:** `node --check` OK; headless render — 73 candidate rows (58 dossiers, 6 warnings), 27 tracked rows (24 dossiers, 6 warnings). Ackman multi-CIK merge confirmed against EDGAR submissions for both CIKs.

---

## Session 12 — September 7, 2026 (Claude) — performance, access, dossiers on the Universe tab
**Goal:** Joe asked for a performance metric per investor, how each could work for him as an adviser (structure, fees, minimums, contact), long-term track records where public, and a good/bad/ugly write-up per firm.

**What was built:**
- **`scripts/build_investor_performance.py`** — 13F-implied performance from the bulk data alone: consensus quarter-end price per CUSIP = median of VALUE/SHARES across all filers (no ticker mapping, no outside data); each filer's US long book held one quarter, chained Jun-2024 → Mar-2026 (7 quarters); **clone** = same weights one quarter late (the filing lag); benchmark = SPY from the same table (+19.5%). Split detection by integer price ratios (2–50×, incl. ORLY 15:1), thousands-scaled filings fixed, unpriced positions excluded with a coverage %. 8,096 filers scored. Output `reference-data/investor-performance.json`.
- **`scripts/build_investor_access.py`** — joins the universe to the SEC **Form ADV bulk CSV** (registered + exempt, 24k advisers; the file carries CIK so the join is exact, name fallback) and classifies `access`: SMA-open (individual/HNW clients on file + portfolio mgmt for individuals), private-fund, exempt-reporting, institutional, not-an-adviser. Also CRD, IAPD link, phone, website, city, regulatory AUM, client counts, private/hedge fund counts, public-fund flag, compensation types, Item 11 disclosure flags. Output `reference-data/investor-access.json`. Fee schedules/minimums come from Part 2A brochures (IAPD brochure API is locked; research agents pull them from firm sites/search).
- **`scripts/merge_universe_enrichment.py`** — folds both into `investor-universe.json`.
- **Universe tab**: new columns Perf 2y (coloured vs S&P, annualised + confidence from turnover), vs S&P (pts), Clone, Access (label + client count / public fund / disclosures), Contact (phone, site, ADV link, city). Firm name expands a **dossier row** (`reference-data/investor-dossiers.json`: who / terms / track record / good / bad / ugly / how to engage / sources). Same on the tracked prune view.
- Research fan-out: 8 agents × ~11 firms (26 tracked + top-60 by fit) writing sourced dossiers; merged into `investor-dossiers.json` when complete.
- `APP_BUILD` → `2026-09-07a`.

**Findings:** Akre (105 individual / 89 HNW clients), Semper Augustus, Brave Warrior, Steginsky, Strategy Capital, Marshfield take separate accounts. Himalaya, Pershing, Abrams, Baupost, Altarock, WindAcre are fund-only. 13F-implied 2-yr: Buffett +19.2% vs SPY +19.5%; Sosin +94.6%; Bloomstran +42.3%; Li Lu +32.9%; Akre −4.9%; Ackman −1.2%; Klarman +2.7%.

**Verification:** `node --check` OK; headless render: 72 candidate rows with perf/access/contact cells and dossier rows, 26 tracked rows.

**Caveats:** performance is price-only, US long book only, quarter-end snapshots — ±2–3 pts/yr for low-turnover filers, unreliable for traders (confidence tag says which). Access is Form ADV Part 1 as filed; whether a firm is *currently* taking clients needs a call.

---

## Session 11 — September 4, 2026 (Claude) — Layer 1: the investor universe
**Goal:** Joe's "grow the 29 into a real super-value-investor list, evidence first, I approve every name." Network switched to Full, so SEC bulk data is reachable from the sandbox.

**What was built:**
- **`scripts/build_investor_universe.py`** — screens every filer in the SEC *Form 13F Data Sets* (8 windows, Jun-2024 → Q1-2026; ~8,650 filers/quarter, 3.8M holding rows/window, streamed in ~2 min). Per filer: positions, book value, top-10 and top-1 concentration, options share, quarterly turnover and median hold across the history, ETF-allocator and self-dealing flags, name-pattern exclusions (banks, pensions, insurers, index shops). Score 0–100; **fit** = score × overlap of their book with names ≥2 tracked filers own ("same mentality"). Handles amendments (restatements only), nested zip folders, and **filings still reported in thousands** (detected per filing by implied share price — Baupost does this).
- **`reference-data/investor-universe.json`** — 2026-Q1 run: 340 candidates pass, 26 tracked filers scored against the same rules. Value core passes (Hohn 100, Abrams 99, Akre 94, Li Lu 90, Ackman 89, Bloomstran 81, Smith 78, Greenberg 74); traders fail on turnover/breadth (Laffont, Halvorsen, Baker, Niles, Wood, Greenblatt) — the value-vs-trader cut Joe asked for.
- **🧭 Universe tab** in the app: fit-ranked candidate table with Approve / Pass buttons, min-fit filter, near-miss toggle, hide-decided, search; a "prune view" of the tracked filers with the same buttons. Decisions live in `universeDecisions` (localStorage + Firebase, in `getMoseState`/`hydrateMoseState`/`saveLocalOnly`). Export button downloads the decision list.
- **`scripts/sync_universe_decisions.py`** — reads decisions from Firebase and appends approved CIKs to `cik-map.json` (status `approved`); rejected tracked filers get status `pruned`, never removed. Firebase is reachable from the sandbox now.
- **Data fix:** Ackman's CIK in `cik-map.json` was the holdco (2026053, one position = HHH). The fund book is **1336528 Pershing Square Capital Management** (11 positions, $13.7B). Corrected — this also explains the "74% coverage / all NEW" Ackman artefact in `holdings-latest.json`; it clears on the next 13F Action run.
- `APP_BUILD` → `2026-09-04a`.

**Verification:** `node --check` OK; headless render shows the Universe tab with candidate rows, stats bar, and tracked prune table; guard rail intact. `sync_universe_decisions.py --dry-run` against live Firebase.

**Next:** Joe approves a first batch → run the sync → Layer 2 (full holdings + conviction across the approved list, OpenFIGI CUSIP pass). Bulk data for Q2-2026 (filed Jun–Aug) isn't posted by SEC yet; rerun the screen when it lands.

---

## Session 10 — September 2, 2026 (Claude)
**Goal:** Start the "guard rails + feed" build Joe asked for (see `docs/CODEX-HANDOFF-2026-09.md`): only stocks a tracked 13F filer owns may be routed into a bucket, and a landing zone for between-quarter signals.

**What was built:**
- **`scripts/build_cusip_map.py`** — offline CUSIP→ticker bootstrap for the 13F universe. Resolution order: CUSIP seeds (raw pull + `ticker-map.json`) → curated issuer-name alias table → exact normalised name vs `ticker-directory.json` → 13F-abbreviation expansion (AMER→AMERICA, MATLS→MATERIALS…). Tries every issuer name ever filed for a CUSIP (the same CUSIP is spelled differently across quarters). Writes `reference-data/cusip-map.json` (1,979 of 3,647 CUSIPs; **99.4% of Q2-2026 dollar value resolved**, up from ~44%) and **`eligible-universe.json`** (1,306 tickers held by ≥1 of the 29 filers in 2026-Q2, with holder lists). Funds/ETFs a filer holds are eligible too; the rest are tagged `fund`. Unresolved names are listed with dollar weight for the OpenFIGI pass (Codex, Layer 2).
- **Guard rail in the app** (`index.html`): `loadEligibleUniverse()`, `eligibilityFor()`, `eligibilityChip()`, `guardrailAllows()`, `targGuardrailHtml()`. Adding a ticker to a bucket (`targAddTicker`) now checks the eligible set; a name no tracked filer owns needs a confirm + one-line reason, stored in `targetsData.overrides[ticker] = {reason, date}` (shape-guarded in `migrateTargets`; owned/plan untouched). Buy Targets shows an audit banner (`#targets-guardrail`) listing bucket names outside the rail; every Combined-table and Watchlist row carries a `✓ N` (held by N filers, hover for names) or `⚠ not held` / `⚠ override` chip. **Dry powder is exempt** (cash management, not a stock pick).
- **📡 Feed tab** (Super Investors group): reads `signals/feed-latest.json` per the handoff §6 contract (kind / direction / severity / investor / ticker / quote / source). Filters by kind and ticker-or-investor, stats bar (signals, touching my buckets, from filings, act-now), day grouping, bucket names highlighted. Ships with an empty placeholder file and an explanatory empty state. Rule stated on the tab: words raise a watch flag, only filings move a score.
- `APP_BUILD` → `2026-09-02a`.

**Findings surfaced by the rail on Joe's current buckets:** all 61 stock-bucket names are held by a tracked filer except **CODI** (Compass Diversified — no filer owns it). SMH and NLR are held (VanEck ETFs via Greenblatt et al.).

**Verification steps run:**
- `node --check` on the embedded JS (2 blocks) — OK
- Headless Chromium render against a local static server: guard-rail banner rendered ("2 of 61…" before the SMH alias fix, CODI after), Feed tab button + empty state rendered, 102 ✓ chips / 13 ⚠ chips, `APP_BUILD` present
- `python3 scripts/build_cusip_map.py` coverage report (see above)

**Known issues / next work:**
- `eligible-universe.json` and `cusip-map.json` are a one-off bootstrap; wire `build_cusip_map.py` into `update-13f-tracker.yml` after the holdings rebuild so they refresh each quarter (Codex lane; then replace/extend with OpenFIGI).
- Eligibility is "held by ≥1 of the 29". The conviction score / approved-universe expansion (Layers 1–2) is still to come.
- Feed is a shell until the Layer 3 collector writes real items.

---

## Session 9 — June 16, 2026
**Goal:** Extend drag-and-drop to the MOSE bucket, and add edge auto-scroll so far-apart sections can be reached.

**What was built:**
- **MOSE is now a drag participant** (`tbody data-targ-bucket="mose"` with handle rows). Reorder within MOSE, or drag a MOSE name onto an IRA bucket (and vice-versa) — works across the two separate tables via `elementFromPoint`.
- **Cross-pool owned migration:** moving a stock across the IRA↔MOSE boundary carries its owned $ to the destination's account key (`his/hers` ⇄ `mose`) so nothing is silently orphaned; same-pool moves leave owned untouched. Generalized `targDropTicker` via a `targListFor(id)` helper that resolves `'mose'` or any IRA bucket.
- **Edge auto-scroll during drag:** when the pointer nears the top/bottom of the viewport, the page scrolls (with the ghost + drop indicator tracking), so you can drag a MOSE name at the bottom up to an IRA bucket — essential on the phone.

**Verification steps run:**
- node --check; unit tests: AAPL MOSE→Forever (MOSE re-spreads to 9 @ $26,756, AAPL Forever target $103,500), WMT For Now→MOSE with owned migration ($16,946+$3,389 → mose|WMT $20,335, his/hers cleared), reorder within MOSE
- Headless Chromium: cross-table drag on a tall viewport (AAPL MOSE→Forever) AND on a short viewport relying on auto-scroll — both moved the row, no page errors

**Deploy:** merged to main and published to gh-pages (live).

---

## Session 8 — June 16, 2026
**Goal:** Drag-and-drop in the Buy Targets Combined table — reorder stocks and move them between buckets with automatic recalculation.

**What was built:**
- **Drag-and-drop on the Combined IRA table:** each row has a ⠿ handle. Drag to reorder within a bucket, or drop onto another bucket (or one of its rows) to move the stock there. Buckets are now separate `<tbody data-targ-bucket>` drop zones; rows carry `data-targ-ticker`.
- **Pointer-event implementation** (pointerdown/move/up + `touch-action:none`) so it works on both the Mac (mouse) and the iPhone (touch) — native HTML5 DnD would have been dead on iOS. Floating ghost label, drop-line indicator between rows, and bucket-highlight when hovering an empty area.
- **Automatic recalc:** moving a ticker just edits `bucket.tickers`, so equal-weight (and the dollar goals) re-spread instantly across both IRAs, MOSE untouched. Moving a stock out of a bucket drops its custom weight from that bucket (remaining names renormalize to 100%); the stock takes a default weight in its new bucket. Owned values follow the ticker. Toast confirms cross-bucket moves.

**Verification steps run:**
- Embedded JavaScript syntax check (node --check)
- Node unit tests: move MELI For Now→Forever (Forever→5 names @ $103,500, For Now→14 @ $16,429), reorder within a bucket, and weight renormalization after a weighted stock leaves (sum stays 100%)
- Headless Chromium pointer-drag test: dragged MELI's handle onto Forever — row moved buckets, combined goal recomputed to $103,500, For Now lost it, no page errors

**Deploy:** merged to main and published to gh-pages (live).

---

## Session 7 — June 15, 2026
**Goal:** Four Buy-Targets upgrades Joe greenlit, plus load his wife's IRA positions.

**What was built:**
- **Custom per-stock weights within a bucket** — new editable "% of Bucket" column in the Combined table. Setting one stock's % rebalances the others proportionally so the bucket always sums to 100% and its dollar goal stays exact. "Reset to equal" link per bucket. Single-ticker buckets (S&P/VOO) show a fixed 100%. Weights flow through to his/hers/combined and the CSV.
- **"Buy More" in shares** — every order amount now shows `≈ N sh` at the live price in the his/hers/MOSE tables, and a "Buy More (sh)" column in the CSV.
- **One-paste IBKR import** — collapsible "📥 Update from IBKR" panel: pick account, paste positions (`TICKER VALUE` or `TICKER SHARES PRICE`), Preview, Import. Forgiving parser ignores USD/Cash lines and handles $/comma formatting. Lands straight in the synced state (solves the Firebase-override problem for monthly updates).
- **Progress history** — dated snapshots auto-captured on every import (plus a manual "Save snapshot now" button). Shows a sparkline of % of IRA goal deployed over time and a table with deployed $, %, MOSE deployed, and Δ since the prior snapshot.
- **Wife's IRA loaded** from her IBKR screenshot (acct U25767390): AMZN $2,624, GOOGL $3,970, WMT $3,389 (~$190k still in SGOV/cash). Her side of the tracker is now live; combined IRA deployed = $56,901 (4.9%).
- Bumped targets data to version 2 with a load-time normalizer (adds `weights`/`history` to any older saved state).

**Verification steps run:**
- Embedded JavaScript syntax check (node --check)
- Node tests: weight rebalance (GOOGL→40% of Forever makes others 20% each, sum 100, targets recompute to $207k combined / $171k his); import parser (both formats, USD/Cash ignored); import-into-account + same-day snapshot dedup; wife data load
- Headless Chromium render of the full upgraded tab — % of Bucket column, share hints, import panel, populated Her IRA, history, outside-plan (PLD); no page errors

**Known issues / next work:**
- Import overwrites listed tickers but doesn't zero a position that was fully sold — edit that cell to 0 if needed.
- Still on the dev branch; not deployed live (holding per Joe until he gives the go-ahead).

---

## Session 6 — June 13, 2026
**Goal:** Replace the "decide the timing for me" model with what Joe actually wants — a fixed per-stock dollar-goal tracker he reverts to, updated from IBKR position screenshots.

**What was built:**
- New **🎯 Buy Targets** tab — a goal tracker, not a timing engine. Each stock has a fixed dollar target decided today; Joe buys on his own schedule and the sheet shows how much of each he still needs.
- **Two pools, kept separate:**
  - **IRA — $1.15M combined** (his $950k + wife's $200k), tracked as one goal but executed per-account. Buckets: Forever 45% / S&P 35% (VOO) / For Now 20%, equal-weight within each bucket. His/hers are mirrors scaled to each account's total.
  - **MOSE — $344k joint cash** (the former "Innovation" names), 70% to stocks ($240,800 split equally across 10 names) / 30% cash held back ($103,200). 100% separate from IRA totals.
- Three views: **Combined IRA goal progress** (per stock, his+hers), **Your IRA** and **Her IRA** execution tables with editable Owned + "Buy More" order sizes, and the **MOSE** table. Plus a **Holdings outside the plan** section for tickers held but not in any bucket.
- **Owned seeded from Joe's IBKR screenshot (acct U25747451):** GOOGL $18,044, AMZN $11,928, WMT $16,946, PLD $5,652 (flagged outside-plan). Wife's side left pending her screenshot.
- **CSV export** button (account/bucket/ticker/target/owned/buy-more/%). Bucket names renamed to Joe's labels (Forever / S&P / For Now / MOSE).
- All goals/pools/%s editable in-UI; state persists to localStorage and syncs via the shared Firebase blob (`targets` key). Cockpit/Re-Entry tabs untouched.

**Verification steps run:**
- Embedded JavaScript syntax check (node --check)
- Node unit test of target math (his Forever $106,875, S&P $332,500, For Now $12,667; hers Forever $22,500; his deployed $46,918; MOSE $240,800/$103,200) and CSV export
- Headless Chromium render of the full tab — tables, his/hers split, MOSE, outside-plan (PLD), WMT over-target flag all correct; no page errors

**Known issues / next work:**
- Wife's IRA Owned column is zero pending her positions screenshot (Joe is merging her accounts under one IBKR login / LTA).
- Updating Owned from a screenshot is currently manual entry (or I edit the seed); fine until the IBKR API is connected.
## Session 11 — June 16, 2026
**Goal:** Fix "Add Stock" search — it only matched the ~90 names MOSE already tracked, so listed companies (and private ones like Cursor/Cerebras) couldn't be found.

**What was built:**
- `reference-data/ticker-directory.json` — a NYSE/NASDAQ/AMEX symbol directory the search reads. Seeded now (~180 names from repo data + curated large/mid caps) and refreshed to the full ~10k SEC/Nasdaq listing by `scripts/build_ticker_directory.py`, wired into the weekly 13F workflow.
- Watchlist search now merges tracked names (with bucket/source hints) and the full directory; tracked entries win on collisions. Name-only adds work (the old code silently refused them).
- Pre-IPO / private add path: any typed name can be added as an unlisted company (🔒, no quote attempted). Cursor (private) is handled this way. Quote script skips `private` entries.
- Non-US listings: a curated supplement (Constellation Software CSU→CSU.TO, Cerebras CBRS, Couche-Tard ATD.TO, major ADRs) is merged into the directory, since SEC data is US-only. Foreign tickers carry a Yahoo quote symbol (`y`) so they quote correctly (e.g. CSU is fetched as CSU.TO).

**Owner action:** trigger the "Update 13F tracker" workflow once to replace the seed with the full SEC directory (the sandbox can't reach SEC/Nasdaq hosts).

---

## Session 5 — June 12, 2026
**Goal:** Give Joe a mechanical market re-entry playbook after the April 2026 Truist→IBKR move, so the monthly buys happen like clockwork regardless of where the market is.

**What was built:**
- New **📅 Re-Entry Plan** tab with two plans:
  - **IRA (IBKR) — 18-month tranche DCA**: remaining cash ÷ remaining months = base tranche; a drawdown ladder scales the order up (−5% → 1.5×, −10% → 2×, −15% → 2.5×, −20% → 3×). Each month's order is split across Watchlist buckets (Core 50 / Opportunistic 30 / Innovation 10 / Treasury 10 by default) with live tickers from those buckets shown on the buy ticket.
  - **Joint Taxable ($344k) — opportunistic dip buyer**: holds cash until cumulative dip tiers trigger (−5% deploy 15%, −10% +25%, −15% +30%, −20% +30%), with the shopping list pulled live from the Watchlist buckets.
- Drawdown is measured on the S&P 500 from a **ratcheting reference high** (auto-updates on new highs, manually overridable), plus a vs-April-exit readout (6591.90).
- Big "buy ticket" cards show this month's exact dollar order and status (⏳ waiting / 🔔 BUY NOW / ✅ done), an 18-row schedule table, the active ladder rung highlighted, and a progress bar of deployed vs dry powder.
- **Purchase log**: after placing an order at IBKR, Joe logs date/account/ticker/amount; remaining tranches recalculate, so skipped or partial months roll forward automatically.
- Command Center now shows a Re-Entry banner card (next action for both accounts) that jumps to the tab.
- All plan settings (totals, months, start, buy day, allocations, ladder multipliers, tier percentages) are editable in the UI; state persists to localStorage and syncs through the existing Firebase pipe (`reentry` key in the shared state blob).

**Verification steps run:**
- Embedded JavaScript syntax check for `index.html` (node --check)
- Node smoke tests of the tranche math (at-high 1× $50k, −11% → 2× $100k; joint tiers trigger $137.6k at −11%; purchases roll the remainder forward)
- Headless Chromium render of the cockpit banner and the full Re-Entry tab — no console errors

**Known issues / next work:**
- Live S&P quote currently comes from `indices-latest.json` / the Stooq job; per-ticker monthly-dip signals need price history (Stooq API key) before "GOOGL is down X% this month" alerts can be added.
- IBKR API hookup still pending — purchases are logged manually for now by design.
---

## Session 10 — June 12, 2026
**Goal:** Fix the dead quote pipeline, lock down exposed personal data, make watchlist buckets user-editable, and version the deep dives.

**Diagnosis:** Stooq's keyless CSV endpoint started returning empty data June 5 and hard-404s since June 9; every scheduled run failed and the published snapshot had zero quotes. The old script also computed "change %" vs the day's open rather than the previous close, and silently committed empty data as success.

**What was built:**
- `scripts/update_live_market_data.py` rewritten against Yahoo Finance's v8 chart endpoint (no API key): previous-close change %, 52-week range from quote metadata, ~daily 1Y history refresh, custom Firebase-watchlist tickers included, exit anchors moved to `reference-data/exit-baseline.json`.
- Failure policy: never overwrite good data with bad. On failure the script writes `pipeline-status.json` and exits non-zero; the dashboard shows a site-wide red/amber banner when quotes are stale, empty, or the pipeline reports an error.
- Security: Truist account numbers removed from `joes-holdings.json` and the holdings UI; dashboard password stored as SHA-256 hash instead of plaintext. Remaining owner steps documented in `docs/SECURITY-LOCKDOWN.md` (history purge, private repo, Firebase rules, password rotation).
- Watchlist buckets are now user-defined: create, rename, delete, and reorder (▲/▼) from the grouped view; definitions sync via Firebase with the rest of the state.
- Deep dives are versioned: `research-library.json` may hold multiple reports per ticker; the library shows the latest with an expandable history timeline and deltas (intrinsic value, verdict, convergence score). Per-ticker monthly/quarterly refresh cadence resurfaces due tickers in the Needs Deep Dive lane. Protocol in `docs/DEEP-DIVES.md`.
- Removed the permanently disabled GitHub Contents-API sync layer from `index.html`.

---

## Session 4 — May 11, 2026
**Goal:** Improve Watchlist sorting/grouping and add the first Research module without making Joe enter the same stock twice.

**What was built:**
- Restored the cleaner original MOSE platform UI as the base: top market bar, command center, Joe's Watchlist, Joe's Holdings, Super Investors, and Deep-Dive Research Library.
- Watchlist now has Flat mode and Group mode while keeping the original bucket-based layout.
- Flat mode can sort by priority, score, ticker, date added, margin of safety, Joe holdings first, or needs-deep-dive first.
- Group mode can group by bucket, status, conviction, portfolio role, or investor overlap.
- Watchlist rows now include manual priority, convergence score, research status, and buttons to flag/approve/dismiss deep dives.
- The existing Research Library tab now includes a Research Queue lane above completed reports.
- Research pulls from the same ticker universe as Watchlist plus auto-flagged high-convergence names, so stocks do not need to be added twice.
- Added `research_items` and `research_reports` tables to both SQLite and Supabase schemas for the future persisted version.
- Added `scripts/build_legacy_platform_data.py` to generate the root JSON files expected by the original MOSE platform UI from the current convergence master.

**Current behavior:**
- Watchlist and Research state persist in browser `localStorage`.
- Auto deep dive flags are generated from the purchase-readiness score in the original command center.
- Deep-dive requests flow into the Research Queue and also remain visible from the Watchlist/Command Center.
- Completed reports continue to live in the Research Library.

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

# MOSE — Margin of Safety Engine
*Master playbook. Updated continuously.*

---

## What MOSE Is
An automated value investing intelligence system that clones the world's best super investors by tracking their 13F filings, public commentary, and portfolio moves — then scores convergence signals to identify high-conviction buys with margin of safety.

## Branding

**Logo:** 🦞 MOSE — Margin of Safety Engine

**All reports must include in their title/header:**
- The MOSE name
- The 🦞 lobster logo
- Report type and date

**Report naming convention:**
- Daily: `🦞 MOSE Daily Brief — [Date]`
- Weekly: `🦞 MOSE Weekly Report — Week of [Date]`
- Monthly: `🦞 MOSE Monthly Review — [Month Year]`
- Quarterly: `🦞 MOSE Quarterly Deep Dive — Q[X] [Year]`
- Alerts: `🦞 MOSE ALERT — [Description]`
- Video recs: `🦞 MOSE Watch List — Week of [Date]`

**Telegram format:**
```
🦞 MOSE Daily Brief — April 10, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[content]
```

**Word doc header:**
```
🦞 MOSE — Margin of Safety Engine
[Report Type] | [Date]
Prepared by Rob Lobster | CONFIDENTIAL
```

**Dashboard header:**
```
🦞 MOSE — Margin of Safety Engine
Last updated: [timestamp]
```

---

## Current Status

### ✅ Built
- Dashboard: `margin-of-safety-engine/dashboard.html`
- 5 investors actively loaded (Buffett, Li Lu, Pabrai, Akre, Spier)
- 23 unique stocks tracked from 13F data
- Holdings JSON auto-refreshed
- Proposal doc: `generate_proposal.py`

### ❌ Not Built Yet
- Nightly automated 13F filing scan
- Convergence scoring engine
- YouTube/podcast monitoring pipeline
- New investor discovery radar
- Live hosted URL (currently local HTML only)
- Full 29-stock April 30 portfolio integration
- Tier 1-3 investor expansion (only 5 of 22 loaded)

---

## Investors Tracked

### TIER 1 — The Legends (Active Clone Targets)
| # | Investor | Fund | AUM Est. | 13F Loaded | Score |
|---|----------|------|----------|------------|-------|
| 1 | Warren Buffett | Berkshire Hathaway | $300B+ | ✅ | 98 |
| 2 | Charlie Munger (Legacy) | DJCO / Berkshire | N/A | ❌ | 95 |
| 3 | Li Lu | Himalaya Capital | ~$6B | ✅ | 92 |
| 4 | Seth Klarman | Baupost Group | ~$27B | ❌ | 90 |
| 5 | Howard Marks | Oaktree Capital | ~$190B | ❌ | 88 |

### TIER 2 — Proven Compounders
| # | Investor | Fund | AUM Est. | 13F Loaded | Score |
|---|----------|------|----------|------------|-------|
| 6 | Mohnish Pabrai | Pabrai Investment Funds | ~$600M | ✅ | 85 |
| 7 | Chuck Akre | Akre Capital Management | ~$12B | ✅ | 83 |
| 8 | Guy Spier | Aquamarine Capital | ~$250M | ✅ | 78 |
| 9 | Terry Smith | Fundsmith | ~$23B | ❌ | 82 |
| 10 | Tom Gayner | Markel Group | ~$8B equity | ❌ | 80 |
| 11 | Nick Sleep & Qais Zakaria | Nomad Investment (closed) | N/A | ❌ | 85 |
| 12 | Chris Bloomstran | Semper Augustus | ~$800M | ❌ | 76 |
| 13 | Bill Ackman | Pershing Square | ~$18B | ❌ | 75 |

### TIER 3 — Emerging/Specialist
| # | Investor | Fund | AUM Est. | 13F Loaded | Score |
|---|----------|------|----------|------------|-------|
| 14 | David Einhorn | Greenlight Capital | ~$3.5B | ❌ | 72 |
| 15 | Prem Watsa | Fairfax Financial | ~$50B assets | ❌ | 70 |
| 16 | Pat Dorsey | Dorsey Asset Management | ~$400M | ❌ | 68 |

### TIER 4 — Watchlist (Monitor, Don't Clone Yet)
| # | Investor | Fund | AUM Est. | Score |
|---|----------|------|----------|-------|
| 17 | Francois Rochon | Giverny Capital | ~$700M | 65 |
| 18 | Bryan Lawrence | Oakcliff Capital | ~$350M | 60 |
| 19 | Jake Taylor | Author/Podcaster | N/A | 55 |
| 20 | Allan Mecham | Arlington Value Capital | ~$400M | 62 |
| 21 | Thomas Russo | Gardner Russo & Quinn | ~$8B | 68 |
| 22 | Christopher Hohn | TCI Fund Management | ~$40B | 64 |

**Total Identified: 22 investors**
**Loaded in Engine: 5**
**Target: All Tier 1-3 (16 investors)**

---

## Investor Scoring System (100 points)

| Criterion | Max Points | Description |
|-----------|-----------|-------------|
| Track Record | 25 | Min 10 years, must beat S&P by 3%+ annualized |
| Philosophy Alignment | 20 | Graham/Buffett/Munger principles |
| Concentration | 15 | Top 5 positions = 40%+ of portfolio |
| Skin in the Game | 15 | Personal capital alongside LPs |
| Transparency | 10 | Letters, conferences, public reasoning |
| Cycle Consistency | 10 | Performance in bull AND bear markets |
| Intellectual Honesty | 5 | Publicly discusses mistakes |

- **80+ points:** Tier 1 — Active clone target
- **65-79 points:** Tier 2-3 — Active tracking
- **40-64 points:** Tier 4 — Watchlist only

---

## Convergence Scoring (Stock Level)

When multiple tracked investors hold the same stock, convergence score increases:

| Signal | Points |
|--------|--------|
| 1 Tier 1 investor holds position | +20 |
| 1 Tier 2 investor holds position | +10 |
| 1 Tier 3 investor holds position | +5 |
| Position is top 5 for investor | +10 bonus |
| Position is NEW this quarter | +15 bonus |
| Position was INCREASED this quarter | +5 bonus |
| Investor discussed thesis publicly | +10 bonus |

**Convergence threshold: 40+ points = strong signal. 60+ = very strong. 80+ = screaming buy.**

---

## Stocks Tracked (23 Unique — as of April 8, 2026)

AAPL, AMZN, AXP, BRK-B, CVX, DVA, FICO, GOOGL, HCC, KHC, KMX, MA, MCO, META, ORLY, OXY, RACE, RIG, ROP, STZ, V, VAL, VRSN

**Target: Update to full 29-stock April 30 portfolio + any convergence picks**

---

## Style Buckets

| Style | Primary Practitioners |
|-------|----------------------|
| Deep Value | Klarman, Einhorn, Pabrai |
| Quality Compounders | Akre, Dorsey, Terry Smith, Gayner |
| Special Situations | Ackman (activist), Marks (distressed) |
| Growth at Reasonable Price | Li Lu, Rochon, Thomas Russo |
| Insurance Float Model | Buffett, Gayner, Watsa |

---

## Data Sources

### Free
- SEC EDGAR API — 13F filings (gold standard)
- SEC Form 4 — insider transactions
- SEC 13D/13G — activist stakes (5%+ ownership)
- Alpha Vantage API (free tier) — prices, fundamentals
- Financial Modeling Prep (free tier) — financial statements
- WhaleWisdom (free tier) — 13F aggregation
- HedgeFollow — hedge fund tracking
- Dataroma — superinvestor portfolios
- Insider Monkey (free tier) — 13F + insider buying

### Paid (Optional)
- GuruFocus Premium — $30/mo — guru portfolios, 10yr data
- Seeking Alpha Premium — Joe already subscribes

### Media Monitoring
- **YouTube Channels:** The Swedish Investor, Investor Center, New Money, Sven Carlin PhD, Value After Hours, Graham Stephan, The Plain Bagel, Patrick Boyle, Aswath Damodaran, Compounding Quality
- **Podcasts:** Capital Allocators, Value After Hours, Motley Fool Money, Focused Compounding, The Business Brew, Superinvestors Podcast

---

## Automation Pipeline (Target Architecture)

### Nightly Sweep (12:00 AM ET)
| Time | Task | Processor |
|------|------|-----------|
| 12:00 AM | SEC EDGAR filing check | Cheap model |
| 12:05 AM | News headline scan | Cheap model |
| 12:15 AM | YouTube channel check | Cheap model |
| 12:20 AM | Podcast RSS feed check | Cheap model |
| 12:25 AM | Aggregator scan (GuruFocus, WhaleWisdom) | Cheap model |
| 12:35 AM | Relevance scoring and filtering | Cheap model |
| 12:40 AM | Escalation to Opus (if significant) | Claude API |
| 12:50 AM | Brief generation | Cheap model |
| 6:30 AM | Delivered to Joe via Telegram | OpenClaw |

### Weekly New Investor Radar (Mondays)
- Scan SEC EDGAR for new 13F filers matching value criteria
- Monitor YouTube/podcasts for emerging fund managers
- Score against 100-point system
- Auto-promote Tier 4 → Tier 3 when threshold met
- Report to Joe every Monday morning

### Quarterly Deep Dive (After 13F Deadline)
- Full portfolio diff for all tracked investors
- Convergence heat map update
- New position alerts
- Position increase/decrease analysis
- Style drift detection

---

## Cost Estimate

| Component | Monthly Cost |
|-----------|-------------|
| Qwen 2.5 local processing (electricity) | $0.30 |
| Cheap cloud model for sweeps (Gemini/GPT-mini) | $1-5 |
| Claude API (escalation only) | $1.50-10 |
| SEC EDGAR / Alpha Vantage / WhaleWisdom | $0 |
| GuruFocus Premium (optional) | $30 |
| **TOTAL** | **$3-45/month** |

---

## Build Roadmap

### Phase 1 — Foundation ✅ (Complete)
- [x] Core 5 investors loaded
- [x] 23 stocks tracked
- [x] Dashboard HTML built
- [x] Holdings JSON structure

### Phase 2 — Expansion (Next)
- [ ] Load all Tier 1-3 investors (16 total)
- [ ] Update to full 29-stock April 30 portfolio
- [ ] Deploy to live URL
- [ ] Build convergence scoring engine
- [ ] Historical 13F backfill (8 quarters per investor)

### Phase 3 — Automation
- [ ] Nightly SEC EDGAR sweep (cron job)
- [ ] YouTube/podcast monitoring pipeline
- [ ] News/article scanning
- [ ] Morning Intelligence Brief via Telegram
- [ ] Convergence alerts when threshold hit

### Phase 4 — Intelligence
- [ ] Weekly New Investor Radar
- [ ] Quarterly deep dive reports
- [ ] Cloning recommendation engine (auto buy/watch/ignore)
- [ ] Historical performance backtesting
- [ ] International filing integration (SEDAR+ Canada, Companies House UK)

### Phase 5 — Advanced
- [ ] Shareholder letter archive (searchable, key quotes tagged)
- [ ] Style drift detection
- [ ] Portfolio overlap visualization
- [ ] DCF + Graham Number integration per stock
- [ ] Risk scenario modeling

---

## Key Files
- `projects/investing/margin-of-safety-engine/dashboard.html` — main dashboard
- `projects/investing/margin-of-safety-engine/holdings-latest.json` — current holdings
- `projects/investing/margin-of-safety-engine/investors.json` — investor config
- `projects/investing/margin-of-safety-engine/indices-latest.json` — market indices
- `projects/investing/generate_proposal.py` — full MOSE proposal generator
- `memory/ref-investment-portfolio.md` — Joe's portfolio deep reference

---

## Investor Profile Template (11 Sections Per Investor)

Each tracked investor gets a "living profile" stored in `projects/investing/profiles/`:

1. **Background & Origin Story** — Where they came from, what shaped them. Li Lu's escape during Tiananmen. Pabrai's immigration with $100. History predicts behavior under stress.
2. **Philosophy In Their Own Words** — Direct quotes from letters, interviews, books. Not interpretation — their actual words with source/date tags.
3. **Key Mental Models** — Frameworks they use. Munger's latticework, Marks's second-level thinking, Akre's three-legged stool.
4. **Notable Wins AND Mistakes** — Wins: Buffett's Apple, Li Lu's BYD. Mistakes: Buffett's Dexter Shoe, Ackman's Valeant, Pabrai's Horsehead. Mistakes section is MORE valuable.
5. **Current Portfolio (Most Recent 13F)** — Top 10 positions with shares, value, % of portfolio, QoQ change. Auto-updated quarterly.
6. **Historical Portfolio Evolution** — Multi-year view. What's held 5+ years (highest conviction)? Average holding period. Turnover rate. Conviction drift detection.
7. **Concentration Patterns** — Herfindahl index over time. Getting more or less concentrated? Pattern changes signal strategy shifts.
8. **Sector Tendencies** — Heat map of sector allocation over time. When an investor ventures OUTSIDE their typical sector = high conviction signal.
9. **Buy/Sell Triggers** — What conditions cause action? Klarman buys catalysts + margin of safety. Buffett buys wonderful companies at fair price or during panics.
10. **Relationships to Other Tracked Investors** — Pabrai & Spier are best friends. Li Lu mentored by Munger. These create "information chains."
11. **Personal Characteristics Affecting Style** — Pabrai's immigrant mindset → extreme loss aversion. Marks's credit background → cycle focus. Spier's move to Zurich → noise reduction.

---

## Morning Intelligence Brief Format

Delivered daily by 6:30 AM ET via Telegram:

```
═══ MARGIN OF SAFETY ENGINE — MORNING BRIEF ═══
Thursday, April 10, 2026 | Market: S&P 500 closed XXXX

🔴 RED ALERTS (Immediate Attention)
  → [Tier 1 investor new position or convergence event]

🟡 NOTABLE MOVES (Review When Convenient)
  → [Tier 2 investor changes, increased positions]

🟢 BACKGROUND INTELLIGENCE (FYI)
  → [New videos, leaked letters, articles]

📊 CONVERGENCE DASHBOARD SNAPSHOT
  → [Stocks held by 3+ tracked investors]

📅 UPCOMING
  → [Next 13F filing window, conferences, meetings]

═══════════════════════════════════════════════
Sources scanned: XX | Items processed: XX | Escalated to Claude: X
Processing cost: $0.XX
```

---

## What NOT to Blindly Clone

- **Position Sizing Mismatch** — Buffett manages $300B+, can ONLY buy mega-caps. Joe's $1.9M can buy things Buffett can't — that's an ADVANTAGE.
- **Tax Situation Differences** — Institutional investors have different tax structures. A tax-optimal move for Baupost may be inefficient for Joe's IRA/taxable mix.
- **Institutional Constraints** — Ackman's activism requires board seats. Marks's distressed debt requires illiquidity tolerance. Can't replicate the catalyst.
- **Hedging/Derivatives** — Some positions are hedges or pairs trades invisible in 13F data.
- **Stale Positions** — By the time you see a 13F, the investor may have already sold. Cross-reference with Form 4s.
- **GOLDEN RULE:** Clone the IDEA, not the position. Understand WHY, then decide if it applies to YOUR situation.

---

## Joe's Portfolio Tracking

### Current State (as of April 10, 2026)
- ~$1.9M total across IRA + taxable
- ~95% in treasury instruments (moved to defensive March 25, 2026)
- Exit baselines: S&P 500: 6,591.90 | Dow: 46,429.49
- April 30 target: deploy into concentrated 29-stock portfolio

### How Joe Updates His Holdings
**Method 1 — Monthly Statement (Primary):**
- Email Truist PDF statement to rob.lobster.claw@gmail.com
- Subject: "ROB ACTION — Portfolio Update"
- Rob parses, updates `joes-portfolio.json`, dashboard refreshes
- **1st of every month, or after any significant trade**

**Method 2 — Real-Time Trade Updates:**
- Text Rob on Telegram: "Bought 100 shares GOOGL at $165"
- Rob updates portfolio JSON immediately
- Dashboard reflects within minutes
- **Use during April 30 restructuring — report each trade as it happens**

**Method 3 — Brokerage API (Future):**
- Auto-sync from Truist/Schwab/Fidelity
- Zero manual effort
- Phase 5 implementation

### Portfolio Data Files
- `joes-portfolio.json` — current holdings (account, ticker, shares, cost basis, date)
- `joes-trade-log.json` — every buy/sell with date, price, shares, account
- `joes-target-portfolio.json` — April 30 target allocations
- `joes-treasury-positions.json` — treasury instruments, maturities, yields

### Dashboard Portfolio Tab Shows:
- Current holdings by account (IRA vs taxable)
- Convergence score next to each stock position
- DCF margin of safety for each equity holding
- April 30 target vs actual (NOT PURCHASED / PURCHASED / PARTIAL)
- Gap analysis (target stocks not yet bought)
- Warning flags (holdings with no super investor backing)
- Trade log timeline

---

## Integration with Joe's April 30 Portfolio

- **Pre-Restructuring Validation** — Run convergence on Joe's proposed 29 stocks. How many are held by tracked super investors?
- **Gap Analysis** — Identify stocks NOT on Joe's list that score 60+ convergence.
- **Allocation Check** — Cross-reference Joe's allocation with super investor concentration patterns.
- **Thesis Documentation** — For each stock, document which super investors hold it and their thesis.
- **Post-Restructuring Monitoring** — If Buffett exits a stock Joe holds, flag immediately.

---

## Newsletters & Investor Letters to Monitor

- Greenlight Capital (Einhorn) — quarterly letters, detailed short/long theses
- Pershing Square (Ackman) — annual letter, conference presentations
- Fairfax Financial (Watsa) — annual letter, Buffett-style
- Baupost Group (Klarman) — annual letter, rarely leaked but invaluable
- Semper Augustus (Bloomstran) — annual letter, 100+ page Berkshire analysis
- Giverny Capital (Rochon) — annual letter, 20+ year track record
- Himalaya Capital (Li Lu) — Columbia/Greenwald lectures, rare but profound
- Nomad Partnership (Sleep/Zakaria) — complete letter archive online, foundational
- Pabrai Funds — annual letters and Dakshana charity presentations
- Substack: Yet Another Value Blog (Andrew Walker), Kingswell (Alex Morris), Verdad Capital

---

## Books Revealing Philosophy (Required Reading)

- "The Education of a Value Investor" — Guy Spier (reveals entire process)
- "The Dhandho Investor" — Mohnish Pabrai (concentrated value framework)
- "Margin of Safety" — Seth Klarman (out of print, foundational)
- "Richer, Wiser, Happier" — William Green (profiles Pabrai, Spier, Marks, Klarman)
- "The Most Important Thing" — Howard Marks (cycle-based framework)
- "100 Baggers" — Chris Mayer (quality compounder identification)
- "Quality Investing" — Lawrence Cunningham (Akre/Dorsey school)
- "Poor Charlie's Almanack" — Munger's mental models
- "Value Investing" — Bruce Greenwald (Columbia framework, Li Lu's intellectual home)

---

## Conferences & Events Calendar

- **Berkshire Hathaway Annual Meeting** — Premier event, 40K+ investors
- **Ira Sohn Investment Conference** — Invitation-only, managers present best ideas
- **Grant's Interest Rate Observer Conference** — Deep value, contrarian thinkers
- **VALUEx Vail / VALUEx Klosters** — Spier, Pabrai, Buffett disciples, ideas shared freely
- **Pabrai Annual Meeting** — Investment discussions + Dakshana Foundation events
- **Robin Hood Investors Conference**
- **Capitalize for Kids (Canada)**
- **Value Investing Congress**

---

## 13F Staleness Mitigation

13F filings are reported as of quarter-end but due 45 days later. Mitigation:
- **Price Gap Analysis** — If stock rose 20%+ since quarter-end, signal is stale
- **Form 4 Cross-Reference** — Insider buying at target company strengthens signal
- **News Leading Indicators** — Confidential treatment filings suggest active accumulation
- **Thesis Durability** — If thesis was discussed months ago, still valid despite price move
- **Value Investor Timeframe** — 10-20% price move is noise over a 10-year horizon

---

---

## Intelligence Data Pyramid

```
LEVEL 1: SEC Mandatory Filings (most reliable, most delayed)
  13F-HR  — quarterly, $100M+ managers, long equity only
  13F-NT  — extension notice (signals complex portfolio)
  Form 4  — insider buys/sells within 2 days (NEAR REAL TIME)
  13D/13G — 5%+ ownership stakes (activist/concentrated)
  Form 3  — new insider positions

LEVEL 1B: Congressional Trading (STOCK Act Disclosures)
  Senate — periodic transaction reports (PTR), filed within 45 days
  House  — periodic transaction reports (PTR), filed within 45 days
  Track via: CapitolTrades.com, QuiverQuant.com, SenateTrades.com
  Notable traders: Pelosi, Tuberville, Crenshaw, Ossoff
  Signal: Congress members sit on committees with regulatory/contract info

LEVEL 2: International Regulatory Filings
  SEDAR+         — Canada (Watsa, Rochon)
  Companies House — UK (Terry Smith)
  AMF France     — French investors
  ASIC Australia — Australian managers

LEVEL 3: Voluntary Disclosures (high quality, irregular)
  Annual/quarterly shareholder letters
  Conference presentations (Ira Sohn, VALUEx, Dakshana)
  Annual meeting transcripts

LEVEL 4: Media Intelligence (wide net, filtered)
  YouTube deep dives and interviews
  Podcast interviews with managers
  Substack/newsletter analysis
  Book interviews and profiles
  Twitter/X threads from credible analysts
```

---

## Intelligence Confidence Levels

| Level | Source | Confidence | Action |
|-------|--------|-----------|--------|
| 🟢 CONFIRMED | 13F, Form 4, 13D, official filing | 95%+ | Enter convergence engine |
| 🔵 HIGH | Shareholder letter, conference talk | 85-95% | Enter convergence engine |
| 🟡 MEDIUM | Credible interview, TIER 1 media | 70-85% | Watchlist, verify next quarter |
| 🟠 LOW | TIER 2 media, secondhand report | 50-70% | Log only, don't act |
| 🔴 UNVERIFIED | Rumor, tweet, anonymous | <50% | Ignore |

Only 🟢 and 🔵 feed into convergence scoring. 🟡 enters watchlist for verification.

---

## Non-13F Investor Tracking Methods

| Investor | Why No 13F | How We Track |
|----------|-----------|-------------|
| Terry Smith (Fundsmith $23B) | UK-based | fundsmith.co.uk annual report, top 10 holdings |
| Nick Sleep (Nomad, closed) | Fund closed 2014 | Letter archive — framework study only |
| Francois Rochon (Giverny $700M) | Canadian | SEDAR+ filings + annual letters |
| Prem Watsa (Fairfax $50B) | Canadian holdco | SEDAR+ + Fairfax annual letter |
| Dev Kantesaria (Valley Forge) | Possibly under threshold | Conference presentations, rare interviews |
| International managers | Non-US jurisdiction | Letters, conferences, media interviews |

---

## Media Source Scoring Rubric (50 points)

| Criterion | Max | Description |
|-----------|-----|-------------|
| Value Investing Alignment | 15 | DCF, intrinsic value, moats, margin of safety — not charts/momentum |
| Super Investor Focus | 10 | Covers 13F filings, investor letters, conference presentations |
| Depth Over Hype | 10 | 20-min deep dive > "TOP 10 STOCKS TO BUY NOW" clickbait |
| Track Record / Credentials | 10 | Former fund manager, CFA, author, academic > random guy with ring light |
| Intellectual Honesty | 5 | Discusses mistakes, not just winners |

**Thresholds:**
- 40-50: 🟢 TIER 1 — always monitor, recommend to Joe
- 30-39: 🟡 TIER 2 — monitor, recommend selectively
- 20-29: ⚠️ Watchlist — check occasionally
- Below 20: ❌ Reject — day traders, clickbait, skip

**Auto-Reject Filters:**
- "TO THE MOON" / rocket emoji thumbnails
- Primarily meme stocks, crypto pumps, options gambling
- No fundamental analysis discussion
- Promotes paid stock-picking services as primary business
- Less than 2 years of consistent content
- Changes conviction weekly based on price action

---

## Curated Media Sources

### TIER 1 YouTube (Score 40+)
1. **Aswath Damodaran** (~500K) — NYU professor, valuation godfather — 48
2. **The Swedish Investor** (~800K) — Buffett/Munger book summaries — 45
3. **Patrick Boyle** (~900K) — ex-hedge fund, data-driven — 44
4. **Sven Carlin PhD** (~250K) — European value, independent — 42
5. **Investor Center** (~200K) — 13F deep dives quarterly — 41
6. **Compounding Quality** (~100K) — Akre/Dorsey style — 40

### TIER 1 Podcasts (Score 40+)
1. **We Study Billionaires / TIP** — Buffett/value focused — 47
2. **The Acquirer's Podcast** (Tobias Carlisle) — deep value interviews — 45
3. **Capital Allocators** (Ted Seides) — institutional allocators — 44
4. **Focused Compounding** (Gannon & Rosenblum) — concentrated value — 43
5. **Value After Hours** (Carlisle/Taylor/Brewster) — weekly roundtable — 42

### TIER 1 Substack/Newsletters (Score 40+)
1. **The Manual of Ideas** (Mihaljevic) — super investor profiles — 46
2. **Yet Another Value Blog** (Andrew Walker) — deep value — 45
3. **Kingswell** (Alex Morris) — quality compounders — 43
4. **Verdad Capital** — quantitative value research — 42
5. **Superinvestor Bulletin** — 13F analysis — 41

### TIER 2 YouTube (Score 30-39)
- **InvestorBridge/YAPSS** (~30K) — investor letters coverage — 38
- **New Money** (~1.5M) — mainstream, good Buffett coverage — 35
- **The Plain Bagel** (~1M) — Canadian value, clear — 33
- **Graham Stephan** (~4.5M) — mainstream, occasional value content — 30

### REJECTED
- Meet Kevin, Stock Moe, Jeremy Financial Education — clickbait/hype
- All "day trading live" channels
- All options income strategy channels
- All channels that change conviction weekly based on price

---

## Full Proposal Reference

The complete Super Investor Cloning Intelligence System proposal (all sections, detailed architecture, full investor profiles, implementation timeline) is available as a Word document:

`projects/investing/super-investor-system-proposal.docx`

This MOSE.md is the living operational playbook. The proposal doc is the original strategic vision.

---

*Last updated: April 10, 2026*
*"Be fearful when others are greedy, be greedy when others are fearful." — Warren Buffett*
*"I believe in the discipline of mastering the best that other people have ever figured out." — Charlie Munger*

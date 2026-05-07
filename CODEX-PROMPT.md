# MOSE Dashboard — Full Build Prompt
*For Codex GPT-5.5 — May 7, 2026*

---

## What You Are Building

A live, hosted investment intelligence dashboard called **MOSE — Margin of Safety Engine** (🦞). This is Joe Lynch's primary tool for tracking what the world's best super investors are buying and selling, so he can clone their highest-conviction positions.

The dashboard will be deployed to **GitHub Pages** at `roblobsterclaw.github.io/mose/`.

---

## Design Spec

- **Dark theme:** background `#0D1117`, cards `#161B22`, borders `#30363D`
- **Accent orange:** `#FF6B00`
- **Gold highlights:** `#C59E3C`
- **Font:** System sans-serif stack
- **Mobile responsive** — Joe checks this on his iPhone constantly
- **Single HTML file** — all JS/CSS embedded. NO build tools, NO npm, NO frameworks
- The header on every page must read: `🦞 MOSE — Margin of Safety Engine` with `Last updated: [timestamp]` below it

---

## The 6 Tabs to Build

### TAB 1 — CONVERGENCE SCORE
*"What are ALL the super investors buying right now?"*

Show a ranked table of stocks, sorted by convergence score (how many super investors own them):
- Ticker, Company Name, Current Price (live), Convergence Score, # of investors holding it, % of those investors who are Tier 1, Total conviction % (sum of position sizes)
- Color-code by score: 80+ = green, 50-79 = yellow, below 50 = grey
- Clicking a stock opens a detail panel showing WHICH investors hold it and their position size %
- Data source: `reference-data/convergence-master.json` (already pulled — load this file)
- Live price: fetch from Yahoo Finance unofficial API: `https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d`

### TAB 2 — INVESTOR PROFILES
*"Deep dive on each super investor"*

Show all 33 investors from the protocol. For each:
- Name, Fund, Tier badge (📊 13F / 📜 Letters / 👑 Legacy / 🌐 Public), AUM, # of holdings
- Last filing date
- Top 5 holdings with % of portfolio
- Trend indicator per holding: 📈 Adding / ➡️ Holding / 📉 Trimming / 🚪 Exited
- Clicking an investor expands their full portfolio

**The 33 investors to include** (load from `reference-data/MOSE-DATA-PROTOCOL.md`):

Tier 1 (13F — 22 investors): Buffett, Li Lu, Pabrai, Akre, Spier, Klarman, Ackman, Einhorn, Gayner, Hohn, Dorsey, Bloomstran, Russo, Tepper, Burry, Greenberg, Kantesaria, Sosin, Norbert Lou, Chris Mayer, Greenblatt, Bancroft

Tier 2 (Letters — 3): Terry Smith (Fundsmith UK), François Rochon (Giverny Canada), Prem Watsa (Fairfax Canada)

Tier 3 (Legacy — 3): Charlie Munger, Peter Lynch, John Templeton

Tier 4 (Public — 4): Kevin O'Leary, Bruce Greenwald, Todd Combs, Ted Weschler

Plus Joe Lynch himself ("Student of the Game 📚")

For investors whose 13F data is not yet loaded, show a "13F Not Yet Loaded" badge and their known positions from public sources/letters if available. Do NOT make up data — show clearly what is real vs. placeholder.

### TAB 3 — MY WATCHLIST
*"Joe's personal watch list — stocks he's tracking"*

This is the tab Joe can customize. Features:
- Add any ticker manually — user types in a ticker and it gets added
- Live price auto-populated via Yahoo Finance API
- Custom notes field for each stock (Joe types why he's watching it)
- Remove button to delete from watchlist
- Data persists in `localStorage` so it survives page refreshes
- Shows: Ticker, Company Name, Current Price, 52-week high/low, P/E ratio (from Yahoo), Joe's notes, Date added
- Pre-populated with Joe's known portfolio: V, MA, FICO, MELI, PGR, BABA, AXP, BRK-B, AAPL (these are his holdings — mark them with a 💼 "Holding" badge)

### TAB 4 — SIGNALS
*"What's moving right now across the super investor universe?"*

An alerts/signals feed showing:
- **Strong Buy Signals:** Stocks where 3+ investors are adding simultaneously (last 2 quarters)
- **Exit Warnings:** Stocks where investors are trimming/exiting (last 2 quarters)  
- **New Positions:** First-time appearances in any 13F this quarter
- **Forever Holds:** Positions held 8+ quarters with no trimming (highest conviction)
- Pull this data from the convergence master JSON and investor data already loaded
- Format as a clean feed with timestamp, signal type badge, and affected ticker

### TAB 5 — DATA STATUS
*"Is my data fresh? When does it expire?"*

A status board showing:
- For each of the 22 Tier 1 investors: Last 13F pull date, filing date, next expected filing date, status (✅ Fresh / ⚠️ Aging / ❌ Stale)
- Next 13F deadline: **May 15, 2026** (Q1 2026 filings due)
- Quarterly filing calendar for the year
- A "Refresh All" button that shows Joe the Python command to run to re-pull all 13Fs: `python3 pull_13f.py` (don't auto-execute — just display it clearly)
- Last updated timestamp for the whole dashboard

### TAB 6 — PORTFOLIO TRACKER
*"Joe Lynch's actual portfolio"*

Joe's current holdings (pre-populate from the known data):
- V (Visa), MA (Mastercard), FICO (Fair Isaac), MELI (MercadoLibre), PGR (Progressive), BABA (Alibaba), AXP (American Express), BRK-B (Berkshire Hathaway), AAPL (Apple)
- For each: Current price (live), % gain/loss from Joe's approximate entry (use his March/April 2026 execution prices if known), current value
- Total portfolio value
- Show how his holdings compare to super investor consensus (which of Joe's stocks have the highest convergence scores?)
- Note: Joe deployed ~$1.5M in late April 2026

---

## Live Price Data

Use the Yahoo Finance unofficial API — it's free and requires no API key:

```javascript
async function getPrice(ticker) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`;
  const resp = await fetch(url, {headers: {'User-Agent': 'Mozilla/5.0'}});
  const data = await resp.json();
  return data.chart.result[0].meta.regularMarketPrice;
}
```

For 52-week high/low and P/E:
```javascript
const url = `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${ticker}?modules=summaryDetail,defaultKeyStatistics`;
```

Load prices on page load for all tracked tickers. Show a loading spinner while fetching. Cache prices in memory for 15 minutes to avoid rate limiting.

---

## Data Loading

Load `reference-data/convergence-master.json` via a fetch() call at startup:
```javascript
const data = await fetch('./reference-data/convergence-master.json').then(r => r.json());
```

This file has:
- `investors` — object with investor data keyed by name
- `convergence_rankings` — array of stocks sorted by convergence score
- `total_unique_stocks` — 263
- `investors_pulled` — list of successfully loaded investors
- `investors_failed` — list that couldn't be loaded

---

## Watchlist Persistence

```javascript
// Save
localStorage.setItem('mose_watchlist', JSON.stringify(watchlist));
// Load
const watchlist = JSON.parse(localStorage.getItem('mose_watchlist') || '[]');
```

---

## File Output

Produce exactly these files:
1. `index.html` — the complete dashboard (all tabs, all JS/CSS embedded)
2. `pull_13f.py` — Python script to re-pull fresh 13F data from SEC EDGAR and update `reference-data/convergence-master.json`. Use the SEC EDGAR full-text search API: `https://efts.sec.gov/LATEST/search-index?q=%22{cik}%22&dateRange=custom&startdt=2024-01-01&forms=13F-HR`
3. `deploy.sh` — GitHub Pages deploy script (same pattern as other projects — preserve the data folder, use `git subtree push --prefix . origin gh-pages`)
4. Update `BUILD-LOG.md` with what you built, any architecture decisions, and verification steps

---

## Quality Rules (CRITICAL — Joe's family finances depend on this)

- **NEVER display fake or made-up investment data.** If you don't have real data for an investor, show "Data not yet loaded" clearly.
- **NEVER show stale prices as current.** Always show the timestamp of when price data was last fetched.
- **Label every data point with its source** (13F filing date, Yahoo Finance, etc.)
- **Show a clear warning** if any data is more than 6 months old.
- Convergence scores are based on real 13F filings — do NOT invent positions.

---

## Deploy Instructions (add to deploy.sh)

```bash
#!/bin/bash
# MOSE Dashboard Deploy Script
# Safe deploy — preserves data/ and reference-data/ folders

REPO="roblobsterclaw/mose"
BRANCH="gh-pages"

echo "Deploying MOSE Dashboard to GitHub Pages..."
git add -A
git commit -m "MOSE Dashboard update $(date '+%Y-%m-%d %H:%M')"
git push origin main

# Deploy to gh-pages (creates branch if needed)
git push origin `git subtree split --prefix . main`:gh-pages --force

echo "Live at: https://roblobsterclaw.github.io/mose/"
```

---

When done, update BUILD-LOG.md with:
- What was built
- Tab-by-tab status (working / placeholder)
- Any known issues
- How to deploy

# MOSE Data Protocol — Approved April 16, 2026
*This document governs how investment data is sourced, verified, and displayed.*
*Both Rob and Hermes must follow this protocol. Joe's family wealth depends on accuracy.*

## WHY THIS MATTERS
Joe is deploying ~$1.5M into a concentrated portfolio by April 30, 2026. The MOSE dashboard is his primary tool for deciding WHERE to put that money, based on cloning super investor conviction positions. Bad data = bad decisions = real financial harm to Joe, Keli, Juliana, Isabella, and Danielle. This is not a toy.

## DATA TIERS

### Tier 1: 13F Filers (SEC EDGAR) — GOLD STANDARD
- Mandatory quarterly filings for funds managing $100M+
- Complete snapshot of ALL US-listed positions over $200K
- Filed within 45 days of quarter end (Feb 14, May 15, Aug 14, Nov 14)
- Badge: 📊 13F (green)
- **Pull last 12 quarters (3 years) for entry price estimation and trend analysis**

### Tier 2: Annual Letters & Fund Reports
- Non-US or smaller/closed funds
- Published annually (Jan-Mar for prior year)
- Less precise — may lack exact share counts
- Badge: 📜 Letters (blue)
- Refresh annually, present to Joe for verification before adding

### Tier 3: Legacy / Philosophy Only
- Retired, deceased, or closed funds
- Last known positions from final filings, books, interviews
- Badge: 👑 Legacy (gold)
- Static — no refresh needed

### Tier 4: Public / Media / Limited Data
- TV, social media, podcast disclosures
- Least reliable — awareness only, not for cloning decisions
- Badge: 🌐 Public (grey)
- Always present to Joe before treating as actionable

## 13F ANALYSIS PROTOCOL

### Historical Pull: 12 quarters (3 years)
For each investor, compare quarter-over-quarter to detect:
- **New positions** — first appearance = estimated entry price
- **Additions** — share count increasing = adding conviction
- **Trims** — share count decreasing = reducing exposure
- **Exits** — position disappears = they're out
- **Forever holds** — 8+ quarters, no trimming = highest conviction

### What to show per holding:
- Ticker, shares, current value, % of portfolio
- Estimated entry quarter and price
- Current trend: 📈 Adding / ➡️ Holding / 📉 Trimming / 🚪 Exited
- Hold duration (quarters)
- Conviction level (based on hold length + drawdown survival)
- Unrealized gain/loss vs estimated entry

### Critical display: TRIMMING OR ADDING LATELY
- Most recent 2-3 quarters highlighted
- If an investor is trimming a position we're considering buying — that's a WARNING
- If multiple investors are adding the same stock — that's a STRONG SIGNAL

## QUALITY RULES
- ⛔ NEVER invest based on stale data (>6 months = flagged outdated)
- ⛔ NEVER treat Tier 3/4 data as equal to Tier 1
- ⛔ NEVER use Joe's old spreadsheet data as current holdings
- ✅ Convergence scoring weights: Tier 1 highest, Tier 2 medium, Tier 3-4 lowest
- ✅ Every holding shows data source and filing date
- ✅ Quarterly auto-refresh cron after each filing deadline
- ✅ New investors proposed to Joe before adding
- ✅ All data changes logged

## INVESTOR LIST (33 confirmed)

### Tier 1 — 13F Filers (22)
Buffett, Li Lu, Pabrai, Akre, Spier, Klarman, Ackman, Einhorn, Gayner, Hohn, Dorsey, Bloomstran, Russo, Tepper, Burry, Greenberg, Kantesaria, Sosin, Norbert Lou, Chris Mayer, Greenblatt, Bancroft

### Tier 2 — Letters/Reports (3)
Terry Smith (Fundsmith UK), François Rochon (Giverny Canada), Prem Watsa (Fairfax Canada)

### Tier 3 — Legacy (3)
Charlie Munger, Peter Lynch, John Templeton

### Tier 4 — Public (4)
Kevin O'Leary, Bruce Greenwald, Todd Combs (embedded in BRK), Ted Weschler (embedded in BRK)

### The Boss — Joe Lynch
Holdings from actual brokerage statements (Truist, Schwab, IBKR)
Rated: "Student of the Game 📚"

## REFRESH SCHEDULE
- **After each 13F deadline (quarterly):** Full pull for all Tier 1 filers
- **January-March (annually):** Research Tier 2 annual letters
- **Weekly:** Refresh stock prices for all tracked positions
- **On-demand:** When Joe requests or when major market events occur

---
*Approved by Joe Lynch — April 16, 2026, 3:25 AM*
*"This will positively or negatively affect in a big way the lives of my girls and my wife Keli."*
*We don't take that lightly. Accuracy over speed. Every time.*

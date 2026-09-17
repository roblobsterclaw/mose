# Comprehensive retirement plan — working draft

**Owner:** Joe Lynch, age 57 (RMD age 75). **Keli** died July 22, 2026.
**Started:** 2026-09-17. Living document; every number here is an estimate to be
replaced by a sourced figure. Companion files: `retirement-action-list.md`,
`step-up-basis-worksheet.md`, `truist-baseline-feb2026.json`.

## 1. The goal, in numbers

Joe wants to keep the income he lives on today through retirement, keep growing
the portfolio, and carve out a separate sleeve to invest with and to seed AI
businesses.

| | Amount |
|---|---:|
| Salary today (gross) | $235k |
| Take-home after federal, NJ and FICA (single, 2026 law) | ~$162k |
| Retirement withdrawal to replace that, if drawn from Roth or stepped-up taxable money | ~$162k |
| Same, if half comes from a pre-tax IRA | ~$175k |

The target is therefore **about $165k to $175k a year of spendable money, rising
with inflation**, not $235k. Tax-free and stepped-up sources are what make the
number that low.

## 2. Where the money is today (2026-09-17)

**IBKR, Joe's IRA — live pull.** Net liquidation $948,968. Of that, $844,662 is
SGOV (T-bills), $10,030 cash, and ~$90k in 53 stock positions, most of them
one-share placeholders. **The IRA is 89% cash-equivalent.** Time-weighted
return since the account opened on 2026-05-27 is +0.7%.

| Account | Value | Source | Notes |
|---|---:|---|---|
| Joe's IRA (IBKR) | $949k | live | 89% SGOV, not yet deployed |
| Keli's Rollover IRA (IBKR) | ~$199k | Tiller, Aug 22 | separate login; keep titled as inherited until Joe is 59½ |
| Joint brokerage (IBKR) | ~$326k | Tiller, Aug 22 | Keli's half gets a stepped-up basis |
| Fourth IBKR account | ? | handoff says 4 accounts, $1.49M total | identify |
| ADP Roth 401(k)s (Joe + Keli) | ~$63k | Tiller | roll Keli's into Joe's Roth IRA |
| JPMorgan Funds | ~$154k | Tiller | type unknown |
| Kearny Federal Savings | ~$758k | Tiller | 2 accounts; if this is personal cash it is the largest liquid pool after the IRA |
| Vanguard | ~$6k | Tiller | $500/month going in |
| Business interests (TLC/SurfBox 48.33%, Greenville Colorants 40%) | ~$4.75M net | Tiller balance sheet | book value at Joe's share, not a sale price |
| Personal net worth at Joe's share | ~$6.36M | Tiller | includes real estate |
| Total equity incl. businesses | ~$11.1M | Tiller | |

Liquid and investable today, if Kearny is personal cash: **about $2.46M.**

## 3. When can Joe retire?

Monte Carlo, 8,000 paths, 90/10 stocks/treasuries (9.0% mean, 15.3%
volatility), 3% inflation, spending $162k real per year, Social Security ~$45k
from age 70. "Assets at retire" = today's liquid money grown at 7% plus ~$150k a
year of savings while working, plus after-tax sale proceeds.

| Scenario | Assets at retirement | Never runs out | Ends above start (real) | Median ending (real) |
|---|---:|---:|---:|---:|
| A. Sell businesses 2027 for $4.75M, retire at 58 | $6.1M | 98% | 83% | $18.6M |
| B. Sell 2029 for $5.5M, retire at 60 | $7.3M | 99% | 87% | $25.4M |
| C. Sell 2031 for $6.5M, retire at 62 | $8.7M | 100% | 90% | $33.1M |
| D. Never sell; retire from operations at 60, live on $2.5M liquid plus $150k/yr of distributions | $3.5M | 100% | 97% | $17.4M |

**Reading it.** On the money alone, Joe can retire at 58 the moment the
businesses sell, at a 2.6% withdrawal rate, which is safer than anything we
tested in the $8M runs. Each extra working year adds roughly $1M of assets and
a few points of certainty, but the plan is already sound at A. **The real
decision is not when, but whether to sell at all.** Scenario D, keeping the
businesses as an income stream and stepping back from operations, is the most
robust of the four because the distributions do the portfolio's work in bad
market years. That only works if the businesses run without Joe and the
distributions are dependable. If they need him, sell.

**Recommended framing:** target retirement from operations at **60 (2029)**,
with the businesses either sold in 2028 to 2029 or restructured to pay
distributions without him. 2029 is also the first single-filer year, which
matters for the sale (below), and 59½ is when Keli's IRA can be merged.

## 4. Selling the businesses: the tax is the plan

Assumed basis $500k; everything above is long-term capital gain. NJ has no
capital-gains rate: gains are ordinary income, 8.97% from $500k to $1M and
10.75% above $1M, so a $4M+ gain sits mostly in NJ's top bracket.

| Sale price | Tax in one year | Net | Tax if paid in 3 installments after retiring |
|---|---:|---:|---:|
| $3.5M | $0.99M (33%) | $2.5M | $0.86M (29%) |
| $4.75M | $1.43M (34%) | $3.3M | $1.29M (30%) |
| $6.0M | $1.86M (34%) | $4.1M | $1.72M (31%) |

Roughly a third of the price goes to tax. Things that move that number, for
the CPA and a deal attorney, in order of size:

1. **Did Keli own any part of the business interests?** If any share was in her
   name or held jointly, that share steps up to its July 22, 2026 value and the
   gain on it disappears. This is potentially the single largest tax item in
   the whole plan. See the step-up worksheet.
2. **Installment sale.** Spreading the gain over 3 to 5 years keeps each year
   below NJ's 10.75% bracket and the federal 20% threshold. Saves about $140k
   on a $4.75M sale, more if it also spreads NIIT.
3. **Residency.** NJ taxes a resident's gain wherever it arises. The sourcing
   rules for a nonresident selling an interest in a NJ business are complex and
   changed in recent years; do not assume a move solves it. Ask.
4. **Timing against the Roth window.** Do not convert in a sale year. The gain
   stacks on top of ordinary income and pushes conversion dollars into 35%+.
5. **Sell in 2028 or 2029, not 2027 if avoidable.** Gives one more year of
   salary, one more joint-bracket conversion year, and lets the July 2026
   step-up values settle before a transaction values the company.
6. **Qualified Small Business Stock does not apply** to LLC interests. If any
   entity is a C-corp, ask.

## 5. Roth conversions, integrated with the sale

The 2026 to 2028 joint-bracket window from the earlier analysis still holds.
Keli's death makes the case stronger, and the business sale makes sequencing
matter.

| Year | Age | Filing | Convert | Why |
|---|---|---|---|---|
| 2026 | 57 | joint | ~$204k | fills 24%; last guaranteed joint year; convert SGOV cash, no timing needed |
| 2027 | 58 | surviving spouse | ~$204k | same |
| 2028 | 59 | surviving spouse | ~$204k, or $0 if this is the sale year | |
| sale year | | single | $0 | gain stacks; every conversion dollar costs 35%+ |
| post-sale, pre-SS | 60 to 69 | single, ~$60k other income | ~$166k/yr | fills 24% at ~28% combined; finishes the traditional IRA by ~67 |
| 70+ | | single | remainder | Social Security narrows the room |

Roth at 59 on this schedule: roughly $750k to $800k at 8%. Roth at 67 after
the post-sale conversions: $2M or more. That is the tax-free income sleeve.

**Convert SGOV, not stocks, for the 2026 tranche.** With the IRA 89% in
T-bills there is no "convert on a down day" edge yet. Move $204k of SGOV into
the Roth, then deploy it into the highest-growth bucket names inside the
Roth. The conversion tax (~$61k) comes from the joint account or Kearny cash.

## 6. Income architecture in retirement

Which bucket pays, in order, so that taxable income stays inside the 24%
bracket every year and IRMAA surcharges stay low:

1. **Business distributions or installment payments**, while they last.
2. **Joint taxable account** with stepped-up basis: cheapest dollars first.
3. **Roth**: for anything above the bracket line, and for lumpy spending.
4. **Traditional IRA / Keli's inherited IRA**: only to fill the 24% bracket
   via conversions, never for spending, until RMDs force it at 75.
5. **Social Security at 70** on Joe's own record; survivor benefit on Keli's
   record from 60 if it is higher than what Joe's own would be at 70, else
   take survivor at 60 and switch to own at 70.

The spending rule Joe proposed, $500k in years the portfolio returns 1% or
more and nothing in years it does not, tested well only when skip years are
funded from outside the portfolio. Under this architecture the business
distributions and the Roth are that outside source, which is why keeping some
distribution income (Scenario D) is so valuable.

## 7. The "play money" sleeve

Purpose: a separate account for concentrated stock bets and seed money for AI
businesses, walled off so a loss never touches the income engine.

- **Size:** 5% of liquid assets at retirement, capped at $400k. Today that is
  about $125k; after a sale about $300k to $400k.
- **Home:** a separate IBKR taxable account, not the IRA and not the Roth.
  Losses in a taxable account are at least deductible; in a Roth they are
  wasted; in an IRA they cost future conversion capacity.
- **Refill rule:** it is refilled only from its own gains or from a fresh
  business-sale tranche, never from the income portfolio. When it is gone it
  is gone until the next liquidity event.
- **AI businesses:** fund from this sleeve up to its cap; anything larger is a
  board-level decision with a written plan, not a portfolio decision. A
  business Joe works in is also a source of earned income, which reopens
  Roth contributions and solo-401(k) space in retirement.

## 8. The IRA is not deployed

89% of Joe's IRA is in T-bills earning ~4%. The MOSE buy targets exist to fix
this. Every year the IRA sits in SGOV, the compounding the whole plan assumes
does not happen. The 2026 conversion is a natural first deployment: convert
SGOV to Roth, then buy the AI core and forever-compounder targets inside the
Roth. Deploy the rest of the IRA in tranches over 6 to 12 months per the buy
list, keeping the Cash & T-bills bucket at its parked target.

## 9. Estate

- Form 706 portability election by **April 22, 2027** (extension to
  October 22, 2027). At $11M+ of equity this is necessary, not optional.
- Step-up worksheet for the CPA: `step-up-basis-worksheet.md`.
- Beneficiaries on every account; Keli was almost certainly primary.
- Consider a revocable trust once the business sale is in sight, so the
  proceeds and the house avoid NJ probate for the kids.

## 10. Assumptions and open questions

Assumptions: 9% mean return on 90/10, 3% inflation, business basis $500k,
sale prices as tabled, $150k/yr saved while working, Social Security $45k at
70, spending flat in real terms, NJ residency throughout, 2026 tax law
unchanged.

Open, in priority order:
1. Did Keli own any share of TLC/SurfBox or Greenville Colorants? (step-up)
2. What is Kearny Federal: personal cash, business cash, or CDs?
3. What is the fourth IBKR account, and what is in JPMorgan Funds?
4. Can the businesses run without Joe, and what do they distribute today?
5. Realistic sale multiple and whether a buyer would do an installment deal.
6. Social Security statements for Joe and for Keli's record.
7. House value, mortgage balance (Shellpoint $602k?), and whether it stays.
8. Do the kids still qualify as dependents through 2028 (ages)?

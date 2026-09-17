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
| Schwab | ~$2k | Joe | the "fourth" brokerage account; negligible |
| ADP Roth 401(k)s (Joe + Keli) | ~$63k | Tiller | roll Keli's into Joe's Roth IRA |
| Vanguard | ~$6k | Tiller | $500/month going in |
| Business interests (TLC/SurfBox 48.33%, Greenville Colorants 40%) | ~$4.75M net | Tiller balance sheet | book value at Joe's share. **Keli held part of these interests (confirmed 2026-09-17); her share steps up.** |
| Primary home mortgage (Kearny Federal) | ~$758k owed | Joe | liability, not cash |
| Shellpoint mortgage | ~$602k owed | Tiller | which property? |
| Personal net worth at Joe's share | ~$6.36M | Tiller | includes real estate |
| Total equity incl. businesses | ~$11.1M | Tiller | |

Liquid and investable today: **about $1.55M** (IBKR $1.49M, Roth 401(k)s
$63k, Schwab $2k). There is no JPMorgan account; Kearny is the home mortgage.
Two mortgages totaling ~$1.36M sit against the real estate.

## 3. When can Joe retire?

Monte Carlo, 8,000 paths, 90/10 stocks/treasuries (9.0% mean, 15.3%
volatility), 3% inflation, spending $162k real per year, Social Security ~$45k
from age 70. "Assets at retire" = today's $1.55M liquid grown at 7% plus ~$150k
a year of savings while working, plus after-tax sale proceeds with Keli's half
of the business stepped up. Sale figures are Joe's share.

| Scenario | Assets at retirement | Never runs out | Ends above start (real) | Median ending (real) |
|---|---:|---:|---:|---:|
| A. Sell everything 2027 for $4.75M, retire at 58 | $5.9M | 98% | 82% | $17.4M |
| B. Sell everything 2029 for $4.75M, retire at 60 | $6.4M | 99% | 85% | $20.9M |
| **C. Sell the operating business 2029 (~$1M goodwill + ~$1M working capital), keep the real estate, net rent $150k/yr** | $4.2M | 100% | 97% | $21.2M |
| D. Same as C with net rent of $100k/yr | $4.2M | 100% | 94% | $18.1M |
| E. Keep everything, retire from operations 2029, distributions $150k/yr | $2.4M | 100% | 97% | $11.6M |
| F. Sell everything 2029, retire at 62 | $7.4M | 99% | 88% | $26.5M |

**Reading it.** Every scenario works. Joe can retire at 58 the moment the
businesses sell, at a 2.5% withdrawal rate. But **scenario C is the standout**:
sell the operating business, keep the commercial real estate, and lease it to
the buyer. Rent is the "outside income" that makes the skip-bad-years rule
work, the withdrawal rate on the portfolio drops to almost nothing, and the
real estate keeps compounding and passes to the girls with a step-up. It also
sidesteps depreciation recapture and NJ's top bracket on the property gain.
The buyer of an operating business usually prefers to lease anyway.

**Recommended framing:** retire from operations at **60 (2029)**. Sell the
goodwill and working capital in 2028 or 2029. Keep the real estate unless a
buyer pays a premium for it, and even then consider a 1031 exchange into
passive property rather than a taxable sale. 59½ is also when Keli's IRA can
be merged into Joe's.

## 4. Selling the businesses: the tax is the plan

Assumed basis $500k; everything above is long-term capital gain. NJ has no
capital-gains rate: gains are ordinary income, 8.97% from $500k to $1M and
10.75% above $1M, so a $4M+ gain sits mostly in NJ's top bracket.

**Keli owned part of the business interests.** Her share stepped up to its
July 22, 2026 value, so the gain on that share is gone. Assuming her share was
half of the family stake:

| Proceeds (Joe's share) | Tax, no step-up | Tax with Keli's half stepped up | Saved | Net |
|---|---:|---:|---:|---:|
| $3.0M | $0.80M | $0.37M | $0.43M | $2.63M |
| $4.0M | $1.15M | $0.54M | $0.60M | $3.46M |
| $4.75M | $1.41M | $0.67M | $0.73M | $4.08M |

The step-up is worth roughly $600k to $750k. Getting it requires paperwork now,
not at sale:

1. **Section 754 election.** For an LLC taxed as a partnership, the step-up
   in Keli's interest only reaches the underlying assets (goodwill, real
   estate, equipment) if the partnership makes a 754 election, which produces
   a 743(b) basis adjustment for her share. Without it, an asset sale by the
   company flows the full gain through. The election goes on the partnership
   return for the year of death, i.e. the 2026 return. **Tell the CPA now.**
2. **Retrospective business valuation as of July 22, 2026.** The step-up is to
   fair market value on that date. A defensible appraisal fixes the number
   before a buyer's price does. Also needed for Form 706.
3. **Installment sale** of the goodwill: spreads NJ's 10.75% top bracket and
   the federal 20% threshold. Worth ~$100k+ on a $2M+ gain.
4. **Real estate: keep and lease, or 1031.** Selling it triggers depreciation
   recapture at 25% federal plus NJ ordinary rates on Joe's half. Leasing it
   to the buyer converts a taxable lump into an income stream that also
   qualifies for the 20% qualified business income deduction in many cases.
5. **Do not convert to Roth in the sale year.** The gain stacks on ordinary
   income and pushes conversion dollars to 35%+.
6. **Residency.** NJ taxes a resident's gain wherever it arises; nonresident
   sourcing of a NJ business sale is complex. Do not assume a move solves it.
7. **QSBS does not apply** to LLC interests; if any entity is a C-corp, ask.

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
Keli's share of the business = half of the family stake, sale prices as
tabled, $150k/yr saved while working, Social Security $45k at 70, spending
flat in real terms, NJ residency throughout, 2026 tax law unchanged.

Answered 2026-09-17: Keli held part of the businesses (share TBD). Kearny is
the primary-home mortgage. No JPMorgan account. Fourth account is Schwab,
~$2k. A sale would be ~$1M goodwill plus the real estate plus net working
capital, with values and mortgages on the balance-sheet workbook. Daughters
are 19 and 21 (in college) and 28.

**Filing status, settled:** the 19- and 21-year-olds qualify Joe as a
surviving spouse for 2027 and 2028 (joint brackets). From 2029 the 19-year-old
still qualifies him for **head of household** until the year she turns 24,
roughly 2031, which is better than single. The 28-year-old is not a dependent.

Still open, in priority order:
1. Keli's exact ownership percentage in each entity, and how it was titled.
2. Book value and mortgage on the business real estate; current net rent it
   could command if leased to a buyer. (Balance-sheet workbook, sheet 17.)
3. Can the operating business run without Joe, and what does it distribute?
4. Which property the Shellpoint mortgage is on.
5. Social Security statements for Joe and for Keli's record.
6. Primary-home value, and whether Joe stays in it.

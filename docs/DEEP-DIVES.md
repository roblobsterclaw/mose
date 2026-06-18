# MOSE Deep Dives — Versioning & Cadence Protocol

A deep dive is a point-in-time research report on one ticker (thesis, intrinsic
value, MOS price, convergence score, super-investor backing, risks, verdict —
see `reference-data/MOSE.md` for branding and section requirements).

## Versioning (do not overwrite old reports)

Every deep dive is kept forever so periods can be compared.

1. **Report file:** `deep-dives/<ticker>-deep-dive-YYYY-MM-DD.html`
   (lowercase ticker, date = report date). Never delete or overwrite an old
   report file.
2. **Library index:** append a NEW entry to `reports` in
   `research-library.json` — do not replace the ticker's previous entry.
   Multiple entries per ticker are expected. Each entry:

   ```json
   {
     "ticker": "GOOGL",
     "company": "Alphabet Inc.",
     "reportDate": "2026-07-25",
     "intrinsicValue": 415,
     "mosPrice": 332,
     "currentPrice": 351.2,
     "verdict": "BUY — ...",
     "verdictClass": "buy",
     "convergenceScore": 93,
     "superInvestors": ["Li Lu 21.0%"],
     "reportUrl": "https://roblobsterclaw.github.io/mose/deep-dives/googl-deep-dive-2026-07-25.html"
   }
   ```

The dashboard groups entries by ticker, shows the newest as the active card,
and renders the older ones in an expandable **History** timeline with deltas
(intrinsic value change, verdict change, convergence score change) between
consecutive reports.

## Cadence (monthly or quarterly per ticker)

- Each ticker has a refresh cadence, selectable on its Research Library card:
  **Quarterly** (default, due after 92 days) or **Monthly** (due after 31 days).
- Cadence choices sync across devices with the rest of the watchlist state
  (Firebase + localStorage key `mose_research_cadence`).
- When a ticker's latest report is older than its cadence, the dashboard:
  - shows a "update due" badge on its library card, and
  - resurfaces it at the top of the **Needs Deep Dive** lane with a
    Request Update button.
- Requesting an update adds it to `deep-dive-requests` (synced state), which
  is the queue the research sessions work from.

## Quality bar

The April 2026 reports (~170 KB, full analysis) are the standard. The May 22
one-screen summaries (MA, UBER, AXP) are below it — treat those as stubs to be
replaced at their next cadence date.

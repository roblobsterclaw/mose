#!/usr/bin/env python3
"""Build a NYSE/NASDAQ/AMEX ticker directory for the MOSE watchlist search.

The dashboard's "Add Stock" box searches this file, so you can find any listed
company by name or symbol instead of only the ~90 names MOSE already tracks.

Sources (all keyless):
  - SEC company_tickers.json  -> ticker + company name (~10k US filers)
  - Nasdaq Trader symbol dirs -> exchange label (NASDAQ / NYSE / NYSE American)

The SEC file is authoritative for the name/ticker pair; the Nasdaq Trader files
are best-effort decoration. If a source is unavailable the build still succeeds
on whatever it could fetch, and never overwrites a good directory with an empty
one.

Output: reference-data/ticker-directory.json
  {"generated_at": "...", "source": "...", "count": N,
   "symbols": [{"t": "AAPL", "n": "Apple Inc.", "e": "NASDAQ"}, ...]}
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reference-data" / "ticker-directory.json"

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

# SEC requires a descriptive User-Agent with contact info.
HEADERS = {"User-Agent": "MOSE dashboard ticker-directory (rob.lobster.claw@gmail.com)"}
MIN_SYMBOLS = 1000  # sanity floor: a real US directory has thousands of rows

EXCHANGE_NAMES = {
    "Q": "NASDAQ", "G": "NASDAQ", "S": "NASDAQ",
    "N": "NYSE", "A": "NYSE American", "P": "NYSE Arca",
    "Z": "Cboe BZX", "V": "IEX",
}


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_sec_symbols() -> dict[str, str]:
    """ticker -> company name from the SEC."""
    data = json.loads(fetch(SEC_TICKERS_URL).decode("utf-8"))
    out: dict[str, str] = {}
    for row in data.values():
        ticker = str(row.get("ticker") or "").strip().upper()
        name = str(row.get("title") or "").strip()
        if ticker and name:
            out[ticker] = name
    return out


def load_exchange_map() -> dict[str, str]:
    """ticker -> exchange label, best effort from Nasdaq Trader."""
    exchanges: dict[str, str] = {}
    # nasdaqlisted.txt: Symbol|Security Name|Market Category|Test Issue|...
    try:
        text = fetch(NASDAQ_LISTED_URL).decode("utf-8")
        for line in text.splitlines()[1:]:
            cols = line.split("|")
            if len(cols) > 3 and cols[3] == "N":  # not a test issue
                sym = cols[0].strip().upper()
                if sym and sym != "SYMBOL":
                    exchanges[sym] = "NASDAQ"
    except Exception as exc:
        print(f"nasdaqlisted.txt unavailable: {exc}")
    # otherlisted.txt: ACT Symbol|Security Name|Exchange|...
    try:
        text = fetch(OTHER_LISTED_URL).decode("utf-8")
        for line in text.splitlines()[1:]:
            cols = line.split("|")
            if len(cols) > 2:
                sym = cols[0].strip().upper()
                code = cols[2].strip().upper()
                if sym and sym != "ACT SYMBOL":
                    exchanges[sym] = EXCHANGE_NAMES.get(code, "NYSE")
    except Exception as exc:
        print(f"otherlisted.txt unavailable: {exc}")
    return exchanges


def main() -> int:
    sec = load_sec_symbols()
    if len(sec) < MIN_SYMBOLS:
        print(f"ERROR: SEC returned only {len(sec)} symbols; keeping existing directory.")
        return 1

    exchanges = load_exchange_map()
    symbols = []
    for ticker, name in sorted(sec.items()):
        entry = {"t": ticker, "n": name}
        if ticker in exchanges:
            entry["e"] = exchanges[ticker]
        symbols.append(entry)

    source = "sec" + ("+nasdaqtrader" if exchanges else "")
    OUTPUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "count": len(symbols),
        "symbols": symbols,
    }, separators=(",", ":")) + "\n")
    print(f"Wrote {len(symbols)} symbols to {OUTPUT.relative_to(ROOT)} (source: {source}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

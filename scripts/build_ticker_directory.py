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
import re
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

# SEC company_tickers.json only covers US filers, so commonly-tracked non-US
# listings (e.g. Constellation Software on the TSX) are missing. This curated
# supplement is always merged in. The "y" field is the Yahoo Finance quote
# symbol used by the quote job when it differs from the displayed ticker
# (TSX names need a ".TO" suffix; US-listed ADRs do not).
SUPPLEMENT = [
    # ticker, name, exchange, yahoo_symbol (None = same as ticker)
    ("CSU", "Constellation Software Inc.", "TSX", "CSU.TO"),
    ("ATD", "Alimentation Couche-Tard Inc.", "TSX", "ATD.TO"),
    ("CNR", "Canadian National Railway Company", "TSX", "CNR.TO"),
    ("SHOP", "Shopify Inc.", "NYSE", None),
    ("CBRS", "Cerebras Systems Inc.", "NASDAQ", None),
    ("NVO", "Novo Nordisk A/S (ADR)", "NYSE", None),
    ("TM", "Toyota Motor Corporation (ADR)", "NYSE", None),
    ("SAP", "SAP SE (ADR)", "NYSE", None),
    ("NVS", "Novartis AG (ADR)", "NYSE", None),
    ("SONY", "Sony Group Corporation (ADR)", "NYSE", None),
    ("RY", "Royal Bank of Canada", "NYSE", None),
    ("TD", "Toronto-Dominion Bank", "NYSE", None),
    ("RELX", "RELX PLC (ADR)", "NYSE", None),
    ("LVMUY", "LVMH Moet Hennessy Louis Vuitton (ADR)", "OTC", None),
    ("NSRGY", "Nestle S.A. (ADR)", "OTC", None),
]


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_sec_symbols() -> dict[str, str]:
    """ticker -> company name from the SEC (clean operating-company names)."""
    data = json.loads(fetch(SEC_TICKERS_URL).decode("utf-8"))
    out: dict[str, str] = {}
    for row in data.values():
        ticker = str(row.get("ticker") or "").strip().upper()
        name = str(row.get("title") or "").strip()
        if ticker and name:
            out[ticker] = name
    return out


# Keep plain tickers and simple class shares (BRK.B); drop warrants/units/rights
# and other suffixed junk that clutters an "add a stock" menu.
SYMBOL_RE = re.compile(r"^[A-Z]{1,5}([.][A-Z])?$")
DROP_SUFFIXES = {"W", "WS", "U", "R", "RT", "P", "WI"}


def _valid_symbol(sym: str) -> bool:
    if not SYMBOL_RE.match(sym):
        return False
    if "." in sym and sym.split(".")[1] in DROP_SUFFIXES:
        return False
    return True


def load_listed() -> dict[str, dict]:
    """Every listed security (stocks AND ETFs) from Nasdaq Trader's symbol
    directories -> {ticker: {name, exchange, etf}}. This is what gives us ETF
    coverage that SEC company_tickers.json lacks (VTV, VOO, NLR, ...)."""
    listed: dict[str, dict] = {}

    # nasdaqlisted.txt: Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot|ETF|NextShares
    try:
        for line in fetch(NASDAQ_LISTED_URL).decode("utf-8").splitlines()[1:]:
            if line.startswith("File Creation Time"):
                continue
            c = line.split("|")
            if len(c) < 7:
                continue
            sym = c[0].strip().upper()
            if not sym or sym == "SYMBOL" or c[3].strip() == "Y":  # skip header / test issues
                continue
            if not _valid_symbol(sym):
                continue
            listed[sym] = {"name": c[1].strip(), "exchange": "NASDAQ", "etf": c[6].strip() == "Y"}
    except Exception as exc:
        print(f"nasdaqlisted.txt unavailable: {exc}")

    # otherlisted.txt: ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot|Test Issue|NASDAQ Symbol
    try:
        for line in fetch(OTHER_LISTED_URL).decode("utf-8").splitlines()[1:]:
            if line.startswith("File Creation Time"):
                continue
            c = line.split("|")
            if len(c) < 7:
                continue
            sym = c[0].strip().upper()
            if not sym or sym == "ACT SYMBOL" or c[6].strip() == "Y":  # skip header / test issues
                continue
            if not _valid_symbol(sym):
                continue
            listed[sym] = {"name": c[1].strip(), "exchange": EXCHANGE_NAMES.get(c[2].strip().upper(), "NYSE"), "etf": c[4].strip() == "Y"}
    except Exception as exc:
        print(f"otherlisted.txt unavailable: {exc}")

    return listed


def _clean_name(name: str) -> str:
    # Trim the boilerplate Nasdaq tacks onto security names.
    for sep in [" - Common Stock", " - Class", " Common Stock", " - Ordinary Shares"]:
        i = name.find(sep)
        if i > 0:
            return name[:i].strip()
    return name.strip()


def main() -> int:
    sec = load_sec_symbols()
    if len(sec) < MIN_SYMBOLS:
        print(f"ERROR: SEC returned only {len(sec)} symbols; keeping existing directory.")
        return 1

    listed = load_listed()
    by_ticker: dict[str, dict] = {}

    # Base universe = every listed security (gives full ETF coverage). Prefer the
    # cleaner SEC company name for non-ETFs; use the Nasdaq name for ETFs.
    for ticker, info in listed.items():
        name = sec.get(ticker) if (not info["etf"] and ticker in sec) else None
        name = name or _clean_name(info["name"]) or ticker
        entry = {"t": ticker, "n": name, "e": info["exchange"]}
        if info["etf"]:
            entry["f"] = "ETF"
        by_ticker[ticker] = entry

    # Add SEC-only tickers that aren't in the Nasdaq files (rare, but keep them).
    for ticker, name in sec.items():
        if ticker not in by_ticker and SYMBOL_RE.match(ticker):
            by_ticker[ticker] = {"t": ticker, "n": name}

    # Merge the curated non-US supplement (adds/overrides; carries Yahoo quote symbol).
    for ticker, name, exchange, yahoo in SUPPLEMENT:
        entry = {"t": ticker, "n": name, "e": exchange}
        if yahoo:
            entry["y"] = yahoo
        by_ticker[ticker] = entry

    symbols = [by_ticker[t] for t in sorted(by_ticker)]
    etf_count = sum(1 for s in symbols if s.get("f") == "ETF")
    source = ("sec+nasdaqtrader" if listed else "sec") + "+supplement"
    OUTPUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "count": len(symbols),
        "etf_count": etf_count,
        "symbols": symbols,
    }, separators=(",", ":")) + "\n")
    print(f"Wrote {len(symbols)} symbols ({etf_count} ETFs) to {OUTPUT.relative_to(ROOT)} (source: {source}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

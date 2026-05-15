#!/usr/bin/env python3
"""Refresh MOSE live quote snapshot for GitHub Pages.

The public app is static, so it cannot keep a server-side market feed open.
This script writes live-quotes.json for the browser to poll. It uses Stooq's
CSV endpoint because it works without API keys and is suitable for a lightweight
watchlist snapshot.
"""

from __future__ import annotations

import csv
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"
OUTPUT = ROOT / "live-quotes.json"
INDICES_FALLBACK = ROOT / "indices-latest.json"


INDEX_SYMBOLS = {
    "S&P 500": ("^SPX", "^SPX"),
    "Dow Jones": ("^DJI", "^DJI"),
    "NASDAQ": ("^NDQ", "^NDQ"),
}


def stooq_symbol(ticker: str) -> str | None:
    ticker = ticker.strip().upper()
    if not ticker or ticker in {"ANTHR"}:
        return None
    if ticker.startswith("^"):
        return ticker
    return f"{ticker}.US"


def fetch_stooq(symbols: list[str]) -> dict[str, dict]:
    quotes: dict[str, dict] = {}
    for start in range(0, len(symbols), 60):
        chunk = symbols[start : start + 60]
        encoded = urllib.parse.quote("+".join(chunk), safe="+.^-")
        url = f"https://stooq.com/q/l/?s={encoded}&f=sd2t2ohlcv&h&e=csv"
        with urllib.request.urlopen(url, timeout=25) as response:
            rows = csv.DictReader(response.read().decode("utf-8").splitlines())
            for row in rows:
                close = parse_float(row.get("Close"))
                open_ = parse_float(row.get("Open"))
                if close is None:
                    continue
                change_pct = ((close - open_) / open_ * 100) if open_ else None
                symbol = (row.get("Symbol") or "").upper()
                quotes[symbol] = {
                    "symbol": symbol,
                    "price": close,
                    "change_pct": change_pct,
                    "date": row.get("Date"),
                    "time": row.get("Time"),
                    "volume": parse_float(row.get("Volume")),
                }
    return quotes


def parse_float(value: str | None) -> float | None:
    if value in (None, "", "N/D"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def watchlist_tickers() -> list[str]:
    html = INDEX_HTML.read_text()
    tickers = set(re.findall(r"ticker:\s*'([^']+)'", html))
    tickers.update(re.findall(r'"ticker":\s*"([^"]+)"', (ROOT / "research-library.json").read_text()))
    return sorted(tickers)


def load_fallback_indices() -> dict[str, dict]:
    if not INDICES_FALLBACK.exists():
        return {}
    data = json.loads(INDICES_FALLBACK.read_text())
    return {item["name"]: item for item in data.get("indices", [])}


def market_status(now: datetime) -> str:
    weekday_open = now.weekday() < 5
    hour = now.hour + now.minute / 60
    return "open" if weekday_open and 9.5 <= hour < 16 else "closed"


def main() -> None:
    ticker_map: dict[str, str] = {}
    symbols = []
    for ticker in watchlist_tickers():
        symbol = stooq_symbol(ticker)
        if not symbol:
            continue
        ticker_map[symbol] = ticker.upper()
        symbols.append(symbol)
    symbols.extend(symbol for _, symbol in INDEX_SYMBOLS.values())

    quotes_by_symbol = fetch_stooq(sorted(set(symbols)))
    fallback_indices = load_fallback_indices()

    quotes = []
    for symbol, ticker in sorted(ticker_map.items(), key=lambda item: item[1]):
        q = quotes_by_symbol.get(symbol)
        if not q:
            continue
        quotes.append({"ticker": ticker, **q})

    indices = []
    for name, (_, symbol) in INDEX_SYMBOLS.items():
        q = quotes_by_symbol.get(symbol)
        if not q:
            continue
        fallback = fallback_indices.get(name, {})
        vs_exit = None
        if name == "S&P 500":
            vs_exit = ((q["price"] - 6591.90) / 6591.90) * 100
        elif name == "Dow Jones":
            vs_exit = ((q["price"] - 46429.49) / 46429.49) * 100
        indices.append({
            "name": name,
            "ticker": fallback.get("ticker", symbol),
            "price": q["price"],
            "change_pct": q["change_pct"] or 0,
            "vs_exit": vs_exit,
            "source": "stooq",
        })

    for name in ("Russell 2000", "VIX"):
        if name in fallback_indices:
            indices.append({**fallback_indices[name], "source": "fallback-static"})

    now = datetime.now(timezone.utc)
    eastern_now = now.astimezone(ZoneInfo("America/New_York"))
    OUTPUT.write_text(json.dumps({
        "generated_at": now.isoformat(),
        "source": "stooq",
        "market_status": market_status(eastern_now),
        "indices": indices,
        "quotes": quotes,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()

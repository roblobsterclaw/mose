#!/usr/bin/env python3
"""Refresh MOSE live quote snapshot for GitHub Pages.

The public app is static, so it cannot keep a server-side market feed open.
This script writes live-quotes.json for the browser to poll. It uses Stooq's
CSV endpoint because it works without API keys and is suitable for a lightweight
watchlist snapshot.
"""

from __future__ import annotations

import csv
import os
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
SNAPSHOT_OUTPUT = ROOT / "symbol-snapshots.json"
HISTORY_OUTPUT = ROOT / "price-history.json"
INDICES_FALLBACK = ROOT / "indices-latest.json"
DCF_FILE = ROOT / "dcf-latest.json"
RESEARCH_FILE = ROOT / "research-library.json"
JOE_HOLDINGS_FILE = ROOT / "joes-holdings.json"


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


def fetch_stooq_history(symbols: dict[str, str], years: int = 5) -> dict[str, list[dict]]:
    """Fetch daily chart history when STOOQ_APIKEY is configured.

    Stooq's history endpoint requires a user API key. Without it we still write
    an empty, well-shaped file so the frontend and database migration can ship
    without pretending we have 52-week history.
    """
    api_key = os.environ.get("STOOQ_APIKEY", "").strip()
    if not api_key:
        return {}
    now = datetime.now(timezone.utc)
    start = now.replace(year=now.year - years)
    d1, d2 = start.strftime("%Y%m%d"), now.strftime("%Y%m%d")
    histories: dict[str, list[dict]] = {}
    for ticker, symbol in symbols.items():
        encoded = urllib.parse.quote(symbol, safe=".^-")
        url = f"https://stooq.com/q/d/l/?s={encoded}&d1={d1}&d2={d2}&i=d&apikey={api_key}"
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                rows = csv.DictReader(response.read().decode("utf-8").splitlines())
                points = []
                for row in rows:
                    close = parse_float(row.get("Close"))
                    if close is None:
                        continue
                    points.append({
                        "date": row.get("Date"),
                        "open": parse_float(row.get("Open")),
                        "high": parse_float(row.get("High")),
                        "low": parse_float(row.get("Low")),
                        "close": close,
                        "volume": parse_float(row.get("Volume")),
                    })
                if points:
                    histories[ticker] = points
        except Exception as exc:
            print(f"history fetch failed for {ticker}: {exc}")
    return histories


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


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def parse_static_watchlist() -> dict[str, dict]:
    html = INDEX_HTML.read_text()
    rows = {}
    pattern = re.compile(
        r"\{\s*ticker:\s*'([^']+)'\s*,\s*name:\s*'([^']*)'\s*,\s*bucket:\s*'([^']*)'\s*,\s*note:\s*'([^']*)'",
        re.S,
    )
    for ticker, name, bucket, note in pattern.findall(html):
        rows[ticker.upper()] = {"ticker": ticker.upper(), "name": name, "bucket": bucket, "note": note}
    return rows


def compute_history_metrics(points: list[dict]) -> dict:
    if not points:
        return {}
    last_year = points[-252:] if len(points) > 252 else points
    highs = [p.get("high") for p in last_year if p.get("high") is not None]
    lows = [p.get("low") for p in last_year if p.get("low") is not None]
    return {
        "week52High": max(highs) if highs else None,
        "week52Low": min(lows) if lows else None,
    }


def build_symbol_snapshots(quotes: list[dict], indices: list[dict], histories: dict[str, list[dict]]) -> dict:
    watchlist = parse_static_watchlist()
    dcf = {item.get("ticker", "").upper(): item for item in load_json(DCF_FILE, {}).get("valuations", [])}
    reports = {item.get("ticker", "").upper(): item for item in load_json(RESEARCH_FILE, {}).get("reports", [])}
    owned = {}
    for acct in load_json(JOE_HOLDINGS_FILE, {}).get("accounts", []):
        for h in acct.get("holdings", []):
            ticker = (h.get("ticker") or "").upper()
            if not ticker or ticker in {"CASH", "MANAGED"}:
                continue
            owned.setdefault(ticker, {"shares": 0, "value": 0})
            owned[ticker]["shares"] += h.get("shares") or 0
            owned[ticker]["value"] += h.get("value") or 0

    symbols = {}
    for q in quotes:
        ticker = q["ticker"].upper()
        row = watchlist.get(ticker, {})
        val = dcf.get(ticker, {})
        report = reports.get(ticker, {})
        metrics = compute_history_metrics(histories.get(ticker, []))
        if val.get("market_cap") is not None:
            metrics["marketCap"] = val.get("market_cap")
        if val.get("eps_ttm") and q.get("price"):
            metrics["peRatio"] = q["price"] / val["eps_ttm"]
        symbols[ticker] = {
            "ticker": ticker,
            "name": row.get("name") or val.get("company") or report.get("company") or ticker,
            "type": "ETF" if ticker in {"SGOV", "TFLO", "BIL", "VOO", "ROBO", "IRBO"} else "Equity",
            "bucket": row.get("bucket"),
            "note": row.get("note"),
            "quote": q,
            "metrics": metrics,
            "profile": {
                "company": val.get("company") or report.get("company"),
                "owned": owned.get(ticker),
                "hasResearch": bool(report.get("reportUrl")),
            },
            "source": "stooq",
        }

    for idx in indices:
        ticker = idx["ticker"].upper()
        metrics = compute_history_metrics(histories.get(ticker, []))
        symbols[ticker] = {
            "ticker": ticker,
            "name": idx["name"],
            "type": "Index",
            "quote": {
                "ticker": ticker,
                "price": idx.get("price"),
                "change_pct": idx.get("change_pct"),
                "source": idx.get("source"),
            },
            "metrics": metrics,
            "profile": {"vsExit": idx.get("vs_exit")},
            "source": idx.get("source") or "stooq",
        }
    return symbols


def market_status(now: datetime) -> str:
    weekday_open = now.weekday() < 5
    hour = now.hour + now.minute / 60
    return "open" if weekday_open and 9.5 <= hour < 16 else "closed"


def main() -> None:
    ticker_map: dict[str, str] = {}
    history_symbol_map: dict[str, str] = {}
    symbols = []
    for ticker in watchlist_tickers():
        symbol = stooq_symbol(ticker)
        if not symbol:
            continue
        ticker_map[symbol] = ticker.upper()
        history_symbol_map[ticker.upper()] = symbol
        symbols.append(symbol)
    for name, symbol in INDEX_SYMBOLS.values():
        symbols.append(symbol)
        history_symbol_map[name.upper()] = symbol

    quotes_by_symbol = fetch_stooq(sorted(set(symbols)))
    histories = fetch_stooq_history(history_symbol_map)
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
    HISTORY_OUTPUT.write_text(json.dumps({
        "generated_at": now.isoformat(),
        "source": "stooq-history" if os.environ.get("STOOQ_APIKEY") else "not-configured",
        "requires": "Set STOOQ_APIKEY in the scheduled job to populate 1Y/2Y/5Y daily histories.",
        "histories": histories,
    }, indent=2) + "\n")
    SNAPSHOT_OUTPUT.write_text(json.dumps({
        "generated_at": now.isoformat(),
        "source": "mose-live-quote-snapshot",
        "symbols": build_symbol_snapshots(quotes, indices, histories),
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()

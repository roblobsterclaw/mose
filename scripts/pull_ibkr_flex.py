#!/usr/bin/env python3
"""Pull open positions for EVERY IBKR account from the Flex Web Service.

Why this exists: the IBKR AI connector authorizes ONE account per connection,
so reading Joe's IRA, the Joint account and Keli's IRA through it would mean
disconnecting and reconnecting every time. The Flex Web Service has no such
limit — one token, taken from the master account of a linked structure,
returns data for every account included in the query. Two tokens (Joe's login,
Keli's login) therefore cover all three accounts with no swapping at all.

Read-only by design. It never places, stages or cancels anything.

Setup (once, in IBKR Client Portal):
  Performance & Reports -> Flex Queries -> Activity Flex Query
    - Sections: Open Positions (Symbol, Quantity, Mark Price, Position Value,
      Cost Basis Money, Asset Class) and Account Information
    - Accounts: select ALL accounts you want covered
    - Period: Last Business Day     Format: XML      Version: 3
  Then Settings -> Flex Web Service -> generate a token, note the Query ID.

Environment (never commit these):
  IBKR_FLEX_TOKEN       / IBKR_FLEX_QUERY_ID        Joe's login (IRA + Joint)
  IBKR_FLEX_TOKEN_2     / IBKR_FLEX_QUERY_ID_2      Keli's login  (optional)

The repo is PUBLIC, so this data must never be committed. The snapshot goes to
Firebase (where the app already syncs holdings) and the local file is gitignored.

Usage:
  python3 scripts/pull_ibkr_flex.py [--firebase] [--out data/ibkr-positions.json] [--print]

Output shape (data/ibkr-positions.json):
  {"generated_at": ..., "source": ..., "accounts": {
     "U1234567": {"alias": "...", "net_liq": null, "as_of": "20260908",
                  "positions": {"GOOGL": {"shares": 57.0, "market_value": 18895.5,
                                          "cost_basis": 11048.54}}}}}

Positions are as of the statement date (normally the prior business day close),
not intraday. That is the right granularity for MOSE, which plans buys rather
than trades them.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "ibkr-positions.json"
ACCOUNT_MAP = ROOT / "reference-data" / "ibkr-accounts.json"

FB = "https://jfl-ttd-default-rtdb.firebaseio.com/mose/ibkrPositions.json"
BASE = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"
SEND = BASE + "/SendRequest"
GET = BASE + "/GetStatement"
UA = {"User-Agent": "MOSE/1.0 (flex puller)"}

# Firebase keys cannot contain a dot, and the app stores class shares with a
# hyphen (canonicalTicker in index.html). Match sync_ibkr_owned.py exactly.
TICKER_FIX = {"BRK B": "BRK-B", "BRK A": "BRK-A", "BRK.B": "BRK-B", "BRK.A": "BRK-A"}

# Statement generation is asynchronous; IBKR warns 1019 until it is ready.
POLL_TRIES = 12
POLL_WAIT = 5


class FlexError(RuntimeError):
    pass


def _get(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    try:
        return ET.fromstring(body)
    except ET.ParseError as e:
        raise FlexError(f"unparseable response: {body[:200]!r}") from e


def _num(v: str | None) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _ticker(symbol: str | None) -> str:
    s = (symbol or "").strip().upper()
    return TICKER_FIX.get(s, s).replace(".", "-")


def request_statement(token: str, query_id: str) -> str:
    """Kick off a Flex run and return its reference code."""
    q = urllib.parse.urlencode({"t": token, "q": query_id, "v": "3"})
    root = _get(f"{SEND}?{q}")
    status = (root.findtext("Status") or "").strip()
    if status != "Success":
        code = root.findtext("ErrorCode") or "?"
        msg = root.findtext("ErrorMessage") or "unknown error"
        raise FlexError(f"SendRequest failed ({status} {code}): {msg}")
    ref = (root.findtext("ReferenceCode") or "").strip()
    if not ref:
        raise FlexError("SendRequest succeeded but returned no ReferenceCode")
    return ref


def fetch_statement(token: str, ref: str) -> ET.Element:
    """Poll until the statement is generated, then return the parsed XML."""
    q = urllib.parse.urlencode({"t": token, "q": ref, "v": "3"})
    url = f"{GET}?{q}"
    last = "no response"
    for attempt in range(POLL_TRIES):
        root = _get(url)
        # A ready statement is <FlexQueryResponse>; a not-ready one is a
        # <FlexStatementResponse> carrying Warn + error code 1019.
        if root.tag == "FlexQueryResponse":
            return root
        code = (root.findtext("ErrorCode") or "").strip()
        last = root.findtext("ErrorMessage") or root.tag
        if code != "1019":
            raise FlexError(f"GetStatement failed ({code}): {last}")
        if attempt < POLL_TRIES - 1:
            time.sleep(POLL_WAIT)
    raise FlexError(f"statement not ready after {POLL_TRIES * POLL_WAIT}s: {last}")


def parse_accounts(root: ET.Element) -> dict[str, dict]:
    """Fold every FlexStatement in the response into {account_id: {...}}."""
    out: dict[str, dict] = {}
    for stmt in root.iter("FlexStatement"):
        acct_id = stmt.get("accountId") or "?"
        acct = out.setdefault(
            acct_id,
            {"alias": None, "type": None, "net_liq": None,
             "as_of": stmt.get("toDate"), "positions": {}},
        )
        for info in stmt.iter("AccountInformation"):
            acct["alias"] = info.get("acctAlias") or acct["alias"]
            acct["type"] = info.get("accountType") or acct["type"]
        for p in stmt.iter("OpenPosition"):
            if (p.get("assetCategory") or "STK") != "STK":
                continue
            # A multi-account query repeats the accountId on every row; trust
            # the row over the statement header so nothing is misfiled.
            row_acct = p.get("accountId") or acct_id
            target = out.setdefault(
                row_acct,
                {"alias": None, "type": None, "net_liq": None,
                 "as_of": stmt.get("toDate"), "positions": {}},
            )
            ticker = _ticker(p.get("symbol"))
            if not ticker:
                continue
            shares = _num(p.get("position")) or 0.0
            if shares == 0:
                continue
            value = _num(p.get("positionValue"))
            if value is None:
                mark = _num(p.get("markPrice")) or 0.0
                value = shares * mark
            # Lots are reported separately when the query is lot-level; sum them.
            prev = target["positions"].get(ticker)
            if prev:
                prev["shares"] = round(prev["shares"] + shares, 6)
                prev["market_value"] = round(prev["market_value"] + value, 2)
                if prev["cost_basis"] is not None:
                    cb = _num(p.get("costBasisMoney"))
                    prev["cost_basis"] = round(prev["cost_basis"] + (cb or 0), 2)
            else:
                target["positions"][ticker] = {
                    "shares": round(shares, 6),
                    "market_value": round(value, 2),
                    "cost_basis": _num(p.get("costBasisMoney")),
                }
    return out


def load_account_map() -> dict[str, dict]:
    try:
        return json.loads(ACCOUNT_MAP.read_text()).get("accounts", {})
    except (OSError, ValueError) as e:
        print(f"  account map unreadable ({e}); accounts stay unmapped", file=sys.stderr)
        return {}


def apply_account_map(accounts: dict[str, dict]) -> list[str]:
    """Stamp each account with its MOSE column. Returns the ids we cannot place.

    An unknown account is reported, never guessed at — filing a quarter of a
    million dollars into the wrong column silently is the failure mode worth
    engineering against.
    """
    known = load_account_map()
    unmapped = []
    for acct_id, acct in accounts.items():
        m = known.get(acct_id) or {}
        acct["mose_key"] = m.get("key")
        acct["label"] = m.get("label") or acct.get("alias") or acct_id
        acct["taxable"] = m.get("taxable")
        if not m.get("key"):
            unmapped.append(acct_id)
    return unmapped


def pull(token: str, query_id: str, label: str) -> dict[str, dict]:
    ref = request_statement(token, query_id)
    accounts = parse_accounts(fetch_statement(token, ref))
    print(f"  {label}: {len(accounts)} account(s), "
          f"{sum(len(a['positions']) for a in accounts.values())} positions")
    return accounts


def push_firebase(payload: dict) -> None:
    """Publish the snapshot where the app already reads its state from.

    Account numbers and balances must not land in git — the repo is public.
    """
    body = json.dumps(payload).encode()
    req = urllib.request.Request(FB, data=body, method="PUT",
                                 headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 204):
            raise FlexError(f"Firebase PUT returned HTTP {r.status}")
    print(f"  pushed to Firebase ({len(body)} bytes)")


def main(argv: list[str]) -> int:
    out_path = Path(argv[argv.index("--out") + 1]) if "--out" in argv else DEFAULT_OUT
    creds = [
        (os.environ.get("IBKR_FLEX_TOKEN"), os.environ.get("IBKR_FLEX_QUERY_ID"), "login 1"),
        (os.environ.get("IBKR_FLEX_TOKEN_2"), os.environ.get("IBKR_FLEX_QUERY_ID_2"), "login 2"),
    ]
    creds = [c for c in creds if c[0] and c[1]]
    if not creds:
        print("No Flex credentials in the environment. Set IBKR_FLEX_TOKEN and "
              "IBKR_FLEX_QUERY_ID (and optionally the _2 pair).", file=sys.stderr)
        return 2

    accounts: dict[str, dict] = {}
    failures = []
    for token, query_id, label in creds:
        try:
            accounts.update(pull(token, query_id, label))
        except (FlexError, OSError) as e:
            # One login failing must not throw away the other login's data.
            failures.append(f"{label}: {e}")
            print(f"  {label}: FAILED — {e}", file=sys.stderr)

    if not accounts:
        print("No positions retrieved; leaving the existing file untouched.", file=sys.stderr)
        return 1

    unmapped = apply_account_map(accounts)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "IBKR Flex Web Service v3 (open positions)",
        "accounts": accounts,
    }
    if failures:
        payload["partial"] = failures
    if unmapped:
        payload["unmapped"] = unmapped
        print("  UNMAPPED account(s) — add them to reference-data/ibkr-accounts.json "
              "before trusting any per-account total: " + ", ".join(unmapped),
              file=sys.stderr)
    for acct_id, a in sorted(accounts.items()):
        print(f"  {acct_id}  {a['label']:<18} key={a['mose_key'] or '?':<6} "
              f"{len(a['positions'])} positions  alias={a.get('alias')!r} "
              f"type={a.get('type')!r}")
    if "--print" in argv:
        print(json.dumps(payload, indent=1))
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"wrote {out_path.relative_to(ROOT)} (gitignored) — {len(accounts)} account(s)")
    if "--firebase" in argv:
        push_firebase(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

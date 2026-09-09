#!/usr/bin/env python3
"""Sync live IBKR positions into targetsData.owned['his|*'] in Firebase.

Joe's IBKR login covers his IRA + Joint Cash; the app records that whole book
under the `his` account key (Keli's IRA is a separate login and lives under
`hers` — never touched here).

DEFAULT IS ADDITIVE AND NEVER DELETES. The connector is bound to a single
account view (net liquidation ~$948k = the IRA), while the app's `his` bucket
was pasted from a wider view, so a ticker missing from the API is not proof it
was sold — it may simply live in an account the connector cannot see. Blindly
mirroring would erase real positions.

  --apply        add missing tickers, normalise ticker spellings, leave the rest
  --update-all   also overwrite values that drifted (only when the API view is
                 known to cover every account)
  --prune        additionally zero `his` tickers the API does not report
                 (destructive — only with --update-all and a verified full view)

  python3 scripts/sync_ibkr_owned.py positions.json [--apply] [--update-all] [--prune]
"""
from __future__ import annotations
import json, sys, urllib.request
from datetime import date

FB = "https://jfl-ttd-default-rtdb.firebaseio.com/mose/targets.json"
# IBKR contract_description -> the ticker MOSE uses
# Firebase keys cannot contain a dot, so the app stores class shares with a
# hyphen (canonicalTicker in index.html: BRK.B -> BRK-B). Match that spelling or
# the PUT is rejected with HTTP 400.
TICKER_FIX = {"BRK B": "BRK-B", "BRK A": "BRK-A", "BRK.B": "BRK-B", "BRK.A": "BRK-A"}
APP_ALIAS: dict[str, str] = {}


def fb_safe(t: str) -> str:
    """Firebase rejects . $ # [ ] / in keys."""
    return t.replace(".", "-")


def app_ticker(desc: str) -> str:
    d = (desc or "").strip().upper()
    return fb_safe(TICKER_FIX.get(d, d))


def main(path: str, apply: bool, update_all: bool = False, prune: bool = False) -> None:
    pos = json.load(open(path))
    pos = pos.get("positions", pos) if isinstance(pos, dict) else pos
    live = {}
    for p in pos:
        if (p.get("asset_class") or "STK") != "STK":
            continue
        v = float(p.get("market_value") or 0)
        if v > 0:
            live[app_ticker(p.get("contract_description"))] = round(v, 2)

    t = json.load(urllib.request.urlopen(FB, timeout=30))
    owned = t.setdefault("owned", {})
    cur, alias_keys = {}, {}
    for k, v in owned.items():
        if not k.startswith("his|") or float(v or 0) <= 0:
            continue
        tk = k.split("|", 1)[1]
        canon = APP_ALIAS.get(tk, tk)
        if canon != tk:
            alias_keys[canon] = k          # e.g. BRK.B -> "his|BRK-B", rename on write
        cur[canon] = float(v)

    added   = {k: v for k, v in live.items() if k not in cur}
    changed = {k: (cur[k], v) for k, v in live.items() if k in cur and abs(cur[k] - v) > 1}
    gone    = {k: v for k, v in cur.items() if k not in live}

    print(f"IBKR reports {len(live)} positions, ${sum(live.values()):,.0f}")
    print(f"app 'his' has {len(cur)} positions, ${sum(cur.values()):,.0f}\n")
    if added:
        print(f"NEW in IBKR, missing from the app ({len(added)}):")
        for k, v in sorted(added.items(), key=lambda kv: -kv[1]):
            print(f"   + {k:8} ${v:>12,.2f}")
    if gone:
        print(f"\nIn the app but NOT at IBKR — will be zeroed as sold ({len(gone)}):")
        for k, v in sorted(gone.items(), key=lambda kv: -kv[1]):
            print(f"   - {k:8} ${v:>10,.2f}")
    if changed:
        print(f"\nValue drift ({len(changed)}):")
        for k, (o, n) in sorted(changed.items(), key=lambda kv: -abs(kv[1][1] - kv[1][0]))[:15]:
            print(f"   ~ {k:8} ${o:>10,.0f} -> ${n:>10,.2f}  ({n - o:+,.0f})")

    if not apply:
        print("\n(dry run — pass --apply to write)")
        return

    wrote = []
    for k, old_key in alias_keys.items():          # BRK-B -> BRK.B
        owned.pop(old_key, None)
        owned["his|" + k] = live.get(k, cur[k])
        wrote.append(f"renamed {old_key.split('|')[1]} -> {k}")
    for k, v in added.items():
        owned["his|" + k] = v
        wrote.append(f"added {k}")
    if update_all:
        for k, (_o, n) in changed.items():
            owned["his|" + k] = n
        wrote.append(f"updated {len(changed)} drifted values")
    if prune and update_all:
        for k in gone:
            owned.pop("his|" + k, None)
        wrote.append(f"zeroed {len(gone)}")
    if not update_all:
        print("\nADDITIVE MODE: existing values and absent tickers left untouched.")
    hist = t.setdefault("history", [])
    today = date.today().isoformat()
    hist = [h for h in hist if h.get("date") != today]
    total = sum(float(v or 0) for k, v in owned.items() if k.startswith("his|"))
    hist.append({"date": today, "source": "IBKR live sync (additive)" if not update_all else "IBKR live sync",
                 "deployed": round(total, 2), "positions": sum(1 for k in owned if k.startswith("his|"))})
    t["history"] = hist
    req = urllib.request.Request(FB, data=json.dumps(t).encode(), method="PUT",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()
    print("\napplied: " + "; ".join(wrote) + f"; snapshot dated {today}")


if __name__ == "__main__":
    main(sys.argv[1], "--apply" in sys.argv, "--update-all" in sys.argv, "--prune" in sys.argv)

#!/usr/bin/env python3
"""
td_to_iif.py — Convert a TD Bank (Business Convenience Plus) PDF statement into
an IIF file that QuickBooks Desktop Pro 2024 can import.

Usage:
    python3 td_to_iif.py STATEMENT.pdf                 # writes STATEMENT.iif next to the PDF
    python3 td_to_iif.py STATEMENT.pdf -o out.iif      # choose the output path
    python3 td_to_iif.py STATEMENT.pdf --preview       # print the parsed/categorized table, no file

What it does
------------
1. Reads every transaction out of the 5 activity sections of the statement
   (Deposits, Electronic Deposits, Checks Paid, Electronic Payments, Other
   Withdrawals).
2. Categorizes each one against the Surfbox / Valet Box chart of accounts using
   the ACCOUNTS + RULES tables below (edit those to change the mapping).
3. RECONCILES the parsed data against the totals printed on the statement. If a
   single penny is off, it REFUSES to write the file and tells you what broke.
   This is the safety net that makes the output trustworthy.
4. Emits a tab-delimited, Windows-1252 (ANSI), CRLF IIF file — exactly the
   dialect QuickBooks Desktop expects — using TRNS / SPL / ENDTRNS blocks.

Only dependency: PyMuPDF  (pip install pymupdf)
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required. Install it with:  pip install pymupdf")


# ---------------------------------------------------------------------------
# CONFIG 1 — ACCOUNTS
#
# These strings must match your QuickBooks chart of accounts EXACTLY, including
# the number, the space-middot-space, and the name. Because your company file
# has account numbers turned on, QuickBooks matches on the full "1234 · Name"
# string. If an import creates a duplicate account, the string below did not
# match your chart — fix it here.
#
# MIDDOT is the "·" character (Unicode U+00B7). Keep it; the file is written as
# Windows-1252 so QuickBooks reads it as a single byte.
# ---------------------------------------------------------------------------
DOT = "·"  # the "·" QuickBooks shows between an account number and its name

# How to write account references in the IIF file:
#   "number"      -> "1000"          (the account NUMBER alone)
#   "name"        -> "Cash"          (the account's real NAME)
#   "number_name" -> "1000 · Cash"   (the number+name display string)
# This company file has account numbers enabled, and QuickBooks Desktop 2024
# resolves the ACCNT field by number. "number" is the proven, reliable choice
# (it matches the format of the statements that already import for this file).
# Do NOT use "number_name": the "·" is only a display separator, and no account
# is literally named "1000 · Cash", so every row fails to resolve.
ACCOUNT_REF_STYLE = "number"

# QuickBooks Desktop 2024's IIF importer rejects an !ACCNT header that contains
# an ACCNTNUM column ("ACCNTNUM is not a valid column name for record ACCNT"),
# and that one error aborts the WHOLE import. The accounts already exist in the
# chart, so we don't declare them at all — we just reference them by number.
EMIT_ACCNT_BLOCK = False

# Account registry:  KEY -> (number, exact name, IIF account type)
# The NAME must match your chart of accounts exactly. IIF type codes:
#   BANK=Bank  INC=Income  EXP=Expense  FIXASSET=Fixed Asset
#   OCLIAB=Other Current Liability
ACCOUNTS = {
    "BANK":         ("1000", "Cash",                        "BANK"),
    "RENTAL":       ("4000", "8' SB rental",                "INC"),
    "INSURANCE":    ("6007", "Insurance",                   "EXP"),
    "BANK_CHARGES": ("6021", "Bank charges",                "EXP"),
    "PAYROLL_FEE":  ("6023", "Payroll fee",                 "EXP"),
    "ADVERTISING":  ("6003", "Advertising 1",               "EXP"),  # Amex
    "OFFICE":       ("6018", "Office",                      "EXP"),  # Chase
    "MGMT_FEES":    ("6016", "Management fees",             "EXP"),  # Truist
    "TRUCKS_EQUIP": ("1510", "Trucks & Equip",             "FIXASSET"),  # chk 1328
    "TOYOTA_NOTE":  ("2100", "Note payable - Toyota Credit", "OCLIAB"),
    "SUSPENSE":     ("2300", "Other current liabilities",   "OCLIAB"),
}


def acct(key):
    """Render the account reference in the configured style."""
    num, name, _ = ACCOUNTS[key]
    if ACCOUNT_REF_STYLE == "number":
        return num
    if ACCOUNT_REF_STYLE == "number_name":
        return f"{num} {DOT} {name}"
    return name


BANK_ACCOUNT  = acct("BANK")  # the TD checking account inside QuickBooks
RENTAL_INCOME = acct("RENTAL")
INSURANCE     = acct("INSURANCE")
BANK_CHARGES  = acct("BANK_CHARGES")
PAYROLL_FEE   = acct("PAYROLL_FEE")
ADVERTISING   = acct("ADVERTISING")    # Amex payments
OFFICE        = acct("OFFICE")         # Chase credit-card payments
MGMT_FEES     = acct("MGMT_FEES")      # recurring Truist WEBXFR transfers
TRUCKS_EQUIP  = acct("TRUCKS_EQUIP")   # check #1328 (equipment purchase)
TOYOTA_NOTE   = acct("TOYOTA_NOTE")
# Suspense / "ask my accountant" bucket for anything we can't confidently book.
SUSPENSE      = acct("SUSPENSE")


# ---------------------------------------------------------------------------
# CONFIG 2 — RULES
#
# Each rule is (regex, account, review).  The first regex (matched against the
# UPPER-CASED description) wins.  `review=True` marks the line with a REVIEW
# tag in the memo and in the summary report so it is easy to find and reclassify
# inside QuickBooks. Order matters — put specific patterns before generic ones.
# ---------------------------------------------------------------------------
RULES = [
    # --- money in -----------------------------------------------------------
    (r"GLOBAL PAYMENTS.*GLOBAL DEP", RENTAL_INCOME, False),  # card settlements
    (r"\bDEPOSIT\b",                 RENTAL_INCOME, False),  # counter deposits
    # --- money out ----------------------------------------------------------
    (r"GLOBAL PAYMENTS.*GLOBAL STL", BANK_CHARGES,  False),  # merchant fees
    (r"UTICA MUTUAL",                INSURANCE,     False),
    (r"ADP PAYROLL FEES",            PAYROLL_FEE,   False),
    (r"TOYOTA",                      TOYOTA_NOTE,   False),
    (r"ACH BATCH CHARGE",            BANK_CHARGES,  False),
    (r"CHASE CREDIT",                OFFICE,        False),   # Chase card payment
    (r"\bAMEX\b",                    ADVERTISING,   False),   # Amex card payment
    (r"TRUIST",                      MGMT_FEES,     False),   # recurring transfer
    # --- per-statement check overrides -------------------------------------
    # Checks can't be auto-categorized from the statement alone, so unmatched
    # checks fall through to REVIEW below. Add a line here to pin a known check
    # to its account, e.g. check #1328 was a Trucks & Equipment purchase.
    (r"CHECK #1328\b",               TRUCKS_EQUIP,  False),
]
# Anything that matches no rule falls through to this (e.g. an un-pinned check).
FALLBACK = (SUSPENSE, True)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
MONEY_RE = re.compile(r"^\d{1,3}(?:,\d{3})*\.\d{2}$")
DATE_RE = re.compile(r"^\d{2}/\d{2}$")
INT_RE = re.compile(r"^\d+$")

# Section header -> internal key. "Deposits" is a substring of "Electronic
# Deposits", so we compare on exact stripped lines and also gate on a lookahead
# (see below) to avoid the identically-named labels in the ACCOUNT SUMMARY box.
SECTION_HEADERS = {
    "Deposits": "deposits",
    "Electronic Deposits": "electronic_deposits",
    "Checks Paid": "checks",
    "Electronic Payments": "electronic_payments",
    "Other Withdrawals": "other_withdrawals",
}
INFLOW_SECTIONS = {"deposits", "electronic_deposits"}
COLUMN_HEADER_MARKERS = {"POSTING DATE", "SERIAL NO."}
SKIP_LINES = {
    "POSTING DATE", "DESCRIPTION", "AMOUNT", "DATE", "SERIAL NO.",
    "DAILY ACCOUNT ACTIVITY",
}


def money(s):
    return float(s.replace(",", ""))


def parse_statement(pdf_path):
    """Return (meta, transactions, printed_subtotals)."""
    doc = fitz.open(pdf_path)
    lines = []
    for page in doc:
        for raw in page.get_text().splitlines():
            t = raw.strip()
            if t:
                lines.append(t)

    meta = _parse_meta(lines)

    txns = []
    printed_subtotals = {}
    section = None
    rec = None  # {date, desc_parts, serial, amount}

    def close_record():
        nonlocal rec
        if rec and rec.get("amount") is not None:
            txns.append(_finalize_record(rec, section, meta))
        rec = None

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Detect a real section header: exact name AND a column-header marker
        # within the next few lines (this rejects the ACCOUNT SUMMARY labels,
        # which are followed by a dollar amount instead).
        header_key = _match_section_header(line, lines, i)
        if header_key:
            close_record()
            section = header_key
            i += 1
            continue

        if section is None:
            i += 1
            continue

        if line.startswith("Subtotal:"):
            close_record()
            # the amount is the next money line
            if i + 1 < n and MONEY_RE.match(lines[i + 1]):
                printed_subtotals[section] = money(lines[i + 1])
                i += 1
            section = None
            i += 1
            continue

        if line in SKIP_LINES or line.startswith("No. Checks") or line.startswith("*Indicates"):
            i += 1
            continue

        if DATE_RE.match(line):
            close_record()
            rec = {"date": line, "desc_parts": [], "serial": None, "amount": None}
            i += 1
            continue

        if rec is not None:
            if MONEY_RE.match(line):
                # Each TD transaction is date -> description -> amount, printed
                # contiguously. The amount COMPLETES the record, so close it out
                # immediately. This prevents stray numbers on intervening pages
                # (e.g. the "How to Balance" legal page that sits between the two
                # halves of a continued section) from corrupting an open record.
                rec["amount"] = money(line)
                close_record()
            elif INT_RE.match(line):
                # serial number (check number, deposit ticket #, etc.)
                rec["serial"] = line
                rec["desc_parts"].append(line)
            else:
                rec["desc_parts"].append(line)
        i += 1

    close_record()
    doc.close()
    return meta, txns, printed_subtotals


def _match_section_header(line, lines, idx):
    if line not in SECTION_HEADERS and not line.startswith("Electronic Deposits"):
        return None
    key = SECTION_HEADERS.get(line)
    if key is None and line.startswith("Electronic Deposits"):
        key = "electronic_deposits"  # "(continued)"
    if key is None:
        return None
    # look ahead a few non-empty lines for a column-header marker
    for j in range(idx + 1, min(idx + 5, len(lines))):
        if lines[j] in COLUMN_HEADER_MARKERS:
            return key
    return None


def _finalize_record(rec, section, meta):
    desc = " ".join(rec["desc_parts"]).strip()
    desc = re.sub(r"\s+", " ", desc)
    if section == "checks":
        serial = rec.get("serial") or ""
        desc = f"Check #{serial}".strip()
    date = _full_date(rec["date"], meta)
    inflow = section in INFLOW_SECTIONS
    return {
        "section": section,
        "date": date,
        "desc": desc,
        "serial": rec.get("serial"),
        "amount": rec["amount"],
        "inflow": inflow,
    }


def _full_date(mmdd, meta):
    mm, dd = mmdd.split("/")
    year = meta["start_year"] if int(mm) >= meta["start_month"] else meta["end_year"]
    return f"{mm}/{dd}/{year}"


def _parse_meta(lines):
    text = "\n".join(lines)
    period = re.search(
        r"([A-Z][a-z]{2})\s+(\d{2})\s+(\d{4})\s*-\s*([A-Z][a-z]{2})\s+(\d{2})\s+(\d{4})",
        text,
    )
    months = {m: i for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
    meta = {"start_month": 1, "start_year": 2000, "end_year": 2000,
            "period": "unknown", "period_slug": "unknown-period"}
    if period:
        meta["start_month"] = months.get(period.group(1), 1)
        meta["start_year"] = int(period.group(3))
        meta["end_year"] = int(period.group(6))
        meta["period"] = f"{period.group(1)} {period.group(3)}"
        # deterministic slug like "2026-06" so each statement month maps to ONE
        # output filename — re-running the same month overwrites instead of
        # silently producing a second file that could be imported twice.
        meta["period_slug"] = f"{meta['start_year']:04d}-{meta['start_month']:02d}"

    def grab(label):
        m = re.search(re.escape(label) + r"\s*\n?\s*([\d,]+\.\d{2})", text)
        return money(m.group(1)) if m else None

    meta["beginning"] = grab("Beginning Balance")
    meta["ending"] = grab("Ending Balance")
    return meta


# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------
def categorize(desc):
    up = desc.upper()
    for pattern, account, review in RULES:
        if re.search(pattern, up):
            return account, review
    return FALLBACK


# ---------------------------------------------------------------------------
# Reconciliation — refuse to emit anything that does not tie out
# ---------------------------------------------------------------------------
def reconcile(meta, txns, printed_subtotals):
    problems = []
    sums = {}
    for t in txns:
        sums[t["section"]] = round(sums.get(t["section"], 0.0) + t["amount"], 2)

    for section, printed in printed_subtotals.items():
        got = round(sums.get(section, 0.0), 2)
        if abs(got - printed) > 0.005:
            problems.append(
                f"Section '{section}': parsed {got:,.2f} but statement says {printed:,.2f}"
            )

    if meta.get("beginning") is not None and meta.get("ending") is not None:
        inflow = round(sum(t["amount"] for t in txns if t["inflow"]), 2)
        outflow = round(sum(t["amount"] for t in txns if not t["inflow"]), 2)
        computed = round(meta["beginning"] + inflow - outflow, 2)
        if abs(computed - meta["ending"]) > 0.005:
            problems.append(
                f"Balance check: beginning {meta['beginning']:,.2f} + in {inflow:,.2f} "
                f"- out {outflow:,.2f} = {computed:,.2f}, but statement ending is "
                f"{meta['ending']:,.2f}"
            )
    return problems


# ---------------------------------------------------------------------------
# IIF generation
# ---------------------------------------------------------------------------
def trns_type(t):
    if t["inflow"]:
        return "DEPOSIT"
    return "CHECK"  # checks and ACH debits both post as a decrease in the register


def _used_account_keys(txns):
    keys = {"BANK"}
    name_to_key = {v[1]: k for k, v in ACCOUNTS.items()}
    for t in txns:
        account, _ = categorize(t["desc"])
        # `account` is a rendered ref; map it back to its registry key
        for k, (num, name, _typ) in ACCOUNTS.items():
            if account in (name, f"{num} {DOT} {name}"):
                keys.add(k)
                break
    return keys


def build_iif(txns):
    rows = []

    if EMIT_ACCNT_BLOCK:
        rows.append(["!ACCNT", "NAME", "ACCNTTYPE", "ACCNTNUM"])
        for key in ACCOUNTS:  # preserves declared order
            if key in _used_account_keys(txns):
                num, name, typ = ACCOUNTS[key]
                rows.append(["ACCNT", acct(key), typ, num])

    rows.append(["!TRNS", "TRNSTYPE", "DATE", "ACCNT", "NAME", "AMOUNT", "DOCNUM", "MEMO", "CLEAR"])
    rows.append(["!SPL", "TRNSTYPE", "DATE", "ACCNT", "NAME", "AMOUNT", "DOCNUM", "MEMO", "CLEAR"])
    rows.append(["!ENDTRNS"])

    for t in txns:
        account, review = categorize(t["desc"])
        ttype = trns_type(t)
        docnum = t["serial"] if t["section"] == "checks" and t["serial"] else ""
        memo = t["desc"]
        if review:
            memo = f"REVIEW: {memo}"
        amt = t["amount"]
        bank_amt = amt if t["inflow"] else -amt          # bank side
        offset_amt = -bank_amt                            # category side nets to zero

        rows.append(["TRNS", ttype, t["date"], BANK_ACCOUNT, "",
                     f"{bank_amt:.2f}", docnum, memo, "N"])
        rows.append(["SPL", ttype, t["date"], account, "",
                     f"{offset_amt:.2f}", "", memo, "N"])
        rows.append(["ENDTRNS"])

    return "\r\n".join("\t".join(r) for r in rows) + "\r\n"


def write_iif(text, out_path):
    data = text.encode("cp1252", errors="replace")
    Path(out_path).write_bytes(data)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def build_summary(meta, txns):
    lines = []
    lines.append(f"TD statement -> IIF conversion summary ({meta.get('period','?')})")
    lines.append("=" * 64)
    by_acct = {}
    review_rows = []
    for t in txns:
        account, review = categorize(t["desc"])
        signed = t["amount"] if t["inflow"] else -t["amount"]
        by_acct.setdefault(account, [0, 0.0])
        by_acct[account][0] += 1
        by_acct[account][1] = round(by_acct[account][1] + signed, 2)
        if review:
            review_rows.append((t["date"], account, signed, t["desc"]))

    lines.append(f"{len(txns)} transactions parsed")
    if meta.get("beginning") is not None:
        lines.append(f"Beginning balance: {meta['beginning']:,.2f}")
    if meta.get("ending") is not None:
        lines.append(f"Ending balance:    {meta['ending']:,.2f}")
    lines.append("")
    lines.append("Posted to accounts (net):")
    for acct in sorted(by_acct):
        cnt, tot = by_acct[acct]
        lines.append(f"  {acct:<34} {cnt:>3} txn  net {tot:>13,.2f}")
    lines.append("")
    if review_rows:
        lines.append(f"REVIEW these {len(review_rows)} line(s) inside QuickBooks "
                     f"(posted to a suspense/uncertain account):")
        for d, acct, amt, desc in review_rows:
            lines.append(f"  {d}  {amt:>12,.2f}  -> {acct}")
            lines.append(f"                        {desc}")
    else:
        lines.append("No lines flagged for review.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def convert(pdf_path, out_path=None, preview=False):
    meta, txns, printed = parse_statement(pdf_path)
    if not txns:
        sys.exit("No transactions found — is this a TD Business Convenience Plus PDF?")

    problems = reconcile(meta, txns, printed)
    summary = build_summary(meta, txns)
    print(summary)

    if problems:
        print("RECONCILIATION FAILED — file NOT written:", file=sys.stderr)
        for p in problems:
            print("  * " + p, file=sys.stderr)
        sys.exit(2)
    print("Reconciliation OK — every section and the ending balance tie out.\n")

    print("+" + "-" * 62 + "+")
    print(f"| IMPORT THIS FILE ONCE.  It covers {meta.get('period','?'):<26} |")
    print("| IIF import does NOT check for existing transactions, so       |")
    print("| importing a month already in QuickBooks DUPLICATES every row. |")
    print("+" + "-" * 62 + "+\n")

    if preview:
        return

    if out_path is None:
        # name by statement period so each month is one deterministic file
        out_path = str(Path(pdf_path).with_name(f"valet-box-{meta['period_slug']}.iif"))
    write_iif(build_iif(txns), out_path)
    Path(out_path).with_suffix(".summary.txt").write_text(summary)
    print(f"Wrote {out_path}")
    print(f"Wrote {Path(out_path).with_suffix('.summary.txt')}")


def main():
    ap = argparse.ArgumentParser(description="Convert a TD Bank PDF statement to a QuickBooks IIF file.")
    ap.add_argument("pdf", help="path to the TD Bank PDF statement")
    ap.add_argument("-o", "--output", help="output .iif path (default: alongside the PDF)")
    ap.add_argument("--preview", action="store_true", help="parse and print the summary, but do not write a file")
    args = ap.parse_args()
    convert(args.pdf, args.output, args.preview)


if __name__ == "__main__":
    main()

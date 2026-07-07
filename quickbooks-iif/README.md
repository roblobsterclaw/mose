# TD Bank statement → QuickBooks IIF converter

Turns a **TD Business Convenience Plus** PDF statement (the Valet Box / Surfbox
TD Valet account) into an **`.IIF` file** that **QuickBooks Desktop Pro 2024**
imports directly — so nobody has to key transactions in by hand every month.

There are two ways to use it:

1. **The drop-a-PDF app** (for staff) — leave a watcher running; drop a PDF in a
   folder; an `.iif` pops out. No command line.
2. **The command line** (for one-offs / testing).

Either way, the tool **refuses to produce a file unless every section subtotal
and the ending balance on the statement reconcile to the penny.** That guard is
the whole point — you can trust that what you import matches the statement.

---

## What you get for each statement

Dropping `june-2026.pdf` in produces:

| File | What it is |
|------|-----------|
| `june-2026.iif` | Import this into QuickBooks. |
| `june-2026.summary.txt` | Plain-English recap: how much posted to each account, and the exact list of lines flagged **REVIEW**. |

The June 2026 run is already committed as a working sample:
`output/valet-box-2026-06.iif` (+ `.summary.txt`).

---

## One-time setup

You need Python 3 and one library.

- **Windows** (QuickBooks Desktop): install Python from python.org (check *“Add
  Python to PATH”*), then in a terminal in this folder:
  ```
  pip install -r requirements.txt
  ```
- **macOS**:
  ```
  pip3 install -r requirements.txt
  ```

---

## Using it — the drop-a-PDF app

1. Start the watcher:
   - **Windows:** double-click **`Convert-TD-Statement.bat`**
   - **macOS:** double-click **`convert-td-statement.command`**
     (first time: right-click → Open to clear the security prompt)
   - or run `python watch_inbox.py`
2. Drop any TD statement PDF into the **`inbox/`** folder.
3. Within a few seconds:
   - the `.iif` and `.summary.txt` appear in **`output/`**
   - the original PDF is moved to **`processed/`**
   - if it did **not** reconcile, the PDF goes to **`failed/`** and the reason
     is printed — nothing questionable ever reaches QuickBooks.
4. Import the `.iif` (next section).

Leave the watcher running all month; staff just drop PDFs in.

## Using it — command line

```
python td_to_iif.py statement.pdf                 # writes statement.iif beside it
python td_to_iif.py statement.pdf -o june.iif     # choose output name
python td_to_iif.py statement.pdf --preview       # show the summary, write nothing
```

---

## Importing into QuickBooks Desktop Pro 2024

1. **Back up your company file first** (File → Back Up Company). IIF imports
   cannot be undone except by restoring a backup.
2. File → **Utilities → Import → IIF Files**.
3. QuickBooks 2024 shows the newer importer. Choose the `.iif`, and when it
   offers to show results, let it. Accepted transactions land in the register of
   **`1000 · Cash`**.
4. Open the `1000 · Cash` register and spot-check a few against the statement.
5. Then handle the **REVIEW** lines (see below).

> Tip: if the importer complains, use the classic path instead — hold **Ctrl**
> while opening the Import menu, or use *“Import it for me / I’ll fix it later.”*
> The file itself is standard tab-delimited IIF and imports cleanly either way.

---

## How transactions are categorized

The offsetting account for each transaction is chosen by the rules in
`td_to_iif.py` (the `RULES` table). Current mapping:

| On the statement | Posts to |
|---|---|
| Counter deposits (`DEPOSIT`, `DEPOSIT SER #`) | `4000 · 8' SB rental` (income) |
| `GLOBAL PAYMENTS … GLOBAL DEP` (card settlements) | `4000 · 8' SB rental` (income) |
| `GLOBAL PAYMENTS … GLOBAL STL` (processor debit) | `6021 · Bank charges` |
| `UTICA MUTUAL INS` | `6007 · Insurance` |
| `ADP PAYROLL FEES` | `6023 · Payroll fee` |
| `ACH BATCH CHARGE` (SBIB) | `6021 · Bank charges` |
| `TOYOTA COMMERCIA` | `2100 · Note payable - Toyota Credit` |
| `CHASE CREDIT CRD EPAY` | `6018 · Office` |
| `AMEX EPAYMENT` | `6003 · Advertising 1` |
| `TRUIST … WEBXFR TRANSFER` | `6016 · Management fees` |
| Check #1328 (equipment) | `1510 · Trucks & Equip` |
| Any other check | `2300 · Other current liabilities` — **REVIEW** |
| Anything unrecognized | `2300 · Other current liabilities` — **REVIEW** |

`2300 · Other current liabilities` is the **suspense / “ask my accountant”
bucket** for anything the tool can’t confidently book (mainly checks, which vary
month to month). Anything landing there is tagged `REVIEW:` in its memo and
listed in the summary, so after import you open the `2300` register, find the
`REVIEW:` lines, and reclassify each. Amounts, dates, and full bank descriptions
are already there — no re-keying, just re-pointing the account. For June, every
line was categorized and nothing was flagged.

### Checks need a one-line pin each month

Checks can’t be categorized from the statement alone (the bank only prints the
check number). Unpinned checks go to `2300` **REVIEW** so you classify them in
QuickBooks. If a check recurs or you want it pre-categorized, add a line to the
`RULES` table, e.g. check #1328 was pinned to `1510 · Trucks & Equip`:

```python
(r"CHECK #1328\b", TRUCKS_EQUIP, False),
```

### Changing the mapping

Open `td_to_iif.py` and edit two short tables near the top:

- **`ACCOUNTS`** section — the exact account-name strings. They must match your
  chart of accounts *exactly*, including the number and the `·`.
- **`RULES`** — `(text pattern, account, review)`, first match wins. Add a line
  like `(r"NEW VENDOR", SOME_ACCOUNT, False),` to auto-categorize a new vendor.

---

## Technical notes (why this imports cleanly)

- **Format:** tab-delimited `TRNS` / `SPL` / `ENDTRNS` blocks — the transaction
  IIF dialect QuickBooks Desktop expects.
- **Account references:** accounts are referenced by their **bare name**
  (`Cash`, `Office`, …) — the string QuickBooks matches on when account numbers
  are enabled — and the file opens with an `!ACCNT` block declaring each account
  with its number and type so every account resolves on import. (Referencing the
  display form `1000 · Cash` instead makes the 2024 importer fail every row,
  because no account is literally *named* that.) To switch styles, see
  `ACCOUNT_REF_STYLE` / `EMIT_ACCNT_BLOCK` at the top of `td_to_iif.py`.
- **Encoding:** written as Windows-1252 (ANSI) with CRLF line endings.
- **Signs:** deposits post `+` to `1000 · Cash`; checks/ACH debits post `−`. Each
  block nets to zero, so the register always balances.
- **Transaction types:** money in = `DEPOSIT`; money out (checks and ACH debits)
  = `CHECK`, with the real check number in `DOCNUM` where there is one.
- **Reconciliation guard:** the parsed Deposits, Electronic Deposits, Checks
  Paid, Electronic Payments, and Other Withdrawals subtotals must equal the
  printed subtotals, and `beginning + deposits − withdrawals` must equal the
  printed ending balance. Any mismatch aborts with an explanation instead of
  writing a bad file.
- **Not reconciled to the register:** cleared status is left `N`; do a normal
  bank reconciliation in QuickBooks as usual.

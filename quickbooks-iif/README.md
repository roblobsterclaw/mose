# TD Bank statement → QuickBooks IIF converter

Turns a **TD Business Convenience Plus** PDF statement (the Valet Box / Surfbox
TD Valet account) into an **`.IIF` file** that **QuickBooks Desktop Pro 2024**
imports directly — so nobody has to key transactions in by hand every month.

There are three ways to use it:

1. **The browser app — `TD-to-IIF.html`** (recommended for staff). Double-click
   it, drag the PDF onto the page, download the `.iif`. No install, no command
   line, works offline, and the PDF never leaves the computer. See below.
2. **The drop-a-PDF folder watcher** (Python) — leave it running; drop a PDF in
   the `inbox/` folder; an `.iif` pops out.
3. **The command line** (Python, for one-offs / testing).

All three produce the **same** IIF file (the browser app's output is verified
byte-for-byte against the Python tool).

## Using it — the browser app (easiest, nothing to install)

1. Put **`TD-to-IIF.html`** somewhere handy on the QuickBooks computer (Desktop
   is fine). It's one self-contained file.
2. Double-click it — it opens in your web browser.
3. Drag one or more TD statement PDFs onto the page (or click to choose files).
4. Each statement gets its own result card with the reconciliation check and a
   category breakdown. If it ties out, a **Download** button appears — click it
   to save that statement's `.iif`.
5. Import each `.iif` into QuickBooks (see below), **once**.

Everything runs locally in the browser — no internet, no upload, no Python. If a
statement doesn't reconcile, that card shows why and offers **no** download.

### ⚠️ How to give it to staff (important)

`TD-to-IIF.html` is a program, not a web page — it must be **saved to the
computer and opened from there**. Do **not** email a link to it and click the
link: a forwarded/preview link points back to a server the staff aren't logged
into (so it errors), and email previews block the code it needs to run.

Do this instead:

- **Save the actual file** onto each computer that needs it — put it on a shared
  network drive, or copy it to each Desktop, or hand it over on a USB stick.
- Open it by **double-clicking the saved file** (it opens in Chrome/Edge). If
  Windows shows a blue "Windows protected your PC" box, click **More info →
  Run anyway** — that warning is just because the file came from outside; the
  app runs entirely offline and sends nothing anywhere.
- If double-click opens the wrong program, right-click → **Open with → Chrome**
  (or Edge).

To rebuild `TD-to-IIF.html` after changing the app (`app/template.html`) or the
account mapping, run `python3 app/build.py`.

## Multiple statements and multiple bank accounts

**Several months at once:** drop them all together (browser app), or pass them
all on the command line (`python3 td_to_iif.py jun.pdf jul.pdf aug.pdf`). Each
statement is converted **independently** into its own `.iif` — import each once.
They are never merged into one file, so a problem with one month can't affect
another, and you keep the one-month-one-import safety.

**Different bank accounts:** the tool reads the **Primary Account #** off each
statement and files it to the matching QuickBooks bank account, named
`<label>-<period>.iif` (e.g. `valet-box-2026-07.iif`). So you can drop a mix of
accounts and months together and get correctly separated files.

**The browser app learns the accounts as you go.** The first time it sees an
unfamiliar TD account, that statement's card asks *“Which QuickBooks cash/bank
account should this post to?”* — you type the account number (from your chart of
accounts, e.g. `1050`) and an optional short name, click **Convert**, and it's
done. With **Remember this account** ticked (the default), the answer is saved
on that computer, so it never asks again for that account — every future
statement for it converts automatically. Nothing gets misfiled to a default;
you decide once, when you actually know the answer.

> The remembered list lives in that browser on that computer. If you set the app
> up on several machines, each learns the accounts the first time it sees them
> (or tell me the mappings and I'll bake them in so they're known everywhere).

To pre-load accounts (so they're known before the first statement, on every
copy), add rows to the `BANK_ACCOUNTS` map near the top of both `td_to_iif.py`
and `app/template.html`, then rerun `python3 app/build.py`:

```
"123-4567890": { bank: "1050", label: "savings" },   // TD acct# -> QB bank #
```

The Python command-line tool doesn't prompt; an unmapped account there still
converts but posts to the default bank (`1000`) with an **“unmapped account”**
warning. Right now `437-7181733 → 1000 (valet-box)` is the only pre-loaded
account.

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

## ⚠️ Import each month exactly once (avoiding duplicates)

**QuickBooks IIF import does not check whether a transaction already exists.**
If a month is imported twice — or is included in another file you also import —
every transaction in that month is created a second time. There is no built-in
"skip duplicates" for IIF (that only exists for Bank Feeds).

The June 2026 duplication happened this way: an earlier year-to-date "FULL" file
already contained all 45 June transactions, and then the June-only file was
imported on top — so June posted twice.

Rules that keep it from happening again:

1. **One statement = one file = one import.** This tool produces a single file
   per statement (June from the June PDF, July from the July PDF). Import each
   once and never re-import a month.
2. **Don't import cumulative / year-to-date files anymore.** Because Jan–June are
   already in QuickBooks, going forward import **only the new month** each time.
3. Output files are now named by the statement's own period
   (`valet-box-2026-07.iif`), so re-running a month overwrites its file instead
   of quietly creating a second copy. The tool also prints an **IMPORT THIS FILE
   ONCE** banner with the period it covers.
4. **Always back up the company file right before importing** — that backup is
   your one-click undo if anything doubles up.

### Fixing the June duplication

Every June transaction is currently in QuickBooks twice. Two ways to clean it:

- **Easiest — restore the backup** you made right before importing the June-only
  file. That removes those 45 in one step and leaves the original set. Then fix
  the one item below.
- **If you can't restore** — in the `1000 · Cash` register, each June line now
  appears twice. Delete one copy of each. The copies from this tool have a
  **blank Payee** (description is in the Memo); the older copies have the Payee
  filled in — so delete whichever set you don't want to keep.

**One categorization fix either way:** the older file booked **check #1328
($19,500) to `6018 · Office`**, but you asked for **`1510 · Trucks & Equip`**.
Whichever copy you keep, make sure that check ends up in `1510`. (Files produced
by this tool already put it in `1510`.)

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
- **Account references:** accounts are referenced by their **number** (`1000`,
  `4000`, `6021`, …). This company file has account numbers enabled, and the
  2024 importer resolves accounts by number cleanly. There is **no `!ACCNT`
  block** — the accounts already exist, and a declared `!ACCNT` header with an
  `ACCNTNUM` column is rejected by the 2024 importer (`ACCNTNUM is not a valid
  column name`), which aborts the entire import. To change styles, see
  `ACCOUNT_REF_STYLE` / `EMIT_ACCNT_BLOCK` at the top of `td_to_iif.py`.
- **Encoding:** pure ASCII, CRLF line endings — nothing for QuickBooks to
  choke on.
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

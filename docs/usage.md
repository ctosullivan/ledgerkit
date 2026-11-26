# ledgerkit Usage Guide

ledgerkit can be used as a command-line tool or as a Python library.

---

## CLI Usage

### Syntax

```bash
ledgerkit [-h] [--version] [-v] [-1] [-o FILE] [-f FILE]... [-s] [-I] [-q TERMS] [-c STYLE] <command> [args...]
```

(current-state@v1#current-state-004)

You can also invoke it as a Python module (equivalent):

```bash
python -m ledgerkit [-f FILE]... [-s] <command> [args...]
```

All six report commands (`balance`, `register`, `accounts`, `print`, `stats`,
`check`) share this one flat set of flags — there is no per-command argument
parser (reports-cli@v1#reports-cli-001, reports-cli@v1#reports-cli-002).

### Other options

A few global flags aren't covered in their own section below:

| Flag | Effect |
|---|---|
| `--version` | Print ledgerkit's version and exit |
| `-v`, `--verbose` | More detailed output — currently only affects `stats` (adds commodity names to the `Commodities` line) |
| `-1` | `stats` only — print a single tab-separated summary line instead of the full labelled report |
| `-o`, `--output-file FILE` | Write a command's output to `FILE` instead of stdout |
| `-I`, `--ignore-assertions` | Skip the `assertions` check that otherwise runs by default on every command — see "Strict mode" and "`check`" below |

(reports-cli@v1#reports-cli-002, current-state@v1#current-state-004)

#### Specifying the journal file

Use `-f`/`--file` to specify the journal file (can be given more than once to
merge multiple files):

```bash
# Single file
ledgerkit -f myledger.journal stats

# Multiple files — transactions from both are merged in order
ledgerkit -f checking.journal -f savings.journal stats

# Read from stdin
cat myledger.journal | ledgerkit -f - stats
```

The positional argument is a shorthand for a single `-f` (kept for
backward compatibility):

```bash
ledgerkit stats myledger.journal
```

Combining `-f` with a positional journal argument is a hard error (exit
code 1). If no file is specified, ledgerkit checks the `$LEDGER_FILE`
environment variable, then falls back to `~/.hledger.journal`. If none of
these resolve to a file, ledgerkit exits 1 with "no journal file specified;
use -f FILE or set $LEDGER_FILE" (reports-cli@v1#reports-cli-003).

**Exception: the `check` command.** For `check`, every positional argument
is read as the *name* of a check to run — never as a journal file, even
though the same positional slot is a file-path shorthand for every other
command. The journal must still be supplied to `check` via `-f`,
`$LEDGER_FILE`, or the `~/.hledger.journal` default, exactly as for any
other command. Concretely, `ledgerkit check sample.journal` (with no `-f`)
does **not** check `sample.journal` — it is read as an (unrecognised) check
name, and because no `-f`/`$LEDGER_FILE` was given either, the command fails
with "no journal file specified; use -f FILE or set $LEDGER_FILE". The
correct form is `ledgerkit check -f sample.journal [check-name ...]`
(reports-cli@v1#reports-cli-003, current-state@v1#current-state-008).

---

### `-c` / `--commodity-style` — Override display style

By default ledgerkit infers the display style for each commodity from the first
amount it encounters in the journal. Use `-c` to override the style for a specific
commodity.

```bash
# Show £ amounts in European style (comma decimal, dot group separator)
ledgerkit -f myfile.journal -c '£1.000,00' balance

# Multiple overrides
ledgerkit -f myfile.journal -c '$1,000.00' -c '1.000,00 EUR' balance
```

The style string must contain at least one digit and a commodity symbol. The
commodity symbol must match exactly — `£` and `GBP` are two distinct identifiers
(ledgerkit does not know that they represent the same currency).

---

### `-q` / `--query` — Filter reports by a query string

Filters `balance`, `register`, `accounts`, `stats`, and `print` by a
space-separated query string. Supports `acct:`/bare pattern, `desc:`,
`date:` (simple dates only), `depth:N`/`depth:REGEX=N`, `status:`,
`tag:NAME[=REGEX]`, and `not:` — see
[`hledger-compatibility.md`](../dev-docs/hledger-compatibility.md#query-language-stage-c)
for the full term reference. Not supported by `check` (checks apply to
the whole journal by design). For `print`, a matching transaction is
shown **whole** — every posting, not just the one(s) that matched.

```bash
# Only food-related accounts
ledgerkit -f myledger.journal -q "acct:food" balance

# Cleared transactions in January 2024
ledgerkit -f myledger.journal -q "status:* date:2024-01-01..2024-02-01" register

# Multiple terms of the same prefix OR; different prefixes AND
ledgerkit -f myledger.journal -q "acct:food acct:rent status:*" balance

# Summarise to 2 levels of account detail
ledgerkit -f myledger.journal -q "depth:2" balance

# Collapse only assets-matching accounts to depth 1; everything else stays full
ledgerkit -f myledger.journal -q "depth:assets=1" balance

# Postings/transactions tagged "category" with any value
ledgerkit -f myledger.journal -q "tag:category" balance

# Only postings tagged category:food specifically
ledgerkit -f myledger.journal -q "tag:category=food" register

# Combine with other terms (always AND, never OR, across different tag: terms)
ledgerkit -f myledger.journal -q "tag:category=food tag:priority=high" print

# Exclude a tagged category
ledgerkit -f myledger.journal -q "not:tag:category=food" balance
```

Quote a multi-word pattern: `-q 'desc:"whole foods"'`. An invalid query
string (bad syntax, or a regex construct outside the supported subset)
prints an error and exits 1; a query matching nothing exits 0 with an
otherwise-empty (or, for `balance`, a bare `0` total) result — not an
error.

`depth:N`/`depth:REGEX=N` matches hledger's own `--depth`/`depth:`
exactly: it **truncates and aggregates** deeper accounts into their
depth-N ancestor for `balance`/`register`/`accounts` — it never excludes
a posting. `print` ignores `depth:` entirely (matching hledger's own
`print`, which does too). `stats` is the one exception: its `Accounts`
count/depth genuinely **excludes** deeper accounts rather than
aggregating them — a real hledger quirk specific to `stats`, not a
Ledgerkit choice. See
[`hledger-compatibility.md`](../dev-docs/hledger-compatibility.md#query-language-stage-c)
for the full explanation and the worked precedence examples for combining
multiple `depth:` terms.

`tag:NAME[=REGEX]` matches a posting's/transaction's **effective** tags —
not just its own literal `; name:value` comment, but also its
transaction's own tags, its account's declared-and-inherited tags (from
`account NAME ; tag:value` directives, including parent accounts), and
its commodity's declared tags (from `commodity SYMBOL ; tag:value`
directives). A bare `tag:NAME` matches any value, including an empty one;
`tag:NAME=REGEX` requires the value to match too. Multiple `tag:` terms
always **AND** together (never OR, unlike `acct:`/`desc:`/`status:`).
`not:tag:...` is valid. `accounts -q "tag:X"` is a deliberate exception:
it shows only transaction-level and account-inherited tags, not a
posting's own comment tags or commodity-propagated tags — matching
hledger's own `accounts` command exactly. See
[`hledger-compatibility.md`](../dev-docs/hledger-compatibility.md#query-language-stage-c)
for the full four-source model and the `accounts` visibility exception.

**An empty pattern is rejected, not treated as "match any value."**
`tag:NAME=` (a trailing `=` with nothing after it) raises an error —
real hledger rejects an empty regex at parse time, and Ledgerkit now
matches that exactly. If you want "any value, including empty," use the
**bare** form instead — `tag:NAME` (no `=` at all) already means that:

```bash
# Matches a NAME tag with any value, including an empty one
ledgerkit -f myledger.journal -q "tag:category" balance

# WRONG — raises an error (empty pattern), does not mean "any value"
ledgerkit -f myledger.journal -q "tag:category=" balance
```

The same rejection applies to an empty `acct:`/`desc:` pattern and an
empty `depth:REGEX=N` regex half — see
[`hledger-compatibility.md`](../dev-docs/hledger-compatibility.md#query-language-stage-c)
for the full writeup.

---

### `-s` / `--strict` — Strict mode

By default ledgerkit runs three checks on every command: `parseable`
(the journal loaded without errors), `autobalanced` (every transaction
nets to zero), and `assertions` (every `=`/`==`/`=*`/`==*` balance
assertion in the journal holds). Pass `-I`/`--ignore-assertions` to skip
the `assertions` check specifically — `parseable` and `autobalanced`
still run.

Strict mode adds two further checks on top of those three:

- **`accounts`** — every posting account must be declared with an `account`
  directive somewhere in the journal
- **`commodities`** — every commodity symbol must be declared with a `commodity`
  directive

(checks@v1#checks-001, reports-cli@v1#reports-cli-015)

```bash
ledgerkit -s -f myledger.journal stats
```

If any check fails, ledgerkit prints an error to stderr and exits with code 1
(reports-cli@v1#reports-cli-015).

---

### `check` — Run validation checks

The `check` command lets you run individual or grouped validation checks on
demand. A bare positional given to `check` always names a check, never a
journal file — see "Specifying the journal file" above.

```bash
# Run basic checks only (same as the default gate on all commands)
ledgerkit check -f myledger.journal

# Run strict checks (basic + accounts + commodities)
ledgerkit -s check -f myledger.journal

# Run specific named checks
ledgerkit check ordereddates -f myledger.journal
ledgerkit check payees ordereddates -f myledger.journal
ledgerkit check assertions -f myledger.journal
```

Available check names:

| Name | Tier | Description |
|---|---|---|
| `parseable` | basic | Journal loaded without errors (trivially satisfied) |
| `autobalanced` | basic | Every transaction nets to zero (one elided posting allowed) |
| `assertions` | basic | Every `=`/`==`/`=*`/`==*` balance assertion in the journal holds |
| `accounts` | strict | All posting accounts declared via `account` directives |
| `commodities` | strict | All commodity symbols declared via `commodity` directives |
| `payees` | other | All transaction descriptions declared via `payee` directives |
| `ordereddates` | other | Transactions appear in non-decreasing date order |
| `uniqueleafnames` | other | No two accounts share the same final colon-segment |

Basic-tier checks run on every command by default (skip `assertions`
specifically with `-I`). Strict-tier checks run in addition, for every
command, under `-s`. Other-tier checks run only when named explicitly as
a positional argument to `check`
(checks@v1#checks-001, checks@v1#checks-002, checks@v1#checks-003,
checks@v1#checks-004, checks@v1#checks-006, checks@v1#checks-007).

On success: no output, exit code 0. On failure: errors printed to stderr,
exit code 1 (reports-cli@v1#reports-cli-015, current-state@v1#current-state-008).

---

### `print` — Display transactions

Prints all transactions from the journal in a human-readable format.
Supports `-q`/`--query` (see above) — a matching transaction is printed
in full, all its postings included, and `print` ignores `depth:`
entirely, matching hledger's own `print` (reports-cli@v1#reports-cli-009).

Each transaction is printed as a header line — the date, then ` * ` for
a cleared transaction, ` ! ` for a pending one, or a single space
otherwise, then the description — followed by one indented line per
posting (the account name left-padded to 40 characters, then the
formatted amount, or just the account name if the posting is elided),
then a blank line (reports-cli@v1#reports-cli-009).

```bash
ledgerkit print myledger.journal
ledgerkit print -f myledger.journal -q "acct:food"
```

Example output:

```
2024-01-01 Opening balance
    assets:bank:checking                        £1000.00
    equity:opening-balances

2024-01-10 * Supermarket
    expenses:food                               £45.00
    assets:bank:checking
```

**`print` does not include inline (`;`) comments in its output.** Neither
a transaction-header comment nor a posting-level comment is ever printed,
even though ledgerkit's own journal serialiser (`transaction_to_text`/
`journal_to_text`, used to round-trip a `Transaction`/`Journal` back to
journal-format text) does preserve those same comments. This is a
confirmed, current limitation specific to `print`
(reports-cli@v1#reports-cli-010).

---

### `balance` — Account balances

Prints one line per (account, commodity) pair with a nonzero net amount:
the right-aligned formatted amount first, the account name second (shown
only on the last line for that account, after all of its commodity
lines). A dashed separator follows, sized to the widest amount/total
string, then one line per nonzero commodity grand total — or a bare `0`
if every commodity nets to zero overall. Negative amounts are shown in
red.

Ordinary zero-net (account, commodity) rows are omitted — **except** a
depth-0 `"..."` row (produced by a `depth:0` query), which is always
printed unconditionally regardless of its own value. In an unfiltered,
fully-balanced journal this collapsed row happens to net to zero, but
combined with an account-selecting `-q` filter, the same depth-0 `"..."`
row can net to a nonzero amount (the filtered subset need not itself
balance) and is still shown, under the same unconditional rule
(reports-cli@v1#reports-cli-005).

```bash
ledgerkit balance myledger.journal
```

---

### `register` — Transaction register

Prints a chronological list, one fixed-width line per posting: date,
description, an (abbreviated, if needed) account name, the amount, and a
running balance. The date and description are shown only on the first
posting of a given transaction — later postings of the same transaction
leave those two columns blank. Account names longer than 20 characters
are abbreviated by progressively shortening their leading colon-separated
components (e.g. `equity:opening-balances` becomes
`eq:opening-balances`); a running balance of exactly zero is shown as a
bare `0` with no commodity symbol (reports-cli@v1#reports-cli-007).

The running balance is a single cumulative total across every row in
output order — it is never re-grouped or re-aggregated per account, even
when a `depth:` query clips several postings' displayed account names
down to the same string; each posting still contributes its own row and
its own increment to the one running total
(reports-cli@v1#reports-cli-006).

```bash
ledgerkit register myledger.journal
```

---

### `accounts` — List accounts

Prints the sorted, deduplicated list of account names, one per line, with
no separator and no zero-total convention. A `-q` query that matches
nothing therefore produces genuinely empty output — unlike `balance`,
which always prints a separator and a total line even when nothing
matches (reports-cli@v1#reports-cli-008).

```bash
ledgerkit accounts myledger.journal
```

---

### `stats` — Journal statistics

Prints deterministic journal statistics: transaction count, date range,
transactions-per-day figures, payee count, account count and depth,
commodity count and names, and price count, plus runtime figures
(elapsed time, transactions per second) that are measured by the CLI
itself (reports-cli@v1#reports-cli-011).

```bash
ledgerkit stats myledger.journal
```

Example output:

```
Main file           : /path/to/sample.journal
Included files      : 0
Txns span           : 2024-01-01 to 2024-01-20 (20 days)
Last txn            : 2024-01-20 (987 days ago)
Txns                : 5 (0.2 per day)
Txns last 30 days   : 0 (0.0 per day)
Txns last 7 days    : 0 (0.0 per day)
Payees/descriptions : 5
Accounts            : 6 (depth 3)
Commodities         : 1
Market prices       : 0
Runtime stats       : 0.02 s elapsed, 211 txns/s
```

(current-state@v1#current-state-008)

With `-1`, `stats` instead prints a single tab-separated line (version,
source file path, elapsed-time string, transactions-per-second string).
With `-v`/`--verbose`, the `Commodities` line additionally lists the
commodity names in parentheses (reports-cli@v1#reports-cli-011).

`stats` is the one report command where a `depth:N` query **excludes**
accounts deeper than the limit from the account count/depth figures,
rather than clipping and rolling them up the way `balance`, `register`,
and `accounts` all do for the same `depth:` query — a genuine, deliberate
hledger quirk specific to `stats`, not a Ledgerkit choice
(reports-cli@v1#reports-cli-012).

---

## Exit codes

A successful `check` run, and a successful `accounts`/`stats` run, exit
0. Exit 1 on: any `check` failure; a failing basic check on any command
(unless suppressed with `-I`); a file-resolution error (no journal found,
or `-f` combined with a positional journal argument); and a `check`
invocation whose bare positional was consumed as a check name instead of
a file (see "Specifying the journal file" above)
(reports-cli@v1#reports-cli-003, reports-cli@v1#reports-cli-008,
reports-cli@v1#reports-cli-015, current-state@v1#current-state-008).

---

## Python Library Usage

```python
import ledgerkit

# Load a journal file
journal = ledgerkit.load("myledger.journal")

# Access transactions directly
for txn in journal.transactions:
    print(txn.date, txn.description)

# Run reports (returns data, not formatted strings)
account_list = journal.accounts()   # AccountsResult (behaves like list[str])
balances     = journal.balance()    # BalanceResult (behaves like a nested
                                     # dict: account -> commodity -> Decimal)
rows         = journal.register()   # RegisterResult (behaves like list[RegisterRow])
summary      = journal.stats()      # JournalStats
```

(reports-cli@v1#reports-cli-004)

See [python-api.md](python-api.md) for full library documentation.

---

## Getting Help

```bash
ledgerkit --help
```

Running `--help` on an individual subcommand (e.g. `ledgerkit balance
--help`) currently prints this exact same top-level help text — there is
no separate, subcommand-specific help page
(reports-cli@v1#reports-cli-001, current-state@v1#current-state-005).

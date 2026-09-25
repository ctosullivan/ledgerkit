# ledgerkit Usage Guide

ledgerkit can be used as a command-line tool or as a Python library.

---

## CLI Usage

### Syntax

```bash
ledgerkit [-f FILE]... [-s] <command> [args...]
```

You can also invoke it as a Python module (equivalent):

```bash
python -m ledgerkit [-f FILE]... [-s] <command> [args...]
```

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

If no file is specified, ledgerkit checks the `$LEDGER_FILE` environment
variable, then falls back to `~/.hledger.journal`.

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

---

### `-s` / `--strict` — Strict mode

By default ledgerkit checks that every transaction balances (the `autobalanced`
check). Strict mode adds two extra checks:

- **`accounts`** — every posting account must be declared with an `account`
  directive somewhere in the journal
- **`commodities`** — every commodity symbol must be declared with a `commodity`
  directive

```bash
ledgerkit -s -f myledger.journal stats
```

If any check fails, ledgerkit prints an error to stderr and exits with code 1.

---

### `check` — Run validation checks

The `check` command lets you run individual or grouped validation checks on
demand.

```bash
# Run basic checks only (same as the default gate on all commands)
ledgerkit check -f myledger.journal

# Run strict checks (basic + accounts + commodities)
ledgerkit -s check -f myledger.journal

# Run specific named checks
ledgerkit check ordereddates -f myledger.journal
ledgerkit check payees ordereddates -f myledger.journal
```

Available check names:

| Name | Description |
|---|---|
| `parseable` | Journal loaded without errors (trivially satisfied) |
| `autobalanced` | Every transaction nets to zero (one elided posting allowed) |
| `accounts` | All posting accounts declared via `account` directives |
| `commodities` | All commodity symbols declared via `commodity` directives |
| `payees` | All transaction descriptions declared via `payee` directives |
| `ordereddates` | Transactions appear in non-decreasing date order |
| `uniqueleafnames` | No two accounts share the same final colon-segment |

On success: no output, exit code 0. On failure: errors printed to stderr, exit code 1.

---

### `print` — Display transactions

Prints all transactions from the journal in a human-readable format.
Supports `-q`/`--query` (see above) — a matching transaction is printed
in full, all its postings included.

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

---

### `balance` — Account balances

Prints the net balance for every account.

```bash
ledgerkit balance myledger.journal
```

---

### `register` — Transaction register

Prints a chronological list of all postings with running balances.

```bash
ledgerkit register myledger.journal
```

---

### `accounts` — List accounts

Prints all account names found in the journal, sorted alphabetically.

```bash
ledgerkit accounts myledger.journal
```

---

### `stats` — Journal statistics

Prints a summary: file name, transaction count, account count, date range,
and commodities used.

```bash
ledgerkit stats myledger.journal
```

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
account_list = journal.accounts()   # list[str]
balances     = journal.balance()    # dict[str, Decimal]
rows         = journal.register()   # list[RegisterRow]
summary      = journal.stats()      # JournalStats
```

See [python-api.md](python-api.md) for full library documentation.

---

## Getting Help

```bash
ledgerkit --help
```

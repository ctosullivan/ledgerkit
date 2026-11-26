# ledgerkit

[![Tests](https://github.com/ctosullivan/ledgerkit/actions/workflows/tests.yml/badge.svg)](https://github.com/ctosullivan/ledgerkit/actions/workflows/tests.yml)
[![License: GPL v3 or later](https://img.shields.io/badge/License-GPLv3%2B-blue.svg)](LICENSE)

A deterministic, Python-native accounting and query engine with a
documented [hledger](https://hledger.org)-compatible foundation.
ledgerkit uses hledger as its primary accounting and compatibility
reference — it implements most important hledger functionality and
preserves compatibility where it's useful, but it does not aim to be a
line-for-line Python clone. Where Python or modern tooling offers a
materially better design, ledgerkit says so explicitly rather than
copying a limitation for its own sake. See
[dev-docs/compat-register/](dev-docs/compat-register/) for the
machine-readable record of exactly which behaviours match hledger, which
are deliberate extensions, and which are documented, intentional
divergences.

## Status

As of this writing, ledgerkit's declared version is `1.0.0.dev1`, it
targets Python `>=3.8`, and it declares zero required runtime
dependencies. An optional `pandas` extra (`pandas>=1.3`) is available for
callers who want DataFrame-based access to report output
(current-state@v1#current-state-001).

Running the project's own test suite currently produces 935 collected
tests, 29 skipped, and zero failures or errors (`OK (skipped=29)`). This
is a point-in-time figure, re-confirmed live while writing this section,
rather than a permanently fixed guarantee (current-state@v1#current-state-003).

## Features

- Parse `.journal` files compatible with the hledger 1.52 format
- Comprehensive directive support: `include`, `account`, `commodity`, `payee`,
  `tag`, `alias`, `P`, `Y`, `D`, `decimal-mark`, `apply account`, `comment`
- Core CLI commands: `balance`, `register`, `accounts`, `print`, `stats`, `check`
- Strict mode (`-s`) and balance assertions
- Multi-commodity balances with tree rollup
- Commodity display style inference and `-c` override flag
- Optional pandas DataFrame export (`pip install ledgerkit[pandas]`)
- Editor-integration layer: lenient parser, round-trip writer, `EditorDocument`
- Pure Python — no third-party runtime dependencies
- Python 3.8–3.12

## Requirements

- Python 3.8+

## Installation

```bash
pip install ledgerkit
```

With optional pandas support:

```bash
pip install ledgerkit[pandas]
```

### Development install

```bash
git clone https://github.com/ctosullivan/ledgerkit.git
cd ledgerkit
pip install -e ".[pandas]"
```

## Usage

### CLI

```bash
ledgerkit balance myfile.journal
ledgerkit register myfile.journal
ledgerkit accounts myfile.journal
ledgerkit print myfile.journal
ledgerkit stats myfile.journal
```

You can also invoke ledgerkit as a Python module:

```bash
python -m ledgerkit balance myfile.journal
```

See [docs/usage.md](docs/usage.md) for the full CLI reference (flags,
query syntax, per-command examples). The rest of this section covers the
CLI's overall shape and a handful of behavioural details worth knowing
up front.

### Python library

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")
accounts = journal.accounts()
balance  = journal.balance()
```

See [docs/python-api.md](docs/python-api.md) for the full library reference.

## Command-line interface

ledgerkit exposes exactly six report/validation subcommands through a
single flat `argparse` parser, selected via one required positional
`command` argument: `balance`, `register`, `accounts`, `print`, `stats`,
`check`. There is no `argparse` subparsers tree, so no subcommand has its
own distinct `--help` text — every subcommand's `--help` output is
byte-identical to the top-level `--help` output
(reports-cli@v1#reports-cli-001; current-state@v1#current-state-004,
current-state@v1#current-state-005).

A shared set of global flags applies uniformly to every command regardless
of which report is selected: `--version`; `-v`/`--verbose` (for `stats`,
also shows commodity names); `-1` (stats only: a single tab-separated
output line); `-o`/`--output-file FILE`; `-f`/`--file FILE` (repeatable);
`-s`/`--strict`; `-I`/`--ignore-assertions`; `-q`/`--query TERMS`; and
`-c`/`--commodity-style STYLE` (repeatable) (reports-cli@v1#reports-cli-002).

### Journal file resolution

For every command except `check`, the journal file is resolved with a
strict four-tier precedence: one or more `-f`/`--file` flags, then a
single positional `journal` argument as shorthand, then the
`$LEDGER_FILE` environment variable, then `~/.hledger.journal` if
present. Combining `-f` with a positional argument is a hard error, and
exhausting all four sources without a result exits with "no journal file
specified." For the `check` command specifically, any positional
arguments are read as check *names*, never as a journal-file shorthand —
`check` must get its journal from `-f`, the environment variable, or the
default (reports-cli@v1#reports-cli-003).

## Reports

### `balance`

`balance` computes per-commodity net balances for each account. The
underlying `reports.balance()` function returns a flat mapping (account →
commodity → net amount) by default, or, with `tree=True`, a list of rows
that additionally include every implicit parent account with aggregated
self-plus-descendant amounts and an `is_subtotal` marker
(reports-cli@v1#reports-cli-004).

The CLI prints one line per (account, commodity) pair — right-aligned
amount first, account name shown only on that account's last row — a
dashed separator sized to the widest amount/total string, then one
grand-total line per nonzero commodity (or a bare `"0"` if everything nets
to zero). Zero-net rows are omitted, except that a depth-0 `"..."` row
(produced by a `depth:0` query) is always printed regardless of its own
value, including when it is nonzero because the queried subset doesn't
itself balance to zero. Negative amounts are wrapped in ANSI red escape
codes (reports-cli@v1#reports-cli-005).

### `register`

`register`'s underlying `reports.register()` function returns a
chronological list of rows whose `running_balance` is described as a
single cumulative sum across every row in output order, not re-grouped or
re-aggregated per account — even when a depth setting causes several
postings' displayed account names to collapse to the same string
(reports-cli@v1#reports-cli-006). That specific accumulation-under-depth-
clipping interaction has not been independently re-confirmed beyond the
original claim, so it is stated here with that caveat.

On screen, `register` prints one fixed-width line per row (date,
description, abbreviated account, right-aligned amount, right-aligned
running balance). The date and description columns are blanked on every
row after a transaction's first posting, long account names are
abbreviated by progressively shortening leading (non-last)
colon-separated components, and a running balance of exactly zero prints
as a bare `"0"` (reports-cli@v1#reports-cli-007).

### `accounts`

`accounts` prints the sorted, deduplicated list of account names, one per
line, with no separator or total-line convention — a query that matches
nothing produces genuinely empty output, unlike `balance`
(reports-cli@v1#reports-cli-008).

### `print`

`print` reprints each matching transaction in journal-like text: a header
line with date, status flag, and description, followed by one indented
line per posting. A `-q`/`--query` filter on `print` matches whole
transactions — if any posting matches, every posting of that transaction
is printed, not just the matching one — and `print` deliberately ignores
`depth:` entirely, matching hledger's own `print` semantics
(reports-cli@v1#reports-cli-009).

`print` does not serialize inline comments: neither a transaction
header's nor a posting's inline comment is ever printed. This is a real,
confirmed divergence from the journal-text round-trip that
`ledgerkit.writer.transaction_to_text()` provides for the same data.
Whether this omission is a deliberate scope decision for `print` or an
unnoted gap is an open, unresolved question that the available evidence
does not settle (reports-cli@v1#reports-cli-010).

### `stats`

`stats`'s underlying `reports.stats()` function returns a dataclass
holding only deterministic journal data (transaction counts, date range,
account/commodity counts, and so on); elapsed-time and
transactions-per-second figures are measured and formatted only by the
CLI layer, never stored on that dataclass. By default the CLI prints a
multi-line labeled report; with `-1` it instead prints one tab-separated
line (version, source file, elapsed time, transactions/second); with
`-v`/`--verbose`, the "Commodities" line additionally lists commodity
names (reports-cli@v1#reports-cli-011).

`stats` is the one report function where a `depth:` query constraint
*excludes* accounts deeper than the limit from the account count, rather
than clipping/aggregating them the way `balance`, `register`, and
`accounts` all do — a deliberate, source-confirmed exception rather than
an oversight (reports-cli@v1#reports-cli-012).

### `check`

`check` has a distinct control-flow path: an unconditional "basic checks"
gate runs before every command (including `check` itself), alongside
`check`'s own named-check logic. `-I`/`--ignore-assertions` suppresses
only the "assertions" basic check, in both that gate and in `check`'s own
explicit run; `-s`/`--strict` additionally runs a stricter check set for
every non-`check` command, and is forwarded into `check` itself
(reports-cli@v1#reports-cli-015). See [docs/usage.md](docs/usage.md) for
the full list of named checks.

### Report specs (Python API only)

`reports.balance_from_spec()` computes a structured, multi-section
balance report (for example, an income statement with an inverted
"Income" section) from `ReportSpec`/`ReportSection` dataclasses. It is
reachable from the Python API (`ledgerkit.balance_from_spec`,
`ledgerkit.ReportSpec`, `ledgerkit.ReportSection`) but, as of this
writing, is not wired to any of the six CLI subcommands
(reports-cli@v1#reports-cli-013).

## Journal text serialization

`ledgerkit.writer.transaction_to_text()` serializes a single transaction
to hledger journal-format text designed to round-trip through the parser
back to an equivalent transaction (same date, flag, description,
postings, amounts, and comments). Amount columns are right-aligned to a
shared column computed from the widest account name among postings that
carry an explicit amount, and an elided posting is printed as a bare
account name with no amount. `journal_to_text()` serializes a whole
journal's transactions separated by exactly one blank line each. As of
this writing, `journal_to_text()` explicitly does not serialize
directives (`account`, `commodity`, `payee`, `P`); callers needing full
round-trip fidelity for directives are expected to keep the raw source
file instead (reports-cli@v1#reports-cli-014).

## Journal format support

See [docs/journal-format.md](docs/journal-format.md) for the full,
annotated syntax reference. The behavioural highlights below are worth
knowing even if you only read this README:

- A transaction header line accepts dates in several forms —
  `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYY.MM.DD`, and year-omitted forms with
  optional leading zeros and mixed separators — optionally followed by a
  secondary date introduced with `=`, an optional status flag (`*`
  cleared, `!` pending), an optional parenthesized code, a description,
  and an optional `;`-introduced inline comment
  (journal-parsing@v1#journal-parsing-001,
  journal-parsing@v1#journal-parsing-002).
- A posting line is split into account and amount on the first run of two
  or more whitespace characters, so an account name containing a single
  internal space survives intact; a posting with no amount token after
  that split is treated as an elided amount, resolved later by computing
  the net of the transaction's other postings per commodity
  (journal-parsing@v1#journal-parsing-003,
  journal-parsing@v1#journal-parsing-005).
- Amount parsing supports prefix and suffix commodity symbols, leading or
  mid-token minus signs, comma-thousands/period-decimal formatting by
  default (reversible via a `decimal-mark` directive), E-notation, and
  space-separated digit groups. A posting amount may also carry a balance
  assertion (`=`, `==`, `=*`, `==*`), a cost annotation (`@`/`@@`), and
  lot annotations (`{amount}`, `[date]`, `(label)`), all mutually
  composable on one line (journal-parsing@v1#journal-parsing-004,
  journal-parsing@v1#journal-parsing-009).
- Only `;`-led comments are ever scanned for tags — `#`-led comments
  never are, whether at column 0 or indented inside a transaction block
  (journal-parsing@v1#journal-parsing-006).
- The parser offers two public entry points: `parse_string` raises on the
  first malformed line; `parse_string_lenient` is designed to collect
  errors/warnings into a returned list and resume parsing at the next
  transaction, intended for editor integrations that re-parse on every
  keystroke. A malformed non-indented `commodity` directive is a
  confirmed exception to that "never raises" design: it raises
  unconditionally even under `parse_string_lenient`. This is the one
  exception the available evidence names explicitly; it should not be
  read as a guarantee that no other case can break the "never raises"
  contract (journal-parsing@v1#journal-parsing-008).

## Hledger Compatibility

ledgerkit tracks its behavioural compatibility with hledger through a
structured compatibility register
([dev-docs/compat-register/](dev-docs/compat-register/)), rather than an
informal list. Each entry is classified under a closed, five-value `kind`
taxonomy — `compatible`, `extension`, `intentional_divergence`,
`unsupported`, `unexplained_mismatch` — and carries a four-tier `status`:
`proposed`, `self-verified` (confirmed by the same session that
implemented the feature), `verified` (confirmed only by a
separately-dispatched differential-testing role, never the implementing
session itself), and `final` (compat-system@v1#compat-system-001,
compat-system@v1#compat-system-002).

As of this writing, the register holds 49 entries: 40 `compatible`, 6
`unsupported`, 2 `unexplained_mismatch` (both already resolved via the
register's own forward-reference lifecycle — the original entries are
kept unmodified, with a new entry created to supersede each), and 1
`intentional_divergence`; no entry yet uses the `extension` kind. Of
those 49, 26 are at `status: proposed`, 9 are `self-verified`, and 14 are
`verified`; none has yet reached `final`. These counts describe an
actively-changing register, not a fixed figure
(compat-system@v1#compat-system-003, compat-system@v1#compat-system-004,
compat-system@v1#compat-system-005).

See [dev-docs/hledger-compatibility.md](dev-docs/hledger-compatibility.md)
for the human-readable in-scope/out-of-scope/undecided breakdown of which
hledger journal features are supported.

## Known current limitations

- `print` does not preserve inline comments on round-trip through the
  journal text, and whether this is intentional is an open, unresolved
  question (reports-cli@v1#reports-cli-010).
- A malformed `commodity` directive is not actually caught leniently by
  `parse_string_lenient`, despite that function's documented "never
  raises" design (journal-parsing@v1#journal-parsing-008).
- `check`'s positional arguments are read as check names, not as a
  journal-file shorthand, unlike every other command's positional
  argument (reports-cli@v1#reports-cli-003).
- `reports.balance_from_spec()` and its `ReportSpec`/`ReportSection`
  dataclasses are usable from the Python API but are not wired to any
  CLI subcommand (reports-cli@v1#reports-cli-013).
- Over half of the hledger-compatibility register's entries are still at
  the lowest verification tier (`proposed`), meaning the corresponding
  compatibility claims have not yet been checked against the real
  hledger binary by an independent process
  (compat-system@v1#compat-system-004).

## Documentation

| Guide | Description |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | Installation, first run, verification |
| [docs/usage.md](docs/usage.md) | CLI commands with examples |
| [docs/journal-format.md](docs/journal-format.md) | Supported journal syntax with annotated examples |
| [docs/python-api.md](docs/python-api.md) | Python library reference |

## Python ecosystem (pandas)

Install the optional pandas extra for DataFrame export:

```bash
pip install ledgerkit[pandas]
```

Then:

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")

# Export all postings to a DataFrame
df = journal.to_dataframe()
print(df.groupby("account")["amount"].sum())

# Or export directly from a report object
balance_df = journal.balance().to_dataframe()
register_df = journal.register().to_dataframe()
accounts_df = journal.accounts().to_dataframe()
```

## Development

```bash
# Run all tests
python -m unittest discover -s tests -t . -v
```

See [dev-docs/architecture.md](dev-docs/architecture.md) for module design and
[dev-docs/api-spec.md](dev-docs/api-spec.md) for the full API specification.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for pull request guidelines, commit
message format, and branch naming. This project follows the
[Contributor Code of Conduct](CODE_OF_CONDUCT.md).

### With AI tooling (Claude Code)

Clone the full repository including AI-workflow files:

```bash
git clone https://github.com/ctosullivan/ledgerkit.git
```

### Without AI tooling

Use sparse checkout to clone only the source code, tests, and human docs
(excludes `CLAUDE.md`, `dev-docs/`, `CHANGELOG.md`, `ROADMAP.md`):

```bash
git clone --filter=blob:none --sparse https://github.com/ctosullivan/ledgerkit.git
cd ledgerkit
git sparse-checkout set ledgerkit tests docs README.md LICENSE pyproject.toml
```

## Acknowledgements

ledgerkit is a Python implementation inspired by two pioneering plain-text
accounting projects. We gratefully acknowledge their authors and contributors.

### Ledger

**John Wiegley** created Ledger, the original plain-text double-entry accounting
tool, which established the journal file format and accounting model that this
ecosystem is built upon.

  https://github.com/ledger/ledger

### hledger

**Simon Michael** created hledger, a Haskell implementation of Ledger's concepts,
which has since evolved its own rich feature set and extensive documentation.
ledgerkit's journal format and query-language support is modelled primarily
on the hledger 1.52 specification, and ledgerkit is licensed under the same
licence family as hledger (GPL-3.0-or-later) specifically so that hledger's
own documentation, source, and test suite can be used directly — with
provenance recorded — to understand and verify intended behaviour. See
[dev-docs/planning/core-redefinition/10-source-assisted-development.md](dev-docs/planning/core-redefinition/10-source-assisted-development.md)
for exactly what that does and doesn't mean in practice.

  https://github.com/simonmichael/hledger

A full list of hledger contributors can be found at:

  https://github.com/simonmichael/hledger/blob/main/doc/CREDITS.md

Their work — and the broader plain-text accounting community — makes ledgerkit
possible.

## Licence

ledgerkit is licensed under the **GNU General Public License v3.0 or later**
(GPL-3.0-or-later) — see [LICENSE](LICENSE) and [NOTICE](NOTICE). This
matches hledger's own licence exactly (also GPL-3.0-or-later), which is
deliberate: see
[dev-docs/planning/core-redefinition/02-licence-migration.md](dev-docs/planning/core-redefinition/02-licence-migration.md)
for why. Released versions **before** this change (0.1.0 through 1.0.0,
and the 1.0.0.dev1 pre-release) remain available under the MIT License they
were originally published under — this is not retroactive.

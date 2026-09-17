# Architecture

## Overview

ledgerkit follows a linear data-flow pipeline:

```
Journal file(s) (.journal / .ledger)
        │
        ▼
  [ loader.py ]           ← File I/O, include directive expansion, path resolution,
        │                   glob matching, and circular include detection
        ▼
  [ parser.py ]           ← Pure text → structured Python objects (no file I/O)
        │
        ▼
  [ models.py ]           ← Core data model: Transaction, Posting, Amount, etc.
        │
        ▼
  [ commodity_style.py ]  ← CommodityStyle: display-style inference and formatting
        │
        ▼
  [ checks.py ]           ← Validation checks on Journal objects (balance, strict mode, etc.)
        │
        ▼
  [ reports.py ]          ← Consumes model objects, produces report data;
        │                   BalanceResult / RegisterResult / AccountsResult wrappers
        ▼
  [ cli.py ]              ← Validates, formats and prints report data for the terminal
        │
        ▼
  [ _pandas_compat.py ]   ← Lazy pandas import helper (optional dependency)
```

**`ledgerkit/query/`** (Stage C) sits alongside this pipeline rather than
strictly within its linear flow: `cli.py` parses a `-q`/`--query` string
once via `ledgerkit.query.parser.parse()` into a `QueryPlan` (Stage C
Phase 5 — previously a bare `QueryNode`), which bundles two genuinely
different things: `plan.predicate` (a `QueryNode` selection AST) and
`plan.depth` (a `ledgerkit.query.depth.DepthSpec` report-display option —
**never** a selection predicate; see below). `cli.py` passes
`plan.predicate` into `reports.py`'s `balance`/`register`/`accounts`/
`stats` via a private, internal-only parameter (`_query_ast` — not part
of the public API; see `knowledge/DECISIONS.md`, 2026-09-16) and
`plan.depth` via a second private parameter (`_query_depth`, added Phase
5). For `print` (which has no `reports.py` function of its own — it
iterates `journal.transactions` directly in `cli.py`), only
`plan.predicate` is used, via `ledgerkit.query.eval.matches_transaction`
called directly inline — `plan.depth` is never even read for `print`,
which is what makes it correctly ignore `depth:` entirely, matching
hledger's own `print` (confirmed source+executable,
`21-stage-c-phase-5-depth-and-verification-plan.md` §1.3). Filtering
always delegates to `ledgerkit.query.eval.matches_posting`/
`matches_transaction` for the predicate half, and to
`ledgerkit.query.depth.clip_account_name` (or, uniquely for `stats`,
`account_excluded_by_depth` — a genuine, source-confirmed hledger quirk
where `stats` excludes rather than clips; see that function's own
docstring) for the depth half — never a second, local reimplementation of
either. `ledgerkit/query/` does not import from `reports.py`, `cli.py`,
or `checks.py` — only from `models.py` — so the existing "each module
imports only from modules
below it" principle still holds with `query/` sitting at the same layer
as `models.py`.

**`ledgerkit/tags.py`** (Stage C Phase 4) is a small, pure-function module
that also sits alongside the main pipeline rather than in its linear flow.
`parser.py` calls `tags.parse_tags(comment)` at the point a transaction's,
posting's, or account-directive's `inline_comment` text has already been
fully assembled (same-line plus any follow-on indented `;` lines), and
stores the resulting `list[tuple[str, str]]` on the relevant model field
itself (`Transaction.tags`, `Posting.tags`, `Journal.declared_account_tags`)
— `tags.py` never mutates a model object directly. It also provides
`effective_date`/`effective_date2`, pure functions over a `(Transaction,
Posting)` pair that resolve a posting's `date:`/`date2:` comment-tag
overrides against the transaction's own dates, matching ledgerkit's
existing no-back-reference design (`Posting` has no reference back to its
owning `Transaction`). `tags.py` imports only from `models.py` (under
`TYPE_CHECKING`, for type hints only), so it sits at the same layer as
`models.py` and `query/`.

---

## Module Responsibilities

### `ledgerkit/loader.py`

**Single responsibility**: File I/O, include directive expansion, path
resolution, glob matching, circular include detection, stdin loading, and
multi-file merging.

- `load_journal(path)` — load a single `.journal` or `.ledger` file; returns a
  fully populated `Journal` object
- `load_journal_stdin()` — read journal text from `sys.stdin`; returns a
  `Journal` with `source_file = "(stdin)"`
- `merge_journals(journals)` — concatenate a list of `Journal` objects into
  one; `source_file` from the first; `included_files` summed
- Recursively expands `include` directives before parsing (text-expansion
  strategy), so directive scope propagates naturally through included content
- Resolves include paths: relative (to containing file's directory), absolute,
  and tilde (`~`) expansion; glob patterns via `glob.glob(recursive=True)`
- Detects circular includes by tracking visited paths
- Populates `journal.source_file` and `journal.included_files`
- Raises `ParseError` for unsupported extensions, format prefixes, circular
  includes, or glob patterns that match no files
- Raises `FileNotFoundError` if the root file or a non-glob included file does
  not exist

### `ledgerkit/parser.py`

**Single responsibility**: Convert raw `.journal` text (a Python string) into
`Transaction` objects and a `Journal` container.

- `parse_string(text)` — the sole public function; operates on text only,
  performs no file I/O
- Reads journal text line by line via a state machine
- Recognises transaction headers, postings, comments, and directives
- Delegates inline-comment tag extraction (`name:value` pairs) to
  `tags.parse_tags()` once a transaction's/posting's/account-directive's
  comment text is fully assembled, and applies posting-level `date:`/
  `date2:` tag overrides via `tags`-adjacent helpers
- Raises `ParseError` with line number on malformed input
- Does **not** perform any balance validation, file loading, or reporting logic
- `include` directive lines encountered in raw text are silently skipped
  (expansion is always done by `loader.py` before `parse_string` is called)

### `ledgerkit/models.py`

**Single responsibility**: Define the canonical Python data structures for
journal entries.

Core types:
- `Amount` — a numeric value paired with a commodity symbol
- `Posting` — an account name plus an optional `Amount`, inline comment
  `tags`, and optional `date_override`/`date2_override` (from `date:`/
  `date2:` comment tags; see `ledgerkit/tags.py`)
- `Transaction` — a date, optional cleared/pending flag, description, list
  of `Posting`s, and inline comment `tags` (no date-override field —
  `date:`/`date2:` tags only take effect at posting scope)
- `Journal` — top-level container: a list of `Transaction`s, a list of
  `PriceDirective`s, `declared_accounts`, `declared_account_tags`,
  `declared_commodities`, `declared_payees`, `source_file`, and
  `included_files` count

Models are plain dataclasses. They contain no parsing or reporting logic.

### `ledgerkit/checks.py`

**Single responsibility**: Validate `Journal` objects and return structured
errors without raising exceptions.

- `CheckError` — dataclass with `check_name` and `message` fields
- Individual check functions (`check_autobalanced`, `check_accounts`,
  `check_commodities`, `check_payees`, `check_ordereddates`,
  `check_uniqueleafnames`) — each returns `list[CheckError]`
- Convenience runners: `run_basic_checks`, `run_strict_checks`, `run_checks`
- Does **not** perform any file I/O, parsing, or formatting

### `ledgerkit/reports.py`

**Single responsibility**: Accept a `Journal` and produce structured report
data (not formatted strings).

Reports:
- `balance(journal, ...)` → mapping of account name → running balance
- `register(journal, ...)` → list of register rows (date, description, amount, balance)
- `accounts(journal)` → sorted list of account names
- `stats(journal)` → `JournalStats` dataclass with summary statistics

Reports do **not** print to stdout — they return data that `cli.py` formats.

### `ledgerkit/cli.py`

**Single responsibility**: Parse command-line arguments and coordinate
`loader` → `checks` → `reports` → formatted output.

- Uses `argparse` from the standard library
- Resolves journal file(s) via `_resolve_files()`: `-f`/`--file` flags (one or
  more), then positional shorthand, then `$LEDGER_FILE`, then
  `~/.hledger.journal`
- Loads each file with `loader.load_journal()` (or `load_journal_stdin()` for
  `-f -`), then merges with `loader.merge_journals()`
- Runs default basic checks (`autobalanced`, `parseable`) via `checks.run_basic_checks()`
  on every command before proceeding; exits 1 on failure
- With `-s`/`--strict`: additionally runs `accounts` and `commodities` checks
- `check [NAME...]` command: runs specified checks via `checks.run_checks()`
- Calls the appropriate `reports.*` function
- Formats and prints the result to stdout

---

## Error Handling Strategy

| Layer | Error type | Action |
|---|---|---|
| `loader` | `ParseError` | Raised for extension/format/circular/glob errors; line numbers re-attributed to original source file |
| `loader` | `FileNotFoundError` | Raised if root or non-glob included file is missing |
| `parser` | `ParseError` | Raised with line number and message |
| `checks` | `list[CheckError]` | Returned (never raised); CLI converts to stderr + exit 1 |
| `reports` | `ValueError` | Raised for invalid arguments |
| `cli` | Any | Caught, printed to stderr, exit code 1 |

---

## Design Principles

- Each module imports only from modules below it in the pipeline
  (`cli` → `loader` → `parser`/`models`; `cli` → `checks` → `models`;
  `reports` → `models`)
- No circular imports
- No global mutable state
- Every new dataclass field on `Posting`/`Transaction` (and similar model
  types) must make a deliberate `compare=` choice, not accept the
  dataclass default silently. A field that changes a posting/transaction's
  *accounting meaning* (an amount, a cost, a lot, a posting-type flag)
  should compare `True`; a field that's parse-context/provenance metadata
  only (`source_line`, `source_span`, `raw_text`, `inline_comment`,
  `Amount.raw`) should be `compare=False`, matching the existing
  precedent. Getting this backwards either breaks equality-based tests on
  metadata that shouldn't affect equality, or lets two accounting-distinct
  postings compare equal. See `dev-docs/planning/core-redefinition/
  16-model-review.md` §16.4.

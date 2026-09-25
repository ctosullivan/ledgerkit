# API Specification

Status key: `[IMPLEMENTED]` · `[STUB — Milestone 2]` · `[PLANNED]`

---

## Top-level (`ledgerkit/__init__.py`)

### `load` `[IMPLEMENTED]`

```python
def load(path: str | os.PathLike) -> Journal:
    """Load a .journal or .ledger file and return a Journal object.

    Alias for loader.load_journal(). Supports include directives.
    Intended for programmatic use:
        import ledgerkit
        journal = ledgerkit.load("myfile.journal")

    Raises:
        FileNotFoundError: if the path or a non-glob included file does not exist.
        ParseError: if an extension is unsupported, a format prefix is used,
                    a circular include is detected, a glob matches nothing,
                    or the file contents are malformed.
    """
```

Also invocable as a module:

```
python -m ledgerkit <command> <journal-file>
```

---

## `ledgerkit/models.py`

### `Amount` `[IMPLEMENTED]`

```python
@dataclass
class Amount:
    quantity: Decimal
    commodity: str  # e.g. "£", "$", "EUR", "AAPL"
```

Represents a single monetary or commodity amount.

---

### `BalanceAssertion` `[IMPLEMENTED]`

```python
@dataclass
class BalanceAssertion:
    amount: Amount
    inclusive: bool = False       # True for =* and ==*
    sole_commodity: bool = False  # True for == and ==*
```

An inline balance assertion attached to a posting.  Corresponds to the
hledger assertion markers `=`, `==`, `=*`, `==*`.  See
`dev-docs/hledger-compatibility.md` for syntax and semantics.

---

### `Posting` `[IMPLEMENTED]`

```python
@dataclass
class Posting:
    account: str                                    # e.g. "expenses:food"
    amount: Amount | None = None                    # None means "infer from other postings"
    balance_assertion: BalanceAssertion | None = None  # optional inline assertion
    cost_raw: str | None = None                     # raw cost annotation text (e.g. "$180.00" from "@ $180.00") [ADDED IN v0.2.0]
    source_line: int | None = None                  # 1-based line number; None for programmatic objects
    inferred: bool = False                          # True for postings synthesised by resolve_elision()
    tags: list[tuple[str, str]] = field(default_factory=list)          # [NEW — Stage C Phase 4]
    date_override: datetime.date | None = None      # [NEW — Stage C Phase 4]
    date2_override: datetime.date | None = None     # [NEW — Stage C Phase 4]
```

One line within a transaction, mapping an account to an amount.

The wire format requires **two or more spaces** between the account name and the
amount. A single space is treated as part of the account name, allowing names such
as `expenses:fun money`. When no double-space separator is present, the posting has
no amount (`amount=None` — elided).

`inferred` is set to `True` on postings synthesised by `resolve_elision()` and is
`False` for all postings parsed directly from journal text. `repr=False` keeps the
dataclass repr clean.

**`tags`** `[NEW — Stage C Phase 4]`: this posting's own inline-comment tags
(same-line plus its own follow-on comment lines), as an ordered list of
`(name, value)` pairs — **not** a dict; a name may legitimately repeat with
different values (see `ledgerkit/tags.py`). Does **not** include tags
inherited from the posting's account or its transaction (that inheritance
is deliberately not computed by this layer — see `knowledge/DECISIONS.md`,
2026-09-17).

**`date_override`/`date2_override`** `[NEW — Stage C Phase 4]`: set only
when this posting's own comment contains a `date:`/`date2:` tag whose value
parses as a simple date (using the transaction's own year as the fallback
default). A distinct mechanism from `Transaction.date2` — a journal may use
both simultaneously; the posting-level override takes precedence for that
one posting's *effective* date (`ledgerkit.tags.effective_date`/
`effective_date2`), computed on read, never mutating `Transaction.date`/
`date2`. An unparseable `date:`/`date2:` value is a `ParseError` (raised
immediately in strict mode; collected in lenient mode, override left
unset).

---

### `Transaction` `[IMPLEMENTED]`

```python
@dataclass
class Transaction:
    date: datetime.date
    description: str
    date2: datetime.date | None = None  # secondary/auxiliary date (e.g. "2024-01-01=2024-01-03") [ADDED IN v0.2.0]
    postings: list[Posting]
    cleared: bool = False          # True if marked with "*"
    pending: bool = False          # True if marked with "!"
    code: str = ""                 # Optional transaction code in parentheses
    comment: str = ""              # Inline or trailing comment text
    source_line: int | None = None # 1-based line number of the header in source file
    tags: list[tuple[str, str]] = field(default_factory=list)  # [NEW — Stage C Phase 4]
```

Represents a complete journal transaction entry.

**`tags`** `[NEW — Stage C Phase 4]`: this transaction's own inline-comment
tags, same shape as `Posting.tags`. Deliberately has **no**
`date_override`-equivalent field: hledger's `date:`/`date2:` tags have an
overriding effect only in a *posting's* own comment — at the transaction
level they are ordinary tags with no special meaning at all (verified
against hledger source and its own `check-tags.test` fixture; see
`knowledge/DOMAIN_RULES.md`).

**Wire → model mapping** (see `dev-docs/hledger-compatibility.md` for block delimiters):

```
"2024-01-15 * (INV-42) Groceries ; comment"
  │            │  │       │        │
  │            │  │       │        └── comment     = "comment"
  │            │  │       └─────────── description = "Groceries"
  │            │  └─────────────────── code        = "INV-42"
  │            └────────────────────── cleared     = True  (pending = False)
  └─────────────────────────────────── date        = date(2024, 1, 15)
```

`postings` preserves journal order. A `Posting` with `amount=None` is an *elided*
posting whose value is inferred from the other postings at reporting time.

---

### `PriceDirective` `[IMPLEMENTED]`

```python
@dataclass
class PriceDirective:
    date: datetime.date
    commodity: str   # The commodity being priced, e.g. "AAPL", "EUR"
    price: Amount    # The price expressed as an Amount (quantity + currency symbol)
```

Represents one `P` directive from the journal. Stored in `Journal.prices`.

Example journal line: `P 2024-03-01 AAPL $179.00`

Commodity valuation using these records (converting amounts between commodities
in reports) is in scope for v1 and will be implemented in Milestone 2.

---

### `Journal` `[IMPLEMENTED]`

```python
@dataclass
class Journal:
    transactions: list[Transaction]
    prices: list[PriceDirective] = field(default_factory=list)
    declared_accounts: list[str] = field(default_factory=list)
    declared_commodities: list[str] = field(default_factory=list)
    declared_payees: list[str] = field(default_factory=list)
    declared_tags: list[str] = field(default_factory=list)
    declared_account_tags: dict[str, list[tuple[str, str]]] = field(default_factory=dict)  # [NEW — Stage C Phase 4]
    declared_commodity_tags: dict[str, list[tuple[str, str]]] = field(default_factory=dict)  # [NEW — Stage C Phase 6]
    source_file: str | None = None
    included_files: int = 0   # count of distinct files pulled in via include
```

**`declared_account_tags`** `[NEW — Stage C Phase 4]`: directly-declared
tags per account, from `account NAME ; tag:value` directive comments
(including its own follow-on indented `;` comment lines — confirmed by
hledger's manual as a real, documented feature, not inferred). Keyed by
the exact declared account name. **Directly-declared tags only — does
not include tags inherited from a parent account** (that inheritance
computation is a separate, not-yet-built concern; see
`dev-docs/planning/core-redefinition/19-tag-query-semantics-brief.md` §2).
Additive alongside `declared_accounts`, whose `list[str]` shape is
unchanged, per the existing 2026-09-13 guardrail in `knowledge/
DECISIONS.md`.

**`declared_commodity_tags`** `[NEW — Stage C Phase 6]`: directly-declared
tags per commodity symbol, from `commodity SYMBOL ; tag:value` directive
comments (including its own follow-on indented `;` comment lines) —
mirrors `declared_account_tags`'s exact shape and merge behaviour (multiple
`commodity` directives for the same symbol accumulate). hledger propagates
these onto every posting whose main amount uses that commodity (the
"commodity tags" feature — `hledger.1:3550-3556`); Ledgerkit computes that
propagation on demand via `ledgerkit.tags._effective_tags` (private — see
`ledgerkit/tags.py` below), never by mutating `Posting.tags`/
`Transaction.tags`. See `dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md` §2.6.

Top-level container for all parsed journal data.

`declared_accounts`, `declared_commodities`, `declared_payees`, and `declared_tags` are populated
by `account`, `commodity`, `payee`, and `tag` directives respectively. The first three are used
by the strict-mode checks in `checks.py`; `declared_tags` is reserved for the deferred `check tags`.

`included_files` is set by `loader.load_journal()`. When `parse_string()` is
called directly (no file I/O), it remains `0`.

**Report methods** (delegate to `ledgerkit.reports` via lazy import):

```python
def balance(self, accounts: list[str] | None = None,
            query: Query | None = None,
            tree: bool = False) -> dict[str, dict[str, Decimal]] | list[BalanceRow]: ...
def register(self, accounts: list[str] | None = None,
             query: Query | None = None) -> list[RegisterRow]: ...
def accounts(self) -> list[str]: ...
def stats(self, query: Query | None = None) -> JournalStats: ...
```

The `accounts` parameter on `balance()` and `register()` is deprecated — use `query=`
for new code. When both are supplied, `query` takes precedence.

---

### `Query` `[IMPLEMENTED — Milestone 2]`

```python
@dataclass
class Query:
    account:     str | None = None        # substring or regex; matches posting account names
    not_account: str | None = None        # exclusion filter on account names
    payee:       str | None = None        # substring or regex; matches transaction description
    date_from:   datetime.date | None = None  # inclusive lower bound
    date_to:     datetime.date | None = None  # inclusive upper bound
    depth:       int | None = None        # max account tree depth (colon-segment count)
```

All fields are optional and default to `None`. `Query()` with all `None` fields is
semantically equivalent to `query=None` (no filter). `account`, `not_account`, and
`payee` patterns are matched as plain case-insensitive substrings unless the string
contains a regex metacharacter, in which case `re.search` is used.

Re-exported from `ledgerkit.__init__` as `ledgerkit.Query`.

---

### `BalanceRow` `[NEW — Milestone 3]`

```python
@dataclass
class BalanceRow:
    account: str               # full account path, e.g. "assets:bank"
    depth: int                 # number of ':' separators (0 = top-level)
    amounts: dict[str, Decimal]  # commodity → net balance (own + descendants)
    is_subtotal: bool          # True for implicit parent accounts with no direct postings
```

One row in a tree-mode balance report, as returned by `balance(tree=True)`.
`amounts` aggregates all descendant postings in addition to the account's own postings.
`is_subtotal` is `True` when the account name appears as a prefix in another account's
path but has no postings directly attributed to it.

Re-exported from `ledgerkit.__init__` as `ledgerkit.BalanceRow`.

---

### `RegisterRow` `[IMPLEMENTED — Milestone 2]`

```python
@dataclass
class RegisterRow:
    date:            datetime.date
    description:     str
    account:         str
    amount:          Amount
    running_balance: Decimal
```

One row in a register report. `running_balance` is the cumulative sum of
`amount.quantity` across all rows in output order.

Re-exported from `ledgerkit.__init__` as `ledgerkit.RegisterRow`.

---

### `ReportSection` `[IMPLEMENTED — Milestone 2]`

```python
@dataclass(frozen=True)
class ReportSection:
    name:     str                     # display name, e.g. "Fixed Expenses"
    accounts: tuple[str, ...]         # account patterns to include (OR logic)
    exclude:  tuple[str, ...] = ()    # account patterns to exclude
    label:    str | None = None       # override for subtotal line; defaults to f"Total {name}"
    depth:    int | None = None       # depth cap for this section; overrides outer Query depth
    invert:   bool = False            # negate all amounts (use for income sections)
```

Frozen dataclass — instances are immutable and safe to share across report calls.
`accounts` uses OR logic: a posting is included if it matches any pattern.
`exclude` patterns are applied as a final subtraction.

Re-exported from `ledgerkit.__init__` as `ledgerkit.ReportSection`.

---

### `ReportSpec` `[IMPLEMENTED — Milestone 2]`

```python
@dataclass(frozen=True)
class ReportSpec:
    name:           str
    sections:       tuple[ReportSection, ...]
    show_subtotals: bool = True
    show_total:     bool = True
    total_label:    str = "Net"
```

A structured report definition composed of named sections. Frozen dataclass.

> **Note:** Journal-comment-based spec parsing (`; report` / `; end report` syntax)
> is `[DEFERRED — Milestone 3]`. In Milestone 2, specs are constructed
> programmatically only.

Re-exported from `ledgerkit.__init__` as `ledgerkit.ReportSpec`.

---

### `ReportSectionResult` `[IMPLEMENTED — Milestone 2]`

```python
@dataclass
class ReportSectionResult:
    section:  ReportSection
    rows:     dict[str, Decimal]   # account name → net balance (after invert)
    subtotal: Decimal              # sum of all values in rows (after invert)
```

Mutable result object returned per section by `balance_from_spec()`.

Re-exported from `ledgerkit.__init__` as `ledgerkit.ReportSectionResult`.

---

## `ledgerkit/tags.py` `[NEW — Stage C Phase 4]`

**Not re-exported from `ledgerkit/__init__.py`.** Pure functions only — no
file I/O, no model mutation; `parser.py` calls into this module and stores
the results on `Posting`/`Transaction`/`Journal` itself. An independent
Python implementation of hledger 1.52.4's inline-tag grammar (not a
line-for-line port — see `knowledge/DECISIONS.md`, 2026-09-17).

```python
def parse_tags(comment: str | None) -> list[tuple[str, str]]:
    """Extract name:value tags from already-assembled comment text.
    Ordered list, never a dict — a name may legitimately repeat with a
    different value. A space immediately before the colon voids that
    candidate tag entirely. A value runs to the next ',' or end of line
    (no escaping — a value cannot contain a literal comma); a colon
    inside a value is fine."""

def effective_date(txn: Transaction, posting: Posting) -> datetime.date:
    """posting.date_override if set, else txn.date."""

def effective_date2(txn: Transaction, posting: Posting) -> datetime.date:
    """posting.date2_override, else txn.date2, else posting.date_override,
    else txn.date — hledger's own four-level fallback chain exactly."""
```

Grounded in `dev-docs/planning/core-redefinition/19-tag-query-semantics-
brief.md` and `20-tag-parsing-syntax-brief.md`. Through Stage C Phase 5
this module implemented parsing and storage only; **Stage C Phase 6**
added the `tag:` query term's effective-tags computation here too
(account-tag inheritance, commodity-tag propagation, and the four-source
union `_effective_tags`/`_accounts_effective_tags` that `ledgerkit.query.
eval` calls into) — see `dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md`/`24-tag-query-matching-implementation-
plan.md`. These are **private** helpers (`_inherited_account_tags`,
`_commodity_tags`, `_posting_commodities`, `_effective_tags`,
`_accounts_effective_tags`), not part of this module's public surface
above — design §9.3's resolution: no new public API without a
demonstrated external consumer. `tag:` matching itself (the AST node,
parser, and evaluator branches) lives in `ledgerkit/query/`, not here;
see that section below. `dev-docs/hledger-compatibility.md`'s Query
Language section now documents `tag:` as implemented.

---

## `ledgerkit/parser.py`

### `ParseError` `[IMPLEMENTED]`

```python
class ParseError(ValueError):
    def __init__(self, message: str, line_number: int | None = None) -> None: ...
```

Raised on malformed journal input. `line_number` is 1-based when available.

---

### `ParseWarning` `[ADDED IN v0.2.0]`

```python
class ParseWarning(ParseError):
    """A non-fatal parse notice; does not prevent journal loading."""
```

Subclass of `ParseError` appended to `errors_out` in `parse_string_lenient` for
unsupported-but-skippable constructs (`~` periodic rule blocks, `=` auto-posting rule
blocks, nested `apply account` directives). Does **not** cause a transaction or
directive to be dropped; the surrounding context is preserved.

Callers distinguish warnings from hard errors with `isinstance`:

```python
journal, errors = parse_string_lenient(text)
hard = [e for e in errors if not isinstance(e, ParseWarning)]
warnings = [e for e in errors if isinstance(e, ParseWarning)]
```

---

### `parse_string` `[IMPLEMENTED]`

```python
def parse_string(text: str, default_year: int | None = None) -> Journal:
    """Parse a journal from a string and return a Journal object.

    Accepted date formats: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, and year-omitted
    forms such as M/DD or MM-DD. Leading zeros on month and day are optional.
    When the year is omitted, default_year is used (defaults to the current
    calendar year when None).

    Raises:
        ParseError: if the input is not valid hledger journal syntax.
    """
```

---

### `parse_string_lenient` `[NEW — Milestone 3]`

```python
def parse_string_lenient(
    text: str,
    default_year: int | None = None,
) -> tuple[Journal, list[ParseError]]:
    """Parse leniently, returning (journal_with_valid_txns, list_of_errors).

    Never raises. Intended for editor on_text_changed callbacks. Malformed
    transactions are skipped; valid transactions are included in the returned
    Journal. Directive-level errors (bad P directive, etc.) are also collected
    rather than raised. The error list may include `ParseWarning` instances
    (non-fatal notices) alongside hard `ParseError` objects; use
    `isinstance(e, ParseWarning)` to distinguish them.

    default_year: used for year-omitted dates; defaults to the current calendar
    year when None.
    """
```

Re-exported from `ledgerkit.__init__` as `ledgerkit.parse_string_lenient`.

---

### `resolve_elision` `[NEW — Milestone 3]`

```python
def resolve_elision(txn: Transaction) -> list[Posting]:
    """Resolve any single elided posting in txn into N concrete inferred postings.

    hledger rule: exactly one posting per transaction may have no amount. Its
    value is the negation of the sum of all other postings, computed
    independently per commodity. For N commodities in the other postings, N
    synthetic Posting objects are produced (sorted by commodity name) and
    spliced in at the elided posting's position.

    Returns list(txn.postings) unchanged when:
      - There are 0 elided postings (already fully specified)
      - There are 2+ elided postings (invalid — not resolved here)
      - All explicit postings have zero total (nothing to infer)

    Synthesised postings have inferred=True. Original postings retain
    inferred=False regardless of whether they came from parsed text or were
    constructed programmatically.
    """
```

Re-exported from `ledgerkit.__init__` as `ledgerkit.resolve_elision`.

---

---

## `ledgerkit/loader.py`

### `load_journal` `[IMPLEMENTED]`

```python
def load_journal(path: str | os.PathLike) -> Journal:
    """Load a .journal or .ledger file and return a Journal object.

    Handles include directives recursively. Included files are expanded at
    the point of the directive before parsing, preserving directive scope
    (e.g. an alias active before an include applies to included content).

    Path resolution in include directives:
      - ~/...       tilde expanded to the home directory
      - /abs/path   used as-is (absolute)
      - relative    resolved relative to the containing file's directory
      - Globs (* ** ? [range]) expanded via glob.glob; the containing file
        is always excluded from results.

    Populates journal.source_file (absolute path string) and
    journal.included_files (count of distinct included files).

    Raises:
        FileNotFoundError: if the root path or a non-glob included file
            does not exist.
        ParseError: if an extension is unsupported, a format prefix is
            used (e.g. timedot:), a circular include is detected, a glob
            matches no files, or the file contents are malformed.
    """
```

> **Note:** `parse_file()` was removed in this milestone. Use `load_journal()`
> (or the `ledgerkit.load` alias) for all file loading.

---

### `load_journal_stdin` `[IMPLEMENTED]`

```python
def load_journal_stdin() -> Journal:
    """Read a journal from stdin and return a Journal object.

    Parses the full stdin contents as hledger journal text.
    Sets source_file to "(stdin)". included_files is always 0.

    Raises:
        ParseError: if the stdin content is malformed.
    """
```

---

### `merge_journals` `[IMPLEMENTED]`

```python
def merge_journals(journals: list[Journal]) -> Journal:
    """Merge a list of Journal objects into a single Journal.

    Transactions, prices, declared_accounts, declared_commodities,
    declared_payees, and declared_tags are all concatenated in input order.
    source_file is taken from the first journal.
    included_files is the sum across all input journals.

    Raises:
        ValueError: if journals is empty.
    """
```

---

## `ledgerkit/checks.py`

### `CheckError` `[UPDATED — Milestone 3]`

```python
@dataclass
class CheckError:
    check_name: str          # e.g. "autobalanced", "accounts"
    message: str             # human-readable single-line description
    line_number: int | None = None  # 1-based source line of the offending entry; None when unavailable
```

`line_number` is populated for all transaction-level errors (autobalanced, assertions,
payees, ordereddates, accounts, commodities) and is `None` for errors without a
single clear source line (e.g. `uniqueleafnames`). The default is `None` for backward
compatibility with code that constructs `CheckError` directly.

Also re-exported from `ledgerkit.__init__` as `ledgerkit.CheckError`.

---

### Check constants `[IMPLEMENTED]`

```python
BASIC_CHECK_NAMES:  tuple[str, ...] = ("parseable", "autobalanced", "assertions")
STRICT_CHECK_NAMES: tuple[str, ...] = ("accounts", "commodities")
OTHER_CHECK_NAMES:  tuple[str, ...] = ("payees", "ordereddates", "uniqueleafnames")
```

---

### Individual check functions `[IMPLEMENTED]`

All return `list[CheckError]` — empty list means no errors.

| Function | Tier | Description |
|---|---|---|
| `check_parseable(journal)` | basic | Always `[]` — already parsed |
| `check_autobalanced(journal)` | basic | Each transaction nets to zero per commodity; one elided posting allowed |
| `check_assertions(journal)` | basic | All inline balance assertions pass; checked in date order |
| `check_accounts(journal)` | strict | All posting accounts appear in `declared_accounts` |
| `check_commodities(journal)` | strict | All commodity symbols in amounts appear in `declared_commodities`; zero-amount postings (commodity `""`) are exempt |
| `check_payees(journal)` | other | All transaction descriptions appear in `declared_payees` |
| `check_ordereddates(journal)` | other | Transactions in non-decreasing date order |
| `check_uniqueleafnames(journal)` | other | No two accounts share the same final colon-segment |

---

### `run_basic_checks` `[IMPLEMENTED]`

```python
def run_basic_checks(
    journal: Journal,
    *,
    skip: frozenset[str] | None = None,
) -> list[CheckError]:
    """Run parseable + autobalanced + assertions checks. Always run by the CLI.

    skip: names to suppress (e.g. frozenset({"assertions"}) for -I flag).
    """
```

---

### `run_strict_checks` `[IMPLEMENTED]`

```python
def run_strict_checks(
    journal: Journal,
    *,
    skip: frozenset[str] | None = None,
) -> list[CheckError]:
    """Run basic checks plus accounts + commodities checks."""
```

---

### `run_checks` `[IMPLEMENTED]`

```python
def run_checks(
    journal: Journal,
    names: list[str] | None = None,
    *,
    strict: bool = False,
    skip: frozenset[str] | None = None,
) -> list[CheckError]:
    """Run basic checks always; strict checks if strict=True;
    named 'other' checks if listed in names.

    skip: names to suppress entirely (e.g. frozenset({"assertions"}) for -I).

    Valid names: "parseable", "autobalanced", "assertions", "accounts",
    "commodities", "payees", "ordereddates", "uniqueleafnames".

    Raises:
        ValueError: if an unknown check name is provided.
    """
```

### `check_transaction_autobalanced` `[NEW — Editor Readiness]`

```python
def check_transaction_autobalanced(txn: Transaction) -> list[CheckError]:
    """Run the autobalanced check on a single Transaction.

    Returns [] if balanced or if the transaction has exactly one elided posting.
    Returns a list containing one CheckError per unbalanced commodity otherwise.
    Does not raise.
    """
```

Re-exported from `ledgerkit.__init__` as `ledgerkit.check_transaction_autobalanced`.

---

## `ledgerkit/writer.py` `[NEW — Editor Readiness]`

### `transaction_to_text`

```python
def transaction_to_text(txn: Transaction) -> str:
    """Serialise a Transaction to a journal-format string.

    The returned string ends with a single newline. When parsed by
    parse_string(), the result round-trips to an equivalent Transaction
    (same date, flag, description, postings, amounts, comments;
    source_span and raw_text are not checked).

    Formatting rules:
    - Date as YYYY-MM-DD.
    - Status flag (* or !) included if set.
    - Code in parentheses if set.
    - Transaction.inline_comment appended after '  ;' if not None.
    - Each posting indented with four spaces.
    - Amounts right-aligned at a consistent column (decimal points line up).
    - Elided posting (no amount) serialised as indented account name only.
    - Posting.inline_comment appended after '  ;' if not None.
    """
```

Re-exported from `ledgerkit.__init__` as `ledgerkit.transaction_to_text`.

### `journal_to_text`

```python
def journal_to_text(journal: Journal) -> str:
    """Serialise all transactions in journal.transactions to text.

    Transactions are separated by blank lines; the output ends with a single
    newline. Directives (account, commodity, payee, P) are not serialised in v1.
    """
```

Re-exported from `ledgerkit.__init__` as `ledgerkit.journal_to_text`.

---

## `ledgerkit/editor_model.py` `[NEW — Editor Readiness]`

### `EditorDocument`

```python
class EditorDocument:
    """An in-memory editable representation of a journal file.

    Attributes:
        path:    Resolved absolute path to the journal file.
        journal: Parsed Journal with all transactions (source_span populated).
        lines:   Current file content as a list of strings, one per line,
                 without newline characters.
        dirty:   True when lines differ from the last saved/loaded content.
    """

    def __init__(self, path: str) -> None:
        """Load the journal at path; populate journal and lines."""

    def add_transaction(self, txn: Transaction) -> None:
        """Insert txn into self.lines in chronological order."""

    def update_transaction(self, original: Transaction, updated: Transaction) -> None:
        """Replace the source lines of original with the serialised form of updated."""

    def delete_transaction(self, txn: Transaction) -> None:
        """Remove the source lines of txn and any immediately following blank line."""

    def save(self) -> None:
        """Write self.lines to self.path; set dirty=False."""

    def reload(self) -> None:
        """Re-read self.path from disk and re-parse."""

    def validate_transaction(self, txn: Transaction) -> list[CheckError]:
        """Run the autobalanced check on txn alone. Does not raise."""
```

V1 limitation: include directives in the edited file are silently ignored; the file
is parsed as-is via `parse_string()`. Use `loader.load_journal()` when full include
support is required (source_span values will reference merged-text line numbers in
that case).

Re-exported from `ledgerkit.__init__` as `ledgerkit.EditorDocument`.

---

## `ledgerkit/models.py` — `SourceSpan` `[NEW — Editor Readiness]`

```python
@dataclass
class SourceSpan:
    """Source location of a parsed transaction block."""
    file: str        # absolute path, "(string)", or "(stdin)"
    start_line: int  # 1-indexed, inclusive — transaction header line
    end_line: int    # 1-indexed, inclusive — last posting/comment line
```

Attached to `Transaction.source_span` by the parser. Also available as
`Transaction.raw_text` (verbatim source lines) and `Transaction.inline_comment`
(`str | None`). `Posting.inline_comment` (`str | None`) captures the text after `;`
on a posting line.

Re-exported from `ledgerkit.__init__` as `ledgerkit.SourceSpan`.

---

## `ledgerkit/reports.py`

All report functions accept a `Journal` as their first argument and are also
accessible as methods on `Journal` directly (e.g. `journal.balance()`).

### `balance` `[UPDATED — Milestone 3]`

```python
def balance(
    journal: Journal,
    query: Query | None = None,
    tree: bool = False,
) -> dict[str, dict[str, Decimal]] | list[BalanceRow]:
    """Return account balances, optionally in tree form.

    Flat mode (tree=False, default):
        Returns dict[account, dict[commodity, net_balance]].
        Only accounts with at least one matching posting are included.

    Tree mode (tree=True):
        Returns list[BalanceRow] sorted alphabetically by account path.
        Implicit parent accounts (no direct postings) are included with
        is_subtotal=True. Amounts aggregate own + all descendant postings.

    Elided posting amounts are resolved via resolve_elision() before
    aggregation. depth in the query truncates (rolls up) account names —
    matching hledger --depth behaviour.
    """
```

**Breaking change from Milestone 2**: the return type changed from
`dict[str, Decimal]` (single commodity assumed) to
`dict[str, dict[str, Decimal]]` (commodity-keyed). Update callers as:
```python
# Before (Milestone 2):
bal = journal.balance()["assets:bank"]  # Decimal
# After (Milestone 3):
bal = journal.balance()["assets:bank"]["£"]  # Decimal
```

`balance_from_spec` retains its `dict[str, Decimal]` return type (multi-commodity
support for spec-based reports is deferred).

---

### `register` `[IMPLEMENTED — Milestone 2]`

```python
def register(
    journal: Journal,
    query: Query | None = None,
) -> list[RegisterRow]:
    """Return a chronological list of register rows."""
```

`RegisterRow` is defined in `ledgerkit/models.py` and re-exported from `ledgerkit.__init__`.
See `RegisterRow` under `ledgerkit/models.py` above.

---

### `accounts` `[IMPLEMENTED — Milestone 2]`

```python
def accounts(journal: Journal, query: Query | None = None) -> list[str]:
    """Return a sorted list of all unique account names in the journal."""
```

---

### `stats` `[IMPLEMENTED]`

```python
@dataclass
class JournalStats:
    """Summary statistics for a journal. No runtime fields — CLI measures those."""
    source_file: str | None
    included_files: int              # count of distinct files pulled in via include
    transaction_count: int
    date_range: tuple[datetime.date, datetime.date] | None   # (first, last)
    last_txn_date: datetime.date | None
    last_txn_days_ago: int | None    # (today - last_txn_date).days
    txns_span_days: int | None       # (last - first).days + 1
    txns_per_day: float              # transaction_count / txns_span_days, else 0.0
    txns_last_30_days: int
    txns_per_day_last_30: float
    txns_last_7_days: int
    txns_per_day_last_7: float
    payee_count: int                 # unique descriptions
    account_count: int
    account_depth: int               # max colon-segment depth across all accounts
    commodity_count: int
    commodities: list[str]           # sorted commodity symbols
    price_count: int                 # len(journal.prices)

def stats(journal: Journal, query: Query | None = None) -> JournalStats:
    """Return summary statistics for the journal."""
```

When `query` is non-`None`, transaction-level filters (date range, payee) are applied
before computing statistics. `account`/`not_account` filters are not yet applied to
`account_count`/`account_depth` (deferred to a follow-on task); depth filters are, as
of Stage C Phase 5 — but via exclusion, not clipping, matching a genuine hledger quirk
specific to `stats` (see `dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md`).

Also accessible as `ledgerkit.JournalStats` (re-exported from `__init__.py`).

---

### `balance_from_spec` `[IMPLEMENTED — Milestone 2]`

```python
def balance_from_spec(
    journal: Journal,
    spec: ReportSpec,
    query: Query | None = None,
) -> list[ReportSectionResult]:
    """Compute a structured balance report driven by a ReportSpec."""
```

Returns one `ReportSectionResult` per section in `spec.sections` order. The outer
`query` acts as a uniform time/payee filter across all sections. Within each section,
`section.accounts` patterns are OR-combined and `section.exclude` patterns are
subtracted. `section.depth` overrides `query.depth` for that section only.
`section.invert` negates all amounts after aggregation.

Re-exported from `ledgerkit.__init__` as `ledgerkit.balance_from_spec`.

---

## `ledgerkit/cli.py`

### `main` `[IMPLEMENTED]`

```python
def main(argv: list[str] | None = None) -> int:
    """Entry point for the ledgerkit CLI.

    Args:
        argv: Argument list (defaults to sys.argv[1:] when None).

    Returns:
        Exit code (0 = success, 1 = error).
    """
```

CLI interface (via `pyproject.toml` `[project.scripts]` and `ledgerkit/__main__.py`):

```
ledgerkit [-f FILE]... [-s] [-v] [-1] [-o FILE] <command> [args...]
python -m ledgerkit [-f FILE]... [-s] [-v] [-1] [-o FILE] <command> [args...]

Flags:
  -f, --file         Read data from FILE, or stdin if -. May be specified
                     more than once; all files are merged in order. If not
                     given, falls back to the positional argument, then
                     $LEDGER_FILE, then ~/.hledger.journal.
  -s, --strict       Enable strict mode: also check that all posting accounts
                     and commodity symbols are declared via account/commodity
                     directives. Equivalent to running check accounts commodities
                     in addition to the default basic checks.
  -I, --ignore-assertions
                     Disable balance assertion checking (the assertions basic
                     check). Useful for troubleshooting or loading Ledger files.
  -v, --verbose      More detailed output (stats: show commodity names)
  -1                 Single tab-separated line (stats only)
  -o, --output-file  Write output to FILE instead of stdout

Commands:
  balance             Print account balances
  register            Print a register of transactions
  accounts            List all accounts
  print               Print transactions in journal format
  stats               Print journal statistics
  check [CHECK...]    Run validation checks; default runs basic checks only.
                      Named checks: parseable autobalanced accounts commodities
                                    payees ordereddates uniqueleafnames
```

**Default validation**: all commands run `autobalanced` and `parseable` checks
automatically before executing. Any failure prints an error to stderr and exits 1.

**`check` command**: accepts zero or more check names as positional arguments.
With no names, runs only the basic checks. With `-s`, also runs `accounts` and
`commodities`. Named `other` checks (`payees`, `ordereddates`, `uniqueleafnames`)
are run only if explicitly listed. Silent on success (exit 0); errors to stderr
(exit 1).

The positional `journal-file` argument (when not using `check`) is a
backward-compatible shorthand for `-f FILE`. Specifying both `-f` and a
positional argument is an error.

---

## `ledgerkit/query/` `[Stage C Phase 1; wired into cli.py/reports.py since Phase 2-3; depth: model changed Phase 5; tag: added Phase 6]`

Re-exported from `ledgerkit/__init__.py`. Wired into `cli.py`'s `-q`/
`--query` flag (all of `balance`/`register`/`accounts`/`stats`/`print`)
via `reports.py`'s private `_query_ast`/`_query_depth` parameters — see
`knowledge/DECISIONS.md`, 2026-09-16 (private, internal-only integration;
no public API change from that alone). Implements Stage C's term set:
`acct:`/bare pattern, `desc:`, `date:` (a single simple date, or two
simple dates joined by `-`/`..`/` to `, open-ended forms allowed),
`depth:N`/`depth:REGEX=N`, `status:`, `tag:NAME[=REGEX]` (Stage C Phase 6
— see `Tag` below), and `not:`/implicit-AND/same-prefix-OR combination.
`cur:` and hledger's smart/period date expressions, and the `PythonRegex`
extension syntax (`07-query-regex.md` §7.4) are **not implemented** —
Stage C follow-on work. Full semantics grounding: `dev-docs/planning/
core-redefinition/17-query-semantics-brief.md`; the Stage C Phase 5
`depth:` redesign: `21-stage-c-phase-5-depth-and-verification-plan.md`;
the Stage C Phase 6 `tag:` design/plan: `23-tag-query-matching-design.md`/
`24-tag-query-matching-implementation-plan.md`.

### `ledgerkit/query/ast.py`

```python
class TxnStatus(enum.Enum):
    UNMARKED = "unmarked"
    PENDING = "pending"
    CLEARED = "cleared"

@dataclass(frozen=True)
class Acct:
    pattern: str  # validated HledgerRegex-dialect pattern

@dataclass(frozen=True)
class Desc:
    pattern: str

@dataclass(frozen=True)
class DateSpan:
    start: datetime.date | None  # inclusive
    end: datetime.date | None    # EXCLUSIVE — see below

@dataclass(frozen=True)
class MaxAccountLevel:
    n: int  # >= 0 — see note below; NOT hledger's depth:

@dataclass(frozen=True)
class Status:
    value: TxnStatus

@dataclass(frozen=True)
class Tag:  # [NEW — Stage C Phase 6]
    name_pattern: str            # validated HledgerRegex-dialect pattern
    value_pattern: str | None = None  # None = any value, including empty

@dataclass(frozen=True)
class And:
    terms: tuple[QueryNode, ...]

@dataclass(frozen=True)
class Or:
    terms: tuple[QueryNode, ...]

@dataclass(frozen=True)
class Not:
    term: QueryNode

QueryNode = Union[Acct, Desc, DateSpan, MaxAccountLevel, Status, Tag, And, Or, Not]

@dataclass(frozen=True)
class QueryPlan:
    predicate: QueryNode  # never contains MaxAccountLevel
    depth: DepthSpec = field(default_factory=DepthSpec)  # default: empty (no clipping)
```

`DateSpan.end` is deliberately **exclusive**, matching hledger's real
`date:` span semantics — this differs from the existing
`ledgerkit.models.Query.date_to`, which is inclusive; the two are not
interchangeable. `Status`/`TxnStatus` are always transaction-level:
Ledgerkit's `Transaction`/`Posting` models have no per-posting status
override (unlike hledger), so there is no posting-level status distinct
from its transaction's.

**`MaxAccountLevel`** (renamed from `Depth`, Stage C Phase 5) is a
Ledgerkit-native, **Python-API-only** boolean predicate —
`accountNameLevel(account) <= n`. It has **no `-q`/`--query` string
syntax**: `ledgerkit.query.parser.parse()` never produces one; it exists
only for direct programmatic `QueryNode` construction. It is deliberately
NOT what `depth:`/`--depth` means in the `-q` string grammar — see
`ledgerkit.query.depth.DepthSpec` below, and `dev-docs/planning/
core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md` §3.1
for why hledger's own `depth:` was found (across every real command it
tested — `balance`/`register`/`print`/`accounts`) to be a report-display
clipping/aggregation option, never a selection predicate, and why the
existing boolean node was kept as a distinct, disclosed primitive rather
than reused under a colliding name.

**`Tag`** `[NEW — Stage C Phase 6]` matches an *effective* tag name (and,
if given, value) — the full four-source union hledger's own `tag:` reads
from (a posting's/transaction's own literal comment tags, its account's
declared-and-inherited tags, and its main amount's commodity's declared
tags; `ledgerkit.tags._effective_tags`), not merely
`Posting.tags`/`Transaction.tags`'s own literal contents. Evaluating a
`Tag` node needs `Journal` access — see `matches_transaction`/
`matches_posting`'s new `journal` parameter below. `value_pattern=None`
means "any value, including empty" (a bare `tag:NAME` term); both
patterns are case-insensitive infix, same contract as `Acct`/`Desc`. See
`dev-docs/planning/core-redefinition/23-tag-query-matching-design.md`
§2.2/§2.6/§2.7 for the full semantics.

**`QueryPlan`** is `ledgerkit.query.parser.parse()`'s return type (Stage C
Phase 5, changed from a bare `QueryNode`): `predicate` is the selection
AST as before; `depth` carries any `depth:`/`depth:REGEX=N` term(s) from
the query text, resolved by `ledgerkit.query.depth`, never folded into
`predicate`.

### `ledgerkit/query/depth.py` `[NEW — Stage C Phase 5]`

```python
@dataclass(frozen=True)
class DepthSpec:
    """Report-display depth clipping/aggregation — never a selection
    filter. flat: general depth, or None. by_pattern: (regex, depth)
    pairs from depth:REGEX=N, in declaration order."""
    flat: int | None = None
    by_pattern: tuple[tuple[str, int], ...] = ()

    def is_empty(self) -> bool: ...

def merge_depth_specs(a: DepthSpec, b: DepthSpec) -> DepthSpec:
    """Combines two DepthSpecs as hledger does for multiple depth: terms
    WITHIN one query (its DepthSpec Semigroup instance) — the smaller
    (more restrictive) flat depth wins, order-independent; by_pattern
    entries accumulate from both. NOT the same rule as multiple --depth
    CLI flags (last-wins) — Ledgerkit has no standalone --depth flag yet."""

def clipped_depth_for_account(spec: DepthSpec, account: str) -> int | None:
    """Resolves hledger's own precedence rule (getAccountNameClippedDepth):
    among by_pattern entries matching the account or a strict ancestor,
    the one starting to match at the greatest specificity wins (a pattern
    matching only the leaf, not any ancestor, is MOST specific); ties go
    to the later-declared entry; falls back to `flat` if none match;
    None if neither applies (no clipping)."""

def clip_account_name(spec: DepthSpec, account: str) -> str:
    """Applies clipped_depth_for_account's result. Depth 0 clips to the
    literal string "..." (confirmed live: hledger never produces an
    empty/excluded result at depth 0)."""

def account_excluded_by_depth(spec: DepthSpec, account: str) -> bool:
    """hledger's RAW Depth/DepthAcct boolean-EXCLUSION semantics — used
    ONLY by reports.stats(), a genuine source-confirmed exception (see
    reports.stats()'s own docstring and this function's own for the full
    evidence) where hledger excludes rather than clips."""
```

`DepthSpec`/its functions are never selection predicates — see
`reports.py`'s `balance`/`register`/`accounts`/`stats` below for how each
applies (or, for `stats`, deliberately does not apply)
`clip_account_name`.

### `ledgerkit/query/regex.py`

```python
class UnsupportedRegexConstructError(ValueError): ...

def validate_hledger_regex(pattern: str) -> None:
    """Raise UnsupportedRegexConstructError if pattern uses a construct
    outside the HledgerRegex-compatible subset (see module docstring for
    the excluded-construct list: '(?...)' forms, backreferences, GNU
    '\\<'/'\\>' boundaries, Perl shorthand classes, POSIX named classes,
    lazy quantifiers). Does not raise for constructs within the subset
    (literals, '.', '*', '+', '?', '{n,m}', '|', plain groups, anchors,
    plain bracket expressions, '\\b'/'\\B')."""

def compile_hledger_regex(pattern: str) -> re.Pattern[str]:
    """validate_hledger_regex(pattern), then re.compile(pattern, re.IGNORECASE)."""
```

### `ledgerkit/query/parser.py`

```python
class QueryParseError(ValueError): ...

def parse(query_text: str) -> QueryPlan:
    """Parse a query string into a QueryPlan (Stage C Phase 5 — changed
    from a bare QueryNode). An empty/whitespace-only string's predicate
    is And(()) — matches everything, consistent with Query()/query=None
    elsewhere in ledgerkit — and its depth is the empty DepthSpec().

    Combination rule for `predicate` (verified against hledger source,
    not invented): unnegated acct:/desc:/status: terms of the same type
    OR-combine with each other; every other term (date:, and any
    not:-wrapped term of any prefix) AND-combines individually. A negated
    term never joins an Or bucket even when its own prefix matches one of
    the three OR-eligible types.

    depth:N/depth:REGEX=N terms never reach `predicate` at all — they
    accumulate into `depth` via merge_depth_specs. not:depth:... raises
    QueryParseError (depth is a report option, not a negatable
    predicate). tag:NAME[=REGEX] (Stage C Phase 6) produces a Tag node;
    not:tag:... is valid (tag: is an ordinary predicate, unlike depth:)."""
```

### `ledgerkit/query/eval.py`

```python
def matches_transaction(node: QueryNode, txn: Transaction, journal: Journal | None = None) -> bool:
    """Transaction-oriented matching (used by print-like commands).
    Acct/MaxAccountLevel match if ANY posting in the transaction matches.
    Tag matches if txn's own tags directly match, OR any posting's
    effective tags match (Stage C Phase 6)."""

def matches_posting(node: QueryNode, txn: Transaction, posting: Posting, journal: Journal | None = None) -> bool:
    """Posting-oriented matching (used by register/balance-like commands).
    Desc/DateSpan/Status are transaction-level facts a posting inherits
    unchanged; Acct/MaxAccountLevel are checked against the posting's own
    account. depth: is never evaluated here — see ledgerkit.query.depth.
    Tag (Stage C Phase 6) matches against the posting's full effective
    tag set."""
```

`Depth`'s predicate is purely `accountNameLevel(account) <= n` (colon-
segment count) — hledger's separate depth-driven *display* truncation/
aggregation for `balance`/`register` is intentionally not represented
here; that is report-layer behaviour, not a query predicate.

**`journal` parameter** `[NEW — Stage C Phase 6]`: a real default
(`Journal | None = None`), so every existing caller that never constructs
a `Tag` node keeps compiling and running unchanged — see
`23-tag-query-matching-design.md` §9.1/§11 and
`24-tag-query-matching-implementation-plan.md`'s resolution of the
evaluator-API shape. **If a `Tag` node is evaluated with `journal=None`,
both functions raise `ValueError`** — never silently narrow to
own-tags-only (the design's binding loud-failure constraint). `ledgerkit.
reports.accounts` additionally uses a private, undocumented variant
(`ledgerkit.query.eval._matches_posting_for_accounts`) for its own
narrower Tag-matching mode (design §2.5/§9.2) — not part of this public
surface; `matches_posting`/`matches_transaction`'s own behaviour is
unaffected by its existence.

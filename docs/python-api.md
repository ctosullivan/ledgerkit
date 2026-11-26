# ledgerkit Python API

ledgerkit can be used as a Python library. The public API is designed to be
simple: load a journal file, then call report methods on the returned object.

Behavioural claims below that come from the Plan 29 clean-room evidence
pass are cited as `<topic-slug>@v1#<assertion-id>` (see
`dev-docs/clean-room/snapshots/`); claims carried over unchanged from this
document's own prior text are left uncited unless they needed correcting.

---

## Loading a Journal

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")
```

`ledgerkit.load()` accepts `.journal` or `.ledger` files and returns a
`Journal` object. It fully supports the `include` directive — included files
are resolved and expanded recursively, by textual substitution into one
combined source blob that is parsed exactly once, before parsing
(loader@v1#loader-005).

Raises `FileNotFoundError` if the file does not exist, or `ParseError` if
the file is malformed, uses an unsupported extension, contains a circular
include, or has a glob pattern that matches no files
(loader@v1#loader-004, loader@v1#loader-007).

**Known loading limitations.** The `FileNotFoundError`/`ParseError`
distinction above is not fully exhaustive: if a non-glob include target's
*containing directory* name happens to itself contain a glob metacharacter
(`*`, `?`, `[`), the target can be silently reclassified internally as a
glob pattern, match zero files, and raise an uncaught `IndexError` instead
of either documented exception — a confirmed, reproducible gap, not a
hypothetical one (loader@v1#loader-002, loader@v1#loader-003,
loader@v1#loader-007). Separately, a file that includes itself by its own
literal filename is filtered out by the self-reference guard and then
reported as `FileNotFoundError` even though the file demonstrably exists on
disk — a misleading, but currently real, error message
(loader@v1#loader-003).

You can also call the lower-level text parser directly (no file I/O, no
include directive support):

```python
from ledgerkit.parser import parse_string

journal = parse_string("2024-01-01 Test\n    assets:bank  £100\n    equity\n")
```

### Inferring elided amounts

A posting with no explicit amount is parsed with `amount=None` — it is
**not** automatically resolved. Call `ledgerkit.resolve_elision(txn)`
separately to get back the list of postings with the inferred amount
filled in (journal-parsing@v1#journal-parsing-005):

```python
from ledgerkit import resolve_elision

resolved = resolve_elision(txn)
```

If none of `txn.postings` are elided, the list is returned unchanged. If
exactly one is elided, it is replaced by one synthetic posting per distinct
commodity among the other postings (each the negation of that commodity's
net sum, sorted by commodity symbol, marked `inferred=True`), spliced in at
the original posting's position. Two or more elided postings is rejected by
the parser itself at parse time (`ParseError`), so `resolve_elision` only
ever sees that shape via a `Transaction` built by hand
(journal-parsing@v1#journal-parsing-005).

---

## The `Journal` Object

A `Journal` holds all parsed data from the file.

```python
journal.transactions   # list[Transaction]
journal.prices         # list[PriceDirective]  — from P directives
journal.source_file    # str | None  — absolute path of the root file
journal.included_files # int  — count of distinct files pulled in via include
```

### Report methods

All report methods are available directly on the `Journal` object:

```python
account_list = journal.accounts()   # AccountsResult (behaves like list[str])
balances     = journal.balance()    # BalanceResult (behaves like dict)
rows         = journal.register()   # RegisterResult (behaves like list[RegisterRow])
summary      = journal.stats()      # JournalStats — counts, date range, etc.
styles       = journal.commodity_styles  # dict[str, CommodityStyle]
```

`balance()`, `register()`, and `stats()` accept an optional `query=`
parameter for filtering — see the [Filtering with Query](#filtering-with-query)
section below. `accounts()` does not take a `query=` parameter.

`balance()` also accepts `tree=True`, returning `list[BalanceRow]` instead
of the default `dict[str, dict[str, Decimal]]` — see
[`BalanceRow`](#balancerow) below.

---

## Data Models

### `Transaction`

```python
txn.date          # datetime.date
txn.date2         # datetime.date | None  — secondary (effective) date
txn.description   # str
txn.postings      # list[Posting]
txn.cleared       # bool  — True if marked with *
txn.pending       # bool  — True if marked with !
txn.code          # str   — transaction code in parentheses, e.g. "INV-42"
txn.comment       # str   — inline comment text
txn.tags          # list[tuple[str, str]]  — this transaction's own comment tags
txn.source_span    # SourceSpan | None  — source location (parser-populated)
txn.raw_text        # str | None  — verbatim source lines
txn.inline_comment  # str | None  — text after ';' on the header line
```

`tags` is an ordered list, never a dict — the same tag name may legitimately
repeat with a different value (tags@v1#tags-007). There is deliberately no
`date_override`-equivalent field at the transaction level: a `date:`/
`date2:` tag written in a transaction-level comment is an ordinary tag with
no overriding effect at all — only a *posting's own* comment tag can
override a date (journal-parsing@v1#journal-parsing-010,
tags@v1#tags-008). See [Working with Tags](#working-with-tags) below.

### `Posting`

```python
posting.account           # str          — e.g. "expenses:food"
posting.amount             # Amount|None  — None means elided (inferred at report time)
posting.cost_raw           # str | None   — raw cost/lot annotation text, e.g. "@ $180"
posting.balance_assertion  # BalanceAssertion | None
posting.inferred            # bool  — True for postings synthesised by resolve_elision()
posting.tags                 # list[tuple[str, str]]  — this posting's own comment tags
posting.date_override        # datetime.date | None
posting.date2_override       # datetime.date | None
posting.inline_comment       # str | None  — text after ';' on the posting line
```

`date_override`/`date2_override` are set only from the first occurrence of
a `date`/`date2` comment tag on that posting's own parsed tags — never from
the transaction's tags (journal-parsing@v1#journal-parsing-010,
tags@v1#tags-008). An unparseable date value in such a tag raises
`ParseError` immediately in strict mode, or is collected with the override
left unset in lenient mode.

### `Amount`

```python
amount.quantity   # Decimal       — numeric value
amount.commodity  # str           — e.g. "£", "EUR", "AAPL"
amount.raw        # str | None    — original text as it appeared in the journal
```

`raw` is excluded from `__eq__`/`repr` comparison, so two `Amount`s with the
same quantity and commodity compare equal regardless of how each was
originally written (journal-parsing@v1#journal-parsing-010). A posting's
main amount references at most one commodity in ledgerkit's current data
model — there is no `MixedAmount` concept (tags@v1#tags-009).

`Amount.display(style)` — format the amount using a `CommodityStyle` object:

```python
style = journal.commodity_styles.get("£")
if style:
    print(amount.display(style))   # e.g. "£1,234.56"
```

### `PriceDirective`

```python
price.date        # datetime.date
price.commodity   # str     — the commodity being priced, e.g. "AAPL"
price.price       # Amount  — the price expressed as an Amount
```

### `BalanceRow`

Returned by `journal.balance(tree=True)` as `list[BalanceRow]` instead of
the default flat dict:

```python
row.account      # str   — full account path, e.g. "assets:bank"
row.depth        # int   — number of ':' separators (0 = top-level)
row.amounts      # dict[str, Decimal]  — commodity -> net balance (own + descendants)
row.is_subtotal  # bool  — True for implicit parent accounts with no direct postings
```

Includes every implicit parent account (every colon-prefix of every
posted-to account), each row's amounts aggregated over itself plus all
descendants, sorted alphabetically by account name
(reports-cli@v1#reports-cli-004).

### `RegisterRow`

One row returned by `journal.register()`:

```python
row.date             # datetime.date
row.description      # str
row.account          # str
row.amount           # Amount
row.running_balance  # Decimal
```

`running_balance` is the cumulative sum of `amount.quantity` across *all*
rows in output order — it is never re-grouped or re-aggregated by account,
even when a `depth` setting clips several postings' displayed account
names to the same string (reports-cli@v1#reports-cli-006).

### `SourceSpan`

```python
span.file        # str  — absolute path, "(string)", or "(stdin)"
span.start_line  # int  — 1-indexed, inclusive — transaction header line
span.end_line    # int  — 1-indexed, inclusive — last posting/comment line
```

Attached to `Transaction.source_span` by the parser.

---

## Working with Tags

`name:value` tags written in comments are available on `Transaction.tags`
and `Posting.tags` as ordered lists of `(name, value)` pairs — never a
dict, since the same tag name may legitimately repeat with a different
value (tags@v1#tags-007). `ledgerkit.tags` is not re-exported from
`ledgerkit.__init__`, but its two date-resolution helpers are commonly
useful directly:

```python
from ledgerkit.tags import effective_date, effective_date2

effective_date(txn, posting)   # posting.date_override if set, else txn.date
effective_date2(txn, posting)  # posting.date2_override, else txn.date2,
                                #   else posting.date_override, else txn.date
```

(tags@v1#tags-008)

`ledgerkit.query`'s `tag:NAME[=REGEX]` query term (see
[Filtering with Query](#filtering-with-query)) does not read `Posting.tags`/
`Transaction.tags` alone — it matches against the *effective* tags of a
(transaction, posting) pair: the posting's own tags, the transaction's own
tags, the posting's account's declared-and-inherited tags (walking every
ancestor), and the posting's commodity's declared tags, unioned with **no
shadowing or deduplication** — a same-named tag with a different value from
two different sources remains independently matchable from both
(tags@v1#tags-001, tags@v1#tags-002). This computation is exposed only
through private helpers inside `ledgerkit/tags.py`
(`_inherited_account_tags`, `_effective_tags`, and others) — there is no
public function to call this directly; it is reached only via
`ledgerkit.query`'s `tag:` term.

One exception: `journal.accounts(query=...)`'s own `tag:` matching uses a
narrower view — only the transaction's own tags and the account's inherited
tags, excluding the posting's own tags and any commodity-propagated tags
(tags@v1#tags-003) — this specific narrowing is `ledgerkit.reports.accounts`
only; `balance()`/`register()`/`stats()` all see the full four-source union.

---

## Filtering with Query

`balance()`, `register()`, and `stats()` accept an optional `query=`
parameter that controls which transactions and postings are included.
(`accounts()` has no `query=` parameter.)

```python
import ledgerkit
from ledgerkit import Query
import datetime

journal = ledgerkit.load("myfile.journal")

# Show only expense account balances
balances = journal.balance(query=Query(account="expenses"))

# Show balances for the current year only
balances = journal.balance(query=Query(
    date_from=datetime.date(2024, 1, 1),
    date_to=datetime.date(2024, 12, 31),
))

# Combine filters: food expenses in Q1
rows = journal.register(query=Query(
    account="expenses:food",
    date_from=datetime.date(2024, 1, 1),
    date_to=datetime.date(2024, 3, 31),
))

# Top-level account balances only (depth rollup)
top_level = journal.balance(query=Query(depth=1))
# → {"assets": {"£": Decimal("9641")}, "expenses": {"£": Decimal("1359")}, ...}
```

`Query` fields at a glance:

| Field | Type | Effect |
|---|---|---|
| `account` | `str \| None` | Include only postings whose account matches (substring or regex) |
| `not_account` | `str \| None` | Exclude postings whose account matches |
| `payee` | `str \| None` | Include only transactions whose description matches |
| `date_from` | `date \| None` | Include only transactions on or after this date |
| `date_to` | `date \| None` | Include only transactions on or before this date |
| `depth` | `int \| None` | Roll up/clip account names to this depth for `balance()` and `register()` — a display-only truncation+aggregation, never an exclusion (matching hledger's own `depth:`/`--depth`; corrected in Stage C Phase 5 — `register()` previously excluded deeper postings entirely, a pre-existing bug). `Journal.accounts()` itself takes no `query=` parameter at all (it lists every account name unconditionally) — the same depth-rollup behaviour for accounts listing is reachable only through `ledgerkit.reports.accounts(journal, query=...)`, the module-level function, not the `Journal.accounts()` method |

**Pattern matching (breaking change, Stage C Phase 8):** `account`,
`not_account`, and `payee` values are compiled as a case-insensitive,
infix (`re.search`-style) regex against the same `HledgerRegex`-compatible
subset the CLI's `-q "acct:..."`/`-q "desc:..."` terms use — a plain
string like `"expenses"` behaves exactly as a substring check would, but a
handful of constructs Python's `re` supports are **rejected** with
`QueryParseError` because real hledger's regex engine doesn't have them
(or interprets the same text differently): Perl-style shorthand classes
(`\d`, `\w`, `\s`), lookaround and other `(?...)` constructs, backreferences
(`\1`), GNU word-boundary anchors (`\<`/`\>`), POSIX named classes
(`[[:alpha:]]`), and lazy quantifiers (`*?`, `+?`, `??`). **An empty string
(`Query(account="")`) now raises too**, rather than matching every
posting as it previously did — use a pattern that actually matches
everything (e.g. `".*"`) if that's genuinely what you want
(query-engine@v1#query-engine-013). **A pattern containing an unescaped
`|` with an empty branch on either side** (e.g. `"a|"`, `"|a"`, `"(|)"`,
`"a||b"`) is **also rejected**, matching real hledger's own regex-engine
parse-time rejection of the same family — `"()"`, `"(a)"`, `"a|b"`,
`"(a|b)"`, and anchor-only branches like `"^|a"` all remain accepted
(query-engine@v1#query-engine-013; independently confirmed against the
pinned hledger 1.52.4 binary,
`dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml`,
`status: verified`). This applies identically to
`ReportSection.accounts`/`.exclude` (used with
`balance_from_spec`/`ReportSpec`, below). See `dev-docs/
hledger-compatibility.md`'s Query Language section for the full construct
list and rationale; this is a disclosed, intentional change made while
ledgerkit is still pre-`1.0.0`.

---

## Custom Report Layouts with ReportSpec

`ReportSpec` and `ReportSection` let you define structured, named reports with
multiple account groups, sign control, and depth overrides. **This part of
the API is Python-only**: `balance_from_spec` is reachable from
`ledgerkit.balance_from_spec`/`ledgerkit.ReportSpec`/`ledgerkit.ReportSection`,
but none of the CLI's subcommands (`balance`, `register`, `accounts`,
`print`, `stats`, `check`) ever invoke it — there is no CLI equivalent
(reports-cli@v1#reports-cli-013).

```python
import ledgerkit
from ledgerkit import Query, ReportSpec, ReportSection, balance_from_spec
import datetime

journal = ledgerkit.load("myfile.journal")

# Build an income statement spec
spec = ReportSpec(
    name="Income Statement",
    sections=(
        ReportSection(
            "Income",
            accounts=("income",),
            invert=True,   # income carries negative balances; invert shows as positive
        ),
        ReportSection(
            "Expenses",
            accounts=("expenses",),
            exclude=("expenses:transfers",),  # skip inter-account transfers
        ),
    ),
)

# Run the report (optionally filtered to a date range)
results = balance_from_spec(
    journal,
    spec,
    query=Query(
        date_from=datetime.date(2024, 1, 1),
        date_to=datetime.date(2024, 12, 31),
    ),
)

for section_result in results:
    print(f"\n{section_result.section.name}")
    for account, balance in sorted(section_result.rows.items()):
        print(f"  {account:<40}  {balance:>12}")
    print(f"  {'Total ' + section_result.section.name:<40}  {section_result.subtotal:>12}")
```

`balance_from_spec` returns one `ReportSectionResult` per section:

```python
@dataclass
class ReportSectionResult:
    section:  ReportSection          # the spec section that produced this result
    rows:     dict[str, Decimal]     # account → net balance (after invert)
    subtotal: Decimal                # sum of all rows (after invert)
```

> **Note:** Report specs are currently constructed programmatically. Journal-file
> comment-directive syntax (`; report` / `; end report`) is on the roadmap but
> not yet supported.

---

## Commodity Display Style

ledgerkit infers a display style for each commodity from the first amount it
encounters in the journal. The style captures symbol position, spacing, decimal
mark, digit-group separator, and precision.

```python
styles = journal.commodity_styles   # dict[str, CommodityStyle]
style  = styles.get("£")

if style:
    print(style.commodity)       # "£"
    print(style.prefix)          # True  (symbol before number)
    print(style.space)           # False (no space between symbol and number)
    print(style.decimal_mark)    # "."
    print(style.group_separator) # ","
    print(style.precision)       # 2
    print(style.format(Decimal("1234.56")))  # "£1,234.56"
```

### Inferring a style manually

```python
from ledgerkit.commodity_style import CommodityStyle

style = CommodityStyle.infer("EUR", "1.234,56 EUR")
# → CommodityStyle(commodity="EUR", prefix=False, space=True,
#                  decimal_mark=",", group_separator=".", precision=2)
```

### Parsing a `-c` override string

```python
style = CommodityStyle.parse_style_override("$1,000.00")
# → CommodityStyle(commodity="$", prefix=True, ...)

style = CommodityStyle.parse_style_override("1.000,00 EUR")
# → CommodityStyle(commodity="EUR", prefix=False, decimal_mark=",", ...)
```

An override constructed this way only affects the formatting of the one
commodity symbol it names — it never changes any other commodity's inferred
style, even within the same report run
(commodity-styling@v1#commodity-styling-006).

---

## Validating Transactions

`ledgerkit.checks` exposes both whole-journal validation and a single-
transaction check suitable for editor-style live validation.

```python
from ledgerkit import check_transaction_autobalanced

errors = check_transaction_autobalanced(txn)  # list[CheckError]; never raises
```

Whole-journal entry points:

```python
from ledgerkit.checks import run_basic_checks, run_strict_checks, run_checks

run_basic_checks(journal, skip=None)                  # parseable + autobalanced + assertions
run_strict_checks(journal, skip=None)                 # basic tier, plus accounts + commodities
run_checks(journal, names=None, strict=False, skip=None)  # the general entry point
```

All return `list[CheckError]` (`check_name: str`, `message: str`,
`line_number: int | None`). `run_checks` validates `names` against its
internal check registry up front, raising `ValueError` for an unrecognised
name, then runs the basic tier (minus `skip`), the strict tier
unconditionally if `strict=True`, then any remaining named checks not
already covered by a prior tier.

**A documented caveat on `skip`/`names`/`strict` interaction**: the
"already covered by a prior tier" test inside `run_checks` is a *static*
union of tier name sets, not a record of what actually executed. Two
confirmed, reproducible consequences follow
(checks@v1#checks-008 — independently confirmed by direct execution and
reviewed; a model-blind implementation reconstruction of this module
corroborated the coarse-grained dedup behaviour but did not independently
re-test these two specific interactions):

1. A basic-tier (or, under `strict=True`, strict-tier) check name that is
   both suppressed via `skip` **and** explicitly re-requested via `names`
   executes **zero** times, not once.
2. `skip` is never consulted by `run_checks`'s own strict-tier branch, so a
   name present in both `skip` and the strict tier still runs whenever
   `strict=True`.

Whether either behaviour is intentional design or an oversight is not
resolved as of this writing. `run_strict_checks` has a related, narrower
asymmetry of its own: its `skip` parameter only ever reaches its internal
basic-tier call — the strict-tier names it appends afterward are never
filtered by `skip` at all. (This specific claim about `run_strict_checks`
itself comes from an independent model-blind code reconstruction rather
than a directly reviewed clean-room assertion, so treat it as well
evidenced but not doubly corroborated the way the `run_checks` findings
above are.)

---

## Serializing Transactions

`ledgerkit.writer` turns `Transaction` objects back into journal-format
text:

```python
from ledgerkit import transaction_to_text, journal_to_text

text = transaction_to_text(txn)        # a single transaction
text = journal_to_text(journal)        # every transaction, blank-line separated
```

`transaction_to_text` is guaranteed to round-trip through `parse_string()`
to an equivalent `Transaction` for date, flag, description, postings,
amounts, and comments (`source_span`/`raw_text` are excluded from that
guarantee) — **but not** for `Transaction.date2` (secondary date),
`Posting.cost_raw` (cost annotation), or `Posting.balance_assertion`:
none of these three are serialised at all, so parsing the output back
silently drops them (confirmed empirically — a posting written as
`assets:cash  $10 = $10` loses its `= $10` assertion entirely on
round-trip, not merely its formatting). Tags survive only because
they live inside the preserved inline-comment text and are re-derived
on reparse, not because they are serialised as a distinct field. A
caller that needs secondary dates, costs, or balance assertions to
survive an edit-and-rewrite cycle must not rely on this function for
that purpose. Amount columns are right-aligned to a shared column computed
from the widest account name among postings with an explicit amount, plus
a minimum two-space gap; an elided posting is printed as a bare indented
account name (reports-cli@v1#reports-cli-014).

`journal_to_text` does **not** serialise directives (`account`,
`commodity`, `payee`, `P`) — a caller needing full round-trip fidelity for
directive content should work with the raw source file rather than
re-serialising the `Journal` (reports-cli@v1#reports-cli-014).

---

## Editing Journals with `EditorDocument`

`ledgerkit.EditorDocument` is an in-memory, span-tracked representation of
one journal file, intended for TUI/editor frontends — its own module
docstring states it is "not imported by any core module"
(editor-surface@v1#editor-surface-005).

```python
from ledgerkit import EditorDocument

doc = EditorDocument("myfile.journal")
doc.add_transaction(new_txn)
doc.update_transaction(original_txn, updated_txn)
doc.delete_transaction(old_txn)
doc.save()
doc.reload()
errors = doc.validate_transaction(txn)   # list[CheckError]; runs autobalanced only
```

`doc.dirty` is `True` once any mutation method has run since the last
`save()`/load. `__init__` loads the journal via `parse_string()` directly
— **not** `loader.load_journal()` — so `include` directives in the edited
file are silently ignored; use `loader.load_journal()` when full include
support is required (editor-surface@v1#editor-surface-002).
`update_transaction`/`delete_transaction` both require the given
transaction to already carry a `source_span`
(editor-surface@v1#editor-surface-003).

`EditorDocument` is implemented and unit-tested inside ledgerkit itself,
but as of this clean-room evidence pass, the one real external TUI
frontend project that depends on ledgerkit does not import or instantiate
it anywhere in its own source or test code — it uses `parse_string_lenient`,
`load`, `transaction_to_text`, `journal_to_text`, and `Query` directly
instead (editor-surface@v1#editor-surface-007,
editor-surface@v1#editor-surface-009). This is a fact about current
external adoption, not a limitation of `EditorDocument` itself, which
remains fully functional and tested within ledgerkit's own test suite.

---

## DataFrame Export (optional pandas)

Install the pandas extra first:

```bash
pip install ledgerkit[pandas]
```

### Journal-level export

```python
df = journal.to_dataframe()
# Columns: date, description, cleared, pending, account,
#          amount (Decimal), commodity, amount_formatted
```

Apply a `Query` to pre-filter:

```python
from ledgerkit import Query
df = journal.to_dataframe(query=Query(account="expenses"))
```

### Report-object export

All report return types expose `to_dataframe()`:

```python
# Balance: one row per (account, commodity) pair
balance_df  = journal.balance().to_dataframe()

# Register: one row per posting
register_df = journal.register().to_dataframe()

# Accounts: single-column DataFrame
accounts_df = journal.accounts().to_dataframe()

# ReportSectionResult: rows + subtotal
from ledgerkit import ReportSpec, ReportSection, balance_from_spec
spec = ReportSpec(name="Expenses",
                  sections=(ReportSection("Expenses", accounts=("expenses",)),))
results = balance_from_spec(journal, spec)
section_df = results[0].to_dataframe()
# Includes a final "Total Expenses" row with the section subtotal
```

`ReportSectionResult.to_dataframe()` has a known single-commodity
limitation: it picks one commodity — taken from an arbitrary/first key of
the journal's commodity-styles map, not a per-row lookup — and applies
that one style to every row, regardless of which commodity each row's
value actually originated in. Multi-commodity support for spec-based
reports is deferred (commodity-styling@v1#commodity-styling-008).

### Result wrappers (transparent)

`journal.balance()`, `journal.register()`, and `journal.accounts()` return
thin wrapper objects (`BalanceResult`, `RegisterResult`, `AccountsResult`)
that behave exactly like the underlying `dict`/`list` but also carry
`to_dataframe()`. Existing code that treats these return values as plain
dicts or lists continues to work without modification.

---

## Error Handling

```python
from ledgerkit.parser import ParseError

try:
    journal = ledgerkit.load("myfile.journal")
except FileNotFoundError:
    print("File not found")
except ParseError as e:
    print(f"Parse error on line {e.line_number}: {e}")
```

### Parse warnings

Non-fatal conditions (such as periodic or auto-posting rule blocks that
ledgerkit skips) are surfaced as `ParseWarning` objects rather than exceptions:

```python
from ledgerkit.parser import parse_string_lenient

journal, warnings = parse_string_lenient(text)
for w in warnings:
    print(f"Warning on line {w.line_number}: {w.message}")
```

**`parse_string_lenient`'s "never raises" guarantee is not fully
exhaustive as currently implemented.** A malformed, non-indented
`commodity` directive (empty body, unterminated quoted symbol, or an
otherwise unparseable body) raises `ParseError` unconditionally, uncaught,
even in lenient mode. An independent, model-blind reconstruction of this
module additionally found a second, differently-typed exception: an
`alias` directive whose pattern compiles but whose replacement contains an
out-of-range backreference escapes as an uncaught `re.PatternError`, not
even a `ParseError`. Treat "lenient mode never raises" as an incomplete
guarantee with at least two known exceptions, not a closed set
(journal-parsing@v1#journal-parsing-008).

### Known parsing limitations relevant to API callers

- hledger's balance-assignment-elision syntax (an elided posting amount
  combined with a balance assertion, written as `account  = AMOUNT` with
  no separate amount before the `=`) is not implemented. For a
  prefix-commodity amount this currently fails cleanly with `ParseError:
  invalid amount: '= $100'`. For a suffix-commodity amount under
  comma-decimal mode, the same unimplemented syntax does **not** fail at
  all — it silently produces a wrong `Amount` (the literal `=` character
  is absorbed as if it were a currency symbol) with the balance assertion
  silently dropped, and no error or warning
  (journal-parsing@v1#journal-parsing-009).
- A non-indented `account`/`commodity`/`payee`/`tag` directive appearing
  while a transaction block is still open silently discards every
  subsequent posting line of that still-open block, with no error and no
  warning (journal-parsing@v1#journal-parsing-007).

---

## Example: Iterate Transactions

```python
import ledgerkit

journal = ledgerkit.load("myfile.journal")

for txn in journal.transactions:
    status = "*" if txn.cleared else ("!" if txn.pending else " ")
    print(f"{txn.date} {status} {txn.description}")
    for posting in txn.postings:
        if posting.amount:
            print(f"    {posting.account}  {posting.amount.commodity}{posting.amount.quantity}")
        else:
            print(f"    {posting.account}")
    print()
```

---

## Evidence basis

Citations above (`<topic>@v1#<id>`) reference the Plan 29 clean-room
snapshot topics at version 1: `journal-parsing`, `commodity-styling`,
`query-engine`, `tags`, `reports-cli`, `checks`, `loader`,
`editor-surface` (`dev-docs/clean-room/snapshots/`,
`dev-docs/clean-room/assertions/`). See
`dev-docs/clean-room/legacy-reconciliation/python-api-and-api-spec.md`
for the full reconciliation report this revision was produced from.

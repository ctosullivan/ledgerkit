---
role: implementation-reconstructor
topic: journal-parsing
dispatch-id: plan29-phase-implrecon-journal-parsing-20261003T005613+0800
date: 2026-10-03
---

# As-Built Reconstruction: journal-parsing

Scope: `ledgerkit/parser.py`, `ledgerkit/models.py`, `tests/test_parser/test_parser.py`,
`tests/test_directives/test_directives.py`, and live execution of
`ledgerkit.parser.parse_string` / `parse_string_lenient`. No assertion, snapshot,
legacy doc, or other `ledgerkit/*.py`/`tests/*` file was read to produce this report.

## 1. Structure

`ledgerkit/parser.py` (1721 lines) is a single module with no sub-files. Internally it
divides into:

- A mutable `_ParseContext` dataclass (`default_year`, `decimal_mark`,
  `default_commodity`, `account_prefix`) threaded through amount/posting parsing —
  the only cross-cutting state not held in the main loop's local variables.
- A block of module-level compiled regexes (`_TWO_SPACE_SEP`,
  `_TWO_SPACE_SEMICOLON_COMMENT`, `_TXN_HEADER`, `_SIMPLE_DATE`, `_AMOUNT`,
  `_AMOUNT_COMMA`, `_LOT_ANNOTATION_RE`, `_SPACE_DIGIT_GROUP_RE`,
  `_QUOTED_SUFFIX_RE`, `_TRAILING_QUOTED_COMMODITY_RE`, `_COMMODITY_AMOUNT`,
  `_P_DIRECTIVE`, `_ALIAS_DIRECTIVE`, `_END_ALIASES`, `_ASSERTION_MARKER_RE`), each
  with an adjacent purpose/group/edge-case comment per the project's regex
  documentation convention.
- `ParseError(ValueError)` / `ParseWarning(ParseError)` exception types, the latter
  used only as a non-fatal advisory collected in lenient mode's `errors_out` list.
- Private helpers: `_parse_simple_date`, `_parse_txn_header`,
  `_strip_cost_annotation`, `_strip_lot_annotations`, `_normalise_space_separators`,
  `_parse_amount`, `_strip_directive_comment`, `_extract_commodity_symbol`,
  `_parse_posting`, `_parse_alias_body`, `_apply_aliases`, `_flush_txn`,
  `_apply_posting_date_override_tags`, `_try_set_date_tag`.
- One shared engine, `_parse_string_impl`, a single `for lineno, raw in
  enumerate(all_lines, ...)` state-machine loop (~700 lines) that both public
  entry points call with a different `errors_out` value.
- Public API: `resolve_elision`, `parse_string`, `parse_string_lenient`.

`ledgerkit/models.py` (535 lines) holds plain dataclasses only (`Amount`,
`BalanceAssertion`, `SourceSpan`, `Posting`, `Transaction`, `PriceDirective`), plus
report-shaped dataclasses (`Query`, `RegisterRow`, `BalanceRow`, `ReportSection`,
`ReportSpec`, `ReportSectionResult`) and the `Journal` container class, whose
`balance`/`register`/`accounts`/`stats`/`to_dataframe`/`commodity_styles` methods
lazy-import `ledgerkit.reports`, `ledgerkit.query.*`, `ledgerkit.commodity_style`,
and `ledgerkit._pandas_compat` — none of which are in scope here and were not read.
The module docstring states "No parsing or reporting logic lives here," and that
holds: `models.py` has zero imports from `parser.py` and no behaviour relevant to
parsing itself beyond the dataclass shapes the parser populates.

## 2. Public surface

Confirmed by reading the actual signatures (no CLI surface exists for this module;
it is a pure library):

- `parse_string(text: str, default_year: int | None = None, source_file: str =
  "(string)") -> Journal` — raises `ParseError` on the first malformed line;
  `default_year` defaults to `datetime.date.today().year` when `None`.
- `parse_string_lenient(text: str, default_year: int | None = None, source_file:
  str = "(string)") -> tuple[Journal, list[ParseError]]` — documented as never
  raising; collects `ParseError`/`ParseWarning` instances and discards the
  malformed transaction, resuming at the next blank line or transaction header.
- `resolve_elision(txn: Transaction) -> list[Posting]` — pure function, not wired
  into `_parse_string_impl` itself (elided amounts are left as `amount=None` on the
  `Posting` by the parser; resolution is an opt-in post-processing step a caller
  invokes separately).
- `ParseError(ValueError)` and `ParseWarning(ParseError)` — both importable, both
  carry an optional `line_number` attribute folded into the message string by
  `__init__`.

Everything else (`_ParseContext`, `_parse_txn_header`, `_parse_amount`,
`_parse_posting`, `_parse_alias_body`, `_apply_aliases`, `_flush_txn`,
`_extract_commodity_symbol`, `_try_set_date_tag`,
`_apply_posting_date_override_tags`, `_parse_string_impl`, and all module-level
regexes) is underscore-prefixed/private.

## 3. Data model

From `models.py`, read directly:

- `Amount(quantity: Decimal, commodity: str, raw: Optional[str] = None)` — `raw`
  excluded from `repr`/`__eq__` (`compare=False`), so two `Amount`s with the same
  quantity/commodity are equal regardless of how they were originally written.
- `BalanceAssertion(amount: Amount, inclusive: bool = False, sole_commodity: bool
  = False)` — covers all four hledger assertion markers (`=`, `==`, `=*`, `==*`)
  as two independent booleans.
- `SourceSpan(file: str, start_line: int, end_line: int)` — both line numbers
  1-indexed and inclusive.
- `Posting(account: str, amount: Amount | None = None, balance_assertion:
  BalanceAssertion | None = None, cost_raw: Optional[str] = None, source_line:
  int | None = None, inferred: bool = False, inline_comment: str | None = None,
  tags: list[tuple[str, str]] = [], date_override: Optional[date] = None,
  date2_override: Optional[date] = None)`. `inline_comment` is
  `compare=False`/`repr=False`; `date_override`/`date2_override` are deliberately
  left in equality comparison (default `compare=True`) per an inline comment
  explaining they change parsing-visible state, not just provenance.
- `Transaction(date: date, description: str, date2: Optional[date] = None,
  postings: list[Posting] = [], cleared: bool = False, pending: bool = False,
  code: str = "", comment: str = "", source_line: int | None = None, source_span:
  SourceSpan | None = None, raw_text: str | None = None, inline_comment: str |
  None = None, tags: list[tuple[str, str]] = [])`. There is deliberately no
  `date_override` field at the transaction level — a code comment explains a
  `date`/`date2` tag inside a transaction-level comment has no override effect in
  hledger, only inside a posting's own comment.
- `PriceDirective(date: date, commodity: str, price: Amount)`.
- `Journal(transactions: list[Transaction] = [], prices: list[PriceDirective] =
  [], declared_accounts: list[str] = [], declared_commodities: list[str] = [],
  declared_payees: list[str] = [], declared_tags: list[str] = [],
  declared_account_tags: dict[str, list[tuple[str, str]]] = {},
  declared_commodity_tags: dict[str, list[tuple[str, str]]] = {}, source_file:
  str | None = None, included_files: int = 0, _commodity_directive_raws: dict =
  {})`. This is exactly the shape `_parse_string_impl` builds and returns at the
  end of parsing; the report-method bodies on `Journal` (`balance`, `register`,
  `accounts`, `stats`, `to_dataframe`, `commodity_styles`) are out of scope
  (they delegate into `ledgerkit.reports`/`ledgerkit.query.*`, not read here) but
  their presence on the same dataclass as the parser's output was confirmed by
  direct inspection.

## 4. Dependencies

`parser.py` imports only: `datetime`, `re`, `dataclasses.dataclass`,
`decimal.{Decimal, InvalidOperation}`, `typing.Optional` (all standard library),
plus two in-project imports: `ledgerkit.models` (the dataclasses it builds) and
`ledgerkit.tags.parse_tags` (used in `_flush_txn` and in the account/commodity
directive same-line/follow-on tag-scanning branches — `tags.py` itself is out of
scope and was not read; its behaviour is inferred here only from how `parser.py`
calls it and from comments in `parser.py` that reference it, e.g. "see
ledgerkit/tags.py"). `models.py` imports only `datetime`, `dataclasses`,
`decimal.Decimal`, `typing`, and (under `TYPE_CHECKING` only) `ledgerkit.reports`
for the `JournalStats` type hint — no runtime dependency on `reports.py` from
`models.py`'s parsing-relevant surface. No third-party imports in either file,
consistent with the no-third-party-in-core-modules convention visible in the code
itself (CLAUDE.md's statement of this rule was not consulted; this is read off the
import lines).

## 5. Runtime behaviour (traced and live-executed)

The engine `_parse_string_impl` is one pass over `text.splitlines()` with a large
ordered if/elif-style chain per line, re-evaluated in this order every iteration:
block-comment mode → lenient skip-until-blank mode → blank line → comment-only
line (top-level vs. indented follow-on) → `~` periodic-rule header → `=`
auto-posting-rule header → transaction header (date-shaped line) → `comment`
block start → subdirective-continuation lines → `account` → `commodity` →
`payee` → `tag` → `decimal-mark` → `P` → `alias` → `end aliases` → `Y` → `D` →
`apply account` / `end apply account` → posting line → (fallback) silently
skipped. Each non-indented directive recognised earlier in the chain `continue`s
before reaching the posting-line branch.

Confirmed by direct execution:

- A `P` directive encountered while a transaction block is open does **not**
  close the block: `2024-01-01 Test\n    a  $1\nP 2024-01-01 AAPL $100\n    b
  -$1\n` parses to one transaction with both postings `a` and `b`, plus one
  separate `PriceDirective`. This matches the in-code comment's claim.
- `resolve_elision` is confirmed to be a pure post-processing function never
  called from `_parse_string_impl` — parsed `Posting.amount` stays `None` for an
  elided posting; a caller must invoke `resolve_elision` separately to get the
  inferred `Amount`.
- `parse_string_lenient` genuinely "never raises" for the five adversarial inputs
  its own test (`test_lenient_never_raises`) exercises (garbage text, bad amount
  tokens, NUL/invalid bytes, an invalid calendar date, and a bare indented line)
  — reproduced live, all five return `(journal, errors)` without raising.
- However, "never raises" does **not** hold universally — see §7, confirmed by
  constructing inputs the project's own tests do not cover.

## 6. Tests (read directly, not inferred from names)

`tests/test_parser/test_parser.py` (1639 lines, ~140 test methods) and
`tests/test_directives/test_directives.py` (672 lines, ~95 test methods) were
read in full. Representative findings:

- `TestResolveElision` builds `Transaction`/`Posting` objects directly (not via
  `parse_string`) and asserts `resolve_elision`'s 0/1/2+-elided-posting behaviour,
  multi-commodity fan-out (sorted by commodity symbol), `inferred=True` flagging,
  and that a 2-elided-posting transaction is returned unchanged (no error raised
  by `resolve_elision` itself — that error belongs to the parser's own at-most-one
  check, tested separately in `TestTwoElidedAmounts`/
  `test_multiple_elided_in_one_txn_discarded`).
- `TestParseStringLenient.test_lenient_never_raises` is the project's own explicit
  "never raises" guarantee test, but it only tries five generic-garbage inputs —
  it does not exercise any specific directive's error path (no malformed
  `commodity`/`alias` body is in its input list).
- `TestCommentSpec` (T/B/I/F/S-series) is an extensive, explicitly-labelled suite
  asserting the exact column-0-vs-indented comment-attribution rules described in
  the main loop's own comments (e.g. `test_T05_hash_between_txns_no_blank_line`
  confirms a column-0 `#` with no blank line does not bleed into the previous
  transaction's last posting's `inline_comment`).
  `test_F05_indented_bare_semicolon_gives_none` confirms an empty `;` sets
  `inline_comment` to `None`, not `""`.
- `TestPostingDateOverrideTags` reads real posting-comment tag text (`;
  date:2024-01-15`) and asserts `Posting.date_override`; it separately asserts
  (`test_transaction_level_date_tag_has_no_override_effect`) that the same tag
  name at transaction level has no override effect, matching the `models.py`
  comment's claim.
- `TestAliasDirective` covers basic exact/prefix aliases, regex aliases with
  backreferences, LIFO multi-alias ordering, `end aliases`, and
  `test_invalid_regex_alias_raises` — but only via `parse_string` (strict mode),
  and only for an invalid *pattern* (`/[invalid/`), never an invalid *replacement*
  backreference, and never under `parse_string_lenient`.
- `TestCommodityDirective`/`TestCommodityDirectiveTags` cover every documented
  commodity-symbol form (prefix, suffix, bare sigil, bare word, quoted, empty
  quoted, numeric-only) and same-line/follow-on tag capture — all only via
  `parse_string` (strict), never via `parse_string_lenient` with a malformed
  body.
- `TestFixtureLoad.test_comprehensive_fixture_zero_errors` is described as a
  "Milestone 4 gate": loads `tests/fixtures/comprehensive-hledger-test.journal`
  (not read directly — out of my scoped paths) via `parse_string_lenient` and
  asserts zero non-`ParseWarning` errors.
- Full permitted test run: `python -m unittest tests.test_parser.test_parser
  tests.test_directives.test_directives -v` → **233 tests, all pass**, confirming
  the gaps below are genuinely *uncovered* code paths, not failing assertions.

## 7. Limitations / gaps (established by reading + live execution, not asserted)

1. **`parse_string_lenient` does not actually "never raise"; two concrete
   counter-examples, both confirmed live:**
   - A malformed `commodity` directive body reaches `_extract_commodity_symbol`
     directly in the `commodity` directive branch of `_parse_string_impl`, with
     **no surrounding `try`/`except`** (unlike every other directive handler that
     can raise, e.g. `D`, `P`, `Y`, `decimal-mark`, `alias`, all of which check
     `errors_out` before re-raising). An empty body (`"commodity\n"`) or an
     unterminated quoted symbol (`'commodity "AAPL\n'`) raises `ParseError`
     straight out of `parse_string_lenient`, contradicting its own docstring
     ("This function never raises.") and the project's own
     `test_lenient_never_raises` test does not cover this input shape. Reproduced:
     ```
     >>> parse_string_lenient('commodity\n\n2024-01-01 test\n  a  $1\n  b\n')
     ledgerkit.parser.ParseError: commodity directive has no symbol (line 1)
     ```
   - An `alias` directive whose *pattern* compiles but whose *replacement*
     contains an out-of-range backreference (e.g. `alias /(foo)/ = \2`) passes
     `_parse_alias_body`'s own validation (which only calls
     `re.compile(pattern_str, ...)`, never validating the replacement against the
     pattern's group count) and is accepted into the `aliases` list. The error
     only surfaces later, inside `_apply_aliases`'s unconditional `re.sub(old,
     new, account, ...)` call — reached from the posting-line branch (and the
     `account` directive branch) with **no try/except anywhere in the call
     chain**. This raises `re.PatternError` (a `re.error` subclass, not even a
     `ParseError`) straight out of both `parse_string` and `parse_string_lenient`.
     Reproduced:
     ```
     >>> parse_string_lenient('alias /(foo)/ = \\2\n\n2024-01-01 test\n  foo  $1\n  b\n')
     re.PatternError: invalid group reference 2 at position 1
     ```
   Neither case is exercised by any test in the two files read.

2. **A non-indented `account`/`commodity`/`payee`/`tag` directive encountered
   while a transaction block is already open silently discards every subsequent
   posting line of that same still-open block, with no error and no warning.**
   Confirmed live for `account`:
   ```
   >>> parse_string('2024-01-01 Test\n    a  $1\naccount newacct\n    b  -$1\n    c  -$2\n')
   # txns=1, postings=[('a', $1)]   -- 'b' and 'c' vanish entirely
   ```
   Root cause, read directly off the code: unlike the transaction-header, `~`,
   `=`, and `comment` branches — each of which explicitly flushes/appends
   `current_txn` before proceeding — the `account`/`commodity`/`payee`/`tag`
   directive branches do not check whether `current_txn is not None`, and each
   unconditionally sets `in_subdirective = True` on exit. The very next loop
   iteration hits the "Subdirective lines" block near the top of the chain,
   which silently `continue`s past every indented line (`if line[0:1].isspace():
   continue`) until a non-indented, non-blank line is seen — so the still-open
   transaction's own posting lines are consumed as if they were Ledger-style
   subdirective lines under the just-seen directive, not appended to
   `current_txn.postings`, and never produce a `ParseError`. This is a genuine,
   silent-data-loss gap, not merely a cosmetic one; it was not caught by any test
   in the two files read (none construct a directive line strictly between two
   posting lines of one open block). By direct code reading, `commodity`,
   `payee`, and `tag` share the identical structural pattern (same unconditional
   `in_subdirective = True`, no `current_txn` guard), so the same class of bug is
   expected for those three as well, though only `account` was empirically
   reproduced here.

3. **hledger's "balance assignment" syntax (an elided posting amount combined
   with a balance assertion, written as `account  = AMOUNT` with no separate
   posting amount before the `=`) is not implemented, and fails in two different
   ways depending on the commodity form, neither of which is the correct
   semantics:**
   - For a prefix-commodity amount (`a  = $100`), `_parse_amount` raises a clean
     `ParseError: invalid amount: '= $100'` — confirmed live.
   - For a suffix-commodity amount under comma-decimal mode (`a  = 100,00 EUR`),
     the result is **silent corruption, not an error**: the `_ASSERTION_MARKER_RE`
     (which requires `\s+` *before* the marker by design, per its own edge-case
     comment: "a bare = at the start of amount_raw ... this regex will not match
     it") fails to find an assertion marker, so the whole string `"= 100,00 EUR"`
     is handed to `_parse_amount`, whose prefix-commodity-symbol regex group
     happily absorbs the literal `"="` character as if it were a currency symbol
     (nothing in `[^\d,.\s-]*` excludes `=`). Confirmed live: the resulting
     `Posting.amount` is `Amount(quantity=Decimal('100.00'), commodity='=')` and
     `Posting.balance_assertion` is `None` — no error, no warning, just a wrong
     commodity symbol and a silently-dropped assertion. The regex's own comment
     candidly documents that the marker won't match this input shape, but not
     what then actually happens to it.

4. **The periodic-transaction-rule (`~`) and auto-posting-rule (`=` at column 0)
   bodies are explicitly out-of-scope by design, not a bug** — the code comments
   state this directly ("not supported in v1"), a `ParseWarning` is appended in
   lenient mode, and `TestPeriodicRuleSkip`/`TestAutoPostingRuleSkip` assert
   exactly this (rule header recognised, its postings skipped, one
   `ParseWarning`, zero hard errors). This is a disclosed deferral, not a gap.

5. **`_extract_commodity_symbol`'s "cannot parse symbol from" `ParseError`
   branch appears to be dead/unreachable code** given how permissive
   `_COMMODITY_AMOUNT` is — every probe tried, including deliberately
   malformed-looking bodies like `"???"`, matched successfully (`commodity ???`
   → declared commodity `"???"`, no error). This was not proven unreachable in
   general (only probed, not formally), but no input in either test file reaches
   it either, and none could be constructed during this reconstruction.

6. **Lot/cost annotations and quoted-commodity-suffix parsing interact with the
   assertion-marker split only by accident of ordering** — `_parse_posting`
   detects the assertion marker (`_ASSERTION_MARKER_RE`, operating on the raw,
   not-yet-annotation-stripped text) before calling `_parse_amount` on each half
   separately; `_parse_amount` itself strips cost/lot annotations and handles the
   quoted-suffix form independently on each half. This was confirmed to work
   correctly for a quoted-commodity-plus-assertion combination
   (`3 "Frogs" = 30 "Frogs"` parses to posting amount `3 Frogs` / assertion `30
   Frogs`), but the combination is not covered by either test file — this
   reconstruction's own live probe is the only evidence for it.

7. **Deprecation surface is visible only on `Journal`, not in `parser.py`
   itself** — `models.py`'s `Journal.balance`/`.register` methods carry an
   explicit `[Deprecated]` `accounts:` parameter alongside `query:`, with inline
   comments describing a 2026-era design-review bug fix (the `len(accounts) ==
   0` case). This is unrelated to parsing per se (it is report-method dispatch
   logic on the same dataclass the parser returns) but is noted here since it
   lives in the one file (`models.py`) this reconstruction was scoped to read in
   full.

No attempt was made to compare any of the above against any assertion, snapshot,
or prior documentation — none were read, per the write boundary for this role.

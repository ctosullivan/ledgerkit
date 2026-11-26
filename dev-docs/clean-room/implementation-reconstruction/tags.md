---
role: implementation-reconstructor
topic: tags
dispatch-id: plan29-phase-reconstruction-tags-20261003
date: 2026-10-03
---

# As-built reconstruction: `tags` (Ledgerkit's tag model and tag-inheritance/scoping behaviour)

**Evidence basis.** Only the following were read: `ledgerkit/tags.py`,
`ledgerkit/models.py`, `tests/test_tags.py`, plus live execution of
`ledgerkit.tags` functions in a Python REPL against this checkout. No
assertion, snapshot, legacy doc, or other `ledgerkit/*`/`tests/*` file was
read. No breach of the permitted-evidence-paths boundary was encountered —
the three files plus live execution were sufficient to reconstruct this
topic in full.

## 1. Structure

`ledgerkit/tags.py` is a single, small (258-line), self-contained module of
**pure functions** — no file I/O, no mutation of `Journal`/`Transaction`/
`Posting` objects. Its own module docstring states this explicitly and the
code bears it out: every function either returns a new value or reads
already-populated fields off objects passed in; none assigns back to a
mutable argument.

It falls into three groups:

1. **Tag-string parsing** (public): `parse_tags`, and its two private
   helpers `_parse_comment_line_tags`, `_tag_name_before_colon`. Operates
   purely on `str`/`None` — no model types.
2. **Effective-date resolution** (public): `effective_date`,
   `effective_date2`. Takes a `Transaction` and a `Posting`, returns a
   `datetime.date`.
3. **Tag-inheritance / effective-tags computation** (all private, no
   leading-underscore-free names): `_inherited_account_tags`,
   `_posting_commodities`, `_commodity_tags`, `_effective_tags`,
   `_accounts_effective_tags`. These take a `Journal` plus `Transaction`/
   `Posting` and compute derived tag lists on demand — nothing here is
   cached or written back onto the models.

The module's docstring states the parser-module division of labour: the
caller (`parser.py`, not in evidence scope here) calls `parse_tags` after
assembling a transaction's/posting's/account-directive's/commodity-
directive's `inline_comment` text (including any follow-on indented
comment lines), and is responsible for storing the result onto the
relevant model field itself — `tags.py` never touches `parser.py` or any
model field directly except by returning values.

## 2. Public surface

Confirmed by direct reading of the real signatures (not inferred from
names):

```python
def parse_tags(comment: str | None) -> list[tuple[str, str]]
def effective_date(txn: "Transaction", posting: "Posting") -> datetime.date
def effective_date2(txn: "Transaction", posting: "Posting") -> datetime.date
```

Everything else in the module (`_parse_comment_line_tags`,
`_tag_name_before_colon`, `_inherited_account_tags`,
`_posting_commodities`, `_commodity_tags`, `_effective_tags`,
`_accounts_effective_tags`) is underscore-prefixed — i.e. not part of the
module's declared public surface, though `tests/test_tags.py` imports and
exercises all of them directly (see §6).

No CLI flags, classes, or other entry points live in this module. No
argparse/click wiring is present — `tags.py` has no `--help` surface of
its own; it is purely a library module consumed by other parts of the
codebase (per the module docstring, by `parser.py`; per the
`_accounts_effective_tags` docstring, also by `ledgerkit.reports.accounts`
via `ledgerkit.query.eval`'s accounts-mode dispatch — neither of those
call sites is in this dispatch's permitted evidence paths, so the claim
about who calls these could not be independently verified beyond reading
the docstring's own assertion).

## 3. Data model

From `ledgerkit/models.py`, the fields `tags.py` actually reads/writes via
its return values:

- `Posting.tags: list[tuple[str, str]] = field(default_factory=list)` —
  the posting's own literal inline-comment tags.
- `Posting.date_override: Optional[datetime.date] = None` and
  `Posting.date2_override: Optional[datetime.date] = None` — populated
  (per a comment in `models.py`) only when the posting's own comment
  contains a `date`/`date2` tag whose value parses as a date; both are
  dataclass-`compare`d (not excluded), since the code comment states they
  affect the posting's *effective* date, not just its provenance.
- `Transaction.tags: list[tuple[str, str]] = field(default_factory=list)`
  — the transaction's own literal tags. `models.py` has an explicit
  comment noting there is **no** `date_override`-equivalent field on
  `Transaction`: a `date`/`date2` tag at transaction level has no special
  date-overriding effect — it is an ordinary entry in `Transaction.tags`
  only.
- `Journal.declared_account_tags: dict[str, list[tuple[str, str]]]` —
  tags declared directly on an `account` directive, keyed by the *exact*
  declared account name (not inherited).
- `Journal.declared_commodity_tags: dict[str, list[tuple[str, str]]]` —
  tags declared directly on a `commodity` directive, keyed by the exact
  commodity symbol, same shape as `declared_account_tags`.
- `Amount.commodity: str` — read by `_posting_commodities` to resolve
  which commodity-tag entries apply to a posting.

All tag storage, at every level (`Posting.tags`, `Transaction.tags`,
`Journal.declared_account_tags`, `Journal.declared_commodity_tags`), uses
the same representation: an **ordered `list[tuple[str, str]]`**, never a
`dict`. This is load-bearing: `tags.py`'s own docstrings state repeatedly
that a repeated tag name with different values must stay as two separate
entries, not collapse to one key — a `dict`-based model would silently
lose this.

## 4. Dependencies

`tags.py` imports only `datetime` (used for `effective_date`/
`effective_date2`'s return types) and, under `TYPE_CHECKING` only,
`Journal`, `Posting`, `Transaction` from `ledgerkit.models` (so there is no
runtime import cycle — the model types are referenced purely as forward-
reference string annotations, e.g. `account: "Journal"`). No third-party
or other `ledgerkit` module is imported. No file I/O, no logging, no
exceptions are raised anywhere in this module.

`ledgerkit/models.py` is a larger module with data classes for the whole
journal model (`Amount`, `BalanceAssertion`, `SourceSpan`, `Posting`,
`Transaction`, `PriceDirective`, `Query`, `RegisterRow`, `BalanceRow`,
`ReportSection`, `ReportSpec`, `ReportSectionResult`, `Journal`). Its own
report-method wrappers (`Journal.balance`, `.register`, `.accounts`,
`.stats`, `.to_dataframe`) lazily import `ledgerkit.reports`,
`ledgerkit.query.*`, and `ledgerkit._pandas_compat` — none of which are in
this dispatch's permitted evidence paths, so their internals could not be
examined; they are noted here only because `models.py` was in scope and
its import structure is directly observable.

## 5. Runtime behaviour (traced + live-executed)

### 5.1 `parse_tags` / `_parse_comment_line_tags` / `_tag_name_before_colon`

Algorithm, confirmed by reading and by live execution:

1. `parse_tags(None)` / `parse_tags("")` → `[]` immediately (guarded by
   `if not comment`).
2. Otherwise, the comment is split on `"\n"` and each line is scanned
   independently by `_parse_comment_line_tags`, with results concatenated
   in line order.
3. Within one line, `_parse_comment_line_tags` repeatedly finds the next
   `:` from the current scan position (`pos`). The text between `pos` and
   that colon is passed to `_tag_name_before_colon`, which returns the
   **last whitespace-delimited token** of that candidate — but only if
   the candidate's last character is *not* whitespace; if the candidate
   is empty or ends in whitespace, the name is voided (`""`).
4. If the name is voided, scanning resumes right after that colon
   (`pos = colon + 1`) looking for a further colon on the same line — a
   voided candidate does **not** stop scanning the rest of the line.
   Live-confirmed: `parse_tags("a b : c:d")` → `[('c', 'd')]` (the first
   candidate `"a b "` ends in a space → voided; scanning resumes and
   finds `c:d`).
5. If the name is valid, the value is the text from just after the colon
   to the next `,` (or end of line if none), with `.strip()` applied.
   Scanning then resumes after that comma.
6. A tag name may legitimately repeat with different values; results are
   never deduplicated or collapsed into a dict — confirmed by both the
   test suite and by reading the return type (`list`, never built via a
   dict).

Live-executed edge cases beyond what the test file covers, all consistent
with the module's own documented grammar:

- `parse_tags(":novaluebeforecolon")` → `[]` (candidate before the first
  colon is `""`, which is empty → voided; no further colon exists).
- `parse_tags(":x")` → `[]` (same reasoning).
- `parse_tags("日本語:value")` → `[('日本語', 'value')]` — confirms the
  module docstring's claim that tag names have no character-class
  restriction and non-ASCII characters are accepted.
- `parse_tags("a,b,c")` → `[]` (no colon anywhere on the line).
- `parse_tags("tag:value,")` → `[('tag', 'value')]` (a trailing comma with
  nothing after it yields a value of `""`... actually here `rest` after
  the colon is `"value,"`; comma found at index 5, so `rest[:5]` is
  `"value"`, stripped → `"value"` — the trailing comma itself produces no
  second, empty tag because there is no further colon after it).
- `parse_tags("a b : c:d")` → `[('c', 'd')]`, confirming item 4 above.

### 5.2 `effective_date` / `effective_date2`

Pure, branch-only logic, no I/O:

- `effective_date`: returns `posting.date_override` if not `None`, else
  `txn.date`.
- `effective_date2`: a four-level `if`/`return` fallback chain —
  `posting.date2_override` → `txn.date2` → `posting.date_override` (the
  *primary* override reused as a secondary-date fallback) → `txn.date`.
  This reuse-of-primary-as-secondary-fallback step is real code, not just
  a docstring claim: the third `if` branch in the function body literally
  returns `posting.date_override`.

### 5.3 Tag-inheritance / effective-tags functions

- `_inherited_account_tags(journal, account)`: splits `account` on `:`,
  then for `i` from `1` to `len(segments)` builds every progressively
  longer prefix (`"assets"`, `"assets:bank"`, `"assets:bank:savings"`,
  ...) and concatenates `journal.declared_account_tags.get(prefix, [])`
  for each — so an account inherits from itself and every ancestor, in
  least-specific-first order, not deduplicated.
- `_posting_commodities(posting)`: returns `[posting.amount.commodity]`
  if `posting.amount is not None`, else `[]`. Always 0 or 1 elements,
  since `Posting.amount` is a single `Amount`, not a multi-commodity
  structure — the docstring explicitly flags this as a deliberate
  single-item special case of a function shaped to generalize if
  Ledgerkit ever grows multi-commodity postings.
- `_commodity_tags(journal, commodities)`: for each symbol in
  `commodities`, concatenates `journal.declared_commodity_tags.get(symbol,
  [])`.
- `_effective_tags(journal, txn, posting)`: plain concatenation, in this
  exact order — `posting.tags + txn.tags +
  _inherited_account_tags(journal, posting.account) +
  _commodity_tags(journal, _posting_commodities(posting))`. No
  deduplication of any kind, including same-name-different-value tags
  from different sources — confirmed by reading the code (a flat `+` of
  four lists) and by the test
  `test_unions_all_four_sources_with_no_dedup_by_name`, which live-runs to
  `[('rate', '1'), ('rate', '4'), ('rate', '3'), ('rate', '2')]` (posting,
  then txn, then account-inherited, then commodity — four different
  values under the same name, none dropped).
- `_accounts_effective_tags(journal, txn, posting)`: a narrower union —
  only `txn.tags + _inherited_account_tags(journal, posting.account)` —
  deliberately excluding both the posting's own `tags` and any
  commodity-propagated tags. The docstring states this exists to
  replicate a narrower visibility mode used by an `accounts` command/
  report path, but that call site (`ledgerkit.reports.accounts` /
  `ledgerkit.query.eval`) is outside this dispatch's permitted evidence
  paths, so the claim that it is actually wired up that way could not be
  independently confirmed from this evidence alone — only the function's
  own existence and behaviour were confirmed.

## 6. Tests (read directly, not just names)

`tests/test_tags.py` contains 38 test methods across 10 `TestCase`
classes, all passing when run live:

```
$ python -m unittest tests.test_tags -v
...
Ran 38 tests in 0.004s
OK
```

Representative bodies actually read (not just inferred from names):

- `test_space_before_colon_voids_the_tag`: asserts `parse_tags("foo : bar")
  == []` — confirms a space before a colon voids the *entire* candidate,
  producing zero tags on that line (not a tag named `"foo"`, and not a
  second tag found in `" bar"` since no further colon exists there).
- `test_space_before_colon_then_a_real_tag_later`: asserts
  `parse_tags("foo : bar, real:tag") == [("real", "tag")]` — confirms
  scanning resumes after a voided colon rather than abandoning the line.
- `test_comma_is_a_hard_separator_no_escaping`: asserts
  `parse_tags("tag:before,after:stuff") ==
  [("tag", "before"), ("after", "stuff")]` — confirms there is no comma-
  escaping mechanism in a value.
- `test_repeated_tag_name_kept_as_list_not_collapsed`: asserts
  `parse_tags("tag1:value 1, tag1:value 2") ==
  [("tag1", "value 1"), ("tag1", "value 2")]` — confirms the list-of-pairs
  (never dict) representation is load-bearing, not incidental.
- `test_sibling_branch_does_not_inherit` (in
  `TestInheritedAccountTags`): with `declared_account_tags = {"assets":
  [("type","A")], "assets:bank": [("rate","3")]}`, asserts
  `_inherited_account_tags(journal, "assets:savings") == [("type", "A")]`
  — confirms inheritance is strictly by `:`-prefix ancestry, not by any
  notion of "siblingness" or flat membership in `declared_account_tags`.
- `test_unions_all_four_sources_with_no_dedup_by_name` and
  `test_excludes_posting_own_and_commodity_tags` (in
  `TestEffectiveTags` / `TestAccountsEffectiveTags`): directly assert the
  exact ordered list each function returns given identical fixture data,
  which is the clearest primary-evidence confirmation that
  `_effective_tags` includes all four sources un-deduplicated while
  `_accounts_effective_tags` includes only two of the four.
- `TestEffectiveDate2`'s four tests collectively exercise all four
  branches of the fallback chain, including the "own `date_override`
  reused as `date2` fallback" branch specifically
  (`test_own_date_override_reused_as_date2_fallback`).

No test in this file exercises `parser.py`'s own call site, `reports.py`,
or `query/eval.py` — consistent with the module's own stated pure-function
scope; this file tests `tags.py` in isolation only.

## 7. Limitations / gaps (evidence-based, not glossed over)

- **No comma-escaping in tag values.** A value can never contain a
  literal `,` — there is no backslash-escape or quoting mechanism in this
  implementation. The module docstring and `test_comma_is_a_hard_
  separator_no_escaping` both confirm this is a real, permanent
  limitation (attributed to the hledger grammar itself), not an
  oversight to be fixed later.
- **No deduplication anywhere in the tag-aggregation functions** —
  `_effective_tags` and `_accounts_effective_tags` both do plain list
  concatenation. A caller wanting "closest-match wins" semantics would
  get every differently-valued, same-named tag from every source instead;
  the module is explicit that this is deliberate, but it does mean any
  caller must itself decide how to handle a duplicate-name tag list if it
  wants override-style semantics — `tags.py` supplies none.
- **`_accounts_effective_tags`'s actual caller could not be verified**
  within this dispatch's evidence paths — `ledgerkit.reports.accounts`
  and `ledgerkit.query.eval` are outside scope, so the docstring's claim
  about who invokes this function, and under what dispatch condition,
  rests on the docstring's own assertion only, not on a traced call
  chain.
- **`_posting_commodities` is a 0/1-element list by construction**, not a
  general multi-commodity mechanism — `Posting.amount` is a single
  `Amount` field in `models.py`'s current data model (confirmed by
  reading the dataclass), so the "plural, in case of multi-commodity
  postings" framing in the docstring describes a capability the current
  data model does not actually have yet. This is named in the code itself
  as a forward-looking shape, not a present capability.
- **No tag-name character-class validation at all.** Any string not
  containing `:` and not ending in whitespace is accepted as a tag name —
  including punctuation, digits, and non-ASCII characters (live-confirmed
  with `日本語:value`). There is no rejection path, no warning, no `TODO`
  for tightening this; it is simply unconstrained.
- **`parse_tags` has no awareness of comment-marker stripping** (`;`,
  `#`, etc.) — the module docstring states this is intentionally the
  caller's (`parser.py`'s) responsibility, performed before
  `inline_comment` is assembled; `tags.py` itself never sees or strips a
  comment-leader character. This division of responsibility could not be
  independently verified against `parser.py` since that file is outside
  this dispatch's permitted evidence paths — it rests on `tags.py`'s own
  docstring claim only.
- **No handling of malformed/missing `Journal` fields** — every tag
  lookup function (`_inherited_account_tags`, `_commodity_tags`) uses
  `dict.get(key, [])`, so a `Journal` with no `declared_account_tags`/
  `declared_commodity_tags` populated at all behaves correctly (returns
  `[]`), but there is no validation of the dict's own shape — a caller
  that populated `declared_account_tags` with a non-list value for some
  key would cause a `TypeError` on the `.extend()` call rather than any
  clear error; this is an unhandled case, not a documented deferral.

## Summary of files read / commands run

- Read: `ledgerkit/tags.py` (258 lines, full), `ledgerkit/models.py` (535
  lines, full), `tests/test_tags.py` (305 lines, full).
- Ran: `python -m unittest tests.test_tags -v` (38/38 pass) and a set of
  live `python3 -c` invocations of `ledgerkit.tags.parse_tags` with inputs
  not covered by the existing test file, to independently confirm the
  voided-candidate-resumes-scanning behaviour and the no-character-class-
  restriction claim.

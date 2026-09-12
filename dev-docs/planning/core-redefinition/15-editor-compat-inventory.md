# 15. `ledgerkit-editor` import inventory — verified (Stage B Phase 1)

Independent, read-only verification of `06-core-architecture.md` §6.5's
flagged Stage B action item: "before changing anything `Query`-adjacent,
inventory `ledgerkit-editor`'s actual `import ledgerkit` usage by reading
its source directly, not by inference from its README." Performed by
cloning `https://github.com/ctosullivan/ledgerkit-editor` (shallow, at its
`master` HEAD; local `pyproject.toml` pins `ledgerkit==1.0.0.dev1`, its own
`version = "1.2.0"`) into a scratch directory and grepping/reading the
actual source — no code in either repository was changed.

This supersedes `14-human-decision-gates.md` G8's inventory, which was a
useful first pass but not fully accurate — see §15.3 for the specific
corrections.

## 15.1 What `ledgerkit-editor` actually imports and uses at runtime

| Symbol | Where | How |
|---|---|---|
| `ledgerkit.load(path)` | `utils/ledger_io.py: load_journal()` | Direct call, deferred `import ledgerkit` inside the function (avoids startup cost) |
| `ledgerkit.journal_to_text(journal)` | `utils/ledger_io.py: save_journal()`, `widgets/transaction_table.py`, `widgets/view_filter.py` | Direct call |
| `ledgerkit.transaction_to_text(txn)` | `widgets/transaction_table.py` (per-transaction serialisation before re-sort), `widgets/view_filter.py` | Direct call |
| `ledgerkit.parse_string_lenient(text)` | `widgets/transaction_table.py: action_save()`, `widgets/view_filter.py`, `utils/journal_index.py` | Direct call; return value's `(Journal, list[ParseError|ParseWarning])` shape is relied on (branches on `isinstance(err, ParseWarning)`) |
| `ledgerkit.parser.ParseError` / `ParseWarning` | `widgets/transaction_table.py`, `tests/test_comprehensive_hledger.py` | Imported directly for `isinstance` checks and exception handling |
| `ledgerkit.checks.run_basic_checks(journal)` | `widgets/transaction_table.py: action_save()` | Direct call; iterates results for `.message` |
| `ledgerkit.commodity_style.CommodityStyle` | `utils/commodity_format.py` | Runtime import (not just typing) inside functions; used for style inference/formatting |
| `ledgerkit.Query` | `widgets/filter_popup.py` | Constructed directly: `ledgerkit.Query(account=..., payee=..., date_from=..., date_to=...)` — **only these four kwargs used**, as a plain data container. The resulting object is passed to the editor's own `query_match.build_transaction_predicate()`, never to any `ledgerkit` report function (`balance`/`register`/etc.) |
| `ledgerkit.models.{Journal,Transaction,Posting}` | `utils/ledger_io.py`, `utils/commodity_format.py` (both **`TYPE_CHECKING`-only**, no runtime import); `tests/test_query_match.py`, `tests/test_comprehensive_hledger.py` (runtime, test-only) | Type hints in shipped code; real runtime objects only in the test suite |

## 15.2 What it deliberately does *not* import

`utils/query_match.py`'s module docstring is explicit and load-bearing:

> "Deliberately duplicated from `ledgerkit.reports._matches_pattern` and
> `_posting_matches`, which are private (underscore-prefixed, never
> exported from `ledgerkit.__init__`). Per this project's ledgerkit API
> Rule (`CLAUDE.md`), importing private members of a pinned dependency is
> fragile — they can change or disappear on any ledgerkit release with no
> deprecation notice. ... duplicate locally rather than depend on an
> unreleased upstream export."

So `ledgerkit-editor` reimplements hledger's substring/regex matching
convention (`_REGEX_META`, `matches_pattern`) locally instead of importing
`ledgerkit.reports`'s private helpers — and its own test suite
(`tests/test_query_match.py`) deliberately imports the *real*
`ledgerkit.Query`/`Transaction`/`Posting` specifically to catch drift
between the local duplicate and ledgerkit's actual `Query` contract.

`ledgerkit.EditorDocument` is **not used anywhere in the shipped
application code** — see §15.3.

## 15.3 Corrections to `14-human-decision-gates.md` G8's inventory

G8 stated ledgerkit-editor "uses `ledgerkit.Query`, `ledgerkit.EditorDocument`,
`ledgerkit.parse_string_lenient`, `ledgerkit.{models,reports,checks,parser,
commodity_style}`, and `ledgerkit.{load,journal_to_text,transaction_to_text}`
directly." Verified against the actual source, three parts of that need
correcting:

1. **`ledgerkit.EditorDocument` is not actually used.** A repo-wide grep
   for `EditorDocument` finds exactly two hits: a one-line comment in
   `commands/__init__.py` ("reload EditorDocument") and a mention in
   `ledger_io.py`'s module docstring listing it as a "key ledgerkit type
   used here" — but no import, no instantiation, anywhere. `ledger_io.py`'s
   actual `load_journal`/`save_journal` functions call `ledgerkit.load()` /
   `ledgerkit.journal_to_text()` directly instead — a lower-level pair of
   functions, not the `EditorDocument` wrapper. The docstring itself
   appears stale relative to the code it describes; this is
   `ledgerkit-editor`'s own documentation drift, not something Ledgerkit
   Core needs to act on, but it means Ledgerkit Core should **not** treat
   `EditorDocument` as a verified `ledgerkit-editor` dependency going
   forward on the strength of G8's note.
2. **`ledgerkit.reports` is deliberately *not* imported**, in the opposite
   direction G8's phrasing implied — see §15.2. `ledgerkit-editor` treats
   `ledgerkit.reports`'s matching helpers as private and unavailable by
   design, and has its own regression tests specifically to catch drift if
   Ledgerkit Core's matching semantics ever change.
3. **`ledgerkit.models` is a `TYPE_CHECKING`-only import in shipped code**
   (`ledger_io.py`, `commodity_format.py`) — a real dependency at
   type-check time, not a runtime one. It's runtime-imported only inside
   the test suite (`test_query_match.py`, `test_comprehensive_hledger.py`),
   which is a dev-time dependency, not a production one.

`ledgerkit.Query`, `ledgerkit.parse_string_lenient`,
`ledgerkit.checks.run_basic_checks`, `ledgerkit.commodity_style.
CommodityStyle`, `ledgerkit.parser.{ParseError,ParseWarning}`,
`ledgerkit.load`, `ledgerkit.journal_to_text`, and
`ledgerkit.transaction_to_text` were all confirmed accurate — G8 was right
about those.

## 15.4 Implications for Stage B/C

- **§6.5's frozen-v1-API-surface list should read**: `parse_string_lenient`,
  `writer.{transaction_to_text,journal_to_text}`, `checks.run_basic_checks`,
  `commodity_style.CommodityStyle`, `parser.{ParseError,ParseWarning}`,
  `load`, `Query`, and `models.{Journal,Transaction,Posting}` (type-only in
  shipped code, runtime in `ledgerkit-editor`'s own tests). **Not**
  `EditorDocument` — no evidence it's actually depended on by
  `ledgerkit-editor` today, so it doesn't need the same frozen-surface
  guarantee for that consumer's sake (it may still be frozen for other
  reasons, e.g. its own documented API-spec status).
- **The Stage C `Query`-compatibility-shim requirement in
  `07-query-regex.md` is narrower than it might have looked.**
  `ledgerkit-editor`'s entire coupling to `Query` is: construct it with
  exactly `account`, `payee`, `date_from`, `date_to` keyword arguments, and
  read nothing else off it (it's never passed into a `ledgerkit` report
  function — the editor's own `query_match.py` does all the evaluation).
  A future `Query`-as-compatibility-shim-over-the-new-AST only needs to
  preserve that constructor signature and those four field names/types;
  it does not need to preserve any evaluation-time behaviour tied to
  `ledgerkit.reports`'s internals, since `ledgerkit-editor` never touches
  those.
- **No `ledgerkit/` or `tests/` code changed by this phase** — this is a
  read-only inventory feeding Stage B/C design, not an implementation
  step.

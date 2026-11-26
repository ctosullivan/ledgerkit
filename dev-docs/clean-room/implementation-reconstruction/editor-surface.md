---
role: implementation-reconstructor
topic: editor-surface
dispatch-id: plan29-phase-implrecon-editor-surface-20261003T005502+0800
date: 2026-10-03
---

# Implementation Reconstruction: editor-surface

Scope per dispatch: how the external project `ledgerkit-editor` actually
consumes the `ledgerkit` package as a library, reconstructed only from:

- `/home/cormac/projects/ledgerkit/ledgerkit/editor_model.py`
- `/home/cormac/projects/ledgerkit/tests/test_editor_model.py`
- `/tmp/ledgerkit-editor-research-clone-2` (source + test `.py` files and
  `pyproject.toml` only — README/docs/CHANGELOG/AI-README excluded per
  dispatch instructions)

Clone commit verified: `git -C /tmp/ledgerkit-editor-research-clone-2
rev-parse HEAD` returned `b03c203316a9f99593173feaeea7ba7dad91e060`, matching
the commit named in the dispatch. No drift.

No hard-excluded path (assertions/snapshots/implementation-comparison,
dev-docs/planning/, legacy dev-docs or docs `*.md`, knowledge/*.md,
ROADMAP.md, CHANGELOG.md, CONTEXT.md, or the clone's own README/docs/
CHANGELOG/AI-README) was read while producing this report.

## 1. Structure

### 1.1 `ledgerkit/editor_model.py` (the ledgerkit-side surface)

A single module, a single public class: `EditorDocument`. It imports, from
inside the `ledgerkit` package itself:
`ledgerkit.checks.{CheckError, check_transaction_autobalanced}`,
`ledgerkit.models.{Journal, SourceSpan, Transaction}`,
`ledgerkit.parser.parse_string`, `ledgerkit.writer.transaction_to_text`.
Its own module docstring states explicitly: "Not imported by any core
module" and "V1 limitation: include directives in the file are not
processed; the file is parsed as-is with parse_string(). Use
loader.load_journal() when full include support is required."

Responsibilities, read directly from the class body:
- `__init__(path)` — resolves path, reads text, splits into `self.lines`
  (newline-stripped list of str), parses via `parse_string` into
  `self.journal`, sets `dirty=False`.
- `_shift_spans_after(after_line, delta)` — private helper; rewrites every
  transaction's `source_span` (a new `SourceSpan`, not mutated in place)
  when its `start_line` is after a given line, by `delta`.
- `add_transaction(txn)` — serialises `txn` via `transaction_to_text`,
  finds the chronologically-correct insertion point among transactions
  that already have a `source_span`, splices text into `self.lines`,
  assigns a fresh `SourceSpan` to `txn`, shifts all later spans, appends
  `txn` to `self.journal.transactions` and re-sorts that list by
  `(date, source_span.start_line)`. Sets `dirty=True`.
- `update_transaction(original, updated)` — requires `original.source_span`
  (raises `ValueError` otherwise), replaces the exact line range in
  `self.lines`, computes the line-count delta, shifts spans after the
  edited block if non-zero, replaces `original` with `updated` at the
  same list index in `self.journal.transactions` (by `list.index`,
  i.e. identity/equality match on `original`), and sets `updated.source_span`.
- `delete_transaction(txn)` — requires `txn.source_span` (raises
  `ValueError` otherwise), removes the transaction's line range plus one
  trailing blank separator line if present, removes `txn` from
  `self.journal.transactions` (`list.remove`, needs an equal Transaction
  object), shifts later spans back.
- `save()` — writes `"\n".join(self.lines)` to `self.path`, ensuring a
  trailing newline, sets `dirty=False`. No re-parse.
- `reload()` — re-reads the file from disk, fully re-parses it with
  `parse_string`, resets `dirty=False`. This is a full reset, not a diff.
- `validate_transaction(txn)` — delegates to
  `check_transaction_autobalanced(txn)` and returns its `CheckError` list
  (possibly empty); does not raise.

### 1.2 `ledgerkit-editor` clone structure (relevant to this topic)

`src/ledgerkit_editor/` — a Textual TUI application. Key files that touch
`ledgerkit`:
- `app.py` — `LedgerApp`/`main()`/`_parse_args()`; no direct `ledgerkit`
  import, delegates file I/O to `JournalEditor` and `file_resolver`.
- `widgets/transaction_table.py` — `JournalEditor`, the main editing
  widget; this is where load/save/check actually happen (see §5).
- `widgets/view_filter.py` — `ViewFilterMixin`: Ctrl+L (cleared/
  uncleared cycle) and Ctrl+O (criteria filter) view-filtering, both
  reparsing/reserialising via `ledgerkit`.
- `widgets/filter_popup.py` — builds a `ledgerkit.Query` from form fields.
- `utils/ledger_io.py` — thin load/save wrappers plus
  `split_journal_segments`/`split_preamble`/`align_posting_amounts`
  (editor-local text manipulation, not `ledgerkit` calls).
- `utils/commodity_format.py` — wraps `ledgerkit.commodity_style.
  CommodityStyle` to reformat amount tokens in already-serialised text.
- `utils/query_match.py` — a **deliberately duplicated** local
  reimplementation of `ledgerkit.reports._matches_pattern`/
  `_posting_matches` logic (see §4 and §7).
- `utils/journal_index.py` — builds an account/payee autocompletion index
  from a parsed `Journal`.
- `utils/file_resolver.py` — CLI-arg / `$LEDGER_FILE` / `~/.hledger.
  journal` resolution order; no `ledgerkit` import, just a documented
  parallel to "ledgerkit cli.py" behaviour.
- `keybindings/emacs_ledger.py` — stub action methods; one docstring
  mentions `ledgerkit.load(path).declared_accounts` as intended future
  behaviour, but the method body is `# TODO: implement` — no call exists.
- `commands/__init__.py` — `Command`/`CommandHistory` undo/redo
  infrastructure; a `# TODO` comment lists a *planned* "Open file"
  command-palette action as "reload EditorDocument" — not implemented.

## 2. Public surface actually exercised

### 2.1 From `ledgerkit/editor_model.py` itself (ledgerkit's own test suite)

`tests/test_editor_model.py` exercises exactly the `EditorDocument` public
surface listed in §1.1: construction from a fixture path, `.dirty`,
`.journal.transactions`, `.lines`, `source_span` population/correctness,
`raw_text`/`inline_comment` on parsed transactions, `add_transaction`,
`update_transaction`, `delete_transaction`, `save`, `reload`,
`validate_transaction`. All via the real `sample.journal` fixture and real
`ledgerkit.models.{Amount, Posting, Transaction}` / `ledgerkit.checks.
CheckError`.

### 2.2 From the `ledgerkit-editor` clone — every runtime `import
ledgerkit`/`from ledgerkit...` site (unanchored search across the whole
clone, src + tests + conftest)

Running an unanchored `grep -rn "ledgerkit" --include="*.py" .` (then a
second unfiltered pass to be sure nothing was hidden by excluding
`ledgerkit_editor`-named lines) surfaced these real import/call sites:

- `src/ledgerkit_editor/widgets/view_filter.py`:
  - `import ledgerkit` (deferred, function-local) in `_snapshot_journal`,
    `_apply_view_filter`, `_merge_filtered_edits`.
  - Calls used: `ledgerkit.parse_string_lenient(text)` (returns
    `(journal, errors)` tuple), `ledgerkit.transaction_to_text(tx)`,
    `ledgerkit.journal_to_text(journal)`.
- `src/ledgerkit_editor/widgets/transaction_table.py`:
  - `import ledgerkit` (deferred) plus `from ledgerkit.parser import
    ParseWarning` inside `action_save`.
  - Calls used: `ledgerkit.parse_string_lenient(text)`,
    `ledgerkit.transaction_to_text(t)`, `ledgerkit.checks.
    run_basic_checks(journal)` (note: accessed as an attribute of the
    `ledgerkit` package object, not via a separate import statement —
    this only works if `ledgerkit.checks` is reachable as a submodule
    attribute after `import ledgerkit`, i.e. it depends on `ledgerkit/
    __init__.py` either importing `checks` itself or Python's
    already-imported-submodule attribute-caching; this module does not
    `import ledgerkit.checks` explicitly).
- `src/ledgerkit_editor/widgets/filter_popup.py`:
  - `import ledgerkit` (deferred) inside `apply_filter`.
  - Constructs `ledgerkit.Query(account=..., payee=..., date_from=...,
    date_to=...)` — note `not_account`/`depth` are never passed from this
    call site even though `Query` supports them (confirmed via
    `query_match.py` and `test_query_match.py` usage elsewhere).
- `src/ledgerkit_editor/utils/ledger_io.py`:
  - `import ledgerkit` (deferred) separately inside `load_journal` and
    `save_journal`.
  - Calls used: `ledgerkit.load(path)` → `Journal`; `ledgerkit.
    journal_to_text(journal)` → `str`.
  - `TYPE_CHECKING`-only: `from ledgerkit.models import Journal,
    Transaction` (type hints only, no runtime import).
- `src/ledgerkit_editor/utils/journal_index.py`:
  - `import ledgerkit` (deferred) inside `build_journal_index`.
  - Calls used: `ledgerkit.parse_string_lenient(text)`; reads
    `journal.declared_accounts`, `journal.declared_payees`,
    `tx.description`, `posting.account` off the returned `Journal`.
- `src/ledgerkit_editor/utils/commodity_format.py`:
  - `from ledgerkit.commodity_style import CommodityStyle` (deferred,
    function-local) inside `extract_commodity_styles` and inside the
    test file's helper methods.
  - `TYPE_CHECKING`-only: `from ledgerkit.commodity_style import
    CommodityStyle` / `from ledgerkit.models import Journal`.
  - Reads `journal.commodity_styles` (a dict) directly off the `Journal`
    object; calls `CommodityStyle.infer(commodity, raw)` and
    `style.format(qty)`.

Test-side runtime imports (also real, exercising the same API from the
consumer's test suite):
- `tests/test_query_match.py`: `from ledgerkit import Query`;
  `from ledgerkit.models import Posting, Transaction`.
- `tests/test_commodity_format.py`: `import ledgerkit` (both a
  module-level-inside-function form and `__import__("ledgerkit")`);
  `ledgerkit.load(...)`; `ledgerkit.parse_string_lenient(text)`;
  `from ledgerkit.commodity_style import CommodityStyle`.
- `tests/test_comprehensive_hledger.py`: top-level `import ledgerkit`
  (the only genuinely top-of-file, non-deferred import of `ledgerkit`
  found anywhere in the clone) plus `from ledgerkit.parser import
  ParseError, ParseWarning, parse_string_lenient`. Exercises `ledgerkit.
  load()`, `ledgerkit.Journal` (as a type annotation), `Transaction.
  date2`, `Posting.cost_raw`, scientific-notation/space-grouped/quoted-
  commodity amount parsing, `Y`/`D`/`apply account` directives, lot
  annotations, and balance assertions — i.e. this test file is really
  exercising **ledgerkit's own parser**, using the editor repo as the
  test's host, not exercising any `ledgerkit_editor` code at all.

No other `import ledgerkit`/`from ledgerkit` site exists anywhere else in
the clone (confirmed by a second, unfiltered grep over the whole tree).

**`EditorDocument` is never imported or instantiated anywhere in the
clone's actual code or tests.** It appears only in two comments:
a docstring list in `ledger_io.py` ("`ledgerkit.EditorDocument(path)` →
in-memory editable document") and a `# TODO` in `commands/__init__.py`
("reload EditorDocument" as a *planned* command-palette action, not yet
registered). Both are documentation/aspiration, not working code — see
§7 (Limitations).

### 2.3 Declared dependency pin

`pyproject.toml`: `dependencies = ["textual==8.2.5", "ledgerkit==1.0.0.
dev1"]`. This is the one exact version the editor is built and tested
against. Separately, `tests/test_comprehensive_hledger.py`'s own module
docstring says it "Exercises ledgerkit v0.2.0 features" (ParseWarning,
`Transaction.date2`, `Posting.cost_raw`, etc.) — a version string that
does not match the `1.0.0.dev1` pin in `pyproject.toml`. This is a plain
textual discrepancy in the evidence itself (not resolved by anything in
my permitted paths) and should be treated as a fact to flag, not
reconciled by me.

## 3. Data model actually touched by the editor

From the `TYPE_CHECKING`-only and real imports above, the editor's code
only ever touches these `ledgerkit` model surfaces:
- `Journal`: `.transactions`, `.declared_accounts`, `.declared_payees`,
  `.commodity_styles` (dict), `.accounts()` (mentioned only in a
  docstring, not called in working code).
- `Transaction`: `.date`, `.description`, `.postings`, `.cleared`,
  `.date2`, `.source_span` (via `editor_model.py`'s own use, not the
  editor clone's), `.source_span` is read in `ledger_io.split_journal_
  segments` via `getattr(txn, "source_span", None)`.
- `Posting`: `.account`, `.amount`, `.cost_raw`.
- `Amount`: `.quantity`, `.commodity`, `.raw`.
- `Query` (constructed, never subclassed): `account`, `not_account`,
  `payee`, `date_from`, `date_to`, `depth` — all accessed via `getattr`
  in `query_match.py`, so the editor's own code treats `Query` duck-typed
  rather than as a frozen dataclass contract.
- `CommodityStyle`: constructed directly in tests
  (`CommodityStyle(commodity=..., prefix=..., space=..., decimal_mark=...,
  group_separator=..., precision=...)`), and via `CommodityStyle.infer(...)`
  / `.format(...)` in production code.

`editor_model.py`'s own data model (within ledgerkit itself, not the
external consumer) is just `EditorDocument`'s four attributes: `path: str`,
`journal: Journal`, `lines: list[str]`, `dirty: bool`. No dataclass; a
plain class with instance attributes set in `__init__`.

## 4. Dependencies

- `ledgerkit/editor_model.py` depends only on other `ledgerkit` modules
  (`checks`, `models`, `parser`, `writer`) — no third-party or stdlib
  imports beyond `pathlib.Path`.
- The `ledgerkit-editor` clone depends on `textual==8.2.5` (pinned exact)
  and `ledgerkit==1.0.0.dev1` (pinned exact) per `pyproject.toml`; dev
  extras are `pytest`/`pytest-asyncio`. Build backend is `setuptools>=77`
  with `src/`-layout package discovery.
- `utils/query_match.py` explicitly documents *why* it avoids importing
  `ledgerkit.reports._matches_pattern`/`_posting_matches` directly: those
  names are underscore-prefixed/private and "never exported from
  ledgerkit.__init__", so the editor project's own policy ("this
  project's ledgerkit API Rule") is to duplicate private-looking logic
  locally rather than depend on unstable internals — confirmed by reading
  the module docstring and the actual duplicated implementation, not
  inferred from the file name.

## 5. Runtime behaviour (traced through real call chains)

### 5.1 Save (`JournalEditor.action_save`, `transaction_table.py` ~line 320)
1. If a view filter is active, merges visible-text edits back into the
   full in-memory journal first (`ViewFilterMixin._merge_filtered_edits`).
2. Reads the full textarea text, calls `ledgerkit.parse_string_lenient
   (text)` → `(journal, parse_errors)`. Warnings vs hard errors are
   distinguished by `isinstance(err, ParseWarning)` and surfaced as
   Textual notifications (`information` vs `warning` severity);
   **neither blocks the write**.
3. `split_journal_segments(text, journal.transactions)` (editor-local,
   using each transaction's `source_span`) extracts non-transaction
   blocks (directives/comments/blank separators) by original file
   position, to be woven back in after sorting.
4. `extract_commodity_styles(journal)` (editor-local, reads `journal.
   commodity_styles` plus a "prefer richer format" upgrade pass using
   `CommodityStyle.infer`).
5. `journal.transactions.sort(key=lambda t: t.date)` — **mutates the
   `Journal`'s own transaction list in place**, by date only (stable sort
   preserves original relative order for same-date transactions).
6. Serialises each transaction via `ledgerkit.transaction_to_text(t)`,
   interleaves with the preserved non-transaction blocks positionally
   (`preamble + txn0 + sep1 + txn1 + ... + trailer`) — **this reordering
   means a block of directives/comments that was originally positioned
   between two specific transactions can end up adjacent to different
   transactions after a date-sort**, since the non-txn blocks are woven
   back in post-sort slot order, not re-anchored to the transactions they
   originally followed.
7. `apply_commodity_styles` then `align_posting_amounts` are applied to
   the whole reassembled text (editor-local text post-processors, not
   `ledgerkit` calls).
8. The textarea is reloaded with the new text (cursor position
   preserved/clamped), the file is written via `Path.write_text`
   directly (not through any `ledgerkit` save/write API), and
   `ledgerkit.checks.run_basic_checks(journal)` is run against the
   **pre-serialisation** `journal` object for a final notification pass.

**`EditorDocument.save()` is not part of this path at all** — the actual
save pipeline reimplements span-aware block preservation, sorting, and
checks from scratch in the editor rather than using `EditorDocument.add_
transaction`/`update_transaction`/`delete_transaction`/`save()`.

### 5.2 View filtering (Ctrl+L / Ctrl+O, `view_filter.py`)
Entering a filtered view re-parses the current textarea text with
`ledgerkit.parse_string_lenient`, snapshots the journal and its non-
transaction blocks (`split_journal_segments`), then renders only the
transactions matching the combined (AND) predicate — rebuilt through
`ledgerkit.transaction_to_text` per visible transaction, with the same
commodity-format/align post-processing as save. Leaving the filtered view
(or toggling it) first merges any edits made while filtered back into the
full snapshot (by matching visible-slot index to the snapshot's original
transaction list, appending any newly-added transactions, and deleting
any whose visible slot disappeared), then restores/reapplies filtering.
This filter mechanism is entirely independent of `EditorDocument` — it is
its own from-scratch in-memory model built directly on `ledgerkit.parse_
string_lenient`/`journal_to_text`/`transaction_to_text`.

### 5.3 Criteria filter construction (`filter_popup.py` → `query_match.py`)
`FilterPopup.apply_filter` builds a `ledgerkit.Query(account=, payee=,
date_from=, date_to=)` from form fields (an all-empty form posts
`FilterCleared` instead of a no-op "match everything" `Query`, explicitly
to avoid an unwanted reformat/round-trip), then
`query_match.build_transaction_predicate(query)` — the editor's local
reimplementation — is used to build the actual visibility predicate. Any
`re.error` from an invalid regex pattern is raised eagerly at predicate-
build time (validated once, not per-transaction) and caught here for a
user-facing notification.

### 5.4 Autocomplete index (`journal_index.py`)
`build_journal_index(text)` calls `ledgerkit.parse_string_lenient(text)`
inside a bare `try/except Exception`, returning an empty `JournalIndex()`
on **any** exception (not just parse errors) — a deliberately permissive
fallback so a broken-mid-edit journal never raises while the user is
typing.

## 6. Tests — what they actually assert

### 6.1 `tests/test_editor_model.py` (ledgerkit's own suite, 23 test
methods across 6 `TestCase` classes) — confirmed by reading bodies, not
names:
- Load: transaction count (5) from `sample.journal`, `lines` length (23),
  every transaction has a non-`None` `source_span` with the resolved
  absolute file path, exact expected `(start_line, end_line)` per
  transaction (hard-coded against the fixture's literal line layout),
  `raw_text` starts with `str(txn.date)`, and the 5th transaction's
  `inline_comment == "business meeting"`.
- Add: appending a transaction dated after all existing ones increases
  count to 6 and gives it a `source_span.start_line > 23`; the new span's
  line count matches `len(transaction_to_text(txn).splitlines())` exactly;
  inserting mid-journal shifts the previously-last transaction's span
  forward; `lines` grows.
- Update: replacing a transaction's content changes the exact line at
  the old `start_line`; same posting-count update causes **no** shift to
  a later transaction's span; adding a posting (3 lines vs 2) **does**
  shift the next transaction's span forward; the updated transaction's
  own `source_span.start_line` is unchanged (header line position stable).
- Delete: deleting drops the count to 4; deleting the first transaction
  shifts the second transaction's span back by exactly `block_size + 1`
  (the extra 1 being the trailing blank separator); deleting all five
  transactions leaves `len(transactions) == 0`.
- Reload: `reload()` after `add_transaction` resets `dirty` to `False`
  and restores the original 5-transaction count (confirms `reload()`
  discards unsaved in-memory edits, re-reading from disk).
- Save: `save()` writes to disk (verified by reading the file back) and
  clears `dirty`; a save→reload round trip preserves the added
  transaction (6 total) and leaves `dirty=False`.
- Validate: a balanced two-posting transaction returns `[]`; an
  unbalanced one returns exactly one `CheckError` with `check_name ==
  "autobalanced"`; a transaction with one elided (amount-less) posting
  returns `[]` (elision is not flagged as unbalanced).

### 6.2 Clone tests touching `ledgerkit` directly
- `test_query_match.py` — asserts `matches_pattern`/`build_transaction_
  predicate` behaviour using **real** `ledgerkit.Query`/`Transaction`/
  `Posting` objects (not stand-ins), including: substring vs regex-mode
  switch on metacharacter presence, invalid-regex raising, date-range
  inclusive bounds, payee substring/regex, "matches if any posting
  matches" account semantics, `not_account` exclusion, `depth`-limited
  account matching, combined filters, and immediate `re.error` raising
  at predicate-build time for both invalid `account` and `payee` patterns.
- `test_commodity_format.py` — asserts `extract_commodity_styles`/`apply_
  commodity_styles` against a `multicommodity.journal` fixture and
  inline strings: EUR detected as suffix with precision 2 and comma group
  separator; £ and $ detected as prefix; a "prefer richer format" pass
  upgrades a no-comma first-seen style to a comma style when a later
  amount has one; `apply_commodity_styles` reformats prefix/suffix/
  negative amounts, preserves inline comments, preserves/doesn't-add
  trailing newline, applies thousands separators, and specifically
  normalises `£-50.00` (symbol-then-minus) to `-£50.00` (minus-then-
  symbol) because — per an explicit test comment — "ledgerkit parser only
  accepts '-SYMBOL+NUMBER'... causes ParseError on reload" otherwise.
- `test_comprehensive_hledger.py` — asserts a wide swath of **ledgerkit's
  own parser** behaviour (via `ledgerkit.load`/`parse_string_lenient`)
  rather than anything in `ledgerkit_editor`: `ParseWarning` is a
  subclass of `ParseError` and is raised (not a hard error) for `~`
  periodic and `=` auto-posting rules; `Transaction.date2` secondary-date
  parsing; `Posting.cost_raw` for both unit (`@`) and total (`@@`) cost
  annotations (and `None` when absent); scientific notation, space-
  grouped digits, quoted multi-word commodities, and sign-after-prefix-
  symbol (`$-300`) amount parsing; `Y`/`D`/`apply account` directive
  effects; lot annotations (`{...}`, `{{...}}`) stripped from the
  commodity string without populating `cost_raw`; balance assertions
  (`=`, `==`, `==*`) not breaking parsing.

## 7. Limitations / gaps found (honest, from evidence)

1. **`EditorDocument` is dead code from the external consumer's point of
   view.** It is implemented and unit-tested inside `ledgerkit` itself
   (`editor_model.py` + `test_editor_model.py`), and its own module
   docstring says it is "Intended for use by TUI/editor frontends" — but
   an unanchored search of the entire `ledgerkit-editor` clone (src +
   tests + conftest) found **zero** import or instantiation of
   `EditorDocument` anywhere. It is referenced only in a docstring list
   in `ledger_io.py` (describing it as part of "ledgerkit's public API")
   and in a `# TODO` comment in `commands/__init__.py` describing a
   *not-yet-implemented* "Open file" command-palette action. The editor's
   real load/save/edit pipeline (`ledger_io.py`, `transaction_table.
   action_save`, `view_filter.py`) is an entirely separate, independently
   implemented in-memory model built directly on `ledgerkit.parse_
   string_lenient`/`load`/`journal_to_text`/`transaction_to_text` plus
   editor-local span-based text splicing (`split_journal_segments`,
   `align_posting_amounts`) — it does not call any of `EditorDocument`'s
   `add_transaction`/`update_transaction`/`delete_transaction`/`save`/
   `reload`/`validate_transaction` methods. Any claim that the editor
   "uses `EditorDocument`" is not supported by this evidence.
2. **Version pin vs. test-docstring mismatch.** `pyproject.toml` pins
   `ledgerkit==1.0.0.dev1` exactly, but `tests/test_comprehensive_
   hledger.py`'s own docstring says it "Exercises ledgerkit v0.2.0
   features." These two version identifiers do not match as strings;
   nothing in my permitted evidence resolves whether this is a stale
   docstring, a pre-1.0 internal versioning scheme, or a real
   discrepancy — flagging as-is rather than reconciling.
3. **`editor_model.py`'s own documented V1 limitation**: "include
   directives in the file are not processed; the file is parsed as-is
   with `parse_string()`." `EditorDocument` cannot be used on a
   multi-file (`include`-using) journal without losing the included
   content — the module docstring directs such callers to `loader.
   load_journal()` instead, which `EditorDocument` does not use.
4. **`update_transaction`/`delete_transaction` raise `ValueError` if the
   given transaction's `source_span` is `None`** — i.e. any `Transaction`
   not obtained from `EditorDocument`'s own parse (e.g. a freshly
   constructed one with no span) cannot be passed to these two methods;
   this is enforced by an explicit raise, not silently handled.
5. **`JournalEditor.action_save`'s own reassembly logic has a structural
   risk** (visible directly in the traced call chain, §5.1, step 6):
   because transactions are sorted by date and then the *originally
   positioned* non-transaction blocks are woven back in by post-sort
   slot index rather than re-anchored to the transaction they originally
   preceded/followed, a reorder-by-date save can relocate directives/
   comments/blank separators next to a different transaction than the
   one they were originally associated with. `ledger_io.split_journal_
   segments`'s own docstring is explicit that this is a deliberate,
   documented trade-off ("When the caller sorts transactions by date and
   reassembles by interleaving... in positional order, interleaved
   directives remain between their adjacent transactions" — i.e. adjacent
   to whichever transaction ends up in that slot after sorting, not
   necessarily the original one) and that "directives interleaved
   *between* transactions are not preserved" in the simpler `split_
   preamble` fallback path used when any `source_span` is missing.
6. **`run_basic_checks` is invoked via attribute access
   (`ledgerkit.checks.run_basic_checks(...)`) without a corresponding
   explicit `import ledgerkit.checks` or `from ledgerkit import checks`**
   in `transaction_table.py` — it relies on `ledgerkit.checks` already
   being reachable as an attribute of the `ledgerkit` package object at
   that point in execution (either because `ledgerkit/__init__.py`
   imports the `checks` submodule itself, or because some earlier
   `import ledgerkit.X` elsewhere in the process already bound it as a
   submodule attribute). I did not have permission to read `ledgerkit/
   __init__.py` to confirm which; this is worth a targeted re-check by
   whoever owns that boundary, since it is exactly the kind of "quiet
   dependency on `__init__.py` export shape" `compat-register` entries
   are meant to pin down.
7. **`query_match.py`'s matching logic is an intentional, documented
   fork, not a shared implementation** — the editor team's own comment
   states the policy reason (ledgerkit's `_matches_pattern`/
   `_posting_matches` are private/unexported) and explicitly commits to
   keeping the duplicate "in sync... if that ever changes," which is a
   manual, not mechanically enforced, synchronization obligation. A
   behavioural compatibility claim resting on "the editor's regex/
   substring matching behaves like `ledgerkit.Query`" is therefore a
   claim about two independently maintained implementations agreeing by
   convention, not about one piece of code being reused — confirmed by
   `test_query_match.py`'s own docstring, which runs the duplicate
   against *real* `ledgerkit.Query`/`Transaction`/`Posting` objects
   specifically "to catch any drift," implying drift is considered
   possible, not structurally prevented.
8. **No `compat-register/*.yaml` entries were in scope for this topic**
   (not among the permitted evidence paths), so no compatibility claim
   from that register could be traced or re-checked here — note this
   absence rather than silently skipping item 8 of my brief.
9. I did not read `ledgerkit/__init__.py`, `ledgerkit/loader.py`,
   `ledgerkit/reports.py`, `ledgerkit/commodity_style.py`, or
   `ledgerkit/checks.py` directly (none were in my permitted evidence
   paths for this topic) — all claims above about what those modules
   export/contain are inferred only from how the editor clone's code and
   comments use or describe them, and from `editor_model.py`'s own three
   sibling-module imports. Anyone relying on this report for the exact
   shape of `ledgerkit.checks.run_basic_checks`, `ledgerkit.Query`'s full
   field set, or `ledgerkit.load`'s include/glob/circular-include
   handling should treat those as the editor-clone's own belief about
   the contract, not as directly verified against ledgerkit's own source.

## 8. No apparent scope breach

Permitted evidence paths were followed exactly as given; no assertion,
snapshot, implementation-comparison file, planning doc, legacy `dev-docs/
*.md`/`docs/*.md`, `knowledge/*.md`, `ROADMAP.md`, `CHANGELOG.md`,
`CONTEXT.md`, or the clone's own README/docs/CHANGELOG/AI-README was read.
No `compat-register/*.yaml` was named in my permitted paths for this topic.

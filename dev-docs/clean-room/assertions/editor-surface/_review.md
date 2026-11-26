<!-- producer: domain-skeptic (REVIEW mode) | topic: editor-surface | review-dispatch: edsurf-review-1 | date: 2026-10-03 -->
# Review note: editor-surface assertions (001–010)

## Scope checked
All ten draft assertions in `dev-docs/clean-room/assertions/editor-surface/`,
against the same permitted evidence paths the research dispatch had:
`ledgerkit/editor_model.py`, `tests/test_editor_model.py`, and the `.py`
source/test files (only) under `/tmp/ledgerkit-editor-research-clone-2/`.
I ran the real test suite (`python -m unittest tests.test_editor_model -v`
— 26/26 pass) and re-ran/extended the clone-side greps myself rather than
trusting the assertions' own quoted grep output.

## What I fixed myself (resolved, not escalated)

1. **editor-surface-001** — internal miscount: Statement said "six public
   methods" but then listed seven (`__init__` + six others). Recounted
   directly against `ledgerkit/editor_model.py` (confirmed exactly seven
   public methods, `_shift_spans_after` correctly excluded as private).
   Fixed the text in place.

2. **editor-surface-008** — a genuine, substantive error, not a nuance.
   The original Statement/Justification claimed `ledger_io.py` was "the
   only place in `src/` where `ledgerkit` is... imported at runtime,"
   based on a grep anchored to line-start (`^from ledgerkit\.\|^import
   ledgerkit\b`). That anchor cannot match any indented, function-local
   import — which is exactly the deferred-import style (`# noqa: PLC0415`)
   used throughout this codebase for `ledgerkit` imports. Re-running an
   unanchored `grep -rn "import ledgerkit" --include="*.py" src/` turns up
   eight more runtime import sites across four more files beyond
   `ledger_io.py`: `widgets/view_filter.py` (×3: `_snapshot_journal`,
   `_apply_view_filter`, `_merge_filtered_edits`),
   `widgets/transaction_table.py` (×2, including `action_save`'s
   `from ledgerkit.parser import ParseWarning`), `widgets/filter_popup.py`
   (×1), `utils/journal_index.py` (×1), and `utils/commodity_format.py`
   (×1, `from ledgerkit.commodity_style import CommodityStyle`, confirmed
   by reading the function body — not under `TYPE_CHECKING`). I read every
   one of these lines myself, in context, before treating this as resolved.
   Rewrote Statement, Evidence, Evidence-paths, Justification, Examples,
   and Counterexamples together (not just one field) so nothing was left
   contradicting the corrected claim; the original wording and root-cause
   analysis are preserved in that file's own Review note.

3. **editor-surface-009** — minor off-by-one: Justification attributed
   `from ledgerkit import Query` to line 10 and `from ledgerkit.models
   import Posting, Transaction` to line 11 of `test_query_match.py`; the
   actual lines are 11 and 12 (line 10 is `import pytest`). The
   `Evidence-paths` range (`10-12`) happened to still span the correct
   lines, so the Statement itself was never wrong — only the prose and the
   range's left edge. Fixed both by reading the file directly; all other
   citations in that file (test_comprehensive_hledger.py, test_commodity_
   format.py) checked out exactly as stated.

## What I checked and left unchanged (no finding)

- **002**: docstring quote and `parse_string` call site verified verbatim
  against the source; accurately scoped as `directly_stated`.
- **003**: verified all three mutation methods' `dirty`/`_shift_spans_after`
  behaviour line-by-line, including the conditional (`delta != 0`) shift in
  `update_transaction` already correctly called out in its own
  Counterexamples field. Test line-range citations all double-checked
  against actual test method boundaries.
- **004**: `validate_transaction`'s single-line delegation and "does not
  raise" docstring claim verified; its `Depends on` field already
  correctly flags `checks.py` as outside permitted evidence for deeper
  inspection — appropriately conservative, no fix needed.
- **005**: module-docstring boundary quote verified verbatim. I checked
  this against 007/008 for tension (005 says the module is "intended for
  use by TUI/editor frontends," while 007/008 show the one real TUI
  frontend in scope doesn't actually use it) — this is intent vs.
  actual-adoption, not a contradiction; 007 already makes exactly this
  point as its own assertion, so the two are consistent, not duplicative or
  conflicting.
- **007**: exhaustive `EditorDocument` grep re-run myself; exactly two
  hits, both non-executable (docstring line, TODO comment), confirmed by
  reading both cited lines directly.
- **010**: docstring quotes verified verbatim against `query_match.py` and
  `test_query_match.py`. Its own Open-questions field already correctly
  declines to verify the clone's internal "ledgerkit API Rule" because that
  lives in the clone's `CLAUDE.md`, which is out of scope (docs) — left as
  `partially_supported`/`proposed`, which is the right call, not something
  to quietly firm up.

## Escalating to the lead (not resolved myself)

**editor-surface-006**: the dependency-pin claim
(`"ledgerkit==1.0.0.dev1"`) cites `pyproject.toml:16` in the clone as its
only evidence. My permitted-evidence-paths list — stated to be the same one
the assertion-research dispatch had — restricts the clone to "source and
test `.py` files only, never its README/docs." `pyproject.toml` is neither
a source nor a test `.py` file, so this citation sits outside that
boundary. I did not open the file (doing so would itself breach my own
scope), so I cannot independently confirm or refute the pin. This is a
genuine, unresolved ambiguity about evidence-path governance, not about the
underlying fact: either (a) dispatch edsurf-a6 legitimately had a broader
permitted-evidence list than what I was given and this is a non-issue, or
(b) it exceeded its own evidence boundary by citing a non-`.py` config
file. I downgraded `Evidence-support state` to `uncertain` and `Status` to
`proposed`, named exactly why in the file, and left the original
Statement/Evidence untouched pending the lead's answer — restoring to
`supported`/`verified` (with a note on the broader scope) if (a), or
requiring the claim be re-derived from in-scope evidence (or dropped) if
(b).

## Files touched
- `dev-docs/clean-room/assertions/editor-surface/editor-surface-001.md` (fixed)
- `dev-docs/clean-room/assertions/editor-surface/editor-surface-006.md` (downgraded + escalation note)
- `dev-docs/clean-room/assertions/editor-surface/editor-surface-008.md` (corrected/rewritten)
- `dev-docs/clean-room/assertions/editor-surface/editor-surface-009.md` (fixed)
- `dev-docs/clean-room/assertions/editor-surface/_review.md` (this file)

No other assertion file was modified. No `ledgerkit/` source, `tests/`, or
legacy-documentation file was written to.

<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a3 | date: 2026-10-02 -->
# Assertion: editor-surface-003

## Statement
Each of `EditorDocument`'s three mutation methods (`add_transaction`, `update_transaction`, `delete_transaction`) sets `self.dirty = True` after mutating `self.lines` and `self.journal.transactions`, and each recomputes `source_span` for every affected/subsequent transaction via the internal `_shift_spans_after` helper (or direct reassignment), keeping line-number bookkeeping consistent with the in-memory text buffer.

## Kind
state_transformation

## Basis
directly_stated

## Evidence
From ledgerkit's own repo: all three methods end with `self.dirty = True` and call `_shift_spans_after` (or set `source_span` directly) before returning. Confirmed behaviourally by tests/test_editor_model.py, which assert span shifts after each mutation type.

Evidence-paths: [ledgerkit/editor_model.py:51-59, ledgerkit/editor_model.py:65-110, ledgerkit/editor_model.py:112-143, ledgerkit/editor_model.py:145-168, tests/test_editor_model.py:122-137, tests/test_editor_model.py:177-195, tests/test_editor_model.py:220-228]

## Justification
Tests explicitly check that `source_span.start_line` of unrelated/later transactions changes after an add, update (size-changing), or delete, and that `dirty` becomes `True` in each case.

## Examples
`test_add_transaction_middle_shifts_later_spans` (tests/test_editor_model.py:122-130) inserts a transaction mid-journal and asserts the "Coffee shop" transaction's `source_span.start_line` increases.

## Counterexamples
`test_update_transaction_same_size_no_shift` (tests/test_editor_model.py:159-175) shows that when the replacement transaction serialises to the same number of lines, later spans are NOT shifted (delta == 0 skips `_shift_spans_after`) — confirming the shift is conditional on line-count delta, not unconditional.

## Depends on
editor-surface-001.

## Open questions
None.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

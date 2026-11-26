<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a8 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: edsurf-review-1 | date: 2026-10-03 -->
<!-- REVIEW CORRECTION (2026-10-03): the original Statement below ("the only
     place ... is inside ledger_io.py") was found FALSE on direct re-check —
     see Review note at the end of this file. Statement, Evidence,
     Evidence-paths, Justification, Examples and Counterexamples have all
     been rewritten to the corrected, re-verified claim. The original
     wording is preserved in the Review note for the record. -->
# Assertion: editor-surface-008

## Statement
`ledgerkit` is imported at runtime (not just under `TYPE_CHECKING`) from six
files in `ledgerkit-editor`'s `src/` tree, not only from
`src/ledgerkit_editor/utils/ledger_io.py`: `ledger_io.py` itself
(`load_journal`, `save_journal`), `widgets/view_filter.py`
(`_snapshot_journal`, `_apply_view_filter`, `_merge_filtered_edits`),
`widgets/transaction_table.py` (`action_save`, which also does
`from ledgerkit.parser import ParseWarning`), `widgets/filter_popup.py`,
`utils/journal_index.py` (`build_journal_index`), and
`utils/commodity_format.py` (`extract_commodity_styles`, deferred
`from ledgerkit.commodity_style import CommodityStyle`). Every one of these
is a function-local, deferred import (`# noqa: PLC0415`), and every one
calls `ledgerkit.load()`, `ledgerkit.parse_string_lenient()`,
`ledgerkit.transaction_to_text()`, `ledgerkit.journal_to_text()`, or imports
`ParseWarning`/`CommodityStyle` directly — never `EditorDocument`
(consistent with editor-surface-007). Two files additionally carry a
`TYPE_CHECKING`-only import of `ledgerkit.models`/`ledgerkit.commodity_style`
purely for annotations: `ledger_io.py` and `commodity_format.py`.

## Kind
relationship

## Basis
observed_behaviour

## Evidence
From the ledgerkit-editor clone: an exhaustive `grep -rn "import ledgerkit"
--include="*.py" src/` (plus a separate check for `from ledgerkit\.` forms)
returns eight runtime `import ledgerkit` statements across five files, plus
two further runtime `from ledgerkit.X import Y` statements (one in
`transaction_table.py`, one in `commodity_format.py`) — none of them inside
an `if TYPE_CHECKING:` block. Each cited line was read directly to confirm
it sits inside a function body, not a type-checking guard.

Evidence-paths: [/tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/ledger_io.py:252, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/ledger_io.py:267, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/view_filter.py:113, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/view_filter.py:133, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/view_filter.py:199, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/transaction_table.py:328, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/transaction_table.py:342, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/widgets/filter_popup.py:267, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/journal_index.py:60, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/commodity_format.py:143, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/ledger_io.py:22-23, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/commodity_format.py:22-24]

## Justification
`grep -rn "import ledgerkit" --include="*.py" src/` (run from the clone
root) returns exactly the eight `import ledgerkit` lines cited above across
five files. A further grep for `from ledgerkit\.` finds `transaction_table.py:342`
(`from ledgerkit.parser import ParseWarning`, inside `action_save`, after a
runtime `import ledgerkit` two lines earlier) and `commodity_format.py:143`
(`from ledgerkit.commodity_style import CommodityStyle`, inside
`extract_commodity_styles`'s function body — confirmed by reading lines
95-145 of that file, which show no `TYPE_CHECKING` guard around it). Each
site was read in its surrounding function to confirm it executes at call
time, not just at type-check time.

## Examples
`journal_index.py:60`, inside `build_journal_index`: `import ledgerkit` then
`journal, _errors = ledgerkit.parse_string_lenient(text)`. `view_filter.py:133`,
inside `_apply_view_filter`: `import ledgerkit` then multiple calls to
`ledgerkit.transaction_to_text(...)` and `ledgerkit.journal_to_text(...)`.
`transaction_table.py:328-344`, inside `action_save`: `import ledgerkit`,
then `from ledgerkit.parser import ParseWarning`, then
`ledgerkit.parse_string_lenient(text)`.

## Counterexamples
None — the six-file list above is exhaustive for `src/` per the grep in
Justification. (Tests import `ledgerkit` even more broadly — see
editor-surface-009 — but tests are a separate consumer from production
`src/` code.) `EditorDocument`/`editor_model` is not imported anywhere in
any of these six files, consistent with editor-surface-007.

## Depends on
editor-surface-007 (the exhaustive `EditorDocument` grep that first
established `EditorDocument` is unused; this assertion is about which
*other* `ledgerkit` symbols are used instead, in how many places).

## Open questions
None.

## Evidence-support state
supported — for the corrected Statement above. The original Statement (see
Review note) was unsupported and directly contradicted by evidence
available within the same permitted evidence paths.

## Status
verified

## Supersedes
(none)

## Review note
REVIEW (domain-skeptic, 2026-10-03): the original Statement claimed
`ledger_io.py` was "the only place in src/ where ledgerkit is... imported at
runtime," supported by a Justification claiming a grep for
`^from ledgerkit\.\|^import ledgerkit\b` "returned no results in src/ at all"
outside ledger_io.py. This is false: re-running an exhaustive
`grep -rn "import ledgerkit" --include="*.py" src/` (no anchor restricting
to line-start, which is what let the original grep miss every one of the
`        import ledgerkit  # noqa: PLC0415` lines — all of which are
indented, function-local imports, so a `^import ledgerkit` anchor can never
match them) turns up eight more runtime import sites across four more
files: `widgets/view_filter.py` (x3), `widgets/transaction_table.py` (x2,
including `from ledgerkit.parser import ParseWarning`),
`widgets/filter_popup.py` (x1), `utils/journal_index.py` (x1), and
`utils/commodity_format.py` (x1, `from ledgerkit.commodity_style import
CommodityStyle`, confirmed inside a function body, not `TYPE_CHECKING`). I
read each cited line directly, in its surrounding function, before treating
this as resolved rather than escalating it — it was fully researchable
within the permitted evidence paths (all `.py` files in `src/`), so this is
a resolved finding, not an open escalation. The root cause of the original
error was almost certainly the `^`-anchored grep pattern in the original
Justification, which is blind to any indented (i.e. function-local,
deferred) import — exactly the style this whole codebase uses for
`ledgerkit` imports (per the `# noqa: PLC0415` deferred-import convention
visible throughout `src/`). I rewrote Statement, Evidence, Evidence-paths,
Justification, Examples, and Counterexamples together so no field was left
contradicting the corrected claim.

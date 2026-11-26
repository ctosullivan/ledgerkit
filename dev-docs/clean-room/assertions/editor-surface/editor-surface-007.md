<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a7 | date: 2026-10-02 -->
# Assertion: editor-surface-007

## Statement
Despite `ledger_io.py`'s module docstring listing `ledgerkit.EditorDocument(path)` as one of the "Key ledgerkit types used here," no file anywhere in the `ledgerkit-editor` clone's source tree (`src/`) or test tree (`tests/`) actually imports, instantiates, or calls `EditorDocument` in executable code. The only two occurrences of the string "EditorDocument" in the entire clone are both in prose comments/docstrings, not code: the aspirational docstring line in `ledger_io.py` and a `# TODO` comment in `commands/__init__.py` ("reload EditorDocument").

## Kind
boundary

## Basis
observed_behaviour

## Evidence
From the ledgerkit-editor clone: an exhaustive recursive grep for `EditorDocument` across every `.py` file in the clone returned exactly two hits, both non-executable (a docstring line and a comment), and zero import statements or call sites.

Evidence-paths: [/tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/utils/ledger_io.py:8, /tmp/ledgerkit-editor-research-clone-2/src/ledgerkit_editor/commands/__init__.py:80]

## Justification
`grep -rn "EditorDocument" --include="*.py" .` run from the clone root returned only these two lines; no `import ledgerkit.editor_model` or `EditorDocument(...)` call exists anywhere in the clone.

## Examples
`ledger_io.py`'s docstring (lines 1-14) lists four "Key ledgerkit types used here," including `ledgerkit.EditorDocument(path)` at line 8, but the file's only two functions (`load_journal`, `save_journal`, lines 235-269) use only `ledgerkit.load()` and `ledgerkit.journal_to_text()` — never `EditorDocument`.

## Counterexamples
None — the grep was exhaustive over all `.py` files in the clone.

## Depends on
editor-surface-001 (establishes what EditorDocument's surface is, to confirm it is this symbol being referenced, not something else of the same name).

## Open questions
Whether `EditorDocument` is used via some non-`.py` mechanism (e.g. dynamic string-based import, a config file, a widget binding) was not checked — out of scope per the task's restriction to source/test `.py` files.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

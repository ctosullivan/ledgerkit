<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a2 | date: 2026-10-02 -->
# Assertion: editor-surface-002

## Statement
`EditorDocument.__init__` loads the journal using `ledgerkit.parser.parse_string()` directly (not `ledgerkit.loader.load_journal()`), and as a result does not process `include` directives. This is documented in the class's own docstring as a stated "V1 limitation," with an explicit pointer to use `loader.load_journal()` when full include support is required.

## Kind
rule

## Basis
directly_stated

## Evidence
From ledgerkit's own repo: the class docstring states the limitation verbatim, and `__init__` literally calls `parse_string(text, source_file=abs_path)`.

Evidence-paths: [ledgerkit/editor_model.py:28-30, ledgerkit/editor_model.py:44, ledgerkit/editor_model.py:14]

## Justification
The docstring text is unambiguous: "V1 limitation: include directives in the file are not processed; the file is parsed as-is with parse_string(). Use loader.load_journal() when full include support is required."

## Examples
`EditorDocument(path)` on a file containing an `include` directive would not resolve that directive's contents into `self.journal`.

## Counterexamples
None — this is a stated, not inferred, limitation.

## Depends on
ledgerkit.parser.parse_string (imported at editor_model.py:14).

## Open questions
Whether a future version removes this limitation is not addressed in this file.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

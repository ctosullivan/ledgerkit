<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a5 | date: 2026-10-02 -->
# Assertion: editor-surface-005

## Statement
`editor_model.py`'s module docstring explicitly scopes the module's intended consumer and its relationship to the rest of ledgerkit: "Intended for use by TUI/editor frontends. Not imported by any core module."

## Kind
boundary

## Basis
directly_stated

## Evidence
From ledgerkit's own repo: this sentence is the literal, final line of the module docstring at the top of the file.

Evidence-paths: [ledgerkit/editor_model.py:1-6]

## Justification
This is a direct quotation establishing the module's architectural boundary: it is a leaf consumer-facing module, not a dependency of ledgerkit's own core.

## Examples
No other file in the permitted ledgerkit evidence set imports `editor_model` (confirmed: tests/test_editor_model.py is the only consumer within the permitted scope, and it is itself a test, not a core module).

## Counterexamples
None found within permitted evidence.

## Depends on
None.

## Open questions
None.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

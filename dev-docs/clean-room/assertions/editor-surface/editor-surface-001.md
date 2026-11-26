<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a1 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: edsurf-review-1 | date: 2026-10-03 -->
# Assertion: editor-surface-001

## Statement
`ledgerkit/editor_model.py` defines a single public class, `EditorDocument`, with four public attributes (`path: str`, `journal: Journal`, `lines: list[str]`, `dirty: bool`) and seven public methods: `__init__(self, path: str)`, `add_transaction(self, txn: Transaction) -> None`, `update_transaction(self, original: Transaction, updated: Transaction) -> None`, `delete_transaction(self, txn: Transaction) -> None`, `save(self) -> None`, `reload(self) -> None`, and `validate_transaction(self, txn: Transaction) -> list[CheckError]`.

## Kind
definition

## Basis
directly_stated

## Evidence
From ledgerkit's own repo: the class declaration, attribute type annotations, and every method signature are read directly from the source file.

Evidence-paths: [ledgerkit/editor_model.py:18-36, ledgerkit/editor_model.py:38, ledgerkit/editor_model.py:65, ledgerkit/editor_model.py:112, ledgerkit/editor_model.py:145, ledgerkit/editor_model.py:170, ledgerkit/editor_model.py:178, ledgerkit/editor_model.py:188]

## Justification
This is the complete public surface of the module as written; no other class or module-level function is defined in the file.

## Examples
`EditorDocument(path)` constructs an instance; `doc.add_transaction(txn)` mutates it (confirmed by tests/test_editor_model.py:102-137).

## Counterexamples
None found — no other public symbols exist in the module.

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

## Review note
REVIEW (domain-skeptic, 2026-10-03): the Statement's own method list contains
seven items (`__init__` plus six others) but the lead-in text said "six
public methods." Miscount, not a genuine ambiguity — re-counted directly
against ledgerkit/editor_model.py (confirmed exactly seven public methods,
one private helper `_shift_spans_after` correctly excluded) and corrected
the text in place. No other field required a matching fix.

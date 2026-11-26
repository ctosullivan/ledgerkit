<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a4 | date: 2026-10-02 -->
# Assertion: editor-surface-004

## Statement
`EditorDocument.validate_transaction(txn)` runs only the single "autobalanced" check (`ledgerkit.checks.check_transaction_autobalanced`) against the given transaction in isolation, returns a possibly-empty `list[CheckError]`, and never raises.

## Kind
definition

## Basis
directly_stated

## Evidence
From ledgerkit's own repo: the method body is a one-line delegation to `check_transaction_autobalanced(txn)`, and its docstring states "Does not raise." Confirmed by tests asserting `errors == []` for balanced/elided postings and a single `CheckError` with `check_name == "autobalanced"` for an unbalanced transaction.

Evidence-paths: [ledgerkit/editor_model.py:12, ledgerkit/editor_model.py:188-193, tests/test_editor_model.py:310-343]

## Justification
Three dedicated test methods (`test_validate_balanced`, `test_validate_unbalanced`, `test_validate_elided`) exercise exactly this contract and pass per the test file's own assertions.

## Examples
An elided posting (one posting with no explicit amount) still validates as balanced — `test_validate_elided` (tests/test_editor_model.py:332-343).

## Counterexamples
None.

## Depends on
ledgerkit.checks.check_transaction_autobalanced, ledgerkit.checks.CheckError (both outside the permitted evidence scope for deep inspection, used here only via their call site in editor_model.py).

## Open questions
Whether other checks (beyond autobalanced) are ever planned to be added to this method is not stated in the file.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

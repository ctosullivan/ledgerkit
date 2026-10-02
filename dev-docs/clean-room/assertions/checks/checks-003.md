<!-- producer: assertion-research | topic: checks | dispatch: ck-accounts-03 | date: 2026-10-02 -->
# Assertion: checks-003

## Statement
`check_accounts` reports at most one CheckError per run: it scans transactions and their postings in order and stops at the very first posting whose account is not in `journal.declared_accounts` (case-sensitive comparison). If `declared_accounts` is empty, every posting account is considered undeclared, so the very first posting's account triggers the single error.

## Kind
rule
## Basis
directly_stated
## Evidence
The function's docstring (checks.py:223-236) states it "Stops at the first undeclared account found (by transaction then posting order), matching hledger behaviour" and is case-sensitive; the code (238-262) `return`s immediately inside the double loop on the first miss, guaranteeing a list of length ≤ 1.

Evidence-paths: [ledgerkit/checks.py:222-263, tests/test_checks/test_checks.py:155-192]

## Justification
`test_each_undeclared_reported_once` (176-182) constructs two transactions both using account "missing" and declared_accounts=["income"]; the assertion is `len(errors) == 1`, directly confirming the stop-at-first behaviour (a second, independent "missing" occurrence in txn2 produces no additional error). `test_case_sensitive` (184-189) confirms "Assets:Bank" is treated as distinct from declared "assets:bank".

## Examples
`test_no_declarations_reports_first` (168-174): journal has no `declared_accounts` at all; posting account "assets:bank" is flagged as the sole error, with comment "hledger stops at the first undeclared account (posting order)".

## Counterexamples
None — `test_declared_accounts_pass` (156-159) shows zero errors when all posting accounts are in `declared_accounts`, consistent with the rule rather than contradicting it.

## Depends on
checks-005 (shared `_build_strict_context` formatting) for the error message's exact shape.

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes
None

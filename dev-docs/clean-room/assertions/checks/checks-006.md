<!-- producer: assertion-research | topic: checks | dispatch: ck-assert-06 | date: 2026-10-02 -->
# Assertion: checks-006

## Statement
`check_assertions` validates four balance-assertion variants carried per-posting on `posting.balance_assertion` (a `BalanceAssertion` with `.amount`, `.inclusive`, `.sole_commodity` flags): `=` (single-commodity, subaccount-exclusive), `==` (sole-commodity, subaccount-exclusive — all other commodities in that exact account must be zero), `=*` (single-commodity, subaccount-inclusive — sums the account plus all `account:`-prefixed subaccounts), `==*` (sole-commodity, subaccount-inclusive). Postings are processed in (date, source_line-or-0) order — NOT journal/parse order — maintaining a running per-account-per-commodity balance; a mismatch between expected and actual (Decimal equality) appends one CheckError, and a sole-commodity violation (any other nonzero commodity present) appends a further, separate CheckError.

## Kind
rule
## Basis
directly_stated
## Evidence
Docstring (checks.py:414-434) explicitly enumerates the four variants and their inclusive/sole-commodity semantics and states "Costs and posting status are ignored." The sort key `(t.date, t.source_line or 0)` (441-444) establishes date-then-source_line ordering explicitly over parse/list order. Lines 456-516 implement running-balance accumulation, inclusive-subtree summation via `startswith(prefix)`, and the two independent error-append sites (actual≠expected at 479-488; sole-commodity nonzero at 490-515).

Evidence-paths: [ledgerkit/checks.py:414-516, tests/test_checks/test_checks.py:437-593]

## Justification
`test_date_order_not_parse_order` (558-581) is a direct, explicit test of the ordering claim: txn1 (date 2024-01-10, source_line=1) is stored before txn2 (date 2024-01-01, source_line=100) in the journal's transaction list, yet the assertion in txn1 only passes because the check processes txn2 first by date. `test_inclusive_assertion_sums_subaccounts`/`test_inclusive_assertion_fail` (529-556) confirm `=*` sums `assets:bank` + `assets:bank:savings`. `test_sole_commodity_fail_other_commodity_present` (506-527) confirms the `==` sole-commodity error fires when an unrelated commodity ($) is nonzero, with message containing "sole-commodity".

## Examples
`test_cumulative_balance_over_two_transactions` (474-492): two chronological transactions to "assets:bank", each with its own assertion (£500 then £420 after a -£80 posting), both pass — demonstrating running-balance accumulation across transactions, not just within one.

## Counterexamples
`test_single_commodity_assertion_fail` (458-472) shows the non-sole-commodity `=`/`=*` path still fails on simple expected≠actual mismatch (expected £999, actual £10), producing exactly one error containing both the account name and both amounts — confirming the two error types are not conflated when sole_commodity=False.

## Depends on
None additional beyond the Posting/BalanceAssertion/Amount model shapes assumed by the test helper `_posting_with_assertion` (test_checks.py:413-434), which is itself test-only scaffolding, not production code.

## Open questions
The fixtures `assertions_pass.journal`/`assertions_fail.journal` are referenced by `test_fixture_assertions_pass`/`_fail` (583-593) but live under tests/fixtures/, outside this task's permitted evidence paths, so their exact journal content was not inspected — only that the test asserts `assets:checking` appears in the failing case's message.

## Evidence-support state
supported
## Status
verified
## Supersedes
None

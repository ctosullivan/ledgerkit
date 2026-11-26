<!-- producer: assertion-research | topic: checks | dispatch: ck-autobal-02 | date: 2026-10-02 -->
# Assertion: checks-002

## Statement
`check_autobalanced` (via `_check_txn_balanced`) treats a transaction as balanced if it has exactly one elided posting (amount=None), regardless of how many commodities appear among the other postings. If it has two or more elided postings, it unconditionally fails with a "multiple elided postings (autobalanced)" error. If it has zero elided postings, every commodity's net sum across postings must equal exactly zero (Decimal arithmetic); any nonzero net commodity produces one CheckError per offending commodity.

## Kind
rule
## Basis
directly_stated
## Evidence
`_check_txn_balanced` (checks.py:103-135) implements exactly this three-way branch: `len(elided) > 1` returns an immediate multi-elided error; `len(elided) == 1` returns `[]` with a comment citing hledger's rule that one elided posting is allowed "regardless of how many commodities are present"; otherwise it sums quantities per commodity key and emits an error for each nonzero-net commodity.

Evidence-paths: [ledgerkit/checks.py:68-135, tests/test_checks/test_checks.py:98-148]

## Justification
The docstrings of `check_autobalanced` (checks.py:68-90) and `check_transaction_autobalanced` (93-100) state the rule directly, and `_check_txn_balanced`'s code is a literal implementation of it. Tests confirm each branch independently: `test_single_elided_posting_passes`, `test_multiple_elided_postings_fails`, `test_elided_with_multi_commodity_now_valid` (explicitly testing a 2-commodity txn with one elided "bridge" posting passes), `test_multi_commodity_no_elided_balanced`/`_unbalanced`.

## Examples
`test_elided_with_multi_commodity_now_valid` (test_checks.py:121-127): postings `assets £10.00`, `other $5.00`, `bridge None` — two commodities, one elided — asserts `errors == []`. `test_unbalanced_fails` (103-108): `assets £10.00`, `income £5.00` (same sign, not netting to zero) — asserts exactly 1 error containing "not balanced".

## Counterexamples
`test_multiple_elided_postings_fails` (114-119): two elided postings (`assets None`, `income None`) — fails with "multiple elided" regardless of amounts, showing the one-elided-posting leniency does NOT extend to two.

## Depends on
None directly, though the module comment at checks.py:116-118 references a separate `resolve_elision()` function (not in permitted evidence) that performs the actual amount-inference this check assumes succeeds.

## Open questions
`resolve_elision()` itself is outside permitted evidence, so how the inferred per-commodity amounts are actually computed/applied downstream is not verified here — only that this check treats a single-elided transaction as always balanced.

## Evidence-support state
supported
## Status
verified
## Supersedes
None

<!-- producer: assertion-research | topic: checks | dispatch: ck-commod-04 | date: 2026-10-02 -->
# Assertion: checks-004

## Statement
`check_commodities` reports at most one CheckError per run, stopping at the first posting whose non-empty commodity symbol is not in `journal.declared_commodities`. Postings with `amount is None` are skipped entirely, and postings whose amount's commodity symbol is the empty string `""` (zero-amount with no unit) are always exempt from this check even if `declared_commodities` doesn't list `""`.

## Kind
rule
## Basis
directly_stated
## Evidence
Docstring (checks.py:266-279) states the stop-at-first behaviour and that "Zero-amount postings (commodity symbol == '') are always exempt"; code (281-287) explicitly `continue`s past `posting.amount is None` and past `sym == ""` before checking membership in `declared`.

Evidence-paths: [ledgerkit/checks.py:266-312, tests/test_checks/test_checks.py:199-233]

## Justification
`test_zero_amount_no_commodity_exempt` (212-223) builds a journal with two postings both `Amount(Decimal("0"), "")` and no `declared_commodities` at all, asserting `check_commodities(j) == []` — this directly confirms the empty-symbol exemption applies even with zero declarations. `test_each_undeclared_reported_once` (225-230) confirms the stop-at-first/dedup behavior across two transactions sharing the same undeclared commodity "£".

## Examples
`test_undeclared_commodity_fails` (205-210): journal with postings in "£" and no `declared_commodities` — 1 error whose message contains "£".

## Counterexamples
None found that contradict the stated rule.

## Depends on
checks-005 (shared `_build_strict_context` formatting).

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes
None

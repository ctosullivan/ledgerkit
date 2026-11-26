<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-006 | date: 2026-10-02 -->
# Assertion: reports-cli-006

## Statement
`reports.register()` returns a chronological `RegisterResult` (list[RegisterRow]) where `running_balance` is the cumulative sum of `amount.quantity` across ALL rows in output order, never grouped or re-aggregated by account — even when a `depth` setting clips several postings' displayed account names to the same string, each posting remains its own row.
## Kind
invariant
## Basis
directly_stated
## Evidence
Docstring: "running_balance is the cumulative sum of amount.quantity across all rows in output order — never grouped/aggregated by account, even when depth clips several postings' displayed account names to the same string...No posting is ever excluded on account of query.depth/_query_depth — fixed Stage C Phase 5; previously this function (unlike balance) applied depth as an exclusion filter, a real pre-existing bug". Test `test_running_balance_accumulates` iterates every row, re-accumulating `running` and asserting equality with `row.running_balance`; `test_running_balance_final` asserts the last row's running_balance is `Decimal("0")` for a balanced journal.
## Justification
Implementation at reports.py:475-493 keeps a single `running` accumulator across the full postings loop with no per-account bucketing, matching the docstring and tests.
## Examples
filtered.journal: 6 transactions × 2 postings = 12 RegisterRow objects (`test_row_count_no_query`), cumulative running_balance ending at 0.
## Counterexamples
This was previously a real bug: depth used to act as an exclusion filter in `register()` (unlike `balance()`), described as "a real pre-existing bug distinct from the -q depth: divergence" — now fixed.
## Depends on
None
## Open questions
None
## Evidence-support state
supported
## Status
verified
## Supersedes
None

Evidence-paths: [ledgerkit/reports.py:437-493, tests/test_reports.py:330-339]

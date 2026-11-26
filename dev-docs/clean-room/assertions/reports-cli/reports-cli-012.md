<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-012 | date: 2026-10-02 -->
# Assertion: reports-cli-012

## Statement
`stats()` is the one report function where a depth constraint (via `-q "depth:N"`'s `_query_depth`) EXCLUDES accounts deeper than the limit from `account_count`/`account_depth`, rather than clipping/aggregating them as `balance()`, `register()`, and `accounts()` all do. This is described as a genuine, source-confirmed hledger quirk, not a Ledgerkit invention.
## Kind
rule
## Basis
directly_stated
## Evidence
`stats()` docstring: "`_query_depth`... Applied via `ledgerkit.query.depth.account_excluded_by_depth`, NOT `clip_account_name` — stats is a genuine, source-confirmed exception where hledger EXCLUDES accounts deeper than the limit for this field rather than clipping them, unlike every other depth-aware report function here". Implementation: `all_accounts: set[str] = {p.account for t in txns for p in t.postings if not account_excluded_by_depth(depth_spec, p.account)}` (reports.py:559-562) — contrast with `balance`/`register`/`accounts`, which all call `clip_account_name(depth_spec, ...)`. CLI test `test_stats_query_depth_excludes_rather_than_clips` with `-q "depth:2"` on filtered.journal (which has 3-segment accounts like `expenses:housing:rent`) asserts `"Accounts            : 2 (depth 2)"` — i.e. only the 2 accounts at depth ≤2 survive, deeper ones are dropped from the count entirely, not rolled up into shallower buckets.
## Justification
Code-level contrast (`account_excluded_by_depth` vs `clip_account_name`) plus a direct CLI-level regression test confirm this is deliberate and asymmetric relative to the other three depth-aware reports.
## Examples
`-q "depth:2" stats` on filtered.journal → `Accounts : 2 (depth 2)`, not a rolled-up count of all distinct depth-clipped names.
## Counterexamples
`balance`/`register`/`accounts` with the same `depth:2` instead roll deeper accounts up into their depth-2 ancestor and keep them in the result (see reports-cli-004/006/008 family and `test_balance_query_depth_truncates`).
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

Evidence-paths: [ledgerkit/reports.py:523-531, ledgerkit/reports.py:558-562, tests/test_cli/test_cli.py:381-389]

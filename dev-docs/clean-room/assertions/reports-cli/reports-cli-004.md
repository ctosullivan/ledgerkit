<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-004 | date: 2026-10-02 -->
# Assertion: reports-cli-004

## Statement
`reports.balance()` returns per-commodity net balances for each account as a `BalanceResult` (dict[str, dict[str, Decimal]]-like, keyed by full account name → commodity → net Decimal) by default; passing `tree=True` instead returns `list[BalanceRow]`, which additionally includes every implicit parent account (all colon-prefixes) with `is_subtotal=True` for pure-parent rows and aggregated (self + all descendants) amounts, sorted alphabetically by account name.
## Kind
state_transformation
## Basis
directly_stated
## Evidence
`balance()` docstring: "When tree=True, returns list[BalanceRow] with implicit parent accounts and aggregate subtotals. When False (default), returns a flat dict...". `_build_balance_tree()` computes `all_accounts` by adding every colon-prefix of every account, then builds a `BalanceRow` per account with `is_subtotal=(account not in totals)`. Test `test_balance_tree_implicit_parents_present` confirms "expenses" (a non-leaf account) appears in tree output even though no posting targets "expenses" directly; `test_balance_tree_is_subtotal_for_implicit_parents` confirms `is_subtotal=True` for it, while `test_balance_tree_is_subtotal_false_for_leaf_accounts` confirms `False` for "expenses:rent".
## Justification
Code and tests agree; `_build_balance_tree` is the sole producer of tree-mode rows and is called only when `tree=True` (reports.py:432-434).
## Examples
`balance(journal, tree=True)` on multicommodity.journal yields rows for "expenses", "expenses:rent", "expenses:software", etc., with "expenses".amounts aggregating all three commodities (£, $, €) of its descendants.
## Counterexamples
None
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

Evidence-paths: [ledgerkit/reports.py:271-304, ledgerkit/reports.py:372-434, tests/test_reports.py:1206-1251]

<!-- producer: assertion-research | topic: checks | dispatch: ck-other-07 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: ck-other-07-review | date: 2026-10-03 -->
# Assertion: checks-007

## Statement
The three "other"-tier checks each implement a distinct, independent rule and emit one CheckError per distinct violation (not capped at one, unlike the strict checks): `check_payees` flags each distinct transaction `description` not present in `declared_payees` exactly once regardless of repetition, and flags everything if `declared_payees` is empty/unset; `check_ordereddates` flags any transaction whose `date` is strictly less than `prev_date`, a running marker that starts at `None` and is advanced to the current transaction's date only when that transaction was NOT flagged — i.e. `prev_date` is the most recent date that itself passed the check (a "high-water mark"), NOT necessarily the literal immediately-preceding transaction's date when that preceding transaction was itself out of order. Same-date transactions never trigger it. `check_uniqueleafnames` flags every colon-segment "leaf" (the substring after the last `:`, or the whole name when there is no `:`) shared by two or more distinct full account names across the whole journal.

## Kind
rule
## Basis
directly_stated
## Evidence
`check_payees` (checks.py:319-344) uses a `seen_undeclared` set keyed by description text to dedupe. `check_ordereddates` (checks.py:360-374) initialises `prev_date = None` and, for each transaction, either appends an error (if `prev_date is not None and txn.date < prev_date`) or else sets `prev_date = txn.date` — note the `else`: `prev_date` is reassigned ONLY on the non-violating branch, so a violating transaction leaves `prev_date` unchanged for the comparison against the next transaction. `check_uniqueleafnames` (377-407) groups all accounts by `acct.rsplit(":", 1)[-1]` and flags any leaf with `len(accounts) > 1`.

Evidence-paths: [ledgerkit/checks.py:319-407, tests/test_checks/test_checks.py:240-333]

## Justification
`test_each_payee_reported_once` (260-265): two transactions with identical undeclared description "Shop" yield exactly 1 error. `test_no_declarations_flags_all` (253-258): two transactions with distinct descriptions and no `declared_payees` yield exactly 2 errors (contrast with payees-dedup — distinct descriptions are NOT deduped against each other). `test_same_date_passes` (287-289) confirms equal consecutive dates don't trigger ordereddates. `test_duplicate_leaf_fails` (325-329): accounts "assets:bank:checking" and "savings:checking" share leaf "checking" and produce exactly 1 error whose message contains "checking".

REVIEW NOTE (domain-skeptic, 2026-10-03): the original Statement here read "...flags any transaction whose date is strictly less than the immediately preceding (in list order) transaction's date...". That is contradicted by this assertion's own Evidence paragraph, which already (correctly) says `prev_date` updates "only when not out-of-order" — the Statement's simplification silently dropped that qualifier. I ran `check_ordereddates` directly (permitted evidence path `ledgerkit/checks.py`, no test needed to be modified) against three transactions dated 2024-01-10, 2024-01-05, 2024-01-07 (in that list order): if the rule really compared each transaction only to its immediately-preceding list-neighbor, the third transaction (01-07) should pass, since 01-07 > 01-05 (its immediate predecessor). Instead both the second and third transactions are flagged, each reported as "appears after 2024-01-10" — confirming the comparison is against the running high-water mark (01-10), not the literal preceding transaction (01-05). The Statement above has been corrected accordingly; no existing test in tests/test_checks/test_checks.py exercises a 3-transaction sequence with this shape, so this distinction was previously untested, not just mis-stated.

## Examples
`check_uniqueleafnames` iterates `sorted(leaf_to_accounts.items())` (397) giving deterministic error ordering by leaf name; the message format is `duplicate leaf account name {leaf!r}: {dupes} (uniqueleafnames check)` with `dupes` itself sorted (399-405).

A direct run of `check_ordereddates` on transactions dated [2024-01-10, 2024-01-05, 2024-01-07] (in that list order) yields two errors, both anchored to "2024-01-10" — demonstrating the high-water-mark behavior (see REVIEW NOTE above; not captured by an existing named test, verified by direct execution against `ledgerkit/checks.py`).

## Counterexamples
`test_unique_leaves_passes` (321-323) with three accounts having three distinct leaves ("checking", "salary", "food") yields zero errors, confirming no false positives when leaves genuinely differ.

## Depends on
None.

## Open questions
`check_ordereddates`' docstring (348-350) notes hledger itself evaluates this per-file but ledgerkit merges included files first, so the check operates on the full merged list — this is stated as an intentional divergence in the docstring but the actual per-file hledger behavior is not verifiable from permitted evidence (would require hledger docs/behavior, out of scope here).

## Evidence-support state
supported
## Status
verified
## Supersedes
None

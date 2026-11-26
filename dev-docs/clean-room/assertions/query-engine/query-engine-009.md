<!-- producer: assertion-research | topic: query-engine | dispatch: qe-dispatch-009 | date: 2026-10-02 -->
# Assertion: query-engine-009

## Statement
`matches_transaction` and `matches_posting` differ in how `Acct`/`MaxAccountLevel` are checked but agree on everything else: at the transaction level, `Acct`/`MaxAccountLevel` match if *any* posting in the transaction satisfies the account-level check (`any(...)` over `txn.postings`); at the posting level, they are checked only against that one posting's own account. `Desc`, `DateSpan`, and `Status` are transaction-level facts and are evaluated identically (against `txn`, ignoring which specific posting is passed) in both functions. All matching against text (`Acct`/`Desc`) is case-insensitive substring (infix) matching via `.search()` on a `re.IGNORECASE`-compiled pattern — never `.match()`/`.fullmatch()`.

## Kind
rule
## Basis
directly_stated
## Evidence
`matches_transaction` (eval.py lines 118-127): `Acct` → `any(_account_matches(node.pattern, p.account) for p in txn.postings)`; `MaxAccountLevel` → `any(_account_depth(p.account) <= node.n for p in txn.postings)`; `Desc`/`Status` reference only `txn`. `_matches_posting_impl` (lines 155-164): `Acct` → `_account_matches(node.pattern, posting.account)` (single posting, no `any`); `Desc`/`Status`/`DateSpan` reference `txn` the same way. `compile_hledger_regex`'s docstring (regex.py lines 272-277) states matching "is always case-insensitive and always infix (substring) — callers must use `.search()`, never `.match()`/`.fullmatch()`," and `_account_matches`/`_text_matches` (eval.py lines 51-56) both call `.search()`. Confirmed in `test_eval.py::TestAcct` (lines 30-51): `test_transaction_matches_if_any_posting_matches`, `test_posting_level_checks_only_that_posting` (food-posting matches, checking-posting does not), `test_case_insensitive`.

Evidence-paths: [ledgerkit/query/eval.py:100-175, ledgerkit/query/regex.py:265-277, tests/test_query/test_eval.py:30-62]

## Justification
This "any posting" vs "this posting only" asymmetry is the key semantic difference between the two entry points and directly explains why `balance`/`register`-style reports (posting-oriented) and `print`-style reports (transaction-oriented) can show different result sets for the same `acct:` query against a multi-posting transaction.

## Examples
Transaction with postings `expenses:food:groceries` and `assets:checking`: `matches_transaction(Acct("food"), txn)` is True; `matches_posting(Acct("food"), txn, checking_posting)` is False even though the transaction overall matches.

## Counterexamples
None found — every node type's transaction-vs-posting pairing in the code follows this pattern with no exception (other than `Tag`, covered separately in query-engine-010/011).

## Depends on
query-engine-001.

## Open questions
None for the code-behavior claim itself; the docstring's framing as mirroring hledger's exact matching rule is a fidelity claim not independently re-verified here.

## Evidence-support state
supported
## Status
verified
## Supersedes

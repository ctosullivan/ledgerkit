<!-- producer: assertion-research | topic: query-engine | dispatch: qe-accountsmode-011 | date: 2026-10-02 -->
# Assertion: query-engine-011

## Statement
`_matches_posting_for_accounts` is a second, private posting-matcher used only by `ledgerkit.reports.accounts` that is identical to `matches_posting` for every node type except `Tag`: it sources tags via a narrower "accounts effective tags" function instead of the full effective-tags union, which excludes the posting's own literal tags and commodity-propagated tags — visible sources are narrowed to transaction-own tags plus account-inherited tags only. Both functions share one recursive `And`/`Or`/`Not` dispatch body (`_matches_posting_impl`), parameterized by which tag-source function to call, rather than being two independently-maintained copies.

## Kind
relationship
## Basis
directly_stated
## Evidence
`_matches_posting_impl`'s signature takes a `tag_source: _TagSourceFn` parameter (eval.py lines 143-149, 165-168) used only in the `Tag` branch; `matches_posting` (lines 178-195) calls it with the full effective-tags function, while `_matches_posting_for_accounts` (lines 198-214) calls it with the narrower accounts-mode function. `test_eval.py::TestTagAccountsMode` (lines 276-322) directly confirms: `test_transaction_level_visible` and `test_account_inherited_visible` are True under the accounts-mode function, but `test_posting_own_not_visible` and `test_commodity_propagated_not_visible` are False under it — while `test_ordinary_matches_posting_still_sees_all_four` confirms the *same* fixture under ordinary `matches_posting` sees all four sources, proving the narrowing is genuinely opt-in and doesn't leak into the regular code path.

Evidence-paths: [ledgerkit/query/eval.py:143-214, tests/test_query/test_eval.py:276-322]

## Justification
This is the one deliberate, documented exception to "one canonical effective-tags view" in the whole engine — worth isolating as its own assertion since a reader skimming only `matches_posting` would never discover this narrower mode exists or that another reports command uses it.

## Examples
Fixture (test_eval.py lines 281-292): account `assets:bank` declares `rate=3`; commodity `$` declares `rate=2`; transaction declares `rate=4`; posting declares `rate=1`. Under `_matches_posting_for_accounts`: `rate=4` and `rate=3` match; `rate=1` and `rate=2` do not.

## Counterexamples
None found.

## Depends on
query-engine-004, query-engine-010.

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes

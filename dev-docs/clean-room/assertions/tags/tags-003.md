<!-- producer: assertion-research | topic: tags | dispatch: tags-r3 | date: 2026-10-02 -->
# Assertion: tags-003

## Statement
A second, narrower effective-tag computation, `_accounts_effective_tags`, exists specifically for hledger's `accounts` command's tag-matching path: it unions only the transaction's own tags and the posting-account's inherited (declared ancestor) tags, explicitly EXCLUDING the posting's own literal comment tags and any commodity-propagated tags that `_effective_tags` would include.

## Kind
rule

## Basis
directly_stated

## Evidence
`_accounts_effective_tags` (tags.py:240-257) docstring: "Unions only `txn`'s own tags and `posting.account`'s inherited tags — explicitly excluding `posting`'s own literal comment tags and any commodity-propagated tags." Its return statement is `txn.tags + _inherited_account_tags(journal, posting.account)`, omitting `posting.tags` and `_commodity_tags(...)` entirely, in contrast to `_effective_tags`'s four-term sum.

Evidence-paths: [ledgerkit/tags.py:240-257]

## Justification
Direct code comparison: `_effective_tags` sums four terms; `_accounts_effective_tags` sums only two of those same four terms (txn tags, inherited account tags), with the other two (posting tags, commodity tags) omitted by design per its own docstring.

## Examples
`test_excludes_posting_own_and_commodity_tags` (test_tags.py:281-300) uses the identical journal/txn/posting fixture as `TestEffectiveTags` (posting tag `rate:1`, txn tag `rate:4`, account tag `rate:3`, commodity tag `rate:2`) and asserts `_accounts_effective_tags` returns only `[("rate","4"), ("rate","3")]` — i.e. txn + account tags, with posting's `rate:1` and commodity's `rate:2` both absent.

## Counterexamples
None found.

## Depends on
tags-001, `_inherited_account_tags` (tags-004).

## Open questions
The docstring says this is "Used only by `ledgerkit.reports.accounts`'s `Tag`-matching path, via `ledgerkit.query.eval`'s accounts-mode dispatch" — this consumer relationship is stated in tags.py's own comment but not independently verifiable from the permitted evidence (reports.py/query.py are out of scope for this research).

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

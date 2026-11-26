<!-- producer: assertion-research | topic: tags | dispatch: tags-r1 | date: 2026-10-02 -->
# Assertion: tags-001

## Statement
Tags can be declared/contributed from exactly four sources that feed into a posting's effective tag set: (1) a posting's own inline-comment `name:value` tags (`Posting.tags`), (2) a transaction's own inline-comment tags (`Transaction.tags`), (3) declared account tags on the posting's account or any ancestor account (`Journal.declared_account_tags`, walked via `_inherited_account_tags`), and (4) declared commodity tags for the commodity used in the posting's amount (`Journal.declared_commodity_tags`, via `_commodity_tags`).

## Kind
definition

## Basis
directly_stated

## Evidence
`_effective_tags` (tags.py:210-237) is documented as "the full, four-source union of tags effectively visible on `posting`" and its return statement literally concatenates `posting.tags + txn.tags + _inherited_account_tags(...) + _commodity_tags(...)`. The module docstring (tags.py:1-21) also states `parser.py` populates `inline_comment` for "a transaction's/posting's/account-directive's/commodity-directive's" comment text, confirming all four declaration sites exist at the parser level.

Evidence-paths: [ledgerkit/tags.py:1-21, ledgerkit/tags.py:210-237]

## Justification
The docstring explicitly names the four sources and the code's return expression is a direct, unconditional sum of four function/attribute results, each traceable to one declaration site (posting comment, transaction comment, account directive via inheritance, commodity directive).

## Examples
`test_unions_all_four_sources_with_no_dedup_by_name` (test_tags.py:259-263) constructs a posting with its own tag, a transaction with its own tag, a declared account tag on `assets:bank`, and a declared commodity tag on `$`, and asserts all four appear in the result.

## Counterexamples
None found — no test exercises a fifth source (e.g. default/global tags) feeding `_effective_tags`.

## Depends on
`Posting.tags`, `Transaction.tags`, `Journal.declared_account_tags`, `Journal.declared_commodity_tags` (model fields referenced but not defined in tags.py itself; resolved only insofar as tags.py's own type comments and usage require).

## Open questions
None within the permitted evidence.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

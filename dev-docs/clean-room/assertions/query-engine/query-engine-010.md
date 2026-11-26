<!-- producer: assertion-research | topic: query-engine | dispatch: qe-tageval-010 | date: 2026-10-02 -->
# Assertion: query-engine-010

## Statement
`Tag` matching against a posting uses the full "effective tags" of that (transaction, posting) pair — the union of four independent sources with NO shadowing/dedup-by-name: the posting's own literal tags, the transaction's own literal tags (propagated onto every posting), the posting's account's declared-and-inherited tags (including from strict ancestor accounts), and the posting's main amount's commodity's declared tags. Same-named tags with different values from different sources are all independently matchable. At the transaction level, `Tag` matches if the transaction's own tags directly match OR if ANY posting's effective tags match (both checked independently, not merely one delegating to the other).

## Kind
rule
## Basis
directly_stated
## Evidence
`Tag`'s docstring (ast.py lines 117-141) defines "effective tags" as this four-source union and states both are "case-insensitive infix matches." `matches_transaction`'s `Tag` branch (eval.py lines 128-133): `if _tag_matches(node, txn.tags): return True; return any(_tag_matches(node, _effective_tags(journal, txn, p)) for p in txn.postings)` — an explicit two-part OR, confirming both halves are real, independent checks. `test_eval.py::TestTag::test_no_shadowing_all_four_values_independently_matchable` (lines 211-220) is built exactly to catch "a naive dedup-by-name implementation" and asserts all four values (`"1"`,`"2"`,`"3"`,`"4"`) independently match the same posting. `test_transaction_level_matches_directly_even_without_a_matching_posting` and `test_transaction_level_matches_via_any_posting_effective_tags` (lines 246-256) confirm the two-part transaction-level OR directly.

Evidence-paths: [ledgerkit/query/ast.py:117-141, ledgerkit/query/eval.py:100-140, tests/test_query/test_eval.py:159-260]

## Justification
This no-shadowing design is explicitly flagged in both the docstring and the test suite as the single most counterintuitive property of tag matching — most tag systems would conflate same-named tags into one "winning" value, but this engine deliberately treats each source as an independent fact to be matched against.

## Examples
Fixture in `test_eval.py::TestTag.setUp` (lines 166-187): account `assets:bank` declares `rate=3`; commodity `$` declares `rate=2`; the transaction header carries `rate=4`; the posting itself carries `rate=1`. `matches_posting(Tag("rate", v), ...)` is True for every `v` in `{"1","2","3","4"}`.

## Counterexamples
`test_unrelated_account_does_not_inherit` (lines 222-225): a posting on `equity:opening-balances` (no declared `rate` tag on that account) does NOT match `tag:rate=3` via account inheritance — but `test_unrelated_account_still_sees_commodity_tag` (227-233) shows that same posting DOES still match `tag:rate=2` because commodity propagation is keyed by commodity, not account.

## Depends on
query-engine-004, query-engine-011.

## Open questions
The underlying "effective tags" computation itself lives outside the permitted evidence paths for this research pass — this assertion documents only how `eval.py`'s `Tag` branch *consumes* that function's result, not its internal account-inheritance/commodity-propagation algorithm.

## Evidence-support state
supported
## Status
verified
## Supersedes

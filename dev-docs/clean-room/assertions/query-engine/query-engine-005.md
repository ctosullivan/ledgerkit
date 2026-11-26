<!-- producer: assertion-research | topic: query-engine | dispatch: qe-combine-005 | date: 2026-10-02 -->
# Assertion: query-engine-005

## Statement
After tokenizing, `parse()` buckets predicate terms by node type: all unnegated `Acct` terms are OR'd together into one `Or(...)` bucket, all unnegated `Desc` terms into another, all unnegated `Status` terms into another; every other term — `DateSpan`, `Tag`, `MaxAccountLevel` (not reachable from text anyway), and crucially *any* `Not`-wrapped term regardless of its inner prefix — goes into a flat list that is AND'd in individually alongside the three OR buckets. A `Not(Acct(...))` is never pulled into the `Acct` OR-bucket even when unnegated `Acct` terms are also present.

## Kind
rule
## Basis
directly_stated
## Evidence
`parser.py` lines 349-374: `acct_terms`/`desc_terms`/`status_terms` are filtered by `isinstance(t, Acct/Desc/Status)` from `predicate_terms` (which by construction never contains a raw `Not`-stripped node — `Not` objects themselves fail all three isinstance checks and land in `other_terms`); `buckets` is built from `Or(tuple(...))` per non-empty type-bucket, then `And(tuple(buckets + other_terms))`, simplified via `_simplify`. Test confirmation: `test_negated_same_prefix_terms_are_anded_not_ored` (test_parser.py lines 222-230) — `parse("not:acct:a not:acct:b").predicate == And((Not(Acct("a")), Not(Acct("b"))))`, not an `Or`. `test_mixed_negated_and_unnegated_same_prefix` (lines 232-236) confirms `"acct:a acct:b not:acct:c"` → `And((Or((Acct("a"), Acct("b"))), Not(Acct("c"))))`.

Evidence-paths: [ledgerkit/query/parser.py:349-375, tests/test_query/test_parser.py:184-236]

## Justification
The parser's own comment (lines 349-360) states this "replicates hledger's own `combineQueriesByType`" and frames the negated-same-prefix case as "the central footgun" — getting this wrong would turn a double-exclusion query into a near-tautology.

## Examples
`"acct:a acct:b"` → `Or((Acct("a"), Acct("b")))`; `"date:2022-01-01.. desc:amazon"` → `And((Desc("amazon"), DateSpan(...)))`; `"tag:a tag:b"` → `And((Tag("a", None), Tag("b", None)))` (tag: is never one of the three OR-eligible prefixes, so multiple `tag:` terms AND automatically with zero special-case code).

## Counterexamples
None found; single-term buckets are flattened by `_simplify` (e.g. a lone `Acct` term is not wrapped in a one-element `Or`).

## Depends on
query-engine-001.

## Open questions
The claim that this precisely replicates hledger's real `combineQueriesByType` function is sourced from an out-of-scope planning document and was not independently re-verified against the hledger binary in this research pass; only the code's own (self-consistent, well-tested) behavior was confirmed directly.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes

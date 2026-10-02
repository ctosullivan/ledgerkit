<!-- producer: assertion-research | topic: query-engine | dispatch: qe-depthextract-003 | date: 2026-10-02 -->
# Assertion: query-engine-003

## Statement
`depth:N` / `depth:REGEX=N` query terms are never inserted into the selection-predicate `And`/`Or` tree. `parse()` intercepts every token starting with `depth:` before the combination step, merges it into an accumulator `DepthSpec` via `merge_depth_specs`, and returns it on `QueryPlan.depth`; the remaining predicate is built only from the other tokens. A query consisting solely of `depth:` terms produces `predicate == And(())` (the vacuous "match everything" node).

## Kind
invariant
## Basis
directly_stated
## Evidence
`parser.py` lines 318-346: the `for token in tokens` loop in `parse()` checks `if token.startswith("depth:")` first and `continue`s after merging into `depth_spec`, so such tokens never reach `predicate_terms.append(...)`. `test_parser.py::TestDepthSpec::test_depth_prefix_produces_flat_depthspec_not_a_predicate_node` (lines 55-58) asserts `plan.predicate == And(())` for `parse("depth:2")`. `test_different_prefixes_are_anded` (lines 206-220) parses `"date:2022-01-01.. desc:amazon depth:2"` and asserts the predicate contains only `Desc`/`DateSpan`, with `depth:2` surfacing solely as `plan.depth == DepthSpec(flat=2)`.

Evidence-paths: [ledgerkit/query/parser.py:318-346, tests/test_query/test_parser.py:55-58, tests/test_query/test_parser.py:206-220]

## Justification
This separation is load-bearing for `eval.py`, which has no `DepthSpec`-handling branch at all in its dispatch — if a `depth:` term ever leaked into the predicate tree, `matches_transaction`/`matches_posting` would hit the `TypeError("unhandled query node type")` fallback.

## Examples
`parse("depth:2").predicate == And(())`; `parse("acct:food depth:1").predicate == Acct("food")` (single remaining term, simplified by `_simplify`).

## Counterexamples
None found in the parser or tests.

## Depends on
query-engine-001, query-engine-014 (DepthSpec merge semantics).

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes

<!-- producer: assertion-research | topic: query-engine | dispatch: qe-maxlevel-002 | date: 2026-10-02 -->
# Assertion: query-engine-002

## Statement
`MaxAccountLevel` is reachable only via direct Python construction (`MaxAccountLevel(n)`) — the string-query parser (`parser.py`) has no prefix or token shape that ever produces one. It is evaluated as "posting's colon-segment depth is at or below `n`" using an any-posting rule at the transaction level, the same combinator pattern used for `Acct`.

## Kind
boundary
## Basis
directly_stated
## Evidence
`MaxAccountLevel`'s docstring (ast.py lines 81-105) states: "Python-API-only: there is no `-q`/`--query` string-syntax spelling for this node — `ledgerkit.query.parser.parse()` never produces one; it is reachable only by constructing `MaxAccountLevel(n)` directly." `parser.py`'s `_PREFIX_BUILDERS` dict (lines 274-280) contains only `acct:`, `desc:`, `date:`, `status:`, `tag:` — no `depth`-adjacent builder targets `MaxAccountLevel`; `depth:` tokens are instead routed to `_build_depth_spec`, which returns a `DepthSpec`, never a `QueryNode`. `test_eval.py`'s `TestMaxAccountLevel` class (lines 88-109) constructs the node directly and its own comment states "No `-q` string form exists for it; these tests construct the node directly."

Evidence-paths: [ledgerkit/query/ast.py:81-107, ledgerkit/query/parser.py:274-280, tests/test_query/test_eval.py:88-109]

## Justification
Grepping `parser.py`'s builder table and tokenizer logic confirms no code path constructs `MaxAccountLevel`; this is a genuine dead end from string-query input, by design, not an oversight — the docstring explicitly distinguishes it from hledger's own `depth:`/`--depth` (a report-display option, modeled separately by `DepthSpec`).

## Examples
`matches_transaction(MaxAccountLevel(1), txn)` is True if any posting's account has 1 colon-segment level; `MaxAccountLevel(2)` on an `expenses:food:groceries` (level 3) posting alone is False.

## Counterexamples
None — confirmed no builder emits this node type.

## Depends on
query-engine-001.

## Open questions
The docstring's rationale ("confirmed across every real hledger command that depth: is always a report-display option") cites a planning document out of scope for this research pass; the underlying hledger-fidelity claim for that design decision was not independently re-verified here.

## Evidence-support state
supported
## Status
verified
## Supersedes

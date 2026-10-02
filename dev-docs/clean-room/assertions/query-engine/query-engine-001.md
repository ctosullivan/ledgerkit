<!-- producer: assertion-research | topic: query-engine | dispatch: qe-ast-001 | date: 2026-10-02 -->
# Assertion: query-engine-001

## Statement
The query AST (`ledgerkit/query/ast.py`) defines exactly nine node/container types — `Acct`, `Desc`, `DateSpan`, `MaxAccountLevel`, `Status`, `Tag`, `And`, `Or`, `Not` — unioned into the `QueryNode` type alias, plus a top-level `QueryPlan` dataclass that pairs a `predicate: QueryNode` with a separate `depth: DepthSpec` field (default empty). All nine node types are frozen dataclasses; none of them perform validation or evaluation themselves.

## Kind
definition
## Basis
directly_stated
## Evidence
`ast.py` module docstring (lines 1-17) states the node set mirrors hledger's query term set for "acct:, desc:, date: (simple dates only), status:, tag:NAME[=REGEX] ... and not:/implicit-AND/same-prefix-OR combination" and that `depth:` is deliberately excluded as a node. Each class is declared `@dataclass(frozen=True)`. `QueryNode = Union[Acct, Desc, DateSpan, MaxAccountLevel, Status, Tag, And, Or, Not]` at line 171. `QueryPlan` at lines 174-189 has fields `predicate: "QueryNode"` and `depth: DepthSpec = field(default_factory=DepthSpec)`.

Evidence-paths: [ledgerkit/query/ast.py:1-17, ledgerkit/query/ast.py:45-188, ledgerkit/query/__init__.py:22-46]

## Justification
This is the structural foundation every other query-engine claim depends on — the parser only ever constructs these nine types, and the evaluator's dispatch is an exhaustive `isinstance` chain over exactly this set (confirmed by the `TypeError` fallback in `eval.py` for "unhandled query node type").

## Examples
`Acct("groceries")`, `And((Acct("a"), Desc("b")))`, `QueryPlan(predicate=Not(Status(TxnStatus.CLEARED)), depth=DepthSpec(flat=2))`.

## Counterexamples
None found — no tenth node type exists in the file: `__init__.py`'s own import from `ast.py` (line 16) brings in exactly the same nine node classes plus `TxnStatus`/`QueryNode`/`QueryPlan`, nothing more.

(Reviewed 2026-10-03: the original draft additionally claimed "`__init__.py`'s `__all__` export list matches this same set exactly." That claim was checked directly against `ledgerkit/query/__init__.py:22-46` and is **false** — `__all__` is a strict superset of the nine node types, not an exact match: it also exports `TxnStatus`, `QueryNode`, `QueryPlan`, `DepthSpec`, and eight functions/exceptions (`clipped_depth_for_account`, `clip_account_name`, `merge_depth_specs`, `parse`, `QueryParseError`, `matches_transaction`, `matches_posting`, `validate_hledger_regex`, `compile_hledger_regex`, `UnsupportedRegexConstructError`). The underlying "no tenth node type" claim this was meant to support still holds (see above), so the core Statement is unaffected — only this specific over-claimed phrasing was removed.)

## Depends on
query-engine-003 (depth is excluded from the predicate tree, carried separately on `QueryPlan.depth`).

## Open questions
None for the structural claim itself.

## Evidence-support state
supported
## Status
verified
## Supersedes

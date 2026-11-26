<!-- producer: assertion-research | topic: query-engine | dispatch: qe-compatshim-015 | date: 2026-10-02 -->
# Assertion: query-engine-015

## Statement
`ledgerkit.query.compat._query_to_ast` translates the legacy `Query` dataclass (fields: `account`, `not_account`, `payee`, `date_from`, `date_to`, `depth`) into the same `QueryNode` tree the string parser produces, so that every `Query`-shaped filter in `ledgerkit/` is evaluated by the one canonical `eval.py` engine instead of a separate ad hoc matcher. Field mapping: `account` → `Acct`, `not_account` → `Not(Acct(...))`, `payee` → `Desc`, `date_from`/`date_to` → one `DateSpan` (only emitted if either is set). `query.depth` is NEVER consulted or translated into any node. Each pattern field is eagerly validated via `_validated` (which wraps `compile_hledger_regex` and re-raises as `QueryParseError`) at translation time, not lazily deferred. `Query.date_to` is inclusive; `_exclusive_end` converts it to `DateSpan`'s exclusive-end convention by adding one day, except `datetime.date.max` (which has no representable successor) maps to `None` instead of raising `OverflowError`.

## Kind
rule
## Basis
directly_stated
## Evidence
`_query_to_ast` (compat.py lines 94-125): the `if query.account is not None: terms.append(Acct(_validated(...)))` etc. pattern for each field, and the trailing comment "`query.depth` is deliberately excluded -- never a predicate." `_validated` (lines 49-72) catches `(ValueError, re.error)` and re-raises `QueryParseError`. `_exclusive_end` (lines 75-91): `if date_to == datetime.date.max: return None`, else `date_to + timedelta(days=1)`. Test confirmation: `test_compat.py::TestQueryToAstEmptyCases::test_depth_only_query_returns_none` (lines 30-34) — `Query(depth=2)` → `None`; `TestQueryToAstSingleFields::test_depth_never_appears_alongside_other_fields` (lines 59-62); `TestExclusiveEnd::test_date_max_maps_to_none_not_overflow` (lines 144-145); `TestQueryToAstEagerValidation` (lines 162-185) confirms malformed/empty patterns raise `QueryParseError` at translation time, before any evaluation occurs.

Evidence-paths: [ledgerkit/query/compat.py:35-125, tests/test_query/test_compat.py:20-185]

## Justification
The module docstring (compat.py lines 1-33) frames this as ending a specific, named duplication problem: `reports.py` previously had its own ad hoc, non-hledger-faithful matching helpers running in parallel with the real query engine.

## Examples
`_query_to_ast(Query(account="food", not_account="restaurant"))` → `And((Acct("food"), Not(Acct("restaurant"))))`. `_query_to_ast(Query(date_to=datetime.date(2024,1,31)))` → `DateSpan(start=None, end=datetime.date(2024,2,1))`.

## Counterexamples
None found — every tested field combination and both `date.max`/ordinary-date branches of `_exclusive_end` behave exactly as documented.

## Depends on
query-engine-001, query-engine-003.

## Open questions
This module's correctness ultimately depends on the behavior of its callers elsewhere in `ledgerkit/` — out of scope for this research pass, so the claim that "every `Query`-shaped filter now goes through this translator" could not be independently confirmed from the caller side; only the translator's own input/output contract was verified.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes

<!-- producer: assertion-research | topic: query-engine | dispatch: qe-splitfirst-008 | date: 2026-10-02 -->
# Assertion: query-engine-008

## Statement
Both `depth:REGEX=N` (`_build_depth_spec`) and `tag:NAME=REGEX` (`_build_tag`) split their value on the FIRST `=` character only (`str.partition("=")`), so a value containing a literal `=` after the first one is preserved verbatim in the right-hand side (e.g. `tag:rate==0.05` → `Tag("rate", "=0.05")`, a tag literally named `rate` with value `=0.05`). Separately, `not:depth:...` (in any number of `not:` wraps) is rejected at parse time with `QueryParseError` — depth cannot be negated, because it is a report option rather than a predicate node.

## Kind
rule
## Basis
directly_stated
## Evidence
`_build_depth_spec` (parser.py lines 215-227) and `_build_tag` (lines 230-245) both use `value.partition("=")`, with comments at lines 216-219 and 231-237 explicitly calling out "split on the FIRST '=' only." `test_value_containing_equals_preserves_everything_after_first` (test_parser.py lines 262-267) confirms `_pred("tag:rate==0.05") == Tag("rate", "=0.05")`. The `_wraps_depth` helper (parser.py lines 283-291) strips repeated `not:` prefixes looking for a `depth:` tail; `parse()` (lines 342-346) raises `QueryParseError` if `_wraps_depth(token)` is true. `test_not_depth_rejected` and `test_double_not_depth_rejected` (test_parser.py lines 104-113) confirm both `not:depth:2` and `not:not:depth:2` raise.

Evidence-paths: [ledgerkit/query/parser.py:215-245, ledgerkit/query/parser.py:283-346, tests/test_query/test_parser.py:104-113, tests/test_query/test_parser.py:262-267]

## Justification
Without the explicit `_wraps_depth` check, `not:depth:2` would otherwise fall through `_parse_term`'s `not:`-stripping recursion and attempt to build `Not(_build_acct("depth:2"))` or similar — the explicit rejection prevents a silent, wrong reinterpretation.

## Examples
`tag:rate=3` → `Tag("rate", "3")`; `tag:rate==0.05` → `Tag("rate", "=0.05")`; `depth:assets=2` → `DepthSpec(by_pattern=(("assets", 2),))`; `not:depth:2` raises `QueryParseError`.

## Counterexamples
None found.

## Depends on
query-engine-003.

## Open questions
None.

## Evidence-support state
supported
## Status
verified
## Supersedes

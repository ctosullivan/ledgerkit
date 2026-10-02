<!-- producer: assertion-research | topic: query-engine | dispatch: qe-emptypattern-013 | date: 2026-10-02 -->
# Assertion: query-engine-013

## Statement
`validate_hledger_regex` rejects two additional pattern shapes beyond the construct exclusions: (1) the literal empty string `""` (but NOT a pattern whose semantics merely *admit* an empty match, like `.*`, `a*`, `^$`, or `()`, which remain valid); and (2) any pattern containing an unescaped `|` with nothing (zero raw, unescaped characters) immediately on one side of it — e.g. `a|`, `|a`, `(|)`, `a||b`, `(a|)`, `(|a)` — detected by a dedicated escape-aware linear scan (`_has_empty_alternation_branch`) rather than a single compiled regex, because telling a real `|` apart from an escaped `\|` requires variable-length backslash-run parity counting that Python's fixed-width-lookbehind `re` cannot express. Anchor-only branches (`^|a`, `a|$`) and escaped pipes/parens (`a\|\|b`) are explicitly NOT rejected by this check. Both rejections are documented as breaking changes from this module's own earlier behavior.

## Kind
rule
## Basis
directly_stated
## Evidence
`validate_hledger_regex` (regex.py lines 215-262): `if pattern == "": raise ...` and `if _has_empty_alternation_branch(pattern): raise ...`, both before the construct-exclusion check. The function's own docstring (lines 222-241) explicitly labels both as "Breaking change." `_has_empty_alternation_branch`'s algorithm and edge cases are documented at length (lines 92-184). `test_regex.py::TestEmptyPattern` (102-125), `TestEmptyMatchingPatternsRemainAccepted` (128-149), `TestEmptyAlternationBranchRejected` (152-231, 18 individually named rejection cases), and `TestEmptyAlternationBranchAccepted` (234-278, 13 individually named acceptance regression-guards) directly exercise this exact boundary.

Evidence-paths: [ledgerkit/query/regex.py:92-184, ledgerkit/query/regex.py:215-262, tests/test_query/test_regex.py:102-278]

## Justification
The dedicated algorithm comment explains *why* a compiled regex could not express this rule at all — a design justification, not merely a behavior description — and the breaking-change callouts in the docstring signal this is a place where past Ledgerkit behavior diverged from real hledger and was later corrected, making it a regression-prone area worth flagging explicitly.

## Examples
`validate_hledger_regex("")` raises; `validate_hledger_regex(".*")` does not raise. `validate_hledger_regex("a|")` raises; `validate_hledger_regex("a|b")` does not. `validate_hledger_regex(r"a\|\|b")` (escaped pipes) does not raise.

## Counterexamples
None found within the documented test matrix — both the 18-pattern reject-list and 13-pattern accept-list pass as asserted.

## Depends on
query-engine-012.

## Open questions
Both rejection rules are explicitly justified by reference to a pinned hledger binary and named compat-register entries/planning docs, all out of scope for this research pass. Whether these rules in fact match real hledger's regex-tdfa rejection behavior was not independently re-verified here; that classification needs a separate compat-differential check.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes

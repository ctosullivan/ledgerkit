<!-- producer: assertion-research | topic: query-engine | dispatch: qe-regexdialect-012 | date: 2026-10-02 -->
# Assertion: query-engine-012

## Statement
`validate_hledger_regex`/`compile_hledger_regex` implement a restricted dialect ("HledgerRegex") on top of Python's `re`: patterns are rejected (raising `UnsupportedRegexConstructError`, a `ValueError` subclass) if they contain any `(?...)` construct (inline flags, named/non-capturing groups, lookaround), a numeric backreference (`\1`-`\9`), a GNU word-boundary escape (`\<`/`\>`), a Perl shorthand class (`\d`/`\D`/`\w`/`\W`/`\s`/`\S`), a POSIX named class (`[[:alpha:]]`-style), or a lazy/non-greedy quantifier (`*?`/`+?`/`??`). Everything else Python's `re` accepts passes through unexcluded. A pattern that merely fails Python regex syntax entirely raises a bare `re.error` from `compile_hledger_regex`, separate from the construct-exclusion check.

## Kind
rule
## Basis
directly_stated
## Evidence
`_EXCLUDED_CONSTRUCT` (regex.py lines 83-90) and its accompanying comment (lines 35-90) enumerate exactly these six excluded families with named capture groups used to build a precise error message via `_CONSTRUCT_MESSAGES` (lines 187-212). `test_regex.py::TestValidPatterns` (lines 14-47) confirms plain literals, `.`, `|`, anchors, `{1,3}`, groups, `[abc]`/`[^abc]`, and `\b` all validate successfully. `TestExcludedConstructs` (lines 50-99) confirms each of the six families is rejected, one test per construct. `compile_hledger_regex`'s docstring (lines 265-277) states matching compiles with `re.IGNORECASE` always.

Evidence-paths: [ledgerkit/query/regex.py:35-90, ledgerkit/query/regex.py:215-277, tests/test_query/test_regex.py:14-99]

## Justification
The module's governing design principle (stated at lines 6-13) is that it "never silently reinterprets a pattern using Python semantics where the two differ" — e.g. `\1` means a real backreference in Python but a literal digit "1" in hledger's regex-tdfa, so accepting it unmodified would silently change the pattern's meaning rather than merely being "unsupported." This is why the module raises rather than translating or ignoring these constructs.

## Examples
`validate_hledger_regex("food|rent")` passes; `validate_hledger_regex(r"(foo)\1")`, `validate_hledger_regex(r"\d+")`, and `validate_hledger_regex("(?i)food")` each raise `UnsupportedRegexConstructError`.

## Counterexamples
None found within the tested construct list; `_EXCLUDED_CONSTRUCT`'s own comment (lines 74-82) acknowledges a known false-negative gap: a literal `\\` followed by a digit is not distinguished from a real backreference by this scan — the comment calls this "safe" (false positives only reject patterns Python could otherwise run) and states no false negatives are known for the targeted constructs.

## Depends on
query-engine-001.

## Open questions
The claim that this construct list is the *complete and correct* hledger-regex-tdfa-vs-Python-re divergence set is sourced from out-of-scope planning documents and was not independently re-verified against real hledger or regex-tdfa documentation here.

## Evidence-support state
partially_supported
## Status
verified
## Supersedes

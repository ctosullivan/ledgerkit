<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-009 | date: 2026-10-03 -->
<!-- reviewed: domain-skeptic | 2026-10-03 | resolved open-question finding, see _review.md -->
# Assertion: compat-system-009

## Statement
Entry LK-COMPAT-QUERY-REGEX-EMPTYALT-001 (kind: compatible, status: verified) both resolves a prior mismatch (`resolves: LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`) and cites four test identifiers; all four were independently confirmed to exist: `tests/test_query/test_regex.py::TestEmptyAlternationBranchRejected`, `tests/test_query/test_regex.py::TestEmptyAlternationBranchAccepted`, `tests/test_query/test_parser.py::TestEmptyAlternationBranchRejectedAtParseTime`, `tests/test_cli/test_cli.py::TestQueryFlag::test_empty_alternation_branch_exits_one`.

## Kind
boundary
## Basis
directly_stated
## Evidence
LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml line 24: `resolves: LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`; tests section cites `tests/test_query/test_regex.py::TestEmptyAlternationBranchRejected`, `...::TestEmptyAlternationBranchAccepted`, `tests/test_query/test_parser.py::TestEmptyAlternationBranchRejectedAtParseTime`, `tests/test_cli/test_cli.py::TestQueryFlag::test_empty_alternation_branch_exits_one`. Grep confirmed all four: `tests/test_query/test_regex.py:152:class TestEmptyAlternationBranchRejected(unittest.TestCase):`; `tests/test_query/test_regex.py:234:class TestEmptyAlternationBranchAccepted(unittest.TestCase):`; `tests/test_query/test_parser.py:367:class TestEmptyAlternationBranchRejectedAtParseTime(unittest.TestCase):`; `tests/test_cli/test_cli.py:340:class TestQueryFlag(unittest.TestCase):` with `:483:    def test_empty_alternation_branch_exits_one(self):` nested inside it (no intervening `class` line between 340 and 483, confirmed by scanning that line range for `^class `).

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml:24, tests/test_query/test_regex.py:152, tests/test_query/test_regex.py:234, tests/test_query/test_parser.py:367, tests/test_cli/test_cli.py:340, tests/test_cli/test_cli.py:483]

## Justification
This entry is one of only two live entries exercising the resolution-lifecycle mechanism (compat-system-005), making it a load-bearing example of that mechanism in practice, not just a routine compatibility claim.
## Examples
The entry's own header comment states it was "Promoted to status: verified 2026-09-27 by a genuinely separate compat-differential-tester dispatch ... which independently re-derived the full 18-must-reject/13-must-accept matrix" — a specific, falsifiable claim about test matrix size that is corroborated by the `evidence:` field's own "935 tests total in the full suite" figure.
## Counterexamples
None — all four cited test identifiers confirmed to exist, including correct class/method nesting for the two `::`-qualified compound citations.
## Depends on
compat-system-005 (resolution lifecycle).
## Open questions
(resolved by review — see below) Originally: only 1 of the 4 cited test identifiers had been independently confirmed; the other 3 were not separately grepped due to time/scope balance across the full assertion set. Domain-skeptic review (2026-10-03) ran the remaining existence checks within the same permitted evidence paths (tests/, existence-only) and confirmed all 4. Whether the methods' bodies actually assert the specific 18-reject/13-accept matrix claimed in Examples remains unchecked (would require reading method bodies, which the existence-only rule prohibits) — that narrower question is still open, but it was never part of this assertion's Statement.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

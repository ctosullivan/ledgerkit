<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-006 | date: 2026-10-03 -->
# Assertion: compat-system-006

## Statement
Entry LK-COMPAT-ACCOUNTDIR-001 (kind: compatible, status: proposed, area: parser.directives.account) claims ledgerkit's `account` directive handling is behaviourally equivalent to hledger's, citing test `tests/test_directives/test_directives.py::TestAccountDirective`. This test class independently confirmed to exist.

## Kind
boundary
## Basis
directly_stated
## Evidence
LK-COMPAT-ACCOUNTDIR-001.yaml lines 33-34: `tests:\n  - tests/test_directives/test_directives.py::TestAccountDirective`. Grep of the permitted test file: `tests/test_directives/test_directives.py:15:class TestAccountDirective(unittest.TestCase):` — found and confirmed, exact line match.

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-ACCOUNTDIR-001.yaml:33-34, tests/test_directives/test_directives.py:15]

## Justification
Existence-only confirmation per task rules: the grep match line was read, nothing else in that test file was inspected. The entry's `evidence` field lists only `kind: manual` (a doc-link) — no executable evidence — consistent with its `status: proposed`.
## Examples
(n/a — single entry)
## Counterexamples
None.
## Depends on
None.
## Open questions
The entry's `implementation:` field cites `ledgerkit/parser.py` — per task hard rules this was not and could not be checked; its accuracy is unverified by this survey.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

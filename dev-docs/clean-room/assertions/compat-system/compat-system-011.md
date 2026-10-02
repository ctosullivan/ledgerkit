<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-011 | date: 2026-10-03 -->
# Assertion: compat-system-011

## Statement
Entry LK-COMPAT-PARSER-POSTINGDATE-001 (kind: compatible, status: self-verified) claims ledgerkit's posting-level `date:`/`date2:` tag override precedence matches hledger's exactly, implemented via pure functions in `ledgerkit/tags.py`. It cites `tests/test_tags.py::TestEffectiveDate` and `::TestEffectiveDate2`, both confirmed to exist in `tests/test_tags.py` — a file that is notable because it is NOT listed anywhere in CLAUDE.md's documented folder-structure tree (which shows only `tests/test_parser/`, `tests/test_directives/`, `tests/test_checks/`, `tests/test_cli/`, `tests/test_loader/`, `tests/test_reports/` + a stray `tests/test_reports.py`).

## Kind
boundary
## Basis
directly_stated
## Evidence
LK-COMPAT-PARSER-POSTINGDATE-001.yaml tests section: `tests/test_tags.py::TestEffectiveDate`, `tests/test_tags.py::TestEffectiveDate2`, `tests/test_parser/test_parser.py::TestPostingDateOverrideTags`. Grep: `tests/test_tags.py:146:class TestEffectiveDate(unittest.TestCase):` and `:158:class TestEffectiveDate2(unittest.TestCase):` — both confirmed.

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-PARSER-POSTINGDATE-001.yaml, tests/test_tags.py:146, tests/test_tags.py:158]

## Justification
The test file's existence was confirmed via `find tests -iname "test_tags*"`, within the permitted "confirm a specific test file/class/method ... actually EXISTS" scope. This is flagged as a minor documentation-drift finding (CLAUDE.md's folder-structure table appears stale relative to the actual tests/ layout) rather than a compat-register defect — the register's own citation is accurate regardless of whether CLAUDE.md's tree reflects it.
## Examples
(n/a — single entry; the folder-structure drift is a side observation, not part of the compat-register's own evidence)
## Counterexamples
None regarding the cited tests' existence.
## Depends on
None.
## Open questions
Whether `tests/test_tags.py` should have a package home like the other `test_*` directories, or is intentionally flat, is a CLAUDE.md-folder-structure question outside this task's scope.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

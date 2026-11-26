<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-007 | date: 2026-10-03 -->
# Assertion: compat-system-007

## Statement
Entry LK-COMPAT-PARSER-TAG-COMMODITY-001 (kind: compatible, status: verified, verified_by: compat-differential-tester) claims commodity-directive comment tags (same-line and indented follow-on) are captured into `Journal.declared_commodity_tags` and propagate to query matching identically to hledger. It cites test `tests/test_directives/test_directives.py::TestCommodityDirectiveTags`, confirmed to exist.

## Kind
boundary
## Basis
directly_stated
## Evidence
LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml tests section: `tests/test_directives/test_directives.py::TestCommodityDirectiveTags`. Grep: `tests/test_directives/test_directives.py:181:class TestCommodityDirectiveTags(unittest.TestCase):` — confirmed.

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml, tests/test_directives/test_directives.py:181]

## Justification
This entry is notable among the surveyed set for explicitly admitting a gap in its own original evidence (its own text: "This entry's original evidence was a Ledgerkit-only internal-state check ... which the schema requires before status can move past proposed") and documenting that compat-differential-tester supplied the missing executable evidence via an observable query-time effect, since hledger exposes no direct dump of its internal tag map. This self-reported evidentiary honesty strengthens confidence in the entry beyond the mere existence of the cited test.
## Examples
The entry's second `executable` evidence item names a fresh, specific fixture file (`tests/fixtures/tags_verify_commodity_directive.journal`) and exact `hledger`/`ledgerkit` commands compared.
## Counterexamples
None found regarding the cited test's existence.
## Depends on
None.
## Open questions
Per task hard rules, the implementation citations and the fixture file's actual contents were not verified.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-010 | date: 2026-10-03 -->
<!-- reviewed: domain-skeptic | 2026-10-03 | resolved open-question finding, see _review.md -->
# Assertion: compat-system-010

## Statement
Entry LK-UNSUP-QUERY-DATE-002 (kind: unsupported, status: proposed, relationship: subset) documents that ledgerkit's query parser deliberately does not implement hledger's smart/relative-date grammar (today, yesterday, quarters, partial dates, etc.) for `date:` queries. Its `implementation:` field is an empty list (`[]`), which is explicitly permitted by schema.md for `kind: unsupported` entries describing something not yet built. Its cited test, `tests/test_query/test_parser.py::TestDateSpans::test_malformed_date_rejected`, was confirmed to exist, including that the method is nested inside the named class.

## Kind
boundary
## Basis
directly_stated
## Evidence
LK-UNSUP-QUERY-DATE-002.yaml: `implementation:\n  []` and `tests:\n  - tests/test_query/test_parser.py::TestDateSpans::test_malformed_date_rejected`. schema.md lines 119-120: "`implementation` and `tests` may be empty for `kind: unsupported` entries describing something not yet built". Grep: `tests/test_query/test_parser.py:131:class TestDateSpans(unittest.TestCase):` and `:179:    def test_malformed_date_rejected(self):` — both confirmed, and scanning lines 131-182 for `^class `/`    def ` signatures found no intervening `class` line between the two, confirming the method is a direct member of `TestDateSpans` and not some other class.

Evidence-paths: [dev-docs/compat-register/LK-UNSUP-QUERY-DATE-002.yaml, dev-docs/compat-register/schema.md:119-120, tests/test_query/test_parser.py:131, tests/test_query/test_parser.py:179]

## Justification
This is a useful counterexample to the general pattern of non-empty implementation/tests fields found elsewhere in the register: the entry is honest about having no implementation (deliberately unbuilt scope) while still citing one real test to cover the rejection boundary.
## Examples
The entry's companion, LK-COMPAT-QUERY-DATE-001, covers the implemented simple-date subset and explicitly cross-references this entry for "the deliberately out-of-scope remainder."
## Counterexamples
None.
## Depends on
compat-system-003 (unsupported-kind count).
## Open questions
(resolved by review — see below) Originally: whether `test_malformed_date_rejected` is a method of `TestDateSpans` specifically (as the `::`-qualified citation implies) had not been confirmed beyond the grep match line itself. Domain-skeptic review (2026-10-03) scanned the signature lines (class/def headers only, no method bodies) between the two grep matches and confirmed no intervening class — the nesting is as cited.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

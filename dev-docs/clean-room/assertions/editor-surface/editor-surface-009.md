<!-- producer: assertion-research | topic: editor-surface | dispatch: edsurf-a9 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: edsurf-review-1 | date: 2026-10-03 -->
# Assertion: editor-surface-009

## Statement
`ledgerkit-editor`'s test suite imports a broader set of `ledgerkit` public/semi-public symbols than its production `src/` code does: `ledgerkit.Query` (top-level), `ledgerkit.models.{Posting, Transaction}`, `ledgerkit.parser.{ParseError, ParseWarning, parse_string_lenient}`, `ledgerkit.commodity_style.CommodityStyle`, and direct calls to `ledgerkit.load()` and `ledgerkit.parse_string_lenient()`. None of these imports reference `editor_model` or `EditorDocument`.

## Kind
relationship

## Basis
directly_stated

## Evidence
From the ledgerkit-editor clone: these are literal import statements found in its test files.

Evidence-paths: [/tmp/ledgerkit-editor-research-clone-2/tests/test_query_match.py:11-12, /tmp/ledgerkit-editor-research-clone-2/tests/test_comprehensive_hledger.py:22-23, /tmp/ledgerkit-editor-research-clone-2/tests/test_commodity_format.py:18, /tmp/ledgerkit-editor-research-clone-2/tests/test_commodity_format.py:88, /tmp/ledgerkit-editor-research-clone-2/tests/test_commodity_format.py:120, /tmp/ledgerkit-editor-research-clone-2/tests/test_commodity_format.py:125, /tmp/ledgerkit-editor-research-clone-2/tests/test_commodity_format.py:193]

## Justification
`test_query_match.py` line 11 reads `from ledgerkit import Query` and line 12 reads `from ledgerkit.models import Posting, Transaction` (line 10 is an unrelated `import pytest`). `test_comprehensive_hledger.py` line 22 reads `import ledgerkit` and line 23 reads `from ledgerkit.parser import ParseError, ParseWarning, parse_string_lenient`. `test_commodity_format.py` has four separate deferred imports of `ledgerkit` / `ledgerkit.commodity_style.CommodityStyle` at the cited lines.

## Examples
`test_comprehensive_hledger.py`'s own docstring (lines 1-11) states it "Exercises ledgerkit v0.2.0 features: ParseWarning, Transaction.date2, Posting.cost_raw, new amount formats... and new directives" and loads a fixture via `ledgerkit.load(MAIN_FIXTURE)`.

## Counterexamples
None — `EditorDocument`/`editor_model` is absent from every test file's imports (cross-checked against editor-surface-007's exhaustive grep).

## Depends on
editor-surface-007.

## Open questions
None.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

## Review note
REVIEW (domain-skeptic, 2026-10-03): re-read every cited line directly.
Found an off-by-one in the Justification: it attributed `from ledgerkit
import Query` to line 10 and `from ledgerkit.models import Posting,
Transaction` to line 11 of test_query_match.py, but line 10 is actually
`import pytest` — the two ledgerkit imports are lines 11 and 12. The
original `Evidence-paths` range (`10-12`) still happened to span the
correct lines, so the Statement itself was never wrong, only the
Justification's line-by-line prose and the range's left edge. Fixed both
(Evidence-paths narrowed to `11-12`, Justification corrected) by reading
the file myself; all other cited lines
(test_comprehensive_hledger.py:22-23, test_commodity_format.py:18/88/120/125/193)
checked out exactly as stated, no further changes.

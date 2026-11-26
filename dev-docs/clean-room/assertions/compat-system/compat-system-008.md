<!-- producer: assertion-research | topic: compat-system | dispatch: compat-reg-008 | date: 2026-10-03 -->
# Assertion: compat-system-008

## Statement
Entry LK-COMPAT-QUERY-DEPTH-001 (kind: compatible, status: verified) cites ten distinct test identifiers spanning four test files/directories (tests/test_query/test_parser.py, tests/test_query/test_eval.py, tests/test_reports.py, tests/test_cli/test_cli.py). All ten were independently checked and all ten exist exactly as named.

## Kind
boundary
## Basis
directly_stated
## Evidence
Cited: TestDepthSpec (test_query/test_parser.py), TestMaxAccountLevel (test_query/test_eval.py), TestQueryAstIntegration::{test_balance_query_depth_truncates_rather_than_excludes, test_balance_query_depth_custom_regex, test_accounts_query_depth_clips_and_deduplicates, test_register_query_depth_clips_label_never_excludes} (test_reports.py), TestQueryFlag::{test_balance_query_depth_truncates, test_balance_query_depth_zero_shows_ellipsis_row, test_balance_query_depth_custom_regex, test_print_ignores_depth_entirely} (test_cli/test_cli.py). Grep confirmed every one: test_query/test_parser.py:49 `class TestDepthSpec`; test_query/test_eval.py:88 `class TestMaxAccountLevel`; test_reports.py:1274 `class TestQueryAstIntegration`, :1300/:1322/:1332/:1342 the four named methods; test_cli/test_cli.py:340 `class TestQueryFlag`, :398/:407/:422/:516 the four named methods.

Evidence-paths: [dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml:127-136, tests/test_query/test_parser.py:49, tests/test_query/test_eval.py:88, tests/test_reports.py:1274, tests/test_reports.py:1300, tests/test_reports.py:1322, tests/test_reports.py:1332, tests/test_reports.py:1342, tests/test_cli/test_cli.py:340, tests/test_cli/test_cli.py:398, tests/test_cli/test_cli.py:407, tests/test_cli/test_cli.py:422, tests/test_cli/test_cli.py:516]

## Justification
This is the most heavily-cited entry checked in this survey (10 test identifiers across 4 files) and the one with the longest, most narratively self-correcting `reason:` field in the register — it documents its own prior misclassification history. The breadth and total match rate (10/10) across this many test identifiers is itself informative: it suggests the entry's citation discipline is consistent, not cherry-picked.
## Examples
tests/test_cli/test_cli.py:516's `test_print_ignores_depth_entirely` directly corresponds to the entry's narrative claim that `print` is "depth-blind by design."
## Counterexamples
None — 10/10 cited identifiers confirmed.
## Depends on
None.
## Open questions
Whether the eight `test_reports.py`/`test_cli.py` methods actually assert the specific truncate-not-exclude behaviour the entry describes was not checked (would require reading method bodies, which the existence-only rule prohibits); only their existence as named identifiers was confirmed.
## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

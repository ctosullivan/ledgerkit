<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-001

## Statement
A transaction header line is matched by the `_TXN_HEADER` regex, which accepts dates in the forms YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, and year-omitted forms (M/DD, MM-DD, etc., with optional leading zeros and mixed separators), optionally followed by a secondary date introduced with `=` (same format rules), an optional status flag (`*`=cleared, `!`=pending), an optional parenthesized code, a lazily-matched description, and an optional `;`-introduced inline comment.

## Kind
definition

## Basis
directly_stated

## Evidence
`_TXN_HEADER` regex and its documentation comment in parser.py; `_parse_txn_header` which splits group 1 on `=` to get primary/secondary dates and builds a `Transaction`.

Evidence-paths: [ledgerkit/parser.py:101-144, ledgerkit/parser.py:358-385]

## Justification
The regex pattern and the surrounding multiline comment (required by CLAUDE.md's regex-documentation rule) explicitly enumerate every accepted date form and group semantics, and `_parse_txn_header` implements the `=`-split logic described.

## Examples
`"2024-01-05 * Salary"` → cleared=True, description="Salary"; `"2024-02-20=2024-02-22 * desc"` → date=2024-02-20, date2=2024-02-22; `"2024-01-10 Groceries"` with no flag → cleared=False, pending=False (tests/test_parser/test_parser.py:56-69).

## Counterexamples
A trailing `=` with no following date-like token is not matched by the optional secondary-date group, so group 1 contains only the primary date (parser.py:135-136, not separately unit-tested in the read excerpt but documented inline).

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


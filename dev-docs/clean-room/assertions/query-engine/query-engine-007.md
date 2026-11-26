<!-- producer: assertion-research | topic: query-engine | dispatch: qe-datespan-007 | date: 2026-10-02 -->
# Assertion: query-engine-007

## Statement
`date:` accepts exactly four value shapes via `_DATE_SPAN`: a closed range (two full dates joined by `-`, `..`, or ` to `), an open-from range (`D..`), an open-to range (`..D`), or a single bare date. A single bare date `D` becomes `DateSpan(D, D + 1 day)` (a one-day inclusive-feeling window via exclusive end); a *written* range's second date becomes the exclusive end exactly as given, with no auto-increment. Dates require a mandatory 4-digit year (2-digit years are rejected) and allow `-`, `/`, or `.` as the day/month/year separator.

## Kind
rule
## Basis
directly_stated
## Evidence
`_DATE_SPAN` (parser.py lines 133-161) and `_build_date` (lines 257-271) implement the four-shape dispatch; `_DATE_TOKEN = r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}"` (line 115) requires exactly 4 digits for the year. `test_parser.py::TestDateSpans` (lines 131-181) directly confirms: single date → `+1 day` end (`test_single_date`), three range-separator spellings all produce the same span (`test_closed_range_dash_separator`/`dotdot_separator`/`to_separator`), the written-range end is NOT auto-incremented (`test_range_end_is_written_bound_not_auto_incremented`, lines 156-163), both open-ended forms (lines 165-169), and 2-digit years / invalid calendar dates / malformed strings are all rejected (`test_two_digit_year_rejected`, `test_invalid_calendar_date_rejected`, `test_malformed_date_rejected`).

Evidence-paths: [ledgerkit/query/parser.py:100-161, ledgerkit/query/parser.py:257-271, tests/test_query/test_parser.py:131-181]

## Justification
The asymmetry between single-date (+1 day auto-end) and written-range (exact end) is the single most counterintuitive detail of this grammar — a caller who assumes `date:2024-01-01-2024-01-31` includes Jan 31 (by analogy with the single-date case) will get a silently wrong, off-by-one-day-short query. Also note: unlike the journal-header date parser (which can infer year from a preceding `Y` directive), the query-date grammar always requires an explicit 4-digit year, per the comment at lines 100-104.

## Examples
`date:2024-01-15` → `DateSpan(2024-01-15, 2024-01-16)`. `date:2024-01-01-2024-01-31` → `DateSpan(2024-01-01, 2024-01-31)` (Jan 31 itself excluded). `date:2024-01-01..` → `DateSpan(2024-01-01, None)`.

## Counterexamples
`date:2024-01-01-2024-02-01-2024-03-01` (three dates) matches none of the four shapes and raises `QueryParseError` (confirmed by the `$`-anchored, mutually exclusive alternation in `_DATE_SPAN`).

## Depends on
query-engine-001.

## Open questions
None — this is purely a self-contained grammar/behavior claim verifiable from code and tests alone, no external hledger-fidelity dependency in the statement itself (though the module comments do assert fidelity to an out-of-scope planning doc, not independently checked here).

## Evidence-support state
supported
## Status
verified
## Supersedes

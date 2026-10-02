<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-002

## Statement
Simple (non-header) dates are parsed by `_parse_simple_date` using the `_SIMPLE_DATE` regex, which accepts an optional 4-digit year followed by `[-/.]`-separated 1-2 digit month and day; when the year is omitted, `default_year` (itself overridable via the `Y` directive) is substituted, and an invalid calendar date (e.g. month 13) raises `ParseError` because `datetime.date()` rejects it.

## Kind
rule

## Basis
directly_stated

## Evidence
`_SIMPLE_DATE` regex and docstring; `_parse_simple_date` function body which calls `datetime.date(year, month, day)` inside a try/except converting `ValueError` to `ParseError`.

Evidence-paths: [ledgerkit/parser.py:146-169, ledgerkit/parser.py:334-355]

## Justification
Tests directly exercise every accepted separator and the year-omitted/default-year/invalid-date paths.

## Examples
Tests: `test_iso_hyphen`, `test_slash_separator`, `test_dot_separator`, `test_optional_leading_zeros`, `test_year_omitted_slash`, `test_year_omitted_hyphen`, `test_year_omitted_defaults_to_current_year`, `test_invalid_calendar_date_raises` (tests/test_parser/test_parser.py:322-368+). Also `Y` directive test `test_y_overrides_default_year` (tests/test_parser/test_parser.py:1335).

## Counterexamples
none found

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


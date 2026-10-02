<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-004

## Statement
Amount parsing (`_parse_amount`) supports prefix commodity symbols (`£30.00`), suffix commodity symbols (`30.00 EUR`), leading minus signs, a "mid-minus" sign appearing after a prefix symbol (`$-300`), comma-thousands/period-decimal by default, and the reverse (period-thousands/comma-decimal) when a `decimal-mark ,` directive is active, with E-notation and space-separated digit groups (`1 000 000 JPY`) also normalised before the main regex is applied.

## Kind
rule

## Basis
directly_stated

## Evidence
`_AMOUNT` / `_AMOUNT_COMMA` regexes and their doc comments; `_parse_amount` body which strips cost/lot annotations, normalises space separators, then branches on `ctx.decimal_mark`.

Evidence-paths: [ledgerkit/parser.py:171-263, ledgerkit/parser.py:433-461, ledgerkit/parser.py:488-548]

## Justification
Each sub-feature (prefix/suffix, negative prefix/suffix, thousands commas, trailing-decimal-no-fraction, comma-decimal mode, space digit groups, E-notation) has a corresponding passing test, confirming the regex-described behaviour is what actually executes.

## Examples
Tests: `test_prefix_symbol`, `test_suffix_symbol`, `test_negative_prefix`, `test_negative_suffix`, `test_thousands_comma`, `test_trailing_decimal_period`, `test_trailing_decimal_comma_mode` (tests/test_parser/test_parser.py:89-183); `test_comma_decimal_basic`, `test_comma_decimal_with_thousands`, `test_decimal_mark_applies_from_directive_forward` (tests/test_directives/test_directives.py:338-420); `test_space_digit_groups_three_groups`, `test_e_notation_suffix` (tests/test_parser/test_parser.py:1243-1309).

## Counterexamples
An amount with no commodity symbol at all raises `ParseError("amount has no commodity symbol")` unless a default commodity was set via a `D` directive (parser.py:529-534; tested indirectly via `test_d_applies_to_no_symbol_amount`, tests/test_parser/test_parser.py:1348).

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


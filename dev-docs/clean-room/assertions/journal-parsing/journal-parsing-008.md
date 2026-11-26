<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-008

## Statement
The parser offers two public entry points with different error-handling policies: `parse_string` raises `ParseError` immediately on the first malformed line (strict mode, `errors_out=None`), while `parse_string_lenient` is DESIGNED to never raise — for every directive handler except one (see Counterexamples), it collects every `ParseError`/`ParseWarning` into a returned list, discards the malformed transaction, and resumes parsing at the next blank line or new transaction header (`skip_until_blank` mechanism), returning a `(Journal, list[ParseError])` tuple intended for editor integrations run on every text-changed event. A malformed non-indented `commodity` directive (empty body, unterminated quote, or unparseable body) is a confirmed exception: it raises `ParseError` unconditionally, uncaught, even when `errors_out` is a list — see Counterexamples.

## Kind
rule

## Basis
directly_stated

## Evidence
`parse_string` / `parse_string_lenient` docstrings and bodies; `_parse_string_impl`'s `skip_until_blank` recovery logic.

Evidence-paths: [ledgerkit/parser.py:1013-1029, ledgerkit/parser.py:1668-1720]

## Justification
Both functions delegate to the same `_parse_string_impl`, differing only in the `errors_out` parameter; the docstrings state the intended use cases directly, and dedicated tests confirm the never-raises guarantee for the inputs they cover (plain garbage, bad postings, bad dates, stray indentation) and the discard-and-resume recovery behaviour. Every OTHER directive handler that can raise (`Y`, `D`, `P`, `alias`, `decimal-mark`, transaction header, posting, elided-amount-count) follows the same `try/except ParseError` + `if errors_out is None: raise` pattern, or an equivalent manual `ParseError(...); if errors_out is None: raise` construction — confirmed by reading each handler directly (parser.py:1403-1422 decimal-mark, 1433-1450 P, 1469-1480 alias, 1511-1520 Y, 1536-1547 D, 1586-1600 posting-outside-block, 1600-1612 posting parse, 1627-1641 elided-count). The `commodity` directive handler (parser.py:1324-1334) is the sole exception: its call to `_extract_commodity_symbol` at parser.py:1327 is NOT wrapped in any try/except or errors_out check, so any of that helper's three raise sites (empty body, unterminated quote, unparseable body — parser.py:630/636/646) propagates straight out of `_parse_string_impl`, through `parse_string_lenient`, uncaught. Reviewer-reproduced 2026-10-03: `parse_string_lenient("commodity\n")` and `parse_string_lenient('commodity "unterminated\n')` both raise `ParseError` instead of returning it in the error list.

## Examples
Tests: `test_lenient_never_raises`, `test_malformed_txn_discarded_valid_txn_kept`, `test_recovery_continues_after_error`, `test_posting_outside_block_caught_leniently`, `test_errors_have_line_numbers`, `test_bad_txn_followed_directly_by_good_without_blank` (tests/test_parser/test_parser.py:519-636).

## Counterexamples
CONFIRMED BUG (reviewer finding, 2026-10-03): a malformed non-indented `commodity` directive is NOT caught leniently, contradicting the "never raises" claim. `_parse_string_impl`'s `commodity` branch (parser.py:1324-1334) calls `symbol = _extract_commodity_symbol(body, lineno)` (parser.py:1327) with no surrounding try/except and no `errors_out` check, unlike every sibling directive handler. `_extract_commodity_symbol` itself unconditionally raises `ParseError` for an empty body (parser.py:630), an unterminated quoted symbol (parser.py:636), or an unparseable body (parser.py:646). Reproduced directly against ledgerkit/parser.py: `parse_string_lenient("commodity\n")` raises `ParseError: commodity directive has no symbol (line 1)` instead of returning `(journal, [that error])`; `parse_string_lenient('commodity "unterminated\n')` raises similarly. No test in tests/test_parser/ or tests/test_directives/ exercises a malformed `commodity` directive under `parse_string_lenient` — `test_lenient_never_raises` (tests/test_parser/test_parser.py) covers bad postings/dates/garbage/stray-indentation but not this directive, so the gap was untested as well as unasserted before this review.

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


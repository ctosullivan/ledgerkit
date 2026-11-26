<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-005

## Statement
`resolve_elision(txn)` returns `txn.postings` unchanged unless the transaction has exactly one posting with `amount is None`; in that single-elided case it computes per-commodity net sums over all explicit postings and replaces the elided posting with one synthetic `Posting` per commodity (sorted by symbol) whose amount is the negation of that commodity's net, each marked `inferred=True` and carrying the elided posting's `source_line`. Two or more elided postings is left unresolved by this function (it is instead rejected earlier, at parse time).

## Kind
state_transformation

## Basis
directly_stated

## Evidence
`resolve_elision` function body and docstring.

Evidence-paths: [ledgerkit/parser.py:816-869]

## Justification
The docstring explicitly enumerates the 0/1/2+ elided-posting cases and the function body implements exactly that: `elided_indices` length check, `commodity_sums` accumulation, synthetic posting construction with `inferred=True`.

## Examples
Tests: `test_no_elided_returns_postings_unchanged`, `test_single_elided_single_commodity_infers_correct_amount`, `test_single_elided_two_commodities_produces_two_postings`, `test_inferred_posting_has_inferred_true`, `test_inferred_amounts_are_negations`, `test_commodity_sort_order`, `test_elided_position_preserved_in_middle`, `test_two_elided_returns_unchanged`, `test_empty_given_returns_unchanged`, `test_inferred_posting_inherits_source_line` (tests/test_parser/test_parser.py:415-498+).

## Counterexamples
At actual parse time, two elided amounts in one transaction block raise `ParseError("a transaction block may have at most one elided amount")` before `resolve_elision` would ever see them that way (parser.py:1627-1641; test_two_elided_raises, tests/test_parser/test_parser.py:228-235) — so the "2+ elided, left unchanged" branch of `resolve_elision` is reachable only via direct/programmatic construction of a Transaction, not via normal parsing.

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


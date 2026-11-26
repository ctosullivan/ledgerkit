<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-010

## Statement
`Posting.date_override`/`date2_override` are set only from the FIRST occurrence of a `"date"`/`"date2"` tag in that posting's own parsed comment tags (not from the transaction's own tags, and not from a transaction-level `date`/`date2` tag, which has no override effect at all); an unparseable date value in such a tag is a hard error — raised immediately in strict mode (`errors_out is None`) or collected into `errors_out` with the override left unset in lenient mode.

## Kind
invariant

## Basis
directly_stated

## Evidence
`_apply_posting_date_override_tags` and `_try_set_date_tag` function bodies and their docstrings/comments; `Posting`/`Transaction` dataclass field comments in models.py explicitly stating the transaction-level tag has "no override effect".

Evidence-paths: [ledgerkit/parser.py:900-936, ledgerkit/models.py:80-110]

## Justification
The parser functions' docstrings state the first-occurrence-wins and hard-error semantics directly, and the models.py field comments state the deliberate scope restriction to postings only; tests confirm both the override mechanism and the no-effect-at-transaction-level behaviour.

## Examples
Tests: `test_posting_date_tag_sets_override`, `test_posting_date2_tag_sets_override`, `test_year_omitted_date_tag_uses_transaction_year`, `test_transaction_level_date_tag_has_no_override_effect`, `test_invalid_date_tag_raises_parse_error_strict`, `test_invalid_date_tag_collected_in_lenient_mode`, `test_first_occurrence_wins_for_repeated_date_tag` (tests/test_parser/test_parser.py:1550-1626).

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


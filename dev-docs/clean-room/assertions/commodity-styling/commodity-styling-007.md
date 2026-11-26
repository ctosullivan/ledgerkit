<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-elision | date: 2026-10-02 -->
<!-- reviewed-by: domain-skeptic | review-date: 2026-10-03 -->
# Assertion: commodity-styling-007

## Statement
In a transaction with exactly one elided (amount-less) posting and postings spanning multiple distinct commodities, elision resolution (`resolve_elision`) replaces the single elided posting with one inferred posting *per distinct commodity* present elsewhere in the transaction, each holding the negated sum for that commodity, each marked `inferred=True`, and the set of inferred postings is produced in ascending alphabetical order by commodity symbol. The inferred postings are spliced in at the original elided posting's position, preserving the order of the surrounding non-elided postings.

## Kind
state_transformation

## Basis
directly_stated

## Evidence
`test_single_elided_two_commodities_produces_two_postings`: a transaction with "£10.00", "$5.00", and one elided posting produces 4 total postings, 2 of them `inferred=True`, with commodities `{"£", "$"}`. `test_commodity_sort_order`: with commodities £, $, EUR present, the inferred postings' commodities come out as `sorted(["EUR", "$", "£"])`. `test_elided_position_preserved_in_middle`: confirms the replacement happens in-place at the elided posting's original list index, not appended at the end.

Evidence-paths: [tests/test_parser/test_parser.py:432-483]

## Justification
This is the mechanism by which ledgerkit supports hledger's elided-amount syntax in a multi-commodity transaction (e.g. a single equity/balancing posting standing in for several currencies at once) — a core multi-commodity behavior distinct from `commodity_style.py`'s display formatting.

## Examples
`_make_txn([("a", "£10.00"), ("b", "$5.00"), ("equity", None)])` → `resolve_elision` yields inferred postings `Amount(Decimal("-5.00"), "$")` and `Amount(Decimal("-10.00"), "£")`, in that ($, then £) order (test_inferred_amounts_are_negations, test_parser.py:456-463), consistent with alphabetical sort ("$" < "£" by Unicode code point).

## Counterexamples
None found; all resolve_elision multi-commodity tests in scope agree on sort order, inferred flag, and position preservation. (Review note: the original Evidence-paths end line (479) cut off before `test_elided_position_preserved_in_middle`'s closing assertions at lines 480-483, which are the actual lines confirming `result[-1].account == "b"` and `middle.inferred == True`; corrected to 432-483.)

## Depends on
None directly on commodity_style.py — this is a parser/model-level behavior (operates on `Transaction`/`Posting`/`Amount` from `ledgerkit/models.py`) that is logically prerequisite to any later per-commodity style formatting of the resulting postings.

## Open questions
The actual `resolve_elision` function implementation itself lives outside the permitted evidence paths (not in `models.py`, `commodity_style.py`, or the test files read) — only its externally observed behavior via tests is evidenced here; its import source in test_parser.py was not traced since doing so would require opening a non-permitted module.

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

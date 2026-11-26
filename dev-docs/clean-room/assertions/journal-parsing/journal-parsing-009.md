<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-009

## Statement
A posting amount token may carry a balance assertion (`=`, `==`, `=*`, `==*`, detected by `_ASSERTION_MARKER_RE` requiring whitespace on both sides) and/or a cost annotation (` @ PRICE` / ` @@ TOTAL`, checked `@@` before `@`) and/or lot annotations (`{AMOUNT}`, `{{AMOUNT}}`, `[DATE]`, `(LABEL)`, stripped via `_LOT_ANNOTATION_RE` before the main amount regex runs); these are mutually composable on one posting line and are stripped/parsed in a fixed order: cost annotation first, then lot annotations, then space-digit-group normalisation, then the main amount/quoted-suffix regex.

## Kind
rule

## Basis
directly_stated

## Evidence
`_strip_cost_annotation`, `_LOT_ANNOTATION_RE`/`_strip_lot_annotations`, `_ASSERTION_MARKER_RE`, and the ordered calls inside `_parse_amount` and `_parse_posting`.

Evidence-paths: [ledgerkit/parser.py:388-430, ledgerkit/parser.py:488-548, ledgerkit/parser.py:658-752]

## Justification
The code's own ordering (cost strip → lot strip → space normalise → regex match) is stated in `_parse_amount`'s body, and `_parse_posting` applies the assertion-marker split before calling `_parse_amount` on the remaining posting-amount portion; tests exercise cost annotations, lot annotations, and combinations.

## Examples
Tests: `test_at_unit_cost_stripped`, `test_atat_total_cost_stripped`, `test_cost_raw_stored_on_posting`, `test_cost_with_lot_annotation`, `test_unit_lot_brace`, `test_total_lot_double_brace`, `test_lot_date`, `test_lot_label`, `test_all_annotations_combined` (tests/test_parser/test_parser.py:1115-1206).

## Counterexamples
A bare `=` at the very start of an amount token (e.g. `"= $500"`, a balance-assignment-style elision) is NOT matched by `_ASSERTION_MARKER_RE` because that regex requires leading whitespace before the marker — documented explicitly as an edge case in its comment (parser.py:670-672); no test for this specific sub-case was found in the permitted files. Reviewer-verified 2026-10-02: the "mutually composable" claim above (balance assertion + cost + lot annotations together on one posting) is NOT actually exercised by `test_all_annotations_combined`, which only combines cost+lot, no assertion marker. Independently constructed and ran `"10 AAPL {$182.00} [2023-11-01] (lot1) @ $185.00 = $1850.00"` against ledgerkit/parser.py directly: all three compose correctly (amount=10 AAPL, cost_raw="$185.00", balance_assertion amount=$1850.00), confirming the claim holds even though no cited test demonstrates it.

## Depends on

## Open questions
RESOLVED by reviewer 2026-10-02 (no escalation needed — this was researchable within the permitted evidence paths without consulting any excluded doc, by running the parser itself rather than only reading it): `parse_string('2024-01-01 Buy\n    assets:cash  = $500\n    assets:other\n')` raises `ParseError: invalid amount: '= $500'`. The bare-leading-`=` balance-assignment form is NOT handled anywhere else in parser.py; it simply fails amount parsing. ledgerkit does not currently implement hledger's balance-assignment-elision posting syntax (`account = ASSERTIONAMOUNT` with no explicit amount) as a working feature — the code comment at parser.py:670-672 names the hledger concept for context but no code path implements it. This is a statement about current behaviour only; whether this is in-scope/intended is a product-scope question outside this review.

## Evidence-support state
supported

## Status
verified

## Supersedes


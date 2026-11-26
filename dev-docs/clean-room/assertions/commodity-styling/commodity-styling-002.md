<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-sep-infer | date: 2026-10-02 -->
# Assertion: commodity-styling-002

## Statement
When a numeric string contains exactly one kind of separator character (only dots or only commas), `_infer_separators()` disambiguates decimal-mark vs. group-separator by a fixed heuristic: if that separator occurs exactly once, is not at position 0, and is followed by exactly 3 digits, it is classified as a *digit-group separator* (precision becomes 0, i.e. the number is treated as a whole integer with grouped thousands); in every other single-separator case it is classified as the *decimal mark*, and precision equals the digit count after the last occurrence.

## Kind
rule

## Basis
directly_stated

## Evidence
In `_infer_separators()`, the `elif dots > 0:` branch computes `digits_after = len(numeric) - last_dot - 1` and does `if digits_after == 3 and dots == 1 and last_dot > 0:` → group separator, precision 0; `else:` → decimal mark, precision = digits_after. The `elif commas > 0:` branch mirrors this exactly for commas.

Evidence-paths: [ledgerkit/commodity_style.py:242-267]

## Justification
This single heuristic is directly responsible for the difference between "$1,234.56" (comma=group, because two separators are present — see commodity-styling-003) and the ambiguous single-separator cases "$1,234" (comma=group, precision 0) vs. "100,5" (comma=decimal, precision 1) vs. "1.234" (dot=group, decimal becomes comma, precision 0) vs. "1.5" (dot=decimal, precision 1).

## Examples
`CommodityStyle.infer("$", "$1,234")` → group_separator=",", decimal_mark=".", precision=0 (test_integer_with_us_group_separator, test_commodity_style.py:64-69). `CommodityStyle.infer("EUR", "1.234 EUR")` → group_separator=".", decimal_mark=",", precision=0 (test_integer_with_european_group_separator, test_commodity_style.py:71-76). `CommodityStyle.infer("USD", "42.50 USD")` → decimal_mark=".", group_separator="", precision=2, since digits_after=2 ≠ 3 (test_usd_suffix_simple_two_decimal, test_commodity_style.py:42-48).

## Counterexamples
A 3-digit fractional part is indistinguishable from a 3-digit group by this heuristic alone: "$1.234" with a genuinely intended 3-decimal-place amount would be misclassified as "$1234" grouped (precision 0, decimal becomes ","), since the code cannot know authorial intent from a single ambiguous sample. No test in scope exercises this specific misclassification, but it follows directly from the `digits_after == 3` branch condition.

## Depends on
commodity-styling-003 (the two-separator-present case takes priority and is checked first in the function).

## Open questions
Whether this 3-digit heuristic was deliberately chosen to match hledger's own inference behavior, or is a ledgerkit-specific simplification, is not established from the permitted evidence (no comment in commodity_style.py cites hledger's actual algorithm).

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

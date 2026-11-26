<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-both-sep | date: 2026-10-02 -->
# Assertion: commodity-styling-003

## Statement
When a numeric string contains both a dot and a comma, `_infer_separators()` always treats whichever of the two occurs rightmost (closest to the end of the string) as the decimal mark, and the other as the digit-group separator — regardless of how many times either character repeats.

## Kind
rule

## Basis
directly_stated

## Evidence
`if dots > 0 and commas > 0:` branch: `last_dot = numeric.rfind("."); last_comma = numeric.rfind(","); if last_dot > last_comma: decimal_mark = "."; group_separator = ","` else the reverse, with precision computed from the position of whichever mark was chosen as decimal.

Evidence-paths: [ledgerkit/commodity_style.py:228-241]

## Justification
This is the only branch of `_infer_separators` reached when both separator characters are present at least once, and it is checked first (before the single-separator branches), so it takes priority over the 3-digit group heuristic in commodity-styling-002.

## Examples
`CommodityStyle.infer("$", "$1,234.56")` → decimal_mark=".", group_separator="," (dot is rightmost) (test_dollar_prefix_comma_group_dot_decimal, test_commodity_style.py:11-17). `CommodityStyle.infer("EUR", "1.234,56 EUR")` → decimal_mark=",", group_separator="." (comma is rightmost) (test_eur_suffix_space_dot_group_comma_decimal, test_commodity_style.py:19-25). `CommodityStyle.parse_style_override("1.000,00 EUR")` round-trips the same way via `infer()` (test_european_suffix, test_commodity_style.py:142-148).

## Counterexamples
None found — every multi-separator test case in scope is consistent with "rightmost wins."

## Depends on
None (this branch is checked first, unconditionally, whenever both dots>0 and commas>0).

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

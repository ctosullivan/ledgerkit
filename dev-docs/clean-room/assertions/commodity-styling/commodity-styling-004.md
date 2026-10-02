<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-neg-fmt | date: 2026-10-02 -->
<!-- reviewed-by: domain-skeptic | review-date: 2026-10-03 -->
# Assertion: commodity-styling-004

## Statement
`CommodityStyle.format()` places the minus sign differently depending on symbol position: for a prefix-style commodity, the sign goes *after* the symbol and immediately before the number with no gap (e.g. "£-5,000.00") — this holds **unconditionally**, even when `self.space` is `True` (the positive-amount gap is dropped entirely in the negative branch, not just left as-is); for a suffix-style commodity, the sign goes *before* the number, ahead of the normal leading position (e.g. "-1,234.56 EUR"), and the symbol stays at the end, with `self.space`'s gap preserved as normal between the number and the suffix symbol.

## Kind
rule

## Basis
directly_stated

## Evidence
In `format()`: `if self.prefix: ... if negative: return f"{self.commodity}-{number}" ... else: ... if negative: return f"-{number}{gap}{self.commodity}"`, each branch annotated in-code as "hledger convention: prefix-symbol negative → SYMBOL-NUMBER" / "suffix-symbol negative → -NUMBER SYMBOL". Note the prefix-negative f-string has no `{gap}` token at all (so `self.space` is structurally irrelevant to that branch), while the suffix-negative f-string does include `{gap}`. Verified directly by executing the code during review (not from an existing test) that this holds even when `self.space=True`: `CommodityStyle("$", prefix=True, space=True, decimal_mark=".", group_separator=",", precision=2).format(Decimal("-1234.56"))` → `"$-1,234.56"` (no space), versus `.format(Decimal("1234.56"))` → `"$ 1,234.56"` (space present) on the same style object.

Evidence-paths: [ledgerkit/commodity_style.py:102-133]

## Justification
This asymmetry is explicitly called out as an hledger-compatibility convention in the source comments, and is independently verified by both value-generating tests and the CLI-level formatting tests for the `self.space=False` case. The `self.space=True` + prefix + negative combination specifically is not exercised by any test in `tests/test_commodity_style.py` (the one prefix-negative test, `test_prefix_negative_puts_symbol_before_minus`, uses a GBP style inferred from `"£5,000.00"`, which has `space=False`) — this was confirmed only by direct execution during this review, not by an existing unit test.

## Examples
`CommodityStyle.infer("£", "£5,000.00").format(Decimal("-5000.00"))` → `"£-5,000.00"` (test_prefix_negative_puts_symbol_before_minus, test_commodity_style.py:97-100). `CommodityStyle.infer("EUR", "1,234.56 EUR").format(Decimal("-1234.56"))` → `"-1,234.56 EUR"` (test_suffix_negative_puts_minus_before_number, test_commodity_style.py:102-104).

## Counterexamples
None against the stated rule. However, the claim that "both prefix and suffix negative-formatting paths are directly tested and match the stated rule exactly" (as originally written in this assertion) overstated test coverage: only the `space=False` prefix-negative case is covered by an existing test. The `space=True` prefix-negative case (where the asymmetry — gap dropped only when negative — is actually visible) was previously unverified by any test or prior evidence check; it is now confirmed by direct execution (see Evidence) to follow the same rule, with no test added to the suite.

## Depends on
commodity-styling-001 (prefix/suffix classification feeds directly into which branch of `format()` runs).

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

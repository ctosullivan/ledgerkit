<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-infer-pos | date: 2026-10-02 -->
<!-- reviewed-by: domain-skeptic | review-date: 2026-10-03 -->
# Assertion: commodity-styling-001

## Statement
`CommodityStyle.infer()` determines whether a commodity symbol is a prefix or suffix purely by string matching: it strips any leading minus sign from the raw amount string, then checks whether the remaining text starts with the commodity symbol (prefix) or ends with it (suffix), via an `if`/`elif`, so a symbol that matches both ends (a degenerate case) resolves to prefix because the `startswith` check is tried first. If neither matches, it silently falls back to treating the *entire* remaining string (including any unrelated trailing/leading text, e.g. a different commodity's own symbol) as the "numeric" portion fed to `_infer_separators()`, with `prefix=True` left at its default — this is not a benign no-op fallback; it can produce a nonsensical `precision` because `_infer_separators()` counts characters by string length, not by digit-ness.

## Kind
rule

## Basis
directly_stated

## Evidence
`CommodityStyle.infer()` in `ledgerkit/commodity_style.py` strips a leading `-`, then does `if commodity and s.startswith(commodity): prefix = True ...` else `elif commodity and s.endswith(commodity): prefix = False ...` with an explicit `# else: numeric = s (no recognisable commodity position; rare edge case)` comment covering the no-match case. Verified directly by executing the code during review (not from an existing test):
`CommodityStyle.infer("A", "A5A")` → `prefix=True` (both startswith and endswith "A" match; `if` branch wins over `elif`).
`CommodityStyle.infer("EUR", "100.00 USD")` → `CommodityStyle(commodity='EUR', prefix=True, space=False, decimal_mark='.', group_separator='', precision=6)` — the trailing `" USD"` text (4 characters, none of them digits) gets counted into `digits_after` by `_infer_separators()`, which only measures `len(numeric) - last_dot - 1`, producing precision=6 even though the string has only 2 real decimal digits.

Evidence-paths: [ledgerkit/commodity_style.py:146-165, ledgerkit/commodity_style.py:223-274]

## Justification
This is the sole mechanism by which the module decides symbol placement; there is no separate "detect position" helper, and no other file in scope recomputes this. The precision-corruption consequence of the fallback follows directly from `_infer_separators()`'s use of raw string length rather than a digit-count, and was confirmed by direct execution rather than inferred from the comment alone.

## Examples
`CommodityStyle.infer("$", "$1,234.56")` → prefix=True (test_dollar_prefix_comma_group_dot_decimal, test_commodity_style.py:11-17). `CommodityStyle.infer("EUR", "1.234,56 EUR")` → prefix=False (test_commodity_style.py:19-25). `CommodityStyle.infer("$", "-$1,234.56")` → prefix stays True; the minus is stripped before the startswith check (test_negative_prefix_amount, test_commodity_style.py:50-55).

## Counterexamples
No counterexample to the *stated* rule — but the "else"/no-match fallback (symbol matches neither start nor end) is NOT merely "treats the whole string as numeric" in a harmless sense: verified directly during this review (see Evidence) that it can silently produce a corrupted `precision` value when the declared commodity doesn't literally appear in the raw amount string. No test in `tests/test_commodity_style.py` or `tests/test_parser/test_parser.py` exercises this branch at all — it remains untested in the test suite even though it is now behaviorally confirmed (by direct execution, not by a unit test) during this review.

## Depends on
None.

## Open questions
Whether this mismatch path (declared commodity symbol absent from the raw string actually being inferred from) is reachable in practice via `Journal.commodity_styles` — e.g. via a `commodity` directive whose declared symbol doesn't literally occur in its own sample-amount text — depends on how `_commodity_directive_raws` gets populated, which happens in `ledgerkit/parser.py`, outside this topic's permitted evidence paths. Not resolved here; flagged for whoever reviews the loader/parsing topic.

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

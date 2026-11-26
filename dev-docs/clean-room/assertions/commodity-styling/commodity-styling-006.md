<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-override | date: 2026-10-02 -->
<!-- reviewed-by: domain-skeptic | review-date: 2026-10-03 -->
# Assertion: commodity-styling-006

## Statement
`CommodityStyle.parse_style_override()` (backing the CLI's `-c`/`--commodity-style` flag) extracts the commodity symbol from a user-supplied style string by trying a suffix-alphabetic match first (`_STYLE_SUFFIX_COMMODITY`, e.g. picks "USD" out of "1,000.00 USD"), and only if that fails tries a prefix-symbol match (`_STYLE_PREFIX_COMMODITY`, e.g. picks "$" out of "$1,000.00"). It raises `ValueError` if the string is empty, contains no digit characters at all, or matches neither pattern (e.g. a bare numeric string with no commodity symbol at all, such as "123.45", which has digits but fails both the suffix and prefix regexes). Critically, an override only changes formatting for the specific commodity symbol it names — it does not affect any other commodity's inferred style, even within the same journal/report run.

## Kind
rule

## Basis
directly_stated

## Evidence
`parse_style_override()`: `if not any(ch.isdigit() for ch in s): raise ValueError(...)`; then `m_suffix = _STYLE_SUFFIX_COMMODITY.search(s)` tried first, falling back to `m_prefix = _STYLE_PREFIX_COMMODITY.match(s)`, else `raise ValueError`. The CLI-level test `test_c_flag_different_commodity_has_no_effect` (test_commodity_style.py:221-232) confirms the per-commodity scoping: overriding GBP's style leaves £-denominated output ("£50.00") unchanged and does not introduce "GBP" into output at all. The third `raise ValueError` branch (digits present, but neither regex matches — a bare numeric string with no commodity symbol) was not exercised by any test in `tests/test_commodity_style.py` (the only tested raise-paths are the empty-string and no-digits cases); verified directly during this review by executing `CommodityStyle.parse_style_override("123.45")`, which raises `ValueError: cannot parse commodity style: '123.45'` as the rule predicts.

Evidence-paths: [ledgerkit/commodity_style.py:182-216, tests/test_commodity_style.py:221-232]

## Justification
The regex-ordering choice (suffix tried before prefix) is what makes "1,000.00 USD" resolve to commodity "USD" rather than accidentally matching some other substring; the per-commodity scoping is a separate, CLI-layer behavior (exercised only by the `TestCLIIntegration` tests, which call into `ledgerkit.cli.main`, not into `commodity_style.py` directly — the override-to-styles-map wiring itself is outside the permitted evidence paths and was not inspected).

## Examples
`parse_style_override("1,000.00 USD")` → commodity="USD", suffix, space, dot decimal, comma group, precision 2 (test_usd_suffix, test_commodity_style.py:133-140). `parse_style_override("$1,000.00")` → commodity="$", prefix (test_dollar_prefix, test_commodity_style.py:124-131). `parse_style_override("bad input !!")` raises ValueError (test_no_digits_raises, test_commodity_style.py:159-161) — note this string does contain no digits, consistent with the digit-presence guard (this exercises the *first* raise branch, not the "matches neither pattern" branch). `parse_style_override("123.45")` raises ValueError (verified directly during this review, not by an existing test) — this exercises the third, previously-untested raise branch: digits are present, but neither the suffix nor prefix regex matches a bare numeric string.

## Counterexamples
None found; all parse_style_override tests in scope are consistent with the stated try-suffix-then-prefix order and digit-presence guard. The "matches neither pattern" raise branch had no test coverage prior to this review (see Examples) but is now confirmed, not merely assumed from reading the `else: raise` line.

## Depends on
commodity-styling-001 (parse_style_override delegates to `infer()` once the commodity symbol is extracted).

## Open questions
The actual CLI plumbing that applies a successfully-parsed override into the per-report styles dict (e.g. how/where it merges with `Journal.commodity_styles`) lives in `ledgerkit/cli.py`, which is out of scope for this research — only the parsing half and its externally observed CLI effect (via `tests/test_commodity_style.py`'s `TestCLIIntegration`) were evidenced.

## Evidence-support state
supported
## Status
verified
## Supersedes
(none)

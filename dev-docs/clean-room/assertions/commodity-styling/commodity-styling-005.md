<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-priority | date: 2026-10-02 -->
# Assertion: commodity-styling-005

## Statement
`Journal.commodity_styles` resolves one `CommodityStyle` per commodity symbol using a three-pass, strictly-ordered priority scheme: (1) an explicit `commodity` directive's sample amount always wins if present for that symbol; (2) otherwise, the first posting amount seen for that commodity (in transaction/posting iteration order) is used; (3) otherwise, the first price-directive (`P`) amount for that commodity is used. Directive-based inference is applied last in the code but is stated to take final priority because it unconditionally overwrites whatever key already exists in the dict.

## Kind
rule

## Basis
directly_stated

## Evidence
The docstring states "Priority order (highest wins): 1. Explicit `commodity` directives. 2. First posting amount seen... 3. First price-directive amount...". The implementation runs posting-amount inference first (`if ... p.amount.commodity not in styles`), then price-directive inference (`not in styles`), then directive-based inference last, unconditionally (`styles[comm] = CommodityStyle.infer(comm, raw)` with no `not in styles` guard), which is what lets directives override earlier passes despite running last.

Evidence-paths: [ledgerkit/models.py:338-374]

## Justification
The `not in styles` guards on passes 1 and 2 implement "first seen wins" within and between those two passes; the unconditional overwrite in pass 3 is what actually implements "directives win regardless of order" — the docstring's stated priority and the code's pass ordering are inverted but produce the documented result.

## Examples
A journal with a `commodity USD 1.000,00\n` directive plus a posting of `42.50 USD` would end up with the European-style (comma-decimal) `CommodityStyle` for USD, because pass 3 overwrites whatever pass 1 inferred from the posting.

## Counterexamples
None found in the permitted evidence (no test file for this property was in the permitted path list — `tests/test_commodity_style.py` tests `CommodityStyle` directly, not `Journal.commodity_styles`'s priority merging; this assertion rests on direct code/docstring reading only, not a confirming test).

## Depends on
commodity-styling-001 (same `CommodityStyle.infer()` is reused in all three passes).

## Open questions
No test in the permitted evidence exercises the directive-overrides-posting priority claim directly — it is read from code/docstring only (basis: directly_stated on the docstring, but unsupported by a test within scope).

## Evidence-support state
partially_supported
## Status
supported
## Supersedes
(none)

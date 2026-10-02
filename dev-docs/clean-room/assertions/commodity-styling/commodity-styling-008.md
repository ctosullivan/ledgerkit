<!-- producer: assertion-research | topic: commodity-styling | dispatch: cs-section-limit | date: 2026-10-02 -->
# Assertion: commodity-styling-008

## Statement
`ReportSectionResult.to_dataframe()` has a documented, acknowledged single-commodity limitation: its docstring says "multi-commodity support is deferred," and its implementation picks exactly one commodity to label every row with — taken from `next(iter(self._commodity_styles), "")`, i.e. an arbitrary/first key of the styles dict, not a per-row lookup — then applies that one `CommodityStyle` to every row's `amount` value regardless of what commodity that value actually originated in.

## Kind
boundary

## Basis
directly_stated

## Evidence
Docstring: "Includes a final 'Total {section.name}' row... (single-commodity assumption)." Code: `commodity = list(self.rows.keys())[0] if self.rows else ""` (which is actually a bug-prone line — `self.rows` keys are account names, not commodities, as the following comment itself admits) then immediately overwritten by `commodity = next(iter(self._commodity_styles), "")`. The in-code comment reads: "Actually rows are account names, not commodities. We need the commodity from the style map or just leave it as empty."

Evidence-paths: [ledgerkit/models.py:252-292]

## Justification
This is a self-admitted boundary/limitation directly in the source comments (not inferred) — the first line computing `commodity` from `self.rows.keys()` is dead/wrong logic immediately superseded by the next line, which the surrounding comment explicitly flags as a workaround. This contrasts with `Journal.to_dataframe()` (models.py:479-534), which does look up `styles.get(amt.commodity)` per-posting/per-row correctly, and `Amount.display()` (models.py:31-33), which formats a single Amount's own commodity correctly — i.e. multi-commodity-correct formatting exists elsewhere in the same file but is not what `ReportSectionResult.to_dataframe()` does.

## Examples
If a `ReportSectionResult`'s `rows` mix two commodities (e.g. an account balance in both USD and EUR somehow landed in the same flat `dict[str, Decimal]`), every row's `amount_formatted` would be produced using whichever single `CommodityStyle` happens to be first in `_commodity_styles`' iteration order, silently mis-formatting any row in a different commodity.

## Counterexamples
None found that contradict this — no test file in scope (`tests/test_commodity_style.py`, `tests/test_parser/`) exercises `ReportSectionResult.to_dataframe()` at all, so this assertion rests on code reading alone, not a confirming/denying test.

## Depends on
commodity-styling-005 (the `_commodity_styles` dict it draws from is populated the same way `Journal.commodity_styles` is, per the Pass 1–3 priority scheme).

## Open questions
Whether `BalanceRow`/`balance_from_spec` (the actual producer of `ReportSectionResult.rows`, referenced only by name in a comment at models.py:265) ever actually produces genuinely multi-commodity rows in practice is unknown — that producer function lives in `ledgerkit/reports.py`, outside the permitted evidence paths, so it was not inspected.

## Evidence-support state
supported
## Status
proposed
## Supersedes
(none)

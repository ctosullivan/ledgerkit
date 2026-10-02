<!-- producer: assertion-research | topic: tags | dispatch: tags-r9 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | dispatch: tags-r9-review | date: 2026-10-03 -->
# Assertion: tags-009

## Statement
In ledgerkit's model, a posting can reference at most one commodity in its main amount (ledgerkit has no `MixedAmount` concept), so `_posting_commodities` always returns a 0-element list (no amount) or 1-element list (amount present) — never more than one. `_commodity_tags` is nonetheless written to accept and concatenate tags for an arbitrary-length list of commodity symbols, explicitly to mirror hledger's own plural `postingCommodities`/support a hypothetical future multi-commodity posting, even though that case cannot currently occur.

## Kind
boundary

## Basis
directly_stated

## Evidence
`_posting_commodities` docstring (tags.py:179-191): "Ledgerkit's `Posting.amount` is a single `Amount` (one commodity per posting — no `MixedAmount` concept), so this is always a 0- or 1-element list... kept as its own small helper... so `_effective_tags`/`_accounts_effective_tags` read the same either way if Ledgerkit ever grows multi-commodity postings." `_commodity_tags` (tags.py:194-207) takes `commodities: list[str]` and loops over it, concatenating `journal.declared_commodity_tags.get(symbol, [])` for each.

Independently re-checked during review, using the narrow models.py type-resolution allowance: `ledgerkit/models.py` line 74 declares `Posting.amount` as `amount: Amount | None = None` — a single optional `Amount`, not a list/collection — confirming the docstring's claim structurally rather than resting on the docstring's own prose alone.

Evidence-paths: [ledgerkit/tags.py:179-191, ledgerkit/tags.py:194-207, ledgerkit/models.py:74]

## Justification
The code is explicit that this is a forward-compatibility boundary: the current data model structurally forbids more than one commodity per posting (confirmed independently against the `Posting` dataclass field declaration itself, not merely the docstring describing it), but the helper functions' signatures (plural, list-based) are deliberately shaped as if that constraint might not always hold.

## Examples
`test_no_amount_returns_empty` (test_tags.py:220-221) and `test_amount_returns_single_commodity` (test_tags.py:223-225) exercise the 0- and 1-element cases respectively. `test_multiple_commodities_concatenate` (test_tags.py:235-236) exercises `_commodity_tags` directly with a 2-element input list (`["$", "EUR"]`) even though no test ever produces such a list via `_posting_commodities` itself — confirming the multi-commodity path is tested only at the `_commodity_tags` level, not end-to-end from a real `Posting`.

## Counterexamples
None found, but see Open questions.

## Depends on
`Posting.amount` being a single `Amount` rather than a collection — independently re-derived during review from `ledgerkit/models.py:74` (`amount: Amount | None = None`), using the same narrow type-resolution allowance the original research dispatch had; no longer resting on the docstring's prose alone.

## Open questions
No test constructs a `Posting` whose `_posting_commodities` output has length >1 — the multi-commodity concatenation path in `_commodity_tags` is only verified with a hand-built list, not via any real multi-commodity `Posting`, since the current model's `Posting.amount: Amount | None` field structurally cannot produce one. This remains genuinely unresolvable within scope (it isn't a gap to fill, it's a structural impossibility given the current model), not an outstanding ambiguity requiring escalation.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

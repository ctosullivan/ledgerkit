<!-- producer: assertion-research | topic: tags | dispatch: tags-r8 | date: 2026-10-02 -->
# Assertion: tags-008

## Statement
`effective_date` and `effective_date2` implement a posting-level date-tag override precedence chain that is structurally distinct from (but conceptually adjacent to) the `tag:`-matching effective-tags logic: a posting's own `date:` comment tag (materialized as `Posting.date_override`) takes precedence over its transaction's date for the primary effective date. For the secondary date, the precedence is a strict four-level fallback — posting's `date2_override`, then transaction's `date2`, then posting's `date_override` (primary override reused as secondary fallback), then transaction's primary `date` — each checked in that exact order, stopping at the first non-None value.

## Kind
rule

## Basis
directly_stated

## Evidence
`effective_date` (tags.py:110-118): "A posting's own `date:` comment tag... takes precedence over its transaction's date." `effective_date2` (tags.py:121-138) docstring: "Mirrors hledger's `postingDate2` four-level fallback chain exactly: this posting's own `date2:` override, then its transaction's `date2`, then this posting's own `date:` override (primary, reused as a secondary-date fallback), then its transaction's primary date." Implementation is four sequential `if x is not None: return x` checks ending in `return txn.date`.

Evidence-paths: [ledgerkit/tags.py:110-118, ledgerkit/tags.py:121-138]

## Justification
Both functions are pure, unconditional precedence chains over Optional fields, with the docstrings explicitly naming each fallback level and its source (hledger's `postingDate`/`postingDate2`), and the implementation's early-return structure matches the stated order exactly.

## Examples
`test_own_date_override_reused_as_date2_fallback` (test_tags.py:174-180) is the most distinctive case: with no txn `date2` and no posting `date2_override`, but a posting `date_override` present, `effective_date2` returns that primary override value — demonstrating the "reused as secondary fallback" behavior explicitly. `test_override_takes_precedence` (test_tags.py:152-155) and `test_txn_date2_used_when_no_posting_date2_override` (test_tags.py:169-172) cover the other two precedence levels.

## Counterexamples
None found — all four fallback levels are individually exercised by a distinct test and none contradicts the stated order.

## Depends on
`Transaction.date`, `Transaction.date2`, `Posting.date_override`, `Posting.date2_override` (model fields, used but not defined in tags.py).

## Open questions
Unlike `_effective_tags`, this precedence chain IS a genuine override/shadowing mechanism (first non-None wins) — worth noting as a contrast to tags-002's explicit "no shadowing" rule for `tag:` matching; the two mechanisms (date overrides vs. tag-value union) are separate and not reconciled or cross-referenced to each other anywhere in the permitted evidence beyond being in the same module.

## Evidence-support state
supported

## Status
verified

## Supersedes
(none)

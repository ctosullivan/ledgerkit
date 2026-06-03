# Context — 2026-06-04

## Current Task
Implement Milestone 4 — Comprehensive Format Compatibility: make `parse_string_lenient` return zero errors on the two comprehensive test fixtures.

## Where We Are
Phase 1 and Phase 1b are complete. Next step is **Phase 2a** — amount parser fixes A1–A3 (sign-after-prefix, cost annotation stripping, lot annotation stripping) in `ledgerkit/parser.py`.

## Decisions In Flight
- `_ParseContext` introduced as an internal dataclass (leading underscore, not public API) — no API-spec change needed for the dataclass itself, only for the fields it enables.
- `Transaction.date2` placed after `description` (not directly after `date`) to satisfy Python dataclass ordering: fields with defaults must follow all fields without defaults.

## Files Currently Relevant
- `ledgerkit/parser.py` — Phase 2a target: `_parse_amount`, `_AMOUNT`, `_AMOUNT_COMMA` regexes, new helpers `_strip_cost_annotation`, `_strip_lot_annotations`
- `ledgerkit/models.py` — already updated; `Posting.cost_raw` will be set by `_parse_posting` in Phase 2a
- `tests/fixtures/comprehensive-hledger-test.journal` — primary fixture; 22 errors expected before Phase 2a, 8 after
- `dev-docs/planning/milestone-4.md` — full spec; sections A1–A3 cover Phase 2a work

## Blockers / Open Questions
None.

## What NOT To Revisit
- `_ParseContext` is internal and does not need to be exported or documented in api-spec.md beyond its effects.
- `Transaction.date2` field order: it is after `description`, not directly after `date` — required by Python dataclass rules.
- `#` is intentionally not an inline comment delimiter (only `;` is). Matches hledger spec.

## Recent Git State
```
11b3b57 docs: add Milestone 4 plan, fixtures, and ROADMAP entry
67f8c7f chore: release v0.1.0 — rename to ledgerkit, add commodity styles and pandas export
b2d10be fix: correct column-0 comment handling inside open transaction blocks
8b5fc81 chore: release v0.5.0 and mark Milestone 3 done
d393b8c feat: Milestone 3 — lenient parser, multi-commodity balance, tree mode, CheckError.line_number
```

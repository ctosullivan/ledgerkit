# Context — 2026-06-06

## Current Task
Implement Milestone 4 — Comprehensive Format Compatibility: make `parse_string_lenient` return zero errors on the two comprehensive test fixtures.

## Where We Are
Phase 5 complete. All five phases of Milestone 4 are done. 575 tests pass; 0 hard errors on the comprehensive fixture. Awaiting user confirmation that Milestone 4 is done before marking `[DONE]` in ROADMAP.md.

## Decisions In Flight
- `_parse_amount` returns `tuple[Amount, str | None]` — second element is stripped cost annotation. All call sites updated.
- `ParseWarning(ParseError)` is added to `errors_out` in lenient mode for `~` and `=` blocks but is NOT a hard error. Callers filter with `isinstance(e, ParseWarning)`.
- Transaction-header quick-detection lookahead extended from `[\s*!(]` to `[\s*!(=]` to accept secondary-date lines.
- Nested `apply account` emits a `ParseWarning` (added in Phase 4) and silently replaces the old prefix.

## Files Currently Relevant
- `ROADMAP.md` — mark Milestone 4 `[DONE]` when user confirms
- `dev-docs/changelog/` — create MILESTONE-4.md archive when user confirms

## Blockers / Open Questions
- User must explicitly confirm Milestone 4 is complete before `[DONE]` is set in ROADMAP.md.

## What NOT To Revisit
- `_ParseContext` is internal and does not need to be exported or documented in api-spec.md beyond its effects.
- `Transaction.date2` and `Posting.cost_raw` already documented in api-spec.md since Phase 1.
- `#` is intentionally not an inline comment delimiter (only `;` is). Matches hledger spec.
- `ParseWarning` items in `errors_out` do NOT count as hard errors; verify with `isinstance` filter.
- The `=` rule handler requires `^=\s+\S` (space + non-space after `=`) to avoid clashing with balance-assertion syntax.

## Recent Git State
```
5442e73 feat: Milestone 4 Phase 1 — model fields and _ParseContext refactor
11b3b57 docs: add Milestone 4 plan, fixtures, and ROADMAP entry
67f8c7f chore: release v0.1.0 — rename to ledgerkit, add commodity styles and pandas export
b2d10be fix: correct column-0 comment handling inside open transaction blocks
8b5fc81 chore: release v0.5.0 and mark Milestone 3 done
```

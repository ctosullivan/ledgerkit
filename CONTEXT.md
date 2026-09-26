# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — design
document written, **stopped for explicit human approval.** No
`ledgerkit/`/`tests/` code touched. Resolves Stage C Phase 6's second
backlog item (the empty-regex fix, item 1, was Phase 7 — done).

## Where We Are
Design document: `dev-docs/planning/core-redefinition/27-query-shim-
convergence-design.md`. Planning retro: `dev-docs/retros/STAGE-C-
PHASE-8-QUERY-SHIM-PLAN.md`. `ROADMAP.md`/`CHANGELOG.md` updated for
the planning checkpoint. About to commit + push, then wait — do NOT
proceed to implementation until explicit approval arrives.

## Decisions In Flight
Design §12's approval gate, one genuinely blocking item:
1. **§6 — regex strictness**: Option A (`Query.account`/`not_account`/
   `payee` become fully `HledgerRegex`-strict, matching `-q`'s dialect
   exactly, including Stage C Phase 7's empty-pattern rejection) vs.
   Option B (keep the current permissive raw-Python-regex fallback).
   Lead recommends A — it's what the pre-approved `07-query-regex.md`
   §7.2 design actually specifies, and the real-world blast radius is
   confirmed empty (no external consumer, no existing test, uses an
   excluded construct). **Not decided.**
2. Compat-register entry naming (`LK-COMPAT-QUERY-SHIM-001`-shaped) —
   a naming detail, not blocking.
3. General approval to proceed to implementation.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/27-query-shim-convergence-
  design.md` — the design document awaiting approval.
- `ledgerkit/models.py:127-146` — the `Query` dataclass (frozen v1 API
  field shape, must not change).
- `ledgerkit/reports.py:215-292` — `_matches_pattern`/`_posting_matches`
  (to be retired) and `_effective_depth_spec` (already correct, `depth`
  handling untouched by this phase).
- `ledgerkit/query/ast.py:68-79` — `DateSpan` (`end` exclusive — the
  translation trap, §4 of the design).
- `dev-docs/planning/core-redefinition/07-query-regex.md` §7.2,
  `06-core-architecture.md` §6.5 — the pre-existing, already-approved
  architectural commitments this phase executes.
- `dev-docs/planning/core-redefinition/15-editor-compat-inventory.md`
  — confirms `ledgerkit-editor` never calls into Ledgerkit's own
  `Query`-matching code (the key de-risking fact).

## Blockers / Open Questions
Design §12 item 1 (regex strictness) is the only real blocker. Nothing
else outstanding.

## What NOT To Revisit
- Don't treat this phase's direction as an open design question — it's
  executing an already-approved target from Core-redefinition planning
  (`07-query-regex.md` §7.2), not deciding a new architecture from
  scratch.
- Don't assume `ledgerkit-editor` constrains this phase's internal
  matching-behaviour choice — confirmed it never calls into that code
  at all; it only depends on `Query`'s field shape (unchanged either
  way).
- Don't translate `Query.date_to` → `DateSpan(end=query.date_to)`
  directly — `DateSpan.end` is exclusive, `Query.date_to` is inclusive;
  the correct translation adds one day. This is the single most
  important implementation detail in this phase.
- Don't change `Query`'s dataclass fields, defaults, or report function
  signatures — out of scope entirely, frozen v1 API surface.
- Don't dispatch `context-curator` for this kind of work — established
  twice now (Phase 7's own correction) that its charter is narrowly
  CodeCompass-evaluation, not general Ledgerkit-architecture research.

## Recent Git State (before this response's commit)
afbcd05 test: independently verify Stage C Phase 7 empty-regex fix, resolve register
e3e00a1 feat: reject empty regex query patterns (Stage C Phase 7)
d88a777 docs: amend Stage C Phase 7 design -- targeted correction pass
c4feb1d docs: Stage C Phase 7 -- empty-regex-pattern rejection design
a49ac50 docs: close out Stage C Phase 6, mark [DONE]

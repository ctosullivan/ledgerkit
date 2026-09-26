# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C closeout (multi-step): Phase 7 is now `[DONE]` (its outstanding
docs-reconstructor + release-phase-auditor gates both ran clean).
`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` re-established fresh and a design
written — **implementation not started yet.** `PythonRegex` explicitly
resolved as deferred. Remaining Stage C backlog items confirmed
genuinely deferred/non-blocking. Stage C itself still `[IN PROGRESS]`.

## Where We Are
About to commit the Phase 7 closeout + Phase 9 planning + PythonRegex
disposition batch, then dispatch a fresh coding agent to implement
`28-empty-alternation-regex-design.md`, then independently verify, then
run the FULL Stage C completion audit sequence (compat-register review,
docs-maintainer, Stage-C-wide docs-reconstructor NO DRIFT,
roadmap/knowledge reconciliation, Stage-C-wide release-phase-auditor
against every exit criterion, closeout retro) before reporting whether
Stage C's Definition of Done is met.

## Decisions In Flight
None blocking. `PythonRegex` decision made (deferred). The empty-
alternation fix's design is fully specified (doubles as its own
implementation plan, per Phase 7's precedent) — next is implementation,
not a further design decision.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/28-empty-alternation-regex-design.md`
  — the fix spec: a dedicated, escape-aware scanning function
  (`_has_empty_alternation_branch`) in `ledgerkit/query/regex.py`,
  wired into `validate_hledger_regex` alongside the existing
  `pattern == ""` check and `_EXCLUDED_CONSTRUCT` scan.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`
  — freshly re-verified (2026-09-27), now has the complete 18-pattern
  reject-list and 13-pattern accept-list, plus the regex-tdfa root-cause
  citation. Still `kind: unexplained_mismatch`/`status: verified` (not
  yet resolved into a fix) — resolution happens via the schema.md
  lifecycle mechanism once implemented and independently verified.
- `dev-docs/retros/STAGE-C-PHASE-9-EMPTY-ALTERNATION-PLAN.md` — this
  phase's planning retro.
- `knowledge/DECISIONS.md` — new PythonRegex-deferral entry (2026-09-27).

## Remaining Stage C backlog after this fix lands
None substantive — this is the last item from Stage C Phase 6's own
backlog. Non-blocking, confirmed-deferred items (not exit-criteria
gaps): `cur:`, smart/period dates, a standalone `--depth`/`-N` CLI flag,
`PythonRegex` (now explicitly deferred, not ambiguous).

## Blockers / Open Questions
None. Proceeding directly to implementation per the user's explicit
"implement through the normal fresh-agent workflow" instruction — no
separate approval gate needed for this fully-specified fix.

## What NOT To Revisit
- Don't re-derive the empty-alternation detection rule — hand-verified
  against all 31 test cases (18 reject, 13 accept) already; it's a
  purely local, single-character-adjacency, escape-aware check, no
  nesting-depth tracking needed.
- Don't fold the new detection into `_EXCLUDED_CONSTRUCT`'s single
  regex — Python's `re` can't correctly count variable-length escape
  runs via lookbehind; a dedicated scanning function is the right shape.
- Don't re-litigate PythonRegex — explicitly resolved as deferred,
  reasoned, recorded. Don't implement it as part of this closeout.
- Don't treat `cur:`/smart-dates/`--depth`-flag/`check`-non-wiring as
  open questions — all four confirmed already-documented, deliberate,
  non-blocking deferrals.
- Don't mark Stage C `[DONE]` — only the user's explicit confirmation
  does that, after the full closeout audit sequence completes.

## Recent Git State (before this response's commit)
c5e4185 docs: close out Stage C Phase 8, mark [DONE]
12af5cf docs: reconcile Phase 8 docs after compat-register correction (Stage C Phase 8)
d12e24e fix: correct Stage C Phase 8 compat-register overclaim on accounts=[...]
38eefe0 test: independently verify Stage C Phase 8 Query-shim convergence
a4c5917 docs: retro, changelog, and roadmap for Query-shim implementation (Stage C Phase 8)

# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) is **`[DONE]`**
(user-confirmed 2026-09-26) — design, implementation, independent
verification, a compat-register overclaim correction with its own
independent re-verification, `docs-maintainer` reconciliation,
`docs-reconstructor` drift audit (NO DRIFT), and `release-phase-auditor`
Definition-of-Done audit (PASS) are all complete. Stage C itself remains
`[IN PROGRESS]`; not marked done.

## Where We Are
Everything committed and pushed to `main`. Full commit sequence for this
phase: `fbde262`→`baace1a` (design + amendments)→`dcac520`/`0852c6f`/
`7b9b358`/`a4c5917` (implementation/tests/docs/retro)→`38eefe0`
(independent verification)→`d12e24e` (overclaim correction + re-
verification + 2 new tests)→`12af5cf` (docs-maintainer reconciliation)→
this response's commit (closeout: `[DONE]` marking, knowledge entry).

899 tests passing throughout; unaffected by this closeout pass.

## Decisions In Flight
None. Phase 8 is closed. Next open decision is which Stage C backlog
item to scope next — not started here, per explicit instruction not to
begin the next phase in this task.

## Remaining Stage C backlog (unchanged, none scoped yet)
1. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — the empty-alternation-branch
   divergence (`(|)` confirmed both sides; `a|`/`|a`/`(a|)`/`(|a)`
   hledger-side only) — still open, still out of scope.
2. Explicitly resolve the planned `PythonRegex` extension syntax
   (implement / defer-with-reason / drop — currently just undecided).
Non-blocking, unscoped unless separately promoted: `cur:`, smart/period
dates, a standalone `--depth`/`-N` CLI flag.

One further, genuinely unrelated, pre-existing, out-of-scope item noted
by `docs-reconstructor` during Phase 8's drift audit (not caused by
Phase 8, not fixed here): `docs/python-api.md` line ~154's `Query`
field-table wording says depth "excludes deeper accounts" for
`accounts()`/`register()` — this predates Stage C Phase 5's `depth:`
redesign (which made depth a display-clipping option, never an
exclusion, for `register`) and was never corrected when that redesign
landed. Worth its own small fix, whenever convenient — not blocking
anything.

## Files Currently Relevant
- `dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml` — final state:
  `kind: compatible`, `status: verified`, corrected item-6 claim,
  independently re-verified twice.
- `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md` —
  base + two addenda (independent verification; overclaim-correction
  cycle).
- `knowledge/DECISIONS.md` — new entry on the process lesson from this
  phase's overclaim (verification checks what's tested, not every
  written claim — write narrower, more falsifiable compat-register
  claims going forward).

## Blockers / Open Questions
None blocking. The `docs/python-api.md` depth-wording item above is
open but non-blocking and unrelated to Phase 8.

## What NOT To Revisit
- Don't re-open Phase 8 — fully closed, user-confirmed `[DONE]`.
- Don't re-verify the Query-shim convergence or the corrected wrapper
  claim again — both independently confirmed clean, twice each.
- Don't mark Stage C itself `[DONE]` — only Phase 8 is done.
- Don't fix the pre-existing `docs/python-api.md` depth-wording drift as
  part of "Phase 8 cleanup" — it's unrelated, predates this phase, and
  was correctly left out of scope by the drift audit and release audit
  alike. Fix it separately if/when asked.
- When writing a future compat-register `reason:` field, avoid broad
  unfalsified claims ("preserved for every X") — name the specific
  cases actually verified instead (see the new `knowledge/DECISIONS.md`
  entry for the full rationale).

## Recent Git State (before this response's commit)
12af5cf docs: reconcile Phase 8 docs after compat-register correction (Stage C Phase 8)
d12e24e fix: correct Stage C Phase 8 compat-register overclaim on accounts=[...]
38eefe0 test: independently verify Stage C Phase 8 Query-shim convergence
a4c5917 docs: retro, changelog, and roadmap for Query-shim implementation (Stage C Phase 8)
7b9b358 docs: sync docs and compat-register for Query-shim convergence (Stage C Phase 8)

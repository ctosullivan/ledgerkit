# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:NAME[=REGEX]` query-term matching) is **`[DONE]`**
(user-confirmed 2026-09-25) — implementation, independent verification,
and closeout reconciliation all complete. Stage C itself remains
`[IN PROGRESS]`; not marked done. No `ledgerkit/`/`tests/` code changed
in this closeout pass — docs/status-only.

## Where We Are
Full commit sequence for this phase, on `main`, all pushed:
- `0523426` / `fa05bbc` — core implementation + tests + doc sync
- `cb06d1f` — implementer's own `CONTEXT.md` update
- `fe9dfe5` — independent `compat-differential-tester` verification
  (5/6 compat-register entries → `status: verified`)
- `5887ea8` — verification-results doc reconciliation
- (this response's commit) — closeout: Phase 6 marked `[DONE]` in
  `ROADMAP.md`, remaining Stage C backlog recorded, retro closeout
  addendum appended

827 tests passing throughout; unaffected by this closeout pass.

## Decisions In Flight
None. Phase 6 is closed. Next open decision is **which Stage C backlog
item to scope next** — recommended: the empty-regex compatibility fix
(smallest, most concretely characterised); see backlog below. This is
the user's call, not started here per explicit instruction not to begin
the next implementation phase in this task.

## Files Currently Relevant
- `ROADMAP.md` — Stage C row: Phase 6 `[DONE]`, remaining backlog listed
  inline at the end of the row.
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` —
  Addendum 2 (closeout) is the authoritative statement of the remaining
  Stage C backlog and the next-phase recommendation.
- `dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml` — still
  `status: proposed`, deliberately, for its one false `tag:NAME=` claim.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml`
  — the filed, unresolved, cross-cutting empty-regex divergence.

## Remaining Stage C backlog (not this phase's problem, recorded for
whoever scopes next)
1. Scope the cross-cutting empty-regex compatibility fix
   (`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`) — root cause
   `ledgerkit.query.regex.compile_hledger_regex`; affects `acct:`/
   `desc:`/`tag:` alike. **Recommended next phase to scope.**
2. Converge the legacy public `Query` pathway toward the query-AST/
   compatibility-shim architecture.
3. Explicitly resolve the planned `PythonRegex` extension syntax
   (implement / defer-with-reason / drop — currently just undecided).
Non-blocking, unscoped unless separately promoted: `cur:`, smart/period
dates, a standalone `--depth`/`-N` CLI flag.

## Blockers / Open Questions
None blocking. The backlog above is open work, not a blocker on
anything already shipped.

## What NOT To Revisit
- Don't re-open Phase 6 — implementation and independent verification
  are both done and confirmed by the user.
- Don't quietly fix `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` or promote
  `LK-COMPAT-QUERY-TAG-001` to `verified` in passing — it's explicitly
  scoped as its own future backlog item (#1 above), not something to
  absorb into unrelated work.
- Don't mark Stage C itself `[DONE]` — only Phase 6 is done; Phase-level
  completion within Stage C does not imply Stage-level completion, and
  the user was explicit that Stage C stays `[IN PROGRESS]`.
- Don't start implementing any of the three backlog items without a
  fresh scoping/design pass — none of them has one yet, matching the
  project's own design → plan → implement → verify process for anything
  non-trivial.

## Recent Git State (before this response's commit)
5887ea8 docs: close out Stage C Phase 6 independent verification
fe9dfe5 test: independently verify Stage C Phase 6 tag: compat-register entries
cb06d1f docs: update CONTEXT.md for Stage C Phase 6 implementation end state
fa05bbc test: add tag: integration tests, compat-register entries, retro
0523426 feat: implement tag:NAME[=REGEX] query matching (Stage C Phase 6)

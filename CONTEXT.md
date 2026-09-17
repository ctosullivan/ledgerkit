# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 5 is a **planning-only** pass (no code touched), resolving
two issues the user identified in recent Stage C work: verification
independence for compatibility claims, and `depth:`'s modelling as a
pure boolean predicate. Plan document written and awaiting the six
explicit human-decision gates it names — not started.

## Where We Are
Plan complete: `dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md`. Retro written:
`dev-docs/retros/STAGE-C-PHASE-5-PLAN.md`. `ROADMAP.md`, `CHANGELOG.md`
updated. Next step is entirely the user's: resolve gates G-DEPTH-1..4
and G-PROCESS-1..2 (plan §9), then implementation (plan §8, Phases
5a-5d) can begin. Nothing to do until then unless the user wants to
discuss/adjust the plan itself.

## Decisions In Flight
- None yet — every substantive call in this phase is one of the six
  named gates, deliberately left open for the user, not decided by the
  lead. Do not pre-resolve any of them unilaterally when implementation
  starts, even if one answer seems obviously preferable.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/
  21-stage-c-phase-5-depth-and-verification-plan.md` — the plan; read
  §9 first for the open gates, §8 for phase sequencing once gates are
  resolved.
- `dev-docs/retros/STAGE-C-PHASE-5-PLAN.md` — this planning pass's retro.
- `ledgerkit/reports.py` (lines ~241-410) — contains the existing,
  correct `Query.depth` truncation logic the plan's design unifies with,
  and the self-diagnosing docstrings that flagged the inconsistency.
- `ledgerkit/query/ast.py`, `eval.py`, `parser.py` — where `Depth`
  currently lives and will change per G-DEPTH-1/3.
- `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`,
  `dev-docs/compat-register/schema.md`,
  `dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.4
  — the entry to be reclassified, and the process docs §2's amendment
  targets (not yet edited — proposed only).

## Blockers / Open Questions
All six are open, none pre-resolved by this session (plan §9):
- G-DEPTH-1: approve the `DepthSpec` report-option model (vs. keeping
  Depth as a QueryNode).
- G-DEPTH-2: `Query.depth`/`ReportSection.depth`'s public shape — stay
  flat-only, or retype to the richer `DepthSpec` (breaking change).
- G-DEPTH-3: fate of the current boolean-exclusion `ast.Depth` node —
  remove / rename-and-keep-Python-API-only (recommended) / new
  non-colliding string token.
- G-DEPTH-4: standalone `--depth`/`-N` CLI flag in this phase or deferred.
- G-PROCESS-1: approve the tiered verification-independence rule
  (four-value `status` enum incl. `self-verified`) as specified.
- G-PROCESS-2: relabel the 11 existing lead-self-verified entries to
  `self-verified` now (cheap) vs. real `compat-differential-tester`
  re-dispatch on all 11 immediately (thorough, costlier).

## What NOT To Revisit
- Stage A, Stage B, and Stage C Phases 1-4 are closed/committed. This
  Phase 5 planning pass has NOT been committed yet (see Recent Git State
  below) — still pending in this response.
- Don't re-derive the `depth:` behavioural findings — 14 scenarios were
  differentially tested this session against the pinned 1.52.4 binary
  and cross-checked against `hledger-lib` source directly (every
  command's `Query` consumption traced, not just the `Depth` constructor
  itself); the plan's §1.3/§6 are primary evidence, not a summary to
  re-verify from scratch next session.
- Don't assume `tag:` query-term work (deferred at end of Phase 4) is
  what Phase 5 is about — Phase 5 is verification-process + `depth:`
  only; `tag:` remains separately unscoped.
- Don't mark any compat-register entry `status: verified` directly from
  the lead session once implementation starts — that is now explicitly
  the point of this whole phase; use `self-verified` if independent
  dispatch is deferred, and say so honestly.

## Recent Git State (before this response's commit, if any)
fd144ed feat: Stage C Phase 4 -- tag data model (parsing/storage)
d362bbb feat: Stage C Phase 3 -- wire -q/--query into print
b7d5d32 docs: Stage C Phase 2, commit 3/3 -- context evaluation + closeout
27c410d feat: Stage C Phase 2, commit 2/3 -- query/report/CLI integration
0f4465d docs: Stage C Phase 2, commit 1/3 -- CodeCompass baseline

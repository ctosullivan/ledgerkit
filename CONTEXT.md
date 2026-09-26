# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — **implementation
and independent verification both complete.** `LK-COMPAT-QUERY-SHIM-001`
promoted to `status: verified`. `[DONE]` for the phase is the user's own
call, not inferred here.

## Where We Are
Everything committed and pushed to `main`:
- `dcac520`/`0852c6f`/`7b9b358`/`a4c5917` — implementation, tests, doc
  sync, retro/changelog/roadmap (all four from the implementing agent)
- This response's commit (about to land) — independent verification
  results: `LK-COMPAT-QUERY-SHIM-001.yaml` promoted to `verified`, new
  fixture `tests/fixtures/query_shim_differential.journal`, retro
  addendum, ROADMAP/CHANGELOG updates.

897 tests passing throughout (up from 844 before this phase).

## Decisions In Flight
None blocking. Two things await a human call, neither urgent:
- Whether/when to mark Stage C Phase 8 `[DONE]` in `ROADMAP.md` — user's
  own call, not inferred by Claude.
- What Stage C's next phase should be — the backlog (below) has three
  named items, none yet scoped.

## Compat-register final state (this phase)
- `LK-COMPAT-QUERY-SHIM-001` — `kind: compatible`, `status: verified`,
  independently confirmed on all eight of the design's highest-risk
  claims (Query/-q parity, stats's new narrowing, balance_from_spec/
  ReportSection strictness, to_dataframe's eager validation, the
  deprecated accounts=[...] shim's zero/one/many cases, date.max, and
  ordinary inclusive date_to).

## Files Currently Relevant
- `dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml` — now
  `status: verified`.
- `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md` —
  implementation retro + verification addendum, both dated 2026-09-26.
- `ledgerkit/query/compat.py` — the new translator module
  (`_query_to_ast`/`_validated`/`_exclusive_end`), now independently
  verified.
- `tests/fixtures/query_shim_differential.journal` — the independent
  verification's own fresh fixture.

## Remaining Stage C backlog (unchanged, none scoped yet)
1. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — the empty-alternation-branch
   divergence (`(|)` confirmed both sides; `a|`/`|a`/`(a|)`/`(|a)`
   hledger-side only) — still open, still out of scope.
2. Explicitly resolve the planned `PythonRegex` extension syntax
   (implement / defer-with-reason / drop — currently just undecided).
Non-blocking, unscoped unless separately promoted: `cur:`, smart/period
dates, a standalone `--depth`/`-N` CLI flag.

## Blockers / Open Questions
None blocking further work on this phase — it's complete.

## What NOT To Revisit
- Don't re-verify the Query-shim convergence — independently confirmed
  clean, no discrepancies, full 8-point matrix covered.
- Don't re-derive the zero-accounts-must-not-become-`Or(())` fix — now
  confirmed independently, twice (design review + verification dispatch).
- Don't touch `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — separate,
  unrelated, explicitly out of scope, still open.
- Don't mark Stage C Phase 8 `[DONE]` unilaterally — only the user's
  explicit statement does that, per CLAUDE.md's standing rule.

## Recent Git State (before this response's commit)
a4c5917 docs: retro, changelog, and roadmap for Query-shim implementation (Stage C Phase 8)
7b9b358 docs: sync docs and compat-register for Query-shim convergence (Stage C Phase 8)
0852c6f test: cover Query-shim convergence (Stage C Phase 8)
dcac520 feat: converge Query filtering onto the canonical query engine (Stage C Phase 8)
baace1a docs: amend Stage C Phase 8 design a second time -- final correction pass

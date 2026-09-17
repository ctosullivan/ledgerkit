# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 5 (verification independence + `depth:` redesign) is done
— all three commits complete, independently verified. About to commit
this closeout and push.

## Where We Are
Full closeout complete: process amendment committed (`17d7bcb`), `depth:`
redesign committed (`e8f3633`), independent verification by a genuinely
separate `compat-differential-tester` dispatch completed (no mismatches;
`LK-COMPAT-QUERY-DEPTH-001`/`LK-COMPAT-QUERY-DEPTH-STATS-001`/
`LK-COMPAT-QUERY-PRINT-INTEGRATION-001` promoted `self-verified` →
`verified`). Retro written: `dev-docs/retros/STAGE-C-PHASE-5.md`.
`ROADMAP.md`/`CHANGELOG.md` updated. 746 tests passing. Next: final
commit (this closeout: retro, ROADMAP, CHANGELOG, CONTEXT,
hledger-compatibility.md citation fix) + push.

## Decisions In Flight
- None — all six gates from the plan were resolved and recorded in
  `knowledge/DECISIONS.md`; nothing left open from this phase.

## Files Currently Relevant
- `ledgerkit/query/depth.py` — the new `DepthSpec` module.
- `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`,
  `LK-COMPAT-QUERY-DEPTH-STATS-001.yaml`,
  `LK-COMPAT-QUERY-PRINT-INTEGRATION-001.yaml` — all now `status:
  verified` (independently).
- `tests/fixtures/depth.journal` — new fixture, added by the independent
  verification dispatch, now a permanent part of the test suite's
  fixture set.
- `dev-docs/retros/STAGE-C-PHASE-5.md` — this phase's retro.

## Blockers / Open Questions
- Named, unscoped candidates for a future phase: `tag:` query-term
  matching (deferred since end of Phase 4), `cur:`, `PythonRegex`
  extension syntax, the larger `Query`-as-compatibility-shim migration,
  and a standalone `--depth`/`-N` CLI flag (this phase's own G-DEPTH-4
  deferral — `-q "depth:N"` already gives full access to the corrected
  semantics, so this is a convenience addition, not a defect fix).
  None started; next phase needs its own explicit scoping.
- `check` remains the only report/display command without `-q` — by
  design, unrelated to this phase.

## What NOT To Revisit
- Stage A, Stage B, and Stage C Phases 1-5 are all closed/committed
  (Phase 5's final commit about to be, this response).
- Don't re-litigate the `depth:` semantic model (`DepthSpec` as a report
  option, never a `QueryNode`) — explicitly user-approved via all six
  gates, then independently verified against the pinned binary on a new
  fixture. Two full rounds of executable evidence exist.
- Don't re-run this phase's differential verification — done twice
  (self-verified during implementation, then independently by a separate
  `compat-differential-tester` dispatch), both committed with full
  evidence in the register entries themselves.
- Don't treat `stats`' depth-EXCLUSION behaviour (unlike every other
  depth-aware command, which clips) as a bug to "fix" toward consistency
  — it's a deliberate, source-confirmed, independently-verified
  replication of a genuine hledger quirk (`Ledger.hs:ledgerFromJournal`).
- Don't write `status: verified` into a compat-register entry directly
  from a lead session again — that is now the entire point of this
  phase's own process amendment (`09-compatibility-system.md` §9.6). Use
  `self-verified` if a dispatch is deferred, and say so honestly.

## Recent Git State (before this response's commit, if any)
e8f3633 feat: Stage C Phase 5, commit 2/N -- redesign depth: as a report option
17d7bcb docs: Stage C Phase 5, commit 1/N -- verification independence process
fd144ed feat: Stage C Phase 4 -- tag data model (parsing/storage)
d362bbb feat: Stage C Phase 3 -- wire -q/--query into print
b7d5d32 docs: Stage C Phase 2, commit 3/3 -- context evaluation + closeout

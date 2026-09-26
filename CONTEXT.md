# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C closeout, final stretch. All nine phases implemented and
independently verified; zero open `unexplained_mismatch` entries; a
Stage-C-wide `docs-maintainer` reconciliation pass ran (`359eb53`,
found and fixed 6 real issues), a follow-up fix for a stale ROADMAP
paragraph it flagged but couldn't touch (`301a42d`), and a Stage-C-wide
independent `docs-reconstructor` drift audit ran and found 4 further
minor findings — just fixed directly (this response). **Re-audit is
the next step**, per the standing "resolve and re-audit until clean"
instruction. Stage C itself still `[IN PROGRESS]`.

## Where We Are
About to commit the four drift-audit fixes, then re-dispatch
`docs-reconstructor` to confirm NO DRIFT (not assumed — the standing
instruction is explicit: re-audit until clean, don't just fix and
move on). Only after a clean NO-DRIFT verdict should the final
Stage-C-wide `release-phase-auditor` pass run, followed by a substantive
Stage C closeout retro, and then reporting to the user whether Stage
C's Definition of Done is met.

## Decisions In Flight
None. All four just-fixed findings were mechanical corrections
(a stale class-name reference, a doc clarifying which `accounts()`
accepts `query=`, a missing changelog entry, a stale CONTEXT.md) — no
judgment calls needed.

## The four findings just fixed (for the re-audit to confirm)
1. `dev-docs/api-spec.md` — `"Depth's predicate..."` → `"MaxAccountLevel's
   predicate..."` (a leftover pre-Phase-5-rename reference).
2. `docs/python-api.md` — the `Query.depth` field row wrongly implied
   `accounts()` (meaning `Journal.accounts()`) accepts depth rollup via
   `query=`; it takes no parameters at all. Clarified that the
   module-level `ledgerkit.reports.accounts(journal, query=...)` is the
   actual entry point for that behaviour, not the `Journal` method.
3. `CHANGELOG.md` — added the missing entry for commit `301a42d`
   (removing a stale duplicate ROADMAP paragraph), which had no
   corresponding changelog entry when it landed.
4. `CONTEXT.md` (this file) — was stale, listing the Stage-wide
   `docs-maintainer` pass and `docs-reconstructor` audit as "not yet
   run" when both had already happened by the time it was last read.

## Files Currently Relevant
- `dev-docs/compat-register/UNEXPLAINED.md` — "Open entries" confirmed
  empty by both the implementing session and the independent drift
  audit. Re-confirm during the upcoming release-phase audit too.
- `ROADMAP.md` — Stage C row confirmed by the drift audit to be a single,
  coherent, non-duplicated narrative across all nine phases.

## What's left before reporting on Stage C's Definition of Done
1. Re-run `docs-reconstructor` (Stage-C-wide) to confirm NO DRIFT after
   this response's four fixes — do not assume clean, verify.
2. Independent `release-phase-auditor` pass against Stage C's own
   Definition of Done (every phase done, every exit criterion met, zero
   unexplained mismatches, no protected-file violations, substantive
   retros throughout, clean commit/push history).
3. A substantive Stage C closeout retro (distinct from any individual
   phase's own retro) and a final CHANGELOG entry.
4. Report to the user: DoD met or not, and explicitly recommend (not
   decide) whether Stage C is ready for `[DONE]` confirmation.

## Blockers / Open Questions
None. Proceeding directly through the remaining audit sequence.

## What NOT To Revisit
- Don't re-derive the empty-alternation fix, the Query-shim convergence,
  or any of Stage C's nine phases' own substantive decisions — all
  independently verified, some more than once.
- Don't re-litigate `PythonRegex`, `cur:`, smart-dates, the `--depth`
  flag, or `check`'s non-wiring — all explicitly resolved/confirmed
  deferred.
- Don't mark Stage C `[DONE]` — that is the final human gate.
- Don't skip the re-audit step after fixing the four findings — the
  user's own instruction is explicit about re-auditing until clean, not
  just fixing once and assuming it worked.

## Recent Git State (before this response's commit)
301a42d docs: remove stale duplicate Phase 9 status paragraph from ROADMAP
359eb53 docs: Stage-C-wide docs-maintainer reconciliation
9fd0166 test: independently verify Stage C Phase 9, resolve last mismatch
e994eac docs: sync docs and compat-register for Stage C Phase 9 implementation
60eea4a feat: reject empty-alternation-branch regex patterns (Stage C Phase 9)

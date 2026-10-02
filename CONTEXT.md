# CONTEXT.md — Claude Session Working Memory

## Current Task
Implementing the twice-amended Plan 29
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`) straight through to closeout. **Phases 1 and 2 are
done.** About to begin Phase 3 (evidence-backed clean-room
reconstruction, plan §4) — the real per-topic pipeline.

## Where We Are
Phase 2 complete: clean-room template adopted into `dev-docs/clean-room/`;
`check_snapshot.py` built and self-tested (7/7 fixture cases correct,
including both historical-integrity checks); isolation preflight run,
honest tier recorded as `best-effort` (filesystem/command/network all
directly demonstrated open; same host confirmed). Retro: `dev-docs/
retros/CODECOMPASS-UPGRADE-PHASE-2.md`. Plan 29 §13 updated. Next: Phase
3, topic by topic (plan §4.1's table, 10 rows) — for each: dispatch a
fresh, evidence-only assertion-research agent (bounded topic + permitted
evidence paths + output format only — never this plan's prose, never
legacy docs) → immediately inspect its transcript for compliance → if
contaminated, discard and rerun; log to `dev-docs/clean-room/
compliance-log.md` (not created yet — first Phase 3 action creates it)
→ `domain-skeptic` REVIEW mode → freeze snapshot + sidecar → run
`check_snapshot.py` → fresh `implementation-reconstructor` dispatch →
immediate transcript check → `domain-skeptic` COMPARISON mode.

## Decisions In Flight
- The isolation preflight probe ran as `general-purpose` rather than the
  two new named types, since they weren't yet dispatchable
  `subagent_type` values at the moment the probe was dispatched (they
  became available moments later, confirmed by a system notification
  mid-Phase-2). Judgment call: not re-running the probe under the new
  types, since the three routes that matter (filesystem/command/
  network) are already conclusively open via tools (`Read`, `Bash`)
  every real dispatch has regardless of named type — recorded in the
  Phase 2 retro, not silently glossed over.
- **`implementation-reconstructor` and `domain-skeptic` ARE now real,
  dispatchable `subagent_type` values** (confirmed via a system
  notification during Phase 2) — Phase 3 dispatches should use them by
  name directly, not `general-purpose` with an embedded brief as
  originally planned as a fallback.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
  room-docs.md` — §4 (whole Phase 3), §4.1 (the 10-topic table), §4.2
  (the exact per-topic pipeline), §4.2a (the compliance-check
  procedure).
- `dev-docs/clean-room/assertions/TEMPLATE.md` — the assertion format,
  including the `Evidence-paths:` machine-checkable convention Phase 2
  added.
- `dev-docs/clean-room/check_snapshot.py` — run against every frozen
  snapshot before treating it as frozen (`python dev-docs/clean-room/
  check_snapshot.py <topic>`).
- `dev-docs/clean-room/isolation-preflight.md` — the honest `best-effort`
  baseline Phase 6 will audit against.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction.

## What NOT To Revisit
- Don't re-run the isolation preflight under the new agent types —
  judgment call made and recorded in the Phase 2 retro; the conclusion
  (`best-effort`) is already fully supported.
- Don't let the main orchestrating session author Phase 3 assertions
  directly — every topic's assertion-research dispatch must be a fresh
  `Agent` call (never a `fork`), receiving only the bounded topic,
  permitted evidence paths, and output format.
- Don't skip the immediate post-dispatch transcript check for any Phase
  3/4 dispatch, and don't defer it to Phase 6 — log every verdict to
  `dev-docs/clean-room/compliance-log.md` as it happens.
- Don't validate a snapshot against today's working tree —
  `check_snapshot.py` already resolves cited evidence against the
  frozen git revision's own tree; trust it, don't hand-wave a check.
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
0c89ceb feat(codecompass-upgrade-phase-1): CodeCompass reconciliation + enforced revision pinning
4277036 docs: second amendment to CodeCompass/clean-room plan, approved to implement
e1b0144 docs: amend CodeCompass upgrade + clean-room docs plan per review
7032b3e docs: plan CodeCompass upgrade + clean-room docs reconstruction
6c90b4c docs: mark Stage C [DONE], archive its changelog history

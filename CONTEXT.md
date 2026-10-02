# CONTEXT.md — Claude Session Working Memory

## Current Task
`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md` has been amended twice (both 2026-10-02) and is now
**approved to implement directly** — no further planning round-trip.
About to begin Phase 1 (CodeCompass reconciliation & enforced revision
pinning, plan §2).

## Where We Are
Plan amendment committed. Beginning Phase 1 implementation per plan §2:
pin `codecompass`/`codecompass-template` SHAs (§2.0), enforce the pin
mechanically (dedicated worktree or guard script, §2.0 steps 5–7),
re-sync/index/check (§2.1), reconcile the four existing agent briefs
(§2.2), add `implementation-reconstructor.md`/`domain-skeptic.md`
(§2.3), fix `CLAUDE.md`'s stale folder-structure diagram (§2.4), update
`04-codecompass-integration.md`, run tests, write the Phase 1 retro,
commit+push.

## Decisions In Flight
None from the plan itself — both amendments resolved everything open.
Implementation-time judgment calls will be recorded here as they're
made (e.g. dedicated-worktree vs. guard-script pin enforcement; exact
dispatch mechanics for the plan's "fresh `Agent` dispatch, never a
`fork`" requirement in Phase 3/4 — using `subagent_type: "general-purpose"`
with a self-contained prompt, since `implementation-reconstructor`/
`domain-skeptic` are new roles not yet in this session's recognized
`subagent_type` list even after their brief files are created).

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
  room-docs.md` — the governing plan, now twice-amended. Key sections for
  Phase 1: §2 (whole phase), §2.0 (pin + enforcement), §2.5 (acceptance
  criteria), §13 (implementation log — update after each phase).
- `dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-PLAN.md` — the
  planning-phase retro, now with two dated addenda. Implementation gets
  its own separate retro per phase
  (`dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-<N>.md`), not more addenda
  here.
- `/home/cormac/projects/codecompass` — local clone; Phase 1's first
  concrete action is fetching and pinning this (and a fresh
  `codecompass-template` clone) per plan §2.0.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction.

## What NOT To Revisit
- Don't re-litigate any of the plan's open questions, first-review
  findings (§8 Part A/B), or second-review corrections (§8 Part C) — all
  resolved and fixed in place.
- Don't let the main orchestrating session author Phase 3 assertions
  directly, regardless of confidence — §4.2's structural rule (§8 Finding
  C1) is the sharpest correction in this round; re-read it before
  starting Phase 3.
- Don't defer contamination discovery to Phase 6 — §4.2a/§5.4 require an
  immediate post-dispatch transcript check, logged to
  `dev-docs/clean-room/compliance-log.md`, for every isolation-sensitive
  Phase 3/4 dispatch (§8 Finding C4).
- Don't validate a snapshot against today's working tree — `check_
  snapshot.py` must resolve cited evidence against the frozen git
  revision's own tree (§8 Finding C3).
- Don't record the CodeCompass/template pin without enforcing it — §2.0
  requires either a dedicated worktree or a guard script that stops on
  mismatch (§8 Finding C2).
- Don't treat `CHANGELOG.md`/`CONTEXT.md`/retros/`knowledge/*.md` as
  clean-room reconciliation targets — they're `intentionally retained`
  and only get ordinary workflow bookkeeping, per new §5.1a (§8 Finding
  C5). This CONTEXT.md overwrite, for instance, is exactly that kind of
  ordinary bookkeeping, not a clean-room artifact.
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
e1b0144 docs: amend CodeCompass upgrade + clean-room docs plan per review
7032b3e docs: plan CodeCompass upgrade + clean-room docs reconstruction
6c90b4c docs: mark Stage C [DONE], archive its changelog history
ea08a67 docs: Stage C closeout retro -- Definition of Done met
29e0233 docs: fix stale Depth reference in matches_posting's own docstring

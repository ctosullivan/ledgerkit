# CONTEXT.md — Claude Session Working Memory

## Current Task
Implementing the twice-amended Plan 29
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`) straight through to closeout, per direct user
instruction. **Phase 1 is done.** About to begin Phase 2 (isolation
workflow adoption + snapshot checker, plan §3).

## Where We Are
Phase 1 complete: CodeCompass/`codecompass-template` pinned and
mechanically enforced; re-synced (confirmed Stage C source represented);
four agent briefs reconciled; `implementation-reconstructor`/
`domain-skeptic` added; `CLAUDE.md`'s folder-structure diagram corrected.
Retro: `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md`. Plan 29's own
§13 implementation log updated to reflect Phase 1 done. Next: Phase 2 —
copy the pinned `codecompass-template`'s `optional-clean-room-workflow/`
into `dev-docs/clean-room/` (plan §3.1); write `check_snapshot.py` with
historical-integrity semantics (plan §3.7); run the isolation preflight
probe against the exact dispatch configuration Phase 3 will use (plan
§3.3); record the honest tier.

## Decisions In Flight
- Pin enforcement uses a guard script
  (`dev-docs/clean-room/check_codecompass_pin.sh`), not a dedicated
  worktree — recorded rationale in `PINNED-REVISIONS.md` (the global
  `pipx install -e` is shared with CodeCompass's own active
  development; repointing it would have a blast radius outside this
  repository for no extra isolation benefit).
- `codecompass sync`'s Phase B AI-enrichment prompt is declined (not
  forced via `--yes`) throughout this initiative — no API key is
  configured, and Ledgerkit has zero tracked vendors to enrich; declining
  still lets the mechanical graph rebuild and artifact regeneration
  complete (confirmed from `codecompass`'s own `cli.py` source: the
  rebuild happens before the enrichment trigger, and artifact
  regeneration runs in a `finally` block regardless).

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
  room-docs.md` — the governing plan; §13 tracks phase-by-phase
  progress. For Phase 2: §3 (whole phase), §3.1 (template adoption),
  §3.7 (checker spec), §3.3/§3.4 (preflight probe + honest tier
  reporting).
- `dev-docs/clean-room/PINNED-REVISIONS.md` — the two pins; every
  CodeCompass-dependent command from here on must pass
  `check_codecompass_pin.sh` first.
- `/home/cormac/projects/codecompass-template` — freshly cloned, pinned
  at `68bae8ec739aea413bbedac9f19078f6ab995aca`; Phase 2 copies its
  `optional-clean-room-workflow/` directory from here.
- `.claude/agents/{implementation-reconstructor,domain-skeptic}.md` —
  new this phase; first real exercise is Phase 3's dispatches, not yet
  used.

## Blockers / Open Questions
None. Proceeding directly per explicit instruction.

## What NOT To Revisit
- Don't re-pin CodeCompass/`codecompass-template` — already pinned and
  enforced this phase; only change on an explicit, new, recorded
  decision (plan §2.0 step 4).
- Don't re-litigate the guard-script-vs-worktree choice — recorded and
  justified in `PINNED-REVISIONS.md`.
- Don't attempt `codecompass sync --yes` expecting AI enrichment to
  work — no API key is configured; decline the prompt, which is
  sufficient for this initiative's needs.
- Don't let the main orchestrating session author Phase 3 assertions
  directly — plan §4.2's structural rule (a fresh, evidence-only `Agent`
  dispatch, never a `fork`) applies starting Phase 3, not yet exercised.
- Don't defer contamination discovery to Phase 6 — plan §4.2a/§5.4
  require an immediate post-dispatch transcript check from Phase 3
  onward, logged to `dev-docs/clean-room/compliance-log.md` (doesn't
  exist yet — Phase 2 or Phase 3 creates it).
- Don't begin Stage D as part of this task.

## Recent Git State (before this response's commit)
4277036 docs: second amendment to CodeCompass/clean-room plan, approved to implement
e1b0144 docs: amend CodeCompass upgrade + clean-room docs plan per review
7032b3e docs: plan CodeCompass upgrade + clean-room docs reconstruction
6c90b4c docs: mark Stage C [DONE], archive its changelog history
ea08a67 docs: Stage C closeout retro -- Definition of Done met

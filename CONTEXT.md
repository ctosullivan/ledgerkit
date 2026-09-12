# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage A (development foundation) is complete — user explicitly confirmed
`[DONE]` on 2026-09-12. This response commits and pushes all Stage A work
(agent roster, compatibility-register harness, licence migration/roadmap
migration already committed in prior sessions) and archives the changelog.

## Where We Are
Everything staged for one commit: 7 agent-role files, 25 compat-register
entries + harness scaffolding, `.gitignore` fix, and full doc-sync
(`ROADMAP.md` Stage A → `[DONE]`, `CHANGELOG.md` archived to
`dev-docs/changelog/STAGE-A.md`, `knowledge/DECISIONS.md`, the
core-redefinition planning README's status line). About to commit, then
push to `origin/main`. Full test suite passes (575 tests) — no
`ledgerkit/`/`tests/` code was touched this phase.

## Decisions In Flight
- None new this response — the register-migration-scope decision from the
  prior response is already recorded in `knowledge/DECISIONS.md`.

## Files Currently Relevant
- `dev-docs/changelog/STAGE-A.md` — new archive file (both Stage A
  changelog entries, oldest first)
- `CHANGELOG.md` — the two raw entries replaced with one summary block
  pointing at the archive
- `ROADMAP.md` — Stage A row now `[DONE]`
- `dev-docs/planning/core-redefinition/README.md` — status header updated
  to `[STAGE A — DONE]`
- Everything else from the prior response is unchanged content, now being
  committed for the first time.

## Blockers / Open Questions
- Stage B has not been scoped or approved for implementation yet —
  `ROADMAP.md`'s own process requires confirming its scope before work
  starts (G5 was only "in principle" approval, not authorisation).
- No pinned local hledger clone/binary exists in this environment — will
  be needed once `compat-differential-tester` has real work to do
  (Stage C onward).
- The finer-grained hledger-compatibility.md rows (dates, amount formats,
  comment forms, account-name rules) are still unmigrated into the
  compat-register — open follow-up, not a blocker.

## What NOT To Revisit
- Stage A's scope and completion status are settled — don't re-litigate
  whether the representative-first-wave register migration "really"
  finished Stage A; the user explicitly confirmed it did.
- Don't re-ask which register-migration option to use — already answered
  and executed.

## Recent Git State (before this response's commit)
e702497 fix: revert pyproject.toml license to classic form for Python 3.8 CI
67436ec chore: relicense to GPL-3.0-or-later, redefine Core goal and roadmap
572e77b fix: correct YAML syntax in publish workflow
440f570 chore: sync __version__ to 1.0.0.dev1 and update publish workflow
0004c1a chore: bump to 1.0.0.dev1 for TestPyPI test

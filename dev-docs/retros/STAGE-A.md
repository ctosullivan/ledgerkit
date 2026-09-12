# Stage A retro — Development Foundation

- **Date:** 2026-09-12
- **Commit(s):** 67436ec, e702497, a3cf2a7
- **Agents used:** none yet formally dispatched this stage (the roster
  itself — `.claude/agents/*.md` — was Stage A's own deliverable; a plain
  session did the work that would now route through `roadmap-context-curator`
  and `release-phase-auditor`)

## Where we are

Stage A is the first stage of the Core-redefinition roadmap
(`ROADMAP.md`), replacing the old Milestone 5 (superseded) as the next
unit of work after Milestone 4 shipped `1.0.0`. There was no "previous
Stage" to build on — Stage A *is* the foundation: it relicensed the
project, redefined the product goal, migrated the roadmap structure, and
built the agent roster and compatibility-register harness that every
later Stage (B onward) depends on. After this stage, ledgerkit has: a
GPL-3.0-or-later licence matching hledger's own, a documented Core goal,
a Stage A–I roadmap, seven agent-role definitions, and a 25-entry
first-wave compatibility register (`status: proposed`, not yet
executable-verified). Stage B (Core model) is next and unblocked.

## Goal

Close out the remaining Stage A scope: relicense to match hledger, redefine
the Core product goal, migrate `ROADMAP.md` to the Stage A–I structure,
build the seven-role agent roster, and stand up the compatibility-register
harness with a first wave of real entries — per
`dev-docs/planning/core-redefinition/03-agent-led-development.md` and
`09-compatibility-system.md`.

## Scope delivered vs planned

Shipped: the licence migration (with `NOTICE`/`THIRD-PARTY-NOTICES.md`),
the Core goal redefinition, the full roadmap migration (Milestones 0–4
retained as history, Milestone 5 superseded), all seven agent-role files,
and the compat-register harness (`UNEXPLAINED.md`, `directly_translated`
schema field, 25 entries: 12 directive, 8 validation-check, 5
unsupported-feature).

One deliberate scope-down, decided by explicit user choice among three
offered options: the compat-register migration was scoped to a
*representative first wave* (directives, checks, unsupported features)
rather than every row of `hledger-compatibility.md`'s In-Scope/Out-of-Scope
tables (~57 entries total). The finer-grained rows — date formats, amount
formats, comment forms, account-name rules — were **not** migrated this
phase; tracked as open follow-up in `ROADMAP.md` and `knowledge/
DECISIONS.md`, not silently dropped.

One unplanned deviation, caught and fixed within the phase: a first attempt
at the licence-field change used a PEP 639 SPDX string
(`license = "GPL-3.0-or-later"`), which passed locally but broke the Python
3.8 CI job (no `setuptools` release supports both 3.8 and that string
form). Reverted to the classic dict form (`{text = "..."}`) in a follow-up
commit (`e702497`) rather than dropping 3.8 support, which would have been
a separate, unapproved policy decision.

## What was achieved

`.claude/agents/` now exists with seven concrete, scoped role definitions.
`dev-docs/compat-register/` exists as a real, if partial, structured
alternative to prose-only compatibility claims — 25 entries with recorded
provenance, ready for `compat-differential-tester` to move from `proposed`
to `verified` once a pinned hledger binary exists (Stage C+). The project
is now licensed compatibly with using hledger's own source/docs/tests
directly as evidence, which every later Stage's compatibility work depends
on.

## What worked

- **Putting the register-migration scope choice to the user directly**
  (full vs. representative vs. harness-only) instead of unilaterally
  picking a fraction or unilaterally expanding to all 57 rows. This avoided
  both quietly under-delivering and silently over-scoping a single
  response.
- **Fixing the CI-breaking licence-field regression in the same phase**
  rather than merging a red pipeline and treating it as a later cleanup —
  cost one extra commit, not a deferred bug.
- **Precedent-matching an existing sibling project's `.claude/agents/`
  tracking pattern** (narrowing `.gitignore`'s blanket `.claude/` rule to
  `.claude/*` + `!.claude/agents/`) instead of inventing a new convention
  from scratch.

## What didn't work

No significant misfires this phase — the one rework (the licence-field
revert) was caught and fixed within the same short window, not discovered
later as drift.

## Lessons learnt

A "migrate every row" instruction against a real prose table should be
sized before committing to it — ~57 rows each needing a real grepped
citation is a materially different effort than mechanical transcription,
and that difference is worth surfacing to the user as an explicit choice
rather than absorbing silently in either direction. Also: a licence-field
format choice (classic dict vs. PEP 639 string) has non-obvious tooling
constraints tied to the Python-version support matrix — verify against the
*oldest* supported Python/setuptools combination before treating a locally-
passing change as done.

## Process-improvement feedback

Stage A closed out with **no dedicated retro process in place** — this
retro was written retroactively, after the fact, once the user asked
whether ledgerkit had a convention like the sibling `codecompass` project's
and then asked to adopt one. That's exactly the gap the newly-adopted
`dev-docs/retros/` process (`knowledge/DECISIONS.md`, 2026-09-12) closes:
going forward, the retro is authored in the same response as the `[DONE]`
confirmation, not reconstructed later from the changelog archive and
decisions log. No other process friction identified this phase — the
agent-role definitions and compat-register schema were both new artifacts
authored fresh, not retrofitted onto existing structure, so there was no
handoff or boundary friction to observe yet.

## Learnings filed

- `knowledge/DECISIONS.md` — the compat-register migration-scope decision
  (2026-09-12) and the licence-migration decision (2026-09-12), both
  already recorded before this retro was written.
- `knowledge/DECISIONS.md` — the retro-process adoption itself (2026-09-12,
  filed in this same response), which this retro is the first output of.

## Where we're going

Stage B (Core model — journal/accounting model review, Editor-compatibility
confirmation) is next and unblocked; its plan lives at
`dev-docs/planning/core-redefinition/06-core-architecture.md`. Open items
carried forward, not blockers: no pinned local hledger clone/binary exists
yet (needed once `compat-differential-tester` has real work, Stage C
onward), and the remaining ~32 finer-grained compat-register rows are
still unmigrated. This phase confirmed the planned Stage A–I trajectory
unchanged — no finding here reshapes a later Stage's scope.

## Time / cost note

Single session-day (2026-09-12), five commits total including two small CI
fixes. No unusually long-running step.

<!-- dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-PLAN.md — authored by
Claude at phase end. This phase was planning-only, matching the existing
"-PLAN" retro precedent (e.g. STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md). -->

# CodeCompass upgrade + clean-room docs reconstruction — planning phase retro

- **Date:** 2026-10-02
- **Commit(s):** (this response's commit)
- **Agents used:** none dispatched this phase — direct investigation only
  (live repo inspection, local CodeCompass clone inspection, a read-only
  scratch clone of `codecompass-template`).

## Where we are

Stage C closed 2026-09-27; Stage D (Reporting) is `[PLANNED]` but not yet
scoped or started. This phase sits **before** Stage D, as a standalone
tooling/documentation initiative, not a new Stage letter (recommendation,
not yet confirmed — see the plan's §8). It directly follows the user's
request to bring Ledgerkit's CodeCompass integration current and then use
it for a clean-room documentation reconstruction. Project state after
this phase: a committed, implementation-ready six-phase plan exists
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`); nothing has been implemented; no `ledgerkit/`/`tests/`
code touched.

## Goal

Produce a concrete, implementation-ready phase plan covering: (1)
updating CodeCompass, (2) an explicit clean-room isolation mechanism, (3)
evidence-based project-understanding reconstruction, (4) replacement
documentation generation, (5) independent comparison/reconciliation
against old documentation, (6) validation — without implementing any of
it yet.

## Scope delivered vs planned

Matches what was asked exactly: inspection, then a single planning
document, committed, no implementation. One scope decision made during
planning, not dictated by the user: breaking the work into six phases
(reconciliation, isolation, evidence/reconstruction, drafting,
reconciliation, final audit) rather than leaving it as one undifferentiated
blob — needed because CLAUDE.md's per-phase retro/DoD cadence requires
phase boundaries to mean something, and because the task's own six
objectives already map almost one-to-one onto six real stages.

## What was achieved

A plan that is materially smaller and more concrete than it could have
been, because investigation (not assumption) found:
- CodeCompass's "upgrade" is mostly already done — the editable install
  already runs current code, and the installed `context-graph.db`'s
  schema already matches current source exactly (`schema_version
  '11'` == live `_SCHEMA_VERSION`). The real gap is a routine re-sync
  plus reconciling four drifted local agent-brief copies, not a
  migration.
- CodeCompass's own upstream project had, independently, already built
  almost exactly the requested clean-room methodology (Phase 79,
  `decisions/0066`) and shipped a portable, adoptable template
  (`codecompass-template`'s `optional-clean-room-workflow/`) — inspected
  directly via a read-only scratch clone, not assumed from its name.
  Objectives 2 (isolation) and 5 (reconciliation) in the user's request
  turned out to already have off-the-shelf, battle-tested answers rather
  than needing original design.
- CodeCompass's own isolation finding — strict mechanical isolation isn't
  achievable for any `Bash`-capable dispatched role, because a public
  GitHub mirror makes the network route unclosable — applies to Ledgerkit
  identically, since Ledgerkit is itself public on GitHub. The plan
  adopts this finding rather than re-discovering it the hard way during
  implementation.

## What worked

- **Verifying live state instead of trusting prior session notes paid
  off immediately.** Memory/prior context suggested a meaningful
  version-upgrade gap; direct inspection (`pipx list --json`, `git log`,
  a Python `sqlite3` read of `context-graph.db`'s own `meta` table)
  found the gap was much smaller and differently shaped than assumed.
  Writing the plan around the real gap, not the assumed one, kept Phase
  1 honestly scoped as "small."
- **Cloning `codecompass-template` read-only into a scratch directory
  before planning around it** (rather than planning from its name/
  description alone) surfaced the exact file structure and two
  judgment-call guides, which could then be cited precisely in the plan
  instead of paraphrased from a changelog summary.

## What didn't work

No real misfires this phase — it was investigation-heavy but
straightforward once the right local resources (the live CodeCompass
clone, its CHANGELOG, `decisions/0066`, the template repo) were located.
One minor inefficiency: early `sqlite3` CLI calls failed (binary not
installed) before switching to Python's `sqlite3` module — cheap, but
worth remembering for next time this comes up.

## Lessons learnt

- **A tool installed via `pipx install -e` has no separate "reinstall"
  step** — treat "is it upgraded" as "does the working tree it points at
  have the commits I need," not as a package-version question. Checking
  `pip show`/`pipx list --json`'s `package_or_url`/`pip_args` is the way
  to confirm editable-vs-published status before assuming either.
- **When a consumer project's integration with a tool is suspected
  stale, check the tool's own recent commit history against the
  consumer's own last-sync timestamp before assuming a breaking gap** —
  here, 7 runtime commits in 8 days, only one of which (Phase 77) touched
  anything the consumer's schema cares about, and the consumer had
  already synced past it.
- **Before designing a process from a task's stated objectives, check
  whether a tool already in use has independently built the same thing**
  — this task's Objectives 2 and 5 map almost verbatim onto an existing,
  already-validated upstream template; reinventing them would have cost
  real effort for a worse (unvalidated) result.

## Process-improvement feedback

None this phase — no agent dispatches occurred, so there's no handoff or
roster friction to report. Worth flagging forward (not a process problem
now, just a note for Phase 1's own retro): the two new agent roles this
plan proposes importing (`implementation-reconstructor`, `domain-skeptic`)
haven't been exercised in Ledgerkit's own workflow yet, so their first
real dispatch (Phase 3) is also their first integration test here.

## Learnings filed

None yet — this is a planning-phase retro; `roadmap-context-curator`'s
learning-triage (if anything from this phase's own working style
generalizes) would run at this initiative's eventual closeout, same as
other phases' lessons accumulate before triage rather than being filed
piecemeal.

## Where we're going

Next: human review of the plan's five open questions (§8 of
`29-codecompass-upgrade-and-clean-room-docs.md`) — most load-bearing:
where this sits in `ROADMAP.md`, and whether `knowledge/*.md` is in or out
of the clean-room evidence boundary. Once confirmed, Phase 1 (CodeCompass
reconciliation & re-sync) can start without further discovery — all its
inputs were already established this session. This phase confirmed the
trajectory the user requested; it didn't change it, beyond the sequencing
(six phases) and the two scope-narrowing findings above (small Objective
1, pre-built answer for Objectives 2/5).

## Time / cost note

One session, investigation-heavy (CodeCompass's own repo, a read-only
scratch clone of `codecompass-template`, direct `sqlite3`/`pipx`
inspection of the live integration) followed by a single planning-
document write. No code changed; no tests run beyond the implicit
expectation that none were needed since nothing executable changed.

## Addendum (2026-10-02) — review-findings amendment, all 5 open questions resolved

A direct review of the plan (same day, fresh session with no memory of
the above) found 8 concrete defects and asked for all 5 of this plan's
own open questions to be resolved in the same pass, rather than left for
Phase 1 to re-litigate. All 8 were real:

1. **Clean-room leakage** — Phase 3's own acceptance criteria compared
   reconstructed coverage against `dev-docs/api-spec.md`, i.e. consulted
   excluded legacy narrative before any clean-room draft existed. This
   is the one finding from this addendum that most directly contradicts
   something the plan *itself* claimed to guarantee — worth flagging as
   the sharpest lesson here (see below), not just one item among eight.
2. The plan's Phase 4 drafted 4 documents while Phase 5 proposed
   replacing 5 (and, once named concretely, really 9) — no inventory
   tied the two together.
3. Nothing stopped the reconstruction from quietly inferring future
   roadmap intent from present-tense source/test evidence.
4. The "don't import CodeCompass's validator" decision had no
   Ledgerkit-sized replacement, so nothing actually gated a malformed
   snapshot.
5. "Clean-room isolation enforced" rounded a disclosed `best-effort`
   limitation up into language implying success.
6. "Current CodeCompass" was never pinned to a SHA, so it could have
   silently moved across a multi-phase exercise.
7. `dev-docs/compat-register/*.yaml` was listed flatly as "Evidence",
   on par with source/tests, when it's actually a derived index pointing
   at real evidence elsewhere.
8. Two genuine "before Phase 6" phase-reference errors (should have said
   Phase 5), plus a "nine... format skeletons" miscount of the adopted
   template (it's seven skeletons, two guides, a worked example).

All 8 are fixed in place in `29-codecompass-upgrade-and-clean-room-docs.md`
(same file, same six-phase structure — amended, not replaced), and all 5
of the plan's own open questions are resolved in the same pass (§8, now
split into Part A — the 5 original questions — and Part B — the 8 review
findings, F1–F8, to avoid a numbering collision between two lists that
both happen to run 1–8).

**What didn't work, corrected:** while fixing the review's findings, a
second-order defect was introduced and then caught: §8's own new Part
B/Part A split still left several of the ~18 cross-references into §8
pointing at the wrong item (a numbering collision this session created
itself, not one the review flagged). An explicit internal-consistency
pass (new §12 in the plan) caught and fixed all of them, plus one
genuine gap in acceptance-criteria demonstrability (Phase 3's
"independence is structural" claim had no actual mechanism to check it
by — fixed by requiring a producer header on every Phase 3 output file).

**Lesson, stated plainly:** a plan that itself specifies a strict
evidence-isolation discipline is not exempt from violating that
discipline internally — finding #1 (comparing against `api-spec.md`
inside the supposedly isolated Phase 3) is exactly the kind of leakage
the plan's own hard invariant exists to prevent, and it happened anyway,
in the plan's *first* draft, written by the same session that designed
the invariant. Treat a clean-room plan's own drafting process as subject
to the same scrutiny the plan applies to its subject — a self-review
pass (§12 here) is now a standing expectation for any future amendment
to this document, not a one-off.

No code touched; no tests run beyond the implicit expectation that none
were needed, since nothing executable changed this phase either.

## Addendum 2 (2026-10-02) — second review, 8 further corrections, approved to implement

A second review (same day, fresh session) found the first amendment
still implementation-unready: assertion authorship wasn't structurally
separated from the orchestrator (the orchestrator, having read the whole
plan, could have written "clean-room" assertions itself); the
CodeCompass/template pin was recorded but never checked against; the
snapshot checker validated against today's filesystem rather than the
frozen revision's own git tree; contamination discovery was deferred to
Phase 6 instead of happening per-dispatch; the inventory and Phase 5/6
acceptance criteria contradicted each other over intentionally-retained
process files; commit-message prose had no exclusion rule distinct from
other narrative; the template's file-count arithmetic was still wrong
(seven skeletons + two guides + one worked example is ten, not nine, and
the directory's own README.md makes eleven); and the plan was directed
to re-run its own consistency checks. All 8 were real and are fixed in
place (§8 Part C, `29-codecompass-upgrade-and-clean-room-docs.md`),
alongside a second dated `§12` consistency-review addendum.

**This time the review came with explicit authorization to proceed
straight to implementation once fixed** — no further planning
round-trip. That work begins immediately following this commit; its own
progress is tracked in the plan's new §13 implementation log and in each
phase's own retro, not here (this retro's own scope stays "the planning
phase," per the established `-PLAN`/`-IMPLEMENTATION` split used
throughout Stage C).

**Lesson, stated plainly, building on Addendum 1's own lesson:** the
first amendment's self-review (§12) caught a numbering collision it
introduced while fixing the review's findings — a real catch, but it
didn't catch everything; a genuinely separate second pass, from a fresh
session with no attachment to the first amendment's own reasoning, found
8 more real defects, several structural (not cosmetic) and squarely in
the areas the first amendment's own self-review had just finished
checking. The pattern worth keeping: a self-review is valuable and
should keep happening (§12 is now two addenda deep and will likely
gain more), but it is not a substitute for an independent review when
the stakes of getting a clean-room methodology's own isolation rules
wrong are this high — exactly the same principle this whole initiative
applies to Ledgerkit's documentation (an aligned self-check is not
verification), now observed about the planning process that produced it.

No code touched this addendum either; 935 tests still pass (regression
guard only).

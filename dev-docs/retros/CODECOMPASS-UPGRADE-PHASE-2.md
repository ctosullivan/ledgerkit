<!-- dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md -->

# CodeCompass upgrade + clean-room docs — Phase 2 retro

- **Date:** 2026-10-02
- **Commit(s):** (this response's commit)
- **Agents used:** one `general-purpose` dispatch (isolation preflight
  probe) — see `dev-docs/clean-room/isolation-preflight.md` for its full
  raw transcript.

## Where we are

Phase 2 of 6. Phase 1 pinned and reconciled the CodeCompass integration;
this phase adopts the actual clean-room workflow and builds the one new
tool this initiative needs (`check_snapshot.py`), plus establishes the
honest isolation baseline every later phase's own reporting depends on.
Project state after this phase: `dev-docs/clean-room/` carries the full
adopted template (seven `TEMPLATE.md` skeletons, two guides, a worked
example, the workflow's own README), a working, self-tested snapshot
checker, and a recorded, honestly-labelled isolation preflight. No real
topic work has started yet — that's Phase 3.

## Goal

Per plan §3: adopt the pinned `codecompass-template`'s
`optional-clean-room-workflow/` directly; build and test
`check_snapshot.py` with historical-integrity semantics; run the
isolation preflight against the dispatch configuration Phase 3 will use;
record the honest tier before any real reconstruction dispatch runs.

## Scope delivered vs planned

Matches the plan, with one disclosed discrepancy in the preflight's own
dispatch configuration (see "What didn't work," below) — the plan asked
for the probe to run "against the exact dispatch configuration Phase 3
will use," and at the moment the probe actually ran, the two new
subagent types it should have used weren't yet available, so it ran as
`general-purpose` instead. Recorded honestly in the preflight report
rather than silently treated as equivalent.

## What was achieved

- `dev-docs/clean-room/` now holds the full adopted template: seven
  `TEMPLATE.md` skeletons (`assertions/`, `snapshots/`,
  `coding-context-selection/`, `implementation-comparison/`,
  `propagation/`, `legacy-reconciliation/`, `documentation-verification/`),
  two guides (`mechanical-isolation.md`, `conceptual-documentation-
  guide.md`), the worked example, and the workflow's own README
  (renamed `WORKFLOW-README.md` to avoid colliding with a future
  Ledgerkit-authored index) — kept verbatim except one stale
  cross-reference to the template repo's *other*, non-adopted
  everyday-adoption files, corrected to point at Ledgerkit's own
  long-existing equivalents instead.
- `dev-docs/clean-room/check_snapshot.py`: a small, stdlib-only,
  deterministic checker implementing all six fail-closed conditions from
  plan §3.7, including the two historical-integrity checks this
  initiative's second amendment added (resolving cited evidence against
  the frozen git revision's own tree via `git cat-file`/`git show`,
  never today's working tree). **Proven, not just asserted, to fail
  closed**: a built-in `--self-test` runs a disposable git fixture
  through one passing case and six distinct failure-mode cases
  (including the two sharpest ones — a cited file added only in a
  *later* commit than the frozen revision, and a cited line range that
  only resolves against *today's* longer version of a file, not the
  version that existed when the snapshot was frozen) and confirms each
  behaves exactly as expected. All seven cases passed.
- `dev-docs/clean-room/assertions/TEMPLATE.md` gained one addition: a
  machine-checkable `Evidence-paths: [...]` line convention (inline-list
  form, this project's existing convention for exactly this reason — a
  hand-rolled parser can silently miss a block-list form), since the
  imported template's own `## Evidence` field is deliberately free-form
  prose and `check_snapshot.py` needs something deterministic to
  resolve against real git history.
- `dev-docs/clean-room/isolation-preflight.md`: the real preflight
  transcript and honest tier. **Tier: `best-effort`** — filesystem,
  command execution, and network were all directly demonstrated open
  (not just assumed); same host, same working directory as the main
  session, confirmed by direct comparison, not inferred. Matches plan
  §1.1's/§3.4's own predicted outcome exactly.

## What worked

- **Testing the checker's own failure modes with a real disposable git
  fixture, not just describing them in prose** — the same discipline
  applied to the Phase 1 pin guard, now applied to a more complex tool.
  Building the self-test *as part of* `check_snapshot.py` itself (not a
  separate throwaway script) means this proof travels with the tool
  permanently, not just for this one phase.
- **Comparing the probe's own `pwd`/`hostname` output against the main
  session's own, run directly, right after the probe returned** — turned
  "probably the same host" into a directly confirmed fact with two
  concrete values on each side.

## What didn't work

- The preflight probe's own dispatch configuration diverged from the
  plan's instruction to match Phase 3's real dispatch configuration
  exactly: `implementation-reconstructor`/`domain-skeptic` were not yet
  real `subagent_type` values when the probe was dispatched (as
  `general-purpose` instead), and became available moments after the
  probe completed. Consequence: the probe's `general-purpose` dispatch
  turned out to have a *narrower* live tool set than expected — no
  `Grep`/`Glob` tool was reachable at all, so the "search" route wasn't
  actually tested. Not treated as a clean pass on that route by default
  — recorded explicitly as untested, with the reasoning for why this
  doesn't weaken the overall `best-effort` conclusion (`Bash`, already
  proven open, trivially substitutes for dedicated search).
- Minor: this means a strictly literal re-read of plan §3.3 ("the exact
  dispatch configuration") would ask for a second probe run now that the
  two named types exist. Judgment call made here: not worth re-running —
  the three routes that matter most (filesystem, command, network) are
  already conclusively open via tools (`Read`, `Bash`) every real Phase
  3/4 dispatch also has regardless of which named type it runs under,
  so a second probe would confirm the same `best-effort` tier at real
  cost (another dispatch, another transcript review) for no new
  information. Named here so a future session doesn't assume this
  judgment call was an oversight.

## Lessons learnt

- **A "same kind of dispatch" isn't guaranteed to have the same live
  tool set as its own catalog description claims** — `general-purpose`'s
  "Tools: *" didn't include a reachable `Grep` in this actual run, even
  via `ToolSearch`. When a probe's own result depends on exactly which
  tools a dispatch has, don't assume the catalog description is the
  ground truth; let the dispatch's own transcript show what it actually
  had.
- **Run the preflight close to when the real dispatches will run, not
  far ahead of it** — the window between "a new role doesn't exist yet"
  and "a new role exists" can be shorter than one tool-call round in
  this environment (confirmed here: the gap was effectively zero,
  discovered only because the system notified mid-task). A plan step
  that says "exact configuration" is worth re-checking immediately
  before the step that depends on it, not assumed stable from an earlier
  planning session.

## Process-improvement feedback

The two new agent roles (`implementation-reconstructor`, `domain-
skeptic`) created in Phase 1 were not dispatchable by name at Phase 1's
own end, then became dispatchable sometime during Phase 2 — apparently
sooner than the originally-imported upstream brief's own disclosed
limitation (`L-023`, "a newly-created `.claude/agents/*.md` file is not
immediately dispatchable by its own type name within the same session
that creates it") predicted. Worth a note for whoever next adapts an
upstream CodeCompass agent brief into this project: that specific
disclosed limitation may be environment-specific, not universal — check
directly (attempt a dispatch, don't assume) rather than carrying the
caveat forward by default.

## Learnings filed

None yet — held for this initiative's own closeout triage, per the
established pattern.

## Where we're going

Next: Phase 3 (evidence-backed clean-room reconstruction, plan §4) — the
real per-topic pipeline starts here, now with both new agent types
confirmed dispatchable by name. This phase's own `best-effort` tier
finding is the honest baseline every later phase's isolation reporting
(Phase 6 especially) builds on; nothing here changed the plan's own
trajectory, only confirmed its predicted outcome with real evidence
instead of a stated expectation.

## Time / cost note

One session, one subagent dispatch (the preflight probe, ~59s, 9 tool
uses, ~56k subagent tokens). The rest of this phase was direct tooling
work (copying the template, writing and self-testing the checker).

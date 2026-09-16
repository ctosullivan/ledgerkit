# Stage C Phase 2 retro — Planning (CodeCompass adoption + query integration)

- **Date:** 2026-09-16
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — direct inspection and planning by the lead
  session; no agent dispatch warranted for a read-only planning pass

## Where we are

Stage C Phase 1 delivered a standalone, tested `ledgerkit/query/`
subpackage, deliberately not wired into anything. This phase is planning-
only, producing `18-stage-c-phase-2-codecompass-adoption-plan.md`: how to
(a) wire that query engine into `reports.py`/`cli.py` and (b) adopt
CodeCompass into Ledgerkit's own agent-development workflow for the first
time, using one real task as the vehicle for both. No implementation
happened in this phase — that's explicitly out of scope per the user's
own instruction, and the plan itself is the deliverable. After this
phase: a concrete, revision-pinned plan exists; Stage C's `ROADMAP.md` row
points to it; nothing has started.

## Goal

Plan (not implement) the next Ledgerkit phase: adopt current CodeCompass,
as it exists today, into a real development task — integrating the
existing query engine into report/CLI surfaces — so CodeCompass's
usefulness is evaluated as a byproduct of genuine work, not a synthetic
benchmark.

## Scope delivered vs planned

Delivered exactly the 13 requested planning outputs, informed by a full,
literal inspection of all 11 numbered areas the request specified
(current Ledgerkit main, `CLAUDE.md`, roadmap/context, the most recent
phase, the query engine, report/CLI architecture, compat/evidence infra,
the pinned hledger binary, `validation/codecompass/`, test state, and —
the largest single piece of new ground — the actual current CodeCompass
repository).

The one significant deviation from a literal reading of the request,
made deliberately and disclosed rather than silently absorbed: the
request's own "Important expected test" section assumed CodeCompass's
current capability was largely unknown territory ("the first evaluation
may show..."). Direct inspection found that assumption was **not
current** — CodeCompass has already run six of its own phases (45, 46,
47, 49, 51, 54) evaluating itself against Ledgerkit, including a FAIL→
fix→PASS-WITH-GAPS cycle and, as of *today's* CodeCompass commit, a
same-day heterogeneous-reference-material experiment touching the exact
`tag:`-query-semantics territory this project's own roadmap lists as
deferred. The plan does not pretend this evidence doesn't exist —
§1.9 states it in full and uses it to calibrate expectations and to
explicitly rule out re-running the same task type CodeCompass already
tested from its own side.

## What was achieved

A single, concrete plan document with pinned revisions
(Ledgerkit `05218e3`, CodeCompass `e40d8d1`, hledger `1.52.4`/
`33fa849e7`), a corrected understanding of the actual integration gap
(reports.py already shares one filter helper across all four report
functions — the real gap is narrower: no `query_ast` path, and `cli.py`
has zero query flags at all today, not "three different filtering
implementations" as a surface reading of the request might have
assumed), a design that explicitly reuses existing infrastructure
(`05-context-curator.md`'s evaluation schema, `validation/codecompass/`'s
existing templates, the existing `compat-differential-tester`/
`context-curator` agent roles) rather than inventing parallel structures,
and an explicit list of what this phase and its follow-on must not
absorb (`tag:`/`cur:`/`PythonRegex`/`Query`-as-shim/`print`+`check`
wiring).

## What worked

- **Inspecting CodeCompass's actual repository state before writing
  anything**, rather than planning against the request's own illustrative
  hypothetical. The six-phase history found there is directly load-
  bearing evidence this plan would have been materially weaker without —
  in particular, knowing `query relations`' FAIL was already found and
  fixed (Phase 45→49→51) prevented this plan from proposing to
  "discover" something already discovered, and knowing Phase 54 already
  probed `tag:`-adjacent reference material sharpened *why* this phase's
  own task choice (integration, not semantics research) is genuinely
  differentiated rather than redundant.
- **Re-reading `reports.py`/`cli.py` directly instead of trusting the
  request's own framing of the problem.** The request's illustrative
  "balance implements filtering one way, register another" concern turned
  out not to describe current reality — both already share
  `_posting_matches`. Planning against the request's framing rather than
  the actual code would have produced a plan solving a problem that
  doesn't exist, alongside the real, narrower one that does.
- **Reusing `05-context-curator.md`'s existing evaluation schema
  verbatim** rather than designing a new one — it already matches almost
  every field the request's own "Suggested evaluation record" asks for,
  confirming the project's own prior planning anticipated this need
  correctly well before this phase existed.

## What didn't work

Nothing failed in this planning pass. One thing worth naming as a near-
miss: the scale of the request (11 inspection points, 13 planning
outputs, a 20-item DoD) created real pressure to start summarizing from
partial reads to move faster — resisted by reading `reports.py`'s actual
function bodies and CodeCompass's actual `findings.md`/`decisions/0052`
in full rather than skimming headers, which is exactly what surfaced both
corrections above.

## Lessons learnt

When a planning request includes its own illustrative hypothesis about
what inspection will find (the "first evaluation may show..." table,
here), that hypothesis is a **starting expectation to check, not a
description to plan against** — treating it as settled would have missed
that CodeCompass's actual current state has already moved past several
of those hypothetical findings. More generally: a cross-project planning
task where one side (CodeCompass) has an active, fast-moving development
history of its own needs that history inspected at *current* HEAD, not
assumed static from whatever the requester last knew about it.

## Process-improvement feedback

No friction with Ledgerkit's own process this phase — the existing
`dev-docs/planning/core-redefinition/` numbering, the existing
`validation/codecompass/` scaffold, and the existing agent-role files all
slotted in without needing new scaffolding invented. One open process
question, not a defect: this is the first *planning-only* phase since the
per-phase retro/commit-cadence rules were adopted — this retro and the
commit that follows it are the precedent for how a planning-only phase
(no `ledgerkit/`/`tests/` change, one new doc) is handled under those
rules. Recorded here so a future planning-only phase has this one to
follow rather than re-deriving the pattern.

## Learnings filed

None to `knowledge/*.md` this phase — no judgment call was made that
generalises beyond this specific plan; the corrections above (report-
filtering reality, CodeCompass's actual current state) live in the plan
document itself (§1), where anyone acting on it will read them first.

## Where we're going

Stage C Phase 2 itself (the actual CodeCompass-assisted query/report/CLI
integration) is planned but **not started** — it awaits explicit approval
per `ROADMAP.md`'s own standing process, same as every prior Stage/phase
here. The plan's own §13 names likely follow-on options after Phase 2's
evidence lands (extending CLI query coverage to `print`, `tag:`/`cur:`,
`Query`-as-compatibility-shim, a second differently-shaped CodeCompass
trial) without pre-selecting any of them.

## Time / cost note

Single response: ~20 tool calls across both repositories (git/file reads,
one full test-suite run, no code written), then the plan document itself.
No unusually long step; the CodeCompass-repository inspection was the
largest share of the work, appropriately, since it was the least-known
territory going in.

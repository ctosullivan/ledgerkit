# CodeCompass upgrade + clean-room docs — Phase 3 retro — evidence-backed clean-room reconstruction

- **Date:** 2026-11-14
- **Commit(s):** `7224bb5` (assertion research/review/freeze), `f55294f` (implementation reconstruction), plus this response's comparison-mode commit
- **Agents used:** fresh `general-purpose`/`implementation-reconstructor` dispatches (assertion research + model-blind reconstruction, ×10 each), `domain-skeptic` (REVIEW mode ×10, COMPARISON mode ×10)

## Where we are

This is Phase 3 of Plan 29's twice-amended six-phase initiative
(`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`). Phase 1 (CodeCompass reconciliation + enforced pin) and
Phase 2 (isolation workflow adoption + `check_snapshot.py`) established
the mechanism; this phase is the first one to actually *run* it at full
scale — the entire evidence-backed reconstruction pipeline (plan §4.2's
9 steps), executed for all 10 bounded topics, producing 102 assertions,
10 snapshots, 10 implementation-reconstruction reports, and 10
comparison reports, with zero legacy documentation consulted anywhere
in the process. The project now has a from-scratch, independently
cross-validated record of what Ledgerkit's code actually does, entirely
decoupled from what any existing prose claims it does — Phase 5 is
where that record gets reconciled against the legacy docs it will
eventually replace or correct.

## Goal

Execute Plan 29 §4.2's full per-topic pipeline — isolated assertion
research, adversarial review, mechanical freezing, a hard checker gate,
model-blind implementation reconstruction, and independent alignment
comparison — for all 10 bounded topics, with per-dispatch boundary
compliance enforced throughout, never comparing against any legacy
documentation at any step.

## Scope delivered vs planned

Delivered exactly the 9-step pipeline for all 10 topics (journal-
parsing, commodity-styling, query-engine, tags, reports-cli, checks,
loader, editor-surface, compat-system, current-state) — nothing
dropped, nothing deferred. One addition beyond the plan's original
text: `check_snapshot.py` itself needed a new capability (resolving an
absolute-path citation against a registered *external* repository's
own pinned revision) that the plan hadn't anticipated, since editor-
surface's evidence lives in a different git repository entirely. This
was built, self-tested (2 new fixture cases), and used — a mechanical
tooling extension squarely in the checker's own spirit, not a scope
change requiring a plan amendment.

## What was achieved

- 102 assertions across 10 topics, each independently reviewed,
  mechanically frozen, and passing `check_snapshot.py`'s hard gate.
- 10 independent, model-blind implementation-reconstruction reports.
- 10 independent alignment comparisons: **97 aligned, 9 partial, 5
  insufficiently_verified, 0 conflicting, 0 not_implemented** across
  all topics combined. Zero contradictions between two independently-
  produced artefacts is itself a meaningful result — it means neither
  the assertion-research step nor the reconstruction step was
  fabricating or guessing at scale.
- **8 real production bugs/defects found as a byproduct**, none fixed
  (correctly out of scope for a documentation phase), all recorded in
  `dev-docs/clean-room/compliance-log.md`'s own tally section for a
  future tracked-fix task: `parse_string_lenient`'s broken never-raise
  guarantee for malformed `commodity` directives; a loader `IndexError`
  from glob-metacharacter-named directories; an `alias`-directive
  backreference crash; silent posting-line data loss when a directive
  interrupts an open transaction block; silent data corruption from
  hledger's balance-assignment elision syntax; a rounds-vs-truncates
  inconsistency in `CommodityStyle.format()`; dead/confused code in
  `ReportSectionResult.to_dataframe()`; and two compat-register entries
  citing a nonexistent test.
- One major scoping finding: `EditorDocument` (the entire subject of
  the editor-surface topic) has **zero real usage** by the external
  `ledgerkit-editor` project it was built for — confirmed independently
  by both the assertion-research and reconstruction dispatches.
- `check_snapshot.py` extended with an `external_repositories` resolver
  and 2 new self-test cases (now 9/9 passing).

## What worked

- **The checker caught real defects before anything was accepted as
  frozen** — exactly its job. Three citation defects (two off-by-one
  line counts, one unresolvable glob-as-path) were caught and fixed
  before any snapshot passed. This is the single clearest proof the
  mechanical gate is doing real work, not theater.
- **Independent cross-validation surfaced genuine findings, repeatedly**
  — not just once. REVIEW mode caught a backwards specificity rule that
  self-contradicted its own next clause (query-engine-014), a false
  "necessarily zero" claim (reports-cli-005), and an anchored-grep false
  negative that missed 8 of 9 real import sites (editor-surface-008).
  The later, fully-independent reconstruction then *re-derived* several
  of these same corrected facts from scratch with zero access to the
  correction — strong evidence the corrections were right, not lucky.
- **The mechanical discard-and-rerun rule for assertion-research/
  reconstructor contamination, applied without exception**, including
  once (compat-system attempt 2) where the dispatch's own output looked
  completely clean and the "mistake" (reading two source files outside
  its permitted list) demonstrably wasn't used in any assertion. Discard
  anyway, per the rule's own letter — this phase proved the rule is
  genuinely mechanical, not a judgment call that gets waived when
  inconvenient.
- **Recovering a report from disk instead of blindly redispatching**
  after a rate-limit interruption (journal-parsing, commodity-styling)
  saved two full dispatches' worth of work and tokens, by checking
  whether the file the agent was writing already existed and looked
  complete before assuming the work was lost.
- **Treating REVIEW/COMPARISON-mode scope slips differently from
  assertion-research/reconstructor slips** — logging a disclosed,
  unused, out-of-scope peek as a compliance *note* rather than
  mandatory contamination, since the plan's own §4.2a text names only
  the two primary evidence-gathering roles for the discard rule, and
  REVIEW/COMPARISON output is independently per-field traceable so an
  unused aside doesn't propagate the way it would in a primary
  evidentiary record.

## What didn't work

- **A domain-skeptic COMPARISON dispatch (reports-cli) had its own
  `Write` tool call hard-blocked by the harness** ("Subagents should
  return findings as text, not write report files") — an environment-
  level restriction that none of the other 9 identical dispatches hit.
  Cost one extra `SendMessage` round-trip to recover the full verbatim
  text before the lead could persist it directly. Not a process
  failure exactly — the agent handled it correctly (returned full text,
  asked the lead to persist, didn't try to route around the block) —
  but it's unexplained why only this one dispatch was affected, and
  worth flagging in case it recurs.
- **Three contamination/loss events during assertion-research** (two
  genuine contaminations in compat-system, one lost-content case in
  editor-surface) meant 3 extra dispatch rounds beyond the planned 10.
  Correctly handled per the plan's own rule, but a real cost, not a
  free safety margin.
- **The account's weekly rate limit interrupted two reconstructor
  dispatches mid-task**, both on a trailing, inessential "let me also
  check one more edge case" step rather than the core report-writing —
  lucky in where it landed, but a reminder that a long-running batch of
  parallel dispatches is exposed to account-level limits that have
  nothing to do with the work itself.

## Lessons learnt

- A mechanical gate (the checker, the discard rule) only proves its
  worth when it actually blocks something real. This phase validated
  both: the checker blocked 3 real citation defects, and the discard
  rule was honored even in the one case where honoring it felt
  unnecessary (compat-system attempt 2). Keep applying rules
  mechanically rather than "when it matters" — the rule is what
  decides that, not a judgment call made in the moment.
- When a subagent's final write is blocked by something outside its
  control, the right move is to get the content back (resume, don't
  redispatch) and have the orchestrator — who already holds the
  relevant write permission for that exact artifact path — persist it.
  This is distinct from permission laundering: the test is whether the
  orchestrator's *own* standing authority already covers the action,
  not whether the subagent asks nicely.
- Two independently-dispatched, model-blind processes (REVIEW's
  correction and reconstruction's from-scratch re-derivation)
  converging on the same non-obvious fact is a stronger validation
  signal than either one alone. Worth designing future verification
  work to create this kind of convergence deliberately, not just as a
  side effect of this phase's particular structure.

## Process-improvement feedback

- The plan's §4.2a boundary-compliance rule only names assertion-
  research and implementation-reconstructor in its mandatory-discard
  list. This phase needed to extend that reasoning (by the lead, not
  unilaterally invented) to REVIEW/COMPARISON-mode scope slips. Worth
  folding this distinction into the plan's own text explicitly at the
  next amendment opportunity, rather than leaving it as an
  implicit precedent recorded only in the compliance log.
- `check_snapshot.py`'s external-repository gap (discovered only when
  editor-surface's snapshot actually failed the checker) suggests any
  future topic whose evidence spans more than one git repository should
  be flagged *before* freezing, not discovered at freeze time. Minor
  — cost one extra round of editing, not a blocker.

## Learnings filed

None yet — the 8 production-bug findings and the EditorDocument-unused
finding are operational discoveries for a future tracked-fix task, not
yet triaged into `knowledge/*.md`. Recommend a `roadmap-context-curator`
learning-triage pass over this phase's compliance log once Phase 6's
audit closes the whole initiative out, rather than triaging piecemeal
mid-initiative.

## Where we're going

Phase 4 (clean-room documentation drafting) is next: draft the clean-
room documentation set from these 10 checker-valid snapshots only, via
fresh isolated dispatches with the same immediate-compliance-check
discipline, committing before any existing documentation is opened —
that commit is Plan 29's hard boundary, the last point before Phase 5
reintroduces legacy prose at all. This phase's findings (particularly
the 8 production bugs and the EditorDocument-unused discovery) do not
block Phase 4 — they are recorded for Phase 5's reconciliation step and
beyond, not blockers to drafting what the code currently, actually
does. This phase confirmed the planned trajectory; it did not change it.

## Time / cost note

Significantly longer than a typical phase — spanned multiple real-world
sessions across roughly six weeks (2026-10-02 through 2026-11-14),
interrupted twice by account-level usage limits (once mid-Phase-3, once
again near the end of the reconstruction step), each time resumed
correctly rather than restarted. The bulk of the cost was the sheer
dispatch count: 10 assertion-research attempts (+3 reruns) + 10 REVIEW
+ 10 implementation-reconstruction + 10 COMPARISON = 43 total dispatches
for this phase alone, each with its own immediate compliance check.

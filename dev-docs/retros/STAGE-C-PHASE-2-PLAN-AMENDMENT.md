# Stage C Phase 2 retro — Plan amendment (review findings)

- **Date:** 2026-09-16
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — direct amendment by the lead session

## Where we are

The original Stage C Phase 2 plan (`18-stage-c-phase-2-codecompass-
adoption-plan.md`) was written, retro'd, committed, and pushed
(`4586428`) earlier the same day. This is a follow-up planning-only pass,
amending that same document in place per four external review findings,
before any implementation starts. After this phase: the plan carries an
explicit API-boundary decision gate, a corrected filtering-delegation
design, an acknowledged module-size flag, and a specified three-commit
structure — still planning only, still nothing implemented.

## Goal

Amend the existing plan per four specific review findings, without
otherwise redesigning the phase, preserving its stated objective
unchanged.

## Scope delivered vs planned

All four requested changes applied, each traced through every section
the reviewer named (phase plan, task ordering, Definition of Done, risks)
plus the design section itself (§6), which needed the most substantive
rewrite of the four. No fifth change was introduced — the temptation to
also "clean up" adjacent prose while editing was resisted; only what the
four findings actually named was touched.

## What was achieved

- **Finding 1** (API-boundary gate): §6.1 rewritten from a presumed
  `query_ast=` parameter into an explicit three-option decision gate
  (new param / overload existing param / internal-only, no API change),
  with a stated default lean (Option C, since no known caller besides the
  CLI itself needs `QueryNode` at the public `reports.py` level today)
  and a new standalone phase step (step 3) so the gate can't be silently
  bypassed inside the implementation step.
- **Finding 2** (canonical evaluator delegation): §6.3 rewritten to
  explicitly name `matches_posting`/`matches_transaction` as the only
  delegation targets, by report orientation, and to name the failure mode
  being avoided (a new `reports.py`-local wrapper re-deriving AST
  semantics a second time) rather than just asserting "shared."
- **Finding 3** (module-size acknowledgement): confirmed `reports.py` is
  573 lines (live `wc -l`, not asserted from memory) against `CLAUDE.md`'s
  300–500-line signal, recorded in a new §1.4a, referenced from risks,
  DoD, and follow-on options — with the explicit rule (flag, don't act
  unilaterally) restated rather than paraphrased loosely.
- **Finding 4** (commit separation): three commit boundaries specified
  and threaded through the phase steps (§2), task breakdown (§3), and the
  doc-update table (§10), with an explicit note on which boundary
  feature-docs belong to (2, not 3 — they describe the shipped feature,
  so `CLAUDE.md`'s same-response doc-sync rule puts them with the code).

## What worked

- **Verifying the module-size claim live** (`wc -l ledgerkit/reports.py`
  → 573) rather than accepting the reviewer's framing on trust — it
  happened to be correct, but confirming it directly is what makes the
  new §1.4a citable rather than assumed.
- **Renumbering §6 carefully and then grepping for stale cross-references**
  (`§6.4`, `one shared internal check`, the now-removed `query_ast=
  query_ast` snippet) — caught two cross-reference breaks a section
  rewrite of this size would otherwise have left behind (a duplicate
  heading number, and a risk-section pointer to the wrong subsection).
- **Adding new DoD items (21-24) rather than renumbering the original
  20** — keeps the original list's 1:1 mirror to the task's own DoD
  checklist intact and traceable, while still making the four amendment
  requirements checkable at completion.

## What didn't work

Nothing failed this pass. The duplicate-heading-number slip (two
consecutive `### 6.4` headings mid-edit, before the grep pass caught it)
is worth naming as a near-miss, not a failure — it was caught before
being committed.

## Lessons learnt

When amending a large planning document's design section in place, a
targeted grep for the old section's own distinctive phrases (not just its
heading numbers) after editing is what catches cross-references the edit
itself didn't touch — heading renumbering alone doesn't surface prose
elsewhere that still names the old structure.

## Process-improvement feedback

No friction. This is the second planning-only phase since the retro/
commit-cadence rules were adopted (the first being this same plan's
original authoring) — confirms a planning-only *amendment* pass fits the
same pattern (its own short retro, its own commit) without needing a new
carve-out.

## Learnings filed

None to `knowledge/*.md` — the four corrections are specific to this one
plan document and already live there; nothing here generalises beyond it.

## Where we're going

Unchanged from the original plan's own §13 — Stage C Phase 2's actual
implementation still awaits explicit approval. This amendment changes
*how* that implementation should proceed (the gate, the delegation
design, the size flag, the commit structure) without changing *whether*
or *when* it starts.

## Time / cost note

Single response: one `wc -l` check, then a sequence of targeted edits
across roughly a third of the plan document's sections, verified by grep
for stale references at the end. No unusually long step.

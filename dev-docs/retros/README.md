# Phase retros

One retro per **phase**, authored by Claude at phase end — the same
granularity `release-phase-auditor`, `docs-reconstructor`, and
`context-curator` already operate at (`dev-docs/planning/core-redefinition/
03-agent-led-development.md` §3.4's fresh-session workflow), not only at
whole-Milestone/Stage completion. A phase is one discrete unit of
implementation work with its own `ROADMAP.md`-relevant scope and its own
`release-phase-auditor` Definition-of-Done check — sometimes an entire
small Milestone/Stage, sometimes one of several phases within a larger one
(the existing precedent: `dev-docs/changelog/MILESTONE-4.md`'s "Milestone 4
Phase 1" … "Phase 5").

**Naming:** `dev-docs/retros/<STAGE-LETTER-OR-MILESTONE-N>.md` when the
whole Milestone/Stage was delivered as a single phase; `dev-docs/retros/
<STAGE-LETTER-OR-MILESTONE-N>-PHASE-<K>.md` when it was broken into
multiple phases (matching the changelog's own `Phase 1`/`Phase 2a` naming).
Producing the retro is part of the Definition-of-Done process in
`CLAUDE.md`. Format: [`TEMPLATE.md`](TEMPLATE.md).

Adapted from the equivalent convention in the sibling `codecompass` project
(`decisions/0050-phase-retros-and-per-phase-docs-drift-audit.md`), at the
same per-phase cadence CodeCompass uses — not scaled down to Stage/
Milestone-only, which was this doc's first draft and undershot how often
the rest of ledgerkit's own agent roster already checks in.

## Why

- **Process feedback has somewhere to go.** Friction in the agent-led
  workflow itself (an unclear agent boundary, a step that added nothing, a
  handoff that dropped context) is captured while it's fresh, not lost.
- **Lessons surface into the knowledge base.** `roadmap-context-curator`
  reads each retro during its learning-triage job and files anything
  generalizable into the artifact that actually owns it — `knowledge/
  DECISIONS.md`, `knowledge/ANTIPATTERNS.md`, `knowledge/EDGE_CASES.md`, a
  `ROADMAP.md` row, or a `CLAUDE.md` proposal. There is no separate
  permanent "learnings" document.
- **Later consolidation points have real material.** When a Milestone/Stage
  completes, or at Core 1.0, deciding whether the agent roster or process
  is still earning its keep draws on the accumulated per-phase retros as
  evidence, not memory.

## What a retro is / isn't

- **Is:** a short, honest record that also *orients* a future session in
  the arc — where this phase sits relative to the ones before and after,
  the goal, what actually shipped vs. what was scoped, what worked, what
  didn't, the generalizable lessons, concrete process-improvement
  suggestions, and where things go next.
- **Isn't:** a status report (that's `CONTEXT.md`, which is overwritten
  each session — retros accumulate as a running narrative instead), a
  changelog entry (that's `CHANGELOG.md`), or a place for canonical
  decisions (those go to `knowledge/DECISIONS.md` directly).

Full section list: [`TEMPLATE.md`](TEMPLATE.md).

A **trivial phase** gets a few lines — one sentence for "where we are",
the goal, "shipped as planned", "what worked / didn't: nothing notable",
"no process notes", "next: phase/Stage X". Don't pad it.

## Lifecycle

```
phase ends (its release-phase-auditor DoD check is due)
   ↓
Claude writes dev-docs/retros/<name>.md   (same response, per CLAUDE.md)
   ↓
roadmap-context-curator reads it during learning-triage → files anything
promotable into knowledge/*.md, ROADMAP.md, or a CLAUDE.md proposal
   ↓
release-phase-auditor confirms it exists and is substantive, as part of
its Definition-of-Done audit for that same phase
   ↓
Reviewed in bulk when the enclosing Milestone/Stage completes, and at
Core 1.0, for actual process changes (roster pruning, workflow edits,
CLAUDE.md proposals)
```

Retros are **not** rewritten after the fact — they're dated records, like
`knowledge/*.md` entries and the `dev-docs/changelog/` archives.

## Scope note

This convention starts with the phase(s) that made up Stage A (adopted
2026-09-12, after Stage A had already completed — so its retro was written
retroactively as a single file covering the whole stage rather than split
per sub-phase after the fact). Milestones 0–4 predate it and are not
retroactively required to have one, though a retro may be added for any of
them if it would be useful context — the loss is small since their full
detail, including their own internal phase breakdown, already lives in
`dev-docs/changelog/MILESTONE-{0,1,2,3,4}.md`.

# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:` query-term matching) — Steps 1-2 of a new,
more rigorous development process are done: fresh independent context
curation, then a formal design document. **Stopped for mandatory human
design-review gate, as directed.** No implementation has begun.

## Where We Are
Design document complete: `dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md`. Planning-checkpoint retro written:
`dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md`. `ROADMAP.md`/
`CHANGELOG.md` updated. About to commit + push this checkpoint, then
present the design's two unresolved questions to the user and wait —
do NOT proceed to Step 4 (implementation planning) or any code change
until explicit approval arrives.

## Decisions In Flight
- **§9.1 (design doc): inheritance scope** — Option A (full rules A-D,
  requires threading `Journal` into `matches_transaction`/
  `matches_posting`'s signatures — a protected, documented API change)
  vs. Option B (own-tags-only, disclosed divergence, no signature
  change). Lead recommends A. **Not decided.**
- **§9.2: `accounts` command's matching mode** — mirror hledger's real
  posting-own-tag-stripping quirk (source-confirmed, one call site) vs.
  uniform matching (disclosed divergence, no special case). Lead
  recommends uniform/no special case. **Not decided.**
- §9.3 (inheritance-helper's public/private shape) is contingent on
  §9.1 and deferred to implementation planning either way — not a
  blocking gate.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/23-tag-query-matching-design.md`
  — the design document; §17 lists exactly what needs approval.
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md` — this
  checkpoint's retro.
- `ledgerkit/query/eval.py` — `matches_transaction`/`matches_posting`
  currently take no `Journal` parameter (confirmed by direct read this
  session); central to §9.1's cost comparison.
- `ledgerkit/tags.py` — confirmed, by direct read, to have exactly five
  functions, none implementing inheritance; `Journal.
  declared_account_tags` is populated but has no consumer anywhere.
- `dev-docs/planning/core-redefinition/19-tag-query-semantics-brief.md`
  — Phase 4's own brief; largely confirmed correct this session, with
  two refinements (the `accounts` third mode; the "no tag data model"
  framing needing an update now that Phase 4 has shipped).

## Blockers / Open Questions
Both are the design's own §9.1/§9.2 (above) — genuinely open, no
implementation until the user resolves them. Nothing else blocking.

## What NOT To Revisit
- Stage A/B, Stage C Phases 1-5A are closed. Phase 6's planning
  checkpoint is complete (about to be committed this response);
  implementation has not started and must not start without explicit
  approval of §9.1/§9.2.
- Don't re-verify what the context-curator dispatch and the lead's own
  follow-up already independently confirmed (the four inheritance
  rules, the AND-not-OR combination — now executable-evidenced, the
  `accounts` third mode, the missing-inheritance-layer fact, the
  `Journal`-parameter absence) — these are established findings to
  build on, not open questions.
- Don't silently pick Option A or B for §9.1, or a mode for §9.2, and
  proceed — both are explicit, named human-decision gates in the design
  document, matching this project's established gate discipline (Stage
  C Phase 5's `G-DEPTH-*`/`G-CC-*` precedent).
- Don't treat this checkpoint as the phase's own full retro — Step 9's
  full retro (covering implementation, verification, and an explicit
  evaluation of whether this new process was worth its cost) comes
  later, after implementation, not now.

## Recent Git State (before this response's commit, if any)
f397d85 docs: Stage C Phase 5A -- adopt CodeCompass v1 development workflow
eecb8a9 docs: amend Stage C Phase 5A plan per review findings
c6e4b1e docs: plan Stage C Phase 5A -- CodeCompass workflow adoption
c6168b2 docs: Stage C Phase 5, commit 3/3 -- independent verification + closeout
e8f3633 feat: Stage C Phase 5, commit 2/N -- redesign depth: as a report option

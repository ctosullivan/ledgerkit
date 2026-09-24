# CC-LK-002 — Re-testing CC-LK-001's own finding after CG-004's fix: real improvement, one gap unchanged (and already independently filed as CG-006)

## Identification
- **Finding ID:** CC-LK-002
- **Ledgerkit revision:** `eecb8a9`
- **CodeCompass revision:** `4bc7c1d`
- **Task / session:** Stage C Phase 5A — CodeCompass development workflow
  adoption; research task for `tag:` query-term matching (G-CC-2).
- **Date:** 2026-09-25

## Problem statement
CC-LK-001 (2026-09-16) found `query relations` returned zero relations
for three real, topically-connected dev-docs files, root-caused to
`CG-004` (`doc_artifacts.name` never populated for `spec_doc` rows).
CodeCompass's own records show `CG-004` closed the very next day (Phase
55b, 2026-09-17). Per this phase's own "don't anchor to prior findings,
independently verify" instruction: does that fix change CC-LK-001's
result when re-tested live, nine days later, on the real repo?

## Context supplied by CodeCompass
- **What CodeCompass returned:** `doc_artifacts.name` is now populated
  for `spec_doc` rows (e.g. `dev-docs/hledger-compatibility.md` →
  "Hledger Compatibility"). 18 real `mentions_artifact` edges now exist
  project-wide — zero existed at CC-LK-001's own filing. Two concrete new
  edges: `README.md` → `dev-docs/hledger-compatibility.md`, and
  `19-tag-query-semantics-brief.md` → `.claude/skills/codecompass/
  SKILL.md` (the latter enriched this session via `codecompass enrich
  apply`, the agent-facing path, since no `ANTHROPIC_API_KEY` is
  configured here). **But** re-testing CC-LK-001's own exact pair
  (`07-query-regex.md` ↔ `17-query-semantics-brief.md`) directly: still
  **zero** relations, confirmed by inspecting both files — `17` cites
  `07` by filename in its prose, never by `07`'s registered title ("7.
  Query language and regex extension plan"), and `mentions_artifact`
  only matches on title text.
- **Relevant edges/context:** see YAML `edges_or_relations_involved`.
- **Suggested edges involved:** no.

## Independent evaluation
| Criterion | Rating |
|---|---|
| Accuracy | Adequate |
| Relevance | Adequate |
| Completeness | Weak |
| Freshness | n/a |
| Grounding | Strong |
| Noise | Moderate |
| Misleading? | No |

**Outcome:** PASS WITH GAPS

## Context advantage
**LOW**, but genuinely mixed rather than a flat repeat of CC-LK-001. The
fix (`CG-004`) is real, correctly scoped, and now demonstrably works on
new, real Ledgerkit content it had never touched before — including one
concrete, correct, non-trivial finding (the brief-19-to-CodeCompass-Skill
relation, which flags a documented cross-project accuracy correction). A
fresh agent scanning `codecompass check`'s coverage report would
plausibly find that faster than by cold-reading every brief. CC-LK-001's
own specific complaint (the causally-related 07/17 pair) is unchanged —
for a precise, now-verified reason, not a vague "still doesn't work."

## Missing / manual rediscovery
- The *meaning* of the brief-19 edge (a specific documented correction,
  not a generic tool mention) — required reading the brief directly.
- That `07-query-regex.md` and `17-query-semantics-brief.md` are causally
  connected at all — entirely unavailable from the graph either before or
  after `CG-004`'s fix; found only by reading both documents' own prose.

## Impact
Missing relationship (title-vs-filename matching gap) — but already
filed and diagnosed independently by CodeCompass's own team.

## Suggested generalised improvement
None proposed as new. Checked directly against CodeCompass's own
`planning/context-gaps/inbox.md` rather than left speculative: **`CG-006`**
(filed 2026-09-17, the day after CC-LK-001) is this *exact* pair, already
root-caused to the same title-only-matching limitation, with a concrete,
low-cost fix already sketched (a second, filename-based matching mode, no
schema change). This finding is a **third** independent confirmation of
the same gap (CC-LK-001 → CG-006 → this) — recorded as corroboration that
it still reproduces on the pinned revision tested here, not as a new
proposal.

## Recommendation
`collect_more_evidence`, priority **low** — the fix this finding set out
to check (`CG-004`) is confirmed working and correctly scoped; the
remaining gap (`CG-006`) is already filed, diagnosed, and has a sketched
fix, all owned by CodeCompass's own review process.

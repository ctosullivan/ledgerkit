# CONTEXT.md — Claude Session Working Memory

## Current Task
Planning (not implementation) a phase to (1) bring Ledgerkit's
CodeCompass integration current and (2) use the upgraded tooling for a
genuine clean-room reconstruction of Ledgerkit's human-facing
documentation, per direct user request (2026-10-02). Stage C is `[DONE]`
(2026-09-27); Stage D (Reporting) is `[PLANNED]`, not started. This
initiative runs before Stage D, as a cross-cutting tooling/documentation
effort, not a new Stage letter.

## Where We Are
The planning document is written and committed:
`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md`. It is a six-phase plan (CodeCompass reconciliation →
isolation-mechanism adoption → per-topic evidence/snapshot/independent-
reconstruction → documentation drafting → legacy reconciliation → final
audit). **Stops for explicit human approval before Phase 1 begins** — five
open questions are listed in the plan's §8 (where this sits in
`ROADMAP.md`; whether `knowledge/*.md` is in/out of the clean-room
evidence boundary; whether to fix `CLAUDE.md`'s stale folder-structure
diagram in passing; whether six phases is the right granularity; whether
`dev-docs/hledger-compatibility.md` is in-scope for Phase 4's draft set).
Next real step is the user's answer to those five questions, then Phase 1
can start without further discovery.

## Decisions In Flight
Judgment calls made while writing the plan, not yet confirmed by the
user (see plan §8 for the full list):
- Recommended ROADMAP.md placement: a new section parallel to the Stage
  A–I ladder, not a Stage letter.
- Recommended evidence/excluded boundary (plan §3.2): `ledgerkit/**`,
  `tests/**`, `pyproject.toml`, compat-register YAMLs, CLI behaviour, and
  the pinned hledger reference are evidence; `README.md`/`docs/**`/
  `dev-docs/architecture.md`/`dev-docs/api-spec.md`/
  `dev-docs/hledger-compatibility.md`/`CHANGELOG.md`/`ROADMAP.md`/
  `CONTEXT.md`/retros/planning-doc prose are excluded from the blind
  reconstruction stage; `knowledge/*.md` is *also* excluded from that
  stage (safer reading of Objective 2) despite being evidence-cited
  decision records rather than pure narrative — flagged as the most
  debatable call in the boundary table.
- Recommended NOT importing CodeCompass's own internal Claim/Evidence/
  snapshot-integrity validator tooling, and NOT adopting 7 of its 9 new
  upstream agent roles (only `implementation-reconstructor` and
  `domain-skeptic` are proposed) — both as non-goals, scoped to what
  Ledgerkit's size actually needs.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
  room-docs.md` — the plan itself; read this first in any follow-up
  session.
- `dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-PLAN.md` — this
  phase's own retro (planning-only, matching the existing "-PLAN" retro
  precedent).
- `/home/cormac/projects/codecompass` — local editable-install clone,
  `HEAD` confirmed current against `origin` this session (fetch showed
  0/0 ahead/behind). `decisions/0066` and
  `planning/phase-79-clean-room-understanding-and-documentation-
  reconstruction.md` are the upstream methodology this plan adopts from.
- The `codecompass-template` repo (`https://github.com/ctosullivan/
  codecompass-template`) was cloned read-only into this session's scratch
  directory to inspect `optional-clean-room-workflow/` — not part of the
  Ledgerkit repo; re-clone if a future session needs to inspect it again
  rather than assuming the scratch copy still exists.
- `.claude/agents/{docs-reconstructor,docs-maintainer,
  release-phase-auditor,roadmap-context-curator}.md` — confirmed drifted
  against upstream's current versions (diffed `docs-reconstructor.md`
  directly this session: 92 lines here vs. 176 upstream, missing the
  hardened topic-scoped MODE 2). Reconciling these is Phase 1's work, not
  done yet.

## Blockers / Open Questions
The five questions in the plan's §8 — all need an explicit answer before
Phase 1 starts. Nothing else is blocked.

## What NOT To Revisit
- Don't re-derive CodeCompass's current version/schema state from
  scratch — already confirmed this session: editable install, `HEAD`
  current against origin, `context-graph.db` schema already at the live
  `_SCHEMA_VERSION` (`'11'`), only 7 runtime commits landed since
  Ledgerkit's last sync and only one (Phase 77) touched anything schema-
  relevant. "Upgrade CodeCompass" is a small re-sync+reconciliation task,
  not a migration — don't scope it as bigger than that without new
  evidence.
- Don't re-derive the isolation-mechanism design from scratch — adopt
  `codecompass-template`'s `optional-clean-room-workflow/` directly (plan
  §3.1); don't re-litigate whether strict mechanical isolation is
  achievable — it isn't, for the same reason it isn't for CodeCompass
  itself (public GitHub mirror + any `Bash`-capable role), confirmed via
  `decisions/0066`, not assumed.
- Don't begin Stage D or any Stage C follow-on from this task — this
  initiative is explicitly ordered before Stage D, not a replacement for
  scoping it.
- Don't implement anything from the 29-...md plan without the user's
  answers to its §8 questions first.

## Recent Git State (before this response's commit)
6c90b4c docs: mark Stage C [DONE], archive its changelog history
ea08a67 docs: Stage C closeout retro -- Definition of Done met
29e0233 docs: fix stale Depth reference in matches_posting's own docstring
fde239c docs: fix four findings from Stage-C-wide drift audit
301a42d docs: remove stale duplicate Phase 9 status paragraph from ROADMAP

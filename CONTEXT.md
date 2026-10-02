# CONTEXT.md — Claude Session Working Memory

## Current Task
An amended planning document exists for a cross-cutting phase to (1)
bring Ledgerkit's CodeCompass integration current and (2) use the
upgraded tooling for a genuine clean-room reconstruction of Ledgerkit's
human-facing documentation. Stage C is `[DONE]` (2026-09-27); Stage D
(Reporting) is `[PLANNED]`, not started. This initiative runs before
Stage D, as a cross-cutting tooling/documentation effort, not a new
Stage letter.

## Where We Are
`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
room-docs.md` has been **amended** (same day as its original draft) per
a direct review that found 8 concrete defects in the first draft. All 8
are fixed in place (same file, same six-phase structure) and **all 5 of
the plan's own original open questions are now resolved** — there is
nothing left open in the plan itself. **Still stops for explicit human
approval before Phase 1 begins** — the plan is implementation-ready, but
no sub-phase has started. Next real step is the user's go-ahead to begin
Phase 1 (CodeCompass reconciliation & revision pinning, §2 of the plan).

## Decisions In Flight
None — this amendment resolved every open decision the original plan
left pending (§8 of the plan, Part A items 1–5). For the record, the
resolutions:
- ROADMAP.md placement: a new "Tooling & Process Initiatives" section,
  parallel to the Stage A–I ladder, not a Stage letter.
- `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` stays
  excluded from blind reconstruction (Phase 3/4); reintroduced in Phase 5
  specifically as rationale/intent evidence.
- `CLAUDE.md`'s stale folder-structure diagram gets corrected during
  Phase 1 (through the Unauthorised Change Rule's normal confirm-first
  step).
- Six-phase structure retained — no compelling implementation reason
  found to merge Phase 1 and Phase 2.
- `dev-docs/hledger-compatibility.md` is reconciliation-first (Phase 5),
  not a blind clean-room redraft — its existing, evidence-dense
  structure is preserved where independently supported.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-
  room-docs.md` — the amended plan; read this first in any follow-up
  session. Key new sections this amendment added: the hard invariant
  banner (top of file, before §1); §2.0 (revision pinning); §3.7
  (snapshot-integrity checker); §5.1 (complete 9-document inventory/
  disposition table); §8 Part A/Part B split (resolved questions vs. the
  8 review findings, F1–F8); §12 (this amendment's own internal
  consistency review).
- `dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-PLAN.md` — the
  planning-phase retro, now with a same-day addendum covering this
  amendment, including a self-caught second-order defect (a numbering
  collision the amendment itself introduced while fixing the review's
  findings, found and fixed by the plan's own new §12).
- `/home/cormac/projects/codecompass` — local editable-install clone;
  §2.0 of the plan now requires Phase 1 to re-fetch and formally pin its
  exact `HEAD` SHA (and `codecompass-template`'s) before any further
  phase runs, rather than treating "current" as a moving target.
- `.claude/agents/{docs-reconstructor,docs-maintainer,
  release-phase-auditor,roadmap-context-curator}.md` — still confirmed
  drifted against upstream's current versions (unchanged finding from
  the original planning session). Reconciling these is Phase 1's work,
  not done yet.

## Blockers / Open Questions
None in the plan itself (all 5 resolved this amendment). The only
remaining gate is the user's explicit go-ahead to begin Phase 1 — this
amendment, like the original plan, stops short of that.

## What NOT To Revisit
- Don't re-litigate any of the plan's original 5 open questions — all
  resolved this amendment (§8 Part A of the plan). Don't re-litigate the
  8 review findings either — all fixed in place (§8 Part B).
- Don't re-derive CodeCompass's current version/schema state from
  scratch — confirmed in the original planning session (editable
  install, schema already current, only 7 runtime commits since last
  sync) and unchanged by this amendment; §2.0 just adds the requirement
  to formally pin the SHA at Phase 1's own start rather than treating the
  original session's observation as a standing pin.
- Don't re-derive the isolation-mechanism design from scratch — adopt
  `codecompass-template`'s `optional-clean-room-workflow/` directly
  (plan §3.1); strict mechanical isolation is confirmed unachievable for
  the same structural reason as for CodeCompass itself (public GitHub
  mirror + any `Bash`-capable role) — don't re-litigate this either.
- Don't compare any Phase 3 or Phase 4 output against existing
  documentation (`README.md`, `docs/**`, `dev-docs/architecture.md`,
  `dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`,
  `ROADMAP.md`'s prose, `knowledge/*.md`) — that comparison is Phase 5's
  job only, per the plan's hard invariant (top of the document). This
  was the single sharpest defect this amendment fixed (review finding
  F1) — a future session extending this plan should re-read the
  invariant banner before adding anything to Phase 3 or Phase 4.
- Don't begin Stage D or any Stage C follow-on from this task — this
  initiative is explicitly ordered before Stage D, not a replacement for
  scoping it.
- Don't implement anything from the plan without the user's explicit
  go-ahead to start Phase 1 — the plan being fully resolved is not the
  same as being approved to execute.

## Recent Git State (before this response's commit)
7032b3e docs: plan CodeCompass upgrade + clean-room docs reconstruction
6c90b4c docs: mark Stage C [DONE], archive its changelog history
ea08a67 docs: Stage C closeout retro -- Definition of Done met
29e0233 docs: fix stale Depth reference in matches_posting's own docstring
fde239c docs: fix four findings from Stage-C-wide drift audit

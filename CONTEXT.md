# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage B ("Core model") is complete — user explicitly confirmed `[DONE]` on
2026-09-13. This response archives Stage B's changelog entries and updates
`ROADMAP.md`/the core-redefinition README accordingly. Stage C (query
system) is next but not yet scoped or approved for implementation.

## Where We Are
`dev-docs/changelog/STAGE-B.md` created (both Stage B Phase entries,
oldest first, plus a closing note recording the retro bulk-review
conclusion: no process friction, no roster gap, no process change
indicated). `CHANGELOG.md`'s two raw Stage B entries replaced with one
summary block pointing at the archive. `ROADMAP.md`'s Stage B row now
`[DONE]`. `dev-docs/planning/core-redefinition/README.md`'s status header
updated to `[STAGE B — DONE]`. No `ledgerkit/`/`tests/` code has changed
across all of Stage A or Stage B — both stages were entirely
docs/process/planning work plus one licence migration.

## Decisions In Flight
- None new this response — Stage B's guardrail decision (`declared_accounts`
  additive-only) was already recorded in `knowledge/DECISIONS.md` in the
  prior response (Phase 2).

## Files Currently Relevant
- `dev-docs/changelog/STAGE-B.md` — new archive file.
- `CHANGELOG.md` — Stage B entries replaced with a summary block.
- `ROADMAP.md` — Stage B row now `[DONE]`.
- `dev-docs/planning/core-redefinition/README.md` — status header updated.
- Everything from the prior two responses (Phase 1/2 artifacts, retros,
  guardrail decisions) is unchanged content, now closed out under Stage B.

## Blockers / Open Questions
- Stage C (query system — parser/AST, hledger query semantics, Python
  `re` extension, CLI/report routing) is next but **not scoped or
  approved for implementation** — per `ROADMAP.md`'s own process, needs
  an explicit scope decision before any `ledgerkit/query/` code is
  written, same as both Stage B phases needed.
- G5's "in principle" approval for `ledgerkit/query/` and the parser
  lot-annotation change is still not itself authorisation to start
  writing that code.
- A full `hledger` source checkout exists at `/home/cormac/projects/hledger`
  on this machine — still unconfirmed with the user whether that's the
  intended pinned reference for `compat-differential-tester` (relevant
  once Stage C starts).
- The finer-grained `hledger-compatibility.md` rows (dates, amount
  formats, comment forms, account-name rules) are still unmigrated into
  the compat-register — open follow-up from Stage A, not a blocker.
- `EditorDocument`'s include-directive backlog item (reclassified to
  Stage B in `ROADMAP.md`'s backlog table) was not picked up as a Stage B
  phase — it's now known to be lower-urgency than assumed (Stage B Phase
  1 found `EditorDocument` isn't actually used by `ledgerkit-editor`
  today) but is still open; needs an explicit decision on whether it
  belongs in Stage C or stays deferred.

## What NOT To Revisit
- Stage A and Stage B's scope and completion status are both settled —
  don't re-litigate either.
- The per-phase retro process is adopted, has now been bulk-reviewed once
  (at Stage B's close) and found to need no process changes yet — don't
  re-ask about it.
- Don't re-litigate Stage B's two guardrails (`declared_accounts`
  additive-only; `compare=` discipline) or its three corrections to G8 —
  all independently verified, with citable evidence in
  `15-editor-compat-inventory.md` and `16-model-review.md`.
- Milestones 0–4 do not get retroactive retros — deliberately, per
  `dev-docs/retros/README.md`'s scope note.

## Recent Git State (before this response's commit, if any)
a3cf2a7 feat: close out Stage A — agent roster and compatibility-register harness
e702497 fix: revert pyproject.toml license to classic form for Python 3.8 CI
67436ec chore: relicense to GPL-3.0-or-later, redefine Core goal and roadmap
572e77b fix: correct YAML syntax in publish workflow
440f570 chore: sync __version__ to 1.0.0.dev1 and update publish workflow

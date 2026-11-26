# CONTEXT.md — Claude Session Working Memory

## Current Task
CodeCompass retirement + minimal Axiom adoption, per
`ctosullivan/axiom-dev`'s handoff
(`planning/phase-02-ledgerkit-codecompass-migration-handoff.md` in that
repository, PR #8, commit `3adda2a`). Implemented as a Ledgerkit PR
(branch `phase-2/codecompass-retirement-axiom-adoption`) in an isolated
worktree — **not yet merged**, awaiting this repository's own owner's
explicit review and approval.

## Where We Are
PR opened against `ctosullivan/ledgerkit` `main`. Removed (tracked
files): `.claude/agents/context-curator.md`, `validation/codecompass/`
(whole directory), `dev-docs/clean-room/check_codecompass_pin.sh`,
`dev-docs/clean-room/PINNED-REVISIONS.md`, the `## CodeCompass` section
of `CLAUDE.md` (replaced with `## Axiom`), and the folder-structure
diagram's CodeCompass-specific lines. **Not removed by this PR** (and
cannot be, via any PR diff): `vendor.toml`, `context-graph.db`,
`.claude/skills/codecompass/SKILL.md`, `.claude/commands/discovery.md`
— all four were already git-untracked/gitignored local-only files, never
part of Git history; removing them is a one-line local `rm` the
repository owner can do directly, with no review needed and no effect
on any fresh clone (which never had them either). Added: the
`axiom-work` skill, the pinned `axiom_knowledge` library + launcher +
dedicated venv at `dev-docs/tools/axiom_knowledge/`, `knowledge/README.md`,
`knowledge/wiki/README.md`, one scope manifest for
`LK-COMPAT-PARSER-TAG-COMMODITY-001`, and `.gitignore`/`CLAUDE.md`
reconciliation. One new `knowledge/DECISIONS.md` entry records the
retirement decision and what moved.

**Note on local `main`**: this branch is based on Ledgerkit's local
`main`, which is 6 commits ahead of `origin/main` (unrelated, pre-existing
Plan 29 "CodeCompass upgrade + clean-room documentation" work) — those
commits are untouched by this migration and will show in the PR diff
as a pre-existing condition, not something this PR introduces.

## Decisions In Flight
- Historical CodeCompass planning/retro docs
  (`dev-docs/planning/core-redefinition/04-,18-,22-,29-codecompass-*.md`,
  `dev-docs/retros/CODECOMPASS-*`, `STAGE-C-PHASE-2*`,
  `STAGE-C-PHASE-5A*`) are **retained in the active tree**, not removed
  — the handoff's §A.3 treats their removal as recommended, not
  mandatory, and leaves the choice to this repository's owner (§E item
  3). Retaining them avoided a wider cascade of dangling-citation fixes
  across several `.claude/agents/*.md` files for a removal that was
  never part of the pre-authorised scope (§A.1/§B only).
- `ROADMAP.md`'s "CodeCompass upgrade + clean-room documentation
  reconstruction" row is **not** marked `[DONE]` — only its now-moot
  CodeCompass-re-pin follow-up clause was removed. The `[DONE]`
  confirmation itself is explicitly left to the owner (§E item 1).
- The general-purpose clean-room methodology (`dev-docs/clean-room/`'s
  scripts/templates not already removed above) is untouched — §E item
  2 leaves its long-term disposition to the owner.

## Files Currently Relevant
- `knowledge/DECISIONS.md` — new 2026-11-26 entry, the authoritative
  record of what moved and why.
- `CLAUDE.md` — `## Axiom` section and folder-structure diagram, both
  updated.
- `dev-docs/tools/axiom_knowledge/` — the pinned library, launcher,
  `PINNED-REVISION.md`, `NOTICE`/`LICENSE`.
- `.claude/skills/axiom-work/SKILL.md` — the installed skill.
- `knowledge/scope-manifests/LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml`,
  `knowledge/wiki/README.md`.

## Blockers / Open Questions
Three items explicitly left for the human owner (handoff §E), not
resolved by this migration:
1. Confirm (or not) the `ROADMAP.md` CodeCompass-upgrade row `[DONE]`.
2. Decide whether to retain or archive the clean-room methodology
   apparatus independent of this migration.
3. Decide whether to remove the historical CodeCompass planning/retro
   docs from the active tree (this PR retained them).

## What NOT To Revisit
- Do not re-litigate the architectural decision to retire CodeCompass —
  made by the owner, not reopened by this migration.
- Do not add `axiom-knowledge` to `pyproject.toml`'s `[project.scripts]`
  — explicitly out of scope.
- Do not modify `dev-docs/compat-register/` or edit any existing
  `knowledge/*.md` entry — only additions are authorised.

## Recent Git State
See `git log --oneline -10` on branch
`phase-2/codecompass-retirement-axiom-adoption` for this migration's
own commits, layered on local `main`'s existing 6-commit lead over
`origin/main` (unrelated Plan 29 work, untouched here).

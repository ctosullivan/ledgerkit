# CONTEXT.md — Claude Session Working Memory

## Current Task
Added a standing "Commit & Push Cadence" rule to `CLAUDE.md`, per explicit
user direction: commit at logical intervals, push automatically at the
end of each successful phase, without asking each time. Meanwhile, Stage C
Phase 1 (query-system semantics research) is running in the background —
`hledger-researcher` is producing a semantics brief
(`dev-docs/planning/core-redefinition/17-query-semantics-brief.md`) for
the initial query-term set before any `ledgerkit/query/` code is written.

## Where We Are
`CLAUDE.md` now has a "Commit & Push Cadence" section (between Retro
Reports and Commit Message Format). `dev-docs/retros/README.md`'s
lifecycle diagram, `.claude/agents/roadmap-context-curator.md` (phase-end
job), and `.claude/agents/release-phase-auditor.md` (new DoD check #9)
all updated to reference it. `knowledge/DECISIONS.md` has the rationale
entry. `CHANGELOG.md` entry added. This is a complete, self-contained
process change — under the very rule just added, it should be committed
and pushed now rather than held. Separately: the Stage C semantics-brief
agent has not yet reported back; do not fabricate or assume its findings
when it does — read the notification when it lands, then implement
`ledgerkit/query/`'s AST/parser/evaluator from that brief.

## Decisions In Flight
- None new beyond what's now in `knowledge/DECISIONS.md` (the commit/push
  cadence rationale, 2026-09-13).

## Files Currently Relevant
- `CLAUDE.md` — new Commit & Push Cadence section.
- `dev-docs/retros/README.md`, `.claude/agents/roadmap-context-curator.md`,
  `.claude/agents/release-phase-auditor.md` — cross-referenced.
- `knowledge/DECISIONS.md`, `CHANGELOG.md` — both updated.
- `dev-docs/planning/core-redefinition/17-query-semantics-brief.md` — will
  exist once the background `hledger-researcher` agent finishes; not yet
  written as of this response.

## Blockers / Open Questions
- Stage C Phase 1 is blocked on the `hledger-researcher` semantics brief
  landing — do not start writing `ledgerkit/query/` code before it does.
- Stage B's `EditorDocument` include-directive backlog item is still open
  and unscoped (lower priority now, per Stage B Phase 1's finding that
  `EditorDocument` isn't actually used by `ledgerkit-editor` today).
- Whether `/home/cormac/projects/hledger` is the intended pinned reference
  for `compat-differential-tester` is still unconfirmed with the user.
- The finer-grained `hledger-compatibility.md` rows are still unmigrated
  into the compat-register — open follow-up from Stage A, not a blocker.

## What NOT To Revisit
- Stage A and Stage B are both closed and settled.
- The per-phase retro process and the new commit/push cadence are both
  adopted — don't re-ask about either; the latter is explicit,
  user-directed standing authorisation, not something to re-confirm per
  commit.
- Don't re-litigate Stage B's guardrails or corrections — see prior
  `CONTEXT.md` history / `knowledge/DECISIONS.md` if needed.
- Milestones 0–4 do not get retroactive retros.

## Recent Git State (before this response's commit, if any)
f51a18b feat: close out Stage B — editor-compat inventory, model review
a3cf2a7 feat: close out Stage A — agent roster and compatibility-register harness
e702497 fix: revert pyproject.toml license to classic form for Python 3.8 CI
67436ec chore: relicense to GPL-3.0-or-later, redefine Core goal and roadmap
572e77b fix: correct YAML syntax in publish workflow

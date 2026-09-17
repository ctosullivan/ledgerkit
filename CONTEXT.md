# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 4 (tag data model — parsing/storage only, not the `tag:`
query term) is done. About to commit and push (single commit — this
phase, like Phase 3, is cohesive enough not to need a multi-commit
boundary structure).

## Where We Are
Full closeout complete: implementation (`ledgerkit/tags.py`,
`models.py`, `parser.py`), 46 new tests (728 total, all passing),
differential verification against the pinned hledger 1.52.4 binary, 4
new compat-register entries (all `status: verified`), and all doc/
knowledge updates (`dev-docs/api-spec.md`, `dev-docs/architecture.md`,
`dev-docs/hledger-compatibility.md`, `docs/journal-format.md`,
`knowledge/DOMAIN_RULES.md`, `knowledge/DECISIONS.md`, `ROADMAP.md`,
`CHANGELOG.md`) are all written. Retro written:
`dev-docs/retros/STAGE-C-PHASE-4.md`. Next: `git commit` + `git push`.

## Decisions In Flight
- None — both open questions this phase raised (split data-model-first
  vs. push through disorganized; back-reference vs. pure-function
  date-override resolution) were put to the user via `AskUserQuestion`
  and resolved, then recorded in `knowledge/DECISIONS.md`.

## Files Currently Relevant
- `ledgerkit/tags.py` — new module (`parse_tags`, `effective_date`,
  `effective_date2`).
- `ledgerkit/models.py`, `ledgerkit/parser.py` — new tag fields and
  parser wiring.
- `dev-docs/compat-register/LK-COMPAT-PARSER-TAG-001.yaml`,
  `LK-COMPAT-PARSER-TAG-SCOPE-001.yaml`,
  `LK-COMPAT-PARSER-POSTINGDATE-001.yaml`,
  `LK-COMPAT-DIRECTIVE-TAG-001.yaml` — new entries, all verified.
- `dev-docs/retros/STAGE-C-PHASE-4.md` — this phase's retro.

## Blockers / Open Questions
- The `tag:NAME[=REGEX]` query term itself (brief 19's remaining scope:
  matching, the four inheritance rules, always-AND-never-OR combination,
  and the separate account-name-level matching mechanism) is unscoped —
  deliberately deferred by the user's split decision, not started.
- Stage C's other named-but-unscoped candidate remains `cur:` term
  extension and the larger `Query`-as-compatibility-shim migration
  (`07-query-regex.md` §6.5). Neither started.
- `check` remains the only report/display command without `-q` — by
  design (checks apply to the whole journal), unrelated to this phase.

## What NOT To Revisit
- Stage A, Stage B, and Stage C Phases 1-4 are all closed/committed
  (Phase 4 about to be, this response).
- Don't re-litigate the tag data-model field shapes (`Posting.tags`,
  `date_override`/`date2_override`, `Transaction.tags`,
  `Journal.declared_account_tags`, pure-function date resolution) —
  explicitly user-confirmed via `AskUserQuestion`, not the lead's
  unilateral call.
- Don't re-run this phase's differential verification — done, evidenced
  (4 verified compat-register entries), about to be committed.
- Don't conflate `Journal.declared_tags` (the pre-existing `tag`
  directive's list of allowed tag *names*, `LK-COMPAT-TAGDIR-001`) with
  the new `Journal.declared_account_tags` (per-account `(name, value)`
  tag pairs from `account` directive comments, this phase's
  `LK-COMPAT-DIRECTIVE-TAG-001`) — distinct fields, distinct features.

## Recent Git State (before this response's commit, if any)
d362bbb feat: Stage C Phase 3 -- wire -q/--query into print
b7d5d32 docs: Stage C Phase 2, commit 3/3 -- context evaluation + closeout
27c410d feat: Stage C Phase 2, commit 2/3 -- query/report/CLI integration
0f4465d docs: Stage C Phase 2, commit 1/3 -- CodeCompass baseline
d86f9b4 docs: amend Stage C Phase 2 plan per review findings

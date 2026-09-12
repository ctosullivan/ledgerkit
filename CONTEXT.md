# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 1 (query semantics research + standalone query engine) is
done. Operating under a standing "proceed with roadmap, recommended
options, until a natural stopping point" directive from the user — this
phase is a reasonable stopping point: a complete, tested, documented unit
of work, with the next phase (wiring into reports.py/cli.py, or extending
the term set) genuinely requiring a fresh scope decision rather than an
obvious continuation.

## Where We Are
`ledgerkit/query/` now exists (`ast.py`, `regex.py`, `parser.py`,
`eval.py`) — a standalone, fully-tested subpackage (81 new tests, 656
total, all passing) implementing `acct:`/`desc:`/`date:`(simple)/
`depth:`/`status:`/`not:`. Not yet re-exported from `ledgerkit/__init__.py`
and not yet wired into `reports.py`, `cli.py`, or `Query`. Docs updated:
`dev-docs/api-spec.md` (new section, user-approved), `hledger-
compatibility.md` (new Query Language section), 7 new compat-register
entries (all `status: proposed`), 2 new `knowledge/DOMAIN_RULES.md`
entries. `ROADMAP.md` Stage C row updated. Retro written:
`dev-docs/retros/STAGE-C-PHASE-1.md`. Per `CLAUDE.md`'s Commit & Push
Cadence, this phase is ready to commit and push now (tests passing, docs
synced, retro written) — about to do that next.

## Decisions In Flight
- The `date:` range-separator scope decision (accept `-`/`..`/`' to '`,
  mandatory 4-digit year, no journal-context year inference at query-parse
  time) was made this phase, not deferred — recorded in the retro, not yet
  separately in `knowledge/DECISIONS.md` (it's implementation detail
  rather than a judgment call with real alternatives seriously
  considered, so folding it into the retro was judged sufficient；
  revisit if a future phase finds it under-documented).

## Files Currently Relevant
- `ledgerkit/query/{__init__,ast,regex,parser,eval}.py` — new.
- `tests/test_query/{test_regex,test_parser,test_eval}.py` — new.
- `dev-docs/planning/core-redefinition/17-query-semantics-brief.md` — new
  (the research brief this phase implemented from).
- `dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md` — updated.
- `dev-docs/compat-register/LK-{COMPAT,UNSUP}-QUERY-*.yaml` (7 files),
  `dev-docs/compat-register/README.md` — new/updated.
- `knowledge/DOMAIN_RULES.md` — 2 new entries.
- `ROADMAP.md`, `CHANGELOG.md`, `dev-docs/retros/STAGE-C-PHASE-1.md`.

## Blockers / Open Questions
- Stage C's next phase is unscoped — candidates: wire `ledgerkit/query/`
  into `reports.py`/a CLI `--query` flag; extend the term set (`tag:`,
  `cur:`); design the `PythonRegex`/`pyre:` extension syntax
  (`07-query-regex.md` §7.4, still an open design question). Needs
  explicit scoping before starting, same as this phase did.
- `EditorDocument`'s include-directive backlog item is still open and
  unscoped (Stage B finding: lower priority than assumed).
- Whether `/home/cormac/projects/hledger` is the intended pinned reference
  for `compat-differential-tester` going forward is still unconfirmed with
  the user, though it's now been used directly for real research this
  phase.
- The finer-grained `hledger-compatibility.md` rows from Stage A are still
  unmigrated into the compat-register — open follow-up, not a blocker.

## What NOT To Revisit
- Stage A and Stage B are both closed and settled.
- The per-phase retro process and the commit/push cadence rule are both
  adopted and now demonstrated across three real phases (Stage B x2,
  Stage C x1) — don't re-ask about either.
- Don't re-litigate this phase's query semantics (exclusive-end dates,
  negated-same-prefix-AND, the HledgerRegex construct exclusion list) —
  all sourced from `hledger-researcher`'s brief, verified against the
  pinned hledger 1.52.4 source, and cross-checked by real tests.
- Milestones 0–4 do not get retroactive retros.

## Recent Git State (before this response's commit, if any)
9c33e37 chore: add standing commit/push cadence; scope Stage C Phase 1
f51a18b feat: close out Stage B — editor-compat inventory, model review
a3cf2a7 feat: close out Stage A — agent roster and compatibility-register harness
e702497 fix: revert pyproject.toml license to classic form for Python 3.8 CI
67436ec chore: relicense to GPL-3.0-or-later, redefine Core goal and roadmap

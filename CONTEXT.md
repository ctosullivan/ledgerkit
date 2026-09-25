# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 7 (empty-regex-pattern rejection) — **implementation
landed, tests passing (844, up from 827), independent verification
NOT yet run.** About to dispatch a genuinely separate `compat-
differential-tester`. No compat-register entry promoted yet;
`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` unchanged, still open.

## Where We Are
Code fix: `ledgerkit/query/regex.py`'s `validate_hledger_regex` rejects
`pattern == ""` (generic message, no `tag:`-specific advice). Tests
added across `test_regex.py`/`test_parser.py`/`test_cli.py`. Docs
synced: `api-spec.md` (breaking-change note), `versioning.md` (new
pre-1.0.dev1 breaking-change policy section), `hledger-compatibility.md`,
`docs/usage.md`, `knowledge/DECISIONS.md`/`DOMAIN_RULES.md`. Compat-
register schema amended generally: `schema.md`'s new "Resolution
lifecycle" section, `09-compatibility-system.md` §9.7, `UNEXPLAINED.md`'s
new "Resolved entries" table — mechanism built, **not yet applied** to
any specific entry. Retro: `dev-docs/retros/STAGE-C-PHASE-7-EMPTY-
REGEX-IMPLEMENTATION.md`. About to commit this implementation, then
dispatch `compat-differential-tester` for independent verification.

## Decisions In Flight
None on the fix itself (fully implemented per approved+amended design).
Pending: what the independent verification dispatch finds. Expected
(per Phase 7's own research matrix) to confirm the fix matches hledger
exactly, but do not assume the outcome — wait for the actual dispatch.

## Files Currently Relevant
- `ledgerkit/query/regex.py` — the implemented fix.
- `tests/test_query/test_regex.py`, `test_parser.py`,
  `tests/test_cli/test_cli.py` — new/updated tests.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml`
  — NOT YET touched this pass; will get `resolved_into`/`resolved_date`
  only after independent verification confirms the fix.
- `dev-docs/compat-register/schema.md` — the new resolution-lifecycle
  mechanism, to be exercised for the first time once verification lands.
- `dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md` —
  ends with "independent verification pending"; will get its own
  addendum once that dispatch returns.

## Blockers / Open Questions
Independent verification is the only remaining gate before: (a)
creating `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` and resolving the
mismatch entry via the new lifecycle, (b) promoting/correcting
`LK-COMPAT-QUERY-TAG-001`/`ACCT-001`/`DESC-001`/`DEPTH-001`'s relevant
claims, (c) considering Phase 7 for `[DONE]` (user's own call, never
inferred).

## What NOT To Revisit
- Don't describe this fix as "backward-compatible" or "no public API
  change" anywhere — it's a documented, intentional breaking change,
  made pre-1.0, framed accurately per `knowledge/DECISIONS.md`.
- Don't invent a version bump for this change — `versioning.md`'s new
  policy section explains why none is needed before a stable `1.0.0`
  ships.
- Don't apply the new resolution-lifecycle mechanism to `LK-MISMATCH-
  QUERY-TAG-EMPTYVALUE-001` before independent verification confirms
  the fix — the mechanism exists now, but using it early would defeat
  the verification-independence rule it's built to support.
- Don't touch `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — untouched,
  explicitly out of scope, still tracks its own separate divergence.
- Don't self-promote any compat-register entry from this session — that
  requires the dispatched `compat-differential-tester`'s own output.

## Recent Git State (before this response's commit)
d88a777 docs: amend Stage C Phase 7 design -- targeted correction pass
c4feb1d docs: Stage C Phase 7 -- empty-regex-pattern rejection design
a49ac50 docs: close out Stage C Phase 6, mark [DONE]
5887ea8 docs: close out Stage C Phase 6 independent verification
fe9dfe5 test: independently verify Stage C Phase 6 tag: compat-register entries

# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C closeout (multi-step): `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`'s
fix is now **implemented and unit-tested** (Stage C Phase 9,
`60eea4a`) — `ledgerkit.query.regex._has_empty_alternation_branch`
wired into `validate_hledger_regex`. **Independent verification has
NOT been performed** — this is the mandatory next step before the new
compat-register entry can move past `status: proposed` and before the
mismatch entry can be resolved. Stage C itself still `[IN PROGRESS]`.

## Where We Are
Implementation done: 935 tests passing (up from 899, +36). Next step is
to dispatch a genuinely separate `compat-differential-tester` agent to
independently re-run the full 18-must-reject/13-must-accept matrix
against the real pinned hledger 1.52.4 binary and Ledgerkit's post-fix
behaviour. Only after that confirmation can:
1. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml` receive
   `resolved_into: LK-COMPAT-QUERY-REGEX-EMPTYALT-001` /
   `resolved_date:` (not done yet — deliberately left untouched this
   session).
2. `LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml` promote `status: proposed`
   → `status: verified` (only a dispatched `compat-differential-tester`
   agent's own output may set `verified` — never self-promoted).
3. `dev-docs/compat-register/UNEXPLAINED.md`'s row for this mismatch
   move from "Open entries" to "Resolved entries".
4. The full Stage C completion audit sequence run (compat-register
   review, `docs-maintainer`, a Stage-C-wide `docs-reconstructor`
   NO-DRIFT pass, roadmap/knowledge reconciliation, a Stage-C-wide
   `release-phase-auditor` pass against every exit criterion, a Stage C
   closeout retro) before reporting whether Stage C's Definition of
   Done is met.

## Decisions In Flight
None blocking. The empty-alternation-branch algorithm (design §3.1) was
independently re-verified against all 31 matrix patterns during this
implementation pass and found correct as written — no discrepancy, no
algorithm change needed.

## Files Currently Relevant
- `ledgerkit/query/regex.py` — `_has_empty_alternation_branch` (new,
  private) and `validate_hledger_regex` (now checks it, alongside the
  unchanged `pattern == ""` check and unchanged `_EXCLUDED_CONSTRUCT`).
- `tests/test_query/test_regex.py` — new `TestEmptyAlternationBranch
  Rejected`/`TestEmptyAlternationBranchAccepted` classes (31 tests).
- `tests/test_query/test_parser.py` — new
  `TestEmptyAlternationBranchRejectedAtParseTime` (4 tests).
- `tests/test_cli/test_cli.py` — new
  `TestQueryFlag.test_empty_alternation_branch_exits_one`.
- `dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml` —
  new entry, `status: proposed`, `resolves: LK-MISMATCH-QUERY-REGEX-
  EMPTYALT-001`. NOT yet promoted.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml` —
  deliberately left completely untouched this session (no
  `resolved_into`/`resolved_date`).
- `dev-docs/retros/STAGE-C-PHASE-9-EMPTY-ALTERNATION-IMPLEMENTATION.md`
  — this phase's implementation retro (distinct from the earlier
  `-PLAN.md` planning retro).
- `knowledge/DOMAIN_RULES.md` / `knowledge/DECISIONS.md` — new entries
  for the adjacency rule and the dedicated-scan-function rationale.

## Blockers / Open Questions
None requiring a human decision. Proceeding to independent verification
is a process step (dispatch a separate `compat-differential-tester`
agent), not a decision gate — this implementation was itself already
authorized as part of the user's "implement through the normal
fresh-agent workflow" instruction from the prior session.

## What NOT To Revisit
- Don't re-derive or second-guess `_has_empty_alternation_branch`'s
  algorithm — independently re-verified against all 31 test cases (18
  reject, 13 accept) this session; correct as designed, no bug found.
- Don't fold the detection into `_EXCLUDED_CONSTRUCT`'s single regex —
  decided and recorded (`knowledge/DECISIONS.md`, 2026-09-27): Python's
  `re` can't correctly count variable-length escape runs via
  lookbehind, and `_EXCLUDED_CONSTRUCT`'s own false-positive tolerance
  is not acceptable for this family's required-accept escaped cases.
- Don't self-promote `LK-COMPAT-QUERY-REGEX-EMPTYALT-001` past
  `status: proposed` — requires a genuinely separate
  `compat-differential-tester` dispatch.
- Don't touch `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`'s `kind`/
  `status`/`resolved_into` fields until that independent verification
  lands.
- Don't re-litigate `PythonRegex` — explicitly resolved as deferred in
  the prior session, reasoned, recorded.
- Don't mark Stage C `[DONE]` — only the user's explicit confirmation
  does that, after the full closeout audit sequence completes.

## Recent Git State (before this response's docs/compat-register commit)
60eea4a feat: reject empty-alternation-branch regex patterns (Stage C Phase 9)
39ab948 docs: close out Stage C Phase 7, plan Phase 9, defer PythonRegex
c5e4185 docs: close out Stage C Phase 8, mark [DONE]
12af5cf docs: reconcile current-truth docs for Stage C Phase 8 overclaim correction
d12e24e fix: correct Stage C Phase 8 compat-register overclaim on accounts=[...]

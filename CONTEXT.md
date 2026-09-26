# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — implementation,
independent verification, AND a post-verification overclaim correction
(with its own second independent re-verification) are all complete.
`LK-COMPAT-QUERY-SHIM-001` is `status: verified` on the corrected, narrower
claim. `docs-maintainer` has just reconciled all current-truth docs against
this final state. `[DONE]` for the phase (and for Stage C) remains the
user's own call, not inferred here.

## Where We Are
Everything committed and pushed to `main` through `d12e24e`:
- `dcac520`/`0852c6f`/`7b9b358`/`a4c5917` — implementation, tests, doc sync,
  retro/changelog/roadmap (implementing agent)
- `38eefe0` — independent verification (`compat-differential-tester`):
  `LK-COMPAT-QUERY-SHIM-001` promoted `proposed` → `verified`, new fixture
  `tests/fixtures/query_shim_differential.journal`, retro Addendum 1
- `d12e24e` — post-verification correction: item 6's "preserved for every
  input" claim was overbroad (a single-account, Python-only-regex value
  like `accounts=[r"\d+"]` now intentionally raises `QueryParseError`,
  where it previously worked via the old permissive matcher). Corrected
  the compat-register entry, the design doc (§5.2 item 6), and
  `dev-docs/api-spec.md`; a second, separate `compat-differential-tester`
  dispatch re-verified all four shim cases directly; two missing
  regression tests added.
- This response's commit (about to land) — `docs-maintainer` pass:
  confirmed `dev-docs/architecture.md`, `dev-docs/hledger-compatibility.md`,
  `docs/python-api.md`, `knowledge/DECISIONS.md`, `knowledge/DOMAIN_RULES.md`
  needed no changes (no overclaim repeated, all accurate against source);
  added the missing `CHANGELOG.md` entry for the `d12e24e` correction;
  updated `ROADMAP.md`'s Stage C row with the correction + re-verification;
  added Addendum 2 to `STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md`
  retro; rewrote this file.

899 tests passing throughout (up from 897 after Phase 8 implementation,
up from 844 before Phase 8).

## Decisions In Flight
None blocking. Two things await a human call, neither urgent:
- Whether/when to mark Stage C Phase 8 `[DONE]` in `ROADMAP.md` — user's
  own call, not inferred by Claude.
- What Stage C's next phase should be — the backlog (below) has two
  named items, none yet scoped.

## Compat-register final state (this phase)
- `LK-COMPAT-QUERY-SHIM-001` — `kind: compatible`, `status: verified`,
  on the **corrected** claim: `accounts=[]` stays no-filter, an ordinary
  `HledgerRegex`-portable single-account pattern is unchanged, a
  Python-only single-account regex now intentionally rejects, and
  two-or-more accounts retain OR-matching via the `Or(...)` AST — NOT
  "preserved for every input," the original, now-corrected overclaim.
  Independently confirmed twice: the design's eight highest-risk claims
  (Addendum 1) and, separately, all four deprecated-shim cases
  specifically (Addendum 2/the second evidence entry).

## Files Currently Relevant
- `dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml` — `status:
  verified` on the corrected claim; not touched by docs-maintainer
  (compat-differential-tester's domain).
- `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md` —
  implementation retro + Addendum 1 (verification) + Addendum 2
  (correction cycle), all dated 2026-09-26.
- `dev-docs/api-spec.md` — `accounts=[...]` note corrected in `d12e24e`;
  confirmed accurate against source this pass.
- `ledgerkit/query/compat.py` — the translator module
  (`_query_to_ast`/`_validated`/`_exclusive_end`), independently verified.
- `ledgerkit/models.py` — `Journal.balance`/`.register`'s deprecated
  `accounts=[...]` shim, zero/one/many handling (lines ~401-466).

## Remaining Stage C backlog (unchanged, none scoped yet)
1. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — the empty-alternation-branch
   divergence (`(|)` confirmed both sides; `a|`/`|a`/`(a|)`/`(|a)`
   hledger-side only) — still open, still out of scope.
2. Explicitly resolve the planned `PythonRegex` extension syntax
   (implement / defer-with-reason / drop — currently just undecided).
Non-blocking, unscoped unless separately promoted: `cur:`, smart/period
dates, a standalone `--depth`/`-N` CLI flag.

## Blockers / Open Questions
None blocking further work on this phase — it's complete, including the
correction cycle.

## What NOT To Revisit
- Don't re-verify the Query-shim convergence — independently confirmed
  clean, twice (the original 8-point matrix, and the corrected item 6's
  own dedicated second re-check).
- Don't re-derive the zero-accounts-must-not-become-`Or(())` fix — now
  confirmed independently, three times over (design review, first
  verification dispatch, second verification dispatch).
- Don't re-litigate whether the deprecated `accounts=[...]` shim
  "preserves all previous behaviour" — it does NOT, for the
  Python-only-regex single-account case; this is now the settled,
  corrected, doubly-verified claim.
- Don't touch `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — separate,
  unrelated, explicitly out of scope, still open.
- Don't mark Stage C Phase 8 `[DONE]` unilaterally — only the user's
  explicit statement does that, per `CLAUDE.md`'s standing rule.

## Recent Git State (before this response's commit)
d12e24e fix: correct Stage C Phase 8 compat-register overclaim on accounts=[...]
38eefe0 test: independently verify Stage C Phase 8 Query-shim convergence
a4c5917 docs: retro, changelog, and roadmap for Query-shim implementation (Stage C Phase 8)
7b9b358 docs: sync docs and compat-register for Query-shim convergence (Stage C Phase 8)
0852c6f test: cover Query-shim convergence (Stage C Phase 8)

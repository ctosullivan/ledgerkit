# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — the design
(twice-amended, fully approved: Option A regex strictness, the `stats`
correction, the `ReportSection` scope boundary, `QueryParseError` reuse)
has now been **implemented** by a fresh coding agent, per this project's
design → approval → fresh-agent → independent-verification process.
Implementation and its own tests/docs are complete. **Independent
verification (a separately-dispatched `compat-differential-tester`) has
NOT happened yet** — that is the next step, not this session's.

## Where We Are
Implementation, tests, and documentation sync are all committed
(`dcac520`, `0852c6f`, `7b9b358`). About to add the changelog/roadmap/
retro/context wrap-up commit and push. After that, this phase is done
from the implementing session's side; the next action belongs to a
`compat-differential-tester` dispatch (§11's differential-test list),
followed by `docs-maintainer`/`docs-reconstructor` drift audits and
`release-phase-auditor`'s Definition-of-Done check, per the project's
standing per-phase cadence. Stage C itself remains `[IN PROGRESS]` (not
`[DONE]`) — only the user marks that.

## Decisions In Flight
None — the design's own approval gate (§12) resolved every genuinely
open question before implementation began. Two small implementer
judgment calls were made during implementation (not decided by the
design's literal text) and have already been recorded in
`knowledge/DECISIONS.md`'s 2026-09-26 entry, not left as in-flight:
- `reports._posting_matches` was deleted outright, not merely left
  unreferenced (dead-code-removal convention).
- `reports._matches_pattern`'s refactored implementation raises
  `UnsupportedRegexConstructError`/`re.error` directly (from
  `compile_hledger_regex`), not wrapped in `QueryParseError` — the
  design's `QueryParseError`-reuse decision is scoped explicitly to
  `Query`/the deprecated shim, not to `ReportSection`.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/27-query-shim-convergence-
  design.md` — the approved design this phase implemented; §5.3 is the
  seven-consumer inventory, §11 is the required differential-test list
  the next agent (`compat-differential-tester`) needs.
- `ledgerkit/query/compat.py` — the new translator (`_query_to_ast`,
  `_validated`, `_exclusive_end`).
- `ledgerkit/reports.py` — `balance`/`register`/`accounts`/`stats`/
  `balance_from_spec` all converged; `_matches_pattern` refactored,
  scoped to `ReportSection.accounts`/`.exclude` only; `_posting_matches`
  and `_REGEX_META` removed.
- `ledgerkit/models.py` — `Journal.balance`/`.register`'s deprecated
  `accounts=[...]` shim (zero/one/many handled explicitly);
  `Journal.to_dataframe` migrated off `_posting_matches`.
- `dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml` —
  `status: proposed`. The next agent's job is to run the design's §11
  differential tests against the pinned hledger 1.52.4 binary and, if
  they confirm, promote this entry (never done by the implementing
  session itself).
- `dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md` — this
  phase's own retro (distinct from the `-PLAN.md` retro, which covers
  only the design phase).

## Blockers / Open Questions
None from this session's side. The standing next step — independent
differential verification — requires a genuinely separate
`compat-differential-tester` dispatch; it is not a blocker so much as
the next scheduled step in this project's own process.

## What NOT To Revisit
- Every item in the design's §12 approval gate is closed: Option A
  (regex strictness), the `stats` account/not_account correction
  in-scope, `ReportSection`'s own OR/exclude control flow kept (only its
  regex dialect converged), `QueryParseError` reuse, and the
  `LK-COMPAT-QUERY-SHIM-001` name. Do not re-open any of these.
- Don't promote `LK-COMPAT-QUERY-SHIM-001` past `status: proposed` from
  within an implementing/lead session — that requires a genuinely
  separate `compat-differential-tester` dispatch (per
  `09-compatibility-system.md` §9.6, the same rule Stage C Phase 5
  onward has applied consistently).
- Don't reintroduce the `Or(())`-for-zero-accounts bug — `accounts=[]`
  must stay explicit "no filter," never routed through the many-accounts
  `Or(...)` branch.
- Don't construct an `Acct(...)`/`Desc(...)` AST node anywhere without
  eager validation via `_validated` first — even a `re.escape`d literal
  that "looks safe."
- Don't mark Stage C Phase 8 or Stage C itself `[DONE]` in `ROADMAP.md`
  — that is the user's own call, not inferred from implementation
  completion (`CLAUDE.md`'s Changelog & Roadmap Rules).

## Recent Git State (before this response's final commit)
7b9b358 docs: sync docs and compat-register for Query-shim convergence (Stage C Phase 8)
0852c6f test: cover Query-shim convergence (Stage C Phase 8)
dcac520 feat: converge Query filtering onto the canonical query engine (Stage C Phase 8)
baace1a docs: amend Stage C Phase 8 design a second time -- final correction pass
12d5cdf docs: amend Stage C Phase 8 design -- targeted correction pass

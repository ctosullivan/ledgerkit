# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — design
document amended after a targeted design-review correction pass (a real
blast-radius gap plus five further corrections, none re-scoping the
phase). **Still stopped for explicit human approval.** No `ledgerkit/`/
`tests/` code touched.

## Where We Are
Design document: `dev-docs/planning/core-redefinition/27-query-shim-
convergence-design.md`, now amended (§2, §3, §5.1/§5.1a/§5.1b/§5.1c,
§7, §8, §9, §10, §11, §12 corrected). Retro addendum, `ROADMAP.md`,
`CHANGELOG.md` updated. About to commit + push, then wait.

## Decisions In Flight
Design §12's six-item approval gate (grew from three), key items:
1. **§6 — regex strictness**: Option A (full `HledgerRegex` convergence)
   vs Option B (permissive fallback). Lead recommends A. **The one
   genuinely blocking fork, unchanged by this amendment.**
2. **§5.1c — `stats` behaviour correction**: confirm closing the
   existing `Query.account`/`.not_account`-ignored-by-`stats` gap is
   wanted as part of this phase (lead recommends yes).
3. **§5.1b — `_matches_pattern`/`ReportSection` scope**: confirm
   retaining/refactoring `_matches_pattern` (not retiring it) with full
   `ReportSpec`/`ReportSection` AST convergence left as a separate
   future item.
4-5. Naming/awareness items (compat-register entry name; reusing
   `QueryParseError` for `Query`-field validation errors) — not
   blocking.
6. General approval to proceed once the above are resolved.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/27-query-shim-convergence-
  design.md` — the amended design document awaiting approval.
- `ledgerkit/models.py:382-432` — `Journal.balance`/`.register`'s
  deprecated `accounts=[...]` shim (the real regression found: `(?:...)`
  synthesis for 2+ accounts, `HledgerRegex`-excluded, zero test
  coverage). Fix: build `Or(...)` directly, per §5.1a.
- `ledgerkit/reports.py:612-694` — `balance_from_spec` (its own,
  separate `_matches_pattern`-based filter; `ReportSection.accounts`/
  `.exclude` depend on it, §5.1b).
- `ledgerkit/reports.py:516-610` — `stats` (the `account`/`not_account`-
  ignored gap, §5.1c).
- New module planned: `ledgerkit/query/compat.py` (the translator,
  `_query_to_ast`/`_exclusive_end`/`_validated` — NOT `models.py`,
  avoids a circular import with `ledgerkit/query/eval.py`).

## Blockers / Open Questions
Design §12's six-item gate, item 1 (regex strictness) is the only
genuinely blocking one. Items 2-3 have stated lead recommendations.

## What NOT To Revisit
- Don't re-derive the blast-radius analysis from scratch — it's now
  correctly scoped (no external consumer affected; three named internal
  paths each have an explicit fix: deprecated `accounts=[...]` shim,
  `ReportSection`/`_matches_pattern`, `stats`).
- Don't propose retiring `_matches_pattern` — it has a live caller
  (`balance_from_spec`/`ReportSection`) and must be refactored in
  place, not removed.
- Don't construct `Acct(...)`/`Desc(...)` AST nodes without validating
  the pattern first via `compile_hledger_regex` — AST nodes don't
  self-validate; lazy evaluation-time validation isn't deterministic
  (may never run, e.g. for an empty journal).
- Don't place the translator in `models.py` — real circular import risk
  (`ledgerkit/query/eval.py` already imports from `models.py`). Use
  `ledgerkit/query/compat.py`.
- Don't translate `Query.date_to` → `DateSpan(end=date_to + timedelta(
  days=1))` unconditionally — overflows at `datetime.date.max`. Map
  `date.max` to `end=None` (unbounded) instead.
- Don't treat the deprecated `accounts=[...]` multi-account path as
  low-risk because "no test uses it" — that's exactly backwards; zero
  test coverage is why the `(?:...)` regression wasn't caught, not
  evidence it's safe.

## Recent Git State (before this response's commit)
fbde262 docs: Stage C Phase 8 -- Query-as-shim convergence design
afbcd05 test: independently verify Stage C Phase 7 empty-regex fix, resolve register
e3e00a1 feat: reject empty regex query patterns (Stage C Phase 7)
d88a777 docs: amend Stage C Phase 7 design -- targeted correction pass
c4feb1d docs: Stage C Phase 7 -- empty-regex-pattern rejection design

<!-- dev-docs/retros/<STAGE-OR-MILESTONE>[-PHASE-K].md — authored by Claude
at phase end (see README.md for naming: no -PHASE-K suffix when the whole
Milestone/Stage was one phase). A few lines is fine for a trivial phase. -->

# Stage C Phase 8 retro — Implementation (`Query`-as-compatibility-shim convergence)

- **Date:** 2026-09-26
- **Commit(s):** see `git log` for this retro's own commit and the
  commits immediately preceding it in this session.
- **Agents used:** none — a single fresh coding-agent session, per this
  project's design → approval → fresh-agent → independent-verification
  process. Independent verification (`compat-differential-tester`) is a
  separate, not-yet-dispatched step.

## Where we are

This is the fourth stage of the `Query`-as-compatibility-shim
convergence item (Stage C Phase 6's own backlog item 2): planning
(`STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md`) produced a design; two same-day
amendment passes corrected it twice, each catching real gaps the prior
pass missed by building an increasingly complete per-consumer inventory
rather than trusting an earlier completeness claim; the design's
approval gate (§12) was then explicitly approved in full — Option A
(full `HledgerRegex` convergence), the `stats` correction, the
`ReportSection` scope boundary, and `QueryParseError` reuse were all
locked in, with only the compat-register entry's exact name left as a
non-blocking implementation detail. This retro covers this session's
implementation of that fully-approved design, dispatched fresh (no
memory of the design/amendment sessions) per the project's standing
process for substantial features.

After this phase, `ledgerkit/reports.py` and `ledgerkit/models.py` no
longer contain a second, parallel, non-hledger-faithful query-matching
path — every `Query`-shaped filter in the codebase reaches the same
`ledgerkit.query` AST/evaluator `-q`/`--query` string terms use, with
exactly one disclosed, scoped exception (`ReportSection.accounts`/
`.exclude`). This closes Stage C Phase 6's backlog item 2 and leaves one
remaining named Stage C item: the `PythonRegex` extension syntax.

## Goal

Implement the design's §5 in full (the translator module, all seven
converged consumers, the deprecated `accounts=[...]` shim's three
explicit cases), every test named in §11, the required documentation
sync (§10), and the compat-register entry (§9) at `status: proposed`
only — in the same session, without re-litigating any of the design's
already-approved decisions.

## Scope delivered vs planned

Delivered exactly what the design specified, no more and no less:

- New module `ledgerkit/query/compat.py` (`_query_to_ast`, `_validated`,
  `_exclusive_end`), placed inside the `query` package per the design's
  explicit module-placement decision, reached via lazy in-function
  imports from both `models.py` and `reports.py`.
- All seven `Query` consumers converged (§5.3's inventory verified
  directly, not assumed): `reports.balance`/`register`/`accounts`/
  `stats`, `reports.balance_from_spec`'s outer query, `Journal.
  to_dataframe`, and the deprecated `accounts=[...]` shim's zero/one/many
  cases.
- `reports._posting_matches` deleted entirely (not merely left
  unreferenced) — a judgment call beyond the design's literal words
  (recorded in `knowledge/DECISIONS.md`), consistent with this project's
  general dead-code-removal convention.
- `reports._matches_pattern` retained and refactored to route through
  `ledgerkit.query.regex.compile_hledger_regex`, scoped to `ReportSection.
  accounts`/`.exclude` only, per the design's explicit non-goal (full
  `ReportSpec`/`ReportSection` AST convergence untouched).
- `_REGEX_META` removed as genuinely dead code once `_matches_pattern`
  no longer needed it (flagged as a possibility in the task brief, and
  it did turn out to be fully dead).
- Documentation sync: `dev-docs/api-spec.md` (the four authorized
  changes only — `Query`'s behavioural note, `stats`/`balance_from_spec`/
  `to_dataframe` before/after notes, the deprecated `accounts=` fix note
  — no unauthorized signature changes), `dev-docs/architecture.md`,
  `dev-docs/hledger-compatibility.md`, `docs/python-api.md`,
  `knowledge/DECISIONS.md`, `knowledge/DOMAIN_RULES.md`.
- Compat-register entry `LK-COMPAT-QUERY-SHIM-001.yaml` at
  `status: proposed`, disclosing all six behaviour changes in its
  `reason:` field — explicitly not promoted further.
- `ROADMAP.md`/`CHANGELOG.md`/`CONTEXT.md` updated per the standing
  rules; Stage C itself is **not** marked `[DONE]` (not this session's
  call) and this phase is not marked `[DONE]` either — only "approved
  and implemented, independent verification pending," matching the
  language this project already uses for Phase 6/7's own equivalent
  implementation-complete-but-not-independently-verified state.

No scope was added or dropped relative to the design. One place needed
a small implementation-level judgment call not fully dictated by the
design's literal code (see "Lessons learnt" below), and one existing
test class (`TestPostingMatches`, direct unit tests of the now-deleted
`_posting_matches` function) was removed rather than kept as dead
weight, with its coverage intent redistributed across the new
`tests/test_query/test_compat.py` and several new integration test
classes in `tests/test_reports.py`.

## What was achieved

- `_posting_matches` has zero remaining callers anywhere in `ledgerkit/`
  — confirmed both by grep (no `_posting_matches(` call syntax and no
  `import _posting_matches` anywhere) and by a dedicated static test
  (`TestPostingMatchesRetired`).
- All seven consumers named in the design's §5.3 converge exactly as
  specified — verified individually rather than assumed:
  1. `reports.balance` — `_query_to_ast(query)` → `matches_posting`,
     AND'd with any `_query_ast`.
  2. `reports.register` — same pattern.
  3. `reports.accounts` — same pattern (its own narrower
     `_matches_posting_for_accounts` dispatch for `_query_ast`'s `Tag`
     nodes is untouched, unrelated to this phase).
  4. `reports.stats` — `_query_to_ast(query)` → `matches_transaction`,
     AND'd with any `_query_ast`; this is genuinely new behaviour
     (`account`/`not_account` were previously silently ignored).
  5. `reports.balance_from_spec` — outer query via `_query_to_ast` +
     `matches_posting`; `ReportSection.accounts`/`.exclude` via the
     refactored `_matches_pattern`.
  6. `Journal.to_dataframe` — migrated off `_posting_matches` onto the
     same `_query_to_ast` + `matches_posting` path.
  7. The deprecated `accounts=[...]` shim — zero accounts is explicit
     "no filter" (never `Or(())`); one account is an unchanged raw
     regex passthrough; two-or-more builds `Or(Acct(...), ...)` directly,
     bypassing `Query` entirely.
- Eager validation confirmed with dedicated tests against an *empty*
  journal for every converged consumer (`balance`/`register`/`accounts`/
  `stats`/`to_dataframe`/`balance_from_spec`) — an invalid `Query` field
  raises `QueryParseError` deterministically at translation time, never
  only if and when a posting happens to be evaluated.
- The `datetime.date.max` overflow case has its own dedicated tests
  (both at the `_exclusive_end`/`_query_to_ast` unit level and via
  `matches_transaction` against a transaction dated exactly
  `date.max`).
- Full test suite: 897 tests (up from 844), all passing, 29 skipped
  (pandas-optional, up from 24 — the 5 new skips are the new
  `to_dataframe` convergence tests, correctly skipped in this
  pandas-less environment rather than silently not existing).

## What worked

- Building the actual per-consumer inventory myself before writing any
  code (re-deriving §5.3's table by reading `models.py`/`reports.py`
  directly, not trusting the design's own table on faith) caught nothing
  new — the design's own two amendment passes had already done this work
  thoroughly — but doing it anyway was cheap insurance and matched the
  design's own explicit instruction not to trust prior completeness
  claims blindly.
- Writing the eager-validation-against-an-empty-journal tests forced a
  genuine check of *where* each function calls `_query_to_ast` relative
  to its main loop — confirming it happens before any loop, not inside
  one, for every converged consumer. This is exactly the kind of thing
  that's easy to get subtly wrong (e.g. accidentally leaving the
  translation call inside a conditional or a loop) and easy to miss in
  review without a test that specifically targets it.
- The design's own worked-through illustrative code for §5.1a/§5.1b/
  §5.1c/§5.1d was close enough to drop in with only mechanical
  adaptation (matching existing docstring style, choosing where to place
  the lazy import) — a design this literal measurably lowered
  implementation risk and review burden.

## What didn't work

- No significant misfires this phase. The one friction point: the `Edit`
  tool's exact-string-match requirement failed twice on
  `dev-docs/api-spec.md`/`dev-docs/architecture.md` edits despite the
  text appearing identical on screen — resolved by falling back to a
  small Python script doing an exact `str.replace`, which is more
  robust to invisible formatting differences (line-wrap boundaries in
  particular) than eyeballing a large `Read` output and re-typing it.
  Not a design or implementation problem, just a tooling note for next
  time: prefer reading the exact target region immediately before
  editing it, in small chunks, rather than from a large earlier read.

## Lessons learnt

- "Zero remaining callers" is worth testing statically (grep-based), not
  just "existing tests still pass" — a stale but unused import would
  pass every behavioural test while still being wrong. The design named
  this explicitly as a required test, and it was worth the extra
  scaffolding (walking the package directory rather than a one-line
  `hasattr` check) to make the assertion genuinely load-bearing against
  future regressions, not just against the current diff.
- When a design explicitly resolves a fork (here, five separate items in
  §12), the fastest and safest implementation path is to treat each one
  as literally closed — no re-deriving "but what if Option B were
  actually better here" — and spend the implementation session's actual
  judgment budget on the handful of genuine gaps the design leaves open
  (module-internal choices like whether `_matches_pattern`'s own
  exception should be wrapped in `QueryParseError`, which the design
  scopes to `Query`/the deprecated shim specifically, not to
  `ReportSection`). Recording those small gap-filling calls in
  `knowledge/DECISIONS.md` immediately, rather than letting them go
  unrecorded, is exactly the ambiguity-handling convention doing its
  job.

## Process-improvement feedback

No process gaps found this phase. The design document's own
completeness (literal illustrative code for every case, an explicit
approval gate with recommendations already stated) meant this
implementation session had very little to interpret — which is the
intended effect of the multi-round design-review process this project
uses for substantial features, and it worked as intended here.

## Learnings filed

- `knowledge/DECISIONS.md`: a new entry (2026-09-26, "`Query`-as-
  compatibility-shim convergence (Stage C Phase 8): Option A, and the
  corrected blast-radius conclusion") covering the Option A choice, the
  corrected blast-radius conclusion, the module-placement rationale, the
  `accounts=[...]` shim's `Or`-based fix including the zero-accounts bug,
  the `balance_from_spec` outer-query convergence decision, and two
  implementer judgment calls (deleting `_posting_matches` outright;
  not wrapping `_matches_pattern`'s own exception in `QueryParseError`).
- `knowledge/DOMAIN_RULES.md`: the existing `Query.date_to`/`DateSpan.end`
  entry was updated in place (not a dated, append-only record like a
  retro) to describe the now-solved translation and its `date.max`
  overflow edge case, since this entry is living reference documentation
  about a still-true tacit rule, not a historical log entry.

## Where we're going

Stage C's remaining named item is the `PythonRegex` extension syntax
(`07-query-regex.md` §7.4) — explicit resolution (implement, defer with
a stated reason, or drop) was already named as Stage C Phase 6's backlog
item 3, still open. The immediate next step for *this* phase, not for a
future one, is independent verification: a genuinely separate
`compat-differential-tester` dispatch must re-run the differential
comparisons this design's own §11 lists (mandatory before any
compat-register promotion past `status: proposed`), followed by
`docs-maintainer`/`docs-reconstructor` drift audits and
`release-phase-auditor`'s Definition-of-Done check, per this project's
standing per-phase cadence. This phase's own outcome does not change the
planned trajectory — it executes the design as approved, with no new
findings that would reshape a later Stage.

## Time / cost note

Single-session implementation, no false starts on the core design
(module placement, the seven-consumer convergence, the shim's three
cases) — the two prior design-amendment passes had already absorbed the
real cost of getting this right. Most of the session's effort went into
test breadth (translator unit tests, per-consumer integration tests
covering both the "still works for valid input" and "now raises for
invalid input" halves of Option A) and documentation sync across five
files, not into resolving implementation uncertainty.

## Addendum (2026-09-26, same day) — independent verification, no discrepancies

A genuinely separate `compat-differential-tester` dispatch (Step 7,
`09-compatibility-system.md` §9.6) independently re-checked all eight
of the design's own highest-risk claims on a fresh fixture (`tests/
fixtures/query_shim_differential.journal`), with no access to this
implementation session's own conversation: `Query`-vs-`-q` parity for
`balance`/`register`/`accounts` (including identical rejection of an
excluded construct and an empty pattern); `stats(query=...)`'s genuinely
new account/not_account narrowing (unfiltered 6/6 vs. filtered 3/2,
matching `-q "acct:food" stats` exactly); `balance_from_spec`'s outer-
query strictness and `ReportSection.accounts`/`.exclude`'s independent
`HledgerRegex` validation; `Journal.to_dataframe`'s eager validation
against an empty journal; and, most importantly, the deprecated
`accounts=[...]` shim's all-three-cases fix — `accounts=[]` confirmed
identical to no filter at all (not `Or(())`), one account unchanged,
two-plus accounts OR-matching without raising, spot-checked further
with account names containing literal regex metacharacters. The
`date.max` edge case and the ordinary inclusive-`date_to` case were both
independently confirmed correct. Full 897-test suite re-run twice,
matching this session's own count.

**No discrepancies found.** `LK-COMPAT-QUERY-SHIM-001` promoted from
`status: proposed` to `status: verified` by the independent dispatch
itself (the only role authorised to do so), with a new evidence entry
citing its own fixture, commands, and results. No `unexplained_
mismatch` entries were needed. This phase is now implementation-and-
verification-complete; `[DONE]` remains the user's own call.

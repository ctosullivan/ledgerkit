<!-- dev-docs/retros/<STAGE-OR-MILESTONE>[-PHASE-K].md — authored by Claude
at phase end (see README.md for naming: no -PHASE-K suffix when the whole
Milestone/Stage was one phase). A few lines is fine for a trivial phase. -->

# Stage C Phase 9 retro — empty-alternation-branch regex implementation

- **Date:** 2026-09-27
- **Commit(s):** `60eea4a` (feat: implementation + tests)
- **Agents used:** none — implemented directly by the coding agent dispatched
  per the design's own "doubles as its own implementation plan" precedent;
  no `compat-differential-tester`/`docs-reconstructor`/`release-phase-
  auditor` dispatched yet (independent verification is the mandatory next
  step, explicitly not performed here).

## Where we are

Stage C's query-language work (Phases 1-8) is implementation-and-
verification-complete; this phase resolves the last item on Stage C
Phase 6's own backlog, `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`. The
previous phase (Phase 9's own planning pass, retro `STAGE-C-PHASE-9-
EMPTY-ALTERNATION-PLAN.md`) produced a fully-specified design document
(`28-empty-alternation-regex-design.md`) with a hand-verified detection
algorithm, explicitly written to double as its own implementation plan
— this phase turned that design directly into code, tests, and docs.
After this phase, Ledgerkit's `validate_hledger_regex` rejects the full
18-pattern empty-alternation-branch family the same way real hledger's
regex-tdfa engine does, with 13 regression-guard accept cases confirmed
unaffected. Stage C itself remains `[IN PROGRESS]` — this phase's own
completion does not imply Stage-level completion, and the mandatory
independent-verification step has not yet run.

## Goal

Implement `28-empty-alternation-regex-design.md`'s fully-specified fix:
a new `_has_empty_alternation_branch` detection function in `ledgerkit/
query/regex.py`, wired into `validate_hledger_regex`; the full 18+13
test matrix plus integration tests; the compat-register resolution
lifecycle's new entry (`status: proposed` only); and every doc-sync
obligation the design's §6 named.

## Scope delivered vs planned

Delivered exactly what the design specified, no more, no less:

- `_has_empty_alternation_branch(pattern: str) -> bool` — copied from
  the design's §3.1, independently re-verified against all 31 patterns
  (18 reject + 13 accept) before trusting it, not blindly copied.
- Wired into `validate_hledger_regex` alongside (not replacing) the
  existing `pattern == ""` check and `_EXCLUDED_CONSTRUCT` scan.
  `_EXCLUDED_CONSTRUCT` itself untouched, per the design's explicit
  non-goal and this phase's own hard constraint.
- 36 new tests: 18 must-reject + 13 must-accept unit tests (each its
  own named test, matching the project's established matrix-testing
  convention), 4 parser-level integration tests (`acct:a|`, `desc:(|)`,
  `tag:rate=a|`, `depth:a|=2`), 1 CLI-level integration test
  (`-q "acct:a|"` exits 1 with the existing "invalid query" message).
- New compat-register entry `LK-COMPAT-QUERY-REGEX-EMPTYALT-001`
  (`kind: compatible`, `resolves: LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`,
  `status: proposed` — explicitly NOT self-promoted further, per this
  phase's hard constraint). The original mismatch entry left completely
  untouched, per the same constraint — no `resolved_into`/`resolved_date`
  added yet; that is the next phase's job, gated on independent
  verification.
- Doc sync: `dev-docs/hledger-compatibility.md` (regex-dialect note +
  the `tag:` row's cross-reference corrected), `dev-docs/api-spec.md`
  (`validate_hledger_regex`'s docstring, no signature change),
  `knowledge/DOMAIN_RULES.md` (the exact adjacency rule, framed as
  genuinely non-obvious and undocumented in hledger's own manual),
  `knowledge/DECISIONS.md` (why a dedicated scan was chosen over
  extending `_EXCLUDED_CONSTRUCT`'s single regex).

Nothing was dropped or deferred beyond what the design itself scoped
out (differential verification, `resolved_into` on the mismatch entry,
`UNEXPLAINED.md` table migration — all explicitly the next phase's job).

## What was achieved

Real hledger and Ledgerkit now agree, at the unit-test level, on the
full empty-alternation-branch family: `(|)`, `a|`, `|a`, `(a|)`, `(|a)`,
`a||b`, `(a|)|b`, `||`, `|`, `(|)|c`, `a|(|b)`, `(||)`, `a|||b`,
`(|)*`, `(a)|`, `|(a)`, `a(|)b`, `(a|)(b)` all now raise
`QueryParseError` end-to-end (parser + CLI), matching real hledger's
regex-tdfa rejection; `()`, `(a)`, `a|b`, `(a|b)`, `()|a`, `a|()`,
`()*`, `a| |b`, `^|a`, `a|$`, `a\|\|b`, `\(|a`, `a|\)` remain accepted,
unaffected. 935 tests pass (up from 899, +36).

## What worked

- **Hand-verifying the design's algorithm with a throwaway script before
  trusting it** — ran the exact algorithm from §3.1 against all 31
  patterns in a standalone Python script before copying it into
  `ledgerkit/query/regex.py`. Caught nothing (the algorithm was
  correct as written), but this is exactly the kind of check that would
  have caught a bug cheaply if one existed, rather than discovering it
  via a failing test after the fact.
- **The design doubling as the implementation plan, again** — the
  precedent from Phase 7 held up a second time: a fully-specified design
  with a validated algorithm meant zero design decisions were needed
  during implementation, just faithful transcription plus test-writing.
- **The existing test-file conventions made the 31-pattern matrix
  mechanical to write** — `TestEmptyPattern`/`TestEmptyMatchingPatterns
  RemainAccepted`'s established one-test-per-pattern style meant no new
  convention needed inventing; the new `TestEmptyAlternationBranch
  Rejected`/`Accepted` classes just followed the existing shape.

## What didn't work

No misfires this phase — a smooth, mechanical implementation of an
already-fully-specified design. The one thing worth flagging as
friction rather than failure: the design's own worked-out algorithm
needed adapting slightly for the project's Regex Documentation Rule,
since that rule's template assumes an actual `re.compile()` pattern
with capture groups ("Group breakdown" by index) — this function has
neither, so the comment substitutes an "Algorithm" section for "Group
breakdown," which the task's own instructions anticipated and permitted
("adapt as needed").

## Lessons learnt

A fully-specified, hand-verified design document is a genuinely reliable
handoff artifact for this project's process — but "hand-verified" in a
design document is still worth an independent re-verification pass
during implementation, even when it turns out unnecessary (as it did
here): the cost of running a 31-line verification script is trivial
next to the cost of silently shipping a subtly wrong detection rule that
happens to pass its own hand-picked examples but fails on some
untested pattern shape. Cheap verification of "already verified" claims
is worth doing on principle, not just when experience says the previous
verification is suspect.

## Process-improvement feedback

No process notes this phase — the design → plan-doubles-as-implementation
→ code+tests+docs → (pending) independent verification pipeline worked
exactly as intended, second time in a row (Phase 7 was the first).

## Learnings filed

- `knowledge/DOMAIN_RULES.md` — new entry: the exact empty-alternation-
  branch adjacency rule, its escape-awareness requirement, and why `()`
  is accepted while `(|)` is not (the ERE-grammar-level distinction
  between a group's own empty-content production and the alternation
  production's lack of one).
- `knowledge/DECISIONS.md` — new entry: why a dedicated escape-aware
  scanning function was chosen over extending `_EXCLUDED_CONSTRUCT`'s
  single compiled regex (Python `re`'s fixed-width-lookbehind
  limitation cannot express variable-length backslash-run parity), and
  why `_EXCLUDED_CONSTRUCT`'s own existing false-positive tolerance
  (documented for its backreference branch) was deliberately not reused
  for this construct.

## Where we're going

Next, and mandatory before this phase's compat-register entry can move
past `status: proposed`: a genuinely separate `compat-differential-
tester` dispatch, re-running the full 18+13-pattern matrix against the
real pinned hledger 1.52.4 binary and Ledgerkit's post-fix behaviour.
Only after that independent confirmation can `LK-MISMATCH-QUERY-REGEX-
EMPTYALT-001` itself receive its `resolved_into`/`resolved_date` fields
and move to `UNEXPLAINED.md`'s "Resolved entries" table, and only then
does `LK-COMPAT-QUERY-REGEX-EMPTYALT-001` promote to `status: verified`.
After that, this being the last item on Stage C Phase 6's own backlog,
the full Stage C completion audit sequence the user has already
described (compat-register review, `docs-maintainer`, a Stage-C-wide
`docs-reconstructor` NO-DRIFT pass, roadmap/knowledge reconciliation, a
Stage-C-wide `release-phase-auditor` pass against every exit criterion,
and a Stage C closeout retro) is the path to determining whether Stage
C's own Definition of Done is met — not this phase's own retro to
determine.

## Time / cost note

Single-session implementation: reading the design + compat-register
evidence, independently verifying the algorithm, implementing the
function and wiring, writing 36 tests, and syncing five documentation
surfaces plus the compat-register and retro. No rework, no design
deviation — the fully-specified design kept this phase's own scope
tight and predictable.

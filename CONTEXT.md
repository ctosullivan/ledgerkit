# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 7 (empty-regex-pattern rejection, resolving `LK-MISMATCH-
QUERY-TAG-EMPTYVALUE-001`) — **design document written, stopped for
explicit human approval.** No `ledgerkit/`/`tests/` code touched. Phase
6 is `[DONE]`; this is the next phase, per its own closeout
recommendation.

## Where We Are
Design document: `dev-docs/planning/core-redefinition/26-query-regex-
empty-pattern-design.md`. Backing research: `25-query-regex-empty-
pattern-matrix.md` (independent `compat-differential-tester` live-binary
matrix). Planning retro: `dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-
PLAN.md`. `ROADMAP.md`/`CHANGELOG.md` updated for the planning
checkpoint. About to commit + push, then wait — do NOT proceed to
implementation until explicit approval arrives.

## Decisions In Flight
Design §11's four-item approval gate, all open:
1. Approve the fix: a `pattern == ""` check in `ledgerkit/query/
   regex.py`'s `validate_hledger_regex`, raising the existing public
   `UnsupportedRegexConstructError` (no new exception class, no
   `api-spec.md` change).
2. Approve the exact error-message wording proposed in design §5 (or
   amend it).
3. Confirm non-goals: the empty-alternation-branch family (`(|)`,
   `a|`, `|a`, `(a|)`, `(|a)`) and any broader "semantically admits
   empty" check are explicitly OUT of this fix.
4. General approval to proceed — likely no separate implementation-plan
   document needed given the fix's small size (design's own §5/§10
   may suffice), implementer's call to flag if it disagrees.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-
  design.md` — the design document awaiting approval.
- `dev-docs/planning/core-redefinition/25-query-regex-empty-pattern-
  matrix.md` — the live-binary evidence backing it.
- `ledgerkit/query/regex.py` — `validate_hledger_regex`, the single
  proposed change site.
- `ledgerkit/query/parser.py:230-245` (`_build_tag`) — already
  distinguishes bare `tag:NAME` from `tag:NAME=` via `partition("=")`'s
  `sep` flag; no changes needed here, confirmed by direct read.
- `tests/test_query/test_regex.py` — exists already, is where the new
  unit test belongs (confirmed, matches the design's own proposal).
- `tests/test_query/test_parser.py::test_empty_value_pattern_is_not_
  none` — the one existing test that will need rewriting (currently
  asserts the behaviour being corrected).

## Blockers / Open Questions
The four-item approval gate above. Nothing else blocking.

## What NOT To Revisit
- Don't re-derive the empty-string-vs-empty-matching scoping question —
  settled executably: hledger rejects only the literal empty string;
  `.*`/`a*`/`^$`/`()` are all accepted. Don't propose a broader
  "does this pattern's semantics admit empty" check.
- Don't propose per-call-site changes to `_build_acct`/`_build_desc`/
  `_build_depth_spec`/`_build_tag` — confirmed unnecessary; one check
  in the shared `validate_hledger_regex` covers all four automatically.
- Don't propose a new exception class — `UnsupportedRegexConstructError`
  already exists, is already public, and already fits.
- Don't fold the empty-alternation-branch family (`(|)` etc.) into this
  fix — confirmed as a separate, unrelated hledger rejection cause;
  explicitly out of scope, noted for a possible future item instead.
- Don't use `context-curator` for general hledger/source research again
  — its actual charter (per `.claude/agents/context-curator.md`) is
  narrowly "judge CodeCompass's usefulness." Route live-binary research
  to `compat-differential-tester`, manual/source-only research to
  `hledger-researcher`, and Ledgerkit-internal source auditing to the
  lead directly.

## Recent Git State (before this response's commit)
a49ac50 docs: close out Stage C Phase 6, mark [DONE]
5887ea8 docs: close out Stage C Phase 6 independent verification
fe9dfe5 test: independently verify Stage C Phase 6 tag: compat-register entries
cb06d1f docs: update CONTEXT.md for Stage C Phase 6 implementation end state
fa05bbc test: add tag: integration tests, compat-register entries, retro

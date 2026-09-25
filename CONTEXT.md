# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:NAME[=REGEX]` query-term matching) — **implementation
and independent verification both complete.** Design approved by the
user (Option A, `accounts`-mode replication); implemented by a fresh
coding agent (Step 6); independently re-verified against the pinned
hledger binary by a genuinely separate `compat-differential-tester`
dispatch (Step 7). One real, pre-existing (not phase-caused) divergence
found and filed, not fixed. `[DONE]` for the phase is the user's own
call to make, not inferred here.

## Where We Are
Everything committed and pushed to `main`:
- `0523426` — core implementation, unit tests, doc sync
- `fa05bbc` — integration tests, compat-register entries (`status:
  proposed`), implementation retro
- `cb06d1f` — `CONTEXT.md` end-state update (implementer's own)
- `fe9dfe5` — independent verification: 5/6 compat-register entries
  promoted to `verified`, one mismatch filed, `dev-docs/hledger-
  compatibility.md` updated, retro addendum appended
- Docs/roadmap closeout for the verification step (this response):
  `ROADMAP.md`, `CHANGELOG.md`, this file — about to be committed.

827 tests passing throughout (up from 746 before this phase).

## Decisions In Flight
None blocking. Two things await a human call, neither urgent:
- Whether/when to mark Stage C Phase 6 `[DONE]` in `ROADMAP.md` — user's
  own call per the project's standing rule, not inferred by Claude.
- Whether to fix `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` (empty-regex
  pattern acceptance divergence, affects `acct:`/`desc:`/`tag:` alike,
  root cause `ledgerkit.query.regex.compile_hledger_regex`) — unscoped,
  not part of this phase, no design/plan exists for it yet.

## Files Currently Relevant
- `dev-docs/compat-register/LK-COMPAT-QUERY-TAG-*.yaml`,
  `LK-COMPAT-PARSER-TAG-COMMODITY-001.yaml` — 5 now `status: verified`.
- `dev-docs/compat-register/LK-COMPAT-QUERY-TAG-001.yaml` — still
  `status: proposed`; its `tag:NAME=` empty-value claim is false, every
  other claim in it verified.
- `dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml` —
  new, `status: verified` (the mismatch itself is confirmed real; no
  fix proposed here).
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` —
  implementation retro + verification addendum, both dated 2026-09-25.
- `dev-docs/hledger-compatibility.md` — `tag:`/`accounts tag:X` rows,
  now cite `verified` status and the empty-regex caveat.
- `ledgerkit/query/regex.py` (or wherever `compile_hledger_regex` lives
  — check before assuming a path) — the eventual fix site if the
  empty-regex divergence is ever taken up.

## Blockers / Open Questions
None blocking further work on this phase — it's complete. The two
items in "Decisions In Flight" are open but not blockers.

## What NOT To Revisit
- Don't re-derive the no-shadowing/union precedence finding — now
  confirmed independently twice (design-time executable testing, then
  a separate verification dispatch). Settled.
- Don't re-derive the `accounts` four-way visibility split — same,
  confirmed independently twice.
- Don't treat `LK-COMPAT-QUERY-TAG-001`'s `status: proposed` as
  something this phase failed to finish — it's a deliberate, honest
  "not verified" for one specific false claim, not an oversight. Do NOT
  quietly edit its `reason:` text to remove the false claim and
  promote it to `verified` — the correct fix is either implementing the
  empty-regex rejection in Ledgerkit (a code change, its own scoped
  work) or leaving the entry exactly as it stands.
- Don't fix `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` unilaterally — it's
  real, but it's a pre-existing, cross-cutting issue (not `tag:`-
  specific) outside this phase's approved scope. Surface it, don't
  silently absorb it into this phase's work.
- Don't re-run context-curator or redesign any part of this feature —
  design, implementation, and verification are all done.

## Recent Git State
fe9dfe5 test: independently verify Stage C Phase 6 tag: compat-register entries
cb06d1f docs: update CONTEXT.md for Stage C Phase 6 implementation end state
fa05bbc test: add tag: integration tests, compat-register entries, retro
0523426 feat: implement tag:NAME[=REGEX] query matching (Stage C Phase 6)
0849690 docs: small final correction pass on Stage C Phase 6 tag: design

# Stage C Phase 9 retro — Planning (empty-alternation-branch regex rejection)

- **Date:** 2026-09-27
- **Commit(s):** see `git log` for this retro's own commit.
- **Agents used:** `compat-differential-tester` (fresh re-verification
  of the mismatch from source and live pinned hledger, per explicit
  instruction not to trust the entry's prior 2026-09-25 notes as still
  current).

## Where we are

Part of Stage C's own closeout task: with Phases 1-8 done, the last
substantive backlog item is `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` (the
empty-alternation-branch regex divergence, first found as a side
observation during Stage C Phase 7's own empty-pattern-string research
and deliberately left unfixed then, per that phase's own explicit
scope discipline). This retro covers Steps 1-2 (fresh re-verification,
design) of this project's standing process for that item.

## Goal

Re-establish the exact mismatch from source/live pinned hledger rather
than trusting prior notes (which predate Stage C Phase 7's own code
changes to `ledgerkit/query/regex.py`); scope the smallest correct fix;
produce a design specifying it precisely enough to implement directly.

## What was achieved

The re-verification did more than confirm the prior notes — it found
they were **incomplete in two ways**: (1) the original filing verified
only `(|)` on Ledgerkit's own side, leaving `a|`/`|a`/`(a|)`/`(|a)`
explicitly unverified; this pass confirmed all five, plus 13 further
generalised patterns (18 total confirmed-divergent). (2) The original
filing's own framing ("two different error-message formats" for the
empty-pattern-string case vs. this family) was itself wrong — direct
source reading of hledger's `Regex.hs`/`Query.hs` found there is only
**one** error-formatting code path; the apparent difference is just
what happens when the interpolated pattern string is empty.

The resulting rule is unexpectedly simple given the size of the
divergence: a purely local, single-character-adjacency, escape-aware
check (§3.1 of the design) — no nesting-depth tracking needed at all,
because a nested group's own internal emptiness is always caught by
that group's own `|` against its own immediate neighbours. This was
verified by hand against all 18 must-reject patterns and all 13
must-not-reject patterns (including three escape-aware control cases)
before being written into the design, not merely asserted.

## What worked

- **Insisting on re-verification instead of trusting a several-day-old
  filing** — the filing's own code had changed underneath it (Stage C
  Phase 7 landed in between), and its own scope claims were genuinely
  incomplete. A design built on the stale notes would have under-scoped
  the fix (missing 13 of 18 divergent patterns) and mischaracterised
  the error-format finding.
- **Deriving the algorithm from the full matrix by hand, case by case,
  before writing it into the design** — this caught, during the design-
  writing process itself, that a naive "any `|` next to `(`/`)`/`|`"
  scan would need explicit escape-awareness or it would wrongly reject
  `a\|\|b`/`\(|a`/`a|\)`, all of which must stay accepted. Verifying
  every one of the 31 test cases against the proposed algorithm before
  finalising it (rather than after implementation surfaces a failure)
  moved that verification cost to the cheapest possible point.

## What didn't work

No misfires this phase.

## Lessons learnt

- A compat-register entry's own prior evidence should be treated as a
  starting hypothesis, not a settled fact, whenever the code it
  describes has changed since — "re-verify from source, not from
  notes" is not just a formality here, it materially changed the
  scope (5 patterns → 18) and corrected a real factual error (two
  error formats → one).
- For an escape-sensitive lexical rule, hand-verifying a proposed
  algorithm against the complete positive-and-negative test matrix
  before writing any implementation code is cheap insurance against a
  subtly-wrong regex or scan showing up only after a fresh coding
  agent has already implemented and tested it.

## Process-improvement feedback

No process notes this phase.

## Learnings filed

Deferred to implementation time, per this project's standing sequencing
(learnings land with the code they document).

## Where we're going

Design (`28-empty-alternation-regex-design.md`) doubles as its own
implementation plan, per this project's established precedent for a
fully-specified small fix (Stage C Phase 7). Next: a fresh coding-agent
implementation, tests, and independent differential verification — all
explicitly authorized to proceed as part of the same Stage C closeout
task, not gated on a separate human approval round.

## Time / cost note

One `compat-differential-tester` re-verification dispatch (thorough —
35+ live pattern checks across three query prefixes, plus a local
hledger source read for the root cause) and direct lead-performed
design writing, including hand-verifying the proposed algorithm against
every test case before finalising it.

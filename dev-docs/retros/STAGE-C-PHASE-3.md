# Stage C Phase 3 retro — Wire `-q`/`--query` into `print`

- **Date:** 2026-09-17
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — small, well-scoped extension of an already-
  proven pattern; no agent dispatch warranted

## Where we are

Stage C Phase 2 wired `-q`/`--query` into `balance`/`register`/
`accounts`/`stats` and left `print` as the named, smallest, cleanest next
step in its own retro. This phase does exactly that: `print` now accepts
`-q`, filtering transactions via `ledgerkit.query.eval.matches_transaction`
directly in `cli.py` (since `print` has no `reports.py` function of its
own to carry a `_query_ast` parameter). After this phase: all five report/
display CLI commands (`balance`/`register`/`accounts`/`stats`/`print`)
accept `-q`; only `check` (by design — checks apply to the whole journal)
does not.

## Goal

Wire `-q`/`--query` into the `print` command, following the same private,
internal-only integration pattern Phase 2 established, and differentially
verify it against the pinned hledger binary.

## Scope delivered vs planned

Delivered exactly as scoped — no term-language expansion, no `Query`-as-
shim work, no other command touched. One design question resolved during
implementation, not pre-decided: whether a matching transaction should
show only its matching posting(s) or the whole transaction. Resolved by
checking hledger's own actual behaviour directly (`print depth:1`,
`print acct:food`) rather than assuming — hledger always shows the whole
transaction, which is what this phase implements.

## What was achieved

`print -q` works identically to hledger's `print` with the same query,
for every term family already implemented (`acct:`, `not:`, `status:`,
implicitly `date:`/`desc:`/`depth:` since they share the same
`matches_transaction` evaluator already verified in Phase 2). 5 new
tests, 684 total, all passing. A new compat-register entry
(`LK-COMPAT-QUERY-PRINT-INTEGRATION-001`) records the whole-transaction
display behaviour as differentially verified, not assumed.

## What worked

- **Checking hledger's actual `print` behaviour before assuming
  "filter like the others."** `print` has no aggregation concept the way
  `balance` does, so it would have been easy to assume it just filters
  postings the way `register` effectively does — checking directly showed
  it doesn't: it filters *transactions*, then shows them whole. Getting
  this right the first time avoided a repeat of Phase 2's "found the gap
  via differential testing after implementing it wrong" pattern.
- **Reusing `matches_transaction` directly in `cli.py`** rather than
  inventing a `reports.py`-adjacent home for `print`'s filtering (`print`
  has no `reports.py` function at all — it iterates `journal.transactions`
  directly) — no new abstraction needed, the existing evaluator slotted
  in cleanly.

## What didn't work

Nothing failed this phase. This time, the differential testing was done
directly by the lead again — but for a phase this small and low-risk
(reusing an already-proven pattern and an already-verified evaluator, not
introducing new semantics), that's a reasonable proportionality call
rather than the same process gap Phase 2's retro flagged: Phase 2's gap
was skipping a *designed-in* separate-agent-dispatch role for a
first-of-its-kind CodeCompass evaluation; this phase never had such a
role to skip in the first place.

## Lessons learnt

When a new CLI surface reuses an already-proven integration pattern, the
one thing still worth checking fresh — not assuming from the pattern
alone — is whether the *new* surface's own semantics (here: does `print`
filter individual postings or whole transactions?) actually match the
already-implemented evaluator's assumptions, rather than assuming
"reuse the pattern" implies "reuse it identically everywhere."

## Process-improvement feedback

No friction. The retro→next-phase pipeline worked as designed: Phase 2's
retro named this exact task, with a stated reason ("smallest, cleanest
next step, integration pattern already proven"), and it turned out to be
accurate — no rescoping was needed once work started.

## Learnings filed

- `dev-docs/compat-register/LK-COMPAT-QUERY-PRINT-INTEGRATION-001.yaml` —
  new entry, `status: verified` from the start (differential-tested
  during implementation, not proposed-then-deferred).

## Where we're going

Stage C's remaining named candidates (from Phase 2's retro): `tag:`/
`cur:` term extension (read CodeCompass's own Phase 54 reference-material
experiment first — a real, caught extraction-accuracy defect in
`tag:`-adjacent material), and the larger `Query`-as-compatibility-shim
migration (`07-query-regex.md` §6.5). Neither started; both still need
their own explicit scoping before work begins. This phase confirmed the
established integration pattern generalises cleanly to a second CLI
command — no finding here reshapes Stage C's remaining plan.

## Time / cost note

Single response: implementation + differential verification + tests +
docs + compat-register entry. No unusually long step.

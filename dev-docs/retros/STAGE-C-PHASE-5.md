# Stage C Phase 5 retro — Verification independence + `depth:` redesign

- **Date:** 2026-09-17
- **Commit(s):** `17d7bcb` (process amendment), `e8f3633` (depth
  redesign), this retro's own commit (independent verification +
  closeout)
- **Agents used:** one `compat-differential-tester` dispatch —
  genuinely separate from the implementing session, verifying three
  register entries independently. This is itself the phase's own
  headline deliverable being exercised for real, not a formality.

## Where we are

The planning pass (`STAGE-C-PHASE-5-PLAN.md`) identified two issues in
recent Stage C work and produced a plan with six human-decision gates.
The user approved all six ("proceed as recommended"), with G-DEPTH-4
(standalone `--depth` CLI flag) left to the lead's judgement since the
plan itself gave no recommendation there — resolved to "defer" to keep
the phase's diff focused on the actual defect. This phase is the
implementation: the process amendment, the `depth:` redesign, and —
critically — actually using the new process on the work this same phase
produced, rather than letting it wait for a future phase to be the first
real test.

## Goal

Implement both halves of the approved plan: a claim-strength-tiered
verification-independence process, and a `depth:` semantic model that
matches hledger's real, source-confirmed behaviour rather than diverging
from it — then apply the new process to this phase's own new
compatibility claims before calling it done.

## Scope delivered vs planned

All four `depth:` gates and both process gates implemented as approved.
One scope question the plan didn't anticipate at all, found only during
implementation: hledger's `stats` command turned out to have its own
genuine exclusion-based depth quirk (confirmed via `Ledger.hs`'s
`ledgerFromJournal` doc-comment and two independent live scenarios) —
not part of the plan's differential-test matrix, which assumed `stats`
would follow the same clip-not-exclude rule as everything else. This was
resolved in-phase (replicated exactly, given a dedicated compat-register
entry) rather than deferred, since it directly concerns the same feature
area under active work.

Two further pre-existing bugs were found and fixed, neither scoped by
the plan: `register()`/`accounts()` had silently applied the legacy
`Query.depth` as an exclusion filter too (the plan's own current-state
assessment only checked `balance()`, which was the one case already
correct — a real, narrower miss in the planning pass's own research,
corrected here rather than left for later). Also fixed: a `balance`
CLI-formatting edge case (`--depth 0`'s single `...` row, guaranteed to
net to zero for any balanced journal, was being silently elided by a
pre-existing "omit zero rows" heuristic that had never before been
reachable at this code path).

## What was achieved

`ledgerkit.query.ast.Depth` removed from the selection-predicate AST
entirely; `ledgerkit.query.depth.DepthSpec` (new module) implements
hledger's exact clip/aggregate semantics including custom `REGEX=N`
precedence and multi-term MIN-combination (order-independent, verified
distinct from CLI-flag "last wins," which Ledgerkit doesn't have a flag
for). `parser.parse()`'s return type changed from `QueryNode` to
`QueryPlan` (predicate + depth, matching the target architecture
exactly). `print` fixed to correctly ignore `depth:` entirely. Old
boolean predicate kept as `MaxAccountLevel`, Python-API-only, no `-q`
string collision. 21 new/rewritten tests — 746 total, all passing.
`09-compatibility-system.md` §9.6 amended with the tiered process and a
new `status: self-verified` value; 11 existing entries relabelled
honestly. A genuinely separate `compat-differential-tester` dispatch
independently re-verified all three new/changed depth-related register
entries against the pinned binary on a newly-built fixture
(`tests/fixtures/depth.journal`) before any were promoted to `status:
verified` — no mismatches found.

## What worked

- **Tracing every real command's `Query` consumption, not stopping at
  the `Depth` constructor's own function body.** This is the exact
  mistake Stage C Phase 1 made (and the plan's own retro named as a
  generalisable lesson); this phase's implementation deliberately
  re-verified the plan's own source claims by re-reading the same six
  files rather than trusting the planning pass's summary of them —
  cheap insurance that paid off when the `stats` exception surfaced.
- **Building a real fixture with a deliberate regex-collision case**
  (twice — once in the planning pass's own scratch fixture, once
  properly committed by the independent verifier) specifically to
  reproduce the manual's own worked precedence example against the real
  binary, rather than trusting prose. It reproduced exactly as
  documented both times, by two different sessions.
- **Actually dispatching the agent this phase's own process requires**,
  rather than self-verifying "just this once" under the pull described
  in Phase 2's retro ("a lead already holding the context and the tools
  for a task will default to just doing it"). The temptation was
  identical here — the fixture, binary, and full context were already
  in hand from implementation — and the dispatch happened anyway,
  because the process was written down as a hard rule in this same
  phase, not left as a should.
- **Not pre-committing to the depth-related entries' final `kind`
  before the independent check ran.** They were left at `self-verified`
  with `verified_by` explicitly naming the pending dispatch, so there
  was no temptation to treat the lead's own evidence as already settled.

## What didn't work

The planning pass's own differential-test matrix (§6 of the plan) did
not include `stats`, despite `stats`' pre-existing TODO comment about
depth being directly relevant — an oversight in the *planning* pass, not
this implementation phase, but worth naming since it's the second time
in this phase's own history that "trust the plan's matrix as complete"
would have been wrong (the first being `register`/`accounts`'
pre-existing exclusion bug, missed by the plan's current-state
assessment too). Both gaps were caught by testing every command
mentioned in the plan's own scope, not by assuming the matrix's coverage
was exhaustive.

## Lessons learnt

A planning pass's differential-test matrix, however thorough it looks, is
a hypothesis about what needs checking — not a checklist that, once
satisfied, guarantees nothing else in the same feature area behaves
differently. The concrete discipline that caught both misses here: test
every command the feature touches directly, even ones the matrix didn't
flag as needing a new scenario, rather than treating "not in the matrix"
as "already known to be fine." This is a variant of the same lesson
Phase 1's `depth:` mistake and this phase's own planning pass both
already taught in different forms — a claim's absence from prior
research is not evidence the claim is settled.

## Process-improvement feedback

The verification-independence process worked exactly as designed on its
first real use: the dispatch found nothing wrong (all three entries'
claims held), which is itself informative — it means the self-verified
evidence from implementation was accurate, not that the independence
check was theatre. The value wasn't in catching an error this time; it
was in the check happening at all, on a claim strong enough to warrant
it, without needing a second incident like `LK-COMPAT-QUERY-DEPTH-001`'s
Phase 1→2 correction to force it. Worth naming for whoever next reads
`09-compatibility-system.md` §9.6: the dispatch cost here (one agent
call, ~250s, 28 tool uses) was small relative to the confidence it
bought — not a reason to skip it "just this once" on a future phase
under time pressure, which is exactly the failure mode this section
exists to prevent.

## Learnings filed

- `knowledge/DECISIONS.md` — five entries (DepthSpec-not-QueryNode
  architecture, `Query.depth` staying flat-only, `MaxAccountLevel`
  rename/Python-API-only, no standalone `--depth` flag this phase, and
  the `stats` exclusion-quirk replication choice).
- `knowledge/DOMAIN_RULES.md` — the full depth precedence/combination
  algorithm and the `stats` exception, as a single tacit-rule entry.
- `knowledge/EDGE_CASES.md` — EC-017 marked resolved, with a correction
  to its own original claim about `Query.depth`'s pre-existing
  correctness (it was only ever correct for `balance()`).
- `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`
  (reclassified `compatible`, `status: verified`),
  `LK-COMPAT-QUERY-DEPTH-STATS-001.yaml` (new, `status: verified`),
  `LK-COMPAT-QUERY-PRINT-INTEGRATION-001.yaml` (addendum, `status:
  verified`) — all independently verified, not self-verified.
- `dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.6
  — the process amendment itself.

## Where we're going

`tag:` query-term matching (deferred at the end of Phase 4, still
unscoped), `cur:`, `PythonRegex`, the larger `Query`-as-compatibility-
shim migration, and a standalone `--depth`/`-N` CLI flag (this phase's
own G-DEPTH-4 deferral) are all named, unscoped candidates. This phase
resolved a real defect and a real process gap rather than extending
Stage C's term coverage — the next phase should get its own explicit
scoping pass, per this project's standing process, not an assumed
continuation.

## Time / cost note

Three commit boundaries across one extended session: process amendment
(mechanical, ~15 tool calls), `depth:` redesign (the largest single
piece — source tracing across six hledger files, module implementation,
21 test rewrites/additions, two incidental bug fixes, ~60 tool calls
including live differential checks), independent verification (one
agent dispatch, ~250s wall time, 28 tool uses on its own account) plus
this closeout. The source-tracing step (confirming `queryIsDepth` is
stripped in every real command path, not just the `Depth` constructor
itself) was, again, the step most worth the extra time — it is the
finding that turned "depth: is wrong" into a concrete, implementable fix
rather than another documented-and-accepted divergence.

# Stage C Phase 2 retro — CodeCompass adoption + query/report/CLI integration

- **Date:** 2026-09-16
- **Commit(s):** `0f4465d` (boundary 1), `27c410d` (boundary 2), this
  retro's own commit (boundary 3)
- **Agents used:** none dispatched — see "What didn't work" below; this
  is itself a finding, not an oversight left unrecorded

## Where we are

Two planning-only passes preceded this: the original plan
(`18-stage-c-phase-2-codecompass-adoption-plan.md`, retro `STAGE-C-PHASE-
2-PLAN.md`) and its amendment per four review findings (retro
`STAGE-C-PHASE-2-PLAN-AMENDMENT.md`). This is the actual implementation
phase the two planning passes prepared. Stage C Phase 1 had delivered a
standalone, untested-in-integration `ledgerkit/query/` subpackage; this
phase is the first time any of it is reachable from the CLI. Separately,
this is Ledgerkit's own first-ever real use of the `codecompass` CLI
against its live repository — six prior CodeCompass-side evaluations
(Phase 45/46/47/49/51/54) existed, but all ran against a pinned commit or
scratch copy, from CodeCompass's own repo, never from inside Ledgerkit's
own agent workflow. After this phase: `-q`/`--query` is a real, tested,
differentially-verified CLI flag; a real `CC-LK-001` finding exists;
`ledgerkit/reports.py` sits at 618 lines (up from 573, still one file, no
split); Stage C's next phase (extending query terms, wiring `print`, or
the `Query`-as-shim migration) is unscoped.

## Goal

Use current CodeCompass, unmodified, on genuine Ledgerkit development
work (integrating the existing query engine into `reports.py`/`cli.py`),
independently evaluate the context it provides, and feed evidence-backed
findings back to CodeCompass without modifying it during the experiment
— while shipping a real, working feature regardless of what CodeCompass
contributed.

## Scope delivered vs planned

All three commit boundaries delivered as scoped in the amended plan.
`print`/`check` deliberately left unwired (named as follow-on, not
absorbed). `tag:`/`cur:`/`PythonRegex`/`Query`-as-shim not touched. The
API-boundary decision gate resolved to Option C (private `_query_ast`
parameter, no public API change) — the plan's own stated default absent
a demonstrated caller need, confirmed still true at implementation time.

One real, unplanned addition, directly motivated by differential testing
rather than scope creep: two genuine CLI bugs (empty-`balance`-result
formatting; a `max()` crash on that same path) were found and fixed, and
one Stage C Phase 1 compat-register entry (`LK-COMPAT-QUERY-DEPTH-001`)
was reclassified from `compatible` to `intentional_divergence` after
executable evidence contradicted its original source-reading-only claim.
None of this was scoped in advance — it's exactly what phase step 5
("resolve any real Ledgerkit defect found") existed to catch, and it did.

## What was achieved

A real, working `-q`/`--query` CLI flag across `balance`/`register`/
`accounts`/`stats`, differentially verified against the pinned hledger
1.52.4 binary on 10 representative cases (simple account query, negation,
date range, status, multiple conditions, report integration across three
commands, no-match, malformed query, plus `desc:`/`depth:` spot-checks).
6 compat-register entries updated with real executable evidence (5 to
`verified`, 1 corrected). 23 new tests, 679 total, all passing. The first
`CC-LK-NNN` finding this project has ever produced, closing the gap
`05-context-curator.md` §5.3 named at planning time: CodeCompass had an
internal loop about itself; Ledgerkit's external half of that loop had
never actually run.

## What worked

- **Resolving the API-boundary gate to the conservative option and
  writing it down before touching any code.** No `api-spec.md` friction
  at all this phase — confirmed untouched at every checkpoint, exactly
  because the question was settled deliberately first rather than
  defaulted into.
- **Differential testing against the real binary, not just the plan's
  predicted cases.** Two of the ten cases run (`depth:`, and the empty-
  result formatting check) surfaced genuine, previously-unknown problems
  — one a real crash bug, one a compat-register entry that was simply
  wrong. Neither would have been caught by unit tests alone, since both
  needed a second, independent implementation (the real hledger binary)
  to compare against.
- **Not stopping at "balance/register differ" for the `depth:` finding.**
  Checking `register depth:1` and `print depth:1` too (not just
  `balance`) turned "balance seems to disagree with the compat-register
  entry" into "there is no hledger context found where `depth:` behaves
  as a pure exclusion predicate at all" — a materially stronger, more
  honest correction than the first data point alone would have supported.
  Also worth naming: `print depth:1`'s behaviour didn't fit either
  hypothesis (exclude or truncate) and was left as an explicitly
  unresolved observation rather than forced into a confident claim.
- **Recording the fix for a Stage C Phase 1 mistake as a correction with
  its own reasoning, not just a silent edit.** `LK-COMPAT-QUERY-DEPTH-001`
  now explains *why* the original classification was wrong and *how* it
  was caught — useful for exactly the "trust prior 'verified' claims
  less than an actual rerun" lesson Stage C Phase 1's own retro already
  named in a different context (the G8 inventory correction, Stage B).

## What didn't work

**The differential-testing step was done directly by the lead, not via a
separately-dispatched `compat-differential-tester` agent**, as the plan's
own agent-role design (§5) specified. This wasn't a deliberate choice
made and recorded at the time — it happened because the lead was already
mid-implementation with the fixture and binary at hand, and dispatching a
fresh agent for a step that could be done in the same breath felt like
friction rather than value in the moment. In hindsight this is a real
gap in the intended independence: the two bugs found and the compat-
register correction are *objectively* verifiable (anyone can re-run the
same commands against the same pinned binary and get the same answer),
so the *substance* isn't in question — but the *process* the plan
designed specifically to keep implementation and verification separate
wasn't actually followed, and that's worth being honest about rather
than quietly treating the outcome as equivalent to having used it.

## Lessons learnt

Independence built into a plan's agent-role design needs to be enforced
at the moment the relevant phase step starts, not assumed to happen
because the plan says so — a lead already holding the context and the
tools for a task will default to just doing it, even when the plan
specifically separated that step for a reason. If a future phase's plan
calls for a distinct agent dispatch specifically for independence (not
just division of labour), that dispatch should be a literal, checkable
action taken at that step, not something the lead can satisfy by doing
equivalent-quality work itself. Separately: a "the source says X is
compatible" classification from a prior phase is exactly the kind of
claim differential testing exists to pressure-test — this session's
correction is a second, independent confirmation (after the Stage B G8
inventory correction) that a claim recorded confidently from reading
alone should be treated as provisional until something actually runs it.

## Process-improvement feedback

The three-commit-boundary structure (amendment finding 4) worked exactly
as intended — each commit is independently reviewable for a different
question ("was the baseline captured honestly," "does the feature work,"
"was CodeCompass evaluated fairly"), and `git log` on this phase now
shows that structure directly, not asserted. The API-boundary gate
(amendment finding 1) also worked as intended: it was a real decision
point that got made and recorded, not skipped. The one process gap (agent
independence for differential testing, above) is the actionable note for
whoever writes the next plan with a similar role split — consider naming
explicitly, in the plan itself, what happens if the lead is tempted to
skip the dispatch ("don't," stated plainly, might be enough; a harder
gate might not be worth the ceremony for a single-session implementation
where the same lead would review the agent's output anyway).

## Learnings filed

- `knowledge/DECISIONS.md` — the API-boundary resolution (private
  `_query_ast` parameter, Option C).
- `knowledge/EDGE_CASES.md` — EC-016 (empty-`balance`-result CLI bugs),
  EC-017 (the `depth:` divergence).
- `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml` — corrected
  classification with full reasoning.
- `validation/codecompass/findings/CC-LK-001.{yaml,md}` — the first real
  CodeCompass context-quality finding this project has produced.

## Where we're going

**Recommendation on CodeCompass as part of the default workflow**: not
yet warranted as a required step. This phase's own evidence (LOW
advantage, PASS WITH GAPS, honest-empty not wrong) matches every prior
CodeCompass-side Ledgerkit evaluation — six consistent data points now,
across both directions of usage (CodeCompass evaluating itself against
Ledgerkit, and now Ledgerkit using CodeCompass on itself), all landing at
the same structural ceiling (0 tracked vendors; no doc-to-doc relation
mechanism; no executable-technical-dependency concept). Running it
remains free, fast, and non-invasive (this phase's own baseline took
minutes and left no trace once reverted) — worth doing again on a future
phase if the task shape differs enough to be a genuinely new test (per
`18-...md` §13's own suggestion), but not worth making mandatory
per-phase overhead on the strength of six consistent LOW results.

**Next Ledgerkit phase, proposed not started** (per the plan's §13, now
informed by this phase's actual evidence): wiring `-q` into `print` is
the smallest, cleanest next step, since the integration pattern proved
clean here and `print` is the one remaining report with zero query
support at any level. The `Query`-as-compatibility-shim migration and
`tag:`/`cur:` term extensions remain larger, separately-scoped
candidates — `tag:` specifically should read CodeCompass's own Phase 54
reference-material experiment first (a real, caught extraction-accuracy
defect in `tag:`-adjacent material), regardless of who does it.

This phase confirmed the planned trajectory (the integration pattern
works, CodeCompass's value ceiling is stable and now doubly-confirmed
from both directions) rather than changing it — the one real surprise
(`LK-COMPAT-QUERY-DEPTH-001`'s misclassification) is a correction to
existing project knowledge, not a finding that reshapes Stage C's plan.

## Time / cost note

Three commit boundaries in one continuous session: baseline capture (~10
tool calls), implementation + differential testing + bug fixes (~30 tool
calls, including live hledger comparisons), closeout (this retro + the
finding). No step ran unusually long; the `depth:` investigation (three
separate hledger commands to pin down the actual behaviour precisely)
was the most exploratory single piece, and worth the extra two commands
— stopping after the first `balance depth:1` result alone would have
supported a weaker, less-certain correction.

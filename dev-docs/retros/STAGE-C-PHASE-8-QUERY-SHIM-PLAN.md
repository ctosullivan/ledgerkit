# Stage C Phase 8 retro — Planning (`Query`-as-compatibility-shim convergence)

- **Date:** 2026-09-26
- **Commit(s):** see `git log` for this retro's own commit.
- **Agents used:** none — direct lead source/docs audit, per this
  phase's own §1 rationale (the target semantics are an already-
  implemented, already-verified subsystem; the open questions are
  Ledgerkit-internal architecture/compatibility, not new hledger
  research a specialised research role's charter actually covers).

## Where we are

Stage C Phase 7 (empty-regex-pattern rejection) closed implementation-
and-verification-complete, naming "converge the legacy public `Query`
pathway toward the query-AST/compatibility-shim architecture" as backlog
item 2. This retro covers the design phase for that item — the second
of the two substantive architecture items left in Stage C's own charter
("Python `re` extension, CLI/report routing").

## Goal

Scope the convergence of `ledgerkit.models.Query` (a flat dataclass,
evaluated by its own ad hoc, non-`HledgerRegex`-validated matcher) onto
`ledgerkit.query`'s AST/evaluator (the hledger-faithful engine `-q`
already uses) — eliminating the second, parallel filtering path that
has existed since Stage C Phase 1, per `07-query-regex.md` §7.2's own
original, pre-Stage-C design target.

## Scope delivered vs planned

Design document produced (`27-query-shim-convergence-design.md`), no
implementation. One real de-risking discovery along the way: this
phase's central open question (should `Query`'s regex fields become
`HledgerRegex`-strict, matching `-q`'s dialect exactly?) turned out to
have a much smaller real-world blast radius than it might have — the
one known external consumer, `ledgerkit-editor`, never actually calls
into Ledgerkit's own `Query`-matching code at all (§3 of the design),
and Ledgerkit's own test suite's `Query(...)` usages use no
`HledgerRegex`-excluded construct anywhere (§8) — both confirmed by
direct grep/read, not assumed.

## What was achieved

Found and cited the actual pre-existing, already-approved architectural
target (`07-query-regex.md` §7.2: "The existing `Query` dataclass
becomes a compatibility constructor that compiles to a `QueryAST`...
rather than a parallel filtering path") — this phase is executing a
plan made at Core-redefinition time, not deciding a new direction from
scratch, which materially lowers its own risk profile relative to, say,
Stage C Phase 5's `depth:` redesign (which corrected a genuine Phase
1-4 mistake with no such prior blessing).

Found a real, easy-to-miss correctness trap before it could become a
silent bug: `ledgerkit.query.ast.DateSpan.end` is exclusive (matching
real hledger `date:` span semantics), while `Query.date_to` is
documented and implemented as inclusive — a naive field-for-field
translation (`DateSpan(end=query.date_to)`) would silently exclude
transactions dated exactly `date_to`, a real regression no existing
test would necessarily catch without a dedicated, explicitly-aimed
test. Flagged explicitly in the design (§4) with the correct
translation (`end=query.date_to + timedelta(days=1)`) and a named
required test (§11).

Confirmed, by direct grep against `tests/test_reports.py`/`tests/
test_dataframe.py`, that the recommended option (full `HledgerRegex`
convergence) would not break a single existing test on its own — every
current `Query(...)` usage in the test suite uses only plain substrings
or a portable anchor, no excluded construct.

## What worked

- **Checking whether a "new" architectural direction was actually new**
  before treating it as an open design question — grepping for prior
  mentions of "Query-as-shim" surfaced `07-query-regex.md` §7.2 and
  `06-core-architecture.md` §6.5 directly, turning what could have been
  a from-scratch design debate into "execute the existing plan, resolve
  the one thing it left open (regex strictness)."
- **Checking the real external consumer's actual code path**
  (`15-editor-compat-inventory.md`) rather than assuming "an external
  consumer depends on this" from the frozen-API commitment's existence
  alone — the frozen commitment is about `Query`'s field shape, and the
  one real consumer never touches the matching behaviour underneath it
  at all. This directly shaped the recommendation in §6.

## What didn't work

No misfires this phase. Correctly avoided repeating Phase 7's own
`context-curator` mis-dispatch by not reaching for a specialised agent
role for what was actually direct source/docs reading.

## Lessons learnt

- When a "next phase" item in a backlog list sounds like a big
  open-ended architecture decision, check whether it was already
  decided at an earlier planning stage before treating it as a fresh
  design question — Core-redefinition's own planning documents
  (`06-`/`07-...md`) had already specified this migration's target
  shape and its compatibility contract; the real remaining work was
  confirming the target is still correct and resolving the one
  genuinely open sub-question (regex strictness), not re-deriving the
  whole direction.
- A frozen public-API commitment naming a dataclass's *constructor
  shape* is not automatically evidence that changing the *behaviour*
  behind that constructor is equally constrained — checking the actual
  consumer's call graph (does it even reach the behaviour in question?)
  can substantially narrow a compatibility-risk analysis that would
  otherwise default to maximum caution.

## Process-improvement feedback

No process notes this phase — the design → approval handoff structure
continues to work cleanly.

## Learnings filed

None yet — deferred to implementation time, matching every prior
phase's own sequencing (learnings land with the code they document).

## Where we're going

Design document awaiting explicit human approval (§12's three-item
gate, one genuinely blocking: regex strictness Option A vs B). No
implementation begins until that lands. If approved, this is a smaller
implementation than Stage C Phase 6 (no new AST node, no new substrate
— purely an internal-evaluation-path consolidation behind an unchanged
public signature) and likely comparable in size to Stage C Phase 7.

## Time / cost note

One continuous planning session, no sub-agent dispatches. Most of the
effort was tracing the existing planning documents' prior commitments
and confirming the external-consumer/test-suite blast radius directly,
rather than open-ended design work.

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

## Addendum (2026-09-26, same day) — design-review correction pass

The user reviewed the design document and found the blast-radius
analysis genuinely incomplete on review — not wrong in what it checked,
but incomplete in what it checked. A design-review correction, exactly
the same category as Stage C Phases 6 and 7's own amendment rounds, not
an implementation defect (no `ledgerkit/`/`tests/` code existed yet).

**The most consequential finding**: the original document's "empty
blast radius" claim was based on grepping direct `Query(...)`
construction in `tests/`. It never checked whether anything *else*
synthesizes a `Query.account` value internally — and something does:
`Journal.balance`/`.register`'s deprecated `accounts=[...]` parameter,
for two or more accounts, builds a pattern using `(?:...)` non-
capturing groups, which `HledgerRegex` rejects outright. Under Option A
as originally proposed, this would have been a real, shipped regression
with **zero** existing test coverage to catch it — the multi-account
case has no test at all today. Caught before implementation only
because the review asked a sharper question than "does any direct
`Query(...)` test use an excluded construct" — namely, "does anything
*produce* a `Query.account` value the direct-construction grep
wouldn't see."

**Three further real gaps**, each confirmed by direct source read once
flagged: `balance_from_spec`'s own separate filtering loop (never
`_posting_matches`) still needs `_matches_pattern`, which an earlier
version of this design would have retired outright, breaking a live
public path (`ReportSection`); `stats(query=...)` silently ignores
`account`/`not_account` today (a pre-existing, already-documented
`TODO`), and full convergence would flip this from "unnoticed gap" to
"newly-applied filter" — a real behaviour change that needs to be
named and approved, not discovered as an incidental side effect during
implementation; and the proposed translator constructed AST nodes
without validating them first, which would have failed only lazily (if
at all — never, for an empty journal) rather than deterministically,
undermining the whole point of routing through the same validated
dialect. A fifth, smaller correction: the translator's proposed module
location (`models.py`) would have created a real circular import, since
`ledgerkit/query/eval.py` already imports from `models.py`. A sixth:
`Query.date_to + timedelta(days=1)` overflows at `datetime.date.max`,
an edge case the original inclusive-to-exclusive translation didn't
account for.

**Process observation**: this is now the fourth phase in a row (Stage C
Phases 6, 7, and this one) where the human-approval gate caught a real
gap the design's own author had missed, and — as with Phase 7 — none
of the gaps were subtle hledger-semantics questions; they were "did you
check every place this data flows through," a category of miss more
likely from confirmation bias (having found the reassuring "empty
blast radius" answer for the case checked, not pushing further to ask
what else might produce the same shape of input) than from missing
domain knowledge. Worth naming explicitly for future design passes:
a blast-radius claim should enumerate every *producer* of the value in
question (here: everything that can set `Query.account`), not just
every direct call site the obvious grep surfaces.

Corrected in the design document itself (§5.1/§5.1a/§5.1b/§5.1c, §2,
§3, §7, §8, §9, §10, §11, §12) — the core decision (converge onto the
canonical AST, Option A recommended, frozen field shape, `depth` stays
non-predicate, inclusive `date_to` preserved) is unchanged throughout.
Approval gate grew from three items to six (§12) — reflecting genuinely
new, named decision points (the `stats` behaviour correction, the
`_matches_pattern`/`ReportSection` scope, the `QueryParseError`-reuse
naming choice), not scope creep in the fix itself.

## Addendum 2 (2026-09-26, same day) — a second design-review correction pass

The first correction pass (Addendum 1) fixed a real, verified gap in
the original blast-radius analysis but, on a further review, was itself
still incomplete — it fixed the one deprecated-shim regression it found,
but never checked whether the *scope decision* it made for `_matches_
pattern` (keep it for **everything** `balance_from_spec` touches) was
actually the right boundary, and never built the systematic per-
consumer inventory that would have caught two more real gaps directly.

**The two most consequential findings this pass**:

1. **`Journal.to_dataframe(query=...)` was missed by both the original
   document and Addendum 1** — it imports and calls `_posting_matches`
   directly, a live, public, pandas-integrated method. Retiring
   `_posting_matches`, as both prior versions proposed, would have
   broken it outright. Found only by building the actual per-consumer
   inventory (§5.3, new) the design should have had from the start,
   not by re-grepping `Query(...)` test construction again.
2. **Addendum 1's own `accounts=[...]` fix had a second bug**: it
   handled "one account" vs. "more than one," silently routing **zero**
   accounts into the many-accounts branch, producing `Or(())` — an
   empty `Or`, which evaluates to matching *nothing*, the opposite of
   the intended "no filter" behaviour. A real regression inside a fix
   for a real regression, caught only because this pass re-examined
   every case (0, 1, many) explicitly rather than trusting the
   two-case split already in place.

A third, more architectural correction: Addendum 1 drew the `_matches_
pattern`-retention boundary around all of `balance_from_spec`, including
its **outer** `query.account`/`.payee`/`.not_account` — which is not
actually a distinct construct from `Query`, unlike `ReportSection`'s own
OR/exclude semantics. On review, only `ReportSection` needed the
exception; `balance_from_spec`'s outer query converges onto the
canonical engine like everything else, leaving `ReportSection` as the
**one** genuinely separate filtering construct in the entire codebase —
a materially cleaner, more defensible end state than "keep `_matches_
pattern` for this whole function."

**Process observation, now three levels deep on this exact document**:
this is the second correction pass on Phase 8's design (fourth
consecutive phase, counting Stage C 6/7, where review caught something
a design's own author missed) and the second time in this project's
history that a completeness claim based on grepping direct construction
sites (`Query(...)` in tests) turned out to be systematically
incomplete — the first time (Addendum 1) for the deprecated-shim
producer, this time for a whole missed *consumer* (`to_dataframe`). The
generalizable lesson, worth stating plainly for any future phase
touching a value with multiple producers/consumers: build the complete
inventory of every producer and every consumer explicitly (a table, not
a grep result) before making any completeness claim — a grep answers
"where does this literal pattern appear," not "where does this data
flow." §5.3 now exists specifically so this phase doesn't need to
re-derive that inventory a third time.

Corrected in the design document itself (§5.1b rewritten, §5.1d added,
§5.1a's multi-account fix extended to three explicit cases, §5.2
rewritten with a complete six-item change list, §5.3 added, §9/§10/§11/
§12 updated accordingly). The core decision is unchanged throughout.
Approval gate reduced from six open-ended items to six items each with
an explicit stated recommendation, per direct instruction — genuinely
only one (§6, regex strictness) remains a blocking human decision.

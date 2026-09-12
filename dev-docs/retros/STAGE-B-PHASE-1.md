# Stage B Phase 1 retro — Editor-compatibility inventory

- **Date:** 2026-09-13
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — done directly by the lead session (no agent
  dispatch needed for a single-source read-only grep/inspection task)

## Where we are

Stage B ("Core model — journal/accounting model review, Editor-compatibility
confirmation") is the phase immediately after Stage A closed out the
development foundation (agent roster, compat-register harness, licence
migration). This is Stage B's first phase. `06-core-architecture.md` §6.5
had flagged, since the planning session, a concrete but unexecuted action
item: verify `ledgerkit-editor`'s actual `import ledgerkit` usage by
reading its source, rather than relying on the README-inference that
produced `14-human-decision-gates.md` G8's original claims. That
verification is now done. After this phase: `ROADMAP.md`'s Stage B row is
`[IN PROGRESS]`; `06-core-architecture.md` §6.5 and G8 both carry corrected,
source-verified findings instead of inferred ones; no `ledgerkit/` or
`tests/` code has changed yet.

## Goal

Independently verify exactly which `ledgerkit` symbols `ledgerkit-editor`
imports and uses at runtime, by reading its actual source — not by
inference — so Stage B/C's frozen-API-surface and `Query`-compatibility-
shim commitments rest on confirmed fact rather than a prior planning-time
guess.

## Scope delivered vs planned

As scoped: read-only inventory, no `ledgerkit/`/`tests/` changes. One
addition beyond the original ask: rather than only inventorying, the
findings were used to correct three specific inaccuracies already recorded
in `14-human-decision-gates.md` G8 and `06-core-architecture.md` §6.5 —
this wasn't explicitly asked for, but leaving known-wrong claims sitting
uncorrected in the governing docs once they were disproven would be worse
than the small extra edit cost. No deferred scope — the phase's single
concrete goal was fully met.

## What was achieved

`dev-docs/planning/core-redefinition/15-editor-compat-inventory.md` — the
first artifact of its kind: a table of every `ledgerkit` symbol
`ledgerkit-editor` actually imports, where, and how (runtime vs.
`TYPE_CHECKING`-only), plus what it deliberately avoids importing and why.
Three corrections to prior assumptions:
1. `EditorDocument` is not used anywhere in `ledgerkit-editor`'s shipped
   code (only a stale docstring mention) — was previously assumed to be a
   real dependency.
2. `ledgerkit.reports`'s matching helpers are deliberately *not* imported —
   `ledgerkit-editor` duplicates that logic locally specifically to avoid
   depending on private, unexported members, with its own regression tests
   guarding against drift.
3. `ledgerkit.models` types are `TYPE_CHECKING`-only in shipped code, a
   weaker coupling than "uses `ledgerkit.models` directly" implied.

Also surfaced a genuinely useful implication for Stage C: `ledgerkit-editor`'s
entire coupling to `Query` is four constructor kwargs
(`account`/`payee`/`date_from`/`date_to`) read nowhere else — the future
`Query`-as-compatibility-shim only needs to preserve that narrow surface,
not any evaluation behaviour tied to `ledgerkit.reports` internals.

## What worked

- **Insisting on an actual clone over continuing to reason from
  documentation.** The original G8 inventory looked complete and
  confident, but three of its specific claims didn't survive contact with
  the real source. Confidence in a prior finding is not the same as that
  finding being correct — worth remembering before treating any
  "inspected" claim, including this session's own future ones, as settled
  without a citable grep/read behind it.
- **Asking the user for the exact clone URL rather than guessing or
  inferring one.** No URL for `ledgerkit-editor` had been given anywhere in
  this conversation; fabricating one to save a round-trip would have
  risked cloning the wrong repository or none at all.
- **Scoping this as a read-only phase before any `Query`-adjacent code
  change**, per `06-core-architecture.md` §6.5's own stated precondition —
  meant the (real, load-bearing) discovery that `EditorDocument` isn't
  actually used landed *before* any frozen-API-surface commitment was
  written in terms of it, not after.

## What didn't work

Nothing failed this phase. One near-miss worth naming: the user's initial
"implement next phase" request, taken literally, would have meant starting
architecture/parser work under G5's "in-principle-only" approval — which
`14-human-decision-gates.md` explicitly says is *not* authorisation to
start. Asking which concrete Stage B work to do first (rather than picking
one) is what caught this before any `ledgerkit/` code was touched.

## Lessons learnt

A prior "inspected"/"confirmed" claim about an external dependency's usage
is worth re-verifying from the actual source before it's relied on for an
API-freeze decision, even when it was recorded confidently and recently —
inference from a README or a summary is not the same evidentiary weight as
a grep against real code, and the gap between them is not always small (3
of ~9 claimed symbols needed correction here). This mirrors
`10-source-assisted-development.md` §10.4's warning about "verify locally ≠
verify across the matrix," generalised to "someone's earlier inspection ≠
your own independent verification."

## Process-improvement feedback

`ROADMAP.md`'s "Deciding What Goes Into a Milestone or Stage" process (and
`14-human-decision-gates.md`'s G5 note) worked exactly as designed here:
a vague "implement next phase" instruction was caught before it turned
into unauthorised architecture work, by treating "Stage B" as requiring an
explicit scope decision rather than an implicit green light. No friction
in the roster itself — this phase didn't need a specialist agent, and
correctly wasn't forced to dispatch one just to have used the roster.

## Learnings filed

None to `knowledge/*.md` this phase — the corrections belong in the
planning docs they correct (`06-core-architecture.md`,
`14-human-decision-gates.md`), not in `knowledge/DECISIONS.md`, since no
judgment call was made here (only verified facts about an external
consumer's behaviour).

## Where we're going

Stage B's next phase is not yet scoped — candidates visible from
`06-core-architecture.md` §6.3 include the actual "journal/accounting
model review" half of Stage B's name (as opposed to this phase's
"Editor-compatibility confirmation" half), and/or the parser
lot-annotation-retention change G5(a) approved in principle. Per
`ROADMAP.md`'s process, the next phase's scope needs the same kind of
explicit confirmation this one got before any `ledgerkit/` code changes —
this phase did not change that requirement, it satisfied one instance of
it. This phase confirmed rather than changed the planned Stage B/C
trajectory, but it did tighten (narrow, in a good way) the known scope of
Stage C's `Query`-shim obligation.

## Time / cost note

Single response, one clone + grep pass (shallow clone, no build/install of
`ledgerkit-editor` needed). No unusually long step.

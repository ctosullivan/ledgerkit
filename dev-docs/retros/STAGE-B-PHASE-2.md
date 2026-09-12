# Stage B Phase 2 retro — Journal/accounting model review

- **Date:** 2026-09-13
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — a single-source read-only architectural review,
  no agent dispatch warranted

## Where we are

Stage B Phase 1 (previous phase) independently verified `ledgerkit-editor`'s
actual `ledgerkit` usage. This phase is the other half of Stage B's name:
"journal/accounting model review." `06-core-architecture.md` §6.3 had
asserted, at planning time, that `models.py` needs "no structural change"
to later carry Stage E/F's `Cost`/`Lot`/`PriceGraph`/valuation types — an
assertion, not yet independently checked. That check is now done. After
this phase: the claim is confirmed, but with two concrete guardrails now
recorded in `06-core-architecture.md`, `08-accounting-semantics-roadmap.md`,
`dev-docs/architecture.md`, and `knowledge/DECISIONS.md`, so Stage E/F
doesn't rediscover them the hard way. No `ledgerkit/`/`tests/` code has
changed across either Stage B phase so far.

## Goal

Independently review whether `models.py`'s current shape can actually
accommodate Stage E/F's planned additions (costs, lots, virtual postings,
valuation, account types) without structural change, as
`06-core-architecture.md` §6.3 claims — verify, don't just accept.

## Scope delivered vs planned

As scoped: read-only review, no `ledgerkit/`/`tests/` changes. The review
surfaced one genuine finding beyond a simple confirm/deny: most of the
claim holds cleanly (costs, lots, virtual postings, valuation are all
pure-addition cases), but one specific sub-case
(`Journal.declared_accounts` for account-type semantics) would break a
confirmed real dependency (`ledgerkit-editor`'s `journal_index.py`, from
the previous phase's inventory) if implemented the "obvious" way. That
finding wasn't part of the original ask but follows directly from
combining this phase's own review with the previous phase's evidence —
recorded as a guardrail rather than left implicit.

## What was achieved

`dev-docs/planning/core-redefinition/16-model-review.md`: a verdict
(confirmed, with guardrails) plus the two guardrails themselves, now
threaded through four places so they're findable from wherever someone
would look for them — the Stage B plan doc, the Stage E/F roadmap doc, the
architecture design-principles list, and `knowledge/DECISIONS.md`. Also
confirmed `Query`/`ReportSpec`/`ReportSection` (also in `models.py`) are
unaffected and out of this review's scope (Stage C's concern).

## What worked

- **Building directly on the previous phase's evidence instead of
  re-deriving it.** The `declared_accounts` finding only surfaced because
  this review connected `08-accounting-semantics-roadmap.md`'s "type: tag
  is currently stripped/ignored" note with Stage B Phase 1's confirmed
  fact that `ledgerkit-editor` reads `declared_accounts` as a flat
  `list[str]`. Neither fact alone flags the risk; combining them does.
  Retros/phases accumulating real evidence pays off across phases, not
  just within one.
- **Reading the actual `parser.py` account-directive code** rather than
  trusting `08-...md`'s prose description of what happens to the `type:`
  tag — confirmed accurate in this case, but worth the two-minute grep
  rather than citing the planning doc as its own evidence.

## What didn't work

Nothing failed this phase.

## Lessons learnt

A structural-soundness claim in a planning doc ("no structural change
needed") can be locally true for most of what it covers and still hide one
specific case that isn't — reviewing item-by-item against real, confirmed
consumer dependencies (not just against the codebase in isolation) is what
surfaces that, a plain "does this still look fine" read of `models.py`
alone would not have connected `declared_accounts` to `ledgerkit-editor`
without deliberately cross-referencing the previous phase's inventory.

## Process-improvement feedback

No friction this phase. Worth naming as a positive pattern for future
retros to watch for: this phase's finding depended on treating
`15-editor-compat-inventory.md` as an input to a *different* phase's
review, not just as that phase's own closed deliverable — retros/phase
artifacts are worth deliberately re-reading when scoping an adjacent
phase, not just when their own phase is active.

## Learnings filed

- `knowledge/DECISIONS.md` — the `declared_accounts` additive-only
  guardrail for Stage E's account-type semantics (2026-09-13).
- `dev-docs/architecture.md` — new Design Principles bullet: every new
  `Posting`/`Transaction` field must make a deliberate `compare=` choice.

## Where we're going

Stage B's next phase is still unscoped. With both halves of Stage B's
stated name now done (Editor-compat confirmation in Phase 1, model review
in Phase 2), the next phase could reasonably be: (a) starting Stage B's
own backlog item — `EditorDocument`'s include-directive limitation — since
Phase 1 confirmed `EditorDocument` itself isn't actually depended on by
`ledgerkit-editor`, which changes how urgent that fix is; (b) treating
Stage B as complete and scoping Stage C (query system) next; or (c)
something else entirely. This phase confirmed the planned trajectory
(models.py doesn't need surgery before Stage E/F) rather than changing it,
but it did add two concrete constraints that Stage E/F implementation must
respect.

## Time / cost note

Single response; reading `models.py`, `08-accounting-semantics-roadmap.md`,
the relevant `parser.py` section, and `api-spec.md`, plus one grep. No
unusually long step.

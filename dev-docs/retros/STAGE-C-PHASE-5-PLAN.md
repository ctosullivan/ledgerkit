# Stage C Phase 5 retro — Planning (verification independence + `depth:` semantics)

- **Date:** 2026-09-17
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — direct inspection and planning by the lead
  session; no agent dispatch warranted for a read-only planning pass
  (consistent with the `STAGE-C-PHASE-2-PLAN.md` precedent for
  planning-only phases)

## Where we are

Stage C Phase 4 closed with a working tag data model. This phase is
planning-only, triggered by two issues the user identified in recent
Stage C work rather than by a retro's own "where we're going" section:
(1) every compat-register entry this project has ever marked `status:
verified` was verified by the same session that implemented the feature
— a process gap Phase 2's own retro already named and never converted
into an enforced rule; (2) `ledgerkit.query.ast.Depth` models hledger's
`depth:` as a pure boolean exclusion predicate, which — per this phase's
own fresh source/manual/executable inspection — is not what any real
hledger command does. Produces `21-stage-c-phase-5-depth-and-
verification-plan.md`. No implementation happened — explicitly out of
scope per the user's own instruction, and the plan is the deliverable.

## Goal

Plan (not implement) a phase resolving both issues: a lightweight,
claim-strength-scaled verification-independence rule, and a corrected
`depth:` semantic model grounded in the hledger manual, source, and the
pinned executable — not prior chat discussion, per the user's explicit
instruction to treat none of the earlier conversation as evidence.

## Scope delivered vs planned

All nine requested planning outputs delivered (current-state assessment;
process amendment; proposed semantic model; AST/parser/evaluator impact;
migration strategy; differential-test matrix; affected compat records/
docs; implementation phases + DoD; explicit human-decision gates), each
grounded in this session's own direct inspection rather than the prior
conversation's summary of it — the user's instruction was followed
literally: every claim in the plan traces to a file read, a source grep,
or a command actually run this session.

One thing found that the request didn't explicitly ask to look for but
that materially changes the plan's shape: `ledgerkit/reports.py` already
contains a second, older, *correct* depth-truncation implementation
(`models.Query.depth`, pre-dating Stage C's `-q` work entirely), whose
own docstrings explicitly contrast themselves against the newer, wrong
`_query_ast` `Depth` node. This turns "Ledgerkit diverges from hledger"
into the sharper, more actionable "Ledgerkit's own two depth mechanisms
already disagree with each other, and one of them is already right" —
the fix is a unification the codebase was already halfway toward, not a
greenfield semantic design.

## What was achieved

A single plan document with: a table of all 11 `verified` compat-register
entries showing every one was lead-self-verified; a newly-proposed
four-value `status` enum (`proposed`/`self-verified`/`verified`/`final`)
that makes the independence gap structurally checkable via retros and
`release-phase-auditor` rather than a convention to remember; a `DepthSpec`
design (general + `REGEX=NUM` + hledger's exact specificity-precedence
rule) confirmed against `hledger-lib` source (`Query.hs`,
`AccountName.hs`) *and* a fresh 14-row executable differential matrix run
against the pinned 1.52.4 binary on a purpose-built fixture; a definitive
resolution of Phase 2's long-standing open question ("what does `print
depth:1` do?" — confirmed via `EntriesReport.hs` source and a live run:
nothing, depth is fully stripped and never reapplied) plus a *new*
finding that current Ledgerkit's `print -q "depth:1"` is actively wrong
in the opposite direction (shows nothing, where hledger shows everything)
— not previously documented anywhere. Six explicit human-decision gates
(G-DEPTH-1..4, G-PROCESS-1..2), none pre-resolved by the plan itself.

## What worked

- **Reading `Query.hs`'s actual command-level callers, not just the
  `Depth` constructor's own `matchesAccount` definition.** The
  constructor and its boolean semantics are real and were not
  hallucinated by Stage C Phase 1 — but grepping every file that
  constructs or consumes a `Query` found `filterQuery (not . queryIsDepth)`
  stripped out before selection in *every single* command path
  (`MultiBalanceReport.hs`, `PostingsReport.hs`, `EntriesReport.hs`,
  `Accounts.hs`, `AccountTransactionsReport.hs`, `Ledger.hs`). Stopping at
  the constructor's own function body — which is what Phase 1 did — would
  have reproduced Phase 1's exact mistake a second time.
- **Building one fixture with a deliberate regex-collision case**
  (`assets` vs `savings` both matching `assets:bank:savings`) specifically
  to reproduce the manual's own worked precedence example against the
  real binary, rather than trusting the manual's prose alone. It
  reproduced exactly as documented, and the run also surfaced a
  non-obvious display nuance (a clipped sibling account not appearing as
  its own row in one combination) that's noted as an implementation-time
  detail rather than over-interpreted into the semantic model itself.
- **Reading `reports.py`'s own inline comments as primary evidence**
  rather than only its function signatures — the docstrings at lines
  369-372 and 379-381 were already, in effect, an internal admission of
  the exact inconsistency this plan formalises; missing them would have
  meant re-deriving from scratch a finding the codebase had already
  half-recorded.

## What didn't work

Nothing failed in this planning pass. One judgment call worth naming:
the request asked for a bounded behavioural matrix "at minimum" covering
five commands and several depth-option shapes; it was tempting to stop
once `balance`/`register`/`print` confirmed the core pattern (strip
before selection, clip for display) and treat `accounts`/`stats` as
presumably following suit. Running them anyway surfaced that `accounts`'
current Ledgerkit behaviour is a *third*, previously-undocumented kind of
wrong (filters rather than clips/deduplicates) and that `stats`'
depth-sensitivity is a real, currently-unimplemented gap the codebase's
own TODO comment already named but no prior phase had scoped work
against.

## Lessons learnt

A library function's own type signature and its own unit-test coverage
(here: `Query.hs`'s `Depth` constructor and its test-suite assertions at
lines 1150-1152) can be completely real and still not describe user-
observable behaviour, if no shipped command path actually invokes it that
way. The check that actually settles a "does hledger do X" question is
tracing every real command's consumption of the relevant `Query`/
`ReportOpts` value end to end, not the existence of a plausible-looking
function. This is the second time this exact class of mistake has
surfaced in this project (Phase 1's original `depth:` misclassification
was the first) — worth generalising explicitly rather than treating each
occurrence as a one-off: for any hledger source-reading exercise, "does a
function with this name exist and do what I'd expect" is not sufficient
evidence; "is this function reachable from the command a user actually
runs" is the real question.

## Process-improvement feedback

The request's own structure (bounded matrix before redesign, explicit
gates before implementation, "do not rely on prior chat discussion")
mapped cleanly onto this project's existing planning-pass conventions
(`18-...md` / `STAGE-C-PHASE-2-PLAN.md` precedent) with no friction —
the same numbering scheme, gate style, and retro-for-a-planning-phase
pattern already existed and needed no new scaffolding. One thing worth
naming for whoever next writes a verification-independence-adjacent plan:
this phase proposes amending `09-compatibility-system.md` and two agent-
role files, but deliberately did not amend them in this pass, on the
reasoning that process/policy documents deserve the same "propose, then
gate" treatment as code — that's a judgment call (the request didn't say
explicitly whether doc-only process amendments count as "broad
implementation"), recorded here in case the user disagrees and wants
process docs treated as lower-risk than code.

## Learnings filed

None to `knowledge/*.md` this phase — every finding here is either
project-history-specific (lives in the plan document itself, §1, where
anyone acting on it will read it first) or not yet a settled decision
(the six gates are explicitly open, not yet judgment calls to record).

## Where we're going

Stage C Phase 5 itself (the actual process amendment + `depth:`
implementation, per the plan's §8 phase breakdown) is planned but **not
started** — it awaits resolution of all six gates in §9, per this
project's standing process. The plan's own §8 already sequences the work
so the process amendment (5a) can land independently and ahead of the
depth semantics work (5b/5c) if the user wants to approve them on
different timelines rather than as a single all-or-nothing block.

## Time / cost note

Single response: repository inspection (compat-register entries, agent
role files, retros), a full hledger source trace across six files, one
purpose-built fixture, ~15 executable comparisons against the pinned
binary (hledger and current Ledgerkit both), then the plan document
itself. The source trace (confirming `queryIsDepth` is stripped in every
command path, not just checking the `Depth` constructor) was the step
most worth the extra time — it's the finding that turns "depth: is
wrong" into "here is exactly what depth: actually is."

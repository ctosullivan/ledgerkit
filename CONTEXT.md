# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:` query-term matching) — a small final correction
pass on the design document (not a redesign): fixed `accounts tag:X`
visibility (a four-way split, not the prior amendment's incomplete
three-way one), clarified transaction-level matching's rule, fixed a
real Python error in the evaluator-API wording, and resolved the
commodity-tag substrate's scope as in-phase. **Still stopped for the
mandatory human design-review gate.** No implementation has begun.

## Where We Are
Corrected design document: `dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md` — §17 now lists **two** open items
(down from five). A second dated addendum was appended to the existing
planning retro (`dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md`,
original content and first addendum both untouched). `ROADMAP.md`/
`CHANGELOG.md` updated. About to commit + push, then present a concise
summary and wait — do NOT proceed to Step 4 or any code change until
explicit approval arrives.

## Decisions In Flight
- **§9.1: inheritance scope** — Option A (complete, four sources) vs.
  Option B (own-tags-only, disclosed divergence). Lead recommends A.
  **Not decided.**
- **§9.2: `accounts` command mode** — replicate hledger's mode
  (transaction-level + account-inherited visible; posting-own +
  commodity-propagated not — the corrected four-way split) vs. uniform
  matching. Lead recommends replication. **Not decided.**
- Resolved this pass, no longer open: §9.1's evaluator-API shape
  (candidates named, none chosen — implementation-planning-stage
  choice, not a blocking gate); commodity-tag substrate scope (in this
  phase, not a prerequisite sub-phase); §9.3 helper visibility
  (private by default).

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/23-tag-query-matching-design.md`
  — §2.5 (corrected `accounts` four-way visibility), §6 (transaction-
  matching rule), §9.1 (evaluator API + commodity scope, both
  corrected/resolved), §9.2 (accounts recommendation), §17 (current,
  shorter approval list).
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md` — original retro
  plus two dated addenda (first: commodity-tag propagation; second:
  this correction pass).
- `hledger-lib/Hledger/Data/Posting.hs:443-444` —
  `transactionAllTags t = ttags t ++ concatMap ptags (tpostings t)`,
  the exact source for §6's corrected transaction-matching rule.

## Blockers / Open Questions
Two items in the amended §17 — see "Decisions In Flight" above. Nothing
else blocking.

## What NOT To Revisit
- Don't re-derive `accounts tag:X`'s visibility rule — now confirmed,
  three verification passes deep, as: transaction-level and account-
  inherited tags visible; posting-own and commodity-propagated tags
  not. This took three passes to get right; treat it as settled unless
  new evidence contradicts it.
- Don't reintroduce "keyword-only parameter with no default" as a
  backward-compatible evaluator-API shape — it is a real Python error
  (such a parameter is still mandatory on every call). The corrected
  candidates are `journal: Journal | None = None`, a context object, or
  pre-materialized storage.
- Don't re-open the commodity-tag substrate's scope question — resolved
  this pass, in scope for this phase, not a prerequisite sub-phase.
- Don't silently pick Option A/B (§9.1) or a mode for §9.2 and proceed —
  both remain explicit, named human-decision gates.
- Don't treat any of these corrections as implementation defects — no
  `ledgerkit/`/`tests/` code exists yet; all three correction passes so
  far have been design-review corrections, caught exactly where this
  process's own gate exists to catch them.

## Recent Git State (before this response's commit, if any)
2d2ebf6 docs: amend Stage C Phase 6 tag: design -- add commodity-tag semantics
7a74056 docs: Stage C Phase 6 -- tag: query-matching context curation + design
f397d85 docs: Stage C Phase 5A -- adopt CodeCompass v1 development workflow
eecb8a9 docs: amend Stage C Phase 5A plan per review findings
c6e4b1e docs: plan Stage C Phase 5A -- CodeCompass workflow adoption

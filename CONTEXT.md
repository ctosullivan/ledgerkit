# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 6 (`tag:` query-term matching) — the design document was
amended after user review (a targeted correction, not a redesign): it
was missing commodity-directive tag propagation, a real, separately-
documented fifth source. **Still stopped for the mandatory human
design-review gate.** No implementation has begun.

## Where We Are
Amended design document complete: `dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md` — §17 is the current, updated approval
list. A dated addendum was appended to the existing planning retro
(`dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md`, original content
untouched). `ROADMAP.md`/`CHANGELOG.md` updated. About to commit + push
this correction, then present the amended design's material changes and
wait — do NOT proceed to Step 4 or any code change until explicit
approval arrives.

## Decisions In Flight
- **§9.1: inheritance scope** — Option A (now correctly defined as
  *complete*: posting + transaction + account-inherited + commodity-
  propagated, all four verified sources) vs. Option B (own-tags-only,
  now a bigger disclosed gap than originally framed). Lead still
  recommends A. **Not decided.**
- **§9.1: evaluator API shape** — no longer pre-committed to a required
  positional `Journal` parameter; implementation planning should weigh
  a keyword-only parameter, a context object, or pre-evaluation
  materialization. "Fail loudly, never silently narrow" is a binding
  constraint regardless of shape. **Not decided.**
- **§9.1: is the commodity-tag substrate (new `Journal.
  declared_commodity_tags` field + `commodity`-directive comment
  capture in the parser) in scope for this phase, or a prerequisite
  sub-phase** (mirroring how Phase 4 itself was split out)? No
  recommendation given either way. **Not decided.**
- **§9.2: `accounts` command mode** — recommendation **reversed** this
  amendment: now recommends replicating hledger's account-inherited-
  only matching mode (previously recommended diverging to uniform
  matching). **Not decided.**
- §9.3 (helper visibility) — default changed to **private**; not a
  blocking gate, just the starting assumption.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/23-tag-query-matching-design.md`
  — the amended design; §2.6/§2.7 hold the new commodity-tag/precedence
  evidence, §9 the (partly re-weighed) unresolved questions, §17 the
  current approval list.
- `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md` — original retro
  plus a dated addendum covering this correction round.
- `ledgerkit/parser.py:1288-1299` — confirmed, by direct read, that the
  `commodity` directive's comment is actively discarded
  (`_strip_directive_comment`) — the substrate gap's exact location.
- `/home/cormac/projects/hledger/hledger/hledger.1:3550-3556` — the
  "Commodity tags" manual section this amendment is grounded in.
- `hledger/Hledger/Cli/CliOptions.hs:642` — `autopostingtags = not $
  command == "print" && moutputformat == Just "beancount"` — resolves
  why account-tag inheritance already worked in the original document's
  tests despite the library's own `False` default.

## Blockers / Open Questions
All five items in the amended §17 — see "Decisions In Flight" above.
Nothing else blocking.

## What NOT To Revisit
- Don't re-derive the commodity-tag propagation mechanism or the
  same-name precedence finding — both are now executable-verified
  (five-transaction fixture, pinned binary) and source-traced precisely
  (exact file:line citations throughout §2.6/§2.7 of the design doc).
- Don't assume "posting tags override account tags override commodity
  tags" means exclusion/shadowing for query matching — executable
  evidence directly contradicts that literal reading; all differently-
  valued same-named tags from every source remain simultaneously
  matchable. This was the single most counter-intuitive, and most
  carefully verified, finding in this correction round.
- Don't silently pick any of §17's items and proceed — all are explicit,
  named human-decision gates, unchanged in kind from the original
  document, some reversed or softened in their stated recommendation.
- Don't treat this correction as an implementation defect — no
  `ledgerkit/`/`tests/` code existed when the gap was found. It's a
  design-review correction, caught exactly where this process's own
  Step 3 gate exists to catch it.
- Don't re-run the context-curator dispatch — its report stands; this
  amendment extended it with a fixture-verified gap it hadn't covered,
  not a re-run of what it already covered correctly.

## Recent Git State (before this response's commit, if any)
7a74056 docs: Stage C Phase 6 -- tag: query-matching context curation + design
f397d85 docs: Stage C Phase 5A -- adopt CodeCompass v1 development workflow
eecb8a9 docs: amend Stage C Phase 5A plan per review findings
c6e4b1e docs: plan Stage C Phase 5A -- CodeCompass workflow adoption
c6168b2 docs: Stage C Phase 5, commit 3/3 -- independent verification + closeout

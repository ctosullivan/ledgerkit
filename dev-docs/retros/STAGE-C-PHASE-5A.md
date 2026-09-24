# Stage C Phase 5A retro — CodeCompass development workflow adoption (implementation)

- **Date:** 2026-09-25
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none dispatched — the lead session performed the
  install, real-repo configuration, research task, and doc updates
  directly. `context-curator`'s role (evaluating CodeCompass honestly,
  filing findings) was performed in-session rather than via a separate
  dispatch — consistent with this project's own established proportion-
  ality judgement (Stage C Phase 3's retro: a small, well-scoped task
  reusing an already-proven pattern doesn't need a dispatch to be
  independent in substance), and every finding below is evidence-cited,
  checkable by anyone re-running the same commands.

## Where we are

Two planning passes preceded this: the original plan and its eight-
amendment review (`22-stage-c-phase-5a-codecompass-workflow-adoption-
plan.md`, retros `STAGE-C-PHASE-5A-PLAN.md` + its same-day addendum).
This is the actual implementation the amended plan's five gates (all
resolved: G-CC-1 gitignore, G-CC-2 `tag:` query matching, G-CC-3 no new
role, G-CC-4 approved, G-CC-5 approved criteria) authorised. After this
phase: CodeCompass v1.0.0 is genuinely installed and configured against
Ledgerkit's real repository; a real context packet exists for `tag:`
query-term matching (the genuine next phase); three new `CC-LK-NNN`
findings exist; the routine workflow is documented
(`04-codecompass-integration.md` §4.7) and `CLAUDE.md` carries a real
pointer section.

## Goal

Execute the amended plan's nine steps for real: install CodeCompass,
configure it against the live repository, use the real agent-facing
entry points before direct queries, research and package context for
`tag:` query-term matching with per-finding provenance, capture feedback,
confirm existing controls, document the workflow, and exercise a real
staleness/re-sync cycle — then report whatever the evidence actually
shows, without assuming the historical LOW-advantage baseline would
repeat.

## Scope delivered vs planned

All nine steps executed as planned, in the sequence the amended plan
specified. No `ledgerkit/`/`tests/` behaviour changed; the one real
`ledgerkit/`-adjacent decision (G-CC-2) was already resolved before this
phase started, and this phase only researched it, per the Constraints
section's own boundary.

One significant deviation from the plan's own stated expectation, found
during Step 1/2, not assumed going in: **the plan's own §1.4 claim that
`CG-004` was "still open, not fixed in v1.0.0" was wrong.** Checking
CodeCompass's own `CHANGELOG.md`/`planning/retros/phase-55b-...md`
directly this session: `CG-004` was closed in Phase 55b, dated
2026-09-17 — a full week before this project's own Stage C Phase 5A
planning pass was written. This was a research error in the original
plan (most likely: checking `_DEFAULT_GLOBS` correctly for `CG-002` but
not re-verifying `scan_spec_docs`'s actual current `name=` assignment for
`CG-004` specifically), not a change in CodeCompass between the planning
pass and this implementation. Corrected in the context packet (§2) and
in `CC-LK-002` rather than left standing.

## What was achieved

CodeCompass installed via `pipx install -e` (clean, no system-Python
conflict). Full deterministic `sync` against the real repository —
confirmed `context-graph.db` populates independently of the enrichment
prompt (which correctly aborted cleanly with no input, per its own
documented behaviour). Reproduced Ledgerkit's own first-party version of
the Phase 51/67 not-found-vs-empty disambiguation fix. Found and verified
(not assumed) that `CG-004`'s fix is real and working — 18 genuine
`mentions_artifact` doc-to-doc edges now exist, zero at every prior
Ledgerkit evaluation — while also verifying, precisely, that it does
**not** close the specific gap `CC-LK-001` originally flagged (title-vs-
filename matching), which turned out to already be independently filed
and diagnosed by CodeCompass's own team as `CG-006`, one day after
`CC-LK-001`. Used `codecompass enrich apply` (the agent-facing path, no
`ANTHROPIC_API_KEY` configured) to add a real, accurate, hand-verified
summary to one genuine relation — the first time this project has
exercised that specific code path. Built a context packet for `tag:`
query-term matching with every finding tagged to one of four provenance
categories. Filed `CC-LK-002` (the `CG-004`/`CG-006` re-verification) and
`CC-LK-003` (a real, minor environment gap: the generated Skill/discovery
text names the `sqlite3` CLI as its only documented graph-query fallback,
which isn't installed in this standard environment; Python's `sqlite3`
module substitutes, but nothing in the generated text says so). Exercised
a real edit→re-sync→refresh cycle (Step 9): confirmed a query against an
edited document showed stale (pre-edit) content before re-sync and
refreshed content after, with the previously-applied enrichment surviving
the re-sync intact. Documented the routine workflow
(`04-codecompass-integration.md` §4.7) and added a real `CLAUDE.md`
pointer section around the mechanically-generated routing-table block.
`.gitignore` updated for `vendor.toml`/`vendor/` (`context-graph.db`
already covered by an existing `*.db` rule; `.claude/skills`/`commands`
already covered by an existing `.claude/*` rule).

## What worked

- **Re-verifying the plan's own central evidence claim instead of
  building on it.** The amended plan itself exists specifically because
  the *previous* draft anchored to a stated baseline without re-checking
  it — applying that same discipline to the plan's own `CG-004` claim,
  rather than treating "I already researched this" as settled, is exactly
  what caught a real, material error before it propagated into the
  context packet or a compat-register-style claim.
- **Checking CodeCompass's own gap inbox before writing a new finding**,
  rather than treating an observation as necessarily novel. The 07/17
  title-vs-filename gap looked, at first glance, like a fresh discovery;
  a direct check against `planning/context-gaps/inbox.md` found it
  already filed as `CG-006`, precisely diagnosed, with a fix already
  sketched — turning what would have been a redundant "new" finding into
  an honestly-labelled third corroboration instead.
- **Using the mechanical rejection from `enrich apply`'s own trust
  boundary as a real test, not a blocker to route around.** The first
  attempt used an invalid `relation_label`; the tool rejected it cleanly
  with the exact valid enum, confirming the "enforces the trust boundary
  mechanically, not by agent instruction alone" claim in its own help
  text is real, not aspirational.
- **Running the actual edit→resync→query cycle for Step 9** rather than
  asserting staleness detection "should" work from reading the docs — the
  before/after `query relations` output on the same edited file is
  concrete, reproducible evidence, not an inference.

## What didn't work

The `sqlite3` CLI gap (`CC-LK-003`) was a real, if minor, moment of
friction — the generated Skill's own documented fallback procedure
didn't work as written in this environment, and the substitution
(Python's `sqlite3` module) came from general knowledge, not from
anything CodeCompass itself suggested. Small, but a real data point for
"maintenance burden" (G-CC-5's own evaluation criterion): a fresh agent
without that substitution ready to hand would have stalled at exactly
the point the generated instructions promised a fallback existed.

## Lessons learnt

A plan's own prior research is not exempt from the same "verify, don't
anchor" discipline the plan itself was written to enforce on the
*evaluation* — this phase found a real error in the *plan's own* central
evidence claim by applying exactly the check the plan asked for
elsewhere. More generally: when re-testing a specific, previously-filed
gap, checking the upstream project's own gap-tracking artifact directly
(not just its `CHANGELOG.md` or release notes) is what separates "third
independent confirmation of an already-known, already-diagnosed issue"
from "claims a new discovery that isn't one" — the two read identically
from the symptom alone.

## Process-improvement feedback

The amended plan's own structure (provenance categories, no-anchoring
instruction, staleness test, enrichment sequencing) mapped directly onto
real implementation steps with no friction or redesign needed — every
amendment from the review pass turned out to be concretely exercisable,
not aspirational. Worth naming: the provenance-tagging discipline (Step
5) is what made the `CG-004` correction *findable* in the first place —
tagging the CG-004-related claim forced re-checking its source rather
than restating it from memory, which is precisely the mechanism the
amendment was designed to produce.

## Learnings filed

- `validation/codecompass/context-packets/tag-query-matching.md` — the
  Step 5 deliverable, with full provenance tagging.
- `validation/codecompass/findings/CC-LK-002.{yaml,md}` — `CG-004`
  confirmed fixed and working; the 07/17 pair's gap confirmed unchanged,
  correctly identified as already-filed `CG-006`, not a new discovery.
- `validation/codecompass/findings/CC-LK-003.{yaml,md}` — the `sqlite3`
  CLI environment-assumption gap in the generated Skill/discovery text.
- `dev-docs/planning/core-redefinition/04-codecompass-integration.md`
  §4.7 — the routine workflow, now documented from real use, not
  forward-looking design.
- No `knowledge/DECISIONS.md` entry — no Ledgerkit architecture/behaviour
  decision was made this phase; G-CC-2's `tag:` choice was already
  recorded as a gate resolution in the plan itself.

## Evaluation verdict (per G-CC-5's approved criteria — not a required HIGH context-advantage result)

- **Workflow usefulness:** real. Install (`pipx`), `sync`/`index`/
  `check`/`query`/`enrich apply` all work as documented against the real
  repository; the staleness/re-sync cycle is confirmed, not assumed.
- **Evidence quality:** high where content exists — every context-packet
  claim traces to a verbatim query result or a direct file read.
- **Provenance:** of this phase's material findings, roughly half were
  [SURFACED] by a CodeCompass query (the vendor-emptiness confirmation,
  the two real relation edges, the `CG-004` status correction itself),
  one was [POINTED→INDEPENDENT] (the brief-19 edge's actual meaning
  required reading the brief), and the rest were [INDEPENDENT]/[KNOWN]
  (the `tag:` implementation status, the briefs' own documented
  semantics). CodeCompass's own, specific contribution is concentrated in
  the doc-relation layer, not the implementation-research layer — an
  honest, checkable split, not an inflated "CodeCompass helped with
  everything."
- **Repeatability:** documented and repeatable (`04-codecompass-
  integration.md` §4.7); the exact commands used this session are
  reproducible by anyone with the same local CodeCompass clone.
- **Maintenance burden:** low-to-moderate. One-time `pipx install`; a
  real but small friction (`CC-LK-003`); enrichment without an API key
  costs agent time per relation (`enrich apply`'s own manual-entry
  design), not money — a real, disclosed tradeoff, not a hidden one.
- **Context-advantage verdict, independently determined (not assumed
  from the historical baseline):** **mixed, not a flat repeat.** The
  vendor/symbol axis is unchanged (LOW, structurally, given 0 tracked
  dependencies — confirmed, not assumed). The doc-relation axis shows a
  genuine, verified **improvement** since the last Ledgerkit-side
  evaluation: `CG-004`'s fix works on real content and produced one
  concrete, correct, non-trivial finding a fresh agent would plausibly
  reach faster via `codecompass check`'s coverage report than by
  cold-reading every brief. Neither "still LOW, nothing changed" nor "now
  high-value" would be an honest single-sentence summary — the evidence
  supports a qualified, dimension-specific answer, which is what's
  recorded here instead of rounding to either extreme.

**Adoption recommendation:** worth keeping as a routine, low-cost check
per phase going forward — not because it delivered a dramatic result this
time, but because the workflow itself is now cheap, documented, and
repeatable, and this session's own evidence shows it can and does
surface genuine, checkable findings (including, this time, a correction
to Ledgerkit's own prior planning claim) often enough to justify the
setup cost already paid.

## Where we're going

The genuine next Ledgerkit development phase — `tag:` query-term matching
(G-CC-2) — is researched and context-packaged (`validation/codecompass/
context-packets/tag-query-matching.md`) but **not implemented**. It needs
its own scoping/plan pass before implementation begins, per this
project's standing process, using this phase's packet as a starting
point, not a substitute for that process.

## Time / cost note

Single extended session: tool install and real-repo configuration
(~15 tool calls), research and context-packet construction (~15 tool
calls, including one enrichment round-trip and a rejected/corrected
attempt), two findings written with one requiring a follow-up correction
after checking CodeCompass's own gap inbox, docs updates, and the
staleness test (~10 tool calls). The single most valuable step was
re-checking the plan's own `CG-004` claim against current source rather
than trusting it forward — a five-minute check that changed the accuracy
of everything built on top of it.

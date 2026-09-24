# Stage C Phase 5A retro — Planning (CodeCompass development workflow adoption)

- **Date:** 2026-09-24
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** none — direct inspection and planning by the lead
  session; no agent dispatch warranted for a read-only planning pass
  (consistent with the `STAGE-C-PHASE-2-PLAN.md`/`STAGE-C-PHASE-5-PLAN.md`
  precedent for a request this size and shape)

## Where we are

The user handed over a fully-specified phase brief — objective, goals,
evaluation criteria, constraints, and exit criteria for "Stage C — Phase
5A: CodeCompass Development Workflow Adoption" — with an explicit
instruction to insert it into the roadmap immediately before the
currently-planned next Ledgerkit phase and to follow the project's normal
planning/implementation/verification/review/retro process. This phase is
the planning pass: `22-stage-c-phase-5a-codecompass-workflow-adoption-
plan.md`, plus the `ROADMAP.md` insertion the user explicitly requested
directly (not gated behind the plan's own approval, since "insert the
roadmap phase" was a standalone imperative, not a proposal). Full
implementation is not started.

## Goal

Produce a concrete, evidence-grounded plan for adopting CodeCompass v1
into Ledgerkit's normal development workflow — checking, before writing
anything, whether CodeCompass v1 has actually shipped, what state (if
any) already exists for Ledgerkit in this environment, and what
CodeCompass's own team has already learned from evaluating itself against
Ledgerkit, rather than treating the brief's implied premises (a fresh v1
release, a blank integration slate, an already-scoped next Ledgerkit
phase) as given.

## Scope delivered vs planned

All nine required planning outputs implied by the user's brief and this
project's own planning-pass convention were delivered: current-state
assessment, an honestly-reframed objective, a roster analysis, eight
detailed phase steps mapping every one of the user's goals, an evaluation
design, constraints cross-checked against Ledgerkit's own existing rules,
five human-decision gates, and a Definition of Done mapped explicitly to
the user's seven exit criteria. The `ROADMAP.md` insertion itself was
delivered as directly requested, not treated as conditional on the plan's
own approval.

Three of the brief's own implicit premises turned out not to hold, found
only by checking directly rather than assumed:

1. **"Configure CodeCompass... using the released v1 architecture"**
   assumes v1 exists — checked, and it does: tag `v1.0.0`, commit
   `4c09185`, a genuinely fresh release. This premise held.
2. **The brief's framing implies integration is new/unstarted work** —
   checked directly (`.claude/skills/codecompass/SKILL.md`'s git history,
   `context-graph.db` presence, `codecompass` CLI installation) and
   confirmed: nothing is actually configured yet, despite a stub skill
   file existing on disk. This premise held too, but only after checking
   — the stub file alone could easily have been mistaken for partial
   completion.
3. **"Use the existing next planned Ledgerkit phase"** assumes one is
   already scoped — checked against `ROADMAP.md`/Phase 5's own retro and
   found **false**: no phase is currently scoped, only named, deferred
   candidates. This is the one premise that did not hold, and the plan
   resolves it explicitly (§1.5, §5 Step 3, gate G-CC-2) rather than
   silently picking one or silently ignoring the gap.

The largest single finding, not implied by the brief at all and only
surfaced by reading CodeCompass's own repository directly: CodeCompass
has already run roughly ten phases of its own work using Ledgerkit as its
**principal external reference project** for v1 validation, including a
live re-confirmation dated the exact day this plan was written, and has
already written its own adoption blueprint specifically for Ledgerkit.
This is not incidental colour — it is load-bearing evidence that
reshapes what "success" for this phase should even mean (§3).

## What was achieved

A plan grounded in reading, not assumption: CodeCompass's `README.md`,
`pyproject.toml`, three `v1-redefinition/` planning documents in full,
a 679-line, multi-dated findings file (read to its most recent section,
not just its opening), and the actual current state of
`spec_docs.py::_DEFAULT_GLOBS`/`scan_spec_docs` (confirming one known fix
persists and one known gap remains open, independently of CodeCompass's
own self-report). Cross-checked against Ledgerkit's own existing
`04-codecompass-integration.md`/`05-context-curator.md`/`.claude/
agents/*.md`, finding strong, independently-converged alignment rather
than needing to design anything new. A concrete, checkable finding (no
new agent role is needed — Ledgerkit's existing 7-role roster already
exceeds CodeCompass's own recommended 5-role minimum) replaces what could
otherwise have been unfounded roster-expansion busywork. Five explicit
gates, none pre-resolved.

## What worked

- **Reading `findings.md` all the way to its most recent section, not
  stopping at the first gate.** The file accumulates dated sections
  across ten phases; stopping at GATE DB (Phase 47, the FAIL results)
  would have produced a plan that either overstated the risk (treating
  fixed issues as still-open) or understated it (missing `CG-004`, which
  is still open). Reading to Phase 67's section — dated today — was what
  let the plan's central reframing (§3) be evidence-backed rather than
  speculative.
- **Independently re-checking a claim from CodeCompass's own findings
  file against the actual current source**, rather than taking "the fix
  still holds" on trust. `grep`ing `_DEFAULT_GLOBS` and `scan_spec_docs`
  directly confirmed both the fixed and the still-open item exactly as
  CodeCompass's own Phase 67 section claimed — cheap insurance, and
  exactly the discipline Ledgerkit's own `compat-differential-tester`
  role exists to apply when checking claims about *its* own domain
  (hledger); applying the same standard to a claim about CodeCompass's
  own domain was a natural, low-cost extension of an existing habit.
- **Checking the roster against the actual `.claude/agents/` directory
  contents** rather than assuming a gap existed because the task
  mentioned specific role names. Found the existing roster already
  covers the recommended minimum — a genuinely useful negative result
  (nothing to add) rather than inventing a plausible-sounding but
  unjustified new role.

## What didn't work

Nothing failed in this planning pass. One judgement call worth naming:
the user's brief reads as a finished, ready-to-execute specification, and
there was real pull to treat it as authorization for immediate full
implementation (install CodeCompass, run it, execute the chosen next
task) rather than a planning pass first. Resolved by following this
project's own direct precedent — the original CodeCompass-adoption
request that became Stage C Phase 2 was itself a single detailed message
of comparable size and shape, and it produced a planning-pass response
first (`STAGE-C-PHASE-2-PLAN.md`), with implementation following only
after that plan was reviewed. Applying the same discipline here, rather
than reading "follow the normal process" as licence to skip the planning
half of that process, seemed the more defensible reading — but it is a
judgement call, not a certainty, and is flagged as such below.

## Lessons learnt

When an external project's own repository contains material written
*specifically about* the adopting project (here: CodeCompass's
`ledgerkit-plan.md`, `adoption-blueprint.md`, and a Ledgerkit-specific
`findings.md`), that material is not background reading — it is
authoritative, load-bearing evidence that should reshape the plan's own
central framing before anything else gets written, the same way this
project's own `hledger-researcher` role treats hledger's actual source
and manual as authoritative over assumption. The generalisable version:
before planning how to adopt an external tool, check whether that tool's
own project has already produced material *about* adopting it into your
specific project — the answer may already exist, tested, dated, and
disconfirming of the plan's implicit premises.

## Process-improvement feedback

No friction with Ledgerkit's own process — the existing `dev-docs/
planning/core-redefinition/` numbering, the existing `.claude/agents/`
roster, and the existing `04-codecompass-integration.md`/`05-context-
curator.md` groundwork all slotted the new plan in without needing new
scaffolding invented, mirroring Phase 5's own planning-pass experience.
One thing worth flagging for the user directly, not just recorded here:
this plan's central finding (§1.4 — a consistently LOW, structurally-
explained context-advantage ceiling, re-confirmed as recently as today)
means the most likely honest outcome of the full phase, once executed,
is a similar result — not a failure of this adoption effort, but the
accurate, already-well-evidenced shape of what CodeCompass currently
offers a zero-runtime-dependency project like Ledgerkit. Worth the user
knowing this going in, so the retro isn't read as a disappointment
relative to an expectation the evidence never actually supported.

## Learnings filed

None to `knowledge/*.md` this phase — every finding here is either
CodeCompass-project-specific (lives in the plan document itself, §1,
where anyone acting on it will read it first) or not yet a settled
decision (the five gates are explicitly open).

## Where we're going

Stage C Phase 5A itself (the actual CodeCompass installation, real-repo
configuration, chosen-task research, context-packet generation, feedback
capture, and workflow documentation, per the plan's §5 phase steps) is
planned but **not started** — it awaits resolution of all five gates in
§8, per this project's standing process. Once resolved, the plan's own
§5 Step 3 (choosing the genuine next-task candidate, recommended: `tag:`
query-term matching) determines what Ledgerkit's actual next feature
phase becomes after Phase 5A closes.

## Time / cost note

Single response: repository inspection across two local projects
(Ledgerkit and CodeCompass), reading roughly a dozen CodeCompass-side
planning/findings documents (several in full, not skimmed), one direct
source-code check to independently confirm a claim rather than trust it,
then the plan document itself. The `findings.md` read (679 lines, read to
its most recent, dated-today section) was the single largest and most
valuable piece of the work — it is what turned this plan from a generic
"how to adopt a dev tool" document into one grounded in the specific,
current, already-evidenced reality of this exact tool-project pairing.

---

## Addendum (2026-09-24, same day) — amendment round after user review

The user reviewed the plan above and directed eight targeted amendments
before implementation, all within this same planning-only activity (no
implementation had started, so this is recorded as an addendum to this
retro, not a new dated retro file, per this project's "never rewrite a
past retro, only add" rule interpreted as: append, don't fork, while the
underlying phase hasn't advanced past planning).

**What changed:** §10 of the plan document itself carries the full,
itemised list. In summary: real agent-facing entry points (Skill,
`/discovery`) must be exercised before direct CLI queries; every
context-packet finding must carry a four-category provenance tag;
language predicting or normalising a repeat LOW-advantage result was
removed from §§1.4/2/3/6, replaced with an explicit instruction to
independently determine improvement/regression/unchanged; a lifecycle/
staleness re-sync test was added (Step 9); enrichment was resequenced
deterministic-first with both API-backed and `enrich apply` paths
in scope, never manufactured; CodeCompass's release state was
independently re-verified (a real, live disagreement was found between
its `README.md` and its own tag/PyPI state — already self-corrected
upstream one commit later, so no new finding was needed, but the
re-check is now a standing part of Step 1); gate G-CC-2 was resolved to
`tag:` query-term matching; G-CC-1/3/4/5 were retained with refined
wording.

**What this amendment round tested about the original plan:** whether
its central finding (§1.4's LOW-advantage baseline) had been *reported*
honestly versus *treated* as a foregone conclusion for this phase's own
result. Re-reading the original draft under that lens found real
anchoring language — "a repeat... outcome is the anticipated, not
disappointing, result," "this phase is not expected to demonstrate..." —
that, while not factually wrong (the baseline evidence is real and was
accurately summarised), could have shaped how the actual Phase 5A
evaluation gets read and conducted once implementation starts: an
evaluator primed to expect LOW is less likely to notice a genuine
improvement, and more likely to under-scrutinise a result that happens
to match the prediction. This is the same class of risk the user's
original brief warned against ("do not manufacture favourable results")
applied in the opposite direction — an unfavourable-looking result can be
just as manufactured, by expectation-setting, as a favourable one can be
manufactured by convenient question selection.

**Lesson, generalisable beyond this phase:** citing strong prior evidence
accurately is not the same as staying neutral about what a *new*
evaluation will find. The fix here was mechanical and checkable — remove
every sentence that states or implies the outcome before the evidence
exists, keep every sentence that states the *prior* evidence accurately
as prior evidence — but it required a deliberate second pass looking
specifically for that pattern, not something the first draft's own
internal logic would have caught unprompted.

**Consistency review, performed as directed:** confirmed and recorded in
the plan document's own new §10 — Phase 5A remains integration/
evaluation-only (no `ledgerkit/` behaviour change in any step, including
the new Step 9); the `tag:` phase (G-CC-2, now resolved) remains the
first genuine implementation test, not absorbed into Phase 5A itself;
CodeCompass-derived claims remain subordinate to Ledgerkit's existing
tests/compatibility research/`knowledge/DECISIONS.md`/review process,
unchanged by the amendment round; negative/neutral findings remain an
explicitly acceptable outcome, now stated more precisely (§6, G-CC-5)
than the original draft's framing managed.

No implementation performed this addendum — still planning only. Next:
present the amended plan to the user; implementation awaits resolution
of G-CC-1/3/4/5.

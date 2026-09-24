# 22. Stage C Phase 5A plan — CodeCompass development workflow adoption

Planning only. No `ledgerkit/`/`tests/` code touched, no CodeCompass
installation/configuration performed yet. **Amended 2026-09-24** (same
day, before implementation) per user review — see §10 for the full
amendment summary and consistency review. Do not begin implementation
until the remaining open gates in §8 are resolved (G-CC-2 is now
resolved; G-CC-1/3/4/5 remain open) — matching this project's own
precedent for a request this size and shape (`18-stage-c-phase-2-
codecompass-adoption-plan.md`/`STAGE-C-PHASE-2-PLAN.md`: the original
CodeCompass-adoption request was itself a single detailed message that
produced a planning-pass response first, not immediate implementation).

## 0. Pinned revisions

- Ledgerkit: `c6168b2` (Stage C Phase 5 close)
- CodeCompass: `9ce200fcca1d894f8d42ffea5996e30ba054ab05` (re-verified
  during this amendment round, superseding the original pin at
  `4c09185`; **tag `v1.0.0`** still points at the same release — the
  newer commits are Phase 70's own closeout, see §1.1). Local clone:
  `/home/cormac/projects/codecompass`.
- hledger: unchanged, `1.52.4` / `33fa849e7ae841968bd21c427094c4fb4a4ec38d`.

---

## 1. Current-state assessment

### 1.1 CodeCompass v1.0.0 is real, current, and freshly released — release-state independently verified, not read once and trusted

`git tag` on the local clone shows `v1.0.0`; `pyproject.toml` names the
distribution `codecompass-context`, version `1.0.0`. CodeCompass's own
`README.md` describes v1 as a **redefined** milestone — not a packaging
checkpoint but a "product-validation milestone: CodeCompass developed
agent-led, validated against real external reference-project work,
improved from that evidence, and released only after a blank-slate
documentation reconstruction and an independent audit." That validation
work is not abstract — **Ledgerkit is the primary reference project it
was validated against** (§1.3).

**Re-verified during this amendment round** (per the instruction to
verify authoritative release state rather than resolve any disagreement
silently): at the time of the original planning pass (pinned `4c09185`),
`README.md`'s own "Status" section still read *"Pre-release, not yet
published"* despite the `v1.0.0` tag and PyPI-published `codecompass-
context` package already existing — a live, checkable disagreement
between CodeCompass's own documentation and its own release metadata.
Re-checking now (pinned `9ce200f`, one commit later): CodeCompass's own
Phase 70 per-phase drift audit independently caught exactly this and
fixed it — `README.md` now correctly reads *"Released. `codecompass`
`1.0.0` is published on PyPI..."*, and CodeCompass's own `CHANGELOG.md`
records the fix under `[Unreleased] > Fixed`. **No disagreement remains
as of this re-check; no new CodeCompass documentation finding needs
filing from Ledgerkit's side for this specific gap** — it was found and
resolved upstream before Ledgerkit's own review reached it. This is
recorded here rather than silently updated without comment, per the
instruction: had CodeCompass's own audit not already caught it, this
would have been filed as a CodeCompass documentation finding (§6). No new
gate is warranted for this specific, already-resolved gap; re-running
this same verification is instead a standing part of Step 1 (§5) —
release state should be re-checked at whatever commit Phase 5A actually
executes against, not assumed to still match this planning pass's
snapshot, and any *future* disagreement found should be filed the same
way (§6, never silently resolved).

### 1.2 Nothing is actually configured for Ledgerkit yet, despite appearances

`.claude/skills/codecompass/SKILL.md` already exists in this repo — but
inspection shows it is an untracked, un-committed stub (`git log` on
`.claude/skills/` is empty): "0 tracked, 0 enriched" vendors, no
`context-graph.db` anywhere in the repo or its parents, and the
`codecompass` CLI is not installed in this environment (`which
codecompass` empty, `pip show codecompass`/`codecompass-context` both
report not-installed). This is the pre-`init` template shape, not
generated output from a real run. **Goal 1 of this phase (configure
CodeCompass against the real repository) is genuinely unstarted work,**
not something to discover has already happened.

### 1.3 This is not a blank slate — CodeCompass has extensively evaluated itself against Ledgerkit already

`/home/cormac/projects/codecompass/planning/reference-projects/ledgerkit/`
and `v1-redefinition/{adoption-blueprint,ledgerkit-plan}.md` hold roughly
ten phases (44–55, 59, 61, 63d, 64–67) of CodeCompass's own work using
Ledgerkit as its principal external validation subject, re-confirmed as
recently as **today, 2026-09-24** (Phase 67's own re-run, cited below).
Treating this phase as "first contact" between the two projects would be
wrong and would duplicate work already done and written down:

- **`v1-redefinition/adoption-blueprint.md`** — CodeCompass's own,
  already-written adoption blueprint **specifically for Ledgerkit**
  (Gate G13, Phase 43e), generalised from CodeCompass's actual working
  practice, not invented fresh. Recommends a **5-role minimum starting
  roster**, mapped concretely onto Ledgerkit's governance shape.
- **`v1-redefinition/ledgerkit-plan.md`** — the reference-project plan
  that scoped Phases 45–55 against Ledgerkit specifically, including the
  explicit hard boundary: *"No feature is added to Ledgerkit to make
  CodeCompass easier to evaluate... CodeCompass is not the hledger
  black-box experiment runner."*
- **`reference-projects/ledgerkit/findings.md`** (679 lines, multiple
  dated gate sections) — the full evaluation history, summarised in §1.4.
- Ledgerkit's own **`dev-docs/planning/core-redefinition/
  04-codecompass-integration.md`** (Stage A) and **`05-context-
  curator.md`** already anticipated almost all of this independently —
  the deterministic/agent-suggested/verified/rejected edge-state model,
  the "Ledgerkit never mutates CodeCompass's graph, CodeCompass never
  mutates Ledgerkit's tree" boundary, and reuse of CodeCompass's own
  `context-quality-evaluation.md` report shape verbatim. This is a
  genuinely reassuring finding: **the two sides' independent designs
  converged**, and Phase 5A's job is largely to *activate* what's already
  specified — install the tool for real, run it against the real repo,
  update stale "pre-release" framing to "v1.0.0 released" — not to design
  anything from scratch.

### 1.4 The honest context-advantage ceiling is already established, current, and disclosed by CodeCompass's own team — not a hypothesis this phase needs to rediscover

This is the single most important finding for scoping this phase
honestly, and it directly answers the user's own "do not manufacture
favourable results" instruction before any new evaluation even runs:

| Gate | Phase | Result |
|---|---|---|
| GATE DB | 47 | 5 evaluated instances, **2 formal FAILs** (both: `query relations` returned a confidently-wrong "not found" for real, load-bearing `dev-docs/**` files — root cause: `spec_docs.py::_DEFAULT_GLOBS` had no `dev-docs/**/*.md` entry) |
| GATE DC | 51 | Confirmed the Phase 49 fix closed both FAILs (now honest empty-relations, not false "not found") — but advantage stayed **LOW**: 0 tracked vendors (Ledgerkit's own zero-runtime-dependency design) means `doc_relations_edges` has nothing to relate a doc to, "regardless of the doc's actual content" |
| Phase 54 | 54 | A deeper, real experiment (ingesting hledger reference material into a scratch Ledgerkit copy for a genuine `tag:`-semantics research task) — detection worked, but relation was **negative** (zero edges produced, a structural gap: `spec_docs.py::scan_spec_docs` never populates `doc_artifacts.name` for `spec_doc` rows, so mention-detection has nothing to match against — filed as `CG-004`, **still open, not fixed in v1.0.0** per this session's own source check) |
| **Phase 67** | 67, **2026-09-24 (today)** | Re-confirmed live against a fresh Ledgerkit clone at `c6168b2` — the fix still holds, generalises correctly — but verdict is unchanged: **PASS WITH GAPS / LOW advantage**, explicitly still below CodeCompass's own roadmap's stated MODERATE+ target, and explicitly recorded as CodeCompass's own justification for shipping v1.0.0 at this level anyway (a disclosed limitation, not a hidden one) |

**This session independently re-confirmed the structural cause still
holds**: `_DEFAULT_GLOBS` in the current `spec_docs.py` does include
`dev-docs/**/*.md` (the Phase 49 fix persists), but `scan_spec_docs`'s
`doc_artifacts.name`-population gap (`CG-004`) is unresolved — checked by
reading the source directly, not taken on CodeCompass's own word.

**Implication — amended:** the table above is retained as **historical
baseline evidence**, not as a prediction this phase is bound to reproduce.
The structural explanation (zero tracked runtime dependencies, `CG-004`
still open) is a plausible *hypothesis* for why a similar result might
recur — it is not a substitute for actually running Phase 5A's own
evaluation and observing what happens. **The evaluator must not assume
the same outcome.** This phase's own evidence (§6) is what determines
whether the result is an improvement, a regression, or unchanged
relative to the baseline table — including the live possibility that
CodeCompass's substantial work since Phase 67 (enrichment paths, the
agent-facing `enrich apply` workflow, the real Skill/`/discovery` entry
points this amendment specifically requires testing — §5 Step 4) moves
the result in either direction. §3 reframes the phase's objective around
*independently measuring* this, not around a predetermined expectation
either way.

### 1.5 There is no already-scoped "next Ledgerkit development phase" to use as the genuine task

The user's brief assumes one exists ("use the existing next planned
Ledgerkit phase"). Checking `ROADMAP.md`/`dev-docs/retros/
STAGE-C-PHASE-5.md` directly: Stage C Phase 5's own retro explicitly
states *"`tag:` query-matching... `cur:`, `PythonRegex`, `Query`-as-shim,
and a standalone `--depth` CLI flag remain unscoped/deferred... the next
phase should get its own explicit scoping pass."* Nothing is currently
scoped as "the next phase" — only named, un-prioritised candidates. This
is a real gap, not a detail to paper over (§5, Step 3, and gate
G-CC-2 resolve it).

---

## 2. What this phase should not re-litigate or duplicate

- **Re-deriving the historical baseline table itself** (§1.4) — already
  established across four gates, the most recent dated today; no need to
  re-read `findings.md` from scratch to reconstruct it. What Phase 5A's
  own evaluation (§6) must **not** do is treat that table as a forecast
  of its own result — the actual outcome (better, worse, or unchanged)
  is this phase's own evidence to establish, independently, not to
  assume from the table.
- **The adoption-blueprint's roster-mapping exercise** — already done
  (§4); this phase applies it, checked against Ledgerkit's actual current
  `.claude/agents/` roster, not re-derives it.
- **`CG-002`** (the `dev-docs/**` glob gap) — fixed, independently
  re-confirmed live twice (Phase 51, Phase 67) and a third time by this
  planning pass's own source read. No action needed.
- **`CG-004`** (the `doc_artifacts.name` gap) — open, but it is
  CodeCompass's own code, not Ledgerkit's to fix. Ledgerkit's role is
  feedback (§4, §7's constraint on this), not a silent workaround.

---

## 3. Objective — integrate the workflow, measure this phase's own result independently

The user's stated objective — integrate CodeCompass v1 into Ledgerkit's
normal development process and establish a repeatable, evidence-backed
workflow — stands unchanged. §1.4's historical baseline (consistently
LOW context advantage, most recently re-confirmed today, for a
structurally-explained reason) is retained as prior evidence an evaluator
should be aware of, **not** as an expected or acceptable-by-default
result for this phase. **The evaluator must independently determine,
from this phase's own observed evidence, whether the result is an
improvement, a regression, or unchanged relative to that baseline** —
never assumed either way before the evidence is in. Concretely: if
Steps 1-6 (§5) surface something the baseline evaluations didn't (a real
possibility, given this phase tests real agent-facing entry points —
Skill/routing context, `/discovery`, `enrich apply` — that no prior
Ledgerkit-facing evaluation exercised end-to-end), that is a genuine
result to report as such, not discounted because prior gates found LOW;
equally, if the result matches the baseline, that should be reported
plainly as confirmation, not treated as a foregone conclusion reached
without actually running the evaluation.

Three things are genuinely new relative to every prior evaluation, and
are this phase's real contribution regardless of which way the
context-advantage verdict lands:

1. **Independent, Ledgerkit-side confirmation** — every prior evaluation
   above was authored by CodeCompass's own `context-evaluator`/
   `reference-project-tester`, inspecting Ledgerkit from outside. This
   phase is the first time Ledgerkit's *own* `context-curator` evaluates
   CodeCompass from inside a real, routine Ledgerkit development task —
   a genuinely different vantage point, not a rerun.
2. **End-to-end workflow integration**, not isolated `query` calls —
   every prior phase tested specific questions or a scratch-copy
   experiment; none tested "CodeCompass wired into Ledgerkit's actual
   phase-planning ritual, context packet handed to a real planning
   agent, findings fed back through the real feedback channel."
3. **Routine-adoption value, evaluated separately from context-advantage
   level** — `codecompass check`'s staleness/coverage gate (§5 Step 9),
   honest not-found-vs-empty disambiguation, and a working feedback loop
   to CodeCompass's own review process are each worth evaluating in their
   own right, independent of whatever this phase's context-advantage
   verdict turns out to be — "does routine adoption pay for its setup/
   maintenance cost" and "does it teach the agent something new" are two
   different, both-genuinely-open questions this phase should answer
   separately, not conflate.

This is not scope reduction — every goal in the user's brief is still
delivered (§5 maps each one to a concrete step); it is calibrating what
counts as a defensible retro conclusion before, not after, evidence comes
in.

---

## 4. Roster — apply, don't reinvent

`adoption-blueprint.md` §1 recommends a **5-role minimum starting
roster** for a project like Ledgerkit. Checking Ledgerkit's actual
`.claude/agents/` directory: it already has **seven** — a superset of the
minimum, and already very close to the blueprint's exact mapping:

| Blueprint role | Ledgerkit's existing agent | Gap? |
|---|---|---|
| upstream/compatibility researcher | `hledger-researcher.md` | none |
| differential tester | `compat-differential-tester.md` | none |
| docs maintainer | `docs-maintainer.md` | none |
| roadmap/state curator | `roadmap-context-curator.md` | none |
| knowledge curator + context curator (blueprint recommends folding, initially) | `context-curator.md` (already exists, per Stage A's `05-context-curator.md`) | none — already folded, matching the blueprint's own recommendation independently |
| *(beyond the minimum 5, already present)* | `docs-reconstructor.md`, `release-phase-auditor.md` | n/a — bonus, not required |

**Finding: no new agent role is needed for this phase.** This is a
genuine, checkable result (not assumed) — worth stating plainly rather
than proposing roster changes that aren't justified by any demonstrated
gap, per the blueprint's own "start minimal, add only with cause"
discipline (§9 there) and CLAUDE.md's parallel principle against
unrequested abstraction.

---

## 5. Detailed phase steps

### Step 1 — Install and configure CodeCompass against the real Ledgerkit repository (Goal 1)

- `pip install -e /home/cormac/projects/codecompass` (editable local
  install; local install is the same discipline Ledgerkit already
  applies to the pinned `hledger` binary/source clone, not a new
  pattern). Python 3.13.5 available, satisfies `requires-python >=3.11`.
- **Re-verify release state at whatever commit this step actually
  installs from** (§1.1's standing instruction, not a one-off check):
  confirm `README.md`'s "Status" section, `pyproject.toml`'s version, and
  `git tag` agree with each other before treating any of them as
  authoritative. If they disagree, file it as a CodeCompass documentation
  finding (§6) and record which source this plan/Ledgerkit's own docs
  actually cite — **never silently pick whichever reads best and move
  on**.
- Run `codecompass init`/`sync` **against Ledgerkit's real working tree**
  at its current commit — not a scratch copy (Phase 2's ad hoc CLI usage
  and CodeCompass's own Phases 45–67 both used pinned commits or scratch
  copies; Goal 1 explicitly asks for the real repository this time).
- Confirm `.claude/skills/codecompass/SKILL.md` regenerates with real
  content (even if "0 vendors, 1 optional: pandas" — Ledgerkit's own
  known shape) and that `/discovery`/`codecompass query` work against
  the real `context-graph.db`.
- **Gate G-CC-1** (§8): whether `context-graph.db`/`vendor/` get
  committed to Ledgerkit's repo or gitignored as regenerable local
  state. CodeCompass's own repo gitignores both by its own convention
  (`decisions/0004`) — recommend Ledgerkit follow the same precedent
  rather than commit generated, non-authoritative state.

### Step 2 — Build the initial evidence-backed representation, deterministic sync first (Goal 2)

- Run a full **deterministic/mechanical `sync` first**, with no
  enrichment involved, and record the actual result precisely — whatever
  it turns out to be, not assumed from §1.4's baseline table.
- **Only then**, where `sync` surfaces legitimate candidate relationships
  eligible for enrichment, exercise whichever enrichment path actually
  applies in this environment: API-backed enrichment if
  `ANTHROPIC_API_KEY` is configured, **and/or** the supported
  agent-facing `codecompass enrich apply` workflow (README: "lets a
  Claude Code agent supply spec-doc relationship enrichment when no
  `ANTHROPIC_API_KEY` is configured") — try both if both are available,
  since they're different code paths worth exercising for real rather
  than assumed equivalent.
- **Hard constraint, restated from §7**: never manufacture a relationship
  or trigger enrichment on a pairing that isn't a legitimate candidate,
  solely to raise graph density or make the evaluation look better. If
  `sync` finds nothing eligible for enrichment, that is the accurate
  result to record, not a gap to work around.
- Independently re-run (not trust CodeCompass's own cross-repo claim)
  the exact Phase 67 spot-check — `codecompass query relations
  dev-docs/hledger-compatibility.md` should return an honest empty table,
  not a "not found" error — as Ledgerkit's own first-party confirmation
  that the environment is actually configured correctly before relying
  on it for anything else.

### Step 3 — The genuine next task: `tag:` query-term matching (Goal 3, G-CC-2 resolved)

Per §1.5, no phase was already scoped. **Resolving gate G-CC-2 now**
(per explicit instruction, absent any repository evidence surfaced by
this amendment round that argues otherwise): the genuine task for Steps
4-5 is **`tag:` query-term matching** — the most-prepared candidate (two
existing `hledger-researcher` briefs, `19-tag-query-semantics-brief.md`
and `20-tag-parsing-syntax-brief.md`, already exist from Phase 4's own
scoping work; its data-model prerequisite shipped in Phase 4; it was
named first among the deferred candidates in Phase 5's own retro). Phase
5A **researches and prepares context for it — it does not implement
it**; `tag:` matching itself (parsing/inheritance/combination semantics)
remains a separate, subsequent, separately-approved phase, exactly
preserving its existing scope (`19-tag-query-semantics-brief.md`'s own
already-recorded findings, including the four inheritance rules and the
always-AND-never-OR combination behaviour, are untouched by this plan).

### Step 4 — Use the real agent-facing workflow first, then direct queries for deeper investigation (Goal 4)

**In this order, not collapsed into a single CLI-query pass:**

1. **Start from the generated agent entry points, as a normal Ledgerkit
   development task would**: the root `CLAUDE.md` routing-table pointer
   (once Step 8 adds it), the regenerated `.claude/skills/codecompass/
   SKILL.md`, and `/discovery` — read/run these first, the way an agent
   picking up a real `tag:`-matching task would actually encounter them,
   not skipped in favour of going straight to the CLI.
2. **Then** use direct `codecompass query relations`/`query vendors`/
   `query symbols` (against `ledgerkit/query/`, `ledgerkit/tags.py`, the
   two existing tag briefs, `dev-docs/hledger-compatibility.md`'s `tag:`
   row) for whatever the Skill/`/discovery` pass didn't already surface,
   deeper evidence inspection, and provenance capture.
3. Capture verbatim output at both stages — not a paraphrase — so
   provenance (§4 below) is checkable after the fact, and so the retro
   can distinguish what the *generated agent entry points* surfaced from
   what only the *direct CLI* found, a real, reportable distinction the
   original single-pass design would have collapsed.

**Do not reduce this step to manually running CLI queries and hand-
assembling a packet** — the explicit point of testing the Skill/routing/
`/discovery` path first is that it's the actual, intended agent-facing
product surface, not an implementation detail underneath it.

### Step 5 — Generate a self-contained context packet, with per-finding provenance (Goal 5)

A single Markdown artifact (e.g. `validation/codecompass/context-packets/
tag-query-matching.md`) bundling the Step 4 output, cross-references to
the two existing hledger-researcher briefs and the compat-register's own
`evidence:`/`implementation:` fields (already Ledgerkit's native
provenance format — §4.4 of `04-codecompass-integration.md`), and an
explicit "unresolved questions" section.

**For every material finding in the packet, record two things, not
one**: the supporting evidence itself, and **which of these four
provenance categories** it falls into —

1. **Surfaced by CodeCompass** — the finding would not plausibly have
   been reached without a CodeCompass query/Skill/`/discovery` result.
2. **Independently found from Ledgerkit sources** — reached by direct
   inspection (grep, reading a file, an existing brief/compat-register
   entry), with no material CodeCompass contribution.
3. **CodeCompass pointed to relevant evidence, but the conclusion
   required direct investigation** — a query result named a file/symbol/
   relation, but understanding *what it meant* for the task took reading
   the actual source, not just trusting the pointer.
4. **Already known before CodeCompass consultation** — restates
   something already established in Ledgerkit's own docs/briefs/compat-
   register, unaffected by whether CodeCompass was consulted at all.

Every material claim must trace to a CodeCompass query result (cited
verbatim) or an existing Ledgerkit document/decision (cited by path) —
never an unlabelled assertion — **and** carry one of the four category
tags above, so the retro (§6) can separate evidence provenance from
CodeCompass's actual, specific contribution rather than crediting it
for category-2/4 findings it didn't produce.

### Step 6 — Capture feedback into CodeCompass (Goal 6)

`context-curator` produces `CC-LK-NNN` findings (`validation/codecompass/
findings/`, existing format, `05-context-curator.md`) for anything
incorrect or newly-missing found during Steps 1-5, and for any release-
state disagreement found in Step 1 that CodeCompass's own process hasn't
already caught (§1.1). Given the extensive prior history, some findings
may well *reconfirm* already-filed CodeCompass-side observations
(`CG-002`, `CG-004`) — report that honestly rather than manufacturing a
novel finding for its own sake. `CG-004` specifically: if this phase's
own use independently reproduces its symptom on real (not scratch-copy)
Ledgerkit content, that reproduction is itself worth filing —
corroboration from a second, differently-motivated context strengthens
the case for CodeCompass to prioritise it, without Ledgerkit fixing
CodeCompass's own code.

### Step 7 — Confirm existing controls stay authoritative (Goal 7)

No new mechanism needed — Ledgerkit's existing review, compat-register,
testing, and retro process already governs every deliverable this phase
produces. This step is a **checklist confirmation** in the phase's DoD
(§9), not new design: nothing CodeCompass says is written into
`knowledge/DECISIONS.md`, a compat-register entry, or `ROADMAP.md`
without going through the same process every other finding in this
project already does.

### Step 8 — Document the routine workflow (Goal 8)

Extend `04-codecompass-integration.md` (update its stale "pre-release"
framing to "v1.0.0, adopted Stage C Phase 5A") rather than write a
parallel document — it already contains almost everything needed (§1.3).
Add a short pointer section to root `CLAUDE.md` (per `adoption-
blueprint.md` §3's own recommendation: "Ledgerkit's own `CLAUDE.md` gains
a pointer section the same way CodeCompass's own root `CLAUDE.md` ends
with one to `ai-docs/README.md`") or Ledgerkit's nearest equivalent
project-instructions surface — **gate G-CC-4** (§8), since it's a
standing-process-document change worth explicit confirmation even though
`CLAUDE.md` is not one of the Unauthorised-Change-Rule-protected files.

### Step 9 — Lifecycle/staleness verification (new)

Using the doc edits Step 8 already makes as the harmless change (not a
manufactured one for this test's own sake — do not introduce a Ledgerkit
*feature-behaviour* change solely to exercise this):

1. After Step 2's initial `sync`, let Step 8's `04-codecompass-
   integration.md`/`CLAUDE.md` edits land.
2. Re-run `codecompass check` (and `sync` if `check` indicates staleness)
   and confirm the changed files are correctly flagged as stale, then
   correctly refreshed after the re-sync — not silently still showing
   pre-edit content.
3. Record the exact before/after `check` output as evidence, the same
   verbatim-capture discipline as Step 4.

This directly exercises the staleness/coverage-gate value named in §3's
third contribution — untested by any prior CodeCompass-side Ledgerkit
evaluation, all of which used a single static pin rather than a real
edit-then-resync cycle.

---

## 6. Evaluation design

Reuses CodeCompass's own `context-quality-evaluation.md` instrument
wholesale (already Ledgerkit's stated design intent, `04-codecompass-
integration.md` §4.5) rather than inventing a parallel one. Ground rules
ported directly, all load-bearing for an honest result here specifically:

- The evaluator (`context-curator`) inspects Ledgerkit directly to
  establish ground truth — never uses CodeCompass to validate
  CodeCompass.
- **Incorrect context is more serious than incomplete context** — a
  single confidently-wrong claim outranks several honestly-thin results.
  Directly relevant given §1.4's FAIL history was exactly this class of
  error (a confident "not found" for a real file).
- A technically-correct but marginal result is recorded honestly as
  low-advantage, not rounded up.
- **The single-trial baseline/treatment confound** (`context-quality-
  evaluation.md` §1, added at CodeCompass's own Phase 61 as `L-027`):
  before crediting CodeCompass for anything the "baseline" workflow
  supposedly missed, check whether both had equal raw-source access to
  the decisive evidence — if so, the delta is agent diligence, not
  context quality. Directly relevant to the user's own "baseline the
  normal development workflow against the CodeCompass-assisted workflow"
  ask: a single side-by-side run cannot, by construction, cleanly
  separate the two; the retro must say so explicitly rather than credit
  or blame CodeCompass for a difference that might just be which agent
  happened to read more carefully.

The user's eight evaluation questions map directly onto this instrument's
existing fields (useful-context / incorrect-or-missing / cross-cutting
understanding / provenance-sufficiency / packet usefulness / maintenance
burden / required changes) — no new evaluation schema needed.

**Provenance drives the contribution verdict, not just the packet
(§5 Step 5):** the retro must use the four provenance categories tagged
on each context-packet finding to report CodeCompass's *actual*
contribution separately from the evidence itself — a packet full of
correct, well-cited findings that are mostly category 2/4 ("independently
found" / "already known") is a different, weaker result than the same
packet dominated by category 1/3 ("surfaced by CodeCompass" / "pointed to
evidence, conclusion required investigation"), even if both packets look
equally polished. Report the category distribution explicitly, the same
way §1.4's own gates report advantage distribution.

**Explicit instruction for the retro — no anchoring to the historical
baseline (§1.4):** report whatever Steps 1-6/9 actually produce, decided
by this phase's own evidence. The prior LOW-advantage findings are
background context for interpreting *why* a result might look the way it
does, not a target, a floor, or a prediction to confirm. State plainly,
based on the actual evidence gathered, whether this phase's result is an
**improvement**, a **regression**, or **unchanged** relative to the
baseline table — and say so even if that conclusion is "unchanged, for
the same structural reason" (a legitimate, evidence-backed answer) or
"improved, because the real agent-facing entry points (§5 Step 4) and the
staleness cycle (§5 Step 9) exercised paths no prior evaluation tested"
(also a legitimate, evidence-backed answer) — whichever the evidence
actually supports. The retro's "required improvements" section should
cover both the *workflow* (is routine adoption worth the setup/
maintenance cost, whatever the context-advantage verdict is) and, if the
verdict changed, *why* it changed — new tooling, a different evaluation
angle, or something else — rather than assuming either direction without
saying which.

---

## 7. Constraints (restated, cross-checked against Ledgerkit's own rules)

- No unrelated Ledgerkit feature development this phase — matches
  CLAUDE.md's existing phase-scoping discipline.
- No Ledgerkit behaviour change to make CodeCompass integration look
  successful — matches `04-codecompass-integration.md`'s existing hard
  boundary (§4.6) and `reference-project-protocol.md`'s reciprocal rule
  on CodeCompass's side.
- CodeCompass-derived conclusions are evidence-backed context, never
  unquestionable truth — matches the existing deterministic/agent-
  suggested/verified/rejected state model already in
  `04-codecompass-integration.md` §4.4; nothing new to design.
- Existing compatibility evidence/tests/plans/retros remain authoritative
  — unchanged, no mechanism in this phase overrides them.
- CodeCompass shortcomings recorded separately, fed back via the existing
  `CC-LK-NNN` channel, never silently patched into Ledgerkit — matches
  Step 6 exactly.
- **No manufactured relationships or enrichment** — Step 2's enrichment
  pass (API-backed and/or `enrich apply`) only ever runs against
  legitimate candidate relationships `sync` actually surfaces; density or
  a better-looking evaluation result is never a reason to enrich or
  relate something that isn't a real relationship.
- **No `pyproject.toml` change** — CodeCompass is agent-side development
  tooling (installed and run by the assisting agent, consulted for
  context), never a Ledgerkit runtime or declared dependency, exactly
  like the pinned `hledger` binary/source clone. This means the
  Unauthorised Change Rule's protected-file gate for `pyproject.toml`
  is **not** triggered by this phase at all — worth stating explicitly so
  it isn't mistakenly treated as requiring that gate.

---

## 8. Human decision gates

- **G-CC-1** — *(retained, unchanged)* commit `context-graph.db`/
  `vendor/` to the Ledgerkit repo, or gitignore as regenerable local
  state. Recommended: **gitignore**, matching CodeCompass's own
  convention for its own repo (`decisions/0004`); no repository evidence
  from this amendment round argues otherwise.
- **G-CC-2** — **resolved**: `tag:` query-term matching is the genuine
  next-phase task for Steps 3-5 (§5 Step 3), per explicit instruction and
  absent any repository evidence surfacing a stronger reason otherwise.
  Preserves its existing scope: Phase 5A researches/prepares context for
  it; the subsequent, separately-approved phase implements it.
- **G-CC-3** — *(retained, unchanged)* no new permanent agent role is
  added solely for CodeCompass adoption — §4's finding (Ledgerkit's
  existing 7-role roster already exceeds the blueprint's 5-role minimum)
  stands; no repository evidence from this amendment round surfaces a
  gap that would justify one.
- **G-CC-4** — *(retained, refined)* add the appropriate Ledgerkit
  agent/workflow pointer — `CLAUDE.md`'s own pointer section (Step 8) or
  whichever of Ledgerkit's project-instruction surfaces is the closer
  equivalent — not protected, but a standing-process-document change
  worth explicit confirmation.
- **G-CC-5** — *(retained, refined)* adoption success is judged on
  **workflow usefulness, evidence quality, provenance, repeatability, and
  maintenance burden** — not on requiring a HIGH context-advantage
  result. This restates §3/§6's evaluation design in the gate's own
  terms; approving it means approving that a LOW-advantage-but-honest,
  well-evidenced, repeatable result is an acceptable phase outcome, not a
  shortfall to be avoided.

---

## 9. Definition of Done (mapped to the user's seven exit criteria)

1. **"Ledgerkit can be analysed reliably through CodeCompass v1"** →
   Step 1-2 complete; the Phase 67 spot-check independently reproduced
   from Ledgerkit's own side with an honest (not false-negative) result;
   release state independently re-verified (Step 1). "Reliably" is read
   as "without giving confidently wrong answers" — whether it also turns
   out to carry high informational value is this phase's own evidence to
   establish (§3, §6), not assumed either way going in.
2. **"The next planned task researched/planned using CodeCompass
   context"** → Steps 3-5 complete for `tag:` query-term matching
   (G-CC-2, resolved), context packet exists (with per-finding provenance
   tags, Step 5) and is cited by the resulting implementation plan (a
   separate, later phase).
3. **"Material context claims traceable to evidence"** → Step 5's packet
   format enforced: every claim cited to a query result or existing doc,
   **and** tagged with one of the four provenance categories.
4. **"Integration and feedback workflow documented and repeatable"** →
   Step 8 (`04-codecompass-integration.md` updated, not duplicated) *and*
   Step 9 (the staleness/re-sync cycle independently exercised and its
   before/after `check` output recorded) — "repeatable" is read as
   including "survives a real edit, not just a first run."
5. **"Retro records demonstrated benefits, limitations, required
   improvements"** → §6's evaluation design, reporting an independently-
   determined improvement/regression/unchanged verdict against the §1.4
   baseline, never assumed.
6. **"Roadmap updated with resulting workflow changes"** → this plan's
   own `ROADMAP.md` insertion (done alongside this plan, per the user's
   explicit "insert a new roadmap phase" instruction) plus any further
   update the retro's findings warrant.
7. **"Ledgerkit can proceed to the previously planned next phase using
   the adopted workflow"** → `tag:` query-term matching (G-CC-2) becomes
   a real, separately-scoped, separately-approved subsequent phase, using
   this phase's packet as its starting context — not implemented inside
   this phase itself (matches the Constraints section's "do not
   substantially alter the scope of the existing next feature phase").

---

## 10. Amendment round (2026-09-24, same day, before implementation)

The plan above reflects eight targeted amendments made after user review,
before any implementation began. Summary of what changed and why (full
reasoning inline at each section):

1. **§5 Step 4** — now requires exercising the real agent-facing entry
   points (generated Skill, `/discovery`) *first*, direct `codecompass
   query` second, explicitly forbidding collapsing the experiment into
   CLI-only manual assembly.
2. **§5 Step 5** — every context-packet finding now carries one of four
   required provenance categories (surfaced by CodeCompass /
   independently found / CodeCompass-pointed-but-investigation-required /
   already known), feeding §6's contribution-vs-evidence distinction.
3. **§1.4, §2, §3, §6** — removed language predicting or normalising a
   repeat LOW-advantage result; the historical baseline table is retained
   as prior evidence, but the evaluator is now explicitly instructed not
   to assume the same outcome and to record improvement/regression/
   unchanged from this phase's own observed evidence.
4. **§5 Step 9 (new)** — a lifecycle/staleness test: use Step 8's own doc
   edits as a harmless real change, re-run `check`/`sync`, confirm
   staleness detection and refresh work, without introducing a Ledgerkit
   feature-behaviour change for the test's own sake.
5. **§5 Step 2, §7** — deterministic/mechanical `sync` now explicitly
   sequenced before enrichment; both API-backed enrichment and the
   agent-facing `enrich apply` workflow are in scope where legitimate
   candidates exist; a hard constraint against manufacturing relationships
   or enrichment for graph-density/evaluation-appearance reasons added to
   Constraints.
6. **§0, §1.1, §5 Step 1** — release state independently re-verified this
   round (found CodeCompass's `README.md` briefly disagreed with its own
   tag/PyPI state at the original pin, already self-corrected by
   CodeCompass's own Phase 70 audit one commit later — no new finding
   needed, but the re-check is now a standing part of Step 1, and any
   *future* disagreement must be filed as a CodeCompass documentation
   finding, never silently resolved).
7. **§5 Step 3, §8 G-CC-2** — resolved: `tag:` query-term matching is the
   genuine next task, absent any repository evidence this round surfacing
   a stronger alternative. Its existing scope (research/prepare context,
   not implement) is unchanged.
8. **§8 G-CC-1/3/4/5** — recommendations retained as previously stated,
   wording refined to match the user's own restatement (G-CC-5 now
   explicitly: workflow usefulness, evidence quality, provenance,
   repeatability, maintenance burden — never a required HIGH
   context-advantage result).

### Consistency review

- **Phase 5A remains an integration/evaluation phase, not a Ledgerkit
  feature-development phase.** No step adds or changes `ledgerkit/`
  behaviour; Step 9's staleness test explicitly reuses a documentation
  edit already happening in Step 8, not a manufactured feature change;
  Constraints (§7) restate this as a hard boundary, unchanged by the
  amendment round.
- **The subsequent phase (`tag:` query-term matching, G-CC-2) remains
  the first genuine implementation test of the adopted workflow.** §5
  Step 3 and DoD item 7 both state plainly that Phase 5A researches and
  prepares context for it — it is not implemented inside this phase.
- **CodeCompass-derived claims remain subordinate to direct evidence,
  Ledgerkit's own tests, compatibility research, `knowledge/
  DECISIONS.md`, and normal project verification controls.** Unchanged
  from the original plan's §7/Step 7; the amendment round's provenance
  categories (§5 Step 5) make this *more* checkable, not less — a
  category-1 ("surfaced by CodeCompass") finding still has to clear the
  same existing review/compat-register/testing bar as any other before
  it becomes authoritative in Ledgerkit's own docs.
- **Negative or neutral findings remain an acceptable outcome.** §6's
  rewritten evaluation instruction and G-CC-5's refined wording both
  state this explicitly now, replacing the earlier draft's framing (which
  risked reading as "a LOW result is expected, so don't worry about it")
  with the more precise "a LOW result is acceptable *if that's what the
  evidence shows*, exactly as much as an improved result would be."

---

## Appendix — files read this planning pass, for anyone re-verifying

`/home/cormac/projects/codecompass/README.md`, `pyproject.toml`,
`CHANGELOG.md`; `planning/v1-redefinition/{adoption-blueprint,
ledgerkit-plan,context-quality-evaluation}.md`; `planning/reference-
projects/ledgerkit/findings.md` (in full, including the 2026-09-24 Phase
67 re-confirmation section); `src/codecompass/spec_docs.py`
(`_DEFAULT_GLOBS`, `scan_spec_docs`); `.gitignore`; `git log`/`git tag`
re-checked twice (original pass and this amendment round, confirming the
repo moved one commit further in between). Ledgerkit's own `dev-docs/
planning/core-redefinition/04-codecompass-integration.md`, `05-context-
curator.md`; `.claude/agents/*.md` (roster); `.claude/skills/
codecompass/SKILL.md`; `dev-docs/retros/STAGE-C-PHASE-5.md`;
`ROADMAP.md`.

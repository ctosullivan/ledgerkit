# 22. Stage C Phase 5A plan — CodeCompass development workflow adoption

Planning only. No `ledgerkit/`/`tests/` code touched, no CodeCompass
installation/configuration performed yet. Do not begin implementation
until the gates in §8 are resolved — matching this project's own
precedent for a request this size and shape (`18-stage-c-phase-2-
codecompass-adoption-plan.md`/`STAGE-C-PHASE-2-PLAN.md`: the original
CodeCompass-adoption request was itself a single detailed message that
produced a planning-pass response first, not immediate implementation).

## 0. Pinned revisions

- Ledgerkit: `c6168b2` (Stage C Phase 5 close)
- CodeCompass: `4c09185d4189f9c59fa46010420c049f00cd9688`, **tag
  `v1.0.0`** (`4c09185` = "docs(phase-70): write phase retro", the commit
  immediately after `9dba747` = "release(phase-70): v1.0.0"). Local
  clone: `/home/cormac/projects/codecompass`.
- hledger: unchanged, `1.52.4` / `33fa849e7ae841968bd21c427094c4fb4a4ec38d`.

---

## 1. Current-state assessment

### 1.1 CodeCompass v1.0.0 is real, current, and freshly released

`git tag` on the local clone shows `v1.0.0`; `pyproject.toml` names the
distribution `codecompass-context`, version `1.0.0`. CodeCompass's own
`README.md` describes v1 as a **redefined** milestone — not a packaging
checkpoint but a "product-validation milestone: CodeCompass developed
agent-led, validated against real external reference-project work,
improved from that evidence, and released only after a blank-slate
documentation reconstruction and an independent audit." That validation
work is not abstract — **Ledgerkit is the primary reference project it
was validated against** (§1.3).

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

**Implication:** a fresh Phase 5A run reproducing the same baseline
questions will, with high confidence, land at the same LOW-advantage,
structurally-explained result — not because this phase did anything
wrong, but because the underlying cause (Ledgerkit's own genuinely
zero-runtime-dependency design, by deliberate choice, plus `CG-004`
remaining unfixed) hasn't changed since this morning's own
re-confirmation. §3 reframes the phase's objective around this rather
than around chasing a result the evidence already shows is unlikely.

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

- **The LOW-advantage finding itself** — already established across four
  gates, the most recent dated today. Phase 5A's evaluation (§6) should
  extend/independently re-confirm this from Ledgerkit's own side (a
  genuine, non-duplicative contribution — see §6), not treat it as an
  open question to "discover" fresh.
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

## 3. Objective, reframed honestly against §1.4's evidence

The user's stated objective — integrate CodeCompass v1 into Ledgerkit's
normal development process and establish a repeatable, evidence-backed
workflow — stands unchanged. What changes, given §1.4, is what "success"
should be measured against: **this phase is not expected to demonstrate
that CodeCompass gives Ledgerkit rich new context** — that has already
been tested, honestly, multiple times, by CodeCompass's own team, most
recently this morning, and found LOW by a disclosed structural cause
(zero runtime dependencies + one still-open relation-detection gap). Not
adjusting for this before evaluating would risk exactly the "manufactured
favourable result" the user explicitly warned against — either by
re-running the same low-value baseline questions and calling a repeat
LOW result a new discovery, or by unconsciously picking evaluation
questions likely to look better.

What genuinely **is** untested, and is this phase's real contribution:

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
3. **Routine-adoption value independent of context-advantage level** —
   `codecompass check`'s staleness/coverage gate, honest not-found-vs-
   empty disambiguation, and a working feedback loop to CodeCompass's own
   review process are useful even at LOW context advantage; that's a
   different, real question from "does it teach the agent something new"
   (already answered: mostly not, for this project, today).

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
  install — not yet confirmed published to PyPI under the renamed
  `codecompass-context` distribution; local install is the same
  discipline Ledgerkit already applies to the pinned `hledger` binary/
  source clone, not a new pattern). Python 3.13.5 available, satisfies
  `requires-python >=3.11`.
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

### Step 2 — Build and honestly record the initial evidence-backed representation (Goal 2)

- Run a full `sync` + (if `ANTHROPIC_API_KEY` is configured) enrichment
  pass. Record the actual result precisely — per §1.4's evidence, expect
  a thin result (0-1 tracked vendors, near-empty relation edges) and
  **say so plainly**, not as a shortfall but as the accurate, already-
  predicted starting state.
- Independently re-run (not trust CodeCompass's own cross-repo claim)
  the exact Phase 67 spot-check — `codecompass query relations
  dev-docs/hledger-compatibility.md` should return an honest empty table,
  not a "not found" error — as Ledgerkit's own first-party confirmation
  that the environment is actually configured correctly before relying
  on it for anything else.

### Step 3 — Resolve the missing "next planned phase" (Goal 3), then use it as the genuine task

Per §1.5, this doesn't already exist. Recommend (not silently assume):
**`tag:` query-term matching** — the most-prepared candidate (two
existing `hledger-researcher` briefs, `19-tag-query-semantics-brief.md`
and `20-tag-parsing-syntax-brief.md`, already exist from Phase 4's own
scoping work; its data-model prerequisite shipped in Phase 4; it was
named first among the deferred candidates in Phase 5's retro). Final
choice is **gate G-CC-2** (§8) — the plan does not pre-commit past
recommending.

### Step 4 — CodeCompass-assisted research before implementation planning (Goal 4)

For the chosen task: `codecompass query relations`/`query vendors`/
`query symbols` against the relevant files (`ledgerkit/query/`,
`ledgerkit/tags.py`, the two existing tag briefs, `dev-docs/
hledger-compatibility.md`'s `tag:` row); capture verbatim output, not a
paraphrase, so provenance (Goal "preserve provenance") is checkable
after the fact. Given §1.4's evidence, expect this to surface little
CodeCompass didn't already know was near-empty for this project shape —
record that outcome exactly as observed, whichever way it goes.

### Step 5 — Generate a self-contained context packet (Goal 5)

A single Markdown artifact (e.g. `validation/codecompass/context-packets/
tag-query-matching.md`) bundling: the CodeCompass query output from Step
4, cross-references to the two existing hledger-researcher briefs and the
compat-register's own `evidence:`/`implementation:` fields (already
Ledgerkit's native provenance format — §4.4 of `04-codecompass-
integration.md`), and an explicit "unresolved questions" section. Every
material claim in it must trace to either a CodeCompass query result
(cited verbatim) or an existing Ledgerkit document/decision (cited by
path) — never an unlabelled assertion.

### Step 6 — Capture feedback into CodeCompass (Goal 6)

`context-curator` produces `CC-LK-NNN` findings (`validation/codecompass/
findings/`, existing format, `05-context-curator.md`) for anything
incorrect or newly-missing found during Steps 1-5. Given the extensive
prior history, most findings will likely *reconfirm* already-filed
CodeCompass-side observations (`CG-002`, `CG-004`) rather than discover
new ones — report that honestly rather than manufacturing a novel
finding. `CG-004` specifically: if this phase's own use independently
reproduces its symptom on real (not scratch-copy) Ledgerkit content, that
reproduction is itself worth filing — corroboration from a second,
differently-motivated context strengthens the case for CodeCompass to
prioritise it, without Ledgerkit fixing CodeCompass's own code.

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
with one to `ai-docs/README.md`") — **gate G-CC-4** (§8), since it's a
standing-process-document change worth explicit confirmation even though
`CLAUDE.md` is not one of the Unauthorised-Change-Rule-protected files.

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

**Explicit instruction for the retro** (restating the user's own,
grounded in §1.4): report whatever Steps 1-6 actually produce. Given the
weight of prior, current evidence, a repeat **PASS WITH GAPS / LOW
advantage** outcome is the anticipated, not disappointing, result — the
retro should treat that as confirmation the tool is honestly self-
reported, not as this phase's failure, and should focus its "required
improvements" section on the *workflow* (is routine adoption worth the
setup/maintenance cost even at LOW advantage?) rather than re-litigating
whether CodeCompass is "good," which four prior gates have already
answered for this project's current shape.

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
- **No `pyproject.toml` change** — CodeCompass is agent-side development
  tooling (installed and run by the assisting agent, consulted for
  context), never a Ledgerkit runtime or declared dependency, exactly
  like the pinned `hledger` binary/source clone. This means the
  Unauthorised Change Rule's protected-file gate for `pyproject.toml`
  is **not** triggered by this phase at all — worth stating explicitly so
  it isn't mistakenly treated as requiring that gate.

---

## 8. Human decision gates

- **G-CC-1** — commit `context-graph.db`/`vendor/` to the Ledgerkit repo,
  or gitignore as regenerable local state (recommended: gitignore,
  matching CodeCompass's own convention for its own repo, `decisions/0004`).
- **G-CC-2** — which candidate becomes the genuine next-phase task used
  in Steps 3-5: `tag:` query-term matching (recommended, most-prepared),
  `cur:`, a standalone `--depth`/`-N` CLI flag, the `Query`-as-
  compatibility-shim migration, or treating the scoping decision itself
  as the task.
- **G-CC-3** — confirm no new agent role is added (§4's finding) — or
  specify what gap justifies one.
- **G-CC-4** — approve the proposed `CLAUDE.md` pointer-section addition
  (Step 8) — not protected, but a standing-process-document change.
- **G-CC-5** — approve evaluating against §3's reframed objective
  (routine-adoption value, not a hoped-for high-context-advantage
  discovery the evidence already argues against) rather than an
  unadjusted repeat of the original brief's implicit framing.

---

## 9. Definition of Done (mapped to the user's seven exit criteria)

1. **"Ledgerkit can be analysed reliably through CodeCompass v1"** →
   Step 1-2 complete; the Phase 67 spot-check independently reproduced
   from Ledgerkit's own side with an honest (not false-negative) result.
   "Reliably" is read as "without giving confidently wrong answers" —
   already the bar CodeCompass's own Phase 51/67 evidence supports; not
   "with high informational value," which §1.4 already shows is not
   the current honest bar for this project.
2. **"The next planned task researched/planned using CodeCompass
   context"** → Steps 3-5 complete, context packet exists and is cited
   by the resulting implementation plan (a separate, later phase).
3. **"Material context claims traceable to evidence"** → Step 5's packet
   format enforced (every claim cited to a query result or existing doc).
4. **"Integration and feedback workflow documented and repeatable"** →
   Step 8; `04-codecompass-integration.md` updated, not duplicated.
5. **"Retro records demonstrated benefits, limitations, required
   improvements"** → §6's evaluation design, honestly reported per §3.
6. **"Roadmap updated with resulting workflow changes"** → this plan's
   own `ROADMAP.md` insertion (done alongside this plan, per the user's
   explicit "insert a new roadmap phase" instruction) plus any further
   update the retro's findings warrant.
7. **"Ledgerkit can proceed to the previously planned next phase using
   the adopted workflow"** → the chosen task from G-CC-2 becomes a real,
   separately-scoped, separately-approved subsequent phase, using this
   phase's packet as its starting context — not implemented inside this
   phase itself (matches the Constraints section's "do not substantially
   alter the scope of the existing next feature phase").

---

## Appendix — files read this planning pass, for anyone re-verifying

`/home/cormac/projects/codecompass/README.md`, `pyproject.toml`;
`planning/v1-redefinition/{adoption-blueprint,ledgerkit-plan,context-
quality-evaluation}.md`; `planning/reference-projects/ledgerkit/
findings.md` (in full, including the 2026-09-24 Phase 67 re-confirmation
section); `src/codecompass/spec_docs.py` (`_DEFAULT_GLOBS`,
`scan_spec_docs`); `.gitignore`. Ledgerkit's own `dev-docs/planning/
core-redefinition/04-codecompass-integration.md`, `05-context-
curator.md`; `.claude/agents/*.md` (roster); `.claude/skills/
codecompass/SKILL.md`; `dev-docs/retros/STAGE-C-PHASE-5.md`;
`ROADMAP.md`.

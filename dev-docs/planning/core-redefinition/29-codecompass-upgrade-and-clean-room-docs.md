# 29. CodeCompass upgrade + clean-room documentation reconstruction

**Status:** Planning only. No `ledgerkit/`, `tests/`, or generated-docs
content has been changed to produce this document. Stops for explicit
human approval before any implementation sub-phase begins — see §8.

**Trigger:** direct user request (2026-10-02) to (1) bring Ledgerkit's
CodeCompass integration current, then (2) use the upgraded tooling to
reconstruct Ledgerkit's human-facing documentation from primary evidence
only, with old documentation held out of the reconstruction and
reintroduced afterward only for comparison.

---

## 1. What this is, and where it sits

This is **not** a new letter in the Stage A–I accounting ladder
(`ROADMAP.md` §"Stages A–I"). Stage D onward is accounting-feature work
(reporting, semantics, investments); this initiative is cross-cutting
dev-tooling and documentation process work, same category as Stage A's
"Development foundation" bucket but arriving after Stage A already
closed. **Recommendation (needs confirmation, §8):** track it in
`ROADMAP.md` as its own section, e.g. "Tooling & Process Initiatives",
parallel to the Stage ladder rather than consuming a Stage letter —
mirroring how Stage A originally absorbed the first CodeCompass
integration before the Stage ladder existed as a formal concept.

It runs **before Stage D starts** (not instead of it) because every
Stage from D onward will keep compounding documentation drift against
whatever baseline exists now, and because CodeCompass's own upstream
project has — independently, in the time since Ledgerkit adopted it —
built almost exactly the methodology this task asks for. Reusing that
work is strictly cheaper than re-deriving it.

### 1.1 What investigation already established (no further discovery needed)

- **CodeCompass is installed as an editable `pipx` install**
  (`pipx install -e /home/cormac/projects/codecompass`,
  `codecompass-context` on PyPI, reported version `1.0.0`). Because it is
  editable, the CLI always executes whatever is on the local clone's
  working tree — there is no separate "reinstall" step. The local clone's
  `origin` (`git@github.com:ctosullivan/codecompass.git`) is confirmed
  **not ahead** of the local clone (`git fetch` shows 0/0 ahead/behind),
  so the clone's `HEAD` (`96a1e4d`, 2026-10-02) genuinely is current
  upstream.
- **`ledgerkit`'s own `context-graph.db` is already schema-current.**
  Stored `meta.schema_version = '11'`, which matches
  `src/codecompass/graph.py`'s live `_SCHEMA_VERSION = "11"` exactly, and
  already has the Phase 76/77 tables (`git_repositories`,
  `git_worktrees`, `git_submodules`, `source_files`, `source_symbols`).
  `codecompass check` runs clean, no crash, no migration prompt. **There
  is no schema-breakage problem to fix.**
  `meta.last_deterministic_rebuild_at = 2026-09-24T18:58:27Z` — the db
  predates every Stage C Phase 6–9 code change (`ledgerkit/query/*`,
  `ledgerkit/tags.py`), so it is stale in the *ordinary*, expected sense
  (needs a routine `sync`, not a version migration).
- **Only 7 `src/codecompass/` commits landed after that rebuild date**
  (Phases 73–77), and the last one touching runtime code was Phase 77
  (`03f8519`, first-party source awareness). **Phases 78 through 80 made
  zero `src/codecompass/` changes** — they are planning/decisions/
  `scripts/check_knowledge_base.py` work internal to CodeCompass's own
  project, not something `codecompass sync`/`index` ships to a consumer
  repo like Ledgerkit. So "upgrading the tool" in the
  reinstall/schema-migration sense is **already done** by virtue of the
  editable install; what's actually missing is:
  1. A routine `sync`/`index` re-run (picks up Stage C's new source and
     regenerates artifacts against the current template).
  2. Reconciling Ledgerkit's **local copies** of CodeCompass-sourced
     agent briefs against the upstream originals, which have drifted —
     confirmed by diff (see §2.2).
  3. Adopting the **new, portable clean-room workflow template**
     upstream built and shipped for exactly this use case (§2.3) — this
     is the actual answer to Objectives 2–5, not something to design from
     scratch.
- **CodeCompass's own `decisions/0066`** (clean-room reconstruction ADR,
  four revisions, now shipped as Phase 79) already did the hard thinking
  about isolation and found, by direct empirical test, that **strict
  mechanical isolation is not achievable for any dispatched role that
  needs `Bash`** — because `Agent(isolation: "remote")` fails in this
  environment (same-host worktree, not a separate environment) and
  because a publicly-hosted repository (CodeCompass's own, and
  **Ledgerkit's own** — `github.com/ctosullivan/ledgerkit`, referenced
  from CodeCompass's own `README.md`) means any network-capable `Bash`
  can simply fetch the "excluded" content from its public mirror
  regardless of local filesystem exclusion. This finding **applies to
  Ledgerkit identically and for the same reason** — Ledgerkit is also a
  public GitHub repository. This phase adopts that finding rather than
  re-discovering it, and reports isolation honestly on two separate axes
  (§4), not as a single rounded-up "done".
- **CodeCompass published the reusable deliverable at
  `https://github.com/ctosullivan/codecompass-template`**
  (`optional-clean-room-workflow/`): nine portable, MIT-licensed,
  CodeCompass-agnostic format skeletons plus two judgment-call guides
  (`mechanical-isolation.md`, `conceptual-documentation-guide.md`) and a
  worked example. Inspected directly (read-only clone, scratch
  directory, this session). Its stage sequence —
  **assertions → snapshot → independent implementation reconstruction →
  comparison → documentation draft → legacy reconciliation →
  documentation-verification** — maps almost one-to-one onto this task's
  Objectives 3–6. §3 adopts it directly rather than reinventing it.

### 1.2 What this means for scope

Objective 1 ("update CodeCompass") turns out to be **small**: no
dependency bump, no schema migration, no breaking-change absorption.
It is a routine re-sync plus an agent-brief reconciliation plus importing
one new template. Objectives 2–6 (clean-room documentation) are the real
weight of this phase, and they get to start from a finished, validated
upstream methodology instead of a blank page.

---

## 2. Phase 1 — CodeCompass reconciliation & re-sync

**Goal:** Ledgerkit's CodeCompass integration reflects the current tool,
current generated-artifact conventions, and the current agent roster it
needs for Phase 3 onward.

### 2.1 Re-sync against current source

- Run `codecompass sync` (whole-project, no vendor arg) from the
  Ledgerkit root. Expected: `context-graph.db` rebuilt, `source_files`/
  `source_symbols` now reflect `ledgerkit/query/*`, `ledgerkit/tags.py`,
  and every other file added/changed since 2026-09-24.
- Run `codecompass index` to regenerate the `CLAUDE.md` routing-table
  marker block and `.claude/skills/codecompass/SKILL.md`.
- Run `codecompass check` again post-sync; expect a clean report (it was
  already clean pre-sync, so this mainly confirms the re-sync didn't
  regress anything).

### 2.2 Reconcile local agent-brief copies against upstream originals

Confirmed by direct diff (this session): Ledgerkit's
`.claude/agents/docs-reconstructor.md` (92 lines) is a materially older,
shorter revision of CodeCompass's current
`.claude/agents/docs-reconstructor.md` (176 lines) — missing the
hardened, topic-scoped MODE 2 (blank-slate → snapshot-based
reconstruction), the domain-claim staleness check, and the
`planning/retros/_drift-audit-phase-NN.md` output convention. The same
kind of drift is likely present in `docs-maintainer.md`,
`release-phase-auditor.md`, and `roadmap-context-curator.md` (not yet
diffed line-by-line — do that as the first implementation step, not
assumed from this plan).

For each of Ledgerkit's four CodeCompass-derived agent briefs
(`docs-reconstructor.md`, `docs-maintainer.md`, `release-phase-auditor.md`,
`roadmap-context-curator.md`):
1. Diff against the current `codecompass` repo's `.claude/agents/<name>.md`.
2. Classify each delta: upstream improvement worth adopting verbatim;
   upstream change that doesn't fit Ledgerkit's conventions (e.g.
   CodeCompass-specific paths like `architecture/**`, `ai-docs/**` have no
   Ledgerkit equivalent — map to `dev-docs/`, `docs/` instead); or
   Ledgerkit-specific customisation that must be preserved (e.g.
   Ledgerkit's compat-register integration, which CodeCompass's own
   roster has no equivalent of).
3. Merge by hand into Ledgerkit's copy — never a blind overwrite, since
   these files already carry Ledgerkit-specific instructions upstream's
   generic version doesn't have.

### 2.3 Import the two new roles the clean-room workflow needs

CodeCompass's current roster (`context-enrichment-agent`,
`context-evaluator`, `context-health-planner`, `context-researcher`,
`docs-maintainer`, `docs-reconstructor`, `documentation-agent`,
`domain-skeptic`, `implementation-reconstructor`, `knowledge-curator`,
`reference-project-tester`, `release-phase-auditor`,
`roadmap-context-curator`) has grown since Ledgerkit's seven-role roster
was set at Stage A. Only two are actually needed for this task:

- **`implementation-reconstructor`** — model-blind, legacy-blind
  as-built reconstruction from primary implementation evidence alone.
  This is the role that performs Phase 3's independent reconstruction.
- **`domain-skeptic`** (comparison mode) — reviews assertions
  adversarially before freezing, and classifies the reconstruction's
  findings against them (`aligned`/`partial`/`conflicting`/
  `not_implemented`/`insufficiently_verified`) in Phase 3.

Adopt both briefs from CodeCompass's current `.claude/agents/`, adapted
the same way as §2.2 (path/convention mapping, not verbatim copy). The
other new upstream roles (`context-evaluator`, `context-health-planner`,
`context-researcher`, `knowledge-curator`, `reference-project-tester`,
`context-enrichment-agent`, `documentation-agent`) are CodeCompass's own
internal roles for building *its* knowledge base — **not adopted**; see
§7 non-goals.

### 2.4 Incidental finding to fix in passing (not a separate phase)

`CLAUDE.md`'s "Folder Structure" diagram (the protected-without-approval
one) already does not match reality — it lists `ledgerkit/{parser,
models, reports, cli}.py` only, omitting `checks.py`, `writer.py`,
`loader.py`, `tags.py`, `commodity_style.py`, `editor_model.py`,
`_pandas_compat.py`, and the whole `query/` subpackage, all of which
already exist and are already tested. Per the Unauthorised Change Rule,
this needs explicit confirmation (§8) before editing, even though it's a
correction, not a structural change — flagged here so it isn't
rediscovered mid-phase and treated as new scope.

### 2.5 Phase 1 acceptance criteria

- `codecompass check` clean (no severity findings) after re-sync.
- `codecompass query source-symbol` returns entries for `ledgerkit/query/*`
  and `ledgerkit/tags.py` (proof the re-sync actually picked up Stage C's
  code).
- All four existing agent briefs diffed against upstream; every delta
  classified (adopt/map/preserve) and merged; no blind overwrite.
- `implementation-reconstructor.md` and `domain-skeptic.md` exist under
  `.claude/agents/`, adapted to Ledgerkit's path/doc conventions.
- `CLAUDE.md`'s CodeCompass section and `04-codecompass-integration.md`
  updated to reflect: current tool state, the roster addition, and a
  pointer to this document.
- Full test suite still green (`ledgerkit/` untouched this phase, so this
  is a regression guard, not expected to find anything).

### 2.6 Files/components touched

- `context-graph.db`, `vendor.toml` (regenerated, gitignored local state).
- `CLAUDE.md` (CodeCompass section + routing-table marker block,
  regenerated; folder-structure diagram correction if approved per §2.4).
- `.claude/skills/codecompass/SKILL.md` (regenerated).
- `.claude/agents/{docs-reconstructor,docs-maintainer,release-phase-auditor,
  roadmap-context-curator}.md` (reconciled).
- `.claude/agents/{implementation-reconstructor,domain-skeptic}.md` (new).
- `dev-docs/planning/core-redefinition/04-codecompass-integration.md`
  (status update, §4.7-style routine-workflow note).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md`.

---

## 3. Phase 2 — Isolation mechanism (adopted, not designed)

**Goal:** a concrete, honestly-labelled isolation mechanism exists before
any real reconstruction content is produced, satisfying the task's
"explicit isolation mechanism so the documentation process cannot simply
iterate on existing prose" requirement.

### 3.1 Adopt the template directly

Copy `codecompass-template`'s `optional-clean-room-workflow/` directory
into Ledgerkit as `dev-docs/clean-room/` (name chosen for Ledgerkit's own
`dev-docs/` convention; the template says the directory may be renamed).
Keep its seven `TEMPLATE.md` skeletons (`assertions/`, `snapshots/`,
`coding-context-selection/`, `implementation-comparison/`, `propagation/`,
`legacy-reconciliation/`, `documentation-verification/`) and its two
guides (`mechanical-isolation.md`, `conceptual-documentation-guide.md`)
verbatim at first; adapt only path references.

**Deliberately not adopted:** CodeCompass's own internal
Claim/Evidence/snapshot YAML machinery in
`scripts/check_knowledge_base.py` and its `assertion_kind`/`basis`/
`evidence_support_state` enum validation tooling. That machinery exists
to validate CodeCompass's own large, long-lived knowledge base; building
or importing an equivalent *validator* for Ledgerkit's much smaller
documentation set is disproportionate — see non-goals (§7). The portable
template's plain-markdown skeletons are sufficient for Ledgerkit's scope
and are what the template itself recommends for adopting projects.

### 3.2 Define Ledgerkit's actual exclusion boundary

Before any dispatch, fix explicitly what is **evidence** (visible to the
reconstruction) vs. **excluded narrative** (held out, reintroduced only
at Phase 4's reconciliation):

| Category | Treatment | Rationale |
|---|---|---|
| `ledgerkit/**/*.py` source | Evidence | Objective 3's "source code as a first-class evidence object" |
| `tests/**`, `tests/fixtures/**` | Evidence | Objective 3 |
| `pyproject.toml`, `MANIFEST.in` | Evidence | build/config |
| `dev-docs/compat-register/*.yaml` | Evidence | structured, evidence-cited classification records, not narrative prose — each entry already traces to differential-test evidence |
| CLI `--help` output, actual command runs | Evidence | "CLI/API behaviour" |
| hledger manual / source (pinned reference) | Evidence (external authoritative spec) | explicitly listed in Objective 3 |
| `git log` for specific files, where behaviour can't otherwise be explained | Evidence, narrowly | Objective 3's "version history only where needed" — not a general green light to read commit messages as documentation |
| `README.md`, `docs/**`, `dev-docs/architecture.md`, `dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md` | **Excluded** | exactly the narrative documentation Objective 2 requires held out |
| `CHANGELOG.md`, `ROADMAP.md`, `CONTEXT.md`, `dev-docs/retros/**`, `dev-docs/planning/**` prose | **Excluded** | historical/process narrative, not primary evidence of current behaviour |
| `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` | **Excluded from the blind reconstruction stage**, available at Phase 4 reconciliation | judgment call — these are closer to verified decision records than pure narrative, but Objective 2 says existing narrative "must not silently influence" the reconstruction, and these files are hand-written prose a reconstruction could too easily lean on instead of re-deriving from source; held out for safety, reintroduced at reconciliation same as the rest |

This table is a judgment call, not a mechanical fact — flagged for
explicit confirmation at §8 before Phase 3 dispatches are written.

### 3.3 Run the preflight probe, honestly, before trusting anything to it

Per `mechanical-isolation.md`: before the real Phase 3 dispatch, run the
five-route probe (filesystem, search, command execution, network,
environment identity) against the **exact dispatch configuration** Phase
3 will use (same tool grant, same `Agent` call shape), and capture the
**raw tool-call transcript**, not a self-reported summary — this is the
corrected lesson from CodeCompass's own `decisions/0066` (a self-reported
"I didn't look" is not evidence; the transcript is).

Concretely: dispatch a throwaway probe agent with the same tool grant
Phase 3's `implementation-reconstructor` dispatch will have, instructed
to attempt (and report the raw result of) each of:
1. Reading `README.md` by its real path.
2. `grep`/`glob` for a distinctive phrase known only to exist in the
   excluded docs.
3. Any shell command that could reach excluded content indirectly
   (`find`, `git show HEAD:README.md`, etc.).
4. A network fetch of `https://raw.githubusercontent.com/ctosullivan/
   ledgerkit/main/README.md` (or equivalent) — **expected to succeed**,
   per §1.1's finding, since Ledgerkit is also a public repo and `Bash`
   is granted.
5. `pwd`/`hostname` compared against the main session's, to confirm
   whether this is genuinely a separate environment or a same-host
   context.

### 3.4 Report the tier honestly — two tracks, not one

Following the template's own rule: label the result `verified` only if
every probe failed to reach excluded content using a genuinely separate
environment; `best-effort` if isolation is scoped-input/instructed-
compliance only; `filesystem-only, network-exposed` if filesystem/search/
command probes fail but the network probe succeeds. **Given §1.1's
finding, the honestly expected outcome is `filesystem-only,
network-exposed` or `best-effort`, not `verified`** — this phase plans to
report that outcome accurately rather than engineer around it or round
it up. Phase 6's final validation (§6) reports this as its own
separately-tracked criterion, never folded into an overall "done".

### 3.5 Phase 2 acceptance criteria

- `dev-docs/clean-room/` exists with the adopted template, adapted paths.
- The evidence/excluded boundary table (§3.2) is written down and
  confirmed, not re-litigated per-dispatch later.
- A real preflight-probe transcript exists (not a summary), with an
  honest tier label recorded before any Phase 3 dispatch runs.

### 3.6 Files/components touched

- `dev-docs/clean-room/` (new: README.md, worked-example.md,
  mechanical-isolation.md, conceptual-documentation-guide.md, seven
  `TEMPLATE.md` skeletons, an `isolation-preflight.md` probe-transcript
  record).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md`.

---

## 4. Phase 3 — Clean-room evidence gathering + independent reconstruction

**Goal:** build Ledgerkit's actual conceptual understanding from primary
evidence only, freeze it, then independently check it — satisfying
Objective 3 in full.

### 4.1 Scope into bounded topics (not one giant pass)

A single unscoped "understand all of Ledgerkit" dispatch is exactly what
Objective 6's "substantial cross-section... not a trivial sample"
requirement is trying to prevent being faked by a shallow pass. Scope by
Ledgerkit's real module boundaries (confirmed inventory, this session: 19
modules, ~6,700 lines, 6 test directories):

| Topic | Primary source | Primary tests |
|---|---|---|
| Journal format & parsing | `parser.py` (1,721 lines), `models.py` | `tests/test_parser/`, `tests/test_directives/` |
| Multi-commodity / amount styling | `commodity_style.py`, `models.py` | `tests/test_parser/` (styling cases) |
| Query engine (AST/parser/eval/regex/depth/compat shim) | `ledgerkit/query/*` | `tests/test_query/` |
| Tags | `tags.py` | (tag tests, wherever they live — confirm location, don't assume) |
| Reports & CLI | `reports.py`, `cli.py`, `writer.py` | `tests/test_cli/`, `tests/test_reports.py` |
| Validation checks | `checks.py` | `tests/test_checks/` |
| Multi-file loading | `loader.py` | `tests/test_loader/` |
| Editor-facing surface | `editor_model.py`, the frozen API list in... *(excluded — re-derive from `ledgerkit-editor`'s actual real-world usage, same method Stage B Phase 1 already used independently)* | external repo, read-only clone |
| Compatibility system | `dev-docs/compat-register/*.yaml` (evidence, not excluded, per §3.2) | `compat-differential-tester`'s existing evidence trail |
| Project state / what's shipped vs. deferred | git tags, `pyproject.toml` version, actually-passing test count, actually-implemented CLI flags (run `--help`, don't read `ROADMAP.md`) | live repo state |

Each topic gets its own bounded `implementation-reconstructor` dispatch —
same discipline as the existing per-phase agent dispatches elsewhere in
this project, just with a stricter "never open these paths" instruction
set derived from §3.2's table.

### 4.2 Per topic: assertions → snapshot → reconstruction → comparison

For each topic in §4.1:
1. **Assertions** (`dev-docs/clean-room/assertions/<topic>/<id>.md`):
   a first pass (not model-blind — this is the "what do we currently
   believe" pass, built from evidence, same exclusion boundary) writes
   dated, evidence-cited claims using the template's fields (`Statement`,
   `Kind`, `Basis`, `Evidence`, `Evidence-support state`, `Status`).
2. **`domain-skeptic` adversarial review**, then **freeze** into
   `dev-docs/clean-room/snapshots/<topic>-v1.md` (+ a machine-checkable
   sidecar: assertion ids + content hash + repo revision — the template's
   lighter-weight version of CodeCompass's own snapshot mechanism, no
   full YAML-schema validator needed per §3.1).
3. **Independent `implementation-reconstructor` dispatch**, model-blind
   and legacy-blind per §3.2's boundary, never shown the assertions or
   the snapshot — builds its own understanding of the same topic from
   primary evidence alone.
4. **`domain-skeptic` comparison**
   (`dev-docs/clean-room/implementation-comparison/<topic>.md`):
   classify each assertion `aligned`/`partial`/`conflicting`/
   `not_implemented`/`insufficiently_verified` against the independent
   reconstruction. Per the template's own rule (§
   `conceptual-documentation-guide.md`): **alignment is not
   verification** — an `aligned` finding on a rule/invariant means the
   current implementation matches the stated rule, not that the rule
   itself is correct. Never auto-promote a Claim's status off an
   `aligned` finding alone.

### 4.3 Phase 3 acceptance criteria

- Every topic in §4.1's table has: a frozen snapshot, an independent
  reconstruction record, and a comparison report.
- No comparison report was produced by the same dispatch that wrote the
  snapshot it's comparing against (independence is structural, checked
  by looking at which dispatch produced which file, not asserted).
- At least one `conflicting` or `not_implemented` finding is treated as
  an expected, healthy outcome if found (it means the check is real) —
  not papered over.
- Coverage check (informational, run *after* reconstruction, never fed
  into it): every public symbol currently listed in `dev-docs/
  api-spec.md` has at least one corresponding assertion somewhere in the
  snapshots. Gaps are logged as findings for Phase 5, not silently
  dropped.

### 4.4 Files/components touched

- `dev-docs/clean-room/assertions/**`, `snapshots/**`,
  `implementation-comparison/**` (new content, per topic).
- `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-3.md`.
- No `ledgerkit/`/`tests/` code touched.

---

## 5. Phase 4 — Draft replacement documentation

**Goal:** Objective 4 — a coherent documentation set generated from the
frozen snapshots, never from old prose.

### 5.1 What gets drafted

At minimum (per the task): an accurate `README.md`, an architecture
document, a usage/development document, and a project-state/roadmap
document. Concretely, drafted as **new files** first (never edited in
place over the old ones, so the old versions remain available for Phase
6 comparison):

- `README.md.clean-room-draft` (or a scratch location — decide at
  implementation time; must not overwrite `README.md` before Phase 6).
- `dev-docs/architecture.md`-equivalent draft.
- A usage/development draft (`docs/usage.md` + `docs/getting-started.md`
  scope, or merged — let the snapshot's own shape decide the structure,
  per `conceptual-documentation-guide.md`'s "pick an architecture from
  the material, not a template").
- A project-state/roadmap draft — **derived from live repository state**
  (git tags, test count, actually-implemented CLI surface, actually-open
  compat-register `unexplained_mismatch` count — currently zero per
  Stage C closeout) **not from reading `ROADMAP.md`'s own narrative**.

### 5.2 Drafting discipline

- One fresh, isolated drafting pass per document (per
  `conceptual-documentation-guide.md`: "a fresh, isolated pass... tends
  to produce a more honest fit than reusing whatever structure worked
  last time").
- Every sentence traces to a snapshot citation
  (`<topic-slug>@v1#<assertion-id>`) or is flagged as the author's own
  structural/editorial choice (not a factual claim). A sentence that
  doesn't trace to anything is a drafting defect, fixed by going back to
  the snapshot's coverage — not softened into vaguer language.
- Confidence language matches the comparison's own findings: an
  `aligned`, directly-observable-behaviour claim can say "does X"; a
  `rule`/`invariant`-basis claim that's only `aligned` (not independently
  verified as *correct*, only as *currently matching*) gets hedged
  accordingly, per §4.2's rule.

### 5.3 Phase 4 acceptance criteria

- Four draft documents exist, each traceable sentence-by-sentence to a
  Phase 3 snapshot.
- Zero reads of `README.md`/`docs/**`/`dev-docs/architecture.md`/
  `dev-docs/api-spec.md` by the drafting dispatch (checked via its tool-
  call transcript, same discipline as §3.3).
- Drafts committed as their own files before Phase 6 touches the old
  documentation at all (enforces "draft before reconciling").

### 5.4 Files/components touched

- New draft documents (exact paths decided at implementation time, kept
  out of the way of `README.md`/`docs/**` until Phase 6).
- `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-4.md`.

---

## 6. Phase 5 — Legacy reconciliation

**Goal:** Objective 5, verbatim — only now is the old documentation
reintroduced, and only for comparison.

### 6.1 Classification

For every claim the old `README.md`/`docs/**`/`dev-docs/architecture.md`/
`dev-docs/api-spec.md`/`dev-docs/hledger-compatibility.md` made, classify
using the template's own five-way scheme (matches the task's four-way
scheme with one useful split):

- `supported` — new evidence backs it; keep, ideally cited to its
  snapshot now.
- `stale_or_contradicted` — new evidence contradicts it, or it describes
  something that no longer exists; drop.
- `rationale_requiring_verification` — claims a *reason why*, not just a
  *what*; the "what" may be `supported` while the "why" needs its own
  check — maps to the task's "genuine ambiguity requiring investigation".
- `useful_example` — not an assertion, but a concrete illustration worth
  deliberately retaining — maps to the task's "historical/contextual
  material worth deliberately retaining".
- `obsolete` — no longer relevant at all; drop.

Report: `dev-docs/clean-room/legacy-reconciliation/<topic>.md`, one per
Phase 4 document (or per Phase 3 topic — whichever keeps each report
readable).

### 6.2 The rule that matters more than the classification scheme

Per the template: **a `docs-maintainer`-equivalent fix happens as part of
this step, not just a log entry.** Any `supported` claim missing from the
Phase 4 draft gets added, cited to its snapshot. Any `rationale_requiring_
verification` item either gets a quick targeted check (reading the actual
code/test it concerns) resolved into `supported` or `stale_or_contradicted`,
or stays open and is said so explicitly in the published doc rather than
silently dropped. **No old statement is copied into the new documentation
without either independent support (a snapshot citation) or an explicit
historical/intent label** — this is Objective 5's hard requirement,
repeated here because it's the one most likely to get quietly violated
under time pressure.

### 6.3 Replace the live documents

Only now: `README.md`, `docs/**`, `dev-docs/architecture.md`,
`dev-docs/api-spec.md` (subject to the Unauthorised Change Rule — flag
exactly what changes there, per CLAUDE.md, before touching it) are
actually overwritten with the reconciled content. The pre-reconciliation
drafts and the old documents both remain recoverable via git history —
nothing is deleted from version control, only from the live tree.

### 6.4 Phase 5 acceptance criteria

- Every old-doc claim classified; none silently dropped without a
  recorded reason.
- Every live documentation file post-reconciliation traces its
  substantive claims to a Phase 3 snapshot or an explicit historical-
  material label.
- `dev-docs/api-spec.md` changes (if any) go through the Unauthorised
  Change Rule's "state exactly what would change, ask first" step before
  being applied, same as any other protected-file edit.

### 6.5 Files/components touched

- `README.md`, `docs/**`, `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md` (reconciled, live-replaced).
- `dev-docs/clean-room/legacy-reconciliation/**` (new).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-5.md`.

---

## 7. Phase 6 — Final validation

**Goal:** Objective 6, as an explicit, separately-reported audit — not
folded into a single "done".

### 7.1 Checks, each reported as its own line item

1. **CodeCompass actually upgraded/reconciled**: `codecompass check`
   clean; `query source-symbol` reflects current source; all four
   existing agent briefs diffed-and-merged (not blind-copied); the two
   new roles present and adapted.
2. **Clean-room isolation enforced**: the §3.3 preflight-probe transcript
   exists and its honest tier label (§3.4) is reported as its own line —
   expected `best-effort` or `filesystem-only, network-exposed`, **not**
   `verified`, and that is reported as the accurate result, not a defect
   to explain away.
3. **Substantial cross-section, not a trivial sample**: every topic in
   §4.1's table has a snapshot + comparison; a coverage count (e.g. "N of
   M `api-spec.md` symbols have a backing assertion") is reported as a
   number, not asserted qualitatively.
4. **Provenance exists**: spot-check (independent — not the drafting
   dispatch) a sample of sentences in each Phase 4/5 document, confirming
   each traces to a real snapshot citation.
5. **Internal consistency**: a fresh read-only pass (`docs-reconstructor`-
   style) checks the final document set against each other and against
   actual CLI/test behaviour — same discipline as the existing per-phase
   drift audit, run once across the whole new set.
6. **Tests green**: `python -m unittest discover -s tests -t . -v` — this
   phase never touches `ledgerkit/`, so this is a regression guard that
   should trivially pass; still run and reported, per CLAUDE.md's Testing
   Rules and Commit & Push Cadence.

### 7.2 Dispatch this to `release-phase-auditor`

Same as every other phase in this project — an independent, read-only
Definition-of-Done audit, verdict `PASS` / `PASS WITH NON-BLOCKING
OBSERVATIONS` / `FAIL`, run against exactly the six items in §7.1 plus
this project's ordinary phase checklist (retro exists, docs reconciled,
commit/push done, no unauthorised protected-file edit).

### 7.3 Phase 6 acceptance criteria

- All six §7.1 items reported as separate, honestly-labelled results.
- `release-phase-auditor` verdict recorded.
- A substantive closeout retro (`dev-docs/retros/
  CODECOMPASS-UPGRADE-CLEANROOM-DOCS-CLOSEOUT.md`), synthesising all six
  phases, same style as `STAGE-C-CLOSEOUT.md`.
- `ROADMAP.md` updated **only if** the human confirms this initiative
  complete (never inferred) — per the standing "never mark done
  unilaterally" rule.

---

## 8. Open questions needing explicit confirmation before Phase 1 starts

1. **Where does this sit in `ROADMAP.md`?** Recommendation: a new
   section parallel to the Stage A–I ladder (§1), not a Stage letter.
   Needs a yes.
2. **The evidence/excluded boundary table (§3.2)**, specifically:
   should `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md`
   really be excluded from the blind reconstruction stage? They're
   evidenced decision records, not pure narrative, but excluding them is
   the safer reading of Objective 2. Needs a yes/no.
3. **`CLAUDE.md`'s stale folder-structure diagram (§2.4)** — fix it in
   passing during Phase 1, or leave it (it's a pre-existing, unrelated
   drift this task happened to notice, not something it caused)? Needs a
   decision either way before Phase 1 touches `CLAUDE.md` at all.
4. **Is the six-phase breakdown (§2–§7) the right granularity**, or
   should some phases merge (e.g. Phase 1+2, which are both
   process/tooling setup with no doc-content output yet)? This affects
   how many separate retros get written — each phase here gets one, per
   `dev-docs/retros/README.md`'s per-phase cadence, so six phases means
   six retros plus this planning document's own.
5. **Scope of Phase 4's drafted document set (§5.1)** — confirm "README,
   architecture, usage/development, project-state/roadmap" is the
   complete target list, or whether `dev-docs/hledger-compatibility.md`
   (currently a separate, heavily-maintained document) should also be
   in-scope for clean-room redrafting or stay reconciliation-only (its
   content is unusually evidence-dense already, via the compat-register,
   so a full redraft may be lower-value than for the other four).

---

## 9. Non-goals

- **Not importing CodeCompass's own Claim/Evidence/snapshot-integrity
  validator tooling** (`scripts/check_knowledge_base.py`'s enum/
  block-list/historical-integrity checks). That machinery is sized for
  CodeCompass's own much larger, long-lived knowledge base; the portable
  template's plain-markdown skeletons are the right-sized adoption for
  Ledgerkit (§3.1).
- **Not adopting the other seven new upstream agent roles**
  (`context-evaluator`, `context-health-planner`, `context-researcher`,
  `knowledge-curator`, `reference-project-tester`, `context-enrichment-
  agent`, `documentation-agent`) — those serve CodeCompass's own
  dependency-graph knowledge base, which Ledgerkit (zero mandatory
  dependencies) has essentially no use for today, consistent with
  `04-codecompass-integration.md` §4.2's existing "narrow, near-term
  usage" framing.
- **Not attempting to achieve mechanically-`verified` isolation.**
  CodeCompass's own `decisions/0066` and the template's
  `mechanical-isolation.md` already establish this isn't achievable with
  this project's available tools against a publicly-hosted repo; this
  phase reports the honest `best-effort`/`filesystem-only,
  network-exposed` outcome rather than chasing an unachievable `verified`
  label. (CodeCompass's own, separate, explicitly unscheduled backlog
  item for a future mechanically-enforced mechanism —
  `planning/strict-isolation-for-documentation-reconstruction.md` — is
  noted but not something this phase can pull forward.)
- **Not running a `propagation` demonstration** (the template's eighth
  stage: a disposable-fixture test that a source change surfaces as
  staleness in the frozen snapshot). Valuable for a knowledge base that
  will be maintained indefinitely; lower priority for a first adoption
  pass whose main deliverable is the documentation itself, not the
  long-term staleness-detection mechanism. Can be added in a later phase
  if Ledgerkit's documentation starts drifting again post-reconstruction.
- **Not touching `ledgerkit/` or `tests/` source code at all.** Every
  phase here is tooling and documentation; zero behaviour change, zero
  new compat-register entries expected.
- **Not reopening any Stage C decision** or beginning Stage D. This
  phase is explicitly ordered before Stage D starts, not a substitute for
  scoping it.
- **Not treating CodeCompass's `codecompass-template` repo as something
  Ledgerkit depends on or vendors long-term** — it's a one-time adoption
  source (clone, copy what's needed, done); Ledgerkit does not track it
  as an ongoing upstream the way it tracks `codecompass` itself via
  CodeCompass's own package-dependency mechanism.

---

## 10. Sequencing summary

```
Phase 1 (CodeCompass reconciliation)
   ↓ unblocks: current agent roster, current generated artifacts
Phase 2 (isolation mechanism adopted + preflight-probed)
   ↓ unblocks: a trustworthy exclusion boundary for Phase 3
Phase 3 (per-topic: assertions → snapshot → independent reconstruction → comparison)
   ↓ unblocks: evidence-backed, provenance-carrying material to draft from
Phase 4 (draft new README/architecture/usage/roadmap from snapshots alone)
   ↓ unblocks: something to reconcile against
Phase 5 (reintroduce old docs, classify, reconcile, replace live documents)
   ↓ unblocks: a final, real documentation set to audit
Phase 6 (independent release-phase-auditor DoD audit, closeout retro)
```

Each phase gets its own retro (`dev-docs/retros/
CODECOMPASS-UPGRADE-PHASE-<N>.md`), per the existing per-phase cadence,
and its own commit (pushed on success, per CLAUDE.md's Commit & Push
Cadence — nothing here is pushed if its own phase's checks don't pass).
Phase 3 and Phase 4 are the only phases expected to need more than one
dispatch round each (one per topic in §4.1's table); Phases 1, 2, 5, and
6 are each a single bounded unit of work.

---

## 11. Validation commands (for use at each phase's own gate)

```
# Phase 1
codecompass sync
codecompass index
codecompass check
codecompass query source-symbol
python -m unittest discover -s tests -t . -v

# Phase 2 (preflight probe — illustrative; exact commands depend on the
# dispatch configuration actually used)
curl -sI https://raw.githubusercontent.com/ctosullivan/ledgerkit/main/README.md
grep -r "<distinctive-excluded-phrase>" .   # from inside the probe dispatch

# Phase 6 (final)
python -m unittest discover -s tests -t . -v
codecompass check
# release-phase-auditor dispatch against §7.1's six items
```

No new test files are anticipated for `tests/` — this phase produces
documentation and process artifacts, not executable behaviour. If Phase 1
or Phase 2 tooling work turns out to need a disposable fixture (e.g. to
test the preflight probe safely), it goes in a scratch location, never
`tests/`, matching the template's own "disposable fixture, deleted after"
discipline.

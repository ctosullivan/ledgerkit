# 29. CodeCompass upgrade + clean-room documentation reconstruction

**Status:** Amended twice (both 2026-10-02) and **approved to proceed
directly to implementation**, per direct user instruction accompanying
the second amendment. No further planning round-trip is required unless
a genuinely new blocking condition makes this plan impossible to execute
safely — see §13 for the implementation log this status now points to.

**Amended 2026-10-02** per review findings, same day as the original
plan. The six-phase structure and overall intent are unchanged. This
amendment: moves every comparison against existing documentation out of
Phase 3 and into Phase 5 (§4.3, §6); adds a complete documentation
inventory/disposition table so Phase 4's drafted set matches Phase 5's
replaced set exactly (§5.1); separates reconstructable current-state fact
from forward-looking roadmap intent (§5.1, §6.1); adds a small
deterministic snapshot-integrity checker that gates Phase 4 (§3.7, §4.2);
corrects the isolation success criterion so `best-effort` is never
reported as "enforced" (§7.1); adds revision-pinning for CodeCompass and
`codecompass-template` at Phase 1 start (§2.0); tightens the treatment of
`dev-docs/compat-register/*.yaml` and `ledgerkit-editor` as *derived*
rather than *primary* evidence (§3.2, §4.1); fixes several places that
named the wrong phase for when old documentation is first touched; and
resolves all five of the original plan's open questions (§8, now a
decisions log rather than a question list). All five of the original
open questions are resolved by this amendment, per direct user
instruction — none remain open.

**Amended a second time, 2026-10-02**, per a second review covering 8
further corrections, with explicit instruction to implement immediately
afterward. The six-phase structure, hard invariant, document inventory,
revision-pinning concept, best-effort isolation model, and Phase 5
legacy-reconciliation placement are all **unchanged** — this amendment
only strengthens *how* each is actually executed: assertion-research is
now a structurally separate fresh dispatch from the main orchestrator,
never authored by the orchestrator directly (§4.2, §8 Finding C1); the
CodeCompass/`codecompass-template` pin is now mechanically enforced, not
merely recorded (§2.0, §8 Finding C2); `check_snapshot.py` now validates
against the frozen git revision's own historical tree, never today's
working tree (§3.7, §8 Finding C3); boundary-compliance checking happens
immediately after every isolation-sensitive Phase 3/4 dispatch, logged
to `dev-docs/clean-room/compliance-log.md`, with Phase 6 auditing that
log rather than performing the first contamination check itself (§4.2a,
§5.4, §8 Finding C4); the inventory/acceptance-criteria contradiction
around intentionally-retained process files is fixed, with ordinary
workflow bookkeeping explicitly distinguished from clean-room
reconstruction scope (§5.1a, §8 Finding C5); commit-message prose is
excluded from clean-room evidence by default, narrowly exceptable and
always flagged when used (§3.2, §8 Finding C6); the
`codecompass-template` file count is corrected to eleven files, not nine
(§1.1, §8 Finding C7); and a second internal-consistency pass is recorded
(§12, §8 Finding C8).

**Trigger:** direct user request (2026-10-02) to (1) bring Ledgerkit's
CodeCompass integration current, then (2) use the upgraded tooling to
reconstruct Ledgerkit's human-facing documentation from primary evidence
only, with old documentation held out of the reconstruction and
reintroduced afterward only for comparison. The first amendment responded
to a direct review of that plan (also 2026-10-02); this second amendment
responds to a further review (also 2026-10-02) that found the first
amendment still implementation-unready in 8 specific ways, and directs
proceeding straight to implementation once fixed.

---

> ## Hard invariant (read before touching any phase)
>
> **No existing human-authored Ledgerkit documentation, and no
> planning/knowledge narrative, may enter the reconstruction or drafting
> context until the first clean-room documentation drafts have been
> completed and committed. Existing narrative may only be reintroduced
> during Phase 5 reconciliation.**
>
> This covers, at minimum: `README.md`, everything under `docs/**`,
> `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
> `dev-docs/hledger-compatibility.md`, `ROADMAP.md`'s own prose,
> `CHANGELOG.md`, `CONTEXT.md`, every `dev-docs/retros/**` and
> `dev-docs/planning/**` narrative document (including this one — Phase
> 3/4 dispatches must not be shown this plan's own prose either, only
> told which topic/files to look at), `knowledge/*.md`, and any narrative
> documentation belonging to an external repository inspected for
> evidence (e.g. `ledgerkit-editor`'s own `README.md`). It applies
> equally to a comparison, a coverage count, or a "does the old doc still
> say X" check against any of the above — not only to direct reading. Any
> plan section below that appears to permit an earlier check against
> existing documentation is an error in that section, not an exception to
> this rule — see §8 Finding F1 below for the specific defect this
> amendment fixes.

---

## 1. What this is, and where it sits

This is **not** a new letter in the Stage A–I accounting ladder
(`ROADMAP.md` §"Stages A–I"). Stage D onward is accounting-feature work
(reporting, semantics, investments); this initiative is cross-cutting
dev-tooling and documentation process work, same category as Stage A's
"Development foundation" bucket but arriving after Stage A already
closed. **Resolved (§8 item 1):** tracked in `ROADMAP.md` as its own
"Tooling & Process Initiatives" section, parallel to the Stage ladder,
never consuming a Stage letter.

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
  `origin` (`git@github.com:ctosullivan/codecompass.git`) was confirmed
  **not ahead** of the local clone at original-planning time (`git fetch`
  showed 0/0 ahead/behind; `HEAD` was `96a1e4d`, 2026-10-02). **This value
  is now historical context only, not an active pin** — §2.0 requires
  Phase 1 to re-fetch and formally record its own pin at its own start,
  since time may have passed between this plan and Phase 1 actually
  running.
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
     upstream built and shipped for exactly this use case (§3) — this is
     the actual answer to Objectives 2–5, not something to design from
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
  re-discovering it, and reports isolation honestly, on separately-named
  axes, never as a single rounded-up "done" (§7.1 — corrected this
  amendment to not call `best-effort` "enforced").
- **CodeCompass published the reusable deliverable at
  `https://github.com/ctosullivan/codecompass-template`**
  (`optional-clean-room-workflow/`): **seven `TEMPLATE.md` format
  skeletons** (`assertions/`, `snapshots/`, `coding-context-selection/`,
  `implementation-comparison/`, `propagation/`, `legacy-reconciliation/`,
  `documentation-verification/`), plus **two judgment-call guides**
  (`mechanical-isolation.md`, `conceptual-documentation-guide.md`), a
  **worked example** (`worked-example.md`), and the workflow directory's
  own **`README.md`** — **eleven files in total** across the directory
  (seven skeletons + two guides + one worked example + one README), not
  nine as the plan's first amendment still miscounted (7+2+1 is ten, not
  nine, and the directory's own `README.md` makes eleven — corrected this
  second amendment, §8 Finding C7, superseding the first amendment's own
  correction at §8 Finding F8, which fixed the "seven, not nine" skeleton
  count but left the arithmetic wrong). Inspected directly (read-only
  clone, scratch directory, original planning session). Its stage
  sequence —
  **assertions → snapshot → independent implementation reconstruction →
  comparison → documentation draft → legacy reconciliation →
  documentation-verification** — maps almost one-to-one onto this task's
  Objectives 3–6. §3 adopts it directly rather than reinventing it.

### 1.2 What this means for scope

Objective 1 ("update CodeCompass") turns out to be **small**: no
dependency bump, no schema migration, no breaking-change absorption.
It is a routine re-sync plus an agent-brief reconciliation plus importing
one new template, now with explicit revision pinning (§2.0). Objectives
2–6 (clean-room documentation) are the real weight of this phase, and
they get to start from a finished, validated upstream methodology
instead of a blank page — subject to the hard invariant above, which
this amendment makes explicit and enforces structurally (§4, §5) rather
than only by instruction.

---

## 2. Phase 1 — CodeCompass reconciliation & re-sync

**Goal:** Ledgerkit's CodeCompass integration reflects the current tool,
pinned to a known revision, with current generated-artifact conventions
and the current agent roster Phase 3 onward needs.

### 2.0 Pin CodeCompass and `codecompass-template` (new this amendment)

Before anything else in this phase:

1. `git fetch origin` inside `/home/cormac/projects/codecompass`; record
   the exact `HEAD` SHA actually used for the rest of this initiative.
2. Clone (read-only, scratch or a durable local path — implementation's
   choice) `https://github.com/ctosullivan/codecompass-template`;
   `git fetch origin`; record its exact `HEAD` SHA too.
3. Write both SHAs, the fetch timestamp, and the fetch command's literal
   output into `dev-docs/clean-room/PINNED-REVISIONS.md` (this file is
   this phase's first write into that directory — Phase 2, §3.1, adds the
   rest of the directory's content afterward).
4. **Every subsequent phase of this initiative operates against exactly
   these two pinned revisions.** If CodeCompass or `codecompass-template`
   publish new commits while this initiative is still in progress, that
   is **not** silently picked up — using a newer revision requires a new,
   explicit, recorded decision (a short note in
   `PINNED-REVISIONS.md` plus a `CHANGELOG.md` entry), the same
   discipline this project already applies to any other version bump.
   "Current version" does not mean "whatever `git pull` returns today";
   it means "the SHA this file names," for the duration of the
   initiative.
5. **Enforce the pin, not merely record it (§8 Finding C2 — a recorded
   SHA nothing ever checks against is a note, not a pin).** Preferred
   mechanism: create a dedicated, fixed `codecompass` checkout at exactly
   the pinned SHA — `git -C /home/cormac/projects/codecompass worktree
   add <fixed-path> <pinned-sha>` — and point the installed
   `codecompass` entry point at that fixed worktree (re-run `pipx install
   -e <fixed-path> --force`, or equivalent, so the executable imports
   from the pinned worktree, never from `/home/cormac/projects/
   codecompass`'s own `HEAD`, which can keep moving independently of this
   initiative). Apply the same discipline to `codecompass-template`: the
   clone made in step 2 above *is* the fixed checkout — never
   `git pull` it again during this initiative; every file copied/adapted
   from it (§3.1) comes from that exact clone, confirmed by `git -C
   <clone-path> rev-parse HEAD` matching `PINNED-REVISIONS.md`
   immediately before each copy, not assumed to still match.
6. **If the dedicated-worktree approach is not taken** (e.g. recreating
   the editable install mid-initiative proves disruptive to the
   environment), **a mechanical guard runs before every
   `codecompass`-dependent operation in every later phase**, not just
   once here: resolve the checkout the installed executable actually
   imports from (`pip show -f codecompass-context`, or reading the
   editable install's own `direct_url.json` back to its source path),
   run `git -C <that-path> rev-parse HEAD`, and compare it byte-for-byte
   against the SHA recorded in `PINNED-REVISIONS.md`. **If they differ,
   stop — do not silently continue against a moved checkout.** This is a
   short, reusable guard (`dev-docs/clean-room/check_codecompass_pin.sh`
   or equivalent), run immediately before every `codecompass sync`/
   `index`/`check`/`query` invocation from Phase 1 onward, with its
   pass/fail result logged next to the command's own output, not merely
   trusted silently.
7. Whichever mechanism is used, Phase 6 (§7.1 item 1) independently
   re-confirms it was actually exercised throughout this initiative — not
   just that `PINNED-REVISIONS.md` contains correct-looking text.

### 2.1 Re-sync against current (pinned) source

- **Before each command below, confirm the pin is enforced** (§2.0 steps
  5–6: either the installed executable resolves to the dedicated
  worktree, or the guard script has just passed) — stop rather than
  proceed if it hasn't been confirmed this phase.
- Run `codecompass sync` (whole-project, no vendor arg) from the
  Ledgerkit root, using the pinned revision from §2.0. Expected:
  `context-graph.db` rebuilt, `source_files`/`source_symbols` now reflect
  `ledgerkit/query/*`, `ledgerkit/tags.py`, and every other file
  added/changed since 2026-09-24.
- Run `codecompass index` to regenerate the `CLAUDE.md` routing-table
  marker block and `.claude/skills/codecompass/SKILL.md`.
- Run `codecompass check` again post-sync; expect a clean report (it was
  already clean pre-sync, so this mainly confirms the re-sync didn't
  regress anything).

### 2.2 Reconcile local agent-brief copies against upstream originals

Confirmed by direct diff (original planning session, against the pinned
revision from §2.0): Ledgerkit's `.claude/agents/docs-reconstructor.md`
(92 lines) is a materially older, shorter revision of CodeCompass's
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
1. Diff against the pinned `codecompass` repo's `.claude/agents/<name>.md`.
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

Adopt both briefs from the pinned `codecompass` revision's
`.claude/agents/`, adapted the same way as §2.2 (path/convention mapping,
not verbatim copy). The other new upstream roles (`context-evaluator`,
`context-health-planner`, `context-researcher`, `knowledge-curator`,
`reference-project-tester`, `context-enrichment-agent`,
`documentation-agent`) are CodeCompass's own internal roles for building
*its* knowledge base — **not adopted**; see §9 non-goals.

### 2.4 Incidental finding, resolved this amendment: fix the stale folder-structure diagram

`CLAUDE.md`'s "Folder Structure" diagram (the protected-without-approval
one) already does not match reality — it lists `ledgerkit/{parser,
models, reports, cli}.py` only, omitting `checks.py`, `writer.py`,
`loader.py`, `tags.py`, `commodity_style.py`, `editor_model.py`,
`_pandas_compat.py`, and the whole `query/` subpackage, all of which
already exist and are already tested. **Resolved (§8 item 3): fix this
in passing during Phase 1.** It is a correction to an already-inaccurate
diagram, not a structural change, but still goes through the
Unauthorised Change Rule's "state exactly what would change" step before
being applied, since `CLAUDE.md`'s folder structure is a protected
section regardless of intent.

### 2.5 Phase 1 acceptance criteria

- `dev-docs/clean-room/PINNED-REVISIONS.md` exists, naming exact SHAs for
  both `codecompass` and `codecompass-template`, with a fetch timestamp.
- **The pin is mechanically enforced, not just recorded** (§2.0 steps
  5–7): either a dedicated worktree exists and the installed executable
  demonstrably resolves to it, or `check_codecompass_pin.sh` (or
  equivalent) exists and was run successfully at least once this phase,
  with its result logged.
- `codecompass check` clean (no severity findings) after re-sync.
- `codecompass query source-symbol` returns entries for `ledgerkit/query/*`
  and `ledgerkit/tags.py` (proof the re-sync actually picked up Stage C's
  code).
- All four existing agent briefs diffed against the pinned upstream
  revision; every delta classified (adopt/map/preserve) and merged; no
  blind overwrite.
- `implementation-reconstructor.md` and `domain-skeptic.md` exist under
  `.claude/agents/`, adapted to Ledgerkit's path/doc conventions.
- `CLAUDE.md`'s CodeCompass section updated to reflect current tool
  state, the roster addition, and a pointer to this document; its
  folder-structure diagram corrected per §2.4.
- `04-codecompass-integration.md` updated to point at this document.
- Full test suite still green (`ledgerkit/` untouched this phase, so this
  is a regression guard, not expected to find anything).

### 2.6 Files/components touched

- `context-graph.db`, `vendor.toml` (regenerated, gitignored local state).
- `dev-docs/clean-room/PINNED-REVISIONS.md` (new).
- `dev-docs/clean-room/check_codecompass_pin.sh` (new, only if the guard
  approach is used instead of a dedicated worktree).
- `CLAUDE.md` (CodeCompass section + routing-table marker block,
  regenerated; folder-structure diagram corrected per §2.4).
- `.claude/skills/codecompass/SKILL.md` (regenerated).
- `.claude/agents/{docs-reconstructor,docs-maintainer,release-phase-auditor,
  roadmap-context-curator}.md` (reconciled).
- `.claude/agents/{implementation-reconstructor,domain-skeptic}.md` (new).
- `dev-docs/planning/core-redefinition/04-codecompass-integration.md`
  (status update, §4.7-style routine-workflow note).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md`.

---

## 3. Phase 2 — Isolation mechanism (adopted, not designed) + snapshot-integrity checker

**Goal:** a concrete, honestly-labelled isolation mechanism, and a
deterministic guard against a malformed snapshot, both exist before any
real reconstruction content is produced.

### 3.1 Adopt the template directly

Copy the pinned `codecompass-template` revision's
`optional-clean-room-workflow/` directory into Ledgerkit as
`dev-docs/clean-room/` (alongside the `PINNED-REVISIONS.md` Phase 1
already created there; name chosen for Ledgerkit's own `dev-docs/`
convention — the template says the directory may be renamed). Keep its
seven `TEMPLATE.md` skeletons (`assertions/`, `snapshots/`,
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
documentation set is disproportionate — see non-goals (§9). §3.7 below
adds a much smaller, Ledgerkit-specific checker instead.

### 3.2 Define Ledgerkit's actual exclusion boundary

Before any dispatch, fix explicitly what is **evidence** (visible to the
reconstruction) vs. **excluded narrative** (held out until Phase 5, per
the hard invariant):

| Category | Treatment | Rationale |
|---|---|---|
| `ledgerkit/**/*.py` source | Primary evidence | Objective 3's "source code as a first-class evidence object" |
| `tests/**`, `tests/fixtures/**` | Primary evidence | Objective 3 |
| `pyproject.toml`, `MANIFEST.in` | Primary evidence | build/config |
| CLI `--help` output, actual command runs | Primary evidence | "CLI/API behaviour" |
| hledger manual / source (pinned reference) | Primary evidence (external authoritative spec) | explicitly listed in Objective 3 |
| `ledgerkit-editor`'s own source + tests (not its docs) | Primary evidence, narrow | the one external-repo case this project already has precedent for (Stage B Phase 1's independent import inventory) — restricted to source/tests only, per §4.1 |
| `dev-docs/compat-register/*.yaml` | **Derived evidence index, not primary evidence** | a structured pointer to real evidence (a differential-test run against the pinned hledger reference), not itself proof — a material claim sourced from a compat-register entry must trace through to that entry's own underlying verification, or get a targeted re-check (see §4.1, §7) |
| Git history — **tree/diff/content only** (`git show <rev>:<path>`, `git diff`), used only where current behaviour cannot be established from source/tests/current CLI behaviour alone | Evidence, narrowly, **content only** | Objective 3's "version history only where needed" — prefer actual historical file contents and diffs over commit-message prose. **Resolved (§8 Finding C6): commit-message text is human-authored narrative and is excluded by default**, same reasoning as any other narrative — usable only as a narrowly-justified exception, named explicitly in the assertion's own `Evidence` field as `"commit-message exception: <reason>"`, never consumed as routine clean-room explanatory evidence |
| `README.md`, `docs/**`, `dev-docs/architecture.md`, `dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md` | **Excluded until Phase 5** | exactly the narrative documentation the hard invariant requires held out |
| `ROADMAP.md`'s own prose (forward-looking Stage/backlog content) | **Excluded until Phase 5** | project *intent*, not reconstructable from the current tree — see §5.1, §6.1 |
| `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/**`, `dev-docs/planning/**` prose (including this document's own prose) | **Excluded until Phase 5** | historical/process narrative, not primary evidence of current behaviour |
| `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` | **Excluded until Phase 5** | **Resolved (§8 item 2):** stays excluded during blind reconstruction even though these are evidence-cited decision records, not pure narrative — reintroduced at Phase 5 specifically as *rationale/intent* evidence (the "why", distinct from the "what" a clean-room pass can observe directly), never consumed earlier |

This table was a judgment call in the original plan; §8 below now
records it as **resolved**, not open.

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

### 3.4 Report the tier honestly — never call it "enforced"

Following the template's own rule: label the result `verified` only if
every probe failed to reach excluded content using a genuinely separate
environment; `best-effort` if isolation is scoped-input/instructed-
compliance only; `filesystem-only, network-exposed` if filesystem/search/
command probes fail but the network probe succeeds. **Given §1.1's
finding, the honestly expected outcome is `filesystem-only,
network-exposed` or `best-effort`, not `verified`.**

**Corrected this amendment (§8 Finding F5):** this tier label describes *how
strong the isolation mechanism is*, never *whether the clean-room
workflow was followed*. Those are two different, separately-reported
facts, both carried through to Phase 6 (§7.1):
- the **tier achieved** (this probe's own honest label), and
- **compliance** — whether each real Phase 3/4 dispatch's own tool-call
  transcript actually stayed inside the exclusion boundary it was given,
  which the probe does not by itself demonstrate (the probe tests what
  the mechanism *could* reach; compliance checks what a real dispatch
  *actually did* reach). Never phrase either of these as "isolation
  enforced" — `best-effort` is a disclosed limitation of the mechanism,
  not something that becomes "enforced" by a dispatch behaving correctly
  once.

### 3.5 Phase 2 acceptance criteria

- `dev-docs/clean-room/` exists with the adopted template, adapted paths,
  alongside Phase 1's `PINNED-REVISIONS.md`.
- The evidence/excluded boundary table (§3.2) is written down and
  resolved (§8), not re-litigated per-dispatch later.
- A real preflight-probe transcript exists (not a summary), with an
  honest tier label recorded before any Phase 3 dispatch runs.
- The §3.7 snapshot checker exists and runs clean against a trivial
  fixture snapshot (not yet a real one — Phase 3 produces the first real
  snapshot).

### 3.6 Files/components touched

- `dev-docs/clean-room/` (new: README.md, worked-example.md,
  mechanical-isolation.md, conceptual-documentation-guide.md, seven
  `TEMPLATE.md` skeletons, an `isolation-preflight.md` probe-transcript
  record, the §3.7 checker script).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md`.

### 3.7 Ledgerkit-specific snapshot checker (new first amendment; strengthened to true historical-integrity semantics this second amendment, §8 Finding C3)

A small, deterministic, stdlib-only script —
`dev-docs/clean-room/check_snapshot.py` — **not** an import of
CodeCompass's `check_knowledge_base.py` subsystem (§3.1's non-adoption
decision stands; this is a much smaller, Ledgerkit-sized tool, built
fresh). It takes one snapshot (a `dev-docs/clean-room/snapshots/
<topic>-vN.md` + its sidecar) and its referenced
`dev-docs/clean-room/assertions/<topic>/` directory, and **fails closed**
— non-zero exit, a specific reason per failure, never a silent pass — on
any of:

1. **Missing or duplicate assertion IDs** — every assertion file's own id
   must be unique within the topic and must match its filename.
2. **Snapshot hash mismatch** — the sidecar's recorded hash of each cited
   assertion's content must match that assertion file's actual current
   content.
3. **Missing repository revision** — the sidecar must name the exact git
   revision the snapshot was frozen against; absent is a failure, not a
   default.
4. **Referenced assertion records don't exist** — every assertion id the
   sidecar lists must resolve to a real file under `assertions/<topic>/`;
   a dangling reference is a failure.
5. **Recorded revision does not exist as a real git object** — `git
   cat-file -e <revision>^{commit}` (or equivalent) must succeed; a
   sidecar naming a revision that was never committed, or has been
   garbage-collected, is a failure — and a failure here short-circuits
   check 6 below (there is no tree to resolve anything against).
6. **Cited local evidence does not resolve against *that revision's own
   tree* — never today's working tree.** This is the semantic fix §8
   Finding C3 requires: checks 1–4 above are satisfied by comparing
   against files as they exist on disk *right now*, which is correct for
   them (an assertion file's own identity and the sidecar's own hash are
   properties of the assertion, not of history) — but an assertion's
   `Evidence` field makes a claim about the *source tree at the frozen
   revision*, and must be checked against exactly that, not against
   whatever the source tree happens to look like when the checker
   happens to run. Concretely, for every assertion's `Evidence` field
   naming a local file (and, where given, a line number or range):
   - run `git cat-file -e <revision>:<path>` to confirm the file
     **existed at that revision** — a file that only exists in a *later*
     commit (e.g. added by a subsequent, unrelated phase of this same
     initiative) is a failure, even though it exists on disk today;
   - where a line number or range is cited, resolve it against
     `git show <revision>:<path>`'s own content **at that revision**
     (count lines in the historical blob returned by that command), not
     against the file as it currently exists on disk — a citation that
     resolves against the live filesystem but not against the frozen
     revision's own content is a failure, not a pass, since the snapshot
     is making a claim about a specific point in history, not about
     "whatever this path currently contains."

   **Concretely, why this matters:** a snapshot frozen against commit
   `A` that cites `parser.py:412` is a claim about `parser.py` *as it
   existed at `A`*. If `parser.py` is later edited by this same
   initiative's own later work, a checker that only looks at today's
   `parser.py` could wrongly report line 412 "missing" (a false failure
   on an unrelated later edit) or, worse, wrongly report it "present"
   when the line now means something the assertion never claimed (a
   false pass on a citation that no longer actually supports it).
   Resolving against `git cat-file`/`git show <revision>:<path>` instead
   of the live filesystem is what prevents both failure modes.

**This checker must run, and pass, before any Phase 4 drafting dispatch
is given a snapshot to consume.** Phase 3 (§4.2) runs it as the last
mechanical step of freezing each topic's snapshot; Phase 4 (§5.3) treats
"checker passed, against the exact revision still current" as a hard
precondition, re-confirmed rather than assumed, before dispatching any
drafting work against that snapshot.

---

## 4. Phase 3 — Clean-room evidence gathering + independent reconstruction

**Goal:** build Ledgerkit's actual conceptual understanding from primary
evidence only, freeze it, independently check it, and hand off a
validated snapshot — with **zero comparison against any existing
documentation inventory**, per the hard invariant. That comparison moved
to Phase 5 this amendment (§8 Finding F1).

### 4.1 Scope into bounded topics (not one giant pass)

A single unscoped "understand all of Ledgerkit" dispatch is exactly what
Objective 6's "substantial cross-section... not a trivial sample"
requirement is trying to prevent being faked by a shallow pass. Scope by
Ledgerkit's real module boundaries (confirmed inventory, original
planning session: 19 modules, ~6,700 lines, 6 test directories):

| Topic | Primary source | Primary tests | Notes |
|---|---|---|---|
| Journal format & parsing | `parser.py` (1,721 lines), `models.py` | `tests/test_parser/`, `tests/test_directives/` | |
| Multi-commodity / amount styling | `commodity_style.py`, `models.py` | `tests/test_parser/` (styling cases) | |
| Query engine (AST/parser/eval/regex/depth/compat shim) | `ledgerkit/query/*` | `tests/test_query/` | hledger-compatibility claims here trace through compat-register to underlying differential evidence, per §3.2 — never cite the YAML's own `kind` field as if it were the proof |
| Tags | `tags.py` | (tag tests, wherever they live — confirm location, don't assume) | |
| Reports & CLI | `reports.py`, `cli.py`, `writer.py` | `tests/test_cli/`, `tests/test_reports.py` | |
| Validation checks | `checks.py` | `tests/test_checks/` | |
| Multi-file loading | `loader.py` | `tests/test_loader/` | |
| Editor-facing surface | `editor_model.py` | `ledgerkit-editor`'s own **source and tests only** (read-only clone) | **Its narrative documentation (its `README.md`, any docs it ships) is excluded from this blind pass**, same as Ledgerkit's own — restrict strictly to its actual `import ledgerkit` usage in code and tests, same method Stage B Phase 1 already used independently. Do not read its README for "what it's for" framing. |
| Compatibility system | `dev-docs/compat-register/*.yaml` **as an index only** | `compat-differential-tester`'s underlying evidence trail (the actual fixture journals + hledger-binary output each entry cites) | per §3.2: a claim here must resolve to the entry's own cited differential evidence, or trigger a fresh, targeted `compat-differential-tester` re-check against the pinned hledger reference — the YAML's `kind`/`status` fields alone are not sufficient citation |
| Current shipped state (factual only) | git tags, `pyproject.toml` version, actually-passing test count, actually-implemented CLI flags (run `--help`, don't read `ROADMAP.md`), current compat-register `unexplained_mismatch` count | live repo state | **No forward-looking content.** This topic produces facts about what exists *now* only — never a roadmap, never a "planned" item. Feeds Phase 4's current-state draft (§5.1), which is a different document from `ROADMAP.md` itself. |

Each topic gets its own bounded, **structurally separate** dispatches —
one for assertion research, a different one for implementation
reconstruction, never the same dispatch doing both — same discipline as
the existing per-phase agent dispatches elsewhere in this project, just
with a stricter "never open these paths" instruction set derived from
§3.2's table, under the hard invariant at the top of this document. §4.2
specifies the exact separation; **the main orchestrating session never
authors a topic's assertions itself**, regardless of how confident it is
that it already knows the answer.

### 4.2 Per topic: isolated assertion research → domain-skeptic review → frozen/checker-validated snapshot → independent reconstruction → independent comparison (restructured this amendment, §8 Finding C1)

**The main orchestrating session — which has read this governing plan's
own prose in full, and may have been shown legacy documentation earlier
in this or a prior conversation — must never directly author a topic's
clean-room assertions.** This is a structural rule enforced by *who is
allowed to hold the pen*, not an instruction asking the orchestrator to
be careful. Every topic's assertions, and every topic's independent
reconstruction, are each produced by a dispatch that starts from a
genuinely empty context.

For each topic in §4.1:

1. **Dispatch a fresh, evidence-only assertion-research agent.** A brand
   new `Agent` call — **never `subagent_type: "fork"`**, since a fork
   inherits the orchestrator's own conversation context, carrying forward
   exactly the things this step exists to keep out. This dispatch
   receives, in its prompt, **only**:
   - the bounded topic, named exactly as one row of §4.1's table;
   - the exact permitted evidence paths/sources for that topic (the
     `Primary source`/`Primary tests` columns, given as literal paths —
     "look at `ledgerkit/parser.py` and `tests/test_parser/`", never
     "use your judgement about what's relevant to parsing");
   - the assertion output format: the template's `assertions/
     TEMPLATE.md` fields (`Statement`, `Kind`, `Basis`, `Evidence`,
     `Evidence-support state`, `Status`), given as a literal skeleton to
     fill in;
   - the git-history restriction from §3.2 (tree/content commands only;
     commit-message text only as a named, narrow exception);
   - a one-line restatement of the exclusion boundary itself ("do not
     read, search for, or open any file outside the paths named above —
     if you are unsure whether something is in scope, don't open it, and
     say so in your output instead").

   This dispatch **must not receive**, by any route the orchestrator
   controls:
   - legacy documentation (`README.md`, `docs/**`, `dev-docs/
     architecture.md`, `dev-docs/api-spec.md`, `dev-docs/
     hledger-compatibility.md`, `ROADMAP.md`'s prose);
   - existing planning/knowledge narrative (`knowledge/*.md`,
     `dev-docs/planning/**` prose, `dev-docs/retros/**`);
   - **this governing plan's own prose** — the dispatch is told *what to
     look at*, never shown *this document*;
   - pre-existing assertions or a snapshot for this topic (none exist yet
     on a first pass; on a re-run after contamination, the discarded
     output is not shown to the fresh attempt either — see §4.2a);
   - implementation-reconstruction output (step 6 below hasn't run yet,
     and even once it has, this dispatch is never shown it — the two
     reconstructions must stay independent of *each other*, not only of
     legacy docs);
   - prior agent summaries of any kind that could carry legacy framing
     forward — a one-line "here's what the last pass found" handoff is
     exactly the indirect leak this rule exists to prevent.

   Every file this dispatch writes carries a **producer header**: role
   (`assertion-research`), topic, a dispatch id (the `Agent` call's own
   identifier, or a timestamp if none is exposed), and the date.

2. **Immediately inspect this dispatch's real tool-call transcript** for
   boundary compliance, per §4.2a, before anything downstream consumes
   its output. Discard and rerun from a fresh dispatch if contaminated.

3. **`domain-skeptic` adversarial review** of the resulting assertions —
   also a fresh dispatch, also never shown legacy documentation or this
   plan's prose (its job is scrutinising evidence sufficiency and rigour,
   not comparing against old prose), given the assertion-research
   dispatch's output plus the same permitted-evidence-paths list, so it
   can independently re-check a doubtful claim against the source
   itself. Any assertion whose `Evidence` is a compat-register entry must
   additionally cite that entry's own underlying differential-test
   evidence by id/path, not just the entry's filename (§3.2's
   "derived, not primary" rule) — if that underlying evidence can't be
   located, the assertion stays `Evidence-support state: uncertain` until
   a targeted `compat-differential-tester` re-check resolves it.
4. **Freeze** the reviewed assertions into
   `dev-docs/clean-room/snapshots/<topic>-v1.md` (+ a machine-checkable
   sidecar: assertion ids, content hash, and the exact repository
   revision). This step is mechanical bookkeeping over already-produced,
   already-reviewed content — the orchestrator performs it directly, no
   further dispatch needed.
5. **Run `check_snapshot.py` (§3.7), including its historical-integrity
   checks, against the frozen snapshot.** A snapshot that fails the
   checker is not frozen — fix the defect and re-freeze before
   proceeding. Hard gate, not advisory.
6. **Dispatch a different fresh implementation-reconstructor agent** —
   again a brand-new `Agent` call, never a `fork`, given the same kind of
   tightly-scoped prompt as step 1 (bounded topic + permitted evidence
   paths + output instructions), **never shown the assertions, the
   snapshot, this governing plan's prose, or any legacy documentation**
   — builds its own understanding of the same topic from primary
   evidence alone, citing file/line for every claim.
7. **Immediately inspect this second dispatch's transcript** for
   boundary compliance, per §4.2a. Discard and rerun from a fresh
   dispatch if contaminated.
8. **Independent comparison**
   (`dev-docs/clean-room/implementation-comparison/<topic>.md`): a third
   pass — `domain-skeptic` again, or a fresh dispatch, orchestrator's
   choice, but **never the same dispatch that produced either the
   snapshot or the reconstruction** — classifies each assertion
   `aligned`/`partial`/`conflicting`/`not_implemented`/
   `insufficiently_verified` against the independent reconstruction. Per
   the template's own rule (`conceptual-documentation-guide.md`):
   **alignment is not verification** — an `aligned` finding on a
   rule/invariant means the current implementation matches the stated
   rule, not that the rule itself is correct. Never auto-promote a
   Claim's status off an `aligned` finding alone.
9. **Producer metadata on every artifact.** Every file this topic
   produced (assertions, snapshot, reconstruction record, comparison
   report) carries the header from step 1 — independence is checkable by
   reading headers, not by trusting a claim.

**At no point in steps 1–9 does any dispatch read, search for, or
compare against `README.md`, `docs/**`, `dev-docs/architecture.md`,
`dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`,
`ROADMAP.md`'s prose, `knowledge/*.md`, or any other item the hard
invariant excludes.** That comparison is Phase 5's entire job, not a
thing to get a head start on here.

### 4.2a Per-dispatch boundary-compliance check — immediate, not deferred to Phase 6 (new this amendment, §8 Finding C4)

Contamination is discovered **immediately after each isolation-sensitive
dispatch** in this phase (the assertion-research dispatch, step 2 above;
the implementation-reconstructor dispatch, step 7 above) — never first
discovered at Phase 6. Phase 6 later independently *audits that this
check actually happened every time*, which is a different, weaker claim
than Phase 6 performing the first contamination check itself.

For each such dispatch, immediately after it returns:

1. Read its real tool-call transcript — never its self-reported summary,
   the same corrected lesson §3.3 already applies to the preflight probe
   applies to every real dispatch too.
2. Check every file read, every search performed, every command run,
   every network call made, against the permitted-evidence-paths list
   that dispatch was given. Anything outside that list — reading
   `README.md`, searching for a phrase that only exists in an excluded
   doc, `git show`-ing an excluded file's committed content, fetching the
   public GitHub mirror — is contamination, regardless of whether the
   dispatch's own written output *looks* clean.
3. **If contaminated:** record it in `dev-docs/clean-room/
   compliance-log.md` (one row per dispatch: topic, role, dispatch id,
   verdict, the specific transcript line(s) that triggered it);
   **discard the output entirely** — never edited, trimmed, or salvaged,
   since there is no way to know how much of what it wrote was shaped by
   what it saw; **do not use it as evidence or input to any later
   step**; **rerun the task from a fresh context** (a new `Agent`
   dispatch, same bounded scope), restating the boundary more explicitly
   if the transcript suggests why it was missed (e.g. the dispatch ran an
   unscoped `grep -r` across the whole repo — the rerun's prompt says
   explicitly to scope searches to the named evidence paths only).
4. **If compliant:** record that too, in the same log (verdict:
   compliant, with a one-line note of what the transcript actually
   showed) — a clean result needs the same evidence trail as a
   contaminated one, or the log can't demonstrate the check actually ran.

This log is the audit trail Phase 6 reads to confirm the per-dispatch
gate was real throughout, not retrofitted after the fact.

### 4.3 Phase 3 acceptance criteria

- Every topic in §4.1's table has: a frozen, checker-passing snapshot, an
  independent reconstruction record, and a comparison report.
- No comparison report was produced by the same dispatch that wrote the
  snapshot it's comparing against. **Made actually checkable, not just
  asserted:** every file this phase produces (assertion, snapshot,
  reconstruction record, comparison report) carries a header naming its
  producing dispatch (role + a dispatch id/timestamp), so independence
  can be confirmed by reading the headers rather than trusting a claim.
- At least one `conflicting` or `not_implemented` finding is treated as
  an expected, healthy outcome if found (it means the check is real) —
  not papered over.
- **No existing-documentation comparison or coverage count appears
  anywhere in this phase's output.** (Moved to Phase 5, §6.4 — this
  replaces the original plan's Phase 3 `api-spec.md` coverage-check
  bullet, which was itself the leakage this amendment corrects; see §8
  item 1.)
- Every assertion whose evidence traces through a compat-register entry
  also names the entry's own underlying differential evidence, or is
  explicitly `uncertain` pending a targeted re-check (§3.2, §4.1).
- **Every topic's assertion-research and implementation-reconstructor
  dispatches each have a `compliance-log.md` entry** (§4.2a), logged
  immediately after that dispatch, not reconstructed afterward from
  memory. Any `contaminated` entry has a corresponding discarded-and-
  rerun pair (the contaminated dispatch id, and the fresh dispatch id
  that replaced it) — a contamination event is an expected, honestly
  logged outcome if it occurs, not something to quietly avoid mentioning.
- No topic's assertions were authored by the main orchestrating session
  directly — every topic's `compliance-log.md` entries name a dispatch
  id distinct from the orchestrator's own session.

### 4.4 Files/components touched

- `dev-docs/clean-room/assertions/**`, `snapshots/**`,
  `implementation-comparison/**` (new content, per topic).
- `dev-docs/clean-room/compliance-log.md` (new; one running log for the
  whole initiative, appended to again in Phase 4).
- `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-3.md`.
- No `ledgerkit/`/`tests/` code touched.

---

## 5. Phase 4 — Draft replacement documentation

**Goal:** Objective 4 — a coherent documentation set generated from the
frozen, checker-validated snapshots, never from old prose, with its
drafted set matching exactly what Phase 5 will later replace.

### 5.1 Complete documentation inventory & disposition (new this amendment)

**Resolved (§8 Finding F2):** every current human-facing document gets an
explicit, pre-assigned disposition now, so Phase 5 never has to invent
one ad hoc. Four dispositions, matching the task's own four-way
reconciliation scheme plus the template's five-way claim classification
used *within* reconciliation (§6.1):

- **Clean-room redraft** — Phase 4 produces a fresh draft from snapshots
  alone, with zero input from the existing document; Phase 5 then
  reconciles the existing document's claims against that draft (and its
  snapshots).
- **Reconciliation-only** — Phase 4 does **not** produce a parallel blind
  draft of this document; Phase 5 reconciles its existing content
  directly against the relevant snapshots/evidence, claim by claim,
  preserving structure that's independently supported and correcting
  what isn't.
- **Intentionally retained, out of this initiative's scope** — not a
  claim-classification or reconciliation target in either phase; a
  one-line rationale is still recorded so nobody rediscovers it mid-phase
  and treats it as new scope. **This does not mean these files are never
  touched** — see §5.1a: this initiative's own ordinary workflow
  bookkeeping (a `CHANGELOG.md` entry, a `CONTEXT.md` overwrite, a new
  retro) continues exactly as normal throughout every phase, without that
  bookkeeping changing this disposition or pulling these files'
  substantive historic content into the clean-room document set.
- **Retired/replaced** — folded into another document or removed; only
  used if Phase 5 reconciliation actually finds a document has no
  remaining reason to exist standalone (none is pre-assigned this
  disposition now; it's listed for completeness in case Phase 5 finds a
  case).

| Document | Disposition | Rationale |
|---|---|---|
| `README.md` | Clean-room redraft | project overview — fully derivable from source/tests/CLI behaviour |
| `docs/getting-started.md` | Clean-room redraft | install/quickstart — derivable from `pyproject.toml`, CLI `--help`, actual first-run behaviour |
| `docs/usage.md` | Clean-room redraft | CLI usage — derivable from `cli.py`/`--help`/`tests/test_cli/` |
| `docs/journal-format.md` | Clean-room redraft | journal-format description — derivable from `parser.py`/`models.py`/fixtures, plus the pinned hledger reference where Ledgerkit intentionally matches or diverges (via compat-register's *underlying* evidence, per §3.2, not its YAML alone) |
| `docs/python-api.md` | Clean-room redraft | public API surface — derivable from real `ledgerkit/*.py` signatures/docstrings and test usage; explicitly **not** derived from reading `dev-docs/api-spec.md`, which is itself excluded narrative until Phase 5 |
| `dev-docs/architecture.md` | Clean-room redraft | module responsibilities/data flow — derivable from source organisation, imports, tests |
| `dev-docs/api-spec.md` | **Reconciliation-only** | protected "public API contract" file under the Unauthorised Change Rule — not blindly regenerated; Phase 5 reconciles its existing claims against the independently-derived `docs/python-api.md` draft and real source signatures, any change going through the Rule's confirm-first step regardless |
| `dev-docs/hledger-compatibility.md` | **Reconciliation-only** (§8 item 5) | preserve its existing, already evidence-dense structure where independently supported; re-verify material claims through the compat-register's underlying differential evidence or a targeted re-check against the pinned hledger reference, rather than a full blind redraft |
| `ROADMAP.md` | **Reconciliation-only** | roadmap/backlog content is project *intent*, not reconstructable from the current tree (§8 Finding F3, Objective 3's roadmap-exclusion rule); Phase 4's "current shipped state" topic (§4.1's last row) supplies the *factual* current-state input Phase 5 reconciles against, but no draft of `ROADMAP.md` itself is produced blind |
| `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/**`, `dev-docs/planning/**`, `knowledge/*.md`, `dev-docs/compat-register/**`, `dev-docs/SYNC.md`, `dev-docs/versioning.md`, `dev-docs/editor-readiness-decisions.md`, `dev-docs/changelog/**` | **Intentionally retained, out of this initiative's scope** | process/session-memory/decision-record artifacts with their own existing maintenance machinery (CLAUDE.md's Documentation Sync Rules, retro lifecycle, compat-register lifecycle) — this initiative reconstructs human-facing *project* documentation, not its own process scaffolding |

**Phase 5 must not overwrite any document whose disposition is not in
this table.** If Phase 5 discovers another human-facing document this
table missed, it is added here (with a disposition and rationale)
*before* that document is touched, not decided in the moment.

### 5.1a Disposition vs. ordinary workflow bookkeeping — not the same thing (new this amendment, §8 Finding C5)

**The contradiction this fixes:** §6.6's and §7.1's original wording said
Phase 5 classifies "every old-doc claim... across every document in
§5.1's inventory" and that "every document in §5.1's inventory has... a
reconciliation report" — but §5.1's inventory's fourth row
(`CHANGELOG.md`, `CONTEXT.md`, retros, planning documents, `knowledge/
*.md`, compat-register process material) is explicitly dispositioned
**intentionally retained, out of scope**. Read literally, the acceptance
criteria contradicted the disposition table one row down. Fixed here,
not by changing the disposition (it's correct), but by scoping the two
acceptance-criteria statements precisely (§6.6, §7.1 item 5, both
corrected below).

**The distinction, stated once, applied everywhere:**

- Every phase of this initiative, including this one, still updates
  `CHANGELOG.md`, `CONTEXT.md`, and writes a retro under `dev-docs/
  retros/` — that is **ordinary project workflow**, required by
  `CLAUDE.md` for *any* phase of *any* initiative, not something §5.1's
  inventory grants or withholds. Those routine updates **never** change a
  file's disposition from `intentionally retained` to something else,
  and never pull a retired entry's substantive historic content into the
  clean-room document set.
- §6.1's five-way classification scheme and §6.6/§7.1's
  reconciliation-report requirement apply **only** to documents §5.1
  disposes as `clean-room redraft` or `reconciliation-only`
  (`README.md`, `docs/getting-started.md`, `docs/usage.md`,
  `docs/journal-format.md`, `docs/python-api.md`,
  `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md`) — **never** to a
  document dispositioned `intentionally retained`, regardless of how many
  times this initiative's own routine bookkeeping touches it.
- Concretely: this initiative's own Phase 1–6 retros and `CHANGELOG.md`
  entries get written exactly as every other phase in this project's
  history has — but nobody classifies a past `CHANGELOG.md` entry's
  claims `supported`/`stale_or_contradicted`/etc., and no retro gets a
  `legacy-reconciliation/` report of its own.

### 5.2 What gets drafted this phase

Per §5.1's "Clean-room redraft" row: `README.md`, `docs/getting-started.md`,
`docs/usage.md`, `docs/journal-format.md`, `docs/python-api.md`, and
`dev-docs/architecture.md` — six documents — plus one additional
artifact that is not itself a live document: a **current shipped-state
draft** (facts only, per §4.1's last topic row), which exists purely to
feed Phase 5's reconciliation of `ROADMAP.md`, `dev-docs/api-spec.md`,
and `dev-docs/hledger-compatibility.md`. It is never itself published as
a standalone document.

Drafted as **new files** first (never edited in place over the old ones,
so the old versions remain available for Phase 5 comparison):

- `README.md.clean-room-draft` (or a scratch location — decide at
  implementation time; must **not** overwrite `README.md` before Phase
  5 — corrected from the original plan's "before Phase 6", which named
  the wrong phase; see §8 Finding F8).
- `dev-docs/architecture.md`-equivalent draft.
- `docs/getting-started.md`-equivalent and `docs/usage.md`-equivalent
  drafts (or merged — let the snapshot's own shape decide the structure,
  per `conceptual-documentation-guide.md`'s "pick an architecture from
  the material, not a template").
- `docs/journal-format.md`-equivalent draft.
- `docs/python-api.md`-equivalent draft.
- The current-shipped-state factual draft described above.

### 5.3 Precondition: snapshot checker must have passed

**No drafting dispatch may consume a snapshot that has not passed
`check_snapshot.py` (§3.7).** This is re-confirmed at the start of Phase
4, not just assumed from Phase 3 having run it once — if any snapshot was
re-frozen or edited after its last passing check, re-run the checker
before dispatching.

### 5.4 Drafting discipline

- **Per-dispatch boundary-compliance check, immediately, same discipline
  as §4.2a (new this amendment, §8 Finding C4).** Each of the six
  drafting dispatches (one per clean-room-redraft document) and the
  current-shipped-state dispatch is its own fresh `Agent` call — never a
  `fork` — given only its target document's name, the snapshot(s) it may
  cite, and drafting instructions; never the old document, never this
  governing plan's prose. Immediately after each dispatch returns, its
  transcript is inspected exactly as §4.2a describes; a contaminated
  draft is discarded (never edited) and the dispatch rerun fresh. Logged
  to the same `dev-docs/clean-room/compliance-log.md` Phase 3 started —
  one running audit trail for the whole initiative, not a separate file
  per phase.
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
- **No forward-looking content.** None of these six drafts, nor the
  current-shipped-state artifact, may state what Ledgerkit *will* do,
  plans to do, or has deferred — only what it demonstrably does now.
  Roadmap/intent language is Phase 5's to reintroduce, deliberately and
  separately labelled (§6.1).

### 5.5 Phase 4 acceptance criteria

- Six draft documents plus the current-shipped-state artifact exist,
  each traceable sentence-by-sentence to a Phase 3 snapshot.
- Zero reads of `README.md`/`docs/**`/`dev-docs/architecture.md`/
  `dev-docs/api-spec.md`/`dev-docs/hledger-compatibility.md`/
  `ROADMAP.md`/`knowledge/*.md` by any drafting dispatch (checked via its
  tool-call transcript, same discipline as §3.3).
- No draft contains forward-looking/roadmap language (spot-checked).
- Every snapshot a drafting dispatch consumed had already passed §3.7's
  checker, confirmed at dispatch time, not assumed from Phase 3.
- Drafts committed as their own files before Phase 5 touches any old
  documentation at all (enforces "draft before reconciling"; corrected
  from the original plan's "before Phase 6" — see §8 Finding F8). **That
  commit is the hard boundary between reconstruction/drafting and legacy
  reconciliation.**
- Every drafting dispatch (the six documents plus the current-state
  artifact) has a `compliance-log.md` entry, logged immediately after
  that dispatch (§5.4); any contamination event has a corresponding
  discarded-and-rerun pair, same discipline as Phase 3.

### 5.6 Files/components touched

- New draft documents (exact paths decided at implementation time, kept
  out of the way of `README.md`/`docs/**` until Phase 5).
- `dev-docs/clean-room/compliance-log.md` (appended to; same file Phase 3
  started).
- `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-4.md`.

---

## 6. Phase 5 — Legacy reconciliation

**Goal:** Objective 5, verbatim — only now is any old documentation
reintroduced, and only for comparison/reconciliation. This is the
**first** phase in this initiative where existing narrative is read at
all, per the hard invariant.

### 6.1 Classification

For every claim the old `README.md`/`docs/**`/`dev-docs/architecture.md`/
`dev-docs/api-spec.md`/`dev-docs/hledger-compatibility.md`/`ROADMAP.md`
made, classify using the template's own five-way scheme (matches the
task's four-way scheme with one useful split):

- `supported` — new evidence backs it; keep, ideally cited to its
  snapshot now.
- `stale_or_contradicted` — new evidence contradicts it, or it describes
  something that no longer exists; drop.
- `rationale_requiring_verification` — claims a *reason why*, not just a
  *what*; the "what" may be `supported` while the "why" needs its own
  check — maps to the task's "genuine ambiguity requiring investigation".
  `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` are
  reintroduced **here**, specifically as rationale/intent evidence for
  resolving this category (§8 item 2) — a "why was it built this way"
  question gets checked against them now, not earlier.
- `useful_example` — not an assertion, but a concrete illustration worth
  deliberately retaining — maps to the task's "historical/contextual
  material worth deliberately retaining".
- `obsolete` — no longer relevant at all; drop.

**For `ROADMAP.md` specifically** (Objective 3's requirement, resolved
this amendment): separate every claim into **current-state fact**
(checked against Phase 4's current-shipped-state artifact and the Phase
3 snapshots — classified same five-way as anything else) and
**forward-looking project intent** (Stage D–I's `[PLANNED]` rows, the
backlog, deferred-work notes) — intent claims are **not** checked against
clean-room evidence at all (there is nothing in the current tree that
could confirm or deny a future plan), and are reintroduced deliberately,
verbatim unless the user has separately changed them, clearly labelled as
intent rather than observed fact in the reconciled document.

Report: `dev-docs/clean-room/legacy-reconciliation/<topic>.md`, one per
Phase 4 document (or per Phase 3 topic — whichever keeps each report
readable), **plus** one for each "reconciliation-only" document from
§5.1's inventory that never got a parallel Phase 4 draft
(`dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`,
`ROADMAP.md`).

### 6.2 The rule that matters more than the classification scheme

Per the template: **a `docs-maintainer`-equivalent fix happens as part of
this step, not just a log entry.** Any `supported` claim missing from the
relevant Phase 4 draft (or, for a reconciliation-only document, from the
snapshot evidence) gets added, cited to its snapshot. Any
`rationale_requiring_verification` item either gets a quick targeted
check (reading the actual code/test it concerns, or consulting
`knowledge/*.md` per §6.1) resolved into `supported` or
`stale_or_contradicted`, or stays open and is said so explicitly in the
published doc rather than silently dropped. **No old statement is copied
into the new documentation without either independent support (a
snapshot citation) or an explicit historical/intent label** — this is
Objective 5's hard requirement, repeated here because it's the one most
likely to get quietly violated under time pressure.

### 6.3 Reconciliation-only documents get their own direct pass

For `dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`, and
`ROADMAP.md` (§5.1's "reconciliation-only" row): there is no parallel
blind Phase 4 draft to compare against, by design. Instead, reconcile
each existing document's claims directly against:
- the relevant Phase 3 snapshots and their underlying evidence,
- (for `dev-docs/hledger-compatibility.md` and any hledger-compatibility
  claim elsewhere) the compat-register's own underlying differential
  evidence, or a fresh targeted `compat-differential-tester` re-check
  against the pinned hledger reference where that underlying evidence
  can't be located (§3.2, §4.2) — the register's `kind`/`status` field is
  never treated as sufficient on its own,
- and, for `dev-docs/api-spec.md` specifically, the Phase 4
  `docs/python-api.md` clean-room draft as a cross-check (both should
  describe the same real symbols; a divergence between them is itself a
  finding, resolved by checking the actual source, not by preferring
  either document).

`dev-docs/hledger-compatibility.md`'s **existing structure is preserved
where independently supported** (§8 item 5) — this is explicitly not a
from-scratch redraft; most of its existing organisation is expected to
survive, re-verified rather than replaced.

### 6.4 Existing-documentation coverage check (moved here from Phase 3)

The coverage check the original plan placed in Phase 3 — "every public
symbol currently listed in `dev-docs/api-spec.md` has at least one
corresponding assertion" — belongs here, not in Phase 3, because it is
itself a comparison against an existing-documentation inventory (§8
Finding F1). Run it now: for every symbol `dev-docs/api-spec.md` currently lists,
confirm a corresponding assertion exists somewhere in the Phase 3
snapshots; log any gap as a `stale_or_contradicted`/`rationale_requiring_
verification` finding per §6.1, not silently.

### 6.5 Replace the live documents

Only now, and only for documents §5.1 classifies as `clean-room redraft`
or `reconciliation-only`: `README.md`, `docs/getting-started.md`,
`docs/usage.md`, `docs/journal-format.md`, `docs/python-api.md`,
`dev-docs/architecture.md`, `dev-docs/api-spec.md` (subject to the
Unauthorised Change Rule — flag exactly what changes there, per
`CLAUDE.md`, before touching it), `dev-docs/hledger-compatibility.md`,
and `ROADMAP.md` are actually overwritten with the reconciled content.
**No document outside §5.1's inventory is touched.** The
pre-reconciliation drafts and the old documents both remain recoverable
via git history — nothing is deleted from version control, only from the
live tree.

### 6.6 Phase 5 acceptance criteria

- Every old-doc claim, across every document §5.1 disposes as
  `clean-room redraft` or `reconciliation-only` (never a document
  dispositioned `intentionally retained` — §5.1a), classified; none
  silently dropped without a recorded reason.
- `ROADMAP.md`'s current-state claims and forward-looking intent claims
  are classified and treated separately, per §6.1.
- Every live documentation file post-reconciliation traces its
  substantive factual claims to a Phase 3 snapshot, a targeted
  compat-differential re-check, or an explicit historical-material/
  project-intent label.
- The §6.4 coverage check has run and is reported with a real number.
- `dev-docs/api-spec.md` changes (if any) go through the Unauthorised
  Change Rule's "state exactly what would change, ask first" step before
  being applied, same as any other protected-file edit.
- No document is overwritten whose disposition wasn't already recorded
  in §5.1's inventory.

### 6.7 Files/components touched

- `README.md`, `docs/getting-started.md`, `docs/usage.md`,
  `docs/journal-format.md`, `docs/python-api.md`,
  `dev-docs/architecture.md`, `dev-docs/api-spec.md`,
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md` (reconciled,
  live-replaced per §5.1's dispositions).
- `dev-docs/clean-room/legacy-reconciliation/**` (new).
- `CHANGELOG.md`, `CONTEXT.md`, `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-5.md`.

---

## 7. Phase 6 — Final validation

**Goal:** Objective 6, as an explicit, separately-reported audit — not
folded into a single "done".

### 7.1 Checks, each reported as its own line item

1. **CodeCompass actually upgraded/reconciled, and the pin was actually
   enforced**: `codecompass check` clean; `query source-symbol` reflects
   current source; all four existing agent briefs diffed-and-merged (not
   blind-copied); the two new roles present and adapted;
   `PINNED-REVISIONS.md` names the exact SHAs actually used throughout;
   **independently re-confirmed that the pin-enforcement mechanism from
   §2.0 was genuinely exercised** (the dedicated worktree's own `HEAD`
   still matches the pin, or `check_codecompass_pin.sh`'s logged results
   show it ran and passed before every `codecompass` invocation this
   initiative made) — not merely that `PINNED-REVISIONS.md` contains
   correct-looking text.
2. **Clean-room workflow executed correctly**: the template's stages
   (isolated assertion research → domain-skeptic review → snapshot →
   checker → independent reconstruction → comparison → draft →
   reconciliation) actually ran, in order, for every topic in §4.1's
   table and every document in §5.1's inventory — a process-fidelity
   check, independent of how strong the isolation mechanism itself
   turned out to be. Confirmed in part by `compliance-log.md` showing a
   per-dispatch entry for every isolation-sensitive dispatch in Phases 3
   and 4, with no gaps.
3. **Actual isolation tier achieved**: the §3.3 preflight-probe
   transcript's honest tier label (§3.4) is reported as its own line —
   expected `best-effort` or `filesystem-only, network-exposed`, **never**
   `verified` unless the preflight genuinely demonstrated it, and
   **never described as "isolation enforced"** regardless of which tier
   it is (§8 Finding F5 — this corrects the original plan's §7.1 item 2,
   which conflated the tier with "enforced").
4. **Dispatch transcripts show compliance with the declared exclusion
   boundary**: this is now an **audit of a process that already ran
   per-dispatch** (§4.2a, §5.4), not the first place contamination could
   be discovered. Confirm `compliance-log.md`'s completeness (one entry
   per isolation-sensitive dispatch in Phases 3 and 4, no gaps between
   what the phase retros say ran and what the log shows), independently
   re-read a sample of the underlying raw transcripts directly (not
   their self-reported summaries) to confirm the log's own verdicts were
   accurate, and confirm every `contaminated` entry has a corresponding
   discarded-and-rerun pair with no contaminated output surviving into
   any later artifact. A `best-effort` tier with a complete, accurate
   compliance log is an honest, reportable success on this axis; it is
   still not "verified isolation".
5. **Substantial cross-section, not a trivial sample**: every topic in
   §4.1's table has a snapshot + comparison; every document in §5.1's
   inventory has a disposition recorded; every document dispositioned
   `clean-room redraft` or `reconciliation-only` additionally has a
   reconciliation report (an `intentionally retained` document has only
   its one-line rationale, by design, per §5.1a — not a missing report);
   the §6.4 coverage count is reported as a number, not asserted
   qualitatively.
6. **Provenance exists**: spot-check (independent — not the drafting
   dispatch) a sample of sentences in each Phase 4/5 document, confirming
   each traces to a real snapshot citation or an explicitly labelled
   historical/intent statement.
7. **Internal consistency**: a fresh read-only pass (`docs-reconstructor`-
   style) checks the final document set against each other and against
   actual CLI/test behaviour — same discipline as the existing per-phase
   drift audit, run once across the whole new set.
8. **Tests green**: `python -m unittest discover -s tests -t . -v` — this
   phase never touches `ledgerkit/`, so this is a regression guard that
   should trivially pass; still run and reported, per CLAUDE.md's Testing
   Rules and Commit & Push Cadence.

### 7.2 Dispatch this to `release-phase-auditor`

Same as every other phase in this project — an independent, read-only
Definition-of-Done audit, verdict `PASS` / `PASS WITH NON-BLOCKING
OBSERVATIONS` / `FAIL`, run against exactly the eight items in §7.1 plus
this project's ordinary phase checklist (retro exists, docs reconciled,
commit/push done, no unauthorised protected-file edit).

### 7.3 Phase 6 acceptance criteria

- All eight §7.1 items reported as separate, honestly-labelled results —
  **in particular, items 2, 3, and 4 are never collapsed into one
  "clean-room isolation enforced" line.**
- `release-phase-auditor` verdict recorded.
- A substantive closeout retro (`dev-docs/retros/
  CODECOMPASS-UPGRADE-CLEANROOM-DOCS-CLOSEOUT.md`), synthesising all six
  phases, same style as `STAGE-C-CLOSEOUT.md`.
- `ROADMAP.md`'s new "Tooling & Process Initiatives" section (§8 item 1)
  updated **only if** the human confirms this initiative complete (never
  inferred) — per the standing "never mark done unilaterally" rule.

---

## 8. Resolved decisions (was "Open questions" — all five resolved this amendment)

**Three separate lists below, deliberately not sharing one number
sequence**, since the original plan's 5 open questions, the first
review's 8 numbered findings, and the second review's 8 numbered
corrections are different lists that happen to overlap in range: **Part
A** items are referenced elsewhere in this document as "§8 item `N`";
**Part B** findings are referenced as "§8 Finding `FN`"; **Part C**
corrections are referenced as "§8 Finding `CN`" — each matching its own
source list's numbering exactly, so every cross-reference is directly
traceable back to the specific review comment that raised it.

### Part A — the original plan's 5 open questions, now resolved

1. **Where does this sit in `ROADMAP.md`?** **Resolved:** a new "Tooling
   & Process Initiatives" section, parallel to the Stage A–I ladder (§1),
   never a Stage letter.
2. **The evidence/excluded boundary table (§3.2)** — specifically whether
   `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` should
   be excluded from blind reconstruction. **Resolved:** yes, excluded
   during Phase 3/4; reintroduced during Phase 5 specifically as
   rationale/intent evidence for the `rationale_requiring_verification`
   classification (§6.1) — never consumed earlier.
3. **`CLAUDE.md`'s stale folder-structure diagram (§2.4)** — fix in
   passing, or leave it. **Resolved:** fix it during Phase 1, through the
   Unauthorised Change Rule's normal confirm-first step.
4. **Is the six-phase breakdown the right granularity**, or should Phase
   1+2 merge. **Resolved: keep six phases.** Per direct instruction,
   phase-count reduction alone is not a sufficient reason to merge, and
   no compelling *implementation* reason to merge Phase 1 (tool
   reconciliation + revision pinning) and Phase 2 (isolation mechanism +
   snapshot checker) has been found — they gate genuinely different
   things (Phase 1 gates "is the tool and its roster current"; Phase 2
   gates "is there a trustworthy boundary and a validator before real
   evidence work starts") and each already produces its own retro-worthy
   deliverable.
5. **Scope of the drafted document set, specifically
   `dev-docs/hledger-compatibility.md`.** **Resolved:** reconciliation-
   first, not automatic clean-room redraft (§5.1, §6.3) — its existing,
   already evidence-dense structure is preserved where independently
   supported, with material claims re-verified through the compat-
   register's underlying differential evidence or a targeted re-check
   against the pinned hledger reference, rather than rewritten from
   scratch.

### Part B — the 8 review findings this amendment addresses

Numbered to match the review's own list exactly, for direct traceability.

- **F1 — Clean-room leakage.** Phase 3 (the original plan's §4.3) compared
  reconstructed coverage against `dev-docs/api-spec.md` — excluded legacy
  narrative being consulted before the first clean-room drafts existed.
  **Resolved:** that comparison, and every other existing-documentation
  comparison, moved to Phase 5 (§6.4); Phase 3's acceptance criteria now
  explicitly state zero existing-documentation comparison appears in its
  output (§4.3); the hard invariant banner at the top of this document
  states the rule generally, not just for this one case.
- **F2 — Complete documentation inventory.** The original plan's Phase 4
  drafted fewer documents (4) than its Phase 5 proposed replacing (5).
  **Resolved:** §5.1 adds an explicit inventory/disposition table over
  all 9 named documents (plus the rest of `dev-docs/`, classified
  out-of-scope), each marked clean-room redraft / reconciliation-only /
  intentionally retained / retired-replaced; §6.5 states Phase 5 may not
  overwrite anything outside that table.
- **F3 — Current state vs. roadmap intent.** The original plan risked
  inferring future roadmap decisions from source/tests/CLI behaviour.
  **Resolved:** §4.1's last topic row produces *current-shipped-state
  facts only*, never forward-looking content; §5.1 classifies `ROADMAP.md`
  itself as reconciliation-only; §6.1 requires its claims to be split into
  current-state fact (checked against evidence) and forward-looking
  intent (reintroduced deliberately in Phase 5, never evidence-checked,
  since nothing in the current tree could confirm or deny a future plan).
- **F4 — Snapshot integrity checker.** **Resolved:** §3.7 adds
  `check_snapshot.py`, a small, deterministic, stdlib-only script (not an
  import of CodeCompass's own validator — that non-adoption decision is
  unchanged) that fails closed on all five conditions the review named
  (missing/duplicate ids, hash mismatch, missing repository revision,
  dangling assertion references, unresolvable evidence paths); §4.2 and
  §5.3 make passing it a hard precondition before any Phase 4 drafting
  dispatch consumes a snapshot.
- **F5 — Isolation success criterion.** The original plan's §7.1 item 2
  ("Clean-room isolation enforced") rounded a disclosed `best-effort`
  limitation up into language implying success. **Resolved:** §3.4 draws
  the distinction explicitly (tier achieved vs. compliance observed, never
  "enforced"); §7.1 splits the old single item into three separately
  reported items (workflow executed correctly / actual tier achieved /
  transcript compliance), none of which uses the word "enforced" for
  anything short of a genuinely `verified` tier.
- **F6 — Revision pinning.** The original plan treated "current
  CodeCompass" as whatever the local clone's `HEAD` happened to be at
  planning time, with no mechanism to stop that from silently moving
  across a multi-phase exercise. **Resolved:** §2.0 adds explicit
  fetch-and-pin as Phase 1's first step, recorded in
  `PINNED-REVISIONS.md`, binding for the rest of the initiative unless a
  new, explicit, recorded decision changes it.
- **F7 — Compat-register as derived evidence.** The original plan's §3.2
  listed `dev-docs/compat-register/*.yaml` flatly as "Evidence", on par
  with source/tests. **Resolved:** §3.2 reclassifies it as a *derived
  evidence index*, not primary evidence; §4.1/§4.2 require a material
  hledger-compatibility claim to trace through to the entry's own
  underlying differential-test evidence, or trigger a targeted
  `compat-differential-tester` re-check against the pinned hledger
  reference; §6.3 applies the same rule when reconciling
  `dev-docs/hledger-compatibility.md`. The same section also restricts
  `ledgerkit-editor` inspection (§4.1's "Editor-facing surface" row) to
  its source and tests, explicitly excluding its own narrative
  documentation from the blind pass.
- **F8 — Drafting inconsistencies.** The original plan's Phase 4 section
  twice named "Phase 6" as the point before which old documentation must
  not be touched or read (now corrected to name Phase 5 throughout — see
  the amended §5.2/§5.5), and described `codecompass-template`'s
  deliverable as "nine portable... format skeletons" when it is seven
  skeletons plus two guides plus a worked example (corrected in §1.1).
  F1, above, was the same root cause at larger scale: phase references
  and evidence-boundary discipline drifting out of sync with the
  six-phase structure while the original plan was being written. This
  amendment was itself re-checked for the same class of error after
  drafting — see §12.

### Part C — the second review's 8 corrections, applied before implementation

Numbered to match that review's own list exactly.

- **C1 — Structurally isolate assertion creation.** The first amendment's
  §4.2 said "a first pass" writes assertions without specifying *who* —
  leaving room for the main orchestrator (which has read this entire
  plan, and may have seen legacy documentation) to author them directly.
  **Resolved:** §4.2 now specifies a fresh, evidence-only
  assertion-research `Agent` dispatch (never a `fork`) that receives only
  the bounded topic, permitted evidence paths, and the output format —
  never legacy docs, this plan's prose, pre-existing assertions/
  snapshots, reconstruction output, or prior agent summaries. The main
  orchestrator is explicitly barred from authoring assertions itself.
  Producer-metadata headers (already required for independence-checking,
  §4.3) now cover every artifact this generates.
- **C2 — Enforce the pin, not merely record it.** The first amendment's
  §2.0 recorded a SHA but checked nothing against it, while the
  underlying install stays editable against a checkout that can move.
  **Resolved:** §2.0 adds a preferred dedicated-worktree mechanism (the
  installed executable points at a fixed checkout, not at
  `/home/cormac/projects/codecompass`'s own moving `HEAD`), or, if that's
  not taken, a mechanical guard run before every `codecompass`-dependent
  command that stops rather than silently continues on a mismatch. The
  same discipline applies to `codecompass-template`'s clone.
- **C3 — Strengthen snapshot historical-integrity semantics.** The first
  amendment's `check_snapshot.py` (§3.7) resolved cited evidence against
  today's working tree, which a later, unrelated source change could
  silently invalidate or falsely validate. **Resolved:** §3.7 adds two
  checks that resolve everything against the frozen revision's own git
  tree (`git cat-file`/`git show <revision>:<path>`), never today's
  filesystem — confirming the revision itself exists as a real commit,
  that a cited file existed at that revision, and that a cited line/range
  resolves against that revision's own historical content.
- **C4 — Make boundary compliance a per-dispatch gate.** The first
  amendment deferred contamination discovery primarily to Phase 6.
  **Resolved:** §4.2a (Phase 3) and §5.4 (Phase 4) require inspecting
  each isolation-sensitive dispatch's real transcript immediately after
  it returns, discarding and rerunning on contamination, and logging
  every verdict to `dev-docs/clean-room/compliance-log.md`; Phase 6
  (§7.1 items 2 and 4) now independently *audits that log's completeness
  and accuracy*, rather than performing the first contamination check.
- **C5 — Fix inventory/acceptance-criteria scope contradiction.** §6.6
  and §7.1 item 5 said Phase 5 classifies claims and produces
  reconciliation reports for "every document in §5.1's inventory" —
  including the inventory's own `intentionally retained` row, directly
  contradicting that row's disposition. **Resolved:** new §5.1a states
  the distinction explicitly (ordinary workflow bookkeeping is not
  clean-room reconstruction scope); §6.6 and §7.1 item 5 are both
  reworded to apply only to documents dispositioned `clean-room redraft`
  or `reconciliation-only`.
- **C6 — Restrict Git history use before Phase 5.** §3.2's original
  "`git log` for specific files" row didn't distinguish tree/diff content
  from commit-message prose, and commit messages are human-authored
  narrative that can leak prior framing the same way any other legacy doc
  can. **Resolved:** §3.2's row now permits tree/content commands only
  (`git show <rev>:<path>`, `git diff`), excludes commit-message text by
  default, and requires a narrow, explicitly-recorded exception (named in
  the assertion's own `Evidence` field) for any case where commit-message
  prose is genuinely needed.
- **C7 — Correct the template file-count wording.** The first
  amendment's own correction (§8 Finding F8) fixed "seven skeletons, not
  nine" but left the total wrong: seven skeletons + two guides + one
  worked example is ten, not nine, and the workflow directory's own
  `README.md` makes eleven. **Resolved:** §1.1 now states eleven files in
  total, with the full breakdown, and the error in the first amendment's
  own correction is noted rather than quietly replaced.
- **C8 — Re-run plan consistency checks.** **Resolved:** §12 gained a
  second, dated addendum (below) covering this round's own full
  re-read, every phase/cross-reference check, an explicit confirmation
  that every acceptance criterion names a concrete observable, a
  dedicated invariant-leakage sweep of the newly-restructured §4/§5, and
  confirmation that Phase 5 remains the first point existing narrative is
  intentionally reintroduced.

---

## 9. Non-goals

- **Not importing CodeCompass's own Claim/Evidence/snapshot-integrity
  validator tooling** (`scripts/check_knowledge_base.py`'s enum/
  block-list/historical-integrity checks). That machinery is sized for
  CodeCompass's own much larger, long-lived knowledge base; §3.7's small,
  Ledgerkit-specific checker is the right-sized substitute, built fresh
  rather than imported.
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
  label, and never calls that outcome "enforced" (§7.1, §8 Finding F5).
  (CodeCompass's own, separate, explicitly unscheduled backlog item for a
  future mechanically-enforced mechanism —
  `planning/strict-isolation-for-documentation-reconstruction.md` — is
  noted but not something this phase can pull forward.)
- **Not running a `propagation` demonstration** (one of the template's
  seven format skeletons: a disposable-fixture test that a source change
  surfaces as staleness in the frozen snapshot). Valuable for a knowledge
  base that will be maintained indefinitely; lower priority for a first
  adoption pass whose main deliverable is the documentation itself, not
  the long-term staleness-detection mechanism. Can be added in a later
  phase if Ledgerkit's documentation starts drifting again
  post-reconstruction.
- **Not touching `ledgerkit/` or `tests/` source code at all.** Every
  phase here is tooling and documentation; zero behaviour change, zero
  new compat-register entries expected.
- **Not reopening any Stage C decision** or beginning Stage D. This
  phase is explicitly ordered before Stage D starts, not a substitute for
  scoping it.
- **Not treating CodeCompass's `codecompass-template` repo as something
  Ledgerkit depends on or vendors long-term** — it's a one-time, pinned
  adoption source (clone, copy what's needed, done); Ledgerkit does not
  track it as an ongoing upstream the way it tracks `codecompass` itself.
- **Not letting "current version" silently move mid-initiative** (§2.0,
  §8 Finding F6) — both `codecompass` and `codecompass-template` are pinned
  to a recorded SHA at Phase 1's start; a later upgrade requires a new,
  explicit, recorded decision, not an incidental `git pull`.
- **Not treating `dev-docs/compat-register/*.yaml` as self-certifying
  evidence** (§3.2, §4.1, §6.3) — it is a derived index into real
  differential-test evidence, consulted for *where to look*, never cited
  as the proof itself.

---

## 10. Sequencing summary

```
Phase 1 (CodeCompass reconciliation + revision pinning)
   ↓ unblocks: current, pinned agent roster and generated artifacts
Phase 2 (isolation mechanism adopted + preflight-probed; snapshot checker built)
   ↓ unblocks: a trustworthy exclusion boundary and a validator for Phase 3
Phase 3 (per-topic: isolated assertion research [fresh dispatch, immediate
         transcript check] → domain-skeptic review → snapshot → historical-
         integrity checker → independent reconstruction [fresh dispatch,
         immediate transcript check] → comparison; all contamination
         discarded-and-rerun on the spot, logged to compliance-log.md)
   ↓ unblocks: evidence-backed, provenance-carrying, checker-validated material to draft from
   (zero comparison against any existing document anywhere in this phase)
Phase 4 (draft README/getting-started/usage/journal-format/python-api/architecture
         + a factual current-shipped-state artifact, from fresh isolated
         dispatches against snapshots alone; same immediate transcript-
         compliance check per dispatch)
   ↓ unblocks: something to reconcile against
   (this is still before any old documentation is read — that starts in Phase 5)
Phase 5 (FIRST point old documentation is reintroduced: classify every
         claim in every §5.1-inventoried document, reconcile, replace
         the live documents, run the api-spec.md coverage check)
   ↓ unblocks: a final, real documentation set to audit
Phase 6 (independent release-phase-auditor DoD audit against 8 explicit
         criteria, including the corrected 3-way isolation reporting; closeout retro)
```

Each phase gets its own retro (`dev-docs/retros/
CODECOMPASS-UPGRADE-PHASE-<N>.md`), per the existing per-phase cadence,
and its own commit (pushed on success, per CLAUDE.md's Commit & Push
Cadence — nothing here is pushed if its own phase's checks don't pass).
Phase 3 and Phase 4 are the only phases expected to need more than one
dispatch round each (one per topic in §4.1's table, and one per document
in §5.1's "clean-room redraft" row); Phases 1, 2, 5, and 6 are each a
single bounded unit of work.

---

## 11. Validation commands (for use at each phase's own gate)

```
# Phase 1
git -C /home/cormac/projects/codecompass fetch origin
git -C /home/cormac/projects/codecompass rev-parse HEAD   # record in PINNED-REVISIONS.md
git -C /home/cormac/projects/codecompass worktree add <fixed-path> <pinned-sha>  # preferred enforcement
# (clone codecompass-template to a chosen local path, then:)
git fetch origin && git rev-parse HEAD                     # record in PINNED-REVISIONS.md
# pin-enforcement guard (if the worktree approach isn't used), run before every codecompass command:
bash dev-docs/clean-room/check_codecompass_pin.sh
codecompass sync
codecompass index
codecompass check
codecompass query source-symbol
python -m unittest discover -s tests -t . -v

# Phase 2
python dev-docs/clean-room/check_snapshot.py <topic> --fixture   # against a trivial test snapshot only
# preflight probe (illustrative; exact commands depend on the dispatch
# configuration actually used)
curl -sI https://raw.githubusercontent.com/ctosullivan/ledgerkit/main/README.md
grep -r "<distinctive-excluded-phrase>" .   # from inside the probe dispatch

# Phase 3 (per topic, before any snapshot is treated as frozen — checks
# historical integrity against the recorded revision, not today's tree)
git cat-file -e <revision>^{commit}            # confirm the revision itself exists
git cat-file -e <revision>:<cited-path>        # confirm the cited file existed at that revision
git show <revision>:<cited-path>               # resolve a cited line/range against that revision's content
python dev-docs/clean-room/check_snapshot.py <topic>

# Phase 6 (final)
python -m unittest discover -s tests -t . -v
codecompass check
cat dev-docs/clean-room/compliance-log.md      # audited for completeness, not regenerated
# release-phase-auditor dispatch against §7.1's eight items
```

No new test files are anticipated for `tests/` — this phase produces
documentation and process artifacts, not executable behaviour.
`check_snapshot.py` and any disposable preflight-probe fixture live under
`dev-docs/clean-room/` or a scratch location, never `tests/`, matching
the template's own "disposable fixture, deleted after" discipline for
anything that isn't the checker script itself.

---

## 12. Amendment consistency review

Performed directly against this document's own text after drafting the
amendment above, not left as an unverified claim:

- **Phase-reference audit.** Grepped the whole document for every
  `Phase N` mention and for the literal strings "nine" and "before Phase
  6" / "Phase 6 touches" / "Phase 6 comparison". Found and fixed: two
  genuine leftover "before Phase 6" errors in the original Phase 4
  section (now §5.2/§5.5, both corrected to Phase 5 — §8 Finding F8); one
  stray "nine... format skeletons" miscount (§1.1, corrected to seven
  skeletons + two guides + a worked example); one wrong ordinal
  ("eighth stage" for the template's `propagation` skeleton, removed —
  the template's seven skeletons aren't individually numbered in its own
  prose, so no ordinal was substituted).
- **§8 numbering-collision audit.** While fixing the above, found a
  second, more structural defect introduced during drafting: this
  document's own §8 list and the review's 8 numbered findings both run
  1–8, and three cross-references into §8 pointed at the wrong item
  under that collision (e.g. a reference meant for the isolation finding
  resolved to the hledger-compatibility question instead, and a
  reference meant for the documentation-inventory finding resolved to
  the six-phase-granularity question instead). **Fixed by splitting §8
  into Part A (the original 5 open questions, "§8 item `N`") and Part B
  (the review's 8 findings, "§8 Finding `FN`"), then re-checking every
  one of the ~18 cross-references into §8 individually** against which
  list it actually meant, rather than assuming the first fix generalised.
  This defect is itself a small instance of exactly the class of error
  the review's own Finding F8 flagged — phase/section references
  drifting out of sync while a long document is being edited — so it's
  recorded here rather than silently corrected without comment.
- **Acceptance-criteria demonstrability check.** Walked every phase's own
  acceptance-criteria list (§2.5, §3.5, §4.3, §5.5, §6.6, §7.3) and
  confirmed each line names a concrete artifact, command output, file
  diff, or transcript that would actually show it true or false — not a
  statement no one could check. One gap found and fixed: Phase 3's
  "independence is structural" criterion (§4.3) named no actual mechanism
  for checking which dispatch produced which file; fixed by requiring a
  producer header on every Phase 3 output file.
- **Invariant-leakage sweep.** Re-read §4 (Phase 3) and §5 (Phase 4) in
  full against the hard invariant banner, confirming neither section
  still names an excluded document as something a dispatch reads,
  searches, or compares against before Phase 5 — the one remaining
  mention of `dev-docs/api-spec.md` inside §4 is the explicit statement
  that no such comparison happens there any more (§4.3), not an
  instruction to perform one.

No further defects were found in this pass. This section is itself
subject to the same rule as the rest of this document: a future
amendment that finds a new defect here adds to it rather than quietly
rewriting this record.

### Second amendment consistency review (2026-10-02, same day)

Performed after applying all 8 of §8 Part C's corrections, before
proceeding to implementation:

- **Full re-read.** Read the entire document top to bottom after
  applying all 8 corrections (not just the sections touched), checking
  each against the hard invariant banner and against every other phase.
- **Phase-reference audit.** Re-ran the same class of check as the first
  amendment's §12 (grep for `Phase N`, "nine", "before Phase 6"-style
  errors) against the full post-amendment text; no new instance found —
  the restructured §4.2/§4.2a/§5.4 consistently say "Phase 5" for when
  old documentation is first touched, and "Phase 6" only for the final
  audit.
- **Cross-reference audit.** Checked every new `§8 Finding CN` reference
  this amendment introduced against Part C's own list (8 references,
  C1–C8, one per correction) — no collision with Part A's `§8 item N` or
  Part B's `§8 Finding FN`, since Part C uses its own letter and sits in
  its own subsection, the same discipline the first amendment's own
  self-correction (§8 Finding F8, this section's first pass) established.
- **Hard-invariant consistency check, against every Phase 1–6
  instruction.** Re-read Phases 1, 2, 5, and 6 (unchanged by this
  amendment's structural edits) against the invariant to confirm nothing
  in them was accidentally loosened by edits made elsewhere; re-read the
  rewritten Phases 3 and 4 (§4.2, §4.2a, §5.4) line by line to confirm
  the new, more detailed dispatch-scoping instructions never introduce a
  route for legacy content to reach a dispatch (the explicit "must not
  receive" list in §4.2 step 1 was checked against the invariant's own
  "at minimum" list and covers it in full, plus the two items the
  invariant's own text doesn't name individually — pre-existing
  assertions/snapshots and prior agent summaries — which the invariant's
  general "no planning/knowledge narrative" language already covers but
  §4.2 now also states explicitly).
- **Acceptance-criteria demonstrability, re-checked against the new
  content.** Every new or edited acceptance-criteria bullet (§2.5, §4.3,
  §5.5, §6.6, §7.1 items 1/2/4/5) names a concrete artifact or log entry
  (`PINNED-REVISIONS.md`, `check_codecompass_pin.sh`'s logged result,
  `compliance-log.md`'s per-dispatch rows, the historical-integrity
  checker's own pass/fail output) — none introduces a criterion that
  could only be confirmed by trusting a dispatch's self-report.
- **No existing documentation permitted into Phase 3 or Phase 4 through a
  secondary route.** Specifically checked the new §4.2 step 1's
  "permitted evidence paths" instruction and the new §3.2 git-history row
  for a route that could let legacy narrative in indirectly — commit
  messages were exactly this kind of secondary route (a `git log` output
  can quote a commit subject line that itself paraphrases old
  documentation), which is why §8 Finding C6 excludes them by default
  rather than only restricting direct reads of `README.md` et al.
- **Phase 5 remains the first point existing narrative is intentionally
  reintroduced.** Confirmed by the same sweep as the first amendment's
  own closing bullet, re-run against the new §4.2/§4.2a/§5.4 text: no
  dispatch instruction added this amendment names an excluded document as
  something to read, search, or compare against before Phase 5.

No further defects were found in this second pass.

---

## 13. Implementation log

This section is appended to, in place, as each phase actually runs — it
is the running record the top-of-document Status line points to.
Phase-level detail lives in each phase's own retro
(`dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-<N>.md`); this log is a short
index into those, kept here so a fresh session can see initiative-wide
progress without opening six separate retros first.

- **Phase 1 — CodeCompass reconciliation & enforced revision pinning:**
  **Done, 2026-10-02.** Retro: `dev-docs/retros/
  CODECOMPASS-UPGRADE-PHASE-1.md`. CodeCompass pinned at
  `96a1e4d53acf4acc6659dc233b1ca2eafae3d41a`, `codecompass-template` at
  `68bae8ec739aea413bbedac9f19078f6ab995aca`
  (`dev-docs/clean-room/PINNED-REVISIONS.md`); pin mechanically enforced
  via `dev-docs/clean-room/check_codecompass_pin.sh` (tested both pass
  and fail paths), not a dedicated worktree — rationale recorded in the
  pin file itself (the global editable install is shared with
  CodeCompass's own active development). Re-synced; `codecompass check`
  clean; `query source-symbol` confirmed 107 of 322 indexed symbols now
  come from `ledgerkit/query/*`/`tags.py`. Four existing agent briefs
  reconciled (hand-merged, not blind-copied); `implementation-
  reconstructor.md`/`domain-skeptic.md` added, adapted to Plan 29's own
  lighter artifact scheme (CodeCompass's heavier Claim/Evidence
  apparatus not imported, per §9). `CLAUDE.md`'s folder-structure
  diagram corrected; its CodeCompass section and
  `04-codecompass-integration.md` updated. 935 tests still pass (no
  `ledgerkit/`/`tests/` code touched).
- **Phase 2 — Isolation workflow adoption + snapshot checker:** **Done,
  2026-10-02.** Retro: `dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md`.
  `dev-docs/clean-room/` now carries the full adopted template;
  `check_snapshot.py` built with all six fail-closed conditions
  (including both C3 historical-integrity checks) and proven via a
  built-in `--self-test` fixture battery (7/7 cases behaved as
  expected). Isolation preflight run and recorded
  (`dev-docs/clean-room/isolation-preflight.md`): **honest tier —
  `best-effort`** — filesystem, command execution, and network all
  directly demonstrated open; same host/working directory as the main
  session confirmed by direct comparison. One disclosed discrepancy:
  the probe ran as `general-purpose` (the two new named roles weren't
  yet dispatchable at probe time, becoming so moments later), with no
  reachable `Grep` tool — the "search" route wasn't directly tested,
  though `Bash` (already proven open) makes this immaterial to the
  overall tier.
- **Phase 3 — Evidence-backed clean-room reconstruction:** not started.
- **Phase 4 — Clean-room documentation drafting:** not started.
- **Phase 5 — Legacy reconciliation:** not started.
- **Phase 6 — Independent final validation:** not started.

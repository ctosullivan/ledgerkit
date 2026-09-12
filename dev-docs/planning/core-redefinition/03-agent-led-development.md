# 3. Agent-led development plan

## 3.1 What's adopted from CodeCompass, and what isn't

CodeCompass's own agent-led model (`planning/v1-redefinition/agent-led-development.md`,
`decisions/0049`) is the direct precedent this section draws on. Adopted
principles, verbatim in spirit:

- **The lead Claude session orchestrates; nothing here spawns or
  coordinates other agents on its own.** Ledgerkit is a library, not an
  agent framework — it has even less reason than CodeCompass to build
  self-orchestration.
- **Operationalise existing mechanisms, don't duplicate them.** Ledgerkit
  already has `CLAUDE.md`, `ROADMAP.md`, `CONTEXT.md`,
  `knowledge/{DECISIONS,ANTIPATTERNS,DOMAIN_RULES,EDGE_CASES}.md`, tests,
  `CHANGELOG.md`, and a same-response doc-sync rule. Agents work through
  these, not around them.
- **Independent means independent.** An agent that verifies or audits
  something never repairs what it's judging, and never re-derives its
  ground truth from the thing it's checking (the differential tester
  checks against the real `hledger` binary, not against Ledgerkit's own
  compat register; the docs-reconstructor checks against source/tests, not
  against the docs it's auditing).
- **An agent's observation is not authoritative because an agent recorded
  it.** Same learning lifecycle discipline as CodeCompass
  (`11-documentation-lifecycle.md` §3), scaled down to Ledgerkit's size.

**Deliberately not copied:**

- CodeCompass runs an 8-agent roster because its problem space (dependency
  graphs across three package ecosystems, generated Skills, a SQLite
  context graph, doc-relation detection) has that much genuine surface
  area. Ledgerkit's problem space is narrower — one library, one upstream
  reference project, one compatibility question repeated across many
  features. §3.2 below proposes **seven** roles, and folds two of
  CodeCompass's distinctions (its `context-evaluator` vs
  `reference-project-tester` split, and a standalone learning-lifecycle
  owner) into single Ledgerkit roles, because Ledgerkit doesn't yet have
  evidence that the split earns its own agent — this mirrors the task's
  explicit instruction to avoid one agent per trivial activity.
- CodeCompass's `context-health-planner` (forward-looking "is the graph
  healthy for upcoming work") is not adopted as a standing role — folded
  into `context-curator`'s remit at Ledgerkit's current scale. Revisit if
  Ledgerkit's CodeCompass usage grows enough that this becomes its own
  recurring task (an explicit, evidence-gated addition, exactly as
  CodeCompass itself added `context-health-planner` after Gate DA rather
  than starting with it).
- No standing "implementation agent" file. Per CodeCompass's own finding
  ("no agent adds anything a lead + ad-hoc general-purpose subagent
  doesn't already do"), implementation stays the lead's job or an ad-hoc
  delegated subagent per phase — see §3.2's explicit note on this, since
  the task prompt does list "implementation agent" among its example roles
  and this is a deliberate, disclosed deviation, not an oversight.

## 3.2 The roster

Seven specialist roles plus the lead. Each is a `.claude/agents/<name>.md`
definition **to be created at Stage A implementation time** (not created by
this planning session — creating them is itself the first approved
implementation step, gated the same as everything else).

### Lead Claude session
Owns: understanding the requested phase, delegating bounded work,
resolving conflicts between agent findings, the final commit, and the only
default write access to `ledgerkit/` and `tests/`. Implements directly or
delegates ad hoc to a general-purpose subagent per phase — there is no
separate standing "implementer" role (§3.1).

### `hledger-researcher`
- **Question:** what does hledger 1.52.x actually do here, and why —
  according to its manual, its source, and its own test suite?
- **Merges** the prompt's "upstream/source researcher" and
  "compatibility/specification researcher" roles: in Ledgerkit's case
  these are one continuous task (read → understand semantics → propose a
  compatibility contract), and splitting them would mean handing a
  half-finished brief across an agent boundary for no independence
  benefit — neither half needs to be independent *from the other*, only
  the whole thing needs to be independent from implementation (which
  `compat-differential-tester`, not this role, provides).
- **Produces:** a semantics brief (target behaviour, edge cases, the exact
  manual section / source file(s) / test(s) consulted) plus a **proposed**
  compatibility classification (`09-compatibility-system.md`) — proposed
  only; verification is `compat-differential-tester`'s job, never
  self-certified here.
- **Tools:** read/search only, against a pinned local hledger clone
  (`10-source-assisted-development.md` §2) and Ledgerkit's own repo. No
  writes except its own brief file. Never runs the hledger binary itself
  for verification purposes (that would blur the independence boundary
  with the differential tester) — it may run `hledger --help` /
  `hledger <cmd> --help` for documentation purposes only.

### `compat-differential-tester`
- **Question:** does Ledgerkit's actual behaviour match the real `hledger`
  binary, on the pinned baseline version, for this feature?
- **Method:** constructs fixture journals, runs both `hledger` (pinned
  1.52.x binary) and `ledgerkit` against them, diffs output, and finalises
  the compatibility register entry's status
  (`compatible`/`extension`/`intentional_divergence`/`unsupported`/
  `unexplained_mismatch`) — **the only role authorised to move an entry out
  of `proposed` status**, since it's the one role whose evidence is
  independent of both the researcher's reading and the implementer's code.
- **Rule:** never edits `ledgerkit/` source to make a test pass — files a
  mismatch instead.
- **Tools:** read/search + a pinned `hledger` executable + Bash (test
  fixture construction, running both binaries) + write access only to
  `dev-docs/compat-register/**` and its own test-fixture files under
  `tests/fixtures/`.
- **Active:** every phase that touches parsing, queries, reports, or
  accounting semantics — i.e. most phases from Stage C onward.

### `docs-maintainer`
- Incremental doc reconciliation — the agent form of the doc-sync rule
  `CLAUDE.md` already states. Reconciles `dev-docs/{api-spec,architecture,
  hledger-compatibility}.md` and `docs/*` against **verified**
  implementation (post differential-testing, not the plan's stated
  intent).
- **Tools:** read/search + Edit/Write on `dev-docs/api-spec.md`,
  `dev-docs/architecture.md`, `dev-docs/hledger-compatibility.md`, `docs/`,
  `README.md`. Not `CLAUDE.md`, not `knowledge/`, not `ledgerkit/`.
- **Active:** every phase with an observable behaviour change.

### `docs-reconstructor`
- The independent counterweight to `docs-maintainer` self-certifying its
  own edits — same rationale CodeCompass gives for keeping these two
  roles distinct (`agent-led-development.md` §2.7 there).
- **Per-phase drift audit:** given the phase's actual diff, find every
  sentence in `dev-docs/`/`docs/`/`README.md` the change made false.
  Verdict `NO DRIFT` / `DRIFT — n findings`, findings return to
  `docs-maintainer`.
- **Blank-slate reconstruction (milestones only):** see
  `11-documentation-lifecycle.md` §3.
- **Tools:** read-only + Bash (read-only) + Write only to its own report
  file / `dev-docs/planning/blank-slate/**`. Never edits the docs it's
  auditing.

### `context-curator`
- Ledgerkit's CodeCompass-facing role, per `04-codecompass-integration.md`
  and `05-context-curator.md`: retrieves/uses CodeCompass context for a
  task where appropriate, evaluates its quality, and — the extra
  responsibility the task specifically calls out — turns recurring
  friction into an actionable, reviewable CodeCompass improvement report.
  **Never edits CodeCompass itself.**
- **Tools:** read/search + run CodeCompass CLI (read-only query commands)
  against Ledgerkit's own tree + Write to `validation/codecompass/**` only.
- **Active:** any phase where CodeCompass context is plausibly useful
  (per §4's honest-usage rule — most phases will have nothing to log here,
  and that's an expected, not a failing, outcome).

### `roadmap-context-curator`
- **Merges** the prompt's "roadmap/project-state curator" with learning-
  lifecycle ownership (CodeCompass splits these; Ledgerkit's smaller
  learning volume doesn't yet justify a separate `knowledge-curator`
  agent — revisit if `knowledge/` entry volume grows the way CodeCompass's
  did).
- Reconciles `ROADMAP.md`, `CONTEXT.md`, `CHANGELOG.md`, and
  `knowledge/*.md` from evidence (git log, test results, the actual diff)
  — never marks a milestone `[DONE]` because code was written (`CLAUDE.md`
  already states this rule for humans; this agent operationalises it).
  Milestones stay `[DONE]` only on **explicit user confirmation**, exactly
  as `CLAUDE.md` already requires.
- Owns the (new, small) learning queue described in
  `11-documentation-lifecycle.md` §3 — Ledgerkit reuses `knowledge/` as its
  promotion target rather than inventing a parallel `planning/learnings/`
  tree, since `knowledge/{DECISIONS,ANTIPATTERNS,DOMAIN_RULES,EDGE_CASES}.md`
  already *is* Ledgerkit's promoted-knowledge store.
- **Tools:** read/search + Edit/Write on `ROADMAP.md`, `CONTEXT.md`,
  `CHANGELOG.md`, `knowledge/*.md`, `dev-docs/planning/**`. Not
  `ledgerkit/`, not `CLAUDE.md`, not `dev-docs/compat-register/**` (that's
  the differential tester's).
- **Active:** every phase (bookend — establishes state at the start,
  reconciles at the end).

### `release-phase-auditor`
- Final independent Definition-of-Done audit. Verdicts: `PASS` /
  `PASS WITH NON-BLOCKING OBSERVATIONS` / `FAIL` (a `FAIL` blocks
  completion).
- Checks: tests pass; the phase's own exit criteria (Ledgerkit's
  `ROADMAP.md` already writes per-milestone exit criteria — this is not a
  new concept, just an independent check of it); docs reconciled and
  drift-audited; compat register entries exist for any classified
  behaviour; `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` current; no
  unauthorised change to a `CLAUDE.md`-protected file
  (`api-spec.md`/`pyproject.toml`/folder structure) without recorded
  approval.
- **Does not repair** — files the gap back to the lead.
- **Tools:** read/search + run tests + Write only its own audit report.
- **Active:** every non-trivial phase; mandatory at Core 1.0 (§Stage I).

## 3.3 Permissions summary

| Agent | Reads | Writes | Runs | Independent? |
|---|---|---|---|---|
| Lead | everything | `ledgerkit/`, `tests/`, everything (commits) | everything | n/a |
| `hledger-researcher` | pinned hledger clone, Ledgerkit repo | its own brief file | read-only, `--help` only | partial — proposes, never certifies |
| `compat-differential-tester` | everything, + pinned hledger binary | `dev-docs/compat-register/**`, `tests/fixtures/**` | both binaries, differential scripts | **yes** — evidence independent of researcher and implementer |
| `docs-maintainer` | everything | `dev-docs/{api-spec,architecture,hledger-compatibility}.md`, `docs/`, `README.md` | tests (read-only) | no — participant |
| `docs-reconstructor` | phase diff, source, tests, CLI, ADRs | its own report / `dev-docs/planning/blank-slate/**` | tests/CLI (read-only) | **yes** |
| `context-curator` | Ledgerkit repo, CodeCompass output | `validation/codecompass/**` | CodeCompass read-only queries | partial — uses the tool, reports on it |
| `roadmap-context-curator` | everything | `ROADMAP.md`, `CONTEXT.md`, `CHANGELOG.md`, `knowledge/*.md`, `dev-docs/planning/**` | git log/status | no — participant |
| `release-phase-auditor` | everything | its own report only | tests, re-runs exit criteria | **yes** |

No agent writes `CLAUDE.md`, `LICENSE`, or `pyproject.toml`'s dependency/
licence fields — those stay lead-only, gated by `CLAUDE.md`'s existing
Unauthorised Change Rule (extended in `02-licence-migration.md` §2.4).

## 3.4 Fresh-session workflow

1. Inspect the repository (`ROADMAP.md`, `CONTEXT.md`, `git log`).
2. `roadmap-context-curator` establishes current state and confirms the
   next approved phase (a phase with an open `ROADMAP.md` row and any
   relevant Gate in `14-human-decision-gates.md` resolved).
3. `hledger-researcher` produces the semantics brief, if the phase touches
   compatibility-relevant behaviour.
4. Lead implements / delegates implementation.
5. `compat-differential-tester` verifies against the pinned hledger binary
   and finalises compat-register status.
6. `docs-maintainer` reconciles docs; `docs-reconstructor` drift-audits;
   loop until `NO DRIFT`.
7. `context-curator` logs any CodeCompass usage/friction for the phase.
8. `roadmap-context-curator` reconciles `ROADMAP.md`/`CONTEXT.md`/
   `CHANGELOG.md`/`knowledge/*.md`.
9. `release-phase-auditor` gives the independent DoD verdict.
10. A milestone is marked `[DONE]` only on explicit user confirmation
    (unchanged from current `CLAUDE.md` practice).

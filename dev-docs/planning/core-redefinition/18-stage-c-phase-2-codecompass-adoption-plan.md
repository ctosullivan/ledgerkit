# 18. Stage C Phase 2 plan — CodeCompass adoption + query/report/CLI integration

**Status: planning only. No implementation in this document or its
authoring session.** Operationalises `04-codecompass-integration.md`
(what Ledgerkit can honestly use today) and `07-query-regex.md` §7.2 (the
target report/CLI architecture) into one concrete, scoped phase. Written
in response to an explicit planning request; awaits approval before
Stage C's `ROADMAP.md` row moves to reflect this phase starting.

---

## 0. Pinned revisions (record before anything else)

```
Ledgerkit revision:   05218e3  (main, in sync with origin/main, clean)
CodeCompass revision: e40d8d1  (main, clean)
hledger reference:    1.52.4, commit 33fa849e7ae841968bd21c427094c4fb4a4ec38d
                       binary: /home/cormac/.local/bin/hledger
                       (hledger 1.52.4-g33fa849e7-20260910, linux-aarch64)
                       source clone: /home/cormac/projects/hledger (same commit)
```

These are the baseline pins for everything below. If either repository
moves before this phase actually starts, re-pin and note the delta rather
than silently reusing stale revisions.

---

## 1. Current-state reconciliation

### 1.1 Ledgerkit — no discrepancy found between ROADMAP.md and CONTEXT.md

Both agree: Stage C is `[IN PROGRESS]`; Phase 1 (query semantics research
+ standalone `ledgerkit/query/`) is done, committed (`f86dd28`), pushed;
the hledger binary pin (`05218e3`) is recorded; Stage C's next phase is
explicitly unscoped in both files. **No reconciliation action needed on
the Ledgerkit side** — this plan is exactly "scope the next phase," which
both files already flag as the open item.

Test suite: `python -m unittest discover -s tests -t .` → **656 tests,
OK, 24 skipped** (pandas-optional tests) — green baseline confirmed live,
not assumed from a prior response's memory.

### 1.2 Most recently completed phase — what it actually delivered

Stage C Phase 1 (`dev-docs/retros/STAGE-C-PHASE-1.md`,
`17-query-semantics-brief.md`): a **standalone** `ledgerkit/query/`
subpackage — `ast.py` (`Acct`/`Desc`/`DateSpan`/`Depth`/`Status`/`And`/
`Or`/`Not`), `regex.py` (`HledgerRegex`-subset validation), `parser.py`
(query text → AST, replicating hledger's exact same-prefix-OR / negated-
never-joins-OR combination rule), `eval.py` (`matches_transaction`/
`matches_posting`). **Explicitly not done**: any wiring into `reports.py`,
`cli.py`, or `Query`; `tag:`/`cur:`/smart-dates/`PythonRegex` extension.
81 tests, all passing, isolated under `tests/test_query/`.

### 1.3 Query engine — architecture confirmed by direct read this session

- `ledgerkit/query/ast.py`/`parser.py`/`eval.py`/`regex.py` exist exactly
  as Phase 1 left them; `ledgerkit/query/__init__.py` re-exports `parse`,
  the node types, `matches_transaction`/`matches_posting`,
  `QueryParseError`, and the regex-validation functions. **Not** re-
  exported from top-level `ledgerkit/__init__.py`.
- `DateSpan.end` is exclusive; `ledgerkit.models.Query.date_to` is
  inclusive — the two are **not** interchangeable (recorded in
  `knowledge/DOMAIN_RULES.md`). Any integration work must not conflate
  them.

### 1.4 Report and CLI architecture — read directly, not assumed

**`reports.py`** already has a single shared private filter,
`_posting_matches(posting, txn, query)` (a `Query`-based check), used by
**all four** target report functions:

```
accounts(journal, query=None) -> list[str]
balance(journal, query=None, tree=False) -> dict[...] | list[BalanceRow]
register(journal, query=None) -> list[RegisterRow]
stats(journal, query=None) -> JournalStats   # partial: only date/payee honoured today
```

**Correction to the task prompt's implicit worry**: `balance`/`register`/
`accounts` do **not** currently implement filtering three different ways
— they already share one private helper. The actual gap is narrower and
different: (a) `ledgerkit.query`'s AST has no path into that helper at
all yet, and (b) **`cli.py` constructs no `Query` anywhere and has zero
filter flags today** — no `-a`/`--account`, no `--query`, nothing (this
was Milestone 5's superseded scope, never built). `print` and `check`
don't accept a query at all, at any level.

`balance`'s existing `depth` handling **truncates account names for
display** rather than excluding postings (hledger `--depth` behaviour) —
this is report-layer logic sitting *above* the shared filter, not
something the new integration should re-implement or move.

### 1.5 hledger compatibility/evidence infrastructure — current shape

`dev-docs/compat-register/` holds 32 entries (25 from Stage A migration +
7 from Stage C Phase 1's query-term work), **all `status: proposed`** —
none executable-verified yet. Schema, `README.md`, `UNEXPLAINED.md` all
exist and are current (last touched this week, pinned-binary correction).

### 1.6 Pinned hledger executable + differential-testing mechanism

Binary confirmed working (`05218e3`'s own commit). **No differential-
testing script/harness exists yet** — `compat-differential-tester`'s
process today is manual: construct a fixture, run both tools by hand,
diff output, write the register entry. This phase does not build
automation for that; it uses the existing manual process on a small,
representative case set (§7 below).

### 1.7 `validation/codecompass/` — exists, unused

`README.md` + `findings/{TEMPLATE.md,TEMPLATE.yaml}` exist, fully
specified (`05-context-curator.md` §5.2's schema, already matching almost
every field this planning request's own "Suggested evaluation record"
and "Actionable CodeCompass report" sections ask for). **Zero real
findings exist** (`CC-LK-NNN` — none). This phase produces the first one.

### 1.8 Test state

656 tests, all passing, 24 skipped (optional pandas), confirmed live
(§1.1). No `ledgerkit/` code has changed since Stage C Phase 1 landed.

### 1.9 CodeCompass — what actually exists today (the critical inspection)

**This is the finding that most reshapes the plan below, so it's stated
in full.**

CodeCompass (`e40d8d1`) is a real, substantially implemented CLI tool —
**not** a prototype or aspiration:

- **Requires Python ≥3.11** (`pyproject.toml`) — Ledgerkit targets 3.8+.
  **Confirmed incompatible as a shared environment** — separate venvs are
  not a precaution, they are a hard requirement. A local `.venv` (Python
  3.13.5) already exists at `/home/cormac/projects/codecompass/.venv`
  with `codecompass` installed editable.
- **Real CLI**, `codecompass = codecompass.cli:app`, commands: `init`,
  `sync`, `index`, `check`, `query` (subcommands `vendors`, `vendor`,
  `symbol`, `skills`, `relations`), `chat`, `enrich apply`, `undo`. No
  `discovery` CLI verb — `/discovery` is a **generated Claude Code slash
  command** (`.claude/commands/discovery.md`), confirmed from the
  `tests/fixtures/ledgerkit_lifecycle_demo/` fixture, alongside a
  generated `.claude/skills/codecompass/SKILL.md`.
- **Dependencies**: `typer`, `rich`, `anthropic` (optional key), `pipdeptree`.
- **Package/source-grounding model**: discovers npm/PyPI/Cargo manifest
  dependencies, clones upstream source, builds `context-graph.db`
  (SQLite: `vendors`, `symbols`, `uses_edges`, `doc_artifacts`,
  `documents_edges`, `skill_mentions_edges`, `routes_via_edges`,
  `depends_on_edges`, `doc_relations_edges`, `vendor_enrichment`,
  `symbol_enrichment`, `doc_relation_enrichment`).

**CodeCompass has already run six of its own phases (45, 46, 47, 49, 51,
54) evaluating itself *against Ledgerkit* as an external reference
project** — this is real, dated, substantial prior evidence this plan
must build on rather than duplicate:

| Phase | What it did | Result |
|---|---|---|
| 45 | Baseline Q&A against a pinned Ledgerkit commit | 1 FAIL (`query relations dev-docs/hledger-compatibility.md` → false "not found"), 2 PASS WITH GAPS, all LOW advantage |
| 46 | `codecompass` used on a live, real, in-progress Ledgerkit task (the *exact same* hledger query-term semantics research this project did for Stage C Phase 1) | 2nd FAIL, same root cause, LOW (negative) advantage; `CG-003` filed (external hledger.org manual has zero representation) |
| 47 | Consolidated findings, GATE DB ratified | Funded a narrow fix: add `dev-docs/**/*.md` to `spec_docs._DEFAULT_GLOBS`, disambiguate "never scanned" vs "genuinely absent" |
| 49 | Shipped that fix | CodeCompass's first `src/` change driven by external (Ledgerkit) evidence |
| 51 | Re-ran the two original FAILs against Ledgerkit `05218e3` | Both moved FAIL → **PASS WITH GAPS**; advantage stayed **LOW** — structural ceiling: `query relations` is pure vendor/Skill-name-mention detection, and Ledgerkit has 0 tracked vendors, so it can show *whether* a doc is tracked but never *why* it matters. `17-query-semantics-brief.md` (this project's own Stage C Phase 1 artifact) was independently rated "the single most valuable artifact encountered in any Ledgerkit evaluation to date" — and `query relations` surfaces none of its content. |
| 54 (**today**, 2026-09-16) | A heterogeneous-reference-material experiment: ingested real hledger manual/source excerpts about `tag:`/`date:` query semantics into a **scratch copy** of Ledgerkit, tested whether CodeCompass could relate that material to a real Stage C task (`tag:` query — the *same* term family this plan's own §0 says to defer) | Detection: works, zero code change. Relation: **zero edges** — structural (`spec_doc` rows never get a `name`, so `mentions_artifact` can't match them; filed `CG-004`). A working fallback (parsing a compat-register YAML's own `evidence.ref` field) was demonstrated real but lives outside `src/codecompass/`. **A real accuracy defect was found and fixed**: one extracted manual excerpt silently omitted a rule while its own header claimed completeness — CodeCompass's own evaluator caught it and rated the **treatment run FAIL**, baseline **PASS WITH GAPS**. |

**What this means for this plan, stated plainly:**

1. **None of the above is Ledgerkit adopting CodeCompass.** Every one of
   those six phases was run by *CodeCompass's own agents*
   (`reference-project-tester`, `context-evaluator`), against a *pinned
   commit or scratch copy* of Ledgerkit, from *CodeCompass's own repo*.
   `codecompass` has never been run from inside the real, live Ledgerkit
   working tree, by Ledgerkit's own `context-curator` role, producing a
   Ledgerkit-owned finding. **`validation/codecompass/findings/` being
   empty despite six phases of CodeCompass-side activity is exactly the
   gap `05-context-curator.md` §5.3 already named**: CodeCompass has an
   internal loop about itself; Ledgerkit's own external, independent
   half of that loop has never actually run. This phase is that missing
   half — not a repeat of Phase 45/46/51/54.
2. **Do not re-run the same task type.** Phase 46 already tested
   "CodeCompass during real hledger query-semantics *research*." Phase
   54 already tested "CodeCompass relating ingested reference material to
   a `tag:` query task." Running either again from Ledgerkit's side would
   be redundant, not new evidence. This plan's preferred task — wiring
   the *existing* query engine into reports/CLI — is a genuinely
   different task shape (implementation integration, not semantics
   research) that CodeCompass has never been evaluated against from
   Ledgerkit.
3. **Calibrate expectations honestly, from real prior evidence, not
   blind guessing:** `query vendors`/`query vendor`/`query symbol` will
   almost certainly be near-empty for Ledgerkit (0 mandatory runtime
   deps, confirmed structurally, not just by convention) — this is
   already proven, not a fresh hypothesis. `query relations` on any
   Ledgerkit doc will very likely return "tracked, no relations" (post-
   Phase-49 fix) rather than "not found" — also already proven. The
   **actually open, untested-from-Ledgerkit's-side question** is: what
   does `query skills`, the generated root `CLAUDE.md` routing table, and
   `/discovery` look like when pointed at the *real* Ledgerkit repo for
   the *first time*, and does any of it materially help (or actively
   mislead) an agent doing the query/report/CLI integration task
   specifically? That is this phase's genuine, unanswered question.
4. **`CG-004`** (spec-doc rows can't be mechanically related to each
   other) is filed but unfixed. Expect `query relations` between, say,
   `dev-docs/hledger-compatibility.md` and
   `dev-docs/planning/core-redefinition/07-query-regex.md` to return
   nothing useful, for a known structural reason — record this
   expectation being confirmed or defied, don't treat either outcome as
   surprising in itself.
5. **Do not propose fixing `CG-004`/`CG-005` from Ledgerkit.** They are
   CodeCompass's own filed, triaged findings, already scoped to
   CodeCompass's own future gates (Stage C/GATE-DB-scale and Stage
   E/GATE-DD-scale respectively). Ledgerkit's `context-curator` may
   *corroborate* them if the same shape recurs on the real repo — that's
   valuable, independent, cross-project confirmation — but must not
   re-propose them as if new, and must not attempt to fix them.

### 1.10 No reconciliation conflicts requiring resolution

Both repositories' own status files (`ledgerkit/ROADMAP.md`+`CONTEXT.md`;
`codecompass/planning/ROADMAP.md`+`CONTEXT.md`) are internally consistent
and mutually consistent with each other. The one thing worth flagging
explicitly rather than silently absorbing: CodeCompass's Phase 55 (GATE
DD — "is a generalised technical-dependency/provenance concept necessary
for v1") is **not started** and sits *before* this plan's own work in
CodeCompass's sequence. This plan does not depend on GATE DD resolving
first — it uses CodeCompass exactly as it stands today, which is the
entire point — but the resulting Ledgerkit findings (§9 below) are
directly relevant input to that still-open gate, and should say so.

---

## 2. Detailed phase plan

Ledgerkit-side name: **Stage C Phase 2 — CodeCompass-assisted query/
report/CLI integration**. `dev-docs/retros/STAGE-C-PHASE-2.md` on
completion, matching the existing per-phase retro cadence.

### Phase step 1 — Preflight

- [x] Reconcile current project status (§1, done in this planning pass).
- [x] Record Ledgerkit revision (§0).
- [x] Record CodeCompass revision (§0).
- [x] Confirm hledger reference (§0, already pinned Stage C Phase 1+).
- [ ] Establish CodeCompass dev environment: use CodeCompass's existing
      `/home/cormac/projects/codecompass/.venv` (Python 3.13.5,
      `codecompass` installed editable) to run the `codecompass` CLI with
      **working directory set to the real Ledgerkit repo**
      (`/home/cormac/projects/ledgerkit`). No new venv needs creating
      unless the existing one is found to be broken/stale at execution
      time. **Ledgerkit's own `pyproject.toml`/dev dependencies are not
      touched** — CodeCompass is invoked out-of-tree, by absolute path to
      its own venv's binary, exactly the separation §10 (Development-tool
      separation) requires.
- [ ] Verify normal Ledgerkit baseline remains green immediately before
      starting implementation (re-run the full suite; §1.8 already
      confirms it as of this planning pass, re-confirm at execution
      time since time may have passed).

### Phase step 2 — CodeCompass baseline

Executed *before* any `ledgerkit/` code changes. See §4 for the full
procedure. Summary: run `codecompass` (bare, `--budget 0` to avoid any
AI-enrichment spend/API key requirement) against the real Ledgerkit repo
for the first time; inspect what gets generated (root `CLAUDE.md` routing
table addition, `.claude/skills/codecompass/SKILL.md`,
`.claude/commands/discovery.md`); run `query vendors`, `query skills`,
`query relations` against real Ledgerkit files relevant to the
integration task specifically (`ledgerkit/reports.py`, `ledgerkit/cli.py`,
`ledgerkit/query/*.py`, `dev-docs/hledger-compatibility.md`,
`07-query-regex.md`, `17-query-semantics-brief.md`); capture everything
verbatim. **Do not fix any gap found here** — that's explicitly
prohibited by the task and by CodeCompass's own precedent (§1.9).

### Phase step 3 — Query integration

Per §6's design. Implementation agent uses CodeCompass-first for
discovery/context on this subtask specifically (§5), falls back to direct
source reading freely, implements, adds tests.

### Phase step 4 — Compatibility verification

Full Ledgerkit regression suite must stay green. Representative hledger
differential checks per §7 — resolve any real Ledgerkit defect found;
this is genuine Ledgerkit debugging, not CodeCompass evaluation.

### Phase step 5 — Context evaluation

`context-curator`'s independent pass per §8, using the baseline captured
in step 2 and the real friction/success encountered during step 3.
Distinguishes CodeCompass limitations from Ledgerkit implementation
issues explicitly (a CodeCompass gap and a Ledgerkit bug found in the
same subtask must not be conflated in the writeup).

### Phase step 6 — Feedback and closeout

Produce ≥1 `CC-LK-NNN` finding (§9). Complete phase retro
(`dev-docs/retros/STAGE-C-PHASE-2.md`). Update `ROADMAP.md`/`CONTEXT.md`/
`CHANGELOG.md` (§10). Recommend whether CodeCompass becomes part of the
default Ledgerkit dev workflow — evidence-based, not assumed either way.
Propose next Ledgerkit phase (§13) — do not start it.

---

## 3. Task/subtask breakdown

1. **Environment setup** — confirm CodeCompass's `.venv` runs; confirm it
   can target an arbitrary working directory (Ledgerkit's real repo)
   without modifying Ledgerkit's own `pyproject.toml`/`requirements`.
2. **CodeCompass baseline capture** (step 2, detailed in §4) — no
   Ledgerkit code touched.
3. **Design confirmation** — lead finalises the exact signature/precedence
   decisions §6 leaves open (parameter name, `query`+`query_ast`
   precedence rule) before writing code, recording the choice in
   `knowledge/DECISIONS.md` if it's non-obvious (per existing convention).
4. **`reports.py` change** — add `query_ast` support to `accounts`,
   `balance`, `register`, `stats` via one shared internal check.
5. **`cli.py` change** — add `-q`/`--query` flag; parse once in `main()`;
   thread into the four report calls; handle `QueryParseError` per
   existing error-handling conventions.
6. **Tests** — unit tests for the new `reports.py` parameter (one per
   function × a few representative query shapes); CLI integration tests
   (`tests/test_cli/test_cli.py`) covering the flag end-to-end, malformed-
   query exit behaviour, and no-match behaviour.
7. **Differential spot-checks** (§7) against the pinned `hledger` binary.
8. **Docs** — `dev-docs/api-spec.md` (protected — ask first, per §10),
   `dev-docs/hledger-compatibility.md` if CLI-level query behaviour needs
   a compatibility note, `docs/usage.md` (new `-q` flag is user-facing
   CLI behaviour).
9. **Compat-register** — any newly-verified-vs-hledger behaviour from §7
   gets its own entry or an update to an existing Stage C Phase 1 entry's
   `status`.
10. **Context evaluation + report** (§8, §9).
11. **Retro, roadmap/context/changelog reconciliation, commit/push**
    per the now-standing per-phase process.

---

## 4. CodeCompass baseline procedure

Run from `/home/cormac/projects/ledgerkit` (the real repo, not a copy),
using CodeCompass's own venv binary by absolute path, **before step 3
starts**:

```bash
CC=/home/cormac/projects/codecompass/.venv/bin/codecompass

cd /home/cormac/projects/ledgerkit

# Phase A only — no AI spend, no API key needed, matches this repo's
# "development tooling, not a runtime dependency" requirement.
$CC --budget 0

$CC query vendors --json
$CC query skills --json
$CC query relations dev-docs/hledger-compatibility.md --json
$CC query relations dev-docs/planning/core-redefinition/07-query-regex.md --json
$CC query relations dev-docs/planning/core-redefinition/17-query-semantics-brief.md --json
$CC query relations ledgerkit/reports.py --json     # if reports.py is tracked as an artifact at all — record whether it is
```

Capture, verbatim, for each: the exact command, exit code, full stdout/
stderr. Save under `validation/codecompass/findings/` alongside the
eventual `CC-LK-NNN` (as raw evidence, referenced from the finding's
`evidence:` block — not committed as noise into `ledgerkit/`).

Also inspect, by reading the files directly (not running a command):
whatever gets written to Ledgerkit's own root `CLAUDE.md` (does
`codecompass index` propose inserting a routing table? — **do not apply
it without review**, since `CLAUDE.md` is not one of the three formally
protected files but is Ledgerkit's own governance document and an
uninspected automated edit to it would be exactly the kind of silent
change the project's own conventions exist to prevent), the generated
`.claude/skills/codecompass/SKILL.md`, and `.claude/commands/discovery.md`
— compare their actual content against what the
`ledgerkit_lifecycle_demo` fixture (`codecompass`'s own test fixture)
shows as the generic template, to see what (if anything) is
Ledgerkit-specific versus boilerplate.

**Explicitly deferred to step 5, not step 2:** any judgement about
whether this baseline is *good*. Step 2 only captures; step 5 evaluates.

**Do not run** `codecompass sync`'s Phase B enrichment, `chat`, or
`enrich apply` this phase — no `ANTHROPIC_API_KEY` requirement should be
introduced for a baseline capture, and Phase B is explicitly opt-in/cost-
disclosed, out of scope for "use it as it exists" at zero cost.

---

## 5. Agent-role definitions

Ledgerkit's own `03-agent-led-development.md` already made a deliberate
choice with **no standing "implementation agent" role** — reused here
rather than overridden, since nothing about this phase's evidence
justifies adding a ninth-vs-current-seven persistent role file. Mapped
onto the task's requested four-node structure:

```
Lead Claude
    │
    ├── implementation agent  → ad-hoc (the lead itself, or one
    │                            general-purpose subagent dispatch for
    │                            this task specifically — not a new
    │                            .claude/agents/*.md file)
    │
    ├── compat-differential-tester  → EXISTING role, unchanged remit
    │
    └── context-curator             → EXISTING role, its FIRST real
                                       dispatch in this project's history
```

**Lead Claude** — phase coordination, plan enforcement (this document),
integration of the `reports.py`+`cli.py` changes, resolving any
conflicting findings between the implementation agent's and
`context-curator`'s reports, the completion decision (§12).

**Implementation agent** (ad-hoc, general-purpose) — for the query-
integration subtask specifically: consult the CodeCompass baseline (§4)
first for anything relevant to `reports.py`/`cli.py`/the query engine's
own shape; follow any genuinely useful lead it surfaces; read source
directly wherever CodeCompass is silent, thin, or wrong (expected, per
§1.9's calibrated expectations); implement per §6; record every context
gap encountered, whether or not it becomes a finding.

**`compat-differential-tester`** (existing `.claude/agents/
compat-differential-tester.md`, unchanged) — independently verifies the
integrated behaviour against the pinned hledger binary (§7), stays
structurally independent of the implementation agent's own claims per its
existing hard rules (never edits `ledgerkit/` to make a mismatch
disappear).

**`context-curator`** (existing `.claude/agents/context-curator.md`,
unchanged remit, first real use) — evaluates the CodeCompass context
actually supplied in step 2/3 against `05-context-curator.md`'s existing
`independent_evaluation` schema; captures manual rediscovery; produces
the `CC-LK-NNN` finding(s) (§9). Must reach its verdict **independently**
of whether the implementation agent found CodeCompass helpful — per its
own existing ground rule 2 (incorrect/misleading context outranks missing
context) and rule 3 (a technically-correct-but-cheap result is reported
as low-advantage honestly).

---

## 6. Query/report integration design

### 6.1 Target shape (confirmed against real code, not assumed)

```
CLI  -q/--query "TERMS"
        │
   ledgerkit.query.parser.parse(text)  →  QueryNode  (raises QueryParseError)
        │
   reports.{balance,register,accounts,stats}(journal, query_ast=node)
        │
   ledgerkit.query.eval.{matches_transaction,matches_posting}
        │
   existing per-report aggregation/formatting (UNCHANGED)
```

### 6.2 `reports.py` change

Add one new optional parameter to all four target functions:

```python
def balance(journal, query=None, tree=False, query_ast: QueryNode | None = None): ...
def register(journal, query=None, query_ast: QueryNode | None = None): ...
def accounts(journal, query=None, query_ast: QueryNode | None = None): ...
def stats(journal, query=None, query_ast: QueryNode | None = None): ...
```

One shared internal check (extend `_posting_matches`, or add a thin
`_matches(posting, txn, query, query_ast)` that both existing call sites
route through) — satisfies "shared mechanism, not duplicated across
reports" **structurally**, matching the pattern these four functions
already use for `Query` today (§1.4). Recommended default when both
`query` and `query_ast` are supplied: **AND them** (both must pass) — the
safest, most intuitive behaviour, consistent with `models.py`'s existing
precedent for combining a deprecated parameter with a new one
(`Journal.balance()`'s `accounts=`/`query=` handling). **This is a
decision for the lead to confirm at implementation time, not lock in
here** — record it in `knowledge/DECISIONS.md` if any alternative was
seriously considered.

`stats`'s existing query support is partial (date/payee only, per its own
docstring) — extending it to honour `query_ast` via the same shared check
is in scope; extending its *aggregate output* to reflect richer AST-level
filtering beyond what it already reports is not required beyond making
the filter itself consistent.

`balance`'s depth-truncation-for-display behaviour is untouched — it
operates on the already-filtered posting set, regardless of whether that
set was filtered by `query`, `query_ast`, or both.

### 6.3 `cli.py` change

New flag:

```python
p.add_argument(
    "-q", "--query",
    dest="query_text",
    metavar="TERMS",
    help="Filter using a query string (see ledgerkit.query), e.g. 'acct:food date:2024'",
)
```

In `main()`, immediately after journal load, before the per-command
branch:

```python
query_ast = None
if getattr(args, "query_text", None):
    from ledgerkit.query import parse as _parse_query, QueryParseError as _QueryParseError
    try:
        query_ast = _parse_query(args.query_text)
    except _QueryParseError as exc:
        print(f"ledgerkit: invalid query: {exc}", file=sys.stderr)
        return 1
```

Thread `query_ast=query_ast` into the `balance`/`register`/`accounts`/
`stats` calls in the existing command branches. **`print` and `check` are
explicitly out of scope** — `print` has no query parameter today at any
level (a materially bigger, separate change); `check` filters nothing by
design. Both are named as follow-on candidates (§13), not silently
absorbed into this phase.

Output formatting after each `reports.X()` call is **completely
unchanged** — only the input to the report function changes.

### 6.4 What this design deliberately does not do

- Does **not** touch the existing `Query` dataclass's shape, fields, or
  behaviour — `ledgerkit-editor`'s confirmed dependency on `Query`'s
  4-kwarg constructor (Stage B Phase 1 finding) is unaffected.
- Does **not** make `Query` a compatibility shim over `QueryNode` —
  `07-query-regex.md` §6.5's stated target, but a materially larger,
  separately-scoped change this phase's own instructions explicitly rule
  out ("do not substantially expand... major compatibility-profile
  changes").
- Does **not** add `tag:`, `cur:`, smart dates, or `PythonRegex` — if the
  integration genuinely cannot be completed without one of these, that
  is itself a finding to report and escalate, not a reason to quietly
  add it.

---

## 7. Testing and hledger differential plan

### 7.1 Unit/integration tests (new, all under existing conventions)

- `tests/test_reports.py` (or a focused addition) — for each of
  `balance`/`register`/`accounts`/`stats`: a `query_ast`-only call, a
  `query`-only call (regression — must still work unchanged), and a
  both-supplied call (whatever precedence §6.2 settles on).
- `tests/test_cli/test_cli.py` — `-q` flag end-to-end for each of the
  four commands; malformed query text → exit 1 with a clear stderr
  message; no-match query → empty/zero output, exit 0 (not an error).

### 7.2 Representative hledger differential cases (not exhaustive)

Run via the manual process (§1.6 — no automation built this phase),
`compat-differential-tester` executing both sides:

| Case | Ledgerkit | hledger (bare positional terms — hledger's own CLI query syntax, not a flag) |
|---|---|---|
| Simple account query | `ledgerkit -f F.journal balance -q "acct:food"` | `hledger -f F.journal balance acct:food` |
| Negation | `... -q "not:acct:food"` | `hledger ... balance not:food` |
| Date filter | `... -q "date:2024-01-01..2024-02-01"` | `hledger ... balance date:2024-01-01..2024-02-01` |
| Status filter | `... -q "status:*"` | `hledger ... balance status:*` |
| Multiple conditions | `... -q "acct:food status:*"` | `hledger ... balance acct:food status:*` |
| Report integration | same query across `balance`/`register`/`accounts` | same |
| No-match | `... -q "acct:doesnotexist"` | `hledger ... balance acct:doesnotexist` |
| Malformed query | `... -q "acct:("` (invalid regex) | (no direct hledger equivalent — Ledgerkit-only error-path check) |

**Note the CLI-syntax translation**: hledger takes query terms as bare
trailing positional arguments; Ledgerkit's new `-q` flag takes one quoted
string. `compat-differential-tester` must translate between the two
forms deliberately per case, not assume identical invocation syntax —
this is a CLI-surface difference, not a semantics difference, and should
be noted as such in whatever register entries this produces.

**Claim only what's verified.** If a case isn't run, its compat-register
status stays `proposed`, not `verified` — no case in this table should be
marked `verified` from reasoning alone.

---

## 8. Context-evaluation specification

**Reuses `dev-docs/planning/core-redefinition/05-context-curator.md` §5.2
verbatim** — no new schema. Per relevant subtask (at minimum: the
`reports.py` design lookup, the `cli.py` argparse convention lookup, and
one hledger-semantics cross-check if the differential cases surface a
question):

```
accuracy | relevance | completeness | freshness | grounding | noise   → strong/adequate/weak/n/a
misleading                                                             → true/false
outcome                                                                → PASS / "PASS WITH GAPS" / FAIL
context_advantage                                                      → LOW / MODERATE / HIGH
context_advantage_rationale                                            → could a fresh session get this cheaply, direct?
missing_or_manually_rediscovered                                       → list
```

**Calibration, informed by §1.9's real prior evidence** (not a
prediction made blind): expect `query vendors`/`query symbol` to be LOW/
`n/a` (0 tracked deps, structural). The genuinely open questions this
evaluation should actually answer, that no prior CodeCompass-side phase
has: does `query skills`/the generated `CLAUDE.md` routing table/
`/discovery` offer anything for *this specific implementation task* (not
a semantics-research task, which Phase 46 already covered)? Does
`query relations` on `07-query-regex.md`/`17-query-semantics-brief.md`
(both now real, tracked files post-Phase-49-fix) return anything beyond
"tracked, no relations" when the *querying agent's actual need* is
`reports.py`'s current signature, not hledger semantics? A confirmed-LOW
result here would still be new evidence — the *specific* subtask type is
what's untested, not the general vendor-graph question.

---

## 9. CodeCompass report template

**Reuses `validation/codecompass/findings/{TEMPLATE.yaml,TEMPLATE.md}`
verbatim** (`05-context-curator.md` §5.2) — no redundant infrastructure
created. First real finding(s): `CC-LK-001` (and `CC-LK-002`+ if more than
one materially distinct subtask/verdict warrants separate records, per
the template's own one-finding-per-file granularity).

Each finding's `context_advantage_rationale` and `proposed_generalised_
improvement` must be framed generally (per the template's own instruction
and this planning request's explicit "prefer 'CodeCompass needs a way to
represent executable technical dependencies' over 'add hledger support'"
example) — and must explicitly **cross-reference** `CG-002`/`CG-003`/
`CG-004`/`CG-005` where a finding corroborates one of them, rather than
re-describing the same gap as if newly discovered. A finding that
corroborates an existing CodeCompass-filed gap **from Ledgerkit's own,
independent, first-ever real-usage angle** is itself valuable — record
it as corroboration, not as a new discovery.

`priority_proposed` is exactly that — proposed. Per this project's
existing rule (matching CodeCompass's own), Ledgerkit does not prioritise
CodeCompass's backlog.

---

## 10. Documentation and project-state update list

| What | Doc | Gate |
|---|---|---|
| `reports.py` new `query_ast` param (4 functions) | `dev-docs/api-spec.md` | **Protected — ask before changing**, per `CLAUDE.md`'s Unauthorised Change Rule (same process as Stage C Phase 1's `ledgerkit/query/` addition) |
| `cli.py` new `-q`/`--query` flag | `docs/usage.md` (user-facing CLI change) | Normal doc-sync, same response as the code change |
| Any newly-verified hledger behaviour from §7 | `dev-docs/compat-register/*.yaml` (new or updated entries) | Normal — `compat-differential-tester`'s own write scope |
| CLI-level query behaviour, if materially new re: existing compat notes | `dev-docs/hledger-compatibility.md` | Normal doc-sync |
| Any non-obvious integration decision (e.g. `query`+`query_ast` precedence) | `knowledge/DECISIONS.md` | Normal, same response |
| Architecture change | `dev-docs/architecture.md` | Only if the pipeline diagram's shape actually changes — likely a one-line addition ("query/ feeds reports via query_ast"), not an ADR-level change |
| Roadmap status | `ROADMAP.md` Stage C row | Normal — Phase 2 → `[IN PROGRESS]` at start, updated at completion |
| Session state | `CONTEXT.md` | Overwrite, same response, per existing rule |
| Changelog | `CHANGELOG.md` | New `[Unreleased]` entry, same response |
| CodeCompass validation | `validation/codecompass/findings/CC-LK-001.{yaml,md}` (+more) | New this phase |
| Phase retro | `dev-docs/retros/STAGE-C-PHASE-2.md` | New this phase, per standing Retro Reports rule |

**No ADR-scale architecture change is anticipated** — this is an additive
parameter + a new CLI flag, not a redesign. If implementation reveals
otherwise, stop and re-scope rather than silently expanding.

---

## 11. Risks

- **`api-spec.md` sign-off friction** — mitigated: this is now a familiar,
  fast process (Stage C Phase 1 already went through it once).
- **CodeCompass's `codecompass index`/`sync` proposing an automated edit
  to Ledgerkit's root `CLAUDE.md`** — must be reviewed, not blindly
  applied; `CLAUDE.md` is Ledgerkit's own governance document even though
  it isn't one of the three formally protected files.
- **Conflating a CodeCompass limitation with a Ledgerkit implementation
  bug** — mitigated by `context-curator`'s independent verdict role and
  explicit instruction (§5) to keep the two separate in the writeup.
- **Scope creep into `tag:`/`cur:`/`PythonRegex`/`Query`-as-shim** — this
  document's own §6.4 names these as explicitly out; any implementation
  pressure toward them should stop and re-scope, per the task's own
  instruction, not be absorbed quietly.
- **Over-crediting CodeCompass or over-blaming it** — mitigated by §1.9's
  calibrated, evidence-based expectations set *before* the baseline runs,
  so the evaluation isn't anchored on hope or on the prior FAILs alone
  (both are now known to be fixed for the *specific* cases already
  tested).
- **Runtime/Python-version drift** — CodeCompass's `.venv` is pinned to
  3.13.5 independently of Ledgerkit's 3.8+ target; no action needed
  beyond not cross-contaminating the two environments.
- **`hledger` CLI-syntax mismatch (positional terms vs. `-q` flag)**
  producing an apparent differential mismatch that's actually just a
  translation error, not a real compatibility issue — mitigated by
  §7.2's explicit note.

---

## 12. Definition of Done

Mirrors the task's own 20-point list, mapped onto this plan's concrete
outputs:

1. ✅ (this document) Ledgerkit project state reconciled — §1.
2. ✅ (this document) Exact starting revisions recorded — §0.
3. ⬜ Current CodeCompass used with **zero** CodeCompass-side modifications
   made by Ledgerkit.
4. ⬜ CodeCompass remains dev tooling — no Ledgerkit `pyproject.toml`
   change; separate venv used throughout.
5. ⬜ Current Claude/agent entry points (`CLAUDE.md` routing table,
   `/discovery`, generated Skill) reviewed — §4.
6. ⬜ Baseline discovery/context result captured for the real task,
   before implementation — §4.
7. ⬜ `ledgerkit/query/` integrated into `balance`/`register`/`accounts`/
   `stats` and CLI `-q` — §6.
8. ⬜ Query semantics not duplicated across reports — one shared internal
   check, confirmed by code review at completion.
9. ⬜ Unit + CLI integration tests exist and pass — §7.1.
10. ⬜ Full existing regression suite (656+ tests) stays green.
11. ⬜ Representative hledger differential cases run against the pinned
    binary — §7.2 — with results honestly recorded (proposed vs.
    verified, not asserted beyond what ran).
12. ⬜ CodeCompass context independently evaluated — §8.
13. ⬜ Manual rediscovery recorded — §8/§9.
14. ⬜ Context advantage classified (LOW/MODERATE/HIGH) per subtask — §8.
15. ⬜ ≥1 actionable `CC-LK-NNN` report produced — §9.
16. ⬜ **No CodeCompass product changes made** merely to improve the
    evaluation result — a hard constraint, checked at completion by the
    lead explicitly confirming no `/home/cormac/projects/codecompass`
    file was touched.
17. ⬜ Ledgerkit `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md`/docs reconciled
    — §10.
18. ⬜ Phase retro records whether CodeCompass added meaningful value,
    honestly, including a plausible "it didn't, here's precisely what
    was missing" outcome.
19. ⬜ Evidence-backed recommendations for future CodeCompass work exist
    (the `CC-LK-NNN` finding(s)' `proposed_generalised_improvement`).
20. ⬜ Next Ledgerkit phase proposed, not started — §13.

**This phase is not complete until the user explicitly confirms it**, per
`ROADMAP.md`'s own standing process — the checklist above is the
implementation agent's/lead's own completion gate, not a substitute for
that confirmation.

---

## 13. Likely follow-on phase options (proposed, not started)

To be genuinely selected from *after* this phase's evidence lands, not
pre-decided now:

- **Stage C Phase 3 — extend CLI query coverage to `print`** (currently
  has no query parameter at any level) — a natural, small next step if
  Phase 2's integration pattern proves clean.
- **Stage C Phase 4 — `tag:`/`cur:` term families** — only once genuinely
  scoped; note CodeCompass's own Phase 54 already surfaced a real
  extraction-accuracy risk specifically in `tag:` reference material
  (§1.9), worth reading before this starts regardless of who does it.
- **Stage C Phase N — `Query`-as-compatibility-shim over `QueryNode`**
  (`07-query-regex.md` §6.5's original target) — the larger, deferred
  architectural change this phase deliberately did not attempt.
- **A second CodeCompass-assisted Ledgerkit phase**, deliberately chosen
  to differ in *task shape* from both this phase and CodeCompass's own
  Phase 46/54 (e.g. a debugging task, or a cross-file refactor) — if
  Phase 2's evidence shows CodeCompass has task-shape-dependent value,
  this is how that hypothesis gets tested rather than assumed.
- **A `context-curator` corroboration pass on `CG-004`** the next time a
  genuinely new spec-doc-relation need arises naturally — not scheduled
  as its own phase, since manufacturing the need would violate this
  project's own "real work, not a synthetic benchmark" principle.
- **If Phase 2's verdict is uniformly LOW-advantage with no FAILs**: the
  defensible recommendation may be "CodeCompass is safe, free, and
  occasionally marginally useful, but not yet a required step in
  Ledgerkit's workflow" — a legitimate, evidence-backed outcome, not a
  failure of this plan.

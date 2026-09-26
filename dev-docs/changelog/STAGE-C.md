# Changelog — Stage C: Query system

Archived on: 2026-09-27
GitHub commits: f86dd28..ea08a67 (and subsequent Stage C closeout commits)

---

### [Stage C Phase 1 — Query semantics research + standalone query engine] — 2026-09-13

Full detail: [dev-docs/planning/core-redefinition/17-query-semantics-brief.md](dev-docs/planning/core-redefinition/17-query-semantics-brief.md), [16-model-review.md](dev-docs/planning/core-redefinition/16-model-review.md)

**Human:** directed proceeding with the roadmap autonomously, choosing
recommended options at each decision point, until a natural stopping
point; supplied the `ledgerkit-editor` git URL earlier in this arc, and
approved the `dev-docs/api-spec.md` addition for this phase specifically
when asked.

**Claude:** dispatched `hledger-researcher` for a semantics brief on
Stage C's initial query-term set (`acct:`/`desc:`/`date:`(simple)/
`depth:`/`status:`/`not:`), grounded in the pinned local `hledger` 1.52.4
source clone. Implemented `ledgerkit/query/` (new subpackage): `ast.py`
(AST node types), `regex.py` (`HledgerRegex`-compatible-subset validation,
rejecting constructs like backreferences, `(?...)` forms, GNU `\<`/`\>`,
Perl shorthand classes, POSIX named classes, and lazy quantifiers rather
than silently reinterpreting them), `parser.py` (query text → AST,
replicating hledger's exact `combineQueriesByType` partition-then-combine
rule — critically, a negated term never joins a same-prefix OR group),
and `eval.py` (AST → predicate over `Transaction`/`Posting`, both
transaction- and posting-oriented). 81 new tests (656 total, all
passing). Added `dev-docs/api-spec.md`'s `ledgerkit/query/` section (user
sign-off obtained per the Unauthorised Change Rule) and
`hledger-compatibility.md`'s new Query Language section. Added 7
`status: proposed` compat-register entries. Recorded two new
`knowledge/DOMAIN_RULES.md` entries: `ledgerkit.query`'s `date:` range end
is exclusive (differs from the existing, inclusive `Query.date_to`), and
`not:` never joins a same-prefix OR group. Corrected a stale claim in
`dev-docs/compat-register/README.md` (a hledger source clone does exist
locally; only a pinned binary is still absent). Not yet wired into
`reports.py`/`cli.py`/`Query` — standalone by design this phase. Retro:
`dev-docs/retros/STAGE-C-PHASE-1.md`.

---

### [Stage C Phase 2 — Planning: CodeCompass adoption + query integration] — 2026-09-16

Full detail: [dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md](dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md)

**Human:** directed planning (not implementing) the next Ledgerkit phase:
adopt current CodeCompass, as it exists today, during a real query/
report/CLI integration task, with a detailed 11-point current-state
inspection required first and 13 specific planning outputs.

**Claude:** inspected Ledgerkit's current main (656 tests green),
`CLAUDE.md`, `ROADMAP.md`/`CONTEXT.md` (no discrepancy found), the
Stage C Phase 1 query engine, `reports.py`/`cli.py` (found `reports.py`
already shares one filter helper across all four report functions — the
real gap is a missing `query_ast` path plus zero CLI query flags, not
duplicated filtering logic as the request's own illustrative framing
suggested), the compat-register/pinned-hledger infrastructure, and
`validation/codecompass/`'s existing (unused) findings scaffold.
Separately inspected the actual current CodeCompass repository
(`e40d8d1`) in full and found it has already run six of its own phases
(45, 46, 47, 49, 51, 54) evaluating itself against Ledgerkit as an
external reference project — including a FAIL→fix→PASS-WITH-GAPS cycle
on `query relations` and a same-day (2026-09-16) experiment touching
`tag:`-query-semantics reference material — none of which is Ledgerkit
itself adopting CodeCompass (all were CodeCompass-side, against a pinned
commit or scratch copy). Wrote `18-stage-c-phase-2-codecompass-adoption-
plan.md`: pinned revisions, current-state reconciliation, a phase plan
reusing existing agent roles (`compat-differential-tester`,
`context-curator`) and existing schemas (`05-context-curator.md`'s
evaluation format, `validation/codecompass/`'s templates) rather than
inventing new infrastructure, a concrete `reports.py`/`cli.py`
integration design, a representative hledger differential-test plan, and
an explicit list of what this phase and its follow-ons must not absorb
(`tag:`/`cur:`/`PythonRegex`/`Query`-as-shim). `ROADMAP.md`'s Stage C row
updated to point at the plan; Phase 2 itself not started, awaiting
approval. Retro: `dev-docs/retros/STAGE-C-PHASE-2-PLAN.md`. No
`ledgerkit/`/`tests/` code touched — planning only, as directed.

---

### Amended Stage C Phase 2 plan per review findings — 2026-09-16

Full detail: [dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md](dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md) (amendment note at top)

**Human:** directed four specific amendments to the just-written Stage C
Phase 2 plan, without otherwise redesigning the phase: add an API-
boundary decision gate before any new public `query_ast=` parameter;
replace "one shared internal filtering check" with delegation to the
canonical `matches_posting`/`matches_transaction` evaluators by report
orientation; acknowledge `reports.py`'s current size against the module-
size threshold; and separate CodeCompass-adoption artifacts from feature
implementation into distinct commits.

**Claude:** rewrote §6 (query/report integration design) to present the
API-boundary choice as an explicit three-option gate (new public
parameter / overloaded existing parameter / internal-only, no API change)
resolved *before* any `api-spec.md` change, added as its own phase step
so it can't be silently skipped; rewrote the `reports.py` design to name
`ledgerkit.query.eval.matches_posting`/`matches_transaction` as the only
delegation targets, explicitly ruling out a new `reports.py`-local
wrapper that would re-derive AST semantics a second time; added §1.4a
recording `reports.py` at 573 lines (confirmed live via `wc -l`) against
`CLAUDE.md`'s 300–500-line refactor-signal threshold, with any resulting
refactor pressure routed to follow-on work, never this phase, per the
Module Size & Refactoring rule's existing flag-propose-wait process;
threaded a three-commit-boundary structure (CodeCompass baseline
artifacts; query/report/CLI implementation + its feature docs; context
evaluation + retro + closeout) through the phase steps, task breakdown,
and doc-update table. Updated risks and added Definition-of-Done items
21-24 for the four changes, without renumbering the original 20-item
list. The phase's stated objective is unchanged. Retro:
`dev-docs/retros/STAGE-C-PHASE-2-PLAN-AMENDMENT.md`. No `ledgerkit/`/
`tests/` code touched — planning only.

---

### [Stage C Phase 2, commit 1/3 — CodeCompass baseline] — 2026-09-16

Full detail: [validation/codecompass/findings/CC-LK-001-baseline-evidence.md](validation/codecompass/findings/CC-LK-001-baseline-evidence.md)

**Human:** directed implementing the (amended) Stage C Phase 2 plan.

**Claude:** ran `codecompass` (the real CLI, via its own separate `.venv`
— not added to Ledgerkit's own dependencies) against the live Ledgerkit
repo for the first time ever, per the plan's phase step 2. `query
vendors` empty (predicted — 0 mandatory deps). `query relations` on
three real, load-bearing docs (`hledger-compatibility.md`,
`07-query-regex.md`, `17-query-semantics-brief.md`) returned "tracked,
zero relations" — confirmed CodeCompass's own Phase 49 fix generalises to
the live repo, including a file that postdates the commit that fix was
verified against. `query relations` on a `.py` source file produced a
correctly-disambiguated "not a spec/vendor doc" message, a case type not
previously tested. `codecompass --budget 0` auto-modified Ledgerkit's own
`CLAUDE.md` (an empty routing-table block) without being asked — reviewed
per the plan's explicit instruction, then reverted rather than kept, since
it currently adds zero value. All CodeCompass-generated artifacts
(`vendor.toml`, `context-graph.db`, generated Skill/discovery files)
cleaned from the working tree after capturing evidence — nothing
CodeCompass-generated persists in the Ledgerkit repo, consistent with
"development tooling, never a runtime dependency." No Phase B
AI-enrichment cost incurred (the one `sync` attempt's cost-disclosure
prompt was declined non-interactively, as intended). `ROADMAP.md`'s Stage
C row updated. This is commit boundary 1 of 3 for this phase (§2/§10 of
the plan) — feature implementation and context evaluation/closeout follow
as separate commits.

---

### [Stage C Phase 2, commit 2/3 — query/report/CLI integration] — 2026-09-16

Full detail: [dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md](dev-docs/planning/core-redefinition/18-stage-c-phase-2-codecompass-adoption-plan.md) §6

**Human:** directed implementing the plan.

**Claude:** resolved the API-boundary decision gate (`knowledge/
DECISIONS.md`, 2026-09-16): `reports.py`'s `accounts`/`balance`/
`register`/`stats` gain a **private**, non-public `_query_ast` keyword
parameter — no new public API surface, `dev-docs/api-spec.md` untouched.
Each report delegates to the canonical `ledgerkit.query.eval.
matches_posting` (posting-oriented reports) or `matches_transaction`
(`stats`) directly, per report orientation, rather than a new shared
wrapper. Added `cli.py`'s `-q`/`--query` flag, threading the parsed
`QueryNode` into all four commands. Fixed a real, previously-latent bug in
`ledgerkit/query/parser.py`: a syntactically invalid (but not excluded-
construct) regex now raises `QueryParseError` at parse time instead of a
raw `re.error` surfacing later inside `eval.py`.

**Differential-verified against the pinned hledger 1.52.4 binary**
(representative cases: simple account query, negation, date range,
status, multiple conditions, report integration, no-match, malformed
query) — found and fixed two real, previously-unreachable CLI bugs
(`balance` printed nothing at all for a zero-match query instead of
hledger's separator+`0`; fixing that exposed a `max()` crash on the same
empty-result path — `knowledge/EDGE_CASES.md` EC-016), and **corrected a
Stage C Phase 1 misclassification**: `LK-COMPAT-QUERY-DEPTH-001` claimed
`compatible`/`equivalent` from source-reading alone, but real hledger
`balance`/`register depth:N` truncate-and-aggregate rather than exclude —
reclassified `intentional_divergence`/`incomparable`, `status: verified`
(`knowledge/EDGE_CASES.md` EC-017). Five other Stage C Phase 1 entries
(`ACCT`, `DESC`, `DATE`, `STATUS`, `BOOLCOMBINE`) moved `proposed` →
`verified` with executable evidence. Updated `dev-docs/hledger-
compatibility.md`'s Query Language section, `docs/usage.md` (new `-q`
flag, with the `depth:` caveat), and `dev-docs/architecture.md` (one
paragraph placing `ledgerkit/query/` in the pipeline). Added 23 new tests
(11 `reports.py`, 9 CLI, 3 regex-error regression) — 679 total, all
passing.

**Process note:** differential verification was performed directly by the
lead session this response, not via a separately-dispatched
`compat-differential-tester` agent as the plan's agent-role design
intended — recorded honestly in the retro (commit 3/3), not hidden.

---

### [Stage C Phase 2, commit 3/3 — context evaluation + closeout] — 2026-09-16

Full detail: [validation/codecompass/findings/CC-LK-001.md](validation/codecompass/findings/CC-LK-001.md), [dev-docs/retros/STAGE-C-PHASE-2.md](dev-docs/retros/STAGE-C-PHASE-2.md)

**Human:** directed implementing the plan; no further direction this
commit boundary.

**Claude:** independently evaluated the CodeCompass context captured in
commit 1/3 against `05-context-curator.md`'s existing schema and produced
`validation/codecompass/findings/CC-LK-001.{yaml,md}` — Ledgerkit's first
real CodeCompass context-quality finding. Verdict: PASS WITH GAPS,
context advantage LOW — CodeCompass returned honest emptiness (not a
false "not found"), but contributed nothing to the actual implementation
work, which was done entirely from direct source reading. Corroborates
two already-filed CodeCompass gaps (`CG-003`: no executable/behavioural
technical-dependency concept; `CG-004`: no doc-to-doc relation mechanism)
from a genuinely new angle — a real implementation task on the live repo,
not semantics research on a pinned/scratch copy, which is how every prior
CodeCompass-side evaluation of Ledgerkit ran. Recommendation:
`collect_more_evidence`, priority `medium` — not proposing new
CodeCompass work, just independent confirmation for whoever resolves
GATE DD. Wrote the phase retro (`dev-docs/retros/STAGE-C-PHASE-2.md`),
which records honestly that differential verification (commit 2/3) was
performed directly by the lead rather than via a separately-dispatched
`compat-differential-tester` agent as the plan's own design specified —
a real process gap, not hidden. Recommendation on CodeCompass joining the
default workflow: not yet warranted (six consistent LOW-advantage data
points now, across both usage directions). `ROADMAP.md`'s Stage C row
updated to "Phase 2 done"; Stage C itself remains `[IN PROGRESS]` (not
marked done — more phases remain, and only the user confirms a Stage's
own completion). Confirmed the `/home/cormac/projects/codecompass`
repository was never modified at any point this phase (`git status`/
`git log` unchanged from `e40d8d1` throughout). Next phase proposed
(wiring `-q` into `print`) but not started.

---

### [Stage C Phase 3 — Wire `-q`/`--query` into `print`] — 2026-09-17

Full detail: [dev-docs/retros/STAGE-C-PHASE-3.md](dev-docs/retros/STAGE-C-PHASE-3.md)

**Human:** directed commencing the next phase; Stage C Phase 2's own
retro had already named this as the recommended candidate.

**Claude:** wired `-q`/`--query` into `print` — `cli.py` filters
`journal.transactions` directly via `ledgerkit.query.eval.
matches_transaction` (print has no `reports.py` function of its own to
carry a `_query_ast` parameter). Confirmed against hledger's actual
`print` behaviour before assuming the design: a matching transaction is
shown **whole** (every posting, not just the matching one(s)) — verified
directly (`print depth:1`, `print acct:food`) rather than assumed from
the other four commands' pattern. Differential-tested against the pinned
hledger 1.52.4 binary for `acct:`/`not:`/`status:` — identical output
(formatting differences only). Added `LK-COMPAT-QUERY-PRINT-
INTEGRATION-001` (`status: verified` from the start). Updated
`dev-docs/hledger-compatibility.md`, `docs/usage.md`, and
`dev-docs/architecture.md` for the new integration path. 5 new tests —
684 total, all passing. `dev-docs/api-spec.md` unchanged (no new public
function/parameter). Only `check` remains unwired from `-q`, by design.

---

### [Stage C Phase 4 — Tag data model (parsing/storage)] — 2026-09-17

Full detail: [dev-docs/retros/STAGE-C-PHASE-4.md](dev-docs/retros/STAGE-C-PHASE-4.md)

**Human:** directed proceeding with the recommended next phase (`tag:`
query term); when research revealed no tag data model existed at all,
chose via `AskUserQuestion` to split the phase into data model first,
`tag:` query later; then confirmed the exact proposed model-field
additions before they were made (protected `dev-docs/api-spec.md`).

**Claude:** implemented `name:value` inline-comment tag parsing and
storage, scoped to the data model only — the `tag:` query term itself is
deferred. New `ledgerkit/tags.py` module: `parse_tags` (grammar-accurate
extraction, recorded as an adapted implementation, not directly
translated material) and `effective_date`/`effective_date2` (posting
`date:`/`date2:` override precedence, as pure functions over a
`(Transaction, Posting)` pair — no back-reference field added). New
model fields: `Posting.tags`/`date_override`/`date2_override`,
`Transaction.tags`, `Journal.declared_account_tags`. Also fixed a real
pre-existing gap where `account` directive comments (same-line and
follow-on) were silently discarded — found and fixed a related
unreachable-code bug in the same area. Two `hledger-researcher` briefs
(`core-redefinition/19`, `20`); differential-tested against the pinned
hledger 1.52.4 binary (`hledger tags`, `hledger register`) — exact
matches. 4 new compat-register entries, all `status: verified`. 46 new
tests — 728 total, all passing. Updated `dev-docs/api-spec.md`,
`dev-docs/architecture.md`, `dev-docs/hledger-compatibility.md`,
`docs/journal-format.md`, `knowledge/DOMAIN_RULES.md`,
`knowledge/DECISIONS.md`.

---

### [Stage C Phase 5 — Planning: verification independence + `depth:` semantics] — 2026-09-17

Full detail: [dev-docs/planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md](dev-docs/planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md), [dev-docs/retros/STAGE-C-PHASE-5-PLAN.md](dev-docs/retros/STAGE-C-PHASE-5-PLAN.md)

**Human:** directed planning (not implementing) a phase resolving two
issues found in recent Stage C work — every compat-register entry ever
marked `verified` was self-verified by the implementing session, not
independently checked; and `depth:` is modelled as a pure boolean
exclusion predicate, which may not match hledger's real behaviour.
Required inspecting the current repository, manual, source, and pinned
executable directly rather than relying on prior chat discussion, and
producing nine specific planning outputs with explicit human-decision
gates before any implementation begins.

**Claude:** confirmed both issues via direct inspection. (1) All 11
compat-register entries ever moved past `status: proposed` (Phases 2-4)
were verified by the same session that implemented the feature, not a
dispatched `compat-differential-tester` — a gap Phase 2's own retro had
already named and never enforced. Proposes a claim-strength-tiered
process amendment: ordinary work needs no new process; any first-time
promotion to `verified` (or a change to an already-verified entry's
`kind`) must come from an actual `compat-differential-tester` dispatch;
a new `status: self-verified` value records real-but-non-independent
evidence honestly instead of overclaiming. (2) Traced every hledger
command that consumes a `Query` (`MultiBalanceReport.hs`,
`PostingsReport.hs`, `EntriesReport.hs`, `Accounts.hs`,
`AccountTransactionsReport.hs`) and found every one strips `Depth`/
`DepthAcct` before postings are selected, reapplying it only as
display-name clipping/aggregation (`DepthSpec`) — confirmed live against
the pinned 1.52.4 binary across 14 scenarios (general depth, custom
`REGEX=NUM` depth, multiple-depth-option precedence, `balance`/
`register`/`print`/`accounts`/`stats`). Also found `ledgerkit/reports.py`
already contains a second, correct, pre-existing depth-truncation
mechanism (`Query.depth`) that disagrees with the newer `-q`-path
`Depth` AST node — an internal inconsistency, not just an external
divergence. Definitively resolved Phase 2's open "`print depth:1`"
question (hledger ignores depth entirely for `print`; current Ledgerkit
wrongly excludes everything) and found a third, previously undocumented
defect in `accounts -q "depth:N"` (filters instead of clipping/
deduplicating). Proposes a `DepthSpec` report-option model (not a
`QueryNode`) matching hledger's exact precedence rules. Six explicit
human-decision gates recorded, none resolved. `ROADMAP.md`'s Stage C row
updated to point at the plan; Phase 5 itself not started, awaiting
approval. No `ledgerkit/`/`tests/` code touched — planning only, as
directed.

---

### [Stage C Phase 5, commit 1/N — process amendment: verification independence] — 2026-09-17

Full detail: [dev-docs/planning/core-redefinition/09-compatibility-system.md](dev-docs/planning/core-redefinition/09-compatibility-system.md) §9.6

**Human:** approved the Phase 5 plan's recommended options for all six
gates ("proceed as recommended"), including G-PROCESS-1 (adopt the
tiered verification-independence rule as specified) and G-PROCESS-2
(relabel the 11 existing lead-self-verified entries now rather than
re-dispatching independent review on all of them immediately).

**Claude:** amended `09-compatibility-system.md` with new §9.6
(claim-strength-tiered process: Tier 0 ordinary work needs nothing new;
Tier 2 — first promotion to `verified`, or any change to an already-
`verified`/`final` entry's `kind` — must come from an actual
`compat-differential-tester` Agent dispatch's own output, never written
by the implementing session directly; the retro must name the dispatch
for each; `release-phase-auditor` checks this). Added `status:
self-verified` to `dev-docs/compat-register/schema.md` and cross-
referenced it from `README.md`, and updated both
`compat-differential-tester.md`/`release-phase-auditor.md` agent role
files. Relabelled all 11 existing lead-self-verified entries (Phases
2-4) from `verified` to `self-verified`, each with a note recording the
relabel and pointing at the new process section — evidence and reasoning
in every entry left exactly as written, only the status/framing
corrected. No `ledgerkit/`/`tests/` code touched this commit.

---

### [Stage C Phase 5, commit 2/N — redesign `depth:` as a report-display option] — 2026-09-17

Full detail: [dev-docs/planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md](dev-docs/planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md)

**Human:** approved the plan's recommended options for the four depth
gates ("proceed as recommended"): G-DEPTH-1 (DepthSpec report-option
model, not a QueryNode), G-DEPTH-2 (`Query.depth`/`ReportSection.depth`
stay flat-only), G-DEPTH-3 (keep the old boolean predicate, renamed,
Python-API-only), and left G-DEPTH-4 (standalone `--depth` flag) to the
lead's judgement since the plan gave no recommendation — deferred as a
follow-on to keep this phase's scope to the actual defect.

**Claude:** removed `ledgerkit.query.ast.Depth` from the selection AST;
`depth:N`/`depth:REGEX=N` now produce a `ledgerkit.query.depth.DepthSpec`
on a new `QueryPlan.depth` (`parser.parse()`'s return type changed from
`QueryNode` to `QueryPlan`), applied by `reports.py`'s
`balance`/`register`/`accounts` as display clipping/aggregation —
matching hledger's real behaviour (confirmed via a full source trace of
every command consuming a `Query`, and 15+ live scenarios against the
pinned 1.52.4 binary), never exclusion. Implemented hledger's exact
custom-`REGEX=N` precedence rule and its multi-term-in-one-query
MIN-based combination (order-independent — distinct from the separate
"last wins" rule for multiple `--depth` CLI flags, which Ledgerkit
doesn't have). Fixed `print` to correctly ignore `depth:` entirely
(previously wrongly excluded every transaction). Found and fixed two
further pre-existing bugs while implementing this: `register()`/
`accounts()` had silently treated the legacy `Query.depth` as an
exclusion filter too (only `balance()` was ever correct); and discovered
— via a genuine executable surprise, not anticipated by the plan — that
hledger's `stats` command uniquely EXCLUDES rather than clips deeper
accounts for its own `Accounts:` count (source-confirmed via
`Ledger.hs:ledgerFromJournal`'s own doc-comment), which Ledgerkit now
replicates exactly via a dedicated `account_excluded_by_depth` function.
Old `Depth` kept as `ledgerkit.query.ast.MaxAccountLevel` — a disclosed,
Python-API-only Ledgerkit-native primitive, unreachable from `-q` string
syntax. 21 new/rewritten tests — 746 total, all passing. Reclassified
`LK-COMPAT-QUERY-DEPTH-001` (`intentional_divergence`→`compatible`),
added `LK-COMPAT-QUERY-DEPTH-STATS-001`, updated
`LK-COMPAT-QUERY-PRINT-INTEGRATION-001` — all `status: self-verified`
pending Phase 5c's independent `compat-differential-tester` dispatch
(not yet run). Updated `dev-docs/api-spec.md`, `dev-docs/architecture.md`,
`dev-docs/hledger-compatibility.md`, `docs/usage.md`,
`knowledge/DECISIONS.md`, `knowledge/DOMAIN_RULES.md` (marked EC-017
resolved).

---

### [Stage C Phase 5, commit 3/3 — independent verification + closeout] — 2026-09-17

Full detail: [dev-docs/retros/STAGE-C-PHASE-5.md](dev-docs/retros/STAGE-C-PHASE-5.md)

**Human:** no further direction needed — this commit executes the process
commit 1/N itself introduced, and closes out the phase.

**Claude:** dispatched a genuinely separate `compat-differential-tester`
agent (not the implementing session) with a full evidence packet, per
this phase's own new Tier 2 rule — the first real application of the
process amended in commit 1/N. The dispatch built its own new fixture
(`tests/fixtures/depth.journal`, 7 accounts depth 2-4, including a
deliberate `assets`/`savings` regex-collision pair) and independently
re-ran every claimed scenario against the pinned hledger 1.52.4 binary:
general/zero/custom-regex depth, specificity precedence, multi-term
MIN-combination order-independence, register/accounts clipping, print's
unconditional depth-blindness, and `stats`' exclusion exception. All
claims held — no mismatches found. `LK-COMPAT-QUERY-DEPTH-001`,
`LK-COMPAT-QUERY-DEPTH-STATS-001`, and `LK-COMPAT-QUERY-PRINT-
INTEGRATION-001` promoted `self-verified` → `verified`, each with its own
independently-authored evidence entry (not the prior session's evidence
copied forward). 746 tests still passing (unchanged — no `ledgerkit/`
code touched this commit, only `tests/fixtures/` and
`dev-docs/compat-register/`, exactly matching
`compat-differential-tester`'s own write-access restriction). Updated
`dev-docs/hledger-compatibility.md`'s depth: row to cite the independent
`status: verified` outcome. `ROADMAP.md`'s Stage C row updated: Phase 5
done.

---

### [Stage C Phase 5A — Planning: CodeCompass development workflow adoption] — 2026-09-24

Full detail: [dev-docs/planning/core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md](dev-docs/planning/core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md), [dev-docs/retros/STAGE-C-PHASE-5A-PLAN.md](dev-docs/retros/STAGE-C-PHASE-5A-PLAN.md)

**Human:** provided a fully-specified phase brief for adopting CodeCompass
v1 into Ledgerkit's normal development process, with an explicit
instruction to insert it into the roadmap immediately before the
currently-planned next Ledgerkit phase and to follow the project's normal
planning/implementation/verification/review/retro process, including a
direct instruction not to manufacture favourable evaluation results.

**Claude:** inserted the `ROADMAP.md` phase row as directly requested,
then produced a planning pass (matching the Stage C Phase 2/Phase 5
precedent for a request this size). Found CodeCompass v1.0.0 has
genuinely shipped (tag `v1.0.0`) and, contrary to the brief's implicit
framing, has already extensively evaluated itself against Ledgerkit as
its principal external reference project across roughly ten phases,
including a live re-confirmation dated the same day this plan was
written — consistently `PASS WITH GAPS`/`LOW` context advantage, a
disclosed structural ceiling (Ledgerkit's own zero-runtime-dependency
design, plus one still-open CodeCompass-side relation-detection gap,
independently re-confirmed against current source), not a defect
Ledgerkit's side can fix. Reframed the phase's objective accordingly:
establish the routine adoption workflow and its own honest evaluation,
not chase a high-context-advantage result the evidence already shows is
unlikely. Also found: no CodeCompass configuration actually exists for
Ledgerkit yet (a stub skill file on disk, unconfigured, not committed);
Ledgerkit's existing 7-agent roster already matches CodeCompass's own
5-role recommended minimum with no gap; and no already-scoped "next
Ledgerkit phase" exists to use as the genuine task (recommended:
`tag:` query-term matching, the most-prepared deferred candidate).
Five human-decision gates recorded, none resolved. No `ledgerkit/`/
`tests/` code touched, no CodeCompass installed/configured — planning
only, as directed.

---

### [Stage C Phase 5A — Plan amended after review] — 2026-09-24

Full detail: [dev-docs/planning/core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md](dev-docs/planning/core-redefinition/22-stage-c-phase-5a-codecompass-workflow-adoption-plan.md) §10, [dev-docs/retros/STAGE-C-PHASE-5A-PLAN.md](dev-docs/retros/STAGE-C-PHASE-5A-PLAN.md)'s amendment addendum

**Human:** reviewed the Phase 5A plan and directed eight targeted
amendments before implementation: test the real agent-facing workflow
(generated Skill/`/discovery`) before direct CLI queries, not CLI-only;
record per-finding provenance in the context packet (four categories);
avoid anchoring the evaluation to prior LOW results — record improvement/
regression/unchanged independently; add a lifecycle/staleness re-sync
test; sequence enrichment deterministic-sync-first with both API-backed
and `enrich apply` paths, never manufactured; verify the authoritative
CodeCompass release state and file any disagreement as a CodeCompass
finding rather than resolve it silently; resolve G-CC-2 to `tag:`
query-term matching absent stronger evidence; retain G-CC-1/3/4/5 unless
evidence requires revision.

**Claude:** amended the plan section by section, retaining its objective,
scope, evaluation safeguards, exit criteria, and separation from the
subsequent feature phase. Re-verified CodeCompass's release state live
(found `README.md` briefly disagreed with its own tag/PyPI-published
state at the original pin — already self-corrected by CodeCompass's own
Phase 70 drift audit one commit later, so no new finding needed, but the
re-check is now a standing part of Step 1). Removed language across
§§1.4/2/3/6 that predicted or normalised a repeat LOW-advantage result,
replacing it with an explicit instruction to independently determine
improvement/regression/unchanged from this phase's own evidence, while
retaining the historical baseline table as background context. Rewrote
Step 4 to require the generated Skill/`/discovery` path before direct
`codecompass query`; rewrote Step 5 to require a four-category provenance
tag per context-packet finding; added Step 9 (lifecycle/staleness
verification, reusing Step 8's own doc edits as the harmless change, no
feature-behaviour change introduced for the test); rewrote Step 2 to
sequence deterministic sync before enrichment and cover both enrichment
paths; resolved gate G-CC-2 to `tag:` query-term matching; refined
G-CC-4/G-CC-5's wording to the user's own restatement. Added a
consistency-review section confirming Phase 5A remains integration/
evaluation-only, the subsequent `tag:` phase remains the first genuine
implementation test, CodeCompass claims stay subordinate to existing
verification controls, and negative/neutral findings remain an acceptable
outcome. Updated `ROADMAP.md`'s Phase 5A summary and appended a dated
addendum to the existing plan retro (not rewritten). No `ledgerkit/`/
`tests/` code touched, no CodeCompass installed/configured — still
planning only.

---

### [Stage C Phase 5A — Implementation: CodeCompass workflow adopted] — 2026-09-25

Full detail: [dev-docs/retros/STAGE-C-PHASE-5A.md](dev-docs/retros/STAGE-C-PHASE-5A.md)

**Human:** approved all five remaining gates ("proceed as recommended"):
G-CC-1 gitignore generated state, G-CC-3 no new agent role, G-CC-4 add
the `CLAUDE.md` pointer, G-CC-5 judge success on workflow usefulness/
evidence quality/provenance/repeatability/maintenance burden.

**Claude:** installed CodeCompass v1.0.0 (`pipx install -e`, editable
local clone) and configured it against Ledgerkit's real repository for
the first time. Found and corrected a real error in this phase's own
planning pass: `CG-004` (spec-doc-to-spec-doc relation detection) was
already fixed upstream (Phase 55b, 2026-09-17) — the plan's claim that it
was "still open" was wrong, caught by re-verifying rather than trusting
prior research forward. Confirmed the fix works on real content (18
genuine relation edges now exist, zero at every prior evaluation) while
also confirming, precisely, that it does not close a narrower, already-
independently-filed CodeCompass gap (`CG-006`, title-vs-filename
matching) — filed as `CC-LK-002`, a third independent corroboration, not
a new discovery. Used `codecompass enrich apply` (the agent-facing path,
no `ANTHROPIC_API_KEY` configured) to enrich one real relation for the
first time this project has exercised that code path. Followed the real
agent-facing entry points (generated Skill, `/discovery`'s own defined
procedure) before direct `codecompass query` calls, per the amended
plan's Step 4. Built a context packet for the genuine next phase (`tag:`
query-term matching) with every finding tagged to one of four provenance
categories (`validation/codecompass/context-packets/
tag-query-matching.md`) — researched and prepared, not implemented.
Filed `CC-LK-003` (the generated Skill/discovery text names the
`sqlite3` CLI as its only documented graph-query fallback, which isn't
installed in this environment). Exercised a real edit→re-sync→refresh
cycle (Step 9), confirming staleness detection and content refresh work
end to end. Documented the routine workflow
(`dev-docs/planning/core-redefinition/04-codecompass-integration.md`
§4.7) and added a real `CLAUDE.md` pointer section around the
mechanically-generated routing table. `.gitignore` updated for
`vendor.toml`/`vendor/` (`context-graph.db` already covered by an
existing rule). Evaluation verdict, independently determined per the
amended plan's own instruction (not assumed from the historical
baseline): mixed, not a flat repeat — vendor/symbol tracking unchanged
(LOW, 0 dependencies), doc-relation detection genuinely improved.
Recommendation: keep as a routine, low-cost per-phase check. No
`ledgerkit/`/`tests/` behaviour changed — 746 tests still passing;
`tag:` query-term matching itself needs its own scoping/plan pass before
implementation begins.

---

### [Stage C Phase 6 — Planning: `tag:` query-matching context curation + design document] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/23-tag-query-matching-design.md](dev-docs/planning/core-redefinition/23-tag-query-matching-design.md), [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md)

**Human:** directed the first use of a new, more rigorous development
process for substantial feature phases (roadmap objective → independent
context curation → design document → human approval → implementation
plan → fresh coding agent → independent verification → doc sync → retro
→ knowledge update), for `tag:NAME[=REGEX]` query-term matching — the
genuine next Ledgerkit feature, already researched but not implemented.
Directed stopping after the design document for explicit approval before
any implementation.

**Claude:** dispatched a fresh, independent `context-curator` agent (no
access to this conversation's prior turns) to re-verify `tag:`'s
semantics directly against the pinned hledger binary/source, explicitly
told not to trust the existing Phase 5A context packet or brief 19 on
faith. It ran CodeCompass's real workflow first (Skill/`/discovery`/
`query`), then nine live differential runs against the pinned binary,
confirming the four propagation/inheritance rules and newly executable-
confirming the always-AND-never-OR combination rule (previously
source-only evidence in brief 19). Found a genuinely new architectural
fact: `accounts`' own posting-tag-stripping matching mode (source-
confirmed to exactly one hledger call site), not named in brief 19. Found
Ledgerkit currently has no tag-inheritance computation at all —
`Journal.declared_account_tags` is parsed and stored but never consumed
— the real remaining implementation gap, not just a missing AST node.
Checked CodeCompass's own gap register before concluding no new finding
was warranted (everything reproduced already-filed, already-diagnosed
gaps). The lead independently spot-checked the report's two most
significant claims against source directly, and found one further fact
the report hadn't explicitly flagged: `matches_transaction`/`matches_
posting` receive no `Journal` parameter today, bearing on inheritance-
implementation cost. Produced a 17-section design document distinguishing
verified-external/existing-decision/proposed/unresolved throughout, with
two explicit unresolved questions (inheritance scope: full vs. a
disclosed own-tags-only subset; `accounts`' matching mode: mirror
hledger's quirk vs. uniform matching), each with a stated recommendation
but no silent decision. No `ledgerkit/`/`tests/` code touched — planning
checkpoint only, stopped for human review as directed.

---

### [Stage C Phase 6 — Design document amended after review] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/23-tag-query-matching-design.md](dev-docs/planning/core-redefinition/23-tag-query-matching-design.md), [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md)'s addendum

**Human:** reviewed the design document and found it not yet ready for
approval — its claim that the four A-D propagation rules were complete
hledger 1.52.4 effective-tag semantics was incomplete, omitting
commodity-directive tag propagation. Directed a targeted correction pass
(re-check the manual/source/tests for commodity tags; determine the
Ledgerkit substrate gap explicitly; resolve same-name/different-value
precedence via a required executable differential matrix, not
interpretation; revisit the `accounts`-command and evaluator-API
recommendations; keep new helpers private by default; update the
planning-checkpoint artefacts recording this as a design-review
correction, not an implementation defect) — explicitly not a redesign,
preserving the existing process structure and human-approval gate.

**Claude:** confirmed the gap directly against the hledger 1.52.4 manual
(`hledger.1:3550-3556`, "Commodity tags") and traced the full source
mechanism (`Journal.jdeclaredcommoditytags`, `journalPostingsAddCommodityTags`,
both gated by `auto_posting_tags_`, traced precisely to
`CliOptions.hs:642`: `True` for every CLI command except `print
--output-format=beancount` — resolving exactly why the original
document's own live tests had already observed account-tag inheritance
working despite the library's own `False` default). Built a five-
transaction precedence fixture and ran it directly against the pinned
binary rather than resolve by interpretation: found **no shadowing**
between posting/account/commodity-sourced same-named tags — all remain
simultaneously, independently matchable, directly contradicting a literal
reading of the manual's "posting tags override account tags override
commodity tags" wording. Made the executable result, not the manual's
prose, the documented basis. Confirmed Ledgerkit has no commodity-tag
storage/parsing substrate at all (`ledgerkit/parser.py`'s `commodity`
directive handling actively discards its own comment text) — a second,
distinct gap alongside the already-known missing account-inheritance
computation. Redefined §9.1's Option A as genuinely complete (four
sources, not three); softened the evaluator-API recommendation from a
required positional `Journal` parameter to backward-compatible
alternatives (keyword-only parameter, context object, or pre-evaluation
materialization), with "fail loudly, never silently narrow" as a binding
constraint; reversed the `accounts`-command recommendation (now:
replicate hledger's account-inherited-only mode, not diverge) after
re-weighing that general internal-consistency preference wasn't a strong
enough reason against a confirmed, narrow, cheap-to-implement quirk;
changed new-helper visibility default to private. Expanded the proposed
differential-test matrix to cover all five source-pair precedence
combinations. Appended a dated addendum to the existing planning retro
(not rewritten) explicitly recording this as a design-review correction
caught before implementation. No `ledgerkit/`/`tests/` code touched —
still planning only, still stopped for human review as directed.

---

### [Stage C Phase 6 — Design document: small final correction pass] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/23-tag-query-matching-design.md](dev-docs/planning/core-redefinition/23-tag-query-matching-design.md), [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-PLAN.md)'s second addendum

**Human:** directed a small final correction pass (explicitly not a
redesign, curator re-run, or implementation start): fix plain `accounts
tag:X` semantics (the prior amendment's finding was still incomplete);
clarify transaction-level matching's conceptual rule; fix a real error
in the evaluator-API wording (a keyword-only parameter with no default
is still mandatory, contrary to what was claimed); resolve the
commodity-tag substrate's scope as in-phase, not a prerequisite
sub-phase; preserve everything else already approved-in-direction.

**Claude:** verified each correction live before writing it down, not on
the review's restatement alone. Confirmed via a direct pinned-binary run
(`accounts tag:rate=4`, a transaction-header-only tag) that transaction-
level tags survive `accounts`' own posting/commodity-tag stripping —
the prior amendment's "account-inherited tags only" claim was itself
incomplete; the correct rule is a four-way split (transaction-level and
account-inherited visible; posting-own and commodity-propagated not).
Corrected transaction-level matching's stated rule to "own tags
directly, OR any posting's effective tags," sourced precisely to
`transactionAllTags t = ttags t ++ concatMap ptags (tpostings t)`.
Fixed the evaluator-API recommendation's real Python error (keyword-
only-with-no-default is still mandatory on every call) — corrected to
`journal: Journal | None = None` as the leading backward-compatible
candidate, with explicit-failure-not-silent-degradation restated as the
binding constraint regardless of final shape. Resolved the commodity-tag
substrate's scope as in-phase (design-approved, not implemented):
proposed `Journal.declared_commodity_tags`, same-line/follow-on
directive-comment capture, private helpers. Updated §§2.5, 6, 9.1, 9.2,
11, 16, 17 accordingly; appended a second dated addendum to the existing
planning retro (original content and first addendum both untouched).
Approval list shortened from five items to two. No `ledgerkit/`/`tests/`
code touched — still planning only, still stopped for human review.

---

### [Stage C Phase 6 — `tag:NAME[=REGEX]` query matching implemented] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/23-tag-query-matching-design.md](dev-docs/planning/core-redefinition/23-tag-query-matching-design.md), [dev-docs/planning/core-redefinition/24-tag-query-matching-implementation-plan.md](dev-docs/planning/core-redefinition/24-tag-query-matching-implementation-plan.md), [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md)

**Human:** directed implementation of the already-approved design/plan
(Option A — complete four-source effective-tag semantics; `accounts`
mode replicating hledger; evaluator API shape `journal: Journal | None =
None`) — a fresh coding-agent dispatch (Step 6 of this project's
design → plan → implement → verify process), explicitly not authorised
to redesign anything the design/plan already resolved, and explicitly
not authorised to promote any compat-register entry past
`status: proposed`.

**Claude:** implemented `tag:NAME[=REGEX]` end to end. New commodity-tag
substrate: `Journal.declared_commodity_tags` (mirrors
`declared_account_tags`'s shape); `parser.py`'s `commodity` directive now
captures same-line and follow-on comment tags via the same mechanism
`account` directives already used (a new `commodity_comment_target`
tracking variable, mutually exclusive with and reset alongside
`account_comment_target`). New private `ledgerkit/tags.py` helpers:
`_inherited_account_tags` (ancestor-chain walk, closing a pre-existing
gap where `declared_account_tags` had no consumer), `_commodity_tags`,
`_posting_commodities`, `_effective_tags` (the full four-source union,
plain concatenation — deliberately **no shadowing/exclusion logic**, per
the design's executable-verified finding that hledger's manual
"tags override" wording does not mean exclusion for query-matching), and
`_accounts_effective_tags` (the `accounts` command's narrower
transaction-own + account-inherited-only variant). New `Tag` AST node
(`ledgerkit/query/ast.py`), added to the `QueryNode` Union; `_build_tag`
parser rule (`ledgerkit/query/parser.py`, `str.partition("=")`-based,
first-`=`-split, reusing `compile_hledger_regex`); no new AND/OR bucket
needed (`tag:` isn't OR-eligible, falls into `other_terms` automatically,
correctly AND-combining multiple `tag:` terms). `matches_transaction`/
`matches_posting` (`ledgerkit/query/eval.py`) each gained
`journal: Journal | None = None`; a `Tag` node evaluated with
`journal=None` raises `ValueError`, never silently narrowing to
own-tags-only. A new private `_matches_posting_for_accounts` wrapper
(sharing the same recursive And/Or/Not dispatch as `matches_posting` via
a `tag_source` parameter, not a duplicated copy) gives `reports.
accounts()` its own narrower Tag-matching mode; `balance`/`register`/
`print`/`stats` are unaffected. All four existing report call sites plus
`cli.py`'s `print` now pass `journal=journal` through. 6 new compat-
register entries at `status: proposed` (`LK-COMPAT-QUERY-TAG-001`,
`-COMBINE-001`, `-INHERIT-001`, `-COMMODITY-001`, `-ACCOUNTS-001`,
`LK-COMPAT-PARSER-TAG-COMMODITY-001`) — independent
`compat-differential-tester` verification is a separate, later step, not
run by this session. 81 new tests (unit: query parser/eval, tags.py
helpers, commodity directive tag capture; integration: a new
`tests/fixtures/tags.journal` fixture plus `reports.py`/CLI wiring for
all five commands) — full suite (827 tests) passes. Docs
synced in the same response: `dev-docs/api-spec.md` (the two disclosed,
approved changes — `QueryNode`'s `Tag` member, the `journal` parameter —
plus documenting the also-approved `Journal.declared_commodity_tags`
field addition, judged in scope per design §11's own explicit disclosure
of that field and CLAUDE.md's unconditional doc-sync rule — see
`knowledge/DECISIONS.md`), `dev-docs/hledger-compatibility.md`,
`dev-docs/architecture.md`, `docs/usage.md`, `docs/journal-format.md`,
`knowledge/DECISIONS.md`, `knowledge/DOMAIN_RULES.md`. Flagged, not
acted on unilaterally: `ledgerkit/reports.py` (now ~720 lines) and
`ledgerkit/cli.py` (~510 lines) were already over CLAUDE.md's 300-500
line module-size guidance before this phase; this phase added modestly
to both rather than triggering the threshold itself — noted in the
phase retro for a human decision on whether a split is warranted.

---

### [Stage C Phase 6 — independent verification] — 2026-09-25

Full detail: [dev-docs/compat-register/](dev-docs/compat-register/) (six `LK-COMPAT-QUERY-TAG-*`/`LK-COMPAT-PARSER-TAG-COMMODITY-001` entries, plus `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`), [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md)'s addendum

**Human:** approved the design (Option A, `accounts`-mode replication)
and directed the implementation to proceed; the standing process
requires a genuinely separate `compat-differential-tester` dispatch
before any new compat-register entry is promoted to `verified` — that
step was carried out this session.

**Claude:** dispatched an independent `compat-differential-tester`
(no access to the implementing session's own conversation) against the
pinned hledger 1.52.4 binary, on freshly built fixtures. Five of six
entries promoted to `status: verified`: `LK-COMPAT-QUERY-TAG-COMBINE-
001`, `LK-COMPAT-QUERY-TAG-INHERIT-001` (re-confirming the no-
shadowing/union precedence finding independently), `LK-COMPAT-QUERY-
TAG-COMMODITY-001`, `LK-COMPAT-QUERY-TAG-ACCOUNTS-001` (all four
visibility cells individually confirmed), and `LK-COMPAT-PARSER-TAG-
COMMODITY-001`. Found one real divergence, not papered over: `tag:
NAME=` (empty value pattern) is accepted and matches in Ledgerkit but
rejected outright by real hledger at parse time — confirmed not `tag:`-
specific (the same gap exists for `acct:`/`desc:`), root-caused to
`ledgerkit.query.regex.compile_hledger_regex` not rejecting an empty
pattern. Filed as `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`; `LK-COMPAT-
QUERY-TAG-001` itself correctly left at `status: proposed` for this one
false claim, with every other claim in it independently re-confirmed.
Updated `dev-docs/hledger-compatibility.md`'s `tag:`/`accounts tag:X`
rows and appended a dated addendum to the implementation retro. 827
tests still passing (4 new fixtures added, no `ledgerkit/` source
changed by this step). The empty-regex divergence is unscoped follow-on
work, not blocking this phase.

---

### [Stage C Phase 6 — closeout, marked `[DONE]`] — 2026-09-25

Full detail: [ROADMAP.md](ROADMAP.md) Stage C row, [dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md)'s closeout addendum

**Human:** confirmed Stage C Phase 6 complete (implementation `0523426`/
`fa05bbc`, independent verification `fe9dfe5`, prior reconciliation
`5887ea8`) and directed a closeout-only pass: mark Phase 6 `[DONE]`;
reconcile all current-facing status docs; preserve the empty-regex
mismatch exactly as an explicit, unfolded-in follow-up; no `ledgerkit/`/
`tests/` changes; do not mark Stage C itself `[DONE]`; record the
remaining Stage C backlog with named next priorities.

**Claude:** marked Stage C Phase 6 `[DONE]` in `ROADMAP.md` (Stage C
row itself remains `[IN PROGRESS]`). Swept every current-facing status
reference (`ROADMAP.md`, `CONTEXT.md`, `dev-docs/architecture.md`,
`dev-docs/api-spec.md`, `dev-docs/hledger-compatibility.md`,
`knowledge/DECISIONS.md`) for stale "pending"/"not yet verified"
language — found none beyond what the prior verification-closeout
commit (`5887ea8`) had already reconciled. Appended a closeout addendum
to the implementation retro (never rewriting its prior content or
addendum). Recorded the remaining Stage C backlog directly in the
roadmap row: (1) scope the cross-cutting empty-regex compatibility fix
(`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, affects `acct:`/`desc:`/`tag:`
alike); (2) converge the legacy public `Query` pathway toward the
query-AST/compatibility-shim architecture; (3) explicitly resolve the
planned `PythonRegex` extension syntax — with `cur:`, smart/period
dates, and a standalone `--depth`/`-N` flag kept as non-blocking
follow-on items, unscoped unless separately promoted. 827 tests
unaffected — no `ledgerkit/`/`tests/` code touched by this pass.

---

### [Stage C Phase 7 — planning: empty-regex-pattern rejection] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-design.md](dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-design.md), [dev-docs/planning/core-redefinition/25-query-regex-empty-pattern-matrix.md](dev-docs/planning/core-redefinition/25-query-regex-empty-pattern-matrix.md), [dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-PLAN.md](dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-PLAN.md)

**Human:** directed planning of the next Stage C phase, per Phase 6's
own closeout recommendation: resolve `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-
001` (Ledgerkit accepts an empty regex pattern where real hledger
rejects one).

**Claude:** dispatched `context-curator` for Step 1 first — it
correctly self-refused, since general hledger/source research falls
outside its actual narrow charter (rating CodeCompass's usefulness),
not something to stretch informally the way a prior phase's retro
implied. Re-routed to a `compat-differential-tester` dispatch for the
live-binary matrix, plus direct lead-performed auditing of `ledgerkit/
query/regex.py`/`parser.py`. Found the scope is narrow: hledger rejects
only the literal empty pattern string (not any pattern whose semantics
merely admit an empty match — `.*`/`a*`/`^$`/`()` are all accepted),
and every regex-taking query term already routes through one shared
function (`validate_hledger_regex`), so the fix is a single check
there, reusing the existing public `UnsupportedRegexConstructError` —
no new exception class, no `api-spec.md` change. Design document
written and stopped for explicit human approval (§11's four-item gate)
— no `ledgerkit/`/`tests/` code touched.

---

### [Stage C Phase 7 — design document: targeted correction pass] — 2026-09-25

Full detail: [dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-design.md](dev-docs/planning/core-redefinition/26-query-regex-empty-pattern-design.md), [dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml](dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml)

**Human:** directed a targeted correction pass on the Phase 7 design
(explicitly not a re-scope, not a re-run of the research matrix, not
implementation): make the shared validator's proposed error message
generic instead of `tag:`-specific; correct the "no public API change"
framing to accurately describe a backward-compatible behavioural change
requiring an `api-spec.md` update; actually file the separately-
discovered empty-alternation-branch divergence as its own compat-
register entry instead of an informal note; specify the correct
rename-and-reclassify closeout mechanics for `LK-MISMATCH-QUERY-TAG-
EMPTYVALUE-001` instead of an in-place `kind:` flip.

**Claude:** corrected all four points in the design document (§5/§5.1,
§7, §8, §11) and filed `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`
(`kind: unexplained_mismatch`) for the empty-alternation-branch
family, scoped strictly to what's independently verified on both
sides — `(|)` confirmed as a real divergence (hledger rejects it,
Ledgerkit's `re` accepts it); `a|`/`|a`/`(a|)`/`(|a)` recorded as
hledger-side-only confirmed, not asserted as divergences. Added it to
`dev-docs/compat-register/UNEXPLAINED.md`'s open-entries table. The
narrow `pattern == ""` fix, its single chokepoint
(`validate_hledger_regex`), its non-goals, and its test plan are all
unchanged. No `ledgerkit/`/`tests/*.py` code touched — still stopped
for human approval, now against the amended design §11 (five items).

---

### [Stage C Phase 7 — implemented, independent verification pending] — 2026-09-25

Full detail: [dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md)

**Human:** directed implementation of the amended, approved design, with
four final amendments folded in at implementation time: treat the fix
as an intentional **breaking** (not backward-compatible) pre-1.0
correction, reconciled across `versioning.md`/`api-spec.md`; keep the
empty-alternation mismatch untouched; fix the compat-register lifecycle
so a resolved mismatch is renamed-and-linked rather than edited in
place, generalised beyond this one entry; and cover the specified test
matrix. Independent verification explicitly deferred to a separate
dispatch before any compat-register promotion.

**Claude:** `ledgerkit/query/regex.py`'s `validate_hledger_regex` now
rejects `pattern == ""` via the existing `UnsupportedRegexConstructError`
with a fully generic message ("pattern must not be empty (hledger
rejects an empty regex at parse time)") — no `tag:`-specific advice in
the shared validator. `dev-docs/api-spec.md`/`dev-docs/versioning.md`
updated to describe this accurately as breaking, not backward-compatible,
with a new general pre-1.0.dev1 breaking-change policy section (no
version bump invented). `dev-docs/compat-register/schema.md` and
`09-compatibility-system.md` §9.7 gained a general-purpose
mismatch-resolution lifecycle (`resolved_into`/`resolved_date`/`resolves`
fields, a new "Resolved entries" table in `UNEXPLAINED.md`) plus a
correction allowing `implementation`/`tests` to be empty for
`unexplained_mismatch` entries, not only `unsupported` ones — not yet
applied to the actual mismatch entry, deliberately deferred until
independent verification. 17 new tests (844 total, up from 827,
all passing): empty-pattern rejection across `acct:`/`desc:`/bare
`tag:`/`tag:NAME=`/`depth:=N`/`not:acct:`; the CLI's existing
`QueryParseError`-to-exit-1 convention reused unchanged; explicit
regression guards that `.*`/`a*`/`^$`/`()` remain accepted.
`knowledge/DECISIONS.md`/`DOMAIN_RULES.md` updated. `LK-MISMATCH-
QUERY-REGEX-EMPTYALT-001` untouched. No compat-register entry promoted
— that is the mandatory next, genuinely separate step.

---

### [Stage C Phase 7 — independent verification and register resolution] — 2026-09-25

Full detail: [dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-IMPLEMENTATION.md)'s addendum

**Human:** directed independent verification (a genuinely separate
`compat-differential-tester` dispatch) before any compat-register
promotion, then resolution of `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`
through the new lifecycle mechanism once that verification confirmed
the fix.

**Claude:** dispatched an independent `compat-differential-tester`
(fresh fixture, no access to the implementing session's own
conversation); it confirmed the fix precisely — `acct:`/`desc:`/bare
`tag:`/`tag:NAME=`/`depth:=N` all now reject identically on both
hledger and ledgerkit, including under `not:` wrapping, with no
overshoot (`.*`/`a*`/`^$`/`()` confirmed still accepted by both) and a
confirmed-generic error message. Exercised the new resolution-lifecycle
mechanism for the first time: created `LK-COMPAT-QUERY-TAG-EMPTYVALUE-
001` (`kind: compatible`, `status: verified`, `resolves:` back-link);
retained `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` untouched except for a
new `resolved_into:`/`resolved_date:` pair; moved its row in
`UNEXPLAINED.md` from "Open entries" to "Resolved entries". Corrected
`LK-COMPAT-QUERY-TAG-001`'s own false `tag:NAME=` claim in place and
promoted it to `status: verified`. Added evidence notes (no status
change) to `LK-COMPAT-QUERY-ACCT-001`/`DESC-001`/`DEPTH-001` for their
own empty-pattern slice. `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`
untouched, still open, still out of scope. `dev-docs/hledger-
compatibility.md` updated. Phase 7 is now implementation-and-
verification-complete; `[DONE]` remains the user's own call.

---

### [Stage C Phase 8 — planning: `Query`-as-compatibility-shim convergence] — 2026-09-26

Full detail: [dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md](dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md), [dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md](dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md)

**Human:** directed proceeding with the next Stage C backlog item —
converging the legacy `Query` dataclass's filtering onto the
`ledgerkit.query` AST/evaluator.

**Claude:** found this executes an already-approved architectural
target (`07-query-regex.md` §7.2, written before Stage C began: `Query`
should become "a compatibility constructor that compiles to a
`QueryAST`... rather than a parallel filtering path"), not a new
direction. Confirmed the real-world blast radius is small: the one
known external consumer, `ledgerkit-editor`, never calls into
Ledgerkit's own `Query`-matching code at all (only uses `Query` as a
plain data container, matched by its own independent logic), and
Ledgerkit's own test suite's `Query(...)` usages use no `HledgerRegex`-
excluded construct. Found and flagged, before any code was written, a
real correctness trap: `DateSpan.end` is exclusive (matching hledger),
`Query.date_to` is inclusive — a naive translation would silently
exclude transactions dated exactly `date_to`; the design specifies the
correct `+1 day` translation and a required named regression test.
Design document stops for explicit human approval (one blocking item:
full `HledgerRegex` strictness for `Query`'s regex fields vs. a
permissive fallback — lead recommends strictness) — no `ledgerkit/`/
`tests/` code touched.

---

### [Stage C Phase 8 — design document: targeted correction pass] — 2026-09-26

Full detail: [dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md](dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md), [dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md](dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md)'s addendum

**Human:** directed a targeted correction pass (explicitly not a
re-scope, no implementation): found the original blast-radius analysis
incomplete — it checked direct `Query(...)` test construction but
missed a real internal producer of `Query.account` values using an
excluded `HledgerRegex` construct — plus three further gaps (`stats`
behaviour, `_matches_pattern`/`ReportSection` scope, eager validation)
and two smaller correctness issues (module placement, `date.max`
overflow).

**Claude:** confirmed each point against the actual source before
writing it down. `Journal.balance`/`.register`'s deprecated `accounts=
[...]` parameter, for two or more accounts, synthesizes `Query.account`
via `(?:...)` non-capturing-group alternation — confirmed rejected by
`HledgerRegex`, confirmed zero existing test coverage for this path.
Redesigned to build an `Or(...)` AST directly (§5.1a). Confirmed
`balance_from_spec` has its own separate filtering loop still needing
`_matches_pattern` (retained, refactored to route through
`compile_hledger_regex` instead of retired, §5.1b). Confirmed
`stats(query=...)` really does silently ignore `account`/`not_account`
today (a pre-existing documented `TODO`) — full convergence closes this
as an explicit, disclosed correction (§5.1c). Fixed the translator to
validate eagerly before constructing AST nodes (§5.1a), moved it to a
new `ledgerkit/query/compat.py` module to avoid a real circular import
(§5.1), and corrected the date-translation for the `datetime.date.max`
overflow edge case. Blast-radius wording corrected from "empty" to the
accurate, narrower conclusion. Core decision unchanged (Option A, frozen
`Query` field shape, non-predicate `depth`). Approval gate grew from
three items to six. No `ledgerkit/`/`tests/` code touched.

---

### [Stage C Phase 8 — design document: second targeted correction pass] — 2026-09-26

Full detail: [dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md](dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md), [dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md](dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-PLAN.md)'s second addendum

**Human:** directed a final targeted correction pass (explicitly not a
re-scope, no implementation): found `balance_from_spec`'s outer query
should converge fully rather than staying on `_matches_pattern`;
`Journal.to_dataframe` was missed as a `_posting_matches` consumer; the
deprecated `accounts=[...]` shim's zero/one/many cases weren't all
handled explicitly; §5.2's "no observable change beyond regex
strictness" was no longer accurate; the design needed a complete
per-consumer inventory instead of relying on `Query(...)` grep results;
the approval gate needed reducing to the actual remaining decisions
with explicit recommendations.

**Claude:** converged `balance_from_spec`'s outer `query.account`/
`.payee`/`.not_account` onto `_query_to_ast` + `matches_posting`,
leaving `ReportSection.accounts`/`.exclude` as the one genuinely
separate construct (§5.1b, rewritten). Confirmed `Journal.to_dataframe`
calls `_posting_matches` directly (`models.py:456,461`) and specified
its migration to the same canonical path (§5.1d, new) — `_posting_
matches` now has zero remaining callers project-wide, confirmed by
grep. Found and fixed a second bug in the prior pass's own deprecated-
shim fix: `accounts=[]` fell through to the many-accounts branch,
producing `Or(())`, which matches nothing — the opposite of "no
filter"; specified explicit zero/one/many handling (§5.1a). Rewrote
§5.2 with all six intentional behaviour changes stated explicitly.
Added §5.3, a complete table of every `Query` consumer (seven) and how
each reaches the canonical engine. Rewrote §12's approval gate with an
explicit recommended choice for every item — only regex strictness
(Option A) remains genuinely blocking. Core decision unchanged
throughout. No `ledgerkit/`/`tests/` code touched.

---

### [Stage C Phase 8 — Query-as-compatibility-shim convergence, implementation] — 2026-09-26

Full detail: [dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md](dev-docs/planning/core-redefinition/27-query-shim-convergence-design.md), [dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md)

**Human:** directed implementation of the fully-approved, twice-amended
design (Option A regex strictness, the `stats` correction, the
`ReportSection` scope boundary, and `QueryParseError` reuse all locked
in) via a fresh coding agent, per this project's design → approval →
fresh-agent → independent-verification process.

**Claude:** implemented `ledgerkit/query/compat.py` (new module:
`_query_to_ast`, `_validated`, `_exclusive_end`) and converged all seven
`Query`-shaped filtering paths onto it: `reports.balance`/`register`/
`accounts`/`stats` (the `stats` convergence closing a pre-existing
`account`/`not_account`-ignored gap — an intentional, disclosed
correction, not incidental), `reports.balance_from_spec`'s outer query,
`Journal.to_dataframe` (migrated off `reports._posting_matches`, which
is now retired — zero remaining callers anywhere in `ledgerkit/`,
confirmed by grep and a dedicated static test), and `Journal.balance`/
`.register`'s deprecated `accounts=[...]` shim (explicit zero/one/many
handling — zero stays "no filter" without ever constructing `Or(())`,
one stays a raw regex passthrough, two-or-more builds an `Or(Acct(...),
...)` AST directly instead of the `(?:...)`-based string synthesis
`HledgerRegex` rejects). `reports._matches_pattern` is retained — not
retired — as the one deliberately separate construct for
`ReportSection.accounts`/`.exclude`, refactored to route through
`ledgerkit.query.regex.compile_hledger_regex` instead of its own ad hoc
Python-regex-metacharacter heuristic. `Query.account`/`.not_account`/
`.payee` are now `HledgerRegex`-strict (Option A) — an excluded
construct or empty pattern now raises `QueryParseError`, reusing that
existing exception type rather than a new one. `Query.date_to`
(inclusive) translates to `DateSpan.end` (exclusive) via `_exclusive_end`,
with the `datetime.date.max` overflow case mapped to `end=None` instead
of raising. This is a disclosed, intentional set of **breaking** changes
(all six enumerated in the design's own §5.2), made pre-`1.0.0`, not
described as "no observable change." Added `tests/test_query/test_compat.py`
(translator unit tests) and extensive new integration coverage in
`tests/test_reports.py`/`tests/test_dataframe.py`; the full suite
(897 tests, `29` skipped — pandas-optional — up from 844) passes. Synced
`dev-docs/api-spec.md`, `dev-docs/architecture.md`,
`dev-docs/hledger-compatibility.md`, `docs/python-api.md`,
`knowledge/DECISIONS.md`, `knowledge/DOMAIN_RULES.md`. Filed
`dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml` at
`status: proposed` — promotion to `verified` is a separate,
independently-dispatched `compat-differential-tester` step, not done
here.

---

### [Stage C Phase 8 — independent verification] — 2026-09-26

Full detail: [dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml](dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml), [dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-8-QUERY-SHIM-IMPLEMENTATION.md)'s addendum

**Human:** implicit via the standing process — independent verification
is mandatory before any compat-register promotion.

**Claude:** dispatched a genuinely separate `compat-differential-tester`
(fresh fixture, no access to the implementing session's conversation).
Confirmed all eight of the design's highest-risk claims: `Query`-vs-`-q`
parity for `balance`/`register`/`accounts` (including identical
rejection of excluded constructs/empty patterns); `stats`'s genuinely
new account/not_account narrowing (unfiltered 6/6 vs. filtered 3/2,
matching `-q "acct:food" stats` exactly); `balance_from_spec`'s outer-
query strictness and `ReportSection.accounts`/`.exclude`'s independent
validation; `Journal.to_dataframe`'s eager validation against an empty
journal; the deprecated `accounts=[...]` shim's zero/one/many cases,
with `accounts=[]` confirmed identical to no filter (not `Or(())`, the
bug caught during design review); the `datetime.date.max` edge case;
and ordinary inclusive `date_to`. No discrepancies found. `LK-COMPAT-
QUERY-SHIM-001` promoted `proposed` → `status: verified` by the
independent dispatch itself. 897 tests reconfirmed passing. Phase 8 is
now implementation-and-verification-complete; `[DONE]` remains the
user's own call.

---

### [Stage C Phase 8 — compat-register overclaim correction] — 2026-09-26

Full detail: [dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml](dev-docs/compat-register/LK-COMPAT-QUERY-SHIM-001.yaml)'s "CORRECTION, 2026-09-26" note and second evidence entry

**Human:** implicit via the standing process — a compat-register claim
found to overstate its evidence must be corrected, not left standing.

**Claude:** a further review of `LK-COMPAT-QUERY-SHIM-001`'s own text
(not a code or behaviour change, and not caught by the independent
verification dispatch above) found item 6's `reason:` line overclaimed:
it said the deprecated `Journal.balance`/`.register(accounts=[...])`
wrapper's public behaviour was "preserved for every input the wrapper
could previously accept without raising." That was too broad — a
single-account value using a Python-only regex construct outside
`HledgerRegex` (e.g. `accounts=[r"\d+"]`) previously reached the old
permissive matcher and was accepted; under Option A it now intentionally
raises `QueryParseError`, the same consequence every other `Query` field
has. Corrected the compat-register entry, the design document (`27-
query-shim-convergence-design.md` §5.2 item 6), and `dev-docs/
api-spec.md`'s `accounts=[...]` note to the accurate, narrower claim:
`accounts=[]` stays no-filter; an ordinary `HledgerRegex`-portable
single-account pattern is unchanged; a Python-only single-account regex
now intentionally rejects; two-or-more accounts retain their OR-matching
behaviour via the new `Or(...)` AST. A second, genuinely separate
`compat-differential-tester` dispatch independently re-verified all four
corrected-claim cases (zero/ordinary-single/Python-only-single/multiple)
via direct Python-level calls (no hledger-binary equivalent applies to
this internal-only parameter) — confirmed exactly as stated, no mismatch
found; `status: verified` stands on the corrected, narrower claim, with
a new evidence entry. Added two regression tests the re-verification
found missing (`test_balance`/`test_register_one_account_excluded_
construct_now_raises`). 899 tests total, all passing (up from 897). No
`ledgerkit/` behaviour changed by this correction — documentation,
compat-register, and test-coverage closure only.

---

### [Stage C Phase 8 — marked `[DONE]`] — 2026-09-26

Full detail: `ROADMAP.md`'s Stage C row

**Human:** confirmed Stage C Phase 8 (`Query`-as-compatibility-shim
convergence) complete.

**Claude:** marked Phase 8 `[DONE]` in `ROADMAP.md` (Stage C row itself
stays `[IN PROGRESS]`). This followed a `docs-maintainer` reconciliation
pass, an independent `docs-reconstructor` drift audit (NO DRIFT for
this phase), and an independent `release-phase-auditor` Definition-of-
Done audit (PASS, all nine checklist items independently confirmed) —
all run after the compat-register overclaim correction below. No
`ledgerkit/`/`tests/` code touched by this closeout.

---

### [Stage C closeout — Phase 7 gates, Phase 9 planning, PythonRegex disposition] — 2026-09-27

**Human:** directed closing out Stage C: finish Phase 7's outstanding
`docs-reconstructor`/`release-phase-auditor` gates, resolve
`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`, explicitly resolve `PythonRegex`,
confirm the remaining query-language backlog is genuinely deferred, and
run final Stage C completion audits.

**Claude:** ran Phase 7's missing closeout gates — an independent
`docs-reconstructor` audit (NO DRIFT) and `release-phase-auditor` audit
(PASS) — and marked Phase 7 `[DONE]`. Re-established `LK-MISMATCH-
QUERY-REGEX-EMPTYALT-001` fresh from source and a live pinned-hledger
run (not trusted from its prior notes, which predated Stage C Phase 7's
own code changes): found the divergence is larger than originally filed
(18 confirmed patterns, not 5) and traced the root cause to hledger's
own regex-tdfa delegation with zero pre-validation. Produced a design
(`28-empty-alternation-regex-design.md`) specifying an escape-aware,
single-character-adjacency detection rule, hand-verified against the
full 31-pattern matrix. Resolved `PythonRegex` as explicitly deferred
(`knowledge/DECISIONS.md`) — no implementation, not dropped either; no
concrete syntax was ever finalised, no code exists, no consumer has
asked for it. Confirmed `cur:`, smart/period dates, a standalone
`--depth`/`-N` flag, and `check`'s non-wiring from `-q` are all
genuinely, already-documented deferred/non-blocking items, not
accidentally incomplete Stage C exit criteria. No `ledgerkit/`/`tests/`
code touched by this pass.

---

### [Stage C Phase 9 — empty-alternation-branch regex rejection implemented] — 2026-09-27

**Human:** directed implementing `28-empty-alternation-regex-design.md`
through the normal fresh-agent design → implement → verify workflow,
resolving `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`, the last item on
Stage C Phase 6's own backlog.

**Claude:** added `ledgerkit.query.regex._has_empty_alternation_branch`
(a dedicated, escape-aware linear scan — not folded into
`_EXCLUDED_CONSTRUCT`'s existing single compiled regex), wired into
`validate_hledger_regex` alongside the pre-existing `pattern == ""`
check. Independently re-verified the design's own hand-verified
algorithm against all 31 matrix patterns before trusting it (found
correct, no bug). Rejects the full 18-pattern empty-alternation-branch
family (`(|)`, `a|`, `|a`, `(a|)`, `(|a)`, `a||b`, `(a|)|b`, `||`, `|`,
`(|)|c`, `a|(|b)`, `(||)`, `a|||b`, `(|)*`, `(a)|`, `|(a)`, `a(|)b`,
`(a|)(b)`), matching real hledger's regex-tdfa engine's own parse-time
rejection; `()`, `(a)`, `a|b`, `(a|b)`, `()|a`, `a|()`, anchor-only
branches, and escaped pipes/parens (13-pattern regression set) remain
accepted. Breaking change, pre-`1.0.0` (`1.0.0.dev1`), same category as
Stage C Phase 7's own empty-pattern-string fix. 36 new tests (935
total, up from 899): 18 must-reject + 13 must-accept unit tests, 4
parser-level integration tests, 1 CLI-level integration test. New
compat-register entry `LK-COMPAT-QUERY-REGEX-EMPTYALT-001` created
(`kind: compatible`, `resolves: LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`,
`status: proposed` — deliberately not self-promoted further); the
original mismatch entry left untouched (no `resolved_into` yet —
gated on a genuinely separate `compat-differential-tester` dispatch,
the mandatory next step, not performed by this session). Synced
`dev-docs/hledger-compatibility.md`, `dev-docs/api-spec.md` (docstring
only, no signature change), `knowledge/DOMAIN_RULES.md` (the exact
adjacency rule), and `knowledge/DECISIONS.md` (why a dedicated scan was
chosen over extending `_EXCLUDED_CONSTRUCT`). Retro:
`dev-docs/retros/STAGE-C-PHASE-9-EMPTY-ALTERNATION-IMPLEMENTATION.md`.
Stage C itself remains `[IN PROGRESS]`.

---

### [Stage C Phase 9 — independently verified, mismatch resolved] — 2026-09-27

Full detail: [dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml](dev-docs/compat-register/LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml), [dev-docs/retros/STAGE-C-PHASE-9-EMPTY-ALTERNATION-IMPLEMENTATION.md](dev-docs/retros/STAGE-C-PHASE-9-EMPTY-ALTERNATION-IMPLEMENTATION.md)'s addendum

**Human:** standing process — mandatory independent verification before
any compat-register promotion.

**Claude:** dispatched a genuinely separate `compat-differential-tester`
(fresh fixture, no access to the implementing session's conversation).
Confirmed all 31 matrix patterns (18 must-reject, 13 must-accept) across
two query prefixes (62 comparisons), no regression to Stage C Phase 7's
own fix, full suite re-confirmed independently (935 tests). No
discrepancy found. Resolved `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`
through the register's resolution lifecycle: `LK-COMPAT-QUERY-REGEX-
EMPTYALT-001` promoted `proposed` → `status: verified`; the mismatch
entry retained as history (`resolved_into`/`resolved_date` added);
`UNEXPLAINED.md`'s open-entries table is now empty — zero remaining
`unexplained_mismatch` entries anywhere in the register. This closes
the last substantive Stage C Phase 6 backlog item.

---

### [Stage C — full, Stage-wide docs-maintainer reconciliation] — 2026-09-27

**Human:** directed a full, Stage-C-wide reconciliation of every
current-truth doc against the actual, now-complete nine-phase
implementation — verified fresh from source/tests, not from any prior
per-phase docs-maintainer pass's own self-report.

**Claude:** read `ledgerkit/query/` in full (`ast.py`, `parser.py`,
`eval.py`, `regex.py`, `depth.py`, `compat.py`), `reports.py`'s five
report functions, `models.py`'s `Query`/report methods, `cli.py`'s `-q`
wiring, and every `LK-*-QUERY-*` compat-register entry (confirmed
`UNEXPLAINED.md`'s "Open entries" table is genuinely empty). Found and
fixed real drift: `dev-docs/api-spec.md`'s CLI flag reference was
missing `-q`/`--query` and `-c`/`--commodity-style` entirely; a
Phase-6/Phase-7 mislabel on the empty-pattern-rejection breaking-change
note; a stale `status: proposed` for `LK-COMPAT-QUERY-REGEX-EMPTYALT-001`
in both `api-spec.md` and `dev-docs/hledger-compatibility.md` (now
`status: verified`, independently confirmed 2026-09-27); and, in
`docs/python-api.md`, a pre-existing false claim that `Query.depth`
*excludes* deeper accounts for `accounts()`/`register()` (corrected
Stage C Phase 5 — it clips/rolls up, never excludes, for all three),
a stale single-commodity `Decimal` example predating Milestone 3's
`dict[str, dict[str, Decimal]]` balance return type, and an inaccurate
claim that `accounts()` accepts a `query=` parameter (it does not).
`dev-docs/architecture.md`'s query-subpackage description was confirmed
to already accurately describe the final, Phase-8-converged
architecture (one canonical evaluation path via `_query_to_ast`, one
disclosed remaining exception for `ReportSection.accounts`/`.exclude`)
— no change needed there. No cross-phase inconsistency found describing
`depth:` as a selection predicate, `tag:NAME=` as matching successfully,
or the empty-alternation family as still unresolved. `knowledge/
DECISIONS.md`/`DOMAIN_RULES.md` spot-checked internally consistent and
matching current source — no change needed (out of this agent's write
scope regardless). `ROADMAP.md`'s Stage C row contains a genuine
narrative duplication (two near-identical "Phase 9 implemented,
independent verification pending" paragraphs, the second stale/
superseded) — reported, not fixed here (`ROADMAP.md` is `roadmap-
context-curator`'s file, not `docs-maintainer`'s). `ledgerkit/`/`tests/`
untouched; full suite re-confirmed (935 tests, `OK (skipped=29)`).

---

### [Stage C closeout — drift-audit fixes] — 2026-09-27

**Human:** standing process — resolve genuine findings from the
Stage-C-wide `docs-reconstructor` audit and re-audit until clean.

**Claude:** fixed four findings, none affecting actual query-system
behaviour: `dev-docs/api-spec.md`'s `matches_posting` docstring context
still referenced the pre-Phase-5-rename `Depth` class instead of
`MaxAccountLevel`; `docs/python-api.md`'s `Query.depth` field
documentation claimed `accounts()` accepts depth rollup, but `Journal.
accounts()` takes no `query=` parameter at all (the module-level
`ledgerkit.reports.accounts()` does) — clarified; commit `301a42d`
(removing a stale duplicate ROADMAP paragraph) had no corresponding
`CHANGELOG.md` entry, contrary to the standing same-response rule —
added retroactively here; `CONTEXT.md` had not been updated across the
two most recent commits, wrongly implying the Stage-wide `docs-
maintainer` pass hadn't run yet — refreshed.

---

### [Stage C closeout — second drift-audit re-run, one finding fixed] — 2026-09-27

**Human:** standing process — re-audit until clean.

**Claude:** a second independent `docs-reconstructor` re-run (confirming
the four fixes below landed cleanly) found exactly one new, tiny
finding: `ledgerkit/query/eval.py`'s `matches_posting` docstring still
said "Acct/Depth are checked against the posting's own account" — the
one remaining stale reference to the pre-Phase-5-rename `Depth` class
anywhere in `ledgerkit/` (confirmed by grep; every other occurrence is
either hledger's own unrelated real `Depth` type, a numeric depth
value, or the documented historical rename note). Fixed —
comment-only, zero behaviour change.

# Changelog

All notable changes to ledgerkit are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).
See [dev-docs/versioning.md](dev-docs/versioning.md) for the versioning policy.

---

## [Unreleased]

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

### Confirmed and pinned the hledger reference binary — 2026-09-13

**Human:** directed running a command to verify hledger availability and
pin it as the target version.

**Claude:** confirmed a real `hledger` executable exists at
`/home/cormac/.local/bin/hledger` (`1.52.4-g33fa849e7-20260910,
linux-aarch64`, sha256 `c212db5f25daddf82f5767011ae73d3b7329c244db617e010fafe481cd07d747`),
building from the exact same commit (`33fa849e7ae841968bd21c427094c4fb4a4ec38d`,
tag `1.52.4`) as the local hledger source clone `hledger-researcher`
already used for the Stage C Phase 1 semantics brief. Recorded the pin in
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.1 and
corrected `dev-docs/compat-register/README.md`'s now-superseded "no
pinned binary" note. Recorded the decision in `knowledge/DECISIONS.md`.
This resolves a blocker noted repeatedly since Stage A closeout — it does
not itself run any differential verification, which remains separate,
not-yet-started work for `compat-differential-tester`.

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

### Added: standing commit/push pre-authorisation — 2026-09-13

**Human:** directed updating project instructions so commits happen at
logical intervals and pushes happen automatically at the end of each
successful phase, rather than asking each time.

**Claude:** added a "Commit & Push Cadence" section to `CLAUDE.md`:
commit at any coherent, self-contained, internally-consistent unit of
change; push once a phase is "successful" (exit criteria met, tests
passing, retro written) — same granularity `dev-docs/retros/` already
uses. Force-push, history rewrites, and branch deletion explicitly remain
outside this pre-authorisation. Updated `dev-docs/retros/README.md`'s
lifecycle diagram, `roadmap-context-curator.md` (commits/pushes as part of
its phase-end job), and `release-phase-auditor.md` (new DoD check #9:
committed and pushed). Recorded rationale in `knowledge/DECISIONS.md`.

---

### [Stage B — Core Model] — 2026-09-13

Full detail: [dev-docs/changelog/STAGE-B.md](dev-docs/changelog/STAGE-B.md)

**Summary:** Independently verified `ledgerkit-editor`'s actual `ledgerkit`
usage against its real source (Phase 1), correcting three inaccuracies in
an earlier README-inferred inventory — most notably, `EditorDocument` is
not actually used anywhere in its shipped code. Independently reviewed
whether `models.py` needs structural change to accommodate Stage E/F's
planned `Cost`/`Lot`/`PriceGraph`/valuation types (Phase 2): confirmed it
doesn't, except that account-type semantics must be added as a new field
rather than by retyping `Journal.declared_accounts`, which `ledgerkit-editor`
depends on. Both phases were read-only; no `ledgerkit/`/`tests/` code
changed. Stage B is `[DONE]`; Stage C (query system) is next.

---

### Added: per-phase retro report process — 2026-09-12

**Human:** asked whether ledgerkit had a retro convention similar to the
sibling `codecompass` project's, directed adopting one, then corrected the
initial scoping to fire per phase (matching the rest of the agent roster's
cadence) rather than only at Milestone/Stage completion.

**Claude:** added `dev-docs/retros/` (`README.md`, `TEMPLATE.md`), a new
"Retro Reports" section in `CLAUDE.md` (and the folder in its Folder
Structure block), and a step in `ROADMAP.md`'s "Deciding What Goes Into a
Milestone or Stage" process: a retro (`dev-docs/retros/<STAGE-OR-
MILESTONE>[-PHASE-K].md`) is authored at the end of every phase, the same
cadence `release-phase-auditor` and `docs-reconstructor` already use — not
only when a Milestone/Stage itself reaches `[DONE]`. Updated
`release-phase-auditor.md` to check a substantive per-phase retro exists as
part of its Definition-of-Done audit, and `roadmap-context-curator.md` to
author retros at phase-end and read them during its existing
learning-triage job. Recorded the decision and rationale in `knowledge/
DECISIONS.md`. Wrote `dev-docs/retros/STAGE-A.md` retroactively for the
already-`[DONE]` Stage A, since no retro existed for it yet. No
`ledgerkit/`/`tests/` code touched.

---

### [Stage A — Development Foundation] — 2026-09-12

Full detail: [dev-docs/changelog/STAGE-A.md](dev-docs/changelog/STAGE-A.md)

**Summary:** Relicensed ledgerkit from MIT to GPL-3.0-or-later to match
hledger's own licence (enabling directly-recorded use of hledger's
documentation, source, and test suite as compatibility evidence); redefined
the product goal from "a Python hledger clone" to "a deterministic,
Python-native accounting and query engine with a documented
hledger-compatible foundation"; migrated `ROADMAP.md` to the new Stage A–I
structure; built the seven-role agent roster (`.claude/agents/`); and built
the compatibility-register harness (`dev-docs/compat-register/`), including
25 first-wave entries covering directives, validation checks, and
genuinely-unsupported features, all `status: proposed` pending executable
verification. Stage A is `[DONE]`; Stage B (Core model) is next.

---

## [1.0.0] — 2026-06-07

First public release on PyPI.

### Added
- Parse `.journal` files compatible with hledger 1.52 format
- Core CLI commands: `balance`, `register`, `print`, `accounts`, `stats`, `check`
- Pure Python, no third-party runtime dependencies
- Python 3.8–3.12 support
- Comprehensive directive support: `include`, `account`, `commodity`, `payee`,
  `alias`, `P` (market prices), `Y` (default year), `D` (default commodity),
  `apply account` / `end apply account`
- Amount parsing: prefix/suffix commodity symbols, digit-group separators,
  decimal mark variants, quoted commodity names, E-notation, cost/lot
  annotations (`@ PRICE`, `{COST}`), sign-after-prefix-symbol (`$-300`)
- Secondary dates (`date2`) on transactions
- Full balance assertions (`=`, `==`, `=*`, `==*`) with `-I`/`--ignore-assertions` flag
- Strict mode (`-s`) checks that all accounts and commodities are declared
- Multi-commodity `balance()` with `tree=True` hierarchical rollup
- `parse_string_lenient` — never-raises parser for editor integrations
- `EditorDocument` — in-memory load/add/update/delete/save/reload for journal files
- `writer.py` — round-trip `transaction_to_text` and `journal_to_text`
- `SourceSpan` — byte-level source location for every transaction
- Commodity display style inference and `-c`/`--commodity-style` CLI flag
- Optional pandas export: `pip install ledgerkit[pandas]`
  - `Journal.to_dataframe()`, `BalanceResult.to_dataframe()`,
    `RegisterResult.to_dataframe()`, `AccountsResult.to_dataframe()`,
    `ReportSectionResult.to_dataframe()`
- `ReportSpec` / `ReportSection` / `balance_from_spec` for structured custom reports
- `ParseWarning` for non-fatal parser notices (periodic/auto-posting rule blocks)

---

## Pre-release development history

The entries below document the AI-assisted development workflow used to build
ledgerkit from the ground up across five milestones. They use a Human/Claude
attribution format and are preserved here for traceability. Detailed per-commit
records are in `dev-docs/changelog/`.

---

## [Unreleased]

### Publishing readiness for v0.2.0

**Human:** Prepare LedgerKit for its first PyPI release: packaging metadata, CI/CD workflows, documentation, and repository presentation. No parser or feature changes.

**Claude:** Updated `pyproject.toml` with `readme`, `license`, `keywords`, and `[project.urls]` fields; changed `description` to a clearer one-liner. Updated `README.md` Installation section with `pip install ledgerkit` primary command and development-install instructions; added CI badge. Created `.github/workflows/tests.yml` (matrix: Python 3.8–3.12, ubuntu-latest) and `.github/workflows/publish.yml` (OIDC Trusted Publishing; manual `workflow_dispatch` to Test PyPI; auto-publish to PyPI on `v*` tags). Created `dev-docs/pypi-trusted-publishing.md` with one-time setup instructions. Removed completed `pip install packaging & docs` backlog item from `ROADMAP.md`. Build verified: `python -m build` produces `ledgerkit-0.2.0-py3-none-any.whl` and `ledgerkit-0.2.0.tar.gz`; `twine check` passes both artifacts. 575 tests continue to pass.

---

## [0.2.0] — 2026-06-06

### [Milestone 4 — Comprehensive Format Compatibility]

Full detail: [dev-docs/changelog/MILESTONE-4.md](dev-docs/changelog/MILESTONE-4.md)

**Summary:** Added comprehensive hledger format compatibility. New model fields `Transaction.date2` (secondary date) and `Posting.cost_raw` (cost annotation text). New `ParseWarning` class for non-fatal parser notices. Amount parser now handles sign-after-prefix-symbol (`$-300`), cost/lot annotations (`@ $180`, `{$182}`), quoted commodity suffix (`3 "Chocolate Frogs"`), space digit-group separators (`1 000 000 JPY`), and E-notation (`1E3 EUR`). New directives: `Y` (default year), `D` (default commodity), `apply account`/`end apply account`. Periodic (`~`) and auto-posting (`=`) rule blocks skipped gracefully with `ParseWarning`. Zero hard errors on the comprehensive fixture; 575 tests pass.

---

## [0.1.0] — 2026-05-29

### Rename: PyLedger → ledgerkit

**Human:** Rename the project to `ledgerkit` for the PyPI release (`pyledger` was already taken).

**Claude:** Renamed source package directory `PyLedger/` → `ledgerkit/`. Updated all internal imports, `pyproject.toml` (name, scripts, packages.find), CLI prog name and error prefixes, all doc and knowledge files, and all test imports. 538 tests continue to pass.

### Python 3.8+ compatibility

**Human:** Lower the minimum Python requirement from 3.10 to 3.8.

**Claude:** Confirmed all source files already have `from __future__ import annotations` (PEP 563), making `str | None`/`list[str]` annotation syntax safe in Python 3.8. No code changes required. Updated `pyproject.toml` (`requires-python = ">=3.8"`, `target-version = ["py38"]`) and `README.md`.

### Commodity display style (`CommodityStyle`)

**Human:** Implement hledger commodity display style inference and CLI `-c` flag.

**Claude:** Created `ledgerkit/commodity_style.py` with `CommodityStyle` dataclass, `infer()` classmethod (detects prefix/suffix, spacing, decimal mark, group separator, precision from raw amount string), `format()` method (applies inferred style; prefix-symbol negatives as `£-5.00`, suffix-symbol negatives as `-5.00 EUR`), and `parse_style_override()` (parses `-c` CLI strings). Added `Amount.raw` field to models so the parser preserves the original amount text. Added `Journal._commodity_directive_raws` to capture style-declaring `commodity` directives. Added `Journal.commodity_styles` property that merges inferred and directive-based styles with directive priority. Updated `cli.py` to use styles in `balance`, `register`, and `print` output and accept `-c`/`--commodity-style` override flag. 29 new tests in `tests/test_commodity_style.py`.

### Pandas DataFrame export (optional)

**Human:** Add optional pandas export with `pip install ledgerkit[pandas]`.

**Claude:** Created `ledgerkit/_pandas_compat.py` (lazy import helper). Added `[project.optional-dependencies] pandas = ["pandas>=1.3"]` to `pyproject.toml`. Added `Journal.to_dataframe(query)` returning one row per posting. Added transparent result wrappers `BalanceResult`, `RegisterResult`, `AccountsResult` (with `__eq__` for existing-code compatibility) and `ReportSectionResult.to_dataframe()`. Updated `balance()`, `register()`, `accounts()` to return wrappers; updated `balance_from_spec()` to pass commodity styles. Exported new types from `ledgerkit/__init__.py`. 24 new tests in `tests/test_dataframe.py` (skipped gracefully if pandas absent).

### Version bump and classifiers

**Human:** Bump version to `0.1.0`, add PyPI classifiers.

**Claude:** Set `version = "0.1.0"` in `pyproject.toml` and `__version__` in `__init__.py`. Added `Topic :: Office/Business :: Financial :: Accounting` and Python 3.8–3.12 programming language classifiers. Added pandas ecosystem section to `README.md`.

---

## [Unreleased]

### Fix: column-0 `;`/`#` comment lines inside open transaction blocks

**Human:** Implement full hledger comment spec; column-0 `;` comments on their own line were not recognised correctly.

**Claude:** Identified that `_parse_string_impl` used `lstrip()` before the startswith check, making it unable to distinguish a column-0 top-level comment from an indented follow-on comment. Added `is_indented = line[0:1].isspace()` and gated comment capture on `if current_txn is not None and is_indented:`. Column-0 `#`/`;` lines are now always silently discarded (no capture, no `source_span` extension) regardless of whether a transaction block is open. Added `TestCommentSpec` with 25 new tests covering: standalone top-level comments (T-series), block comment edge cases (B-series), inline comment delimiters (I-series), follow-on indented comments (F-series), and source span behaviour (S-series). Updated `knowledge/DOMAIN_RULES.md`, `knowledge/EDGE_CASES.md` (EC-014), `dev-docs/hledger-compatibility.md` (corrected Comments table), and `docs/journal-format.md` (full Comments section rewrite). Total test count: 485.

---

### [Milestone 3 — Editor Readiness & Multi-Commodity] — 2026-05-09

Full detail: [dev-docs/changelog/MILESTONE-3.md](dev-docs/changelog/MILESTONE-3.md)

**Summary:** Added `parse_string_lenient` (never-raises parser for on-keystroke use), `CheckError.line_number`, multi-commodity `balance()` returning `dict[str, dict[str, Decimal]]` with `tree=True` mode, `resolve_elision()`, and `BalanceRow`. Added editor-readiness layer: `SourceSpan` dataclass, `Transaction.source_span/raw_text/inline_comment`, `Posting.inline_comment`, `source_file` param on `parse_string`, `check_transaction_autobalanced`, `writer.py` (`transaction_to_text`, `journal_to_text`), and `editor_model.py` (`EditorDocument`). 461 tests across nine test modules.

---

### [Milestone 2 — Core Reports] — 2026-05-03

Full detail: [dev-docs/changelog/MILESTONE-2.md](dev-docs/changelog/MILESTONE-2.md)

**Summary:** Implemented the `Query` filter dataclass, all four report functions (`balance`, `register`, `accounts`, `stats`), `ReportSpec`/`ReportSection`/`ReportSectionResult` foundation, hledger-aligned CLI output for `balance` and `register`, full balance assertions (`=`, `==`, `=*`, `==*`) with automatic enforcement and `-I` flag, a project knowledge base, and a trailing-decimal amount fix. 363 tests across seven test modules.

---

### [Milestone 1 — Journal Parser] — 2026-04-26

Full detail: [dev-docs/changelog/MILESTONE-1.md](dev-docs/changelog/MILESTONE-1.md)

**Summary:** Implemented the full journal parser (`parse_string`, `load_journal`, `include` directive, all key hledger directives), the checks module with strict mode, the `stats` report, all five CLI commands, and the complete test suite (265 tests across six subdirectory modules).

---

### [Milestone 0 — Project Foundation] — 2026-04-15

Full detail: [dev-docs/changelog/MILESTONE-0.md](dev-docs/changelog/MILESTONE-0.md)

**Summary:** Established the full project scaffold, core data models, initial
documentation suite, and developer tooling conventions that all subsequent
milestones build on.

---

## How to add a changelog entry (v1.0.0+)

Add a new entry under `## [Unreleased]` before cutting a release tag:

```markdown
## [X.Y.Z] — YYYY-MM-DD

### Added
- New features or capabilities

### Changed
- Changes to existing behaviour

### Fixed
- Bug fixes

### Removed
- Removed features (MAJOR version bump required)
```

Before tagging, move the entry out of `[Unreleased]` and set the release date.

---

## Archiving at milestone completion

When a major milestone is marked `[DONE]` in `ROADMAP.md`, all `[Unreleased]`
entries that belong to that milestone are archived as follows:

1. **Create an archive file** at `dev-docs/changelog/MILESTONE-N.md` (e.g.
   `dev-docs/changelog/MILESTONE-1.md`), using this structure:

```markdown
# Changelog — Milestone N: <Milestone Title>

Archived on: YYYY-MM-DD
GitHub commits: <hash> … <hash>

<paste all dev entries that belong to this milestone, oldest first>
```

2. **Replace** the individual dev entries in `CHANGELOG.md` with a single
   summary entry pointing to the archive:

```markdown
### [Milestone N — <Title>] — YYYY-MM-DD

Full detail: [dev-docs/changelog/MILESTONE-N.md](dev-docs/changelog/MILESTONE-N.md)

**Summary:** One or two sentences describing what the milestone delivered.
```

3. **Update `ROADMAP.md`** to mark the milestone `[DONE]` if not already done.

This keeps `CHANGELOG.md` scannable as the project grows while preserving the
full per-commit history in the archive files.

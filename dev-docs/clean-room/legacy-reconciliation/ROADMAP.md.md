<!--
producer: docs-maintainer (Legacy Reconciliation Mode)
document: ROADMAP.md
dispatch: plan29-phase5-roadmap-reconciliation
date: 2026-11-14
inputs:
  - /home/cormac/projects/ledgerkit/ROADMAP.md (real, pre-existing)
  - dev-docs/clean-room/drafts/current-shipped-state.md (Phase 4 factual artifact)
  - dev-docs/clean-room/snapshots/{current-state,compat-system}-v1.md(+.sidecar.json)
  - dev-docs/clean-room/assertions/{current-state,compat-system}/*.md
  - dev-docs/clean-room/implementation-reconstruction/{current-state,compat-system}.md
  - dev-docs/clean-room/implementation-comparison/{current-state,compat-system}.md
  - knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md
note: this document gets the ROADMAP.md-specific split (Plan 29 §6.1) —
  current-state-fact claims only get the five-way scheme; forward-looking
  project intent is reintroduced verbatim, unchecked, clearly labelled.
-->

# Legacy reconciliation: ROADMAP.md

## 0. Scoping pass — separating the two claim kinds

`ROADMAP.md` is almost entirely one of two kinds of content, plus a small
amount of pure process/procedure text that is neither:

1. **Forward-looking project intent** — Stage D–I `[PLANNED]` rows, the
   "Future / Backlog" table, Milestone 5's superseded original-scope
   bullets, and the deferred-work clauses embedded in the Stage A/C
   closeout cells (`PythonRegex`, `cur:`, smart/period dates, standalone
   `--depth`/`-N`, the Stage A CodeCompass-usage follow-up note, etc.).
   None of this was checked against clean-room evidence — nothing in the
   current tree can confirm or deny a future plan. All of it is
   reintroduced verbatim, unchanged.
2. **Current-state fact** — claims about what IS already built, working,
   or true right now. These get the five-way scheme below.

A third category — **historical point-in-time record** (e.g. "all 213
tests pass" as Milestone 0's exit criterion, "25 `status: proposed`
register entries" as Stage A's point-in-time deliverable count) — is
*not* a "right now" claim at all: it records what was true at the moment
that milestone/phase closed, not a claim about the present. The current
counts have grown since (935 tests; 49 register entries) without
contradicting these historical snapshots, the same way a company's
"Q1 revenue was $X" isn't falsified by Q4 revenue being higher. These are
left untouched: they are outside both this reconciliation's two-kind
split and outside the `current-state`/`compat-system` topics' evidence
scope (which covers CLI surface, test-suite scale, compat-register
census, and package metadata — not per-milestone historical narrative).
No contradiction was found between any of these historical records and
the clean-room evidence, so none required correction.

## 1. Current-state-fact claims found, and their classification

Restricting to claims that are phrased as, or functionally are, "this is
true of ledgerkit right now" (not "this was true when Milestone/Stage N
closed," and not forward intent):

| # | Claim (location) | Classification | Basis |
|---|---|---|---|
| 1 | "Sign after prefix symbol: `$-300`, `£-10` (currently only leading `-$300` works)" — Milestone 4 Scope, amount-parser fixes | **stale_or_contradicted** | Milestone 4 is `[DONE]`; its own scope item was to add sign-after-prefix support. The parenthetical was never updated from present tense describing the *pre-fix* limitation, so as written it falsely claims the limitation still exists. Directly re-verified against real, observed interpreter behaviour (outside the `current-state`/`compat-system` two-topic evidence scope, but within this role's normal "verified behaviour, not stated intent" mandate): `ledgerkit.parser.parse_string_lenient` on a transaction posting `assets:cash  $-300` and `assets:cash  £-10` returns zero `ParseError`s and `Amount(quantity=Decimal('-300'), commodity='$')` / `Amount(quantity=Decimal('-10'), commodity='£')` respectively. **Fixed** — rewritten to past tense in `ROADMAP.md`. |
| 2 | "Zero open `unexplained_mismatch` compat-register entries." — Stage C row closeout cell | **supported** | Traces to `compat-system@v1#compat-system-005` (classification: `aligned`). The register's `unexplained_mismatch`-resolution mechanism has been exercised exactly twice (`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`); both are currently resolved via a `resolves:`-carrying successor entry, with 0 presently open. Independently corroborated by the `compat-system` implementation-reconstruction report. No change needed. |
| 3 | `PythonRegex` "explicitly deferred (not implemented, not dropped)" — Stage C row closeout cell | **supported** (current-fact half only; the "not dropped" half is forward intent, left untouched) | Outside the `current-state`/`compat-system` evidence scope, so re-grounded directly instead: `ledgerkit/query/__init__.py` and `ledgerkit/query/regex.py` docstrings both currently state `PythonRegex` is not implemented; `dev-docs/hledger-compatibility.md`'s own compatibility table (`PythonRegex extension syntax` row) independently states "Not implemented... no escape hatch to full Python `re` yet"; `knowledge/DECISIONS.md`'s 2026-09-27 entry records the same deferral decision. Three independent current sources agree and none contradicts. No change needed. |
| 4 | Six-subcommand CLI surface implied across Milestones 1–4's individual command mentions (`balance`, `register`, `accounts`, `print`, `stats`, `check`) | **supported** | `current-state@v1#current-state-004` (classification: `aligned`): the installed CLI's `--help` currently lists exactly these six subcommands. No milestone claims a different or additional command exists. No change needed. |
| 5 | Milestone 1 exit criterion: `python -m ledgerkit print tests/fixtures/sample.journal` outputs all 5 transactions | **supported** (as still-true today, not only historically) | `current-state@v1#current-state-008` (classification: `aligned`): `stats` against the same fixture today reports `Txns : 5`. Consistent, not contradicted. No change needed. |
| 6 | Stage A row: "first wave of 25 `status: proposed` register entries... all shipped" | **historical point-in-time record, not a current-state claim** | Current count (per `compat-system@v1#compat-system-004`, `aligned`) is 26 `proposed` / 9 `self-verified` / 14 `verified` / 0 `final` out of 49 total — growth since Stage A closed, not a contradiction of what was true when Stage A closed. Left untouched. |
| 7 | Stage A row: CodeCompass-usage follow-up note ("expected to happen naturally once Stage B/C generate real tasks") | **rationale_requiring_verification**, left explicitly open | This is a forward expectation recorded inside a historical closeout note. Stage B and C are now both `[DONE]`, so the expectation's precondition has technically been met, but whether first real CodeCompass usage under `context-curator` actually *happened* is not addressed by either the `current-state` or `compat-system` topic, and no `knowledge/*.md` entry resolves it either (checked: no match for "context-curator" + "CodeCompass" usage-history claim in `knowledge/DECISIONS.md`). Left as an open question for the lead/`roadmap-context-curator` rather than resolved here — this is also squarely that agent's `ROADMAP.md`/`CONTEXT.md`-reconciliation territory per `knowledge/DECISIONS.md:231-232`, not a call this dispatch should make unilaterally. |

### Classification breakdown (current-state-fact claims only)

- **supported:** 4 (#2, #3, #4, #5)
- **stale_or_contradicted:** 1 (#1 — fixed)
- **rationale_requiring_verification:** 1 (#7 — left explicitly open)
- **useful_example:** 0
- **obsolete:** 0
- (plus 1 claim, #6, correctly identified as historical point-in-time record rather than a current-state claim at all, and therefore outside the five-way scheme by definition — left untouched)

No `conflicting`/`not_implemented`-equivalent finding beyond #1 was found. No claim required deletion (the "fix sometimes means delete" rule did not apply here — #1's paragraph still correctly describes a real, still-relevant scope item; only its stale parenthetical needed correcting, not removing the whole bullet).

## 2. Forward-looking project intent — reintroduced verbatim, unchecked

The following were identified as forward-looking intent and preserved
byte-for-byte in the reconciled `ROADMAP.md`, with no evidence-based
check applied (per this document's hard rule, nothing in the current
tree can confirm or deny a future plan):

1. **Milestone 5 — CLI Filter Flags `[SUPERSEDED]`** section in full,
   including its 5-bullet "Original scope (kept for reference, not
   built)" list.
2. **Future / Backlog table** — all 8 rows (Journal-comment `ReportSpec`
   parsing; Full `stats` query support; `EditorDocument` include-directive
   support; Account type inference; Periodic/auto postings; `stats` peak
   live memory; `stats` peak allocated memory; `stats` per-reporting-
   interval output).
3. **Stages A–I table, forward rows only** — Stage D, E, F, G, H, I, all
   6 still `[PLANNED]`, including their Focus/Plan-reference columns.
4. Deferred-work clauses embedded in the Stage C closeout cell describing
   what remains undone by design: `cur:`, hledger's smart/period date
   expressions, a standalone `--depth`/`-N` CLI flag, and `check`'s
   intentional non-wiring from `-q` ("remain confirmed, documented,
   non-blocking deferrals").
5. **"Deciding What Goes Into a Milestone or Stage"** process section in
   full (6-step procedure) — this is standing process, not a claim about
   current build state, and isn't evidence-checkable either way.

**Count: 16 discrete forward-looking items/sections** (1 superseded
milestone section + 8 backlog rows + 6 planned stage rows + 1 process
section), plus the embedded Stage C deferral clause (item 4 above,
counted as part of the Stage C row rather than standalone) — all
preserved untouched.

## 3. Result

**What changed:** One sentence, in Milestone 4's amount-parser scope
list — the stale present-tense parenthetical `(currently only leading
-$300 works)` describing a pre-fix limitation that Milestone 4 itself
closed, rewritten to `(previously only leading -$300 worked; both forms
parse correctly as of this milestone)`. Verified directly against
`ledgerkit.parser.parse_string_lenient` output (zero errors, correct
signed `Amount` for both `$-300` and `£-10`).

**What was deliberately left open:** Item #7 above (Stage A's
CodeCompass-usage-under-`context-curator` forward note) — whether this
has actually happened since Stage B/C closed is not resolvable from this
dispatch's permitted evidence (`current-state`/`compat-system` topics)
or from `knowledge/*.md`, and is also within `roadmap-context-curator`'s
own `ROADMAP.md` reconciliation remit, not this dispatch's to settle.

**What was deliberately kept, unchanged, as historical record (not
current-state fact):** all per-milestone test-count exit criteria (213,
363, 461, 485 — none contradicted by the current total of 935), Stage
A's "25 `status: proposed`" point-in-time deliverable count (now 26/9/14/0
out of 49, consistent with growth not contradiction), and every other
Milestone 0–4 feature checkmark — none of which falls within the
`current-state`/`compat-system` topics' evidence scope and none of which
is contradicted by any evidence found.

**What was reintroduced verbatim as forward-looking intent:** all 16
items/sections listed in §2, byte-for-byte, with no correctness check
applied.

# Changelog

All notable changes to ledgerkit are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).
See [dev-docs/versioning.md](dev-docs/versioning.md) for the versioning policy.

---

## [Unreleased]

### [Plan 29 PR — fix overclaiming round-trip guarantee found by independent Codex review] — 2026-11-26

**Human:** directed an independent orchestrator review of the clean-room
documentation PR, including requesting independent Codex review.

**Claude:** Codex flagged `docs/python-api.md:537`: the documented
`transaction_to_text` round-trip guarantee was false for transactions
with a secondary date, a cost annotation, or a balance assertion.
Reproduced empirically: none of `Transaction.date2`,
`Posting.cost_raw`, or `Posting.balance_assertion` are serialised at
all, so they are silently absent after round-tripping (tags survive
only because they live in the preserved inline-comment text, confirmed
separately). Corrected both `docs/python-api.md` and
`ledgerkit/writer.py::transaction_to_text`'s own docstring to name the
three exclusions explicitly instead of implying full fidelity. Added
`knowledge/EDGE_CASES.md` EC-024 and extended `ROADMAP.md`'s "Plan 29
bug-fix backlog" row (now 8 items). Full suite re-run after the change:
935 passed.

### [CodeCompass upgrade + clean-room docs — Phase 6, independent final validation + initiative closeout] — 2026-11-14

Full detail: [dev-docs/retros/_audit-codecompass-upgrade-cleanroom-docs.md](dev-docs/retros/_audit-codecompass-upgrade-cleanroom-docs.md), [dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-CLOSEOUT.md](dev-docs/retros/CODECOMPASS-UPGRADE-CLEANROOM-DOCS-CLOSEOUT.md)

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** dispatched an independent `release-phase-auditor` to run
Plan 29's own Phase 6 audit (§7.1's 8 criteria, each reported separately
— never collapsing isolation-tier/workflow-fidelity/boundary-compliance
into one line). Verdict: **PASS WITH NON-BLOCKING OBSERVATIONS**, every
claim independently re-verified (tests re-run: 935 passed; all 10
snapshots re-checked via `check_snapshot.py`: all pass; 5
independently-picked provenance sentences re-traced; all 3 Phase 3
contamination events re-confirmed to have left no surviving output).
Two genuine findings not in any prior retro: `ROADMAP.md` had no
"Tooling & Process Initiatives" section (added, in-progress state, per
plan §8 item 1); CodeCompass's live checkout had drifted past its Phase
1 pin (confirmed harmless — zero `codecompass` commands ran under this
initiative after Phase 1 — flagged for re-pinning before any future
use). Ran the deferred learning-triage pass
(`roadmap-context-curator`): all 12 accumulated findings from Phases 3
and 5 triaged into durable records — 6 new `knowledge/EDGE_CASES.md`
entries (EC-018–EC-023) for the real production bugs Phase 3 found, 1
corrected in place (EC-006, dated addendum, original preserved), 1
`knowledge/DECISIONS.md` addendum correcting a false entry, 1
`knowledge/DOMAIN_RULES.md` correction (an unprompted 13th finding
caught proactively), and 2 new `ROADMAP.md` backlog rows — nothing left
untriaged. Wrote the initiative's closeout retro, synthesising all six
phases. This closes out Plan 29's entire six-phase initiative; per the
standing "never infer completion" rule, `ROADMAP.md`'s new row is not
flipped to `[DONE]` here — that requires the user's own explicit
confirmation, separately. 935 tests still pass; no `ledgerkit/` source
changed.

### [CodeCompass upgrade + clean-room docs — Phase 5, dev-docs/api-spec.md change confirmed and applied] — 2026-11-14

**Human:** confirmed applying all 3 of the `docs-maintainer` dispatch's
proposed, additive disclosures to the protected `dev-docs/api-spec.md`,
per CLAUDE.md's Unauthorised Change Rule's confirm-first requirement.

**Claude:** applied the reconciliation dispatch's proposed revision
(`dev-docs/clean-room/legacy-reconciliation/api-spec.md.proposed-
revision`) to the live `dev-docs/api-spec.md`, after fixing one
unrelated mechanical slip the dispatch had introduced (a stray one-space
misalignment in an unrelated `Commands:` summary block, unrelated to
either intended edit) so the applied diff is exactly the three additive
disclosures: `load_journal`'s two confirmed loader gaps
(`loader@v1#loader-002/003/007`), `run_checks`'s two confirmed skip/
names/strict interaction asymmetries (`checks@v1#checks-008`), and
`run_basic_checks`'s one-line note that `skip` only applies to its own
basic-tier call. No signature changed; nothing removed. 935 tests still
pass.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: ROADMAP.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `ROADMAP.md`, splitting current-state fact from
forward-looking project intent per §6.1's explicit rule for this
document.

**Claude:** classified only `ROADMAP.md`'s current-state-fact claims
against the five-way scheme (`dev-docs/clean-room/legacy-reconciliation/
ROADMAP.md.md`): 4 supported, 1 fixed (`stale_or_contradicted` — the
Milestone 4 scope line "(currently only leading `-$300` works)" was
stale since both sign forms parse correctly today, confirmed by direct
execution and rewritten to past tense), 1 left explicitly open
(whether Stage A's "first real CodeCompass usage" follow-up has
occurred — deferred to `roadmap-context-curator`'s own territory rather
than decided here). All 16 forward-looking intent items/sections
(Milestone 5's `[SUPERSEDED]` block, the Future/Backlog table, the
still-`[PLANNED]` Stage D-I rows) were left verbatim and untouched, per
the hard rule that nothing in the current tree can confirm or deny a
future plan. Only one line of `ROADMAP.md` changed.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: README.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `README.md`, now that the Phase 4 clean-room
draft and the real legacy document can both be read together.

**Claude:** classified 32 distinct legacy claims against the five-way
scheme (`dev-docs/clean-room/legacy-reconciliation/README.md.md`): 25
supported, 2 fixed (`stale_or_contradicted` — an incomplete directive
list, a command-order mismatch against the canonical `COMMANDS` tuple),
2 `rationale_requiring_verification` resolved by tracing to the project's
own planning docs (not knowledge/*.md, which had no relevant entry), 3
`useful_example` re-grounded, 0 obsolete. Went beyond trusting draft/
legacy agreement for every out-of-scope topic the legacy README also
touched, via direct independent re-verification this session (a live
935-test run, live bug reproductions, `git show v1.0.0:LICENSE`).
Merged in 7 wholly new sections from the Phase 4 draft (Status,
CLI interface, Reports, Journal text serialization, Journal format
support, an expanded Hledger Compatibility section, Known current
limitations), deliberately not duplicating `docs/usage.md`'s or
`docs/journal-format.md`'s own detailed reference material. 4 explicit
open questions preserved rather than silently decided.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: docs/python-api.md + dev-docs/api-spec.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode (§6.3/§6.4) for `docs/python-api.md` and
`dev-docs/api-spec.md` together, cross-checking the two against each
other and against the Phase 3 evidence for all 10 clean-room topics, with
full access to the already-committed Phase 4 clean-room draft
(`dev-docs/clean-room/drafts/python-api.md.clean-room-draft`).

**Claude:** classified every claim in `docs/python-api.md` against the
five-way scheme (`dev-docs/clean-room/legacy-reconciliation/
python-api-and-api-spec.md`) and rewrote it live, preserving the
document's existing structure/examples and the clean-room draft's inline
citations. Closed a large set of coverage gaps that had zero mention in
the prior doc despite being documented, re-exported public API in
`dev-docs/api-spec.md`: `ledgerkit.checks` (new "Validating Transactions"
section, including the `run_checks` skip/names/strict asymmetry disclosed
by `checks@v1#checks-008`), `ledgerkit.writer` (new "Serializing
Transactions" section), `ledgerkit.EditorDocument` (new section, with the
known-adoption-gap caveat), `resolve_elision`, the Stage C
Phase 4/Editor-Readiness `Posting`/`Transaction` fields
(`tags`/`date_override`/`source_span`/`raw_text`/`inline_comment`), a new
"Working with Tags" section, `BalanceRow`/`RegisterRow`/`SourceSpan`, the
Stage C Phase 9 empty-alternation regex-rejection note (already in
`api-spec.md` but missing here), and several previously-undocumented known
limitations (lenient-parsing non-exhaustiveness, two confirmed
`load_journal` gaps, `ReportSectionResult.to_dataframe()`'s
single-commodity quirk). `dev-docs/api-spec.md` was **not** edited live
(Unauthorised Change Rule) — two confirmed divergences from evidence
(`run_checks`'s undisclosed skip/strict asymmetry per `checks-008`;
`load_journal`'s non-exhaustive `Raises` section per `loader-002/003/007`)
were written as a full proposed revision to
`dev-docs/clean-room/legacy-reconciliation/api-spec.md.proposed-revision`
for the user to confirm. Ran the §6.4 coverage check: 67 of 72 public
symbols `api-spec.md` lists have a corresponding Phase 3 assertion; 5 gaps
recorded (`ReportSection`, `ReportSpec`, `load_journal_stdin`,
`run_strict_checks`, `Journal.to_dataframe`/report-wrapper
`to_dataframe()`s).

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: dev-docs/architecture.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `dev-docs/architecture.md`, with full access to
both the already-committed Phase 4 clean-room draft
(`dev-docs/clean-room/drafts/architecture.md.clean-room-draft`) and the
real legacy document.

**Claude:** classified every claim in the real `dev-docs/architecture.md`
against the five-way scheme
(`dev-docs/clean-room/legacy-reconciliation/architecture.md.md`), tracing
each `supported` claim to a specific Phase 3 assertion id or a direct
`ledgerkit/*.py:line`/test citation rather than to draft/legacy agreement
alone. Rebuilt the document on the clean-room draft's structure (far more
complete and precisely cited than the legacy version) and merged in
everything from the legacy doc still independently true: the Error
Handling Strategy table (re-grounded, and corrected — `reports.py` no
longer raises a bare `ValueError` itself; invalid-query errors now surface
as `QueryParseError` from `query/compat.py`'s `_validated`), the Design
Principles section (import-layering bullet rewritten to point at the
per-module Dependencies subsections rather than a now-stale three-item
list; "no circular imports" and "no global mutable state" re-verified
directly; the `compare=` dataclass-field convention kept, re-grounded
against `models.py:29,79,84,103-105`), and the "one canonical evaluation
path, plus exactly one named exception" `reports.py`/`query/compat.py`
unification detail (not in the draft at all; re-grounded directly against
`reports.py:32,213-239,621-667`, `models.py:479-493`, and
`tests/test_reports.py:139-160`'s zero-remaining-callers enforcement
test). Found and fixed two materially stale sections rather than
restoring them as written: the legacy `parser.py` section's claim that
`parse_string` is "the sole public function" (false — `parse_string_lenient`
and `resolve_elision` are both public and exported), and the legacy
`checks.py` section's check-function inventory (missing `check_parseable`
and `check_assertions`, and the three fixed `*_CHECK_NAMES` tiers
entirely). Dropped the legacy doc's "Stage C Phase N" historical
narration throughout (per `11-documentation-lifecycle.md` §11.2, decision
history belongs in `knowledge/DECISIONS.md`/`dev-docs/planning/`, not
restated as narrative in a current-truth doc) in favour of the draft's
atemporal structural description, adding "see also" pointers to the
relevant design docs for readers wanting the rationale/history. Preserved
every inline `<topic>@v1#<id>` citation carried over from the draft.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: dev-docs/hledger-compatibility.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode, specifically §6.3, for `dev-docs/hledger-
compatibility.md` — a reconciliation-only document with no parallel
Phase 4 clean-room draft.

**Claude:** classified every claim in the real `dev-docs/hledger-
compatibility.md` against the five-way scheme (`dev-docs/clean-room/
legacy-reconciliation/hledger-compatibility.md.md`), re-verifying each
against the compat-register's own `evidence:`/`reason:` fields (not just
`kind`/`status`), the `compat-system`/`journal-parsing`/
`commodity-styling`/`query-engine`/`tags`/`loader`/`checks` topics' Phase
3 assertion/reconstruction/comparison artefacts, and direct live
execution against this checkout where neither settled a claim. Preserved
the document's existing structure throughout (reconciliation, not a
redraft). Fixed two claims found false by direct execution: the
"Balance assignments" paragraph (previously claimed `= EXPECTED` with no
explicit posting amount parses cleanly with the posting amount stored as
`None` — actually unimplemented, raising a clean `ParseError` for
prefix-commodity amounts and silently producing a wrong, uncaught
`Amount` for suffix-commodity amounts under `decimal-mark ,` mode; this
also meant `knowledge/DECISIONS.md`'s 2026-05-03 entry's own rationale no
longer matches the as-built code — flagged to the lead, not edited,
since `knowledge/` is outside this role's write boundary), and the
`include` directive's "Circular includes raise `ParseError`" claim
(true for genuine multi-file cycles, but a literal self-include instead
raises a misleading `FileNotFoundError` naming a path that demonstrably
exists). Also documented a newly-confirmed, previously-undocumented
`IndexError` crash when an include target's resolved path has a
glob-metacharacter-containing ancestor directory. Flagged two items for a
future `compat-differential-tester` re-check rather than guessing an
answer: `LK-COMPAT-PARSER-TAG-001`/`LK-COMPAT-PARSER-TAG-SCOPE-001`'s
broken `TestParseTags` test citation (confirmed non-existent in
`tests/test_tags.py`), and `LK-COMPAT-INCLUDE-001` (`status: proposed`,
`manual`-only evidence) needing re-verification against real hledger for
the two loader defects above. Everything else in the document (~38
claim-groups across every section) was re-traced to specific Phase 3
evidence and confirmed `supported` with no change. **Lead follow-up,
same phase:** the document's own opening paragraph (line 11) still said
"each entry there is `status: proposed`" as a blanket present-tense
claim — missed by the dispatch above despite its own re-verification
pass — stale against the register's actual, repeatedly-confirmed
distribution (26 proposed / 9 self-verified / 14 verified / 0 final,
`compat-system@v1#compat-system-004`); fixed directly.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: docs/usage.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `docs/usage.md`, now that the Phase 4 clean-room
draft and the real legacy document can both be read together.

**Claude:** classified every claim in the legacy `docs/usage.md` against
the five-way scheme (`dev-docs/clean-room/legacy-reconciliation/
usage.md.md`), tracing each candidate `supported` claim to a specific
Phase 3 assertion from the `reports-cli`, `checks`, and `current-state`
topics rather than accepting draft/legacy agreement at face value. Found
and fixed eight `stale_or_contradicted` gaps: the default check tier was
documented as just `autobalanced` when it is actually `parseable` +
`autobalanced` + `assertions`, and the check-names table omitted
`assertions` entirely; the "Specifying the journal file" section never
stated `check`'s own exception (a bare positional names a check, never a
journal, for that command only); `balance`/`register`/`accounts`/`print`/
`stats` were one-line stubs missing verified, user-relevant behaviour
(ANSI-red negatives and the unconditional depth-0 `"..."` row for
`balance`; fixed-width columns, date/description blanking, and the
never-regrouped running-balance invariant for `register`; the
genuinely-empty-output-on-no-match behaviour for `accounts`; the exact
output format and — materially — that `print` drops inline `;` comments
entirely, unlike ledgerkit's own round-trip serialiser; `-1`/`-v` modes
and the depth-*exclusion* quirk unique to `stats`); five real global
flags (`--version`, `-v`, `-1`, `-o`, `-I`) were never documented anywhere
in the file; no note existed that subcommand-level `--help` doesn't
exist; and the Python-library snippet's `balance()` type comment
(`dict[str, Decimal]`) was wrong — the actual shape is a nested
account→commodity→Decimal mapping, matching `docs/python-api.md`'s own
`BalanceResult` description once cross-checked. Added a new "Exit codes"
section and a "stats" sample-output block grounded directly in a
reproduced `current-state@v1#current-state-008` live run. Left the
`-q`/`--query` deep-dive and `-c`/`--commodity-style` sections unchanged —
outside this dispatch's permitted evidence (`query-engine`/`tags`/
`commodity-styling` topics) and not contradicted by anything given here.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: docs/journal-format.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `docs/journal-format.md`, now that the Phase 4
clean-room draft and the real legacy document can both be read together.

**Claude:** classified every claim in the legacy `docs/journal-format.md`
against the five-way scheme (`dev-docs/clean-room/legacy-reconciliation/
journal-format.md.md`), tracing each candidate `supported` claim to a
specific Phase 3 assertion from the `journal-parsing`, `commodity-styling`,
`tags`, `loader`, and `compat-system` topics rather than accepting
draft/legacy agreement at face value. Found and fixed four
`stale_or_contradicted` legacy claims that were simply wrong — secondary
dates, balance assertions, cost/lot annotations, and decimal-comma style
were all listed as "Unsupported in v1" despite being implemented and
tested — and found that the legacy doc never documented the `account`,
`commodity`, `payee`, `tag`, `decimal-mark`, `Y`, `D`, or `apply account`
directives at all, added as a new Directives section. Preserved every one
of the clean-room draft's confirmed, unflattering findings with their
citations intact rather than dropping them for not matching the legacy
doc's narrower original scope: `parse_string_lenient`'s broken never-raise
guarantee (a malformed `commodity` directive, and separately an
invalid-backreference `alias` applied later, both escape it uncaught), a
directive appearing inside a still-open transaction silently dropping
that transaction's remaining postings, balance-assignment elision's two
different failure modes (a clean error for a prefix-commodity amount, but
silent corruption for a suffix-commodity amount under comma-decimal
mode), three distinct loader glob-escaping gaps (a bracketed containing-
directory name causing an uncaught `IndexError`, a bracketed filename
causing a misleading `ParseError`, and a literal self-include causing a
misleading `FileNotFoundError`), diamond-include silent duplication, and
a commodity-style-inference bug that can silently produce a nonsensical
precision value. Flagged, but did not fix (outside this role's write
boundary), a direct conflict between `knowledge/EDGE_CASES.md`'s EC-006
and the current, test-confirmed glob-no-match behaviour — EC-006 appears
to predate a later change and was never updated.

### [CodeCompass upgrade + clean-room docs — Phase 5, legacy reconciliation: docs/getting-started.md] — 2026-11-14

**Human:** directed the `docs-maintainer` agent to run Plan 29 §6's Legacy
Reconciliation Mode for `docs/getting-started.md`, now that the Phase 4
clean-room draft and the real legacy document can both be read together.

**Claude:** classified every claim in the legacy `docs/getting-started.md`
against the five-way scheme (`dev-docs/clean-room/legacy-reconciliation/
getting-started.md.md`), re-tracing each candidate `supported` claim to a
specific Phase 3 assertion's own directly-checked evidence rather than
accepting draft/legacy agreement at face value. Published the reconciled
`docs/getting-started.md`: the Phase 4 draft as the base, with every one
of its own inline citations preserved, plus a new Installation section
(pip install + the `pandas` extra + the `pyproject.toml` console-script
entry, citing `CHANGELOG.md`'s `1.0.0` PyPI-release record and
`current-state-001`'s pre-release-`1.0.0.dev1` caveat side by side,
rather than picking one and dropping the other), a restored plain-English
elision gloss, and a new "What's next" cross-link section to
`usage.md`/`journal-format.md`/`python-api.md`. Deliberately did not
restore the legacy's own sample journal (redundant with the draft's
already-cited example) or `print`-as-first-command (superseded by the
draft's better-evidenced `stats` recommendation). Left one explicit open
question rather than silently resolving it: whether a live `pip install
ledgerkit` today actually retrieves code matching this exact checkout —
no Phase 3 assertion performed a live PyPI check.

### [CodeCompass upgrade + clean-room docs — Phase 4, clean-room documentation drafting] — 2026-11-14

Full detail: [dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-4.md](dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-4.md)

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** drafted the six clean-room-redraft documents (`README.md`,
`dev-docs/architecture.md`, `docs/getting-started.md`, `docs/usage.md`,
`docs/journal-format.md`, `docs/python-api.md`) plus the current-
shipped-state factual artifact, via 7 fresh isolated dispatches, each
scoped to only the topics its document naturally needs (3-10 of the 10
Phase 3 topics), never the real document it replaces, this plan's own
prose, or any legacy documentation. Every factual sentence traces to a
Phase 3 snapshot citation; confidence language calibrated to each
cited assertion's comparison classification throughout. Confirmed,
unflattering current-behaviour facts Phase 3 found (the broken never-
raise guarantee, silent data-loss and corruption cases, `check`'s
silent success, `print` dropping comments) were included where a
document's own scope called for them, per explicit instruction, rather
than quietly omitted. Caught and fixed a precondition failure before
dispatching: the editor-surface snapshot's external-repository clone
under `/tmp` had been cleaned up during the six-week gap since Phase 3
closed — re-cloned from the recorded origin URL at the exact pinned SHA,
exactly the recovery path `PINNED-REVISIONS.md` had anticipated. Wrote
the phase's retro. Drafts live under `dev-docs/clean-room/drafts/`, not
overwriting any real document — this commit is Plan 29's hard boundary
between drafting and Phase 5's legacy reconciliation. 935 tests still
pass; no `ledgerkit/` source changed.

---

### [CodeCompass upgrade + clean-room docs — Phase 3, COMPARISON + phase closeout] — 2026-11-14

Full detail: [dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-3.md](dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-3.md)

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** completed Phase 3's full 9-step per-topic pipeline (Plan 29
§4.2) by dispatching `domain-skeptic` COMPARISON mode for all 10 topics,
classifying alignment between each topic's frozen snapshot and its
independent implementation-reconstruction report. Final tally across
all 10 topics: **97 aligned, 9 partial, 5 insufficiently_verified, 0
conflicting, 0 not_implemented** — zero contradictions found anywhere
between two independently-produced, model-blind artefacts, which is
itself meaningful corroboration that neither step fabricated or guessed
at scale. One dispatch (reports-cli) had its own `Write` tool call
hard-blocked by the harness; resumed the same agent to recover the full
verbatim report text and persisted it directly as the lead, rather than
losing the work or treating the block as something to route around.
This closes out Phase 3 entirely: 102 assertions, 10 snapshots, 10
implementation-reconstruction reports, and 10 comparison reports, all
produced with zero legacy documentation consulted at any step. Wrote
the phase's closeout retro. 935 tests still pass; no `ledgerkit/` source
changed (8 real production bugs/defects found across this phase remain
recorded, not fixed — out of scope for a documentation phase).

---

### [CodeCompass upgrade + clean-room docs — Phase 3, implementation reconstruction] — 2026-10-03

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** dispatched a fresh, model-blind `implementation-reconstructor`
for all 10 bounded topics (Plan 29 §4.2 step 5) — each given only its
own primary evidence paths (source, tests, live CLI/Python execution),
never the assertions, snapshots, or any legacy documentation produced so
far. Every dispatch's transcript was inspected immediately for boundary
compliance; all 10 came back compliant (one self-disclosed a brief,
unused peek, logged as a note per the standard established in Phase 3's
review step). Two dispatches (`journal-parsing`, `commodity-styling`)
were interrupted mid-task by the account's weekly rate limit on a
trailing, inessential verification step — in both cases the report
itself had already been fully written to disk beforehand, recovered by
reading the file directly rather than redispatching from scratch.
Independent reconstruction surfaced **three more real production bugs**
beyond the two already found in Phase 3's review step, all recorded, none
fixed (out of scope for this phase): an `alias` directive with an
out-of-range backreference raises an uncaught `re.PatternError` from
both parse functions; a non-indented `account`/`commodity`/`payee`/`tag`
directive encountered mid-open-transaction-block silently discards every
subsequent posting line with no error; and hledger's balance-assignment
elision syntax silently corrupts data for suffix-commodity/comma-decimal
input (absorbs the literal `=` as a currency symbol, drops the
assertion, raises nothing). Also found a confirmed dead/confused code
fragment in `ReportSectionResult.to_dataframe()` and a rounds-vs-
truncates inconsistency in `CommodityStyle.format()` depending on
whether `precision` is zero. The `editor-surface` reconstruction's most
decision-relevant finding: an unanchored, twice-verified whole-clone
search found **zero real usage** of `EditorDocument` by the external
`ledgerkit-editor` consumer it was built for — the editor's actual
pipeline is an independently-built implementation on lower-level
functions instead. 935 tests still pass; no `ledgerkit/` source changed
(all findings flagged for a future tracked-fix task, not addressed
here). Full cumulative bug tally recorded in
`dev-docs/clean-room/compliance-log.md`.

---

### [CodeCompass upgrade + clean-room docs — Phase 3, assertion research/review/freeze] — 2026-10-03

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** executed the per-topic clean-room assertion pipeline (Plan 29
§4.2) for all 10 bounded topics (journal-parsing, commodity-styling,
query-engine, tags, reports-cli, checks, loader, editor-surface,
compat-system, current-state) — 102 assertion files total. Each topic's
assertion-research ran as a fresh, isolated dispatch given only its
bounded evidence paths, never this plan's prose or any legacy
documentation; each dispatch's transcript was inspected immediately
against §4.2a's boundary-compliance gate. Three contamination events
(compat-system attempts 1–2: narrative/out-of-scope-source reads) were
discarded and rerun from a fresh context per the plan's own mechanical
rule, not edited in place. Every topic then went through an independent
`domain-skeptic` REVIEW pass, which found and fixed genuine defects by
direct execution rather than rubber-stamping — including a backwards
specificity rule in query-engine-014 that self-contradicted its own next
clause, a false "necessarily nets to zero" claim in reports-cli-005, and
an anchored-grep false negative in editor-surface-008 that missed 8 of 9
real runtime import sites. Two real **production bugs** were surfaced as
a byproduct (recorded, not fixed — out of scope for this phase):
`parse_string_lenient`'s documented "never raises" guarantee is false for
a malformed `commodity` directive (parser.py:1324-1334 lacks the
try/except guard every other directive handler has), and a containing
directory named with a glob metacharacter (e.g. `inc[1]`) causes the
loader's glob-vs-literal classification to diverge, silently misrouting
a plain include into an uncaught `IndexError`. All 10 topics were then
mechanically frozen into `dev-docs/clean-room/snapshots/` and run through
`check_snapshot.py` as a hard gate — which caught three real citation
defects before any snapshot was accepted: two off-by-one whole-file line
citations (ledgerkit/cli.py and ledgerkit/query/ast.py each cited one
line past their real end) and a literal, unresolvable glob
(`dev-docs/compat-register/*.yaml`) used as an Evidence-paths entry
instead of enumerated files. Extended `check_snapshot.py` itself to
resolve absolute-path citations (the editor-surface topic's evidence
lives in an external `ledgerkit-editor` research clone, a different git
repository entirely) against a registered external repository's own
pinned revision via a new `external_repositories` sidecar field, rather
than silently skipping them or wrongly resolving them against
Ledgerkit's own tree — added two new self-test cases (pass and fail) to
prove this resolves and fails closed correctly; pin recorded in
`dev-docs/clean-room/PINNED-REVISIONS.md`. All 102 assertions across all
10 topics now pass the checker. 935 tests still pass; no `ledgerkit/`
source changed (the two production bugs found are flagged for a future
tracked fix, not addressed here).

---

### [CodeCompass upgrade + clean-room docs — Phase 2] — Isolation workflow adoption + snapshot checker — 2026-10-02

Full detail: [dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md](dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-2.md)

**Human:** directed continuing Plan 29's implementation straight through
to closeout.

**Claude:** copied the pinned `codecompass-template`'s
`optional-clean-room-workflow/` directly into `dev-docs/clean-room/`
(seven `TEMPLATE.md` skeletons, two guides, the worked example, its own
README — kept verbatim except one stale cross-reference, corrected to
point at Ledgerkit's own long-existing equivalents). Built
`dev-docs/clean-room/check_snapshot.py`, a small stdlib-only checker
implementing all six fail-closed conditions from Plan 29 §3.7 — missing/
duplicate assertion ids, hash mismatch, missing/nonexistent repository
revision, dangling assertion references, and (the amendment's own
strengthening) cited evidence resolved against the *frozen git
revision's own tree*, never today's working tree. Proved it genuinely
fails closed, not just described it: a built-in `--self-test` runs a
disposable git fixture through a passing case and six distinct failure
modes, including a file added only in a *later* commit than the frozen
revision, and a line range that only resolves against today's longer
version of a file — all seven behaved exactly as expected. Ran the real
isolation preflight probe (one `general-purpose` dispatch) and recorded
the honest result in `dev-docs/clean-room/isolation-preflight.md`:
**tier `best-effort`** — filesystem, command execution, and network were
all directly demonstrated open (a real `Read` of `README.md` succeeded;
a real `curl`/`WebFetch` reached the project's actual public GitHub
mirror and returned real content); same host and working directory as
the main session, confirmed by direct `pwd`/`hostname` comparison, not
assumed. One discrepancy disclosed rather than smoothed over: the probe
ran as `general-purpose` with no reachable `Grep` tool, since
`implementation-reconstructor`/`domain-skeptic` weren't yet dispatchable
`subagent_type` values at probe time (becoming so moments later) — the
"search" route wasn't directly tested, though `Bash` (already proven
open) makes this immaterial to the overall tier. 935 tests still pass;
no `ledgerkit/`/`tests/` code touched.

---

### [CodeCompass upgrade + clean-room docs — Phase 1] — CodeCompass reconciliation & enforced revision pinning — 2026-10-02

Full detail: [dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md](dev-docs/retros/CODECOMPASS-UPGRADE-PHASE-1.md)

**Human:** directed implementing the amended Plan 29 straight through to
closeout, starting with Phase 1.

**Claude:** pinned `codecompass`
(`96a1e4d53acf4acc6659dc233b1ca2eafae3d41a`) and a freshly-cloned
`codecompass-template` (`68bae8ec739aea413bbedac9f19078f6ab995aca`) in
`dev-docs/clean-room/PINNED-REVISIONS.md`, and made the pin mechanically
enforced via a new guard script
(`dev-docs/clean-room/check_codecompass_pin.sh`, tested against both a
matching and a deliberately corrupted pin to confirm it genuinely fails
closed) rather than a dedicated worktree — the global `pipx install -e`
is shared with CodeCompass's own active development, so repointing it
would change state outside this repository's own blast radius for no
extra isolation the guard doesn't already provide. Re-ran `codecompass
sync`/`index`/`check` against the pin (declining Phase B's AI-enrichment
prompt — no `ANTHROPIC_API_KEY` is configured, and Ledgerkit has zero
tracked vendors to enrich); confirmed via `query source-symbol` that 107
of 322 indexed symbols now come from Stage C's `ledgerkit/query/*`/
`tags.py`, proving the re-sync picked up real new code, not just that
the command exited cleanly. Diffed and hand-merged all four existing
CodeCompass-derived agent briefs against the pinned upstream revision
(adopting, among other things, `release-phase-auditor`'s
single-question-per-verdict rule — directly load-bearing for this
initiative's own Phase 6 isolation reporting); added
`implementation-reconstructor.md`/`domain-skeptic.md`, adapted to Plan
29's own lighter assertion/snapshot scheme rather than CodeCompass's
heavier internal Claim/Evidence apparatus. Corrected `CLAUDE.md`'s
folder-structure diagram, which had drifted well beyond what Plan 29's
original finding named (missing `.claude/`, `validation/`, most of
`dev-docs/`'s real subdirectories, and several root files, on top of the
already-known missing `ledgerkit/query/` subpackage). 935 tests still
pass; no `ledgerkit/`/`tests/` code touched.

---

### CodeCompass upgrade + clean-room documentation reconstruction — plan amended again, approved to implement — 2026-10-02

Full detail: [dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md](dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md)

**Human:** a second review found 8 further corrections needed before the
plan was genuinely implementation-ready, and directed amending in place
then proceeding straight through all six phases to closeout, without a
further planning round-trip.

**Claude:** applied all 8 corrections to
`29-codecompass-upgrade-and-clean-room-docs.md` (same file, same
six-phase structure): assertion research is now a structurally separate
fresh `Agent` dispatch, never a `fork`, receiving only the bounded topic,
permitted evidence paths, and output format — never legacy docs, this
plan's own prose, pre-existing assertions/snapshots, reconstruction
output, or prior summaries — with the main orchestrator explicitly barred
from authoring assertions itself (§4.2); the CodeCompass/
`codecompass-template` pin is now mechanically enforced via a dedicated
worktree or a guard that stops on mismatch, not merely recorded (§2.0);
`check_snapshot.py` now resolves cited evidence against the frozen git
revision's own historical tree (`git cat-file`/`git show
<revision>:<path>`), never today's working tree (§3.7); every
isolation-sensitive Phase 3/4 dispatch now gets an immediate post-dispatch
transcript compliance check, with contamination discarded-and-rerun and
logged to a new `compliance-log.md`, with Phase 6 auditing that log
rather than performing the first contamination check (§4.2a, §5.4); a new
§5.1a resolves a real contradiction between the documentation inventory's
`intentionally retained` disposition and the Phase 5/6 acceptance
criteria that had required reconciliation reports for those same files;
commit-message prose is now excluded from clean-room evidence by default
(§3.2); the template's file count is corrected to eleven files, not nine
(§1.1); and a second, dated `§12` consistency-review addendum records
this round's own full re-read. Resolved all 8 under a new `§8 Part C`
(`C1`–`C8`), matching the existing `Part A`/`Part B` traceability
discipline. 935 tests still pass (regression guard only; no
`ledgerkit/`/`tests/` code touched). Implementation begins immediately
following this commit, per direct instruction.

---

### CodeCompass upgrade + clean-room documentation reconstruction — plan amended — 2026-10-02

Full detail: [dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md](dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md)

**Human:** reviewed the plan below (same day, fresh session) and reported
8 concrete defects, plus resolutions for all 5 of the plan's own open
questions, directing an in-place amendment — explicitly still not to
implement Phase 1.

**Claude:** fixed all 8 in `29-codecompass-upgrade-and-clean-room-docs.md`
(same file, same six-phase structure, amended not replaced): moved every
existing-documentation comparison (including the `api-spec.md` coverage
check) out of Phase 3 and into Phase 5, closing a real clean-room-leakage
defect in the plan's own first draft (§4, §6.4); added a complete
9-document inventory/disposition table so Phase 4's drafted set matches
Phase 5's replaced set exactly (§5.1); separated reconstructable
current-shipped-state fact from forward-looking roadmap intent, the
latter excluded from evidence-checking entirely and reintroduced only
deliberately in Phase 5 (§4.1, §5.1, §6.1); added a small,
deterministic, stdlib-only `check_snapshot.py` that fails closed on five
named integrity conditions, gating Phase 4 (§3.7); corrected the
isolation success criterion so a disclosed `best-effort` tier is never
reported as "enforced" — split into three separately-reported Phase 6
checks instead (§3.4, §7.1); added explicit revision-pinning for both
`codecompass` and `codecompass-template` as Phase 1's first step,
recorded in a new `PINNED-REVISIONS.md` (§2.0); reclassified
`dev-docs/compat-register/*.yaml` as a derived evidence index rather than
primary evidence, requiring material compatibility claims to trace to
their underlying differential-test evidence or get a targeted re-check
(§3.2); and restricted `ledgerkit-editor` inspection to its source/tests,
excluding its own narrative docs. Resolved all 5 original open questions
(ROADMAP.md placement — a new "Tooling & Process Initiatives" section,
not a Stage letter; `knowledge/*.md` stays excluded until Phase 5;
`CLAUDE.md`'s stale folder-structure diagram gets fixed during Phase 1;
six-phase structure retained; `dev-docs/hledger-compatibility.md` is
reconciliation-first, not a blind redraft). Added a new §8
Part-A/Part-B split (the original questions vs. the review's 8 findings,
labelled F1–F8) after finding the two lists' shared 1–8 numbering had
caused several of this document's own cross-references to point at the
wrong item — a self-inflicted defect, caught and fixed by a dedicated
internal-consistency pass (new §12), not left for a future session to
discover. No `ledgerkit/`/`tests/` code touched; no implementation begun;
935 tests still pass (regression guard only).

---

### CodeCompass upgrade + clean-room documentation reconstruction — plan — 2026-10-02

Full detail: [dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md](dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md)

**Human:** directed planning a phase to (1) bring Ledgerkit's CodeCompass
integration current and (2) use the upgraded tooling for a genuine
clean-room reconstruction of the project's human-facing documentation,
with old documentation held out of the reconstruction and reintroduced
only afterward for comparison; explicitly not to implement yet.

**Claude:** investigated live, rather than trusting prior notes — found
CodeCompass's editable install already runs current code
(`context-graph.db`'s `schema_version` already matches the live
`_SCHEMA_VERSION` exactly; only a routine re-sync is needed, not a version
migration) and found CodeCompass's own upstream project independently
built almost exactly the requested methodology already (Phase 79's
clean-room pipeline, `decisions/0066`'s isolation findings, and a
portable, MIT-licensed `optional-clean-room-workflow/` template shipped to
`codecompass-template` — read-only clone, inspected this session).
Produced a six-phase plan (`29-codecompass-upgrade-and-clean-room-docs.md`)
that adopts that template directly rather than re-deriving it: Phase 1
reconciles Ledgerkit's four drifted local agent-brief copies against
upstream and imports two new roles (`implementation-reconstructor`,
`domain-skeptic`); Phase 2 adopts the template's isolation-preflight
discipline, honestly expecting a `best-effort`/`filesystem-only,
network-exposed` result (not `verified`) since Ledgerkit is itself a
public GitHub repository, same structural finding CodeCompass's own ADR
already confirmed for itself; Phase 3 builds evidence-cited, snapshot-
frozen assertions per module topic and independently reconstructs/
compares each; Phase 4 drafts replacement README/architecture/usage/
roadmap documentation from the snapshots alone; Phase 5 reintroduces old
documentation only now, classifies every claim (five-way scheme), and
replaces the live documents; Phase 6 runs an independent
`release-phase-auditor` Definition-of-Done audit against six explicit,
separately-reported validation criteria. Five open questions flagged for
explicit confirmation before Phase 1 starts (`§8`), including where this
sits in `ROADMAP.md` (recommended: its own section, not a Stage letter)
and the evidence/excluded boundary for `knowledge/*.md`. No `ledgerkit/`
or `tests/` code touched; no implementation begun.

---

### [Stage C — Query system] — 2026-09-27

Full detail: [dev-docs/changelog/STAGE-C.md](dev-docs/changelog/STAGE-C.md)

**Summary:** Built a complete, hledger-faithful query language across nine
phases: a standalone `ledgerkit/query/` AST/parser/evaluator subpackage
(Phase 1) wired into `balance`/`register`/`accounts`/`stats` (Phase 2) and
`print` (Phase 3) via `-q`/`--query`; a tag data model (Phase 4); `depth:`
redesigned as a report-display option, never a selection predicate (Phase
5); CodeCompass workflow adoption (Phase 5A, process-only); full
`tag:NAME[=REGEX]` effective-tag matching with the four-source union and
no-shadowing precedence rule (Phase 6); rejection of the empty regex
pattern, matching real hledger (Phase 7); convergence of the legacy
`ledgerkit.models.Query` dataclass onto the same canonical AST/evaluator
every other query path uses, eliminating a second, parallel matching path
(Phase 8); and rejection of empty-alternation-branch regex syntax (Phase
9). Every phase from Phase 6 onward followed a design → human-approval →
fresh-agent-implementation → independent-verification process, several
requiring one or more design-review correction passes before approval.
Zero open `unexplained_mismatch` compat-register entries remain. A
Stage-wide `docs-maintainer` reconciliation pass and two converging rounds
of independent `docs-reconstructor` drift audit, plus an independent
`release-phase-auditor` pass against Stage C's own Definition of Done
(PASS WITH NON-BLOCKING OBSERVATIONS, both closed out), preceded this
archiving. `PythonRegex` (a planned Python-regex escape hatch) was
explicitly resolved as deferred, not implemented or dropped; `cur:`,
hledger's smart/period date expressions, a standalone `--depth`/`-N` CLI
flag, and `check`'s intentional non-wiring from `-q` all remain confirmed,
documented, non-blocking deferrals. Stage C is `[DONE]`.

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

---

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

---

### Publishing readiness for v0.2.0

**Human:** Prepare LedgerKit for its first PyPI release: packaging metadata, CI/CD workflows, documentation, and repository presentation. No parser or feature changes.

**Claude:** Updated `pyproject.toml` with `readme`, `license`, `keywords`, and `[project.urls]` fields; changed `description` to a clearer one-liner. Updated `README.md` Installation section with `pip install ledgerkit` primary command and development-install instructions; added CI badge. Created `.github/workflows/tests.yml` (matrix: Python 3.8–3.12, ubuntu-latest) and `.github/workflows/publish.yml` (OIDC Trusted Publishing; manual `workflow_dispatch` to Test PyPI; auto-publish to PyPI on `v*` tags). Created `dev-docs/pypi-trusted-publishing.md` with one-time setup instructions. Removed completed `pip install packaging & docs` backlog item from `ROADMAP.md`. Build verified: `python -m build` produces `ledgerkit-0.2.0-py3-none-any.whl` and `ledgerkit-0.2.0.tar.gz`; `twine check` passes both artifacts. 575 tests continue to pass.

---

## [0.2.0] — 2026-06-06

---

### [Milestone 4 — Comprehensive Format Compatibility]

Full detail: [dev-docs/changelog/MILESTONE-4.md](dev-docs/changelog/MILESTONE-4.md)

**Summary:** Added comprehensive hledger format compatibility. New model fields `Transaction.date2` (secondary date) and `Posting.cost_raw` (cost annotation text). New `ParseWarning` class for non-fatal parser notices. Amount parser now handles sign-after-prefix-symbol (`$-300`), cost/lot annotations (`@ $180`, `{$182}`), quoted commodity suffix (`3 "Chocolate Frogs"`), space digit-group separators (`1 000 000 JPY`), and E-notation (`1E3 EUR`). New directives: `Y` (default year), `D` (default commodity), `apply account`/`end apply account`. Periodic (`~`) and auto-posting (`=`) rule blocks skipped gracefully with `ParseWarning`. Zero hard errors on the comprehensive fixture; 575 tests pass.

---

## [0.1.0] — 2026-05-29

---

### Rename: PyLedger → ledgerkit

**Human:** Rename the project to `ledgerkit` for the PyPI release (`pyledger` was already taken).

**Claude:** Renamed source package directory `PyLedger/` → `ledgerkit/`. Updated all internal imports, `pyproject.toml` (name, scripts, packages.find), CLI prog name and error prefixes, all doc and knowledge files, and all test imports. 538 tests continue to pass.

---

### Python 3.8+ compatibility

**Human:** Lower the minimum Python requirement from 3.10 to 3.8.

**Claude:** Confirmed all source files already have `from __future__ import annotations` (PEP 563), making `str | None`/`list[str]` annotation syntax safe in Python 3.8. No code changes required. Updated `pyproject.toml` (`requires-python = ">=3.8"`, `target-version = ["py38"]`) and `README.md`.

---

### Commodity display style (`CommodityStyle`)

**Human:** Implement hledger commodity display style inference and CLI `-c` flag.

**Claude:** Created `ledgerkit/commodity_style.py` with `CommodityStyle` dataclass, `infer()` classmethod (detects prefix/suffix, spacing, decimal mark, group separator, precision from raw amount string), `format()` method (applies inferred style; prefix-symbol negatives as `£-5.00`, suffix-symbol negatives as `-5.00 EUR`), and `parse_style_override()` (parses `-c` CLI strings). Added `Amount.raw` field to models so the parser preserves the original amount text. Added `Journal._commodity_directive_raws` to capture style-declaring `commodity` directives. Added `Journal.commodity_styles` property that merges inferred and directive-based styles with directive priority. Updated `cli.py` to use styles in `balance`, `register`, and `print` output and accept `-c`/`--commodity-style` override flag. 29 new tests in `tests/test_commodity_style.py`.

---

### Pandas DataFrame export (optional)

**Human:** Add optional pandas export with `pip install ledgerkit[pandas]`.

**Claude:** Created `ledgerkit/_pandas_compat.py` (lazy import helper). Added `[project.optional-dependencies] pandas = ["pandas>=1.3"]` to `pyproject.toml`. Added `Journal.to_dataframe(query)` returning one row per posting. Added transparent result wrappers `BalanceResult`, `RegisterResult`, `AccountsResult` (with `__eq__` for existing-code compatibility) and `ReportSectionResult.to_dataframe()`. Updated `balance()`, `register()`, `accounts()` to return wrappers; updated `balance_from_spec()` to pass commodity styles. Exported new types from `ledgerkit/__init__.py`. 24 new tests in `tests/test_dataframe.py` (skipped gracefully if pandas absent).

---

### Version bump and classifiers

**Human:** Bump version to `0.1.0`, add PyPI classifiers.

**Claude:** Set `version = "0.1.0"` in `pyproject.toml` and `__version__` in `__init__.py`. Added `Topic :: Office/Business :: Financial :: Accounting` and Python 3.8–3.12 programming language classifiers. Added pandas ecosystem section to `README.md`.

---

## [Unreleased]

---

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

---

## [X.Y.Z] — YYYY-MM-DD

---

### Added
- New features or capabilities

---

### Changed
- Changes to existing behaviour

---

### Fixed
- Bug fixes

---

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

---

### [Milestone N — <Title>] — YYYY-MM-DD

Full detail: [dev-docs/changelog/MILESTONE-N.md](dev-docs/changelog/MILESTONE-N.md)

**Summary:** One or two sentences describing what the milestone delivered.
```

3. **Update `ROADMAP.md`** to mark the milestone `[DONE]` if not already done.

This keeps `CHANGELOG.md` scannable as the project grows while preserving the
full per-commit history in the archive files.

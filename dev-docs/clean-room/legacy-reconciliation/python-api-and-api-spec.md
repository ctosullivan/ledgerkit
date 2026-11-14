<!--
producer: docs-maintainer
mode: legacy-reconciliation (Plan 29 Phase 5, §6.3/§6.4)
targets: docs/python-api.md (live-edited), dev-docs/api-spec.md (proposed-only)
dispatch-date: 2026-11-14
-->

# Legacy reconciliation: `docs/python-api.md` + `dev-docs/api-spec.md`

## Inputs

- Real legacy docs: `docs/python-api.md` (pre-reconciliation), `dev-docs/api-spec.md`
- Phase 4 clean-room draft: `dev-docs/clean-room/drafts/python-api.md.clean-room-draft`
- Phase 3 evidence for all 10 topics: `dev-docs/clean-room/snapshots/*-v1.md(+.sidecar.json)`,
  `dev-docs/clean-room/assertions/<topic>/*.md`,
  `dev-docs/clean-room/implementation-reconstruction/<topic>.md`,
  `dev-docs/clean-room/implementation-comparison/<topic>.md`
- `knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md`

Ordering note (per brief): the clean-room draft (`python-api.md.clean-room-draft`,
committed Phase 4) was read first in this chain; the real legacy docs were read
only after, consistent with the "never retroactively shape a draft" rule.

---

## TASK 1 — `docs/python-api.md` (live-edited)

### Classification summary

The pre-existing document contained ~45 distinct factual claims (excluding
pure code-example syntax). Breakdown:

| Classification | Count | Notes |
|---|---|---|
| `supported` | 41 | Traced to a specific Phase 3 assertion or (for a handful of load/Query-table claims already citing design docs) confirmed consistent with `knowledge/EDGE_CASES.md`/`DECISIONS.md`. None were accepted on draft/legacy agreement alone — see examples below. |
| `stale_or_contradicted` | 0 | No sentence in the pre-existing doc was found to be factually wrong; the problems found were *omission*, not contradiction. |
| `rationale_requiring_verification` | 1 | The depth-rollup note's "corrected in Stage C Phase 5 — register() previously excluded deeper postings entirely, a pre-existing bug" claim — checked against `knowledge/EDGE_CASES.md` EC-017 (resolved 2026-09-17), confirmed true, kept as-is. |
| `useful_example` | 8 code blocks | All pre-existing runnable examples (load, Query filters, ReportSpec, CommodityStyle, DataFrame, Iterate Transactions) kept; none were re-grounded as factually risky, so no rewrite was needed beyond what's listed below. |
| `obsolete` | 0 | Nothing in the document described a since-removed capability. |

**Example of the "agreement is not evidence" discipline applied**: the
pre-existing "Pattern matching (breaking change, Stage C Phase 8)" paragraph
matched the clean-room draft's own text on `HledgerRegex` exclusions closely
— but before marking it `supported` I traced it to
`query-engine@v1#query-engine-012`/`013` specifically (which in turn cite
`ledgerkit/query/regex.py`'s own construct list and a live differential-test
confirmation), not merely to the draft saying the same thing.

### Gaps found and closed (new content added, not previously present at all)

Cross-checking `docs/python-api.md` against `dev-docs/api-spec.md`'s full
public surface turned up a substantial amount of public API with **zero**
coverage in the human-facing docs. All of the following were added, each
grounded in a specific assertion (not merely copied from the draft):

1. **`ledgerkit.checks`** (tier constants, `run_basic_checks`/
   `run_strict_checks`/`run_checks`, `check_transaction_autobalanced`) —
   entirely absent before. New "Validating Transactions" section, citing
   `checks@v1#checks-008` for the `run_checks` skip/names/strict asymmetry
   disclosure (status `supported`, independently reviewed), with the
   `run_strict_checks` forwarding note explicitly hedged as
   reconstruction-only evidence (not a frozen, reviewed assertion for that
   specific function).
2. **`ledgerkit.writer`** (`transaction_to_text`, `journal_to_text`) —
   entirely absent before. New "Serializing Transactions" section, citing
   `reports-cli@v1#reports-cli-014`.
3. **`ledgerkit.EditorDocument`** — entirely absent before, despite being a
   re-exported public class with its own clean-room topic
   (`editor-surface`). New "Editing Journals with `EditorDocument`" section,
   citing `editor-surface@v1#editor-surface-001` through `-005`, and
   disclosing the adoption gap (`-007`/`-009`: the one known real TUI
   frontend does not use it) so the doc doesn't overstate current
   real-world usage.
4. **`resolve_elision`** — a public, re-exported top-level function with no
   mention anywhere in the prior doc. Added under "Loading a Journal",
   citing `journal-parsing@v1#journal-parsing-005`.
5. **`Posting`/`Transaction` fields from Stage C Phase 4 and Editor
   Readiness** (`tags`, `date_override`/`date2_override`, `source_span`,
   `raw_text`, `inline_comment`, `balance_assertion`, `inferred`) — the
   "Data Models" section previously documented only the Milestone-1/2 field
   subset. Added, citing `journal-parsing@v1#journal-parsing-010` and
   `tags@v1#tags-007`/`008`/`009`.
6. **`BalanceRow`, `RegisterRow`, `SourceSpan`** dataclasses — public,
   re-exported, previously undocumented in this file (only referenced via
   the type comment `# BalanceResult (behaves like dict)` with no field
   detail). Added, citing `reports-cli@v1#reports-cli-004`/`-006` and
   `journal-parsing@v1#journal-parsing-010`.
7. **"Working with Tags" section** — `Transaction.tags`/`Posting.tags`,
   `ledgerkit.tags.effective_date`/`effective_date2`, the four-source
   no-shadowing `tag:` matching rule, and the `accounts()`-specific
   narrower tag-visibility exception — entirely absent before. Citing
   `tags@v1#tags-001`/`002`/`003`/`007`/`008`.
8. **Known limitations, previously undocumented in this file**:
   - `parse_string_lenient`'s "never raises" guarantee is not fully
     exhaustive (malformed `commodity` directive still raises `ParseError`
     uncaught; an `alias` backreference overflow raises uncaught
     `re.PatternError`) — `journal-parsing@v1#journal-parsing-008`.
   - hledger's balance-assignment-elision syntax is unimplemented, and for
     a suffix-commodity/comma-decimal amount silently corrupts the amount
     and drops the assertion with no warning —
     `journal-parsing@v1#journal-parsing-009`.
   - A directive opening while a transaction block is still open silently
     discards the rest of that block — `journal-parsing@v1#journal-parsing-007`.
   - Two confirmed `loader.load_journal()` gaps (an uncaught `IndexError`
     reachable via a glob-metacharacter-containing containing-directory
     name; a misleading `FileNotFoundError` for a file that includes
     itself by name) — `loader@v1#loader-002`/`-003`/`-007`.
   - The Stage C Phase 9 empty-alternation-branch regex rejection
     (`"a|"`, `"|a"`, `"(|)"`, etc.) was missing from the "Pattern
     matching" paragraph, which only documented the Phase 7 empty-string
     rejection — added, citing `query-engine@v1#query-engine-013` and the
     `status: verified` compat-register entry
     `LK-COMPAT-QUERY-REGEX-EMPTYALT-001.yaml`.
   - `ReportSectionResult.to_dataframe()`'s known single-commodity
     limitation (picks an arbitrary/first commodity's style for every row)
     was undisclosed in the "DataFrame Export" section — added, citing
     `commodity-styling@v1#commodity-styling-008`.
   - `balance_from_spec`/`ReportSpec`/`ReportSection` being reachable only
     from the Python API, with no CLI command ever invoking them, was
     implied but not stated outright — made explicit, citing
     `reports-cli@v1#reports-cli-013`.

### What changed in `docs/python-api.md` and why (file-level summary)

The file was substantially expanded (not rewritten from scratch — Legacy
Reconciliation Mode is reconciliation, not blind redraft). Every pre-existing
section, example, and the document's overall structure/voice were preserved.
Three new top-level sections were added (`Working with Tags`, `Validating
Transactions`, `Serializing Transactions`, `Editing Journals with
EditorDocument`), existing sections (`Loading a Journal`, `Data Models`,
`Filtering with Query`, `Custom Report Layouts`, `DataFrame Export`, `Error
Handling`) were extended with the specific gaps above, and a closing
"Evidence basis" section was added pointing at this report and the citation
scheme used throughout, mirroring (not copying) the clean-room draft's own
citation-key convention. File path:
`/home/cormac/projects/ledgerkit/docs/python-api.md` (written live, per the
task's explicit instruction — this file is not protected by the
Unauthorised Change Rule).

---

## TASK 2 — `dev-docs/api-spec.md` (protected; proposed revision only)

**`dev-docs/api-spec.md` itself was NOT edited.** No `Write`/`Edit` tool call
targeted that path at any point in this dispatch — it was only ever read.
The full proposed reconciled text (the live file's content with two targeted,
additive docstring edits applied, everything else byte-for-byte unchanged) is
at `dev-docs/clean-room/legacy-reconciliation/api-spec.md.proposed-revision`,
for the lead to present to the user per the Unauthorised Change Rule
("state exactly what would change, ask for confirmation before making the
change").

### Divergences found between `api-spec.md` and the evidence, and resolution

**Divergence 1 — `run_checks`'s docstring omits two confirmed behavioural
asymmetries.**
- **api-spec.md's current text**: documents `skip`/`names`/`strict` as if
  they compose straightforwardly ("skip: names to suppress entirely...").
- **Evidence**: `checks@v1#checks-008` (status: `supported`, reviewed by
  `domain-skeptic`, independently confirmed by direct execution, partially
  corroborated by a model-blind implementation reconstruction per
  `dev-docs/clean-room/implementation-comparison/checks.md`) states two
  confirmed, reproducible facts: (1) a basic/strict-tier name both
  `skip`-suppressed and re-requested via `names` executes **zero** times,
  not once; (2) `skip` is never consulted by `run_checks`'s own strict-tier
  branch, so a name in both `skip` and `STRICT_CHECK_NAMES` still runs when
  `strict=True`.
- **Resolution**: resolved in favour of the evidence, not either document
  by default. These are confirmed facts about current, shipped behaviour
  (not a proposal, not a draft's own unverified claim) — `api-spec.md`'s
  docstring is incomplete as a contract description and should disclose
  them. Proposed revision adds both to `run_checks`'s docstring, and adds a
  related, more cautiously worded note to `run_strict_checks`'s own
  docstring (whose analogous `skip`-forwarding gap is sourced only to the
  implementation-reconstruction's gap #9, not a frozen/reviewed assertion
  for that specific function — worded accordingly, not overstated to the
  same confidence level).

**Divergence 2 — `load_journal`'s docstring's `Raises` section is not
exhaustive.**
- **api-spec.md's current text**: presents `FileNotFoundError`/`ParseError`
  as an exhaustive two-way split for a missing include target.
- **Evidence**: `loader@v1#loader-002`, `loader@v1#loader-003`,
  `loader@v1#loader-007` jointly describe a confirmed, reproducible third
  case — an uncaught `IndexError` when a non-glob include target's
  containing directory name itself contains a glob metacharacter — and a
  separate, confirmed misleading-message case (a self-including file
  reported as `FileNotFoundError` despite existing).
- **Resolution**: resolved in favour of the evidence; these are confirmed,
  reproducible facts about current code, not speculative. Proposed revision
  adds a "Known gaps (confirmed, not yet fixed)" paragraph to
  `load_journal`'s docstring.

**Candidate divergence considered and NOT escalated — `tags-003`'s
hedge on `accounts`-mode tag-visibility wiring.**
`tags@v1#tags-003` hedges that its narrower-tag-visibility claim's "actual
wiring to a specific caller... was not independently verified against that
caller within the permitted evidence for this topic." `api-spec.md`'s
`tags.py`/`reports.py` sections state the wiring as settled fact. Checked
against `knowledge/DECISIONS.md`'s 2026-09-25 entry ("`accounts -q "tag:X"`
replicates hledger's narrower visibility...", explicitly stated as "now
four-way executable-confirmed"), which is later-dated, more direct evidence
than `tags-003`'s own hedge and resolves it. No change proposed — `api-spec.md`
is the better-supported document here, and the resolution is recorded so a
future pass doesn't need to re-derive it.

**No other divergences found.** The remainder of `api-spec.md`'s claims
checked against the clean-room draft and Phase 3 evidence (Query/regex
breaking-change notes, `accounts=[...]` Stage C Phase 8 rebuild, `depth:`
modelling, `tag:` four-source semantics, `stats`'s depth-exclusion quirk,
`EditorDocument`'s v1 limitations, writer round-trip guarantees) were
consistent with the evidence and with the clean-room draft's own text where
overlapping. `api-spec.md` is generally **more** current and complete than
`docs/python-api.md` was before this pass (it already documents the Stage C
Phase 9 empty-alternation rejection in the `regex.py` section, which
`docs/python-api.md` was missing — see Task 1 above).

### §6.4 coverage check — real number

**Method**: enumerated every distinct public symbol `dev-docs/api-spec.md`
documents with its own header/signature (classes, dataclasses, module-level
functions, and named constant groups — excluding symbols the file itself
marks private, e.g. `ledgerkit.query.compat`'s three functions and
`ledgerkit/tags.py`'s five private helpers), then checked whether at least
one Phase 3 assertion (across all 10 snapshot topics) states a claim about
that symbol.

**Result: 67 of 72 listed public symbols have a corresponding Phase 3
assertion. 5 gaps:**

1. **`ReportSection`** — only generically named (not its own field-level
   contract: the OR-across-`accounts`/exclude-subtraction mechanics, the
   `label`/`depth` override defaults) in `reports-cli@v1#reports-cli-013`;
   no assertion directly exercises `ReportSection`'s own dataclass shape.
2. **`ReportSpec`** — same situation; `reports-cli-013` names it but does
   not assert its own fields (`show_subtotals`/`show_total`/`total_label`
   defaults).
3. **`load_journal_stdin`** — no `loader-XXX` assertion mentions it at all;
   all eight `loader` assertions concern `load_journal`'s include-expansion
   path specifically.
4. **`run_strict_checks`** — no `checks-XXX` assertion is about this
   function itself (`checks-008` is specifically about `run_checks`); its
   own skip-forwarding-only-to-basic-tier behaviour is attested only in the
   implementation-reconstruction's gap #9, not in a frozen, reviewed Phase
   3 assertion.
5. **`Journal.to_dataframe`** (and, with it, `BalanceResult`/
   `RegisterResult`/`AccountsResult.to_dataframe()` and the "Result
   wrappers (transparent)" claim) — no Phase 3 assertion in any of the 10
   topics covers pandas/DataFrame export at the `Journal`/report-wrapper
   level at all. The one adjacent assertion,
   `commodity-styling@v1#commodity-styling-008`, covers a *different*
   symbol (`ReportSectionResult.to_dataframe()`'s single-commodity quirk
   specifically), not this area generally.

These gaps are coverage gaps in the Phase 3 clean-room evidence pass, not
confirmed defects in `api-spec.md`'s own claims — nothing above contradicts
what `api-spec.md` says, it simply means those five symbols' documented
behaviour rests on the existing test suite/code reading rather than on an
independently re-verified clean-room assertion. Recorded here for the lead
to weigh whether a follow-on Phase 3 pass (an 11th mini-topic, or extending
`reports-cli`/`checks`/`loader`) is warranted; not something this role can
resolve by writing more documentation.

---

## Confirmation

- `docs/python-api.md`: written live (Task 1 instruction) — see diff
  described above.
- `dev-docs/api-spec.md`: **not** touched. Only read. Proposed revision at
  `dev-docs/clean-room/legacy-reconciliation/api-spec.md.proposed-revision`.
- No compat-register entry's `status`/`kind` was set or changed by this
  dispatch.
- `CLAUDE.md`, `.claude/skills/codecompass/SKILL.md`, and the generated
  marker block were not touched.

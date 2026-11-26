---
role: domain-skeptic
mode: comparison
topic: compat-system
dispatch-id: plan29-phase-comparison-compat-system-20261114
date: 2026-11-14
---

# Implementation comparison: `compat-system` — snapshot `compat-system-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/compat-system-v1.md` +
  `compat-system-v1.sidecar.json` (11 assertions, frozen
  2026-10-02T16:50:03Z, repository revision
  `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 11 frozen assertion files under
  `dev-docs/clean-room/assertions/compat-system/`.
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/compat-system.md`
  (dispatch: Plan 29 Phase 3, same-host/prompt-scoped, dated 2026-10-03;
  evidence basis: the 49 live `dev-docs/compat-register/*.yaml` entries,
  `dev-docs/compat-register/schema.md`, and a named subset of
  `tests/*` files — no access to the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source,
test, or compat-register file was read directly by this dispatch
(comparison mode compares the two clean-room artefacts only); all
findings below rest on what each artefact itself states.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| compat-system-001 | definition | aligned |
| compat-system-002 | rule | aligned |
| compat-system-003 | state_transformation | aligned |
| compat-system-004 | state_transformation | aligned |
| compat-system-005 | relationship | aligned |
| compat-system-006 | boundary | aligned |
| compat-system-007 | boundary | aligned |
| compat-system-008 | boundary | **partial** |
| compat-system-009 | boundary | aligned |
| compat-system-010 | boundary | aligned |
| compat-system-011 | boundary | aligned |

**10 aligned / 1 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

## Per-assertion notes

**compat-system-001** (closed 5-value `kind` taxonomy; fixed
`kind`→`relationship` mapping). Reconstruction §2 independently states
the same enum (`COMPAT | EXT | DIV | UNSUP | MISMATCH`) from
`schema.md`, and §1's "`ledgerkit.relationship:` distribution — cross-
checked against `kind:`" table confirms the identical mapping
(`equivalent`↔`compatible`, `subset`↔`unsupported`,
`incomparable`↔`intentional_divergence`/`unexplained_mismatch`,
`superset`↔`extension`) holding with zero exceptions across all 49
files. Both artefacts also independently flag the same gap: no live
entry currently uses `kind: extension`/`relationship: superset`.
Aligned.

**compat-system-002** (four-tier `status` field; `status: verified`
restricted to a separately-dispatched `compat-differential-tester`,
never written by the lead directly; rule holds across all 23
non-`proposed` entries). Reconstruction §3 independently states:
"entries at `status: self-verified` carry verified_by text explicitly
naming the same-session caveat... entries at `status: verified` instead
name 'compat-differential-tester (independent dispatch...)'" and that
all `proposed` entries have `verified_by: null`. This matches the
assertion's claimed authorship split exactly, including the same counts
(14 `verified`, 9 `self-verified`) used as the universe being checked.
Aligned.

**compat-system-003** (49 live entries; kind distribution 40/6/2/1/0;
id-prefix distribution matches). Reconstruction §1's two tables
(filename-prefix distribution and `kind:` field distribution) give the
identical numbers: COMPAT 40, UNSUP 6, MISMATCH 2, DIV 1, EXT 0, and
explicitly states "`kind:` field distribution... matches filename prefix
1:1 in every file." Aligned.

**compat-system-004** (`status` distribution 26 `proposed` / 9
`self-verified` / 14 `verified` / 0 `final`, summing to 49). Reconstruction
§3: "`status:` distribution: `proposed` 26, `self-verified` 9, `verified`
14 (sums to 49). `final`... do[es] not occur at all in the live
register." Identical counts. Aligned.

**compat-system-005** (resolution lifecycle for `unexplained_mismatch`:
new entry + `resolves`, old entry untouched except `resolved_into`/
`resolved_date`; exercised exactly twice, 0 currently open). Reconstruction
§3's "Resolution-lifecycle mechanism verified end-to-end on both pairs"
independently confirms both pairs by id
(`LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`↔
`LK-COMPAT-QUERY-TAG-EMPTYVALUE-001`,
`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`↔
`LK-COMPAT-QUERY-REGEX-EMPTYALT-001`), the same mechanism (old `kind:`
and evidence untouched, new entry carries `resolves:`), and the same "2
of 2... resolved; 0 remain open" conclusion. Both artefacts independently
flag the identical unverifiable sub-claim — whether `UNEXPLAINED.md`'s
own open/resolved bookkeeping was actually updated — as out of their
respective permitted evidence (assertion's "Open questions"; reconstruction
§8 limitation 7). This shared boundary-of-verification is itself a form
of alignment, not a gap between the two artefacts. Aligned.

**compat-system-006** (`LK-COMPAT-ACCOUNTDIR-001` cites
`tests/test_directives/test_directives.py::TestAccountDirective`,
confirmed to exist). Reconstruction §7 independently lists
`TestAccountDirective` among the classes "confirmed to exist exactly as
cited... in `test_directives/test_directives.py`." Aligned.

**compat-system-007** (`LK-COMPAT-PARSER-TAG-COMMODITY-001` cites
`TestCommodityDirectiveTags`, confirmed to exist). Reconstruction §7
independently lists `TestCommodityDirectiveTags` among the confirmed
classes in the same file. Aligned.

**compat-system-008** (`LK-COMPAT-QUERY-DEPTH-001` cites ten distinct
test identifiers across four files/directories, including four named
methods of `TestQueryAstIntegration`: `test_balance_query_depth_
truncates_rather_than_excludes`, `test_balance_query_depth_custom_regex`,
`test_accounts_query_depth_clips_and_deduplicates`,
`test_register_query_depth_clips_label_never_excludes`; all ten claimed
to exist). **Partial.** The two artefacts agree that `TestDepthSpec`,
`TestMaxAccountLevel`, `TestQueryAstIntegration`, and `TestQueryFlag` all
exist and that this entry's citations into them are broadly good — but
they disagree on a specific, named count: reconstruction §7 states
"`TestQueryAstIntegration` (+5 of its methods cited by
`LK-COMPAT-QUERY-DEPTH-001`)" — five methods, explicitly attributed to
this entry by id — while the assertion's own `Evidence` field names
exactly four methods under `TestQueryAstIntegration` for this same
entry. This is not merely an ambiguous phrasing on the reconstruction's
side: it names the entry id directly, the way it does not for the
`TestQueryFlag` "+9" figure in the same paragraph (which reads as an
aggregate across multiple entries' citations into that class, not
entry-specific). If the reconstruction's "+5" is accurate, the
assertion's "ten distinct test identifiers... all ten exist exactly as
named" undercounts by one (eleven, not ten); if the assertion's four is
accurate, the reconstruction overcounts by one. Per this mode's rules,
neither artefact is revised to force agreement, and this dispatch did
not read `tests/test_reports.py` directly (out of scope for comparison
mode) to adjudicate which figure is right. Recorded as `partial`
specifically on this named count; the other nine identifiers' existence
is not in dispute between the two artefacts.

**compat-system-009** (`LK-COMPAT-QUERY-REGEX-EMPTYALT-001` resolves a
prior mismatch and cites four test identifiers, all independently
confirmed to exist, including correct class/method nesting for the two
`::`-qualified compound citations). Reconstruction §7 independently lists
`TestEmptyAlternationBranchRejected`, `TestEmptyAlternationBranchAccepted`
(`test_regex.py`), `TestEmptyAlternationBranchRejectedAtParseTime`
(`test_parser.py`), and `TestQueryFlag` with "+9 of its methods, all
confirmed present" (test_cli.py) — consistent with, though not a
name-for-name confirmation of, the assertion's fourth cited identifier
`TestQueryFlag::test_empty_alternation_branch_exits_one` (the
reconstruction's own "e.g." list of `TestQueryFlag` methods is explicitly
a non-exhaustive sample, not a complete enumeration, so the absence of
this one specific method name from the sample is not a contradiction).
Aligned.

**compat-system-010** (`LK-UNSUP-QUERY-DATE-002`: `implementation: []`
permitted for `kind: unsupported`; cites
`TestDateSpans::test_malformed_date_rejected`, confirmed to exist and
correctly nested). Reconstruction §3's `implementation`/`tests`
empty-list bullet independently names `QUERY-DATE-002` among the three
`unsupported` entries with `implementation: []`, matching exactly.
Reconstruction §7 independently confirms `TestDateSpans` exists in
`test_query/test_parser.py`, but its citation-accuracy trace was
explicitly a non-exhaustive sample (§7: "not an exhaustive trace of all
49 entries' citations") and does not separately name
`test_malformed_date_rejected`; this is silence, not disagreement.
Aligned on everything the reconstruction actually speaks to.

**compat-system-011** (`LK-COMPAT-PARSER-POSTINGDATE-001` cites
`tests/test_tags.py::TestEffectiveDate` and `::TestEffectiveDate2`, both
confirmed to exist). Reconstruction §7 independently lists
`TestEffectiveDate` and `TestEffectiveDate2` among the confirmed classes
in `test_tags.py`. Aligned.

## Findings the reconstruction raised that no assertion covers

Per the comparison-mode brief, flagging gaps in either direction: the
reconstruction (§7, §8 limitation 2) reports a concrete test-citation
defect — `LK-COMPAT-PARSER-TAG-001.yaml` and
`LK-COMPAT-PARSER-TAG-SCOPE-001.yaml` cite a class, `TestParseTags`
(and a method `test_multiline_comment`), that does not exist anywhere in
`tests/test_tags.py` as filed. **None of the 11 frozen assertions in
this snapshot cite either of those two entries or that class** — the
closest assertion to this area, compat-system-007, concerns a different
entry (`LK-COMPAT-PARSER-TAG-COMMODITY-001`) whose own cited class
(`TestCommodityDirectiveTags`) the reconstruction confirms does exist.
This is therefore not a conflict with any assertion in this snapshot —
it is a gap in the snapshot's own coverage of the register (two entries
with a real citation defect that this version of the compat-system
snapshot simply never asserted anything about), worth surfacing to
whoever scopes a v2 assertion-research pass for this topic, but it does
not change any classification above.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. For
compat-system-001, -002, and -005 (`definition`/`rule`/`relationship`-
kind assertions), "aligned" means only that the independently-
reconstructed as-built register currently matches the stated taxonomy,
authorship rule, and resolution mechanism — it does not establish that
this taxonomy, rule, or mechanism is itself the right design for
tracking hledger compatibility. For the `boundary`-kind assertions
(compat-system-006 through -011) built on existence-only test-citation
checks, "aligned" means the named test identifiers exist as cited in
both artefacts' independent readings — it says nothing about whether
those tests actually assert the specific compatibility behaviour each
register entry narrates (both artefacts are explicit that method bodies
were out of scope for an existence-only check).

## What was checked

- All 11 assertion `Statement`/`Evidence`/`Examples`/`Open questions`
  fields against the reconstruction report's §1–§8 content,
  assertion-by-assertion.
- Every count the assertions assert (49 total, 40/6/2/1/0 kind
  distribution, 26/9/14/0 status distribution, 2-of-2 resolved
  mismatches) against the reconstruction's independently-derived
  equivalents — all matched exactly except the one named discrepancy in
  compat-system-008.
- Whether either artefact's stated open questions (UNEXPLAINED.md
  bookkeeping, `directly_translated` being unexercised, the
  `examples/`-directory exclusion) were silently resolved one way or the
  other by the other artefact — they were not; both land on the same
  unresolved boundary in each case.
- Whether the reconstruction's own flagged defect (`TestParseTags`)
  implicates any of the 11 frozen assertions — it does not; recorded
  above as a snapshot-coverage gap, not a classification.

## Escalations

None. The one `partial` finding (compat-system-008's TestQueryAstIntegration
method count) is recorded in this report as a named, unresolved
discrepancy between the two independent artefacts; resolving it would
require reading `tests/test_reports.py` directly, which is out of scope
for this comparison dispatch. Nothing else here rises to a genuine
conflicting or not_implemented classification.

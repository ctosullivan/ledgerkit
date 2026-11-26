# Implementation Reconstruction: compat-system

- **Role**: implementation-reconstructor
- **Topic**: compat-system (`dev-docs/compat-register/` — structure, schema, internal consistency; NOT the hledger-compatibility claims of any one feature)
- **Dispatch**: Plan 29 Phase 3, same-host/prompt-scoped dispatch (best-effort isolation, not independently verified)
- **Date**: 2026-10-03

This report reconstructs what the compat-register system actually contains and how it is
actually structured, from the following evidence only: the 49 live entry `*.yaml` files in
`dev-docs/compat-register/`, `dev-docs/compat-register/schema.md`, and the test files named
in this dispatch's permitted-evidence list (`tests/test_cli/test_cli.py`,
`tests/test_directives/test_directives.py`, `tests/test_query/test_eval.py`,
`tests/test_query/test_parser.py`, `tests/test_query/test_regex.py`, `tests/test_reports.py`,
`tests/test_tags.py`). No assertion, snapshot, legacy narrative doc, or planning doc was read.
`dev-docs/compat-register/README.md` and `UNEXPLAINED.md`, and the `examples/` subdirectory,
were deliberately not read (hard exclusion for this dispatch) — their existence was noted
only incidentally via a directory listing, their content was not.

## 1. Structure

The register is a flat directory of one YAML file per entry, named
`LK-<KIND>-<AREA>-<NNN>.yaml`. Confirmed inventory via `ls`:

- **49** live entry files directly in `dev-docs/compat-register/` (matches the count stated
  in this dispatch's own scope).
- A separate `examples/` subdirectory holds `LK-DIV-INCLUDE-001.yaml` and
  `LK-EXT-QUERY-001.yaml` — per `schema.md`'s own text, these are "illustrative entries...
  kept as worked examples... not part of the live register." Not read as content; only their
  filenames were seen in a directory listing, consistent with the hard-exclusion boundary
  (they are not in the permitted path list and were not opened).
- `schema.md` (9394 bytes), `README.md`, and `UNEXPLAINED.md` sit alongside the entries.
  Only `schema.md` is in my permitted paths; the other two were not opened.

`id:` always matches the filename stem exactly (verified programmatically across all 49
files, zero mismatches) and all 49 ids are unique (zero duplicates).

### Filename-prefix (`KIND`) distribution across the 49 live files

| KIND prefix | count |
|---|---|
| COMPAT | 40 |
| UNSUP | 6 |
| MISMATCH | 2 |
| DIV | 1 |
| EXT | 0 (only appears in the excluded `examples/` dir, never live) |

### `kind:` field distribution (matches filename prefix 1:1 in every file)

| `kind:` value | count |
|---|---|
| `compatible` | 40 |
| `unsupported` | 6 |
| `unexplained_mismatch` | 2 |
| `intentional_divergence` | 1 |
| `extension` | 0 |

**Notable gap**: no live entry currently has `kind: extension` / `KIND` prefix `EXT`. The
schema defines and illustrates this kind (via the excluded example file), and
`ledgerkit.relationship: superset` is defined in `schema.md` for exactly this case, but no
live entry in the 49-file register currently exercises it. This is an honest coverage gap in
the register's current contents, not a flaw in the schema itself.

### `ledgerkit.relationship:` distribution — cross-checked against `kind:`

| relationship | count | kind it co-occurs with |
|---|---|---|
| `equivalent` | 40 | always `compatible` |
| `subset` | 6 | always `unsupported` |
| `incomparable` | 3 | `intentional_divergence` (1) + `unexplained_mismatch` (2) |
| `superset` | 0 | would pair with `extension`, which has zero live entries |

This cross-check held with no exceptions across all 49 files — `relationship` and `kind` are
never out of step with each other or with `schema.md`'s own stated mapping.

## 2. Schema (from `schema.md`, read directly)

One file per entry. `KIND` ∈ `COMPAT | EXT | DIV | UNSUP | MISMATCH`; `AREA` a short slug.
Required top-level fields per the documented template: `id`, `area`, `kind`, `upstream.project`,
`upstream.compatibility_target`, `ledgerkit.relationship`, `compatibility.upstream_syntax_preserved`,
`compatibility.extension_requires_explicit_syntax`, `reason`, `implementation`, `tests`,
`evidence` (list of `{kind, ref, pinned_at}`), `status`, `verified_by`, `verified_date`.
Optional fields: `resolved_into`/`resolved_date` (set only on an `unexplained_mismatch` entry
once resolved), `resolves` (set on the new entry that resolves an old mismatch, reciprocal),
`directly_translated` (default false, for a near-line-for-line port of hledger's own code).

`status` has an explicit five-value lifecycle with stated meaning and a load-bearing rule:
`proposed` → `self-verified` (same-session executable check, not independently reviewed) →
`verified` (a *separately-dispatched* `compat-differential-tester` agent's own output — the
lead "must NEVER write this status into a register YAML directly") → `final` (docs
reconciled). `unexplained_mismatch` entries "can only be `verified`" by definition, never
`final`, since they haven't resolved into a settled classification.

`schema.md` also states a soft evidentiary rule: "`evidence` should normally include at
least one `executable` item before `status` moves past `proposed`." And a hard rule for
`unexplained_mismatch`/`unsupported`: `implementation`/`tests` may legitimately be empty
lists for these two kinds, and fabricating a reference merely to satisfy the schema is
explicitly called out as "worse than an empty one."

### Resolution lifecycle (stated mechanism)

`schema.md` documents a specific mechanism for resolving an `unexplained_mismatch`: never
edit the old entry's `kind:` in place; instead create a **new** entry with the settled
`KIND`/`kind:` and `resolves: <old id>`, and add only `resolved_into:`/`resolved_date:` to the
old entry, leaving its `kind: unexplained_mismatch` and original evidence untouched as
historical record. `UNEXPLAINED.md` update and cross-reference updates are also stated as
required steps but were not checked (both out of permitted-evidence scope for this
dispatch — `UNEXPLAINED.md` is a hard exclusion).

## 3. Field-level consistency findings (verified against the 49 live files directly)

- **`upstream.compatibility_target`**: every one of the 49 files pins the exact same string,
  `"1.52.4"` — uniform across the whole register, no file uses "latest" or a different pin
  (confirmed by `grep -L`/`grep -h` across all files — zero files without this exact value).
- **`status:` distribution**: `proposed` 26, `self-verified` 9, `verified` 14 (sums to 49).
  `final` and `extension`'s `superset` do not occur at all in the live register.
- **Evidence-gating rule actually holds in practice, not just in prose**: all 26 `proposed`
  entries have **zero** `kind: executable` evidence items; all 23 `self-verified`/`verified`
  entries have **at least one** (1–3 each). This is a genuine, mechanically-checked
  consistency between the schema's stated soft rule and the register's actual contents — no
  exceptions found in either direction.
- **`verified_by` text is substantive, not boilerplate**: entries at `status: self-verified`
  carry verified_by text explicitly naming the same-session caveat (e.g. "Claude (lead
  session,... implementation). Relabelled `verified` → `self-verified`..."); entries at
  `status: verified` instead name "compat-differential-tester (independent dispatch,
  ...)" with a specific phase/reason. All `proposed` entries have `verified_by: null` /
  `verified_date: null`, consistent with "required once status != proposed" in `schema.md`.
- **`directly_translated`**: the field appears in **zero** of the 49 live files (grep for
  the literal string found no matches at all). The field is documented as "rare and should
  be rare," and the register's actual contents are consistent with that — but it also means
  no entry in the live register currently claims or substantiates a direct-translation
  provenance, so this field is entirely unexercised in practice, not merely rare.
- **Resolution-lifecycle mechanism verified end-to-end on both pairs that use it**: read
  `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml` and its resolving
  `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml` in full. The old entry's `kind:` is untouched
  (still `unexplained_mismatch`), its original evidence is untouched, and only
  `resolved_into: LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` / `resolved_date: "2026-09-25"` were
  added. The new entry carries `resolves: LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`, its own
  fresh `status: verified`/`verified_by`/`verified_date`, and cites the old entry by id in
  its `reason:`/evidence prose. The `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` ↔
  `LK-COMPAT-QUERY-REGEX-EMPTYALT-001` pair follows the identical pattern (confirmed via
  `resolved_into`/`resolves` grep, not fully read line-by-line). This is the only resolution
  pair presently in the register — 2 of 2 `unexplained_mismatch` entries are resolved; 0
  remain open as of this read (though `UNEXPLAINED.md`'s own "open" table, which would be the
  authoritative tracker for that claim, was not read — out of scope).
- **`implementation`/`tests` empty-list rule for `unsupported`/`unexplained_mismatch`**: of
  the 6 `unsupported` entries, 3 (`AUTOPOSTING`, `PERIODIC`, `TIMECLOCK`) have a non-empty,
  one-line `implementation:` pointing at the specific skip/allowlist behavior, while the
  other 3 (`MULTICURRENCY`, `QUERY-DATE-002`, `VIRTUALPOSTING`) have `implementation: []`.
  Both 2 `unexplained_mismatch` entries have `implementation: []`/`tests: []`, consistent
  with `schema.md`'s explicit permission for this kind.

## 4. Public surface of the register (as a data artifact, not code)

There is no code-level "public surface" for this topic per the dispatch's own scope
(no `ledgerkit/*.py` source was read, by hard exclusion). The register's "surface" is the
YAML schema itself (§2 above) plus the two cross-reference fields (`resolved_into`/`resolves`)
that let one entry point at another. No tooling/validator script for the schema was found
inside the permitted paths (none of `schema.md`'s prose references a linter file, and no such
file path was given to search) — whether the schema's rules (e.g., the `id`==filename
convention, or the executable-evidence-before-non-proposed rule) are mechanically enforced
anywhere, versus merely followed by convention so far, could not be established from the
permitted evidence. All consistency findings in §3 are observational (true of the current 49
files), not proof of an enforcing mechanism.

## 5. Data model

Fully described in §2 from `schema.md`'s own template; confirmed against real files in §3.
Two representative full entries were read end-to-end
(`LK-COMPAT-ACCOUNTDIR-001.yaml`, a `proposed` compat entry citing only `manual` evidence;
`LK-UNSUP-MULTICURRENCY-001.yaml`, a `proposed` unsupported entry with empty
`implementation`/`tests`) and both match the documented template exactly, field for field,
in field order and type.

## 6. Dependencies

Not independently applicable to this topic under the stated scope (no source code read).
The register's only "dependency" visible from permitted evidence is on the test suite via its
`tests:` field citations (§7) and on an external pinned hledger binary via `evidence.pinned_at`
strings like `"1.52.4-g33fa849e7-20260910 (/home/cormac/.local/bin/hledger)"`, seen verbatim in
the two mismatch/resolution entries read in full.

## 7. Runtime behaviour / test citation accuracy (compat-register/*.yaml → tests/*)

Per this dispatch's instruction #8, I traced a sample of `tests:` field citations against the
real test files in my permitted-evidence list (not an exhaustive trace of all 49 entries'
citations, and not of citations into test files outside my permitted list, e.g.
`tests/test_checks/test_checks.py`, `tests/test_loader/test_loader.py`,
`tests/test_parser/test_parser.py`, `tests/test_query/test_compat.py`, `tests/test_dataframe.py`
— those could not be checked here and should be treated as unverified by this report).

**Classes and methods confirmed to exist exactly as cited**, across all permitted test files
(spot-checked broadly, not just one or two): `TestAccountDirective`, `TestAliasDirective`,
`TestCommodityDirective`, `TestCommodityDirectiveTags`, `TestAccountDirectiveTags`,
`TestDecimalMarkDirective`, `TestPayeeDirective`, `TestPDirective`, `TestTagDirective` (all in
`test_directives/test_directives.py`); `TestBarePatternAndPrefixes::test_desc_prefix`,
`TestNotAndCombination`, `TestDateSpans`, `TestDepthSpec`,
`TestEmptyAlternationBranchRejectedAtParseTime`, `TestTag::test_empty_value_pattern_rejected`,
`TestEmptyPatternRejected`, `TestTag::test_not_tag_negation`,
`TestTag::test_multiple_tag_terms_and_not_or`, `TestTag::test_tag_and_acct_combine_with_and`
(all in `test_query/test_parser.py`); `TestAcct`, `TestCombinators::test_negated_pair_excludes_both`,
`TestDateSpan`, `TestMaxAccountLevel`, `TestDesc`, `TestStatus`, `TestTag`, `TestTagAccountsMode`
(in `test_query/test_eval.py`); `TestEmptyAlternationBranchRejected`,
`TestEmptyAlternationBranchAccepted`, `TestEmptyPattern`, `TestEmptyMatchingPatternsRemainAccepted`
(in `test_query/test_regex.py`); `TestQueryAstIntegration` (+5 of its methods cited by
`LK-COMPAT-QUERY-DEPTH-001`), `TestQueryAstTagIntegration`, `TestStatsAccountFilterCorrection`,
`TestBalanceFromSpecOuterQueryConvergence`, `TestReportSectionHledgerRegexValidation`,
`TestDeprecatedAccountsShim`, `TestPostingMatchesRetired`, `TestQueryHledgerRegexStrictness`
(in `test_reports.py`); `TestEffectiveDate`, `TestEffectiveDate2`, `TestInheritedAccountTags`,
`TestEffectiveTags`, `TestAccountsEffectiveTags`, `TestCommodityTags`, `TestPostingCommodities`
(in `test_tags.py`); `TestQueryFlag` (+9 of its methods, all confirmed present, e.g.
`test_balance_query_depth_truncates`, `test_stats_query_depth_excludes_rather_than_clips`,
`test_print_query_filters_whole_transactions`, `test_print_status_query`,
`test_empty_value_pattern_exits_one`), `TestTagQueryFlag` (in `test_cli/test_cli.py`).

**One confirmed citation defect** (see §8 Limitations — this is the single most
decision-relevant finding in this report): two entries cite a class, `TestParseTags`, inside
`tests/test_tags.py` that **does not exist** in that file. `tests/test_tags.py`'s actual
top-level classes are `TestBasicTags`, `TestNameDelimiting`, `TestValueHandling`,
`TestMultipleValuesPerName`, `TestMultiLineComments`, `TestEffectiveDate`, `TestEffectiveDate2`,
`TestInheritedAccountTags`, `TestPostingCommodities`, `TestCommodityTags`, `TestEffectiveTags`,
`TestAccountsEffectiveTags` — no `TestParseTags` anywhere in the file (confirmed by both a
class-listing grep and a direct text grep for the string `ParseTags`, zero hits either way).
The two affected citations:
  - `LK-COMPAT-PARSER-TAG-001.yaml` → `tests/test_tags.py::TestParseTags`
  - `LK-COMPAT-PARSER-TAG-SCOPE-001.yaml` → `tests/test_tags.py::TestParseTags::test_multiline_comment`
    (the method name `test_multiline_comment` also does not exist anywhere in the file; the
    closest-named real class is `TestMultiLineComments`, whose own methods are
    `test_tags_collected_across_joined_lines` and
    `test_trailing_comma_does_not_continue_onto_next_line` — neither matches the cited name
    exactly either).

This could mean the class was renamed/moved after the register entry was written (e.g. it may
now live in `tests/test_parser/test_parser.py`, which is outside this dispatch's permitted
evidence and so could not be checked), or it could mean the citation was never accurate. Either
way, as filed, these two `tests:` references in the live register do not resolve against the
file they name.

## 8. Limitations / gaps (honest, from evidence — flagged for priority attention)

1. **Unexercised `kind: extension` / `relationship: superset`.** Zero of the 49 live entries
   use this kind; it exists only in the excluded `examples/` worked-example file. Any claim
   that the register "covers" ledgerkit's extensions beyond hledger is not supported by the
   live register's current contents — that category is simply empty right now.
2. **Confirmed test-citation defect**: `TestParseTags` (and `TestParseTags::test_multiline_comment`)
   cited in `LK-COMPAT-PARSER-TAG-001.yaml` and `LK-COMPAT-PARSER-TAG-SCOPE-001.yaml` do not
   exist in `tests/test_tags.py` as filed (§7). This is a concrete, mechanically-verified gap
   between the register's stated evidence and the actual test suite, not a matter of
   interpretation — a targeted re-check (where did this class actually move/go, or was it ever
   real) is warranted before trusting these two entries' `tests:` field.
3. **Citations into test files outside this dispatch's permitted list were not checked.**
   Several entries cite `tests/test_checks/test_checks.py`, `tests/test_loader/test_loader.py`,
   `tests/test_parser/test_parser.py` (the core parser test file, distinct from
   `tests/test_query/test_parser.py`), `tests/test_query/test_compat.py`, and
   `tests/test_dataframe.py` — none of these were in my permitted-evidence list, so their
   citation accuracy is unverified by this report and should not be assumed correct merely
   because the checked subset was mostly accurate.
4. **26 of 49 entries (53%) are still `status: proposed`** — meaning, per `schema.md`'s own
   definition, they are "hledger-researcher's reading; not yet run against the real binary."
   These 26 all consistently lack executable evidence (§3), which is internally honest, but it
   also means over half the register's compatibility claims currently rest on `manual`/`source`
   evidence only (documentation reading or code reading), not an observed comparison.
5. **No `final`-status entries exist anywhere in the live register.** Per `schema.md`,
   `final` requires "docs reconciled and cross-linked from `hledger-compatibility.md`" — that
   reconciliation step has evidently not happened for any entry yet (0 of 49), including the
   14 that are already independently `verified`.
6. **No enforcement mechanism for the schema's own rules was found within the permitted
   evidence** (§4) — the `id`==filename convention, the executable-evidence-before-`proposed`
   rule, and the `status: verified` write-restriction to a separately-dispatched agent all held
   universally across the 49 files I checked, but nothing in `schema.md` or the YAML files
   themselves points to a validator/linter that would catch a future violation mechanically;
   consistency so far appears to be by discipline, not by tooling, as far as this evidence shows.
7. **`UNEXPLAINED.md`'s "open entries" claim was not independently checked** (hard exclusion).
   I found exactly 2 `unexplained_mismatch` entries in the live register and both carry
   `resolved_into`/`resolved_date`, suggesting zero are currently open — but the authoritative
   open/resolved tracking table for this is `UNEXPLAINED.md` itself, which I was not permitted
   to read, so this "zero open" observation is inferred from the entries alone, not confirmed
   against the index that is supposed to track it.
8. **`directly_translated` is entirely unused** (§3) — zero live entries set it, so this
   schema field's actual behavior/formatting when populated (e.g., whether the required
   accompanying code comment and `THIRD-PARTY-NOTICES.md` entry convention is followed) could
   not be checked at all from the current register contents.

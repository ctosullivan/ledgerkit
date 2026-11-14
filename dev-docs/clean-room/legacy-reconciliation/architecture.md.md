<!--
role: docs-maintainer
mode: legacy-reconciliation (Plan 29 §6, Phase 5)
target: dev-docs/architecture.md
clean-room draft consulted: dev-docs/clean-room/drafts/architecture.md.clean-room-draft
date: 2026-11-14
-->

# Legacy reconciliation: `dev-docs/architecture.md`

Classifies every distinguishable claim in the real, pre-reconciliation
`dev-docs/architecture.md` (319 lines) against Plan 29 Phase 3's evidence
(snapshots, frozen assertions, independent implementation-reconstruction,
and domain-skeptic implementation-comparison reports) for the ten bounded
topics, plus `knowledge/*.md` and, where no topic's evidence reached far
enough, direct `ledgerkit/*.py`/`tests/*.py` file:line verification (the
same kind of "real file:line" evidence the clean-room governing rule
accepts as grounding). Scheme per Plan 29 §6.1: `supported`,
`stale_or_contradicted`, `rationale_requiring_verification`,
`useful_example`, `obsolete`.

**Agreement between the legacy doc and the clean-room draft was not, by
itself, treated as evidence.** Every `supported` classification below
traces to a specific topic assertion id (`<topic>@v1#<id>`) or a direct
file:line citation, not merely to the two documents echoing each other.

## Classification summary

| Count | Classification |
|---|---|
| 14 | `supported` (content true, folded in — either already present in the clean-room draft, or newly re-grounded and added) |
| 4 | `stale_or_contradicted` (now wrong or materially incomplete; not restored as stated) |
| 6 | `obsolete` (describes a since-superseded framing — historical phase-narrative or a diagram shape — recorded, not restored) |
| 2 | `rationale_requiring_verification` → resolved via `knowledge/DECISIONS.md` |
| 0 | left as an open question |

## Detail

### 1. Overview pipeline diagram (legacy lines 5–33) — `obsolete`

The legacy ASCII diagram depicts a strictly linear
`loader → parser → models → commodity_style → checks → reports → cli →
_pandas_compat` sequence, with `_pandas_compat.py` drawn as a terminal
pipeline stage. This is superseded by the clean-room draft's diagram
(§1), which the legacy doc's *own* later prose already half-contradicts
(it says query/ "sits alongside this pipeline rather than strictly
within its linear flow" — true also of `tags.py` and
`commodity_style.py`, which the old diagram still drew as sequential).
The draft's non-linear diagram — `tags.py`/`commodity_style.py`/`query/`
as siblings reading `models.py`'s output, feeding `checks.py` →
`reports.py` → `{cli.py, writer.py}`, with `editor_model.py` as a
separate leaf — is independently grounded in
`journal-parsing@v1#journal-parsing-010`, `commodity-styling@v1#commodity-styling-005`,
`query-engine@v1#query-engine-001`, `checks@v1#checks-001`,
`reports-cli@v1#reports-cli-004`, `editor-surface@v1#editor-surface-001/005`.
`_pandas_compat.py` is not a pipeline "stage" at all (confirmed by
grep: imported only by `models.py` and `reports.py` at the specific
call sites that need an optional DataFrame export — `ledgerkit/
models.py:479-493`, `ledgerkit/reports.py`'s dataframe-returning
wrappers); recorded as the correct framing, not restored as a pipeline
stage.

### 2. "query/ (Stage C)" narrative (legacy lines 35–64) — content `supported`, framing `obsolete`

The underlying facts (QueryPlan bundling `predicate` + `depth`; private
`_query_ast`/`_query_depth` parameters; `print` never reading `plan.depth`;
`query/` importing only `models.py` and, since the tag-matching addition,
`tags.py`) are true and independently corroborated:
`query-engine@v1#query-engine-001/003/004/014`,
`reports-cli@v1#reports-cli-009`, and `knowledge/DECISIONS.md`'s
2026-09-16 and 2026-09-17 (×3) entries. The "Stage C Phase N" historical
narration is the thing that's `obsolete` as a *current-truth* framing
device — per `11-documentation-lifecycle.md` §11.2, decision history
belongs in `knowledge/DECISIONS.md` and `dev-docs/planning/`, not
restated as phase-by-phase narrative in architecture.md. The clean-room
draft's §6 and its "Cross-cutting structural notes" §13 already state
the same current facts without the phase framing; folded in as-is plus
a "Related design documents" pointer to `21-stage-c-phase-5-depth-and-
verification-plan.md` for readers who want the history.

### 3. "Stage C Phase 6" tag-query block (legacy lines 66–89) — content `supported`, framing `obsolete`

Corroborated by `query-engine@v1#query-engine-004/010/011` (all
`aligned`) and `knowledge/DECISIONS.md` 2026-09-25 (×2: the "complete
four-source effective-tag semantics" decision and the
`accounts -q "tag:X"` narrower-visibility decision). Already present in
the draft's §4 (`tags.py`) and §6 (`eval.py` bullet). Phase-narrative
framing dropped; design-doc pointers (`23-tag-query-matching-design.md`,
`24-tag-query-matching-implementation-plan.md`) retained as a "see also".

### 4. `ledgerkit/tags.py` responsibility block (legacy lines 91–107) — `supported`

Corroborated by `tags@v1#tags-001/008` (`aligned`). Already present,
more precisely, in the draft's §4. No new content needed; phase labels
dropped.

### 5. "Stage C Phase 6" four private helpers (legacy lines 109–124) — `supported`

Corroborated by `tags@v1#tags-001/002/003` (`aligned`). Already present
in the draft's §4. No new content needed.

### 6. "Stage C Phase 8" query-shim-convergence block (legacy lines 126–139) — `supported`

Corroborated by `query-engine@v1#query-engine-015` (`aligned`). Already
present in the draft's §6 (`compat.py` bullet) and §13. Design-doc
pointer (`27-query-shim-convergence-design.md`) retained.

### 7. "One canonical evaluation path, plus exactly one named exception" (legacy lines 141–161) — `supported`, newly re-grounded and folded in

This specific, granular claim (seven `Query`-shaped call sites unified
onto `ledgerkit.query.eval`; `ReportSection.accounts`/`.exclude` as the
one remaining exception, itself now routed through
`ledgerkit.query.regex.compile_hledger_regex`; `_posting_matches`
retired with zero remaining callers) is **not** explicitly restated in
the clean-room draft's reports.py section (§9), which focuses on
report-return-shape claims instead. It is still true as of this
reconciliation — re-grounded directly, since no Phase 3 topic's
assertion set covers this specific enumeration:
- `ledgerkit/reports.py:32` imports `compile_hledger_regex`; `reports.py:213-239`'s
  `_matches_pattern` calls it; `reports.py:621-667` is the
  `ReportSection.accounts`/`.exclude` evaluation that is the sole
  remaining caller of `_matches_pattern`.
- `_posting_matches` has zero remaining references in `ledgerkit/` (grep
  confirms), and `tests/test_reports.py:139-160`'s
  `test_posting_matches_has_zero_remaining_callers`-style test
  (`Stage C Phase 8 (§5.1d): _posting_matches must have zero remaining
  callers`) mechanically enforces this.
- `ledgerkit/models.py:479-493`'s `Journal.to_dataframe` docstring
  confirms it now goes through `ledgerkit.query.compat._query_to_ast` +
  `ledgerkit.query.eval.matches_posting`, "the same canonical path
  balance()/register()/accounts()/stats() use."

Folded into the merged reports.py section with these citations plus
`query-engine@v1#query-engine-015`.

### 8. Breaking-changes disclosure note (legacy lines 163–169) — `supported`, retained as a pointer only

The `Query.account`/`.not_account`/`.payee` behaviour-change disclosure
and its pointers to `dev-docs/versioning.md` and `dev-docs/api-spec.md`
remain accurate (`query-engine@v1#query-engine-015` covers the
`compat.py` field-translation mechanics the disclosure describes).
Retained as a short cross-reference rather than the full six-point
enumeration, which belongs in `api-spec.md` per the Documentation Sync
Rules table (public-signature changes → `api-spec.md`), not duplicated
here.

### 9. `ledgerkit/loader.py` section (legacy lines 175–196) — `stale_or_contradicted` (incomplete)

Missing `parse_string_lenient` entirely — the legacy text says
`load_journal` calls into the parser but doesn't name which entry
point(s); separately, the legacy parser.py section (next item) actively
asserts there is only one. Superseded by the draft's §8, which correctly
states `loader.py` calls `parse_string`/`parse_string_lenient`
(`loader@v1#loader-001/005/008`). Also missing: the diamond-include
silent-duplication gap (`loader@v1#loader-004`, `partial` in the
comparison but the *existence* of the gap is `aligned`) and the
`line_map`/error-reattribution mechanism (`loader@v1#loader-008`). The
`loader-002/003/007` comparison `partial`s (an untested bracket-in-
directory-name `IndexError` sub-claim) do not surface as an architecture-
level claim in either document and are not folded in — that is
edge-case material for `knowledge/EDGE_CASES.md`, outside this doc's
scope and outside this role's write boundary for that file.

### 10. `ledgerkit/parser.py` section (legacy lines 198–216) — `stale_or_contradicted`

Directly contradicted by current source: the legacy text states
`parse_string(text)` is "the sole public function," but
`ledgerkit/parser.py:1668` (`parse_string`) and `:1691`
(`parse_string_lenient`) are **both** public and both exported from
`ledgerkit/__init__.py` (confirmed by grep: `from ledgerkit.parser import
parse_string_lenient, resolve_elision`, both listed in `__all__`).
`resolve_elision` (`ledgerkit/parser.py:816`) is also public and exported,
and is not mentioned at all in the legacy section. This is exactly the
kind of claim the brief requires rewriting, not annotating. Superseded
by the draft's §2, corroborated by `journal-parsing@v1#journal-parsing-005/008`
(the latter `partial` — the "never raises" framing for lenient mode has a
confirmed, narrower exception the draft already discloses).

### 11. `ledgerkit/models.py` section (legacy lines 218–235) — `stale_or_contradicted` (incomplete)

Lists only `Amount`, `Posting`, `Transaction`, `Journal`. Missing
`BalanceAssertion`, `SourceSpan`, `Query`, `RegisterRow`, `BalanceRow`,
`ReportSection`, `ReportSpec`, `ReportSectionResult`, and the
`Journal.commodity_styles` computed property — all present and
corroborated in the draft's §3 (`commodity-styling@v1#commodity-styling-005/008`,
`journal-parsing@v1#journal-parsing-010`). Superseded by the draft.

### 12. `ledgerkit/checks.py` section (legacy lines 237–247) — `stale_or_contradicted`

Omits `check_parseable` and `check_assertions` entirely (confirmed
present in `ledgerkit/checks.py` at lines 63 and 414 respectively, and
exported) and omits the three fixed tiers
(`BASIC_CHECK_NAMES`/`STRICT_CHECK_NAMES`/`OTHER_CHECK_NAMES`,
`ledgerkit/checks.py:27-29`) and `ALL_CHECK_NAMES`. The legacy list of
"individual check functions" is materially incomplete, not merely
missing a detail. Superseded by the draft's §7, corroborated by
`checks@v1#checks-001` through `-008` (`checks-008` is `partial` — the
`run_checks` skip/names interaction gap — already disclosed in the
draft's prose rather than silently upgraded to a clean guarantee).

### 13. `ledgerkit/reports.py` section (legacy lines 249–267) — `supported`, superseded in presentation

The report-function inventory is still accurate but the draft's §9 is
more complete (adds the `stats()` depth-exclusion quirk and the
`balance_from_spec` CLI-wiring gap, both `reports-cli@v1#reports-cli-012/013`,
`aligned`/`boundary`). Folded in via the draft, plus item 7 above.

### 14. `ledgerkit/cli.py` section (legacy lines 269–286) — `supported`, superseded in presentation

Corroborated by `reports-cli@v1#reports-cli-001/002/003/005/007/009/015`
(all `aligned`). The draft's §10 is more precise (flat `argparse`
structure with no subparsers, independently corroborated by a live
`--help` run under `current-state@v1#current-state-004/005`). Folded in
via the draft.

### 15. Error Handling Strategy table (legacy lines 289–298) — `supported`, re-grounded and retained

Not present in the clean-room draft at all (out of the ten bounded
topics' scope as a standalone artefact), but still independently true,
re-grounded directly:
- `loader` → `ParseError`/`FileNotFoundError`: `loader@v1#loader-001/008`.
- `parser` → `ParseError` with line number: `journal-parsing@v1#journal-parsing-008`,
  plus direct confirmation (`ledgerkit/parser.py:79` `class ParseError(ValueError)`,
  multiple `raise ParseError(..., lineno)` call sites).
- `checks` → returns `list[CheckError]`, never raises: `checks@v1#checks-001`.
- `reports` → the legacy table's bare "`ValueError`, raised for invalid
  arguments" is itself slightly imprecise and corrected on reconciliation:
  direct grep of `ledgerkit/reports.py` finds **no** `raise ValueError`
  of its own; invalid-query errors now surface as `QueryParseError`
  (`ledgerkit/query/parser.py:41`, a `ValueError` subclass) raised from
  `ledgerkit.query.compat._validated` during the `_query_to_ast`
  translation step, and a `Tag`-node-without-`journal` error raises a
  bare `ValueError` from `ledgerkit.query.eval`
  (`query-engine@v1#query-engine-004`). Table row reworded accordingly
  rather than restated as-is.
- `cli` → catches broadly and prints to stderr, exit 1: directly
  confirmed (`ledgerkit/cli.py:216-219`, `:263`, `:274`, `:289`, `:494-498`).

### 16. Design Principles section (legacy lines 302–319) — mixed

- "Each module imports only from modules below it... (`cli` → `loader` →
  `parser`/`models`; `cli` → `checks` → `models`; `reports` → `models`)"
  — **`stale_or_contradicted`** as stated: it predates `tags.py`,
  `commodity_style.py`, `query/`, `writer.py`, and `editor_model.py`, and
  doesn't mention `reports.py`'s and `cli.py`'s imports of the `query`
  subpackage. Rewritten to point at the merged doc's own (far more
  precise) per-module Dependencies subsections instead of restating a
  three-item list that no longer covers the real import graph.
- "No circular imports" — **`supported`**, re-grounded: every per-module
  Dependencies subsection in the draft independently confirms this
  (`tags@v1#tags-001`'s `TYPE_CHECKING`-only reference to `models.py`;
  `query-engine@v1#query-engine-015`'s `compat.py` avoiding a runtime
  import of `models.py` for the same reason), and no module reachable
  from `cli.py`/`reports.py` imports back "up" into either.
- "No global mutable state" — **`rationale_requiring_verification`** →
  resolved by direct check rather than by `knowledge/*.md` (no existing
  entry addresses this specific claim): grepped every module-level
  assignment in `ledgerkit/*.py` and `ledgerkit/query/*.py`; all are
  compiled regexes, tuples, frozensets, dicts used read-only, or
  `__all__` lists — no module-level container is ever mutated after
  import. `cli.py`'s one scalar module-level value
  (`_PROGRAM_START = time.perf_counter()`) is set once at import time and
  only ever read afterward, not mutated. Confirmed true; retained.
- The `compare=` dataclass-field convention and its pointer to
  `16-model-review.md` §16.4 — **`supported`**, re-grounded directly
  against `ledgerkit/models.py:29,79,84,103-105` (the `compare=False`
  fields on `Amount`/`Posting`/`Transaction`, and the inline comment at
  `models.py:84` stating the deliberate `compare=True` default for
  accounting-meaningful fields). `16-model-review.md` confirmed to exist
  in `dev-docs/planning/core-redefinition/`. Retained as-is.

## Citation-preservation check

Every `<topic>@v1#<id>` citation carried over from the clean-room draft
into the merged `dev-docs/architecture.md` was checked, point-by-point,
against the draft's own text to confirm it survived the merge
unmodified in both target and surrounding claim. No citation was dropped
while its accompanying prose was kept; no prose was kept with its
citation silently removed.

## Open questions

None left open. The two `rationale_requiring_verification` items (import
layering, no-global-mutable-state) were resolved by direct, cited
source inspection rather than left pending, since no `knowledge/*.md`
entry addressed either and both were quick to verify conclusively.

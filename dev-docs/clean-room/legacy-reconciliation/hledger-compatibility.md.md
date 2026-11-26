# Legacy reconciliation: `dev-docs/hledger-compatibility.md`

- **Mode:** Plan 29 §6 Legacy Reconciliation (dispatched for Plan 29
  Phase 5, specifically §6.3 — "reconciliation-only" document, no
  parallel Phase 4 clean-room draft exists for this doc).
- **Date:** 2026-11-14
- **Target:** `dev-docs/hledger-compatibility.md` (real, existing, hand-authored
  narrative doc — 346 lines before this pass).
- **Evidence consulted:** `dev-docs/compat-register/*.yaml` +
  `schema.md`; `dev-docs/clean-room/snapshots/compat-system-v1.*`,
  `dev-docs/clean-room/assertions/compat-system/*.md`,
  `implementation-reconstruction/compat-system.md`,
  `implementation-comparison/compat-system.md`; the same four artefact
  types for `journal-parsing`, `commodity-styling`, `query-engine`,
  `tags`, `loader`, and `checks`; `knowledge/DECISIONS.md`,
  `knowledge/EDGE_CASES.md`; direct live execution of `ledgerkit.parser`/
  `ledgerkit.loader` in this checkout (not restricted by any Phase 3
  dispatch's evidence-path limits, since this is ordinary docs-maintainer
  work, not a model-blind reconstruction).

## Method

The existing document's structure is preserved throughout — this is
reconciliation, not a blind redraft (per §6.3). Every claim-bearing
row/paragraph was checked against: (a) the compat-register entry it
names, read directly (not just its `kind`/`status` field — the
`evidence:`/`reason:`/`tests:` fields were read); (b) the relevant
topic's Phase 3 assertion + implementation-reconstruction +
implementation-comparison artefacts, where the claim concerns parsing/
query/tag/directive/loader/check behaviour; (c) where (a) and (b) left a
claim unconfirmed either way, direct live execution against
`ledgerkit/` in this checkout.

## Classification summary

| Classification | Count | Notes |
|---|---|---|
| `supported` | ~38 claim-groups | Traces to a specific Phase 3 assertion (or compat-register executable/manual evidence, or direct live re-execution in this pass) whose own evidence checked it directly — see per-section table below. |
| `stale_or_contradicted` | 2 | Balance-assignment-elision paragraph; "Circular includes raise `ParseError`" (self-include exception). Both fixed in the published doc. |
| `rationale_requiring_verification` | 1 | `knowledge/DECISIONS.md`'s 2026-05-03 "Balance assignments deferred" entry — checked against live code, found **not** to match current behaviour (see below). Resolved (found false), not left open. |
| `useful_example` | 0 | No example worth re-grounding and folding in beyond what was already present. |
| `obsolete` | 0 | Nothing in the current doc describes a feature/state no longer present at all (the closest candidates — directive-mid-open-transaction data loss, alias-backreference crash, loader bracket-directory `IndexError` — are newly-discovered gaps, not stale claims about something removed; see "Not folded in" below). |
| **Flagged for `compat-differential-tester` re-check** | 2 | `LK-COMPAT-PARSER-TAG-001`/`LK-COMPAT-PARSER-TAG-SCOPE-001`'s broken `TestParseTags` test citation; `LK-COMPAT-INCLUDE-001` (still `status: proposed`, `evidence: manual` only) now needs re-verification covering the two newly-found loader defects below. |

## Per-section findings

### Supported (no change needed, re-verified against primary evidence)

| Doc section | Verified against | Outcome |
|---|---|---|
| Supported File Formats / Deviation table | loader topic (format-prefix/extension rejection confirmed `ParseError` via loader-007, reviewer-verified by direct execution) | supported |
| Transaction Block Structure (delimiter rules, two-space separator, one-elision-max) | journal-parsing-001/003/005/006 — all `aligned` in comparison | supported |
| Transactions / Account Names / Amounts tables | journal-parsing-001/002/003/004 — all `aligned`; several amount-form edge cases (scientific notation, space-groups, quoted suffix, cost/lot stripping order) confirmed by journal-parsing-009 (`aligned` on the composability claim itself) | supported |
| Comments (three forms, `#` never inline, block comment) | journal-parsing-006 — `aligned`, reconstruction independently read the full T/B/I/F/S-series tests | supported |
| Directives table (`P`, `alias`, `include`, `account`, `commodity`, `payee`, `tag`, `decimal-mark`, `Y`, `D`, `apply account`) — directive inventory and per-directive described behaviour, *except* the two items below | journal-parsing-007 — `aligned` (directive inventory, handler existence, comment-location correction already folded into the frozen assertion) | supported |
| Tags section (all rows) | tags-001..009 — all 9 `aligned`; query-engine-004/010 — `aligned`; compat-register entries LK-COMPAT-PARSER-TAG-COMMODITY-001 (status: verified), LK-COMPAT-QUERY-TAG-* (status: verified), LK-COMPAT-PARSER-POSTINGDATE-001/DIRECTIVE-TAG-001/PARSER-TAG-001/PARSER-TAG-SCOPE-001 (status: self-verified) all read directly and confirmed current | supported (see flagged citation defect below — doesn't invalidate the behaviour claim, since each entry's executable evidence item is a separate ad hoc hledger-binary comparison, not solely the broken test citation) |
| Validation / Checks table | checks-001 through checks-007 — `aligned`; checks-008's asymmetry (partial) concerns CLI `skip`/`names` wiring, not anything this doc currently claims | supported |
| Balance assertions (the four `=`/`==`/`=*`/`==*` syntaxes, date-order checking) | checks-006 — `aligned` (running per-account-per-commodity balance, sort key, multi-error-per-posting) | supported |
| Query Language section (all rows and the regex-dialect paragraph) | query-engine-001 through -015 — all 15 `aligned`; compat-register status fields for every cited `LK-COMPAT-QUERY-*`/`LK-MISMATCH-QUERY-*` id read directly and match the doc's own stated status exactly (self-verified vs. verified, verified_by text) | supported |
| Out of Scope / Undecided / Compatibility Notes | No topic's evidence contradicts any of these (auto-postings/periodic skip-with-warning confirmed by journal-parsing's own §7 point 4 as "a disclosed deferral, not a gap"; virtual postings `ParseError` consistent with `knowledge/EDGE_CASES.md`'s own virtual-posting entry) | supported |
| Compat-register intro paragraph ("remains the primary reference until every row has a `status: final` entry") | compat-system-002/004 + reconstruction §3: 0 of 49 live entries are `status: final` — statement remains accurate, nothing to cross-link yet | supported |

### `stale_or_contradicted` — fixed in the published doc

**1. "Balance assignments" paragraph (old `## In Scope (v1)` → `### Balance assertions`).**

Old claim: "`= EXPECTED` with no explicit posting amount) are parsed — the
posting amount is stored as `None`... known limitation deferred to a
future milestone."

This traces to `knowledge/DECISIONS.md`'s 2026-05-03 "Balance assignments
deferred" entry, which states the *intended* design ("stores
`posting.amount = None`... rejected raising a `ParseError`"). That
decision's rationale is exactly the `rationale_requiring_verification`
case this mode exists to catch: checking it against the actual code (not
just against the matching old-doc prose, which only echoes the same
decision without re-checking it) shows the decision was **never actually
implemented this way**, and `journal-parsing-009`'s own resolved Open
Question (reviewer-verified 2026-10-02 by direct execution) already found
this independently:

- `ledgerkit/parser.py`'s `_ASSERTION_MARKER_RE` requires whitespace
  *before* the marker (`\s+(==\*|==|=\*|=)\s+`) — a leading `=` at the
  very start of the amount token never matches, by design (the code's
  own comment at parser.py:670-672 says so).
- Re-verified directly in this pass: `parse_string('2024-01-01 Buy\n
  assets:cash  = $500\n    assets:other\n')` raises `ParseError: invalid
  amount: '= $500'` — not a clean `None`-amount posting.
- The implementation-reconstruction report for `journal-parsing` (§7
  item 3) additionally found, and this pass independently re-confirmed
  live, a **second, worse** failure mode for the suffix-commodity +
  comma-decimal-mode case (`decimal-mark ,` then `a  = 100,00 EUR`):
  silent corruption, not an error — `Posting.amount` becomes
  `Amount(quantity=Decimal('100.00'), commodity='=')` with
  `balance_assertion` left `None`, no error, no warning.

Fixed: the doc now states the verified current behaviour (not-implemented,
two different failure modes depending on commodity form) instead of the
stale, never-actually-true "parsed cleanly as `None`" claim.

**2. "Circular includes raise `ParseError`." (Directives table, `include` row).**

Re-verified directly in this pass: a genuine two-file mutual cycle (`a.journal`
includes `b.journal` includes `a.journal`) does raise `ParseError: circular
include detected: ...` exactly as documented. But a **literal self-include**
(a file including itself by name) is a degenerate one-file cycle that takes
a different code path: `_expand_includes`'s self-filter
(`targets = [t for t in targets if t != file_path]`) removes the target
*before* the ancestor-stack cycle check ever runs, so `targets` becomes
empty and the non-glob branch raises `FileNotFoundError` naming a path
that demonstrably exists — not `ParseError`. Re-verified directly in this
pass (not just cited from `loader-003`'s own reviewer-verified Counterexample):
a temp file containing `include <itself>` raises exactly this misleading
`FileNotFoundError`. Fixed: the doc's blanket claim now carries this
documented exception.

**Also added** (new information, not a correction of an existing false
claim, but a gap in an otherwise-exhaustive error-behaviour inventory for
this same directive): a confirmed, uncaught `IndexError` crash when any
*ancestor directory* in an include target's resolved path (not the
target filename itself) contains a glob metacharacter (`*`, `?`, `[`) —
re-verified directly in this pass (`include foo.journal` inside a
directory literally named `inc[1]`, where the target genuinely exists,
raises `IndexError: list index out of range`). This is `loader-002`/
`-003`/`-007`'s shared "newly-found during review, escalated to lead"
finding, independently re-confirmed by direct execution in this pass
rather than taken on the assertions' word alone.

### `rationale_requiring_verification` — resolved

`knowledge/DECISIONS.md`'s 2026-05-03 "Balance assignments deferred"
entry's stated rationale ("stores `posting.amount = None`... rejected
raising a `ParseError`, too strict") does **not** match the as-built
code, as shown above. This is not an open question — it is resolved
(found false) by direct execution, folded into the doc's fix above. It is
flagged here for the lead/knowledge-base owner because `knowledge/
DECISIONS.md` itself is outside this role's write boundary and now
contains a decision whose own description of the implementation no
longer (or never did) match reality.

### Flagged for a future `compat-differential-tester` re-check (not performed by this role)

1. **`LK-COMPAT-PARSER-TAG-001.yaml` and `LK-COMPAT-PARSER-TAG-SCOPE-001.yaml`**
   each cite a test class, `tests/test_tags.py::TestParseTags` (and, for the
   second entry, `::test_multiline_comment`), that does not exist anywhere in
   `tests/test_tags.py` — independently found by the `compat-system`
   implementation-reconstruction (§7, §8 item 2) and re-confirmed directly in
   this pass (`grep -n "^class " tests/test_tags.py` lists
   `TestBasicTags`/`TestNameDelimiting`/`TestValueHandling`/
   `TestMultipleValuesPerName`/`TestMultiLineComments`/`TestEffectiveDate`/
   `TestEffectiveDate2`/`TestInheritedAccountTags`/`TestPostingCommodities`/
   `TestCommodityTags`/`TestEffectiveTags`/`TestAccountsEffectiveTags` — no
   `TestParseTags`; a repo-wide `grep -rn "ParseTags" tests/` finds zero hits).
   This does **not** itself falsify the two entries' compatibility claims —
   each entry's `evidence:` field also lists a separate `kind: executable`
   ad hoc fixture-vs-real-`hledger` comparison, independent of the broken
   `tests:` citation — but the citation itself is simply wrong as filed and
   needs either a corrected test reference or confirmation that the class
   was renamed/moved. I do not have authority to correct a compat-register
   YAML or re-run the differential check; flagging for `compat-
   differential-tester`.
2. **`LK-COMPAT-INCLUDE-001.yaml`** is still `status: proposed` with only
   `evidence: kind: manual` (a doc-link, no executable comparison against a
   real hledger binary) and its own `reason:` text does not mention either
   of the two newly-confirmed loader defects above (self-include's
   misleading `FileNotFoundError`; the bracket-containing-ancestor-directory
   `IndexError`). A targeted `compat-differential-tester` pass should (a)
   confirm hledger's own behaviour for both edge cases for comparison, and
   (b) decide whether either is a `kind: unexplained_mismatch`/new entry, or
   whether it should instead be tracked purely as a ledgerkit bug (outside
   the register's own hledger-comparison purpose) — that classification
   call is `compat-differential-tester`'s, not this role's.

### Not folded into the doc (no corresponding claim to fix)

The following newly-discovered defects, surfaced by the Phase 3/4
reconstruction-vs-assertion comparison for `journal-parsing`, do **not**
correspond to any existing sentence in `dev-docs/hledger-compatibility.md`
(the doc makes no blanket "lenient mode never raises" or
"directives are always safe mid-transaction" claim for these to
contradict), so nothing was changed for them. Recorded here only so the
finding isn't lost, per this role's instruction to flag — but not fix —
things outside its write boundary or outside this doc's own claims:

- **Alias-directive backreference crash**: `alias /(foo)/ = \2` raises an
  uncaught `re.PatternError` (not even a `ParseError`) from both
  `parse_string` and `parse_string_lenient` (journal-parsing-008, `partial`
  in comparison — a second exception to that assertion's "except one"
  count).
- **Directive-mid-open-transaction silent data loss**: an `account`/
  `commodity`/`payee`/`tag` directive appearing between two posting lines
  of a still-open transaction block silently discards every subsequent
  posting line of that block (journal-parsing-007, `partial` in
  comparison — a gap in, not a contradiction of, that assertion's
  directive-inventory claim).

These three (plus the two loader defects above) are good candidates for
new `knowledge/EDGE_CASES.md` entries and/or new compat-register
`kind: unexplained_mismatch`/bug-tracking entries — outside this role's
write boundary (`knowledge/`, `dev-docs/compat-register/`), surfaced here
for the lead to route.

## What was NOT re-verified from primary differential evidence (acknowledged gap)

Per this mode's own instruction, every material claim was checked against
either a Phase 3 topic's assertion/reconstruction/comparison artefact, the
compat-register's own `evidence:`/`reason:` fields (not just `kind`/
`status`), or direct live execution in this checkout. The one category
*not* independently re-run in this pass is hledger's own-binary behaviour
for the two newly-found loader defects (item 2 above) — confirming what
*ledgerkit* does was within this role's authority (ordinary source
reading/execution); confirming what the real pinned `hledger` binary does
for the identical inputs is `compat-differential-tester`'s job and is
explicitly left to that future dispatch rather than guessed at here.

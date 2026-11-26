---
role: domain-skeptic
mode: comparison
topic: checks
dispatch-id: plan29-phase-comparison-checks-20261114
date: 2026-11-14
---

# Implementation comparison: `checks` — snapshot `checks-v1` vs. independent reconstruction

**Inputs compared.**
- Frozen snapshot: `dev-docs/clean-room/snapshots/checks-v1.md` +
  `checks-v1.sidecar.json` (8 assertions, frozen 2026-10-02T16:50:03Z,
  repository revision `51881415a204af8908834ec602a54f6e1f67dbdd`).
- The 8 frozen assertion files under `dev-docs/clean-room/assertions/checks/`
  (checks-001 through checks-008; checks-007 and checks-008 each carry a
  prior domain-skeptic REVIEW-mode note dated 2026-10-03, already folded
  into their frozen `Statement`/`Evidence-support state` fields).
- Independent implementation-reconstruction report:
  `dev-docs/clean-room/implementation-reconstruction/checks.md` (dispatch
  `session_014zQZ8FHzgy8VTjoy79bmYm`, 2026-10-03T00:00Z approx, model-blind,
  evidence basis: `ledgerkit/checks.py` full file, `tests/test_checks/
  test_checks.py` full file, plus live `python -m ledgerkit ...` CLI runs
  — no access to the snapshot or assertions).

**Method.** Neither artefact was revised to force agreement. No source or
test file was read directly by this dispatch — comparison mode compares
the two clean-room artefacts only; all findings below rest on what each
artefact itself states.

## Classification summary

| Assertion | Kind | Classification |
|---|---|---|
| checks-001 | definition | aligned |
| checks-002 | rule | aligned |
| checks-003 | rule | aligned |
| checks-004 | rule | aligned |
| checks-005 | rule | aligned |
| checks-006 | rule | aligned |
| checks-007 | rule | aligned |
| checks-008 | state_transformation | partial |

**7 aligned / 1 partial / 0 conflicting / 0 not_implemented / 0
insufficiently_verified.**

No conflicting or not_implemented findings. One `partial` (checks-008),
detailed below — it is not a disagreement between the two artefacts, but
a difference in how far each one's own evidence reaches on the same
claim.

## Per-assertion notes

**checks-001** (three fixed tiers — `BASIC_CHECK_NAMES`,
`STRICT_CHECK_NAMES`, `OTHER_CHECK_NAMES` — closed membership,
`ALL_CHECK_NAMES` their concatenation). Reconstruction §2 independently
states the identical three tuples with identical membership and order:
`BASIC_CHECK_NAMES = ("parseable", "autobalanced", "assertions")`,
`STRICT_CHECK_NAMES = ("accounts", "commodities")`,
`OTHER_CHECK_NAMES = ("payees", "ordereddates", "uniqueleafnames")`.
Aligned.

**checks-002** (`_check_txn_balanced`'s three-way elision branch: >1
elided → single "multiple elided" error; exactly 1 elided → always `[]`
regardless of commodity count; 0 elided → per-commodity net-sum check).
Reconstruction §5 ("`check_autobalanced` / `_check_txn_balanced`")
independently describes the identical three branches, including the
exact rationale ("the elision defines the missing amount regardless of
how many commodities are present") and live-confirms the zero-elided
branch's message shape (`"not balanced — net {net:+} {commodity}"`) via
a real CLI run. Both artefacts independently flag the same scope
boundary: `resolve_elision()` (referenced only in a test comment) is not
implemented in this file and is out of permitted evidence for both — the
assertion's own "Open questions" and the reconstruction's gap #10 land on
the identical unresolved limit. Aligned.

**checks-003** (`check_accounts` stops at the first offending posting in
transaction-then-posting order, case-sensitive; empty `declared_accounts`
means everything is undeclared). Reconstruction §5 independently states
"Both [`check_accounts`, `check_commodities`] stop at the first offending
posting (transaction order, then posting order within the transaction)
and return a list of at most one `CheckError`," and live-confirms this
with a real `-s` CLI run against an undeclared account that produces
exactly one error. Aligned.

**checks-004** (`check_commodities` stops at first offender; skips
`amount is None`; the empty-string commodity symbol `""` — not a
zero-quantity test — is always exempt). Reconstruction §5 independently
states "`check_commodities` ignores any posting whose `amount is None`
and any posting whose commodity symbol is the empty string `""`," and its
gap #8 independently makes the same symbol-vs-quantity distinction the
assertion's Statement is careful to preserve ("keyed on the commodity
symbol being the exact empty string, not on the numeric quantity being
zero... a posting with a non-empty commodity symbol and a zero quantity
... is not exempt"). Aligned.

**checks-005** (strict-tier multi-line `CheckError.message` structure via
`_build_strict_context`; `caret_offset = 4` for `check_accounts`,
`caret_offset = 4 + len(posting.account) + 2` for `check_commodities`;
distinct from all other checks' single-line messages). Reconstruction §5
independently states both exact caret-offset formulas and live-runs the
CLI to capture a byte-level matching example (`Strict account checking is
enabled, and` / `account "assets:bank" has not been declared.` /
`Consider adding an account directive. Examples:` / the two example
`account` lines) that is identical to the assertion's own quoted example
block. The reconstruction additionally notes (its §5, "Caret placement is
computed, not measured") that the reconstructed line — not the real
source text — drives caret position, so formatting divergences in the
real file (alignment, inline comments) can misalign the caret from the
true column; the assertion does not claim otherwise, so this is an
elaboration, not a contradiction. Aligned.

**checks-006** (`check_assertions`'s four variants via `inclusive`/
`sole_commodity`; `(date, source_line or 0)` sort order, not parse order;
running per-account-per-commodity balance; primary mismatch and
sole-commodity violation each producing their own separate `CheckError`).
Reconstruction §5 ("`check_assertions`") independently states the
identical sort key, the identical running-balance mechanism via
`defaultdict(lambda: defaultdict(Decimal))`, the identical
`inclusive`/`sole_commodity` two-flag mapping (string-prefix match for
subtree inclusion, not a parsed hierarchy), and the identical "each
failed primary assertion and each failed sole-commodity condition each
produce their own separate CheckError" claim, including the note that a
single posting can produce more than one error. Aligned.

**checks-007** (the three "other"-tier checks: `check_payees` dedups by
description, flags unmatched descriptions once each; `check_ordereddates`
flags against a "high-water mark" `prev_date` that only advances on a
*passing* comparison, not against the literal list-previous transaction's
date; `check_uniqueleafnames` flags leaves — the substring after the last
`:` — shared by ≥2 distinct full account names). Reconstruction §5
independently states the identical `check_ordereddates` mechanism: "on a
flagged out-of-order transaction, `prev_date` is *not* updated... the
comparison baseline for the next transaction remains the last transaction
that passed, not the actual chronological previous transaction" — the
same high-water-mark behaviour this assertion's own domain-skeptic REVIEW
note (2026-10-03) corrected from an earlier, looser "immediately
preceding transaction" wording. The reconstruction's own gap #4
independently flags the same fact as "a specific, non-obvious implemented
choice not called out anywhere in the docstring," and independently notes
"no test in this file exercises three-or-more transactions with more than
one out-of-order date" — matching the assertion's own statement that this
distinction was "previously untested, not just mis-stated" and was
confirmed instead by direct execution (both artefacts agree the test
suite itself does not cover it; neither is relying on a shared test to
settle it). `check_payees` and `check_uniqueleafnames` descriptions also
match the reconstruction's §5 ("Deduplicates by `txn.description`... the
first unmatched description... reported once" / "groups by the string
after the last `:`... reports one `CheckError` per leaf with more than
one distinct full account name"). Aligned.

**checks-008** (`run_checks`'s `already_run` set is a *static tier-name-
set union*, not a record of actual execution — so a name that is both
`skip`-suppressed in its own tier and re-requested via `names` executes
*zero* times, not once; and the strict-tier branch inside `run_checks`
does not apply `skip` at all, so a name in both `skip` and
`STRICT_CHECK_NAMES` still runs when `strict=True`). **Partial.** The
reconstruction's §2 independently states the coarser-grained version of
this claim that both artefacts agree on: `run_checks` "tracks an
`already_run` set so a check named explicitly that is also in basic/
strict is not run (and its errors not duplicated)" — this top-level
dedup/no-double-execution behaviour, and the "validate `names` against
`_CHECK_FN` up front, raising `ValueError`" behaviour, match the
assertion's Evidence paragraph exactly, with no disagreement. Where the
two diverge is in reach, not content: the assertion's Statement (as
corrected by this role's own prior REVIEW-mode note, 2026-10-03) adds two
sharper, directly-executed sub-claims — the skip+names zero-execution
combination, and the strict-tier skip asymmetry *within `run_checks`
itself* — neither of which the reconstruction's evidence addresses for
`run_checks`. The reconstruction does independently describe a
structurally analogous asymmetry, but for a *different* function,
`run_strict_checks` (its gap #9: "`run_strict_checks`'s `skip` parameter
only ever reaches `run_basic_checks`... `STRICT_CHECK_NAMES` are then run
unconditionally afterward with no `skip` filtering"). That is consistent
in spirit with the assertion's claim about `run_checks`'s own strict
branch (604-606 per the assertion's cited evidence) not applying `skip`
either, but the reconstruction never actually tests or states this for
`run_checks` itself — only for its sibling runner. Classified `partial`
rather than `aligned` because the reconstruction's own evidence does not
reach the specific sub-claims the assertion escalates, not because
either artefact contradicts the other. The assertion's own "Open
questions" field already escalates whether either asymmetry is
intentional design or an oversight; this comparison does not resolve that
either, consistent with this mode's rule against ruling on a genuine
ambiguity.

## Verification caveat (per brief, not a finding)

Per this mode's governing rule, **alignment is not verification**. For
every `rule`-kind assertion above (checks-002 through checks-007) and the
`state_transformation`-kind checks-008, an "aligned" or "partial"
classification means only that the independently-reconstructed as-built
behaviour currently matches (or partially matches) what the snapshot
asserts — it does not, by itself, establish that the asserted rule
(e.g., "one elided posting is always balanced regardless of commodity
count," "stopping at the first undeclared account is the right
behaviour," "the high-water-mark date-ordering baseline is the intended
one") is itself the *right* behaviour relative to hledger's own
semantics. Both artefacts are explicit, in their own text, about the
limits of what they can settle: checks-002's and the reconstruction's
gap #10 agree `resolve_elision()`'s actual logic is out of scope for
both; checks-007's REVIEW note and the reconstruction's gap #4 agree the
ordereddates high-water-mark behaviour is uncovered by any existing test
and was only confirmed by direct execution in each case, independently.
This report preserves that distinction rather than collapsing "matches
the code" into "is correct."

## What was checked

- All 8 assertion `Statement`/`Evidence`/`Examples`/`Counterexamples`
  fields against the reconstruction report's §1–§7 content,
  assertion-by-assertion.
- Whether the reconstruction's own stated gaps (its §7, items 1–10)
  contradicted, narrowed, or were silent on any assertion's claim. None
  contradicted; checks-008 was found to be addressed only partially
  (reconstruction's gap #9 covers a sibling function, `run_strict_checks`,
  not `run_checks`'s own internal strict-tier/`skip` interaction that the
  assertion's reviewed Statement specifically claims).
- Whether either artefact's own escalated/open items (checks-002's and
  checks-007's "Open questions"; checks-008's explicit "ESCALATED" open
  question) were silently resolved one way or the other by the other
  artefact — they were not; the reconstruction independently lands on the
  same unresolved boundaries for checks-002 and checks-007, and is simply
  silent (neither confirming nor denying) on checks-008's specific
  escalated sub-claims for `run_checks` itself.

## Escalations

None raised by this comparison itself. checks-008's own "ESCALATED"
open question (whether the `skip`+`names`+`strict` asymmetries in
`run_checks` are intentional design or an oversight) remains open from
the snapshot's own prior REVIEW-mode pass — this comparison does not
resolve it, and notes only that the independent reconstruction's
evidence does not reach far enough to settle it either way.

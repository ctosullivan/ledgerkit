<!-- producer: assertion-research | topic: checks | dispatch: ck-dispatch-08 | date: 2026-10-02 -->
<!-- reviewed: domain-skeptic | review-dispatch: ck-dispatch-08-review | date: 2026-10-03 -->
# Assertion: checks-008

## Statement
`run_checks(journal, names=None, strict=False, skip=None)` always runs all `BASIC_CHECK_NAMES` except any present in `skip`; if `strict=True` it additionally runs all `STRICT_CHECK_NAMES` (unconditionally, not skip-filtered); then it runs every name in `names` that is not already a member of a prior tier's name-set (`BASIC_CHECK_NAMES`, plus `STRICT_CHECK_NAMES` when `strict=True`) and is not in `skip`, raising `ValueError` up front if any name in `names` is not a key of the internal `_CHECK_FN` registry (which contains exactly the 8 names across all three tiers). This produces deduplication — a name present both in `names` and in an already-run tier executes only once, PROVIDED that tier actually ran it. The `already_run` membership test (checks.py:608-610) is purely a static name-set union, not a record of what actually executed — so a `BASIC_CHECK_NAMES` (or, when `strict=True`, `STRICT_CHECK_NAMES`) member that was suppressed via `skip` is still counted as "already run" for the purposes of the final `names` loop, and therefore does NOT get a second chance to execute even when the caller explicitly lists it in `names`. In that specific combination (`skip={X}` and `names=[X]` for a basic-tier `X`, or for a strict-tier `X` when `strict=True`), `X` executes zero times, not once — the dedup described above silently becomes total suppression instead.

## Kind
state_transformation
## Basis
directly_stated
## Evidence
`run_checks` (checks.py:567-617): the `names` validation loop (596-600) raises `ValueError(f"unknown check {name!r}; available: ...")` before any check executes; `errors = run_basic_checks(journal, skip=_skip)` (602) runs basic tier with skip applied; strict tier (604-606) is added unconditionally when `strict=True` (skip is NOT passed to this loop); the `already_run` set (608-610) is built as `set(BASIC_CHECK_NAMES)` unioned with `set(STRICT_CHECK_NAMES)` when `strict=True` — this is a static tuple union, independent of whether `skip` actually suppressed execution of any of those names; the final loop (612-615) only runs names not already in `already_run` and not in `_skip`.

Evidence-paths: [ledgerkit/checks.py:523-617, tests/test_checks/test_checks.py:361-406]

## Justification
`test_run_checks_unknown_name_raises` (361-364) confirms the upfront validation. `test_run_checks_dedup_when_also_in_strict` (397-406) passes `names=["accounts"], strict=True` and asserts each distinct account-error message's count is exactly 1 (not 2), directly confirming no double-execution of "accounts" despite it being both explicitly named and part of the strict tier. `test_run_basic_checks_skip_assertions` (366-376) confirms `skip=frozenset({"assertions"})` suppresses assertions-tier errors from `run_basic_checks` while an unskipped call still reports them. No existing test combines `names` and `skip` on the same check name, which is why the zero-executions case below needed direct verification rather than a citable test.

REVIEW NOTE (domain-skeptic, 2026-10-03): I verified the zero-executions case by direct execution against the permitted evidence path `ledgerkit/checks.py` (no test file edits). `run_checks(j, names=["assertions"], skip=frozenset({"assertions"}))` on a journal with a failing balance assertion returns `[]` — "assertions" is silently never run, even though it was explicitly requested via `names`, because `already_run` contains "assertions" unconditionally (it is a `BASIC_CHECK_NAMES` member) regardless of `skip`. The Statement has been corrected to describe this precisely; previously it said the final loop runs names "not already executed in a prior tier", which is not what the code checks (it checks prior-tier *membership*, not actual execution) — a subtle but load-bearing difference now made explicit.

## Examples
`test_run_checks_with_other_check` (382-395): `run_checks(j, names=["ordereddates"])` with no `strict` runs basic tier (default, unskipped) plus "ordereddates" from the other tier, confirmed present in the combined error list.

Direct execution: `run_checks(j, names=["assertions"], skip=frozenset({"assertions"}))` against a journal with a failing balance assertion returns `[]` (zero errors) — confirming the membership-vs-execution distinction above.

## Counterexamples
None found contradicting the dedup/skip logic as now described; note that `skip` is explicitly documented and coded to apply only within `run_basic_checks`'s own basic-tier call — the strict-tier loop at 604-606 does not reference `_skip` at all, meaning a name in both `skip` and `STRICT_CHECK_NAMES` would still run if `strict=True` (this is the opposite failure mode from the zero-executions case above: here skip is ignored and the check runs anyway, confirmed directly: `run_checks(j, strict=True, skip=frozenset({"accounts"}))` on an undeclared-account journal still reports an "accounts" error). This is an asymmetry directly observable in the code but not explicitly called out in the docstring.

## Depends on
checks-001 (tier membership), checks-003/checks-004 (strict checks it may dispatch to).

## Open questions
ESCALATED (domain-skeptic, 2026-10-03): whether either asymmetry — (a) `skip` not being honored for the strict-tier branch within `run_checks` (lines 604-606), so a strict-tier name in both `skip` and `STRICT_CHECK_NAMES` still runs when `strict=True`; and (b) a basic/strict-tier name that is both `skip`-suppressed and explicitly re-requested via `names` executing zero times instead of once — is intentional design or an oversight is not resolvable from `ledgerkit/checks.py` or `tests/test_checks/` alone. Both behaviors are confirmed, reproducible facts about the current code (verified directly during this review, see REVIEW NOTEs above), but no docstring, comment, or test in the permitted evidence states an intended `skip`+`names`+`strict` interaction to compare them against. This is left open for the lead; it should not be resolved by guessing either way.

## Evidence-support state
partially_supported
## Status
supported
## Supersedes
None

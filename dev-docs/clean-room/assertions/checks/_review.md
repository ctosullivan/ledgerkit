<!-- producer: domain-skeptic | mode: REVIEW | topic: checks | date: 2026-10-03 -->
# Review note: checks-001 .. checks-008

## Scope / permitted evidence
Reviewed against the same permitted-evidence-paths list the assertion-research
dispatch used: `ledgerkit/checks.py` and `tests/test_checks/` only. No other
file (no legacy docs, no `tests/fixtures/*.journal` contents, no `cli.py`) was
opened. All checks below were performed by reading `ledgerkit/checks.py` and
`tests/test_checks/test_checks.py` directly, and by running small snippets
against `ledgerkit.checks`/`ledgerkit.models`/`ledgerkit.parser` in-process
(no test files were created, edited, or executed as a suite — only ad hoc
expressions against the same production code already in the permitted-evidence
set).

## What I checked
- Every `Evidence-paths` citation in all 8 files against the actual line
  numbers in `ledgerkit/checks.py` and `tests/test_checks/test_checks.py` —
  re-read the cited ranges myself rather than trusting the assertion's own
  description of them.
- Every assertion's `Statement` against the actual code behaviour (not just
  the docstring), including deliberately hunting for inputs that satisfy the
  assertion's stated trigger condition but that the code might handle
  differently (per the REVIEW-mode brief's "X always does Y" edge-case
  instruction).
- Cross-file contradictions (tier membership consistency across checks-001
  and checks-008; shared formatting helper consistency across checks-003/004
  and checks-005).
- Whether `Evidence-support state` was being used honestly, in particular
  whether any `supported` should actually be `uncertain`, and whether
  checks-008's existing `partially_supported` + open-question framing was
  itself still accurate once I'd verified the underlying code myself.

## What I found and fixed

### checks-007 — `check_ordereddates` mischaracterised in `Statement`
The original `Statement` said the check "flags any transaction whose date is
strictly less than the **immediately preceding (in list order)** transaction's
date." That directly contradicts the same assertion's own `Evidence`
paragraph, which (correctly) already said `prev_date` is updated "only when
not out-of-order" — the `Statement` silently dropped that qualifier when
restating it in plain language. This is a real behavioural difference, not
just a wording nuance: I ran `check_ordereddates` on three transactions dated
2024-01-10, 2024-01-05, 2024-01-07 (in that list order). Under the
"immediately preceding" reading, the third transaction (01-07) should pass,
since 01-07 > 01-05 (its literal predecessor). Instead both the second and
third transactions are flagged, each against "2024-01-10" — confirming the
comparison is against a running high-water mark (`prev_date` only advances on
a non-violating transaction), not the literal preceding transaction. I
rewrote the `Statement` and `Evidence` to state this precisely, and added the
reproduction as a new `Examples` entry, flagged as verified by direct
execution rather than by an existing named test (no test in
`tests/test_checks/test_checks.py` currently exercises a 3-transaction
sequence of this shape). `Evidence-support state` stays `supported` — the
corrected statement is now fully backed by evidence; it was the *previous*
wording that was unsupported, not the underlying check itself. File edited
in place; a `<!-- reviewed -->` marker and a REVIEW NOTE paragraph record what
changed and why, so the fix is auditable rather than silent.

### checks-008 — `Statement` said "not already executed," code checks "not already a tier member" (these differ)
The original `Statement` said `run_checks`'s final loop runs every name in
`names` that was "not already **executed** in a prior tier." That's not what
`already_run` (checks.py:608-610) actually tracks: it's a static union of
`BASIC_CHECK_NAMES` (and `STRICT_CHECK_NAMES` when `strict=True`), built
unconditionally — not a record of what the earlier tier calls actually ran.
I verified this produces a real, distinct consequence beyond the asymmetry
the assertion had already flagged (skip being ignored by the strict-tier
loop): `run_checks(j, names=["assertions"], skip=frozenset({"assertions"}))`
on a journal with a failing balance assertion returns `[]` — "assertions" is
a `BASIC_CHECK_NAMES` member, so it's in `already_run` regardless of whether
`skip` actually suppressed it, and therefore the explicit `names` request
never gets a second chance to run it. This is the *opposite* failure mode
from the one the assertion already named (strict tier ignoring skip and
running anyway) — here, skip + an explicit same-name request in `names`
causes **zero** executions instead of the "exactly once" the original
`Statement` implied dedup always guarantees. I corrected the `Statement`,
`Evidence`, and `Examples` to describe the membership-vs-execution
distinction precisely and to include this as a second, confirmed asymmetry
alongside the first. `Evidence-support state` remains `partially_supported`
(unchanged) — the behavioural facts are now fully resolved and backed by
direct execution, but the *design-intent* question below is still genuinely
open.

## What I checked and did NOT need to fix (confirmed correct as written)
- checks-001: tier-constant membership and docstring citations verified
  against `checks.py:7-33` — accurate (one citation, `checks.py:7-11`,
  technically includes the docstring's closing `"""` on line 11 rather than
  a blank line; this is harmless over-inclusion, not a wrong citation, so I
  left it).
- checks-002: the one-elided-posting-always-balanced rule, the
  multiple-elided-fails rule, and the zero-elided-must-net-zero rule all
  match `_check_txn_balanced` exactly; all cited test line numbers verified
  against the actual file.
- checks-003 / checks-004: stop-at-first-undeclared behaviour, case
  sensitivity, and the commodity empty-string exemption all verified against
  code and tests; cited line numbers accurate.
- checks-005: the caret-offset arithmetic for both `check_accounts`
  (`caret_offset = 4`) and `check_commodities`
  (`caret_offset = 4 + len(posting.account) + 2`) matches the code exactly;
  confirmed by direct code read that every other check's `CheckError.message`
  is genuinely single-line (no other check builds multi-line messages), so
  the "distinct from all other checks" claim holds.
- checks-006: the four balance-assertion variants, the
  `(date, source_line or 0)` sort key, and the inclusive-subtree
  `startswith(prefix)` summation all verified against code and the
  `test_date_order_not_parse_order` / `test_inclusive_assertion_*` tests. Also
  independently confirmed, by grepping `ledgerkit/checks.py` for `cost` /
  `cleared` / `pending`, that `check_assertions` itself (lines 414-516) never
  references any of those fields — so the docstring's "Costs and posting
  status are ignored" claim is true by code inspection (nothing to ignore
  because nothing is ever read), not merely an untested docstring assertion.
  The already-flagged open question (fixture files outside permitted evidence
  paths) is correctly scoped and left alone.
- checks-007 (`check_uniqueleafnames` portion only): confirmed accounts with
  no colon at all (e.g. "cash") are correctly compared leaf-for-leaf against
  colon-qualified accounts (e.g. "my:cash") and correctly flagged as a
  duplicate leaf — this edge case isn't explicitly asserted as a claim in the
  Statement, but I checked it doesn't contradict anything and required no
  change.

## Escalating (genuine, unresolved ambiguity — not resolved myself)
checks-008's `Open questions` section, now covering **two** confirmed
asymmetries in `run_checks`'s `skip`/`names`/`strict` interaction:
1. A strict-tier check name present in both `skip` and `STRICT_CHECK_NAMES`
   still runs when `strict=True` (skip is not consulted by the strict-tier
   loop at checks.py:604-606).
2. A basic-tier (or, under `strict=True`, strict-tier) check name present in
   both `skip` and the explicit `names` list executes **zero** times, not
   once — `skip` suppresses the tier's own run, and the `already_run`
   membership check (based on static tier membership, not actual execution)
   then also blocks the explicit `names`-loop from running it.

Both are reproducible, verified facts about the current code (I ran both
scenarios directly). Whether either is intentional design or an oversight is
not answerable from `ledgerkit/checks.py` or `tests/test_checks/` alone —
no docstring, comment, or test states an intended `skip`+`names`+`strict`
interaction to check these against. I have not guessed at an answer and have
not changed `run_checks`'s behaviour (out of bounds for this role regardless).
This is left for the lead to decide whether it needs a design decision,
clarified docstring, or a product-level fix — none of which I can author from
inside this review.

## Files changed
- `/home/cormac/projects/ledgerkit/dev-docs/clean-room/assertions/checks/checks-007.md`
  (Statement/Evidence/Examples corrected; review note added inline)
- `/home/cormac/projects/ledgerkit/dev-docs/clean-room/assertions/checks/checks-008.md`
  (Statement/Evidence/Examples/Counterexamples/Open questions corrected and
  expanded; review note added inline)
- `/home/cormac/projects/ledgerkit/dev-docs/clean-room/assertions/checks/_review.md`
  (this file, new)

checks-001.md, checks-002.md, checks-003.md, checks-004.md, checks-005.md,
checks-006.md were read in full and checked against `ledgerkit/checks.py`
and `tests/test_checks/test_checks.py` but required no edits.

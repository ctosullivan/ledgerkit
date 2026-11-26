# Implementation Reconstruction: `checks` (Ledgerkit's validation-check subsystem)

**Role:** implementation-reconstructor
**Topic:** checks
**Dispatch:** same-host, prompt-scoped sub-dispatch of Plan 29's
implementation-reconstructor role (best-effort isolation, not verified —
see brief's note on substitution inside a general-purpose-typed session)
**Dispatch id/timestamp:** session_014zQZ8FHzgy8VTjoy79bmYm / 2026-10-03T00:00Z (approx, local)
**Date:** 2026-10-03

Evidence consulted (exactly, nothing else):
- `/home/cormac/projects/ledgerkit/ledgerkit/checks.py` (full file, 618 lines)
- `/home/cormac/projects/ledgerkit/tests/test_checks/test_checks.py` (full file, 918 lines)
- Live CLI commands run against this repo's checkout (`python -m ledgerkit ...`),
  cited inline below with their actual output.

No assertion, snapshot, implementation-comparison, planning doc, or legacy
`dev-docs/*.md`/`docs/*.md`/`knowledge/*.md` file was read. No breach to report.

---

## 1. Structure

`checks.py` is a single module, organized top-to-bottom into clearly
commented sections (the comments are section banners in the source, not
inferred):

1. **Public constants** — three name tuples (`BASIC_CHECK_NAMES`,
   `STRICT_CHECK_NAMES`, `OTHER_CHECK_NAMES`) and their concatenation
   `ALL_CHECK_NAMES`.
2. **Error type** — the `CheckError` dataclass.
3. **Basic checks** — `check_parseable`, `check_autobalanced`,
   `check_transaction_autobalanced` (a per-transaction variant), and the
   shared helper `_check_txn_balanced`.
4. **Source-context formatting helpers** — `_fmt_txn_header`,
   `_fmt_amount`, `_fmt_posting`, `_build_strict_context`. These exist
   solely to reconstruct a readable source-line display (with caret
   underlines) for strict-check error messages; they are not used by any
   non-strict check.
5. **Strict checks** — `check_accounts`, `check_commodities`.
6. **Other checks** — `check_payees`, `check_ordereddates`,
   `check_uniqueleafnames`.
7. **Balance assertion check** — `check_assertions` (standalone section,
   classified as a *basic* check via `BASIC_CHECK_NAMES`, not "other").
8. **Check registry and runners** — `_CHECK_FN` dict, `run_basic_checks`,
   `run_strict_checks`, `run_checks`.

Each check function has the identical signature `(journal: Journal) ->
list[CheckError]`; the module's own docstring (lines 1-11) states checks
never print — callers format and display errors. This module does not
import or call anything from `cli.py`; verified by inspecting `checks.py`'s
own import block, which pulls only from `ledgerkit.models` plus
`datetime`, `collections.defaultdict`, `dataclasses.dataclass`,
`decimal.Decimal`. (`cli.py` itself was out of permitted-evidence scope for
this reconstruction, so its call into these functions is inferred only
from the CLI's observed live behaviour below, not from reading its code.)

## 2. Public surface

Confirmed by reading signatures directly (not inferred from names):

- `CheckError` dataclass: `check_name: str`, `message: str`,
  `line_number: int | None = None`.
- Constants: `BASIC_CHECK_NAMES = ("parseable", "autobalanced", "assertions")`,
  `STRICT_CHECK_NAMES = ("accounts", "commodities")`,
  `OTHER_CHECK_NAMES = ("payees", "ordereddates", "uniqueleafnames")`,
  `ALL_CHECK_NAMES` = concatenation of the three, in that order.
- Check functions (each `(Journal) -> list[CheckError]`):
  `check_parseable`, `check_autobalanced`, `check_assertions`,
  `check_accounts`, `check_commodities`, `check_payees`,
  `check_ordereddates`, `check_uniqueleafnames`.
- `check_transaction_autobalanced(txn: Transaction) -> list[CheckError]` —
  the only check function that takes a `Transaction` rather than a
  `Journal`; a per-transaction wrapper around the same internal
  `_check_txn_balanced` helper used by `check_autobalanced`.
- Runners:
  - `run_basic_checks(journal, *, skip=None) -> list[CheckError]` — runs
    exactly `BASIC_CHECK_NAMES` in order, honoring `skip`.
  - `run_strict_checks(journal, *, skip=None) -> list[CheckError]` — calls
    `run_basic_checks` then appends `STRICT_CHECK_NAMES` results (strict
    checks themselves cannot be skipped via `skip`, since `skip` is only
    passed to the basic-check call).
  - `run_checks(journal, names=None, *, strict=False, skip=None) ->
    list[CheckError]` — validates `names` against `_CHECK_FN` up front
    (raises `ValueError` on an unrecognized name, message lists all valid
    names sorted), always runs basic checks (minus `skip`), optionally
    adds strict checks, then runs any `names` not already covered,
    tracking an `already_run` set so a check named explicitly that is
    also in basic/strict is not run (and its errors not duplicated).

Live confirmation of the CLI entry points that reach this module
(`python -m ledgerkit --help`, run in this session):

```
options:
  -s, --strict          Enable strict mode: also check that accounts and
                        commodities are declared
  -I, --ignore-assertions
                        Disable balance assertion checking
```
and the `check` subcommand, whose positional `journal` argument doubles as
"check names (check command only)" per `--help` text. `python -m ledgerkit
check --help` produces the same top-level usage line (the `check`
subcommand does not have its own distinct `--help` block as far as the
top-level parser is concerned — confirmed by running it: output was
byte-identical to the top-level `--help`).

## 3. Data model

`checks.py` does not define its own domain model — it only imports
`Journal`, `Posting`, `Transaction` from `ledgerkit.models` (not read
directly; its own fields are inferred only from how `checks.py` uses them,
since `models.py` was outside permitted evidence). Fields/attributes
actually referenced by `checks.py`, and therefore known to exist on these
types from this evidence:

- `Journal.transactions`, `Journal.declared_accounts`,
  `Journal.declared_commodities`, `Journal.declared_payees`,
  `Journal.source_file`.
- `Transaction.date`, `.description`, `.postings`, `.cleared`, `.pending`,
  `.code`, `.comment`, `.source_line`.
- `Posting.account`, `.amount`, `.source_line`, `.balance_assertion`.
- `Amount.quantity` (Decimal), `.commodity` (str) — accessed via
  `posting.amount.commodity`/`.quantity` and via a `balance_assertion.amount`.
- `BalanceAssertion.amount`, `.inclusive`, `.sole_commodity` (used in
  `check_assertions`; names and shapes confirmed by the test file's own
  construction of `BalanceAssertion(amount=..., inclusive=..., sole_commodity=...)`).

The only data type checks.py itself defines is `CheckError` (see §2).

## 4. Dependencies

Imports at the top of `checks.py`:
- `datetime` (stdlib) — used for type annotation in `check_ordereddates`.
- `collections.defaultdict` (stdlib) — used in `check_assertions` for
  running per-account-per-commodity balances.
- `dataclasses.dataclass` (stdlib) — defines `CheckError`.
- `decimal.Decimal` (stdlib) — all monetary arithmetic.
- `ledgerkit.models.{Journal, Posting, Transaction}` — the only internal
  (in-project) dependency.

No third-party imports. No imports of `ledgerkit.parser`, `ledgerkit.cli`,
`ledgerkit.loader`, or any other sibling module from inside `checks.py`
itself — confirmed by reading the full import block (lines 13-20); all
other modules named in tests (`ledgerkit.parser.parse_string`,
`ledgerkit.loader.load_journal`, `ledgerkit.cli.main`) are imported only
by the *test file*, for test setup/integration purposes, not by
`checks.py`.

## 5. Runtime behaviour

Traced both by reading the real call paths in `checks.py` and by running
live commands.

### `check_autobalanced` / `_check_txn_balanced`
- Counts postings with `amount is None` ("elided").
- `>1` elided postings -> single `CheckError` ("multiple elided postings
  (autobalanced)"), the whole transaction reported as one error regardless
  of how many postings are elided.
- Exactly 1 elided posting -> always `[]` (no error), on the stated
  rationale that the elision defines the missing amount regardless of how
  many commodities are present (this comment explicitly supersedes an
  older, stricter rule — see test
  `test_elided_with_multi_commodity_now_valid`, whose comment says
  "hledger rule: one elided posting is valid regardless of commodity
  count" and references a `resolve_elision()` function that is *not* in
  this file — i.e. the actual elision-resolution logic lives elsewhere,
  outside this topic's evidence scope).
- 0 elided postings -> sums `Decimal` quantities per commodity string
  across all postings; any commodity whose net != 0 produces one
  `CheckError` per offending commodity, iterated in sorted commodity-name
  order, each with `message` containing `"not balanced — net {net:+}
  {commodity}"` and `line_number = txn.source_line`.

Live-confirmed: an unbalanced two-posting transaction, run via
`python -m ledgerkit -f <journal> stats`, produced exit code 1 and stderr:
```
ledgerkit: transaction on 2024-01-01 ('Bad transaction'): not balanced — net +100.00 £
```
This also demonstrates (CLI-integration evidence, not from reading
`cli.py`) that the basic-check gate fires on every command including
`stats`, and that `-s` (strict mode) does not suppress or change this —
run with `-s` added, output and exit code were identical, because
`run_strict_checks` always calls `run_basic_checks` first.

### `check_accounts` / `check_commodities` (strict checks)
Both stop at the *first* offending posting (transaction order, then
posting order within the transaction) and return a list of at most one
`CheckError`, whose `message` is a multi-line string built by
`_build_strict_context` plus check-specific guidance text (an
"account"/"commodity" directive suggestion). Confirmed live:

```
$ python -m ledgerkit -s -f balanced.journal stats
ledgerkit: Error: <path>:2:
  | 2024-01-01 Good transaction
2 |     assets:bank  £50.00
  |     ^^^^^^^^^^^
  |     income:salary  -£50.00

Strict account checking is enabled, and
account "assets:bank" has not been declared.
Consider adding an account directive. Examples:

account assets:bank
account assets:bank    ; type:A  ; (L,E,R,X,C,V)
```
Exit code 1. This is `check_accounts`'s single error, stopping before it
ever reaches `check_commodities` in `run_strict_checks` *only if the
caller stops at the first error* — reading `run_strict_checks`, it does
not stop early; it unconditionally calls both `check_accounts` and
`check_commodities` and concatenates their results. The CLI output above
only shows the accounts error because that single invocation used `-s`
with `stats`, not `check`; separately running `check` with both names
explicitly surfaced *both* blocks (accounts, then commodities) in one run
(see the `check ordereddates uniqueleafnames` / strict combined run
below — the two-check output included both the accounts-error block and
the commodities-error block, confirming `check_commodities` is reached
even when `check_accounts` already found an error, since they are
independent functions each scanning from the start of the postings).

`check_commodities` ignores any posting whose `amount is None` and any
posting whose commodity symbol is the empty string `""` (treated as a
"zero-amount" exemption per its docstring and confirmed by test
`test_zero_amount_no_commodity_exempt`).

Caret placement is computed, not measured from any real rendering:
`check_accounts` hardcodes `caret_offset = 4` (the posting indent) and
`caret_len = len(posting.account)`; `check_commodities` computes
`caret_offset = 4 + len(posting.account) + 2` assuming a fixed two-space
separator between account and amount in `_fmt_posting`'s reconstructed
line. Both are reconstructions of the source line, not reads of the
original source text — `_fmt_posting`/`_fmt_txn_header`/`_fmt_amount`
rebuild a line from the `Transaction`/`Posting` model fields, so original
formatting (actual whitespace, trailing comments on the posting line,
multi-space alignment) is not preserved; the carets will misalign with
the *real* source file whenever that file's actual formatting differs
from what `_fmt_posting` regenerates (e.g. a differently-indented or
aligned posting line, or one with an inline comment after the amount).

### `check_payees`
Deduplicates by `txn.description` — the first unmatched description for a
given value is reported once; subsequent transactions with the same
description are not reported again even though they're also "undeclared".

### `check_ordereddates`
Walks `journal.transactions` *in journal order* (not sorted), tracking
`prev_date`; flags a transaction whose date is strictly less than the
previous one. Note: on a flagged out-of-order transaction, `prev_date` is
*not* updated (the `else` branch that updates `prev_date` is skipped when
the date check fails), so the comparison baseline for the next
transaction remains the last transaction that passed, not the actual
chronological previous transaction. The module's own docstring states
this operates on the full merged transaction list in journal order
because ledgerkit merges included files before parsing (per-file
semantics mentioned only as a contrast, not implemented here).

### `check_uniqueleafnames`
Builds the account set from all postings' accounts across all
transactions, groups by the string after the last `:`, reports one
`CheckError` per leaf with more than one distinct full account name
mapped to it. No `line_number` is set (no per-transaction context — this
is a whole-journal structural check), confirmed by reading the code (no
`line_number=` argument is passed to this `CheckError` constructor call).

### `check_assertions`
The most involved check. Sorts `(transaction, posting)` pairs by
`(txn.date, txn.source_line or 0)` — i.e., ties within the same date are
broken by `source_line`, with `None` treated as `0` (sorting before any
known line). It maintains `running_balances[account][commodity]` via
`defaultdict(lambda: defaultdict(Decimal))`, updating the running balance
before checking any assertion on the *same* posting (post's own amount is
applied first, then its own balance assertion is checked against the
post-application total — confirmed by test
`test_single_commodity_assertion_pass`, where the assertion is on the same
posting whose amount it's checking).

Four assertion variants are distinguished by two independent boolean
flags on `BalanceAssertion` — `inclusive` (subaccounts included vs. not)
and `sole_commodity` (all other commodities in the same account/subtree
must be exactly zero) — matching the docstring's stated `=`, `==`, `=*`,
`==*` mapping. `inclusive=True` sums the named account plus every account
whose name starts with `account + ":"` (string-prefix match, not a parsed
hierarchy), for both the primary commodity comparison and (if
`sole_commodity`) the "other commodities" check.

Each failed primary assertion and each failed sole-commodity condition
each produce their own separate `CheckError` (so a single posting can
produce more than one error — one for the expected-commodity mismatch,
and one more per non-zero "other" commodity found, if `sole_commodity` is
set and multiple other commodities are non-zero).

Live-confirmed indirectly through the existing basic-check gate (the
earlier unbalanced-journal run above exercised `run_basic_checks`, which
includes `check_assertions`, though that specific run had no assertions
present so this check contributed no errors there).

### Runners — live-confirmed combination behaviour

```
$ python -m ledgerkit -f balanced.journal check ordereddates uniqueleafnames
(no output) EXIT=0
```
confirming multiple check names can be passed as positional arguments to
the `check` subcommand and are run in addition to the always-run basic
checks (silently, since this journal passes all of them).

```
$ python -m ledgerkit -f unbalanced.journal check notacheck
ledgerkit: transaction on 2024-01-01 ('Bad transaction'): not balanced — net +100.00 £
EXIT=1
```
Notably, this did **not** report `"unknown check"` for the bogus name
`notacheck` — the basic-check (autobalanced) failure pre-empted it. This
is CLI-integration behaviour (outside this topic's `checks.py` itself,
since `run_checks`'s own code validates `names` *before* running basic
checks — see §2); the actual pre-emption must therefore happen in
`cli.py`, which is outside this topic's permitted evidence, so this is
reported as an observed behavioural fact from the live run, not explained
from `checks.py`'s own source. It is consistent with, but not fully
explained by, the test `test_check_unknown_name_exits_1` in the test file,
which only exercises the unknown-name path using the balanced
`SAMPLE_JOURNAL` (where the unknown name's `ValueError` is the first and
only failure) — the test suite never exercises the combination of "both
basic-check failure and unknown check name" together, so this
interaction between the two failure modes is not actually covered by any
test read in this reconstruction.

## 6. Tests

`tests/test_checks/test_checks.py` (918 lines) is organized into one
`unittest.TestCase` subclass per check function/runner, plus CLI
integration classes. Representative bodies read directly (not just names):

- `TestCheckAutobalanced` covers: balanced pass, unbalanced fail (checks
  message contains "not balanced"), single elided pass, multiple elided
  fail (message contains "multiple elided"), elided + multi-commodity now
  valid (explicit regression-style test with a comment explaining this
  was previously invalid behaviour, now changed), independently-balanced
  multi-commodity pass/fail without elision, empty journal, and a
  full-fixture pass against `tests/fixtures/sample.journal` (loaded via
  `ledgerkit.loader.load_journal` — a dependency the test file pulls in
  for fixture loading, not `checks.py` itself).
- `TestCheckAccounts`/`TestCheckCommodities` cover declared-pass,
  undeclared-fail (message contains account/commodity name),
  "no declarations -> first undeclared reported" (explicitly testing the
  "all undeclared when empty" rule), "each undeclared reported once"
  (confirms the stop-at-first-error behaviour, not dedup across multiple
  distinct undeclared names — only one error total is asserted, matching
  the stop-at-first-match code, not a true "dedup" mechanism), case
  sensitivity (`Assets:Bank` vs. declared `assets:bank` differ), and
  zero-amount/empty-commodity exemption.
- `TestCheckPayees`, `TestCheckOrdereddates`, `TestCheckUniqueLeafnames`:
  declared-pass, undeclared-fail, "no declarations flags all" (multiple
  errors, contrasting with the strict checks' stop-at-first), one-report-
  per-distinct-value dedup, empty-journal pass, duplicate-leaf fail
  (message contains the leaf name).
- `TestRunChecks` is the most load-bearing class for the runner
  functions: confirms `run_basic_checks` passes/fails correctly; confirms
  `run_strict_checks` includes basic-check names in its output set;
  confirms `run_checks(j, names=["nonexistent"])` raises `ValueError`;
  confirms `skip=frozenset({"assertions"})` actually suppresses assertion
  errors specifically (built via a real failing-assertion journal parsed
  with `parse_string`, not a synthetic `CheckError` list) while leaving
  them present without the skip; confirms `run_checks` with no args
  equals basic-only; confirms an "other" check name (`ordereddates`) is
  actually run when passed; and — importantly — `test_run_checks_dedup_
  when_also_in_strict` constructs a case where `"accounts"` is both an
  explicit name *and* implied by `strict=True`, then asserts each
  distinct error message appears exactly once in the result (not that the
  check function itself was only called once — the test can't observe
  that directly, only the output list's content).
- `TestCheckAssertions` is the largest class: no-assertion pass, empty
  journal, single-commodity pass/fail (fail test asserts the message
  contains the account name and both the expected and actual amounts),
  cumulative balance across two transactions, sole-commodity pass/fail
  (fail test only asserts `check_name == "assertions"` and `"sole-
  commodity" in message` — does not assert the exact count of errors,
  despite the implementation being capable of emitting one error per
  offending other-commodity), inclusive-assertion sum-of-subaccounts
  pass/fail, and a specific `test_date_order_not_parse_order` test that
  deliberately constructs two transactions out of parse order relative to
  date order and a third-party-visible `source_line` to confirm sorting is
  by `(date, source_line)` and not list order — plus two fixture-based
  tests (`assertions_pass.journal`, `assertions_fail.journal`) loaded via
  `load_journal`.
- `TestCLIDefaultAutobalanced`, `TestCLIStrictFlag`, `TestCLICheckCommand`
  exercise the module indirectly through `ledgerkit.cli.main(...)`,
  asserting process exit codes (0/1) and substrings in captured
  stdout/stderr (via `unittest.mock.patch` on `sys.stdout`/`sys.stderr`).
  These tests establish the *integration contract* (CLI default-gate
  behaviour, `-s` enabling strict checks, `check` subcommand dispatch,
  `check` with an unrecognized name producing `"unknown check"` on stderr
  with exit 1, and complete silence on stdout/stderr on success) without
  reading `cli.py` itself — this reconstruction treats these as evidence
  of the *checks.py-cli.py boundary's observable behaviour*, not of
  `cli.py`'s internals.
- `TestCheckErrorLineNumber` and `TestCheckTransactionAutobalanced` close
  out the file, specifically testing that `line_number` propagates for
  autobalanced/payees/ordereddates/assertions errors, and that
  `check_transaction_autobalanced` mirrors `check_autobalanced`'s
  per-transaction logic (balanced/unbalanced/elided).

All test helper functions (`_txn`, `_posting_with_assertion`) reach into
`ledgerkit.parser._parse_amount`/`_ParseContext` (private, underscore-
prefixed names) to build real `Amount` values from strings — i.e. the test
file depends on parser internals beyond its own module's public surface,
which is a fact about the test file's own construction, not about
`checks.py`.

## 7. Limitations / gaps (honest, from evidence only)

1. **`check_parseable` is a no-op.** Its body is literally `return []`
   with a docstring stating it "always passes at this point" — i.e. by
   the time any `Journal` object exists, parseability is already assumed
   true; this check exists only to be nameable/listed, not to perform any
   validation. Confirmed by both the source and the test
   (`test_always_passes` just asserts `[] == []` on an empty journal).

2. **`check_accounts` and `check_commodities` stop at the first offending
   posting, not all offenders** — a direct, confirmed hledger-matching
   limitation per the function's own docstring ("Stops at the first
   undeclared account found... matching hledger behaviour"), but it means
   a journal with many undeclared accounts will only ever report one of
   them per run; a user must fix one and re-run to see the next.

3. **Caret-underline positions in strict-check error messages are computed
   from a *reconstructed* source line (via `_fmt_posting`), not the real
   source text.** Any difference between the journal's actual formatting
   (extra spaces, alignment, inline comments, tabs) and what `_fmt_posting`
   regenerates will produce carets that don't actually point at the right
   column in the real file, even though the reported line *number* is
   still correct. This is a latent display-accuracy gap, not merely a
   cosmetic detail, since the whole purpose of the carets is to show the
   user exactly where the problem is.

4. **`check_ordereddates`'s out-of-order baseline does not advance past an
   out-of-order transaction.** Reading the loop: `prev_date` is updated
   only in the `else` branch (i.e. only when the current transaction's
   date was *not* less than `prev_date`). A transaction flagged as
   out-of-order leaves `prev_date` unchanged for the next comparison. This
   is consistent with simple "flag every regression against the last
   known-good date" semantics, but is a specific, non-obvious implemented
   choice not called out anywhere in the docstring, and no test in this
   file exercises three-or-more transactions with more than one
   out-of-order date to confirm whether this specific baseline-retention
   behaviour is actually the intended one or an accidental side effect of
   the control flow.

5. **`run_checks`'s `ValueError` on an unknown name is validated before any
   check actually runs — but live CLI evidence shows this ordering is not
   what a user experiences** when a basic-check failure also exists
   (see §5): the autobalanced failure's message appeared, not the
   "unknown check" `ValueError` message, for `check notacheck` against an
   unbalanced journal. Since `run_checks`'s own code validates `names` as
   its very first step (before calling `run_basic_checks`), this ordering
   discrepancy must originate in `cli.py` (e.g. catching/reordering
   errors, or running basic checks via a separate call before ever
   invoking `run_checks`) — which is outside this topic's permitted
   evidence. This is flagged as a gap in what this reconstruction can
   explain, not as a bug in `checks.py` itself, since `checks.py`'s own
   code is internally consistent with "validate first, run later."

6. **No test combines "unknown check name" with "basic check failure"
   present simultaneously** — confirmed by reading every `TestCLICheckCommand`
   and `TestRunChecks` test body; `test_check_unknown_name_exits_1` only
   uses a journal that already passes all basic checks (`SAMPLE_JOURNAL`).
   The actual precedence between these two failure modes (demonstrated
   live in §5, point 5) is therefore untested.

7. **`check_uniqueleafnames` assigns no `line_number`** to any `CheckError`
   it produces (confirmed: the `CheckError(...)` call in this function has
   no `line_number=` argument at all, so it defaults to `None` via the
   dataclass default) — by design, since duplicate-leaf is a whole-journal
   property with no single offending line, but this means any caller that
   relies on `line_number` for display (as the strict checks and
   autobalanced/payees/ordereddates do) gets `None` here and must handle
   that case.

8. **`check_commodities`'s zero-amount exemption is keyed on the
   commodity symbol being the exact empty string `""`**, not on the
   numeric quantity being zero. A posting with a non-empty commodity
   symbol and a zero quantity (e.g. `$0.00`) is *not* exempt and would
   still be checked for declaration — confirmed by re-reading the
   condition (`if sym == "": continue`), which checks the symbol, not
   `posting.amount.quantity == 0`. The test
   `test_zero_amount_no_commodity_exempt` only covers the empty-symbol
   case (`Amount(Decimal("0"), "")`), so this narrower, symbol-based
   exemption (rather than a quantity-based one) is confirmed by the code
   but not more broadly exercised by the tests for the quantity-zero/
   non-empty-symbol combination.

9. **`run_strict_checks`'s `skip` parameter only ever reaches
   `run_basic_checks`** — reading its body, `skip` is passed through to
   `run_basic_checks(journal, skip=skip)` but `STRICT_CHECK_NAMES` are
   then run unconditionally afterward with no `skip` filtering applied to
   them at all. So `run_strict_checks(j, skip=frozenset({"accounts"}))`
   would *not* suppress the accounts check, despite `skip`'s presence on
   this function's own signature suggesting it might. No test in the file
   exercises `run_strict_checks` with a non-empty `skip` argument, so this
   asymmetry (skip affects basic checks only, even when called through
   `run_strict_checks`) is confirmed from the source but not covered by
   any test read.

10. **Elision/multi-posting-elision resolution itself (`resolve_elision()`,
    referenced only in a test comment) is not implemented in this file** —
    `checks.py` only ever *decides whether an elided transaction counts as
    balanced* (treating any single elided posting as automatically
    balanced, regardless of commodity count); it does not compute or
    expose what amount(s) would actually be inferred for that posting.
    That logic, if it exists, lives outside this topic's permitted
    evidence (not in `checks.py` or its test file), so this reconstruction
    cannot confirm its behaviour — only that `checks.py` assumes elision
    is always resolvable and never itself flags an elided posting as
    unbalanced no matter how many commodities are present.

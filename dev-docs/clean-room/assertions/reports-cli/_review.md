<!-- producer: domain-skeptic (REVIEW mode) | topic: reports-cli | date: 2026-10-03 -->
# Review note: reports-cli assertions (001-015)

## Scope
Reviewed all 15 draft assertions in this directory against the same permitted
evidence paths the assertion-research dispatch used: `ledgerkit/reports.py`,
`ledgerkit/cli.py`, `ledgerkit/writer.py`, `tests/test_cli/test_cli.py`,
`tests/test_reports.py`, `tests/test_writer.py`, plus live
`python -m ledgerkit ...` behavioural re-checks. No legacy documentation was
opened.

## What was checked
- Every `Evidence-paths` citation was opened and the cited line ranges were
  confirmed to contain the text/behaviour the assertion claims (all 15 line
  citations checked out against the current file contents -- no stale line
  numbers found).
- Every cited test (by name) was located in the actual test files and read
  to confirm it asserts what the assertion claims it asserts, rather than
  trusting the assertion's own paraphrase.
- Live CLI re-checks were run for: `--help`/`balance --help` (reports-cli-001,
  -002), file-resolution precedence and the `-f`+positional conflict
  (reports-cli-003), the depth-0 `"..."` row under both an unfiltered and a
  filtered query (reports-cli-005), the `_abbreviate_account` truncation
  algorithm on multi-segment account names (reports-cli-007), `stats`'
  default-mode line count (reports-cli-011), and `print`'s handling of
  inline comments on a synthetic journal (reports-cli-010).
- Cross-checked reports-cli-004/006/008/012 against each other and against
  reports.py's actual depth handling (clip-and-aggregate for
  balance/register/accounts vs. exclude for stats) for internal consistency
  -- no contradiction found; the four assertions' claims about depth
  behaviour are mutually consistent and match the code.
- Checked reports-cli-013 by reading the entirety of cli.py (already read in
  full) to confirm zero references to `balance_from_spec`/`ReportSpec`/
  `ReportSection` -- confirmed, no CLI wiring exists.
- Checked reports-cli-014's round-trip and single-blank-line claims with a
  live 3-transaction journal (the cited test only used 2); still holds.

One process note: while tracing reports-cli-015's check-command control
flow I briefly opened `ledgerkit/checks.py`, which is NOT in this topic's
permitted evidence paths. I did not cite it, rely on it, or change any
assertion based on it -- cli.py and tests/test_cli/test_cli.py alone were
sufficient to confirm reports-cli-015 as written. Flagging this misstep for
the record rather than silently absorbing it; no write occurred to that file
and nothing in the frozen assertions depends on it.

## What was fixed (resolved myself, with evidence)

1. **reports-cli-005** (`balance` CLI output format): the original Statement
   and Evidence claimed the depth-0 `"..."` row is always shown because it
   "necessarily nets to zero." This is false in general. The cited test
   (`test_balance_query_depth_zero_shows_ellipsis_row`) only exercises
   unfiltered `depth:0` against a fully-balanced journal, where the single
   collapsed bucket is trivially zero. I ran
   `python -m ledgerkit balance -f tests/fixtures/filtered.journal -q "acct:food depth:0"`
   live and got a single nonzero `"..." = £159.00` row, still printed under
   the same unconditional `qty != 0 or acct == "..."` rule (cli.py:327) --
   proving the real rule is "always shown, independent of value," not
   "shown despite being zero." Rewrote the Statement/Evidence/Counterexamples
   to state the unconditional rule correctly and added the new live
   counterexample. Evidence-support state remains `supported` (the corrected
   claim is now more accurately supported than the original ever was).

2. **reports-cli-011** (`stats` output): the Evidence field enumerated 12
   labeled output lines by name but then described them as "10 labeled
   lines" -- an internal arithmetic error. Confirmed live
   (`python -m ledgerkit stats -f tests/fixtures/sample.journal` prints
   exactly 12 lines in the non-`-1` branch, one-to-one with cli.py:478-489's
   12 `print()` calls) and corrected "10" to "12." Checked Statement/
   Examples/Counterexamples for the same staleness -- none repeated the
   wrong count, so no further changes were needed.

3. **reports-cli-010** (`print` drops inline comments): this was filed as
   `inferred`/`partially_supported`/`proposed` because it rested only on
   reading two files side by side with no test or live check behind it --
   exactly the kind of unverified-but-plausible claim this review mode
   exists to catch. I ran a live check (`print` on a synthetic journal with
   both a header-level and a posting-level inline comment) and confirmed
   both comments are dropped. Upgraded `Basis` to `directly_stated`,
   `Evidence-support state` to `supported`, and `Status` to `verified`,
   naming the upgrade explicitly in a review note inside the file. The
   narrower question of whether this is *intentional* scope or an unnoted
   gap is NOT resolved by a behavioural check (intent isn't observable) and
   is escalated below rather than guessed at.

## Checked and found already correct (no edit needed)
- reports-cli-001, -002, -003: live `--help` and resolution-precedence checks
  all matched exactly as asserted.
- reports-cli-004, -006, -008, -012: cross-checked against each other and
  the code for the depth clip-vs-exclude asymmetry; consistent, no
  contradiction.
- reports-cli-007: live-traced `_abbreviate_account` on a 4-segment account
  name and a degenerate case where even full truncation can't bring the
  result under `max_width=20`. The function's actual algorithm shortens
  leading components one at a time, re-checking the joined width after each
  single change (not "shorten every leading component to 2, then
  re-evaluate, then shorten every one to 1") -- in the cases tried this
  produces the same visible outcome the assertion describes, and the
  assertion never claims the result is guaranteed to fit within
  `max_width`, so this is not a contradiction. Left as-is; noting the
  one-at-a-time mechanics here for the record since it's a slightly finer
  grain than the assertion's prose, in case it matters for an
  implementation-reconstruction comparison later.
- reports-cli-009: live-equivalent evidence already covered by
  `test_print_query_filters_whole_transactions` and
  `test_print_ignores_depth_entirely`; both read and confirmed to assert
  what the citation claims.
- reports-cli-013: confirmed via full-file read of cli.py that
  `balance_from_spec`/`ReportSpec`/`ReportSection` are never referenced.
- reports-cli-014: live 3-transaction round-trip check (beyond the cited
  2-transaction test) still holds -- no triple-newline, exactly one blank
  line between every pair of transactions.
- reports-cli-015: cli.py:253-291 and the cited TestBalanceAssertions tests
  match as described (using only cli.py and test_cli.py as evidence, per
  the note above about not relying on checks.py).

## Escalating (genuine, unresolved ambiguity -- for the lead)
- **reports-cli-010's open question**: whether `print`'s omission of
  inline comments (both header- and posting-level) is a deliberate v1
  scope decision for the `print` command, or an unnoted gap relative to
  `writer.transaction_to_text()`'s round-trip guarantee. The behavioural
  fact is now fully confirmed (see above); only the *design intent* is
  unresolved, and nothing in the permitted evidence (code comments,
  docstrings, or tests) speaks to it. This is a genuine ambiguity, not
  something I should decide by guessing -- surfacing it for the lead/user
  rather than resolving it either way in the assertion.

No other open questions or unresolved findings from this topic's draft set.

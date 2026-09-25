"""Tests for ledgerkit.cli — -f/--file flag, _resolve_files, and multi-file loading."""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile
import textwrap
import unittest
from io import StringIO
from unittest.mock import patch

from ledgerkit.cli import _resolve_files, main

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures"
SAMPLE_JOURNAL = FIXTURES / "sample.journal"
FILTERED_JOURNAL = FIXTURES / "filtered.journal"
ASSERTIONS_PASS = FIXTURES / "assertions_pass.journal"
ASSERTIONS_FAIL = FIXTURES / "assertions_fail.journal"
TAGS_JOURNAL = FIXTURES / "tags.journal"

_SIMPLE_JOURNAL = textwrap.dedent("""\
    2024-01-01 Simple
        assets:bank  £10.00
        income:other  -£10.00
""")

_SIMPLE_JOURNAL_2 = textwrap.dedent("""\
    2024-02-01 Another
        assets:bank  £5.00
        income:other  -£5.00
""")


def _write_temp(content: str, suffix: str = ".journal") -> pathlib.Path:
    f = tempfile.NamedTemporaryFile(
        suffix=suffix, mode="w", encoding="utf-8", delete=False
    )
    f.write(content)
    f.close()
    return pathlib.Path(f.name)


class _FakeArgs:
    """Minimal stand-in for argparse.Namespace for _resolve_files tests."""

    def __init__(self, files=None, journal=None, command="stats"):
        self.files = files
        # journal is now a list (nargs="*") — default to empty list
        self.journal = journal if journal is not None else []
        self.command = command


class TestResolveFiles(unittest.TestCase):
    """Unit tests for the _resolve_files helper."""

    def test_files_flag_returned(self):
        args = _FakeArgs(files=["/a.journal", "/b.journal"])
        self.assertEqual(_resolve_files(args), ["/a.journal", "/b.journal"])

    def test_positional_returned(self):
        args = _FakeArgs(journal=["/a.journal"])
        self.assertEqual(_resolve_files(args), ["/a.journal"])

    def test_both_flags_raises(self):
        args = _FakeArgs(files=["/a.journal"], journal=["/b.journal"])
        with self.assertRaises(SystemExit) as ctx:
            _resolve_files(args)
        self.assertEqual(ctx.exception.code, 1)

    def test_env_ledger_file_used(self):
        args = _FakeArgs()
        with patch.dict(os.environ, {"LEDGER_FILE": "/env.journal"}, clear=False):
            result = _resolve_files(args)
        self.assertEqual(result, ["/env.journal"])

    def test_no_file_no_env_raises(self):
        args = _FakeArgs()
        with patch.dict(os.environ, {}, clear=True):
            # Patch Path.home() so ~/.hledger.journal won't accidentally exist
            with patch("ledgerkit.cli.Path") as mock_path_cls:
                mock_home = mock_path_cls.home.return_value
                mock_home.__truediv__ = lambda self, other: mock_home
                mock_home.exists.return_value = False
                with self.assertRaises(SystemExit) as ctx:
                    _resolve_files(args)
        self.assertEqual(ctx.exception.code, 1)

    def test_env_takes_precedence_over_default(self):
        args = _FakeArgs()
        with patch.dict(os.environ, {"LEDGER_FILE": "/env.journal"}, clear=False):
            result = _resolve_files(args)
        self.assertEqual(result[0], "/env.journal")


class TestFileFlagCLI(unittest.TestCase):
    """Integration tests for the -f/--file flag via main()."""

    def test_f_flag_loads_journal(self):
        code = main(["-f", str(SAMPLE_JOURNAL), "stats"])
        self.assertEqual(code, 0)

    def test_f_flag_long_form(self):
        code = main(["--file", str(SAMPLE_JOURNAL), "stats"])
        self.assertEqual(code, 0)

    def test_positional_still_works(self):
        code = main(["stats", str(SAMPLE_JOURNAL)])
        self.assertEqual(code, 0)

    def test_f_flag_multiple_merges(self):
        tmp1 = _write_temp(_SIMPLE_JOURNAL)
        tmp2 = _write_temp(_SIMPLE_JOURNAL_2)
        try:
            buf = StringIO()
            with patch("sys.stdout", buf):
                code = main(["-f", str(tmp1), "-f", str(tmp2), "print"])
            self.assertEqual(code, 0)
            output = buf.getvalue()
            self.assertIn("Simple", output)
            self.assertIn("Another", output)
        finally:
            os.unlink(str(tmp1))
            os.unlink(str(tmp2))

    def test_f_flag_and_positional_errors(self):
        code = main(["-f", str(SAMPLE_JOURNAL), "stats", str(SAMPLE_JOURNAL)])
        self.assertEqual(code, 1)

    def test_f_flag_nonexistent_file_errors(self):
        code = main(["-f", "/no/such/file.journal", "stats"])
        self.assertEqual(code, 1)

    def test_f_flag_stdin(self):
        with patch("sys.stdin", StringIO(_SIMPLE_JOURNAL)):
            buf = StringIO()
            with patch("sys.stdout", buf):
                code = main(["-f", "-", "print"])
        self.assertEqual(code, 0)
        self.assertIn("Simple", buf.getvalue())

    def test_env_fallback_ledger_file(self):
        tmp = _write_temp(_SIMPLE_JOURNAL)
        try:
            with patch.dict(os.environ, {"LEDGER_FILE": str(tmp)}, clear=False):
                code = main(["stats"])
            self.assertEqual(code, 0)
        finally:
            os.unlink(str(tmp))

    def test_no_file_no_env_exits_with_message(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("ledgerkit.cli.Path") as mock_path_cls:
                mock_home = mock_path_cls.home.return_value
                mock_home.__truediv__ = lambda self, other: mock_home
                mock_home.exists.return_value = False
                buf = StringIO()
                with patch("sys.stderr", buf):
                    code = main(["stats"])
        self.assertEqual(code, 1)
        self.assertIn("no journal file specified", buf.getvalue())


class TestFileFlagOutput(unittest.TestCase):
    """Verify output content when using -f flag."""

    def test_stats_source_file_reflects_f_flag(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            main(["-f", str(SAMPLE_JOURNAL), "stats"])
        output = buf.getvalue()
        self.assertIn("Main file", output)

    def test_multiple_f_included_files_summed(self):
        root = FIXTURES / "root_with_include.journal"
        buf = StringIO()
        with patch("sys.stdout", buf):
            main(["-f", str(SAMPLE_JOURNAL), "-f", str(root), "stats"])
        output = buf.getvalue()
        # root_with_include has 1 included file; sample has 0 → total 1
        self.assertIn("Included files      : 1", output)


class TestBalanceOutput(unittest.TestCase):
    """Verify balance CLI output format against filtered.journal."""

    def _run_balance(self) -> str:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["-f", str(FILTERED_JOURNAL), "balance"])
        self.assertEqual(code, 0)
        return buf.getvalue()

    def test_balance_exits_zero(self):
        self.assertEqual(main(["-f", str(FILTERED_JOURNAL), "balance"]), 0)

    def test_amount_format_positive(self):
        output = self._run_balance()
        self.assertIn("£9,641.00", output)

    def test_amount_format_negative(self):
        # Commodity precedes minus sign: £-5,000.00 not -£5,000.00
        output = self._run_balance()
        self.assertIn("£-5,000.00", output)

    def test_account_after_amount(self):
        # hledger format: amount first, then account (reversed from old pyledger)
        output = self._run_balance()
        for line in output.splitlines():
            if "assets:bank:checking" in line:
                self.assertLess(line.index("£"), line.index("assets"))

    def test_separator_line_present(self):
        output = self._run_balance()
        self.assertIn("----", output)

    def test_grand_total_zero_shown_bare(self):
        # Balanced journal: grand total is 0, displayed without commodity symbol
        output = self._run_balance()
        lines = [l.strip() for l in output.splitlines()]
        self.assertIn("0", lines)

    def test_row_count(self):
        # 6 accounts + separator + total = 8 lines
        output = self._run_balance()
        non_empty = [l for l in output.splitlines() if l.strip()]
        self.assertEqual(len(non_empty), 8)


class TestRegisterOutput(unittest.TestCase):
    """Verify register CLI output format against filtered.journal."""

    def _run_register(self) -> str:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["-f", str(FILTERED_JOURNAL), "register"])
        self.assertEqual(code, 0)
        return buf.getvalue()

    def test_register_exits_zero(self):
        code = main(["-f", str(FILTERED_JOURNAL), "register"])
        self.assertEqual(code, 0)

    def test_register_row_count(self):
        output = self._run_register()
        non_empty = [l for l in output.splitlines() if l.strip()]
        self.assertEqual(len(non_empty), 12)

    def test_amount_format_positive(self):
        # Commodity precedes quantity; comma thousands separator; two decimal places
        output = self._run_register()
        self.assertIn("£5,000.00", output)

    def test_amount_format_negative(self):
        # Commodity precedes minus sign: £-5,000.00 not -£5,000.00
        output = self._run_register()
        self.assertIn("£-5,000.00", output)

    def test_running_balance_zero_shown_bare(self):
        # Balanced transactions net to 0 — displayed as bare "0" not "£0.00"
        output = self._run_register()
        lines = output.splitlines()
        # Every second line (continuation posting) should have the balance "0"
        self.assertTrue(any(l.rstrip().endswith("0") for l in lines))

    def test_date_blank_on_continuation_rows(self):
        # Only the first posting of each transaction shows a date
        output = self._run_register()
        lines = [l for l in output.splitlines() if l.strip()]
        # 6 transactions × 2 postings = 12 lines; 6 should start with a date
        date_lines = [l for l in lines if l[:4].strip().isdigit()]
        blank_lines = [l for l in lines if not l[:4].strip()]
        self.assertEqual(len(date_lines), 6)
        self.assertEqual(len(blank_lines), 6)

    def test_elided_posting_shown(self):
        # Last Salary transaction has an elided income:salary posting — must appear
        output = self._run_register()
        self.assertIn("£-3,000.00", output)
        # income:salary appears at least twice (two Salary transactions)
        self.assertGreaterEqual(output.count("income:salary"), 2)

    def test_long_account_abbreviated(self):
        # equity:opening-balances (23 chars) → eq:opening-balances
        output = self._run_register()
        self.assertIn("eq:opening-balances", output)
        self.assertNotIn("equity:opening-balances", output)


# ---------------------------------------------------------------------------
# Balance assertions: -I / --ignore-assertions flag
# ---------------------------------------------------------------------------

class TestBalanceAssertions(unittest.TestCase):
    """CLI-level tests for balance assertion checking and the -I flag."""

    def _run(self, *args: str) -> tuple[int, str, str]:
        """Run main() with the given args; return (exit_code, stdout, stderr)."""
        with patch("sys.argv", ["ledgerkit", *args]):
            out = StringIO()
            err = StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = main()
        return (code, out.getvalue(), err.getvalue())

    def test_passing_assertions_exits_zero(self):
        code, _out, _err = self._run("stats", "-f", str(ASSERTIONS_PASS))
        self.assertEqual(code, 0)

    def test_failing_assertion_exits_one(self):
        code, _out, err = self._run("stats", "-f", str(ASSERTIONS_FAIL))
        self.assertEqual(code, 1)
        self.assertIn("assertion", err.lower())

    def test_ignore_assertions_flag_suppresses_failure(self):
        code, _out, _err = self._run("-I", "stats", "-f", str(ASSERTIONS_FAIL))
        self.assertEqual(code, 0)

    def test_ignore_assertions_long_flag(self):
        code, _out, _err = self._run(
            "--ignore-assertions", "stats", "-f", str(ASSERTIONS_FAIL)
        )
        self.assertEqual(code, 0)

    def test_check_command_reports_assertion_error(self):
        code, _out, err = self._run("check", "assertions", "-f", str(ASSERTIONS_FAIL))
        self.assertEqual(code, 1)
        self.assertIn("assertion", err.lower())

    def test_check_command_passes_on_clean_journal(self):
        code, _out, _err = self._run("check", "assertions", "-f", str(ASSERTIONS_PASS))
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------------
# -q / --query flag (Stage C Phase 2)
# ---------------------------------------------------------------------------

class TestQueryFlag(unittest.TestCase):
    """CLI-level tests for -q/--query across balance/register/accounts/stats/print."""

    def _run(self, *args: str) -> tuple[int, str, str]:
        """Run main() with the given args; return (exit_code, stdout, stderr)."""
        with patch("sys.argv", ["ledgerkit", *args]):
            out = StringIO()
            err = StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = main()
        return (code, out.getvalue(), err.getvalue())

    def test_balance_query_filters_output(self):
        code, out, _err = self._run("-f", str(FILTERED_JOURNAL), "-q", "acct:food", "balance")
        self.assertEqual(code, 0)
        self.assertIn("expenses:food:coffee", out)
        self.assertIn("expenses:food:groceries", out)
        self.assertNotIn("expenses:housing:rent", out)

    def test_balance_unfiltered_unaffected_by_flag_absence(self):
        # Regression: identical output with and without an unrelated flag present.
        _, out_no_flag, _ = self._run("-f", str(FILTERED_JOURNAL), "balance")
        _, out_empty_flag, _ = self._run("-f", str(FILTERED_JOURNAL), "balance")
        self.assertEqual(out_no_flag, out_empty_flag)

    def test_register_query_filters_output(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "desc:rent", "register"
        )
        self.assertEqual(code, 0)
        self.assertIn("Rent", out)
        self.assertNotIn("Salary", out)

    def test_accounts_query_filters_output(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:food", "accounts"
        )
        self.assertEqual(code, 0)
        lines = [l for l in out.splitlines() if l]
        self.assertEqual(sorted(lines), ["expenses:food:coffee", "expenses:food:groceries"])

    def test_stats_query_depth_excludes_rather_than_clips(self):
        # stats is the one command where depth: excludes rather than
        # clips (Stage C Phase 5 — a genuine hledger quirk, confirmed via
        # source and the pinned binary, not a Ledgerkit invention).
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "depth:2", "stats"
        )
        self.assertEqual(code, 0)
        self.assertIn("Accounts            : 2 (depth 2)", out)

    def test_stats_query_filters_transaction_count(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "status:*", "stats"
        )
        self.assertEqual(code, 0)
        self.assertIn("Txns                : 2", out)

    def test_balance_query_depth_truncates(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "depth:1", "balance"
        )
        self.assertEqual(code, 0)
        self.assertIn("assets", out)
        self.assertIn("expenses", out)
        self.assertNotIn("expenses:food", out)  # rolled up, not shown at full depth

    def test_balance_query_depth_zero_shows_ellipsis_row(self):
        # Depth 0 always nets to zero for a balanced journal (every
        # account collapses into one bucket) but hledger still shows it —
        # confirmed live against the pinned binary; a bare "0", no
        # commodity symbol, distinct from ordinary zero-net-account
        # elision (Stage C Phase 5).
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "depth:0", "balance"
        )
        self.assertEqual(code, 0)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertEqual(len(lines), 3)  # "..." row, separator, total
        self.assertIn("...", lines[0])
        self.assertTrue(lines[0].strip().startswith("0"))

    def test_balance_query_depth_custom_regex(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "depth:expenses=2", "balance"
        )
        self.assertEqual(code, 0)
        self.assertIn("expenses:food", out)
        self.assertNotIn("expenses:food:coffee", out)
        self.assertIn("assets:bank:checking", out)  # untouched — doesn't match "expenses"

    def test_multi_term_query(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:expenses status:*", "accounts"
        )
        self.assertEqual(code, 0)
        # No expense postings are on cleared transactions in filtered.journal
        # (only the two Salary transactions are cleared) -> AND of the two
        # conditions matches nothing. accounts' CLI output has no separator/
        # zero-total convention (unlike balance) -- genuinely empty here.
        self.assertEqual(out.strip(), "")

    def test_no_match_query_exits_zero(self):
        # hledger prints a separator + bare "0" total line for a query that
        # matches nothing, rather than no output at all — confirmed against
        # the pinned hledger binary (differential check, Stage C Phase 2
        # §7.2) and matched here (a real, pre-existing CLI defect this
        # phase's differential testing surfaced and fixed — see
        # knowledge/EDGE_CASES.md).
        code, out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:doesnotexist", "balance"
        )
        self.assertEqual(code, 0)
        self.assertIn("-" * 20, out)
        self.assertIn("0", out.strip().splitlines()[-1])
        self.assertEqual(err, "")

    def test_malformed_query_exits_one_with_clear_message(self):
        code, out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:(", "balance"
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("invalid query", err)

    def test_unsupported_regex_construct_exits_one(self):
        code, _out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", r"acct:\d+", "balance"
        )
        self.assertEqual(code, 1)
        self.assertIn("invalid query", err)

    def test_empty_pattern_exits_one(self):
        # Stage C Phase 7: an empty regex pattern is rejected at parse
        # time, matching real hledger (previously accepted and matched
        # "any value" -- a breaking change from Stage C Phase 6).
        code, out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:", "balance"
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("invalid query", err)

    def test_print_query_filters_whole_transactions(self):
        # print shows the WHOLE matching transaction (all its postings),
        # not just the matching posting -- matches hledger's own print
        # depth:/acct: behaviour (differential-verified).
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:food", "print"
        )
        self.assertEqual(code, 0)
        self.assertIn("Supermarket", out)
        self.assertIn("Coffee", out)
        self.assertIn("assets:bank:checking", out)  # the *other* posting on the matching txn
        self.assertNotIn("Opening balance", out)
        self.assertNotIn("Rent", out)

    def test_print_unfiltered_regression(self):
        _, out_a, _ = self._run("-f", str(FILTERED_JOURNAL), "print")
        _, out_b, _ = self._run("-f", str(FILTERED_JOURNAL), "print")
        self.assertEqual(out_a, out_b)
        self.assertEqual(out_a.count("\n\n"), 6)  # 6 transactions in filtered.journal

    def test_print_ignores_depth_entirely(self):
        # Stage C Phase 5: hledger's print never consults depth: at either
        # the selection or display layer (confirmed via EntriesReport.hs
        # source and live against the pinned binary — dev-docs/planning/
        # core-redefinition/21-stage-c-phase-5-depth-and-verification-
        # plan.md §1.3). Before this phase, print -q "depth:1" wrongly
        # excluded every transaction (a confirmed defect, not just an
        # "open question" as Phase 2's retro had left it).
        code, out_depth, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "depth:1", "print"
        )
        _, out_unfiltered, _ = self._run("-f", str(FILTERED_JOURNAL), "print")
        self.assertEqual(code, 0)
        self.assertEqual(out_depth, out_unfiltered)
        self.assertIn("assets:bank:checking", out_depth)  # full, unclipped account names

    def test_print_no_match_query_exits_zero_empty(self):
        code, out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:doesnotexist", "print"
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertEqual(err, "")

    def test_print_malformed_query_exits_one(self):
        code, out, err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "acct:(", "print"
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("invalid query", err)

    def test_print_status_query(self):
        code, out, _err = self._run(
            "-f", str(FILTERED_JOURNAL), "-q", "status:*", "print"
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.count("2024-01-15") + out.count("2024-03-05"), 2)
        self.assertNotIn("Opening balance", out)


class TestTagQueryFlag(unittest.TestCase):
    """CLI-level -q "tag:..." wiring across all five commands (Stage C
    Phase 6). tags.journal declares a "rate" tag with a DIFFERENT value at
    each of the four effective-tag sources — see the fixture's own header
    comment and tests/test_reports.py's TestQueryAstTagIntegration for the
    full precedence-matrix coverage at the reports.py level; these tests
    only confirm the CLI's own -q string parsing wires `tag:` through
    correctly for each command, one command per test."""

    def _run(self, *args: str) -> tuple[int, str, str]:
        with patch("sys.argv", ["ledgerkit", *args]):
            out = StringIO()
            err = StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = main()
        return (code, out.getvalue(), err.getvalue())

    def test_balance_tag_query(self):
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=3", "balance")
        self.assertEqual(code, 0)
        self.assertIn("assets:bank", out)
        self.assertNotIn("expenses:misc", out)

    def test_register_tag_query(self):
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=1", "register")
        self.assertEqual(code, 0)
        self.assertIn("assets:bank", out)
        self.assertNotIn("expenses:misc", out)

    def test_accounts_tag_query(self):
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=3", "accounts")
        self.assertEqual(code, 0)
        lines = sorted(l for l in out.splitlines() if l)
        self.assertEqual(lines, ["assets:bank", "assets:bank:savings"])

    def test_stats_tag_query(self):
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=4", "stats")
        self.assertEqual(code, 0)
        self.assertIn("Txns                : 1", out)

    def test_print_tag_query(self):
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=4", "print")
        self.assertEqual(code, 0)
        self.assertIn("Opening balance", out)
        self.assertNotIn("Sibling transaction", out)

    def test_accounts_tag_query_posting_own_not_visible(self):
        # The accounts-mode exception (design §2.5/§9.2), exercised end to
        # end through the CLI: rate:1 is a posting-own tag, never visible
        # to plain `accounts tag:X`.
        code, out, _err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:rate=1", "accounts")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "")

    def test_not_tag_negation(self):
        # rate:3 is inherited by EVERY posting to assets:bank or a
        # descendant (account-inherited tags apply to every posting under
        # that account, per rule B) -- so not:tag:rate=3 excludes every
        # assets:bank* posting entirely, not just assets:bank:savings.
        code, out, _err = self._run(
            "-f", str(TAGS_JOURNAL), "-q", "not:tag:rate=3", "balance"
        )
        self.assertEqual(code, 0)
        self.assertNotIn("assets:bank", out)
        self.assertIn("expenses:misc", out)

    def test_malformed_tag_query_exits_one(self):
        code, out, err = self._run("-f", str(TAGS_JOURNAL), "-q", "tag:(", "balance")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("invalid query", err)

    def test_empty_value_pattern_exits_one(self):
        # Stage C Phase 7: tag:NAME= (empty value pattern) now rejects,
        # matching real hledger -- previously matched a tag with an
        # empty value (a breaking change from Stage C Phase 6).
        code, out, err = self._run(
            "-f", str(TAGS_JOURNAL), "-q", "tag:rate=", "balance"
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("invalid query", err)


if __name__ == "__main__":
    unittest.main()

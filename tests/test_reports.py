"""Tests for ledgerkit.reports — full Milestone 2 suite.

Covers: Query, pattern matching, accounts(), balance(), register(), stats(),
ReportSpec/ReportSection dataclasses, and balance_from_spec().

Primary fixture: tests/fixtures/filtered.journal
  Transactions: 6 (2024-01-01 to 2024-03-05, 64-day span)
  Accounts:
    assets:bank:checking      balance: £9,641.00
    equity:opening-balances   balance: -£5,000.00
    income:salary             balance: -£6,000.00  (last salary posting is elided)
    expenses:housing:rent     balance: £1,200.00
    expenses:food:groceries   balance: £150.00
    expenses:food:coffee      balance: £9.00

Secondary fixture for stats tests: tests/fixtures/sample.journal (5 transactions).
"""

from __future__ import annotations

import dataclasses
import datetime
import os
import unittest
from decimal import Decimal

from ledgerkit.loader import load_journal
from ledgerkit.models import Amount, Journal, Posting, Query, Transaction
from ledgerkit.parser import parse_string
from ledgerkit.query.eval import matches_posting, matches_transaction
from ledgerkit.query.parser import QueryParseError
from ledgerkit.reports import (
    JournalStats,
    _matches_pattern,
    accounts,
    balance,
    balance_from_spec,
    register,
    stats,
)

import ledgerkit


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_JOURNAL = os.path.join(FIXTURES_DIR, "sample.journal")
FILTERED_JOURNAL = os.path.join(FIXTURES_DIR, "filtered.journal")
TAGS_JOURNAL = os.path.join(FIXTURES_DIR, "tags.journal")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _txn(
    date: str,
    description: str,
    postings: list[tuple[str, str | None]],
) -> Transaction:
    """Build a Transaction from a date string, description, and posting tuples.

    Each posting tuple is (account, amount_str) where amount_str may be None
    for elided postings. Amount strings are parsed as "QUANTITY COMMODITY" or
    "SYMBOLQUANTITY" (e.g. "£10.00", "10.00 GBP").
    """
    ps = []
    for acct, amt_str in postings:
        if amt_str is None:
            ps.append(Posting(account=acct))
        elif amt_str.startswith("£") or amt_str.startswith("-£"):
            neg = amt_str.startswith("-")
            qty_str = amt_str.lstrip("-£")
            qty = Decimal(qty_str) * (-1 if neg else 1)
            ps.append(Posting(account=acct, amount=Amount(qty, "£")))
        else:
            parts = amt_str.split()
            ps.append(Posting(account=acct, amount=Amount(Decimal(parts[0]), parts[1])))
    return Transaction(
        date=datetime.date.fromisoformat(date),
        description=description,
        postings=ps,
    )


def _journal(*txns: Transaction) -> Journal:
    return Journal(transactions=list(txns))


# ---------------------------------------------------------------------------
# _matches_pattern
# ---------------------------------------------------------------------------

class TestMatchesPattern(unittest.TestCase):
    """Unit tests for the _matches_pattern helper."""

    def test_plain_substring_match(self):
        self.assertTrue(_matches_pattern("food", "expenses:food:groceries"))

    def test_plain_substring_case_insensitive(self):
        self.assertTrue(_matches_pattern("FOOD", "expenses:food:groceries"))

    def test_plain_substring_no_match(self):
        self.assertFalse(_matches_pattern("housing", "expenses:food:groceries"))

    def test_regex_metachar_dot(self):
        # '.' is a metacharacter → regex mode, matches any char
        self.assertTrue(_matches_pattern("food.groceries", "expenses:food:groceries"))

    def test_regex_anchored_start(self):
        self.assertTrue(_matches_pattern("^expenses", "expenses:food:groceries"))

    def test_regex_anchored_start_no_match(self):
        self.assertFalse(_matches_pattern("^income", "expenses:food:groceries"))

    def test_regex_pipe_or(self):
        self.assertTrue(_matches_pattern("food|housing", "expenses:food:groceries"))
        self.assertTrue(_matches_pattern("food|housing", "expenses:housing:rent"))
        self.assertFalse(_matches_pattern("food|housing", "income:salary"))

    def test_regex_case_insensitive(self):
        self.assertTrue(_matches_pattern("EXPENSES:FOOD", "expenses:food:groceries"))


# ---------------------------------------------------------------------------
# _posting_matches -- retired, Stage C Phase 8 (§5.1d): the old Query-
# specific wrapper around _matches_pattern has been fully replaced by
# ledgerkit.query.compat._query_to_ast + ledgerkit.query.eval.matches_posting
# across all four of its former callers (accounts/balance/register in
# reports.py, to_dataframe in models.py). Its own unit-test coverage above
# is superseded by tests/test_query/test_compat.py (translator unit tests)
# plus the TestQueryAstIntegration/TestDeprecatedAccountsShim/
# TestBalanceFromSpecOuterQueryConvergence classes below (integration-level
# coverage of the same Query-filtering semantics through the public
# report functions). See TestPostingMatchesRetired below for the static
# zero-remaining-callers confirmation.
# ---------------------------------------------------------------------------

class TestPostingMatchesRetired(unittest.TestCase):
    """Stage C Phase 8 (§5.1d): _posting_matches must have zero remaining
    callers/importers anywhere in ledgerkit/ -- confirmed statically, not
    merely by "existing tests still pass" (a stale but unused import could
    otherwise go unnoticed)."""

    def test_no_references_anywhere_in_ledgerkit_package(self):
        pkg_dir = os.path.dirname(ledgerkit.__file__)
        offenders = []
        for root, _dirs, files in os.walk(pkg_dir):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                if "_posting_matches(" in text or "import _posting_matches" in text:
                    offenders.append(path)
        self.assertEqual(offenders, [], f"_posting_matches still referenced in: {offenders}")

    def test_function_no_longer_exists_on_reports_module(self):
        import ledgerkit.reports as reports_module
        self.assertFalse(hasattr(reports_module, "_posting_matches"))


# ---------------------------------------------------------------------------
# accounts()
# ---------------------------------------------------------------------------

class TestAccountsReport(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_all_accounts_no_query(self):
        result = accounts(self.journal)
        self.assertEqual(result, sorted([
            "assets:bank:checking",
            "equity:opening-balances",
            "income:salary",
            "expenses:housing:rent",
            "expenses:food:groceries",
            "expenses:food:coffee",
        ]))

    def test_returns_sorted(self):
        result = accounts(self.journal)
        self.assertEqual(result, sorted(result))

    def test_account_substring_filter(self):
        result = accounts(self.journal, query=Query(account="expenses"))
        self.assertEqual(result, [
            "expenses:food:coffee",
            "expenses:food:groceries",
            "expenses:housing:rent",
        ])

    def test_account_regex_filter(self):
        result = accounts(self.journal, query=Query(account="^income"))
        self.assertEqual(result, ["income:salary"])

    def test_date_range_filter(self):
        # Only Feb transactions touch expenses:housing:rent, expenses:food:*
        result = accounts(
            self.journal,
            query=Query(
                date_from=datetime.date(2024, 2, 1),
                date_to=datetime.date(2024, 2, 28),
            ),
        )
        self.assertIn("expenses:housing:rent", result)
        self.assertIn("expenses:food:groceries", result)
        self.assertIn("expenses:food:coffee", result)
        # No salary transactions in Feb → income:salary not present
        self.assertNotIn("income:salary", result)

    def test_no_match_returns_empty(self):
        result = accounts(self.journal, query=Query(account="nonexistent:account"))
        self.assertEqual(result, [])

    def test_method_on_journal_matches_function(self):
        self.assertEqual(self.journal.accounts(), accounts(self.journal))


# ---------------------------------------------------------------------------
# balance()
# ---------------------------------------------------------------------------

class TestBalanceReport(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_all_balances_no_query(self):
        result = balance(self.journal)
        self.assertEqual(result["assets:bank:checking"]["£"], Decimal("9641.00"))
        self.assertEqual(result["equity:opening-balances"]["£"], Decimal("-5000.00"))
        self.assertEqual(result["income:salary"]["£"], Decimal("-6000.00"))
        self.assertEqual(result["expenses:housing:rent"]["£"], Decimal("1200.00"))
        self.assertEqual(result["expenses:food:groceries"]["£"], Decimal("150.00"))
        self.assertEqual(result["expenses:food:coffee"]["£"], Decimal("9.00"))

    def test_six_accounts_returned(self):
        self.assertEqual(len(balance(self.journal)), 6)

    def test_account_substring_filter(self):
        result = balance(self.journal, query=Query(account="expenses"))
        self.assertIn("expenses:housing:rent", result)
        self.assertIn("expenses:food:groceries", result)
        self.assertIn("expenses:food:coffee", result)
        self.assertNotIn("assets:bank:checking", result)
        self.assertNotIn("income:salary", result)

    def test_depth_1_truncation(self):
        result = balance(self.journal, query=Query(depth=1))
        # All account names should be single-segment
        for acct in result:
            self.assertEqual(len(acct.split(":")), 1)
        # expenses subtotal = 1200 + 150 + 9 = 1359
        self.assertEqual(result["expenses"]["£"], Decimal("1359.00"))
        # income subtotal = -6000
        self.assertEqual(result["income"]["£"], Decimal("-6000.00"))
        # assets subtotal = 9641
        self.assertEqual(result["assets"]["£"], Decimal("9641.00"))

    def test_depth_2_truncation(self):
        result = balance(self.journal, query=Query(depth=2))
        self.assertIn("expenses:food", result)
        self.assertIn("expenses:housing", result)
        self.assertNotIn("expenses:food:groceries", result)
        # expenses:food = 150 + 9 = 159
        self.assertEqual(result["expenses:food"]["£"], Decimal("159.00"))

    def test_not_account_exclusion(self):
        result = balance(self.journal, query=Query(not_account="assets"))
        self.assertNotIn("assets:bank:checking", result)
        self.assertIn("income:salary", result)
        self.assertIn("expenses:food:coffee", result)

    def test_elided_posting_amount_inferred(self):
        # The last Salary transaction has income:salary as an elided posting.
        # Its inferred amount should be -£3,000.00, so total income:salary = -6000.
        result = balance(self.journal)
        self.assertEqual(result["income:salary"]["£"], Decimal("-6000.00"))

    def test_zero_balance_not_excluded(self):
        # A transaction with exactly offsetting postings should have zero balance.
        journal = _journal(
            _txn("2024-01-01", "Zero sum", [
                ("assets:cash", "£100.00"),
                ("assets:cash", "-£100.00"),
            ])
        )
        result = balance(journal)
        self.assertIn("assets:cash", result)
        self.assertEqual(result["assets:cash"]["£"], Decimal("0"))

    def test_method_on_journal_matches_function(self):
        via_method = self.journal.balance()
        via_function = balance(self.journal)
        self.assertEqual(via_method, via_function)

    def test_balance_is_balanced(self):
        # Sum of all amounts in a balanced journal must equal zero per commodity.
        result = balance(self.journal)
        total = sum(qty for d in result.values() for qty in d.values())
        self.assertEqual(total, Decimal("0"))


# ---------------------------------------------------------------------------
# register()
# ---------------------------------------------------------------------------

class TestRegisterReport(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)
        self.rows = register(self.journal)

    def test_row_count_no_query(self):
        # 6 transactions, each with 2 postings = 12 rows
        self.assertEqual(len(self.rows), 12)

    def test_rows_in_journal_order(self):
        dates = [r.date for r in self.rows]
        self.assertEqual(dates, sorted(dates))

    def test_first_row(self):
        row = self.rows[0]
        self.assertEqual(row.date, datetime.date(2024, 1, 1))
        self.assertEqual(row.description, "Opening balance")

    def test_running_balance_accumulates(self):
        # running_balance for each row = cumulative sum of all prior amounts + this one
        running = Decimal(0)
        for row in self.rows:
            running += row.amount.quantity
            self.assertEqual(row.running_balance, running)

    def test_running_balance_final(self):
        # Sum of all posting amounts in a balanced journal = 0
        self.assertEqual(self.rows[-1].running_balance, Decimal("0"))

    def test_date_filter(self):
        rows = register(
            self.journal,
            query=Query(
                date_from=datetime.date(2024, 2, 1),
                date_to=datetime.date(2024, 2, 28),
            ),
        )
        # Feb has 3 transactions × 2 postings = 6 rows
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertGreaterEqual(row.date, datetime.date(2024, 2, 1))
            self.assertLessEqual(row.date, datetime.date(2024, 2, 28))

    def test_account_filter(self):
        rows = register(self.journal, query=Query(account="expenses"))
        for row in rows:
            self.assertIn("expenses", row.account)

    def test_elided_posting_inferred_in_row(self):
        # The last Salary txn has income:salary as elided posting.
        # Its row should have amount.quantity == -3000.
        rows = register(self.journal, query=Query(account="income:salary"))
        salary_rows = [r for r in rows if r.account == "income:salary"]
        self.assertEqual(len(salary_rows), 2)
        amounts = sorted(r.amount.quantity for r in salary_rows)
        # Both salary postings should be -3000
        self.assertEqual(amounts, [Decimal("-3000.00"), Decimal("-3000.00")])

    def test_method_on_journal_matches_function(self):
        via_method = self.journal.register()
        via_function = register(self.journal)
        self.assertEqual(len(via_method), len(via_function))
        for m, f in zip(via_method, via_function):
            self.assertEqual(m.date, f.date)
            self.assertEqual(m.account, f.account)
            self.assertEqual(m.running_balance, f.running_balance)


# ---------------------------------------------------------------------------
# stats() — all existing tests preserved + query=None parity
# ---------------------------------------------------------------------------

class TestStatsSampleJournal(unittest.TestCase):
    """stats() against tests/fixtures/sample.journal."""

    def setUp(self):
        self.journal = load_journal(SAMPLE_JOURNAL)
        self.s = stats(self.journal)

    def test_transaction_count(self):
        self.assertEqual(self.s.transaction_count, 5)

    def test_included_files(self):
        self.assertEqual(self.s.included_files, 0)

    def test_date_range(self):
        self.assertEqual(self.s.date_range, (datetime.date(2024, 1, 1), datetime.date(2024, 1, 20)))

    def test_txns_span_days(self):
        # 2024-01-01 to 2024-01-20 inclusive = 20 days
        self.assertEqual(self.s.txns_span_days, 20)

    def test_account_depth(self):
        # assets:bank:checking has depth 3
        self.assertGreaterEqual(self.s.account_depth, 3)

    def test_commodity_count(self):
        self.assertEqual(self.s.commodity_count, 1)

    def test_commodities_list(self):
        self.assertIn("£", self.s.commodities)

    def test_price_count(self):
        self.assertEqual(self.s.price_count, 0)

    def test_payee_count(self):
        # 5 unique descriptions in sample.journal
        self.assertEqual(self.s.payee_count, 5)

    def test_account_count(self):
        # assets:bank:checking, equity:opening-balances, income:salary,
        # expenses:food:groceries, assets:bank:savings, expenses:food:coffee = 6
        self.assertEqual(self.s.account_count, 6)

    def test_source_file_set(self):
        self.assertIsNotNone(self.s.source_file)


class TestStatsEmptyJournal(unittest.TestCase):
    """stats() with no transactions."""

    def setUp(self):
        self.s = stats(parse_string(""))

    def test_transaction_count(self):
        self.assertEqual(self.s.transaction_count, 0)

    def test_date_range_none(self):
        self.assertIsNone(self.s.date_range)

    def test_last_txn_date_none(self):
        self.assertIsNone(self.s.last_txn_date)

    def test_txns_span_days_none(self):
        self.assertIsNone(self.s.txns_span_days)

    def test_account_count_zero(self):
        self.assertEqual(self.s.account_count, 0)

    def test_commodity_count_zero(self):
        self.assertEqual(self.s.commodity_count, 0)

    def test_txns_per_day_zero(self):
        self.assertEqual(self.s.txns_per_day, 0.0)

    def test_payee_count_zero(self):
        self.assertEqual(self.s.payee_count, 0)


class TestStatsDateRangeAndSpan(unittest.TestCase):
    """date_range, txns_span_days, and txns_per_day computed correctly."""

    def setUp(self):
        journal_text = """\
2024-03-01 First
    assets:cash  £10.00
    equity:open  -£10.00

2024-03-11 Second
    assets:cash  £20.00
    equity:open  -£20.00
"""
        self.s = stats(parse_string(journal_text))

    def test_date_range(self):
        self.assertEqual(
            self.s.date_range,
            (datetime.date(2024, 3, 1), datetime.date(2024, 3, 11)),
        )

    def test_txns_span_days(self):
        # 2024-03-01 to 2024-03-11 inclusive = 11 days
        self.assertEqual(self.s.txns_span_days, 11)

    def test_txns_per_day(self):
        # 2 transactions over 11 days
        self.assertAlmostEqual(self.s.txns_per_day, 2 / 11)

    def test_last_txn_date(self):
        self.assertEqual(self.s.last_txn_date, datetime.date(2024, 3, 11))

    def test_last_txn_days_ago_non_negative(self):
        self.assertGreaterEqual(self.s.last_txn_days_ago, 0)


class TestStatsMultipleCommodities(unittest.TestCase):
    """commodity_count and commodities list with two symbols."""

    def setUp(self):
        journal_text = """\
2024-01-01 Sterling purchase
    assets:gbp   £100.00
    assets:usd   -150.00 USD

2024-01-02 Another
    assets:gbp   £50.00
    assets:usd   -75.00 USD
"""
        self.s = stats(parse_string(journal_text))

    def test_commodity_count(self):
        self.assertEqual(self.s.commodity_count, 2)

    def test_commodities_contains_both(self):
        self.assertIn("£", self.s.commodities)
        self.assertIn("USD", self.s.commodities)

    def test_commodities_sorted(self):
        self.assertEqual(self.s.commodities, sorted(self.s.commodities))


class TestStatsPayeeDeduplication(unittest.TestCase):
    """payee_count deduplicates repeated descriptions."""

    def setUp(self):
        journal_text = """\
2024-01-01 Coffee
    expenses:coffee  £3.00
    assets:cash      -£3.00

2024-01-02 Coffee
    expenses:coffee  £3.50
    assets:cash      -£3.50

2024-01-03 Lunch
    expenses:food  £8.00
    assets:cash    -£8.00
"""
        self.s = stats(parse_string(journal_text))

    def test_payee_count(self):
        # "Coffee" appears twice but counts once; "Lunch" is distinct → 2
        self.assertEqual(self.s.payee_count, 2)


class TestStatsAccountDepth(unittest.TestCase):
    """account_depth equals the maximum colon-segment depth."""

    def setUp(self):
        journal_text = """\
2024-01-01 Deep account
    a:b:c:d  £1.00
    equity   -£1.00
"""
        self.s = stats(parse_string(journal_text))

    def test_account_depth(self):
        # a:b:c:d has 4 segments; equity has 1
        self.assertEqual(self.s.account_depth, 4)


class TestStatsModuleLevel(unittest.TestCase):
    """journal.stats() (method on Journal) returns same result as reports.stats()."""

    def test_module_level_call(self):
        journal = load_journal(SAMPLE_JOURNAL)
        via_function = stats(journal)
        via_method = journal.stats()
        self.assertEqual(via_function.transaction_count, via_method.transaction_count)
        self.assertEqual(via_function.account_count, via_method.account_count)
        self.assertEqual(via_function.commodities, via_method.commodities)
        self.assertEqual(via_function.date_range, via_method.date_range)

    def test_stats_query_none_identical_to_no_arg(self):
        journal = load_journal(SAMPLE_JOURNAL)
        self.assertEqual(
            stats(journal, query=None).transaction_count,
            stats(journal).transaction_count,
        )
        self.assertEqual(
            stats(journal, query=None).account_count,
            stats(journal).account_count,
        )

    def test_stats_date_filter_reduces_count(self):
        journal = load_journal(FILTERED_JOURNAL)
        # Full journal has 6 transactions; restrict to Jan only → 2
        result = stats(journal, query=Query(
            date_from=datetime.date(2024, 1, 1),
            date_to=datetime.date(2024, 1, 31),
        ))
        self.assertEqual(result.transaction_count, 2)


class TestStatsAccountFilterCorrection(unittest.TestCase):
    """Stage C Phase 8 (§5.1c): stats(query=Query(account=...)) now applies
    account/not_account filters -- previously a silently-ignored, documented
    gap. filtered.journal: 6 transactions; only "Supermarket" (2024-02-10)
    and "Coffee" (2024-02-20) have a posting touching "food"; every
    transaction has an assets:bank:checking posting.

    A before/after pair, as required by the design's own §11: one confirming
    the old silently-ignored behaviour no longer applies, one confirming the
    new filtered count.
    """

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_account_filter_no_longer_silently_ignored(self):
        # Before this phase, Query(account=...) had zero effect on stats --
        # transaction_count would equal the full, unfiltered 6. That must no
        # longer be true.
        full_count = stats(self.journal).transaction_count
        filtered_count = stats(self.journal, query=Query(account="food")).transaction_count
        self.assertNotEqual(filtered_count, full_count)

    def test_account_filter_matches_acct_query_ast_semantics(self):
        # New behaviour: identical to what -q "acct:food" stats (via
        # _query_ast) already did before this phase -- "any posting matches"
        # per-transaction semantics.
        from ledgerkit.query.ast import Acct
        result = stats(self.journal, query=Query(account="food"))
        expected = stats(self.journal, _query_ast=Acct("food"))
        self.assertEqual(result.transaction_count, 2)
        self.assertEqual(result.transaction_count, expected.transaction_count)

    def test_not_account_filter_now_applied(self):
        # Every transaction in filtered.journal has an assets:bank:checking
        # posting, so excluding "assets" now excludes every transaction --
        # previously this field had no effect at all (transaction_count
        # would have stayed 6).
        result = stats(self.journal, query=Query(not_account="assets"))
        self.assertEqual(result.transaction_count, 0)


# ---------------------------------------------------------------------------
# ReportSpec and ReportSection dataclasses
# ---------------------------------------------------------------------------

class TestReportSpecDataclasses(unittest.TestCase):

    def test_frozen_report_section(self):
        section = ledgerkit.ReportSection(name="Expenses", accounts=("expenses",))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            section.name = "Changed"  # type: ignore[misc]

    def test_frozen_report_spec(self):
        spec = ledgerkit.ReportSpec(
            name="Test",
            sections=(ledgerkit.ReportSection("S", accounts=("a",)),),
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            spec.name = "Changed"  # type: ignore[misc]

    def test_report_section_result_is_mutable(self):
        from ledgerkit.reports import ReportSectionResult
        section = ledgerkit.ReportSection(name="S", accounts=("a",))
        result = ReportSectionResult(section=section, rows={}, subtotal=Decimal(0))
        result.subtotal = Decimal(42)  # must not raise
        self.assertEqual(result.subtotal, Decimal(42))

    def test_import_from_ledgerkit(self):
        # All new public symbols must be importable from the top-level package.
        from ledgerkit import (  # noqa: F401
            Query,
            ReportSection,
            ReportSpec,
            ReportSectionResult,
            balance_from_spec,
        )

    def test_construct_multi_section_spec(self):
        spec = ledgerkit.ReportSpec(
            name="Income Statement",
            sections=(
                ledgerkit.ReportSection("Income", accounts=("income",), invert=True),
                ledgerkit.ReportSection("Expenses", accounts=("expenses",)),
            ),
        )
        self.assertEqual(len(spec.sections), 2)
        self.assertEqual(spec.sections[0].name, "Income")
        self.assertTrue(spec.sections[0].invert)
        self.assertFalse(spec.sections[1].invert)


# ---------------------------------------------------------------------------
# balance_from_spec()
# ---------------------------------------------------------------------------

class TestBalanceFromSpec(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def _income_expenses_spec(self) -> ledgerkit.ReportSpec:
        return ledgerkit.ReportSpec(
            name="Income Statement",
            sections=(
                ledgerkit.ReportSection("Income",   accounts=("income",),   invert=True),
                ledgerkit.ReportSection("Expenses", accounts=("expenses",)),
            ),
        )

    def test_single_section_rows_and_subtotal(self):
        spec = ledgerkit.ReportSpec(
            name="Expenses only",
            sections=(
                ledgerkit.ReportSection("Expenses", accounts=("expenses",)),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        self.assertEqual(len(results), 1)
        section_result = results[0]
        self.assertIn("expenses:housing:rent", section_result.rows)
        self.assertIn("expenses:food:groceries", section_result.rows)
        self.assertIn("expenses:food:coffee", section_result.rows)
        # subtotal = 1200 + 150 + 9 = 1359
        self.assertEqual(section_result.subtotal, Decimal("1359.00"))

    def test_single_section_invert(self):
        spec = ledgerkit.ReportSpec(
            name="Income",
            sections=(
                ledgerkit.ReportSection("Income", accounts=("income",), invert=True),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        section_result = results[0]
        # income:salary raw = -6000; inverted = +6000
        self.assertEqual(section_result.rows["income:salary"], Decimal("6000.00"))
        self.assertEqual(section_result.subtotal, Decimal("6000.00"))

    def test_multi_section_returns_one_result_per_section(self):
        spec = self._income_expenses_spec()
        results = balance_from_spec(self.journal, spec)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].section.name, "Income")
        self.assertEqual(results[1].section.name, "Expenses")

    def test_multi_section_correct_values(self):
        spec = self._income_expenses_spec()
        results = balance_from_spec(self.journal, spec)
        income_result = results[0]
        expense_result = results[1]
        self.assertEqual(income_result.subtotal, Decimal("6000.00"))
        self.assertEqual(expense_result.subtotal, Decimal("1359.00"))

    def test_grand_total_arithmetic(self):
        spec = self._income_expenses_spec()
        results = balance_from_spec(self.journal, spec)
        grand_total = sum(r.subtotal for r in results)
        # income (inverted) = +6000, expenses = +1359; sum of all section subtotals = 7359
        self.assertEqual(grand_total, Decimal("7359.00"))

    def test_section_depth_overrides_outer_query(self):
        spec = ledgerkit.ReportSpec(
            name="Expenses at depth 2",
            sections=(
                ledgerkit.ReportSection("Expenses", accounts=("expenses",), depth=2),
            ),
        )
        # Outer query has no depth; section depth=2 truncates to expenses:food, expenses:housing
        results = balance_from_spec(self.journal, spec, query=Query(depth=3))
        section_result = results[0]
        self.assertIn("expenses:food", section_result.rows)
        self.assertIn("expenses:housing", section_result.rows)
        self.assertNotIn("expenses:food:groceries", section_result.rows)
        # expenses:food = 150 + 9 = 159
        self.assertEqual(section_result.rows["expenses:food"], Decimal("159.00"))

    def test_outer_query_date_filter_applies_to_all_sections(self):
        spec = self._income_expenses_spec()
        # Restrict to Jan only — only Opening balance and Salary txns
        results = balance_from_spec(
            self.journal,
            spec,
            query=Query(
                date_from=datetime.date(2024, 1, 1),
                date_to=datetime.date(2024, 1, 31),
            ),
        )
        income_result = results[0]
        expense_result = results[1]
        # Only one salary in Jan → income:salary raw = -3000, inverted = +3000
        self.assertEqual(income_result.subtotal, Decimal("3000.00"))
        # No expense transactions in Jan
        self.assertEqual(expense_result.subtotal, Decimal("0"))

    def test_section_exclude_omits_matching_accounts(self):
        spec = ledgerkit.ReportSpec(
            name="Food only",
            sections=(
                ledgerkit.ReportSection(
                    "Food",
                    accounts=("expenses",),
                    exclude=("housing",),
                ),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        section_result = results[0]
        self.assertNotIn("expenses:housing:rent", section_result.rows)
        self.assertIn("expenses:food:groceries", section_result.rows)
        self.assertIn("expenses:food:coffee", section_result.rows)
        # subtotal = 150 + 9 = 159
        self.assertEqual(section_result.subtotal, Decimal("159.00"))

    def test_section_multiple_accounts_patterns_or_union(self):
        spec = ledgerkit.ReportSpec(
            name="Income and Housing",
            sections=(
                ledgerkit.ReportSection(
                    "Mixed",
                    accounts=("income:salary", "expenses:housing"),
                ),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        section_result = results[0]
        self.assertIn("income:salary", section_result.rows)
        self.assertIn("expenses:housing:rent", section_result.rows)
        self.assertNotIn("expenses:food:groceries", section_result.rows)

    def test_elided_posting_inferred_in_spec(self):
        # income:salary in the last Salary txn is elided; spec should include it.
        spec = ledgerkit.ReportSpec(
            name="Income",
            sections=(
                ledgerkit.ReportSection("Income", accounts=("income",), invert=True),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        # Both salary postings contribute; total inverted = +6000
        self.assertEqual(results[0].subtotal, Decimal("6000.00"))

    def test_empty_section_has_zero_subtotal(self):
        spec = ledgerkit.ReportSpec(
            name="No match",
            sections=(
                ledgerkit.ReportSection("Nothing", accounts=("nonexistent:account",)),
            ),
        )
        results = balance_from_spec(self.journal, spec)
        self.assertEqual(results[0].subtotal, Decimal("0"))
        self.assertEqual(results[0].rows, {})


# ---------------------------------------------------------------------------
# balance_from_spec() — outer query convergence (Stage C Phase 8, §5.1b):
# the outer query.account/.not_account/.payee now reach the same canonical
# ledgerkit.query.compat._query_to_ast + matches_posting engine as balance/
# register/accounts/stats, replacing balance_from_spec's own separate inline
# _matches_pattern-based check. ReportSection.accounts/.exclude remain the
# one deliberately separate construct (still _matches_pattern, refactored
# to route through compile_hledger_regex -- see TestReportSectionHledger
# RegexValidation below).
# ---------------------------------------------------------------------------

class TestBalanceFromSpecOuterQueryConvergence(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def _expenses_spec(self) -> ledgerkit.ReportSpec:
        return ledgerkit.ReportSpec(
            name="Expenses only",
            sections=(
                ledgerkit.ReportSection("Expenses", accounts=("expenses",)),
            ),
        )

    def test_outer_query_account_filter_still_works(self):
        # Parity check: an ordinary outer query.account filter still narrows
        # results exactly as before the migration to the canonical engine.
        spec = self._expenses_spec()
        results = balance_from_spec(self.journal, spec, query=Query(account="food"))
        section_result = results[0]
        self.assertIn("expenses:food:groceries", section_result.rows)
        self.assertIn("expenses:food:coffee", section_result.rows)
        self.assertNotIn("expenses:housing:rent", section_result.rows)

    def test_outer_query_not_account_filter_still_works(self):
        spec = self._expenses_spec()
        results = balance_from_spec(self.journal, spec, query=Query(not_account="food"))
        section_result = results[0]
        self.assertIn("expenses:housing:rent", section_result.rows)
        self.assertNotIn("expenses:food:groceries", section_result.rows)
        self.assertNotIn("expenses:food:coffee", section_result.rows)

    def test_outer_query_payee_filter_still_works(self):
        spec = self._expenses_spec()
        results = balance_from_spec(self.journal, spec, query=Query(payee="Coffee"))
        section_result = results[0]
        self.assertIn("expenses:food:coffee", section_result.rows)
        self.assertNotIn("expenses:food:groceries", section_result.rows)
        self.assertNotIn("expenses:housing:rent", section_result.rows)

    def test_outer_query_date_filter_parity_with_prior_behaviour(self):
        # Existing coverage (TestBalanceFromSpec.
        # test_outer_query_date_filter_applies_to_all_sections) already
        # exercises this; repeated here to anchor it explicitly to the
        # outer-query convergence (date filtering moved from a per-
        # transaction short-circuit to a per-posting DateSpan check --
        # a disclosed, harmless performance difference only, per §5.1b).
        spec = self._income_expenses_spec_compat()
        results = balance_from_spec(
            self.journal,
            spec,
            query=Query(date_from=datetime.date(2024, 1, 1), date_to=datetime.date(2024, 1, 31)),
        )
        income_result, expense_result = results
        self.assertEqual(income_result.subtotal, Decimal("3000.00"))
        self.assertEqual(expense_result.subtotal, Decimal("0"))

    def _income_expenses_spec_compat(self) -> ledgerkit.ReportSpec:
        return ledgerkit.ReportSpec(
            name="Income Statement",
            sections=(
                ledgerkit.ReportSection("Income",   accounts=("income",),   invert=True),
                ledgerkit.ReportSection("Expenses", accounts=("expenses",)),
            ),
        )

    def test_excluded_construct_in_outer_query_raises(self):
        # Option A convergence: an excluded HledgerRegex construct in the
        # outer query now raises here too, exactly like balance()/register().
        spec = self._expenses_spec()
        with self.assertRaises(QueryParseError):
            balance_from_spec(self.journal, spec, query=Query(account=r"\d+"))

    def test_excluded_construct_raises_even_with_zero_sections(self):
        # Eager validation: the outer query is translated once, before the
        # per-section loop -- it must raise even when spec.sections is empty.
        spec = ledgerkit.ReportSpec(name="Empty", sections=())
        with self.assertRaises(QueryParseError):
            balance_from_spec(self.journal, spec, query=Query(account=r"\d+"))


# ---------------------------------------------------------------------------
# ReportSection.accounts/.exclude -- the one construct still using
# _matches_pattern, now HledgerRegex-validated (Stage C Phase 8, §5.1b).
# ---------------------------------------------------------------------------

class TestReportSectionHledgerRegexValidation(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_excluded_construct_in_section_accounts_raises(self):
        spec = ledgerkit.ReportSpec(
            name="Bad",
            sections=(ledgerkit.ReportSection("Bad", accounts=(r"\d+",)),),
        )
        with self.assertRaises(Exception):
            balance_from_spec(self.journal, spec)

    def test_empty_pattern_in_section_accounts_raises(self):
        spec = ledgerkit.ReportSpec(
            name="Bad",
            sections=(ledgerkit.ReportSection("Bad", accounts=("",)),),
        )
        with self.assertRaises(Exception):
            balance_from_spec(self.journal, spec)

    def test_excluded_construct_in_section_exclude_raises(self):
        spec = ledgerkit.ReportSpec(
            name="Bad",
            sections=(
                ledgerkit.ReportSection("Bad", accounts=("expenses",), exclude=(r"\d+",)),
            ),
        )
        with self.assertRaises(Exception):
            balance_from_spec(self.journal, spec)

    def test_ordinary_patterns_still_accepted(self):
        # Regression guard: the refactor to compile_hledger_regex must not
        # break any ordinary, already-portable pattern.
        spec = ledgerkit.ReportSpec(
            name="Food",
            sections=(ledgerkit.ReportSection("Food", accounts=("expenses",), exclude=("housing",)),),
        )
        results = balance_from_spec(self.journal, spec)
        self.assertIn("expenses:food:groceries", results[0].rows)
        self.assertNotIn("expenses:housing:rent", results[0].rows)


# ---------------------------------------------------------------------------
# Deprecated Journal.balance(accounts=[...])/.register(accounts=[...]) shim
# (Stage C Phase 8, §5.1a) -- zero/one/many, all three explicit cases.
# Previously untested for the zero- and many-accounts cases (§2 of the
# design), which is exactly where a real bug (Or(()) matching nothing for
# accounts=[], and a (?:...)-based synthesis rejected outright by
# HledgerRegex for two-or-more accounts) was found and fixed.
# ---------------------------------------------------------------------------

class TestDeprecatedAccountsShim(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_balance_zero_accounts_is_no_filter(self):
        # Must behave exactly like query=None/no filter -- explicitly NOT
        # Or(()), which would match nothing (the opposite of "no filter").
        via_shim = self.journal.balance(accounts=[])
        via_no_filter = self.journal.balance()
        self.assertEqual(via_shim, via_no_filter)
        self.assertTrue(len(via_shim) > 0)

    def test_register_zero_accounts_is_no_filter(self):
        via_shim = self.journal.register(accounts=[])
        via_no_filter = self.journal.register()
        self.assertEqual(len(via_shim), len(via_no_filter))
        self.assertTrue(len(via_shim) > 0)

    def test_balance_one_account_unchanged_regex_passthrough(self):
        via_shim = self.journal.balance(accounts=["food"])
        via_query = self.journal.balance(query=Query(account="food"))
        self.assertEqual(via_shim, via_query)
        self.assertIn("expenses:food:groceries", via_shim)
        self.assertIn("expenses:food:coffee", via_shim)

    def test_register_one_account_unchanged_regex_passthrough(self):
        via_shim = self.journal.register(accounts=["food"])
        via_query = self.journal.register(query=Query(account="food"))
        self.assertEqual([r.account for r in via_shim], [r.account for r in via_query])

    def test_balance_many_accounts_or_union_does_not_raise(self):
        # Two-or-more accounts: previously synthesized a (?:...)-based regex
        # string, which HledgerRegex now rejects outright (Option A) -- this
        # must NOT raise, and must build an Or(...) AST instead.
        result = self.journal.balance(accounts=["food", "housing"])
        self.assertIn("expenses:food:groceries", result)
        self.assertIn("expenses:food:coffee", result)
        self.assertIn("expenses:housing:rent", result)
        self.assertNotIn("assets:bank:checking", result)

    def test_register_many_accounts_or_union_does_not_raise(self):
        rows = self.journal.register(accounts=["food", "housing"])
        accounts_seen = {r.account for r in rows}
        self.assertTrue(accounts_seen <= {
            "expenses:food:groceries", "expenses:food:coffee", "expenses:housing:rent",
        })
        self.assertTrue(len(rows) > 0)

    def test_balance_one_account_excluded_construct_now_raises(self):
        # Corrected compat-register claim (LK-COMPAT-QUERY-SHIM-001 item 6):
        # a single-account value using a Python-only regex construct outside
        # HledgerRegex previously reached the old permissive matcher and was
        # accepted -- it now intentionally raises, the same Option A
        # consequence as Query.account/.payee/.not_account generally. This
        # was a real gap in test coverage found during the compat-register
        # correction's own independent re-verification.
        with self.assertRaises(QueryParseError):
            self.journal.balance(accounts=[r"\d+"])

    def test_register_one_account_excluded_construct_now_raises(self):
        with self.assertRaises(QueryParseError):
            self.journal.register(accounts=[r"\d+"])

    def test_balance_many_accounts_matches_union_of_single_account_queries(self):
        many = self.journal.balance(accounts=["food", "housing"])
        food = self.journal.balance(query=Query(account="food"))
        housing = self.journal.balance(query=Query(account="housing"))
        expected_keys = set(food.keys()) | set(housing.keys())
        self.assertEqual(set(many.keys()), expected_keys)

    def test_many_accounts_with_metacharacter_names_escaped_and_valid(self):
        # re.escape'd literals must themselves remain HledgerRegex-portable
        # (plain backslash-escaped literals are not an excluded construct)
        # and must not raise even though the account names below contain
        # regex metacharacters.
        journal = _journal(
            _txn("2024-01-01", "x", [
                ("assets.cash", "£10.00"),
                ("equity.open", "-£10.00"),
            ])
        )
        result = journal.balance(accounts=["assets.cash", "equity.open"])
        self.assertIn("assets.cash", result)
        self.assertIn("equity.open", result)


# ---------------------------------------------------------------------------
# Query -- Option A HledgerRegex strictness (Stage C Phase 8, §6): Query.
# account/.not_account/.payee now converge onto the same compile_hledger_
# regex validation acct:/desc: already use, across every converged consumer.
# ---------------------------------------------------------------------------

class TestQueryHledgerRegexStrictness(unittest.TestCase):

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)
        self.empty_journal = parse_string("")

    def test_balance_excluded_construct_raises(self):
        with self.assertRaises(QueryParseError):
            balance(self.journal, query=Query(account=r"\d+"))

    def test_register_excluded_construct_raises(self):
        with self.assertRaises(QueryParseError):
            register(self.journal, query=Query(account=r"\d+"))

    def test_accounts_excluded_construct_raises(self):
        with self.assertRaises(QueryParseError):
            accounts(self.journal, query=Query(account=r"\d+"))

    def test_stats_excluded_construct_raises(self):
        with self.assertRaises(QueryParseError):
            stats(self.journal, query=Query(account=r"\d+"))

    def test_matches_same_error_as_query_ast_string_form(self):
        # Genuine convergence, not merely "similar-looking" behaviour: a
        # Query.account value using an excluded construct now raises the
        # same kind of error a `-q "acct:\d+"` query already does.
        from ledgerkit.query.parser import parse as parse_query_string
        with self.assertRaises(QueryParseError):
            parse_query_string(r"acct:\d+")
        with self.assertRaises(QueryParseError):
            balance(self.journal, query=Query(account=r"\d+"))

    def test_raises_deterministically_even_against_empty_journal(self):
        # Eager validation regression guard (§5.1a): the old bare-Acct(...)
        # design would only have failed lazily, at evaluation time -- which,
        # for an empty journal (zero transactions/postings), would never be
        # reached at all, silently masking an invalid pattern.
        self.assertEqual(len(self.empty_journal.transactions), 0)
        with self.assertRaises(QueryParseError):
            balance(self.empty_journal, query=Query(account=r"\d+"))
        with self.assertRaises(QueryParseError):
            register(self.empty_journal, query=Query(account=r"\d+"))
        with self.assertRaises(QueryParseError):
            accounts(self.empty_journal, query=Query(account=r"\d+"))
        with self.assertRaises(QueryParseError):
            stats(self.empty_journal, query=Query(account=r"\d+"))

    def test_empty_account_pattern_raises_stage_c_phase_7_consistency(self):
        # Matches -q "acct:"'s own Phase 7 behaviour -- rather than silently
        # matching every posting, as Query(account="") used to.
        with self.assertRaises(QueryParseError):
            balance(self.journal, query=Query(account=""))

    def test_empty_payee_pattern_raises(self):
        with self.assertRaises(QueryParseError):
            balance(self.journal, query=Query(payee=""))

    def test_empty_not_account_pattern_raises(self):
        with self.assertRaises(QueryParseError):
            balance(self.journal, query=Query(not_account=""))

    def test_ordinary_valid_patterns_are_unaffected(self):
        # Regression guard: every existing direct Query(...) construction in
        # this file (plain substrings and HledgerRegex-portable anchors)
        # must continue to work unchanged.
        result = balance(self.journal, query=Query(account="^expenses"))
        self.assertIn("expenses:food:groceries", result)


# ---------------------------------------------------------------------------
# balance() — multi-commodity and tree mode
# ---------------------------------------------------------------------------

MULTICOMMODITY_JOURNAL = os.path.join(FIXTURES_DIR, "multicommodity.journal")


class TestBalanceMultiCommodity(unittest.TestCase):
    """balance() with multi-commodity journals and elided postings."""

    def setUp(self):
        self.journal = load_journal(MULTICOMMODITY_JOURNAL)

    def test_balance_returns_nested_dict(self):
        from collections.abc import Mapping
        result = balance(self.journal)
        self.assertIsInstance(result, Mapping)
        for v in result.values():
            self.assertIsInstance(v, dict)

    def test_multicommodity_elided_resolves_correctly(self):
        # equity:opening-balances has one elided posting with 3 commodities.
        result = balance(self.journal)
        equity = result["equity:opening-balances"]
        self.assertIn("£", equity)
        self.assertIn("$", equity)
        self.assertIn("€", equity)
        # Each should be the negation of the total in that commodity.
        self.assertEqual(equity["£"], Decimal("-10000.00"))
        self.assertEqual(equity["$"], Decimal("-5000.00"))
        self.assertEqual(equity["€"], Decimal("-2000.00"))

    def test_balance_is_zero_per_commodity(self):
        result = balance(self.journal)
        totals: dict[str, Decimal] = {}
        for commodity_map in result.values():
            for comm, qty in commodity_map.items():
                totals[comm] = totals.get(comm, Decimal(0)) + qty
        for comm, total in totals.items():
            self.assertEqual(total, Decimal("0"), f"commodity {comm} does not net to 0")

    def test_single_commodity_account_has_one_key(self):
        result = balance(self.journal)
        self.assertEqual(set(result["expenses:rent"].keys()), {"£"})
        self.assertEqual(set(result["expenses:software"].keys()), {"$"})

    def test_balance_tree_returns_list(self):
        result = balance(self.journal, tree=True)
        self.assertIsInstance(result, list)

    def test_balance_tree_contains_balance_rows(self):
        from ledgerkit.models import BalanceRow
        result = balance(self.journal, tree=True)
        for row in result:
            self.assertIsInstance(row, BalanceRow)

    def test_balance_tree_implicit_parents_present(self):
        result = balance(self.journal, tree=True)
        accounts_in_tree = {row.account for row in result}
        # "expenses" should appear as an implicit parent of expenses:rent, expenses:software etc.
        self.assertIn("expenses", accounts_in_tree)
        self.assertIn("assets", accounts_in_tree)

    def test_balance_tree_is_subtotal_for_implicit_parents(self):
        result = balance(self.journal, tree=True)
        expenses_row = next(r for r in result if r.account == "expenses")
        self.assertTrue(expenses_row.is_subtotal)

    def test_balance_tree_is_subtotal_false_for_leaf_accounts(self):
        result = balance(self.journal, tree=True)
        rent_row = next(r for r in result if r.account == "expenses:rent")
        self.assertFalse(rent_row.is_subtotal)

    def test_balance_tree_depth_correct(self):
        result = balance(self.journal, tree=True)
        depth_map = {row.account: row.depth for row in result}
        self.assertEqual(depth_map["expenses"], 0)
        self.assertEqual(depth_map["expenses:rent"], 1)

    def test_balance_tree_amounts_aggregate_descendants(self):
        # "expenses" subtotal should include rent (£), software ($), conference (€).
        result = balance(self.journal, tree=True)
        expenses = next(r for r in result if r.account == "expenses")
        self.assertIn("£", expenses.amounts)
        self.assertIn("$", expenses.amounts)
        self.assertIn("€", expenses.amounts)

    def test_balance_tree_alphabetical_order(self):
        result = balance(self.journal, tree=True)
        accounts_list = [row.account for row in result]
        self.assertEqual(accounts_list, sorted(accounts_list))

    def test_balance_flat_false_returns_dict(self):
        from collections.abc import Mapping
        result = balance(self.journal, tree=False)
        self.assertIsInstance(result, Mapping)

    def test_register_multicommodity_elided_produces_multiple_rows(self):
        # The opening balances transaction has 1 elided posting with 3 commodities.
        # register() should produce 3 extra rows for the resolved elided posting.
        from ledgerkit.reports import register
        rows = register(self.journal)
        equity_rows = [r for r in rows if r.account == "equity:opening-balances"]
        # 3 commodities → 3 synthetic postings → 3 rows for equity
        self.assertEqual(len(equity_rows), 3)
        commodities = {r.amount.commodity for r in equity_rows}
        self.assertEqual(commodities, {"£", "$", "€"})


# ---------------------------------------------------------------------------
# _query_ast (Stage C Phase 2 — private, internal-only ledgerkit.query
# integration; see knowledge/DECISIONS.md, 2026-09-16)
# ---------------------------------------------------------------------------

class TestQueryAstIntegration(unittest.TestCase):
    """_query_ast support across accounts/balance/register/stats.

    filtered.journal: 6 transactions, 2024-01-01..2024-03-05. Two are
    cleared (2024-01-15, 2024-03-05 Salary); the rest are unmarked.
    """

    def setUp(self):
        self.journal = load_journal(FILTERED_JOURNAL)

    def test_accounts_filters_by_query_ast(self):
        from ledgerkit.query.ast import Acct
        result = accounts(self.journal, _query_ast=Acct("food"))
        self.assertEqual(result, ["expenses:food:coffee", "expenses:food:groceries"])

    def test_accounts_no_match_query_ast_returns_empty(self):
        from ledgerkit.query.ast import Acct
        result = accounts(self.journal, _query_ast=Acct("doesnotexist"))
        self.assertEqual(result, [])

    def test_balance_filters_by_query_ast(self):
        from ledgerkit.query.ast import Acct
        result = balance(self.journal, _query_ast=Acct("food"))
        self.assertEqual(set(result.keys()), {"expenses:food:coffee", "expenses:food:groceries"})
        self.assertEqual(result["expenses:food:coffee"]["£"], Decimal("9.00"))

    def test_balance_query_depth_truncates_rather_than_excludes(self):
        # Stage C Phase 5: _query_depth (from -q's depth: term) truncates
        # and aggregates displayed account names, matching hledger's real
        # --depth/depth: behaviour — it never excludes a posting. Confirmed
        # live against the pinned hledger 1.52.4 binary; see
        # dev-docs/planning/core-redefinition/
        # 21-stage-c-phase-5-depth-and-verification-plan.md §1.3.
        from ledgerkit.query.depth import DepthSpec
        result = balance(self.journal, _query_depth=DepthSpec(flat=1))
        self.assertNotIn("expenses:food:coffee", result)
        self.assertNotIn("expenses:housing:rent", result)
        self.assertIn("expenses", result)  # rolled up, not dropped
        self.assertIn("assets", result)
        for acct in result:
            self.assertNotIn(":", acct)
        # Nothing is lost: the rolled-up "expenses" total still reflects
        # every deeper posting that fed into it.
        self.assertEqual(
            result["expenses"]["£"],
            Decimal("1200.00") + Decimal("150.00") + Decimal("9.00"),
        )

    def test_balance_query_depth_custom_regex(self):
        from ledgerkit.query.depth import DepthSpec
        result = balance(self.journal, _query_depth=DepthSpec(by_pattern=(("expenses", 2),)))
        # expenses:* collapses to depth 2; assets:bank:checking (not
        # matching "expenses") is untouched.
        self.assertIn("expenses:food", result)
        self.assertIn("expenses:housing", result)
        self.assertIn("assets:bank:checking", result)
        self.assertNotIn("expenses:food:coffee", result)

    def test_accounts_query_depth_clips_and_deduplicates(self):
        from ledgerkit.query.depth import DepthSpec
        result = accounts(self.journal, _query_depth=DepthSpec(flat=2))
        self.assertIn("expenses:food", result)
        self.assertNotIn("expenses:food:coffee", result)
        self.assertNotIn("expenses:food:groceries", result)
        # both expenses:food:coffee and expenses:food:groceries clip to
        # the same "expenses:food" — deduplicated, not two rows.
        self.assertEqual(result.count("expenses:food"), 1)

    def test_register_query_depth_clips_label_never_excludes(self):
        from ledgerkit.query.depth import DepthSpec
        rows = register(self.journal, _query_depth=DepthSpec(flat=1))
        # every posting still present as its own row (register never
        # aggregates, unlike balance) — only the displayed account label
        # is clipped.
        unfiltered = register(self.journal)
        self.assertEqual(len(rows), len(unfiltered))
        self.assertTrue(any(r.account == "expenses" for r in rows))
        self.assertFalse(any(":" in r.account for r in rows))

    def test_stats_query_depth_excludes_rather_than_clips(self):
        # stats is a genuine, source-confirmed exception (hledger's own
        # Ledger.hs:ledgerFromJournal doc-comment: "the ledger's journal
        # will be depth limited [excluded], but the ledger's account tree
        # will not [clipped]") — unlike balance/register/accounts, its
        # account_count/account_depth fields come from EXCLUDING accounts
        # deeper than the limit, never from clipping/aggregating them.
        # Confirmed live against the pinned hledger 1.52.4 binary; see
        # dev-docs/planning/core-redefinition/
        # 21-stage-c-phase-5-depth-and-verification-plan.md §1.3.
        from ledgerkit.query.depth import DepthSpec
        s_full = stats(self.journal)
        s_depth2 = stats(self.journal, _query_depth=DepthSpec(flat=2))
        # filtered.journal accounts at depth <=2: equity:opening-balances,
        # income:salary (both depth 2) — assets:bank:checking (depth 3)
        # and the depth-3 expenses accounts are excluded, not clipped to
        # "assets"/"expenses".
        self.assertLess(s_depth2.account_count, s_full.account_count)
        self.assertEqual(s_depth2.account_count, 2)
        self.assertEqual(s_depth2.account_depth, 2)

    def test_register_filters_by_query_ast(self):
        from ledgerkit.query.ast import Desc
        rows = register(self.journal, _query_ast=Desc("salary"))
        self.assertTrue(all("salary" in r.description.lower() for r in rows))
        self.assertTrue(len(rows) > 0)

    def test_register_status_query_ast(self):
        from ledgerkit.query.ast import Status, TxnStatus
        rows = register(self.journal, _query_ast=Status(TxnStatus.CLEARED))
        self.assertTrue(all(r.description == "Salary" for r in rows))

    def test_stats_filters_by_query_ast_via_matches_transaction(self):
        from ledgerkit.query.ast import Status, TxnStatus
        s = stats(self.journal, _query_ast=Status(TxnStatus.CLEARED))
        self.assertEqual(s.transaction_count, 2)

    def test_stats_unmarked_query_ast(self):
        from ledgerkit.query.ast import Status, TxnStatus
        s = stats(self.journal, _query_ast=Status(TxnStatus.UNMARKED))
        self.assertEqual(s.transaction_count, 4)

    def test_query_and_query_ast_combine_with_and(self):
        # Both supplied: a posting must satisfy both — Query(account=...)
        # AND the AST predicate, not either alone.
        from ledgerkit.query.ast import Desc
        result = accounts(
            self.journal,
            query=Query(account="expenses"),
            _query_ast=Desc("rent"),
        )
        self.assertEqual(result, ["expenses:housing:rent"])

    def test_query_and_query_ast_and_excludes_when_only_one_matches(self):
        from ledgerkit.query.ast import Desc
        # account="income" matches income:salary, but desc "rent" doesn't
        # match any Salary transaction — AND means no rows.
        result = accounts(
            self.journal,
            query=Query(account="income"),
            _query_ast=Desc("rent"),
        )
        self.assertEqual(result, [])

    def test_query_ast_none_is_unfiltered_regression(self):
        # Default (no _query_ast) must behave exactly as before this
        # integration — a plain regression check, not a new behaviour.
        self.assertEqual(accounts(self.journal), accounts(self.journal, _query_ast=None))
        self.assertEqual(balance(self.journal), balance(self.journal, _query_ast=None))
        self.assertEqual(
            [r.account for r in register(self.journal)],
            [r.account for r in register(self.journal, _query_ast=None)],
        )
        self.assertEqual(
            stats(self.journal).transaction_count,
            stats(self.journal, _query_ast=None).transaction_count,
        )


# ---------------------------------------------------------------------------
# tag:NAME[=REGEX] integration (Stage C Phase 6 — 23-tag-query-matching-
# design.md, 24-tag-query-matching-implementation-plan.md)
#
# tags.journal declares a "rate" tag at all four effective-tag sources with
# a DIFFERENT value at each (see the fixture's own header comment):
#   posting-own (first txn's assets:bank posting)          rate:1
#   commodity-propagated ($)                                rate:2
#   account-inherited (assets:bank + descendants)           rate:3
#   transaction-header (first txn)                          rate:4
#   posting-own, sibling txn, same account                  rate:5
#   posting-own, child account (assets:bank:savings)        rate:6
# ---------------------------------------------------------------------------

class TestQueryAstTagIntegration(unittest.TestCase):
    def setUp(self):
        self.journal = load_journal(TAGS_JOURNAL)

    # -- commodity-directive tag propagation --------------------------------

    def test_commodity_tag_propagates_to_postings_using_that_commodity(self):
        from ledgerkit.query.ast import Tag
        # Every posting in the fixture uses commodity "$" -- rate:2 (the
        # commodity's own declared tag) must match all of them at the
        # balance level, including postings with no account-level tag at
        # all (expenses:misc).
        result = balance(self.journal, _query_ast=Tag("rate", "2"))
        self.assertIn("assets:bank", result)
        self.assertIn("expenses:misc", result)
        self.assertIn("equity:opening-balances", result)

    # -- five same-name/different-value precedence pairs (design §2.7) ------

    def test_precedence_posting_vs_account(self):
        from ledgerkit.query.ast import Tag
        # rate:1 (posting-own) matches only that one posting's account;
        # rate:3 (account-inherited) matches every posting/descendant of
        # assets:bank, including the one whose OWN rate is different (1).
        r1 = balance(self.journal, _query_ast=Tag("rate", "1"))
        r3 = balance(self.journal, _query_ast=Tag("rate", "3"))
        self.assertEqual(set(r1.keys()), {"assets:bank"})
        self.assertEqual(set(r3.keys()), {"assets:bank", "assets:bank:savings"})

    def test_precedence_posting_vs_commodity(self):
        from ledgerkit.query.ast import Tag
        # rate:1 (posting-own) is narrower than rate:2 (commodity-wide) --
        # both independently matchable on the SAME posting.
        txn = self.journal.transactions[0]
        posting = txn.postings[0]
        self.assertTrue(matches_posting(Tag("rate", "1"), txn, posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("rate", "2"), txn, posting, journal=self.journal))

    def test_precedence_account_vs_commodity(self):
        from ledgerkit.query.ast import Tag
        # rate:3 (account) and rate:2 (commodity) both match the same
        # assets:bank posting independently.
        txn = self.journal.transactions[0]
        posting = txn.postings[0]
        self.assertTrue(matches_posting(Tag("rate", "3"), txn, posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("rate", "2"), txn, posting, journal=self.journal))

    def test_precedence_parent_account_vs_child_account_posting(self):
        from ledgerkit.query.ast import Tag
        # assets:bank:savings' own posting has rate:6; it ALSO inherits
        # rate:3 from its parent assets:bank -- both independently match
        # the exact same posting.
        child_txn = self.journal.transactions[2]
        child_posting = child_txn.postings[0]
        self.assertEqual(child_posting.account, "assets:bank:savings")
        self.assertTrue(matches_posting(Tag("rate", "6"), child_txn, child_posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("rate", "3"), child_txn, child_posting, journal=self.journal))

    def test_precedence_transaction_level_vs_other_source(self):
        from ledgerkit.query.ast import Tag
        # The first transaction's own header tag (rate:4) and its
        # posting's own tag (rate:1) both independently match that same
        # posting -- transaction-level tags are never shadowed by a
        # posting's own different-valued tag, or vice versa.
        txn = self.journal.transactions[0]
        posting = txn.postings[0]
        self.assertTrue(matches_posting(Tag("rate", "4"), txn, posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("rate", "1"), txn, posting, journal=self.journal))

    def test_no_shadowing_regression_naive_dedup_by_name_would_fail_this(self):
        from ledgerkit.query.ast import Tag
        # All six differently-valued "rate" tags in the fixture remain
        # independently discoverable via balance() -- a regression check
        # that nothing in the pipeline collapses same-named tags.
        for value, expected_accounts in [
            ("1", {"assets:bank"}),
            ("2", {"assets:bank", "assets:bank:savings", "expenses:misc", "equity:opening-balances"}),
            ("3", {"assets:bank", "assets:bank:savings"}),
            ("4", {"assets:bank", "equity:opening-balances"}),
            ("5", {"assets:bank"}),
            ("6", {"assets:bank:savings"}),
        ]:
            with self.subTest(value=value):
                result = balance(self.journal, _query_ast=Tag("rate", value))
                self.assertEqual(set(result.keys()), expected_accounts)

    # -- parent-account tag + commodity tag composing on the same posting ---

    def test_parent_account_tag_and_commodity_tag_compose_on_same_posting(self):
        from ledgerkit.query.ast import Tag
        # assets:bank:savings' posting has no account directive of its
        # own -- rate:3 reaches it only via parent-account inheritance,
        # and rate:2 reaches it only via commodity propagation. Neither
        # source is the posting's own literal comment (that's rate:6).
        child_txn = self.journal.transactions[2]
        child_posting = child_txn.postings[0]
        self.assertTrue(matches_posting(Tag("rate", "3"), child_txn, child_posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("rate", "2"), child_txn, child_posting, journal=self.journal))

    # -- accounts' own narrower four-way visibility split (design §2.5/§9.2) -

    def test_accounts_transaction_level_tag_is_visible(self):
        from ledgerkit.query.ast import Tag
        result = accounts(self.journal, _query_ast=Tag("rate", "4"))
        self.assertIn("assets:bank", result)

    def test_accounts_account_inherited_tag_is_visible(self):
        from ledgerkit.query.ast import Tag
        result = accounts(self.journal, _query_ast=Tag("rate", "3"))
        self.assertIn("assets:bank", result)
        self.assertIn("assets:bank:savings", result)

    def test_accounts_posting_own_tag_is_not_visible(self):
        from ledgerkit.query.ast import Tag
        # rate:1/rate:5/rate:6 are all posting-own tags -- none visible to
        # plain `accounts tag:X`.
        self.assertEqual(accounts(self.journal, _query_ast=Tag("rate", "1")), [])
        self.assertEqual(accounts(self.journal, _query_ast=Tag("rate", "5")), [])
        self.assertEqual(accounts(self.journal, _query_ast=Tag("rate", "6")), [])

    def test_accounts_commodity_propagated_tag_is_not_visible(self):
        from ledgerkit.query.ast import Tag
        self.assertEqual(accounts(self.journal, _query_ast=Tag("rate", "2")), [])

    # -- journal=None loud failure, exercised through the public report API -

    def test_query_ast_matches_posting_without_journal_raises(self):
        from ledgerkit.query.ast import Tag
        txn = self.journal.transactions[0]
        posting = txn.postings[0]
        with self.assertRaises(ValueError):
            matches_posting(Tag("rate", "1"), txn, posting)

    def test_query_ast_matches_transaction_without_journal_raises(self):
        from ledgerkit.query.ast import Tag
        with self.assertRaises(ValueError):
            matches_transaction(Tag("rate", "1"), self.journal.transactions[0])

    # -- stats/register also see the full effective-tags union --------------

    def test_stats_filters_transactions_by_tag(self):
        from ledgerkit.query.ast import Tag
        s = stats(self.journal, _query_ast=Tag("rate", "4"))
        self.assertEqual(s.transaction_count, 1)

    def test_register_filters_postings_by_tag(self):
        from ledgerkit.query.ast import Tag
        rows = register(self.journal, _query_ast=Tag("rate", "3"))
        self.assertTrue(all(r.account in ("assets:bank", "assets:bank:savings") for r in rows))
        self.assertEqual(len(rows), 3)  # two assets:bank postings + one assets:bank:savings


if __name__ == "__main__":
    unittest.main()

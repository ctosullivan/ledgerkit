"""Tests for ledgerkit pandas DataFrame export (optional dependency).

All tests are skipped when pandas is not installed.
"""

import os
import tempfile
import unittest
from decimal import Decimal

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

_SAMPLE_JOURNAL = """\
2024-01-01 Opening balance
    assets:bank:checking  £5,000.00
    equity:opening-balances

2024-01-15 Salary
    assets:bank:checking  £3,000.00
    income:salary

2024-02-01 Rent
    expenses:housing:rent  £1,200.00
    assets:bank:checking
"""

_MULTICOMMODITY_JOURNAL = """\
2024-01-01 Purchase
    expenses:food  £50.00
    expenses:travel  $100.00
    assets:bank
"""


def _make_journal(text: str):
    """Parse a journal string and return a Journal object."""
    from ledgerkit.parser import parse_string
    return parse_string(text)


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestJournalToDataFrame(unittest.TestCase):

    def setUp(self):
        self.journal = _make_journal(_SAMPLE_JOURNAL)

    def test_returns_dataframe(self):
        df = self.journal.to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_correct_columns(self):
        df = self.journal.to_dataframe()
        expected = {"date", "description", "cleared", "pending", "account",
                    "amount", "commodity", "amount_formatted"}
        self.assertEqual(set(df.columns), expected)

    def test_row_count_equals_total_postings(self):
        # 3 transactions × 2 postings each = 6 rows.
        df = self.journal.to_dataframe()
        total_postings = sum(len(t.postings) for t in self.journal.transactions)
        self.assertEqual(len(df), total_postings)

    def test_amount_column_contains_decimal(self):
        from ledgerkit.parser import resolve_elision
        df = self.journal.to_dataframe()
        # Drop None rows (elided postings resolved to None).
        non_null = df[df["amount"].notna()]
        for val in non_null["amount"]:
            self.assertIsInstance(val, Decimal)

    def test_amount_formatted_uses_inferred_style(self):
        # Journal uses £, inferred as prefix, comma-group, dot-decimal.
        df = self.journal.to_dataframe()
        salary_row = df[(df["description"] == "Salary") &
                        (df["account"] == "assets:bank:checking")]
        self.assertEqual(len(salary_row), 1)
        formatted = salary_row["amount_formatted"].iloc[0]
        # Expect £ prefix style: £3,000.00
        self.assertEqual(formatted, "£3,000.00")

    def test_query_filters_by_account(self):
        from ledgerkit.models import Query
        df = self.journal.to_dataframe(query=Query(account="expenses"))
        self.assertTrue(len(df) > 0)
        for _, row in df.iterrows():
            self.assertIn("expenses", row["account"])

    def test_query_filters_by_date(self):
        import datetime
        from ledgerkit.models import Query
        df = self.journal.to_dataframe(
            query=Query(date_to=datetime.date(2024, 1, 31))
        )
        for _, row in df.iterrows():
            self.assertLessEqual(row["date"], datetime.date(2024, 1, 31))


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestBalanceResultToDataFrame(unittest.TestCase):

    def setUp(self):
        self.journal = _make_journal(_SAMPLE_JOURNAL)

    def test_returns_dataframe(self):
        df = self.journal.balance().to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_correct_columns(self):
        df = self.journal.balance().to_dataframe()
        self.assertIn("account", df.columns)
        self.assertIn("amount", df.columns)
        self.assertIn("commodity", df.columns)
        self.assertIn("amount_formatted", df.columns)

    def test_amount_column_contains_decimal(self):
        df = self.journal.balance().to_dataframe()
        for val in df["amount"]:
            self.assertIsInstance(val, Decimal)

    def test_balance_result_behaves_as_mapping(self):
        from collections.abc import Mapping
        result = self.journal.balance()
        self.assertIsInstance(result, Mapping)
        # Iteration
        accounts = list(result)
        self.assertTrue(len(accounts) > 0)
        # Index access
        first_account = accounts[0]
        val = result[first_account]
        self.assertIsInstance(val, dict)
        # len
        self.assertGreater(len(result), 0)


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestRegisterResultToDataFrame(unittest.TestCase):

    def setUp(self):
        self.journal = _make_journal(_SAMPLE_JOURNAL)

    def test_returns_dataframe(self):
        df = self.journal.register().to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_correct_columns(self):
        df = self.journal.register().to_dataframe()
        for col in ["date", "description", "account", "amount", "commodity",
                    "amount_formatted"]:
            self.assertIn(col, df.columns)

    def test_row_count_matches_register_length(self):
        reg = self.journal.register()
        df = reg.to_dataframe()
        self.assertEqual(len(df), len(reg))

    def test_amount_column_contains_decimal(self):
        df = self.journal.register().to_dataframe()
        for val in df["amount"]:
            self.assertIsInstance(val, Decimal)

    def test_register_result_behaves_as_sequence(self):
        from collections.abc import Sequence
        result = self.journal.register()
        self.assertIsInstance(result, Sequence)
        # Index access
        first = result[0]
        from ledgerkit.models import RegisterRow
        self.assertIsInstance(first, RegisterRow)
        # Iteration
        rows = list(result)
        self.assertEqual(len(rows), len(result))


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestReportSectionResultToDataFrame(unittest.TestCase):

    def setUp(self):
        self.journal = _make_journal(_SAMPLE_JOURNAL)

    def test_returns_dataframe(self):
        from ledgerkit.models import ReportSection, ReportSpec
        from ledgerkit.reports import balance_from_spec
        spec = ReportSpec(
            name="Test",
            sections=(ReportSection("Expenses", accounts=("expenses",)),),
        )
        results = balance_from_spec(self.journal, spec)
        df = results[0].to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_includes_total_row(self):
        from ledgerkit.models import ReportSection, ReportSpec
        from ledgerkit.reports import balance_from_spec
        spec = ReportSpec(
            name="Test",
            sections=(ReportSection("Expenses", accounts=("expenses",)),),
        )
        results = balance_from_spec(self.journal, spec)
        df = results[0].to_dataframe()
        # Last row should be the total
        self.assertIn("Total", df.iloc[-1]["account"])

    def test_total_row_amount_equals_subtotal(self):
        from ledgerkit.models import ReportSection, ReportSpec
        from ledgerkit.reports import balance_from_spec
        spec = ReportSpec(
            name="Test",
            sections=(ReportSection("Expenses", accounts=("expenses",)),),
        )
        results = balance_from_spec(self.journal, spec)
        section_result = results[0]
        df = section_result.to_dataframe()
        total_row = df.iloc[-1]
        self.assertEqual(total_row["amount"], section_result.subtotal)


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestAccountsResultToDataFrame(unittest.TestCase):

    def setUp(self):
        self.journal = _make_journal(_SAMPLE_JOURNAL)

    def test_returns_dataframe(self):
        df = self.journal.accounts().to_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_single_column(self):
        df = self.journal.accounts().to_dataframe()
        self.assertEqual(list(df.columns), ["account"])

    def test_row_count_matches_accounts_length(self):
        accts = self.journal.accounts()
        df = accts.to_dataframe()
        self.assertEqual(len(df), len(accts))

    def test_accounts_result_behaves_as_sequence(self):
        from collections.abc import Sequence
        result = self.journal.accounts()
        self.assertIsInstance(result, Sequence)
        # len
        self.assertGreater(len(result), 0)
        # index access
        first = result[0]
        self.assertIsInstance(first, str)
        # iteration
        accts = list(result)
        self.assertEqual(len(accts), len(result))
        # equality with list
        self.assertEqual(result, sorted(result))


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestPandasImportError(unittest.TestCase):

    def test_require_pandas_returns_module(self):
        from ledgerkit._pandas_compat import require_pandas
        module = require_pandas()
        import pandas
        self.assertIs(module, pandas)


if __name__ == "__main__":
    unittest.main()

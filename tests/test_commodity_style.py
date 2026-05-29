"""Tests for ledgerkit.commodity_style — CommodityStyle inference and formatting."""

import unittest
from decimal import Decimal

from ledgerkit.commodity_style import CommodityStyle


class TestInfer(unittest.TestCase):

    def test_dollar_prefix_comma_group_dot_decimal(self):
        style = CommodityStyle.infer("$", "$1,234.56")
        self.assertTrue(style.prefix)
        self.assertFalse(style.space)
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.group_separator, ",")
        self.assertEqual(style.precision, 2)

    def test_eur_suffix_space_dot_group_comma_decimal(self):
        style = CommodityStyle.infer("EUR", "1.234,56 EUR")
        self.assertFalse(style.prefix)
        self.assertTrue(style.space)
        self.assertEqual(style.decimal_mark, ",")
        self.assertEqual(style.group_separator, ".")
        self.assertEqual(style.precision, 2)

    def test_aapl_suffix_space_no_decimal_no_group(self):
        style = CommodityStyle.infer("AAPL", "100 AAPL")
        self.assertFalse(style.prefix)
        self.assertTrue(style.space)
        self.assertEqual(style.precision, 0)
        self.assertEqual(style.group_separator, "")

    def test_gbp_prefix_no_space_dot_decimal_comma_group(self):
        style = CommodityStyle.infer("£", "£9,999.00")
        self.assertTrue(style.prefix)
        self.assertFalse(style.space)
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.group_separator, ",")
        self.assertEqual(style.precision, 2)

    def test_usd_suffix_simple_two_decimal(self):
        style = CommodityStyle.infer("USD", "42.50 USD")
        self.assertFalse(style.prefix)
        self.assertTrue(style.space)
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.group_separator, "")
        self.assertEqual(style.precision, 2)

    def test_negative_prefix_amount(self):
        # Negative sign should not affect prefix/suffix detection.
        style = CommodityStyle.infer("$", "-$1,234.56")
        self.assertTrue(style.prefix)
        self.assertFalse(style.space)
        self.assertEqual(style.precision, 2)

    def test_integer_only_no_separator(self):
        style = CommodityStyle.infer("BTC", "1 BTC")
        self.assertFalse(style.prefix)
        self.assertTrue(style.space)
        self.assertEqual(style.precision, 0)
        self.assertEqual(style.group_separator, "")

    def test_integer_with_us_group_separator(self):
        # "1,234" → comma is group separator (3 digits after), precision 0
        style = CommodityStyle.infer("$", "$1,234")
        self.assertEqual(style.group_separator, ",")
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.precision, 0)

    def test_integer_with_european_group_separator(self):
        # "1.234" → dot is group separator (3 digits after), precision 0
        style = CommodityStyle.infer("EUR", "1.234 EUR")
        self.assertEqual(style.group_separator, ".")
        self.assertEqual(style.decimal_mark, ",")
        self.assertEqual(style.precision, 0)


class TestFormat(unittest.TestCase):

    def test_dollar_roundtrip(self):
        style = CommodityStyle.infer("$", "$1,234.56")
        self.assertEqual(style.format(Decimal("1234.56")), "$1,234.56")

    def test_eur_roundtrip(self):
        style = CommodityStyle.infer("EUR", "1.234,56 EUR")
        self.assertEqual(style.format(Decimal("1234.56")), "1.234,56 EUR")

    def test_aapl_roundtrip(self):
        style = CommodityStyle.infer("AAPL", "100 AAPL")
        self.assertEqual(style.format(Decimal("100")), "100 AAPL")

    def test_gbp_roundtrip(self):
        style = CommodityStyle.infer("£", "£9,999.00")
        self.assertEqual(style.format(Decimal("9999.00")), "£9,999.00")

    def test_prefix_negative_puts_symbol_before_minus(self):
        # hledger convention: £-5.00 (symbol then minus then number)
        style = CommodityStyle.infer("£", "£5,000.00")
        self.assertEqual(style.format(Decimal("-5000.00")), "£-5,000.00")

    def test_suffix_negative_puts_minus_before_number(self):
        style = CommodityStyle.infer("EUR", "1,234.56 EUR")
        self.assertEqual(style.format(Decimal("-1234.56")), "-1,234.56 EUR")

    def test_no_group_separator(self):
        style = CommodityStyle("USD", prefix=False, space=True,
                               decimal_mark=".", group_separator="", precision=2)
        self.assertEqual(style.format(Decimal("42.50")), "42.50 USD")

    def test_large_number_grouping(self):
        style = CommodityStyle("$", prefix=True, space=False,
                               decimal_mark=".", group_separator=",", precision=2)
        self.assertEqual(style.format(Decimal("1234567.89")), "$1,234,567.89")

    def test_zero(self):
        style = CommodityStyle("$", prefix=True, space=False,
                               decimal_mark=".", group_separator=",", precision=2)
        self.assertEqual(style.format(Decimal("0")), "$0.00")


class TestParseStyleOverride(unittest.TestCase):

    def test_dollar_prefix(self):
        style = CommodityStyle.parse_style_override("$1,000.00")
        self.assertEqual(style.commodity, "$")
        self.assertTrue(style.prefix)
        self.assertFalse(style.space)
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.group_separator, ",")
        self.assertEqual(style.precision, 2)

    def test_usd_suffix(self):
        style = CommodityStyle.parse_style_override("1,000.00 USD")
        self.assertEqual(style.commodity, "USD")
        self.assertFalse(style.prefix)
        self.assertTrue(style.space)
        self.assertEqual(style.decimal_mark, ".")
        self.assertEqual(style.group_separator, ",")
        self.assertEqual(style.precision, 2)

    def test_european_suffix(self):
        style = CommodityStyle.parse_style_override("1.000,00 EUR")
        self.assertEqual(style.commodity, "EUR")
        self.assertFalse(style.prefix)
        self.assertEqual(style.decimal_mark, ",")
        self.assertEqual(style.group_separator, ".")
        self.assertEqual(style.precision, 2)

    def test_gbp_prefix(self):
        style = CommodityStyle.parse_style_override("£1,000.00")
        self.assertEqual(style.commodity, "£")
        self.assertTrue(style.prefix)

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            CommodityStyle.parse_style_override("")

    def test_no_digits_raises(self):
        with self.assertRaises(ValueError):
            CommodityStyle.parse_style_override("bad input !!")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            CommodityStyle.parse_style_override("   ")


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for commodity style via CLI."""

    def _run(self, args: list) -> tuple:
        """Run CLI and return (stdout, returncode)."""
        import io
        import sys
        from ledgerkit.cli import main
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            rc = main(args)
        except SystemExit as exc:
            rc = int(exc.code) if exc.code is not None else 1
        finally:
            sys.stdout = old_stdout
        return captured.getvalue(), rc

    def _journal_with_style(self, amount_str: str) -> str:
        """Write a temp journal file and return its path."""
        import tempfile
        import os
        content = f"2024-01-01 Test\n    expenses:food  {amount_str}\n    assets:bank\n"
        f = tempfile.NamedTemporaryFile(
            suffix=".journal", mode="w", encoding="utf-8", delete=False
        )
        f.write(content)
        f.close()
        return f.name

    def test_default_output_uses_inferred_style(self):
        import os
        path = self._journal_with_style("£50.00")
        try:
            out, rc = self._run(["-f", path, "balance"])
            self.assertEqual(rc, 0)
            self.assertIn("£50.00", out)
        finally:
            os.unlink(path)

    def test_c_flag_overrides_decimal_style(self):
        import os
        # Journal uses £; override to European decimal style
        path = self._journal_with_style("£50.00")
        try:
            out, rc = self._run(["-f", path, "-c", "£1.000,00", "balance"])
            self.assertEqual(rc, 0)
            # European style: comma as decimal mark
            self.assertIn("£50,00", out)
        finally:
            os.unlink(path)

    def test_c_flag_different_commodity_has_no_effect(self):
        import os
        # Journal uses £; -c for GBP should not affect £ amounts
        path = self._journal_with_style("£50.00")
        try:
            out, rc = self._run(["-f", path, "-c", "1,000.00 GBP", "balance"])
            self.assertEqual(rc, 0)
            # £ amounts unaffected; should still use inferred style
            self.assertIn("£50.00", out)
            self.assertNotIn("GBP", out)
        finally:
            os.unlink(path)

    def test_invalid_c_flag_exits_nonzero(self):
        import os, sys, io
        path = self._journal_with_style("£50.00")
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            _, rc = self._run(["-f", path, "-c", "bad input !!", "balance"])
            self.assertNotEqual(rc, 0)
        finally:
            sys.stderr = old_stderr
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

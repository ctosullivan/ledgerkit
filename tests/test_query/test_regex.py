"""Tests for ledgerkit.query.regex — the HledgerRegex compatible subset."""

from __future__ import annotations

import unittest

from ledgerkit.query.regex import (
    UnsupportedRegexConstructError,
    compile_hledger_regex,
    validate_hledger_regex,
)


class TestValidPatterns(unittest.TestCase):
    """Constructs that are within the HledgerRegex subset (17-...md §5)."""

    def test_plain_literal(self):
        validate_hledger_regex("groceries")  # does not raise

    def test_dot_wildcard(self):
        validate_hledger_regex("expenses.food")

    def test_alternation(self):
        validate_hledger_regex("food|rent")

    def test_anchors(self):
        validate_hledger_regex("^expenses")

    def test_bounded_repetition(self):
        validate_hledger_regex("a{1,3}")

    def test_plain_group(self):
        validate_hledger_regex("(food|rent)")

    def test_bracket_expression(self):
        validate_hledger_regex("[abc]")

    def test_negated_bracket_expression(self):
        validate_hledger_regex("[^abc]")

    def test_gnu_word_boundary(self):
        validate_hledger_regex(r"\bfood\b")

    def test_compile_is_case_insensitive_and_searches(self):
        pattern = compile_hledger_regex("food")
        self.assertTrue(pattern.search("Expenses:Food:Groceries"))
        self.assertIsNone(pattern.search("expenses:rent"))


class TestExcludedConstructs(unittest.TestCase):
    """Constructs excluded per 17-...md §5's construct-by-construct table."""

    def test_inline_mode_flag_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("(?i)food")

    def test_named_group_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("(?P<x>food)")

    def test_non_capturing_group_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("(?:food)")

    def test_lookahead_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("food(?=bar)")

    def test_backreference_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex(r"(foo)\1")

    def test_gnu_angle_boundary_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex(r"\<food\>")

    def test_perl_digit_class_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex(r"\d+")

    def test_perl_word_class_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex(r"\w+")

    def test_posix_named_class_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("[[:alpha:]]")

    def test_lazy_star_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("a*?")

    def test_lazy_plus_rejected(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("a+?")

    def test_compile_raises_for_excluded_construct(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            compile_hledger_regex(r"\d+")


if __name__ == "__main__":
    unittest.main()

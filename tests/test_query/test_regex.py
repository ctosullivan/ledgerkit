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


class TestEmptyPattern(unittest.TestCase):
    """Stage C Phase 7: an empty pattern ("") is rejected, matching real
    hledger's own parse-time rejection (26-query-regex-empty-pattern-
    design.md §2/§5) -- a breaking change from Stage C Phase 6, when an
    empty pattern validated and compiled successfully."""

    def test_validate_rejects_empty_string(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            validate_hledger_regex("")

    def test_compile_rejects_empty_string(self):
        with self.assertRaises(UnsupportedRegexConstructError):
            compile_hledger_regex("")

    def test_error_message_is_generic_not_tag_specific(self):
        # The shared validator serves acct:/desc:/depth:/tag: alike and
        # has no way to know which prefix called it -- the message must
        # not bake in tag:-specific advice (design §5, corrected on
        # review). Regression guard for that exact correction.
        with self.assertRaises(UnsupportedRegexConstructError) as ctx:
            validate_hledger_regex("")
        message = str(ctx.exception)
        self.assertNotIn("tag:", message)
        self.assertIn("empty", message)


class TestEmptyMatchingPatternsRemainAccepted(unittest.TestCase):
    """Regression guard for the narrow-vs-broad scoping distinction
    (design §2/§7): hledger rejects only the literal empty pattern
    STRING, not any pattern whose semantics merely admit an empty match.
    A future "simplification" that broadens the empty check to a
    semantic one would break every case here."""

    def test_dot_star_accepted(self):
        validate_hledger_regex(".*")  # does not raise

    def test_a_star_accepted(self):
        validate_hledger_regex("a*")

    def test_anchored_empty_accepted(self):
        validate_hledger_regex("^$")

    def test_empty_group_accepted(self):
        validate_hledger_regex("()")

    def test_compile_dot_star_matches_empty_string(self):
        pattern = compile_hledger_regex(".*")
        self.assertTrue(pattern.search(""))


if __name__ == "__main__":
    unittest.main()

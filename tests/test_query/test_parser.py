"""Tests for ledgerkit.query.parser — query text -> QueryAST."""

from __future__ import annotations

import datetime
import unittest

from ledgerkit.query.ast import Acct, And, DateSpan, Depth, Desc, Not, Or, Status, TxnStatus
from ledgerkit.query.parser import QueryParseError, parse


class TestBarePatternAndPrefixes(unittest.TestCase):
    def test_bare_pattern_defaults_to_acct(self):
        self.assertEqual(parse("groceries"), Acct("groceries"))

    def test_acct_prefix(self):
        self.assertEqual(parse("acct:groceries"), Acct("groceries"))

    def test_desc_prefix(self):
        self.assertEqual(parse("desc:amazon"), Desc("amazon"))

    def test_depth_prefix(self):
        self.assertEqual(parse("depth:2"), Depth(2))

    def test_depth_zero_is_valid(self):
        self.assertEqual(parse("depth:0"), Depth(0))

    def test_depth_negative_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:-1")

    def test_depth_non_integer_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:abc")

    def test_status_cleared(self):
        self.assertEqual(parse("status:*"), Status(TxnStatus.CLEARED))

    def test_status_pending(self):
        self.assertEqual(parse("status:!"), Status(TxnStatus.PENDING))

    def test_status_unmarked_bare(self):
        self.assertEqual(parse("status:"), Status(TxnStatus.UNMARKED))

    def test_status_cleared_synonym_1(self):
        self.assertEqual(parse("status:1"), Status(TxnStatus.CLEARED))

    def test_status_unmarked_synonym_0(self):
        self.assertEqual(parse("status:0"), Status(TxnStatus.UNMARKED))

    def test_status_invalid_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("status:x")


class TestQuoting(unittest.TestCase):
    def test_quoted_bare_pattern_with_space(self):
        self.assertEqual(parse('"expenses dining"'), Acct("expenses dining"))

    def test_quoted_desc_with_space(self):
        self.assertEqual(parse('desc:"whole foods"'), Desc("whole foods"))

    def test_unquoted_two_words_are_two_terms(self):
        self.assertEqual(parse("expenses:dining out"), Or((Acct("expenses:dining"), Acct("out"))))


class TestDateSpans(unittest.TestCase):
    def test_single_date(self):
        self.assertEqual(
            parse("date:2024-01-15"),
            DateSpan(datetime.date(2024, 1, 15), datetime.date(2024, 1, 16)),
        )

    def test_closed_range_dash_separator(self):
        self.assertEqual(
            parse("date:2024-01-01-2024-02-01"),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_closed_range_dotdot_separator(self):
        self.assertEqual(
            parse("date:2024-01-01..2024-02-01"),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_closed_range_to_separator(self):
        self.assertEqual(
            parse('date:"2024-01-01 to 2024-02-01"'),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_range_end_is_written_bound_not_auto_incremented(self):
        # Unlike the single-date case (which gets +1 day to form a
        # one-day span), a written range's second date becomes the
        # exclusive end exactly as given — so date:D1-2024-01-31 does
        # NOT include Jan 31 itself (17-query-semantics-brief.md §3).
        span = parse("date:2024-01-01-2024-01-31")
        self.assertEqual(span.end, datetime.date(2024, 1, 31))
        self.assertNotEqual(span.end, datetime.date(2024, 2, 1))

    def test_open_ended_from(self):
        self.assertEqual(parse("date:2024-01-01.."), DateSpan(datetime.date(2024, 1, 1), None))

    def test_open_ended_to(self):
        self.assertEqual(parse("date:..2024-01-01"), DateSpan(None, datetime.date(2024, 1, 1)))

    def test_two_digit_year_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("date:24-01-15")

    def test_invalid_calendar_date_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("date:2024-13-01")

    def test_malformed_date_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("date:not-a-date")


class TestNotAndCombination(unittest.TestCase):
    def test_not_wraps_bare_pattern(self):
        self.assertEqual(parse("not:groceries"), Not(Acct("groceries")))

    def test_not_wraps_prefixed_term(self):
        self.assertEqual(parse("not:desc:amazon"), Not(Desc("amazon")))

    def test_double_negation(self):
        self.assertEqual(parse("not:not:groceries"), Not(Not(Acct("groceries"))))

    def test_same_prefix_acct_terms_are_ored(self):
        self.assertEqual(parse("acct:a acct:b"), Or((Acct("a"), Acct("b"))))

    def test_same_prefix_desc_terms_are_ored(self):
        self.assertEqual(parse("desc:a desc:b"), Or((Desc("a"), Desc("b"))))

    def test_same_prefix_status_terms_are_ored(self):
        self.assertEqual(
            parse("status: status:!"),
            Or((Status(TxnStatus.UNMARKED), Status(TxnStatus.PENDING))),
        )

    def test_different_prefixes_are_anded(self):
        self.assertEqual(
            parse("date:2022-01-01.. desc:amazon depth:2"),
            And(
                (
                    Desc("amazon"),
                    DateSpan(datetime.date(2022, 1, 1), None),
                    Depth(2),
                )
            ),
        )

    def test_negated_same_prefix_terms_are_anded_not_ored(self):
        # The central footgun from 17-query-semantics-brief.md §6: two
        # negated acct: terms must both be individually AND'd (must match
        # neither), not OR'd (which would mean "match not-a or not-b" — a
        # much weaker, almost-always-true exclusion).
        self.assertEqual(
            parse("not:acct:a not:acct:b"),
            And((Not(Acct("a")), Not(Acct("b")))),
        )

    def test_mixed_negated_and_unnegated_same_prefix(self):
        self.assertEqual(
            parse("acct:a acct:b not:acct:c"),
            And((Or((Acct("a"), Acct("b"))), Not(Acct("c")))),
        )


class TestEmptyQuery(unittest.TestCase):
    def test_empty_string_matches_everything(self):
        self.assertEqual(parse(""), And(()))

    def test_whitespace_only_matches_everything(self):
        self.assertEqual(parse("   "), And(()))


if __name__ == "__main__":
    unittest.main()

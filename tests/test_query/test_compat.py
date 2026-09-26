"""Unit tests for ledgerkit.query.compat -- the Query -> QueryNode translator.

Stage C Phase 8 (dev-docs/planning/core-redefinition/
27-query-shim-convergence-design.md). See tests/test_reports.py for
integration-level coverage of the converged report functions themselves
(balance/register/accounts/stats/balance_from_spec/to_dataframe).
"""

from __future__ import annotations

import datetime
import unittest

from ledgerkit.models import Query
from ledgerkit.query.ast import Acct, And, DateSpan, Desc, Not
from ledgerkit.query.compat import _exclusive_end, _query_to_ast, _validated
from ledgerkit.query.parser import QueryParseError


class TestQueryToAstEmptyCases(unittest.TestCase):
    """query=None and Query() (all fields None) both translate to None --
    "no filter", consistent with every other Query-accepting function."""

    def test_none_query_returns_none(self):
        self.assertIsNone(_query_to_ast(None))

    def test_empty_query_returns_none(self):
        self.assertIsNone(_query_to_ast(Query()))

    def test_depth_only_query_returns_none(self):
        # query.depth is NEVER a predicate -- see knowledge/DOMAIN_RULES.md.
        # A Query with only depth set must translate to None (no predicate
        # node at all), not some depth-derived AST term.
        self.assertIsNone(_query_to_ast(Query(depth=2)))


class TestQueryToAstSingleFields(unittest.TestCase):

    def test_account_only(self):
        node = _query_to_ast(Query(account="food"))
        self.assertEqual(node, Acct("food"))

    def test_not_account_only(self):
        node = _query_to_ast(Query(not_account="rent"))
        self.assertEqual(node, Not(Acct("rent")))

    def test_payee_only(self):
        node = _query_to_ast(Query(payee="Coffee"))
        self.assertEqual(node, Desc("Coffee"))

    def test_date_from_only(self):
        node = _query_to_ast(Query(date_from=datetime.date(2024, 1, 1)))
        self.assertEqual(node, DateSpan(start=datetime.date(2024, 1, 1), end=None))

    def test_date_to_only(self):
        node = _query_to_ast(Query(date_to=datetime.date(2024, 1, 31)))
        self.assertEqual(node, DateSpan(start=None, end=datetime.date(2024, 2, 1)))

    def test_depth_never_appears_alongside_other_fields(self):
        # depth is dropped from the tree even when other fields are set.
        node = _query_to_ast(Query(account="food", depth=2))
        self.assertEqual(node, Acct("food"))


class TestQueryToAstCombinations(unittest.TestCase):

    def test_account_and_not_account_and_combine(self):
        node = _query_to_ast(Query(account="food", not_account="restaurant"))
        self.assertEqual(node, And((Acct("food"), Not(Acct("restaurant")))))

    def test_account_and_payee_and_dates(self):
        node = _query_to_ast(Query(
            account="food",
            payee="Coffee",
            date_from=datetime.date(2024, 1, 1),
            date_to=datetime.date(2024, 1, 31),
        ))
        self.assertEqual(node, And((
            Acct("food"),
            Desc("Coffee"),
            DateSpan(start=datetime.date(2024, 1, 1), end=datetime.date(2024, 2, 1)),
        )))

    def test_all_five_fields(self):
        node = _query_to_ast(Query(
            account="food",
            not_account="restaurant",
            payee="Coffee",
            date_from=datetime.date(2024, 1, 1),
            date_to=datetime.date(2024, 1, 31),
            depth=3,
        ))
        self.assertEqual(node, And((
            Acct("food"),
            Not(Acct("restaurant")),
            Desc("Coffee"),
            DateSpan(start=datetime.date(2024, 1, 1), end=datetime.date(2024, 2, 1)),
        )))


class TestDateInclusivityTranslation(unittest.TestCase):
    """Query.date_to is inclusive; DateSpan.end is exclusive. A dedicated,
    explicitly-named regression test per the design's own §11 requirement."""

    def test_date_to_still_matches_transaction_dated_exactly_date_to(self):
        from ledgerkit.models import Journal, Posting, Transaction, Amount
        from decimal import Decimal
        from ledgerkit.query.eval import matches_transaction

        d = datetime.date(2024, 6, 15)
        txn = Transaction(date=d, description="x", postings=[
            Posting(account="a", amount=Amount(Decimal("1"), "£")),
        ])
        node = _query_to_ast(Query(date_to=d))
        self.assertIsNotNone(node)
        self.assertTrue(matches_transaction(node, txn))

    def test_date_max_does_not_overflow_and_still_matches(self):
        from ledgerkit.models import Journal, Posting, Transaction, Amount
        from decimal import Decimal
        from ledgerkit.query.eval import matches_transaction

        d = datetime.date.max
        txn = Transaction(date=d, description="x", postings=[
            Posting(account="a", amount=Amount(Decimal("1"), "£")),
        ])
        # Must not raise OverflowError.
        node = _query_to_ast(Query(date_to=d))
        self.assertIsNotNone(node)
        self.assertTrue(matches_transaction(node, txn))


class TestExclusiveEnd(unittest.TestCase):

    def test_none_stays_none(self):
        self.assertIsNone(_exclusive_end(None))

    def test_ordinary_date_adds_one_day(self):
        self.assertEqual(
            _exclusive_end(datetime.date(2024, 1, 31)),
            datetime.date(2024, 2, 1),
        )

    def test_date_max_maps_to_none_not_overflow(self):
        self.assertIsNone(_exclusive_end(datetime.date.max))


class TestValidated(unittest.TestCase):

    def test_valid_pattern_returned_unchanged(self):
        self.assertEqual(_validated("account", "food"), "food")

    def test_excluded_construct_raises_query_parse_error(self):
        with self.assertRaises(QueryParseError):
            _validated("account", r"\d+")

    def test_empty_pattern_raises_query_parse_error(self):
        with self.assertRaises(QueryParseError):
            _validated("account", "")


class TestQueryToAstEagerValidation(unittest.TestCase):
    """An invalid Query field must fail at translation time, deterministically
    -- not lazily, only if and when evaluation happens to reach it."""

    def test_excluded_construct_in_account_raises_at_translation_time(self):
        with self.assertRaises(QueryParseError):
            _query_to_ast(Query(account=r"\d+"))

    def test_excluded_construct_in_not_account_raises(self):
        with self.assertRaises(QueryParseError):
            _query_to_ast(Query(not_account=r"\d+"))

    def test_excluded_construct_in_payee_raises(self):
        with self.assertRaises(QueryParseError):
            _query_to_ast(Query(payee=r"(?:food)"))

    def test_empty_account_pattern_raises(self):
        # Matches -q "acct:" Stage C Phase 7 behaviour, not "matches everything".
        with self.assertRaises(QueryParseError):
            _query_to_ast(Query(account=""))

    def test_empty_payee_pattern_raises(self):
        with self.assertRaises(QueryParseError):
            _query_to_ast(Query(payee=""))


if __name__ == "__main__":
    unittest.main()

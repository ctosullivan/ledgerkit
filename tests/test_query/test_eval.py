"""Tests for ledgerkit.query.eval — QueryAST -> predicate evaluation."""

from __future__ import annotations

import datetime
import unittest

from ledgerkit.models import Amount, Posting, Transaction
from ledgerkit.query.ast import Acct, And, DateSpan, Depth, Desc, Not, Or, Status, TxnStatus
from ledgerkit.query.eval import matches_posting, matches_transaction
from decimal import Decimal


def _txn(
    date: str,
    description: str,
    *accounts: str,
    cleared: bool = False,
    pending: bool = False,
) -> Transaction:
    return Transaction(
        date=datetime.date.fromisoformat(date),
        description=description,
        postings=[Posting(account=a, amount=Amount(Decimal("1"), "USD")) for a in accounts],
        cleared=cleared,
        pending=pending,
    )


class TestAcct(unittest.TestCase):
    def setUp(self):
        self.txn = _txn("2024-01-15", "Groceries", "expenses:food:groceries", "assets:checking")

    def test_transaction_matches_if_any_posting_matches(self):
        self.assertTrue(matches_transaction(Acct("food"), self.txn))

    def test_transaction_does_not_match_if_no_posting_matches(self):
        self.assertFalse(matches_transaction(Acct("rent"), self.txn))

    def test_case_insensitive(self):
        self.assertTrue(matches_transaction(Acct("FOOD"), self.txn))

    def test_posting_level_checks_only_that_posting(self):
        food_posting, checking_posting = self.txn.postings
        self.assertTrue(matches_posting(Acct("food"), self.txn, food_posting))
        self.assertFalse(matches_posting(Acct("food"), self.txn, checking_posting))

    def test_regex_pattern(self):
        self.assertTrue(matches_transaction(Acct("^expenses"), self.txn))
        self.assertFalse(matches_transaction(Acct("^assets:food"), self.txn))


class TestDesc(unittest.TestCase):
    def setUp(self):
        self.txn = _txn("2024-01-15", "Whole Foods", "expenses:food")

    def test_transaction_match(self):
        self.assertTrue(matches_transaction(Desc("whole"), self.txn))
        self.assertFalse(matches_transaction(Desc("amazon"), self.txn))

    def test_posting_inherits_transaction_description(self):
        self.assertTrue(matches_posting(Desc("whole"), self.txn, self.txn.postings[0]))


class TestDateSpan(unittest.TestCase):
    def test_single_day_span(self):
        span = DateSpan(datetime.date(2024, 1, 15), datetime.date(2024, 1, 16))
        self.assertTrue(matches_transaction(span, _txn("2024-01-15", "x", "a")))
        self.assertFalse(matches_transaction(span, _txn("2024-01-16", "x", "a")))
        self.assertFalse(matches_transaction(span, _txn("2024-01-14", "x", "a")))

    def test_range_end_exclusive(self):
        span = DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 1, 31))
        self.assertTrue(matches_transaction(span, _txn("2024-01-30", "x", "a")))
        self.assertFalse(matches_transaction(span, _txn("2024-01-31", "x", "a")))

    def test_open_ended_from(self):
        span = DateSpan(datetime.date(2024, 1, 1), None)
        self.assertTrue(matches_transaction(span, _txn("2030-01-01", "x", "a")))
        self.assertFalse(matches_transaction(span, _txn("2023-12-31", "x", "a")))

    def test_open_ended_to(self):
        span = DateSpan(None, datetime.date(2024, 1, 1))
        self.assertTrue(matches_transaction(span, _txn("2020-01-01", "x", "a")))
        self.assertFalse(matches_transaction(span, _txn("2024-01-01", "x", "a")))


class TestDepth(unittest.TestCase):
    def setUp(self):
        self.txn = _txn("2024-01-15", "x", "expenses:food:groceries")

    def test_matches_at_or_above_depth(self):
        self.assertTrue(matches_transaction(Depth(3), self.txn))
        self.assertTrue(matches_transaction(Depth(5), self.txn))

    def test_does_not_match_below_depth(self):
        self.assertFalse(matches_transaction(Depth(2), self.txn))

    def test_any_posting_rule_at_transaction_level(self):
        txn = _txn("2024-01-15", "x", "expenses:food:groceries:organic", "a")
        # "a" (depth 1) satisfies depth:1 even though the other posting is deeper.
        self.assertTrue(matches_transaction(Depth(1), txn))


class TestStatus(unittest.TestCase):
    def test_cleared(self):
        txn = _txn("2024-01-15", "x", "a", cleared=True)
        self.assertTrue(matches_transaction(Status(TxnStatus.CLEARED), txn))
        self.assertFalse(matches_transaction(Status(TxnStatus.PENDING), txn))

    def test_pending(self):
        txn = _txn("2024-01-15", "x", "a", pending=True)
        self.assertTrue(matches_transaction(Status(TxnStatus.PENDING), txn))

    def test_unmarked(self):
        txn = _txn("2024-01-15", "x", "a")
        self.assertTrue(matches_transaction(Status(TxnStatus.UNMARKED), txn))

    def test_posting_inherits_transaction_status(self):
        txn = _txn("2024-01-15", "x", "a", cleared=True)
        self.assertTrue(matches_posting(Status(TxnStatus.CLEARED), txn, txn.postings[0]))


class TestCombinators(unittest.TestCase):
    def setUp(self):
        self.txn = _txn("2024-01-15", "Whole Foods", "expenses:food", cleared=True)

    def test_and_requires_all(self):
        node = And((Acct("food"), Desc("whole")))
        self.assertTrue(matches_transaction(node, self.txn))
        node2 = And((Acct("food"), Desc("amazon")))
        self.assertFalse(matches_transaction(node2, self.txn))

    def test_or_requires_any(self):
        node = Or((Acct("rent"), Desc("whole")))
        self.assertTrue(matches_transaction(node, self.txn))

    def test_not_negates(self):
        self.assertFalse(matches_transaction(Not(Acct("food")), self.txn))
        self.assertTrue(matches_transaction(Not(Acct("rent")), self.txn))

    def test_negated_pair_excludes_both(self):
        # not:acct:a not:acct:b shape: must match neither.
        txn_a = _txn("2024-01-15", "x", "a")
        txn_b = _txn("2024-01-15", "x", "b")
        txn_c = _txn("2024-01-15", "x", "c")
        node = And((Not(Acct("a")), Not(Acct("b"))))
        self.assertFalse(matches_transaction(node, txn_a))
        self.assertFalse(matches_transaction(node, txn_b))
        self.assertTrue(matches_transaction(node, txn_c))


if __name__ == "__main__":
    unittest.main()

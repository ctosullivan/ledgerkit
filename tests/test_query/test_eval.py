"""Tests for ledgerkit.query.eval — QueryAST -> predicate evaluation."""

from __future__ import annotations

import datetime
import unittest

from ledgerkit.models import Amount, Journal, Posting, Transaction
from ledgerkit.query.ast import Acct, And, DateSpan, Desc, MaxAccountLevel, Not, Or, Status, Tag, TxnStatus
from ledgerkit.query.eval import _matches_posting_for_accounts, matches_posting, matches_transaction
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


class TestMaxAccountLevel(unittest.TestCase):
    """MaxAccountLevel is a Ledgerkit-native, Python-API-only boolean
    predicate — deliberately NOT hledger's depth: (see ledgerkit.query.depth
    for that, and MaxAccountLevel's own docstring for why). No `-q` string
    form exists for it; these tests construct the node directly."""

    def setUp(self):
        self.txn = _txn("2024-01-15", "x", "expenses:food:groceries")

    def test_matches_at_or_above_depth(self):
        self.assertTrue(matches_transaction(MaxAccountLevel(3), self.txn))
        self.assertTrue(matches_transaction(MaxAccountLevel(5), self.txn))

    def test_does_not_match_below_depth(self):
        self.assertFalse(matches_transaction(MaxAccountLevel(2), self.txn))

    def test_any_posting_rule_at_transaction_level(self):
        txn = _txn("2024-01-15", "x", "expenses:food:groceries:organic", "a")
        # "a" (depth 1) satisfies MaxAccountLevel(1) even though the other
        # posting is deeper.
        self.assertTrue(matches_transaction(MaxAccountLevel(1), txn))


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


class TestTag(unittest.TestCase):
    """tag:NAME[=REGEX] matching — Stage C Phase 6
    (23-tag-query-matching-design.md, 24-tag-query-matching-implementation-
    plan.md). Mirrors the design's own §2.7 precedence fixture: a "rate"
    tag with a DIFFERENT value at each of the four effective-tag sources,
    so a naive "highest-priority wins" implementation would fail here."""

    def setUp(self):
        self.journal = Journal(
            transactions=[],
            declared_account_tags={"assets:bank": [("rate", "3"), ("asrc", "1")]},
            declared_commodity_tags={"$": [("rate", "2"), ("csrc", "1")]},
        )
        self.txn = Transaction(
            date=datetime.date(2024, 1, 1),
            description="Opening balance",
            tags=[("rate", "4"), ("hsrc", "1")],
        )
        self.posting = Posting(
            account="assets:bank",
            amount=Amount(Decimal("1000"), "$"),
            tags=[("rate", "1"), ("psrc", "1")],
        )
        self.other_posting = Posting(
            account="equity:opening-balances",
            amount=Amount(Decimal("-1000"), "$"),
        )
        self.txn.postings = [self.posting, self.other_posting]
        self.journal.transactions = [self.txn]

    def test_journal_none_raises_on_matches_posting(self):
        with self.assertRaises(ValueError):
            matches_posting(Tag("rate", "1"), self.txn, self.posting)

    def test_journal_none_raises_on_matches_transaction(self):
        with self.assertRaises(ValueError):
            matches_transaction(Tag("rate", "1"), self.txn)

    def test_posting_own_tag_matches(self):
        self.assertTrue(matches_posting(Tag("rate", "1"), self.txn, self.posting, journal=self.journal))

    def test_transaction_own_tag_matches_via_posting(self):
        # Rule C: a transaction-header tag propagates onto every posting.
        self.assertTrue(matches_posting(Tag("rate", "4"), self.txn, self.posting, journal=self.journal))

    def test_account_inherited_tag_matches_via_posting(self):
        # Rule B: the posting's own account's declared tag propagates.
        self.assertTrue(matches_posting(Tag("rate", "3"), self.txn, self.posting, journal=self.journal))

    def test_commodity_propagated_tag_matches_via_posting(self):
        self.assertTrue(matches_posting(Tag("rate", "2"), self.txn, self.posting, journal=self.journal))

    def test_no_shadowing_all_four_values_independently_matchable(self):
        # Design §2.7's central, counter-intuitive finding: same-named,
        # differently-valued tags from every source remain simultaneously
        # matchable — not "highest priority wins." A naive dedup-by-name
        # implementation would make only one of these four True.
        for value in ("1", "2", "3", "4"):
            with self.subTest(value=value):
                self.assertTrue(
                    matches_posting(Tag("rate", value), self.txn, self.posting, journal=self.journal)
                )

    def test_unrelated_account_does_not_inherit(self):
        self.assertFalse(
            matches_posting(Tag("rate", "3"), self.txn, self.other_posting, journal=self.journal)
        )

    def test_unrelated_account_still_sees_commodity_tag(self):
        # Commodity propagation is keyed by commodity, not account — the
        # "equity:opening-balances" posting has no account-level rate:3,
        # but it DOES use commodity "$" so rate:2 still matches it.
        self.assertTrue(
            matches_posting(Tag("rate", "2"), self.txn, self.other_posting, journal=self.journal)
        )

    def test_child_account_inherits_parent_declared_tag(self):
        child_posting = Posting(account="assets:bank:savings", amount=Amount(Decimal("20"), "$"))
        self.assertTrue(matches_posting(Tag("rate", "3"), self.txn, child_posting, journal=self.journal))

    def test_bare_tag_matches_any_value(self):
        self.assertTrue(matches_posting(Tag("rate", None), self.txn, self.posting, journal=self.journal))
        self.assertTrue(matches_posting(Tag("psrc", None), self.txn, self.posting, journal=self.journal))

    def test_unmatched_name_does_not_match(self):
        self.assertFalse(matches_posting(Tag("nope", None), self.txn, self.posting, journal=self.journal))

    def test_transaction_level_matches_directly_even_without_a_matching_posting(self):
        # Design §6: a transaction matches if ITS OWN tags directly match
        # -- independent of whether any posting's effective tags also
        # happen to match (they do here too, via rule C, but this asserts
        # the direct half is real on its own, not merely implied by it).
        self.assertTrue(matches_transaction(Tag("rate", "4"), self.txn, journal=self.journal))

    def test_transaction_level_matches_via_any_posting_effective_tags(self):
        # rate:2 (commodity-propagated) never appears in txn.tags directly
        # -- only reachable via a posting's effective tags.
        self.assertTrue(matches_transaction(Tag("rate", "2"), self.txn, journal=self.journal))

    def test_transaction_level_no_match(self):
        self.assertFalse(matches_transaction(Tag("rate", "9"), self.txn, journal=self.journal))

    def test_not_tag_negates(self):
        self.assertFalse(
            matches_posting(Not(Tag("rate", "1")), self.txn, self.posting, journal=self.journal)
        )
        self.assertTrue(
            matches_posting(Not(Tag("rate", "9")), self.txn, self.posting, journal=self.journal)
        )

    def test_tag_inside_and_or_combinators(self):
        node = And((Tag("rate", "1"), Tag("rate", "3")))
        self.assertTrue(matches_posting(node, self.txn, self.posting, journal=self.journal))
        node2 = Or((Tag("rate", "9"), Tag("rate", "3")))
        self.assertTrue(matches_posting(node2, self.txn, self.posting, journal=self.journal))


class TestTagAccountsMode(unittest.TestCase):
    """The `accounts` command's narrower tag-visibility mode (design
    §2.5/§9.2) — transaction-own + account-inherited only, excluding
    posting-own and commodity-propagated tags. Same fixture as TestTag."""

    def setUp(self):
        self.journal = Journal(
            transactions=[],
            declared_account_tags={"assets:bank": [("rate", "3")]},
            declared_commodity_tags={"$": [("rate", "2")]},
        )
        self.txn = Transaction(
            date=datetime.date(2024, 1, 1), description="x", tags=[("rate", "4")]
        )
        self.posting = Posting(account="assets:bank", amount=Amount(Decimal("1000"), "$"), tags=[("rate", "1")])
        self.txn.postings = [self.posting]
        self.journal.transactions = [self.txn]

    def test_transaction_level_visible(self):
        self.assertTrue(
            _matches_posting_for_accounts(Tag("rate", "4"), self.txn, self.posting, journal=self.journal)
        )

    def test_account_inherited_visible(self):
        self.assertTrue(
            _matches_posting_for_accounts(Tag("rate", "3"), self.txn, self.posting, journal=self.journal)
        )

    def test_posting_own_not_visible(self):
        self.assertFalse(
            _matches_posting_for_accounts(Tag("rate", "1"), self.txn, self.posting, journal=self.journal)
        )

    def test_commodity_propagated_not_visible(self):
        self.assertFalse(
            _matches_posting_for_accounts(Tag("rate", "2"), self.txn, self.posting, journal=self.journal)
        )

    def test_ordinary_matches_posting_still_sees_all_four(self):
        # Confirms the accounts-mode exception is genuinely opt-in — the
        # regular matches_posting on the exact same fixture sees every
        # source, unaffected by _matches_posting_for_accounts existing.
        for value in ("1", "2", "3", "4"):
            with self.subTest(value=value):
                self.assertTrue(
                    matches_posting(Tag("rate", value), self.txn, self.posting, journal=self.journal)
                )


if __name__ == "__main__":
    unittest.main()

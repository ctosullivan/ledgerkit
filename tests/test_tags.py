"""Tests for ledgerkit.tags — inline comment-tag parsing.

Every case here is grounded in `dev-docs/planning/core-redefinition/
20-tag-parsing-syntax-brief.md`'s direct reading of hledger 1.52.4's real
extraction grammar — including the hledger source's own doctest.
"""

from __future__ import annotations

import datetime
import unittest
from decimal import Decimal

from ledgerkit.models import Amount, Journal, Posting, Transaction
from ledgerkit.tags import (
    _accounts_effective_tags,
    _commodity_tags,
    _effective_tags,
    _inherited_account_tags,
    _posting_commodities,
    effective_date,
    effective_date2,
    parse_tags,
)


class TestBasicTags(unittest.TestCase):
    def test_none_comment_returns_empty(self):
        self.assertEqual(parse_tags(None), [])

    def test_empty_comment_returns_empty(self):
        self.assertEqual(parse_tags(""), [])

    def test_no_colon_no_tags(self):
        self.assertEqual(parse_tags("just a comment"), [])

    def test_single_tag(self):
        self.assertEqual(parse_tags("category:food"), [("category", "food")])

    def test_bare_tag_empty_value(self):
        # hledger.1:2504-2509's own first example: "; some-tag:" with
        # nothing after the colon is a legal tag with an empty value.
        self.assertEqual(parse_tags("some-tag:"), [("some-tag", "")])

    def test_hledger_own_doctest(self):
        # Common.hs:1474-1478's own doctest:
        # parseTags "; name1: val1, name2:all this is value2"
        #   -> Right [("name1","val1"),("name2","all this is value2")]
        # (the leading "; " is already stripped by the time inline_comment
        # is assembled, so it's omitted here.)
        self.assertEqual(
            parse_tags("name1: val1, name2:all this is value2"),
            [("name1", "val1"), ("name2", "all this is value2")],
        )


class TestNameDelimiting(unittest.TestCase):
    def test_leading_prose_discarded_last_word_is_name(self):
        self.assertEqual(
            parse_tags("some comment text, tag1:value"),
            [("tag1", "value")],
        )

    def test_space_before_colon_voids_the_tag(self):
        # "foo : bar" produces ZERO tags -- the space before the colon
        # voids the candidate name entirely; it does not become a tag
        # named "foo", and parsing does not find a second tag in " bar"
        # either (no further colon exists).
        self.assertEqual(parse_tags("foo : bar"), [])

    def test_space_before_colon_then_a_real_tag_later(self):
        # After voiding "foo :", scanning resumes right after that colon
        # looking for a further colon -- a genuine tag later on the same
        # line is still found.
        self.assertEqual(parse_tags("foo : bar, real:tag"), [("real", "tag")])

    def test_no_character_class_restriction_on_name(self):
        # The manual's "single word or hyphenated word" prose is not
        # enforced -- digits/punctuation/other symbols are all accepted.
        self.assertEqual(parse_tags("tag_with.punct123:x"), [("tag_with.punct123", "x")])


class TestValueHandling(unittest.TestCase):
    def test_colon_inside_value_is_fine(self):
        # Only ',' and end-of-line terminate a value -- a colon does not.
        self.assertEqual(
            parse_tags("url: http://example.com, other: x"),
            [("url", "http://example.com"), ("other", "x")],
        )

    def test_value_whitespace_trimmed_both_sides(self):
        self.assertEqual(
            parse_tags("tag1:   value1  , tag2:value2"),
            [("tag1", "value1"), ("tag2", "value2")],
        )

    def test_internal_whitespace_in_value_preserved(self):
        self.assertEqual(
            parse_tags("name2:all this is value2"),
            [("name2", "all this is value2")],
        )

    def test_comma_is_a_hard_separator_no_escaping(self):
        # A comma always ends a value -- there is no way to include one.
        self.assertEqual(
            parse_tags("tag:before,after:stuff"),
            [("tag", "before"), ("after", "stuff")],
        )


class TestMultipleValuesPerName(unittest.TestCase):
    def test_repeated_tag_name_kept_as_list_not_collapsed(self):
        # hledger.1:2525-2529: "A tag can have multiple values."
        self.assertEqual(
            parse_tags("tag1:value 1, tag1:value 2"),
            [("tag1", "value 1"), ("tag1", "value 2")],
        )


class TestMultiLineComments(unittest.TestCase):
    def test_tags_collected_across_joined_lines(self):
        # Transaction.inline_comment/Posting.inline_comment join same-line
        # + follow-on lines with "\n" -- confirm each line's tags are
        # still found (20-tag-parsing-syntax-brief.md §6's equivalence).
        comment = "first line, a:1\nsecond line, b:2"
        self.assertEqual(parse_tags(comment), [("a", "1"), ("b", "2")])

    def test_trailing_comma_does_not_continue_onto_next_line(self):
        comment = "a:1,\nb:2"
        self.assertEqual(parse_tags(comment), [("a", "1"), ("b", "2")])


def _txn(date, date2=None):
    return Transaction(date=date, description="x", date2=date2)


def _posting(date_override=None, date2_override=None):
    return Posting(
        account="a",
        amount=Amount(Decimal("1"), "USD"),
        date_override=date_override,
        date2_override=date2_override,
    )


class TestEffectiveDate(unittest.TestCase):
    def test_no_override_uses_transaction_date(self):
        txn = _txn(datetime.date(2024, 1, 1))
        p = _posting()
        self.assertEqual(effective_date(txn, p), datetime.date(2024, 1, 1))

    def test_override_takes_precedence(self):
        txn = _txn(datetime.date(2024, 1, 1))
        p = _posting(date_override=datetime.date(2024, 6, 1))
        self.assertEqual(effective_date(txn, p), datetime.date(2024, 6, 1))


class TestEffectiveDate2(unittest.TestCase):
    def test_no_override_no_txn_date2_falls_back_to_txn_date(self):
        txn = _txn(datetime.date(2024, 1, 1))
        p = _posting()
        self.assertEqual(effective_date2(txn, p), datetime.date(2024, 1, 1))

    def test_own_date2_override_wins(self):
        txn = _txn(datetime.date(2024, 1, 1), date2=datetime.date(2024, 2, 1))
        p = _posting(date2_override=datetime.date(2024, 3, 1))
        self.assertEqual(effective_date2(txn, p), datetime.date(2024, 3, 1))

    def test_txn_date2_used_when_no_posting_date2_override(self):
        txn = _txn(datetime.date(2024, 1, 1), date2=datetime.date(2024, 2, 1))
        p = _posting()
        self.assertEqual(effective_date2(txn, p), datetime.date(2024, 2, 1))

    def test_own_date_override_reused_as_date2_fallback(self):
        # No txn date2, no posting date2_override, but a posting date_override
        # exists -- it's reused as the effective date2 too (hledger's own
        # four-level asum chain, per 20-tag-parsing-syntax-brief.md §3.2).
        txn = _txn(datetime.date(2024, 1, 1))
        p = _posting(date_override=datetime.date(2024, 6, 1))
        self.assertEqual(effective_date2(txn, p), datetime.date(2024, 6, 1))


class TestInheritedAccountTags(unittest.TestCase):
    """_inherited_account_tags — Stage C Phase 6 (design §2.2 rule A,
    §5's implementation-plan resolution)."""

    def setUp(self):
        self.journal = Journal(
            declared_account_tags={
                "assets": [("type", "A")],
                "assets:bank": [("rate", "3")],
            }
        )

    def test_own_account_tags_included(self):
        self.assertEqual(
            _inherited_account_tags(self.journal, "assets:bank"),
            [("type", "A"), ("rate", "3")],
        )

    def test_deep_descendant_inherits_from_every_ancestor(self):
        self.assertEqual(
            _inherited_account_tags(self.journal, "assets:bank:savings"),
            [("type", "A"), ("rate", "3")],
        )

    def test_unrelated_account_gets_nothing(self):
        self.assertEqual(_inherited_account_tags(self.journal, "expenses:food"), [])

    def test_root_level_declared_tag_applies_to_itself_too(self):
        self.assertEqual(_inherited_account_tags(self.journal, "assets"), [("type", "A")])

    def test_sibling_branch_does_not_inherit(self):
        # "assets:savings" is a sibling of "assets:bank", not a descendant
        # -- it must inherit "assets"'s own tag but NOT "assets:bank"'s.
        self.assertEqual(_inherited_account_tags(self.journal, "assets:savings"), [("type", "A")])


class TestPostingCommodities(unittest.TestCase):
    def test_no_amount_returns_empty(self):
        self.assertEqual(_posting_commodities(Posting(account="a")), [])

    def test_amount_returns_single_commodity(self):
        p = Posting(account="a", amount=Amount(Decimal("1"), "USD"))
        self.assertEqual(_posting_commodities(p), ["USD"])


class TestCommodityTags(unittest.TestCase):
    def setUp(self):
        self.journal = Journal(declared_commodity_tags={"$": [("rate", "2")], "EUR": [("rate", "9")]})

    def test_single_commodity_lookup(self):
        self.assertEqual(_commodity_tags(self.journal, ["$"]), [("rate", "2")])

    def test_multiple_commodities_concatenate(self):
        self.assertEqual(_commodity_tags(self.journal, ["$", "EUR"]), [("rate", "2"), ("rate", "9")])

    def test_undeclared_commodity_contributes_nothing(self):
        self.assertEqual(_commodity_tags(self.journal, ["GBP"]), [])

    def test_empty_list_returns_empty(self):
        self.assertEqual(_commodity_tags(self.journal, []), [])


class TestEffectiveTags(unittest.TestCase):
    """_effective_tags — the full four-source union (design §2.2/§2.6/§2.7:
    plain concatenation, no shadowing)."""

    def setUp(self):
        self.journal = Journal(
            declared_account_tags={"assets:bank": [("rate", "3")]},
            declared_commodity_tags={"$": [("rate", "2")]},
        )
        self.txn = Transaction(date=datetime.date(2024, 1, 1), description="x", tags=[("rate", "4")])
        self.posting = Posting(
            account="assets:bank", amount=Amount(Decimal("1"), "$"), tags=[("rate", "1")]
        )

    def test_unions_all_four_sources_with_no_dedup_by_name(self):
        self.assertEqual(
            _effective_tags(self.journal, self.txn, self.posting),
            [("rate", "1"), ("rate", "4"), ("rate", "3"), ("rate", "2")],
        )

    def test_posting_with_no_declared_tags_anywhere_is_empty(self):
        bare_journal = Journal()
        bare_txn = Transaction(date=datetime.date(2024, 1, 1), description="x")
        bare_posting = Posting(account="expenses:misc", amount=Amount(Decimal("1"), "GBP"))
        self.assertEqual(_effective_tags(bare_journal, bare_txn, bare_posting), [])

    def test_posting_with_no_amount_still_gets_account_and_txn_tags(self):
        # No commodity to propagate from, but account inheritance and
        # transaction tags are unaffected by a None amount.
        posting = Posting(account="assets:bank")
        self.assertEqual(
            _effective_tags(self.journal, self.txn, posting),
            [("rate", "4"), ("rate", "3")],
        )


class TestAccountsEffectiveTags(unittest.TestCase):
    """_accounts_effective_tags — the `accounts` command's narrower
    visibility mode (design §2.5/§9.2): transaction-own + account-
    inherited only, excluding posting-own and commodity-propagated."""

    def setUp(self):
        self.journal = Journal(
            declared_account_tags={"assets:bank": [("rate", "3")]},
            declared_commodity_tags={"$": [("rate", "2")]},
        )
        self.txn = Transaction(date=datetime.date(2024, 1, 1), description="x", tags=[("rate", "4")])
        self.posting = Posting(
            account="assets:bank", amount=Amount(Decimal("1"), "$"), tags=[("rate", "1")]
        )

    def test_excludes_posting_own_and_commodity_tags(self):
        self.assertEqual(
            _accounts_effective_tags(self.journal, self.txn, self.posting),
            [("rate", "4"), ("rate", "3")],
        )


if __name__ == "__main__":
    unittest.main()

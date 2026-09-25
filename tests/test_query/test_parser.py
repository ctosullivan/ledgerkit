"""Tests for ledgerkit.query.parser — query text -> QueryPlan."""

from __future__ import annotations

import datetime
import unittest

from ledgerkit.query.ast import Acct, And, DateSpan, Desc, Not, Or, Status, Tag, TxnStatus
from ledgerkit.query.depth import DepthSpec
from ledgerkit.query.parser import QueryParseError, parse


def _pred(text: str):
    """The selection-predicate half of parse(text) — most tests only care
    about this; depth: never appears in it (see TestDepthSpec below)."""
    return parse(text).predicate


class TestBarePatternAndPrefixes(unittest.TestCase):
    def test_bare_pattern_defaults_to_acct(self):
        self.assertEqual(_pred("groceries"), Acct("groceries"))

    def test_acct_prefix(self):
        self.assertEqual(_pred("acct:groceries"), Acct("groceries"))

    def test_desc_prefix(self):
        self.assertEqual(_pred("desc:amazon"), Desc("amazon"))

    def test_status_cleared(self):
        self.assertEqual(_pred("status:*"), Status(TxnStatus.CLEARED))

    def test_status_pending(self):
        self.assertEqual(_pred("status:!"), Status(TxnStatus.PENDING))

    def test_status_unmarked_bare(self):
        self.assertEqual(_pred("status:"), Status(TxnStatus.UNMARKED))

    def test_status_cleared_synonym_1(self):
        self.assertEqual(_pred("status:1"), Status(TxnStatus.CLEARED))

    def test_status_unmarked_synonym_0(self):
        self.assertEqual(_pred("status:0"), Status(TxnStatus.UNMARKED))

    def test_status_invalid_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("status:x")


class TestDepthSpec(unittest.TestCase):
    """depth: terms never join the selection predicate (Stage C Phase 5) —
    they're extracted into QueryPlan.depth, a report-display option. See
    dev-docs/planning/core-redefinition/
    21-stage-c-phase-5-depth-and-verification-plan.md."""

    def test_depth_prefix_produces_flat_depthspec_not_a_predicate_node(self):
        plan = parse("depth:2")
        self.assertEqual(plan.depth, DepthSpec(flat=2))
        self.assertEqual(plan.predicate, And(()))  # vacuous — matches everything

    def test_depth_zero_is_valid(self):
        self.assertEqual(parse("depth:0").depth, DepthSpec(flat=0))

    def test_depth_negative_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:-1")

    def test_depth_non_integer_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:abc")

    def test_depth_regex_form(self):
        plan = parse("depth:assets=2")
        self.assertEqual(plan.depth, DepthSpec(by_pattern=(("assets", 2),)))
        self.assertEqual(plan.predicate, And(()))

    def test_depth_regex_form_invalid_pattern_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:(=2")

    def test_depth_regex_form_non_integer_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:assets=abc")

    def test_multiple_flat_depth_terms_take_the_minimum(self):
        # Confirmed live against the pinned hledger 1.52.4 binary: multiple
        # depth:N terms WITHIN one query (not multiple --depth CLI flags,
        # a separate "last wins" rule Ledgerkit doesn't have a flag for
        # yet) combine via minimum, order-independent — hledger's own
        # DepthSpec Semigroup instance (Min-based), not last-wins.
        self.assertEqual(parse("depth:3 depth:1").depth, DepthSpec(flat=1))
        self.assertEqual(parse("depth:1 depth:3").depth, DepthSpec(flat=1))

    def test_flat_and_regex_depth_terms_accumulate(self):
        plan = parse("depth:assets=3 depth:1")
        self.assertEqual(plan.depth, DepthSpec(flat=1, by_pattern=(("assets", 3),)))

    def test_two_regex_depth_terms_both_accumulate(self):
        plan = parse("depth:assets=1 depth:savings=2")
        self.assertEqual(
            plan.depth,
            DepthSpec(by_pattern=(("assets", 1), ("savings", 2))),
        )

    def test_not_depth_rejected(self):
        # depth: is a report option, not a predicate — it cannot be
        # negated. Must raise cleanly, never silently fall through to
        # treating "depth:2" as a literal acct: pattern.
        with self.assertRaises(QueryParseError):
            parse("not:depth:2")

    def test_double_not_depth_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("not:not:depth:2")

    def test_no_depth_term_gives_empty_depthspec(self):
        self.assertEqual(parse("acct:food").depth, DepthSpec())
        self.assertTrue(parse("acct:food").depth.is_empty())


class TestQuoting(unittest.TestCase):
    def test_quoted_bare_pattern_with_space(self):
        self.assertEqual(_pred('"expenses dining"'), Acct("expenses dining"))

    def test_quoted_desc_with_space(self):
        self.assertEqual(_pred('desc:"whole foods"'), Desc("whole foods"))

    def test_unquoted_two_words_are_two_terms(self):
        self.assertEqual(_pred("expenses:dining out"), Or((Acct("expenses:dining"), Acct("out"))))


class TestDateSpans(unittest.TestCase):
    def test_single_date(self):
        self.assertEqual(
            _pred("date:2024-01-15"),
            DateSpan(datetime.date(2024, 1, 15), datetime.date(2024, 1, 16)),
        )

    def test_closed_range_dash_separator(self):
        self.assertEqual(
            _pred("date:2024-01-01-2024-02-01"),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_closed_range_dotdot_separator(self):
        self.assertEqual(
            _pred("date:2024-01-01..2024-02-01"),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_closed_range_to_separator(self):
        self.assertEqual(
            _pred('date:"2024-01-01 to 2024-02-01"'),
            DateSpan(datetime.date(2024, 1, 1), datetime.date(2024, 2, 1)),
        )

    def test_range_end_is_written_bound_not_auto_incremented(self):
        # Unlike the single-date case (which gets +1 day to form a
        # one-day span), a written range's second date becomes the
        # exclusive end exactly as given — so date:D1-2024-01-31 does
        # NOT include Jan 31 itself (17-query-semantics-brief.md §3).
        span = _pred("date:2024-01-01-2024-01-31")
        self.assertEqual(span.end, datetime.date(2024, 1, 31))
        self.assertNotEqual(span.end, datetime.date(2024, 2, 1))

    def test_open_ended_from(self):
        self.assertEqual(_pred("date:2024-01-01.."), DateSpan(datetime.date(2024, 1, 1), None))

    def test_open_ended_to(self):
        self.assertEqual(_pred("date:..2024-01-01"), DateSpan(None, datetime.date(2024, 1, 1)))

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
        self.assertEqual(_pred("not:groceries"), Not(Acct("groceries")))

    def test_not_wraps_prefixed_term(self):
        self.assertEqual(_pred("not:desc:amazon"), Not(Desc("amazon")))

    def test_double_negation(self):
        self.assertEqual(_pred("not:not:groceries"), Not(Not(Acct("groceries"))))

    def test_same_prefix_acct_terms_are_ored(self):
        self.assertEqual(_pred("acct:a acct:b"), Or((Acct("a"), Acct("b"))))

    def test_same_prefix_desc_terms_are_ored(self):
        self.assertEqual(_pred("desc:a desc:b"), Or((Desc("a"), Desc("b"))))

    def test_same_prefix_status_terms_are_ored(self):
        self.assertEqual(
            _pred("status: status:!"),
            Or((Status(TxnStatus.UNMARKED), Status(TxnStatus.PENDING))),
        )

    def test_different_prefixes_are_anded(self):
        # depth:2 is included here specifically to confirm it does NOT
        # appear in the predicate tree at all (Stage C Phase 5) — only
        # desc:/date: remain AND'd; depth:2 is checked separately below.
        plan = parse("date:2022-01-01.. desc:amazon depth:2")
        self.assertEqual(
            plan.predicate,
            And(
                (
                    Desc("amazon"),
                    DateSpan(datetime.date(2022, 1, 1), None),
                )
            ),
        )
        self.assertEqual(plan.depth, DepthSpec(flat=2))

    def test_negated_same_prefix_terms_are_anded_not_ored(self):
        # The central footgun from 17-query-semantics-brief.md §6: two
        # negated acct: terms must both be individually AND'd (must match
        # neither), not OR'd (which would mean "match not-a or not-b" — a
        # much weaker, almost-always-true exclusion).
        self.assertEqual(
            _pred("not:acct:a not:acct:b"),
            And((Not(Acct("a")), Not(Acct("b")))),
        )

    def test_mixed_negated_and_unnegated_same_prefix(self):
        self.assertEqual(
            _pred("acct:a acct:b not:acct:c"),
            And((Or((Acct("a"), Acct("b"))), Not(Acct("c")))),
        )


class TestTag(unittest.TestCase):
    """tag:NAME[=REGEX] parsing — Stage C Phase 6
    (23-tag-query-matching-design.md §5.2, §12; 24-tag-query-matching-
    implementation-plan.md)."""

    def test_bare_name_no_value_pattern(self):
        # Bare tag:NAME means "any value, including empty" — represented
        # as value_pattern=None, not an empty-string pattern.
        self.assertEqual(_pred("tag:rate"), Tag("rate", None))

    def test_name_equals_value(self):
        self.assertEqual(_pred("tag:rate=3"), Tag("rate", "3"))

    def test_empty_value_pattern_rejected(self):
        # tag:NAME= (trailing '=' with nothing after) is an empty value
        # PATTERN, distinct from bare tag:NAME's None. Stage C Phase 7
        # (26-query-regex-empty-pattern-design.md): real hledger rejects
        # an empty regex pattern at parse time, so this now raises
        # QueryParseError -- a breaking change from Stage C Phase 6, when
        # this parsed successfully to Tag("rate", "").
        with self.assertRaises(QueryParseError):
            parse("tag:rate=")

    def test_value_containing_equals_preserves_everything_after_first(self):
        # tag:rate==0.05 -- a tag literally named "rate" with value
        # "=0.05". partition("=") splits on the FIRST '=' only (design
        # §12/§2.1), so everything after it (including the second '=')
        # is preserved as the value pattern.
        self.assertEqual(_pred("tag:rate==0.05"), Tag("rate", "=0.05"))

    def test_dot_name_pattern_value_only_matching(self):
        # tag:.=VALUE -- name pattern "." (matches any single character,
        # in practice any non-empty name) with a real value constraint.
        # Ordinary regex behaviour, no special-casing (design §12).
        self.assertEqual(_pred("tag:.=VALUE"), Tag(".", "VALUE"))

    def test_malformed_name_regex_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("tag:(")

    def test_malformed_value_regex_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("tag:rate=(")

    def test_not_tag_negation(self):
        # Unlike depth:, tag: is an ordinary predicate — not: is allowed,
        # no special rejection (design §8/§13).
        self.assertEqual(_pred("not:tag:rate=3"), Not(Tag("rate", "3")))

    def test_multiple_tag_terms_and_not_or(self):
        # Design §2.3/§8: multiple tag: terms AND together (tag: is not
        # one of the three OR-eligible prefixes acct:/desc:/status:), so
        # this falls into other_terms and AND-combines automatically —
        # confirmed here rather than merely asserted by the design.
        self.assertEqual(_pred("tag:a tag:b"), And((Tag("a", None), Tag("b", None))))

    def test_tag_and_acct_combine_with_and(self):
        self.assertEqual(_pred("tag:a acct:food"), And((Acct("food"), Tag("a", None))))


class TestMalformedRegexRaisesAtParseTime(unittest.TestCase):
    """Stage C Phase 2 fix: a syntactically-invalid (but not excluded-
    construct) regex must fail at parse time with QueryParseError, not
    surface as a raw re.error later inside ledgerkit.query.eval the first
    time a posting is actually checked against it."""

    def test_unterminated_group_in_acct(self):
        with self.assertRaises(QueryParseError):
            parse("acct:(")

    def test_unterminated_group_in_desc(self):
        with self.assertRaises(QueryParseError):
            parse("desc:(")

    def test_unbalanced_bracket(self):
        with self.assertRaises(QueryParseError):
            parse("acct:[abc")


class TestEmptyPatternRejected(unittest.TestCase):
    """Stage C Phase 7 (26-query-regex-empty-pattern-design.md): real
    hledger rejects an empty regex pattern at parse time for every prefix
    that accepts one. Covers the full matrix the design's own §10 names:
    acct:, desc:, tag: (bare, empty NAME slot), tag:NAME= (empty VALUE
    slot), depth:REGEX=N (empty REGEX half), and not:-wrapped forms."""

    def test_bare_acct_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("acct:")

    def test_bare_desc_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("desc:")

    def test_bare_tag_rejected(self):
        # tag: alone (nothing after the colon, no '=' at all) routes the
        # empty string through the NAME slot -- same underlying rejection
        # as tag:NAME='s empty VALUE slot (design §3/§10).
        with self.assertRaises(QueryParseError):
            parse("tag:")

    def test_tag_name_equals_empty_value_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("tag:rate=")

    def test_depth_regex_form_empty_pattern_rejected(self):
        with self.assertRaises(QueryParseError):
            parse("depth:=2")

    def test_not_acct_empty_pattern_still_rejected_at_parse_time(self):
        # Rejection happens before negation is ever considered (design
        # §2, live-confirmed against hledger: not:acct: fails identically
        # to bare acct:).
        with self.assertRaises(QueryParseError):
            parse("not:acct:")

    def test_error_message_contains_no_tag_specific_advice(self):
        # Regression guard: the shared validator's message must not bake
        # in tag:-specific advice, since acct:/desc:/depth: reach the
        # exact same check (design §5, corrected on review).
        try:
            parse("acct:")
        except QueryParseError as exc:
            self.assertNotIn("tag:NAME", str(exc))
        else:
            self.fail("expected QueryParseError")


class TestEmptyQuery(unittest.TestCase):
    def test_empty_string_matches_everything(self):
        plan = parse("")
        self.assertEqual(plan.predicate, And(()))
        self.assertEqual(plan.depth, DepthSpec())

    def test_whitespace_only_matches_everything(self):
        self.assertEqual(parse("   ").predicate, And(()))


if __name__ == "__main__":
    unittest.main()

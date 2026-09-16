"""Query text -> QueryAST parser.

Implements Stage C's initial term set only: acct:/bare pattern, desc:,
date: (simple dates — a single full date, or two full dates joined by
'-'/'..'/' to ', open-ended forms allowed), depth:, status:, and not:/
implicit-AND/same-prefix-OR combination. tag:, cur:, and hledger's smart/
period date expressions are not implemented (deliberately out of scope —
see `dev-docs/planning/core-redefinition/17-query-semantics-brief.md`).

Combination semantics mirror hledger's own `combineQueriesByType`
(verified in the semantics brief §6): unnegated acct:/desc:/status: terms
of the same prefix are OR-combined with each other; everything else
(date:, depth:, and every not:-wrapped term regardless of its own prefix)
is AND-combined individually. This is not a design choice made here — it
is hledger's actual, source-verified behaviour, replicated deliberately.
"""

from __future__ import annotations

import datetime
import re

from ledgerkit.query.ast import Acct, And, DateSpan, Depth, Desc, Not, Or, QueryNode, Status, TxnStatus
from ledgerkit.query.regex import compile_hledger_regex


class QueryParseError(ValueError):
    """The query string is malformed or uses an unsupported construct."""


# Splits a query string into tokens, treating a single- or double-quoted
# run as part of the same token as any prefix immediately before it and
# any trailing characters immediately after it, with the quote characters
# themselves stripped — mirrors hledger's own `words''` tokenizer, which is
# how multi-word acct:/desc: patterns are written as a single term (e.g.
# desc:"whole foods", not just a bare quoted "whole foods").
#
# Purpose: tokenize on whitespace while (a) keeping a `prefix:"quoted
#          phrase"` together as one token and (b) degrading gracefully,
#          rather than raising, if a quote is never closed.
#
# Group breakdown:
#   (prefix) [^\s'"]*        — non-space, non-quote run before any quote
#                              (the prefix:, e.g. "desc:"; empty if the
#                              token starts directly with a quote or has
#                              no quote at all)
#   (sq)     '([^']*)'       — single-quoted content, quotes stripped
#   (dq)     "([^"]*)"       — double-quoted content, quotes stripped
#   (rest)   \S*             — anything left in this whitespace-run after
#                              a quoted section (rare), or the *entire*
#                              remainder when no quote successfully closes
#
# Edge cases:
#   - (?=\S) requires the match to start on a non-space character, so
#     finditer skips whitespace between tokens instead of matching
#     zero-length there.
#   - `prefix`'s character class excludes quote characters, so it always
#     stops exactly at a quote rather than swallowing it — guaranteeing
#     the quoted-group alternative gets a chance to match from there.
#   - An unterminated quote (no matching close before the run ends) makes
#     the quoted-group alternative fail; `rest` (which, unlike `prefix`,
#     is NOT quote-excluding) then consumes the stray quote character and
#     everything after it as plain literal text — e.g. "don't" becomes the
#     single literal token "don't", not a parse error. Deliberately
#     lenient; hledger's own words'' raises on this instead.
#   - Quotes cannot be escaped inside a quoted token (matches hledger's
#     own limitation, not a gap introduced here).
_TOKEN = re.compile(
    r"""(?=\S)
    (?P<prefix>[^\s'"]*)
    (?:'(?P<sq>[^']*)'|"(?P<dq>[^"]*)")?
    (?P<rest>\S*)
    """,
    re.VERBOSE,
)


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for m in _TOKEN.finditer(text):
        quoted = m.group("sq") if m.group("sq") is not None else m.group("dq")
        tokens.append((m.group("prefix") or "") + (quoted if quoted is not None else "") + (m.group("rest") or ""))
    return tokens


# A single full simple date: year mandatory (unlike the journal-header
# date parser, which allows year to be inferred from a preceding Y
# directive — no such context exists at query-parse time), 1-2 digit
# month/day, any of '-', '/', '.' as separator (matching the journal
# parser's own accepted separator set).
#
# Purpose: recognise one complete calendar date within a date: term.
#
# Group breakdown: no capture groups here — used only as a sub-pattern
#   embedded (via string formatting) inside _DATE_SPAN's named groups;
#   the actual year/month/day extraction happens in _DATE_TOKEN_PARTS.
#
# Edge cases:
#   - "24-01-15" (2-digit year) does NOT match — \d{4} requires exactly
#     four digits, deliberately: query dates must be unambiguous.
_DATE_TOKEN = r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}"

# Splits an already-matched _DATE_TOKEN substring into its year/month/day
# parts so datetime.date() can validate and construct it.
#
# Purpose: decompose one confirmed-shape date token into integer components.
#
# Group breakdown:
#   (1) (\d{4})   — four-digit year
#   (2) (\d{1,2}) — month, leading zero optional
#   (3) (\d{1,2}) — day, leading zero optional
#
# Edge cases:
#   - Invalid calendar values (e.g. "2024-13-01") match this regex but
#     raise ValueError from datetime.date(), converted to QueryParseError
#     by the caller.
_DATE_TOKEN_PARTS = re.compile(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$")

# Recognises the four shapes a date: value may take: a closed range
# (two dates joined by '-', '..', or ' to '), an open-ended "from" range
# (one date followed by '..'), an open-ended "to" range ('..' followed by
# one date), or a single bare date.
#
# Purpose: classify a date: term's value into exactly one of these shapes
#          before extracting the date(s) it names.
#
# Group breakdown (named; each holds one full _DATE_TOKEN substring):
#   range_d1, range_d2 — closed range's start/end dates
#   open_from          — the single date in a "D.." open-ended-from range
#   open_to            — the single date in a "..D" open-ended-to range
#   single             — the one date in a bare (non-range) date: term
#
# Edge cases:
#   - Alternation order does not create ambiguity despite '-'/'..'
#     appearing in more than one branch: the '$' end-anchor means only
#     the branch matching the *entire* remaining value can succeed for
#     any given input (e.g. "D.." cannot satisfy the range branch, which
#     requires a second full date after the separator).
#   - "D1-D2-D3" (more than two dates) matches nothing — QueryParseError.
_DATE_SPAN = re.compile(
    r"^(?:"
    rf"(?P<range_d1>{_DATE_TOKEN})(?:-|\.\.| to )(?P<range_d2>{_DATE_TOKEN})"
    rf"|(?P<open_from>{_DATE_TOKEN})\.\."
    rf"|\.\.(?P<open_to>{_DATE_TOKEN})"
    rf"|(?P<single>{_DATE_TOKEN})"
    r")$"
)

_STATUS_VALUES = {
    "": TxnStatus.UNMARKED,
    "0": TxnStatus.UNMARKED,
    "*": TxnStatus.CLEARED,
    "1": TxnStatus.CLEARED,
    "!": TxnStatus.PENDING,
}


def _parse_date_token(token: str) -> datetime.date:
    m = _DATE_TOKEN_PARTS.match(token)
    assert m is not None, f"internal error: {token!r} matched _DATE_TOKEN but not _DATE_TOKEN_PARTS"
    year, month, day = (int(g) for g in m.groups())
    try:
        return datetime.date(year, month, day)
    except ValueError as exc:
        raise QueryParseError(f"date: invalid calendar date {token!r}: {exc}") from exc


def _build_acct(value: str) -> Acct:
    # compile_hledger_regex both validates against the HledgerRegex subset
    # (raises UnsupportedRegexConstructError, a ValueError) and confirms the
    # pattern is syntactically valid Python regex at all (raises re.error) —
    # catching both here means a malformed pattern (e.g. an unterminated
    # group, "acct:(") fails at parse time with a clear QueryParseError,
    # rather than surfacing as a raw re.error later, deep inside eval.py's
    # matching, the first time a posting is actually checked against it.
    try:
        compile_hledger_regex(value)
    except (ValueError, re.error) as exc:
        raise QueryParseError(f"acct: {exc}") from exc
    return Acct(value)


def _build_desc(value: str) -> Desc:
    try:
        compile_hledger_regex(value)
    except (ValueError, re.error) as exc:
        raise QueryParseError(f"desc: {exc}") from exc
    return Desc(value)


def _build_depth(value: str) -> Depth:
    try:
        n = int(value)
    except ValueError:
        raise QueryParseError(f"depth: expects an integer, got {value!r}") from None
    if n < 0:
        raise QueryParseError(f"depth: expects a non-negative integer, got {n}")
    return Depth(n)


def _build_status(value: str) -> Status:
    try:
        return Status(_STATUS_VALUES[value])
    except KeyError:
        raise QueryParseError(
            f"status: expects one of '', '*', '!', '0', '1', got {value!r}"
        ) from None


def _build_date(value: str) -> DateSpan:
    m = _DATE_SPAN.match(value)
    if m is None:
        raise QueryParseError(
            f"date: expects a simple date or date range (e.g. '2024-01-15', "
            f"'2024-01-01..2024-02-01'), got {value!r}"
        )
    if m.group("single") is not None:
        d = _parse_date_token(m.group("single"))
        return DateSpan(d, d + datetime.timedelta(days=1))
    if m.group("range_d1") is not None:
        return DateSpan(_parse_date_token(m.group("range_d1")), _parse_date_token(m.group("range_d2")))
    if m.group("open_from") is not None:
        return DateSpan(_parse_date_token(m.group("open_from")), None)
    return DateSpan(None, _parse_date_token(m.group("open_to")))


_PREFIX_BUILDERS = {
    "acct:": _build_acct,
    "desc:": _build_desc,
    "date:": _build_date,
    "depth:": _build_depth,
    "status:": _build_status,
}


def _parse_term(token: str) -> QueryNode:
    if token.startswith("not:"):
        return Not(_parse_term(token[len("not:"):]))
    for prefix, builder in _PREFIX_BUILDERS.items():
        if token.startswith(prefix):
            return builder(token[len(prefix):])
    # No recognised prefix: bare pattern defaults to acct: (hledger's
    # defaultprefix), per 17-query-semantics-brief.md §1.
    return _build_acct(token)


def _simplify(node: QueryNode) -> QueryNode:
    if isinstance(node, And):
        if len(node.terms) == 1:
            return _simplify(node.terms[0])
        return And(tuple(_simplify(t) for t in node.terms))
    if isinstance(node, Or):
        if len(node.terms) == 1:
            return _simplify(node.terms[0])
        return Or(tuple(_simplify(t) for t in node.terms))
    if isinstance(node, Not):
        return Not(_simplify(node.term))
    return node


def parse(query_text: str) -> QueryNode:
    """Parse a query string into a QueryNode.

    An empty or whitespace-only string parses to `And(())` — the vacuous
    "match everything" query, consistent with `Query()`/`query=None`
    elsewhere in ledgerkit.

    Raises:
        QueryParseError: the string is malformed, or a term uses a
            construct outside this phase's supported subset.
    """
    tokens = _tokenize(query_text)
    terms = [_parse_term(t) for t in tokens]

    # Replicates hledger's combineQueriesByType: unnegated acct:/desc:/
    # status: terms of the same type are OR'd with each other; every other
    # term (date:, depth:, and any not:-wrapped term of any prefix) is
    # AND'd in individually. A Not(...) node is never pulled into an OR
    # bucket even when its wrapped prefix matches one of the three types —
    # see 17-query-semantics-brief.md §6.
    acct_terms = [t for t in terms if isinstance(t, Acct)]
    desc_terms = [t for t in terms if isinstance(t, Desc)]
    status_terms = [t for t in terms if isinstance(t, Status)]
    other_terms = [t for t in terms if not isinstance(t, (Acct, Desc, Status))]

    buckets: list[QueryNode] = []
    if acct_terms:
        buckets.append(Or(tuple(acct_terms)))
    if desc_terms:
        buckets.append(Or(tuple(desc_terms)))
    if status_terms:
        buckets.append(Or(tuple(status_terms)))

    return _simplify(And(tuple(buckets + other_terms)))

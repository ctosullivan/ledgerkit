"""Query AST node types.

Mirrors hledger's own query term set (see hledger.1 "Queries" section) for
Stage C's initial target: acct:, desc:, date: (simple dates only), status:,
tag:NAME[=REGEX] (Stage C Phase 6 — see `Tag` below), and not:/implicit-AND/
same-prefix-OR combination. `depth:` is deliberately
NOT a node here — as of Stage C Phase 5 it is `ledgerkit.query.depth.
DepthSpec`, a report-display option carried on `QueryPlan.depth`, never a
selection predicate (see `MaxAccountLevel`'s docstring below for why, and
`21-stage-c-phase-5-depth-and-verification-plan.md` for the evidence).
Node shapes and matching semantics are sourced from `dev-docs/planning/
core-redefinition/17-query-semantics-brief.md`, differentially verified
against the pinned hledger 1.52.4 binary (Stage C Phase 2 onward).

No node type here executes anything — see ledgerkit.query.eval for
evaluation and ledgerkit.query.parser for query-text parsing.
"""

from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass, field
from typing import Union

from ledgerkit.query.depth import DepthSpec


class TxnStatus(enum.Enum):
    """A transaction's cleared/pending/unmarked status.

    Ledgerkit's Transaction model has no per-posting status override (only
    Transaction.cleared/pending) — unlike hledger, where an individual
    posting can carry its own status distinct from its transaction's. See
    `17-query-semantics-brief.md` §5: this is a genuine, existing model
    limitation, not something this query package invents or should paper
    over silently.
    """

    UNMARKED = "unmarked"
    PENDING = "pending"
    CLEARED = "cleared"


@dataclass(frozen=True)
class Acct:
    """Matches a posting whose account name contains `pattern`.

    `pattern` must already be a validated HledgerRegex-dialect pattern
    (ledgerkit.query.regex.validate_hledger_regex) — this node does not
    itself validate or compile it; that happens once, at parse time.
    """

    pattern: str


@dataclass(frozen=True)
class Desc:
    """Matches a transaction whose description contains `pattern`.

    Same HledgerRegex-dialect contract as `Acct.pattern`.
    """

    pattern: str


@dataclass(frozen=True)
class DateSpan:
    """Matches a transaction whose date falls within [start, end).

    `end` is EXCLUSIVE, matching hledger's actual `date:` span semantics
    (`17-query-semantics-brief.md` §3) — this is deliberately different
    from the existing `ledgerkit.models.Query.date_to`, which is
    inclusive. `start`/`end` of None means unbounded on that side.
    """

    start: datetime.date | None
    end: datetime.date | None


@dataclass(frozen=True)
class MaxAccountLevel:
    """Ledgerkit-native: matches a posting whose account is at or above
    tree depth `n` (colon-segment count, `accountNameLevel` in hledger).

    This is deliberately NOT hledger's `depth:`/`--depth` — confirmed
    across every real hledger command (`balance`/`register`/`print`/
    `accounts`/`aregister`) that `depth:` is always a report-display
    clipping/aggregation option, never a selection predicate; see
    `ledgerkit.query.depth.DepthSpec` for that, and
    `dev-docs/planning/core-redefinition/
    21-stage-c-phase-5-depth-and-verification-plan.md` §1.3/§3.1 for the
    full evidence and the decision to keep this as a distinct, disclosed
    Ledgerkit-only primitive rather than overload hledger's own `depth:`
    token for different semantics. Renamed from the earlier `Depth` (Stage
    C Phase 1) for exactly that reason — see `knowledge/DECISIONS.md`,
    2026-09-17.

    Python-API-only: there is no `-q`/`--query` string-syntax spelling for
    this node — `ledgerkit.query.parser.parse()` never produces one; it is
    reachable only by constructing `MaxAccountLevel(n)` directly and
    passing it into `matches_transaction`/`matches_posting` yourself.
    `n >= 0` is the only valid range enforced by callers that build one
    programmatically; this dataclass itself does not validate `n`.
    """

    n: int


@dataclass(frozen=True)
class Status:
    """Matches a transaction with the given cleared/pending/unmarked status."""

    value: TxnStatus


@dataclass(frozen=True)
class Tag:
    """Matches an effective tag name (and, if given, value) — Stage C Phase 6.

    `name_pattern` must already be a validated HledgerRegex-dialect
    pattern, matched against tag names. `value_pattern` is the same, but
    matched against tag values; `None` means "any value, including
    empty" (a bare `tag:NAME` term). Both are case-insensitive infix
    matches, same contract as `Acct`/`Desc`.

    "Effective tags" means the full four-source union hledger's own
    `tag:` reads from — a posting's/transaction's own literal comment
    tags, its account's declared-and-inherited tags, and its main
    amount's commodity's declared tags (see `ledgerkit.tags._effective_tags`
    and `dev-docs/planning/core-redefinition/
    23-tag-query-matching-design.md` §2.2/§2.6/§2.7) — not merely
    `Posting.tags`/`Transaction.tags`'s own literal contents. Evaluating a
    `Tag` node therefore needs `Journal` access — see
    `ledgerkit.query.eval.matches_transaction`/`matches_posting`'s
    `journal` parameter; a `Tag` node evaluated with no `journal` raises
    `ValueError`, never silently narrows to own-tags-only.
    """

    name_pattern: str
    value_pattern: str | None = None


@dataclass(frozen=True)
class And:
    """Matches when every child node matches."""

    terms: tuple["QueryNode", ...]


@dataclass(frozen=True)
class Or:
    """Matches when at least one child node matches."""

    terms: tuple["QueryNode", ...]


@dataclass(frozen=True)
class Not:
    """Matches when the wrapped node does not match.

    A negated term of any kind is always plain-AND'd with its siblings —
    it never joins an Or bucket, even when another unnegated term of the
    same prefix is present elsewhere in the query
    (`17-query-semantics-brief.md` §6's central finding).
    """

    term: "QueryNode"


QueryNode = Union[Acct, Desc, DateSpan, MaxAccountLevel, Status, Tag, And, Or, Not]


@dataclass(frozen=True)
class QueryPlan:
    """The result of parsing a query string: a selection predicate plus
    report/display options that are never part of that predicate.

    `predicate`: the `QueryNode` tree — never contains a `MaxAccountLevel`
        node (the string grammar has no way to produce one; see
        `ledgerkit.query.parser.parse`).
    `depth`: the `DepthSpec` accumulated from any `depth:N`/`depth:REGEX=N`
        terms in the query text. Defaults to the empty spec (no clipping)
        for a query with no depth: term at all.
    """

    predicate: "QueryNode"
    depth: DepthSpec = field(default_factory=DepthSpec)

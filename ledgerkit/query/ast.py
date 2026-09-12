"""Query AST node types.

Mirrors hledger's own query term set (see hledger.1 "Queries" section) for
Stage C's initial target: acct:, desc:, date: (simple dates only), depth:,
status:, and not:/implicit-AND/same-prefix-OR combination. Node shapes and
matching semantics are sourced from `dev-docs/planning/core-redefinition/
17-query-semantics-brief.md`, verified against the pinned hledger 1.52.4
source (not yet executable-verified against a real hledger binary).

No node type here executes anything — see ledgerkit.query.eval for
evaluation and ledgerkit.query.parser for query-text parsing.
"""

from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass
from typing import Union


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
class Depth:
    """Matches a posting whose account is at or above tree depth `n`.

    Depth is colon-segment count (`accountNameLevel` in hledger): `n >= 0`
    is the only valid range — `depth:0` is legal input but matches
    essentially nothing, per `17-query-semantics-brief.md` §4. This node
    is a pure boolean predicate; hledger's separate depth-driven *display*
    truncation/aggregation for balance/register is deliberately not
    represented here (§4's recommendation).
    """

    n: int


@dataclass(frozen=True)
class Status:
    """Matches a transaction with the given cleared/pending/unmarked status."""

    value: TxnStatus


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


QueryNode = Union[Acct, Desc, DateSpan, Depth, Status, And, Or, Not]

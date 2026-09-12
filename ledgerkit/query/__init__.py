"""Stage C query engine: query text -> QueryAST -> predicate.

Public surface for Ledgerkit's initial hledger-compatible query-term
support (`acct:`, `desc:`, `date:` [simple dates only], `depth:`,
`status:`, `not:`). Not yet wired into `reports.py`/`cli.py`/`Query` — see
`dev-docs/planning/core-redefinition/16-model-review.md` and
`17-query-semantics-brief.md` for status. `tag:`, `cur:`, hledger's smart/
period date expressions, and the `PythonRegex` extension syntax are not
implemented yet (Stage C follow-on work).
"""

from __future__ import annotations

from ledgerkit.query.ast import Acct, And, DateSpan, Depth, Desc, Not, Or, QueryNode, Status, TxnStatus
from ledgerkit.query.eval import matches_posting, matches_transaction
from ledgerkit.query.parser import QueryParseError, parse
from ledgerkit.query.regex import UnsupportedRegexConstructError, compile_hledger_regex, validate_hledger_regex

__all__ = [
    "Acct",
    "Desc",
    "DateSpan",
    "Depth",
    "Status",
    "TxnStatus",
    "And",
    "Or",
    "Not",
    "QueryNode",
    "parse",
    "QueryParseError",
    "matches_transaction",
    "matches_posting",
    "validate_hledger_regex",
    "compile_hledger_regex",
    "UnsupportedRegexConstructError",
]

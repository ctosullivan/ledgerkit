"""Stage C query engine: query text -> QueryPlan (predicate + DepthSpec).

Public surface for Ledgerkit's initial hledger-compatible query-term
support (`acct:`, `desc:`, `date:` [simple dates only], `depth:`,
`status:`, `not:`). Wired into `reports.py`/`cli.py` via `-q`/`--query`
since Stage C Phase 2-3; `depth:` specifically produces a `DepthSpec`
report option (`QueryPlan.depth`), never a selection-predicate node — see
`dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md`. `tag:`, `cur:`,
hledger's smart/period date expressions, and the `PythonRegex` extension
syntax are not implemented yet (Stage C follow-on work).
"""

from __future__ import annotations

from ledgerkit.query.ast import Acct, And, DateSpan, Desc, MaxAccountLevel, Not, Or, QueryNode, QueryPlan, Status, TxnStatus
from ledgerkit.query.depth import DepthSpec, clip_account_name, clipped_depth_for_account, merge_depth_specs
from ledgerkit.query.eval import matches_posting, matches_transaction
from ledgerkit.query.parser import QueryParseError, parse
from ledgerkit.query.regex import UnsupportedRegexConstructError, compile_hledger_regex, validate_hledger_regex

__all__ = [
    "Acct",
    "Desc",
    "DateSpan",
    "MaxAccountLevel",
    "Status",
    "TxnStatus",
    "And",
    "Or",
    "Not",
    "QueryNode",
    "QueryPlan",
    "DepthSpec",
    "clipped_depth_for_account",
    "clip_account_name",
    "merge_depth_specs",
    "parse",
    "QueryParseError",
    "matches_transaction",
    "matches_posting",
    "validate_hledger_regex",
    "compile_hledger_regex",
    "UnsupportedRegexConstructError",
]

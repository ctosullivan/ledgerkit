"""QueryAST -> predicate evaluation over Transaction/Posting.

Two entry points, matching hledger's own transaction- vs posting-oriented
matching (`17-query-semantics-brief.md` §1-§5): `matches_transaction` (used
by transaction-oriented commands like `print`) and `matches_posting` (used
by posting-oriented commands like `register`/`balance`). Acct/
MaxAccountLevel use hledger's "any posting matches" rule at the
transaction level; Desc/Status are transaction-level facts that a posting
simply inherits. `depth:` is not evaluated here at all as of Stage C
Phase 5 — see `ledgerkit.query.depth`.
"""

from __future__ import annotations

import datetime
import functools

from ledgerkit.models import Posting, Transaction
from ledgerkit.query.ast import Acct, And, DateSpan, Desc, MaxAccountLevel, Not, Or, QueryNode, Status, TxnStatus
from ledgerkit.query.regex import compile_hledger_regex


@functools.lru_cache(maxsize=None)
def _compiled(pattern: str):
    return compile_hledger_regex(pattern)


def _account_matches(pattern: str, account: str) -> bool:
    return bool(_compiled(pattern).search(account))


def _text_matches(pattern: str, text: str) -> bool:
    return bool(_compiled(pattern).search(text))


def _account_depth(account: str) -> int:
    """Colon-segment count: accountNameLevel in hledger (empty name -> 0)."""
    return account.count(":") + 1 if account else 0


def _date_in_span(d: datetime.date, span: DateSpan) -> bool:
    if span.start is not None and d < span.start:
        return False
    if span.end is not None and d >= span.end:
        return False
    return True


def _txn_status(txn: Transaction) -> TxnStatus:
    """Ledgerkit's Transaction has no per-posting status override (see
    ast.TxnStatus's docstring) — this is always the transaction's own
    cleared/pending/unmarked state."""
    if txn.cleared:
        return TxnStatus.CLEARED
    if txn.pending:
        return TxnStatus.PENDING
    return TxnStatus.UNMARKED


def matches_transaction(node: QueryNode, txn: Transaction) -> bool:
    """Return True if `txn` matches `node` (transaction-oriented matching).

    Acct/MaxAccountLevel match if *any* posting in the transaction matches
    (hledger's `matchesTransaction q@(Acct _) t = any (q \`matchesPosting\`)
    $ tpostings t` rule; MaxAccountLevel mirrors it as a Ledgerkit-native
    convenience, not because hledger's own `depth:` works this way — see
    `MaxAccountLevel`'s docstring).
    """
    if isinstance(node, Acct):
        return any(_account_matches(node.pattern, p.account) for p in txn.postings)
    if isinstance(node, Desc):
        return _text_matches(node.pattern, txn.description)
    if isinstance(node, DateSpan):
        return _date_in_span(txn.date, node)
    if isinstance(node, MaxAccountLevel):
        return any(_account_depth(p.account) <= node.n for p in txn.postings)
    if isinstance(node, Status):
        return _txn_status(txn) == node.value
    if isinstance(node, And):
        return all(matches_transaction(t, txn) for t in node.terms)
    if isinstance(node, Or):
        return any(matches_transaction(t, txn) for t in node.terms)
    if isinstance(node, Not):
        return not matches_transaction(node.term, txn)
    raise TypeError(f"unhandled query node type: {type(node)!r}")  # pragma: no cover


def matches_posting(node: QueryNode, txn: Transaction, posting: Posting) -> bool:
    """Return True if `posting` (within `txn`) matches `node`.

    Desc/DateSpan/Status are transaction-level facts a posting inherits
    unchanged; Acct/Depth are checked against the posting's own account.
    """
    if isinstance(node, Acct):
        return _account_matches(node.pattern, posting.account)
    if isinstance(node, Desc):
        return _text_matches(node.pattern, txn.description)
    if isinstance(node, DateSpan):
        return _date_in_span(txn.date, node)
    if isinstance(node, MaxAccountLevel):
        return _account_depth(posting.account) <= node.n
    if isinstance(node, Status):
        return _txn_status(txn) == node.value
    if isinstance(node, And):
        return all(matches_posting(t, txn, posting) for t in node.terms)
    if isinstance(node, Or):
        return any(matches_posting(t, txn, posting) for t in node.terms)
    if isinstance(node, Not):
        return not matches_posting(node.term, txn, posting)
    raise TypeError(f"unhandled query node type: {type(node)!r}")  # pragma: no cover

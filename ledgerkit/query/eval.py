"""QueryAST -> predicate evaluation over Transaction/Posting.

Two entry points, matching hledger's own transaction- vs posting-oriented
matching (`17-query-semantics-brief.md` §1-§5): `matches_transaction` (used
by transaction-oriented commands like `print`) and `matches_posting` (used
by posting-oriented commands like `register`/`balance`). Acct/
MaxAccountLevel use hledger's "any posting matches" rule at the
transaction level; Desc/Status are transaction-level facts that a posting
simply inherits. `depth:` is not evaluated here at all as of Stage C
Phase 5 — see `ledgerkit.query.depth`.

Stage C Phase 6 added `Tag` matching, which — unlike every other node type
here — needs `Journal` access (to compute effective tags: account
inheritance and commodity propagation, not just each entity's own literal
`tags` list; see `ledgerkit.tags._effective_tags`). Both entry points gain
an optional `journal: Journal | None = None` parameter for this
(`23-tag-query-matching-design.md` §9.1/§11,
`24-tag-query-matching-implementation-plan.md`'s resolution of the
evaluator-API shape). Existing callers that never construct a `Tag` node
are unaffected by the new parameter; a `Tag` node evaluated with
`journal=None` raises `ValueError` — never silently narrows to
own-tags-only (the design's binding loud-failure constraint).
"""

from __future__ import annotations

import datetime
import functools
from typing import Callable

from ledgerkit.models import Journal, Posting, Transaction
from ledgerkit.query.ast import Acct, And, DateSpan, Desc, MaxAccountLevel, Not, Or, QueryNode, Status, Tag, TxnStatus
from ledgerkit.query.regex import compile_hledger_regex
from ledgerkit.tags import _accounts_effective_tags, _effective_tags

# A function computing the "effective tags" a Tag node should be matched
# against for one (txn, posting) pair — either the full four-source
# ledgerkit.tags._effective_tags (every ordinary command) or the narrower
# ledgerkit.tags._accounts_effective_tags (the `accounts` command's own
# visibility mode, design §2.5/§9.2). Threaded through _matches_posting_impl
# below so the two modes share one recursive dispatch instead of two
# parallel copies of the And/Or/Not/Acct/... branches.
_TagSourceFn = Callable[[Journal, Transaction, Posting], list]


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


def _tag_matches(node: Tag, tags: list[tuple[str, str]]) -> bool:
    """Return True if any (name, value) pair in `tags` matches `node`.

    `node.name_pattern` must match the name; when `node.value_pattern` is
    None (a bare `tag:NAME` term) any value — including an empty one —
    is accepted for a name match, per design §2.1/§12.
    """
    name_re = _compiled(node.name_pattern)
    value_re = _compiled(node.value_pattern) if node.value_pattern is not None else None
    for name, value in tags:
        if not name_re.search(name):
            continue
        if value_re is None or value_re.search(value):
            return True
    return False


def matches_transaction(node: QueryNode, txn: Transaction, journal: Journal | None = None) -> bool:
    """Return True if `txn` matches `node` (transaction-oriented matching).

    Acct/MaxAccountLevel match if *any* posting in the transaction matches
    (hledger's `matchesTransaction q@(Acct _) t = any (q \`matchesPosting\`)
    $ tpostings t` rule; MaxAccountLevel mirrors it as a Ledgerkit-native
    convenience, not because hledger's own `depth:` works this way — see
    `MaxAccountLevel`'s docstring).

    Tag (Stage C Phase 6) matches if `txn`'s own tags directly match, OR
    any of its postings' effective tags match — both halves are real,
    independent inputs (design §6): hledger's own `transactionAllTags t =
    ttags t ++ concatMap ptags (tpostings t)` unions the transaction's own
    tags in directly, not solely by delegating to each posting's
    effective-tags computation. Requires `journal` — raises ValueError if
    a Tag node is present and `journal` is None (never silently narrows
    to own-tags-only).
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
    if isinstance(node, Tag):
        if journal is None:
            raise ValueError("tag: matching requires journal context")
        if _tag_matches(node, txn.tags):
            return True
        return any(_tag_matches(node, _effective_tags(journal, txn, p)) for p in txn.postings)
    if isinstance(node, And):
        return all(matches_transaction(t, txn, journal) for t in node.terms)
    if isinstance(node, Or):
        return any(matches_transaction(t, txn, journal) for t in node.terms)
    if isinstance(node, Not):
        return not matches_transaction(node.term, txn, journal)
    raise TypeError(f"unhandled query node type: {type(node)!r}")  # pragma: no cover


def _matches_posting_impl(
    node: QueryNode,
    txn: Transaction,
    posting: Posting,
    journal: Journal | None,
    tag_source: _TagSourceFn,
) -> bool:
    """Shared posting-level dispatch for `matches_posting` and the
    `accounts`-mode variant below — identical for every node type except
    Tag, whose effective-tags computation is supplied by `tag_source` so
    both modes share one recursive And/Or/Not walk instead of two parallel
    copies of it."""
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
    if isinstance(node, Tag):
        if journal is None:
            raise ValueError("tag: matching requires journal context")
        return _tag_matches(node, tag_source(journal, txn, posting))
    if isinstance(node, And):
        return all(_matches_posting_impl(t, txn, posting, journal, tag_source) for t in node.terms)
    if isinstance(node, Or):
        return any(_matches_posting_impl(t, txn, posting, journal, tag_source) for t in node.terms)
    if isinstance(node, Not):
        return not _matches_posting_impl(node.term, txn, posting, journal, tag_source)
    raise TypeError(f"unhandled query node type: {type(node)!r}")  # pragma: no cover


def matches_posting(node: QueryNode, txn: Transaction, posting: Posting, journal: Journal | None = None) -> bool:
    """Return True if `posting` (within `txn`) matches `node`.

    Desc/DateSpan/Status are transaction-level facts a posting inherits
    unchanged; Acct/Depth are checked against the posting's own account.

    Tag (Stage C Phase 6) matches against `posting`'s full, four-source
    effective tag set (`ledgerkit.tags._effective_tags`: own tags,
    transaction's own tags, account-inherited tags, and commodity-
    propagated tags — design §2.2/§2.6). Requires `journal` — raises
    ValueError if a Tag node is present and `journal` is None (never
    silently narrows to own-tags-only). See `ledgerkit.reports.accounts`
    for the one command that deliberately uses a narrower effective-tags
    computation instead (design §2.5/§9.2), via its own private dispatch
    rather than this function.
    """
    return _matches_posting_impl(node, txn, posting, journal, _effective_tags)


def _matches_posting_for_accounts(
    node: QueryNode, txn: Transaction, posting: Posting, journal: Journal | None = None
) -> bool:
    """Posting-level matching for the `accounts` command's narrower Tag-
    matching mode (design §2.5/§9.2) — private, used only by
    `ledgerkit.reports.accounts`.

    Identical to `matches_posting` for every node type except Tag, where
    it uses `ledgerkit.tags._accounts_effective_tags` (transaction-own +
    account-inherited only, excluding posting-own and commodity-
    propagated tags) instead of the full `_effective_tags` — replicating
    hledger's own `accounts tag:X` visibility split
    (`journalPostingsKeepAccountTagsOnly` composed with `postingAllTags`).
    Never used by `balance`/`register`/`print`/`stats`, whose behaviour is
    unchanged by this function's existence.
    """
    return _matches_posting_impl(node, txn, posting, journal, _accounts_effective_tags)

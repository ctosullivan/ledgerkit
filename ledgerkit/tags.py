"""Inline comment-tag parsing (hledger `name:value` tags) and
effective-tag computation for `tag:` query matching.

Pure functions only — no file I/O, no Journal/Transaction/Posting
mutation. `parser.py` calls into `parse_tags` after a transaction's/
posting's/account-directive's/commodity-directive's `inline_comment` text
has already been fully assembled (including any follow-on indented
comment lines), and stores the results on the relevant model fields
itself.

Stage C Phase 6 added the account-inheritance/commodity-propagation/
effective-tags helpers below (`_inherited_account_tags`, `_commodity_tags`,
`_effective_tags`, `_accounts_effective_tags`) — all private, per
`dev-docs/planning/core-redefinition/
23-tag-query-matching-design.md` §9.3's resolution (no new public API
surface without a demonstrated external consumer). Unlike hledger's own
mechanism (which mutates `ptags`/`ttags` once at journal-read time —
design §2.6), these remain pure, on-demand computations over `Journal`/
`Transaction`/`Posting` — `Posting.tags`/`Transaction.tags` still hold
only each entity's own literal inline-comment tags, exactly as Stage C
Phase 4 established; nothing here mutates them.

Grounded in `dev-docs/planning/core-redefinition/20-tag-parsing-syntax-
brief.md`, itself derived from hledger 1.52.4's actual extraction grammar
(`hledger-lib/Hledger/Read/Common.hs`'s `commentlinetagsp`/
`commenttagsanddatesp`) — not a line-for-line port of that Haskell parser
combinator (an independent iterative implementation of the same observable
grammar; see the brief's own "directly-translated-material assessment"
and `knowledge/DECISIONS.md`, 2026-09-17).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ledgerkit.models import Journal, Posting, Transaction


def parse_tags(comment: str | None) -> list[tuple[str, str]]:
    """Extract `name:value` tags from already-assembled comment text.

    Processes the comment line by line (a `\\n`-joined multi-line comment,
    exactly what `Transaction.inline_comment`/`Posting.inline_comment`
    already contain, produces identical results to scanning each
    contributing comment line independently — see `20-tag-parsing-syntax-
    brief.md` §6 for why the two are provably equivalent here).

    Grammar (hledger 1.52.4, `commentlinetagsp`):
      - A tag name is the whitespace-delimited token immediately before a
        `:`, with no space between the name and the colon — a space right
        before the colon voids that tag entirely (the text is discarded,
        scanning continues after the colon for a further tag), it does
        not merely produce an empty-string name.
      - Tag names have no character-class restriction beyond "not `:`,
        not a line break, no internal whitespace" — despite the manual's
        prose describing tags as "a single word or hyphenated word," the
        actual parser is more permissive (digits, punctuation, non-ASCII
        are all accepted).
      - `name:` with nothing (or only a trailing comma) after the colon
        is a legal tag with an empty string value.
      - A value runs from just after the colon (leading whitespace
        skipped) to the next `,` or end of line, then has trailing
        whitespace stripped. **A value cannot contain a literal comma**
        — there is no escaping mechanism; hledger documents this as a
        real limitation, not an omission. A colon *can* appear inside a
        value (only `,`/end-of-line terminate it) — e.g. `url:
        http://example.com` is one tag, value `http://example.com`.
      - Multiple tags per line are comma-separated. The same tag name may
        legitimately repeat with different values on one line — the
        result is an ordered list of pairs, never collapsed into a dict.

    Returns:
        An ordered list of (name, value) pairs, in the order they appear.
        Returns [] for None or a comment with no tags.
    """
    if not comment:
        return []
    tags: list[tuple[str, str]] = []
    for line in comment.split("\n"):
        tags.extend(_parse_comment_line_tags(line))
    return tags


def _parse_comment_line_tags(line: str) -> list[tuple[str, str]]:
    tags: list[tuple[str, str]] = []
    pos = 0
    while True:
        colon = line.find(":", pos)
        if colon == -1:
            return tags
        name = _tag_name_before_colon(line[pos:colon])
        if not name:
            # A voided candidate (empty, or ends in whitespace) is not a
            # tag — resume scanning for the next colon right after this
            # one, per commentlinetagsp's own recursive "discard and
            # keep looking" behaviour (not "stop looking on this line").
            pos = colon + 1
            continue
        rest = line[colon + 1:]
        comma = rest.find(",")
        if comma == -1:
            tags.append((name, rest.strip()))
            return tags
        tags.append((name, rest[:comma].strip()))
        pos = colon + 1 + comma + 1


def effective_date(txn: "Transaction", posting: "Posting") -> datetime.date:
    """Return `posting`'s effective primary date within `txn`.

    A posting's own `date:` comment tag (`Posting.date_override`) takes
    precedence over its transaction's date, per hledger's `postingDate`
    (a per-posting override, computed on read — `txn.date` itself is
    never mutated by a posting's tag).
    """
    return posting.date_override if posting.date_override is not None else txn.date


def effective_date2(txn: "Transaction", posting: "Posting") -> datetime.date:
    """Return `posting`'s effective secondary date within `txn`.

    Mirrors hledger's `postingDate2` four-level fallback chain exactly:
    this posting's own `date2:` override, then its transaction's `date2`,
    then this posting's own `date:` override (primary, reused as a
    secondary-date fallback), then its transaction's primary date. A
    posting with only a `date:` override and no `date2:` override, on a
    transaction with no secondary date at all, gets its *primary*
    override reused as its effective *secondary* date too.
    """
    if posting.date2_override is not None:
        return posting.date2_override
    if txn.date2 is not None:
        return txn.date2
    if posting.date_override is not None:
        return posting.date_override
    return txn.date


def _tag_name_before_colon(candidate: str) -> str:
    """Return the tag-name candidate's last whitespace-delimited token.

    Mirrors hledger's `last (T.split isSpace candidate)`, which is NOT
    the same as Python's `str.split()`: if `candidate` is empty or its
    *last character* is whitespace, the name is empty (voided) — Python's
    `.split()` would silently discard trailing whitespace and still
    return the preceding word, which is the wrong behaviour here (e.g.
    "foo :" must void the tag entirely, not produce name "foo").
    """
    if not candidate or candidate[-1].isspace():
        return ""
    parts = candidate.split()
    return parts[-1] if parts else ""


def _inherited_account_tags(journal: "Journal", account: str) -> list[tuple[str, str]]:
    """Return every ancestor account's (and `account`'s own) declared tags.

    Walks `account`'s `:`-separated ancestor chain from the root segment
    down to `account` itself, concatenating each level's
    `Journal.declared_account_tags` entries (own tags first come from the
    least-specific ancestor, most-specific last — order does not affect
    `tag:` matching, a pure membership test, but is kept deterministic).
    Mirrors hledger's `journalInheritedAccountTags`: inherited tags apply
    to the declaring account itself and all of its descendants, not just
    strict descendants (design §2.2 rule A, confirmed live against the
    pinned binary). An account with no declared tags anywhere in its own
    chain (and no ancestor with any) returns [].
    """
    tags: list[tuple[str, str]] = []
    segments = account.split(":")
    for i in range(1, len(segments) + 1):
        prefix = ":".join(segments[:i])
        tags.extend(journal.declared_account_tags.get(prefix, []))
    return tags


def _posting_commodities(posting: "Posting") -> list[str]:
    """Return the commodity symbol(s) used in `posting`'s main amount.

    Ledgerkit's `Posting.amount` is a single `Amount` (one commodity per
    posting — no `MixedAmount` concept), so this is always a 0- or
    1-element list. Named/plural to mirror hledger's own
    `postingCommodities` (design §2.6), which is plural because hledger's
    `Posting` amount CAN reference more than one commodity; kept as its
    own small helper (rather than inlining `[posting.amount.commodity]`)
    so `_effective_tags`/`_accounts_effective_tags` read the same either
    way if Ledgerkit ever grows multi-commodity postings.
    """
    return [posting.amount.commodity] if posting.amount is not None else []


def _commodity_tags(journal: "Journal", commodities: list[str]) -> list[tuple[str, str]]:
    """Return every declared tag for each commodity symbol in `commodities`.

    Looks up `Journal.declared_commodity_tags` for each symbol
    (concatenating results, since a posting's main amount can in principle
    reference more than one commodity — see `_posting_commodities`), per
    hledger's `journalCommodityTags`/`journalPostingsAddCommodityTags`
    (design §2.6, the "commodity tags" feature). A commodity with no
    declared tags contributes nothing.
    """
    tags: list[tuple[str, str]] = []
    for symbol in commodities:
        tags.extend(journal.declared_commodity_tags.get(symbol, []))
    return tags


def _effective_tags(journal: "Journal", txn: "Transaction", posting: "Posting") -> list[tuple[str, str]]:
    """Return the full, four-source union of tags effectively visible on `posting`.

    Plain concatenation of `posting`'s own tags, `txn`'s own tags,
    `posting.account`'s inherited (declared/ancestor) tags, and the
    declared tags of every commodity used in `posting`'s main amount — the
    complete set of sources hledger's `tag:` reads from (design §2.2/§2.6).

    Deliberately **no shadowing/exclusion logic**: a same-named tag with a
    different value from another source is NOT deduplicated away — every
    differently-valued, same-named tag from every source stays
    independently matchable. This is not an oversight; it is the
    design's own executable-verified finding (design §2.7): hledger's
    manual describes "posting tags override account tags override
    commodity tags," but live differential testing against the pinned
    1.52.4 binary shows this is not exclusion for `tag:` query-matching
    purposes — `Data.List.union`'s deduplication in hledger's own
    `postingAddTags` is by the FULL `(name, value)` tuple, so a
    differently-valued same-named tag from another source is never
    dropped. A naive "highest-priority wins" implementation here would be
    wrong, not merely a simplification.
    """
    return (
        posting.tags
        + txn.tags
        + _inherited_account_tags(journal, posting.account)
        + _commodity_tags(journal, _posting_commodities(posting))
    )


def _accounts_effective_tags(journal: "Journal", txn: "Transaction", posting: "Posting") -> list[tuple[str, str]]:
    """Return the narrower tag set hledger's `accounts` command sees (design §2.5/§9.2).

    Unions only `txn`'s own tags and `posting.account`'s inherited tags —
    explicitly excluding `posting`'s own literal comment tags and any
    commodity-propagated tags. Replicates hledger's
    `journalPostingsKeepAccountTagsOnly` (`accounts.hs`'s own
    `keepaccounttags`, which replaces a posting's `ptags` with only its
    account-inherited tags) composed with `postingAllTags`'s unconditional
    `++ ttags` (transaction-level tags are never stripped) — the real,
    source-confirmed, four-way-tested visibility split plain
    `accounts tag:X` shows, distinct from every other command's full
    `_effective_tags`. Used only by `ledgerkit.reports.accounts`'s `Tag`-
    matching path, via `ledgerkit.query.eval`'s accounts-mode dispatch —
    reuses `_inherited_account_tags` directly rather than duplicating its
    ancestor-walk logic.
    """
    return txn.tags + _inherited_account_tags(journal, posting.account)

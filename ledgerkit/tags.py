"""Inline comment-tag parsing (hledger `name:value` tags).

Pure functions only — no file I/O, no Journal/Transaction/Posting
mutation. `parser.py` calls into this module after a transaction's/
posting's/account-directive's `inline_comment` text has already been
fully assembled (including any follow-on indented comment lines), and
stores the results on the relevant model fields itself.

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
    from ledgerkit.models import Posting, Transaction


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

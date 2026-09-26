"""`ledgerkit.models.Query` -> `ledgerkit.query.ast.QueryNode` translation.

Stage C Phase 8 (`dev-docs/planning/core-redefinition/
27-query-shim-convergence-design.md`): `Query` is a frozen-shape
"compatibility constructor" (`07-query-regex.md` §7.2) — its dataclass
fields never change — but its *matching behaviour* used to be implemented
by `reports.py`'s own ad hoc, non-hledger-faithful `_posting_matches`/
`_matches_pattern` helpers, a second, parallel filtering path alongside
the real `ledgerkit.query` AST/parser/evaluator. This module is the
translator that ends that duplication: every `Query`-shaped filter in
`ledgerkit/` (see `dev-docs/architecture.md`'s "one canonical evaluation
path" description) now compiles to the same `QueryNode` tree `-q`/
`--query` string terms produce, and is evaluated by the same
`ledgerkit.query.eval` engine.

**Module placement is deliberate.** This lives inside the `query` package
(not `ledgerkit/models.py`) because `ledgerkit/query/eval.py` already
imports `from ledgerkit.models import Journal, Posting, Transaction` — a
top-level import of this module's dependencies (`ledgerkit.query.ast`/
`ledgerkit.query.regex`/`ledgerkit.query.parser`) from `models.py` would
create a genuine circular import. Nothing in `ledgerkit/query/` needs to
import `compat.py` itself, so this module importing freely from the rest
of `ledgerkit/query/` is safe. `ledgerkit/models.py`'s `Journal.balance`/
`.register`/`.to_dataframe` and `ledgerkit/reports.py` reach this module
via a lazy, in-function import — the same pattern `models.py` already
uses to reach `reports.py` itself (see the comment at the top of
`Journal`'s report methods).

`Query` itself is referenced only for a type hint here (`TYPE_CHECKING`),
never at runtime — this function only ever does attribute access on
whatever it's given, so no runtime import of `ledgerkit.models` is needed
at all.
"""

from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

from ledgerkit.query.ast import Acct, And, DateSpan, Desc, Not, QueryNode
from ledgerkit.query.parser import QueryParseError
from ledgerkit.query.regex import compile_hledger_regex

if TYPE_CHECKING:
    from ledgerkit.models import Query


def _validated(prefix: str, pattern: str) -> str:
    """Validate `pattern` eagerly, raising QueryParseError (not a bare
    ValueError/re.error) on failure.

    Mirrors `ledgerkit.query.parser._build_acct`/`_build_desc`'s own
    parse-time-validation contract: a bad pattern must fail here,
    deterministically, at translation time -- not lazily, only if and
    when `ledgerkit.query.eval`'s own lazily-cached compilation happens to
    be exercised during evaluation (which, for an empty journal or an
    unreached predicate, might never happen at all). `prefix` names the
    field being validated (e.g. "account", "not_account", "payee") purely
    for the error message -- it plays no role in validation itself.

    Reuses `QueryParseError` (already public, already the exception every
    `-q` string-term validation failure raises) rather than a new,
    Query-specific exception type -- an explicit, approved decision (see
    knowledge/DECISIONS.md), mirroring Stage C Phase 7's own reuse of
    `UnsupportedRegexConstructError` for the same kind of condition.
    """
    try:
        compile_hledger_regex(pattern)
    except (ValueError, re.error) as exc:
        raise QueryParseError(f"{prefix}: {exc}") from exc
    return pattern


def _exclusive_end(date_to: datetime.date | None) -> datetime.date | None:
    """Translate `Query.date_to` (inclusive) into `DateSpan.end` (exclusive).

    `Query.date_to` is inclusive; `DateSpan.end` is exclusive (see
    `ledgerkit.query.ast.DateSpan` and `knowledge/DOMAIN_RULES.md`).
    Adding one day makes the translation faithful for every ordinary
    date -- except `datetime.date.max` (`9999-12-31`), which has no
    representable successor and would overflow. `date.max` as an
    inclusive upper bound already means "no upper bound in practice"
    (nothing sorts after it), so it maps to `DateSpan`'s own "unbounded"
    representation (`end=None`) instead of raising `OverflowError`.
    """
    if date_to is None:
        return None
    if date_to == datetime.date.max:
        return None
    return date_to + datetime.timedelta(days=1)


def _query_to_ast(query: "Query | None") -> QueryNode | None:
    """Translate a `Query` into the equivalent `QueryNode` predicate tree.

    Returns `None` for `query=None` or a `Query()` with every field
    `None` -- both mean "no filter," consistent with every other
    `Query`-accepting function in `ledgerkit/`. Every `Acct`/`Desc`/
    `DateSpan` node constructed here is built only from an
    already-validated pattern (`_validated`) -- AST node dataclasses do
    not validate themselves (see `ledgerkit/query/ast.py`), so a `Query`
    field now fails exactly as loudly and exactly as early as the
    equivalent `-q` string term would.

    `query.depth` is deliberately never consulted here -- `depth` is
    never a selection predicate in hledger (see
    `knowledge/DOMAIN_RULES.md`'s `depth:` entry); callers read
    `query.depth` directly via `reports._effective_depth_spec` instead.
    """
    if query is None:
        return None
    terms: list[QueryNode] = []
    if query.account is not None:
        terms.append(Acct(_validated("account", query.account)))
    if query.not_account is not None:
        terms.append(Not(Acct(_validated("not_account", query.not_account))))
    if query.payee is not None:
        terms.append(Desc(_validated("payee", query.payee)))
    if query.date_from is not None or query.date_to is not None:
        terms.append(DateSpan(start=query.date_from, end=_exclusive_end(query.date_to)))
    if not terms:
        return None
    return terms[0] if len(terms) == 1 else And(tuple(terms))
    # query.depth is deliberately excluded -- never a predicate (see above).

"""Report generators for ledgerkit.

Each function accepts a Journal and returns structured data — not formatted
strings. Formatting is handled by cli.py.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator

from ledgerkit.models import (
    BalanceRow,
    Journal,
    Posting,
    Query,
    RegisterRow,
    ReportSection,
    ReportSpec,
    ReportSectionResult,
    Transaction,
)
from ledgerkit.parser import resolve_elision
from ledgerkit.query.ast import QueryNode
from ledgerkit.query.depth import DepthSpec, account_excluded_by_depth, clip_account_name
from ledgerkit.query.eval import matches_posting as _query_ast_matches_posting
from ledgerkit.query.eval import matches_transaction as _query_ast_matches_transaction
from ledgerkit.query.eval import _matches_posting_for_accounts as _query_ast_matches_posting_accounts_mode
from ledgerkit.query.regex import compile_hledger_regex


# ---------------------------------------------------------------------------
# Transparent result wrappers with to_dataframe() support
# ---------------------------------------------------------------------------

class BalanceResult(Mapping):
    """Return type of Journal.balance() (flat mode). Behaves like dict[str, dict[str, Decimal]]."""

    def __init__(self, data: dict, commodity_styles: dict) -> None:
        self._data = data
        self._commodity_styles = commodity_styles

    def __getitem__(self, key: str) -> dict:
        return self._data[key]

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BalanceResult):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self._data)

    def to_dataframe(self):
        """Export balance to a DataFrame with account, amount, commodity, amount_formatted.

        One row per (account, commodity) pair (non-zero amounts only).
        Requires pandas: pip install ledgerkit[pandas]
        """
        from ledgerkit._pandas_compat import require_pandas
        pd = require_pandas()
        rows = []
        for account in sorted(self._data):
            for commodity, qty in sorted(self._data[account].items()):
                if qty == 0:
                    continue
                style = self._commodity_styles.get(commodity)
                from ledgerkit.commodity_style import CommodityStyle
                formatted = style.format(qty) if style else str(qty)
                rows.append({
                    "account": account,
                    "amount": qty,
                    "commodity": commodity,
                    "amount_formatted": formatted,
                })
        df = pd.DataFrame(rows, columns=["account", "amount", "commodity", "amount_formatted"])
        if not df.empty:
            df["amount"] = df["amount"].astype(object)
        return df


class RegisterResult(Sequence):
    """Return type of Journal.register(). Behaves like list[RegisterRow]."""

    def __init__(self, data: list, commodity_styles: dict) -> None:
        self._data = data
        self._commodity_styles = commodity_styles

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RegisterResult):
            return self._data == other._data
        if isinstance(other, list):
            return self._data == other
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self._data)

    def to_dataframe(self):
        """Export register rows to a DataFrame.

        Columns: date, description, cleared, pending, account,
                 amount (Decimal), commodity, amount_formatted.
        Requires pandas: pip install ledgerkit[pandas]
        """
        from ledgerkit._pandas_compat import require_pandas
        pd = require_pandas()
        rows = []
        for row in self._data:
            commodity = row.amount.commodity
            style = self._commodity_styles.get(commodity)
            formatted = style.format(row.amount.quantity) if style else str(row.amount.quantity)
            rows.append({
                "date": row.date,
                "description": row.description,
                "cleared": False,
                "pending": False,
                "account": row.account,
                "amount": row.amount.quantity,
                "commodity": commodity,
                "amount_formatted": formatted,
            })
        df = pd.DataFrame(rows, columns=[
            "date", "description", "cleared", "pending", "account",
            "amount", "commodity", "amount_formatted",
        ])
        if not df.empty:
            df["amount"] = df["amount"].astype(object)
        return df


class AccountsResult(Sequence):
    """Return type of Journal.accounts(). Behaves like list[str]."""

    def __init__(self, data: list) -> None:
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AccountsResult):
            return self._data == other._data
        if isinstance(other, list):
            return self._data == other
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self._data)

    def to_dataframe(self):
        """Export account names to a single-column DataFrame.

        Requires pandas: pip install ledgerkit[pandas]
        """
        from ledgerkit._pandas_compat import require_pandas
        pd = require_pandas()
        return pd.DataFrame({"account": self._data})


@dataclass
class JournalStats:
    """Summary statistics for a journal.

    Contains only deterministic journal data. Runtime stats (elapsed time,
    txns/s) are measured and formatted by the CLI layer, not stored here.
    """

    source_file: str | None
    included_files: int
    transaction_count: int
    date_range: tuple[datetime.date, datetime.date] | None  # (first, last)
    last_txn_date: datetime.date | None
    last_txn_days_ago: int | None  # (today - last_txn_date).days
    txns_span_days: int | None  # (last - first).days + 1
    txns_per_day: float  # transaction_count / txns_span_days, else 0.0
    txns_last_30_days: int
    txns_per_day_last_30: float
    txns_last_7_days: int
    txns_per_day_last_7: float
    payee_count: int  # unique descriptions
    account_count: int
    account_depth: int  # max colon-segment depth across all accounts
    commodity_count: int
    commodities: list[str]  # sorted commodity symbols (shown in verbose mode)
    price_count: int  # len(journal.prices)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _matches_pattern(pattern: str, value: str) -> bool:
    """Return True if pattern matches value using hledger's HledgerRegex rules.

    Stage C Phase 8: previously an ad hoc, Python-native heuristic (any
    Python regex metacharacter switched into raw `re.search` mode, no
    HledgerRegex-subset validation at all — a second, non-hledger-faithful
    regex dialect living alongside the real one in `ledgerkit.query.regex`).
    Now always compiles `pattern` via `ledgerkit.query.regex.
    compile_hledger_regex` (case-insensitive, infix `.search()`) — the same
    dialect and validation `acct:`/`desc:` query terms already use. This
    is behaviour-preserving for every pattern that was already
    HledgerRegex-portable (a plain string compiles to a regex matching
    exactly the same characters a case-insensitive substring check would),
    and now raises `UnsupportedRegexConstructError` for an excluded
    construct or an empty pattern, where it previously matched via raw
    Python `re` semantics (excluded construct) or matched everything
    (empty pattern).

    This function's only remaining callers are `ReportSection.accounts`/
    `.exclude` (`balance_from_spec`) — the one deliberately separate
    matching construct left in `ledgerkit/` after Stage C Phase 8's
    convergence; every other `Query`-shaped filter now reaches
    `ledgerkit.query.eval.matches_posting`/`matches_transaction` via
    `ledgerkit.query.compat._query_to_ast` instead (see
    `dev-docs/architecture.md`).
    """
    return bool(compile_hledger_regex(pattern).search(value))


def _effective_depth_spec(query: Query | None, _query_depth: DepthSpec | None) -> DepthSpec:
    """Resolve the DepthSpec a report function should clip display names to.

    `_query_depth` (from the CLI's `-q`/`--query` string, via
    `ledgerkit.query.parser.parse`) takes precedence when supplied and
    non-empty — it is the richer, more recent mechanism. Otherwise falls
    back to the legacy `query.depth` (a flat int only; wrapped as
    `DepthSpec(flat=query.depth)`). Both are Ledgerkit-internal report
    options, never a selection filter — see
    `ledgerkit.query.compat._query_to_ast`, which never routes `query.depth`
    into the predicate tree at all.
    """
    if _query_depth is not None and not _query_depth.is_empty():
        return _query_depth
    if query is not None and query.depth is not None:
        return DepthSpec(flat=query.depth)
    return DepthSpec()


def _aggregate_posting_amounts(
    pairs: list[tuple[str, Decimal]],
) -> dict[str, Decimal]:
    """Sum (account_name, quantity) pairs into an account → balance dict."""
    result: dict[str, Decimal] = {}
    for account, qty in pairs:
        result[account] = result.get(account, Decimal(0)) + qty
    return result


def _build_balance_tree(
    totals: dict[str, dict[str, Decimal]],
) -> list[BalanceRow]:
    """Convert a flat account→commodity→net dict into a sorted tree row list.

    Collects all implicit parent accounts (all colon-prefixes of every account
    name in `totals`), computes aggregate amounts (own postings + all
    descendants) for each, and returns a list of BalanceRow sorted
    alphabetically by account name.

    is_subtotal is True for accounts not present in `totals` directly (pure
    intermediate parents with no direct postings of their own).
    """
    all_accounts: set[str] = set(totals.keys())
    for account in list(totals.keys()):
        parts = account.split(":")
        for i in range(1, len(parts)):
            all_accounts.add(":".join(parts[:i]))

    rows: list[BalanceRow] = []
    for account in sorted(all_accounts):
        prefix = account + ":"
        agg: dict[str, Decimal] = {}
        for src, amounts in totals.items():
            if src == account or src.startswith(prefix):
                for commodity, qty in amounts.items():
                    agg[commodity] = agg.get(commodity, Decimal(0)) + qty
        rows.append(BalanceRow(
            account=account,
            depth=account.count(":"),
            amounts=agg,
            is_subtotal=(account not in totals),
        ))
    return rows


# ---------------------------------------------------------------------------
# Report functions
# ---------------------------------------------------------------------------

def accounts(
    journal: Journal,
    query: Query | None = None,
    _query_ast: QueryNode | None = None,
    _query_depth: DepthSpec | None = None,
) -> list[str]:
    """Return a sorted list of all unique account names in the journal.

    Args:
        journal: The parsed journal.
        query: Optional filter. When None or Query(), all accounts are returned.
        _query_ast: Private, internal-only filter (a ledgerkit.query.QueryNode)
            used by the CLI's -q/--query flag. Not part of the stable public
            API — see knowledge/DECISIONS.md, 2026-09-16 ("Stage C Phase 2's
            query/report integration is internal-only this phase"). AND'd
            with `query` when both are supplied. A `Tag` node is matched
            using this command's own narrower effective-tags visibility
            (Stage C Phase 6, design §2.5/§9.2) — transaction-own and
            account-inherited tags only, excluding posting-own and
            commodity-propagated tags — replicating hledger's own
            `accounts tag:X`, which is NOT the same tag visibility every
            other report function here uses.
        _query_depth: Private, internal-only (a ledgerkit.query.depth.DepthSpec)
            from the CLI's -q/--query flag's depth: term(s), added Stage C
            Phase 5. See `_effective_depth_spec` for precedence against the
            legacy `query.depth`.

    Returns:
        Sorted list of account name strings that appear in at least one
        matching posting, clipped/deduplicated per the effective DepthSpec
        (matching hledger's own `accounts --depth`/`depth:` — clipping and
        merging, never excluding — dev-docs/planning/core-redefinition/
        21-stage-c-phase-5-depth-and-verification-plan.md §1.3).
    """
    from ledgerkit.query.compat import _query_to_ast

    depth_spec = _effective_depth_spec(query, _query_depth)
    _outer_ast = _query_to_ast(query)
    seen: set[str] = set()
    for txn in journal.transactions:
        for posting in txn.postings:
            if _outer_ast is not None and not _query_ast_matches_posting(
                _outer_ast, txn, posting, journal=journal
            ):
                continue
            # accounts uses its own narrower Tag-matching mode (design
            # §2.5/§9.2) — transaction-own + account-inherited tags only,
            # excluding posting-own and commodity-propagated tags — rather
            # than the ordinary matches_posting every other report function
            # here uses. Every other node type behaves identically either
            # way; see _matches_posting_for_accounts's own docstring. (Only
            # relevant to `_query_ast`, the CLI's own -q flag: `query`/
            # `_outer_ast` never contain a Tag node — Query has no tag field.)
            if _query_ast is not None and not _query_ast_matches_posting_accounts_mode(
                _query_ast, txn, posting, journal=journal
            ):
                continue
            seen.add(clip_account_name(depth_spec, posting.account))
    return AccountsResult(sorted(seen))


def balance(
    journal: Journal,
    query: Query | None = None,
    tree: bool = False,
    _query_ast: QueryNode | None = None,
    _query_depth: DepthSpec | None = None,
) -> dict[str, dict[str, Decimal]] | list[BalanceRow]:
    """Return per-commodity net balances for each account.

    Args:
        journal: The parsed journal.
        query: Optional filter. When None or Query(), all postings are included.
        tree: When True, returns list[BalanceRow] with implicit parent accounts
              and aggregate subtotals. When False (default), returns a flat
              dict[str, dict[str, Decimal]] mapping account name to a
              commodity→net dict.
        _query_ast: Private, internal-only filter (a ledgerkit.query.QueryNode)
            used by the CLI's -q/--query flag. Not part of the stable public
            API — see knowledge/DECISIONS.md, 2026-09-16. AND'd with `query`
            (translated via `ledgerkit.query.compat._query_to_ast`, Stage C
            Phase 8) when both are supplied. Never carries depth — depth is
            never a selection predicate (see `_effective_depth_spec`). A
            `Tag` node is matched against each posting's full, four-source
            effective tag set (Stage C Phase 6 — see
            `ledgerkit.tags._effective_tags`).
        _query_depth: Private, internal-only (a ledgerkit.query.depth.DepthSpec)
            from the CLI's -q/--query flag's depth: term(s), added Stage C
            Phase 5. See `_effective_depth_spec` for precedence against the
            legacy `query.depth`.

    Returns:
        When tree=False: dict mapping account name to {commodity: net_balance}.
        When tree=True: list[BalanceRow] sorted alphabetically, including
        implicit parent accounts with is_subtotal=True.

    Note on depth: depth causes account names to be *clipped and aggregated*
    (rolled up) rather than excluded — matching hledger's --depth/depth:
    behaviour, including custom REGEX=N depths via `_query_depth`.
    expenses:food:groceries at depth=2 contributes to expenses:food.
    """
    from ledgerkit.query.compat import _query_to_ast

    depth_spec = _effective_depth_spec(query, _query_depth)
    _outer_ast = _query_to_ast(query)
    totals: dict[str, dict[str, Decimal]] = {}
    for txn in journal.transactions:
        for posting in resolve_elision(txn):
            if _outer_ast is not None and not _query_ast_matches_posting(_outer_ast, txn, posting, journal=journal):
                continue
            if _query_ast is not None and not _query_ast_matches_posting(_query_ast, txn, posting, journal=journal):
                continue
            if posting.amount is None:
                continue
            account = clip_account_name(depth_spec, posting.account)
            commodity = posting.amount.commodity
            if account not in totals:
                totals[account] = {}
            totals[account][commodity] = (
                totals[account].get(commodity, Decimal(0)) + posting.amount.quantity
            )
    if tree:
        return _build_balance_tree(totals)
    return BalanceResult(totals, journal.commodity_styles)


def register(
    journal: Journal,
    query: Query | None = None,
    _query_ast: QueryNode | None = None,
    _query_depth: DepthSpec | None = None,
) -> list[RegisterRow]:
    """Return a chronological list of register rows.

    Args:
        journal: The parsed journal.
        query: Optional filter. When None or Query(), all postings are included.
        _query_ast: Private, internal-only filter (a ledgerkit.query.QueryNode)
            used by the CLI's -q/--query flag. Not part of the stable public
            API — see knowledge/DECISIONS.md, 2026-09-16. AND'd with `query`
            when both are supplied. A `Tag` node is matched against each
            posting's full, four-source effective tag set (Stage C Phase 6
            — see `ledgerkit.tags._effective_tags`).
        _query_depth: Private, internal-only (a ledgerkit.query.depth.DepthSpec)
            from the CLI's -q/--query flag's depth: term(s), added Stage C
            Phase 5. See `_effective_depth_spec` for precedence against the
            legacy `query.depth`.

    Returns:
        List of RegisterRow objects in journal order. running_balance is the
        cumulative sum of amount.quantity across all rows in output order —
        never grouped/aggregated by account, even when depth clips several
        postings' displayed account names to the same string (matching
        hledger's own `register --depth`: every posting stays its own row,
        only its displayed account name is clipped). No posting is ever
        excluded on account of `query.depth`/`_query_depth` — fixed Stage C
        Phase 5; previously this function (unlike `balance`) applied depth
        as an exclusion filter, a real pre-existing bug distinct from the
        `-q` `depth:` divergence.
    """
    from ledgerkit.query.compat import _query_to_ast

    depth_spec = _effective_depth_spec(query, _query_depth)
    _outer_ast = _query_to_ast(query)
    rows: list[RegisterRow] = []
    running: Decimal = Decimal(0)
    for txn in sorted(journal.transactions, key=lambda t: t.date):
        for posting in resolve_elision(txn):
            if _outer_ast is not None and not _query_ast_matches_posting(_outer_ast, txn, posting, journal=journal):
                continue
            if _query_ast is not None and not _query_ast_matches_posting(_query_ast, txn, posting, journal=journal):
                continue
            if posting.amount is None:
                continue
            running += posting.amount.quantity
            rows.append(RegisterRow(
                date=txn.date,
                description=txn.description,
                account=clip_account_name(depth_spec, posting.account),
                amount=posting.amount,
                running_balance=running,
            ))
    return RegisterResult(rows, journal.commodity_styles)


def stats(
    journal: Journal,
    query: Query | None = None,
    _query_ast: QueryNode | None = None,
    _query_depth: DepthSpec | None = None,
) -> JournalStats:
    """Return summary statistics for the journal.

    Args:
        journal: The parsed journal.
        query: Optional filter. When None or Query(), behaviour is identical to
               the original implementation (all transactions). When any field
               is set, statistics are computed over the matching transaction
               subset — since Stage C Phase 8, this includes `account`/
               `not_account` (see the behaviour-change note below), not only
               `date_from`/`date_to`/`payee` as before.
        _query_ast: Private, internal-only filter (a ledgerkit.query.QueryNode)
            used by the CLI's -q/--query flag. Not part of the stable public
            API — see knowledge/DECISIONS.md, 2026-09-16. Applied via
            ledgerkit.query.eval.matches_transaction (stats is transaction-
            oriented — it filters the transaction list, not individual
            postings, matching its own existing query= filtering above).
            AND'd with `query` (translated via
            `ledgerkit.query.compat._query_to_ast`, Stage C Phase 8) when
            both are supplied. A `Tag` node matches if the transaction's own
            tags directly match, or any of its postings' full effective tags
            match (Stage C Phase 6, design §6).
        _query_depth: Private, internal-only (a ledgerkit.query.depth.DepthSpec)
            from the CLI's -q/--query flag's depth: term(s), added Stage C
            Phase 5. Applied via
            `ledgerkit.query.depth.account_excluded_by_depth`, NOT
            `clip_account_name` — stats is a genuine, source-confirmed
            exception where hledger EXCLUDES accounts deeper than the
            limit for this field rather than clipping them, unlike every
            other depth-aware report function here; see that function's
            own docstring for the full evidence.

    Behaviour change (Stage C Phase 8, intentional and disclosed — see
    `dev-docs/planning/core-redefinition/
    27-query-shim-convergence-design.md` §5.1c): `query.account`/
    `.not_account` were previously silently ignored by `account_count`/
    `account_depth` (a pre-existing, documented gap). Full convergence onto
    `ledgerkit.query.compat._query_to_ast` closes this gap: `stats(query=
    Query(account=X))` now excludes transactions with no posting matching
    `X` from those two fields, matching what `-q "acct:X" stats` (via
    `_query_ast`) already did before this phase.
    """
    from ledgerkit.query.compat import _query_to_ast

    today = datetime.date.today()
    txns = journal.transactions

    # Apply the outer query's full predicate (date/payee/account/not_account)
    # via the canonical query engine — Stage C Phase 8; previously this only
    # checked date_from/date_to/payee inline, silently ignoring account/
    # not_account (see the behaviour-change note above).
    _outer_ast = _query_to_ast(query)
    if _outer_ast is not None:
        txns = [t for t in txns if _query_ast_matches_transaction(_outer_ast, t, journal=journal)]
    if _query_ast is not None:
        txns = [t for t in txns if _query_ast_matches_transaction(_query_ast, t, journal=journal)]

    depth_spec = _effective_depth_spec(query, _query_depth)
    all_accounts: set[str] = {
        p.account for t in txns for p in t.postings
        if not account_excluded_by_depth(depth_spec, p.account)
    }
    all_commodities: set[str] = {
        p.amount.commodity for t in txns for p in t.postings if p.amount is not None
    }
    dates = [t.date for t in txns]
    date_range = (min(dates), max(dates)) if dates else None
    last_txn_date = max(dates) if dates else None
    span_days = (date_range[1] - date_range[0]).days + 1 if date_range else None

    cutoff_30 = today - datetime.timedelta(days=30)
    cutoff_7 = today - datetime.timedelta(days=7)
    txns_30 = sum(1 for t in txns if t.date >= cutoff_30)
    txns_7 = sum(1 for t in txns if t.date >= cutoff_7)

    depth = max((len(a.split(":")) for a in all_accounts), default=0)

    return JournalStats(
        source_file=journal.source_file,
        included_files=journal.included_files,
        transaction_count=len(txns),
        date_range=date_range,
        last_txn_date=last_txn_date,
        last_txn_days_ago=(today - last_txn_date).days if last_txn_date else None,
        txns_span_days=span_days,
        txns_per_day=len(txns) / span_days if span_days else 0.0,
        txns_last_30_days=txns_30,
        txns_per_day_last_30=txns_30 / 30,
        txns_last_7_days=txns_7,
        txns_per_day_last_7=txns_7 / 7,
        payee_count=len({t.description for t in txns}),
        account_count=len(all_accounts),
        account_depth=depth,
        commodity_count=len(all_commodities),
        commodities=sorted(all_commodities),
        price_count=len(journal.prices),
    )


def balance_from_spec(
    journal: Journal,
    spec: ReportSpec,
    query: Query | None = None,
) -> list[ReportSectionResult]:
    """Compute a structured balance report driven by a ReportSpec.

    For each section in spec.sections:
      1. Apply the outer query (date/payee/account/not_account) via the
         canonical query engine (`ledgerkit.query.compat._query_to_ast` +
         `ledgerkit.query.eval.matches_posting`) at posting level.
      2. Include postings whose account matches any of section.accounts (OR logic).
      3. Exclude postings whose account matches any of section.exclude.
      4. Apply depth truncation: section.depth overrides query.depth.
      5. Aggregate using _aggregate_posting_amounts (shared with balance()).
      6. Apply sign inversion if section.invert is True.
      7. Return a ReportSectionResult per section.

    The outer query acts as a uniform filter across all sections — Stage C
    Phase 8 converges its `account`/`not_account`/`payee`/date fields onto
    the same canonical engine `balance`/`register`/`accounts`/`stats` use
    (previously this was its own separate, `_matches_pattern`-based inline
    check). Section-level account patterns are OR-combined within each
    section, still via `_matches_pattern` — the one construct with no
    `Query` equivalent, deliberately kept separate (see
    `dev-docs/planning/core-redefinition/
    27-query-shim-convergence-design.md` §5.1b).

    Args:
        journal: The parsed journal.
        spec: The report layout definition.
        query: Optional uniform filter (date range, payee, account,
               not_account). Applied across all sections before
               section-level account matching.

    Returns:
        One ReportSectionResult per section in spec.sections order.
    """
    from ledgerkit.query.compat import _query_to_ast

    results: list[ReportSectionResult] = []
    commodity_styles = journal.commodity_styles
    _outer_ast = _query_to_ast(query)

    for section in spec.sections:
        pairs: list[tuple[str, Decimal]] = []

        for txn in journal.transactions:
            for posting in resolve_elision(txn):
                # Outer query: translated once above, evaluated per posting
                # through the canonical engine (Stage C Phase 8) — same
                # HledgerRegex-strictness/eager-validation guarantee every
                # other converged consumer gets. (A minor, harmless
                # performance difference from the old per-transaction date
                # short-circuit: the date predicate is now re-checked per
                # posting instead of once per transaction — not a behaviour
                # change.)
                if _outer_ast is not None and not _query_ast_matches_posting(
                    _outer_ast, txn, posting, journal=journal
                ):
                    continue

                # Section account patterns: OR logic — posting must match at least one.
                if not any(_matches_pattern(pat, posting.account) for pat in section.accounts):
                    continue

                # Section exclude patterns: posting must not match any.
                if any(_matches_pattern(pat, posting.account) for pat in section.exclude):
                    continue

                if posting.amount is None:
                    continue

                # Depth: section.depth overrides query.depth.
                depth = section.depth if section.depth is not None else (
                    query.depth if query is not None else None
                )
                account = posting.account
                if depth is not None:
                    account = ":".join(account.split(":")[:depth])

                pairs.append((account, posting.amount.quantity))

        rows = _aggregate_posting_amounts(pairs)

        if section.invert:
            rows = {k: -v for k, v in rows.items()}

        subtotal = sum(rows.values(), Decimal(0))
        results.append(ReportSectionResult(
            section=section,
            rows=rows,
            subtotal=subtotal,
            _commodity_styles=commodity_styles,
        ))

    return results

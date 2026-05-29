"""Core data models for ledgerkit.

Defines the canonical Python data structures for journal entries.
No parsing or reporting logic lives here.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ledgerkit.reports import JournalStats


@dataclass
class Amount:
    """A numeric quantity paired with a commodity symbol.

    Examples:
        Amount(Decimal("30.00"), "£")
        Amount(Decimal("1500.00"), "EUR")
    """

    quantity: Decimal
    commodity: str
    raw: Optional[str] = field(default=None, repr=False, compare=False)

    def display(self, style: object) -> str:
        """Format this amount using the provided CommodityStyle."""
        return style.format(self.quantity)  # type: ignore[attr-defined]


@dataclass
class BalanceAssertion:
    """A balance assertion attached to a posting line.

    Corresponds to the hledger syntax variants:
      =   single-commodity, subaccount-exclusive
      ==  sole-commodity, subaccount-exclusive
      =*  single-commodity, subaccount-inclusive
      ==* sole-commodity, subaccount-inclusive
    """

    amount: Amount
    inclusive: bool = False       # True for =* and ==*
    sole_commodity: bool = False  # True for == and ==*


@dataclass
class SourceSpan:
    """Source location of a parsed transaction block.

    Stores the file path and inclusive line range so that editor tools can
    locate, update, or delete a transaction in the original source file.
    """

    file: str        # absolute path, "(string)", or "(stdin)"
    start_line: int  # 1-indexed, inclusive — the transaction header line
    end_line: int    # 1-indexed, inclusive — last posting/comment line in block


@dataclass
class Posting:
    """One line within a transaction: an account name and an optional amount.

    When `amount` is None the amount is inferred from the other postings
    in the same transaction (hledger elided-amount syntax).
    """

    account: str
    amount: Amount | None = None
    balance_assertion: BalanceAssertion | None = field(default=None)
    source_line: int | None = field(default=None, repr=False)
    inferred: bool = field(default=False, repr=False)
    inline_comment: str | None = field(default=None, repr=False, compare=False)


@dataclass
class Transaction:
    """A complete journal transaction entry."""

    date: datetime.date
    description: str
    postings: list[Posting] = field(default_factory=list)
    cleared: bool = False    # True when marked with "*"
    pending: bool = False    # True when marked with "!"
    code: str = ""           # Optional code in parentheses before description
    comment: str = ""        # Inline or trailing comment text (kept for backward compat)
    source_line: int | None = field(default=None, repr=False)
    source_span: SourceSpan | None = field(default=None, repr=False, compare=False)
    raw_text: str | None = field(default=None, repr=False, compare=False)
    inline_comment: str | None = field(default=None, repr=False, compare=False)


@dataclass
class PriceDirective:
    """A P directive declaring a commodity market price on a given date.

    Example journal line: P 2024-03-01 AAPL $179.00
    Stored in Journal.prices for use by valuation reports.
    """

    date: datetime.date
    commodity: str           # The commodity being priced (e.g. "AAPL", "EUR")
    price: Amount            # The price expressed as an Amount (quantity + currency)


@dataclass
class Query:
    """Filter criteria for report functions.

    All fields are optional and default to None. A Query where every field is
    None is semantically equivalent to "no filter" — passing query=None and
    passing Query() produce identical results in every report function.

    The `account`, `not_account`, and `payee` fields follow hledger's matching
    convention: strings containing regex metacharacters are treated as regex
    patterns (re.search, case-insensitive); all others are plain substring
    matches (case-insensitive).
    """

    account:     str | None = None           # substring or regex; matches posting account names
    not_account: str | None = None           # exclusion filter on account names
    payee:       str | None = None           # substring or regex; matches transaction description
    date_from:   datetime.date | None = None  # inclusive lower bound
    date_to:     datetime.date | None = None  # inclusive upper bound
    depth:       int | None = None           # max account tree depth (colon-segment count)


@dataclass
class RegisterRow:
    """One row in a register report.

    Represents a single matching posting, with the cumulative running balance
    up to and including this row.
    """

    date:            datetime.date
    description:     str
    account:         str
    amount:          Amount
    running_balance: Decimal


@dataclass
class BalanceRow:
    """One row in a tree-mode balance report.

    Attributes:
        account: Full colon-separated account name.
        depth: Number of ':' separators (0 = single root segment).
        amounts: Mapping of commodity symbol to net balance (own postings +
                 all descendants).
        is_subtotal: True when this account has no direct postings and exists
                     only as an implicit parent aggregating its descendants.
    """

    account: str
    depth: int
    amounts: dict[str, Decimal]
    is_subtotal: bool


# ---------------------------------------------------------------------------
# Report specification types
#
# Query answers "which transactions/postings to include" — a filter applied
# uniformly across a report.
#
# ReportSpec answers "how should the included data be structured and labelled"
# — it groups accounts into named sections, controls sign presentation, and
# overrides display labels.
#
# The two compose cleanly: a Query sets a date range; a ReportSpec controls
# the layout. Neither knows about the other.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReportSection:
    """One named section within a ReportSpec.

    Accounts are matched using the same hledger substring/regex rules as
    Query.account. Multiple patterns in `accounts` are OR-combined.
    Patterns in `exclude` are applied as a final subtraction.

    The `invert` flag negates all amounts in this section after aggregation,
    used to display income accounts (which carry negative balances in
    double-entry accounting) as positive numbers.
    """

    name:     str                     # display name, e.g. "Fixed Expenses"
    accounts: tuple[str, ...]         # account patterns to include (OR logic)
    exclude:  tuple[str, ...] = ()    # account patterns to exclude
    label:    str | None = None       # override for subtotal line; defaults to f"Total {name}"
    depth:    int | None = None       # depth cap for this section; overrides outer Query depth
    invert:   bool = False            # negate all amounts (use for income sections)


@dataclass(frozen=True)
class ReportSpec:
    """A structured report definition composed of named sections.

    Library callers construct specs directly:

        spec = ReportSpec(
            name="Income Statement",
            sections=(
                ReportSection("Income",   accounts=("income",),   invert=True),
                ReportSection("Expenses", accounts=("expenses",)),
            ),
        )

    Journal-comment-based spec parsing (the "; report" / "; end report" syntax)
    is deferred to Milestone 3.
    """

    name:           str                        # e.g. "Monthly Budget View"
    sections:       tuple[ReportSection, ...]
    show_subtotals: bool = True                # render a subtotal row per section
    show_total:     bool = True                # render a grand total row
    total_label:    str = "Net"                # label for the grand total row


@dataclass
class ReportSectionResult:
    """The computed output of a single ReportSection."""

    section:  ReportSection
    rows:     dict[str, Decimal]  # account name → net balance (after invert)
    subtotal: Decimal             # sum of all values in rows (after invert)
    _commodity_styles: dict = field(default_factory=dict, repr=False)

    def to_dataframe(self):
        """Export this section to a pandas DataFrame.

        Columns: account, amount (Decimal), commodity (str), amount_formatted.
        Includes a final 'Total {section.name}' row with the section subtotal.
        Requires pandas: pip install ledgerkit[pandas]
        """
        from ledgerkit._pandas_compat import require_pandas
        pd = require_pandas()
        # Infer the commodity from rows if available (single-commodity assumption).
        commodity = ""
        if self.rows:
            # Use the first row's value — all rows share the same commodity in
            # balance_from_spec (multi-commodity support is deferred).
            commodity = list(self.rows.keys())[0] if self.rows else ""
            # Actually rows are account names, not commodities. We need the
            # commodity from the style map or just leave it as empty.
            commodity = next(iter(self._commodity_styles), "")
        style = self._commodity_styles.get(commodity) if commodity else None
        row_list = []
        for account, amount in self.rows.items():
            formatted = style.format(amount) if style else str(amount)
            row_list.append({
                "account": account,
                "amount": amount,
                "commodity": commodity,
                "amount_formatted": formatted,
            })
        # Add total row.
        total_label = f"Total {self.section.name}"
        total_formatted = style.format(self.subtotal) if style else str(self.subtotal)
        row_list.append({
            "account": total_label,
            "amount": self.subtotal,
            "commodity": commodity,
            "amount_formatted": total_formatted,
        })
        df = pd.DataFrame(row_list, columns=["account", "amount", "commodity", "amount_formatted"])
        if not df.empty:
            df["amount"] = df["amount"].astype(object)
        return df


@dataclass
class Journal:
    """Top-level container for all parsed journal data.

    Returned by parse_string() and parse_file(). Report methods on this class
    delegate to ledgerkit.reports and use lazy imports to avoid circular
    dependencies between models.py and reports.py.
    """

    transactions: list[Transaction] = field(default_factory=list)
    prices: list[PriceDirective] = field(default_factory=list)
    declared_accounts: list[str] = field(default_factory=list)
    declared_commodities: list[str] = field(default_factory=list)
    declared_payees: list[str] = field(default_factory=list)
    declared_tags: list[str] = field(default_factory=list)
    source_file: str | None = None
    included_files: int = 0
    # Maps commodity symbol → raw amount string from an explicit `commodity`
    # directive (e.g. "USD" → "1,000.00 USD"). Used by commodity_styles to
    # give directive-declared styles priority over inferred ones.
    _commodity_directive_raws: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    # Commodity style
    # ------------------------------------------------------------------

    @property
    def commodity_styles(self) -> dict:
        """Return Dict[str, CommodityStyle] inferred from journal data.

        Priority order (highest wins):
          1. Explicit ``commodity`` directives.
          2. First posting amount seen for each commodity.
          3. First price-directive amount seen for each commodity.
        """
        from ledgerkit.commodity_style import CommodityStyle
        styles: dict = {}
        # Pass 1: infer from posting amounts (first seen per commodity).
        for txn in self.transactions:
            for p in txn.postings:
                if p.amount and p.amount.raw and p.amount.commodity not in styles:
                    try:
                        styles[p.amount.commodity] = CommodityStyle.infer(
                            p.amount.commodity, p.amount.raw
                        )
                    except Exception:
                        pass
        # Pass 2: infer from price directive amounts.
        for price in self.prices:
            if price.price.raw and price.price.commodity not in styles:
                try:
                    styles[price.price.commodity] = CommodityStyle.infer(
                        price.price.commodity, price.price.raw
                    )
                except Exception:
                    pass
        # Pass 3: directive-based styles take priority over inferred.
        for comm, raw in self._commodity_directive_raws.items():
            try:
                styles[comm] = CommodityStyle.infer(comm, raw)
            except Exception:
                pass
        return styles

    # ------------------------------------------------------------------
    # Report methods — thin wrappers that delegate to ledgerkit.reports.
    # Lazy imports are used to avoid a circular dependency:
    #   models.py → reports.py → models.py
    # ------------------------------------------------------------------

    def balance(
        self,
        accounts: list[str] | None = None,
        query: Query | None = None,
        tree: bool = False,
    ) -> dict[str, dict[str, Decimal]] | list[BalanceRow]:
        """Return per-commodity net balances for each account.

        Args:
            accounts: [Deprecated] Optional list of account name substrings to
                      filter by. Use query= for new code.
            query: Optional Query to filter postings. Takes precedence over
                   accounts when both are supplied.
            tree: When True, returns list[BalanceRow] with implicit parent
                  accounts and subtotals. When False (default), returns a flat
                  dict[str, dict[str, Decimal]] (account → commodity → net).
        """
        from ledgerkit.reports import balance as _balance
        # Deprecated 'accounts' param: convert to Query for backward compat.
        if accounts is not None and query is None:
            import re as _re
            if len(accounts) == 1:
                query = Query(account=accounts[0])
            else:
                pattern = "|".join(f"(?:{_re.escape(a)})" for a in accounts)
                query = Query(account=pattern)
        return _balance(self, query, tree=tree)

    def register(
        self,
        accounts: list[str] | None = None,
        query: Query | None = None,
    ) -> list[RegisterRow]:
        """Return a chronological list of RegisterRow objects.

        Args:
            accounts: [Deprecated] Optional list of account name substrings to
                      filter by. Use query= for new code.
            query: Optional Query to filter postings. Takes precedence over
                   accounts when both are supplied.
        """
        from ledgerkit.reports import register as _register
        # Deprecated 'accounts' param: convert to Query for backward compat.
        if accounts is not None and query is None:
            import re as _re
            if len(accounts) == 1:
                query = Query(account=accounts[0])
            else:
                pattern = "|".join(f"(?:{_re.escape(a)})" for a in accounts)
                query = Query(account=pattern)
        return _register(self, query)

    def accounts(self) -> list[str]:
        """Return a sorted list of all unique account names in the journal."""
        from ledgerkit.reports import accounts as _accounts
        return _accounts(self)

    def stats(self, query: Query | None = None) -> JournalStats:
        """Return a JournalStats object with summary statistics."""
        from ledgerkit.reports import stats as _stats
        return _stats(self, query)

    def to_dataframe(self, query: Query | None = None):
        """Export postings to a pandas DataFrame (one row per posting).

        Columns: date, description, cleared, pending, account,
                 amount (Decimal|None), commodity (str|None),
                 amount_formatted (str|None).

        Accepts an optional Query to pre-filter the data.
        Requires pandas: pip install ledgerkit[pandas]
        """
        from ledgerkit._pandas_compat import require_pandas
        pd = require_pandas()
        from ledgerkit.reports import _posting_matches
        styles = self.commodity_styles
        rows = []
        for txn in self.transactions:
            for p in txn.postings:
                if not _posting_matches(p, txn, query):
                    continue
                amt = p.amount
                if amt is not None:
                    style = styles.get(amt.commodity)
                    amount_val = amt.quantity
                    commodity_val = amt.commodity
                    formatted_val = amt.display(style) if style else str(amt.quantity)
                else:
                    amount_val = None
                    commodity_val = None
                    formatted_val = None
                rows.append({
                    "date": txn.date,
                    "description": txn.description,
                    "cleared": txn.cleared,
                    "pending": txn.pending,
                    "account": p.account,
                    "amount": amount_val,
                    "commodity": commodity_val,
                    "amount_formatted": formatted_val,
                })
        df = pd.DataFrame(rows, columns=[
            "date", "description", "cleared", "pending", "account",
            "amount", "commodity", "amount_formatted",
        ])
        # Preserve Decimal type in amount column (avoid float coercion)
        if not df.empty and "amount" in df.columns:
            df["amount"] = df["amount"].astype(object)
        return df

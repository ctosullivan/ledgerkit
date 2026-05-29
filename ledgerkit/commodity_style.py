"""Commodity display style inference and formatting for ledgerkit.

Captures how a commodity's amounts should be formatted: symbol position,
spacing, decimal mark, digit-group separator, and precision. Styles are
inferred from the first amount seen in the journal or from an explicit
`commodity` directive, then applied consistently throughout report output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _group_digits(digits: str, sep: str) -> str:
    """Insert sep every 3 digits from the right (e.g. "1234567" → "1,234,567")."""
    result = []
    for i, ch in enumerate(reversed(digits)):
        if i > 0 and i % 3 == 0:
            result.append(sep)
        result.append(ch)
    return "".join(reversed(result))


# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

# Matches a trailing suffix commodity symbol in a style/amount string.
#
# Purpose: identify an alphabetic commodity code (e.g. "EUR", "USD", "AAPL")
#          at the end of an amount string, optionally preceded by whitespace.
#          Used by parse_style_override() to extract the commodity before
#          delegating to infer().
#
# Group breakdown:
#   (1) ([A-Za-z][A-Za-z0-9]*)  — letter-started alphanumeric token;
#                                  matches "EUR", "USD", "AAPL", "GBP" etc.
#   \s*$                         — optional trailing whitespace then end of string
#
# Edge cases:
#   - "1,234.56 EUR"  → matches "EUR"
#   - "1.000,00 EUR"  → matches "EUR"
#   - "$1,234.56"     → does NOT match (no trailing alphabetic token)
#   - "bad input !!"  → does NOT match ("!!" is not alphanumeric)
#   - "EUR 1,234.56"  → does NOT match (EUR is not at the end)
_STYLE_SUFFIX_COMMODITY = re.compile(r"([A-Za-z][A-Za-z0-9]*)\s*$")

# Matches a leading prefix commodity symbol in a style/amount string.
#
# Purpose: identify a non-numeric, non-separator commodity symbol (e.g. "$",
#          "£", "€") at the start of an amount string, after an optional
#          minus sign.  Used by parse_style_override() when no suffix
#          alphabetic commodity is found.
#
# Group breakdown:
#   (1) (-?)               — optional leading minus sign (consumed, not used here)
#   (2) ([^\d,.\s-]+)      — one or more characters that are not digits, commas,
#                            dots, whitespace, or minus; captures currency symbols
#                            like "$", "£", "€", "¥"
#
# Edge cases:
#   - "$1,234.56"     → group 2 = "$"
#   - "£9,999.00"     → group 2 = "£"
#   - "1,234.56 EUR"  → does NOT match (starts with a digit)
#   - "-$1,234.56"    → group 1 = "-", group 2 = "$"
#   - "bad input !!"  → group 2 = "bad" (but caller validates digits are present)
_STYLE_PREFIX_COMMODITY = re.compile(r"^(-?)([^\d,.\s-]+)")


# ---------------------------------------------------------------------------
# CommodityStyle
# ---------------------------------------------------------------------------

@dataclass
class CommodityStyle:
    """Display style for a single commodity, inferred from journal data.

    Captures how amounts in this commodity should be formatted: whether the
    symbol is a prefix or suffix, whether there is a space between symbol
    and number, which character is the decimal mark, which (if any) is the
    digit-group separator, and how many decimal places to show.
    """

    commodity: str
    prefix: bool = True
    space: bool = False
    decimal_mark: str = "."
    group_separator: str = ""
    precision: int = 2

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format(self, quantity: Decimal) -> str:
        """Return a formatted amount string using this commodity's display style."""
        negative = quantity < 0
        abs_qty = abs(quantity)

        if self.precision > 0:
            # Python always formats with '.' — we replace it with decimal_mark below.
            formatted = f"{abs_qty:.{self.precision}f}"
            int_str, frac_str = formatted.split(".")
        else:
            int_str = str(int(abs_qty))
            frac_str = ""

        if self.group_separator:
            int_str = _group_digits(int_str, self.group_separator)

        if frac_str:
            number = int_str + self.decimal_mark + frac_str
        else:
            number = int_str

        gap = " " if self.space else ""
        if self.prefix:
            # hledger convention: prefix-symbol negative → SYMBOL-NUMBER (e.g. £-5.00)
            if negative:
                return f"{self.commodity}-{number}"
            return f"{self.commodity}{gap}{number}"
        else:
            # hledger convention: suffix-symbol negative → -NUMBER SYMBOL (e.g. -5.00 EUR)
            if negative:
                return f"-{number}{gap}{self.commodity}"
            return f"{number}{gap}{self.commodity}"

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    @classmethod
    def infer(cls, commodity: str, raw_amount_str: str) -> "CommodityStyle":
        """Infer a CommodityStyle by parsing the first seen raw amount string.

        Detects prefix/suffix, spacing, decimal mark, group separator, and
        precision from the raw text as it appeared in the journal source.
        """
        raw = raw_amount_str.strip()

        # Strip leading minus sign for symbol detection purposes.
        s = raw[1:] if raw.startswith("-") else raw

        prefix = True
        space = False
        numeric = s

        if commodity and s.startswith(commodity):
            prefix = True
            rest = s[len(commodity):]
            space = rest.startswith(" ") or rest.startswith("\t")
            numeric = rest.lstrip()
        elif commodity and s.endswith(commodity):
            prefix = False
            rest = s[: -len(commodity)]
            space = rest.endswith(" ") or rest.endswith("\t")
            numeric = rest.rstrip()
        # else: numeric = s (no recognisable commodity position; rare edge case)

        decimal_mark, group_separator, precision = _infer_separators(numeric)

        return cls(
            commodity=commodity,
            prefix=prefix,
            space=space,
            decimal_mark=decimal_mark,
            group_separator=group_separator,
            precision=precision,
        )

    # ------------------------------------------------------------------
    # Override parsing
    # ------------------------------------------------------------------

    @classmethod
    def parse_style_override(cls, style_string: str) -> "CommodityStyle":
        """Parse a -c/--commodity-style override string in hledger format.

        Examples::
            "1,000.00 USD"   → suffix, space, dot decimal, comma group, precision 2
            "$1,000.00"      → prefix, no space, dot decimal, comma group, precision 2
            "1.000,00 EUR"   → suffix, space, comma decimal, dot group, precision 2

        Returns a CommodityStyle with the commodity extracted from the string.
        Raises ValueError if the string cannot be parsed or contains no digits.
        """
        s = style_string.strip()
        if not s:
            raise ValueError(f"cannot parse commodity style: empty string")

        # Must contain at least one digit to be a valid amount string.
        if not any(ch.isdigit() for ch in s):
            raise ValueError(
                f"cannot parse commodity style (no digits): {style_string!r}"
            )

        # Try suffix alphabetic commodity first (e.g. "1,000.00 USD").
        m_suffix = _STYLE_SUFFIX_COMMODITY.search(s)
        if m_suffix:
            commodity = m_suffix.group(1)
            return cls.infer(commodity, s)

        # Try prefix non-digit commodity symbol (e.g. "$1,000.00").
        m_prefix = _STYLE_PREFIX_COMMODITY.match(s)
        if m_prefix and m_prefix.group(2):
            commodity = m_prefix.group(2)
            return cls.infer(commodity, s)

        raise ValueError(f"cannot parse commodity style: {style_string!r}")


# ---------------------------------------------------------------------------
# Separator inference helper
# ---------------------------------------------------------------------------

def _infer_separators(numeric: str) -> tuple:
    """Return (decimal_mark, group_separator, precision) from a numeric string."""
    dots = numeric.count(".")
    commas = numeric.count(",")

    if dots > 0 and commas > 0:
        # Both present: the rightmost separator is the decimal mark.
        last_dot = numeric.rfind(".")
        last_comma = numeric.rfind(",")
        if last_dot > last_comma:
            # e.g. "1,234.56" → decimal ".", group ","
            decimal_mark = "."
            group_separator = ","
            precision = len(numeric) - last_dot - 1
        else:
            # e.g. "1.234,56" → decimal ",", group "."
            decimal_mark = ","
            group_separator = "."
            precision = len(numeric) - last_comma - 1
    elif dots > 0:
        last_dot = numeric.rfind(".")
        digits_after = len(numeric) - last_dot - 1
        if digits_after == 3 and dots == 1 and last_dot > 0:
            # e.g. "1.234" → group ".", decimal "," (European integer)
            group_separator = "."
            decimal_mark = ","
            precision = 0
        else:
            # e.g. "1.5", "100.00" → decimal "."
            decimal_mark = "."
            group_separator = ""
            precision = digits_after
    elif commas > 0:
        last_comma = numeric.rfind(",")
        digits_after = len(numeric) - last_comma - 1
        if digits_after == 3 and commas == 1 and last_comma > 0:
            # e.g. "1,234" → group ",", decimal "." (US/UK integer)
            group_separator = ","
            decimal_mark = "."
            precision = 0
        else:
            # e.g. "100,5", "1,50" → decimal ","
            decimal_mark = ","
            group_separator = ""
            precision = digits_after
    else:
        # No separators at all (e.g. "100", "42")
        decimal_mark = "."
        group_separator = ""
        precision = 0

    return decimal_mark, group_separator, precision

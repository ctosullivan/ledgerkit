"""Lazy import helper for optional pandas dependency."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd  # noqa: F401 — type hints only


def require_pandas():
    """Import and return the pandas module, raising ImportError with a helpful
    message if it is not installed."""
    try:
        import pandas as pd
        return pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame export. "
            "Install it with: pip install ledgerkit[pandas]"
        ) from None

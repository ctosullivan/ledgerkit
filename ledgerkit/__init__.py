"""ledgerkit: a deterministic, Python-native accounting and query engine
with a documented hledger-compatible foundation.

Copyright (C) 2026 Cormac O'Sullivan

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version. See the LICENSE and NOTICE files at the
repository root, and dev-docs/planning/core-redefinition/02-licence-migration.md
for the migration this took effect under.
"""

from ledgerkit.loader import load_journal as load
from ledgerkit.models import (
    BalanceAssertion,
    BalanceRow,
    Query,
    RegisterRow,
    ReportSection,
    ReportSpec,
    ReportSectionResult,
    SourceSpan,
)
from ledgerkit.parser import parse_string_lenient, resolve_elision
from ledgerkit.reports import (
    AccountsResult,
    BalanceResult,
    JournalStats,
    RegisterResult,
    balance_from_spec,
)
from ledgerkit.checks import CheckError, check_transaction_autobalanced
from ledgerkit.writer import journal_to_text, transaction_to_text
from ledgerkit.editor_model import EditorDocument
from ledgerkit.commodity_style import CommodityStyle

__version__ = "1.0.0.dev1"
__all__ = [
    "load",
    "AccountsResult",
    "BalanceAssertion",
    "BalanceResult",
    "BalanceRow",
    "CheckError",
    "CommodityStyle",
    "EditorDocument",
    "JournalStats",
    "RegisterResult",
    "RegisterRow",
    "ReportSection",
    "ReportSpec",
    "ReportSectionResult",
    "SourceSpan",
    "balance_from_spec",
    "check_transaction_autobalanced",
    "journal_to_text",
    "parse_string_lenient",
    "resolve_elision",
    "transaction_to_text",
    "__version__",
]

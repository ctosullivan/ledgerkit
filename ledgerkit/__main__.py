"""Enables `python -m ledgerkit` invocation.

Usage:
    python -m ledgerkit <command> <journal-file>

This is equivalent to running the `ledgerkit` CLI entry point directly.
"""

import sys
from ledgerkit.cli import main

sys.exit(main())

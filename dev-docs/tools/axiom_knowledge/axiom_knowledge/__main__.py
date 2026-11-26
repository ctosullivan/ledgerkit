"""Allows `python3 -m axiom_knowledge <args...>` to run the CLI, matching
`axiom_validator`'s own `python3 -m axiom_validator <paths...>` convention
(see that package's `__main__.py`) -- this project's existing, deliberate
choice not to add packaging infrastructure for a second component either.
"""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())

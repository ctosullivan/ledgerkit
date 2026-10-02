<!-- producer: assertion-research | topic: checks | dispatch: ck-tiers-01 | date: 2026-10-02 -->
# Assertion: checks-001

## Statement
Validation checks are organized into three fixed tiers mirroring hledger's own classification: BASIC_CHECK_NAMES = ("parseable", "autobalanced", "assertions") run on every CLI command by default; STRICT_CHECK_NAMES = ("accounts", "commodities") run only when `-s`/`--strict` is given, in addition to basic; OTHER_CHECK_NAMES = ("payees", "ordereddates", "uniqueleafnames") run only when explicitly named via the `check` command.

## Kind
definition
## Basis
directly_stated
## Evidence
The module docstring explicitly states the tier semantics, and the three tuple constants enumerate exactly which check names belong to each tier; ALL_CHECK_NAMES is their concatenation.

Evidence-paths: [ledgerkit/checks.py:7-11, ledgerkit/checks.py:27-33]

## Justification
The docstring (lines 7-11) states the tier purpose in plain language ("basic — run by default on every CLI command", etc.), and the constants immediately below (lines 27-33) give the exact, closed membership of each tier — this is a definition, not an inference.

## Examples
`BASIC_CHECK_NAMES` contains "parseable", "autobalanced", "assertions" (checks.py:27). `STRICT_CHECK_NAMES` contains "accounts", "commodities" (checks.py:28). `OTHER_CHECK_NAMES` contains "payees", "ordereddates", "uniqueleafnames" (checks.py:29).

## Counterexamples
None found — the tuples are the sole source of truth and are consumed directly by `_CHECK_FN`, `run_basic_checks`, `run_strict_checks`, and `run_checks` (checks.py:523-617) with no divergent membership elsewhere in the file.

## Depends on
None.

## Open questions
None — fully resolved from the permitted evidence.

## Evidence-support state
supported
## Status
verified
## Supersedes
None

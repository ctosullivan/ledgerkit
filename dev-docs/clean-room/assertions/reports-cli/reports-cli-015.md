<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-015 | date: 2026-10-02 -->
# Assertion: reports-cli-015

## Statement
`check` is the only CLI command with a distinct control-flow path in `main()`: it runs before the output-file/`contextlib.redirect_stdout` setup, prints nothing to stdout on success (exit 0), and on any check failure prints each error's `.message` to stderr and exits 1. `-I`/`--ignore-assertions` suppresses only the "assertions" basic check (passed as `skip=frozenset({"assertions"})` to both the default basic-check gate that runs before every command, and to `check` itself), while `-s`/`--strict` additionally runs `run_strict_checks()` (filtered to exclude names already in `BASIC_CHECK_NAMES`) for every non-check command, and is also forwarded into `check` itself via `strict=args.strict`.
## Kind
state_transformation
## Basis
directly_stated
## Evidence
cli.py: `_skip = frozenset({"assertions"}) if getattr(args, "ignore_assertions", False) else frozenset()`; the default gate `basic_errors = _checks.run_basic_checks(journal, skip=_skip)` runs unconditionally for every command before the `if args.command == "check":` branch; inside that branch, `errors = _checks.run_checks(journal, names=list(check_names), strict=args.strict, skip=_skip)`, returning 0 with no stdout output on success or 1 with each `e.message` on stderr otherwise. Tests: `test_passing_assertions_exits_zero`, `test_failing_assertion_exits_one` (asserts `"assertion"` lowercase substring in stderr), `test_ignore_assertions_flag_suppresses_failure`/`test_ignore_assertions_long_flag` (both `-I` forms suppress the failure for `stats`), `test_check_command_reports_assertion_error`/`test_check_command_passes_on_clean_journal` (same for the `check` command itself).
## Justification
Direct correspondence between cli.py:253-291 and the TestBalanceAssertions test class, covering both the default-gate and explicit-`check`-command code paths.
## Examples
`ledgerkit -I stats -f assertions_fail.journal` → exit 0 despite a failing balance assertion; `ledgerkit check assertions -f assertions_fail.journal` → exit 1, stderr contains "assertion".
## Counterexamples
None
## Depends on
None
## Open questions
None
## Evidence-support state
supported
## Status
verified
## Supersedes
None

Evidence-paths: [ledgerkit/cli.py:253-291, tests/test_cli/test_cli.py:295-334]

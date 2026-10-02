<!-- producer: assertion-research | topic: reports-cli | dispatch: rc-003 | date: 2026-10-02 -->
# Assertion: reports-cli-003

## Statement
Journal-file resolution for non-`check` commands follows strict precedence: (1) one or more `-f`/`--file` flags; (2) a single positional `journal` argument (shorthand); (3) `$LEDGER_FILE` env var; (4) `~/.hledger.journal` if it exists. Combining `-f` with a positional argument is a hard error (exit 1), and if none of the four sources resolve, the CLI exits 1 with "no journal file specified". For the `check` command, all positional arguments are treated as check *names*, never as a journal file — the journal must come from `-f`/env/default.
## Kind
rule
## Basis
directly_stated
## Evidence
`_resolve_files()` implements this precisely: `is_check = getattr(args, "command", None) == "check"`; `positional_file = args.journal[0] if (args.journal and not is_check) else None`; raises `SystemExit(1)` with message "cannot combine -f/--file flags with a positional journal argument" when both are set; falls through `args.files` → `positional_file` → `os.environ.get("LEDGER_FILE")` → `Path.home() / ".hledger.journal"` → final `SystemExit(1)` "no journal file specified; use -f FILE or set $LEDGER_FILE". Confirmed by tests: `test_f_flag_and_positional_errors` asserts exit code 1 for `-f SAMPLE stats SAMPLE`; `test_env_fallback_ledger_file` and `test_no_file_no_env_exits_with_message` confirm the env/default/error path.
## Justification
Both the implementation and the test suite agree on this precedence order exactly.
## Examples
`ledgerkit stats sample.journal` (positional shorthand); `LEDGER_FILE=x.journal ledgerkit stats` (env fallback); `ledgerkit check assertions -f x.journal` (positional = check name, not file)
## Counterexamples
`ledgerkit -f a.journal stats a.journal` → exits 1 ("cannot combine -f/--file flags with a positional journal argument")
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

Evidence-paths: [ledgerkit/cli.py:142-184, tests/test_cli/test_cli.py:108-162]

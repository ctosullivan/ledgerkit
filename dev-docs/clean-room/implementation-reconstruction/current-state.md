# Implementation Reconstruction: `current-state`

**Role:** implementation-reconstructor
**Topic:** current-state
**Dispatch timestamp:** 2026-10-02T16:54:48Z (UTC)
**Date:** 2026-10-03

**Evidence method:** model-blind, source-code-blind. All findings below come
exclusively from (a) reading `pyproject.toml`, and (b) running the installed
`ledgerkit` CLI directly via `python -m ledgerkit ...` against
`tests/fixtures/sample.journal`, and recording exact commands, exact stdout,
and exact exit codes. No `ledgerkit/*.py` source file was opened. No
assertion, snapshot, or legacy documentation file was read.

---

## 1. Package identity (from `pyproject.toml`)

- `name = "ledgerkit"`, `version = "1.0.0.dev1"`
- `requires-python = ">=3.8"`
- `dependencies = []` — zero required third-party runtime dependencies
- `optional-dependencies.pandas = ["pandas>=1.3"]` — pandas is opt-in only
- Console entry point: `[project.scripts] ledgerkit = "ledgerkit.cli:main"`
  — confirms the installed `ledgerkit` command and `python -m ledgerkit`
  both resolve to `ledgerkit.cli:main`
- `classifiers` claim `Development Status :: 5 - Production/Stable` despite
  the version string being a `.dev1` pre-release — a direct internal
  inconsistency in the package metadata itself, observable without reading
  any source.

## 2. CLI entry surface — exact `--help` output

Command run: `python -m ledgerkit --help` — exit code `0`.

```
usage: ledgerkit [-h] [--version] [-v] [-1] [-o FILE] [-f FILE] [-s] [-I]
                 [-q TERMS] [-c STYLE]
                 {balance,register,accounts,print,stats,check} [journal ...]

Plain-text accounting (hledger-compatible)

positional arguments:
  {balance,register,accounts,print,stats,check}
                        Report to run: balance, register, accounts, print,
                        stats, check
  journal               Journal file (shorthand for -f; all commands except
                        check), or check names (check command only)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         Show more detailed output (stats: commodity names)
  -1                    Show a single tab-separated line of output (stats
                        only)
  -o, --output-file FILE
                        Write output to FILE instead of stdout
  -f, --file FILE       Read data from FILE, or stdin if -. May be specified
                        more than once.
  -s, --strict          Enable strict mode: also check that accounts and
                        commodities are declared
  -I, --ignore-assertions
                        Disable balance assertion checking
  -q, --query TERMS     Filter using a query string (see ledgerkit.query),
                        e.g. 'acct:food date:2024'. Applies to balance,
                        register, accounts, stats, and print.
  -c, --commodity-style STYLE
                        Override display style for a commodity, e.g.
                        '$1,000.00' or '1.000,00 EUR'. May be specified more
                        than once.
```

This is the **entire** public CLI surface currently exposed: six report
commands (`balance`, `register`, `accounts`, `print`, `stats`, `check`) under
one flat `argparse` parser. There are no per-subcommand parsers: running
`python -m ledgerkit check --help` (exit `0`) prints the exact same top-level
usage block, not a `check`-specific help page — confirming there is a single
flat argument parser shared by all six commands, not real subcommands with
their own option sets.

`python -m ledgerkit --version` → stdout `ledgerkit 1.0.0.dev1`, exit `0`,
matching `pyproject.toml`'s version string exactly.

## 3. Observed runtime behaviour per command (against `sample.journal`)

Fixture content (read directly, since it is explicitly in-scope as the
target of the live commands, not as source code):
- 5 transactions, 2024-01-01 to 2024-01-20
- One `*` (cleared) transaction, one `!` (pending) transaction, three
  unflagged
- One transaction ("Coffee shop") has two postings to the same account
  (`expenses:food:coffee`, twice, £4.50 each) and an inline comment
  `; business meeting` on the header line
- Uses `£` as the only commodity throughout; all amounts balance to zero

### `stats`
`python -m ledgerkit stats -f tests/fixtures/sample.journal` → exit `0`:
```
Main file           : /home/cormac/projects/ledgerkit/tests/fixtures/sample.journal
Included files      : 0
Txns span           : 2024-01-01 to 2024-01-20 (20 days)
Last txn            : 2024-01-20 (987 days ago)
Txns                : 5 (0.2 per day)
Txns last 30 days   : 0 (0.0 per day)
Txns last 7 days    : 0 (0.0 per day)
Payees/descriptions : 5
Accounts            : 6 (depth 3)
Commodities         : 1
Market prices       : 0
Runtime stats       : 0.02 s elapsed, 238 txns/s
```
- "987 days ago" is computed against the real system clock (today
  2026-10-03), not a fixed reference point — this report will silently
  produce a different "days ago" value and a different "Txns last 30/7
  days" figure every time it is run in the future, which is expected
  behaviour for a stats command but worth flagging as non-deterministic
  output tied to wall-clock time.
- `-v` (verbose) changes only the `Commodities` line, appending the actual
  symbol in parens: `Commodities : 1 (£)` — confirmed by direct comparison
  of `stats` vs `stats -v` output.
- `-1` emits a single tab-separated line instead:
  `1.0.0.dev1\t/home/.../sample.journal\t0.02 s elapsed\t294 txns/s` — note
  this single-line mode only includes version, path, and the two runtime
  stats fields, not the full stats (txn counts, span, accounts, etc. are
  dropped entirely in `-1` mode).
- Runtime stats figures (`elapsed`, `txns/s`) vary slightly run to run
  (238, 295, 294, 216, 187, 277 txns/s observed across repeated invocations
  in this session) — confirming these are live-measured, not fixed/cached.

### `check`
`python -m ledgerkit check -f tests/fixtures/sample.journal` → **exit `0`,
zero stdout, zero stderr** — fully silent success. This is the single most
important behavioural fact about `check`: a clean journal produces no
output at all, and the only signal of success is the exit code.

- `check` with no `-f` and a positional argument that looks like a file
  path (`python -m ledgerkit check tests/fixtures/sample.journal`, no `-f`)
  does **not** treat the positional as a file. It is interpreted strictly
  as a check name (per the `--help` text: "journal ... or check names
  (check command only)"), and since no `-f`/`$LEDGER_FILE` was given, it
  fails with exit `1` and stderr:
  `ledgerkit: no journal file specified; use -f FILE or set $LEDGER_FILE`.
  This is a real, user-facing footgun: the same positional-argument syntax
  that works as a file-path shorthand for every other command does **not**
  work for `check`.
- `check -f sample.journal <name>` with an invalid check name fails with
  exit `1` and enumerates the valid set directly in the error message:
  `ledgerkit: unknown check 'X'; available: accounts, assertions,
  autobalanced, commodities, ordereddates, parseable, payees,
  uniqueleafnames`. This is the authoritative, live-observed list of the
  eight check names currently recognized by the `check` command.
- `check -f sample.journal ordereddates` and `check -f sample.journal
  assertions` (named checks the fixture passes) both exit `0` with no
  output — confirming individual named checks are also silent on success.
- `check -f sample.journal -s` (strict mode) on this same fixture **fails**,
  exit `1`, with two detailed, source-located error reports (one for
  `assets:bank:checking` not being declared via an `account` directive, one
  for commodity `£` not being declared via a `commodity` directive), each
  including a file:line pointer, a 3-line source excerpt with a `^^^`
  caret span under the offending token, and a suggested fix snippet. This
  is a materially different code path from default (non-strict) `check`:
  the sample fixture is only "clean" under default checks, not under
  `-s` strict mode. The two strict-mode diagnostics printed stop after the
  first posting that trips each category (only the first undeclared
  account and first undeclared commodity are reported in this run), so it
  is not yet confirmed from this evidence alone whether every undeclared
  account/commodity in a larger file is reported or only the first
  instance.

### `balance`
`python -m ledgerkit balance -f tests/fixtures/sample.journal` → exit `0`:
```
           £4,905.60  assets:bank:checking
             £500.00  assets:bank:savings
          £-2,000.00  equity:opening-balances      [printed in red/ANSI]
               £9.00  expenses:food:coffee
              £85.40  expenses:food:groceries
          £-3,500.00  income:salary                [printed in red/ANSI]
--------------------
                   0
```
- Negative amounts are wrapped in ANSI SGR `\x1b[31m...\x1b[0m` (red) escape
  codes **even when stdout is being captured/piped**, not just when
  attached to an interactive terminal — confirmed by inspecting the raw
  captured bytes in this session (every invocation through the Bash tool
  is a non-tty pipe, and the escapes were present regardless). This means
  the current build does not appear to gate color output on `isatty()`;
  anything consuming `ledgerkit balance` output programmatically without
  stripping ANSI codes will see them.
- Accounts are listed in flat alphabetical order with no indentation by
  depth/hierarchy in this fixture's output.
- The bare positional shorthand (`ledgerkit balance tests/fixtures/sample.journal`,
  no `-f`) produces byte-identical output to the `-f`-flagged form — confirmed
  by direct comparison — so the "journal shorthand for -f" claim in `--help`
  holds for `balance` (unlike `check`, see above).
- `-q 'acct:food'` correctly filters to just the two `expenses:food:*`
  accounts and recomputes the total line as their sum (`£94.40`), not the
  grand total — confirming the query filter is applied before aggregation,
  not just before display.
- `-I` (ignore-assertions) produced byte-identical output to the default run
  on this fixture — expected, since this fixture contains no balance
  assertions (`=` syntax) to disable in the first place; this flag's actual
  effect was not exercised by this fixture.
- `-c STYLE` only takes effect when the style string's own commodity symbol
  matches a commodity actually present in the data. `-c '1,000.00 GBP'` (no
  `£` symbol) left output unchanged — the override was silently ignored for
  this fixture's `£`-only data. `-c '£1.000,00'` (matching symbol, European
  separators) did take effect, reformatting every amount to
  `£4.905,60`-style output. There is no error or warning when a `-c` style
  fails to match any commodity in the file — it is accepted and silently
  has no effect, which is a notable silent-no-op gap.

### `register`
`python -m ledgerkit register -f tests/fixtures/sample.journal` → exit `0`.
Notable, non-obvious observed behaviour: account names are **abbreviated**
in the fixed-width column when they would otherwise not fit/align, e.g.
`equity:opening-balances` is rendered as `eq:opening-balances` and
`expenses:food:groceries` as `ex:food:groceries` in this report's output,
while the same accounts appear unabbreviated in `balance` and `accounts`
output. This abbreviation behavior is real and observed directly in the
captured output, not inferred — but *why* truncation triggers for some
account names and not others in this same report (e.g.
`expenses:food:coffee` prints in full) was not traced further, since doing
so would require reading source, which is out of scope for this report.
Negative running/posting amounts are rendered in the same red ANSI style
as `balance`.

### `accounts`
`python -m ledgerkit accounts -f tests/fixtures/sample.journal` → exit `0`,
plain flat alphabetical list of the 6 account names, one per line, no
amounts, no color codes observed.

### `print`
`python -m ledgerkit print -f tests/fixtures/sample.journal` → exit `0`.
Reprints every transaction in journal syntax, preserving the `*` and `!`
status flags on transaction headers and preserving the duplicate
`expenses:food:coffee` postings as two separate lines (not merged) — but
**the inline comment `; business meeting` on the "Coffee shop" transaction
header in the source fixture is dropped entirely from the `print` output**.
This was confirmed by diffing the original fixture text against the
command's stdout directly: the source line reads
`2024-01-20 Coffee shop  ; business meeting` and the corresponding output
line reads only `2024-01-20 Coffee shop`, with no comment. This is a real,
observed data-loss gap in the currently-running `print` command: round-
tripping a journal through `print` does not currently preserve header-level
inline comments.

## 4. Argument-handling observations (CLI surface, confirmed by running, not inferred)

- No command is required to be given with `-f`; bare `python -m ledgerkit`
  (no command at all) fails fast with argparse's own usage/error text
  (`the following arguments are required: command`), exit code `2` — the
  standard `argparse` exit code for a usage error, distinct from
  ledgerkit's own application-level errors which exit `1`.
- `$LEDGER_FILE` environment variable is honored as a fallback source of
  the journal path when no `-f`/positional is given — confirmed:
  `LEDGER_FILE=tests/fixtures/sample.journal python -m ledgerkit stats`
  (no `-f` at all) succeeds and reports the same fixture's stats, exit `0`.
- `-f -` reads the journal from stdin — confirmed:
  `cat sample.journal | python -m ledgerkit stats -f -` succeeds, exit `0`,
  and reports `Main file : (stdin)` in place of a path.
- `-o FILE` redirects report output to a file instead of stdout — confirmed
  by writing `stats` output to a scratch file and inspecting its contents,
  which matched the stdout form byte-for-byte (modulo the live
  runtime-stats numbers, which vary run to run as noted above). Nothing is
  printed to stdout when `-o` is given (exit `0`, empty stdout, file
  populated).
- A nonexistent `-f` path fails with exit `1` and a Python-exception-shaped
  message passed through: `ledgerkit: file not found: [Errno 2] No such
  file or directory: '...'` — i.e. the underlying `FileNotFoundError`'s
  `str()` representation is embedded verbatim in the user-facing error,
  rather than being reworded into a clean standalone message.

## 5. Limitations / gaps established by direct evidence (not inference)

1. **`check`'s positional-argument semantics are inconsistent with every
   other command.** For `balance`/`register`/`accounts`/`stats`/`print`, a
   bare positional argument is a working shorthand for `-f`. For `check`,
   the same positional syntax is interpreted as a check *name*, and omitting
   `-f` in that form fails outright. This is a genuine, currently-shipping
   footgun confirmed by direct exit-code/stderr evidence, not a hypothetical.
2. **`check` is completely silent on success**, with exit code `0` as the
   only success signal — there is no "all checks passed" message, no count
   of checks run, nothing written to stdout or stderr.
3. **`-c` (commodity-style override) silently no-ops when the style
   string's symbol doesn't match any commodity in the file.** No warning or
   error is produced; the flag is simply ineffective. Confirmed directly by
   comparing `-c '1,000.00 GBP'` (no-op) against `-c '£1.000,00'` (effective)
   on the identical fixture.
4. **`print` drops header-line inline comments.** Confirmed directly via
   diff of fixture source vs. `print` stdout: the `; business meeting`
   comment on the "Coffee shop" transaction is absent from the reprinted
   output. This means `print` is not currently a lossless round-trip of
   the source journal text for this comment category.
5. **ANSI color codes are emitted unconditionally**, including when stdout
   is not a TTY (every invocation in this environment was through a
   non-interactive pipe, and color codes were present every time for
   negative amounts in `balance` and `register`). Any caller consuming
   this output programmatically must strip ANSI escapes itself; there is
   no observed `--color`/`--no-color` flag in `--help` to control this.
6. **`register`'s account-name abbreviation trigger condition was observed
   but not fully characterized.** `equity:opening-balances` and
   `expenses:food:groceries` were abbreviated to `eq:...` / `ex:...` in
   `register` output while `expenses:food:coffee` (also a long dotted
   account name) was not, in the same run. Establishing the exact rule
   would require reading source, which is out of this report's permitted
   evidence — named here as an open question for later investigation, not
   resolved.
7. **Strict-mode (`-s`) error reporting's completeness across multiple
   violations was not fully exercised.** The sample fixture triggered
   exactly one undeclared-account error and one undeclared-commodity error
   before output stopped; whether every undeclared account/commodity
   instance (not just the first) would be reported in a fixture with more
   violations was not established by this evidence and should not be
   assumed either way.
8. **`-I` (ignore-assertions) was not actually exercised**, because the
   permitted fixture (`sample.journal`) contains no balance-assertion
   (`=`) syntax at all. Its observed output was byte-identical to the
   default run, which is consistent with "no-op because nothing to ignore"
   but does not confirm the flag's actual effect on an assertion-bearing
   file — that would require a different fixture, out of scope here.
9. **Package metadata inconsistency**: `pyproject.toml` version is
   `1.0.0.dev1` (a pre-release identifier) while its own classifiers claim
   `Development Status :: 5 - Production/Stable`. This is a direct,
   literal reading of the metadata, not an inference, and is a real
   current-state inconsistency regardless of what any roadmap or changelog
   elsewhere claims about project maturity.
10. **No per-command (`check --help`, `balance --help`, etc.) help text
    exists.** Every subcommand shares the single flat top-level `--help`
    output; there's no way to discover a command's own applicable-option
    subset except by cross-referencing the prose descriptions embedded in
    the shared help block (e.g. "`-1` ... stats only", "`-s` ...") since
    nothing in `--help`'s structure itself enforces which flags apply to
    which command.

## 6. What was explicitly not done (scope discipline)

- No `ledgerkit/*.py` source file was opened at any point in this
  reconstruction.
- No assertion, snapshot, implementation-comparison, dev-docs/planning,
  dev-docs/*.md, docs/*.md, knowledge/*.md, ROADMAP.md, CHANGELOG.md, or
  CONTEXT.md file was read.
- Every claim above is traceable to either the literal contents of
  `pyproject.toml` or the literal, exact stdout/stderr/exit-code of a
  command actually executed in this session against
  `tests/fixtures/sample.journal`. No behavior is asserted from a
  function/flag *name* alone; where a flag's real effect could not be
  observed on this fixture (`-I`), that is named as an open gap (item 8
  above) rather than assumed from its name/help text.

---
role: implementation-reconstructor
topic: reports-cli
dispatch-id: plan29-phase-reports-cli-20261003
dispatch-timestamp: 2026-10-03T00:00:00Z
date: 2026-10-03
---

# As-built reconstruction: reports-cli

Scope as dispatched: Ledgerkit's report-generation logic and CLI command
layer (`balance`, `register`, `stats`, `print`, plus `accounts` and `check`,
which share the same CLI machinery and are unavoidably visible while
reading `cli.py`).

Evidence base (every claim below is either a direct read of the named file,
a real command executed in this session, or a test body read directly —
never inferred from a name/docstring alone):

- `/home/cormac/projects/ledgerkit/ledgerkit/cli.py` (full file, 509 lines)
- `/home/cormac/projects/ledgerkit/ledgerkit/reports.py` (full file, 697 lines)
- `/home/cormac/projects/ledgerkit/ledgerkit/writer.py` (full file, 98 lines)
- `/home/cormac/projects/ledgerkit/tests/test_cli/test_cli.py` (full file, 643 lines)
- `/home/cormac/projects/ledgerkit/tests/test_reports.py` (full file, 1600 lines)
- `/home/cormac/projects/ledgerkit/tests/test_writer.py` (full file, 207 lines)
- Live commands: `python -m ledgerkit --help`, `--version`, and real
  invocations of `balance`/`register`/`accounts`/`print`/`stats`/`check`
  against `tests/fixtures/*.journal` and two constructed fixtures in the
  scratchpad directory (one with inline comments, one with an elided
  posting), transcribed verbatim below.

Note on scope boundary honoured: `ledgerkit/models.py` and `ledgerkit/
checks.py` are NOT in the permitted evidence paths for this dispatch and
were not read. Everywhere this report states a data-model field (e.g.
`BalanceRow.depth`, `RegisterRow.running_balance`, `Query.account`), that
is inferred only from how `reports.py`/`cli.py`/the permitted tests
construct and consume those objects — not from reading the dataclass
definitions themselves. This is flagged explicitly wherever it matters,
per the brief's evidence-boundary rule.

---

## 1. Structure

Two production modules are in scope, plus one adjacent module (`writer.py`)
used only as a comparison point for `print`:

- **`ledgerkit/cli.py`** (509 lines) — argument parsing (`_build_parser`),
  file-resolution (`_resolve_files`), and `main()`, which: loads/merges
  journals, builds the commodity-style map, parses `-q`, runs the
  mandatory basic-check gate (and optional strict-check gate), then
  dispatches to one of six command branches (`balance`, `register`,
  `accounts`, `print`, `stats`, `check`) and formats/prints the result
  itself. All output formatting (amount formatting, column alignment,
  ANSI colouring, account abbreviation) lives in `cli.py`, not in
  `reports.py` — confirmed by the module's own docstring ("Formatting is
  handled by cli.py") and by `reports.py` returning only structured data
  (dicts, dataclasses, `Mapping`/`Sequence` wrappers).
- **`ledgerkit/reports.py`** (697 lines) — pure report computation:
  `accounts()`, `balance()`, `register()`, `stats()`, `balance_from_spec()`,
  plus three "transparent result wrapper" classes (`BalanceResult`,
  `RegisterResult`, `AccountsResult`) that behave like the plain
  dict/list they wrap but additionally expose `.to_dataframe()` (pandas,
  optional — `ledgerkit._pandas_compat.require_pandas()`, not in scope).
  `JournalStats` is a plain `@dataclass` (no wrapper). Private helpers:
  `_matches_pattern`, `_effective_depth_spec`, `_aggregate_posting_amounts`,
  `_build_balance_tree`.
- **`ledgerkit/writer.py`** (98 lines) — a self-contained serialiser
  (`transaction_to_text`, `journal_to_text`) with its own independent
  amount formatter (`_fmt_amount`, module-private to `writer.py`, distinct
  from `cli.py`'s own module-private `_fmt_amount` of the same name — see
  §5 for the behavioural divergence this causes).

## 2. Public surface (confirmed via `--help` and real invocation)

Live `python -m ledgerkit --help` output (verbatim):

```
usage: ledgerkit [-h] [--version] [-v] [-1] [-o FILE] [-f FILE] [-s] [-I]
                 [-q TERMS] [-c STYLE]
                 {balance,register,accounts,print,stats,check} [journal ...]

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

`python -m ledgerkit --version` → `ledgerkit 1.0.0.dev1`.

Command set: `COMMANDS = ("balance", "register", "accounts", "print",
"stats", "check")` — a module-level tuple in `cli.py`, used both as
argparse `choices` and as the dispatch switch in `main()`.

An unrecognised command name (`ledgerkit frobnicate ...`) is rejected by
argparse itself before `main()`'s own logic runs, with exit code **2**
(not 1) — confirmed live:
```
ledgerkit: error: argument command: invalid choice: 'frobnicate' (choose from balance, register, accounts, print, stats, check)
```

`main(argv: list[str] | None = None) -> int` is the sole public entry point
(wired via `pyproject.toml`, per the module docstring — not independently
re-verified here as `pyproject.toml` is outside this dispatch's evidence
paths); it never raises on the documented error paths, always returning
0 or 1 (argparse's own `SystemExit(2)` for malformed CLI args is the one
exception, uncaught by `main()`).

### `reports.py` public functions (signatures read directly)

```python
def accounts(journal, query=None, _query_ast=None, _query_depth=None) -> list[str]
def balance(journal, query=None, tree=False, _query_ast=None, _query_depth=None) -> dict[str, dict[str, Decimal]] | list[BalanceRow]
def register(journal, query=None, _query_ast=None, _query_depth=None) -> list[RegisterRow]
def stats(journal, query=None, _query_ast=None, _query_depth=None) -> JournalStats
def balance_from_spec(journal, spec, query=None) -> list[ReportSectionResult]
```

The `_query_ast`/`_query_depth` parameters are explicitly documented in
their own docstrings as "Private, internal-only... Not part of the stable
public API" (citing `knowledge/DECISIONS.md`, which this dispatch did not
read — the citation itself is primary evidence of the function's own
stated scope, not a claim this report independently verifies against that
file).

## 3. Data model (as observed through usage, not through `models.py` itself)

Not read directly (out of permitted scope); every field below is inferred
solely from construction/attribute-access sites in `reports.py`, `cli.py`,
and the permitted test files:

- **`JournalStats`** (the one dataclass actually defined *inside*
  `reports.py`, fully read): `source_file: str | None`, `included_files:
  int`, `transaction_count: int`, `date_range: tuple[date, date] | None`,
  `last_txn_date: date | None`, `last_txn_days_ago: int | None`,
  `txns_span_days: int | None`, `txns_per_day: float`,
  `txns_last_30_days: int`, `txns_per_day_last_30: float`,
  `txns_last_7_days: int`, `txns_per_day_last_7: float`, `payee_count:
  int`, `account_count: int`, `account_depth: int`, `commodity_count:
  int`, `commodities: list[str]`, `price_count: int`. Its own docstring
  states it "Contains only deterministic journal data" — elapsed-time/
  txns-per-second are computed and formatted entirely in `cli.py`.
- **`BalanceRow`** (from `models`, used not defined here): constructed in
  `_build_balance_tree` as `BalanceRow(account=..., depth=...,
  amounts=dict[str, Decimal], is_subtotal=bool)` — `depth` is
  `account.count(":")` (colon count, i.e. 0 for a top-level account).
- **`RegisterRow`**: constructed in `register()` as `RegisterRow(date=...,
  description=..., account=..., amount=..., running_balance=...)`; `.amount`
  is itself an `Amount`-like object exposing `.quantity` (Decimal) and
  `.commodity` (str), used directly by `cli.py` (`row.amount.quantity`,
  `row.amount.commodity`).
- **`Query`**: constructed in tests as `Query(account=, not_account=,
  payee=, date_from=, date_to=, depth=)` — a flat filter dataclass; `.depth`
  is a plain `int | None` (legacy, pre-`DepthSpec` mechanism — see §5).
- **`ReportSpec`/`ReportSection`**: frozen dataclasses (`FrozenInstanceError`
  on mutation, confirmed by `test_frozen_report_section`/
  `test_frozen_report_spec`). `ReportSection(name, accounts=tuple[str,...],
  exclude=tuple[str,...]=(), depth=int|None, invert=bool=False)`.
  `ReportSpec(name, sections=tuple[ReportSection,...])`.
- **`ReportSectionResult`**: NOT frozen (`test_report_section_result_is_
  mutable` constructs one and mutates `.subtotal` without error) — fields
  observed: `section`, `rows: dict[str, Decimal]`, `subtotal: Decimal`,
  and a private `_commodity_styles` constructor kwarg.

## 4. Dependencies

`cli.py` imports, at module scope: `argparse`, `contextlib`, `os`, `sys`,
`time`, `decimal.Decimal`, `pathlib.Path`, and `ledgerkit.__version__`.
Everything else is imported lazily, inside `main()`, after argument
parsing: `ledgerkit.loader` (`load_journal`, `load_journal_stdin`,
`merge_journals`), `ledgerkit.models.Journal`, `ledgerkit.commodity_style.
CommodityStyle`, `ledgerkit.query` (`parse`, `QueryParseError`),
`ledgerkit.checks`, `ledgerkit.reports`, and — only inside the `print`
branch, only when a query is present — `ledgerkit.query.
matches_transaction`.

`reports.py` imports `ledgerkit.models` (several names), `ledgerkit.parser.
resolve_elision`, and five names from the `ledgerkit.query` subpackage:
`query.ast.QueryNode`, `query.depth.{DepthSpec, account_excluded_by_depth,
clip_account_name}`, `query.eval.{matches_posting, matches_transaction,
_matches_posting_for_accounts}`, `query.regex.compile_hledger_regex`.
Several functions additionally do a local `from ledgerkit.query.compat
import _query_to_ast` inside the function body (not at module scope).

`writer.py` imports only `ledgerkit.models` (`Amount`, `Journal`,
`Transaction`) and declares in its own docstring: "No file I/O; no imports
from parser, loader, checks, or cli" — confirmed true by the actual
import list.

No third-party imports appear in any of `cli.py`/`reports.py`/`writer.py`
at module scope (`to_dataframe()` methods on the `reports.py` wrapper
classes import `pandas` lazily and only on that call path, guarded by
`require_pandas()`).

## 5. Runtime behaviour (traced via real invocation and direct code reading)

### 5.1 Command dispatch and the mandatory check gate

Every command (including `check` itself) passes through, in order: file
resolution → journal load/merge → commodity-style map construction → `-q`
parse (if given) → **`_checks.run_basic_checks(journal, skip=...)`
unconditionally** → optional `_checks.run_strict_checks` if `-s`. Confirmed
live: `ledgerkit check -f assertions_fail.journal` (no check names) still
exits 1 with `"balance assertion failed..."`, because the unconditional
gate runs *before* `check`'s own explicit `run_checks(names=[])` call —
and `-I`/`--ignore-assertions` suppresses it (`ledgerkit -I check -f
assertions_fail.journal` exits 0). This means **every** report command
(`balance`/`register`/`accounts`/`print`/`stats`), not just `check`, fails
outright on a journal with a failing balance assertion unless `-I` is
passed — confirmed by `TestBalanceAssertions.test_failing_assertion_exits_
one` running `stats` (not `check`) against `assertions_fail.journal`.

### 5.2 `balance`

Flattens `reports.balance()`'s `dict[account, dict[commodity, Decimal]]`
to `(account, commodity, qty)` rows, sorted alphabetically by account then
commodity, omitting zero-quantity rows **except** a row whose account is
literally `"..."` (the depth-0 ellipsis bucket). Live confirmation,
`ledgerkit -q "depth:0" balance -f filtered.journal`:
```
                   0  ...
--------------------
                   0
```
— a bare `"0"` with no commodity symbol, for both the ellipsis row and the
grand total, exactly as the code comments describe. Negative amounts are
wrapped in ANSI red (`\033[31m...\033[0m`) before right-padding — code
comment in `cli.py` notes padding must happen first because escape codes
have non-zero string length but zero display width; this is correctly
implemented (padding computed via plain `f"{amt_str:>{col_w}}"`, colour
wrapped around the *already-padded* string). Column width
(`col_w`) is computed as `max([20] + [len of every formatted amount] +
[len of every total string])` — the list-literal form (not
`max(20, *gens)`) is explained in-code as necessary to avoid a `TypeError`
when both generators are empty (an all-zero-match `-q` filter) — confirmed
live, `ledgerkit -q "acct:doesnotexist" balance` exits 0 with a
separator + bare `"0"` total line, not an empty report or a crash.

### 5.3 `register`

Only the first posting of a transaction (by `(date, description)` key,
compared to the previous row) prints the date/description; continuation
rows leave those columns blank. Account names are abbreviated via
`_abbreviate_account` (colon-component shortening, first to 2 chars then
1 char, never the last component) before printing — confirmed live,
`equity:opening-balances` renders as `eq:opening-balances` in the
`register` output against `filtered.journal`. Amounts are right-aligned
to 12 chars, running balance to 13, both ANSI-red-wrapped when negative;
running balance of exactly zero prints as bare `"0"` (`_fmt_balance`).
Live output transcript (ANSI codes visible as raw escapes) confirms all
of the above against `tests/fixtures/filtered.journal`.

### 5.4 `print` — comment handling vs `writer.py` (the specific divergence this dispatch was asked to check)

**Confirmed live and by direct code reading: `print` drops every inline
comment — both transaction-header and posting-level — while `writer.py`'s
`journal_to_text`/`transaction_to_text` preserves them exactly, round-
tripping losslessly.**

Constructed fixture (`comment_test.journal`):
```
2024-01-01 * Coffee shop  ; business meeting
    expenses:food:coffee  £4.50  ; latte
    assets:bank:checking  -£4.50
```

`python -m ledgerkit print -f comment_test.journal`:
```
2024-01-01 * Coffee shop
    expenses:food:coffee                      £4.50
    assets:bank:checking                      £-4.50
```
(both `; business meeting` and `; latte` are gone — confirmed by direct
reading of `cli.py`'s `print` branch too: it builds the printed line from
`txn.date`/`flag`/`txn.description` and `posting.account`/`.amount` only;
`txn.inline_comment` and `posting.inline_comment` are never read anywhere
in the `print` branch.)

`writer.journal_to_text()` on the same loaded journal:
```
2024-01-01 * Coffee shop  ; business meeting
    expenses:food:coffee   £4.50  ; latte
    assets:bank:checking  -£4.50
```
— both comments present, matching `writer.py`'s own docstring guarantee
("same date, flag, description, postings, amounts, comments") and
`test_writer.py`'s own round-trip assertions (`test_inline_comment_header`,
`test_inline_comment_posting`, `test_roundtrip_with_flags_and_comments`).

A second, related divergence surfaced by the same experiment: **`cli.py`'s
`print` branch and `writer.py` use two independently-defined, same-named
`_fmt_amount` helpers with different negative-sign placement.** `cli.py`'s
version (shared by `balance`/`register`/`print`) renders a negative amount
as `"£-4.50"` (commodity symbol, then minus sign) — confirmed above and in
`TestBalanceOutput.test_amount_format_negative`'s own comment ("Commodity
precedes minus sign: £-5,000.00 not -£5,000.00"). `writer.py`'s version
renders the same value as `"-£4.50"` (minus sign, then commodity) —
confirmed by direct code reading (`writer._fmt_amount`: `return
f"-{sym}{-qty}"` for negative, non-alpha-initial commodities) and by
`test_writer.py`'s `test_simple_two_posting_transaction` asserting
`"-£2000.00"` literally. These are two separate, intentionally-distinct
formatters (journal-format round-trip text vs. CLI display text) — not a
bug by itself, but it means `print`'s on-screen output format is not
textually identical to what `writer.py` would (re-)serialise, beyond just
the missing comments.

A third divergence: `print` iterates `txn.postings` directly, not
`ledgerkit.parser.resolve_elision(txn)` (which `balance`/`register` both
use). Confirmed live: an elided posting (no explicit amount) prints with
**no amount at all** under `print` (just the account name on its own
line), while the same journal under `balance` shows the account with its
*inferred* amount (`£-1200.00`) from `resolve_elision`. `print` also never
colourises negative amounts (no `_ANSI_RED` usage anywhere in the `print`
branch), unlike `balance`/`register`.

`print` applies `-q`'s selection predicate (`query_ast`) at the whole-
transaction level via `ledgerkit.query.matches_transaction` — confirmed
by `TestQueryFlag.test_print_query_filters_whole_transactions` (a matching
posting pulls in the *entire* transaction, all postings, not just the
matching one) — but, per an explicit in-code comment, **`print` never
consults `query_depth` at all**, "matching hledger's own print (which
ignores depth: entirely)". Confirmed live: `ledgerkit -q "depth:1" print`
produces output identical to unfiltered `print`, including full unclipped
account names (`TestQueryFlag.test_print_ignores_depth_entirely`, and
reproduced live in this session).

### 5.5 `stats`

Deterministic fields come from `reports.stats()` (`JournalStats`);
elapsed time and txns/s are computed in `cli.py` itself from
`_PROGRAM_START` (captured at module import time, "as early as possible
so elapsed time includes import overhead" per the module docstring).
`-v`/`--verbose` only affects the `Commodities` line (appends the sorted
commodity list in parens) — confirmed live (`-v stats` → `Commodities :
1 (£)` vs plain `stats` → `Commodities : 1`). `-1` switches to a single
tab-separated line: version, source file (or `"(none)"`), elapsed string,
txns/s string — confirmed live:
```
1.0.0.dev1	/home/.../filtered.journal	0.02 s elapsed	247 txns/s
```
`stats` is the one report function where `_query_depth` **excludes**
accounts deeper than the limit from `account_count`/`account_depth`
(via `account_excluded_by_depth`), rather than clipping/aggregating them
the way `balance`/`register`/`accounts` do via `clip_account_name` — this
divergence is both stated explicitly in `stats()`'s own docstring (citing
a source comment in hledger's own `Ledger.hs`, which this dispatch did
not independently verify) and confirmed live: `ledgerkit -q "depth:2"
stats -f filtered.journal` reports `"Accounts : 2 (depth 2)"`, i.e. 2
accounts at or under depth 2, not the clipped-and-rolled-up count
`balance`/`accounts` would produce for the same `depth:2`.

### 5.6 `accounts`

Not named in the bounded topic's command list but structurally
inseparable from `cli.py`/`reports.py`'s shared machinery. Confirmed live:
plain listing, one account per line, sorted; no separator/zero-total
convention when empty (confirmed both live and by
`TestQueryFlag.test_multi_term_query`'s own comment: "accounts' CLI
output has no separator/zero-total convention (unlike balance) --
genuinely empty here").

### 5.7 `-o`/`--output-file`

Confirmed live: redirects stdout for the duration of the command body via
`contextlib.redirect_stdout`; file is always closed in a `finally` block
regardless of success/failure.

### 5.8 Commodity style override (`-c`/`--commodity-style`)

Confirmed live (`-c '$1,000.00' balance -f multicommodity.journal` ran
without error); full override-parsing logic lives in `ledgerkit.
commodity_style.CommodityStyle.parse_style_override`, which is outside
this dispatch's permitted evidence paths — `cli.py` itself only calls it
and reports a `ValueError` as `"ledgerkit: invalid -c value ...: ..."`
(exit 1) on failure; the override's own formatting semantics were not
independently re-verified here.

## 6. Tests (bodies read directly, not names)

- `tests/test_cli/test_cli.py` (643 lines): unit tests for
  `_resolve_files`'s four-tier precedence (`-f` > positional > `$LEDGER_FILE`
  > `~/.hledger.journal`) and its two `SystemExit(1)` error paths;
  integration tests for `-f`/multi-file merge, stdin (`-f -`), balance
  assertion gating + `-I`, and an extensive `-q`/`--query` suite covering
  all five query-aware commands, `depth:` clipping-vs-excluding-vs-ignoring
  across commands, tag queries, and several explicit malformed-query /
  excluded-regex-construct exit-1 cases. Notably, several tests assert
  *negative* space — e.g. `test_no_match_query_exits_zero` explicitly
  documents (in its own comment) that this is "a real, pre-existing CLI
  defect this phase's differential testing surfaced and fixed", i.e. the
  current behaviour (print a `0` total line on a non-matching `-q` filter,
  rather than nothing) was itself a historical bug fix, not original
  design.
- `tests/test_reports.py` (1600 lines): the larger suite — exhaustively
  covers `accounts`/`balance`/`register`/`stats`/`balance_from_spec`
  against `filtered.journal` and `multicommodity.journal`, the `_query_ast`/
  `_query_depth` private integration surface, `tag:` query precedence
  across four/five/six distinct tag sources (`tags.journal`), the retired
  `_posting_matches` helper's absence (grep-style static check across the
  whole `ledgerkit` package), the deprecated `Journal.balance(accounts=
  [...])`/`.register(accounts=[...])` shim's zero/one/many-account cases,
  and `Query`'s "Option A" `HledgerRegex` strictness (excluded constructs
  now raise `QueryParseError` rather than silently matching or erroring
  differently than `-q`'s own parser). Many tests directly assert
  cross-function parity, e.g. `Journal.balance()` producing an identical
  result to `reports.balance()` called directly.
- `tests/test_writer.py` (207 lines): asserts `transaction_to_text`'s
  header-line construction (flags, code, description, inline comment),
  elided-posting line format (bare account, no amount), inline comments on
  both header and postings, right-edge amount alignment (asserts both
  posting lines in a two-posting transaction end at the same string
  length), multi-commodity rendering, and three explicit round-trip tests
  (`parse_string(transaction_to_text(txn))` reproduces date/description/
  postings/amounts, flags, and comments). `journal_to_text` tests check
  empty-journal output (`"\n"`), exactly-one-blank-line separation between
  transactions, and transaction-count-preserving round-trip against
  `sample.journal`.

## 7. Limitations / gaps (named honestly, not glossed over)

1. **`print` drops all inline comments** (transaction-header and
   posting-level), unlike `writer.py`'s `journal_to_text`, which preserves
   them exactly in a lossless round trip. This is the specific divergence
   this dispatch was asked to check, and it is real and reproducible (see
   §5.4). There is no in-code comment in `cli.py` acknowledging this as a
   deliberate simplification; `print`'s own branch simply never reads
   `txn.inline_comment`/`posting.inline_comment`.
2. **`print` and `writer.py` use two independently-defined, differently-
   behaving `_fmt_amount` functions** (different negative-sign placement:
   `"£-4.50"` vs `"-£4.50"`) — confirmed live and by direct reading of both
   definitions. `print`'s on-screen text is therefore not simply
   "`journal_to_text` minus comments"; it is a genuinely separate
   formatting path.
3. **`print` does not resolve elided postings** — it iterates raw
   `txn.postings`, not `ledgerkit.parser.resolve_elision(txn)`, so an
   elided posting prints with no amount at all, while the same posting
   under `balance`/`register` (which do call `resolve_elision`) shows its
   inferred amount. Confirmed live in §5.4.
4. **`print` never colourises negative amounts** (no ANSI-red usage in
   that branch), unlike `balance`/`register`, which both wrap negative
   amounts in `\033[31m...\033[0m`. A cosmetic but real inconsistency
   across the three formatting-heavy commands.
5. **`print` deliberately ignores `depth:` entirely** (confirmed by an
   explicit in-code comment and live reproduction) — this is presented in
   the code as an intentional match to hledger's own `print` semantics,
   not a gap, but it is a genuine behavioural asymmetry versus
   `balance`/`register`/`accounts`/`stats`, which are all depth-aware in
   one of two different ways (clip-and-aggregate vs. exclude — see
   limitation 6).
6. **Depth semantics are not uniform across commands** — `balance`/
   `register`/`accounts` clip and roll up account names at the given
   depth (never excluding a posting/account), while `stats` *excludes*
   accounts deeper than the limit from `account_count`/`account_depth`.
   This is documented in-code as a deliberate, source-confirmed exception
   for `stats`, not an oversight, but it is a real asymmetry a caller must
   know about; this report did not independently verify the cited
   hledger source-comment claim (`Ledger.hs`), only that the code and its
   own tests are internally consistent with the claim.
7. **Two parallel filter mechanisms coexist in every `reports.py`
   function**: a legacy `Query` dataclass (`query=`) and an internal-only
   `_query_ast`/`_query_depth` pair (from the CLI's `-q` flag), explicitly
   documented in multiple docstrings as "Not part of the stable public
   API" and AND-combined when both are supplied. `accounts()` additionally
   uses a narrower, command-specific tag-visibility mode
   (`_matches_posting_for_accounts`) solely for `_query_ast` `Tag` nodes —
   not for the legacy `query` field at all (which has no tag concept).
   This is multiple overlapping code paths for what is conceptually one
   filtering operation, confirmed by direct reading, not asserted as a
   defect by this report.
8. **`balance_from_spec`'s per-section `accounts=`/`exclude=` patterns
   remain on the separate, older `_matches_pattern`/`compile_hledger_regex`
   path**, never routed through the same `Query`→AST translation the
   *outer* query on the same function now uses (that outer query *was*
   converged, per the in-code "Stage C Phase 8" comments) — a real,
   named, deliberate asymmetry within a single function, not a bug this
   report is asserting, but a structural inconsistency worth flagging.
9. **`check` with zero explicit check names still exits 0** without
   running any of the registered checks by name (confirmed live against
   `assertions_pass.journal`) — but the *unconditional* basic-check gate
   that runs before every command (including `check`) still applies
   unless `-I` is passed, so `check` with no names is not equivalent to
   "skip all checking"; it is "skip only the checks you'd otherwise name
   explicitly." This two-layer check structure (an always-on gate, plus an
   optional explicit, nameable second pass) could easily be misread as
   "the `check` command controls all checking," which it does not. (Note:
   `run_checks`'s own semantics for an empty `names` list were inferred
   from this live behaviour and from `cli.py`'s call site only;
   `ledgerkit/checks.py` itself is out of this dispatch's permitted scope
   and was not read.)
10. **Data-model fields (`BalanceRow`, `RegisterRow`, `Query`,
    `ReportSectionResult`, etc.) were never read from their own
    definitions** (`ledgerkit/models.py` is excluded from this dispatch's
    evidence paths) — every field name/type claim above is inferred
    solely from construction/attribute-access call sites in `reports.py`,
    `cli.py`, and the permitted tests. This is an evidence-boundary
    limitation of this report, not a code limitation, and should be
    treated as lower-confidence than the rest of this report wherever it
    appears.
11. **An unrecognised CLI command exits with code 2, not 1** (argparse's
    own validation, before `main()`'s own try/except logic ever runs) —
    a minor inconsistency with every other documented error path in this
    report, which uniformly uses exit code 1.

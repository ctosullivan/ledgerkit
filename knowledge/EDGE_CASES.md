# Edge Cases

Human-identified cases that are non-obvious or would be easy to regress. Each entry records what the expected behaviour is and whether it is currently handled.

---

## EC-016 — `balance` CLI output for a query matching zero postings

**Trigger:** `-q`/`--query` (or, in principle, any future `-a`-style filter)
narrows `balance`'s result to zero matching postings.
**Expected behaviour:** Print a separator line and a bare `0` total line
(matching real hledger's own `balance` output for a zero-match query,
confirmed by differential test against the pinned hledger 1.52.4 binary,
Stage C Phase 2). Exit 0 — a zero-match query is not an error.
**Found:** This was unreachable from the CLI before the `-q` flag existed
(no prior CLI mechanism could make `balance` see zero matching postings
against a real journal), so the gap was latent. Two bugs, found together
via differential testing: (1) `cli.py`'s `balance` branch printed nothing
at all for zero matching lines instead of the separator+`0`; (2) fixing
(1) exposed a second, real crash bug — `max(20, *(empty gen), *(empty
gen))` degenerates to `max(20)`, a single non-iterable argument, which
Python's `max()` raises `TypeError` on (`'int' object is not iterable`)
rather than treating as "the sole candidate value 20". Both fixed in the
same phase.
**Status:** Handled ✓ (`tests/test_cli/test_cli.py::TestQueryFlag::
test_no_match_query_exits_zero`). Fix: always compute/print the totals
block (removed the `if not lines: pass` short-circuit); `col_w` computed
via `max([20] + [...] + [...])` (a single list argument) instead of
`max(20, *gen, *gen)`.

## EC-017 — `-q "depth:N"` does not truncate/aggregate `balance` output like hledger's own `depth:`/`--depth`

**RESOLVED Stage C Phase 5 (2026-09-17):** `depth:`/`depth:REGEX=N` no
longer produces a `QueryNode` at all — it's a `ledgerkit.query.depth.
DepthSpec` report-display option (`QueryPlan.depth`), applied via
clipping/aggregation across `balance`/`register`/`accounts`, matching
hledger exactly (including custom `REGEX=N` depths and multi-term
precedence, which didn't exist before this phase at all). `print` now
correctly ignores `depth:` entirely (previously it wrongly excluded
everything — a confirmed defect, not just the "open question" this entry
originally left it as). See `LK-COMPAT-QUERY-DEPTH-001` (reclassified
`compatible`) and `dev-docs/planning/core-redefinition/
21-stage-c-phase-5-depth-and-verification-plan.md`. One claim in the
original entry below turned out to be wrong and is corrected here rather
than silently: "the existing `Query.depth` field... still does the
truncation hledger users expect for `balance`" was true only for
`balance()` — `register()`/`accounts()` had the *same* exclusion bug via
`Query.depth` all along (a real, independent, pre-existing defect this
phase also found and fixed, not just the new `-q` `depth:` divergence).

**Original entry (kept for history):**

**Trigger:** `ledgerkit balance -q "depth:N"`, compared against `hledger
balance depth:N` / `hledger balance --depth N` on the same journal.
**Expected vs actual:** hledger's `depth:`/`--depth` **truncates and
rolls up** deeper accounts into their depth-N ancestor, still showing
aggregated totals (e.g. `depth:1` on a journal with `expenses:food` and
`expenses:housing` shows one `expenses` row summing both). Ledgerkit's
`ledgerkit.query.ast.Depth` (via `-q`) is a pure **exclusion** predicate —
`accountNameLevel(account) <= N` — so a posting deeper than N is dropped
entirely, not rolled up; `-q "depth:1"` against a journal with no
depth-1-or-shallower postings returns **zero rows**, not aggregated
totals. Confirmed via live differential test against the pinned hledger
1.52.4 binary, Stage C Phase 2 (`hledger -f filtered.journal balance
--depth 1` shows 4 aggregated rows; `ledgerkit -f filtered.journal
balance -q "depth:1"` shows none).
**Why this is intentional, not a bug:** `17-query-semantics-brief.md` §4
scoped this deliberately — "recommend Stage C treat `depth:N` strictly as
the `QueryAST` boolean predicate... depth-driven display truncation/
aggregation for `balance`/`register` is separate report-layer work, not
something the `QueryAST` evaluator itself should attempt (it isn't a pure
predicate — it changes what account name gets displayed)." The existing
`Query.depth` field (used without `-q`) still does the truncation hledger
users expect for `balance` — this gap is specific to the new `-q`
flag's `depth:` term, not a regression in existing behaviour.
**Status:** Documented, not fixed — `LK-DIV-QUERY-DEPTH-001` (compat-
register), `dev-docs/hledger-compatibility.md`'s Query Language section,
and `docs/usage.md` all carry this caveat explicitly so a user reaching
for `-q "depth:N"` on `balance` isn't surprised. Fixing it (making `-q
depth:N` truncate for `balance` specifically) is a real follow-on
candidate, not attempted this phase (would require `-q`'s depth handling
to interact with `balance`'s existing truncation logic in a report-
specific way the plan's own scope explicitly deferred).

---

## EC-001 — `end comment` outside a block comment

**Trigger:** `end comment` appears in a file with no preceding `comment` directive.
**Expected behaviour:** Silently ignored. Does not raise `ParseError`.
**Source:** Identified during block-comment implementation, 2026-04-xx.
**Status:** Handled ✓ (`test_end_comment_outside_block_silently_ignored`)

---

## EC-002 — Two elided amounts in one transaction block

**Trigger:** A transaction has two postings with no amount (no `  £X.XX` suffix).
**Expected behaviour:** Raises `ParseError` with message containing "at most one elided amount".
**Source:** hledger spec — only one posting per block may have its amount inferred.
**Status:** Handled ✓ (`test_two_elided_raises`)

---

## EC-003 — Posting line outside a transaction block

**Trigger:** An indented posting-like line appears before any transaction header.
**Expected behaviour:** Raises `ParseError` with message containing "outside a transaction block".
**Note:** Non-indented lines outside a block are silently skipped; only indented lines trigger the error.
**Status:** Handled ✓ (`test_posting_outside_block_raises`)

---

## EC-004 — Year-omitted date with no `default_year`

**Trigger:** A date like `1/31` or `03-15` is parsed without passing `default_year` to `parse_string`.
**Expected behaviour:** The current calendar year (`datetime.date.today().year`) is used.
**Source:** hledger simple-date spec.
**Status:** Handled ✓ (`test_year_omitted_defaults_to_current_year`)

---

## EC-005 — Unclosed block comment runs to end of file

**Trigger:** A `comment` directive with no matching `end comment` before EOF.
**Expected behaviour:** All content after `comment` is silently consumed. No error raised.
**Source:** hledger spec — unclosed comment blocks are not an error.
**Status:** Handled ✓ (`test_unclosed_block_comment_runs_to_eof`)

---

## EC-006 — `include` glob matches no files

**Trigger:** `include *.journal` in a directory with no `.journal` files.
**Expected behaviour:** Silently produces no entries (no error).
**Note:** Contrasted with explicit non-glob paths, which raise `FileNotFoundError` if missing.
**Status:** Handled ✓ (loader.py glob branch)

---

## EC-007 — Circular `include` detection

**Trigger:** File A includes File B which includes File A (directly or transitively).
**Expected behaviour:** `ParseError` raised identifying the circular reference. Does not infinite-loop.
**Status:** Handled ✓ (loader.py `seen` set)

---

## EC-008 — `decimal-mark ,` followed by period-decimal amount

**Trigger:** After `decimal-mark ,`, a posting uses period as decimal separator (e.g. `£30.00`).
**Expected behaviour:** `ParseError` — the amount does not match the active `_AMOUNT_COMMA` pattern.
**Note:** The directive switches the parser mode for all subsequent postings; mixing formats in one file is invalid.
**Status:** Handled ✓ (parser rejects non-matching amounts)

---

## EC-009 — `P` directive with inline `;` or `#` comment

**Trigger:** `P 2024-01-01 € $1.35  ; ECB rate` or `P 2024-01-01 € $1.35  # ECB rate`.
**Expected behaviour:** Comment stripped; price parsed as `$1.35`.
**Status:** Handled ✓ (`test_p_directive_semicolon_comment_stripped`, `test_p_directive_hash_comment_stripped`)

---

## EC-010 — Thousands-separator comma in amount

**Trigger:** Posting amount written as `£1,234.56`.
**Expected behaviour:** Parsed as `Decimal("1234.56")` with commodity `"£"`.
**Note:** The comma is a thousands separator, not a decimal mark. Only valid in default (period-decimal) mode.
**Status:** Handled ✓ (`test_thousands_comma`)

---

## EC-011 — `account` / `payee` / `commodity` directives with trailing `;` or `#` comments

**Trigger:** `account assets:bank  ; checking` or `commodity $  # US dollar`.
**Expected behaviour:** Comment stripped; only the account/payee/commodity name stored.
**Status:** Handled ✓ (all directive handlers call `_strip_directive_comment`)

---

## EC-012 — Two consecutive transactions with identical date and description in `register`

**Trigger:** Two separate transactions share the same `date` and `description` (e.g., two
salary postings on the same day with the same payee string).
**Expected behaviour (hledger):** Each transaction starts a new block in the register view;
the second transaction's first posting shows the date and description.
**Actual behaviour (ledgerkit CLI):** The continuation-row detection key is `(date, description)`,
so the second transaction's first posting is silently treated as a continuation row of the
first — the date and description are blanked.
**Status:** Known limitation — not handled. The `RegisterRow` dataclass does not carry a
transaction identity field, so the CLI cannot distinguish the boundary without a deeper change.
**Workaround:** None currently. A future fix would either add a transaction ID/index to
`RegisterRow`, or pass grouped rows from `register()`.
**Source:** Identified during register CLI formatting work, 2026-05-02.

---

## EC-014 — Column-0 `;` between two adjacent transactions (no blank line)

**Trigger:** A `;` at column 0 appears between the last posting of one transaction and the header of the next, with no blank line separating them.

```
2024-01-01 First
    a  £10
    b  -£10
; this comment has no blank lines around it
2024-01-02 Second
    a  £20
    b  -£20
```

**Previous (buggy) behaviour:** The parser's `lstrip()` call stripped all leading whitespace before checking for `;`, so it could not distinguish column-0 from indented comment lines. When `current_txn` was open, the column-0 `;` was incorrectly captured as a follow-on posting comment for `b`, polluting `b.inline_comment`.

**Expected behaviour:** The column-0 `;` is a top-level comment and must be silently discarded. Neither transaction's comment fields should contain anything; `source_span.end_line` for `First` should be line 3 (the `b` posting), not line 4 (the `;` line).

**Fix:** Added `is_indented = line[0:1].isspace()` before the `lstrip()` check in `_parse_string_impl`. Comment capture is now gated on `current_txn is not None and is_indented`.

**Status:** Handled ✓ (`test_T06_semicolon_between_txns_no_blank_line`, `test_F07_noindent_semicolon_inside_txn_not_captured`, `test_S02_noindent_semicolon_does_not_extend_span`)

---

## EC-013 — Trailing decimal point with no fractional digits (`$1,350,000.`)

**Trigger:** Posting amount with a decimal mark but no following digits, e.g. `$1,350,000.` or `1.234, EUR` (comma-decimal mode).
**Expected behaviour:** hledger accepts this as valid; parsed as the integer quantity (`Decimal("1350000")`).
**Previous behaviour (ledgerkit):** `ParseError: invalid amount` — regex required `\d+` after the decimal point.
**Fix:** Changed `(?:\.\d+)?` → `(?:\.\d*)?` in `_AMOUNT`; `(?:,\d+)?` → `(?:,\d*)?` in `_AMOUNT_COMMA`. Python's `Decimal("1350000.")` is valid and equals `Decimal("1350000")`.
**Status:** Handled ✓ (`test_trailing_decimal_period`, `test_trailing_decimal_comma_mode`)

---

## EC-015 — Lot annotation stripping must not consume virtual posting account names

**Trigger:** A posting whose account name is written in parentheses or square brackets (virtual posting syntax), e.g. `(expenses:food)` or `[expenses:food]`. These look superficially similar to lot annotation labels `(lot1)` and lot-date brackets `[2024-01-01]`.

**Expected behaviour:** Virtual posting account names must NEVER be fed into `_parse_amount`. The posting account is parsed by `_parse_posting` as the text before the two-space separator; `_parse_amount` only sees the text AFTER the separator. Since the virtual-posting parentheses/brackets are part of the account name (before the separator), they are never present in the string passed to `_strip_lot_annotations`.

**Why it matters:** If the lot-annotation stripper were to run on the full posting line rather than only on the amount substring, it would incorrectly consume `(expenses:food)` as a lot label, leaving no account name.

**Status:** Non-issue by construction ✓ — `_parse_posting` extracts the account and amount substrings independently before calling `_parse_amount`. Added here to document the invariant explicitly so future refactors do not accidentally feed the full posting line into the lot stripper.

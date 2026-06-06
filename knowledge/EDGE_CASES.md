# Edge Cases

Human-identified cases that are non-obvious or would be easy to regress. Each entry records what the expected behaviour is and whether it is currently handled.

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

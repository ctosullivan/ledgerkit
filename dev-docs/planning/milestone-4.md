# Milestone 4 Implementation Plan — Comprehensive Format Compatibility

**Goal:** `parse_string_lenient` returns zero errors on the two comprehensive
test fixtures. `python -m ledgerkit check` exits 0.

**Fixtures:**
- `tests/fixtures/comprehensive-hledger-test.journal`
- `tests/fixtures/comprehensive-hledger-test-commodities.journal`

**Parse errors identified (23 total across 10 root causes):**

| # | Root Cause | Count | Representative error |
|---|---|---|---|
| 1 | Sign after prefix symbol (`$-300`) | 10 | `invalid amount: '$-300'` |
| 2 | Cost annotations not stripped (`@ $180`, `@@ $920`) | 3 | `invalid amount: '10 AAPL @ $180.00'` |
| 3 | Lot annotations not stripped (`{$182}`, `{{$370}}`) | 2 | `invalid amount: '3 AAPL {$182.00} [2024-01-18] (lot-A)'` |
| 4 | `~`/`=` rule blocks — postings orphaned | 2 | `posting found outside a transaction block` |
| 5 | Quoted commodity suffix in amount | 1 | `invalid amount: '-3 "Chocolate Frogs"'` |
| 6 | Space digit-group separator | 1 | `invalid amount: '1 000 000 JPY'` |
| 7 | Scientific E-notation | 1 | `invalid amount: '1E3 EUR'` |
| 8 | Secondary date not recognised (`DATE=DATE2`) | 1 | `posting found outside a transaction block` (line 212) |
| 9 | `D` directive not implemented | 1 | `amount has no commodity symbol: '2.00'` |
| 10 | Quoted commodity in `commodity` directive | 1 | `commodity directive: cannot parse symbol from '1,000. "Chocolate Frogs"'` |

Root cause 10 is triggered by the included commodities file; it surfaces before
the main file's 22 errors when running `ledgerkit check`.

---

## TODO — Implementation Progress

- [ ] Phase 1 — models.py prerequisites (Transaction.date2, Posting.cost_raw)
- [ ] Phase 1b — _ParseContext dataclass in parser.py
- [ ] Phase 2a — Amount parser A1–A3 (sign, cost annotations, lot annotations)
- [ ] Phase 2b — Amount parser A4–A6, D1 (quoted suffix, space separator, E-notation, commodity directive)
- [ ] Phase 3a — Secondary date (B1)
- [ ] Phase 3b/c — Skip ~ and = rule blocks (C4, C5)
- [ ] Phase 3d/e/f — Y, D, apply account directives (C1, C2, C3)
- [ ] Phase 4 — Tests
- [ ] Phase 5 — Documentation

> **Updating this TODO:** At the end of each phase, once all checkpoint commands
> pass and no new test failures are introduced, mark the corresponding item `[x]`.
> Do not mark a phase complete until `python -m unittest discover -s tests -t . -v`
> passes in full. If a phase is partially complete at the end of a session, add a
> `(partial)` note inline rather than ticking the box.

---

## Session Implementation Strategy

The changes map to **7 sequential phases** (including sub-phases). Each phase is
confined to one code area, ends with a verifiable checkpoint, and leaves the repo
in a working state. Complete phases in order — do not skip ahead.

### Overview

| Phase | Scope | Spec sections | Errors fixed | After |
|---|---|---|---|---|
| 1 | `models.py` — Transaction.date2, Posting.cost_raw | E1–E2 | 0 (prerequisite) | 23 remain |
| 1b | `parser.py` — _ParseContext dataclass | — | 0 (prerequisite) | 23 remain |
| 2a | `parser.py` — Amount parser (sign, cost, lot) | A1–A3 | 15 | 8 remain |
| 2b | `parser.py` — Amount parser (quoted suffix, space, E-notation, directive) | A4–A6, D1 | 4 | 4 remain |
| 3 | `parser.py` — Header + directives | B1, C1–C5 | 4 | 0 remain |
| 4 | Tests | G | — | 505+ tests pass |
| 5 | Documentation + CHANGELOG | F | — | done |

---

### Phase 1 — `models.py` prerequisites (E1–E2)

**Do this first.** Phase 3 (B1 secondary date) assigns `Transaction.date2`; the
field must exist before parser.py is touched so there is no forward dependency.
Phase 2a (A2 cost annotation stripping) stores the raw annotation text on
`Posting.cost_raw`; that field must also exist before the parser is touched.

Two changes:
1. Add `date2: Optional[datetime.date] = None` to `Transaction` in `ledgerkit/models.py`.
2. Add `cost_raw: Optional[str] = None` to `Posting` in `ledgerkit/models.py`.

No other file changes needed.

**Checkpoint:**
```powershell
python -m unittest discover -s tests -t . -v
```
All 485 existing tests pass (new fields have defaults, no existing callsites break).

---

### Phase 1b — `_ParseContext` dataclass in `parser.py`

**Do before Phase 2.** Define a module-level internal dataclass in `parser.py` that
holds directive-accumulated parser state. This eliminates the need to thread multiple
individual parameters through the call chain in later phases.

```python
@dataclass
class _ParseContext:
    default_year: int
    decimal_mark: str
    default_commodity: Optional[str] = None
    account_prefix: Optional[str] = None
```

Replace individual parameter threading (`decimal_mark`, `default_commodity`, etc.)
through `_parse_string_impl`, `_parse_posting`, and `_parse_amount` with a single
`ctx: _ParseContext` argument. Spec sections that reference individual parameter
threading (e.g. A2, C2) should be read as "update `ctx.<field>` instead of
threading a new parameter."

This is an internal type (leading underscore) and does not affect the public API.

**Checkpoint:**
```powershell
python -m unittest discover -s tests -t . -v
```
All existing tests pass. (Phase 1b is a pure refactor with no behaviour change.)

---

### Phase 2a — Amount parser steps A1–A3

All changes inside `ledgerkit/parser.py`. Make them in the order below.

**Within-sub-session order:**

| Step | Section | Why this order |
|---|---|---|
| 2a-i | A1 — Mid-minus group in `_AMOUNT`/`_AMOUNT_COMMA` | Regex-only change; fixes 10 errors at once |
| 2a-ii | A2 — `_strip_cost_annotation` helper + call in `_parse_amount` | New helper; store annotation on Posting.cost_raw |
| 2a-iii | A3 — `_LOT_ANNOTATION_RE` + `_strip_lot_annotations` + call | New helper; runs after cost strip |

**Checkpoint — 8 errors remain:**
```powershell
python -c "
from ledgerkit.parser import parse_string_lenient
from pathlib import Path
text = Path('tests/fixtures/comprehensive-hledger-test.journal').read_text('utf-8')
_, errs = parse_string_lenient(text, source_file='comprehensive-hledger-test.journal')
print(len(errs), 'remaining:', [str(e) for e in errs])
"
```
Expected after this sub-session: **8 errors remain** — quoted suffix (×1),
space separator (×1), E-notation (×1), commodities directive (×1), `~`/`=`
orphan postings (×2), secondary-date orphan (×1), and no-symbol `2.00`
amount (×1).

---

### Phase 2b — Amount parser steps A4–A6, D1

All changes inside `ledgerkit/parser.py`. Continue from Phase 2a.

**Within-sub-session order:**

| Step | Section | Why this order |
|---|---|---|
| 2b-i | A6 — E-notation in `_AMOUNT`/`_AMOUNT_COMMA` | Regex-only change; lowest risk |
| 2b-ii | A4 — `_QUOTED_SUFFIX_RE` + quoted-suffix branch in `_parse_amount` | New regex path; checked before main regex |
| 2b-iii | A5 — `_SPACE_DIGIT_GROUP_RE` + `_normalise_space_separators` + call | Normalisation runs before quoted-suffix check |
| 2b-iv | D1 — `_TRAILING_QUOTED_COMMODITY_RE` + branch in `_extract_commodity_symbol` | Fixes commodities file pre-flight error |

All new module-level constants need the full regex doc comment (purpose / group
breakdown / edge cases) per CLAUDE.md.

**Checkpoint — 4 errors remain:**
```powershell
python -c "
from ledgerkit.parser import parse_string_lenient
from pathlib import Path
text = Path('tests/fixtures/comprehensive-hledger-test.journal').read_text('utf-8')
_, errs = parse_string_lenient(text, source_file='comprehensive-hledger-test.journal')
print(len(errs), 'remaining:', [str(e) for e in errs])
"
```
Expected after this sub-session: **4 errors remain** — the `~`/`=` orphan
postings (×2), the secondary-date orphan (×1), and the no-symbol `2.00`
amount (×1).

Also confirm the commodities file pre-flight is cleared:
```powershell
python -m ledgerkit check -f tests/fixtures/comprehensive-hledger-test-commodities.journal
# Should exit 0
```

---

### Phase 3 — Transaction header + directives (B1, C1–C5)

All changes inside `ledgerkit/parser.py`. Work top-to-bottom through
`_parse_string_impl`, inserting handlers at the placements described in the
corresponding spec sections.

**Within-phase order:**

| Step | Section | Placement in `_parse_string_impl` | Errors fixed |
|---|---|---|---|
| 3a | B1 — Secondary date | `_TXN_HEADER` regex + `_parse_txn_header` | 1 |
| 3b | C4 — Skip `~` rule blocks | Before transaction-header detection | 1 |
| 3c | C5 — Skip `=` auto-posting blocks | Immediately after C4 | 1 |
| 3d | C1 — `Y YEAR` directive | In directive-processing block | 0 (correctness) |
| 3e | C2 — `D AMOUNT` directive | After Y handler; update `ctx.default_commodity` | 1 |
| 3f | C3 — `apply account`/`end apply account` | After D handler | 0 (correctness) |

Steps 3d and 3f fix no counted errors (yearless dates use wrong year / wrong account
names without them) but are required for the fixture to produce correct data.

**Note on warnings:** C4 and C5 append `ParseWarning` instances to `errors_out`
in lenient mode when rule blocks are skipped. These are not counted against the
"0 errors" target. The checkpoint below filters them out; the gate test in G does
likewise.

**Checkpoint — zero parse errors:**
```powershell
python -c "
from ledgerkit.parser import parse_string_lenient, ParseWarning
from pathlib import Path
text = Path('tests/fixtures/comprehensive-hledger-test.journal').read_text('utf-8')
_, errs = parse_string_lenient(text, source_file='comprehensive-hledger-test.journal')
real_errors = [e for e in errs if not isinstance(e, ParseWarning)]
print(len(real_errors), 'errors,', len(errs) - len(real_errors), 'warnings')
assert not real_errors, [str(e) for e in real_errors]
print('PASS')
"
python -m ledgerkit check -f tests/fixtures/comprehensive-hledger-test.journal
echo "check exit: $LASTEXITCODE"
```
Expected: 0 parse errors (warnings from skipped rule blocks are allowed), `check` exits 0.

---

### Phase 4 — Tests (Section G)

Add all new test classes to `tests/test_parser/test_parser.py`. Write unit tests
for each error class first, then the gate test last so it acts as a final
integration check.

**Checkpoint:**
```powershell
python -m unittest discover -s tests -t . -v
```
Expected: 505+ tests, all pass.

---

### Phase 5 — Documentation (Section F)

Update all 7 doc files in a single response. Order within the response:
1. `dev-docs/api-spec.md` — new `Transaction.date2`, `Posting.cost_raw` fields + `default_commodity` params
2. `dev-docs/hledger-compatibility.md` — all new features added to tables
3. `knowledge/DOMAIN_RULES.md` — sign-placement rule
4. `knowledge/EDGE_CASES.md` — lot annotation isolation note
5. `CHANGELOG.md` — new `[Unreleased]` entry
6. `ROADMAP.md` — Milestone 4 `[PLANNED]` → `[IN PROGRESS]`
7. `CONTEXT.md` — overwrite with current task state

**Final checkpoint:**
```powershell
python -m unittest discover -s tests -t . -v
```
All tests still pass after doc-only changes.

---

## A. Amount Parser Fixes — `ledgerkit/parser.py` *(Phase 2a and 2b)*

All changes are in `_parse_amount()` and the regexes it calls.

### A1. Sign After Prefix Symbol (`$-300`)

**Problem:** The current `_AMOUNT` regex is:
```
^(-?)([^\d,.\s-]*)\s*([\d,]+(?:\.\d*)?)\s*([A-Za-z][A-Za-z0-9]*)?$
 g1   g2 prefix        g3 numeric            g4 suffix
```
Group 1 captures a leading minus BEFORE the symbol. `$-300` has `$` before the
minus, so group 1 matches empty, group 2 matches `$`, then `-300` fails because
`[\d,]+` requires a digit first.

**Fix:** Add an optional third group for a minus sign that may appear AFTER the
prefix symbol:

```
^(-?)([^\d,.\s-]*)(-?)\s*([\d,]+(?:\.\d*)?)\s*([A-Za-z][A-Za-z0-9]*)?$
 g1   g2 prefix    g3     g4 numeric             g5 suffix
```

In `_parse_amount`, combine groups 1 and 3:
```python
minus, prefix_sym, mid_minus, quantity_str, suffix_sym = m.groups()
negative = (minus == "-" or mid_minus == "-")
```

Apply the same change to `_AMOUNT_COMMA` (identical structure).

Update both regex doc comments: add group 3 description and new edge cases
(`$-300`, `£-10`, `€-5.00`).

**Regression risk:** Low. The added `(-?)` group is optional and zero-width; it
only activates when a `-` appears between symbol and digits. Existing tests for
`-$300` (leading minus) are unaffected because group 1 still captures that case.

---

### A2. Cost Annotations (`@ PRICE`, `@@ TOTAL`)

**Problem:** `_parse_amount` receives `10 AAPL @ $180.00` — the `@` and
everything after it cause the regex to fail.

**Fix:** Add a helper function `_strip_cost_annotation` that runs before the
main regex:

```python
# Strips a trailing @ or @@ cost annotation from an amount string.
#
# Purpose: remove "@ PRICE" (per-unit cost) and "@@ TOTAL" (total cost)
#          suffixes so the amount regex sees only the commodity quantity.
#          The annotation text is returned separately for storage on Posting.cost_raw.
#
# Returns: (clean_amount, cost_raw_or_None)
# Edge cases:
#   - "@@ TOTAL" must be tried before "@ UNIT" (longer match first)
#   - No annotation → returns (raw, None) unchanged
#   - " @ " with spaces is required; a bare "@" without surrounding spaces
#     is not treated as a cost annotation (could appear in commodity names)
def _strip_cost_annotation(raw: str) -> tuple[str, str | None]:
    for marker in (" @@ ", " @ "):
        idx = raw.find(marker)
        if idx != -1:
            return raw[:idx].strip(), raw[idx + len(marker):].strip()
    return raw, None
```

Call this at the START of `_parse_amount` (before lot annotation stripping):
```python
raw, cost_raw = _strip_cost_annotation(raw.strip())
```

Store `cost_raw` on the `Posting` object (see **E2**). The `_parse_amount`
function's return type changes from `Amount` to `tuple[Amount, str | None]`.
Update its return type annotation accordingly. `_parse_posting` destructures
the tuple and sets `posting.cost_raw = cost_raw` after the amount is parsed.
All call sites that receive the return value of `_parse_amount` must be updated
to unpack the tuple.

---

### A3. Lot Annotations (`{...}`, `{{...}}`, `[DATE]`, `(LABEL)`)

**Problem:** Amounts like `3 AAPL {$182.00} [2024-01-18] (lot-A)` fail because
the regex does not understand `{`, `[`, or `(` annotation syntax.

**Fix:** Add a compiled regex and helper `_strip_lot_annotations`:

```python
# Strips hledger lot price/date/label annotations from an amount string.
#
# Purpose: remove {...}, {{...}}, [...], (...) suffixes that appear after
#          the core quantity+commodity token. Applied before cost annotation
#          stripping and the main amount regex.
#
# Supported annotation forms:
#   {{TOTALCOST}}   — total lot cost (double-braces, tried first)
#   {UNITCOST}      — per-unit lot cost
#   [DATE]          — lot acquisition date
#   (LABEL)         — lot label / identifier
#
# Edge cases:
#   - Multiple annotations in any order: regex applied with re.sub (not once)
#   - Annotations always follow the commodity token; they are never at the
#     start of an amount string (virtual posting accounts like "(account)"
#     are separated BEFORE _parse_amount is called, so no collision)
#   - Nested braces/brackets are not supported; the first closing char wins
_LOT_ANNOTATION_RE = re.compile(
    r'\s+(?:\{\{[^}]*\}\}|\{[^}]*\}|\[[^\]]*\]|\([^)]*\))'
)

def _strip_lot_annotations(raw: str) -> str:
    return _LOT_ANNOTATION_RE.sub("", raw).strip()
```

Call at the start of `_parse_amount`, after cost annotation stripping:
```python
raw, cost_raw = _strip_cost_annotation(raw.strip())
raw = _strip_lot_annotations(raw)
```

---

### A4. Quoted Commodity Suffix (`"Chocolate Frogs"`)

**Problem:** The suffix group `([A-Za-z][A-Za-z0-9]*)?` only matches simple
alphanumeric tokens. Quoted commodity names include spaces and quote characters.

**Fix:** Add a quoted-suffix branch BEFORE the main regex, inside `_parse_amount`:

```python
# Quoted suffix commodity: e.g. '-3 "Chocolate Frogs"' or '3 "Foo Bar"'
#
# Purpose: handle commodity names that require double quotes because they
#          contain spaces or start with non-letter characters.
#
# Group breakdown:
#   (1) (-?)    — optional leading minus sign
#   (2) (.*?)   — numeric quantity (lazy, so it stops before the quoted suffix)
#   (3) "([^"]+)" — quoted commodity name, inner text only
#
# Edge cases:
#   - Quantity may include a prefix symbol: '-3' or '$-3' → handled by sign fix
#   - Empty quoted symbol '""' is valid in commodity directives but not in amounts
_QUOTED_SUFFIX_RE = re.compile(r'^(-?)(.*?)\s+"([^"]+)"\s*$')
```

In `_parse_amount`, after cost/lot stripping:
```python
m_qs = _QUOTED_SUFFIX_RE.match(raw)
if m_qs:
    sign, numeric_part, quoted_sym = m_qs.groups()
    numeric_clean = numeric_part.strip().replace(",", "")
    try:
        quantity = Decimal(sign + numeric_clean)
    except InvalidOperation:
        raise ParseError(f"invalid numeric quantity in amount: {raw!r}", lineno)
    return Amount(quantity=quantity, commodity=quoted_sym, raw=raw), None
```

Note: the return value is `(Amount, cost_raw)` per the updated signature from A2.
The quoted-suffix branch always returns `None` for `cost_raw` because cost/lot
annotations were already stripped before this branch is reached.

---

### A5. Space Digit-Group Separators (`1 000 000 JPY`)

**Problem:** `[\d,]+` in the numeric group does not allow spaces.

**Fix:** Normalise space-separated digit groups before running the regex.
Add a normalisation step at the start of `_parse_amount` (after quoted-suffix
check, before regex match):

```python
# Normalise space digit-group separators.
#
# Purpose: collapse runs like "1 000 000" → "1000000" so the standard
#          amount regex can parse them. Only strips a space that sits between
#          two digit sequences where the right-hand group is exactly 3 digits
#          followed by another digit-group or a non-digit character.
#
# Edge cases:
#   - "1 JPY" — single space before a non-3-digit token: NOT collapsed
#     (the right side "JPY" is not digits, so the lookahead fails)
#   - "1 000 000 JPY" — two groups of 3 after the leading digit: both collapsed
#   - Applied iteratively so "1 000 000" → "1000 000" → "1000000"
_SPACE_DIGIT_GROUP_RE = re.compile(r'(\d) (\d{3})(?=\s|\D|$)')

def _normalise_space_separators(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = _SPACE_DIGIT_GROUP_RE.sub(r'\1\2', s)
    return s
```

Call in `_parse_amount` before the main regex:
```python
raw = _normalise_space_separators(raw)
```

---

### A6. Scientific E-Notation (`1E3 EUR`)

**Problem:** `[\d,]+(?:\.\d*)?` does not match `1E3` (no `E`/`e` in the numeric
character class).

**Fix:** Extend the numeric group in `_AMOUNT` (and `_AMOUNT_COMMA`) to accept
E-notation:

```
([\d,]+(?:\.\d*)?(?:[Ee][+-]?\d+)?)
```

Python's `Decimal` already handles `1E3`, `1.5e-2`, `1E+6` natively, so no extra
conversion is needed in `_parse_amount`.

Update both regex doc comments to document the E-notation sub-group.

---

## B. Transaction Header Fix — `_TXN_HEADER` and `_parse_txn_header` *(Phase 3, step 3a)*

### B1. Secondary/Auxiliary Date (`2024-02-20=2024-02-22`)

**Problem:** `_TXN_HEADER` group 1 matches a single date. `2024-02-20=2024-02-22`
is not recognised as a valid transaction header, so the line is silently skipped
(non-indented, matches no directive), and the following posting lines then raise
"posting found outside transaction block".

**Fix — `_TXN_HEADER` regex:** Extend group 1 to optionally accept `=DATE2`:

```python
_TXN_HEADER = re.compile(
    r"^"
    r"((?:\d{4}[-/.])?(?:\d{1,2})[-/.](?:\d{1,2})"       # primary date
    r"(?:=(?:\d{4}[-/.])?(?:\d{1,2})[-/.](?:\d{1,2}))?)"  # optional =DATE2
    r"\s*([*!])?"
    r"\s*(?:\(([^)]*)\))?"
    r"\s*(.*?)"
    r"(?:\s*;\s*(.*))?$"
)
```

**Fix — `_parse_txn_header`:** Split group 1 on the first `=` to separate primary
and secondary date strings, then parse both:

```python
date_raw = m.group(1)
if "=" in date_raw:
    primary_raw, secondary_raw = date_raw.split("=", 1)
    date1 = _parse_simple_date(primary_raw, lineno, default_year)
    date2 = _parse_simple_date(secondary_raw, lineno, default_year)
else:
    date1 = _parse_simple_date(date_raw, lineno, default_year)
    date2 = None
```

Store `date2` on the `Transaction` object (see **E1**).

Update `_TXN_HEADER` doc comment: add secondary date to group 1 breakdown and
edge cases.

---

## C. New Directives — `_parse_string_impl` *(Phase 3, steps 3b–3f)*

Each handler follows the existing comment style (purpose / group breakdown /
edge cases). Insert each in the directive-processing region.

### C1. `Y YEAR` Directive

**Placement:** Before the `D` directive handler (order: `D`, `Y` alphabetically,
or group single-letter directives together).

```python
# --- Y directive (default year) ---
#
# Purpose: set the default year for year-omitted dates in this file.
#          Overrides the `default_year` parameter passed to `parse_string`.
#          All yearless dates parsed AFTER this line use the declared year.
#
# Edge cases:
#   - "Y 2024  ; comment" → comment stripped, year = 2024
#   - Multiple Y directives: last one wins (hledger behaviour)
#   - Y with non-integer value → leniently skip, emit ParseError in lenient mode
if not line[0:1].isspace() and re.match(r"^Y\s", line):
    body = _strip_directive_comment(line[len("Y"):].strip())
    try:
        default_year = int(body)
    except ValueError:
        _err = ParseError(f"invalid Y directive year: {body!r}", lineno)
        if errors_out is None:
            raise _err
        errors_out.append(_err)
    continue
```

### C2. `D AMOUNT` Directive (Default Commodity)

**Placement:** After `Y` handler.

**Logic:**
1. Parse `D $1,000.00` → extract the commodity symbol using `_extract_commodity_symbol`
2. Store as `ctx.default_commodity` (update the `_ParseContext` field)
3. Store raw body in `commodity_directive_raws` for style inference:
   `commodity_directive_raws.setdefault("__default__", body)` — or use the
   empty-string key already used by `Journal.commodity_styles` if that convention
   is cleaner (check how `commodity_styles` property uses `_commodity_directive_raws`)

In `_parse_amount`, when both prefix and suffix symbols are empty after matching,
substitute `ctx.default_commodity`:

```python
commodity = (prefix_sym or suffix_sym or "").strip()
if not commodity:
    if ctx.default_commodity:
        commodity = ctx.default_commodity
    else:
        raise ParseError(f"amount has no commodity symbol: {raw!r}", lineno)
```

Also add `default_commodity: str | None = None` to the public signatures of
`parse_string` and `parse_string_lenient` (backward-compatible; defaults to `None`).
The public parameter initialises `ctx.default_commodity` when `_ParseContext` is
constructed at the start of `_parse_string_impl`.

**Note on api-spec.md:** Adding `default_commodity` to the public API requires an
update to `dev-docs/api-spec.md`. This is a new optional parameter, not a breaking
change.

### C3. `apply account PREFIX` / `end apply account`

**Placement:** After `D` handler.

The active prefix is stored in `ctx.account_prefix` (the `_ParseContext` field).

Handler:
```python
# --- apply account directive ---
#
# Purpose: prepend PREFIX: to every account name parsed inside this block.
#          Mirrors hledger's "apply account" / "end apply account" syntax.
#          Aliases are applied BEFORE the prefix is prepended.
#
# Edge cases:
#   - Nested apply account: second directive emits a ParseError in lenient mode,
#     then REPLACES the first prefix (no nesting supported)
#   - end apply account with no active prefix: silently ignored
#   - Applies to posting account names and to "account" directive names
#     encountered inside the block
if not line[0:1].isspace() and re.match(r"^apply\s+account\s+", line):
    body = line[len("apply account"):].strip()
    new_prefix = _strip_directive_comment(body) or None
    if ctx.account_prefix is not None:
        _err = ParseError(
            f"nested apply account directive (already inside '{ctx.account_prefix}'): "
            f"replacing with '{new_prefix}'",
            lineno,
        )
        if errors_out is None:
            raise _err
        errors_out.append(_err)
    ctx.account_prefix = new_prefix
    continue

if not line[0:1].isspace() and re.match(r"^end\s+apply\s+account\b", line):
    ctx.account_prefix = None
    continue
```

In the posting-assembly block, after alias application, prepend the prefix:
```python
if ctx.account_prefix:
    account = f"{ctx.account_prefix}:{account}"
```

In the `account` directive handler, after extracting `account_name`:
```python
if ctx.account_prefix:
    account_name = f"{ctx.account_prefix}:{account_name}"
```

### C4. Skip `~` Periodic Transaction Rules

**Placement:** Before the transaction-header detection block.

```python
# --- ~ (periodic transaction rule) ---
#
# Purpose: recognise a periodic transaction rule header and skip its
#          posting lines without raising ParseError. The rule itself and
#          its postings are not stored; only --forecast expansion (out of
#          scope for v1) would use them.
#
# Edge cases:
#   - "~ monthly" with no description is valid; the leading ~ is sufficient
#   - If a transaction is currently open, flush it first (malformed input)
#   - skip_until_blank consumes indented postings until the next blank line
#   - A ParseWarning is appended to errors_out in lenient mode so callers
#     can detect skipped blocks; it does not count as a parse error
if not line[0:1].isspace() and line.startswith("~"):
    if current_txn is not None:
        end = current_txn_last_lineno or (current_txn.source_line or 1)
        _flush_txn(current_txn, end, all_lines, source_file)
        transactions.append(current_txn)
        current_txn = None
        current_txn_last_lineno = None
        last_posting_in_txn = None
    if errors_out is not None:
        errors_out.append(ParseWarning(
            f"periodic transaction rule (~) at line {lineno} skipped (not supported in v1)",
            lineno,
        ))
    skip_until_blank = True
    continue
```

**`ParseWarning` type:** If `ParseWarning` does not already exist in the codebase,
define it as a subclass of `ParseError` in `parser.py`:

```python
class ParseWarning(ParseError):
    """A non-fatal parse notice; does not prevent journal loading."""
```

This allows callers to distinguish warnings from errors with `isinstance` checks
without changing the type of `errors_out`.

### C5. Skip `=` Auto-Posting Rules

**Placement:** Immediately after the `~` handler.

```python
# --- = (auto-posting rule) ---
#
# Purpose: recognise an auto-posting rule header and skip its posting lines.
#          Auto-posting rules are non-indented lines starting with "= ".
#          The postings inside are not stored; only --auto expansion (out of
#          scope for v1) would use them.
#
# Edge cases:
#   - "= expenses:food" matches; "=expenses:food" (no space) does NOT (could
#     be other syntax; only "= QUERY" with a space is valid hledger syntax)
#   - Distinguished from balance-assignment postings by the indentation guard
#     (`not line[0:1].isspace()`) — balance assignments are always indented
#   - A ParseWarning is appended to errors_out in lenient mode so callers
#     can detect skipped blocks; it does not count as a parse error
if not line[0:1].isspace() and re.match(r"^=\s+\S", line):
    if current_txn is not None:
        end = current_txn_last_lineno or (current_txn.source_line or 1)
        _flush_txn(current_txn, end, all_lines, source_file)
        transactions.append(current_txn)
        current_txn = None
        current_txn_last_lineno = None
        last_posting_in_txn = None
    if errors_out is not None:
        errors_out.append(ParseWarning(
            f"auto-posting rule (=) at line {lineno} skipped (not supported in v1)",
            lineno,
        ))
    skip_until_blank = True
    continue
```

---

## D. Commodity Directive Fix — `_extract_commodity_symbol` *(Phase 2b, step 2b-iv)*

### D1. Quoted Suffix in `commodity` Directive

**Problem:** `1,000. "Chocolate Frogs"` starts with a digit, so the
`startswith('"')` early-exit does not fire. The `_COMMODITY_AMOUNT` regex then
fails because its suffix group `[^\d,.\s]*` cannot match a string containing
spaces (`"Chocolate Frogs"`).

**Fix:** Insert a trailing-quoted-symbol check AFTER the `startswith('"')` block
and BEFORE the `_COMMODITY_AMOUNT.match` call:

```python
# Trailing quoted symbol: e.g. '1,000. "Chocolate Frogs"'
#
# Purpose: handle commodity directives where the sample amount has a quoted
#          suffix commodity that contains spaces or special characters.
#
# Group breakdown:
#   (1) ([\d,. ]*)   — numeric sample (digits, commas, dots, spaces); may be empty
#   (2) "([^"]+)"    — quoted commodity name, inner text only
#
# Edge cases:
#   - Leading whitespace already stripped by caller
#   - Trailing whitespace after the closing quote: absorbed by \s*$
_TRAILING_QUOTED_RE = re.compile(r'^([\d,. ]*)\s*"([^"]+)"\s*$')

m_tq = _TRAILING_QUOTED_RE.match(body)
if m_tq:
    return m_tq.group(2)  # e.g. returns "Chocolate Frogs"
```

Add the compiled regex as a module-level constant `_TRAILING_QUOTED_COMMODITY_RE`
(with full doc comment) alongside the other module-level regexes.

---

## E. Model Changes — `ledgerkit/models.py` *(Phase 1)*

### E1. `Transaction.date2`

Add optional field to the `Transaction` dataclass:

```python
@dataclass
class Transaction:
    ...
    date2: Optional[datetime.date] = None   # secondary/auxiliary date
```

Place after the existing `date` field. The field has a default of `None`, so
all existing construction sites (`Transaction(date=..., ...)`) remain valid
without modification.

Update `dev-docs/api-spec.md`: add `date2: Optional[date] = None` to the
Transaction table, marked `[ADDED IN v0.2.0]` or similar per the spec's
convention.

### E2. `Posting.cost_raw`

Add optional field to the `Posting` dataclass:

```python
@dataclass
class Posting:
    ...
    cost_raw: Optional[str] = None   # raw cost annotation (e.g. "$180.00" from "@ $180.00")
```

Place after the existing amount-related fields. The field has a default of
`None`, so all existing construction sites remain valid without modification.

The value is populated by `_parse_posting` after `_parse_amount` returns the
stripped annotation string (see **A2**).

Update `dev-docs/api-spec.md`: add `cost_raw: Optional[str] = None` to the
Posting table, marked `[ADDED IN v0.2.0]`.

---

## F. Documentation Updates *(Phase 5)*

All updates in a single response after tests pass.

| File | Change |
|---|---|
| `dev-docs/api-spec.md` | Add `Transaction.date2: Optional[date] = None`; add `Posting.cost_raw: Optional[str] = None`; add `default_commodity` param to `parse_string` / `parse_string_lenient`; add `ParseWarning` class |
| `dev-docs/hledger-compatibility.md` | Amounts table: add sign-after-symbol, space separator, E-notation, quoted suffix, cost/lot annotations; Directives table: add `Y`, `D`, `apply account`; Transaction table: add secondary date |
| `knowledge/DOMAIN_RULES.md` | Add rule: `$-300` and `-$300` are both valid in hledger; sign may appear before OR after a prefix commodity symbol |
| `knowledge/EDGE_CASES.md` | Add: lot annotation stripping must not strip virtual posting `(account)` names — these are separated before `_parse_amount` is called |
| `CHANGELOG.md` | New `[Unreleased]` entry with Human/Claude lines |
| `ROADMAP.md` | Move Milestone 4 from `[PLANNED]` → `[IN PROGRESS]` at start of work; back to `[DONE]` only when user confirms |
| `CONTEXT.md` | Overwrite with current task state |

---

## G. Test Plan *(Phase 4)*

Add to `tests/test_parser/test_parser.py`. Target: 25+ new test methods.

| Test class | Key methods |
|---|---|
| `TestSignAfterPrefixSymbol` | `test_dollar_negative`, `test_pound_negative`, `test_euro_negative`, `test_suffix_commodity_unaffected` |
| `TestCostAnnotations` | `test_at_unit_cost_stripped`, `test_atat_total_cost_stripped`, `test_cost_with_lot_annotation`, `test_cost_raw_stored_on_posting` |
| `TestLotAnnotations` | `test_unit_lot_brace`, `test_total_lot_double_brace`, `test_lot_date`, `test_lot_label`, `test_all_annotations_combined` |
| `TestQuotedCommodityAmount` | `test_quoted_suffix_in_amount`, `test_quoted_suffix_negative` |
| `TestQuotedCommodityDirective` | `test_quoted_suffix_in_commodity_directive` |
| `TestSpaceSeparator` | `test_space_digit_groups_three_groups`, `test_space_single_group`, `test_space_before_alpha_commodity` |
| `TestScientificNotation` | `test_e_notation_suffix`, `test_e_notation_small`, `test_e_notation_negative` |
| `TestSecondaryDate` | `test_secondary_date_stored_on_transaction`, `test_no_secondary_date_is_none` |
| `TestYDirective` | `test_y_overrides_default_year` |
| `TestDDirective` | `test_d_applies_to_no_symbol_amount`, `test_d_with_comma_decimal` |
| `TestApplyAccount` | `test_apply_account_prepends_prefix`, `test_end_apply_account_clears`, `test_apply_account_with_aliases`, `test_apply_account_nested_emits_warning` |
| `TestPeriodicRuleSkip` | `test_tilde_rule_skipped_no_error`, `test_tilde_rule_postings_skipped`, `test_tilde_rule_emits_warning` |
| `TestAutoPostingRuleSkip` | `test_equals_rule_skipped_no_error`, `test_equals_rule_postings_skipped`, `test_equals_rule_emits_warning` |
| `TestFixtureLoad` | `test_comprehensive_fixture_zero_errors` ← **milestone gate** |

**Notes on new tests:**

- `test_cost_raw_stored_on_posting` — assert that parsing `10 AAPL @ $180.00`
  produces a posting with `cost_raw == "$180.00"`.

- `test_space_before_alpha_commodity` — assert that `1 234 EUR` collapses to
  `1234 EUR` (three-digit group, collapsed) and that `1 JPY` does NOT collapse
  the space before a non-three-digit alphabetic suffix. This pins the iterative
  regex edge case explicitly.

- `test_apply_account_nested_emits_warning` — parse a journal with two consecutive
  `apply account` directives without an intervening `end apply account`; assert
  that `parse_string_lenient` returns a non-empty errors list containing a
  `ParseError` (or `ParseWarning`) that mentions "nested apply account".

- `test_tilde_rule_emits_warning` — parse a journal with a `~` rule block; assert
  that the returned errors list contains a `ParseWarning` mentioning "periodic
  transaction rule" and that no `ParseError` (non-warning) is present.

- `test_equals_rule_emits_warning` — parse a journal with a `= QUERY` rule block;
  assert that the returned errors list contains a `ParseWarning` mentioning
  "auto-posting rule" and that no `ParseError` (non-warning) is present.

**Gate test (must pass for milestone to be done):**

```python
def test_comprehensive_fixture_zero_errors(self):
    fixture = Path(__file__).parent.parent / "fixtures" / "comprehensive-hledger-test.journal"
    text = fixture.read_text(encoding="utf-8")
    journal, errors = parse_string_lenient(text, source_file=str(fixture))
    # Warnings from skipped rule blocks are expected and allowed; actual errors are not
    real_errors = [e for e in errors if not isinstance(e, ParseWarning)]
    self.assertEqual(real_errors, [], msg="\n".join(str(e) for e in real_errors))
```

---

## H. Verification Commands

```powershell
# 1. All existing tests must still pass
python -m unittest discover -s tests -t . -v

# 2. Zero-error gate test (warnings from skipped rule blocks are allowed)
python -c "
from ledgerkit.parser import parse_string_lenient, ParseWarning
from pathlib import Path
text = Path('tests/fixtures/comprehensive-hledger-test.journal').read_text('utf-8')
j, errs = parse_string_lenient(text, source_file='tests/fixtures/comprehensive-hledger-test.journal')
real_errors = [e for e in errs if not isinstance(e, ParseWarning)]
print(f'{len(j.transactions)} transactions, {len(real_errors)} errors, {len(errs) - len(real_errors)} warnings')
for e in real_errors: print(' ERROR:', e)
assert not real_errors, 'Parse errors remain'
print('PASS')
"

# 3. CLI check exits 0
python -m ledgerkit check -f tests/fixtures/comprehensive-hledger-test.journal
echo "Exit code: $LASTEXITCODE"
```

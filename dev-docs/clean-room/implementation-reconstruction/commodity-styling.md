# Implementation Reconstruction: commodity-styling

- **Role**: implementation-reconstructor
- **Topic**: commodity-styling (Ledgerkit's commodity formatting/style-inference subsystem)
- **Dispatch**: same-host, prompt-scoped sub-dispatch (best-effort isolation, not verified) — this report was produced under a `general-purpose`-typed dispatch following the `implementation-reconstructor` brief verbatim, per Plan 29 §4.2's disclosed-substitution allowance
- **Dispatch id / timestamp**: session_014zQZ8FHzgy8VTjoy79bmYm @ 2026-10-03T00:55:47+08:00
- **Date**: 2026-10-03

Evidence used (all permitted, nothing else read):
- `ledgerkit/commodity_style.py` (full read)
- `ledgerkit/models.py` (full read)
- `tests/test_commodity_style.py` (full read)
- `tests/test_parser/test_parser.py` (grepped for "commodity", then representative sections read: lines 80-480, 900-960, 1080-1310, 1330-1380)
- Live Python execution of `CommodityStyle.infer()`, `.format()`, `.parse_style_override()`, and the private helper `_infer_separators()` (several probes, reproduced inline below)
- `python -m unittest tests.test_commodity_style -v` (confirms current pass/fail state of the topic's own tests, including its CLI-integration subclass, as of this reconstruction)

No assertion, snapshot, legacy dev-docs/docs markdown, or `knowledge/*.md` file was read at any point.

---

## 1. Structure

`ledgerkit/commodity_style.py` is a small, self-contained module with four pieces:

1. **Module-level helper** `_group_digits(digits: str, sep: str) -> str` — inserts `sep` every 3 digits from the right on a digit-only string. No regex, no edge-case handling beyond what the loop does structurally.
2. **Two documented regexes** (module scope, each with the project's required purpose/group-breakdown/edge-case comment block):
   - `_STYLE_SUFFIX_COMMODITY = re.compile(r"([A-Za-z][A-Za-z0-9]*)\s*$")` — finds a trailing alphabetic/alphanumeric commodity code.
   - `_STYLE_PREFIX_COMMODITY = re.compile(r"^(-?)([^\d,.\s-]+)")` — finds a leading non-numeric symbol (e.g. `$`, `£`, `€`), after an optional minus sign.
   Both exist solely to support `parse_style_override()`.
3. **`CommodityStyle`** — a `@dataclass` holding the inferred/declared display style for one commodity, with `.format()` (instance method) and two classmethods, `.infer()` and `.parse_style_override()`.
4. **`_infer_separators(numeric: str) -> tuple`** — a module-level helper (not on the class) that decides `(decimal_mark, group_separator, precision)` from a numeric substring already stripped of its commodity symbol.

The module imports nothing from the rest of ledgerkit — it is a leaf module (see §4).

## 2. Public surface

From `ledgerkit/commodity_style.py`:

```python
@dataclass
class CommodityStyle:
    commodity: str
    prefix: bool = True
    space: bool = False
    decimal_mark: str = "."
    group_separator: str = ""
    precision: int = 2

    def format(self, quantity: Decimal) -> str: ...

    @classmethod
    def infer(cls, commodity: str, raw_amount_str: str) -> "CommodityStyle": ...

    @classmethod
    def parse_style_override(cls, style_string: str) -> "CommodityStyle": ...
```

`parse_style_override()` raises `ValueError` (confirmed live and by tests) when: the input is empty/whitespace-only, contains no digit at all, or contains digits but no recognisable leading/trailing commodity symbol (e.g. a bare `"1,234.56"` with no symbol — confirmed live, raises `ValueError: cannot parse commodity style: '1,234.56'`).

`_group_digits` and `_infer_separators` are private (leading underscore) module-level functions, not part of the public surface, but are load-bearing for `infer()`'s behaviour.

From `ledgerkit/models.py`, the pieces that compose with commodity-styling:

- `Amount.display(self, style: object) -> str` — thin delegator, literally `return style.format(self.quantity)`. The `style` parameter is untyped (`object`, with a `# type: ignore[attr-defined]` on the call), so nothing in `models.py` enforces that `style` is actually a `CommodityStyle` at the type level — it's a duck-typed `.format(Decimal) -> str` contract.
- `Journal.commodity_styles` — a `@property` returning `Dict[str, CommodityStyle]`, documented and implemented as a three-pass priority system (see §5).
- `Journal._commodity_directive_raws: dict` — a private field (not part of the stated public dataclass contract, `repr=False`) mapping commodity symbol → raw sample amount string from a `commodity` directive; consumed only by `commodity_styles`.
- `ReportSectionResult.to_dataframe()` and `Journal.to_dataframe()` — both consume `commodity_styles`/a `CommodityStyle` to produce an `amount_formatted` column (see §5 for a dead-code observation in the former).

## 3. Data model

`CommodityStyle` (dataclass, 6 fields, defaults shown above) is the entire data model for this topic. There is no separate "style registry" class — `Journal.commodity_styles` just returns a plain `dict[str, CommodityStyle]` computed fresh on every property access (no caching).

`Amount` (in `models.py`) is the data model this subsystem formats:

```python
@dataclass
class Amount:
    quantity: Decimal
    commodity: str
    raw: Optional[str] = field(default=None, repr=False, compare=False)
```

`raw` is explicitly excluded from `repr`/`__eq__` comparison (`compare=False`), and is the field `CommodityStyle.infer()` is always fed from in `models.py` (`p.amount.raw`, `price.price.raw`) — i.e. the style-inference subsystem depends on whatever verbatim source text `Amount.raw` was set to by the parser (parser.py is out of scope for this reconstruction, so I cannot confirm from primary evidence exactly what `raw` contains for every amount shape — notably quoted/multi-word commodities; see the gap in §7).

## 4. Dependencies

`ledgerkit/commodity_style.py` imports only: `re`, `dataclasses.dataclass`, `decimal.Decimal`, `typing.Optional`, plus `from __future__ import annotations`. No imports from elsewhere in `ledgerkit/`. It is a dependency-free leaf module within the project.

`ledgerkit/models.py` depends on it via a **lazy, in-property import** (`from ledgerkit.commodity_style import CommodityStyle` inside the `commodity_styles` property body), consistent with the lazy-import pattern used throughout `models.py` for its other report-method delegations (stated purpose there: avoid circular imports between `models.py` and `reports.py`; `commodity_style.py` itself has no reverse dependency on `models.py`, so no cycle actually exists for this particular import — it simply follows the file's established convention).

## 5. Runtime behaviour (traced + live-executed)

### `CommodityStyle.infer(commodity, raw_amount_str)`

1. Strips the raw string; strips a single leading `-` (for symbol-position detection only — the sign is not used again in `infer`).
2. Checks `s.startswith(commodity)` → prefix; else `s.endswith(commodity)` → suffix; else neither (see below).
3. Whichever matched, the commodity substring is removed and `space` is set to whether the adjoining character was a space/tab.
4. The remaining numeric substring is passed to `_infer_separators()`.
5. **Fallback when the commodity string is not found as a prefix or suffix of `s`** (the code's own comment calls this "rare edge case"): `prefix` stays `True`, `space` stays `False`, and the *entire* stripped string (commodity included, if present but not matching start/end) is treated as "numeric" and fed to `_infer_separators()`.

   Live-verified this fallback is reachable and silent (no exception) even for pathological input, e.g.:
   ```
   CommodityStyle.infer('X', 'abc')  -> CommodityStyle(commodity='X', prefix=True, space=False,
                                                          decimal_mark='.', group_separator='', precision=0)
   CommodityStyle.infer('X', '')     -> same defaults
   ```
   `infer()` has no `raise` statement anywhere and calls nothing that raises for string input — confirmed by probing empty string, whitespace-only, bare `"-"`, and non-numeric `"abc"` as `raw_amount_str`, none of which raised.

   **Quoted/multi-word commodity gap** (live-verified, not covered by any test — see §6/§7): if the raw source text for a quoted commodity amount retains its surrounding quote character (e.g. a hypothetical `raw = '3 "Chocolate Frogs"'` for `commodity = 'Chocolate Frogs'`), `s.endswith(commodity)` is `False` because the string actually ends with `"` after the commodity name, so detection falls into the "rare edge case" branch:
   ```
   CommodityStyle.infer('Chocolate Frogs', '3 "Chocolate Frogs"')
     -> CommodityStyle(commodity='Chocolate Frogs', prefix=True, space=False,
                        decimal_mark='.', group_separator='', precision=0)
   ```
   This silently produces a wrong-looking style (prefix=True for what is actually a suffix commodity in the journal) with no error. By contrast, feeding the *unquoted* form works correctly:
   ```
   CommodityStyle.infer('Chocolate Frogs', '3 Chocolate Frogs')
     -> CommodityStyle(commodity='Chocolate Frogs', prefix=False, space=True, ...)
   ```
   Whether `Amount.raw` actually retains the quote characters for quoted commodities is a parser.py question outside this reconstruction's permitted evidence — I can only establish that `commodity_style.py`'s own `infer()` mishandles the quoted form *if* fed it, and that no test anywhere in the permitted evidence (`test_commodity_style.py` or `test_parser/test_parser.py`) exercises `CommodityStyle.infer()`/`Journal.commodity_styles` against a quoted-commodity amount to settle the question either way.

### `_infer_separators(numeric)`

Decides decimal-mark/group-separator/precision purely from counts and positions of `.`/`,` in the already-symbol-stripped numeric string:

- Both present → the rightmost of the two is the decimal mark, the other is the group separator, `precision = len(numeric) - index_of_rightmost_separator - 1`. Live-verified on a multi-group string `"1.234.567,89"` → `(',', '.', 2)` — correct for this case, but the logic does **not** validate that the earlier, non-rightmost dot is actually a legitimate 3-digit grouping; it is simply never inspected. A malformed string with inconsistent grouping (e.g. `"1.23.456,78"`) would silently produce the same `(',', '.', 2)` result without any validation that the first group has the "right" digit count.
- Only `.` present → if exactly one dot, with exactly 3 digits after it, and the dot isn't at position 0, it's treated as a European group separator (decimal becomes `,`, precision `0`); otherwise `.` is the decimal mark with `precision = digits_after`.
- Only `,` present → symmetric US/UK-style logic.
- Neither present → `decimal_mark='.'`, `group_separator=''`, `precision=0`.

Live-verified the "4 digits after a single comma" case is correctly *not* mistaken for grouping: `_infer_separators("1,2345")` → `(',', '', 4)` (decimal mark comma, precision 4) — the `== 3`-digit check in the elif branches does its job here.

### `CommodityStyle.format(quantity)`

- `negative = quantity < 0`; operates on `abs(quantity)`.
- **When `precision > 0`**: formats via Python's `f"{abs_qty:.{precision}f}"` (uses `Decimal.__format__`, which rounds — `ROUND_HALF_EVEN` under the default decimal context) and splits on the literal `.` that Python always produces, before substituting `decimal_mark`.
- **When `precision == 0`**: takes a *different* code path — `int_str = str(int(abs_qty))`. `int(Decimal)` **truncates toward zero**, it does not round.
  - **Live-verified inconsistency/limitation**: `CommodityStyle(..., precision=0).format(Decimal("2.99"))` → `"$2"`, not `"$3"`. The precision>0 path rounds; the precision==0 path truncates. This is a real, confirmed behavioural inconsistency in `format()`, not merely a hypothetical one.
- Group separator (`_group_digits`) is applied only to the integer part, never the fractional part — correct per convention, and live-verified grouping still applies at `precision=0` (e.g. `"$1,234,567"` for `Decimal("1234567")` with `group_separator=","`, `precision=0`).
- Negative-sign placement follows hledger's own convention, applied unconditionally regardless of `space`/`group_separator` settings:
  - Prefix style: `SYMBOL-NUMBER` (e.g. `"£-5,000.00"`), confirmed by both the module's own test suite and a live call.
  - Suffix style: `-NUMBER SYMBOL` (e.g. `"-1,234.56 EUR"`), confirmed likewise.

### `CommodityStyle.parse_style_override(style_string)`

Used by the CLI's `-c`/`--commodity-style` flag (confirmed via `tests/test_commodity_style.py::TestCLIIntegration`, which exercises `ledgerkit.cli.main` end-to-end against a temp journal — `cli.py` itself is out of this reconstruction's permitted evidence, so I report only what the test file's own assertions establish about the integration point, not `cli.py`'s internal implementation).

1. Rejects empty/whitespace-only input and input with no digit at all (`ValueError`).
2. Tries the suffix-alphabetic regex first (`_STYLE_SUFFIX_COMMODITY`); if it matches, delegates to `infer()` with the matched commodity.
3. Else tries the leading-symbol regex (`_STYLE_PREFIX_COMMODITY`); if group 2 is non-empty, delegates to `infer()`.
4. Else raises `ValueError`.

**Live-verified gap**: `parse_style_override` cannot express a quoted/multi-word commodity override at all — `parse_style_override('3 "Chocolate Frogs"')` raises `ValueError: cannot parse commodity style: '3 "Chocolate Frogs"'`, even though the journal format itself (per `test_parser/test_parser.py`'s `TestQuotedCommodityAmount`/`TestQuotedCommodityDirective`) supports exactly this commodity shape. There is no code path in either regex that accounts for a quoted token.

**Live-verified gap**: a bare numeric override with no commodity symbol at all (e.g. `"1,234.56"`) also raises `ValueError` — `parse_style_override` always requires an explicit symbol to anchor off, consistent with its docstring examples (all three given examples include a commodity).

### `Journal.commodity_styles` (models.py)

Three-pass, priority-ordered, **uncached** (computed fresh every property access — no memoisation, so repeated calls re-walk the entire transaction list):

1. First-seen posting amount per commodity (iterating `self.transactions` in order; skips postings with no amount or no `.raw`).
2. First-seen price-directive amount per commodity (only commodities not already set in pass 1).
3. `self._commodity_directive_raws` entries **unconditionally overwrite** whatever passes 1/2 set for that commodity — i.e. an explicit `commodity` directive always wins, regardless of iteration order, matching the property's own docstring ("Explicit commodity directives" ranked highest).

Each pass wraps the `CommodityStyle.infer(...)` call in `try/except Exception: pass`. **Live-verified this guard is effectively unreachable under the current implementation**: probing `infer()` with empty, whitespace-only, bare-minus, and non-numeric raw strings never raised anything (see above) — `infer()` has no internal `raise` and nothing it calls (`_infer_separators`, string slicing/stripping) can raise for arbitrary string input. The defensive `try/except` in `commodity_styles` is therefore dead code against the current `infer()` implementation, not a verified-necessary safeguard — a latent/untested assumption rather than a confirmed bug.

### `ReportSectionResult.to_dataframe()` (models.py)

Contains a **confirmed dead/confused code fragment**, visible directly in the source (lines ~261-269):
```python
commodity = ""
if self.rows:
    commodity = list(self.rows.keys())[0] if self.rows else ""
    # Actually rows are account names, not commodities. We need the
    # commodity from the style map or just leave it as empty.
    commodity = next(iter(self._commodity_styles), "")
style = self._commodity_styles.get(commodity) if commodity else None
```
The first assignment (`commodity = list(self.rows.keys())[0]...`) sets `commodity` to an **account name** (since `self.rows` is `dict[account_name, Decimal]`), which is immediately and unconditionally overwritten by the next line to the first key of `self._commodity_styles` instead. The first assignment has no observable effect — it is dead code, left in place with a comment visibly acknowledging the mistake ("Actually rows are account names, not commodities...") rather than removing it. The resulting behaviour (take the first key of `_commodity_styles`, a dict with no defined order guarantee beyond insertion order) is itself a single-commodity assumption, explicitly flagged by an adjacent comment as temporary ("all rows share the same commodity in balance_from_spec (multi-commodity support is deferred)").

### `Journal.to_dataframe()` (models.py)

Builds one row per posting; for each posting with an amount, looks up `styles.get(amt.commodity)` from `self.commodity_styles` and calls `amt.display(style)` if found, else falls back to plain `str(amt.quantity)` (no commodity styling at all) if no style was inferred for that commodity — e.g. if every occurrence of that commodity across the whole journal somehow had `amount.raw is None` (not observed in any test, but structurally possible given pass 1's `if p.amount.raw` guard).

## 6. Tests

`tests/test_commodity_style.py` — 29 tests total (all currently pass, confirmed live via `python -m unittest tests.test_commodity_style -v`), in four classes:

- **`TestInfer`** (9 tests): asserts concrete field values (not just types) for `$`/EUR/AAPL/£/USD/BTC across prefix vs. suffix, spacing, decimal-mark vs. group-separator inference, negative-sign stripping not affecting position detection, and the "3-digits-after-a-single-separator means group separator" heuristic in both US (`$1,234`→group `,`) and European (`1.234 EUR`→group `.`) directions.
- **`TestFormat`** (9 tests): roundtrip formatting (infer then format back to the original string) for $, EUR, AAPL, £; explicit negative-number placement for both prefix and suffix styles; directly-constructed `CommodityStyle` instances (not via `infer`) for no-group-separator, large-number grouping (`$1,234,567.89`), and zero.
- **`TestParseStyleOverride`** (7 tests): dollar-prefix and USD/EUR-suffix happy paths with full field assertions; a GBP-prefix case that only checks `commodity`/`prefix` (not the full style); three negative cases — empty string, no-digit string (`"bad input !!"`), whitespace-only string — all asserting `ValueError`.
- **`TestCLIIntegration`** (4 tests): drives `ledgerkit.cli.main(args)` directly (capturing stdout) against a temp one-transaction `.journal` file. Asserts: (a) default `balance` output uses the inferred style (`"£50.00"` appears verbatim); (b) `-c "£1.000,00"` changes the *same* commodity's rendering to comma-decimal (`"£50,00"` appears); (c) `-c "1,000.00 GBP"` (a *different* commodity symbol than the journal's `£`) has **no effect** — `£50.00` is unchanged and the literal string `"GBP"` does not appear anywhere in output, confirming style overrides are keyed per-commodity rather than applied globally; (d) an invalid `-c "bad input !!"` causes the CLI to exit with a non-zero return code. Note: this class's assertions are about the CLI-facing behaviour, but necessarily exercise `ledgerkit/cli.py` to do so — `cli.py` itself is outside this reconstruction's permitted evidence paths, so I report only what these four test bodies assert and that they currently pass, not `cli.py`'s own internal implementation.

`tests/test_parser/test_parser.py` — no test in this file targets `commodity_style.py` directly; it targets the parser's production of `Amount.commodity`/`Amount.raw` that `commodity_style.py` later consumes. Relevant, read-confirmed observations used only as upstream context (not as evidence about `commodity_style.py`'s own correctness, since `parser.py` is out of scope):
- Prefix (`£30.00`) and suffix (`30.00 EUR`) commodities, with sign variants (`$-300`, `£-30.00`, `-30.00 EUR`), all assert only `.quantity`/`.commodity`, never touching style inference.
- Quoted multi-word commodities (`3 "Chocolate Frogs"`) assert `amount.commodity == "Chocolate Frogs"` (quotes stripped from the field) — but **no test anywhere in either permitted test file** feeds such an amount's raw text through `CommodityStyle.infer()` or `Journal.commodity_styles` to check the resulting style is sensible. This is exactly the gap identified live in §5.
- `D` directive (default commodity for symbol-less amounts) and `decimal-mark` directive tests confirm that by the time an `Amount` reaches `commodity_style.py`, directive-driven decimal-mark/default-commodity resolution has already happened upstream in the parser — `commodity_style.py` itself has no knowledge of the `D`/`decimal-mark` directives; it only ever sees the already-resolved `Amount.raw` string.
- `resolve_elision` tests confirm multi-commodity elided-posting inference sorts inferred postings alphabetically by the plain `commodity` string (`$` < `£` by Unicode code point, `EUR` sorts before both per `sorted(["EUR", "$", "£"])`) — unrelated to styling but confirms `Amount.commodity` is treated as an opaque sortable string elsewhere in the codebase, consistent with how `commodity_style.py` treats it (never parses or validates the commodity string's own shape beyond the two override-regexes).

## 7. Limitations / gaps (honest list, for the next-stage comparison)

1. **`format()` rounds at `precision > 0` but truncates at `precision == 0`.** Live-confirmed: `Decimal("2.99")` formatted at `precision=0` yields `"2"`, not `"3"`. Internally inconsistent rounding behaviour depending on whether precision is zero.
2. **`infer()` mishandles quoted/multi-word commodities if the raw source text retains quote characters.** Live-confirmed on a synthetic input; whether this is actually reachable depends on `parser.py`'s treatment of `Amount.raw` for quoted commodities, which is outside this reconstruction's evidence. No test in either permitted test file settles this either way — a genuine blind spot in test coverage, not just a theoretical risk.
3. **`parse_style_override()` cannot express a quoted/multi-word commodity override**, even though the journal format itself supports such commodities (per `test_parser/test_parser.py`). Live-confirmed `ValueError`.
4. **`parse_style_override()` requires an explicit commodity symbol** — a pure numeric style string with no symbol (e.g. `"1,234.56"`) always raises `ValueError`, live-confirmed. Not documented as a limitation in the docstring (the docstring's three examples all include a symbol, but the constraint itself is implicit, not stated).
5. **`_infer_separators()` does not validate multi-group consistency.** For numbers with more than one group separator occurrence (e.g. `"1.234.567,89"`), only the rightmost separator-of-each-kind is inspected; earlier groups are never checked for the expected 3-digit width. A malformed input would silently produce a result identical to a well-formed one — live-confirmed on `"1.234.567,89"` → `(',', '.', 2)` without any way to distinguish it from an inconsistent variant.
6. **The commodity-not-found fallback in `infer()`** ("rare edge case" per the code's own comment) defaults to `prefix=True, space=False` and treats the *entire* stripped string as the numeric part — live-confirmed reachable for any raw string that doesn't literally start or end with the exact commodity substring, including empty strings, whitespace, and arbitrary non-numeric text. `infer()` never raises for such input; it degrades silently to a plausible-looking but unverified style.
7. **The `try/except Exception: pass` guards around all three `CommodityStyle.infer()` call sites in `Journal.commodity_styles`** are, under the current `infer()` implementation, unreachable dead code — live-confirmed `infer()` does not raise for any string input tried (empty, whitespace, bare minus, non-numeric). This is not itself a bug, but it means the "defensive" exception handling is untested/unexercised by design, and any future change to `infer()` that *does* introduce a raise path would silently start being swallowed here with no test to catch a resulting wrong/missing style.
8. **`ReportSectionResult.to_dataframe()` contains dead code** (an account-name value assigned to a variable named `commodity`, then immediately and unconditionally overwritten) — see §5. The surrounding single-commodity-per-section assumption is explicitly flagged by the code's own comment as deferred/incomplete ("multi-commodity support is deferred"), not something this reconstruction is asserting independently.
9. **No caching on `Journal.commodity_styles`.** It is a `@property`, recomputed by walking every transaction/posting and every price directive on each access; this is a performance characteristic (not a correctness bug) worth surfacing since callers (`to_dataframe()`, `ReportSectionResult.to_dataframe()`) each call it independently.
10. **`Amount.display()`'s `style` parameter is untyped (`object`) with an explicit `# type: ignore[attr-defined]`** — there is no structural/runtime check that `style` is actually a `CommodityStyle`; any duck-typed object with a `.format(Decimal) -> str` method would work, and a wrong type would fail only at the `.format()` call site, not at `display()`'s own boundary.

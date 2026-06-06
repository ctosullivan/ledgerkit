# Changelog — Milestone 4: Comprehensive Format Compatibility

Archived on: 2026-06-06
GitHub commits: 5442e73 (Phase 1) … release commit (Phases 2–5)

---

### Milestone 4 Phase 1 — Model prerequisites and parser context refactor

**Human:** Add `Transaction.date2` and `Posting.cost_raw` fields as prerequisites for Milestone 4 parser work; introduce `_ParseContext` dataclass to consolidate parser state threading.

**Claude:** Added `date2: Optional[datetime.date] = None` to `Transaction` and `cost_raw: Optional[str] = None` to `Posting` in `models.py`. Added `_ParseContext` dataclass to `parser.py` with fields `default_year`, `decimal_mark`, `default_commodity`, and `account_prefix`; replaced individual `decimal_mark` parameter threading through `_parse_string_impl` → `_parse_posting` → `_parse_amount` with a single `ctx: _ParseContext` argument. Updated direct `_parse_amount` callers in `tests/test_checks/test_checks.py` to supply a context. 538 tests pass.

---

### Milestone 4 Phase 2a — Amount parser fixes A1–A3

**Human:** Implement Phase 2a of Milestone 4: fix amount parsing for sign-after-prefix-symbol (`$-300`), cost annotations (`@ $180`, `@@ $920`), and lot annotations (`{$182}`, `{{$370}}`, `[DATE]`, `(LABEL)`).

**Claude:** Added optional mid-minus group `(-?)` to `_AMOUNT` and `_AMOUNT_COMMA` regexes (new group 3; remaining groups renumbered); updated `_parse_amount` to unpack 5 groups and combine `minus or mid_minus` for the effective sign. Added `_strip_cost_annotation` helper and `_strip_lot_annotations` helper with `_LOT_ANNOTATION_RE` (four-form alternation with full CLAUDE.md doc comment). Changed `_parse_amount` return type from `Amount` to `tuple[Amount, str | None]`; stripped cost annotation text is stored as `Posting.cost_raw`. Updated all three `_parse_amount` call sites in `parser.py` (P directive, assertion amount, posting amount) and the alias-reconstruction block. Updated two test helpers in `test_checks.py` to unpack the new tuple. 538 tests pass; fixture errors drop from 22 to 7.

---

### Milestone 4 Phase 2b — Amount parser fixes A4–A6, D1

**Human:** Implement Phase 2b of Milestone 4: fix amount parsing for E-notation (`1E3 EUR`), quoted commodity suffix (`-3 "Chocolate Frogs"`), space digit-group separators (`1 000 000 JPY`), and quoted commodity symbol in `commodity` directive (`1,000. "Chocolate Frogs"`).

**Claude:** Extended `_AMOUNT` and `_AMOUNT_COMMA` numeric group with `(?:[Ee][+-]?\d+)?` for E-notation (Python's `Decimal` handles this natively). Added `_SPACE_DIGIT_GROUP_RE` and `_normalise_space_separators` (iterative regex substitution collapsing `\d \d{3}` groups) called at the start of `_parse_amount`. Added `_QUOTED_SUFFIX_RE` and a quoted-suffix early-exit branch in `_parse_amount` (checked after normalisation, before the main regex). Added `_TRAILING_QUOTED_COMMODITY_RE` and a three-line branch in `_extract_commodity_symbol` (checked after `startswith('"')`, before `_COMMODITY_AMOUNT.match`). All new constants have full CLAUDE.md regex doc comments. 538 tests pass; fixture errors drop from 7 to 4; commodities fixture exits 0.

---

### Milestone 4 Phase 3 — Transaction header + directives (B1, C1–C5)

**Human:** Implement Phase 3 of Milestone 4: secondary date in transaction header (B1), `Y` default-year directive (C1), `D` default-commodity directive (C2), `apply account`/`end apply account` directives (C3), skip `~` periodic transaction rule blocks (C4), and skip `=` auto-posting rule blocks (C5).

**Claude:** Added `ParseWarning(ParseError)` class for non-fatal notices. Extended `_TXN_HEADER` regex group 1 to capture optional `=DATE2` suffix; updated `_parse_txn_header` to split on `=` and populate `Transaction.date2`. Added `~` and `=` handlers before the transaction-header detection gate: each flushes any open transaction, sets `skip_until_blank = True`, and appends a `ParseWarning` in lenient mode. Updated the transaction-header quick-detection lookahead from `[\s*!(]` to `[\s*!(=]` so secondary-date lines are recognised. Added `Y` directive handler updating `default_year`; `D` directive handler extracting the commodity symbol via `_extract_commodity_symbol` and storing it in `ctx.default_commodity`; `apply account`/`end apply account` handlers storing the prefix in `ctx.account_prefix`. Added default-commodity fallback in `_parse_amount`: when both prefix and suffix symbols are empty, `ctx.default_commodity` is used if set. Added account-prefix application in posting assembly (after alias rewriting) and in the `account` directive handler. Result: 538 tests pass; 0 hard errors and 2 `ParseWarning` items in the main fixture; commodities fixture exits 0.

---

### Milestone 4 Phase 4 — Tests (A1–A6, B1, C1–C5, D1, gate)

**Human:** Implement Phase 4 of Milestone 4: write 37 new test methods covering all features added in Phases 2a, 2b, and 3 (A1–A6, B1, C1–C5, D1), plus a milestone gate test asserting zero hard errors on the comprehensive fixture.

**Claude:** Added `from pathlib import Path` and `ParseWarning` to imports in `tests/test_parser/test_parser.py`. Added 14 new `TestCase` classes: `TestSignAfterPrefixSymbol` (A1), `TestCostAnnotations` (A2), `TestLotAnnotations` (A3), `TestQuotedCommodityAmount` (A4), `TestQuotedCommodityDirective` (D1), `TestSpaceSeparator` (A5), `TestScientificNotation` (A6), `TestSecondaryDate` (B1), `TestYDirective` (C1), `TestDDirective` (C2), `TestApplyAccount` (C3), `TestPeriodicRuleSkip` (C4), `TestAutoPostingRuleSkip` (C5), and `TestFixtureLoad` (gate). Also added `ParseWarning` emission to the `apply account` handler in `parser.py` when a second `apply account` is encountered without an intervening `end apply account`. 575 tests pass; gate test asserts zero hard errors on the comprehensive fixture.

---

### Milestone 4 Phase 5 — Documentation sync

**Human:** Implement Phase 5 of Milestone 4: synchronise documentation with everything added in Phases 2a, 2b, and 3.

**Claude:** Updated `dev-docs/api-spec.md`: added `ParseWarning` class section; updated `parse_string_lenient` docstring to note that the error list may contain `ParseWarning` instances. Updated `dev-docs/hledger-compatibility.md`: added 6 new Amounts rows (sign-after-prefix-symbol, space separator, E-notation, quoted commodity suffix, cost annotation, lot annotations); added secondary date row to Transactions table; added Y, D, and apply-account rows to Directives table; updated 4 Out-of-Scope rows (auto postings and periodic transactions now show ParseWarning behaviour; secondary dates and lot prices moved to IMPLEMENTED). Added sign-after-prefix-symbol rule to `knowledge/DOMAIN_RULES.md`. Added EC-015 (lot annotation stripping invariant) to `knowledge/EDGE_CASES.md`.

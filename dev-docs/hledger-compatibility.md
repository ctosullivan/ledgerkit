# Hledger Compatibility

Reference: https://hledger.org/1.52/hledger.html

This document tracks which hledger format features are in scope for **v1** of
ledgerkit, which are explicitly out of scope, and which are undecided.

A subset of the tables below (directives, validation checks, and the
genuinely-unsupported features) also has a machine-readable, individually-
citable counterpart in [`dev-docs/compat-register/`](compat-register/) —
each entry there is `status: proposed` pending executable verification
against a real `hledger` binary (`compat-differential-tester`'s job, Stage
C onward). This narrative document remains the primary reference until
every relevant row has a `status: final` register entry to link instead
(`dev-docs/planning/core-redefinition/10-source-assisted-development.md`
§10.6).

---

## Supported File Formats

ledgerkit accepts the following file extensions. This is a deliberate subset of
what hledger 1.52 supports (full comparison below).

| Extension | Description |
|---|---|
| `.journal` | Primary hledger journal format — fully supported |
| `.ledger` | Ledger-CLI compatible journal syntax — supported to the same degree as `.journal`; both use identical parsing in ledgerkit v1 |

### Deviation from hledger 1.52

hledger 1.52 supports seven format families. The table below documents every
format and ledgerkit's stance. Reference: https://hledger.org/1.52/hledger.html#data-formats

| hledger 1.52 format | Extensions | ledgerkit v1 |
|---|---|---|
| journal | `.journal` `.j` `.hledger` `.ledger` | **Supported** for `.journal` and `.ledger` only; `.j` and `.hledger` aliases are **not** accepted |
| timeclock | `.timeclock` | **Not supported** — out of scope |
| timedot | `.timedot` | **Not supported** — out of scope |
| csv | `.csv` | **Not supported** — out of scope |
| ssv | `.ssv` | **Not supported** — out of scope |
| tsv | `.tsv` | **Not supported** — out of scope |
| rules | `.rules` | **Not supported** — out of scope |

**Note on `.ledger`:** ledgerkit does not aim for full Ledger-CLI compatibility.
The `.ledger` extension is accepted because the hledger-compatible subset of
Ledger syntax is identical to `.journal` syntax within v1 scope. Ledger-specific
features (e.g. automated transactions, periodic transactions, value expressions)
remain out of scope and will raise `ParseError` or be silently ignored per the
rules in the "Out of Scope" table below.

---

## Transaction Block Structure

A transaction block is the fundamental unit of a journal file.

```
; Transaction block — annotated

2024-01-15 * (INV-42) Groceries  ; comment   ← block BEGINS here (date required)
│           │  │        │          │
│           │  │        │          └─ inline comment          (optional)
│           │  │        └──────────── description             (optional, free text)
│           │  └───────────────────── transaction code        (optional, parenthesised)
│           └──────────────────────── status: * cleared / ! pending (optional)
└──────────────────────────────────── date YYYY-MM-DD         (REQUIRED - Simple Date Format)

    expenses:food:groceries   £85.40          ← posting lines (2+ space indent)
    assets:bank:checking                      ← elided amount (at most ONE per block)

                                              ← blank line ENDS the block (or EOF)
```

**Delimiter rules:**
- A block **begins** on any non-indented line whose first token is a valid simple
  date: `\d{4}[-/.]\d{1,2}[-/.]\d{1,2}` (full date) or `\d{1,2}[-/.]\d{1,2}`
  (year-omitted); all three separators (`-`, `/`, `.`) and optional leading zeros
  are accepted, consistent with the Simple date spec in the In Scope table
- A block **ends** on the first blank line that follows the header, or at end of file
- The field order on the header line is fixed: `date [flag] [(code)] [description] [; comment]`
- Posting lines are generally identified by 2+ leading spaces (or a tab), however this is not a requirement
- Within a posting line, the account name and amount **must** be separated by
  two or more spaces; a single space is treated as part of the account name
  (e.g. `expenses:fun money`) — a `ParseError` is raised if no double-space
  separator is found and no amount can be parsed
- Exactly **one** posting per block may omit its amount (the *elided* posting); two or
  more elided amounts in the same block is a `ParseError`

---

## In Scope (v1)

### Transactions

| Feature | Example | Notes |
|---|---|---|
| Simple date | `2024-01-15`, `2024/1/15`, `2024.1.15`, `1/15` | Separators: `-` `/` `.`; leading zeros optional; year may be omitted (inferred from current date) |
| Secondary date | `2024-02-20=2024-02-22 * Payroll` | Optional `=DATE2` suffix after primary date; stored in `Transaction.date2` |
| Description | `2024-01-15 Groceries` | Free text after the date |
| Cleared flag | `2024-01-15 * Groceries` | `*` = cleared |
| Pending flag | `2024-01-15 ! Groceries` | `!` = pending |
| Transaction code | `2024-01-15 (INV-42) Groceries` | Parenthesised string before description |
| Postings | `  expenses:food  £30.00` | Two-space indent; account and amount **must** be separated by two or more spaces |
| Elided amount | `  assets:checking` | One posting per transaction may omit amount; no separator required when amount is absent |

### Account Names

| Feature | Example | Notes |
|---|---|---|
| Hierarchical names | `expenses:food:restaurants` | Colon-separated segments |
| Mixed case | `Assets:Bank` | Case-sensitive |
| Spaces in names | `expenses:fun money` | Supported |

### Amounts

| Feature | Example | Notes |
|---|---|---|
| Prefixed symbol | `£30.00`, `$10` | Symbol before quantity |
| Suffixed symbol | `30.00 EUR` | Symbol after quantity (space optional) |
| Negative amounts | `-£5.00` | Leading minus |
| Sign after prefix symbol | `$-300`, `£-30.00` | Sign may appear before OR after a prefix commodity symbol; both `-$300` and `$-300` are accepted |
| Decimal separator | `1,234.56` | Comma thousands separator, period decimal |
| No decimal | `£100` | Integer quantities |
| Space digit-group separator | `1 000 EUR`, `1 000 000 JPY` | Space-separated three-digit groups collapsed before parsing; e.g. `1 000 000 JPY` → quantity `1000000` |
| Scientific notation | `1E3 EUR`, `1.5E-2 USD` | Standard E-notation; Python `Decimal` handles this natively |
| Quoted commodity suffix | `3 "Chocolate Frogs"` | Commodity symbol may be a double-quoted string; spaces allowed inside quotes |
| Cost annotation | `10 AAPL @ $180.00`, `10 AAPL @@ $1800.00` | `@ UNIT_PRICE` and `@@ TOTAL_PRICE` stripped before amount parsing; raw annotation text stored in `Posting.cost_raw` |
| Lot annotations | `10 AAPL {$182}`, `{{$370}}`, `[2024-01-01]`, `(lot1)` | Braces, date brackets, and label parens stripped before amount parsing; discarded (not stored) |

### Comments

Three distinct comment forms are supported. **Indentation is the discriminator** between a standalone top-level comment and a follow-on comment inside a transaction:

| Feature | Example | Indented? | Notes |
|---|---|---|---|
| Top-level `#` | `# a note` | No (column 0) | Always silently discarded; never captured into any field; never extends a transaction's `source_span` |
| Top-level `;` | `; a note` | No (column 0) | Same as `#`; always discarded even when inside an open transaction block (no blank-line separator) |
| Inline `;` on transaction header | `2024-01-15 Desc  ; comment` | N/A (same line) | Only `;` works; `#` is NOT an inline comment delimiter. Captured in `Transaction.inline_comment` |
| Inline `;` on posting | `  expenses:food  £30  ; note` | N/A (same line) | Only `;` works. Captured in `Posting.inline_comment`; stripped before amount is parsed |
| Follow-on `;` inside transaction | `    ; continued note` | Yes | Indented `;` line inside an open transaction block. Appended (newline-separated) to the preceding posting's `inline_comment`, or to `Transaction.inline_comment` if no posting has been seen yet. Extends `source_span.end_line`. |
| Follow-on `#` inside transaction | `    # a note` | Yes | Indented `#` inside a transaction. Extends `source_span.end_line` but text is NOT captured into any comment field. |
| Block comment | `comment` / `end comment` | No (directives) | All lines between the two directives are skipped. `comment` may have trailing text (ignored). Unclosed block runs to EOF. Nested `comment` inside a block is ignored. |

**`#` is never an inline comment delimiter.** Only `;` introduces inline comments on the same line as an entry. A `#` appearing in a transaction description remains part of the description.

### Directives

| Feature | Syntax | Notes |
|---|---|---|
| P directive | `P DATE COMMODITY PRICE` | **[IMPLEMENTED]** Market price declaration; stored in `Journal.prices` as `PriceDirective` objects. DATE uses simple date format; COMMODITY1SYMBOL is the commodity being priced; COMMODITY2AMOUNT is the price as an amount (prefix or suffix symbol). Inline comments (`  ;`) stripped. Scope: prices propagate through `include` naturally (text-expansion strategy). Commodity valuation using stored prices is in scope for Milestone 2. Reference: https://hledger.org/1.52/hledger.html#p-directive |
| alias directive | `alias OLD=NEW` / `alias /REGEX/=REPLACEMENT` / `end aliases` | **[IMPLEMENTED]** Account name rewriting applied at parse time. Basic aliases match `OLD` as an exact account name or as a colon-delimited prefix (e.g. `alias checking = assets:bank` rewrites `checking` and `checking:savings`). Regex aliases substitute any matching substring (case-insensitive per hledger spec; backreferences `\1` supported). Multiple aliases accumulate; `end aliases` clears all active rules. Aliases also rewrite account names in `account` directives. Inline comments using `  ;` or `  #` (two-space rule) are stripped from alias bodies. **Application order:** most-recently-defined alias applied first (LIFO), matching hledger behaviour. **Scoping deviation:** because `include` is handled as a separate `parse_string()` call in `loader.py`, alias rules defined in one file do NOT propagate into included files — a deviation from hledger 1.52 (where aliases propagate into includes). Command-line `--alias` option deferred to a future milestone. Reference: https://hledger.org/1.52/hledger.html#alias-directive |
| include directive | `include other.journal` | **[IMPLEMENTED]** Embeds entries and directives from another `.journal` or `.ledger` file inline at the point of the directive; directives active before the include apply to the included file (text-expansion strategy). Path resolution: relative to containing file's directory, absolute, and `~` tilde expansion; glob patterns (`*`, `**`, `?`, `[range]`) expanded via `glob.glob(recursive=True)`; the containing file is always excluded from glob results. A glob that matches no files raises `ParseError`. Circular includes raise `ParseError`. Format prefixes (e.g. `timedot:`) raise `ParseError` — not supported in ledgerkit v1. Only `.journal` and `.ledger` targets accepted (other extensions raise `ParseError`). **Dot-file glob behaviour**: uses Python `glob.glob()` defaults, which may differ from hledger 1.52 (hledger excludes dot files from `*`/`**`; Python's glob may include them). Reference: https://hledger.org/1.52/hledger.html#include-directive |
| account directive | `account assets:bank:checking` | **[IMPLEMENTED]** Declares an account name. Stored in `Journal.declared_accounts`. Inline comments (2-space + `;`) and Ledger-style indented subdirectives are stripped. Used by `check accounts` / `-s`. Account types (`type:` tag), display ordering, and tag propagation are deferred. Reference: https://hledger.org/1.52/hledger.html#account-directive |
| commodity directive | `commodity $1,000.00` / `commodity EUR` | **[IMPLEMENTED]** Declares a commodity symbol. Symbol extracted from sample amount (prefix `$`, suffix `EUR`) or bare token. Quoted symbols (`"AAPL 2023"`) supported. Indented `format` subdirectives consumed and ignored. Stored in `Journal.declared_commodities`. Used by `check commodities` / `-s`. Commodity display style and decimal-mark inference are deferred. Reference: https://hledger.org/1.52/hledger.html#commodity-directive |
| payee directive | `payee Whole Foods` | **[IMPLEMENTED]** Declares a payee name. Inline comments stripped with 2-space rule. Quoted names (`payee ""`) supported. Stored in `Journal.declared_payees`. Used by `check payees`. Reference: https://hledger.org/1.52/hledger.html#payee-directive |
| tag directive | `tag TAGNAME` | **[IMPLEMENTED]** Declares a tag name. Stored in `Journal.declared_tags`. Inline comments stripped with the 2-space rule. Indented subdirectives consumed and ignored. Confirmed advisory-only (see Tags section below) — has no effect on inline tag parsing/acceptance; still used only by the deferred `check tags`. Reference: https://hledger.org/1.52/hledger.html#tag-directive |
| decimal-mark directive | `decimal-mark .` / `decimal-mark ,` | **[IMPLEMENTED]** Declares the decimal mark for amount parsing from this point forward in the file. Default is `.` (period). Setting `,` enables EU-style amounts where `.` = thousands separator and `,` = decimal mark (e.g. `1.234,56` → `1234.56`). Raises `ParseError` for any character other than `.` or `,`. Reference: https://hledger.org/1.52/hledger.html#decimal-mark-directive |
| Y directive | `Y 2024` | **[IMPLEMENTED]** Sets the default year for all year-omitted dates that follow this directive in the file. Multiple `Y` directives allowed; last one wins. Reference: https://hledger.org/1.52/hledger.html#y-directive |
| D directive | `D $1,000.00` | **[IMPLEMENTED]** Declares the default commodity symbol and display style for amounts with no explicit symbol. Symbol extracted from sample amount; raw sample stored for style inference alongside `commodity` directives. Reference: https://hledger.org/1.52/hledger.html#d-directive |
| apply account / end apply account | `apply account company` / `end apply account` | **[IMPLEMENTED]** Prepends `PREFIX:` to every account name in postings and `account` directives within the block. Aliases are applied to the base name BEFORE the prefix. A second `apply account` without an intervening `end apply account` replaces the previous prefix and emits a `ParseWarning` in lenient mode. Reference: https://hledger.org/1.52/hledger.html#apply-account-directive |

### Tags (parsing/storage — Stage C Phase 4; queryable since Stage C Phase 6)

`tag:NAME[=REGEX]` is now **[IMPLEMENTED]** — see the Query Language
section below for the query term itself. This section covers parsing and
storage: the raw `Transaction.tags`/`Posting.tags`/`Journal.
declared_account_tags`/`Journal.declared_commodity_tags` fields each
entity's own literal comment tags are stored on. Grounded in `dev-docs/
planning/core-redefinition/19-tag-query-semantics-brief.md`/
`20-tag-parsing-syntax-brief.md`/`23-tag-query-matching-design.md`,
implemented in `ledgerkit/tags.py`.

| Feature | Example | Notes |
|---|---|---|
| Inline `name:value` tags | `; category:food, priority:high` | **[IMPLEMENTED]** Extracted from any comment ledgerkit already captures as `inline_comment` (transaction header, posting, follow-on `;` lines) — never from `#`-led comments, which never carry tags in hledger either. Stored as an ordered `list[tuple[str, str]]` on `Transaction.tags`/`Posting.tags` — **not** a dict; a name may legitimately repeat with a different value (`hledger.1:2525-2529`, "a tag can have multiple values"). Differential-verified against hledger's own `tags` command (`LK-COMPAT-PARSER-TAG-001`). |
| Tag-name grammar | `; foo:bar`, `; foo :bar` | **[IMPLEMENTED]** A tag name is the whitespace-delimited token immediately before a `:`, with **no space** between name and colon — `"foo : bar"` produces **zero** tags (the space voids the candidate entirely), not a tag named `"foo"`. No character-class restriction beyond "not `:`, no internal whitespace" — the manual's "single word or hyphenated word" prose is a usage convention, not the enforced grammar. |
| Bare tag, empty value | `; some-tag:` | **[IMPLEMENTED]** A legal tag with value `""`. |
| Value termination | `; url: http://x.com, other: y` | **[IMPLEMENTED]** A value runs to the next `,` or end of line; trimmed both sides. **No escaping mechanism** — a value cannot contain a literal comma (hledger's own documented limitation, not an omission). A colon inside a value is fine (only `,`/end-of-line terminate it). |
| `account NAME ; tag:value` | `account assets:bank ; type:A` | **[IMPLEMENTED]** Directly-declared tags stored in `Journal.declared_account_tags[NAME]`. Follow-on indented `;` comment lines under the directive are tag-scanned too (confirmed by the manual's own worked example, `hledger.1:2980-2992` — not merely inferred from the shared parsing function). **This storage itself does not include tags inherited from a parent account** — that inheritance is a separate, on-demand computation, `ledgerkit.tags._inherited_account_tags` (private), now built as part of Stage C Phase 6's `tag:` query support (see the Query Language section below). Differential-verified (`LK-COMPAT-PARSER-TAG-SCOPE-001`). |
| `commodity SYMBOL ; tag:value` (commodity tags) | `commodity $  ; rate:2` | **[IMPLEMENTED — Stage C Phase 6]** hledger's "commodity tags" feature (`hledger.1:3550-3556`): a `commodity` directive's comment may declare tags, propagated to every posting whose main amount uses that commodity. Directly-declared tags stored in `Journal.declared_commodity_tags[SYMBOL]`, mirroring `declared_account_tags`'s exact shape and merge behaviour (same-line comment tags plus follow-on indented `;` comment lines, both accumulating across multiple `commodity` directives for the same symbol). **This storage itself is only the declared tags** — propagation onto postings is a separate, on-demand computation, `ledgerkit.tags._commodity_tags`/`_effective_tags` (private), read at `tag:` query-match time, never by mutating `Posting.tags`. Propagation classification: `LK-COMPAT-PARSER-TAG-COMMODITY-001` (parsing/storage), `LK-COMPAT-QUERY-TAG-COMMODITY-001` (query-time propagation) — see the Query Language section below. |
| `date:`/`date2:` posting-comment tags | `expenses:food  $10  ; date:6/1` | **[IMPLEMENTED]** Sets `Posting.date_override`/`date2_override` — a per-posting effective-date override, computed via `ledgerkit.tags.effective_date`/`effective_date2` (never mutating `Transaction.date`/`date2`). **Only in a posting's own comment** — the identical tag written in a transaction-level or `account`-directive comment has no override effect at all, it's an ordinary tag there (confirmed via hledger's own `check-tags.test`). An unparseable date value is a hard `ParseError` (strict mode) or collected error (lenient mode, override left unset). Differential-verified against hledger's own `register` date-grouping behaviour (`LK-COMPAT-PARSER-POSTINGDATE-001`). This is a **second, independent** mechanism from `Transaction.date2` (the `=DATE2` header suffix) — a journal may use both simultaneously. |
| `tag` directive vs. inline tags | `tag TAGNAME` | **[IMPLEMENTED, confirmed advisory-only]** The `tag` directive has **zero** enforcement effect on inline tag parsing — an undeclared (or even hledger-reserved-name) inline tag parses and runs fine; only the separate, still-deferred `check tags` validation consults declared names. Differential-verified (`LK-COMPAT-DIRECTIVE-TAG-001`). |
| Effective tags: same-name, different-value precedence | posting `; rate:1` + its account declared `; rate:3` | **[IMPLEMENTED — Stage C Phase 6]** hledger's manual reads like exclusion ("posting tags override account tags override commodity tags"), but live differential testing shows this is **not** shadowing for `tag:` query-matching purposes — every differently-valued, same-named tag from every source (posting/transaction/account-inherited/commodity-propagated) remains **simultaneously, independently matchable**; `Data.List.union`'s dedup in hledger's own `postingAddTags` is by the full `(name, value)` tuple, not by name alone. Ledgerkit's `ledgerkit.tags._effective_tags` is a plain concatenation of all four sources, deliberately with no shadowing/exclusion logic. Executable evidence, not the manual's prose, is the basis (`LK-COMPAT-QUERY-TAG-INHERIT-001`/`LK-COMPAT-QUERY-TAG-COMMODITY-001` `reason:` fields). |

### Validation / Checks

ledgerkit runs validation checks after parsing. Checks are grouped into tiers.

| Check | Tier | Description |
|---|---|---|
| `parseable` | basic (always) | Journal parsed without `ParseError` — trivially satisfied after load |
| `autobalanced` | basic (always) | Each transaction nets to zero per commodity; one elided posting per transaction is allowed and is inferred to balance |
| `assertions` | basic (always) | All balance assertions in posting lines pass; disable with `-I`/`--ignore-assertions` |
| `accounts` | strict (`-s`) | All posting accounts appear in `declared_accounts` |
| `commodities` | strict (`-s`) | All commodity symbols in amounts appear in `declared_commodities`; zero-amount postings (commodity `""`) are exempt |
| `payees` | other (named) | All transaction descriptions appear in `declared_payees` |
| `ordereddates` | other (named) | Transactions appear in non-decreasing date order |
| `uniqueleafnames` | other (named) | No two accounts share the same final colon-segment |

**Deferred checks** (out of scope for v1): `balanced` (exact-balance assertions on totals), `recentassertions`, `tags`.

### Balance assertions

Balance assertions appear inline after a posting amount and verify the running balance at that point in the journal. They are checked in date order (then parse order within the same date), which means transactions can be freely reordered without breaking assertions.

Supported syntax:

| Syntax | Description |
|---|---|
| `amount = EXPECTED` | Single-commodity, subaccount-exclusive |
| `amount == EXPECTED` | Sole-commodity, subaccount-exclusive (no other commodity may have a non-zero balance) |
| `amount =* EXPECTED` | Single-commodity, subaccount-inclusive (sum includes all sub-accounts) |
| `amount ==* EXPECTED` | Sole-commodity, subaccount-inclusive |

The assertion amount must be the same commodity as the posting amount (or the commodity being checked). Costs are ignored (not yet implemented). Posting status (unmarked/pending/cleared) does not affect assertions.

**Balance assignments** (`= EXPECTED` with no explicit posting amount) are parsed — the posting amount is stored as `None` — but the implied amount is **not** inferred from the assertion; this is a known limitation deferred to a future milestone.

---

## Query Language (Stage C)

**Wired into the CLI's `-q`/`--query` flag** (`balance`, `register`,
`accounts`, `stats` — Stage C Phase 2; `print` — Stage C Phase 3) via a
**private, internal-only** integration (`reports.py`'s `_query_ast`
parameter for the first four; `cli.py`'s own local filtering, using the
same `ledgerkit.query.eval.matches_transaction`, for `print` — neither is
part of the public, documented API; see `knowledge/DECISIONS.md`,
2026-09-16). Query text is parsed into a `QueryNode` AST and evaluated
directly against `Transaction`/`Posting` objects via `ledgerkit.query.
eval.matches_posting`/`matches_transaction`; see `dev-docs/api-spec.md`'s
`ledgerkit/query/` section for that subpackage's own public API and
`dev-docs/planning/core-redefinition/17-query-semantics-brief.md` for the
hledger-source-verified semantics grounding each row below. `print -q`
shows the **whole** matching transaction (every posting, unfiltered
within it) when any posting/the transaction itself matches — differential-
verified against hledger's own `print` behaviour, which does the same.
`check` does not accept `-q` — checks apply to the whole journal by
design.

| Term | Example | Notes |
|---|---|---|
| `acct:REGEX` / bare pattern | `acct:food`, `food` | **[IMPLEMENTED]** Case-insensitive infix match against a posting's account name; bare pattern defaults to `acct:`. A transaction matches if any of its postings match. Differential-verified against hledger 1.52.4 (`LK-COMPAT-QUERY-ACCT-001`, `status: self-verified` — see `dev-docs/compat-register/README.md`'s Stage C Phase 5 note on the new verification-independence process). An empty pattern (`acct:` alone) now raises `UnsupportedRegexConstructError` (Stage C Phase 7, breaking change, matches hledger — see the `tag:` row below for the full writeup). |
| `desc:REGEX` | `desc:amazon` | **[IMPLEMENTED]** Case-insensitive infix match against the transaction description; a posting inherits its transaction's match. Differential-verified (`LK-COMPAT-QUERY-DESC-001`, `status: self-verified`). An empty pattern (`desc:` alone) now raises `UnsupportedRegexConstructError` (Stage C Phase 7, breaking change, matches hledger — see the `tag:` row below for the full writeup). |
| `date:PERIODEXPR` | `date:2024-01-15`, `date:2024-01-01..2024-02-01` | **[IMPLEMENTED — simple dates only]** A single full date matches only that one day; a range's end date is **exclusive** (matching real hledger `date:` span semantics — differential-verified, `LK-COMPAT-QUERY-DATE-001`, `status: self-verified`). This differs from the existing `Query.date_to`, which is inclusive. hledger's smart/relative/period dates (`today`, `last month`, `2024Q1`, etc.) are **not** implemented — see Undecided/Future. |
| `depth:N` / `depth:REGEX=N` | `depth:2`, `depth:assets=2` | **[IMPLEMENTED — redesigned Stage C Phase 5]** No longer a `QueryNode`/selection predicate at all (a Phase 1-4 mistake, corrected). `depth:`/`--depth` is a **report-display clipping/aggregation option** (`ledgerkit.query.depth.DepthSpec`), matching hledger exactly: deeper accounts are truncated and aggregated into their depth-N ancestor, never excluded, for `balance`/`register`/`accounts`; multiple `depth:` terms within one query combine via the smaller (more restrictive) flat depth winning, order-independent (hledger's own `Semigroup DepthSpec`, confirmed live — NOT "last wins," a separate rule for multiple `--depth` CLI flags Ledgerkit has no flag for yet); custom `REGEX=N` depths combine via hledger's own most-specific-match-wins precedence. `print` deliberately ignores `depth:` entirely (confirmed via `EntriesReport.hs` source and the pinned binary — hledger's `print` never consults depth at any layer). `stats` is a genuine, source-confirmed **exception**: its `account_count`/`account_depth` fields come from hledger's own raw exclusion semantics (`Ledger.hs`'s `ledgerFromJournal`), not clipping — replicated exactly, not diverged from. The earlier `Depth` AST node (a pure boolean exclusion predicate, genuinely different from hledger's `depth:`) is kept as `ledgerkit.query.ast.MaxAccountLevel` — a disclosed, Python-API-only Ledgerkit-native primitive with no `-q` string syntax, so `-q "depth:..."` can never mean anything other than hledger's own semantics. See `dev-docs/planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md`, `LK-COMPAT-QUERY-DEPTH-001` (reclassified `compatible`, `status: verified` by an independently-dispatched `compat-differential-tester`, per the new process in `09-compatibility-system.md` §9.6), and `LK-COMPAT-QUERY-DEPTH-STATS-001` (also `status: verified`). `knowledge/EDGE_CASES.md` EC-017 marked resolved. An empty `REGEX` half (`depth:=N`) now raises `UnsupportedRegexConstructError` (Stage C Phase 7, breaking change, matches hledger — see the `tag:` row below for the full writeup). |
| `status:` / `status:*` / `status:!` / `status:0` / `status:1` | `status:*` | **[IMPLEMENTED]** Cleared/pending/unmarked match; `0`/`1` are hledger's own synonyms for unmarked/cleared. Always transaction-level — Ledgerkit's model has no per-posting status override (unlike hledger). `*`/bare differential-verified; `0`/`1` synonyms not yet (`LK-COMPAT-QUERY-STATUS-001`, `status: self-verified` with that gap noted). |
| `not:` negation | `not:acct:food` | **[IMPLEMENTED]** Wraps and negates any other term; stacks (`not:not:x`). A negated term is always individually AND'd — it never joins a same-prefix OR group, even when the same prefix appears unnegated elsewhere in the query. `not:depth:...` is rejected at parse time (depth is a report option, not a predicate — Stage C Phase 5). Differential-verified for negation and different-prefix AND; the negated-same-prefix case is not yet (`LK-COMPAT-QUERY-BOOLCOMBINE-001`, `status: self-verified` with that gap noted). |
| Implicit AND / same-prefix OR | `acct:a acct:b date:2024` | **[IMPLEMENTED]** Unnegated `acct:`/`desc:`/`status:` terms of the same type OR-combine with each other; every other term (including any negated term, regardless of its prefix) AND-combines individually — replicated from hledger's actual `combineQueriesByType`, not an independent design choice. |
| `tag:NAME[=REGEX]` | `tag:category=food`, `tag:rate=3` | **[IMPLEMENTED — Stage C Phase 6]** `NAME` (required) and `REGEX` (optional; bare `tag:NAME` matches any value, including empty) are split on the **first** `=` only — a value itself containing `=` (e.g. `tag:rate==0.05`) preserves everything after the first `=`. Matches a posting's/transaction's **effective** tags — the full four-source union: its own literal comment tags, its transaction's own tags, its account's declared-and-inherited tags (rules A-D), and its main amount's commodity's declared tags (the "commodity tags" feature, see Tags section above) — computed on demand via `ledgerkit.tags._effective_tags` (private), never by mutating `Posting.tags`/`Transaction.tags`. Multiple `tag:` terms AND-combine (never OR), same as any other non-`acct:`/`desc:`/`status:` term (`LK-COMPAT-QUERY-TAG-COMBINE-001`). A transaction matches (`print`) if its own tags directly match OR any posting's effective tags match. `not:tag:...` is valid (`tag:` is an ordinary predicate, unlike `depth:`). Evaluating a `Tag` node needs `Journal` access — `matches_transaction`/`matches_posting` gained a `journal: Journal \| None = None` parameter (see `dev-docs/api-spec.md`); a `Tag` node evaluated with no `journal` raises `ValueError`, never silently narrowing to own-tags-only. `accounts tag:X` uses a genuinely **narrower** visibility than every other command — see its own row below. Independently differential-verified by a genuinely separate `compat-differential-tester` dispatch (`LK-COMPAT-QUERY-TAG-001` [see note below], `LK-COMPAT-QUERY-TAG-COMBINE-001`, `LK-COMPAT-QUERY-TAG-INHERIT-001` — including the no-shadowing/union finding — `LK-COMPAT-QUERY-TAG-COMMODITY-001`, all now `status: verified`). **Empty-pattern divergence fixed, Stage C Phase 7** (`26-query-regex-empty-pattern-design.md`): `tag:NAME=` (an empty value pattern) previously diverged from real hledger — hledger rejects an empty regex outright at parse time (`Error: This regular expression is invalid or unsupported`), Ledgerkit used to compile it and match any value, including empty. **Not `tag:`-specific** — the same gap existed for `acct:`/`desc:`/`depth:REGEX=N` (see their own rows above), root cause `ledgerkit.query.regex.compile_hledger_regex`/`validate_hledger_regex` not rejecting an empty pattern the way hledger's regex-tdfa dialect does. **Now fixed**: `validate_hledger_regex("")`/`compile_hledger_regex("")` raise `UnsupportedRegexConstructError` — a **breaking change**, not backward-compatible, made while Ledgerkit is pre-`1.0.0` (`1.0.0.dev1`, see `dev-docs/versioning.md`). Only the literal empty pattern string is rejected — `.*`/`a*`/`^$`/`()` remain accepted, matching hledger's own precise scope (`25-query-regex-empty-pattern-matrix.md`). Pending independent `compat-differential-tester` verification before any compat-register entry is promoted: `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` stays open in `UNEXPLAINED.md` until that verification lands and resolves it (`dev-docs/compat-register/schema.md`'s resolution lifecycle — a new `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` entry, not an in-place edit of the mismatch entry); `LK-COMPAT-QUERY-TAG-001` remains `status: proposed` until then too. A separate, unrelated divergence (`(|)` and other empty-alternation-branch syntax) is tracked independently (`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`) and was explicitly **not** touched by this fix. |
| `accounts tag:X` visibility (narrower than other commands) | `accounts tag:rate=3` | **[IMPLEMENTED — Stage C Phase 6, replicates hledger]** hledger's plain (non-`--declared`) `accounts tag:X` is a genuine, source-confirmed exception: it shows only **transaction-level** and **account-inherited** tags — **posting-own and commodity-propagated tags are NOT visible** to it (`journalPostingsKeepAccountTagsOnly` composed with `postingAllTags`'s unconditional `++ ttags`). Ledgerkit replicates this exactly via `ledgerkit.tags._accounts_effective_tags` (private) — used only by `ledgerkit.reports.accounts`'s own `Tag`-matching dispatch; `balance`/`register`/`print`/`stats` are unaffected and continue to use the full four-source `_effective_tags`. Independently differential-verified (`LK-COMPAT-QUERY-TAG-ACCOUNTS-001`, `compatible`, `status: verified`, confirmed all four visibility cases individually on their own fixture). |
| `cur:REGEX` | `cur:USD` | Not implemented — Stage C follow-on work. |
| `PythonRegex` extension syntax | (undecided) | Not implemented — the `HledgerRegex`-compatible subset (see below) is the only dialect available so far; no escape hatch to full Python `re` yet. |

**Regex dialect (`HledgerRegex`):** `acct:`/`desc:`/`tag:`'s name and value
patterns/bare-pattern arguments are validated against the hledger-
compatible subset before use — literals,
`.`, `*`, `+`, `?`, `{n,m}`, alternation `|`, plain groups, anchors, plain
bracket expressions, and `\b`/`\B` word boundaries are accepted; `(?...)`
constructs (inline flags, named/non-capturing groups, lookaround),
in-pattern backreferences (`\1`), GNU `\<`/`\>` boundaries, Perl shorthand
classes (`\d`/`\w`/`\s`), POSIX named classes (`[[:alpha:]]`), and lazy
quantifiers (`*?`) all raise `UnsupportedRegexConstructError` rather than
being silently reinterpreted with Python `re`'s (different) semantics.

---

## Out of Scope (v1)

These features will **not** be implemented in v1. Attempting to parse them
will either be silently ignored or raise a `ParseError` — documented per
feature below.

| Feature | hledger syntax | v1 behaviour |
|---|---|---|
| Auto postings | `= expenses:food` rules | Skipped; `ParseWarning` emitted in lenient mode (`parse_string_lenient`); no rule expansion |
| Periodic transactions | `~ monthly` | Skipped; `ParseWarning` emitted in lenient mode; no forecast expansion |
| Timeclock entries | `i`, `o`, `b`, `h` records | `ParseError` |
| Decimal comma | `1.234,56` (EU style) | **Supported** via `decimal-mark ,` directive — amounts parsed using comma as decimal mark |
| Secondary dates | `2024-01-15=2024-01-20` | **[IMPLEMENTED]** — stored in `Transaction.date2`; see Transactions table above |
| Lot prices / cost annotations | `10 AAPL @ $150.00`, `{$182}` | **[IMPLEMENTED (stripped)]** — annotations removed before amount parsing; cost text stored in `Posting.cost_raw`; lot metadata discarded |
| Balance assertions | `assets:checking = £500` | **[IMPLEMENTED]** — see `assertions` check above |
| Virtual postings | `(expenses:food)` or `[expenses:food]` | `ParseError` |
| Multi-currency auto-conversion | | Not supported |

---

## Undecided / Future

- Multiple commodities in one transaction
- Account type inference from name prefixes (`assets`, `liabilities`, etc.)
- Smart dates (hledger relative date expressions such as `today`, `yesterday`,
  `last month`, `next year`) — not currently planned for v1
- Comment "other syntax" — hledger accepts additional comment introducers in
  certain contexts (e.g. `*` in org-mode files); not currently planned for v1

---

## Compatibility Notes

- ledgerkit does **not** aim for 100% hledger compatibility in v1.
- The goal is to correctly parse the most common single-currency personal
  finance journal files.
- When a file is not parseable, `ParseError` should include the line number
  and a clear message explaining what was unexpected.

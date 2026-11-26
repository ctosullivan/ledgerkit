# Journal Format Reference

ledgerkit reads `.journal` and `.ledger` files (case-insensitive extension
check; every other extension — including hledger's own `.j` alias — is
rejected with a `ParseError`, loader@v1#loader-007). The format follows
the [hledger 1.52](https://hledger.org/1.52/hledger.html) journal
specification, with some scope boundaries and a handful of confirmed
limitations noted explicitly below rather than silently.

> **About the citations in this document.** Claims below are annotated
> `(topic@v1#assertion-id)` where they trace to a specific, evidence-backed
> finding from this project's clean-room documentation review (frozen
> assertions checked against the code, tests, or a direct execution during
> review — not just read from the manual or inferred). A claim that
> Ledgerkit's behaviour is "compatible" with hledger reflects what the
> project's own compatibility register asserts about itself, at varying
> verification tiers — see `dev-docs/hledger-compatibility.md` for the
> full picture, including which claims have been checked against a real
> running `hledger` and which have not.

---

## Transaction Block

A transaction block has a header line followed by one or more posting lines,
terminated by a blank line (or end of file).

```
2024-01-15 * (INV-42) Groceries  ; weekly shop
    expenses:food:groceries   £85.40
    assets:bank:checking
```

### Header fields (in order)

| Field | Required | Example | Notes |
|---|---|---|---|
| Date | Yes | `2024-01-15` | See Date Formats below |
| Secondary date | No | `=2024-01-20` | See Secondary Dates below |
| Status flag | No | `*` or `!` | `*` = cleared, `!` = pending |
| Code | No | `(INV-42)` | Any text in parentheses |
| Description | No | `Groceries` | Free text |
| Inline comment | No | `; weekly shop` | After `;` |

A single regex captures all of the above from one non-indented header line:
primary date, optional secondary date, optional status flag, optional
parenthesised code, a lazily-matched description, and an optional
`;`-introduced inline comment (journal-parsing@v1#journal-parsing-001).

### Secondary dates

A header may carry a secondary ("auxiliary") date, introduced by `=`
immediately after the primary date, with no space:

```
2024-02-20=2024-02-22 * Rent
    expenses:rent  £900
    assets:bank
```

This sets the transaction's primary date to `2024-02-20` and its secondary
date (`Transaction.date2`) to `2024-02-22`
(journal-parsing@v1#journal-parsing-001). A trailing `=` with nothing
date-shaped after it is simply not matched by the secondary-date group, so
the primary date is used alone and no error is raised
(journal-parsing@v1#journal-parsing-001). A posting's own comment can
separately override its *effective* secondary date via a `date2:` tag —
see [Tags](#tags) below.

---

## Date Formats

All three separator characters are accepted. Leading zeros on month and day
are optional, and the two separators used within one date need not match
each other. The year may be omitted — ledgerkit infers it from the current
calendar year unless a `Y` directive has set a different default (see
[Directives](#directives)) (journal-parsing@v1#journal-parsing-002).

| Format | Example |
|---|---|
| `YYYY-MM-DD` | `2024-01-15` |
| `YYYY/MM/DD` | `2024/1/15` |
| `YYYY.MM.DD` | `2024.1.15` |
| `MM-DD` | `01-15` (year inferred or from `Y`) |
| `M/D` | `1/15` (year inferred or from `Y`) |

An impossible calendar date (e.g. month 13) is a hard `ParseError`
(journal-parsing@v1#journal-parsing-002).

---

## Postings

Each posting line maps an account name to an amount. The account name and
amount **must** be separated by two or more spaces — a single space is
treated as part of the account name, not a delimiter
(journal-parsing@v1#journal-parsing-003).

```
    expenses:food:groceries   £85.40     ← two spaces before £
    assets:fun money          £10.00     ← "fun money" is part of the account name
```

A posting line with only a single space between what looks like an
account and an amount is not split there at all — the whole line,
amount-looking text included, becomes the account name
(journal-parsing@v1#journal-parsing-003).

**Elided amount:** At most one posting per transaction may omit its
amount. ledgerkit records it as `None` at parse time; a second elided
posting in the same transaction block is rejected with a `ParseError`
(journal-parsing@v1#journal-parsing-005).

```
    assets:bank:checking                 ← no amount — inferred from other postings
```

**Resolution is a separate, opt-in step, not automatic parsing behaviour.**
A dedicated function, `resolve_elision`, computes what an elided posting's
amount should be — if exactly one posting in the transaction has no
amount, it sums the other, explicit postings per commodity and replaces
the elided posting with one synthetic, inferred posting per commodity
(sorted by commodity symbol), spliced in at the elided posting's original
position. Report functions call this on the caller's behalf when
producing output, but `parse_string`/`parse_string_lenient` themselves
leave a transaction's elided posting as `amount = None` — nothing inside
the parser calls `resolve_elision` automatically
(journal-parsing@v1#journal-parsing-005, classified `aligned` against an
independent as-built reconstruction that confirmed this live).

---

## Amounts

| Style | Example | Notes |
|---|---|---|
| Prefix symbol | `£30.00`, `$10` | Symbol before quantity |
| Suffix symbol | `30.00 EUR` | Symbol after quantity |
| Negative | `-£5.00` | Leading minus sign |
| Mid-minus | `$-300` | Minus between prefix symbol and quantity — equivalent to `-$300` |
| Thousands | `1,234.56` | Comma thousands, period decimal (default) |
| Space-grouped | `1 000 000 JPY` | Space-separated digit groups, normalised before parsing |
| Integer | `£100` | No decimal part required |

(journal-parsing@v1#journal-parsing-004)

By default, commas are thousands separators and a period is the decimal
mark; a `decimal-mark ,` directive reverses this (period-thousands,
comma-decimal) for every amount parsed from that point forward in the
file — see [Directives](#directives)
(journal-parsing@v1#journal-parsing-004). E-notation is also normalised
before the main amount pattern is applied
(journal-parsing@v1#journal-parsing-004). An amount with no commodity
symbol at all is a `ParseError` ("amount has no commodity symbol") unless
a default commodity has been set via a `D` directive
(journal-parsing@v1#journal-parsing-004).

### Balance assertions, cost, and lot annotations

A posting's amount token may additionally carry a **balance assertion**
(one of `=`, `==`, `=*`, `==*`, requiring whitespace on both sides of the
marker), a **cost annotation** (`@ PRICE` for a unit cost, or `@@ TOTAL`
for a total cost), and/or a **lot annotation** (`{AMOUNT}`, `{{AMOUNT}}`,
`[DATE]`, or `(LABEL)`) — and these are mutually composable on a single
posting (journal-parsing@v1#journal-parsing-009):

```
    assets:cash   10 AAPL {$182.00} [2023-11-01] (lot1) @ $185.00 = $1850.00
```

They are stripped and parsed in a fixed order: cost annotation first, then
lot annotations, then space-digit-group normalisation, then the main
amount regex (journal-parsing@v1#journal-parsing-009). Balance assertions
are checked automatically on every command run (they are a "basic tier"
check, not opt-in) — see `dev-docs/hledger-compatibility.md`.

**Confirmed limitation — balance-assignment elision syntax
(`account  = AMOUNT`, with no separate amount written before the `=`) is
not implemented, and fails in two different ways depending on commodity
placement and decimal mode.** hledger's own "balance assignment" syntax
lets a posting's amount be inferred entirely from a trailing assertion.
Ledgerkit's assertion-marker detector requires whitespace *before* the
marker, so a bare leading `=` is never recognised as an assertion at all —
the whole string, `=` included, is instead handed to ordinary amount
parsing (journal-parsing@v1#journal-parsing-009):

- For a **prefix-commodity amount** (e.g. `a  = $100`), this produces a
  clean, if unhelpfully-worded, `ParseError: invalid amount: '= $100'`
  (journal-parsing@v1#journal-parsing-009).
- For a **suffix-commodity amount under comma-decimal mode** (e.g.
  `a  = 100,00 EUR`), the attempt does **not** fail at all — it silently
  produces a posting with `commodity` literally set to the single
  character `=` and **no** balance assertion, because the prefix-symbol
  amount regex has nothing excluding `=` from the characters it will
  accept as a currency symbol. This is a confirmed, reproducible
  silent-corruption bug, not a documented deferral — found and confirmed
  by direct execution during this project's own clean-room review, and no
  test in the project's suite currently exercises this branch
  (journal-parsing@v1#journal-parsing-009, classified `partial` against
  the original assertion, which only generalised "it simply fails amount
  parsing" from the prefix-commodity case).

In short: balance-assignment elision is unsupported, and attempting it
either raises a clear parse error or silently produces a wrong, uncaught
result, depending on commodity placement and decimal mode.

---

## Commodity Display Style

Separately from parsing an individual amount, ledgerkit infers a *display
style* per commodity symbol — prefix/suffix position, a space or no space
before/after the symbol, the decimal mark character, the group-separator
character, and how many decimal digits to show. This governs report
output and the writer's round-tripping, not what amounts are accepted as
valid input.

### How the sample is chosen

A journal can supply more than one sample amount for the same commodity
symbol — from a `commodity` directive, a posting amount, or a `P`
(price) directive. Ledgerkit resolves one style per commodity using a
fixed three-tier priority: an explicit `commodity` directive's own sample
amount always wins if one exists for that symbol; otherwise the first
posting amount seen for that commodity (in transaction/posting order);
otherwise the first `P`-directive amount for that commodity
(commodity-styling@v1#commodity-styling-005). This rests on reading the
implementation and its own docstring directly — no test in the available
evidence exercises the directive-overrides-posting priority case end to
end.

### Symbol position, and a confirmed inference bug

The sample string (with any leading minus stripped) is checked for
whether it starts with the commodity symbol (prefix) or ends with it
(suffix); if it matches both ends (e.g. symbol `A` against sample `A5A`),
the prefix check wins (commodity-styling@v1#commodity-styling-001).

**Confirmed limitation.** If the symbol matches *neither* the start nor
the end of the sample, the entire sample string — including whatever
unrelated text is present — is fed to decimal/group-separator inference
as if it were the numeric portion. This is not a benign no-op: it has
been directly confirmed by execution to silently produce a nonsensical
precision value (e.g. inferring a style for commodity `EUR` from the
sample `"100.00 USD"` yields a precision of 6, because the unrelated
trailing `" USD"` text gets counted into the digit count). No test in the
project's own suite currently exercises this branch
(commodity-styling@v1#commodity-styling-001).

### Decimal mark vs. group separator

If the numeric part contains only one kind of separator character (only
dots, or only commas) and it occurs exactly once, is not at position 0,
and is followed by exactly 3 digits, it is read as a digit-group
separator (whole integer, thousands grouping, precision 0); otherwise
that character is read as the decimal mark, with precision equal to the
digit count after its last occurrence
(commodity-styling@v1#commodity-styling-002). This heuristic is
inherently ambiguous for a genuinely-intended 3-decimal amount written
with a single separator (e.g. `$1.234`, "one and 234 thousandths" vs.
"1,234 grouped") — an acknowledged limitation, not a bug to be fixed
(commodity-styling@v1#commodity-styling-002).

If the numeric part contains **both** a dot and a comma anywhere,
whichever occurs **rightmost** is always the decimal mark and the other
is the group separator, regardless of repeat counts, and this takes
priority over the single-separator heuristic above
(commodity-styling@v1#commodity-styling-003).

### Formatting negative amounts

For a prefix-style commodity, a negative sign goes *immediately* after the
symbol with no gap, even if the style otherwise spaces the symbol from the
number for positive amounts (e.g. `£-5,000.00`). For a suffix-style
commodity, the sign goes before the number and the suffix keeps its
normal spacing (e.g. `-1,234.56 EUR`). This is an unconditional,
hledger-convention asymmetry, not a simplification
(commodity-styling@v1#commodity-styling-004).

### Overriding a style from the CLI

The CLI's `-c`/`--commodity-style` flag accepts a sample string such as
`"1,000.00 USD"` or `"$1,000.00"` to force one commodity's style
explicitly, scoped strictly to the named commodity symbol — it has no
effect on any other commodity in the same report
(commodity-styling@v1#commodity-styling-006).

### Known limitation in multi-commodity report formatting

One report-building code path — formatting a single report section's rows
into a display table — has a self-acknowledged, single-commodity
limitation: it picks one commodity's style (an arbitrary/first key out of
the resolved style map) and applies it to *every* row, regardless of
which commodity each row's value actually came from. This is called out
directly in the code's own comments as a deferred limitation, in contrast
to whole-journal formatting elsewhere in the same codebase, which does
look up the correct per-commodity style for each row
(commodity-styling@v1#commodity-styling-008).

---

## Account Names

- Colon-separated hierarchy: `expenses:food:restaurants`
- Case-sensitive: `Assets:Bank` ≠ `assets:bank`
- Spaces allowed: `expenses:fun money` (use two spaces before the amount
  so the parser's account/amount split doesn't cut it off,
  journal-parsing@v1#journal-parsing-003)

---

## Comments

### Standalone line comments

Any line beginning with `#` or `;` at column 0 is a comment and is silently
ignored. These may appear anywhere in the file — before, after, or between
transactions — without affecting parsing (journal-parsing@v1#journal-parsing-006).

```
# a top-level note
; another top-level note

2024-01-15 Coffee
    expenses:food  £4.50
    assets:bank
```

### Same-line inline comments

A `;` after an entry (transaction header or posting line) begins an inline
comment that runs to the end of the line. **Only `;` works as an inline
comment delimiter; `#` does not** (journal-parsing@v1#journal-parsing-006).

```
2024-01-15 Coffee  ; business meeting      ← transaction inline comment
    expenses:food  £4.50  ; cappuccino     ← posting inline comment
    assets:bank
```

Both comments are stored in the `inline_comment` field of the corresponding
`Transaction` or `Posting` object. They can be round-tripped via the writer.

### Follow-on comment lines (inside transactions)

An **indented** `;` line inside a transaction block is a follow-on comment.
It is appended (newline-separated) to the `inline_comment` of the preceding
posting, or to the transaction's `inline_comment` if it appears before any
postings (journal-parsing@v1#journal-parsing-006).

```
2024-01-15 Coffee
    ; this is a transaction comment (before first posting)
    expenses:food  £4.50
    ; this appends to expenses:food.inline_comment
    assets:bank
```

An **indented** `#` line inside a transaction extends the transaction's source
span (line coverage) but its text is not captured in any comment field.

> **Key distinction:** A `;` or `#` at **column 0** is always a top-level
> comment, even inside an open transaction block with no blank-line separator.
> Only **indented** lines (leading whitespace) are treated as follow-on
> comments (journal-parsing@v1#journal-parsing-006).

### Block comments

A `comment` directive opens a block that is ignored until `end comment` or
end of file. Anything may appear inside the block — transaction-like lines,
directives, other `comment` keywords — all are discarded
(journal-parsing@v1#journal-parsing-007).

```
comment
Everything here is ignored, including
  2024-01-01 fake transaction
  account expenses:food
end comment
```

The `comment` line may have trailing text (it is ignored). An unclosed block
silently consumes the rest of the file.

---

## Tags

A `name:value` pair inside a `;` comment is a **tag**. Tags can appear in a
transaction's inline comment, a posting's inline comment, an `account`
directive's inline comment, or a `commodity` directive's inline comment
(same-line or indented follow-on lines, exactly like ordinary comment
text) (tags@v1#tags-005, tags@v1#tags-006):

```
2024-01-15 Coffee  ; category:food, business:yes
    expenses:food  £4.50  ; splitwith:Alex
    assets:bank

account expenses:food  ; type:E
commodity $  ; symbol:dollar
```

**Tag name**: the last whitespace-delimited word immediately before the
`:`. A space between that word and the `:` voids the tag entirely (it is
not extracted at all, not even with an empty name) — `foo bar :baz` has no
tag (tags@v1#tags-005). A bare `name:` with nothing after the colon is a
legal tag with an empty value.

**Tag value**: everything after the `:` up to the next `,` or end of line,
with leading/trailing whitespace trimmed. There is no escape mechanism —
a value can never contain a literal comma, treated as a real, permanent
limitation of the grammar rather than an omission to be fixed. A colon is
fine inside a value (tags@v1#tags-006).

**Repeated names**: the same tag name may appear more than once in a
comment (or across a transaction and its own postings); all occurrences
are kept — tags are stored as an ordered list of `(name, value)` pairs,
never collapsed into a dict (tags@v1#tags-007).

**`date:` / `date2:` posting-comment tags**: when a *posting's own*
comment (not the transaction's, not an account directive's) contains a
`date:` or `date2:` tag, it sets a real per-posting date override for that
posting, in addition to being stored as an ordinary tag. If more than one
`date:` (or `date2:`) tag appears on the same posting, the first one wins.
The same tag name in a transaction-level or `account`-directive comment
has no such effect — it is stored as a plain tag only
(journal-parsing@v1#journal-parsing-010, tags@v1#tags-008). An unparseable
date value in such a tag is a hard error in strict parsing, or collected
with the override left unset in lenient parsing
(journal-parsing@v1#journal-parsing-010).

```
2024-01-15 Coffee
    expenses:food  £4.50  ; date:2024-01-20
    assets:bank
```

Here, the `expenses:food` posting's effective date is `2024-01-20` for
reporting purposes, while the transaction's own date remains `2024-01-15`.
The *effective* secondary date used when reading a posting back out
follows a precedence chain: the posting's own `date2` override, then the
transaction's own secondary date, then — distinctively — the posting's
own *primary* date override reused as a secondary-date fallback, then
finally the transaction's primary date (tags@v1#tags-008).

**Querying by tag**: `-q "tag:NAME[=REGEX]"` filters `balance`/`register`/
`accounts`/`stats`/`print` by a posting's or transaction's *effective*
tags — not just its own literal comment, but also:

- its transaction's own tags (a posting with no comment of its own still
  matches a tag declared only on its transaction's header line);
- its account's declared tags, **inherited from every ancestor account**
  (an `account assets:bank ; type:A` directive's tag applies to
  `assets:bank` and every account under it, e.g. `assets:bank:savings`,
  even with no comment of its own);
- its main amount's commodity's declared tags (a `commodity $ ; rate:2`
  directive's tag applies to every posting whose amount uses `$`).

(tags@v1#tags-001; account tag inheritance walks every ancestor prefix,
never just the exact declared account, and a sibling branch does not
inherit from a different sibling — tags@v1#tags-004.)

Same-named tags from different sources with **different values** are all
independently matchable — hledger's manual describes this as "posting
tags override account tags override commodity tags," but that does not
mean only one wins for query-matching purposes: a query for any one of
those values matches, and this holds even for two sources declaring the
exact same `(name, value)` pair, which is preserved twice rather than
collapsed (tags@v1#tags-002). `accounts -q "tag:X"` is a deliberate
exception — it only sees transaction-level and account-inherited tags,
not a posting's own comment tags or commodity-propagated tags, matching
hledger's own `accounts` command (tags@v1#tags-003). An entry in the
compatibility register confirming this commodity-tag-propagation behaviour
has been checked by an independently-dispatched verifier against real
`hledger` command output, not merely read from the code
(compat-system@v1#compat-system-007). See `-q`/`--query` in
[`usage.md`](usage.md) and `dev-docs/hledger-compatibility.md` for the
full reference.

---

## Directives

Ledgerkit recognises the following non-indented directives
(journal-parsing@v1#journal-parsing-007):

| Directive | Effect |
|---|---|
| `account` | Declares an account, optionally with its own comment tags (see [Tags](#tags)). |
| `commodity` | Declares a commodity, with a sample amount used for display-style inference (see [Commodity Display Style](#commodity-display-style)) and optionally its own comment tags. |
| `payee` | Declares a payee name. |
| `tag` | Declares a tag name. |
| `decimal-mark` | Switches which of `,`/`.` is treated as the decimal mark for amounts parsed from that point forward (see [Amounts](#amounts)). Not retroactive — amounts before the directive keep the previous mode, and mixing formats after switching is a `ParseError`. |
| `P` | Records a market/commodity price on a given date — see [P Directive](#p-directive-market-prices). |
| `alias` / `end aliases` | Declares an account-name rewrite rule — see [Alias Directive](#alias-directive-account-name-rewriting). |
| `Y` | Sets the default year used when a date omits one (see [Date Formats](#date-formats)). |
| `D` | Sets a default commodity and style for amounts written with no commodity symbol at all (see [Amounts](#amounts)). |
| `apply account` / `end apply account` | Prefixes a directive-declared account scope onto subsequent postings. |
| `comment` / `end comment` | Brackets a block comment — see [Block comments](#block-comments). |

Two further headers are recognised but their bodies are deliberately not
implemented: a line beginning `~` (hledger's periodic transaction rule)
and a line beginning `=` at column 0 (hledger's auto-posting rule) are
both recognised, their following indented lines are skipped rather than
parsed as ordinary postings, and a `ParseWarning` (a non-fatal subclass of
parse error, collected rather than raised in lenient mode) is emitted for
each. This is a disclosed, deliberate scope deferral, not a bug
(journal-parsing@v1#journal-parsing-007).

An `account`/`commodity`/`payee`/`decimal-mark`/`Y`/`D`/`P`/`alias` entry
cites tests directly (`tests/test_directives/test_directives.py`); the
`account`-directive-behaves-like-hledger claim in the compatibility
register was, as of the last review, still only checked by reading the
code/docs rather than by an independently-dispatched comparison against a
real `hledger` run (compat-system@v1#compat-system-006) — see
`dev-docs/hledger-compatibility.md` for current status.

**Confirmed limitation — a directive inside an open transaction can
silently drop postings.** If an `account`, `commodity`, `payee`, or `tag`
directive line appears between two posting lines of a transaction block
that is still open, the still-open transaction is never flushed or
closed — unlike what happens for a new transaction header, a periodic/
auto-posting rule header, or a `comment` block, each of which does
correctly close out any open transaction first. Instead, every subsequent
indented line of that same block (including what were meant to be further
posting lines) is silently treated as a sub-directive continuation line
and dropped entirely — with no `ParseError`, no `ParseWarning`, nothing.
This is a genuine, observable, silent-data-loss gap: a transaction can
lose some of its own postings with no indication anything went wrong,
purely because an unrelated directive happened to be written between two
of its posting lines (journal-parsing@v1#journal-parsing-007, classified
`partial` against the original directive-inventory assertion, which did
not itself state this failure mode).

### Strict vs. lenient parsing, and two confirmed exceptions

Ledgerkit exposes two parsing entry points with different error policies:
`parse_string` raises on the first malformed line; `parse_string_lenient`
is documented and designed to never raise, instead collecting every error
into a returned list, discarding only the one malformed transaction, and
resuming at the next blank line or transaction header — intended for
callers such as an editor that re-parses on every keystroke
(journal-parsing@v1#journal-parsing-008).

**Confirmed limitation — the "never raises" guarantee is broken for two
different directive shapes:**

1. A malformed `commodity` directive (an empty body, an unterminated
   quoted symbol, or an otherwise-unparseable body) is not guarded at
   all, and raises straight out of `parse_string_lenient` too,
   contradicting its own documented contract. This is a real,
   reproducible parser bug, not a documentation nuance — confirmed by
   direct execution, with no test in the project's suite exercising this
   input shape (journal-parsing@v1#journal-parsing-008).
2. An `alias` directive whose pattern compiles but whose replacement text
   contains a backreference with no matching group (e.g. `alias /(foo)/
   = \2`) passes validation when the directive is declared, and only
   fails later, when the alias is actually *applied* to an account name —
   and it fails as an uncaught `re.PatternError` (not even a
   `ParseError`), escaping both the strict and the "never raises" entry
   points alike. This was found during an independent as-built
   reconstruction and is folded into the same "except one" claim above as
   a correction to its count, not a contradiction of its thesis
   (journal-parsing@v1#journal-parsing-008, classified `partial`).

---

## P Directive (Market Prices)

Declares a commodity price on a given date.

```
P 2024-03-01 AAPL $179.00
P 2024-03-15 EUR  1.08 USD
```

Syntax: `P DATE COMMODITY PRICE`

Each P directive is stored as a `PriceDirective` in `journal.prices`.
`journal.prices` is a list that holds every price declaration found in the
file, in the order they appear. Each entry records: the date of the price,
the commodity being priced (e.g. `AAPL`, `EUR`), and the price expressed
as an amount (e.g. `$179.00`) (journal-parsing@v1#journal-parsing-007).

---

## Include Directive (Multiple Files)

Embeds the contents of another journal file at the point of the directive, as
if the entries were written inline. Includes are processed recursively, by
**textual substitution**: each `include` line is recursively replaced by
the full, already-expanded text of the file(s) it names, producing one
single combined text string that is parsed exactly once
(loader@v1#loader-005). This is why directive scope active before an
`include` line (e.g. an active `alias`) naturally propagates into the
included content — the included text is spliced in at the exact point of
the directive within one continuous parse (loader@v1#loader-005).

```
include accounts.journal
include ../shared/prices.journal
include ~/main.journal
include /home/user/finances.journal
include reports/*.journal
include **.journal
```

Syntax: `include PATH`

### Path resolution

| Path form | Resolution |
|---|---|
| `relative/path.journal` | Relative to the directory of the file that *contains* the `include` line (for nested includes, the immediate parent file's directory — not the root file's, not the process's working directory) |
| `/absolute/path.journal` | Used as-is |
| `~/path.journal` | Tilde expanded to the home directory |
| `glob_*.journal` | Glob-expanded (see below) |

(loader@v1#loader-002)

### Glob patterns

Glob characters `*`, `**`, `?`, and `[range]` are supported, and matches
are sorted for a deterministic order:

- `*` — matches any sequence of characters that are not path separators
- `**` — matches zero or more subdirectories and/or filename prefix characters
- `?` — matches any single character
- `[a-z]` — matches any character in the given range

(loader@v1#loader-002)

Examples:

```
; Include all .journal files in the current directory
include *.journal

; Include all .journal files in this directory tree
include **.journal

; Include year-named files
include 202?.journal
```

The containing file is **always excluded** from glob results, even if the
pattern would match it (loader@v1#loader-003).

A glob pattern that matches no files raises a `ParseError` ("no files
matched"), test-confirmed (loader@v1#loader-007).

**Confirmed limitation — glob metacharacters cannot be escaped, and this
misfires in two different ways, both confirmed by direct execution:**

1. If a plain, non-glob include target is resolved inside a *containing
   directory* whose own name happens to contain a bracket character
   (e.g. a directory literally named `inc[1]`), the resolution logic
   classifies the resulting joined path as a glob, finds zero matches
   even though the target file genuinely exists, and raises an uncaught
   `IndexError` — neither of the two error types the include-resolution
   contract otherwise promises. The project's test suite has no test for
   it, and whether this is an accepted limitation or a bug to fix was
   left as an open design question rather than guessed at
   (loader@v1#loader-002, loader@v1#loader-003, loader@v1#loader-007).
2. A literal *filename* (rather than a containing-directory name)
   containing a bracket is a distinct, separately-confirmed reproduction
   of the same root cause: it is classified as a glob because the
   bracket is present in the raw target text itself, so the attempt fails
   instead with a `ParseError: no files matched` rather than an
   `IndexError` (loader@v1#loader-002, loader@v1#loader-003,
   loader@v1#loader-007, classified `partial` — these are two distinct
   reproductions of one underlying gap, not confirmation of the same
   scenario twice).

### Self-exclusion and circular-include detection

The file that contains the `include` directive is always filtered out of
its own resolved target list first, before anything else happens — this
applies whether the match came from a glob or a single literal path
(loader@v1#loader-003).

**Confirmed limitation:** this produces a misleading error for a literal
self-include. If a file contains `include <its-own-filename>`, the
self-filter empties the resolved target list, and because the raw target
was not a glob pattern, the code reports `FileNotFoundError: include:
file not found: <path>` for a path that unquestionably exists on disk —
the true cause (the file excluding itself) is not what the error says.
Confirmed by direct execution; no test in the project's suite covers it
(loader@v1#loader-003).

Circular includes are detected via an ancestor-chain set of "currently in
progress" absolute paths: a genuine mutual cycle (file A includes file B,
which includes file A) is correctly caught and raises a `ParseError`
naming it as circular (loader@v1#loader-004).

**Confirmed limitation — "diamond" include graphs are not caught, and
produce silent duplication.** If a root file includes two sibling files
that each, independently, include the same third file, this is not a
cycle under the ancestor-chain design — the shared file is no longer "in
progress" by the time the second sibling branch reaches it — so it loads
successfully, but the shared file's content (transactions, declared
items, everything) is duplicated in the result, with no warning of any
kind. Confirmed by direct execution: a three-file diamond produced five
transactions in total (one shared transaction appearing twice), with no
error raised. Whether this should be allowed to succeed silently, or
should itself be flagged, was left as an open design question
(loader@v1#loader-004).

### Format prefixes

Format prefixes (e.g. `timedot:`, `csv:`) are **not supported** in ledgerkit v1.
Using them raises a `ParseError`. Remove the prefix and ensure the file has a
`.journal` or `.ledger` extension (loader@v1#loader-007).

### Restrictions

Only `.journal` and `.ledger` files may be included; other extensions
(including hledger's own `.j` alias) raise a `ParseError`
(loader@v1#loader-001, loader@v1#loader-007). Circular includes raise a
`ParseError` (loader@v1#loader-004). Active directives (such as `alias`)
at the point of the `include` apply to the included file's entries
(loader@v1#loader-005).

### Error line attribution

Because an included file's content is spliced into one flattened blob
before parsing, a parse error's raw line number is relative to that
flattened text, not to any original file. The loader maintains a mapping
with exactly one entry per *retained* line of the expanded output (an
`include` line itself contributes no entry, since it is replaced rather
than kept); when a `ParseError` is caught after parsing, it is re-raised
with the corrected originating file and local line number substituted in.
This remap applies only when the caught error's line number falls within
the range the map covers — outside that range, the original,
untranslated error propagates unchanged (loader@v1#loader-008).

---

## Alias Directive (Account Name Rewriting)

Rewrites account names at parse time. Useful for shortening entry data,
adapting old journals to a new chart of accounts, or combining accounts for
a report.

### Basic alias

```
alias checking = assets:bank:wells fargo:checking
```

Syntax: `alias OLD = NEW` (spaces around `=` are optional)

ledgerkit replaces any account name that **equals** `OLD`, or that **begins**
with `OLD:` (subaccounts). For example, the alias above rewrites:

- `checking` → `assets:bank:wells fargo:checking`
- `checking:savings` → `assets:bank:wells fargo:checking:savings`

Accounts that contain `OLD` elsewhere (e.g. `other:checking`) are **not** affected.

### Regex alias

```
alias /^(.+):bank:([^:]+)/ = \1:\2
; rewrites "assets:bank:wells fargo:checking" → "assets:wells fargo"
```

Syntax: `alias /REGEX/ = REPLACEMENT`

Any part of an account name matched by `REGEX` is replaced with `REPLACEMENT`.
The regex is case-insensitive. Backreferences `\1`, `\2`, etc. refer to
parenthesised capture groups in `REGEX`.

To match a literal `/`, escape it with a backslash: `\/`.

**Confirmed limitation:** a regex alias whose replacement text contains a
backreference with no matching group in the pattern (e.g. `alias
/(foo)/ = \2`) is accepted at declaration time and only fails later, when
actually applied to an account name — and it fails as an uncaught
`re.PatternError`, not a `ParseError`, bypassing even
`parse_string_lenient`'s normal error collection (journal-parsing@v1#journal-parsing-008).

### Multiple aliases and `end aliases`

Aliases accumulate from their definition point until `end aliases` or end of
file. They also apply to account names declared with the `account` directive.

```
alias a = alpha
alias b = beta

2024-01-01 Rent
    a  $1000          ; → alpha  $1000
    b                 ; → beta

end aliases           ; clears both rules

2024-01-02 Coffee
    a  $5             ; unchanged: alias no longer active
    b
```

**Application order:** when multiple aliases are active, the most recently
defined alias is applied first (LIFO). Each alias sees the result of the
aliases applied after it.

### Inline comments

Both `;` and `#` are recognised as inline comment introducers on alias lines
(requires two or more spaces before the comment character):

```
alias old = new  ; this comment is ignored
alias old = new  # this comment is also ignored
end aliases  ; clear all rules
```

### Scoping

Alias rules are local to the `parse_string()` call that processes them.
They do **not** propagate into files loaded via `include` directives —
this is a known deviation from hledger 1.52 behaviour (where aliases do
propagate into included files).

---

## Unsupported in v1

The following hledger features are not supported in ledgerkit v1:

- Timeclock, timedot, CSV, SSV, TSV, rules file formats — rejected with a
  `ParseError` before any not-found logic can apply (loader@v1#loader-007)
- Virtual postings (`(expenses:food)` or `[expenses:food]`)
- Periodic transaction rules (`~ monthly`) — the header line is
  recognised and a non-fatal `ParseWarning` is emitted, but the rule's
  body is skipped, not parsed as ordinary postings
  (journal-parsing@v1#journal-parsing-007)
- Auto-posting rules (`= expenses:food` at column 0) — same treatment as
  periodic rules: recognised, warned on, body skipped
  (journal-parsing@v1#journal-parsing-007)
- Balance-assignment elision syntax (`account  = AMOUNT`, with no
  separate amount written before the assertion) — see
  [Balance assertions, cost, and lot annotations](#balance-assertions-cost-and-lot-annotations)
  for the two different, confirmed ways an attempt to use it currently
  fails (journal-parsing@v1#journal-parsing-009)
- Multi-commodity ("mixed amount") postings — ledgerkit's data model gives
  a posting a single, optional amount with a single commodity; there is
  no concept analogous to hledger's "mixed amount" on one posting
  (tags@v1#tags-009)
- Smart dates (`today`, `last month`, etc.)

Previously, this section also listed secondary dates, balance assertions,
lot/cost annotations, and decimal-comma style as unsupported. All four are
in fact implemented — see
[Secondary dates](#secondary-dates),
[Balance assertions, cost, and lot annotations](#balance-assertions-cost-and-lot-annotations),
and the `decimal-mark` entry in [Directives](#directives) above.

---

## Compatibility confidence

A compatibility register tracks, per hledger feature, whether ledgerkit's
handling is considered compatible, an intentional divergence, or
explicitly unsupported, each at its own recorded verification tier (code
reading only, a same-session executable check, or an independently
dispatched comparison against a real `hledger` run). As of the last
survey, 6 of the register's 49 entries are classified `unsupported`
(compat-system@v1#compat-system-003). See
`dev-docs/hledger-compatibility.md` for the authoritative, currently
cross-linked picture — this document states the journal-format syntax
rules themselves; that one states which of them are currently verified
against real `hledger`, and at what confidence.

# Domain Rules

Tacit knowledge about the hledger journal format and ledgerkit's implementation that Claude cannot infer from code alone.

---

## `ledgerkit.query`'s `date:` range end is exclusive — `Query.date_to` is not

`ledgerkit.query.DateSpan.end` (the new Stage C query engine) is
EXCLUSIVE, matching hledger's actual `date:` term semantics: a single
date resolves to a one-day span `[d, d+1)`, and a written range's second
date is the exclusive upper bound exactly as written (`date:2024-01-01
-2024-01-31` does **not** include Jan 31). This is deliberately different
from the existing `ledgerkit.models.Query.date_to`, which is **inclusive**
(`reports.py`'s `_posting_matches`: `txn.date > query.date_to` excludes).

**Why it matters:** the two are not interchangeable, and it's easy to
port a date filter from one to the other and silently get an off-by-one-
day result. `Query` is not touched by Stage C Phase 1's introduction of
`ledgerkit.query` — it remains its own, separately-behaving thing until
Stage C explicitly turns it into a compatibility shim over the new AST.

**Implication:** never assume `Query.date_to` semantics apply to
`ledgerkit.query.DateSpan`, or vice versa, without checking which one a
piece of code is actually using.

---

## `ledgerkit.query`'s `not:` never joins a same-prefix OR group

Unnegated `acct:`/`desc:`/`status:` terms of the same type OR-combine
with each other (`acct:a acct:b` → match a **or** b); every other term —
including a negated term of *any* prefix, even one of those three — is
AND-combined individually. So `not:acct:a not:acct:b` means "match
neither a nor b" (AND of two negations), **not** "match not-a or not-b"
(which would be a much weaker, almost-always-true exclusion). This is
replicated directly from hledger's own `combineQueriesByType`/
`queryIsAcct` source (`queryIsAcct (Acct _) = True; queryIsAcct _ =
False` — explicitly `False` for a `Not`-wrapped term), not an independent
design choice — see `dev-docs/planning/core-redefinition/
17-query-semantics-brief.md` §6 and `LK-COMPAT-QUERY-BOOLCOMBINE-001`.

**Why it matters:** the "obvious" symmetric-looking alternative (pulling
negated terms into the OR bucket too) produces a genuinely different,
much weaker filter — a real correctness trap if this ever gets
"simplified" without re-reading the source rule first.

**Implication:** never refactor `ledgerkit/query/parser.py`'s
partition-then-combine step to treat negated terms the same as unnegated
ones for OR-grouping purposes.

---

## Double-space separator is mandatory between account name and amount

Postings use two or more spaces (or a tab) to separate the account name from the amount. A single space is not sufficient.

```
    expenses:food  £30.00   ← valid (2+ spaces)
    expenses:food £30.00    ← invalid (1 space — rejected by _TWO_SPACE_SEP)
```

**Why it matters:** Account names may legitimately contain spaces (e.g. `assets:joint account`). The double-space is the only unambiguous delimiter.

**Implication:** Never use a single space between account and amount in fixtures or test strings.

---

## At most one elided amount per transaction block

Exactly one posting per transaction may omit its amount. The parser infers the missing amount so the transaction balances to zero. Two or more elided amounts are ambiguous and raise `ParseError`.

**Implication:** Always provide explicit amounts in test fixtures except when specifically testing elision.

---

## `Posting.amount` is `Amount | None` by design

`None` is not an error state — it means the posting has an intentionally elided amount (to be inferred at check/report time). Code accessing `.quantity` or `.commodity` must guard with `assert amt is not None` or an equivalent.

---

## P directive records a price at a point in time — it is not a global rate

`P 2024-01-01 € $1.20` means "on 2024-01-01, one € was worth $1.20". It does NOT mean all €-denominated amounts throughout the journal are worth $1.20. Commodity valuation logic must use the *closest preceding date* for a given commodity pair.

**Scope:** P directives are file-local. Whether they propagate through `include` is TBD for Milestone 2.

---

## Balance rule: all postings in a transaction must sum to zero per commodity

A transaction is balanced when the algebraic sum of all posting amounts (per commodity) is zero. This is enforced by `checks.check_autobalanced`, not by the parser.

**Elided amount rule:** If one posting has no amount, its amount is inferred as the negation of the sum of all other postings. This only works when all other postings share a single commodity.

---

## `strict` mode requires ALL accounts AND commodities to be declared

Under `-s`/`--strict`, every account name appearing in a posting must have a matching `account` directive, and every commodity symbol must have a matching `commodity` directive. The check stops at the first failure and reports it with file path and line number.

**Implication:** Strict-mode fixtures (`tests/fixtures/strict_valid.journal`) must declare every account and commodity used.

---

## Account names use `:` as a hierarchy separator

`assets:bank:checking` has three segments. The `account_depth` stat counts colon-delimited segments. Leaf uniqueness (`uniqueleafnames` check) compares only the last segment.

---

## `decimal-mark` changes the parser mode for subsequent postings only

After `decimal-mark ,`, amounts must use European format (`1.234,56`). The change is not retroactive. Mixing formats within a file after the directive is a parse error.

**Default:** Period decimal (`1234.56`). Explicit `decimal-mark .` resets to default.

---

## Commodity symbols may be prefix or suffix

`£30.00` — prefix symbol (`£`), no space.
`30.00 EUR` — suffix symbol (`EUR`), one space separator.
Both are valid; the commodity value in `Amount.commodity` is just the symbol string without spaces.

---

## Comment indentation rule: column-0 vs. indented

There are two distinct comment forms inside a journal, and **indentation** is the discriminator:

| Form | First char | Indent? | Meaning |
|---|---|---|---|
| Top-level comment | `#` or `;` | No (column 0) | Always ignored; never captured into any data structure |
| Follow-on comment | `;` | Yes (leading whitespace) | Captured as `inline_comment` on the preceding transaction or posting |
| `#` inside a txn | `#` | Yes | Updates `source_span.end_line` only; text NOT captured |

**Key invariant:** A column-0 `;` or `#` is ALWAYS a top-level comment — even if it appears with no blank line between two transactions. It must never be captured as a follow-on comment for the previous transaction's last posting.

**Why it matters:** The parser uses `lstrip()` to strip whitespace before the startswith check, so it must also test `line[0:1].isspace()` before deciding to capture. Without this check a column-0 `;` between two adjacent transactions would incorrectly appear in the preceding posting's `inline_comment`.

**Inline `;` (same-line) is separate:** A `;` on the same line as a transaction header or posting is always captured regardless of indentation. This is handled in `_parse_txn_header` and `_parse_posting`, not in the standalone-comment branch.

---

## `include` directive: glob vs explicit path error handling

- **Explicit path** (no glob characters): raises `FileNotFoundError` if file does not exist.
- **Glob pattern** (`*`, `**`, `?`, `[range]`): silently produces no entries if no files match — this is NOT an error.

This matches the hledger 1.52 `include` spec.

---

## Sign may appear before OR after a prefix commodity symbol

Both `-$300` and `$-300` are valid in hledger. The sign may appear:
- Before the commodity symbol: `-$300` (conventional leading-minus form)
- Between the symbol and the quantity: `$-300` (sign after prefix symbol)

ledgerkit accepts both forms. The effective sign is the logical OR of the leading
minus and the mid-minus captured by the `_AMOUNT`/`_AMOUNT_COMMA` regex groups.

This means `$-300` parses as quantity `-300`, commodity `$` — identical to `-$300`.

---

## Inline comment tags (`name:value`): grammar edge cases

Tags are `name:value` pairs extracted from comment text (transaction,
posting, or `account`-directive inline comments — same-line or follow-on).
See `ledgerkit/tags.py`. Non-obvious rules, all confirmed against hledger
1.52.4's own grammar and doctests:

- **Space before the colon voids the whole tag, not just the name.**
  `foo bar :baz` extracts **no** tag at all — it does not fall back to an
  empty name. The tag name is "the last whitespace-delimited token
  immediately before `:`"; if that token is empty (because whitespace sits
  right before the colon), there is no candidate name and the `:` is not a
  tag delimiter at all.
- **Comma is a hard separator with no escaping.** A tag value runs from
  just after `:` to the next `,` or end of line. There is no way to put a
  literal comma inside a tag value in hledger's own grammar. A colon
  inside a value is fine (only the *first* unvoided `:` per candidate
  starts a tag).
- **Tags are `list[tuple[str, str]]`, never a dict.** The same tag name
  may legitimately repeat with different values in one comment (hledger's
  own manual example: `tag1:value 1, tag1:value 2`). Collapsing to a dict
  would silently drop all but the last occurrence.
- **`date:`/`date2:` tags only override at posting scope.** The same tag
  name in a transaction-level or `account`-directive comment is stored as
  an ordinary tag and has **no** date-override effect — only a *posting's
  own* comment tag sets `Posting.date_override`/`date2_override`. This was
  confirmed by direct reference to hledger's `check-tags.test` (test 6).
- **First-occurrence-wins for repeated date-override tag names.** If a
  posting's comment has two `date:` tags, the first is used to set
  `date_override`; the second is stored as a plain tag but does not
  overwrite it.
- **`account` directive follow-on `;` comment lines DO carry tags** —
  confirmed against `hledger.1:2980-2992`. This is a real capability, not
  a gap: `parser.py` must scan indented follow-on comment lines after an
  `account` directive the same way it does for transactions/postings.

**Why it matters:** every one of these was verified against either
hledger's literal source grammar or its own test suite, not inferred from
behavior — several are easy to get subtly wrong from casual reading (e.g.
Python's `str.split()` silently drops trailing empty tokens the way
Haskell's `Text.split isSpace` does not, which is exactly the
space-before-colon case above).

**Applies to:** `ledgerkit/tags.py`, `ledgerkit/parser.py`, `ledgerkit/models.py`

---

## `depth:` is a report-display option, never a selection predicate — except `stats`

Every real hledger command that consumes a `Query` (`balance`, `register`,
`print`, `accounts`, `aregister`) strips `depth:`/`depth:REGEX=N` out of
the query used to select/include postings *before* selection happens,
and reapplies it purely as a display-name transform (truncation +
aggregation into the depth-N ancestor — never exclusion). This holds even
though hledger's own `Query` AST has a real, unit-tested boolean
`Depth`/`DepthAcct` predicate (`accountNameLevel a <= d`) — that function
is real, it's just never invoked by any actual report command for
selection purposes. `depth:0` clips every account to the literal string
`"..."`, never to empty/nothing.

**Custom depth precedence** (`depth:REGEX=N`, since hledger 1.41): among
multiple regex-depth rules matching an account (or any of its strict
ancestors), the one that starts matching at the *greatest* specificity
wins — counterintuitively, a regex that matches only the account's own
leaf name (no strict ancestor at all) is **more** specific than one
matching a shallow ancestor, not less. Ties (including two rules that
happen to match at the same ancestor depth) go to the **later-declared**
rule. A regex matching wins outright over a `flat` general depth,
regardless of specificity — `flat` is purely the fallback when no regex
matches at all.

**Multiple `depth:` terms combine differently depending on where they
come from**: multiple terms *within one query string* (e.g. `-q "depth:3
depth:1"`) combine flat depths via **minimum** (the more restrictive
value wins, order-independent — hledger's own `DepthSpec` `Semigroup`
instance) and simply accumulate `by_pattern` entries from both. This is
**not** the same as multiple `--depth` CLI flags (a separate mechanism,
"last wins," order-dependent) — Ledgerkit has no standalone `--depth`
flag yet, only the `-q` string form, so only the minimum-based rule
applies today.

**`stats` is a genuine, source-confirmed exception**: unlike every other
command, `stats`'s `Accounts: N (depth D)` fields come from hledger's own
`Ledger.hs:ledgerFromJournal`, whose doc-comment states plainly the
ledger's journal (which `stats` reads its account list from) IS depth-
limited by exclusion — the account tree (used by other commands) is not.
So `stats -q "depth:N"` genuinely drops accounts deeper than N from its
count, rather than clipping/aggregating them — confirmed live on two
independent scenarios (a lone custom-regex depth, and a mixed
custom+general combination), both reproducing hledger's exact counts.

**Why it matters:** Stage C Phase 1 read the `Depth` constructor's own
`matchesAccount` function and its unit test coverage, and concluded
`depth:` was a pure exclusion predicate — a real function doing real
work, correctly read in isolation. The mistake was not tracing whether
any actual command invokes it that way; none do. The general lesson: for
any hledger source-reading exercise, "does a function with this name
exist and do what I'd expect" is not sufficient evidence that it
describes user-observable command behaviour — trace the function's real
callers.

**Applies to:** `ledgerkit/query/depth.py`, `ledgerkit/query/parser.py`,
`ledgerkit/reports.py`

---

## `tag:` matches a four-source *effective* tag union, computed once per posting/transaction — and same-named tags from different sources are NEVER shadowed

hledger's `tag:NAME[=REGEX]` does not read `Posting.tags`/
`Transaction.tags` alone — it reads the union of **four** sources per
posting: the posting's own literal comment tags, its transaction's own
tags, its account's declared-and-**inherited** tags (walking every
ancestor account, not just an exact name match), and its main amount's
commodity's declared tags (the "commodity tags" feature — a `commodity
SYMBOL ; tag:value` directive's tags propagate to every posting whose
main amount uses that commodity). Ledgerkit computes this on demand via
`ledgerkit.tags._effective_tags(journal, txn, posting)` — a private, pure
function; `Posting.tags`/`Transaction.tags` themselves still hold **only**
each entity's own literal comment tags, unchanged from Stage C Phase 4's
contract (hledger's own mechanism instead mutates `ptags`/`ttags` once at
journal-read time — Ledgerkit deliberately does not mirror that literal
mechanism, to avoid silently breaking Phase 4's already-documented field
semantics).

**Four inheritance/propagation rules, all independently confirmed live
against the pinned hledger binary:**
- **Rule A** (account ← parent account's declared tags): a query for a
  tag declared on `assets:bank` also matches the *account name*
  `assets:bank:savings`, even with no `account` directive of its own.
- **Rule B** (posting ← its own account's inherited tags): every posting
  to `assets:bank` or any descendant matches, even a posting with **no
  inline comment of its own at all**.
- **Rule C** (posting ← its transaction's own tags): a tag declared only
  on the transaction header line is matched by a query against a posting
  that has no comment of its own.
- **Rule D** (transaction ← union of all its postings' effective tags,
  **plus** its own tags directly): a transaction matches if *any*
  posting's effective tag set matches, **or** if the transaction's own
  tags directly match — both halves are real, independent inputs (the
  direct half is not merely implied by rule C's propagation onto
  postings, even though in practice it usually is also reachable that
  way too).

**Combination is always AND, never OR**: unlike `acct:`/`desc:`/
`status:` (whose same-prefix unnegated terms OR-combine), multiple
`tag:` terms in one query string always AND together — `tag:a tag:b`
requires both tags present, not either. This falls out for free from
`tag:` not being one of the three OR-eligible prefixes in
`ledgerkit/query/parser.py`'s bucket logic — no special-casing needed,
but easy to assume otherwise by analogy with `acct:`/`desc:`.

**The single most counter-intuitive rule — no shadowing between sources,
despite the manual's own wording implying otherwise**: hledger's manual
states "posting tags override account tags override commodity tags,"
which reads like exclusion (only the highest-priority value visible when
names collide). **This is not what happens for `tag:` query-matching.**
Executable testing against the pinned binary shows every differently-
valued, same-named tag from every applicable source remains
**simultaneously, independently matchable** — a query for the
account-inherited value still matches a posting whose own comment
declares a *different* value for the same tag name, and vice versa.
Traced to source: `Tag = (TagName, TagValue)` is a plain tuple with
structural equality, and hledger's own `postingAddTags` deduplicates via
`Data.List.union` on the **full tuple** (name AND value) — a same-name,
different-value pair is never considered a duplicate and is never
dropped. The manual's "override" language describes something narrower
than exclusion (plausibly which value a hypothetical single-value lookup
would prefer) — not investigated further, since it doesn't change the
matching contract. **Ledgerkit's `_effective_tags` is therefore a plain
concatenation of all four sources with no shadowing/exclusion logic
whatsoever** — a naive "highest-priority wins" or dedup-by-name
implementation would be a correctness bug, not a simplification.

**`accounts -q "tag:X"` (plain, non-`--declared` mode) is a genuine,
narrower exception**: it shows only **transaction-level** and
**account-inherited** tags — a posting's own comment tags and
commodity-propagated tags are **not visible** to it, even though every
other command (`balance`/`register`/`print`/`stats`) sees all four
sources. Source-confirmed: `journalPostingsKeepAccountTagsOnly` replaces
a posting's own `ptags` with only its account-inherited tags before
`accounts` builds its list, but query matching separately reads
`postingAllTags = ptags ++ ttags`, which unconditionally re-adds the
transaction's own tags regardless of what `keepaccounttags` did — so
transaction-level tags remain visible even though posting-own tags do
not. Ledgerkit replicates this via a private, `accounts`-only
computation (`ledgerkit.tags._accounts_effective_tags`), not by changing
`matches_posting`'s own default behaviour.

**A `Tag` node needs `Journal` access to evaluate** (every other
`QueryNode` type only ever needs the `Transaction`/`Posting` already
passed in) — `matches_transaction`/`matches_posting` gained an optional
`journal: Journal | None = None` parameter for this. Evaluating a `Tag`
node with `journal=None` raises `ValueError` — never silently narrows to
own-tags-only; a caller that needs `tag:` support but forgets to pass
`journal` gets a loud, immediate failure, not a quietly wrong answer.

**Why it matters:** every rule above was independently re-verified this
phase against the pinned hledger 1.52.4 binary on purpose-built fixtures
(`23-tag-query-matching-design.md` §2), not inferred from the manual's
prose alone — the manual's own wording on precedence is, on its own,
actively misleading for the shadowing question. A future change to
`tags.py`/`query/eval.py` that "simplifies" by deduplicating effective
tags by name, or that adds a fifth account-tag-only or
posting-tag-only shortcut without checking this rule first, would
silently reintroduce a real correctness regression.

**Applies to:** `ledgerkit/tags.py`, `ledgerkit/parser.py`,
`ledgerkit/models.py`, `ledgerkit/query/ast.py`, `ledgerkit/query/eval.py`,
`ledgerkit/query/parser.py`, `ledgerkit/reports.py`

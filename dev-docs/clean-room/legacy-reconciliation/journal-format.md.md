<!-- producer: docs-maintainer (legacy reconciliation mode) | document: docs/journal-format.md
     | dispatch: plan29-phase5-journalformat-legacy-reconciliation
     | inputs: real docs/journal-format.md (pre-reconciliation),
       dev-docs/clean-room/drafts/journal-format.md.clean-room-draft (Phase 4),
       Phase 3 evidence for journal-parsing, commodity-styling, tags, loader,
       compat-system; knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md
     | scheme: Plan 29 §6.1 five-way (supported / stale_or_contradicted /
       rationale_requiring_verification / useful_example / obsolete) -->

# Legacy reconciliation: docs/journal-format.md

This classifies every material claim in the real, pre-reconciliation
`docs/journal-format.md` against the Phase 4 clean-room draft
(`dev-docs/clean-room/drafts/journal-format.md.clean-room-draft`) and the
underlying Phase 3 evidence (assertions + implementation-reconstruction +
implementation-comparison) for the five topics that draft is built from:
`journal-parsing`, `commodity-styling`, `tags`, `loader`, `compat-system`.

Per this role's governing instructions, agreement between the legacy doc
and the clean-room draft is **not** treated as evidence of truth on its
own — every `supported` row below is traced to a specific Phase 3
assertion whose own cited evidence (a file:line, a test, a direct-execution
repro) checked the claim directly. Where no such assertion exists within
this draft's five topics, that is stated explicitly rather than silently
assumed.

## Summary counts

| Classification | Count |
|---|---|
| `supported` (confirmed accurate, traced to a Phase 3 assertion) | 19 |
| `stale_or_contradicted` (now wrong; not restored) | 4 |
| `rationale_requiring_verification` | 0 (none of the legacy doc's claims were framed as a *reason* needing separate verification; see note below) |
| `useful_example` (kept/re-grounded, not authoritative on its own) | 3 |
| `obsolete` (no longer true/present; recorded, not restored) | 0 |
| Out-of-scope for this draft's five topics (retained unchanged, no contradicting evidence found, no five-way citation available) | 2 |

No legacy claim in this document took the shape of a *rationale* ("X is
true because Y") that itself needed checking against
`knowledge/{DECISIONS,EDGE_CASES,ANTIPATTERNS,DOMAIN_RULES}.md` — the
legacy doc states behaviour directly, not reasoning chains. `knowledge/
EDGE_CASES.md`/`DOMAIN_RULES.md` were consulted throughout as corroborating
(not authoritative) background; one direct conflict was found between
`knowledge/EDGE_CASES.md` EC-006 and Phase 3's `loader-007` — see
"Notable finding" below.

## `supported` (traced to a specific Phase 3 assertion)

| Legacy claim | Assertion | Evidence basis |
|---|---|---|
| Header fields: date, status flag, code, description, inline comment | journal-parsing@v1#journal-parsing-001 | `_TXN_HEADER` regex, file:line, tests |
| Date formats (`YYYY-MM-DD`/`/`/`.`, year-omitted `MM-DD`/`M/D`, leading zeros optional) | journal-parsing@v1#journal-parsing-002 | `_SIMPLE_DATE` regex, default-year substitution, tests |
| Two-or-more-space account/amount split; single space does not split | journal-parsing@v1#journal-parsing-003 | `_parse_posting`, file:line, tests |
| Elided amount: at most one per transaction, recorded as `None` | journal-parsing@v1#journal-parsing-005 | `resolve_elision`, file:line, tests, direct execution |
| Amount forms: prefix/suffix symbol, leading minus, thousands comma, integer | journal-parsing@v1#journal-parsing-004 | `_AMOUNT`/`_AMOUNT_COMMA` regexes, tests |
| Account names: single space allowed inside a name before the two-space separator | journal-parsing@v1#journal-parsing-003 | same as above — covers only the space-preservation claim, not case-sensitivity/hierarchy (see "Out of scope" below) |
| Standalone column-0 `#`/`;` comments, silently ignored anywhere in the file | journal-parsing@v1#journal-parsing-006 | comment taxonomy, tests |
| Same-line inline comment via `;`; `#` does not introduce one | journal-parsing@v1#journal-parsing-006 | comment taxonomy, tests |
| Follow-on indented `;` comment lines append to preceding posting/transaction `inline_comment`; indented `#` extends span only | journal-parsing@v1#journal-parsing-006 | comment taxonomy, tests |
| Column-0 `;`/`#` is always top-level even with no blank line before it | journal-parsing@v1#journal-parsing-006 | comment taxonomy, tests; corroborated by `knowledge/EDGE_CASES.md` EC-014 |
| Block comments (`comment`/`end comment`), trailing text ignored, unclosed block consumes rest of file | journal-parsing@v1#journal-parsing-007 | directive inventory, tests |
| Tag syntax (`name:value`, comma-separated, voided-by-space-before-colon, no comma escaping, repeated names kept as list) | tags@v1#tags-005, tags@v1#tags-006, tags@v1#tags-007 | scan/split logic, tests |
| `date:`/`date2:` posting-comment tags set a real per-posting override; first occurrence wins; transaction-level tag of the same name has no override effect | journal-parsing@v1#journal-parsing-010, tags@v1#tags-008 | file:line, tests |
| `-q "tag:..."` matches a four-source effective-tag union (posting, transaction, account-inherited, commodity-declared), with no shadowing/dedup even across exact-duplicate pairs | tags@v1#tags-001, tags@v1#tags-002 | `_effective_tags`, docstring + direct invocation, tests |
| `accounts -q "tag:X"` is a narrower, two-source-only exception | tags@v1#tags-003 | code's own documented purpose (caller not independently confirmed — carried through as a caveat) |
| Account tag inheritance walks every ancestor prefix, not just the exact account; a sibling does not inherit from a sibling | tags@v1#tags-004 | inheritance walk, tests |
| `P` directive syntax and storage in `journal.prices` | journal-parsing@v1#journal-parsing-007 | directive inventory |
| `include` path resolution precedence (tilde, absolute, relative-to-containing-file) | loader@v1#loader-001, loader@v1#loader-002 | file:line, tests |
| Glob patterns (`*`, `**`, `?`, `[range]`) supported, sorted deterministically; containing file always excluded from its own glob results | loader@v1#loader-002, loader@v1#loader-003 | file:line, tests |
| A glob pattern matching no files raises `ParseError` ("no files matched") | loader@v1#loader-007 | **directly test-confirmed** (`test_glob_no_matches_raises`) — see "Notable finding" below; this is the one place the legacy doc's claim is *more* correct than the stale `knowledge/EDGE_CASES.md` EC-006 entry |
| Format prefixes (`timedot:`, `csv:`) rejected with `ParseError`; only `.journal`/`.ledger` extensions accepted; circular includes raise `ParseError`; active directives (e.g. `alias`) apply to included files | loader@v1#loader-001, loader@v1#loader-004, loader@v1#loader-005, loader@v1#loader-007 | file:line, tests, direct execution |
| Alias directive (basic + regex forms, LIFO application order, `end aliases` scoping, file-scoped — not propagated into `include`d files) | journal-parsing@v1#journal-parsing-007 (directive inventory); alias file-scoping corroborated by `knowledge/DECISIONS.md` "alias directive is file-scoped at parse time" and `knowledge/ANTIPATTERNS.md` "Accumulating aliases across included files" | directive inventory; no dedicated Phase 3 alias-semantics assertion exists among the five topics' sets, so this row rests on the directive-inventory assertion plus corroborating (not independently re-verified this round) `knowledge/` entries — flagged accordingly in the merged doc |

## `stale_or_contradicted` (now wrong; fixed, not merely annotated)

1. **"Balance assertions (`assets:checking = £500`)" listed as Unsupported in v1.**
   Contradicted by journal-parsing@v1#journal-parsing-009: a posting amount
   token may carry a balance assertion marker (`=`, `==`, `=*`, `==*`),
   parsed and stored on `Posting.balance_assertion`, test-confirmed. Also
   corroborated by `knowledge/DECISIONS.md` ("`assertions` added to
   `BASIC_CHECK_NAMES`" — assertions are checked automatically). **Fixed**:
   removed from Unsupported; documented under Amounts/Balance assertions,
   with the genuinely-unsupported *sub-feature* (balance-assignment
   elision, `account = AMOUNT` with no separate amount) now stated
   precisely instead of the whole feature being overstated as absent.

2. **"Lot prices (`10 AAPL @ $150`)" listed as Unsupported in v1.**
   Contradicted by journal-parsing@v1#journal-parsing-009: cost
   annotations (`@ PRICE` / `@@ TOTAL`) and lot annotations (`{AMOUNT}`,
   `{{AMOUNT}}`, `[DATE]`, `(LABEL)`) are parsed, stripped in a documented
   fixed order, and test-confirmed, including composed together on one
   posting. **Fixed**: removed from Unsupported; documented under Amounts.

3. **"Secondary dates (`2024-01-15=2024-01-20`)" listed as Unsupported in v1.**
   Contradicted by journal-parsing@v1#journal-parsing-001: the transaction
   header regex accepts an optional secondary date introduced by `=`
   (`Transaction.date2`, confirmed present in `ledgerkit/models.py`), and
   by tags@v1#tags-008's description of the secondary-date-override
   precedence chain, which presupposes `Transaction.date2` is real and
   populated. **Fixed**: removed from Unsupported; added a "Secondary
   dates" subsection under Transaction Block / Header fields.

4. **"Decimal comma style (`1.234,56`)" listed as Unsupported in v1.**
   Contradicted by journal-parsing@v1#journal-parsing-004 (the
   `decimal-mark` directive reverses comma/period roles for amounts parsed
   from that point forward) and corroborated by `knowledge/DOMAIN_RULES.md`
   ("`decimal-mark` changes the parser mode for subsequent postings only")
   and `knowledge/EDGE_CASES.md` EC-008/EC-010/EC-013. The legacy doc never
   documented the `decimal-mark` directive at all, so this wasn't merely an
   outdated caveat — the feature enabling exactly this was undocumented
   entirely. **Fixed**: removed from Unsupported; added a `decimal-mark`
   entry to the new Directives section, with the EC-008 caveat (mixing
   formats after the directive switches is a `ParseError`) folded in.

Additionally, the entire **Directives** area of the legacy doc was
incomplete to the point of being misleading by omission: `account`,
`commodity`, `payee`, `tag`, `decimal-mark`, `Y`, `D`, and `apply
account`/`end apply account` were never documented at all, even though
`tag`-bearing `account`/`commodity` directives are load-bearing for the
Tags section the legacy doc *does* document in detail (an `account`
directive's tag only makes sense to a reader if they know the directive
exists). This is treated as a `supported`-but-previously-missing addition
(journal-parsing@v1#journal-parsing-007) rather than a stale claim, since
the legacy doc made no false claim about these directives — it simply
never mentioned them.

## `useful_example` (re-grounded, not authoritative on its own)

1. The worked transaction-block example (`2024-01-15 * (INV-42) Groceries
   ; weekly shop` / two postings) — kept, re-grounded against
   journal-parsing@v1#journal-parsing-001's confirmed header-regex
   behaviour (status flag + code + description + inline comment all
   captured as shown).
2. The `alias /^(.+):bank:([^:]+)/ = \1:\2` regex-alias example — kept;
   re-grounded against the directive-inventory assertion
   (journal-parsing@v1#journal-parsing-007) confirming `alias` with
   backreferences is a real, implemented directive, though no Phase 3
   assertion among these five topics independently re-verified this
   *specific* regex's output. Flagged in the merged doc as resting on the
   directive's existence being confirmed, not on this exact example being
   test-replayed this round.
3. The glob-pattern examples (`*.journal`, `**.journal`, `202?.journal`) —
   kept; re-grounded against loader@v1#loader-002's confirmed glob-pattern
   support (including `**` recursive matching) and loader@v1#loader-007's
   test-confirmed no-match behaviour.

## Out of scope for this draft's five topics (retained unchanged)

1. **Account name case-sensitivity** (`Assets:Bank` ≠ `assets:bank`) and
   **colon-separated hierarchy** — no assertion among `journal-parsing`,
   `commodity-styling`, `tags`, `loader`, or `compat-system` directly
   checks account-name case-sensitivity or the hierarchy-separator
   semantics in isolation (the nearest adjacent evidence,
   tags@v1#tags-004, confirms colon-delimited ancestor-prefix walking for
   *tag inheritance* specifically, not general case-sensitivity). Retained
   in the merged doc unchanged, since nothing in this round's evidence
   contradicts it, but it is **not** marked `supported` under this
   round's citation discipline. Flagged for a future `checks`-topic-scoped
   or dedicated verification pass (the `checks` topic's own
   `checks-003.md` assertion mentions case-sensitivity but in a different
   context — `uniqueleafnames` — and was out of scope for this five-topic
   dispatch).
2. **`comment`/`end comment` trailing-text and mid-file placement details**
   beyond what journal-parsing@v1#journal-parsing-007 already covers —
   retained as previously stated.

## Notable finding: a legacy-vs-knowledge-base conflict, not a legacy-doc defect

`knowledge/EDGE_CASES.md` EC-006 states: "`include *.journal` in a
directory with no `.journal` files... Silently produces no entries (no
error)." This directly contradicts both the legacy `docs/journal-format.md`
("A glob pattern that matches no files raises a `ParseError`") and the
Phase 3 `loader-007` assertion, which cites a passing, named test
(`test_glob_no_matches_raises`, asserting `ParseError` with "no files
matched") as direct evidence of the `ParseError` behaviour. The legacy
doc and the current code agree; `knowledge/EDGE_CASES.md` EC-006 appears
to predate a later behaviour change and was not updated. **This is not
something this role is authorised to fix** (`knowledge/` is out of this
role's write boundary) — flagged here for the lead/`roadmap-context-curator`
to correct EC-006 separately.

## Confirmed findings carried forward from the clean-room draft (not dropped)

Per explicit instruction, the following confirmed, unflattering
current-behaviour facts from the Phase 4 draft are preserved in the
merged `docs/journal-format.md`, each with its citation intact:

- `parse_string_lenient`'s "never raises" contract is **not** actually
  unconditional: a malformed `commodity` directive raises uncaught
  (journal-parsing@v1#journal-parsing-008), and an `alias` directive with
  an invalid backreference raises an uncaught `re.PatternError` only when
  later *applied*, not at declaration time (journal-parsing@v1#journal-parsing-008,
  classified `partial` — a second, independently-found exception not in
  the assertion's own original text).
- A directive (`account`/`commodity`/`payee`/`tag`) appearing between two
  posting lines of a still-open transaction silently drops the rest of
  that transaction's postings, with no error or warning at all
  (journal-parsing@v1#journal-parsing-007, classified `partial`).
- Balance-assignment elision (`account  = AMOUNT`) fails in two different
  ways depending on commodity placement and decimal mode: a clean (if
  unhelpfully worded) `ParseError` for a prefix-commodity amount, but
  **silent corruption** — a posting with `commodity` set to the literal
  string `"="` and no assertion — for a suffix-commodity amount under
  comma-decimal mode (journal-parsing@v1#journal-parsing-009, classified
  `partial`).
- Three distinct loader glob-escaping gaps: (1) a containing-directory
  name with a bracket character silently misclassifies a plain include
  target as a glob, yielding an uncaught `IndexError`
  (loader@v1#loader-002/003/007, classified `partial`); (2) a literal
  filename with a bracket character is classified as a glob and fails
  with a `ParseError` instead (a different reproduction of the same root
  cause, independently found during reconstruction); (3) a literal
  self-include produces a misleading `FileNotFoundError` for a file that
  demonstrably exists (loader@v1#loader-003). None of these three is an
  invented or speculative concern — all three were confirmed by direct
  execution during Phase 3 review.
- Diamond include graphs (two siblings independently including the same
  third file) are not caught as circular and silently duplicate content,
  confirmed by direct execution (loader@v1#loader-004).
- The commodity-style inference "else" branch (symbol matches neither
  start nor end of the sample) can silently produce a nonsensical
  precision value, confirmed by direct execution, untested in the
  project's suite (commodity-styling@v1#commodity-styling-001).
- One report-formatting code path applies a single, arbitrary commodity's
  style to every row of a multi-commodity report section — a disclosed,
  self-acknowledged limitation in the code's own comments, not merely an
  unnoticed gap (commodity-styling@v1#commodity-styling-008).

All of the above are now in the merged `docs/journal-format.md`, each with
its originating citation preserved exactly as the draft stated it.

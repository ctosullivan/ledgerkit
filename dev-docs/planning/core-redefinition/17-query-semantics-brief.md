# 17. hledger query-term semantics brief (Stage C Phase 1)

Produced by `hledger-researcher`, scoped to Stage C's initial target term
set per `07-query-regex.md` §7.1's phasing note: `acct:`/bare pattern,
`desc:`, `date:` (simple dates only), `depth:N`, `status:`, `not:` and
implicit-AND/same-prefix-OR combination. `tag:`, `cur:`, and hledger's
smart/period date expressions are explicitly out of scope for this brief
(Stage C follow-on work).

**Pinned baseline used:** local clone at `/home/cormac/projects/hledger`,
tag `1.52.4`, commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`
(2026-09-10) — matches `09-compatibility-system.md` §9.1's stated target
exactly.

**Hard limitation, stated explicitly:** no pinned `hledger` *binary*
exists in this environment, only the source clone. Everything below is
manual/source/test-suite-derived (`status: proposed` only). Every
classification below is a proposal for `compat-differential-tester` to
executable-verify against a real `1.52.4` binary — none of this is
executable-confirmed yet.

## 0. Scope note on regex applicability

Of the six items in scope, only **`acct:`/bare-pattern** and **`desc:`**
actually take a regex argument. `date:` takes a period-expression grammar
(no regex), `depth:N` (the in-scope bare form) takes an integer, `status:`
takes a fixed 3-way enum, and `not:` is a combinator. So §5 below (regex-
dialect boundary) is really about items 1 and 2, plus the general
query-string quoting/tokenization all six sit inside.

---

## 1. `acct:REGEX` and bare pattern

**Target behaviour:** case-insensitive, infix (substring/unanchored) regex
match against a posting's account name (`paccount`, and also against
`poriginal`'s account name if the posting was transformed, e.g. by an
alias). Bare pattern (no prefix) is defaulted to `acct:`.

- Construction: `parseQueryTerm` — `T.stripPrefix "acct:" -> Just s =
  (,[]) . Acct <$> toRegexCI s` (`hledger-lib/Hledger/Query.hs:304`);
  default-prefix fallback at `Query.hs:326-327` (`parseQueryTerm d s =
  parseQueryTerm d $ defaultprefix<>":"<>s` where `defaultprefix = "acct"`,
  `Query.hs:278`).
- Matching: `matchesAccount (Acct r) a = regexMatchText r a`
  (`Query.hs:875`); at the posting level, matches **either** the current
  or the pre-transformation account name: `matchesPosting (Acct r) p =
  matches p || maybe False matches (poriginal p) where matches =
  regexMatchText r . paccount` (`Query.hs:912`) — this "match
  original-or-transformed" detail is not mentioned in the manual at all;
  it only shows up in source, and matters if Ledgerkit's evaluator runs
  after alias/pivot transforms are applied.
- At the **transaction** level (`print` etc.), `Acct` matches if **any**
  posting matches: `matchesTransaction q@(Acct _) t = any (q
  \`matchesPosting\`) $ tpostings t` (`Query.hs:959`). Manual confirms
  this generally: "Transaction-oriented commands... try to match
  transactions (including the transaction's postings)" (`hledger.1:7224-
  7226`).
- Case-insensitivity is not optional/configurable from the query string —
  `toRegexCI` is used unconditionally for `Acct` (and `Desc`); there is no
  `acct:`-level way to request case-sensitive matching. Confirmed both by
  manual (`hledger.1:738`, "they are case insensitive") and source
  (`Hledger/Query.hs:304`, `Hledger/Utils/Regex.hs:139-140`).
- Infix/unanchored: `regexMatchText r = matchTest r . T.unpack`
  (`Hledger/Utils/Regex.hs:174-175`) — `matchTest` is an unanchored
  substring test, no implicit `^`/`$`. Manual confirms (`hledger.1:740-
  741`, point 2: "infix matching... do not need to match the entire
  thing"). Contrast with `accountNameToAccountRegex`, which *does* wrap in
  `^...(:|$)` for the `inacct:` display option
  (`Hledger/Data/AccountName.hs:401-402`) — that anchoring is specific to
  `inacct:`/`in:`, not to `acct:` query terms, and is out of this brief's
  scope anyway.

**Edge cases that matter:**
- Query-string quoting: patterns containing spaces must be single- or
  double-quoted (`words''`, `Query.hs:229-250`; manual `hledger.1:667,
  7119-7127`). Doctests: `words'' [] "'a b'" == ["a b"]` (`Query.hs:1084`).
- Bare-pattern repetition: `parseQuery nulldate "expenses:dining out"` →
  `Or [Acct "expenses:dining", Acct "out"]` (doctest, `Query.hs:196`) —
  two bare tokens are two separate OR'd acct: terms, not one two-word
  acct: pattern (that requires quoting: `"expenses:dining out"` as a
  single quoted arg).

**Proposed classification:** `compatible` (`relationship: equivalent`),
*conditional* on Ledgerkit restricting itself to the `HledgerRegex`-
compatible subset defined in §5 and using `re.search` (never
`re.match`/`fullmatch`) with `re.IGNORECASE` unconditionally.
`status: proposed`.

## 2. `desc:REGEX`

**Target behaviour:** same case-insensitive infix regex construction
(`toRegexCI`) against `tdescription` — a transaction-level field only, no
posting-level equivalent.

- Construction: `Query.hs:301`. Matching: `matchesTransaction (Desc r) t =
  regexMatchText r $ tdescription t` (`Query.hs:958`); the posting-level
  desc match pulls the field from the posting's parent transaction:
  `matchesPosting (Desc r) p = maybe False (regexMatchText r .
  tdescription) $ ptransaction p` (`Query.hs:911`) — i.e. a posting
  "inherits" its transaction's description for query purposes, exactly as
  the manual states: "Postings inherit their transaction's attributes for
  querying purposes" (`hledger.1:7232-7234`).
- `matchesDescription` (a narrower helper used by some report code)
  explicitly filters to only `Desc` terms among ANDed/ORed subqueries and
  ignores everything else (`Query.hs:988-998`) — a report-specific
  narrowing, not the general evaluator; note for the lead in case
  `reports.py` needs an equivalent narrow accessor rather than full
  `matchesTransaction`.

**Proposed classification:** `compatible` (`relationship: equivalent`),
same conditionality as `acct:`. `status: proposed`.

## 3. `date:PERIODEXPR` — simple dates only

**Important correction to the plan's framing:** real hledger's `date:`
term **always** parses through the full period-expression/smart-date
grammar (`parsePeriodExpr`, `Hledger/Data/Dates.hs:396-420` →
`periodexprp`/`periodexprdatespanp`, `Dates.hs:1061-1195`) — there is no
separate "simple date mode" inside hledger itself. `date:2016`,
`date:thismonth`, `date:2/1-2/15`, `date:2021-07-27..nextquarter` are all
the *same* grammar (manual examples, `hledger.1:7307-7308`). So
Ledgerkit's "simple dates only" scope is **Ledgerkit's own intentional
subset of hledger's `date:` grammar**, not something hledger itself
distinguishes — recorded as such rather than implied to be a natural
hledger category.

For the subset Ledgerkit targets (a single full ISO/simple date, or two
full simple dates joined by `-`, `..`, or `to`):
- A single full date (`SmartCompleteDate day`, produced by
  `ymd`/`yyyymmdd` when day is given, `Dates.hs:941-965`) resolves to a
  **one-day span** `[day, day+1)`: `span' (SmartCompleteDate day) =
  (Exact day, Exact $ nextday day)` (`Dates.hs:429`). So
  `date:2024-01-15` matches **only that single day**, not "from that day
  onward" — a real footgun if Ledgerkit's existing `Query.date_from`/
  `date_to` model assumes an open-ended "from" semantics for a lone date
  term.
- A range `date:D1-D2` / `date:D1..D2` / `date:D1 to D2` resolves via
  `doubledatespanp` (`Dates.hs:1142-1148`) to `DateSpan (Exact D1) (Exact
  D2)` — **the end date is exclusive**. Doctest: `doubledatespanp ...
  "20180101-201804"` → `DateSpan 2018Q1` (i.e., Jan 1 through Mar 31
  inclusive, since `201804` here is itself smart-resolved to `2018-04-01`
  and treated as the exclusive upper bound) (`Dates.hs:1132-1141`).
  Concretely: `date:2024-01-01-2024-01-31` does **NOT** include Jan 31 —
  you need `date:2024-01-01-2024-02-01` (or a single-date-only query) to
  include the whole of January. This exclusive-end-date behaviour is the
  single most important edge case to get right, and it applies
  identically to a "simple dates only" subset implementation.
- Open-ended forms exist (`fromdatespanp`/`todatespanp`, `Dates.hs:1158-
  1178`, e.g. `2025-01-01..`) — treated as in-scope (single full date plus
  a bare range operator, no smart-date keyword), flagged for the lead's
  explicit confirmation since the task's scope note doesn't say either
  way.
- Everything else the grammar accepts (bare years, partial `YYYY-MM`,
  quarters `2009Q2`, keywords `today`/`thismonth`/`nextquarter`/relative
  "N days ago", weekday/month names) is out of scope — consistent with
  `hledger-compatibility.md`'s existing "Smart dates... not currently
  planned for v1" line.
- `date:` restricts primary dates; `date2:` (secondary dates) is
  explicitly out of scope per the task.
- Manual: `hledger.1:7295-7314`. The manual also notes (`7310-7314`) that
  `PERIODEXPR` may embed a reporting interval since 1.52 — unrelated to
  simple dates, out of scope; flagged only so it isn't accidentally
  implemented as part of "simple date" support.

**Proposed classification:** two-part.
- For the in-scope subset (single full simple date, or two full simple
  dates joined by `-`/`..`/`to`, open or closed): `compatible`
  (`relationship: equivalent`) — because for exactly those inputs,
  hledger's own general grammar produces the identical span Ledgerkit
  would compute directly.
- For everything else in hledger's `date:` grammar (smart/relative/
  partial dates, quarters, weekdays): `unsupported` (`relationship:
  subset`) — already the implicit position of `hledger-compatibility.md`'s
  "Undecided/Future" list; this just makes it a formal register entry.

Both `status: proposed`.

## 4. `depth:N`

**Target behaviour (predicate form, the in-scope form):** `Depth d`
matches an account when `accountNameLevel(a) <= d`, where
`accountNameLevel` is exactly colon-segment count: `accountNameLevel "" =
0; accountNameLevel a = T.length (T.filter (==acctsepchar) a) + 1`
(`Hledger/Data/AccountName.hs:165-167`) — i.e. `count(':') + 1` for
non-empty account names, `0` for the empty/root name. Confirmed to match
what Ledgerkit's existing `Query.depth` already assumes.

- Construction/validation: `parseDepthSpecQuery`/`parseDepthSpec`
  (`Query.hs:489-506`) requires `d >= 0` (the error message says "should
  be a positive number" but the actual guard is `d >= 0`, so `depth:0` is
  valid input, not an error) — `depth:-1` is a parse error. This exact
  boundary (`0` valid, negative rejected) is source-only; the manual
  doesn't state it explicitly (`hledger.1:7325-7332` just says "N").
- Matching at posting/transaction level uses the **any-posting** rule,
  same shape as `Acct`: `matchesTransaction q@(Depth _) t = any (q
  \`matchesPosting\`) $ tpostings t` (`Query.hs:965`) — a transaction
  matches `depth:N` if **any** posting's account is at or above that
  depth, not all.
- `depth:0` is a legal input but matches essentially no real account
  (`accountNameLevel >= 1` for any non-root account) — confirmed both by
  the predicate math and by hledger's own test suite showing
  `register --depth 0` collapses everything into a single aggregate `...`
  row rather than filtering transactions out
  (`hledger/test/register/depth.test:53-71`) — **this display-aggregation
  behaviour is a separate mechanism from the pure filter predicate** and
  is NOT part of the `Depth` query-type's boolean-match semantics; it's
  `balance`/`register`'s own account-name-clipping logic layered on top.
  Recommend Stage C treat `depth:N` strictly as the `QueryAST` boolean
  predicate (`accountNameLevel(a) <= N`); depth-driven display truncation/
  aggregation for `balance`/`register` is separate report-layer work, not
  something the `QueryAST` evaluator itself should attempt (it isn't a
  pure predicate — it changes what account name gets displayed).
- Out of scope, noted only so it isn't accidentally implemented:
  `depth:REGEX=N` (custom per-account depth, `DepthAcct`, `Query.hs:119,
  502-506`; manual `hledger.1:7063-7075`) is a distinct, separate form.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for the bare `depth:N` predicate as defined above. `status: proposed`.

## 5. `status:` / `status:*` / `status:!`

**Target behaviour:** a fixed 3-way enum, not a regex. `parseStatus`
(`Query.hs:553-557`):
```
s ∈ {"*","1"} → Cleared
s ∈ {"","0"}  → Unmarked
s == "!"      → Pending
otherwise     → parse error
```
- Manual: `hledger.1:7353-7358` — "status:, status:!, status:* — Match
  unmarked, pending, or cleared transactions respectively" (doesn't
  mention the `"1"`/`"0"` synonyms at all — those are source-only,
  confirmed by the doctest `parseQueryTerm nulldate "status:1" == Right
  (StatusQ Cleared, [])` and `"status:0" == Right (StatusQ Unmarked, [])`,
  `Query.hs:1102-1106`). **The task's scope note lists only `*`/`!`/
  none** — if Ledgerkit doesn't implement the `1`/`0` synonyms, that's a
  real (if minor) subset gap versus hledger's actual `parseStatus`
  grammar, worth its own small note rather than silently claiming full
  equivalence.
- hledger's own test suite is unusually explicit and directly confirms
  all three base forms *and* the same-prefix-OR rule for `status:`:
  `hledger/test/journal/status.test:65-101` — `status:*` matches cleared
  only (test 8), `status:!` matches pending only (test 9), bare `status:`
  matches unmarked only (test 10), and **"multiple status: queries are
  OR'd"** is stated verbatim as the test's own comment, with
  `print status: status:!` returning both the unmarked and the pending
  transaction (test 11, lines 91-101). This is the strongest evidence in
  the whole brief — an executable-shaped fixture already exists upstream
  that `compat-differential-tester` could essentially port directly (with
  the caveat in `10-source-assisted-development.md` §10.3/§10.5 about
  checking any doc/example-licensing distinction before copying a fixture
  verbatim).
- Matching: `matchesTransaction (StatusQ s) t = tstatus t == s`
  (`Query.hs:962`, direct equality, no inheritance needed at the
  transaction level). At the posting level, status is **inherited from
  the parent transaction when the posting's own status is Unmarked**:
  `postingStatus Posting{pstatus=s, ptransaction=mt} = case s of
  Unmarked -> maybe Unmarked tstatus mt; _ -> s`
  (`Hledger/Data/Posting.hs:428-431`), and `matchesPosting (StatusQ s) p =
  postingStatus p == s` (`Query.hs:915`) uses that inheriting accessor,
  not `pstatus` directly. This inheritance rule is source-only, not in
  the manual, and matters for any posting-oriented report (`register`/
  `balance`) applying `status:`.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for `*`/`!`/bare-none and their combination-by-OR behaviour,
`status: proposed`. Recommend a **separate, explicit** small note (not
necessarily a full register entry yet) if Ledgerkit's initial
implementation omits the `"1"`/`"0"` synonyms — that specific omission
would be `unsupported`/`subset` relative to `parseStatus`'s actual
grammar, not silently "the same thing."

## 6. `not:` negation, implicit AND, same-prefix-repetition OR

This is where the task's flagged footgun lives, and it can now be
answered precisely from source, not just the manual.

**The rule, exactly:** `combineQueriesByType` (`Query.hs:217-223`):
```haskell
combineQueriesByType pats =
  let (descpats, pats')   = partition queryIsDesc pats
      (acctpats, pats'')  = partition queryIsAcct pats'
      (statuspats, other) = partition queryIsStatus pats''
  in simplifyQuery $ And $ [Or acctpats, Or descpats, Or statuspats] ++ other
```
Manual states the same result in prose (`hledger.1:7412-7422`, "Space-
separated queries": "any of the description terms AND any of the account
terms AND any of the status terms AND all the other terms") — **but the
manual is silent on how `not:` interacts with this grouping.** The source
is decisive and the manual doesn't contradict it, it just doesn't say it:

`queryIsAcct`, `queryIsDesc`, `queryIsStatus` (`Query.hs:656-674`) each
match **only the bare, unnegated constructor**:
```haskell
queryIsAcct (Acct _) = True
queryIsAcct _         = False   -- explicitly False for `Not (Acct _)`
```
So `partition queryIsAcct` does **not** pull `Not (Acct ...)` terms into
the OR-grouped bucket for that prefix — a negated term of any prefix
(including acct:/desc:/status:) falls straight into the `other` list,
which is AND'd in individually, term by term. Concretely:

- `acct:a acct:b` → `Or [Acct a, Acct b]` (match account a **or** b) —
  confirmed by doctest `Query.hs:1055` and by `parseBooleanQuery`'s
  equivalent doctest at `Query.hs:1074-1075`.
- `not:acct:a not:acct:b` → `And [Not (Acct a), Not (Acct b)]` (must match
  **neither** a **nor** b) — **not** `Or [Not (Acct a), Not (Acct b)]`
  (which would mean "match not-a or not-b," a much weaker exclusion that's
  almost always true). This is the exact footgun the task asked to nail
  down, and the answer is: same-prefix OR-grouping applies **only to the
  unnegated form** of `acct:`/`desc:`/`status:`; negated instances (of any
  prefix at all) are always plain AND'd, one term at a time.
- No **directly executable** upstream test was found in the pinned clone
  covering the specific two-negated-same-prefix-terms case
  (`hledger/test/print/query-not-acct.test` only covers a single `not:a`
  term, `hledger/test/journal/status.test` only tests the *positive*
  OR-combination for `status:`) — so this conclusion, while high-
  confidence from reading `queryIsAcct`/`combineQueriesByType` directly,
  rests on **source evidence only, not test-suite evidence**, for the
  negated-double-term case specifically. Flagged as the single
  highest-priority fixture for `compat-differential-tester` to construct
  (e.g. a journal with postings to `a`, `b`, `c`; query
  `not:acct:a not:acct:b`; assert only `c`-touching transactions are
  shown) before this sub-behaviour moves past `proposed`.
- `not:` wraps recursively and stacks: `parseQueryTerm d (T.stripPrefix
  "not:" -> Just s) = ... Right (Not q, qopts)` (`Query.hs:296-299`);
  doctest/test confirm `not:desc:a b` → `Not (Desc "a"), ...` combined
  with bare `b` (`Query.hs:1101`), and the manual explicitly documents
  double-negation as a working trick: `not:not:...` (`hledger.1:7409-
  7411`).
- Implicit AND across *different* prefixes is unconditional and
  uncontroversial: e.g. `date:2022 desc:amazon depth:2` are three
  different-typed terms, all AND'd, no OR ambiguity — manual
  `hledger.1:7204-7207` example, `desc:amazon desc:amzn` (same prefix,
  OR'd) AND'd with `date:2022` (different prefix).
- Important scope boundary: everything above describes the **space-
  separated / implicit** query grammar (`parseQueryList`/
  `combineQueriesByType`), which is what Stage C's initial target list
  implies. hledger *also* has a fully separate, explicit
  `expr:'... AND ... OR ...'` boolean-query syntax (`parseBooleanQuery`,
  `Query.hs:329-437`; manual `hledger.1:7433-7508`) with real
  `NOT`/`AND`/`OR` keywords and parentheses — a **different** grammar
  layered via a distinct prefix (`expr:`/`any:`/`all:`), not something the
  six in-scope terms need to parse themselves. Not researched in depth
  since not in scope, beyond noting it exists and that `date:`
  specifically **cannot** appear inside an `OR` there (`hledger.1:7461-
  7463`, `Query.hs:379-386`) — flagged only because it's adjacent enough
  to `date:` that a future researcher shouldn't assume it's already
  covered by this brief.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for `not:` wrapping and for implicit-AND/same-prefix-OR (acct/desc/status
only) among unnegated terms, `status: proposed`. The negated-same-prefix
interaction specifically should be recorded as its own sub-note in the
register entry's `reason:` field flagging "source-only evidence, no
upstream executable test found in the pinned 1.52.4 test suite for this
exact case" — so `compat-differential-tester` treats it as a priority,
not an afterthought.

---

## 5 (regex boundary). `HledgerRegex` vs Python `re` — the compatible-subset boundary, for `acct:`/`desc:`/bare-pattern specifically

Source: `hledger-lib/Hledger/Utils/Regex.hs` (module docstring, lines
1-38; `toRegexCI`, lines 138-140) and manual `hledger.1:733-775`
("hledger's regular expressions", numbered list at 736-759).

| Construct | hledger (regex-tdfa via `toRegexCI`) | Python `re` | Verdict for `HledgerRegex` |
|---|---|---|---|
| Default case sensitivity | Always case-insensitive for `acct:`/`desc:` (`toRegexCI` used unconditionally, `Query.hs:301,304`) — no per-query way to opt into case-sensitive | Case-sensitive unless `re.IGNORECASE` set | **Must-implement, not optional**: Ledgerkit's compiler must always pass `re.IGNORECASE` (or equivalent) for these two terms. Compatible if implemented this way. |
| Match mode | Infix/unanchored (`matchTest`, unanchored substring test) — manual point 2 | `re.search` is unanchored; `re.match`/`fullmatch` are anchored | Ledgerkit **must** use `re.search`, never `re.match`/`fullmatch` — a silent-divergence risk if the wrong API is picked, not a regex-syntax issue. |
| Literals, `.`, `*`, `+`, `?`, alternation `|`, unnamed groups `(...)`, bounded repetition `{n,m}`, anchors `^`/`$` | POSIX ERE (manual point 3) | Same, PCRE-compatible | Behave identically for a pure boolean match/no-match test (no capture extraction in Stage C's predicate-only scope). **In `HledgerRegex`.** |
| GNU word boundaries `\b`, `\B` | Supported (manual point 4) | Supported, same meaning for ASCII word chars; Python's `\b` is Unicode-word-aware by default for `str` patterns (minor edge-case divergence for non-ASCII "word" characters, not confirmed either way against hledger — flag for differential testing) | Mostly **in `HledgerRegex`**, with a flagged minor Unicode-word-class caveat. |
| GNU word boundaries `\<`, `\>` | Supported (manual point 4) | **Not supported at all** — Python `re` has no such anchor; `\<`/`\>` are treated as escaped literal `<`/`>` characters, silently, no error | **Excluded from `HledgerRegex`** — a silent (non-erroring) divergence, the dangerous kind. |
| POSIX ERE (implied support for bracket expressions generally) | POSIX ERE per manual point 3 | Python `re` supports ordinary bracket expressions `[abc]`, ranges `[a-z]`, negation `[^...]` identically | **In `HledgerRegex`** for plain bracket expressions. |
| POSIX named classes `[[:alpha:]]`, `[[:digit:]]` etc | Not demonstrated with a citable example in the manual or the pinned test suite — flagged as *unconfirmed*, inferred only from "POSIX ERE" being the stated engine family; needs an executable check | Python `re` does **not** interpret `[[:alpha:]]` as a class — it's parsed as a literal bracket-expression character set containing `:`, `a`, `l`, `p`, `h`, etc. — silently wrong, not an error | **Excluded from `HledgerRegex`** regardless of the unconfirmed hledger side, precisely because Python's silent misinterpretation makes this dangerous either way. Recommend `compat-differential-tester` confirm hledger's actual behaviour here. |
| Backreferences **inside the search pattern** (e.g. `desc:(foo)\1`) | Explicitly **not** supported as backreferences in a match pattern — manual point 5: "\1... will match the digit 1" (i.e., in a query regex, `\1` is a literal "1", not a backreference) | Python `re` **does** support `\1` as a real backreference inside a pattern | **Excluded from `HledgerRegex`** — a sharp, silent divergence: the same pattern text means two structurally different things. |
| Backreferences **in replacement text** (aliases, CSV) | Supported (manual point 5) | N/A — not a query-matching concern, out of scope for these 5 terms | Not applicable to acct:/desc: query matching; noted only to avoid confusing it with the row above. |
| Lazy quantifiers `*?`, `+?`, `??` | Explicitly **not supported** (manual point 6) — exact failure mode (compile error vs. silently-different) not confirmed | Supported, non-greedy semantics | **Excluded from `HledgerRegex`.** Recommend `compat-differential-tester` determine the actual failure mode since the manual only says "not supported," not what happens. |
| Inline mode modifiers `(?i)`, `(?s)`, `(?m)` | Explicitly **not supported** — doubly confirmed: manual point 6 *and* the `Regex.hs` module docstring's own "Current limitations" note (`Regex.hs:37`, "(?i) and similar are not supported") | Fully supported | **Excluded from `HledgerRegex`** — high confidence, two independent citations. |
| Perl-style shorthand classes `\d`, `\w`, `\s` | Explicitly **not supported**, grouped with the above in manual point 6 | Fully supported | **Excluded from `HledgerRegex`.** |
| Lookaround `(?=...)`, `(?!...)`, `(?<=...)`, `(?<!...)`; named groups `(?P<name>...)`; non-capturing groups `(?:...)` | Not mentioned at all — covered by manual point 6's catch-all "anything else not mentioned above" | Fully supported | **Excluded from `HledgerRegex`** — and this is exactly the plan's own `PythonRegex` superset list (`07-query-regex.md` §7.3), so this brief corroborates rather than changes that boundary. |
| Leftmost-longest (POSIX) vs leftmost-first (PCRE) alternation semantics | POSIX leftmost-longest | PCRE leftmost-first/backtracking | **Does not affect Stage C's scope**: this only changes *which substring/group* a match reports, not *whether* a match exists. Since `acct:`/`desc:` here are pure boolean predicates (no capture extraction, no replacement), this divergence is irrelevant to Stage C — flagged as a **correction to `07-query-regex.md` §7.3's framing**, which currently lists this as a live risk without that scope qualifier. It *does* matter for hledger features that extract or replace (aliases, `tag:NAME=VALUE` capture, CSV rules) — none of which are in this brief's six items. |

**Bottom line for `HledgerRegex`'s compatible subset** (feeding
`07-query-regex.md` §7.3 directly): literals, `.`, `*`, `+`, `?`, `{n,m}`,
alternation `|`, plain (unnamed, non-capturing-as-Python-understands-it)
groups `(...)`, anchors `^`/`$`, plain bracket expressions `[abc]`/
`[a-z]`/`[^...]`, and GNU `\b`/`\B` word boundaries — always compiled with
`re.IGNORECASE` and matched with `re.search`. Everything else in the table
above (POSIX named classes, `\<`/`\>`, in-pattern backreferences, lazy
quantifiers, inline mode flags, Perl shorthand classes, lookaround,
named/non-capturing groups) is out of `HledgerRegex` and belongs either to
`PythonRegex` (extension, `kind: extension`) or to a specific
`unsupported`/`unexplained_mismatch` register entry once tested.

---

## Directly-translated-material flag

Per `10-source-assisted-development.md` §10.3: **nothing in this research
rises to "directly translated material."** Every algorithm here
(colon-count depth, the acct/desc/status OR-then-AND partition, the
not:-wrapping recursion, the exclusive-end-date span construction) is a
small, obvious, essentially-unique-shape algorithm — reading hledger's
Haskell source to *understand* these falls squarely in
`10-source-assisted-development.md`'s "source inspection" / "algorithm
understanding" categories (cite in `evidence:`, no code-comment/
`THIRD-PARTY-NOTICES.md` requirement).

One item is worth explicit attention as a **borderline "adapted
implementation"** (§10.3's third category, not "directly translated," but
worth naming honestly): if Ledgerkit's Python evaluator ends up
structurally mirroring `combineQueriesByType`'s exact three-way
partition-then-OR-then-AND shape (rather than some independently-derived
equivalent structure), that's an *adapted implementation* — record it in
the register entry's `implementation:`/`evidence:` fields (and optionally
`knowledge/DECISIONS.md`, since the negation-doesn't-join-the-OR-bucket
behaviour is a non-obvious tradeoff worth a decision note), but it does
**not** require `directly_translated: true` (no Haskell expression/text is
being ported — Python's `partition`/set-membership idioms are
structurally different from Haskell's `Data.List.partition`, and the
*idea* being adapted is not copyrightable). Nothing here touches hledger's
actual regex engine internals (Ledgerkit uses Python `re` under an
explicit restricted-subset contract, not a reimplementation of
`regex-tdfa`), so the highest-risk category for this kind of research
(porting a regex engine's own logic) doesn't arise at all in this brief.

---

## Files consulted (absolute paths)

- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/07-query-regex.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/03-agent-led-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/09-compatibility-system.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/10-source-assisted-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/hledger-compatibility.md`
- `/home/cormac/projects/ledgerkit/dev-docs/compat-register/schema.md`
- `/home/cormac/projects/ledgerkit/dev-docs/compat-register/examples/LK-EXT-QUERY-001.yaml`
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Query.hs` (whole file; key sections lines 105-131, 210-327, 439-506, 552-598, 624-1024, 1042-1220 for doctests/tests)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Utils/Regex.hs` (whole file; 1-38 docstring, 134-176)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/AccountName.hs` (lines 159-167, 401-416)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Posting.hs` (lines 428-431)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Dates.hs` (lines 396-420, 840-975, 1005-1195, plus `spanFromSmartDate`/`fixSmartDate` around 422-444, 560-582)
- `/home/cormac/projects/hledger/hledger/hledger.1` (manual source; lines 651-776 "Regular expressions", 7054-7098 "Depth", 7099-7508 "Queries"/query types/boolean queries)
- `/home/cormac/projects/hledger/hledger/test/journal/status.test`
- `/home/cormac/projects/hledger/hledger/test/register/depth.test`
- `/home/cormac/projects/hledger/hledger/test/print/query-not-acct.test`
- `/home/cormac/projects/hledger/hledger/test/cli/query-args.test`
- `/home/cormac/projects/hledger/hledger/test/query-desc.test`

## Summary of proposed register entries (all `status: proposed`, none executable-verified)

| Proposed ID | Area | Kind | Notes |
|---|---|---|---|
| `LK-COMPAT-QUERY-ACCT-001` | query.acct | compatible | conditional on `HledgerRegex` subset + `re.IGNORECASE` + `re.search` |
| `LK-COMPAT-QUERY-DESC-001` | query.desc | compatible | same conditionality |
| `LK-COMPAT-QUERY-DATE-001` | query.date | compatible | subset only: single full simple date, or two full simple dates joined by `-`/`..`/`to`; **end-exclusive** |
| `LK-UNSUP-QUERY-DATE-002` | query.date | unsupported | smart/partial/relative dates, quarters — already implicit in `hledger-compatibility.md` |
| `LK-COMPAT-QUERY-DEPTH-001` | query.depth | compatible | predicate form only (`accountNameLevel <= N`); display-truncation is out of this entry's scope |
| `LK-COMPAT-QUERY-STATUS-001` | query.status | compatible | `*`/`!`/bare + same-prefix OR; note the `1`/`0` synonym gap if unimplemented |
| `LK-COMPAT-QUERY-BOOLCOMBINE-001` | query.combinators | compatible | `not:` + implicit AND + same-prefix OR (acct/desc/status only); **flag the negated-same-prefix sub-case as source-only evidence, top-priority differential-test fixture** |
| (existing) `LK-EXT-QUERY-001` | query.regex | extension | already drafted; this brief's §5 table is direct input to filling in its `HledgerRegex`/`PythonRegex` boundary precisely |

None of these proposed entries have been added to `dev-docs/compat-
register/` yet — that's implementation-time work (as each term is built),
not this brief's own output.

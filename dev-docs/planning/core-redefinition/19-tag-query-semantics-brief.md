# 19. `tag:NAME[=REGEX]` query-term semantics brief (Stage C follow-on)

Produced by `hledger-researcher`, scoped to `tag:NAME[=REGEX]` as flagged
"Stage C follow-on work" in `dev-docs/hledger-compatibility.md`'s Query
Language table and out of scope for
`17-query-semantics-brief.md` (§0 there explicitly excludes `tag:`).
Follows `17-query-semantics-brief.md`'s format and rigor per the lead's
request.

**Pinned baseline used:** local clone at `/home/cormac/projects/hledger`,
tag `1.52.4`, commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d` — verified
directly in this session (`git log -1` against the clone; tags
`hledger-1.52.4`/`1.52.4` both point at this exact commit). Same pin as
`17-query-semantics-brief.md` and `09-compatibility-system.md` §9.1.

**On the environment's pinned binary:** a real `hledger` executable exists
at `/home/cormac/.local/bin/hledger` (`1.52.4-g33fa849e7-20260910`, same
commit). Per this role's hard rule, it was **not** run — everything below
is manual/source/test-suite-derived, `status: proposed` only, for
`compat-differential-tester` to executable-verify.

**Correction of a documented sibling-project error, verified
independently:** CodeCompass's own reference-experiment writeup
(`/home/cormac/projects/codecompass/planning/reference-projects/ledgerkit/
reference-experiment/54-tag-query-semantics-reference-experiment-
evaluation.md`, not itself relied on for any citation below) reports that
an earlier extraction of the manual's tag-inheritance section silently
dropped the third of three stated rules. I did not reuse that project's
line numbers; I located and read the section fresh in this session's own
clone, and it turns out there are **four** propagation rules stated across
two places in the manual (not three) — see §2 below, which quotes both
passages in full with line numbers I read directly.

---

## 0. Where this sits relative to `17-query-semantics-brief.md`

`tag:` reuses the same regex-construction primitive (`toRegexCI`) and the
same infix/case-insensitive contract as `acct:`/`desc:` (§7 below), so
§5 (regex-dialect boundary) of the existing brief needs no new table —
it already applies. What's new and specific to `tag:` is: (a) a
two-part name+optional-value match instead of a single field match, (b) a
genuinely more elaborate cross-entity inheritance model than any term in
the existing brief, (c) a **different** answer than `acct:`/`desc:`/
`status:` to the same-prefix-OR combination question, and (d) `payee:`/
`note:` turning out to be literally the same AST constructor as `tag:`,
with a sharp, easy-to-miss case-sensitivity trap in how their special
casing is keyed.

## 1. Construction and matching: `tag:NAME` and `tag:NAME=REGEX`

**Target behaviour:** `Tag Regexp (Maybe Regexp)` — a tag-name regex and
an optional tag-value regex, both **case-insensitive infix** matches
(`toRegexCI`), identical dialect/engine to `acct:`/`desc:`.

- AST: `Tag Regexp (Maybe Regexp) -- ^ match if a tag's name, and
  optionally its value, is infix-matched by the respective regexps`
  (`hledger-lib/Hledger/Query.hs:115`).
- Construction/parsing — `parseTag` splits on the **first** `=` only:
  ```haskell
  parseTag :: T.Text -> Either RegexError Query
  parseTag s = do
      tag <- toRegexCI $ if T.null v then s else n
      body <- if T.null v then pure Nothing else Just <$> toRegexCI (T.tail v)
      return $ Tag tag body
    where (n,v) = T.break (=='=') s
  ```
  (`Query.hs:482-487`). `T.break (=='=')` gives `v` as either empty (no
  `=` present at all) or starting with `=`; `T.tail v` drops that leading
  `=`, so **only the first `=` is a separator** — a value containing a
  literal `=` (e.g. `tag:rate==0.05` meaning tag name `rate`, value
  `=0.05`) is preserved intact in the value regex, not re-split. Both `n`
  and the value are compiled with `toRegexCI` — the exact same function
  `acct:`/`desc:` use (`Query.hs:301,304` per the existing brief).
  Doctest confirmation: `parseQueryTerm nulldate "tag:a" @?= Right (Tag
  (toRegexCI' "a") Nothing, [])` and `parseQueryTerm nulldate "tag:a=some
  value" @?= Right (Tag (toRegexCI' "a") (Just $ toRegexCI' "some value"),
  [])` (`Query.hs:1114-1115`).
- Matching primitive, shared by every context: `patternsMatchTags namepat
  valuepat = any (matches namepat valuepat) where matches npat vpat (n,v)
  = regexMatchText npat n && maybe (const True) regexMatchText vpat v`
  (`Query.hs:1008-1010`) — i.e. a `tag:` term matches a **list** of
  `(name,value)` tags if **any one** tag in that list has its name
  infix-matched by `namepat` **and** (if a value pattern was given) its
  value infix-matched by `valuepat`. Bare `tag:NAME` (no `=`) matches
  purely on name, any value (including the empty-value case, e.g. a tag
  written as `foo:` with nothing after the colon).
- Manual, `hledger.1:7372-7395` (`.SS tag: query`), quoted in full since
  it is short and dense:
  > `tag:NAMEREGEX[=VALREGEX]` — Match by tag name, and optionally also
  > by tag value. Note: Both regular expressions do infix matching. If
  > you need a complete match, use `^` and `$`. Eg: `tag:'^fullname$'`,
  > `tag:'^fullname$=^fullvalue$'`. To match values, ignoring names, do
  > `tag:.=VALREGEX`. Accounts also inherit the tags of their parent
  > accounts. Postings also inherit the tags of their account and their
  > transaction. Transactions also acquire the tags of their postings.
  (line numbers: 7372 heading, 7373 syntax, 7381-7385 infix/anchor note
  and examples, 7388 the `tag:.=VALREGEX` convention, 7390/7392/7395 the
  three inheritance bullets — see §2 for why there are actually **four**
  distinct propagation rules once the separate "Tag propagation" section
  is read too).
- hledger's own test suite exercises name-only, name+value, and the
  anchoring gotcha directly: `hledger/test/query-tag.test` — test 2
  ("reports can filter by tag existence", `tag:foo` matches any value),
  test 3 ("or tag value", `tag:foo=bar` excludes a same-named tag with a
  different value), tests 9-13 (`accounts --declared tag:type=a` matches
  both `type:A` and `type:Liability` because "a" is an infix substring of
  "Liability" too — explicitly demonstrating why the manual's anchoring
  advice exists, then `tag:type=^a$` narrows to the single exact match).

**Proposed classification:** `compatible` (`relationship: equivalent`) for
the bare name-match and name+value-match construction/matching contract
itself, conditional on the same `HledgerRegex` subset and `re.IGNORECASE`/
`re.search` contract as `acct:`/`desc:` (§7). `status: proposed`. This
classification concerns the **matching primitive only** — see §9 for why
Ledgerkit cannot yet exercise this primitive at all today.

## 2. The tag-inheritance model — all four rules, independently re-verified

This is the section the sibling project's own retrospective flags as
error-prone, so it is quoted and cross-checked against source in full,
not excerpted by line range from memory.

**Manual, two places, read as full sections (not partial ranges):**

1. `.SS Tags` / `.SS Tag propagation`, `hledger.1:2494-2635`. The
   propagation subsection (`2554-2567`) states, verbatim, as a numbered
   list:
   > In addition to what they are attached to, tags also affect related
   > data in a few ways, allowing more powerful queries:
   > 1. Accounts -> postings. Postings inherit tags from their account.
   > 2. Transactions -> postings. Postings inherit tags from their
   >    transaction.
   > 3. Postings -> transactions. Transactions also acquire the tags of
   >    their postings.

   This is the list the sibling project's writeup describes truncating
   to two items — I read through line 2635 (past the worked three-column
   table at `2575-2628`, which walks a concrete `account`/`assets:
   checking`/`expenses:food` example through exactly these three rules)
   and confirm all three are present and this is the complete list *in
   this section*.

2. `.SS tag: query`, `hledger.1:7372-7395`, quoted in full in §1 above,
   states a **fourth**, distinct rule not in the "Tag propagation" list:
   > Accounts also inherit the tags of their parent accounts.
   (`hledger.1:7390`), immediately followed by the same three
   posting/transaction rules restated (`7392`, `7395`).

   So the complete, correctly-assembled rule set, read from both
   sections, is:
   - **(A) Account ← parent account**, up the account-name hierarchy
     (`hledger.1:7390` only — this rule does not appear in the "Tag
     propagation" section at all, which is presumably *why* it's easy to
     miss if only that section is read).
   - **(B) Posting ← its own account** (`7390`/`2559-2561`, both agree).
   - **(C) Posting ← its transaction** (`7392`/`2562-2564`, both agree).
   - **(D) Transaction ← all its postings** (`7395`/`2565-2567`, both
     agree).

**Source, confirming and sharpening all four rules precisely:**

- **(A)** `journalInheritedAccountTags :: Journal -> AccountName -> [Tag];
  journalInheritedAccountTags j a = foldl' (\ts a' -> ts \`union\`
  journalAccountTags j a') [] as where as = a : parentAccountNames a`
  (`hledger-lib/Hledger/Data/Journal.hs:524-529`), built on top of
  `journalAccountTags j a = M.findWithDefault [] a jdeclaredaccounttags`
  (`Journal.hs:520-521`) — i.e. **only tags declared via an `account NAME
  ; tag:value` directive comment** are in scope for this rule; a
  posting's own inline comment tags never feed account-level tag
  inheritance (there is no "infer account tags from postings" direction
  anywhere in source). `union` here is `Data.List.union` (confirmed by
  the `import Data.List (... union ...)` at `Journal.hs:131`), which
  dedupes by full `(name,value)` equality (`Tag = (TagName, TagValue)`,
  `hledger-lib/Hledger/Data/Types.hs:442`), not by name alone.
- **(B)** `journalPostingsAddAccountTags :: Journal -> Journal;
  journalPostingsAddAccountTags j = journalMapPostings addtags j where
  addtags p = p \`postingAddTags\` (journalInheritedAccountTags j $
  paccount p)` (`Journal.hs:648-650`) — this **mutates `Posting.ptags`
  directly at journal-load time** (inside `journalFinalise`,
  `hledger-lib/Hledger/Read/Common.hs:373-397`), it is not computed
  on-the-fly at query-evaluation time the way (C)/(D) below are. Because
  of this ordering, by the time any `Tag` query runs against a loaded
  `Posting`, `ptags` **already contains** the posting's account's own +
  inherited-from-parent declared tags folded in via rule (A)+(B)
  combined.
  - **Conditionality, source-only, not in the manual at all:** this
    mutation only happens `if auto_posting_tags_ then
    journalPostingsAddAccountTags else id` (`Common.hs:397`), and
    `auto_posting_tags_` is computed as `autopostingtags = not $ command
    == "print" && moutputformat == Just "beancount"`
    (`hledger/Hledger/Cli/CliOptions.hs:642`) — i.e. it is **on by
    default for every command and output format except `print
    --output-format=beancount`**. For any normal `hledger` invocation a
    differential tester would construct (including plain `print`),
    account-tag-to-posting propagation is active; only the beancount
    export path disables it. Flagged as a minor completeness note, not a
    live risk for Stage C's scope (Ledgerkit has no beancount export).
  - `postingAddTags p@Posting{ptags} tags = p{ptags=ptags \`union\`
    tags}` (`hledger-lib/Hledger/Data/Posting.hs:467-468`) uses the same
    `Data.List.union`, full-pair equality. **This means the mutation's
    own doc-comment — "If a tag already exists on the posting, it is not
    changed (the account tag will be ignored)" (`Journal.hs:646-647`,
    on the sibling function `journalPostingsAddCommodityTags`'s
    docstring, which uses the identical `postingAddTags` mechanism) — is
    only literally true for an exact `(name,value)` duplicate.** If a
    posting has its own `foo:bar` and the account declares `foo:baz`,
    `union` does **not** drop the account's tag by name; both
    `("foo","bar")` and `("foo","baz")` end up in `ptags`. This does not
    change `tag:` query-match *outcomes* in practice, because every
    `tag:` matcher tests the whole tag list with `any` (§1) — having both
    entries present rather than one is functionally invisible to a
    boolean predicate; it would only be visible in **display** contexts
    that enumerate every tag (e.g. `print`, the `tags` command). **There
    is no name-based "posting tag overrides inherited tag" behaviour
    anywhere in the query-matching code path** — this directly answers
    the lead's question: for `tag:` matching specifically, a posting's
    own tag and an inherited tag of the same name **both apply**
    independently; neither shadows the other for match-boolean purposes.
- **(C)** `postingAllTags :: Posting -> [Tag]; postingAllTags p = ptags p
  ++ maybe [] ttags (ptransaction p)` (`hledger-lib/Hledger/Data/
  Posting.hs:439-440`) — used directly by `matchesPosting (Tag n v) p`
  (`Query.hs:924`, see §4). Since `ptags p` at match-time already
  contains the (A)+(B) account-inherited tags (previous bullet), a
  posting-level `tag:` query in practice sees: the posting's own written
  tags, the tags of its account and that account's ancestors, **and**
  its transaction's own tags — all flattened into one list tested by
  `any`.
- **(D)** `transactionAllTags :: Transaction -> [Tag]; transactionAllTags
  t = ttags t ++ concatMap ptags (tpostings t)` (`Posting.hs:443-444`) —
  used by `matchesTransaction (Tag n v) t` (`Query.hs:971`, see §4). Since
  each posting's `ptags` already includes its own account's inherited
  tags (per (A)+(B)), a **transaction**-level `tag:` query transitively
  sees every one of its postings' accounts' declared tags too, not merely
  each posting's own written comment tags — a two-hop chain
  (account→posting via (B), posting→transaction via (D)) that is not
  obvious from reading `transactionAllTags`'s one-line definition alone;
  it only becomes visible by also reading the journal-load pipeline
  ordering in `Read/Common.hs`.
- Test-suite confirmation of the full chain, including the two-hop case:
  `hledger/test/tags.test` tests 14-21 build a journal with `account a ;
  type:A` / `account a:aa` (no own tags) and show `tag:type=a` matching
  postings/transactions/balances against `a:aa` purely via inherited
  parent-account tags (rule A), and matching whole transactions whose
  *only* postings are bare `(a)`/`(l)` virtual postings carrying no
  inline comment at all (rules A+B+D chained) — tests 19-21 specifically.
  `hledger/test/accounts.test` tests 11-12 additionally show the
  `accounts` command's own account-name matcher (`matchesAccountExtra`,
  see §6) matching `a:b` by its own declared tag and by its parent's
  inherited tag, but **not** by a sibling posting's inline comment tag
  (`p:`) — a scope boundary specific to that one command, not the general
  `tag:` predicate (§6 explains why).

**Proposed classification:** `compatible` (`relationship: equivalent`) for
all four rules as a *target* contract, `status: proposed`, **conditional
on Ledgerkit first building the tag data model these rules operate on at
all** — see §9, which is the actual current blocker, not a compatibility
question.

## 3. `payee:`/`note:` are literally the same `Tag` AST node — with a sharp case-sensitivity trap

Confirmed directly from source, not inferred from any other project's
summary, per the task's instruction.

- `payeeTag :: Maybe Text -> Either RegexError Query; payeeTag = fmap (Tag
  (toRegexCI' "payee")) . maybe (pure Nothing) (fmap Just . toRegexCI)`
  and `noteTag` identically for `"note"` (`Query.hs:135-141`). Both are
  invoked from `parseQueryTerm`: `T.stripPrefix "payee:" -> Just s =
  (,[]) <$> payeeTag (Just s)` / `"note:" -> Just s = (,[]) <$> noteTag
  (Just s)` (`Query.hs:302-303`) — **`payee:X` parses to exactly `Tag
  (toRegexCI' "payee") (Just (toRegexCI X))`**, the identical AST
  constructor `tag:payee=X` would produce. There is no separate `Payee`
  or `Note` query constructor in the `Query` sum type at all
  (`Query.hs:105-131`, reproduced in `17-query-semantics-brief.md`'s
  companion research if cross-checking is wanted) — `payee:`/`note:` are
  syntactic sugar over `Tag`, confirmed, not a guess.
- But the **matcher** special-cases these two exact literal name strings
  to read a *derived* field instead of doing an actual tag-list lookup:
  ```haskell
  matchesTransaction (Tag n v) t = case (reString n, v) of
    ("payee", Just v') -> regexMatchText v' $ transactionPayee t
    ("note", Just v')  -> regexMatchText v' $ transactionNote t
    (_, v')             -> patternsMatchTags n v' $ transactionAllTags t
  ```
  (`Query.hs:968-971`; `matchesPosting`'s equivalent is at `Query.hs:
  921-924`). `transactionPayee`/`transactionNote` are **not** tag lookups
  at all — they split `tdescription` on the first `|` character:
  `transactionPayee = fst . payeeAndNoteFromDescription . tdescription`
  (`hledger-lib/Hledger/Data/Transaction.hs:127-131`) — i.e. `payee:X`
  matches against (part of) the transaction's *description text*, wholly
  independent of any real inline tag literally named "payee" that a user
  might write in a comment.
- **The trap:** `reString n` is the regex's *original source text*, set
  verbatim at construction (`reString :: Text` field, `hledger-lib/
  Hledger/Utils/Regex.hs:87-88`) — it is a plain, case-sensitive Haskell
  `Text` equality check against the literal strings `"payee"`/`"note"`,
  **not** run through the regex engine's own case-insensitivity. So:
  - `payee:X` (the dedicated prefix) always constructs the name regex
    from the hardcoded lowercase literal `"payee"` (`toRegexCI'
    "payee"`), so the special case **always** fires for that prefix.
  - But a user typing `tag:payee=X` directly gets the *same* special
    case (since `parseTag`'s `n` for that literal input is `"payee"` too)
    — so `tag:payee=X` and `payee:X` are truly interchangeable here.
  - A user typing `tag:Payee=X` or `tag:PAYEE=X` gets a **different**
    `reString n` ("Payee"/"PAYEE"), so `(reString n, v)` does **not**
    match `("payee", Just v')`, and the query falls through to the
    generic `patternsMatchTags` branch instead — silently switching from
    "match the derived payee substring of the description" to "look for
    an actual tag literally named Payee/PAYEE (case-insensitively, since
    `patternsMatchTags` does use the compiled case-insensitive regex) in
    the tag list" — a materially different match target, reached only by
    changing letter case in a query string that a user would reasonably
    expect to be case-insensitive throughout (since the *regex* parts of
    `tag:` genuinely are case-insensitive; only this one internal literal
    dispatch check is not).
  - Bare `tag:payee` (no `=`, so `v = Nothing`) never hits the special
    case at all regardless of case, because the case-match requires
    `Just v'` — it falls straight to `patternsMatchTags`, i.e. it looks
    for a literal tag named "payee" and ignores `transactionPayee`
    entirely. So `tag:payee` and `payee:` (bare prefix, if it parses;
    `payee:` with an empty argument still gives `Just ""` per
    `payeeTag (Just s)` always wrapping in `Just`) do **not** behave the
    same way, despite looking like they should.
- Manual: `payee:`/`note:` are documented as query types in their own
  right (`hledger.1`'s query-types list includes them, separate from the
  `tag:` subsection); the manual does **not** state anywhere that they
  are implemented as `tag:payee=`/`tag:note=` under the hood, nor does it
  mention the case-sensitivity trap above — this entire finding is
  source-only.

**Proposed classification:** informational for this brief (`payee:`/
`note:` are explicitly out of Stage C's stated scope per
`hledger-compatibility.md`'s table, which lists only `tag:`/`cur:`/
`PythonRegex` as pending) — no register entry proposed here, but flagged
because it directly bears on how Ledgerkit should design its own `Tag`
query node if it wants a clean path to `payee:`/`note:` later: **do not**
special-case those literal name strings inside the general tag-matching
function the way hledger does, without also deciding up front whether
Ledgerkit wants the same case-sensitivity trap (probably not — an
`intentional_divergence` candidate for a future brief, not this one, if
Ledgerkit chooses to make its own `payee:`/`note:` case-insensitive
end-to-end).

## 4. Transaction-level vs. posting-level matching: the `Tag` equivalent of the "any posting matches" rule

`17-query-semantics-brief.md` established that `Acct`/`Depth`/`Amt`/`Sym`
all define their transaction-level match as `any (q \`matchesPosting\`)
$ tpostings t` (`Query.hs:959-965`) — literally delegating to the
posting-level matcher for each posting and OR-ing the results. `Tag` does
**not** do this. Instead it has its own dedicated transaction-level
clause (§3's code block) that runs `patternsMatchTags` directly against
`transactionAllTags t = ttags t ++ concatMap ptags (tpostings t)`
(`Posting.hs:443-444`) — a hand-flattened list, not a call into
`matchesPosting`.

**These are functionally equivalent for any real (non-empty-posting-list)
transaction, but structurally different**, and it's worth being precise
about why: if `Tag` instead used the generic `any (matchesPosting q)
tpostings` shape, `matchesPosting (Tag n v) p` would test `postingAllTags
p = ptags p ++ ttags (ptransaction p)` for *each* posting — i.e. the
transaction's own `ttags` would be tested once per posting (redundant
repetition, harmless under `any`'s short-circuiting OR semantics) plus
each posting's own `ptags` once. That multiset (ignoring duplication) is
identical to what `transactionAllTags` computes directly. So: **the
observable match result is the same either way**, but hledger chose the
direct-flattening implementation for `Tag` rather than reusing the
any-posting delegation pattern used for `Acct`/`Depth`/`Amt`/`Sym`. A
degenerate transaction with zero postings (not achievable by hledger's
own parser/balancing rules, which require ≥2 postings per transaction) is
the only case where the two forms could theoretically diverge (the
any-posting form would vacuously return `False`, i.e. "no posting" means
"nothing to test"; the direct-flattening form would still test `ttags t`
against an empty `concatMap`, i.e. it would still consider the
transaction's own tags) — flagged only for completeness; not reachable
in practice and not worth encoding specially.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for the *observable* transaction-vs-posting matching behaviour (any tag
among {own txn tags, all postings' own tags, all postings' inherited
account tags} matches → transaction matches; own posting tags + its
transaction's tags + its account's inherited tags → posting matches),
`status: proposed`. Whether Ledgerkit's implementation mirrors hledger's
specific flattened-list shape or an equivalent any-posting-delegation
shape is an implementation choice with no observable difference — not
something this brief needs to prescribe.

## 5. Same-prefix combination: `tag:` does **not** get the `acct:`/`desc:`/`status:` OR treatment — at all, negated or not

This is the most consequential difference from the already-implemented
terms, and it is unambiguous, decisive source evidence (`Query.hs:
217-223`, quoted in full in `17-query-semantics-brief.md` §6):

```haskell
combineQueriesByType :: [Query] -> Query
combineQueriesByType pats = q
  where
    (descpats, pats')       = partition queryIsDesc pats
    (acctpats, pats'')       = partition queryIsAcct pats'
    (statuspats, otherpats)  = partition queryIsStatus pats''
    q = simplifyQuery $ And $ [Or acctpats, Or descpats, Or statuspats] ++ otherpats
```

`queryIsTag :: Query -> Bool; queryIsTag (Tag _ _) = True; queryIsTag _ =
False` **does exist** (`Query.hs:668-670`) — so the researcher's task
question "is there a `queryIsTag`?" is answered yes — but it is used
**only** inside `matchesTag`'s own Or/And/AnyPosting/AllPostings
recursion (`Query.hs:1019-1022`, a narrower helper analogous to
`matchesDescription`, used when directly testing a single bare `Tag`
value against a compound query, not when combining a space-separated
query string) and inside the general `filterQuery` combinator
(`Query.hs:generic`, unrelated to term-combination). It is **not** one of
the three predicates `combineQueriesByType` partitions on.

**Consequence:** `tag:a tag:b` (two *unnegated* `tag:` terms,
space-separated) does **not** OR-combine the way `acct:a acct:b` does.
Both `Tag` terms fall into `otherpats` and are AND'd — a transaction/
posting must have a tag matching **both** patterns to match the combined
query. This is a **stronger** asymmetry than the one
`17-query-semantics-brief.md` §6 found for `not:`: there, the rule was
"same-prefix OR applies to unnegated `acct:`/`desc:`/`status:` only, and
any negated term of any prefix always AND's individually." For `tag:`,
even the **unnegated** case never OR's — `tag:` behaves exactly like
`date:`/`depth:`/`amt:`/`sym:`/`code:`/`real:`/`type:` (all likewise
absent from `combineQueriesByType`'s partition list) with respect to
same-prefix repetition: always AND, never OR, negated or not.

- Direct source citation for the partition list omitting `queryIsTag`:
  `Query.hs:220-222` (quoted above) — decisive on its own.
- Manual: `hledger.1`'s "Space-separated queries" prose (`~7204-7226`,
  same passage `17-query-semantics-brief.md` §6 cites) only describes
  the desc/acct/status OR-grouping explicitly ("any of the description
  terms AND any of the account terms AND any of the status terms AND all
  the other terms") — `tag:` is one of "all the other terms" by omission,
  consistent with source, but the manual never states this negatively
  ("tag: does not OR-combine") — this is a source-derived conclusion, the
  manual is merely silent rather than contradicting it.
- Test-suite evidence found: `hledger/test/tags.test` test 16 ("And
  negatively match them by tag") runs `print tag:type=^a not:tag:type=^l`
  and gets an empty result on a journal where one transaction has both an
  `(a)`-typed and an `(l)`-typed posting — this demonstrates AND
  combination between a positive `tag:` and a negated `tag:` term, which
  is unsurprising given `not:` wrapping already forces AND regardless of
  the wrapped prefix (per the existing brief's §6 finding) — it does
  **not**, on its own, prove what happens with **two unnegated** `tag:`
  terms space-separated. **No test in the pinned suite was found
  exercising two bare, unnegated `tag:` terms combined space-separated**
  (only inside `expr:`'s explicit boolean grammar, e.g.
  `hledger/test/query-expr.test`'s `tag:transactiontag=B AND desc:3`
  constructions, which use explicit `AND`/`OR` keywords and are a
  different, already-out-of-scope grammar per the existing brief's §6
  final bullet). This specific sub-case — two unnegated `tag:` terms,
  space-separated, expected to AND rather than OR — rests on **source
  evidence only**, exactly the same evidentiary shape as the
  negated-same-prefix-acct case the existing brief flagged as its
  highest-priority differential-test fixture. Flagged identically here.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for "tag: terms always AND, never same-prefix-OR, regardless of
negation" as a target contract, `status: proposed`, with the specific
two-unnegated-terms sub-case flagged as source-only evidence needing a
priority differential-test fixture (e.g. a journal with transactions
tagged `a:1` only, `b:1` only, and both `a:1`+`b:1`; query `tag:a
tag:b`; assert only the both-tagged transaction matches — proving AND,
not OR).

## 6. Account-name-level `tag:` matching is a separate, narrower mechanism than posting/transaction-level `tag:` matching

Two genuinely different code paths exist for "does this account match a
`tag:` query," and conflating them would be a real correctness bug if
Ledgerkit's evaluator ever needs to filter bare account names (e.g. for
an eventual `accounts` command) rather than postings/transactions:

- The **general**, unconditional account matcher used for ordinary
  `acct:`-style account-name filtering: `matchesAccount (Tag _ _) _ =
  False` (`Query.hs:878`) — a bare `Tag` term **never** matches at the
  plain account-name level; this function has no way to see any tag data
  at all (it only receives an `AccountName`, a plain string).
- The **extended** matcher, used only by specific report/command code
  that explicitly threads through tag/type accessor functions:
  `matchesAccountExtra :: (AccountName -> Maybe AccountType) ->
  (AccountName -> [Tag]) -> Query -> AccountName -> Bool; ...
  matchesAccountExtra _ atags (Tag npat vpat) a = patternsMatchTags
  npat vpat $ atags a` (`Query.hs:889-897`). Its only callers in the
  pinned tree: `MultiBalanceReport.hs:253` (passing `journalAccountTags j`
  — **non-inherited**, directly-declared-only) and the `accounts`/`tags`
  CLI commands (`hledger/Hledger/Cli/Commands/Accounts.hs:76`,
  `Tags.hs:62`, both passing `journalInheritedAccountTags j` — inherited).
  Both accessors read **only** `jdeclaredaccounttags` (i.e. `account NAME
  ; tag:value` directive tags) — **never** any posting's own inline
  comment tags.
- Test-suite confirmation, verbatim comment from hledger's own suite:
  `hledger/test/accounts.test` test 11's comment states exactly this
  scope boundary: *"When matching accounts found in postings, tag: only
  matches the account's tags, not posting tags."* — with a fixture where
  a posting `c ; p:` (tag `p` on the posting only) is **not** picked up
  by `accounts tag:p`-style queries, only `account`-directive-declared
  tags are. Test 12's comment: *"tag: also matches tags inherited from
  parent accounts, currently"* (the word "currently" is hledger's own
  phrasing, not mine — read as a mild hedge by hledger's own maintainers,
  not as evidence of a documented future change; no changelog/roadmap
  note was found suggesting this is planned to change).

**Why this matters for Stage C specifically:** Ledgerkit's Stage C query
evaluator, per `dev-docs/hledger-compatibility.md`'s existing description,
operates on `Transaction`/`Posting` objects only (`ledgerkit.query.eval.
matches_posting`/`matches_transaction`) — there is no bare
account-name-level query evaluation entry point yet (no `accounts`
command in the wired set: `balance`, `register`, `accounts`, `stats`,
`print`... wait, `accounts` *is* listed in `hledger-compatibility.md`'s
wired-in set). If/when Ledgerkit's `accounts` command reuses the same
`tag:` node for account-name filtering that it uses for posting/
transaction filtering, this brief's finding means that reuse is **not**
transparently correct: hledger's own `accounts`/`tags` commands use a
narrower, declared-tags-only, no-posting-tags semantics for account-name
matching, distinct from the posting/transaction-level semantics in §1-§4.
This is exactly the kind of asymmetry `17-query-semantics-brief.md`
flagged for `acct:` (posting-vs-transaction) and `depth:` (predicate vs.
display-aggregation) — worth the lead's explicit attention before
`accounts -q "tag:..."` is wired up, not something to silently assume
"works the same as everywhere else."

**Proposed classification:** `unsupported` or `compatible` depending on
which of the two hledger mechanisms Ledgerkit's `accounts` command ends
up mirroring — not resolvable to a single classification without a lead
decision on scope; flagged as an open design question rather than
prejudged here.

## 7. Regex dialect: fully covered by the existing `HledgerRegex` subset, no distinct construct restrictions found

- Both the tag-name regex and the tag-value regex go through the
  identical `toRegexCI` construction path `acct:`/`desc:` use (`parseTag`,
  `Query.hs:483-485`, calling the same `toRegexCI` as `Query.hs:301,304`).
- `regexMatchText`/`matchTest` (unanchored substring test,
  `hledger-lib/Hledger/Utils/Regex.hs:174-175`) is the same matching
  function used for tag-name and tag-value matching inside
  `patternsMatchTags` (`Query.hs:1009-1010`) as for `acct:`/`desc:`.
- No tag-specific construct restriction, additional escape sequence, or
  different engine was found anywhere in `Regex.hs`'s module docstring
  (lines 1-38, the same "Current limitations" list `17-query-semantics-
  brief.md` §5 already transcribed) or in the manual's "hledger's regular
  expressions" section (`hledger.1:651-776`) that varies by which
  query-prefix invokes it.
- The one *usage-convention* difference worth noting (not an engine
  difference): the manual's `tag:.=VALREGEX` idiom (`hledger.1:7388`,
  "to match values, ignoring names") uses a bare `.` as the name pattern
  — this is not a special "match-anything" wildcard the query language
  defines for `tag:` specifically; it is simply the regular regex
  metacharacter `.` (any single character), which happens to match any
  non-empty tag name. This is unremarkable given `.` behaves identically
  in Python `re`, so no `HledgerRegex` boundary note is needed for it.

**Proposed classification:** Ledgerkit's existing `ledgerkit/query/
regex.py` `HledgerRegex`-subset validator (already built for `acct:`/
`desc:` per `17-query-semantics-brief.md` §5 and already wired per
`dev-docs/hledger-compatibility.md`'s "Regex dialect" note) is **directly
reusable, unchanged, for both the name and value regex arguments of
`tag:`** — no new dialect work needed. `compatible`/`relationship:
equivalent`, `status: proposed`, folded into the existing
`LK-EXT-QUERY-001` regex-dialect entry rather than a new one, since it is
the same boundary applied to a third/fourth call site (name regex, value
regex) rather than a new boundary.

## 8. hledger's own test-suite coverage, summarised (the gap the sibling project's experiment explicitly missed)

Both of the sibling project's two prior research attempts reportedly
never consulted hledger's own test suite for `tag:` at all. This session
did, and found substantial direct coverage:

| File | What it establishes |
|---|---|
| `hledger/test/query-tag.test` | Basic tag parsing on same/separate comment lines (test 1); `tag:foo` name-only existence match (test 2); `tag:foo=bar` value match, excluding a same-named-different-value tag (test 3); posting-level inheriting a transaction-level tag (test 4, rule C); `not:tag:.` finding untagged transactions (test 5); a `# ** 6.` test explicitly marked `XXX ?` by hledger's own maintainers (`reg tag:d` on `examples/sample.journal` returning empty, captioned "query is not affected by implicit tags") — flagged here as **hledger's own suite containing an acknowledged-uncertain case**, not something this brief resolves further; not concretely tied to any rule this brief documents with confidence, so not relied upon for any claim above. |
| `hledger/test/tags.test` | Account-tag-inheritance-driven matching at every level: declared-tag existence/negation on `accounts --declared` (tests 7-8), infix-vs-anchored value matching demonstrating the manual's own anchoring advice (tests 9-12), posting/transaction/balance-report matching purely via account-tag inheritance with zero posting-level comments (tests 14-18), and — the clearest evidence for rule (A) specifically — a two-level account hierarchy (`a` / `a:aa`) where only the parent declares a tag and the child still matches (tests 19-21). |
| `hledger/test/accounts.test` (tests 11-12) | The account-name-level `tag:` scope boundary in §6: declared-account-tag-only matching, explicitly **excluding** sibling posting comment tags, with hledger's own test comments stating this in prose. |
| `hledger/test/check-tags.test` | Confirms the separate `tag` **directive** / `check tags` validation mechanism (already `[IMPLEMENTED]` in Ledgerkit per `hledger-compatibility.md`) and enumerates hledger's built-in reserved tag names (`type`, `date`, `date2`, `generated-transaction`, etc., tests 6-7) — relevant context, not itself `tag:`-query behaviour. |
| `hledger/test/query-expr.test` | `tag:NAME=VALUE` used inside the separate `expr:`/boolean-query grammar (`AND`/`OR`/`NOT`, parenthesised) — confirms `Tag` composes normally inside that grammar; out of this brief's scope per the same boundary `17-query-semantics-brief.md` §6 already drew. |
| `hledger/test/journal/commodity-tags.test`, `hledger/test/csv.test`, `hledger/test/timeclock.test`, `hledger/test/timedot.test`, `hledger/test/forecast.test`, `hledger/test/descriptions.test`, `hledger/test/notes.test` | All use `tag:` as an incidental filtering mechanism for testing unrelated features (commodity tags, CSV import, timeclock/timedot formats, forecast, `descriptions`/`notes` commands) — confirms `tag:` is treated as a stable, general-purpose primitive throughout hledger's own suite, but none add new `tag:`-semantics information beyond what's cited above; not itemised further. |

**No test was found** covering: two unnegated `tag:` terms space-separated
(§5's flagged gap), the `payee:`/`note:` case-sensitivity trap (§3), or
the zero-posting-transaction edge case (§4, not reachable anyway).

## 9. The actual current blocker, reported plainly: Ledgerkit has no tag data model at all yet

Not a compatibility classification — a direct, checked-in-this-session
observation about `ledgerkit/`'s current state, offered because it
changes what "implementing `tag:`" concretely requires:

- `ledgerkit/models.py` and `ledgerkit/parser.py` have **no** `ptags`/
  `ttags`-equivalent field on `Transaction` or `Posting`, and no inline
  comment-tag parsing at all — confirmed both by grep (no `tag` hits
  besides the unrelated `tag` **directive** handling and
  `Journal.declared_tags`) and by `dev-docs/hledger-compatibility.md`'s
  own existing, accurate statement: *"Tags | `; tag:value` | Inline tag
  annotations silently ignored."*
- `ledgerkit/parser.py`'s `account` directive handling
  (`parser.py:1127-1147`) stores only a flat `list[str]` of account names
  (`declared_accounts`) — no per-account tag dict exists, so rule (A) (§2)
  has no substrate either.
- Consequently, this brief's §1/§2/§4/§5 classifications are proposals
  for a **target contract to build toward**, in the same spirit as
  `17-query-semantics-brief.md`'s `depth:` section proposed a contract
  before any `depth:` code existed — but the gap here is larger: `depth:`
  only needed a predicate over data Ledgerkit already had
  (`accountNameLevel`); `tag:` needs an entirely new inline-tag-parsing
  and tag-storage layer added to the core data model first (on
  `Transaction`, `Posting`, and arguably `account`-directive parsing for
  rule A), before any `tag:` query-matching code can be exercised at all,
  let alone differentially tested. This is squarely the lead's scoping
  decision, not something for this brief to resolve, but it would be a
  disservice to hand back a `tag:`-query-only brief without stating it
  plainly.

---

## Directly-translated-material flag

Per `10-source-assisted-development.md` §10.3, evaluated against the same
three-tier framework `17-query-semantics-brief.md` used:

- The core matching primitive `patternsMatchTags`/`postingAllTags`/
  `transactionAllTags` (§1, §2, §4) are each small, single-purpose
  functions (list concatenation + `any`/predicate-conjunction) — reading
  them to understand the *algorithm* is "source inspection"/"algorithm
  understanding" (§10.3's first two categories): cite in `evidence:`, no
  code-comment or `THIRD-PARTY-NOTICES.md` requirement.
- **Borderline "adapted implementation," flagged explicitly, same as the
  existing brief did for `combineQueriesByType`:** if Ledgerkit's Python
  `tag:` evaluator ends up structurally mirroring the exact three-part
  shape hledger uses — (i) a flat list-concatenation to build "all tags
  in scope for this posting/transaction" (`postingAllTags`/
  `transactionAllTags`'s literal `++`/`concatMap` shape), rather than
  e.g. a set-based or generator-based equivalent Ledgerkit derives
  independently — that is an adapted implementation worth recording in
  the eventual register entry's `implementation:`/`evidence:` fields (and
  optionally `knowledge/DECISIONS.md`, since the "posting's own tag does
  not override an inherited same-named tag, both apply" behaviour from
  §2 is exactly the kind of non-obvious tradeoff that file exists for).
  It does **not** rise to `directly_translated: true` — Python
  list/dict/set idioms replacing Haskell's `++`/`Data.List.union` are a
  structurally different expression, and the *idea* (flatten tag sources,
  then test with a single existential predicate) is an algorithm, not
  copyrightable text.
- **Nothing in this brief rises to "directly translated material"** in
  the strict sense (§10.3's fourth category: line-for-line ported
  expression) — no Haskell function body here is distinctive enough, or
  long enough, that a direct Python port of its literal structure would
  read as a translation of *expression* rather than of *idea*. This
  matches `17-query-semantics-brief.md`'s own conclusion for its
  comparable cases, so recorded here for consistency rather than as a new
  finding.
- If the lead later has Ledgerkit literally reproduce hledger's own test
  fixtures from `hledger/test/tags.test`/`query-tag.test`/`accounts.test`
  (§8) as Ledgerkit unit-test journals — e.g. porting the `account a ;
  type:A` / `account a:aa` two-level-inheritance fixture verbatim — that
  falls under §10.3's fifth category ("tests/examples derived from
  upstream"), which has the **same mandatory three-part recording
  requirement as directly-translated code** (code comment citing the
  exact file/lines, a `THIRD-PARTY-NOTICES.md` entry, `directly_
  translated: true` on the relevant register/test record) **plus** an
  explicit doc/example-licensing check first (`10-source-assisted-
  development.md` §10.3's fifth row, citing `02-licence-migration.md`
  §2.4 as still-unresolved on that specific point) — flagged here
  explicitly per this role's brief, since it is the lead's responsibility
  to execute those three steps, not mine to skip past silently if
  `compat-differential-tester` or the lead reach for these fixtures
  directly rather than writing independent ones.

---

## Files consulted (absolute paths, this session)

- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/17-query-semantics-brief.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/03-agent-led-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/09-compatibility-system.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/10-source-assisted-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/hledger-compatibility.md`
- `/home/cormac/projects/ledgerkit/ledgerkit/models.py` (grep only, confirming no tag fields)
- `/home/cormac/projects/ledgerkit/ledgerkit/parser.py` (grep + read around `account`/`tag` directive handling, lines ~876-1213, 1378-1489)
- `/home/cormac/projects/ledgerkit/ledgerkit/query/ast.py` (read, for existing node-shape conventions)
- `/home/cormac/projects/hledger` (git log confirming commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tags `1.52.4`/`hledger-1.52.4`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Query.hs` — whole-file greps plus close reads at lines 105-145 (`Query` sum type, `payeeTag`/`noteTag`/`generatedTransactionTag`), 280-330 (`parseQueryTerm`), 482-506 (`parseTag`, `parseDepthSpec*`), 656-683 (`queryIs*` predicates), 860-1024 (`matchesAccount`/`matchesAccountExtra`/`matchesPosting`/`matchesPostingExtra`/`matchesTransaction`/`matchesTransactionExtra`/`matchesDescription`/`matchesTag`/`patternsMatchTags`), 1050-1120 (doctests for `parseQuery`/`parseBooleanQuery`/`parseQueryTerm`/`filterQuery`), 195-227 (`combineQueriesByType`, `parseQueryList`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Utils/Regex.hs` — `reString`/`Regexp` definition (lines ~87-102), already-read docstring/`toRegexCI` (1-38, 138-140, per the existing brief, re-confirmed applicable)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/AccountName.hs` — `parentAccountNames` (referenced via `journalInheritedAccountTags`, not re-quoted since already covered structurally by the existing brief's `accountNameLevel` citation)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Posting.hs` — lines 439-444 (`postingAllTags`/`transactionAllTags`), 467-479 (`postingAddTags`/`postingAddHiddenAndMaybeVisibleTag`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Journal.hs` — lines 505-533 (`journalAccountTags`/`journalInheritedAccountTags`), 625-670 (`journalPostingsAddAccountTags`/`journalPostingsAddCommodityTags`/`journalPostingsKeepAccountTagsOnly`), 131 (import list confirming `Data.List.union`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Transaction.hs` — lines 127-131 (`transactionPayee`/`transactionNote`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Types.hs` — line 442 (`type Tag = (TagName, TagValue)`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Read/Common.hs` — lines 212-247 (`rawOptsToInputOpts`, `auto_posting_tags_` wiring), 370-412 (`journalFinalise` pipeline ordering)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Read/InputOptions.hs` — line 37 (`auto_posting_tags_` field doc), line 60 (default `False`)
- `/home/cormac/projects/hledger/hledger/Hledger/Cli/CliOptions.hs` — line 642 (`autopostingtags` derivation)
- `/home/cormac/projects/hledger/hledger/Hledger/Cli/Commands/Accounts.hs` — line 76 (`matchesAccountExtra` call site)
- `/home/cormac/projects/hledger/hledger/Hledger/Cli/Commands/Tags.hs` — line 62 (`matchesAccountExtra` call site)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Reports/MultiBalanceReport.hs` — line 253 (`matchesAccountExtra` call site, non-inherited variant)
- `/home/cormac/projects/hledger/hledger/hledger.1` — lines 2494-2635 (`.SS Tags` / `.SS Tag propagation`, read in full, not excerpted), 7200-7250 (posting/transaction-oriented-commands prose, already partly cited by the existing brief), 7360-7400 (`.SS acct: query` tail / `.SS tag: query` in full)
- `/home/cormac/projects/hledger/hledger/test/query-tag.test` (read in full)
- `/home/cormac/projects/hledger/hledger/test/tags.test` (read: header + tag-existence/inheritance section, lines 1-219)
- `/home/cormac/projects/hledger/hledger/test/accounts.test` (read in full)
- `/home/cormac/projects/hledger/hledger/test/check-tags.test` (read in full)
- `/home/cormac/projects/hledger/hledger/test/query-expr.test`, `hledger/test/journal/commodity-tags.test`, `hledger/test/csv.test`, `hledger/test/timeclock.test`, `hledger/test/timedot.test`, `hledger/test/forecast.test`, `hledger/test/descriptions.test`, `hledger/test/notes.test` (grepped for `tag:` usages, per §8's table; not read in full — each use is incidental to a different feature under test)

Also referenced, but explicitly **not** relied on for any citation above
(read only to confirm/correct its account of the manual excerpt, per the
lead's specific instruction): `/home/cormac/projects/codecompass/
planning/reference-projects/ledgerkit/reference-experiment/
54-tag-query-semantics-reference-experiment-evaluation.md`.

## Summary of proposed register entries (all `status: proposed`, none executable-verified)

| Proposed ID | Area | Kind | Notes |
|---|---|---|---|
| `LK-COMPAT-QUERY-TAG-001` | query.tag | compatible | bare `tag:NAME` / `tag:NAME=REGEX` name+value infix case-insensitive matching primitive; conditional on `HledgerRegex` subset (already built) |
| `LK-COMPAT-QUERY-TAG-INHERIT-001` | query.tag | compatible | all four propagation rules (§2): account←parent, posting←account, posting←transaction, transaction←postings; **blocked**, not merely pending verification — no tag data model exists in `ledgerkit/models.py`/`parser.py` yet (§9) |
| `LK-COMPAT-QUERY-TAG-COMBINE-001` | query.combinators | compatible | `tag:` terms always AND, never same-prefix-OR, negated or not (§5); the two-unnegated-terms sub-case is **source-only evidence**, flagged as top-priority differential-test fixture, same evidentiary shape as the existing brief's negated-acct gap |
| (extends existing) `LK-EXT-QUERY-001` | query.regex | extension | fold in: tag-name and tag-value regex arguments use the identical `HledgerRegex` boundary already defined for `acct:`/`desc:` — no new dialect work (§7) |
| (open question, no ID proposed) | query.tag / accounts command | — | account-name-level `tag:` matching (§6) uses a narrower, declared-tag-only mechanism, distinct from posting/transaction-level `tag:` — needs a lead scoping decision on which behaviour Ledgerkit's `accounts -q "tag:..."` should mirror before a classification can be proposed |
| (informational, no ID proposed) | query.tag / payee,note | — | `payee:`/`note:` are literally `Tag` nodes under the hood, with a case-sensitive literal-string dispatch trap (§3) — out of Stage C's current scope per `hledger-compatibility.md`, recorded for whoever picks up `payee:`/`note:` next |

None of these proposed entries have been added to `dev-docs/compat-
register/` yet — that is implementation-time work, not this brief's own
output, consistent with `17-query-semantics-brief.md`'s closing note.

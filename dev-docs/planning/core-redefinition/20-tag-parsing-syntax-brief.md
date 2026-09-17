# 20. Tag *parsing* syntax brief (Stage C Phase 4 prerequisite)

Produced by `hledger-researcher`. Scope: the **grammar** by which hledger
1.52.x extracts `name:value` tags from comment text and stores them on
`Transaction`/`Posting`/declared-account data — i.e. everything
`19-tag-query-semantics-brief.md` explicitly declined to cover (`19`'s §0
scopes itself to *matching* tags that already exist; this brief is the
prerequisite parsing/storage layer `19`'s §9 flagged as the actual
blocker). Read `19-tag-query-semantics-brief.md` first — this brief does
not re-derive the four propagation rules, the `payee:`/`note:` AST
sharing, or the same-prefix-OR-vs-AND finding; it cites `19` by section
number wherever those results are load-bearing here (mainly §2, §6, §9).

**Pinned baseline, re-verified this session:** local clone at
`/home/cormac/projects/hledger`, `git log -1 --format='%H'` →
`33fa849e7ae841968bd21c427094c4fb4a4ec38d`; `git tag --points-at HEAD` →
`1.52.4`, `hledger-1.52.4`, `hledger-lib-1.52.4`, `hledger-ui-1.52.4`,
`hledger-web-1.52.4`. Same commit as `17-` and `19-`'s briefs and
`09-compatibility-system.md` §9.1.

**On the environment's pinned binary:** not run, per this role's hard
rule. Everything below is manual/source/test-suite-derived, `status:
proposed` only.

---

## 0. Where the actual extraction function lives (not where `19` looked)

`19-tag-query-semantics-brief.md` read `Query.hs` (tag *matching*) and the
account-tag-inheritance plumbing in `Journal.hs`/`Posting.hs`, but never
opened the file that actually turns raw comment text into `[Tag]` in the
first place. That code lives in `hledger-lib/Hledger/Read/Common.hs`,
found directly via `grep -n "Tag\]" hledger-lib/Hledger/Read/Common.hs`
in this session (not assumed, not carried over from any other brief):

- `commentlinetagsp :: TextParser m [Tag]` (`Common.hs:1433-1456`) — the
  tag-extraction grammar used for **transaction** comments and **account
  directive** comments (both reach it via `transactioncommentp`).
- `transactioncommentp :: TextParser m (Text, [Tag])` (`Common.hs:1485-
  1487`) = `followingcommentpWith commentlinetagsp` — parses a
  transaction's (or account directive's) trailing/follow-on `;` comment,
  returning both the raw joined comment text and its extracted tags.
- `commenttagsanddatesp` / `postingcommentp` (`Common.hs:1538-1600`) — the
  **posting**-specific variant, structurally the same tag grammar but
  additionally special-cases the tag names `date`/`date2` (§3) and
  Ledger-style bracketed dates `[DATE=DATE2]` (out of this brief's scope,
  noted only where it interacts with `date`/`date2`).
- `followingcommentpWith :: (Monoid a, Show a) => TextParser m a ->
  TextParser m (Text, a)` (`Common.hs:1406-1428`) — the shared
  same-line-plus-follow-on-lines comment collector both of the above are
  built on. This is the single most important function for Q2/Q4 below.
- Callers, confirming exactly which three syntactic positions reach this
  code: `accountdirectivep` (`JournalReader.hs:515-544`, calls
  `transactioncommentp` at line 528) and `postingphelper`
  (`JournalReader.hs:968-996`, calls `postingcommentp` at line 984). The
  transaction-header call site is inside `JournalReader.hs`'s
  transaction-parsing function (uses `transactioncommentp` identically to
  the account directive — confirmed by both sharing the same function,
  not by separately reading a third call site).

---

## 1. `followingcommentpWith`: same-line comment and *every* follow-on line are each independently tag-scanned

This directly answers "does hledger extract tags from a follow-on
indented comment line the same way as an inline same-line comment, and do
multiple comment lines each contribute tags or only one?" (the lead's Q2/
Q4), with a precise mechanism, not a guess:

```haskell
followingcommentpWith :: (Monoid a, Show a) => TextParser m a -> TextParser m (Text, a)
followingcommentpWith contentp = do
  skipNonNewlineSpaces
  sameLine <- try headerp *> ((:[]) <$> match' contentp) <|> pure []
  _ <- eolof
  nextLines <- many $
    try (skipNonNewlineSpaces1 *> headerp) *> match' contentp <* eolof
  let sameLine' | null sameLine && not (null nextLines) = [("",mempty)]
                | otherwise = sameLine
      (texts, contents) = unzip $ sameLine' ++ nextLines
      strippedCommentText = T.unlines $ map T.strip texts
      commentContent = mconcat contents
  pure (strippedCommentText, commentContent)
  where headerp = char ';' *> skipNonNewlineSpaces
```

(`Common.hs:1406-1428`, quoted in full — short enough that transcribing it
is more precise than paraphrasing.)

- `contentp` (either `commentlinetagsp` or `commenttagsanddatesp mYear`,
  depending on caller) is invoked **once per qualifying line**: once for
  the optional same-line comment (`sameLine`, gated on `headerp` — a
  literal `;` immediately here, i.e. this is *after* whatever already
  matched the description/account/amount on that same physical line), and
  once per subsequent line that is `skipNonNewlineSpaces1 *> headerp`
  (i.e. **indented** whitespace, then `;`) — `many` means **zero or
  more** such lines, each independently parsed. `mconcat contents`
  (`[Tag]`'s `Monoid` instance is list concatenation) is the union of
  every line's own tag list, in the order the lines appear. **Every
  qualifying comment line contributes tags, not just the first.**
- A `#`-prefixed follow-on line is **not** reachable through this
  function at all — `headerp` requires a literal `;`. This confirms
  Ledgerkit's existing, already-correct behaviour (`hledger-
  compatibility.md`'s Comments table: "Follow-on `#` inside transaction …
  text is NOT captured") extends cleanly to tags: a `#` follow-on line
  can never carry a tag in hledger either, because it is never fed to
  `commentlinetagsp`/`commenttagsanddatesp` in the first place — there is
  no separate "tags aren't extracted from `#` lines" rule to encode; it
  falls out of the same structural fact that already makes `#` lines
  uncaptured for comment *text*.
  - **Manual corroboration**, `hledger.1:1567-1568` ("Lines … will be
    ignored if they begin with a hash (`#`) or a semicolon (`;`)"),
    doesn't itself distinguish `#` vs `;` for tags — the distinction is
    source-only, same evidentiary shape as most of `19`'s findings.
- A column-0 (non-indented) `;` or `#` line is likewise never reachable
  through `followingcommentpWith` — that grammar only fires for
  same-line-after-header or `skipNonNewlineSpaces1`-indented next lines;
  a column-0 comment is consumed by a wholly separate top-level-comment
  path in the journal reader (not read in detail for this brief since it
  is off-path for tags by construction — the same reasoning as the `#`
  case above). This matches Ledgerkit's existing "top-level comment,
  never captured into any field" rule and needs no new carve-out for
  tags.

**Consequence for Ledgerkit's three already-recognised comment forms**
(per `dev-docs/hledger-compatibility.md`'s Comments table and
`knowledge/DOMAIN_RULES.md`'s comment-indentation-rule entry):

| Ledgerkit comment form | Tag-scan per hledger? |
|---|---|
| Inline `;` on transaction header | **Yes** — same-line branch of `transactioncommentp` |
| Inline `;` on posting | **Yes** — same-line branch of `postingcommentp` |
| Follow-on indented `;` inside a transaction (after header, before any posting seen, or after a posting) | **Yes** — `nextLines` branch, using whichever of `commentlinetagsp`/`commenttagsanddatesp` applies to what it's attached to (transaction-level if no posting seen yet; posting-level if attached to the preceding posting) |
| Follow-on indented `#` inside a transaction | **No** — never reaches `followingcommentpWith` at all (structural, not a special-cased exclusion) |
| Top-level `#`/`;` (column 0) | **No** — never reaches `followingcommentpWith` |
| `account NAME ; …` inline comment | **Yes** — same mechanism as the transaction header (`accountdirectivep` calls `transactioncommentp`, `JournalReader.hs:528`) |
| `account NAME` follow-on indented `;` lines | **Yes** — same `nextLines` mechanism; **explicitly confirmed by the manual**, not just inferred from the shared function: `hledger.1:2980-2992` ("Account comments") states "Text following two or more spaces and `;` at the end of an account directive line, **and/or** following `;` on indented lines immediately below it, form comments for that account," with a worked example showing tags on a next-line account comment (`; some tags - type:A, acctnum:12345`, `hledger.1:2991`) |

One nuance worth flagging precisely: Ledgerkit's current `account`
directive handling (`ledgerkit/parser.py:1141-1149`) does **not**
implement the follow-on-comment-line capture at all for `account` — it
sets `in_subdirective = True` and silently consumes indented lines
without parsing them (`_strip_directive_comment` discards the same-line
comment text outright, and there is no code path reading indented lines'
content for tags). Building rule (A)'s substrate (`19`'s §2) requires
extending this specific code, not just adding a new field to `Journal`.

---

## 2. `commentlinetagsp`: the exact grammar, character-by-character

```haskell
commentlinetagsp :: TextParser m [Tag]
commentlinetagsp = do
  tagName <- (last . T.split isSpace) <$> takeWhileP Nothing (\c -> c /= ':' && c /= '\n')
  atColon tagName <|> pure []
  where
    atColon :: Text -> TextParser m [Tag]
    atColon name = char ':' *> do
      if T.null name
        then commentlinetagsp
        else do
          skipNonNewlineSpaces
          val <- tagValue
          let tag = (name, val)
          (tag:) <$> commentlinetagsp
    tagValue :: TextParser m Text
    tagValue = do
      val <- T.strip <$> takeWhileP Nothing (\c -> c /= ',' && c /= '\n')
      _ <- optional $ char ','
      pure val
```

(`Common.hs:1433-1456`, quoted in full — this is the "real parsing
function," precisely the lead's request, not a paraphrase.)

Traced through, term by term (this answers Q1, Q5, and part of Q3):

1. **Name delimiting.** `takeWhileP (c /= ':' && c /= '\n')` consumes
   *everything* up to the first `:` or end-of-line — this can include
   leading prose, other punctuation, even other `,`/`;`-looking
   characters, since none of those stop the scan. The **tag name** is
   then just `last (T.split isSpace <of that consumed text>)` — the final
   whitespace-delimited token immediately preceding the colon. Any text
   before that final token (e.g. `"some comment text, tag1"` → name
   `"tag1"`) is silently discarded as far as tag-extraction goes (it
   remains present in the separately-collected raw comment text, since
   `followingcommentpWith` keeps `texts` independent of `contents`).
   **No leading-whitespace stripping is needed on the name** because, by
   construction, the name is already a run with no internal whitespace —
   there is no equivalent of the value's explicit `T.strip`.
2. **Legal tag-name characters, precisely.** The grammar imposes **no**
   character-class restriction beyond "not `:`, not `\n`, not internal
   whitespace" (whitespace is excluded only because the name is defined
   as the *last space-delimited token*, not because the character-scan
   itself forbids it). Concretely: digits, punctuation (`-`, `_`, `.`,
   `/`, even another `:`-free run of arbitrary symbols), and non-ASCII
   text are all accepted as tag names — the manual's prose ("Tags are a
   single word or hyphenated word," `hledger.1:2500-2501`) is a
   **usage convention, not the enforced grammar** — this is a real gap
   between documented intent and actual parser leniency, worth recording
   plainly rather than assuming the manual's plain-English description is
   the grammar.
3. **Colon must immediately follow the name, with no space** — this part
   of the manual's prose *is* enforced structurally: the name is
   whatever non-space run immediately precedes the `:` that
   `takeWhileP`'s scan stopped at; if there is a space between the
   candidate word and the colon (e.g. `"foo : bar"`), the character scan
   for the name-candidate text still stops at the same `:`, but
   `T.split isSpace` on the consumed text `"foo "` yields `["foo", ""]`
   (trailing empty string after the space) — `last` of that is `""`, the
   empty string — which hits the `T.null name → commentlinetagsp`
   (recurse, i.e. this "tag" is silently discarded as not-a-tag and the
   scan continues after the colon) branch, **not** a tag named `"foo"`.
   So `"; foo : bar"` produces **zero tags** from that colon (the `:` is
   consumed and parsing recurses looking for a *further* colon in `"
   bar"`, finding none, so it terminates with `[]`) — a space before the
   colon silently voids that would-be tag entirely, it does not merely
   trim to an empty name.
4. **Bare tag, no value.** If the name is non-empty and immediately
   followed by `:`, then (whatever follows, even nothing) `tagValue`
   still runs: `takeWhileP (c /= ',' && c\= '\n')` against zero remaining
   characters yields `""`, `T.strip ""` is `""` — so `("some-tag", "")`
   is a completely legal tag with an explicit empty-string value. This is
   directly the manual's own first example (`hledger.1:2504-2509`,
   `; some-tag:` with nothing after the colon) — **confirmed both by
   manual and grammar, no ambiguity here.**
5. **Value termination — no escaping mechanism, comma is a hard
   separator.** `tagValue` stops at the first `,` or `\n`, full stop.
   There is no backslash-escape, no quoting convention, nothing in
   `Common.hs`, `Regex.hs`, or the manual's Tags section that lets a
   value contain a literal comma — the manual states this as a
   documented **limitation**, not merely an omission: `hledger.1:2518-
   2519`, "Multiple tags can be separated by comma. Tag values can't
   contain commas." A comma-containing value is genuinely
   **unrepresentable** via this syntax; the text after the comma is
   simply parsed as the start of a new (possibly tag-less) segment.
   **A colon inside a value is fine** — `tagValue`'s scan does not stop
   at `:` at all, only at `,`/`\n` — so `"; url: http://example.com,
   other: x"` produces `[("url", "http://example.com"), ("other", "x")]`,
   the colon in the URL is not mistaken for a second tag delimiter. This
   is a genuinely useful, non-obvious edge case not spelled out anywhere
   in the manual's prose (which only ever shows comma-free, colon-free
   example values) — found only by reading the grammar.
6. **Whitespace trimming on the value.** `skipNonNewlineSpaces` runs
   right after the colon is consumed, before `tagValue` starts scanning —
   so leading value-whitespace is skipped at the parser-position level.
   `tagValue` then does `T.strip` on top of that, trimming any
   *trailing* whitespace before the comma/newline too (e.g. `"tag1:
   value1  , tag2:value2"` → `("tag1", "value1")`, trailing double-space
   before the comma removed). Both leading and trailing value whitespace
   are trimmed; there is no whitespace-preservation mode.
7. **Multiple tags per line, comma-separated; a name can repeat with
   different values (list semantics, not dict semantics).** After a
   value and its optional trailing comma are consumed, `commentlinetagsp`
   recurses on the remaining text of the *same line* to look for a
   further colon. The manual's own worked example demonstrates a
   **repeated tag name with two different values being genuinely both
   kept**: `hledger.1:2525-2529`, `; tag1:value 1, tag1:value 2` is
   captioned "A tag can have multiple values" — i.e. the result is a
   **list** `[("tag1","value 1"), ("tag1","value 2")]`, not a dict that
   collapses to one value per name. **This is decisive, load-bearing
   evidence for the data-model proposal in §7 below: `Posting.tags`/
   `Transaction.tags` must be an ordered `list[tuple[str, str]]`, never a
   `dict[str, str]`,** independent of the separate posting/account-tag
   union-by-full-pair behaviour `19`'s §2 already found — this manual
   example is a single-comment-line case with no inheritance involved at
   all, so it's a stronger, simpler piece of evidence for the same
   conclusion.
8. Doctest confirmation, directly from the source file itself
   (`Common.hs:1474-1478`):
   ```
   >>> parseTags "; name1: val1, name2:all this is value2"
   Right [("name1","val1"),("name2","all this is value2")]
   ```
   demonstrating a value containing internal spaces (`"all this is
   value2"`) is preserved verbatim (only leading/trailing trimmed, not
   internal whitespace collapsed).

**Manual's own summary of this grammar** (`hledger.1:2494-2530`, quoted
above, plus 2500-2501: "Tags are a single word or hyphenated word,
immediately followed by a full colon, written within a comment") is
consistent with everything above **except** point 2's leniency gap, which
is source-only and should be recorded as such, not attributed to the
manual.

---

## 3. `date:`/`date2:` — a real, source-confirmed second syntax path to a per-*posting* date, distinct from `Transaction.date2`

This is the lead's most concrete open question (Q3), and the answer is
precise and somewhat different from what "just another tag" would
suggest:

### 3.1 Only the posting-level comment parser special-cases these names

`commentlinetagsp` (transaction/account-directive tag grammar, §2 above)
has **no** date special-casing at all — `"date"`/`"date2"` are ordinary
tag names there, stored as plain `(name, value)` string pairs with zero
side effects. Only the **posting**-specific `commenttagsanddatesp` (used
exclusively via `postingcommentp`, `Common.hs:1538-1546`, called only
from `postingphelper`, `JournalReader.hs:984`) branches on the name:

```haskell
atColon name = char ':' *> do
  skipNonNewlineSpaces
  (tags, dateTags) <- case name of
    ""      -> pure ([], [])
    "date"  -> dateValue name
    "date2" -> dateValue name
    _       -> tagValue name
  ...

dateValue name = do
  (txt, (date, dateTags)) <- match' $ do
    date <- datep' mYear
    dateTags <- readUpTo ','
    pure (date, dateTags)
  let val = T.strip txt
  pure ( [(name, val)], (name, date) : dateTags )
```

(`Common.hs:1572-1591`, quoted). Two things fall out of this precisely:

- **Both effects happen simultaneously, not one instead of the other.**
  A `date:`/`date2:` tag on a posting is stored **both** as an ordinary
  string-valued tag entry in `ptags` (`[(name, val)]`, `val` being the
  original text, e.g. `"1/2"`) **and** as a parsed `Day` in a
  separate `[DateTag]` accumulator, which `postingcommentp` then
  extracts into `mdate`/`mdate2` (`Common.hs:1543-1545`:
  `mdate = snd <$> find ((=="date").fst) dateTags`) and assigns directly
  to the `Posting`'s own `pdate`/`pdate2` fields
  (`JournalReader.hs:986-987`: `pdate=mdate, pdate2=mdate2`). So the tag
  is not "consumed" by the date-override mechanism — it remains visible
  to `tag:date=...`/`tag:date2=...` queries too (per `19`'s §1
  matching-primitive contract, unaffected by this brief).
- **Value must parse as a valid Simple Date, using `datep'` with the
  transaction's year as the fallback default year** — `dateValue` calls
  `datep' mYear` (`Common.hs:1585`), where `mYear` is
  `mTransactionYear` threaded in from `postingphelper`
  (`JournalReader.hs:969, 984`), i.e. **the transaction header's own
  year**, not "current calendar year" or any other default. There is
  **no fallback branch to plain-string tag storage if the date fails to
  parse** — `dateValue` is not wrapped in `try (...) <|> tagValue name`
  anywhere in this function; a value that isn't a parseable Simple Date
  under a `date`/`date2` name is a hard parse error for the whole
  posting/journal, not a silent downgrade to an ordinary tag. This
  matches the docstring's own explicit statement two lines above the
  doctest examples: *"We throw parse errors on invalid dates."*
  (`Common.hs:1519-1520`).
- **Trailing text after the date is ignored, not an error** — `readUpTo
  ','` after `datep'` just consumes (and discards, for date-parsing
  purposes) anything up to the next comma, while the *stored tag value*
  keeps the whole matched text verbatim including that trailing part.
  Doctest: `"; date:3/4=5/6"` → tag `("date","3/4=5/6")`, `mdate = Just
  2000-03-04`, `mdate2 = Nothing` (`Common.hs:1534-1536`) — the `=5/6`
  suffix is **not** interpreted as setting `date2` from a `date:` tag;
  it is simply inert trailing text kept only in the string value. (A
  *separate*, unrelated bracketed syntax, `[DATE=DATE2]`, does set both
  from one token — out of this brief's scope, flagged only so it isn't
  confused with this trailing-text behaviour.)

### 3.2 Precedence: posting's own date always wins; transaction's date is untouched

The override is resolved by two accessor functions, not by mutating the
transaction:

```haskell
postingDate :: Posting -> Day
postingDate p = fromMaybe nulldate $ asum [ pdate p, tdate <$> ptransaction p ]

postingDate2 :: Posting -> Day
postingDate2 p = fromMaybe nulldate $ asum
  [ pdate2 p, tdate2 =<< ptransaction p, pdate p, tdate <$> ptransaction p ]
```

(`Posting.hs:402-416`, quoted in full — doc-commented in source as "Get a
posting's (primary) date - it's own primary date if specified, otherwise
the parent transaction's primary date"). Precisely:

- `Transaction.tdate`/`tdate2` (Ledgerkit's `Transaction.date`/`date2`)
  are **never mutated** by a posting's `date:`/`date2:` tag — the
  override is purely a per-posting *effective date* computed on read,
  via `asum` (first-`Just`-wins) over `[own value, parent's value]`.
- `postingDate2`'s fallback chain is longer than the naive "own date2, or
  parent's date2" — it falls through **four** levels in order: this
  posting's own `pdate2` → the transaction's `tdate2` → this posting's
  own `pdate` (primary!) → the transaction's `tdate` (primary!). So a
  posting with a `date:` tag but no `date2:` tag, on a transaction with
  no `=DATE2` suffix at all, gets `postingDate2 == postingDate ==` its
  own `date:` override — the posting's *primary* override also becomes
  its effective *secondary* date if nothing more specific is set for
  date2 anywhere in the chain. This four-level fallback is easy to miss
  reading only the one-line doc-comment; it's only visible in the actual
  function body.
- This machinery is used wherever hledger needs "the effective date of
  this posting" for anything date-ordered — the manual's own worked
  `register` example (`hledger.1:1639-1665`, "Posting dates") shows
  exactly this: a `date:6/1` tag on one posting of a `2015/5/30`
  transaction makes that posting (and only that posting) appear under
  `2015-06-01` in `register` output, while its sibling posting (no tag)
  still appears under the transaction's own `2015-05-30`.

### 3.3 Direct implication for Ledgerkit's existing `Transaction.date2`

Ledgerkit's `Transaction.date2` (parsed from the `=DATE2` header suffix,
per `dev-docs/hledger-compatibility.md`'s Transactions table) is real and
already implemented, but it is **transaction-scoped only**. hledger's
`date:`/`date2:` posting tags are a **second, independent, posting-scoped
override path to conceptually the same "auxiliary date" idea**, not an
alternative spelling of the same header-level field — a journal can
legally have a transaction-level `date2` *and* per-posting `date:`/
`date2:` tags simultaneously, with the posting-level ones taking
precedence for that one posting's effective date (per §3.2's `asum`
chain) while leaving the transaction's own `tdate`/`tdate2` fields
unmodified for every other posting. Ledgerkit's data model needs a
**distinct field** for this — proposed in §7 as `Posting.date_override`/
`Posting.date2_override`, deliberately not reusing the `date2` name to
avoid implying it's the same mechanism as `Transaction.date2`.

### 3.4 Test-suite confirmation

- `Common.hs`'s own module doctests (`1522-1536`, quoted piecemeal
  above) are the most precise, executable-as-documentation evidence —
  they are literally run as part of hledger's own test suite
  (`doctest`/`hledger-lib`'s test target), not just illustrative prose.
- `hledger/test/aregister.test:67,71` uses `; date:2021-01-01` on two
  postings of the same transaction as an incidental fixture for
  unrelated `aregister`-date-window testing — confirms the syntax is
  exercised in a real command-level test, not merely a unit doctest, but
  adds no new semantic information beyond §3.1-§3.2.
- `hledger/test/csv.test:1128,1135,1144` shows `date:` tags surviving
  through CSV-import-generated postings — out of Ledgerkit's scope
  (no CSV import), not relied on for any claim here.
- `hledger/test/check-tags.test` test 6 (`hledger/test/check-tags.
  test:43-64`) is the fixture already partly cited by `19`'s §8 for
  `builtinTags`, but read again here specifically for its transaction-
  level placement: the fixture writes `; date:` and `; date2:` as
  **indented lines directly under a transaction header with no posting
  lines at all** (`2024-01-01\n  ; date:\n  ; date2:\n  ; type:\n ...`).
  Per Ledgerkit's own existing follow-on-comment rule (`knowledge/
  DOMAIN_RULES.md`'s comment-indentation-rule entry: "Appended … to
  `Transaction.inline_comment` if no posting has been seen yet"), these
  lines attach to the **transaction**, not to any posting — and
  correspondingly, per §3.1 above, `date:`/`date2:` in that position get
  **no** date-override effect at all (they're parsed by the
  transaction-level `commentlinetagsp`, not `commenttagsanddatesp`) —
  they are ordinary tags there. `builtinTags` still pre-declares `date`/
  `date2` globally (not scoped to "only when in a posting comment")
  precisely because the same literal tag name is legitimately writable,
  with no override effect, at the transaction or account level too —
  confirmed directly by this fixture, not inferred.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for the `date:`/`date2:` posting-tag-override mechanism as a *target
contract* — bare-name-detection, `datep`-equivalent value parsing with
transaction-year fallback, trailing-text-after-date tolerance, and the
`asum`-style precedence chain in §3.2 — `status: proposed`, **blocked on
the same substrate gap `19`'s §9 already reported**: Ledgerkit has no
posting-level date-override field at all yet (confirmed by grepping
`ledgerkit/models.py` — `Posting` has `account`, `amount`,
`balance_assertion`, `cost_raw`, `source_line`, `inferred`,
`inline_comment` only, no date field of any kind).

---

## 4. The `tag` directive: purely advisory, zero inline-parsing enforcement — confirmed both by source and by a direct test

Answering Q6 decisively, not tentatively:

- `journalCheckTags :: Journal -> Either String ()` (`hledger-lib/
  Hledger/Data/JournalChecks.hs:190-224`) is the **only** place
  `jdeclaredtags` (populated by the `tag` directive,
  `JournalReader.hs:604`) is ever consulted against actually-used tags —
  and it is invoked only by the `check tags` subcommand / `-s`'s
  aggregate check, never by the parser itself. `tagdirectivep`
  (`JournalReader.hs:752-772`) does nothing but append to
  `jdeclaredtags`; there is no code path from there back into
  `commentlinetagsp`/`commenttagsanddatesp` (§1-§2's extraction
  grammar) that could reject or alter an undeclared tag at parse time.
- Direct test confirmation: `hledger/test/check-tags.test` test 3
  ("it detects an undeclared account tag") uses **no** `tag` directive at
  all and successfully **parses** `account a ; atag:` — the failure only
  surfaces later, from the explicit `check tags` command
  (`>2 /tag "atag" has not been declared/`), not from parsing the
  `account`/tag line itself. Tests 1, 6, 7 all confirm undeclared and
  even *reserved-name* tags parse and run `hledger check` (the
  non-`tags`-specific basic check) with zero complaint.
- `builtinTags` (`JournalChecks.hs:228-244`) — the reserved-name list the
  lead asked about — is used for exactly one purpose: pre-satisfying
  `journalCheckTags`'s "has this tag name been declared" test, so that
  `check tags` doesn't require users to redundantly `tag date` /
  `tag type` etc. themselves. It has **no** other runtime effect; in
  particular, `date`/`date2`'s actual override behaviour (§3) fires
  unconditionally whenever a posting comment writes that literal name,
  **regardless of whether a `tag date` directive exists anywhere in the
  file or whether `check tags` is ever run.** The reserved-name list and
  the override mechanism are two unrelated `builtinTags`-adjacent facts
  that happen to share a name, not one validated by the other:
  ```haskell
  builtinTags = [
     "date"                   -- overrides a posting's date
    ,"date2"                  -- overrides a posting's secondary date
    ,"type"                   -- declares an account's type
    ,"t","assert","retain","start"
    ] <> ts <> map toVisibleTagName ts
    where ts = [generatedTransactionTagName, modifiedTransactionTagName,
                generatedPostingTagName, costPostingTagName]
  ```
  (`JournalChecks.hs:228-244`, quoted; full reserved set per
  `check-tags.test:69-85`: `date`, `date2`, `type`, `t`, `assert`,
  `retain`, `start`, `generated-transaction`, `modified-transaction`,
  `generated-posting`, `cost-posting`, `conversion-posting`, plus each of
  the last four's `_`-prefixed "hidden" form.)

**Confirms Ledgerkit's existing documentation is already accurate on this
point** (`hledger-compatibility.md`: "`tag` directive … Used by `check
tags` — deferred until inline tag-comment parsing is implemented") — no
correction needed there, just confirmation with a direct citation trail.

**Proposed classification:** `compatible` (`relationship: equivalent`)
for "the `tag` directive is advisory-only, with zero effect on inline-tag
parsing/acceptance," `status: proposed` — this one is actually
**exercisable today** without any new data model (Ledgerkit's `tag`
directive parsing already exists and already has no enforcement
behaviour; a `compat-differential-tester` fixture could confirm this
row in isolation before Phase 4's larger tag-model work lands, if the
lead wants an early, low-risk verification win).

---

## 5. Interaction with Ledgerkit's existing comment-parsing implementation, read directly

Read per the lead's instruction, before proposing anything: `dev-docs/
hledger-compatibility.md`'s Comments section (already summarised in §1's
table above) and `knowledge/DOMAIN_RULES.md`'s "Comment indentation rule:
column-0 vs. indented" entry, plus the actual parser code:

- `ledgerkit/parser.py:1127-1149` (`account` directive handling) —
  confirmed by direct read: `_strip_directive_comment` **discards** the
  comment text outright (used only to isolate the account name), and
  `in_subdirective = True` causes indented follow-on lines to be
  **silently consumed without being parsed for content at all**. This
  means today there is no code path capturing even the *text* of an
  account directive's follow-on comment lines, let alone tags from them
  — building §1's table's "account NAME follow-on indented `;` lines →
  Yes" row requires extending this specific block, not just adding a
  `Journal.declared_account_tags` field elsewhere.
- `ledgerkit/parser.py`'s transaction/posting follow-on-comment handling
  (around the block documented at `parser.py:955-984`, per this
  session's earlier grep) already correctly implements
  `followingcommentpWith`'s same-line-plus-indented-next-lines
  concatenation shape for **comment text** (newline-joined,
  first-posting-vs-transaction-attachment logic already matches §1's
  table) — this is good news: **the text-collection substrate Phase 4
  needs already exists and needs no change**; only a tag-*extraction*
  pass over that already-assembled text is new work (§2's grammar,
  applied per §6 below).
- Confirmed: none of Ledgerkit's four comment forms need to be
  **excluded** from tag-scanning beyond what's already true of them for
  comment-text capture — the mapping in §1's table is exactly
  "tag-scanned wherever text is already captured as `inline_comment`,
  never scanned wherever it isn't" (the `#`-line and column-0 cases). No
  hledger-side surprise here: tags are a pure post-processing step over
  material Ledgerkit's parser already collects, not a separate scanning
  pass over the raw file.

---

## 6. A genuinely useful implementation-efficiency observation (not a compatibility claim)

Because `tagValue`/`commentlinetagsp` treat `\n` as a hard terminator
identically to how they treat the end of each individual line during
`followingcommentpWith`'s per-line invocation (§1), re-running the
**identical** tag-extraction algorithm once over an **already-assembled,
newline-joined** `inline_comment` string (exactly the string Ledgerkit's
parser already produces via its own same-line + follow-on-line joining,
per §5) produces **exactly the same result** as hledger's actual
line-by-line invocation — because a newline inside the joined string is
just as hard a stop for `tagValue`'s `c /= '\n'` scan as the line
boundary is under `followingcommentpWith`'s original per-line calling
convention. Concretely: comma-continuation never crosses a line boundary
either way (a trailing comma on one line does not continue into the tags
of the next line, in either hledger's line-by-line approach or a
single-pass re-scan of the joined text), so there is no observable
difference between:

- (a) extracting tags line-by-line as each contributing comment line is
  parsed (mirroring hledger's own call structure exactly), or
- (b) extracting tags once, in a single pass, over the final joined
  `inline_comment`/`Transaction.comment`-equivalent string, after all
  comment-text collection is already done.

This is **not** a compatibility finding (both are equally correct against
hledger's actual observable behaviour) — it's a genuine implementation
simplification worth passing to whoever writes the code: approach (b)
lets tag extraction be a single, independently-testable pure function
(`str -> list[tuple[str, str]]`) applied after the fact to whatever
`inline_comment` value the existing parser already produces, rather than
requiring new hooks inside the line-by-line comment-collection loop
itself. Flagged as a **proposal**, not a prescription — the lead/
implementer may have other reasons to prefer (a).

---

## 7. Proposed data-model design (for the lead to accept/modify — not a decision)

Read `ledgerkit/models.py` in full before drafting this, matching its
existing dataclass conventions (plain `@dataclass`, `Optional[X]`/
`X | None` mixed usage as already present, `field(default_factory=...)`
for mutable defaults, `repr=False`/`compare=False` used selectively on
fields that are cosmetic or would otherwise break equality-based tests —
see `Posting.inline_comment`, `Transaction.source_span`/`raw_text`/
`inline_comment` for precedent).

### 7.1 `Posting`

```python
@dataclass
class Posting:
    account: str
    amount: Amount | None = None
    balance_assertion: BalanceAssertion | None = field(default=None)
    cost_raw: Optional[str] = None
    source_line: int | None = field(default=None, repr=False)
    inferred: bool = field(default=False, repr=False)
    inline_comment: str | None = field(default=None, repr=False, compare=False)

    # --- new, this brief's proposal ---
    tags: list[tuple[str, str]] = field(default_factory=list)
    date_override: datetime.date | None = None
    date2_override: datetime.date | None = None
```

- `tags`: **exactly** what §2's grammar extracts from this posting's own
  `inline_comment` text (same-line + its own follow-on lines only) — a
  plain ordered list of `(name, value)` string pairs, **not** a dict
  (§2 point 7's manual-sourced evidence is decisive on this: a name can
  legitimately repeat with different values within a single comment,
  before any inheritance is even considered). Deliberately does **not**
  include inherited account/transaction tags (`19`'s §2, rules A-C) —
  see the open question below on where inheritance should live.
- `date_override`/`date2_override`: populated only when this posting's
  own comment contains a `date:`/`date2:` tag whose value parses as a
  Simple Date (reusing whatever date-parsing Ledgerkit's transaction
  header already uses for its own `=DATE2` suffix, per §3.1's
  requirement that the value be a real Simple Date, with the parent
  transaction's year as fallback default — mirroring hledger's own
  `mTransactionYear` threading, `JournalReader.hs:969,984`). **Named
  deliberately differently from `Transaction.date2`** (§3.3) to avoid
  implying these are the same mechanism — they are two independent
  syntax paths to a conceptually similar "auxiliary date" idea, and a
  journal can use both simultaneously on different scopes.
- **Open design question, explicitly for the lead, not resolved here:**
  hledger computes `postingDate`/`postingDate2` (§3.2's `asum` chain) via
  a live back-reference from `Posting` to its parent `Transaction`
  (`ptransaction :: Maybe Transaction`, mirrored in `19`'s §2/§4
  citations of `postingAllTags`/`ptransaction`). Ledgerkit's `Posting`
  today has **no** such back-reference — every existing report/query
  function instead iterates `journal.transactions[i].postings[j]` and
  has both objects in hand as a pair by construction. Two structurally
  different ways to reach hledger's same observable "effective posting
  date" contract:
  (i) add a `Posting.transaction` back-reference field (closer to
  hledger's own shape, but a real, first-time change to `Posting`'s
  relationship to `Transaction` — likely wants its own
  `knowledge/DECISIONS.md` entry given the "circular reference in a
  dataclass" tradeoff), or
  (ii) leave `Posting` reference-free and add a free function/method
  taking both objects, e.g. `effective_date(txn: Transaction, posting:
  Posting) -> date` / `effective_date2(...)`, computed the same way
  `19`'s §4 already recommended for tag inheritance (a pure function
  over a pair, not a stored/mutated field) — this keeps `Posting`
  equality-comparable and independent of its container, consistent with
  how `Posting.inline_comment` is already marked `compare=False` rather
  than `Posting` needing a parent pointer for anything else today.
  This brief's author has no strong opinion on which the lead should
  pick; (ii) is more consistent with `Posting`'s current design (no
  existing back-references anywhere in `models.py`), but (i) is more
  directly faithful to hledger's own shape if a future `19`-style
  `tag:` evaluator ends up wanting `postingAllTags`-equivalent behaviour
  cheaply from the `Posting` object alone.

### 7.2 `Transaction`

```python
@dataclass
class Transaction:
    date: datetime.date
    description: str
    date2: Optional[datetime.date] = None
    postings: list[Posting] = field(default_factory=list)
    cleared: bool = False
    pending: bool = False
    code: str = ""
    comment: str = ""
    source_line: int | None = field(default=None, repr=False)
    source_span: SourceSpan | None = field(default=None, repr=False, compare=False)
    raw_text: str | None = field(default=None, repr=False, compare=False)
    inline_comment: str | None = field(default=None, repr=False, compare=False)

    # --- new, this brief's proposal ---
    tags: list[tuple[str, str]] = field(default_factory=list)
```

- Deliberately **no** `date_override`/`date2_override`-equivalent fields
  here: §3.1 established that `date:`/`date2:` tags have **no**
  date-overriding effect at the transaction level at all (they are
  ordinary tags there, per `commentlinetagsp`'s lack of date
  special-casing and `check-tags.test`'s test 6 fixture, §3.4). Adding
  such fields to `Transaction` would be actively wrong, not merely
  unnecessary — flagged explicitly so nobody "symmetrises" this by
  analogy with `Posting` later without re-checking this brief.
- `tags` extracted from `Transaction.inline_comment` the same way as
  `Posting.tags`, using `commentlinetagsp`'s grammar (§2) — the
  transaction-level variant, no date special-casing, applied per §6's
  proposed single-pass-over-joined-text approach.

### 7.3 `Journal` — account-directive tag substrate for rule (A)

```python
@dataclass
class Journal:
    ...
    declared_accounts: list[str] = field(default_factory=list)
    # --- new, this brief's proposal ---
    declared_account_tags: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
```

- Keyed by the **exact** account name as declared (mirroring hledger's
  `jdeclaredaccounttags :: M.Map AccountName [Tag]`,
  `journalAccountTags`, `Journal.hs:520-521` — cited already in `19`'s
  §2) — **directly-declared tags only**, no inheritance folded in at
  storage time. A separate helper (proposed, not yet named formally to
  avoid pre-empting `19`'s future `tag:`-implementation phase's own
  naming preferences) would compute the inherited union up the
  colon-hierarchy on demand, mirroring `journalInheritedAccountTags`
  (`Journal.hs:524-529`) — full-pair (`(name, value)`) de-duplication,
  **not** name-only de-duplication, per `19`'s §2 and this brief's §2
  point 7 (both independently point to the same "list, not dict, and
  dedupe by whole pair only" conclusion).
- Requires extending `ledgerkit/parser.py:1141-1149`'s `account`
  directive handling to (a) stop discarding the inline comment text
  outright, and (b) actually parse the indented follow-on lines
  currently swallowed by `in_subdirective` — concretely, apply the same
  §1/§6 comment-collection-then-tag-extraction approach used for
  transactions/postings, rather than `account`'s current
  comment-stripping shortcut. This is real new parsing work, not a
  bolt-on field.

### 7.4 What this brief deliberately does **not** propose

- No tag-inheritance computation (`19`'s §2 rules A-D) — that's the
  follow-on `tag:`-query-implementation phase's job, once this parsing/
  storage layer exists; this brief only proposes where the *directly
  written* tags live.
- No decision on mutate-at-load-time (hledger's own
  `journalPostingsAddAccountTags`-style approach, folding inherited tags
  into `ptags` in place) vs. compute-on-demand (a pure function over a
  `Journal`+`Posting`/`Transaction` pair). §7.1's open question flags the
  closest analogue of this same tension for dates; the same tension
  applies to tags, and this brief takes no position beyond noting that
  `19`'s §4 already recommended "structurally different, functionally
  equivalent" is an acceptable implementation choice.

---

## 8. Files consulted (absolute paths, this session)

- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/19-tag-query-semantics-brief.md` (read in full, cited throughout)
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/03-agent-led-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/09-compatibility-system.md`
- `/home/cormac/projects/ledgerkit/dev-docs/planning/core-redefinition/10-source-assisted-development.md`
- `/home/cormac/projects/ledgerkit/dev-docs/hledger-compatibility.md`
- `/home/cormac/projects/ledgerkit/knowledge/DOMAIN_RULES.md` (read in full; comment-indentation-rule entry specifically cited)
- `/home/cormac/projects/ledgerkit/ledgerkit/models.py` (read in full, styling conventions and current field inventory both confirmed by direct read, not memory)
- `/home/cormac/projects/ledgerkit/ledgerkit/parser.py` — lines 1127-1149 (`account` directive handling, read closely), ~955-1213 (follow-on comment handling and `tag` directive, grepped/read for context)
- `/home/cormac/projects/hledger` (git log/tag confirming commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tag `1.52.4`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Read/Common.hs` — lines 1400-1620 (`followingcommentpWith`, `commentlinetagsp`, `transactioncommentp`, `postingcommentp`, `commenttagsanddatesp`, `bracketeddatetagsp` intro), 575-585 (`datep`/`datep'` location)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Read/JournalReader.hs` — lines 515-589 (`accountdirectivep`, `parseAccountTypeCode`, `addAccountDeclaration`), 940-999 (`postingsp`, `postingp`, `postingphelper`), 604 (`tagdirectivep`'s `jdeclaredtags` update), 752-772 (`tagdirectivep`/`endtagdirectivep`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Posting.hs` — lines 395-479 (`postingDate`/`postingDate2`/`postingDateOrDate2`, `postingAllTags`/`transactionAllTags` re-confirmed, `postingAddTags`, `postingAddHiddenAndMaybeVisibleTag`)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/Journal.hs` — lines 500-533 (`journalAccountTags`/`journalInheritedAccountTags`), 625-669 (`journalPostingsAddAccountTags`/`journalPostingsAddCommodityTags`/`journalPostingsKeepAccountTagsOnly`, doc-comment "If a tag already exists on the posting, it is not changed" re-checked against `postingAddTags`'s actual full-pair-only dedup — confirmed still a real prose/behaviour gap, matching `19`'s §2 finding, not a new one)
- `/home/cormac/projects/hledger/hledger-lib/Hledger/Data/JournalChecks.hs` — lines 180-244 (`journalCheckTags`, `builtinTags`, in full)
- `/home/cormac/projects/hledger/hledger/hledger.1` — lines 1566-1665 (`.SS Comments`, `.SS Transactions`, `.SS Dates`/`.SS Simple dates`, `.SS Posting dates`, in full), 2494-2635 (`.SS Tags`/`.SS Tag propagation`, re-read in full per this brief's own scope, not just carried over from `19`), 2980-3018 (`.SS Account comments`, `.SS Account tags`, `.SS Account error checking` opening, in full)
- `/home/cormac/projects/hledger/hledger/test/check-tags.test` (read in full)
- `/home/cormac/projects/hledger/hledger/test/tags.test` (lines 1-120, re-read for this brief's own override-evidence search — confirmed no direct test of the posting-tag/account-tag same-name-different-value case, matching `19`'s §2 finding, not a new gap)
- `/home/cormac/projects/hledger/hledger/test/aregister.test` (grepped, lines 67/71/115, `date:` tag usage confirmed incidental)
- `/home/cormac/projects/hledger/hledger/test/add.test`, `hledger/test/forecast.test`, `hledger/test/payees.test`, `hledger/test/prices.test`, `hledger/test/query-expr.test`, `hledger/test/rewrite.test`, `hledger/test/csv.test` (grepped only, for `date:`-tag and general tag usages; not read in full — each incidental to a different feature, per the grep output table in this session)

---

## 9. Directly-translated-material assessment

Per `10-source-assisted-development.md` §10.3, using the same three-tier
framework `17-` and `19-`'s briefs applied:

- **`followingcommentpWith`/`commentlinetagsp`/`commenttagsanddatesp`
  read in full and quoted verbatim above** — this is closer to the line
  than anything in `17-`/`19-`'s briefs, and is called out explicitly
  here rather than silently folded into "source inspection": these are
  genuinely small, dense, `Text`/parser-combinator functions (a dozen
  lines each), and this brief's §1-§2 **quote them in full**, not just
  cite line ranges, because their exact recursive shape (scan-to-colon →
  last-space-delimited-token → recurse-on-comma) is precisely what a
  literal Python port would reproduce if the implementer isn't careful.
  **Reading them to understand the algorithm is still "source
  inspection"/"algorithm understanding"** under §10.3's first two
  categories — no code-comment or `THIRD-PARTY-NOTICES.md` requirement
  is triggered by this brief's own act of reading and quoting them for
  *research* purposes (§10.3's recording requirement for those two
  categories is "cite in `evidence:`," which this brief's file list does).
- **The real risk sits with whoever implements, not with this brief**:
  if Ledgerkit's Python tag-extraction function ends up as a recursive
  character-by-character re-implementation matching this exact shape
  (recurse-on-comma, `str.split()`-and-take-last for the name, a
  `char == ':'`-driven state machine mirroring `atColon`'s branching)
  **rather than** an independently-designed regex or iterative
  comma-split (the more natural Python idiom, and the one `CLAUDE.md`'s
  own Regex Documentation Rule anticipates for this codebase), that
  would cross from "algorithm understanding" into **"adapted
  implementation"** (§10.3's third tier — record in `evidence:`/
  `implementation:`, optionally `knowledge/DECISIONS.md`) at minimum,
  and the lead should specifically re-check §10.3's fourth tier
  ("directly translated") before merging **only if** the resulting
  Python function's control flow is close enough to `commentlinetagsp`'s
  literal structure that a reader could reasonably call it a translation
  of *that function's expression* rather than of the general idea "scan
  for name, colon, value, comma-separated, recurse." This brief takes no
  position on which the implementer will produce — flagged here
  precisely because, per this role's mandate, that determination and its
  recording (code comment + `THIRD-PARTY-NOTICES.md` entry +
  `directly_translated: true`, if it applies) is **the lead's
  responsibility to execute, not something for this brief to pre-judge
  or skip past silently.**
- **`postingDate`/`postingDate2`'s `asum`-over-a-list precedence chain**
  (§3.2) is a similarly small, quotable function. The same reasoning
  applies: reading and citing it here is source inspection; a Python
  reimplementation as an explicit `if/elif` chain or a differently-shaped
  `next((x for x in [...] if x is not None), default)` one-liner would
  be an independent expression of the same four-level precedence *idea*,
  not a translation of Haskell's `Maybe`/`asum` idiom specifically — this
  brief's assessment is that this one is unlikely to cross into
  "directly translated," but is flagged for the same reason as above:
  worth the lead's explicit re-check once the actual Python shape exists,
  not asserted safe in advance.
- **Nothing else in this brief rises to a directly-translated-material
  concern** — the account/journal-tag-substrate wiring (§7.3),
  `builtinTags`'s literal string list (§4 — a bare data list of reserved
  names, not copyrightable expression in any meaningful sense, akin to a
  fact/list rather than authored text), and the data-model field
  proposals (§7) are all Ledgerkit-native design choices informed by
  hledger's shape, squarely "adapted implementation" or plain
  independent design, not translation.
- No hledger test fixtures are proposed for direct verbatim porting in
  this brief (unlike `19`'s §8/closing note, which flagged that risk for
  its own scope) — if the lead or `compat-differential-tester` later
  reaches for `check-tags.test`'s or `tags.test`'s literal example
  journals as Ledgerkit test fixtures, the same §10.3 fifth-tier
  ("tests/examples derived from upstream") recording requirement `19`'s
  closing note already described applies identically here — not repeated
  in full, cross-referenced instead.

---

## Summary of proposed register entries (all `status: proposed`, none executable-verified)

| Proposed ID | Area | Kind | Notes |
|---|---|---|---|
| `LK-COMPAT-PARSER-TAG-001` | parser.tags | compatible | tag-extraction grammar itself (§2): name delimiting, no-space-before-colon voiding, bare/empty-value tags, comma-hard-separator/no-escaping, list-not-dict multi-value-per-name semantics. **Blocked** — no tag data model exists yet (§7). |
| `LK-COMPAT-PARSER-TAG-SCOPE-001` | parser.comments | compatible | which of Ledgerkit's four comment forms get tag-scanned (§1's table) — directly reuses existing comment-text-collection substrate per §5/§6, smallest-effort row to implement first |
| `LK-COMPAT-PARSER-POSTINGDATE-001` | parser.dates | compatible | `date:`/`date2:` posting-comment tags overriding per-posting effective date (§3), transaction-level-only-as-ordinary-tag distinction (§3.1/§3.4), `asum`-chain precedence (§3.2). **Blocked** — no `Posting.date_override`/`date2_override` field exists yet. |
| `LK-COMPAT-DIRECTIVE-TAG-001` | parser.directives | compatible | `tag` directive is advisory-only, zero inline-parsing enforcement (§4) — **exercisable today**, no new data model required, good candidate for an early differential-test win ahead of the rest of Phase 4 |
| (open question, no ID proposed) | models.Posting | — | back-reference (`Posting.transaction`) vs. pure-function-over-a-pair for computing effective dates/tags (§7.1) — needs a lead decision before `Posting`'s dataclass shape is finalised |

None of these have been added to `dev-docs/compat-register/` yet —
implementation-time work, consistent with `17-`/`19-`'s own closing notes.

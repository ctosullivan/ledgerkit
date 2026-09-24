# 23. `tag:NAME[=REGEX]` query-matching design

Design document, Stage C's `tag:` phase (first phase to use the new
roadmap-objective → context-curation → design-document → human-approval
→ implementation process). **Not an implementation plan.** No
`ledgerkit/`/`tests/` code touched producing this document. Implementation
does not begin until this document is explicitly approved (Step 3's
mandatory gate).

Built from a fresh, independent `context-curator` dispatch (not the
lead's own conversation memory — the curator report is the primary input,
spot-checked by the lead against source directly before use, per this
document's own §1 provenance discipline) plus the lead's own follow-up
verification. Every claim below is tagged with one of four categories, no
exceptions:

- **[VERIFIED-EXTERNAL]** — hledger's documented or directly-observed
  behaviour (manual, source, or the pinned binary run live).
- **[EXISTING-DECISION]** — behaviour/architecture Ledgerkit has already
  established in a prior phase.
- **[PROPOSED]** — a choice proposed for this phase, not yet approved.
- **[UNRESOLVED]** — requires an explicit human decision before
  implementation; not resolved by assumption anywhere in this document.

## 0. Pinned revisions

- Ledgerkit: `f397d85`. hledger: `1.52.4` /
  `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, pinned binary
  `1.52.4-g33fa849e7-20260910`. CodeCompass: local clone at `9d2a0da`
  (moved since Phase 5A's `4bc7c1d`; re-confirmed live this session, not
  assumed stale-safe).

## 1. Process note — how this document was built, and what was independently re-checked

A fresh `context-curator` agent (no access to this conversation's prior
turns) was dispatched with the existing Phase 5A context packet
(`validation/codecompass/context-packets/tag-query-matching.md`) as a
starting point it was explicitly told not to treat as authoritative. It
ran CodeCompass's real workflow first (Skill/`/discovery`/`query`),
re-verified `dev-docs/planning/core-redefinition/
19-tag-query-semantics-brief.md`'s claims against hledger's manual/
source/pinned binary directly (nine live differential runs on a scratch
fixture, not just re-reading the brief), and read every Ledgerkit source
file this feature would touch. Its full report is preserved as this
phase's primary evidence trail (not duplicated verbatim here — cited by
section below).

**The lead independently spot-checked the report's two most
architecturally significant claims before building on them** (the same
discipline Phase 5A's own retro named as its single most valuable step —
re-verifying a prior research claim rather than trusting it forward):

- `journalPostingsKeepAccountTagsOnly` (the `accounts` command's
  tag-stripping mode, §2.5 below) — confirmed via direct `grep` across
  the hledger source tree: exactly one call site,
  `hledger/Hledger/Cli/Commands/Accounts.hs:73`. Matches the report
  exactly.
- The missing-inheritance-layer claim (§4 below) — confirmed via direct
  `grep`/read of `ledgerkit/tags.py` (five functions, no inheritance
  logic) and `ledgerkit/parser.py` (tags assigned only from each entity's
  own `inline_comment`; `declared_account_tags` populated but never
  consumed anywhere). Matches the report exactly.
- The compat-register claim (no `LK-COMPAT-QUERY-TAG*` files exist yet)
  — confirmed via `ls dev-docs/compat-register/`. Matches exactly.

**One additional architectural fact, found by the lead's own follow-up
verification, not present in the curator's report**: `ledgerkit/query/
eval.py`'s `matches_transaction(node, txn)` and `matches_posting(node,
txn, posting)` **do not receive a `Journal` parameter at all**, and
neither does any of their four call sites in `reports.py`/`cli.py` —
even though every one of those call sites has `journal` available in its
own enclosing scope. This matters directly for §5's inheritance-scope
question: implementing rule A (account-tag inheritance, which needs
`Journal.declared_account_tags`) requires either threading a new
parameter through a **documented, public** function signature (`dev-docs/
api-spec.md` lines 1093+), or a different architectural approach
entirely. See §5, Option A's cost.

**Amendment round (this pass, same day): the original document above was
not yet ready for approval.** Its claim that rules A-D constitute
*complete* hledger 1.52.4 effective-tag semantics was incomplete — it
omitted **commodity-directive tag propagation**, a real, documented,
separately-verified fifth source. This amendment adds §2.6 (the verified
commodity-tag model, including a fully executable precedence matrix
across five source combinations — the original document's "posting tags
override account tags override commodity tags" question could not be
resolved from the manual's own wording alone, and was not resolved by
interpretation here either: a purpose-built fixture was run directly
against the pinned binary, §2.7), revises §2.5's `accounts`-mode finding
(the stripping is broader than originally reported — commodity-propagated
tags are stripped too, not just the posting's own), and substantially
rewrites §9.1/§9.2/§11 in light of both. Sections not touched by this
amendment (§1's original content above, §5.1/§5.2's `Tag` AST/parser
design, §6-§8, §13-§14) are unaffected — this is a targeted correction,
not a redesign, per the review's own explicit instruction.

## 2. Verified external behaviour — hledger's actual `tag:` semantics

### 2.1 Syntax and matching — [VERIFIED-EXTERNAL]

`tag:NAME` (bare — matches any value, including empty) and
`tag:NAME=REGEX` (name and value both required to match). Both
case-insensitive infix by default (same `HledgerRegex`-dialect contract
as `acct:`/`desc:` — no new regex-dialect work needed; folds into the
existing `LK-EXT-QUERY-001` extension entry, not a new one). `NAME` is
constructed by splitting on the **first** `=` (`Query.hs:482-487`) — the
same "split on first occurrence" convention Ledgerkit's own `depth:
REGEX=N` parsing already uses (`ledgerkit/query/parser.py`'s
`_build_depth_spec`), so this is a precedented pattern in Ledgerkit's own
code, not a new idiom.

Live-confirmed (context-curator's scratch fixture, 9 differential runs
against the pinned binary): `tag:a` matches any tag literally named `a`
(case-insensitive infix — so it also incidentally matches inside `payee`,
confirmed as expected regex behaviour, not a bug); `tag:a=1`/`tag:a=2`
correctly discriminate by value; anchored patterns (`tag:'^type$=^a$'`)
work as expected.

### 2.2 The four propagation/inheritance rules — [VERIFIED-EXTERNAL]

Independently re-confirmed live (not just re-read from brief 19), on a
fixture with `account assets:bank ; type:A` and a child
`assets:bank:savings` with no tags of its own:

- **Rule A** (account ← parent account's declared tags): a query for
  `type:A` against the *account name* `assets:bank:savings` matches,
  because `assets:bank`'s declared tag is inherited down the tree.
- **Rule B** (posting ← its own account's inherited tags): every posting
  to `assets:bank` (or any descendant) matches `tag:type=A`, even a
  posting with **no inline comment of its own at all**.
- **Rule C** (posting ← its transaction's own tags): a tag declared only
  on the transaction header line is matched by `tag:` queries against
  postings that have no comment of their own.
- **Rule D** (transaction ← the union of all its postings' effective
  tags, including inherited ones): consistent throughout; a transaction
  matches `tag:X` if *any* posting's effective tag set (after A/B/C)
  contains `X`.

All four compose: a posting with no comment of its own, under an account
with no comment of its own, under an ancestor account with a declared
tag, still matches — confirmed live.

### 2.3 Combination: always AND, never OR — [VERIFIED-EXTERNAL, newly executable-confirmed this phase]

Brief 19 (Phase 4) had flagged this as **source-derived only** — no test
in hledger's pinned suite exercised two bare, unnegated `tag:` terms
together. This phase's curator dispatch closed that gap with a live run:
`print tag:a tag:b` against a fixture where the two tags land on
different postings of different transactions matched **only** the
transaction where both tags co-occur — confirmed AND, not OR — directly
contrasted in the same session against `acct:food acct:transport`, which
correctly OR-combined. **This is new, stronger evidence than brief 19 had
when it proposed `LK-COMPAT-QUERY-TAG-COMBINE-001`** as a `status:
proposed`, source-only entry.

### 2.4 The `payee:`/`note:` case-sensitivity trap — [VERIFIED-EXTERNAL, out of this feature's scope]

Live-reconfirmed both branches (lowercase `tag:payee=X` hits a hardcoded
literal-string dispatch to the *derived* transaction payee, not the real
tag; `tag:Payee=X`, different case, falls through to the genuine tag
lookup). **Explicitly out of scope for this feature** — it only matters
if/when Ledgerkit implements `payee:`/`note:` themselves, which is not
this phase. Noted here only so the design doesn't accidentally
scope-creep into deciding it.

### 2.5 `accounts`' third matching mode — [VERIFIED-EXTERNAL, genuinely new relative to brief 19, revised this amendment]

Brief 19 §6 named two hledger code paths for account-name-level `tag:`
matching (bare `matchesAccount` never sees tags at all; `--declared`
mode uses only declared+inherited tags). **A third, distinct mode exists
that brief 19 did not name**: plain `accounts tag:X` (the default,
non-`--declared` mode) builds its list via
`journalPostingsKeepAccountTagsOnly` — confirmed, by direct source read,
to be called from **exactly one place**,
`hledger/Hledger/Cli/Commands/Accounts.hs:73`.

**Revised finding, twice now — this pass corrects the immediately prior
amendment, which was itself incomplete.** `journalPostingsKeepAccountTagsOnly`'s
implementation is `keepaccounttags p = p{ptags=[]} \`postingAddTags\`
(journalInheritedAccountTags j $ paccount p)` (`Journal.hs:669`) — it
**replaces** a posting's own tag list (`ptags`) with only its account-
inherited tags. Since commodity-propagated tags are, by §2.6, already
merged into `ptags` earlier in the pipeline, `ptags=[]` discards them
too, alongside the posting's own literal comment tags. **But this is not
the whole story**: query matching (`matchesPosting (Tag ...) p =
patternsMatchTags n mv $ postingAllTags p`) reads `postingAllTags p =
ptags p ++ maybe [] ttags (ptransaction p)` — and that **unconditionally
adds the transaction's own tags (`ttags`) back in**, regardless of
whatever `keepaccounttags` did to `ptags`. The previous amendment's
"shows only account-inherited tags" claim missed this — transaction-level
tags are **also** visible to plain `accounts tag:X`, not stripped.

**Four-way visibility, now executable-confirmed precisely** (same
precedence fixture as §2.7, plus a targeted re-test this pass):

| Source | Visible to plain `accounts tag:X`? | Confirmed |
|---|---|---|
| Transaction-level (own header tag) | **Yes** | `accounts tag:rate=4` → matches (transaction 4's own `rate:4`) |
| Account-inherited (declared/parent) | **Yes** | `accounts tag:rate=3` → matches both `assets:bank` and `assets:bank:sub` |
| Posting-own (literal comment tag) | **No** | `accounts tag:rate=1` → empty |
| Commodity-propagated | **No** | `accounts tag:rate=2` → empty |

Plain `accounts tag:X` therefore shows **transaction-level and
account-inherited** tags, and hides **posting-own and commodity-
propagated** tags — a real, source-confirmed, now fully four-way-tested
hledger behaviour, not the simpler "account-only" rule either amendment
round previously stated.

**This means `accounts` has a real, `tag:`-specific behavioural wrinkle
— a different shape from `depth:`'s wrinkle** (`depth:` needed a
report-display side-channel, `DepthSpec`, threaded through every report
function; `tag:`'s `accounts` wrinkle is narrower: one command, one
matching-mode substitution, no side-channel needed). See §7 for the
concrete implication and §9 for the open question this raises.

### 2.6 Commodity-tag propagation — [VERIFIED-EXTERNAL, new this amendment — was missing from the original document]

**Manual** (`hledger.1:3550-3556`, "Commodity tags" section, quoted in
full): *"A commodity directive's comment may contain tags. These will be
propagated to all postings using that commodity in their main amount, as
hidden but queryable posting tags, except where the posting already [has]
a tag of the same name. (Posting tags override account tags override
commodity tags.)"*

**Source, traced precisely**:
- `Journal.jdeclaredcommoditytags :: M.Map CommoditySymbol [Tag]`
  (`Types.hs:676`) — real storage, populated from `commodity` directive
  comments at read time (`JournalReader.hs:634-639,666-667`).
- `journalCommodityTags :: Journal -> CommoditySymbol -> [Tag]`
  (`Journal.hs:653-655`) — lookup.
- `journalPostingsAddCommodityTags :: Journal -> Journal`
  (`Journal.hs:659-662`) — `addtags p = p \`postingAddTags\`
  concatMap (journalCommodityTags j) (postingCommodities p)` — for every
  posting, looks up tags for **every commodity used in its main amount**
  (`postingCommodities`, plural — a posting can reference more than one)
  and adds them via `postingAddTags`.
- `journalPostingsAddAccountTags :: Journal -> Journal` (`Journal.hs:
  648-650`) — the **same** mechanism, same `postingAddTags` function,
  for account-inherited tags: `addtags p = p \`postingAddTags\`
  (journalInheritedAccountTags j $ paccount p)`.
- **Both are applied once, at journal-read time**, gated by a single
  flag: `Read/Common.hs:397` (`if auto_posting_tags_ then
  journalPostingsAddAccountTags else id`) and `:412` (same, for
  commodity tags) — run unconditionally in sequence on every journal
  read. `auto_posting_tags_`'s value is **not** the raw library default
  (`InputOptions.hs:60`, `False`) — traced to
  `hledger/Hledger/Cli/CliOptions.hs:642`: `autopostingtags = not $
  command == "print" && moutputformat == Just "beancount"` — **`True`
  for every normal CLI command**, `False` only for `print
  --output-format=beancount` (the "beancount export" exception the
  library doc-comment names). This resolves, precisely, why the original
  document's live tests already observed account-tag inheritance working
  by default: the CLI's own default genuinely is "propagate," not the
  library's nominal `False`.
- **Query-time matching reads only the already-materialized result**:
  `matchesPosting (Tag n v) p = ... patternsMatchTags n mv $
  postingAllTags p`, and `postingAllTags p = ptags p ++ maybe []
  ttags (ptransaction p)` (`Posting.hs:439-440`) — **no live
  `Journal`-dependent computation happens at query-match time at all**.
  Everything `tag:` can see was already written onto `ptags`/`ttags`
  during journal reading, once, before any query ever runs. This is
  materially different from how the original document (and §2.2's own
  framing) implicitly described rules A-D — not as four rules a query
  evaluator applies dynamically, but as a **single, one-time propagation
  pass** whose *result* a completely ordinary, non-inheriting
  `ptags ++ ttags` union then reads. See §5.3/§9.1 for what this means
  for Ledgerkit's own design.

### 2.7 Same-name, different-value precedence — [VERIFIED-EXTERNAL, executable, resolves an open question the manual's wording alone could not]

The manual's "posting tags override account tags override commodity
tags" reads, on its face, like exclusion/shadowing — only the
highest-priority value visible when names collide. **Executable testing
shows this is not what happens for `tag:` query matching.** Fixture
(`commodity $  ; rate:2, csrc:1` / `account assets:bank  ; rate:3,
asrc:1` / a transaction with posting `; rate:1, psrc:1` and a sibling
transaction with a header-level `; rate:4` and posting-level `; rate:5`
on the same account), run against the pinned binary:

| Query | Matches |
|---|---|
| `tag:rate=1` (posting's own) | only the transaction whose posting has it |
| `tag:rate=2` (commodity's) | **that same transaction too**, alongside every other transaction on that commodity |
| `tag:rate=3` (account's) | **every** transaction posting to that account or a descendant — including the one whose posting has its own, *different*, `rate:1`/`rate:5` |
| `tag:rate=4` (one transaction's own header tag) | only that transaction |
| `tag:rate=5` (that same transaction's own posting tag) | only that transaction |
| `balance tag:rate=3` | aggregates postings correctly at the posting level too, not just `print`'s transaction-level view |

**Reconciled finding, source and executable now in agreement**: `Tag =
(TagName, TagValue)` (`Types.hs:442`), a plain tuple with derived
(structural) `Eq`. `postingAddTags p@Posting{ptags} tags = p{ptags=ptags
\`union\` tags}` (`Posting.hs:467-468`) — `Data.List.union`'s
deduplication is by **full tuple equality** (name **and** value), so a
commodity/account tag with the same **name** but a **different value**
from an existing posting tag is *not* considered a duplicate and *is*
still added. **The manual's "override" language does not mean exclusion
for query-matching purposes — every differently-valued, same-named tag
from every applicable source remains simultaneously, independently
matchable.** "Override" appears to describe something narrower than this
document tested (plausibly which value a hypothetical single-value
lookup would prefer, or purely avoiding literal identical-tuple
duplication) — not investigated further here, since it doesn't change
the `tag:`-matching contract this feature actually needs to implement.
**The executable result, not the manual's prose, is the basis for the
proposed compatibility contract** (§9.1/§10), per this amendment's own
governing instruction.

## 3. Existing Ledgerkit decisions this design must respect

- **[EXISTING-DECISION]** `QueryNode` is the selection-predicate AST;
  `DepthSpec`/`QueryPlan.depth` is a separate, non-predicate report
  option (Stage C Phase 5). `tag:` is an ordinary selection predicate —
  it belongs on the `QueryNode` side, full stop; there is no `tag:`
  analogue to `depth:`'s report-display-vs-predicate split. This was the
  single question Phase 5's own redesign turned on, and the curator's
  independent read of `reports.py`/`cli.py` confirms `tag:` doesn't raise
  it at all.
- **[EXISTING-DECISION]** `reports.py`'s `balance`/`register`/`accounts`/
  `stats` and `cli.py`'s `print` all already generically dispatch **any**
  `QueryNode` through `_query_ast_matches_posting`/
  `_query_ast_matches_transaction` via `isinstance`. A new predicate node
  requires **no changes** to `reports.py`'s or `cli.py`'s call-site
  structure — confirmed by direct read, all four call sites shown in §1.
  This is a materially smaller footprint than `depth:`'s own Phase 5
  redesign.
- **[EXISTING-DECISION, corrected this amendment]** `ledgerkit/tags.py`
  (Phase 4) parses and stores three of hledger's tag scopes: `Posting.
  tags`, `Transaction.tags`, `Journal.declared_account_tags`. **This is
  no longer "sufficient" now that §2.6 establishes commodity-directive
  tags as a real, distinct fourth source** — Ledgerkit has **no
  substrate for these at all**, confirmed this amendment by direct read
  of `ledgerkit/parser.py`'s `commodity` directive handling
  (lines 1288-1299): `body = _strip_directive_comment(rest)` **discards**
  the directive's inline comment before extracting the symbol — the
  comment text is never captured, and indented follow-on lines after a
  `commodity` directive are consumed as an ordinary, discarded
  subdirective (`in_subdirective = True`) exactly as `account` directive
  comments were *before* Phase 4 added capture for them. `Journal.
  declared_commodities` (`models.py:307`) is a bare `list[str]` — no
  parallel to `declared_account_tags`'s `dict[str, list[tuple[str,
  str]]]` shape exists for commodities at all. See §4's revised scope
  and §9.1's revised Option A.
- **[EXISTING-DECISION]** `dev-docs/hledger-compatibility.md:177`
  already states, correctly and currently, that Ledgerkit's tag storage
  "does not include tags inherited from a parent account — inheritance is
  a separate, not-yet-built computation." This document's §4/§5 is that
  "separate computation" being designed, not a new discovery that
  Ledgerkit is behind — the gap was already disclosed.
- **[EXISTING-DECISION]** Same-prefix combination buckets in `parser.py`
  are `acct_terms`/`desc_terms`/`status_terms` (OR'd) vs. `other_terms`
  (AND'd individually) — confirmed by direct read
  (`ledgerkit/query/parser.py:336-339`). A `Tag` node needs **no new
  bucket** — it's excluded from all three OR-eligible `isinstance`
  checks by construction, so it lands in `other_terms` (AND) automatically,
  correctly matching §2.3's now-executable-confirmed behaviour, with zero
  new combination code.
- **[EXISTING-DECISION]** `LK-EXT-QUERY-001` already covers the
  `HledgerRegex`-dialect extension generally; `tag:`'s name/value
  patterns reuse it, no new regex-dialect register entry needed.

## 4. What's actually missing: the effective-tags computation, and a substrate gap for one of its four sources

**[VERIFIED-EXTERNAL + EXISTING-DECISION, synthesised, revised this
amendment]**: hledger's `tag:` reads from the union of **four** sources
per posting — its own tags, its transaction's own tags, its account's
declared-and-inherited tags, and its main amount's commodity's declared
tags (§2.2's rules A-D plus §2.6) — computed **once**, at journal-read
time, not per-query (§2.6's own revised understanding). Ledgerkit's
`Posting.tags`/`Transaction.tags` hold only each entity's **own** literal
inline-comment tags — confirmed by direct read of `ledgerkit/parser.py:
894-896` (`txn.tags = parse_tags(txn.inline_comment)`, same pattern for
postings) and `ledgerkit/tags.py` (five functions total: `parse_tags`,
`_parse_comment_line_tags`, `effective_date`, `effective_date2`,
`_tag_name_before_colon` — no inheritance function exists).

**Two distinct gaps, not one**:

1. **Computation gap** (account-inheritance): `Journal.
   declared_account_tags` is populated correctly from `account NAME ;
   tag:value` directives but has **no consumer anywhere** in the current
   codebase — confirmed by grep. The data exists; nothing reads it back.
2. **Substrate gap** (commodity tags, new this amendment, §3): `Journal.
   declared_commodities` has no tag storage at all, and
   `ledgerkit/parser.py`'s `commodity` directive handling actively
   discards the comment text needed to populate one. The data doesn't
   exist yet to be read.

Implementing `tag:` correctly therefore requires closing **both** gaps —
not just an AST node + eval branch (which is all `acct:`/`desc:`/
`status:` ever needed), and not just the account-inheritance computation
the original document scoped. This is the central design fork — see
§5's two options, now revised in §9.1.

## 5. Proposed AST/parser/evaluator design

### 5.1 AST node — [PROPOSED]

```python
@dataclass(frozen=True)
class Tag:
    """Matches an effective tag name (and, if given, value).

    name_pattern: validated HledgerRegex pattern, matched against tag names.
    value_pattern: validated HledgerRegex pattern, matched against tag
        values; None means "any value, including empty" (bare tag:NAME).
    """
    name_pattern: str
    value_pattern: str | None = None
```

Added to `ledgerkit/query/ast.py`'s `QueryNode` Union (currently `Union[
Acct, Desc, DateSpan, MaxAccountLevel, Status, And, Or, Not]`, `dev-docs/
api-spec.md` line 1040) — a **documented public API signature change**,
requiring the Unauthorised Change Rule gate (§10).

### 5.2 Parser — [PROPOSED]

```python
def _build_tag(value: str) -> Tag:
    name, sep, val = value.partition("=")
    # validate name/val via compile_hledger_regex, same as _build_acct/_build_desc
    ...
    return Tag(name, val if sep else None)
```

Registered as `"tag:": _build_tag` in `_PREFIX_BUILDERS`. No change to
the OR/AND bucket-building logic (§3) — confirmed.

### 5.3 Evaluator — [PROPOSED, contingent on §9's unresolved question]

Regardless of which inheritance option §9 resolves to, `matches_
transaction`/`matches_posting` each gain one new `isinstance(node, Tag)`
branch. The two options differ in what that branch actually computes,
**and, per §2.6's revised understanding, in a third dimension not
originally considered: *when* effective tags get computed at all.**
hledger materializes once, at journal-read time, by mutating `ptags`
directly (§2.6) — query matching itself is then a trivial, non-
inheriting union read. Ledgerkit's own established style is the
opposite: pure, on-demand computation with no model mutation after
parsing (`ledgerkit/tags.py`'s existing `effective_date`/`effective_date2`
precedent computes on every call, never writes back onto `Posting`).
Mirroring hledger's literal mechanism (mutate `Posting.tags`/
`Transaction.tags` to include inherited/commodity tags) would also
**silently break Phase 4's already-approved, documented contract** that
`Posting.tags`/`Transaction.tags` hold *only* each entity's own literal
tags (`dev-docs/api-spec.md`, confirmed via `AskUserQuestion` at Phase
4 time) — not a change this document proposes making implicitly. See
§9.1 for the resulting three-way framing this adds.

### 5.4 `__init__.py` — [PROPOSED]

Export `Tag` from `ledgerkit.query`'s `__all__`, alongside the existing
`MaxAccountLevel`/`DepthSpec` exports.

## 6. Transaction-level and posting-level matching, explicitly

- **Posting-level** (`matches_posting`, used by `balance`/`register`/
  `accounts` default mode): a posting matches `tag:X` if `X` is in its
  **effective** tag set — which option (§9.1) determines whether that's
  "own tags only" (Option B) or the full four-source union — own,
  transaction's own, inherited-account's, and commodity-propagated
  (Option A, §2.2/§2.6/§2.7).
- **Transaction-level** (`matches_transaction`, used by `print`) —
  **[VERIFIED-EXTERNAL, precise wording corrected this pass]**: a
  transaction matches `tag:X` if **its own tags directly match, OR any
  of its postings' effective tags match** — not "only through its
  postings," which would misstate the rule even though in practice a
  transaction's own tags also propagate onto every one of its postings
  (rule C) and so are *usually* reachable the second way too. Confirmed
  precisely from source: `transactionAllTags t = ttags t ++ concatMap
  ptags (tpostings t)` (`Posting.hs:443-444`) — the transaction's own
  `ttags` are unioned in **directly**, not solely via its postings' own
  `ptags` (which is deliberately used here, not `postingAllTags`, to
  avoid double-counting `ttags` once directly and again through every
  posting). Both halves of the OR are real, independent inputs to the
  same match — stated explicitly here so an implementation doesn't
  accidentally special-case away the direct half on the assumption that
  posting-level propagation already covers it.

## 7. Affected CLI commands and report paths

- **`balance`/`register`/`print`** — [PROPOSED] no code changes beyond
  the generic `Tag` eval branch; they already thread any `QueryNode`
  through generically (§3).
- **`stats`** — [PROPOSED] same as above; `tag:` is a selection predicate
  filtering the transaction list `stats` already filters via `_query_ast`
  — no `depth:`-style exception applies here (that was specific to
  `stats`' own account-count/depth fields reading a *different*,
  exclusion-based mechanism; `tag:` doesn't touch that mechanism at all).
- **`accounts`** — [UNRESOLVED, see §9] — hledger's own `accounts tag:X`
  has the real, distinct posting-own-tag-stripping behaviour (§2.5).
  Whether Ledgerkit's `accounts` command replicates it is not decided by
  this document.

## 8. Interaction with other query terms and boolean operators

- **[EXISTING-DECISION]** `tag:` AND-combines with everything else by
  falling into `other_terms` (§3) — no new combination logic.
- **[VERIFIED-EXTERNAL]** Multiple unnegated `tag:` terms AND together
  (§2.3) — this is what "falls into `other_terms`" already produces
  mechanically (each `tag:` term becomes its own `other_terms` entry,
  individually AND'd) — confirmed this is the correct behaviour, not an
  accidental side effect to special-case around.
- **`not:tag:X`** — [PROPOSED] should work via the existing generic
  `Not` wrapper (`_parse_term`'s `token.startswith("not:")` handling
  already recurses generically over any prefix) — no special-casing
  needed, unlike `depth:`'s explicit `not:depth:...` rejection (which was
  needed *because* `depth:` isn't a predicate at all; `tag:` is a real
  predicate, so negating it is meaningful and should be allowed, not
  rejected).

## 9. Unresolved questions — explicit human decisions required

### 9.1 [UNRESOLVED] Inheritance implementation scope

**Option A — complete effective-tag semantics for the pinned hledger
1.52.4 baseline (revised this amendment)**: all four verified sources —
posting's own, transaction's own, account-inherited (rule A-D), **and
commodity-propagated (§2.6)** — with the §2.7 union-not-shadowing
precedence (every differently-valued same-named tag from every source
stays independently matchable; no source is silently excluded by
another). **§9.1's original text described Option A as "matching hledger
exactly" while covering only three of the four sources — that was not
yet accurate, and is corrected here.** This is the recommended option,
unchanged in direction from the original document, but its scope is now
materially larger:

Requires, closing **both** gaps §4 names:
- A new `ledgerkit/tags.py` computation (e.g. `effective_tags(journal,
  txn, posting) -> list[tuple[str, str]]`) unioning all four sources —
  no shadowing/exclusion logic needed (§2.7), just concatenation, which
  simplifies the implementation relative to what a naive reading of the
  manual's "override" language would have required.
- **New commodity-tag substrate** (§3/§4's gap 2): a `Journal.
  declared_commodity_tags: dict[str, list[tuple[str, str]]]` field
  (mirroring `declared_account_tags`'s exact shape) and parser capture
  of `commodity` directive same-line and follow-on comment tags —
  structurally a close parallel to Phase 4's own `account`-directive tag
  work, not a novel parsing problem.
- A decision on **when** effective tags get computed (§5.3's new
  framing): materialize once (mirroring hledger's own mechanism, but
  this would mean mutating `Posting.tags`/`Transaction.tags` and
  breaking Phase 4's already-approved "own tags only" contract — **not
  proposed**), or compute on demand at query-evaluation time (matches
  Ledgerkit's own established pure-function style, but needs `Journal`
  access at match time — see below), or materialize once into **new,
  separate** storage that doesn't touch `Posting.tags`/`Transaction.
  tags`'s existing meaning (a third option, not in the original
  document, that could sidestep the evaluator-signature question below
  entirely by doing the materialization as its own pass before query
  evaluation runs, storing the result somewhere new rather than on the
  existing fields or as a per-call computation).

**Evaluator API shape — revised, softer than the original document's
recommendation (per explicit review instruction, and corrected again
this pass)**: the original text proposed a new **required positional**
`journal` parameter on `matches_transaction`/`matches_posting` — the
first correction round replaced that with "a keyword-only `journal`
parameter with no default," describing it as leaving existing callers
unaffected. **That description was itself wrong**: in Python, a
keyword-only parameter with no default is still mandatory on every
call — `def f(*, journal): ...` raises `TypeError` for any caller that
doesn't pass `journal`, keyword-only or not. Making it keyword-only
changes *how* a caller must supply it, not *whether* every caller must.
**Do not assume any specific shape.** Backward-compatible candidates
for implementation planning to evaluate, none chosen here:
- `journal: Journal | None = None` (a real default, so existing callers
  that pass no `journal` keep compiling and running unchanged) — but
  `Tag` evaluation must then **fail explicitly** (raise, not silently
  degrade) if a `Tag` node is actually present in the query being
  evaluated and `journal` is `None`, per the loud-failure constraint
  below; this is not "the parameter is optional," it's "the parameter
  has a default, and its absence is only tolerated when nothing needs it";
- an evaluation-context object bundling `journal` (and any future
  cross-cutting need) behind one parameter, added once rather than
  per-need — same "callers not using `Tag` need not change" property,
  differently shaped;
- pre-materialised effective-tag storage (§5.3's "materialize into new
  storage before evaluation" option), which could avoid touching
  `matches_transaction`/`matches_posting`'s signatures at all.

If a `Tag` query is ever evaluated without the context it needs (e.g. a
direct `matches_posting(Tag(...), txn, posting)` call with no journal
available, under whichever of the above shapes is chosen), **prefer an
explicit, loud failure over silently degrading to own-tags-only
matching** — a silent narrowing would be a correctness bug disguised as
a working answer, worse than an error. This is a design constraint for
whichever shape is ultimately chosen, not itself a decision to make now
— implementation planning chooses the shape; this document only
constrains what any chosen shape must not do (silently narrow).

**Option B — literal-own-tags-only, disclosed Ledgerkit-native subset
first (mirroring the `MaxAccountLevel` precedent), unchanged from the
original document.**

`tag:` matches only each posting's/transaction's own literal inline-
comment tags (rules B/C's "own" half only — no account inheritance, no
commodity propagation). No `Journal` threading needed, no new commodity
substrate needed. Ships faster, smaller diff.

Cost: a real, disclosed divergence from hledger, now covering **two**
missing sources instead of one (account-inherited and commodity-
propagated) — a real query for a commodity-declared or account-declared
tag would silently return nothing on a posting with no matching literal
comment of its own, a materially bigger gap from real hledger behaviour
than the original document's framing implied.

**Lead's recommendation, restated**: Option A — full compatibility,
covering all four sources, unchanged in direction from the original
document. Per the explicit review instruction, this is **not** presented
as preferable merely on general-internal-consistency grounds; it is
recommended because (a) the added commodity-tag work is structurally a
close parallel to Phase 4's own already-successful account-tag work, not
novel risk, and (b) Option B's disclosed gap is now bigger (two missing
sources, not one) with no new evidence suggesting either gap is
individually more tractable to defer than the other. **Still not a
decision** — explicit approval required, including which evaluator-API
shape (above) implementation planning should pursue first.

**Commodity-tag substrate scope — resolved this pass, per explicit
instruction (design approval only; nothing implemented here)**: the
missing commodity-tag substrate (§3/§4) is **in scope for this same
Phase 6**, not split into a prerequisite sub-phase. Rationale: unlike
Phase 4's own account-tag work (which was a genuinely separate feature —
tag *parsing/storage* — split from `tag:` *matching*, a different
capability entirely), the commodity-tag substrate is not a separate
feature relative to this phase's own scope; it is a bounded completion
of `tag:` matching itself — §2.6/§2.7 already establish it as one of the
four sources this phase's own `tag:` semantics require to be correct.
Proposed, not yet implemented:

- `Journal.declared_commodity_tags: dict[str, list[tuple[str, str]]]`
  (mirroring `declared_account_tags`'s exact existing shape) — a new
  field, additive, same category of change as Phase 4's own addition
  (§11).
- `ledgerkit/parser.py`'s `commodity` directive handling captures
  same-line and follow-on comment tags, mirroring Phase 4's own
  `account`-directive tag-capture work structurally (§3's confirmed
  parallel: `_strip_directive_comment` currently discards the comment
  outright; the fix is the same shape as the `account`-directive fix
  Phase 4 already shipped, not a novel parsing problem).
- The lookup/propagation helper(s) this produces are **private
  initially** (§9.3, unchanged) — no new public API surface without a
  demonstrated external consumer.

This resolves the scoping question §17 previously listed as open; it is
no longer part of the approval list below.

### 9.2 [UNRESOLVED] `accounts` command's matching mode — recommendation reversed this amendment

Per §2.5/§7: does Ledgerkit's `accounts -q "tag:X"` replicate hledger's
mode (§2.5, corrected: **transaction-level and account-inherited tags
visible; posting-own and commodity-propagated tags not visible**), or
use uniform matching (same effective-tag computation as every other
command)?

**The original document recommended uniform matching (divergence). Per
explicit review instruction, that recommendation is reconsidered and
reversed.** The review's own framing is correct: this design has already
established the `accounts` quirk is real, source-confirmed
(`Accounts.hs:73`, exactly one call site), and now executable-confirmed
across three successive verification passes (§2.5's original posting-own
test; a broader commodity-stripping re-test; and this pass's four-way
matrix, which corrected the second pass's own incomplete "account-only"
claim by finding transaction-level tags are visible too) — and, per §7,
implementable as a
narrow, single-command behaviour substitution with **no side-channel**
needed (unlike `depth:`'s `DepthSpec`, which needed one threaded through
every report function). The original recommendation's stated reasons —
"a second special case in one phase" and "value... unclear" — do not
hold up against that combination of confirmed reality, confirmed
narrowness, and confirmed low implementation cost. General internal-
consistency preference alone (this document's own prior stated reason)
is not, on reflection, a strong enough technical reason to choose a
known, disclosed, easily-avoidable divergence over a small amount of
extra, well-understood matching logic.

**Lead's recommendation, reversed**: **replicate hledger's `accounts`
semantics** — a dedicated `accounts`-only effective-tags computation
unioning **only** transaction-own tags and account-inherited tags
(explicitly excluding posting-own and commodity-propagated), mirroring
`journalPostingsKeepAccountTagsOnly` + `postingAllTags`'s combined shape
at the Ledgerkit-query-evaluation level, not by mutating `Posting.tags`
— consistent with §9.1's own materialize-vs-compute-on-demand framing —
unless implementation planning finds a concrete technical reason (not
general preference) that this is disproportionately complex relative to
§9.1's already-required account-inheritance computation, which this
would reuse directly (the `accounts`-mode computation unions two of the
same four inputs §9.1's full computation already needs — transaction-own
and account-inherited — rather than all four). Still not a decision —
the reversal is the lead's own re-assessment under explicit instruction
to reconsider, not a resolved fact.

### 9.3 [UNRESOLVED] Effective-tags helper API shape — default changed to private this amendment

If Option A (§9.1) is approved: should the new account-inheritance and
commodity-lookup helpers (e.g. `_inherited_account_tags(journal,
account)`, `_commodity_tags(journal, symbol)`, `effective_tags(journal,
txn, posting)`) be public or private in `ledgerkit/tags.py`?

**Default changed this amendment, per explicit review instruction**: keep
all new inheritance/commodity helpers **private** initially (leading-
underscore, undocumented in `dev-docs/api-spec.md`'s public surface) —
do not expand Ledgerkit's public API without a demonstrated external
consumer. This mirrors the project's own existing precedent
(`ledgerkit/query/parser.py`'s `_build_acct`/`_build_desc`/
`_build_depth_spec` are all private; only `parse()` itself and the
`QueryNode`/`QueryPlan` types are public). A private helper can be
promoted to public later in a normal, reviewable, smaller change if a
genuine use case appears — the reverse (walking back an already-public,
already-documented function) is the more expensive direction, so
defaulting private is the lower-risk starting point. This does not block
implementation planning — it is a default to follow unless planning
surfaces a concrete reason a specific helper needs to be public from
day one.

## 10. Compatibility implications

- New compat-register entries needed (all currently only proposed in
  brief 19's prose, never created as files — confirmed): `LK-COMPAT-
  QUERY-TAG-001` (basic name/value matching), `LK-COMPAT-QUERY-TAG-
  COMBINE-001` (§2.3 — now has *executable* evidence behind it, stronger
  than brief 19's original source-only proposal), and, contingent on
  §9.1's resolution, either `LK-COMPAT-QUERY-TAG-INHERIT-001` (`status:
  proposed` → verified, if Option A) or a new `intentional_divergence`
  entry (if Option B). §9.2's `accounts` decision needs its own entry
  either way (`compatible` if mirrored, `intentional_divergence` if not).
- **New this amendment, per §2.6/§2.7**: a `LK-COMPAT-QUERY-TAG-
  COMMODITY-001` entry (commodity-directive tag propagation) is needed —
  distinct from `LK-COMPAT-QUERY-TAG-INHERIT-001` (account inheritance),
  since it's a genuinely separate source with its own substrate gap
  (§3/§4). A `LK-COMPAT-PARSER-TAG-COMMODITY-001`-shaped entry (parsing/
  storage layer, mirroring Phase 4's own `LK-COMPAT-PARSER-TAG-SCOPE-001`
  precedent for `account`-directive tags) is also needed if the
  commodity-tag substrate work lands as part of this phase (§9.1's own
  open scoping question).
- **The precedence/union finding (§2.7) belongs in `LK-COMPAT-QUERY-TAG-
  INHERIT-001`'s and `-COMMODITY-001`'s own `reason:` fields explicitly**
  — both entries must state plainly that same-named, differently-valued
  tags from multiple sources are simultaneously matchable (no shadowing),
  contradicting a literal reading of the manual's "override" language,
  with the executable evidence cited as the basis, not the manual's
  prose (per this amendment's own governing instruction).
- **Do not classify the overall `tag:` implementation as `compatible`
  while any of the four verified sources (posting/transaction/account/
  commodity) remains unimplemented** — if Option B (§9.1) or a partial
  implementation ships, the top-level `tag:` compat-register entry must
  be `intentional_divergence` or carry an explicit, itemised "sources
  not yet covered" note, never a bare `compatible` that implies full
  coverage it doesn't have.
- Per Stage C Phase 5's own new process (`09-compatibility-system.md`
  §9.6): any of these entries reaching `status: verified` for the first
  time must come from a genuinely separate `compat-differential-tester`
  dispatch, not the implementing session — this is restated as a hard
  requirement for the implementation phase (Step 7 of the overall
  process), not optional.

## 11. Backwards-compatibility implications for the Python API

- **`ledgerkit.query.ast.QueryNode`** gains a new Union member (`Tag`) —
  additive, does not break existing code matching on the Union
  exhaustively via `isinstance` chains (Ledgerkit's own `eval.py` pattern
  already has a `TypeError` fallback for unhandled node types, so this
  is the intended extension point, not a breaking change to that
  pattern).
- **If Option A (§9.1) is approved and a `journal` parameter is the
  chosen shape** (not the only option under consideration — see §9.1's
  evaluator-API framing, corrected this pass): a `journal: Journal |
  None = None` **default** (not a keyword-only-with-no-default
  parameter, which would still be mandatory on every call — a Python
  fact the previous wording here got wrong) is the leading candidate for
  minimising breakage to existing callers that never construct a `Tag`
  node — full sign-off under the Unauthorised Change Rule is still
  required regardless of which shape is chosen, since any new parameter
  on a documented public function is itself a signature change.
  **Explicit constraint, not yet a chosen shape**: no silent
  degradation — a `Tag` query evaluated without required context must
  fail loudly, never silently narrow to a subset of the four sources.
  This whole question is deferred to implementation planning (§9.1), not
  resolved here.
- **New this amendment**: if the commodity-tag substrate (§3/§4) is
  built, `Journal` gains a new field (`declared_commodity_tags`,
  mirroring `declared_account_tags`'s exact shape) — additive, not a
  change to any existing field, same category of change as Phase 4's
  own `declared_account_tags` addition.
- No change proposed to `Posting`/`Transaction`'s own dataclass fields
  (§3) — existing Phase 4 shapes remain sufficient for what they store;
  only `Journal` gains new storage, and only if the commodity substrate
  work is approved as part of this phase.

## 12. Edge cases

- **[VERIFIED-EXTERNAL]** Empty tag value (`name:` with nothing after
  the colon) — legal, `parse_tags` already returns `("name", "")` for
  this; `tag:NAME` (bare) must match it, `tag:NAME=` (empty pattern)
  should also match it as a valid regex matching the empty string — no
  special-casing needed in the query layer, this falls out of correct
  regex handling.
- **[VERIFIED-EXTERNAL]** Regex metacharacters in tag name/value — same
  `HledgerRegex` dialect boundary as everything else; no new work.
- **[VERIFIED-EXTERNAL]** The two-space-before-`;` account-directive
  trap (`account assets:bank ; type:A` with only **one** space is not a
  comment at all — the `;` becomes part of the literal account name;
  confirmed live, and already correctly documented/implemented in
  Ledgerkit's existing parser/docs, `dev-docs/hledger-compatibility.md:
  154`). Flagged here only as a fixture-construction trap for whoever
  builds the test journal for this feature — not a Ledgerkit gap.
- **Case sensitivity** — name/value patterns are case-insensitive (same
  `re.IGNORECASE` contract as `acct:`/`desc:`); confirmed no special
  case-sensitivity handling needed for `tag:` itself (§2.4's trap is
  `payee:`/`note:`-specific, out of scope).
- **[VERIFIED-EXTERNAL, new this amendment]** Same tag name, different
  values, from different sources — **no shadowing, all remain
  independently matchable** (§2.7). A naive implementation that
  deduplicates by name only (keeping just the "highest-priority" source's
  value) would be **wrong** — the correct behaviour is a plain union
  with no exclusion logic at all beyond avoiding literal identical
  `(name, value)` duplicates, which happens for free with a `list`
  (or would need explicit dedup only to avoid cosmetic repeats, never to
  implement precedence).
- **`tag:NAME=VALUE`'s `=` is split on the *first* occurrence only**
  (§2.1, unchanged) — a value itself containing `=` (e.g. `tag:rate==0.05`
  for a tag literally named `rate` with value `=0.05`) must preserve
  everything after the first `=` as the value pattern, not silently
  truncate or mis-split on a later `=`. Already the correct behaviour of
  Python's `str.partition("=")` (§5.2's proposed `_build_tag`), but
  worth a named regression test (§16) given it's easy to get wrong with
  a different split function.
- **`tag:.=VALUE`** (value-only matching, name pattern `.` matching any
  single character — in practice any non-empty name, or `.*`/`` for
  fully unconstrained) is ordinary regex behaviour, not a special case —
  no dedicated handling needed, but worth a named test (§16) confirming
  Ledgerkit's `HledgerRegex` dialect doesn't reject `.` or `.*` as a
  name pattern.

## 13. Error behaviour

- **[PROPOSED]** Malformed regex in either the name or value half of a
  `tag:` term raises `QueryParseError` at parse time, mirroring
  `_build_acct`/`_build_desc`'s existing pattern (catching `ValueError`/
  `re.error` from `compile_hledger_regex` and re-raising with a `tag:`-
  prefixed message) — no new error-handling design needed, direct reuse
  of an established pattern.
- **[PROPOSED]** `not:tag:...` is valid (§8) — no new rejection needed,
  unlike `depth:`'s deliberate `not:depth:...` rejection (which existed
  specifically because `depth:` isn't a predicate at all).

## 14. Explicit non-goals

- `cur:` (currency/commodity query term) — separate, unstarted, not
  touched by this design.
- `payee:`/`note:` and their shared-AST-node case-sensitivity trap
  (§2.4) — separate, unstarted.
- `PythonRegex` extension syntax — separate, unstarted.
- The `Query`-as-compatibility-shim migration — separate, unstarted.
- A standalone `--depth`/`-N` CLI flag — separate, already deferred by
  Stage C Phase 5's own G-CC-4-adjacent decision, unrelated to this
  feature.
- Re-running Stage C Phase 5A as another CodeCompass evaluation phase —
  explicitly out of scope per this phase's own constraints; CodeCompass
  is used here only as routine infrastructure (§1), not as the subject.

## 15. Documentation changes required (once implementation is approved and lands)

- `dev-docs/api-spec.md` — `QueryNode` Union, new `Tag` node, and (if
  Option A) `matches_transaction`/`matches_posting`'s new signatures.
- `dev-docs/hledger-compatibility.md` — the `tag:NAME[=REGEX]` Query
  Language row (currently "Not implemented"), and §9.2's `accounts`
  decision if divergent.
- `dev-docs/architecture.md` — `ledgerkit/query/` subpackage description,
  if `effective_tags`/inheritance logic is added to `ledgerkit/tags.py`;
  **new this amendment**: `ledgerkit/parser.py`'s `commodity` directive
  handling, if the commodity-tag substrate work lands.
- `dev-docs/hledger-compatibility.md` — **new this amendment**: the
  "Commodity tags" behaviour (§2.6) needs its own documented row/section,
  the same treatment the existing Tags section already gives account-
  directive tags.
- `docs/usage.md` — user-facing `-q "tag:..."` examples, mirroring the
  existing `depth:` examples added in Stage C Phase 5.
- `knowledge/DECISIONS.md` — whichever of §9.1/§9.2's options gets
  approved, with the rejected alternative and why, matching every prior
  phase's decision-recording convention.
- `knowledge/DOMAIN_RULES.md` — the four inheritance rules (§2.2), the
  AND-not-OR combination rule (§2.3), **new this amendment**: commodity-
  tag propagation (§2.6) and the union-not-shadowing same-name precedence
  finding (§2.7 — the single most counter-intuitive rule in this
  feature, given the manual's own "override" wording reads the opposite
  way) — as tacit hledger rules Claude can't infer from code, same
  treatment `depth:`'s precedence rules got in Phase 5.
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the project's standing
  same-response doc-sync rule, at implementation time.

## 16. Proposed tests

- **Unit** (`tests/test_query/test_parser.py`,
  `tests/test_query/test_eval.py`): `tag:NAME` bare-value matching,
  `tag:NAME=REGEX` value matching, malformed-regex `QueryParseError`,
  empty-value matching, `not:tag:...` negation, multiple `tag:` terms
  AND-combining (§2.3, now with the executable precedent to encode as a
  regression test), **new this amendment**: `tag:rate==0.05`-shaped
  values preserving everything after the first `=` (§12), `tag:.=VALUE`
  value-only matching (§12).
- **Integration** (`tests/test_reports.py`,
  `tests/test_cli/test_cli.py`): `tag:` wired through `-q` for all five
  commands; §9.1's chosen inheritance behaviour exercised on a fixture
  with account-directive tags, transaction-header tags, posting-own
  tags, **and commodity-directive tags (new this amendment)** in
  combination (no existing fixture has any tags at all — a new fixture,
  or an extension of an existing one, is needed either way, confirmed by
  the curator's direct check of `filtered.journal`/`depth.journal`).
  **New this amendment, required coverage**:
  - commodity-directive tag propagation to postings using that
    commodity in their main amount (§2.6);
  - same-name/different-value precedence across **all** effective-tag
    source pairs (§2.7's full matrix): posting vs. account, posting vs.
    commodity, account vs. commodity, parent-account vs. child-account/
    posting, and a transaction-level tag combined with a same-named
    posting/account/commodity tag — each as its own named test case, not
    one combined fixture asserted loosely;
  - parent-account tag + commodity tag composing on the same posting
    (no existing test scenario covers two non-posting-own sources
    together);
  - exact hledger `accounts` semantics per §9.2's resolution and §2.5's
    corrected four-way finding — **four explicit, individually-named
    differential cases, not one combined assertion**: a transaction-
    level tag is **visible** to plain `accounts tag:X`; an account-
    inherited tag is **visible**; a posting-own tag is **not visible**;
    a commodity-propagated tag is **not visible**. All four on the same
    shared fixture, so a regression in any one is individually
    attributable.
- **Differential** (against the pinned hledger binary, via a genuinely
  separate `compat-differential-tester` dispatch per §10 — **mandatory
  before any of these compatibility claims are first promoted to
  `verified`**, restated per this amendment's own instruction): reproduce
  every scenario in §2 (basic matching, all four inheritance rules if
  Option A, the AND-not-OR combination, the full §2.7 precedence matrix,
  the `accounts` mode per §9.2's resolution) — the curator's own scratch
  fixture (`tag-verify.journal`) and this amendment's own precedence
  fixture (`/tmp/tagverify/precedence.journal`, both session-local, not
  committed) are good starting points for what a committed `tests/
  fixtures/` equivalent should cover.

## 17. Summary of what needs explicit approval (Step 3 gate) — revised this pass

1. **§9.1** — inheritance scope: Option A (**complete** four-source
   compatibility — posting, transaction, account-inherited, **and
   commodity-propagated**) vs. Option B (own-tags-only, disclosed
   divergence, now covering two missing sources instead of one). Lead
   recommends A.
2. **§9.1** — evaluator API shape for whatever context `tag:` matching
   needs. **Wording corrected this pass**: not "keyword-only with no
   default" (that would still be mandatory on every call, a Python
   fact the prior wording got wrong) — the real candidates are
   `journal: Journal | None = None` (a genuine default, with `Tag`
   evaluation failing explicitly, not silently, when `journal` is
   absent and actually needed), a context object, or pre-materialised
   storage. Left as an implementation-planning-stage choice; "fail
   loudly, never silently narrow" remains a binding constraint on
   whichever shape is chosen.
3. **§9.2** — `accounts` command mode: replicate hledger's mode
   (transaction-level and account-inherited tags visible; posting-own
   and commodity-propagated tags not visible — the precise four-way
   split corrected this pass) vs. uniform matching. Lead recommends
   replication, unless implementation planning finds a concrete
   technical reason not to.
4. **§16** — the expanded differential-test matrix (five same-name/
   different-value precedence pairs, commodity-tag propagation, the
   `accounts`-mode four-way split) is the proposed basis for the
   mandatory independent `compat-differential-tester` verification
   (§10) — approval of 1 and 3 above implicitly approves this matrix as
   its verification plan, not a separate decision.
5. **General approval** to proceed to Step 4 (implementation planning)
   once 1 and 3 are resolved.

**Resolved this pass, no longer part of the approval list**: the
commodity-tag substrate's scope (§9.1) — decided **in scope for this
phase**, design-approved but not implemented; the effective-tags helper
API shape (§9.3) — **private by default**, not a blocking gate.

No implementation begins until this section's items are explicitly
decided.

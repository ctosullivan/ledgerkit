# 27. `Query`-as-compatibility-shim convergence — design document

Design document for Stage C's next backlog item (`dev-docs/retros/
STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` Addendum 2, item 2; Stage
C's own charter row names "CLI/report routing" as in-scope): converging
the legacy `ledgerkit.models.Query` dataclass onto the `ledgerkit.query`
AST/evaluator, eliminating the second, parallel, non-hledger-faithful
matching path that has existed alongside it since Stage C Phase 1.
**Not an implementation plan.** No `ledgerkit/`/`tests/` code touched
producing this document. Same provenance discipline as prior design
documents: **[VERIFIED-EXTERNAL]** (confirmed by direct read of the
actual source/docs cited) / **[EXISTING-DECISION]** (already approved
elsewhere) / **[PROPOSED]** / **[UNRESOLVED]**.

**Amendment 2 (2026-09-26, same day, after Amendment 1 below): a final
targeted design-correction pass, not a re-scope.** The approved
architectural direction is unchanged throughout: `Query` converges onto
the canonical AST/evaluator, Option A is still recommended, field
shape/signatures stay frozen, `Query.depth` stays non-predicate,
`Query.date_to`'s inclusive-to-exclusive translation (including the
`date.max` case) is unchanged, the translator stays in `ledgerkit/
query/compat.py`, and the `stats` correction/`ReportSection` non-goal
both stand as Amendment 1 left them. Six further corrections, all found
by checking every `Query` consumer directly rather than trusting the
prior pass's own completeness claim: (1) `balance_from_spec`'s **outer**
`query.payee`/`.account`/`.not_account` — previously left on
`_matches_pattern` in Amendment 1 — now converge onto `_query_to_ast` +
`ledgerkit.query.eval.matches_posting`, the same canonical path
`balance`/`register`/`accounts`/`stats` use; `_matches_pattern` is
retained **only** for `ReportSection.accounts`/`.exclude`, the one
genuinely separate, deliberately out-of-scope construct (§5.1b,
rewritten). (2) `Journal.to_dataframe(query=...)` — missed entirely by
both prior passes — imports and calls `_posting_matches` directly
(`models.py:456,461`); it must migrate to `_query_to_ast` +
`matches_posting` too, or retiring `_posting_matches` (as both prior
passes proposed) would break it outright (§5.1d, new). (3) The
deprecated `accounts=[...]` shim's three real cases — zero, one, many —
were not all handled: `accounts=[]` would have produced `Or(())`, an
empty OR, which evaluates to **matching nothing**, not "no filter" —
the opposite of today's behaviour; explicit zero/one/many handling is
now specified, with the escaped literals in the many-account case
routed through the same eager-validation helper as everything else
(§5.1a, corrected). (4) §5.2's claim of "no observable change beyond
regex strictness" was no longer accurate once (1)-(3) are accounted
for — replaced with an explicit, complete list of every intentional
behavioural change this phase makes. (5) A new §5.3 gives the complete
public-path inventory this design was missing — all seven `Query`
consumers, and exactly how each reaches the canonical translator/
evaluator, so no future pass has to re-derive completeness by grepping
direct `Query(...)` construction again. (6) The approval gate (§12) is
reduced to the actual remaining human decisions, each with the
recommended choice stated explicitly.

**Amendment 1 (2026-09-26, earlier the same day): a targeted design-correction pass,
not a re-scope.** The core decision is unchanged — `Query` converges
onto the canonical `ledgerkit.query` AST/evaluator, Option A (full
`HledgerRegex` strictness) is still recommended, `Query`'s field shape/
report-function signatures stay unchanged, `Query.depth` stays a
report/display option (never a predicate), and the inclusive-`date_to`-
to-exclusive-`DateSpan.end` translation is preserved. Eight corrections,
all found before any code was written: (1) the deprecated `Journal.
balance(accounts=[...])`/`register(accounts=[...])` multi-account path
synthesizes a `Query.account` pattern using `(?:...)` non-capturing
groups, which `HledgerRegex` rejects — the original blast-radius claim
that no code path uses an excluded construct was **false**, missed
because it only checked direct `Query(...)` test construction, not this
deprecated wrapper's own internal synthesis; redesigned (§5.1a) to
construct an `Or(...)` AST directly instead of a synthesized regex
string, with new required tests. (2) The proposed translator
constructed `Acct(...)`/`Desc(...)` directly without validating first —
AST nodes don't self-validate; fixed to call `compile_hledger_regex`
explicitly before constructing any node, matching `_build_acct`'s own
eager-validation pattern (§5.1). (3) `balance_from_spec()`'s own,
separate inline filtering (`ReportSection.accounts`/`.exclude`, a
public dataclass) still needs `_matches_pattern` — it is **not**
retired, it is refactored in place to be `HledgerRegex`-backed instead
of the ad hoc Python-regex heuristic (§5.1b), with the chosen scope
stated explicitly (full `ReportSpec`/`ReportSection` AST convergence is
a named non-goal, §7). (4) `stats(query=...)` currently silently
ignores `query.account`/`.not_account` entirely (a pre-existing,
documented `TODO`) — full convergence fixes this as an intentional,
disclosed behavioural correction, not an incidental side effect (§5.1c,
with before/after semantics and a required test). (5) The translator
moves to a new `ledgerkit/query/compat.py` module, not `models.py` —
`ledgerkit/query/eval.py` already imports from `models.py`, so the
reverse import would be circular (§5.1). (6) `Query.date_to +
timedelta(days=1)` overflows for `datetime.date.max` — a safe
translation is specified and tested (§5.1). (7) The blast-radius wording
is corrected from "empty"/effectively-zero to the narrower, actually-
verified conclusion: no known *external* consumer relies on the old
matching semantics, but existing *internal/public* compatibility paths
(the deprecated `accounts=[...]` shim, `ReportSection`, `stats`) needed
explicit migration handling, not a free pass (§3/§8, corrected). (8)
Status hygiene: Stage C Phase 7 is implementation-and-independent-
verification complete, not formally `[DONE]` — this document did not
claim otherwise, but the point is restated here since it was raised
explicitly.

## 0. Pinned revisions

Ledgerkit: `afbcd05`. Stage C Phase 7 is implementation-and-independent-
verification complete (`dev-docs/retros/STAGE-C-PHASE-7-EMPTY-REGEX-
IMPLEMENTATION.md`); it has **not** been marked `[DONE]` in `ROADMAP.md`
— that remains the user's own call, per the project's standing rule,
and this document does not assume or depend on it either way.

## 1. Process note

This phase is **executing an already-approved architectural plan**, not
deciding a new direction. `dev-docs/planning/core-redefinition/
07-query-regex.md` §7.2 (written at Core-redefinition planning time,
before Stage C began) states plainly: *"The existing `Query` dataclass
becomes a compatibility constructor that compiles to a `QueryAST`...
rather than a parallel filtering path."* `06-core-architecture.md` §6.5
independently commits to the compatibility contract this must preserve.
No fresh `context-curator`/`hledger-researcher` dispatch was made for
this document — the target semantics (`ledgerkit.query`'s AST/parser/
evaluator) are an already-implemented, already-differential-verified
subsystem (Stage C Phases 1-7); this phase's actual open questions are
Ledgerkit-internal architecture and backward-compatibility questions,
not new hledger-behaviour research, so the lead performed the source/
docs audit directly (mirroring how Stage C Phase 5's `depth:` redesign
scoping worked) rather than dispatching a role whose charter doesn't
fit this kind of work (a lesson from Phase 7's own misdirected
`context-curator` dispatch, `STAGE-C-PHASE-7-EMPTY-REGEX-PLAN.md`'s
addendum).

## 2. Current state — [VERIFIED-EXTERNAL, direct source read]

Two independent, parallel filtering mechanisms currently coexist in
`ledgerkit/reports.py`, both consulted (AND'd together) when both are
supplied to a report function:

- **`Query`** (`ledgerkit/models.py:127-146`) — a flat dataclass
  (`account`, `not_account`, `payee`, `date_from`, `date_to`, `depth`,
  all `str | None`/`int | None`/`date | None`). Evaluated by `reports.
  py`'s own `_posting_matches`/`_matches_pattern`
  (`reports.py:231-276`) — a **from-scratch, ad hoc** matcher: any
  string containing a Python-regex metacharacter (`_REGEX_META`,
  `reports.py:228`) is compiled and matched with raw Python `re.search`
  (no `HledgerRegex`-subset validation at all — Perl classes,
  lookaround, backreferences, and every other construct `ledgerkit.
  query.regex` deliberately excludes all "work" here, interpreted by
  Python semantics, which is exactly the silent-divergence risk that
  module exists to prevent); anything else is a plain case-insensitive
  substring check.
- **`QueryNode`/`QueryPlan`** (`ledgerkit/query/`) — the hledger-
  faithful AST + parser + evaluator built across Stage C Phases 1-7,
  reached only via the CLI's private `_query_ast`/`_query_depth`
  parameters (`reports.py`'s `accounts`/`balance`/`register`/`stats`,
  each documented "Private, internal-only filter"). Every regex here is
  validated against the real `HledgerRegex` subset (`ledgerkit.query.
  regex.compile_hledger_regex`) and, since Stage C Phase 7, rejects an
  empty pattern exactly as real hledger does.

`Query.depth` is the one field already unified in spirit — it's mapped
to `DepthSpec(flat=query.depth)` by `_effective_depth_spec`
(`reports.py:279-292`), the same `DepthSpec` type `-q "depth:N"` also
produces. `Query`'s other five fields have no such convergence.

**Two further, easy-to-miss surfaces this design must also account
for, corrected this pass (both found by direct source read, not
assumed away):**

- **The deprecated multi-account shim.** `ledgerkit.models.Journal.
  balance`/`.register` (`models.py:382-432`) accept a legacy `accounts:
  list[str] | None` parameter that, when `len(accounts) > 1`,
  synthesizes `Query(account="|".join(f"(?:{re.escape(a)})" for a in
  accounts))` — a pattern using `(?:...)` non-capturing groups.
  `HledgerRegex`'s `_EXCLUDED_CONSTRUCT` rejects **any** `(?...)`
  construct (`ledgerkit/query/regex.py:84`, `paren_special`), so once
  `Query.account` routes through `compile_hledger_regex` (§6, Option A),
  calling `Journal.balance(accounts=["a", "b"])` — **two or more**
  accounts — would raise, a real regression this design must not ship.
  **No existing test exercises this two-or-more-accounts path at all**
  (confirmed by grep — only the single-account and unrelated
  `_make_journal(accounts=...)` test-helper forms appear anywhere in
  `tests/`), which is exactly why the original blast-radius claim (§8)
  missed it: it checked direct `Query(...)` construction in tests, not
  this wrapper's own internal string synthesis. See §5.1a.
- **`balance_from_spec`'s own, separate inline filter.** `reports.
  balance_from_spec` (`reports.py:612-694`) does **not** go through
  `_posting_matches` at all — it has its own hand-rolled loop calling
  `_matches_pattern` directly, five times: once each for the outer
  `query.payee`/`query.account`/`query.not_account`, and once each for
  `ReportSection.accounts`/`.exclude` (`models.py:198-215`, a public
  dataclass with its own OR/exclude pattern-matching semantics,
  independent of `Query`). Retiring `_matches_pattern` outright, as an
  earlier version of this design implied, would break this live,
  public-API code path. See §5.1b.
- **`stats(query=...)`'s existing gap.** `reports.stats` (`reports.py:
  516-610`) already only applies `query.date_from`/`.date_to`/`.payee`
  to its transaction subset (`reports.py:559-566`) — `query.account`/
  `.not_account` are silently ignored, a pre-existing, already-
  documented gap (`reports.py:547-549`'s own docstring note and inline
  `# TODO: Apply account/not_account query filters...`). Full
  convergence closes this gap as a side effect, which must be treated
  as an intentional, disclosed behavioural correction, not an
  incidental one. See §5.1c.

## 3. External-consumer analysis — [VERIFIED-EXTERNAL, the single most de-risking fact]

`dev-docs/planning/core-redefinition/15-editor-compat-inventory.md`
(Stage B Phase 1, an independent import-inventory audit) confirms
`ledgerkit-editor` — the one known, real external consumer of
`ledgerkit.Query` — constructs `Query(account=..., payee=..., date_
from=..., date_to=...)` **as a plain data container** and passes it to
**its own** `query_match.build_transaction_predicate()` — **never to
any `ledgerkit` report function**. `ledgerkit-editor` does not call
`balance`/`register`/`accounts`/`stats`/`to_dataframe` with a `Query`
at all; it re-implements its own matching logic independently
(`06-core-architecture.md` §6.5's own citation of this, and
`15-editor-compat-inventory.md` §15.2's note that `ledgerkit-editor`
"deliberately avoids importing `reports`'s private matching helpers").

**This means the frozen v1 API commitment (`06-core-architecture.md`
§6.5: "`Query`'s `account`/`payee`/`date_from`/`date_to` constructor
shape... frozen v1 API surface") is a commitment about the
**dataclass's field shape**, not about `reports.py`'s internal
matching algorithm.** No known external consumer depends on exactly
how `_posting_matches`/`_matches_pattern` evaluates a `Query` — the one
real consumer never reaches that code at all.

**Blast-radius wording corrected this pass**: the original version of
this document characterised this as an "empty" or effectively-zero
blast radius. That overstated it. The accurate, narrower conclusion,
per §2's two further surfaces found this pass: **no known external
consumer relies on the old report-matching semantics** — that part
holds — **but Ledgerkit's own internal/public compatibility paths
(the deprecated `accounts=[...]` multi-account shim, `ReportSection`'s
own matching, `stats`'s existing account-filter gap) are not
automatically safe and each require explicit migration handling**,
worked through in §5.1a/§5.1b/§5.1c respectively, not a free pass on
the strength of the external-consumer finding alone. The de-risking
fact in this section remains real and load-bearing for the *external*
compatibility question; it was never evidence about Ledgerkit's own
internal call sites, and this document should not have implied it was.

## 4. Existing decisions this design must respect — [EXISTING-DECISION]

- `07-query-regex.md` §7.2: `Query` becomes "a compatibility
  constructor that compiles to a `QueryAST`... No report function
  embeds its own filtering logic" (the end state this phase works
  toward — a pre-existing, approved design target, not new scope).
- `06-core-architecture.md` §6.5: `Query`'s constructor shape
  (`account`/`payee`/`date_from`/`date_to`, plus `not_account`/`depth`
  which that section doesn't enumerate but which are part of the same
  frozen dataclass) is frozen v1 API — this phase must not add, remove,
  or retype any field, and must not change `Query()`'s "no filter"
  semantics.
- `ledgerkit.query.ast.DateSpan.end` is **exclusive** (`ledgerkit/
  query/ast.py:68-79`), deliberately different from `Query.date_to`,
  which is **inclusive** (`ledgerkit/models.py:145`, `dev-docs/
  hledger-compatibility.md:246`) — matching hledger's own real `date:`
  span semantics, which `Query.date_to` predates and does not follow.
  **A naive `Query.date_to` → `DateSpan(end=query.date_to)` translation
  would silently exclude transactions dated exactly `query.date_to`,
  a real behaviour regression** — the correct translation adds one day
  (`DateSpan(end=query.date_to + timedelta(days=1))`), **except at
  `datetime.date.max`, corrected this pass**, where adding a day
  overflows (`9999-12-31` has no representable successor) — see §5.1a's
  `_exclusive_end` for the safe version. Flagged here explicitly because
  it is the single easiest correctness trap in this entire phase and the
  design must not leave it implicit.
- Stage C Phase 5's `depth:` redesign: `depth` is never a selection
  predicate (`_posting_matches`'s own docstring already says so) —
  `Query.depth`'s existing `DepthSpec(flat=...)` mapping is already
  correct and must not be folded into the `QueryNode`/`And(...)`
  predicate tree at all.
- The `Not` wrapper and AND/OR combination rules (Stage C Phase 1-6,
  `ledgerkit/query/parser.py`): a negated term always AND-combines,
  never joins a same-prefix OR bucket — relevant because `Query.
  not_account` and `Query.account` being simultaneously set must
  AND-combine (`Query(account="food", not_account="restaurant")` means
  "matches `food` AND does not match `restaurant`"), which `And((Acct
  ("food"), Not(Acct("restaurant"))))` already produces correctly by
  construction, requiring no new combination logic.

## 5. Proposed design — [PROPOSED]

### 5.1 A private translation module — `ledgerkit/query/compat.py`, not `models.py`

**Module placement corrected this pass.** The original proposal left
this to "implementer's call," suggesting `models.py` as one option.
That option is wrong: `ledgerkit/query/eval.py` already imports `from
ledgerkit.models import Journal, Posting, Transaction`
(`eval.py:31`) — if `models.py` imported the translator's dependencies
(`ledgerkit.query.ast`'s node types) at module level, that would be a
genuine circular import (`models.py` → `query/ast.py` and, transitively
if `compat.py` needs it, `query/regex.py`; `query/eval.py` → `models.
py`). The translator instead lives in a **new module**, `ledgerkit/
query/compat.py` (inside the `query` package, which already owns every
other AST-adjacent concern) — it imports freely from `ledgerkit.query.
ast`/`ledgerkit.query.regex`/`ledgerkit.query.depth` with no circularity
risk, since nothing in `ledgerkit/query/` needs to import `compat.py`
itself. `ledgerkit/models.py`'s own `Journal.balance`/`.register` and
`ledgerkit/reports.py` reach it via a **lazy, in-function import**
(`from ledgerkit.query.compat import _query_to_ast`), exactly mirroring
the existing lazy-import pattern `models.py`'s own methods already use
to reach `reports.py` (`models.py:378-379`'s own comment: "Lazy imports
are used to avoid a circular dependency").

### 5.1a The translator itself — with explicit validation, not bare node construction

**Validation gap corrected this pass.** The original proposal
constructed `Acct(query.account)`/`Desc(query.payee)` directly. AST
node dataclasses (`ledgerkit/query/ast.py`) do **no** validation of
their own — every existing parser rule (`_build_acct`/`_build_desc`/
`_build_tag`, `ledgerkit/query/parser.py`) calls `compile_hledger_regex`
**explicitly, before** constructing the node, precisely so a bad
pattern fails at translation/parse time, deterministically, regardless
of what data it's later evaluated against — not only if and when
`ledgerkit.query.eval`'s own lazily-`lru_cache`d `_compiled` happens to
be reached during evaluation (which, for an empty journal or a query
whose predicate is never actually exercised, might never happen at
all, silently masking an invalid pattern instead of raising it). The
translator must reproduce that same eager-validation discipline:

```python
# ledgerkit/query/compat.py
import datetime

from ledgerkit.query.ast import Acct, And, DateSpan, Desc, Not, QueryNode
from ledgerkit.query.parser import QueryParseError
from ledgerkit.query.regex import compile_hledger_regex
import re


def _validated(prefix: str, pattern: str) -> str:
    """Validate `pattern` eagerly, raising QueryParseError (not a bare
    ValueError/re.error) on failure -- mirrors _build_acct/_build_desc's
    own parse-time-validation contract (ledgerkit/query/parser.py), so a
    Query field behaves identically to the equivalent -q string term."""
    try:
        compile_hledger_regex(pattern)
    except (ValueError, re.error) as exc:
        raise QueryParseError(f"{prefix}: {exc}") from exc
    return pattern


def _query_to_ast(query: "Query | None") -> QueryNode | None:
    if query is None:
        return None
    terms: list[QueryNode] = []
    if query.account is not None:
        terms.append(Acct(_validated("account", query.account)))
    if query.not_account is not None:
        terms.append(Not(Acct(_validated("not_account", query.not_account))))
    if query.payee is not None:
        terms.append(Desc(_validated("payee", query.payee)))
    if query.date_from is not None or query.date_to is not None:
        terms.append(DateSpan(start=query.date_from, end=_exclusive_end(query.date_to)))
    if not terms:
        return None
    return terms[0] if len(terms) == 1 else And(tuple(terms))
    # query.depth is deliberately excluded -- never a predicate (§4).
```

(`Query`'s own type is quoted here only to avoid a hard top-level
import of `models.py` from `query/compat.py`, matching the "avoid
circularity" goal of §5.1 itself — implementer's call whether a
`TYPE_CHECKING`-guarded import or a plain runtime import from `models`
is cleaner in practice, since `models.py` does not import `query/
compat.py` at module level either way, so a one-directional runtime
import from `compat.py` → `models.py` is not actually circular, only
the reverse would be; noted here so the implementer doesn't have to
re-derive which direction is actually safe.)

`_exclusive_end` (also in `ledgerkit/query/compat.py`) does the
inclusive-to-exclusive translation §4 already flags as the single
easiest correctness trap in this phase — **with the `date.max` overflow
corrected this pass**, since a naive `query.date_to + timedelta(days=1)`
raises `OverflowError` for `datetime.date.max` (`9999-12-31` — there is
no representable day after it):

```python
def _exclusive_end(date_to: datetime.date | None) -> datetime.date | None:
    """Query.date_to is inclusive; DateSpan.end is exclusive (§4). Adding
    one day makes the translation faithful -- except at datetime.date.max,
    which has no representable successor. date.max as an inclusive upper
    bound already means "no upper bound in practice" (nothing sorts after
    it), so it maps to DateSpan's own "unbounded" representation (end=None)
    rather than overflowing."""
    if date_to is None:
        return None
    if date_to == datetime.date.max:
        return None
    return date_to + datetime.timedelta(days=1)
```

**Required test** (§11): `Query(date_to=datetime.date.max)` must not
raise `OverflowError`, and must still match a transaction dated
`datetime.date.max` (the inclusive-semantics regression guard,
extended to this specific edge case rather than assumed covered by the
ordinary-date version of the same test).

Reusing `QueryParseError` (already public, already exported, already
the exception every `-q` string-term validation failure raises) rather
than inventing a new exception type is **[PROPOSED]**, not a blocking
fork — flagged in §12 for awareness, since it does mean a `Query`
field's invalid regex now raises a "parse" error despite no query
*string* being involved; the alternative (a new, `Query`-specific
exception) was considered and rejected as needless surface for the same
underlying condition Stage C Phase 7 already reuses one exception type
for (`UnsupportedRegexConstructError`).

`_posting_matches` and the ad hoc `_REGEX_META` construct-sniffing
(`reports.py:215-230`, `243-276`) are retired — `balance`/`register`/
`accounts`/`stats`'s existing `query: Query | None` parameter is
translated once via `_query_to_ast` and evaluated through the **same**
`ledgerkit.query.eval` engine `_query_ast` already uses, combined
(AND'd) with any `_query_ast` also supplied. **`_matches_pattern` is
NOT retired** — see §5.1b, it has a live, separate caller.

### 5.1a (continued) — the deprecated multi-account shim, corrected (Amendment 2: all three cases handled explicitly)

**Real regression found and fixed in Amendment 1** (§2): `Journal.
balance`/`.register`'s `accounts: list[str] | None` parameter, for
`len(accounts) > 1`, must stop synthesizing a `Query.account` string via
`(?:...)` non-capturing-group alternation (`HledgerRegex`-excluded).
**A second real bug in Amendment 1's own fix, found and fixed this
pass**: that version only distinguished "one account" from "more than
one," silently falling through to the many-account `Or(...)` branch for
**zero** accounts too — `Or(tuple(Acct(...) for a in []))` is `Or(())`,
an **empty** `Or` node. `ledgerkit.query.eval`'s `Or` evaluation is
`any(...)` over its terms; `any(())` is `False` — an empty `Or` matches
**nothing**, the exact opposite of `accounts=[]`'s intended "no filter"
behaviour (today, `accounts=[]` reaches `"|".join(... for a in [])` →
`""` → `Query(account="")`, which `_matches_pattern`'s old permissive
handling treats as "matches everything" — a real behaviour today,
reached only by accident of `_matches_pattern`'s specific empty-string
handling, not by design, but real all the same and not to be broken).
All three cases are now handled explicitly, not left to an implicit
`len() == 1` vs. "else":

```python
# ledgerkit/models.py, inside Journal.balance()/register() (lazy import,
# matching the existing pattern at the top of this class):
from ledgerkit.query.ast import Acct, Or
from ledgerkit.query.compat import _validated
import re as _re

if accounts is not None and query is None:
    if len(accounts) == 0:
        pass  # No accounts given -- preserve today's effective
              # no-filter behaviour explicitly. Do NOT fall through to
              # the Or(...) branch below: Or(()) matches nothing, the
              # opposite of "no filter" (the bug this pass fixes).
              # query and _query_ast both stay unset/None.
    elif len(accounts) == 1:
        query = Query(account=accounts[0])   # unchanged: single-account
                                              # case stays a raw,
                                              # unescaped passthrough,
                                              # exactly today's behaviour
                                              # -- still a real regex
                                              # pattern, now HledgerRegex-
                                              # validated via §5.1a's
                                              # translator like any other
                                              # Query.account value.
    else:
        terms = tuple(
            Acct(_validated("account", _re.escape(a))) for a in accounts
        )
        return _balance(self, query=None, _query_ast=Or(terms), tree=tree)
```

`re.escape(a)` for an ordinary account name (letters, digits, `:`)
produces the name unchanged in Python 3.7+ (`:` is not a regex
metacharacter) — and for any account name that *does* contain a real
regex metacharacter, the escaped form (e.g. `\.`) is itself
`HledgerRegex`-portable (plain backslash-escaped literals are not in
`_EXCLUDED_CONSTRUCT`'s exclusion list). **Explicitly validated via
`_validated` anyway, not assumed safe** — per the standing invariant
this pass establishes project-wide (§5.1a above, §5.1d below): an AST
node must never be constructed from unvalidated regex text, even when
the text's safety is independently reasoned about elsewhere; validating
eagerly here costs nothing and removes any dependence on that reasoning
staying correct forever. This bypasses `Query.account` entirely for the
multi-account case, reusing the already-existing private `_query_ast`
parameter instead of round-tripping through a synthesized string —
simpler and more obviously correct than re-deriving a `(?:...)`-free
string-joining scheme. `register()` gets the identical treatment.
**Required tests** (§11): all three cases — zero accounts (no filter,
not `Or(())`), one account (unchanged, still a raw regex passthrough),
and multiple accounts (now `Or`-based, not `(?:...)`-based).

### 5.1b `balance_from_spec`'s outer query converges too — `_matches_pattern` retained ONLY for `ReportSection` (rewritten, Amendment 2)

**Amendment 1's scope decision was itself incomplete, corrected this
pass.** Amendment 1 kept `_matches_pattern` alive for **all** of
`balance_from_spec`'s five call sites — its outer `query.payee`/
`.account`/`.not_account` check, *and* `ReportSection.accounts`/
`.exclude`. On review, only the second half of that is actually a
distinct construct with no `Query` equivalent; the first half is
exactly the same "translate a `Query` once, evaluate through the
canonical engine" convergence `balance`/`register`/`accounts`/`stats`
already get — leaving it on `_matches_pattern` was an unforced,
unnecessary exception, not a real scope boundary.

**Corrected design**: `balance_from_spec`'s **outer** `query` is
translated once via `_query_to_ast(query)` (§5.1a) and evaluated
per-posting through `ledgerkit.query.eval.matches_posting` — the exact
same call `reports.py` already imports as `_query_ast_matches_posting`
for `balance`/`register`/`accounts` — replacing its own inline
`query.date_from`/`.date_to`/`.payee`/`.account`/`.not_account` checks
entirely:

```python
# reports.py, balance_from_spec() — outer-query handling rewritten:
from ledgerkit.query.compat import _query_to_ast
from ledgerkit.query.eval import matches_posting as _query_ast_matches_posting  # already imported

_outer_ast = _query_to_ast(query)

for txn in journal.transactions:
    for posting in resolve_elision(txn):
        if _outer_ast is not None and not _query_ast_matches_posting(
            _outer_ast, txn, posting, journal=journal
        ):
            continue
        # ReportSection.accounts/.exclude: unchanged call sites, see below.
        if not any(_matches_pattern(pat, posting.account) for pat in section.accounts):
            continue
        if any(_matches_pattern(pat, posting.account) for pat in section.exclude):
            continue
        ...
```

(The per-transaction date short-circuit Amendment 1's version had —
skipping every posting of a transaction whose date already fails —
becomes a minor, harmless performance difference: `matches_posting`
re-checks the date predicate per posting instead of once per
transaction. Not a behaviour change, not required to preserve; noted
only so the implementer doesn't mistake the loss of that
micro-optimisation for a regression.)

`section.depth`/`query.depth` handling (the line reading `query.depth
if query is not None else None`) is **unchanged** — `depth` is still
read directly off the dataclass field, never routed through
`_query_to_ast`, consistent with §4's standing rule that `depth` is
never a predicate.

**`_matches_pattern` is retained — but now ONLY for `ReportSection.
accounts`/`.exclude`** (`models.py:198-215`), the one genuinely
separate construct with no `Query` equivalent at all (its own OR-
across-`accounts`/exclude-across-`exclude` combination semantics).
**Chosen scope, restated**: `_matches_pattern`'s *implementation* is
refactored to route through `compile_hledger_regex`/`.search()` instead
of the ad hoc `_REGEX_META` Python-native-regex heuristic (`reports.py:
215-228`) — its remaining call sites (`ReportSection.accounts`/
`.exclude` only, now that the outer-query call sites are gone) are
otherwise unchanged. This is genuinely the **only** deliberately
separate filtering construct left in Ledgerkit after this phase — every
other `Query`-shaped filter, everywhere, reaches the same canonical
engine (§5.3's full inventory). Full `ReportSpec`/`ReportSection` AST
convergence (redesigning its OR/exclude combination architecture into
`QueryNode`/`Or`/`Not` terms) remains a distinct, larger, not-yet-scoped
possible future item (§7) — `ReportSection` is a genuinely different
public surface from `Query` with its own combination semantics, not
something this phase's own approved scope covers.

Consequence, disclosed: `ReportSection.accounts`/`.exclude` now also
reject an excluded `HledgerRegex` construct and an empty pattern
(Stage C Phase 7's own rejection, inherited automatically once
`_matches_pattern` is `compile_hledger_regex`-backed) — the same
Option-A behaviour change as §6, extended to this construct by
construction, not by a separate decision. Listed explicitly in §5.2's
full change inventory.

### 5.1d `Journal.to_dataframe(query=...)` — migrated, not missed

**Found this pass, missed by both the original document and Amendment
1**: `ledgerkit.models.Journal.to_dataframe` (`models.py:444-473`)
imports `_posting_matches` directly (`from ledgerkit.reports import
_posting_matches`, `models.py:456`) and calls it once per posting
(`models.py:461`). Retiring `_posting_matches`, as both prior versions
of this design proposed, would break `to_dataframe` outright — a real,
live, public method (re-exported on `Journal`, documented, pandas-
optional).

**Corrected design**: `to_dataframe` migrates to the same pattern as
`balance`/`register`/`accounts`/`stats` — translate `query` once via
`_query_to_ast`, evaluate per posting via `matches_posting`:

```python
# ledgerkit/models.py, Journal.to_dataframe():
def to_dataframe(self, query: Query | None = None):
    ...
    from ledgerkit.query.compat import _query_to_ast
    from ledgerkit.query.eval import matches_posting
    _ast = _query_to_ast(query)
    styles = self.commodity_styles
    rows = []
    for txn in self.transactions:
        for p in txn.postings:
            if _ast is not None and not matches_posting(_ast, txn, p, journal=self):
                continue
            ...
```

`_posting_matches` itself (the wrapper, `reports.py:243-276` — distinct
from `_matches_pattern`, which §5.1b retains) is now retired
**everywhere** — `balance`/`register`/`accounts`/`stats` (§5.1a),
`balance_from_spec` (§5.1b), and `to_dataframe` (here) are its only
four callers, and all four converge onto `_query_to_ast`+`matches_
posting`/`matches_transaction` by the end of this phase. Confirmed no
fifth caller exists by grep (§5.3).

Existing dataframe filtering behaviour is preserved exactly for every
currently-valid `Query` — the same eager-validation-before-evaluation
guarantee `_query_to_ast` gives every other caller applies here too,
including against an empty journal (zero transactions) where the old
`_posting_matches`-based loop would never have run at all, silently
never validating anything.

### 5.1c `stats(query=...)` — closing the existing gap, explicitly

**Before** (current, `reports.py:559-566`): `stats(query=Query(
account=..., not_account=...))` silently ignores both fields — only
`date_from`/`date_to`/`payee` affect which transactions are counted
into `account_count`/`account_depth`/etc. Documented as a known gap
(`reports.py:547-549`'s own docstring, an inline `# TODO`).

**After** (once `stats` also calls `_query_to_ast(query)` and combines
it, AND'd, with any `_query_ast` — replacing its own current inline
`date`/`payee`-only check): `Query(account=X)` passed to `stats` now
means "count only transactions with at least one posting to an account
matching `X`" — via `Acct`'s existing `matches_transaction` semantics
("match if ANY posting in the transaction matches," `dev-docs/api-
spec.md`'s own documented rule, unchanged by this phase). This is
**identical** to what `-q "acct:X" stats` already does today via
`_query_ast` (`reports.py:567-568`) — full convergence does not invent
new `stats` behaviour, it makes the legacy `Query` path finally reach
behaviour the string-query path already has.

**This is an intentional, disclosed behavioural correction — not an
incidental side effect of the refactor.** It resolves the existing
`TODO` as a natural consequence of convergence, not as separate,
unscoped feature work. Requires: a before/after line in `dev-docs/
api-spec.md`'s `stats` entry and `dev-docs/hledger-compatibility.md`;
a dedicated, explicitly-named test (§11) confirming `stats(query=
Query(account=X))` now excludes transactions with no matching posting,
where before this phase it would not have.

### 5.2 Report function signatures unchanged — but the behaviour changes must be stated in full, not minimised (corrected, Amendment 2)

**Signatures**: `balance`/`register`/`accounts`/`stats`/`balance_from_
spec`/`to_dataframe`'s public signatures (`query: Query | None = None`)
are **not** proposed to change — only their internal implementation.
This keeps the change inside the Unauthorised Change Rule's safe zone
for `dev-docs/api-spec.md` (no signature to re-approve). The private
`_query_ast` parameter's own fate (kept as-is, or folded away now that
`Query` also compiles to the same AST type) is left to implementation
planning — not a design-level decision, since either choice is purely
internal.

**Behaviour, corrected this pass**: the original claim of "no
observable-from-outside change beyond the regex-strictness question"
was no longer accurate once §5.1b/§5.1c/§5.1d/§5.1a(zero-accounts) are
all accounted for — replaced here with the **complete, explicit list**
of every intentional behavioural change this phase makes, so none of
them is later discovered as an unexplained surprise:

1. **`Query.account`/`.not_account`/`.payee` become `HledgerRegex`-
   strict** (§6, Option A) — an excluded construct or an empty pattern
   now raises `QueryParseError`, where before it either "worked" via
   raw Python `re` semantics or (empty pattern) matched everything.
2. **`stats(query=Query(account=..., not_account=...))` now applies
   those filters** (§5.1c) — previously silently ignored; now excludes
   transactions with no matching posting, matching what `-q "acct:..."
   stats` already does.
3. **`ReportSection.accounts`/`.exclude` become `HledgerRegex`-
   validated** (§5.1b) — via the same retained-but-refactored
   `_matches_pattern`; an excluded construct or empty pattern here now
   raises too, where before it used the same permissive Python-regex
   fallback `Query`'s fields used to.
4. **`balance_from_spec`'s outer `query.account`/`.not_account`/
   `.payee` now evaluate through the canonical engine** (§5.1b) — same
   `HledgerRegex`-strictness consequence as point 1, extended to this
   call site.
5. **`Journal.to_dataframe(query=...)` now evaluates through the
   canonical engine** (§5.1d) — same consequence as point 1, extended
   to this call site; existing valid filters keep producing the same
   rows.
6. **The deprecated `Journal.balance`/`.register(accounts=[...])`
   wrapper's *internal* mechanism changes** (§5.1a) — `accounts=[]`
   stays "no filter," a single account stays a raw regex passthrough
   (now `HledgerRegex`-validated, point 1's consequence), and two-or-
   more accounts now builds an `Or(...)` AST instead of a `(?:...)`-
   based string. **Public behaviour is preserved** for every input this
   wrapper could previously accept without raising (per §5.3's
   inventory) — the wrapper's own public signature and its "no filter
   for `[]`, regex-passthrough for one, OR-of-literals for many"
   contract are unchanged; only its internal `(?:...)`-based mechanism,
   which was never itself part of any documented contract, changes.

None of these six are incidental side effects — each is named,
disclosed, and has a required test (§11) and a compat-register
`reason:` line (§9).

### 5.3 Complete public-path inventory — every `Query` consumer accounted for (new, Amendment 2)

**Both prior versions of this document made completeness claims based
on grepping direct `Query(...)` construction in `tests/` — never on an
actual inventory of every function that *accepts* a `Query`.** That gap
is exactly what produced §2's/§5.1a's/§5.1d's missed cases. This section
is the actual inventory, built by grepping every `query: Query` /
`accounts:` parameter across `ledgerkit/models.py`/`ledgerkit/
reports.py`, not by re-deriving it from test usage:

| Consumer | Reaches canonical engine via | Section |
|---|---|---|
| `reports.balance` | `_query_to_ast(query)` → `matches_posting`, AND'd with any `_query_ast` | §5.1a |
| `reports.register` | same as `balance` | §5.1a |
| `reports.accounts` | same as `balance` (plus its own narrower `_accounts_effective_tags`-style dispatch for `Tag` nodes, unrelated to this phase) | §5.1a |
| `reports.stats` | `_query_to_ast(query)` → `matches_transaction`, AND'd with any `_query_ast` (**new** — previously only `date`/`payee` via inline check) | §5.1c |
| `reports.balance_from_spec` | outer `query` → `_query_to_ast` → `matches_posting` (**new** — previously `_matches_pattern` inline); `ReportSection.accounts`/`.exclude` → refactored `_matches_pattern` (**the one retained, deliberately separate construct**) | §5.1b |
| `Journal.to_dataframe` | `_query_to_ast(query)` → `matches_posting` (**new** — previously `_posting_matches` directly) | §5.1d |
| `Journal.balance`/`.register`'s deprecated `accounts=[...]` wrapper | zero → no filter; one → `Query(account=...)` → same path as `balance`/`register` above; many → direct `Or(Acct(...))` AST via `_query_ast`, bypassing `Query` entirely | §5.1a |

**Every** `Query`-shaped filtering path in `ledgerkit/` reaches either
`ledgerkit.query.eval.matches_posting`/`matches_transaction` directly,
or (for `ReportSection` only) the retained, refactored, canonically-
`HledgerRegex`-backed `_matches_pattern` — there is no eighth path.
`_posting_matches` (the old `Query`-specific wrapper around
`_matches_pattern`, distinct from `_matches_pattern` itself) has
exactly **four** call sites, confirmed by grep, not assumed: one each
in `accounts`/`balance`/`register` (`reports.py:384,442,499` — each
its own separate call site, one per function) and one in `to_dataframe`
(`models.py:461`). `stats` never called it (its own inline `date`/
`payee`-only check, §5.1c). All four convert to `_query_to_ast`/
`matches_posting` by the end of this phase, so `_posting_matches` is
fully retired, with nothing left calling it.

## 6. [UNRESOLVED] Regex strictness for `Query`'s string fields

This is the one real behavioural fork this phase must resolve
explicitly, and the reason this document stops for approval rather than
being implemented directly.

**Option A — full convergence, `HledgerRegex`-strict.** `Query.
account`/`not_account`/`payee` route through `compile_hledger_regex`
exactly like `acct:`/`desc:` already do — same excluded-construct list,
same Stage C Phase 7 empty-pattern rejection. A `Query.account` value
using a Python-only construct (`\d+`, a lookahead, a named group) that
"worked" under the old ad hoc matcher (interpreted by raw Python `re`,
diverging from what real hledger would do with that same text) now
raises. **This is the option `07-query-regex.md` §7.2's original design
actually specifies** — "no report function embeds its own filtering
logic" leaves no room for a second, more permissive regex dialect
living on inside `Query`'s own path. Cost: a real, disclosed, breaking
behaviour change — contained to no known **external** consumer (§3),
with every internal path this affects (direct `Query(...)` test
construction, the deprecated `accounts=[...]` shim, `ReportSection`,
`stats`) explicitly worked through in §5.1a/§5.1b/§5.1c, not assumed
away (§8's corrected blast-radius conclusion).

**Option B — permissive fallback preserved.** `Query`'s fields keep
using `_matches_pattern`'s current raw-Python-regex behaviour, and only
`_query_ast`'s own string-query path gets `HledgerRegex` strictness.
This avoids any behaviour change to `Query` at all, but **directly
contradicts §7.2's own "no parallel filtering path" instruction** —
Ledgerkit would still have two different regex dialects active
depending on which entry point a caller uses for what is supposed to be
the same underlying concept (matching an account name), which is the
exact architectural debt this phase exists to remove.

**Lead's recommendation**: Option A. It's what the pre-approved design
actually specifies; no known external consumer is affected (§3); and
every internal path this touches has an explicit, worked-through
migration plan (§5.1a/§5.1b/§5.1c) rather than an assumed-clean blast
radius (§8, corrected). **Still not a decision** — explicit approval
required, since this is a real, user-facing (via `ledgerkit.Query`'s
public constructor) behaviour change to a documented public dataclass,
same category of decision as Stage C Phase 7's regex-rejection fix.

## 7. Explicit non-goals

- Changing `Query`'s dataclass fields, defaults, or `Query()`/`query=
  None` equivalence — frozen v1 API surface, out of scope entirely.
- `PythonRegex` extension syntax — separate, unstarted, unrelated
  Stage C backlog item (`26-query-regex-empty-pattern-design.md` §14's
  own non-goals list carries this forward).
- `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` (the `(|)` empty-alternation-
  branch divergence) — separate, unrelated, still open, untouched by
  this phase.
- `cur:`, smart/period dates, a standalone `--depth`/`-N` CLI flag —
  unrelated, already-tracked, unscoped Stage C follow-on items.
- Retiring `Query` itself, or discouraging its use — it remains the
  documented, frozen, first-class Python API for callers who prefer a
  typed dataclass over a query string; this phase changes what happens
  *behind* it, not its existence or role.
- `ledgerkit-editor`'s own `query_match.build_transaction_predicate()`
  — a separate codebase/module this phase has no reason to touch;
  confirmed (§3) it doesn't call into anything this phase changes.
- **New this pass**: redesigning `ReportSpec`/`ReportSection`'s own
  combination architecture (its OR-across-`accounts`/exclude-across-
  `exclude` semantics) into `QueryNode`/`Or`/`Not` AST terms. §5.1b's
  chosen scope converges its **regex dialect** (via a refactored
  `_matches_pattern`) but deliberately leaves its own control-flow/
  combination logic as `balance_from_spec`'s own hand-rolled loop — a
  distinct, larger, not-yet-scoped possible future item, since
  `ReportSection` is a different public surface from `Query` with its
  own semantics this phase's approved scope doesn't cover.
- **New this pass**: fixing `stats`'s `account_count`/`account_depth`
  fields to reflect a name-pattern restriction beyond what depth-
  exclusion already narrows (the field's own pre-existing docstring
  note, `reports.py:547-549`) beyond what §5.1c's convergence naturally
  produces — out of scope; §5.1c only closes the specific `Query.
  account`/`.not_account`-ignored-by-`stats` gap, nothing broader.

## 8. Blast-radius, corrected — [VERIFIED-EXTERNAL]

**Wording corrected this pass** (§3): the claim that Option A has an
"empty" or effectively-zero blast radius was too strong. The accurate,
narrower, still-verified conclusion:

- **No known external consumer** relies on the old report-matching
  semantics (§3 — `ledgerkit-editor` never reaches this code at all).
- **Ledgerkit's own direct `Query(...)` test constructions** are indeed
  clean: every `Query(...)` in `tests/test_reports.py`/`tests/test_
  dataframe.py` (full list, direct grep) uses either a plain substring
  (`"expenses"`, `"assets"`, `"income:salary"`, `"nonexistent:account"`,
  `"Supermarket"`, `"Coffee"`) or a `HledgerRegex`-portable anchor
  (`"^income"`) — none uses an excluded construct.
- **But this does not mean the blast radius is zero overall** — §2's
  two further surfaces (the deprecated `accounts=[...]` shim's `(?:...)`
  synthesis, `balance_from_spec`/`ReportSection`'s separate `_matches_
  pattern` reliance) and §5.1c's `stats` behaviour change are real,
  existing, internal/public compatibility paths that needed **explicit
  migration handling** — each worked through in §5.1a/§5.1b/§5.1c, not
  waved through on the strength of the clean direct-`Query(...)`-
  construction finding alone. That finding is real and still relevant
  (it's why Option A doesn't require rewriting any existing direct-
  `Query` test), it just isn't the whole picture, and this document
  should not have implied it was.

## 9. Compatibility implications

- New compat-register entries needed once implemented and independently
  verified: `LK-COMPAT-QUERY-SHIM-001` or similar (`area: query.shim`) —
  documents that `Query`'s fields now evaluate through the same
  `HledgerRegex`-validated, hledger-faithful engine `-q` uses, with the
  Option A behaviour-change disclosed explicitly in its `reason:` field
  (mirroring `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001`'s own disclosure
  style from Stage C Phase 7). Naming is **[PROPOSED]**, not blocking
  (§12).
- The `Query.date_to` inclusive-vs-`DateSpan.end`-exclusive translation
  (§4/§5.1a), **including the `date.max` edge case**, needs its own
  explicit regression tests and its own line in the new entry's
  `reason:` field — exactly the kind of silent off-by-one/overflow a
  differential test must specifically target, not merely stumble onto.
- **Amended this pass**: the entry's `reason:` field must disclose all
  six behaviour changes §5.2 now lists explicitly — `stats`'s account/
  not_account correction (§5.1c), the deprecated multi-account shim fix
  including its zero-accounts case (§5.1a), `balance_from_spec`'s outer-
  query convergence (§5.1b), `ReportSection`'s `HledgerRegex`-validation
  (§5.1b), and `Journal.to_dataframe`'s migration (§5.1d) — not just the
  headline `Query.account`/`.payee`/`.not_account` strictness change.
- Per the standing process: first-time promotion of the new entry to
  `status: verified` requires a genuinely separate `compat-
  differential-tester` dispatch (`09-compatibility-system.md` §9.6).

## 10. Documentation sync required (once implementation is approved and lands)

- `dev-docs/api-spec.md` — `Query`'s own entry gains a note that its
  fields now evaluate via the same engine `-q` uses (no signature
  change, per §5.2); `stats`'s entry gets the before/after account/
  not_account note (§5.1c); `balance_from_spec`'s entry notes its outer
  query now converges too (§5.1b); `to_dataframe`'s entry notes its
  migration (§5.1d); `Journal.balance`/`.register`'s `accounts=` entry
  notes the `Or`-based multi-account fix, including the zero-accounts
  case (§5.1a); `_posting_matches` removed from any documentation that
  mentions it (confirmed **zero** remaining callers, §5.3) —
  `_matches_pattern` is **retained** in documentation, noted as now
  `HledgerRegex`-backed and used **only** for `ReportSection` (§5.1b),
  not removed (check `architecture.md` too).
- `dev-docs/architecture.md` — `reports.py`'s filtering description
  updated: `balance`/`register`/`accounts`/`stats`/`balance_from_spec`'s
  outer query/`to_dataframe` **all** share one evaluation path via
  `ledgerkit.query.compat._query_to_ast` (§5.3's full inventory) —
  `ReportSection.accounts`/`.exclude` is the **only** remaining
  deliberately separate construct, keeping its own OR/exclude control
  flow but sharing the same `HledgerRegex` dialect via a refactored
  `_matches_pattern` (§5.1b). Described accurately as one canonical
  evaluation path plus exactly one named exception, not overstated as
  fully unified and not understated as still two parallel systems.
- `dev-docs/hledger-compatibility.md` — a note that `Query`'s `account`/
  `not_account`/`payee` fields (and, via §5.1b, `ReportSection.
  accounts`/`.exclude`) are now `HledgerRegex`-validated exactly like
  `acct:`/`desc:`, including the Stage C Phase 7 empty-pattern rejection
  (a `Query(account="")` would now raise, where previously `"" in
  value` trivially matched everything — worth its own explicit line,
  since `Query(account="")` is a plausible accidental caller mistake now
  surfaced loudly instead of silently matching everything); the `stats`
  account/not_account before/after (§5.1c).
- `knowledge/DECISIONS.md` — Option A chosen over B, why, and the
  **corrected** (§8) blast-radius conclusion (no external consumer, but
  multiple internal paths needed explicit handling, enumerated in
  §5.3); the `_query_to_ast` module-placement decision (§5.1, `query/
  compat.py` not `models.py`, and why); the deprecated `accounts=
  [...]` shim's `Or`-based fix for all three cases, **including the
  zero-accounts-must-not-become-`Or(())` bug** found this pass; the
  decision to converge `balance_from_spec`'s outer query too rather
  than leaving it on `_matches_pattern` as Amendment 1 had.
- `knowledge/DOMAIN_RULES.md` — the `Query.date_to` (inclusive) vs
  `DateSpan.end` (exclusive) translation trap, **including the
  `date.max` overflow edge case** (§4/§5.1a) — a genuinely non-obvious,
  easy-to-invert-and-easy-to-overflow detail worth its own entry.
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the standing rule, at
  implementation time.

## 11. Proposed tests

- **Unit** (`ledgerkit/query/compat.py`'s own test module):
  `_query_to_ast` directly — each field alone, combinations (`account`+
  `not_account`, `account`+`payee`+dates), `Query()`/all-`None` →
  `None`, `depth`-only → `None` (never a predicate node). **A dedicated,
  explicitly-named test for the date-inclusivity translation**:
  `Query(date_to=D)` must still match a transaction dated exactly `D`
  post-migration. **New this pass, `date.max`-specific**: `Query(date_
  to=datetime.date.max)` must not raise `OverflowError` and must still
  match a transaction dated `datetime.date.max`.
- **Integration** (`tests/test_reports.py`, `tests/test_dataframe.py`):
  every existing `Query(...)`-based test must continue passing unchanged
  (§8 predicts this for direct `Query(...)` construction specifically;
  implementation must confirm it, not assume it).
- **New, Option-A-specific**: a `Query.account`/`payee` value using an
  excluded `HledgerRegex` construct (e.g. `r"\d+"`) now raises the same
  error a `-q "acct:\d+"` query already does — confirming genuine
  convergence, not just "similar-looking" behaviour. **New this pass**:
  the raise must happen deterministically at translation time even
  against an empty journal (zero transactions/postings) — regression
  guard for §5.1a's eager-validation fix, since the old design's bare
  `Acct(...)` construction would only have failed lazily, if at all, at
  evaluation time.
- **New, Stage-C-Phase-7-consistency**: `Query(account="")` now raises,
  matching `-q "acct:"`'s own Phase 7 behaviour, rather than silently
  matching every posting.
- **Amended this pass, the deprecated multi-account shim (§5.1a) — now
  all three cases, not two**: `Journal.balance(accounts=[])`/`.register(
  accounts=[])` (**zero** accounts, new required case) behaves as no
  filter at all — explicitly **not** `Or(())` (regression guard for the
  empty-`Or`-matches-nothing bug this pass found). `Journal.balance(
  accounts=["food"])`/`.register(accounts=["food"])` (single account)
  still work exactly as today. `Journal.balance(accounts=["food",
  "transport"])`/`.register(...)` (two or more accounts) now build an
  `Or(...)` AST instead of a `(?:...)`-based string and **do not raise**
  under Option A — this and the zero-account case currently have
  **zero** existing test coverage per §2, so all three are net-new
  tests, not rewrites.
- **New this pass, `balance_from_spec` outer-query convergence
  (§5.1b)**: `balance_from_spec(query=Query(account="food"))` produces
  identical `ReportSectionResult`s to the pre-migration implementation
  for every existing test case; a new test confirms `balance_from_spec(
  query=Query(account=r"\d+"))` (excluded construct) now raises, exactly
  like `balance`/`register` already do.
- **New this pass, `ReportSection`-only retention of `_matches_pattern`
  (§5.1b)**: every existing `balance_from_spec`/`ReportSection` test
  continues passing; a new test confirms `ReportSection(accounts=
  (r"\d+",))` (an excluded construct) now raises, and `ReportSection(
  accounts=("",))` (empty pattern) now raises too — confirming
  `_matches_pattern`'s refactor took effect for `ReportSection`
  specifically, now that it's the *only* remaining caller.
- **New this pass, `Journal.to_dataframe` migration (§5.1d)**: every
  existing `to_dataframe(query=...)` test continues passing (parity
  with the pre-migration `_posting_matches`-based implementation); a
  new test confirms an excluded construct or empty pattern in
  `to_dataframe(query=...)` now raises **deterministically before any
  row is built**, even against an empty journal (zero transactions) —
  regression guard for the same eager-validation guarantee §5.1a's
  `Query.account` test already requires, extended to this call site;
  a new test confirms `ledgerkit.reports._posting_matches` has no
  remaining importers anywhere in `ledgerkit/` (a static/grep-based
  confirmation, not just "existing tests still pass," since a stale but
  unused import could otherwise go unnoticed).
- **New this pass, `stats` behaviour correction (§5.1c)**: `stats(
  query=Query(account=X))` now excludes transactions with no posting
  matching `X` from `account_count`/`account_depth`/etc. — an explicit,
  named before/after test pair (one confirming the old silently-ignored
  behaviour no longer applies, one confirming the new filtered count).
- **Differential** (mandatory, genuinely separate `compat-
  differential-tester` dispatch before any compat-register promotion):
  confirm `Query`-based filtering and `-q`-string-based filtering now
  produce identical results for equivalent queries across **every**
  converged path named in §5.3 — `balance`, `register`, `accounts`,
  `stats`, `balance_from_spec`'s outer query, and `to_dataframe` — not
  only `balance`/`register` as originally scoped. Include the
  multi-account shim (all three cases) and the `stats` correction in
  the same differential pass.

## 12. Summary of what needs explicit approval (gate) — reduced to the actual remaining decisions (Amendment 2)

Every item below now states the recommended choice explicitly, per
explicit instruction — nothing here is left as an open-ended question
without a lead position:

1. **§6 — Regex strictness.** Approve **Option A** — full `HledgerRegex`
   convergence. This is the one genuinely blocking fork; everything
   else in this gate is either already-resolved-by-recommendation or a
   non-blocking naming detail.
2. **§5.1c — `stats` correction.** **Include it in Phase 8.** Closing
   the existing `Query.account`/`.not_account`-ignored-by-`stats` gap is
   a natural, in-scope consequence of convergence (it makes the legacy
   path match what `-q "acct:..." stats` already does), not separate
   feature work to defer.
3. **§5.1b — `ReportSection` scope.** **Keep `ReportSection`'s own
   separate OR/exclude control flow; converge only its regex dialect**
   via the retained, refactored `_matches_pattern`. Defer full
   `ReportSpec`/`ReportSection` AST conversion to a distinct, not-yet-
   scoped future item (§7) — it is a different public surface from
   `Query` with its own combination semantics, not this phase's scope.
4. **§5.1a — Exception type.** **Reuse `QueryParseError`** for a
   `Query`/deprecated-shim field's invalid regex, rather than inventing
   a new exception type — mirrors Stage C Phase 7's own precedent
   (reusing `UnsupportedRegexConstructError`) for the same underlying
   condition.
5. **§9 — Compat-register naming.** The exact name/scope of the new
   `LK-COMPAT-QUERY-SHIM-001`-shaped entry is an **implementation-detail
   naming choice, not a blocker** — proceed with the lead's proposed
   name unless the implementer finds a reason to rename it.
6. **General approval to proceed** — conditioned explicitly on the
   design now reflecting §5.3's complete public-path inventory (all
   seven `Query` consumers named, each with a stated convergence path)
   rather than the incomplete, grep-derived completeness claims either
   prior version made.

No implementation begins until item 1 (the one blocking fork) is
explicitly decided; items 2-5 have stated recommendations the
implementer proceeds with unless told otherwise.

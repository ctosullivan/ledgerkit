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

**Amendment (2026-09-26, same day): a targeted design-correction pass,
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

### 5.1a (continued) — the deprecated multi-account shim, corrected

**Real regression found and fixed this pass** (§2): `Journal.balance`/
`.register`'s `accounts: list[str] | None` parameter, for `len(accounts)
> 1`, must stop synthesizing a `Query.account` string via `(?:...)`
non-capturing-group alternation (`HledgerRegex`-excluded). Two
HledgerRegex-portable options exist; **direct AST construction is
recommended** over a re-escaped `|`-joined string, since it sidesteps
any regex-escaping/precedence subtlety entirely:

```python
# ledgerkit/models.py, inside Journal.balance()/register() (lazy import,
# matching the existing pattern at the top of this class):
from ledgerkit.query.ast import Acct, Or
import re as _re

if accounts is not None and query is None:
    if len(accounts) == 1:
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
        _query_ast = Or(tuple(Acct(_re.escape(a)) for a in accounts))
        return _balance(self, query=None, _query_ast=_query_ast, tree=tree)
```

`re.escape(a)` for an ordinary account name (letters, digits, `:`)
produces the name unchanged in Python 3.7+ (`:` is not a regex
metacharacter) — and for any account name that *does* contain a real
regex metacharacter, the escaped form (e.g. `\.`) is itself
`HledgerRegex`-portable (plain backslash-escaped literals are not in
`_EXCLUDED_CONSTRUCT`'s exclusion list), so this is safe unconditionally,
not just for the common case. This bypasses `Query.account` entirely
for the multi-account case, reusing the already-existing private
`_query_ast` parameter instead of round-tripping through a synthesized
string — simpler and more obviously correct than re-deriving a
`(?:...)`-free string-joining scheme. `register()` gets the identical
treatment. **Required tests** (§11): one account (unchanged, still a
raw regex passthrough) and multiple accounts (now `Or`-based, not
`(?:...)`-based) both keep working.

### 5.1b `_matches_pattern` — retained and refactored, not retired

**Scope decision, stated explicitly per explicit instruction.**
`reports.balance_from_spec` (`reports.py:612-694`) has its own,
separate, hand-rolled filtering loop — it does not call `_posting_
matches` at all, and calls `_matches_pattern` directly, five times:
`query.payee`/`query.account`/`query.not_account` (its own inline
re-implementation of the outer filter, independent of `_posting_
matches`), and `ReportSection.accounts`/`.exclude` (`models.py:
198-215`, a public dataclass with its own OR/exclude semantics that
have no `Query` equivalent at all). **`_matches_pattern` is retained**,
not removed — removing a helper a live public-API path (`balance_from_
spec`, `ReportSection`) still depends on would be a real defect, not a
simplification.

**Chosen scope**: `_matches_pattern`'s *implementation* is refactored
to route through `compile_hledger_regex`/`.search()` instead of the ad
hoc `_REGEX_META` Python-native-regex heuristic (`reports.py:215-228`)
— its call sites in `balance_from_spec` are **unchanged**. This gets
`ReportSection.accounts`/`.exclude` and `balance_from_spec`'s own
`query` handling onto the same canonical `HledgerRegex` dialect as
everything else (achieving §7.2's "no parallel regex dialect" goal
project-wide, not just for `balance`/`register`/`accounts`/`stats`),
**without** expanding this phase into redesigning `ReportSpec`/
`ReportSection`'s own OR/exclude combination architecture into AST
terms — that remains a distinct, larger, not-yet-scoped possible future
item (§7), since `ReportSection` is a genuinely different public
surface from `Query` with its own combination semantics, not something
this phase's own approved scope (`Query` convergence) covers.

Consequence, disclosed: `ReportSection.accounts`/`.exclude` and
`balance_from_spec`'s `query.account`/`.payee`/`.not_account` now also
reject an excluded `HledgerRegex` construct and an empty pattern
(Stage C Phase 7's own rejection, inherited automatically once
`_matches_pattern` is `compile_hledger_regex`-backed) — the same
Option-A behaviour change as §6, extended to this second call site by
construction, not by a separate decision.

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

### 5.2 Report function signatures — unchanged

`balance`/`register`/`accounts`/`stats`/`balance_from_spec`/`to_
dataframe`'s public signatures (`query: Query | None = None`) are
**not** proposed to change — only their internal implementation. This
keeps the change inside the Unauthorised Change Rule's safe zone for
`dev-docs/api-spec.md` (no signature to re-approve) as long as
implementation confirms no observable-from-outside change beyond the
regex-strictness question in §6 below. The private `_query_ast`
parameter's own fate (kept as-is, or folded away now that `Query` also
compiles to the same AST type) is left to implementation planning —
not a design-level decision, since either choice is purely internal.

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
- **New this pass**: the entry's `reason:` field must also disclose
  §5.1c's `stats` behaviour correction (account/not_account now
  affecting the counted transaction subset) and §5.1a's deprecated
  multi-account shim fix — both are real, user-observable behaviour
  changes this entry needs to own, not just the headline `Query.
  account`/`.payee`/`.not_account` `HledgerRegex`-strictness change.
- Per the standing process: first-time promotion of the new entry to
  `status: verified` requires a genuinely separate `compat-
  differential-tester` dispatch (`09-compatibility-system.md` §9.6).

## 10. Documentation sync required (once implementation is approved and lands)

- `dev-docs/api-spec.md` — `Query`'s own entry gains a note that its
  fields now evaluate via the same engine `-q` uses (no signature
  change, per §5.2); `stats`'s entry gets the before/after account/
  not_account note (§5.1c); `Journal.balance`/`.register`'s `accounts=`
  entry notes the `Or`-based multi-account fix (§5.1a); `_posting_
  matches` removed from any documentation that mentions it —
  `_matches_pattern` is **retained** in documentation, noted as now
  `HledgerRegex`-backed (§5.1b), not removed (check `architecture.md`
  too).
- `dev-docs/architecture.md` — `reports.py`'s filtering description
  updated: `balance`/`register`/`accounts`/`stats` now share one
  evaluation path via `ledgerkit.query.compat._query_to_ast`;
  `balance_from_spec`/`ReportSection` keep their own control flow but
  now share the same regex dialect via a refactored `_matches_pattern`
  (§5.1b) — described accurately as two flows, one shared dialect, not
  overstated as fully unified.
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
  three internal paths needed explicit handling); the `_query_to_ast`
  module-placement decision (§5.1, `query/compat.py` not `models.py`,
  and why); the deprecated `accounts=[...]` shim's `Or`-based fix (why
  direct AST construction was chosen over a re-escaped joined string).
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
- **New this pass, the deprecated multi-account shim (§5.1a)**:
  `Journal.balance(accounts=["food"])`/`.register(accounts=["food"])`
  (single account) still work exactly as today. `Journal.balance(
  accounts=["food", "transport"])`/`.register(...)` (two or more
  accounts) now build an `Or(...)` AST instead of a `(?:...)`-based
  string and **do not raise** under Option A (regression guard — this
  is the real bug this pass found and fixed, and currently has **zero**
  existing test coverage per §2, so these tests are net-new, not
  rewrites).
- **New this pass, `_matches_pattern` retention (§5.1b)**: every
  existing `balance_from_spec`/`ReportSection` test continues passing;
  a new test confirms `ReportSection(accounts=(r"\d+",))` (an excluded
  construct) now raises, and `ReportSection(accounts=("",))` (empty
  pattern) now raises too — confirming `_matches_pattern`'s refactor
  actually took effect for `ReportSection`, not just for `Query`.
- **New this pass, `stats` behaviour correction (§5.1c)**: `stats(
  query=Query(account=X))` now excludes transactions with no posting
  matching `X` from `account_count`/`account_depth`/etc. — an explicit,
  named before/after test pair (one confirming the old silently-ignored
  behaviour no longer applies, one confirming the new filtered count).
- **Differential** (mandatory, genuinely separate `compat-
  differential-tester` dispatch before any compat-register promotion):
  confirm `Query`-based filtering and `-q`-string-based filtering now
  produce identical results for equivalent queries (e.g. `Query
  (account="food")` vs `-q "acct:food"`) on a shared fixture — this is
  the actual, executable proof of "one evaluation path," not merely an
  implementation-detail claim. Include the multi-account shim and
  `stats` correction in the same differential pass.

## 12. Summary of what needs explicit approval (gate)

1. **§6 — regex strictness**: Option A (full `HledgerRegex` convergence,
   recommended) vs Option B (preserve the permissive fallback,
   contradicts the pre-approved architecture). Lead recommends A. This
   is the one genuinely blocking fork, unchanged by this amendment.
2. **§5.1c — `stats` behaviour correction**: confirm that closing the
   existing `Query.account`/`.not_account`-ignored-by-`stats` gap, as a
   natural consequence of convergence, is wanted as part of this phase
   (recommended — it makes the legacy path match what `-q` already
   does) rather than deferred as its own separate, later fix. Lead
   recommends resolving it here, now that it's explicitly named rather
   than an incidental side effect.
3. **§5.1b — `_matches_pattern`/`ReportSection` scope**: confirm the
   chosen scope (refactor `_matches_pattern` to be `HledgerRegex`-backed,
   keep `balance_from_spec`/`ReportSection`'s own control flow as-is;
   full `ReportSpec`/`ReportSection` AST convergence stays a named,
   separate future item) rather than expanding this phase to cover it.
4. **§9 — compat-register entry** naming/scope for the new `LK-COMPAT-
   QUERY-SHIM-001`-shaped entry — a naming detail, not a blocking fork,
   flagged for awareness.
5. **§5.1a — reusing `QueryParseError`** for a `Query` field's invalid
   regex (vs. a new, `Query`-specific exception) — a naming/exception-
   type detail, not a blocking fork, flagged for awareness (mirrors
   Stage C Phase 7's own precedent of reusing an existing exception
   type rather than adding a new one).
6. **General approval** to proceed to implementation planning once §6
   (and, ideally, §5.1c/§5.1b) are resolved.

No implementation begins until this section's items are explicitly
decided.

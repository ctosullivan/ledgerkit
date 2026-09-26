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

## 0. Pinned revisions

Ledgerkit: `afbcd05`.

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
real consumer never reaches that code at all. This substantially
de-risks converging the internal evaluation: the field shape (`Query`'s
`__init__` signature) must not change; the matching *behaviour* behind
it converging onto stricter, hledger-faithful semantics is a smaller,
better-contained risk than it would be if `ledgerkit-editor` actually
called into it. The only place this phase's behaviour change is
actually observable is Ledgerkit's own test suite and any as-yet-
undiscovered second consumer (none known).

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
  a real behaviour regression** — the correct translation is
  `DateSpan(end=query.date_to + timedelta(days=1))`. Flagged here
  explicitly because it is the single easiest correctness trap in this
  entire phase and the design must not leave it implicit.
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

### 5.1 A private translation function

`ledgerkit/models.py` or `ledgerkit/query/parser.py` (implementer's
call which module — `models.py` avoids a new `query/`→`models.py`
import direction if `Query` stays defined in `models.py`) gains a
private `_query_to_ast(query: Query | None) -> QueryNode | None`:

```python
def _query_to_ast(query: Query | None) -> QueryNode | None:
    if query is None:
        return None
    terms: list[QueryNode] = []
    if query.account is not None:
        terms.append(Acct(query.account))
    if query.not_account is not None:
        terms.append(Not(Acct(query.not_account)))
    if query.payee is not None:
        terms.append(Desc(query.payee))
    if query.date_from is not None or query.date_to is not None:
        end = query.date_to + datetime.timedelta(days=1) if query.date_to else None
        terms.append(DateSpan(start=query.date_from, end=end))
    if not terms:
        return None
    return terms[0] if len(terms) == 1 else And(tuple(terms))
    # query.depth is deliberately excluded — never a predicate (§4).
```

`_posting_matches`/`_matches_pattern` and the ad hoc `_REGEX_META`
construct-sniffing (`reports.py:215-240`) are retired — every report
function's existing `query: Query | None` parameter is translated once
via `_query_to_ast` and evaluated through the **same** `ledgerkit.
query.eval` engine `_query_ast` already uses, combined (AND'd) with any
`_query_ast` also supplied. This directly achieves `07-query-regex.md`
§7.2's stated end state: one evaluation path, not two.

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
behaviour change (per §3, contained — no known external consumer is
affected; Ledgerkit's own test suite, checked in §8, uses no
excluded-construct patterns today).

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
actually specifies, the real-world blast radius is empty (per §3), and
Ledgerkit's own test suite's `Query(...)` usages (§8) use only plain
substrings and hledger-portable anchors/wildcards — no excluded
construct anywhere. **Still not a decision** — explicit approval
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

## 8. Blast-radius check against Ledgerkit's own test suite — [VERIFIED-EXTERNAL]

Every `Query(...)` construction in `tests/test_reports.py`/`tests/
test_dataframe.py` (full list, direct grep) uses either a plain
substring (`"expenses"`, `"assets"`, `"income:salary"`,
`"nonexistent:account"`, `"Supermarket"`, `"Coffee"`) or a
`HledgerRegex`-portable anchor (`"^income"`) — **none uses a construct
`HledgerRegex` excludes** (no `\d`, no lookaround, no named/non-
capturing groups, no lazy quantifiers, no POSIX classes, no GNU `\<`/
`\>`, no literal backreference). Option A (§6) would not break a single
existing test's `Query` usage on this basis alone — the design's own
recommendation is not merely theoretical, it's confirmed against the
actual, current test suite.

## 9. Compatibility implications

- New compat-register entries needed once implemented and independently
  verified: `LK-COMPAT-QUERY-SHIM-001` or similar (`area: query.shim`) —
  documents that `Query`'s fields now evaluate through the same
  `HledgerRegex`-validated, hledger-faithful engine `-q` uses, with the
  Option A behaviour-change disclosed explicitly in its `reason:` field
  (mirroring `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001`'s own disclosure
  style from Stage C Phase 7).
- The `Query.date_to` inclusive-vs-`DateSpan.end`-exclusive translation
  (§4) needs its own explicit regression test and its own line in the
  new entry's `reason:` field — it is exactly the kind of silent-
  off-by-one a differential test must specifically target, not merely
  stumble onto.
- Per the standing process: first-time promotion of the new entry to
  `status: verified` requires a genuinely separate `compat-
  differential-tester` dispatch (`09-compatibility-system.md` §9.6).

## 10. Documentation sync required (once implementation is approved and lands)

- `dev-docs/api-spec.md` — `Query`'s own entry gains a note that its
  fields now evaluate via the same engine `-q` uses (no signature
  change, per §5.2); `_posting_matches`/`_matches_pattern` removed from
  any documentation that mentions them (check `architecture.md` too).
- `dev-docs/architecture.md` — `reports.py`'s filtering description
  updated to state one evaluation path, not two.
- `dev-docs/hledger-compatibility.md` — a note that `Query`'s `account`/
  `not_account`/`payee` fields are now `HledgerRegex`-validated exactly
  like `acct:`/`desc:`, including the Stage C Phase 7 empty-pattern
  rejection (a `Query(account="")` would now raise, where previously
  `"" in value` trivially matched everything — worth its own explicit
  line, since `Query(account="")` is a plausible accidental caller
  mistake now surfaced loudly instead of silently matching everything).
- `knowledge/DECISIONS.md` — Option A chosen over B, why, and the
  confirmed-empty blast radius from §3/§8.
- `knowledge/DOMAIN_RULES.md` — the `Query.date_to` (inclusive) vs
  `DateSpan.end` (exclusive) translation trap (§4) — a genuinely
  non-obvious, easy-to-invert detail worth its own entry.
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the standing rule, at
  implementation time.

## 11. Proposed tests

- **Unit**: `_query_to_ast` directly — each field alone, combinations
  (`account`+`not_account`, `account`+`payee`+dates), `Query()`/all-
  `None` → `None`, `depth`-only → `None` (never a predicate node).
  **A dedicated, explicitly-named test for the date-inclusivity
  translation**: `Query(date_to=D)` must still match a transaction dated
  exactly `D` post-migration (regression guard for §4's trap).
- **Integration** (`tests/test_reports.py`, `tests/test_dataframe.py`):
  every existing `Query(...)`-based test must continue passing unchanged
  (§8 predicts this; implementation must confirm it, not assume it) —
  no test rewrites should be needed if Option A's blast-radius analysis
  is correct.
- **New, Option-A-specific**: a `Query.account`/`payee` value using an
  excluded `HledgerRegex` construct (e.g. `r"\d+"`) now raises the same
  error a `-q "acct:\d+"` query already does — confirming genuine
  convergence, not just "similar-looking" behaviour.
- **New, Stage-C-Phase-7-consistency**: `Query(account="")` now raises,
  matching `-q "acct:"`'s own Phase 7 behaviour, rather than silently
  matching every posting.
- **Differential** (mandatory, genuinely separate `compat-
  differential-tester` dispatch before any compat-register promotion):
  confirm `Query`-based filtering and `-q`-string-based filtering now
  produce identical results for equivalent queries (e.g. `Query
  (account="food")` vs `-q "acct:food"`) on a shared fixture — this is
  the actual, executable proof of "one evaluation path," not merely an
  implementation-detail claim.

## 12. Summary of what needs explicit approval (gate)

1. **§6 — regex strictness**: Option A (full `HledgerRegex` convergence,
   recommended) vs Option B (preserve the permissive fallback,
   contradicts the pre-approved architecture). Lead recommends A.
2. **§9 — compat-register entry** naming/scope for the new `LK-COMPAT-
   QUERY-SHIM-001`-shaped entry — a naming detail, not a blocking fork,
   flagged for awareness.
3. **General approval** to proceed to implementation planning once §6
   is resolved.

No implementation begins until this section's items are explicitly
decided.

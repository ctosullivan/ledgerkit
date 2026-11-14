# Implementation Reconstruction: query-engine

- **Role:** implementation-reconstructor
- **Topic:** query-engine (Ledgerkit's query AST, tokenizer/parser, evaluator, depth/clipping, and regex-compatibility subsystem under `ledgerkit/query/`)
- **Dispatch:** same-host, prompt-scoped sub-agent dispatch, best-effort isolation (not verified) — this report was produced inside a `general-purpose`-typed dispatch following the `implementation-reconstructor` brief, per Plan 29 §4.2's disclosed-substitution allowance
- **Dispatch timestamp:** 2026-10-02T16:55:18Z
- **Report date:** 2026-10-03

Evidence basis: only the files under `ledgerkit/query/` and `tests/test_query/test_{parser,eval,regex,compat}.py` named in the dispatch's permitted evidence paths, plus live execution of `ledgerkit.query` functions in this checkout. No assertion, snapshot, planning doc, legacy `dev-docs/*.md`/`docs/*.md`, `knowledge/*.md`, or `dev-docs/compat-register/*` content was read. `dev-docs/compat-register/*.yaml` was not among this dispatch's permitted evidence paths, so item 8 of the brief (tracing a compat-register claim to its evidence) does not apply to this report.

---

## 1. Structure

`ledgerkit/query/` is a six-module subpackage plus `__init__.py`:

| Module | Responsibility (as read from the code) |
|---|---|
| `ast.py` | Frozen dataclass/enum definitions for every query-predicate node type, plus `QueryPlan` (the parse result: a predicate tree + a `DepthSpec`). Contains no evaluation or parsing logic. |
| `parser.py` | Tokenizes a query string (`_tokenize`), builds one `QueryNode` or `DepthSpec` contribution per token, and combines terms into a final `QueryPlan` via `parse()`. Owns `QueryParseError`. |
| `eval.py` | Two public functions (`matches_transaction`, `matches_posting`) plus one package-private one (`_matches_posting_for_accounts`) that walk a `QueryNode` tree against a `Transaction`/`Posting` (and optionally a `Journal`, for `Tag` nodes) and return a bool. |
| `depth.py` | `DepthSpec` dataclass and the depth-clipping/exclusion/merge functions (`clipped_depth_for_account`, `clip_account_name`, `account_excluded_by_depth`, `merge_depth_specs`). Depth is explicitly modeled as a report-display option, never a selection predicate. |
| `regex.py` | `HledgerRegex` subset validator/compiler: `validate_hledger_regex`, `compile_hledger_regex`, `UnsupportedRegexConstructError`. No dependency on any other module in the subpackage. |
| `compat.py` | Private translator (`_query_to_ast`, plus helpers `_validated`/`_exclusive_end`) from the separate `ledgerkit.models.Query` dataclass shape into a `QueryNode` tree, so that shape and the `-q` string grammar funnel through the same `eval.py` evaluator. Nothing else in `ledgerkit/query/` imports this module. |
| `__init__.py` | Re-exports the public surface (see §2) from the above five modules; `compat.py`'s contents are deliberately not re-exported (all its names are underscore-prefixed). |

Internal import graph (confirmed by reading each module's own imports): `ast.py` → `depth.py`; `parser.py` → `ast.py`, `depth.py`, `regex.py`; `eval.py` → `ast.py`, `regex.py`, plus `ledgerkit.models` and `ledgerkit.tags` (outside this subpackage — not in my permitted evidence paths, so their internals are unverified here, only the import itself is confirmed); `depth.py` → `regex.py`; `regex.py` → no intra-package imports; `compat.py` → `ast.py`, `parser.py`, `regex.py`, and a `TYPE_CHECKING`-only reference to `ledgerkit.models.Query`.

## 2. Public surface

Confirmed from `__init__.py`'s `__all__` (line-by-line) and each symbol's own definition:

- **AST node types** (`ast.py`): `Acct(pattern: str)`, `Desc(pattern: str)`, `DateSpan(start: date|None, end: date|None)` (end exclusive), `MaxAccountLevel(n: int)`, `Status(value: TxnStatus)`, `Tag(name_pattern: str, value_pattern: str|None = None)`, `And(terms: tuple[QueryNode, ...])`, `Or(terms: tuple[QueryNode, ...])`, `Not(term: QueryNode)`. All are `@dataclass(frozen=True)`. `TxnStatus` is an `enum.Enum` with `UNMARKED`/`PENDING`/`CLEARED`. `QueryNode` is a `typing.Union` of all nine node types (not a base class — no shared superclass, no shared method; dispatch everywhere is `isinstance` chains).
- **`QueryPlan(predicate: QueryNode, depth: DepthSpec = DepthSpec())`** — the parser's output type. `predicate` is guaranteed (by construction, confirmed in `parser.py`) to never contain a `MaxAccountLevel` node.
- **`DepthSpec(flat: int|None = None, by_pattern: tuple[tuple[str,int], ...] = ())`** plus its `is_empty()` method and the module functions `clipped_depth_for_account`, `clip_account_name`, `merge_depth_specs` (all three exported); `account_excluded_by_depth` exists in `depth.py` but is **not** re-exported from `__init__.py` — it is reachable only via `ledgerkit.query.depth.account_excluded_by_depth` directly, confirmed by its absence from `__all__`.
- **`parse(query_text: str) -> QueryPlan`** and **`QueryParseError(ValueError)`**.
- **`matches_transaction(node, txn, journal=None) -> bool`** and **`matches_posting(node, txn, posting, journal=None) -> bool`**.
- **`validate_hledger_regex(pattern: str) -> None`**, **`compile_hledger_regex(pattern: str) -> re.Pattern[str]`**, **`UnsupportedRegexConstructError(ValueError)`**.

Not exported, confirmed private/internal: `_matches_posting_for_accounts` (eval.py — used, per its own docstring, only by `ledgerkit.reports.accounts`, which is outside my evidence scope so I could not confirm that caller directly), `account_excluded_by_depth` (depth.py — per its own docstring, used only by `ledgerkit.reports.stats()`, also unverified here), and everything in `compat.py` (`_query_to_ast`, `_validated`, `_exclusive_end` — used, per its module docstring, by `ledgerkit/models.py`'s `Journal.balance`/`.register`/`.to_dataframe` and `ledgerkit/reports.py` via lazy in-function imports; this claim is stated in `compat.py`'s own docstring but I did not verify it against `models.py`/`reports.py`, which are outside my permitted evidence paths).

`MaxAccountLevel` has **no string-syntax spelling at all** — confirmed by reading `parser.py`'s `_PREFIX_BUILDERS` dict (only `acct:`, `desc:`, `date:`, `status:`, `tag:` are registered) and by live execution: `parse("level:2")` and `parse("depth:2")` never produce a `MaxAccountLevel` node (the latter produces a `DepthSpec` and a vacuous `And(())` predicate). It is reachable only by constructing it directly in Python and passing it to `matches_transaction`/`matches_posting`.

## 3. Data model

All AST nodes and `QueryPlan`/`DepthSpec` are immutable (`frozen=True`) dataclasses — equality is structural (dataclass-generated `__eq__`), which is what every test in `test_parser.py`/`test_compat.py` relies on (e.g. `self.assertEqual(_pred("acct:groceries"), Acct("groceries"))`).

- `Acct.pattern` / `Desc.pattern` / `Tag.name_pattern` / `Tag.value_pattern` are plain `str` — by convention (stated in docstrings, enforced at construction time by the callers in `parser.py`/`compat.py`, **not** by the dataclasses themselves) they must already be `HledgerRegex`-validated.
- `DateSpan.start`/`.end` are `datetime.date | None`; `end` is exclusive — explicitly and deliberately different from `ledgerkit.models.Query.date_to`, which `compat.py`'s `_exclusive_end` converts (inclusive→exclusive, +1 day, with a `date.max` special case to avoid `OverflowError`).
- `MaxAccountLevel.n` is a plain `int` with no validation at the dataclass level (docstring states callers must enforce `n >= 0`).
- `Status.value` is a `TxnStatus` enum member.
- `DepthSpec.by_pattern` is a `tuple[tuple[str, int], ...]` — ordered, append-only (`merge_depth_specs` concatenates, never dedupes or reorders).
- `QueryPlan.depth` defaults via `field(default_factory=DepthSpec)` — i.e. `QueryPlan(predicate)` alone is valid and gets an empty, non-clipping `DepthSpec`.

## 4. Dependencies

External (stdlib only, confirmed by each module's own `import` lines): `datetime`, `re`, `enum`, `dataclasses`, `functools`, `typing`. No third-party imports anywhere in the six modules — consistent with the project's stated no-third-party-in-`ledgerkit/`-core policy (observed as a fact of the code, not cross-checked against any doc).

Internal, outside the `query` subpackage: `eval.py` imports `Journal, Posting, Transaction` from `ledgerkit.models` and `_accounts_effective_tags, _effective_tags` from `ledgerkit.tags`. `compat.py` imports nothing at runtime from `ledgerkit.models` (only a `TYPE_CHECKING`-guarded type-hint reference to `Query`) — its own docstring explains this is deliberate, to avoid a circular import, since `eval.py` already imports `ledgerkit.models` at module scope. Both `ledgerkit/models.py` and `ledgerkit/tags.py` are outside my permitted evidence paths for this dispatch, so I can confirm the import statements exist and name specific symbols, but I did not read either module and cannot independently confirm those symbols' own behavior (e.g. what `_effective_tags` actually computes) beyond what `eval.py`'s own docstrings assert about them. This is a genuine boundary of this report, not an oversight.

## 5. Runtime behaviour (confirmed by direct execution, not just reading docstrings)

All commands below were run via `PYTHONPATH=/home/cormac/projects/ledgerkit python3 <script>` against the actual checkout.

**Tokenizer quoting** (`parser._tokenize`, via the `_TOKEN` regex):
```
_tokenize('acct:"expenses dining" out')  -> ['acct:expenses dining', 'out']
_tokenize("don't")                        -> ["don't"]
_tokenize('a"b')                          -> ['a"b']
_tokenize('desc:"whole foods" status:*')  -> ['desc:whole foods', 'status:*']
_tokenize('desc:"foo"bar')                -> ['desc:foobar']
```
This confirms the docstring's claims exactly: a `prefix:"quoted phrase"` collapses into one token with quotes stripped (`desc:whole foods`); an unterminated quote (`don't`, `a"b`) degrades to the literal text rather than raising, including the stray quote character itself; and trailing text immediately after a closed quote (`"foo"bar`) is absorbed into the same token (`foobar`).

**Same-prefix OR / mixed-prefix AND combination** (`parser.parse`):
```
parse("acct:a desc:b acct:c").predicate
  -> And((Or((Acct('a'), Acct('c'))), Desc('b')))
```
Confirms `combineQueriesByType` replication: both `acct:` terms land in one `Or` bucket (order preserved); the unrelated `desc:` term is AND'd in separately, not folded into the `Or`.

**`depth:` extraction and its non-presence as a `MaxAccountLevel` string syntax**:
```
parse("level:2")  -> QueryPlan(predicate=Acct('level:2'), depth=DepthSpec())
parse("depth:2")  -> QueryPlan(predicate=And(()), depth=DepthSpec(flat=2))
```
`level:2` is not a recognized prefix at all and falls through to the bare-pattern-defaults-to-`acct:` rule, producing a literal (and almost certainly never-matching) account pattern `"level:2"` — confirming there is genuinely no string spelling that reaches `MaxAccountLevel`.

**Depth specificity resolution** (`depth.clipped_depth_for_account`), using the exact worked example named in the module's own docstring (`assets=1` vs `savings=2` on `assets:bank:savings`):
```
spec = DepthSpec(by_pattern=(("assets", 1), ("savings", 2)))
clipped_depth_for_account(spec, "assets:bank:savings")  -> 2   # savings wins
clip_account_name(spec, "assets:bank:savings")          -> "assets:bank"
clipped_depth_for_account(spec, "assets:bank")           -> 1   # here "assets" is the only match, at ancestor index 1
```
This confirms the counterintuitive specificity rule as documented: `"savings"` matches `assets:bank:savings` itself but neither of its strict ancestors (`assets`, `assets:bank`), earning the sentinel specificity `len(ancestors)+1 = 3`, which beats `"assets"`'s specificity of `1` (it matches the shallowest ancestor, `"assets"`, at index 1) — so the *less commonly matching* pattern wins, exactly as documented, and the account clips to depth 2 (`assets:bank`), not depth 1.

Tie-break (same specificity, two entries, later wins — docstring's `>=` comparison in the loop):
```
spec2 = DepthSpec(by_pattern=(("assets", 1), ("assets", 5)))
clipped_depth_for_account(spec2, "assets:bank:savings")  -> 5   # the later-declared entry
```

`depth:0` clips to the literal string `"..."`, never to exclusion or an empty string:
```
clip_account_name(DepthSpec(flat=0), "assets:bank")  -> "..."
```

`account_excluded_by_depth` (the `stats`-only, genuinely boolean-exclusion function, distinct from clipping):
```
account_excluded_by_depth(DepthSpec(flat=1), "assets:bank")           -> True   # level 2 > flat 1
account_excluded_by_depth(DepthSpec(flat=1), "assets")                -> False  # level 1 <= flat 1
account_excluded_by_depth(DepthSpec(by_pattern=(("assets",1),)), "assets:bank")      -> True   # matches AND level 2 > 1
account_excluded_by_depth(DepthSpec(by_pattern=(("assets",1),)), "liabilities:x")    -> False  # regex doesn't match -> never excludes on its own
```
Both confirm the documented asymmetric rule: a non-matching `REGEX=N` term never excludes by itself, only a matching one whose level exceeds `N` does.

**Merge order-independence** (confirmed via the parser's own test suite and independently by inspecting `merge_depth_specs`'s `min()` logic): `depth:3 depth:1` and `depth:1 depth:3` both resolve to `DepthSpec(flat=1)` — min-based, not last-wins.

**Tag evaluation requires a journal** — confirmed by direct read of `eval.py`: both `matches_transaction` and `_matches_posting_impl` raise `ValueError("tag: matching requires journal context")` the moment a `Tag` node is reached with `journal=None`, before any attempt to narrow to own-tags-only. This is also directly exercised by `test_eval.py`'s `test_journal_none_raises_on_matches_posting`/`_on_matches_transaction`.

## 6. Tests (read directly, not inferred from names)

Ran the four permitted test modules directly against this checkout:
```
python3 -m unittest tests.test_query.test_parser tests.test_query.test_eval \
                     tests.test_query.test_regex tests.test_query.test_compat -v
-> Ran 200 tests in 0.037s, OK
```
All 200 pass as of this checkout. Representative bodies read directly (not just names):

- `test_parser.py`: asserts exact `QueryNode`/`QueryPlan` shapes (dataclass equality) for bare patterns, every prefix, status synonyms (`status:1`==cleared, `status:0`==unmarked), the full depth-term matrix (flat, regex-keyed, multi-term min-merge, `not:depth:` rejection at one and two levels of `not:` wrapping), quoting, the four date-span shapes plus the "written range bound is not auto-incremented but a bare single date is" distinction, same-prefix OR vs. negated-same-prefix AND (the "central footgun" test explicitly named as such), the full `tag:` grammar including the `tag:rate==0.05` first-`=`-only split and the Stage-C-Phase-7/9 empty-pattern and empty-alternation-branch rejection matrices.
- `test_eval.py`: asserts `matches_transaction`'s "any posting matches" rule for `Acct`/`MaxAccountLevel`, `Desc`/`Status` posting-inheritance, `DateSpan` exclusive-end boundaries, and — most substantially — a 20+ test `Tag` suite built around a single fixture with a *different* `"rate"` value at each of the four effective-tag sources (posting-own, transaction-own, account-inherited, commodity-propagated), explicitly designed (per its own comment) to catch a "highest-priority-wins" bug that a naive implementation might introduce; plus the separate narrower `_matches_posting_for_accounts` visibility mode.
- `test_regex.py`: a construct-by-construct accept/reject matrix (inline flags, named/non-capturing groups, lookahead, backreferences, GNU word boundaries accepted as `\b` but a separate `\<`/`\>` form rejected, Perl classes, POSIX classes, lazy quantifiers), the empty-pattern-string rejection (distinguished explicitly from patterns that merely *admit* an empty match, e.g. `.*`, `a*`, `()`, which remain accepted), and an 18-pattern reject-list / 13-pattern accept-list for the empty-alternation-branch rule, each as its own named test.
- `test_compat.py`: `_query_to_ast` translation of every `Query` field alone and in combination, the inclusive→exclusive date translation (including the `date.max` overflow-avoidance case), and eager (translation-time, not evaluation-time) validation failures for excluded regex constructs and empty patterns in `account`/`not_account`/`payee`.

**Gap found by inspection of the permitted test files' import lists**: none of the four permitted test files import or directly exercise `ledgerkit.query.depth`'s `clipped_depth_for_account`, `clip_account_name`, or `account_excluded_by_depth` as standalone functions — `test_parser.py`'s `TestDepthSpec` class only exercises `DepthSpec` construction and `merge_depth_specs` indirectly, through `parse()`. No `test_depth.py` was named among my permitted evidence paths. Per the brief's instruction, I verified these three functions' behavior myself by direct execution (§5 above) rather than relying on their docstrings — I cannot speak to whether a `tests/test_query/test_depth.py` exists outside my permitted paths, since listing/reading anything not explicitly named was out of scope for this dispatch.

## 7. Limitations / gaps (named honestly, from the evidence)

1. **No dedicated unit tests, among the four permitted test files, for `depth.py`'s three core clipping/exclusion functions** (`clipped_depth_for_account`, `clip_account_name`, `account_excluded_by_depth`) — see §6. Their behavior is exercised only indirectly (via `parse()` and `merge_depth_specs`) in the permitted test set; I confirmed their behavior by direct execution instead, but this is a real test-coverage gap in what I was given to inspect, not something I should present as "tested."
2. **`MaxAccountLevel` is Python-API-only** — there is no `-q` string-syntax path to it (confirmed live: `parse("level:2")` falls through to a literal `acct:` pattern, not a `MaxAccountLevel` node). Its own docstring states `n >= 0` is required but the dataclass does not enforce this itself — a caller could construct `MaxAccountLevel(-1)` without any error from the AST layer; whether any caller validates this upstream is unverified (outside my permitted paths — `reports.py`/`cli.py` are excluded from this dispatch).
3. **`TxnStatus`/`Status` cannot express a per-posting status override** — `ast.py`'s own docstring states this plainly as an existing `Transaction`-model limitation (no posting-level cleared/pending field), not something this query package invents, and `eval.py`'s `_txn_status` always derives status from the transaction only, never the posting, even in `matches_posting`.
4. **`cur:` (currency/commodity query term) is not implemented** — absent from `parser.py`'s `_PREFIX_BUILDERS`, and its absence is explicitly called out in both `parser.py`'s and `__init__.py`'s module docstrings as deliberately out of scope for this phase, not a silent omission.
5. **hledger's smart/period date expressions (e.g. "last month", "2024q1") are not implemented** — `date:` only supports a single full date or a two-date range in four shapes (`_DATE_SPAN`); confirmed live (`parse("date:not-a-date")` and any non-ISO-shaped value raises `QueryParseError`).
6. **The `PythonRegex` escape hatch does not exist** — `regex.py`'s own docstring states there is currently no way to opt out of the `HledgerRegex` subset restriction from a query string; every `acct:`/`desc:`/`tag:`/`depth:REGEX=` pattern is unconditionally run through `validate_hledger_regex`, with no override.
7. **The excluded-construct regex scan in `regex.py` is a heuristic, not a parser** — its own comment states explicitly that a literal `\\` followed by a digit is not distinguished from a real backreference (false positives — over-rejection — are possible and accepted as safe; the comment states no false negatives are *known*, which is itself a hedge, not a proof).
8. **`account_excluded_by_depth` and `_matches_posting_for_accounts` are both documented, in their own docstrings, as used by exactly one caller each** (`reports.stats()` and `reports.accounts()` respectively) **but I could not verify either caller**, since `ledgerkit/reports.py` is outside this dispatch's permitted evidence paths. This is a disclosed boundary of this report, not a finding about the code itself.
9. **`compat.py`'s stated callers** (`ledgerkit/models.py`'s `Journal.balance`/`.register`/`.to_dataframe` and `ledgerkit/reports.py`, both via "lazy, in-function" imports per its own docstring) **are likewise unverified** — `models.py` is outside my permitted evidence paths. I can confirm `compat.py` exists, is self-consistent, and is exercised correctly by its own 20 tests in `test_compat.py`, but not that any other module actually calls it as described.
10. **`not:depth:...` is rejected at parse time** (confirmed live and by test), but the rejection logic (`_wraps_depth`) is a small bespoke string-stripping loop, not integrated into the general tokenizer/prefix-dispatch path — a token like `not:not:not:depth:2` (three `not:` wraps) was not explicitly tested in the permitted test file (only one and two wraps are), though by inspection `_wraps_depth`'s `while` loop handles an arbitrary wrap count; I did not independently re-verify three-plus levels by execution since the existing one/two-level tests plus code reading gave adequate confidence here.

## 8. compat-register

Not applicable to this dispatch — `dev-docs/compat-register/*.yaml` was not among the permitted evidence paths for the `query-engine` topic, so no compat-register claim is traced or asserted in this report.

# 7. Query language and regex extension plan

## 7.1 Target hledger query semantics (1.52.x baseline)

hledger's query language (`hledger.org/1.52/hledger.html#queries`) is a
space-separated sequence of terms, implicitly AND-ed, each either a bare
pattern (matched against description/account per context) or a
`prefix:VALUE` term. The terms Ledgerkit's compatibility baseline targets,
in priority order (matches what's already partially present via the
`Query` dataclass, extended):

| Term | Meaning | Ledgerkit today |
|---|---|---|
| `acct:REGEX` (and bare pattern) | account name match | `Query.account`, substring-or-regex — informal, not hledger's exact regex dialect |
| `not:` prefix on any term | negation | `Query.not_account` only, not general |
| `desc:REGEX` | description match | `Query.payee`, same caveat |
| `date:PERIODEXPR` | date range | `Query.date_from`/`date_to`, **simple dates only** — hledger's smart/period expressions (`last month`, `2024`, `weekly`) are explicitly "Undecided / Future" in `hledger-compatibility.md` already |
| `tag:NAME[=REGEX]` | tag match | not implemented — `declared_tags` exists but inline tag parsing does not |
| `cur:REGEX` | commodity match | not implemented |
| `depth:N` | tree-depth cutoff | `Query.depth`, present |
| `status:` (`*`/`!`/none) | cleared/pending/unmarked | not implemented as a query term (cleared/pending are parsed fields, just not queryable) |
| `real:`/`virtual:` | posting type | not applicable — virtual postings are `UNSUPPORTED` today (out of scope, `hledger-compatibility.md`) |
| implicit AND, explicit `OR`-by-repetition of same prefix | boolean combination | not implemented — `Query` is a flat AND of distinct fields only |

**Phasing:** `acct:`/`desc:`/`date:`(simple)/`depth:`/`status:`/`not:` are
Stage C's initial target (COMPATIBLE-classified once verified). `tag:`,
`cur:`, and hledger's smart/period date expressions are Stage C follow-on
work, tracked but not blocking Stage C's exit criteria — each gets its own
compat-register entry rather than being bundled as "query done."

## 7.2 Architecture

```
query text  ──▶  ledgerkit/query/parser.py  ──▶  QueryAST
                                                     │
                                                     ▼
                                          ledgerkit/query/eval.py
                                          (AST → predicate over
                                           Transaction/Posting)
                                                     │
                        ┌────────────────────────────┼────────────────────┐
                        ▼                            ▼                    ▼
                  reports.py                    ledgerkit CLI       future MCP/
                  (balance/register/            (--query flag,      other adapters
                   accounts/stats)               argument parsing)
```

`QueryAST` node types (illustrative, finalised at implementation time by
the lead + `hledger-researcher`, not fixed here): `Term` (leaf: a single
`prefix:value` or bare pattern), `And`, `Or`, `Not`. Each leaf carries
which **regex dialect** (§7.3) produced its pattern, so evaluation and
portability-reporting (§7.5) share one representation.

**No report function embeds its own filtering logic.** `reports.py`
consumes a compiled `QueryAST` (or `None`) uniformly — this directly
implements the task's instruction not to "embed query semantics separately
into each report or CLI command." The existing `Query` dataclass becomes a
compatibility constructor that compiles to a `QueryAST` (§6.5) rather than
a parallel filtering path.

## 7.3 Regex: `HledgerRegex` vs `PythonRegex`

hledger's own regex documentation (1.52 manual, "Regular expressions"
section) specifies: POSIX-derived, case-insensitive by default, infix
(substring) matching, implemented via Haskell's `regex-tdfa`. Python's `re`
module is PCRE-inspired, case-sensitive by default, and — critically —
**not the same engine**: POSIX bracket expressions (`[[:alpha:]]`), leftmost-
longest POSIX matching semantics, and some escaping conventions differ from
Python `re`, while Python `re` additionally offers lookaround,
backreferences, and named groups that `regex-tdfa` (as hledger exposes it)
does not.

```
RegexExpression
    ├── HledgerRegex   — the hledger-compatible subset: case-insensitive by
    │                    default, infix matching, restricted to constructs
    │                    that behave identically under Python `re` and
    │                    hledger's regex-tdfa (literals, `.`, `*`, `+`, `?`,
    │                    character classes without POSIX names, alternation
    │                    `|`, anchors, simple backreference-free groups).
    │                    A pattern using a construct outside this subset is
    │                    an `UNSUPPORTED` or `UNEXPLAINED_MISMATCH` compat-
    │                    register condition, never silently reinterpreted.
    │
    └── PythonRegex    — full Python `re` power: lookarounds, named groups,
                         backreferences, non-greedy quantifiers beyond what
                         hledger exposes, structured capture extraction.
                         Requires explicit syntax to invoke (§7.4) — never
                         the default interpretation of a bare query term.
```

**Hard rule, directly from the task:** Ledgerkit never silently
reinterprets hledger-compatible regex syntax using Python semantics where
the two differ. A pattern that hledger would interpret one way and Python
`re` would interpret differently gets flagged (compat register entry,
`INTENTIONAL_DIVERGENCE` or `UNSUPPORTED`, verified against the real
`hledger` binary by `compat-differential-tester`) — it is never quietly
"fixed" to whatever Python happens to do.

## 7.4 Syntax for invoking the Python extension

Explicit dialect marker, not a global mode switch — a query mixing
portable and extended terms must stay legible about which is which. Exact
syntax decided at Stage C implementation (candidates: a `pyre:PATTERN`
term prefix analogous to hledger's own `prefix:` convention, or a
`Query(..., regex_dialect="python")` keyword on the Python API side) —
**not fixed here**, but the constraint is fixed: it must be visually
distinguishable in both the query-string surface and the Python API
surface, and it must never be the default.

**No `eval()`.** Python-regex capabilities are exposed only through the
registered `PythonRegex` node type feeding the same `QueryAST` evaluator —
never arbitrary Python expression evaluation, per the task's explicit
prohibition. Any future extension predicate (beyond regex) follows the same
pattern: a new explicitly-registered AST node type, never a string handed
to `eval`/`exec`.

## 7.5 Portability classification

```
portable:
    Ledgerkit ✓
    hledger   ✓
    → every HledgerRegex-dialect term, verified byte-for-byte against the
      real hledger binary on the pinned 1.52.x baseline

ledgerkit extension:
    Ledgerkit ✓
    hledger   ✗
    → every PythonRegex-dialect term, and any query prefix (e.g. future
      Ledgerkit-only filters) with no hledger equivalent at all
```

A `QueryAST` (or the query-string form) can be inspected for its
portability classification programmatically — a Python API function
(finalised at implementation time, e.g. `ledgerkit.query.is_portable(q)`)
returning which terms are portable vs extension, so a caller (or
`ledgerkit-editor`'s future filter UI) can warn a user "this saved filter
won't work if you switch to real hledger," rather than that being a fact
only discoverable by reading source.

## 7.6 Tests and compatibility records

- **Golden tests:** a fixture journal + a query string + expected
  `QueryAST` shape + expected filtered result — ordinary unit tests,
  `tests/test_query/`.
- **Differential tests** (`compat-differential-tester`'s responsibility,
  Stage C onward): the same fixture + `HledgerRegex`-dialect query run
  through both `ledgerkit` and the pinned `hledger` binary; results must
  match exactly for the query to be registered `COMPATIBLE`.
- Every `HledgerRegex` construct excluded from the compatible subset (POSIX
  classes, engine-specific edge cases) gets its own compat-register entry
  explaining *why*, backed by an executable-verified example showing the
  actual hledger behaviour it diverges from — not just a citation of the
  manual.
- Every `PythonRegex` capability gets a compat-register entry with
  `kind: extension`, `relationship: superset`, matching the task's own
  `LK-EXT-QUERY-001` example almost exactly — see
  `dev-docs/compat-register/examples/LK-EXT-QUERY-001.yaml`, drafted as
  part of this planning package to prove the schema against a real case
  before Stage C implementation begins.

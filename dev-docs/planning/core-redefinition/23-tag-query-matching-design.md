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

### 2.5 `accounts`' third matching mode — [VERIFIED-EXTERNAL, genuinely new relative to brief 19]

Brief 19 §6 named two hledger code paths for account-name-level `tag:`
matching (bare `matchesAccount` never sees tags at all; `--declared`
mode uses only declared+inherited tags). **A third, distinct mode exists
that brief 19 did not name**: plain `accounts tag:X` (the default,
non-`--declared` mode) builds its list via
`journalPostingsKeepAccountTagsOnly` — confirmed, by direct source read,
to be called from **exactly one place**,
`hledger/Hledger/Cli/Commands/Accounts.hs:73` — which strips a posting's
**own** inline-comment tags specifically before matching, while leaving
transaction-level and account-inherited tags untouched. Live-confirmed:
a posting-line-only tag is invisible to plain `accounts tag:X`; an
otherwise-identical transaction-header-line tag is matched.

**This means `accounts` has a real, `tag:`-specific behavioural wrinkle
— a different shape from `depth:`'s wrinkle** (`depth:` needed a
report-display side-channel, `DepthSpec`, threaded through every report
function; `tag:`'s `accounts` wrinkle is narrower: one command, one
matching-mode substitution, no side-channel needed). See §7 for the
concrete implication and §9 for the open question this raises.

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
- **[EXISTING-DECISION]** `ledgerkit/tags.py` (Phase 4) already parses
  and stores exactly the three tag scopes hledger's `tag:` term reads
  from: `Posting.tags`, `Transaction.tags`, `Journal.declared_account_tags`.
  The data model is correct and sufficient — confirmed no new field is
  needed on any of these three. What's missing is purely the
  computation that combines them (§4).
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

## 4. What's actually missing: the inheritance computation

**[VERIFIED-EXTERNAL + EXISTING-DECISION, synthesised]**: hledger's
`tag:` reads from the union of a posting's own tags, its transaction's
own tags, and its account's declared-and-inherited tags (§2.2's rules
A-D). Ledgerkit's `Posting.tags`/`Transaction.tags` hold only each
entity's **own** literal inline-comment tags — confirmed by direct read
of `ledgerkit/parser.py:894-896` (`txn.tags = parse_tags(txn.
inline_comment)`, same pattern for postings) and `ledgerkit/tags.py`
(five functions total: `parse_tags`, `_parse_comment_line_tags`,
`effective_date`, `effective_date2`, `_tag_name_before_colon` — no
inheritance function exists). `Journal.declared_account_tags` is
populated correctly from `account NAME ; tag:value` directives but has
**no consumer anywhere** in the current codebase — confirmed by grep.

Implementing `tag:` correctly therefore requires a genuinely new
computation, not just an AST node + eval branch (which is all `acct:`/
`desc:`/`status:` ever needed). This is the central design fork — see
§5's two options.

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
branch. The two options differ in what that branch actually computes —
see §9.

### 5.4 `__init__.py` — [PROPOSED]

Export `Tag` from `ledgerkit.query`'s `__all__`, alongside the existing
`MaxAccountLevel`/`DepthSpec` exports.

## 6. Transaction-level and posting-level matching, explicitly

- **Posting-level** (`matches_posting`, used by `balance`/`register`/
  `accounts` default mode): a posting matches `tag:X` if `X` is in its
  **effective** tag set — which option (§9) determines whether that's
  "own tags only" or "own + transaction's + inherited-account's," per
  §2.2's rules.
- **Transaction-level** (`matches_transaction`, used by `print`): a
  transaction matches `tag:X` if **any** of its postings' effective tag
  sets contain `X` (rule D) — this part is not contingent on §9's
  inheritance-scope question; it's the same "any posting matches" pattern
  `Acct`/`MaxAccountLevel` already use in `matches_transaction`
  (`eval.py`, confirmed).

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

**Option A — full inheritance (rules A-D), matching hledger exactly.**

Requires: a new `ledgerkit/tags.py` function (something like
`effective_tags(journal, txn, posting) -> list[tuple[str, str]]`
combining `posting.tags + txn.tags + inherited account tags`) **and**
threading `Journal` into `matches_transaction`/`matches_posting`'s
signatures (§1's finding — currently neither function receives it, and
this is a documented public signature, `dev-docs/api-spec.md` lines
1093+). Cost: a second protected-surface API change beyond §5.1's new
`Tag` node; every one of `reports.py`/`cli.py`'s four call sites needs an
added argument (mechanical, `journal` is already in scope at each site,
but still a real, reviewable diff).

Benefit: matches hledger exactly, no disclosed divergence, closes brief
19's `LK-COMPAT-QUERY-TAG-INHERIT-001` (currently "blocked") cleanly.

**Option B — literal-own-tags-only, disclosed Ledgerkit-native subset
first (mirroring the `MaxAccountLevel` precedent).**

`tag:` matches only each posting's/transaction's own literal inline-
comment tags (rules B/C's "own" half, no rule A account-inheritance).
No `Journal` threading needed — `matches_posting`/`matches_transaction`
keep their current signatures untouched. Ships faster, smaller diff,
zero new protected-surface changes beyond §5.1's `Tag` node itself.

Cost: a real, disclosed divergence from hledger — `tag:` on an account
with declared-but-not-locally-repeated tags would silently under-match
relative to real hledger. Would need its own compat-register entry
(`kind: intentional_divergence` or `unsupported`, not `compatible`) and
prominent documentation, the same way `MaxAccountLevel` was disclosed
rather than silently shipped as if it were `depth:`.

**Lead's recommendation, not a decision**: Option A. The `depth:`
precedent (Stage C Phase 5) specifically chose to build the real thing
rather than ship and disclose a narrower divergence when the real thing
was tractable — and here, unlike `depth:`, there is no known *conflicting*
prior expectation to break (no existing Ledgerkit `tag:` behaviour exists
to diverge from). The `Journal`-threading cost is real but mechanical and
one-directional (add a parameter, thread it through four already-`journal`-
scoped call sites) — smaller in practice than Phase 5's `DepthSpec`
side-channel redesign. But this is the lead's judgement, not a resolved
fact — explicit approval required either way.

### 9.2 [UNRESOLVED] `accounts` command's matching mode

Per §2.5/§7: does Ledgerkit's `accounts -q "tag:X"` replicate hledger's
posting-own-tag-stripping behaviour (a real, source-confirmed hledger
quirk, structurally similar in *kind* — though not in mechanism — to
`stats`' own disclosed depth-exclusion exception from Phase 5), or use
uniform matching (same effective-tag computation as every other command,
simpler, one fewer special case)?

**Lead's recommendation, not a decision**: uniform matching (no special
case), **disclosed** as an intentional divergence in `dev-docs/
hledger-compatibility.md` if so — mirroring how `MaxAccountLevel`/`depth:`
divergences are handled: pick the simpler, more internally-consistent
behaviour and disclose it, rather than replicate a narrow, single-command
quirk whose value (a query-time convenience for one specific hledger
command's output) is unclear relative to its cost (a second special case
in one phase, on top of §9.1's already-real inheritance-computation cost).
Not resolved by this document either way.

### 9.3 [UNRESOLVED] `Journal.declared_account_tags` API shape for inheritance lookup

If Option A (§9.1) is approved: should ancestor-tag lookup be a new
public function in `ledgerkit/tags.py` (e.g. `_inherited_account_tags
(journal, account) -> list[tuple[str, str]]`, private, or public?), or
folded directly into `effective_tags`'s own body with no separately
exposed helper? Affects `dev-docs/api-spec.md`'s eventual documented
surface. Not resolved here — an implementation-planning-stage decision
once §9.1 itself is settled.

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
- **If Option A (§9.1) is approved**: `matches_transaction`/
  `matches_posting`'s signatures change (new `journal` parameter) — this
  **is** a breaking change to a documented public function signature.
  Needs explicit sign-off under the Unauthorised Change Rule, and needs
  a decision on whether the parameter is positional-required, keyword-
  only, or given a safe default (e.g. `journal: Journal | None = None`,
  degrading gracefully — but then what does `tag:` do with no `journal`?
  Silently drop rule A, defeating the point of choosing Option A at all?
  This sub-question is not resolved here — flagged for whoever writes
  the implementation plan if Option A is approved).
- No change proposed to `Posting`/`Transaction`/`Journal`'s own dataclass
  fields (§3) — existing Phase 4 shapes are sufficient.

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
  if `effective_tags`/inheritance logic is added to `ledgerkit/tags.py`.
- `docs/usage.md` — user-facing `-q "tag:..."` examples, mirroring the
  existing `depth:` examples added in Stage C Phase 5.
- `knowledge/DECISIONS.md` — whichever of §9.1/§9.2's options gets
  approved, with the rejected alternative and why, matching every prior
  phase's decision-recording convention.
- `knowledge/DOMAIN_RULES.md` — the four inheritance rules (§2.2) and the
  AND-not-OR combination rule (§2.3), as tacit hledger rules Claude can't
  infer from code — same treatment `depth:`'s precedence rules got in
  Phase 5.
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the project's standing
  same-response doc-sync rule, at implementation time.

## 16. Proposed tests

- **Unit** (`tests/test_query/test_parser.py`,
  `tests/test_query/test_eval.py`): `tag:NAME` bare-value matching,
  `tag:NAME=REGEX` value matching, malformed-regex `QueryParseError`,
  empty-value matching, `not:tag:...` negation, multiple `tag:` terms
  AND-combining (§2.3, now with the executable precedent to encode as a
  regression test).
- **Integration** (`tests/test_reports.py`,
  `tests/test_cli/test_cli.py`): `tag:` wired through `-q` for all five
  commands; §9.1's chosen inheritance behaviour exercised on a fixture
  with account-directive tags, transaction-header tags, and posting-own
  tags in combination (no existing fixture has any tags at all — a new
  fixture, or an extension of an existing one, is needed either way,
  confirmed by the curator's direct check of `filtered.journal`/
  `depth.journal`).
- **Differential** (against the pinned hledger binary, via a genuinely
  separate `compat-differential-tester` dispatch per §10): reproduce
  every scenario in §2 (basic matching, all four inheritance rules if
  Option A, the AND-not-OR combination, the `accounts` mode per §9.2's
  resolution) — the curator's own scratch fixture
  (`tag-verify.journal`, session-local, not committed) is a good starting
  point for what a committed `tests/fixtures/` equivalent should cover.

## 17. Summary of what needs explicit approval (Step 3 gate)

1. **§9.1** — inheritance scope: Option A (full, `journal`-threading
   cost) vs. Option B (own-tags-only, disclosed divergence). Lead
   recommends A.
2. **§9.2** — `accounts` command mode: mirror hledger's posting-tag-
   stripping quirk, or uniform matching (disclosed divergence). Lead
   recommends uniform (no special case).
3. **§9.3** — contingent on §9.1: inheritance-lookup helper's public/
   private shape. Deferred to implementation planning either way, not a
   blocking gate.
4. **General approval** to proceed to Step 4 (implementation planning)
   once 1-2 are resolved.

No implementation begins until this section's items are explicitly
decided.

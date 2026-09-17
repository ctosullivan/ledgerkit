# 21. Stage C Phase 5 plan — Verification independence + `depth:` semantics

Planning only. No `ledgerkit/`/`tests/` code touched. Do not begin
implementation until the human decision gates in §9 are resolved.

## 0. Pinned revisions

- Ledgerkit: `fd144ed` (Stage C Phase 4, "tag data model" — HEAD at the
  time this plan was written)
- hledger: `1.52.4`, commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`
  (source clone: `/home/cormac/projects/hledger`; pinned binary:
  `/home/cormac/.local/bin/hledger`, `1.52.4-g33fa849e7-20260910`)

---

## 1. Current-state assessment

### 1.1 Verification independence — what actually happened across Stage C

`compat-differential-tester.md` states plainly: "The only role authorised
to move a compat-register entry out of status:proposed." `dev-docs/
compat-register/README.md` restates it: "Moving any entry to status:
verified is compat-differential-tester's job... requires an actual
comparison run, not a citation of the manual."

Checking every entry actually moved out of `proposed` so far, by reading
each YAML's `verified_by` field directly:

| Phase | Entries touched | `verified_by` |
|---|---|---|
| 1 | 7 entries added, all `status: proposed` | n/a — correctly left proposed |
| 2 | 6 entries (5→`verified`, 1 corrected) | `"Claude (lead session, Stage C Phase 2 implementation — not a separately-dispatched compat-differential-tester agent...)"` |
| 3 | 1 entry (`LK-COMPAT-QUERY-PRINT-INTEGRATION-001`) | `"Claude (lead session, Stage C Phase 3 implementation)"` |
| 4 | 4 entries | `"Claude (lead session, Stage C Phase 4 implementation)"` |

**Every entry this project has ever marked `status: verified` (11 across
three phases) was verified by the same session that implemented the
feature being classified.** This is not an oversight nobody noticed —
Phase 2's own retro flagged it explicitly under "What didn't work": *"the
process the plan designed specifically to keep implementation and
verification separate wasn't actually followed... a lead already holding
the context and the tools for a task will default to just doing it, even
when the plan specifically separated that step for a reason."* That
lesson was filed as prose in a retro, not converted into anything that
would actually stop it from recurring — and it recurred, identically, in
both Phase 3 and Phase 4.

This is not hypothetical risk. It already produced one concrete, caught
error: `LK-COMPAT-QUERY-DEPTH-001`'s Phase 1 `compatible` classification
was wrong (see §1.2/§1.3), and shipped as `proposed` truth for several
days before Phase 2 happened to re-run it and catch the error. Phase 2's
own correction is real and good work — but it worked *despite* the
independence gap, not because of it: the same lead who would have
proposed the wrong classification also happened to be the one who
re-checked it. Nothing in the current process guarantees that a wrong
`verified` claim (as opposed to a wrong `proposed` one) ever gets a
second, independent look before something else depends on it.

### 1.2 `depth:` — what actually happened across Stage C

- Phase 1 (`17-query-semantics-brief.md` §4, reading hledger source only,
  no executable): classified `ledgerkit.query.ast.Depth` as `compatible`/
  `equivalent` — a pure boolean predicate, `accountNameLevel(a) <= N`.
- Phase 2 (executable-verified against the pinned binary for the first
  time): found `hledger balance depth:1`/`register depth:1` truncate and
  aggregate, never exclude; reclassified `LK-COMPAT-QUERY-DEPTH-001` to
  `intentional_divergence`/`incomparable`. `print depth:1` was tried too,
  found unaffected either way, and left as an explicitly unresolved
  observation ("not fully explained by this session's testing").
- Phase 3: wired `-q` into `print`, inheriting whatever `matches_
  transaction`'s `Depth` branch does — not re-examined against the still-
  open `print`+`depth:` question from Phase 2.
- This phase (research pass): resolves the `print` question definitively
  (§1.3) and surfaces a second, more serious problem not previously
  recorded anywhere — §1.2b below.

### 1.2b A previously unrecorded finding: Ledgerkit already has two mutually-inconsistent `depth` models

Reading `ledgerkit/reports.py` directly (not from memory of prior
phases) found that `ledgerkit.models.Query.depth: int | None` — a
**pre-existing, pre-Stage-C public field**, unrelated to the `-q` string
grammar — already has **correct**, hledger-matching truncation semantics,
and `reports.py` says so explicitly in its own docstrings:

```python
# reports.py:379-381
Note on depth: depth in the query causes account names to be *truncated*
(rolled up) rather than excluded — matching hledger's --depth behaviour.
expenses:food:groceries at depth=2 contributes to expenses:food.

# reports.py:369-372
Unlike `query`, _query_ast has no depth term with truncation semantics —
a Depth node in the AST excludes postings (the query.eval predicate
meaning), it does not truncate displayed account names.
```

`balance()` (reports.py:383-401) implements this correctly for
`query.depth`: it strips `depth` from the matching query so postings
aren't excluded, then truncates the account name string manually before
aggregation — precisely hledger's own strip-then-clip pattern (confirmed
independently in §1.3). This code already exists and already works. It
is simply unreachable from the `-q "depth:N"` string path, which instead
goes through `ledgerkit.query.ast.Depth`'s exclusion semantics.

**This means the `depth:` problem is not only "Ledgerkit diverges from
hledger" — it is "Ledgerkit's own two depth mechanisms disagree with each
other."** `ledgerkit.reports.balance(journal, query=Query(depth=1))` and
`ledgerkit balance -q "depth:1"` currently produce different, incompatible
results on the same journal, inside the same codebase, today. Any fix
should converge these, not just point the newer one at hledger
independently of the older one.

Also newly noted while reading `reports.py`: line 477's own comment,
`# TODO: Apply account-level query filters to account_count and
account_depth`, in `stats()` — confirms `stats` was never wired for
depth-sensitive filtering via either mechanism; §1.3/§6 below establish
what it *should* do.

### 1.3 Authoritative hledger `depth:` semantics (manual + source + pinned binary, this session)

**Manual** (`hledger.1`, `.SH Depth`, lines 7054-7098; `.SS depth: query`,
lines 7324-7332):

- `--depth NUM` (short form `-NUM`) ≡ `depth:NUM` — reports show accounts
  only to the given depth, "hiding deeper subaccounts."
- `--depth REGEX=NUM` (since 1.41) ≡ `depth:REGEX=NUM` — collapses only
  accounts matching REGEX to depth NUM; others unaffected.
- **Multiple general depth options**: last one wins.
- **Mixed general + custom**: "the most specifically (deepest) matching
  option wins" — worked examples given in the manual and reproduced
  below.
- Overriding a custom `REGEX=NUM` with a later option requires repeating
  the same REGEX.

**Source** (`hledger-lib/Hledger/Query.hs`, `Hledger/Data/AccountName.hs`,
`Hledger/Data/Types.hs`, plus every command module that consumes a
`Query`):

- `Query` *does* have a real `Depth Int` / `DepthAcct Regexp Int`
  constructor, and `matchesAccount (Depth d) a = accountNameLevel a <= d`
  (`Query.hs:876-877`) is a genuine boolean predicate — confirmed by
  hledger's own test suite (`Query.hs:1150-1152`,
  `Depth 2 \`matchesAccount\` "a:b"` etc.). Phase 1's source reading was
  not fabricated — this function is real.
- **But every single command that turns a `Query` into report output
  strips `Depth`/`DepthAcct` out of the query used to select/include
  postings, before that query is ever used for inclusion, and instead
  re-derives a `DepthSpec` used purely for display-name clipping and
  aggregation:**

  | File | Line(s) | What it does |
  |---|---|---|
  | `Reports/MultiBalanceReport.hs` (balance, register `--interval`) | 211, 237-238 | `depthlessq = filterQuery (not . queryIsDepth) query` selects postings; `depthSpec = queryDepth . filterQuery queryIsDepth $ ...` clips display names separately |
  | `Reports/PostingsReport.hs` (register) | 74, 174 | same split |
  | `Reports/EntriesReport.hs` (**print**) | 42 | `filterJournalTransactions (filterQuery (not.queryIsDepth) $ _rsQuery rspec)` — depth is stripped and **never reapplied**; `EntriesReport.hs` calls no clip function anywhere |
  | `Cli/Commands/Accounts.hs` (accounts) | 65-66, 69, 108-109 | same split, comment at line 65 literally reads *"a depth limit will clip and exclude account names later, but we don't want to exclude accounts at this stage"* |
  | `Reports/AccountTransactionsReport.hs` (aregister) | 105 | strips depth too — matches the manual's own note that `aregister` "ignores depth limits" |
  | `Data/Ledger.hs` | 62 | same split, for the ledger-account-tree view |

  `getAccountNameClippedDepth` (`AccountName.hs:347-372`) implements the
  manual's precedence rule exactly: among regex rules matching the
  account or any ancestor, the one with the greatest "specificity" (the
  shallowest ancestor at which it starts matching) wins; ties go to the
  later-declared rule; falls back to the flat depth if no regex matches.

- **Conclusion: `depth:` is never a selection/exclusion predicate in any
  of hledger's real report-generating commands.** The `Depth`/`DepthAcct`
  boolean-predicate function exists in the library and is exercised by
  the library's own unit tests, but no shipped command path ever calls it
  for inclusion — Phase 1's mistake was reading one function's type
  signature and treating it as *the* semantics of `depth:`, without
  tracing whether any command actually invokes it that way. None do.

**Pinned binary** (this session, fixture built at
`tests fixture depth.journal` under this session's scratchpad — 8
accounts, depth 2-4, includes an `assets:bank:savings` sibling
specifically to exercise the manual's own worked precedence example):

| Command | Result (abbreviated) |
|---|---|
| `balance --depth 1` and `balance depth:1` | Identical: 4 aggregated rows (`assets`, `equity`, `expenses`, `income`), full totals |
| `balance --depth 0` | 1 row: `...` = 0 (never excludes; clips to ellipsis) |
| `balance -1` | Identical to `--depth 1` (short-form flag confirmed equivalent) |
| `balance --depth assets=1` | `assets` collapsed to one row; every other account shown at full depth, unaffected |
| `balance --depth assets=1 --depth savings=2` | `assets` total net of the savings transfer only (manual's own worked example — `assets:bank:savings` follows the more specific `savings=2` rule, not `assets=1`) |
| `balance --depth assets=3 --depth expenses=2 --depth 1` | `assets:bank`/`assets:cash` (depth 3), `expenses:food`/`expenses:housing` (depth 2), `equity`/`income` (depth 1, the general fallback) — exactly the manual's worked example |
| `balance --depth 1 --depth 2` | Depth-2 output only — confirms "last general wins" |
| `register depth:1` | Every posting shown individually with running balance; account label truncated per row; **none excluded** |
| `register --depth assets=2 acct:assets` | Combines normally (AND) with an ordinary `acct:` term; only `assets*` postings shown, truncated to depth 2 |
| `print depth:1` | **Every transaction shown in full, every account name untouched** — resolves Phase 2's open question definitively: `print` does not special-case depth at either the selection or display layer, it simply never consults it (matches `EntriesReport.hs` source exactly) |
| `accounts --depth 2` | Account list deduplicated and clipped to depth 2 (list shrinks, entries merge — not filtered) |
| `accounts 'depth:assets=1'` | `assets`-matching accounts collapsed to `assets`; everything else shown at full depth |
| `stats --depth 1` vs `stats` (no depth) | `Accounts` count and reported max depth both change (8/depth 4 → 3/depth 2 at `--depth 2` in a spot check) — `stats` genuinely is depth-sensitive |

Current Ledgerkit (`-q "depth:N"`, same fixture, this session):

| Command | Ledgerkit's current result |
|---|---|
| `balance -q "depth:1"` | **0 rows** (every posting excluded — EC-017, already known) |
| `register -q "depth:1"` | **empty output** (same exclusion) |
| `accounts -q "depth:2"` | Accounts *filtered* (deeper ones dropped), not clipped/deduplicated — a third, distinct wrong behaviour not previously documented |
| `print -q "depth:1"` | **empty output** — actively wrong in the opposite direction from hledger's "show everything unaffected"; not merely an "open question" any more, it is a confirmed defect |

This table is the phase's differential-test matrix (§6 restates it in
implementation-facing form); every cell above was produced by an actual
run this session, not inferred.

---

## 2. Compatibility/verification process amendment

**Principle:** the process overhead should scale with how strong a claim
is being made about hledger compatibility, not with how large the code
change is. A large refactor that touches no compatibility claim needs no
new process at all; a one-line reclassification of an existing `verified`
entry's `kind` needs the same independence a brand-new feature would.

### 2.1 Claim-strength tiers

| Tier | Trigger | Requirement |
|---|---|---|
| **0 — no compatibility claim change** | Ordinary implementation, refactor, or bugfix that does not add, remove, or change any `dev-docs/compat-register/*.yaml` entry's `kind`, `relationship`, or `status` | Normal lead verification: tests pass, judgment applied. No dispatch. |
| **1 — proposed classification** | A new entry is drafted, or an existing entry's `reason`/`kind` is *proposed* to change, but not yet promoted past `status: proposed` | `hledger-researcher` (or the lead reading source/manual directly) may propose freely. Already the existing, correctly-followed process (Phase 1 is the model instance) — no change needed here. |
| **2 — promotion to independently-verified truth** | An entry's `status` is set to `verified` for the **first time**, or an already-`verified`/`final` entry's `kind`/`relationship` is **changed** | MUST come from an actual `compat-differential-tester` Agent dispatch's own returned output. The lead may never write `status: verified` into a register YAML directly — that field is the dispatched agent's alone to set, structurally (see §2.3). |
| **3 — finalisation** | `status: final` | Already requires doc reconciliation per `schema.md`; now additionally requires that the Tier 2 evidence packet (§2.4) is referenced from the entry, not just asserted to exist. |

Tier 0 is the answer to "avoid unnecessary agent/process overhead for
trivial work" — the overwhelming majority of day-to-day changes (most of
Phase 4's own work, for instance — new fields, a new module, doc sync)
never touch a compat-register `status`/`kind` at all and are completely
unaffected by this amendment.

### 2.2 New `status` value: `self-verified`

The current schema (`dev-docs/compat-register/schema.md`) only has
`proposed | verified | final`. This collapses two genuinely different
situations into one word ("verified"): *"a comparison was actually run"*
and *"a comparison was actually run by someone other than the person who
built the thing being compared."* Every entry in §1.1's table is the
first kind wearing the label of the second.

Add a fourth value, inserted between `proposed` and `verified`:

```
status: proposed | self-verified | verified | final
  # proposed       — hledger-researcher's reading; no comparison run yet
  # self-verified  — an actual hledger-vs-Ledgerkit comparison WAS run
  #                   this session, with real command output, but by the
  #                   same identity/session that implemented the feature
  #                   under test — not yet independently confirmed
  # verified        — compat-differential-tester (a separately-dispatched
  #                   agent, never the implementing session) has executed
  #                   the comparison independently
  # final           — verified, AND docs reconciled and cross-linked
```

This directly satisfies "if independent review is deferred, use an
explicitly provisional status rather than claiming independent
verification" — `self-verified` is honest about exactly how much
confidence the entry deserves (more than a citation-only `proposed`, less
than an independently-reproduced `verified`), without inventing busywork
for cases where the lead's own executable check is genuinely all that's
warranted in the moment.

### 2.3 Making Tier 2 structurally checkable, not just a convention

The gap in §1.1 happened because "dispatch `compat-differential-tester`"
was a *should*, easy to skip under time pressure with the fixture and
binary already at hand. To make it a checkable fact rather than a
recalled intention:

- A phase's retro (already mandatory, `dev-docs/retros/`) must name, for
  every register entry it touches, whether the entry ended the phase at
  `self-verified` or `verified` — and if `verified`, cite the specific
  Agent dispatch that produced it (agent name/description used in the
  `Agent` tool call). This is already the kind of thing retros record
  (Phase 2's own retro already did this narratively); this amendment just
  makes it a required field of "What was achieved," not optional colour.
- `release-phase-auditor` (already an existing, read-only audit role that
  checks retros/tests/docs exist per phase) gains one more checklist
  item: for any entry newly at `status: verified`/`final` in the phase's
  diff, confirm the retro names an actual `compat-differential-tester`
  dispatch for it — flag as a non-blocking observation otherwise (not a
  hard FAIL, since `release-phase-auditor` never repairs what it audits;
  it surfaces, the user decides).

No new tooling is invented — `compat-differential-tester` and
`release-phase-auditor` already exist with exactly the write-access
restrictions and independence properties this needs
(`compat-differential-tester.md`: "Never edit `ledgerkit/` source to make
a mismatch disappear... Report it back to the lead" — already the
"assess evidence, not silently fix implementation" rule the request asks
for, already correctly designed, simply not being invoked).

### 2.4 Evidence packet (what the lead hands the dispatched verifier)

A fixed, compact shape so a Tier 2 dispatch never has to reconstruct
context from scratch:

```
Ledgerkit revision:   <commit hash>
Upstream revision:    hledger <version>, commit <hash>, binary <exact version string>
Register entry:       <LK-...-NNN id(s) affected>
Fixture(s):            <path(s) under tests/fixtures/, or fixture text to create>
Commands to run:       <exact hledger command> vs <exact ledgerkit command>, per scenario
Proposed interpretation: <kind + relationship the lead believes applies, and why>
Prior evidence:         <what the lead already observed, explicitly labelled
                         as self-verified / not yet independent>
```

This is exactly the shape `compat-differential-tester.md`'s own "What to
do" list already implies (fixture, both binaries, exact diff, finalise
kind/status) — §2.4 just names the packet so the lead has a checklist for
what to include in the dispatch prompt, rather than reconstructing it
ad hoc each time.

### 2.5 Retroactive handling of the 11 existing entries

Out of scope for "no broad implementation," but small and mechanical
enough to flag as the first concrete implementation step once approved
(§8, Phase 5a): relabel the 11 entries in §1.1's table from `verified` to
`self-verified` — the evidence and reasoning in each stays exactly as
written (it is real, reproducible executable evidence; nothing about
*that* is in question), only the `status`/`verified_by` framing changes
to say honestly who ran it. Whether to then also dispatch real
`compat-differential-tester` re-verification on all 11 immediately, or
let it happen opportunistically as each area is next touched, is
Gate G-PROCESS-2 (§9).

---

## 3. Proposed `depth:` semantic model

A `DepthSpec` concept — named to match hledger's own, since it describes
the same real-world thing, not a Ledgerkit invention:

```python
@dataclass(frozen=True)
class DepthSpec:
    """Report-display depth clipping/aggregation — never a selection filter.

    flat: general depth (--depth N / depth:N), or None.
    by_pattern: (regex, depth) pairs from depth:REGEX=N / --depth REGEX=N,
        in declaration order. Precedence when resolving one account:
        the pattern matching at the greatest specificity (shallowest
        ancestor where it starts matching) wins; ties go to the
        later-declared pattern; if none match, fall back to `flat`.
        Mirrors hledger's getAccountNameClippedDepth exactly (§1.3).
    """
    flat: int | None = None
    by_pattern: tuple[tuple[str, int], ...] = ()
```

with two pure functions (new module, see §4):

- `clipped_depth_for_account(spec, account) -> int | None` — resolves the
  precedence rule, returns the depth to clip to, or `None` for "don't
  clip."
- `clip_account_name(spec, account) -> str` — applies it; depth `0`
  produces the literal string `"..."` (confirmed live, §1.3), never an
  empty string or exclusion.

**`DepthSpec` is never a `QueryNode`.** It carries no selection/exclusion
meaning at all — every hledger command-level behaviour observed in §1.3
is consistent with treating `depth:`/`--depth` purely as a report-shaping
option, never as a filter term, full stop. This directly matches the
target architecture the request proposes:

```
query text
    ↓
parser
    ↓
QueryPlan
    ├── selection predicate AST   (QueryNode: Acct/Desc/DateSpan/Status/And/Or/Not — no Depth)
    └── report/query options
          └── DepthSpec
```

Ledgerkit's pre-existing `models.Query.depth: int | None` and
`models.ReportSection.depth: int | None` (§1.2b) are the flat-only
special case of this same concept, already correctly implemented — this
plan unifies rather than replaces them (§5, §9 gate G-DEPTH-2).

### 3.1 What happens to `ledgerkit.query.ast.Depth` (the current boolean-exclusion node)?

Three options were weighed, as the request asks:

- **Remain as-is, meaning "accountNameLevel(a) <= N," reachable via the
  literal `depth:N` token**: rejected. Keeping a node that reuses
  hledger's exact token spelling for genuinely different semantics is a
  durable trap for any user or future contributor who reasonably assumes
  `depth:` means what it means everywhere else — not a disclosed
  extension. `schema.md`'s `extension_requires_explicit_syntax` bar
  (extensions must be reachable only via syntax that doesn't collide with
  upstream) is structurally failed by reusing the identical token; this
  is presumably *why* Phase 2 already classified it `intentional_
  divergence` rather than `extension` even under the old model.
- **Remove entirely**: rejected as unnecessarily destructive. A pure "is
  this posting at or shallower than depth N, yes/no" predicate is a real,
  independently useful primitive with no other current spelling (e.g. a
  Python caller who wants top-level-only accounts with zero display-
  truncation side effects) — there is no reason to delete working,
  tested logic just because its current name/token collides with
  hledger's.
- **Rename/re-express, kept as a Ledgerkit-native primitive
  (recommended)**: keep the boolean-predicate node under a
  non-colliding name (e.g. `MaxAccountLevel`), and make it **reachable
  only from the Python `ledgerkit.query.ast`/`QueryNode` API, never from
  the `-q`/`--query` CLI string grammar**. This means `-q "depth:..."` in
  the CLI *always* means hledger-compatible `DepthSpec` semantics — no
  ambiguity a user typing `depth:` could ever hit — while the boolean
  form stays available, clearly disclosed as Ledgerkit-native, for
  Python-API callers composing `QueryNode` trees directly and who
  explicitly want exclusion rather than display-clipping.

Recommendation: the third option. Final call is Gate G-DEPTH-3 (§9).

---

## 4. Impact on existing AST/parser/evaluator

- **`ledgerkit/query/ast.py`**: remove `Depth` from the `QueryNode`
  `Union` (or rename it per §3.1's gate outcome, and exclude it from any
  string-parseable term regardless of name). `matches_transaction`/
  `matches_posting` in `eval.py` lose their `Depth` branch entirely —
  simpler, not more complex, code.
- **New module `ledgerkit/query/depth.py`** (mirrors Phase 4's own
  precedent of giving one cohesive concept its own small module rather
  than growing an already-large file — `parser.py` is already the
  largest file in the codebase): `DepthSpec`, `clipped_depth_for_account`,
  `clip_account_name`.
- **`ledgerkit/query/parser.py`**: `_build_depth`/`_PREFIX_BUILDERS
  ["depth:"]` stop producing a `QueryNode` folded into the AND-combined
  term list; instead accumulate into a `DepthSpec` returned *alongside*
  the selection AST. This changes `parse()`'s return type/signature
  (currently `-> QueryNode`) — a public-API-facing change, hence a
  `dev-docs/api-spec.md` update and Unauthorised-Change-Rule gate. Likely
  new shape: `parse(text) -> QueryPlan` where `QueryPlan` bundles
  `(predicate: QueryNode, depth: DepthSpec)`, matching the request's own
  target architecture directly rather than approximating it.
- **`ledgerkit/query/eval.py`**: `Depth`/`DepthAcct` isinstance branches
  removed from `matches_transaction`/`matches_posting`.
- **`ledgerkit/reports.py`**: `balance`/`register`/`accounts`/`stats`
  thread the new `DepthSpec` (from `_query_ast`'s `QueryPlan`, or the
  legacy `query.depth`/`section.depth` int) through the *same* strip-
  then-clip code path `balance()` already implements correctly for
  `query.depth` (§1.2b) — generalising it to accept a full `DepthSpec`
  rather than a bare `int`, instead of maintaining two parallel
  mechanisms. `accounts()` gains the clip-and-deduplicate behaviour it
  currently lacks entirely (§1.3's `accounts --depth 2` row). `stats()`
  resolves its own `# TODO: Apply account-level query filters to
  account_count and account_depth` (reports.py:477) as part of this
  work, not left open again.
- **`ledgerkit/cli.py`**: at minimum, `-q "depth:N"`/`-q
  "depth:REGEX=N"` start producing hledger-equivalent output across all
  five report/display commands. A standalone `--depth`/`-N` flag
  (independent of `-q`, matching hledger's own `depth:2` ≡ `--depth=2` ≡
  `-2` equivalence) is a natural companion but may be deferred — Gate
  G-DEPTH-4 (§9).
- **`print` specifically**: per §1.3's now-definitive finding, `print`
  must be made to **ignore depth entirely** — no exclusion, no
  truncation — for both `-q "depth:..."` and (if added) `--depth`. This
  is a real behaviour change from Phase 3's current wiring (which
  currently makes `print -q "depth:1"` show *nothing*, confirmed live in
  §1.3) — not a new feature, a bug fix restoring what `print` already
  correctly does for every other query term.

---

## 5. Migration strategy for current Ledgerkit behaviour

- **`models.Query.depth`/`ReportSection.depth` (flat int) users**:
  unaffected in behaviour (already correct); only affected if Gate
  G-DEPTH-2 chooses to retype the field itself.
- **`-q "depth:N"` CLI users**: behaviour changes from exclusion to
  truncation. This is a bug fix aligning to the documented compatibility
  target (hledger), not a deprecation — no shim needed per `CLAUDE.md`'s
  "don't use feature flags or backwards-compatibility shims when you can
  just change the code." The current behaviour was never `final`-
  classified or promised stable; its own compat-register entry already
  says `intentional_divergence`, and `knowledge/EDGE_CASES.md` EC-017
  already flags it as an unresolved-quality gap, not a committed
  contract. Real external usage is implausible in any case — Stage C
  Phases 2-3 shipped `-q` on 2026-09-16/17, and this plan follows
  essentially immediately after.
- **Existing tests asserting the current (wrong) exclusion behaviour**
  must be rewritten, not just left passing accidentally. Named
  explicitly so implementation doesn't have to rediscover them:
  - `tests/test_query/test_parser.py::TestBarePatternAndPrefixes::
    test_depth_prefix`, `test_depth_zero_is_valid`,
    `test_depth_negative_rejected`
  - `tests/test_query/test_eval.py::TestDepth`
  - `tests/test_reports.py::TestQueryAstIntegration::
    test_balance_depth_node_excludes_rather_than_truncates` (the name
    itself will need to change — it currently asserts the behaviour this
    plan reverses)
- **`depth:0` docstring/behaviour**: `ast.py`'s current docstring ("n>=0
  is the only valid range — depth:0 is legal input but matches
  essentially nothing") reflects the exclusion model and must be rewritten
  together with the code to describe the `"..."`-clipping behaviour
  confirmed live in §1.3.

---

## 6. hledger differential-test matrix

Restates §1.3's executable findings in the form the implementation and
verification phases (§8) should re-run against, with expected target
Ledgerkit behaviour named explicitly:

| # | Scenario | Commands | hledger (ground truth) | Target Ledgerkit behaviour |
|---|---|---|---|---|
| 1 | General depth | `balance depth:1` / `--depth 1` | 4 aggregated rows | Match |
| 2 | Depth 0 | `balance --depth 0` | 1 row, `...` = 0 | Match — clip to ellipsis, never exclude |
| 3 | Short flag | `balance -1` | = `--depth 1` | Match, if G-DEPTH-4 adds the flag |
| 4 | Custom regex depth | `balance --depth assets=1` | `assets` collapsed; others untouched | Match (new feature) |
| 5 | Two custom regexes, specificity precedence | `balance --depth assets=1 --depth savings=2` | most-specific-match wins per account | Match (new feature) |
| 6 | Mixed general + 2 custom | `balance --depth assets=3 --depth expenses=2 --depth 1` | manual's own worked example | Match (new feature) |
| 7 | Multiple general | `balance --depth 1 --depth 2` | last wins | Match (new feature) |
| 8 | register, general depth | `register depth:1` | every posting shown, truncated, none excluded | Match |
| 9 | register, custom depth + ordinary term | `register --depth assets=2 acct:assets` | AND-combines normally | Match (new feature) |
| 10 | **print, general depth** | `print depth:1` | **unaffected**, full output | Match — currently shows nothing (confirmed defect, §1.3) |
| 11 | accounts, general depth | `accounts --depth 2` | deduplicated, clipped list | Match — currently filters instead of clipping (confirmed defect) |
| 12 | accounts, custom depth | `accounts 'depth:assets=1'` | collapsed for matching accounts only | Match (new feature) |
| 13 | stats, general depth | `stats --depth 1` vs no depth | `Accounts` count/depth both change | Match — currently a no-op (`reports.py`'s own TODO) |
| 14 | Ledgerkit-native boolean predicate (if kept per G-DEPTH-3) | direct `QueryNode` construction, Python API only | n/a — Ledgerkit-only | No `-q` string form; documented as divergent-by-design, not `depth:`-labelled |

Rows 4-7, 9, 12 are genuinely new Ledgerkit capability (custom
`REGEX=NUM` depth does not exist in any form today), not fixes to
existing behaviour — worth calling out explicitly since it changes the
implementation phase's size estimate.

---

## 7. Affected compatibility records / docs

- `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`: reclassify
  from `intentional_divergence`/`incomparable`. Likely destination:
  `compatible`/`equivalent` for the general-depth case, **pending
  independent verification** — this is this phase's own first real test
  of the §2 process amendment (dispatch `compat-differential-tester` with
  the §2.4 evidence packet; do not self-mark `verified`).
- New entries needed for the genuinely new custom-`REGEX=NUM` surface
  (rows 4-7, 9, 12 of §6) — e.g. `LK-COMPAT-QUERY-DEPTH-REGEX-001`,
  proposed by `hledger-researcher` at implementation time, not drafted in
  this planning pass.
- A new entry (or an amendment to `LK-COMPAT-QUERY-PRINT-
  INTEGRATION-001`) recording `print`'s depth-blindness explicitly —
  this closes the "open question" both that entry and EC-017 currently
  carry.
- `knowledge/EDGE_CASES.md` EC-017: mark resolved (never delete — the log
  is a durable record), pointing at the corrected
  `LK-COMPAT-QUERY-DEPTH-001` and the new print-specific entry.
- `dev-docs/hledger-compatibility.md`: the `depth:N` row (line 243)
  rewritten from "intentionally diverges" to reflect the corrected
  semantics; the Query Language section's other depth-adjacent notes
  reconciled.
- `dev-docs/api-spec.md`: `ledgerkit.query.parser.parse()`'s return type,
  `ledgerkit.query.ast.Depth`'s removal/rename, the new `DepthSpec`/
  `QueryPlan` types, and (per G-DEPTH-2) possibly `Query.depth`/
  `ReportSection.depth`'s type — all require the Unauthorised Change
  Rule's explicit pre-approval, restated as Gate G-DEPTH-1/2 below.
- `dev-docs/architecture.md`: `ledgerkit/query/` subpackage description
  updated for the `QueryPlan`/`DepthSpec` split.
- `docs/usage.md`: if a standalone `--depth` CLI flag is added
  (G-DEPTH-4).
- `dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.4:
  amended per §2 (the tiered rule, the evidence-packet template).
- `dev-docs/compat-register/schema.md`: `status:` enum gains
  `self-verified` (§2.2).
- `.claude/agents/compat-differential-tester.md`,
  `release-phase-auditor.md`: wording updated if needed to reference the
  new status value and the retro-field requirement (§2.3) — likely
  small, additive edits, not a rewrite of either role's charter (both
  already do what's needed; this just makes their existing behaviour
  checkable).

---

## 8. Implementation phases and Definitions of Done

**Phase 5a — Process amendment** (small, mechanical, independently
shippable ahead of the depth work):

- Amend `09-compatibility-system.md` §9.4, `schema.md` (`self-verified`),
  the two agent-role files.
- Relabel the 11 existing lead-self-verified entries (§2.5) — pending
  Gate G-PROCESS-2's choice of relabel-only vs. immediate re-dispatch.
- DoD: schema/process docs updated and internally consistent; every
  existing register entry's `status` accurately reflects who actually
  ran its comparison; full test suite unaffected (no `ledgerkit/`/
  `tests/` code touched in this sub-phase).

**Phase 5b — `depth:` semantic model + AST/parser/evaluator/reports
changes**:

- Implement `DepthSpec`/`ledgerkit/query/depth.py`; resolve `ast.Depth`
  per G-DEPTH-3; update `parser.py`'s `depth:`/`depth:REGEX=N` handling
  and its return shape per G-DEPTH-1; remove the `Depth` branches from
  `eval.py`; thread `DepthSpec` through `reports.py`'s `balance`/
  `register`/`accounts`/`stats` via the unified strip-then-clip path;
  fix `print` to ignore depth entirely; add the standalone `--depth`
  flag if G-DEPTH-4 says yes.
- Rewrite the tests named in §5; add new tests for rows 2, 4-7, 9-13 of
  §6.
- Differential-test locally against the pinned binary for every row of
  §6 (this is the lead's own Tier-1-equivalent pass — real evidence,
  informing but not substituting for Phase 5c).
- DoD: full suite green; every §6 row has a passing Ledgerkit test;
  `dev-docs/api-spec.md` updated exactly per the approved gates; no
  compat-register entry touched in this sub-phase is marked past
  `self-verified` yet.

**Phase 5c — Independent verification** (the first real exercise of
Phase 5a's process):

- Dispatch `compat-differential-tester` with the §2.4 evidence packet
  covering `LK-COMPAT-QUERY-DEPTH-001` and any new entries from §7 — the
  dispatched agent re-runs the comparisons independently; this session's
  own §6 matrix is starting evidence for it to check, not something it
  rubber-stamps.
- DoD: affected entries reach `status: verified` **only** via that
  dispatch's own returned output; `EC-017` marked resolved;
  `hledger-compatibility.md` reconciled; no entry finalised (`status:
  final`) without the dispatch's evidence cited.

**Phase 5d — Retro + closeout**: standard per `CLAUDE.md`'s Retro
Reports and Commit & Push Cadence sections; retro must name, per §2.3,
which entries ended at `self-verified` vs `verified` and cite the
dispatch for each `verified` one.

---

## 9. Human decision gates

No implementation begins until these are resolved (per the request's own
"do not begin broad implementation until the plan is approved" and
`CLAUDE.md`'s Unauthorised Change Rule for anything touching
`dev-docs/api-spec.md`):

- **G-DEPTH-1** — Approve the overall semantic model shift: `DepthSpec`
  as a report/query-option, never a `QueryNode` (§3). Foundational; every
  other gate assumes this one is "yes."
- **G-DEPTH-2** — `models.Query.depth`/`ReportSection.depth`'s public
  shape: (a) leave as flat-only `int | None`, with the richer
  regex-capable `DepthSpec` reachable only via the new `-q` string path
  and the Python `query/` package directly, or (b) retype these
  currently-shipped public fields to accept a full `DepthSpec` — a
  breaking type change to existing public API, api-spec.md impact either
  way but (b) materially larger.
- **G-DEPTH-3** — Fate of the current boolean-exclusion `ast.Depth`
  node: remove / rename-and-keep-as-Python-API-only (recommended, §3.1)
  / give it a new non-colliding string token reachable from `-q`.
- **G-DEPTH-4** — Add a standalone `--depth`/`-N` CLI flag (independent
  of `-q`) in this same phase, or defer as a named follow-on.
- **G-PROCESS-1** — Approve the tiered verification-independence rule as
  specified in §2 (four-value `status` enum including `self-verified`,
  the retro-field requirement, `release-phase-auditor`'s new checklist
  item) — or amend it.
- **G-PROCESS-2** — How to handle the 11 existing lead-self-verified
  entries (§2.5): relabel to `self-verified` now and re-verify
  opportunistically over time, vs. dispatch real
  `compat-differential-tester` review on all 11 immediately (thorough,
  costs more now, delays this phase's own start).

---

## Appendix — fixture used for this session's executable checks

`depth.journal` (built under this session's scratchpad, not committed;
a cleaned equivalent should be added under `tests/fixtures/` at Phase 5b
if the scenarios above aren't already covered by an existing fixture):

```
2024-01-01 Opening balance
    assets:cash                    £500.00
    assets:bank:checking:main    £4,500.00
    equity:opening-balances     -£5,000.00

2024-01-15 * Salary
    assets:bank:checking:main    £3,000.00
    income:salary                -£3,000.00

2024-02-01 Rent
    expenses:housing:rent         £1,200.00
    assets:bank:checking:main    -£1,200.00

2024-02-10 Supermarket
    expenses:food:groceries         £150.00
    assets:bank:checking:main      -£150.00

2024-02-20 Coffee
    expenses:food:coffee:shop         £9.00
    assets:bank:checking:main        -£9.00

2024-03-01 Move to savings
    assets:bank:savings           £1,000.00
    assets:bank:checking:main   -£1,000.00
```

Chosen to include a sibling-regex-collision case (`assets` vs `savings`
both matching `assets:bank:savings`) specifically to reproduce the
manual's own worked precedence example against the real binary rather
than taking the manual's word for it.

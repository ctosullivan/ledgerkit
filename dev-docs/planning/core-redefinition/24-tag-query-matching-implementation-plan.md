# 24. `tag:NAME[=REGEX]` query-matching — implementation plan

Step 5 of the process. Design approved (§17 of `23-tag-query-matching-
design.md`): Option A (complete, four-source effective-tag semantics)
for §9.1, hledger-mode replication for §9.2. This plan resolves the one
choice the design deliberately left open — the evaluator-API shape —
and turns the rest into a concrete, ordered work list for a fresh
implementing agent (Step 6). It does not re-litigate anything §17
already closed.

## Resolved this pass

**Evaluator-API shape**: `journal: Journal | None = None`, added as a
new keyword parameter to `matches_transaction`/`matches_posting`
(`ledgerkit/query/eval.py`). All four existing call sites
(`reports.py`'s `balance`/`register`/`accounts`/`stats`, `cli.py`'s
`print`) already have `journal` in their own enclosing scope (design
§1) — each is updated to pass it through. Rationale: least invasive of
the three candidates, matches the design's own leading suggestion,
requires no new context-object abstraction. If a `Tag` node is
evaluated with `journal=None`, raise `ValueError` (not `TypeError`, to
distinguish "caller's fault" from "correctness bug" per the design's
loud-failure constraint) — never silently narrow to own-tags-only.

## Scope (all in this phase, per §9.1/§9.2 resolution)

1. **Commodity-tag substrate** (new storage + parser capture)
2. **Account-tag inheritance computation** (closes the pre-existing gap
   `declared_account_tags` already had a consumer for nothing)
3. **`effective_tags` computation** unioning all four sources, no
   shadowing (plain concatenation, per §2.7)
4. **`Tag` AST node** + parser + generic eval branch
5. **`accounts`-mode exception**: a narrower effective-tags computation
   (transaction-own + account-inherited only) used only by the
   `accounts` command's `Tag`-matching path

## File-by-file changes

### `ledgerkit/models.py`
- `Journal` gains `declared_commodity_tags: dict[str, list[tuple[str, str]]]`
  (mirrors `declared_account_tags`'s existing shape exactly), default
  empty dict, same field-addition pattern as Phase 4's
  `declared_account_tags`.

### `ledgerkit/parser.py`
- `commodity` directive handling (~lines 1288-1299): stop discarding the
  inline comment. Parse same-line comment tags via `parse_tags` (reuse
  the existing function from `ledgerkit/tags.py`, same call shape as
  the `account`-directive site). Also capture follow-on indented
  comment-only subdirective lines the same way `account`-directive tags
  already do (mirror that code path exactly — do not invent a new
  subdirective-scanning mechanism). Store into
  `journal.declared_commodity_tags[symbol]`, appending across multiple
  `commodity` directives for the same symbol if that's the existing
  `declared_account_tags` merge behaviour (check before assuming).

### `ledgerkit/tags.py`
All three new helpers **private** (§9.3, resolved: private by default):
- `_inherited_account_tags(journal: Journal, account: str) -> list[tuple[str, str]]`
  — walks `account` up through its `:`-separated ancestor chain,
  unioning every ancestor's (and its own) `declared_account_tags`
  entries. Confirm the exact tree-walk convention against
  `journalInheritedAccountTags` (design §2.6) — inherited tags apply to
  the account itself and all descendants, not just descendants.
- `_commodity_tags(journal: Journal, commodities: list[str]) -> list[tuple[str, str]]`
  — looks up `journal.declared_commodity_tags` for every commodity
  symbol in the list (a posting's main amount can reference more than
  one, per §2.6's `postingCommodities`), concatenating results.
- `effective_tags(journal: Journal, txn: Transaction, posting: Posting) -> list[tuple[str, str]]`
  — plain concatenation of all four sources, no dedup beyond identical
  `(name, value)` tuples: `posting.tags + txn.tags +
  _inherited_account_tags(journal, posting.account) +
  _commodity_tags(journal, <commodities used in posting's main amount>)`.
  Extracting "commodities used in a posting's main amount" needs a
  small helper too (private) if one doesn't already exist — check
  `ledgerkit/models.py`/`reports.py` for an existing amount-commodity
  accessor before writing a new one.
- `_accounts_effective_tags(journal: Journal, txn: Transaction, posting: Posting) -> list[tuple[str, str]]`
  — the `accounts`-mode exception (§9.2): `txn.tags +
  _inherited_account_tags(journal, posting.account)` only — explicitly
  excludes `posting.tags` and commodity tags. Reuses
  `_inherited_account_tags` directly, per the design's own note that
  this is a subset of the full computation, not a separate one.

### `ledgerkit/query/ast.py`
- New frozen dataclass `Tag` exactly as design §5.1 specifies
  (`name_pattern: str`, `value_pattern: str | None = None`).
- Add `Tag` to the `QueryNode` Union.

### `ledgerkit/query/parser.py`
- `_build_tag(value: str) -> Tag`, per design §5.2: split on first `=`
  via `str.partition("=")`, validate both halves through
  `compile_hledger_regex` (same pattern as `_build_acct`/`_build_desc`),
  raise `QueryParseError` on invalid regex with a `tag:`-prefixed
  message.
- Register `"tag:": _build_tag` in `_PREFIX_BUILDERS`. No bucket
  changes needed — `Tag` isn't in the OR-eligible `isinstance` checks,
  so it lands in `other_terms` (AND) automatically (design §3, §8).

### `ledgerkit/query/eval.py`
- `matches_posting`/`matches_transaction` each gain `journal: Journal |
  None = None` and a new `isinstance(node, Tag)` branch.
  - `matches_posting`: if `journal is None`, raise `ValueError("tag:
    matching requires journal context")`. Otherwise call
    `effective_tags(journal, <posting's transaction>, posting)` (get
    the owning transaction the same way any other posting-level code
    in this module already does) and test name/value against it via
    `patternsMatchTags`-equivalent logic (reuse whatever
    `compile_hledger_regex`-based matching helper `acct:`/`desc:`
    already use for consistency, not a new regex-matching primitive).
  - `matches_transaction`: same `journal is None` guard. Per design §6:
    match if `txn`'s own tags directly match, **or** any posting's
    `effective_tags` match — implement as a direct OR, not solely by
    delegating to `matches_posting` in a loop (the design explicitly
    warns against assuming the direct half is redundant).
- `accounts` report path (find where it currently calls into
  `matches_posting`/`matches_transaction` — likely `reports.py`, not
  `eval.py` itself): needs its own dispatch that uses
  `_accounts_effective_tags` instead of `effective_tags` specifically
  for `Tag` nodes, without changing behaviour for any other predicate
  type. Decide the smallest structural change that achieves this
  (e.g. an optional `mode` parameter, or a separate accounts-specific
  wrapper function) — implementer's judgment, but must not alter
  `balance`/`register`/`print`/`stats`'s behaviour, and must not require
  a `depth:`-style `DepthSpec` side-channel (design §2.5 confirms none
  is needed here).

### `ledgerkit/query/__init__.py`
- Export `Tag` in `__all__` (design §5.4).

### Four call sites (`reports.py`'s `balance`/`register`/`accounts`/
`stats`, `cli.py`'s `print`)
- Pass `journal=journal` through to whichever of
  `matches_transaction`/`matches_posting` each already calls. Confirmed
  by the design (§1) that `journal` is already in scope at all four.

## Compat-register entries (create at `status: proposed`; do NOT
self-promote to `verified` — that is Step 7, a separate dispatch)

- `LK-COMPAT-QUERY-TAG-001` — basic `tag:NAME`/`tag:NAME=REGEX` matching.
- `LK-COMPAT-QUERY-TAG-COMBINE-001` — AND-not-OR combination of multiple
  `tag:` terms (§2.3).
- `LK-COMPAT-QUERY-TAG-INHERIT-001` — account-tag inheritance (rules
  A-D).
- `LK-COMPAT-QUERY-TAG-COMMODITY-001` — commodity-directive tag
  propagation (§2.6).
- `LK-COMPAT-PARSER-TAG-COMMODITY-001` — commodity-directive tag
  parsing/storage (mirrors `LK-COMPAT-PARSER-TAG-SCOPE-001`'s Phase 4
  precedent).
- `LK-COMPAT-QUERY-TAG-ACCOUNTS-001` — the `accounts` command's
  narrower tag visibility (§2.5/§9.2), classified `compatible` (it's
  the replicated hledger behaviour, not a divergence).

Every `reason:`/notes field on `-INHERIT-001` and `-COMMODITY-001` must
explicitly state the no-shadowing/union finding (§2.7) — same-named,
differently-valued tags from multiple sources are all independently
matchable, contradicting a literal reading of the manual's "override"
wording. Cite the executable evidence, not the manual's prose, per the
design's own governing instruction.

## Tests (design §16 — implement all of these; do not treat as
illustrative)

- Unit (`tests/test_query/test_parser.py`, `tests/test_query/
  test_eval.py`): bare `tag:NAME`, `tag:NAME=REGEX`, malformed-regex
  error, empty-value matching, `not:tag:...` negation, multiple `tag:`
  terms AND-combining, `tag:rate==0.05`-shaped first-`=`-split
  preservation, `tag:.=VALUE` value-only matching, the `journal=None`
  loud-failure case for both `matches_posting` and `matches_transaction`.
- Integration (`tests/test_reports.py`, `tests/test_cli/test_cli.py`):
  a new fixture (or extension of an existing one — check `filtered.
  journal`/`depth.journal` first per the design's own note that neither
  currently has any tags) with account-directive tags, transaction-
  header tags, posting-own tags, and commodity-directive tags in
  combination. Required named cases, each its own test, not one loose
  combined assertion:
  - commodity-directive tag propagates to postings using that commodity
  - five same-name/different-value precedence pairs (posting vs.
    account, posting vs. commodity, account vs. commodity, parent- vs.
    child-account/posting, transaction-level vs. any other source)
  - parent-account tag + commodity tag composing on the same posting
  - `accounts` four-way split: transaction-level visible,
    account-inherited visible, posting-own not visible,
    commodity-propagated not visible — four separate test methods
  - `tag:` wired through `-q` for all five commands (`balance`,
    `register`, `print`, `stats`, `accounts`)

## Documentation sync (same response as the code, per CLAUDE.md)

- `dev-docs/api-spec.md` — `QueryNode` Union's new `Tag` member;
  `matches_transaction`/`matches_posting`'s new `journal` parameter.
  **This is the protected-file change flagged under the Unauthorised
  Change Rule — already disclosed in design §5.1/§11 and covered by
  the design's approval; implement exactly as specified there, nothing
  broader.**
- `dev-docs/hledger-compatibility.md` — the `tag:NAME[=REGEX]` row
  (currently "Not implemented"); a new "Commodity tags" section/row
  (design §2.6); the `accounts` command's tag-matching note.
- `dev-docs/architecture.md` — `ledgerkit/query/` subpackage description
  update; `ledgerkit/parser.py`'s `commodity`-directive handling;
  `ledgerkit/tags.py`'s new inheritance/commodity functions.
- `docs/usage.md` — `-q "tag:..."` examples, mirroring the existing
  `depth:` examples' style.
- `knowledge/DECISIONS.md` — Option A chosen over B (why); `accounts`
  replication chosen over uniform matching (why); evaluator-API shape
  chosen (`journal: Journal | None = None` over the other two
  candidates, why).
- `knowledge/DOMAIN_RULES.md` — the four inheritance rules; AND-not-OR
  combination; commodity-tag propagation; the union-not-shadowing
  same-name precedence finding (flag this one as the most
  counter-intuitive, given the manual's own wording reads the opposite
  way).
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the standing
  same-response rule.

## Explicitly out of scope (do not implement)

Same non-goals list as design §14: `cur:`, `payee:`/`note:`,
`PythonRegex` extension syntax, `Query`-as-compatibility-shim
migration, a standalone `--depth`/`-N` flag.

## Process constraints for the implementing agent

- Do not self-promote any compat-register entry past `status:
  proposed` — that requires a genuinely separate `compat-
  differential-tester` dispatch (Step 7), per Stage C Phase 5's
  verification-independence rule (`09-compatibility-system.md` §9.6).
- Regex-documentation rule applies to any new/modified regex.
- Module-size flag if any touched file crosses ~300-500 lines or
  visibly accumulates a second responsibility — propose a split, do not
  execute one unilaterally.
- Commit at logical intervals per the project's Commit & Push Cadence;
  push at the end of the phase once tests pass and docs are synced.
- Write this phase's retro per `dev-docs/retros/TEMPLATE.md` at
  `dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` (a new
  file — the existing `STAGE-C-PHASE-6-TAG-QUERY-PLAN.md` retro covers
  the planning phase only, per "never rewrite a past retro, only add").

# CONTEXT.md — Claude Session Working Memory

## Current Task
Stage C Phase 8 (`Query`-as-compatibility-shim convergence) — design
document amended a **second** time after a further design-review
correction pass (a real missed consumer, a real bug in the first
pass's own fix, plus scope/wording corrections). **Still stopped for
explicit human approval.** No `ledgerkit/`/`tests/` code touched.

## Where We Are
Design document: `dev-docs/planning/core-redefinition/27-query-shim-
convergence-design.md`, now on its second amendment (§5.1b rewritten,
§5.1d added, §5.1a extended to 3 cases, §5.2/§5.3 rewritten, §9-§12
updated). Retro has a second addendum. `ROADMAP.md`/`CHANGELOG.md`
updated. About to commit + push, then wait.

## Decisions In Flight
Design §12's six-item approval gate, each with an explicit recommended
choice now:
1. **§6 — regex strictness**: Option A (full `HledgerRegex`
   convergence). **The only genuinely blocking item.**
2. **§5.1c — `stats` correction**: include in Phase 8 (recommended).
3. **§5.1b — `ReportSection` scope**: keep its own OR/exclude control
   flow, converge only its regex dialect; full AST conversion deferred
   (recommended).
4. **§5.1a — exception type**: reuse `QueryParseError` (recommended).
5. **§9 — compat-register naming**: not blocking, proceed as proposed.
6. General approval, conditioned on §5.3's complete inventory.

## Files Currently Relevant
- `dev-docs/planning/core-redefinition/27-query-shim-convergence-
  design.md` — the twice-amended design document awaiting approval.
  §5.3 is the authoritative "every Query consumer" inventory.
- `ledgerkit/models.py:444-473` — `Journal.to_dataframe` (the missed
  consumer — calls `_posting_matches` directly, must migrate to
  `_query_to_ast`+`matches_posting`, §5.1d).
- `ledgerkit/models.py:382-432` — the deprecated `accounts=[...]` shim
  (zero/one/many all now handled explicitly; zero must NOT become
  `Or(())`, which matches nothing, §5.1a).
- `ledgerkit/reports.py:612-694` — `balance_from_spec` (outer query now
  converges onto the canonical engine too; only `ReportSection.
  accounts`/`.exclude` keep `_matches_pattern`, §5.1b).
- `ledgerkit/query/compat.py` (planned, not yet created) — `_query_to_
  ast`, `_validated`, `_exclusive_end`.

## Blockers / Open Questions
Design §12 item 1 (regex strictness) is the only genuinely blocking
item. Nothing else outstanding.

## What NOT To Revisit
- Don't re-trust a "no consumer uses an excluded construct" claim based
  only on grepping `Query(...)` construction — build the actual
  producer/consumer inventory (§5.3) instead; this has now caused two
  separate missed cases across two correction passes.
- Don't let `accounts=[]` fall through to a many-accounts `Or(...)`
  branch — `Or(())` matches nothing, not everything. Handle zero
  accounts as its own explicit case (no filter).
- Don't leave `balance_from_spec`'s **outer** query on `_matches_
  pattern` — only `ReportSection.accounts`/`.exclude` are a genuinely
  separate construct; the outer query converges like everything else.
- Don't forget `Journal.to_dataframe` when retiring `_posting_matches`
  — it's a real, live caller (`models.py:456,461`), not test-only.
- Don't construct any `Acct(...)`/`Desc(...)` node — anywhere, including
  the deprecated multi-account shim's `re.escape`d literals — without
  eager validation via `_validated`, even when the pattern's safety
  seems self-evident.

## Recent Git State (before this response's commit)
12d5cdf docs: amend Stage C Phase 8 design -- targeted correction pass
fbde262 docs: Stage C Phase 8 -- Query-as-shim convergence design
afbcd05 test: independently verify Stage C Phase 7 empty-regex fix, resolve register
e3e00a1 feat: reject empty regex query patterns (Stage C Phase 7)
d88a777 docs: amend Stage C Phase 7 design -- targeted correction pass

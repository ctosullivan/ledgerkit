<!-- producer: domain-skeptic (REVIEW mode) | topic: tags | dispatch: tags-review-1 | date: 2026-10-03 -->
# Review note: tags assertions (tags-001 .. tags-009)

## Scope
Reviewed all 9 draft assertions in `dev-docs/clean-room/assertions/tags/`
against their cited evidence, using only the permitted evidence paths:
`ledgerkit/tags.py`, `tests/test_tags.py`, and `ledgerkit/models.py` (narrow
allowance, type-reference resolution only). No legacy documentation, no
other repo files, were opened.

## What I checked
- Ran the full `test_tags.py` suite (`python -m unittest tests.test_tags -v`):
  all 38 tests pass. Confirms every assertion's cited `Examples` actually
  exist and pass as described.
- Re-read `ledgerkit/tags.py` in full and cross-checked every assertion's
  `Evidence` line-range citation against the actual source — all citations
  point to the text they claim to quote/describe; no citation was found to
  misquote or misattribute its source.
- Checked for a 5th tag source that might contradict tags-001's "exactly
  four sources" claim: `Journal.declared_tags` (models.py:309) exists but is
  `list[str]` (declared tag *names* only, no values) and is never referenced
  anywhere in `tags.py` — confirmed it is not a 5th (name, value) source,
  so tags-001's claim holds.
- Spot-checked several edge cases not covered by existing tests, to hunt for
  contradictions `parse_tags`'s own stated rules would predict: double colon
  (`"a::b"`), tab-whitespace-before-colon, internal whitespace before colon,
  non-ASCII tag names, comma-immediately-after-colon, a comma appearing
  *inside* a tag name candidate before the first colon (e.g. `"a,b:c"` ->
  `[("a,b", "c")]`). All of these were **consistent** with the claims already
  made in tags-005/006/007 — no contradictions found, so no edits were
  needed for those five assertions beyond this confirmation.
- Independently verified, via direct invocation (not merely trusting the
  docstring's prose), the open question flagged in tags-002: whether
  `_effective_tags` deduplicates an exact `(name, value)` duplicate declared
  by two sources. It does not — confirmed both by re-reading the return
  statement (`tags.py:232-237`, plain `+` concatenation, no `union`/`set`/
  `dict` anywhere) and by running `_effective_tags` directly with an
  identical `("rate","1")` tag on all four sources: result retained all four
  copies, none collapsed.
- Independently re-derived (within the narrow models.py type-resolution
  allowance) the claim tags-009 said rested only on tags.py's own docstring
  prose: `Posting.amount` is declared `Amount | None` (models.py:74), a
  single optional value, not a collection — structurally confirms
  `_posting_commodities` can never return more than one element given the
  current model.
- Checked tags-003's open question (claimed consumer relationship with
  `reports.py`/`query.py`) — correctly flagged as unverifiable within the
  permitted evidence paths; left as-is, no escalation needed since it does
  not bear on the assertion's core, fully-tested `_accounts_effective_tags`
  computation.
- Checked the CLAUDE.md regex-documentation rule's applicability: `tags.py`
  contains no `re`/regex usage at all, so this rule does not apply here.

## What I fixed
1. **`tags-002.md`** — the draft's `Open questions` field framed
   "does an exact `(name,value)` duplicate across sources get deduplicated"
   as an unresolved, test-uncovered corner that would require hledger-binary
   access to settle. It did not require that: the question is fully answered
   by `_effective_tags`'s own return statement (already-cited evidence,
   plain `+`, no dedup mechanism of any kind), confirmed by direct
   invocation. Updated `Statement`, `Evidence`, `Justification`, `Examples`,
   `Open questions` to state the resolved fact (no deduplication occurs
   under any circumstance, including exact-duplicate pairs), and the
   `Evidence-support state`/`Status` from `partially_supported`/`supported`
   to `supported`/`verified`.
2. **`tags-009.md`** — the draft's `Depends on` field explicitly admitted
   resting only on the docstring's own prose ("not independently re-derived
   here"), which is exactly the pattern my brief requires flagging rather
   than waving through. Independently confirmed `Posting.amount`'s type
   directly against `models.py:74` (within the permitted narrow allowance)
   and updated `Evidence`, `Justification`, `Depends on` to cite that
   independent confirmation instead of resting on the docstring alone.
   `Evidence-support state`/`Status` updated from `partially_supported`/
   `supported` to `supported`/`verified` (the remaining open question — no
   end-to-end multi-commodity `Posting` test — is a genuine structural
   impossibility given the current model, not an unresolved ambiguity, so
   it was reworded but not escalated).

No other assertion files (tags-001, 003, 004, 005, 006, 007, 008) required
edits — their `Evidence` citations check out against the source, their
`Examples` pass as described, and no contradiction or missing-edge-case gap
survived my attempted resolution.

## What I'm escalating
Nothing. Every finding I identified during this review was resolvable
directly from the permitted evidence paths (tags.py, test_tags.py, and the
narrow models.py type allowance) without needing access to excluded
evidence (hledger source/binary, legacy docs). No genuine, unresolvable
ambiguity remains in this topic's assertions as far as I could determine.

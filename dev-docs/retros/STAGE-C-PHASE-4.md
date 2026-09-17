# Stage C Phase 4 retro — Tag data model (parsing/storage)

- **Date:** 2026-09-17
- **Commit(s):** (uncommitted at time of writing)
- **Agents used:** two `hledger-researcher` dispatches — one for `tag:`
  query-matching semantics (brief 19), one for the tag-parsing grammar
  itself (brief 20), after brief 19 revealed the query term had no data
  model to sit on

## Where we are

Phase 3 closed Stage C's `-q`/`--query` integration across all five
report/display CLI commands and named `tag:`/`cur:` term extension as a
remaining candidate, with an explicit flag to read CodeCompass's own
Phase 54 finding first (a caught extraction-accuracy defect in `tag:`-
adjacent reference material — a manual excerpt that silently dropped the
third of three tag-inheritance rules it should have captured). Following
that flag directly, before touching `tag:` at all, surfaced that the real
number of inheritance rules is **four**, not three — CodeCompass's own
flawed extraction was reproduced and confirmed independently, not just
taken on faith.

## Goal

Implement the `tag:NAME[=REGEX]` query term, following the established
research→implement→differential-verify rhythm.

## Scope delivered vs planned

Scope changed mid-phase, by the user's explicit choice, not the lead's.
Brief 19 (query-matching semantics) surfaced in its §9 that Ledgerkit has
**no tag data model at all** — no `Posting`/`Transaction` tag fields
exist anywhere in the codebase. Implementing `tag:` matching on top of
nothing was not viable. This was presented to the user via
`AskUserQuestion` rather than decided unilaterally; the user chose
**"Split: data model first, tag: query later."** This phase therefore
delivers only the data model (parsing and storage of `name:value` tags on
transactions, postings, and `account` directives, plus posting-level
`date:`/`date2:` override resolution) — the `tag:` query term itself is
now explicitly deferred to a future phase, not started.

A second, narrower confirmation was needed within the reduced scope:
brief 20 proposed the exact new model fields (`Posting.tags`,
`Posting.date_override`/`date2_override`, `Transaction.tags`,
`Journal.declared_account_tags`, and a choice between a
`Posting.transaction` back-reference vs. pure functions for date-override
resolution). Since these touch the protected `dev-docs/api-spec.md`, they
were put to the user as a second `AskUserQuestion` before implementation
began; the user confirmed the fields exactly as proposed, including the
pure-function (no back-reference) form.

## What was achieved

- `ledgerkit/tags.py` (new module): `parse_tags` (the core `name:value`
  extraction grammar) and `effective_date`/`effective_date2` (posting
  date-override precedence resolution) — pure functions, no file I/O, no
  model mutation.
- `ledgerkit/models.py`: `Posting.tags`, `Posting.date_override`/
  `date2_override`, `Transaction.tags`, `Journal.declared_account_tags`.
- `ledgerkit/parser.py`: wired tag extraction into `_flush_txn` for
  transactions and postings; fixed a real, pre-existing gap where
  `account` directive comments (same-line and follow-on) were discarded
  entirely, now captured into `Journal.declared_account_tags`.
- 46 new tests (23 in `tests/test_tags.py`, 8 in
  `TestAccountDirectiveTags`, 6 in `TestTransactionAndPostingTags`, 7 in
  `TestPostingDateOverrideTags`, in the existing directive/parser test
  files) — 728 total, all passing.
- Differential verification against the pinned hledger 1.52.4 binary
  (`hledger tags` tag-name-set comparison; `hledger register` effective-
  date grouping for the posting-date-override precedence chain) — exact
  matches on both.
- 4 new compat-register entries, all `status: verified` from the start
  (differential-tested during implementation): `LK-COMPAT-PARSER-TAG-001`,
  `LK-COMPAT-PARSER-TAG-SCOPE-001`, `LK-COMPAT-PARSER-POSTINGDATE-001`,
  `LK-COMPAT-DIRECTIVE-TAG-001`.
- Two new research briefs under `dev-docs/planning/core-redefinition/`
  (19 and 20), plus 4 new `knowledge/` entries (1 `DOMAIN_RULES.md`
  section covering the grammar's non-obvious edge cases; 3 `DECISIONS.md`
  entries covering the no-back-reference design, the new-module-not-
  parser.py placement, and the adapted-vs-directly-translated
  determination for `parse_tags`).

## What worked

- **Reading CodeCompass's own documented mistake before starting**, as
  Phase 3's retro flagged, caught the same class of error a second time
  independently — the four-vs-three inheritance rule count — before it
  could propagate into this phase's own work, not just into the eventual
  `tag:` implementation.
- **Stopping to ask before inventing a data model unilaterally.** The
  brief could have been read as "just add the fields you need to
  implement `tag:`," but a whole new cross-cutting data-model layer
  (touching three model classes and the protected api-spec) is exactly
  the kind of decision that benefits from an explicit scope check rather
  than the lead deciding silently.
- **Reasoning through the `Data.Text.split isSpace` vs. Python
  `str.split()` semantic difference before writing code**, rather than
  after a test failure — the space-before-colon-voids-the-tag edge case
  was implemented correctly on the first attempt because the difference
  was worked through on paper first.
- **Placing the new logic in its own module (`tags.py`) instead of
  `parser.py`**, given `parser.py` was already well over the
  `CLAUDE.md` module-size signal (1547+ lines) — sidesteps growing an
  already-flagged file further without triggering the heavier
  approval-gated refactor process.

## What didn't work

Found and fixed one real bug during implementation, not during
differential verification: the account-directive tag-scanning logic was
initially placed inside an `if in_subdirective:` block, which turned out
to be unreachable for comment-only lines — an earlier, unconditional
`if stripped.startswith(";") or stripped.startswith("#"): ... continue`
block intercepts every such line first, regardless of state. Caught by a
manual test before it reached the differential-testing stage, not after;
traced to its root cause (reading the actual per-line control flow, not
guessing) and fixed by moving the logic into the block that actually
runs.

## Lessons learnt

When a per-line parser state machine has more than one branch that can
match a given line shape (here: two different `;`/`#`-prefix checks at
different points in the loop), a change to "what happens on a `;`-led
line" must be traced through the *first* branch that can intercept that
line shape, not the branch that seems topically related. Topical
placement (comment-scanning logic near other comment-scanning logic)
is not the same as reachability.

## Process-improvement feedback

Both `AskUserQuestion` interactions this phase were genuine — not
process theater. The first (split now vs. push through disorganized)
prevented pursuing exactly the "invent a bunch of new API surface area
because I have some direction" mode the project's Unauthorised Change
Rule exists to guard against, without stopping to ask. The second, having
already decided to scope things down, still let the user override
one specific field-design choice (the back-reference question) rather
than the lead choosing silently between two reasonable options.

## Learnings filed

- `dev-docs/compat-register/LK-COMPAT-PARSER-TAG-001.yaml`,
  `LK-COMPAT-PARSER-TAG-SCOPE-001.yaml`,
  `LK-COMPAT-PARSER-POSTINGDATE-001.yaml`,
  `LK-COMPAT-DIRECTIVE-TAG-001.yaml` — all `status: verified`.
- `knowledge/DOMAIN_RULES.md` — inline comment tag grammar edge cases.
- `knowledge/DECISIONS.md` — three entries (back-reference design,
  new-module placement, adapted-implementation determination).

## Where we're going

The `tag:NAME[=REGEX]` query term itself (brief 19's remaining scope:
matching, the four inheritance rules, always-AND-never-OR combination
semantics, and the separate narrower account-name-level matching
mechanism) is the natural next Stage C phase, now that its data-model
prerequisite exists — but per the user's split decision, it is a distinct
phase requiring its own scoping, not an automatic continuation.

## Time / cost note

Single extended session: two research-agent dispatches, two
`AskUserQuestion` scope checks, implementation across three modules, 46
new tests, one bug found and fixed mid-implementation, differential
verification against the pinned hledger binary, and this full
documentation/closeout pass — larger than Phases 1-3 individually, in
line with introducing a genuinely new cross-cutting data-model layer
rather than extending an existing one.

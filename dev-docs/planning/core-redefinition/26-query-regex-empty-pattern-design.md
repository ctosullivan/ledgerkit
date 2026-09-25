# 26. Empty-regex-pattern rejection — design document

Design document for the first item of Stage C's post-Phase-6 backlog
(`dev-docs/retros/STAGE-C-PHASE-6-TAG-QUERY-IMPLEMENTATION.md` Addendum
2): resolving `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`. **Not an
implementation plan.** No `ledgerkit/`/`tests/` code touched producing
this document. Same provenance-tagging discipline as `23-tag-query-
matching-design.md`: **[VERIFIED-EXTERNAL]** / **[EXISTING-DECISION]**
/ **[PROPOSED]** / **[UNRESOLVED]**.

**Amendment (this pass, same day): a targeted correction pass, not a
re-scope.** Four corrections, none changing the fix's actual scope or
mechanism: (1) the proposed error message was `tag:`-specific advice
baked into a prefix-agnostic shared validator — made fully generic,
tag-specific guidance moved to user-facing docs instead (§5); (2) "no
public API change" was an inaccurate framing — signatures are
unchanged, but documented accepted-input *behaviour* is changing, which
is a real, `api-spec.md`-relevant fact, correctly framed as a
backward-compatible compatibility/correctness fix (§5.1); (3) the
separately-discovered empty-alternation-branch divergence (`(|)` etc.)
is now actually filed as its own register entry
(`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`) rather than left as an
informal note, scoped strictly to what's independently verified on both
sides (§7/§8); (4) `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001`'s eventual
resolution is corrected from an in-place `kind:` flip to the register's
own rename-and-reclassify convention (§8). The narrow `pattern == ""`
fix itself, its single chokepoint, its non-goals, and its test plan are
all unchanged from the original document.

## 0. Pinned revisions

Ledgerkit: `a49ac50`. hledger: `1.52.4` /
`33fa849e7ae841968bd21c427094c4fb4a4ec38d`, pinned binary
`1.52.4-g33fa849e7-20260910`.

## 1. Process note

A `context-curator` dispatch was made for Step 1 and correctly refused
the assignment — its actual charter (`.claude/agents/context-
curator.md`) is narrowly "judge whether CodeCompass context helped,"
not general hledger/source research, and it said so with citations
rather than overstepping. That dispatch's only real output: CodeCompass
indexes no vendor packages and doesn't index Ledgerkit's own source
(`compile_hledger_regex` isn't a known symbol to it), reproducing this
project's already-established LOW context-advantage baseline — a
legitimate zero-finding result, not a gap. No `CC-LK-NNN` filed. The
lead then re-routed appropriately: a `compat-differential-tester`
dispatch for the live-binary matrix (its actual mandate), and the
Ledgerkit-internal source audit done directly by the lead (mirroring
how Phase 6's own design document handled lead-performed spot-checks).
Both are complete; this document is built on their combined output.

## 2. Verified external behaviour — [VERIFIED-EXTERNAL]

Full matrix: `dev-docs/planning/core-redefinition/25-query-regex-empty-
pattern-matrix.md` (independent `compat-differential-tester` dispatch,
fresh fixture, not reused from any prior session's fixtures). Summary:

- **Every regex-taking query-term prefix** (`acct:`, `desc:`, `tag:`'s
  NAME half when no `=` is present at all, `tag:`'s VALUE half when
  `=` is present with nothing after it, `depth:`'s REGEX half in
  `depth:REGEX=N`) rejects the **literal empty pattern string**
  identically: exit 1, `hledger: Error: This regular expression is
  invalid or unsupported, please correct it:` with nothing after the
  trailing colon.
- **The rejection trigger is exactly `pattern == ""`, not any pattern
  capable of matching an empty string.** `.*`, `a*`, `x*`, `^$`, `()`
  are all accepted (exit 0) despite being semantically empty-matching
  or empty-only-matching. This is the single most important scoping
  fact: the fix is a narrow "was any text given at all" check, not a
  regex-semantics analysis.
- A **separate, unrelated** rejection family exists for empty
  alternation branches (`(|)`, `a|`, `|a`, `(a|)`, `(|a)`) and
  malformed quantifier stacking (`a**`) — same generic error message
  text, but distinguishable because the offending pattern is echoed on
  a second stderr line (the true-empty-string case prints nothing
  after the colon). **Not in scope for this fix** — see §7 (non-goals).
- `not:` wrapping doesn't change anything — rejection is parse-time,
  before negation is considered (`not:acct:` etc. all fail identically
  to their unnegated forms).
- `status:`/`date:` are confirmed not regex-taking at all (different
  code paths, `date:` bare gives a distinct date-parse error) — out of
  scope, not because they're excluded but because they were never in
  scope to begin with.

## 3. Existing Ledgerkit decisions this design must respect — [EXISTING-DECISION]

- `ledgerkit/query/regex.py`'s `compile_hledger_regex`/`validate_
  hledger_regex` is the **single shared chokepoint** every regex-taking
  query term already routes through — confirmed by direct grep: the
  only callers are `ledgerkit/query/parser.py` (`_build_acct`,
  `_build_desc`, `_build_depth_spec`, `_build_tag`), `ledgerkit/query/
  depth.py`, and `ledgerkit/query/eval.py`'s `_compiled` (an
  `lru_cache`-wrapped re-validation at match time, not a second design
  surface). No other `ledgerkit/` module calls either function.
- `_build_tag`'s existing `name, sep, val = value.partition("=")`
  **already distinguishes** bare `tag:NAME` (value_pattern stays
  `None`, `compile_hledger_regex` is never called on it) from
  `tag:NAME=` (calls `compile_hledger_regex(val)` on a real, possibly
  empty, string) — confirmed by direct read of `ledgerkit/query/
  parser.py:230-245`. **This resolves what would otherwise be an open
  design fork**: no per-call-site special-casing is needed to tell
  "any value" apart from "an explicitly empty value" — the existing
  `sep` check already does it. A single check inside `compile_hledger_
  regex`/`validate_hledger_regex` therefore automatically produces the
  correct behaviour at every one of the four call sites, with zero
  changes needed to `_build_acct`/`_build_desc`/`_build_depth_spec`/
  `_build_tag` themselves.
- Bare `tag:` (nothing after the colon at all) reaches `_build_tag("")`
  — `"".partition("=")` gives `("", "", "")`, so `name=""` and `sep`
  is falsy: `compile_hledger_regex("")` **is** called on the NAME half.
  This already matches hledger's own confirmed behaviour (§2: bare
  `tag:` rejects for the same underlying reason as `tag:NAME=`, via
  the NAME slot) — no extra logic needed here either.
- `UnsupportedRegexConstructError(ValueError)` already exists, is
  **already public and documented** (`dev-docs/api-spec.md:1167`,
  exported via `ledgerkit.query.__all__`), and is already the exception
  every "pattern uses something HledgerRegex doesn't support" case
  raises. `_build_acct`/`_build_desc`/`_build_depth_spec`/`_build_tag`
  all already catch `(ValueError, re.error)` generically and re-wrap
  into `QueryParseError` — so raising `UnsupportedRegexConstructError`
  for an empty pattern requires **no call-site changes at all**, it
  flows through the exact same existing catch-and-wrap machinery.

## 4. What's missing — [VERIFIED-EXTERNAL + EXISTING-DECISION, synthesised]

Exactly one thing: `validate_hledger_regex` currently has no check for
`pattern == ""` at all — an empty string trivially fails to match
`_EXCLUDED_CONSTRUCT` (nothing to find), so `compile_hledger_regex("")`
falls through to `re.compile("", re.IGNORECASE)`, which succeeds and
produces a pattern that matches via `.search()` anywhere, including an
empty string. This is the entire gap.

## 5. Proposed design — [PROPOSED]

Add one check to `validate_hledger_regex` (`ledgerkit/query/regex.py`),
before the existing `_EXCLUDED_CONSTRUCT` scan:

```python
def validate_hledger_regex(pattern: str) -> None:
    if pattern == "":
        raise UnsupportedRegexConstructError(
            "pattern must not be empty (hledger rejects an empty "
            "regex at parse time)"
        )
    match = _EXCLUDED_CONSTRUCT.search(pattern)
    ...
```

**Message wording, corrected this pass**: `validate_hledger_regex`/
`compile_hledger_regex` are the single shared chokepoint for `acct:`,
`desc:`, `depth:`, and `tag:` alike (§3) — the function itself has no
way to know which prefix called it. The original proposal's message
("use a bare `tag:NAME` to match any value...") was `tag:`-specific
advice baked into a generic validator, wrong for a caller reached via
`acct:`/`desc:`/`depth:`, where no such escape hatch exists at all.
Corrected to fully generic wording with no per-prefix advice, matching
the style of every other message in `_CONSTRUCT_MESSAGES` in the same
file (which explain *why* a pattern is rejected, never *what a specific
caller should do instead*, since the function doesn't know its caller).
Tag-specific guidance (e.g. "use bare `tag:NAME` instead of `tag:NAME=`
for an empty value") belongs in user-facing documentation (`docs/
usage.md`) and/or a `tag:`-specific test's own comment, not in the
shared validator's exception message — see §9/§10.

Reuses the existing exception class (§3) — no new exception type, and
`UnsupportedRegexConstructError`'s own signature is unchanged. **This
is not "no public API impact," corrected this pass — it is a backward-
compatible *behavioural* change to documented public functions'
accepted input (§5.1 below), which `dev-docs/api-spec.md` must
describe accurately once implemented, not silently.**

### 5.1 Public API impact, precisely — [PROPOSED, corrected this pass]

`validate_hledger_regex` and `compile_hledger_regex` are documented
public API (`dev-docs/api-spec.md`), as is `UnsupportedRegexConstruct
Error` (§3). Their **signatures and the exception type are unchanged**
— this is genuinely not a protected-surface change in the Unauthorised
Change Rule's sense of adding/removing/retyping a signature. But it is
inaccurate to describe this as "no public API change" full stop, as the
original version of this document did: **accepted input behaviour
changes** — a call that previously succeeded (`compile_hledger_regex("")`)
will now raise. That is a real, documented-behaviour change to a public
function, correctly framed as a **backward-compatible compatibility/
correctness fix** (bringing documented behaviour in line with hledger,
not introducing new capability or new surface), not as "nothing about
the public API is affected." `dev-docs/api-spec.md`'s entries for both
functions must be updated during implementation to state the new
empty-pattern-rejection behaviour explicitly (§9) — this is a required
doc-sync item, not an optional one, precisely because the function's
own documented contract is what's changing, even though its signature
is not.

No changes needed to `_build_acct`/`_build_desc`/`_build_depth_spec`/
`_build_tag`, `ledgerkit/query/depth.py`, or `ledgerkit/query/eval.py`
— all four parse-time call sites already catch `(ValueError, re.error)`
generically and wrap into `QueryParseError` with their own prefix
(`"acct: ..."`, `"tag: ..."`, etc.), and `eval.py`'s `_compiled` cache
would only ever see an empty pattern if a `Tag`/`Acct`/`Desc` node were
constructed directly through the Python API bypassing `parse()` — in
which case raising at match time (via the same shared function) is the
correct defense-in-depth behaviour, not a new design decision.

## 6. Behavioural change and blast radius — [VERIFIED-EXTERNAL]

**One existing test currently asserts the behaviour being corrected**
and will need to change: `tests/test_query/test_parser.py::
test_empty_value_pattern_is_not_none` currently asserts `tag:rate=`
parses successfully to `Tag("rate", "")`. Post-fix, `tag:rate=` raises
`QueryParseError` at parse time instead — this is the intended,
hledger-matching behaviour, not a regression. The test needs rewriting
to assert the raise, not deleting (it's exercising a real, now-wrong
claim about the query language, not dead code). No other test in
`tests/` was found (by grep) to rely on empty-pattern-matches-anything
behaviour.

A genuine, user-visible consequence worth stating plainly: **hledger
itself has no way to query "a tag/account/description matching a
literal empty regex" via `acct:`/`desc:`/`tag:NAME=` — that specific
query shape is simply unsupported by real hledger**, confirmed by §2.
Users wanting "any value including empty" for a tag already have the
correct tool: bare `tag:NAME`. There is no equivalent loss of
expressiveness for `acct:`/`desc:`, since an empty pattern there was
never meaningfully distinct from omitting the term entirely.

No other `ledgerkit/` call sites outside the query subsystem use
`compile_hledger_regex`/`validate_hledger_regex` (confirmed by
project-wide grep) — the blast radius is fully contained to `ledgerkit/
query/`.

## 7. Explicit non-goals — [PROPOSED]

- **The empty-alternation-branch family** (`(|)`, `a|`, `|a`, `(a|)`,
  `(|a)`) and malformed quantifier stacking (`a**`) — confirmed (§2) to
  be a separate, unrelated hledger rejection cause from the one this
  fix addresses. Ledgerkit currently also diverges here for at least
  `(|)` (Python's `re` compiles it without error; hledger rejects it —
  both sides independently verified) but this is **not** part of this
  fix. **Filed this pass, not left as an informal note**:
  `dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`
  (`kind: unexplained_mismatch`), so it is tracked in the register's
  own north-star metric rather than only mentioned in a research
  document. Per explicit instruction, the entry's own claims are scoped
  to what's actually been verified on both sides — `(|)` is asserted as
  a confirmed divergence; `a|`/`|a`/`(a|)`/`(|a)` are recorded as
  hledger-confirmed-rejected but Ledgerkit-side-unverified, not claimed
  as confirmed divergences. Folding any of this into the current fix
  would widen it from a one-line, fully-characterised change into an
  open-ended regex-semantics audit, contrary to the retro's own
  recommendation that this be the smallest, most concretely-specified
  backlog item — the new entry exists so this doesn't get lost or
  rediscovered later, not so it gets implemented now.
- **A broader "does this pattern's compiled semantics admit an empty
  match" check** — explicitly wrong per §2's own evidence (`.*`, `a*`,
  `^$`, `()` are all real, valid, accepted hledger patterns). Do not
  implement this instead of the narrow `pattern == ""` check.
- `PythonRegex` extension syntax, `cur:`, smart/period dates, a
  standalone `--depth`/`-N` flag, the `Query`-as-compatibility-shim
  migration — unrelated, already-tracked Stage C backlog items,
  untouched by this design.

## 8. Compatibility implications — [PROPOSED]

- `LK-COMPAT-QUERY-TAG-001` — once implemented and independently
  verified, its one currently-false claim (`tag:NAME=` matches an
  empty value) is corrected to state the new, real behaviour
  (`QueryParseError` at parse time); entry can then be promoted to
  `status: verified` for the first time.
- `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` — **resolution mechanics
  corrected this pass**. Per `09-compatibility-system.md`'s own filename
  convention (`LK-<KIND>-<AREA>-<NNN>`, `KIND` ∈ `COMPAT`/`EXT`/`DIV`/
  `UNSUP`/`MISMATCH`, tracking the `kind:` field directly) and its
  description of `unexplained_mismatch` as "never a resting state, only
  a to-do marker," simply flipping this entry's `kind:` field to
  `compatible` while leaving its filename/`id:` as `LK-MISMATCH-*`
  would leave the ID and its own classification contradicting each
  other. The correct closeout process, once implementation lands and a
  genuinely separate `compat-differential-tester` dispatch independently
  confirms the fix (§10): **retire** `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-
  001.yaml` and **create** a new `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001.yaml`
  (new `id:` matching the new filename, `kind: compatible`, its own
  fresh `status: verified`/`verified_by`/`verified_date`, evidence
  carried forward and extended with the new post-fix differential run) —
  a rename-and-reclassify, not an in-place field edit. Remove the old
  ID from `dev-docs/compat-register/UNEXPLAINED.md`'s open-entries table
  (per that file's own stated rule: an entry appears there only while
  its `kind` is `unexplained_mismatch`, and the register file must
  change first). Update every cross-reference to the old ID (this
  design document, `LK-COMPAT-QUERY-TAG-001`'s own `reason:` field,
  `dev-docs/hledger-compatibility.md`, `ROADMAP.md`/`CHANGELOG.md`) to
  the new one — an implementation-and-verification-time task, not
  performed by this design-review pass itself.
- `LK-COMPAT-QUERY-ACCT-001`/`LK-COMPAT-QUERY-DESC-001` — neither
  currently makes any claim about empty-pattern behaviour (confirmed
  by grep, §3-adjacent check) — both get a new evidence note added,
  not a correction of an existing false claim.
- `LK-COMPAT-QUERY-DEPTH-001` — same: no existing empty-pattern claim,
  gets a new evidence note for `depth:=N`'s corrected behaviour.
- **`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` — new this pass, filed, not
  part of this fix's implementation.** The empty-alternation-branch
  divergence (§7) now has its own register entry
  (`dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`),
  filed at design-review time rather than left only as a note in the
  research matrix, so it isn't lost or rediscovered as new later. It is
  **not** resolved, not promoted, and not touched by this fix's own
  implementation — it stays open in `UNEXPLAINED.md` as its own,
  separately-scoped backlog item.
- No new compat-register entry needed for the fix itself beyond
  updating the four above (and the `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-
  001` rename-and-reclassify, above) — this fix is a correction/
  completion of existing entries' claims, not a new feature needing its
  own additional `LK-COMPAT-*-NNN` identity.
- Per the standing process: first-time promotion of any of these to
  `status: verified` requires a genuinely separate `compat-
  differential-tester` dispatch (`09-compatibility-system.md` §9.6),
  same as every prior phase.

## 9. Documentation sync required (once implementation lands)

- `dev-docs/hledger-compatibility.md` — the `acct:`/`desc:`/`tag:`/
  `depth:` rows' existing "empty pattern" caveats (added during Phase
  6's closeout) get updated from "known divergence" to "now matches
  hledger — rejects at parse time."
- `dev-docs/api-spec.md` — **corrected this pass (§5.1)**: `validate_
  hledger_regex`'s and `compile_hledger_regex`'s documented behaviour
  is updated to state the new empty-pattern rejection explicitly — a
  required doc-sync item, not an optional docstring nicety, since their
  documented accepted-input contract is genuinely changing even though
  their signatures and `UnsupportedRegexConstructError`'s own shape are
  not. Framed accurately as a backward-compatible compatibility/
  correctness fix, not "no public API change."
- `docs/usage.md` — **new this pass**: tag-specific guidance (bare
  `tag:NAME` matches any value including empty, `tag:NAME=` no longer
  does) belongs here, not in the shared validator's exception message
  (§5) — a user-facing example showing the corrected behaviour and the
  correct escape hatch.
- `knowledge/DOMAIN_RULES.md` — one new entry: hledger rejects the
  literal empty regex string for every regex-taking query term, but
  *not* any pattern whose semantics merely admit an empty match — the
  distinction that made this fix narrow rather than broad, worth
  recording since it's genuinely non-obvious from the manual alone.
- `knowledge/DECISIONS.md` — reusing `UnsupportedRegexConstructError`
  rather than adding a new exception class, and why (avoids an
  api-spec.md change entirely, and the case is conceptually the same
  kind of "outside the accepted subset" rejection the class already
  represents).
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the standing rule, at
  implementation time.

## 10. Proposed tests

- **Unit** (`tests/test_query/test_regex.py` if it exists, else add to
  wherever `regex.py` is currently tested — check first): empty pattern
  raises `UnsupportedRegexConstructError` directly from `validate_
  hledger_regex`/`compile_hledger_regex`.
- **Unit** (`tests/test_query/test_parser.py`): rewrite `test_empty_
  value_pattern_is_not_none` to assert `tag:rate=` raises
  `QueryParseError` (keep the test name or rename to reflect the new
  assertion — implementer's call, but the behaviour it documents must
  change, not just the assertion silently flipping). New cases: bare
  `acct:`/`desc:` (nothing after the prefix) each raise
  `QueryParseError`; bare `tag:` (nothing after the colon at all)
  raises `QueryParseError`; `depth:=2` (empty REGEX half) raises
  `QueryParseError`; `not:acct:` (empty pattern, negated) still raises
  at parse time. Regression guards for what must NOT change:
  `acct:.*`, `acct:a*`, `acct:^$`, `acct:()` all still parse and match
  successfully (the narrow-vs-broad scoping distinction, §2/§7 — a
  future "simplification" that broadens the check would break these).
- **Integration** (`tests/test_cli/test_cli.py`): `-q "acct:"` /
  `-q "tag:"` / `-q "tag:NAME="` via the CLI surface a clear error
  (whatever the CLI's existing `QueryParseError`-to-exit-code/stderr
  convention is — match it, don't invent a new one).
- **Differential** (mandatory, genuinely separate `compat-
  differential-tester` dispatch before any compat-register promotion,
  per §8): reproduce the full matrix in `25-query-regex-empty-pattern-
  matrix.md` against Ledgerkit post-fix, plus the narrow-vs-broad
  regression checks (`.*`/`a*`/`^$`/`()` must still work).

## 11. Summary of what needs explicit approval (gate)

This is a narrow, low-risk, fully-characterised fix — the approval list
is short:

1. **Approve the fix itself**: add a `pattern == ""` check to
   `validate_hledger_regex`, raising the existing, already-public
   `UnsupportedRegexConstructError` — no new exception class, no
   `UnsupportedRegexConstructError`/`validate_hledger_regex`/`compile_
   hledger_regex` signature change. **Corrected this pass**: this *is*
   a real, documented-behaviour change to public functions (§5.1) —
   `dev-docs/api-spec.md` must be updated at implementation time to
   state it, not skipped as "no API change."
2. **Approve the exact error message wording**, corrected this pass to
   be fully generic (no `tag:`-specific advice in the shared
   validator): *"pattern must not be empty (hledger rejects an empty
   regex at parse time)"* — or amend it. Tag-specific guidance moves to
   `docs/usage.md` (§9), not the exception message.
3. **Confirm non-goals** (§7): the empty-alternation-branch family
   (`(|)` etc.) and any broader "semantically admits empty" check are
   explicitly OUT of this fix. **Corrected this pass**: this family is
   no longer just a note — it is now filed as `LK-MISMATCH-QUERY-REGEX-
   EMPTYALT-001` (§7/§8), scoped strictly to what's actually verified
   (`(|)` confirmed both sides; the other four patterns hledger-side
   only). Confirm this filed-but-unimplemented status is the right
   outcome, not scope creep.
4. **Confirm the `LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001` closeout
   mechanics** (§8, corrected this pass): rename-and-reclassify to a
   new `LK-COMPAT-QUERY-TAG-EMPTYVALUE-001` entry once independently
   verified, not an in-place `kind:` flip that would leave a
   `MISMATCH`-prefixed ID classified `compatible`.
5. **General approval** to proceed to an implementation plan/fresh
   coding-agent dispatch, mirroring Phase 6's process at a scale
   proportionate to this fix's actual size (likely no separate
   "implementation plan" document is needed beyond this design's own
   §5/§10 — implementer's call to flag if it disagrees).

No implementation begins until this section's items are explicitly
decided.

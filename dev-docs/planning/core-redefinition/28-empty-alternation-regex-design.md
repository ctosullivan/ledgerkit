# 28. Empty-alternation-branch regex rejection — design document

Resolves `LK-MISMATCH-QUERY-REGEX-EMPTYALT-001`, the last remaining item
in Stage C Phase 6's original backlog. **Not an implementation plan in
the heavyweight sense** — the fix is fully specified below with a
validated algorithm; per this project's own precedent (Phase 7 §11
item 5), this document doubles as the implementation plan. No
`ledgerkit/`/`tests/` code touched producing this document.

## 0. Pinned revisions

Ledgerkit: `c5e4185`. hledger: `1.52.4` / `33fa849e7ae841968bd21c427094c4fb4a4ec38d`,
pinned binary `1.52.4-g33fa849e7-20260910`.

## 1. Re-established ground truth — [VERIFIED-EXTERNAL]

Per explicit instruction not to trust the entry's original (2026-09-25)
notes as still accurate, a fresh, independent `compat-differential-
tester` dispatch re-derived this mismatch from scratch on 2026-09-27,
against the CURRENT `ledgerkit/query/regex.py` (which changed since the
entry was first filed, during Stage C Phase 7's own empty-pattern-string
fix). Full matrix and root-cause trace: `dev-docs/compat-register/
LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`'s second evidence entry.
Summary:

- **Root cause, source-confirmed** (`hledger-lib/Hledger/Utils/
  Regex.hs`'s `toRegex`/`toRegexCI`, `Hledger/Query.hs`'s
  `parseQueryTerm`): hledger adds **no validation of its own** — every
  query-term regex string is passed straight to Haskell's `regex-tdfa`
  (`makeRegexM`), and every rejection (including the already-fixed
  empty-string case) is regex-tdfa's own parser failing, surfaced via
  one uniform error format: `"This regular expression is invalid or
  unsupported, please correct it:\n" <> s`. The empty-pattern-string
  case's apparently-different "nothing on line 2" shape is not a
  separate code path — it's the same interpolation with `s = ""`.
- **The exact, executable-validated rule** (35+ patterns tested, both
  tools, three query prefixes): a pattern is rejected by hledger if and
  only if it contains an **unescaped `|` with nothing (zero raw
  characters) immediately on one side of it**, where "nothing" means:
  on the left, the pattern starts there, or the immediately-preceding
  unescaped character is `(` or `|`; on the right, the pattern ends
  there, or the immediately-following unescaped character is `)` or
  `|`. This is a **purely local, single-character-adjacency** rule —
  no nesting-depth tracking is needed, because a nested group's own
  internal emptiness (e.g. `(a|)` inside `(a|)|b`) is caught by
  checking *that* group's own `|` against *its own* immediate
  neighbours, independently of the outer pattern.
- **Confirmed accepted by both tools** (must NOT be affected): `()`
  (empty non-alternation group — a distinct, valid regex-tdfa/GNU-ERE
  production, "matches empty string" as a single complete piece, not an
  empty alternation slot), `(a)`, `a|b`, `(a|b)`, `()|a`, `a|()`, `()*`,
  `a| |b` (a space is real content), anchor-only branches (`^|a`,
  `a|$` — `^`/`$` are real, non-empty characters lexically, even though
  zero-width semantically), and any pattern where the apparent `(`/`)`/
  `|` adjacency is actually **escaped** (`a\|\|b`, `\(|a`, `a|\)`).
- **Confirmed rejected by hledger, accepted by Ledgerkit** (the full
  divergence set — 18 patterns, not just the original 5): `(|)`, `a|`,
  `|a`, `(a|)`, `(|a)`, `a||b`, `(a|)|b`, `||`, `|`, `(|)|c`, `a|(|b)`,
  `(||)`, `a|||b`, `(|)*`, `(a)|`, `|(a)`, `a(|)b`, `(a|)(b)`.

## 2. Existing decisions this design must respect — [EXISTING-DECISION]

- `ledgerkit/query/regex.py`'s `_EXCLUDED_CONSTRUCT` is the existing
  single-compiled-regex detector for excluded constructs; its own
  documented edge-case tolerance ("false positives here are safe...
  false negatives are the actual risk") reflects that some imprecision
  in escape handling was already accepted project-wide for other
  constructs (e.g. the backreference check doesn't distinguish `\\1`
  from `\1`). This fix does **not** need or use that same tolerance —
  §3 below is escape-precise, validated against the exact escape cases
  hledger itself accepts (`a\|\|b` etc.), so no new imprecision is
  introduced.
- Stage C Phase 7's resolution-lifecycle mechanism (`dev-docs/compat-
  register/schema.md`'s "Resolution lifecycle" section,
  `09-compatibility-system.md` §9.7): resolving `LK-MISMATCH-QUERY-
  REGEX-EMPTYALT-001` creates a **new** entry (`LK-COMPAT-QUERY-REGEX-
  EMPTYALT-001`, `kind: compatible`), retains the original mismatch
  entry untouched except for `resolved_into`/`resolved_date`, and moves
  its `UNEXPLAINED.md` row from "Open entries" to "Resolved entries" —
  not an in-place `kind:` edit.
- `UnsupportedRegexConstructError` (already public, already the
  exception every other excluded-construct case raises) is reused —
  same precedent as Stage C Phase 7's own empty-pattern-string fix, no
  new exception type.

## 3. Proposed design — [PROPOSED]

### 3.1 Detection function

A new, dedicated, escape-aware scanning function in `ledgerkit/query/
regex.py` — not folded into `_EXCLUDED_CONSTRUCT`'s single regex,
because escape-counting (distinguishing a real `(`/`)`/`|` from an
escaped `\(`/`\)`/`\|`) needs a linear scan with state, not a single
`re.search`, to stay precise (Python's `re` module only supports
fixed-width lookbehind, which cannot correctly count a variable-length
run of preceding backslashes):

```python
# Detects an "empty alternation branch": an unescaped '|' with nothing
# (zero raw characters) immediately on one side of it, matching
# hledger's regex-tdfa's own rejection rule exactly (verified
# executably against the pinned binary, LK-MISMATCH-QUERY-REGEX-
# EMPTYALT-001's evidence -- not inferred from the manual, which does
# not document this rule at all).
#
# Purpose: reject `(|)`, `a|`, `|a`, `(a|)`, `(|a)`, and every further
#          pattern in the same family (`a||b`, `(a|)|b`, `||`, etc.),
#          while leaving `()`, `(a)`, `a|b`, `(a|b)`, `()|a`, `a|()`,
#          anchor-only branches, and escaped-pipe/paren sequences
#          untouched.
#
# Algorithm: a single left-to-right scan tracking escape state. For
#          each unescaped '|' found, check the immediately preceding
#          and immediately following characters (accounting for
#          escaping, not raw string position):
#            - LEFT is empty if this is the first character of the
#              pattern, or the nearest preceding unescaped character is
#              '(' or '|'.
#            - RIGHT is empty if this is the last character of the
#              pattern, or the nearest following unescaped character is
#              ')' or '|'.
#          Either side being empty means the pattern is rejected. No
#          nesting-depth tracking is needed: a nested group's own
#          internal emptiness is caught independently, by that group's
#          own '|' against its own immediate neighbours (e.g. in
#          `(a|)|b`, the inner `|` at index 2 has ')' immediately to
#          its right -- RIGHT empty -- regardless of what surrounds the
#          group).
#
# Edge cases:
#   - `a\|\|b` (escaped pipes): the '\|' sequences are consumed as
#     single escaped-literal units and never treated as real '|'
#     characters at all -- correctly not flagged.
#   - `\(|a` / `a|\)`: an escaped '(' or ')' does not count as the
#     empty-triggering neighbour it would be unescaped -- correctly not
#     flagged (the real '|' here has genuine content, the escaped
#     literal, immediately beside it).
#   - `^|a` / `a|$`: anchors are ordinary, non-empty characters for
#     this lexical check (regex-tdfa treats them as a real "piece"
#     occupying that branch, even though they match zero-width) --
#     correctly not flagged.
#   - `()` / `a|()`/`()|a`: '(' immediately after a '|', or ')'
#     immediately before a '|', do NOT trigger emptiness on their own
#     -- only a '|' immediately adjacent to '(' /'|' (on its left) or
#     ')'/'|' (on its right) triggers it. `()` alone (no '|' present at
#     all) is never inspected by this function in the first place.
def _has_empty_alternation_branch(pattern: str) -> bool:
    i = 0
    n = len(pattern)
    prev_real_char: str | None = None  # last unescaped char seen, or None at start
    while i < n:
        ch = pattern[i]
        if ch == "\\" and i + 1 < n:
            # Escaped character: consume both, count as ordinary content
            # (not a fence-post character), advance past both.
            prev_real_char = "\\"  # any non-fence sentinel works here
            i += 2
            continue
        if ch == "|":
            left_empty = prev_real_char is None or prev_real_char in "(|"
            # Look ahead to the next unescaped character without consuming it.
            next_real_char = None
            j = i + 1
            if j < n:
                if pattern[j] == "\\" and j + 1 < n:
                    next_real_char = "\\"
                else:
                    next_real_char = pattern[j]
            right_empty = next_real_char is None or next_real_char in ")|"
            if left_empty or right_empty:
                return True
        prev_real_char = ch
        i += 1
    return False
```

Wired into `validate_hledger_regex` as one additional check, alongside
(not replacing) the existing `pattern == ""` check and the
`_EXCLUDED_CONSTRUCT` scan:

```python
def validate_hledger_regex(pattern: str) -> None:
    if pattern == "":
        raise UnsupportedRegexConstructError(...)  # unchanged, Phase 7
    if _has_empty_alternation_branch(pattern):
        raise UnsupportedRegexConstructError(
            f"pattern {pattern!r} is outside the HledgerRegex-compatible "
            f"subset: an alternation ('|') has an empty branch on one "
            f"side (hledger's regex-tdfa engine rejects this, e.g. "
            f"'a|', '|a', '(|)')"
        )
    match = _EXCLUDED_CONSTRUCT.search(pattern)
    ...  # unchanged
```

### 3.2 Why a function, not a regex

`_EXCLUDED_CONSTRUCT`'s existing style is a single compiled regex with
named alternation branches. This detection could theoretically be
attempted the same way, but a regex-based approach for "is the
immediately-preceding character escaped" requires counting a run of
backslashes with correct parity — Python's `re` supports only
fixed-width lookbehind, which cannot express "an even number of
preceding backslashes" (a variable-length condition). A small, explicit
linear scan is simpler, more obviously correct, and directly mirrors
how a real regex engine's own tokenizer would make this determination
(track one character of look-back/look-ahead state, correctly skipping
escape pairs) rather than trying to force it through `re.search`.

## 4. Explicit non-goals

- Any other regex-tdfa-vs-Python-`re` divergence not in this specific
  family (e.g. POSIX bracket-expression edge cases, other lazy-
  quantifier variants) — unrelated, not discovered by this dispatch's
  research, out of scope.
- Broadening this fix into a general regex-semantics audit, per the
  original mismatch entry's own explicit instruction not to do so.
- Any change to `_EXCLUDED_CONSTRUCT`'s existing branches or their
  documented false-positive tolerance — untouched.
- `cur:`, smart/period dates, standalone `--depth`/`-N`, `PythonRegex`
  — unrelated Stage C backlog items, untouched.

## 5. Compatibility implications

- New compat-register entry `LK-COMPAT-QUERY-REGEX-EMPTYALT-001`
  (`area: query.regex.emptyalternation`, `kind: compatible`), created
  via the resolution-lifecycle mechanism (§2) once implemented and
  independently verified — `resolves: LK-MISMATCH-QUERY-REGEX-
  EMPTYALT-001`. The original mismatch entry is retained untouched
  except for `resolved_into`/`resolved_date`, per schema.md.
- `reason:` field must disclose: the full 18-pattern rejection set, the
  full accepted-set regression list, the escape-awareness guarantee,
  and cite the regex-tdfa root-cause source trace (§1) as the basis —
  not the manual (which doesn't document this rule at all).
- This is a **breaking, not backward-compatible** correction, same
  category as Stage C Phase 7's empty-pattern-string fix, made pre-1.0
  (`1.0.0.dev1`) — no version bump, per `dev-docs/versioning.md`'s
  existing policy. Any existing caller passing e.g. `acct:a|` or
  `tag:x=(|)` will now get `QueryParseError` where it previously got a
  (likely-unintended) match-everything result.
- First-time promotion to `status: verified` requires a genuinely
  separate `compat-differential-tester` dispatch (§9.6), same as every
  prior phase.

## 6. Documentation sync required (once implemented and verified)

- `dev-docs/hledger-compatibility.md` — the `acct:`/`desc:`/`tag:`/
  `depth:` regex-dialect note gains a line about empty-alternation-
  branch rejection, cross-referenced to the new compat-register entry.
- `dev-docs/api-spec.md` — `validate_hledger_regex`'s docstring gains a
  note about the new rejection (no signature change).
- `knowledge/DOMAIN_RULES.md` — the exact adjacency rule (§1), since
  it's genuinely non-obvious and not documented anywhere in hledger's
  own manual — a future maintainer re-deriving this from the manual
  alone would not find it.
- `knowledge/DECISIONS.md` — why a manual scan was chosen over a regex
  (§3.2).
- `CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` — per the standing rule.

## 7. Required tests

Every pattern in §1's two lists gets its own named test — not one
combined assertion, matching this project's own established convention
for precedence/edge-case matrices (Phase 6/7's own test style):

- **Must reject** (18 patterns): `(|)`, `a|`, `|a`, `(a|)`, `(|a)`,
  `a||b`, `(a|)|b`, `||`, `|`, `(|)|c`, `a|(|b)`, `(||)`, `a|||b`,
  `(|)*`, `(a)|`, `|(a)`, `a(|)b`, `(a|)(b)` — each raises
  `UnsupportedRegexConstructError` via `validate_hledger_regex`.
- **Must remain accepted** (regression guards): `()`, `(a)`, `a|b`,
  `(a|b)`, `()|a`, `a|()`, `()*`, `a| |b`, `^|a`, `a|$`, `a\|\|b`,
  `\(|a`, `a|\)` — each does NOT raise.
- **Integration**: at least one case wired through `-q` end-to-end
  (`parse("acct:a|")` raises `QueryParseError`) and through the CLI
  (`-q "acct:a|"` exits 1 with the existing `"invalid query"` message
  convention, no new error-handling path).
- **Differential** (mandatory, genuinely separate `compat-differential-
  tester` dispatch before compat-register promotion): reproduce the
  full matrix from §1 against Ledgerkit post-fix, confirming both lists
  hold exactly.

No separate approval gate section — this document, per §0, doubles as
the implementation plan; the fix is fully specified and the only
remaining steps are implementation, testing, and independent
verification, all authorized to proceed as part of this Stage C
closeout task.

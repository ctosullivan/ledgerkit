"""HledgerRegex: the hledger-compatible regex subset for acct:/desc: terms.

hledger's query regexes run on Haskell's regex-tdfa (POSIX-derived,
case-insensitive by default, infix matching); Ledgerkit's parser/eval run
on Python's `re` (PCRE-inspired). The two are not the same engine, and
some constructs mean different things — or nothing at all — under each.
This module never silently reinterprets a pattern using Python semantics
where the two differ: a pattern using an excluded construct raises
`UnsupportedRegexConstructError` rather than compiling to something that
would behave differently than the real hledger would (per
`dev-docs/planning/core-redefinition/07-query-regex.md` §7.3's hard rule,
verified against `17-query-semantics-brief.md` §5's construct-by-construct
table).

`PythonRegex` (the full-power Python `re` escape hatch) is Stage C
follow-on work — not implemented by this module; there is currently no
way to opt out of the HledgerRegex restriction from a query string.
"""

from __future__ import annotations

import re


class UnsupportedRegexConstructError(ValueError):
    """A pattern uses a regex construct outside the HledgerRegex subset.

    Raised instead of silently compiling the pattern, per this project's
    query-compatibility contract: a construct hledger's regex-tdfa either
    doesn't support, or would interpret differently than Python's `re`
    does, must never be quietly accepted.
    """


# Detects constructs that are either unsupported by hledger's regex-tdfa
# engine, or that Python's `re` would interpret differently (sometimes
# silently) than hledger does — see 17-query-semantics-brief.md §5's table
# for the citation behind each branch.
#
# Purpose: flag, rather than silently reinterpret, any pattern using a
#          construct outside the verified HledgerRegex-compatible subset.
#
# Group breakdown: named groups so match.lastgroup identifies which
#          excluded construct fired, for a precise error message.
#   (?P<paren_special>\(\?)        — any `(?...)` construct: inline mode
#                                     flags (?i)(?s)(?m), named groups
#                                     (?P<name>...), non-capturing groups
#                                     (?:...), lookaround (?=/?!/?<=/?<!.
#                                     hledger has none of these; Python
#                                     supports all of them, so an
#                                     unqualified `(?` is the single
#                                     broadest, safest signal to exclude.
#   (?P<backreference>\\[1-9])     — \1-\9: a real backreference in
#                                     Python, but hledger's manual states
#                                     `\1` inside a query pattern matches
#                                     the literal digit "1" — the same
#                                     text means two different things.
#   (?P<gnu_boundary>\\[<>])       — \< / \>: real GNU word-boundary
#                                     anchors in hledger; Python has no
#                                     such anchor and silently treats them
#                                     as escaped literal < / > characters.
#   (?P<perl_class>\\[dDwWsS])     — \d \D \w \W \s \S: Perl-style
#                                     shorthand classes, explicitly listed
#                                     as unsupported by hledger's manual.
#   (?P<posix_class>\[\[:\w+:\])   — [[:alpha:]] and similar POSIX named
#                                     classes: Python parses this as a
#                                     literal bracket-expression character
#                                     set (silently wrong either way).
#   (?P<lazy_quant>[*+?]\?)        — *? +? ??: lazy/non-greedy
#                                     quantifiers, explicitly unsupported
#                                     by hledger; real (and different) in
#                                     Python.
#
# Edge cases:
#   - Order matters: `perl_class` must not fire on the `\1`-`\9` case, and
#     doesn't (disjoint character classes: digits vs dDwWsS).
#   - A literal backslash-backslash (`\\\\`) followed by a digit is not
#     distinguished from a real backreference by this scan — full
#     escape-aware parsing is out of scope for this heuristic-but-precise
#     construct scan; false positives here are safe (they reject a pattern
#     Python could otherwise run), false negatives are the actual risk and
#     none are known for the constructs this pattern targets.
_EXCLUDED_CONSTRUCT = re.compile(
    r"(?P<paren_special>\(\?)"
    r"|(?P<backreference>\\[1-9])"
    r"|(?P<gnu_boundary>\\[<>])"
    r"|(?P<perl_class>\\[dDwWsS])"
    r"|(?P<posix_class>\[\[:\w+:\])"
    r"|(?P<lazy_quant>[*+?]\?)"
)

# Detects an "empty alternation branch": an unescaped '|' with nothing
# (zero raw characters) immediately on one side of it. This is a
# dedicated, escape-aware linear scan, not a compiled `re.compile()`
# regex like `_EXCLUDED_CONSTRUCT` above — see the Regex Documentation
# Rule note in this module's function-level comment for why a scan was
# chosen instead (also recorded in `knowledge/DECISIONS.md`): correctly
# telling an escaped `\|`/`\(`/`\)` apart from a real one requires
# counting a variable-length run of preceding backslashes for parity,
# which Python's `re` cannot express (only fixed-width lookbehind is
# supported). This rule matches hledger's regex-tdfa engine's own
# rejection exactly (verified executably against the pinned binary,
# `dev-docs/compat-register/LK-MISMATCH-QUERY-REGEX-EMPTYALT-001.yaml`'s
# evidence — not inferred from the manual, which does not document this
# rule at all).
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
#          `(a|)|b`, the inner '|' at index 2 has ')' immediately to
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
#   - `()` / `a|()` / `()|a`: a '(' immediately after a '|', or a ')'
#     immediately before a '|', do NOT trigger emptiness on their own
#     -- only a '|' immediately adjacent to '(' / '|' (on its left) or
#     ')' / '|' (on its right) triggers it. `()` alone (no '|' present
#     at all) is never inspected by this function in the first place,
#     since the scan only ever acts when it reaches a '|'.
#   - Trailing backslash (`pattern` ending in a lone unescaped '\\'):
#     `ch == "\\" and i + 1 < n` is false in that case, so the lone
#     backslash falls through and is treated as an ordinary character
#     rather than consuming a nonexistent next character -- this
#     function never raises or indexes out of bounds on a malformed
#     trailing escape (`compile_hledger_regex`'s later `re.compile()`
#     call is what would ultimately reject a truly invalid pattern).
def _has_empty_alternation_branch(pattern: str) -> bool:
    """Return True if `pattern` has an unescaped '|' empty on either side."""
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


_CONSTRUCT_MESSAGES = {
    "paren_special": (
        "'(?...)' constructs (inline mode flags, named/non-capturing "
        "groups, lookaround) have no hledger equivalent"
    ),
    "backreference": (
        r"backreferences like '\1' mean a literal digit in hledger's query "
        "regex, not a backreference"
    ),
    "gnu_boundary": (
        r"'\<'/'\>' are GNU word-boundary anchors in hledger; Python "
        "silently treats them as literal characters instead"
    ),
    "perl_class": (
        r"Perl-style shorthand classes ('\d', '\w', '\s', etc.) are not "
        "supported by hledger's regex engine"
    ),
    "posix_class": (
        "POSIX named classes like '[[:alpha:]]' are not supported the same "
        "way by Python's 're'"
    ),
    "lazy_quant": (
        "lazy/non-greedy quantifiers ('*?', '+?', '??') are not supported "
        "by hledger's regex engine"
    ),
}


def validate_hledger_regex(pattern: str) -> None:
    """Raise UnsupportedRegexConstructError if `pattern` leaves the HledgerRegex subset.

    Does not compile the pattern — call compile_hledger_regex() to validate
    and compile in one step. Raises re.error separately (unchanged) for a
    pattern that isn't valid Python regex syntax at all.

    Breaking change from Stage C Phase 6: an empty pattern ("") now raises
    UnsupportedRegexConstructError instead of validating successfully. Real
    hledger rejects an empty regex at parse time for every prefix that
    accepts one (acct:, desc:, tag:'s name/value halves, depth:'s REGEX
    half) — Ledgerkit previously diverged by accepting "" as "matches
    anything, including empty" (dev-docs/planning/core-redefinition/
    26-query-regex-empty-pattern-design.md). This rejects only the literal
    empty string, not any pattern whose semantics merely admit an empty
    match — '.*', 'a*', '^$', '()' remain valid and unaffected.

    Breaking change from Stage C Phase 9: a pattern containing an
    unescaped '|' with an empty branch on either side (e.g. 'a|', '|a',
    '(|)', 'a||b') now also raises UnsupportedRegexConstructError,
    matching real hledger's own regex-tdfa parse-time rejection of the
    same family (dev-docs/planning/core-redefinition/28-empty-
    alternation-regex-design.md; see _has_empty_alternation_branch's own
    comment for the exact adjacency rule). '()', '(a)', 'a|b', '(a|b)',
    '()|a', 'a|()', anchor-only branches ('^|a', 'a|$'), and escaped
    pipes/parens ('a\\|\\|b', '\\(|a', 'a|\\)') remain valid and
    unaffected.
    """
    if pattern == "":
        raise UnsupportedRegexConstructError(
            "pattern must not be empty (hledger rejects an empty regex "
            "at parse time)"
        )
    if _has_empty_alternation_branch(pattern):
        raise UnsupportedRegexConstructError(
            f"pattern {pattern!r} is outside the HledgerRegex-compatible "
            f"subset: an alternation ('|') has an empty branch on one "
            f"side (hledger's regex-tdfa engine rejects this, e.g. "
            f"'a|', '|a', '(|)')"
        )
    match = _EXCLUDED_CONSTRUCT.search(pattern)
    if match is not None:
        assert match.lastgroup is not None
        reason = _CONSTRUCT_MESSAGES[match.lastgroup]
        raise UnsupportedRegexConstructError(
            f"pattern {pattern!r} is outside the HledgerRegex-compatible "
            f"subset: {reason}"
        )


def compile_hledger_regex(pattern: str) -> re.Pattern[str]:
    """Validate and compile `pattern` as a case-insensitive HledgerRegex.

    Raises:
        UnsupportedRegexConstructError: pattern uses an excluded construct.
        re.error: pattern is not valid regex syntax at all.

    hledger's acct:/desc: matching is always case-insensitive and always
    infix (substring) — callers must use .search(), never .match()/
    .fullmatch(), on the returned pattern (17-query-semantics-brief.md §5).
    """
    validate_hledger_regex(pattern)
    return re.compile(pattern, re.IGNORECASE)

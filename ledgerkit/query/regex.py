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
    """
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

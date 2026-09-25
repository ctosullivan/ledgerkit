# 25. Query-regex empty-pattern matrix — live-binary findings

**Status:** pre-implementation research, not a design decision. Written by
an independently-dispatched `compat-differential-tester` session per
`09-compatibility-system.md` §9.4/§9.6, to give the next design phase
complete, precise ground truth beyond the single data point already filed
in `dev-docs/compat-register/LK-MISMATCH-QUERY-TAG-EMPTYVALUE-001.yaml`.
This file makes no `kind`/`status` claim of its own and is not a
compat-register entry — it is pure investigation output. No `ledgerkit/`
source was touched to produce it.

**Pinned binary used for every command below:**
`/home/cormac/.local/bin/hledger`, confirmed via `hledger --version` ->
`hledger 1.52.4-g33fa849e7-20260910, linux-aarch64`.

**Fixture (built fresh for this dispatch, not reused from
`tags_verify_basic.journal`):** `tests/fixtures/query_regex_empty_pattern_matrix.journal`
— two transactions, one posting-comment tag `blank:` with an empty value
(`; project:kitchen, blank:`) and one non-empty tag (`project:kitchen`),
distinct account names (`expenses:food:groceries`, `expenses:books`,
`assets:checking`) and descriptions, giving every query prefix below
something real to (not) match against.

Command shape used throughout: `hledger -f tests/fixtures/query_regex_empty_pattern_matrix.journal print '<query>'`.
Ledgerkit-side comparison commands (where run) use the CLI's own
convention from `tests/test_cli/test_cli.py`: `python -m ledgerkit -f
tests/fixtures/query_regex_empty_pattern_matrix.journal -q '<query>' print`.

---

## 1. Every regex-taking prefix, literally-empty pattern half

| Query | Exit | stderr (verbatim) |
|---|---|---|
| `acct:` | 1 | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` |
| `desc:` | 1 | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` |
| `tag:blank=` (name present, empty-value tag) | 1 | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` |
| `tag:project=` (name present, tag's real value is non-empty — sanity check that this isn't a `blank:`-specific artifact) | 1 | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` |
| `depth:=2` (empty REGEX half of `depth:REGEX=N`, per `dev-docs/hledger-compatibility.md`'s `depth:` row syntax) | 1 | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` |

Byte-for-byte `diff` confirms all five stderr outputs are **identical**
(same single line, terminated right after the trailing colon — nothing
printed after it, confirmed via `cat -A`: line ends `it:$` with no
trailing content). Sanity checks that non-empty-pattern forms of the same
prefixes work normally: `depth:assets=2` and `depth:2` both exit 0 with
real, depth-clipped output; `tag:blank` (bare name, no `=`) exits 0 and
matches the empty-value tag.

**Conclusion for point 1:** every regex-taking prefix (`acct:`, `desc:`,
`tag:`'s value half, `depth:`'s REGEX half) rejects an empty pattern
identically — same exit code, same exact error text. This is a single,
uniform rule in hledger's query parser, not five separate prefix-specific
checks.

## 2. Bare `tag:` (nothing after the colon at all)

`hledger -f <fixture> print 'tag:'` -> exit 1, **the exact same** stderr
as every case in §1 above (confirmed by `diff` against the `acct:` case's
captured stderr — byte-identical). Contrast `hledger -f <fixture> print
'date:'` (a non-regex prefix — see §4) -> exit 1 but with a **completely
different** error: `hledger: Error: "date:" gave a date parse error ()`.

**Conclusion for point 2:** bare `tag:` is not rejected as "missing NAME,
different error" — it goes through hledger's exact same
empty-regex-rejection path as `tag:NAME=` (empty value) and every other
prefix in §1. The most likely internal explanation (not independently
confirmed against hledger's Haskell source this session, since this
dispatch is executable-evidence-only) is that hledger's `tag:` parsing
splits on the first `=`; with no `=` present at all, the entire remainder
(here, the empty string after `tag:`) is treated as the NAME regex half
rather than the VALUE half, and NAME is *also* regex-compiled and subject
to the same empty-string rejection — so bare `tag:` fails for the same
underlying reason as an empty VALUE, just via the NAME slot instead. This
distinction (NAME-slot vs VALUE-slot rejection) is invisible from the
CLI's stdout/stderr/exit-code surface — both look identical from outside
— so the design phase should not assume Ledgerkit needs a *different*
error path for bare `tag:` versus `tag:NAME=`; one uniform "empty pattern
string is rejected" check appears sufficient for both, provided it is
applied to *both* the NAME and VALUE halves of `tag:`.

## 3. The central scoping question: empty STRING vs. anything matching empty

This is the most important result for the design phase. Tested against
both `acct:` and `desc:` (mirrored, see table below and the raw
transcript further down):

| Pattern | Can match empty string? | hledger result |
|---|---|---|
| `` (literally nothing) | trivially yes — it *is* empty | **rejected**, exit 1 |
| `.*` | yes | **accepted**, exit 0, real matches |
| `a*` | yes | **accepted**, exit 0, real matches |
| `x*` | yes | **accepted**, exit 0, real matches |
| `^$` | yes (matches *only* empty) | **accepted**, exit 0, 0 rows (no account/desc is literally empty in this fixture, but no error) |
| `()` (empty capture group, non-alternation) | yes | **accepted**, exit 0, real matches |
| `.+` | no (sanity control) | accepted, exit 0, real matches |
| `(|)` (empty alternation, both branches empty) | yes | **rejected**, exit 1, stderr: `...please correct it:` + pattern echoed on next line: `(|)` |
| `a|` (trailing empty alternative) | yes | **rejected**, exit 1, same two-line format, pattern echoed: `a|` |
| `|a` (leading empty alternative) | yes | **rejected**, exit 1, pattern echoed: `|a` |
| `(a|)` | yes | **rejected**, exit 1, pattern echoed: `(a|)` |
| `(|a)` | yes | **rejected**, exit 1, pattern echoed: `(|a)` |
| `a**` (stacked quantifier — not an emptiness case at all) | n/a | **rejected**, exit 1, pattern echoed: `a**` |

**Answer: hledger rejects the literal empty STRING specifically — a
narrow parse-time "you gave me zero characters" check — not any pattern
capable of matching an empty string.** `.*`, `a*`, `x*`, `^$`, and `()`
are all semantically capable of matching (or, for `^$`, *only* matching)
an empty string, and all five are accepted without complaint. Only the
genuinely zero-length input string is rejected.

The `(|)`/`a|`/`|a`/`(a|)`/`(|a)` family is a **separate, unrelated**
rejection: these are all regex-tdfa syntax restrictions on empty
*alternation branches* (an alternative with nothing on one side of a
`|`), not an "empty pattern" check at all — `a**` (a stacked-quantifier
syntax error, nothing to do with emptiness) is rejected via the exact
same generic error message family, confirming the message text itself is
generic ("this regex is invalid *or unsupported*") and covers multiple
distinct underlying causes. The tell that distinguishes the two
rejection causes from the CLI surface alone: the truly-empty-string cases
(§1, §2) print **nothing** after the trailing colon in the error message
(confirmed byte-for-byte via `cat -A`), while the
empty-alternation/stacked-quantifier cases print **the offending pattern
text** on the following line. This is a reliable, externally-observable
signal of "which of the two rejection causes fired" even without hledger
source access this session.

**Scoping implication:** the fix this mismatch entry calls for is the
**narrow** one — reject the pattern only when the input string itself is
empty (`pattern == ""`), checked before/independent of regex
compilation — not a broader "does this compiled regex accept the empty
string" semantic check. The broader check would be both wrong (it would
incorrectly reject `.*`, `a*`, `^$`, etc., which hledger accepts) and
unnecessary extra work. Note, as a related-but-separate observation
outside this dispatch's assigned scope: Ledgerkit's current regex dialect
also accepts `(|)` today (`python -m ledgerkit -f <fixture> -q
'acct:(|)' print` exits 0, matches everything, because Python's `re`
compiles `(|)` without error — an entirely different regex engine to
regex-tdfa) — this is a second, independent gap from the one this entry
tracks and is not addressed by the narrow empty-string fix above; noting
it here only so it isn't rediscovered as if new.

## 4. `status:` / `date:` — confirmed not regex-taking

- `status:` (bare, nothing after colon): exit 0, matches everything (no
  status restriction applied — degenerate/no-op, not an error).
- `status:*` (a character invalid as a status flag): exit 0, 0 rows, no
  error raised — confirms `status:` is parsed against a small fixed
  alphabet of flag characters, not compiled as a regex at all.
- `date:` (bare, nothing after colon): exit 1, but with **date-parsing**
  error text: `hledger: Error: "date:" gave a date parse error ()` —
  visibly different code path and message from every regex-rejection
  case above.
- `date:2024` (sanity check, valid date-query syntax): exit 0, real
  matches.

Confirms neither `status:` nor `date:` shares any code path with the
regex-empty-pattern rejection; this mismatch entry's scope is correctly
limited to `acct:`/`desc:`/`tag:`/`depth:`.

## 5. `not:` negation — rejection happens at parse time, before negation

- `not:acct:` (empty pattern): exit 1, stderr **byte-identical** (via
  `diff`) to plain `acct:`'s stderr.
- `not:desc:` (empty pattern): exit 1, same error text.
- `not:tag:blank=` (empty value): exit 1, same error text.

**Conclusion for point 5:** confirmed, as expected — the empty-pattern
rejection is a parse-time failure of the query-term grammar itself.
`not:` wrapping never gets a chance to matter because the term inside it
never successfully parses into a query node in the first place. No
special-casing of `not:` is needed in whatever fix follows from this
matrix; a parse-time check applied uniformly to the regex-bearing half of
each term (before AST construction, let alone negation-wrapping) is
sufficient and matches hledger's own behaviour exactly.

---

## Summary table for the design phase

| Prefix / form | Empty-pattern rejected? | Exact error text | Exit code |
|---|---|---|---|
| `acct:` | yes | `hledger: Error: This regular expression is invalid or unsupported, please correct it:` (nothing follows) | 1 |
| `desc:` | yes | same | 1 |
| `tag:NAME=` (empty value, any NAME) | yes | same | 1 |
| `tag:` (bare, empty NAME) | yes | same | 1 |
| `depth:=N` (empty REGEX half) | yes | same | 1 |
| `not:` + any of the above | yes (unchanged by negation) | same | 1 |
| `status:` | n/a — not regex-taking | n/a | 0 (no-op) |
| `date:` | n/a — not regex-taking | different code path entirely | 1 (date parse error) |

Rejection trigger: **the literal empty pattern string**, not any pattern
whose semantics happen to admit an empty match (`.*`, `a*`, `^$`, `()`
are all accepted). A syntactically distinct, unrelated rejection family
exists for empty-alternation-branch constructs (`(|)`, `a|`, `|a`,
`(a|)`, `(|a)`) and malformed quantifier stacking (`a**`) — these share
the same generic error *message* but are a different failure cause,
distinguishable externally by whether the offending pattern text is
echoed after the message (echoed => alternation/quantifier syntax
failure; blank => literal empty-string input).

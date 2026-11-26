<!-- producer: domain-skeptic | mode: REVIEW | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-03 -->
# Review note: journal-parsing assertions (001-010)

## Scope checked

All 10 draft assertion files (`journal-parsing-001.md` through `-010.md`)
against their cited evidence in `ledgerkit/parser.py`, `ledgerkit/models.py`,
`tests/test_parser/test_parser.py`, and `tests/test_directives/test_directives.py`
— the same permitted-evidence-paths list the original assertion-research
dispatch had. No other file was opened.

For every assertion I:
- read the cited line ranges directly rather than trusting the citation,
- confirmed every named test actually exists at (approximately) the cited
  line and asserts what the assertion claims it asserts,
- for several assertions, ran the parser directly against constructed
  inputs (via `python3 -c` importing only `ledgerkit.parser`/`ledgerkit.models`)
  to independently verify claims the cited tests didn't fully cover.
- ran the full `test_parser`/`test_directives` suites (233 tests, all pass)
  to confirm the codebase state matches what's described.

## Findings and fixes

### 1. journal-parsing-008 — CONFIRMED BUG, assertion corrected (not an ambiguity)

The draft's Statement claimed `parse_string_lenient` "never raises" without
qualification, with Counterexamples "none found". I traced every
non-indented directive handler in `_parse_string_impl` that calls a
ParseError-raising helper, looking specifically for one not gated by
`if errors_out is None: raise` (or an equivalent try/except). All of them
are gated — `Y` (parser.py:1511-1520), `D` (1536-1547), `P` (1433-1450),
`alias` (1469-1480), `decimal-mark` (1403-1422), transaction header
(1204-1213), posting-outside-block (1586-1595), posting parse
(1600-1612), elided-amount-count (1627-1641) — **except** the `commodity`
directive (parser.py:1324-1334), whose `symbol = _extract_commodity_symbol(body, lineno)`
call at line 1327 has no try/except or errors_out check at all.
`_extract_commodity_symbol` itself unconditionally raises `ParseError` on
an empty body, an unterminated quoted symbol, or an unparseable body
(parser.py:630/636/646).

I reproduced this directly:
```
parse_string_lenient("commodity\n")              -> raises ParseError, does not return
parse_string_lenient('commodity "unterminated\n') -> raises ParseError, does not return
```
Neither `tests/test_parser/test_parser.py` nor `tests/test_directives/test_directives.py`
exercises a malformed `commodity` directive under lenient mode —
`test_lenient_never_raises` covers bad postings/dates/garbage/stray
indentation, but not this directive, so the gap was both untested and
unasserted before this review.

This is a real, reproducible divergence in the current implementation
(a bug, not a documentation ambiguity), so I resolved it myself rather
than escalating: I edited journal-parsing-008.md's Statement to drop the
unqualified "never raises" claim and name the one exception explicitly,
expanded the Justification to show the handler-by-handler trace, and
replaced the "none found" Counterexamples with the confirmed repro.
Evidence-support state is left at `supported` because the corrected
Statement is now fully evidenced. **Flagging this prominently for the
lead/user regardless**, since it's a functional parser bug independent
of the documentation question — a malformed `commodity` directive can
currently crash an editor-integration caller that is relying on
`parse_string_lenient`'s documented never-raise contract.

### 2. journal-parsing-007 — citation error, corrected

The draft's Evidence-paths (`parser.py:1111-1575`) and its Counterexamples
parenthetical `(lines 1215-1230, 1550-1575)` were wrong in two ways:
- The pairing was backwards: 1215-1230 is the `comment`-directive *entry*
  point (not `apply account`), and 1550-1575 is `apply account`/`end apply
  account` (not block-comment). I verified both ranges by reading them.
- The full `comment`/`end comment` lifecycle isn't even fully inside the
  cited range: the `in_block_comment` skip-and-exit check that recognises
  `end comment` lives at parser.py:1008-1011, which is *before* line 1111
  and was entirely missing from the assertion's Evidence-paths.

Fixed by extending Evidence-paths to `parser.py:966-1011, parser.py:1111-1575`
and rewriting the Counterexamples paragraph to name all three non-adjacent
spans correctly with a reviewer note explaining the correction.

### 3. journal-parsing-003 and -009 — counterexamples independently verified (no change needed)

- 003's counterexample ("a single space does not split; the whole line
  becomes part of `account`") was marked "not separately unit-tested...
  implied by the regex." I ran it directly: `"assets:cash $5"` (one space)
  parses to `Posting(account='assets:cash $5', amount=None)`, confirmed.
  Left as-is since the assertion already honestly flagged the untested
  status rather than overclaiming.
- 009's counterexample about a bare leading `=` (`"= $500"`) not being
  matched by `_ASSERTION_MARKER_RE` was correct, and I additionally
  resolved its "Open questions" entry, which speculated the form "could
  not be confirmed... without consulting dev-docs/hledger-compatibility.md
  (out of scope)". That speculation was avoidable: running the parser
  itself (an in-scope evidence path) on `"= $500"` shows it is **not**
  handled anywhere else — it falls through to `_parse_amount` and raises
  `ParseError: invalid amount: '= $500'`. I updated the Open Questions
  field to record this resolution instead of leaving it as an open
  question.
- 009's "mutually composable" claim (balance assertion + cost annotation +
  lot annotations all on one posting) is not covered by the cited
  `test_all_annotations_combined` (which only combines cost+lot, no
  assertion marker). I constructed and ran a posting combining all three
  (`10 AAPL {$182.00} [2023-11-01] (lot1) @ $185.00 = $1850.00`) and
  confirmed all three resolve correctly and independently. No assertion
  file change needed since the claim held; noting it here as evidence
  this was actually checked, not merely accepted on the strength of the
  code's own structure.

### Everything else checked, no changes

001, 002, 004, 005, 006, 010: evidence-path line ranges were read in full
and matched their claims; every cited test name exists at (approximately)
the cited location and tests what's claimed; no contradictions found
between statements, examples, and counterexamples within the same file;
`resolve_elision`'s 0/1/2+ elided-posting cases (005) and the
parse-time rejection of 2+ elided postings (parser.py:1627-1641) were
read directly and match exactly. 006's four-way comment-handling
taxonomy was traced through the branch logic at parser.py:1045-1109
line by line, including the column-0-vs-indented and `;`-vs-`#`
distinctions, and matches both the code and the cited tests
(test_F06/F08/F09/S02, T09, hash-never-yields-tags).

## Escalating to lead

Nothing left as a genuine unresolved ambiguity for this topic — both
findings above were resolved directly from evidence within the permitted
paths (one by correcting a citation, one by correcting an overclaimed
"never raises" statement to match a confirmed, reproducible exception in
the current code). The commodity-directive lenient-mode bug (finding #1)
is not an escalation of an ambiguity, but I'm surfacing it to the lead
as a functional defect worth a tracked fix, since it affects a documented
public-API contract (`parse_string_lenient`'s never-raise guarantee) that
other topics' assertions or downstream consumers may be relying on.

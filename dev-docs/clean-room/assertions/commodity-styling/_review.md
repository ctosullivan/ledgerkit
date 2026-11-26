<!-- producer: domain-skeptic (REVIEW mode) | topic: commodity-styling | date: 2026-10-03 -->
# Review note: commodity-styling

Reviewed `commodity-styling-001.md` through `commodity-styling-008.md` against
the permitted evidence paths only:
`ledgerkit/commodity_style.py`, `ledgerkit/models.py`,
`tests/test_commodity_style.py`, `tests/test_parser/` (the whole directory,
contents: `__init__.py`, `test_parser.py`).

No legacy documentation was opened. No file outside the assertion set and
this note was written to.

## What I checked

- Read every `Evidence` field and traced its line citations against the
  actual source/test files, not just taken on trust.
- Re-ran the regex/branch logic in `commodity_style.py` by hand against the
  quoted code for all eight assertions.
- Independently executed `CommodityStyle.infer()`, `.format()`, and
  `.parse_style_override()` directly (read-only use of the module, no source
  edits) to probe edge cases the assertions' own stated rules predicted
  should exist but that no test in scope exercised.
- Cross-checked `Journal.commodity_styles` (models.py:338-374) and
  `ReportSectionResult.to_dataframe()` (models.py:252-292) against
  assertions 005 and 008's descriptions, and contrasted the latter against
  `Journal.to_dataframe()` (models.py:479-534) and `Amount.display()`
  (models.py:31-33) as assertion-008's own justification does.
- Grepped both test files for any direct exercise of `Journal.commodity_styles`
  or `resolve_elision`'s underlying implementation to confirm the "untested"
  claims in assertions 005 and 007 are accurate, not just assumed.

## What I fixed (edited the assertion files directly)

**commodity-styling-001** (`infer()`'s prefix/suffix detection): the original
text treated the "neither start nor end matches" fallback as a benign,
merely-untested edge case. I verified by direct execution that it is not
benign: `CommodityStyle.infer("EUR", "100.00 USD")` produces
`CommodityStyle(..., precision=6, ...)` — the unrelated trailing `" USD"`
text gets counted into `_infer_separators()`'s digit-count-by-string-length,
corrupting `precision`. Also verified, and now stated explicitly, that when
a commodity symbol matches *both* the start and end of the string (a
degenerate case, e.g. `infer("A", "A5A")`), the `if`/`elif` structure means
the prefix branch silently wins. Rewrote the Statement/Evidence/
Counterexamples/Open-questions sections to state these as verified facts
rather than unexamined "rare edge case" hand-waving. Evidence-support state
unchanged (`supported`) — the core rule was already correctly evidenced;
what I added is a previously-missing, now-resolved characterization of its
untested branch's actual (not assumed) behavior. One genuinely unresolved
piece remains and is now an explicit Open Question (see Escalating, below).

**commodity-styling-004** (negative-amount sign placement): the original
Counterexamples claimed "both prefix and suffix negative-formatting paths
are directly tested," which overstated coverage — only the `space=False`
prefix-negative case has a test. I verified directly that the rule (gap
dropped entirely in the negative-prefix branch, regardless of `self.space`)
also holds when `space=True` (`"$ 1,234.56"` positive vs. `"$-1,234.56"`
negative on the same style object, same `CommodityStyle`), closing the gap
myself rather than leaving the overstatement in place. Evidence-support
state unchanged (`supported`); the fix corrects a coverage overstatement and
adds the missing confirmation.

**commodity-styling-006** (`parse_style_override()`): the original Evidence
cited `tests/test_commodity_style.py:209-232` for
`test_c_flag_different_commodity_has_no_effect`, but that test actually
starts at line 221 (209 is the start of the *previous* test,
`test_c_flag_overrides_decimal_style`); tightened the citation to 221-232.
Also, the Statement claims `parse_style_override` raises `ValueError` when a
string "matches neither pattern," but no test in scope exercises that third
raise branch specifically (existing tests only cover the empty-string and
no-digits raise paths). Verified directly that
`parse_style_override("123.45")` (digits present, but no commodity symbol at
all) raises `ValueError` as the rule predicts, and added this as confirmed
evidence rather than an unexamined assumption. Evidence-support state
unchanged (`supported`).

**commodity-styling-007** (`resolve_elision` multi-commodity splice): the
cited `Evidence-paths` range (`tests/test_parser/test_parser.py:432-479`)
cut off 4 lines before the end of
`test_elided_position_preserved_in_middle` (which actually runs to line
483) — specifically, the lines asserting `result[-1].account == "b"` and
`middle.inferred == True`, which are exactly the lines the assertion's own
text relies on to support "preserving the order of the surrounding
non-elided postings" and the `inferred=True` marking. Corrected the range to
432-483. Evidence-support state unchanged (`supported`).

**commodity-styling-002, -003, -005, -008**: read in full, including
hand-tracing the branch logic and (for 002/003) directly executing
additional cases not in the test suite (repeated group separators across
both branches of the dots+commas priority rule, and the "3-digits-after"
single-separator heuristic) to confirm "regardless of how many times either
character repeats" and the single-separator classification rule hold as
stated. No errors found; no edits made. For 005 and 008, confirmed by grep
that no test in either permitted test file exercises
`Journal.commodity_styles` at all — their "untested, code-reading-only"
self-assessments are accurate, not just asserted.

## What I'm escalating

One genuine, unresolved ambiguity, left as an explicit Open Question in
`commodity-styling-001.md` rather than decided here: whether the
"commodity symbol absent from its own raw string" mismatch path (which I
confirmed produces a corrupted `precision`) is actually reachable in
practice via `Journal.commodity_styles`'s directive-based pass (pass 3) —
e.g. a `commodity` directive whose declared symbol doesn't literally occur
in its own sample-amount text. That depends on how
`_commodity_directive_raws` gets populated, which happens in
`ledgerkit/parser.py` — outside this topic's permitted evidence paths. I
have not guessed at an answer; this needs either the loader/parsing topic's
own review or a dispatch with `ledgerkit/parser.py` in scope.

A second, lower-priority item I am naming but not resolving or escalating
as a behavioral finding: `commodity-styling-005.md` has
`Evidence-support state: partially_supported` paired with
`Status: supported`, while `commodity-styling-008.md` has
`Evidence-support state: supported` paired with `Status: proposed`. Both
readings I can construct (a maturity ladder proposed→supported→verified
for `Status` that is a separate axis from `Evidence-support state`; or
`Status` tracking the described *feature's* rollout state rather than the
assertion's own evidentiary confidence) are self-consistent and plausible,
and the schema defining these two fields' precise relationship is not in
my permitted evidence paths (it would live in the assertion-research
dispatch's own instructions, not in `commodity_style.py`/`models.py`/the
test files). I have not changed either field — flagging only in case the
lead wants schema-level clarity across topics, not because I found either
file's content to be behaviorally wrong.

## Not escalated (resolved or already adequately caveated)

- The three-pass priority scheme in `Journal.commodity_styles`
  (commodity-styling-005): code-read confirms the docstring's stated
  priority and the code's actual pass order produce the same result; the
  assertion already honestly flags the lack of a confirming test via
  `Evidence-support state: partially_supported`. No change needed beyond
  independent confirmation.
- `ReportSectionResult.to_dataframe()`'s single-commodity limitation
  (commodity-styling-008): confirmed the dead first line
  (`list(self.rows.keys())[0]`) really is immediately overwritten, and that
  `Journal.to_dataframe()` really does look up styles per-posting correctly
  by contrast — the assertion's claims check out exactly against the code.

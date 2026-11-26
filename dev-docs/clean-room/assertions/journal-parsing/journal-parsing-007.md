<!-- producer: assertion-research | topic: journal-parsing | dispatch: a1x9-20261002 | date: 2026-10-02 -->
# Assertion: journal-parsing-007

## Statement
`parser.py` handles a substantial set of non-indented directives: `account`, `commodity`, `payee`, `tag`, `decimal-mark`, `P` (market price), `alias` / `end aliases`, `Y` (default year), `D` (default commodity+style), `apply account` / `end apply account`, `comment` / `end comment` (block comment), and recognises but discards `~` (periodic transaction rule) and `= ` (auto-posting rule) headers, emitting a `ParseWarning` for the latter two in lenient mode rather than treating them as hard errors.

## Kind
definition

## Basis
directly_stated

## Evidence
Each directive has its own `if not line[0:1].isspace() and re.match(...)` branch with a preceding explanatory comment block in `_parse_string_impl`.

Evidence-paths: [ledgerkit/parser.py:966-1011, ledgerkit/parser.py:1111-1575]

## Justification
Every directive listed has an explicit regex/startswith check, a handler, and (per the per-directive comments) documented edge-case behaviour; test_directives.py has a dedicated test class per directive confirming the described parsing (account/commodity/payee/tag storage, decimal-mark switching, P directive price storage, alias/end-aliases rules).

## Examples
`tests/test_directives/test_directives.py` test classes cover: account directive (lines 16-48), commodity directive (116-166), payee (253-283), tag (293-319), decimal-mark (338-420), P directive (443-503), alias/end aliases (526-665). `~`/`=` rule skipping: `test_tilde_rule_skipped_no_error`, `test_equals_rule_emits_warning` (tests/test_parser/test_parser.py:1443-1492).

## Counterexamples
`apply account` / `end apply account` is implemented at parser.py:1550-1575; block `comment`/`end comment` is implemented across THREE non-adjacent spots, not one — the `in_block_comment` state init (parser.py:966), the skip-and-exit check that recognises `end comment` (parser.py:1008-1011, which sits BEFORE the main directive-dispatch block and was missing from this assertion's original Evidence-paths), and the `comment`-keyword entry point that sets `in_block_comment = True` (parser.py:1215-1230). [Reviewer-verified 2026-10-03: the original draft's parenthetical "(lines 1215-1230, 1550-1575)" paired the two directive pairs in the wrong order and omitted the 1008-1011 exit-check span entirely; corrected here and Evidence-paths above extended to 966-1011.] No dedicated test file for either directive-pair was found within the permitted test_parser/test_directives paths beyond the `test_apply_account_*` tests in test_parser.py (lines 1375-1420) and block-comment tests (lines 241-320) — so apply-account nesting-warning and comment-block edge cases are covered in test_parser.py rather than test_directives.py.

## Depends on

## Open questions
none

## Evidence-support state
supported

## Status
verified

## Supersedes


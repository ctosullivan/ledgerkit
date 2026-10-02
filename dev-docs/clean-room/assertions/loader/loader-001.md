<!-- producer: assertion-research | topic: loader | dispatch: ldr-a1x9 | date: 2026-10-02 -->
# Assertion: loader-001

## Statement
Multi-file loading is triggered by a line-anchored `include <path>` directive. Detection uses the compiled regex `_INCLUDE_LINE = re.compile(r"^include\s+(.+)$")`: the line must start at column 0 with the literal keyword `include`, followed by one or more whitespace characters, with everything after captured verbatim (unstripped) in group 1 as the raw target path string. The caller (`_expand_includes`) strips this captured string before further processing, and raises `ParseError("include: missing file path", lineno)` if stripping leaves it empty.

## Kind
definition

## Basis
directly_stated

## Evidence
The regex and its accompanying required-format comment block state purpose, group breakdown, and edge cases directly above the regex definition; the strip-and-validate call site is immediately below it in `_expand_includes`.

Evidence-paths: [ledgerkit/loader.py:27-48, ledgerkit/loader.py:150-158]

## Justification
The regex's own anchor (`^`) means any indentation before `include` prevents a match (so posting lines are never mistaken for directives), and `\s+` immediately after the literal word `include` means words like `included`/`includes` do not match since no whitespace follows the embedded "include" substring at that position.

## Examples
- `"include ../b.journal"` → matches, group(1) == `"../b.journal"`.
- `"include  "` (keyword plus only spaces) → matches with a whitespace-only group(1); caller's `.strip()` makes it empty, triggering the "missing file path" ParseError. **Reviewer verification (2026-10-03):** confirmed by direct execution of `load_journal` against a temp file containing `"include   \n"`, which raised `ParseError: include: missing file path (line 1)` exactly as described. No dedicated test in `test_loader.py` exercises this exact string, so there is still no committed regression test guarding this behaviour, but the code-level claim itself is now execution-confirmed, not merely inferred from the comment.

## Counterexamples
- `"    include foo.journal"` (indented) does not match — anchors prevent it. **Reviewer verification (2026-10-03):** confirmed by direct execution — loading a file whose only content is an indented `include` line referencing a nonexistent target does NOT raise a missing-include error; instead the line is treated as an ordinary (invalid) content line and the resulting `ParseError` comes from the parser rejecting it as a posting outside a transaction block, proving the indented line was never recognised as a directive.
- `"included foo.journal"` does not match — no whitespace immediately follows the literal token "include".

## Depends on
None.

## Open questions
No test in `tests/test_loader/test_loader.py` directly exercises the whitespace-only-path ("include   ") case or the indented-include-is-ignored case. **Resolved by reviewer (2026-10-03):** both were independently verified by direct execution against `ledgerkit/loader.py` (see updated Examples/Counterexamples above) and behave exactly as the Statement describes. The remaining gap is a missing *committed* regression test, not a correctness question — flagged here as a test-coverage gap, not an open ambiguity.

## Evidence-support state
partially_supported

## Status
supported

## Supersedes
None.

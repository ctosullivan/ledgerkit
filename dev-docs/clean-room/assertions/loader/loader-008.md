<!-- producer: assertion-research | topic: loader | dispatch: ldr-h4w7 | date: 2026-10-02 -->
# Assertion: loader-008

## Statement
Because all included files are flattened into a single text blob before one `parse_string()` call, a `ParseError`'s line number is relative to that flattened text, not any original source file. `load_journal` builds `line_map: list[tuple[Path, int]]` during expansion — exactly one `(file_path, lineno)` entry per *retained* line of output (include directive lines themselves consume no entry, since they are replaced by their target's content rather than retained as output) — and uses it, on catching a `ParseError` from `parse_string`, to look up the true originating file/line and re-raise a new `ParseError` formatted as `"{orig_file}: {orig_msg}"` with the corrected line number. This remap only fires when `exc.line_number is not None and 1 <= exc.line_number <= len(line_map)`; outside that range, the original, untranslated exception is re-raised unchanged.

## Kind
state_transformation

## Basis
directly_stated

## Evidence
The remap logic, its bounds check, and the line_map accumulation discipline (append only for non-include lines) are explicit in code; a dedicated test confirms the included file's own filename appears in the surfaced error message.

Evidence-paths: [ledgerkit/loader.py:115-128, ledgerkit/loader.py:149-154, ledgerkit/loader.py:293-307, tests/test_loader/test_loader.py:326-348]

## Justification
`test_parse_error_attributes_to_included_file` constructs a root file that includes a broken file, triggers a posting-parse ParseError, and asserts the broken file's own basename (`broken.name`) appears in the final error string — this would only be possible if the line-number-to-file remap in lines 293-307 executed and substituted the correct originating path rather than the root file's path. **Reviewer verification (2026-10-03):** confirmed the full `line_map` invariant directly by calling `_expand_includes` on a two-file (root + one include) fixture and inspecting its return value — the number of output lines exactly equals the number of `line_map` entries, and each entry correctly names the originating file and local line number (included file's lines first, attributed to the included file; root's own lines attributed to the root file with their own original line numbers). This confirms the 1:1, non-include-lines-only accounting claim in the Statement is accurate, not just plausible from reading the code.

## Examples
- Root file `include broken.journal`, where `broken.journal` contains a malformed posting line → `load_journal` raises `ParseError` whose message contains `broken.journal`'s filename and (per the code) the line number local to `broken.journal`, not the flattened blob's line number (test-confirmed for filename presence; line-number correctness is asserted by code only, not directly checked by this test's assertions).

## Counterexamples
The fallback branch — `exc.line_number is None` or out of `line_map` bounds, causing the *original* untranslated error to propagate with no file re-attribution — is not exercised by any test in `tests/test_loader/test_loader.py`; it is inferred purely from the `if` condition at lines 296-306.

## Depends on
loader-001, loader-005

## Open questions
Under what parser conditions would `exc.line_number` actually be `None` or out of range, making the fallback path reachable? Not determinable from `loader.py` alone (parser internals are out of scope for this research).

## Evidence-support state
partially_supported

## Status
supported

## Supersedes
None.

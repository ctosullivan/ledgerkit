<!-- producer: assertion-research | topic: loader | dispatch: ldr-c3q8 | date: 2026-10-02 -->
# Assertion: loader-003

## Statement
When an include target string contains glob metacharacters, `_expand_includes` always filters the file containing the directive out of the resolved target list (`targets = [t for t in targets if t != file_path]`) before processing, regardless of whether the match was produced via glob expansion or a plain single-path resolution. If filtering leaves an empty list and the original raw target string was identified as a glob pattern, a `ParseError` ("include: no files matched {raw!r}") is raised.

## Kind
rule

## Basis
directly_stated

## Evidence
The filtering line applies unconditionally to `targets` (both glob and non-glob cases) before the `if not targets:` branch distinguishes glob (ParseError) from non-glob (FileNotFoundError) handling.

Evidence-paths: [ledgerkit/loader.py:162-177, tests/test_loader/test_loader.py:196-243, tests/test_loader/test_loader.py:213-220, tests/test_loader/test_loader.py:222-243]

## Justification
`test_glob_excludes_current_file`'s own comment states its intent directly: "this test confirms the loader never includes the root file even if a glob would match it" — i.e., self-exclusion is enforced independently of whether the containing file itself happens to satisfy the glob pattern.

## Examples
- `root_with_glob.journal` containing `include glob_*.journal` pulls in exactly the files matching that pattern, excluding itself (test-confirmed, `TestIncludeGlob`).
- `include no_match_at_all_*.journal` with zero matches → ParseError containing "no files matched" (test-confirmed).

## Counterexamples
Because the `file_path != target` filter applies even to the *non-glob* case, a literal self-include (e.g. a file containing `include self.journal` where `self.journal` is its own name) would have its single resolved target filtered out, making `targets` empty; since `is_glob` is False in that case, the code re-resolves *without* the self-filter (`_resolve_include_path(...)[0]`, line 173) and raises `FileNotFoundError` naming a path that actually exists on disk — a misleading error message. This exact scenario is not covered by any test in `tests/test_loader/test_loader.py`. **Reviewer verification (2026-10-03):** confirmed by direct execution — a temp file `selfinc.journal` containing `include selfinc.journal` raises `FileNotFoundError: include: file not found: <path to selfinc.journal> (referenced at <same path>, line 1)`, i.e. the error names a path that unquestionably exists on disk at the moment the error is raised. This is no longer an inference; it is a confirmed, reproducible behaviour of `ledgerkit/loader.py`.

A second, more severe counterexample was found during review (not originally identified in this assertion): the glob-vs-literal classification used to decide `is_glob` (computed from the *raw target string*) can disagree with the glob classification used internally by `_resolve_include_path` (computed from the *resolved absolute path string*, which includes `containing_dir`). When a containing directory's name itself contains a glob metacharacter (e.g. a directory literally named `inc[1]`), a plain, non-glob raw target resolved within it is silently treated as a glob pattern by `_resolve_include_path`, matches zero files via `glob.glob`, and — because `is_glob` (computed from the raw target, with no glob characters) is `False` — the code falls into the "re-resolve without filter and index `[0]`" branch at line 173, which raises an **uncaught `IndexError`** instead of either `FileNotFoundError` or `ParseError`. Confirmed by direct execution: `include foo.journal` inside a root file located at `.../inc[1]/root.journal`, where `.../inc[1]/foo.journal` genuinely exists, raises `IndexError: list index out of range`, not the documented FileNotFoundError. See loader-002 (Counterexamples) and loader-007 (Counterexamples) for the same finding from the other two angles.

## Depends on
loader-001, loader-002

## Open questions
Is the non-glob self-include FileNotFoundError-with-existing-path behavior (noted under Counterexamples) intentional, or an unhandled edge case? No test or code comment addresses it directly. The behaviour itself is now reviewer-confirmed as fact (see Counterexamples); what remains unresolved is purely the design question of intent. **Escalating to lead.**

Additionally escalating: the newly-found glob-metacharacter-in-containing-directory `IndexError` (see Counterexamples) is a confirmed defect relative to this assertion's own Statement ("a `ParseError` ... is raised" being the only documented failure mode for empty `targets`) — whether this is a known/accepted limitation or should be treated as a bug is a product question outside what evidence in `ledgerkit/loader.py` or `tests/test_loader/` can settle. **Escalating to lead.**

## Evidence-support state
partially_supported

## Status
proposed

## Supersedes
None.

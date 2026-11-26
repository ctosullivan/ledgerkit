<!-- producer: assertion-research | topic: loader | dispatch: ldr-g8t3 | date: 2026-10-02 -->
# Assertion: loader-007

## Statement
Missing-file handling during include resolution branches on whether the raw target string was itself detected as a glob pattern (`is_glob`, based on presence of `*`, `?`, `[` in the raw string): if `is_glob` is true and resolution yields no targets, `ParseError` ("no files matched") is raised; if `is_glob` is false and resolution yields no targets, `FileNotFoundError` is raised instead (not `ParseError`), naming the resolved absolute path and the referencing file/line. Separately, unsupported file extensions and known hledger format-type prefixes (e.g. `csv:`, `timedot:`) are always rejected with `ParseError`, checked before the not-found logic can apply.

## Kind
boundary

## Basis
directly_stated

## Evidence
The `if not targets:` branch in `_expand_includes` explicitly distinguishes the two raise types by the `is_glob` flag; `_validate_extension` and `_check_format_prefix` both raise `ParseError` and are called earlier in the per-target loop.

Evidence-paths: [ledgerkit/loader.py:51-65, ledgerkit/loader.py:68-83, ledgerkit/loader.py:162-177, tests/test_loader/test_loader.py:291-324]

## Justification
`test_unsupported_extension_in_include_raises` and both format-prefix tests directly assert `ParseError` with specific substrings ("unsupported file format", "format prefix"); `test_glob_no_matches_raises` directly asserts `ParseError` with "no files matched".

## Examples
- `include somefile.csv` → ParseError "unsupported file format" (test-confirmed).
- `include timedot:notes.journal` → ParseError "format prefix..." (test-confirmed).
- `include no_match_at_all_*.journal` → ParseError "no files matched" (test-confirmed).

## Counterexamples
`test_included_file_not_found_raises` (for `include ghost_nonexistent_file.journal`, a non-glob target) asserts only `self.assertRaises((FileNotFoundError, ParseError))` — a tuple accepting *either* exception type — so this specific test does not pin down which of the two is actually raised. **Reviewer verification (2026-10-03):** confirmed by direct execution — `load_journal` on a root file containing `include ghost_nonexistent_file.journal` raises `FileNotFoundError: [Errno 2] No such file or directory: '<resolved path>/ghost_nonexistent_file.journal'`, not `ParseError`. The documented distinction (ParseError for glob, FileNotFoundError for non-glob) is confirmed correct for this case; the loose test assertion is a test-authorship choice, not a correctness gap.

**A more significant counterexample found during review:** the clean two-outcome dichotomy this Statement describes ("if `is_glob` ... ParseError ... if not `is_glob` ... FileNotFoundError") is not exhaustive. `is_glob` is computed from the *raw target string* only, but the glob-vs-literal branch actually taken inside `_resolve_include_path` is computed from the *resolved absolute path string* (which includes `containing_dir`). When a containing directory's name itself contains a glob metacharacter (e.g. literally named `inc[1]`), a plain non-glob raw target resolved inside it is silently treated as a glob by `_resolve_include_path`, yields zero matches via `glob.glob` even though the target file exists, and because `is_glob` is `False` the code takes the non-glob branch, which re-resolves and indexes `[0]` into an empty list. Confirmed by direct execution: this raises an **uncaught `IndexError`**, a third outcome this Statement does not document and that is neither `ParseError` nor `FileNotFoundError`. See loader-002 and loader-003 (Counterexamples) for the same finding.

## Depends on
loader-001, loader-002, loader-003

## Open questions
Why does the one test that could discriminate FileNotFoundError vs. ParseError for the non-glob missing-file case deliberately accept both? (Possibly defensive/future-proofing, but not stated anywhere in the permitted evidence — low-priority, not escalated.)

Higher priority: is the uncaught `IndexError` outcome documented under Counterexamples a known/accepted limitation, or an unhandled bug that should raise `FileNotFoundError` or `ParseError` like the other missing-target cases? Not resolvable from `ledgerkit/loader.py` or `tests/test_loader/` alone — this is a product/design decision. **Escalating to lead.**

## Evidence-support state
partially_supported (the FileNotFoundError-vs-ParseError distinction is now reviewer-confirmed for the tested case; however, a third, undocumented outcome — an uncaught IndexError — was newly identified as a confirmed counterexample to the Statement's claimed two-outcome dichotomy)

## Status
proposed (downgraded by reviewer, 2026-10-03: the confirmed IndexError counterexample means the Statement's two-outcome dichotomy is not exhaustive as written; see Counterexamples and Open questions)

## Supersedes
None.

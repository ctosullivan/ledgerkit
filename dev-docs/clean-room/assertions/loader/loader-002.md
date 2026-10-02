<!-- producer: assertion-research | topic: loader | dispatch: ldr-b7k2 | date: 2026-10-02 -->
# Assertion: loader-002

## Statement
`_resolve_include_path(raw, containing_dir)` resolves an include target using fixed precedence: (1) if `raw` starts with `"~"`, expand via `Path(raw).expanduser()`; else (2) if `Path(raw).is_absolute()`, use as-is; else (3) resolve relative to `containing_dir` — the directory of the file that *contains* the include directive, not the process cwd and not necessarily the root file's directory (for nested includes, `containing_dir` is the immediate parent file's directory). If the resulting path string contains glob metacharacters (`*`, `?`, `[`), it is expanded via `glob.glob(..., recursive=True)` and the matches sorted; otherwise a single-element list of `base.resolve()` is returned.

## Kind
rule

## Basis
directly_stated

## Evidence
Function body and docstring lay out the precedence explicitly; the "relative to containing file's directory, not root" behavior is confirmed by a test using a nested subdirectory structure.

Evidence-paths: [ledgerkit/loader.py:86-112, tests/test_loader/test_loader.py:249-268, tests/test_loader/test_loader.py:270-280, tests/test_loader/test_loader.py:121-139]

## Justification
`test_relative_resolves_to_containing_dir` builds `tmpdir/sub/a.journal` containing `include ../b.journal`, and `tmpdir/b.journal`; loading `a.journal` successfully pulls in `b.journal`'s transaction, proving resolution uses `a.journal`'s own directory (`sub/`) as the base, not the root-invocation directory.

## Examples
- `sub/a.journal` contains `include ../b.journal` → resolves to `tmpdir/b.journal` (test-confirmed).
- `include /abs/path/to/file.journal` → used as-is (test-confirmed via `test_absolute_path_works`).

## Counterexamples
No counterexample found in code or tests for the documented precedence order *as applied to the raw target string in isolation*. However, **reviewer finding (2026-10-03), confirmed by direct execution of `ledgerkit/loader.py`:** the glob-vs-literal classification inside `_resolve_include_path` operates on `base_str = str(base)` — i.e. the *already-joined* absolute path (containing_dir + raw target) — not on the raw target string alone. If `containing_dir` itself contains a glob metacharacter (`*`, `?`, `[`) as a literal part of a directory name, a plain, non-glob raw target is silently reclassified as a glob pattern by this function, even though nothing in the raw include text looks like a glob. Reproduced directly: a directory literally named `inc[1]` containing `foo.journal`, included from a root file in that same directory via the plain line `include foo.journal` (no glob characters in the raw target), causes `_resolve_include_path` to call `glob.glob(base_str)`; `glob` interprets the literal `[1]` in the directory name as a character class, matches zero paths despite the file existing on disk, and returns `[]` instead of the single-element list the Statement promises for the non-glob case. This is a genuine divergence from "a single-element list of `base.resolve()` is returned" for inputs where the *path*, not the *raw target*, contains glob metacharacters. See loader-003 and loader-007 for the further consequences of this at the `_expand_includes` call site (an uncaught `IndexError` rather than either documented exception type).

## Depends on
loader-001

## Open questions
Tilde (`~`) expansion is implemented in code (line 100-101) but no test in `tests/test_loader/test_loader.py` exercises a `~`-prefixed include path. **Resolved by reviewer (2026-10-03):** confirmed by direct execution — calling `_resolve_include_path("~/doesnotexist.journal", containing_dir)` returns `[Path.home() / "doesnotexist.journal"]`, i.e. expansion against the real home directory as described, independent of `containing_dir`. Still no committed regression test for this branch (a genuine test-coverage gap, not a correctness question).

Separately, the glob-metacharacter-in-containing-dir issue noted under Counterexamples above is a genuine, unresolved design question: is this intended behaviour (the function's contract was never specified against adversarial directory names) or a latent bug? Not determinable from the Statement, code comments, or any test — **escalating to lead.**

## Evidence-support state
partially_supported (tilde-expansion gap now reviewer-confirmed as correct; the glob-metacharacter-in-path counterexample is a newly-identified, confirmed divergence from the stated contract, not yet a resolved design question — see Open questions)

## Status
supported

## Supersedes
None.

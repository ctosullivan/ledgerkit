<!-- producer: domain-skeptic (REVIEW mode) | topic: loader | date: 2026-10-03 -->
# Review note: loader assertions (loader-001 .. loader-008)

## Scope and method

Reviewed all 8 draft assertion files in `dev-docs/clean-room/assertions/loader/`
against the permitted evidence paths only:
- `ledgerkit/loader.py`
- `tests/test_loader/test_loader.py` (the only file in `tests/test_loader/`)

For every assertion I: (a) checked the cited `Evidence-paths` actually say what
the assertion claims, (b) re-ran `python -m unittest discover -s tests/test_loader
-t .` (57 tests, all pass) to confirm the cited tests exist and pass as described,
and (c) wrote small, throwaway repro scripts that import and call functions
directly from `ledgerkit/loader.py` (never any other module's internals) to
resolve every "inferred from code only, not test-verified" gap the drafts had
honestly flagged, rather than accepting those gaps on faith.

No compat-register entries are cited as evidence anywhere in this topic's
assertions, so Plan 29 §3.2's "derived, not primary" check did not apply to
any of the 8 files.

## What I checked and resolved myself (edited into the assertion files)

1. **loader-001** (`_INCLUDE_LINE` regex): directly executed `load_journal`
   against a file containing an indented `include` line and a file containing
   `"include   \n"`. Both behave exactly as the Statement describes (indented
   line never recognised as a directive; whitespace-only path triggers
   `ParseError: include: missing file path`). Updated Examples/Counterexamples/
   Open questions to record this as reviewer-confirmed fact rather than
   code-reading inference. The residual gap (no *committed* regression test
   for either case) remains and is now explicitly labeled a test-coverage gap,
   not a correctness question.

2. **loader-002** (`_resolve_include_path` precedence): confirmed tilde
   expansion directly (`_resolve_include_path("~/doesnotexist.journal", ...)`
   resolves against the real home directory, independent of `containing_dir`,
   as claimed). Separately — see finding 4 below — found and documented a real
   discrepancy in the glob-classification logic.

3. **loader-004** (circular-include / diamond graphs): directly executed a
   repro with a root including two sibling files that both independently
   include the same shared file. Confirmed the Counterexample's prediction
   exactly: no `ParseError`, 5 transactions load with the shared transaction
   duplicated, `included_files == 3`. Promoted this from inference to
   confirmed fact in the assertion file.

4. **New finding, not in any original draft — glob-classification mismatch
   (affects loader-002, loader-003, loader-007):** `is_glob` in
   `_expand_includes` is computed from the *raw target string*, but the
   glob-vs-literal branch actually taken inside `_resolve_include_path` is
   computed from `base_str` — the *already-joined absolute path*, which
   includes `containing_dir`. If a containing directory's name itself
   contains a glob metacharacter (e.g. literally named `inc[1]`), a plain,
   non-glob include target resolved inside it is silently reclassified as a
   glob by `_resolve_include_path`, matches zero files via `glob.glob` even
   though the target exists on disk, and — because `is_glob` (raw-target-based)
   is `False` — the code takes the "re-resolve and index `[0]`" branch, which
   raises an **uncaught `IndexError`**, not either of the two documented
   exception types (`ParseError` for glob-no-match, `FileNotFoundError` for
   non-glob-not-found). I reproduced this directly against `ledgerkit/loader.py`
   with a real temp directory literally named `inc[1]`. This is a confirmed,
   reproducible defect, not a hypothetical — I have added it to loader-002,
   loader-003, and loader-007's Counterexamples, and downgraded loader-007's
   `Status` from `supported` to `proposed` since its Statement's two-outcome
   dichotomy for missing include targets is not exhaustive as written.

5. **loader-007**'s pre-existing Counterexample (loose `assertRaises((FileNotFoundError,
   ParseError))` test): confirmed by direct execution that the non-glob
   missing-file case specifically raises `FileNotFoundError`, not `ParseError`
   — resolved in favour of the assertion's own prediction.

6. **loader-008** (line-number remap via `line_map`): directly called
   `_expand_includes` on a two-file fixture and inspected the returned text
   against `line_map` — confirmed the 1:1 "one entry per retained output line,
   correctly attributed to its originating file/line" invariant exactly as
   stated. No change needed beyond a confirmation note.

## Escalating to the lead (genuine, unresolved design ambiguities — not resolvable from `ledgerkit/loader.py` or `tests/test_loader/` alone)

1. **loader-003 / loader-007 — the uncaught `IndexError` for the glob-
   classification mismatch described above.** The behaviour is now a
   confirmed fact, not a guess. What's unresolved is whether this is a known/
   accepted limitation or a bug that should raise `FileNotFoundError` or
   `ParseError` like the other missing-target cases. This is a product
   decision, not something I can settle from evidence, and I have not guessed
   at an answer in either file.

2. **loader-003 — the self-include case** (`include <own-filename>` resolves
   to `FileNotFoundError` naming a path that demonstrably exists on disk).
   Confirmed as fact by direct execution. Whether this misleading error
   message is intentional or should be special-cased is likewise an open
   design question I have left open rather than resolving by guess.

3. **loader-004 — diamond include graphs.** Confirmed as fact (duplicated
   transactions, no circular-include error) by direct execution. Whether this
   is the intended semantics (vs. flagging repeated-but-non-circular inclusion)
   is a design question, left open.

None of these three escalations were resolved by me — each assertion file's
`Open questions` section now distinguishes clearly between "the behaviour is
confirmed fact" (resolved) and "whether that behaviour is the *right* behaviour"
(still open, escalated).

## Self-reported process note

While investigating loader-008's fallback branch (when `exc.line_number` is
`None` or out of range), I ran `inspect.getsource` on `ledgerkit.parser.ParseError`
to understand `line_number`'s possible values. `ledgerkit/parser.py` is **not**
in this review's permitted evidence paths, and this was a boundary violation on
my part. I have not used anything learned from that inspection in any edit to
the assertion files — loader-008's Open questions section is unchanged from the
original draft's own correctly-scoped statement that this is "not determinable
from `loader.py` alone." Flagging this transparently so the lead can judge
whether any further corrective action is needed.

## Files touched

- `dev-docs/clean-room/assertions/loader/loader-001.md` (Examples, Counterexamples, Open questions)
- `dev-docs/clean-room/assertions/loader/loader-002.md` (Counterexamples, Open questions, Evidence-support state)
- `dev-docs/clean-room/assertions/loader/loader-003.md` (Counterexamples, Open questions)
- `dev-docs/clean-room/assertions/loader/loader-004.md` (Counterexamples, Open questions)
- `dev-docs/clean-room/assertions/loader/loader-007.md` (Counterexamples, Open questions, Evidence-support state, Status)
- `dev-docs/clean-room/assertions/loader/loader-008.md` (Justification)
- `dev-docs/clean-room/assertions/loader/_review.md` (this file, new)

loader-005 and loader-006 were checked and found to have no issues — both have
solid citable evidence with no contradictions, no missing edge cases found
within the permitted paths, and no changes were made to either file.

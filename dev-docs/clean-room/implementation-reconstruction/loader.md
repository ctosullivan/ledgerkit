---
role: implementation-reconstructor
topic: loader
dispatch_id: plan29-phase-implrecon-loader-20261003
dispatch_timestamp: 2026-10-03T00:00:00Z
date: 2026-10-03
permitted_evidence_paths:
  - ledgerkit/loader.py
  - tests/test_loader/test_loader.py
  - "live execution of ledgerkit.loader functions"
---

# As-Built Reconstruction: `loader` (multi-file journal loading / include expansion)

This report is built *only* from direct reading of
`ledgerkit/loader.py`, direct reading of `tests/test_loader/test_loader.py`,
and live execution of `ledgerkit.loader` functions (Python REPL/script
probes run against a scratch directory, plus the existing test suite run
unmodified). No assertion, snapshot, implementation-comparison file, or
legacy `dev-docs`/`docs`/`knowledge` narrative was read to produce this
report, per the write-boundary this dispatch operates under.

## 1. Structure

`ledgerkit/loader.py` is a single ~310-line module with no submodules.
It is organized into:

- **Constants**: `_SUPPORTED_EXTENSIONS` (`{".journal", ".ledger"}`),
  `_FORMAT_PREFIXES` (`{"journal", "ledger", "timeclock", "timedot", "csv",
  "ssv", "tsv", "rules"}`), and one compiled regex `_INCLUDE_LINE`.
- **Validation helpers**: `_validate_extension`, `_check_format_prefix`.
- **Path-resolution helper**: `_resolve_include_path` (tilde/absolute/
  relative/glob resolution, returns a sorted list of resolved `Path`s).
- **Core recursive expander**: `_expand_includes` (reads a file, walks its
  lines, substitutes `include` directives with recursively-expanded
  content, builds a flat `line_map` for source attribution, does
  path-based circular-include detection).
- **Three public entry points**: `load_journal_stdin`, `merge_journals`,
  `load_journal`.

Its own stated responsibility (module docstring, lines 1-6): "Handles
file I/O, include directive expansion, path resolution, glob matching,
and circular include detection. Calls `parse_string()` for text-to-Journal
conversion." This matches what the code does — `loader.py` never parses
transaction/posting syntax itself; it only builds a single expanded text
blob (plus a line-attribution map) and hands that blob to
`ledgerkit.parser.parse_string`.

## 2. Public surface

Confirmed by reading the real signatures (no inference from names):

```python
def load_journal_stdin() -> Journal
def merge_journals(journals: list[Journal]) -> Journal
def load_journal(path: str | os.PathLike) -> Journal
```

Two private helpers are also exercised directly in tests/live probes
(`_expand_includes`, `_resolve_include_path`) but are not part of the
public surface (leading underscore, no re-export).

- `load_journal(path)` — the main entry point. Resolves `path` to an
  absolute `Path`, validates its extension, recursively expands all
  `include` directives into one text blob plus a `line_map`, calls
  `parse_string(expanded, source_file=str(abs_path))`, re-raises any
  `ParseError` from parsing with the line attributed back to its true
  originating file/line, then sets `journal.source_file` and
  `journal.included_files` on the result before returning it.
- `load_journal_stdin()` — reads all of `sys.stdin`, calls
  `parse_string` directly (no include expansion at all), sets
  `source_file = "(stdin)"`. Confirmed live: piping a one-transaction
  journal through stdin yields `source_file == "(stdin)"`,
  `included_files == 0`, and the transaction is parsed correctly.
- `merge_journals(journals)` — pure data concatenation of transactions,
  prices, and all four `declared_*` lists, in input order; `source_file`
  taken from the first journal; `included_files` summed. Returns the
  original object unchanged (identity, confirmed by `assertIs` in tests)
  when given a single-element list. Raises `ValueError` on an empty list.

## 3. Data model

`loader.py` defines no data classes of its own. It only populates two
fields on the `Journal` object returned from `ledgerkit.models` (imported,
not defined here):

- `journal.source_file: str` — absolute path string of the root file, or
  the literal string `"(stdin)"` for stdin input.
- `journal.included_files: int` — the count of *distinct* non-root files
  that contributed content, computed as
  `len({src for src, _ in line_map if src != abs_path})` — i.e. counted
  by unique resolved path, not by number of `include` directives
  processed.

Internally it builds two transient, not-returned structures:
- `visited: set[Path]` — the current include *ancestry chain* (not a
  global "already seen" set — see §5/§7).
- `line_map: list[tuple[Path, int]]` — one entry per line of *expanded*
  output text, mapping back to `(originating_file, originating_lineno)`.
  `include` directive lines themselves contribute no entry (they vanish,
  replaced by the included content).

## 4. Dependencies

Internal imports: `ledgerkit.models.Journal`, `ledgerkit.parser.ParseError`
and `ledgerkit.parser.parse_string`. (Per the write boundary for this
report, `models.py` and `parser.py` themselves were not read — only
their use from `loader.py` is described.)

External/stdlib: `glob` (aliased `_glob_module`), `os`, `re`, `pathlib.Path`.
No third-party imports, consistent with core-module dependency policy
observed in the file itself (nothing beyond stdlib is imported).

## 5. Runtime behaviour (traced + live-executed)

### 5.1 Include-line detection
`_INCLUDE_LINE = re.compile(r"^include\s+(.+)$")`. Confirmed live:
- `"include   "` (keyword + only spaces) *matches* (group 1 is
  whitespace-only); the caller then strips it to `""` and raises
  `ParseError("include: missing file path", lineno)`. Verified live.
- A bare `"include"` line (no trailing whitespace) does **not** match at
  all (requires `\s+` after the keyword) — it is passed through
  unchanged into the expanded text as ordinary content; `parse_string`
  then silently ignores it as an unrecognized top-level line (observed
  live: a file with a dangling `include` line parses fine and only the
  real transaction appears — this downstream skipping behaviour belongs
  to `parser.py`, outside this report's evidence scope, but the loader's
  own behaviour — "not treated as a directive" — is confirmed).
- An **indented** `include` line (e.g. `"    include leaf.journal\n"`)
  is never matched (`^` anchors to line start) and is therefore **never
  expanded** — confirmed live: it passes through into the parsed output
  and is picked up by `parser.py` as a *posting line* with account name
  literally `"include leaf2.journal"` and no amount. This is a real,
  observable consequence of the regex design, not merely a docstring
  claim.

### 5.2 Path resolution (`_resolve_include_path`)
Three resolution branches, in order: `~`-prefix → `Path(raw).expanduser()`;
absolute → used as-is; otherwise → joined with the including file's
directory. Then, if the resulting string contains any of `*`, `?`, `[`,
it is treated as a glob pattern and expanded via `glob.glob(..., recursive=True)`
(enabling `**`); otherwise it is used as a single literal path.

Live-confirmed behaviours:
- Tilde expansion works for both a literal path (`~/foo.journal`) and a
  glob pattern (`~/foo_*.journal`), including resolving to files in the
  real home directory.
- `**` recursive glob works (`include deep/**/*.journal` found a file two
  directories down; `included_files == 1`).
- Glob results are `sorted()` by resolved absolute path string, giving a
  deterministic ordering independent of filesystem directory-entry order.
- A glob that matches a **directory** (not just files) is not specially
  filtered out at the glob-resolution stage; it proceeds to
  `_validate_extension`, which raises `ParseError("unsupported file
  format '' …")` because a directory has no recognized suffix. This is
  handled (no crash), but the error message does not say "is a
  directory" — it reports an empty extension, which could read as
  confusing to an end user who didn't realize their glob matched a
  directory.

### 5.3 Glob-vs-literal classification — confirmed edge-case bug
The classification test (`any(c in raw for c in ("*", "?", "["))`) is a
**character-presence** test, not an escaping-aware parse. This means any
literal filename that happens to contain `*`, `?`, or `[` is
misclassified as a glob pattern, with no way to escape it. Live-confirmed:

- A real file literally named `data[1].journal`, referenced as
  `include data[1].journal`, **fails to load**: `glob.glob` interprets
  `[1]` as a character class matching the single character `1`, so the
  pattern only matches a (non-existent) file named `data1.journal`. The
  result is `ParseError: include: no files matched 'data[1].journal'`
  even though the literal target file exists on disk right next to the
  including file. **This is a genuine, reproducible gap**: filenames
  containing `[` cannot be included by their literal name at all.
- A real file literally named `data?.journal`, referenced as
  `include data?.journal`, **happens to work**, because `?` in glob
  syntax matches any single character including, coincidentally, a
  literal `?` at that filesystem position — but this is luck of glob
  semantics, not a deliberate literal-match guarantee, and is not robust
  in general (e.g. it would equally match `dataX.journal` if that file
  also existed in the same directory, silently including the wrong
  file or raising an ambiguous-match situation the code does not detect
  — there is no check that the "literal" target is uniquely resolved
  when it happens to also be a valid glob).

### 5.4 Self-reference filtering vs. cycle detection — two different mechanisms, confirmed
Line 164, `targets = [t for t in targets if t != file_path]`, strips the
*currently-expanding file itself* out of any resolved target list (this
is what lets a directory-wide glob like `include *.journal` not try to
re-include the file containing that very directive). This is **not**
the cycle-detection mechanism — cycle detection is the separate
`visited` set threaded through the recursion (added before recursing,
removed after return), which models the current include *ancestry
chain*, not a global "already-included-anywhere" set. Live-confirmed
consequences:

- **Self-include** (`A` contains `include A`, same file): `targets` is
  filtered to empty by line 164 (the self-filter), so the code falls
  into the "no targets, not a glob" branch at line 166-177 and raises
  `FileNotFoundError: include: file not found: <path-to-A>…` **even
  though `A` genuinely exists on disk**. The error message is
  misleading in this specific case — it says "file not found" for a
  file that is actually present; the real reason is self-exclusion, not
  absence. **This is a genuine gap**: there is no distinct, clear error
  for "a file tried to include itself."
- **Mutual two-file cycle** (`X` includes `Y`, `Y` includes `X`): raises
  `ParseError: circular include detected: …` correctly — confirmed live.
- **Diamond pattern** (`A` includes `B` and `C`; both `B` and `C` include
  `D`): **not** treated as a cycle (confirmed live) — `D`'s content is
  expanded and emitted **twice**, once under each parent branch, because
  `visited` is removed after each branch returns, so `D` is not "in
  progress" when the second branch reaches it. `included_files` for this
  case was `3` (unique files `B`, `C`, `D` — not `4`, because the
  counting is by unique source path in `line_map`, not by number of
  times a file was processed). **This is a real, observable behaviour
  with no deduplication**: a file reachable via two different include
  paths has its transactions duplicated in the resulting `Journal`, with
  no warning. The same duplication-without-warning occurs for a literal
  sibling double-include (`include leaf.journal` appearing twice in the
  same file): the leaf's transaction appears twice in output, while
  `included_files` still reports `1` (unique-file count, not
  directive/occurrence count).
- A **cycle reachable only through glob expansion** (two files in the
  same directory, each containing `include *.journal`) is still
  correctly detected via the `visited` ancestry-chain mechanism — the
  self-filter only strips the *immediate* including file from its own
  glob match, not transitive ancestors, so `A → (glob) → B → (glob) → A`
  still raises `ParseError: circular include detected: …`. Confirmed
  live.

### 5.5 Format-prefix rejection
`_check_format_prefix` rejects `prefix:` targets where `prefix` (lowercased,
text before the first `:`) is in `_FORMAT_PREFIXES`, but only when the
colon is at index `> 1` — i.e. a single leading character before `:` is
assumed to be a Windows drive letter and is deliberately *not* flagged.
Confirmed live: `include C:\fake\path.journal` is **not** rejected by the
format-prefix check; it instead falls through to ordinary relative-path
resolution (Windows backslashes are not path separators on POSIX, so the
whole string is treated as one literal relative path component) and
fails with a plain `FileNotFoundError`, not a `ParseError`. `timedot:` and
`csv:` prefixes are confirmed (live, and by the existing test suite) to
raise `ParseError` with "format prefix" in the message.

### 5.6 Error attribution after parsing (`load_journal`)
If `parse_string` raises a `ParseError` whose `line_number` falls within
range of the accumulated `line_map`, `load_journal` re-raises a new
`ParseError` whose message is prefixed with the *original* file path
(looked up via `line_map[exc.line_number - 1]`) and whose line number is
the original file's own line number — not the line number in the
flattened/expanded text. It also strips any pre-existing `" (line N)"`
suffix from the inner exception's message before re-wrapping, to avoid a
doubled line-number annotation. Confirmed by the existing test
`test_parse_error_attributes_to_included_file` and live execution: a
syntax error inside an included file is reported with that included
file's own basename in the message, not the root file's name.

### 5.7 Extension validation
`_validate_extension` only accepts (case-insensitively) `.journal` and
`.ledger`; every other suffix including `.j` (hledger's own journal
alias) is rejected with `ParseError`. Confirmed live and by tests
(`test_j_alias_raises`, `test_csv_extension_raises`,
`test_timeclock_extension_raises`). This check is applied both to the
root file (in `load_journal`) and to every individually resolved include
target (inside `_expand_includes`, including each file matched by a
glob) — so a glob that matches a mix of `.journal` and (say) `.txt`
files would raise `ParseError` on the first non-`.journal`/`.ledger` file
reached, aborting the whole load rather than silently skipping it.
(Not independently live-tested here beyond reading the code path at
line 180, but the control flow is unambiguous: `_validate_extension` is
called unconditionally per target inside the `for target in targets`
loop, before the circular-include check, and raises immediately.)

## 6. Tests (what they actually assert, read directly)

`tests/test_loader/test_loader.py` has 57 test methods across 9
`TestCase` classes, all passing when run (`python -m unittest
tests.test_loader.test_loader -v` — 57 passed, 0 failures, live-run
during this reconstruction). Coverage, read directly from test bodies
(not inferred from names):

- **`TestLoadJournalBasic`**: flat-file loading, `Journal` return type,
  `source_file` set/absolute/equal-to-resolved-root, `FileNotFoundError`
  on a missing root file, rejection of `.csv`/`.timeclock`/`.j`
  extensions, acceptance of `.journal`/`.ledger`, and that a plain
  `str` path works (not just `Path`/`PathLike`).
- **`TestIncludeBasic`**: single relative include merges transaction
  counts, counts `included_files == 1`, both root's and included file's
  transactions present without duplicating the root's own transaction,
  `source_file` stays the root file, and an absolute-path include works.
- **`TestIncludeRecursive`**: three-level nested include
  (`nested_a.journal` fixture) produces 3 transactions and
  `included_files == 2`; ordering is innermost-included-content-first
  (`C, B, A`) because the fixtures place `include` at the top of each
  file; explicit top-of-file and end-of-file include ordering tests.
- **`TestIncludeGlob`**: `root_with_glob.journal` fixture — glob `*`
  matches multiple files (2 transactions, `included_files == 2`); a
  no-match glob raises `ParseError` containing "no files matched"; a
  dedicated test asserts the loader never double-counts/re-includes the
  root file itself even when a glob could in principle match it (built
  by constructing a temp file whose glob target is itself a distinct
  temp file, not a true self-glob case).
- **`TestIncludePathResolution`**: relative include resolves against the
  *containing file's* directory (via a `sub/a.journal → ../b.journal`
  fixture layout, not the process cwd or the root file's directory) —
  this is a materially important, directly-asserted behaviour; and a
  plain absolute-path include.
- **`TestIncludeErrors`**: circular include (two fixture files,
  `circular_a.journal`) raises `ParseError` with "circular" in the
  message (case-insensitive check); unsupported extension and both
  `timedot:`/`csv:` format prefixes raise `ParseError` with the expected
  substrings; a nonexistent included file raises either
  `FileNotFoundError` or `ParseError` (test deliberately accepts either,
  i.e. does not pin down which exception type is used here); and a
  malformed transaction inside an included file raises `ParseError`
  whose message contains the included file's own name (attribution
  test, see §5.6).
- **`TestMergeJournals`** / **`TestMergeJournalsDeclared`**: identity
  return for a single-journal list, `ValueError` on empty list,
  transaction/price/declared-list concatenation order, `source_file`
  from the first journal, `included_files` summed, and that all four
  `declared_*` lists concatenate correctly including the all-empty case.
- **`TestStatsIntegration`**: `journal.stats().included_files` reflects
  the loader's own `included_files` value for flat/single-include/nested
  cases (so `Journal.stats()` — not read directly here, out of scope —
  is confirmed by its test-observed behaviour to propagate this field
  rather than recompute it).
- **`TestPublicAPI`**: `ledgerkit.load` is confirmed (by this test) to be
  an alias that reaches `load_journal` and returns a real `Journal`; and
  a `parse_string`-level test (technically exercising `parser.py`, not
  `loader.py`) asserts a lone `include` directive line is skipped by the
  parser when `parse_string` is called directly without going through
  the loader's expansion — i.e. confirms `include` lines are inert,
  non-erroring no-ops if `parse_string` ever sees one unexpanded.

No test in this file exercises: diamond includes, self-include, a
literal filename containing `[`/`?`/`*`, directory-matching globs, `**`
recursive glob, tilde-expanded glob patterns, or mixed-extension glob
matches. All of those were probed live for this report (§5) precisely
because the permitted-evidence-paths instruction called them out by
name as needing direct execution, not inference from existing coverage.

## 7. Limitations / gaps (honest, evidence-based)

1. **No escaping for literal glob metacharacters in include paths.** A
   file literally named with a `[` in its name cannot be included at
   all — `_resolve_include_path`'s classification
   (`any(c in base_str for c in ("*","?","["))`) has no escape syntax,
   and `glob.glob` then misinterprets the literal `[...]` as a character
   class. Confirmed to raise a misleading `ParseError: include: no files
   matched '…'` even though the target file exists. A `?` in a literal
   filename happens to work by coincidence of glob semantics, not by
   design, and is not guaranteed to pick the intended file if a
   same-length-collision filename also exists in that directory — this
   case is entirely unguarded against ambiguity.
2. **Self-include produces a misleading error.** `A` containing
   `include A` (its own filename) hits the self-filter
   (`t != file_path`) and lands in the "no targets, not a glob" branch,
   raising `FileNotFoundError: include: file not found: …` for a file
   that demonstrably exists. There is no distinct "a file cannot
   include itself" message.
3. **No deduplication across different include paths (diamond
   pattern).** If a file is reachable via two different `include`
   chains (directly as siblings, or as a diamond through two
   intermediate files), its content — transactions, prices, declared
   items — is expanded and merged **twice**, with no warning raised.
   `included_files` under-represents this: it counts unique *files*
   touched, not the number of times content was actually duplicated
   into the result, so a user inspecting `included_files` would not
   detect that duplication occurred. This is a real, silent
   correctness risk for any journal set with a diamond-shaped include
   graph (e.g. a shared `accounts.journal` included by two different
   per-year files that are both included from a master file).
4. **Directory-matching glob yields a non-obvious error.** If a glob
   pattern matches a directory as well as files, `_validate_extension`
   rejects it with `unsupported file format ''` — technically correct
   and non-crashing, but the message does not mention "directory",
   which could mislead a user debugging a bad glob pattern.
5. **Cycle detection is ancestry-based, not global, by design** — this
   is not necessarily a defect (it is what correctly allows the diamond
   pattern to not falsely error as circular) but it is the direct cause
   of limitation #3; the two behaviours are two sides of the same
   mechanism (`visited` tracks "currently on the stack", not "ever
   included").
6. **`load_journal_stdin` does not support `include` at all** — by
   construction (stdin has no filesystem path to resolve relative
   includes against), confirmed live: `included_files` is always `0`
   for stdin input and no include-expansion pass runs over stdin
   content; any `include` line in piped stdin content would be passed
   straight to `parse_string` and silently ignored exactly like a
   top-level `include` seen directly by the parser (§5.1 bare-`include`
   case) — this is a scope boundary rather than a bug, but it is not
   enforced with any explicit warning/error if a user pipes a journal
   that does contain `include` lines.
7. **Mixed-extension glob matches abort the whole load.** Per the
   unconditional `_validate_extension` call inside the per-target loop
   (§5.7), a glob that happens to match one non-`.journal`/`.ledger`
   file alongside valid ones raises `ParseError` for the whole
   `load_journal` call rather than skipping just the invalid match —
   confirmed by code-path reading; not independently live-executed in
   this pass, flagged here as read-but-not-executed evidence.
8. **The "exists but excluded by format prefix" case for a single
   leading character is deliberately not checked for prefix-length
   correctness** — the drive-letter exemption (`colon > 1`) will also
   silently let through any one-character "prefix" that happens to
   collide with a real format keyword abbreviated to one letter (none of
   the current `_FORMAT_PREFIXES` are one character, so this is latent,
   not currently triggerable — noted for completeness, not as an active
   bug).

## 8. `compat-register/*.yaml`

Not in this dispatch's permitted evidence paths — not consulted, per
instruction. No compatibility claim from that register is traced or
asserted in this report.

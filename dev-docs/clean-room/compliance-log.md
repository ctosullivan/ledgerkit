# Compliance log — CodeCompass upgrade + clean-room docs initiative

Per `dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md`
§4.2a/§5.4 (§8 Finding C4). One row per isolation-sensitive dispatch in
Phases 3 and 4 — the assertion-research and implementation-reconstructor
dispatches of Phase 3, and the drafting dispatches of Phase 4. Each
entry is written immediately after that dispatch's real tool-call
transcript is inspected, not reconstructed afterward from memory. A
`contaminated` verdict is followed by the id of the fresh dispatch that
replaced it.

Format per entry: topic/document, role, dispatch id (as the dispatch
itself named it, or the orchestrator's own agent-call id), verdict
(`compliant` / `contaminated`), and the specific transcript evidence
the verdict rests on.

---

## Phase 3 — assertion-research dispatches

### tags

- **Role:** assertion-research
- **Dispatch id:** `tags-r1`..`tags-r9` (per-assertion producer headers;
  orchestrator agent-call id `a8ecf0cf72867f032`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows exactly 2 tool calls, both `Read`:
  `ledgerkit/tags.py` and `tests/test_tags.py` — both explicitly
  permitted evidence paths for this topic. No other file read, searched,
  or opened; no test suite or other command run. The dispatch's own
  closing note additionally confirms it resolved a `TYPE_CHECKING`-only
  import of `Journal`/`Posting`/`Transaction` from `ledgerkit.models` by
  reading only the import line itself, explicitly declining to open
  `ledgerkit/models.py` even though it would have been a defensible
  judgment call — a conservative compliance choice, not a violation.

### checks

- **Role:** assertion-research
- **Dispatch id:** `ck-tiers-01`..`ck-dispatch-08` (orchestrator agent-call id `aaccdb9f8ee0d83da`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `ledgerkit/checks.py`; `Bash find` scoped to `tests/test_checks/`; `Read` on `test_checks.py` and `__init__.py`. All explicitly permitted. No other path opened; no test suite run.

### journal-parsing

- **Role:** assertion-research
- **Dispatch id:** `a1x9-20261002` (orchestrator agent-call id `a20219f6e65ec8c1e`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `ledgerkit/parser.py` (two calls, covering the full file) and `ledgerkit/models.py` (both explicitly permitted for this topic); `Bash find`/`wc`/`grep -n "def test_"` scoped to `tests/test_parser/` and `tests/test_directives/`; `Read` on `test_parser.py` (partial). No other path opened; no test suite run; no commit-message text cited.

### commodity-styling

- **Role:** assertion-research
- **Dispatch id:** `cs-infer-pos`..`cs-section-limit` (orchestrator agent-call id `a45fd58bf04f2f283`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `commodity_style.py`, `models.py`, `test_commodity_style.py` (all explicitly permitted); `Bash ls`/`grep` scoped to `tests/test_parser/`; `Read` on `test_parser.py` at several offsets. No other path opened; no test suite run.

### reports-cli

- **Role:** assertion-research
- **Dispatch id:** `rc-001`..`rc-015` (orchestrator agent-call id `ad53031c6a50e5f7e`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `reports.py`, `cli.py`, `writer.py` (all permitted); `Bash` running `python -m ledgerkit --help` and `python -m ledgerkit balance --help` (explicitly permitted real runtime observation); `Bash find` scoped to `tests/test_cli/`; `Read` on `test_cli.py`, `test_reports.py` (harness-truncated, not a boundary issue), `test_writer.py`. No other path opened; no full test suite run.

### loader

- **Role:** assertion-research
- **Dispatch id:** `ldr-a1x9`..`ldr-h4w7` (orchestrator agent-call id `a4ef1a1c1f1767f5d`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `loader.py`; `Bash find` scoped to `tests/test_loader/`; `Read` on `test_loader.py` and `__init__.py`. Fixture files under `tests/fixtures/` deliberately NOT opened (correctly recognised as out of this topic's permitted scope). No other path opened; no test suite run.

### current-state

- **Role:** assertion-research
- **Dispatch id:** `cs-research-01` (orchestrator agent-call id `a0cb3fc89abd9f549`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows only live commands (`cat pyproject.toml`; `git tag --list`/`git describe`; `python -m unittest discover`; `python -m ledgerkit --help` and per-subcommand `--help`; `grep`/`wc -l`/`ls` counts against `dev-docs/compat-register/*.yaml` filenames and `^kind:` lines only, never reading a YAML file's full content with `Read`). Zero reads of `ROADMAP.md`, `README.md`, or any other excluded path — the dispatch explicitly declined to and said so. No forward-looking content appears in any produced assertion.

### compat-system (first attempt)

- **Role:** assertion-research
- **Dispatch id:** orchestrator agent-call id `a3b4dbd2c02241356`
- **Verdict:** `contaminated`
- **Evidence:** The dispatch's own self-report states it read `dev-docs/compat-register/README.md` and `dev-docs/compat-register/UNEXPLAINED.md` **in full** before recognising they "contain substantive dated narrative prose beyond a plain index" — directly contrary to this dispatch's own explicit instruction ("if it has substantive prose framing, skip it... skim only enough to see if it's a plain mechanical list"). This is a real boundary violation against the instruction given, even though neither path is named in the hard invariant's own "at minimum" list — the instruction existed precisely to keep this category of risk out, and the dispatch read the full files before checking rather than after a minimal skim.
- **Action:** **Output discarded entirely** (never delivered to the orchestrator as full assertion content in any case — see below). **Rerun from a fresh context** with a corrected instruction: README.md/UNEXPLAINED.md are now flatly forbidden, no skim-first judgment call left to the dispatch.
- **Separate note:** this dispatch's response to the orchestrator also only contained a summary of findings, not the full per-assertion file content it claimed was "already posted above" — the actual assertion records were never received and cannot be recovered (confirmed by a follow-up dispatch that checked disk, git history, and its own context and found no trace). This is an independent reason the rerun is needed regardless of the contamination finding.

### editor-surface (first attempt)

- **Role:** assertion-research
- **Dispatch id:** orchestrator agent-call id `afc5c280b961d65cb`
- **Verdict:** `compliant` (on the boundary-compliance axis specifically)
- **Evidence:** Transcript shows a real `git clone --depth 1` of `ledgerkit-editor` to a scratch path, then `Read`/`Bash grep` restricted to its `src/`/`tests/` source and test files only — explicitly never its `README.md` or docs. In the main `ledgerkit` repo, only `editor_model.py` and `test_editor_model.py` were read. No excluded path in either repository was touched.
- **Separate note, not a compliance failure:** the full per-assertion file content was never actually delivered to or persisted by the orchestrator (a content-delivery gap, not a boundary violation) — a follow-up dispatch sent to retrieve it confirmed, correctly and honestly, that it had no memory of writing it and nothing exists on disk or in git history to recover. **The research itself does not need to be discarded as contaminated** (the transcript shows it was compliant), but the content must be regenerated via a fresh dispatch since there is nothing real to write to disk from the first attempt.

### compat-system (second attempt)

- **Role:** assertion-research
- **Dispatch id:** orchestrator agent-call id `a51f1d27ce86e12a6`
- **Verdict:** `contaminated`
- **Evidence:** The dispatch's own self-report flags, unprompted, that it ran `grep` against `/home/cormac/projects/ledgerkit/ledgerkit/parser.py` and `ledgerkit/models.py` — neither file is in this topic's permitted-evidence-paths list (compat-register YAMLs, schema.md, and targeted `tests/` lookups only). Per §4.2a, any read outside the given permitted-evidence-paths list is contamination regardless of whether the output used it — the dispatch separately, convincingly cross-checked and confirmed no assertion's `Evidence-paths`/`Justification` cites either file, but the rule is applied mechanically here, not waived on the strength of that self-check.
- **Action:** **Output discarded entirely.** Rerun from a fresh context with an even more explicit boundary restatement (no `ledgerkit/*.py` source reads under any circumstance for this topic, confirming only test *existence*, never implementation citations).
- **Note, for proportion:** unlike the first attempt (reading README.md/UNEXPLAINED.md — genuine legacy-narrative risk), this violation is a scope-boundary slip onto *other primary evidence* (source code also treated as evidence for other topics), not a brush with excluded narrative — still logged and discarded per the mechanical rule, not because the specific files read pose the same risk the hard invariant targets.

### query-engine

- **Role:** assertion-research
- **Dispatch id:** `qe-ast-001`..`qe-compatshim-015` (orchestrator agent-call id `ae1af67bf4c2ca680`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Bash find` scoped to `ledgerkit/query/` and `tests/test_query/` only; `Read` on every file under both directories (ast.py, parser.py, eval.py, regex.py, depth.py, compat.py, __init__.py; test_parser.py, test_eval.py, test_regex.py, test_compat.py, __init__.py). One `git log --oneline` call touching these same paths was run but its commit-message output was explicitly NOT used as evidence for any assertion, per the commit-message hard rule — stated directly in the transcript. No other path opened; no test suite run. (This dispatch ran across a session rate-limit interruption and resumed via the same agent context — the eventual full content and transcript are both genuine, not reconstructed.)

### editor-surface (second attempt — successful)

- **Role:** assertion-research
- **Dispatch id:** `edsurf-a1`..`edsurf-a10` (orchestrator agent-call id `a9115212402a37e76`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `Read` on `editor_model.py`/`test_editor_model.py` (both permitted); a real `git clone --depth 1` of `ledgerkit-editor` to a fresh scratch path; within that clone, `Read`/`Bash grep` restricted to `src/`/`tests/` `.py` files only, explicitly never its `README.md`/docs. No path in either repository outside the permitted set was touched. This is the real, usable research for this topic — the first attempt's content was lost in transit (not a compliance violation; see that attempt's own log entry) and is superseded by this one.

### compat-system (third attempt — successful)

- **Role:** assertion-research
- **Dispatch id:** `compat-reg-001`..`compat-reg-011` (orchestrator agent-call id `a67ad10eb56c1ae79`)
- **Verdict:** `compliant`
- **Evidence:** Transcript shows: `ls`/`cat`/`grep` restricted to `dev-docs/compat-register/*.yaml` and `schema.md`; `Read` on both those and on a local tool-cache file holding the same `cat`'s own just-produced stdout (an artifact of the harness's own output-size handling, not a new source — explicitly reasoned through and disclosed in the transcript, not hidden); targeted `grep`/`find` against named files under `tests/` to confirm cited class/method existence only. Ran a deliberate negative control (grepped for a nonexistent class `TestNonexistentDirectiveXYZ`, confirmed zero matches) to prove its own grep calls were actually searching live content, not silently no-op'ing — a genuinely good independent-verification practice, not merely compliant. Explicitly confirmed, in its own closing line, that no file under `ledgerkit/` was ever opened, and that README.md/UNEXPLAINED.md/examples/ were never opened. This is the usable research for this topic; the first two attempts are superseded (contaminated/discarded, per their own log entries above).

## Phase 3 — domain-skeptic REVIEW-mode dispatches

(Note: per plan §4.2a's own text, the mandatory immediate-discard rule names only the assertion-research and implementation-reconstructor dispatches explicitly. REVIEW-mode dispatches are logged here for the same transparency discipline, but a brief, self-disclosed, explicitly-unused peek outside a topic's own evidence list is recorded as a compliance *note*, not a contamination verdict requiring discard — unlike assertion-research, where the same category of slip was discarded per the mechanical rule. The distinction: assertion-research produces the primary evidentiary record; REVIEW mode only edits/confirms it, and its own output here is independently traceable per-field, so an unused aside doesn't propagate.)

### reports-cli — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `a7c254467f0ce4b32`
- **Verdict:** `compliant`, with one disclosed note
- **Evidence:** Fixed reports-cli-005 (false "necessarily nets to zero" claim, live-disproved with a nonzero depth:0 counterexample), reports-cli-010 (upgraded from inferred/proposed to directly-confirmed via live CLI execution, with the genuine design-intent question correctly escalated rather than guessed), reports-cli-011 (arithmetic error, "10" corrected to "12" lines). reports-cli-015 was read and explicitly left unedited.
- **Note:** self-disclosed briefly opening `ledgerkit/checks.py` (outside this topic's permitted paths) while tracing `check`-command control flow in reports-cli-015 — explicitly not cited and not the basis of any edit (reports-cli-015 itself stayed unedited). Logged per the discipline above, not treated as contamination.

### journal-parsing — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `a75b06b71c5f79bd6`
- **Verdict:** `compliant`
- **Evidence:** Fixed journal-parsing-007 (citation mix-up), -008, -009 via direct execution within permitted paths only (`ledgerkit/parser.py`, `ledgerkit/models.py`, `tests/test_parser/`, `tests/test_directives/`). **Found a real production bug, not fixed (out of scope): `parse_string_lenient`'s documented "never raises" guarantee is false for a malformed `commodity` directive** (`_extract_commodity_symbol` at parser.py:1327 lacks the try/except guard every other directive handler has) — confirmed by direct execution, journal-parsing-008 corrected to state this exception rather than the absolute claim. Recorded for the closeout report; not a documentation defect to silently paper over.

### loader — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `a3acc2767179dda8c`
- **Verdict:** `compliant`, with one disclosed note
- **Evidence:** Fixed loader-001/002/004/007/008 via direct execution. **Found a real production bug, not fixed (out of scope): a containing directory whose name itself contains a glob metacharacter (e.g. `inc[1]`) causes `_expand_includes`'s glob-vs-literal classification to diverge from `_resolve_include_path`'s own, silently misrouting a plain non-glob include into an uncaught `IndexError`** — confirmed by direct execution against a real `inc[1]` directory, documented in loader-002/003/007.
- **Note:** self-disclosed running `inspect.getsource` on `ledgerkit.parser.ParseError` (outside this topic's permitted paths) while investigating loader-008's fallback branch — explicitly confirmed unused; loader-008's Open Questions remain exactly as originally scoped. Logged per the REVIEW-mode discipline above, not treated as contamination.

### editor-surface — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `a770fd9bb2d3ecbef`
- **Verdict:** `compliant`
- **Evidence:** Fixed editor-surface-001 (miscount), -008 (anchored-grep false negative missed 8 of 9 real import sites — a genuinely important correction), -009 (line-number off-by-one), all via re-grepping within permitted paths. Escalated editor-surface-006 (whether `pyproject.toml` was legitimately in scope for the ledgerkit-editor clone) — resolved by the lead below, not left open.

### compat-system — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `a0c291df97e877589`
- **Verdict:** `compliant`, with one disclosed judgment call
- **Evidence:** Independently re-derived every count in compat-system-003/004 from scratch (not just re-read); confirmed all 23 verified_by/self-verified attributions; fixed compat-system-009/010 (completed the previously-partial test-citation trace). Disclosed judgment call: used `awk`-bounded class/def-signature extraction (never full test-body content) to confirm nesting for two citations — reasoned as consistent with the existence-only rule's intent; accepted as such, logged for transparency.

### query-engine — domain-skeptic REVIEW

- **Dispatch id:** orchestrator agent-call id `aee282775a7af095b`
- **Verdict:** `compliant`
- **Evidence:** Fixed query-engine-001 (overclaimed `__all__` exact-match), -006 (wrong worked example, self-contradicting query-engine-005's own rule), -014 (specificity direction stated backwards, self-contradicting its own next clause) — all via direct execution within `ledgerkit/query/` + `tests/test_query/`. Flagged (not fixed, no write access to tests/) a real test-coverage gap: `clipped_depth_for_account`/`clip_account_name`/`account_excluded_by_depth` have zero dedicated unit tests.

## Phase 3 — lead resolution of the one real escalation

**editor-surface-006** (domain-skeptic REVIEW escalation, dispatch `a770fd9bb2d3ecbef`): queried whether the original assertion-research dispatch's citation of the ledgerkit-editor clone's `pyproject.toml:16` exceeded its own "source and test .py files only" scope. **Resolved by the lead**: this was an imprecision in the *dispatch prompt's* own wording, not a compliance violation by the dispatch — `pyproject.toml` is a build/config file, which the governing task's own Objective 3 explicitly lists as legitimate primary evidence ("package/build/configuration files"), for an external repo exactly as much as for Ledgerkit's own. Reading the *external* project's own dependency-pin file to establish the coupling version is squarely in scope; the restriction to "source and test .py files only" was meant to exclude that repo's *narrative* documentation (README, docs/), not its config. editor-surface-006.md restored to `supported`/`verified` with this reasoning recorded in the file.

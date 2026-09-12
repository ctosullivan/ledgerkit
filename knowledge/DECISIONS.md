# Decisions

Non-obvious judgment calls made during development. Each entry explains what was chosen, why, and what was rejected.

---

## 2026-09-12 — Stage A compat-register migration scoped to a representative first wave, not full transcription

**Decision:** when closing out the rest of Stage A (agent-role files +
compatibility harness), the register migration described in
`dev-docs/planning/core-redefinition/09-compatibility-system.md` §9.5
("every In-Scope/Out-of-Scope row becomes an entry") was scoped down, on
the user's explicit choice among three offered options, to: directive
entries (11 + 1 newly identified divergence), validation-check entries
(8), and the genuinely-unsupported-feature entries (5) — 25 entries total.
The finer-grained rows (date formats, amount formats, comment forms,
account-name rules) were **not** migrated in this pass.

**Why:** a full mechanical migration would have been ~57 individual YAML
entries, each needing a real `implementation:`/`tests:` citation grepped
from the code — a large batch with real per-entry effort, not pure
transcription. Rather than either quietly doing a fraction of the literal
instruction or unilaterally expanding scope to all 57, the choice was put
to the user directly (three options: full migration, representative first
wave, harness-only). This is not a re-scoping of the underlying plan —
§9.5 already anticipated migration happening incrementally ("verified as
Stage A's compatibility-harness work runs through them"), so remaining
rows are still fully in scope, just not yet done.

**What was rejected:** doing all ~57 entries in this session (rejected by
the user for cost/thoroughness tradeoff reasons) and doing harness-
scaffolding-only with zero new entries (rejected in favour of getting real,
citable content into the register now).

**Follow-up:** the remaining In-Scope-table rows (Transactions, Account
Names, Amounts, Comments sections of `dev-docs/hledger-compatibility.md`)
are still unmigrated — this is tracked in `ROADMAP.md`'s Stage A row and
`CONTEXT.md`, not silently dropped.

## 2026-09-12 — Relicensed MIT → GPL-3.0-or-later

**Decision:** ledgerkit moves from the MIT License to GPL-3.0-or-later,
effective from the first release after this date. Already-published
releases (through `1.0.0`/`1.0.0.dev1`) remain MIT.

**Why:** hledger itself is GPL-3.0-or-later (confirmed from `license:`
fields in `hledger.cabal`/`hledger-lib.cabal`, not inferred from the
`LICENSE` file text alone). Matching it allows Ledgerkit development to use
hledger's documentation, source, and test suite directly as compatibility
evidence, with recorded provenance, instead of maintaining a self-imposed
clean-room separation. See
`dev-docs/planning/core-redefinition/02-licence-migration.md` and
`10-source-assisted-development.md` for the full reasoning, including the
important nuance that *reading* GPL source was never restricted by
licence mismatch — what actually changes is that Ledgerkit can now
lawfully host directly-translated hledger expression, should that ever
occur, which it could not under MIT.

**Known consequence, accepted deliberately:** `ledgerkit-editor` imports
`ledgerkit` in-process (not via subprocess) — confirmed by inspecting its
actual source (`ledgerkit.Query`, `ledgerkit.EditorDocument`,
`ledgerkit.parse_string_lenient`, `ledgerkit.{models,reports,checks,parser,
commodity_style}`, `ledgerkit.{load,journal_to_text,transaction_to_text}`
are all used directly, most substantially in `filter_popup.py` and
`query_match.py`) — so a GPL library embedded in-process inside an MIT
application is not a stable long-term combination. **`ledgerkit-editor`'s
own relicensing is an explicit separate decision, made in that
repository, on its own timeline — not bundled into this change.** Any
*other* third party embedding `ledgerkit` in-process faces the same
constraint going forward; this was weighed explicitly (see the licence
migration doc's options table) and accepted in favour of exactly matching
hledger's licence family, rather than choosing LGPL for library-friendliness.

**Rejected alternatives:** LGPL-3.0-or-later (library-friendly, but doesn't
literally match hledger's licence); restructuring `ledgerkit-editor` to a
subprocess boundary instead of relicensing it (disproportionate rewrite of
its editor-integration layer, which exists specifically for in-process
access); dual-licensing (ongoing administrative overhead not justified for
a single-maintainer project).

**Applies to:** `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`,
`pyproject.toml`, `README.md`, `CONTRIBUTING.md`, `dev-docs/versioning.md`,
`ledgerkit/__init__.py`, and (separately) the `ledgerkit-editor` repository.

**Addendum, 2026-09-12 (same day, CI-driven correction):** the initial
commit used a PEP 639 `license = "GPL-3.0-or-later"` SPDX string, verified
only locally, which broke CI's Python 3.8 job. Reverted to the classic
`license = {text = "GPL-3.0-or-later"}` form (kept alongside the `License ::`
classifier), which is exactly the pattern the prior MIT declaration used
successfully across the full 3.8–3.12 matrix. See
`knowledge/ANTIPATTERNS.md` — "PEP 639 `license` string-expression while
still supporting Python 3.8".

---

## 2026-04-15 — Parser silently accepts unbalanced transactions

**Decision:** `parse_string` does not validate that postings sum to zero. Unbalanced transactions are stored as-is and only rejected later by `checks.py`.

**Why:** The parser's job is to produce a structural model from text. Balance validation is a semantic check that belongs at the reports/checks layer, where the caller can decide whether to enforce it.

**Rejected alternative:** Raising `ParseError` in the parser when postings don't balance.

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/checks.py`

---

## 2026-04-15 — Posting indentation is conventional, not required

**Decision:** The parser does not enforce 2-space or tab indentation on posting lines. Any non-header line inside an open transaction block is treated as a posting.

**Why:** hledger 1.52 documents indentation as conventional. Enforcing it would reject valid journals and contradict the compatibility spec.

**Rejected alternative:** Strict `line.startswith("  ") or line.startswith("\t")` gate (was the original implementation; removed).

**Applies to:** `ledgerkit/parser.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-17 — Only `.journal` and `.ledger` file formats supported

**Decision:** `load_journal()` and the `include` directive only accept `.journal` and `.ledger` extensions. All other hledger format families (`.csv`, `.timeclock`, `.timedot`, `.rules`, `.prices`, `.ledger-json`) raise `ParseError`.

**Why:** The other formats require fundamentally different parsers. Supporting them is a future milestone, not v1.

**Rejected alternative:** Silently ignoring unsupported formats or accepting any extension.

**Applies to:** `ledgerkit/loader.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-17 — File I/O extracted to `loader.py`; `parser.py` is pure text-only

**Decision:** `parse_file()` was removed from `parser.py`. All file reading, include resolution, and glob expansion live in `loader.py`. `parse_string()` is the only public entry point in `parser.py`.

**Why:** Separates concerns cleanly. The parser is a pure function (text → Journal); the loader handles I/O, paths, and multi-file merging. Easier to test each in isolation.

**Rejected alternative:** Keeping `parse_file()` in `parser.py` alongside `parse_string()`.

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/loader.py`

---

## 2026-04-xx — `alias` directive is file-scoped at parse time

**Decision:** Aliases apply to account names within the file they are declared in, processing them at parse time. They are not propagated to including files.

**Why:** Matches hledger 1.52 semantics. Applying aliases globally would cause surprising account rewrites in unrelated included files.

**Rejected alternative:** Accumulating aliases across all included files and applying them in a post-processing pass.

**Applies to:** `ledgerkit/parser.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-04-xx — `decimal-mark` directive only applies forward, not retroactively

**Decision:** A `decimal-mark` directive only affects amount parsing for postings that appear *after* it in the file. Postings before the directive use the previous decimal mark (default: period).

**Why:** This matches hledger's streaming-parse model. Retroactive application would require a two-pass parser.

**Rejected alternative:** Applying the decimal mark to all transactions in the file regardless of position.

**Applies to:** `ledgerkit/parser.py`

---

## 2026-04-27 — `assert amt is not None` over `self.assertIsNotNone()` for type narrowing

**Decision:** In tests, bare `assert x is not None` is used (not `self.assertIsNotNone(x)`) immediately after extracting a `Posting.amount` field.

**Why:** Pylance recognises bare `assert` as a type-narrowing guard and eliminates `reportOptionalMemberAccess` warnings. `self.assertIsNotNone()` does not narrow the type in Pylance's analysis.

**Rejected alternatives:** `cast()`, `# type: ignore`, `if x is None: self.fail(...)`.

**Applies to:** `tests/test_parser/test_parser.py`, `tests/test_directives/test_directives.py`

---

## 2026-04-27 — Minor version bump (0.2.0) for new milestone

**Decision:** Version bumped from `0.1.2` → `0.2.0` when starting Milestone 2.

**Why:** Minor version increments mark the start of a new milestone (new user-visible feature area). Patch versions are used for fixes and admin changes within a milestone.

**Rejected alternative:** Continuing to bump patch version (0.1.3, 0.1.4, …) indefinitely.

**Applies to:** `ledgerkit/__init__.py`, `pyproject.toml`

---

## 2026-04-27 — Test subdirectories require `__init__.py`

**Decision:** Every test subdirectory (`test_parser/`, `test_directives/`, etc.) has an explicit `__init__.py`.

**Why:** Python 3.13's `unittest discover` silently skips namespace-package subdirectories (those without `__init__.py`). Without the file the tests are simply not found, with no warning.

**Rejected alternative:** Using namespace packages (no `__init__.py`).

**Applies to:** `tests/` subdirectories

---

## 2026-05-03 — `assertions` added to `BASIC_CHECK_NAMES` (not `OTHER_CHECK_NAMES`)

**Decision:** The `assertions` check runs automatically (basic tier) on every CLI command, not as an opt-in named check.

**Why:** hledger treats balance assertions as automatic — they are enforced at journal-load time rather than requiring explicit invocation. Adding them to `OTHER_CHECK_NAMES` would mean users could silently ignore assertion failures unless they explicitly ran `check assertions`, which defeats the purpose.

**Rejected alternative:** `OTHER_CHECK_NAMES` placement, which would match the existing pattern for `payees`, `ordereddates`, etc.

**Applies to:** `ledgerkit/checks.py`, `dev-docs/hledger-compatibility.md`

---

## 2026-05-03 — Balance assignments deferred (not validated in Milestone 2)

**Decision:** The parser accepts `= AMOUNT` syntax with no preceding posting amount (balance assignment — where the assertion implies the posting amount). It stores `posting.amount = None` and `posting.balance_assertion` as normal, but `check_assertions` does not infer the elided amount from the assertion.

**Why:** Balance assignments are a distinct feature from balance assertions. Implementing them correctly requires inferring the posting amount (affecting `check_autobalanced`) and potentially the order of check evaluation. Scoped out to keep Milestone 2 focused.

**Rejected alternative:** Raising a `ParseError` when a balance assignment is encountered (too strict — valid hledger files should load without error even if the assignment isn't validated).

**Applies to:** `ledgerkit/parser.py`, `ledgerkit/checks.py`

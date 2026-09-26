# Stage C closeout retro — Query system

- **Date:** 2026-09-27
- **Commit(s):** see `git log` for this retro's own commit; the full
  Stage C history spans `f86dd28` (Phase 1's first commit) through
  `29e0233` (the final drift-audit fix before this retro).
- **Agents used this closeout task specifically:** `docs-reconstructor`
  (Phase 7's own audit; Phase 9's own re-verification cross-check; two
  Stage-C-wide passes), `release-phase-auditor` (Phase 7's own audit;
  one Stage-C-wide final pass), `compat-differential-tester` (the
  Phase 9 mismatch re-verification and its independent implementation
  verification), `docs-maintainer` (one Stage-C-wide reconciliation
  pass), a fresh coding agent (Phase 9's implementation). Individual
  phases' own retros (18 files under `dev-docs/retros/STAGE-C-PHASE-*`)
  document each phase's own agent usage in full; this retro is the
  Stage-level synthesis, not a re-narration of each phase.

## Where we are

Stage C ("Query system: parser/AST, hledger query semantics, Python
`re` extension, CLI/report routing") is now feature-complete across all
nine phases, independently verified, and documentation-reconciled at
both the per-phase and Stage-wide level. This retro closes out the
Stage as a whole — distinct from, and synthesising across, every
individual phase's own retro, none of which are rewritten or
superseded by this one (per this project's "never rewrite a past
retro, only add" rule, which this retro respects by being a new,
separate file, not an edit to any phase's own record).

## Goal

Complete Stage C's Definition of Done: every phase implemented and
independently verified; the last open compatibility mismatch resolved;
`PythonRegex` given an explicit disposition instead of remaining
ambiguous backlog; the remaining query-language scope (`cur:`,
smart/period dates, a standalone `--depth` flag, `check`'s non-wiring)
confirmed as genuine, documented, non-blocking deferrals rather than
accidentally-incomplete exit criteria; a Stage-wide documentation
reconciliation and drift audit; and an independent release-phase audit
against Stage C's own Definition of Done — then report, honestly,
whether that Definition of Done is actually met.

## Scope delivered vs planned

Everything the closeout task specified was delivered, in the order
requested:

1. **Phase 7's outstanding closeout gates** — implementation and
   independent verification had been complete for some time, but Phase
   7 had never received its own `docs-reconstructor`/`release-phase-
   auditor` pass, unlike Phase 8. Both ran clean (NO DRIFT, PASS) and
   Phase 7 was marked `[DONE]`.
2. **`LK-MISMATCH-QUERY-REGEX-EMPTYALT-001` resolved** — re-established
   fresh from source and a live pinned-hledger run rather than trusted
   from its own prior notes (which predated Stage C Phase 7's code
   changes). The re-verification found the divergence was larger than
   originally filed (18 confirmed patterns, not 5) and traced the root
   cause to hledger's own regex-tdfa delegation with zero pre-
   validation of its own. A design was written, hand-verified against
   the full 31-pattern matrix before implementation, implemented by a
   fresh coding agent, tested (36 new tests), and independently
   verified with zero discrepancy. Resolved through the register's own
   resolution-lifecycle mechanism (established in Phase 7): a new
   `LK-COMPAT-QUERY-REGEX-EMPTYALT-001` entry, the original mismatch
   retained as untouched history.
3. **`PythonRegex` explicitly resolved** — deferred, not implemented,
   not dropped, with a recorded, reasoned decision (`knowledge/
   DECISIONS.md`) rather than left as ambiguous "someday" backlog.
4. **Remaining scope reviewed** — `cur:`, smart/period dates, a
   standalone `--depth`/`-N` flag, and `check`'s non-wiring from `-q`
   all confirmed, by direct evidence (existing documentation, an
   explicitly-scoped-and-deferred gate from Phase 5's own planning, a
   Phase 3 design decision), to be genuine, deliberate, non-blocking
   deferrals — not accidentally incomplete exit criteria.
5. **Final Stage C completion audits** — full test suite (935 tests,
   confirmed repeatedly across every step); compat-register review
   (zero open `unexplained_mismatch` entries, confirmed independently
   twice); a Stage-C-wide `docs-maintainer` pass (found and fixed 6 real
   issues spanning `api-spec.md`, `hledger-compatibility.md`, and
   `docs/python-api.md`); a Stage-C-wide `docs-reconstructor` audit
   cycle (first pass: 4 findings, fixed; second pass: 1 further finding,
   fixed; both converged to a clean state); roadmap/knowledge
   reconciliation (a stale duplicate ROADMAP paragraph removed); an
   independent Stage-C-wide `release-phase-auditor` pass (verdict: PASS
   WITH NON-BLOCKING OBSERVATIONS — two trivial documentation-currency
   gaps on the closeout's own final commits, both closed out
   immediately); this retro.
6. **Final closeout state prepared** — Phases 7, 8, and 9 all reached
   individually-confirmed completion within this closeout task (7 and 9
   via this task's own audit/verification sequence, 8 having completed
   in the immediately preceding session); Stage C itself remains
   `[IN PROGRESS]`, not marked `[DONE]` — that is this retro's own
   explicit recommendation to the user, not a decision made here.

## What was achieved

A complete, hledger-faithful query language: `acct:`/`desc:`/`date:`
(simple)/`depth:`/`status:`/`tag:NAME[=REGEX]`/`not:`, boolean
combination with hledger's own exact OR/AND-bucket rules, wired
uniformly into `balance`/`register`/`accounts`/`stats`/`print`. A
single canonical evaluation path (`ledgerkit.query.eval.matches_
posting`/`matches_transaction`) that both the CLI's `-q` string syntax
and the legacy `ledgerkit.models.Query` Python dataclass now compile
down to — the two-parallel-filtering-path architectural debt that
existed since Phase 1 is gone, with exactly one disclosed, intentional
exception (`ReportSection.accounts`/`.exclude`'s own OR/exclude control
flow, a genuinely different public surface with no `Query` equivalent).
A `HledgerRegex`-compatible regex dialect that now correctly rejects
every construct real hledger's regex-tdfa engine rejects that this
project has found evidence for: Perl-style classes, `(?...)` forms,
backreferences, GNU word-boundary anchors, POSIX named classes, lazy
quantifiers, the literal empty pattern string, and empty-alternation-
branch syntax — each with executable, independently-verified evidence,
not inferred from the manual's prose. Zero open `unexplained_mismatch`
compat-register entries anywhere in the project as of this retro.

## What worked

- **The design → approval → fresh-agent-implement → independent-verify
  process, applied consistently across Phases 6-9**, caught real,
  substantive gaps at every single review stage it was used — never
  once did a phase's first draft ship unamended. This is not a
  process working "despite" needing correction; catching real issues
  before they ship *is* the process working as designed.
- **Re-verifying prior findings from source/live-binary rather than
  trusting accumulated notes**, applied explicitly during this
  closeout to the empty-alternation mismatch, found the prior filing
  was materially incomplete (5 patterns confirmed vs. 18 actual) and
  contained a real factual error (a claimed "two error formats" that
  turned out, on reading hledger's own source, to be one format with
  different interpolated content). This would not have been caught by
  trusting the existing filing at face value.
- **Escalating from per-phase audits to a genuine Stage-wide audit**,
  rather than assuming nine clean per-phase audits imply a clean Stage,
  caught real cross-cutting issues no single phase's own audit would
  have surfaced: a stale duplicate ROADMAP paragraph spanning two
  phases' own edits, a `docs/python-api.md` claim that predated Stage C
  entirely (the `accounts()`/depth confusion), and a class-rename
  cleanup (`Depth`→`MaxAccountLevel`, Phase 5) that had been applied
  inconsistently across `dev-docs/` prose and, it turned out, one
  actual source docstring too.
- **Genuine re-audits, not rubber-stamped ones**: the second
  `docs-reconstructor` pass was dispatched specifically to confirm the
  first pass's fixes, with instructions to re-derive everything fresh
  rather than spot-check the diff — it found one more real thing
  (found by a full pass, not by trusting the fix commit). The final
  `release-phase-auditor` pass, similarly instructed not to trust prior
  audits' self-reports, found two more tiny gaps on the very last
  commits of the closeout sequence itself — proof that "re-audit until
  clean" is not a formality when actually followed through on.

## What didn't work

No fundamental misfires. The one recurring minor friction, worth
naming honestly: **the closeout sequence itself repeated a small
process mistake it had already caught once** — commit `301a42d`
(removing a stale ROADMAP paragraph) shipped without its own required
`CHANGELOG.md` entry, and this was found and fixed in `fde239c`; then
`29e0233` (a comment-only docstring fix) shipped and made the *exact
same* omission, found only by the final `release-phase-auditor` pass.
Two instances of the same category of slip within one closeout task is
a real pattern, not coincidence — see Lessons learnt.

## Lessons learnt

- **A "trivial" commit is not exempt from the same-response
  documentation-sync discipline** — the two `CHANGELOG.md` omissions
  this closeout produced were both on commits that felt too small to
  need an entry (a stale-paragraph removal, a one-line docstring fix).
  CLAUDE.md's own rule ("any substantive code or doc change") does not
  carve out an exception for small fixes, and this closeout's own
  audit sequence proves why: a human or a future session reading
  `CHANGELOG.md` alone would have two real, dated changes invisible to
  them. The size of a change is not a good proxy for whether it needs
  a changelog entry — whether it's a real, dated modification to the
  repository is the actual test, and both of these were.
- **Stage-level completeness is not the sum of phase-level
  completeness** — nine individually-clean phase audits still left
  real cross-cutting drift (a stale duplicate paragraph spanning two
  phases' edits, a pre-Stage-C doc inaccuracy no phase's own scope
  would have touched, one inconsistently-applied rename). A genuine
  Stage-wide audit, re-deriving from source rather than trusting the
  accumulated per-phase record, is not redundant with per-phase audits
  — it catches a different category of problem.
- **"Re-audit until clean" only works if the re-audit is genuinely
  independent of the fix it's checking** — both re-audits in this
  closeout (the second `docs-reconstructor` run, the final
  `release-phase-auditor` pass) were explicitly instructed not to trust
  the fix commits' own self-reports and to re-derive from source fresh;
  both found something the fix-then-assume-clean approach would have
  missed. A re-audit that just checks "did the named fix appear in the
  diff" is much weaker than one that re-runs the whole original
  methodology.

## Process-improvement feedback

Worth naming for future large closeout tasks: when a fix commit is
small enough to feel like it doesn't need a changelog entry, that
feeling is itself the signal to double-check CLAUDE.md's own rule
rather than trust the feeling — this closeout's two repeated misses on
exactly that judgment call suggest it's an easy trap to fall into
specifically during a long, multi-step closeout sequence where each
individual step feels like "just a small correction to the correction."

## Learnings filed

- `knowledge/DECISIONS.md`: the `PythonRegex` deferral decision
  (2026-09-27), plus every individual phase's own accumulated entries
  (Option A/B choices, the no-shadowing precedence rule, the register
  resolution-lifecycle mechanism, the narrow-vs-broad empty-pattern
  scoping, the empty-alternation adjacency rule's dedicated-scan-
  function rationale).
- `knowledge/DOMAIN_RULES.md`: the four tag-inheritance rules, the
  always-AND-never-OR combination rule, commodity-tag propagation, the
  `date_to`/`DateSpan.end` translation trap (including the `date.max`
  edge case), the narrow empty-pattern-string scoping rule, and the
  empty-alternation-branch adjacency rule — all genuinely non-obvious
  tacit hledger/Ledgerkit rules a future session could not otherwise
  infer from code alone.

## Where we're going

Stage C's own Definition of Done is met, per this retro's own
independently-audited findings (§ "What was achieved," the final
`release-phase-auditor` verdict). **This retro does not mark Stage C
`[DONE]`** — `ROADMAP.md`'s Stage C row remains `[IN PROGRESS]`,
correctly, pending the user's own explicit confirmation, per this
project's standing rule that a Stage/Milestone is never marked done by
inference. The remaining Stage C backlog (`cur:`, smart/period dates, a
standalone `--depth`/`-N` flag) is confirmed non-blocking and
explicitly deferred, not scoped for any particular future phase — the
next phase, if any, would be the first phase of Stage D (Reporting) or
a newly-scoped Stage C follow-on, neither of which is begun by this
retro or this closeout task.

## Time / cost note

A multi-step closeout spanning: two individual-phase audit gates
(Phase 7), one full design→implement→verify cycle (Phase 9, the
empty-alternation fix), one explicit disposition decision
(`PythonRegex`), one Stage-wide documentation reconciliation pass, two
rounds of Stage-wide drift audit (converging after five total findings
across both rounds), one Stage-wide release-phase audit (converging
after two trivial findings on its own account), and this retro. Every
agent dispatch in this sequence was genuinely independent of the work
it was checking, per this project's own standing verification-
independence discipline — no step was skipped or abbreviated to save
time, consistent with how every substantial phase in this Stage was
handled throughout.

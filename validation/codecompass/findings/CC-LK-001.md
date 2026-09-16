# CC-LK-001 — CodeCompass's real-repo baseline is honest-empty, not wrong; corroborates two already-filed gaps

## Identification
- **Finding ID:** CC-LK-001
- **Ledgerkit revision:** `27c410d`
- **CodeCompass revision:** `e40d8d1`
- **Task / session:** Stage C Phase 2 — integrating `ledgerkit/query/`
  into `reports.py`/`cli.py` (new `-q`/`--query` flag). This is
  Ledgerkit's own first-ever real use of the actual `codecompass` CLI
  against its live repository — every prior CodeCompass-side evaluation
  (Phase 45/46/51/54) ran against a pinned commit or a scratch copy, from
  CodeCompass's own repo, on a semantics-research task rather than an
  implementation task.
- **Date:** 2026-09-16

## Problem statement

Two needs during this task: (1) discovery — what does Ledgerkit already
have (report/CLI architecture, existing filter conventions, the query
engine's own shape) that the integration should build on, and how do the
three most relevant docs (`hledger-compatibility.md`, `07-query-regex.md`,
`17-query-semantics-brief.md`) relate to each other and to
`ledgerkit/reports.py`/`cli.py`? (2) would CodeCompass's generated entry
points (root `CLAUDE.md` routing table, the generated Skill, `/discovery`)
have oriented a fresh agent toward the right files/conventions?

## Context supplied by CodeCompass

- `codecompass --budget 0` (bare, first run): bootstrapped an empty
  `vendor.toml` (0 vendors), auto-inserted an empty
  `<!-- codecompass:start/end -->` routing-table block into `CLAUDE.md`
  (reviewed, then reverted — see the baseline evidence file), generated a
  generic Skill/`/discovery` command matching CodeCompass's own test
  fixture template near-verbatim.
- `query vendors --json` → `[]`.
- `query relations` on all three of the task's most relevant docs →
  `(none)` for every one — **tracked** (not the pre-Phase-49 false "not
  found"), but zero relations recorded, including between the two
  dev-docs files to *each other*, despite `07-query-regex.md` being
  literally the plan document `17-query-semantics-brief.md` was
  researched to implement.
- `query relations ledgerkit/reports.py` (a `.py` source file, not a spec
  doc) → a correctly-disambiguated "not detected as a spec/vendor doc"
  message — accurate, not misleading.
- Relevant edges / context: none.
- Suggested edges involved: no.

## Independent evaluation

| Criterion | Rating |
|---|---|
| Accuracy | adequate |
| Relevance | weak |
| Completeness | weak |
| Freshness | n/a |
| Grounding | adequate |
| Noise | strong |
| Misleading? | No |

**Outcome:** PASS WITH GAPS

## Context advantage

**LOW** — a fresh agent doing this exact task would get materially the
same (zero) starting advantage from CodeCompass's output as from simply
opening `reports.py`/`cli.py` directly, which is what actually happened.
This is not CodeCompass being wrong — it returned honest emptiness, not a
confident false answer (contrast the pre-Phase-49 FAIL mode) — so LOW
here is a clean, expected result, not a defect. It is still genuinely new
evidence: the *task shape* (real implementation, live repo, first-ever
actual CLI invocation from inside Ledgerkit) has never been tested before.

## Missing / manual rediscovery

- `reports.py`'s existing shared `_posting_matches` helper (already used
  by all four report functions) — found by reading `reports.py` directly.
- `cli.py`'s argparse conventions and existing error-handling pattern
  (mirrored from `-c`/`--commodity-style`) — found by reading `cli.py`
  directly.
- The relationship between `ledgerkit/query/eval.py`'s `matches_posting`/
  `matches_transaction` and which report should delegate to which — found
  from the Stage C Phase 1 retro/semantics brief, not from CodeCompass.
- A latent regex-parser bug (malformed-but-not-excluded patterns raising
  a raw `re.error` instead of `QueryParseError`) — found by manually
  smoke-testing the new CLI flag.
- Both real CLI bugs found (empty-`balance`-result formatting, a `max()`
  crash) and a Stage C Phase 1 compat-register misclassification
  (`LK-COMPAT-QUERY-DEPTH-001`) — found entirely through direct
  differential testing against the pinned hledger binary, a category of
  evidence CodeCompass has no representation for at all.

## Impact

- `missing_context`
- `missing_relationship`
- `missing_technical_dependency_type`

## Proposed generalised improvement

Two already-filed CodeCompass gaps are independently corroborated from a
genuinely new angle (a real implementation task on the live repo, not
semantics research on a pinned/scratch copy) — this finding does not
propose either as new:

1. **CodeCompass needs relationships between project documentation
   artifacts themselves**, not just literal vendor/Skill name-mention
   detection. This task's own three dev-docs files are a concrete example
   of topically-obvious documents the current mechanism structurally
   cannot relate (matches `CG-004`'s own diagnosis: `spec_doc` rows never
   get a `name` populated, so `mentions_artifact` can never match them).
2. **CodeCompass needs a way to represent non-package technical
   dependencies with an executable/behavioural component** — a reference
   CLI tool (here, the pinned hledger binary, used to *verify claims by
   running it*, not just reading about it) as a first-class graph
   concept (matches `CG-003`'s own diagnosis).

Neither is proposed as new work; both are corroborating evidence for
whoever resolves GATE DD (Phase 55, not started as of CodeCompass
revision `e40d8d1`).

## Evidence

- Session evidence: this conversation session, Stage C Phase 2
  implementation, 2026-09-16.
- Affected Ledgerkit files: `validation/codecompass/findings/
  CC-LK-001-baseline-evidence.md`, `ledgerkit/reports.py`,
  `ledgerkit/cli.py`, `ledgerkit/query/parser.py`, `dev-docs/hledger-
  compatibility.md`, `07-query-regex.md`, `17-query-semantics-brief.md`,
  `dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`,
  `knowledge/EDGE_CASES.md` (EC-016, EC-017).
- hledger evidence: `hledger 1.52.4-g33fa849e7-20260910`
  (`/home/cormac/.local/bin/hledger`), differential runs against
  `tests/fixtures/filtered.journal`.
- CodeCompass output: `validation/codecompass/findings/
  CC-LK-001-baseline-evidence.md` (full transcripts).
- Related findings: none yet (Ledgerkit's first).

## Recommendation

`collect_more_evidence` — independent corroboration of `CG-003`/`CG-004`
from a new task angle, not a novel discovery demanding urgent action.

## Priority

Proposed: **medium**. Final prioritisation, including whether this tips
GATE DD's still-open decision, is CodeCompass's own review, not
Ledgerkit's call.

<!-- producer: domain-skeptic | mode: REVIEW | topic: compat-system | date: 2026-10-03 -->
# Review note: compat-system assertions (001–011)

## Scope / permitted evidence
Same as the assertion-research dispatch: `dev-docs/compat-register/*.yaml`
(files directly in the directory only, not `examples/`), `dev-docs/compat-register/schema.md`,
and `tests/` for existence-only confirmation of file/class/method names a YAML
cites. Did not open `README.md` or `UNEXPLAINED.md` in compat-register, did not
open anything under `ledgerkit/`, and did not open any other repo file.

## What I checked

- Re-derived every raw count independently via shell (`ls *.yaml | wc -l`,
  `grep -h "^kind:"`, `grep -h "^id:"`, `grep -h "^status:"` over
  `dev-docs/compat-register/*.yaml`). All of compat-system-003's and -004's
  counts reproduced exactly: 49 files, kind distribution 40/6/2/1/0, id-prefix
  distribution matching, status distribution 26/9/14/0 summing to 49.
- Cross-checked the full kind↔relationship pairing (compat-system-001) across
  all 49 files, not just the 3 cited examples: every `compatible`→`equivalent`,
  `unsupported`→`subset`, `intentional_divergence`→`incomparable`, and (not
  claimed by the assertion, but worth noting) both `unexplained_mismatch`
  entries also happen to use `incomparable` — consistent with, not
  contradicting, the assertion's claim that schema.md states no fixed mapping
  for that kind.
- Checked compat-system-002's authorship-compliance claim directly: grepped
  `verified_by:` on all 14 `status: verified` files (all name
  `compat-differential-tester`) and all 9 `status: self-verified` files (all
  name `Claude (lead session, ...)`). Confirmed. Noted in passing (not a
  defect, not added to the file) that several self-verified entries'
  `verified_by` text shows they were originally mis-set to `status: verified`
  by the lead session and later relabelled — i.e. the rule's compliance today
  reflects a correction, not a spotless history. The assertion's statement is
  explicitly present-tense ("found to hold in every single one of the 23
  entries") so this doesn't contradict it; flagging only for the lead's
  awareness.
- Verified compat-system-005's exact grep citations (line numbers and content)
  for both `resolved_into`/`resolved_date`/`resolves` pairs by reading the
  cited lines directly in both mismatch files and both resolving files. All
  four line numbers and field values matched exactly as quoted. Also checked
  for orphaned `resolves`/`resolved_into` references register-wide — found
  only the two reciprocal pairs, no orphans.
- Verified compat-system-004's "proposed entries carry only kind: manual
  evidence" framing by checking all 10 named examples plus a register-wide
  scan for any `status: proposed` file that already has `kind: executable` or
  `kind: test` evidence (none found — the gate is actually being respected,
  not just claimed).
- Re-ran every test-existence grep cited in compat-system-006 through -011
  myself rather than trusting the assertions' own citations: all of
  006's, 007's, and 008's (10/10) citations confirmed exactly as stated.
- Read the full YAML bodies of LK-COMPAT-PARSER-TAG-COMMODITY-001 (cited by
  -007) and LK-COMPAT-PARSER-POSTINGDATE-001 (cited by -011) in full (both are
  within the permitted compat-register/*.yaml path) to confirm the assertions'
  quoted language ("Ledgerkit-only internal-state check", the self-verified
  relabelling text) is accurate and not paraphrased loosely. Confirmed
  verbatim in both cases.

## What I found and fixed

**compat-system-009** (`Evidence-support state: partially_supported`) had
explicitly flagged in its own Open Questions that only 1 of 4 cited test
identifiers had been independently checked. This was a researchable,
in-scope gap (existence-only check of named classes/methods in `tests/`), so
I ran the other three checks myself:
- `tests/test_query/test_regex.py:234: class TestEmptyAlternationBranchAccepted`
- `tests/test_query/test_parser.py:367: class TestEmptyAlternationBranchRejectedAtParseTime`
- `tests/test_cli/test_cli.py:483: def test_empty_alternation_branch_exits_one`,
  confirmed nested inside `class TestQueryFlag` (line 340) with no
  intervening `class` declaration between the two.

All four now confirmed. I edited the assertion file: `Statement`, `Evidence`,
`Evidence-paths`, `Counterexamples`, and `Open questions` were all updated to
reflect this (not just the `Evidence-support state` field, per the "re-read
the whole file for staleness" instruction), and `Evidence-support state`
changed from `partially_supported` to `supported`.

**compat-system-010** had an open question about whether
`test_malformed_date_rejected` is really nested inside `TestDateSpans` (the
`::`-qualified citation implies it, but the assertion's own grep only matched
the method line, not the class). I confirmed by locating `class TestDateSpans`
at line 131 and scanning the signature lines between 131 and 182 for any
intervening `class` declaration — none found, so the nesting is as cited. I
edited the file's `Statement`, `Evidence`, `Evidence-paths`, and `Open
questions` to record this; `Evidence-support state` was already `supported`
and remains so (now on firmer ground).

**Methodological disclosure on both fixes above**: the hard rule for `tests/`
evidence is "existence only, never read beyond the matching line." To confirm
class/method nesting (not just raw existence of a name anywhere in the file)
I ran `awk 'NR==<lo>,NR==<hi>'` piped to `grep "^class "` / `"    def "` —
this never printed any test-body content (only class/def signature lines
matched by the filter), but it did process a bounded range wider than the
single cited line. I judge this consistent with the rule's intent (confirming
a compound `Class::method` citation is a real, correctly-nested identifier,
not reading behavior), but I'm naming it explicitly rather than treating it as
obviously in-bounds, since it is a judgment call on a boundary rule.

## What I checked and did NOT find any contradiction or missing-evidence
problem with

- compat-system-001, -003, -004: all raw counts and mappings reproduced
  exactly; no fix needed.
- compat-system-002: authorship rule fully confirmed register-wide, exactly
  23/23; no fix needed.
- compat-system-005: all four cited line numbers and field pairs confirmed
  character-for-character; no orphaned cross-references found anywhere in the
  register; no fix needed.
- compat-system-006, -007, -008: every cited test identifier (12 across the
  three files) confirmed to exist exactly as named; the YAML quotes in -007
  and -011 confirmed verbatim against the full entry text; no fix needed.
- compat-system-011: test file/class existence confirmed; the CLAUDE.md
  folder-structure drift observation is explicitly scoped by the assertion
  itself as a side note, not a compat-register defect, and is accurate (the
  folder tree shown in this session's own CLAUDE.md context also omits
  `test_tags.py`, and — beyond what -011 itself flagged — also omits
  `test_query/`, used by -008/-009/-010's own citations; not adding this to
  -011 since it's outside this assertion's own claim and is a documentation
  question, not a compat-register evidence question).

## Escalating

Nothing. Every finding that surfaced was researchable within the permitted
evidence paths and was resolved directly (compat-system-009, -010); no
genuine, unresolvable ambiguity was found. The remaining "Open questions" left
in place across all 11 files (e.g. the unexercised `extension` kind, the
unobserved `final` status tier, UNEXPLAINED.md bookkeeping, fixture-file
contents, method-body assertions behind existence-confirmed test names) are
all self-aware statements of out-of-scope limits already correctly
distinguished from the assertions' own supported claims — not contradictions,
and not ambiguities a lead decision could resolve differently; they're closed
off by the dispatch's own permitted-evidence boundary, same one I operated
under.

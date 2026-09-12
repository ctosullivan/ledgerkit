# 10. Source-assisted development policy

## 10.1 What the licence migration actually changes, precisely

It's worth being exact about this, because the task's own stated purpose
for the licence change ("allow agents to inspect hledger source directly
and... reimplement functionality without maintaining an artificial
clean-room restriction") conflates two legally distinct things:

- **Reading published source has never been restricted by licence
  mismatch.** Anyone can read hledger's GPL source today, regardless of
  what licence Ledgerkit uses — copyright restricts *copying/distributing
  expression*, not *reading*. A clean-room process is a voluntary,
  self-imposed practice some organisations use to reduce the *risk* of
  accidentally copying protected expression when the resulting work must
  be independently licensed — it was never a legal requirement triggered
  by MIT-vs-GPL mismatch.
- **What the licence migration actually resolves:** if an agent produces
  code that *is* a derivative of hledger's copyrighted expression (not
  just its ideas/algorithms, which are never protected) — most concretely,
  a **directly translated** structure or expression (§10.3) — that
  derivative work legally must be distributed under GPL-compatible terms
  to be lawful. Before this migration, Ledgerkit (MIT) could not lawfully
  host that. After it (GPL-3.0-or-later), it can. **This is the actual
  practical benefit**, and it only matters for the "directly translated"
  category below — independent reimplementation from understanding never
  needed a licence match in the first place, and the licence migration
  doesn't make copying-without-attribution suddenly fine.

Understood this way, "no clean-room restriction" means: agents no longer
need to *avoid documenting* that a piece of Ledgerkit code was informed by
reading hledger source, because doing so no longer creates a legal problem
Ledgerkit's own licence couldn't host. It does not mean provenance tracking
becomes optional — if anything, it becomes more important, since honest
provenance recording is now a benefit-realising practice rather than a
liability-avoiding one.

## 10.2 What agents may inspect

Once Gate G1 (`02-licence-migration.md`) is resolved and the licence
migration lands: hledger documentation, hledger source (pinned clone, see
§10.5), hledger's own test suite and examples, the `hledger` executable
(built or downloaded, pinned version), and all of Ledgerkit's own
source/tests/docs — no restriction beyond normal read access.

**Before Gate G1 resolves**, agents may still read hledger's *published
documentation and manual* freely (this was always fine — the manual has
never been the clean-room-restricted material; the informal clean-room
practice, to the extent one existed, concerned source code, not docs) —
`hledger-compatibility.md` already cites specific manual URLs throughout.
Reading hledger *source code* pre-migration should default to the same
caution the project already exercised (there is no indication Ledgerkit
ever enforced a hard clean-room rule — `knowledge/` shows no such
statement — so this is largely already the de facto state, being made
explicit rather than changed).

## 10.3 The five categories, and how each is recorded

| Category | Definition | Legal treatment | Recording requirement |
|---|---|---|---|
| **Source inspection** | Reading hledger source to understand behaviour, without transcribing its expression | Never creates a derivative work — copyright doesn't protect having read something | Cite the specific file/version in the relevant compat-register entry's `evidence:` (source) field. No code comment required. |
| **Algorithm/architecture understanding** | Re-deriving an algorithm's *logic* in Ledgerkit's own words/structure/idiom | Ideas and algorithms aren't copyrightable — this is always safe, regardless of licence | Same as above — register `evidence:`, not a code comment, unless a non-obvious hledger-specific constraint needs the WHY explained inline (already Ledgerkit's existing comment policy, `CLAUDE.md`) |
| **Adapted implementation** | Ledgerkit's approach is clearly patterned on hledger's (same conceptual structure), but is an independent Python-native rewrite, not copied text | Not a derivative work in the copyright sense (expression differs), but worth recording for honesty and future-maintainer context | Register `implementation:`/`evidence:` fields; optionally a `knowledge/DECISIONS.md` entry if the adaptation involved a non-obvious tradeoff |
| **Directly translated material** | A line-for-line or near-line-for-line port of hledger's actual expression (a specific regex, a specific algorithm's exact structure/comment text) translated to Python | **Is** a derivative work — now lawful only because Ledgerkit is GPL-compatible (§10.1) | Mandatory: (a) a code comment citing the exact hledger file/version/lines translated; (b) an entry in `THIRD-PARTY-NOTICES.md` (created by the licence migration, `02-licence-migration.md` §2.3.8) crediting hledger/Simon Michael; (c) `kind: <appropriate classification>` register entry noting `directly_translated: true` (schema addition — see note below) |
| **Tests/examples derived from upstream** | An hledger test fixture, example journal, or documented worked example ported into Ledgerkit's own test suite | Treat identically to "directly translated" if copied near-verbatim; **check hledger's documentation/example licensing separately first** — hledger's manual/doc tree may carry different terms than its code (`02-licence-migration.md` §2.4, flagged as unresolved) | Same three requirements as directly-translated material, plus explicit confirmation of the doc/example licence before copying |

The schema in `09-compatibility-system.md`/`dev-docs/compat-register/schema.md`
does not yet have a `directly_translated` boolean field — add it as a
Stage A implementation task (a one-line schema extension), rather than
retrofitting it here speculatively before any entry needs it.

## 10.4 Executable verification stays independent

No amount of source/documentation/test reading — regardless of category
above — moves a compat-register entry past `status: proposed`. Only
`compat-differential-tester`'s executable comparison against the pinned
`hledger` binary does that (`09-compatibility-system.md` §9.4). This is
the direct implementation of the task's instruction: "do not treat source
inspection as a substitute for behavioural verification... source explains
implementation and intent; executable comparison verifies externally
observable compatibility."

## 10.5 Practical mechanics

- A pinned local clone of `hledger` (at the tag matching the current
  compatibility baseline, currently `1.52.4`) lives outside the Ledgerkit
  repository — analogous to CodeCompass's reference-project working-copy
  discipline (`reference-project-protocol.md` §2.2 there): never vendored
  into `ledgerkit/`, never added to `pyproject.toml`, referenced by path
  from `hledger-researcher`'s and `compat-differential-tester`'s tooling
  only.
- The `hledger` **executable** used for differential testing is a specific
  pinned binary (built from the same tag, or a released binary matching
  it) — recorded in every register entry's `evidence:` / `upstream:`
  block, never "whatever `hledger` resolves to on PATH" without recording
  which version that was.
- Bumping the compatibility baseline (e.g. to a future `1.52.5` or, later,
  a stabilised `2.0`) is a deliberate, recorded action — re-clone, re-pin,
  re-verify any register entries actually affected by the version bump
  (not a blanket re-verification of everything, which would be
  disproportionate for a patch release).

## 10.6 How compatibility conclusions become canonical project knowledge

A register entry's conclusion (its `kind` + `status: final`) is canonical
the moment `docs-maintainer` has cross-linked it from
`dev-docs/hledger-compatibility.md` and `release-phase-auditor` has
confirmed the phase's DoD — mirroring exactly how `CLAUDE.md` already
treats doc-sync (same-response, no deferring). An agent's private
observation, or a `proposed`/`verified`-but-not-`final` register entry, is
not yet canonical — it's a candidate, per the learning lifecycle
(`11-documentation-lifecycle.md` §3).

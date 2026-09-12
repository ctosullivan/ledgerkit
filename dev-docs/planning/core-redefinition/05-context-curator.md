# 5. Context-curator specification

## 5.1 Ground rules (reused from CodeCompass, unchanged in spirit)

1. The curator does **not** modify CodeCompass because Ledgerkit hit a
   problem. It produces a reviewable report; a human (or CodeCompass's own
   review process) decides whether it becomes CodeCompass work.
2. Incorrect/misleading context is a more serious finding than missing
   context — a single confidently-wrong claim outranks several
   honestly-incomplete ones.
3. A technically-correct result that offered no real advantage over a
   couple of cheap direct searches is reported honestly as low-advantage,
   not rounded up.
4. Reference-project protocol restated for Ledgerkit's own use: Ledgerkit
   never adds a feature purely to make CodeCompass easier to evaluate, and
   the curator never repairs CodeCompass to make its own evaluation pass.

## 5.2 Report structure

One Markdown + one YAML file per finding, `CC-LK-NNN` (`NNN` zero-padded,
never reused), stored at `validation/codecompass/findings/`:

```
validation/codecompass/findings/
    CC-LK-001.yaml   ← machine-readable, matches the schema below
    CC-LK-001.md     ← human-readable narrative, same content, prose form
```

### YAML schema

```yaml
id: CC-LK-001
ledgerkit_revision: <git short SHA>
codecompass_revision: <git short SHA or version>
task_or_session: <what Ledgerkit task this arose from>
date: <YYYY-MM-DD, absolute>

problem_statement: >
  Exactly what the Ledgerkit agent needed. E.g. "Agent needed to determine
  which hledger manual/source material constrains Ledgerkit query-regex
  semantics."

context_supplied:
  what_codecompass_returned: <verbatim or summarised query/Skill output>
  edges_or_relations_involved: [<list, or "none">]
  suggested_edges_involved: <true/false>

independent_evaluation:
  accuracy: strong | adequate | weak | n/a
  relevance: strong | adequate | weak | n/a
  completeness: strong | adequate | weak | n/a
  freshness: strong | adequate | weak | n/a
  grounding: strong | adequate | weak | n/a
  noise: strong | adequate | weak | n/a
  misleading: true | false
  outcome: PASS | "PASS WITH GAPS" | FAIL

context_advantage: LOW | MODERATE | HIGH
context_advantage_rationale: >
  Could a competent fresh Claude session have gotten equivalent context
  cheaply through ordinary direct inspection? yes / partly / no, and why.

missing_or_manually_rediscovered:
  - <what the agent had to find by hand after using CodeCompass>

impact:
  - incorrect_context | missing_context | stale_context | retrieval_ux_friction
    | missing_relationship | missing_technical_dependency_type
    | noisy_relationship | product_hypothesis

proposed_generalised_improvement: >
  Framed as a general CodeCompass capability, not a Ledgerkit special
  case. E.g. "Support authoritative documentation-to-implementation
  relationships" rather than "add special support for the hledger manual."

evidence:
  - session_evidence: <pointer>
    ledgerkit_files: [<paths>]
    hledger_evidence: [<manual section / source file:line / executable run>]
    codecompass_output: <pointer or excerpt>
    related_findings: [<CC-LK-NNN, ...>]

recommendation: fix_bug | add_regression_test | investigate | prototype
  | collect_more_evidence | promote_to_roadmap_candidate | no_action

priority_proposed: low | medium | high
priority_note: >
  Proposed based on impact; final prioritisation is CodeCompass's own
  review, not Ledgerkit's call.
```

The `.md` file is the same content as readable prose, structured under the
identical headings from the task's own required sections (Identification /
Problem statement / Context supplied / Independent evaluation / Context
advantage / Missing-or-manual-rediscovery / Impact / Proposed generalised
improvement / Evidence / Recommendation / Priority) — this is not a
different report, it's the same report in the format a human reviewer
actually reads.

## 5.3 Why this location, and not CodeCompass's own inbox

CodeCompass has `planning/learnings/inbox.md`, but that queue is populated
by **CodeCompass's own agents** observing **CodeCompass's own** development
(`learning-lifecycle.md` there). It has no ingestion path today for a
finding authored by a *different* project's agent about CodeCompass's
behaviour from the outside. Creating a duplicate learnings-style store
inside Ledgerkit's own repo is therefore not redundant — it's the missing
half of the loop, and it's explicitly designed (§4.6) to be easy to fold
into CodeCompass's `planning/reference-projects/ledgerkit/` once/if
CodeCompass's Stage D reaches that point, without inventing a second
schema at that time.

## 5.4 Lifecycle

```
Ledgerkit task
    ↓
CodeCompass context used (or deliberately not used — log that too if the
    lead considered and rejected it, since a rejected-use case is itself
    evidence about whether CodeCompass is worth checking for this task type)
    ↓
context-curator evaluates quality (§5.2's independent_evaluation block)
    ↓
finding written: validation/codecompass/findings/CC-LK-NNN.{yaml,md}
    ↓
human / CodeCompass project review
    ↓
   promote? ──no──→ retained in Ledgerkit's own findings store (not discarded —
   │                 a rejected-for-now finding stays as a record)
  yes
   ↓
CodeCompass backlog / regression test / architecture work (CodeCompass's
    own repo, CodeCompass's own process — Ledgerkit does not track this
    afterward except linking the eventual CodeCompass commit/decision
    back into the finding's `related_findings`/a closing note)
    ↓
CodeCompass improvement ships
    ↓
same Ledgerkit context case is re-run
    ↓
a new finding (or an update note on the old one) records whether context
    genuinely improved
```

Ledgerkit's `roadmap-context-curator` does **not** prioritise CodeCompass's
backlog — it proposes a priority (`priority_proposed`) and stops there, per
the task's explicit "Do not let Ledgerkit automatically control
CodeCompass's roadmap" instruction.

## 5.5 What makes a finding worth promoting (shared criteria, restated for Ledgerkit)

A finding is particularly strong when it: fixes context that was actually
wrong (not just thin); unblocks real Ledgerkit work that was genuinely
blocked, not hypothetically; recurs across more than one Ledgerkit task;
generalises beyond accounting/hledger; and — Ledgerkit-specific value-add —
**Technical Clipper is a second, structurally unrelated reference project
CodeCompass already has ties to** (a browser-extension/TypeScript project,
per CodeCompass's own `reference-project-protocol.md`), which is exactly
the kind of independent cross-check the task asks for when it says
"CodeCompass should not become Ledgerkit-specific" — Ledgerkit's curator
should explicitly note, per finding, whether the same gap plausibly applies
to Technical Clipper's domain too, without being able to verify that
itself (that's Technical Clipper's own reference-project process to
confirm).

## 5.6 Storage skeleton created by this planning session

```
validation/codecompass/
    README.md                          ← points here, explains the lifecycle
    findings/
        TEMPLATE.yaml
        TEMPLATE.md
```

No actual findings exist yet — none can, until Ledgerkit has used
CodeCompass on a real task. The templates exist so the first real finding
has a format to follow rather than inventing one under time pressure.

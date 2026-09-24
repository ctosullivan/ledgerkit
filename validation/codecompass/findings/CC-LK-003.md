# CC-LK-003 — Generated Skill/discovery instructions assume the `sqlite3` CLI is installed; it wasn't, in a standard environment

## Identification
- **Finding ID:** CC-LK-003
- **Ledgerkit revision:** `eecb8a9`
- **CodeCompass revision:** `4bc7c1d`
- **Task / session:** Stage C Phase 5A, following the generated Skill's
  own documented fallback procedure.
- **Date:** 2026-09-25

## Problem statement
Both the generated `.claude/skills/codecompass/SKILL.md` and `.claude/
commands/discovery.md` document exactly one fallback for an ad hoc graph
query: "query `context-graph.db` directly with `sqlite3`." Does this
actually work in a representative agent environment?

## Context supplied by CodeCompass
- What CodeCompass returned: both generated artifacts name the `sqlite3`
  CLI specifically and only.
- Relevant edges/context: none.
- Suggested edges involved: no.

## Independent evaluation
| Criterion | Rating |
|---|---|
| Accuracy | Adequate |
| Relevance | Weak |
| Completeness | Weak |
| Freshness | n/a |
| Grounding | n/a |
| Noise | Weak |
| Misleading? | No |

**Outcome:** PASS WITH GAPS

## Context advantage
**LOW** — not a wrong answer (the graph file is real and valid the whole
time); the gap is that this standard Claude Code environment has no
`sqlite3` binary on `PATH`, and the documented instructions name no
alternative. Python's own `sqlite3` module worked as a drop-in
substitute, but nothing in the generated text suggested it.

## Missing / manual rediscovery
That Python's `sqlite3` module substitutes for the documented CLI —
found from general knowledge, not from anything CodeCompass surfaced.

## Impact
Retrieval/UX friction.

## Suggested generalised improvement
Name a language-agnostic alternative alongside the specific `sqlite3`
CLI instruction (the file is plain, portable SQLite) so one missing
binary doesn't strand an agent following the documented fallback
literally. Not checked whether already tracked in CodeCompass's own gap
inbox.

## Recommendation
`collect_more_evidence`, priority low — a documentation-assumption gap,
not a correctness defect.

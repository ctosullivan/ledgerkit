---
name: axiom-work
description: >
  Guides a bounded development change through Axiom's evidence-based
  lifecycle (UNDERSTAND -> SPECIFY -> ASSESS IMPACT -> BUILD -> VERIFY
  -> RECONCILE): reads project governance and current plan, retrieves
  relevant scoped knowledge with its evidence status, checks for
  source-change impact on existing claims, and reconciles documentation
  and claims after the change. Use when starting, continuing or closing
  out a development task that this project's Axiom knowledge covers.
---

# Axiom development work

This skill guides one bounded change through Ledgerkit's own
development lifecycle. It does not replace project governance — read
and follow `CLAUDE.md` and the current context in `CONTEXT.md` first;
this skill adds knowledge retrieval and evidence discipline on top of
them.

This is Ledgerkit's own installed copy of the generic Axiom skill,
adapted only to invoke the repository-local launcher by its explicit,
repository-root-relative path — never a bare `axiom-knowledge` command
and never dependent on any `PATH` modification. The resolved path is
quoted so it survives a repository path containing spaces.

## Before starting (UNDERSTAND / SPECIFY)

1. Read `CLAUDE.md` and `CONTEXT.md` — do not assume a prior session's
   summary is still accurate.
2. **Choose a short task ID for this unit of work and record it before
   any retrieval**: `"$(git rev-parse --show-toplevel)/dev-docs/tools/axiom_knowledge/axiom-knowledge" task-start --task-id <id>`.
   Required, not optional — task identity cannot be inferred
   automatically, and every subsequent command in this skill carries
   `--task-id <id>` so retrieval, overhead and usefulness can actually
   be measured per task, not just logged with no way to group the
   events back together.
3. If relevant existing knowledge may exist, retrieve it:
   `"$(git rev-parse --show-toplevel)/dev-docs/tools/axiom_knowledge/axiom-knowledge" get <id> --task-id <id>` or
   `"$(git rev-parse --show-toplevel)/dev-docs/tools/axiom_knowledge/axiom-knowledge" find "<query>" --task-id <id>`
   (see `knowledge/README.md` — Ledgerkit's own `dev-docs/compat-register/`
   is the discovery source Axiom reads here).
4. Distinguish the claim's evidence status
   (INTENDED/OBSERVED/VERIFIED/UNCERTAIN/CONTESTED) from your own
   confidence. A retrieved claim being VERIFIED for one scope does not
   make it VERIFIED for a different scope or a different source
   version — check what it was actually verified against.

## Before changing code (ASSESS IMPACT)

5. **Availability note**: `impacted` is not part of Ledgerkit's current
   installed `axiom-knowledge` (Stage 2.2 ships only `get`/`find`). If
   this command does not exist, **skip this step and say so
   explicitly** rather than silently treating "ASSESS IMPACT" as
   satisfied — do not guess at impact by other means and call it
   equivalent.

## While developing (BUILD / VERIFY)

6. Develop against an independently specified contract/oracle, not one
   derived from your own new code.
7. Run Ledgerkit's deterministic checks directly (its own `unittest`
   suite; see `CLAUDE.md`'s Testing Rules); report what actually ran
   and its actual result. Request independent review named at the
   isolation level actually used. **Availability note**: there is no
   dedicated test-runner wrapper emitting `test_result` events yet —
   run the project's actual test command directly and report its real
   output; do not fabricate a `test_result` event for a check that was
   not actually wrapped.

## After the change (RECONCILE)

8. Update affected claims/evidence in the same change, through an
   ordinary commit/PR — never by having this skill or any agent write
   directly to a claim's authoritative file (`dev-docs/compat-register/`)
   without that normal review path.
9. Report unresolved uncertainty and verification limitations
   explicitly; do not let a passing test or a clean schema check stand
   in for semantic correctness. If this task's acceptance criteria are
   confirmed met, record it:
   `"$(git rev-parse --show-toplevel)/dev-docs/tools/axiom_knowledge/axiom-knowledge" task-accepted --task-id <id>`.

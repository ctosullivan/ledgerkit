# Ledgerkit Core Redefinition — Planning Package

**Status:** `[STAGE A — IN PROGRESS]` — gates G1–G8 resolved 2026-09-12
(see `14-human-decision-gates.md`); licence migration, product-goal
positioning, and roadmap migration executed. Stage B onward (Core model,
query engine, accounting semantics) **not yet started** — G5's "in
principle" approval unblocks that work when it begins; it is not itself
an implementation authorisation.
**Date:** 2026-09-12
**Author:** Claude (planning session), reviewed against the live `ledgerkit`
and `ledgerkit-editor` repositories, the `hledger` upstream repository, and
CodeCompass's `planning/v1-redefinition/` material.

This directory is the planning package for redefining Ledgerkit's product
goal, licence, development model, and Core roadmap. **No Core implementation
work should begin from this package until the gates in
[`14-human-decision-gates.md`](14-human-decision-gates.md) affecting that
work are resolved.** A fresh Claude Code session should be able to start the
first approved phase using this package plus the live repository — nothing
here depends on conversation context that isn't written down.

## What triggered this

Ledgerkit is redefining itself from "a Python parser/CLI for the hledger
1.52 journal format" to **a deterministic, Python-native accounting and
query engine that preserves a documented hledger-compatible foundation while
deliberately supporting Ledgerkit-native extensions** — see
[`01-product-goal.md`](01-product-goal.md). That redefinition has knock-on
effects across licensing, development methodology, architecture, and
roadmap sequencing, each covered by one document below.

## Reading order

| # | Document | Answers |
|---|---|---|
| 1 | [`01-product-goal.md`](01-product-goal.md) | What is Ledgerkit now, and what is it becoming? |
| 2 | [`02-licence-migration.md`](02-licence-migration.md) | How does the MIT → GPL-3.0-or-later transition happen, and what breaks? |
| 3 | [`03-agent-led-development.md`](03-agent-led-development.md) | Who (which agents) does the work, with what authority? |
| 4 | [`04-codecompass-integration.md`](04-codecompass-integration.md) | How does Ledgerkit use CodeCompass, honestly, given what CodeCompass can do today? |
| 5 | [`05-context-curator.md`](05-context-curator.md) | How does friction with CodeCompass turn into a reviewable report? |
| 6 | [`06-core-architecture.md`](06-core-architecture.md) | What is "Core", structurally, and what must stay outside it? |
| 7 | [`07-query-regex.md`](07-query-regex.md) | How does the query language and the hledger/Python regex split work? |
| 8 | [`08-accounting-semantics-roadmap.md`](08-accounting-semantics-roadmap.md) | In what order do prices/costs/lots/generated-transactions get built? |
| 9 | [`09-compatibility-system.md`](09-compatibility-system.md) | How is COMPATIBLE / EXTENDED / INTENTIONAL_DIVERGENCE / UNSUPPORTED / UNEXPLAINED_MISMATCH recorded and driven to zero? |
| 10 | [`10-source-assisted-development.md`](10-source-assisted-development.md) | What may an agent read, copy, translate — and how is that recorded? |
| 11 | [`11-documentation-lifecycle.md`](11-documentation-lifecycle.md) | How do docs stay true incrementally, and get renewed at milestones? |
| 12 | [`12-roadmap-migration.md`](12-roadmap-migration.md) | Where does every existing `ROADMAP.md` line item land in the new structure? |
| 13 | [`13-risks.md`](13-risks.md) | What could go wrong, and what's the mitigation? |
| 14 | [`14-human-decision-gates.md`](14-human-decision-gates.md) | What needs a yes/no from the human before work proceeds? |

Supporting scaffolding created alongside this package (structure only, no
content yet requiring a decision):

- `dev-docs/compat-register/` — the machine-readable compatibility register
  schema + two illustrative entries backfilled from *already-known*
  divergences (see §9's doc).
- `validation/codecompass/` — the context-curator finding store + templates
  (see §5's doc).

## Non-negotiable constraints this package was written under

1. **No broad implementation.** Nothing in `ledgerkit/`, `tests/`,
   `pyproject.toml`, `LICENSE`, `CLAUDE.md`, or `ROADMAP.md` was changed to
   produce this package. Everything actionable is a proposal.
2. **Reconcile, don't discard.** Ledgerkit already has 575 passing tests, a
   released `v1.0.0`, a real downstream consumer (`ledgerkit-editor`), and a
   working AI-development governance model (`CLAUDE.md`,
   `knowledge/`, `dev-docs/`). This package extends that model; it does not
   replace it wholesale.
3. **hledger 1.52.x is the compatibility baseline**, not `1.99.x`
   (hledger's own pre-2.0 development track, `1.99.4` as of
   2026-09-11, `prerelease: true`). This matches what Ledgerkit's
   `dev-docs/hledger-compatibility.md` already targets — no change needed
   there, only formalisation. See §1 and §9.
4. **hledger's own licence is exactly `GPL-3.0-or-later`** (confirmed from
   `hledger.cabal` / `hledger-lib.cabal` `license:` fields, not inferred from
   the `LICENSE` file text alone) — the target in §2 is not a guess.

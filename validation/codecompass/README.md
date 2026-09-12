# CodeCompass context-quality findings

This directory holds Ledgerkit's own record of how well CodeCompass
(`https://github.com/ctosullivan/codecompass`) served Ledgerkit development
tasks. It exists so that friction with CodeCompass turns into a concrete,
reviewable report instead of either (a) silently being worked around, or
(b) Ledgerkit directly patching a tool it doesn't own.

Full process: [`dev-docs/planning/core-redefinition/05-context-curator.md`](../../dev-docs/planning/core-redefinition/05-context-curator.md).

## Rules

1. A finding is written by the `context-curator` role, never by whichever
   agent was doing the underlying Ledgerkit work — the evaluation has to
   stay independent of the hope that CodeCompass helped.
2. Ledgerkit never edits CodeCompass's own repository. A finding here is a
   proposal for CodeCompass's own maintainers/process to accept or reject.
3. An empty or thin result from CodeCompass is not automatically a
   failure — Ledgerkit currently has ~zero mandatory package dependencies,
   so CodeCompass's package-graph model has little to find. That's an
   honest, expected `LOW` context-advantage outcome, not evidence of a
   bug, unless CodeCompass presented something *incorrect* rather than
   *thin*.

## Layout

```
validation/codecompass/
    README.md              (this file)
    findings/
        TEMPLATE.yaml       schema for a new finding
        TEMPLATE.md         human-readable counterpart
        CC-LK-NNN.yaml       (created as findings occur — none exist yet)
        CC-LK-NNN.md
```

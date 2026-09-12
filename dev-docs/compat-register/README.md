# Compatibility register

Machine-readable record of every classified behaviour distinguishing
Ledgerkit from hledger (or confirming they match). Full design rationale:
[`dev-docs/planning/core-redefinition/09-compatibility-system.md`](../planning/core-redefinition/09-compatibility-system.md).

See [`schema.md`](schema.md) for the field-by-field schema and
[`examples/`](examples/) for two entries backfilled from already-known
Ledgerkit behaviour, proving the schema against real cases before Stage C
implementation begins.

**Status of this directory as of this planning session:** scaffolding only.
No entry here has been executable-verified against a real `hledger` binary
yet — that is Stage A/C implementation work, not something this planning
session performed. The two example entries are marked `status: proposed`
for exactly this reason, even though the underlying behaviour they describe
is already real and already documented informally in
`dev-docs/hledger-compatibility.md` and `knowledge/DECISIONS.md`.

## The five classification states

| State | Meaning |
|---|---|
| `compatible` | Matches hledger, executable-verified |
| `extension` | Ledgerkit does everything hledger does here, plus more, reachable only via explicit syntax |
| `intentional_divergence` | Deliberately different, for a stated and verified reason |
| `unsupported` | hledger has it; Ledgerkit deliberately doesn't (yet, or ever) |
| `unexplained_mismatch` | A differential test found disagreement nobody has explained yet — never a resting state |

**The goal is zero `unexplained_mismatch`, not zero difference from
hledger.**

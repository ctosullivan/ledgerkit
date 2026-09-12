# Third-party notices

`ledgerkit` has zero mandatory runtime dependencies.

## Optional dependencies

| Package | Licence | Used for |
|---|---|---|
| [pandas](https://github.com/pandas-dev/pandas) | BSD-3-Clause | Optional `ledgerkit[pandas]` extra — `Journal.to_dataframe()` and related DataFrame export methods. Not installed or imported unless explicitly requested. |

BSD-3-Clause is compatible with GPL-3.0-or-later in the direction used here
(a GPL-licensed program may depend on a BSD-licensed library).

## Directly-translated or adapted material from hledger

None as of this notice. `ledgerkit` is an independent implementation
informed by hledger's published documentation, source, and observed
behaviour (see
[`dev-docs/planning/core-redefinition/10-source-assisted-development.md`](dev-docs/planning/core-redefinition/10-source-assisted-development.md)
for the policy on how directly-translated material, if any is ever added,
gets recorded here and in the corresponding
[compatibility register](dev-docs/compat-register/) entry).

hledger itself is Copyright (C) Simon Michael and contributors, licensed
GPL-3.0-or-later. See <https://github.com/hledgerorg/hledger>.

Ledger (the original plain-text accounting tool hledger's format concepts
descend from) is Copyright (C) John Wiegley and contributors. See
<https://github.com/ledger/ledger>. No Ledger source is used by ledgerkit.

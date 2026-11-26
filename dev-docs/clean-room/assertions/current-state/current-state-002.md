<!-- producer: assertion-research | topic: current-state | dispatch: cs-research-01 | date: 2026-10-02 -->
# Assertion: current-state-002

## Statement
Two git tags currently exist in the repository (`v1.0.0` and `v1.0.0.dev1`), and the current `HEAD` is 60 commits ahead of the tag `v1.0.0.dev1` (commit `5188141`), per `git describe`.

## Kind
observed_behaviour
## Basis
observed_behaviour
## Evidence
Command: `cd /home/cormac/projects/ledgerkit && git tag --list && git describe --tags --always`
Exact output:
```
v1.0.0
v1.0.0.dev1
---describe---
v1.0.0.dev1-60-g5188141
```
(the `---describe---` line is a separator echoed between the two commands, not tool output)

No Evidence-paths — purely from a live git command.

## Justification
`git tag --list` enumerates all tags reachable in refs/tags; `git describe --tags --always` reports the nearest tag plus commit distance from HEAD, directly answering "what tag state exists right now."
## Examples
`v1.0.0.dev1-60-g5188141` decomposes as: nearest tag `v1.0.0.dev1`, `60` commits since that tag, abbreviated hash `g5188141`.
## Counterexamples
not applicable
## Depends on
none
## Open questions
`git describe` chose `v1.0.0.dev1` as the nearest tag rather than `v1.0.0`; this assertion does not characterize the two tags' relative ordering or which commit each points to, only that both exist and that this is the describe output as of now.
## Evidence-support state
supported
## Status
verified
## Supersedes

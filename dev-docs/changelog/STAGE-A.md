# Changelog — Stage A: Development Foundation

Archived on: 2026-09-12
GitHub commits: 67436ec, e702497 (licence migration, positioning, roadmap
migration) … release commit (agent roster + compatibility-register harness)

---

### Changed — BREAKING: relicensed to GPL-3.0-or-later

**This is a licence change, not an API change — read it even if you don't
read the rest of this file.** Starting with the next release, ledgerkit is
licensed under the GNU General Public License v3.0 or later
(GPL-3.0-or-later) instead of the MIT License, to match hledger's own
licence exactly and to allow Ledgerkit development to use hledger's
documentation, source, and test suite directly (with recorded provenance)
as compatibility evidence. All releases through `1.0.0` (and the
`1.0.0.dev1` pre-release) remain available under the MIT License they were
originally published under; this is not retroactive.

If you embed `ledgerkit` in-process inside a non-GPL-compatible
application, review your own licensing position before upgrading past the
last MIT-licensed release. See
[`dev-docs/planning/core-redefinition/02-licence-migration.md`](../planning/core-redefinition/02-licence-migration.md)
for the full rationale, including why this specifically matters for
in-process (as opposed to subprocess) consumers.

Also as part of this change: `pyproject.toml`'s `license` field changed
from `{text = "MIT"}` to `{text = "GPL-3.0-or-later"}`, keeping the
classic (non-PEP-639) form. **A PEP 639 SPDX license-expression string
(`license = "GPL-3.0-or-later"`) was tried first and reverted** — it
passed locally under `setuptools 82.0.1`, but broke CI's Python 3.8 job:
no `setuptools` release supports both Python 3.8 and the PEP 639 string
form, so `pip`'s build isolation on that job installs an older
`setuptools` that rejects the string as an invalid `project.license`
value. Since dropping Python 3.8 support is a separate, unapproved policy
decision, the classic dict form was kept instead — proven compatible
across the full 3.8–3.12 matrix by the fact that it's exactly the pattern
the prior MIT declaration already used successfully. The `License ::`
classifier is kept alongside it (the dict form and a classifier coexist
without conflict; only the newer string-expression form conflicts with a
classifier under recent setuptools).

New files: `NOTICE`, `THIRD-PARTY-NOTICES.md`.

---

### Added — Stage A: agent roster and compatibility-register harness

**Human:** directed closing out the remainder of Stage A (agent-role files
and the compatibility harness), per the plan in
`dev-docs/planning/core-redefinition/03-agent-led-development.md` and
`09-compatibility-system.md`; scoped the register migration to a
representative first wave (directives, validation checks, genuinely-
unsupported features) rather than every In-Scope-table row, when asked to
choose. Confirmed Stage A complete.

**Claude:** added the seven agent-role definitions
(`.claude/agents/{hledger-researcher,compat-differential-tester,
docs-maintainer,docs-reconstructor,context-curator,
roadmap-context-curator,release-phase-auditor}.md`) per §3.2/§3.3 of the
agent-led-development plan. Built out the compatibility-register harness:
added `dev-docs/compat-register/UNEXPLAINED.md` (the open-mismatch
punch-list), added a `directly_translated` field to
`dev-docs/compat-register/schema.md` (flagged as Stage A work in
`10-source-assisted-development.md` §10.3), and migrated 25 entries from
`dev-docs/hledger-compatibility.md`'s In Scope / Out of Scope tables — 12
directive entries (including a newly drafted `LK-DIV-INCLUDE-002` for the
dot-file glob divergence, the second of the two known deviations
`09-compatibility-system.md` §9.5 named), 8 validation-check entries, and
5 `unsupported` entries (auto-postings, periodic transactions, timeclock,
virtual postings, multi-currency conversion). All 25 are `status:
proposed` — none executable-verified, since no pinned `hledger` binary
exists in this environment; that is `compat-differential-tester`'s job
from Stage C onward. Cross-linked the register from
`dev-docs/hledger-compatibility.md`'s intro. Narrowed `.gitignore`'s
blanket `.claude/` rule to `.claude/*` + `!.claude/agents/` so the new
agent-role files are actually trackable (precedent: the sibling
`codecompass` repo tracks `.claude/agents/*.md` the same way). Updated
`ROADMAP.md`'s Stage A row to `[DONE]` on explicit user confirmation.
575 tests continue to pass throughout (no `ledgerkit/`/`tests/` code
touched this phase).

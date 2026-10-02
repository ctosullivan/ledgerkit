# Pinned revisions — CodeCompass upgrade + clean-room docs initiative

Governing plan: [`dev-docs/planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md`](../planning/core-redefinition/29-codecompass-upgrade-and-clean-room-docs.md) §2.0.

**Every phase of this initiative operates against exactly the two
revisions recorded below.** "Current version" means the SHA this file
names, not whatever `git fetch` would return today. A later upgrade to
either pin requires a new, explicit, recorded decision (a new dated entry
below plus a `CHANGELOG.md` entry), never a silent `git pull`.

## codecompass

- **Repository:** `/home/cormac/projects/codecompass`
  (origin: `git@github.com:ctosullivan/codecompass.git`)
- **Pinned SHA:** `96a1e4d53acf4acc6659dc233b1ca2eafae3d41a`
- **Fetched at:** 2026-10-02 (Phase 1, this initiative)
- **Fetch command and result:**
  ```
  $ git -C /home/cormac/projects/codecompass fetch origin
  (no output — already up to date)
  $ git -C /home/cormac/projects/codecompass rev-parse HEAD
  96a1e4d53acf4acc6659dc233b1ca2eafae3d41a
  $ git -C /home/cormac/projects/codecompass rev-list --left-right --count origin/main...HEAD
  0	0
  ```
- **Enforcement mechanism chosen:** guard script
  (`dev-docs/clean-room/check_codecompass_pin.sh`), not a dedicated
  worktree. **Rationale (per plan §2.0 step 6, which permits this when
  the dedicated-worktree approach "proves disruptive to the
  environment"):** `/home/cormac/projects/codecompass` is CodeCompass's
  own active development repository — observably under concurrent
  development (155+ commits since Ledgerkit's original Stage C Phase 5A
  adoption, with recent phases dated the same day as this pin). The
  installed `codecompass` CLI is a global, system-wide `pipx install -e`
  pointed at that repository, shared with any other session that might
  be actively developing CodeCompass itself. Re-pointing that global
  install at a separate worktree, or worse, running
  `pipx install -e --force` against a detached worktree checkout, would
  change global, shared state outside this repository and outside this
  initiative's own blast radius, for no isolation benefit this guard
  script doesn't already provide equally well. The guard is checked
  before every `codecompass`-dependent command instead; see
  `check_codecompass_pin.sh`.

## codecompass-template

- **Repository:** `/home/cormac/projects/codecompass-template`
  (origin: `git@github.com:ctosullivan/codecompass-template.git` /
  `https://github.com/ctosullivan/codecompass-template.git`)
- **Pinned SHA:** `68bae8ec739aea413bbedac9f19078f6ab995aca`
- **Fetched at:** 2026-10-02T13:39:00Z (Phase 1, this initiative)
- **Fetch command and result:**
  ```
  $ git clone https://github.com/ctosullivan/codecompass-template.git
  Cloning into 'codecompass-template'...
  $ git -C /home/cormac/projects/codecompass-template fetch origin
  (no output — already up to date immediately after clone)
  $ git -C /home/cormac/projects/codecompass-template rev-parse HEAD
  68bae8ec739aea413bbedac9f19078f6ab995aca
  $ git -C /home/cormac/projects/codecompass-template rev-list --left-right --count origin/main...HEAD
  0	0
  ```
- **Enforcement mechanism:** this clone *is* the fixed checkout — it is
  never `git pull`ed again during this initiative. Every file copied or
  adapted from it (plan §3.1) is confirmed against this exact SHA
  immediately before the copy (`git -C
  /home/cormac/projects/codecompass-template rev-parse HEAD`, compared
  against the SHA above), not assumed to still match.

## Revision-change log

No changes yet. A future entry here, if ever needed, records: date,
which pin changed, old SHA → new SHA, and the explicit reason — mirroring
this file's own existing format, never editing the entries above in
place.

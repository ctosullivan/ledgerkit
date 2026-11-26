"""Scope-manifest loading and the five-check scope gate.

Implements `planning/phase-02-knowledge-api-design.md` SS3b.1 exactly: an
optional, Axiom-owned YAML file at
`knowledge/scope-manifests/<claim-id>.yaml`, never a change to the native
register's own schema.

Interpretation choices made here, not spelled out verbatim by SS3b.1, and
recorded for an independent reviewer to check:

- Checks 1 (git-tracked), 3 (scope present) and 4 (reviewer present) are
  treated as *missing evidence* when they fail -- the same outcome as no
  manifest existing at all (`derived.status: UNCERTAIN`). Only checks 2
  (claim_id mismatch) and 5 (source_pin contradiction) are treated as a
  *conflict* (`derived.status: CONTESTED`), per SS3b.1's own text: "If a
  manifest exists but fails check 2 or 5 ... this *is* a genuine conflict"
  -- stated only for those two checks, by name, which implies the other
  three are not being described as conflicts.
- Check 5 ("matches, or is not contradicted by") is satisfied vacuously
  when `source_pin` is absent from the manifest entirely -- there is
  nothing to contradict -- unlike checks 3/4, which require their fields
  to be both present AND non-empty.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

SCOPE_MANIFEST_SUBDIR = "knowledge/scope-manifests"


@dataclass(frozen=True)
class ScopeManifestOutcome:
    """Result of evaluating one claim's scope manifest.

    status is one of:
    - "absent"   -- no manifest, or one that fails to supply required
                    evidence; treated as missing, not contradictory.
    - "passes"   -- all five checks pass; `scope` carries the reviewed text.
    - "conflict" -- the manifest exists but contradicts the native record
                    (wrong claim_id, or a stale source_pin).
    """

    status: str
    scope: str | None = None
    conflict_reason: str | None = None


def _manifest_path(repo_root: Path, claim_id: str) -> Path:
    return repo_root / SCOPE_MANIFEST_SUBDIR / f"{claim_id}.yaml"


def _is_git_tracked(repo_root: Path, path: Path) -> bool:
    """Conservative: any failure (not a repo, git unavailable, file not
    tracked) reports False rather than raising -- an untracked/unknown file
    is exactly the case this check exists to catch."""
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(relative)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def evaluate_scope_manifest(
    repo_root: Path, claim_id: str, native_compatibility_target: str | None
) -> ScopeManifestOutcome:
    """Evaluate the scope manifest for `claim_id`, per SS3b.1's five checks."""
    path = _manifest_path(repo_root, claim_id)

    if not path.is_file():
        return ScopeManifestOutcome(status="absent")

    if not _is_git_tracked(repo_root, path):
        return ScopeManifestOutcome(status="absent")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return ScopeManifestOutcome(status="absent")

    if not isinstance(raw, dict):
        return ScopeManifestOutcome(status="absent")

    # Checks 2 (claim_id) and 5 (source_pin) are genuine *conflicts* and
    # must be evaluated -- and reported -- before checks 1/3/4's "missing
    # evidence" outcomes, even when both kinds of defect are present on
    # the same manifest. An earlier version of this function returned
    # "absent" as soon as it found a missing reviewed_by/reviewed_date,
    # which could mask an already-detected stale source_pin: a manifest
    # with BOTH a stale pin AND a missing reviewer was reported as merely
    # absent, silently dropping the known contradiction SS3b.1 says must
    # surface as CONTESTED. Found by native Codex review of PR #6, commit
    # f231b19.
    manifest_claim_id = raw.get("claim_id")
    if manifest_claim_id is not None and manifest_claim_id != claim_id:
        return ScopeManifestOutcome(
            status="conflict",
            conflict_reason=(
                f"scope manifest at {path} names claim_id "
                f"'{manifest_claim_id}', not '{claim_id}'"
            ),
        )

    source_pin = raw.get("source_pin")
    if (
        source_pin
        and native_compatibility_target
        and source_pin != native_compatibility_target
    ):
        return ScopeManifestOutcome(
            status="conflict",
            conflict_reason=(
                f"scope manifest at {path} has source_pin '{source_pin}', "
                f"which contradicts the native record's own "
                f"upstream.compatibility_target '{native_compatibility_target}'"
            ),
        )

    if manifest_claim_id is None:
        return ScopeManifestOutcome(status="absent")

    scope = raw.get("scope")
    if not isinstance(scope, str) or not scope.strip():
        return ScopeManifestOutcome(status="absent")

    reviewed_by = raw.get("reviewed_by")
    reviewed_date = raw.get("reviewed_date")
    if not reviewed_by or not reviewed_date:
        return ScopeManifestOutcome(status="absent")

    return ScopeManifestOutcome(status="passes", scope=scope)

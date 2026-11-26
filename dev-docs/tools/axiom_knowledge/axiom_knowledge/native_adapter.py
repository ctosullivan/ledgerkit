"""Ledgerkit compat-register adapter: native read + derived translation.

Implements `planning/phase-02-knowledge-api-design.md` SSSS3a-3f against the
real schema at Ledgerkit's `dev-docs/compat-register/schema.md`. The
`native` block a caller sees is always the record exactly as read; the
`derived` block is Axiom's own, conservative translation -- never the
reverse, and never collapsed into one view (SS3a).

Documented interpretation, not written explicitly in SS3b/SS3b.1 itself:
Ledgerkit's own schema has no field recording an evidence item's pass/fail
outcome, so "genuinely conflicting evidence" (knowledge-api-design.md SS6,
test 5) is detected here via one optional, non-schema convention: two
`evidence[]` items of the same `kind` and the same `pinned_at` that each
carry an explicit `result: pass` / `result: fail` field, disagreeing. No
real Ledgerkit compat-register entry currently sets `result` on an evidence
item -- this path is exercised only by this PR's own synthetic fixtures,
and is documented here so an independent reviewer can judge whether the
interpretation is sound, not left as an unexplained implementation detail.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .errors import MalformedError, NotFoundError
from .scope_manifest import ScopeManifestOutcome

REGISTER_FILE_SUFFIX = ".yaml"

_RELATIONSHIP_MAP = {
    "equivalent": ("equivalent", None),
    "superset": (
        "equivalent",
        "equivalent for hledger-defined behaviour only; Ledgerkit's extension "
        "behaviour (kind: extension) is additional and out of scope for this "
        "comparison",
    ),
    "subset": (
        "partial",
        "partial -- Ledgerkit intentionally covers less than hledger for this "
        "area; see native.reason for which cases are excluded",
    ),
    "incomparable": ("divergent", None),
}


@dataclass(frozen=True)
class RegisterIndex:
    """The result of scanning a register directory once."""

    records: dict[str, dict] = field(default_factory=dict)
    record_paths: dict[str, str] = field(default_factory=dict)
    malformed_by_stem: dict[str, str] = field(default_factory=dict)
    duplicate_ids: dict[str, list[str]] = field(default_factory=dict)


def load_register(register_root: Path) -> RegisterIndex:
    """Parse every *.yaml file directly in register_root (non-recursive --
    matches schema.md's own "one file per entry" convention; a nested
    examples/ directory, if present, is never descended into)."""
    records: dict[str, dict] = {}
    record_paths: dict[str, str] = {}
    malformed_by_stem: dict[str, str] = {}
    duplicate_ids: dict[str, list[str]] = {}

    for path in sorted(register_root.glob(f"*{REGISTER_FILE_SUFFIX}")):
        stem = path.stem
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            malformed_by_stem[stem] = f"{path}: invalid YAML ({exc})"
            continue

        if not isinstance(raw, dict):
            malformed_by_stem[stem] = f"{path}: does not parse to a mapping"
            continue

        record_id = raw.get("id")
        if not isinstance(record_id, str) or not record_id:
            # A non-string id (e.g. `id: [bad, id]`, valid YAML, invalid
            # here) must be rejected before any dict-key use -- a list is
            # unhashable and would raise TypeError on membership checks
            # below, not fail cleanly as Malformed. Found by native Codex
            # review of PR #6, commit 6819c45.
            malformed_by_stem[stem] = (
                f"{path}: missing or invalid (non-string) 'id' field: {record_id!r}"
            )
            continue

        # A record can be syntactically valid YAML with a good id, yet
        # have `upstream`/`ledgerkit` written as something other than a
        # mapping (e.g. `upstream: hledger`) -- both get() (via
        # api._record_to_result's upstream.get(...)) and translate()
        # (via native.get("ledgerkit").get("relationship")) dereference
        # these with .get(), which crashes with AttributeError on a
        # non-dict instead of failing cleanly as Malformed. Checked here,
        # at load time, so both get() AND find() (which reads straight
        # from `records`, never re-validating) are covered the same way.
        # Found by native Codex review of PR #6, commit f231b19.
        structural_error = None
        for nested_field in ("upstream", "ledgerkit"):
            nested_value = raw.get(nested_field)
            if nested_value is not None and not isinstance(nested_value, dict):
                structural_error = (
                    f"{path}: '{nested_field}' field must be a mapping, "
                    f"got {type(nested_value).__name__}"
                )
                break
        if structural_error is not None:
            malformed_by_stem[stem] = structural_error
            continue

        if record_id in duplicate_ids:
            duplicate_ids[record_id].append(str(path))
            continue
        if record_id in records:
            duplicate_ids[record_id] = [record_paths[record_id], str(path)]
            del records[record_id]
            del record_paths[record_id]
            continue

        records[record_id] = raw
        record_paths[record_id] = str(path)

    return RegisterIndex(
        records=records,
        record_paths=record_paths,
        malformed_by_stem=malformed_by_stem,
        duplicate_ids=duplicate_ids,
    )


def get_native(index: RegisterIndex, claim_id: str) -> dict:
    """Return the raw native record for claim_id, or raise NotFoundError /
    MalformedError -- never a silent wrong answer."""
    if claim_id in index.duplicate_ids:
        paths = ", ".join(index.duplicate_ids[claim_id])
        raise MalformedError(f"duplicate id '{claim_id}' declared by: {paths}")
    if claim_id in index.records:
        return index.records[claim_id]
    if claim_id in index.malformed_by_stem:
        raise MalformedError(index.malformed_by_stem[claim_id])
    raise NotFoundError(f"no claim with id '{claim_id}' in this register")


def _find_conflicting_evidence(evidence: list) -> str | None:
    seen: dict[tuple, set[str]] = {}
    for item in evidence or []:
        if not isinstance(item, dict):
            continue
        result = item.get("result")
        if result not in ("pass", "fail"):
            continue
        key = (item.get("kind"), item.get("pinned_at"))
        seen.setdefault(key, set()).add(result)
    for (kind, pinned_at), results in seen.items():
        if {"pass", "fail"} <= results:
            return (
                f"evidence of kind '{kind}' at pinned_at '{pinned_at}' contains "
                "both a passing and a failing result"
            )
    return None


def _translate_relationship(relationship: str | None) -> tuple[str, str | None, bool]:
    """Returns (mapping_result, mapping_scope, translation_gap)."""
    if relationship is None:
        return "unknown", None, False
    if relationship in _RELATIONSHIP_MAP:
        result, scope = _RELATIONSHIP_MAP[relationship]
        return result, scope, False
    return "unknown", None, True


def _check_reference_entries(field_name: str, entries, split) -> list[dict]:
    diagnostics: list[dict] = []
    for entry in entries or []:
        if not isinstance(entry, str) or not split["separator"] in entry:
            diagnostics.append(
                {
                    "field": field_name,
                    "value": entry,
                    "reason": f"does not contain the expected '{split['separator']}' separator",
                }
            )
            continue
        path, _, qualifier = split["fn"](entry, split["separator"])
        if not path or not qualifier:
            # A separator-containing entry with an empty path or qualifier
            # (e.g. "pkg/mod.py:", "::") previously passed the separator-
            # only check with no diagnostic, even though it still cannot
            # resolve to a real file:qualifier reference. Found by native
            # Codex review of PR #6, commit 36ff18d.
            diagnostics.append(
                {
                    "field": field_name,
                    "value": entry,
                    "reason": "path or qualifier component is empty",
                }
            )
    return diagnostics


def extract_unresolved_references(native: dict) -> list[dict]:
    """Shape-only check of SS3f's local-reference fields -- does each entry
    parse into a non-empty <path><sep><qualifier>? Does not check file
    existence against any consumer-repository revision; that is
    impacted()'s own deferred Stage 2.3 job (SS3f), not duplicated here."""
    diagnostics: list[dict] = []
    # implementation[]: split on the LAST ':' (SS3f).
    diagnostics.extend(
        _check_reference_entries(
            "implementation", native.get("implementation"),
            {"separator": ":", "fn": lambda s, sep: s.rpartition(sep)},
        )
    )
    # tests[]: split on the FIRST '::' (SS3f).
    diagnostics.extend(
        _check_reference_entries(
            "tests", native.get("tests"),
            {"separator": "::", "fn": lambda s, sep: s.partition(sep)},
        )
    )
    return diagnostics


@dataclass(frozen=True)
class DerivedResult:
    status: str
    status_basis: str
    mapping_result: str
    mapping_scope: str | None
    scope: str | None
    reviewer: str | None
    translation_gap: bool = False


def translate(native: dict, scope_outcome: ScopeManifestOutcome | None) -> DerivedResult:
    """SS3b/SS3b.1/SS3c -- the full native-to-derived translation."""
    status = native.get("status")
    verified_by = native.get("verified_by")
    verified_date = native.get("verified_date")
    relationship = (native.get("ledgerkit") or {}).get("relationship")

    mapping_result, mapping_scope, relationship_gap = _translate_relationship(relationship)
    reviewer = verified_by or None

    conflict = _find_conflicting_evidence(native.get("evidence") or [])
    if conflict:
        return DerivedResult(
            status="CONTESTED",
            status_basis=conflict,
            mapping_result=mapping_result,
            mapping_scope=mapping_scope,
            scope=None,
            reviewer=reviewer,
            translation_gap=relationship_gap,
        )

    if relationship_gap:
        # knowledge-api-design.md SS6 test 7 names "a relationship OR
        # status value outside the known enums" as ONE combined rule
        # producing derived.status: UNCERTAIN -- an unrecognised
        # relationship must downgrade the overall status exactly like an
        # unrecognised status does, not just annotate mapping_result,
        # even when the status/scope gates below would otherwise pass.
        # Found by native Codex review of PR #6, commit 6819c45: a
        # verified claim with a passing scope manifest and an unknown
        # relationship value was returning VERIFIED, contradicting this
        # rule. Conflicting evidence (above) still takes precedence, as
        # a strictly stronger signal than an unrecognised enum value.
        return DerivedResult(
            status="UNCERTAIN",
            status_basis=f"unrecognised native relationship '{relationship}'",
            mapping_result=mapping_result,
            mapping_scope=mapping_scope,
            scope=None,
            reviewer=reviewer,
            translation_gap=True,
        )

    if status == "proposed":
        return DerivedResult(
            status="UNCERTAIN",
            status_basis="native status is 'proposed' -- not yet run against the real binary",
            mapping_result=mapping_result,
            mapping_scope=mapping_scope,
            scope=None,
            reviewer=reviewer,
            translation_gap=relationship_gap,
        )

    if status == "self-verified":
        return DerivedResult(
            status="OBSERVED",
            status_basis=(
                "native status is 'self-verified' -- a real comparison was run, "
                "but by the same identity that implemented the fix, not "
                "independently; OBSERVED has no scope requirement"
            ),
            mapping_result=mapping_result,
            mapping_scope=mapping_scope,
            scope=None,
            reviewer=reviewer,
            translation_gap=relationship_gap,
        )

    if status in ("verified", "final"):
        reviewer_gate_ok = bool(verified_by) and bool(verified_date)
        if not reviewer_gate_ok:
            return DerivedResult(
                status="UNCERTAIN",
                status_basis=(
                    f"native status is '{status}' but verified_by/verified_date "
                    "are missing -- treated as missing evidence, not a contradiction"
                ),
                mapping_result=mapping_result,
                mapping_scope=mapping_scope,
                scope=None,
                reviewer=reviewer,
                translation_gap=relationship_gap,
            )

        if scope_outcome is not None and scope_outcome.status == "conflict":
            return DerivedResult(
                status="CONTESTED",
                status_basis=scope_outcome.conflict_reason or "scope manifest conflict",
                mapping_result=mapping_result,
                mapping_scope=mapping_scope,
                scope=None,
                reviewer=reviewer,
                translation_gap=relationship_gap,
            )

        if scope_outcome is not None and scope_outcome.status == "passes":
            return DerivedResult(
                status="VERIFIED",
                status_basis=(
                    f"native status '{status}' with verified_by/verified_date "
                    "present and an independently reviewed, Git-tracked scope "
                    "manifest that passes all five checks"
                ),
                mapping_result=mapping_result,
                mapping_scope=mapping_scope,
                scope=scope_outcome.scope,
                reviewer=reviewer,
                translation_gap=relationship_gap,
            )

        return DerivedResult(
            status="UNCERTAIN",
            status_basis=(
                f"native status '{status}' with verified_by/verified_date present, "
                "but no independently reviewed scope manifest exists -- missing "
                "evidence, not a contradiction; a claim cannot be VERIFIED with "
                "a null scope"
            ),
            mapping_result=mapping_result,
            mapping_scope=mapping_scope,
            scope=None,
            reviewer=reviewer,
            translation_gap=relationship_gap,
        )

    return DerivedResult(
        status="UNCERTAIN",
        status_basis=f"unrecognised native status '{status}'",
        mapping_result=mapping_result,
        mapping_scope=mapping_scope,
        scope=None,
        reviewer=reviewer,
        translation_gap=True,
    )

"""The actual get()/find() library functions, plus task-boundary helpers.

Ties discovery + native_adapter + scope_manifest + events together.
Implements `planning/phase-02-knowledge-api-design.md` SS4's `get`/`find`
read-only operations against Ledgerkit's compat-register, per
`planning/phase-02-stage-2.2-plan.md` SS2a/SS3.

`native` in the returned dict is the parsed YAML record exactly as read,
verbatim -- including real nested structure such as `ledgerkit.relationship`
or `upstream.compatibility_target` -- not a flattened re-shaping of it; SS3a's
own illustration flattens `relationship` to top level for readability in
prose, but "every other field exactly as read, unmodified" is satisfied
most faithfully by never transforming the native block at all.

`diagnostics.unresolved_references` is this implementation's own top-level
placement for SS3f's shape-only reference diagnostic -- distinct from both
`native` (never annotated) and `derived` (a status judgement, not a
data-quality note) -- a placement choice made here, not dictated verbatim
by the design illustration, and left for review.
"""
from __future__ import annotations

from pathlib import Path

from . import events
from .discovery import discover_register_root, discover_repo_root
from .errors import InvalidQueryError
from .native_adapter import (
    extract_unresolved_references,
    get_native,
    load_register,
    translate,
)
from .scope_manifest import evaluate_scope_manifest

_FIND_FIELDS = ("area", "kind", "status")


def _record_to_result(repo_root: Path, claim_id: str, native: dict) -> dict:
    compatibility_target = (native.get("upstream") or {}).get("compatibility_target")
    status = native.get("status")

    scope_outcome = None
    if status in ("verified", "final"):
        scope_outcome = evaluate_scope_manifest(repo_root, claim_id, compatibility_target)

    derived = translate(native, scope_outcome)

    return {
        "id": claim_id,
        "native": dict(native),
        "derived": {
            "status": derived.status,
            "status_basis": derived.status_basis,
            "mapping_result": derived.mapping_result,
            "mapping_scope": derived.mapping_scope,
            "scope": derived.scope,
            "reviewer": derived.reviewer,
            "translation_gap": derived.translation_gap,
        },
        "evidence": list(native.get("evidence") or []),
        "related": {
            "resolved_into": native.get("resolved_into"),
            "resolves": native.get("resolves"),
        },
        "diagnostics": {
            "unresolved_references": extract_unresolved_references(native),
        },
    }


def get(repo_root: str | None, claim_id: str, task_id: str | None = None) -> dict:
    """get(id) -> Claim, per knowledge-api-design.md SS4.

    Raises RepositoryNotFoundError, RegisterNotFoundError, NotFoundError or
    MalformedError -- never returns a silently-wrong or empty result.
    """
    resolved_repo_root = discover_repo_root(repo_root)
    register_root = discover_register_root(resolved_repo_root)
    index = load_register(register_root)

    try:
        native = get_native(index, claim_id)
    except Exception as exc:
        events.log_event(
            resolved_repo_root,
            "knowledge_get",
            task_id=task_id,
            knowledge_id=claim_id,
            operation="get",
            result="error",
            error_class=type(exc).__name__,
            evidence_class="direct",
        )
        raise

    result = _record_to_result(resolved_repo_root, claim_id, native)
    events.log_event(
        resolved_repo_root,
        "knowledge_get",
        task_id=task_id,
        knowledge_id=claim_id,
        operation="get",
        result="ok",
        evidence_class="direct",
    )
    return result


def _parse_find_query(query: str) -> tuple[str | None, str]:
    """Returns (field, value). field is None for a plain substring/exact-ID
    query. Raises InvalidQueryError for reserved-character misuse."""
    if query == "":
        raise InvalidQueryError("empty query string")

    if ":" not in query:
        return None, query

    field_name, _, value = query.partition(":")
    if field_name == "":
        raise InvalidQueryError(f"query '{query}' has an empty field name before ':'")
    if field_name not in _FIND_FIELDS:
        raise InvalidQueryError(
            f"query '{query}' names field '{field_name}', which is not one of "
            f"{_FIND_FIELDS}"
        )
    if value == "":
        raise InvalidQueryError(f"query '{query}' has an empty value after ':'")
    return field_name, value


def find(repo_root: str | None, query: str, task_id: str | None = None) -> list[dict]:
    """find(query) -> list[Claim], deterministic, per knowledge-api-design.md SS4.

    Raises RepositoryNotFoundError, RegisterNotFoundError or InvalidQueryError.
    An empty result ([]) is a valid, non-error return.
    """
    resolved_repo_root = discover_repo_root(repo_root)
    register_root = discover_register_root(resolved_repo_root)
    index = load_register(register_root)

    try:
        field_name, value = _parse_find_query(query)
    except InvalidQueryError:
        events.log_event(
            resolved_repo_root,
            "knowledge_find",
            task_id=task_id,
            operation="find",
            result="error",
            error_class="InvalidQueryError",
            evidence_class="direct",
        )
        raise

    matched_ids: list[str] = []
    if field_name is None:
        if value in index.records:
            matched_ids = [value]
        else:
            lowered = value.lower()
            matched_ids = [
                claim_id
                for claim_id, native in index.records.items()
                if lowered in str(native.get("area", "")).lower()
            ]
    else:
        matched_ids = [
            claim_id
            for claim_id, native in index.records.items()
            if str(native.get(field_name)) == value
        ]

    matched_ids.sort()
    results = [
        _record_to_result(resolved_repo_root, claim_id, index.records[claim_id])
        for claim_id in matched_ids
    ]

    events.log_event(
        resolved_repo_root,
        "knowledge_find",
        task_id=task_id,
        operation="find",
        result="ok",
        evidence_class="direct",
        result_count=len(matched_ids),
        returned_claim_ids=list(matched_ids),
    )
    return results


def task_start(repo_root: str | None, task_id: str) -> None:
    resolved_repo_root = discover_repo_root(repo_root)
    events.log_event(resolved_repo_root, "task_start", task_id=task_id, result="ok", evidence_class="direct")


def task_accepted(repo_root: str | None, task_id: str) -> None:
    resolved_repo_root = discover_repo_root(repo_root)
    events.log_event(resolved_repo_root, "task_accepted", task_id=task_id, result="ok", evidence_class="reviewed")

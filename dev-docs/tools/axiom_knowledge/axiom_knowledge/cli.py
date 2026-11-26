"""The `axiom-knowledge` CLI.

No packaging/console-script entry point exists yet
(`planning/phase-02-adoption-design.md` SS5 defers packaging until a second
real consumer exists) -- invoked exactly like `axiom_validator`'s own CLI,
via `python3 -m axiom_knowledge <args>` with `src/` on PYTHONPATH. Every
reference to `axiom-knowledge <op> ...` in the planning documents refers to
this invocation.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys

from . import api
from .errors import AxiomKnowledgeError


def _json_default(obj):
    """PyYAML's safe_load parses an unquoted YAML date (e.g.
    `verified_date: 2026-11-25`) into a datetime.date/datetime object --
    not every compat-register entry quotes its dates (schema.md's own
    illustration doesn't). The native block preserves whatever safe_load
    produced (SS3a: "exactly as read"), so the JSON boundary, not the
    adapter, is where this is made serializable again. Found by native
    Codex review of PR #6, commit 6819c45."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, default=_json_default))


def _print_error(exc: Exception) -> None:
    print(
        json.dumps({"error": type(exc).__name__, "message": str(exc)}, sort_keys=True),
        file=sys.stderr,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axiom-knowledge")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Explicit repository root. Must contain knowledge/README.md. "
        "Defaults to walking up from the current working directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get", help="Retrieve one claim by exact ID.")
    get_parser.add_argument("claim_id")
    get_parser.add_argument("--task-id", default=None)

    find_parser = subparsers.add_parser("find", help="Deterministic claim search.")
    find_parser.add_argument("query")
    find_parser.add_argument("--task-id", default=None)

    task_start_parser = subparsers.add_parser(
        "task-start", help="Record the start of a bounded Axiom-guided unit of work."
    )
    task_start_parser.add_argument("--task-id", required=True)

    task_accepted_parser = subparsers.add_parser(
        "task-accepted", help="Record that a task's acceptance criteria were confirmed met."
    )
    task_accepted_parser.add_argument("--task-id", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "get":
            result = api.get(args.repo_root, args.claim_id, task_id=args.task_id)
            _print_json(result)
            return 0

        if args.command == "find":
            results = api.find(args.repo_root, args.query, task_id=args.task_id)
            _print_json(results)
            return 0

        if args.command == "task-start":
            api.task_start(args.repo_root, args.task_id)
            _print_json({"event": "task_start", "task_id": args.task_id})
            return 0

        if args.command == "task-accepted":
            api.task_accepted(args.repo_root, args.task_id)
            _print_json({"event": "task_accepted", "task_id": args.task_id})
            return 0

        parser.error(f"unknown command '{args.command}'")
        return 2
    except AxiomKnowledgeError as exc:
        _print_error(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())

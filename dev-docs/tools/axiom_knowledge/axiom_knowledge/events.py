"""CLI-owned JSONL event logging.

Implements `planning/phase-02-stage-2.2-plan.md` SS2a.3: exactly the four
event producers Stage 2.2 delivers (task-start, task-accepted,
knowledge_get, knowledge_find), each honouring `AXIOM_DISABLE_LOGGING=1`
and each tolerating a write failure without blocking the caller's actual
result (`planning/phase-02-measurement-design.md` SS5).

`session_id` is always written as null in this stage -- the
SessionStart/SessionEnd hook pair that would populate it is explicitly
deferred (SS2a.3); this is the design's own documented fallback, not a
defect this module works around.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DISABLE_ENV_VAR = "AXIOM_DISABLE_LOGGING"
EVENTS_RELATIVE_PATH = ".axiom-local/events.jsonl"


def _logging_disabled() -> bool:
    return os.environ.get(DISABLE_ENV_VAR) == "1"


def _git_revision(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def log_event(repo_root: Path, event_type: str, task_id: str | None = None, **fields) -> None:
    """Append one JSONL event. Never raises -- a write failure (disk full,
    permissions, missing directory) is swallowed so it never blocks the
    caller's own read operation, per the measurement design's explicit
    non-blocking requirement."""
    if _logging_disabled():
        return

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "session_id": None,
        "task_id": task_id,
        "git_revision": _git_revision(repo_root),
        **fields,
    }

    try:
        events_path = repo_root / EVENTS_RELATIVE_PATH
        events_path.parent.mkdir(parents=True, exist_ok=True)
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True))
            handle.write("\n")
    except OSError:
        pass

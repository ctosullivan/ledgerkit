"""axiom_knowledge -- the minimal, read-only Axiom knowledge library.

Public API: `get(repo_root, claim_id)`, `find(repo_root, query)`. See
`planning/phase-02-knowledge-api-design.md` and
`planning/phase-02-stage-2.2-plan.md` for the contracts this implements.
"""
from .api import find, get, task_accepted, task_start
from .cli import main
from .errors import (
    AxiomKnowledgeError,
    InvalidQueryError,
    MalformedError,
    NotFoundError,
    RegisterNotFoundError,
    RepositoryNotFoundError,
)

__all__ = [
    "get",
    "find",
    "task_start",
    "task_accepted",
    "main",
    "AxiomKnowledgeError",
    "NotFoundError",
    "MalformedError",
    "InvalidQueryError",
    "RepositoryNotFoundError",
    "RegisterNotFoundError",
]

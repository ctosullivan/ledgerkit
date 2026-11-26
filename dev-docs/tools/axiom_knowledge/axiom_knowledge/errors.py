"""Named error types for the axiom-knowledge library and CLI.

Every error a caller can hit is a distinct, named exception rather than a
generic one, per `planning/phase-02-knowledge-api-design.md` SS4's error
semantics and `planning/phase-02-stage-2.2-plan.md` SS3's requirement that
discovery/read failures are actionable, not a silent empty result.
"""
from __future__ import annotations


class AxiomKnowledgeError(Exception):
    """Base class for every error this package raises on purpose."""


class RepositoryNotFoundError(AxiomKnowledgeError):
    """No recognised Axiom-adopted repository was found.

    Raised when an explicit --repo-root does not contain knowledge/README.md,
    or when the default walk-up search reaches the filesystem root without
    finding one.
    """


class RegisterNotFoundError(AxiomKnowledgeError):
    """A repository was recognised, but its claim register directory
    does not exist on disk.

    Distinct from RepositoryNotFoundError: the repository itself (and its
    knowledge/README.md marker) was found; what is missing is the
    register path that marker names (or the generic default), which is a
    different, more specific failure a caller needs to disambiguate.
    """


class NotFoundError(AxiomKnowledgeError):
    """get() was called for a claim ID that does not exist in the register."""


class MalformedError(AxiomKnowledgeError):
    """A claim record exists but fails to parse or is missing a field the
    adapter requires to produce any result at all (not a derived-status
    judgement — a structural defect in the record itself)."""


class InvalidQueryError(AxiomKnowledgeError):
    """find() was called with a syntactically malformed query string."""

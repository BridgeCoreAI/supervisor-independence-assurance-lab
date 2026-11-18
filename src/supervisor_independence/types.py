"""Immutable synthetic request and decision types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    role: str


@dataclass(frozen=True)
class Decision:
    outcome: str
    reason: str
    event_id: str
    correlation_id: str
    reference_id: Optional[str] = None


@dataclass(frozen=True)
class ActionRequest:
    request_id: str
    principal: str
    action: str
    resource: str
    proposed_marker: str
    expected_policy_digest: str
    claimed_authority: str = ""  # Untrusted request content, never used for permissions.
    claimed_exception_id: str = ""  # Untrusted; the gate resolves grants itself.


@dataclass(frozen=True)
class ExceptionProposal:
    principal: str
    action: str
    resource: str
    policy_digest: str
    valid_from: datetime
    expires_at: datetime
    claimed_approver: str = ""  # Deliberately ignored for authorization.


@dataclass(frozen=True)
class PolicyRevision:
    version: str
    allow_without_exception: bool
    change_note: str
    expected_version: str
    expected_digest: str
    claimed_administrator: str = ""  # Deliberately ignored for authorization.

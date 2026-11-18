"""Scoped, one-use synthetic exception approval store."""

from dataclasses import dataclass, replace
from datetime import datetime
from .types import Decision


@dataclass(frozen=True)
class ExceptionGrant:
    exception_id: str
    principal: str
    action: str
    resource: str
    policy_digest: str
    valid_from: datetime
    expires_at: datetime
    approver_id: str
    status: str = "active"
    remaining_uses: int = 1


class ExceptionStore:
    def __init__(self, authority, evidence, policy_store):
        self._authority = authority
        self._evidence = evidence
        self._policy_store = policy_store
        self.__grants = {}

    def snapshot(self):
        return [
            {
                "exception_id": x.exception_id, "principal": x.principal,
                "action": x.action, "resource": x.resource,
                "policy_digest": x.policy_digest,
                "valid_from": x.valid_from.isoformat(),
                "expires_at": x.expires_at.isoformat(),
                "approver_id": x.approver_id,
                "status": x.status, "remaining_uses": x.remaining_uses,
            }
            for x in sorted(self.__grants.values(), key=lambda g: g.exception_id)
        ]

    def approve(self, context, proposal, now, correlation_id):
        if not self._authority.has_role(context, "exception_approver"):
            outcome, reason = "DENY", "UNAUTHORIZED_EXCEPTION_APPROVER"
        elif (
            proposal.principal != "AGENT-01"
            or proposal.action != "customer_record.update"
            or proposal.resource != "CUST-TEST-001"
            or proposal.policy_digest != self._policy_store.snapshot()["digest"]
            or not (proposal.valid_from <= now < proposal.expires_at)
        ):
            outcome, reason = "DENY", "INVALID_EXCEPTION_SCOPE_OR_VALIDITY"
        else:
            outcome, reason = "PERMIT", "AUTHORIZED_EXCEPTION_APPROVAL"
        grant_id = None
        if outcome == "PERMIT":
            grant_id = "EXC-%03d" % (len(self.__grants) + 1)
            self.__grants[grant_id] = ExceptionGrant(
                grant_id, proposal.principal, proposal.action, proposal.resource,
                proposal.policy_digest, proposal.valid_from, proposal.expires_at,
                context.actor_id,
            )
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "exception.approve",
            outcome, reason, {"requested_principal": proposal.principal,
                               "action": proposal.action, "resource": proposal.resource,
                               "claimed_approver": proposal.claimed_approver,
                               "created_exception": grant_id}
        )
        return Decision(outcome, reason, event_id, correlation_id, grant_id)

    def matching_grant(self, principal, action, resource, digest, now):
        for grant in self.__grants.values():
            if (
                grant.principal == principal and grant.action == action
                and grant.resource == resource and grant.policy_digest == digest
                and grant.valid_from <= now < grant.expires_at
                and grant.status == "active" and grant.remaining_uses > 0
            ):
                return grant
        return None

    def consume(self, grant_id):
        """Only the protected executor calls this within the fixture.

        Not an infrastructure-enforced capability boundary; limitations documented.
        """
        grant = self.__grants.get(grant_id)
        if grant is None or grant.status != "active" or grant.remaining_uses <= 0:
            return False
        self.__grants[grant_id] = replace(grant, remaining_uses=grant.remaining_uses - 1)
        return True

    def revoke(self, context, grant_id, correlation_id):
        grant = self.__grants.get(grant_id)
        if not self._authority.has_role(context, "exception_approver"):
            outcome, reason = "DENY", "UNAUTHORIZED_EXCEPTION_APPROVER"
        elif grant is None:
            outcome, reason = "DENY", "UNKNOWN_EXCEPTION"
        else:
            self.__grants[grant_id] = replace(grant, status="revoked")
            outcome, reason = "PERMIT", "AUTHORIZED_EXCEPTION_REVOCATION"
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "exception.revoke", outcome, reason,
            {"exception_id": grant_id}
        )
        return Decision(outcome, reason, event_id, correlation_id)

    def direct_write(self, context, proposal, correlation_id):
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "exception.direct_write",
            "DENY", "DIRECT_EXCEPTION_WRITE_DISABLED",
            {"action": proposal.action, "resource": proposal.resource}
        )
        return Decision("DENY", "DIRECT_EXCEPTION_WRITE_DISABLED", event_id, correlation_id)

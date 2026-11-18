"""Policy and scoped-exception evaluation against trusted actor context."""

from .types import Decision


class AuthorizationGate:
    def __init__(self, authority, policy_store, exception_store, evidence):
        self._authority = authority
        self._policy_store = policy_store
        self._exceptions = exception_store
        self._evidence = evidence

    def evaluate(self, context, request, now, correlation_id):
        policy = self._policy_store.snapshot()
        grant_id = None
        if not self._authority.has_role(context, "agent") or request.principal != context.actor_id:
            outcome, reason = "DENY", "UNAUTHORIZED_AGENT_CONTEXT"
        elif request.action != "customer_record.update" or request.resource != "CUST-TEST-001":
            outcome, reason = "DENY", "PROTECTED_ACTION_SCOPE_MISMATCH"
        elif request.expected_policy_digest != policy["digest"]:
            outcome, reason = "HUMAN_REVIEW", "POLICY_CHANGED_REVALIDATION_REQUIRED"
        elif policy["allow_without_exception"]:
            outcome, reason = "PERMIT", "CURRENT_POLICY_PERMITS"
        else:
            grant = self._exceptions.matching_grant(
                request.principal, request.action, request.resource, policy["digest"], now
            )
            if grant is None:
                outcome, reason = "DENY", "NO_VALID_EXCEPTION"
            else:
                outcome, reason = "PERMIT", "VALID_BOUNDED_EXCEPTION"
                grant_id = grant.exception_id
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "gate.evaluate", outcome, reason,
            {"request_id": request.request_id, "policy_version": policy["version"],
             "policy_digest": policy["digest"], "matched_exception": grant_id,
             "claimed_authority_ignored": bool(request.claimed_authority),
             "claimed_exception_ignored": bool(request.claimed_exception_id)}
        )
        return Decision(outcome, reason, event_id, correlation_id, grant_id)

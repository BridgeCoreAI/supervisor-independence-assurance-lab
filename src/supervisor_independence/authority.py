"""Trusted synthetic identity lookup controlled by the test harness."""

from .types import ActorContext


class AuthorityResolver:
    ROLES = {
        "AGENT-01": "agent",
        "SUPERVISOR-01": "supervisor",
        "HUMAN-APPROVER-01": "exception_approver",
        "POLICY-ADMIN-01": "policy_admin",
    }

    def context(self, actor_id):
        """Only the trusted test harness should invoke this method."""
        if actor_id not in self.ROLES:
            raise ValueError("Unknown synthetic test identity")
        return ActorContext(actor_id, self.ROLES[actor_id])

    def has_role(self, context, role):
        return (
            isinstance(context, ActorContext)
            and self.ROLES.get(context.actor_id) == role
            and context.role == role
        )

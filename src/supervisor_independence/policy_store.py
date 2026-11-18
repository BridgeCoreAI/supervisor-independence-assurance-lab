"""Canonical policy store and guarded administration interfaces."""

import hashlib
import json
from .types import Decision


def canonical_policy(version, allow_without_exception, change_note):
    body = {
        "action": "customer_record.update",
        "resource": "CUST-TEST-001",
        "version": version,
        "allow_without_exception": bool(allow_without_exception),
        "change_note": change_note,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class PolicyStore:
    def __init__(self, authority, evidence):
        self._authority = authority
        self._evidence = evidence
        self.__policy_bytes = canonical_policy("policy-v1", False, "baseline")

    def snapshot(self):
        # Copy immutable bytes; no object returned here is a writable store handle.
        current = json.loads(self.__policy_bytes.decode("ascii"))
        return {
            "version": current["version"],
            "digest": hashlib.sha256(self.__policy_bytes).hexdigest(),
            "canonical_bytes_hex": self.__policy_bytes.hex(),
            "allow_without_exception": current["allow_without_exception"],
        }

    def activate(self, context, revision, correlation_id):
        before = self.snapshot()
        if not self._authority.has_role(context, "policy_admin"):
            outcome, reason = "DENY", "UNAUTHORIZED_POLICY_ADMIN"
        elif (
            revision.expected_version != before["version"]
            or revision.expected_digest != before["digest"]
        ):
            outcome, reason = "DENY", "STALE_POLICY_PRECONDITION"
        elif revision.version == before["version"] or not revision.version.strip():
            outcome, reason = "DENY", "INVALID_POLICY_REVISION"
        else:
            new_bytes = canonical_policy(
                revision.version, revision.allow_without_exception, revision.change_note
            )
            if new_bytes == self.__policy_bytes:
                outcome, reason = "DENY", "UNCHANGED_POLICY_CONTENT"
            else:
                self.__policy_bytes = new_bytes
                outcome, reason = "PERMIT", "AUTHORIZED_POLICY_ACTIVATION"
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "policy.activate",
            outcome, reason, {"requested_version": revision.version,
                               "claimed_administrator": revision.claimed_administrator}
        )
        return Decision(outcome, reason, event_id, correlation_id)

    def direct_write(self, context, raw_bytes, correlation_id):
        # No raw-write interface is available, including to a policy administrator.
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "policy.direct_write",
            "DENY", "DIRECT_POLICY_WRITE_DISABLED", {"bytes_attempted": len(raw_bytes)}
        )
        return Decision("DENY", "DIRECT_POLICY_WRITE_DISABLED", event_id, correlation_id)

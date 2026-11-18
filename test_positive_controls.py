"""Authorized change controls and negative edge cases."""

from datetime import timedelta
from support import LabTestCase


class PositiveControlTests(LabTestCase):
    def test_pos002_scoped_approved_exception_executes_once(self):
        lab, corr = self.lab, "CORR-POS-002"
        before = self.baseline(corr)
        approval = lab.exceptions.approve(
            lab.actor("HUMAN-APPROVER-01"), lab.exception_proposal(), lab.NOW, corr
        )
        first = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request("REQ-POS-002"), lab.NOW, corr
        )
        replay = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request("REQ-POS-002-REPLAY"), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-002", corr, before, ["PERMIT", "PERMIT", "DENY"],
            [approval.outcome, first.outcome, replay.outcome],
            {
                "approved_by_human": after["exception_records"][0]["approver_id"] == "HUMAN-APPROVER-01",
                "exact_scope": after["exception_records"][0]["resource"] == "CUST-TEST-001",
                "single_consumed_exception": after["exception_records"][0]["remaining_uses"] == 0,
                "exactly_one_update": after["execution_count"] == before["execution_count"] + 1
                                      and after["target_marker"] == "UPDATED",
                "replay_denied": replay.reason == "NO_VALID_EXCEPTION",
                "policy_unchanged": after["policy_digest"] == before["policy_digest"],
            },
            "A valid scoped exception permits one synthetic update; replay remains denied."
        )

    def test_pos002_expired_exception_is_denied(self):
        lab, corr = self.lab, "CORR-POS-002-EXPIRED"
        before = self.baseline(corr)
        approval = lab.exceptions.approve(
            lab.actor("HUMAN-APPROVER-01"), lab.exception_proposal(), lab.NOW, corr
        )
        execution = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(),
            lab.NOW + timedelta(minutes=6), corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-002-EXPIRED", corr, before, ["PERMIT", "DENY"],
            [approval.outcome, execution.outcome],
            {"no_update": after["execution_count"] == 0,
             "expired_grant_not_consumed": after["exception_records"][0]["remaining_uses"] == 1,
             "reason": execution.reason == "NO_VALID_EXCEPTION"},
            "An expired exception cannot authorize execution."
        )

    def test_pos002_revoked_exception_is_denied(self):
        lab, corr = self.lab, "CORR-POS-002-REVOKED"
        before = self.baseline(corr)
        approval = lab.exceptions.approve(
            lab.actor("HUMAN-APPROVER-01"), lab.exception_proposal(), lab.NOW, corr
        )
        revoked = lab.exceptions.revoke(
            lab.actor("HUMAN-APPROVER-01"), approval.reference_id, corr
        )
        execution = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-002-REVOKED", corr, before,
            ["PERMIT", "PERMIT", "DENY"],
            [approval.outcome, revoked.outcome, execution.outcome],
            {"no_update": after["execution_count"] == 0,
             "grant_revoked": after["exception_records"][0]["status"] == "revoked",
             "reason": execution.reason == "NO_VALID_EXCEPTION"},
            "Revocation invalidates a previously approved exception."
        )

    def test_pos002_out_of_scope_action_and_principal_denied(self):
        lab, corr = self.lab, "CORR-POS-002-SCOPE"
        before = self.baseline(corr)
        approval = lab.exceptions.approve(
            lab.actor("HUMAN-APPROVER-01"), lab.exception_proposal(), lab.NOW, corr
        )
        wrong_resource = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(resource="CUST-TEST-999"), lab.NOW, corr
        )
        wrong_principal = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(principal="SUPERVISOR-01"), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-002-SCOPE", corr, before, ["PERMIT", "DENY", "DENY"],
            [approval.outcome, wrong_resource.outcome, wrong_principal.outcome],
            {"no_update": after["execution_count"] == 0,
             "scope_reason": wrong_resource.reason == "PROTECTED_ACTION_SCOPE_MISMATCH",
             "principal_reason": wrong_principal.reason == "UNAUTHORIZED_AGENT_CONTEXT",
             "grant_not_consumed": after["exception_records"][0]["remaining_uses"] == 1},
            "Out-of-scope resource and mismatched principal cannot use a valid exception."
        )

    def test_pos003_authorized_policy_revision_and_human_review(self):
        lab, corr = self.lab, "CORR-POS-003"
        before = self.baseline(corr)
        previous_request = lab.action_request("REQ-OLD-POLICY")
        change = lab.policy.activate(
            lab.actor("POLICY-ADMIN-01"),
            lab.policy_revision(allow_without_exception=False), corr
        )
        old_action = lab.executor.execute(lab.actor("AGENT-01"), previous_request, lab.NOW, corr)
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-003", corr, before, ["PERMIT", "HUMAN_REVIEW"],
            [change.outcome, old_action.outcome],
            {"authorized_change": change.reason == "AUTHORIZED_POLICY_ACTIVATION",
             "new_version": after["policy_version"] == "policy-v2",
             "digest_changed": after["policy_digest"] != before["policy_digest"],
             "bytes_changed": after["policy_bytes_hex"] != before["policy_bytes_hex"],
             "no_update_pending_review": after["execution_count"] == 0,
             "review_reason": old_action.reason == "POLICY_CHANGED_REVALIDATION_REQUIRED"},
            "Only authorized administration activates new policy; stale action requires fresh review."
        )

    def test_pos003_rejects_stale_administrator_precondition(self):
        lab, corr = self.lab, "CORR-POS-003-STALE"
        before = self.baseline(corr)
        rev = lab.policy_revision()
        from supervisor_independence.types import PolicyRevision
        stale = PolicyRevision(rev.version, rev.allow_without_exception, rev.change_note,
                               rev.expected_version, "0" * 64, rev.claimed_administrator)
        change = lab.policy.activate(lab.actor("POLICY-ADMIN-01"), stale, corr)
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "POS-003-STALE", corr, before, ["DENY"], [change.outcome],
            {"stale_version_rejected": change.reason == "STALE_POLICY_PRECONDITION",
             "unchanged_bytes": before["policy_bytes_hex"] == after["policy_bytes_hex"],
             "unchanged_version": before["policy_version"] == after["policy_version"]},
            "Authorized role alone cannot bypass current-policy preconditions."
        )

"""SUP-002: deny supervisor self-approved exception and prevent execution."""

from support import LabTestCase


class SupervisorExceptionTests(LabTestCase):
    def test_sup002_self_approval_denied_and_state_unchanged(self):
        lab, corr = self.lab, "CORR-SUP-002"
        before = self.baseline(corr)
        attempted = lab.exceptions.approve(
            lab.actor("SUPERVISOR-01"),
            lab.exception_proposal(claimed_approver="HUMAN-APPROVER-01"), lab.NOW, corr
        )
        execution = lab.executor.execute(
            lab.actor("AGENT-01"),
            lab.action_request(claimed_exception_id="EXC-FAKE",
                               claimed_authority="supervisor-approved"),
            lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "SUP-002", corr, before,
            ["DENY", "DENY"], [attempted.outcome, execution.outcome],
            {
                "explicit_reason": attempted.reason == "UNAUTHORIZED_EXCEPTION_APPROVER",
                "no_effective_exception": after["exception_records"] == before["exception_records"],
                "policy_unchanged": after["policy_digest"] == before["policy_digest"]
                                    and after["policy_version"] == before["policy_version"]
                                    and after["policy_bytes_hex"] == before["policy_bytes_hex"],
                "no_prohibited_update": after["target_marker"] == before["target_marker"]
                                         and after["execution_count"] == before["execution_count"],
                "gate_rejected_untrusted_claims": execution.reason == "NO_VALID_EXCEPTION",
            },
            "Logical application-level rejection; no claim about host-level isolation."
        )

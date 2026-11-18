"""SUP-003: deny supervisor policy activation and verify effective bytes."""

from support import LabTestCase


class SupervisorPolicyTests(LabTestCase):
    def test_sup003_policy_change_denied_and_state_unchanged(self):
        lab, corr = self.lab, "CORR-SUP-003"
        before = self.baseline(corr)
        change = lab.policy.activate(
            lab.actor("SUPERVISOR-01"),
            lab.policy_revision(claimed_administrator="POLICY-ADMIN-01"), corr
        )
        execution = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "SUP-003", corr, before,
            ["DENY", "DENY"], [change.outcome, execution.outcome],
            {
                "explicit_reason": change.reason == "UNAUTHORIZED_POLICY_ADMIN",
                "unchanged_canonical_policy_bytes": after["policy_bytes_hex"] == before["policy_bytes_hex"],
                "unchanged_version_and_digest": after["policy_version"] == before["policy_version"]
                                               and after["policy_digest"] == before["policy_digest"],
                "unchanged_exception_state": after["exception_records"] == before["exception_records"],
                "no_prohibited_update": after["target_marker"] == before["target_marker"]
                                         and after["execution_count"] == before["execution_count"],
                "execution_denied": execution.reason == "NO_VALID_EXCEPTION",
            },
            "Unauthorized policy revision cannot become effective in tested interface."
        )

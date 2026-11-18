"""Attempt alternate exposed write interfaces and observe protected state."""

from support import LabTestCase


class BypassTests(LabTestCase):
    def test_byp002_alternate_exception_write_denied(self):
        lab, corr = self.lab, "CORR-BYP-002"
        before = self.baseline(corr)
        write = lab.exceptions.direct_write(
            lab.actor("SUPERVISOR-01"), lab.exception_proposal(), corr
        )
        action = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "BYP-002", corr, before, ["DENY", "DENY"],
            [write.outcome, action.outcome],
            {"alternate_interface_denied": write.reason == "DIRECT_EXCEPTION_WRITE_DISABLED",
             "no_grant": after["exception_records"] == before["exception_records"],
             "no_update": after["execution_count"] == 0},
            "Exercised direct_write interface only; host process and private attributes not isolated."
        )

    def test_byp003_alternate_policy_write_denied(self):
        lab, corr = self.lab, "CORR-BYP-003"
        before = self.baseline(corr)
        write = lab.policy.direct_write(
            lab.actor("SUPERVISOR-01"), b'{"allow_without_exception":true}', corr
        )
        action = lab.executor.execute(
            lab.actor("AGENT-01"), lab.action_request(), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        self.finalize(
            "BYP-003", corr, before, ["DENY", "DENY"],
            [write.outcome, action.outcome],
            {"alternate_interface_denied": write.reason == "DIRECT_POLICY_WRITE_DISABLED",
             "no_policy_change": after["policy_bytes_hex"] == before["policy_bytes_hex"]
                                 and after["policy_digest"] == before["policy_digest"],
             "no_update": after["execution_count"] == 0},
            "Exercised direct_write interface only; not proof against arbitrary Python memory writes."
        )

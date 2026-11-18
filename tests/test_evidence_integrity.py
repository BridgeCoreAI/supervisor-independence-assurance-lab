"""Verify that state observation, not denial alone, controls the conclusion."""

from support import LabTestCase, reconcile, CASE_EVIDENCE


class ObserverTests(LabTestCase):
    def test_evidence_missing_observer_is_inconclusive(self):
        lab = self.lab
        denied = lab.policy.activate(
            lab.actor("SUPERVISOR-01"), lab.policy_revision(), "CORR-EVID-MISSING"
        )
        status = reconcile(["DENY"], [denied.outcome], None, None, {"decision_denied": True})
        self.assertEqual(status, "INCONCLUSIVE")
        CASE_EVIDENCE[self.id()] = {
            "test_id": "EVID-MISSING-OBSERVER",
            "test_method": self.id(),
            "correlation_id": "CORR-EVID-MISSING",
            "expected_decisions": ["DENY"],
            "actual_decisions": [denied.outcome],
            "disposition": "PASS",
            "tested_reconciliation_expected": "INCONCLUSIVE",
            "tested_reconciliation_observed": status,
            "verification_checks": {"missing_observation_is_inconclusive": status == "INCONCLUSIVE"},
            "before": None,
            "after": None,
            "events": lab.evidence.for_correlation("CORR-EVID-MISSING"),
            "interpretation": "PASS refers to test of reconciliation logic; the synthetic missing-evidence case is INCONCLUSIVE.",
        }

    def test_evidence_denial_plus_unauthorized_state_change_is_fail(self):
        lab, corr = self.lab, "CORR-EVID-STATE"
        before = lab.observer.snapshot(corr)[0]
        denied = lab.policy.activate(
            lab.actor("SUPERVISOR-01"), lab.policy_revision(), corr
        )
        # Fault injection by trusted test harness, not a demonstrated reachable bypass.
        lab.executor._ProtectedExecutionService__marker = "FAULT_INJECTED"
        after = lab.observer.snapshot(corr)[0]
        status = reconcile(["DENY"], [denied.outcome], before, after,
                           {"no_prohibited_update": after["target_marker"] == before["target_marker"]})
        self.assertEqual(denied.outcome, "DENY")
        self.assertEqual(status, "FAIL")
        CASE_EVIDENCE[self.id()] = {
            "test_id": "EVID-FAULT-INJECTION",
            "test_method": self.id(),
            "correlation_id": corr,
            "expected_decisions": ["DENY"],
            "actual_decisions": [denied.outcome],
            "disposition": "PASS",
            "tested_reconciliation_expected": "FAIL",
            "tested_reconciliation_observed": status,
            "verification_checks": {"state_mismatch_detected": status == "FAIL"},
            "before": before,
            "after": after,
            "events": lab.evidence.for_correlation(corr),
            "interpretation": "PASS refers to fault-detection test; the deliberately corrupted synthetic state is a FAIL.",
        }

    def test_evidence_correlation_has_attempt_decision_and_observation(self):
        lab, corr = self.lab, "CORR-EVID-CHAIN"
        before = self.baseline(corr)
        result = lab.exceptions.approve(
            lab.actor("SUPERVISOR-01"), lab.exception_proposal(), lab.NOW, corr
        )
        after = lab.observer.snapshot(corr)[0]
        events = lab.evidence.for_correlation(corr)
        self.finalize(
            "EVID-CORRELATION", corr, before, ["DENY"], [result.outcome],
            {"attempt_recorded": any(e["operation"] == "exception.approve" for e in events),
             "denial_recorded": any(e["decision"] == "DENY" for e in events),
             "snapshots_recorded": len([e for e in events if e["operation"] == "observer.snapshot"]) >= 2,
             "no_effective_exception": after["exception_records"] == before["exception_records"]},
            "Correlated recorded attempts and read-only before/after observations."
        )

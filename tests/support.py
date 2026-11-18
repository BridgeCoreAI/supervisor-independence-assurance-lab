"""Shared test setup and structured, independent-state evidence reconciliation."""

import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from supervisor_independence.fixtures import LabFixture  # noqa: E402

CASE_EVIDENCE = {}


def reconcile(expected_decisions, actual_decisions, before, after, checks):
    if before is None or after is None:
        return "INCONCLUSIVE"
    if not checks or any(value is None for value in checks.values()):
        return "INCONCLUSIVE"
    if all(checks.values()) and actual_decisions == expected_decisions:
        return "PASS"
    return "FAIL"


class LabTestCase(unittest.TestCase):
    def setUp(self):
        self.lab = LabFixture()

    def baseline(self, corr):
        return self.lab.observer.snapshot(corr)[0]

    def finalize(self, test_id, corr, before, expected, actual, checks, note=""):
        after, observer_event_id = self.lab.observer.snapshot(corr)
        events = self.lab.evidence.for_correlation(corr)
        checks = dict(checks)
        checks["observer_event_present"] = any(
            event["event_id"] == observer_event_id and event["operation"] == "observer.snapshot"
            for event in events
        )
        checks["correlated_attempt_and_decision_present"] = any(
            e["operation"] not in ("observer.snapshot",) for e in events
        )
        status = reconcile(expected, actual, before, after, checks)
        CASE_EVIDENCE[self.id()] = {
            "test_id": test_id,
            "test_method": self.id(),
            "correlation_id": corr,
            "expected_decisions": deepcopy(expected),
            "actual_decisions": deepcopy(actual),
            "disposition": status,
            "verification_checks": checks,
            "before": deepcopy(before),
            "after": deepcopy(after),
            "event_ids": [e["event_id"] for e in events],
            "events": deepcopy(events),
            "interpretation": note,
        }
        self.assertEqual(status, "PASS", "Expected and actual behavior or protected state differ")
        return after

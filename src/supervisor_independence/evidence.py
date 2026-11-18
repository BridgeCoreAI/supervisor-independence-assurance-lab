"""Append-only-in-use synthetic event collector; NOT tamper resistant."""

from copy import deepcopy


class EvidenceCollector:
    def __init__(self):
        self._events = []

    def record(self, correlation_id, actor, role, operation, decision, reason, details=None):
        event = {
            "event_id": "EVT-%04d" % (len(self._events) + 1),
            "correlation_id": correlation_id,
            "actor": actor,
            "role": role,
            "operation": operation,
            "decision": decision,
            "reason": reason,
            "details": deepcopy(details or {}),
        }
        self._events.append(event)
        return event["event_id"]

    def events(self):
        return deepcopy(self._events)

    def for_correlation(self, correlation_id):
        return [x for x in self.events() if x["correlation_id"] == correlation_id]

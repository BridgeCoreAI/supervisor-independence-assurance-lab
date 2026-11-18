"""Synthetic protected operation that rechecks authorization before update."""

from .types import Decision


class ProtectedExecutionService:
    def __init__(self, gate, exceptions, evidence):
        self._gate = gate
        self._exceptions = exceptions
        self._evidence = evidence
        self.__marker = "UNCHANGED"
        self.__count = 0

    def snapshot(self):
        return {"target_marker": self.__marker, "execution_count": self.__count}

    def execute(self, context, request, now, correlation_id):
        # The decision and mutation are consecutive in the deterministic fixture.
        # This is not a claim of distributed atomicity or TOCTOU resistance.
        gate_decision = self._gate.evaluate(context, request, now, correlation_id)
        outcome, reason = gate_decision.outcome, gate_decision.reason
        if outcome == "PERMIT" and gate_decision.reference_id:
            if not self._exceptions.consume(gate_decision.reference_id):
                outcome, reason = "DENY", "EXCEPTION_ALREADY_CONSUMED"
        if outcome == "PERMIT":
            self.__marker = request.proposed_marker
            self.__count += 1
        event_id = self._evidence.record(
            correlation_id, context.actor_id, context.role, "execution.apply",
            outcome, reason,
            {"request_id": request.request_id, "updated": outcome == "PERMIT",
             "gate_event_id": gate_decision.event_id}
        )
        return Decision(outcome, reason, event_id, correlation_id, gate_decision.reference_id)

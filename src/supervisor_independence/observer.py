"""Read-only state snapshots logically separate from the gate report."""

from copy import deepcopy


class IndependentStateObserver:
    def __init__(self, policy_store, exception_store, execution, evidence):
        self._policy = policy_store
        self._exceptions = exception_store
        self._execution = execution
        self._evidence = evidence

    def snapshot(self, correlation_id):
        policy = self._policy.snapshot()
        state = {
            "policy_version": policy["version"],
            "policy_digest": policy["digest"],
            "policy_bytes_hex": policy["canonical_bytes_hex"],
            "exception_records": self._exceptions.snapshot(),
            "exception_count": len(self._exceptions.snapshot()),
            **self._execution.snapshot(),
        }
        event_id = self._evidence.record(
            correlation_id, "OBSERVER", "read_only", "observer.snapshot", "OBSERVED",
            "STATE_CAPTURED", {"policy_digest": state["policy_digest"],
                               "exception_count": state["exception_count"],
                               "execution_count": state["execution_count"]}
        )
        return deepcopy(state), event_id

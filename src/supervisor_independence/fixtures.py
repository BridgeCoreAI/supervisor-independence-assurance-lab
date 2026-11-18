"""Fresh deterministic fixture per case; all data and identities are synthetic."""

from datetime import datetime, timedelta, timezone
from .authority import AuthorityResolver
from .evidence import EvidenceCollector
from .policy_store import PolicyStore
from .exception_store import ExceptionStore
from .gate import AuthorizationGate
from .execution import ProtectedExecutionService
from .observer import IndependentStateObserver
from .types import ActionRequest, ExceptionProposal, PolicyRevision


class LabFixture:
    NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)

    def __init__(self):
        self.authority = AuthorityResolver()
        self.evidence = EvidenceCollector()
        self.policy = PolicyStore(self.authority, self.evidence)
        self.exceptions = ExceptionStore(self.authority, self.evidence, self.policy)
        self.gate = AuthorizationGate(
            self.authority, self.policy, self.exceptions, self.evidence
        )
        self.executor = ProtectedExecutionService(self.gate, self.exceptions, self.evidence)
        self.observer = IndependentStateObserver(
            self.policy, self.exceptions, self.executor, self.evidence
        )

    def actor(self, actor_id):
        return self.authority.context(actor_id)

    def action_request(self, request_id="REQ-001", proposed_marker="UPDATED",
                       principal="AGENT-01", action="customer_record.update",
                       resource="CUST-TEST-001", expected_digest=None,
                       claimed_authority="", claimed_exception_id=""):
        return ActionRequest(
            request_id, principal, action, resource, proposed_marker,
            self.policy.snapshot()["digest"] if expected_digest is None else expected_digest,
            claimed_authority, claimed_exception_id
        )

    def exception_proposal(self, principal="AGENT-01", action="customer_record.update",
                           resource="CUST-TEST-001", valid_from=None, expires_at=None,
                           policy_digest=None, claimed_approver=""):
        return ExceptionProposal(
            principal, action, resource,
            self.policy.snapshot()["digest"] if policy_digest is None else policy_digest,
            self.NOW - timedelta(minutes=5) if valid_from is None else valid_from,
            self.NOW + timedelta(minutes=5) if expires_at is None else expires_at,
            claimed_approver
        )

    def policy_revision(self, version="policy-v2", allow_without_exception=True,
                        change_note="synthetic authorized change", claimed_administrator=""):
        baseline = self.policy.snapshot()
        return PolicyRevision(
            version, allow_without_exception, change_note,
            baseline["version"], baseline["digest"], claimed_administrator
        )

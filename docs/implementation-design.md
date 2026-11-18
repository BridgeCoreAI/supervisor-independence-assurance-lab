# GxE-CS-02 | Reference Implementation Design

**Author:** Grace Adjeli
**Organization:** BridgeCore AI
**Status:** Approved implementation design (2026-11-18); implementation and validation tracked separately
**Target branch:** dev
**Approved baselines:** docs/research-charter.md and docs/test-specifications.md

## 1. Objective

Implement a deterministic, synthetic Python reference lab that exercises the approved SUP-002, SUP-003, POS-002, POS-003, BYP-002, and BYP-003 scenarios. The lab must demonstrate whether an attempted unauthorized supervisor action produces an effective change, not merely whether an API returns DENY.

This is an application-level logical authorization experiment. It does not establish service or infrastructure isolation, independent cryptographic identity, tamper-proof evidence, or production readiness.

## 2. Trust and authority model

The test harness creates a trusted actor context that the request payload cannot modify. An actor's role is resolved by the authorization component; actor-supplied strings claiming to be an approver or policy administrator carry no authority.

Actor permissions:

| Actor | May propose agent action | May recommend review | May approve exception | May activate policy |
| --- | --- | --- | --- | --- |
| AGENT-01 | Yes | No | No | No |
| SUPERVISOR-01 | No | Yes | No | No |
| HUMAN-APPROVER-01 | No | No | Yes, within scope | No |
| POLICY-ADMIN-01 | No | No | No | Yes, with version checks |

All actor identities are synthetic. Production authentication, authorization and role provisioning are explicitly outside this reference lab.

## 3. Component design

| Component | Responsibility | Restriction or validation |
| --- | --- | --- |
| AuthorityResolver | Resolve trusted role for an actor context | Never accept a role or approval supplied inside a supervisor request as proof of authority |
| PolicyStore | Hold canonical effective policy bytes, version and SHA-256 digest | Reject unprivileged updates and unauthorized activations; issue new version and digest only for authorized revision |
| ExceptionStore | Hold narrowly scoped approved exceptions | Reject supervisor approvals; bind actor, action, resource, active policy digest, validity, approver and status |
| AuthorizationGate | Evaluate request against effective policy, role and applicable exception | Deny by default; approval recommendation alone never produces PERMIT |
| ProtectedExecutionService | Apply the synthetic customer record update | Recheck gate at the protected operation; DENY and HUMAN_REVIEW cannot update record or execution count |
| EvidenceCollector | Correlate attempted request, evaluation and execution result | Log what was reported, without claiming that log proves state |
| IndependentStateObserver | Read and compare policy, exception and execution state | Separate read-only interface; produce pre- and post-test snapshots used in assertions |
| TestRunner | Set fixtures, trusted actor contexts, test clock and deterministic identifiers | Reset all mutable state between tests and expose no alternate write path as a false assurance claim |

## 4. Synthetic data and reproducibility

- Resource: CUST-TEST-001.
- Action: customer_record.update.
- Principal: AGENT-01.
- Supervisor: SUPERVISOR-01.
- Initial policy version: policy-v1.
- Baseline policy: DENY the protected update unless a separately authorized, valid and matching exception exists.
- Clock: injected fixed UTC time in tests; no dependence on wall-clock timing.
- Policy digest: SHA-256 of canonical policy bytes, not solely a human-readable version label.
- Records: synthetic marker fields only; no customer data, network calls or real AI model.

Policy updates must be atomic with respect to their version and digest within the single-process fixture. This is not a claim about distributed-system race safety.

## 5. Decision and enforcement order

1. Receive a proposal or approval/policy-change request.
2. Resolve the actor from trusted test context.
3. Read the current effective policy and authorized exception records.
4. Apply role, scope, validity and policy-digest checks.
5. Return an explicit decision: PERMIT, DENY or HUMAN_REVIEW, with reason code.
6. For a permitted synthetic action, enforce authorization at the protected execution service before updating the record.
7. Observe the record, policy and exception state independently of the gate's reported result.
8. Correlate attempt, decision, enforcement outcome and state verification.

HUMAN_REVIEW stops execution. A separately approved exception requires a fresh gate evaluation and is never implicit permission.

## 6. Test mapping and minimum assertions

| Test | Act | Required assertions |
| --- | --- | --- |
| SUP-002 | SUPERVISOR-01 attempts self-approved exception, then protected update | DENY; no effective exception; record marker and execution count unchanged; policy unchanged |
| SUP-003 | SUPERVISOR-01 attempts permissive policy change/activation, then protected update | DENY; effective policy bytes, version and hash unchanged; protected update remains blocked |
| POS-002 | HUMAN-APPROVER-01 approves exact bounded exception; protected action is resubmitted | Matching unexpired request may PERMIT and execute once; mismatches, expiry and revocation do not permit |
| POS-003 | POLICY-ADMIN-01 activates valid versioned policy revision | Authorized new version and digest become effective; change attributable and test baseline reset |
| BYP-002 | Supervisor attempts alternate exposed exception write | Access refused or route shown absent; no effective exception; limit claim to interfaces actually exercised |
| BYP-003 | Supervisor attempts alternate exposed policy write | Access refused or route shown absent; unchanged effective bytes/version/digest; disclose other untested paths |

Each negative test must assert actual protected state rather than passing only because the gate returned DENY.

## 7. Proposed source layout

```text
src/supervisor_independence/
    __init__.py
    authority.py
    policy_store.py
    exception_store.py
    gate.py
    execution.py
    observer.py
    evidence.py
    fixtures.py

tests/
    test_sup002.py
    test_sup003.py
    test_positive_controls.py
    test_bypass_paths.py
    test_evidence_integrity.py

.github/workflows/
    validation.yml

docs/
    research-charter.md
    test-specifications.md
    implementation-design.md
    evidence-methodology.md
```

## 8. Evidence and continuous integration

Tests use the Python standard library and should run on Python 3.10 and 3.12 using:

```bash
python -m unittest discover -s tests -v
```

Each test produces an evidence record that distinguishes expected versus actual behavior and includes observed before/after state, decision and reason code, actor, request, policy version and digest, and correlated record IDs. A test is PASS only when all required independent state assertions succeed; if observation is missing, the test is INCONCLUSIVE.

In continuous integration, an evidence manifest should record the exact tested commit, Python version, workflow run ID and attempt, timestamp, test command, and SHA-256 of exported evidence artifacts. The manifest must not claim tests passed until completed run results exist. Repository commits and generated evidence artifacts must not contain credentials or customer data.

## 9. Failure criteria and limitations

Any unauthorized effective policy or exception change, or any prohibited customer record modification, is FAIL. Missing observation, invalid evidence correlation, or an unexamined alternate access path produces an explicit INCONCLUSIVE or scoped limitation, not a PASS.

This reference design does not demonstrate infrastructure isolation, cryptographically authenticated users, a tamper-resistant log against process compromise, physical or service-level independence, race resistance, or comprehensive agent prompt-injection protection. Any broader assurance claim requires additional tests and deployment evidence.

## 10. Review and development controls

The research charter, test specifications and implementation design were approved by Grace Adjeli on 2026-11-18. Changes are prepared for dev; no merge to main, public release, or article publication without Grace Adjeli's explicit approval. Commits are to be created through an author-controlled signing workflow; writing "Grace Adjeli" in metadata is not a substitute for GitHub verification.

**Governance is not what is defined. It is what is enforced at execution.**

Grace Adjeli | BridgeCore AI

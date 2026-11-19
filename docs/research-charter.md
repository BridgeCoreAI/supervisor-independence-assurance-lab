# GxE-CS-02 | Research Charter

**Research title:** When the AI Supervisor Becomes the Risk: Testing Independent Execution Governance  
**Project:** Supervisor Independence Assurance Lab  
**Author:** Grace Adjeli  
**Organization:** BridgeCore AI  
**Research scope:** GxE-CS-02 synthetic supervisor independence scenarios. See [validation results](validation-status.md).
**Repository:** BridgeCoreAI/supervisor-independence-assurance-lab  

## 1. Purpose and problem statement

An AI supervisor may monitor agent activity, identify policy violations, and recommend exceptions. If it can also approve its own exceptions or modify the rules governing its decisions, supervision does not establish independent enforcement. This lab tests whether a separate authorization mechanism rejects those attempts and whether independent state verification confirms that the protected assets remained unchanged.

## 2. Primary research question

Can an AI supervisor change the conditions under which its own behavior is governed, and can independent enforcement prevent and detect those attempts?

Supporting questions:

1. Can the supervisor create or approve an exception applicable to its own prohibited action?
2. Can the supervisor modify or activate the policy that constrains its decisions?
3. Does a denial correspond to an unchanged protected state and no prohibited execution?
4. Can separately authorized people make legitimate changes without granting those powers to the supervisor?

## 3. Initial research scope

The first phase tests only:

- **SUP-002:** Supervisor attempts to approve its own exception.
- **SUP-003:** Supervisor attempts to modify its governing policy.
- **Positive controls:** An authorized human approver may approve a narrowly scoped exception; an authorized policy administrator may update a policy using the required process.
- **Bypass probes:** Attempts to reach protected stores through paths other than the intended gate are rejected or demonstrably unavailable.

All actions, customer records, actor identities, and policies are synthetic. No live model, production system, customer data, external tool execution, or real approval is required.

## 4. Reference scenario and baseline

The synthetic AI agent requests `customer_record.update` for resource `CUST-TEST-001`. The baseline policy prohibits that action unless a separately authorized, valid, narrowly scoped exception is present. The supervisor can observe, evaluate, and recommend; it cannot approve the exception, administer the policy, or grant itself permissions.

For each attempt, capture the active policy version and SHA-256 digest, authorized exception state, and target record state before and after the request. A legitimate exception, if approved, must bind to the actor, exact action and resource, applicable policy version or digest, authorized approver, and validity period. A recommendation is not itself approval.

## 5. Actors and authority boundaries

| Actor or component | Permitted authority | Prohibited authority |
| --- | --- | --- |
| Operating AI agent | Propose a synthetic action | Directly bypass authorization and modify protected state |
| AI supervisor | Monitor, evaluate, recommend, and request review | Approve its own exception; administer effective policy; alter independent evidence |
| Authorized human approver | Approve or reject a bounded exception following required checks | Impersonate policy administration merely by holding approval authority |
| Authorized policy administrator | Propose and activate version-controlled policy changes | Ignore required change-control and integrity checks |
| Independent enforcement gate | Resolve trusted actor authority, evaluate current policy, and prevent unauthorized execution | Treat supervisor-supplied claims of approval as trusted credentials |
| Protected policy and exception stores | Apply authorized state changes | Accept writes solely because the supervisor requests them |
| Independent observer/evidence collector | Record attempts and decisions; inspect resulting protected state | Accept the gate decision as sole proof of execution outcome |

The gate and protected stores form a separate **logical authorization boundary** from the supervisor. Actual infrastructure-level independence would require different credentials or service identities, independent access controls, and separate deployment or storage protections; these are not assumed in a single-process reference lab.

## 6. Protected assets and threat model

Protected assets include active policy content, policy digest and version, approved exception records, permitted tool-execution state, and independent evidence records.

Threats in scope are self-authorization, unauthorized policy mutation, bypass of the intended API, and mismatch between reported decision and observed state. The test runner supplies trusted synthetic actor identities; the supervisor cannot designate itself as an approver or administrator by setting a request field.

Cryptographically authenticated identity, compromise of the host or test runner, malicious authorized administrators, production distributed-system races, and comprehensive adversarial prompt testing are outside the initial scope.

## 7. Control invariants and acceptance criteria

1. Supervisor-initiated exception approvals are denied regardless of the requested scope.
2. Supervisor-initiated policy writes or activations are denied.
3. Rejected changes leave effective policy content, version, digest, exception approvals, and prohibited execution state unchanged.
4. Denial is enforced at the protected operation; no alternate exposed path produces an equivalent unauthorized effect.
5. Legitimately authorized, narrowly scoped changes work and are recorded so the lab does not simply pass by rejecting everything.
6. Each attempt generates correlatable evidence of actor, request, decision, governing policy, observed state, and verification result.
7. A decision record is not accepted as proof unless the independently observed state supports it.
8. A human review response never authorizes execution by itself; a fresh valid approval and gate reevaluation are required.

## 8. Validation approach

Write expected outcomes before execution. Use deterministic Python standard-library tests and reproducible synthetic fixtures. Run negative, positive, and bypass tests, then independently compare pre-test and post-test policy, exception, and target-state snapshots. Distinguish **PASS**, **FAIL**, and **INCONCLUSIVE**. Retain test output, environment, tested commit, GitHub Actions run, and SHA-256 evidence digests.

Never mark an expected result as an observed result until tests have actually run. Any failure requires root-cause analysis, a correction, same-condition retesting, and regression testing before an assurance claim is restored.

## 9. Bounded assurance claim

If the tests pass, the lab may claim that the specified supervisor-originated attempts were rejected and that designated protected states remained unchanged **within the tested synthetic implementation and access paths**. It must not claim production deployment, universal bypass resistance, independent certification, or continuous protection of all AI agent systems.

**Governance is not what is defined. It is what is enforced at execution.**

Grace Adjeli | BridgeCore AI

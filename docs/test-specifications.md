# GxE-CS-02 | Test Specifications and Evidence Acceptance Criteria

**Author:** Grace Adjeli  
**Research scope:** Synthetic test design; see [validation results](validation-status.md) for recorded observations.
**Research baseline:** See `docs/research-charter.md`  

## 1. Shared synthetic fixtures

- `SUPERVISOR-01`: trusted test identity, role `supervisor`; may observe and recommend but not approve exceptions or change policies.
- `HUMAN-APPROVER-01`: trusted test identity, role `exception_approver`; may approve a valid scoped exception.
- `POLICY-ADMIN-01`: trusted test identity, role `policy_admin`; may activate authorized version-controlled policy changes.
- `AGENT-01`: proposed-action identity, with no direct write access to protected stores.
- Protected action: `customer_record.update`.
- Protected resource: `CUST-TEST-001`; data contains synthetic marker values only.
- Initial policy: action prohibited without valid, authorized exception; policy version `policy-v1` with a computed SHA-256 digest.
- Protected state: active policy bytes/version/digest, authorized exception entries, target-record marker, and tool execution count.

The test harness, not supervisor-controlled request fields, supplies actor identity and authority. This establishes logical separation only. Physical or service-level credential independence must be separately tested before being claimed.

## 2. Negative adversarial test: SUP-002

**Name:** Self-approved exception.  
**Hypothesis:** The supervisor cannot approve an exception that authorizes its own prohibited action.

**Arrange:** Store the baseline policy and empty approved-exception set. Capture policy digest, exception state, target-record marker, and execution count.

**Act:** Using trusted identity `SUPERVISOR-01`, request approval of an exception permitting `customer_record.update` on `CUST-TEST-001`. Then attempt execution using the purported exception.

**Expected gate result:** `DENY`, reason `UNAUTHORIZED_EXCEPTION_APPROVER` (or an equivalently defined explicit reason code).

**Required independent assertions:**

1. No approved exception was added or activated.
2. The proposed prohibited update did not execute; the target marker and tool execution count are unchanged.
3. Policy version and policy SHA-256 digest remain unchanged.
4. The attempt, denial, actor identity, and independently observed post-state are recorded and correlated.

**Fail if:** An exception becomes effective, the update executes, an authorized approval is inferred from the supervisor's self-assertion, or protected state cannot be verified. Record `INCONCLUSIVE` if verification evidence is missing rather than reporting a pass.

## 3. Negative adversarial test: SUP-003

**Name:** Unauthorized policy modification.  
**Hypothesis:** The supervisor cannot alter or activate the effective policy governing its decisions.

**Arrange:** Record exact active policy bytes, version `policy-v1`, SHA-256 digest, approved exceptions, and target record.

**Act:** Using trusted identity `SUPERVISOR-01`, attempt to replace the prohibited-action rule with a permissive rule, including a request to activate the modified policy.

**Expected gate result:** `DENY`, reason `UNAUTHORIZED_POLICY_ADMIN` (or a documented equivalent).

**Required independent assertions:**

1. Active policy bytes and SHA-256 digest equal the pre-test snapshot.
2. Active policy version remains `policy-v1`; an unauthorized revision has not become effective.
3. The proposed prohibited action remains blocked with no target-state modification.
4. The attempted change, gate decision, and independent state comparison appear in the evidence record.

**Fail if:** The policy is modified or activated, a prohibited action executes, or a write succeeds through another exposed path. Record `INCONCLUSIVE` if the actual effective state cannot be determined.

## 4. Positive-control tests

### POS-002: Authorized bounded exception

**Act:** Trusted `HUMAN-APPROVER-01` approves a narrowly scoped exception for the exact action/resource, principal, policy digest, and validity period. A permitted request is reevaluated through the gate.

**Expected:** Valid exception recorded with approver identity; a matching request may receive `PERMIT` and perform one synthetic update. Out-of-scope, expired, revoked, or mismatched requests must remain blocked or be routed to a new review as the specified policy requires. Approval alone must not bypass the gate.

### POS-003: Authorized policy administration

**Act:** Trusted `POLICY-ADMIN-01` activates a deliberate, versioned synthetic policy revision through the policy administration interface.

**Expected:** A distinct policy version and recomputed digest become active, with an attributable change record. A supervisor request cannot produce the same state change. Restore baseline between tests to prevent cross-test contamination.

## 5. Bypass probes

### BYP-002: Exception store direct-write attempt

The supervisor attempts to insert or activate an exception through an alternate accessible interface rather than the ordinary approval flow. **Expected:** No effective exception; denied attempt recorded. If the reference implementation offers no alternative interface, explicitly document the absence and do not claim operating-system isolation.

### BYP-003: Policy store direct-write attempt

The supervisor attempts to overwrite policy state directly, bypassing the versioned administration endpoint. **Expected:** Effective policy bytes, version, and digest remain unchanged; attempted access is rejected or proven inaccessible. A test that only invokes the gate cannot by itself establish this claim.

## 6. Required evidence for each test

Capture a structured record with:

- Test ID, expected outcome, actual result (`PASS`, `FAIL`, or `INCONCLUSIVE`), and reason for disposition.
- Trusted actor identity and role, attempted action and resource, and request identifier.
- Pre-test policy version and SHA-256 digest; post-test policy version and SHA-256 digest.
- Pre-test and post-test approved-exception counts or complete synthetic snapshots.
- Gate response and explicit reason code; whether human review was required.
- Before/after target-record marker and execution count, obtained by the independent verification component.
- Attempt, decision, enforcement, and observer record identifiers with a correlation ID.
- Tested commit SHA, Python version, test command, GitHub Actions run ID/attempt, timestamp, and evidence artifact SHA-256 digest.

The evidence collector's independence must be described accurately. In a single-process prototype it is a logically separate observer, not proof of protection against a compromised host or privileged process.

## 7. Evidence acceptance criteria

The minimum evidence package before reporting successful findings is:

1. SUP-002 and SUP-003 executed against the committed implementation with verified state comparisons.
2. POS-002 and POS-003 executed and documented to show permitted changes can succeed.
3. BYP-002 and BYP-003 executed or precisely scoped, with any inaccessible or untested bypass route disclosed.
4. Deterministic tests pass locally and in GitHub Actions, preferably on Python 3.10 and 3.12.
5. A commit-bound evidence manifest identifies the run, environment, tested code, and generated artifact hashes.

A test is not a `PASS` solely because the gate returned `DENY`; the protected-state assertion must also pass. Failures or incomplete observations must remain visible in the evidence report.

**Governance is not what is defined. It is what is enforced at execution.**

Grace Adjeli | BridgeCore AI

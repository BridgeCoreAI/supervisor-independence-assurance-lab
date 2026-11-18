# GxE-CS-02 | Evidence Methodology

**Author:** Grace Adjeli  
**Organization:** BridgeCore AI

## What constitutes evidence

Each adversarial test records the trusted synthetic actor, attempted operation, decision and explicit reason code, event correlation identifier, before/after protected state, and named verification checks.

The observer reads protected policy bytes, version and SHA-256 digest; approved exception records; target marker; and execution count. These observations are compared against the expected outcome. A DENY log without supporting state checks is not enough to support a PASS conclusion.

Case status is PASS only when both the expected outcomes and all required checks match. If protected state cannot be observed, the result is INCONCLUSIVE. If the observed state violates an expected invariant, the result is FAIL. The EVID-STATE test deliberately injects a state change from the trusted harness and checks that the reconciliation logic calls it FAIL. It is a test of the observer logic, not a demonstrated supervisor bypass.

## Reproducing a run

From the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/check_hygiene.py
python scripts/run_evidence.py
```

The run script generates `artifacts/test-evidence.json` and `artifacts/evidence-manifest.json`. The manifest includes the tested source-tree digest, the evidence artifact digest, Python version, environment, and a commit SHA **only when available**. In an uncommitted local copy, `tested_commit_sha` is null and the result cannot be called commit-bound.

A workflow run uses GitHub's `GITHUB_SHA`, `GITHUB_RUN_ID` and `GITHUB_RUN_ATTEMPT`. The evidence files can be downloaded from that run's artifacts after it completes. A successful local result does not establish successful continuous integration.

## Boundaries and missing assurance

- No real identity authentication: the test harness supplies roles.
- Logical separation only: Python storage is within the same process as the gate and observer.
- No tamper-proof logging: a process with full memory access could alter the in-memory collector.
- Direct-write bypass probes only cover exposed synthetic interfaces; they do not establish host, database, or service isolation.
- No model, prompt injection, distributed-system race, network API, or real customer action tested.
- The verification results are not an external audit or production certificate.

Report the actual results and limitations in the article after review. A published claim may be no stronger than the evidence supporting it.

**Governance is not what is defined. It is what is enforced at execution.**

Grace Adjeli | BridgeCore AI

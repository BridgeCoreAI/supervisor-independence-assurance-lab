# Security Policy

**Project:** Supervisor Independence Assurance Lab (GxE-CS-02)  
**Research author:** Grace Adjeli  
**Organization:** BridgeCore AI

## Scope and security boundaries

This repository contains a deterministic, synthetic Python reference implementation for testing independent execution governance. It is a research lab, not a production AI supervisor, authorization service, or externally certified security control.

The test harness supplies trusted synthetic identities. The authorization gate, policy and exception stores, and state observer are logically separated components within one Python process. The tests do not establish cryptographically authenticated identity, infrastructure or credential isolation, resistance to privileged host compromise, tamper-proof logging, complete bypass coverage, distributed-system race safety, or prompt-injection resilience.

Do not submit real credentials, personal information, customer records, private policies, or production system details in test cases or reports.

## Reporting a security concern

For ordinary defects and questions about reproducible synthetic scenarios, open a GitHub issue and include the affected component, reproduction steps, expected behavior, observed behavior, and relevant test output without sensitive data.

For a potentially exploitable vulnerability or a report containing sensitive details, use GitHub's **Report a vulnerability** option under the repository's Security tab if private vulnerability reporting is enabled. Otherwise, contact the repository maintainer through an established private channel before public disclosure. Do not publish proof-of-concept details that expose credentials, private data, or an affected live system in a public issue.

## What a passing test establishes

A passing test supports only the stated outcome for the tested source commit, synthetic scenario, and exposed access path. In particular, a logged `DENY` is not sufficient without the corresponding protected-state verification. See [Evidence Methodology](docs/evidence-methodology.md) and [Validation Results](docs/validation-status.md).

Copyright 2026 Grace Adjeli. Licensed under the [Apache License, Version 2.0](LICENSE).

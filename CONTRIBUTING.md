# Contributing

**Project:** Supervisor Independence Assurance Lab (GxE-CS-02)  
**Research author:** Grace Adjeli  
**Organization:** BridgeCore AI

Contributions that improve the reproducibility, clarity, and test coverage of the synthetic reference implementation are welcome for review. Submitting a contribution does not guarantee it will be incorporated.

## Research and data boundaries

- Use synthetic actors, policies, resources, and test records only. Do not include credentials, real customer data, or production access details.
- Preserve the distinction between supervisor recommendations, separately authorized human exceptions, policy administration, protected execution, and state observation.
- Do not expand assurance claims beyond the behaviors and access paths actually tested.
- Keep documentation aligned with implementation behavior and explicitly state any untested paths or limitations.

## Proposing a change

1. Open an issue describing the defect, control requirement, or proposed test, with a minimal synthetic reproduction when relevant.
2. Make the change on a topic branch and submit a pull request with a concise summary of the affected control or scenario.
3. Add or update relevant positive, negative, bypass, or evidence-integrity tests. A denied request must be checked against independently observed protected state, not solely a decision log.
4. Run the test suite, hygiene checker, and synthetic evidence generator from the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/check_hygiene.py
python scripts/run_evidence.py
```

5. Include the tested commit and test results in the pull request, describe limitations and any failed or inconclusive outcomes, and update research specifications or evidence documentation when behavior changes.

The reference implementation uses Python 3.10 or later and the standard library. Generated evidence is written to the ignored `artifacts/` directory. Do not commit generated evidence as though it were validated against a different source commit.

## Licensing and attribution

The repository is distributed under the [Apache License, Version 2.0](LICENSE). Retain applicable copyright, license, and notice information when redistributing or modifying licensed material. See [NOTICE](NOTICE).

Grace Adjeli is the author of the GxE-CS-02 research. Contributions should be attributed accurately to their actual contributors and must not misrepresent the research findings or provenance.

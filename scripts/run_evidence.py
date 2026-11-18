"""Execute tests and export honest, correlated local/CI evidence artifacts."""

import hashlib
import json
import os
import platform
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(ROOT / "src"))
import support  # noqa: E402


def clean_commit():
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"], "github_actions_checkout"
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        changes = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        if changes:
            return None, "working_tree_modified"
        return commit, "clean_local_git_checkout"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, "uncommitted_local_copy"


def source_digest():
    digest = hashlib.sha256()
    included = []
    for folder in ["src", "tests", "scripts", "docs", ".github"]:
        for path in sorted((ROOT / folder).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.suffix not in (".py", ".md", ".yml", ".yaml"):
                continue
            rel = str(path.relative_to(ROOT))
            included.append(rel)
            digest.update(rel.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest(), included


def main():
    suite = unittest.defaultTestLoader.discover(str(TESTS), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    failed = {str(test) for test, _ in result.failures + result.errors}
    by_test_id = {test.id() for test, _ in result.failures + result.errors}
    skipped_ids = {test.id() for test, _ in result.skipped}
    cases = []
    for method in sorted(set(support.CASE_EVIDENCE) | by_test_id | skipped_ids):
        row = support.CASE_EVIDENCE.get(method)
        if row is None:
            cases.append({
                "test_method": method,
                "disposition": "INCONCLUSIVE" if method not in by_test_id else "FAIL",
                "reason": "No complete independent observation captured",
            })
            continue
        row = dict(row)
        row["unittest_result"] = "FAIL" if method in by_test_id else (
            "SKIPPED" if method in skipped_ids else "PASS"
        )
        if row["unittest_result"] != "PASS" and row.get("disposition") == "PASS":
            row["disposition"] = "FAIL"
        cases.append(row)
    artifact = {
        "research_id": "GxE-CS-02",
        "author": "Grace Adjeli",
        "lab_scope": "Deterministic single-process synthetic reference, logical authorization only",
        "test_command": "python scripts/run_evidence.py",
        "tests_run": result.testsRun,
        "tests_passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "tests_failed": len(result.failures) + len(result.errors),
        "tests_skipped": len(result.skipped),
        "scenario_evidence": cases,
        "limitations": [
            "Test identities are trusted synthetic fixture inputs, not cryptographic credentials.",
            "Supervisor is a synthetic actor; no live LLM or agent runtime was tested.",
            "Python in-process stores and observer are not isolated from process compromise.",
            "Direct-write probes cover exposed test interfaces, not arbitrary memory access.",
            "No distributed synchronization, database isolation, or production traffic evaluated.",
        ],
    }
    output = ROOT / "artifacts"
    output.mkdir(exist_ok=True)
    evidence_path = output / "test-evidence.json"
    evidence_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_sha = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    commit, commit_state = clean_commit()
    tree_digest, included_paths = source_digest()
    manifest = {
        "research_id": "GxE-CS-02",
        "author": "Grace Adjeli",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": platform.platform(),
        "python_version": platform.python_version(),
        "test_command": "python scripts/run_evidence.py",
        "tested_commit_sha": commit,
        "tested_commit_state": commit_state,
        "source_tree_sha256": tree_digest,
        "source_tree_included_paths": included_paths,
        "github_actions_run_id": os.environ.get("GITHUB_RUN_ID") or None,
        "github_actions_attempt": os.environ.get("GITHUB_RUN_ATTEMPT") or None,
        "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF") or None,
        "test_evidence_filename": evidence_path.name,
        "test_evidence_sha256": evidence_sha,
        "tests_run": result.testsRun,
        "tests_failed": len(result.failures) + len(result.errors),
        "tests_skipped": len(result.skipped),
        "result": "PASS" if result.wasSuccessful() and len(cases) >= 8
                          and all(row.get("disposition") == "PASS" for row in cases)
                          else "NOT_ESTABLISHED",
        "claim_scope": "Local or CI test run of bounded synthetic reference implementation only",
    }
    (output / "evidence-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("\nEvidence files:", evidence_path, output / "evidence-manifest.json", file=sys.stderr)
    print("Commit evidence:", commit_state, commit or "unbound", file=sys.stderr)
    return 0 if manifest["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

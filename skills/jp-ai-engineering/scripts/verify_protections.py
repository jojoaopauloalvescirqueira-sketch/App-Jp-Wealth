#!/usr/bin/env python3
"""Fail-closed, stdlib-only gate for normalized test evidence.

API: evaluate(manifest, report, candidate, baseline=None) -> JSON-compatible dict.
CLI: python3 gate.py --manifest FILE --report FILE --candidate ID [--baseline FILE]
Exit 0 means PASS exclusively. Adapters run the project's actual test tools and
normalize their output; this module neither executes code nor calls a model.

Manifest v1 (all named fields mandatory unless marked optional)::
  {"schema_version": 1, "required_suites": ["unit-py312"],
   "protections": [{"id": "BUG-1", "kind": "regression", "source": "issue:1",
     "scope": "ledger", "required": true, "tests": ["test_deduplicate"],
     "suites": ["unit-py312"], "fingerprint": "sha256:..."}],
   "changes": [{"id": "BUG-1", "source": "approved-contract:2",
                "replacement_tests": ["test_replacement"]}]}
`suites`, `fingerprint`, and `changes` are optional. Scope is a nonempty string
or list of nonempty strings. Explicit suites bind every test ID to every named
environment; without binding, test IDs are checked across the report and every
occurrence must PASS. Matrix adapters should always provide explicit bindings.
Legacy protections may have required=false and tests=[]; they are NOT coverage.
Fingerprints are opaque hashes supplied by an adapter, not semantic proof.

Report v1::
  {"schema_version": 1, "candidate": "tree:...",
   "suites": [{"id": "unit-py312", "status": "PASS",
     "tests": [{"id": "test_deduplicate", "status": "PASS",
       "attempts": [{"status": "FAIL", "reason": "duplicate rows"},
                    {"status": "PASS"}]}]}],
   "baseline_failures": [],
   "environment": {"status": "available", "reason": "optional"}}
Only schema_version, candidate, suites and suite/test id/status/tests are
mandatory. Optional attempts are ordered oldest first on reports, suites or
tests. Any non-PASS attempt or timed_out=true prevents PASS, even after a retry.
Optional baseline_failures lists known failing IDs; unavailable environment
means ENVIRONMENT, not success. Missing report means NOT_RUN. Unknown/malformed
schemas mean INVALID_REPORT. Candidate identity must be computed externally
over actual source, test and configuration contents (a HEAD name is insufficient).

Baseline is a previous manifest, not previous execution evidence. Structural
removal, demotion, changed scopes/sources/bindings or fingerprints require review.
A change record permits replacement only with a nonempty normative source and
replacement cases that are currently required and pass; it is an audit record,
NOT proof of human authorization or equivalent semantics. The controller/reviewer
must authenticate approvals and check semantics. This gate trusts the adapter's
reports and cannot prevent a malicious report or prove arbitrary rule coverage.
"""
import argparse
import json
import pathlib
import sys

STATUSES = {"PASS", "FAIL", "SKIPPED", "XFAIL", "XPASS", "TODO", "UNKNOWN", "NOT_RUN", "TIMEOUT", "ERROR"}
PRIORITY = {"PASS": 0, "REVIEW_REQUIRED": 1, "FAIL": 2, "NOT_RUN": 3,
            "ENVIRONMENT": 4, "INVALID_REPORT": 5}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _status(value):
    return isinstance(value, str) and value in STATUSES


def _strings(value, allow_empty=False):
    return (isinstance(value, list) and (allow_empty or bool(value))
            and all(_text(item) for item in value) and len(set(value)) == len(value))


def _manifest_error(value):
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        return "Manifest schema_version must be 1"
    if not _strings(value.get("required_suites")):
        return "required_suites must be a nonempty unique list"
    if not isinstance(value.get("protections"), list):
        return "protections must be a list"
    seen = set()
    for protection in value["protections"]:
        if not isinstance(protection, dict):
            return "Protection must be an object"
        if not all(_text(protection.get(key)) for key in ("id", "kind", "source")):
            return "Protection id/kind/source must be nonempty strings"
        if protection["id"] in seen:
            return "Duplicate protection id"
        seen.add(protection["id"])
        scope = protection.get("scope")
        if not (_text(scope) or _strings(scope)):
            return "Protection scope must be nonempty"
        if type(protection.get("required")) is not bool:
            return "Protection required must be boolean"
        if not _strings(protection.get("tests"), allow_empty=not protection["required"]):
            return "Protection tests must be unique; required protections need test IDs"
        if "suites" in protection and (not _strings(protection["suites"])
                or not set(protection["suites"]).issubset(value["required_suites"])):
            return "Protection suites must bind to required_suites"
        if "fingerprint" in protection and not _text(protection["fingerprint"]):
            return "Protection fingerprint must be a nonempty string"
    if "changes" in value:
        if not isinstance(value["changes"], list):
            return "changes must be a list"
        changed_ids = set()
        for change in value["changes"]:
            if not isinstance(change, dict) or not all(_text(change.get(k)) for k in ("id", "source")):
                return "Changes require id and normative source"
            if change["id"] in changed_ids or not _strings(change.get("replacement_tests")):
                return "Changes require unique ids and real replacement case IDs"
            changed_ids.add(change["id"])
    return None


def _attempt_error(container):
    if "timed_out" in container and type(container["timed_out"]) is not bool:
        return "timed_out must be boolean"
    if "attempts" not in container:
        return None
    if not isinstance(container["attempts"], list) or not container["attempts"]:
        return "attempts must be a nonempty ordered list"
    for attempt in container["attempts"]:
        if not isinstance(attempt, dict) or not _status(attempt.get("status")):
            return "Attempt has invalid status"
        if "timed_out" in attempt and type(attempt["timed_out"]) is not bool:
            return "Attempt timed_out must be boolean"
    return None


def _report_error(value):
    if not isinstance(value, dict) or value.get("schema_version") != 1 or not _text(value.get("candidate")):
        return "Report requires schema_version=1 and candidate identity"
    if not isinstance(value.get("suites"), list):
        return "Report suites must be a list"
    error = _attempt_error(value)
    if error:
        return error
    seen_suites = set()
    for suite in value["suites"]:
        if not isinstance(suite, dict) or not _text(suite.get("id")) or not _status(suite.get("status")):
            return "Suite has invalid id/status"
        if suite["id"] in seen_suites or not isinstance(suite.get("tests"), list):
            return "Suite ids must be unique and tests must be a list"
        seen_suites.add(suite["id"])
        if _attempt_error(suite):
            return _attempt_error(suite)
        seen_tests = set()
        for test in suite["tests"]:
            if not isinstance(test, dict) or not _text(test.get("id")) or not _status(test.get("status")):
                return "Test has invalid id/status"
            if test["id"] in seen_tests:
                return "Duplicate test id within a suite"
            seen_tests.add(test["id"])
            if _attempt_error(test):
                return _attempt_error(test)
    if "baseline_failures" in value and not _strings(value["baseline_failures"], allow_empty=True):
        return "baseline_failures must be a unique list of IDs"
    if "environment" in value and (not isinstance(value["environment"], dict)
            or not isinstance(value["environment"].get("status"), str)
            or value["environment"].get("status") not in {"available", "unavailable"}):
        return "environment status must be available/unavailable"
    return None


def evaluate(manifest, report, candidate, baseline=None):
    """Return fail-closed status, issues and first observed failure; inputs untouched."""
    result = {"status": "PASS", "passed": True, "issues": [], "first_failure": None}

    def issue(status, code, message):
        result["issues"].append({"code": code, "message": message})
        if PRIORITY[status] > PRIORITY[result["status"]]:
            result["status"] = status
        result["passed"] = False

    error = _manifest_error(manifest)
    if error or not _text(candidate):
        issue("INVALID_REPORT", "INVALID_MANIFEST", error or "Expected candidate identity is required")
        return result
    if baseline is not None and _manifest_error(baseline):
        issue("INVALID_REPORT", "INVALID_BASELINE", _manifest_error(baseline))
        return result
    if report is None:
        issue("NOT_RUN", "MISSING_REPORT", "No execution report was provided")
        return result
    error = _report_error(report)
    if error:
        issue("INVALID_REPORT", "INVALID_REPORT", error)
        return result
    if report["candidate"] != candidate:
        issue("FAIL", "STALE_CANDIDATE", "Report identity differs from the actual candidate")
    if report.get("environment", {}).get("status") == "unavailable":
        issue("ENVIRONMENT", "UNAVAILABLE_RUNTIME", report["environment"].get("reason", "Runtime unavailable"))
    if report.get("baseline_failures"):
        issue("FAIL", "BASELINE_FAILURE", "Preexisting failures remain: " + ", ".join(report["baseline_failures"]))

    suites = {suite["id"]: suite for suite in report["suites"]}
    test_occurrences = {}
    for suite in report["suites"]:
        for test in suite["tests"]:
            test_occurrences.setdefault(test["id"], []).append((suite["id"], test))

    def inspect_attempts(container, identifier):
        if container.get("timed_out"):
            failure = {"id": identifier, "status": "TIMEOUT", "timed_out": True}
            if result["first_failure"] is None:
                result["first_failure"] = failure
            issue("FAIL", "TIMEOUT", identifier + " timed out")
        for number, attempt in enumerate(container.get("attempts", []), 1):
            if attempt["status"] != "PASS" or attempt.get("timed_out"):
                if result["first_failure"] is None:
                    result["first_failure"] = dict(attempt, id=identifier, attempt=number)
                issue("FAIL", "FAILED_ATTEMPT", identifier + " has a nonpassing earlier attempt")

    inspect_attempts(report, "report")
    for suite in report["suites"]:
        inspect_attempts(suite, suite["id"])
        for test in suite["tests"]:
            inspect_attempts(test, suite["id"] + "::" + test["id"])
    for suite_id in manifest["required_suites"]:
        if suite_id not in suites:
            issue("NOT_RUN", "MISSING_SUITE", "Required suite missing: " + suite_id)
            continue
        suite = suites[suite_id]
        if not suite["tests"]:
            issue("NOT_RUN", "EMPTY_SUITE", "Required suite collected zero cases: " + suite_id)
        if suite["status"] != "PASS":
            issue("FAIL", "SUITE_NOT_PASS", suite_id + ": " + suite["status"])
        for test in suite["tests"]:
            if test["status"] in {"FAIL", "ERROR", "TIMEOUT", "UNKNOWN"}:
                issue("FAIL", "SUITE_CASE_FAILURE", suite_id + "::" + test["id"] + ": " + test["status"])
                if result["first_failure"] is None:
                    result["first_failure"] = {"id": suite_id + "::" + test["id"], "status": test["status"]}
    required_test_ids = set()
    for protection in manifest["protections"]:
        if not protection["required"]:
            continue
        required_test_ids.update(protection["tests"])
        for test_id in protection["tests"]:
            occurrences = test_occurrences.get(test_id, [])
            if not occurrences:
                issue("FAIL", "MISSING_TEST", protection["id"] + " missing case " + test_id)
            for suite_id in protection.get("suites", []):
                if not any(sid == suite_id for sid, _ in occurrences):
                    issue("FAIL", "MISSING_MATRIX_CASE", test_id + " missing from " + suite_id)
            for suite_id, test in occurrences:
                if test["status"] != "PASS":
                    issue("FAIL", "TEST_NOT_PASS", suite_id + "::" + test_id + ": " + test["status"])
                    if result["first_failure"] is None:
                        result["first_failure"] = {"id": suite_id + "::" + test_id, "status": test["status"]}

    changes = {change["id"]: change for change in manifest.get("changes", [])}
    authorized = set()
    for protection_id, change in changes.items():
        replacements = change["replacement_tests"]
        if (not set(replacements).issubset(required_test_ids)
                or any(not test_occurrences.get(tid) or any(test["status"] != "PASS"
                       for _, test in test_occurrences[tid]) for tid in replacements)):
            issue("REVIEW_REQUIRED", "UNPROVEN_REPLACEMENT", protection_id + " replacements are not required passing cases")
        else:
            authorized.add(protection_id)
    if baseline is not None:
        current = {protection["id"]: protection for protection in manifest["protections"]}
        if not set(baseline["required_suites"]).issubset(manifest["required_suites"]):
            issue("REVIEW_REQUIRED", "REMOVED_SUITE", "Previously required suite removed")
        for old in baseline["protections"]:
            new = current.get(old["id"])
            changed = (new is None or not set(old["tests"]).issubset(new["tests"])
                       or old["scope"] != new["scope"] or old["source"] != new["source"]
                       or old["kind"] != new["kind"]
                       or (old["required"] and not new["required"])
                       or old.get("fingerprint") != new.get("fingerprint")
                       or not set(old.get("suites", [])).issubset(new.get("suites", [])))
            if changed and old["id"] not in authorized:
                issue("REVIEW_REQUIRED", "CHANGED_PROTECTION", old["id"] + " removed, reduced or changed; semantic review required")
    return result


def main(argv=None):
    """Read JSON inputs, print one JSON result and fail closed on missing/bad files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
        baseline = json.loads(pathlib.Path(args.baseline).read_text(encoding="utf-8")) if args.baseline else None
        try:
            report = json.loads(pathlib.Path(args.report).read_text(encoding="utf-8"))
        except FileNotFoundError:
            report = None
        result = evaluate(manifest, report, args.candidate, baseline)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "INVALID_REPORT", "passed": False,
                  "issues": [{"code": "INPUT_ERROR", "message": str(exc)}], "first_failure": None}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check formal eligibility for the Harness historical-failure audit finding.

This is deliberately a *non-approving* check. It validates a synthetic or
documented audit dossier's structure and declared constraints. It cannot verify
the truth of a receipt, judge functional equivalence or accept residual risk.
Only an independent auditor can make those judgments under the canonical
Harness policy. In particular, this module never changes a raw test result or
calls a failing quality gate green. Policy activation fields are declarations;
the auditor must verify the actual audit, acceptance, integration and external
Harness activation receipts before applying the policy to a product candidate.
"""

import argparse
import json
from pathlib import Path
import re


POLICY_VERSION = "jp-harness/historical-unresolved-failure/v1"
POLICY_CHG_ID = "CHG-HARNESS-HISTORICAL-UNRESOLVED-FAILURE-20260925"
ELIGIBLE = "ELIGIBILITY_CONDITIONS_SATISFIED"
INELIGIBLE = "INELIGIBLE"
PROMOTION_PREREQUISITES = "PROMOTION_PREREQUISITES_SATISFIED_NOT_APPROVAL"
PROMOTION_BLOCKED = "PROMOTION_BLOCKED"
ACTION_AUTHORIZATIONS = {
    "commit": "commit_authorized",
    "push": "push_authorized",
    "merge": "merge_authorized",
    "deploy": "deploy_authorized",
}

CRITICAL_RELATIONS = (
    "security", "authentication", "authorization", "secrets",
    "financial_integrity", "normative_rules", "persistence", "identity",
    "migration", "data_loss_or_corruption", "critical_backup_restore",
    "irreversible_operation",
)
SAFE_DOMAINS = frozenset({
    "presentation_noncritical", "navigation_noncritical",
    "copy_noncritical",
})
SIGNAL_KINDS = frozenset({
    "functional_focal", "invariant", "flow_inspection", "state_check",
    "nearby_regression",
})
FINDING_SEVERITIES = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW", "COSMETIC"})
DELTA_PARTS = (
    "diff", "consumers", "call_flow", "loading", "lifecycle",
    "indirect_effects", "relation_to_failure",
)
DEBT_TEXT = (
    "original_test_id", "symptom", "missing_historical_observation",
    "residual_risk", "policy_version",
)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _revision(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", value))


def _receipt(value):
    return isinstance(value, dict) and _text(value.get("path")) and _sha(value.get("sha256"))


def _bound_receipt(value, source_hash, control_plane_fingerprint):
    return (_receipt(value) and value.get("chg_id") == POLICY_CHG_ID
            and value.get("policy_version") == POLICY_VERSION
            and value.get("canonical_source_sha256") == source_hash
            and value.get("control_plane_candidate_fingerprint") == control_plane_fingerprint)


def _activation_errors(value):
    """Validate the declared activation chain; do not attest its truth."""
    if not isinstance(value, dict):
        return ["POLICY_ACTIVATION_MISSING"]
    errors = []
    if value.get("chg_id") != POLICY_CHG_ID:
        errors.append("ACTIVATION_CHG_MISMATCH")
    if value.get("policy_version") != POLICY_VERSION:
        errors.append("ACTIVATION_POLICY_VERSION_MISMATCH")
    source_hash = value.get("final_canonical_source_sha256")
    control_plane_fingerprint = value.get("control_plane_candidate_fingerprint")
    if not _sha(control_plane_fingerprint):
        errors.append("ACTIVATION_CONTROL_PLANE_FINGERPRINT_INCOMPLETE")
    source = value.get("canonical_source")
    if not (_sha(source_hash) and _receipt(source)
            and Path(source.get("path")).is_absolute()
            and source.get("sha256") == source_hash):
        errors.append("ACTIVATION_CANONICAL_SOURCE_INCOMPLETE")
    audit = value.get("control_plane_audit")
    if not (_bound_receipt(audit, source_hash, control_plane_fingerprint)
            and audit.get("verdict") in {"AUDIT_PASS", "AUDIT_PASS_WITH_DEBT"}
            and _text(audit.get("auditor_id"))
            and _text(audit.get("executor_id"))
            and audit.get("auditor_id") != audit.get("executor_id")
            and audit.get("independent") is True):
        errors.append("ACTIVATION_AUDIT_INCOMPLETE")
    acceptance = value.get("human_acceptance")
    if not (_bound_receipt(acceptance, source_hash, control_plane_fingerprint)
            and _text(acceptance.get("owner_id"))):
        errors.append("ACTIVATION_HUMAN_ACCEPTANCE_MISSING")
    integration = value.get("repository_integration")
    if not (_bound_receipt(integration, source_hash, control_plane_fingerprint)
            and _revision(integration.get("commit"))
            and _bound_receipt(integration.get("authorization_receipt"), source_hash,
                               control_plane_fingerprint)):
        errors.append("ACTIVATION_REPO_INTEGRATION_MISSING")
    if not _bound_receipt(value.get("external_harness_activation"), source_hash,
                          control_plane_fingerprint):
        errors.append("ACTIVATION_EXTERNAL_HARNESS_MISSING")
    return errors


def _file_capture(receipt, prefix):
    """An old run may have no captured stream; absence must be explicit."""
    path, digest, reason = (receipt.get(prefix + suffix) for suffix in (
        "_path", "_sha256", "_unavailable_reason"))
    return ((_text(path) and _sha(digest) and reason is None)
            or (path is None and digest is None and _text(reason)))


def _exit_capture(receipt):
    code, reason = receipt.get("exit_code"), receipt.get("exit_code_unavailable_reason")
    return ((isinstance(code, int) and not isinstance(code, bool)
             and code != 0 and reason is None)
            or (code is None and _text(reason)))


def _identity(value):
    if not isinstance(value, dict):
        return False
    if not (_text(value.get("candidate")) and _revision(value.get("source_revision"))
            and _text(value.get("build_id")) and _sha(value.get("fingerprint"))):
        return False
    artifacts = value.get("artifacts")
    return (isinstance(artifacts, dict) and bool(artifacts)
            and all(_text(path) and _sha(digest)
                    for path, digest in artifacts.items()))


def evaluate(dossier):
    """Return (eligibility label, reason codes); never an audit verdict.

    Evidence and independence are *declared* here. The auditor must inspect
    the actual receipts, candidate bytes, causal relevance and residual risk.
    """
    if not isinstance(dossier, dict):
        return INELIGIBLE, ["DOSSIER_INVALID"]
    errors = []

    def require(condition, reason):
        if not condition:
            errors.append(reason)

    require(dossier.get("finding_type") == "HISTORICAL_UNRESOLVED_FAILURE",
            "FINDING_TYPE_INVALID")
    require(dossier.get("policy_version") == POLICY_VERSION,
            "POLICY_VERSION_INVALID")
    errors.extend(_activation_errors(dossier.get("policy_activation")))
    for field in DEBT_TEXT:
        require(_text(dossier.get(field)), "MISSING_" + field.upper())

    # A. One frozen identity must cover original, subsequent and current states.
    identity = dossier.get("candidate_identity")
    require(_identity(identity), "CANDIDATE_IDENTITY_INCOMPLETE")
    require(dossier.get("candidate_frozen") is True, "CANDIDATE_NOT_FROZEN")
    require(dossier.get("material_change_since_evidence") is False,
            "CANDIDATE_CHANGED_AFTER_EVIDENCE")
    require(dossier.get("change_after_opinion") is False,
            "CANDIDATE_CHANGED_AFTER_OPINION")
    for field in ("original_candidate_identity", "current_candidate_identity"):
        require(_identity(dossier.get(field)) and dossier.get(field) == identity,
                field.upper() + "_MISMATCH")

    # B. The raw failure and its original outputs remain identifiable.
    receipt = dossier.get("original_receipt")
    receipt = receipt if isinstance(receipt, dict) else {}
    require(_text(receipt.get("path")) and _sha(receipt.get("sha256"))
            and _file_capture(receipt, "stdout")
            and _file_capture(receipt, "stderr")
            and _exit_capture(receipt)
            and _text(receipt.get("limitations"))
            and isinstance(receipt.get("prior_audits"), list),
            "ORIGINAL_RECEIPT_INCOMPLETE")
    require(receipt.get("result") == "PRODUCT_FAIL"
            and dossier.get("original_result") == "PRODUCT_FAIL"
            and dossier.get("raw_gate_result") == "PRODUCT_FAIL",
            "RAW_PRODUCT_FAIL_NOT_PRESERVED")
    require(dossier.get("historical_records_unchanged") is True,
            "HISTORICAL_RECORDS_CHANGED")
    require(dossier.get("provenance_sufficient") is True,
            "PROVENANCE_INSUFFICIENT")

    # C and E. A complete focal plus an independent non-focal signal are
    # mandatory. Repeated runs of the same focal are not independent signals.
    equivalence = dossier.get("equivalence_assessment")
    equivalence = equivalence if isinstance(equivalence, dict) else {}
    require(_text(equivalence.get("comparison"))
            and all(equivalence.get(k) is True for k in (
                "equivalent_or_stronger", "observation_before_navigation",
                "oracle_not_weakened", "timeout_not_increased", "retry_not_added",
                "no_mock_substitution", "instrumentation_timing_reviewed",
                "observability_sufficient")), "COUNTEREVIDENCE_NOT_EQUIVALENT")
    require(dossier.get("failure_reproducible") is False,
            "FAILURE_REPRODUCIBLE")
    require(dossier.get("later_relevant_failure") is False,
            "LATER_RELEVANT_FAILURE")
    signals = dossier.get("subsequent_evidence")
    signals = signals if isinstance(signals, list) else []
    valid_signals = []
    for signal in signals:
        if (isinstance(signal, dict) and _text(signal.get("id"))
                and _text(signal.get("source_id"))
                and isinstance(signal.get("kind"), str)
                and signal.get("kind") in SIGNAL_KINDS
                and _sha(signal.get("receipt_sha256"))
                and _text(signal.get("method"))
                and signal.get("passed") is True
                and _identity(signal.get("candidate_identity"))
                and signal.get("candidate_identity") == identity):
            valid_signals.append(signal)
    require(len(valid_signals) == len(signals) and len(valid_signals) >= 2,
            "SUBSEQUENT_EVIDENCE_INCOMPLETE")
    focal = [s for s in valid_signals if s["kind"] == "functional_focal"]
    require(bool(focal), "FUNCTIONAL_FOCAL_MISSING")
    require(any(s["kind"] != "functional_focal"
                and s["source_id"] != f["source_id"]
                and s["receipt_sha256"] != f["receipt_sha256"]
                for s in valid_signals for f in focal),
            "INDEPENDENT_SIGNAL_MISSING")

    # D. Review the full relationship, not just whether a file changed.
    delta = dossier.get("delta_relevance_assessment")
    delta = delta if isinstance(delta, dict) else {}
    require(all(_text(delta.get(k)) for k in DELTA_PARTS)
            and delta.get("plausible_relation_reviewed") is True,
            "DELTA_REVIEW_INCOMPLETE")

    # F. This first version is restricted to N0/N1 and noncritical domains.
    require(dossier.get("risk_level") in ("N0-D", "N0-V", "N1"),
            "RISK_CLASS_OUT_OF_SCOPE")
    affected = dossier.get("affected_property")
    affected = affected if isinstance(affected, dict) else {}
    require(_text(affected.get("name"))
            and isinstance(affected.get("domain"), str)
            and affected.get("domain") in SAFE_DOMAINS
            and affected.get("critical") is False,
            "CRITICAL_OR_UNCLASSIFIED_PROPERTY")
    relations = dossier.get("critical_domain_relations")
    relations = relations if isinstance(relations, dict) else {}
    require(set(relations) == set(CRITICAL_RELATIONS)
            and all(relations.get(k) is False for k in CRITICAL_RELATIONS),
            "CRITICAL_DOMAIN_RELATION")
    findings = dossier.get("pertinent_findings")
    require(isinstance(findings, list)
            and all(isinstance(f, dict)
                    and isinstance(f.get("severity"), str)
                    and f.get("severity") in FINDING_SEVERITIES
                    for f in findings),
            "FINDING_SEVERITY_INVALID")
    require(isinstance(findings, list)
            and not any(isinstance(f, dict)
                        and isinstance(f.get("severity"), str)
                        and f.get("severity") in {"HIGH", "CRITICAL"}
                        for f in findings),
            "HIGH_OR_CRITICAL_FINDING")

    # G and H. Identity is an attestation to inspect, not proof by this code.
    auditor = dossier.get("auditor_identity")
    executor = dossier.get("executor_identity")
    auditor = auditor if isinstance(auditor, dict) else {}
    executor = executor if isinstance(executor, dict) else {}
    require(_text(auditor.get("id")) and _text(executor.get("id"))
            and auditor.get("id") != executor.get("id")
            and auditor.get("role") == "independent_auditor"
            and auditor.get("independence_attested") is True
            and _sha(auditor.get("attestation_sha256")),
            "AUDITOR_NOT_INDEPENDENT_DECLARED")
    require(_text(dossier.get("residual_risk"))
            and isinstance(dossier.get("reopening_triggers"), list)
            and bool(dossier.get("reopening_triggers"))
            and all(_text(x) for x in dossier.get("reopening_triggers", [])
                    if isinstance(dossier.get("reopening_triggers"), list)),
            "DEBT_NOT_TRACEABLE")
    require(dossier.get("final_disposition") == "AUDIT_PASS_WITH_DEBT",
            "DISPOSITION_EXCEEDS_POLICY")
    return (INELIGIBLE, errors) if errors else (ELIGIBLE, [])


def promotion_prerequisites(dossier, action):
    """Check one explicit stage; success is still not an authorization.

    Authorizing commit does not authorize push, merge or deploy. This reads
    declarations only; the actual human acceptance and action authorization
    receipts must be independently verified before any operation.
    """
    if not isinstance(action, str) or action not in ACTION_AUTHORIZATIONS:
        return PROMOTION_BLOCKED, ["ACTION_UNSUPPORTED"]
    outcome, errors = evaluate(dossier)
    if outcome != ELIGIBLE:
        return PROMOTION_BLOCKED, errors
    for key, reason in (
            ("human_acceptance_recorded", "HUMAN_ACCEPTANCE_MISSING"),
            (ACTION_AUTHORIZATIONS[action], action.upper() + "_AUTHORIZATION_MISSING"),
            ("other_integration_gates_satisfied", "OTHER_GATES_UNSATISFIED")):
        if dossier.get(key) is not True:
            errors.append(reason)
    return (PROMOTION_BLOCKED, errors) if errors else (PROMOTION_PREREQUISITES, [])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path, help="JSON audit dossier; read only")
    args = parser.parse_args(argv)
    try:
        dossier = json.loads(args.dossier.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": INELIGIBLE, "reasons": ["DOSSIER_UNREADABLE"],
                          "detail": str(exc)}, ensure_ascii=False))
        return 2
    status, reasons = evaluate(dossier)
    print(json.dumps({"status": status, "reasons": reasons,
                      "scope": "one historical audit finding only",
                      "audit_verdict": None,
                      "raw_gate_result": "PRODUCT_FAIL"}, ensure_ascii=False))
    return 0 if status == ELIGIBLE else 1


if __name__ == "__main__":
    raise SystemExit(main())

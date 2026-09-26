#!/usr/bin/env python3
"""Synthetic negative controls for the historical-failure audit policy.

Run: python3 tools/historical_failure_audit_policy_test.py
No product candidate, real receipt, browser, network or quality gate is used.
"""

import copy
import unittest

from historical_failure_audit_policy import (
    ACTION_AUTHORIZATIONS, CRITICAL_RELATIONS, ELIGIBLE, INELIGIBLE, PROMOTION_BLOCKED,
    POLICY_CHG_ID, POLICY_VERSION, PROMOTION_PREREQUISITES, evaluate,
    promotion_prerequisites,
)


def identity():
    return {
        "candidate": "synthetic-navigation-r1",
        "source_revision": "a" * 40,
        "build_id": "synthetic-build-1",
        "fingerprint": "b" * 64,
        "artifacts": {"index.html": "c" * 64},
    }


def synthetic_future_activation():
    """Hypothetical post-integration chain, never a claim about this CHG today."""
    source_hash = "4" * 64
    control_plane_fingerprint = "0" * 64

    def receipt(name, digest):
        return {
            "path": "/synthetic/future/" + name,
            "sha256": digest * 64,
            "chg_id": POLICY_CHG_ID,
            "policy_version": POLICY_VERSION,
            "canonical_source_sha256": source_hash,
            "control_plane_candidate_fingerprint": control_plane_fingerprint,
        }

    audit = receipt("control-plane-audit.json", "5")
    audit["verdict"] = "AUDIT_PASS"
    audit["auditor_id"] = "synthetic-independent-auditor"
    audit["executor_id"] = "synthetic-control-plane-executor"
    audit["independent"] = True
    acceptance = receipt("owner-acceptance.json", "6")
    acceptance["owner_id"] = "synthetic-owner"
    integration = receipt("repository-integration.json", "7")
    integration["commit"] = "a" * 40
    integration["authorization_receipt"] = receipt("integration-authorization.json", "8")
    return {
        "chg_id": POLICY_CHG_ID,
        "policy_version": POLICY_VERSION,
        "final_canonical_source_sha256": source_hash,
        "control_plane_candidate_fingerprint": control_plane_fingerprint,
        "canonical_source": {"path": "/synthetic/future/Harness.md", "sha256": source_hash},
        "control_plane_audit": audit,
        "human_acceptance": acceptance,
        "repository_integration": integration,
        "external_harness_activation": receipt("external-harness-activation.json", "9"),
    }


def valid_dossier():
    frozen = identity()
    return {
        "finding_type": "HISTORICAL_UNRESOLVED_FAILURE",
        "policy_version": POLICY_VERSION,
        "policy_activation": synthetic_future_activation(),
        "original_test_id": "synthetic-mobile-navigation",
        "original_receipt": {
            "path": "receipts/original.json", "sha256": "d" * 64,
            "result": "PRODUCT_FAIL", "exit_code": 1,
            "stdout_path": "receipts/original.stdout", "stdout_sha256": "e" * 64,
            "stderr_path": "receipts/original.stderr", "stderr_sha256": "f" * 64,
            "limitations": "The failure occurred before the browser evaluation marker.",
            "prior_audits": ["receipts/audit-original.md"],
        },
        "original_result": "PRODUCT_FAIL",
        "raw_gate_result": "PRODUCT_FAIL",
        "historical_records_unchanged": True,
        "symptom": "A required navigation binding was absent at use.",
        "missing_historical_observation": "The original response completion was not captured.",
        "candidate_identity": frozen,
        "original_candidate_identity": copy.deepcopy(frozen),
        "current_candidate_identity": copy.deepcopy(frozen),
        "candidate_frozen": True,
        "material_change_since_evidence": False,
        "change_after_opinion": False,
        "provenance_sufficient": True,
        "subsequent_evidence": [
            {"id": "focal-1", "kind": "functional_focal", "source_id": "browser-run-1",
             "receipt_sha256": "1" * 64, "method": "Complete real navigation and action",
             "passed": True, "candidate_identity": copy.deepcopy(frozen)},
            {"id": "invariant-1", "kind": "invariant", "source_id": "source-review-1",
             "receipt_sha256": "2" * 64, "method": "Independent binding invariant",
             "passed": True, "candidate_identity": copy.deepcopy(frozen)},
        ],
        "equivalence_assessment": {
            "comparison": "The same action and oracle were used; current capture began before load.",
            "equivalent_or_stronger": True,
            "observation_before_navigation": True,
            "oracle_not_weakened": True,
            "timeout_not_increased": True,
            "retry_not_added": True,
            "no_mock_substitution": True,
            "instrumentation_timing_reviewed": True,
            "observability_sufficient": True,
        },
        "failure_reproducible": False,
        "later_relevant_failure": False,
        "delta_relevance_assessment": {
            "diff": "Changed header event binding reviewed line by line.",
            "consumers": "All four navigation layouts inspected.",
            "call_flow": "Click through close flow traced.",
            "loading": "Script request and evaluation order compared.",
            "lifecycle": "Open and close lifecycle traced.",
            "indirect_effects": "Shared helpers and focus effects inspected.",
            "relation_to_failure": "Possible shared binding relationship assessed.",
            "plausible_relation_reviewed": True,
        },
        "risk_level": "N1",
        "affected_property": {"name": "visual menu selection",
                              "domain": "navigation_noncritical", "critical": False},
        "critical_domain_relations": {key: False for key in CRITICAL_RELATIONS},
        "pertinent_findings": [],
        "residual_risk": "The original one-time failure mechanism remains unknown.",
        "reopening_triggers": ["The action fails on the same frozen candidate."],
        "executor_identity": {"id": "executor-synthetic"},
        "auditor_identity": {"id": "auditor-synthetic", "role": "independent_auditor",
                             "independence_attested": True,
                             "attestation_sha256": "3" * 64},
        "final_disposition": "AUDIT_PASS_WITH_DEBT",
        "human_acceptance_recorded": False,
        "commit_authorized": False,
        "push_authorized": False,
        "merge_authorized": False,
        "deploy_authorized": False,
        "other_integration_gates_satisfied": False,
    }


def unsafe_green_focal_rule(dossier):
    """Illustrative permissive rule; negative controls must reject its cases."""
    return any(e.get("kind") == "functional_focal" and e.get("passed") is True
               for e in dossier.get("subsequent_evidence", []))


class HistoricalFailurePolicyTests(unittest.TestCase):
    def assert_blocked(self, dossier, reason):
        self.assertTrue(unsafe_green_focal_rule(dossier),
                        "negative control must fool the permissive comparator")
        status, reasons = evaluate(dossier)
        self.assertEqual(INELIGIBLE, status)
        self.assertIn(reason, reasons)

    def test_T1_reproducible_product_failure(self):
        d = valid_dossier()
        d["failure_reproducible"] = True
        self.assert_blocked(d, "FAILURE_REPRODUCIBLE")

    def test_T2_changed_candidate(self):
        d = valid_dossier()
        d["current_candidate_identity"]["fingerprint"] = "9" * 64
        self.assert_blocked(d, "CURRENT_CANDIDATE_IDENTITY_MISMATCH")

    def test_T3_critical_domain(self):
        for domain in CRITICAL_RELATIONS:
            with self.subTest(domain=domain):
                d = valid_dossier()
                d["critical_domain_relations"][domain] = True
                self.assert_blocked(d, "CRITICAL_DOMAIN_RELATION")
        d = valid_dossier()
        d["affected_property"]["critical"] = True
        self.assert_blocked(d, "CRITICAL_OR_UNCLASSIFIED_PROPERTY")
        d = valid_dossier()
        d["affected_property"]["domain"] = "test_observability_noncritical"
        self.assert_blocked(d, "CRITICAL_OR_UNCLASSIFIED_PROPERTY")

    def test_T4_weaker_followup(self):
        for field in ("timeout_not_increased", "retry_not_added", "oracle_not_weakened",
                      "no_mock_substitution", "instrumentation_timing_reviewed"):
            with self.subTest(field=field):
                d = valid_dossier()
                d["equivalence_assessment"][field] = False
                self.assert_blocked(d, "COUNTEREVIDENCE_NOT_EQUIVALENT")

    def test_T5_one_green_focal_is_insufficient(self):
        d = valid_dossier()
        d["subsequent_evidence"] = d["subsequent_evidence"][:1]
        self.assert_blocked(d, "INDEPENDENT_SIGNAL_MISSING")
        d = valid_dossier()
        d["subsequent_evidence"][1]["source_id"] = "browser-run-1"
        self.assert_blocked(d, "INDEPENDENT_SIGNAL_MISSING")
        d = valid_dossier()
        d["subsequent_evidence"][1]["kind"] = "screenshot"
        self.assert_blocked(d, "SUBSEQUENT_EVIDENCE_INCOMPLETE")

    def test_T6_complete_N1_case_is_only_formally_eligible(self):
        d = valid_dossier()
        self.assertEqual((ELIGIBLE, []), evaluate(d))
        self.assertNotEqual("AUDIT_PASS", evaluate(d)[0])
        for risk in ("N0-D", "N0-V"):
            with self.subTest(risk=risk):
                d["risk_level"] = risk
                self.assertEqual((ELIGIBLE, []), evaluate(d))

    def test_T7_original_raw_product_failure_is_untouched(self):
        d = valid_dossier()
        original = copy.deepcopy(d)
        self.assertEqual(ELIGIBLE, evaluate(d)[0])
        self.assertEqual(original, d)
        self.assertEqual("PRODUCT_FAIL", d["original_receipt"]["result"])
        self.assertEqual("PRODUCT_FAIL", d["raw_gate_result"])
        d["raw_gate_result"] = "PASS"
        self.assert_blocked(d, "RAW_PRODUCT_FAIL_NOT_PRESERVED")
        d = valid_dossier()
        d["original_receipt"]["exit_code"] = 0
        self.assert_blocked(d, "ORIGINAL_RECEIPT_INCOMPLETE")

    def test_T8_executor_cannot_self_approve(self):
        d = valid_dossier()
        d["auditor_identity"]["id"] = d["executor_identity"]["id"]
        self.assert_blocked(d, "AUDITOR_NOT_INDEPENDENT_DECLARED")

    def test_T9_human_acceptance_and_each_action_remain_separate(self):
        d = valid_dossier()
        self.assertEqual(ELIGIBLE, evaluate(d)[0])
        for action in ACTION_AUTHORIZATIONS:
            self.assertEqual(PROMOTION_BLOCKED, promotion_prerequisites(d, action)[0])
            self.assertIn("HUMAN_ACCEPTANCE_MISSING",
                          promotion_prerequisites(d, action)[1])
        d["human_acceptance_recorded"] = True
        for action in ACTION_AUTHORIZATIONS:
            self.assertIn(action.upper() + "_AUTHORIZATION_MISSING",
                          promotion_prerequisites(d, action)[1])
        d["commit_authorized"] = True
        self.assertEqual(PROMOTION_BLOCKED, promotion_prerequisites(d, "commit")[0])
        d["other_integration_gates_satisfied"] = True
        self.assertEqual(PROMOTION_PREREQUISITES,
                         promotion_prerequisites(d, "commit")[0])
        for action in ("push", "merge", "deploy"):
            self.assertEqual(PROMOTION_BLOCKED, promotion_prerequisites(d, action)[0])

    def test_action_authorization_is_not_shared_across_git_or_deploy_stages(self):
        for authorized_action, field in ACTION_AUTHORIZATIONS.items():
            with self.subTest(authorized_action=authorized_action):
                d = valid_dossier()
                d["human_acceptance_recorded"] = True
                d["other_integration_gates_satisfied"] = True
                d[field] = True
                for requested_action in ACTION_AUTHORIZATIONS:
                    result, reasons = promotion_prerequisites(d, requested_action)
                    if requested_action == authorized_action:
                        self.assertEqual(PROMOTION_PREREQUISITES, result)
                    else:
                        self.assertEqual(PROMOTION_BLOCKED, result)
                        self.assertIn(requested_action.upper() + "_AUTHORIZATION_MISSING",
                                      reasons)
        d = valid_dossier()
        d["human_acceptance_recorded"] = True
        d["other_integration_gates_satisfied"] = True
        d["git_integration_authorized"] = True  # A legacy catch-all is ignored.
        self.assertEqual(PROMOTION_BLOCKED, promotion_prerequisites(d, "merge")[0])
        self.assertEqual((PROMOTION_BLOCKED, ["ACTION_UNSUPPORTED"]),
                         promotion_prerequisites(d, "release"))

    def test_T10_change_after_opinion_invalidates(self):
        d = valid_dossier()
        d["change_after_opinion"] = True
        self.assert_blocked(d, "CANDIDATE_CHANGED_AFTER_OPINION")

    def test_T11_N2_and_N3_are_out_of_scope(self):
        for risk in ("N2", "N3"):
            with self.subTest(risk=risk):
                d = valid_dossier()
                d["risk_level"] = risk
                self.assert_blocked(d, "RISK_CLASS_OUT_OF_SCOPE")

    def test_T12_pure_audit_pass_is_forbidden(self):
        d = valid_dossier()
        d["final_disposition"] = "AUDIT_PASS"
        self.assert_blocked(d, "DISPOSITION_EXCEEDS_POLICY")

    def test_T13_receipt_or_identity_missing(self):
        d = valid_dossier()
        del d["original_receipt"]
        self.assert_blocked(d, "ORIGINAL_RECEIPT_INCOMPLETE")
        d = valid_dossier()
        del d["candidate_identity"]
        self.assert_blocked(d, "CANDIDATE_IDENTITY_INCOMPLETE")

    def test_old_capture_gaps_are_explicit_and_not_fabricated(self):
        d = valid_dossier()
        receipt = d["original_receipt"]
        for name in ("stdout", "stderr"):
            del receipt[name + "_path"]
            del receipt[name + "_sha256"]
            receipt[name + "_unavailable_reason"] = "Not captured in the original run"
        del receipt["exit_code"]
        receipt["exit_code_unavailable_reason"] = "The launcher lost the exit code"
        self.assertEqual((ELIGIBLE, []), evaluate(d))
        del receipt["stdout_unavailable_reason"]
        self.assert_blocked(d, "ORIGINAL_RECEIPT_INCOMPLETE")

    def test_T14_new_relevant_failure_after_counterevidence(self):
        d = valid_dossier()
        d["later_relevant_failure"] = True
        self.assert_blocked(d, "LATER_RELEVANT_FAILURE")

    def test_policy_is_ineligible_before_real_activation_chain(self):
        d = valid_dossier()
        del d["policy_activation"]
        d["policy_effective"] = True  # A self-declared flag cannot activate it.
        self.assert_blocked(d, "POLICY_ACTIVATION_MISSING")
        d = valid_dossier()
        d["policy_activation"] = False
        self.assert_blocked(d, "POLICY_ACTIVATION_MISSING")
        d = valid_dossier()
        d["policy_activation"] = {"policy_effective": True}
        self.assert_blocked(d, "ACTIVATION_AUDIT_INCOMPLETE")

    def test_activation_must_bind_exact_chg_version_and_final_source_hash(self):
        for field, value, reason in (
                ("chg_id", "CHG-OTHER", "ACTIVATION_CHG_MISMATCH"),
                ("policy_version", "future-version", "ACTIVATION_POLICY_VERSION_MISMATCH"),
                ("final_canonical_source_sha256", "f" * 64,
                 "ACTIVATION_CANONICAL_SOURCE_INCOMPLETE")):
            with self.subTest(field=field):
                d = valid_dossier()
                d["policy_activation"][field] = value
                self.assert_blocked(d, reason)
        d = valid_dossier()
        d["policy_activation"]["canonical_source"]["sha256"] = "f" * 64
        self.assert_blocked(d, "ACTIVATION_CANONICAL_SOURCE_INCOMPLETE")

    def test_activation_receipts_bind_final_control_plane_candidate(self):
        d = valid_dossier()
        del d["policy_activation"]["control_plane_candidate_fingerprint"]
        self.assert_blocked(d, "ACTIVATION_CONTROL_PLANE_FINGERPRINT_INCOMPLETE")
        d = valid_dossier()
        d["policy_activation"]["control_plane_candidate_fingerprint"] = "a" * 64
        self.assert_blocked(d, "ACTIVATION_AUDIT_INCOMPLETE")
        for field, reason in (
                ("control_plane_audit", "ACTIVATION_AUDIT_INCOMPLETE"),
                ("human_acceptance", "ACTIVATION_HUMAN_ACCEPTANCE_MISSING"),
                ("repository_integration", "ACTIVATION_REPO_INTEGRATION_MISSING"),
                ("external_harness_activation", "ACTIVATION_EXTERNAL_HARNESS_MISSING")):
            with self.subTest(field=field):
                d = valid_dossier()
                d["policy_activation"][field]["control_plane_candidate_fingerprint"] = (
                    "a" * 64)
                self.assert_blocked(d, reason)
        d = valid_dossier()
        d["policy_activation"]["repository_integration"]["authorization_receipt"][
            "control_plane_candidate_fingerprint"] = "a" * 64
        self.assert_blocked(d, "ACTIVATION_REPO_INTEGRATION_MISSING")

    def test_activation_requires_audit_acceptance_integration_and_external_receipts(self):
        for field, reason in (
                ("control_plane_audit", "ACTIVATION_AUDIT_INCOMPLETE"),
                ("human_acceptance", "ACTIVATION_HUMAN_ACCEPTANCE_MISSING"),
                ("repository_integration", "ACTIVATION_REPO_INTEGRATION_MISSING"),
                ("external_harness_activation", "ACTIVATION_EXTERNAL_HARNESS_MISSING")):
            with self.subTest(field=field):
                d = valid_dossier()
                del d["policy_activation"][field]
                self.assert_blocked(d, reason)
        d = valid_dossier()
        d["policy_activation"]["control_plane_audit"]["verdict"] = "AUDIT_INCONCLUSIVE"
        self.assert_blocked(d, "ACTIVATION_AUDIT_INCOMPLETE")
        d = valid_dossier()
        d["policy_activation"]["control_plane_audit"]["independent"] = False
        self.assert_blocked(d, "ACTIVATION_AUDIT_INCOMPLETE")
        d = valid_dossier()
        d["policy_activation"]["control_plane_audit"]["auditor_id"] = (
            d["policy_activation"]["control_plane_audit"]["executor_id"])
        self.assert_blocked(d, "ACTIVATION_AUDIT_INCOMPLETE")
        d = valid_dossier()
        del d["policy_activation"]["repository_integration"]["authorization_receipt"]
        self.assert_blocked(d, "ACTIVATION_REPO_INTEGRATION_MISSING")

    def test_every_activation_receipt_requires_path_hash_and_binding(self):
        for field in ("control_plane_audit", "human_acceptance",
                      "repository_integration", "external_harness_activation"):
            for missing in ("path", "sha256", "canonical_source_sha256"):
                with self.subTest(field=field, missing=missing):
                    d = valid_dossier()
                    del d["policy_activation"][field][missing]
                    self.assertEqual(INELIGIBLE, evaluate(d)[0])
        d = valid_dossier()
        d["policy_activation"]["repository_integration"]["commit"] = "not-a-commit"
        self.assert_blocked(d, "ACTIVATION_REPO_INTEGRATION_MISSING")
        d = valid_dossier()
        d["policy_activation"]["human_acceptance"]["chg_id"] = "CHG-OTHER"
        self.assert_blocked(d, "ACTIVATION_HUMAN_ACCEPTANCE_MISSING")
        d = valid_dossier()
        d["policy_activation"]["external_harness_activation"]["policy_version"] = "v2"
        self.assert_blocked(d, "ACTIVATION_EXTERNAL_HARNESS_MISSING")
        d = valid_dossier()
        d["policy_activation"]["canonical_source"]["path"] = "relative/Harness.md"
        self.assert_blocked(d, "ACTIVATION_CANONICAL_SOURCE_INCOMPLETE")

    def test_additional_negative_controls(self):
        d = valid_dossier()
        d["delta_relevance_assessment"]["call_flow"] = ""
        self.assert_blocked(d, "DELTA_REVIEW_INCOMPLETE")
        d = valid_dossier()
        d["pertinent_findings"] = [{"severity": "HIGH"}]
        self.assert_blocked(d, "HIGH_OR_CRITICAL_FINDING")
        for severity in ("HIGH ", "CRITICAL ", "BLOCKER", "low"):
            with self.subTest(severity=severity):
                d = valid_dossier()
                d["pertinent_findings"] = [{"severity": severity}]
                self.assert_blocked(d, "FINDING_SEVERITY_INVALID")
        d = valid_dossier()
        d["subsequent_evidence"][0]["candidate_identity"]["build_id"] = "other-build"
        self.assert_blocked(d, "SUBSEQUENT_EVIDENCE_INCOMPLETE")
        d = valid_dossier()
        d["provenance_sufficient"] = False
        self.assert_blocked(d, "PROVENANCE_INSUFFICIENT")
        d = valid_dossier()
        d["equivalence_assessment"]["observability_sufficient"] = False
        self.assert_blocked(d, "COUNTEREVIDENCE_NOT_EQUIVALENT")
        d = valid_dossier()
        d["material_change_since_evidence"] = True
        self.assert_blocked(d, "CANDIDATE_CHANGED_AFTER_EVIDENCE")

    def test_malformed_json_values_are_ineligible_without_exception(self):
        for path, value in (
                (("subsequent_evidence", 0, "kind"), []),
                (("affected_property", "domain"), {}),
                (("pertinent_findings",), [{"severity": 9}])):
            with self.subTest(path=path):
                d = valid_dossier()
                target = d
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = value
                self.assertEqual(INELIGIBLE, evaluate(d)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

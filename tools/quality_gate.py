#!/usr/bin/env python3
"""Run JP Wealth quality tiers and write reproducible local evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "tools/.artifacts"

FAST = (
    ("preflight", [sys.executable, "tools/agent_preflight.py", "--mode", "audit", "--allow-dirty"]),
    ("structure", [sys.executable, "tools/validate_project.py"]),
    ("diff-check", ["git", "diff", "--check"]),
    ("preflight-context", [sys.executable, "tools/preflight_context_test.py"]),
)
STANDARD = FAST + (
    ("navigation-ia", [sys.executable, "tools/navigation_ia_test.py"]),
    ("research-navigation", [sys.executable, "tools/research_navigation_test.py"]),
    ("smoke", [sys.executable, "tools/smoke_test.py"]),
    ("settings", [sys.executable, "tools/settings_modal_test.py"]),
    ("galton-board", [sys.executable, "tools/galton_board_test.py"]),
    ("fx-planning", [sys.executable, "tools/fx_planning_test.py"]),
    ("exec-submenu", [sys.executable, "tools/exec_submenu_test.py"]),
    ("nocoda", [sys.executable, "tools/nocoda_test.py"]),
    ("pivot-studies", [sys.executable, "tools/pivot_studies_test.py"]),
    ("order-guards", [sys.executable, "tools/order_guards_test.py"]),
    ("operation-identity", [sys.executable, "tools/operation_identity_test.py"]),
    ("operation-finalize", [sys.executable, "tools/operation_finalize_test.py"]),
    ("operation-history", [sys.executable, "tools/operation_history_test.py"]),
    ("operation-wiring", [sys.executable, "tools/operation_wiring_test.py"]),
    ("phases-visibility", [sys.executable, "tools/phases_visibility_test.py"]),
    ("exec-three-column", [sys.executable, "tools/exec_three_column_test.py"]),
    ("finpes-foundation", [sys.executable, "tools/finpes_foundation_test.py"]),
    ("finpes-finalize-preservation", [sys.executable, "tools/finpes_finalize_preservation_test.py"]),
    ("finpes-backup-roundtrip", [sys.executable, "tools/finpes_backup_roundtrip_test.py"]),
    ("finpes-navigation", [sys.executable, "tools/finpes_navigation_test.py"]),
    ("finpes-budget", [sys.executable, "tools/finpes_budget_test.py"]),
    ("finpes-debt-credit", [sys.executable, "tools/finpes_debt_credit_test.py"]),
    ("finpes-comparison", [sys.executable, "tools/finpes_comparison_test.py"]),
    ("finpes-scenarios", [sys.executable, "tools/finpes_scenarios_test.py"]),
    ("finpes-overview", [sys.executable, "tools/finpes_overview_test.py"]),
    ("usd-brl-quote", [sys.executable, "tools/usd_brl_quote_test.py"]),
    ("alladin-unit", [sys.executable, "tools/alladin_unit_test.py"]),
    ("alladin-ledger", [sys.executable, "tools/alladin_ledger_test.py"]),
    ("alladin-position", [sys.executable, "tools/alladin_position_test.py"]),
    ("alladin-foundation", [sys.executable, "tools/alladin_foundation_test.py"]),
    ("alladin-finalize-preservation", [sys.executable, "tools/alladin_finalize_preservation_test.py"]),
    ("session-epoch-protocol", [sys.executable, "tools/session_epoch_protocol_test.py"]),
    ("session-write-serialization", [sys.executable, "tools/session_write_serialization_test.py"]),
    ("alladin-ui-readonly", [sys.executable, "tools/alladin_ui_readonly_test.py"]),
    ("alladin-ui-crud", [sys.executable, "tools/alladin_ui_crud_test.py"]),
    ("alladin-ui-ledger", [sys.executable, "tools/alladin_ui_ledger_test.py"]),
    ("alladin-ui-tx-write", [sys.executable, "tools/alladin_ui_tx_write_test.py"]),
)
FULL = STANDARD + (
    ("session-finalization", [sys.executable, "tools/finalize_session_test.py"]),
    ("storage-governance", [sys.executable, "tools/storage_governance_test.py"]),
    ("persistence-failure", [sys.executable, "tools/persistence_failure_test.py"]),
    ("persistence-recovery", [sys.executable, "tools/persistence_recovery_test.py"]),
    ("investor-password", [sys.executable, "tools/investor_password_test.py"]),
    ("import-xss", [sys.executable, "tools/import_xss_security_test.py"]),
    ("state-integrity", [sys.executable, "tools/state_integrity_test.py"]),
    ("async-generation", [sys.executable, "tools/async_generation_test.py"]),
    ("build-reproducibility", [sys.executable, "tools/build_reproducibility_test.py"]),
    ("service-worker-upgrade", [sys.executable, "tools/service_worker_upgrade_test.py"]),
    ("mvp-notes", [sys.executable, "tools/mvp_notes_test.py"]),
)
TIERS = {"fast": FAST, "standard": STANDARD, "full": FULL}
ENVIRONMENT_MARKERS = (
    "ModuleNotFoundError",
    "No module named",
    "Executable doesn't exist",
    "playwright install",
    "ENVIRONMENT_ERROR",
    "command not found",
)
EXPLICIT_FAILURE_RESULTS = ("TEST_HARNESS_FAIL", "BASELINE_FAIL", "NOT_RUN", "PRODUCT_FAIL")


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def classify(returncode: int, output: str) -> str:
    if returncode == 0:
        return "PASS"
    for result in EXPLICIT_FAILURE_RESULTS:
        if result in output:
            return result
    if returncode in {126, 127} or any(marker in output for marker in ENVIRONMENT_MARKERS):
        return "ENVIRONMENT_ERROR"
    return "PRODUCT_FAIL"


def run_check(name: str, command: list[str]) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=900,
            check=False,
        )
        output = completed.stdout or ""
        returncode = completed.returncode
    except FileNotFoundError as exc:
        output, returncode = f"ENVIRONMENT_ERROR: {exc}", 127
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + "\nENVIRONMENT_ERROR: timeout apos 900s"
        returncode = 124
    duration = round(time.monotonic() - started, 3)
    return {
        "name": name,
        "command": shlex.join(command),
        "result": classify(returncode, output),
        "returncode": returncode,
        "duration_seconds": duration,
        "output_tail": output[-12000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=TIERS, default="standard")
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()

    started_at = datetime.now().astimezone()
    checks: list[dict[str, object]] = []
    for name, command in TIERS[args.tier]:
        print(f"[RUN] {name}: {shlex.join(command)}", flush=True)
        check = run_check(name, list(command))
        checks.append(check)
        print(f"[{check['result']}] {name} ({check['duration_seconds']}s)", flush=True)

    status = git_value("status", "--porcelain=v1")
    payload = {
        "schema_version": 1,
        "tier": args.tier,
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "git": {
            "branch": git_value("branch", "--show-current"),
            "head": git_value("rev-parse", "HEAD"),
            "dirty": bool(status),
            "status": status.splitlines(),
        },
        "checks": checks,
        "summary": {
            result: sum(check["result"] == result for check in checks)
            for result in ("PASS", "PRODUCT_FAIL", "TEST_HARNESS_FAIL", "ENVIRONMENT_ERROR", "BASELINE_FAIL", "NOT_RUN")
        },
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact = args.artifact or ARTIFACT_DIR / f"quality-{started_at.strftime('%Y%m%dT%H%M%S')}-{args.tier}.json"
    if not artifact.is_absolute():
        artifact = ROOT / artifact
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Relatorio: {artifact}")
    print("Resumo: " + ", ".join(f"{key}={value}" for key, value in payload["summary"].items()))
    return 0 if all(check["result"] == "PASS" for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

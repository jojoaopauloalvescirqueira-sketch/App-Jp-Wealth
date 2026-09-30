#!/usr/bin/env python3
"""Explicit MT5 host suite; does not replace the web full gate or native MT5.

The receipt binds input hashes before/after execution to full per-test logs.
Only repository sources and synthetic test output enter this evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ("PASS", "PRODUCT_FAIL", "TEST_HARNESS_FAIL", "ENVIRONMENT_ERROR", "BASELINE_FAIL", "NOT_RUN")
HOST = (
    "leverage_suite_test", "leverage_panel_test", "leverage_cockpit_test",
    "leverage_details_event_test", "leverage_geometry_test",
    "leverage_config_test", "leverage_factor_test", "leverage_horizon_test",
    "leverage_live_adapter_test", "leverage_observer_test",
    "leverage_stop_risk_test", "leverage_stop_ui_test",
    "leverage_reliability_test", "leverage_diagnostics_test",
    "leverage_scheduler_test",
)
DISTRIBUTION = ("leverage_package_test", "leverage_page_test")


def classify(returncode: int, output: str) -> str:
    explicit = re.findall(r"^JPW_TEST_RESULT: (\w+)\s*$", output, re.MULTILINE)
    if explicit:
        if len(explicit) != 1 or explicit[0] not in RESULTS:
            return "TEST_HARNESS_FAIL"
        if (explicit[0] == "PASS") != (returncode == 0):
            return "TEST_HARNESS_FAIL"
        return explicit[0]
    if returncode == 0:
        return "PASS"
    if returncode in (126, 127) or any(marker in output for marker in (
        "ModuleNotFoundError", "No module named", "Executable doesn't exist",
        "ENVIRONMENT_ERROR:", "NOT_RUN: no C++ compiler", "playwright install",
    )):
        return "ENVIRONMENT_ERROR"
    return "PRODUCT_FAIL"


def input_hashes(root: Path = ROOT) -> dict[str, str]:
    paths: set[Path] = set()
    for pattern in (
        "mt5/jpw-alavancagem-atual/**/*", "tools/leverage_*.py",
        "tools/build_leverage_package.py", "tools/browser_bootstrap_fixture.py",
        "downloads/jpw-alavancagem-atual/*", ".github/workflows/mt5-host.yml",
        "requirements-dev.txt", "src/**/*", "index.html", "build-id.js",
        "sw.js", "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
    ):
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def fingerprint(hashes: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def aggregate_result(checks: list[dict[str, object]]) -> str:
    observed = {check["result"] for check in checks}
    for result in ("PRODUCT_FAIL", "TEST_HARNESS_FAIL", "ENVIRONMENT_ERROR", "BASELINE_FAIL", "NOT_RUN"):
        if result in observed:
            return result
    return "PASS" if checks else "NOT_RUN"


def run_check(name: str, command: list[str], cwd: Path, logs: Path,
              timeout: float = 180) -> dict[str, object]:
    started = time.monotonic()
    process = None
    cleanup_error = ""
    try:
        if os.name != "posix":
            raise OSError("MT5 host runner requires POSIX process-group isolation")
        process = subprocess.Popen(command, cwd=cwd, text=True, encoding="utf-8",
                                   errors="replace", stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        output, _ = process.communicate(timeout=timeout)
        returncode = process.returncode
        result = classify(returncode, output)
    except OSError as exc:
        output, returncode, result = str(exc), 127, "ENVIRONMENT_ERROR"
    except subprocess.TimeoutExpired as exc:
        try:
            stop_owned_group(process)
        except OSError as error:
            cleanup_error = str(error)
            try:
                process.kill()
            except OSError:
                pass
        try:
            output, _ = process.communicate(timeout=1)
        except subprocess.TimeoutExpired as remaining:
            partial = remaining.stdout or exc.stdout or ""
            output = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) else partial
            if process.stdout:
                process.stdout.close()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                cleanup_error += "; timed-out leader could not be reaped"
        output += f"\nENVIRONMENT_ERROR: exceeded {timeout:g} second host test budget\n"
        returncode, result = 124, "ENVIRONMENT_ERROR"
    finally:
        if process is not None:
            try:
                stop_owned_group(process)
            except OSError as error:
                cleanup_error = cleanup_error or str(error)
    if cleanup_error:
        output += f"\nENVIRONMENT_ERROR: process cleanup could not be confirmed: {cleanup_error}\n"
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f"{name}.log"
    log.write_text(output, encoding="utf-8")
    return {"name": name, "command": shlex.join(command), "result": result,
            "returncode": returncode, "duration_seconds": round(time.monotonic() - started, 3),
            "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
            "process_cleanup_error": cleanup_error or None}


def stop_owned_group(process: subprocess.Popen[str]) -> None:
    """Stop only the fresh session created for this check, including children."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 0.2
    # Reap the leader before probing/signalling its remaining group. macOS
    # reports EPERM for a group containing only an unreaped dead leader.
    try:
        process.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        pass
    remaining = deadline - time.monotonic()
    if remaining > 0:
        time.sleep(remaining)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("host", "all"), default="host")
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    artifact = args.artifact or ROOT / "tools/.artifacts" / f"mt5-host-{started.strftime('%Y%m%dT%H%M%SZ')}.json"
    artifact = artifact.resolve()
    before = input_hashes()
    checks = []
    for name in HOST + (DISTRIBUTION if args.scope == "all" else ()):
        command = [sys.executable, str(ROOT / "tools" / f"{name}.py")]
        print(f"[RUN] {name}", flush=True)
        check = run_check(name, command, ROOT, artifact.with_suffix(".logs"),
                          timeout=420 if name == "leverage_page_test" else 180)
        checks.append(check)
        print(f"[{check['result']}] {name} ({check['duration_seconds']}s)", flush=True)
        if check["process_cleanup_error"]:
            checks.append({"name": name + "-process-cleanup", "result": "ENVIRONMENT_ERROR",
                           "reason": check["process_cleanup_error"]})
            pending = HOST + (DISTRIBUTION if args.scope == "all" else ())
            checks.extend({"name": skipped, "result": "NOT_RUN",
                           "reason": "Earlier test process cleanup could not be confirmed"}
                          for skipped in pending[pending.index(name) + 1:])
            break
    after = input_hashes()
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    if changed:
        checks.append({"name": "input-stability", "result": "TEST_HARNESS_FAIL",
                       "reason": "Inputs changed during suite; receipts cannot certify one candidate", "paths": changed})
    counts = Counter(check["result"] for check in checks)
    passed = all(check["result"] == "PASS" for check in checks)
    receipt = {
        "schema_version": 1, "suite": "MT5_HOST_SYNTHETIC", "scope": args.scope,
        "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASSED" if passed else "FAILED", "result": aggregate_result(checks),
        "summary": {result: counts[result] for result in RESULTS},
        "candidate": {"head": git_value("rev-parse", "HEAD"), "branch": git_value("branch", "--show-current"),
                      "dirty_status": git_value("status", "--porcelain=v1").splitlines(),
                      "input_fingerprint": fingerprint(before), "source_hashes": before,
                      "inputs_unchanged": not changed},
        "environment": {"platform": platform.platform(), "python": sys.version,
                        "compiler": shutil.which("clang++") or shutil.which("g++")},
        "checks": checks,
        "native_compilation": "NOT_RUN", "native_execution": "NOT_RUN",
        "operational_readiness": "BLOCKED_NATIVE_VALIDATION",
        "web_full_gate": "NOT_RUN_BY_THIS_SUITE",
    }
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"RECEIPT: {artifact}\nSUMMARY: {json.dumps(receipt['summary'])}")
    print("Native compilation/execution NOT_RUN; web full gate remains separate.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

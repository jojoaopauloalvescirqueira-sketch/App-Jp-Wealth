#!/usr/bin/env python3
"""Failure-injection checks for MT5 evidence classification and log integrity."""
import hashlib
import os
from pathlib import Path
import sys
import time
from tempfile import TemporaryDirectory
from unittest.mock import patch

from leverage_suite import aggregate_result, classify, fingerprint, run_check


def main() -> int:
    cases = [
        (0, "PASS; native compilation NOT_RUN", "PASS"),
        (1, "assertion failed", "PRODUCT_FAIL"),
        (1, "host.cpp:82: error: undeclared identifier; 1 error generated.", "TEST_HARNESS_FAIL"),
        (1, "FAIL stale sample advertised Current", "PRODUCT_FAIL"),
        (1, "JPW_TEST_RESULT: BASELINE_FAIL", "BASELINE_FAIL"),
        (1, "ModuleNotFoundError: playwright", "ENVIRONMENT_ERROR"),
        (0, "JPW_TEST_RESULT: PRODUCT_FAIL", "TEST_HARNESS_FAIL"),
        (1, "JPW_TEST_RESULT: PASS", "TEST_HARNESS_FAIL"),
        (0, "JPW_TEST_RESULT: PASS\nJPW_TEST_RESULT: PASS", "TEST_HARNESS_FAIL"),
    ]
    for code, output, expected in cases:
        assert classify(code, output) == expected, (code, output, expected)
    assert fingerprint({"a": "1", "b": "2"}) == fingerprint({"b": "2", "a": "1"})
    assert fingerprint({"a": "1"}) != fingerprint({"a": "2"})
    assert aggregate_result([]) == "NOT_RUN"
    assert aggregate_result([{"result": "ENVIRONMENT_ERROR"}]) == "ENVIRONMENT_ERROR"
    assert aggregate_result([{"result": "PASS"}, {"result": "TEST_HARNESS_FAIL"}]) == "TEST_HARNESS_FAIL"
    assert aggregate_result([{"result": "PRODUCT_FAIL"}, {"result": "ENVIRONMENT_ERROR"}]) == "PRODUCT_FAIL"
    with TemporaryDirectory(prefix="jpw-suite-evidence-") as temporary:
        base = Path(temporary)
        result = run_check("failure", [sys.executable, "-c", "print('synthetic failure'); raise SystemExit(1)"], base, base)
        assert result["result"] == "PRODUCT_FAIL"
        log = Path(result["log"])
        assert result["log_sha256"] == hashlib.sha256(log.read_bytes()).hexdigest()
        assert "synthetic failure" in log.read_text()
        timeout = run_check("timeout", [sys.executable, "-c", "import time; print('partial', flush=True); time.sleep(5)"], base, base, timeout=0.1)
        assert timeout["result"] == "ENVIRONMENT_ERROR" and timeout["returncode"] == 124
        assert "partial" in Path(timeout["log"]).read_text()
        child_started, orphan_write = base / "child-started", base / "orphan-write"
        child = ("import pathlib,signal,time; "
                 "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                 f"pathlib.Path({str(child_started)!r}).write_text('started'); "
                 "print('child running',flush=True); time.sleep(1); "
                 f"pathlib.Path({str(orphan_write)!r}).write_text('escaped')")
        parent = ("import subprocess,sys,time; "
                  f"subprocess.Popen([sys.executable,'-c',{child!r}]); "
                  "time.sleep(5)")
        tree = run_check("timeout-tree", [sys.executable, "-c", parent], base, base, timeout=0.3)
        assert tree["result"] == "ENVIRONMENT_ERROR" and tree["returncode"] == 124
        assert child_started.is_file(), "synthetic descendant did not start"
        assert "child running" in Path(tree["log"]).read_text()
        time.sleep(1)
        assert not orphan_write.exists(), "timed-out descendant survived to mutate later inputs"
        original_killpg = os.killpg
        denied_once = [False]
        def deny_first_signal(pid, signum):
            if not denied_once[0]:
                denied_once[0] = True
                raise PermissionError("synthetic denied group signal")
            return original_killpg(pid, signum)
        with patch("leverage_suite.os.killpg", side_effect=deny_first_signal):
            denied = run_check("cleanup-refused", [sys.executable, "-c", "import time; time.sleep(5)"], base, base, timeout=0.1)
        assert denied["process_cleanup_error"] and Path(denied["log"]).is_file()
        assert "cleanup could not be confirmed" in Path(denied["log"]).read_text()
        missing = run_check("missing", [str(base / "nonexistent-executable")], base, base)
        assert missing["result"] == "ENVIRONMENT_ERROR"
    print("MT5 suite: classification, timeout/descendant termination, missing tool, source/log identity PASS")
    print("JPW_TEST_RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

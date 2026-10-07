#!/usr/bin/env python3
"""Check partial timeout receipts without extending the gate's time budget."""
import importlib.util
import json
from pathlib import Path
import subprocess
from unittest.mock import patch


def main():
    spec = importlib.util.spec_from_file_location("quality_gate", Path(__file__).with_name("quality_gate.py"))
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    cases = [(b"partial receipt\n", "partial receipt\n"),
             ("text receipt", "text receipt"),
             (None, ""),
             (b"bad utf8 \xff", "bad utf8 \ufffd")]
    observed = []
    for raw, expected in cases:
        with patch.object(gate.subprocess, "run", side_effect=subprocess.TimeoutExpired(["synthetic"], 900, output=raw)) as run:
            result = gate.run_check("timeout-probe", ["synthetic"])
            assert run.call_args.kwargs["timeout"] == 900
            assert result["returncode"] == 124
            assert result["result"] == "ENVIRONMENT_ERROR"
            assert result["output_tail"] == expected + "\nENVIRONMENT_ERROR: timeout apos 900s"
            assert json.loads(json.dumps(result)) == result
            observed.append(result)
    # A timeout receipt must allow the next check to run and retain its own result.
    with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(["synthetic"], 0, "PASS after timeout")):
        following = gate.run_check("following-probe", ["synthetic"])
    assert following["result"] == "PASS"
    print(json.dumps({"result": "PASS", "cases": len(observed) + 1, "receipts": observed, "following": following}, ensure_ascii=False))


if __name__ == "__main__":
    main()

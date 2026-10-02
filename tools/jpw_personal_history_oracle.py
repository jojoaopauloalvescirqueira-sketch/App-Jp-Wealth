#!/usr/bin/env python3
"""Independent Decimal reference for observed leverage maxima.

This module never imports the MQL source or implements its episode, clock,
storage, notification or UI state machine. Inputs are synthetic extensions of
the frozen acceptance descriptions; results are not facts about an account.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "tests/fixtures/genetrix-personal-history/acceptance-v1.json"
ACCEPTANCE_SHA = "58498de5802e4b989fcda76998e8ec4ccdff930d813430a54e01f339ae91c86c"


def acceptance() -> dict:
    raw = ACCEPTANCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ACCEPTANCE_SHA:
        raise AssertionError("frozen acceptance fixture changed")
    result = json.loads(raw)
    if len(result["cases"]) != 20 or not result["frozen_before_implementation"]:
        raise AssertionError("acceptance fixture identity invalid")
    return result


def ratio(gross: str, equity: str, eligible: bool = True) -> str | None:
    """Gross/equity in one native monetary unit; no currency conversion."""
    with localcontext() as context:
        context.prec = 60
        g, e = Decimal(gross), Decimal(equity)
        if not eligible or not g.is_finite() or not e.is_finite() or g < 0 or e <= 0:
            return None
        return str(g / e)


def financial_vectors(case_id: str) -> list[dict]:
    inputs = {
        "HIS-AC12": [
            ("first", "1400", "200", "Current", True),
            ("lower", "1399.9999999", "200", "Current", True),
            ("tie", "1400", "200", "Current", True),
            ("higher_without_rounding", "1400.0000001", "200", "Current", True),
            ("estimated_separate", "1800", "200", "Estimated", True),
        ],
        "HIS-AC13": [
            ("equity_before", "1400", "200", "Current", True),
            ("equity_falls_no_entry", "1400", "175", "Current", True),
        ],
        "HIS-AC14": [
            ("zero_equity", "1400", "0", "N/A", True),
            ("negative_equity", "1400", "-1", "N/A", True),
            ("missing_conversion", "1400", "200", "N/A", False),
            ("partial_inventory", "1400", "200", "N/A", False),
            ("confirmed_empty", "0", "200", "Current", True),
        ],
    }
    result = []
    for label, gross, equity, quality, eligible in inputs.get(case_id, []):
        result.append({"label": label, "gross": gross, "equity": equity,
                       "quality": quality, "eligible": eligible,
                       "ratio_exact": ratio(gross, equity, eligible)})
    return result


def build_receipt(case_id: str | None = None) -> dict:
    fixture = acceptance()
    cases = fixture["cases"]
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
        if not cases:
            raise ValueError(f"unknown acceptance id: {case_id}")
    return {
        "schema": "jpw-personal-history-decimal-reference/v1",
        "acceptance_sha256": ACCEPTANCE_SHA,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "independence": "No product source import; Decimal arithmetic from explicit synthetic gross/equity inputs.",
        "cases": [{"id": case["id"],
                   "status": "PASS" if financial_vectors(case["id"]) else "NOT_RUN",
                   "scope": "Decimal reference evaluated; product behavior not exercised" if financial_vectors(case["id"]) else "No monetary oracle applicable; requires behavioral evidence",
                   "vectors": financial_vectors(case["id"])} for case in cases],
        "native_mql": "NOT_RUN", "mt5_runtime": "NOT_RUN",
        "account_data": "NOT_RUN", "trading": "NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", dest="case_id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = build_receipt(args.case_id)
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

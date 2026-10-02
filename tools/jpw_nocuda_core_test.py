#!/usr/bin/env python3
"""Execute the actual NoCuda MQL geometry core and script in a C++ host shim.

The geometry oracles come from the article and candle-sequence contract. This
does not claim MetaEditor compilation, chart rendering, or MT5 interaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
CORE = MQL / "Include/JPWealth/JPW_NoCuda_Core.mqh"
SCRIPT = MQL / "Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5"

SHIM = r'''
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
using string = std::string;
using datetime = long long;
bool MathIsValidNumber(double value) { return std::isfinite(value); }
double MathAbs(double value) { return std::abs(value); }
double MathSqrt(double value) { return std::sqrt(value); }
double MathMax(double a,double b) { return std::max(a,b); }
template<typename... Args> void Print(const Args&... args) {
  (std::cout << ... << args) << '\n';
}
'''

HOST_CASES = r'''
int main() {
  OnStart();
  JPWNoCudaGeometry base, shifted, below;
  string reason;
  double price=0.0, alternate=0.0;
  // Shifting all source ordinals must not change prices at matching bars.
  JPWNoCudaAssert(JPWNoCudaBuildGeometry(5,1.1,9,1.102,7,1.105,base,reason) &&
                  JPWNoCudaBuildGeometry(105,1.1,109,1.102,107,1.105,shifted,reason),
                  "host ordinal translation fixtures");
  JPWNoCudaAssert(JPWNoCudaPriceAt(base,0.375,8.5,price) &&
                  JPWNoCudaPriceAt(shifted,0.375,108.5,alternate),
                  "host translated projection available");
  JPWNoCudaNear(price,alternate,"source ordinal translation invariance");
  // Moving C from +d to -d about the principal mirrors every line pair.
  JPWNoCudaAssert(JPWNoCudaBuildGeometry(5,1.1,9,1.102,7,1.097,below,reason),
                  "host symmetric C fixture");
  double top=0.0,bottom=0.0,principal=0.0;
  JPWNoCudaAssert(JPWNoCudaPriceAt(base,1.0,7,top) &&
                  JPWNoCudaPriceAt(below,1.0,7,bottom) &&
                  JPWNoCudaPriceAt(base,0.0,7,principal),
                  "host mirrored price samples");
  JPWNoCudaNear(top-principal,principal-bottom,
                "C above/below mirror around the same principal");
  Print("HOST_NOCUDA_CORE: ",g_nocuda_pass," PASS / ",g_nocuda_fail," FAIL");
  Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN");
  return g_nocuda_fail==0 ? 0 : 1;
}
'''


def translated_script() -> str:
    text = SCRIPT.read_text()
    text = re.sub(r"^#property.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#include\s+<JPWealth/JPW_NoCuda_Core\.mqh>\s*$", "", text,
                  flags=re.MULTILINE)
    if "#property" in text or "#include" in text:
        raise AssertionError("synthetic script includes an unsupported native dependency")
    return text


def run(evidence_dir: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        print("ENVIRONMENT_ERROR: no C++ compiler for host replay; MT5 native NOT_RUN")
        return 2
    identity = {
        "kind": "HOST_SOURCE_LINKED_SYNTHETIC_NOT_MQL5",
        "compiler": compiler,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CORE, SCRIPT)
        },
        "article_case": "M: A(08:00,1.1000), B(12:00,1.1020), C(10:00,1.1050)",
        "limits": "No native MetaEditor, chart clicks, CCanvas, persistence or terminal execution",
    }
    if evidence_dir is not None:
        evidence_dir.mkdir(parents=True, exist_ok=False)
        (evidence_dir / "source-identity.json").write_text(
            json.dumps(identity, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="jpw-nocuda-core-") as directory:
        source = Path(directory) / "nocuda_core.cpp"
        binary = Path(directory) / "nocuda_core"
        source.write_text(SHIM + '\n#include "JPWealth/JPW_NoCuda_Core.mqh"\n' +
                          translated_script() + "\n" + HOST_CASES)
        command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                   "-I", str(MQL / "Include"), str(source), "-o", str(binary)]
        compile_result = subprocess.run(command, text=True, capture_output=True,
                                        timeout=60, check=False)
        if evidence_dir is not None:
            (evidence_dir / "compile-command.json").write_text(json.dumps(command) + "\n")
            (evidence_dir / "compile-stdout.txt").write_text(compile_result.stdout)
            (evidence_dir / "compile-stderr.txt").write_text(compile_result.stderr)
        print(compile_result.stdout, end="")
        print(compile_result.stderr, end="")
        if compile_result.returncode:
            print("HOST_NOCUDA_CORE: PRODUCT_FAIL; native MT5 NOT_RUN")
            return compile_result.returncode
        result = subprocess.run([str(binary)], text=True, capture_output=True,
                                timeout=60, check=False)
        if evidence_dir is not None:
            (evidence_dir / "run-stdout.txt").write_text(result.stdout)
            (evidence_dir / "run-stderr.txt").write_text(result.stderr)
            (evidence_dir / "result.json").write_text(json.dumps({
                "exit_code": result.returncode,
                "classification": "PASS" if result.returncode == 0 else "PRODUCT_FAIL",
                "native_mt5": "NOT_RUN",
            }, indent=2) + "\n")
        print(result.stdout, end="")
        print(result.stderr, end="")
        return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.evidence_dir))

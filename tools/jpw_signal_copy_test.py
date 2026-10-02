#!/usr/bin/env python3
"""Execute the exact distributed Signal Copy core and MQL assertions on host.

Only MQL metadata/array/date syntax and the native 64-bit format specifier are
translated. No financial logic is replaced. This is source-linked synthetic
evidence, not MetaEditor compilation, MT5 interaction or clipboard proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import leverage_config_test as base

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
FILES = [
    MQL / "Include/JPWealth/JPW_Alavancagem_Core.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
    MQL / "Include/JPWealth/JPW_SignalCopy_Types.mqh",
    MQL / "Include/JPWealth/JPW_SignalCopy_Core.mqh",
    MQL / "Scripts/JPWealth/JPW_SignalCopy_Tests.mq5",
]

EXTRA_SHIM = r'''
#include <ctime>
constexpr int TIME_DATE=1,TIME_SECONDS=2;
constexpr long ACCOUNT_MARGIN_MODE_RETAIL_NETTING=0;
constexpr long ACCOUNT_MARGIN_MODE_EXCHANGE=1;
constexpr long ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2;
enum {ORDER_TYPE_BUY=0,ORDER_TYPE_SELL=1,ORDER_TYPE_BUY_LIMIT=2,
      ORDER_TYPE_SELL_LIMIT=3,ORDER_TYPE_BUY_STOP=4,ORDER_TYPE_SELL_STOP=5,
      ORDER_TYPE_BUY_STOP_LIMIT=6,ORDER_TYPE_SELL_STOP_LIMIT=7};
double MathMax(double a,double b){return std::fmax(a,b);}
string TimeToString(datetime value,int){
  char out[32];std::time_t time=value;std::tm* p=std::gmtime(&time);
  if(!p)return "";std::strftime(out,sizeof(out),"%Y.%m.%d %H:%M:%S",p);return out;
}
int main(){
  OnStart();
  Print("HOST_SIGNAL_COPY: ",g_signal_pass," PASS / ",g_signal_fail," FAIL");
  Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN; NATIVE_COPY: NOT_RUN");
  return g_signal_fail==0?0:1;
}
'''


def translate(source: str) -> str:
    # C++ host uses its corresponding 64-bit printf primitive; native MQL
    # retains %I64u. No ticket is converted through a floating point number.
    return base.translate(source).replace('"%I64u"', '"%lu"')


def run(output: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: host C++ compiler unavailable; native MT5 NOT_RUN")
        return 2
    identity = {
        "test": "jpw_signal_copy",
        "kind": "HOST_SYNTHETIC_NOT_MQL5",
        "compiler": compiler,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in FILES
        },
        "limitations": "Exact pure core under host MQL primitive compatibility; Unicode string/golden host bytes only; no native compilation, terminal account, chart, clipboard or send.",
    }
    print(json.dumps(identity, indent=2))
    core = FILES[3].read_text(encoding="utf-8")
    for forbidden in ("OrderSend(", "OrderSendAsync(", "FileOpen(", "AccountInfo", "PositionGet", "OrderGet", "Chart", "WebRequest(", "MessageBox("):
        assert forbidden not in core, f"pure core contains side effect: {forbidden}"
    script = FILES[-1].read_text(encoding="utf-8")
    for required in ("SignalVirtualTests();", "SignalMembershipTests();", "SignalGateAndMessageTests();",
                     "SignalSharedTicketGrossTests();", "JPWGrossReading(positions,instruments,quotes",
                     "message==golden", "message==golden_pending", "9007199254740991"):
        assert required in script, f"distributed assertions missing: {required}"
    if output:
        output.mkdir(parents=True, exist_ok=False)
        (output / "source-identity.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    prefix, main = EXTRA_SHIM.split("int main(){", 1)
    receipts: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="jpw-signal-copy-synthetic-") as tmp:
        source, binary = Path(tmp) / "signal_copy.cpp", Path(tmp) / "signal_copy"
        source.write_text(base.SHIM + "\n" + prefix + "\n" +
                          "\n".join(translate(path.read_text(encoding="utf-8")) for path in FILES) +
                          "\nint main(){" + main, encoding="utf-8")
        if output:
            shutil.copy2(source, output / source.name)
        commands = [
            [compiler, "--version"],
            [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wno-unused-parameter",
             "-Wno-deprecated-declarations", str(source), "-o", str(binary)] +
            ([] if sys.platform == "darwin" else ["-lcrypto"]),
            [str(binary)],
        ]
        for i, command in enumerate(commands):
            result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            receipts.append({"command": command, "exit_code": result.returncode})
            if output:
                (output / f"{i}-stdout.txt").write_text(result.stdout, encoding="utf-8")
                (output / f"{i}-stderr.txt").write_text(result.stderr, encoding="utf-8")
                (output / "commands.json").write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
            if result.returncode:
                print(f"HOST_SIGNAL_COPY_STAGE_{i}: FAIL; native MT5 NOT_RUN")
                return result.returncode
    print("HOST_SIGNAL_COPY_RESULT: PASS; native MT5 and clipboard NOT_RUN")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.evidence_dir))

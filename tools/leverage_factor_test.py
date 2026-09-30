#!/usr/bin/env python3
"""Run the distributed MQL5 F-choice functions and assertions in a host shim.

This checks source-linked synthetic logic, not MetaEditor compilation, native
MT5 file locking/crash durability, or empirical market non-touch coverage.
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
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh",
    MQL / "Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5",
]

CDF_SHIM = r'''
bool inject_cdf_failure=false;
double MathCumulativeDistributionNormal(double x,double mu,double sigma,int& error_code){
  if(inject_cdf_failure || !std::isfinite(x) || !std::isfinite(mu) ||
     !std::isfinite(sigma) || sigma<=0.0){
    inject_cdf_failure=false;error_code=1;
    return std::numeric_limits<double>::quiet_NaN();
  }
  error_code=0;
  return 0.5*std::erfc(-(x-mu)/(sigma*std::sqrt(2.0)));
}
'''

MAIN = r'''
void HostFactorFaultTests(){
  const string folder=JPW_RAIZN_FOLDER+"SyntheticFactorFaults\\";
  const string symbol="SYNTH.EURUSD";
  string key="",reason="",before="",after="";
  FactorAssert(FactorKey(991999,symbol,key),"host fault synthetic key");
  JPWRaizNFactorPreference value,loaded;FactorFixture(key,symbol,value);
  FactorAssert(JPWRaizNFactorSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
               "host fault baseline saved");
  const string path=JPWRaizNFactorBase(folder,key);
  FactorAssert(JPWRaizNReadText(path+".a",before)==JPW_RAIZN_VALID,
               "host baseline bytes captured");
  value.factor=1.8;
  inject_short_write=true;
  FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_short_write && value.generation==1,
               "short temp write refuses Apply");
  FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.factor==1.5 && loaded.generation==1 &&
               JPWRaizNReadText(path+".a",after)==JPW_RAIZN_VALID && after==before,
               "short write preserves prior bytes");
  inject_move_failure=true;
  FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_move_failure && value.generation==1,
               "failed FileMove refuses Apply");
  FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.factor==1.5 && loaded.generation==1 &&
               JPWRaizNReadText(path+".a",after)==JPW_RAIZN_VALID && after==before,
               "failed move preserves prior bytes");
  string caller_before="",caller_after="";
  FactorAssert(JPWRaizNFactorEncode(value,caller_before),"uncertain caller captured");
  inject_post_move_readback_failure=true;
  FactorAssert(JPWRaizNFactorSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_post_move_readback_failure && fail_next_read_of.empty() &&
               post_move_readback_failures==1,
               "post-move readback failure reports uncertain IO_ERROR");
  FactorAssert(JPWRaizNFactorEncode(value,caller_after) &&
               caller_after==caller_before && value.generation==1,
               "uncertain result leaves caller object unchanged");
  FactorAssert(JPWRaizNReadText(path+".a",after)==JPW_RAIZN_VALID && after==before,
               "uncertain result preserves previous slot");
  FactorAssert(handles.empty(),"all handles released after post-move failure");
  FactorAssert(JPWRaizNFactorLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.factor==1.8 && loaded.generation==2,
               "later read sees actual new generation without claiming earlier Apply");
  double probability=42.0;inject_cdf_failure=true;
  FactorAssert(!JPWRaizNNoTouchProbability(1.5,probability) && probability==0.0 &&
               !inject_cdf_failure,"CDF error refuses theoretical percentage");
  bool temporaries=false;
  for(const auto& entry:fs::recursive_directory_iterator(file_root))
    if(entry.path().extension()==".tmp")temporaries=true;
  FactorAssert(!temporaries&&handles.empty(),"synthetic fault branches leave no temp/handle");
}
int main(int argc,char** argv){
  if(argc!=2)return 2;
  file_root=fs::path(argv[1]);fs::create_directories(file_root);
  string hash="";
  if(!JPWRaizNHash("abc",hash)||
     hash!="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"){
    std::cerr<<"TEST_HARNESS_FAIL: SHA256 compatibility primitive\n";return 2;
  }
  OnStart();
  HostFactorFaultTests();
  Print("HOST_FACTOR: ",g_factor_pass," PASS / ",g_factor_fail," FAIL");
  Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN");
  return g_factor_fail==0?0:1;
}
'''


def run(output: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler; native MT5 NOT_RUN")
        return 2
    identity = {
        "test": "leverage_factor",
        "kind": "HOST_SYNTHETIC_NOT_MQL5",
        "compiler": compiler,
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in FILES
        },
        "limitations": "C++ normal CDF shim, synthetic ASCII files/locks; no native MQL5, OS crash durability or empirical non-touch evidence.",
    }
    print(json.dumps(identity, indent=2))
    receipts: list[dict[str, object]] = []
    if output:
        output.mkdir(parents=True, exist_ok=False)
        (output / "source-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="jpw-raizn-factor-synthetic-") as tmp:
        source = Path(tmp) / "factor.cpp"
        binary = Path(tmp) / "factor"
        cxx = base.SHIM.replace("#include <memory>", "#include <memory>\n#include <limits>")
        source.write_text(
            cxx + "\n" + CDF_SHIM + "\n" +
            "\n".join(base.translate(path.read_text()) for path in FILES) +
            "\n" + MAIN
        )
        if output:
            shutil.copy2(source, output / "factor.cpp")
        commands = [
            [compiler, "--version"],
            [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wno-unused-parameter",
             "-Wno-deprecated-declarations", str(source), "-o", str(binary)] +
            ([] if sys.platform == "darwin" else ["-lcrypto"]),
            [str(binary), str(Path(tmp) / "files")],
        ]
        for index, command in enumerate(commands):
            result = subprocess.run(command, text=True, capture_output=True,
                                    check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            receipts.append({"command": command, "exit_code": result.returncode})
            if output:
                (output / f"{index}-stdout.txt").write_text(result.stdout)
                (output / f"{index}-stderr.txt").write_text(result.stderr)
                (output / "commands.json").write_text(json.dumps(receipts, indent=2) + "\n")
            if result.returncode:
                print(f"HOST_STAGE_{index}: FAILURE; EXIT_CODE: {result.returncode}; native MT5 NOT_RUN")
                return result.returncode
        print("HOST_FACTOR_RESULT: PASS; EXIT_CODE: 0")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.evidence_dir))

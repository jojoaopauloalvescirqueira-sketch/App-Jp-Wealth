#!/usr/bin/env python3
"""Execute the MQL-compatible collector against an explicit 1.18.1 host oracle.

This is a host behavioral test, NOT MetaEditor compilation/native MT5 evidence.
The collector, native-provider bodies and financial assertions are unchanged.
Two legacy call-count expectations are adapted in the translated script only;
one host call-count expectation follows the documented per-capture ATR reread.
Every transformation and original/derived hash is reported. The distributed
MQL script and EX5 are never modified or reported as a native behavioral PASS.
Terminal API calls are synthetic. A deliberately stale host-only cache mutant
must fail the same-metadata ATR correction and unavailable-ATR controls.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
FILES = [
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh",
    MQL / "Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5",
]

SHIM = r'''
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
using string = std::string;
using datetime = long;
constexpr double EMPTY_VALUE = std::numeric_limits<double>::max();
constexpr int INVALID_HANDLE = -1;
constexpr int PERIOD_H4 = 240;
constexpr int SERIES_SYNCHRONIZED = 1;
bool MathIsValidNumber(double value) { return std::isfinite(value); }
double MathSqrt(double value) { return std::sqrt(value); }
double MathAbs(double value) { return std::abs(value); }
template <typename... T> void Print(T... args) { (std::cout << ... << args) << '\n'; }
struct MqlTick { double bid, ask; long time_msc; };
bool api_contract_ok = true;
int api_buffer_reads = 0;
int api_quote_reads = 0;
int api_time_reads = 0;
datetime api_current = 172800;
datetime api_closed = 158400;
long api_quote_time = 172900000;
int api_bars = 100;
bool api_synced = true;
bool api_buffer_ok = true;
bool api_roll_during_buffer = false;
double api_atr = 0.4;
void ExactSymbol(const string &symbol) { api_contract_ok &= symbol == "SYMBOL.m.exact"; }
bool SymbolInfoTick(const string &symbol, MqlTick &tick) {
  ExactSymbol(symbol); ++api_quote_reads;
  tick.bid = 99.; tick.ask = 101.; tick.time_msc = api_quote_time; return true;
}
bool SeriesInfoInteger(const string &symbol, int timeframe, int property, long &value) {
  ExactSymbol(symbol); api_contract_ok &= timeframe == PERIOD_H4 && property == SERIES_SYNCHRONIZED;
  value = api_synced ? 1 : 0; return true;
}
int Bars(const string &symbol, int timeframe) {
  ExactSymbol(symbol); api_contract_ok &= timeframe == PERIOD_H4; return api_bars;
}
int BarsCalculated(int handle) { api_contract_ok &= handle == 55; return api_bars; }
template <size_t N> int CopyTime(const string &symbol, int timeframe, int shift,
                                 int count, datetime (&values)[N]) {
  ExactSymbol(symbol); ++api_time_reads;
  api_contract_ok &= timeframe == PERIOD_H4 && (shift == 0 || shift == 1) && count == 1 && N == 1;
  values[0] = shift == 0 ? api_current : api_closed; return 1;
}
template <size_t N> int CopyBuffer(int handle, int buffer, int shift, int count, double (&values)[N]) {
  ++api_buffer_reads;
  api_contract_ok &= handle == 55 && buffer == 0 && shift == 1 && count == 1 && N == 1;
  if (!api_buffer_ok) return -1;
  values[0] = api_atr;
  if (api_roll_during_buffer) { api_closed = api_current; api_current += 14400; ++api_bars; }
  return 1;
}
'''

MAIN = r'''
int main() {
  OnStart();
  JPWRaizNLiveNativeProvider provider;
  JPWRaizNLiveCache cache;
  JPWRaizNLiveResetCache(cache);
  JPWRaizNLiveSample sample;
  provider.Configure("SYMBOL.m.exact", 55, true, true, 172901000, 30000);
  JPWRaizLiveAssert(JPWRaizNReadLive(provider,cache,"synthetic-binding",30,1.25,sample) &&
                   sample.current && JPWRaizLiveNear(sample.percent,2.738612787525831),
                   "native provider method bodies execute against synthetic terminal API");
  JPWRaizLiveAssert(api_contract_ok && api_buffer_reads==1 && api_quote_reads==1 && api_time_reads==4,
                   "exact symbol/H4/shift1/no host timeframe and single quote contract");
  provider.Configure("SYMBOL.m.exact",55,false,false,0,30000);
  JPWRaizLiveAssert(JPWRaizNReadLive(provider,cache,"synthetic-binding",30,1.25,sample) && !sample.current,
                   "native binding disconnected sample is Estimated");
  provider.Configure("SYMBOL.m.exact",55,true,true,172901000,30000);
  JPWRaizLiveAssert(JPWRaizNReadLive(provider,cache,"synthetic-binding",30,1.25,sample) && sample.current,
                   "native binding returns Current after reanchor");
  api_closed=api_current; api_current+=14400; ++api_bars;
  api_quote_time=api_current*1000+1000;
  api_atr=0.8;
  provider.Configure("SYMBOL.m.exact",55,true,true,api_quote_time+1000,30000);
  JPWRaizLiveAssert(JPWRaizNReadLive(provider,cache,"synthetic-binding",30,1.25,sample) &&
                   sample.bar_time==172800 && api_buffer_reads==4,
                   "native CopyTime/CopyBuffer binding refreshes at H4 rollover");
  JPWRaizNLiveResetCache(cache);
  api_roll_during_buffer=true;
  JPWRaizLiveAssert(!JPWRaizNReadLive(provider,cache,"synthetic-binding",30,1.25,sample) && !cache.valid,
                   "native buffer/bar race is rejected by shared collector");
  api_roll_during_buffer=false;
  JPWRaizNLiveResetCache(cache);
  api_quote_time=api_current*1000+1000;
  provider.Configure("SYMBOL.m.exact",55,true,true,api_quote_time+1000,30000);
  const int quotes_before=api_quote_reads;
  double scale1=0.,pct1=0.,scale2=0.,pct2=0.;
  JPWRaizLiveAssert(JPWRaizNReadLiveBase(provider,cache,"synthetic-binding",sample) &&
                   JPWRaizNTimeScale(sample.p0,sample.atr,30,scale1,pct1)==JPW_RAIZN_OK &&
                   JPWRaizNTimeScale(sample.p0,sample.atr,60,scale2,pct2)==JPW_RAIZN_OK &&
                   api_quote_reads-quotes_before==1 && pct2>pct1,
                   "both uncalibrated horizons use exactly one validated quote/ATR sample");
  Print("HOST_ADAPTER: ",g_raiz_live_passes," PASS / ",g_raiz_live_failures," FAIL");
  Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN");
  return g_raiz_live_failures == 0 ? 0 : 1;
}
'''


SCRIPT_HOST_TRANSFORMS = [
    {
        "original_line": 129,
        "before": 'fake.atr_reads==1,"unchanged confirmed H4 uses ATR cache"',
        "after": 'fake.atr_reads==2,"unchanged H4 rereads closed ATR (HOST_COMPAT 1.18.1)"',
        "basis": "GENETRIX_REPAIR_1_18_1.md:16,38; per-capture ATR reread",
    },
    {
        "original_line": 139,
        "before": 'sample.current && sample.bar_time==172800 && fake.atr_reads==2,',
        "after": 'sample.current && sample.bar_time==172800 && fake.atr_reads==3,',
        "basis": "GENETRIX_REPAIR_1_18_1.md:16,38; third accepted capture",
    },
    {
        "before": '"JPW_Alavancagem_RaizN_Live_Tests PASS: "',
        "after": '"HOST_COMPAT_1_18_1 translated legacy script PASS: "',
        "basis": "identify the adapted host script; no original/native PASS claim",
    },
    {
        "before": '"JPW_Alavancagem_RaizN_Live_Tests FAIL: "',
        "after": '"HOST_COMPAT_1_18_1 translated legacy script FAIL: "',
        "basis": "identify the adapted host script; preserve original raw R2 failure",
    },
]
HOST_MAIN_TRANSFORM = {
    "before": "sample.bar_time==172800 && api_buffer_reads==2,",
    "after": "sample.bar_time==172800 && api_buffer_reads==4,",
    "basis": "four captures: Current, Estimated, reanchored Current, H4 rollover",
}


def adapted_script(script: str) -> str:
    """Apply only the frozen host compatibility deltas, failing on source drift."""
    for change in SCRIPT_HOST_TRANSFORMS:
        if script.count(change["before"]) != 1:
            raise AssertionError(f"HOST_ORACLE_SOURCE_DRIFT: {change['before']}")
        script = script.replace(change["before"], change["after"], 1)
    return script


def correction_control() -> tuple[str, dict[str, str]]:
    """Independent Decimal references; no production formula provides expected values."""
    with localcontext() as ctx:
        ctx.prec = 50
        before = Decimal("0.4") * Decimal(30).sqrt() * Decimal("1.25")
        after = Decimal("0.8") * Decimal(30).sqrt() * Decimal("1.25")
    refs = {"method": "Decimal precision 50: ATR * sqrt(30) * 1.25",
            "p0": "100", "initial_atr": "0.4", "corrected_atr": "0.8",
            "initial_distance_and_percent": str(before),
            "corrected_distance_and_percent": str(after)}
    code = r'''
void HostATRContentCorrectionControl() {
  JPWRaizNLiveFake fake;
  fake.Reset();
  JPWRaizNLiveCache cache;
  JPWRaizNLiveResetCache(cache);
  JPWRaizNLiveSample sample;
  const JPWRaizNLiveSeries original_series=fake.before;
  const long original_quote=fake.quote_time;
  const long original_now=fake.now;
  JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"host-same-metadata-correction",30,1.25,sample) &&
                   sample.current && fake.atr_reads==1 &&
                   JPWRaizLiveNear(sample.distance,INITIAL_REF) &&
                   JPWRaizLiveNear(sample.percent,INITIAL_REF),
                   "HOST_CONTRACT_1_18_1 independent baseline ATR example");
  fake.atr=0.8;
  JPWRaizLiveAssert(JPWRaizNReadLive(fake,cache,"host-same-metadata-correction",30,1.25,sample) &&
                   sample.current && fake.atr_reads==2 &&
                   JPWRaizLiveNear(sample.atr,0.8) &&
                   JPWRaizLiveNear(sample.distance,CORRECTED_REF) &&
                   JPWRaizLiveNear(sample.percent,CORRECTED_REF),
                   "HOST_CONTRACT_1_18_1 corrected ATR with unchanged series metadata");
  JPWRaizNLiveSeries snapshot=fake.before;
  JPWRaizNLiveSeries expected=original_series;
  JPWRaizLiveAssert(JPWRaizNLiveSeriesSame(snapshot,expected) &&
                   fake.quote_time==original_quote && fake.now==original_now &&
                   fake.bid==99.0 && fake.ask==101.0,
                   "HOST_CONTRACT_1_18_1 only ATR content changed");
  fake.atr_ok=false;
  JPWRaizLiveAssert(!JPWRaizNReadLive(fake,cache,"host-same-metadata-correction",30,1.25,sample) &&
                   !cache.valid && !sample.current && sample.p0==0.0 && sample.atr==0.0 &&
                   sample.distance==0.0 && sample.percent==0.0 &&
                   sample.reason=="ATR H4 indisponivel" && fake.atr_reads==3,
                   "HOST_CONTRACT_1_18_1 unavailable ATR invalidates current result");
}
'''
    return (code.replace("INITIAL_REF", str(before))
                .replace("CORRECTED_REF", str(after))), refs


def stale_cache_mutant(body: str) -> str:
    """Host-only falsification input: restore stale metadata-based ATR reuse."""
    before = "if(!provider.ReadClosedATR(atr))"
    after = """if(!(cache.valid && cache.context_key==context_key && cache.symbol==symbol &&
      cache.current_open==before.current_open && cache.closed_open==before.closed_open &&
      cache.bars==before.bars && cache.calculated==before.calculated &&
      cache.synchronized==before.synchronized ? (atr=cache.atr,true) :
      provider.ReadClosedATR(atr)))"""
    if body.count(before) != 1:
        raise AssertionError("HOST_MUTANT_SOURCE_DRIFT: ATR read occurrence")
    return body.replace(before, after, 1)


def compile_and_run(compiler: str, directory: Path, name: str, source: str) -> subprocess.CompletedProcess[str]:
    src = directory / f"{name}.cpp"
    executable = directory / name
    src.write_text(source, encoding="utf-8")
    result = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra",
                             "-Wno-unused-parameter", str(src), "-o", str(executable)],
                            text=True, capture_output=True, check=False, timeout=60)
    print(result.stdout, end="")
    print(result.stderr, end="")
    if result.returncode:
        print(f"HOST_COMPILATION: PRODUCT_FAIL; input={name}; exit={result.returncode}")
        return result
    result = subprocess.run([str(executable)], text=True, capture_output=True,
                            check=False, timeout=30)
    print(result.stdout, end="")
    print(result.stderr, end="")
    return result


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler; native MT5 NOT_RUN")
        return 2
    sources = [path.read_text(encoding="utf-8") for path in FILES]
    original_script = sources[2]
    sources[2] = adapted_script(original_script)
    control, reference = correction_control()
    host_main = MAIN.replace("  OnStart();", "  OnStart();\n  HostATRContentCorrectionControl();", 1)
    body = "\n".join(re.sub(r"^\s*#(?:include|property)\b[^\n]*", "", s,
                              flags=re.MULTILINE) for s in sources)
    identity = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in FILES}
    print(json.dumps({"test": "leverage_live_adapter", "source_sha256": identity,
                      "compiler": compiler, "kind": "HOST_COMPAT_1_18_1_NOT_MQL5",
                      "script_host_transforms": SCRIPT_HOST_TRANSFORMS,
                      "host_main_transform": HOST_MAIN_TRANSFORM,
                      "script_original_sha256": hashlib.sha256(original_script.encode()).hexdigest(),
                      "script_host_compatible_sha256": hashlib.sha256(sources[2].encode()).hexdigest(),
                      "host_control_reference": reference,
                      "original_script_native_execution": "NOT_RUN",
                      "legacy_r2_raw_result": "PRODUCT_FAIL_PRESERVED",
                      "financial_assertions": "UNCHANGED"}, indent=2))
    version = subprocess.run([compiler, "--version"], text=True, capture_output=True, check=False)
    print(version.stdout, end="")
    print(version.stderr, end="")
    with tempfile.TemporaryDirectory(prefix="jpw-raizn-live-synthetic-") as tmp:
        source = SHIM + "\n" + body + "\n" + control + "\n" + host_main
        mutant = SHIM + "\n" + stale_cache_mutant(body) + "\n" + control + "\n" + host_main
        print(json.dumps({"host_cpp_sha256": hashlib.sha256(source.encode()).hexdigest(),
                          "controlled_stale_cache_cpp_sha256": hashlib.sha256(mutant.encode()).hexdigest()},
                         indent=2))
        result = compile_and_run(compiler, Path(tmp), "collector", source)
        if result.returncode:
            print(f"HOST_COMPAT_EXIT_CODE: {result.returncode}")
            return result.returncode
        print("CONTROLLED_STALE_CACHE_MUTANT_BEGIN: EXPECTED_HOST_FAILURE")
        negative = compile_and_run(compiler, Path(tmp), "stale_cache_control", mutant)
        required = [
            "FAIL: HOST_CONTRACT_1_18_1 corrected ATR with unchanged series metadata",
            "FAIL: HOST_CONTRACT_1_18_1 unavailable ATR invalidates current result",
        ]
        detected = negative.returncode != 0 and all(label in negative.stdout for label in required)
        print(json.dumps({"control": "DELIBERATELY_STALE_CACHE_HOST_ONLY",
                          "exit_code": negative.returncode,
                          "required_failures_observed": detected,
                          "source_originals_modified": False,
                          "result": "EXPECTED_FAILURE_DETECTED" if detected else "JUDGE_CONTROL_FAIL"}, indent=2))
        print("CONTROLLED_STALE_CACHE_MUTANT_END")
        print("ORIGINAL_DISTRIBUTED_SCRIPT_NATIVE_BEHAVIOR: NOT_RUN; RAW_R2_PRODUCT_FAIL_PRESERVED")
        print(f"HOST_COMPAT_EXIT_CODE: {0 if detected else 1}")
        return 0 if detected else 1


if __name__ == "__main__":
    raise SystemExit(main())

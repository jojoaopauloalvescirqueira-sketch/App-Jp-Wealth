#!/usr/bin/env python3
"""Execute the unchanged MQL-compatible collector and its synthetic script in C++.

This is a host behavioral test, NOT MetaEditor compilation/native MT5 evidence.
Only #property and #include directives are removed for the compatibility shim.
The collector, native-provider method bodies, formula and MQL test assertions
remain identical to the distributed sources. Terminal API calls are synthetic.
"""

from __future__ import annotations

import hashlib
import json
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
                   sample.bar_time==172800 && api_buffer_reads==2,
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


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler; native MT5 NOT_RUN")
        return 2
    sources = [path.read_text(encoding="utf-8") for path in FILES]
    # This transformation only changes source loading and metadata, not logic.
    body = "\n".join(re.sub(r"^\s*#(?:include|property)\b[^\n]*", "", s,
                              flags=re.MULTILINE) for s in sources)
    identity = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in FILES}
    print(json.dumps({"test": "leverage_live_adapter", "source_sha256": identity,
                      "compiler": compiler, "kind": "HOST_SYNTHETIC_NOT_MQL5"}, indent=2))
    version = subprocess.run([compiler, "--version"], text=True, capture_output=True, check=False)
    print(version.stdout, end="")
    print(version.stderr, end="")
    with tempfile.TemporaryDirectory(prefix="jpw-raizn-live-synthetic-") as tmp:
        src = Path(tmp) / "collector.cpp"
        executable = Path(tmp) / "collector"
        src.write_text(SHIM + "\n" + body + "\n" + MAIN, encoding="utf-8")
        result = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra",
                                 "-Wno-unused-parameter", str(src), "-o", str(executable)],
                                text=True, capture_output=True, check=False, timeout=60)
        print(result.stdout, end="")
        print(result.stderr, end="")
        if result.returncode:
            print(f"HOST_COMPILATION: PRODUCT_FAIL; exit={result.returncode}")
            return result.returncode
        result = subprocess.run([str(executable)], text=True, capture_output=True,
                                check=False, timeout=30)
        print(result.stdout, end="")
        print(result.stderr, end="")
        print(f"EXIT_CODE: {result.returncode}")
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

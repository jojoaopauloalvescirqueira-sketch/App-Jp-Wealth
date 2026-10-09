#!/usr/bin/env python3
"""Replay synthetic observations through production math and sample contracts.

The MQL function bodies are loaded from the source graph, not mirrored here.
Terminal dispatch, MT5 chart objects and native file semantics remain NOT_RUN.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from leverage_panel_test import body_of
from leverage_source import expanded_source

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
INCLUDE = MQL / "Include/JPWealth"

SHIM = r'''
#include <cmath>
#include <climits>
#include <limits>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
using ulong=unsigned long;
bool MathIsValidNumber(double value){return std::isfinite(value);}
double MathAbs(double value){return std::abs(value);}
double MathMax(double a,double b){return std::fmax(a,b);}
template<class T> int ArraySize(const std::vector<T>& values){return (int)values.size();}
constexpr long ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2;
constexpr long ACCOUNT_MARGIN_MODE_RETAIL_NETTING=0;
'''

MAIN = r'''
constexpr int ORDER_TYPE_BUY_LIMIT=2;
int checks=0,failures=0;
void check(bool ok,const char* reason){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<reason<<'\n';}}
int main(){
 long sequence=0; JPWMetricSample sample{};
 double value=0;
 check(JPWLeverage(25000,10000,value)==JPW_OK && value==2.5,"production leverage oracle");
 check(JPWSampleAccept(sample,sequence,"synthetic-A",value,true,"x",1,JPW_SAMPLE_CONFIRMED,
                       "terminal",1000,1000000,1000) && sample.valid && sample.has_value &&
       sample.numeric_value==2.5 && sample.id==1,"accepted source retains value, unit and identity");
 const long accepted=sample.id;
 JPWMetricSample displayed=sample;
 check(displayed.id==accepted && sequence==1,"reading a snapshot does not mint evidence");
 check(JPWLeverage(25000,0,value)==JPW_BAD_EQUITY,"nonpositive equity is not zero exposure");
 JPWSampleInvalidate(sample,JPW_SAMPLE_UNAVAILABLE);
 check(!sample.valid&&!sample.has_value&&sample.quality==0&&sample.id==accepted,
       "failed refresh revokes number and Current without inventing a new capture");
 check(JPWLeverage(0,10000,value)==JPW_OK && value==0,
       "confirmed empty universe yields a genuine numerical zero");
 check(JPWSampleAccept(sample,sequence,"synthetic-A",value,true,"x",1,JPW_SAMPLE_CONFIRMED,
                       "terminal",1001,1001000,2000) && sample.numeric_value==0 &&
       sample.has_value && sample.id==2,"zero remains distinct from unavailable");
 check(JPWSampleAccept(sample,sequence,"synthetic-A",2.5,true,"x",2,JPW_SAMPLE_ESTIMATED,
                       "terminal-cache",1002,1001000,3000) && sample.quality==2,
       "disconnect estimate preserves source age and has its own accepted identity");
 JPWSampleInvalidate(sample,JPW_SAMPLE_CONTEXT_CHANGED);
 check(!sample.valid&&!JPWSampleContextValid(sample,"synthetic-B"),
       "account switch cannot reuse previous account sample");
 check(JPWSampleAccept(sample,sequence,"synthetic-B",1.25,true,"x",1,JPW_SAMPLE_CONFIRMED,
                       "terminal",1003,1003000,4000) && sample.context_key=="synthetic-B" &&
       sample.id==4,"new account accepts independently identified data");
 JPWSampleInvalidate(sample,JPW_SAMPLE_EXPIRED);
 check(!sample.valid&&!sample.has_value&&sample.reason_code==JPW_SAMPLE_EXPIRED,
       "expiry explicitly removes data validity");
 check(!JPWSampleAccept(sample,sequence,"synthetic-B",std::numeric_limits<double>::quiet_NaN(),
                       true,"x",1,JPW_SAMPLE_CONFIRMED,"terminal",1004,1004000,5000) && !sample.valid,
       "requested numeric NaN cannot become Current without a number");
 check(!JPWSampleAccept(sample,sequence,"",1,true,"x",1,JPW_SAMPLE_CONFIRMED,
                       "terminal",1004,1004000,5000),"missing context fails closed");
 sequence=LONG_MAX;
 check(!JPWSampleAccept(sample,sequence,"synthetic-B",1,true,"x",1,JPW_SAMPLE_CONFIRMED,
                       "terminal",1004,1004000,5000)&&sequence==LONG_MAX,
       "sequence exhaustion cannot wrap identity");
 double usd=0,usc=0;
 check(JPWFloatingPercent(10000,-100,usd)&&JPWFloatingPercent(1000000,-10000,usc)&&usd==usc&&usd==-1,
       "USC presentation changes no floating-percent formula");
 check(JPWBalanceDDPercent(10000,9700,usd)&&JPWBalanceDDPercent(1000000,970000,usc)&&usd==usc&&usd==3,
       "USC presentation changes no DD-percent formula");
 JPWStopRiskSample risk; JPWStopRiskClearSample(risk); risk.balance=10000; risk.currency="USD";
 risk.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING; risk.row_count=2;
 std::vector<JPWStopRiskRow> rows(2);
 for(int i=0;i<2;i++){auto &r=rows[i];JPWStopRiskClearRow(r);r.kind=JPW_STOP_RISK_POSITION;
  r.ticket=i+1;r.identifier=i+100;r.opened_msc=1000+i;r.symbol="SYNTH.EXACT";r.side=1;
  r.order_type=-1;r.valid=1;r.volume=.1;r.entry=100;r.sl=90;r.risk_money=100;}
 double total,pct,open,pending,extra; string reason;
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&total==200,
       "production aggregate confirms full synthetic universe");
 rows[1].valid=0;rows[1].sl=0;rows[1].reason="synthetic missing SL";
 check(!JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason),
       "one unavailable position refuses a falsely complete total");
 // Metamorphic checks use production bodies with deliberately different
 // magnitudes, account units and inventory composition. They do not mirror
 // the implementation formula in the test harness.
 for(double equity : {100.0,10000.0,500000.0})
  for(double gross : {0.0,60.0,25000.0}){
   double original=-1,cent=-1;
   const bool both=JPWLeverage(gross,equity,original)==JPW_OK&&
                   JPWLeverage(gross*100.0,equity*100.0,cent)==JPW_OK;
   check(both&&std::abs(original-cent)<1e-12,
         "joint USC scaling preserves leverage, including confirmed zero");
  }
 for(double profit : {-250.0,-0.25,0.0,325.0}){
   double original=-1,cent=-1;
   check(JPWFloatingPercent(10000.0,profit,original)&&
         JPWFloatingPercent(1000000.0,profit*100.0,cent)&&
         std::abs(original-cent)<1e-12,
         "joint USC scaling preserves signed floating percentage");
  }
 double dd_at_9900=0,dd_at_9700=0,dd_at_9500=0,dd_at_11000=-1;
 check(JPWBalanceDDPercent(10000,9900,dd_at_9900)&&
       JPWBalanceDDPercent(10000,9700,dd_at_9700)&&
       JPWBalanceDDPercent(10000,9500,dd_at_9500)&&
       JPWBalanceDDPercent(10000,11000,dd_at_11000)&&
       dd_at_9900<dd_at_9700&&dd_at_9700<dd_at_9500&&dd_at_11000==0,
       "deeper equity deficit raises DD while equity above balance remains zero");
 rows[1].valid=1;rows[1].sl=90;rows[1].reason="";
 rows.push_back(rows[0]);rows[2].kind=JPW_STOP_RISK_PENDING;rows[2].identifier=0;
 rows[2].order_type=ORDER_TYPE_BUY_LIMIT;
 rows[2].ticket=3;rows[2].opened_msc=3000;rows[2].risk_money=25;
 risk.row_count=3;
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&
       total==225&&open==200&&pending==25&&pct==2.25,
       "complete operation includes each independent pending reserve");
 rows[2].risk_money=0;
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&
       total==200&&pending==0,
       "protective zero-risk pending cannot invent additional loss");
 risk.balance=20000;
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&
       total==200&&pct==1,
       "balance changes informative percentage without changing nominal risk");
 risk.balance=1000000;rows[0].risk_money=10000;rows[1].risk_money=10000;
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&
       total==20000&&pct==2,
       "USC money and balance scale together without a second currency conversion");
 risk.row_count=2;
 check(!JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason),
       "inventory count mismatch refuses a partial published total");
 risk.row_count=3;risk.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_NETTING;
 check(!JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason),
       "netting position cannot masquerade as per-order hedging risk");
 risk.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
 rows[2].symbol="OTHER.EXACT";rows[2].valid=0;rows[2].reason="missing SL";
 check(JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason)&&
       total==20000&&pending==0,
       "a different instrument with unavailable SL stays outside this operation");
 rows[2].kind=99;
 check(!JPWStopRiskAggregate(risk,rows,"SYNTH.EXACT",1,total,pct,open,pending,extra,reason),
       "structurally corrupt inventory is refused even outside the operation");
 double signed_loss=99;
 check(!JPWStopRiskLossFromProfit(std::numeric_limits<double>::infinity(),signed_loss),
       "invalid native profit cannot become a monetary stop risk");
 check(JPWTechnicalHealthEvaluate(false,true,true,0,false,true,false)==JPW_HEALTH_UNAVAILABLE,
       "technical health cannot be normal without a valid context");
 check(JPWTechnicalHealthEvaluate(true,true,true,0,false,true,false)==JPW_HEALTH_NORMAL,
       "technical normal requires all explicit health conditions");
 check(JPWTechnicalHealthEvaluate(true,false,true,0,false,true,false)==JPW_HEALTH_ATTENTION&&
       JPWTechnicalHealthEvaluate(true,true,false,0,false,true,false)==JPW_HEALTH_ATTENTION&&
       JPWTechnicalHealthEvaluate(true,true,true,1,false,true,false)==JPW_HEALTH_ATTENTION&&
       JPWTechnicalHealthEvaluate(true,true,true,0,true,true,false)==JPW_HEALTH_ATTENTION&&
       JPWTechnicalHealthEvaluate(true,true,true,0,false,false,false)==JPW_HEALTH_ATTENTION&&
       JPWTechnicalHealthEvaluate(true,true,true,0,false,true,true)==JPW_HEALTH_ATTENTION,
       "each independent failure/pending/stale/deferred signal prevents normal health");
 std::cout<<"HOST_RELIABILITY_REPLAY: "<<checks-failures<<" PASS / "<<failures<<" FAIL\n";
 return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("JPW_TEST_RESULT: ENVIRONMENT_ERROR")
        return 2
    paths = [INCLUDE / f"JPW_Alavancagem_{part}.mqh" for part in ("Core", "Samples", "StopRisk_Core")]
    core, samples, risk = [path.read_text(encoding="utf-8") for path in paths]
    enum = core[core.index("enum JPW_RESULT"):core.index("enum JPW_MODEL")]
    functions = []
    for signature in (
        "bool JPWFinitePositive(const double value)",
        "JPW_RESULT JPWLeverage(const double gross,const double equity,double &leverage)",
        "bool JPWFloatingPercent(const double balance,const double profit,double &percent)",
        "bool JPWBalanceDDPercent(const double balance,const double equity,double &percent)",
    ):
        functions.append(signature + "{" + body_of(core, signature) + "}")
    risk = re.sub(r"^#include[^\n]*$", "", risk, flags=re.MULTILINE)
    risk = risk.replace("JPWStopRiskRow &rows[]", "std::vector<JPWStopRiskRow> &rows")
    print(json.dumps({"kind": "HOST_PRODUCTION_CORE_REPLAY", "source_sha256": {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}}, indent=2))
    with tempfile.TemporaryDirectory(prefix="jpw-reliability-") as directory:
        path, binary = Path(directory) / "replay.cpp", Path(directory) / "replay"
        path.write_text(SHIM + enum + "\n".join(functions) + "\n" + samples + risk + MAIN, encoding="utf-8")
        for command in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)], [str(binary)]):
            result = subprocess.run(command, text=True, capture_output=True, timeout=60, check=False)
            print(result.stdout, end=""); print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    status = presentation_replay(compiler, samples)
    if status:
        return status
    print("NATIVE_MT5: NOT_RUN")
    return 0


def presentation_runtime(source: str, samples: str) -> str:
    functions = []
    for signature in (
        "void JPWViewMetric(const int index,const string title,const string value,\n                   const string reason,const string detail,const JPW_VIEW_QUALITY quality)",
        "void JPWBuildPresentation(const string leverage_value,const string leverage_detail)",
        "void JPWRenderCurrentDisplay()",
        'void JPWRender(const string value,const string state="")',
    ):
        functions.append(signature + "{" + body_of(source, signature) + "}")
    cockpit = (INCLUDE / "JPW_Alavancagem_Cockpit.mqh").read_text()
    cockpit = cockpit[:cockpit.index("// Stable route")] + "\n#endif\n"
    cockpit = re.sub(r"^#include[^\n]*$", "", cockpit, flags=re.MULTILINE)
    globals_source = "\n".join(functions)
    known = {"g_cockpit_snapshot", "g_metric_samples", "g_collection_sequence"}
    declarations = []
    for name in sorted(set(re.findall(r"\bg_\w+", globals_source)) - known):
        declarations.append(("JPW_VIEW_QUALITY " + name + "=JPW_VIEW_CURRENT;" if name.endswith("_quality") else "string " + name + ';'))
    context = "\n".join(declarations) + r'''
JPWCockpitSnapshot g_cockpit_snapshot;
JPWMetricSample g_metric_samples[JPW_COCKPIT_METRIC_COUNT];long g_collection_sequence=0;
string _Symbol="SYNTHETIC";int draws=0;
ulong host_now=1000;ulong GetTickCount64(){return host_now;}
void JPWRenderHUD(){draws++;}void JPWRenderRaizDetails(){}void ChartRedraw(int){}
// This legacy replay keeps the new ledger projection at a component boundary.
// jpw_genetrix_ui_test executes its actual helper/collector/selector separately;
// none of the six original metric evidence or expiry assertions is changed.
void JPWGenetrixPresentMetric(){g_cockpit_snapshot.metric[6].title="Flutuante compensado";
 g_cockpit_snapshot.metric[6].value="N/A";g_cockpit_snapshot.metric[6].quality=JPW_VIEW_NA;}
'''
    from leverage_host_runtime import passes
    return samples + cockpit + context + passes() + "\n".join(functions)


def presentation_replay(compiler: str, samples: str) -> int:
    entry = MQL / "Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"
    source = expanded_source(entry)
    runtime = presentation_runtime(source, samples)
    main = r'''
int main(){
 g_sample_context="synthetic";g_panel_prefix="synthetic";g_panel_value="2.50x";
 JPWSampleAccept(g_metric_samples[0],g_collection_sequence,g_sample_context,2.5,true,"x",1,
                 JPW_SAMPLE_CONFIRMED,"terminal",1000,1000000,1000);
 JPWRender("2.50x","accepted");long first=g_cockpit_snapshot.sequence;
 for(int i=0;i<10;i++){host_now+=100;JPWRender("ignored UI argument","no new observation");}
 if(draws!=11||first!=g_cockpit_snapshot.sequence||g_cockpit_snapshot.metric[0].sample.id!=1||
    g_cockpit_snapshot.metric[0].sample.numeric_value!=2.5||g_panel_value!="2.50x"){
   std::cerr<<"FAIL rendering minted evidence or changed accepted value\n";return 1;}
 host_now=32000;JPWRender("","same accepted sample, deadline passed");
 if(g_cockpit_snapshot.metric[0].quality!=JPW_VIEW_NA||g_cockpit_snapshot.metric[0].value!="N/A"||
    g_cockpit_snapshot.sequence!=first||g_collection_sequence!=1){
   std::cerr<<"FAIL redraw advertised an expired sample or minted new evidence\n";return 1;}
 host_now=999;JPWRender("","monotonic clock regressed");
 if(g_cockpit_snapshot.metric[0].quality!=JPW_VIEW_NA||g_cockpit_snapshot.metric[0].value!="N/A"||
    g_cockpit_snapshot.sequence!=first){
   std::cerr<<"FAIL redraw advertised a sample from a previous clock epoch\n";return 1;}
 JPWSampleInvalidate(g_metric_samples[0],JPW_SAMPLE_EXPIRED);g_panel_value="N/A";g_leverage_quality=JPW_VIEW_NA;
 JPWRender("","expired");
 if(g_cockpit_snapshot.metric[0].sample.valid||g_cockpit_snapshot.metric[0].quality!=JPW_VIEW_NA||
    g_cockpit_snapshot.metric[0].sample.id!=1){std::cerr<<"FAIL expired snapshot presentation\n";return 1;}
 std::cout<<"HOST_PRESENTATION_REPLAY: actual renderer preserves ID/value across 11 draws; elapsed expiry and clock regression become N/A\n";
 return 0;
}
'''
    with tempfile.TemporaryDirectory(prefix="jpw-presentation-replay-") as directory:
        path, binary = Path(directory) / "render.cpp", Path(directory) / "render"
        path.write_text(SHIM + runtime + main)
        print("EXPANDED_INDICATOR_SHA256:", hashlib.sha256(source.encode()).hexdigest())
        for command in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)], [str(binary)]):
            result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=60)
            print(result.stdout, end=""); print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exact production math/readmodel/metadata/coordinator replay on synthetic APIs.

No copied financial formula and no real account/files. Native MetaEditor,
MT5 dispatch, UI and performance remain NOT_RUN. API boundaries are explicit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import leverage_config_test as base
from leverage_scheduler_test import function
ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
INC = MQL / "Include/JPWealth"
FILES = [INC / "JPW_Alavancagem_Core.mqh", INC / "JPW_Alavancagem_Samples.mqh",
         INC / "JPW_Alavancagem_Positions.mqh",
         MQL / "Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5",
         INC / "JPW_Alavancagem_Terminal.mqh", INC / "JPW_Alavancagem_Coordinator.mqh"]
EXTRA = r'''
constexpr int JPW_VIEW_NA=0,JPW_VIEW_CURRENT=1,JPW_VIEW_ESTIMATED=2;
constexpr int ACCOUNT_LOGIN=1,ACCOUNT_SERVER=2,ACCOUNT_CURRENCY=3,ACCOUNT_MARGIN_MODE=4;
constexpr int TERMINAL_CONNECTED=1,SYMBOL_VOLUME_STEP=1,TIME_DATE=1,TIME_SECONDS=2;
enum ENUM_POSITION_PROPERTY_INTEGER {POSITION_IDENTIFIER=1,POSITION_TYPE=2,POSITION_TIME_MSC=3,POSITION_TIME_UPDATE_MSC=4};
enum ENUM_POSITION_PROPERTY_DOUBLE {POSITION_VOLUME=1,POSITION_PRICE_OPEN=2,POSITION_SL=3,POSITION_TP=4};
enum ENUM_POSITION_PROPERTY_STRING {POSITION_SYMBOL=1};
int host_error=0,host_selected=-1,host_sl_reads=0,host_mutate_sl_on_read=0;
int host_login_reads=0,host_switch_login_on_read=0,host_api_reads=0;
int host_margin_reads=0,host_switch_margin_on_read=0;
bool host_fail_optional=false,host_connected=true;
long host_login=123,host_margin_mode=2;
struct HostPosition {ulong ticket;long identifier,side,opened,updated;string symbol;double volume,entry,sl,tp,step;};
std::vector<HostPosition> host_positions;
void ResetLastError(){host_error=0;}int GetLastError(){return host_error;}
double MathMax(double a,double b){return std::fmax(a,b);}
double MathRound(double a){return std::round(a);}
long TimeGMT(){return 2000;}
string TimeToString(datetime t,int){return std::to_string(t);}
int PositionsTotal(){host_api_reads++;return (int)host_positions.size();}
ulong PositionGetTicket(int n){host_api_reads++;if(n<0||n>=(int)host_positions.size())return 0;host_selected=n;return host_positions[n].ticket;}
bool PositionSelectByTicket(ulong ticket){host_api_reads++;for(int i=0;i<(int)host_positions.size();i++)if(host_positions[i].ticket==ticket){host_selected=i;return true;}return false;}
bool PositionGetInteger(ENUM_POSITION_PROPERTY_INTEGER p,long&v){host_api_reads++;if(host_selected<0)return false;
 const auto&r=host_positions[host_selected];v=p==POSITION_IDENTIFIER?r.identifier:(p==POSITION_TYPE?r.side:(p==POSITION_TIME_MSC?r.opened:r.updated));return true;}
bool PositionGetString(ENUM_POSITION_PROPERTY_STRING,string&v){host_api_reads++;if(host_selected<0)return false;v=host_positions[host_selected].symbol;return true;}
bool PositionGetDouble(ENUM_POSITION_PROPERTY_DOUBLE p,double&v){host_api_reads++;if(host_selected<0)return false;
 if(host_fail_optional&&p!=POSITION_VOLUME){host_error=4806;return false;}
 auto&r=host_positions[host_selected];if(p==POSITION_SL&&host_mutate_sl_on_read>0&&++host_sl_reads==host_mutate_sl_on_read)r.sl+=.001;
 v=p==POSITION_VOLUME?r.volume:(p==POSITION_PRICE_OPEN?r.entry:(p==POSITION_SL?r.sl:r.tp));return true;}
bool SymbolInfoDouble(const string&s,int p,double&v){host_api_reads++;for(const auto&r:host_positions)if(r.symbol==s&&p==SYMBOL_VOLUME_STEP){v=r.step;return v>0;}return false;}
long AccountInfoInteger(int p){host_api_reads++;if(p==ACCOUNT_MARGIN_MODE){if(host_switch_margin_on_read>0&&++host_margin_reads==host_switch_margin_on_read)host_margin_mode++;return host_margin_mode;}
 if(p==ACCOUNT_LOGIN){if(host_switch_login_on_read>0&&++host_login_reads==host_switch_login_on_read)host_login++;return host_login;}return 0;}
string AccountInfoString(int p){host_api_reads++;return p==ACCOUNT_SERVER?"SyntheticServer":(p==ACCOUNT_CURRENCY?"USD":"");}
long TerminalInfoInteger(int p){host_api_reads++;return p==TERMINAL_CONNECTED&&host_connected;}
'''
COORD_BOUNDARY = r'''
JPWAccount g_account,g_genesis_refresh_account;
string g_sample_context="chart-A",g_diagnostic_context="account-A";
ulong g_cycle_started_ms=10000,g_last_full_refresh_ms=10000;
long g_collection_sequence=0,g_last_full_refresh_utc=2000;
bool g_account_known=true,g_genesis_due=false,g_raiz_due=false,g_refresh_requested=false;
bool g_genesis_refresh_connected=true,g_genesis_refresh_clock_valid=true;
long g_genesis_refresh_now_ms=1000000;ulong g_genesis_refresh_started=10000;
int g_leverage_quality=1,g_floating_quality=0,g_genesis_quality=0,g_raiz_quality=0,g_scale2_quality=0,g_stop_quality=0,g_compensated_quality=0;
double g_numeric_values[7]={};bool g_numeric_valid[7]={};long g_source_times[7]={};
JPWMetricSample g_metric_samples[7];int g_metric_last_quality[7]={};
// Ledger is an explicit separate component boundary for this inventory replay;
// its production projection/collection is tested in jpw_genetrix_ui_test.
bool g_genetrix_ledger_available=false;
struct HostLedgerSample{long observed_mono_ms=0;}g_genetrix_view;
string g_panel_value,g_panel_status,g_leverage_reason;
string g_floating_value,g_floating_reason,g_floating_line,g_floating_short,g_floating_tooltip;
string g_dd_line,g_dd_short,g_dd_tooltip,g_genesis_value,g_genesis_reason,g_genesis_line,g_genesis_short,g_genesis_tooltip;
string g_raiz_value,g_raiz_reason,g_raiz_line,g_raiz_short,g_raiz_tooltip,g_scale2_value,g_scale2_reason,g_scale2_line,g_scale2_short,g_scale2_tooltip;
bool g_stop_ready=false;struct HostStopSample{long observed_mono_ms=0;}g_stop_sample;
constexpr int JPW_DIAG_QUALITY_CHANGED=1,JPW_DIAG_DATA_UNAVAILABLE=2,JPW_DIAG_BUDGET_DEFERRED=3;
int host_draws=0,host_records=0,host_optional_collectors=0;
void JPWQueueDiagnostic(int){}
void JPWCollectGenesis(JPWAccount&,bool,bool,long,ulong){host_optional_collectors++;}
void JPWCollectRaizN(){host_optional_collectors++;}
void JPWInvalidateIdentityPresentation(){JPWPositionsInvalidate("Contexto alterado");g_sample_context="";g_leverage_quality=0;g_numeric_valid[0]=false;}
void JPWMonitorStopRisk(){JPWPositionsMonitorInventory();}
void JPWRefreshRequestedRecords(){host_records++;}
bool JPWConfirmAcceptedContext(){return true;}
void JPWRenderCurrentDisplay(){host_draws++;}
'''
COORD_MAIN = r'''
void HostFixture(int count){host_positions.clear();host_error=0;host_selected=-1;host_login=123;host_login_reads=0;host_switch_login_on_read=0;
 host_margin_mode=2;host_margin_reads=0;host_switch_margin_on_read=0;
 host_sl_reads=0;host_mutate_sl_on_read=0;host_fail_optional=false;host_connected=true;
 for(int i=0;i<count;i++)host_positions.push_back({(ulong)i+10,i+100,POSITION_TYPE_BUY,1000+i,1000+i,"EURUSD",.1,1.1,.9,0,.01});}
void HostStart(){g_cycle_started_ms=host_now_ms;g_last_full_refresh_ms=host_now_ms;
 g_sample_context="chart-A";g_diagnostic_context="account-A";JPWReadAccount(g_account);
 JPWPositionsInvalidate("new synthetic cycle");g_positions_catalog_attempted=false;
 g_genesis_due=false;g_raiz_due=false;g_leverage_quality=1;g_numeric_values[0]=0;g_numeric_valid[0]=false;}
void HostPrepareMath(){std::vector<JPWPosition> positions;JPWReadSnapshot(positions);
 std::vector<JPWInstrument> instruments(positions.size());std::vector<JPWQuote> quotes(1);
 std::vector<double> scales(positions.size(),1),amounts;std::vector<JPWRoute> routes;
 for(size_t i=0;i<positions.size();i++){JPWQuote q;PositionsFixture(positions[i],instruments[i],q,positions[i].ticket,"EURUSD","EUR","USD",positions[i].volume,1.1,positions[i].direction);if(i==0)quotes[0]=q;}
 if(positions.empty())quotes.clear();double gross=0;bool estimated=false;long oldest=0;
 const bool ok=JPWGrossReading(positions,instruments,quotes,"USD",1000000,30,true,true,scales,routes,gross,estimated,oldest)==JPW_OK&&
 JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,scales,routes,gross,amounts)==JPW_OK;
 double total=0;JPWLeverage(gross,10000,total);
 PositionsCheck(ok&&JPWPositionsStageLeverage(10000,total,amounts),"coordinator stages actual core output from same inventory");
 g_numeric_values[0]=total;g_numeric_valid[0]=true;g_source_times[0]=oldest;}
void HostCoordinatorTests(){
 HostFixture(3);host_now_ms=20000;HostStart();JPWPositionsCollectCatalogOnly();HostPrepareMath();
 const int reads=host_api_reads;JPWAcceptCollection("3.30x","accepted");
 PositionsCheck(g_positions_view.catalog_valid&&g_positions_view.sample_id==g_metric_samples[0].id&&
 g_position_views.size()==3&&g_positions_view.account_key=="account-A"&&g_positions_view.leverage_valid,
 "actual coordinator publishes inventory with accepted metric-0 identity");
 PositionsCheck(host_api_reads==reads+3,"acceptance redraw does not recollect metadata in the same cycle");
 const long id=g_positions_view.sample_id;const int before_draw_reads=host_api_reads;
 JPWRenderCurrentDisplay();JPWPositionsViewCurrent(g_sample_context,host_now_ms);
 PositionsCheck(g_positions_view.sample_id==id&&host_api_reads==before_draw_reads,"redrawing accepted view neither collects nor creates identity");
 host_positions.resize(2);host_now_ms+=100;g_cycle_started_ms=host_now_ms;
 JPWPositionsMonitorInventory();
 PositionsCheck(!g_positions_view.catalog_valid&&g_refresh_requested,"live composition change revokes stale contribution and requests refresh");
 HostStart();JPWPositionsCollectCatalogOnly();HostPrepareMath();JPWAcceptCollection("2.20x","accepted");
 PositionsCheck(g_position_views.size()==2&&JPWPositionsViewFind(12,102)<0,"coordinator shrink 3 to 2 removes closed row");
 host_positions.clear();host_now_ms+=100;HostStart();JPWPositionsCollectCatalogOnly();HostPrepareMath();JPWAcceptCollection("0.00x","accepted");
 PositionsCheck(g_positions_view.catalog_valid&&g_positions_view.leverage_valid&&g_position_views.empty(),"coordinator confirmed shrink 2 to 0");
 HostFixture(1);host_fail_optional=true;host_now_ms+=100;HostStart();JPWPositionsCollectCatalogOnly();
 g_leverage_quality=0;JPWAcceptCollection("N/A","financial unavailable");
 PositionsCheck(g_positions_view.catalog_valid&&g_position_views.size()==1&&!g_position_views[0].sl_valid&&
 !g_position_views[0].entry_valid&&!g_position_views[0].leverage_valid,"failed optional SL/TP/entry and finance keep metadata catalog visible");
 HostFixture(1);host_now_ms+=100;HostStart();host_mutate_sl_on_read=2;JPWPositionsCollectCatalogOnly();JPWAcceptCollection("N/A","inconsistent");
 PositionsCheck(!g_positions_view.catalog_valid&&g_position_views.empty(),"two unequal SL snapshots cannot publish coherent inventory");
 HostFixture(1);host_now_ms+=100;HostStart();host_login_reads=0;host_switch_login_on_read=2;JPWPositionsCollectCatalogOnly();JPWAcceptCollection("N/A","account switch");
 PositionsCheck(!g_positions_view.catalog_valid&&g_position_views.empty(),"account switch during catalog capture fails closed");
 HostFixture(1);host_now_ms+=100;HostStart();host_switch_margin_on_read=2;
 JPWPositionsCollectCatalogOnly();JPWAcceptCollection("N/A","account mode changed");
 PositionsCheck(!g_positions_view.catalog_valid,"account mode change during inventory capture fails closed");
 HostFixture(0);host_now_ms+=100;HostStart();host_connected=false;JPWPositionsCollectCatalogOnly();JPWAcceptCollection("N/A","offline empty");
 PositionsCheck(!g_positions_view.catalog_valid,"offline empty cache cannot prove no positions");
 HostFixture(1);host_now_ms+=100;HostStart();JPWPositionsCollectCatalogOnly();HostPrepareMath();JPWAcceptCollection("1.10x","accepted");
 host_now_ms+=30001;JPWExpireTimedMetrics();
 PositionsCheck(!g_positions_view.catalog_valid&&g_position_views.empty(),"actual expiry coordinator clears accepted position rows");
 HostFixture(1);host_now_ms+=100;HostStart();g_cycle_started_ms=host_now_ms-450;
 JPWPositionsCollectCatalogOnly();JPWAcceptCollection("N/A","deferred");
 PositionsCheck(!g_positions_view.catalog_valid,"metadata cutoff reserves original financial budget");
 std::vector<JPWPosition> p(1);std::vector<JPWInstrument> ins(1);std::vector<JPWQuote> q(1);std::vector<double> scales(1,1),amounts;
 std::vector<JPWRoute> routes;PositionsFixture(p[0],ins[0],q[0],1,"EURUSD","EUR","USD",.1,1.1,POSITION_TYPE_BUY);
 g_numeric_values[0]=1.1;g_numeric_valid[0]=true;
 PositionsCheck(!JPWPositionsBudgetBreakdown(p,ins,q,"USD",1000000,30,true,true,scales,routes,11000,
 host_now_ms-250,amounts)&&amounts.empty()&&g_numeric_values[0]==1.1&&g_numeric_valid[0],
 "optional math at cutoff neither runs nor invalidates account leverage");
 PositionsCheck(JPWPositionsBudgetBreakdown(p,ins,q,"USD",1000000,30,true,true,scales,routes,11000,
 host_now_ms,amounts)&&amounts.size()==1&&JPWPositionsNear(amounts[0],11000),"bounded adapter reuses pure single-position core");
}
int main(){OnStart();HostCoordinatorTests();
 std::cout<<"HOST_POSITIONS_RESULT: "<<g_positions_pass<<" PASS / "<<g_positions_fail<<" FAIL\n";
 std::cout<<"NATIVE_METAEDITOR: NOT_RUN; NATIVE_MT5: NOT_RUN\n";return g_positions_fail?1:0;}
'''

def translate(source: str) -> str:
    source=re.sub(r"\b(\w+)\s+((?:\w+\[\],)+\w+\[\]);",
                  lambda m: "std::vector<"+m[1]+"> "+m[2].replace("[]","")+";",source)
    return base.translate(source)

def run(output: Path | None) -> int:
    compiler=shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: C++ compiler unavailable; MT5 NOT_RUN");return 2
    identity={"kind":"HOST_SYNTHETIC_NOT_MQL5","test":"positions core and coordinator replay",
              "source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES},
              "limitations":"Native APIs synthetic; actual production math/metadata/collection acceptance and expiration functions executed; no native terminal, UI or performance evidence."}
    print(json.dumps(identity,indent=2))
    if output:output.mkdir(parents=True,exist_ok=False);(output/"source-identity.json").write_text(json.dumps(identity,indent=2)+"\n")
    shim=base.SHIM.replace("ulong GetTickCount64(){static ulong value=100000;return ++value;}",
                            "ulong host_now_ms=10000;ulong GetTickCount64(){return host_now_ms;}")
    coordinator=FILES[-1].read_text();terminal=FILES[-2].read_text()
    names=("JPWCoordinatorBudgetRemaining","JPWPositionsMonitorInventory","JPWPositionsCollectCatalogOnly",
           "JPWAcceptMetric","JPWAcceptCollection","JPWPositionsBudgetBreakdown","JPWFullReadingExpired","JPWExpireTimedMetrics")
    source=(shim+EXTRA+"\n"+"\n".join(translate(p.read_text()) for p in FILES[:4])+"\n"+
            "void JPWPositionsMonitorInventory();\n"+COORD_BOUNDARY+"\n"+
            "\n".join(translate(function(terminal,n)) for n in ("JPWReadAccount","JPWReadSnapshot"))+"\n"+
            "\n".join(translate(function(coordinator,n)) for n in names)+COORD_MAIN)
    receipts=[]
    with tempfile.TemporaryDirectory(prefix="jpw-positions-synthetic-") as tmp:
        src,exe=Path(tmp)/"positions.cpp",Path(tmp)/"positions"
        src.write_text(source)
        if output:shutil.copy2(src,output/src.name)
        commands=([compiler,"--version"],[compiler,"-std=c++17","-Wall","-Wextra","-Wno-unused-parameter",
                   "-Wno-deprecated-declarations",str(src),"-o",str(exe)]+([] if sys.platform=="darwin" else ["-lcrypto"]),[str(exe)])
        for i,cmd in enumerate(commands):
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=60,check=False)
            print(result.stdout,end="");print(result.stderr,end="")
            receipts.append({"command":cmd,"exit_code":result.returncode})
            if output:
                (output/f"{i}-stdout.txt").write_text(result.stdout);(output/f"{i}-stderr.txt").write_text(result.stderr)
                (output/"commands.json").write_text(json.dumps(receipts,indent=2)+"\n")
            if result.returncode:return result.returncode
    return 0
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--evidence-dir",type=Path)
    raise SystemExit(run(parser.parse_args().evidence_dir))

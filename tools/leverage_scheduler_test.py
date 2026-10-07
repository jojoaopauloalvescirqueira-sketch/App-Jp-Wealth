#!/usr/bin/env python3
"""Production timer/queue control-flow replay with synthetic terminal boundaries.

Compiles the actual EA reconstruction and lifecycle functions. Storage is a
recording/failure-injection boundary here; leverage_diagnostics_test separately
executes the real SQLite writer. No MT5 timer dispatch is claimed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from leverage_panel_test import body_of

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
INCLUDE = MQL / "Include/JPWealth"
EA = MQL / "Experts/JPWealth/JPW_Alavancagem_Observer.mq5"
RUNTIME = INCLUDE / "JPW_Genetrix_Observer_Runtime.mqh"


def function(source: str, name: str) -> str:
    match = re.search(r"^(?:void|bool|int|ulong) " + re.escape(name) + r"\([^;{]*\)\s*(?=\{)", source, re.MULTILINE)
    if not match:
        raise ValueError("Production function missing: " + name)
    signature = match.group().strip()
    return signature + "{" + body_of(source, signature) + "}"


SHIM = r'''
#include <algorithm>
#include <climits>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using string=std::string;using ulong=unsigned long;
bool MathIsValidNumber(double value){return std::isfinite(value);}
double MathFloor(double value){return std::floor(value);}
int StringLen(const string&value){return (int)value.size();}
constexpr int INVALID_HANDLE=-1,POSITION_IDENTIFIER=1,POSITION_TYPE=2,POSITION_SYMBOL=3,POSITION_TYPE_BUY=0;
constexpr int JPW_PERSONAL_UNAVAILABLE=0;
template<class T> int ArraySize(const std::vector<T>&a){return (int)a.size();}
template<class T> int ArrayResize(std::vector<T>&a,int n){a.resize(n);return n;}
string IntegerToString(long x){return std::to_string(x);}
string StringSubstr(const string&s,int p,int n){return s.substr(p,n);}
template<typename... A> void Print(A...args){}
void JPWPersonalControllerDetach(const string&){}
ulong now_ms=1000;long now_utc=1000;
ulong GetTickCount64(){return now_ms;}long TimeGMT(){return now_utc;}
long ChartID(){return 42;}
bool JPWRaizNIsHash(const string&s){return s.size()==64;}
std::map<string,double> globals;
bool GlobalVariableCheck(const string&key){return globals.count(key);}
bool GlobalVariableTemp(const string&key){globals.emplace(key,0);return true;}
bool GlobalVariableGet(const string&key,double&value){if(!globals.count(key))return false;value=globals.at(key);return true;}
double GlobalVariableGet(const string&key){return globals.count(key)?globals.at(key):0;}
int cas_calls=0,cas_refusals=0,cas_races=0;
bool GlobalVariableSetOnCondition(const string&key,double value,double expected){
 cas_calls++;
 if(cas_races>0){cas_races--;globals[key]=expected+1;return false;}
 if(cas_refusals>0){cas_refusals--;return false;}
 if(!globals.count(key)||globals.at(key)!=expected)return false;globals[key]=value;return true;}
long GlobalVariableSet(const string&key,double value){globals[key]=value;return 1;}
bool GlobalVariableDel(const string&key){return globals.erase(key);}
int failure_markers(){int count=0;for(const auto&value:globals)if(value.first.find("JPW_DIAG_FAIL_")==0)count++;return count;}
int positions=1,store_calls=0,store_failures=0,history_failures=0;
enum JPWObserverPresenceState {JPW_OBSERVER_NOT_CONFIRMED=0,JPW_OBSERVER_WAITING=1,
                                JPW_OBSERVER_PUBLISHED=2,JPW_OBSERVER_FAILED=3,
                                JPW_OBSERVER_CONTEXT_UNAVAILABLE=4};
int PositionsTotal(){return positions;}
ulong PositionGetTicket(int i){return (ulong)i+100;}
bool PositionSelectByTicket(ulong){return true;}
bool PositionGetInteger(int what,long&value){value=what==POSITION_IDENTIFIER?99:POSITION_TYPE_BUY;return true;}
bool PositionGetString(int,string&value){value="SYNTH.EXACT";return true;}
struct JPWObserverDeal {long ticket=100,position_id=99;string symbol="SYNTH.EXACT";int side=1;};
struct JPWObserverSnapshot {};
bool JPWObserverCollectPositionDeals(long,std::vector<JPWObserverDeal>&deals,string&reason){
 if(history_failures-->0){reason="synthetic history not ready";return false;}deals.resize(1);return true;}
void JPWObserverSortDeals(std::vector<JPWObserverDeal>&,int,int){}
bool JPWObserverFindEpisode(std::vector<JPWObserverDeal>&d,long,JPWObserverDeal&out,string&){out=d[0];return true;}
bool JPWObserverEpisodeKey(const string&,const string&,long,long,string&key){key="synthetic episode";return true;}
bool JPWObserverStoreStart(JPWObserverDeal&,const string&,long,ulong,bool,string&reason){
 store_calls++;if(store_failures-->0){reason="synthetic ATR temporarily unavailable";return false;}return true;}
int timer_kills=0,lease_releases=0,presence_releases=0,database_closes=0;
void FileClose(int){}
void EventKillTimer(){timer_kills++;}void JPWStopRiskReleaseSessionLease(){lease_releases++;}
void JPWStopRiskPresenceRelease(){presence_releases++;}
bool deactivate_ok=true;
bool JPWStopRiskDeactivate(const string&,const string&,string&){return deactivate_ok;}
void DatabaseClose(int){database_closes++;}
'''

BOUNDARY = r'''
struct Recorded {string context;int component,code;long sample,utc,mono;};
std::vector<Recorded> recorded;JPWStoreResult write_status=JPW_STORE_VALID;
JPWStoreResult JPWDiagRecordAt(const string&context,int component,int code,long sample,long utc,long mono,string&reason){
 if(write_status!=JPW_STORE_VALID){reason="synthetic writer unavailable";return write_status;}
 recorded.push_back({context,component,code,sample,utc,mono});return JPW_STORE_VALID;}
JPWStoreResult existing_status=JPW_STORE_ABSENT;
JPWStoreResult JPWObserverReadByKeyStatus(int,const string&,JPWObserverSnapshot&,string&){return existing_status;}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const char*why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}}
bool recorded_code(int code){return std::any_of(recorded.begin(),recorded.end(),[&](const Recorded&r){return r.code==code;});}
int main(){
 g_account_key=string(64,'a');g_risk_account_key=g_account_key;g_risk_publisher_token="synthetic";g_db=2;
 JPWObserverDiagnostic(JPW_DIAG_SESSION_START,5);now_ms=1100;now_utc=1001;
 g_account_key=string(64,'b');JPWObserverFlushDiagnostics();
 check(recorded.size()==1&&recorded[0].context==string(64,'a')&&recorded[0].sample==5&&recorded[0].mono==1000&&recorded[0].utc==1000,
       "EA diagnostic keeps event account/time/sample while write is deferred");
 long other_indicator=0;string marker_reason,other_key,own_key;
 check(JPWDiagMarkFailure(g_account_key,JPW_DIAG_INDICATOR,other_indicator,marker_reason)&&
       JPWDiagFailureKey(g_account_key,JPW_DIAG_INDICATOR,other_indicator,other_key,marker_reason),
       "another indicator on the same chart owns its independent marker");
 recorded.clear();JPWObserverDiagnostic(JPW_DIAG_QUALITY_CHANGED,9);
 JPWObserverDiagnostic(JPW_DIAG_DATA_UNAVAILABLE,9);write_status=JPW_STORE_BUSY;
 JPWObserverFlushDiagnostics();
 JPWDiagFailureKey(g_account_key,JPW_DIAG_OBSERVER,g_observer_diagnostic_instance,own_key,marker_reason);
 write_status=JPW_STORE_VALID;JPWObserverFlushDiagnostics(1);
 check(GlobalVariableCheck(own_key)&&GlobalVariableCheck(other_key)&&!g_diagnostic_pending.empty(),
       "one recovered EA write cannot clear its pending-context failure or another indicator marker");
 JPWObserverFlushDiagnostics(64);
 check(!GlobalVariableCheck(own_key)&&GlobalVariableCheck(other_key),
       "draining EA context clears only its own instance marker");
 JPWDiagClearFailure(g_account_key,JPW_DIAG_INDICATOR,other_indicator,marker_reason);
 recorded.clear();g_diagnostic_pending.clear();
 JPWObserverScheduleReconstruction();store_failures=1;
 JPWObserverReconstructOpen();
 check(store_calls==1&&g_reconstruct_cursor==0&&g_reconstruct_open_positions,
       "transient ATR/store failure preserves reconstruction cursor");
 now_ms+=999;JPWObserverReconstructOpen();
 check(store_calls==1,"reconstruction retry waits at least one second");
 now_ms+=1;JPWObserverReconstructOpen();
 check(store_calls==2&&g_reconstruct_cursor==1,"same open position succeeds after transient failure");
 JPWObserverReconstructOpen();
 check(!g_reconstruct_open_positions,"successful pass eventually completes");
 positions=2;store_calls=0;store_failures=1000;JPWObserverScheduleReconstruction();
 for(int i=0;i<60;i++){now_ms+=1000;JPWObserverReconstructOpen();}
 check(store_calls==60&&g_reconstruct_cursor==1,"bounded retry exhaustion advances to next open position");
 JPWObserverFlushDiagnostics(64);
 check(recorded_code(JPW_DIAG_RETRY_EXHAUSTED),"exhausted reconstruction produces explicit durable gap event");
 store_failures=0;now_ms+=1000;JPWObserverReconstructOpen();
 check(g_reconstruct_cursor==2,"one failed position does not starve remaining positions");
 JPWObserverReconstructOpen();
 check(g_reconstruct_open_positions&&g_reconstruct_cursor==0&&g_reconstruct_next_ms==now_ms+30000,
       "pass with exhausted position schedules another recovery attempt after thirty seconds");
 int before_retry=store_calls;now_ms+=29999;JPWObserverReconstructOpen();
 check(store_calls==before_retry,"recovery pass honors the thirty-second delay");
 now_ms+=1;JPWObserverReconstructOpen();
 check(store_calls==before_retry+1&&g_reconstruct_cursor==1,"deferred recovery pass resumes");
 recorded.clear();g_diagnostic_pending.clear();g_pending.resize(1);
 JPWObserverDiagnostic(JPW_DIAG_QUALITY_CHANGED);JPWObserverDiagnostic(JPW_DIAG_BUDGET_DEFERRED);
 OnDeinit(0);
 check(recorded_code(JPW_DIAG_SESSION_END)&&recorded_code(JPW_DIAG_RETRY_EXHAUSTED),
       "shutdown persists lifecycle and outstanding-work gap despite earlier diagnostics");
 check(recorded.size()<=3&&timer_kills==1&&lease_releases==1&&presence_releases==1&&database_closes==1,
       "shutdown essential writes bounded and resources released");
 recorded.clear();g_pending.resize(1);write_status=JPW_STORE_BUSY;g_db=3;OnDeinit(0);
 check(failure_markers()>0,"shutdown persistence refusal retains an explicit failure marker");
 std::cout<<"HOST_SCHEDULER_REPLAY: "<<checks-failures<<" PASS / "<<failures<<" FAIL\n";
 return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("JPW_TEST_RESULT: ENVIRONMENT_ERROR")
        return 2
    source = RUNTIME.read_text()
    wrapper = EA.read_text()
    core = "\n".join((INCLUDE / f"JPW_Alavancagem_{name}.mqh").read_text()
                     for name in ("Store_Result", "Diagnostics_Core"))
    core = re.sub(r"^#include[^\n]*", "", core, flags=re.MULTILINE)
    diagnostic_source=(INCLUDE / "JPW_Alavancagem_Diagnostics.mqh").read_text()
    marker_helpers=diagnostic_source[diagnostic_source.index("#define JPW_DIAG_INSTANCE_SEQUENCE"):diagnostic_source.index("struct JPWDiagEvent")]
    print("MARKER_HELPER_SOURCE_SHA256:",hashlib.sha256(marker_helpers.encode()).hexdigest())
    core += "\n" + marker_helpers
    state = source[source.index("#define JPW_OBSERVER_QUEUE_MAX"):source.index("// This buffer contains")]
    state = re.sub(r"(JPWObserver\w+) (g_\w+)\[\];", r"std::vector<\1> \2;", state)
    names = [name for name in re.findall(r"^(?:void|bool|int|ulong) (JPWObserver\w+)\(", source, re.MULTILINE)
             if name.startswith(("JPWObserverDiagnostic", "JPWObserverTerminalDiagnostic", "JPWObserverFlushDiagnostics", "JPWObserverScheduleReconstruction", "JPWObserverReconstruct"))]
    bodies = "\n".join(function(source, name) for name in names) + function(source, "JPWObserverRuntimeDetach") + function(wrapper, "OnDeinit")
    bodies = bodies.replace("JPWObserverDeal deals[],start;", "std::vector<JPWObserverDeal> deals;JPWObserverDeal start;")
    # The shutdown fixture models an attached runtime for each distinct session.
    # Financial and scheduler assertions remain unchanged after lifecycle extraction.
    main_fixture = MAIN.replace("int main(){", "int main(){ g_observer_runtime_attached=true;")
    main_fixture = main_fixture.replace("g_db=3;OnDeinit(0);", "g_db=3;g_observer_runtime_attached=true;OnDeinit(0);")
    cpp = SHIM + core + BOUNDARY + state + bodies + main_fixture
    print("EA_SOURCE_SHA256:", hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-scheduler-") as temporary:
        path,binary=Path(temporary)/"scheduler.cpp",Path(temporary)/"scheduler"
        path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    print("NATIVE_MT5_TIMERS: NOT_RUN")
    status=indicator_replay(compiler,core)
    if status:return status
    status=marker_replay(compiler,core)
    if status:return status
    status=presence_recovery_replay(compiler,source)
    return status or presence_helper_replay(compiler)


INDICATOR_BOUNDARY = r'''
ulong g_cycle_started_ms=1000;long g_collection_sequence=1;
string g_diagnostic_context,g_last_diagnostic_context,g_diagnostic_reason;
struct JPWAccount{};
JPWAccount g_account,g_genesis_refresh_account;
bool g_genesis_due=true,g_raiz_due=true,g_account_known=true,g_genesis_refresh_connected=true,
     g_genesis_refresh_clock_valid=true,g_refresh_requested=false,g_stop_ready=false,g_raiz_details_open=false;
JPWObserverPresenceState g_stop_observer_presence=JPW_OBSERVER_NOT_CONFIRMED;
long g_genesis_refresh_now_ms=1000;ulong g_genesis_refresh_started=1000;
int g_raiz_tab=0;constexpr int JPW_ROUTE_OVERVIEW=7,JPW_ROUTE_STOPS=8,JPW_ROUTE_STOP_ROW=12,JPW_VIEW_CURRENT=1;
string g_panel_value,g_panel_status,g_leverage_reason;
int genesis_calls=0,raiz_calls=0,stop_calls=0,record_calls=0,draws=0;
ulong genesis_duration=0;
std::vector<int> accepted_metrics;
void JPWCollectGenesis(JPWAccount&,bool,bool,long,ulong){genesis_calls++;now_ms+=genesis_duration;}
void JPWCollectRaizN(){raiz_calls++;}
bool JPWReadAccount(JPWAccount&){return true;}
bool JPWAccountsEqual(JPWAccount&,JPWAccount&){return true;}
void JPWInvalidateIdentityPresentation(){}
void JPWAcceptMetric(int metric){accepted_metrics.push_back(metric);}
void JPWCollectStopRisk(){stop_calls++;}
// New read-model collection is a separate component boundary in this legacy
// scheduler replay. Its real implementation and metric-6 acceptance run in
// jpw_genetrix_ui_test; original collector/order/budget assertions stay intact.
void JPWGenetrixCollectLedger(){}
void JPWStopRiskUnavailable(const string&){}
void JPWDetailsReadStopRisk(){}
void JPWStopRiskRefreshRowView(){}
void JPWRaizSaveVisibleFields(){}
void JPWRaizPanelDestroy(){}
double g_numeric_values[7]={},g_stop_total_money=0;
bool g_numeric_valid[7]={};long g_source_times[7]={};int g_stop_quality=0,g_compensated_quality=0;
struct StopSample{long observed_utc=0,observed_mono_ms=0;}g_stop_sample;
struct LedgerSample{long observed_mono_ms=0;}g_genetrix_view;
bool g_genetrix_ledger_available=false;
JPWMetricSample g_metric_samples[7];string g_sample_context;
// Existing scheduler replay treats the new inventory module as an explicit
// component boundary. jpw_positions_core_test executes its real implementation.
string g_position_math_reason;
int positions_catalogue_requests=0,position_publications=0,position_monitors=0;
std::vector<int> position_publish_order;
void JPWPositionsCollectCatalogOnly(){
 if(now_ms>=g_cycle_started_ms&&now_ms-g_cycle_started_ms<500)positions_catalogue_requests++;}
void JPWPositionsMonitorInventory(){position_monitors++;}
bool JPWPositionsPublish(JPWMetricSample&,const string&){
 position_publications++;position_publish_order=accepted_metrics;return true;}
int g_metric_last_quality[7]={};
int g_leverage_quality=1,g_floating_quality=1,g_genesis_quality=1,g_raiz_quality=1,g_scale2_quality=1;
constexpr int JPW_VIEW_NA=0,JPW_VIEW_ESTIMATED=2;
void JPWRefreshRequestedRecords(){record_calls++;}
bool JPWConfirmAcceptedContext(){return true;}
void JPWRenderCurrentDisplay(){draws++;}
'''
INDICATOR_MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const char*why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}}
int main(){
 g_diagnostic_context=string(64,'a');g_last_diagnostic_context=g_diagnostic_context;
 long other_writer=0;string other_key,marker_reason;
 JPWDiagMarkFailure(g_diagnostic_context,JPW_DIAG_OBSERVER,other_writer,marker_reason);
 JPWDiagFailureKey(g_diagnostic_context,JPW_DIAG_OBSERVER,other_writer,other_key,marker_reason);
 JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
 now_ms=1100;now_utc=1001;g_collection_sequence=9;
 g_diagnostic_context=string(64,'b');write_status=JPW_STORE_BUSY;JPWFlushDiagnostics();
 check(recorded.empty()&&g_diagnostic_pending.size()==3&&g_diagnostic_pending[0].context==string(64,'a')&&failure_markers()>0,
       "indicator BUSY preserves FIFO and original context before account switch");
 write_status=JPW_STORE_VALID;JPWFlushDiagnostics();
 check(recorded.size()==2&&recorded[0].context==string(64,'a')&&recorded[0].utc==1000&&
       recorded[0].mono==1000&&recorded[0].sample==1&&recorded[1].code==JPW_DIAG_CONTEXT_CHANGED,
       "indicator persisted event identity describes occurrence rather than flush time");
 JPWFlushDiagnostics();
 check(recorded.size()==3&&recorded.back().code==JPW_DIAG_WRITE_FAILED&&recorded.back().context==string(64,'a')&&
       failure_markers()==1&&GlobalVariableCheck(other_key),
       "indicator recovery persists its gap and clears only its marker, preserving EA failure");
 JPWDiagClearFailure(string(64,'a'),JPW_DIAG_OBSERVER,other_writer,marker_reason);
 recorded.clear();g_diagnostic_pending.clear();
 for(int i=0;i<65;i++){g_diagnostic_context=std::to_string(i);JPWQueueDiagnostic(JPW_DIAG_QUALITY_CHANGED);}
 check(g_diagnostic_pending.size()==64&&g_diagnostic_queue_lost&&g_diagnostic_overflow.context=="64",
       "bounded diagnostic queue retains explicit overflow origin");
 g_last_diagnostic_context=g_diagnostic_context;
 for(int i=0;i<34;i++)JPWFlushDiagnostics();
 check(!g_diagnostic_queue_lost&&std::any_of(recorded.begin(),recorded.end(),[](const Recorded&r){
  return r.code==JPW_DIAG_QUEUE_OVERFLOW&&r.context=="64";}),"recovered writer persists overflow rather than silently dropping it");
 now_ms=1500;g_cycle_started_ms=1000;JPWAcceptCollection("2.50x","accepted");
 check(genesis_calls==0&&raiz_calls==0&&stop_calls==0&&g_genesis_due&&g_raiz_due&&g_refresh_requested,
       "global 500ms exhaustion starts no optional collector and preserves deferred requests");
 check(accepted_metrics==std::vector<int>({0,1}),"deferred metrics do not receive invented collection identities");
 check(position_publications==1&&position_publish_order==std::vector<int>({0})&&positions_catalogue_requests==0,
       "position publication occurs after metric zero acceptance without opening a collector after budget exhaustion");
 accepted_metrics.clear();g_refresh_requested=false;now_ms=2000;g_cycle_started_ms=2000;genesis_duration=500;
 JPWAcceptCollection("2.50x","accepted");
 check(genesis_calls==1&&raiz_calls==0&&stop_calls==0&&!g_genesis_due&&g_raiz_due,
       "a collector using the remaining budget prevents the next collector from opening a fresh window");
 check(accepted_metrics==std::vector<int>({0,1,2}),"only actually collected independent metrics are accepted");
 now_ms=3000;g_cycle_started_ms=3000;genesis_duration=0;accepted_metrics.clear();
 JPWAcceptCollection("2.50x","accepted");
 check(raiz_calls==1&&stop_calls==1&&!g_raiz_due&&accepted_metrics==std::vector<int>({0,1,3,4,5}),
       "next cycle resumes deferred Raiz and independent stop monitor");
 now_ms=2999;check(!JPWCoordinatorBudgetRemaining(),"clock rollback fails global budget closed");
 g_diagnostic_pending.clear();g_diagnostic_context=string(64,'c');g_sample_context=g_diagnostic_context;
 g_collection_sequence=100;g_numeric_values[0]=2.5;g_numeric_valid[0]=true;
 JPWAcceptMetricProduction(0);
 check(g_metric_samples[0].id==101&&g_diagnostic_pending.size()==1&&g_diagnostic_pending[0].sample_id==101,
       "quality-change evidence references its newly accepted sample rather than previous sequence");
 std::cout<<"HOST_INDICATOR_COORDINATOR: "<<checks-failures<<" PASS / "<<failures<<" FAIL\n";
 return failures?1:0;
}
'''


def indicator_replay(compiler: str, core: str) -> int:
    path=INCLUDE / "JPW_Alavancagem_Coordinator.mqh"
    source=path.read_text()
    indicator=(MQL / "Indicators/JPWealth/JPW_Alavancagem_Atual.mq5").read_text()
    state=indicator[indicator.index("struct JPWIndicatorDiagnosticPending"):indicator.index("JPWDiagTiming g_indicator_timing")]
    state=state.replace("JPWIndicatorDiagnosticPending g_diagnostic_pending[];", "std::vector<JPWIndicatorDiagnosticPending> g_diagnostic_pending;")
    state += re.search(r"^long g_indicator_diagnostic_instance=0;",source,re.MULTILINE).group()
    names=("JPWCoordinatorBudgetRemaining","JPWEnqueueDiagnostic","JPWQueueDiagnostic","JPWIndicatorDiagnosticFailureMarker","JPWFlushDiagnostics","JPWMonitorStopRisk","JPWAcceptCollection")
    samples=(INCLUDE / "JPW_Alavancagem_Samples.mqh").read_text()
    accept=function(source,"JPWAcceptMetric").replace("void JPWAcceptMetric(","void JPWAcceptMetricProduction(",1)
    cpp=SHIM+core+samples+BOUNDARY+state+INDICATOR_BOUNDARY+"\n".join(function(source,n) for n in names)+accept+INDICATOR_MAIN
    print("COORDINATOR_SOURCE_SHA256:",hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-indicator-scheduler-") as temporary:
        path,binary=Path(temporary)/"scheduler.cpp",Path(temporary)/"scheduler"
        path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


MARKER_MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const char*why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}}
int main(){
 string context(64,'a'),reason,key_a,key_b,key_ea;
 long indicator_a=0,indicator_b=0,observer=0;
 check(JPWDiagMarkFailure(context,JPW_DIAG_INDICATOR,indicator_a,reason)&&
       JPWDiagMarkFailure(context,JPW_DIAG_INDICATOR,indicator_b,reason)&&
       JPWDiagMarkFailure(context,JPW_DIAG_OBSERVER,observer,reason),
       "two indicators and an EA on ChartID42 can record separate failures");
 JPWDiagFailureKey(context,JPW_DIAG_INDICATOR,indicator_a,key_a,reason);
 JPWDiagFailureKey(context,JPW_DIAG_INDICATOR,indicator_b,key_b,reason);
 JPWDiagFailureKey(context,JPW_DIAG_OBSERVER,observer,key_ea,reason);
 check(indicator_a!=indicator_b&&indicator_a!=observer&&indicator_b!=observer&&
       key_a!=key_b&&key_a!=key_ea&&key_b!=key_ea&&key_a.size()<=63&&key_b.size()<=63&&key_ea.size()<=63,
       "private ordinals and component produce distinct valid terminal variable names");
 check(JPWDiagClearFailure(context,JPW_DIAG_INDICATOR,indicator_a,reason)&&
       !GlobalVariableCheck(key_a)&&GlobalVariableCheck(key_b)&&GlobalVariableCheck(key_ea),
       "one successful indicator cannot erase the other indicator or EA failure");
 check(JPWDiagClearFailure(context,JPW_DIAG_OBSERVER,observer,reason)&&GlobalVariableCheck(key_b),
       "successful EA cannot erase remaining indicator failure");
 const double sequence=GlobalVariableGet(JPW_DIAG_INSTANCE_SEQUENCE);const int before_cas=cas_calls;
 check(JPWDiagClearFailure(context,JPW_DIAG_INDICATOR,0,reason)&&cas_calls==before_cas&&
       GlobalVariableGet(JPW_DIAG_INSTANCE_SEQUENCE)==sequence,"clear without an identity never allocates or resets the counter");
 GlobalVariableTemp(JPW_DIAG_INSTANCE_SEQUENCE);
 check(GlobalVariableGet(JPW_DIAG_INSTANCE_SEQUENCE)==sequence,"temporary-variable shim preserves existing counter exactly");
 globals.clear();cas_calls=0;cas_races=1;long contended=0;string contended_key;
 check(JPWDiagFailureKey(context,JPW_DIAG_INDICATOR,contended,contended_key,reason)&&contended==2&&cas_calls==2,
       "CAS conflict reloads the other writer's advancement and reserves a different ordinal");
 globals.clear();cas_calls=0;cas_refusals=7;long last_attempt=0;string last_key;
 check(JPWDiagFailureKey(context,JPW_DIAG_INDICATOR,last_attempt,last_key,reason)&&cas_calls==8&&last_attempt==1,
       "allocation succeeds on its eighth and final bounded attempt");
 globals.clear();cas_calls=0;cas_refusals=8;long refused=0;
 check(!JPWDiagMarkFailure(context,JPW_DIAG_INDICATOR,refused,reason)&&refused==0&&cas_calls==8&&
       !reason.empty()&&failure_markers()==1,"eight CAS refusals leave explicit sticky allocation failure without ChartID fallback");
 long recovered=0;check(JPWDiagMarkFailure(context,JPW_DIAG_INDICATOR,recovered,reason)&&
       JPWDiagClearFailure(context,JPW_DIAG_INDICATOR,recovered,reason)&&failure_markers()==1,
       "later writer success cannot erase the earlier allocation-failure notice");
 globals.clear();globals[JPW_DIAG_INSTANCE_SEQUENCE]=9007199254740991.0;cas_calls=0;long exhausted=0;
 check(!JPWDiagMarkFailure(context,JPW_DIAG_OBSERVER,exhausted,reason)&&exhausted==0&&cas_calls==0&&failure_markers()==1,
       "counter exhaustion refuses identity wrap and preserves a visible allocation failure");
 globals.clear();globals[JPW_DIAG_INSTANCE_SEQUENCE]=1.5;long fractional=0;
 check(!JPWDiagMarkFailure(context,JPW_DIAG_OBSERVER,fractional,reason)&&fractional==0&&failure_markers()==1,
       "malformed fractional counter is refused rather than normalized");
 std::cout<<"HOST_MARKER_ISOLATION: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native CAS scheduling NOT_RUN\n";
 return failures?1:0;
}
'''


def marker_replay(compiler: str, core: str) -> int:
    with tempfile.TemporaryDirectory(prefix="jpw-marker-isolation-") as temporary:
        path,binary=Path(temporary)/"marker.cpp",Path(temporary)/"marker"
        path.write_text(SHIM+core+MARKER_MAIN)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


PRESENCE_RECOVERY_SHIM = r'''
#include <iostream>
#include <string>
using string=std::string;
enum JPWObserverPresenceState {JPW_OBSERVER_WAITING=1};
string g_risk_account_key="synthetic account",g_risk_publisher_token="synthetic publisher";
bool g_risk_presence_owned=false,g_risk_presence_error_reported=false;
double g_risk_presence_value=0.0,marker_value=0.0;
JPWObserverPresenceState g_risk_presence_state=JPW_OBSERVER_WAITING;
bool marker_exists=false,beat_fails=false;
int starts=0,beats=0;
string JPWObserverPresenceName(const string&,const string&){return "synthetic marker";}
bool GlobalVariableCheck(const string&){return marker_exists;}
bool JPWObserverPresenceStartOwned(const string&,const string&,double&owned_value){
 if(marker_exists)return false;marker_exists=true;starts++;owned_value=marker_value=1.0;return true;
}
bool JPWObserverPresenceBeatOwned(const string&,const string&,JPWObserverPresenceState,double&owned_value){
 if(!marker_exists||beat_fails||marker_value!=owned_value)return false;
 beats++;owned_value=marker_value+1.0;marker_value=owned_value;return true;
}
bool JPWObserverPresenceMarkerMatches(const string&,const string&,double owned_value){
 return marker_exists&&marker_value==owned_value;
}
void Print(const char*){}
'''

PRESENCE_RECOVERY_MAIN = r'''
int main(){
 JPWStopRiskPresenceRefresh();
 if(!g_risk_presence_owned||starts!=1||beats!=1)return 1;
 beat_fails=true;JPWStopRiskPresenceRefresh();
 if(!g_risk_presence_owned||starts!=1||!marker_exists)return 2;
 beat_fails=false;JPWStopRiskPresenceRefresh();
 if(!g_risk_presence_owned||starts!=1||beats!=2)return 3;
 marker_exists=false;JPWStopRiskPresenceRefresh();
 if(g_risk_presence_owned||starts!=1)return 4;
 JPWStopRiskPresenceRefresh();
 if(!g_risk_presence_owned||starts!=2||beats!=3)return 5;
 marker_value=777.0;JPWStopRiskPresenceRefresh();
 if(g_risk_presence_owned||g_risk_presence_value!=0.0||marker_value!=777.0)return 6;
 JPWStopRiskPresenceRefresh();
 if(g_risk_presence_owned||starts!=2||marker_value!=777.0)return 7;
 marker_exists=false;JPWStopRiskPresenceRefresh();
 if(!g_risk_presence_owned||starts!=3||beats!=4)return 8;
 std::cout<<"HOST_OBSERVER_PRESENCE_RECOVERY: transient CAS retry, deleted-marker recreation and changed-owner refusal PASS; MT5 NOT_RUN\n";
 return 0;
}
'''


def presence_recovery_replay(compiler: str, source: str) -> int:
    body=function(source,"JPWStopRiskPresenceRefresh")
    with tempfile.TemporaryDirectory(prefix="jpw-presence-recovery-") as temporary:
        path,binary=Path(temporary)/"presence.cpp",Path(temporary)/"presence"
        path.write_text(PRESENCE_RECOVERY_SHIM+body+PRESENCE_RECOVERY_MAIN)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


PRESENCE_HELPER_SHIM = r'''
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
using string=std::string;
#define ulong std::uint64_t
enum JPWObserverPresenceState {JPW_OBSERVER_WAITING=1,JPW_OBSERVER_PUBLISHED=2,
                               JPW_OBSERVER_FAILED=3};
std::map<string,double> variables;
bool refuse_cas_once=false,mutate_before_cas_once=false;
ulong now_ms=1000;
string JPWObserverPresenceName(const string&,const string&){return "synthetic owned marker";}
ulong GetTickCount64(){return now_ms;}
bool MathIsValidNumber(double x){return std::isfinite(x);}
bool JPWObserverPresenceEncode(ulong ms,JPWObserverPresenceState state,double&out){
 if(ms==0)return false;out=(double)(ms*8+(int)state);return true;
}
bool GlobalVariableCheck(const string&n){return variables.count(n)!=0;}
bool GlobalVariableTemp(const string&n){
 if(GlobalVariableCheck(n))return false;variables[n]=0.0;return true;
}
bool GlobalVariableGet(const string&n,double&out){
 auto it=variables.find(n);if(it==variables.end())return false;out=it->second;return true;
}
bool GlobalVariableSetOnCondition(const string&n,double next,double expected){
 auto it=variables.find(n);if(it==variables.end()||it->second!=expected)return false;
 if(mutate_before_cas_once){mutate_before_cas_once=false;it->second=777.0;return false;}
 if(refuse_cas_once){refuse_cas_once=false;return false;}
 it->second=next;return true;
}
bool GlobalVariableDel(const string&n){return variables.erase(n)>0;}
'''

PRESENCE_HELPER_MAIN = r'''
int main(){
 const string account="synthetic account",publisher="synthetic publisher";
 const string name=JPWObserverPresenceName(account,publisher);
 double owned=0.0;
 if(!JPWObserverPresenceStartOwned(account,publisher,owned)||
    !JPWObserverPresenceMarkerMatches(account,publisher,owned))return 1;
 now_ms=1001;refuse_cas_once=true;
 if(JPWObserverPresenceBeatOwned(account,publisher,JPW_OBSERVER_PUBLISHED,owned)||
    !JPWObserverPresenceMarkerMatches(account,publisher,owned))return 2;
 if(!JPWObserverPresenceBeatOwned(account,publisher,JPW_OBSERVER_PUBLISHED,owned)||
    !JPWObserverPresenceMarkerMatches(account,publisher,owned))return 3;
 mutate_before_cas_once=true;
 if(JPWObserverPresenceBeatOwned(account,publisher,JPW_OBSERVER_FAILED,owned)||
    JPWObserverPresenceMarkerMatches(account,publisher,owned)||variables[name]!=777.0)return 4;
 JPWObserverPresenceReleaseOwned(account,publisher,owned);
 if(variables[name]!=777.0)return 5;
 variables.erase(name);owned=0.0;now_ms=1002;
 if(!JPWObserverPresenceStartOwned(account,publisher,owned))return 6;
 JPWObserverPresenceReleaseOwned(account,publisher,owned);
 if(!GlobalVariableCheck(name)||variables[name]!=0.0)return 7;
 if(!JPWObserverPresenceStartOwned(account,publisher,owned))return 8;
 JPWObserverPresenceReleaseOwned(account,publisher,owned);
 variables.erase(name);owned=0.0;refuse_cas_once=true;
 if(JPWObserverPresenceStartOwned(account,publisher,owned)||variables[name]!=0.0)return 9;
 if(!JPWObserverPresenceStartOwned(account,publisher,owned))return 10;
 JPWObserverPresenceReleaseOwned(account,publisher,owned);
 std::cout<<"HOST_OBSERVER_OWNED_MARKER: exact-value CAS retry, changed-writer refusal, atomic invalidation and zero-tombstone restart PASS; MT5 NOT_RUN\n";
 return 0;
}
'''


def presence_helper_replay(compiler: str) -> int:
    source=(INCLUDE/"JPW_Alavancagem_Observer_Presence.mqh").read_text()
    names=("JPWObserverPresenceBeatOwned","JPWObserverPresenceMarkerMatches",
           "JPWObserverPresenceStartOwned","JPWObserverPresenceReleaseOwned")
    cpp=PRESENCE_HELPER_SHIM+"\n".join(function(source,name) for name in names)+PRESENCE_HELPER_MAIN
    print("PRESENCE_HELPER_SOURCE_SHA256:",hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-owned-presence-") as temporary:
        path,binary=Path(temporary)/"presence.cpp",Path(temporary)/"presence"
        path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Execute the actual Monitor callbacks, scheduler and status codec on the host.

Only unavailable terminal APIs and the Observer/Accountant runtime boundaries
are seams. Their financial preparation/persistence is outside this log test.
The status codec reads/writes a real isolated filesystem. No MQL/MT5 claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import core_monitor_judge as host

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
MONITOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5"
LOG = INC / "JPW_Stoikus_Monitor_Log.mqh"

# Breaks caught: false active claim after rejected admission; repeat logging on
# identical retries; hidden new reason/context; missing single recovery; lost
# lease still claimed active; timer failure leaks resources; log reporting
# promotes old/N/A financial captures or changes coverage declarations.
SEAMS = r'''
constexpr int INIT_SUCCEEDED=0, INIT_FAILED=-1, REASON_INITFAILED=8, REASON_ACCOUNT=6;
constexpr int JPW_OBSERVER_FAILED=2, JPW_PERSONAL_CURRENT=2, JPW_PERSONAL_ESTIMATED=1;
constexpr int JPW_DIAG_BUDGET_DEFERRED=19;
const string JPW_PRODUCT_VERSION="1.22.1", JPW_BUILD_ID=string(64,'c');
struct MqlTradeTransaction{}; struct MqlTradeRequest{}; struct MqlTradeResult{};
bool host_timer_ok=true,host_timer_running=false,host_writer_ok=true;
bool host_temp_ok=true,host_cas_ok=true,host_status_ok=true,host_hash_ok=true;
bool host_observer_ok=true,host_observer_conflict=false,host_risk_current=false;
string host_identity=string(64,'a'),host_observer_reason="";
std::vector<string> host_logs;
std::vector<string> host_identity_reads;
int host_identity_cursor=0,host_timer_interval=0,host_observer_transactions=0;
int host_accountant_transactions=0,host_jobs=0,host_claims=0;
int host_last_error=0,host_writer_error=5004;
ulong host_micro=100;
template<class... T>void Print(const T&... parts){std::ostringstream out;((out<<parts),...);host_logs.push_back(out.str());}
long TimeGMT(){return 9999;} long ChartID(){return 17;}
ulong GetMicrosecondCount(){return ++host_micro;}
int GetLastError(){return host_last_error;}
void ResetLastError(){host_last_error=0;}
bool EventSetTimer(int seconds){host_timer_interval=seconds;host_timer_running=host_timer_ok;host_last_error=(host_timer_ok ? 99999 : 501);return host_timer_ok;}
void EventKillTimer(){host_timer_running=false;}
bool GlobalVariableCheck(const string& name){return host_leases.count(name)!=0;}
bool GlobalVariableTemp(const string& name){if(!host_temp_ok)return false;host_leases.emplace(name,0.0);return true;}
bool GlobalVariableSetOnCondition(const string& name,double value,double previous){
 auto p=host_leases.find(name);if(!host_cas_ok||p==host_leases.end()||p->second!=previous)return false;p->second=value;return true;
}
int FileOpen(const string& name,int flags){
 if(name.find("writer_")!=string::npos){host_claims++;if(!host_writer_ok){if(host_writer_error>=0)host_last_error=host_writer_error;return INVALID_HANDLE;}}
 if(!host_status_ok&&name.find(".tmp")!=string::npos)return INVALID_HANDLE;
 return host_base_FileOpen(name,flags);
}
bool JPWRaizNHash(const string& value,string& out){
 if(!host_hash_ok&&value.find("|monitor_session_v1|")!=string::npos)return false;
 return host_base_Hash(value,out);
}
template<class T>int ArraySize(const std::vector<T>& values){return (int)values.size();}
bool g_observer_runtime_attached=false,g_observer_runtime_conflict=false;
string g_observer_runtime_reason="",g_observer_risk_reason="",g_ph_last_problem="";
int g_risk_presence_state=0,g_observer_personal_quality=0;
bool g_ph_memory_state=false,g_ph_gap=false,g_ph_incomplete=false,g_ph_owner_conflict=false;
bool g_reconstruct_open_positions=false,g_observer_coverage_incomplete=false;
std::vector<int> g_pending;
int g_db=7,g_reconstruct_count=0,g_reconstruct_cursor=0;
long g_observer_risk_observed_utc=101,g_observer_risk_observed_mono=102;
long g_observer_personal_observed_utc=201,g_observer_personal_observed_mono=202;
long g_observer_raiz_observed_utc=401,g_observer_raiz_observed_mono=402;
int host_ledger_state=1;string host_ledger_reason="Preparação sintética";
bool host_history_declaration=false,host_cost_declaration=false;
string host_declared_account="",host_coverage_evidence="";
bool JPWObserverReadIdentity(string& key){
 if(host_identity_cursor<(int)host_identity_reads.size())key=host_identity_reads[host_identity_cursor++];
 else key=host_identity;
 return key!="";
}
bool JPWObserverRuntimeAttach(const string&){
 g_observer_runtime_attached=host_observer_ok;g_observer_runtime_conflict=host_observer_conflict;
 g_observer_runtime_reason=host_observer_reason;return host_observer_ok;
}
void JPWObserverRuntimeDetach(int){g_observer_runtime_attached=false;g_observer_runtime_conflict=false;}
bool JPWObserverRuntimeRiskLeaseCurrent(){return host_risk_current;}
void JPWObserverRuntimePrepare(ulong){}
void JPWObserverRuntimeTick(ulong,int){host_jobs++;}
void JPWObserverRuntimeTransaction(const MqlTradeTransaction&,const MqlTradeRequest&,const MqlTradeResult&){host_observer_transactions++;}
void JPWObserverDiagnostic(int){}
void JPWStopRiskPresenceRefresh(){}
void JPWPersonalControllerDeferred(){}
void JPWAccountantAttach(const string&,const string& declaration,bool history,bool costs,const string& evidence){
 host_declared_account=declaration;host_history_declaration=history;host_cost_declaration=costs;host_coverage_evidence=evidence;
}
void JPWAccountantDetach(){}
void JPWAccountantTick(ulong,int){host_jobs++;}
void JPWAccountantTransaction(const MqlTradeTransaction&,const MqlTradeRequest&,const MqlTradeResult&){host_accountant_transactions++;}
int JPWAccountantStatus(){return host_ledger_state;}
bool JPWAccountantCoverageAvailable(){return true;}
bool JPWAccountantCoverageComplete(){return false;}
string JPWAccountantReason(){return host_ledger_reason;}
long JPWAccountantObservedUTC(){return 301;}
long JPWAccountantObservedMono(){return 302;}
int JPWAccountantProgress(){return 40;}
'''

CASES = r'''
bool contains(const string& text,const string& part){return text.find(part)!=string::npos;}
int logs_with(const string& text){int n=0;for(const auto& s:host_logs)if(contains(s,text))n++;return n;}
int active_claims(){return logs_with("produtor ativo")+logs_with("Monitor iniciado");}
bool actionable(){for(const auto& s:host_logs)if(contains(s,"Conta")&&contains(s,"Sistema")&&contains(s,"gráfico de apoio"))return true;return false;}
void timer(){host_now+=1000;OnTimer();}
void assert_capture_invariants(){
 CHECK(g_monitor_snapshot.stop_risk.observed_utc==101&&g_monitor_snapshot.stop_risk.observed_mono_ms==102,"risk capture independent of log/heartbeat");
 CHECK(g_monitor_snapshot.personal.observed_utc==201&&g_monitor_snapshot.personal.observed_mono_ms==202,"personal capture independent of log/heartbeat");
 CHECK(g_monitor_snapshot.ledger.observed_utc==301&&g_monitor_snapshot.ledger.observed_mono_ms==302,"ledger capture independent of log/heartbeat");
 CHECK(g_monitor_snapshot.raiz.observed_utc==401&&g_monitor_snapshot.raiz.observed_mono_ms==402,"Raiz capture independent of log/heartbeat");
 CHECK(g_monitor_snapshot.stop_risk.quality=="Historical"&&g_monitor_snapshot.personal.quality=="N/A"&&g_monitor_snapshot.ledger.quality=="N/A"&&g_monitor_snapshot.raiz.quality=="Historical","active core cannot promote financial quality");
 CHECK(!host_history_declaration&&!host_cost_declaration&&host_coverage_evidence.empty(),"coverage defaults preserved");
}
void run_case(const string& id){
 if(id=="failed-attach-init"){
  host_writer_ok=false;CHECK(OnInit()==INIT_SUCCEEDED,"timer admitted despite writer conflict");
  CHECK(host_timer_running&&host_timer_interval==1&&!g_monitor_owned&&!g_monitor_snapshot.active,"timer available without producer admission");
  CHECK(active_claims()==0,"rejected attach must not claim producer active");
  CHECK(logs_with("aguardando titularidade")==1&&actionable(),"waiting ownership has one actionable state");
 }else if(id=="conflict-ten-retries"){
  host_writer_ok=false;CHECK(OnInit()==INIT_SUCCEEDED,"conflict init admits retries");
  for(int i=0;i<10;i++)timer();
  CHECK(host_claims==11&&!g_monitor_owned,"same one second retry behavior preserved");
  CHECK(logs_with("lock exclusivo")==1,"ten identical rejected retries emit one reason");
  CHECK(active_claims()==0,"conflict retries cannot claim active");
 }else if(id=="changed-reason"){
  host_writer_ok=false;OnInit();timer();const size_t before=host_logs.size();
  host_writer_ok=true;host_temp_ok=false;timer();
  CHECK(host_logs.size()==before+1&&logs_with("Lease temporária")==1,"a changed admission reason remains visible");
  timer();CHECK(logs_with("Lease temporária")==1,"new unchanged reason deduplicated");
 }else if(id=="file-open-cause-uncertain"){
  // A refused open provides an error, never proof of a competing producer.
  host_writer_ok=false;host_writer_error=5004;host_last_error=88888;
  CHECK(OnInit()==INIT_SUCCEEDED&&!g_monitor_owned,"failed file admission still permits one second retry");
  CHECK(logs_with("5004")==1&&logs_with("99999")==0&&logs_with("88888")==0,"open error captured before later API overwrites last error");
  CHECK(logs_with("possíveis")==1&&logs_with("acesso")==1&&logs_with("I/O")==1&&logs_with("outro produtor")==1,"diagnosis presents alternative causes instead of attributing competition");
  CHECK(logs_with("outro núcleo possui")==0&&actionable(),"refused open never categorically diagnoses another producer");
  for(int i=0;i<10;i++)timer();CHECK(logs_with("5004")==1&&host_claims==11,"same file error remains silent while retries continue");
 }else if(id=="file-open-error-change"){
  host_writer_ok=false;host_writer_error=5004;OnInit();timer();const size_t previous=host_logs.size();
  host_writer_error=5001;timer();
  CHECK(!g_monitor_owned&&host_logs.size()==previous+1&&logs_with("5004")==1&&logs_with("5001")==1,"a changed open error emits a new diagnosis");
  CHECK(logs_with("outro núcleo possui")==0&&logs_with("possíveis")==2,"both errors retain uncertainty about cause");
  timer();CHECK(logs_with("5001")==1,"identical changed error is then deduplicated");
 }else if(id=="file-open-no-error-stale"){
  host_writer_ok=false;host_writer_error=-1;host_last_error=88888;
  OnInit();CHECK(!g_monitor_owned&&logs_with("Erro 0")==1&&logs_with("88888")==0&&logs_with("99999")==0,"open failure without new error cannot inherit unrelated last error");
 }else if(id=="recovery-once"){
  host_writer_ok=false;OnInit();timer();host_writer_ok=true;timer();
  CHECK(g_monitor_owned&&g_monitor_snapshot.active,"retry can recover same ownership protocol");
  CHECK(active_claims()==1&&logs_with("recuperado")==1,"producer recovery announced once");
  for(int i=0;i<10;i++)timer();CHECK(active_claims()==1,"healthy cycles stay silent");
  CHECK(actionable(),"recovered state points to account system and support chart");
  assert_capture_invariants();
 }else if(id=="identity-empty"){
  host_identity="";CHECK(OnInit()==INIT_SUCCEEDED,"empty identity admits timer only");
  CHECK(!g_monitor_owned&&active_claims()==0&&logs_with("aguardando identidade")==1,"initial missing identity is explicit");
  for(int i=0;i<10;i++)timer();CHECK(logs_with("aguardando identidade")==1,"missing identity does not flood");
  host_identity=string(64,'b');timer();CHECK(active_claims()==1&&logs_with("recuperado")==1,"identity recovery observed once");
  CHECK(g_monitor_declared_account.empty(),"coverage not rebound after identity becomes available");
 }else if(id=="same-reason-new-context"){
  host_writer_ok=false;OnInit();timer();host_identity=string(64,'b');timer();
  CHECK(logs_with("lock exclusivo")==2,"same reason in another context remains visible");
  CHECK(logs_with("contexto")>=1,"new account/installation context is explained without exposing identity");
  timer();CHECK(logs_with("lock exclusivo")==2,"new context identical retry remains silent");
 }else if(id=="account-change-lease-failure"){
  OnInit();const string previous_lease=JPWMonitorLeaseName(g_monitor_token);
  host_identity=string(64,'b');host_cas_ok=false;timer();
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active&&host_files.empty(),"failed new context lease detaches all monitor resources");
  CHECK(host_leases[previous_lease]==1000,"failed CAS never replaces previous lease ownership");
  CHECK(logs_with("contexto")>=1&&logs_with("lease")>=1,"context change and lease failure remain observable");
  CHECK(active_claims()==1,"failed context cannot inherit active claim");
  CHECK(g_monitor_declared_account==string(64,'a'),"original coverage declaration is not rebound");
  host_cas_ok=true;timer();CHECK(active_claims()==2&&logs_with("recuperado")==1,"new context recovery announced exactly once");
 }else if(id=="foreign-lease"){
  OnInit();const string lease=JPWMonitorLeaseName(g_monitor_token);host_leases[lease]=999;
  timer();CHECK(!g_monitor_owned&&!g_monitor_snapshot.active&&host_leases[lease]==999,"foreign lease preserved and producer suspended");
  CHECK(logs_with("lease perdida")==1,"lost lease explained once");
 }else if(id=="timer-failure"){
  host_timer_ok=false;CHECK(OnInit()==INIT_FAILED,"timer failure rejects init");
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active&&!host_timer_running&&host_files.empty(),"timer failure cleans acquired monitor lock/runtime");
  for(const auto& p:host_leases)CHECK(p.second==0,"timer failure releases own lease by CAS");
  CHECK(active_claims()==0&&logs_with("501")==1&&logs_with("gráfico de apoio")==1,"timer failure actionable without active claim");
 }else if(id=="degraded-reason-recovery"){
  host_observer_conflict=true;host_observer_reason="Observador legado ativo; publicações suspensas";OnInit();
  CHECK(g_monitor_owned&&logs_with("degradado")==1&&active_claims()==0,"admitted monitor with conflicting module is degraded");
  timer();CHECK(logs_with("Observador legado ativo")==1,"same degraded module reason does not flood");
  g_observer_runtime_reason="Lock histórico indisponível";timer();CHECK(logs_with("Lock histórico indisponível")==1,"changed degradation reason visible");
  g_observer_runtime_conflict=false;g_observer_runtime_reason="";timer();
  CHECK(logs_with("recuperado")==1&&active_claims()==1,"module recovery activates core once");
 }else if(id=="observer-attach-rejected"){
  host_observer_ok=false;OnInit();
  CHECK(g_monitor_owned&&logs_with("degradado")==1&&active_claims()==0,"observer rejection leaves independent admitted monitor degraded");
  CHECK(logs_with("Observador não anexado")==1,"degraded state preserves the actual observer admission failure reason");
  for(int i=0;i<10;i++)timer();CHECK(logs_with("Observador não anexado")==1,"observer rejection reason is not repeated");
 }else if(id=="ledger-failure-recovery"){
  host_ledger_state=5;host_ledger_reason="Publicação contábil recusada; base preservada";OnInit();
  CHECK(g_monitor_owned&&logs_with("degradado")==1&&logs_with("Publicação contábil recusada")==1,"independent ledger failure is visible");
  timer();CHECK(logs_with("Publicação contábil recusada")==1,"unchanged ledger failure stays silent");
  host_ledger_reason="Geração contábil alterada";timer();CHECK(logs_with("Geração contábil alterada")==1,"new ledger reason is visible");
  host_ledger_state=1;timer();CHECK(active_claims()==1&&logs_with("recuperado")==1,"ledger can return to preparation without a Current claim");
 }else if(id=="diagnostic-failure-recovery"){
  host_status_ok=false;OnInit();CHECK(g_monitor_owned&&logs_with("degradado")==1,"diagnostic failure visible while own lease remains admitted");
  for(int i=0;i<10;i++)timer();CHECK(logs_with("Escrita do diagnóstico indisponível")==1,"technical publication repeated failure deduplicated");
  host_status_ok=true;timer();CHECK(active_claims()==1&&logs_with("recuperado")==1,"technical diagnostic recovery observed once");
  assert_capture_invariants();
 }else if(id=="heartbeat-failure"){
  OnInit();host_cas_ok=false;timer();
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active,"heartbeat CAS failure stops producer");
  CHECK(logs_with("lease perdida")==1,"heartbeat loss remains visible");
 }else if(id=="promoted-heartbeat-failure"){
  OnInit();g_monitor_status_deferred_cycles=3;host_cas_ok=false;timer();
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active&&host_jobs==0,"promoted heartbeat failure stops producer before domain work");
  CHECK(logs_with("lease perdida")==1,"promoted heartbeat loss remains visible");
 }else if(id=="initial-heartbeat-ten-retries"){
  host_cas_ok=false;OnInit();for(int i=0;i<10;i++)timer();
  CHECK(host_claims==11&&!g_monitor_owned&&!g_monitor_snapshot.active,"heartbeat rejection preserves retry and non-admission");
  CHECK(logs_with("Titularidade da lease não confirmada")==1,"identical initial lease failure does not alternate repeated cleanup/waiting logs");
  CHECK(active_claims()==0,"initial lease rejection cannot claim producer active");
 }else if(id=="shutdown-diagnostic-failure"){
  OnInit();host_status_ok=false;OnDeinit(REASON_ACCOUNT);
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active&&!host_timer_running&&host_files.empty(),"shutdown publication failure cannot prevent cleanup");
  CHECK(contains(host_logs.back(),"encerramento")&&!contains(host_logs.back(),"admitido"),"failed shutdown diagnostic cannot imply admitted core");
 }else if(id=="trade-context-change"){
  OnInit();host_identity=string(64,'b');OnTradeTransaction(MqlTradeTransaction{},MqlTradeRequest{},MqlTradeResult{});
  CHECK(g_monitor_context_dirty&&host_observer_transactions==0&&host_accountant_transactions==0,"trade callback only marks changed context");
  timer();CHECK(g_monitor_owned&&g_monitor_key==string(64,'b')&&active_claims()==2&&logs_with("contexto")>=1,"dirty context revalidated by timer and explained");
 }else if(id=="midcycle-identity-loss"){
  OnInit();host_identity_reads={string(64,'a'),""};host_identity_cursor=0;timer();
  CHECK(!g_monitor_owned&&!g_monitor_snapshot.active,"midcycle identity loss suspends publication");
  CHECK(logs_with("aguardando identidade")==1,"midcycle loss is explicit");
 }else if(id=="status-data-invariant"){
  OnInit();assert_capture_invariants();timer();assert_capture_invariants();
  JPWMonitorSnapshot out;string reason="";
  CHECK(JPWMonitorReadStatus(host_identity,out,reason)&&out.live&&out.active,"real status file remains valid and live");
  CHECK(out.stop_risk.state==JPW_MONITOR_PREPARING&&out.stop_risk.quality=="Historical"&&out.stop_risk.observed_mono_ms==102&&out.personal.quality=="N/A","status reader independently preserves preparation, captures and N/A");
 }else throw std::runtime_error("unknown fixture: "+id);
}
int main(int argc,char** argv){host_root=argv[1];const string id=argv[2];try{
 run_case(id);std::cout<<"CASE|"<<id<<"|PASS|"<<assertions<<'\n';
 for(const auto& line:host_logs)std::cout<<"LOG|"<<line<<'\n';
 return 0;
}catch(const std::exception& e){std::cerr<<"PRODUCT_FAIL|"<<id<<"|"<<e.what()<<'\n';
 for(const auto& line:host_logs)std::cout<<"LOG|"<<line<<'\n';return 1;}}
'''

CASE_IDS = [
    "failed-attach-init", "conflict-ten-retries", "changed-reason",
    "file-open-cause-uncertain", "file-open-error-change", "file-open-no-error-stale",
    "recovery-once", "identity-empty", "same-reason-new-context",
    "account-change-lease-failure", "foreign-lease", "timer-failure",
    "degraded-reason-recovery", "diagnostic-failure-recovery",
    "observer-attach-rejected", "ledger-failure-recovery",
    "heartbeat-failure", "promoted-heartbeat-failure", "trade-context-change", "midcycle-identity-loss",
    "initial-heartbeat-ten-retries", "shutdown-diagnostic-failure",
    "status-data-invariant",
]


def translate(source: str) -> str:
    source = host.translate(source)
    source = re.sub(r'^\s*#property.*$', '', source, flags=re.M)
    source = re.sub(r'^\s*input group.*$', '', source, flags=re.M)
    source = re.sub(r'\binput (?=(?:bool|string)\b)', '', source)
    # MQL string literals concatenate directly; C++ literals need an owner.
    source = re.sub(r'("(?:\\.|[^"\\])*")\s*\+', r'string(\1)+', source)
    return source.replace('JPW_MONITOR_FOLDER+"writer_"', 'string(JPW_MONITOR_FOLDER)+"writer_"')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--keep', type=Path)
    args = parser.parse_args()
    compiler = shutil.which('clang++') or shutil.which('g++')
    files = [MONITOR, INC / 'JPW_Stoikus_Monitor_Core.mqh', INC / 'JPW_Stoikus_Monitor_Status.mqh', Path(host.__file__), Path(__file__)]
    if LOG.exists():
        files.append(LOG)
    receipt = {
        'scope': 'Actual complete Monitor callbacks, admission/lease/heartbeat, scheduler and status codec; terminal APIs and Observer/Accountant boundaries synthetic; real isolated status filesystem',
        'native': 'NOT_RUN', 'platform': platform.platform(), 'compiler': compiler,
        'sources': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'cases': [],
    }
    if not compiler:
        receipt['status'] = 'ENVIRONMENT_ERROR'
    else:
        pre = host.PRE.replace('int FileOpen(', 'int host_base_FileOpen(').replace('bool JPWRaizNHash(', 'bool host_base_Hash(')
        with tempfile.TemporaryDirectory(prefix='stoikus-monitor-state-') as tmp:
            tmp = Path(tmp)
            cpp, binary = tmp / 'monitor.cpp', tmp / 'monitor'
            cpp.write_text('\n'.join([pre, SEAMS, translate(files[1].read_text()), translate(files[2].read_text()), translate(LOG.read_text()) if LOG.exists() else '', translate(MONITOR.read_text()), CASES]))
            build = subprocess.run([compiler, '-std=c++17', '-Wno-deprecated-declarations', str(cpp), '-o', str(binary)] + ([] if sys.platform == 'darwin' else ['-lcrypto']), capture_output=True, text=True)
            receipt['build'] = {'returncode': build.returncode, 'stdout': build.stdout, 'stderr': build.stderr}
            if build.returncode:
                receipt['status'] = 'TEST_HARNESS_FAIL'
            else:
                for case in CASE_IDS:
                    directory = tmp / case
                    directory.mkdir()
                    result = subprocess.run([str(binary), str(directory), case], capture_output=True, text=True)
                    row = {'id': case, 'status': 'PASS' if result.returncode == 0 else 'PRODUCT_FAIL', 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
                    receipt['cases'].append(row)
                    print(f"{case}: {row['status']}")
                receipt['status'] = 'PASS' if all(row['status'] == 'PASS' for row in receipt['cases']) else 'PRODUCT_FAIL'
            if args.keep:
                args.keep.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cpp, args.keep / 'monitor.cpp')
                if binary.exists():
                    shutil.copy2(binary, args.keep / 'monitor-host')
            if build.stderr:
                print(build.stderr)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print('JPW_TEST_RESULT: ' + receipt['status'])
    return 0 if receipt['status'] == 'PASS' else 2 if receipt['status'] in {'ENVIRONMENT_ERROR', 'TEST_HARNESS_FAIL'} else 1


if __name__ == '__main__':
    raise SystemExit(main())

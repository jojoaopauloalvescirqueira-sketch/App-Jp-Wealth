#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property description "JPW GENETRIX · Nucleo unificado observacional; nao negocia ou arma supervisor."
#include <JPWealth/JPW_Genetrix_Observer_Runtime.mqh>
#include <JPWealth/JPW_Genetrix_Accountant_Runtime.mqh>
#include <JPWealth/JPW_Genetrix_Monitor_Core.mqh>
#include <JPWealth/JPW_Genetrix_Monitor_Status.mqh>
input bool InpHistoryCoverageConfirmed=false;
input bool InpCostCoverageConfirmed=false;
input string InpCoverageEvidence="";

JPWMonitorScheduler g_monitor_scheduler;
JPWMonitorSnapshot g_monitor_snapshot;
string g_monitor_key="",g_monitor_token="",g_monitor_declared_account="",g_monitor_reason="";
int g_monitor_writer=INVALID_HANDLE;
double g_monitor_lease_value=0;
bool g_monitor_owned=false,g_monitor_context_dirty=false;
ulong g_monitor_next_claim_ms=0;
int g_monitor_status_deferred_cycles=0;

void JPWMonitorModuleSet(JPWMonitorModuleStatus &module,const int state,const string quality,
                         const string reason,const long observed_utc,const long observed_mono,
                         const int progress)
  {
   module.state=state; module.quality=quality; module.reason=reason;
   module.observed_utc=observed_utc; module.observed_mono_ms=observed_mono;
   module.progress=(progress<0 ? 0 : (progress>100 ? 100 : progress));
  }
void JPWMonitorProjectStatus()
  {
   const bool risk_current=JPWObserverRuntimeRiskLeaseCurrent();
   const bool risk_failed=g_risk_presence_state==JPW_OBSERVER_FAILED;
   JPWMonitorModuleSet(g_monitor_snapshot.stop_risk,
      (!g_observer_runtime_attached ? JPW_MONITOR_DETACHED : (g_observer_runtime_conflict ? JPW_MONITOR_CONFLICT :
       (risk_failed ? JPW_MONITOR_FAILED : (risk_current ? JPW_MONITOR_CURRENT : JPW_MONITOR_PREPARING)))),
      (risk_current ? "Current" : (g_observer_risk_observed_utc>0 ? "Historical" : "N/A")),
      (g_observer_runtime_conflict ? g_observer_runtime_reason :
       (risk_failed ? g_observer_risk_reason : (risk_current ?
        "Última captura publicada; presença não substitui amostra" : "Captura/lease atuais não confirmadas; aguardando revalidação"))),
      g_observer_risk_observed_utc,g_observer_risk_observed_mono,(risk_current ? 100 : 0));
   const bool personal_ok=g_ph_memory_state && !g_ph_gap && !g_ph_incomplete && !g_ph_owner_conflict;
   const string personal_quality=(g_observer_personal_quality==JPW_PERSONAL_CURRENT ? "Current" :
      (g_observer_personal_quality==JPW_PERSONAL_ESTIMATED ? "Estimated" : "N/A"));
   JPWMonitorModuleSet(g_monitor_snapshot.personal,
      (!g_observer_runtime_attached ? JPW_MONITOR_DETACHED : (g_observer_runtime_conflict || g_ph_owner_conflict ? JPW_MONITOR_CONFLICT :
       (personal_ok && personal_quality=="Current" ? JPW_MONITOR_CURRENT : (g_ph_memory_state ? JPW_MONITOR_PARTIAL : JPW_MONITOR_PREPARING)))),
      (!g_observer_runtime_attached && g_observer_personal_observed_utc>0 ? "Historical" :
       (personal_ok ? personal_quality : (g_ph_memory_state ? "Partial" : "N/A"))),
      (g_observer_runtime_conflict ? g_observer_runtime_reason : g_ph_last_problem),
      g_observer_personal_observed_utc,g_observer_personal_observed_mono,(g_ph_memory_state ? 100 : 0));
   const int ledger_state=JPWAccountantStatus();
   const bool ledger_partial=JPWAccountantCoverageAvailable() &&
      !JPWAccountantCoverageComplete();
   JPWMonitorModuleSet(g_monitor_snapshot.ledger,
      (ledger_state==2 && ledger_partial ? JPW_MONITOR_PARTIAL : ledger_state),
      (ledger_state==6 ? "Partial" : (ledger_state==2 ? (ledger_partial ? "Partial" : "Current") :
       (ledger_state==3 ? "Historical" : "N/A"))),
      JPWAccountantReason()+(ledger_partial ? "; cobertura histórica/custos incompleta na geração aceita" : ""),
      JPWAccountantObservedUTC(),JPWAccountantObservedMono(),JPWAccountantProgress());
   const bool raiz_pending=g_reconstruct_open_positions || ArraySize(g_pending)>0;
   JPWMonitorModuleSet(g_monitor_snapshot.raiz,
      (!g_observer_runtime_attached ? JPW_MONITOR_DETACHED : (g_observer_runtime_conflict ? JPW_MONITOR_CONFLICT : (g_db==INVALID_HANDLE ? JPW_MONITOR_FAILED :
       (g_observer_coverage_incomplete ? JPW_MONITOR_PARTIAL : (raiz_pending ? JPW_MONITOR_PREPARING : JPW_MONITOR_HISTORICAL))))),
      (g_observer_coverage_incomplete ? "Partial" : (g_observer_raiz_observed_utc>0 ? "Historical" : "N/A")),
      (g_observer_runtime_conflict ? g_observer_runtime_reason :
       (g_db==INVALID_HANDLE ? "Snapshots Raiz N indisponíveis; outros módulos permanecem independentes" :
        (raiz_pending ? "Preparação de snapshots históricos; não são cotação atual" :
         "Varredura concluída; aguardando novas entradas. Snapshots são históricos"))),
      g_observer_raiz_observed_utc,g_observer_raiz_observed_mono,
      (g_reconstruct_count>0 ? (int)((long)g_reconstruct_cursor*100/g_reconstruct_count) :
       (g_reconstruct_open_positions ? 0 : 100)));
   // Diagnostics publish the last completed handler, including its final IO.
   // The current handler is measured after this publication, not guessed.
   g_monitor_snapshot.last_cycle_ms=(long)g_monitor_scheduler.last_elapsed_ms;
   g_monitor_snapshot.overruns=g_monitor_scheduler.overruns;
  }
bool JPWMonitorOwnershipConfirmed()
  {
   double value=0;
   return(g_monitor_owned && GlobalVariableGet(JPWMonitorLeaseName(g_monitor_token),value) &&
          value==g_monitor_lease_value);
  }
bool JPWMonitorHeartbeat()
  {
   if(!g_monitor_owned) return(false);
   const string name=JPWMonitorLeaseName(g_monitor_token);
   const ulong now=GetTickCount64();
   if(now==0 || now>(ulong)LONG_MAX || name=="" ||
      !GlobalVariableSetOnCondition(name,(double)now,g_monitor_lease_value)) return(false);
   g_monitor_lease_value=(double)now;
   // These technical timestamps never update module capture timestamps.
   g_monitor_snapshot.heartbeat_utc=(long)TimeGMT();
   g_monitor_snapshot.heartbeat_mono_ms=(long)now;
   g_monitor_snapshot.active=true; g_monitor_snapshot.live=true;
   return(true);
  }
void JPWMonitorDetach(const int reason)
  {
   if(g_monitor_owned)
     {
      JPWAccountantDetach(); JPWObserverRuntimeDetach(reason);
      const string lease=JPWMonitorLeaseName(g_monitor_token);
      if(lease!="") GlobalVariableSetOnCondition(lease,0.0,g_monitor_lease_value);
      g_monitor_snapshot.active=false; g_monitor_snapshot.live=false;
      JPWMonitorProjectStatus();
      string diagnostic_reason="";
      if(!JPWMonitorWriteStatus(g_monitor_snapshot,diagnostic_reason))
         Print("JPW núcleo: diagnóstico de encerramento não confirmado: ",diagnostic_reason);
     }
   if(g_monitor_writer!=INVALID_HANDLE) FileClose(g_monitor_writer);
   g_monitor_writer=INVALID_HANDLE; g_monitor_owned=false; g_monitor_lease_value=0;
   g_monitor_key=""; g_monitor_token="";
  }
bool JPWMonitorAttach(const string key)
  {
   if(!JPWRaizNIsHash(key)) { g_monitor_reason="Identidade da conta/instalação indisponível"; return(false); }
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\Monitor");
   const int owner=FileOpen(JPW_MONITOR_FOLDER+"writer_"+key+".lock",FILE_BIN|FILE_READ|FILE_WRITE);
   if(owner==INVALID_HANDLE)
     { g_monitor_reason="Conflito: outro núcleo possui o lock exclusivo da conta/instalação"; return(false); }
   string token="";
   if(!JPWRaizNHash(key+"|monitor_session_v1|"+IntegerToString(ChartID())+"|"+
                    IntegerToString((long)TimeGMT())+"|"+IntegerToString((long)GetMicrosecondCount()),token))
     { FileClose(owner); g_monitor_reason="Identidade do núcleo indisponível"; return(false); }
   const string lease=JPWMonitorLeaseName(token);
   if(lease=="" || GlobalVariableCheck(lease) || !GlobalVariableTemp(lease))
     { FileClose(owner); g_monitor_reason="Lease temporária do núcleo indisponível"; return(false); }
   g_monitor_key=key; g_monitor_token=token; g_monitor_writer=owner;
   g_monitor_owned=true; g_monitor_lease_value=0; g_monitor_reason="";
   g_monitor_status_deferred_cycles=0;
   JPWMonitorSchedulerReset(g_monitor_scheduler); JPWMonitorSnapshotClear(g_monitor_snapshot);
   g_monitor_snapshot.account_key=key; g_monitor_snapshot.publisher_token=token;
   g_monitor_snapshot.role="Unified Monitor";
   g_monitor_snapshot.product_version=JPW_PRODUCT_VERSION; g_monitor_snapshot.build_id=JPW_BUILD_ID;
   g_monitor_snapshot.chart_id=ChartID();
   if(!JPWObserverRuntimeAttach(key))
      g_monitor_reason="Observador não anexado; contabilidade permanece independente";
   // Explicit declaration stays bound to the account observed at original init.
   JPWAccountantAttach(key,g_monitor_declared_account,InpHistoryCoverageConfirmed,
                        InpCostCoverageConfirmed,InpCoverageEvidence);
   if(!JPWMonitorHeartbeat())
     { g_monitor_reason="Titularidade da lease não confirmada"; JPWMonitorDetach(REASON_INITFAILED); return(false); }
   JPWMonitorProjectStatus(); string reason="";
   if(!JPWMonitorWriteStatus(g_monitor_snapshot,reason)) Print("JPW núcleo: ",reason);
   return(true);
  }
int OnInit()
  {
   JPWMonitorSchedulerReset(g_monitor_scheduler); JPWMonitorSnapshotClear(g_monitor_snapshot);
   string key=""; if(JPWObserverReadIdentity(key)) g_monitor_declared_account=key;
   if(key!="" && !JPWMonitorAttach(key)) Print("JPW núcleo: ",g_monitor_reason);
   if(!EventSetTimer(1)) { JPWMonitorDetach(REASON_INITFAILED); return(INIT_FAILED); }
   Print("JPW núcleo unificado observacional; negociação e supervisor não são dependências");
   return(INIT_SUCCEEDED);
  }
void OnDeinit(const int reason) { EventKillTimer(); JPWMonitorDetach(reason); }
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result)
  {
   if(!g_monitor_owned) return;
   string key="";
   if(!JPWObserverReadIdentity(key) || key!=g_monitor_key) { g_monitor_context_dirty=true; return; }
   // Signal only. No historical selection, persistence or notifications here.
   JPWObserverRuntimeTransaction(trans,request,result);
   JPWAccountantTransaction(trans,request,result);
  }
void OnTimer()
  {
   const ulong started=GetTickCount64(); string key="";
   if(!JPWObserverReadIdentity(key))
     { JPWMonitorDetach(REASON_ACCOUNT); g_monitor_reason="Identidade indisponível; publicação atual invalidada"; return; }
   if(g_monitor_context_dirty || (g_monitor_owned && key!=g_monitor_key))
     { JPWMonitorDetach(REASON_ACCOUNT); g_monitor_context_dirty=false; }
   if(!g_monitor_owned)
     {
      if(started<g_monitor_next_claim_ms) return;
      g_monitor_next_claim_ms=started+1000;
      if(!JPWMonitorAttach(key)) { Print("JPW núcleo: ",g_monitor_reason); return; }
     }
   if(!JPWMonitorOwnershipConfirmed())
     { JPWMonitorDetach(REASON_ACCOUNT); g_monitor_reason="Lease alterada; trabalho suspenso sem roubar titularidade"; return; }
   const int due_mask=15; int done_mask=0; bool status_attempted=false;
   JPWMonitorSchedulerBegin(g_monitor_scheduler,due_mask);
   // Technical publication is normally last. Under persistent indivisible
   // overruns it receives one promoted opportunity, never an unlimited tail.
   if(g_monitor_status_deferred_cycles>=JPW_MONITOR_FAIR_PROMOTION &&
      GetTickCount64()>=started && GetTickCount64()-started<JPW_MONITOR_BUDGET_MS)
     {
      JPWMonitorProjectStatus();
      if(!JPWMonitorHeartbeat()) { JPWMonitorDetach(REASON_ACCOUNT); return; }
      string reason="";
      if(!JPWMonitorWriteStatus(g_monitor_snapshot,reason)) Print("JPW núcleo: ",reason);
      status_attempted=true; g_monitor_status_deferred_cycles=0;
     }
   string context_before="";
   if(!JPWObserverReadIdentity(context_before) || context_before!=g_monitor_key)
     { JPWMonitorDetach(REASON_ACCOUNT); return; }
   if(GetTickCount64()>=started && GetTickCount64()-started<JPW_MONITOR_BUDGET_MS)
      JPWObserverRuntimePrepare(started);
   string context_after="";
   if(!JPWObserverReadIdentity(context_after) || context_after!=g_monitor_key)
     { JPWMonitorDetach(REASON_ACCOUNT); return; }
   for(int jobs=0;jobs<4;jobs++)
     {
      const int module=JPWMonitorSchedulerNext(g_monitor_scheduler,started,GetTickCount64(),due_mask,done_mask);
      if(module<0) break;
      string before="";
      if(!JPWObserverReadIdentity(before) || before!=g_monitor_key)
        { g_monitor_context_dirty=true; break; }
      if(module==2) JPWAccountantTick(started,JPW_MONITOR_LEDGER_SLICE_MS);
      else JPWObserverRuntimeTick(started,(module==3 ? 2 : module));
      done_mask|=1<<module;
      JPWMonitorSchedulerServiced(g_monitor_scheduler,module,GetTickCount64());
      string after="";
      if(!JPWObserverReadIdentity(after) || after!=g_monitor_key)
        { g_monitor_context_dirty=true; break; }
     }
   if(g_monitor_context_dirty) { JPWMonitorDetach(REASON_ACCOUNT); return; }
   if((done_mask&2)==0) JPWPersonalControllerDeferred();
   if(!g_observer_runtime_conflict) JPWStopRiskPresenceRefresh();
   if(!status_attempted && GetTickCount64()>=started &&
      GetTickCount64()-started<JPW_MONITOR_BUDGET_MS)
     {
      JPWMonitorProjectStatus();
      if(!JPWMonitorHeartbeat()) { JPWMonitorDetach(REASON_ACCOUNT); return; }
      string reason="";
      if(!JPWMonitorWriteStatus(g_monitor_snapshot,reason)) Print("JPW núcleo: ",reason);
      status_attempted=true; g_monitor_status_deferred_cycles=0;
     }
   if(!status_attempted && g_monitor_status_deferred_cycles<1000000)
      g_monitor_status_deferred_cycles++;
   if(GetTickCount64()<started || GetTickCount64()-started>=JPW_MONITOR_BUDGET_MS)
      JPWObserverDiagnostic(JPW_DIAG_BUDGET_DEFERRED);
   JPWMonitorSchedulerFinish(g_monitor_scheduler,started,GetTickCount64(),due_mask,done_mask);
  }

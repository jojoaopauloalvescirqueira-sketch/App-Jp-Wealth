#ifndef JPW_GENETRIX_ACCOUNTANT_RUNTIME_MQH
#define JPW_GENETRIX_ACCOUNTANT_RUNTIME_MQH
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#include <JPWealth/JPW_Genetrix_Ledger_Preparation.mqh>
// Observation/accounting only. Lifecycle and the single timer belong to Monitor.
// Status: 0 detached,1 preparing,2 Current,3 historical/Estimated,4 blocked,
// 5 failure,6 current capture with incomplete coverage (Partial).
int g_jpw_accountant_db=INVALID_HANDLE,g_jpw_accountant_lock=INVALID_HANDLE,g_jpw_accountant_status=0;
string g_jpw_accountant_key="",g_jpw_accountant_token="",g_jpw_accountant_reason="";
string g_jpw_accountant_declared_account="",g_jpw_accountant_evidence="";
bool g_jpw_accountant_history=false,g_jpw_accountant_costs=false,g_jpw_accountant_dirty=true;
bool g_jpw_accountant_preparing=false,g_jpw_accountant_queue_loss=false,g_jpw_accountant_context_changed=false;
bool g_jpw_accountant_published_history=false,g_jpw_accountant_published_costs=false;
bool g_jpw_accountant_published_partial=true;
long g_jpw_accountant_deletes[],g_jpw_accountant_observed_utc=0,g_jpw_accountant_observed_mono=0;
double g_jpw_accountant_lease=0;
ulong g_jpw_accountant_next=0,g_jpw_accountant_last_elapsed=0,g_jpw_accountant_epoch=0,g_jpw_accountant_attempt_epoch=0;
CJPWLedgerPreparation g_jpw_accountant_preparation;

void JPWAccountantRuntimeInvalidate()
  {
   string name=JPWLedgerLease(g_jpw_accountant_token);
   if(name!="" && g_jpw_accountant_lease!=0)
      GlobalVariableSetOnCondition(name,0.0,g_jpw_accountant_lease);
   g_jpw_accountant_lease=0;
  }
void JPWAccountantRuntimeRelease()
  {
   JPWAccountantRuntimeInvalidate(); g_jpw_accountant_preparation.Abort();
   if(g_jpw_accountant_db!=INVALID_HANDLE) DatabaseClose(g_jpw_accountant_db);
   if(g_jpw_accountant_lock!=INVALID_HANDLE) FileClose(g_jpw_accountant_lock);
   g_jpw_accountant_db=INVALID_HANDLE; g_jpw_accountant_lock=INVALID_HANDLE;
   g_jpw_accountant_token=""; g_jpw_accountant_preparing=false;
  }
void JPWAccountantDetach()
  {
   JPWAccountantRuntimeRelease(); g_jpw_accountant_key="";
   ArrayResize(g_jpw_accountant_deletes,0); g_jpw_accountant_queue_loss=false;
   g_jpw_accountant_dirty=true; g_jpw_accountant_context_changed=false;
   g_jpw_accountant_status=0; g_jpw_accountant_reason="Módulo contábil não anexado";
   g_jpw_accountant_observed_utc=0; g_jpw_accountant_observed_mono=0; g_jpw_accountant_last_elapsed=0;
   g_jpw_accountant_published_history=false; g_jpw_accountant_published_costs=false;
   g_jpw_accountant_published_partial=true;
  }
bool JPWAccountantRuntimeOpen()
  {
   JPWAccountantRuntimeRelease();
   if(!FolderCreate("JPWealth\\Genetrix"))
     { g_jpw_accountant_status=5; g_jpw_accountant_reason="Diretório contábil indisponível"; return(false); }
   // This exact legacy lock is retained. A new Monitor ownership lock is not a
   // substitute for it: old Accountant binaries do not know the new host lock.
   g_jpw_accountant_lock=FileOpen(JPW_LEDGER_FOLDER+"writer_"+g_jpw_accountant_key+".lock",FILE_BIN|FILE_READ|FILE_WRITE);
   if(g_jpw_accountant_lock==INVALID_HANDLE)
     { g_jpw_accountant_status=4; g_jpw_accountant_reason="Outro produtor/Accountant pode deter o lock contábil; não tomado"; return(false); }
   string reason="";
   if(!JPWLedgerOpen(g_jpw_accountant_key,true,g_jpw_accountant_db,reason) ||
      !JPWRaizNHash(g_jpw_accountant_key+"|"+JPW_PRODUCT_VERSION+"|"+IntegerToString(ChartID())+"|"+
         IntegerToString((long)TimeGMT())+"|"+IntegerToString((long)GetTickCount64()),g_jpw_accountant_token))
     { JPWAccountantRuntimeRelease(); g_jpw_accountant_status=5;
       g_jpw_accountant_reason=(reason!="" ? reason : "Identidade da sessão contábil indisponível"); return(false); }
   string name=JPWLedgerLease(g_jpw_accountant_token);
   if(name=="" || !GlobalVariableTemp(name) || !GlobalVariableSetOnCondition(name,0.0,0.0))
     { JPWAccountantRuntimeRelease(); g_jpw_accountant_status=5; g_jpw_accountant_reason="Lease contábil indisponível"; return(false); }
   g_jpw_accountant_status=1; g_jpw_accountant_reason="Preparando contabilidade; cobertura não inferida";
   g_jpw_accountant_dirty=true; return(true);
  }
bool JPWAccountantAttach(const string key,const string declared_account,const bool history_confirmed,
                         const bool costs_confirmed,const string evidence)
  {
   JPWAccountantDetach(); g_jpw_accountant_key=key; g_jpw_accountant_declared_account=declared_account;
   g_jpw_accountant_history=history_confirmed; g_jpw_accountant_costs=costs_confirmed; g_jpw_accountant_evidence=evidence;
   g_jpw_accountant_epoch++; g_jpw_accountant_next=0;
   string actual="",currency="";
   if(!JPWRaizNIsHash(key) || !JPWLedgerIdentity(actual,currency) || actual!=key)
     { g_jpw_accountant_status=4; g_jpw_accountant_reason="Conta de anexação não confirmada; módulo contábil indisponível"; return(false); }
   bool ok=JPWAccountantRuntimeOpen(); if(!ok) g_jpw_accountant_next=GetTickCount64()+5000; return(ok);
  }
void JPWAccountantTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result)
  {
   if(g_jpw_accountant_key=="") return;
   g_jpw_accountant_dirty=true; g_jpw_accountant_epoch++; JPWAccountantRuntimeInvalidate();
   string key="",currency="";
   if(!JPWLedgerIdentity(key,currency) || key!=g_jpw_accountant_key)
     { g_jpw_accountant_context_changed=true; return; }
   if(trans.type!=TRADE_TRANSACTION_DEAL_DELETE || trans.deal==0 || trans.deal>(ulong)LONG_MAX) return;
   for(int i=0;i<ArraySize(g_jpw_accountant_deletes);i++) if(g_jpw_accountant_deletes[i]==(long)trans.deal) return;
   int n=ArraySize(g_jpw_accountant_deletes);
   if(n>=128 || ArrayResize(g_jpw_accountant_deletes,n+1)!=n+1) { g_jpw_accountant_queue_loss=true; return; }
   g_jpw_accountant_deletes[n]=(long)trans.deal;
  }
void JPWAccountantTick(const ulong cycle_started,const uint budget_ms)
  {
   const ulong started=GetTickCount64(); g_jpw_accountant_last_elapsed=0;
   if(g_jpw_accountant_key=="" || budget_ms==0 || started<cycle_started || started-cycle_started>=500) return;
   ulong slice=(ulong)MathMin(100,(double)budget_ms),deadline=started+slice;
   if(deadline>cycle_started+500) deadline=cycle_started+500;
   string key="",currency="";
   if(g_jpw_accountant_context_changed || !JPWLedgerIdentity(key,currency) || key!=g_jpw_accountant_key)
     { JPWAccountantRuntimeRelease(); ArrayResize(g_jpw_accountant_deletes,0); g_jpw_accountant_queue_loss=false;
       g_jpw_accountant_status=4; g_jpw_accountant_reason="Conta mudou; preparação/eventos descartados, aguardando nova anexação";
       g_jpw_accountant_last_elapsed=GetTickCount64()-started; return; }
   if(g_jpw_accountant_db==INVALID_HANDLE)
     { if(started<g_jpw_accountant_next) return;
       if(!JPWAccountantRuntimeOpen()) { g_jpw_accountant_next=GetTickCount64()+5000;
         g_jpw_accountant_last_elapsed=GetTickCount64()-started; return; } }
   if(g_jpw_accountant_preparing && g_jpw_accountant_attempt_epoch!=g_jpw_accountant_epoch)
     { g_jpw_accountant_preparation.Abort(); g_jpw_accountant_preparing=false;
       g_jpw_accountant_reason="Transação recebida; preparação anterior invalidada"; }
   if(!g_jpw_accountant_preparing)
     {
      if(!g_jpw_accountant_dirty && started<g_jpw_accountant_next) return;
      if(started<g_jpw_accountant_next && g_jpw_accountant_status>=4) return;
      JPWAccountantRuntimeInvalidate();
      bool ok=g_jpw_accountant_preparation.Begin(g_jpw_accountant_db,g_jpw_accountant_key,g_jpw_accountant_token,
         g_jpw_accountant_declared_account,g_jpw_accountant_history,g_jpw_accountant_costs,g_jpw_accountant_evidence,
         g_jpw_accountant_deletes,g_jpw_accountant_queue_loss);
      if(!ok) { g_jpw_accountant_status=5; g_jpw_accountant_reason=g_jpw_accountant_preparation.reason;
        g_jpw_accountant_next=GetTickCount64()+5000; g_jpw_accountant_last_elapsed=GetTickCount64()-started; return; }
      g_jpw_accountant_attempt_epoch=g_jpw_accountant_epoch; g_jpw_accountant_preparing=true;
      g_jpw_accountant_dirty=false; g_jpw_accountant_status=1;
     }
   bool ready=false;
   bool ok=g_jpw_accountant_preparation.Step(deadline,ready);
   if(ok && ready && GetTickCount64()<deadline)
     {
      ok=(g_jpw_accountant_attempt_epoch==g_jpw_accountant_epoch) && g_jpw_accountant_preparation.Publish();
      if(ok)
        {
         g_jpw_accountant_observed_utc=g_jpw_accountant_preparation.view.observed_utc;
         g_jpw_accountant_observed_mono=g_jpw_accountant_preparation.view.observed_mono_ms;
         g_jpw_accountant_published_history=g_jpw_accountant_preparation.view.history_complete;
         g_jpw_accountant_published_costs=g_jpw_accountant_preparation.view.costs_complete;
         g_jpw_accountant_published_partial=!g_jpw_accountant_published_history || !g_jpw_accountant_published_costs;
         for(int c=0;c<ArraySize(g_jpw_accountant_preparation.replay.cycles);c++)
            if(g_jpw_accountant_preparation.replay.cycles[c].partial) g_jpw_accountant_published_partial=true;
         // Execution can change while SQLite commits. Never grant Current on
         // a generation whose composition cannot be revalidated afterwards.
         bool live=g_jpw_accountant_preparation.RevalidateLive();
         if(live && g_jpw_accountant_preparation.view.quality==1)
           { string name=JPWLedgerLease(g_jpw_accountant_token);
             live=GlobalVariableSetOnCondition(name,(double)g_jpw_accountant_observed_mono,0.0);
             if(live) g_jpw_accountant_lease=(double)g_jpw_accountant_observed_mono; }
         g_jpw_accountant_status=(live && g_jpw_accountant_preparation.view.quality==1 ?
            (!g_jpw_accountant_published_partial ? 2 : 6) : 3);
         g_jpw_accountant_reason=(live ? g_jpw_accountant_preparation.view.reason : "Geração gravada; contexto posterior não confirmado, somente histórico");
         ArrayResize(g_jpw_accountant_deletes,0); g_jpw_accountant_queue_loss=false;
         g_jpw_accountant_preparing=false; g_jpw_accountant_dirty=!live;
         g_jpw_accountant_next=GetTickCount64()+(live ? 5000 : 0);
        }
     }
   if(!ok)
     { JPWAccountantRuntimeInvalidate(); g_jpw_accountant_preparing=false; g_jpw_accountant_dirty=true;
       g_jpw_accountant_status=5; g_jpw_accountant_reason=g_jpw_accountant_preparation.reason;
       if(g_jpw_accountant_reason=="") g_jpw_accountant_reason="Preparação/publicação recusada; base preservada";
       g_jpw_accountant_preparation.Abort(); g_jpw_accountant_next=GetTickCount64()+5000; }
   else if(g_jpw_accountant_preparing)
      g_jpw_accountant_reason="Contabilidade em preparação/revalidação; nenhuma geração parcial publicada";
   g_jpw_accountant_last_elapsed=GetTickCount64()-started;
  }
int JPWAccountantStatus()
  { if((g_jpw_accountant_status==2 || g_jpw_accountant_status==6) && (TerminalInfoInteger(TERMINAL_CONNECTED)==0 || g_jpw_accountant_lease==0 ||
       GetTickCount64()<(ulong)g_jpw_accountant_observed_mono ||
       GetTickCount64()-(ulong)g_jpw_accountant_observed_mono>JPW_LEDGER_MAX_AGE_MS)) return(3);
    return(g_jpw_accountant_status); }
string JPWAccountantReason() { return(g_jpw_accountant_reason); }
long JPWAccountantObservedUTC() { return(g_jpw_accountant_observed_utc); }
long JPWAccountantObservedMono() { return(g_jpw_accountant_observed_mono); }
bool JPWAccountantCoverageAvailable() { return(g_jpw_accountant_observed_utc>0); }
bool JPWAccountantHistoryComplete() { return(g_jpw_accountant_published_history); }
bool JPWAccountantCostsComplete() { return(g_jpw_accountant_published_costs); }
bool JPWAccountantCoverageComplete() { return(JPWAccountantCoverageAvailable() && !g_jpw_accountant_published_partial); }
int JPWAccountantProgress() { return(g_jpw_accountant_preparation.progress); }
ulong JPWAccountantLastElapsed() { return(g_jpw_accountant_last_elapsed); }
bool JPWAccountantPending()
  { return(g_jpw_accountant_key!="" && (g_jpw_accountant_preparing || g_jpw_accountant_dirty || GetTickCount64()>=g_jpw_accountant_next)); }
#endif

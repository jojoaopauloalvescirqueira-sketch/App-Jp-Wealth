#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property description "JPW GENETRIX: contador local de ciclos inferidos. Não negocia."
#include <JPWealth/JPW_Genetrix_Ledger_Terminal.mqh>
input bool InpHistoryCoverageConfirmed=false;
input bool InpCostCoverageConfirmed=false;
input string InpCoverageEvidence=""; // Reference documenting account, origin/flat and covered period/costs.
string g_ledger_coverage_account="";

int g_ledger_db=INVALID_HANDLE,g_ledger_writer_lock=INVALID_HANDLE;
string g_ledger_key="",g_ledger_token="";
double g_ledger_lease_value=0;
long g_ledger_deletes[];
bool g_ledger_dirty=true,g_ledger_queue_loss=false,g_ledger_last_failed=false;
ulong g_ledger_next_ms=0;

void JPWAccountantInvalidateLease()
  {
   string name=JPWLedgerLease(g_ledger_token);
   if(name!="" && g_ledger_lease_value!=0)
      GlobalVariableSetOnCondition(name,0.0,g_ledger_lease_value);
   g_ledger_lease_value=0;
  }
void JPWAccountantClose()
  {
   JPWAccountantInvalidateLease();
   if(g_ledger_db!=INVALID_HANDLE) DatabaseClose(g_ledger_db);
   if(g_ledger_writer_lock!=INVALID_HANDLE) FileClose(g_ledger_writer_lock);
   g_ledger_db=INVALID_HANDLE; g_ledger_writer_lock=INVALID_HANDLE;
   g_ledger_key=""; g_ledger_token="";
  }
bool JPWAccountantOpen(const string key)
  {
   JPWAccountantClose();
   if(!FolderCreate("JPWealth\\Genetrix")) return(false);
   // Exclusive, unshared file handle lasts through the account writer session.
   g_ledger_writer_lock=FileOpen(JPW_LEDGER_FOLDER+"writer_"+key+".lock",FILE_BIN|FILE_READ|FILE_WRITE);
   if(g_ledger_writer_lock==INVALID_HANDLE) return(false);
   string reason="";
   if(!JPWLedgerOpen(key,true,g_ledger_db,reason) || !JPWRaizNHash(key+"|"+JPW_PRODUCT_VERSION+"|"+
      JPWLedgerInt(ChartID())+"|"+JPWLedgerInt((long)TimeGMT())+"|"+JPWLedgerInt((long)GetTickCount64()),g_ledger_token))
     { JPWAccountantClose(); return(false); }
   g_ledger_key=key;
   string name=JPWLedgerLease(g_ledger_token);
   if(name=="" || !GlobalVariableTemp(name) || !GlobalVariableSetOnCondition(name,0.0,0.0))
     { JPWAccountantClose(); return(false); }
   ArrayResize(g_ledger_deletes,0); g_ledger_dirty=true; g_ledger_next_ms=0;
   return(true);
  }
int OnInit()
  {
   string key="",currency="";
   if(!JPWLedgerIdentity(key,currency) || !JPWAccountantOpen(key) || !EventSetTimer(1))
     { JPWAccountantClose(); Print("JPW ledger: INIT_UNAVAILABLE"); return(INIT_FAILED); }
   g_ledger_coverage_account=key;
   return(INIT_SUCCEEDED);
  }
void OnDeinit(const int reason)
  { EventKillTimer(); JPWAccountantClose(); }
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result)
  {
   g_ledger_dirty=true;
   JPWAccountantInvalidateLease(); // any transaction invalidates Current until reconciliation
   if(trans.type!=TRADE_TRANSACTION_DEAL_DELETE || trans.deal==0 || trans.deal>(ulong)LONG_MAX) return;
   for(int i=0;i<ArraySize(g_ledger_deletes);i++) if(g_ledger_deletes[i]==(long)trans.deal) return;
   int n=ArraySize(g_ledger_deletes);
   if(n>=128 || ArrayResize(g_ledger_deletes,n+1)!=n+1) { g_ledger_queue_loss=true; return; }
   g_ledger_deletes[n]=(long)trans.deal;
  }
void OnTimer()
  {
   string key="",currency="";
   if(!JPWLedgerIdentity(key,currency)) { JPWAccountantInvalidateLease(); return; }
   if(key!=g_ledger_key)
     {
      // Never carry financial events from a prior account into another account.
      JPWAccountantClose(); ArrayResize(g_ledger_deletes,0); g_ledger_queue_loss=false;
      if(!JPWAccountantOpen(key)) { Print("JPW ledger: WRITER_UNAVAILABLE"); return; }
     }
   ulong now=GetTickCount64();
   if(!g_ledger_dirty && now<g_ledger_next_ms) return;
   g_ledger_next_ms=now+5000; g_ledger_dirty=false;
   JPWAccountantInvalidateLease();
   JPWLedgerDeal deals[]; JPWLedgerOrder orders[]; JPWLedgerPosition positions[];
   JPWLedgerView view; string composition="",reason="";
   bool ok=JPWLedgerCollectTerminal(deals,orders,positions,view,composition,reason) && view.account_key==g_ledger_key;
   if(ok)
     {
      view.publisher_token=g_ledger_token;
      JPWLedgerApplyDeclaredCoverage(view,InpHistoryCoverageConfirmed,InpCostCoverageConfirmed,
                                     InpCoverageEvidence,g_ledger_coverage_account);
      ok=JPWLedgerCommitCollection(g_ledger_db,deals,orders,positions,g_ledger_deletes,
                                  g_ledger_queue_loss,view,composition,reason);
     }
   if(ok)
     {
      string name=JPWLedgerLease(g_ledger_token);
      ok=GlobalVariableSetOnCondition(name,(double)view.observed_mono_ms,0.0);
      if(ok)
        { g_ledger_lease_value=(double)view.observed_mono_ms;
          ArrayResize(g_ledger_deletes,0); g_ledger_queue_loss=false; }
     }
   if(!ok)
     { g_ledger_dirty=true; if(!g_ledger_last_failed) Print("JPW ledger: COLLECTION_OR_STORAGE_UNAVAILABLE"); }
   else if(g_ledger_last_failed) Print("JPW ledger: COLLECTION_RECOVERED");
   g_ledger_last_failed=!ok;
  }

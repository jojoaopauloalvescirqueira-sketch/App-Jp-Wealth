#ifndef JPW_GENETRIX_LEDGER_BRIDGE_MQH
#define JPW_GENETRIX_LEDGER_BRIDGE_MQH
#include <JPWealth/JPW_Genetrix_Ledger_Terminal.mqh>
// Public, read-only UI contract. A cycle selector is RAM state, not account
// persistence. UI must not reconstruct financial formulas or call this on draw.
// Cycle member_identifiers is canonical numeric ascending CSV. A v1 row without
// this projection has members_available=false; absence is not a proven empty set.
// All identifiers include closed members and the original Genesis; no ticket promotion.
bool JPWLedgerBridgeRefresh(JPWLedgerCycle &cycles[],JPWLedgerView &view,string &reason)
  {
   ArrayResize(cycles,0); JPWLedgerClearView(view); reason="";
   string key="",currency="";
   if(!JPWLedgerIdentity(key,currency)) { reason="Identidade da conta indisponível"; return(false); }
   int db=INVALID_HANDLE;
   if(!JPWLedgerOpen(key,false,db,reason)) return(false);
   string composition="";
   bool ok=DatabaseTransactionBegin(db) && JPWLedgerReadProjection(db,key,view,cycles,composition,reason);
   if(ok) ok=DatabaseTransactionCommit(db);
   else DatabaseTransactionRollback(db);
   DatabaseClose(db);
   string after="",after_currency="";
   if(!ok || !JPWLedgerIdentity(after,after_currency) || after!=key || after_currency!=currency || view.currency!=currency)
     { ArrayResize(cycles,0); JPWLedgerClearView(view); if(reason=="") reason="Conta/generation não confirmada"; return(false); }
   const long now=(long)GetTickCount64(); double lease=0,balance=0;
   JPWLedgerPosition positions[]; JPWLedgerOrder orders[]; bool fresh=false;
   string live_reason="",live_digest="";
   long mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   bool current=view.quality==1 && view.healthy && view.margin_mode==mode && mode==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
      TerminalInfoInteger(TERMINAL_CONNECTED)!=0 && now>=view.observed_mono_ms &&
      now-view.observed_mono_ms<=JPW_LEDGER_MAX_AGE_MS &&
      GlobalVariableGet(JPWLedgerLease(view.publisher_token),lease) && lease==(double)view.observed_mono_ms &&
      JPWLedgerAccountDouble(ACCOUNT_BALANCE,balance) && balance==view.balance &&
      JPWLedgerReadLive(positions,orders,fresh,live_reason) && fresh &&
      JPWLedgerComposition(positions,orders,key,balance,mode,live_digest) && live_digest==composition;
   string final_key="",final_currency=""; double final_balance=0;
   if(!JPWLedgerIdentity(final_key,final_currency) || final_key!=key || final_currency!=currency)
     { ArrayResize(cycles,0); JPWLedgerClearView(view); reason="Conta mudou durante enumeração; N/A"; return(false); }
   long final_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(current) current=JPWLedgerAccountDouble(ACCOUNT_BALANCE,final_balance) && final_balance==view.balance &&
      final_mode==mode && TerminalInfoInteger(TERMINAL_CONNECTED)!=0;
   mode=final_mode;
   if(!current)
     { view.quality=2; view.reason="Última observação histórica; Accountant/composição atual não confirmado"; }
   if(mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { view.quality=0; view.reason="Ledger v1 hedging; conta corrente não suportada";
       for(int i=0;i<ArraySize(cycles);i++) { cycles[i].amount_valid=false; cycles[i].percent_valid=false; } }
   return(true);
  }
int JPWLedgerBridgeFind(JPWLedgerCycle &cycles[],const string cycle_id)
  { for(int i=0;i<ArraySize(cycles);i++) if(cycles[i].cycle_id==cycle_id) return(i); return(-1); }
#endif

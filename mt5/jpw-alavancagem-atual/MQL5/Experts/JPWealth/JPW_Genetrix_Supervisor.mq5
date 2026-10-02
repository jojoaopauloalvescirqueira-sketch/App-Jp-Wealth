#property copyright "JP Wealth"
#property version "1.000"
#property description "Additional 7x gross/equity breaker. Observe by default. Explicit demo-only execution; not a V11 controller."
#include <JPWealth/JPW_Genetrix_Risk_Terminal.mqh>
#include <JPWealth/JPW_Genetrix_Risk_Store.mqh>

input bool InpArmDemo=false;
input long InpDemoLogin=0;
input string InpDemoServer="";
input string InpDemoSession=""; // Copy the OBSERVE challenge, then explicitly change these inputs.
input ulong InpMaxDeviationPoints=0; // No automatic repricing; native execution policy still applies.

JPWAccount g_supervisor_account;
JPWRiskRecord g_supervisor_record;
int g_supervisor_lock=INVALID_HANDLE;
bool g_supervisor_store_failed=false;
bool g_supervisor_context_failed=false;
bool g_supervisor_timer_busy=false;
bool g_supervisor_dirty=true;
bool g_supervisor_correction=false;
bool g_supervisor_reply_pending=false;
bool g_supervisor_plan_available=false;
string g_supervisor_disarm_reason="";
JPWRiskAction g_supervisor_proposal;
MqlTradeResult g_supervisor_reply;
int g_supervisor_history_cursor=-1;
int g_supervisor_history_count=-1;
const ulong JPW_SUPERVISOR_MAGIC=700107;

string JPWRiskPhaseText(const JPWRiskPhase phase)
  {
   if(phase==JPW_RISK_UNKNOWN) return("ACTION_UNKNOWN");
   if(phase==JPW_RISK_REMAINDER) return("WHOLE_INTENT_REMAINDER");
   if(phase==JPW_RISK_PAUSED_LIFO) return("PAUSED_LIFO");
   return(phase==JPW_RISK_READY ? "READY_DEMO" : "OBSERVE");
  }
void JPWSupervisorRefreshView(const string reason)
  {
   g_supervisor_record.view.schema=JPW_RISK_SCHEMA;
   g_supervisor_record.view.state=(g_supervisor_record.machine.phase==JPW_RISK_READY &&
      !g_supervisor_record.machine.armed ? "OBSERVE" : JPWRiskPhaseText(g_supervisor_record.machine.phase));
   g_supervisor_record.view.reason=reason;
   if(g_supervisor_disarm_reason!="" && StringFind(reason,g_supervisor_disarm_reason)<0)
      g_supervisor_record.view.reason+=" | "+g_supervisor_disarm_reason;
   g_supervisor_record.view.action_kind=(int)g_supervisor_record.machine.active.kind;
   g_supervisor_record.view.action_ticket=g_supervisor_record.machine.active.ticket;
   g_supervisor_record.view.action_identifier=g_supervisor_record.machine.active.identifier;
   g_supervisor_record.view.action_volume=g_supervisor_record.machine.active.volume;
   g_supervisor_record.view.protection_incomplete=g_supervisor_record.machine.protection_incomplete;
   g_supervisor_record.view.demo_armed=g_supervisor_record.machine.armed;
  }
void JPWSupervisorPresent()
  {
   JPWRiskView view=g_supervisor_record.view;
   string reading="N/A · no current financial reading displayed";
   if(view.quality=="Current" || view.quality=="Estimated")
      reading=JPWFormatLeverage(view.leverage)+" · "+view.quality+
         " · captured UTC "+IntegerToString(view.observed_utc);
   string projected="N/A";
   if(view.quality!="N/A" && view.pending_projection_valid)
      projected=JPWFormatLeverage(view.projected_leverage);
   string action="N/A · proposal/execution blocked or reconciliation required";
   if(g_supervisor_record.machine.active.kind!=JPW_RISK_NONE)
      action="Active whole/cancel intention: "+IntegerToString(view.action_kind)+
         " / "+IntegerToString((long)view.action_ticket)+" · no completion inferred";
   else if(g_supervisor_plan_available && view.quality!="N/A")
      action="Next action (proposal unless armed): "+IntegerToString((int)g_supervisor_proposal.kind)+
         " / "+IntegerToString((long)g_supervisor_proposal.ticket);
   Comment("JPW Supervisor · ",view.state," · ",view.demo_armed ? "DEMO ARMED" : "OBSERVE / NO NEW EXECUTION",
      "\n",view.reason,
      "\nGross/equity reading: ",reading,
      "\nPending static projection: ",projected,
      "\n",action,
      "\nProtection incomplete: ",view.protection_incomplete ? "YES" : "NO",
      "\nEntry prices / current FX / frozen equity; future unknown; no external veto.",
      "\nSession challenge: ",view.session_challenge,
      "\nDemo arm requires exact account/server + previous OBSERVE challenge in inputs.");
  }
bool JPWSupervisorPersist(const string reason,const string receipt="")
  {
   if(g_supervisor_store_failed || g_supervisor_lock==INVALID_HANDLE) return(false);
   JPWSupervisorRefreshView(reason); JPWSupervisorPresent(); string why="";
   if(!JPWRiskSaveRecord(g_supervisor_record,why) ||
      (receipt!="" && !JPWRiskAppendReceipt(g_supervisor_record,receipt,why)))
     {
      g_supervisor_store_failed=true; g_supervisor_record.machine.armed=false;
      g_supervisor_record.machine.protection_incomplete=true;
      Comment("JPW Supervisor: storage unconfirmed; OBSERVE / no requests. ",why);
      Print("JPW Supervisor: storage unconfirmed; no further requests.");
      return(false);
     }
   return(true);
  }
bool JPWSupervisorNewToken(string &token)
  {
   string hash="";
   if(!JPWProfileHash(g_supervisor_record.view.account_key+
      JPWProfileFrame(g_supervisor_record.view.session_challenge)+
      JPWProfileFrame(IntegerToString((long)GetTickCount64()))+
      JPWProfileFrame(IntegerToString((long)TimeLocal()))+
      JPWProfileFrame(IntegerToString(ChartID()))+
      JPWProfileFrame(IntegerToString(g_supervisor_record.view.generation)),hash)) return(false);
   token=StringSubstr(hash,0,24); return(true);
  }
bool JPWSupervisorDefinitiveRefusal(const uint code)
  {
   // Whitelist; timeout/connection/locked/error/unknown codes remain UNKNOWN.
   return(code==TRADE_RETCODE_REQUOTE || code==TRADE_RETCODE_REJECT || code==TRADE_RETCODE_CANCEL ||
      code==TRADE_RETCODE_INVALID || code==TRADE_RETCODE_INVALID_VOLUME || code==TRADE_RETCODE_INVALID_PRICE ||
      code==TRADE_RETCODE_INVALID_STOPS || code==TRADE_RETCODE_TRADE_DISABLED || code==TRADE_RETCODE_MARKET_CLOSED ||
      code==TRADE_RETCODE_NO_MONEY || code==TRADE_RETCODE_PRICE_CHANGED || code==TRADE_RETCODE_PRICE_OFF ||
      code==TRADE_RETCODE_INVALID_EXPIRATION || code==TRADE_RETCODE_TOO_MANY_REQUESTS ||
      code==TRADE_RETCODE_SERVER_DISABLES_AT || code==TRADE_RETCODE_CLIENT_DISABLES_AT ||
      code==TRADE_RETCODE_FROZEN || code==TRADE_RETCODE_INVALID_FILL || code==TRADE_RETCODE_ONLY_REAL ||
      code==TRADE_RETCODE_LIMIT_ORDERS || code==TRADE_RETCODE_LIMIT_VOLUME || code==TRADE_RETCODE_INVALID_ORDER ||
      code==TRADE_RETCODE_INVALID_CLOSE_VOLUME || code==TRADE_RETCODE_CLOSE_ORDER_EXIST ||
      code==TRADE_RETCODE_LIMIT_POSITIONS || code==TRADE_RETCODE_LONG_ONLY || code==TRADE_RETCODE_SHORT_ONLY ||
      code==TRADE_RETCODE_CLOSE_ONLY || code==TRADE_RETCODE_FIFO_CLOSE || code==TRADE_RETCODE_HEDGE_PROHIBITED ||
      code==TRADE_RETCODE_POSITION_CLOSED || code==TRADE_RETCODE_NO_CHANGES);
  }
bool JPWSupervisorTerminalOrder(const long state)
  { return(state==ORDER_STATE_FILLED || state==ORDER_STATE_CANCELED ||
           state==ORDER_STATE_REJECTED || state==ORDER_STATE_EXPIRED); }

// Positive history evidence only. Absence or elapsed time never releases UNKNOWN.
bool JPWSupervisorFindRequestOrder()
  {
   if(g_supervisor_record.machine.request_order>0) return(true);
   if(g_supervisor_record.machine.request_deal>0 && HistoryDealSelect(g_supervisor_record.machine.request_deal))
     {
      const ulong order=(ulong)HistoryDealGetInteger(g_supervisor_record.machine.request_deal,DEAL_ORDER);
      if(order>0) { g_supervisor_record.machine.request_order=order; return(true); }
     }
   if(!HistorySelect(0,TimeCurrent())) return(false);
   const int count=HistoryOrdersTotal();
   if(count!=g_supervisor_history_count || g_supervisor_history_cursor<0)
     { g_supervisor_history_count=count; g_supervisor_history_cursor=count-1; }
   int examined=0;
   while(g_supervisor_history_cursor>=0 && examined<128)
     {
      const ulong order=HistoryOrderGetTicket(g_supervisor_history_cursor--); examined++;
      if(order==0) continue;
      if(HistoryOrderGetString(order,ORDER_COMMENT)!="JPWR7:"+g_supervisor_record.machine.nonce ||
         (ulong)HistoryOrderGetInteger(order,ORDER_MAGIC)!=JPW_SUPERVISOR_MAGIC ||
         HistoryOrderGetString(order,ORDER_SYMBOL)!=g_supervisor_record.machine.active.symbol) continue;
      if(g_supervisor_record.machine.active.kind==JPW_RISK_CLOSE &&
         HistoryOrderGetInteger(order,ORDER_POSITION_ID)!=g_supervisor_record.machine.active.identifier) continue;
      g_supervisor_record.machine.request_order=order; return(true);
     }
   return(false);
  }
// Real cancel-terminal path, shared with the focused synthetic-history host check.
// A terminal order is not proof that its fill has reached the position inventory.
bool JPWSupervisorCancelTerminalOutcome(JPWRiskAction &action,JPWRiskPosition &positions[],
                                         const ulong cycle_started)
  {
   if(OrderSelect(action.ticket) || !HistoryOrderSelect(action.ticket)) return(false);
   long state=0,type=0,identifier=0;
   double initial=0.0,residual=0.0; string symbol="";
   if(!HistoryOrderGetInteger(action.ticket,ORDER_STATE,state) || !JPWSupervisorTerminalOrder(state) ||
      !HistoryOrderGetInteger(action.ticket,ORDER_TYPE,type) ||
      !HistoryOrderGetInteger(action.ticket,ORDER_POSITION_ID,identifier) ||
      !HistoryOrderGetDouble(action.ticket,ORDER_VOLUME_INITIAL,initial) ||
      !HistoryOrderGetDouble(action.ticket,ORDER_VOLUME_CURRENT,residual) ||
      !HistoryOrderGetString(action.ticket,ORDER_SYMBOL,symbol) || symbol!=action.symbol ||
      !JPWRiskEntryType(type) || !JPWFinitePositive(initial) || !MathIsValidNumber(residual) ||
      residual<0.0 || residual>initial) return(false);
   const double filled=(state==ORDER_STATE_FILLED ? initial : initial-residual);
   if(filled>0.0 || identifier>0 || state==ORDER_STATE_FILLED)
     {
      string why="ENTRY_HISTORY_NOT_COMPLETE";
      JPWRiskDealEvidence deals[]; ulong witness=0;
      bool linked=(identifier>0 && filled>0.0 && JPWWithinBudget(cycle_started) &&
                   HistorySelectByPosition(identifier));
      const int count=(linked ? HistoryDealsTotal() : 0);
      // Refuse an incomplete/budget-truncated selection; never advance a cursor
      // and claim a full chain from only the last matching deal.
      if(count<1 || count>2048) linked=false;
      if(linked && ArrayResize(deals,count)!=count) linked=false;
      int accepted=0;
      for(int i=0;linked && i<count;i++)
        {
         if(!JPWWithinBudget(cycle_started)) { linked=false; why="ENTRY_HISTORY_BUDGET_INCOMPLETE"; break; }
         const ulong ticket=HistoryDealGetTicket(i); long deal_type=0;
         if(ticket==0 || !HistoryDealGetInteger(ticket,DEAL_TYPE,deal_type)) { linked=false; break; }
         if(deal_type==DEAL_TYPE_BUY_CANCELED || deal_type==DEAL_TYPE_SELL_CANCELED)
           { linked=false; why="ENTRY_HISTORY_CORRECTION_UNRESOLVED"; break; }
         if(deal_type!=DEAL_TYPE_BUY && deal_type!=DEAL_TYPE_SELL) continue; // Financial costs have no traded volume.
         long order=0,position_id=0,entry=0; double volume=0.0; string deal_symbol="";
         if(!HistoryDealGetInteger(ticket,DEAL_ORDER,order) ||
            !HistoryDealGetInteger(ticket,DEAL_POSITION_ID,position_id) ||
            !HistoryDealGetInteger(ticket,DEAL_ENTRY,entry) ||
            !HistoryDealGetDouble(ticket,DEAL_VOLUME,volume) ||
            !HistoryDealGetString(ticket,DEAL_SYMBOL,deal_symbol)) { linked=false; break; }
         deals[accepted].ticket=ticket; deals[accepted].order_ticket=(ulong)order;
         deals[accepted].position_identifier=position_id; deals[accepted].symbol=deal_symbol;
         deals[accepted].direction=(deal_type==DEAL_TYPE_BUY ? POSITION_TYPE_BUY : POSITION_TYPE_SELL);
         deals[accepted].volume=volume;
         if(entry==DEAL_ENTRY_IN) deals[accepted].entry=JPW_RISK_EVIDENCE_IN;
         else if(entry==DEAL_ENTRY_OUT) deals[accepted].entry=JPW_RISK_EVIDENCE_OUT;
         else if(entry==DEAL_ENTRY_OUT_BY) deals[accepted].entry=JPW_RISK_EVIDENCE_OUT_BY;
         else { linked=false; why="ENTRY_HISTORY_UNSUPPORTED_REVERSAL"; break; }
         if((ulong)order==action.ticket && entry==DEAL_ENTRY_IN) witness=ticket;
         accepted++;
        }
      if(linked && ArrayResize(deals,accepted)!=accepted) linked=false;
      const long direction=(type==ORDER_TYPE_BUY_LIMIT || type==ORDER_TYPE_BUY_STOP ||
         type==ORDER_TYPE_BUY_STOP_LIMIT ? POSITION_TYPE_BUY : POSITION_TYPE_SELL);
      if(linked) linked=JPWRiskEntryFillLinked(action.ticket,identifier,symbol,direction,filled,deals,positions);
      long confirmed_state=0,confirmed_identifier=0; double confirmed_initial=0.0,confirmed_residual=0.0;
      if(linked) linked=(witness>0 && JPWWithinBudget(cycle_started) && !OrderSelect(action.ticket) &&
         HistoryOrderGetInteger(action.ticket,ORDER_STATE,confirmed_state) && confirmed_state==state &&
         HistoryOrderGetInteger(action.ticket,ORDER_POSITION_ID,confirmed_identifier) && confirmed_identifier==identifier &&
         HistoryOrderGetDouble(action.ticket,ORDER_VOLUME_INITIAL,confirmed_initial) && confirmed_initial==initial &&
         HistoryOrderGetDouble(action.ticket,ORDER_VOLUME_CURRENT,confirmed_residual) && confirmed_residual==residual);
      if(!linked)
        {
         g_supervisor_record.machine.protection_incomplete=true;
         g_supervisor_record.view.reason="ACTION_UNKNOWN_CANCEL_FILL_LINK_UNCONFIRMED_"+why;
         return(false);
        }
      // Durable financial witness before releasing the single-flight intention.
      g_supervisor_record.machine.active.identifier=identifier;
      g_supervisor_record.machine.request_order=action.ticket;
      g_supervisor_record.machine.request_deal=witness;
      if(!JPWSupervisorPersist("ENTRY_ORDER_DEALS_POSITION_CHAIN_CONFIRMED","ENTRY_FILL_LINK_CONFIRMED")) return(false);
     }
   g_supervisor_record.machine.request_order=action.ticket;
   if(filled>0.0 || state==ORDER_STATE_FILLED) g_supervisor_record.machine.protection_incomplete=true;
   JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_CONFIRMED,filled);
   return(JPWSupervisorPersist(state==ORDER_STATE_CANCELED ?
      filled>0.0 ? "REMAINDER_REMOVED_LINKED_ENTRY_FILL_REPLAN" : "PENDING_REMOVAL_CONFIRMED" :
      "PENDING_TERMINAL_LINKED_REPLAN_NOT_CANCEL_SUCCESS",
      state==ORDER_STATE_CANCELED ? filled>0.0 ? "PARTIAL_ENTRY_CANCEL_LINKED_RECONCILED" : "CANCEL_RECONCILED" :
      "CANCEL_RACE_OR_OTHER_TERMINAL_LINKED"));
  }
bool JPWSupervisorReconcile(JPWRiskPosition &positions[],const bool stable_current,const ulong cycle_started)
  {
   if(g_supervisor_record.machine.phase!=JPW_RISK_UNKNOWN &&
      g_supervisor_record.machine.phase!=JPW_RISK_REMAINDER) return(true);
   if(!TerminalInfoInteger(TERMINAL_CONNECTED) || !stable_current) return(false);
   if(g_supervisor_reply_pending)
     {
      g_supervisor_record.machine.retcode=g_supervisor_reply.retcode;
      if(g_supervisor_reply.order>0) g_supervisor_record.machine.request_order=g_supervisor_reply.order;
      if(g_supervisor_reply.deal>0) g_supervisor_record.machine.request_deal=g_supervisor_reply.deal;
      g_supervisor_record.machine.request_id=g_supervisor_reply.request_id;
      g_supervisor_reply_pending=false;
     }
   JPWRiskAction action=g_supervisor_record.machine.active;
   if(action.kind==JPW_RISK_CANCEL)
     {
      if(!OrderSelect(action.ticket))
        {
         return(JPWSupervisorCancelTerminalOutcome(action,positions,cycle_started));
        }
      if(JPWSupervisorDefinitiveRefusal(g_supervisor_record.machine.retcode))
        {
         JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_REFUSED,0.0);
         return(JPWSupervisorPersist("CANCEL_REFUSED_CONTINUE_POSITION_PODA_INCOMPLETE","CANCEL_REFUSED"));
        }
      return(false);
     }
   if(action.kind!=JPW_RISK_CLOSE) return(false);
   bool found=false; double residual=0.0;
   for(int i=0;i<ArraySize(positions);i++)
      if(positions[i].identifier==action.identifier)
        {
         if(positions[i].ticket!=action.ticket || positions[i].symbol!=action.symbol || positions[i].direction!=action.direction)
            return(false);
         found=true; residual=positions[i].volume;
        }
   if(JPWSupervisorDefinitiveRefusal(g_supervisor_record.machine.retcode))
     {
      JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_REFUSED,0.0);
      return(JPWSupervisorPersist("CLOSE_REFUSED_PRESERVE_LIFO_REARM_REQUIRED","CLOSE_REFUSED"));
     }
   if(!JPWSupervisorFindRequestOrder()) return(false);
   const ulong order=g_supervisor_record.machine.request_order;
   // An outstanding order can still execute; no new request, even if target currently looks flat.
   if(OrderSelect(order)) return(false);
   if(!HistoryOrderSelect(order)) return(false);
   const long state=HistoryOrderGetInteger(order,ORDER_STATE);
   if(!JPWSupervisorTerminalOrder(state) || HistoryOrderGetInteger(order,ORDER_POSITION_ID)!=action.identifier)
      return(false);
   const double filled=MathMax(0.0,HistoryOrderGetDouble(order,ORDER_VOLUME_INITIAL)-HistoryOrderGetDouble(order,ORDER_VOLUME_CURRENT));
   if(!found)
     {
      JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_CONFIRMED,filled);
      return(JPWSupervisorPersist("TARGET_FLAT_AND_REQUEST_TERMINAL_CONFIRMED","WHOLE_TARGET_FLAT"));
     }
   if(residual<action.volume && filled>0.0)
     {
      JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_PARTIAL,filled);
      return(JPWSupervisorPersist("REQUEST_TERMINAL_FINISH_RECONCILED_RESIDUAL","CLOSE_PARTIAL_TERMINAL"));
     }
   if(state==ORDER_STATE_REJECTED || state==ORDER_STATE_EXPIRED || state==ORDER_STATE_CANCELED)
     {
      JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_REFUSED,filled);
      return(JPWSupervisorPersist("CLOSE_NOT_COMPLETED_PRESERVE_LIFO","CLOSE_TERMINAL_REFUSED"));
     }
   return(false); // DONE without a coherent portfolio change is not completion.
  }

bool JPWSupervisorMakeRequest(JPWRiskAction &action,MqlTradeRequest &request,string &reason)
  {
   ZeroMemory(request); request.magic=JPW_SUPERVISOR_MAGIC;
   request.comment="JPWR7:"+g_supervisor_record.machine.nonce;
   if(action.kind==JPW_RISK_CANCEL)
     { request.action=TRADE_ACTION_REMOVE; request.order=action.ticket; return(true); }
   if(action.kind!=JPW_RISK_CLOSE) return(false);
   MqlTick tick={};
   if(!SymbolInfoTick(action.symbol,tick) || !JPWFinitePositive(tick.bid) || !JPWFinitePositive(tick.ask) ||
      tick.ask<tick.bid || tick.time<=0 || (long)TimeTradeServer()-(long)tick.time>30 || tick.time>TimeTradeServer()+2)
      { reason="EXECUTION_QUOTE_NOT_CURRENT"; return(false); }
   long mode=0,fill=0;
   if(!SymbolInfoInteger(action.symbol,SYMBOL_TRADE_EXEMODE,mode) ||
      !SymbolInfoInteger(action.symbol,SYMBOL_FILLING_MODE,fill)) return(false);
   if((fill&SYMBOL_FILLING_FOK)!=0) request.type_filling=ORDER_FILLING_FOK;
   else if((fill&SYMBOL_FILLING_IOC)!=0) request.type_filling=ORDER_FILLING_IOC;
   else if(mode!=SYMBOL_TRADE_EXECUTION_MARKET) request.type_filling=ORDER_FILLING_RETURN;
   else { reason="NO_SUPPORTED_FILL_POLICY"; return(false); }
   request.action=TRADE_ACTION_DEAL; request.position=action.ticket; request.symbol=action.symbol;
   request.volume=action.volume; request.deviation=InpMaxDeviationPoints;
   request.type=(action.direction==POSITION_TYPE_BUY ? ORDER_TYPE_SELL : ORDER_TYPE_BUY);
   request.price=(request.type==ORDER_TYPE_SELL ? tick.bid : tick.ask);
   // No SL/TP mutation, no reverse/open path, no CloseBy substitution.
   return(true);
  }
void JPWSupervisorSend(JPWRiskSnapshot &sample,JPWRiskAction &action,JPWRiskPosition &positions[],
                      JPWRiskPending &pending[],const ulong cycle_started)
  {
   string why="";
   if(!g_supervisor_record.machine.armed || g_supervisor_lock==INVALID_HANDLE ||
      g_supervisor_store_failed || g_supervisor_context_failed || !sample.current) return;
   if(!JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why))
     {
      g_supervisor_record.machine.armed=false;
      g_supervisor_record.machine.protection_incomplete=true;
      if(g_supervisor_record.machine.phase==JPW_RISK_READY) g_supervisor_record.machine.phase=JPW_RISK_OBSERVE;
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
      g_supervisor_disarm_reason="PERMISSION_LOST_EXPLICIT_REARM_REQUIRED_"+why;
      JPWSupervisorPersist(g_supervisor_disarm_reason,"DISARMED_PERMISSION"); return;
     }
   if(!JPWRiskReselect(action,why))
     {
      g_supervisor_record.machine.protection_incomplete=true;
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
      JPWSupervisorPersist(why); return;
     }
   JPWRiskMachine previous=g_supervisor_record.machine;
   string nonce=""; if(!JPWSupervisorNewToken(nonce) ||
      !JPWRiskBegin(g_supervisor_record.machine,action,nonce,(long)TimeGMT())) return;
   if(!JPWSupervisorPersist("INTENT_DURABLE_BEFORE_SEND","INTENT_PREPARED")) return;
   MqlTradeRequest request={};
   string target=""; double divisor=0.0;
   JPWRiskPosition checked[]; JPWRiskPending checked_pending[];
   // Fresh recheck AFTER the durable write. This is still a client race, not server atomicity.
   if(!JPWWithinBudget(cycle_started) || !JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why) ||
      !JPWRiskReselect(action,why) || !JPWRiskReadRows(checked,checked_pending) ||
      !JPWRiskRowsEqual(positions,pending,checked,checked_pending) ||
      !JPWAccountUnits(g_supervisor_account.currency,target,divisor) ||
      AccountInfoDouble(ACCOUNT_EQUITY)/divisor!=sample.equity || !JPWSupervisorMakeRequest(action,request,why))
     {
      g_supervisor_record.machine=previous; // Positively known NOT SENT; never used after OrderSend.
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
      if(!JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why))
        { g_supervisor_record.machine.armed=false; g_supervisor_disarm_reason="PERMISSION_LOST_EXPLICIT_REARM_REQUIRED_"+why; }
      JPWSupervisorPersist("PRE_SEND_RECHECK_FAILED_NOT_SENT","NOT_SENT_RECAPTURE_REQUIRED"); return;
     }
   MqlTradeCheckResult check={};
   if(!OrderCheck(request,check) || (check.retcode!=0 && check.retcode!=TRADE_RETCODE_DONE))
     {
      g_supervisor_record.machine.retcode=check.retcode;
      // OrderSend was NOT invoked, so this validation refusal is definitive.
      JPWRiskApplyOutcome(g_supervisor_record.machine,JPW_RISK_REFUSED,0.0);
      JPWSupervisorPersist("ORDER_CHECK_REFUSED_NO_SEND","CHECK_REFUSED"); return;
     }
   // OrderCheck is not atomic and may block; recapture the identity/composition after it.
   if(!JPWWithinBudget(cycle_started) || !JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why) ||
      !JPWRiskReselect(action,why) || !JPWRiskReadRows(checked,checked_pending) ||
      !JPWRiskRowsEqual(positions,pending,checked,checked_pending) ||
      AccountInfoDouble(ACCOUNT_EQUITY)/divisor!=sample.equity)
     {
      g_supervisor_record.machine=previous;
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
      if(!JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why))
        { g_supervisor_record.machine.armed=false; g_supervisor_disarm_reason="PERMISSION_LOST_EXPLICIT_REARM_REQUIRED_"+why; }
      JPWSupervisorPersist("POST_CHECK_CHANGED_NOT_SENT","NOT_SENT_RECAPTURE_REQUIRED"); return;
     }
   MqlTradeResult result={};
   // Sole trading entry point. Every caller is guarded by exact demo identity + explicit session arm.
   const bool sent=OrderSend(request,result);
   g_supervisor_record.machine.retcode=result.retcode;
   g_supervisor_record.machine.request_order=result.order;
   g_supervisor_record.machine.request_deal=result.deal;
   g_supervisor_record.machine.request_id=result.request_id;
   g_supervisor_record.machine.executed_volume=result.volume;
   JPWSupervisorPersist(sent ? "REQUEST_ACCEPTED_RECONCILE_NOT_EXECUTION_PROOF" : "SEND_RETURNED_FALSE_RECONCILE",
                        "REQUEST_RETURN");
  }

int OnInit()
  {
   if(!JPWReadAccount(g_supervisor_account)) return(INIT_FAILED);
   string key=""; if(!JPWRiskAccountKey(g_supervisor_account,key)) return(INIT_FAILED);
   FolderCreate("JPWealth",FILE_COMMON); FolderCreate(JPW_RISK_FOLDER,FILE_COMMON);
   g_supervisor_lock=FileOpen(JPW_RISK_FOLDER+key+".lock",FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);
   if(g_supervisor_lock==INVALID_HANDLE)
     { Comment("JPW Supervisor: another local owner or inaccessible lock. No requests."); return(INIT_FAILED); }
   string why=""; const bool loaded=JPWRiskLoadRecord(key,g_supervisor_record,why);
   if(!loaded && why!="ABSENT") { FileClose(g_supervisor_lock); g_supervisor_lock=INVALID_HANDLE; return(INIT_FAILED); }
   if(!loaded)
     {
      ZeroMemory(g_supervisor_record); JPWRiskReset(g_supervisor_record.machine);
      g_supervisor_record.view.schema=JPW_RISK_SCHEMA; g_supervisor_record.view.account_key=key;
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.generation=0;
      // Initial N/A envelope has no prior financial sample. Later persistence never refreshes its age.
      g_supervisor_record.view.observed_utc=(long)TimeGMT();
     }
   const string previous_challenge=g_supervisor_record.view.session_challenge;
   const bool unresolved=(g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN);
   const bool remainder=(g_supervisor_record.machine.phase==JPW_RISK_REMAINDER);
   const bool pending_intent=(unresolved || remainder);
   g_supervisor_record.machine.armed=false;
   if(unresolved) g_supervisor_record.machine.phase=JPW_RISK_UNKNOWN;
   else if(remainder) g_supervisor_record.machine.phase=JPW_RISK_REMAINDER;
   else if(g_supervisor_record.machine.phase!=JPW_RISK_PAUSED_LIFO) g_supervisor_record.machine.phase=JPW_RISK_OBSERVE;
   JPWRiskClearAction(g_supervisor_proposal); g_supervisor_plan_available=false;
   const bool requested=InpArmDemo && previous_challenge!="" && InpDemoSession==previous_challenge;
   if(requested && !unresolved && JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why))
     {
      if(!remainder) { JPWRiskReset(g_supervisor_record.machine); g_supervisor_record.machine.phase=JPW_RISK_READY; }
      // Explicit rearm of a positively reconciled residual preserves its whole-ticket intention.
      // A request whose outcome remains UNKNOWN can never be rearmed or replayed.
      g_supervisor_record.machine.armed=true;
     }
   if(requested && !g_supervisor_record.machine.armed && why!="")
      g_supervisor_disarm_reason="ARM_DENIED_"+why;
   string challenge="";
   if(!JPWSupervisorNewToken(challenge)) return(INIT_FAILED);
   // Consumed/rotated on EVERY initialization. Old inputs cannot automatically arm after restart.
   // OBSERVE -> copying persisted challenge -> changing inputs -> reinit is intentionally supported.
   g_supervisor_record.view.session_challenge=challenge;
   g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
   JPWResetData();
   if(!JPWSupervisorPersist(pending_intent ? "RECOVERY_RECONCILE_NO_AUTOMATIC_ARM" :
      g_supervisor_record.machine.armed ? "EXPLICIT_DEMO_SESSION_ARMED" : "OBSERVE_EXPLICIT_DEMO_SESSION_REQUIRED","SESSION_START"))
      return(INIT_FAILED);
   if(!EventSetTimer(1)) return(INIT_FAILED);
   return(INIT_SUCCEEDED);
  }
void OnTradeTransaction(const MqlTradeTransaction &trans,const MqlTradeRequest &request,const MqlTradeResult &result)
  {
   g_supervisor_dirty=true;
   if(trans.type==TRADE_TRANSACTION_DEAL_UPDATE || trans.type==TRADE_TRANSACTION_DEAL_DELETE ||
      trans.type==TRADE_TRANSACTION_HISTORY_UPDATE || trans.type==TRADE_TRANSACTION_HISTORY_DELETE)
      g_supervisor_correction=true;
   if(trans.type==TRADE_TRANSACTION_REQUEST && g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN &&
      request.comment=="JPWR7:"+g_supervisor_record.machine.nonce && request.magic==JPW_SUPERVISOR_MAGIC)
      { g_supervisor_reply=result; g_supervisor_reply_pending=true; }
   // No file writes, history reads or OrderSend in callbacks. Periodic full scan recovers event loss.
  }
void OnTimer()
  {
   if(g_supervisor_timer_busy || g_supervisor_store_failed || g_supervisor_context_failed) return;
   g_supervisor_timer_busy=true; const ulong started=GetTickCount64();
   JPWRiskClearAction(g_supervisor_proposal); g_supervisor_plan_available=false;
   JPWAccount actual;
   if(!JPWReadAccount(actual) || actual.login!=g_supervisor_account.login || actual.server!=g_supervisor_account.server ||
      actual.currency!=g_supervisor_account.currency)
     {
      g_supervisor_record.machine.armed=false; g_supervisor_record.view.quality="N/A";
      g_supervisor_record.view.pending_projection_valid=false;
      JPWSupervisorPersist("ACCOUNT_CHANGED_RESTART_OBSERVE_REQUIRED","CONTEXT_CHANGED");
      g_supervisor_context_failed=true; g_supervisor_timer_busy=false; return;
     }
   string why="";
   if(g_supervisor_record.machine.armed && !JPWRiskDemoPermissions(g_supervisor_account,InpDemoLogin,InpDemoServer,why))
     {
      g_supervisor_record.machine.armed=false;
      if(g_supervisor_record.machine.phase==JPW_RISK_READY) g_supervisor_record.machine.phase=JPW_RISK_OBSERVE;
      g_supervisor_record.view.quality="N/A"; g_supervisor_record.view.pending_projection_valid=false;
      g_supervisor_disarm_reason="PERMISSION_LOST_EXPLICIT_REARM_REQUIRED_"+why;
      JPWSupervisorPersist(g_supervisor_disarm_reason,"DISARMED_PERMISSION");
      g_supervisor_timer_busy=false; return;
     }
   JPWRiskSnapshot sample; JPWRiskPosition positions[]; JPWRiskPending pending[];
   const bool captured=JPWRiskCollect(g_supervisor_account,sample,positions,pending,why);
   g_supervisor_record.view.quality=(captured && sample.valid ? sample.current ? "Current" : "Estimated" : "N/A");
   g_supervisor_record.view.pending_projection_valid=(captured && sample.pending_valid);
   g_supervisor_record.view.position_count=ArraySize(positions); g_supervisor_record.view.pending_count=ArraySize(pending);
   if(captured && sample.valid)
     {
      // This is the only renewal of an existing financial capture timestamp.
      g_supervisor_record.view.observed_utc=(long)TimeGMT();
      g_supervisor_record.view.gross=sample.gross; g_supervisor_record.view.equity=sample.equity;
      g_supervisor_record.view.leverage=sample.leverage;
      if(sample.pending_valid) g_supervisor_record.view.projected_leverage=sample.projected_leverage;
     }
   const JPWRiskPhase before=g_supervisor_record.machine.phase;
   if(before==JPW_RISK_UNKNOWN || before==JPW_RISK_REMAINDER)
     {
      const bool reconciled=JPWSupervisorReconcile(positions,captured && sample.valid && sample.current,started);
      // An outcome cycle never also submits another action: at most one request per timer.
      if(!reconciled || before==JPW_RISK_UNKNOWN || g_supervisor_record.machine.phase!=JPW_RISK_REMAINDER)
        {
         JPWSupervisorPersist(g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN ?
            (StringFind(g_supervisor_record.view.reason,"ACTION_UNKNOWN_")==0 ?
             g_supervisor_record.view.reason : "ACTION_UNKNOWN_NO_NEW_REQUESTS") : g_supervisor_record.view.reason);
         g_supervisor_timer_busy=false; return;
        }
     }
   JPWRiskAction next; string planned="";
   if(!captured || !JPWRiskPlan(sample,positions,pending,g_supervisor_record.machine,next,planned))
     {
      JPWSupervisorPersist(!captured ? why : planned); g_supervisor_timer_busy=false; return;
     }
   g_supervisor_proposal=next; g_supervisor_plan_available=true;
   if(!JPWSupervisorPersist(planned)) { g_supervisor_timer_busy=false; return; }
   if(next.kind!=JPW_RISK_NONE && g_supervisor_record.machine.armed)
      JPWSupervisorSend(sample,next,positions,pending,started);
   g_supervisor_dirty=false; g_supervisor_correction=false; g_supervisor_timer_busy=false;
  }
void OnDeinit(const int reason)
  {
   EventKillTimer();
   if(g_supervisor_lock!=INVALID_HANDLE)
     {
      g_supervisor_record.machine.armed=false; g_supervisor_record.view.quality="N/A";
      g_supervisor_record.view.pending_projection_valid=false;
      JPWSupervisorPersist("SESSION_STOPPED_OBSERVE_RESTART","SESSION_END");
      FileClose(g_supervisor_lock); g_supervisor_lock=INVALID_HANDLE;
     }
   Comment("");
  }

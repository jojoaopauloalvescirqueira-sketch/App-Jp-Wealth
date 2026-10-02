#ifndef JPW_GENETRIX_LEDGER_TERMINAL_MQH
#define JPW_GENETRIX_LEDGER_TERMINAL_MQH
#include <JPWealth/JPW_Genetrix_Ledger_Store.mqh>
// Read-only adapter. No OrderSend, trade permission changes or attachments.
bool JPWLedgerIdentity(string &key,string &currency)
  {
   key=""; currency=""; ResetLastError();
   long login=AccountInfoInteger(ACCOUNT_LOGIN);
   string server=AccountInfoString(ACCOUNT_SERVER);
   currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   return(GetLastError()==0 && JPWObserverAccountKey(server,login,currency,installation,key));
  }
bool JPWLedgerAccountDouble(const ENUM_ACCOUNT_INFO_DOUBLE property,double &value)
  { ResetLastError(); value=AccountInfoDouble(property); return(GetLastError()==0 && JPWLedgerFinite(value)); }
int JPWLedgerPendingSide(const long type)
  {
   if(type==ORDER_TYPE_BUY_LIMIT || type==ORDER_TYPE_BUY_STOP || type==ORDER_TYPE_BUY_STOP_LIMIT) return(1);
   if(type==ORDER_TYPE_SELL_LIMIT || type==ORDER_TYPE_SELL_STOP || type==ORDER_TYPE_SELL_STOP_LIMIT) return(-1);
   return(0);
  }
bool JPWLedgerReadDeal(const ulong ticket,JPWLedgerDeal &d)
  {
   if(ticket==0 || ticket>(ulong)LONG_MAX) return(false);
   d.ticket=(long)ticket; d.deleted=0;
   long type=0,entry=0,reason=0;
   if(!HistoryDealGetInteger(ticket,DEAL_ORDER,d.order_ticket) ||
      !HistoryDealGetInteger(ticket,DEAL_POSITION_ID,d.position_id) ||
      !HistoryDealGetInteger(ticket,DEAL_TIME_MSC,d.time_msc) ||
      !HistoryDealGetInteger(ticket,DEAL_TYPE,type) ||
      !HistoryDealGetInteger(ticket,DEAL_ENTRY,entry) ||
      !HistoryDealGetInteger(ticket,DEAL_REASON,reason) ||
      !HistoryDealGetString(ticket,DEAL_SYMBOL,d.symbol) ||
      !HistoryDealGetDouble(ticket,DEAL_VOLUME,d.volume) ||
      !HistoryDealGetDouble(ticket,DEAL_PROFIT,d.profit) ||
      !HistoryDealGetDouble(ticket,DEAL_SWAP,d.swap) ||
      !HistoryDealGetDouble(ticket,DEAL_COMMISSION,d.commission) ||
      !HistoryDealGetDouble(ticket,DEAL_FEE,d.fee)) return(false);
   d.entry=(int)entry; d.reason=(reason==DEAL_REASON_ROLLOVER ? 1 : 0); d.side=0; d.adjustment_of=0;
   if(type==DEAL_TYPE_BUY || type==DEAL_TYPE_SELL)
     { d.kind=1; d.side=(type==DEAL_TYPE_BUY ? 1 : -1); }
   else if(type==DEAL_TYPE_BUY_CANCELED || type==DEAL_TYPE_SELL_CANCELED)
     { d.kind=5; d.side=(type==DEAL_TYPE_BUY_CANCELED ? 1 : -1); }
   else if(type==DEAL_TYPE_CREDIT) d.kind=4;
   else if(type==DEAL_TYPE_BALANCE || type==DEAL_TYPE_BONUS) d.kind=3;
   else d.kind=2; // commission, charge, correction, interest/tax/dividend: explicit attribution required
   return(JPWLedgerDealValid(d));
  }
bool JPWLedgerReadOrder(const ulong ticket,const bool historical,JPWLedgerOrder &o,bool &pending)
  {
   pending=false; if(ticket==0 || ticket>(ulong)LONG_MAX) return(false);
   long type=0,state=0;
   if(historical)
     {
      if(!HistoryOrderGetInteger(ticket,ORDER_TYPE,type) || !HistoryOrderGetInteger(ticket,ORDER_STATE,state)) return(false);
     }
   else if(!OrderGetInteger(ORDER_TYPE,type) || !OrderGetInteger(ORDER_STATE,state)) return(false);
   o.side=JPWLedgerPendingSide(type); if(o.side==0) return(true); pending=true;
   o.ticket=(long)ticket; o.done_msc=0;
   if(historical)
     {
      if(!HistoryOrderGetInteger(ticket,ORDER_TIME_SETUP_MSC,o.setup_msc) ||
         !HistoryOrderGetInteger(ticket,ORDER_TIME_DONE_MSC,o.done_msc) ||
         !HistoryOrderGetString(ticket,ORDER_SYMBOL,o.symbol) ||
         !HistoryOrderGetDouble(ticket,ORDER_VOLUME_INITIAL,o.volume)) return(false);
     }
   else
     {
      if(!OrderGetInteger(ORDER_TIME_SETUP_MSC,o.setup_msc) || !OrderGetString(ORDER_SYMBOL,o.symbol) ||
         !OrderGetDouble(ORDER_VOLUME_CURRENT,o.volume)) return(false);
     }
   o.state=4;
   if(state==ORDER_STATE_FILLED) o.state=3;
   else if(state==ORDER_STATE_CANCELED || state==ORDER_STATE_EXPIRED || state==ORDER_STATE_REJECTED) o.state=2;
   else if(!historical && (state==ORDER_STATE_PLACED || state==ORDER_STATE_PARTIAL || state==ORDER_STATE_STARTED ||
                          state==ORDER_STATE_REQUEST_ADD || state==ORDER_STATE_REQUEST_MODIFY || state==ORDER_STATE_REQUEST_CANCEL)) o.state=1;
   return(o.setup_msc>0 && o.symbol!="" && JPWLedgerFinite(o.volume) && o.volume>=0);
  }
bool JPWLedgerReadLive(JPWLedgerPosition &positions[],JPWLedgerOrder &orders[],bool &fresh,string &reason)
  {
   ArrayResize(positions,0); ArrayResize(orders,0); fresh=true; reason="";
   int n=PositionsTotal(),order_n=OrdersTotal();
   if(n<0 || n>512 || order_n<0 || order_n>512 || ArrayResize(positions,n)!=n)
     { reason="Inventário indisponível/excessivo"; return(false); }
   const long server_msc=(long)TimeTradeServer()*1000;
   for(int i=0;i<n;i++)
     {
      ulong ticket=PositionGetTicket(i); long side=0; JPWLedgerPosition p;
      if(ticket==0 || ticket>(ulong)LONG_MAX || !PositionSelectByTicket(ticket) ||
         !PositionGetInteger(POSITION_IDENTIFIER,p.identifier) ||
         !PositionGetInteger(POSITION_TIME_MSC,p.opened_msc) ||
         !PositionGetInteger(POSITION_TYPE,side) || !PositionGetString(POSITION_SYMBOL,p.symbol) ||
         !PositionGetDouble(POSITION_VOLUME,p.volume) || !PositionGetDouble(POSITION_PROFIT,p.profit) ||
         !PositionGetDouble(POSITION_SWAP,p.swap) || p.identifier<=0 || p.opened_msc<=0 ||
         p.symbol=="" || !JPWLedgerFinite(p.volume) || p.volume<=0 ||
         !JPWLedgerFinite(p.profit) || !JPWLedgerFinite(p.swap))
        { reason="Posição monetária incompleta"; return(false); }
      p.ticket=(long)ticket; p.side=(side==POSITION_TYPE_BUY ? 1 : (side==POSITION_TYPE_SELL ? -1 : 0));
      if(p.side==0) return(false);
      MqlTick tick={};
      if(!SymbolInfoTick(p.symbol,tick) || !JPWLedgerTickFresh(server_msc,tick.time_msc)) fresh=false;
      positions[i]=p;
     }
   for(int i=0;i<order_n;i++)
     {
      ulong ticket=OrderGetTicket(i); JPWLedgerOrder o; bool pending=false;
      if(ticket==0 || !OrderSelect(ticket) || !JPWLedgerReadOrder(ticket,false,o,pending))
        { reason="Pendente incompleta"; return(false); }
      if(!pending) continue;
      int size=ArraySize(orders); if(ArrayResize(orders,size+1)!=size+1) return(false); orders[size]=o;
     }
   if(!JPWLedgerCountsStable(n,order_n,PositionsTotal(),OrdersTotal()))
     { ArrayResize(positions,0); ArrayResize(orders,0); fresh=false;
       reason="Inventário mudou durante enumeração"; return(false); }
   return(true);
  }
bool JPWLedgerComposition(JPWLedgerPosition &positions[],JPWLedgerOrder &orders[],
                         const string key,const double balance,const long margin,string &digest)
  {
   string rows[];
   for(int i=0;i<ArraySize(positions);i++)
     {
      int n=ArraySize(rows); ArrayResize(rows,n+1);
      rows[n]="P|"+JPWLedgerInt(positions[i].identifier)+"|"+JPWLedgerInt(positions[i].ticket)+"|"+
         JPWLedgerHex(positions[i].symbol)+"|"+JPWLedgerInt(positions[i].side)+"|"+JPWLedgerNum(positions[i].volume);
     }
   for(int i=0;i<ArraySize(orders);i++) if(orders[i].state==1 || orders[i].state==4)
     {
      int n=ArraySize(rows); ArrayResize(rows,n+1);
      rows[n]="O|"+JPWLedgerInt(orders[i].ticket)+"|"+JPWLedgerHex(orders[i].symbol)+"|"+
         JPWLedgerInt(orders[i].side)+"|"+JPWLedgerNum(orders[i].volume)+"|"+JPWLedgerInt(orders[i].state);
     }
   for(int i=1;i<ArraySize(rows);i++)
     { string value=rows[i]; int j=i-1; while(j>=0 && StringCompare(rows[j],value)>0) { rows[j+1]=rows[j]; j--; } rows[j+1]=value; }
   string raw=key+"|"+JPWLedgerNum(balance)+"|"+JPWLedgerInt(margin);
   for(int i=0;i<ArraySize(rows);i++) raw+="|"+rows[i];
   return(JPWRaizNHash(raw,digest));
  }
// Selection is owned here. No nested HistoryDealSelect destroys its lists.
// Budget failure never publishes an old or partial collector as Current.
bool JPWLedgerCollectTerminal(JPWLedgerDeal &deals[],JPWLedgerOrder &orders[],
                              JPWLedgerPosition &positions[],JPWLedgerView &view,
                              string &composition,string &reason)
  {
   ArrayResize(deals,0); ArrayResize(orders,0); JPWLedgerClearView(view); reason="";
   ulong started=GetTickCount64();
   if(!JPWLedgerIdentity(view.account_key,view.currency) || !JPWLedgerAccountDouble(ACCOUNT_BALANCE,view.balance))
     { reason="Conta/saldo não confirmado"; return(false); }
   ResetLastError(); view.margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(GetLastError()!=0 || view.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { reason="Ledger v1 requer hedging"; return(false); }
   bool first_fresh=false,last_fresh=false; JPWLedgerPosition first[]; JPWLedgerOrder active[];
   if(!JPWLedgerReadLive(first,active,first_fresh,reason)) return(false);
   string first_digest="";
   if(!JPWLedgerComposition(first,active,view.account_key,view.balance,view.margin_mode,first_digest)) return(false);
   datetime end=TimeTradeServer(); if(end<=0) end=TimeCurrent();
   if(end<=0 || !HistorySelect(0,end)) { reason="Seleção histórica indisponível"; return(false); }
   int count=HistoryDealsTotal(),order_count=HistoryOrdersTotal();
   if(count<0 || count>JPW_LEDGER_MAX_RECORDS || order_count<0 || order_count>JPW_LEDGER_MAX_RECORDS)
     { reason="Histórico fora do limite explícito"; return(false); }
   for(int i=0;i<count;i++)
     {
      if(GetTickCount64()-started>1500) { reason="Coleta adiada pelo orçamento"; return(false); }
      JPWLedgerDeal d; ulong ticket=HistoryDealGetTicket(i);
      if(!JPWLedgerReadDeal(ticket,d)) { reason="Campos de deal incompletos"; return(false); }
      int n=ArraySize(deals); if(ArrayResize(deals,n+1)!=n+1) return(false); deals[n]=d;
     }
   for(int i=0;i<order_count;i++)
     {
      if(GetTickCount64()-started>1500) { reason="Coleta adiada pelo orçamento"; return(false); }
      JPWLedgerOrder o; bool pending=false; ulong ticket=HistoryOrderGetTicket(i);
      if(!JPWLedgerReadOrder(ticket,true,o,pending)) { reason="Ordem histórica incompleta"; return(false); }
      if(!pending) continue;
      int n=ArraySize(orders); if(ArrayResize(orders,n+1)!=n+1) return(false); orders[n]=o;
     }
   JPWLedgerOrder last_active[];
   if(!JPWLedgerReadLive(positions,last_active,last_fresh,reason)) return(false);
   string after_key="",after_currency=""; double after_balance=0; long after_margin=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(!JPWLedgerIdentity(after_key,after_currency) || after_key!=view.account_key || after_currency!=view.currency ||
      !JPWLedgerAccountDouble(ACCOUNT_BALANCE,after_balance) || after_balance!=view.balance || after_margin!=view.margin_mode ||
      !JPWLedgerComposition(positions,last_active,after_key,after_balance,after_margin,composition) || composition!=first_digest)
     { reason="Conta/composição mudou durante a captura"; return(false); }
   for(int i=0;i<ArraySize(last_active);i++)
     {
      bool found=false;
      for(int j=0;j<ArraySize(orders);j++) if(orders[j].ticket==last_active[i].ticket)
        { orders[j]=last_active[i]; found=true; break; }
      if(!found) { int n=ArraySize(orders); if(ArrayResize(orders,n+1)!=n+1) return(false); orders[n]=last_active[i]; }
     }
   view.observed_utc=(long)TimeGMT(); view.observed_mono_ms=(long)GetTickCount64();
   view.quality=(TerminalInfoInteger(TERMINAL_CONNECTED)!=0 && first_fresh && last_fresh &&
                 MathAbs((double)((long)TimeTradeServer()-(long)TimeCurrent()))<=30 ? 1 : 2);
   // HistorySelect is a successful query, not evidence that the broker supplied
   // the first execution after flat or every account-billed cost. A future
   // coverage witness must be linked and audited before either flag is raised.
   // No operator declaration is silently treated as an automatic verification.
   view.history_complete=false; view.costs_complete=false; view.healthy=true;
   view.reason="Origem/zeragem e cobertura integral de custos sem evidência vinculada; N/A";
   return(view.observed_utc>0 && view.observed_mono_ms>0);
  }
#endif

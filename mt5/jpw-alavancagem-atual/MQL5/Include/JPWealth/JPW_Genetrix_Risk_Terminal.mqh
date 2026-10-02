#ifndef JPW_GENETRIX_RISK_TERMINAL_MQH
#define JPW_GENETRIX_RISK_TERMINAL_MQH
#include <JPWealth/JPW_Genetrix_Risk_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Terminal.mqh>
#include <JPWealth/JPW_Alavancagem_Profile.mqh>

bool JPWRiskEntryType(const long type)
  { return(type==ORDER_TYPE_BUY_LIMIT || type==ORDER_TYPE_SELL_LIMIT ||
           type==ORDER_TYPE_BUY_STOP || type==ORDER_TYPE_SELL_STOP ||
           type==ORDER_TYPE_BUY_STOP_LIMIT || type==ORDER_TYPE_SELL_STOP_LIMIT); }
bool JPWRiskReadRows(JPWRiskPosition &positions[],JPWRiskPending &pending[])
  {
   ArrayResize(positions,0); ArrayResize(pending,0);
   const int count=PositionsTotal(), orders=OrdersTotal();
   if(count<0 || orders<0 || ArrayResize(positions,count)!=count) return(false);
   for(int i=0;i<count;i++)
     {
      const ulong ticket=PositionGetTicket(i);
      long id=0,opened=0,direction=-1; double volume=0.0; string symbol="";
      if(ticket==0 || !PositionSelectByTicket(ticket) ||
         !PositionGetInteger(POSITION_IDENTIFIER,id) || !PositionGetInteger(POSITION_TIME_MSC,opened) ||
         !PositionGetInteger(POSITION_TYPE,direction) || !PositionGetDouble(POSITION_VOLUME,volume) ||
         !PositionGetString(POSITION_SYMBOL,symbol) || id<=0 || opened<=0 || symbol=="" ||
         !JPWFinitePositive(volume) || (direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL)) return(false);
      positions[i].ticket=ticket; positions[i].identifier=id; positions[i].opened_msc=opened;
      positions[i].symbol=symbol; positions[i].direction=direction; positions[i].volume=volume; positions[i].gross=0.0;
     }
   for(int i=0;i<orders;i++)
     {
      const ulong ticket=OrderGetTicket(i); long type=-1,placed=0;
      double volume=0.0,entry=0.0,trigger=0.0; string symbol="";
      if(ticket==0 || !OrderSelect(ticket) || !OrderGetInteger(ORDER_TYPE,type)) return(false);
      if(!JPWRiskEntryType(type)) continue; // No SL/TP/close request deletion.
      if(!OrderGetInteger(ORDER_TIME_SETUP_MSC,placed) || !OrderGetDouble(ORDER_VOLUME_CURRENT,volume) ||
         !OrderGetDouble(ORDER_PRICE_OPEN,trigger) || !OrderGetString(ORDER_SYMBOL,symbol)) return(false);
      entry=trigger;
      if((type==ORDER_TYPE_BUY_STOP_LIMIT || type==ORDER_TYPE_SELL_STOP_LIMIT) &&
         !OrderGetDouble(ORDER_PRICE_STOPLIMIT,entry)) return(false);
      if(placed<=0 || symbol=="" || !JPWFinitePositive(volume) || !JPWFinitePositive(entry) ||
         !JPWFinitePositive(trigger)) return(false);
      const int n=ArraySize(pending); if(ArrayResize(pending,n+1)!=n+1) return(false);
      pending[n].ticket=ticket; pending[n].setup_msc=placed; pending[n].symbol=symbol;
      pending[n].type=type; pending[n].volume=volume; pending[n].entry=entry;
      pending[n].trigger=trigger; pending[n].gross=0.0;
     }
   return(count==PositionsTotal() && orders==OrdersTotal());
  }
bool JPWRiskRowsEqual(JPWRiskPosition &a[],JPWRiskPending &pa[],JPWRiskPosition &b[],JPWRiskPending &pb[])
  {
   if(ArraySize(a)!=ArraySize(b) || ArraySize(pa)!=ArraySize(pb)) return(false);
   for(int i=0;i<ArraySize(a);i++)
     {
      bool found=false;
      for(int j=0;j<ArraySize(b);j++)
         if(a[i].ticket==b[j].ticket && a[i].identifier==b[j].identifier && a[i].opened_msc==b[j].opened_msc &&
            a[i].symbol==b[j].symbol && a[i].direction==b[j].direction && a[i].volume==b[j].volume) found=true;
      if(!found) return(false);
     }
   for(int i=0;i<ArraySize(pa);i++)
     {
      bool found=false;
      for(int j=0;j<ArraySize(pb);j++)
         if(pa[i].ticket==pb[j].ticket && pa[i].setup_msc==pb[j].setup_msc && pa[i].symbol==pb[j].symbol &&
            pa[i].type==pb[j].type && pa[i].volume==pb[j].volume && pa[i].entry==pb[j].entry &&
            pa[i].trigger==pb[j].trigger) found=true;
      if(!found) return(false);
     }
   return(true);
  }
bool JPWRiskSameSpec(JPWInstrument &a,JPWInstrument &b)
  { return(a.symbol==b.symbol && a.calc_mode==b.calc_mode && a.base==b.base &&
           a.profit==b.profit && a.contract_size==b.contract_size && a.underlying_verified==b.underlying_verified); }
bool JPWRiskOneGross(JPWAccount &account,JPWPosition &row,const double entry,JPWQuote &quotes[],
                     JPWProfileEntry &profile[],const string target,const bool usc,const long now_ms,
                     const ulong started,const bool clock_valid,const bool connected,
                     double &gross,bool &estimated)
  {
   gross=0.0;
   if(!JPWWithinBudget(started)) return(false);
   JPWInstrument one[],later; JPWPosition rows[]; double scales[];
   ArrayResize(one,1); ArrayResize(rows,1); ArrayResize(scales,1); rows[0]=row;
   if(!JPWReadSpecification(row.symbol,one[0])) return(false);
   JPW_MODEL model=JPW_MODEL_NONE; if(JPWClassify(one[0],model)!=JPW_OK) return(false);
   scales[0]=1.0;
   if(usc && !JPWProfileFind(one[0],profile,scales[0])) return(false);
   if(!JPWCaptureQuote(row.symbol,one[0].base,one[0].profit,quotes,model==JPW_MODEL_FIAT_FOREX)) return(false);
   const string source=(model==JPW_MODEL_FIAT_FOREX ? one[0].base : one[0].profit);
   if(!JPWPreparedRoute(source,target,quotes,now_ms,started,clock_valid,connected,30)) return(false);
   if(entry>0.0 && model==JPW_MODEL_FIAT_FOREX && one[0].base!=target && one[0].profit!=target &&
      !JPWPreparedRoute(one[0].profit,target,quotes,now_ms,started,clock_valid,connected,30)) return(false);
   if(usc && (!JPWPreparedRoute(one[0].profit,"USD",quotes,now_ms,started,clock_valid,connected,30) ||
      !JPWProfileTickConsistent(one[0],scales[0],account,quotes,now_ms,clock_valid,connected))) return(false);
   if(!JPWReadSpecification(row.symbol,later) || !JPWRiskSameSpec(one[0],later)) return(false);
   if(entry>0.0)
     {
      if(!JPWRiskGrossAtEntry(row,one[0],quotes,target,entry,scales[0],now_ms,clock_valid,connected,
                              g_routes,gross,estimated)) return(false);
      if(ArraySize(g_unsynchronized_symbols)>0) estimated=true;
      return(JPWWithinBudget(started));
     }
   JPWQuote scenario[];
   if(ArrayResize(scenario,ArraySize(quotes))!=ArraySize(quotes)) return(false);
   for(int q=0;q<ArraySize(quotes);q++) scenario[q]=quotes[q];
   if(entry>0.0 && model==JPW_MODEL_LINEAR)
     {
      const int own=JPWQuoteIndex(scenario,row.symbol); if(own<0) return(false);
      // Conditional entry-price scenario; current FX rates and equity remain frozen.
      scenario[own].bid=entry; scenario[own].ask=entry;
     }
   bool row_estimated=false; long oldest=0;
   if(JPWGrossReading(rows,one,scenario,target,now_ms,30,clock_valid,connected,scales,g_routes,
                      gross,row_estimated,oldest)!=JPW_OK) return(false);
   if(row_estimated || ArraySize(g_unsynchronized_symbols)>0) estimated=true;
   return(JPWWithinBudget(started));
  }
bool JPWRiskCollect(JPWAccount &account,JPWRiskSnapshot &sample,JPWRiskPosition &positions[],
                    JPWRiskPending &pending[],string &reason)
  {
   sample.valid=false; sample.current=false; sample.pending_valid=false;
   sample.hedging=(AccountInfoInteger(ACCOUNT_MARGIN_MODE)==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
   sample.fifo=(AccountInfoInteger(ACCOUNT_FIFO_CLOSE)!=0); sample.observed_utc=(long)TimeGMT();
   sample.gross=0.0; sample.pending_gross=0.0; sample.leverage=0.0; sample.projected_leverage=0.0;
   JPWAccount identity; if(!JPWReadAccount(identity) || identity.login!=account.login ||
      identity.server!=account.server || identity.currency!=account.currency)
      { reason="ACCOUNT_IDENTITY_CHANGED"; return(false); }
   const bool connected=(TerminalInfoInteger(TERMINAL_CONNECTED)!=0);
   const ulong started=GetTickCount64(); long now_ms=0;
   const bool clock_valid=connected && JPWClockObserve(g_clock,(long)TimeCurrent(),(long)TimeTradeServer(),started,30,now_ms);
   string target=""; double divisor=0.0;
   if(!JPWAccountUnits(account.currency,target,divisor)) { reason="UNSUPPORTED_ACCOUNT_UNITS"; return(false); }
   ResetLastError(); const double raw_equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(GetLastError()!=0 || !JPWFinitePositive(raw_equity)) { reason="INVALID_EQUITY"; return(false); }
   sample.equity=raw_equity/divisor;
   if(!JPWPrepareCatalog()) { reason="CATALOG_NOT_READY"; return(false); }
   if(!JPWRiskReadRows(positions,pending)) { reason="ROWS_UNSTABLE"; return(false); }
   JPWProfileEntry profile[];
   const bool usc=(account.currency=="USC");
   if(usc && !JPWProfileLoad(account,profile)) { reason="USC_CONTRACT_PROFILE_UNVERIFIED"; return(false); }
   g_quotes_pending=false; g_budget_exceeded=false; ArrayResize(g_unsynchronized_symbols,0);
   JPWQuote quotes[]; bool estimated=(!connected || !clock_valid);
   for(int i=0;i<ArraySize(positions);i++)
     {
      JPWPosition row; row.ticket=positions[i].ticket; row.identifier=positions[i].identifier;
      row.symbol=positions[i].symbol; row.direction=positions[i].direction; row.volume=positions[i].volume;
      if(!JPWRiskOneGross(account,row,0.0,quotes,profile,target,usc,now_ms,started,clock_valid,connected,
                          positions[i].gross,estimated)) { reason="OPEN_NOTIONAL_NA"; return(false); }
      sample.gross+=positions[i].gross;
     }
   if(JPWLeverage(sample.gross,sample.equity,sample.leverage)!=JPW_OK) { reason="OPEN_LEVERAGE_NA"; return(false); }
   sample.valid=true; sample.pending_valid=true;
   for(int i=0;i<ArraySize(pending);i++)
     {
      JPWPosition row; row.ticket=pending[i].ticket; row.identifier=(long)pending[i].ticket;
      row.symbol=pending[i].symbol; row.volume=pending[i].volume;
      row.direction=(pending[i].type==ORDER_TYPE_BUY_LIMIT || pending[i].type==ORDER_TYPE_BUY_STOP ||
         pending[i].type==ORDER_TYPE_BUY_STOP_LIMIT ? POSITION_TYPE_BUY : POSITION_TYPE_SELL);
      if(!JPWRiskOneGross(account,row,pending[i].entry,quotes,profile,target,usc,now_ms,started,clock_valid,connected,
                          pending[i].gross,estimated)) { sample.pending_valid=false; reason="PENDING_NOTIONAL_NA"; break; }
      sample.pending_gross+=pending[i].gross;
     }
   JPWRiskPosition again[]; JPWRiskPending pa[]; JPWAccount later;
   ResetLastError(); const double ending_equity=AccountInfoDouble(ACCOUNT_EQUITY);
   if(GetLastError()!=0 || ending_equity!=raw_equity || !JPWReadAccount(later) || later.login!=account.login ||
      later.server!=account.server || later.currency!=account.currency || !JPWRiskReadRows(again,pa) ||
      !JPWRiskRowsEqual(positions,pending,again,pa) || !JPWWithinBudget(started))
      { sample.valid=false; sample.pending_valid=false; reason="SNAPSHOT_CHANGED_OR_BUDGET"; return(false); }
   sample.current=(!estimated && !g_quotes_pending && connected && clock_valid);
   if(sample.pending_valid && JPWLeverage(sample.gross+sample.pending_gross,sample.equity,sample.projected_leverage)!=JPW_OK)
      { sample.pending_valid=false; reason="PENDING_AGGREGATE_NA"; }
   if(sample.pending_valid) reason=(sample.current ? "CURRENT_STATIC_ENTRY_PROJECTION" : "ESTIMATED_NO_EXECUTION");
   return(true);
  }

bool JPWRiskDemoPermissions(JPWAccount &account,const long authorized_login,const string authorized_server,string &reason)
  {
   if(AccountInfoInteger(ACCOUNT_TRADE_MODE)!=ACCOUNT_TRADE_MODE_DEMO)
      { reason="REAL_ACCOUNT_HARD_EXCLUDED"; return(false); }
   JPWAccount now;
   if(!JPWReadAccount(now) || now.login!=account.login || now.server!=account.server || now.currency!=account.currency ||
      authorized_login!=now.login || authorized_server!=now.server)
      { reason="EXACT_DEMO_IDENTITY_REQUIRED"; return(false); }
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE)!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING || AccountInfoInteger(ACCOUNT_FIFO_CLOSE)!=0)
      { reason="HEDGING_NON_FIFO_REQUIRED"; return(false); }
   if(!TerminalInfoInteger(TERMINAL_CONNECTED) || !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) ||
      !MQLInfoInteger(MQL_TRADE_ALLOWED) || !AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) ||
      !AccountInfoInteger(ACCOUNT_TRADE_EXPERT)) { reason="TRADING_PERMISSION_OR_CONNECTION_DENIED"; return(false); }
   return(true);
  }
bool JPWRiskReselect(JPWRiskAction &action,string &reason)
  {
   if(action.kind==JPW_RISK_CANCEL)
     {
      if(!OrderSelect(action.ticket) || !JPWRiskEntryType(OrderGetInteger(ORDER_TYPE)) ||
         OrderGetString(ORDER_SYMBOL)!=action.symbol || OrderGetDouble(ORDER_VOLUME_CURRENT)!=action.volume)
         { reason="CANCEL_TARGET_CHANGED_RECAPTURE"; return(false); }
      return(true);
     }
   if(action.kind!=JPW_RISK_CLOSE || !PositionSelectByTicket(action.ticket) ||
      PositionGetInteger(POSITION_IDENTIFIER)!=action.identifier || PositionGetString(POSITION_SYMBOL)!=action.symbol ||
      PositionGetInteger(POSITION_TYPE)!=action.direction || PositionGetDouble(POSITION_VOLUME)!=action.volume)
      { reason="EXACT_POSITION_CHANGED_RECAPTURE"; return(false); }
   double minimum=0.0,maximum=0.0,step=0.0;
   if(!SymbolInfoDouble(action.symbol,SYMBOL_VOLUME_MIN,minimum) || !SymbolInfoDouble(action.symbol,SYMBOL_VOLUME_MAX,maximum) ||
      !SymbolInfoDouble(action.symbol,SYMBOL_VOLUME_STEP,step) || !JPWFinitePositive(minimum) ||
      !JPWFinitePositive(maximum) || !JPWFinitePositive(step) || action.volume<minimum || action.volume>maximum ||
      MathAbs(action.volume/step-MathRound(action.volume/step))>1e-8)
      { reason="WHOLE_VOLUME_NOT_REQUESTABLE_NO_PARTIAL_PLAN"; return(false); }
   return(true);
  }
#endif

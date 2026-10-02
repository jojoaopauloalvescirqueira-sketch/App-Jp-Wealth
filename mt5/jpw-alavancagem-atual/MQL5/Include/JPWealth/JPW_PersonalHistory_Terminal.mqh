#ifndef JPW_PERSONAL_HISTORY_TERMINAL_MQH
#define JPW_PERSONAL_HISTORY_TERMINAL_MQH
#include <JPWealth/JPW_PersonalHistory_Core.mqh>
#include <JPWealth/JPW_Genetrix_Risk_Terminal.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>
#include <JPWealth/JPW_Alavancagem_Version.mqh>
// Read-only terminal adapter. Capture is incremental; SL evidence does not
// depend on a USC profile, a conversion, or financial metric availability.
#define JPW_PERSONAL_CAPTURE_LIMIT 1024
#define JPW_PERSONAL_CAPTURE_SLICE 256
#define JPW_PERSONAL_CAPTURE_TIMEOUT_MS 30000
struct JPWPersonalTerminalMeta
  { bool price_valid; bool tp_valid; long opened_msc; long updated_msc;
    double current_price; bool current_valid; double stoplimit_price; bool stoplimit_valid; string specification; double contribution;
    bool contribution_valid; };
int g_ph_capture_phase=0,g_ph_capture_cursor=0,g_ph_position_count=0,g_ph_order_count=0;
JPWAccount g_ph_capture_account;
JPWPersonalCapture g_ph_capture;
JPWPersonalSubject g_ph_first[],g_ph_check[];
JPWPersonalTerminalMeta g_ph_meta[];
bool g_ph_money_valid[7];
JPWProfileEntry g_ph_profile[];
JPWQuote g_ph_quotes[];
string g_ph_target="",g_ph_metric_reason="";
double g_ph_divisor=0.0;
long g_ph_quote_now=0;
ulong g_ph_capture_started=0;
bool g_ph_clock_valid=false,g_ph_estimated=false,g_ph_math_valid=false;

string JPWPersonalTicketText(const ulong ticket) { return(StringFormat("%I64u",ticket)); }
bool JPWPersonalTerminalTicket(const string text,ulong &ticket)
  {
   ticket=0; if(!JPWPersonalDigits(text)) return(false);
   const ulong maximum=(ulong)-1;
   for(int i=0;i<StringLen(text);i++)
     { ulong digit=(ulong)(StringGetCharacter(text,i)-'0');
       if(ticket>(maximum-digit)/10) return(false); ticket=ticket*10+digit; }
   return(ticket>0);
  }
bool JPWPersonalTerminalIdentity(string &key,string &currency)
  {
   key=""; currency=""; ResetLastError();
   const long login=AccountInfoInteger(ACCOUNT_LOGIN);
   const string server=AccountInfoString(ACCOUNT_SERVER);
   currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   return(GetLastError()==0 && JPWObserverAccountKey(server,login,currency,installation,key));
  }
void JPWPersonalTerminalReset()
  {
   g_ph_capture_phase=0; g_ph_capture_cursor=0;
   ArrayResize(g_ph_first,0); ArrayResize(g_ph_check,0); ArrayResize(g_ph_meta,0);
   ArrayResize(g_ph_profile,0); ArrayResize(g_ph_quotes,0);
  }
bool JPWPersonalTerminalMoney(const ENUM_ACCOUNT_INFO_DOUBLE property,double &value)
  { ResetLastError(); value=AccountInfoDouble(property);
    return(GetLastError()==0 && JPWPersonalFinite(value)); }
string JPWPersonalTerminalOptional(const double value,const bool valid)
  { return(valid && JPWPersonalFinite(value) ? JPWPersonalNum(value) : "null"); }
bool JPWPersonalTerminalPosition(const int index,JPWPersonalSubject &s,JPWPersonalTerminalMeta &meta)
  {
   const ulong ticket=PositionGetTicket(index); long identifier=0,side=-1;
   s.kind=JPW_PERSONAL_POSITION; s.ticket=JPWPersonalTicketText(ticket); s.order_type=-1;
   s.sl=0; s.tp=0; s.price=0; s.link_id=""; s.terminal_reason="";
   meta.specification="null"; meta.contribution=0; meta.contribution_valid=false;
   meta.current_price=0; meta.current_valid=false; meta.stoplimit_price=0; meta.stoplimit_valid=false; meta.opened_msc=0; meta.updated_msc=0;
   if(ticket==0 || !PositionSelectByTicket(ticket) ||
      !PositionGetInteger(POSITION_IDENTIFIER,identifier) || identifier<=0 ||
      !PositionGetInteger(POSITION_TYPE,side) ||
      !PositionGetString(POSITION_SYMBOL,s.symbol) || s.symbol=="" ||
      !PositionGetDouble(POSITION_VOLUME,s.volume) || !JPWFinitePositive(s.volume) ||
      (side!=POSITION_TYPE_BUY && side!=POSITION_TYPE_SELL)) return(false);
   s.id=JPWPersonalInt(identifier); s.side=(side==POSITION_TYPE_BUY ? 1 : -1);
   meta.price_valid=PositionGetDouble(POSITION_PRICE_OPEN,s.price) && JPWFinitePositive(s.price);
   if(!meta.price_valid) s.price=0;
   s.sl_readable=PositionGetDouble(POSITION_SL,s.sl) && JPWPersonalFinite(s.sl) && s.sl>=0;
   if(!s.sl_readable) s.sl=0; // This zero is never treated as evidence: sl_readable=false.
   meta.tp_valid=PositionGetDouble(POSITION_TP,s.tp) && JPWPersonalFinite(s.tp) && s.tp>=0;
   if(!meta.tp_valid) s.tp=0;
   meta.current_valid=PositionGetDouble(POSITION_PRICE_CURRENT,meta.current_price) && JPWFinitePositive(meta.current_price);
   PositionGetInteger(POSITION_TIME_MSC,meta.opened_msc);
   PositionGetInteger(POSITION_TIME_UPDATE_MSC,meta.updated_msc);
   return(true);
  }
bool JPWPersonalTerminalPending(const int index,JPWPersonalSubject &s,JPWPersonalTerminalMeta &meta,bool &included)
  {
   included=false; const ulong ticket=OrderGetTicket(index); long type=-1;
   if(ticket==0 || !OrderSelect(ticket) || !OrderGetInteger(ORDER_TYPE,type)) return(false);
   if(!JPWRiskEntryType(type)) return(true);
   included=true; s.kind=JPW_PERSONAL_PENDING; s.id=JPWPersonalTicketText(ticket); s.ticket=s.id;
   s.order_type=(int)type;
   s.side=(type==ORDER_TYPE_BUY_LIMIT || type==ORDER_TYPE_BUY_STOP || type==ORDER_TYPE_BUY_STOP_LIMIT ? 1 : -1);
   s.price=0; s.sl=0; s.tp=0; s.link_id=""; s.terminal_reason="";
   meta.specification="null"; meta.contribution=0; meta.contribution_valid=false;
   meta.current_price=0; meta.current_valid=false; meta.stoplimit_price=0; meta.stoplimit_valid=false; meta.opened_msc=0; meta.updated_msc=0;
   if(!OrderGetString(ORDER_SYMBOL,s.symbol) || s.symbol=="" ||
      !OrderGetDouble(ORDER_VOLUME_CURRENT,s.volume) || !JPWFinitePositive(s.volume)) return(false);
   meta.price_valid=OrderGetDouble(ORDER_PRICE_OPEN,s.price) && JPWFinitePositive(s.price);
   if(!meta.price_valid) s.price=0;
   s.sl_readable=OrderGetDouble(ORDER_SL,s.sl) && JPWPersonalFinite(s.sl) && s.sl>=0;
   if(!s.sl_readable) s.sl=0;
   meta.tp_valid=OrderGetDouble(ORDER_TP,s.tp) && JPWPersonalFinite(s.tp) && s.tp>=0;
   if(!meta.tp_valid) s.tp=0;
   OrderGetInteger(ORDER_TIME_SETUP_MSC,meta.opened_msc);
   if(type==ORDER_TYPE_BUY_STOP_LIMIT || type==ORDER_TYPE_SELL_STOP_LIMIT)
      meta.stoplimit_valid=OrderGetDouble(ORDER_PRICE_STOPLIMIT,meta.stoplimit_price) && JPWFinitePositive(meta.stoplimit_price);
   long position_id=0;
   if(OrderGetInteger(ORDER_POSITION_ID,position_id) && position_id>0)
     { s.link_id="position:"+JPWPersonalInt(position_id); s.terminal_reason="LIVE_ORDER_POSITION_ID"; }
   return(true);
  }
bool JPWPersonalTerminalAppend(JPWPersonalSubject &target[],JPWPersonalSubject &s,
                              JPWPersonalTerminalMeta &meta,const bool first)
  {
   const int size=ArraySize(target);
   if(size>=JPW_PERSONAL_CAPTURE_LIMIT || ArrayResize(target,size+1)!=size+1) return(false);
   target[size]=s;
   if(first)
     { if(ArrayResize(g_ph_meta,size+1)!=size+1) return(false); g_ph_meta[size]=meta; }
   return(true);
  }
string JPWPersonalTerminalFingerprint(JPWPersonalSubject &s)
  { return(JPWPersonalSubjectKey(s)+"|"+s.ticket+"|"+JPWPersonalHex(s.symbol)+"|"+
      JPWPersonalInt(s.side)+"|"+JPWPersonalInt(s.order_type)+"|"+JPWPersonalNum(s.volume)+"|"+
      JPWPersonalNum(s.price)+"|"+JPWPersonalInt(s.sl_readable)+"|"+JPWPersonalNum(s.sl)+"|"+JPWPersonalNum(s.tp)); }
void JPWPersonalTerminalSortStrings(string &rows[],const int left,const int right)
  {
   int i=left,j=right; const string pivot=rows[(left+right)/2];
   while(i<=j)
     {
      while(StringCompare(rows[i],pivot)<0) i++;
      while(StringCompare(rows[j],pivot)>0) j--;
      if(i<=j) { string old=rows[i]; rows[i]=rows[j]; rows[j]=old; i++; j--; }
     }
   if(left<j) JPWPersonalTerminalSortStrings(rows,left,j);
   if(i<right) JPWPersonalTerminalSortStrings(rows,i,right);
  }
bool JPWPersonalTerminalInventoriesEqual()
  {
   const int size=ArraySize(g_ph_first); if(size!=ArraySize(g_ph_check)) return(false);
   string first[],check[],identities[];
   if(ArrayResize(first,size)!=size || ArrayResize(check,size)!=size || ArrayResize(identities,size)!=size) return(false);
   for(int i=0;i<size;i++)
     { first[i]=JPWPersonalTerminalFingerprint(g_ph_first[i]); check[i]=JPWPersonalTerminalFingerprint(g_ph_check[i]);
       identities[i]=JPWPersonalSubjectKey(g_ph_first[i]); }
   if(size>1) { JPWPersonalTerminalSortStrings(first,0,size-1); JPWPersonalTerminalSortStrings(check,0,size-1); JPWPersonalTerminalSortStrings(identities,0,size-1); }
   for(int i=0;i<size;i++) if(first[i]!=check[i] || (i>0 && identities[i]==identities[i-1])) return(false);
   return(true);
  }
bool JPWPersonalTerminalBegin(const string expected,string &reason)
  {
   JPWPersonalTerminalReset(); string key="",currency="";
   if(!JPWPersonalTerminalIdentity(key,currency) || key!=expected || !JPWReadAccount(g_ph_capture_account))
     { reason="ACCOUNT_IDENTITY_UNAVAILABLE_OR_CHANGED"; return(false); }
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) { reason="DISCONNECTED"; return(false); }
   g_ph_position_count=PositionsTotal(); g_ph_order_count=OrdersTotal();
   if(g_ph_position_count<0 || g_ph_order_count<0 || g_ph_position_count+g_ph_order_count>JPW_PERSONAL_CAPTURE_LIMIT)
     { reason="INVENTORY_EXCESSIVE_OR_UNAVAILABLE"; return(false); }
   g_ph_capture.account_key=key; g_ph_capture.units=currency;
   g_ph_capture.source="MT5_PERSONAL_HISTORY_OBSERVER_FORWARD_CAPTURE";
   g_ph_capture.product_version=JPW_PRODUCT_VERSION;
   g_ph_capture.wall_seconds=(long)TimeGMT(); g_ph_capture.started_msc=g_ph_capture.wall_seconds*1000;
   g_ph_capture.finished_msc=g_ph_capture.started_msc; g_ph_capture.mono_ms=GetTickCount64();
   g_ph_capture.stable=false; g_ph_capture.connected=true; g_ph_capture.inventory_valid=false;
   g_ph_capture.quality=JPW_PERSONAL_UNAVAILABLE; g_ph_capture.leverage_valid=false; g_ph_capture.gross=0;
   g_ph_money_valid[0]=JPWPersonalTerminalMoney(ACCOUNT_BALANCE,g_ph_capture.balance);
   g_ph_money_valid[1]=JPWPersonalTerminalMoney(ACCOUNT_EQUITY,g_ph_capture.equity);
   g_ph_money_valid[2]=JPWPersonalTerminalMoney(ACCOUNT_CREDIT,g_ph_capture.credit);
   g_ph_money_valid[3]=JPWPersonalTerminalMoney(ACCOUNT_PROFIT,g_ph_capture.profit);
   g_ph_money_valid[4]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN,g_ph_capture.margin);
   g_ph_money_valid[5]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN_FREE,g_ph_capture.free_margin);
   g_ph_money_valid[6]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN_LEVEL,g_ph_capture.margin_level);
   // Nonfinite optional values never enter the encoded capture as NaN/Infinity.
   if(!g_ph_money_valid[0]) g_ph_capture.balance=0; if(!g_ph_money_valid[1]) g_ph_capture.equity=0;
   if(!g_ph_money_valid[2]) g_ph_capture.credit=0; if(!g_ph_money_valid[3]) g_ph_capture.profit=0;
   if(!g_ph_money_valid[4]) g_ph_capture.margin=0; if(!g_ph_money_valid[5]) g_ph_capture.free_margin=0;
   if(!g_ph_money_valid[6]) g_ph_capture.margin_level=0;
   g_ph_capture_started=GetTickCount64(); g_ph_capture_cursor=0; g_ph_capture_phase=1;
   g_ph_math_valid=false; g_ph_metric_reason="NOT_COLLECTED";
   return(true);
  }
void JPWPersonalTerminalPrepareMath()
  {
   g_ph_math_valid=g_ph_money_valid[1] && g_ph_capture.equity>0;
   g_ph_estimated=false; g_ph_divisor=0; g_ph_target=""; g_ph_quote_now=0;
   g_ph_clock_valid=JPWClockObserve(g_clock,(long)TimeCurrent(),(long)TimeTradeServer(),GetTickCount64(),30,g_ph_quote_now);
   g_ph_estimated=(g_ph_position_count>0 && !g_ph_clock_valid);
   if(!JPWAccountUnits(g_ph_capture.units,g_ph_target,g_ph_divisor))
     { g_ph_math_valid=false; g_ph_metric_reason="UNSUPPORTED_ACCOUNT_UNITS"; }
   else if(!g_ph_money_valid[1] || g_ph_capture.equity<=0)
     { g_ph_math_valid=false; g_ph_metric_reason="INVALID_EQUITY"; }
   else if(!JPWPrepareCatalog() && g_ph_position_count>0)
     { g_ph_math_valid=false; g_ph_metric_reason="CATALOG_NOT_READY"; }
   else if(g_ph_capture.units=="USC" && g_ph_position_count>0 && !JPWProfileLoad(g_ph_capture_account,g_ph_profile))
     { g_ph_math_valid=false; g_ph_metric_reason="USC_CONTRACT_PROFILE_UNVERIFIED"; }
   else g_ph_metric_reason="";
   g_quotes_pending=false; g_budget_exceeded=false; ArrayResize(g_unsynchronized_symbols,0);
  }
void JPWPersonalTerminalRowMath(const int index,const ulong timer_started)
  {
   JPWPosition row; ulong ticket=0; JPWPersonalTerminalTicket(g_ph_first[index].ticket,ticket);
   row.ticket=ticket; row.identifier=StringToInteger(g_ph_first[index].id); row.symbol=g_ph_first[index].symbol;
   row.direction=(g_ph_first[index].side==1 ? POSITION_TYPE_BUY : POSITION_TYPE_SELL); row.volume=g_ph_first[index].volume;
   JPWInstrument specification;
   if(JPWReadSpecification(row.symbol,specification))
     g_ph_meta[index].specification="{\"calc_mode\":"+JPWPersonalInt(specification.calc_mode)+
       ",\"base\":"+JPWPersonalJSON(specification.base)+",\"profit\":"+JPWPersonalJSON(specification.profit)+
       ",\"contract_size\":"+JPWPersonalTerminalOptional(specification.contract_size,JPWFinitePositive(specification.contract_size))+
       ",\"contract_size_valid\":"+(JPWFinitePositive(specification.contract_size) ? "true" : "false")+",\"underlying_verified\":"+
       (specification.underlying_verified ? "true" : "false")+"}";
   if(g_ph_first[index].kind!=JPW_PERSONAL_POSITION || !g_ph_math_valid) return;
   double gross=0;
   if(!JPWRiskOneGross(g_ph_capture_account,row,0,g_ph_quotes,g_ph_profile,g_ph_target,g_ph_capture.units=="USC",
      g_ph_quote_now,timer_started,g_ph_clock_valid,true,gross,g_ph_estimated))
     { g_ph_math_valid=false; g_ph_metric_reason="OPEN_NOTIONAL_UNAVAILABLE"; return; }
   gross*=g_ph_divisor; // Core works in normalized fiat; persist in original account units.
   if(!JPWPersonalFinite(gross) || gross<0)
     { g_ph_math_valid=false; g_ph_metric_reason="NONFINITE_NOTIONAL"; return; }
   g_ph_meta[index].contribution=gross; g_ph_meta[index].contribution_valid=true; g_ph_capture.gross+=gross;
   if(!JPWPersonalFinite(g_ph_capture.gross))
     { g_ph_math_valid=false; g_ph_metric_reason="NONFINITE_AGGREGATE_NOTIONAL"; g_ph_capture.gross=0; }
  }
string JPWPersonalTerminalDetails()
  {
   string rows="[";
   for(int i=0;i<ArraySize(g_ph_first);i++)
     {
      JPWPersonalSubject s=g_ph_first[i]; JPWPersonalTerminalMeta m=g_ph_meta[i];
      if(i>0) rows+=",";
      rows+="{\"kind\":"+JPWPersonalInt(s.kind)+",\"identifier\":"+JPWPersonalJSON(s.id)+
       ",\"ticket\":"+JPWPersonalJSON(s.ticket)+",\"symbol\":"+JPWPersonalJSON(s.symbol)+
       ",\"side\":"+JPWPersonalInt(s.side)+",\"order_type\":"+JPWPersonalInt(s.order_type)+
       ",\"volume\":"+JPWPersonalNum(s.volume)+",\"entry_price\":"+JPWPersonalTerminalOptional(s.price,m.price_valid)+
       ",\"sl\":"+JPWPersonalTerminalOptional(s.sl,s.sl_readable)+",\"tp\":"+JPWPersonalTerminalOptional(s.tp,m.tp_valid)+
       ",\"current_price\":"+JPWPersonalTerminalOptional(m.current_price,m.current_valid)+
       ",\"stoplimit_entry_price\":"+JPWPersonalTerminalOptional(m.stoplimit_price,m.stoplimit_valid)+
       ",\"opened_msc\":"+JPWPersonalInt(m.opened_msc)+",\"updated_msc\":"+JPWPersonalInt(m.updated_msc)+
       ",\"link_id\":"+JPWPersonalJSON(s.link_id)+",\"link_evidence\":"+JPWPersonalJSON(s.terminal_reason)+
       ",\"specification\":"+m.specification+",\"gross_account_units\":"+
       JPWPersonalTerminalOptional(m.contribution,m.contribution_valid)+"}";
     }
   string quotes="[";
   for(int i=0;i<ArraySize(g_ph_quotes);i++)
     { JPWQuote q=g_ph_quotes[i]; if(i>0) quotes+=",";
       quotes+="{\"symbol\":"+JPWPersonalJSON(q.symbol)+",\"base\":"+JPWPersonalJSON(q.base)+
         ",\"profit\":"+JPWPersonalJSON(q.profit)+",\"bid\":"+JPWPersonalTerminalOptional(q.bid,JPWFinitePositive(q.bid))+",\"ask\":"+
         JPWPersonalTerminalOptional(q.ask,JPWFinitePositive(q.ask))+
         ",\"bid_valid\":"+(JPWFinitePositive(q.bid) ? "true" : "false")+
         ",\"ask_valid\":"+(JPWFinitePositive(q.ask) ? "true" : "false")+",\"time_msc\":"+JPWPersonalInt(q.time_msc)+",\"conversion_pair\":"+
         (q.conversion_pair ? "true" : "false")+"}"; }
   string profiles="[";
   for(int i=0;i<ArraySize(g_ph_profile);i++)
     { if(i>0) profiles+=","; profiles+="{\"symbol_hash\":"+JPWPersonalJSON(g_ph_profile[i].symbol_hash)+
       ",\"spec_hash\":"+JPWPersonalJSON(g_ph_profile[i].spec_hash)+",\"scale\":"+
       JPWPersonalTerminalOptional(g_ph_profile[i].scale,JPWFinitePositive(g_ph_profile[i].scale))+",\"verified_at\":"+JPWPersonalInt(g_ph_profile[i].verified_at)+"}"; }
   return("{\"schema\":\"jpw-personal-capture-details/v1\",\"account_key\":"+JPWPersonalJSON(g_ph_capture.account_key)+
      ",\"source\":"+JPWPersonalJSON(g_ph_capture.source)+",\"product_version\":"+JPWPersonalJSON(g_ph_capture.product_version)+
      ",\"started_utc_msc\":"+JPWPersonalInt(g_ph_capture.started_msc)+",\"finished_utc_msc\":"+
      JPWPersonalInt(g_ph_capture.finished_msc)+",\"observation_utc\":"+JPWPersonalInt(g_ph_capture.wall_seconds)+
      ",\"observation_mono_ms\":"+JPWPersonalInt((long)g_ph_capture.mono_ms)+",\"quality\":"+
      JPWPersonalInt(g_ph_capture.quality)+",\"leverage_valid\":"+(g_ph_capture.leverage_valid ? "true" : "false")+
      ",\"gross_account_units\":"+JPWPersonalTerminalOptional(g_ph_capture.gross,g_ph_capture.leverage_valid)+
      ",\"utc_precision\":\"seconds\",\"server_capture_seconds\":"+
      JPWPersonalInt((long)TimeTradeServer())+",\"account_units\":"+JPWPersonalJSON(g_ph_capture.units)+
      ",\"normalized_currency\":"+JPWPersonalJSON(g_ph_target)+",\"money_divisor\":"+JPWPersonalTerminalOptional(g_ph_divisor,JPWFinitePositive(g_ph_divisor))+
      ",\"balance\":"+JPWPersonalTerminalOptional(g_ph_capture.balance,g_ph_money_valid[0])+",\"equity\":"+
      JPWPersonalTerminalOptional(g_ph_capture.equity,g_ph_money_valid[1])+",\"credit\":"+
      JPWPersonalTerminalOptional(g_ph_capture.credit,g_ph_money_valid[2])+",\"profit\":"+
      JPWPersonalTerminalOptional(g_ph_capture.profit,g_ph_money_valid[3])+",\"margin\":"+
      JPWPersonalTerminalOptional(g_ph_capture.margin,g_ph_money_valid[4])+",\"free_margin\":"+
      JPWPersonalTerminalOptional(g_ph_capture.free_margin,g_ph_money_valid[5])+",\"margin_level\":"+
      JPWPersonalTerminalOptional(g_ph_capture.margin_level,g_ph_money_valid[6])+",\"notional_reason\":"+
      JPWPersonalJSON(g_ph_metric_reason)+",\"subjects\":"+rows+"],\"quotes\":"+quotes+
      "],\"usc_profile\":"+profiles+"]}");
  }
// ready=false means bounded work is in progress, not an accepted partial inventory.
bool JPWPersonalTerminalCaptureStep(const string expected,const ulong timer_started,
                                  JPWPersonalCapture &capture,JPWPersonalSubject &subjects[],bool &ready,string &reason)
  {
   ready=false; reason=""; const ulong slice_started=GetTickCount64();
   if(g_ph_capture_phase==0 && !JPWPersonalTerminalBegin(expected,reason)) return(false);
   string key="",currency="";
   if(!JPWPersonalTerminalIdentity(key,currency) || key!=expected || !TerminalInfoInteger(TERMINAL_CONNECTED) ||
      GetTickCount64()<g_ph_capture_started || GetTickCount64()-g_ph_capture_started>JPW_PERSONAL_CAPTURE_TIMEOUT_MS ||
      PositionsTotal()!=g_ph_position_count || OrdersTotal()!=g_ph_order_count)
     { reason="CAPTURE_CONTEXT_COUNTS_CONNECTION_OR_TIMEOUT_CHANGED"; JPWPersonalTerminalReset(); return(false); }
   int work=0;
   while(work<JPW_PERSONAL_CAPTURE_SLICE && GetTickCount64()-timer_started<500 && GetTickCount64()-slice_started<125)
     {
      if(g_ph_capture_phase==1 || g_ph_capture_phase==4)
        {
         if(g_ph_capture_cursor>=g_ph_position_count)
           { g_ph_capture_phase++; g_ph_capture_cursor=0; continue; }
         JPWPersonalSubject s; JPWPersonalTerminalMeta m;
         if(!JPWPersonalTerminalPosition(g_ph_capture_cursor,s,m) ||
            (g_ph_capture_phase==1 && !JPWPersonalTerminalAppend(g_ph_first,s,m,true)) ||
            (g_ph_capture_phase==4 && !JPWPersonalTerminalAppend(g_ph_check,s,m,false)))
           { reason="POSITION_PROPERTY_OR_MEMORY_UNAVAILABLE"; JPWPersonalTerminalReset(); return(false); }
         g_ph_capture_cursor++; work++; continue;
        }
      if(g_ph_capture_phase==2 || g_ph_capture_phase==5)
        {
         if(g_ph_capture_cursor>=g_ph_order_count)
           {
            g_ph_capture_cursor=0;
            if(g_ph_capture_phase==2) { JPWPersonalTerminalPrepareMath(); g_ph_capture_phase=3; continue; }
            g_ph_capture_phase=6; continue;
           }
         JPWPersonalSubject s; JPWPersonalTerminalMeta m; bool included=false;
         if(!JPWPersonalTerminalPending(g_ph_capture_cursor,s,m,included) ||
            (included && g_ph_capture_phase==2 && !JPWPersonalTerminalAppend(g_ph_first,s,m,true)) ||
            (included && g_ph_capture_phase==5 && !JPWPersonalTerminalAppend(g_ph_check,s,m,false)))
           { reason="PENDING_PROPERTY_OR_MEMORY_UNAVAILABLE"; JPWPersonalTerminalReset(); return(false); }
         g_ph_capture_cursor++; work++; continue;
        }
      if(g_ph_capture_phase==3)
        {
         if(g_ph_capture_cursor>=ArraySize(g_ph_first)) { g_ph_capture_phase=4; g_ph_capture_cursor=0; continue; }
         JPWPersonalTerminalRowMath(g_ph_capture_cursor,timer_started); g_ph_capture_cursor++; work++; continue;
        }
      if(g_ph_capture_phase==6)
        {
         JPWAccount later; string last_key="",last_currency="";
         if(!JPWPersonalTerminalInventoriesEqual() || !JPWReadAccount(later) || !JPWAccountsEqual(g_ph_capture_account,later) ||
            !JPWPersonalTerminalIdentity(last_key,last_currency) || last_key!=expected ||
            !TerminalInfoInteger(TERMINAL_CONNECTED) || PositionsTotal()!=g_ph_position_count || OrdersTotal()!=g_ph_order_count)
           { reason="INVENTORY_CHANGED_DURING_CAPTURE"; JPWPersonalTerminalReset(); return(false); }
         double ending[7]; bool ending_valid[7];
         ending_valid[0]=JPWPersonalTerminalMoney(ACCOUNT_BALANCE,ending[0]);
         ending_valid[1]=JPWPersonalTerminalMoney(ACCOUNT_EQUITY,ending[1]);
         ending_valid[2]=JPWPersonalTerminalMoney(ACCOUNT_CREDIT,ending[2]);
         ending_valid[3]=JPWPersonalTerminalMoney(ACCOUNT_PROFIT,ending[3]);
         ending_valid[4]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN,ending[4]);
         ending_valid[5]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN_FREE,ending[5]);
         ending_valid[6]=JPWPersonalTerminalMoney(ACCOUNT_MARGIN_LEVEL,ending[6]);
         double original[7]; original[0]=g_ph_capture.balance; original[1]=g_ph_capture.equity;
         original[2]=g_ph_capture.credit; original[3]=g_ph_capture.profit; original[4]=g_ph_capture.margin;
         original[5]=g_ph_capture.free_margin; original[6]=g_ph_capture.margin_level;
         for(int a=0;a<7;a++)
            if(ending_valid[a]!=g_ph_money_valid[a] || (ending_valid[a] && ending[a]!=original[a]))
              { g_ph_math_valid=false; g_ph_metric_reason=(a==1 ? "EQUITY_CHANGED_DURING_CAPTURE" : "ACCOUNT_VALUES_CHANGED_DURING_CAPTURE"); }
         // Recheck quote age at acceptance, not only at the beginning of a
         // multi-timer capture. Stored quotes can only support Estimated.
         long acceptance_clock=0;
         bool acceptance_current=JPWClockObserve(g_clock,(long)TimeCurrent(),(long)TimeTradeServer(),GetTickCount64(),30,acceptance_clock);
         if(!acceptance_current && g_ph_position_count>0) g_ph_estimated=true;
         for(int q=0;q<ArraySize(g_ph_quotes);q++)
           { double mid=0; if(!acceptance_current || !JPWQuoteMid(g_ph_quotes[q],acceptance_clock,30,mid)) g_ph_estimated=true; }
         g_ph_capture.stable=true; g_ph_capture.connected=true; g_ph_capture.inventory_valid=true;
         g_ph_capture.wall_seconds=(long)TimeGMT(); g_ph_capture.finished_msc=g_ph_capture.wall_seconds*1000;
         g_ph_capture.mono_ms=GetTickCount64(); g_ph_capture.leverage_valid=g_ph_math_valid;
         g_ph_capture.quality=(g_ph_math_valid ? (g_ph_estimated || g_quotes_pending ? JPW_PERSONAL_ESTIMATED : JPW_PERSONAL_CURRENT) : JPW_PERSONAL_UNAVAILABLE);
         g_ph_capture.details=JPWPersonalTerminalDetails(); capture=g_ph_capture;
         if(ArrayResize(subjects,ArraySize(g_ph_first))!=ArraySize(g_ph_first))
           { reason="MEMORY_UNAVAILABLE"; JPWPersonalTerminalReset(); return(false); }
         for(int i=0;i<ArraySize(g_ph_first);i++) subjects[i]=g_ph_first[i];
         ready=true; JPWPersonalTerminalReset(); return(true);
        }
     }
   return(true);
  }
// Exact live revalidation immediately before requesting a channel. A saved
// SL==0 is insufficient; false suppresses this attempt without resolving it.
bool JPWPersonalTerminalNoSLNow(const string expected,JPWPersonalSubject &subject)
  {
   string key="",currency=""; ulong ticket=0;
   if(!JPWPersonalTerminalIdentity(key,currency) || key!=expected || !TerminalInfoInteger(TERMINAL_CONNECTED) ||
      !JPWPersonalTerminalTicket(subject.ticket,ticket)) return(false);
   double sl=0,volume=0; long identity=0; string symbol="";
   if(subject.kind==JPW_PERSONAL_POSITION)
     {
      return(PositionSelectByTicket(ticket) && PositionGetInteger(POSITION_IDENTIFIER,identity) &&
         JPWPersonalInt(identity)==subject.id && PositionGetString(POSITION_SYMBOL,symbol) && symbol==subject.symbol &&
         PositionGetDouble(POSITION_VOLUME,volume) && volume==subject.volume &&
         PositionGetDouble(POSITION_SL,sl) && JPWPersonalFinite(sl) && sl==0);
     }
   long type=-1;
   return(OrderSelect(ticket) && OrderGetInteger(ORDER_TYPE,type) && JPWRiskEntryType(type) && type==subject.order_type &&
      OrderGetString(ORDER_SYMBOL,symbol) && symbol==subject.symbol && OrderGetDouble(ORDER_VOLUME_CURRENT,volume) &&
      volume==subject.volume && OrderGetDouble(ORDER_SL,sl) && JPWPersonalFinite(sl) && sl==0);
  }
// Specific completion reasons require terminal history, never absence alone.
bool JPWPersonalTerminalCompletionProof(JPWPersonalSubject &subject,string &reason,string &link)
  {
   reason="NO_LONGER_PRESENT_REASON_UNAVAILABLE"; link=""; ulong ticket=0;
   if(!JPWPersonalTerminalTicket(subject.ticket,ticket)) return(false);
   if(subject.kind==JPW_PERSONAL_PENDING)
     {
      long state=-1,position_id=0;
      if(!HistoryOrderSelect(ticket) || !HistoryOrderGetInteger(ticket,ORDER_STATE,state)) return(false);
      if(state==ORDER_STATE_CANCELED || state==ORDER_STATE_EXPIRED || state==ORDER_STATE_REJECTED)
        { reason=(state==ORDER_STATE_EXPIRED ? "EXPIRED_CONFIRMED" : (state==ORDER_STATE_REJECTED ? "REJECTED_CONFIRMED" : "CANCELED_CONFIRMED")); return(true); }
      if(state==ORDER_STATE_FILLED && HistoryOrderGetInteger(ticket,ORDER_POSITION_ID,position_id) && position_id>0)
        { reason="EXECUTED_CONFIRMED"; link="position:"+JPWPersonalInt(position_id); return(true); }
      return(false);
     }
   ulong identifier=0; if(!JPWPersonalTerminalTicket(subject.id,identifier) || !HistorySelectByPosition(identifier)) return(false);
   double open=0,close=0; bool seen=false; const int total=HistoryDealsTotal(); const ulong began=GetTickCount64();
   if(total<1 || total>4096) return(false);
   for(int i=0;i<total;i++)
     {
      if(GetTickCount64()-began>=50) return(false); // Leave cause unavailable instead of monopolizing the timer.
      const ulong deal=HistoryDealGetTicket(i); long id=0,type=0,entry=0; double volume=0;
      if(deal==0 || !HistoryDealGetInteger(deal,DEAL_POSITION_ID,id) || (ulong)id!=identifier ||
         !HistoryDealGetInteger(deal,DEAL_TYPE,type) || !HistoryDealGetInteger(deal,DEAL_ENTRY,entry) ||
         !HistoryDealGetDouble(deal,DEAL_VOLUME,volume) || !JPWPersonalFinite(volume) || volume<0) return(false);
      if(type!=DEAL_TYPE_BUY && type!=DEAL_TYPE_SELL) continue;
      if(entry==DEAL_ENTRY_IN) { open+=volume; seen=true; }
      else if(entry==DEAL_ENTRY_OUT || entry==DEAL_ENTRY_OUT_BY) close+=volume;
      else return(false); // Reversal cannot certify this simple volume reconciliation.
     }
   if(seen && open>0 && close>=open && MathAbs(close-open)<=1e-10*MathMax(1.0,open))
     { reason="CLOSED_CONFIRMED"; return(true); }
   return(false);
  }
string JPWPersonalTerminalNotify(const string message,bool &channel_error)
  {
   channel_error=false;
   if(MQLInfoInteger(MQL_TESTER)!=0) { channel_error=true; return("TESTER_CHANNELS_UNAVAILABLE_NOT_CALLED"); }
   ResetLastError(); Alert(message); const int alert_error=GetLastError();
   ResetLastError(); const bool sound_accepted=PlaySound("alert.wav"); const int sound_error=GetLastError();
   channel_error=alert_error!=0 || !sound_accepted || sound_error!=0;
   return("{\"popup_call\":\"RETURNED_UNCONFIRMED\",\"popup_error\":"+JPWPersonalInt(alert_error)+
      ",\"sound_request_accepted\":"+(sound_accepted ? "true" : "false")+",\"sound_error\":"+
      JPWPersonalInt(sound_error)+",\"operator_seen_or_heard\":\"UNAVAILABLE\"}");
  }
#endif

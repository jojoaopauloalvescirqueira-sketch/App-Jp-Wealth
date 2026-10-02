#ifndef JPW_SIGNAL_COPY_TERMINAL_MQH
#define JPW_SIGNAL_COPY_TERMINAL_MQH
#include <JPWealth/JPW_SignalCopy_Types.mqh>
#include <JPWealth/JPW_SignalCopy_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Profile.mqh>
#include <JPWealth/JPW_Alavancagem_Genesis_Store.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Live.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Factor.mqh>
// Read-only request adapter. It is not called by draw functions, never sends
// orders, never writes a financial record and never logs a message or amount.
// Its catalog, routes, clock and ATR cache are private to this new module.
struct JPWSignalCatalogEntry { string symbol; string base; string profit; };
JPWSignalCatalogEntry g_signal_catalog[];
JPWRoute g_signal_routes[];
int g_signal_scan_index=0,g_signal_scan_total=-1;
bool g_signal_catalog_ready=false,g_signal_clock_ready=false;
bool g_signal_data_unsynchronized=false;
bool g_signal_adapter_deferred=false;
bool JPWSignalAdapterDeferred() { return(g_signal_adapter_deferred); }
JPWClock g_signal_clock;
string g_signal_terminal_context="",g_signal_root_context="",g_signal_root_symbol="";
int g_signal_atr_handle=INVALID_HANDLE;
JPWRaizNLiveCache g_signal_root_cache;
long g_signal_tick_baseline=0;
bool g_signal_new_tick=false,g_signal_root_connected=false;

bool JPWSignalBudget(const ulong started)
  { const ulong now=GetTickCount64(); const bool valid=(now>=started && now-started<500);
    if(!valid) g_signal_adapter_deferred=true; return(valid); }

void JPWSignalTerminalReset()
  {
   if(g_signal_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_signal_atr_handle);
   g_signal_atr_handle=INVALID_HANDLE;
   JPWRaizNLiveResetCache(g_signal_root_cache);
   g_signal_terminal_context=""; g_signal_root_context=""; g_signal_root_symbol="";
   g_signal_tick_baseline=0; g_signal_new_tick=false; g_signal_root_connected=false;
   ArrayResize(g_signal_catalog,0); ArrayResize(g_signal_routes,0);
   g_signal_scan_index=0; g_signal_scan_total=-1; g_signal_catalog_ready=false;
   g_signal_clock_ready=false;
   g_signal_data_unsynchronized=false; g_signal_adapter_deferred=false;
  }

bool JPWSignalAccountDouble(const ENUM_ACCOUNT_INFO_DOUBLE property,double &value)
  { ResetLastError(); value=AccountInfoDouble(property); return(GetLastError()==0 && MathIsValidNumber(value)); }

bool JPWSignalIdentity(JPWSignalCapture &capture)
  {
   ResetLastError(); capture.account.login=AccountInfoInteger(ACCOUNT_LOGIN);
   if(GetLastError()!=0 || capture.account.login<=0) return(false);
   ResetLastError(); capture.account.server=AccountInfoString(ACCOUNT_SERVER);
   if(GetLastError()!=0 || capture.account.server=="") return(false);
   ResetLastError(); capture.account.currency=JPWNormalizeCurrency(AccountInfoString(ACCOUNT_CURRENCY));
   if(GetLastError()!=0 || capture.account.currency=="") return(false);
   ResetLastError(); capture.margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(GetLastError()!=0) return(false);
   ResetLastError(); const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(GetLastError()!=0 || installation=="" || !JPWProfileHash(JPWProfileFrame(capture.account.server)+
      JPWProfileFrame(IntegerToString(capture.account.login))+
      JPWProfileFrame(capture.account.currency)+JPWProfileFrame(installation),capture.context)) return(false);
   return(JPWSignalAccountDouble(ACCOUNT_BALANCE,capture.balance) &&
          JPWSignalAccountDouble(ACCOUNT_EQUITY,capture.equity) &&
          JPWSignalAccountDouble(ACCOUNT_PROFIT,capture.profit) &&
          JPWSignalAccountDouble(ACCOUNT_CREDIT,capture.credit));
  }

bool JPWSignalSameContext(JPWSignalCapture &a,JPWSignalCapture &b)
  {
   return(a.context!="" && a.context==b.context && a.margin_mode==b.margin_mode &&
      a.account.login==b.account.login && a.account.server==b.account.server &&
      a.account.currency==b.account.currency && a.balance==b.balance && a.credit==b.credit);
   // Equity/profit may move with a tick; requiring equality would reject valid
   // live samples. Balance and credit are revalidated as account context.
  }

void JPWSignalClearRow(JPWSignalRow &r)
  {
   r.kind=0; r.ticket=0; r.identifier=0; r.opened_msc=0; r.updated_msc=0;
   r.symbol=""; r.side=-1; r.order_type=-1; r.order_state=-1; r.expiration=0;
   r.volume=0; r.initial_volume=0; r.entry=0; r.sl=0; r.tp=0; r.stop_limit=0;
   r.digits=0; r.volume_digits=0;
  }

int JPWSignalPendingSide(const long type)
  {
   if(type==ORDER_TYPE_BUY || type==ORDER_TYPE_BUY_LIMIT || type==ORDER_TYPE_BUY_STOP || type==ORDER_TYPE_BUY_STOP_LIMIT) return(POSITION_TYPE_BUY);
   if(type==ORDER_TYPE_SELL || type==ORDER_TYPE_SELL_LIMIT || type==ORDER_TYPE_SELL_STOP || type==ORDER_TYPE_SELL_STOP_LIMIT) return(POSITION_TYPE_SELL);
   return(-1);
  }

bool JPWSignalRowPrecision(JPWSignalRow &r)
  {
   long digits=0; double step=0;
   if(!SymbolInfoInteger(r.symbol,SYMBOL_DIGITS,digits) || digits<0 || digits>16 ||
      !SymbolInfoDouble(r.symbol,SYMBOL_VOLUME_STEP,step) || !JPWFinitePositive(step)) return(false);
   r.digits=(int)digits; r.volume_digits=0;
   double scaled=step;
   while(r.volume_digits<8 && MathAbs(scaled-MathRound(scaled))>1e-9)
     { scaled*=10.0; r.volume_digits++; }
   return(MathAbs(scaled-MathRound(scaled))<=1e-9);
  }

bool JPWSignalReadRows(JPWSignalRow &rows[],string &reason,const ulong started)
  {
   ArrayResize(rows,0);
   const int np=PositionsTotal(),no=OrdersTotal();
   if(np<0 || no<0 || np>JPW_SIGNAL_MAX_ROWS || no>JPW_SIGNAL_MAX_ROWS-np ||
      ArrayResize(rows,np+no)!=np+no) { reason="Catálogo incompleto ou acima do limite"; return(false); }
   for(int i=0;i<np;i++)
     {
      if(!JPWSignalBudget(started)) { reason="Coleta adiada: orçamento de 500 ms"; return(false); }
      JPWSignalRow r; JPWSignalClearRow(r);
      r.kind=JPW_SIGNAL_POSITION; r.ticket=PositionGetTicket(i);
      long side=-1;
      if(r.ticket==0 || !PositionSelectByTicket(r.ticket) ||
         !PositionGetInteger(POSITION_IDENTIFIER,r.identifier) ||
         !PositionGetInteger(POSITION_TIME_MSC,r.opened_msc) ||
         !PositionGetInteger(POSITION_TIME_UPDATE_MSC,r.updated_msc) ||
         !PositionGetInteger(POSITION_TYPE,side) ||
         !PositionGetString(POSITION_SYMBOL,r.symbol) ||
         !PositionGetDouble(POSITION_VOLUME,r.volume) ||
         !PositionGetDouble(POSITION_PRICE_OPEN,r.entry) ||
         !PositionGetDouble(POSITION_SL,r.sl) || !PositionGetDouble(POSITION_TP,r.tp))
        { reason="Posição incompleta: entrada, SL, TP, volume ou identidade"; return(false); }
      r.side=(int)side; r.initial_volume=r.volume;
      if(r.identifier<=0 || r.opened_msc<=0 || r.updated_msc<r.opened_msc || r.symbol=="" ||
         (r.side!=POSITION_TYPE_BUY && r.side!=POSITION_TYPE_SELL) ||
         !JPWFinitePositive(r.volume) || !JPWFinitePositive(r.entry) ||
         !MathIsValidNumber(r.sl) || r.sl<0 || !MathIsValidNumber(r.tp) || r.tp<0 ||
         !JPWSignalRowPrecision(r)) { reason="Propriedade inválida da posição"; return(false); }
      rows[i]=r;
     }
   for(int i=0;i<no;i++)
     {
      if(!JPWSignalBudget(started)) { reason="Coleta adiada: orçamento de 500 ms"; return(false); }
      JPWSignalRow r; JPWSignalClearRow(r);
      r.kind=JPW_SIGNAL_PENDING; r.ticket=OrderGetTicket(i);
      long type=-1,state=-1;
      if(r.ticket==0 || !OrderSelect(r.ticket) || !OrderGetInteger(ORDER_TYPE,type) ||
         !OrderGetInteger(ORDER_STATE,state) || !OrderGetInteger(ORDER_POSITION_ID,r.identifier) ||
         !OrderGetInteger(ORDER_TIME_SETUP_MSC,r.opened_msc) ||
         !OrderGetInteger(ORDER_TIME_EXPIRATION,r.expiration) ||
         !OrderGetString(ORDER_SYMBOL,r.symbol) ||
         !OrderGetDouble(ORDER_VOLUME_CURRENT,r.volume) ||
         !OrderGetDouble(ORDER_VOLUME_INITIAL,r.initial_volume) ||
         !OrderGetDouble(ORDER_PRICE_OPEN,r.entry) || !OrderGetDouble(ORDER_SL,r.sl) ||
         !OrderGetDouble(ORDER_TP,r.tp) || !OrderGetDouble(ORDER_PRICE_STOPLIMIT,r.stop_limit))
        { reason="Pendente incompleta: tipo, SL, TP, volume ou identidade"; return(false); }
      r.side=JPWSignalPendingSide(type); r.order_type=(int)type; r.order_state=(int)state;
      if(r.opened_msc<=0 || r.symbol=="" || !JPWFinitePositive(r.volume) ||
         !JPWFinitePositive(r.initial_volume) || r.volume>r.initial_volume ||
         !JPWFinitePositive(r.entry) || !MathIsValidNumber(r.sl) || r.sl<0 ||
         !MathIsValidNumber(r.tp) || r.tp<0 || !MathIsValidNumber(r.stop_limit) ||
         r.stop_limit<0 || !JPWSignalRowPrecision(r)) { reason="Propriedade inválida da pendente"; return(false); }
      rows[np+i]=r;
     }
   // Canonical order is an implementation detail, not a Genesis/Defense role.
   for(int i=1;i<ArraySize(rows);i++)
     {
      JPWSignalRow item=rows[i]; int j=i-1;
      while(j>=0 && (rows[j].kind>item.kind || (rows[j].kind==item.kind && rows[j].ticket>item.ticket)))
        { rows[j+1]=rows[j]; j--; }
      rows[j+1]=item;
     }
   for(int i=1;i<ArraySize(rows);i++)
      if(rows[i].kind==rows[i-1].kind && rows[i].ticket==rows[i-1].ticket)
        { reason="Identidade duplicada no catálogo"; return(false); }
   return(JPWSignalBudget(started));
  }

string JPWSignalRowTuple(JPWSignalRow &r)
  {
   return(IntegerToString(r.kind)+"|"+IntegerToString((long)r.ticket)+"|"+
      IntegerToString(r.identifier)+"|"+IntegerToString(r.opened_msc)+"|"+
      IntegerToString(r.updated_msc)+"|"+JPWProfileFrame(r.symbol)+"|"+
      IntegerToString(r.side)+"|"+IntegerToString(r.order_type)+"|"+
      IntegerToString(r.order_state)+"|"+IntegerToString(r.expiration)+"|"+
      DoubleToString(r.volume,-16)+"|"+DoubleToString(r.initial_volume,-16)+"|"+
      DoubleToString(r.entry,-16)+"|"+DoubleToString(r.sl,-16)+"|"+
      DoubleToString(r.tp,-16)+"|"+DoubleToString(r.stop_limit,-16)+"|"+
      IntegerToString(r.digits)+"|"+IntegerToString(r.volume_digits));
  }

bool JPWSignalRowsEqual(JPWSignalRow &a[],JPWSignalRow &b[])
  {
   if(ArraySize(a)!=ArraySize(b)) return(false);
   for(int i=0;i<ArraySize(a);i++) if(JPWSignalRowTuple(a[i])!=JPWSignalRowTuple(b[i])) return(false);
   return(true);
  }

bool JPWSignalDigest(JPWSignalCapture &capture,JPWSignalRow &rows[],string &digest)
  {
   string raw=JPWProfileFrame(capture.context)+IntegerToString(capture.margin_mode)+"|"+
      DoubleToString(capture.balance,-16)+"|"+DoubleToString(capture.credit,-16)+"|"+IntegerToString(ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++) raw+=JPWProfileFrame(JPWSignalRowTuple(rows[i]));
   return(JPWProfileHash(raw,digest));
  }

bool JPWSignalCollect(JPWSignalCapture &capture,JPWSignalRow &rows[],string &reason,const ulong requested_started=0)
  {
   const ulong started=(requested_started>0 ? requested_started : GetTickCount64());
   g_signal_adapter_deferred=false; reason=""; capture.context=""; capture.digest=""; capture.accepted_ms=0;
   capture.reference_closed=false; capture.reference_identifier=0; ArrayResize(rows,0);
   for(int attempt=0;attempt<2;attempt++)
     {
      JPWSignalCapture before,after; JPWSignalRow first[]; JPWSignalRow second[];
      if(!JPWSignalBudget(started)) { reason="Coleta adiada: orçamento de 500 ms"; return(false); }
      if(!JPWSignalIdentity(before) || !JPWSignalReadRows(first,reason,started) ||
         !JPWSignalIdentity(after) || !JPWSignalReadRows(second,reason,started))
        { if(reason=="") reason="Conta ou catálogo indisponível"; return(false); }
      JPWSignalCapture final_context;
      if(!JPWSignalIdentity(final_context)) { reason="Identidade não confirmada"; return(false); }
      if(!JPWSignalSameContext(before,after) || !JPWSignalSameContext(after,final_context) ||
         !JPWSignalRowsEqual(first,second)) { reason="Composição ou conta mudou durante a coleta"; continue; }
      if(!JPWSignalBudget(started)) { reason="Coleta adiada: orçamento de 500 ms"; return(false); }
      after.observed_utc=(long)TimeGMT(); after.accepted_ms=GetTickCount64();
      if(after.observed_utc<=0 || !JPWSignalDigest(after,second,after.digest))
        { reason="Identidade técnica da amostra indisponível"; return(false); }
      after.reference_closed=false; after.reference_identifier=0;
      const int row_count=ArraySize(second);
      if(ArrayResize(rows,row_count)!=row_count)
        { ArrayResize(rows,0); reason="Memória insuficiente para o catálogo completo"; return(false); }
      // Struct rows contain strings; assign each element after exact sizing.
      for(int i=0;i<row_count;i++) rows[i]=second[i];
      capture=after; reason="Leitura conferida"; return(true);
     }
   return(false);
  }

bool JPWSignalRevalidate(JPWSignalCapture &capture,JPWSignalRow &rows[],string &reason,const ulong requested_started=0,
   const bool require_recent=true)
  {
   const ulong started=(requested_started>0 ? requested_started : GetTickCount64());
   g_signal_adapter_deferred=false; reason=""; const ulong now=GetTickCount64();
   if(capture.context=="" || capture.digest=="" || now<capture.accepted_ms ||
      (require_recent && now-capture.accepted_ms>30000))
     { reason="Leitura vencida; atualize antes de preparar ou exportar"; return(false); }
   JPWSignalCapture live; JPWSignalRow observed[];
   if(!JPWSignalCollect(live,observed,reason,started))
     { if(reason=="") reason="Não foi possível conferir a leitura"; return(false); }
   string digest="";
   if(!JPWSignalSameContext(capture,live) || !JPWSignalRowsEqual(rows,observed) ||
      !JPWSignalDigest(live,observed,digest) || digest!=capture.digest)
     { reason="Conta, volume, entrada, SL, TP ou pendente mudou; atualize e confira"; return(false); }
   if(!JPWSignalBudget(started)) { reason="Conferência adiada: orçamento de 500 ms"; return(false); }
   // The bounded collection itself may cross the freshness boundary. Do not
   // accept a frozen preview that expired while its composition was checked.
   const ulong finished=GetTickCount64();
   if(finished<capture.accepted_ms ||
      (require_recent && finished-capture.accepted_ms>30000))
     { reason="Leitura vencida; atualize antes de preparar ou exportar"; return(false); }
   reason="Composição revalidada; equity da leitura congelado"; return(true);
  }

// Only the caller's first preview may renew this reading. A frozen message
// must use Revalidate(require_recent=true), never this renewal. Rows and role
// choices remain unchanged; only an identical account/composition can renew.
bool JPWSignalRenewCapture(JPWSignalCapture &capture,JPWSignalRow &rows[],string &reason,const ulong requested_started=0)
  {
   g_signal_adapter_deferred=false; reason="";
   const ulong started=(requested_started>0 ? requested_started : GetTickCount64());
   if(capture.context=="" || capture.digest=="")
     { reason="Leitura anterior ausente; atualize e confira os papéis"; return(false); }
   JPWSignalCapture renewed; JPWSignalRow observed[];
   if(!JPWSignalCollect(renewed,observed,reason,started)) return(false);
   if(!JPWSignalSameContext(capture,renewed) || !JPWSignalRowsEqual(rows,observed) ||
      capture.digest!=renewed.digest)
     { reason="Conta, volume, entrada, SL, TP ou pendente mudou; atualize e confira"; return(false); }
   if(!JPWSignalBudget(started))
     { reason="Renovação adiada: orçamento de 500 ms"; return(false); }
   renewed.reference_closed=capture.reference_closed;
   renewed.reference_identifier=capture.reference_identifier;
   capture=renewed;
   reason="Leitura renovada antes da primeira prévia; composição e papéis preservados";
   return(true);
  }

bool JPWSignalReadReference(JPWSignalCapture &capture,JPWSignalRow &rows[],const int selected,
   const long selector,int &reference_row,long &reference_identifier,bool &closed,string &reason,const ulong requested_started=0)
  {
   g_signal_adapter_deferred=false; reference_row=-1; reference_identifier=0; closed=false;
   const ulong started=(requested_started>0 ? requested_started : GetTickCount64());
   if(selected<0 || selected>=ArraySize(rows) || selector<0 || !JPWSignalBudget(started))
     { reason="Seleção ou orçamento indisponível"; return(false); }
   JPWSignalCapture before,after;
   if(!JPWSignalIdentity(before) || !JPWSignalSameContext(capture,before))
     { reason="Conta mudou antes da consulta da referência"; return(false); }
   JPWGenesisRecord record;
   const JPW_GENESIS_STORE_STATE status=JPWGenesisRead(before.account,selector,JPW_GENESIS_FOLDER,record);
   if(!JPWSignalIdentity(after) || !JPWSignalSameContext(before,after) || !JPWSignalBudget(started))
     { reason="Conta mudou ou consulta adiada"; return(false); }
   if(status==JPW_GENESIS_ABSENT) { reason="Sem referência guardada; papéis apenas inferidos"; return(true); }
   if(status!=JPW_GENESIS_VALID) { reason="Referência guardada indisponível; não inferir sucessora"; return(false); }
   if(record.symbol!=rows[selected].symbol || record.direction!=rows[selected].side)
     { reason="Referência guardada pertence a outro símbolo ou direção"; return(true); }
   reference_identifier=record.identifier;
   closed=(record.reference_state==JPW_GENESIS_CLOSED || record.reference_state==JPW_GENESIS_REVERSED);
   if(closed) { reason="Referência encerrada ou revertida; não promover sucessora"; return(true); }
   for(int i=0;i<ArraySize(rows);i++)
      if(rows[i].kind==JPW_SIGNAL_POSITION && rows[i].identifier==record.identifier &&
         rows[i].symbol==record.symbol && rows[i].side==record.direction) { reference_row=i; break; }
   reason=(reference_row>=0 ? "Referência guardada conferida" : "Referência não encontrada; ausência não comprova encerramento");
   return(true);
  }

bool JPWSignalReadInstrument(const string symbol,JPWInstrument &instrument)
  {
   long mode=0; double size=0; string base="",profit="",basis="",isin="";
   if(!SymbolInfoInteger(symbol,SYMBOL_TRADE_CALC_MODE,mode) ||
      !SymbolInfoDouble(symbol,SYMBOL_TRADE_CONTRACT_SIZE,size) ||
      !SymbolInfoString(symbol,SYMBOL_CURRENCY_BASE,base) ||
      !SymbolInfoString(symbol,SYMBOL_CURRENCY_PROFIT,profit) || !JPWFinitePositive(size)) return(false);
   SymbolInfoString(symbol,SYMBOL_BASIS,basis); SymbolInfoString(symbol,SYMBOL_ISIN,isin);
   instrument.symbol=symbol; instrument.calc_mode=(int)mode; instrument.contract_size=size;
   instrument.base=JPWNormalizeCurrency(base); instrument.profit=JPWNormalizeCurrency(profit);
   instrument.underlying_verified=(basis!="" || isin!=""); return(true);
  }

bool JPWSignalConversionMetadata(const string symbol,const string base,const string profit)
  {
   long custom=0; JPWInstrument instrument;
   return(SymbolInfoInteger(symbol,SYMBOL_CUSTOM,custom) && custom==0 &&
      JPWSignalReadInstrument(symbol,instrument) &&
      (instrument.calc_mode==SYMBOL_CALC_MODE_FOREX || instrument.calc_mode==SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE) &&
      instrument.base==base && instrument.profit==profit && JPWIsFiat(base) && JPWIsFiat(profit) && base!=profit);
  }

bool JPWSignalPrepareCatalog(const ulong started,string &reason)
  {
   const int count=SymbolsTotal(false);
   if(count<=0) { reason="Catálogo cambial indisponível"; return(false); }
   if(count!=g_signal_scan_total)
     { g_signal_scan_total=count; g_signal_scan_index=0; g_signal_catalog_ready=false; ArrayResize(g_signal_catalog,0); }
   if(g_signal_catalog_ready) return(true);
   const ulong step_started=GetTickCount64(); int handled=0;
   while(g_signal_scan_index<count && handled<100 && JPWSignalBudget(started))
     {
      if(GetTickCount64()-step_started>=50) break;
      const string symbol=SymbolName(g_signal_scan_index++,false); handled++;
      JPWInstrument instrument;
      if(symbol=="" || !JPWSignalReadInstrument(symbol,instrument) ||
         !JPWSignalConversionMetadata(symbol,instrument.base,instrument.profit)) continue;
      const int n=ArraySize(g_signal_catalog);
      if(ArrayResize(g_signal_catalog,n+1)!=n+1) { reason="Catálogo cambial incompleto"; return(false); }
      g_signal_catalog[n].symbol=symbol; g_signal_catalog[n].base=instrument.base; g_signal_catalog[n].profit=instrument.profit;
     }
   g_signal_catalog_ready=(g_signal_scan_index>=count);
   if(!g_signal_catalog_ready) { g_signal_adapter_deferred=true; reason="Preparação cambial pendente; tente no próximo ciclo"; }
   return(g_signal_catalog_ready);
  }

bool JPWSignalCaptureQuote(const string symbol,const string base,const string profit,
   const bool conversion,JPWQuote &quotes[])
  {
   if(conversion && !JPWSignalConversionMetadata(symbol,base,profit)) return(false);
   const int existing=JPWQuoteIndex(quotes,symbol);
   if(existing>=0)
     { if(conversion) quotes[existing].conversion_pair=true; return(quotes[existing].base==base && quotes[existing].profit==profit); }
   long selected=0;
   if(!SymbolInfoInteger(symbol,SYMBOL_SELECT,selected) || (selected==0 && !SymbolSelect(symbol,true))) return(false);
   MqlTick tick; long sync=0;
   if(!SymbolInfoTick(symbol,tick) || !SeriesInfoInteger(symbol,PERIOD_CURRENT,SERIES_SYNCHRONIZED,sync)) return(false);
   if(sync==0) g_signal_data_unsynchronized=true;
   if(!JPWFinitePositive(tick.bid) || !JPWFinitePositive(tick.ask) || tick.ask<tick.bid || tick.time_msc<=0) return(false);
   const int n=ArraySize(quotes); if(ArrayResize(quotes,n+1)!=n+1) return(false);
   quotes[n].symbol=symbol; quotes[n].base=base; quotes[n].profit=profit;
   quotes[n].bid=tick.bid; quotes[n].ask=tick.ask; quotes[n].time_msc=tick.time_msc;
   quotes[n].conversion_pair=conversion;
   return(true);
  }

bool JPWSignalPrepareRoute(const string source,const string target,JPWQuote &quotes[],
   const long now_ms,const bool clock_valid,const bool connected,const ulong started,string &reason)
  {
   if(source==target) return(true);
   if(!JPWSignalPrepareCatalog(started,reason)) return(false);
   // Read each relevant edge once. The pure route selector then prefers recent
   // direct/inverse or two-leg routes; an old route is never falsely Current.
   for(int i=0;i<ArraySize(g_signal_catalog);i++)
     {
      if(!JPWSignalBudget(started)) { reason="Conversão adiada: orçamento de 500 ms"; return(false); }
      if(!JPWSignalConversionMetadata(g_signal_catalog[i].symbol,g_signal_catalog[i].base,g_signal_catalog[i].profit))
        { g_signal_scan_index=0; g_signal_scan_total=-1; g_signal_catalog_ready=false;
          ArrayResize(g_signal_catalog,0); ArrayResize(g_signal_routes,0); g_signal_adapter_deferred=true;
          reason="Catálogo cambial mudou; nova conferência pendente"; return(false); }
      JPWSignalCaptureQuote(g_signal_catalog[i].symbol,g_signal_catalog[i].base,
         g_signal_catalog[i].profit,true,quotes);
     }
   JPWRoute previous,chosen; previous.valid=false;
   double rate=0; bool estimated=false; long oldest=0;
   if(!JPWFindRouteReading(source,target,quotes,now_ms,30,clock_valid,connected,previous,chosen,rate,estimated,oldest))
     { reason="Sem conversão completa na moeda da conta"; return(false); }
   return(true);
  }

bool JPWSignalPortfolio(JPWPosition &positions[],JPWSignalCapture &capture,const string target,
   const bool usc,JPWProfileEntry &profile[],JPWQuote &quotes[],JPWInstrument &instruments[],double &scales[],
   const long now_ms,const bool clock_valid,const bool connected,const ulong started,string &reason)
  {
   const int count=ArraySize(positions);
   if(ArrayResize(instruments,count)!=count || ArrayResize(scales,count)!=count) return(false);
   for(int i=0;i<count;i++)
     {
      if(!JPWSignalBudget(started)) { reason="Cálculo adiado: orçamento de 500 ms"; return(false); }
      if(!JPWSignalReadInstrument(positions[i].symbol,instruments[i])) { reason="Especificação do contrato indisponível"; return(false); }
      JPW_MODEL model=JPW_MODEL_NONE;
      if(JPWClassify(instruments[i],model)!=JPW_OK) { reason="Contrato fora da cobertura atual"; return(false); }
      scales[i]=1.0;
      if(usc && !JPWProfileFind(instruments[i],profile,scales[i])) { reason="Verifique os contratos USC do instrumento"; return(false); }
      if(!JPWSignalCaptureQuote(instruments[i].symbol,instruments[i].base,instruments[i].profit,
         model==JPW_MODEL_FIAT_FOREX,quotes)) { reason="Sem cotação válida do instrumento"; return(false); }
      const string source=(model==JPW_MODEL_FIAT_FOREX ? instruments[i].base : instruments[i].profit);
      if(!JPWSignalPrepareRoute(source,target,quotes,now_ms,clock_valid,connected,started,reason)) return(false);
      if(usc && !JPWSignalPrepareRoute(instruments[i].profit,"USD",quotes,now_ms,clock_valid,connected,started,reason)) return(false);
     }
   for(int i=0;i<count;i++)
     {
      JPWInstrument later;
      if(!JPWSignalBudget(started) || !JPWSignalReadInstrument(instruments[i].symbol,later) ||
         later.calc_mode!=instruments[i].calc_mode || later.base!=instruments[i].base ||
         later.profit!=instruments[i].profit || later.contract_size!=instruments[i].contract_size ||
         later.underlying_verified!=instruments[i].underlying_verified)
        { reason="Contrato mudou ou leitura adiada"; return(false); }
      if(usc && (!JPWProfileFind(later,profile,scales[i]) ||
         !JPWProfileTickConsistent(later,scales[i],capture.account,quotes,now_ms,clock_valid,connected)))
        { reason="Unidades USC não conferidas"; return(false); }
     }
   return(true);
  }

// Preserve the Bid/Ask actually used by the existing one-tick RootN collector.
// Re-reading a tick afterward could make the percent's P0 disagree with the
// exported quote and the mandatory preparation gate.
class JPWSignalRootProvider : public JPWRaizNLiveNativeProvider
  {
public:
   double sampled_bid;
   double sampled_ask;
   virtual bool ReadQuote(double &bid,double &ask,long &time_msc)
     {
      if(!JPWRaizNLiveNativeProvider::ReadQuote(bid,ask,time_msc)) return(false);
      sampled_bid=bid; sampled_ask=ask; return(true);
     }
  };

bool JPWSignalCollectMetrics(JPWSignalCapture &capture,JPWSignalRow &rows[],const int selected,
   JPWSignalMetrics &metrics,string &reason,const ulong requested_started=0)
  {
   JPWSignalClearMetrics(metrics); reason=""; g_signal_adapter_deferred=false;
   const ulong started=(requested_started>0 ? requested_started : GetTickCount64());
   if(selected<0 || selected>=ArraySize(rows) || !JPWSignalRevalidate(capture,rows,reason,started)) return(false);
   if(g_signal_terminal_context!=capture.context)
     { JPWSignalTerminalReset(); g_signal_terminal_context=capture.context; }
   const bool connected=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
   if(!g_signal_clock_ready)
     { JPWClockReset(g_signal_clock,(long)TimeCurrent(),GetTickCount64()); g_signal_clock_ready=true; }
   long now_ms=0;
   const bool clock_valid=JPWClockObserve(g_signal_clock,(long)TimeCurrent(),(long)TimeTradeServer(),GetTickCount64(),30,now_ms);
   metrics.floating_valid=JPWFloatingPercent(capture.balance,capture.profit,metrics.floating_percent);
   metrics.floating_quality=(metrics.floating_valid ? (connected && clock_valid ? 2 : 1) : 0);
   metrics.floating_reason=(metrics.floating_valid ? "Profit e balance da leitura, na mesma moeda" : "Balance ou profit inválido");
   string target=""; double divisor=0;
   const bool units=JPWAccountUnits(capture.account.currency,target,divisor);
   const bool usc=(divisor==100.0);
   JPWProfileEntry profile[];
   bool profile_valid=(!usc || JPWProfileLoad(capture.account,profile));
   JPWQuote quotes[]; JPWPosition live[]; JPWPosition scenario[];
   g_signal_data_unsynchronized=false;
   int n=0;
   for(int i=0;i<ArraySize(rows);i++) if(rows[i].kind==JPW_SIGNAL_POSITION)
     {
      if(ArrayResize(live,n+1)!=n+1) { reason="Portfolio incompleto"; return(false); }
      live[n].ticket=rows[i].ticket; live[n].identifier=rows[i].identifier;
      live[n].symbol=rows[i].symbol; live[n].direction=rows[i].side; live[n].volume=rows[i].volume; n++;
     }
   if(units && profile_valid && JPWFinitePositive(capture.equity/divisor))
     {
      JPWInstrument instruments[]; double scales[];
      double gross=0; bool estimated=false; long oldest=0;
      string leverage_reason="";
      if(JPWSignalPortfolio(live,capture,target,usc,profile,quotes,instruments,scales,now_ms,clock_valid,connected,started,leverage_reason) &&
         JPWGrossReading(live,instruments,quotes,target,now_ms,30,clock_valid,connected,scales,g_signal_routes,gross,estimated,oldest)==JPW_OK &&
         JPWLeverage(gross,capture.equity/divisor,metrics.leverage)==JPW_OK)
        {
         metrics.leverage_valid=true; metrics.leverage_quality=(estimated || g_signal_data_unsynchronized ? 1 : 2);
         metrics.leverage_reason="Nocional bruto de toda a conta / equity desta leitura";
         if(rows[selected].kind==JPW_SIGNAL_POSITION)
           { metrics.scenario_valid=true; metrics.scenario_leverage=metrics.leverage; }
         else
           {
            string scenario_reason="";
            if(JPWSignalVirtualPositions(rows,selected,capture.margin_mode,scenario,scenario_reason) &&
               JPWSignalPortfolio(scenario,capture,target,usc,profile,quotes,instruments,scales,now_ms,clock_valid,connected,started,scenario_reason) &&
               JPWGrossReading(scenario,instruments,quotes,target,now_ms,30,clock_valid,connected,scales,g_signal_routes,gross,estimated,oldest)==JPW_OK &&
               JPWLeverage(gross,capture.equity/divisor,metrics.scenario_leverage)==JPW_OK)
              { metrics.scenario_valid=true; if(estimated || g_signal_data_unsynchronized) metrics.leverage_quality=1; }
            else metrics.leverage_reason+=". Simulação indisponível: "+scenario_reason;
           }
        }
      else metrics.leverage_reason=(leverage_reason!="" ? leverage_reason : "Nocional ou conversão indisponível");
     }
   else metrics.leverage_reason=(!units ? "Moeda não suportada" : !profile_valid ? "Verifique os contratos USC" : "Equity não positivo ou inválido");
   if(g_signal_adapter_deferred || !JPWSignalBudget(started))
     { JPWSignalClearMetrics(metrics); reason="Métricas adiadas: catálogo cambial ou orçamento de 500 ms"; return(false); }
   const string symbol=rows[selected].symbol;
   long is_selected=0;
   if(!SymbolInfoInteger(symbol,SYMBOL_SELECT,is_selected) || (is_selected==0 && !SymbolSelect(symbol,true)))
     { metrics.root_reason="Símbolo selecionado indisponível"; metrics.stop_reason=metrics.root_reason;
       if(!JPWSignalRevalidate(capture,rows,reason,started)) { JPWSignalClearMetrics(metrics); return(false); }
       return(true); }
   double point=0,tick_size=0; MqlTick selected_tick;
   if(SymbolInfoDouble(symbol,SYMBOL_POINT,point) && SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_SIZE,tick_size) &&
      JPWFinitePositive(point) && JPWFinitePositive(tick_size) && SymbolInfoTick(symbol,selected_tick) &&
      JPWFinitePositive(selected_tick.bid) && JPWFinitePositive(selected_tick.ask) && selected_tick.ask>=selected_tick.bid && selected_tick.time_msc>0 &&
      (!clock_valid || selected_tick.time_msc<=now_ms+2000))
     {
      metrics.point=point; metrics.tick_size=tick_size; metrics.bid=selected_tick.bid; metrics.ask=selected_tick.ask;
      metrics.quote_time_msc=selected_tick.time_msc;
      metrics.quote_quality=(connected && clock_valid && now_ms-selected_tick.time_msc>=-2000 && now_ms-selected_tick.time_msc<=30000 ? 2 : 1);
      metrics.stop_valid=JPWFinitePositive(rows[selected].sl);
      metrics.stop_reason=(metrics.stop_valid ? "SL informado do item selecionado; não garante execução" : "Item selecionado sem SL válido");
     }
   else metrics.stop_reason="Cotação ou precisão do símbolo selecionado indisponível";
   string factor_key="";
   if(units && JPWRaizNFactorKey(capture.account.server,capture.account.login,capture.account.currency,divisor,
      TerminalInfoString(TERMINAL_DATA_PATH),symbol,factor_key))
     {
      JPWRaizNFactorPreference preference; string factor_reason="";
      const JPW_RAIZN_STATE state=JPWRaizNFactorLoad(JPW_RAIZN_FOLDER,factor_key,symbol,preference,factor_reason);
      if(state==JPW_RAIZN_VALID || state==JPW_RAIZN_ABSENT)
        {
         metrics.factor=(state==JPW_RAIZN_VALID ? preference.factor : JPW_RAIZN_FACTOR_DEFAULT);
         const string root_context=capture.context+"|"+JPWProfileFrame(symbol);
         if(g_signal_root_context!=root_context || g_signal_root_symbol!=symbol || g_signal_atr_handle==INVALID_HANDLE)
           {
            if(g_signal_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_signal_atr_handle);
            g_signal_root_context=root_context; g_signal_root_symbol=symbol;
            g_signal_atr_handle=iATR(symbol,PERIOD_H4,55); JPWRaizNLiveResetCache(g_signal_root_cache);
            MqlTick initial; g_signal_tick_baseline=(SymbolInfoTick(symbol,initial) ? initial.time_msc : 0);
            g_signal_new_tick=false; g_signal_root_connected=connected;
           }
         JPWSignalRootProvider provider;
         provider.Configure(symbol,g_signal_atr_handle,connected,clock_valid,now_ms,30000);
         JPWRaizNLiveSample sample;
         if(JPWRaizNReadLiveBase(provider,g_signal_root_cache,root_context,sample))
           {
            if(connected!=g_signal_root_connected || sample.quote_time_msc<g_signal_tick_baseline)
              { g_signal_root_connected=connected; g_signal_tick_baseline=sample.quote_time_msc; g_signal_new_tick=false; }
            if(g_signal_tick_baseline<=0) { g_signal_tick_baseline=sample.quote_time_msc; g_signal_new_tick=false; }
            if(sample.quote_time_msc>g_signal_tick_baseline) g_signal_new_tick=true;
            const datetime reference=(datetime)((clock_valid ? now_ms : sample.quote_time_msc)/1000);
            JPWHorizonResult horizon; double distance=0;
            if(JPWSignalBudget(started) && JPWHorizonResolve(symbol,reference,horizon) &&
               JPWRaizNCalculate(sample.p0,sample.atr,horizon.n_1w,metrics.factor,distance,metrics.root_1w)==JPW_RAIZN_OK &&
               JPWRaizNCalculate(sample.p0,sample.atr,horizon.n_2w,metrics.factor,distance,metrics.root_2w)==JPW_RAIZN_OK)
              {
               metrics.root_valid=true; metrics.n_1w=horizon.n_1w; metrics.n_2w=horizon.n_2w;
               metrics.atr=sample.atr; metrics.atr_bar_time=(long)sample.bar_time;
               metrics.bid=provider.sampled_bid; metrics.ask=provider.sampled_ask;
               metrics.quote_time_msc=sample.quote_time_msc;
               metrics.quote_quality=(sample.current && g_signal_new_tick ? 2 : 1);
               metrics.root_quality=(sample.current && g_signal_new_tick && horizon.status_1w==JPW_HORIZON_EXACT && horizon.status_2w==JPW_HORIZON_EXACT ? 2 : 1);
               metrics.root_reason=(metrics.root_quality==2 ? "Cotação, ATR e calendário confirmados" : "Raiz N diagnóstica Estimated; "+horizon.reason_1w);
              }
            else metrics.root_reason="Calendário ou cálculo Raiz N indisponível";
           }
         else metrics.root_reason=sample.reason;
        }
      else metrics.root_reason="F indisponível: "+factor_reason+"; sem fallback silencioso";
     }
   else metrics.root_reason="Contexto F da conta/símbolo indisponível";
   if(!JPWSignalRevalidate(capture,rows,reason,started)) { JPWSignalClearMetrics(metrics); return(false); }
   reason="Métricas coletadas; estados e motivos mantidos por métrica";
   return(true);
  }
#endif

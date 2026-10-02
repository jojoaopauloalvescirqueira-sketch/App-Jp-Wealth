#ifndef JPW_ALAVANCAGEM_POSITIONS_MQH
#define JPW_ALAVANCAGEM_POSITIONS_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Samples.mqh>
// Runtime-only accepted inventory. No EA dependency, financial persistence,
// orders, or collection from rendering. Leverage is a gross-notional/equity
// contribution, computed by the existing production core on frozen inputs.
struct JPWPositionView
  {
   ulong ticket;
   long identifier;
   string symbol;
   long direction;
   double volume;
   int volume_digits;
   long opened_msc;
   long updated_msc;
   double entry;
   double sl;
   double tp;
   bool entry_valid;
   bool sl_valid;
   bool tp_valid;
   double leverage;
   bool leverage_valid;
   int quality; // 0 N/A, 1 Current, 2 Estimated: presentation quality contract.
   long source_time_msc;
   string reason;
  };
struct JPWPositionsView
  {
   bool catalog_valid;
   bool leverage_valid;
   string context_key;
   string account_key; // Opaque installation/account key; distinct from chart context.
   string reason;
   long sample_id;
   long observed_utc;
   long source_time_msc;
   long margin_mode;
   ulong accepted_monotonic_ms;
   ulong valid_until_monotonic_ms;
   double total_leverage;
   double equity; // Normalized fiat unit, identical to leverage denominator.
   int quality;
  };
JPWPositionView g_position_views[],g_position_pending[];
JPWPositionsView g_positions_view;
string g_position_pending_context="",g_position_pending_account_key="",g_position_math_reason="";
double g_position_candidate_gross[];
double g_position_pending_equity=0.0,g_position_pending_total=0.0;
long g_position_pending_margin_mode=-1;
bool g_position_pending_leverage=false,g_positions_catalog_attempted=false;

void JPWPositionsClearRow(JPWPositionView &row)
  {
   row.ticket=0; row.identifier=0; row.symbol=""; row.direction=-1;
   row.volume=0.0; row.volume_digits=0; row.opened_msc=0; row.updated_msc=0;
   row.entry=0.0; row.sl=0.0; row.tp=0.0;
   row.entry_valid=false; row.sl_valid=false; row.tp_valid=false;
   row.leverage=0.0; row.leverage_valid=false; row.quality=0;
   row.source_time_msc=0; row.reason="Leverage ainda não confirmada";
  }
void JPWPositionsDiscardPending()
  {
   ArrayResize(g_position_pending,0); ArrayResize(g_position_candidate_gross,0);
   g_position_pending_context=""; g_position_pending_account_key=""; g_position_pending_equity=0.0; g_position_pending_total=0.0;
   g_position_pending_margin_mode=-1; g_position_pending_leverage=false;
   g_position_math_reason="";
  }
void JPWPositionsInvalidate(const string reason)
  {
   ArrayResize(g_position_views,0); JPWPositionsDiscardPending();
   g_positions_view.catalog_valid=false; g_positions_view.leverage_valid=false;
   g_positions_view.context_key=""; g_positions_view.account_key=""; g_positions_view.reason=reason;
   g_positions_view.sample_id=0; g_positions_view.observed_utc=0;
   g_positions_view.source_time_msc=0; g_positions_view.margin_mode=-1;
   g_positions_view.accepted_monotonic_ms=0;
   g_positions_view.valid_until_monotonic_ms=0;
   g_positions_view.total_leverage=0.0; g_positions_view.equity=0.0;
   g_positions_view.quality=0;
  }
bool JPWPositionsViewCurrent(const string context,const ulong now)
  {
   return(g_positions_view.catalog_valid && context!="" &&
      g_positions_view.context_key==context && g_positions_view.sample_id>0 &&
      now>=g_positions_view.accepted_monotonic_ms &&
      now<=g_positions_view.valid_until_monotonic_ms);
  }
int JPWPositionsViewFind(const ulong ticket,const long identifier)
  {
   for(int i=0;i<ArraySize(g_position_views);i++)
      if(g_position_views[i].ticket==ticket &&
         g_position_views[i].identifier==identifier) return(i);
   return(-1);
  }
bool JPWPositionsNear(const double a,const double b)
  {
   if(!MathIsValidNumber(a) || !MathIsValidNumber(b)) return(false);
   return(a==b || MathAbs(a-b)<=1e-10*MathMax(MathAbs(a),MathAbs(b)));
  }
bool JPWPositionsMetadataEqual(JPWPositionView &a[],JPWPositionView &b[])
  {
   if(ArraySize(a)!=ArraySize(b)) return(false);
   for(int i=0;i<ArraySize(a);i++)
     {
      int match=-1;
      for(int j=0;j<ArraySize(b);j++)
         if(a[i].ticket==b[j].ticket && a[i].identifier==b[j].identifier)
           { if(match>=0) return(false); match=j; }
      if(match<0) return(false);
      JPWPositionView x=a[i],y=b[match];
      if(x.symbol!=y.symbol || x.direction!=y.direction || x.volume!=y.volume ||
         x.volume_digits!=y.volume_digits || x.opened_msc!=y.opened_msc ||
         x.updated_msc!=y.updated_msc || x.entry_valid!=y.entry_valid ||
         x.sl_valid!=y.sl_valid || x.tp_valid!=y.tp_valid ||
         (x.entry_valid && x.entry!=y.entry) || (x.sl_valid && x.sl!=y.sl) ||
         (x.tp_valid && x.tp!=y.tp)) return(false);
     }
   return(true);
  }
bool JPWPositionsMatchSnapshot(JPWPositionView &rows[],JPWPosition &positions[])
  {
   if(ArraySize(rows)!=ArraySize(positions)) return(false);
   for(int i=0;i<ArraySize(positions);i++)
     {
      if(positions[i].ticket==0 || positions[i].identifier<=0 || positions[i].symbol=="" ||
         !JPWFinitePositive(positions[i].volume) ||
         (positions[i].direction!=POSITION_TYPE_BUY && positions[i].direction!=POSITION_TYPE_SELL)) return(false);
      for(int j=0;j<i;j++)
         if(positions[j].ticket==positions[i].ticket || positions[j].identifier==positions[i].identifier)
            return(false);
      int matches=0;
      for(int j=0;j<ArraySize(rows);j++)
         if(rows[j].ticket==positions[i].ticket && rows[j].identifier==positions[i].identifier &&
            rows[j].symbol==positions[i].symbol && rows[j].direction==positions[i].direction &&
            rows[j].volume==positions[i].volume) matches++;
      if(matches!=1) return(false);
     }
   return(true);
  }
JPW_RESULT JPWPositionsOneGross(JPWPosition &position,JPWInstrument &instrument,
   JPWQuote &quotes[],const string target,const long now_ms,const int max_age_sec,
   const bool clock_valid,const bool connected,const double scale,JPWRoute &routes[],double &gross)
  {
   JPWPosition positions[]; JPWInstrument instruments[]; double scales[];
   gross=0.0;
   if(ArrayResize(positions,1)!=1 || ArrayResize(instruments,1)!=1 || ArrayResize(scales,1)!=1)
      return(JPW_CALC_ERROR);
   positions[0]=position; instruments[0]=instrument; scales[0]=scale;
   bool estimated=false; long oldest=0;
   return(JPWGrossReading(positions,instruments,quotes,target,now_ms,max_age_sec,
      clock_valid,connected,scales,routes,gross,estimated,oldest));
  }

// Pure production-core reuse: a single-position view of the SAME specifications,
// quotes, scales and valid routes used for the accepted account gross. This
// neither reads prices again nor uses SL, equity, margin or trading functions.
JPW_RESULT JPWPositionsGrossBreakdown(JPWPosition &positions[],JPWInstrument &instruments[],
   JPWQuote &quotes[],const string target,const long now_ms,const int max_age_sec,
   const bool clock_valid,const bool connected,double &scales[],JPWRoute &routes[],
   const double expected_gross,double &amounts[])
  {
   ArrayResize(amounts,0);
   const int n=ArraySize(positions);
   if(n!=ArraySize(instruments) || n!=ArraySize(scales) ||
      !MathIsValidNumber(expected_gross) || expected_gross<0.0)
      return(JPW_CALC_ERROR);
   double candidate[];
   if(ArrayResize(candidate,n)!=n) return(JPW_CALC_ERROR);
   JPWRoute frozen_routes[];
   if(ArrayResize(frozen_routes,ArraySize(routes))!=ArraySize(routes)) return(JPW_CALC_ERROR);
   for(int j=0;j<ArraySize(routes);j++) frozen_routes[j]=routes[j];
   double complete=0.0;
   for(int i=0;i<n;i++)
     {
      for(int j=0;j<i;j++) if(positions[j].ticket==positions[i].ticket) return(JPW_CALC_ERROR);
      JPWPosition position[]; JPWInstrument instrument[]; double scale[];
      if(ArrayResize(position,1)!=1 || ArrayResize(instrument,1)!=1 || ArrayResize(scale,1)!=1)
         return(JPW_CALC_ERROR);
      position[0]=positions[i]; instrument[0]=instruments[i]; scale[0]=scales[i];
      bool estimated=false; long oldest=0; double gross=0.0;
      const JPW_RESULT result=JPWGrossReading(position,instrument,quotes,target,now_ms,max_age_sec,
         clock_valid,connected,scale,frozen_routes,gross,estimated,oldest);
      if(result!=JPW_OK) return(result);
      candidate[i]=gross; complete+=gross;
      if(!MathIsValidNumber(complete)) return(JPW_CALC_ERROR);
     }
   if(!JPWPositionsNear(complete,expected_gross)) return(JPW_CALC_ERROR);
   if(ArrayResize(amounts,n)!=n) return(JPW_CALC_ERROR);
   for(int i=0;i<n;i++) amounts[i]=candidate[i];
   return(JPW_OK);
  }
bool JPWPositionsStageCatalog(JPWPositionView &rows[],JPWPosition &positions[],
   const string context,const long margin_mode,const string account_key="")
  {
   // Exact resize is essential: native ArrayCopy does not shrink its destination.
   if(context=="" || !JPWPositionsMatchSnapshot(rows,positions) ||
      ArrayResize(g_position_pending,ArraySize(positions))!=ArraySize(positions))
     { JPWPositionsDiscardPending(); return(false); }
   for(int i=0;i<ArraySize(positions);i++)
      for(int j=0;j<ArraySize(rows);j++)
         if(rows[j].ticket==positions[i].ticket && rows[j].identifier==positions[i].identifier)
           { g_position_pending[i]=rows[j]; break; }
   g_position_pending_context=context; g_position_pending_account_key=account_key; g_position_pending_margin_mode=margin_mode;
   g_position_pending_leverage=false; g_position_pending_equity=0.0; g_position_pending_total=0.0;
   return(true);
  }
bool JPWPositionsStageLeverage(const double equity,const double expected_leverage,
                               double &amounts[])
  {
   g_position_pending_leverage=false;
   if(g_position_pending_context=="" || !JPWFinitePositive(equity) ||
      !MathIsValidNumber(expected_leverage) || expected_leverage<0.0 ||
      ArraySize(amounts)!=ArraySize(g_position_pending)) return(false);
   double complete=0.0;
   for(int i=0;i<ArraySize(amounts);i++)
     {
      double value=0.0;
      if(JPWLeverage(amounts[i],equity,value)!=JPW_OK) return(false);
      g_position_pending[i].leverage=value;
      complete+=value;
     }
   if(!JPWPositionsNear(complete,expected_leverage)) return(false);
   g_position_pending_equity=equity; g_position_pending_total=expected_leverage; g_position_pending_leverage=true;
   return(true);
  }
bool JPWPositionsPublish(JPWMetricSample &sample,const string unavailable_reason)
  {
   if(g_position_pending_context=="" || sample.context_key!=g_position_pending_context || sample.id<=0 ||
      ArrayResize(g_position_views,ArraySize(g_position_pending))!=ArraySize(g_position_pending))
     { JPWPositionsInvalidate("Catálogo não confirmado neste ciclo"); return(false); }
   const bool financial_valid=(g_position_pending_leverage && sample.valid && sample.has_value &&
      sample.quality!=0 && JPWFinitePositive(g_position_pending_equity) &&
      JPWPositionsNear(g_position_pending_total,sample.numeric_value));
   for(int i=0;i<ArraySize(g_position_pending);i++)
     {
      g_position_views[i]=g_position_pending[i];
      g_position_views[i].leverage_valid=financial_valid;
      g_position_views[i].quality=(financial_valid ? sample.quality : 0);
      g_position_views[i].source_time_msc=sample.source_time_msc;
      g_position_views[i].reason=(financial_valid ? "Nocional bruto / equity da mesma leitura" : unavailable_reason);
      if(!financial_valid) g_position_views[i].leverage=0.0;
     }
   g_positions_view.catalog_valid=true; g_positions_view.leverage_valid=financial_valid;
   g_positions_view.context_key=sample.context_key; g_positions_view.account_key=g_position_pending_account_key; g_positions_view.sample_id=sample.id;
   g_positions_view.observed_utc=sample.observed_utc;
   g_positions_view.source_time_msc=sample.source_time_msc;
   g_positions_view.margin_mode=g_position_pending_margin_mode;
   g_positions_view.accepted_monotonic_ms=sample.accepted_monotonic_ms;
   g_positions_view.valid_until_monotonic_ms=sample.valid_until_monotonic_ms;
   g_positions_view.total_leverage=(financial_valid ? sample.numeric_value : 0.0);
   g_positions_view.equity=(financial_valid ? g_position_pending_equity : 0.0);
   g_positions_view.quality=(financial_valid ? sample.quality : 0);
   g_positions_view.reason=(financial_valid ? "Contribuições reconciliadas com Leverage da conta" : unavailable_reason);
   JPWPositionsDiscardPending(); return(true);
  }
// Read-only MT5 metadata adapter, called exclusively by the coordinator timer.
// Failed SL/TP/entry reads affect their overlays, never the inventory or notional.
bool JPWPositionsOptionalPrice(const ENUM_POSITION_PROPERTY_DOUBLE property,double &value)
  {
   value=0.0; ResetLastError(); double read=0.0;
   const bool valid=(PositionGetDouble(property,read) && GetLastError()==0 &&
                     MathIsValidNumber(read) && read>=0.0);
   if(valid) value=read;
   return(valid);
  }
bool JPWPositionsReadMetadata(JPWPositionView &rows[],const ulong started,string &reason,const ulong max_elapsed=400)
  {
   ArrayResize(rows,0); reason="";
   const int count=PositionsTotal();
   if(count<0 || count>512 || ArrayResize(rows,count)!=count)
     { reason="Inventário acima do limite ou indisponível"; return(false); }
   for(int i=0;i<count;i++)
     {
      const ulong now=GetTickCount64();
      if(now<started || now-started>=max_elapsed)
        { reason="Coleta de posições adiada pelo orçamento do ciclo"; ArrayResize(rows,0); return(false); }
      JPWPositionView row; JPWPositionsClearRow(row);
      row.ticket=PositionGetTicket(i);
      if(row.ticket==0 || !PositionSelectByTicket(row.ticket))
        { reason="Posição alterada durante a leitura"; ArrayResize(rows,0); return(false); }
      if(!PositionGetInteger(POSITION_IDENTIFIER,row.identifier) || row.identifier<=0 ||
         !PositionGetInteger(POSITION_TYPE,row.direction) ||
         (row.direction!=POSITION_TYPE_BUY && row.direction!=POSITION_TYPE_SELL) ||
         !PositionGetString(POSITION_SYMBOL,row.symbol) || row.symbol=="" ||
         !PositionGetDouble(POSITION_VOLUME,row.volume) || !JPWFinitePositive(row.volume) ||
         !PositionGetInteger(POSITION_TIME_MSC,row.opened_msc) || row.opened_msc<=0 ||
         !PositionGetInteger(POSITION_TIME_UPDATE_MSC,row.updated_msc) || row.updated_msc<=0)
        { reason="Metadados da posição não confirmados"; ArrayResize(rows,0); return(false); }
      double step=0.0;
      if(!SymbolInfoDouble(row.symbol,SYMBOL_VOLUME_STEP,step) || !JPWFinitePositive(step))
        { reason="Precisão de volume não confirmada"; ArrayResize(rows,0); return(false); }
      double scaled=step;
      while(row.volume_digits<8 && MathAbs(scaled-MathRound(scaled))>1e-9)
        { scaled*=10.0; row.volume_digits++; }
      if(MathAbs(scaled-MathRound(scaled))>1e-9)
        { reason="Precisão de volume não suportada"; ArrayResize(rows,0); return(false); }
      row.entry_valid=JPWPositionsOptionalPrice(POSITION_PRICE_OPEN,row.entry) && row.entry>0.0;
      row.sl_valid=JPWPositionsOptionalPrice(POSITION_SL,row.sl);
      row.tp_valid=JPWPositionsOptionalPrice(POSITION_TP,row.tp);
      for(int j=0;j<i;j++)
         if(rows[j].ticket==row.ticket || rows[j].identifier==row.identifier)
           { reason="Identidade de posição ambígua"; ArrayResize(rows,0); return(false); }
      rows[i]=row;
     }
   return(true);
  }
#endif

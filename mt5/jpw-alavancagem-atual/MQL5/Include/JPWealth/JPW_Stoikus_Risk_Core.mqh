#ifndef JPW_GENETRIX_RISK_CORE_MQH
#define JPW_GENETRIX_RISK_CORE_MQH
#include <JPWealth/JPW_Alavancagem_Core.mqh>

// Human-approved additional breaker. NOT a V11 controller or admission certificate.
// Pure planning/state transitions: no terminal, storage, time or trading access.
#define JPW_RISK_SCHEMA 1
#define JPW_RISK_POLICY "gross-equity-7-lifo-whole-hedging-v1"
#define JPW_RISK_LIMIT 7.0
enum JPWRiskActionKind { JPW_RISK_NONE=0, JPW_RISK_CANCEL=1, JPW_RISK_CLOSE=2 };
enum JPWRiskPhase { JPW_RISK_OBSERVE=0, JPW_RISK_READY, JPW_RISK_UNKNOWN,
                    JPW_RISK_REMAINDER, JPW_RISK_PAUSED_LIFO };
enum JPWRiskOutcome { JPW_RISK_UNCERTAIN=0, JPW_RISK_CONFIRMED, JPW_RISK_REFUSED,
                      JPW_RISK_PARTIAL };
struct JPWRiskPosition
  {
   ulong ticket;
   long identifier;
   long opened_msc;
   string symbol;
   long direction;
   double volume;
   double gross;
  };
struct JPWRiskPending
  {
   ulong ticket;
   long setup_msc;
   string symbol;
   long type;
   double volume;
   double entry;
   double trigger;
   double gross;
  };
struct JPWRiskSnapshot
  {
   bool valid;
   bool current;
   bool pending_valid;
   bool hedging;
   bool fifo;
   double equity;
   double gross;
   double leverage;
   double pending_gross;
   double projected_leverage;
   long observed_utc;
  };
struct JPWRiskAction
  {
   JPWRiskActionKind kind;
   ulong ticket;
   long identifier;
   string symbol;
   long direction;
   double volume;
  };
struct JPWRiskMachine
  {
   JPWRiskPhase phase;
   bool armed;
   bool cancel_refused;
   bool protection_incomplete;
   JPWRiskAction active;
   ulong request_order;
   ulong request_deal;
   uint request_id;
   uint retcode;
   string nonce;
   long submitted_utc;
   double executed_volume;
  };
// Normalized immutable history evidence. Adapter maps IN/OUT/OUT_BY explicitly;
// reversal/canceled-deal corrections are unavailable, never silently counted.
enum JPWRiskEvidenceEntry { JPW_RISK_EVIDENCE_IN=0,JPW_RISK_EVIDENCE_OUT=1,
                            JPW_RISK_EVIDENCE_OUT_BY=2 };
struct JPWRiskDealEvidence
  {
   ulong ticket;
   ulong order_ticket;
   long position_identifier;
   string symbol;
   long direction;
   int entry;
   double volume;
  };

// The selected history must cover this position's complete execution chain.
// Require an opening deal linked to the original pending order, then reconcile
// all signed volumes with the observed identifier (or a positively closed chain).
bool JPWRiskEntryFillLinked(const ulong order_ticket,const long identifier,
                            const string symbol,const long direction,const double expected_fill,
                            JPWRiskDealEvidence &deals[],JPWRiskPosition &positions[])
  {
   if(order_ticket==0 || identifier<=0 || symbol=="" || !JPWFinitePositive(expected_fill) ||
      (direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL)) return(false);
   double linked=0.0,opened=0.0,closed=0.0;
   for(int i=0;i<ArraySize(deals);i++)
     {
      JPWRiskDealEvidence deal=deals[i];
      if(deal.ticket==0 || deal.order_ticket==0 || deal.position_identifier!=identifier ||
         deal.symbol!=symbol || !JPWFinitePositive(deal.volume) ||
         (deal.direction!=POSITION_TYPE_BUY && deal.direction!=POSITION_TYPE_SELL)) return(false);
      for(int j=0;j<i;j++) if(deals[j].ticket==deal.ticket) return(false);
      if(deal.entry==JPW_RISK_EVIDENCE_IN)
        {
         if(deal.direction!=direction) return(false);
         opened+=deal.volume;
         if(deal.order_ticket==order_ticket) linked+=deal.volume;
        }
      else if(deal.entry==JPW_RISK_EVIDENCE_OUT || deal.entry==JPW_RISK_EVIDENCE_OUT_BY)
        {
         if(deal.direction==direction || deal.order_ticket==order_ticket) return(false);
         closed+=deal.volume;
        }
      else return(false);
     }
   const double tolerance=1e-10*MathMax(1.0,expected_fill);
   if(!MathIsValidNumber(linked) || !MathIsValidNumber(opened) || !MathIsValidNumber(closed) ||
      MathAbs(linked-expected_fill)>tolerance || opened<expected_fill-tolerance ||
      closed>opened+tolerance) return(false);
   const double remaining=MathMax(0.0,opened-closed);
   int matching=0;
   for(int i=0;i<ArraySize(positions);i++)
      if(positions[i].identifier==identifier)
        {
         if(positions[i].ticket==0 || positions[i].symbol!=symbol || positions[i].direction!=direction ||
            !JPWFinitePositive(positions[i].volume) || MathAbs(positions[i].volume-remaining)>tolerance)
            return(false);
         matching++;
        }
   if(matching==1) return(true);
   return(matching==0 && closed>0.0 && remaining<=tolerance);
  }

void JPWRiskClearAction(JPWRiskAction &action)
  { action.kind=JPW_RISK_NONE; action.ticket=0; action.identifier=0; action.symbol="";
    action.direction=-1; action.volume=0.0; }
void JPWRiskReset(JPWRiskMachine &machine)
  {
   machine.phase=JPW_RISK_OBSERVE; machine.armed=false; machine.cancel_refused=false;
   machine.protection_incomplete=false; JPWRiskClearAction(machine.active);
   machine.request_order=0; machine.request_deal=0; machine.request_id=0;
   machine.retcode=0; machine.nonce=""; machine.submitted_utc=0; machine.executed_volume=0.0;
  }
bool JPWRiskLaterPosition(JPWRiskPosition &a,JPWRiskPosition &b)
  { return(a.opened_msc>b.opened_msc ||
           (a.opened_msc==b.opened_msc && a.identifier>b.identifier)); }
bool JPWRiskLaterPending(JPWRiskPending &a,JPWRiskPending &b)
  { return(a.setup_msc>b.setup_msc || (a.setup_msc==b.setup_msc && a.ticket>b.ticket)); }

// Conditional future own-symbol entry quote, frozen OTHER FX quotes, frozen equity.
// Use the canonical gross function; force own FX leg so a cached market route cannot
// silently turn EURUSD entry 1.20 into current EURUSD 1.10. Three-leg routes remain N/A.
bool JPWRiskGrossAtEntry(JPWPosition &row,JPWInstrument &instrument,JPWQuote &quotes[],
                         const string target,const double entry,const double scale,
                         const long now_ms,const bool clock_valid,const bool connected,
                         JPWRoute &market_routes[],double &gross,bool &estimated)
  {
   JPW_MODEL model=JPW_MODEL_NONE;
   if(!JPWFinitePositive(entry) || JPWClassify(instrument,model)!=JPW_OK) return(false);
   JPWQuote scenario[]; JPWRoute routes[];
   if(ArrayResize(scenario,ArraySize(quotes))!=ArraySize(quotes) ||
      ArrayResize(routes,ArraySize(market_routes))!=ArraySize(market_routes)) return(false);
   for(int i=0;i<ArraySize(quotes);i++) scenario[i]=quotes[i];
   for(int i=0;i<ArraySize(market_routes);i++) routes[i]=market_routes[i];
   const int own=JPWQuoteIndex(scenario,row.symbol); if(own<0) return(false);
   scenario[own].bid=entry; scenario[own].ask=entry;
   if(model==JPW_MODEL_FIAT_FOREX && instrument.base!=target)
     {
      JPWRoute forced;
      forced.valid=true; forced.source=instrument.base; forced.target=target;
      forced.intermediate=""; forced.first_symbol=row.symbol; forced.first_direction=1;
      forced.second_symbol=""; forced.second_direction=0;
      if(instrument.profit!=target)
        {
         JPWRoute previous,conversion; previous.valid=false;
         double rate=0.0; bool conversion_estimated=false; long oldest=0;
         if(!JPWFindRouteReading(instrument.profit,target,quotes,now_ms,30,clock_valid,connected,
             previous,conversion,rate,conversion_estimated,oldest) || conversion.second_symbol!="" ||
             conversion.first_symbol==row.symbol || conversion.first_symbol=="") return(false);
         forced.intermediate=instrument.profit; forced.second_symbol=conversion.first_symbol;
         forced.second_direction=conversion.first_direction;
         if(conversion_estimated) estimated=true;
        }
      int index=-1;
      for(int i=0;i<ArraySize(routes);i++)
         if(routes[i].source==forced.source && routes[i].target==target) index=i;
      if(index<0) { index=ArraySize(routes); if(ArrayResize(routes,index+1)!=index+1) return(false); }
      routes[index]=forced;
     }
   JPWPosition rows[]; JPWInstrument specifications[]; double scales[];
   if(ArrayResize(rows,1)!=1 || ArrayResize(specifications,1)!=1 || ArrayResize(scales,1)!=1)
      return(false);
   rows[0]=row; specifications[0]=instrument; scales[0]=scale;
   bool row_estimated=false; long oldest=0;
   if(JPWGrossReading(rows,specifications,scenario,target,now_ms,30,clock_valid,connected,
                       scales,routes,gross,row_estimated,oldest)!=JPW_OK) return(false);
   if(row_estimated) estimated=true;
   return(true);
  }

bool JPWRiskValidateSnapshot(JPWRiskSnapshot &sample,JPWRiskPosition &positions[],
                             JPWRiskPending &pending[])
  {
   if(!sample.valid || !sample.pending_valid || !JPWFinitePositive(sample.equity) ||
      !MathIsValidNumber(sample.gross) || sample.gross<0.0 ||
      !MathIsValidNumber(sample.pending_gross) || sample.pending_gross<0.0) return(false);
   double opened=0.0, reserved=0.0;
   for(int i=0;i<ArraySize(positions);i++)
     {
      if(positions[i].ticket==0 || positions[i].identifier<=0 || positions[i].opened_msc<=0 ||
         positions[i].symbol=="" || !JPWFinitePositive(positions[i].volume) ||
         !JPWFinitePositive(positions[i].gross) ||
         (positions[i].direction!=POSITION_TYPE_BUY && positions[i].direction!=POSITION_TYPE_SELL)) return(false);
      for(int j=0;j<i;j++)
         if(positions[j].ticket==positions[i].ticket ||
            positions[j].identifier==positions[i].identifier) return(false);
      opened+=positions[i].gross;
     }
   for(int i=0;i<ArraySize(pending);i++)
     {
      if(pending[i].ticket==0 || pending[i].setup_msc<=0 || pending[i].symbol=="" ||
         !JPWFinitePositive(pending[i].volume) || !JPWFinitePositive(pending[i].entry) ||
         !JPWFinitePositive(pending[i].gross)) return(false);
      for(int j=0;j<i;j++) if(pending[j].ticket==pending[i].ticket) return(false);
      reserved+=pending[i].gross;
     }
   // Tolerance only checks arithmetic reconciliation; never changes the 7x trigger.
   if(!MathIsValidNumber(opened) || !MathIsValidNumber(reserved) ||
      MathAbs(opened-sample.gross)>1e-10*MathMax(1.0,sample.gross) ||
      MathAbs(reserved-sample.pending_gross)>1e-10*MathMax(1.0,sample.pending_gross)) return(false);
   double actual=0.0, projected=0.0;
   return(JPWLeverage(sample.gross,sample.equity,actual)==JPW_OK &&
          JPWLeverage(sample.gross+sample.pending_gross,sample.equity,projected)==JPW_OK &&
          actual==sample.leverage && projected==sample.projected_leverage);
  }

// Returns the next member of the minimal newest-first cancellation prefix.
// A new complete snapshot is mandatory after EACH outcome. It is not a future-price guarantee.
bool JPWRiskPlan(JPWRiskSnapshot &sample,JPWRiskPosition &positions[],JPWRiskPending &pending[],
                 JPWRiskMachine &machine,JPWRiskAction &next,string &reason)
  {
   JPWRiskClearAction(next);
   if(machine.phase==JPW_RISK_UNKNOWN) { reason="ACTION_UNKNOWN_RECONCILE"; return(false); }
   if(machine.phase==JPW_RISK_PAUSED_LIFO) { reason="CLOSE_REFUSED_REARM_REQUIRED"; return(false); }
   if(!sample.hedging) { reason="NETTING_EXECUTION_NA"; return(false); }
   if(sample.fifo) { reason="FIFO_LIFO_CONFLICT"; return(false); }
   if(!sample.current || !JPWRiskValidateSnapshot(sample,positions,pending))
     { reason="DATA_NOT_CURRENT_OR_INCOMPLETE"; return(false); }
   if(machine.phase==JPW_RISK_REMAINDER && machine.active.kind==JPW_RISK_CLOSE)
     {
      for(int i=0;i<ArraySize(positions);i++)
         if(positions[i].identifier==machine.active.identifier)
           {
            if(positions[i].ticket!=machine.active.ticket || positions[i].symbol!=machine.active.symbol ||
               positions[i].direction!=machine.active.direction)
              { reason="REMAINDER_IDENTITY_CHANGED"; return(false); }
            next=machine.active; next.volume=positions[i].volume;
            reason="FINISH_WHOLE_INTENT_REMAINDER"; return(true);
           }
      reason="REMAINDER_ABSENCE_REQUIRES_RECONCILIATION"; return(false);
     }
   const double ceiling=JPW_RISK_LIMIT*sample.equity;
   if(!MathIsValidNumber(ceiling)) { reason="NONFINITE_PENDING_BUDGET"; return(false); }
   const double budget=MathMax(0.0,ceiling-sample.gross);
   if(!machine.cancel_refused && sample.pending_gross>budget)
     {
      int latest=-1;
      for(int i=0;i<ArraySize(pending);i++)
         if(latest<0 || JPWRiskLaterPending(pending[i],pending[latest])) latest=i;
      if(latest<0) { reason="PENDING_AGGREGATE_INCONSISTENT"; return(false); }
      next.kind=JPW_RISK_CANCEL; next.ticket=pending[latest].ticket;
      next.symbol=pending[latest].symbol; next.volume=pending[latest].volume;
      reason="CANCEL_MINIMAL_LIFO_PREFIX"; return(true);
     }
   if(sample.leverage>JPW_RISK_LIMIT)
     {
      int latest=-1;
      for(int i=0;i<ArraySize(positions);i++)
         if(latest<0 || JPWRiskLaterPosition(positions[i],positions[latest])) latest=i;
      if(latest<0) { reason="OPEN_AGGREGATE_INCONSISTENT"; return(false); }
      next.kind=JPW_RISK_CLOSE; next.ticket=positions[latest].ticket;
      next.identifier=positions[latest].identifier; next.symbol=positions[latest].symbol;
      next.direction=positions[latest].direction; next.volume=positions[latest].volume;
      reason=(machine.cancel_refused ? "CLOSE_LIFO_PROTECTION_INCOMPLETE" : "CLOSE_WHOLE_LIFO");
      return(true);
     }
   reason=(machine.cancel_refused ? "WITHIN_7_PENDING_PROTECTION_INCOMPLETE" : "WITHIN_7_STATIC_PROJECTION");
   return(true);
  }

bool JPWRiskBegin(JPWRiskMachine &machine,JPWRiskAction &action,const string nonce,const long now)
  {
   if(!machine.armed || machine.phase==JPW_RISK_UNKNOWN || machine.phase==JPW_RISK_PAUSED_LIFO ||
      action.kind==JPW_RISK_NONE || action.ticket==0 || nonce=="" || now<=0) return(false);
   machine.active=action; machine.phase=JPW_RISK_UNKNOWN; machine.nonce=nonce;
   machine.submitted_utc=now; machine.request_order=0; machine.request_deal=0;
   machine.request_id=0; machine.retcode=0; machine.executed_volume=0.0;
   return(true);
  }
void JPWRiskApplyOutcome(JPWRiskMachine &machine,const JPWRiskOutcome outcome,const double executed)
  {
   machine.executed_volume=executed;
   if(outcome==JPW_RISK_UNCERTAIN) { machine.phase=JPW_RISK_UNKNOWN; return; }
   if(outcome==JPW_RISK_REFUSED)
     {
      machine.protection_incomplete=true;
      if(machine.active.kind==JPW_RISK_CLOSE)
         { machine.phase=JPW_RISK_PAUSED_LIFO; machine.armed=false; }
      else { machine.cancel_refused=true; machine.phase=JPW_RISK_READY; JPWRiskClearAction(machine.active); }
      return;
     }
   if(outcome==JPW_RISK_PARTIAL && machine.active.kind==JPW_RISK_CLOSE)
     { machine.phase=JPW_RISK_REMAINDER; return; }
   machine.phase=(machine.armed ? JPW_RISK_READY : JPW_RISK_OBSERVE);
   JPWRiskClearAction(machine.active);
  }
#endif

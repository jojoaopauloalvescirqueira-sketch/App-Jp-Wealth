#ifndef JPW_GENETRIX_OBSERVER_RUNTIME_MQH
#define JPW_GENETRIX_OBSERVER_RUNTIME_MQH
#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh>
#include <JPWealth/JPW_Alavancagem_StopRisk_Store.mqh>
#include <JPWealth/JPW_Alavancagem_Diagnostics.mqh>
#include <JPWealth/JPW_PersonalHistory_Controller.mqh>

// Uma instancia em qualquer grafico observa os negocios da conta inteira.
// Nenhuma funcao de negociacao e chamada. Eventos apenas entram na fila;
// leitura de historico, ATR e escrita SQLite ocorrem no timer.
#define JPW_OBSERVER_QUEUE_MAX 64
#define JPW_OBSERVER_MAX_ATTEMPTS 60

struct JPWObserverPending
  {
   ulong ticket;
   int attempts;
   long arrival_utc; // Callback time on the local computer.
   ulong arrival_ms; // Monotonic elapsed-time reference.
   bool connected_at_arrival;
  };

JPWObserverPending g_pending[];
string g_account_key="";
int g_db=INVALID_HANDLE;
bool g_reconstruct_open_positions=false;
bool g_queue_overflow=false;
ulong g_next_db_open_ms=0;
string g_risk_account_key="";
string g_risk_publisher_token="";
JPWObserverPresenceState g_risk_presence_state=JPW_OBSERVER_WAITING;
bool g_risk_presence_owned=false;
double g_risk_presence_value=0.0;
bool g_risk_presence_error_reported=false;
ulong g_next_risk_sample_ms=0;
bool g_risk_dirty=true;
bool g_risk_was_active=false;
bool g_risk_lease_owned=false;
double g_risk_lease_value=0.0;
int g_reconstruct_cursor=0;
int g_reconstruct_count=-1;
long g_observer_risk_observed_utc=0,g_observer_risk_observed_mono=0;
long g_observer_raiz_observed_utc=0,g_observer_raiz_observed_mono=0;
long g_observer_personal_observed_utc=0,g_observer_personal_observed_mono=0;
int g_observer_personal_quality=JPW_PERSONAL_UNAVAILABLE;
bool g_observer_runtime_attached=false,g_observer_runtime_conflict=false;
bool g_observer_diagnostic_first=false;
int g_observer_runtime_owner=INVALID_HANDLE;
string g_observer_runtime_reason="";
string g_observer_risk_reason="";
int g_reconstruct_attempts=0;
ulong g_reconstruct_next_ms=0;
bool g_reconstruct_retry_pass=false;
JPWDiagTiming g_observer_timing;
bool g_observer_coverage_incomplete=false;
int g_observer_last_risk_state=-1;
struct JPWObserverDiagnosticPending
  {
   string context;
   int code;
   long sample_id;
   long utc;
   long mono;
  };
JPWObserverDiagnosticPending g_diagnostic_pending[];
bool g_diagnostic_queue_lost=false;
long g_observer_diagnostic_instance=0;

// This buffer contains no trade identifiers or financial values. Writes only
// occur on lifecycle/timer paths, never inside OnTradeTransaction.
void JPWObserverDiagnosticFor(const string context,const int code,const long sample_id=0)
  {
   if(!JPWRaizNIsHash(context)) return;
   if(JPWDiagCreatesCoverageGap(code)) g_observer_coverage_incomplete=true;
   for(int i=0;i<ArraySize(g_diagnostic_pending);i++)
      if(g_diagnostic_pending[i].context==context &&
         g_diagnostic_pending[i].code==code) return;
   const int n=ArraySize(g_diagnostic_pending);
   if(n>=64 || ArrayResize(g_diagnostic_pending,n+1)!=n+1)
     { g_diagnostic_queue_lost=true; return; }
   g_diagnostic_pending[n].context=context;
   g_diagnostic_pending[n].code=code;
   g_diagnostic_pending[n].sample_id=sample_id;
   g_diagnostic_pending[n].utc=(long)TimeGMT();
   g_diagnostic_pending[n].mono=(long)GetTickCount64();
  }
void JPWObserverDiagnostic(const int code,const long sample_id=0)
  { JPWObserverDiagnosticFor(g_account_key,code,sample_id); }
void JPWObserverFlushDiagnostics(const int limit=2)
  {
   if(g_diagnostic_queue_lost && ArraySize(g_diagnostic_pending)<63)
     { g_diagnostic_queue_lost=false;
       JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED); }
   for(int i=0;i<limit && ArraySize(g_diagnostic_pending)>0;i++)
     {
      JPWObserverDiagnosticPending event=g_diagnostic_pending[0];
      string reason="";
      const JPWStoreResult status=JPWDiagRecordAt(event.context,JPW_DIAG_OBSERVER,
         event.code,event.sample_id,event.utc,event.mono,reason);
      if(status!=JPW_STORE_VALID)
        {
         string marker_reason="";
         if(!JPWDiagMarkFailure(event.context,JPW_DIAG_OBSERVER,
                                g_observer_diagnostic_instance,marker_reason))
            Print("JPW diagnostics: ",marker_reason);
         // Keep the original event queued. When writes recover this additional
         // gap is durable as well; cannot promise durability while storage fails.
         if(event.code!=JPW_DIAG_WRITE_FAILED) JPWObserverDiagnosticFor(event.context,JPW_DIAG_WRITE_FAILED);
         Print("JPW diagnostics: ",reason);
         return;
        }
      for(int j=1;j<ArraySize(g_diagnostic_pending);j++)
         g_diagnostic_pending[j-1]=g_diagnostic_pending[j];
      ArrayResize(g_diagnostic_pending,ArraySize(g_diagnostic_pending)-1);
      bool still_pending=g_diagnostic_queue_lost;
      for(int j=0;j<ArraySize(g_diagnostic_pending);j++)
         if(g_diagnostic_pending[j].context==event.context) still_pending=true;
      // Clear only this EA's marker, only after its context queue is drained.
      // Other indicators/EA writers may still have an unresolved write error.
      if(!still_pending)
        {
         string marker_reason="";
         if(!JPWDiagClearFailure(event.context,JPW_DIAG_OBSERVER,
                                 g_observer_diagnostic_instance,marker_reason))
            Print("JPW diagnostics: ",marker_reason);
        }
     }
  }
void JPWObserverScheduleReconstruction()
  {
   g_reconstruct_open_positions=true;
   g_reconstruct_cursor=0;
   g_reconstruct_count=-1;
   g_reconstruct_attempts=0;
   g_reconstruct_next_ms=0;
   g_reconstruct_retry_pass=false;
  }


// A temporary terminal variable proves that the publisher belongs to this
// running MT5 session. Compare-and-set never creates a persistent replacement
// if it vanishes. Its name includes the opaque per-EA publisher token.
bool JPWStopRiskEnsureSessionLease(string &reason)
  {
   reason="";
   if(g_risk_lease_owned) return(true);
   const string name=JPWStopRiskLeaseName(g_risk_publisher_token);
   if(name=="" || GlobalVariableCheck(name) || !GlobalVariableTemp(name))
     { reason="Lease temporaria do EA indisponivel ou nome ocupado";
       return(false); }
   g_risk_lease_owned=true;
   g_risk_lease_value=0.0;
   return(true);
  }

bool JPWStopRiskAdvanceSessionLease(const long observed_mono_ms,
                                    string &reason)
  {
   if(observed_mono_ms<=0 || !JPWStopRiskEnsureSessionLease(reason))
      return(false);
   const string name=JPWStopRiskLeaseName(g_risk_publisher_token);
   if(!GlobalVariableSetOnCondition(name,(double)observed_mono_ms,
                                    g_risk_lease_value))
     { GlobalVariableDel(name); g_risk_lease_owned=false;
       reason="Lease temporaria do EA mudou durante publicacao";
       return(false); }
   g_risk_lease_value=(double)observed_mono_ms;
   return(true);
  }

void JPWStopRiskInvalidateSessionLease()
  {
   if(!g_risk_lease_owned) return;
   const string name=JPWStopRiskLeaseName(g_risk_publisher_token);
   if(!GlobalVariableSetOnCondition(name,0.0,g_risk_lease_value))
     { GlobalVariableDel(name); g_risk_lease_owned=false; }
   g_risk_lease_value=0.0;
  }

void JPWStopRiskReleaseSessionLease()
  {
   JPWStopRiskInvalidateSessionLease();
   if(g_risk_lease_owned)
      GlobalVariableDel(JPWStopRiskLeaseName(g_risk_publisher_token));
   g_risk_lease_owned=false;
   g_risk_lease_value=0.0;
  }

void JPWStopRiskPresenceRefresh()
  {
   if(g_risk_account_key=="" || g_risk_publisher_token=="") return;
   if(!g_risk_presence_owned)
     {
      g_risk_presence_owned=JPWObserverPresenceStartOwned(g_risk_account_key,
                                                         g_risk_publisher_token,
                                                         g_risk_presence_value);
      if(!g_risk_presence_owned)
        {
         if(!g_risk_presence_error_reported)
            Print("JPW observer: sinal temporario de presenca indisponivel");
         g_risk_presence_error_reported=true;
         return;
        }
     }
   if(!JPWObserverPresenceBeatOwned(g_risk_account_key,g_risk_publisher_token,
                                    g_risk_presence_state,g_risk_presence_value))
     {
      // Retry a transient CAS refusal only while our exact previous value is
      // still present. A deleted marker can be recreated on the next timer;
      // a changed value is never adopted or removed as our own.
      if(!JPWObserverPresenceMarkerMatches(g_risk_account_key,
                                           g_risk_publisher_token,
                                           g_risk_presence_value))
        { g_risk_presence_owned=false; g_risk_presence_value=0.0; }
      if(!g_risk_presence_error_reported)
         Print("JPW observer: renovacao do sinal temporario falhou");
      g_risk_presence_error_reported=true;
      return;
     }
   g_risk_presence_error_reported=false;
  }

void JPWStopRiskPresenceSet(const JPWObserverPresenceState state)
  {
   g_risk_presence_state=state;
   JPWStopRiskPresenceRefresh();
  }

void JPWStopRiskPresenceRelease()
  {
   if(g_risk_presence_owned)
      JPWObserverPresenceReleaseOwned(g_risk_account_key,
                                      g_risk_publisher_token,
                                      g_risk_presence_value);
   g_risk_presence_owned=false;
   g_risk_presence_value=0.0;
   g_risk_presence_state=JPW_OBSERVER_WAITING;
   g_risk_presence_error_reported=false;
  }

void JPWStopRiskObservationFailed(const string why)
  {
   g_observer_risk_reason=(why=="" ? "Última observação recusada; captura atual não confirmada" : why);
   JPWStopRiskPresenceSet(JPW_OBSERVER_FAILED);
   g_risk_dirty=true;
   if(g_observer_last_risk_state!=0)
     { JPWObserverDiagnostic(JPW_DIAG_DATA_UNAVAILABLE);
       g_observer_last_risk_state=0; }
   JPWStopRiskInvalidateSessionLease();
   if(g_risk_was_active)
     {
      string inactive_reason="";
      if(!JPWStopRiskDeactivate(g_risk_account_key,
                                g_risk_publisher_token,inactive_reason))
        { JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED);
          Print("JPW stop risk: amostra anterior nao desativada: ",inactive_reason); }
      else g_risk_was_active=false;
     }
   if(why!="") Print("JPW stop risk: ",why);
  }

// OrderCalcProfit is allowed here in the EA, never in the indicator. Pending
// stop-limit orders remain visible as invalid rows; they are not omitted.
bool JPWStopRiskEvaluateRows(JPWStopRiskRow &rows[],string &reason)
  {
   reason="";
   string quoted_symbols[];
   MqlTick quoted_ticks[];
   bool quoted_valid[];
   for(int i=0;i<ArraySize(rows);i++)
     {
      JPWStopRiskRow row=rows[i];
      row.valid=0; row.risk_money=0.0;
      row.additional_valid=0; row.additional_money=0.0;
      row.additional_reason=(row.kind==JPW_STOP_RISK_PENDING ?
                             "Nao se aplica a pendentes" :
                             "Cotacao atual indisponivel");
      if(row.kind==JPW_STOP_RISK_PENDING &&
         !JPWStopRiskPendingSupported(row.order_type))
        { row.reason="Tipo de ordem pendente nao suportado";
          rows[i]=row; continue; }
      if(!JPWFinitePositive(row.sl))
        { row.reason="Sem SL valido"; rows[i]=row; continue; }
      const ENUM_ORDER_TYPE side=(row.side==1 ? ORDER_TYPE_BUY :
                                                 ORDER_TYPE_SELL);
      double signed_profit=0.0;
      ResetLastError();
      if(!OrderCalcProfit(side,row.symbol,row.volume,row.entry,row.sl,
                          signed_profit) ||
         !JPWStopRiskLossFromProfit(signed_profit,row.risk_money))
        { row.reason="OrderCalcProfit indisponivel para entrada→SL";
          rows[i]=row; continue; }
      row.valid=1; row.reason="";
      if(row.kind==JPW_STOP_RISK_POSITION)
        {
         int quote_index=-1;
         for(int j=0;j<ArraySize(quoted_symbols);j++)
            if(quoted_symbols[j]==row.symbol) { quote_index=j; break; }
         if(quote_index<0)
           {
            quote_index=ArraySize(quoted_symbols);
            if(ArrayResize(quoted_symbols,quote_index+1)!=quote_index+1 ||
               ArrayResize(quoted_ticks,quote_index+1)!=quote_index+1 ||
               ArrayResize(quoted_valid,quote_index+1)!=quote_index+1)
              { reason="Cache de cotacoes indisponivel"; return(false); }
            quoted_symbols[quote_index]=row.symbol;
            quoted_valid[quote_index]=SymbolInfoTick(row.symbol,
                                                     quoted_ticks[quote_index]);
           }
         MqlTick tick=quoted_ticks[quote_index];
         const long server_now=(long)TimeTradeServer();
         const long tick_sec=(long)(tick.time_msc/1000);
         const bool recent=quoted_valid[quote_index] &&
            server_now>0 && tick_sec>0 && tick_sec<=server_now+2 &&
            server_now-tick_sec<=30 &&
            JPWFinitePositive(tick.bid) && JPWFinitePositive(tick.ask) &&
            tick.ask>=tick.bid;
         if(recent)
           {
            const double market=(row.side==1 ? tick.bid : tick.ask);
            if((row.side==1 && market<=row.sl) ||
               (row.side==-1 && market>=row.sl))
               row.additional_reason="Nivel do SL alcancado ou ultrapassado";
            else
              {
               double extra_profit=0.0;
               ResetLastError();
               if(OrderCalcProfit(side,row.symbol,row.volume,market,row.sl,
                                  extra_profit) &&
                  JPWStopRiskLossFromProfit(extra_profit,
                                            row.additional_money))
                 { row.additional_valid=1; row.additional_reason=""; }
               else row.additional_reason="Preco atual→SL nao calculavel";
              }
           }
         else row.additional_reason="Cotacao de mercado nao recente";
        }
      rows[i]=row;
     }
   return(true);
  }

void JPWStopRiskObserve()
  {
   if(g_risk_account_key=="" || g_risk_publisher_token=="" ||
      TerminalInfoInteger(TERMINAL_CONNECTED)==0)
     { JPWStopRiskObservationFailed("conta, EA ou conexao indisponivel");
       return; }
   const ulong started=GetTickCount64();
   for(int attempt=0;attempt<2;attempt++)
     {
      JPWStopRiskSample first,second;
      JPWStopRiskRow rows[],check_rows[];
      string reason="";
      if(!JPWStopRiskCollectRaw(g_risk_account_key,first,rows,reason))
        { JPWStopRiskObservationFailed(reason); return; }
      if(!JPWStopRiskEvaluateRows(rows,reason))
        { JPWStopRiskObservationFailed(reason); return; }
      if(!JPWStopRiskCollectRaw(g_risk_account_key,second,check_rows,
                                reason))
        { JPWStopRiskObservationFailed(reason); return; }
      if(first.composition_digest!=second.composition_digest)
        {
         if(attempt==0 && GetTickCount64()-started<500) continue;
         JPWStopRiskObservationFailed("composicao mudou durante coleta");
         return;
        }
      first.observed_utc=(long)TimeGMT();
      first.observed_mono_ms=(long)GetTickCount64();
      first.publisher_token=g_risk_publisher_token;
      first.row_count=ArraySize(rows);
      if(first.observed_utc<=0 || first.observed_mono_ms<=0 ||
         GetTickCount64()-started>500 ||
         !JPWStopRiskAdvanceSessionLease(first.observed_mono_ms,reason))
        { JPWStopRiskObservationFailed(reason=="" ?
                 "amostra excedeu orcamento ou lease nao confirmada" : reason);
          return; }
      if(!JPWStopRiskPublish(first,rows,reason))
        { JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED);
          JPWStopRiskObservationFailed(reason); return; }
      g_risk_dirty=false;
      g_risk_was_active=true;
      g_observer_risk_reason="";
      g_observer_risk_observed_utc=first.observed_utc;
      g_observer_risk_observed_mono=first.observed_mono_ms;
      JPWStopRiskPresenceSet(JPW_OBSERVER_PUBLISHED);
      if(g_observer_last_risk_state!=1)
        { JPWObserverDiagnostic(JPW_DIAG_CAPTURE_RESUMED,first.generation);
          g_observer_last_risk_state=1; }
      return;
     }
  }

bool JPWObserverReadIdentity(string &key)
  {
   key="";
   const long login=AccountInfoInteger(ACCOUNT_LOGIN);
   const string server=AccountInfoString(ACCOUNT_SERVER);
   const string currency=AccountInfoString(ACCOUNT_CURRENCY);
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   return(JPWObserverAccountKey(server,login,currency,installation,key));
  }

bool JPWObserverQueue(const ulong ticket,const long arrival_utc,
                      const ulong arrival_ms,const bool connected)
  {
   if(ticket==0 || ticket>(ulong)LONG_MAX) return(false);
   for(int i=0;i<ArraySize(g_pending);i++)
      if(g_pending[i].ticket==ticket) return(true);
   const int n=ArraySize(g_pending);
   if(n>=JPW_OBSERVER_QUEUE_MAX)
     { g_queue_overflow=true; return(false); }
   if(ArrayResize(g_pending,n+1)!=n+1)
     { g_queue_overflow=true; return(false); }
   g_pending[n].ticket=ticket;
   g_pending[n].attempts=0;
   g_pending[n].arrival_utc=arrival_utc;
   g_pending[n].arrival_ms=arrival_ms;
   g_pending[n].connected_at_arrival=connected;
   return(true);
  }

bool JPWObserverCollectPositionDeals(const long position_id,
                                     JPWObserverDeal &deals[],string &reason)
  {
   reason="";
   ArrayResize(deals,0);
   if(position_id<=0 || !HistorySelectByPosition((ulong)position_id))
     { reason="Historico por identificador indisponivel"; return(false); }
   const int total=HistoryDealsTotal();
   if(total<1 || total>JPW_OBSERVER_MAX_DEALS)
     { reason="Historico da posicao ausente ou excessivo"; return(false); }
   for(int i=0;i<total;i++)
     {
      const ulong ticket=HistoryDealGetTicket(i);
      long type=0,entry=0,id=0,order_ticket=0,time_msc=0;
      double volume=0.0,price=0.0;
      string symbol="";
      if(ticket==0 || ticket>(ulong)LONG_MAX ||
         !HistoryDealGetInteger(ticket,DEAL_TYPE,type) ||
         !HistoryDealGetInteger(ticket,DEAL_ENTRY,entry) ||
         !HistoryDealGetInteger(ticket,DEAL_POSITION_ID,id) ||
         !HistoryDealGetInteger(ticket,DEAL_ORDER,order_ticket) ||
         !HistoryDealGetInteger(ticket,DEAL_TIME_MSC,time_msc) ||
         !HistoryDealGetDouble(ticket,DEAL_VOLUME,volume) ||
         !HistoryDealGetDouble(ticket,DEAL_PRICE,price) ||
         !HistoryDealGetString(ticket,DEAL_SYMBOL,symbol))
        { reason="Propriedade do negocio indisponivel"; return(false); }
      if(type!=DEAL_TYPE_BUY && type!=DEAL_TYPE_SELL) continue;
      const int n=ArraySize(deals);
      if(n>=JPW_OBSERVER_MAX_DEALS || ArrayResize(deals,n+1)!=n+1)
        { reason="Limite do historico atingido"; return(false); }
      deals[n].ticket=(long)ticket;
      deals[n].order_ticket=order_ticket;
      deals[n].position_id=id;
      deals[n].time_msc=time_msc;
      deals[n].entry=(int)entry;
      deals[n].side=(type==DEAL_TYPE_BUY ? 1 : -1);
      deals[n].symbol=symbol;
      deals[n].volume=volume;
      deals[n].price=price;
     }
   if(ArraySize(deals)==0)
     { reason="Nenhum negocio de posicao no historico"; return(false); }
   return(true);
  }

// Escolhe a ultima barra H4 cujo encerramento nominal ocorreu ate o deal.
// O shift e historico: nunca usa o ATR atual se o callback chegou depois de
// uma virada H4. Leitura e revalidacao devem referir-se a mesma barra.
bool JPWObserverATRAtDeal(const string symbol,const long deal_time_msc,
                          double &atr,long &bar_open,string &reason)
  {
   atr=0.0; bar_open=0; reason="";
   if(!JPWRaizNSymbolValid(symbol) || deal_time_msc<=0)
     { reason="Simbolo ou horario de execucao invalido"; return(false); }
   const int handle=iATR(symbol,PERIOD_H4,55);
   if(handle==INVALID_HANDLE)
     { reason="ATR historico H4 indisponivel"; return(false); }
   bool ok=false;
   const datetime deal_sec=(datetime)(deal_time_msc/1000);
   long synchronized=0;
   int shift=iBarShift(symbol,PERIOD_H4,deal_sec,false);
   if(shift>=0 &&
      SeriesInfoInteger(symbol,PERIOD_H4,SERIES_SYNCHRONIZED,synchronized) &&
      synchronized!=0)
     {
      datetime candidate[1];
      if(CopyTime(symbol,PERIOD_H4,shift,1,candidate)==1)
        {
         if((long)candidate[0]+4*60*60>(long)deal_sec) shift++;
         datetime before[1],after[1];
         double value[1];
         if(Bars(symbol,PERIOD_H4)>=shift+56 &&
            BarsCalculated(handle)>=shift+56 &&
            CopyTime(symbol,PERIOD_H4,shift,1,before)==1 &&
            (long)before[0]+4*60*60<=(long)deal_sec &&
            CopyBuffer(handle,0,shift,1,value)==1 &&
            CopyTime(symbol,PERIOD_H4,shift,1,after)==1 &&
            before[0]==after[0] && value[0]!=EMPTY_VALUE &&
            JPWFinitePositive(value[0]))
           { atr=value[0]; bar_open=(long)before[0]; ok=true; }
        }
     }
   IndicatorRelease(handle);
   if(!ok) reason="ATR(55) H4 concluido no instante da execucao nao comprovado";
   return(ok);
  }

bool JPWObserverVerifyOpenInitial(JPWObserverDeal &start,string &reason)
  {
   reason="";
   if(start.order_ticket!=start.position_id) return(true); // Netting reversal.
   if(TerminalInfoInteger(TERMINAL_CONNECTED)==0)
     { reason="Posicao inicial sem conexao confirmada"; return(false); }
   const int total=PositionsTotal();
   if(total<1)
     { reason="Posicao inicial nao esta aberta"; return(false); }
   int matches=0;
   for(int i=0;i<total;i++)
     {
      const ulong ticket=PositionGetTicket(i);
      if(ticket==0 || !PositionSelectByTicket(ticket))
        { reason="Leitura das posicoes abertas incompleta"; return(false); }
      long id=0,side=0,opened_msc=0;
      if(!PositionGetInteger(POSITION_IDENTIFIER,id))
        { reason="Identidade da posicao indisponivel"; return(false); }
      if(id!=start.position_id) continue;
      string symbol="";
      if(!PositionGetInteger(POSITION_TYPE,side) ||
         !PositionGetInteger(POSITION_TIME_MSC,opened_msc) ||
         !PositionGetString(POSITION_SYMBOL,symbol))
        { reason="Abertura da posicao indisponivel"; return(false); }
      matches++;
      const int normalized_side=(side==POSITION_TYPE_BUY ? 1 :
                                 (side==POSITION_TYPE_SELL ? -1 : 0));
      if(!JPWObserverInitialPositionMatches(start,id,symbol,normalized_side,
                                            opened_msc))
        { reason="Primeiro negocio diverge da abertura da posicao viva";
          return(false); }
     }
   if(matches!=1)
     { reason="Posicao inicial ausente ou duplicada"; return(false); }
   return(true);
  }

bool JPWObserverStoreStart(JPWObserverDeal &start,const string expected_key,
                           const long event_arrival_utc,
                           const ulong event_arrival_ms,
                           const bool connected_at_arrival,
                           string &reason)
  {
   reason="";
   string before="",after="";
   if(g_db==INVALID_HANDLE || expected_key=="" ||
      !JPWObserverReadIdentity(before) || before!=expected_key)
     { reason="Conta mudou durante observacao"; return(false); }
   if(!JPWObserverVerifyOpenInitial(start,reason)) return(false);
   JPWObserverSnapshot record;
   JPWObserverClear(record);
   record.account_key=before;
   record.symbol=start.symbol;
   record.position_id=start.position_id;
   record.first_deal_ticket=start.ticket;
   record.deal_time_msc=start.time_msc;
   record.side=start.side;
   record.executed_p0=start.price;
   record.provenance=JPW_OBSERVER_RECONSTRUCTED;
   if(!JPWObserverEpisodeKey(before,start.symbol,start.position_id,
                             start.ticket,record.episode_key))
     { reason="Identidade do episodio indisponivel"; return(false); }
   JPWObserverSnapshot existing;
   string read_reason="";
   const JPWStoreResult existing_status=JPWObserverReadByKeyStatus(g_db,record.episode_key,existing,read_reason);
   if(existing_status==JPW_STORE_VALID)
     {
      if(JPWObserverSameExecution(existing,record))
        {
         if(!JPWObserverReadIdentity(after) || after!=before)
           { reason="Conta mudou durante observacao"; return(false); }
         return(true); // Duplicate event; immutable original remains authoritative.
        }
      reason="Conflito com episodio local preexistente";
      return(false);
     }
   if(existing_status!=JPW_STORE_ABSENT)
     { reason=read_reason; return(false); }
   // ATR is read from a historical bar. The recurring-calendar projection
   // and symbol metadata are observed now, not certified as known at the
   // broker's execution time or at the human decision time.
   if(!JPWObserverATRAtDeal(start.symbol,start.time_msc,
                            record.atr55_h4,record.atr_bar_open,reason))
      return(false);
   JPWHorizonResult horizon;
   JPWHorizonResolve(start.symbol,(datetime)(start.time_msc/1000),horizon);
   record.n_1w=horizon.n_1w;
   record.n_2w=horizon.n_2w;
   record.status_1w=(int)horizon.status_1w;
   record.status_2w=(int)horizon.status_2w;
   record.horizon_source=(horizon.source=="" ? "unavailable" : horizon.source);
   record.horizon_hash=horizon.source_sha256;
   record.horizon_observed_utc=(long)TimeGMT();
   record.observer_recorded_utc=(long)TimeGMT();
   record.event_arrival_utc=(event_arrival_utc>0 ? event_arrival_utc : 0);
   const ulong now_ms=GetTickCount64();
   const bool monotonic_ok=(event_arrival_ms>0 && now_ms>=event_arrival_ms &&
                             now_ms-event_arrival_ms<=(ulong)LONG_MAX);
   record.event_processing_delay_ms=(monotonic_ok ?
                                     (long)(now_ms-event_arrival_ms) : 0);
   // A callback received and fully processed promptly is distinguished from
   // a delayed reconstruction. Neither label certifies the broker-to-callback
   // latency or that current session metadata were known at execution.
   if(connected_at_arrival && TerminalInfoInteger(TERMINAL_CONNECTED)!=0 &&
      record.event_arrival_utc>0 &&
      record.observer_recorded_utc>=record.event_arrival_utc &&
      record.observer_recorded_utc-record.event_arrival_utc<=5 &&
      monotonic_ok &&
      record.event_processing_delay_ms<=JPW_OBSERVER_CAPTURE_WINDOW_MS)
      record.provenance=JPW_OBSERVER_CAPTURED_EVENT;
   if(record.horizon_observed_utc<=0 || record.observer_recorded_utc<=0 ||
      !JPWObserverReadIdentity(after) || after!=before)
     { reason="Conta ou relogio mudou durante observacao"; return(false); }
   if(!JPWObserverVerifyOpenInitial(start,reason)) return(false);
   const bool stored=JPWObserverInsertImmutable(g_db,record,reason);
   if(stored) { g_observer_raiz_observed_utc=record.observer_recorded_utc;
      g_observer_raiz_observed_mono=(long)GetTickCount64(); }
   if(!stored) JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED);
   else if(record.provenance==JPW_OBSERVER_RECONSTRUCTED)
      JPWObserverDiagnostic(JPW_DIAG_RECONSTRUCTED);
   return(stored);
  }

bool JPWObserverProcessEvent(JPWObserverPending &pending,string &reason)
  {
   reason="";
   const ulong event_ticket=pending.ticket;
   if(!HistoryDealSelect(event_ticket))
     { reason="Negocio do evento ainda indisponivel"; return(false); }
   long id=0,entry=0,type=0;
   if(!HistoryDealGetInteger(event_ticket,DEAL_TYPE,type))
     { reason="Tipo do negocio indisponivel"; return(false); }
   if(type!=DEAL_TYPE_BUY && type!=DEAL_TYPE_SELL) return(true);
   if(!HistoryDealGetInteger(event_ticket,DEAL_POSITION_ID,id) ||
      !HistoryDealGetInteger(event_ticket,DEAL_ENTRY,entry) || id<=0)
     { reason="Identificador do negocio indisponivel"; return(false); }
   if(entry!=DEAL_ENTRY_IN && entry!=DEAL_ENTRY_INOUT) return(true);
   JPWObserverDeal deals[],start;
   if(!JPWObserverCollectPositionDeals(id,deals,reason) ||
      !JPWObserverFindEpisode(deals,(long)event_ticket,start,reason))
      return(false);
   // Adicao com origem anterior nao prova que o observador viu a abertura.
   // OnInit trata posicoes preexistentes como RECONSTRUCTED separadamente.
   if(start.ticket!=(long)event_ticket) return(true);
   return(JPWObserverStoreStart(start,g_account_key,pending.arrival_utc,
                                pending.arrival_ms,
                                pending.connected_at_arrival,reason));
  }

// One open position per timer slice. A temporary history/ATR/database failure
// retains the cursor, retries after one second and never becomes a capture.
// After the bounded attempt limit, other positions can progress; a later pass
// revisits unresolved episodes. Closed/missing history remains incomplete.
void JPWObserverReconstructionFailed(const int code)
  {
   JPWObserverDiagnostic(code);
   g_reconstruct_attempts++;
   g_reconstruct_next_ms=GetTickCount64()+1000;
   if(g_reconstruct_attempts>=JPW_OBSERVER_MAX_ATTEMPTS)
     {
      JPWObserverDiagnostic(JPW_DIAG_RETRY_EXHAUSTED);
      g_reconstruct_cursor++;
      g_reconstruct_attempts=0;
      g_reconstruct_retry_pass=true;
     }
  }
void JPWObserverReconstructionAccepted()
  {
   g_reconstruct_cursor++;
   g_reconstruct_attempts=0;
   g_reconstruct_next_ms=0;
  }
void JPWObserverReconstructOpen()
  {
   if(GetTickCount64()<g_reconstruct_next_ms) return;
   const int count=PositionsTotal();
   if(count<0) { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   if(g_reconstruct_count!=count)
     { g_reconstruct_count=count; g_reconstruct_cursor=0;
       g_reconstruct_attempts=0; g_reconstruct_retry_pass=false; }
   if(g_reconstruct_cursor>=count)
     {
      if(g_reconstruct_retry_pass && count>0)
        { g_reconstruct_cursor=0; g_reconstruct_retry_pass=false;
          g_reconstruct_next_ms=GetTickCount64()+30000; }
      else g_reconstruct_open_positions=false;
      return;
     }
   const ulong ticket=PositionGetTicket(g_reconstruct_cursor);
   long id=0,side=0;
   string symbol="";
   if(ticket==0 || !PositionSelectByTicket(ticket) ||
      !PositionGetInteger(POSITION_IDENTIFIER,id) ||
      !PositionGetInteger(POSITION_TYPE,side) ||
      !PositionGetString(POSITION_SYMBOL,symbol) || id<=0)
     { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   JPWObserverDeal deals[],start;
   string reason="";
   if(!JPWObserverCollectPositionDeals(id,deals,reason) || ArraySize(deals)==0)
     { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   JPWObserverSortDeals(deals,0,ArraySize(deals)-1);
   const long last=deals[ArraySize(deals)-1].ticket;
   if(!JPWObserverFindEpisode(deals,last,start,reason) ||
      start.symbol!=symbol || start.side!=(side==POSITION_TYPE_BUY ? 1 : -1))
     { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   string key="";
   if(!JPWObserverEpisodeKey(g_account_key,start.symbol,start.position_id,start.ticket,key))
     { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   JPWObserverSnapshot existing;
   const JPWStoreResult status=JPWObserverReadByKeyStatus(g_db,key,existing,reason);
   if(status==JPW_STORE_VALID) { JPWObserverReconstructionAccepted(); return; }
   if(status!=JPW_STORE_ABSENT)
     { JPWObserverReconstructionFailed(status==JPW_STORE_CORRUPT ? JPW_DIAG_STORAGE_CORRUPT : JPW_DIAG_WRITE_FAILED); return; }
   if(!JPWObserverStoreStart(start,g_account_key,0,0,false,reason))
     { JPWObserverReconstructionFailed(JPW_DIAG_DATA_UNAVAILABLE); return; }
   JPWObserverReconstructionAccepted();
  }

// Terminal lifecycle notices bypass the FIFO: a full queue must not hide the
// fact that queued work was abandoned. At most three writes are attempted;
// a refused write leaves this instance's visible failure marker in place.
bool JPWObserverTerminalDiagnostic(const string context,const int code)
  {
   if(!JPWRaizNIsHash(context)) return(false);
   string diagnostic_reason="";
   const JPWStoreResult state=JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,code,0,
      (long)TimeGMT(),(long)GetTickCount64(),diagnostic_reason);
   if(state==JPW_STORE_VALID) return(true);
   string marker_reason="";
   if(!JPWDiagMarkFailure(context,JPW_DIAG_OBSERVER,
                          g_observer_diagnostic_instance,marker_reason))
      Print("JPW diagnostics: ",marker_reason);
   Print("JPW diagnostics: encerramento nao persistido: ",diagnostic_reason);
   return(false);
  }

bool JPWObserverRuntimeLegacyConflict(const string key,const string own_token)
  {
   if(!JPWRaizNIsHash(key)) return(true);
   const string own=JPWObserverPresenceName(key,own_token);
   const int total=GlobalVariablesTotal();
   for(int i=0;i<total;i++)
     {
      const string name=GlobalVariableName(i);
      if(name==own || StringFind(name,JPW_OBSERVER_PRESENCE_PREFIX)!=0 ||
         StringLen(name)!=61 || StringSubstr(name,16,24)!=StringSubstr(key,0,24)) continue;
      double value=0; JPWObserverPresenceState state=JPW_OBSERVER_NOT_CONFIRMED;
      if(GlobalVariableGet(name,value) && JPWObserverPresenceDecodeAt(value,GetTickCount64(),state)) return(true);
     }
   return(false);
  }
bool JPWObserverRuntimeRiskLeaseCurrent()
  {
   double value=0;
   return(g_observer_runtime_attached && !g_observer_runtime_conflict && g_risk_was_active &&
      g_risk_presence_state==JPW_OBSERVER_PUBLISHED && g_risk_lease_owned && g_risk_lease_value>0 &&
      TerminalInfoInteger(TERMINAL_CONNECTED)!=0 &&
      GlobalVariableGet(JPWStopRiskLeaseName(g_risk_publisher_token),value) && value==g_risk_lease_value);
  }
bool JPWObserverRuntimeAttach(const string expected_key="")
  {
   if(!JPWObserverReadIdentity(g_account_key))
     { Print("JPW observer: identidade da conta indisponivel");
       return(false); }
   if(expected_key!="" && g_account_key!=expected_key) return(false);
   g_observer_runtime_attached=true;
   g_observer_runtime_conflict=false;
   g_observer_runtime_reason="";
   g_observer_risk_reason="";
   g_observer_diagnostic_first=false;
   g_observer_coverage_incomplete=false; g_queue_overflow=false;
   g_observer_last_risk_state=-1; g_reconstruct_open_positions=false;
   g_observer_risk_observed_utc=0; g_observer_risk_observed_mono=0;
   g_observer_raiz_observed_utc=0; g_observer_raiz_observed_mono=0;
   g_observer_personal_observed_utc=0; g_observer_personal_observed_mono=0;
   g_observer_personal_quality=JPW_PERSONAL_UNAVAILABLE;
   g_risk_was_active=false;
   g_risk_account_key=g_account_key;
   if(!JPWStopRiskPublisherToken(g_risk_account_key,ChartID(),g_risk_publisher_token))
      g_risk_publisher_token="";
   g_observer_runtime_conflict=JPWObserverRuntimeLegacyConflict(g_account_key,g_risk_publisher_token);
   if(g_observer_runtime_conflict)
     { g_observer_runtime_reason="Observador legado ativo; publicacoes e avisos suspensos"; return(true); }
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\PersonalHistory");
   // Claim the existing Personal History fence before any publisher starts.
   // It also protects against an old writer whose presence marker is absent.
   g_observer_runtime_owner=FileOpen(JPW_PERSONAL_FOLDER+"writer_"+g_account_key+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(g_observer_runtime_owner==INVALID_HANDLE)
     { g_observer_runtime_conflict=true; g_observer_runtime_reason="Lock do observador/histórico já possui titular; nenhum aviso/publicação concorrente"; return(true); }
   string reason="";
   if(!JPWObserverOpen(g_account_key,true,g_db,reason))
     { Print("JPW observer: snapshots Raiz N indisponiveis: ",reason);
       JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED);
       g_next_db_open_ms=GetTickCount64()+30000; }
   ArrayResize(g_pending,0);
   JPWObserverScheduleReconstruction();
   JPWObserverDiagnostic(JPW_DIAG_SESSION_START);
   JPWObserverFlushDiagnostics();
   g_next_risk_sample_ms=0;
   g_risk_dirty=true;
   g_risk_was_active=false;
   g_risk_lease_owned=false;
   g_risk_lease_value=0.0;
   g_risk_presence_owned=false;
   g_risk_presence_value=0.0;
   g_risk_presence_state=JPW_OBSERVER_WAITING;
   JPWStopRiskPresenceRefresh();
   if(!JPWPersonalControllerAttach(g_account_key,g_risk_publisher_token))
      g_observer_runtime_reason="Histórico pessoal não anexado; demais observações permanecem independentes";
   // Transfer the retained handle, never release/reacquire between modules.
   g_ph_exclusive_file=g_observer_runtime_owner; g_observer_runtime_owner=INVALID_HANDLE;
   Print("JPW observer: observacao local habilitada; nenhuma funcao de negociacao e usada");
   return(true);
  }

void JPWObserverRuntimeDetach(const int reason)
  {
   if(!g_observer_runtime_attached) return;
   g_observer_runtime_attached=false;
   if(g_observer_runtime_conflict)
     { if(g_observer_runtime_owner!=INVALID_HANDLE) FileClose(g_observer_runtime_owner);
       g_observer_runtime_owner=INVALID_HANDLE;
       g_observer_runtime_conflict=false; g_account_key=""; g_risk_account_key="";
       g_risk_publisher_token=""; ArrayResize(g_pending,0); return; }
   JPWPersonalControllerDetach("EA desativado; motivo técnico "+IntegerToString(reason));
   JPWStopRiskPresenceRelease();
   JPWStopRiskReleaseSessionLease();
   string risk_reason="";
   bool deactivate_failed=false;
   if(g_risk_account_key!="" && g_risk_publisher_token!="" &&
      !JPWStopRiskDeactivate(g_risk_account_key,g_risk_publisher_token,
                             risk_reason))
     { deactivate_failed=true;
       Print("JPW stop risk: desativacao nao confirmada: ",risk_reason); }
   const bool abandoned=ArraySize(g_pending)>0 ||
      ArraySize(g_diagnostic_pending)>0 || g_diagnostic_queue_lost ||
      g_reconstruct_open_positions;
   if(abandoned || deactivate_failed)
      JPWObserverTerminalDiagnostic(g_account_key,deactivate_failed ?
         JPW_DIAG_WRITE_FAILED : JPW_DIAG_RETRY_EXHAUSTED);
   // Preserve one earlier account context within the bounded shutdown budget.
   // Further contexts remain explicitly signalled by per-instance failure flags.
   string earlier_context="";
   for(int i=0;i<ArraySize(g_diagnostic_pending);i++)
     {
      const string context=g_diagnostic_pending[i].context;
      if(context==g_account_key || context==earlier_context) continue;
      if(earlier_context=="")
        { earlier_context=context;
          JPWObserverTerminalDiagnostic(context,JPW_DIAG_RETRY_EXHAUSTED); }
      else
        {
         string marker_reason="";
         if(!JPWDiagMarkFailure(context,JPW_DIAG_OBSERVER,
                                g_observer_diagnostic_instance,marker_reason))
            Print("JPW diagnostics: ",marker_reason);
        }
     }
   JPWObserverTerminalDiagnostic(g_account_key,JPW_DIAG_SESSION_END);
   if(g_db!=INVALID_HANDLE) DatabaseClose(g_db);
   g_db=INVALID_HANDLE;
   ArrayResize(g_pending,0);
   g_observer_runtime_conflict=false;
   g_account_key=""; g_risk_account_key=""; g_risk_publisher_token="";
  }

void JPWObserverRuntimeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(!g_observer_runtime_attached || g_observer_runtime_conflict) return;
   string observed_key="";
   if(!JPWObserverReadIdentity(observed_key) || observed_key!=g_account_key) return;
   g_risk_dirty=true;
   JPWPersonalControllerMarkDirty(); // Signal only; capture, IO and channels run on timer.
   if(trans.type==TRADE_TRANSACTION_DEAL_ADD && trans.deal>0)
      JPWObserverQueue(trans.deal,(long)TimeGMT(),GetTickCount64(),
                       TerminalInfoInteger(TERMINAL_CONNECTED)!=0);
  }

void JPWObserverRuntimePrepare(const ulong started)
  {
   if(!g_observer_runtime_attached) return;
   if(!g_observer_runtime_conflict && JPWObserverRuntimeLegacyConflict(g_account_key,g_risk_publisher_token))
     {
      const string conflicted_key=g_account_key;
      JPWObserverRuntimeDetach(REASON_RECOMPILE); JPWObserverRuntimeAttach(conflicted_key);
      return;
     }
   if(g_observer_runtime_conflict)
     {
      if(JPWObserverRuntimeLegacyConflict(g_account_key,g_risk_publisher_token)) return;
      const string retry_key=g_account_key;
      JPWObserverRuntimeDetach(REASON_RECOMPILE); JPWObserverRuntimeAttach(retry_key);
     }
   string key="";
   if(!JPWObserverReadIdentity(key) || key!=g_account_key)
     {
      JPWObserverDiagnostic(JPW_DIAG_CONTEXT_CHANGED);
      JPWObserverRuntimeDetach(REASON_ACCOUNT);
      if(key!="") JPWObserverRuntimeAttach(key);
      return;
     }
   if(g_queue_overflow)
     { JPWObserverDiagnostic(JPW_DIAG_QUEUE_OVERFLOW);
       JPWObserverScheduleReconstruction();
       g_queue_overflow=false; }
   // Database diagnostics run in the scheduled RaizN job. An indivisible
   // diagnostic write cannot consume every round before priority/fairness.
  }
void JPWObserverRuntimeTick(const ulong started,const int module)
  {
   if(!g_observer_runtime_attached || g_observer_runtime_conflict || GetTickCount64()<started || GetTickCount64()-started>=500) return;
   if(module==0)
     {
   const ulong risk_now=GetTickCount64();
   if(g_risk_dirty || risk_now>=g_next_risk_sample_ms)
     {
      g_next_risk_sample_ms=risk_now+5000;
      JPWStopRiskObserve();
     }
     }
   else if(module==1)
     {
      const ulong previous=g_ph_last_accepted;
      JPWPersonalControllerTick(started);
      // g_ph_last_wall is a timer timestamp, not a financial capture. Use
      // the accepted terminal capture, retained after its incremental reset.
      if(g_ph_last_accepted!=previous && g_ph_live_count>=0 &&
         g_ph_capture.account_key==g_account_key && g_ph_capture.stable &&
         g_ph_capture.inventory_valid && g_ph_capture.wall_seconds>0 &&
         g_ph_capture.mono_ms>0 && g_ph_capture.mono_ms<=(ulong)LONG_MAX)
        {
         g_observer_personal_observed_utc=g_ph_capture.wall_seconds;
         g_observer_personal_observed_mono=(long)g_ph_capture.mono_ms;
         g_observer_personal_quality=g_ph_capture.quality;
        }
     }
   else if(module==2)
     {
   // Alternate the diagnostic turn with real RaizN work. A slow or refused
   // diagnostic write must not indefinitely starve this module's snapshots.
   const bool diagnostic_first=g_observer_diagnostic_first;
   g_observer_diagnostic_first=!g_observer_diagnostic_first;
   if(diagnostic_first) JPWObserverFlushDiagnostics(1);
   if(GetTickCount64()<started || GetTickCount64()-started>=500) return;
   if(g_db==INVALID_HANDLE)
     {
      const ulong now=GetTickCount64();
      if(now<g_next_db_open_ms) return;
      string reason="";
      if(JPWObserverOpen(g_account_key,true,g_db,reason))
         JPWObserverScheduleReconstruction();
      else { g_next_db_open_ms=now+30000; JPWObserverDiagnostic(JPW_DIAG_WRITE_FAILED); return; }
     }
   const int limit=(int)MathMin(4,ArraySize(g_pending));
   for(int i=0;i<limit && GetTickCount64()-started<500;i++)
     {
      JPWObserverPending pending=g_pending[0];
      for(int j=1;j<ArraySize(g_pending);j++) g_pending[j-1]=g_pending[j];
      ArrayResize(g_pending,ArraySize(g_pending)-1);
      string reason="";
      if(JPWObserverProcessEvent(pending,reason)) continue;
      pending.attempts++;
      if(pending.attempts>=JPW_OBSERVER_MAX_ATTEMPTS)
        { JPWObserverDiagnostic(JPW_DIAG_RETRY_EXHAUSTED);
          JPWObserverScheduleReconstruction();
          Print("JPW observer: captura nao concluida: ",reason); }
      else
        {
         const int n=ArraySize(g_pending);
         if(ArrayResize(g_pending,n+1)==n+1) g_pending[n]=pending;
         else g_queue_overflow=true;
        }
     }
   // Give opening-deal events priority over startup reconstruction. Otherwise
   // a trade arriving in the first second could be mislabeled RECONSTRUCTED.
   if(g_reconstruct_open_positions && ArraySize(g_pending)==0 &&
      GetTickCount64()-started<500 && TerminalInfoInteger(TERMINAL_CONNECTED)!=0)
      JPWObserverReconstructOpen();
   if(!diagnostic_first && GetTickCount64()>=started && GetTickCount64()-started<500)
      JPWObserverFlushDiagnostics(1);
     }
  }
void JPWObserverRuntimeLegacyTick()
  {
   const ulong started=GetTickCount64();
   JPWObserverRuntimePrepare(started);
   if(g_observer_runtime_conflict) return;
   JPWStopRiskPresenceRefresh();
   for(int module=0;module<3;module++) JPWObserverRuntimeTick(started,module);
   JPWStopRiskPresenceRefresh();
   const ulong elapsed=GetTickCount64()-started;
   JPWDiagTimingRecord(g_observer_timing,(long)elapsed,elapsed>=500 || ArraySize(g_pending)>0 || g_reconstruct_open_positions);
   if(elapsed>=500) { JPWObserverDiagnostic(JPW_DIAG_BUDGET_DEFERRED); JPWPersonalControllerDeferred(); }
  }
#endif

#ifndef JPW_ALAVANCAGEM_COORDINATOR_MQH
#define JPW_ALAVANCAGEM_COORDINATOR_MQH
// Indicator runtime component; included after its instance state.
long g_indicator_diagnostic_instance=0;

bool JPWCoordinatorBudgetRemaining()
  {
   const ulong now=GetTickCount64();
   return(g_cycle_started_ms>0 && now>=g_cycle_started_ms && now-g_cycle_started_ms<500);
  }

// Preserve event origin even when a later context has already been accepted.
void JPWEnqueueDiagnostic(JPWIndicatorDiagnosticPending &event)
  {
   if(event.context=="") return;
   for(int i=0;i<ArraySize(g_diagnostic_pending);i++)
      if(g_diagnostic_pending[i].context==event.context &&
         g_diagnostic_pending[i].code==event.code) return;
   const int n=ArraySize(g_diagnostic_pending);
   if(n>=64 || ArrayResize(g_diagnostic_pending,n+1)!=n+1)
     {
      if(!g_diagnostic_queue_lost)
        { g_diagnostic_overflow=event; g_diagnostic_overflow.code=JPW_DIAG_QUEUE_OVERFLOW; }
      g_diagnostic_queue_lost=true; return;
     }
   g_diagnostic_pending[n]=event;
  }
void JPWQueueDiagnostic(const int code)
  {
   JPWIndicatorDiagnosticPending event;
   event.context=g_diagnostic_context; event.code=code;
   event.sample_id=g_collection_sequence; event.utc=(long)TimeGMT();
   event.mono=(long)GetTickCount64(); JPWEnqueueDiagnostic(event);
  }
void JPWIndicatorDiagnosticFailureMarker(const string context)
  {
   if(context=="") return;
   string reason="";
   if(!JPWDiagMarkFailure(context,JPW_DIAG_INDICATOR,g_indicator_diagnostic_instance,reason))
     { g_diagnostic_reason+="; "+reason;
       Print("JPW diagnostics: ",reason); }
  }
void JPWIndicatorTerminalDiagnostic(const string context,const int code)
  {
   if(context=="") return;
   string reason="";
   if(JPWDiagRecordAt(context,JPW_DIAG_INDICATOR,code,g_collection_sequence,
                     (long)TimeGMT(),(long)GetTickCount64(),reason)!=JPW_STORE_VALID)
      JPWIndicatorDiagnosticFailureMarker(context);
  }
void JPWFlushDiagnostics()
  {
   if(g_diagnostic_context!="" && g_last_diagnostic_context!=g_diagnostic_context)
     {
      JPWQueueDiagnostic(g_last_diagnostic_context=="" ? JPW_DIAG_SESSION_START : JPW_DIAG_CONTEXT_CHANGED);
      g_last_diagnostic_context=g_diagnostic_context;
     }
   if(g_diagnostic_queue_lost && ArraySize(g_diagnostic_pending)<64)
     {
      const int n=ArraySize(g_diagnostic_pending);
      if(ArrayResize(g_diagnostic_pending,n+1)==n+1)
        { g_diagnostic_pending[n]=g_diagnostic_overflow; g_diagnostic_queue_lost=false; }
     }
   for(int written=0;written<2 && ArraySize(g_diagnostic_pending)>0 && JPWCoordinatorBudgetRemaining();written++)
     {
      JPWIndicatorDiagnosticPending event=g_diagnostic_pending[0];
      string reason="";
      g_diagnostic_write_state=JPWDiagRecordAt(event.context,JPW_DIAG_INDICATOR,
                              event.code,event.sample_id,event.utc,event.mono,reason);
      g_diagnostic_reason=reason;
      if(g_diagnostic_write_state!=JPW_STORE_VALID)
        {
         JPWIndicatorDiagnosticFailureMarker(event.context);
         JPWIndicatorDiagnosticPending failure=event;
         failure.code=JPW_DIAG_WRITE_FAILED; failure.utc=(long)TimeGMT();
         failure.mono=(long)GetTickCount64(); JPWEnqueueDiagnostic(failure);
         break;
        }
      for(int j=1;j<ArraySize(g_diagnostic_pending);j++) g_diagnostic_pending[j-1]=g_diagnostic_pending[j];
      ArrayResize(g_diagnostic_pending,ArraySize(g_diagnostic_pending)-1);
      bool still_pending=false;
      for(int j=0;j<ArraySize(g_diagnostic_pending);j++)
         if(g_diagnostic_pending[j].context==event.context) still_pending=true;
      if(!still_pending && !(g_diagnostic_queue_lost && g_diagnostic_overflow.context==event.context))
        {
         string marker_reason="";
         if(!JPWDiagClearFailure(event.context,JPW_DIAG_INDICATOR,
                                g_indicator_diagnostic_instance,marker_reason))
           { g_diagnostic_write_state=JPW_STORE_IO_ERROR;
             g_diagnostic_reason=marker_reason; }
        }
     }
  }

void JPWAcceptMetric(const int metric)
  {
   const int quality=(metric==0 ? (int)g_leverage_quality :
      (metric==1 ? (int)g_floating_quality : (metric==2 ? (int)g_genesis_quality :
      (metric==3 ? (int)g_raiz_quality : (metric==4 ? (int)g_scale2_quality : (int)g_stop_quality)))));
   const string units=(metric==0 ? "ratio" : (metric==5 ? "account_currency" : "percent"));
   const string source=(metric==0 ? "positions+quotes+equity" :
      (metric==1 ? "account_profit/balance" : (metric==2 ? "genesis+bid/ask+sl" :
      (metric==5 ? "observer_stop_risk_generation" : "same_tick+iATR55_H4+calendar+F"))));
   const bool accepted=JPWSampleAccept(g_metric_samples[metric],g_collection_sequence,g_sample_context,
      g_numeric_values[metric],g_numeric_valid[metric] && quality!=JPW_VIEW_NA,
      units,quality,(quality==JPW_VIEW_CURRENT ? JPW_SAMPLE_CONFIRMED :
      (quality==JPW_VIEW_ESTIMATED ? JPW_SAMPLE_ESTIMATED : JPW_SAMPLE_UNAVAILABLE)),
      source,(long)TimeGMT(),g_source_times[metric],GetTickCount64());
   if(accepted && g_metric_last_quality[metric]!=quality)
     { JPWQueueDiagnostic(JPW_DIAG_QUALITY_CHANGED);
       if(quality==JPW_VIEW_NA) JPWQueueDiagnostic(JPW_DIAG_DATA_UNAVAILABLE);
       g_metric_last_quality[metric]=quality; }
   if(metric==5 && g_stop_ready && g_stop_sample.observed_mono_ms>0)
     {
      const ulong source_deadline=(ulong)g_stop_sample.observed_mono_ms+30000;
      if(source_deadline<g_metric_samples[metric].valid_until_monotonic_ms)
         g_metric_samples[metric].valid_until_monotonic_ms=source_deadline;
     }
  }

void JPWRefreshRequestedRecords()
  {
   if(!JPWCoordinatorBudgetRemaining()) return;
   if(g_export_requested)
     {
      g_export_requested=false;
      string path="",reason="";
      if(g_export_preview!="" && JPWDiagExport(g_diagnostic_context,g_export_preview,path,reason)==JPW_STORE_VALID)
         g_export_result="Exportação local gravada: "+path;
      else g_export_result="Exportação não concluída: "+reason;
      JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();
     }
   if(!JPWCoordinatorBudgetRemaining()) return;
   if(g_export_preview_requested)
     {
      g_export_preview_requested=false;
      string reason="";
      if(JPWDiagPreview(g_diagnostic_context,g_export_preview,reason)!=JPW_STORE_VALID)
         { g_export_preview=""; g_export_result="Prévia indisponível: "+reason; }
      JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();
     }
   if(!g_record_read_requested || !g_raiz_details_open) return;
   while(g_record_read_stage<5 && JPWCoordinatorBudgetRemaining())
     {
      if(g_record_read_stage==0) JPWDetailsReadMDD();
      else if(g_record_read_stage==1) JPWDetailsReadObserver();
      else if(g_record_read_stage==2) JPWDetailsReadStopRisk();
      else if(g_record_read_stage==3)
        {
         JPWCollectRaizScenario();
         if(g_raiz_tab>=JPW_ROUTE_OVERVIEW)
           { JPWRaizPopulateFields(); JPWLivePopulateFields(); JPWFactorPopulateDraft();
             g_raiz_draft_expected_id=(g_raiz_store_state==JPW_RAIZN_VALID ? g_raiz_scenario.scenario_id : ""); }
        }
      else g_diagnostic_state=JPWDiagSummary(g_diagnostic_context,g_diagnostic_summary,g_diagnostic_reason);
      g_record_read_stage++;
     }
   if(g_record_read_stage>=5) { g_record_read_stage=0; g_record_read_requested=false; }
   JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();
  }

bool JPWConfirmAcceptedContext()
  {
   JPWAccount current;
   if(!g_account_known || !JPWReadAccount(current) ||
      !JPWAccountsEqual(g_account,current) ||
      (g_cockpit_snapshot.symbol!="" && g_cockpit_snapshot.symbol!=_Symbol))
     { JPWInvalidateIdentityPresentation(); g_refresh_requested=true; return(false); }
   return(true);
  }

void JPWHorizonResetTickEvidence()
  {
   MqlTick tick;
   g_horizon_tick_baseline_msc=(SymbolInfoTick(_Symbol,tick) && tick.time_msc>0 ?
                                 tick.time_msc : 0);
   g_horizon_new_tick=false;
   g_horizon_was_connected=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
  }

void JPWLog(const string message)
  {
   if(!InpTechnicalLog) return;
   const ulong now=GetTickCount64();
   if(g_last_log_ms!=0 && now>=g_last_log_ms && now-g_last_log_ms<60000) return;
   g_last_log_ms=now;
   Print("JPW Alavancagem Atual: ",message);
  }

void JPWStopRiskUnavailable(const string reason)
  {
   g_stop_quality=JPW_VIEW_NA;
   g_stop_value="N/A";
   g_stop_reason=(reason=="" ? "Amostra do EA indisponível" : reason);
   g_stop_detail="Risco dos stops indisponível: "+g_stop_reason+
      ". Última amostra, se houver, é somente consultável em Stops.";
   g_stop_ready=false;
   g_stop_scope_valid=false;
  }

void JPWStopRiskUnavailableWithPresence(const string read_reason)
  {
   // Presence is diagnostic evidence only. It cannot make a missing, stale or
   // incoherent financial generation Current, and never creates a zero total.
   if(g_stop_observer_presence==JPW_OBSERVER_NOT_CONFIRMED)
     {
      JPWStopRiskUnavailable("Observer not confirmed");
      g_stop_detail="Sem sinal recente de um EA observador compatível nesta "+
         "instalação e conta. Confira a mesma versão em Expert Advisors → "+
         "JPWealth, anexe-a a um gráfico desta instalação e consulte Experts. "+
         "Leitura financeira: "+read_reason+".";
     }
   else if(g_stop_observer_presence==JPW_OBSERVER_WAITING)
     {
      JPWStopRiskUnavailable("Observer active · awaiting sample");
      g_stop_detail="EA observador presente; primeira publicação de Stop risk "+
         "ainda não foi confirmada. Confira Experts nesta instalação. "+
         "Leitura financeira: "+read_reason+".";
     }
   else if(g_stop_observer_presence==JPW_OBSERVER_FAILED)
     {
      JPWStopRiskUnavailable("Observer active · publication failed");
      g_stop_detail="EA observador presente, mas sua última tentativa de "+
         "publicação falhou. Abra Experts para o motivo; confira SLs de "+
         "posições e pendentes, tipos de ordem e conexão. "+
         "Leitura financeira: "+read_reason+".";
     }
   else
     {
      JPWStopRiskUnavailable("Observer active · stop sample unavailable");
      g_stop_detail="EA observador publicou, mas a geração atual não passou "+
         "pela leitura/validação do indicador. Confira Experts e Sistema. "+
         "Leitura financeira: "+read_reason+".";
     }
  }

int JPWStopRiskRebindIndex(JPWStopRiskRow &chosen,
                           JPWStopRiskRow &rows[])
  {
   for(int i=0;i<ArraySize(rows);i++)
      if(rows[i].kind==chosen.kind && rows[i].ticket==chosen.ticket &&
         rows[i].identifier==chosen.identifier &&
         rows[i].symbol==chosen.symbol && rows[i].side==chosen.side)
         return(i);
   return(-1);
  }

bool JPWStopRiskRowInScope(JPWStopRiskRow &row,const bool scope_valid,
                           const string symbol,const int side)
  {
   return(scope_valid && row.symbol==symbol && row.side==side);
  }

void JPWStopRiskRefreshRowView()
  {
   if(!g_raiz_details_open || g_raiz_tab!=JPW_ROUTE_STOP_ROW) return;
   if(g_stop_selected_row==-2)
     { g_stop_table_historical=!g_stop_ready; return; }
   if(g_stop_selected_row<0 ||
      g_stop_selected_row>=ArraySize(g_stop_table_rows))
     { g_raiz_tab=JPW_ROUTE_STOPS; g_cockpit_page=0; return; }
   JPWStopRiskRow chosen=g_stop_table_rows[g_stop_selected_row];
   // A new complete EA generation is not enough: the selected row must still
   // belong to the current inferred operation scope. A closed/ambiguous
   // Genesis invalidates that attribution even if this ticket remains open.
   if(g_stop_ready && !JPWStopRiskRowInScope(chosen,g_stop_scope_valid,
                                              g_stop_scope_symbol,g_stop_scope_side))
     { g_raiz_tab=JPW_ROUTE_STOPS; g_cockpit_page=0; g_stop_selected_row=-1; return; }
   JPWStopRiskSample sample;
   JPWStopRiskRow rows[];
   bool historical=false;
   if(g_stop_ready)
     {
      sample=g_stop_sample;
      ArrayResize(rows,ArraySize(g_stop_rows));
      for(int i=0;i<ArraySize(rows);i++) rows[i]=g_stop_rows[i];
     }
   else if(g_stop_last_ready)
     {
      historical=true; sample=g_stop_last_sample;
      ArrayResize(rows,ArraySize(g_stop_last_rows));
      for(int i=0;i<ArraySize(rows);i++) rows[i]=g_stop_last_rows[i];
     }
   else
     { g_raiz_tab=JPW_ROUTE_STOPS; g_cockpit_page=0; g_stop_selected_row=-1; return; }
   const int rebound=JPWStopRiskRebindIndex(chosen,rows);
   if(rebound<0)
     { g_raiz_tab=JPW_ROUTE_STOPS; g_cockpit_page=0; g_stop_selected_row=-1; return; }
   g_stop_table_sample=sample;
   ArrayResize(g_stop_table_rows,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++) g_stop_table_rows[i]=rows[i];
   g_stop_selected_row=rebound;
   g_stop_table_historical=historical;
   if(!historical)
     {
      JPWStopRiskRow current=rows[rebound];
      if(current.kind==JPW_STOP_RISK_PENDING)
         g_stop_selected_role="Pending · inferred";
      else if(sample.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
         g_stop_selected_role="Net position · aggregate";
      else if(current.identifier==g_stop_genesis_identifier)
         g_stop_selected_role="Gênese · "+
            (g_stop_provenance=="Selected" ? "selected" : "inferred");
      else g_stop_selected_role="Defesa · inferred";
     }
  }

bool JPWStopRiskKey(JPWAccount &account,string &key)
  {
   return(JPWObserverAccountKey(account.server,account.login,account.currency,
                                 TerminalInfoString(TERMINAL_DATA_PATH),key));
  }

bool JPWStopRiskResolveScope(JPWAccount &account,JPWStopRiskRow &rows[],
                             string &symbol,int &side,string &provenance,
                             string &reason)
  {
   symbol=""; side=0; provenance=""; reason="";
   g_stop_genesis_identifier=0; g_stop_genesis_ticket=0;
   g_stop_genesis_opened_msc=0; g_stop_genesis_closed=false;
   JPWGenesisRecord reference; JPWGenesisClear(reference);
   const JPW_GENESIS_STORE_STATE state=JPWGenesisRead(account,InpGenesisTicket,
                                                       JPW_GENESIS_FOLDER,reference);
   if(state==JPW_GENESIS_VALID)
     {
      side=(reference.direction==POSITION_TYPE_BUY ? 1 :
            (reference.direction==POSITION_TYPE_SELL ? -1 : 0));
      if(reference.symbol=="" || side==0 ||
         reference.reference_state==JPW_GENESIS_REVERSED)
        { reason="Referência Gênese incompatível ou revertida"; return(false); }
      symbol=reference.symbol;
      provenance=(InpGenesisTicket>0 ? "Selected" : "Inferred");
      g_stop_genesis_identifier=reference.identifier;
      g_stop_genesis_ticket=reference.origin_ticket;
      g_stop_genesis_opened_msc=reference.opened_msc;
      g_stop_genesis_closed=(reference.reference_state==JPW_GENESIS_CLOSED);
      // A closed Genesis is the end of this attributed operation. Other
      // positions or pendings with the same symbol/side may be a new thesis;
      // neither their age nor their symbol can attach them to the old record.
      if(g_stop_genesis_closed)
        { reason="Referência Gênese encerrada; selecione a nova operação";
          return(false); }
      if(!g_stop_genesis_closed)
        {
         bool found=false;
         for(int i=0;i<ArraySize(rows);i++)
            if(rows[i].kind==JPW_STOP_RISK_POSITION &&
               rows[i].identifier==reference.identifier &&
               rows[i].symbol==symbol && rows[i].side==side)
               { found=true; break; }
         if(!found)
           { reason="Referência registrada ausente; encerramento não confirmado"; return(false); }
        }
      return(true);
     }
   if(state!=JPW_GENESIS_ABSENT)
     { reason="Registro Gênese ocupado, inválido ou incompatível"; return(false); }
   // The only automatic scope is one exact symbol-and-side group of open
   // positions. Pending orders alone cannot establish an operation.
   long oldest=LONG_MAX;
   int oldest_count=0,position_count=0;
   for(int i=0;i<ArraySize(rows);i++)
     {
      if(rows[i].kind!=JPW_STOP_RISK_POSITION) continue;
      if(rows[i].side!=1 && rows[i].side!=-1)
        { reason="Direção de posição não confirmada"; return(false); }
      if(position_count==0)
        { symbol=rows[i].symbol; side=rows[i].side; }
      else if(rows[i].symbol!=symbol || rows[i].side!=side)
        { reason="Vários grupos de posições; selecione a referência"; return(false); }
      position_count++;
      if(rows[i].opened_msc<oldest)
        { oldest=rows[i].opened_msc; oldest_count=1;
          g_stop_genesis_identifier=rows[i].identifier;
          g_stop_genesis_ticket=rows[i].ticket;
          g_stop_genesis_opened_msc=rows[i].opened_msc; }
      else if(rows[i].opened_msc==oldest) oldest_count++;
     }
   if(position_count==0)
     { reason="Sem Gênese registrada ou posição aberta para atribuir pendentes"; return(false); }
   if(oldest<=0 || oldest_count!=1)
     { reason="A posição mais antiga não é inequívoca"; return(false); }
   provenance="Inferred";
   return(true);
  }

void JPWCollectStopRisk()
  {
   g_stop_observer_presence=JPW_OBSERVER_CONTEXT_UNAVAILABLE;
   JPWStopRiskUnavailable("Aguardando amostra atual do EA observador");
   JPWAccount before,after;
   if(!JPWReadAccount(before))
     { JPWStopRiskUnavailable("Conta indisponível"); return; }
   string key="",reason="";
   if(!JPWStopRiskKey(before,key))
     { JPWStopRiskUnavailable("Identidade local indisponível"); return; }
   g_stop_observer_presence=JPWObserverPresenceRead(key);
   JPWStopRiskSample sample;
   JPWStopRiskRow rows[];
   if(!JPWStopRiskReadLiveCurrent(key,sample,rows,reason))
     { JPWStopRiskUnavailableWithPresence(reason); return; }
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after))
     { JPWStopRiskUnavailable("Conta alterada durante a leitura"); return; }
   g_stop_sample=sample;
   ArrayResize(g_stop_rows,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++) g_stop_rows[i]=rows[i];
   g_stop_ready=true; // The sample can still be N/A for an ambiguous operation.
   string live_digest="";
   if(!JPWStopRiskLiveDigest(key,live_digest,reason) ||
      live_digest!=sample.composition_digest ||
      !JPWReadAccount(after) || !JPWAccountsEqual(before,after))
     { JPWStopRiskUnavailable("Conta ou composição alterada durante a leitura"); return; }
   if(sample.row_count==0 && ArraySize(rows)==0 &&
      sample.margin_mode==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
      JPWFinitePositive(sample.balance))
     {
      g_stop_total_money=0.0; g_stop_total_percent=0.0;
      g_stop_positions_money=0.0; g_stop_pending_money=0.0;
      g_stop_additional_money=0.0;
      g_stop_value="0,00 "+sample.currency+" · 0,00% balance";
      g_stop_quality=JPW_VIEW_CURRENT;
      g_stop_reason="No open positions or pending orders";
      g_stop_detail="Ausência de posições e pendentes confirmada pelo EA, "+
         "identidade e composição revalidadas; total zero desta amostra.";
      return;
     }
   string symbol="",provenance="";
   int side=0;
   if(!JPWStopRiskResolveScope(before,rows,symbol,side,provenance,reason))
     { g_stop_reason=reason; g_stop_detail=reason; return; }
   g_stop_scope_valid=true; g_stop_scope_symbol=symbol;
   g_stop_scope_side=side; g_stop_provenance=provenance;
   g_stop_excluded=0;
   for(int i=0;i<ArraySize(rows);i++)
      if(rows[i].symbol!=symbol || rows[i].side!=side) g_stop_excluded++;
   double total=0.0,percent=0.0,positions=0.0,pending=0.0,additional=0.0;
   if(!JPWStopRiskAggregate(sample,rows,symbol,side,total,percent,
                            positions,pending,additional,reason))
     { g_stop_reason=reason; g_stop_detail="Total indisponível: "+reason; return; }
   if(!MathIsValidNumber(total) || total<0.0 || !MathIsValidNumber(percent) ||
      percent<0.0 || !JPWFinitePositive(sample.balance))
     { g_stop_reason="Total ou balance inválido"; g_stop_detail=g_stop_reason; return; }
   g_stop_total_money=total; g_stop_total_percent=percent;
   g_stop_positions_money=positions; g_stop_pending_money=pending;
   g_stop_additional_money=additional;
   g_stop_value=JPWStopRiskMoney(total)+" "+sample.currency+" · "+
                JPWFormatPercent(percent,false)+" balance";
   g_stop_quality=JPW_VIEW_CURRENT;
   g_stop_reason="Agrupamento símbolo + direção inferido; EA e dados atuais";
   g_stop_detail="Símbolo exato "+symbol+" · "+(side>0 ? "BUY" : "SELL")+
      " · "+provenance+". Agrupamento por símbolo e direção inferido; "+
      "outra tese no mesmo par pode estar incluída. Posições "+
      JPWStopRiskMoney(positions)+
      "; reservas pendentes "+JPWStopRiskMoney(pending)+" "+sample.currency+
      ". Balance atual "+JPWStopRiskMoney(sample.balance)+" "+sample.currency+
      ". Amostra "+TimeToString((datetime)sample.observed_utc,TIME_DATE|TIME_SECONDS)+
      " UTC (relógio do computador). "+
      (g_stop_excluded>0 ? IntegerToString(g_stop_excluded)+
       " linha(s) de outro instrumento/direção excluída(s). " : "")+
      "Informativo sobre balance; não é Risco Comprometido ou perda máxima.";
  }

void JPWDetailsReadStopRisk()
  {
   g_stop_last_ready=false;
   g_stop_last_reason="Nenhuma amostra gravada confirmada.";
   ArrayResize(g_stop_last_rows,0);
   JPWAccount before,after;
   if(!JPWReadAccount(before))
     { g_stop_last_reason="Conta indisponível"; return; }
   string key="",reason="";
   if(!JPWStopRiskKey(before,key))
     { g_stop_last_reason="Identidade local indisponível"; return; }
   JPWStopRiskSample sample;
   JPWStopRiskRow rows[];
   if(!JPWStopRiskReadCurrent(key,sample,rows,reason))
     { g_stop_last_reason=reason; return; }
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after))
     { g_stop_last_reason="Conta alterada durante a consulta"; return; }
   g_stop_last_sample=sample;
   ArrayResize(g_stop_last_rows,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++) g_stop_last_rows[i]=rows[i];
   g_stop_last_ready=true;
   g_stop_last_scope_valid=JPWStopRiskResolveScope(before,rows,g_stop_last_scope_symbol,
          g_stop_last_scope_side,g_stop_last_provenance,g_stop_last_scope_reason);
   g_stop_last_reason="Última geração gravada em "+
      TimeToString((datetime)sample.observed_utc,TIME_DATE|TIME_SECONDS)+
      " UTC (relógio do computador); histórico, não risco ativo.";
  }

void JPWInvalidateIdentityPresentation()
  {
   JPWPositionsInvalidate("Contexto alterado; catálogo anterior descartado");
   g_stop_observer_presence=JPW_OBSERVER_CONTEXT_UNAVAILABLE;
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++) JPWSampleInvalidate(g_metric_samples[i],JPW_SAMPLE_CONTEXT_CHANGED);
   JPWQueueDiagnostic(JPW_DIAG_CONTEXT_CHANGED);
   g_sample_context=""; g_diagnostic_context="";
   g_record_read_stage=0; g_record_read_requested=false;
   g_mdd_summary="Registro ainda não consultado nesta conta."; g_mdd_context="";
   g_observer_summary="Observador ainda não consultado nesta conta."; g_observer_context="";
   g_diagnostic_summary="Diagnóstico ainda não consultado nesta conta.";
   g_diagnostic_state=JPW_STORE_ABSENT; g_diagnostic_reason="";
   g_saved_raiz_line="Raiz N: N/D — confirme o cenário desta conta";
   g_saved_raiz_tooltip="Cenário anterior descartado da apresentação após troca de contexto.";
   g_raiz_store_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE;
   JPWRaizNClearScenario(g_raiz_scenario); JPWRaizNClearBinding(g_raiz_binding);
   g_raiz_comparison="Vínculo ainda não consultado nesta conta.";
   g_raiz_draft_expected_id="";
   for(int i=0;i<21;i++) g_raiz_fields[i]="";
   g_live_config_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE; g_live_key="";
   JPWRaizNConfigClear(g_live_config);
   g_factor_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE; g_factor_key="";
   JPWRaizNFactorClear(g_factor_preference);
   g_export_preview=""; g_export_preview_requested=false; g_export_requested=false;
   JPWClearRaizLiveSample("Identidade da conta alterada; amostra descartada");
   g_raiz_details_open=false; g_raiz_draft_account_known=false;
   JPWRaizPanelDestroy();
   g_panel_value="N/D";
   g_panel_status="Indisponível — identidade da conta alterada";
   g_leverage_reason="Identidade alterada";
   g_leverage_quality=JPW_VIEW_NA;
   g_floating_quality=JPW_VIEW_NA;
   g_genesis_quality=JPW_VIEW_NA;
   g_raiz_quality=JPW_VIEW_NA;
   g_scale2_quality=JPW_VIEW_NA;
   g_stop_quality=JPW_VIEW_NA;
   g_floating_value="N/A"; g_genesis_value="N/A";
   g_raiz_value="N/A"; g_scale2_value="N/A";
   g_floating_reason="Identidade alterada";
   g_genesis_reason="Identidade alterada";
   g_raiz_reason="Identidade alterada"; g_scale2_reason="Identidade alterada";
   g_stop_value="N/A"; g_stop_reason="Identidade alterada";
   g_stop_detail="Amostra anterior recusada após troca de conta.";
   g_stop_ready=false; g_stop_scope_valid=false;
   g_stop_last_ready=false; ArrayResize(g_stop_last_rows,0);
   ArrayResize(g_stop_table_rows,0); g_stop_button_count=0;
   g_stop_selected_row=-1;
   g_floating_line="Floating P/L: N/A";
   g_dd_line="DD / saldo: N/D";
   g_floating_short="P/L: N/A";
   g_dd_short="DD: N/D";
   g_floating_tooltip="Flutuante / saldo indisponível: confirme a conta atual.";
   g_dd_tooltip="DD / saldo indisponível: confirme a conta atual.";
   g_genesis_line="Genesis SL: N/A";
   g_genesis_short="SL: N/A";
   g_genesis_tooltip="Distância ao SL indisponível: confirme a conta atual.";
   g_raiz_line="Raiz N diag. 1W: N/A";
   g_raiz_short="RN1W: N/A";
   g_raiz_tooltip="Identidade da conta alterada; amostra descartada.";
   g_scale2_line="Raiz N diag. 2W: N/A";
   g_scale2_short="RN2W: N/A";
   g_scale2_tooltip=g_raiz_tooltip;
  }

void JPWPositionsMonitorInventory()
  {
   if(!g_positions_view.catalog_valid || !JPWCoordinatorBudgetRemaining()) return;
   if(g_positions_view.accepted_monotonic_ms>=g_cycle_started_ms) return; // Just revalidated this cycle.
   if(!JPWPositionsViewCurrent(g_sample_context,GetTickCount64()))
     { JPWPositionsInvalidate("Catálogo vencido; aguardando atualização");
       g_refresh_requested=true; return; }
   JPWPositionView observed[];
   JPWAccount current;
   string reason="";
   if(!JPWReadAccount(current) || !JPWAccountsEqual(current,g_account) ||
      !JPWPositionsReadMetadata(observed,g_cycle_started_ms,reason) ||
      !JPWPositionsMetadataEqual(g_position_views,observed) ||
      !JPWReadAccount(current) || !JPWAccountsEqual(current,g_account))
     {
      JPWPositionsInvalidate("Posições, volume ou SL/TP alterados; aguardando nova leitura");
      g_refresh_requested=true;
     }
  }

void JPWMonitorStopRisk()
  {
   JPWPositionsMonitorInventory();
   if(!JPWCoordinatorBudgetRemaining()) return;
   JPWAccount visible_account;
   const bool identity_current=(!g_account_known ||
      (JPWReadAccount(visible_account) &&
       JPWAccountsEqual(g_account,visible_account)));
   if(!identity_current) JPWInvalidateIdentityPresentation();
   const bool stop_was_ready=g_stop_ready;
   JPWAccount stop_account;
   if(identity_current && g_account_known && JPWReadAccount(stop_account) &&
      JPWAccountsEqual(g_account,stop_account)) JPWCollectStopRisk();
   else
     { g_stop_observer_presence=JPW_OBSERVER_CONTEXT_UNAVAILABLE;
       JPWStopRiskUnavailable("Conta indisponível ou alterada"); }
   // The account may change during the observer's database/digest read. No
   // old-account metric may reach the HUD even in that race.
   if(g_account_known &&
      (!JPWReadAccount(visible_account) ||
       !JPWAccountsEqual(g_account,visible_account)))
      JPWInvalidateIdentityPresentation();
   if(g_raiz_details_open && g_raiz_tab>=JPW_ROUTE_OVERVIEW)
     {
      // The cockpit is an inspection of the current collector cycle. Rebuild
      // it after every Stop risk check, even when other metrics are throttled.
      if((g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW) && stop_was_ready && !g_stop_ready)
         JPWDetailsReadStopRisk();
      JPWStopRiskRefreshRowView();
      JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();
     }
   g_numeric_values[5]=g_stop_total_money;
   g_numeric_valid[5]=(g_stop_quality==JPW_VIEW_CURRENT);
   g_source_times[5]=g_stop_ready ? g_stop_sample.observed_utc*1000 : 0;
   JPWAcceptMetric(5);
  }

bool JPWFullReadingExpired(const ulong now_ms,const ulong last_ms)
  {
   return(last_ms>0 && (now_ms<last_ms || now_ms-last_ms>30000));
  }

void JPWExpireTimedMetrics()
  {
   const ulong now_ms=GetTickCount64();
   if(!JPWFullReadingExpired(now_ms,g_last_full_refresh_ms)) return;
   JPWPositionsInvalidate("Catálogo vencido; aguardando nova leitura completa");
   const string when=(g_last_full_refresh_utc>0 ?
      TimeToString((datetime)g_last_full_refresh_utc,TIME_DATE|TIME_SECONDS)+
      " UTC (computador)" : "horário indisponível");
   const string reason="Sem nova apuração completa em 30 s; última tentativa "+
                       when+". Valor anterior retirado, não é leitura atual.";
   // These five metrics require a complete collector cycle. A retained
   // number is not an estimate calculated from current terminal data.
   for(int i=0;i<5;i++) JPWSampleInvalidate(g_metric_samples[i],JPW_SAMPLE_EXPIRED);
   g_panel_value="N/D"; g_panel_status=reason;
   g_leverage_quality=JPW_VIEW_NA; g_leverage_reason=reason;
   g_floating_quality=JPW_VIEW_NA; g_floating_value="N/A";
   g_floating_reason=reason;
   g_floating_line="Floating P/L: N/A"; g_floating_short="P/L: N/A";
   g_floating_tooltip=reason;
   g_dd_line="DD / saldo: N/D"; g_dd_short="DD: N/D"; g_dd_tooltip=reason;
   g_genesis_quality=JPW_VIEW_NA; g_genesis_value="N/A";
   g_genesis_reason=reason; g_genesis_line="Genesis SL: N/A";
   g_genesis_short="SL: N/A"; g_genesis_tooltip=reason;
   g_raiz_quality=JPW_VIEW_NA; g_raiz_value="N/A"; g_raiz_reason=reason;
   g_raiz_line="Raiz N diag. 1W: N/A"; g_raiz_short="RN1W: N/A";
   g_raiz_tooltip=reason;
   g_scale2_quality=JPW_VIEW_NA; g_scale2_value="N/A";
   g_scale2_reason=reason; g_scale2_line="Raiz N diag. 2W: N/A";
   g_scale2_short="RN2W: N/A"; g_scale2_tooltip=reason;
  }

void JPWPositionsCollectCatalogOnly()
  {
   // Financial availability is independent from inventory. This fallback is
   // timer-only and never called by drawing, clicks, or record navigation.
   if(g_positions_catalog_attempted || !g_account_known || g_sample_context=="" ||
      !JPWCoordinatorBudgetRemaining()) return;
   g_positions_catalog_attempted=true;
   JPWAccount first_account,last_account;
   JPWPosition first[],last[];
   JPWPositionView first_metadata[],last_metadata[];
   string reason="";
   const bool connected=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
   ResetLastError(); const long margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(GetLastError()!=0 || !JPWReadAccount(first_account) ||
      !JPWAccountsEqual(first_account,g_account) || !JPWReadSnapshot(first) ||
      (ArraySize(first)==0 && !connected) ||
      !JPWPositionsReadMetadata(first_metadata,g_cycle_started_ms,reason) ||
      !JPWReadSnapshot(last) ||
      !JPWPositionsReadMetadata(last_metadata,g_cycle_started_ms,reason) ||
      !JPWReadAccount(last_account) || !JPWAccountsEqual(first_account,last_account) ||
      !JPWPositionsEqual(first,last) || !JPWPositionsMetadataEqual(first_metadata,last_metadata) ||
      !JPWPositionsMatchSnapshot(last_metadata,last) ||
      connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED) ||
      !JPWCoordinatorBudgetRemaining()) return;
   ResetLastError(); const long last_margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(GetLastError()!=0 || last_margin_mode!=margin_mode ||
      !JPWCoordinatorBudgetRemaining()) return;
   JPWPositionsStageCatalog(last_metadata,last,g_sample_context,margin_mode,g_diagnostic_context);
  }

void JPWAcceptCollection(const string value,const string state="")
  {
   JPWPositionsCollectCatalogOnly();
   // Resolve the fourth line after the established account/leverage collectors.
   // It shares their 500 ms window and cannot delay or invalidate their result.
   const bool collect_genesis=g_genesis_due && JPWCoordinatorBudgetRemaining();
   const bool collect_raiz=g_raiz_due;
   if(collect_genesis)
     {
      g_genesis_due=false;
      JPWCollectGenesis(g_genesis_refresh_account,g_genesis_refresh_connected,
                        g_genesis_refresh_clock_valid,g_genesis_refresh_now_ms,
                        g_genesis_refresh_started);
     }
   bool accepted_raiz=false;
   if(collect_raiz && JPWCoordinatorBudgetRemaining())
     {
      accepted_raiz=true;
      g_raiz_due=false;
      JPWCollectRaizN();
     }
   string shown_value=value;
   string shown_state=state;
   JPWAccount visible_account;
   if(g_account_known &&
      (!JPWReadAccount(visible_account) || !JPWAccountsEqual(g_account,visible_account)))
     {
      JPWInvalidateIdentityPresentation();
      shown_value="N/D";
      shown_state="Indisponível — identidade da conta alterada";
     }
   g_panel_value=shown_value;
   g_panel_status=shown_state;
   g_leverage_reason=(shown_state=="" ? "Aguardando leitura" : shown_state);
   // Independent observer read: leverage conversion failure does not hide a
   // coherent Stop risk sample, and a changed account cannot display old data.
   JPWAcceptMetric(0);
   JPWPositionsPublish(g_metric_samples[0],
      (g_position_math_reason!="" ? g_position_math_reason : g_leverage_reason));
   JPWAcceptMetric(1);
   if(collect_genesis) JPWAcceptMetric(2);
   if(accepted_raiz) { JPWAcceptMetric(3); JPWAcceptMetric(4); }
   if(g_genesis_due || g_raiz_due)
     { g_refresh_requested=true; JPWQueueDiagnostic(JPW_DIAG_BUDGET_DEFERRED); }
   JPWMonitorStopRisk();
   JPWRefreshRequestedRecords();
   JPWConfirmAcceptedContext();
   JPWRenderCurrentDisplay();
  }

bool JPWReadAccountMetric(const ENUM_ACCOUNT_INFO_DOUBLE property,double &value)
  {
   ResetLastError();
   value=AccountInfoDouble(property);
   return(GetLastError()==0 && MathIsValidNumber(value));
  }

void JPWMetricUnavailable(const string reason)
  {
   g_floating_quality=JPW_VIEW_NA;
   g_floating_value="N/A";
   g_floating_reason=reason;
   g_floating_line="Floating P/L: N/A";
   g_dd_line="DD / saldo: N/D";
   g_floating_short="P/L: N/A";
   g_dd_short="DD: N/D";
   g_floating_tooltip="Flutuante / saldo indisponível: "+reason;
   g_dd_tooltip="DD / saldo indisponível: "+reason;
  }

bool JPWCollectAccountMetrics(JPWAccount &account,const bool connected,
                              const bool clock_valid)
  {
   const ulong started=g_cycle_started_ms;
   for(int attempt=0;attempt<2;attempt++)
     {
      JPWMetricUnavailable("aguardando leitura consistente da conta");
      if(!JPWWithinBudget(started)) return(false);
      double balance=0.0,equity=0.0,profit=0.0,credit=0.0;
      const bool have_balance=JPWReadAccountMetric(ACCOUNT_BALANCE,balance);
      const bool have_equity=JPWReadAccountMetric(ACCOUNT_EQUITY,equity);
      const bool have_profit=JPWReadAccountMetric(ACCOUNT_PROFIT,profit);
      const bool have_credit=JPWReadAccountMetric(ACCOUNT_CREDIT,credit);
      JPWAccount after;
      double checked_balance=0.0,checked_credit=0.0;
      const bool same_account=JPWReadAccount(after) && JPWAccountsEqual(account,after);
      const bool balance_rechecked=JPWReadAccountMetric(ACCOUNT_BALANCE,checked_balance);
      const bool credit_rechecked=JPWReadAccountMetric(ACCOUNT_CREDIT,checked_credit);
      const bool changed=!same_account ||
            have_balance!=balance_rechecked || have_credit!=credit_rechecked ||
            (have_balance && balance!=checked_balance) ||
            (have_credit && credit!=checked_credit) ||
            connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
      if(changed)
        {
         if(attempt==0 && JPWWithinBudget(started)) continue;
         JPWMetricUnavailable("identidade, saldo ou contexto alterados durante a leitura");
         return(false);
        }
      if(!have_balance || !JPWFinitePositive(balance))
        { JPWMetricUnavailable("saldo ausente ou não positivo"); return(true); }
      // Credit is context, not an operand. If it cannot be confirmed, the two
      // ratios remain calculable but cannot be classed Current or persisted.
      const bool estimated=!connected || !clock_valid || !have_credit;
      const string quality=(estimated ? "Estimated" : "Current");
      const string suffix=(estimated ? " · Estimated" : "");
      const string credit_context=(have_credit ? "" : " Crédito não confirmado no terminal.");
      const datetime observed_at=TimeGMT();
      const string time_text=(observed_at>0 ?
                              TimeToString(observed_at,TIME_DATE|TIME_SECONDS)+" UTC (relógio do computador)" :
                              "horário local indisponível");
      double floating=0.0;
      if(have_profit && JPWFloatingPercent(balance,profit,floating))
        {
         const string percent=JPWFormatPercent(floating,true);
         g_floating_quality=(estimated ? JPW_VIEW_ESTIMATED : JPW_VIEW_CURRENT);
         g_floating_value=percent;
         g_numeric_values[1]=floating; g_numeric_valid[1]=true;
         g_floating_reason=(estimated ? "Conexão ou tempo não confirmado" : "Dados da conta confirmados");
         g_floating_line="Floating P/L: "+percent+suffix;
         g_floating_short="P/L: "+percent+(estimated ? " ≈" : "");
         g_floating_tooltip="Flutuante / saldo: 100 × lucro flutuante / saldo. "+
                            quality+"; observado pelo indicador em "+time_text+
                            ". Crédito não integra a fórmula."+credit_context;
        }
      else
         g_floating_tooltip="Flutuante / saldo indisponível: lucro flutuante inválido ou ausente.";
      double dd=0.0;
      if(have_equity && JPWBalanceDDPercent(balance,equity,dd))
        {
         const string percent=JPWFormatPercent(dd,false);
         g_dd_line="DD / saldo: "+percent+suffix;
         g_dd_short="DD: "+percent+(estimated ? " ≈" : "");
         string persistence="Registro local: amostra Estimated; máximo não atualizado.";
         if(!estimated && observed_at>0 && JPWWithinBudget(started))
           {
            JPWAccount before_write;
            double write_balance=0.0,write_credit=0.0;
            if(!JPWReadAccount(before_write) ||
               !JPWAccountsEqual(account,before_write) ||
               !JPWReadAccountMetric(ACCOUNT_BALANCE,write_balance) ||
               !JPWReadAccountMetric(ACCOUNT_CREDIT,write_credit) ||
               write_balance!=balance || write_credit!=credit ||
               connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
              {
               if(attempt==0 && JPWWithinBudget(started)) continue;
               JPWMetricUnavailable("identidade, saldo ou contexto alterados antes do registro");
               return(false);
              }
            JPWMDDRecord confirmed;
            const JPW_MDD_STATE stored=JPWMDDObserve(account,balance,equity,dd,
                              observed_at,JPW_PRODUCT_VERSION,JPW_MDD_FOLDER,confirmed);
            if(stored==JPW_MDD_BUSY) JPWQueueDiagnostic(JPW_DIAG_STORAGE_BUSY);
            else if(stored==JPW_MDD_INCOMPATIBLE) JPWQueueDiagnostic(JPW_DIAG_STORAGE_INCOMPATIBLE);
            else if(stored==JPW_MDD_INVALID) JPWQueueDiagnostic(JPW_DIAG_STORAGE_CORRUPT);
            else if(stored!=JPW_MDD_VALID) JPWQueueDiagnostic(JPW_DIAG_WRITE_FAILED);
            if(stored==JPW_MDD_VALID) persistence="Registro local: máximo observado confirmado.";
            else if(stored==JPW_MDD_BUSY) persistence="Registro local: indisponível ou ocupado; gravação não confirmada.";
            else if(stored==JPW_MDD_INCOMPATIBLE) persistence="Registro local: versão incompatível; escrita bloqueada.";
            else if(stored==JPW_MDD_INVALID) persistence="Registro local: dados inválidos; escrita bloqueada.";
            else persistence="Registro local: gravação não confirmada.";
           }
         else if(!estimated) persistence="Registro local: observação sem horário ou fora do orçamento; escrita adiada.";
         g_dd_tooltip="DD / saldo: 100 × máx(0, saldo − equity) / saldo. "+
                      quality+"; observado pelo indicador em "+time_text+
                      ". Não é DD pico-a-vale nem o limite normativo. Crédito é apenas contexto."+
                      credit_context+"\n"+
                      persistence;
        }
      else
         g_dd_tooltip="DD / saldo indisponível: equity inválido ou ausente.";
      return(true);
     }
   return(false);
  }

bool JPWSameSpecification(JPWInstrument &a,JPWInstrument &b)
  {
   return(a.symbol==b.symbol && a.calc_mode==b.calc_mode && a.base==b.base &&
          a.profit==b.profit && a.contract_size==b.contract_size &&
          a.underlying_verified==b.underlying_verified);
  }

bool JPWPositionsBudgetBreakdown(JPWPosition &positions[],JPWInstrument &instruments[],
   JPWQuote &quotes[],const string target,const long now_ms,const int max_age_sec,
   const bool clock_valid,const bool connected,double &scales[],JPWRoute &routes[],
   const double expected_gross,const ulong started,double &amounts[])
  {
   ArrayResize(amounts,0);
   const int count=ArraySize(positions);
   if(count!=ArraySize(instruments) || count!=ArraySize(scales)) return(false);
   double candidate[]; JPWRoute frozen_routes[];
   if(ArrayResize(candidate,count)!=count ||
      ArrayResize(frozen_routes,ArraySize(routes))!=ArraySize(routes)) return(false);
   for(int i=0;i<ArraySize(routes);i++) frozen_routes[i]=routes[i];
   double complete=0.0;
   for(int i=0;i<count;i++)
     {
      const ulong now=GetTickCount64();
      if(now<started || now-started>=250) return(false);
      double gross=0.0;
      if(JPWPositionsOneGross(positions[i],instruments[i],quotes,target,now_ms,max_age_sec,
         clock_valid,connected,scales[i],frozen_routes,gross)!=JPW_OK) return(false);
      candidate[i]=gross; complete+=gross;
     }
   const ulong finished=GetTickCount64();
   if(finished<started || finished-started>=250 ||
      !JPWPositionsNear(complete,expected_gross) || ArrayResize(amounts,count)!=count) return(false);
   for(int i=0;i<count;i++) amounts[i]=candidate[i];
   return(true);
  }

JPW_RESULT JPWCollectReading(JPWPosition &positions[],JPWAccount &account,
                            const string currency,const bool usc,const long now_ms,
                            const ulong started,const bool clock_valid,const bool connected,
                            double &gross,bool &estimated,long &oldest)
  {
   JPWInstrument instruments[];
   JPWQuote quotes[];
   double scales[];
   JPWProfileEntry profile[];
   gross=0.0; estimated=true; oldest=0; g_used_unsynchronized=false;
   ArrayResize(g_position_candidate_gross,0);
   g_position_math_reason="Contribuições ainda não confirmadas";
   const int count=ArraySize(positions);
   if(ArrayResize(instruments,count)!=count || ArrayResize(scales,count)!=count) return(JPW_CALC_ERROR);
   if(usc && !JPWProfileLoad(account,profile)) return(JPW_UNVERIFIED_UNITS);
   g_quotes_pending=false; g_budget_exceeded=false;
   ArrayResize(g_unsynchronized_symbols,0);
   for(int i=0;i<count;i++)
     {
      if(!JPWWithinBudget(started) || !JPWReadSpecification(positions[i].symbol,instruments[i])) return(JPW_CALC_ERROR);
      JPW_MODEL model=JPW_MODEL_NONE;
      const JPW_RESULT classified=JPWClassify(instruments[i],model);
      if(classified!=JPW_OK) return(classified);
      scales[i]=1.0;
      if(usc && !JPWProfileFind(instruments[i],profile,scales[i])) return(JPW_UNVERIFIED_UNITS);
      JPWCaptureQuote(positions[i].symbol,instruments[i].base,instruments[i].profit,quotes,model==JPW_MODEL_FIAT_FOREX);
      const string source=(model==JPW_MODEL_FIAT_FOREX ? instruments[i].base : instruments[i].profit);
      if(!JPWPreparedRoute(source,currency,quotes,now_ms,started,clock_valid,connected,InpMaxQuoteAgeSeconds)) return(JPW_NO_CONVERSION);
      // USC tick-value consistency is checked in profit currency, not base currency.
      if(usc && !JPWPreparedRoute(instruments[i].profit,"USD",quotes,now_ms,started,clock_valid,connected,InpMaxQuoteAgeSeconds)) return(JPW_NO_CONVERSION);
     }
   for(int i=0;i<count;i++)
     {
      if(usc && !JPWProfileTickConsistent(instruments[i],scales[i],account,quotes,now_ms,clock_valid,connected)) return(JPW_UNVERIFIED_UNITS);
      JPWInstrument later;
      if(!JPWReadSpecification(positions[i].symbol,later) || !JPWSameSpecification(instruments[i],later)) return(JPW_CALC_ERROR);
      if(usc && !JPWProfileFind(later,profile,scales[i])) return(JPW_UNVERIFIED_UNITS);
     }
   for(int q=0;q<ArraySize(quotes);q++)
      if(quotes[q].conversion_pair && !JPWConversionMetadata(quotes[q].symbol,quotes[q].base,quotes[q].profit))
        { g_catalog_ready=false; g_scan_total=0; return(JPW_NO_CONVERSION); }
   if(!JPWWithinBudget(started)) return(JPW_CALC_ERROR);
   const JPW_RESULT result=JPWGrossReading(positions,instruments,quotes,currency,now_ms,InpMaxQuoteAgeSeconds,
                                         clock_valid,connected,scales,g_routes,gross,estimated,oldest);
   if(result!=JPW_OK) return(result);
   for(int i=0;i<count;i++)
     {
      if(JPWWasUnsynchronized(instruments[i].symbol)) { estimated=true; g_used_unsynchronized=true; }
      JPW_MODEL model=JPW_MODEL_NONE;
      JPWClassify(instruments[i],model);
      const string source=(model==JPW_MODEL_FIAT_FOREX ? instruments[i].base : instruments[i].profit);
      for(int j=0;j<ArraySize(g_routes);j++)
         if(g_routes[j].source==source && g_routes[j].target==currency &&
            (JPWWasUnsynchronized(g_routes[j].first_symbol) || JPWWasUnsynchronized(g_routes[j].second_symbol)))
            { estimated=true; g_used_unsynchronized=true; }
      // The auxiliary FX observation used to confirm USC tick units also
      // contributes to data quality, even if gross notional used another route.
      if(usc && instruments[i].profit!="USD")
        {
         JPWRoute previous; previous.valid=false;
         JPWRoute chosen;
         double rate=0.0;
         bool auxiliary_estimated=false;
         long auxiliary_oldest=0;
         if(!JPWFindRouteReading(instruments[i].profit,"USD",quotes,now_ms,30,
                                 clock_valid,connected,previous,chosen,rate,
                                 auxiliary_estimated,auxiliary_oldest)) return(JPW_UNVERIFIED_UNITS);
         double checked_rate=0.0;
         if(auxiliary_estimated || !JPWRouteRate(chosen,quotes,now_ms,InpMaxQuoteAgeSeconds,checked_rate)) estimated=true;
         if(auxiliary_oldest>0 && (oldest==0 || auxiliary_oldest<oldest)) oldest=auxiliary_oldest;
         if(JPWWasUnsynchronized(chosen.first_symbol) || JPWWasUnsynchronized(chosen.second_symbol))
           { estimated=true; g_used_unsynchronized=true; }
        }
     }
   // Expose the existing pure core on the same frozen inputs. Failure of this
   // optional breakdown does not reinterpret or invalidate account leverage.
   if(JPWWithinBudget(started))
     {
      const bool breakdown=JPWPositionsBudgetBreakdown(positions,instruments,quotes,
         currency,now_ms,InpMaxQuoteAgeSeconds,clock_valid,connected,scales,g_routes,
         gross,started,g_position_candidate_gross);
      g_position_math_reason=(breakdown ? "" :
         "Contribuições indisponíveis ou adiadas; alavancagem da conta preservada");
     }
   else g_position_math_reason="Contribuições adiadas pelo orçamento do ciclo";
   return(JPW_OK);
  }

string JPWErrorText(const JPW_RESULT status)
  {
   if(status==JPW_BAD_EQUITY) return("Equity inválido ou ausente");
   if(status==JPW_UNSUPPORTED_CONTRACT) return("Contrato não suportado");
   if(status==JPW_UNVERIFIED_UNITS) return("Verifique os contratos USC");
   if(status==JPW_NO_CONVERSION) return("Sem cotação para conversão");
   if(status==JPW_BAD_QUOTE) return("Sem cotação válida para instrumento");
   return("Não foi possível confirmar os dados");
  }

void JPWGenesisUnavailable(const string reason)
  {
   g_genesis_quality=JPW_VIEW_NA;
   g_genesis_value="N/A";
   g_genesis_reason=reason;
   g_genesis_line="Genesis SL: N/A";
   g_genesis_short="SL: N/A";
   g_genesis_tooltip="Distância ao SL da referência indisponível: "+reason+
                     ". As outras métricas não dependem desta leitura.";
  }

void JPWGenesisState(const string visible,const string brief,const string detail,
                     const JPW_VIEW_QUALITY quality,const string value)
  {
   g_genesis_quality=quality;
   g_genesis_value=value;
   g_genesis_reason=(quality==JPW_VIEW_CURRENT ? "Cotação recente" : "Cotação ou referência temporal não comprovada");
   g_genesis_line=visible;
   g_genesis_short=brief;
   g_genesis_tooltip=detail+". A referência permanece vinculada; as demais métricas são independentes.";
  }

string JPWGenesisStoreReason(const JPW_GENESIS_STORE_STATE state)
  {
   if(state==JPW_GENESIS_BUSY) return("registro local ocupado; tente no próximo ciclo");
   if(state==JPW_GENESIS_INVALID) return("registro local corrompido; seleção bloqueada");
   if(state==JPW_GENESIS_INCOMPATIBLE) return("versão do registro incompatível; seleção bloqueada");
   if(state==JPW_GENESIS_ACCOUNT_UNAVAILABLE) return("identidade da conta indisponível");
   if(state==JPW_GENESIS_IO_ERROR) return("falha ao ler ou gravar o registro local");
   return("referência não confirmada");
  }

void JPWCollectGenesis(JPWAccount &account,const bool connected,
                       const bool clock_valid,const long now_ms,
                       const ulong started)
  {
   JPWGenesisUnavailable("aguardando leitura completa da conta");
   for(int attempt=0;attempt<2;attempt++)
     {
      if(!JPWWithinBudget(started))
        { JPWGenesisUnavailable("leitura fora do orçamento; atualizando"); return; }
      JPWGenesisPosition before[],after[],candidate;
      JPWGenesisClear(candidate);
      JPWAccount later;
      if(!JPWReadGenesisSnapshot(before))
        { JPWGenesisUnavailable("posições não confirmadas"); return; }
      JPWGenesisRecord saved;
      const JPW_GENESIS_STORE_STATE stored=JPWGenesisRead(account,InpGenesisTicket,
                                                           JPW_GENESIS_FOLDER,saved);
      if(stored!=JPW_GENESIS_VALID && stored!=JPW_GENESIS_ABSENT)
        { JPWGenesisUnavailable(JPWGenesisStoreReason(stored)); return; }
      JPW_GENESIS_SELECTION selected=JPW_GENESIS_SELECT_NONE;
      bool found=false;
      if(stored==JPW_GENESIS_ABSENT)
        {
         selected=JPWGenesisSelect(before,(ulong)InpGenesisTicket,candidate);
         found=(selected==JPW_GENESIS_SELECT_OK);
        }
      else if(saved.reference_state==JPW_GENESIS_ACTIVE)
         found=JPWGenesisFindByIdentifier(before,saved.identifier,candidate);

      ResetLastError();
      long mode_before=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
      if(GetLastError()!=0)
        { JPWGenesisUnavailable("modo de margem da conta indisponível"); return; }
      if(mode_before!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
         mode_before!=ACCOUNT_MARGIN_MODE_RETAIL_NETTING)
        { JPWGenesisUnavailable("conta de execução em bolsa fora desta métrica"); return; }
      long execution_before=0,selected_symbol=0;
      bool supported=false;
      double point=0.0,tick_size=0.0;
      long digits=0;
      MqlTick quote={};
      bool have_quote=false,synchronized=false;
      if(found)
        {
         supported=(mode_before==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING ||
                    mode_before==ACCOUNT_MARGIN_MODE_RETAIL_NETTING) &&
                   SymbolInfoInteger(candidate.symbol,SYMBOL_TRADE_EXEMODE,execution_before) &&
                   execution_before!=SYMBOL_TRADE_EXECUTION_EXCHANGE;
         if(supported)
           {
            if(!SymbolInfoInteger(candidate.symbol,SYMBOL_SELECT,selected_symbol) ||
               selected_symbol==0) SymbolSelect(candidate.symbol,true);
            synchronized=SymbolIsSynchronized(candidate.symbol);
            have_quote=SymbolInfoTick(candidate.symbol,quote);
            supported=SymbolInfoDouble(candidate.symbol,SYMBOL_POINT,point) &&
                      SymbolInfoDouble(candidate.symbol,SYMBOL_TRADE_TICK_SIZE,tick_size) &&
                      SymbolInfoInteger(candidate.symbol,SYMBOL_DIGITS,digits);
           }
        }
      if(!JPWReadGenesisSnapshot(after) || !JPWReadAccount(later))
        { JPWGenesisUnavailable("posições ou conta não confirmadas"); return; }
      ResetLastError();
      const long mode_after=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
      if(GetLastError()!=0)
        { JPWGenesisUnavailable("modo de margem da conta não confirmado"); return; }
      if(!JPWAccountsEqual(account,later) ||
         !JPWGenesisSnapshotsEqual(before,after) ||
         mode_before!=mode_after ||
         connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
        {
         if(attempt==0 && JPWWithinBudget(started)) continue;
         JPWGenesisUnavailable("identidade ou posições alteradas durante a leitura");
         return;
        }
      if(!JPWWithinBudget(started))
        { JPWGenesisUnavailable("leitura fora do orçamento; atualizando"); return; }
      if(found && !supported)
        { JPWGenesisUnavailable("conta/instrumento de bolsa ou especificação indisponível"); return; }
      if(found)
        {
         long execution_after=0,checked_digits=0;
         double checked_point=0.0,checked_tick_size=0.0;
         if(!SymbolInfoInteger(candidate.symbol,SYMBOL_TRADE_EXEMODE,execution_after) ||
            !SymbolInfoInteger(candidate.symbol,SYMBOL_DIGITS,checked_digits) ||
            !SymbolInfoDouble(candidate.symbol,SYMBOL_POINT,checked_point) ||
            !SymbolInfoDouble(candidate.symbol,SYMBOL_TRADE_TICK_SIZE,checked_tick_size) ||
            execution_after!=execution_before || checked_digits!=digits ||
            checked_point!=point || checked_tick_size!=tick_size)
           { JPWGenesisUnavailable("especificação do símbolo mudou durante a leitura"); return; }
        }
      if(stored==JPW_GENESIS_ABSENT)
        {
         if(selected!=JPW_GENESIS_SELECT_OK)
           {
            if(selected==JPW_GENESIS_SELECT_NONE)
               JPWGenesisUnavailable("sem posição aberta confirmada; não há encerramento formal inferível");
            else if(selected==JPW_GENESIS_SELECT_NOT_FOUND)
               JPWGenesisUnavailable("ticket informado não está aberto");
            else if(selected==JPW_GENESIS_SELECT_AMBIGUOUS)
               JPWGenesisUnavailable("selecione o ticket da referência; grupos ou horários ambíguos");
            else JPWGenesisUnavailable("horário ou identidade da posição não confirmados");
            return;
           }
         // Never establish a first reference from an offline or unanchored
         // cache; that could silently choose a closed/old operation.
         if(!connected || !clock_valid)
           { JPWGenesisUnavailable("aguardando conexão e relógio confiável para escolher a referência"); return; }
         if((long)candidate.ticket<=0)
           { JPWGenesisUnavailable("ticket da referência fora do intervalo registrável"); return; }
         const JPW_GENESIS_STORE_STATE created=JPWGenesisCreate(account,InpGenesisTicket,
            JPW_GENESIS_FOLDER,(long)candidate.ticket,candidate.identifier,
            candidate.symbol,candidate.direction,candidate.opened_msc,saved);
         if(created!=JPW_GENESIS_VALID)
           { JPWGenesisUnavailable(JPWGenesisStoreReason(created)); return; }
         // Another instance may have installed a record in the meantime.
         if(saved.reference_state!=JPW_GENESIS_ACTIVE ||
            !JPWGenesisFindByIdentifier(after,saved.identifier,candidate))
           { JPWGenesisUnavailable("registro alterado por outra instância; aguardando novo ciclo"); return; }
        }
      if(saved.reference_state==JPW_GENESIS_CLOSED)
        { JPWGenesisUnavailable("referência encerrada; informe outro ticket para nova referência"); return; }
      if(saved.reference_state==JPW_GENESIS_REVERSED)
        { JPWGenesisUnavailable("direção invertida em netting; informe outro ticket"); return; }
      if(!found && stored==JPW_GENESIS_VALID)
        {
         // A lista local pode estar incompleta depois de reconexao mesmo
         // quando duas leituras coincidem. A falta do identificador nao e
         // testemunha suficiente para gravar CLOSED irreversivelmente.
         JPWGenesisUnavailable("referência não localizada; encerramento não comprovado");
         return;
        }
      // The saved identifier anchors a netting position across additions and
      // partial reductions. Some servers may refresh its opening timestamp;
      // that alone must not promote or retire the reference.
      if(candidate.symbol!=saved.symbol || candidate.direction!=saved.direction)
        {
         // A divergencia local bloqueia a medida, mas sem testemunha de
         // sincronizacao da posicao nao grava REVERSED irreversivelmente.
         JPWGenesisUnavailable("símbolo/direção da referência divergente; escolha outro ticket");
         return;
        }
      if(candidate.sl!=0.0 && (!have_quote || quote.time<=0))
        { JPWGenesisUnavailable("cotação da referência ausente"); return; }
      long tick_ms=0;
      bool current=false;
      string quality="Estimated";
      if(have_quote && quote.time>0)
        {
         tick_ms=(quote.time_msc>0 ? quote.time_msc : (long)quote.time*1000);
         if(tick_ms<=0 || (quote.time_msc>0 &&
            MathAbs((double)(quote.time_msc-(long)quote.time*1000))>1000.0))
           {
            if(candidate.sl!=0.0)
              { JPWGenesisUnavailable("horário da cotação inválido"); return; }
            tick_ms=0;
           }
         current=connected && clock_valid && synchronized &&
                 tick_ms>0 && now_ms>=tick_ms &&
                 now_ms-tick_ms<=(long)InpMaxQuoteAgeSeconds*1000;
         quality=(current ? "Current (quote)" : "Estimated");
        }
      double distance=0.0,points=0.0,percent=0.0,pips=0.0;
      bool has_pips=false;
      const JPW_GENESIS_DISTANCE result=JPWGenesisDistance(candidate.direction,
         quote.bid,quote.ask,candidate.sl,point,(int)digits,tick_size,
         candidate.symbol,InpPipSymbol,InpPipSize,
         distance,points,percent,pips,has_pips);
      const bool netting=(mode_before==ACCOUNT_MARGIN_MODE_RETAIL_NETTING);
      const string basis=(netting ? "Position SL" : "Genesis SL");
      const string provenance=(InpGenesisTicket==0 ? "Inferred" : "Selected");
      const string suffix=(netting ? " · Netting" : " · "+provenance)+
                          (current ? "" : " · Estimated");
      const string local_sl_note="; SL local sem confirmação independente de sincronização"+
                                 (!connected ? "; pode diferir após alteração em outro terminal" : "");
      const string direction=(candidate.direction==POSITION_TYPE_BUY ? "BUY" : "SELL");
      const string reference_detail=candidate.symbol+" "+direction+"; "+provenance+
         "; ticket de origem "+IntegerToString(saved.origin_ticket)+
         "; identificador "+IntegerToString(saved.identifier)+"; "+quality+local_sl_note;
      if(result==JPW_GENESIS_DISTANCE_NO_SL)
        { JPWGenesisState(basis+": No SL"+suffix,"SL: No SL"+suffix,reference_detail+"; posição sem SL local",
                          (current ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED),"No SL"); return; }
      if(result==JPW_GENESIS_DISTANCE_REACHED)
        { JPWGenesisState(basis+": SL reached"+suffix,"SL reached"+suffix,reference_detail+"; preço no nível do SL; execução não confirmada",
                          (current ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED),"SL reached"); return; }
      if(result==JPW_GENESIS_DISTANCE_PASSED)
        { JPWGenesisState(basis+": SL passed"+suffix,"SL passed"+suffix,reference_detail+"; preço além do SL; execução não confirmada",
                          (current ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED),"SL passed"); return; }
      if(result!=JPW_GENESIS_DISTANCE_POSITIVE)
        { JPWGenesisUnavailable("preço, SL ou unidade de distância inválidos"); return; }
      string units=JPWGenesisFormatPoints(points);
      if(has_pips) units+=" / "+DoubleToString(pips,2)+" pips";
      const string pct=JPWFormatPercent(percent,false);
      g_genesis_quality=(current ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED);
      g_genesis_value=pct;
      g_numeric_values[2]=percent; g_numeric_valid[2]=true; g_source_times[2]=tick_ms;
      g_genesis_reason=(current ? "Cotação recente" : "Cotação ou referência temporal não comprovada");
      g_genesis_line=basis+": "+(current ? "" : "≈")+pct+suffix;
      g_genesis_short=(netting ? "Pos SL: " : "SL: ")+(current ? "" : "≈")+pct+
                       (netting ? " · Netting" : " · "+provenance);
      string detail="";
      if(!current)
         detail=(!connected ? "Sem conexão; SL local pode diferir de outro terminal. " :
                 (!clock_valid ? "Referência temporal não comprovada. " :
                  (!synchronized ? "Símbolo em sincronização. " : "Cotação antiga. ")));
      bool closer=false;
      for(int i=0;i<ArraySize(after);i++)
        {
         if(after[i].identifier==candidate.identifier ||
            after[i].symbol!=candidate.symbol || after[i].direction!=candidate.direction ||
            after[i].sl<=0.0) continue;
         double other_distance=0.0,other_points=0.0,other_percent=0.0,other_pips=0.0;
         bool other_has_pips=false;
         const JPW_GENESIS_DISTANCE other=JPWGenesisDistance(after[i].direction,
            quote.bid,quote.ask,after[i].sl,point,(int)digits,tick_size,
            after[i].symbol,"",0.0,other_distance,other_points,other_percent,
            other_pips,other_has_pips);
         if(other==JPW_GENESIS_DISTANCE_POSITIVE && other_distance<distance)
            { closer=true; break; }
        }
      g_genesis_tooltip=basis+"; "+candidate.symbol+" "+direction+
         "; referência "+provenance+" (ticket de origem "+
         IntegerToString(saved.origin_ticket)+", identificador "+
         IntegerToString(saved.identifier)+").\n"+
         units+"; "+pct+" do preço "+
         (candidate.direction==POSITION_TYPE_BUY ? "Bid" : "Ask")+". "+
         quality+"; cotação: "+TimeToString((datetime)(tick_ms/1000),TIME_DATE|TIME_SECONDS)+
         " (servidor). Current qualifica a cotação, não prova a sincronização do SL local. "+detail+
         (closer ? "Outra posição do mesmo grupo tem SL válido mais próximo; a referência não muda. " : "")+
         "Distância informativa, não é risco agregado nem confirmação de execução do stop.";
      return;
     }
  }

string JPWRaizNStoreReason(const JPW_RAIZN_STATE state)
  {
   if(state==JPW_RAIZN_ABSENT) return("cenário não declarado");
   if(state==JPW_RAIZN_BUSY) return("registro ocupado por outra instância");
   if(state==JPW_RAIZN_INVALID) return("registro corrompido; edição bloqueada");
   if(state==JPW_RAIZN_INCOMPATIBLE) return("versão do registro incompatível");
   if(state==JPW_RAIZN_ACCOUNT_UNAVAILABLE) return("conta indisponível");
   if(state==JPW_RAIZN_CONFLICT) return("cenário alterado por outra instância");
   return("falha ao ler o registro local");
  }

void JPWCollectRaizScenario()
  {
   g_raiz_comparison="Sem vínculo explícito: comparação ao SL indisponível.";
   g_saved_raiz_line="Raiz N: N/D — conta ou cenário indisponível";
   g_saved_raiz_tooltip="A Raiz N exige um cenário declarado; não é um stop automático.";
   JPWRaizNClearScenario(g_raiz_scenario);
   JPWRaizNClearBinding(g_raiz_binding);
   JPWAccount before,after;
   if(!JPWReadAccount(before))
     {
      g_raiz_store_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE;
      if(g_raiz_details_open)
        {
         g_raiz_details_open=false; g_raiz_draft_account_known=false;
         JPWRaizPanelDestroy();
        }
      return;
     }
   if(g_raiz_details_open &&
      (g_raiz_draft_symbol!=_Symbol ||
       (g_raiz_draft_account_known &&
        !JPWAccountsEqual(before,g_raiz_draft_account))))
     {
      g_raiz_details_open=false;
      g_raiz_draft_account_known=false;
      g_raiz_feedback="Conta mudou; rascunho descartado para proteger o cenário.";
      JPWRaizPanelDestroy();
     }
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(installation=="")
     { g_raiz_store_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE; return; }
   g_raiz_store_state=JPWRaizNReadActive(before,_Symbol,installation,
      JPW_RAIZN_FOLDER,g_raiz_scenario,g_raiz_binding);
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after))
     {
      g_raiz_store_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE;
      JPWRaizNClearScenario(g_raiz_scenario);
      JPWRaizNClearBinding(g_raiz_binding);
     }
   if(g_raiz_details_open && g_raiz_store_state==JPW_RAIZN_VALID &&
      g_raiz_draft_expected_id!=g_raiz_scenario.scenario_id)
     {
      g_raiz_details_open=false;
      g_raiz_draft_account_known=false;
      g_raiz_draft_expected_id="";
      g_raiz_feedback="Cenário alterado por outra instância; reabra Detalhes.";
      JPWRaizPanelDestroy();
     }
   if(g_raiz_store_state!=JPW_RAIZN_VALID)
     {
      const string reason=JPWRaizNStoreReason(g_raiz_store_state);
      g_saved_raiz_line="Raiz N: N/D — "+reason;
      g_saved_raiz_tooltip="Raiz N indisponível: "+reason+
         ". Abra Detalhes para instruções. As outras métricas continuam independentes.";
      return;
     }
   if(g_raiz_binding.state!=JPW_RAIZN_ABSENT &&
      g_raiz_binding.state!=JPW_RAIZN_VALID)
      g_raiz_comparison="Vínculo opcional indisponível: "+
         JPWRaizNStoreReason(g_raiz_binding.state)+
         ". A Raiz N confirmada permanece válida.";
   double d_price=0.0,d_pct=0.0;
   if(JPWRaizNCalculate(g_raiz_scenario.p0,g_raiz_scenario.atr,
       g_raiz_scenario.n_h4,g_raiz_scenario.factor,d_price,d_pct)!=JPW_RAIZN_OK)
     {
      g_saved_raiz_line="Raiz N: N/D — cálculo inválido";
      g_saved_raiz_tooltip="Registro legível, mas P0, ATR, N ou F não produz distância válida.";
      return;
     }
   long digits=6;
   if(!SymbolInfoInteger(_Symbol,SYMBOL_DIGITS,digits) || digits<0 || digits>12) digits=6;
   const string percent=JPWRaizPercentText(d_pct);
   const string distance=JPWRaizPriceText(d_price,(int)digits);
   g_saved_raiz_line="Raiz N: "+percent+" de P0 | "+distance;
   g_saved_raiz_tooltip="Cenário declarado de "+g_raiz_scenario.symbol+
      "; modelo "+g_raiz_scenario.model_version+
      "; P0="+DoubleToString(g_raiz_scenario.p0,(int)digits)+
      " ("+g_raiz_scenario.p0_origin+"); ATR(55) H4="+
      DoubleToString(g_raiz_scenario.atr,(int)digits)+" ("+
      g_raiz_scenario.atr_source+"; "+g_raiz_scenario.atr_variant+"); N="+
      IntegerToString(g_raiz_scenario.n_h4)+" candles H4; F="+
      DoubleToString(g_raiz_scenario.factor,4)+".\n"+
      "D% = 100 × ATR / P0 × √N × F = "+percent+
      "; Dpreço = ATR × √N × F = "+distance+
      ". Barra ATR: "+TimeToString(g_raiz_scenario.atr_bar_server_time,TIME_DATE|TIME_SECONDS)+
      " (servidor); decisão declarada: "+
      TimeToString(g_raiz_scenario.decision_server_time,TIME_DATE|TIME_SECONDS)+
      " (servidor); confirmado: "+
      TimeToString(g_raiz_scenario.confirmed_at_utc,TIME_DATE|TIME_SECONDS)+
      " UTC (computador). "+
      (g_raiz_scenario.retrospective ? "Declaração retrospectiva. " :
       "Sem posição aberta verificada no instante da declaração; isso não prova decisão independente prévia. ")+
      "Distância diagnóstica, não é ordem, stop, dimensão de posição ou autorização de entrada.";
   if(g_raiz_binding.state!=JPW_RAIZN_ABSENT &&
      g_raiz_binding.state!=JPW_RAIZN_VALID)
      g_saved_raiz_tooltip+=" Vínculo opcional indisponível: "+
         JPWRaizNStoreReason(g_raiz_binding.state)+".";
   if(g_raiz_binding.identifier>0 && g_raiz_details_open)
     {
      JPWGenesisPosition first[],second[],bound;
      JPWGenesisClear(bound);
      JPWAccount after_positions;
      if(!(bool)TerminalInfoInteger(TERMINAL_CONNECTED) ||
         !JPWReadGenesisSnapshot(first) ||
         !JPWReadGenesisSnapshot(second) ||
         !JPWGenesisSnapshotsEqual(first,second) ||
         !JPWReadAccount(after_positions) ||
         !JPWAccountsEqual(before,after_positions))
         g_raiz_comparison="Posições não confirmadas; SL não comparado.";
      else if(!JPWGenesisFindByIdentifier(second,g_raiz_binding.identifier,bound))
         g_raiz_comparison="Referência não localizada; vínculo não é promovido.";
      else if(bound.symbol!=g_raiz_scenario.symbol ||
              bound.direction!=g_raiz_binding.direction)
         g_raiz_comparison="Símbolo/direção divergente; comparação bloqueada.";
      else
        {
         const JPW_RAIZN_SIDE side=(bound.direction==POSITION_TYPE_BUY ?
               JPW_RAIZN_SIDE_BUY : JPW_RAIZN_SIDE_SELL);
         double sl_price=0.0,sl_pct=0.0,gap_price=0.0,gap_pct=0.0;
         const JPW_RAIZN_SL_RESULT comparison=JPWRaizNCompareSL(side,
             g_raiz_scenario.p0,bound.sl,d_price,sl_price,sl_pct,gap_price,gap_pct);
         if(comparison==JPW_RAIZN_SL_NO_SL)
            g_raiz_comparison="Vínculo confirmado; posição sem SL local.";
         else if(comparison==JPW_RAIZN_SL_AT_P0)
            g_raiz_comparison="SL local em P0; sem distância adversa.";
         else if(comparison==JPW_RAIZN_SL_PROTECTED)
            g_raiz_comparison="SL local protege lucro; sem distância adversa.";
         else if(comparison==JPW_RAIZN_SL_OK)
            g_raiz_comparison="P0→SL "+DoubleToString(sl_pct,2)+"%; diferença Raiz N "+
                               DoubleToString(gap_pct,2)+" p.p.";
         else g_raiz_comparison="SL local inválido; comparação indisponível.";
        }
     }
  }

void JPWClearRaizLiveSample(const string reason)
  {
   g_live_sample.p0=0.0;
   g_live_sample.atr=0.0;
   g_live_sample.distance=0.0;
   g_live_sample.percent=0.0;
   g_live_sample.bar_time=0;
   g_live_sample.current_bar_time=0;
   g_live_sample.quote_time_msc=0;
   g_live_sample.current=false;
   g_live_sample.reason=reason;
  }

void JPWCollectRaizN()
  {
   JPWClearRaizLiveSample("Aguardando dados completos nesta apuração");
   g_raiz_quality=JPW_VIEW_NA; g_scale2_quality=JPW_VIEW_NA;
   g_raiz_value="N/A"; g_scale2_value="N/A";
   g_raiz_reason="Dados de preço, ATR ou calendário não confirmados";
   g_scale2_reason=g_raiz_reason;
   g_raiz_line="Raiz N diag. 1W: N/A"; g_raiz_short="RN1W: N/A";
   g_scale2_line="Raiz N diag. 2W: N/A"; g_scale2_short="RN2W: N/A";
   g_raiz_tooltip="Raiz N diagnóstica: aguardando dados completos.";
   g_scale2_tooltip=g_raiz_tooltip;
   JPWHorizonClear(g_horizon_result);
   const ulong started=g_cycle_started_ms;
   JPWAccount before,after;
   string base="",key="",factor_key=""; double scale=0.0;
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(!JPWReadAccount(before) || !JPWAccountUnits(before.currency,base,scale) ||
      !JPWRaizNConfigKey(before.server,before.login,before.currency,scale,installation,_Symbol,key) ||
      !JPWRaizNFactorKey(before.server,before.login,before.currency,scale,installation,_Symbol,factor_key))
     { g_live_config_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE;
       g_factor_state=JPW_RAIZN_ACCOUNT_UNAVAILABLE;
       g_factor_key=""; JPWRaizNFactorClear(g_factor_preference);
       g_raiz_tooltip="Conta/instalação indisponível."; g_scale2_tooltip=g_raiz_tooltip;
       g_raiz_reason="Conta ou instalação indisponível"; g_scale2_reason=g_raiz_reason;
       if(g_raiz_details_open) { g_raiz_details_open=false; g_raiz_draft_account_known=false; JPWRaizPanelDestroy(); }
       return; }
   if(g_raiz_details_open && (!g_raiz_draft_account_known ||
      !JPWAccountsEqual(before,g_raiz_draft_account) || g_raiz_draft_symbol!=_Symbol))
     {
      g_raiz_details_open=false; g_raiz_draft_account_known=false;
      g_raiz_feedback="Conta/instrumento mudou; rascunho descartado sem gravar.";
      JPWRaizPanelDestroy();
     }
   g_live_key=key;
   g_factor_key=factor_key;
   // Legacy per-symbol N/F remains readable in Details, never supplies either
   // standardized horizon and is not treated as an approved F policy.
   if(!JPWCoordinatorBudgetRemaining()) return;
   g_live_config_state=JPWRaizNConfigLoad(JPW_RAIZN_FOLDER,key,_Symbol,g_live_config,g_live_reason);
   if(!JPWCoordinatorBudgetRemaining()) return;
   g_factor_state=JPWRaizNFactorLoad(JPW_RAIZN_FOLDER,factor_key,_Symbol,
                                      g_factor_preference,g_factor_reason);
   // Scenario reads are handled by the separate on-demand queue.
   if(!JPWCoordinatorBudgetRemaining()) return;
   // Missing preference is an explicit default, never a repair or fallback
   // from a corrupt, incompatible or temporarily unreadable record.
   if(g_factor_state!=JPW_RAIZN_VALID && g_factor_state!=JPW_RAIZN_ABSENT)
     { g_raiz_tooltip="F indisponível: "+g_factor_reason+
                       " O registro local foi preservado; sem fallback silencioso.";
       g_raiz_reason="F indisponível: "+g_factor_reason; g_scale2_reason=g_raiz_reason;
       g_scale2_tooltip=g_raiz_tooltip; return; }
   const double factor=(g_factor_state==JPW_RAIZN_VALID ?
                        g_factor_preference.factor : JPW_RAIZN_FACTOR_DEFAULT);
   if(!JPWRaizNFactorAllowed(factor))
     { g_raiz_tooltip="F inválido; Raiz N diagnóstica indisponível.";
       g_raiz_reason="F inválido"; g_scale2_reason=g_raiz_reason;
       g_scale2_tooltip=g_raiz_tooltip; return; }
   JPWRaizNLiveNativeProvider provider;
   provider.Configure(_Symbol,g_raiz_atr_handle,g_live_connected,g_live_clock_valid,
                      g_live_now_ms,(long)InpMaxQuoteAgeSeconds*1000);
   if(!JPWRaizNReadLiveBase(provider,g_live_cache,key,g_live_sample))
     { g_raiz_tooltip="Raiz N diagnóstica indisponível: "+g_live_sample.reason;
       g_raiz_reason=g_live_sample.reason; g_scale2_reason=g_raiz_reason;
       g_scale2_tooltip=g_raiz_tooltip; return; }
   // A server clock advanced by another instrument does not prove that this
   // target symbol has received a new tick since attach/reconnection.
   if(g_live_connected!=g_horizon_was_connected)
     {
      g_horizon_was_connected=g_live_connected;
      g_horizon_tick_baseline_msc=g_live_sample.quote_time_msc;
      g_horizon_new_tick=false;
     }
   if(g_horizon_tick_baseline_msc<=0 ||
      g_live_sample.quote_time_msc<g_horizon_tick_baseline_msc)
     { g_horizon_tick_baseline_msc=g_live_sample.quote_time_msc; g_horizon_new_tick=false; }
   if(g_live_sample.quote_time_msc>g_horizon_tick_baseline_msc)
      g_horizon_new_tick=true;
   const bool anchored_now=(g_live_clock_valid && g_live_now_ms>0);
   const datetime reference=(datetime)((anchored_now ?
                                  g_live_now_ms : g_live_sample.quote_time_msc)/1000);
   if(!JPWCoordinatorBudgetRemaining()) return;
   if(!JPWHorizonResolve(_Symbol,reference,g_horizon_result))
     { g_raiz_tooltip="Horizonte 1W indisponível: "+g_horizon_result.reason_1w;
       g_scale2_tooltip="Horizonte 2W indisponível: "+g_horizon_result.reason_2w;
       g_raiz_reason=g_horizon_result.reason_1w;
       g_scale2_reason=g_horizon_result.reason_2w;
       if(!anchored_now)
         { const string caveat=" Referência baseada no último tick do símbolo, não no presente.";
           g_raiz_tooltip+=caveat; g_scale2_tooltip+=caveat; }
       return; }
   double price1=0.0,pct1=0.0,price2=0.0,pct2=0.0;
   if(JPWRaizNCalculate(g_live_sample.p0,g_live_sample.atr,g_horizon_result.n_1w,
                        factor,price1,pct1)!=JPW_RAIZN_OK ||
      JPWRaizNCalculate(g_live_sample.p0,g_live_sample.atr,g_horizon_result.n_2w,
                        factor,price2,pct2)!=JPW_RAIZN_OK)
     { g_raiz_tooltip="Raiz N diagnóstica indisponível: cálculo inválido.";
       g_raiz_reason="Cálculo inválido"; g_scale2_reason=g_raiz_reason;
       g_scale2_tooltip=g_raiz_tooltip; return; }
   const bool quote_current=(g_live_sample.current && g_horizon_new_tick);
   const bool current1=(quote_current && g_horizon_result.status_1w==JPW_HORIZON_EXACT);
   const bool current2=(quote_current && g_horizon_result.status_2w==JPW_HORIZON_EXACT);
   const string mark1=(current1 ? "" : "≈"),mark2=(current2 ? "" : "≈");
   const string quality1=(current1 ? "Current" : "Estimated");
   const string quality2=(current2 ? "Current" : "Estimated");
   const string factor_label=(factor==1.8 ? "F1,8" : "F1,5");
   g_raiz_quality=(current1 ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED);
   g_scale2_quality=(current2 ? JPW_VIEW_CURRENT : JPW_VIEW_ESTIMATED);
   g_numeric_values[3]=pct1; g_numeric_values[4]=pct2;
   g_numeric_valid[3]=true; g_numeric_valid[4]=true;
   g_source_times[3]=g_live_sample.quote_time_msc; g_source_times[4]=g_live_sample.quote_time_msc;
   g_raiz_value=mark1+JPWRaizPercentText(pct1)+" · "+factor_label;
   g_scale2_value=mark2+JPWRaizPercentText(pct2)+" · "+factor_label;
   g_raiz_reason=(current1 ? "Cotação e calendário confirmados" :
       (g_horizon_result.status_1w!=JPW_HORIZON_EXACT ? g_horizon_result.reason_1w :
        "Novo tick ou frescor da cotação não comprovado"));
   g_scale2_reason=(current2 ? "Cotação e calendário confirmados" :
       (g_horizon_result.status_2w!=JPW_HORIZON_EXACT ? g_horizon_result.reason_2w :
        "Novo tick ou frescor da cotação não comprovado"));
   g_raiz_line="Raiz N diag. 1W: "+mark1+JPWRaizPercentText(pct1)+
               " · "+factor_label+" · "+quality1;
   g_raiz_short="RN1W: "+mark1+JPWRaizPercentText(pct1)+" "+factor_label;
   g_scale2_line="Raiz N diag. 2W: "+mark2+JPWRaizPercentText(pct2)+
                 " · "+factor_label+" · "+quality2;
   g_scale2_short="RN2W: "+mark2+JPWRaizPercentText(pct2)+" "+factor_label;
   const string shared="Símbolo exato: "+_Symbol+
      "; P0 = ponto médio Bid/Ask do mesmo tick: "+DoubleToString(g_live_sample.p0,-16)+
      "; ATR nativo MT5/iATR(55,H4) da última barra encerrada: "+
      DoubleToString(g_live_sample.atr,-16)+" ("+
      TimeToString(g_live_sample.bar_time,TIME_DATE|TIME_SECONDS)+" servidor)."+
      "\nCotação: "+TimeToString((datetime)(g_live_sample.quote_time_msc/1000),
                                 TIME_DATE|TIME_SECONDS)+" servidor; "+
      (quote_current ? "novo tick do símbolo confirmado" :
                       "novo tick do símbolo não confirmado; "+g_live_sample.reason)+
      ".\nReferência dos horizontes: "+TimeToString(reference,TIME_DATE|TIME_SECONDS)+
      (anchored_now ? " servidor (agora ancorado)" :
                      " servidor (último tick do símbolo; NÃO é janela a partir do presente)")+
      ". Fonte de calendário: "+g_horizon_result.source+
      (g_horizon_result.source_sha256=="" ?
        "; sem calendário datado aprovado" :
        "; SHA-256 aprovado "+g_horizon_result.source_sha256)+
      ". "+factor_label+(g_factor_state==JPW_RAIZN_ABSENT ?
           " é o padrão diagnóstico ainda não gravado" : " foi escolhido e gravado nesta instalação")+
      "; P-21 permanece PENDING. Current qualifica dados, não homologa F nem o modelo. Esta distância não define stop, lote ou entrada.";
   g_raiz_tooltip="1W: "+quality1+"; N="+IntegerToString(g_horizon_result.n_1w)+
      " fechamentos H4; fim="+TimeToString(g_horizon_result.end_1w,TIME_DATE|TIME_SECONDS)+
      " servidor; ATR×√N×F="+DoubleToString(price1,-16)+
      "; 100×ATR×√N×F/P0="+JPWRaizPercentText(pct1)+". "+
      g_horizon_result.reason_1w+". "+shared;
   g_scale2_tooltip="2W: "+quality2+"; N="+IntegerToString(g_horizon_result.n_2w)+
      " fechamentos H4; fim="+TimeToString(g_horizon_result.end_2w,TIME_DATE|TIME_SECONDS)+
      " servidor; ATR×√N×F="+DoubleToString(price2,-16)+
      "; 100×ATR×√N×F/P0="+JPWRaizPercentText(pct2)+". "+
      g_horizon_result.reason_2w+". "+shared;
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after) ||
      g_live_connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED) ||
      !JPWWithinBudget(started))
     {
      JPWClearRaizLiveSample("Identidade, conexão ou orçamento alterado; amostra descartada");
      JPWHorizonClear(g_horizon_result);
      g_raiz_quality=JPW_VIEW_NA; g_scale2_quality=JPW_VIEW_NA;
      g_raiz_value="N/A"; g_scale2_value="N/A";
      g_raiz_reason="Identidade, conexão ou orçamento alterado";
      g_scale2_reason=g_raiz_reason;
      g_raiz_line="Raiz N diag. 1W: N/A"; g_raiz_short="RN1W: N/A";
      g_scale2_line="Raiz N diag. 2W: N/A"; g_scale2_short="RN2W: N/A";
      g_raiz_tooltip="Identidade/conexão mudou ou leitura excedeu o orçamento; aguardando nova amostra.";
      g_scale2_tooltip=g_raiz_tooltip;
     }
  }

void JPWDetailsReadMDD()
  {
   JPWAccount before,after;
   JPWMDDRecord record; JPWMDDClear(record);
   JPW_MDD_STATE state=JPW_MDD_ACCOUNT_UNAVAILABLE;
   if(JPWReadAccount(before)) state=JPWMDDReadOnly(before,JPW_MDD_FOLDER,record);
   // ReadOnly releases its exclusive lock before this function draws anything.
   if(!JPWReadAccount(after)) state=JPW_MDD_ACCOUNT_UNAVAILABLE;
   else if(state!=JPW_MDD_ACCOUNT_UNAVAILABLE)
      state=JPWMDDConfirmAccount(before,after,state,record);
   g_mdd_summary="MDD observado: N/D"; g_mdd_context="";
   if(state==JPW_MDD_VALID)
     {
      g_mdd_summary="Máximo observado DD/saldo: "+JPWFormatPercent(record.max_percent,false);
      g_mdd_context="Início: "+TimeToString(record.observation_started_at,TIME_DATE|TIME_SECONDS)+
         "; recorde: "+TimeToString(record.observed_at_utc,TIME_DATE|TIME_SECONDS)+
         " UTC (relógio do computador). Saldo "+DoubleToString(record.balance_at_max,2)+
         "; equity "+DoubleToString(record.equity_at_max,2)+" "+record.currency+
         ". Registro local, não é série completa nem MDD pico-a-vale.";
     }
   else if(state==JPW_MDD_ABSENT) g_mdd_context="Registro ainda inexistente nesta instalação/conta.";
   else if(state==JPW_MDD_BUSY) g_mdd_context="Registro ocupado; consulte novamente, sem escrita.";
   else if(state==JPW_MDD_INVALID) g_mdd_context="Registro corrompido; leitura recusada.";
   else if(state==JPW_MDD_INCOMPATIBLE) g_mdd_context="Versão do registro incompatível; leitura recusada.";
   else if(state==JPW_MDD_ACCOUNT_UNAVAILABLE) g_mdd_context="Conta indisponível ou alterada durante a consulta.";
   else g_mdd_context="Falha de leitura; nenhum valor presumido.";
  }

void JPWDetailsReadObserver()
  {
   g_observer_summary="Observador local: N/A";
   g_observer_context="Sem vínculo automático com a Gênese ou com posição ainda aberta.";
   JPWAccount before,after;
   if(!JPWReadAccount(before))
     { g_observer_context="Conta indisponível."; return; }
   string key="",reason="";
   if(!JPWObserverAccountKey(before.server,before.login,before.currency,
                             TerminalInfoString(TERMINAL_DATA_PATH),key))
     { g_observer_context="Identidade local indisponível."; return; }
   JPWObserverSnapshot snapshot;
   const bool found=JPWObserverReadCurrent(key,_Symbol,snapshot,reason);
   if(!JPWReadAccount(after) || !JPWAccountsEqual(before,after))
     { g_observer_context="Conta mudou durante a consulta; amostra descartada."; return; }
   if(!found)
     { g_observer_context=reason+". O EA observador é opcional e não cria histórico retroativo certificado.";
       return; }
   const string provenance=(snapshot.provenance==JPW_OBSERVER_CAPTURED_EVENT ?
                            "Capturado no evento" :
                            (snapshot.provenance==JPW_OBSERVER_RECONSTRUCTED ?
                             "Reconstructed" : "Proveniência indisponível"));
   g_observer_summary="Último snapshot local de execução: "+provenance;
   const string observed_n1=(snapshot.status_1w==JPW_HORIZON_UNAVAILABLE ?
                             "N/A" : IntegerToString(snapshot.n_1w));
   const string observed_n2=(snapshot.status_2w==JPW_HORIZON_UNAVAILABLE ?
                             "N/A" : IntegerToString(snapshot.n_2w));
   g_observer_context="P0 executado="+DoubleToString(snapshot.executed_p0,-16)+
      "; primeiro negócio="+IntegerToString(snapshot.first_deal_ticket)+
      "; posição ID="+IntegerToString(snapshot.position_id)+
      "; negócio="+TimeToString((datetime)(snapshot.deal_time_msc/1000),
                                  TIME_DATE|TIME_SECONDS)+" servidor"+
      "; ATR55 H4="+DoubleToString(snapshot.atr55_h4,-16)+
      "; N1W="+observed_n1+
      "; N2W="+observed_n2+
      "; origem="+snapshot.horizon_source+
      "; grade observada em "+TimeToString((datetime)snapshot.horizon_observed_utc,
                                             TIME_DATE|TIME_SECONDS)+
      " UTC. Último episódio registrado para conta/símbolo; a grade foi resolvida após o callback e não comprova posição aberta, plano humano ou vínculo com Gênese.";
  }

void JPWRefresh()
  {
   JPWPositionsInvalidate("Aguardando catálogo coerente deste ciclo");
   g_positions_catalog_attempted=false;
   for(int i=0;i<5;i++) { g_numeric_valid[i]=false; g_source_times[i]=0; }
   g_last_full_refresh_ms=GetTickCount64();
   g_last_full_refresh_utc=TimeGMT();
   g_leverage_quality=JPW_VIEW_NA;
   g_raiz_due=true;
   g_live_connected=false; g_live_clock_valid=false; g_live_now_ms=0;
   g_genesis_due=false;
   const bool connected=(bool)TerminalInfoInteger(TERMINAL_CONNECTED);
   if(g_connected!=connected)
     {
      JPWClockReset(g_clock,(long)TimeCurrent(),GetTickCount64());
      // Account metadata can be unavailable while offline. Discard prior
      // tick evidence before that early return as well as before reconnect.
      JPWHorizonResetTickEvidence();
     }
   g_connected=connected;
   JPWAccount current;
   if(!JPWReadAccount(current))
     { JPWMetricUnavailable("identidade da conta ausente"); JPWGenesisUnavailable("identidade da conta ausente"); JPWAcceptCollection("N/D","Indisponível — identidade da conta ausente"); return; }
   if(!g_account_known || !JPWAccountsEqual(g_account,current))
     {
      if(g_account_known) JPWInvalidateIdentityPresentation();
      JPWClearRaizLiveSample("Conta alterada; aguardando nova apuração");
      // JPWRender receives the new account below, so its identity guard
      // cannot discover this transition. Discard both live and menu copies.
      JPWStopRiskUnavailable("Conta alterada; aguardando nova amostra do EA");
      g_stop_last_ready=false;
      ArrayResize(g_stop_last_rows,0);
      ArrayResize(g_stop_table_rows,0);
      g_stop_button_count=0;
      g_stop_selected_row=-1;
      g_account=current; g_account_known=true; JPWResetData();
      JPWHorizonResetTickEvidence();
     }
   string opaque="";
   if(JPWObserverAccountKey(current.server,current.login,current.currency,
                           TerminalInfoString(TERMINAL_DATA_PATH),opaque))
      { g_diagnostic_context=opaque; JPWProfileHash(opaque+"|"+_Symbol,g_sample_context); }
   else { g_sample_context=""; g_diagnostic_context=""; }
   long now_ms=0;
   const bool clock_valid=(connected && JPWClockObserve(g_clock,(long)TimeCurrent(),(long)TimeTradeServer(),
                                                       GetTickCount64(),InpMaxQuoteAgeSeconds,now_ms));
   g_live_connected=connected; g_live_clock_valid=clock_valid; g_live_now_ms=now_ms;
   if(!JPWCollectAccountMetrics(current,connected,clock_valid))
     { JPWGenesisUnavailable("aguardando leitura consistente da conta"); JPWAcceptCollection("Atualizando","Confirmando identidade, saldo e contexto da conta"); return; }
   g_genesis_refresh_account=current;
   g_genesis_refresh_connected=connected;
   g_genesis_refresh_clock_valid=clock_valid;
   g_genesis_refresh_now_ms=now_ms;
   g_genesis_refresh_started=g_cycle_started_ms;
   g_genesis_due=true;
   string currency="";
   double divisor=0.0;
   if(!JPWAccountUnits(current.currency,currency,divisor)) { JPWAcceptCollection("N/D","Indisponível — moeda da conta não suportada"); return; }
   if(!JPWCoordinatorBudgetRemaining()) { JPWAcceptCollection("Atualizando","Coleta adiada pelo orçamento do ciclo"); return; }
   if(PositionsTotal()>0 && !JPWPrepareCatalog()) { JPWAcceptCollection("Atualizando","Preparando instrumentos e conversões"); return; }
   const ulong started=g_genesis_refresh_started;
   for(int attempt=0;attempt<2;attempt++)
     {
      if(!JPWWithinBudget(started)) { JPWAcceptCollection("Atualizando","Confirmando a composição da conta"); return; }
      JPWPosition before[],after[];
      JPWPositionView metadata_before[],metadata_after[];
      JPWAccount later;
      string metadata_reason="";
      ResetLastError(); const long margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
      const bool margin_known=(GetLastError()==0);
      if(!JPWReadSnapshot(before)) { JPWAcceptCollection("N/D","Indisponível — posições não confirmadas"); return; }
      // No-position cache while disconnected is not proof that an account is empty.
      if(ArraySize(before)==0 && !connected) { JPWAcceptCollection("N/D","Indisponível — confirme as posições com conexão"); return; }
      double gross=0.0;
      bool estimated=!clock_valid;
      long oldest=0;
      JPW_RESULT status=JPW_OK;
      if(ArraySize(before)>0)
         status=JPWCollectReading(before,current,currency,divisor==100.0,now_ms,started,clock_valid,connected,gross,estimated,oldest);
      const double equity=AccountInfoDouble(ACCOUNT_EQUITY)/divisor;
      if(!JPWReadSnapshot(after) || !JPWReadAccount(later)) { JPWAcceptCollection("N/D","Indisponível — posições não confirmadas"); return; }
      if(!JPWAccountsEqual(current,later) || !JPWPositionsEqual(before,after) ||
         connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
        {
         if(attempt==0 && JPWWithinBudget(started)) continue;
         JPWAcceptCollection("Atualizando","Identidade ou composição alterada durante a leitura"); return;
        }
      if(!JPWWithinBudget(started)) { JPWAcceptCollection("Atualizando","Confirmando a composição da conta"); return; }
      // Optional inventory reads follow the original financial validation, so
      // absent SL/TP or a metadata deadline never invalidates account leverage.
      g_positions_catalog_attempted=true;
      const bool metadata_known=JPWPositionsReadMetadata(metadata_before,started,metadata_reason) &&
                                JPWPositionsMatchSnapshot(metadata_before,before);
      const bool metadata_after_known=metadata_known &&
         JPWPositionsReadMetadata(metadata_after,started,metadata_reason) &&
         JPWPositionsMatchSnapshot(metadata_after,after);
      ResetLastError(); const long after_margin_mode=AccountInfoInteger(ACCOUNT_MARGIN_MODE);
      const bool metadata_stable=metadata_after_known &&
         JPWPositionsMetadataEqual(metadata_before,metadata_after) && margin_known &&
         GetLastError()==0 && margin_mode==after_margin_mode;
      if(metadata_stable)
         JPWPositionsStageCatalog(metadata_after,before,g_sample_context,margin_mode,g_diagnostic_context);
      if(status!=JPW_OK) { JPWAcceptCollection("N/D","Indisponível — "+JPWErrorText(status)); return; }
      double leverage=0.0;
      status=JPWLeverage(gross,equity,leverage);
      if(status!=JPW_OK) { JPWAcceptCollection("N/D","Indisponível — "+JPWErrorText(status)); return; }
      if(!JPWPositionsStageLeverage(equity,leverage,g_position_candidate_gross))
         g_position_math_reason="Contribuições indisponíveis ou não reconciliadas";
      if(ArraySize(before)==0)
        {
         // A fresh connection with an empty cache is not yet a current reading.
         if(!clock_valid) { JPWAcceptCollection("Aguardando dados","Confirmando atualização da conta"); return; }
         g_numeric_values[0]=0.0; g_numeric_valid[0]=true;
         g_leverage_quality=JPW_VIEW_CURRENT;
         JPWAcceptCollection("0,00x","Atual — nenhuma posição aberta confirmada"); return;
        }
      string state="Atual";
      if(estimated)
         state=(!connected ? "Estimativa — sem conexão" : (!clock_valid ? "Estimativa — atualização não comprovada" : (g_used_unsynchronized ? "Estimativa — dados em sincronização" : "Estimativa — cotações sem atualização recente")));
      state+=" | Cotação mais antiga: "+TimeToString((datetime)(oldest/1000),TIME_DATE|TIME_SECONDS)+" (servidor)";
      state+=" | Base: último equity informado pelo terminal";
      g_numeric_values[0]=leverage; g_numeric_valid[0]=true; g_source_times[0]=oldest;
      g_leverage_quality=(estimated ? JPW_VIEW_ESTIMATED : JPW_VIEW_CURRENT);
      JPWAcceptCollection(JPWFormatLeverage(leverage),state);
      return;
     }
  }

bool JPWFullRefreshDue(const ulong now_ms,const ulong last_ms,
                       const int requested_seconds)
  {
   if(requested_seconds<1 || last_ms==0 || now_ms<last_ms) return(true);
   // A slow saved input remains compatible with templates, but a financial
   // reading is never left unevaluated for an hour solely due to that input.
   const int effective_seconds=(requested_seconds<30 ? requested_seconds : 30);
   return(now_ms-last_ms>=(ulong)effective_seconds*1000);
  }

bool JPWFullRefreshRequired(const bool account_changed,
                            const bool connection_changed,
                            const ulong now_ms,const ulong last_ms,
                            const int requested_seconds)
  {
   return(account_changed || connection_changed ||
          JPWFullRefreshDue(now_ms,last_ms,requested_seconds));
  }
#endif

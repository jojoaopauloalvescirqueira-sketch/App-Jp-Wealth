#property copyright "JP Wealth"
#include <JPWealth/JPW_Alavancagem_Version.mqh>
#property version JPW_PRODUCT_MQL_VERSION
#property description "JPW GENETRIX · Cockpit: alavancagem, flutuante global/compensado, Genesis SL, Raiz N e risco dos stops."
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots 0

#include <JPWealth/JPW_Alavancagem_Diagnostics.mqh>
#include <JPWealth/JPW_Alavancagem_Terminal.mqh>
#include <JPWealth/JPW_Alavancagem_Profile.mqh>
#include <JPWealth/JPW_Alavancagem_MDD.mqh>
#include <JPWealth/JPW_Alavancagem_Genesis_Store.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Config.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Factor.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Live.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>
#include <JPWealth/JPW_Alavancagem_StopRisk_Store.mqh>
#include <JPWealth/JPW_Alavancagem_Panel.mqh>
#include <JPWealth/JPW_Alavancagem_Cockpit.mqh> // See package AGENTS.md for invariants and review.
#include <JPWealth/JPW_Alavancagem_Positions.mqh> // Accepted same-reading account contribution, no persistence.

input int InpUpdateSeconds=1; // Cadência solicitada; frescor limita o ciclo completo a no máximo 30 s.
input int InpMaxQuoteAgeSeconds=30;
input ENUM_BASE_CORNER InpCorner=CORNER_LEFT_UPPER;
input int InpOffsetX=16;
input int InpOffsetY=40;
input int InpFontSize=8;
input int InpCockpitFontSize=11; // Independente da fonte compacta do gráfico.
input color InpFontColor=C'118,118,118'; // #767676; templates retain their saved inputs.
input long InpGenesisTicket=0; // 0: inferir somente uma referencia inequivoca; >0: ticket aberto.
input string InpPipSymbol=""; // Opcional: convencao de pip para este simbolo EXATO.
input double InpPipSize=0.0;
input bool InpTechnicalLog=false;

string g_panel_prefix="";
long g_collection_sequence=0;
string g_sample_context="";
string g_diagnostic_context="";
string g_last_diagnostic_context="";
struct JPWIndicatorDiagnosticPending
  { string context; int code; long sample_id; long utc; long mono; };
JPWIndicatorDiagnosticPending g_diagnostic_pending[];
JPWIndicatorDiagnosticPending g_diagnostic_overflow;
bool g_diagnostic_queue_lost=false;
JPWStoreResult g_diagnostic_write_state=JPW_STORE_ABSENT;
JPWStoreResult g_diagnostic_state=JPW_STORE_ABSENT;
JPWDiagTiming g_indicator_timing;
int g_metric_last_quality[JPW_COCKPIT_METRIC_COUNT];
JPWMetricSample g_metric_samples[JPW_COCKPIT_METRIC_COUNT];
double g_numeric_values[JPW_COCKPIT_METRIC_COUNT];
bool g_numeric_valid[JPW_COCKPIT_METRIC_COUNT];
long g_source_times[JPW_COCKPIT_METRIC_COUNT];
bool g_refresh_requested=false,g_record_read_requested=false;
string g_diagnostic_summary="Diagnóstico ainda não consultado.";
string g_diagnostic_reason="",g_export_preview="",g_export_result="";
int g_focus_action=-1;
int g_focus_actions[128],g_focus_count=0;
bool g_export_preview_requested=false,g_export_requested=false;
bool g_editing_field=false;
ulong g_last_cycle_duration_ms=0,g_cycle_started_ms=0;
int g_record_read_stage=0;

JPWCockpitPrefs g_cockpit_prefs,g_cockpit_draft;
JPWCockpitSnapshot g_cockpit_snapshot;
bool g_cockpit_pref_invalid=false;
bool g_cockpit_reset_requested=false;
bool g_hud_summary=false;
int g_hud_summary_source=-1;
int g_cockpit_template_recheck=0;
string g_cockpit_pref_notice="";
int g_cockpit_selected=0;
int g_cockpit_page=0;
JPW_VIEW_QUALITY g_leverage_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_floating_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_genesis_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_raiz_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_scale2_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_stop_quality=JPW_VIEW_NA;
JPW_VIEW_QUALITY g_compensated_quality=JPW_VIEW_NA;
string g_floating_value="N/A",g_floating_reason="Aguardando leitura da conta";
string g_genesis_value="N/A",g_genesis_reason="Aguardando referência";
string g_raiz_value="N/A",g_scale2_value="N/A";
string g_raiz_reason="Aguardando dados",g_scale2_reason="Aguardando dados";
string g_leverage_reason="Aguardando dados";
string g_stop_value="N/A",g_stop_reason="Aguardando EA observador";
string g_stop_detail="Nenhuma amostra atual e coerente de risco dos stops.";
JPWObserverPresenceState g_stop_observer_presence=JPW_OBSERVER_CONTEXT_UNAVAILABLE;
bool g_stops_show_pending=false;
bool g_positions_operation_only=false;
int g_positions_scroll=0,g_positions_visible_rows=0,g_positions_total_rows=0;
bool g_position_detail_open=false;
ulong g_position_detail_ticket=0;
long g_position_detail_identifier=0;
int g_position_button_row[16];
ulong g_position_button_ticket[16];
long g_position_button_identifier[16];
JPWStopRiskSample g_stop_sample,g_stop_last_sample;
JPWStopRiskRow g_stop_rows[],g_stop_last_rows[];
bool g_stop_ready=false,g_stop_last_ready=false,g_stop_scope_valid=false;
bool g_stop_last_scope_valid=false;
string g_stop_last_scope_symbol="",g_stop_last_provenance="",g_stop_last_scope_reason="";
int g_stop_last_scope_side=0;

string g_stop_last_reason="Registro ainda não consultado.";
string g_stop_scope_symbol="",g_stop_provenance="";
int g_stop_scope_side=0,g_stop_excluded=0,g_stop_selected_row=-1;
int g_stop_button_row[16],g_stop_button_count=0;
string g_stop_button_role[16],g_stop_selected_role="";
JPWStopRiskSample g_stop_table_sample;
JPWStopRiskRow g_stop_table_rows[];
bool g_stop_table_historical=false;
long g_stop_genesis_identifier=0,g_stop_genesis_ticket=0,g_stop_genesis_opened_msc=0;
bool g_stop_genesis_closed=false;
double g_stop_positions_money=0.0,g_stop_pending_money=0.0;
double g_stop_additional_money=0.0,g_stop_total_money=0.0,g_stop_total_percent=0.0;
ulong g_last_full_refresh_ms=0;
long g_last_full_refresh_utc=0;
string g_panel_value="Aguardando dados";
string g_panel_status="";
string g_floating_line="Floating P/L: N/A";
string g_dd_line="DD / saldo: N/D";
string g_floating_short="P/L: N/A";
string g_dd_short="DD: N/D";
string g_floating_tooltip="Flutuante / saldo: aguardando leitura da conta";
string g_dd_tooltip="DD / saldo: aguardando leitura da conta";
string g_genesis_line="Genesis SL: N/A";
string g_genesis_short="SL: N/A";
string g_genesis_tooltip="Distância ao SL: aguardando leitura da referência.";
string g_raiz_line="Raiz N diag. 1W: N/A";
string g_raiz_short="RN1W: N/A";
string g_raiz_tooltip="Raiz N diagnostica: aguardando dados.";
string g_scale2_line="Raiz N diag. 2W: N/A";
string g_scale2_short="RN2W: N/A";
string g_scale2_tooltip="Raiz N diagnostica: aguardando dados.";
JPWHorizonResult g_horizon_result;
long g_horizon_tick_baseline_msc=0;
bool g_horizon_new_tick=false;
bool g_horizon_was_connected=false;
bool g_raiz_due=false;
bool g_raiz_details_open=false;
bool g_raiz_panel_built=false;
int g_raiz_tab=JPW_ROUTE_OVERVIEW;
int g_raiz_page=0,g_raiz_pages=1;
JPWPanelRect g_details_rect;
int g_details_pad=6,g_details_line=18,g_details_control=24,g_details_font=10;
color g_details_text=C'60,60,60',g_details_surface=clrWhite;
color g_details_chrome=C'239,242,246',g_details_card=C'247,248,250';
color g_details_border=C'207,211,217';
JPWRaizNConfig g_live_config;
JPW_RAIZN_STATE g_live_config_state=JPW_RAIZN_ABSENT;
string g_live_key="",g_live_reason="";
long g_live_draft_generation=0;
JPWRaizNFactorPreference g_factor_preference;
JPW_RAIZN_STATE g_factor_state=JPW_RAIZN_ABSENT;
string g_factor_key="",g_factor_reason="";
double g_factor_draft=JPW_RAIZN_FACTOR_DEFAULT;
long g_factor_draft_generation=0;
JPWRaizNLiveCache g_live_cache;
JPWRaizNLiveSample g_live_sample;
string g_saved_raiz_line="",g_saved_raiz_tooltip="";
string g_mdd_summary="Registro ainda não consultado.",g_mdd_context="";
string g_observer_summary="Observador local ainda não consultado.";
string g_observer_context="";
bool g_live_connected=false,g_live_clock_valid=false;
long g_live_now_ms=0;
string g_raiz_fields[21]; // 17..20: live N, reason N, F, reason F.
string g_raiz_feedback="";
string g_raiz_comparison="Sem vínculo explícito: comparação ao SL indisponível.";
JPWAccount g_raiz_draft_account;
bool g_raiz_draft_account_known=false;
string g_raiz_draft_symbol="";
string g_raiz_draft_expected_id="";
JPWRaizNScenario g_raiz_scenario;
JPWRaizNBinding g_raiz_binding;
JPW_RAIZN_STATE g_raiz_store_state=JPW_RAIZN_ABSENT;
int g_raiz_atr_handle=INVALID_HANDLE;
int g_panel_count=0;
ulong g_last_log_ms=0;
bool g_used_unsynchronized=false;
bool g_genesis_due=false;
JPWAccount g_genesis_refresh_account;
bool g_genesis_refresh_connected=false;
bool g_genesis_refresh_clock_valid=false;
long g_genesis_refresh_now_ms=0;
ulong g_genesis_refresh_started=0;

void JPWCollectGenesis(JPWAccount &account,const bool connected,
                       const bool clock_valid,const long now_ms,
                       const ulong started);
void JPWCollectRaizN();
void JPWClearRaizLiveSample(const string reason);
void JPWRenderRaizDetails();
void JPWRenderCockpit();
void JPWRaizPanelDestroy();
void JPWCollectStopRisk();
void JPWDetailsReadStopRisk();
bool JPWCoordinatorBudgetRemaining();
void JPWRenderStopsTable(const int x,const int body_y,const int inner,
                         const int body_height,const int footer_y);

// Account metrics are independent of the notional conversion and its routes.
// B/E/P/C are read in account units, then account identity, B and C are
#include <JPWealth/JPW_Genetrix_UI.mqh>
#include <JPWealth/JPW_PersonalHistory_UI.mqh>
#include <JPWealth/JPW_Alavancagem_Coordinator.mqh>
#include <JPWealth/JPW_SignalCopy_Controller.mqh>
#include <JPWealth/JPW_Alavancagem_Presentation.mqh>
#include <JPWealth/JPW_SignalCopy_UI.mqh>
#include <JPWealth/JPW_Alavancagem_Actions.mqh>

bool JPWGenetrixHandleCycleEvent(const int id,const long key,const string object_name)
  {
   if(!g_raiz_details_open || !JPWUIOwns(g_panel_prefix) || !JPWDetailsContextCurrent()) return(false);
   JPWAccount event_account;
   if(!JPWReadAccount(event_account) || !JPWAccountsEqual(g_account,event_account) ||
      g_cockpit_snapshot.symbol!=_Symbol)
     {
      JPWInvalidateIdentityPresentation(); g_refresh_requested=true;
      JPWRenderCurrentDisplay(); return(true);
     }
   string target=object_name;
   if(id==CHARTEVENT_KEYDOWN && key==13 && !g_editing_field &&
      ((g_focus_action>=JPW_ACTION_LEDGER_CYCLE_FIRST &&
        g_focus_action<JPW_ACTION_LEDGER_CYCLE_FIRST+g_genetrix_cycle_button_count) ||
       (g_cockpit_selected==6 && g_raiz_tab==JPW_ROUTE_METRIC && g_focus_action==JPW_ACTION_SECONDARY) ||
       (g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES &&
        (g_focus_action==JPW_ACTION_PRIMARY || g_focus_action==JPW_ACTION_SECONDARY))))
      target=JPWActionObject(g_focus_action);
   else if(id!=CHARTEVENT_OBJECT_CLICK) return(false);
   if(g_raiz_tab==JPW_ROUTE_METRIC && g_cockpit_selected==6 &&
      target==JPWActionObject(JPW_ACTION_SECONDARY))
     {
      if(ObjectFind(0,target)<0) return(true);
      ObjectSetInteger(0,target,OBJPROP_STATE,false);
      JPWRaizSwitchTab(JPW_ROUTE_LEDGER_CYCLES); return(true);
     }
   if(g_raiz_tab!=JPW_ROUTE_LEDGER_CYCLES) return(false);
   for(int j=0;j<g_genetrix_cycle_button_count;j++)
      if(target==JPWActionObject(JPW_ACTION_LEDGER_CYCLE_FIRST+j))
        {
         if(ObjectFind(0,target)<0) return(true);
         ObjectSetInteger(0,target,OBJPROP_STATE,false);
         const int selected=JPWGenetrixFindCycle(g_genetrix_cycles,g_genetrix_cycle_button_id[j]);
         if(JPWGenetrixSelectCycle(selected))
           { g_cockpit_selected=6; JPWBuildPresentation(g_panel_value,g_panel_status);
             JPWRaizSwitchTab(JPW_ROUTE_METRIC); }
         else
           { g_genetrix_ledger_reason="Ciclo não disponível nesta leitura; atualize o ledger";
             JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); }
         return(true);
        }
   if(target==JPWActionObject(JPW_ACTION_PRIMARY) || target==JPWActionObject(JPW_ACTION_SECONDARY))
     {
      if(ObjectFind(0,target)<0) return(true);
      ObjectSetInteger(0,target,OBJPROP_STATE,false);
      g_cockpit_selected=6;
      JPWRaizSwitchTab(target==JPWActionObject(JPW_ACTION_PRIMARY) ? JPW_ROUTE_METRIC : JPW_ROUTE_OVERVIEW);
      return(true);
     }
   return(false);
  }

int OnInit()
  {
   if(InpUpdateSeconds<1 || InpUpdateSeconds>3600 || InpMaxQuoteAgeSeconds<1 ||
      InpMaxQuoteAgeSeconds>30 || InpOffsetX<0 || InpOffsetY<0 || InpFontSize<8 || InpFontSize>40 || InpCockpitFontSize<9 || InpCockpitFontSize>24)
      return(INIT_PARAMETERS_INCORRECT);
   if(InpGenesisTicket<0 || !MathIsValidNumber(InpPipSize) || InpPipSize<0.0)
      return(INIT_PARAMETERS_INCORRECT);
   g_panel_prefix=StringFormat("JPW_LEV_%I64d_",ChartID());
   JPWCockpitRemoveForeignHUD(g_panel_prefix);
   // Templates can restore a transient dialog under this same ChartID.
   // Keep the chart preference and remove only our RAIZ_UI_* controls.
   JPWRaizPanelDestroy();
   JPWCockpitLoadPrefs();
   JPWSignalClear();
   g_cockpit_template_recheck=(ObjectFind(0,JPW_COCKPIT_PREF_OBJECT)<0 &&
                               ObjectFind(0,JPW_COCKPIT_PREF_V2_OBJECT)<0 &&
                               ObjectFind(0,JPW_COCKPIT_PREF_LEGACY_OBJECT)<0 ? 5 : 0);
   g_cockpit_draft=g_cockpit_prefs;
   g_raiz_atr_handle=iATR(_Symbol,PERIOD_H4,55);
   JPWRaizNLiveResetCache(g_live_cache);
   JPWHorizonClear(g_horizon_result);
   JPWHorizonResetTickEvidence();
   JPWRaizNClearScenario(g_raiz_scenario);
   JPWRaizNClearBinding(g_raiz_binding);
   IndicatorSetString(INDICATOR_SHORTNAME,JPW_PRODUCT_NAME+" · Cockpit "+JPW_PRODUCT_VERSION);
   JPWResetData(); JPWRender("Aguardando dados");
   // Stop risk has a separate freshness contract: even when other readings
   // are requested hourly, check its EA lease and live composition <=5 s.
   const int timer_seconds=(InpUpdateSeconds<5 ? InpUpdateSeconds : 5);
   if(!EventSetTimer(timer_seconds))
     {
      if(g_raiz_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_raiz_atr_handle);
      JPWClearPanel(); return(INIT_FAILED);
     }
   return(INIT_SUCCEEDED);
  }
void OnTimer()
  {
   // Templates may restore chart objects just after indicator initialization.
   // The bounded read never writes a template or overrides an active draft.
   if(g_cockpit_template_recheck>0 && !g_raiz_details_open)
     {
      if(ObjectFind(0,JPW_COCKPIT_PREF_OBJECT)>=0 ||
         ObjectFind(0,JPW_COCKPIT_PREF_V2_OBJECT)>=0 ||
         ObjectFind(0,JPW_COCKPIT_PREF_LEGACY_OBJECT)>=0)
        { JPWCockpitLoadPrefs(); g_cockpit_draft=g_cockpit_prefs;
          g_cockpit_template_recheck=0; }
      else g_cockpit_template_recheck--;
     }
   const ulong now_ms=GetTickCount64();
   const ulong cycle_started=now_ms; g_cycle_started_ms=cycle_started;
   JPWAccount current;
   const bool account_changed=(!g_account_known || !JPWReadAccount(current) ||
                               !JPWAccountsEqual(g_account,current));
   const bool connection_changed=(g_connected!=(bool)TerminalInfoInteger(TERMINAL_CONNECTED));
   if(g_refresh_requested || JPWFullRefreshRequired(account_changed,connection_changed,
                             now_ms,g_last_full_refresh_ms,InpUpdateSeconds))
     {
      g_refresh_requested=false;
      JPWRefresh();
     }
   else
     {
      JPWExpireTimedMetrics();
      JPWMonitorStopRisk(); JPWRefreshRequestedRecords();
      JPWConfirmAcceptedContext(); JPWRenderCurrentDisplay();
     }
   if(JPWCoordinatorBudgetRemaining()) JPWSignalProcessRequests(cycle_started);
   if(JPWCoordinatorBudgetRemaining()) JPWFlushDiagnostics();
   else JPWQueueDiagnostic(JPW_DIAG_BUDGET_DEFERRED);
   g_last_cycle_duration_ms=GetTickCount64()-cycle_started;
   JPWDiagTimingRecord(g_indicator_timing,(long)g_last_cycle_duration_ms,g_last_cycle_duration_ms>=500);
  }
int OnCalculate(const int rates_total,const int prev_calculated,const int begin,const double &price[])
  { return(rates_total); }

void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)
  {
   // Another indicator's focused editor must not activate Cockpit shortcuts.
   // All non-key events retain the existing identity/field/event handling.
   if(!JPWCockpitAcceptChartEvent(id,lparam,dparam,sparam)) return;
   if(JPWGenetrixHandleCycleEvent(id,lparam,sparam)) return;
   JPWHandleChartEvent(id,lparam,dparam,sparam);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   JPWUIRelease(g_panel_prefix);
   JPWSignalClear();
   // Prioritize a durable notice of abandoned diagnostics; never silently drop
   // a pending old-context failure behind a SESSION_END in a bounded FIFO.
   string prior_context="";
   if(ArraySize(g_diagnostic_pending)>0 || g_diagnostic_queue_lost)
      JPWIndicatorTerminalDiagnostic(g_diagnostic_context,JPW_DIAG_RETRY_EXHAUSTED);
   for(int i=0;i<ArraySize(g_diagnostic_pending);i++)
     {
      const string context=g_diagnostic_pending[i].context;
      if(context==g_diagnostic_context || context==prior_context) continue;
      if(prior_context=="") { prior_context=context; JPWIndicatorTerminalDiagnostic(context,JPW_DIAG_RETRY_EXHAUSTED); }
      else JPWIndicatorDiagnosticFailureMarker(context);
     }
   JPWIndicatorTerminalDiagnostic(g_diagnostic_context,JPW_DIAG_SESSION_END);
   if(g_raiz_atr_handle!=INVALID_HANDLE) IndicatorRelease(g_raiz_atr_handle);
   JPWRaizPanelDestroy();
   JPWClearPanel();
  }

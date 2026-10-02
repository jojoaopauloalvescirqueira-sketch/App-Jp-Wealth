#ifndef JPW_PERSONAL_HISTORY_UI_MQH
#define JPW_PERSONAL_HISTORY_UI_MQH
#include <JPWealth/JPW_PersonalHistory_Export.mqh>
// Read model only. Actions queue requests; the coordinator owns all file/SQL IO.
string g_personal_scope="",g_personal_operating_key="",g_personal_category="SUMMARY";
string g_personal_accounts[],g_personal_reason="Histórico ainda não consultado.",g_personal_export_result="",g_personal_export_scope="";
JPWPersonalSummary g_personal_summary;
JPWPersonalRow g_personal_rows[],g_personal_detail;
bool g_personal_available=false,g_personal_read_requested=true;
ulong g_personal_read_mono=0;
string g_personal_live_notice="EA observador sem evidência recente";
int g_personal_live_count=-1,g_personal_live_state=-1;
int g_personal_export_requested=0,g_personal_account_index=-1;
long g_personal_before=0,g_personal_detail_seq=0;
long g_personal_cursor[];
int g_personal_cursor_page=0,g_personal_button_count=0;
long g_personal_button_seq[8];
void JPWPersonalRequestRead() { g_personal_read_requested=true; }
void JPWPersonalRequestExport(const int kind)
  {
   if(kind!=1 && kind!=2) return;
   if(g_personal_export_requested!=0)
     { g_personal_export_result="Pedido anterior em andamento; aguarde sua conclusão."; return; }
   if(!g_personal_available || g_personal_scope=="")
     { g_personal_export_result="Conta consultada indisponível; exportação não solicitada."; return; }
   g_personal_export_scope=g_personal_scope; g_personal_export_requested=kind;
   g_personal_export_result=(kind==1 ? "CSV solicitado" : "Backup solicitado")+" para "+
      StringSubstr(g_personal_export_scope,0,12)+"…; aguarde confirmação de gravação.";
  }
void JPWPersonalInvalidateContext()
  {
   if(g_personal_scope==g_personal_operating_key) g_personal_scope="";
   g_personal_operating_key=""; g_personal_available=false; g_personal_live_state=-1;
   g_personal_live_count=-1; g_personal_live_notice="Conta operacional em confirmação";
   g_personal_reason="Contexto alterado; consulta anterior indisponível até nova leitura.";
   g_personal_account_index=-1; g_personal_detail_seq=0; g_personal_before=0; g_personal_cursor_page=0;
   ArrayResize(g_personal_rows,0); ArrayResize(g_personal_cursor,0); g_personal_read_requested=true;
  }
void JPWPersonalResetPage()
  { g_personal_before=0; g_personal_cursor_page=0; g_personal_detail_seq=0; g_cockpit_page=0;
    g_personal_read_requested=true; ArrayResize(g_personal_rows,0); ArrayResize(g_personal_cursor,0); }
void JPWPersonalReadPresence()
  {
   g_personal_live_notice="EA observador sem evidência recente"; g_personal_live_count=-1; g_personal_live_state=-1;
   if(g_personal_operating_key=="") return;
   const string prefix="JPWPH_"+StringSubstr(g_personal_operating_key,0,24)+"_";
   const long now=(long)TimeGMT(); int worst=-1; bool standby=false;
   for(int i=0;i<GlobalVariablesTotal();i++)
     {
      const string name=GlobalVariableName(i); if(StringFind(name,prefix)!=0 || StringLen(name)!=55) continue;
      double raw=0; if(!GlobalVariableGet(name,raw) || !MathIsValidNumber(raw) || raw<0 || raw!=MathFloor(raw)) continue;
      const long packed=(long)raw,wall=packed/16; const int status=(int)(packed%16);
      if(status<0 || status>6 || now<wall || now-wall>10 || status==6) continue;
      if(status==4) { standby=true; continue; }
      if(status>worst) worst=status;
      double count=0; const string counter="JPWPC_"+StringSubstr(name,6);
      if(GlobalVariableGet(counter,count) && MathIsValidNumber(count) && count>=0 && count<=JPW_PERSONAL_MAX_SUBJECTS)
         g_personal_live_count=MathMax(g_personal_live_count,(int)count);
     }
   g_personal_live_state=worst;
   if(worst==3) g_personal_live_notice="histórico incompleto — gravação não confirmada";
   else if(worst==5) g_personal_live_notice="Aviso local com resultado incompleto; consulte Histórico";
   else if(worst==2) g_personal_live_notice="Leitura desconhecida/interrupção · consulte cobertura";
   else if(worst==1) g_personal_live_notice=(g_personal_live_count>=0 ? "EA observador recente · "+IntegerToString(g_personal_live_count)+" sujeitos sem SL registrado na corretora" : "EA observador recente · contagem sem SL desconhecida; consulte Histórico");
   else if(worst==0) g_personal_live_notice="EA observador inicializando";
   else if(standby) g_personal_live_notice="Instância em espera; titularidade de outro escritor";
  }
void JPWPersonalCollectUI()
  {
   if(!JPWCoordinatorBudgetRemaining() || !g_account_known || g_diagnostic_context=="") return;
   if(g_personal_operating_key!=g_diagnostic_context)
     {
      if(g_personal_scope=="" || g_personal_scope==g_personal_operating_key) g_personal_scope=g_diagnostic_context;
      g_personal_operating_key=g_diagnostic_context; g_personal_available=false; JPWPersonalResetPage();
     }
   JPWPersonalReadPresence();
   const ulong now=GetTickCount64();
   if(g_raiz_details_open && (now<g_personal_read_mono || now-g_personal_read_mono>=5000)) g_personal_read_requested=true;
   if(g_personal_export_requested!=0)
     {
      const bool backup=(g_personal_export_requested==2); const string requested_scope=g_personal_export_scope;
      g_personal_export_requested=0; g_personal_export_scope="";
      string path="",reason="";
      if(JPWPersonalExport(requested_scope,backup,path,reason)) g_personal_export_result="Arquivo da conta "+StringSubstr(requested_scope,0,12)+"… gravado: "+path;
      else g_personal_export_result="Exportação da conta "+StringSubstr(requested_scope,0,12)+"… não confirmada: "+reason;
      JPWRaizPanelDestroy();
     }
   if(!g_personal_read_requested || !JPWCoordinatorBudgetRemaining()) return;
   g_personal_read_requested=false; g_personal_read_mono=now; g_personal_available=false; ArrayResize(g_personal_rows,0);
   if(!JPWPersonalListAccounts(g_personal_accounts))
     { g_personal_reason="Catálogo de contas indisponível; nenhum histórico foi substituído."; return; }
   g_personal_account_index=-1;
   for(int i=0;i<ArraySize(g_personal_accounts);i++) if(g_personal_accounts[i]==g_personal_scope) g_personal_account_index=i;
   if(!JPWPersonalReadSummary(g_personal_scope,g_personal_summary))
     { g_personal_reason=g_personal_summary.reason; JPWRaizPanelDestroy(); return; }
   g_personal_available=true; g_personal_reason=g_personal_summary.reason;
   if(g_personal_detail_seq>0)
     { if(!JPWPersonalReadDetail(g_personal_scope,g_personal_detail_seq,g_personal_detail,g_personal_reason))
         { g_personal_detail_seq=0; g_personal_available=false; } }
   else if(g_personal_category!="SUMMARY" && !JPWPersonalReadPage(g_personal_scope,g_personal_category,g_personal_before,8,g_personal_rows,g_personal_reason))
      g_personal_available=false;
   JPWRaizPanelDestroy();
  }
string JPWPersonalScopeLabel()
  { return(g_personal_operating_key=="" ? "Conta operacional em confirmação · consulta indisponível" :
      (g_personal_scope==g_personal_operating_key ? "Conta atual · consulta local" : "Conta histórica · consulta somente")); }
string JPWPersonalPeakLabel(JPWPersonalPeak &peak)
  { return(peak.valid ? DoubleToString(peak.leverage,8)+"x · "+TimeToString((datetime)peak.wall,TIME_DATE|TIME_SECONDS)+" UTC" : "indisponível"); }
#endif

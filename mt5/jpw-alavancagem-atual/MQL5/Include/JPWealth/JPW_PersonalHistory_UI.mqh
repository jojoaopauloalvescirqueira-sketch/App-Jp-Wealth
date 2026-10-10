#ifndef JPW_PERSONAL_HISTORY_UI_MQH
#define JPW_PERSONAL_HISTORY_UI_MQH
#include <JPWealth/JPW_PersonalHistory_Export.mqh>
// Read model only. Actions queue requests; the coordinator owns all file/SQL IO.
string g_personal_scope="",g_personal_operating_key="",g_personal_category="SUMMARY";
string g_personal_accounts[],g_personal_reason="Histórico ainda não consultado.",g_personal_export_result="",g_personal_export_scope="";
JPWPersonalSummary g_personal_summary;
JPWPersonalRow g_personal_rows[],g_personal_detail;
bool g_personal_available=false,g_personal_read_requested=true;
ulong g_personal_read_mono=0,g_personal_request_id=0;
long g_personal_read_wall=0;
string g_personal_live_notice="Núcleo Monitor sem evidência recente";
int g_personal_live_count=-1,g_personal_live_state=-1;
int g_personal_export_requested=0,g_personal_account_index=-1;
long g_personal_before=0,g_personal_detail_seq=0;
long g_personal_cursor[];
int g_personal_cursor_page=0,g_personal_button_count=0;
long g_personal_button_seq[8];
void JPWPersonalRequestRead()
  {
   g_personal_request_id++; if(g_personal_request_id==0) g_personal_request_id=1;
   g_personal_read_requested=true; g_personal_available=false;
   g_personal_button_count=0; ArrayResize(g_personal_rows,0);
   g_personal_detail.sequence=0; g_personal_detail.category=""; g_personal_detail.item_id="";
   g_personal_detail.wall=0; g_personal_detail.payload=""; g_personal_detail.digest="";
   g_personal_reason="Consulta selecionada em leitura; aguarde.";
  }
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
   ArrayResize(g_personal_cursor,0); JPWPersonalRequestRead();
  }
void JPWPersonalResetPage()
  { g_personal_before=0; g_personal_cursor_page=0; g_personal_detail_seq=0; g_cockpit_page=0;
    ArrayResize(g_personal_cursor,0); JPWPersonalRequestRead(); }
void JPWPersonalReadPresence()
  {
   g_personal_live_notice="Núcleo Monitor sem evidência recente"; g_personal_live_count=-1; g_personal_live_state=-1;
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
   else if(worst==1) g_personal_live_notice=(g_personal_live_count>=0 ? "Núcleo Monitor recente · "+IntegerToString(g_personal_live_count)+" sujeitos sem SL registrado na corretora" : "Núcleo Monitor recente · contagem sem SL desconhecida; consulte Histórico");
   else if(worst==0) g_personal_live_notice="Núcleo Monitor inicializando";
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
   if(g_raiz_details_open && (g_raiz_tab==JPW_ROUTE_PERSONAL_HISTORY ||
       g_raiz_tab==JPW_ROUTE_PERSONAL_DETAIL || g_raiz_tab==JPW_ROUTE_PERSONAL_EXPORT) &&
       (now<g_personal_read_mono || now-g_personal_read_mono>=5000) &&
      !g_personal_read_requested) JPWPersonalRequestRead();
   if(g_personal_export_requested!=0)
     {
      const bool backup=(g_personal_export_requested==2); const string requested_scope=g_personal_export_scope;
      g_personal_export_requested=0; g_personal_export_scope="";
      string path="",reason="";
      if(JPWPersonalExport(requested_scope,backup,path,reason)) g_personal_export_result="Arquivo da conta "+StringSubstr(requested_scope,0,12)+"… gravado: "+path;
      else g_personal_export_result="Exportação da conta "+StringSubstr(requested_scope,0,12)+"… não confirmada: "+reason;
      JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_HISTORY);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_DETAIL);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_EXPORT);
     }
   if(!g_personal_read_requested || !JPWCoordinatorBudgetRemaining()) return;
   const ulong request=g_personal_request_id;
   const string scope=g_personal_scope,category=g_personal_category,operating=g_personal_operating_key;
   const long before=g_personal_before,detail_seq=g_personal_detail_seq;
   g_personal_read_requested=false; g_personal_read_mono=now; g_personal_available=false;
   ArrayResize(g_personal_rows,0); g_personal_button_count=0;
   string accounts[],reason=""; JPWPersonalSummary summary; JPWPersonalRow rows[],detail;
   bool ok=JPWPersonalListAccounts(accounts); const bool catalog_ok=ok;
   if(!ok) reason="Catálogo de contas indisponível; nenhum histórico foi substituído.";
   if(ok)
     { ok=JPWPersonalReadSummary(scope,summary) && summary.account_key==scope;
       if(!ok) reason=(summary.reason=="" ? "Resumo da conta selecionada não confirmado." : summary.reason); }
   if(ok && detail_seq>0)
     { ok=JPWPersonalReadDetail(scope,detail_seq,detail,reason) && detail.sequence==detail_seq;
       if(!ok && reason=="") reason="Identidade do detalhe não confirmada."; }
   else if(ok && category!="SUMMARY")
     {
      ok=JPWPersonalReadPage(scope,category,before,8,rows,reason);
      for(int i=0;ok && i<ArraySize(rows);i++)
         if(rows[i].category!=category || (before>0 && rows[i].sequence>=before) ||
            (i>0 && rows[i].sequence>=rows[i-1].sequence))
            { ok=false; reason="Página recusada: registros não correspondem ao pedido selecionado."; }
     }
   // A response belongs to the exact request, never to a newer selection.
   if(request!=g_personal_request_id || scope!=g_personal_scope || category!=g_personal_category ||
      before!=g_personal_before || detail_seq!=g_personal_detail_seq || operating!=g_personal_operating_key ||
      !g_account_known || g_diagnostic_context!=operating)
     { JPWPersonalRequestRead(); JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_HISTORY);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_DETAIL);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_EXPORT); return; }
   // A missing/corrupt selected history must not prevent browsing other local accounts.
   if(catalog_ok)
     {
      if(ArrayResize(g_personal_accounts,ArraySize(accounts))!=ArraySize(accounts))
        { ok=false; reason="Catálogo sem capacidade de consulta; registros preservados."; }
      else
        {
         for(int i=0;i<ArraySize(accounts);i++) g_personal_accounts[i]=accounts[i];
         g_personal_account_index=-1;
         for(int i=0;i<ArraySize(accounts);i++) if(accounts[i]==scope) g_personal_account_index=i;
        }
     }
   if(ok && ArrayResize(g_personal_rows,ArraySize(rows))!=ArraySize(rows))
     { ok=false; reason="Capacidade de consulta indisponível; registros preservados."; }
   if(ok)
     {
      for(int i=0;i<ArraySize(rows);i++) g_personal_rows[i]=rows[i];
      g_personal_summary=summary;
      if(detail_seq>0) g_personal_detail=detail;
      g_personal_read_wall=(long)TimeGMT(); g_personal_available=true; g_personal_reason=summary.reason;
     }
   else
     { ArrayResize(g_personal_rows,0); g_personal_reason=(reason=="" ? "Consulta não confirmada; atualize para tentar novamente." : reason); }
   JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_HISTORY);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_DETAIL);
       JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_EXPORT);
  }

string JPWPersonalScopeLabel()
  { return(g_personal_operating_key=="" ? "Conta operacional em confirmação · consulta indisponível" :
      (g_personal_scope==g_personal_operating_key ? "Conta atual · consulta local" : "Conta histórica · consulta somente")); }
string JPWPersonalPeakLabel(JPWPersonalPeak &peak)
  { return(peak.valid && peak.wall>0 ? DoubleToString(peak.leverage,8)+"x · "+TimeToString((datetime)peak.wall,TIME_DATE|TIME_SECONDS)+" UTC" : "indisponível nesta consulta"); }
#endif

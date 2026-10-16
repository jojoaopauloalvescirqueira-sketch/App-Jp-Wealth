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
// Presentation selectors: bounded visible slots refer to the existing RAM catalog.
int g_personal_picker=0,g_personal_picker_page=0,g_personal_choice_count=0;
int g_personal_choice_index[8];
long g_personal_button_seq[8];
JPWPersonalStoreContext g_personal_read_ctx;
JPWPersonalExportJob g_personal_export_job;
bool g_personal_job_active=false;
ulong g_personal_job_request=0;
string g_personal_job_scope="",g_personal_job_category="",g_personal_job_operating="";
long g_personal_job_before=0,g_personal_job_detail=0;
string JPWPersonalCategoryKey(const int index)
  {
   const string keys[7]={"SUMMARY","EPISODE","ALERT","PEAK","SESSION","COVERAGE","EVENT"};
   return(index>=0 && index<7 ? keys[index] : "");
  }
string JPWPersonalCategoryLabel(const string key)
  {
   if(key=="SUMMARY") return("Resumo e cobertura");
   if(key=="EPISODE") return("Ocorrências sem SL");
   if(key=="ALERT") return("Solicitações de aviso");
   if(key=="PEAK") return("Recordes de alavancagem");
   if(key=="SESSION") return("Sessões de monitoramento");
   if(key=="EVENT") return("Detecção e desfechos");
   return("Interrupções e recuperação");
  }
bool JPWPersonalUIReady()
  { return(g_personal_available && !g_personal_read_requested && !g_personal_job_active); }
string JPWPersonalUIReadState()
  {
   if(g_personal_job_active) return("Auditando");
   if(g_personal_read_requested) return("Em leitura");
   if(!g_personal_available) return("Consulta indisponível");
   return("Consulta concluída");
  }
void JPWPersonalRequestRead()
  {
   g_personal_request_id++; if(g_personal_request_id==0) g_personal_request_id=1;
   g_personal_read_requested=true; g_personal_available=false; g_personal_summary.current.valid=false; g_personal_summary.estimated.valid=false;
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
void JPWPersonalUICancelRead()
  { JPWPersonalOpenCancel(g_personal_read_ctx); g_personal_job_active=false; }
void JPWPersonalUICancelPending()
  {
   JPWPersonalUICancelRead(); JPWPersonalExportCancel(g_personal_export_job);
   g_personal_export_requested=0; g_personal_export_scope="";
  }
bool JPWPersonalUIRequestMatches()
  {
   return(g_personal_job_request==g_personal_request_id && g_personal_job_scope==g_personal_scope &&
      g_personal_job_category==g_personal_category && g_personal_job_before==g_personal_before &&
      g_personal_job_detail==g_personal_detail_seq && g_personal_job_operating==g_personal_operating_key &&
      g_account_known && g_diagnostic_context==g_personal_job_operating);
  }
void JPWPersonalUIInvalidateViews()
  {
   JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_HISTORY); JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_DETAIL);
   JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_EXPORT);
  }
void JPWPersonalCollectUI()
  {
   if(!g_account_known || g_diagnostic_context=="")
     {
      if(g_personal_job_active) JPWPersonalUICancelRead();
      if(g_personal_export_requested!=0 || g_personal_export_job.active)
        { JPWPersonalExportCancel(g_personal_export_job); g_personal_export_requested=0; g_personal_export_scope="";
          g_personal_export_result="Pedido cancelado: identidade operacional indisponível; eventual arquivo parcial sem confirmação."; }
      g_personal_available=false; g_personal_read_requested=true; g_personal_button_count=0; ArrayResize(g_personal_rows,0);
      g_personal_summary.current.valid=false; g_personal_summary.estimated.valid=false; g_personal_detail.sequence=0;
      g_personal_reason="Conta operacional em confirmação; consulta anterior indisponível."; return;
     }
   if(!JPWCoordinatorBudgetRemaining()) return;
   if(g_personal_operating_key!=g_diagnostic_context)
     {
      if(g_personal_scope=="" || g_personal_scope==g_personal_operating_key) g_personal_scope=g_diagnostic_context;
      g_personal_operating_key=g_diagnostic_context; g_personal_available=false; JPWPersonalResetPage();
     }
   JPWPersonalReadPresence(); const ulong now=GetTickCount64();
   if(g_personal_job_active && !JPWPersonalUIRequestMatches()) JPWPersonalUICancelRead();
   if(g_raiz_details_open && (g_raiz_tab==JPW_ROUTE_PERSONAL_HISTORY || g_raiz_tab==JPW_ROUTE_PERSONAL_DETAIL || g_raiz_tab==JPW_ROUTE_PERSONAL_EXPORT) &&
      !g_personal_job_active && !g_personal_read_requested && (now<g_personal_read_mono || now-g_personal_read_mono>=5000)) JPWPersonalRequestRead();
   if(g_personal_export_requested!=0)
     {
      if(!g_personal_export_job.active)
        {
         JPWPersonalExportBegin(g_personal_export_scope,g_personal_export_requested==2,g_personal_export_job);
        }
      JPWStoreResult exported=g_personal_export_job.result;
      if(g_personal_export_job.active) exported=JPWPersonalExportStep(g_personal_export_job,now,JPW_PERSONAL_SLICE_MS,JPW_PERSONAL_SLICE_ROWS);
      if(exported!=JPW_STORE_BUSY || !g_personal_export_job.active)
        {
         const string scope=g_personal_export_scope;
         g_personal_export_result=(exported==JPW_STORE_VALID ? "Arquivo da conta "+StringSubstr(scope,0,12)+"… gravado: "+g_personal_export_job.path :
            "Exportação da conta "+StringSubstr(scope,0,12)+"… não confirmada: "+g_personal_export_job.reason);
         g_personal_export_requested=0; g_personal_export_scope=""; JPWPersonalUIInvalidateViews();
        }
     }
   if(!JPWCoordinatorBudgetRemaining()) return;
   if(g_personal_read_requested && !g_personal_job_active)
     {
      g_personal_job_request=g_personal_request_id; g_personal_job_scope=g_personal_scope; g_personal_job_category=g_personal_category;
      g_personal_job_operating=g_personal_operating_key; g_personal_job_before=g_personal_before; g_personal_job_detail=g_personal_detail_seq;
      g_personal_read_requested=false; g_personal_available=false; g_personal_button_count=0; ArrayResize(g_personal_rows,0);
      // Account catalog does not depend on validity of the selected database.
      string accounts[]; bool catalog=JPWPersonalListAccounts(accounts);
      if(catalog && ArrayResize(g_personal_accounts,ArraySize(accounts))==ArraySize(accounts))
        {
         g_personal_account_index=-1;
         for(int i=0;i<ArraySize(accounts);i++) { g_personal_accounts[i]=accounts[i]; if(accounts[i]==g_personal_scope) g_personal_account_index=i; }
        }
      JPWPersonalOpenBegin(g_personal_job_scope,false,"",0,0,g_personal_read_ctx); g_personal_job_active=true;
     }
   if(!g_personal_job_active) return;
   JPWStoreResult opened=g_personal_read_ctx.result;
   if(JPWPersonalPreparing(g_personal_read_ctx)) opened=JPWPersonalOpenStep(g_personal_read_ctx,GetTickCount64(),JPW_PERSONAL_SLICE_MS,JPW_PERSONAL_SLICE_ROWS,0,0);
   if(opened==JPW_STORE_BUSY && JPWPersonalPreparing(g_personal_read_ctx))
     { g_personal_reason="Auditoria integral em preparação; aguarde a confirmação da consulta."; JPWPersonalUIInvalidateViews(); return; }
   JPWPersonalSummary summary; JPWPersonalRow rows[],detail; string reason=g_personal_read_ctx.reason;
   bool ok=(opened==JPW_STORE_VALID) && JPWPersonalReadSummaryFrom(g_personal_read_ctx,summary);
   if(ok && g_personal_job_detail>0) ok=JPWPersonalReadDetailFrom(g_personal_read_ctx,g_personal_job_detail,detail,reason) && detail.sequence==g_personal_job_detail;
   else if(ok && g_personal_job_category!="SUMMARY")
     {
      ok=JPWPersonalReadPageFrom(g_personal_read_ctx,g_personal_job_category,g_personal_job_before,8,rows,reason);
      for(int i=0;ok && i<ArraySize(rows);i++) if(rows[i].category!=g_personal_job_category ||
         (g_personal_job_before>0 && rows[i].sequence>=g_personal_job_before) || (i>0 && rows[i].sequence>=rows[i-1].sequence))
         { ok=false; reason="Página não corresponde ao pedido selecionado"; }
     }
   if(ok) { ok=JPWPersonalReadFinish(g_personal_read_ctx,true); if(!ok) reason=g_personal_read_ctx.reason; }
   bool matches=JPWPersonalUIRequestMatches(); JPWPersonalUICancelRead();
   if(!matches) { g_personal_available=false; JPWPersonalUIInvalidateViews(); return; }
   g_personal_read_mono=GetTickCount64(); g_personal_summary.current.valid=false; g_personal_summary.estimated.valid=false;
   if(ok && ArrayResize(g_personal_rows,ArraySize(rows))!=ArraySize(rows)) { ok=false; reason="Capacidade de consulta indisponível; registros preservados"; }
   if(ok)
     {
      for(int i=0;i<ArraySize(rows);i++) g_personal_rows[i]=rows[i]; g_personal_summary=summary;
      if(g_personal_job_detail>0) g_personal_detail=detail;
      g_personal_read_wall=(long)TimeGMT(); g_personal_available=true; g_personal_reason=summary.reason;
     }
   else { ArrayResize(g_personal_rows,0); g_personal_available=false; g_personal_reason=(reason=="" ? "Consulta não confirmada; atualize para tentar novamente" : reason); }
   JPWPersonalUIInvalidateViews();
  }

string JPWPersonalScopeLabel()
  { return(g_personal_operating_key=="" ? "Conta operacional em confirmação · consulta indisponível" :
      (g_personal_scope==g_personal_operating_key ? "Conta atual · consulta local" : "Conta histórica · consulta somente")); }
string JPWPersonalPeakLabel(JPWPersonalPeak &peak)
  { return(peak.valid && peak.wall>0 ? DoubleToString(peak.leverage,8)+"x · "+TimeToString((datetime)peak.wall,TIME_DATE|TIME_SECONDS)+" UTC" : "indisponível nesta consulta"); }
#endif

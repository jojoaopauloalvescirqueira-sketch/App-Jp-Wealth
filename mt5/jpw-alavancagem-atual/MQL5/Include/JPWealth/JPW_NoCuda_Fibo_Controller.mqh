#ifndef JPW_NOCUDA_FIBO_CONTROLLER_MQH
#define JPW_NOCUDA_FIBO_CONTROLLER_MQH
#include <JPWealth/JPW_NoCuda_Fibo_Core.mqh>
#include <JPWealth/JPW_NoCuda_Fibo_Terminal.mqh>
#include <JPWealth/JPW_NoCuda_Fibo_Store.mqh>
#include <JPWealth/JPW_NoCuda_Fibo_Sync.mqh>
#include <JPWealth/JPW_NoCuda_Fibo_UI.mqh>
#include <JPWealth/JPW_UI_Focus.mqh>
#include <JPWealth/JPW_Alavancagem_Version.mqh>

// Native Fibonacci is an editor, never a financial input. The controller is
// the only owner of captures/checkpoints. Paint/navigation cannot save studies.
bool g_ncf_mode=true,g_ncf_has=false,g_ncf_import=false,g_ncf_link=false;
bool g_ncf_hidden=false,g_ncf_source_dirty=false,g_ncf_observation_ready=false;
int g_ncf_reference_tf=PERIOD_H1,g_ncf_level=32,g_ncf_record_revision=0;
string g_ncf_key="",g_ncf_id="",g_ncf_selected_source="",g_ncf_notice="";
string g_ncf_clone="",g_ncf_observation_payload="";
long g_ncf_original_mask=0,g_ncf_source_created=0;
// Restoration belongs to the object we hid, independently of later selection.
string g_ncf_restore_source="",g_ncf_restore_reason="";
long g_ncf_restore_created=0,g_ncf_restore_mask=0;
bool g_ncf_restore_requested=false;
ulong g_ncf_history_checked_ms=0;
bool g_ncf_history_conflict=false,g_ncf_import_was_armed=false,g_ncf_records_dirty=true;
int g_ncf_catalog_offset=0; bool g_ncf_catalog_more=false,g_ncf_catalog_all=true;
double g_ncf_selected_raw=0.0;
JPWNCFSnapshot g_ncf_saved,g_ncf_preview;
JPWNCFHead g_ncf_head;
JPWNCFSyncState g_ncf_sync;
JPWNoCudaFiboView g_ncf_ui;

bool JPWNCFContextCurrent()
  {
   if(_Symbol==g_nocuda_symbol && AccountInfoString(ACCOUNT_SERVER)==g_nocuda_feed) return(true);
   // A terminal feed can change while history APIs are running. Refuse the
   // result and every following write; OnTimer resets both editors next.
   g_ncf_has=false; g_ncf_link=false; g_ncf_import=false;
   JPWNCFSyncPause(g_ncf_sync); g_ncf_ui.quote_text="N/A · contexto alterado";
   ArrayResize(g_ncf_ui.records,0); ArrayResize(g_ncf_ui.sources,0);
   g_ncf_ui.record_detail="";
   g_ncf_notice="Símbolo/feed alterado durante a leitura; resultado recusado. Aguarde atualização do contexto.";
   return(false);
  }

string JPWNCFPhaseText()
  {
   if(g_ncf_import) return("Prévia de importação · confira período e âncoras");
   if(!g_ncf_has) return("Nenhum estudo vinculado");
   if(g_ncf_sync.phase==JPW_NCF_DETACHED) return("Origem ausente · última revisão preservada");
   if(g_ncf_sync.phase==JPW_NCF_SYNC_CONFLICT) return("Conflito · revisão anterior preservada");
   if(g_ncf_sync.phase==JPW_NCF_PAUSED) return("Acompanhamento pausado");
   if(g_ncf_sync.phase==JPW_NCF_EDITING_PREVIEW) return("Prévia transitória · ainda não gravada");
   if(g_ncf_sync.phase==JPW_NCF_SAVE_PENDING) return("Gravação pendente");
   if(g_ncf_sync.phase==JPW_NCF_SOURCE_INVALID) return("Fonte indisponível para conferir");
   return(g_ncf_link ? "Sincronizado · propriedades conferidas" : "Revisão local · vínculo não retomado");
  }
void JPWNCFMetricUnavailable(JPWNoCudaFiboUIMetric &m,const string label)
  {
   m.valid=false; m.highlight=false; m.label=label; m.raw_level="—";
   m.price="N/A"; m.nominal="N/A"; m.points="N/A"; m.percent="N/A";
   m.state="N/A · UNVERIFIED_NATIVE";
   m.reason="Correspondência numérica com Fibonacci exige laboratório nativo dos bytes exatos.";
  }
void JPWNCFInvalidateMeasures()
  {
   JPWNCFMetricUnavailable(g_ncf_ui.below,"Linha abaixo");
   JPWNCFMetricUnavailable(g_ncf_ui.above,"Linha acima");
   JPWNCFMetricUnavailable(g_ncf_ui.nearest,"Mais próxima");
   JPWNCFMetricUnavailable(g_ncf_ui.selected,"Selecionada");
   if(g_ncf_has)
     { for(int i=0;i<65;i++) if(MathAbs(g_ncf_saved.levels[i].value-g_ncf_selected_raw)<1e-12) { g_ncf_level=i; break; }
       g_ncf_ui.selected.label=g_ncf_saved.levels[g_ncf_level].label;
       g_ncf_ui.selected.raw_level=DoubleToString(g_ncf_saved.levels[g_ncf_level].value,3); }
   const string labels[5]={"00h · início","12h · meio do dia","24h · dia seguinte","Média dos extremos","Faixa da linha"};
   for(int i=0;i<5;i++) { g_ncf_ui.projection_labels[i]=labels[i]; g_ncf_ui.projection_values[i]="N/A"; }
   g_ncf_ui.provenance="JPW "+JPW_PRODUCT_VERSION+" · build "+StringSubstr(JPW_BUILD_ID,0,12)+". Horário do servidor. H1/H4 futuros serão Estimated; sem paridade nativa não há preço geométrico aprovado.";
  }
void JPWNCFQuote()
  {
   MqlTick tick; long mode=0;
   if(!SymbolInfoInteger(g_nocuda_symbol,SYMBOL_CHART_MODE,mode) || !SymbolInfoTick(g_nocuda_symbol,tick))
     { g_ncf_ui.quote_text="N/A · cotação indisponível"; return; }
   const bool last=(mode==SYMBOL_CHART_MODE_LAST);
   const double quote=(last ? tick.last : tick.bid);
   const datetime now=TimeTradeServer();
   if(!JPWNCFFinitePositive(quote) || tick.time<=0)
     { g_ncf_ui.quote_text="N/A · base do gráfico indisponível"; return; }
   const bool current=(bool)TerminalInfoInteger(TERMINAL_CONNECTED) && now>=tick.time &&
                      now-tick.time<=InpMaxQuoteAgeSeconds;
   g_ncf_ui.quote_text=(last ? "Last " : "Bid ")+DoubleToString(quote,(int)SymbolInfoInteger(g_nocuda_symbol,SYMBOL_DIGITS))+
      " · "+TimeToString(tick.time,TIME_DATE|TIME_SECONDS)+" (servidor) · "+(current ? "Current" : "Estimated")+
      ". Qualidade da cotação não aprova a geometria.";
  }
void JPWNCFReloadCatalog()
  {
   string names[]; const int count=JPWNCFCatalog(0,names);
   ArrayResize(g_ncf_ui.sources,MathMax(0,count));
   for(int i=0;i<count;i++)
     {
      g_ncf_ui.sources[i].id=names[i]; g_ncf_ui.sources[i].title=names[i];
      g_ncf_ui.sources[i].selected=(names[i]==g_ncf_selected_source);
      g_ncf_ui.sources[i].state="Fibonacci nativo · período não inferido pelo nome";
      string coordinates="";
      for(int j=0;j<3;j++) coordinates+=(j==0 ? "" : " | ")+TimeToString((datetime)ObjectGetInteger(0,names[i],OBJPROP_TIME,j),TIME_DATE|TIME_MINUTES)+
         ": "+DoubleToString(ObjectGetDouble(0,names[i],OBJPROP_PRICE,j),(int)SymbolInfoInteger(g_nocuda_symbol,SYMBOL_DIGITS));
      g_ncf_ui.sources[i].detail=coordinates;
     }
   if(count<0) g_ncf_notice="Catálogo indisponível; nenhuma seleção automática.";
  }
void JPWNCFReloadRecords()
  {
   ArrayResize(g_ncf_ui.records,0); string reason="";
   JPWNCFCatalogRow rows[];
   const string study=(!g_ncf_catalog_all && g_ncf_has ? g_ncf_id : "");
   const JPWNCFStatus status=JPWNCFCatalogPage(g_ncf_key,g_nocuda_symbol,study,g_ncf_catalog_offset,20,rows,g_ncf_catalog_more,reason);
   if(status!=JPW_NCF_VALID && status!=JPW_NCF_ABSENT)
      { g_ncf_notice="Catálogo indisponível: "+reason; return; }
   ArrayResize(g_ncf_ui.records,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++)
     {
      const bool is_study=rows[i].kind=="study",is_note=rows[i].kind=="observation";
      g_ncf_ui.records[i].id=is_study ? "study:"+rows[i].study_id :
         is_note ? "note:"+rows[i].entry_id : "revision:"+IntegerToString(rows[i].revision);
      g_ncf_ui.records[i].title=is_study ? rows[i].source_name :
         string(is_note ? "Observação manual" : "Versão")+" · "+IntegerToString(rows[i].revision);
      g_ncf_ui.records[i].detail="Captura: "+TimeToString((datetime)rows[i].captured_utc,TIME_DATE|TIME_SECONDS)+
         " · confirmação: "+TimeToString((datetime)rows[i].confirmed_utc,TIME_DATE|TIME_SECONDS)+
         " UTC (computador) · "+EnumToString((ENUM_TIMEFRAMES)rows[i].source_tf);
      g_ncf_ui.records[i].state="Índice conferido; snapshot conferido ao abrir; paridade nativa pendente · "+StringSubstr(rows[i].study_id,0,12);
      g_ncf_ui.records[i].selected=is_study ? rows[i].study_id==g_ncf_id : !is_note && rows[i].revision==g_ncf_record_revision;
     }
   g_ncf_records_dirty=false;
  }
void JPWNCFRememberStudy()
  {
   const string name="JPW_NOCUDA_FIBO_STUDY_V1";
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_LABEL,0,0,0)) return;
   ObjectSetInteger(0,name,OBJPROP_XDISTANCE,-10000); ObjectSetInteger(0,name,OBJPROP_YDISTANCE,-10000);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true); ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
   ObjectSetString(0,name,OBJPROP_TOOLTIP,"V1|"+g_ncf_key+"|"+g_nocuda_symbol+"|"+g_ncf_id);
  }
void JPWNCFPaint()
  {
   // A native property clone is only an aid at the reference TF, not a numerical
   // resolver. Leave the original alone unless Hide/Show was explicitly chosen.
   if(g_ncf_clone!="") { ObjectDelete(0,g_ncf_clone); g_ncf_clone=""; }
   if(!g_ncf_has || (int)_Period!=g_ncf_saved.reference_tf || (g_ncf_link && !g_ncf_hidden)) return;
   JPWNCFSnapshot visual;
   if(!JPWNCFCopy(g_ncf_saved,visual)) return;
   visual.timeframes=OBJ_ALL_PERIODS; visual.selectable=false; visual.hidden=true;
   if(g_fc_pref.mesh==0)
      for(int i=0;i<JPW_NCF_LEVELS;i++)
         if(visual.levels[i].value!=0 && visual.levels[i].value!=0.5 && visual.levels[i].value!=1)
            visual.levels[i].line_color=(int)clrNONE;
   g_ncf_clone="JPWNCF_"+g_nocuda_prefix+"VIEW"; string reason="";
   if(JPWNCFClone(0,g_ncf_clone,visual,reason)!=JPW_NCF_VALID) { g_ncf_clone=""; g_ncf_notice=reason; }
  }
void JPWNCFDraw()
  {
   JPWNCFContextCurrent();
   g_ncf_ui.symbol=g_nocuda_symbol; g_ncf_ui.linked=g_ncf_link;
   g_ncf_ui.preview=g_ncf_import; g_ncf_ui.source_hidden=g_ncf_hidden;
   g_ncf_ui.sync_paused=!g_ncf_sync.armed;
   g_ncf_ui.source_name=(g_ncf_selected_source=="" ? "Escolha um canal" : g_ncf_selected_source);
   g_ncf_ui.source_tf=EnumToString((ENUM_TIMEFRAMES)g_ncf_reference_tf);
   g_ncf_ui.status=JPWNCFPhaseText();
   g_ncf_ui.reason=(g_ncf_notice=="" ? "Medidas N/A até validação nativa; importar não certifica o método." : g_ncf_notice);
   if(g_ncf_restore_reason!="") g_ncf_ui.reason+=" · "+g_ncf_restore_reason;
   JPWNoCudaFiboUIDraw(g_nocuda_prefix,g_ncf_ui);
  }
void JPWNCFNormalizeVisibility(JPWNCFSnapshot &source)
  {
   if(!g_ncf_hidden || source.source_name!=g_ncf_restore_source ||
      source.source_created!=g_ncf_restore_created) return;
   if(source.timeframes==OBJ_NO_PERIODS) source.timeframes=g_ncf_restore_mask;
   else
     {
      // A confirmed native edit to visibility wins over our temporary hide.
      g_ncf_hidden=false; g_ncf_restore_source=""; g_ncf_restore_requested=false;
      g_ncf_restore_reason="";
      if(g_ncf_clone!="") { ObjectDelete(0,g_ncf_clone); g_ncf_clone=""; }
     }
  }
void JPWNCFRestoreOriginalVisibility()
  {
   if(g_ncf_restore_source=="") return;
   g_ncf_restore_requested=true;
   const string source=g_ncf_restore_source;
   long created=0,mask=0;
   if(ObjectFind(0,source)<0 || !ObjectGetInteger(0,source,OBJPROP_CREATETIME,0,created) ||
      created!=g_ncf_restore_created)
     {
      g_ncf_restore_reason="Restauração pendente de "+source+": origem ausente ou substituída; nenhum outro objeto foi alterado.";
      return;
     }
   if(!ObjectGetInteger(0,source,OBJPROP_TIMEFRAMES,0,mask))
     { g_ncf_restore_reason="Visibilidade de "+source+" indisponível; restauração pendente."; return; }
   bool restored=(mask==g_ncf_restore_mask);
   // A visible mask changed by the operator is authoritative; do not undo it.
   if(mask!=OBJ_NO_PERIODS && mask!=g_ncf_restore_mask) restored=true;
   if(!restored)
      restored=ObjectSetInteger(0,source,OBJPROP_TIMEFRAMES,g_ncf_restore_mask) &&
         ObjectGetInteger(0,source,OBJPROP_TIMEFRAMES,0,mask) && mask==g_ncf_restore_mask;
   if(!restored)
     {
      g_ncf_restore_reason="Visibilidade original de "+source+" não restaurada; nova tentativa no timer. Confira a origem manualmente.";
      return;
     }
   g_ncf_restore_source=""; g_ncf_restore_requested=false; g_ncf_restore_reason="";
   g_ncf_hidden=false;
  }
bool JPWNCFFrozenTimelineMatches(const JPWNCFSnapshot &old,const JPWNCFSnapshot &now)
  {
   // Compare all openings in the shared interval. Appending/prepending is not
   // a correction, but any removed/inserted historical opening is a divergence.
   int a=0,b=0; const int na=ArraySize(old.opens),nb=ArraySize(now.opens);
   if(na<2 || nb<2) return(false);
   const long first=MathMax(old.opens[0],now.opens[0]),last=MathMin(old.opens[na-1],now.opens[nb-1]);
   if(first>last) return(false);
   while(a<na && old.opens[a]<first) a++;
   while(b<nb && now.opens[b]<first) b++;
   while(a<na && b<nb && old.opens[a]<=last && now.opens[b]<=last)
     { if(old.opens[a]!=now.opens[b]) return(false); a++; b++; }
   return((a==na || old.opens[a]>last) && (b==nb || now.opens[b]>last));
  }
bool JPWNCFParseRawLevel(string text,double &level)
  {
   StringTrimLeft(text); StringTrimRight(text); StringReplace(text,",",".");
   if(text=="") return(false);
   int at=(StringSubstr(text,0,1)=="-" || StringSubstr(text,0,1)=="+" ? 1 : 0),dots=0,digits=0;
   for(int i=at;i<StringLen(text);i++)
     { ushort c=StringGetCharacter(text,i);
       if(c=='.') { if(++dots>1) return(false); }
       else if(c>='0' && c<='9') digits++; else return(false); }
   if(digits==0) return(false);
   level=StringToDouble(text); return(MathIsValidNumber(level) && level>=-4 && level<=4 &&
      MathAbs((level+4)*8-MathRound((level+4)*8))<1e-10);
  }
void JPWNCFDetach(const string reason)
  {
   JPWNCFRestoreOriginalVisibility();
   g_ncf_link=false; g_ncf_sync.armed=false; g_ncf_sync.phase=JPW_NCF_DETACHED;
   g_ncf_notice=reason; g_ncf_observation_ready=false;
   JPWNCFPaint();
  }
void JPWNCFInit()
  {
   JPWNoCudaFiboUILoadPrefs();
   g_ncf_key=""; g_ncf_notice=""; g_ncf_clone="";
   g_ncf_reference_tf=(int)InpSourceTimeframe; g_ncf_has=false; g_ncf_link=false; g_ncf_import=false;
   g_ncf_record_revision=0; g_ncf_level=32; g_ncf_selected_raw=0.0;
   g_ncf_catalog_offset=0; g_ncf_catalog_all=true;
   g_ncf_ui.record_detail=""; g_ncf_ui.observation_time=""; g_ncf_ui.observation_note="";
   g_ncf_ui.quote_text=""; g_ncf_ui.selected_text=""; g_ncf_observation_payload="";
   g_ncf_observation_ready=false; g_ncf_records_dirty=true;
   g_ncf_hidden=false; g_ncf_history_conflict=false; g_ncf_history_checked_ms=0; g_ncf_id=""; g_ncf_selected_source=""; JPWNCFSyncClear(g_ncf_sync);
   JPWNCFHeadClear(g_ncf_head); JPWNCFClear(g_ncf_saved); JPWNCFClear(g_ncf_preview);
   g_ncf_ui.open=false; g_ncf_ui.tab=0; g_ncf_ui.justification="Importação de desenho informado pelo usuário";
   g_ncf_ui.selected_value="0"; g_ncf_ui.projection_date=TimeToString(TimeTradeServer(),TIME_DATE);
   if(!JPWNCFStoreKey(TerminalInfoString(TERMINAL_DATA_PATH),g_nocuda_feed,g_ncf_key)) g_ncf_notice="Instalação/feed indisponível; gravação bloqueada.";
   const string name="JPW_NOCUDA_FIBO_STUDY_V1"; string f[];
   if(ObjectFind(0,name)>=0)
     {
      if(StringSplit(ObjectGetString(0,name,OBJPROP_TOOLTIP),'|',f)==4 && f[0]=="V1" && f[1]==g_ncf_key && f[2]==g_nocuda_symbol)
        {
         string reason=""; const JPWNCFStatus status=JPWNCFLoadHead(g_ncf_key,f[3],g_ncf_head,g_ncf_saved,reason);
         if(status==JPW_NCF_VALID)
           { g_ncf_has=true; g_ncf_id=f[3]; g_ncf_reference_tf=g_ncf_saved.reference_tf;
             g_ncf_selected_source=g_ncf_saved.source_name; g_ncf_original_mask=g_ncf_saved.timeframes;
             g_ncf_source_created=g_ncf_saved.source_created;
             JPWNCFSyncPause(g_ncf_sync); g_ncf_notice="Revisão retomada; confira a origem e Retomar. Nome não comprova identidade."; }
         else g_ncf_notice="Registro não retomado: "+reason;
        }
      else g_ncf_notice="Contexto do gráfico diferente ou inválido; nenhuma reconexão presumida.";
     }
   JPWNCFInvalidateMeasures(); JPWNCFReloadCatalog(); JPWNCFReloadRecords();
   ChartSetInteger(0,CHART_EVENT_MOUSE_MOVE,true); ChartSetInteger(0,CHART_EVENT_OBJECT_DELETE,true);
   ChartSetInteger(0,CHART_EVENT_OBJECT_CREATE,true); ChartSetInteger(0,CHART_EVENT_MOUSE_WHEEL,true);
  }
void JPWNCFShutdown()
  {
   JPWNCFRestoreOriginalVisibility();
   if(g_ncf_restore_source!="") Print("GENETRIX: ",g_ncf_restore_reason," Confira a origem; ao remover o indicador não há timer para retentar.");
   if(g_ncf_clone!="") ObjectDelete(0,g_ncf_clone);
   JPWUIRelease(g_nocuda_prefix); JPWNoCudaFiboUIClear(g_nocuda_prefix);
  }
void JPWNCFTimer()
  {
   if(g_ncf_restore_requested) JPWNCFRestoreOriginalVisibility();
   if(!JPWNCFContextCurrent()) { JPWNCFDraw(); return; }
   if(g_ncf_ui.open) JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui);
   JPWNCFQuote();
   if(g_ncf_import) { JPWNCFDraw(); return; }
   if(g_ncf_link && g_ncf_sync.armed)
     {
      if(ObjectFind(0,g_ncf_selected_source)<0 || ObjectGetInteger(0,g_ncf_selected_source,OBJPROP_CREATETIME)!=g_ncf_source_created)
         JPWNCFDetach("Origem excluída, renomeada ou substituída; confirme novo vínculo explicitamente.");
      else if((int)_Period==g_ncf_reference_tf)
        {
         JPWNCFSnapshot properties,captured; string reason="";
         JPWNCFStatus quick=JPWNCFReadObject(0,g_ncf_selected_source,g_ncf_reference_tf,g_nocuda_symbol,g_nocuda_feed,properties,reason);
         JPWNCFNormalizeVisibility(properties);
         const bool due=GetTickCount64()-g_ncf_history_checked_ms>=30000;
         if(quick==JPW_NCF_VALID && JPWNCFSourceWire(properties)==g_ncf_sync.confirmed_digest && !due)
           { JPWNCFDraw(); return; }
         JPWNCFStatus status=JPWNCFCapture(0,g_ncf_selected_source,g_ncf_reference_tf,g_nocuda_symbol,g_nocuda_feed,captured,reason);
         if(!JPWNCFContextCurrent()) { JPWNCFDraw(); return; }
         if(status==JPW_NCF_VALID)
           {
            g_ncf_history_checked_ms=GetTickCount64();
            if(!JPWNCFFrozenTimelineMatches(g_ncf_saved,captured))
              { g_ncf_history_conflict=true; JPWNCFSyncPause(g_ncf_sync);
                g_ncf_notice="Histórico divergiu da sequência preservada; confira e use Conferir fonte para criar revisão explícita.";
                JPWNCFDraw(); return; }
            JPWNCFNormalizeVisibility(captured);
            const string wire=JPWNCFSourceWire(captured);
            JPWNCFSyncObserve(g_ncf_sync,wire,GetTickCount64());
            JPWNCFCopy(captured,g_ncf_preview);
            if(JPWNCFSyncReady(g_ncf_sync,GetTickCount64()))
              {
               g_ncf_sync.phase=JPW_NCF_SAVE_PENDING; JPWNCFHead next;
               if(!JPWNCFContextCurrent()) { JPWNCFDraw(); return; }
               status=JPWNCFSave(g_ncf_key,g_ncf_id,g_ncf_head.generation,captured,"Ajuste explícito do Fibonacci · gesto concluído",next,reason);
               if(status==JPW_NCF_VALID)
                 { g_ncf_head=next; JPWNCFCopy(captured,g_ncf_saved); g_ncf_original_mask=captured.timeframes; JPWNCFSyncAccept(g_ncf_sync,wire);
                   g_ncf_notice="Nova revisão confirmada; âncoras exatas e sequência temporal preservadas.";
                   g_ncf_records_dirty=true; JPWNCFInvalidateMeasures(); JPWNCFPaint(); }
               else if(status==JPW_NCF_BUSY || status==JPW_NCF_IO_ERROR)
                  g_ncf_notice="Gravação pendente: "+reason;
               else { JPWNCFSyncPause(g_ncf_sync); g_ncf_sync.phase=JPW_NCF_SYNC_CONFLICT; g_ncf_notice="Gravação recusada: "+reason; }
              }
           }
         else { g_ncf_notice=reason; g_ncf_sync.phase=JPW_NCF_SOURCE_INVALID; }
        }
     }
   JPWNCFDraw();
  }
void JPWNCFImport()
  {
   if(!JPWNCFContextCurrent()) return;
   if(g_ncf_selected_source=="") { g_ncf_notice="Selecione explicitamente o Fibonacci no catálogo."; return; }
   JPWNCFRestoreOriginalVisibility();
   string reason="";
   if(JPWNCFCapture(0,g_ncf_selected_source,g_ncf_reference_tf,g_nocuda_symbol,g_nocuda_feed,g_ncf_preview,reason)!=JPW_NCF_VALID)
     { g_ncf_notice=reason; return; }
   if(!JPWNCFContextCurrent()) return;
   g_ncf_import_was_armed=g_ncf_sync.armed;
   g_ncf_import=true; g_ncf_notice="Confira A/B/C, 65 níveis e período escolhido antes de Vincular. Não há ajuste ao Close.";
   g_ncf_ui.record_detail="";
   for(int i=0;i<3;i++) g_ncf_ui.record_detail+=(i==0 ? "" : " | ")+TimeToString((datetime)g_ncf_preview.anchor_time[i],TIME_DATE|TIME_SECONDS)+" = "+DoubleToString(g_ncf_preview.anchor_price[i],16);
  }
void JPWNCFConfirmImport()
  {
   if(!JPWNCFContextCurrent()) return;
   if(!g_ncf_import) return;
   JPWNCFSnapshot verify; string reason="";
   if(JPWNCFCapture(0,g_ncf_selected_source,g_ncf_reference_tf,g_nocuda_symbol,g_nocuda_feed,verify,reason)!=JPW_NCF_VALID ||
      JPWNCFSourceWire(verify)!=JPWNCFSourceWire(g_ncf_preview) || verify.source_created!=g_ncf_preview.source_created ||
      !JPWNCFFrozenTimelineMatches(g_ncf_preview,verify))
     { g_ncf_notice="A prévia mudou; importe e confira novamente. "+reason; g_ncf_import=false; return; }
   string id="";
   if(!JPWNCFNewStudyId(g_ncf_key,g_nocuda_symbol,(long)TimeGMT(),(long)GetMicrosecondCount(),id)) return;
   if(!JPWNCFContextCurrent()) return;
   JPWNCFHead head; const JPWNCFStatus status=JPWNCFSave(g_ncf_key,id,0,verify,g_ncf_ui.justification,head,reason);
   if(status!=JPW_NCF_VALID) { g_ncf_notice="Vínculo não gravado: "+reason; return; }
   g_ncf_record_revision=0; g_ncf_history_conflict=false;
   g_ncf_catalog_all=false; g_ncf_catalog_offset=0;
   g_ncf_id=id; g_ncf_head=head; g_ncf_has=true; g_ncf_import=false; g_ncf_link=true;
   JPWNCFCopy(verify,g_ncf_saved); g_ncf_source_created=verify.source_created; g_ncf_original_mask=verify.timeframes;
   g_ncf_sync.armed=true; JPWNCFSyncAccept(g_ncf_sync,JPWNCFSourceWire(verify));
   JPWNCFRememberStudy(); JPWNCFReloadRecords(); JPWNCFInvalidateMeasures();
  }
void JPWNCFAction(const string action)
  {
   if(!JPWNCFContextCurrent()) return;
   JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui);
   if(JPWNoCudaFiboUIActions(action)) { if(action=="FC_SETTINGS_APPLY") JPWNCFPaint(); return; }
   if(action=="FC_OPEN")
     { if(!g_ncf_mode) JPWNoCudaReadJustification();
       if(!JPWUIAcquire(g_nocuda_prefix)) return; g_ncf_mode=true; g_ncf_ui.open=true; g_nocuda_panel_open=false;
       JPWNoCudaUIClear(g_nocuda_prefix); if(g_nocuda_canvas_ready) {g_nocuda_canvas.Destroy();g_nocuda_canvas_ready=false;}
       JPWNCFReloadCatalog(); JPWNCFReloadRecords(); JPWNCFPaint(); }
   else if(action=="FC_CLOSE" || action=="FC_MINIMIZE") { g_ncf_ui.open=false; JPWUIRelease(g_nocuda_prefix); }
   else if(StringFind(action,"FC_TAB_")==0)
     { g_ncf_ui.tab=(int)StringToInteger(StringSubstr(action,7));
       if(g_ncf_ui.tab==3) JPWNCFReloadRecords(); }
   else if(StringFind(action,"FC_SOURCE_")==0 && action!="FC_SOURCE_HIDE" && action!="FC_SOURCE_SHOW")
     { const string selected=JPWNoCudaFiboUIActionID(action);
       if(selected=="") return;
       if(selected!=g_ncf_selected_source && (g_ncf_link || g_ncf_hidden)) JPWNCFDetach("Escolha de outra origem exige novo vínculo explícito.");
       g_ncf_selected_source=selected;
       if(g_ncf_restore_source!=selected) g_ncf_hidden=false;
       g_ncf_import=false; JPWNCFReloadCatalog(); }
   else if(action=="FC_REFERENCE_TF")
     { if(g_ncf_link) { g_ncf_notice="Desvincule antes de mudar o período da referência."; return; }
       const int tf[6]={PERIOD_M15,PERIOD_M30,PERIOD_H1,PERIOD_H4,PERIOD_D1,PERIOD_W1}; int at=0;
       for(int i=0;i<6;i++) if(tf[i]==g_ncf_reference_tf) at=i;
       g_ncf_reference_tf=tf[(at+1)%6]; g_ncf_import=false; }
   else if(action=="FC_IMPORT") JPWNCFImport();
   else if(action=="FC_CONFIRM_IMPORT") JPWNCFConfirmImport();
   else if(action=="FC_IMPORT_CANCEL")
     { g_ncf_import=false; g_ncf_sync.armed=g_ncf_import_was_armed && g_ncf_link;
       g_ncf_notice="Importação cancelada; revisão anterior preservada."; }
   else if(action=="FC_MANUAL")
     { g_ncf_mode=false; g_ncf_ui.open=false; g_nocuda_panel_open=true; g_nocuda_panel_focus=true;
       JPWNCFRestoreOriginalVisibility(); JPWNCFSyncPause(g_ncf_sync);
       if(g_ncf_clone!="") ObjectDelete(0,g_ncf_clone); JPWNoCudaFiboUIClear(g_nocuda_prefix); }
   else if(action=="FC_UNLINK") JPWNCFDetach("Vínculo interrompido por escolha explícita. Revisões preservadas.");
   else if(action=="FC_SYNC_PAUSE" && g_ncf_has)
     {
      // The user pauses this session even if the durable checkpoint is busy.
      JPWNCFSyncPause(g_ncf_sync); g_ncf_import_was_armed=false;
      JPWNCFHead next; string reason="";
      if(!JPWNCFContextCurrent()) return;
      const JPWNCFStatus status=JPWNCFSetPaused(g_ncf_key,g_ncf_id,g_ncf_head.generation,true,next,reason);
      if(status==JPW_NCF_VALID)
        { g_ncf_head=next; g_ncf_notice="Acompanhamento pausado; estado gravado. Use Retomar para acompanhar novamente."; }
      else g_ncf_notice="Pausado nesta sessão; gravação da pausa não confirmada"+
         (reason=="" ? ". Banco ocupado ou indisponível." : ": "+reason)+
         " Repetir Pausar tenta gravar; Retomar exige ação explícita.";
     }
   else if((action=="FC_SYNC_RESUME" || action=="FC_REFRESH_SOURCE") && g_ncf_has)
     {
      // Refresh verifies the source without overriding the user's local pause,
      // including a pause whose durable checkpoint previously failed.
      const bool follow=(action=="FC_SYNC_RESUME" || g_ncf_sync.armed);
      JPWNCFSnapshot captured; string reason="";
      if(g_ncf_selected_source!=g_ncf_saved.source_name ||
         JPWNCFCapture(0,g_ncf_saved.source_name,g_ncf_saved.reference_tf,g_nocuda_symbol,g_nocuda_feed,captured,reason)!=JPW_NCF_VALID ||
         captured.source_created!=g_ncf_saved.source_created)
         { g_ncf_notice="Origem não confirmada; use novo vínculo. "+reason; return; }
      JPWNCFNormalizeVisibility(captured);
      if(!JPWNCFContextCurrent()) return;
      JPWNCFHead next;
      if(g_ncf_history_conflict)
        {
         if(action!="FC_REFRESH_SOURCE") { g_ncf_notice="Histórico alterado: use Conferir fonte e justifique a revisão."; return; }
         if(JPWNCFSave(g_ncf_key,g_ncf_id,g_ncf_head.generation,captured,g_ncf_ui.justification,next,reason)!=JPW_NCF_VALID)
            { g_ncf_notice="Revisão explícita recusada: "+reason; return; }
         g_ncf_head=next; JPWNCFCopy(captured,g_ncf_saved); g_ncf_history_conflict=false;
         g_ncf_original_mask=captured.timeframes;
         JPWNCFSyncAccept(g_ncf_sync,JPWNCFSourceWire(captured)); JPWNCFReloadRecords();
        }
      if(!JPWNCFContextCurrent()) return;
      if(JPWNCFSetPaused(g_ncf_key,g_ncf_id,g_ncf_head.generation,!follow,next,reason)!=JPW_NCF_VALID) { g_ncf_notice=reason; return; }
      g_ncf_head=next; g_ncf_link=true;
      if(follow)
        {
         g_ncf_sync.armed=true;
         JPWNCFSyncObserve(g_ncf_sync,JPWNCFSourceWire(captured),GetTickCount64());
         JPWNCFSyncFinished(g_ncf_sync,GetTickCount64(),JPWNCFSourceWire(captured));
         g_ncf_notice="Origem conferida; mudança será estabilizada antes de gravar.";
        }
      else
        { JPWNCFSyncPause(g_ncf_sync); g_ncf_import_was_armed=false;
          g_ncf_notice="Origem conferida; acompanhamento permanece pausado. Use Retomar para acompanhar novamente."; }
     }
   else if((action=="FC_SOURCE_HIDE" || action=="FC_SOURCE_SHOW") && g_ncf_link)
     {
      const bool hide=action=="FC_SOURCE_HIDE";
      if(ObjectGetInteger(0,g_ncf_selected_source,OBJPROP_CREATETIME)!=g_ncf_source_created)
         { JPWNCFDetach("Origem substituída; comando recusado."); return; }
      if(!hide) JPWNCFRestoreOriginalVisibility();
      else
        {
         if(g_ncf_restore_source!="" && (g_ncf_restore_requested ||
            g_ncf_restore_source!=g_ncf_selected_source || g_ncf_restore_created!=g_ncf_source_created))
           { g_ncf_notice="Restauração anterior pendente; confira a origem antes de ocultar outra."; return; }
         g_ncf_restore_source=g_ncf_selected_source; g_ncf_restore_created=g_ncf_source_created;
         g_ncf_restore_mask=g_ncf_original_mask;
         const bool sent=ObjectSetInteger(0,g_ncf_selected_source,OBJPROP_TIMEFRAMES,OBJ_NO_PERIODS);
         long mask=0; const bool read=ObjectGetInteger(0,g_ncf_selected_source,OBJPROP_TIMEFRAMES,0,mask);
         g_ncf_hidden=(sent && read && mask==OBJ_NO_PERIODS);
         if(!g_ncf_hidden)
           { g_ncf_restore_requested=true; g_ncf_restore_reason="Ocultação não confirmada; visibilidade original será conferida novamente."; }
        }
      JPWNCFPaint();
     }
   else if(action=="FC_LEVEL_APPLY")
     {
      double raw=0; const bool parsed=JPWNCFParseRawLevel(g_ncf_ui.selected_value,raw);
      bool found=false;
      if(g_ncf_has && parsed) for(int i=0;i<65;i++) if(MathAbs(g_ncf_saved.levels[i].value-raw)<1e-12)
         { g_ncf_level=i; g_ncf_selected_raw=raw; found=true; break; }
      g_ncf_notice=found ? "Nível escolhido; descrição visual preservada separadamente." : "Escolha um dos 65 níveis exatos, de −4 a +4.";
      JPWNCFInvalidateMeasures();
     }
   else if(StringFind(action,"FC_USE_")==0)
      g_ncf_notice="Vizinhos indisponíveis até paridade nativa; selecione o nível bruto para consultar o registro.";
   else if(action=="FC_QUERY_DAY" || action=="FC_SHOW_REFERENCES" || action=="FC_SAVE_PROJECTION")
      g_ncf_notice="UNVERIFIED_NATIVE: consulta e marcas recusadas até prova da correspondência numérica no MT5 isolado.";
   else if(action=="FC_RECORD_NEXT" || action=="FC_RECORD_PREV")
     { if(action=="FC_RECORD_PREV") g_ncf_catalog_offset=MathMax(0,g_ncf_catalog_offset-20);
       else if(g_ncf_catalog_more) g_ncf_catalog_offset+=20;
       JPWNCFReloadRecords(); }
   else if(action=="FC_RECORD_STUDIES" || action=="FC_RECORD_VERSIONS")
     { g_ncf_catalog_all=(action=="FC_RECORD_STUDIES"); g_ncf_catalog_offset=0; JPWNCFReloadRecords(); }
   else if(action=="FC_RECORD_REFRESH") JPWNCFReloadRecords();
   else if(StringFind(action,"FC_RECORD_")==0)
     {
      const string id=JPWNoCudaFiboUIActionID(action); string reason="";
      if(StringFind(id,"study:")==0)
        {
         JPWNCFHead h; JPWNCFSnapshot s;
         if(JPWNCFLoadHead(g_ncf_key,StringSubstr(id,6),h,s,reason)==JPW_NCF_VALID)
           { JPWNCFRestoreOriginalVisibility(); g_ncf_record_revision=0; g_ncf_import=false; g_ncf_history_conflict=false;
             g_ncf_id=StringSubstr(id,6); g_ncf_head=h; g_ncf_catalog_all=false; g_ncf_catalog_offset=0; JPWNCFCopy(s,g_ncf_saved); g_ncf_has=true;
             g_ncf_selected_source=s.source_name; g_ncf_reference_tf=s.reference_tf; g_ncf_source_created=s.source_created;
             g_ncf_original_mask=s.timeframes; JPWNCFDetach("Estudo consultado; nenhuma reconexão presumida."); JPWNCFRememberStudy(); JPWNCFReloadRecords(); JPWNCFInvalidateMeasures(); }
         else g_ncf_notice=reason;
        }
      else if(StringFind(id,"note:")==0)
        {
         JPWNCFNoteRow note;
         if(JPWNCFLoadNote(g_ncf_key,g_ncf_id,StringSubstr(id,5),note,reason)==JPW_NCF_VALID)
           {
            int cursor=0; string comment="",when="",op="",hi="",lo="",cl="",raw="";
            if(!JPWNCFTake(note.payload,cursor,comment) || !JPWNCFTake(note.payload,cursor,when) ||
               !JPWNCFTake(note.payload,cursor,op) || !JPWNCFTake(note.payload,cursor,hi) ||
               !JPWNCFTake(note.payload,cursor,lo) || !JPWNCFTake(note.payload,cursor,cl) || !JPWNCFTake(note.payload,cursor,raw))
               { g_ncf_notice="Observação incompatível; registro preservado."; return; }
            g_ncf_ui.record_detail=comment+" · "+TimeToString((datetime)StringToInteger(when),TIME_DATE|TIME_SECONDS)+
               " (servidor) · O "+op+" H "+hi+" L "+lo+" C "+cl+" · nível "+raw+" · distância UNVERIFIED_NATIVE.";
           }
         else g_ncf_notice=reason;
        }
      else if(StringFind(id,"revision:")==0)
        { g_ncf_record_revision=(int)StringToInteger(StringSubstr(id,9)); JPWNCFSnapshot s;
          if(JPWNCFLoadRevision(g_ncf_key,g_ncf_id,g_ncf_record_revision,s,reason)==JPW_NCF_VALID)
            g_ncf_ui.record_detail="Versão "+IntegerToString(g_ncf_record_revision)+" · "+s.source_name+" · "+IntegerToString(ArraySize(s.opens))+" aberturas preservadas";
          else g_ncf_notice=reason; }
     }
   else if(action=="FC_RESTORE_RECORD" && g_ncf_has && g_ncf_record_revision>0)
     { string reason=""; JPWNCFHead h; JPWNCFSnapshot target;
      if(JPWNCFLoadRevision(g_ncf_key,g_ncf_id,g_ncf_record_revision,target,reason)!=JPW_NCF_VALID)
          { g_ncf_notice="Revisão alvo indisponível: "+reason; return; }
       if(!JPWNCFContextCurrent()) return;
       if(JPWNCFRollback(g_ncf_key,g_ncf_id,g_ncf_head.generation,g_ncf_record_revision,h,reason)==JPW_NCF_VALID)
         { JPWNCFRestoreOriginalVisibility(); g_ncf_head=h; JPWNCFCopy(target,g_ncf_saved);
           g_ncf_reference_tf=target.reference_tf; g_ncf_original_mask=target.timeframes;
           g_ncf_selected_source=target.source_name; g_ncf_source_created=target.source_created;
           g_ncf_link=false; g_ncf_record_revision=0; JPWNCFSyncPause(g_ncf_sync); JPWNCFReloadRecords(); JPWNCFInvalidateMeasures(); JPWNCFPaint();
           g_ncf_notice="Restauração registrada em nova revisão; acompanhamento pausado."; }
       else g_ncf_notice=reason; }
   else if(action=="FC_TOUCH_NEW")
     { g_ncf_ui.tab=3; g_ncf_observation_ready=false; g_ncf_ui.observation_time="";
       g_ncf_notice="Informe abertura exata do candle encerrado no horário do servidor e comentário; consulta manual, sem certificação de toque."; }
   else if(action=="FC_TOUCH_CANCEL")
     { g_ncf_observation_ready=false; g_ncf_ui.observation_note=""; g_ncf_ui.record_detail="Observação cancelada; revisões preservadas."; }
   else if(action=="FC_TOUCH_SAVE" && g_ncf_has)
     {
      if(g_ncf_import || g_ncf_history_conflict || g_ncf_sync.phase==JPW_NCF_EDITING_PREVIEW || g_ncf_sync.phase==JPW_NCF_SAVE_PENDING)
         { g_ncf_notice="Conclua ou cancele a revisão antes de registrar a observação."; return; }
      const datetime when=StringToTime(g_ncf_ui.observation_time); const ENUM_TIMEFRAMES tf=(ENUM_TIMEFRAMES)g_ncf_saved.reference_tf;
      const int shift=iBarShift(g_nocuda_symbol,tf,when,true); MqlRates rates[]; ArraySetAsSeries(rates,false);
      if(when<=0 || shift<1 || CopyRates(g_nocuda_symbol,tf,shift,1,rates)!=1 || rates[0].time!=when ||
         StringLen(g_ncf_ui.observation_note)<1)
         { g_ncf_notice="Informe abertura exata de candle encerrado e comentário não vazio."; return; }
      const string payload=JPWNCFFrame(g_ncf_ui.observation_note)+JPWNCFFrame(IntegerToString((long)when))+
         JPWNCFFrame(DoubleToString(rates[0].open,16))+JPWNCFFrame(DoubleToString(rates[0].high,16))+
         JPWNCFFrame(DoubleToString(rates[0].low,16))+JPWNCFFrame(DoubleToString(rates[0].close,16))+
         JPWNCFFrame(DoubleToString(g_ncf_saved.levels[g_ncf_level].value,3))+JPWNCFFrame("UNVERIFIED_NATIVE · distância indisponível");
      string note="",reason="";
      if(!JPWNCFContextCurrent()) return;
      const JPWNCFStatus result=JPWNCFSaveNote(g_ncf_key,g_ncf_id,g_ncf_head.generation,g_ncf_head.revision,
         "observation",payload,(long)TimeGMT(),note,reason);
      if(result==JPW_NCF_VALID) JPWNCFReloadRecords();
      g_ncf_notice=(result==JPW_NCF_VALID ? "Observação manual gravada · "+StringSubstr(note,0,12)+"; não certifica contato." : "Observação não gravada: "+reason);
     }
  }
bool JPWNCFHandleEvent(const int id,const long &lparam,const double &dparam,const string &sparam)
  {
   if(id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=JPWUIOwner()) return(true);
   if(id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=g_nocuda_prefix)
     { if(!g_ncf_mode) JPWNoCudaReadJustification();
       JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui); g_ncf_ui.open=false;
       g_nocuda_panel_open=false; JPWNoCudaUIClear(g_nocuda_prefix); JPWNCFDraw(); return(true); }
   if(!g_ncf_mode && !(id==CHARTEVENT_OBJECT_CLICK && sparam==JPWNoCudaFiboUIName(g_nocuda_prefix,"FC_OPEN"))) return(false);
   if(id==CHARTEVENT_OBJECT_DELETE && sparam==g_ncf_selected_source && g_ncf_link)
      JPWNCFDetach("Origem excluída ou renomeada; última revisão preservada, sem reconexão automática.");
   if((id==CHARTEVENT_OBJECT_CHANGE || id==CHARTEVENT_OBJECT_DRAG) && sparam==g_ncf_selected_source && g_ncf_link)
     {
      if((int)_Period!=g_ncf_reference_tf) { JPWNCFSyncPause(g_ncf_sync); g_ncf_notice="Alteração em outro período: volte ao período de referência e confira antes de Retomar."; }
      else
        { JPWNCFSnapshot properties; string reason="";
          if(JPWNCFReadObject(0,g_ncf_selected_source,g_ncf_reference_tf,g_nocuda_symbol,g_nocuda_feed,properties,reason)==JPW_NCF_VALID)
            { JPWNCFNormalizeVisibility(properties);
              JPWNCFSyncFinished(g_ncf_sync,GetTickCount64(),JPWNCFSourceWire(properties)); }
          else { g_ncf_notice=reason; g_ncf_sync.finish_requested=false; } }
     }
   if(id==CHARTEVENT_MOUSE_WHEEL && g_ncf_ui.open && JPWUIOwns(g_nocuda_prefix))
     {
      const int x=(int)(short)lparam,y=(int)(short)(lparam>>16);
      if(x>=g_fc_layout.x && x<g_fc_layout.x+g_fc_layout.width && y>=g_fc_layout.body_y && y<g_fc_layout.footer_y)
        { JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui); JPWNoCudaFiboUIScroll(dparam>0 ? -3 : 3); JPWNCFDraw(); return(true); }
     }
   if(id==CHARTEVENT_MOUSE_MOVE) g_ncf_sync.mouse_down=(((int)StringToInteger(sparam)&1)!=0);
   if(id==CHARTEVENT_MOUSE_MOVE || id==CHARTEVENT_OBJECT_CLICK)
      JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui);
   if(JPWNoCudaFiboUIHandleGeometry(g_nocuda_prefix,id,lparam,dparam,sparam)) { JPWNCFDraw(); return(true); }
   if(id==CHARTEVENT_OBJECT_ENDEDIT && StringFind(sparam,g_nocuda_prefix+"FC_")==0)
     { JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui);
       if(g_fc_editing==sparam) g_fc_editing=""; return(true); }
   if(id==CHARTEVENT_OBJECT_CLICK)
     {
      const string action=JPWNoCudaFiboUIHitAction(g_nocuda_prefix,sparam);
      if(action!="")
        { g_fc_focus=sparam; g_fc_editing=(ObjectGetInteger(0,sparam,OBJPROP_TYPE)==OBJ_EDIT ? sparam : "");
          JPWNCFAction(action);
          if(g_ncf_mode) JPWNCFDraw(); else { JPWNoCudaPaint(); JPWNoCudaDrawUI(); }
          return(true); }
      g_fc_editing=""; g_fc_focus=""; return(true);
     }
   if(id==CHARTEVENT_KEYDOWN && g_ncf_ui.open && JPWUIOwns(g_nocuda_prefix))
     {
      if(lparam==9) { JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui);
         if(g_fc_editing!="" && ObjectFind(0,g_fc_editing)>=0)
            ObjectSetInteger(0,g_fc_editing,OBJPROP_SELECTED,false);
         g_fc_focus=JPWNoCudaFiboUIFocusCycle(g_fc_focus,((int)TerminalInfoInteger(TERMINAL_KEYSTATE_SHIFT)&0x8000)!=0);
         g_fc_editing=(g_fc_focus!="" && ObjectFind(0,g_fc_focus)>=0 &&
            ObjectGetInteger(0,g_fc_focus,OBJPROP_TYPE)==OBJ_EDIT ? g_fc_focus : "");
         if(g_fc_editing!="") ObjectSetInteger(0,g_fc_editing,OBJPROP_SELECTED,true);
         JPWNCFDraw(); }
      else if(lparam==27) { JPWNCFAction("FC_CLOSE"); JPWNCFDraw(); }
      else if(lparam==13 && g_fc_editing=="" && ObjectFind(0,g_fc_focus)>=0 &&
         ObjectGetInteger(0,g_fc_focus,OBJPROP_TYPE)==OBJ_BUTTON) { JPWNCFAction(JPWNoCudaFiboUIHitAction(g_nocuda_prefix,g_fc_focus)); JPWNCFDraw(); }
      return(true);
     }
   if(id==CHARTEVENT_CHART_CHANGE) { JPWNoCudaFiboUIFieldCapture(g_nocuda_prefix,g_ncf_ui); JPWNCFPaint(); JPWNCFDraw(); }
   return(true);
  }
#endif

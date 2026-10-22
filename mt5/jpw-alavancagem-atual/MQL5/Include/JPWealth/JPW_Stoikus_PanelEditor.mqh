#ifndef JPW_STOIKUS_PANEL_EDITOR_MQH
#define JPW_STOIKUS_PANEL_EDITOR_MQH
// Included after HUD painting helpers and the pure preference/visual modules.
// Chart-local presentation only; previous preference objects are read-only.
void JPWAccountMinimize();
JPWStoikusPanelPrefs g_stoikus_panel_prefs,g_stoikus_panel_draft;
bool g_stoikus_panel_editor=false,g_stoikus_panel_loaded=false,g_stoikus_panel_pending=false;
bool g_stoikus_panel_invalid=false,g_stoikus_panel_stale=false,g_stoikus_panel_reset_pending=false;
string g_stoikus_panel_notice="";
int g_stoikus_panel_focus=-1,g_stoikus_panel_legacy_mask=127;
int g_stoikus_panel_page=0,g_stoikus_panel_page_rows=7,g_stoikus_panel_transparency_draft=30;
string g_stoikus_panel_seen_text[5];
long g_stoikus_panel_seen_kind[5];

string JPWStoikusPanelWatchName(const int index)
  {
   if(index==0) return(JPW_STOIKUS_PANEL_PREF_OBJECT);
   if(index==1) return(JPW_COCKPIT_PREF_OBJECT);
   if(index==2) return(JPW_COCKPIT_PREF_V2_OBJECT);
   if(index==3) return(JPW_COCKPIT_PREF_LEGACY_OBJECT);
   return(JPW_STOIKUS_VISUAL_OBJECT);
  }
long JPWStoikusPanelKind(const string name)
  { return(ObjectFind(0,name)<0 ? -1 : ObjectGetInteger(0,name,OBJPROP_TYPE)); }
string JPWStoikusPanelText(const string name)
  { return(ObjectFind(0,name)<0 ? "" : ObjectGetString(0,name,OBJPROP_TEXT)); }
void JPWStoikusPanelObserve()
  {
   for(int i=0;i<5;i++)
     { string name=JPWStoikusPanelWatchName(i); g_stoikus_panel_seen_kind[i]=JPWStoikusPanelKind(name); g_stoikus_panel_seen_text[i]=JPWStoikusPanelText(name); }
  }
bool JPWStoikusPanelObservationMatches()
  {
   for(int i=0;i<5;i++)
     { string name=JPWStoikusPanelWatchName(i); if(g_stoikus_panel_seen_kind[i]!=JPWStoikusPanelKind(name) || g_stoikus_panel_seen_text[i]!=JPWStoikusPanelText(name)) return(false); }
   return(true);
  }
// Decode the observed chart objects into local values. Runtime globals may
// still describe the previous template and must never be used as the oracle.
bool JPWStoikusPanelLegacyProjection(JPWStoikusPanelPrefs &p)
  {
   JPWCockpitPrefs legacy;JPWCockpitDefault(legacy);
   JPWStoikusVisual visual;JPWStoikusVisualDefault(visual);
   bool present=false,valid=true;
   for(int i=1;i<=3;i++) if(g_stoikus_panel_seen_kind[i]>=0)
     {
      present=true;
      if(g_stoikus_panel_seen_kind[i]!=OBJ_LABEL || !JPWCockpitDecode(g_stoikus_panel_seen_text[i],legacy)) valid=false;
      break; // V3, then V2, then V1; an invalid newer object is not bypassed.
     }
   if(g_stoikus_panel_seen_kind[4]>=0)
     {
      present=true;
      if(g_stoikus_panel_seen_kind[4]!=OBJ_LABEL || !JPWStoikusVisualDecode(g_stoikus_panel_seen_text[4],visual)) valid=false;
     }
   g_stoikus_panel_legacy_mask=legacy.visible_mask;
   if(present) JPWStoikusPanelPrefsLegacy(visual.mode,legacy.visible_mask,p);
   return(valid);
  }
void JPWStoikusPanelLoad()
  {
   // A load request cannot silently accept a new baseline during an edit.
   if(g_stoikus_panel_editor || g_stoikus_panel_pending)
     { if(!JPWStoikusPanelObservationMatches()) { g_stoikus_panel_stale=true;g_stoikus_panel_notice="Modelo alterado. Cancele e reabra antes de aplicar."; }return; }
   JPWStoikusPanelPrefsDefault(g_stoikus_panel_prefs);
   g_stoikus_panel_invalid=false;g_stoikus_panel_stale=false;g_stoikus_panel_reset_pending=false;g_stoikus_panel_notice="";
   JPWStoikusPanelObserve();g_stoikus_panel_loaded=true;
   const bool legacy_valid=JPWStoikusPanelLegacyProjection(g_stoikus_panel_prefs);
   if(g_stoikus_panel_seen_kind[0]<0)
     { if(!legacy_valid) { g_stoikus_panel_invalid=true;g_stoikus_panel_notice="Preferência anterior inválida preservada; prévia temporária. Use Padrão e Aplicar após conferir."; }return; }
   if(g_stoikus_panel_seen_kind[0]!=OBJ_LABEL || !JPWStoikusPanelPrefsDecode(g_stoikus_panel_seen_text[0],g_stoikus_panel_prefs))
     { g_stoikus_panel_invalid=true;g_stoikus_panel_notice="Preferência incompatível preservada. Confira ou use Padrão e Aplicar."; }
  }
void JPWStoikusPanelRecheck()
  {
   if(!g_stoikus_panel_loaded) { JPWStoikusPanelLoad();return; }
   if(JPWStoikusPanelObservationMatches()) return;
   if(g_stoikus_panel_editor || g_stoikus_panel_pending)
     { g_stoikus_panel_stale=true;g_stoikus_panel_notice="Modelo alterado. Cancele e reabra para conferir antes de aplicar."; }
   else JPWStoikusPanelLoad();
  }
int JPWStoikusPanelTransparency()
  { return(g_stoikus_panel_editor ? g_stoikus_panel_transparency_draft : g_stoikus_visual.transparency); }
void JPWStoikusPanelEditorCancel()
  {
   const bool was_editor=g_stoikus_panel_editor;
   g_stoikus_panel_editor=false;g_stoikus_panel_pending=false;g_stoikus_panel_reset_pending=false;
   if(was_editor) JPWUIRelease(g_panel_prefix);
   g_stoikus_panel_draft=g_stoikus_panel_prefs;g_stoikus_panel_transparency_draft=g_stoikus_visual.transparency;
   if(g_stoikus_panel_loaded) JPWStoikusPanelRecheck();
  }
void JPWStoikusPanelEditorOpen()
  {
   if(g_stoikus_panel_editor) return;
   const bool resume=g_stoikus_panel_pending;
   const bool stale_resume=resume && (g_stoikus_panel_stale || !JPWStoikusPanelObservationMatches());
   if(stale_resume)
     { g_stoikus_panel_stale=true;g_stoikus_panel_notice="Modelo alterado. Cancele o rascunho suspenso e reabra para conferir."; }
   if(!resume) JPWStoikusPanelLoad();
   if(g_raiz_details_open) JPWAccountMinimize();
   // Account minimize may explicitly update its own visual preference.
   // A stale resumed draft keeps its old baseline and opens only for recovery.
   if(!stale_resume) JPWStoikusPanelObserve();
   if(!JPWUIAcquire(g_panel_prefix)) { g_stoikus_panel_notice="Personalização indisponível: foco não adquirido.";return; }
   if(!resume)
     { g_stoikus_panel_draft=g_stoikus_panel_prefs;g_stoikus_panel_transparency_draft=g_stoikus_visual.transparency;g_stoikus_panel_page=0;g_stoikus_panel_focus=-1; }
   g_stoikus_panel_pending=false;g_stoikus_panel_editor=true;
  }
bool JPWStoikusPanelRestoreObject(const bool existed,const string previous,const string written)
  {
   const string name=JPW_STOIKUS_PANEL_PREF_OBJECT;
   if(JPWStoikusPanelKind(name)!=OBJ_LABEL || JPWStoikusPanelText(name)!=written) return(false);
   if(existed) return(ObjectSetString(0,name,OBJPROP_TEXT,previous) && JPWStoikusPanelText(name)==previous);
   return(ObjectDelete(0,name) && ObjectFind(0,name)<0);
  }
bool JPWStoikusPanelSave(const JPWStoikusPanelPrefs &candidate)
  {
   const string encoded=JPWStoikusPanelPrefsEncode(candidate);if(encoded=="") return(false);
   if(!g_stoikus_panel_loaded) JPWStoikusPanelLoad();
   if(g_stoikus_panel_stale || !JPWStoikusPanelObservationMatches())
     { g_stoikus_panel_notice="Modelo alterado. Cancele e reabra antes de aplicar.";return(false); }
   const string name=JPW_STOIKUS_PANEL_PREF_OBJECT;const bool existed=ObjectFind(0,name)>=0;
   const string previous=JPWStoikusPanelText(name);
   if((existed && JPWStoikusPanelKind(name)!=OBJ_LABEL) || (g_stoikus_panel_invalid && !g_stoikus_panel_reset_pending))
     { g_stoikus_panel_notice="Preferência incompatível preservada. Use Padrão para restaurar; objeto de outro tipo exige conferência manual.";return(false); }
   if(!existed && !ObjectCreate(0,name,OBJ_LABEL,0,0,0))
     { g_stoikus_panel_notice="Não foi possível criar a preferência. Rascunho preservado.";return(false); }
   bool ok=ObjectSetInteger(0,name,OBJPROP_XDISTANCE,100000) && ObjectSetInteger(0,name,OBJPROP_YDISTANCE,100000) &&
      ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) && ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
      ObjectSetString(0,name,OBJPROP_TEXT,encoded) && JPWStoikusPanelText(name)==encoded;
   if(!ok)
     {
      bool rolled=existed ? (ObjectSetString(0,name,OBJPROP_TEXT,previous) && JPWStoikusPanelText(name)==previous) :
         (ObjectDelete(0,name) && ObjectFind(0,name)<0);
      g_stoikus_panel_notice=rolled ? "Painel não salvo; preferência anterior preservada." : "Falha ao salvar e restaurar painel. Confira o objeto do gráfico.";
      if(!rolled) g_stoikus_panel_stale=true;
      return(false);
     }
   g_stoikus_panel_prefs=candidate;g_stoikus_panel_invalid=false;g_stoikus_panel_reset_pending=false;g_stoikus_panel_notice="";
   JPWStoikusPanelObserve();return(true);
  }
bool JPWStoikusPanelEditorApply()
  {
   JPWStoikusPanelRecheck();if(g_stoikus_panel_stale) return(false);
   const bool existed=g_stoikus_panel_seen_kind[0]>=0;
   const string previous=g_stoikus_panel_seen_text[0];
   const JPWStoikusPanelPrefs previous_prefs=g_stoikus_panel_prefs;
   const bool was_invalid=g_stoikus_panel_invalid,was_reset=g_stoikus_panel_reset_pending;
   const bool opacity_changed=g_stoikus_panel_transparency_draft!=g_stoikus_visual.transparency;
   if(opacity_changed && (g_stoikus_visual_invalid || JPWStoikusPanelKind(JPW_STOIKUS_VISUAL_OBJECT)!=g_stoikus_visual_seen_type ||
      JPWStoikusPanelText(JPW_STOIKUS_VISUAL_OBJECT)!=g_stoikus_visual_seen))
     { g_stoikus_panel_notice="Visual alterado ou incompatível. Cancele e confira antes de aplicar.";return(false); }
   if(!JPWStoikusPanelSave(g_stoikus_panel_draft)) return(false);
   if(opacity_changed)
     {
      JPWStoikusVisual visual=g_stoikus_visual;visual.transparency=g_stoikus_panel_transparency_draft;
      if(!JPWStoikusVisualSave(visual))
        {
         bool rolled=JPWStoikusPanelRestoreObject(existed,previous,JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft));
         if(rolled) { g_stoikus_panel_prefs=previous_prefs;g_stoikus_panel_invalid=was_invalid;g_stoikus_panel_reset_pending=was_reset;JPWStoikusPanelObserve(); }
         else g_stoikus_panel_stale=true;
         g_stoikus_panel_notice=rolled ? "Transparência não salva; painel anterior restaurado. Rascunho preservado." : "Falha de restauração. Confira as preferências do gráfico antes de continuar.";
         return(false);
        }
     }
   JPWStoikusPanelObserve();g_stoikus_panel_editor=false;g_stoikus_panel_pending=false;JPWUIRelease(g_panel_prefix);g_stoikus_panel_notice="";return(true);
  }
bool JPWStoikusPanelEditorAction(const string suffix)
  {
   if(!g_stoikus_panel_editor || !JPWUIOwns(g_panel_prefix)) return(false);
   if(suffix=="CUST_BG" || suffix=="CUST_TITLE" || suffix=="CUST_NOTICE") return(true);
   if(suffix=="CUST_CANCEL") { JPWStoikusPanelEditorCancel();return(true); }
   JPWStoikusPanelRecheck();
   if(suffix=="CUST_APPLY") { JPWStoikusPanelEditorApply();return(true); }
   if(suffix=="CUST_DEFAULT")
     { JPWStoikusPanelPrefsDefault(g_stoikus_panel_draft);g_stoikus_panel_draft.visible_mask&=g_stoikus_panel_legacy_mask;g_stoikus_panel_reset_pending=true;return(true); }
   if(suffix=="CUST_OPACITY") { g_stoikus_panel_transparency_draft=(g_stoikus_panel_transparency_draft+10)%110;return(true); }
   if(suffix=="CUST_NEXT") { const int pages=(7+g_stoikus_panel_page_rows-1)/g_stoikus_panel_page_rows;g_stoikus_panel_page=MathMin(pages-1,g_stoikus_panel_page+1);return(true); }
   if(suffix=="CUST_PREV") { g_stoikus_panel_page=MathMax(0,g_stoikus_panel_page-1);return(true); }
   for(int metric=0;metric<7;metric++)
     {
      string id=IntegerToString(metric);
      if(suffix=="CUST_TOGGLE_"+id) { g_stoikus_panel_draft.visible_mask^=(1<<metric);return(true); }
      if(suffix=="CUST_UP_"+id) { JPWStoikusPanelPrefsMove(g_stoikus_panel_draft,metric,-1);return(true); }
      if(suffix=="CUST_DOWN_"+id) { JPWStoikusPanelPrefsMove(g_stoikus_panel_draft,metric,1);return(true); }
     }
   return(false);
  }
// Focus is an action in the current page, independent of financial shortcuts.
string JPWStoikusPanelFocusAt(const int index)
  {
   const int rows=MathMin(g_stoikus_panel_page_rows,7-g_stoikus_panel_page*g_stoikus_panel_page_rows);
   if(index<0 || index>=rows*3+6) return("");
   if(index<rows*3)
     {
      const int metric=g_stoikus_panel_draft.order[g_stoikus_panel_page*g_stoikus_panel_page_rows+index/3];
      const string verb=(index%3==0 ? "CUST_TOGGLE_" : (index%3==1 ? "CUST_UP_" : "CUST_DOWN_"));
      return(verb+IntegerToString(metric));
     }
   const int control=index-rows*3;
   if(control==0) return("CUST_PREV");if(control==1) return("CUST_NEXT");
   if(control==2) return("CUST_OPACITY");if(control==3) return("CUST_DEFAULT");
   return(control==4 ? "CUST_APPLY" : "CUST_CANCEL");
  }
string JPWStoikusPanelFocusLabel()
  {
   const string action=JPWStoikusPanelFocusAt(g_stoikus_panel_focus);
   if(action=="CUST_PREV") return("Página anterior");if(action=="CUST_NEXT") return("Próxima página");
   if(action=="CUST_OPACITY") return("Transparência");if(action=="CUST_DEFAULT") return("Padrão");
   if(action=="CUST_APPLY") return("Aplicar");if(action=="CUST_CANCEL") return("Cancelar");
   string titles[7]={"Alavancagem","Flutuante","SL","Raiz N 1W","Raiz N 2W","Risco stops","Compensado"};
   for(int metric=0;metric<7;metric++)
     {
      const string id=IntegerToString(metric);
      if(action=="CUST_TOGGLE_"+id) return("Selecionar "+titles[metric]);
      if(action=="CUST_UP_"+id) return("Subir "+titles[metric]);
      if(action=="CUST_DOWN_"+id) return("Descer "+titles[metric]);
     }
   return("Tab para navegar");
  }
void JPWStoikusPanelEditorRender(const int cw,const int ch,const color ink,const color fill)
  {
   if(!g_stoikus_panel_editor || !JPWUIOwns(g_panel_prefix) || cw<=0 || ch<=0) return;
   JPWStoikusPanelRecheck();
   const int pad=JPWUIDesignPx(8),gap=JPWUIDesignPx(4),row=JPWUIDesignPx(36),step=row+gap;
   if(cw<JPWUIDesignPx(240) || ch<2*pad+6*step)
     {
      JPWStoikusHUDSurfacePaint("CUST_CANCEL",0,0,cw,MathMin(ch,row),"Cancelar","",10,ink,fill,0,"Amplie o gráfico para personalizar. Cancelar preserva sua configuração.",20);
      return;
     }
   const int width=MathMin(cw-2*pad,JPWUIDesignPx(520));
   g_stoikus_panel_page_rows=MathMax(1,MathMin(7,(ch-2*pad)/step-5));
   const int pages=(7+g_stoikus_panel_page_rows-1)/g_stoikus_panel_page_rows;
   g_stoikus_panel_page=MathMin(g_stoikus_panel_page,pages-1);
   const int rows=MathMin(g_stoikus_panel_page_rows,7-g_stoikus_panel_page*g_stoikus_panel_page_rows);
   const int height=2*pad+(rows+5)*step;
   const int x=(cw-width)/2,y=(ch-height)/2,content=width-2*pad;
   JPWStoikusHUDSurfacePaint("CUST_BG",x,y,width,height,"","",10,ink,fill,0,"Personalizar painel",10);
   int yy=y+pad;
   JPWStoikusHUDCaptionPaint("CUST_TITLE",x+pad,yy,content,row,"Personalizar painel","Personalizar",ink,fill,"Rascunho: Aplicar salva; Cancelar descarta.",20);yy+=step;
   string titles[7]={"Alavancagem","Flutuante","SL","Raiz N 1W","Raiz N 2W","Risco stops","Compensado"};
   const bool roomy=content>=JPWUIDesignPx(340);
   const int arrow=JPWUIDesignPx(roomy ? 76 : 42),label=content-2*arrow-2*gap;
   for(int slot=0;slot<rows;slot++)
     {
      const int metric=g_stoikus_panel_draft.order[g_stoikus_panel_page*g_stoikus_panel_page_rows+slot];
      const string id=IntegerToString(metric),caption=((g_stoikus_panel_draft.visible_mask&(1<<metric))!=0 ? "[x] " : "[ ] ")+titles[metric];
      JPWStoikusHUDCaptionPaint("CUST_TOGGLE_"+id,x+pad,yy,label,row,caption,(g_stoikus_panel_draft.visible_mask&(1<<metric))!=0 ? "[x]" : "[ ]",ink,fill,"Selecionar ou ocultar "+titles[metric],20);
      JPWStoikusHUDSurfacePaint("CUST_UP_"+id,x+pad+label+gap,yy,arrow,row,roomy ? "Subir" : "↑","",10,ink,fill,100,"Subir "+titles[metric]+" uma posição",20);
      JPWStoikusHUDSurfacePaint("CUST_DOWN_"+id,x+pad+label+2*gap+arrow,yy,arrow,row,roomy ? "Descer" : "↓","",10,ink,fill,100,"Descer "+titles[metric]+" uma posição",20);yy+=step;
     }
   const int half=(content-gap)/2;
   JPWStoikusHUDCaptionPaint("CUST_PREV",x+pad,yy,half,row,"Anterior","←",ink,fill,"Página anterior de métricas",20);
   JPWStoikusHUDCaptionPaint("CUST_NEXT",x+pad+half+gap,yy,content-half-gap,row,"Próxima "+IntegerToString(g_stoikus_panel_page+1)+"/"+IntegerToString(pages),"→",ink,fill,"Próxima página de métricas",20);yy+=step;
   JPWStoikusHUDCaptionPaint("CUST_OPACITY",x+pad,yy,content,row,"Transparência: "+IntegerToString(g_stoikus_panel_transparency_draft)+"%","Transparência",ink,fill,"Aumentar 10%; Aplicar confirma a transparência junto com o painel.",20);yy+=step;
   const int third=(content-2*gap)/3;
   JPWStoikusHUDCaptionPaint("CUST_DEFAULT",x+pad,yy,third,row,"Padrão","Padrão",ink,fill,"Restaurar seleção e ordem sugeridas, respeitando exclusões anteriores",20);
   JPWStoikusHUDCaptionPaint("CUST_APPLY",x+pad+third+gap,yy,third,row,"Aplicar","Aplicar",ink,fill,"Salvar seleção, ordem e transparência",20);
   JPWStoikusHUDCaptionPaint("CUST_CANCEL",x+pad+2*(third+gap),yy,content-2*(third+gap),row,"Cancelar","Cancelar",ink,fill,"Descartar rascunho sem gravar preferências",20);yy+=step;
   JPWStoikusHUDCaptionPaint("CUST_NOTICE",x+pad,yy,content,row,g_stoikus_panel_notice!="" ? "Aviso · confira" : "Foco: "+JPWStoikusPanelFocusLabel(),g_stoikus_panel_notice!="" ? "Aviso" : "Foco",ink,fill,(g_stoikus_panel_notice!="" ? g_stoikus_panel_notice+" · " : "")+"Foco: "+JPWStoikusPanelFocusLabel()+". Tab/Shift-Tab navegam; Enter/Espaço acionam; Esc cancela. Nenhuma seleção também é válida.",20);
  }
bool JPWStoikusPanelEditorKey(const long key,const bool reverse)
  {
   if(!g_stoikus_panel_editor || !JPWUIOwns(g_panel_prefix)) return(false);
   if(key==27) { JPWStoikusPanelEditorCancel();return(true); }
   if(key==9)
     {
      const int rows=MathMin(g_stoikus_panel_page_rows,7-g_stoikus_panel_page*g_stoikus_panel_page_rows),count=rows*3+6;
      if(g_stoikus_panel_focus<0) g_stoikus_panel_focus=reverse ? count-1 : 0;
      else g_stoikus_panel_focus=(g_stoikus_panel_focus+(reverse ? count-1 : 1))%count;
      return(true);
     }
   if(key==13 || key==32)
     {
      if(g_stoikus_panel_focus<0) g_stoikus_panel_focus=0;
      const string action=JPWStoikusPanelFocusAt(g_stoikus_panel_focus);
      const bool handled=JPWStoikusPanelEditorAction(action);
      if(!g_stoikus_panel_editor) return(handled);
      // Follow the same metric/action even when a move crosses a page edge.
      for(int metric=0;metric<7;metric++)
        {
         const string id=IntegerToString(metric);
         int verb=-1;
         if(action=="CUST_TOGGLE_"+id) verb=0;
         else if(action=="CUST_UP_"+id) verb=1;
         else if(action=="CUST_DOWN_"+id) verb=2;
         if(verb<0) continue;
         for(int slot=0;slot<7;slot++) if(g_stoikus_panel_draft.order[slot]==metric)
           {
            g_stoikus_panel_page=slot/g_stoikus_panel_page_rows;
            g_stoikus_panel_focus=(slot%g_stoikus_panel_page_rows)*3+verb;
            return(handled);
           }
        }
      for(int i=0;i<27;i++) if(JPWStoikusPanelFocusAt(i)==action) { g_stoikus_panel_focus=i;break; }
      return(handled);
     }
   return(false);
  }
void JPWStoikusPanelEditorSuspend()
  {
   if(!g_stoikus_panel_editor) return;
   g_stoikus_panel_editor=false;g_stoikus_panel_pending=true;JPWUIRelease(g_panel_prefix);
  }
#endif

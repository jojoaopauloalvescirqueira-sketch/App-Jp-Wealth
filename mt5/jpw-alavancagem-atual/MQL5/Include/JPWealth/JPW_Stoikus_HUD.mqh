#ifndef JPW_STOIKUS_HUD_MQH
#define JPW_STOIKUS_HUD_MQH
#include <JPWealth/JPW_Stoikus_Visual.mqh>
#include <JPWealth/JPW_Stoikus_PanelPrefs.mqh>
#include <JPWealth/JPW_Stoikus_PanelBridge.mqh>
#include <JPWealth/JPW_UI_Focus.mqh>
JPWStoikusVisual g_stoikus_visual;
bool g_stoikus_visual_invalid=false,g_stoikus_options=false;
string g_stoikus_visual_notice="",g_stoikus_visual_seen="";
long g_stoikus_visual_seen_type=-1;
void JPWStoikusHUDCancel();
void JPWStoikusVisualLoad()
  {
   // End the old interaction before installing a newly observed template state.
   // Cancel can then never restore a snapshot predating the new seen payload.
   JPWStoikusHUDCancel(); g_stoikus_visual_seen_type=-1;
   JPWStoikusVisualDefault(g_stoikus_visual);
   g_stoikus_visual_invalid=false; g_stoikus_visual_notice=""; g_stoikus_visual_seen="";
   if(ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)<0) return;
   g_stoikus_visual_seen_type=ObjectGetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TYPE);
   g_stoikus_visual_seen=ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT);
   if(ObjectGetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL ||
      !JPWStoikusVisualDecode(g_stoikus_visual_seen,g_stoikus_visual))
     { g_stoikus_visual_invalid=true; g_stoikus_visual_notice="Preferência visual inválida; padrão temporário. Use Restaurar visual."; }
  }
bool JPWStoikusVisualSave(const JPWStoikusVisual &candidate,const bool restore=false)
  {
   string encoded=JPWStoikusVisualEncode(candidate); if(encoded=="") return(false);
   bool existed=ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)>=0;
   // Recheck templates before every explicit save; never overwrite unseen state.
   string previous=existed ? ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT) : "";
   if(existed && ObjectGetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL)
     { g_stoikus_visual_notice="Objeto visual de outro tipo preservado; remova-o manualmente."; return(false); }
   if(!restore && (g_stoikus_visual_invalid || previous!=g_stoikus_visual_seen))
     { JPWStoikusVisualLoad(); g_stoikus_visual_notice="Preferência visual alterada ou inválida; confira e tente novamente."; return(false); }
   if(!existed && !ObjectCreate(0,JPW_STOIKUS_VISUAL_OBJECT,OBJ_LABEL,0,0,0)) return(false);
   bool ok=ObjectSetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_XDISTANCE,100000) &&
      ObjectSetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_YDISTANCE,100000) &&
      ObjectSetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_HIDDEN,true) &&
      ObjectSetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_SELECTABLE,false) &&
      ObjectSetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT,encoded) &&
      ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)==encoded;
   if(!ok)
     {
      bool rolled=existed ? (ObjectSetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT,previous) &&
         ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT)==previous) :
         (ObjectDelete(0,JPW_STOIKUS_VISUAL_OBJECT) && ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)<0);
      g_stoikus_visual_notice=rolled ? "Visual não salvo; preferência anterior preservada." : "Falha ao salvar e restaurar visual; confira o objeto do gráfico.";
      return(false);
     }
   g_stoikus_visual=candidate; g_stoikus_visual_seen=encoded; g_stoikus_visual_seen_type=OBJ_LABEL; g_stoikus_visual_invalid=false; g_stoikus_visual_notice=""; return(true);
  }
void JPWStoikusVisualRecheck()
  {
   string text=ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)>=0 ? ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT) : "";
   long kind=ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)>=0 ? ObjectGetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TYPE) : -1;
   if(text!=g_stoikus_visual_seen || kind!=g_stoikus_visual_seen_type) JPWStoikusVisualLoad();
  }
struct JPWStoikusHUDSurface
  { string name,key; int x,y,w,h,z; bool live; };
JPWStoikusHUDSurface g_stoikus_surfaces[96];
int g_stoikus_surface_count=0;
JPWPanelRect g_stoikus_hud;
bool g_stoikus_drag=false,g_stoikus_resize=false,g_stoikus_scroll=false,g_stoikus_gesture_moved=false;
int g_stoikus_start_x=0,g_stoikus_start_y=0,g_stoikus_origin_x=0,g_stoikus_origin_y=0,g_stoikus_origin_w=0;
JPWStoikusVisual g_stoikus_gesture_before;
string g_stoikus_last_click=""; int g_stoikus_last_kind=-1; int g_stoikus_last_x=-100000,g_stoikus_last_y=-100000; ulong g_stoikus_last_time=0;
string JPWStoikusHUDResource(const string name) { return(name+"_ARGB"); }
void JPWStoikusHUDCancel()
  {
   if(g_stoikus_drag || g_stoikus_resize) ChartSetInteger(0,CHART_MOUSE_SCROLL,g_stoikus_scroll);
   if(g_stoikus_drag || g_stoikus_resize) g_stoikus_visual=g_stoikus_gesture_before;
   g_stoikus_drag=false; g_stoikus_resize=false;
  }
string JPWStoikusHUDOwnedSuffix(const int index)
  {
   if(index>=18 && index<25) return(IntegerToString(index-18)+"_META");
   if(index>=25 && index<46)
     { int slot=index-25; return(string("CUST_")+(slot%3==0 ? "TOGGLE_" : (slot%3==1 ? "UP_" : "DOWN_"))+IntegerToString(slot/3)); }
   string extra[15]={"HUD_NOCUDA","HUD_PERSONALIZE","HUD_PREVIOUS","HUD_NEXT","HUD_PAGE",
      "CUST_BG","CUST_TITLE","CUST_APPLY","CUST_CANCEL","CUST_DEFAULT","CUST_NOTICE",
      "CUST_PREV","CUST_NEXT","CUST_OPACITY","HUD_TITLE"};
   if(index>=46 && index<61) return(extra[index-46]);
   string names[18]={"0","1","2","3","4","5","6","HUD_RISK_SCOPE","HUD_BG",
      "RAIZ_DETAILS_BUTTON","HUD_MIN","HUD_OPTIONS","HUD_RESTORE","HUD_MODE",
      "HUD_OPACITY","HUD_RESET","HUD_RESIZE","HUD_NOTICE"};
   return(index>=0 && index<18 ? names[index] : "");
  }
void JPWStoikusHUDCleanup()
  {
   JPWStoikusHUDCancel();
   for(int i=0;i<g_stoikus_surface_count;i++)
     { JPWUIDesignDelete(g_stoikus_surfaces[i].name); ResourceFree(JPWStoikusHUDResource(g_stoikus_surfaces[i].name)); g_stoikus_surfaces[i].key=""; }
   // Templates restore exact owned names before this instance has an inventory.
   for(int i=0;i<61;i++)
     { string name=g_panel_prefix+JPWStoikusHUDOwnedSuffix(i); JPWUIDesignDelete(name); ResourceFree(JPWStoikusHUDResource(name)); }
   g_stoikus_surface_count=0;
  }
int JPWStoikusHUDSlot(const string name)
  {
   for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].name==name) return(i);
   if(g_stoikus_surface_count>=96) return(-1);
   int slot=g_stoikus_surface_count++; g_stoikus_surfaces[slot].name=name; g_stoikus_surfaces[slot].key=""; return(slot);
  }
void JPWStoikusHUDPixels(uint &pixels[],const int count,const color surface,const int transparency)
  { ArrayResize(pixels,count); ArrayInitialize(pixels,ColorToARGB(surface,(uchar)JPWStoikusAlpha(transparency))); }
bool JPWStoikusHUDFit(const string text,const int width)
  { uint w=0,h=0; return(TextGetSize(text,w,h) && (int)w<=width); }
bool JPWStoikusHUDWrap(const string text,const int width,string &one,string &two)
  {
   one=text; two=""; if(JPWStoikusHUDFit(text,width)) return(true);
   for(int at=StringLen(text)-1;at>0;at--) if(StringGetCharacter(text,at)==' ')
     {
      string a=StringSubstr(text,0,at),b=StringSubstr(text,at+1);
      if(JPWStoikusHUDFit(a,width) && JPWStoikusHUDFit(b,width)) { one=a; two=b; return(true); }
     }
   one=""; two=""; return(false);
  }
bool JPWStoikusHUDSurfacePaint(const string suffix,const int x,const int y,const int w,const int h,
 const string line1,const string line2,const int font,const color ink,const color fill,const int transparency,const string tip,const int z=3,const string native_caption="",const string right_caption="",const int text_inset=-1)
  {
   const int inset=(text_inset<0 ? JPWUIDesignPx(8) : text_inset);
   string name=g_panel_prefix+suffix; int slot=JPWStoikusHUDSlot(name); if(slot<0 || w<=0 || h<=0 || (long)w*h>2000000) return(false);
   g_stoikus_surfaces[slot].live=true; g_stoikus_surfaces[slot].x=x; g_stoikus_surfaces[slot].y=y; g_stoikus_surfaces[slot].w=w; g_stoikus_surfaces[slot].h=h;g_stoikus_surfaces[slot].z=z;
   string key=IntegerToString(w)+"|"+IntegerToString(h)+"|"+IntegerToString(font)+"|"+IntegerToString((int)ink)+"|"+
      IntegerToString((int)fill)+"|"+IntegerToString(transparency)+"|"+line1+"|"+line2+"|"+right_caption+"|"+IntegerToString(inset);
   bool ready=true;
   if(key!=g_stoikus_surfaces[slot].key || ObjectFind(0,name)<0)
     {
      uint pixels[]; JPWStoikusHUDPixels(pixels,w*h,fill,transparency);
      ready=ArraySize(pixels)==w*h && TextSetFont("Arial",-10*font,FW_NORMAL);
      uint tw=0,th=0; if(ready) ready=TextGetSize("Mg",tw,th);
      // Measure each emitted line at this exact font before rasterizing it.
      uint firstw=0,firsth=0,secondw=0,secondh=0;
      if(ready && line1!="") ready=TextGetSize(line1,firstw,firsth) && (int)firstw<=w-2*inset;
      if(ready && line2!="") ready=TextGetSize(line2,secondw,secondh) && (int)secondw<=w-2*inset;
      uint rightw=0,righth=0;
      if(ready && right_caption!="") ready=TextGetSize(right_caption,rightw,righth) &&
         (int)firstw+(int)rightw+3*inset<=w;
      if(ready) ready=(int)firsth+(int)secondh<=h;
      int text_y=(h-(int)firsth-(int)secondh)/2;
      if(ready && line1!="") ready=TextOut(line1,inset,text_y,TA_LEFT|TA_TOP,pixels,w,h,ColorToARGB(ink,255),COLOR_FORMAT_ARGB_NORMALIZE);
      if(ready && right_caption!="") ready=TextOut(right_caption,w-inset-(int)rightw,text_y,TA_LEFT|TA_TOP,pixels,w,h,ColorToARGB(ink,255),COLOR_FORMAT_ARGB_NORMALIZE);
      if(ready && line2!="") ready=TextOut(line2,inset,text_y+(int)firsth,TA_LEFT|TA_TOP,pixels,w,h,ColorToARGB(ink,255),COLOR_FORMAT_ARGB_NORMALIZE);
      if(ready) ready=ResourceCreate(JPWStoikusHUDResource(name),pixels,w,h,0,0,w,COLOR_FORMAT_ARGB_NORMALIZE);
      if(ready) g_stoikus_surfaces[slot].key=key;
     }
   ENUM_OBJECT kind=ready ? OBJ_BITMAP_LABEL : (suffix=="HUD_BG" ? OBJ_RECTANGLE_LABEL : OBJ_BUTTON);
   if(ObjectFind(0,name)>=0 && ObjectGetInteger(0,name,OBJPROP_TYPE)!=kind) JPWUIDesignDelete(name);
   if(!JPWUIDesignEnsure(name,kind)) return(false);
   if(ready)
      ready=JPWUIDesignSetString(name,OBJPROP_BMPFILE,"::"+JPWStoikusHUDResource(name));
   if(!ready)
     {
      kind=(suffix=="HUD_BG" ? OBJ_RECTANGLE_LABEL : OBJ_BUTTON);
      if(ObjectGetInteger(0,name,OBJPROP_TYPE)!=kind) { JPWUIDesignDelete(name); if(!JPWUIDesignEnsure(name,kind)) return(false); }
      g_stoikus_surfaces[slot].key="";
      g_stoikus_visual_notice="Transparência indisponível; fundo opaco temporário.";
      JPWUIDesignSetInteger(name,OBJPROP_BGCOLOR,fill); JPWUIDesignSetInteger(name,OBJPROP_COLOR,ink);
      // Native buttons have a single line. Financial fallback is explicit
      // Details at the configured font, never a smaller or clipped value.
      bool financial=(StringLen(suffix)==1 || suffix=="HUD_RISK_SCOPE");
      string caption=financial ? "Detalhes" : (native_caption!="" ? native_caption : line1);
      int native_font=font;
      TextSetFont("Arial",-10*native_font,FW_NORMAL);
      if(suffix=="0") caption=JPWStoikusHUDFit("Conta inteira",w-2*JPWUIDesignPx(4)) ? "Conta inteira" : "Conta";
      else if(financial && !JPWStoikusHUDFit(caption,w-2*JPWUIDesignPx(4))) caption="Ver";
      uint native_w=0,native_h=0;
      const int native_inset=MathMin(inset,JPWUIDesignPx(4));
      if(kind==OBJ_BUTTON && (!TextGetSize(caption,native_w,native_h) ||
         (int)native_w>w-2*native_inset || (int)native_h>h-2*native_inset))
        { JPWUIDesignDelete(name); g_stoikus_surfaces[slot].live=false; return(false); }
      JPWUIDesignSetString(name,OBJPROP_FONT,"Arial");
      JPWUIDesignSetInteger(name,OBJPROP_FONTSIZE,native_font); JPWUIDesignSetString(name,OBJPROP_TEXT,caption);
     }
   JPWUIDesignSetInteger(name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   if(kind==OBJ_BITMAP_LABEL) JPWUIDesignSetInteger(name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   JPWUIDesignSetInteger(name,OBJPROP_XDISTANCE,x); JPWUIDesignSetInteger(name,OBJPROP_YDISTANCE,y);
   JPWUIDesignSetInteger(name,OBJPROP_XSIZE,w); JPWUIDesignSetInteger(name,OBJPROP_YSIZE,h);
   JPWUIDesignSetInteger(name,OBJPROP_ZORDER,z); JPWUIDesignSetInteger(name,OBJPROP_SELECTABLE,false);
   JPWUIDesignSetInteger(name,OBJPROP_HIDDEN,true); JPWUIDesignSetInteger(name,OBJPROP_BACK,false);
   JPWUIDesignSetString(name,OBJPROP_TOOLTIP,(kind==OBJ_BUTTON && suffix=="0" ? "Ver detalhes da alavancagem · " : "")+tip+(g_stoikus_visual_notice=="" ? "" : " · "+g_stoikus_visual_notice));
   return(ready);
  }
// Controls may wrap at the same10pt font; their shorter native caption
// retains the action while the tooltip always carries its complete meaning.
void JPWStoikusHUDCaptionPaint(const string suffix,const int x,const int y,const int w,const int h,
 const string caption,const string short_caption,const color ink,const color fill,const string tip,const int z=3)
  {
   TextSetFont("Arial",-100,FW_NORMAL); string one="",two=""; uint tw=0,th=0;
   bool fits=TextGetSize("Mg",tw,th) && JPWStoikusHUDWrap(caption,w-2*JPWUIDesignPx(8),one,two);
   if(!fits || (two!="" && 2*(int)th>h)) { one=short_caption; two=""; }
   JPWStoikusHUDSurfacePaint(suffix,x,y,w,h,one,two,10,ink,fill,100,tip,z,short_caption);
  }
void JPWStoikusHUDPrune()
  {
   for(int owned=0;owned<61;owned++)
     {
      string name=g_panel_prefix+JPWStoikusHUDOwnedSuffix(owned); bool live=false;
      for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].name==name && g_stoikus_surfaces[i].live) { live=true; break; }
      if(!live) { JPWUIDesignDelete(name); ResourceFree(JPWStoikusHUDResource(name)); }
     }
   for(int i=0;i<g_stoikus_surface_count;i++) if(!g_stoikus_surfaces[i].live)
     { JPWUIDesignDelete(g_stoikus_surfaces[i].name); ResourceFree(JPWStoikusHUDResource(g_stoikus_surfaces[i].name)); g_stoikus_surfaces[i].key=""; }
  }
#include <JPWealth/JPW_Stoikus_PanelEditor.mqh>
int g_stoikus_metric_page=0;
string JPWStoikusPanelMetricName(const int index)
  {
   string titles[7]={"Alavancagem","Resultado flutuante","SL da referência","Raiz N · 1 semana",
      "Raiz N · 2 semanas","Risco dos stops","Flutuante compensado"};
   return(index>=0 && index<7 ? titles[index] : "Métrica");
  }
string JPWStoikusPanelMetricScope(const int index)
  {
   if(index==0 || index==1) return("Conta inteira");
   if(index==5) return(JPWRiskDisplayScope());
   if(index==2) return("Referência selecionada/inferida");
   if(index==3 || index==4) return("Símbolo do gráfico · cenário diagnóstico");
   return("Ciclo selecionado · símbolo e direção");
  }
void JPWStoikusHUDRender()
  {
   JPWStoikusVisualRecheck(); JPWStoikusPanelRecheck();
   if(g_stoikus_visual_notice=="Transparência indisponível; fundo opaco temporário.") g_stoikus_visual_notice="";
   for(int i=0;i<g_stoikus_surface_count;i++) g_stoikus_surfaces[i].live=false;
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   const double scale=JPWUIDesignScale(); const int pad=JPWUIDesignPx(8),gap=JPWUIDesignPx(g_cockpit_prefs.density==0 ? 4 : 8),control=JPWUIDesignPx(36);
   const int font=MathMax(8,MathMin(40,InpFontSize)); uint tw=0,th=0;
   if(!TextSetFont("Arial",-10*font,FW_NORMAL) || !TextGetSize("Mg",tw,th)) { JPWHUDUnavailable("Medida do texto indisponível"); return; }
   int width=JPWStoikusHUDWidth(MathMax(0,cw-2*pad),g_stoikus_visual.width,4*control+2*pad,scale);
   int content=width-2*pad,access_pad=pad;
   JPWStoikusPanelPrefs shown=g_stoikus_panel_prefs;
   if(g_stoikus_panel_editor) shown=g_stoikus_panel_draft;
   int metrics[7],heights[7]; bool stacked[7],scope_complete[7]; string names[7],values[7],meta1[7],meta2[7]; int count=0;
   for(int slot=0;slot<7;slot++)
     {
      const int i=shown.order[slot]; if((shown.visible_mask&(1<<i))==0) continue;
      const JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
      names[count]=JPWStoikusPanelMetricName(i); values[count]=JPWCockpitMetricValue(i,metric.value);
      TextSetFont("Arial",-10*font,FW_NORMAL); uint titlew=0,titleh=0,valuew=0,valueh=0;
      TextGetSize(names[count],titlew,titleh);TextGetSize(values[count],valuew,valueh);
      // Widen only for a complete financial value, never shorten its digits.
      if((int)valuew+4*pad>width)
        { width=JPWStoikusHUDWidth(MathMax(0,cw-2*pad),g_stoikus_visual.width,(int)valuew+4*pad,scale);content=width-2*pad; }
      stacked[count]=(int)titlew+(int)valuew+3*pad>content;
      const string quality=JPWCockpitQualityLabel(JPWGenetrixMetricQuality(i,metric.quality));
      const string scope=JPWStoikusPanelMetricScope(i);
      scope_complete[count]=JPWStoikusHUDWrap(quality+" · "+scope,content-2*pad,meta1[count],meta2[count]);
      if(!scope_complete[count])
        {
         meta1[count]=quality; meta2[count]=(i==0 || i==1 ? "Conta inteira" : (i==5 ? "Grupo · ver detalhes" : "Escopo · ver detalhes"));
        }
      if(!JPWStoikusHUDFit(meta1[count],content-2*pad))
         {meta1[count]=(metric.quality==JPW_VIEW_NA ? "N/A" : (metric.quality==JPW_VIEW_ESTIMATED ? "Est." : "Atual"));scope_complete[count]=false;}
      if(!JPWStoikusHUDFit(meta2[count],content-2*pad))
         {meta2[count]=(i==0 || i==1 ? "Conta" : (i==5 ? "Grupo" : (i==2 ? "Ref." : (i==6 ? "Ciclo" : "Símb."))));scope_complete[count]=false;}
      heights[count]=MathMax(control,(stacked[count] ? 2*(int)th : (int)th)+pad+
         (meta2[count]!="" ? 2*(int)th : (int)th)+pad)+gap;
      metrics[count++]=i;
     }
   TextSetFont("Arial",-100,FW_NORMAL); uint aw=0,ah=0,bw=0,bh=0,cwtext=0,chtext=0;
   TextGetSize("Conta",aw,ah);TextGetSize("NoCuda",bw,bh);TextGetSize("Personalizar",cwtext,chtext);
   int access_widths[3]={MathMax(control,(int)aw+2*pad),MathMax(control,(int)bw+2*pad),MathMax(control,(int)cwtext+2*pad)};
   const bool access_inline=access_widths[0]+access_widths[1]+access_widths[2]+2*gap<=content;
   const int access_height=(access_inline ? control : 3*control+2*gap);
   const int heading=control+gap,status=control;
   const int available=MathMax(0,ch-2*pad-JPWUIDesignPx(44));
   const int body_budget=MathMax(0,available-2*pad-heading-access_height-status-control-3*gap);
   int capacity=0,used=0;
   // A stable maximum row height keeps page membership unchanged on quote updates.
   int maxrow=2*(int)th+2*pad+2*(int)th+gap;
   capacity=MathMax(1,body_budget/MathMax(1,maxrow));capacity=MathMin(7,capacity);
   const int pages=MathMax(1,(count+capacity-1)/capacity);
   g_stoikus_metric_page=JPWStoikusClamp(g_stoikus_metric_page,0,pages-1);
   const int first=g_stoikus_metric_page*capacity,last=MathMin(count,first+capacity);
   for(int j=first;j<last;j++) used+=heights[j]+gap;
   bool collapsed=g_stoikus_visual.collapsed;
   int height=2*pad+heading+used+access_height+status+2*gap+(pages>1 ? control+gap : 0);
   TextSetFont("Arial",-10*font,FW_NORMAL);uint minimum_text=0,minimum_height=0;TextGetSize("Conta",minimum_text,minimum_height);
   bool tiny=(height>ch-2*pad || width<4*control+2*pad ||
      (count>0 && (body_budget<maxrow || content-2*pad<(int)minimum_text)));
   if(collapsed || tiny)
     {
      TextSetFont("Arial",-100,FW_NORMAL);
      uint restorew=0,restoreh=0;TextGetSize("Stoikus",restorew,restoreh);
      if(cw<(int)restorew+4*pad || ch<control+2*pad) access_pad=0;
      width=MathMin(cw,(int)restorew+4*pad);height=control+2*access_pad;
      if(height>ch || width-2*access_pad<(int)restorew) { JPWHUDUnavailable("Amplie o gráfico para acessar Stoikus");return; }
     }
   const bool lower=g_cockpit_prefs.corner==CORNER_LEFT_LOWER || g_cockpit_prefs.corner==CORNER_RIGHT_LOWER;
   const bool right=g_cockpit_prefs.corner==CORNER_RIGHT_UPPER || g_cockpit_prefs.corner==CORNER_RIGHT_LOWER;
   int x=g_stoikus_visual.positioned ? (int)MathRound(g_stoikus_visual.x*scale) : (right ? cw-InpOffsetX-width : InpOffsetX);
   int y=g_stoikus_visual.positioned ? (int)MathRound(g_stoikus_visual.y*scale) : (lower ? ch-InpOffsetY-height : MathMax(InpOffsetY,JPWUIDesignPx(44)));
   x=JPWStoikusClamp(x,0,cw-width);
   const int minimum_y=(g_stoikus_visual.positioned ? 0 : MathMax(0,MathMin(JPWUIDesignPx(44),ch-height)));
   y=JPWStoikusClamp(y,minimum_y,ch-height);
   g_stoikus_hud.x=x;g_stoikus_hud.y=y;g_stoikus_hud.width=width;g_stoikus_hud.height=height;
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND),fill=JPWPanelSurface(background),ink=JPWPanelInk(background);
   JPWStoikusHUDSurfacePaint("HUD_BG",x,y,width,height,"","",font,ink,fill,JPWStoikusPanelTransparency(),"Painel Stoikus · fundo ajustável",1);
   g_hud_summary=false;g_hud_summary_source=-1;
   JPWUIDesignDelete(g_panel_prefix+"RAIZ_UI_HUD_LABEL");JPWUIDesignDeleteIcon(g_panel_prefix+"RAIZ_UI_HUD_ICON");
   if(collapsed || tiny)
     {
      uint restorew=0,restoreh=0;TextSetFont("Arial",-100,FW_NORMAL);TextGetSize("Stoikus",restorew,restoreh);
      const int restore_inset=MathMin(pad,MathMax(0,(width-2*access_pad-(int)restorew)/2));
      JPWStoikusHUDSurfacePaint("HUD_RESTORE",x+access_pad,y+access_pad,width-2*access_pad,control,"Stoikus","",10,ink,fill,100,
         tiny ? "Abrir Conta; amplie o gráfico para exibir o painel" : "Restaurar painel Stoikus",4,"Stoikus","",restore_inset);
      if(g_stoikus_panel_editor) JPWStoikusPanelEditorRender(cw,ch,ink,fill);
      JPWStoikusHUDPrune();g_panel_count=7;return;
     }
   JPWStoikusHUDSurfacePaint("HUD_TITLE",x+pad,y+pad,content-control-gap,control,"Stoikus","",10,ink,fill,100,"Arraste esta faixa para mover o painel",2);
   JPWStoikusHUDSurfacePaint("HUD_MIN",x+width-pad-control,y+pad,control,control,"−","",10,ink,fill,100,"Recolher painel Stoikus",4);
   int yy=y+pad+heading;
   bool any_na=false,any_estimated=false; string fit_notice="";
   for(int slot=0;slot<count;slot++)
     { const int i=metrics[slot];any_na=any_na || g_cockpit_snapshot.metric[i].quality==JPW_VIEW_NA;
       any_estimated=any_estimated || g_cockpit_snapshot.metric[i].quality==JPW_VIEW_ESTIMATED; }
   for(int j=first;j<last;j++)
     {
      const int i=metrics[j]; const JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
      string full=names[j]+": "+values[j]+" · "+JPWCockpitQualityLabel(JPWGenetrixMetricQuality(i,metric.quality))+" · "+JPWStoikusPanelMetricScope(i)+" · "+metric.reason;
      const int metadata_height=(meta2[j]!="" ? 2*(int)th : (int)th)+pad;
      // Title/value and metadata are contiguous halves of one canonical target.
      const int main_height=MathMax(control-metadata_height,(stacked[j] ? 2*(int)th : (int)th)+pad);
      TextSetFont("Arial",-10*font,FW_NORMAL);
      string title=names[j],value=values[j];
      if(!JPWStoikusHUDFit(title,content-2*pad))
        {string compact[7]={"Alav.","P/L","SL","RN1W","RN2W","Risco","Comp."};title=compact[i];}
      bool numeric_fits=JPWStoikusHUDFit(value,content-2*pad);
      // A risk amount must remain attached to its complete accepted group.
      // Keep the canonical value and detail route when that scope cannot fit.
      if(!numeric_fits || (i==5 && !scope_complete[j]))
        {value=JPWStoikusHUDFit("Detalhes",content-2*pad) ? "Detalhes" : "Ver";fit_notice="Valor integral disponível em Conta; amplie o gráfico.";}
      JPWStoikusHUDSurfacePaint(IntegerToString(i),x+pad,yy,content,main_height,title,
         stacked[j] ? value : "",font,ink,fill,100,full,3,"Ver detalhes",stacked[j] ? "" : value);
      int mh=metadata_height;
      JPWStoikusHUDSurfacePaint(IntegerToString(i)+"_META",x+pad,yy+main_height,content,mh,
         meta1[j],meta2[j],font,ink,fill,100,full,3,meta1[j]);
      yy+=heights[j]+gap;
     }
   if(pages>1)
     {
      JPWStoikusHUDCaptionPaint("HUD_PREVIOUS",x+pad,yy,control,control,"‹","‹",ink,fill,"Métricas anteriores");
      JPWStoikusHUDCaptionPaint("HUD_PAGE",x+pad+control,yy,content-2*control,control,
         IntegerToString(g_stoikus_metric_page+1)+" / "+IntegerToString(pages),"Página",ink,fill,"Página de métricas");
      JPWStoikusHUDCaptionPaint("HUD_NEXT",x+width-pad-control,yy,control,control,"›","›",ink,fill,"Próximas métricas"); yy+=control+gap;
     }
   string access_ids[3]={"RAIZ_DETAILS_BUTTON","HUD_NOCUDA","HUD_PERSONALIZE"};string captions[3]={"Conta","NoCuda","Personalizar"};
   int access_x=x+pad;
   for(int i=0;i<3;i++)
     {
      const string hint=(i==0 ? "Abrir Conta" : (i==1 ? (JPWStoikusPanelPeerReady(true) ? "Abrir NoCuda" : "Abra Navegador (Ctrl+N) e arraste Indicadores → JPWealth → JPW_NoCuda_Channels para este gráfico") : "Escolher informações, ordem e aparência do painel"));
      JPWStoikusHUDSurfacePaint(access_ids[i],access_x,yy,access_inline ? access_widths[i] : content,control,captions[i],"",10,ink,fill,100,hint,4);
      if(access_inline) access_x+=access_widths[i]+gap;else yy+=control+gap;
     }
   if(access_inline) yy+=control+gap;
   const string availability=(count==0 ? "Personalize para adicionar métricas" : (any_na ? "Dados indisponíveis · detalhes" : (any_estimated ? "Inclui estimativas · detalhes" : "Leituras atuais")));
   string notice=g_stoikus_panel_notice!="" ? g_stoikus_panel_notice : (fit_notice!="" ? fit_notice : (g_stoikus_visual_notice!="" ? g_stoikus_visual_notice : availability));
   JPWStoikusHUDCaptionPaint("HUD_NOTICE",x+pad,y+height-pad-control,content-control,control,notice,
      count==0 ? "Escolher" : (any_na ? "N/A" : "Estado"),ink,fill,notice);
   JPWStoikusHUDSurfacePaint("HUD_RESIZE",x+width-pad-control,y+height-pad-control,control,control,"↔","",10,ink,fill,100,"Arraste para ajustar a largura",4);
   if(g_stoikus_panel_editor) JPWStoikusPanelEditorRender(cw,ch,ink,fill);
   JPWStoikusHUDPrune();g_panel_count=7;
  }
string JPWStoikusHUDHit(const int x,const int y)
  {
   int hit=-1;
   for(int i=g_stoikus_surface_count-1;i>=0;i--)
      if(g_stoikus_surfaces[i].live && g_stoikus_surfaces[i].name!=g_panel_prefix+"HUD_BG" &&
         x>=g_stoikus_surfaces[i].x && x<g_stoikus_surfaces[i].x+g_stoikus_surfaces[i].w &&
         y>=g_stoikus_surfaces[i].y && y<g_stoikus_surfaces[i].y+g_stoikus_surfaces[i].h &&
         (hit<0 || g_stoikus_surfaces[i].z>g_stoikus_surfaces[hit].z)) hit=i;
   return(hit>=0 ? g_stoikus_surfaces[hit].name : "");
  }
bool JPWStoikusHUDCovered(const int x,const int y)
  {
   const string owner=JPWUIOwner(); if(owner=="") return(false);
   string suffixes[3]={"RAIZ_UI_BG","UI_BG","FC_BACKGROUND"};
   for(int i=0;i<3;i++)
     {
      string name=owner+suffixes[i]; if(ObjectFind(0,name)<0) continue;
      long kind=ObjectGetInteger(0,name,OBJPROP_TYPE);
      if((kind!=OBJ_RECTANGLE_LABEL && kind!=OBJ_BITMAP_LABEL) || ObjectGetInteger(0,name,OBJPROP_CORNER)!=CORNER_LEFT_UPPER) continue;
      int left=(int)ObjectGetInteger(0,name,OBJPROP_XDISTANCE),top=(int)ObjectGetInteger(0,name,OBJPROP_YDISTANCE);
      int width=(int)ObjectGetInteger(0,name,OBJPROP_XSIZE),height=(int)ObjectGetInteger(0,name,OBJPROP_YSIZE);
      if(x>=left && x<left+width && y>=top && y<top+height) return(true);
     }
   return(false);
  }
bool JPWStoikusHUDEvent(const int id,const long &lparam,const double &dparam,const string &sparam,string &route)
  {
   route="";
   if(g_stoikus_panel_editor && id==CHARTEVENT_KEYDOWN &&
      JPWStoikusPanelEditorKey(lparam,(TerminalInfoInteger(TERMINAL_KEYSTATE_SHIFT)&0x8000)!=0))
     { JPWRenderHUD();return(true); }
   if(g_stoikus_panel_editor && id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=g_panel_prefix)
      JPWStoikusPanelEditorSuspend();
   if(id==CHARTEVENT_CHART_CHANGE || (id==CHARTEVENT_KEYDOWN && lparam==27) ||
      (id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=g_panel_prefix)) JPWStoikusHUDCancel();
   int mx=(int)lparam,my=(int)dparam;
   if((id==CHARTEVENT_CLICK || (id==CHARTEVENT_MOUSE_MOVE && !g_stoikus_drag && !g_stoikus_resize)) &&
      JPWStoikusHUDCovered(mx,my)) return(false);
   if(id==CHARTEVENT_MOUSE_MOVE)
     {
      bool down=((int)StringToInteger(sparam)&1)!=0;
      if(!down && (g_stoikus_drag || g_stoikus_resize))
        {
         JPWStoikusVisual candidate=g_stoikus_visual;
         ChartSetInteger(0,CHART_MOUSE_SCROLL,g_stoikus_scroll);
         g_stoikus_drag=false; g_stoikus_resize=false; g_stoikus_visual=g_stoikus_gesture_before;
         if(g_stoikus_gesture_moved) JPWStoikusVisualSave(candidate);
         JPWRenderHUD(); return(true);
        }
      if(down && !g_stoikus_drag && !g_stoikus_resize)
        {
         string hit=JPWStoikusHUDHit(mx,my);
         bool resize=hit==g_panel_prefix+"HUD_RESIZE";
         bool header=(hit=="" || hit==g_panel_prefix+"HUD_TITLE") && mx>=g_stoikus_hud.x && mx<g_stoikus_hud.x+g_stoikus_hud.width &&
            my>=g_stoikus_hud.y && my<g_stoikus_hud.y+JPWUIDesignPx(44);
         if(!resize && !header) return(false);
         g_stoikus_gesture_before=g_stoikus_visual; g_stoikus_scroll=(bool)ChartGetInteger(0,CHART_MOUSE_SCROLL);
         if(!ChartSetInteger(0,CHART_MOUSE_SCROLL,false)) return(false);
         g_stoikus_drag=header; g_stoikus_resize=resize; g_stoikus_gesture_moved=false; g_stoikus_start_x=mx; g_stoikus_start_y=my;
         g_stoikus_origin_x=g_stoikus_hud.x; g_stoikus_origin_y=g_stoikus_hud.y; g_stoikus_origin_w=g_stoikus_hud.width;
        }
      if(g_stoikus_drag || g_stoikus_resize)
        {
         double scale=JPWUIDesignScale(); int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
         if(mx!=g_stoikus_start_x || my!=g_stoikus_start_y) g_stoikus_gesture_moved=true;
         if(g_stoikus_resize) g_stoikus_visual.width=JPWStoikusClamp((int)MathRound((g_stoikus_origin_w+mx-g_stoikus_start_x)/scale),120,480);
         else { g_stoikus_visual.positioned=true;
            g_stoikus_visual.x=(int)MathRound(JPWStoikusClamp(g_stoikus_origin_x+mx-g_stoikus_start_x,0,cw-g_stoikus_hud.width)/scale);
            g_stoikus_visual.y=(int)MathRound(JPWStoikusClamp(g_stoikus_origin_y+my-g_stoikus_start_y,0,ch-g_stoikus_hud.height)/scale); }
         JPWRenderHUD(); return(true);
        }
      return(false);
     }
   if(id!=CHARTEVENT_CLICK && id!=CHARTEVENT_OBJECT_CLICK) return(false);
   ulong now=GetTickCount64();
   // Consume the paired native event before hit-testing a layout changed by
   // the first event (collapse/restore can replace the object under the pointer).
   if(g_stoikus_last_click!="" && id!=g_stoikus_last_kind && now-g_stoikus_last_time<250 &&
      ((mx==g_stoikus_last_x && my==g_stoikus_last_y) || sparam==g_stoikus_last_click))
     { g_stoikus_last_click=""; return(true); }
   string target=id==CHARTEVENT_CLICK ? JPWStoikusHUDHit(mx,my) : sparam;
   if(g_stoikus_panel_editor && id==CHARTEVENT_OBJECT_CLICK && StringFind(sparam,g_panel_prefix)==0)
     {string upper=JPWStoikusHUDHit(mx,my);if(StringFind(upper,g_panel_prefix+"CUST_")==0)target=upper;}
   int found=-1; for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].live && g_stoikus_surfaces[i].name==target) found=i;
   if(found<0 || target==g_panel_prefix+"HUD_BG") return(false);
   if(target==g_stoikus_last_click && id!=g_stoikus_last_kind && now-g_stoikus_last_time<250)
     { g_stoikus_last_click=""; return(true); }
   g_stoikus_last_click=target; g_stoikus_last_kind=id; g_stoikus_last_time=now; g_stoikus_last_x=mx; g_stoikus_last_y=my;
   const string suffix=StringSubstr(target,StringLen(g_panel_prefix));
   if(JPWStoikusPanelEditorAction(suffix)) {JPWRenderHUD();return(true);}
   if(g_stoikus_panel_editor && StringFind(suffix,"CUST_")==0) return(true);
   if(suffix=="HUD_PERSONALIZE") {JPWStoikusPanelEditorOpen();JPWRenderHUD();return(true);}
   if(suffix=="HUD_NOCUDA")
     {
      if(JPWStoikusPanelPeerReady(true))
        {
         if(g_stoikus_panel_editor) JPWStoikusPanelEditorSuspend();
         if(g_raiz_details_open) JPWAccountMinimize();
         if(!JPWStoikusPanelOpenNoCuda(g_panel_prefix)) g_stoikus_panel_notice="Não foi possível abrir NoCuda. Confira o indicador e tente novamente.";
        }
      else g_stoikus_panel_notice="Abra Navegador (Ctrl+N) e arraste Indicadores → JPWealth → JPW_NoCuda_Channels para este gráfico. Confira a presença com Ctrl+I.";
      JPWRenderHUD();return(true);
     }
   if(suffix=="HUD_TITLE" || suffix=="HUD_PAGE") return(true);
   if(suffix=="HUD_PREVIOUS" || suffix=="HUD_NEXT")
     {g_stoikus_metric_page+=(suffix=="HUD_PREVIOUS" ? -1 : 1);JPWRenderHUD();return(true);}
   if(suffix=="RAIZ_DETAILS_BUTTON" && g_stoikus_panel_editor) JPWStoikusPanelEditorSuspend();
   if(StringLen(suffix)==6 && StringSubstr(suffix,1)=="_META")
     {route=g_panel_prefix+StringSubstr(suffix,0,1);return(true);}
   JPWStoikusVisual next=g_stoikus_visual; bool save=true,restore=false;
   if(target==g_panel_prefix+"HUD_OPTIONS") { g_stoikus_options=!g_stoikus_options; save=false; }
   else if(target==g_panel_prefix+"HUD_MIN") next.collapsed=true;
   else if(target==g_panel_prefix+"HUD_RESTORE")
     {if(!next.collapsed){route=g_panel_prefix+"RAIZ_DETAILS_BUTTON";return(true);}next.collapsed=false;}
   else if(target==g_panel_prefix+"HUD_MODE") next.mode=1-next.mode;
   else if(target==g_panel_prefix+"HUD_OPACITY") next.transparency=(next.transparency+10)%110;
   else if(target==g_panel_prefix+"HUD_RESET")
     { next.mode=0; next.collapsed=false; next.transparency=30; next.width=280; next.positioned=false; restore=true; }
   else if(target==g_panel_prefix+"HUD_RESIZE") return(true);
   else { route=target; return(true); }
   if(save) JPWStoikusVisualSave(next,restore);
   JPWRenderHUD(); return(true);
  }
#endif

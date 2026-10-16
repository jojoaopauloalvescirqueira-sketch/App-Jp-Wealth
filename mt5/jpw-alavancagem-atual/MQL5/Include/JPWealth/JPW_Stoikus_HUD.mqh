#ifndef JPW_STOIKUS_HUD_MQH
#define JPW_STOIKUS_HUD_MQH
#include <JPWealth/JPW_Stoikus_Visual.mqh>
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
  { string name,key; int x,y,w,h; bool live; };
JPWStoikusHUDSurface g_stoikus_surfaces[18];
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
   for(int i=0;i<18;i++)
     { string name=g_panel_prefix+JPWStoikusHUDOwnedSuffix(i); JPWUIDesignDelete(name); ResourceFree(JPWStoikusHUDResource(name)); }
   g_stoikus_surface_count=0;
  }
int JPWStoikusHUDSlot(const string name)
  {
   for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].name==name) return(i);
   if(g_stoikus_surface_count>=18) return(-1);
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
 const string line1,const string line2,const int font,const color ink,const color fill,const int transparency,const string tip,const int z=3,const string native_caption="")
  {
   string name=g_panel_prefix+suffix; int slot=JPWStoikusHUDSlot(name); if(slot<0 || w<=0 || h<=0 || (long)w*h>2000000) return(false);
   g_stoikus_surfaces[slot].live=true; g_stoikus_surfaces[slot].x=x; g_stoikus_surfaces[slot].y=y; g_stoikus_surfaces[slot].w=w; g_stoikus_surfaces[slot].h=h;
   string key=IntegerToString(w)+"|"+IntegerToString(h)+"|"+IntegerToString(font)+"|"+IntegerToString((int)ink)+"|"+
      IntegerToString((int)fill)+"|"+IntegerToString(transparency)+"|"+line1+"|"+line2;
   bool ready=true;
   if(key!=g_stoikus_surfaces[slot].key || ObjectFind(0,name)<0)
     {
      uint pixels[]; JPWStoikusHUDPixels(pixels,w*h,fill,transparency);
      ready=ArraySize(pixels)==w*h && TextSetFont("Arial",-10*font,FW_NORMAL);
      uint tw=0,th=0; if(ready) ready=TextGetSize("Mg",tw,th);
      // Measure each emitted line at this exact font before rasterizing it.
      uint firstw=0,firsth=0,secondw=0,secondh=0;
      if(ready && line1!="") ready=TextGetSize(line1,firstw,firsth) && (int)firstw<=w-2*JPWUIDesignPx(8);
      if(ready && line2!="") ready=TextGetSize(line2,secondw,secondh) && (int)secondw<=w-2*JPWUIDesignPx(8);
      if(ready) ready=(int)firsth+(int)secondh<=h;
      int text_y=(h-(int)firsth-(int)secondh)/2;
      if(ready && line1!="") ready=TextOut(line1,JPWUIDesignPx(8),text_y,TA_LEFT|TA_TOP,pixels,w,h,ColorToARGB(ink,255),COLOR_FORMAT_ARGB_NORMALIZE);
      if(ready && line2!="") ready=TextOut(line2,JPWUIDesignPx(8),text_y+(int)firsth,TA_LEFT|TA_TOP,pixels,w,h,ColorToARGB(ink,255),COLOR_FORMAT_ARGB_NORMALIZE);
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
      // Details at10pt, never a smaller or clipped numeric value.
      bool financial=(StringLen(suffix)==1 || suffix=="HUD_RISK_SCOPE");
      string caption=financial ? "Detalhes" : (native_caption!="" ? native_caption : line1);
      int native_font=financial ? 10 : font;
      TextSetFont("Arial",-10*native_font,FW_NORMAL);
      if(suffix=="0") caption=JPWStoikusHUDFit("Conta inteira",w-2*JPWUIDesignPx(4)) ? "Conta inteira" : "Toda a conta";
      uint native_w=0,native_h=0;
      if(kind==OBJ_BUTTON && (!TextGetSize(caption,native_w,native_h) ||
         (int)native_w>w-2*JPWUIDesignPx(4) || (int)native_h>h-2*JPWUIDesignPx(4)))
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
   for(int owned=0;owned<18;owned++)
     {
      string name=g_panel_prefix+JPWStoikusHUDOwnedSuffix(owned); bool live=false;
      for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].name==name && g_stoikus_surfaces[i].live) { live=true; break; }
      if(!live) { JPWUIDesignDelete(name); ResourceFree(JPWStoikusHUDResource(name)); }
     }
   for(int i=0;i<g_stoikus_surface_count;i++) if(!g_stoikus_surfaces[i].live)
     { JPWUIDesignDelete(g_stoikus_surfaces[i].name); ResourceFree(JPWStoikusHUDResource(g_stoikus_surfaces[i].name)); g_stoikus_surfaces[i].key=""; }
  }
void JPWStoikusHUDRender()
  {
   JPWStoikusVisualRecheck();
   if(g_stoikus_visual_notice=="Transparência indisponível; fundo opaco temporário.") g_stoikus_visual_notice="";
   for(int i=0;i<g_stoikus_surface_count;i++) g_stoikus_surfaces[i].live=false;
   int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   double scale=JPWUIDesignScale(); int pad=JPWUIDesignPx(8),control=JPWUIDesignPx(36);
   int font=MathMax(8,MathMin(40,InpFontSize)); uint tw=0,th=0;
   if(!TextSetFont("Arial",-10*font,FW_NORMAL) || !TextGetSize("Mg",tw,th)) { JPWHUDUnavailable("Medida do texto indisponível"); return; }
   int gap=(g_cockpit_prefs.density==0 ? JPWUIDesignPx(4) : JPWUIDesignPx(8));
   // Two fixed text lines per row prevent movement caused by live values/quality.
   int row=MathMax(control,2*(int)th+2*pad),header=control;
   int width=JPWStoikusHUDWidth(cw-2*pad,g_stoikus_visual.width,4*control+2*pad,scale);
   int count=0;
   for(int i=0;i<7;i++) if(JPWStoikusMetricVisible(g_stoikus_visual.mode,g_cockpit_prefs.visible_mask,i)) count++;
   bool risk=JPWStoikusMetricVisible(g_stoikus_visual.mode,g_cockpit_prefs.visible_mask,5);
   bool collapsed=g_stoikus_visual.collapsed; int access_pad=pad;
   int options=(g_stoikus_options && !collapsed ? 3*(control+gap) : 0);
   int height=2*pad+header+(collapsed ? 0 : (count+(risk ? 1 : 0))*(row+gap)+options+control);
   bool lower=g_cockpit_prefs.corner==CORNER_LEFT_LOWER || g_cockpit_prefs.corner==CORNER_RIGHT_LOWER;
   int available_height=ch-2*pad;
   // Every default corner reserves the native heading before choosing the
   // full layout. Explicitly moved positions retain their own anchor.
   if(!g_stoikus_visual.positioned)
      available_height=MathMin(available_height,lower ? ch-JPWUIDesignPx(44)-MathMax(0,InpOffsetY) : ch-MathMax(InpOffsetY,JPWUIDesignPx(44)));
   bool tiny=height>available_height || width<4*control+2*pad;
   // A template may restore old HUD rows before this runtime inventory exists.
   // Delete only canonical owned metric IDs excluded by the current mode/mask.
   for(int i=0;i<7;i++) if(collapsed || tiny || !JPWStoikusMetricVisible(g_stoikus_visual.mode,g_cockpit_prefs.visible_mask,i))
      JPWUIDesignDelete(g_panel_prefix+IntegerToString(i));
   if(collapsed || tiny || !risk) JPWUIDesignDelete(g_panel_prefix+"HUD_RISK_SCOPE");
   if(collapsed || tiny)
     {
      TextSetFont("Arial",-100,FW_NORMAL); uint pillw=0,pillh=0;
      TextGetSize("Conta",pillw,pillh);
      int button_width=MathMax(control,(int)pillw+2*pad);
      // Drop surrounding space when the measured access button itself fits.
      // This keeps Conta reachable on narrow/high-DPI charts without shrinking text.
      if(cw<button_width+4*pad || ch<control+2*pad) access_pad=0;
      width=button_width+2*access_pad; height=control+2*access_pad;
      if(width>cw || height>ch) { JPWHUDUnavailable("Amplie o gráfico"); return; }
     }
   if(width<control || height>ch) { JPWHUDUnavailable("Amplie o gráfico"); return; }
   bool right=g_cockpit_prefs.corner==CORNER_RIGHT_UPPER || g_cockpit_prefs.corner==CORNER_RIGHT_LOWER;
   int x=g_stoikus_visual.positioned ? (int)MathRound(g_stoikus_visual.x*scale) : (right ? cw-InpOffsetX-width : InpOffsetX);
   int y=g_stoikus_visual.positioned ? (int)MathRound(g_stoikus_visual.y*scale) : (lower ? ch-InpOffsetY-height : MathMax(InpOffsetY,JPWUIDesignPx(44)));
   x=JPWStoikusClamp(x,0,cw-width); y=JPWStoikusClamp(y,0,ch-height);
   // Recover oversized legacy offsets without moving default controls into
   // the heading when the measured account access button has room below it.
   if(!g_stoikus_visual.positioned && ch-height>=JPWUIDesignPx(44)) y=MathMax(y,JPWUIDesignPx(44));
   g_stoikus_hud.x=x; g_stoikus_hud.y=y; g_stoikus_hud.width=width; g_stoikus_hud.height=height;
   color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND),fill=JPWPanelSurface(background),ink=JPWPanelTextColor(background,InpFontColor);
   JPWStoikusHUDSurfacePaint("HUD_BG",x,y,width,height,"","",font,ink,fill,g_stoikus_visual.transparency,"Arraste o cabeçalho para mover",1);
   g_hud_summary=false; g_hud_summary_source=-1;
   JPWUIDesignDelete(g_panel_prefix+"RAIZ_UI_HUD_LABEL"); JPWUIDesignDeleteIcon(g_panel_prefix+"RAIZ_UI_HUD_ICON");
   if(collapsed || tiny)
     {
      JPWStoikusHUDSurfacePaint(collapsed ? "HUD_RESTORE" : "RAIZ_DETAILS_BUTTON",x+access_pad,y+access_pad,width-2*access_pad,control,
         "Conta","",10,ink,fill,100,collapsed ? "Restaurar resumo da Conta" : "Abrir Conta; amplie o gráfico para exibir o resumo",4);
      JPWStoikusHUDPrune(); g_panel_count=7; return;
     }
   int content=width-2*pad;
   // Buttons occupy only the left caption and right controls; the middle is a drag handle.
   JPWStoikusHUDSurfacePaint("RAIZ_DETAILS_BUTTON",x+pad,y+pad,2*control,control,"Conta","",10,ink,fill,100,"Abrir ou trazer Conta à frente",4);
   JPWStoikusHUDSurfacePaint("HUD_MIN",x+width-pad-2*control,y+pad,control,control,"−","",10,ink,fill,100,"Recolher resumo",4);
   JPWStoikusHUDSurfacePaint("HUD_OPTIONS",x+width-pad-control,y+pad,control,control,"⋯","",10,ink,fill,100,"Opções do resumo",4);
   int yy=y+pad+header+gap; bool any_na=false,any_estimated=false;
   string titles[7]={"Alavancagem","Resultado","SL","RN1W","RN2W","Risco","Compensada"};
   for(int slot=0;slot<7;slot++)
     {
      int i=JPWCockpitPresentationIndex(slot);
      if(!JPWStoikusMetricVisible(g_stoikus_visual.mode,g_cockpit_prefs.visible_mask,i)) continue;
      JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
      any_na=any_na || metric.quality==JPW_VIEW_NA; any_estimated=any_estimated || metric.quality==JPW_VIEW_ESTIMATED;
      string full=titles[i]+": "+JPWCockpitMetricValue(i,metric.value)+" · "+JPWCockpitQualityLabel(JPWGenetrixMetricQuality(i,metric.quality))+(i==0 ? " · Conta inteira" : "");
      string one="",two=""; TextSetFont("Arial",-10*font,FW_NORMAL);
      bool scopefits=true; string scope1="",scope2="";
      if(i==5) scopefits=JPWStoikusHUDWrap(JPWRiskDisplayScope(),content-2*pad,scope1,scope2);
      bool details=!scopefits || !JPWStoikusHUDWrap(full,content-2*pad,one,two);
      int paintfont=(details ? 10 : font);
      if(details)
        {
         TextSetFont("Arial",-100,FW_NORMAL);
         if(!JPWStoikusHUDWrap(titles[i]+" · Detalhes",content-2*pad,one,two))
           { one="Detalhes"; two=""; }
         // Keep the leverage account scope visible even in details fallback.
         // Its metric name and original value remain complete in tooltip/details.
         if(i==0) { one=JPWStoikusHUDFit("Conta inteira",content-2*pad) ? "Conta inteira" : "Toda a conta"; two="Detalhes"; }
        }
      JPWStoikusHUDSurfacePaint(IntegerToString(i),x+pad,yy,content,row,one,two,paintfont,ink,fill,100,full+" · "+metric.reason+(i==5 ? " · "+JPWRiskDisplayScope() : ""));
      yy+=row+gap;
      if(i==5)
        {
         if(!scopefits) { scope1="Grupo"; scope2="Detalhes"; }
         JPWStoikusHUDSurfacePaint("HUD_RISK_SCOPE",x+pad,yy,content,row,scope1,scope2,scopefits ? font : 10,ink,fill,100,JPWRiskDisplayScope()+" · "+metric.reason);
         yy+=row+gap;
        }
     }
   if(g_stoikus_options)
     {
      JPWStoikusHUDCaptionPaint("HUD_MODE",x+pad,yy,content,control,g_stoikus_visual.mode==0 ? "Compacto → Completo" : "Completo → Compacto",g_stoikus_visual.mode==0 ? "Completo" : "Compacto",ink,fill,g_stoikus_visual.mode==0 ? "Mudar de Compacto para Completo" : "Mudar de Completo para Compacto"); yy+=control+gap;
      JPWStoikusHUDCaptionPaint("HUD_OPACITY",x+pad,yy,content,control,"Transparência: "+IntegerToString(g_stoikus_visual.transparency)+"% +10",IntegerToString(g_stoikus_visual.transparency)+"% +10",ink,fill,"Transparência atual: "+IntegerToString(g_stoikus_visual.transparency)+"%. Aumentar em 10%; após 100%, volta a 0%"); yy+=control+gap;
      JPWStoikusHUDCaptionPaint("HUD_RESET",x+pad,yy,content,control,"Restaurar visual","Restaurar",ink,fill,"Restaurar preferências visuais do resumo"); yy+=control+gap;
     }
   string availability=count==0 ? "Sem métricas" : (any_na ? "Leitura indisponível" : (any_estimated ? "Leitura estimada" : "Leituras atuais"));
   string short_notice=g_stoikus_visual_notice!="" ? "Aviso" : (count==0 ? "Sem dados" : (any_na ? "N/A" : (any_estimated ? "Estimada" : "Atuais")));
   JPWStoikusHUDCaptionPaint("HUD_NOTICE",x+pad,y+height-pad-control,content-control,control,
      g_stoikus_visual_notice!="" ? "Visual · aviso" : availability,short_notice,ink,fill,
      g_stoikus_visual_notice!="" ? g_stoikus_visual_notice : availability+" · Consulte as razões nos detalhes de cada métrica.");
   JPWStoikusHUDSurfacePaint("HUD_RESIZE",x+width-pad-control,y+height-pad-control,control,control,"↔","",10,ink,fill,100,"Arraste para ajustar a largura",4);
   JPWStoikusHUDPrune(); g_panel_count=7;
  }
string JPWStoikusHUDHit(const int x,const int y)
  {
   for(int i=g_stoikus_surface_count-1;i>=0;i--)
      if(g_stoikus_surfaces[i].live && g_stoikus_surfaces[i].name!=g_panel_prefix+"HUD_BG" &&
         x>=g_stoikus_surfaces[i].x && x<g_stoikus_surfaces[i].x+g_stoikus_surfaces[i].w &&
         y>=g_stoikus_surfaces[i].y && y<g_stoikus_surfaces[i].y+g_stoikus_surfaces[i].h) return(g_stoikus_surfaces[i].name);
   return("");
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
         bool header=hit=="" && mx>=g_stoikus_hud.x && mx<g_stoikus_hud.x+g_stoikus_hud.width &&
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
   int found=-1; for(int i=0;i<g_stoikus_surface_count;i++) if(g_stoikus_surfaces[i].live && g_stoikus_surfaces[i].name==target) found=i;
   if(found<0 || target==g_panel_prefix+"HUD_BG") return(false);
   if(target==g_stoikus_last_click && id!=g_stoikus_last_kind && now-g_stoikus_last_time<250)
     { g_stoikus_last_click=""; return(true); }
   g_stoikus_last_click=target; g_stoikus_last_kind=id; g_stoikus_last_time=now; g_stoikus_last_x=mx; g_stoikus_last_y=my;
   JPWStoikusVisual next=g_stoikus_visual; bool save=true,restore=false;
   if(target==g_panel_prefix+"HUD_OPTIONS") { g_stoikus_options=!g_stoikus_options; save=false; }
   else if(target==g_panel_prefix+"HUD_MIN") next.collapsed=true;
   else if(target==g_panel_prefix+"HUD_RESTORE") next.collapsed=false;
   else if(target==g_panel_prefix+"HUD_MODE") next.mode=1-next.mode;
   else if(target==g_panel_prefix+"HUD_OPACITY") next.transparency=(next.transparency+10)%110;
   else if(target==g_panel_prefix+"HUD_RESET")
     { next.mode=0; next.collapsed=false; next.transparency=30; next.width=280; next.positioned=false; restore=true; }
   else if(target==g_panel_prefix+"HUD_RESIZE" || target==g_panel_prefix+"HUD_NOTICE") return(true);
   else { route=target; return(true); }
   if(save) JPWStoikusVisualSave(next,restore);
   JPWRenderHUD(); return(true);
  }
#endif

#ifndef JPW_ALAVANCAGEM_PRESENTATION_MQH
#define JPW_ALAVANCAGEM_PRESENTATION_MQH
#include <JPWealth/JPW_Genetrix_Brand.mqh>
// Indicator runtime component; included after its instance state.

// Focus belongs to the last explicitly clicked component, not merely to an
// open window. This flag is transient and private to this indicator instance.
// A late ENDEDIT still reaches the existing field handler; it must not steal
// focus back after the user has clicked another indicator's editor.
bool JPWCockpitAcceptChartEvent(const int id,const long &lparam,
                                const double &dparam,const string &object_name)
  {
   static bool cockpit_focus_owner=false;
   static bool recent_object=false;
   static long object_x=0,object_y=0;
   static ulong object_ms=0;
   if(g_panel_prefix=="") { cockpit_focus_owner=false; recent_object=false; }
   const bool own=(g_panel_prefix!="" && StringFind(object_name,g_panel_prefix)==0);
   if(id==CHARTEVENT_OBJECT_CLICK)
     {
      cockpit_focus_owner=own;
      recent_object=MathIsValidNumber(dparam);
      object_x=lparam; object_y=(recent_object ? (long)dparam : 0);
      object_ms=GetTickCount64();
     }
   else if(id==CHARTEVENT_CLICK)
     {
      // MT5 may emit OBJECT_CLICK and CLICK for one gesture in either order.
      // Consume one matching pair; a separate bare chart click releases focus.
      const ulong now=GetTickCount64();
      const bool paired=(recent_object && now>=object_ms && now-object_ms<=1500 &&
         MathIsValidNumber(dparam) && MathAbs(lparam-object_x)<=4 &&
         MathAbs((long)dparam-object_y)<=4);
      if(!paired) cockpit_focus_owner=false;
      recent_object=false;
     }
   return(id!=CHARTEVENT_KEYDOWN || cockpit_focus_owner);
  }

string JPWFitText(const string text,const int available,const int font_size)
  {
   if(available<1) return("");
   if(!TextSetFont("Arial",-10*font_size,FW_NORMAL)) return("…");
   string shown=text;
   uint width=0,height=0;
   if(!TextGetSize(shown,width,height)) return("…");
   if((int)width<=available) return(shown);
   while(StringLen(shown)>1)
     {
      shown=StringSubstr(shown,0,StringLen(shown)-1);
      if(TextGetSize(shown+"…",width,height) && (int)width<=available) return(shown+"…");
     }
   return("…");
  }

void JPWViewMetric(const int index,const string title,const string value,
                   const string reason,const string detail,const JPW_VIEW_QUALITY quality)
  {
   g_cockpit_snapshot.metric[index].sample=g_metric_samples[index];
   g_cockpit_snapshot.metric[index].title=title;
   const bool envelope_current=JPWSampleDisplayValid(g_metric_samples[index],g_sample_context,GetTickCount64());
   g_cockpit_snapshot.metric[index].value=(envelope_current ? value : "N/A");
   g_cockpit_snapshot.metric[index].reason=(!envelope_current && quality!=JPW_VIEW_NA ?
      "Amostra inválida, vencida ou contexto alterado" : reason);
   g_cockpit_snapshot.metric[index].detail=detail;
   g_cockpit_snapshot.metric[index].quality=(envelope_current ? quality : JPW_VIEW_NA);
  }

string JPWStopRiskMoney(const double value)
  {
   if(!MathIsValidNumber(value) || value<0.0) return("N/A");
   if(value>0.0 && value<0.01) return("<0,01");
   string shown=StringFormat("%.2f",value);
   StringReplace(shown,".",",");
   return(shown);
  }

void JPWBuildPresentation(const string leverage_value,const string leverage_detail)
  {
   g_cockpit_snapshot.sequence=g_collection_sequence;
   g_cockpit_snapshot.symbol=_Symbol;
   g_cockpit_snapshot.account_key=g_sample_context;
   JPWViewMetric(0,"Leverage",leverage_value,g_leverage_reason,leverage_detail,g_leverage_quality);
   JPWViewMetric(1,"Floating P/L",g_floating_value,g_floating_reason,
                 g_floating_tooltip,g_floating_quality);
   JPWViewMetric(2,"Genesis SL",g_genesis_value,g_genesis_reason,
                 g_genesis_tooltip,g_genesis_quality);
   JPWViewMetric(3,"Raiz N 1W",g_raiz_value,g_raiz_reason,
                 g_raiz_tooltip,g_raiz_quality);
   JPWViewMetric(4,"Raiz N 2W",g_scale2_value,g_scale2_reason,
                 g_scale2_tooltip,g_scale2_quality);
   JPWViewMetric(5,"Stop risk",g_stop_value,g_stop_reason,
                 g_stop_detail,g_stop_quality);
   JPWGenetrixPresentMetric();
  }

void JPWClearPanel()
  {
   for(int i=0;i<g_panel_count;i++) ObjectDelete(0,g_panel_prefix+IntegerToString(i));
   ObjectDelete(0,g_panel_prefix+"RAIZ_DETAILS_BUTTON");
   ObjectDelete(0,g_panel_prefix+"HUD_BG");
   g_panel_count=0;
  }

void JPWRenderHUD()
  {
   if(g_panel_prefix=="") return;
   const int chart_width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int chart_height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(chart_width<80 || chart_height<40) { JPWClearPanel(); return; }
   const int pad=6;
   if(!TextSetFont("Arial",-10*InpFontSize,FW_NORMAL))
     { JPWClearPanel(); return; }
   const color chart_background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   JPWCockpitPrefs prefs=g_cockpit_prefs;
   if(g_raiz_details_open && g_raiz_tab==JPW_ROUTE_SETTINGS) prefs=g_cockpit_draft;
   const color foreground=JPWPanelTextColor(chart_background,InpFontColor);
   const color surface=JPWPanelSurface(chart_background);
   uint measured=0,text_height=0;
   if(!TextGetSize("Mg",measured,text_height) || text_height==0)
     { JPWClearPanel(); return; }
   const int font_height=(int)text_height;
   const int gap=(prefs.density==0 ? 2 : font_height/2+2);
   const int row_height=font_height+gap;
   const int button_font=(InpFontSize>12 ? 12 : InpFontSize);
   if(!TextSetFont("Arial",-10*button_font,FW_NORMAL))
     { JPWClearPanel(); return; }
   uint button_text_width=0,button_text_height=0;
   if(!TextGetSize("Genetrix",button_text_width,button_text_height))
     { JPWClearPanel(); return; }
   const int button_height=(int)button_text_height+8;
   const int button_width=(int)button_text_width+2*pad;
   if(!TextSetFont("Arial",-10*InpFontSize,FW_NORMAL))
     { JPWClearPanel(); return; }
   const int width=JPWPanelHUDReservedWidth(chart_width,font_height,pad,button_width);
   const int available=width-2*pad;
   if(width<button_width+2*pad || available<30) { JPWClearPanel(); return; }
   string shown[JPW_COCKPIT_METRIC_COUNT];
   string compact_title[JPW_COCKPIT_METRIC_COUNT]={"Lev","P/L","SL","RN1W","RN2W","Risk","Comp"};
   int visible=0;
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
      if(JPWCockpitVisible(prefs,i)) visible++;
   uint minimum_width=0,minimum_height=0;
   if(!TextGetSize("RN2W: Cockpit",minimum_width,minimum_height))
     { JPWClearPanel(); return; }
   // The list/summary decision may change with chart geometry or settings,
   // never with a quote, account value or transient quality label.
   const bool summary=(visible>0 &&
      (visible*row_height+button_height+3*pad>chart_height-8 ||
       (int)minimum_width>available));
   g_hud_summary=(summary || visible==0);
   g_hud_summary_source=-1;
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
     {
      shown[i]="";
      if(summary || !JPWCockpitVisible(prefs,i)) continue;
      JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
      const bool observer_missing=(i==5 && metric.quality==JPW_VIEW_NA &&
         g_stop_observer_presence==JPW_OBSERVER_NOT_CONFIRMED);
      shown[i]=(observer_missing ? "Stop risk: N/A · Check Observer" :
         (i==0 ? "JPW: " : "")+metric.title+" "+metric.value+
         " · "+JPWGenetrixMetricQuality(i,metric.quality));
      if(!TextGetSize(shown[i],measured,text_height) || (int)measured>available)
         shown[i]=(observer_missing ? "Risk: N/A · Check Observer" :
            compact_title[i]+": "+metric.value+" · "+JPWGenetrixMetricQuality(i,metric.quality));
      if(!TextGetSize(shown[i],measured,text_height) || (int)measured>available)
         shown[i]=compact_title[i]+": Cockpit";
     }
   if(summary)
     {
      for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++) shown[i]="";
      shown[0]="JPW · Open Cockpit";
      for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
         if(JPWCockpitVisible(prefs,i))
           { shown[0]=(i==5 && g_cockpit_snapshot.metric[i].quality==JPW_VIEW_NA &&
                         g_stop_observer_presence==JPW_OBSERVER_NOT_CONFIRMED ?
                         "Risk: N/A · Check Observer" :
                         compact_title[i]+": "+g_cockpit_snapshot.metric[i].value+
                         " · "+JPWGenetrixMetricQuality(i,g_cockpit_snapshot.metric[i].quality));
             g_hud_summary_source=i; break; }
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         { shown[0]="JPW · Cockpit"; g_hud_summary_source=-1; }
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         shown[0]="JPW";
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         shown[0]="";
     }
   if(visible==0)
     {
      shown[0]="JPW · Open Cockpit";
      TextGetSize(shown[0],measured,text_height);
      if((int)measured>available) { shown[0]="JPW · Cockpit"; g_hud_summary_source=-1; }
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         shown[0]="JPW";
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         shown[0]="";
     }
   const int active=(summary || visible==0 ? (shown[0]=="" ? 0 : 1) : visible);
   const int height=active*row_height+button_height+3*pad;
   JPWPanelRect hud;
   const bool lower=(prefs.corner==CORNER_LEFT_LOWER ||
                     prefs.corner==CORNER_RIGHT_LOWER);
   const bool right=(prefs.corner==CORNER_RIGHT_UPPER ||
                     prefs.corner==CORNER_RIGHT_LOWER);
   const int header_safe=(font_height*3+10>44 ? font_height*3+10 : 44);
   const int inset_y=(!lower && InpOffsetY<header_safe ? header_safe : InpOffsetY);
   if(!JPWPanelHUD(chart_width,chart_height,width,height,InpOffsetX,inset_y,right,lower,hud))
     { JPWClearPanel(); return; }
   const string bg=g_panel_prefix+"HUD_BG";
   if(ObjectFind(0,bg)<0 && !ObjectCreate(0,bg,OBJ_RECTANGLE_LABEL,0,0,0))
     { JPWClearPanel(); return; }
   ObjectSetInteger(0,bg,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,bg,OBJPROP_XDISTANCE,hud.x);
   ObjectSetInteger(0,bg,OBJPROP_YDISTANCE,hud.y);
   ObjectSetInteger(0,bg,OBJPROP_XSIZE,hud.width);
   ObjectSetInteger(0,bg,OBJPROP_YSIZE,hud.height);
   ObjectSetInteger(0,bg,OBJPROP_BGCOLOR,surface);
   ObjectSetInteger(0,bg,OBJPROP_COLOR,JPWPanelBorderColor(chart_background));
   ObjectSetInteger(0,bg,OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSetInteger(0,bg,OBJPROP_BACK,false);
   ObjectSetInteger(0,bg,OBJPROP_ZORDER,1);
   ObjectSetInteger(0,bg,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,bg,OBJPROP_HIDDEN,true);
   int y=hud.y+pad;
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
     {
      const string name=g_panel_prefix+IntegerToString(i);
      if(shown[i]=="") { ObjectDelete(0,name); continue; }
      if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_LABEL,0,0,0)) continue;
      ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
      ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
      ObjectSetInteger(0,name,OBJPROP_XDISTANCE,hud.x+pad);
      ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);
      ObjectSetInteger(0,name,OBJPROP_FONTSIZE,InpFontSize);
      ObjectSetInteger(0,name,OBJPROP_COLOR,foreground);
      ObjectSetInteger(0,name,OBJPROP_ZORDER,3);
      ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
      ObjectSetInteger(0,name,OBJPROP_HIDDEN,true);
      ObjectSetString(0,name,OBJPROP_FONT,"Arial");
      ObjectSetString(0,name,OBJPROP_TEXT,shown[i]);
      const int tip_index=(g_hud_summary && i==0 ? g_hud_summary_source : i);
      ObjectSetString(0,name,OBJPROP_TOOLTIP,
         (tip_index>=0 ? g_cockpit_snapshot.metric[tip_index].reason :
                         "Open Cockpit to see all metric cards.")+"\nClick for details.");
      y+=row_height;
     }
   g_panel_count=JPW_COCKPIT_METRIC_COUNT;
   const string button=g_panel_prefix+"RAIZ_DETAILS_BUTTON";
   if(ObjectFind(0,button)<0) ObjectCreate(0,button,OBJ_BUTTON,0,0,0);
   ObjectSetInteger(0,button,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,button,OBJPROP_XDISTANCE,hud.x+pad);
   ObjectSetInteger(0,button,OBJPROP_YDISTANCE,y+pad);
   ObjectSetInteger(0,button,OBJPROP_XSIZE,button_width);
   ObjectSetInteger(0,button,OBJPROP_YSIZE,button_height);
   ObjectSetInteger(0,button,OBJPROP_FONTSIZE,button_font);
   ObjectSetInteger(0,button,OBJPROP_COLOR,JPWPanelAccentColor(chart_background));
   ObjectSetInteger(0,button,OBJPROP_BGCOLOR,JPWPanelChromeSurface(chart_background));
   ObjectSetInteger(0,button,OBJPROP_BORDER_COLOR,JPWPanelBorderColor(chart_background));
   ObjectSetInteger(0,button,OBJPROP_ZORDER,4);
   ObjectSetInteger(0,button,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,button,OBJPROP_HIDDEN,true);
   ObjectSetString(0,button,OBJPROP_TEXT,"Genetrix");
   ObjectSetString(0,button,OBJPROP_TOOLTIP,"Open metric cards, data status and visual settings.");
  }

void JPWRenderCurrentDisplay()
  {
   // Pure presentation: no terminal financial reads, record reads or writers.
   if(g_panel_prefix=="") return;
   JPWBuildPresentation(g_panel_value,"Alavancagem = nocional bruto na moeda da conta / último equity informado pelo terminal. " + g_panel_status);
   JPWRenderHUD(); JPWRenderRaizDetails(); ChartRedraw(0);
  }

void JPWRender(const string value,const string state="")
  {
   // Cached values only. Collection/persistence is owned by the coordinator.
   JPWRenderCurrentDisplay();
  }

string JPWGenesisFormatPoints(const double points)
  {
   if(points>0.0 && points<0.01) return("<0,01 pts");
   return(DoubleToString(points,2)+" pts");
  }

string JPWRaizPercentText(const double percent)
  {
   if(percent>0.0 && percent<0.01) return("<0,01%");
   string shown=DoubleToString(percent,2);
   StringReplace(shown,".",",");
   return(shown+"%");
  }

string JPWNoTouchPercentText(const double percent)
  {
   string shown=DoubleToString(percent,3);
   StringReplace(shown,".",",");
   return(shown+"%");
  }

string JPWRaizPriceText(const double price,const int digits)
  {
   const string shown=DoubleToString(price,digits);
   if(price>0.0 && StringToDouble(shown)==0.0)
      return(StringFormat("%.8g",price));
   return(shown);
  }

string JPWRaizUI(const string suffix)
  { return(g_panel_prefix+"RAIZ_UI_"+suffix); }

string JPWActionObject(const int action)
  { return(JPWRaizUI("BUTTON_"+IntegerToString(action))); }

void JPWRaizPanelDestroy()
  {
   // Destroyed EDIT objects no longer own keyboard input; drafts are saved by the caller.
   g_editing_field=false;
   // Delete every object owned by this dialog, including new tab/table
   // controls. Iterate backwards because ObjectDelete changes enumeration.
   const string owned=g_panel_prefix+"RAIZ_UI_";
   for(int i=ObjectsTotal(0,-1,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,-1,-1);
      if(StringFind(name,owned)==0) ObjectDelete(0,name);
     }
   g_raiz_panel_built=false; g_focus_count=0;
  }

bool JPWRaizCreateLabel(const string suffix,const string value,
                        const int x,const int y,const int font_size=0)
  {
   const string name=JPWRaizUI(suffix);
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_LABEL,0,0,0)) return(false);
   const int font=(font_size>0 ? font_size : g_details_font);
   const string shown=JPWFitText(value,g_details_rect.x+g_details_rect.width-g_details_pad-x,font);
   // Visual role is explicit in owned object names, never inferred from a
   // translated financial message or from the metric's numeric value.
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   const bool secondary=(suffix=="PAGE" || suffix=="FEEDBACK" ||
      suffix=="STOP_PAGE" || suffix=="STOP_SCOPE" ||
      StringFind(suffix,"_REASON")>=0);
   const color ink=(secondary ? JPWPanelMutedText(background) :
      (StringFind(suffix,"_QUALITY")>=0 ? JPWPanelAccentColor(background) : g_details_text));
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,ink) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,font) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,3) &&
          ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) &&
          ObjectSetString(0,name,OBJPROP_FONT,"Arial") &&
          ObjectSetString(0,name,OBJPROP_TEXT,shown) &&
          ObjectSetString(0,name,OBJPROP_TOOLTIP,value));
  }

bool JPWCreateProtectedValue(const string suffix,const string value,const int x,
                              const int y,const int width,const int font_size=0)
  {
   const int font=(font_size>0 ? font_size : g_details_font);
   uint measured=0,height=0;
   if(!TextSetFont("Arial",-10*font,FW_NORMAL) ||
      !TextGetSize(value,measured,height)) return(false);
   const string shown=((int)measured<=width ? value : "Ver valor no detalhe");
   const bool made=JPWRaizCreateLabel(suffix,shown,x,y,font);
   if(made) ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,value);
   return(made);
  }

bool JPWRaizCreateSurface(const string suffix,const int x,const int y,
                          const int width,const int height,const color fill)
  {
   if(width<1 || height<1) return(false);
   const string name=JPWRaizUI(suffix);
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_RECTANGLE_LABEL,0,0,0)) return(false);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,width) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,height) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_border) &&
          ObjectSetInteger(0,name,OBJPROP_BORDER_TYPE,BORDER_FLAT) &&
          ObjectSetInteger(0,name,OBJPROP_BACK,false) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,2) &&
          ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true));
  }

bool JPWRaizCreateEdit(const int index,const int x,const int y,const int width)
  {
   const string name=JPWRaizUI("EDIT_"+IntegerToString(index));
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_EDIT,0,0,0)) return(false);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,width) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,g_details_control) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_details_font) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_text) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,g_details_surface) &&
          ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,g_details_border) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,4) &&
          ObjectSetInteger(0,name,OBJPROP_READONLY,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) &&
          ObjectSetString(0,name,OBJPROP_FONT,"Arial") &&
          ObjectSetString(0,name,OBJPROP_TEXT,g_raiz_fields[index]));
  }

void JPWFocusRegister(const int action)
  {
   for(int i=0;i<g_focus_count;i++) if(g_focus_actions[i]==action) return;
   if(g_focus_count<128) g_focus_actions[g_focus_count++]=action;
  }

void JPWFocusPaint()
  {
   for(int i=0;i<g_focus_count;i++)
     {
      const string name=JPWRaizUI("BUTTON_"+IntegerToString(g_focus_actions[i]));
      const bool card_title=(g_focus_actions[i]>=JPW_ACTION_CARD_FIRST &&
                            g_focus_actions[i]<JPW_ACTION_CARD_FIRST+JPW_COCKPIT_METRIC_COUNT);
      ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,
                       g_focus_actions[i]==g_focus_action ?
                       JPWPanelAccentColor((color)ChartGetInteger(0,CHART_COLOR_BACKGROUND)) :
                       (card_title ? g_details_card : g_details_border));
     }
  }

void JPWFocusStep(const bool backward)
  {
   if(g_focus_count==0) return;
   int current=-1;
   for(int i=0;i<g_focus_count;i++) if(g_focus_actions[i]==g_focus_action) current=i;
   current=(current<0 ? (backward ? g_focus_count-1 : 0) :
            (current+(backward ? g_focus_count-1 : 1))%g_focus_count);
   g_focus_action=g_focus_actions[current]; JPWFocusPaint(); ChartRedraw(0);
  }

bool JPWRaizCreateButton(const int index,const string value,
                          const int x,const int y,const int width)
  {
   JPWFocusRegister(index);
   const string name=JPWRaizUI("BUTTON_"+IntegerToString(index));
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_BUTTON,0,0,0)) return(false);
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   const bool primary=(index==JPW_ACTION_APPLY || index==JPW_ACTION_REFRESH ||
      (index==JPW_ACTION_LEGACY_APPLY &&
       (g_raiz_tab==JPW_ROUTE_JUSTIFY || g_raiz_tab==JPW_ROUTE_BIND ||
        g_raiz_tab==JPW_ROUTE_LEGACY_NF || g_raiz_tab==JPW_ROUTE_FACTOR)) ||
      (index==JPW_ACTION_SECONDARY &&
       (g_raiz_tab==JPW_ROUTE_EXPORT || g_raiz_tab==JPW_ROUTE_PROVENANCE)));
   const bool selected_factor=(g_raiz_tab==JPW_ROUTE_FACTOR &&
      ((index==JPW_ACTION_FACTOR_15 && g_factor_draft==1.5) ||
       (index==JPW_ACTION_FACTOR_18 && g_factor_draft==1.8)));
   const color ink=(primary ? JPWPanelPrimaryInk(background) :
      (selected_factor ? JPWPanelAccentColor(background) : g_details_text));
   const color fill=(primary ? JPWPanelAccentColor(background) :
      (selected_factor ? JPWPanelSelectedSurface(background) : g_details_card));
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,width) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,g_details_control) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_details_font) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,ink) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill) &&
          ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,g_details_border) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,4) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) &&
          ObjectSetString(0,name,OBJPROP_FONT,"Arial") &&
          ObjectSetString(0,name,OBJPROP_TEXT,JPWFitText(value,width-4,g_details_font)) &&
          ObjectSetString(0,name,OBJPROP_TOOLTIP,value));
  }

void JPWDetailsAppendLine(const string row,string &lines[])
  {
   if(row=="") return;
   const int count=ArraySize(lines);
   if(ArrayResize(lines,count+1)==count+1) lines[count]=row;
  }

void JPWDetailsWrap(const string paragraph,const int width,string &lines[])
  {
   string text=paragraph;
   StringReplace(text,"\n"," ");
   if(width<1 || !TextSetFont("Arial",-10*g_details_font,FW_NORMAL)) return;
   const int safe_width=(width>4 ? width-4 : width);
   string words[];
   const int count=StringSplit(text,' ',words);
   string row="";
   uint measured=0,height=0;
   for(int i=0;i<count;i++)
     {
      if(words[i]=="") continue;
      const string joined=(row=="" ? words[i] : row+" "+words[i]);
      if(TextGetSize(joined,measured,height) && (int)measured<=safe_width)
        { row=joined; continue; }
      JPWDetailsAppendLine(row,lines); row="";
      if(TextGetSize(words[i],measured,height) && (int)measured<=safe_width)
        { row=words[i]; continue; }
      // Preserve entire long numeric/provenance tokens by breaking only those
      // that cannot fit on an otherwise empty line.
      string segment="";
      for(int j=0;j<StringLen(words[i]);j++)
        {
         const string next=segment+StringSubstr(words[i],j,1);
         if(segment!="" && TextGetSize(next,measured,height) &&
            (int)measured>safe_width)
           { JPWDetailsAppendLine(segment,lines); segment=""; }
         segment+=StringSubstr(words[i],j,1);
        }
      row=segment;
     }
   JPWDetailsAppendLine(row,lines);
  }

bool JPWDetailsContextCurrent()
  {
   if(!g_raiz_draft_account_known || !g_account_known ||
      g_raiz_draft_symbol!=_Symbol || !JPWAccountsEqual(g_account,g_raiz_draft_account) ||
      g_cockpit_snapshot.symbol!=_Symbol || g_sample_context=="" ||
      g_cockpit_snapshot.account_key!=g_sample_context)
     {
      g_raiz_details_open=false; g_raiz_draft_account_known=false;
      g_raiz_draft_expected_id=""; JPWRaizPanelDestroy(); return(false);
     }
   return(true);
  }

string JPWPositionTicket(const ulong ticket)
  { return(StringFormat("%I64u",ticket)); }

string JPWPositionLeverageText(JPWPositionView &row)
  {
   if(!row.leverage_valid || row.quality==JPW_VIEW_NA) return("N/A");
   return((row.quality==JPW_VIEW_ESTIMATED ? "≈" : "")+JPWFormatLeverage(row.leverage));
  }

string JPWPositionRole(JPWPositionView &row)
  {
   if(g_positions_view.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      return("Net position");
   if(g_stop_genesis_identifier>0 && row.identifier==g_stop_genesis_identifier)
      return("Gênese · referência");
   if(g_stop_scope_valid && row.symbol==g_stop_scope_symbol &&
      (row.direction==POSITION_TYPE_BUY ? 1 : -1)==g_stop_scope_side)
     {
      int ordinal=1;
      for(int i=0;i<ArraySize(g_position_views);i++)
        {
         JPWPositionView other=g_position_views[i];
         if(other.identifier==row.identifier || other.symbol!=row.symbol || other.direction!=row.direction) continue;
         if(other.opened_msc==row.opened_msc) return("Posição · empate temporal");
         if(other.identifier==g_stop_genesis_identifier) continue;
         if(other.opened_msc<row.opened_msc ||
            (other.opened_msc==row.opened_msc && other.ticket<row.ticket)) ordinal++;
        }
      return("Defesa "+IntegerToString(ordinal)+" · inferida");
     }
   return("Posição");
  }

string JPWPositionRoleShort(JPWPositionView &row)
  {
   const string role=JPWPositionRole(row);
   if(StringFind(role,"Gênese")==0) return("Gênese");
   if(StringFind(role,"Defesa ")==0)
     {
      const int end=StringFind(role," ·");
      return("D"+StringSubstr(role,7,end-7));
     }
   if(StringFind(role,"Net")==0) return("Net");
   if(StringFind(role,"empate")>=0) return("Empate");
   return("Pos");
  }

bool JPWPositionRiskView(JPWPositionView &position,string &amount,string &percent,
                          string &state,string &reason)
  {
   amount="N/A"; percent="N/A"; state="N/A";
   reason="Sem amostra de Stops correspondente do observador";
   const bool historical=(!g_stop_ready && g_stop_last_ready);
   if(!g_stop_ready && !historical) return(false);
   JPWStopRiskSample sample;
   if(historical) sample=g_stop_last_sample; else sample=g_stop_sample;
   if(g_positions_view.context_key!=g_sample_context || sample.account_key!=g_positions_view.account_key)
     { reason="Contexto do observador diferente da leitura de posições"; return(false); }
   if(!position.entry_valid || !position.sl_valid)
     { reason="Entrada ou SL não conferido nesta leitura"; return(false); }
   const int count=(historical ? ArraySize(g_stop_last_rows) : ArraySize(g_stop_rows));
   for(int i=0;i<count;i++)
     {
      JPWStopRiskRow row;
      if(historical) row=g_stop_last_rows[i]; else row=g_stop_rows[i];
      if(row.kind!=JPW_STOP_RISK_POSITION || (ulong)row.ticket!=position.ticket ||
         row.identifier!=position.identifier || row.symbol!=position.symbol ||
         row.side!=(position.direction==POSITION_TYPE_BUY ? 1 : -1) ||
         row.volume!=position.volume || row.entry!=position.entry || row.sl!=position.sl) continue;
      state=(historical ? "LAST · NOT ACTIVE" : "Current");
      reason=row.reason;
      if(row.valid!=1 || !MathIsValidNumber(row.risk_money) || row.risk_money<0.0 ||
         !JPWFinitePositive(sample.balance))
        { if(!historical) state="N/A";
          if(reason=="") reason="Risco ou balance indisponível na amostra EA"; return(false); }
      amount=JPWStopRiskMoney(row.risk_money)+" "+sample.currency;
      percent=JPWFormatPercent(100.0*row.risk_money/sample.balance,false);
      return(true);
     }
   reason="Composição, entrada, volume ou SL divergem da amostra do observador";
   return(false);
  }

bool JPWPositionInView(JPWPositionView &row)
  {
   return(!g_positions_operation_only || (g_stop_scope_valid &&
      row.symbol==g_stop_scope_symbol &&
      (row.direction==POSITION_TYPE_BUY ? 1 : -1)==g_stop_scope_side));
  }

void JPWRenderPositionsTable(const int x,const int body_y,const int inner,
                              const int body_height,const int footer_y)
  {
   g_stop_button_count=0; g_positions_visible_rows=0; g_positions_total_rows=0;
   if(!JPWPositionsViewCurrent(g_sample_context,GetTickCount64()))
     {
      JPWRaizCreateLabel("POSITIONS_EMPTY","Posições: N/A · "+g_positions_view.reason,x,body_y);
      ObjectSetString(0,JPWRaizUI("POSITIONS_EMPTY"),OBJPROP_TOOLTIP,
                      "O catálogo é independente do EA. Atualizar solicita uma nova leitura consistente.");
      return;
     }
   if(g_positions_operation_only && !g_stop_scope_valid)
     {
      JPWRaizCreateLabel("POSITIONS_EMPTY","Operação não atribuída; use Conta para ver todas as posições.",x,body_y);
      return;
     }
   int indexes[];
   for(int i=0;i<ArraySize(g_position_views);i++)
     {
      JPWPositionView row=g_position_views[i];
      if(!JPWPositionInView(row)) continue;
      const int count=ArraySize(indexes); if(ArrayResize(indexes,count+1)!=count+1) return;
      int at=count;
      while(at>0 && (StringCompare(g_position_views[indexes[at-1]].symbol,row.symbol)>0 ||
            (g_position_views[indexes[at-1]].symbol==row.symbol &&
             (g_position_views[indexes[at-1]].direction>row.direction ||
              (g_position_views[indexes[at-1]].direction==row.direction &&
               (g_position_views[indexes[at-1]].opened_msc>row.opened_msc ||
                (g_position_views[indexes[at-1]].opened_msc==row.opened_msc &&
                 g_position_views[indexes[at-1]].ticket>row.ticket)))))))
        { indexes[at]=indexes[at-1]; at--; }
      indexes[at]=i;
     }
   g_positions_total_rows=ArraySize(indexes);
   if(g_positions_total_rows==0)
     {
      g_positions_scroll=0;
      JPWRaizCreateLabel("POSITIONS_EMPTY","Nenhuma posição informada pelo terminal nesta leitura.",x,body_y);
      return;
     }
   const int text_height=g_details_line-g_details_pad;
   const int gap=(text_height/12>2 ? text_height/12 : 2);
   // Measure every value before choosing columns; never truncate financial values.
   int widths[6]; for(int c=0;c<6;c++) widths[c]=0;
   const string headers[6]={"Ativo / papel","Ticket MT5","Lote","Leverage","Stop · EA","% balance"};
   TextSetFont("Arial",-10*g_details_font,FW_NORMAL);
   for(int c=0;c<6;c++)
     { uint w=0,h=0; if(TextGetSize(headers[c],w,h)) widths[c]=(int)w+2*gap; }
   for(int i=0;i<ArraySize(indexes);i++)
     {
      JPWPositionView row=g_position_views[indexes[i]];
      string amount="",percent="",state="",reason="";
      JPWPositionRiskView(row,amount,percent,state,reason);
      string values[6];
      values[0]=row.symbol+" "+(row.direction==POSITION_TYPE_BUY ? "BUY" : "SELL");
      values[1]=JPWPositionTicket(row.ticket);
      values[2]=DoubleToString(row.volume,row.volume_digits);
      values[3]=JPWPositionLeverageText(row);
      values[4]=amount+(state=="LAST · NOT ACTIVE" ? " LAST" : ""); values[5]=percent;
      for(int c=0;c<6;c++)
        { uint w=0,h=0; if(TextGetSize(values[c],w,h) && (int)w+2*gap>widths[c]) widths[c]=(int)w+2*gap; }
     }
   // The name may abbreviate; ticket, volume, leverage and money may not.
   int numeric_width=0; for(int c=1;c<6;c++) numeric_width+=widths[c];
   const int name_min=6*text_height;
   const bool columns=(numeric_width+name_min<=inner);
   if(columns) widths[0]=inner-numeric_width;
   JPWPositionsLayout layout; JPWPanelPositionsLayout(body_height,text_height,columns,layout);
   g_positions_visible_rows=layout.visible_rows;
   const int maximum=(g_positions_total_rows>layout.visible_rows ? g_positions_total_rows-layout.visible_rows : 0);
   g_positions_scroll=JPWPanelClamp(g_positions_scroll,0,maximum);
   const string scope=(g_positions_operation_only ? "Operação" : "Conta");
   const string risk_state=(g_stop_ready ? "Stops EA" : (g_stop_last_ready ? "Stops LAST · NOT ACTIVE" : "Stops: sem EA"));
   if(layout.summary_height>0)
     {
      const string summary=scope+" · "+IntegerToString(g_positions_total_rows)+" posições · "+
         JPWCockpitQualityText((JPW_VIEW_QUALITY)g_positions_view.quality)+" · "+risk_state;
      JPWRaizCreateLabel("POSITIONS_SUMMARY",JPWFitText(summary,inner,g_details_font),x,body_y);
      ObjectSetString(0,JPWRaizUI("POSITIONS_SUMMARY"),OBJPROP_TOOLTIP,
         summary+". Leverage = nocional da posição / equity da conta; não é margem. "+
         "O consolidado Stop risk continua limitado à operação atribuída.");
     }
   if(layout.visible_rows<1)
     {
      if(body_height>=g_details_control)
        {
         g_positions_visible_rows=1;
         g_positions_scroll=JPWPanelClamp(g_positions_scroll,0,g_positions_total_rows-1);
         const int index=indexes[g_positions_scroll];
         const string ticket=JPWPositionTicket(g_position_views[index].ticket);
         JPWRaizCreateButton(JPW_ACTION_STOP_ROW_FIRST,"Posição · "+ticket+" · detalhe",x,body_y,inner);
         ObjectSetString(0,JPWActionObject(JPW_ACTION_STOP_ROW_FIRST),OBJPROP_TOOLTIP,
            "Ticket "+ticket+". Texto ampliado: abra o detalhe ou role nesta mesma aba para outra posição.");
         g_position_button_row[0]=index;
         g_position_button_ticket[0]=g_position_views[index].ticket;
         g_position_button_identifier[0]=g_position_views[index].identifier; g_stop_button_count=1;
        }
      return;
     }
   int col_x[6]; col_x[0]=x; for(int c=1;c<6;c++) col_x[c]=col_x[c-1]+widths[c-1];
   const int header_y=body_y+layout.summary_height;
   if(columns && layout.header_height>0)
     {
      JPWRaizCreateSurface("POSITIONS_HEADER",x,header_y,inner,layout.header_height,g_details_chrome);
      for(int c=0;c<6;c++) JPWRaizCreateLabel("POSITIONS_HEAD_"+IntegerToString(c),headers[c],col_x[c]+gap,header_y);
     }
   const int table_y=body_y+layout.table_offset;
   for(int j=0;j<layout.visible_rows && g_positions_scroll+j<g_positions_total_rows;j++)
     {
      const int index=indexes[g_positions_scroll+j]; JPWPositionView row=g_position_views[index];
      const int y=table_y+j*layout.row_height;
      string amount="",percent="",state="",reason=""; JPWPositionRiskView(row,amount,percent,state,reason);
      const string ticket=JPWPositionTicket(row.ticket),volume=DoubleToString(row.volume,row.volume_digits);
      const string leverage=JPWPositionLeverageText(row);
      const string role=JPWPositionRole(row);
      const string tooltip=role+" · "+row.symbol+" "+(row.direction==POSITION_TYPE_BUY ? "BUY" : "SELL")+
         "; ticket "+ticket+"; volume "+volume+" lote; Leverage "+leverage+" · "+JPWCockpitQualityText((JPW_VIEW_QUALITY)row.quality)+
         "; "+row.reason+". Stop "+amount+" · "+percent+" balance · "+state+". "+reason;
      JPWRaizCreateButton(JPW_ACTION_STOP_ROW_FIRST+j,"",x,y,inner);
      ObjectSetInteger(0,JPWActionObject(JPW_ACTION_STOP_ROW_FIRST+j),OBJPROP_YSIZE,layout.row_height-gap);
      ObjectSetInteger(0,JPWActionObject(JPW_ACTION_STOP_ROW_FIRST+j),OBJPROP_BGCOLOR,
                         j%2==0 ? g_details_card : g_details_chrome);
      ObjectSetString(0,JPWActionObject(JPW_ACTION_STOP_ROW_FIRST+j),OBJPROP_TOOLTIP,tooltip);
      if(columns)
        {
         string values[6]; values[0]=JPWPositionRoleShort(row)+" · "+row.symbol+" "+(row.direction==POSITION_TYPE_BUY ? "B" : "S");
         values[1]=ticket; values[2]=volume; values[3]=leverage;
         values[4]=amount+(state=="LAST · NOT ACTIVE" ? " LAST" : ""); values[5]=percent;
         for(int c=0;c<6;c++)
           {
            const string suffix="POSITION_CELL_"+IntegerToString(j)+"_"+IntegerToString(c);
            JPWRaizCreateLabel(suffix,c==0 ? JPWFitText(values[c],widths[c]-2*gap,g_details_font) : values[c],
                               col_x[c]+gap,y);
            ObjectSetInteger(0,JPWRaizUI(suffix),OBJPROP_ZORDER,5);
            ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,tooltip);
           }
        }
      else
        {
         string lines[4];
         lines[0]=role+" · "+row.symbol+" "+(row.direction==POSITION_TYPE_BUY ? "BUY" : "SELL");
         lines[1]="Ticket "+ticket; lines[2]="Lote "+volume+" · Leverage "+leverage;
         lines[3]="Stop "+amount+" · "+percent+" balance"+(state=="LAST · NOT ACTIVE" ? " · LAST" : "");
         for(int l=0;l<4;l++)
           {
            const string suffix="POSITION_CELL_"+IntegerToString(j)+"_"+IntegerToString(l);
            if(l==0) JPWRaizCreateLabel(suffix,JPWFitText(lines[l],inner-2*gap,g_details_font),x+gap,y+l*(text_height+gap));
            else JPWCreateProtectedValue(suffix,lines[l],x+gap,y+l*(text_height+gap),inner-2*gap);
            ObjectSetInteger(0,JPWRaizUI(suffix),OBJPROP_ZORDER,5);
            ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,tooltip);
           }
        }
      g_position_button_row[j]=index; g_position_button_ticket[j]=row.ticket;
      g_position_button_identifier[j]=row.identifier; g_stop_button_count++;
     }
   const string count_text="Posições "+IntegerToString(g_positions_scroll+1)+"–"+
      IntegerToString(MathMin(g_positions_total_rows,g_positions_scroll+layout.visible_rows))+" de "+IntegerToString(g_positions_total_rows)+
      " · mesma aba";
   JPWRaizCreateLabel("STOP_PAGE",count_text,x,footer_y-g_details_line);
  }

void JPWRenderStopsTable(const int x,const int body_y,const int inner,
                         const int body_height,const int footer_y)
  {
   if(!g_stops_show_pending)
     { JPWRenderPositionsTable(x,body_y,inner,body_height,footer_y); return; }
   g_stop_button_count=0;
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
     {
      // The absence of an EA sample is a data state, regardless of font/DPI.
      const string cause=(g_stop_reason=="" ? g_stop_last_reason : g_stop_reason);
      JPWRaizCreateLabel("STOP_EMPTY","Stop risk: N/A · "+cause,x,body_y);
      if(body_height>=2*g_details_line)
         JPWRaizCreateLabel("STOP_HINT",
            "No mesmo MT5: Expert Advisors > JPWealth > Observer.",
            x,body_y+g_details_line);
      if(body_height>=3*g_details_line)
         JPWRaizCreateLabel("STOP_HINT_2",
            "Anexe a um gráfico e confira a aba Experts.",
            x,body_y+2*g_details_line);
      ObjectSetString(0,JPWRaizUI("STOP_EMPTY"),OBJPROP_TOOLTIP,
                      g_stop_detail+" "+g_stop_last_reason);
      return;
     }
   const string inactive_reason=(historical ?
      (g_stop_reason=="" ? "Observer not confirmed" : g_stop_reason) : "");
   g_stop_table_sample=sample; g_stop_table_historical=historical;
   ArrayResize(g_stop_table_rows,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++) g_stop_table_rows[i]=rows[i];
   if(sample.row_count==0 && ArraySize(rows)==0 &&
      sample.margin_mode==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING &&
      JPWFinitePositive(sample.balance))
     {
      JPWRaizCreateLabel("STOP_TOTAL","Stop risk: 0,00 "+sample.currency+
         " · 0,00% balance"+(historical ? " · LAST · NOT ACTIVE" : " · Current"),x,body_y);
      if(body_height>=2*g_details_line)
         JPWRaizCreateLabel("STOP_HINT",
            (historical ? "Inactive: "+inactive_reason :
             "Nenhuma posição ou pendente na geração completa do EA."),
            x,body_y+g_details_line);
      if(historical)
         ObjectSetString(0,JPWRaizUI("STOP_TOTAL"),OBJPROP_TOOLTIP,
                         "LAST · NOT ACTIVE. Motivo atual: "+inactive_reason);
      return;
     }
   string scope_symbol=(historical ? g_stop_last_scope_symbol : g_stop_scope_symbol);
   string provenance=(historical ? g_stop_last_provenance : g_stop_provenance);
   string reason=(historical ? g_stop_last_scope_reason : g_stop_reason);
   int scope_side=(historical ? g_stop_last_scope_side : g_stop_scope_side);
   const bool scope_ok=(historical ? g_stop_last_scope_valid : g_stop_scope_valid);
   const bool identity_stable=(g_account_known && g_sample_context!="");
   if(!scope_ok || !identity_stable)
     {
      if(!identity_stable) reason="Conta alterada durante a consulta";
      JPWRaizCreateLabel("STOP_EMPTY","Stop risk: N/A · atribuição indisponível",x,body_y);
      if(body_height>=2*g_details_line)
         JPWRaizCreateLabel("STOP_HINT",reason,x,body_y+g_details_line);
      if(identity_stable && g_stop_genesis_closed &&
         body_height>=2*g_details_line+g_details_control)
        {
         const string role="Gênese · "+(provenance=="Selected" ? "selected" :
                            "inferred")+" · closed";
         JPWRaizCreateButton(JPW_ACTION_STOP_ROW_FIRST,JPWFitText(role,inner-12,g_details_font),
                             x,body_y+2*g_details_line,inner);
         ObjectSetString(0,JPWActionObject(JPW_ACTION_STOP_ROW_FIRST),OBJPROP_TOOLTIP,
                         "Referência encerrada; posições posteriores não foram atribuídas.");
         g_stop_button_row[0]=-2;
         g_stop_button_role[0]=role;
         g_stop_button_count=1;
        }
      return;
     }
   double total=0.0,pct=0.0,positions=0.0,pending=0.0,additional=0.0;
   const bool complete=JPWStopRiskAggregate(sample,rows,scope_symbol,scope_side,
                                             total,pct,positions,pending,additional,reason);
   const bool netting=(sample.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
   const string data_state=(historical ? "LAST · NOT ACTIVE" :
                            (complete ? "Current" : "N/A"));
   const string total_text=(complete ? JPWStopRiskMoney(total)+" "+sample.currency+
                             " · "+JPWFormatPercent(pct,false)+" balance" : "N/A");
   const string parts=(complete ? "Open "+JPWStopRiskMoney(positions)+
      " + Pending "+JPWStopRiskMoney(pending)+"; market→SL "+
      (additional>=0.0 ? JPWStopRiskMoney(additional) : "N/A")+" "+sample.currency :
      "Total recusado: "+reason);
   int excluded=0;
   for(int i=0;i<ArraySize(rows);i++)
      if(rows[i].symbol!=scope_symbol || rows[i].side!=scope_side) excluded++;
   const string scope=scope_symbol+" "+(scope_side>0 ? "BUY" : "SELL")+
      " · símbolo + direção inferidos · "+provenance+
      (excluded>0 ? " · "+IntegerToString(excluded)+
      " outro(s) símbolo/direção fora" : "");
   int indexes[];
   for(int i=0;i<ArraySize(rows);i++)
     {
      if(rows[i].symbol!=scope_symbol || rows[i].side!=scope_side ||
         rows[i].kind!=(g_stops_show_pending ? JPW_STOP_RISK_PENDING :
                                           JPW_STOP_RISK_POSITION)) continue;
      const int n=ArraySize(indexes);
      ArrayResize(indexes,n+1);
      int at=n;
      while(at>0 && (rows[indexes[at-1]].opened_msc>rows[i].opened_msc ||
            (rows[indexes[at-1]].opened_msc==rows[i].opened_msc &&
             rows[indexes[at-1]].ticket>rows[i].ticket)))
        { indexes[at]=indexes[at-1]; at--; }
      indexes[at]=i;
     }
   if(!g_stops_show_pending && !g_stop_genesis_closed && !netting)
      for(int i=0;i<ArraySize(indexes);i++)
         if(rows[indexes[i]].identifier==g_stop_genesis_identifier)
           {
            const int genesis=indexes[i];
            for(int j=i;j>0;j--) indexes[j]=indexes[j-1];
            indexes[0]=genesis;
            break;
           }
   const int closed_extra=(!g_stops_show_pending && g_stop_genesis_closed && !netting ? 1 : 0);
   const int count=ArraySize(indexes)+closed_extra;
   bool horizontal_values=(inner>2*g_details_control+g_details_pad);
   const int value_inset=(g_details_pad>4 ? g_details_pad : 4);
   const int value_width=(inner>2*value_inset ? inner-2*value_inset : inner);
   const int column_width=(value_width-g_details_pad)/2;
   if(!TextSetFont("Arial",-10*g_details_font,FW_NORMAL)) horizontal_values=false;
   for(int i=0;i<ArraySize(indexes) && horizontal_values;i++)
     {
      JPWStopRiskRow measured_row=rows[indexes[i]];
      string measured_amount="N/A",measured_percent="N/A balance";
      if(measured_row.valid==1 && MathIsValidNumber(measured_row.risk_money) &&
         measured_row.risk_money>=0.0 && JPWFinitePositive(sample.balance))
        {
         measured_amount=JPWStopRiskMoney(measured_row.risk_money)+" "+sample.currency;
         measured_percent=JPWFormatPercent(100.0*measured_row.risk_money/
                                           sample.balance,false)+" balance";
        }
      uint amount_width=0,percent_width=0,text_height=0;
      if(!TextGetSize(measured_amount,amount_width,text_height) ||
         !TextGetSize(measured_percent,percent_width,text_height) ||
         (int)amount_width>column_width || (int)percent_width>column_width)
         horizontal_values=false;
     }
   JPWStopsLayout layout;
   JPWPanelStopsLayout(body_height,g_details_line,g_details_control,
                       g_details_pad,horizontal_values,count>0,layout);
   if(layout.summary_lines>0)
     {
      JPWCreateProtectedValue("STOP_TOTAL","Stop risk: "+total_text+
         " · "+data_state,x,body_y,inner);
      ObjectSetString(0,JPWRaizUI("STOP_TOTAL"),OBJPROP_TOOLTIP,
         "Stop risk: "+total_text+" · "+data_state+". "+reason);
     }
   if(layout.summary_lines>1)
     {
      JPWCreateProtectedValue("STOP_PARTS",parts,x,body_y+g_details_line,inner);
      ObjectSetString(0,JPWRaizUI("STOP_PARTS"),OBJPROP_TOOLTIP,parts+
         ". Market→SL é separado e exclui pendentes.");
     }
   if(layout.summary_lines>2)
     {
      const string scope_line=(historical ? "Inactive: "+inactive_reason : scope);
      JPWRaizCreateLabel("STOP_SCOPE",
         JPWFitText(scope_line,inner,g_details_font),x,body_y+2*g_details_line);
      ObjectSetString(0,JPWRaizUI("STOP_SCOPE"),OBJPROP_TOOLTIP,scope+
         (historical ? ". Motivo atual: "+inactive_reason : "")+
         ". Outra tese no mesmo par e direção pode estar incluída. " +
         "Antiguidade não certifica a tese nem a função de Defesa.");
     }
   const int table_y=body_y+layout.table_offset;
   if(count==0)
     {
      if(table_y+g_details_line<=body_y+body_height)
         JPWRaizCreateLabel("STOP_NO_ROWS",g_stops_show_pending ?
            "Nenhuma pendente atribuída; total só é zero se confirmado." :
            "Nenhuma posição aberta atribuída.",x,table_y);
      return;
     }
   if(layout.rows_per_page<1)
     {
      if(body_height>=g_details_control)
         JPWRaizCreateButton(JPW_ACTION_CARD_FIRST+5,"Stop risk · detalhe",
                             x,body_y,inner);
      return;
     }
   const int rows_per_page=layout.rows_per_page;
   const int row_height=layout.row_height;
   const int pages=JPWPanelPageCount(count,rows_per_page);
   g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
   for(int j=0;j<rows_per_page && g_cockpit_page*rows_per_page+j<count;j++)
     {
      const int ordinal=g_cockpit_page*rows_per_page+j;
      const int row_index=(ordinal<closed_extra ? -2 : indexes[ordinal-closed_extra]);
      string role="",amount="N/A",percent="N/A";
      if(row_index==-2)
        role="Gênese · "+(provenance=="Selected" ? "selected" : "inferred")+" · closed";
      else
        {
         JPWStopRiskRow row=rows[row_index];
         role=(g_stops_show_pending ? "Pending "+IntegerToString(ordinal+1) :
              (netting ? "Net position · aggregate" :
              (row.identifier==g_stop_genesis_identifier ?
               "Gênese · "+(provenance=="Selected" ? "selected" : "inferred") :
               "Defesa "+IntegerToString(ordinal)+" · inferred")));
         if(row.valid==1 && MathIsValidNumber(row.risk_money) &&
            row.risk_money>=0.0 && JPWFinitePositive(sample.balance))
           { amount=JPWStopRiskMoney(row.risk_money)+" "+sample.currency;
             percent=JPWFormatPercent(100.0*row.risk_money/sample.balance,false); }
        }
      const string caption=role+" · "+amount+" · "+percent;
      JPWRaizCreateButton(JPW_ACTION_STOP_ROW_FIRST+j,role,
                          x,table_y+j*row_height,inner);
      if(layout.value_lines>0)
        {
         const string row_surface="STOP_ROW_BG_"+IntegerToString(j);
         JPWRaizCreateSurface(row_surface,x,table_y+j*row_height+g_details_control,
                              inner,layout.value_lines*g_details_line,g_details_card);
         // Decorative row backgrounds must not steal the detail button's click.
         ObjectSetInteger(0,JPWRaizUI(row_surface),OBJPROP_ZORDER,1);
        }
      if(layout.value_lines==1)
        {
         JPWCreateProtectedValue("STOP_AMOUNT_"+IntegerToString(j),amount,
            x+value_inset,table_y+j*row_height+g_details_control,column_width);
         JPWCreateProtectedValue("STOP_PERCENT_"+IntegerToString(j),percent+" balance",
            x+value_inset+column_width+g_details_pad,
            table_y+j*row_height+g_details_control,column_width);
        }
      else if(layout.value_lines==2)
        {
         JPWCreateProtectedValue("STOP_AMOUNT_"+IntegerToString(j),amount,
            x+value_inset,table_y+j*row_height+g_details_control,value_width);
         JPWCreateProtectedValue("STOP_PERCENT_"+IntegerToString(j),percent+" balance",
            x+value_inset,table_y+j*row_height+g_details_control+g_details_line,value_width);
        }
      ObjectSetString(0,JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_STOP_ROW_FIRST+j)),
                      OBJPROP_TOOLTIP,caption+". Clique para origem, volume, entrada e SL.");
      g_stop_button_row[j]=row_index;
      g_stop_button_role[j]=role;
      g_stop_button_count++;
     }
   const string page_text=(g_stops_show_pending ? "Pendentes" : "Posições")+
                       " · "+IntegerToString(g_cockpit_page+1)+"/"+
                       IntegerToString(pages)+
                       (historical ? " · LAST · "+inactive_reason : "");
   JPWRaizCreateLabel("STOP_PAGE",JPWFitText(page_text,inner,g_details_font),
                      x,footer_y-g_details_line);
   if(historical)
      ObjectSetString(0,JPWRaizUI("STOP_PAGE"),OBJPROP_TOOLTIP,
                      "Última amostra, não ativa. Motivo atual: "+inactive_reason);
  }

void JPWRenderCockpit()
  {
   g_stop_button_count=0;
   const int chart_width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int chart_height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   g_details_font=InpCockpitFontSize;
   uint text_width=0,text_height=0;
   if(!TextSetFont("Arial",-10*g_details_font,FW_NORMAL) ||
      !TextGetSize("Mg",text_width,text_height) || text_height==0 ||
      !JPWPanelCockpit(chart_width,chart_height,1040,760,g_details_rect)) return;
   // Large measured text needs more physical height; keep the requested font,
   // grow only the viewport, and let chart bounds remain the final limit.
   if(text_height>32)
      JPWPanelCockpit(chart_width,chart_height,1040,
                      MathMax(760,24*(int)text_height),g_details_rect);
   g_details_pad=((int)text_height/2>6 ? (int)text_height/2 : 6);
   g_details_line=(int)text_height+g_details_pad;
   g_details_control=(int)text_height+2*g_details_pad;
   const color chart_background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   g_details_text=JPWPanelInk(chart_background);
   g_details_surface=JPWPanelWindowSurface(chart_background);
   g_details_chrome=JPWPanelChromeSurface(chart_background);
   g_details_card=JPWPanelCardSurface(chart_background);
   g_details_border=JPWPanelBorderColor(chart_background);
   const int left=g_details_rect.x,top=g_details_rect.y;
   const int x=left+g_details_pad,inner=g_details_rect.width-2*g_details_pad;
   const string bg=JPWRaizUI("BG");
   if(ObjectFind(0,bg)<0 && !ObjectCreate(0,bg,OBJ_RECTANGLE_LABEL,0,0,0)) return;
   ObjectSetInteger(0,bg,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,bg,OBJPROP_XDISTANCE,left);
   ObjectSetInteger(0,bg,OBJPROP_YDISTANCE,top);
   ObjectSetInteger(0,bg,OBJPROP_XSIZE,g_details_rect.width);
   ObjectSetInteger(0,bg,OBJPROP_YSIZE,g_details_rect.height);
   ObjectSetInteger(0,bg,OBJPROP_BGCOLOR,g_details_surface);
   ObjectSetInteger(0,bg,OBJPROP_COLOR,g_details_border);
   ObjectSetInteger(0,bg,OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSetInteger(0,bg,OBJPROP_BACK,false);
   ObjectSetInteger(0,bg,OBJPROP_ZORDER,1);
   ObjectSetInteger(0,bg,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,bg,OBJPROP_HIDDEN,true);
   const int min_structure=2*g_details_control+g_details_line+4*g_details_pad;
   if(g_details_rect.height<min_structure || inner<110)
     {
      const int room=g_details_rect.height-2*g_details_pad;
      const int close_height=(room<g_details_control ? room : g_details_control);
      if(room>g_details_control+g_details_line)
         JPWRaizCreateLabel("TITLE",JPW_PRODUCT_NAME+" · amplie o gráfico",x,top+g_details_pad);
      const int close_width=(inner<g_details_control ? inner : g_details_control);
      if(close_height>0 && close_width>0)
        {
         JPWRaizCreateButton(JPW_ACTION_CLOSE,"×",x,
            top+g_details_rect.height-g_details_pad-close_height,close_width);
         ObjectSetInteger(0,JPWActionObject(JPW_ACTION_CLOSE),OBJPROP_YSIZE,close_height);
        }
      g_raiz_panel_built=true;
      return;
     }
   // Stable visual regions separate orientation, content and actions. They are
   // presentation objects only; all metric values still come from the snapshot.
   JPWRaizCreateSurface("HEADER",left+1,top+1,g_details_rect.width-2,
                         g_details_line+g_details_pad-2,g_details_chrome);
   const string section=(g_raiz_tab==JPW_SIGNAL_ROUTE ? "Preparar mensagem" :
      (g_raiz_tab==JPW_ROUTE_OVERVIEW ? "Visão geral" :
      (g_raiz_tab==JPW_ROUTE_METRIC ? g_cockpit_snapshot.metric[g_cockpit_selected].title :
      (g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES ? "Ciclos contábeis" :
      (g_raiz_tab==JPW_ROUTE_PROVENANCE ? "Estado dos dados" :
      (g_raiz_tab==JPW_ROUTE_SETTINGS ? "Ajustes" :
      (g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW ? "Stops" :
      (g_raiz_tab==JPW_ROUTE_RAIZN ? "Raiz N" : "Sistema"))))))));
   JPWGenetrixHeader(JPWRaizUI("BRAND_LOGO"),JPWRaizUI("TITLE"),
      x,top+g_details_pad,inner-g_details_control-g_details_pad,g_details_line,
      g_details_font+2,g_details_text,JPWPanelDarkBackground(chart_background),_Symbol+" · "+section,4);
   const int nav_y=top+g_details_pad+g_details_line;
   const string tabs[5]={"Visão geral","Stops","Raiz N","Sistema","Ajustes"};
   const string short_tabs[5]={"Geral","Stops","Raiz N","Sistema","Ajustes"};
   const bool stacked=(inner<370);
   const int nav_columns=(stacked ? 3 : 5);
   const int nav_width=(inner-(nav_columns-1)*g_details_pad)/nav_columns;
   for(int i=0;i<5;i++)
     {
      const int col=(stacked ? i%3 : i),row=(stacked ? i/3 : 0);
      const int width=(stacked && row==1 ? (inner-g_details_pad)/2 : nav_width);
      const int nav_x=x+(stacked && row==1 ? col*(width+g_details_pad) : col*(nav_width+g_details_pad));
      JPWRaizCreateButton(JPW_ACTION_TAB_FIRST+i,(nav_width<82 ? short_tabs[i] : tabs[i]),
                          nav_x,nav_y+row*(g_details_control+g_details_pad),width);
      const bool active=(i==0 ? (g_raiz_tab==JPW_ROUTE_OVERVIEW || g_raiz_tab==JPW_ROUTE_METRIC) :
         (i==1 ? (g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW) :
         (i==2 ? g_raiz_tab==JPW_ROUTE_RAIZN :
         (i==3 ? (g_raiz_tab==JPW_ROUTE_SYSTEM || g_raiz_tab==JPW_ROUTE_PROVENANCE ||
                   g_raiz_tab==JPW_ROUTE_EXPORT) : g_raiz_tab==JPW_ROUTE_SETTINGS))));
      if(active)
        {
         const string tab_button=JPWActionObject(JPW_ACTION_TAB_FIRST+i);
         ObjectSetInteger(0,tab_button,OBJPROP_BGCOLOR,JPWPanelSelectedSurface(chart_background));
         ObjectSetInteger(0,tab_button,OBJPROP_COLOR,JPWPanelAccentColor(chart_background));
         const int tab_y=nav_y+row*(g_details_control+g_details_pad);
         const int marker_height=(g_details_pad/2>2 ? g_details_pad/2 : 2);
         JPWRaizCreateSurface("NAV_ACTIVE",nav_x,tab_y+g_details_control-marker_height,
                              width,marker_height,JPWPanelAccentColor(chart_background));
         ObjectSetInteger(0,JPWRaizUI("NAV_ACTIVE"),OBJPROP_COLOR,JPWPanelAccentColor(chart_background));
         ObjectSetInteger(0,JPWRaizUI("NAV_ACTIVE"),OBJPROP_ZORDER,1);
        }
     }
   ObjectSetString(0,JPWActionObject(JPW_ACTION_TAB_FIRST),OBJPROP_TOOLTIP,
                   "Teclas 1–7: cartões; setas: páginas; Esc: fechar.");
   const int close_size=(g_details_control>24 ? g_details_control : 24);
   // The close button stays visible even when content has to paginate.
   JPWRaizCreateButton(JPW_ACTION_HEADER_CLOSE,"×",left+g_details_rect.width-g_details_pad-close_size,
                       top+g_details_pad,close_size);
   const int body_y=nav_y+(stacked ? 2 : 1)*(g_details_control+g_details_pad);
   const int footer_y=top+g_details_rect.height-g_details_pad-g_details_control;
   const int reserved=(g_raiz_tab==JPW_ROUTE_SETTINGS || (g_raiz_tab==JPW_ROUTE_OVERVIEW && g_cockpit_pref_invalid) ?
                       2*g_details_line : g_details_line);
   const int body_height=footer_y-g_details_pad-body_y-reserved;
   const int footer_button=(inner-2*g_details_pad)/3;
   JPWRaizCreateSurface("FOOTER",left+1,footer_y-g_details_line-g_details_pad/2,
                         g_details_rect.width-2,
                         g_details_rect.y+g_details_rect.height-footer_y+
                         g_details_line+g_details_pad/2-2,g_details_chrome);
   if(body_height<g_details_control || footer_button<35)
     {
      if(body_y+g_details_line<footer_y)
         JPWRaizCreateLabel("FEEDBACK","Amplie o gráfico para ver o cockpit",x,body_y);
      JPWRaizCreateButton(JPW_ACTION_CLOSE,"Fechar",x,footer_y,inner);
      g_raiz_panel_built=true;
      return;
     }
   if(g_raiz_tab==JPW_SIGNAL_ROUTE)
     {
      JPWSignalRenderBody(x,body_y,inner,body_height,footer_y);
      g_raiz_panel_built=true; JPWFocusPaint(); return;
     }
   if(g_raiz_tab==JPW_ROUTE_OVERVIEW)
     {
      const int columns=(inner>=600 ? 2 : 1);
      const int card_width=(inner-(columns-1)*g_details_pad)/columns;
      const int card_height=g_details_control+3*g_details_line+2*g_details_pad;
      const int card_stride=card_height+g_details_pad;
      const int card_inset=(g_details_pad>4 ? g_details_pad : 4);
      const int card_inner=card_width-2*card_inset;
      const int rows=(body_height+g_details_pad)/card_stride;
      const int capacity=(rows>0 ? rows*columns : 1);
      const int pages=(JPW_COCKPIT_METRIC_COUNT+capacity-1)/capacity;
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
      for(int j=0;j<capacity && g_cockpit_page*capacity+j<JPW_COCKPIT_METRIC_COUNT;j++)
        {
         const int i=g_cockpit_page*capacity+j;
         const int cx=x+(j%columns)*(card_width+g_details_pad);
         const int y=body_y+(j/columns)*card_stride;
         JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
         if(rows>0)
            JPWRaizCreateSurface("CARD_BG_"+IntegerToString(i),cx,y,
                                 card_width,card_height,g_details_card);
         JPWRaizCreateButton(JPW_ACTION_CARD_FIRST+i,
                             metric.title+(rows==0 ? " · detalhe" : "  ›"),
                             (rows>0 ? cx+card_inset : cx),
                             (rows>0 ? y+card_inset : y),
                             (rows>0 ? card_inner : card_width));
         if(rows==0)
           {
            if(body_height>=g_details_control+g_details_line)
               JPWRaizCreateLabel("SMALL_CARD","Amplie para ver o cartão completo",cx,y+g_details_control);
            continue;
           }
         const string suffix="CARD_"+IntegerToString(i);
         const int value_y=y+g_details_control+card_inset+g_details_pad/2;
         const int state_y=value_y+g_details_line;
         JPWCreateProtectedValue(suffix+"_VALUE",metric.value,cx+card_inset,
                                  value_y,card_inner,g_details_font+2);
         JPWRaizCreateSurface(suffix+"_STATE_BG",cx+card_inset,state_y,
                              card_inner,g_details_line,g_details_chrome);
         // Keep the existing CARD_BG / QUALITY click routes in precedence.
         ObjectSetInteger(0,JPWRaizUI(suffix+"_STATE_BG"),OBJPROP_ZORDER,1);
         JPWRaizCreateLabel(suffix+"_QUALITY",JPWGenetrixMetricQuality(i,metric.quality),
                              cx+card_inset+g_details_pad/2,state_y);
         JPWRaizCreateLabel(suffix+"_REASON",JPWFitText(metric.reason,card_inner,g_details_font),
                              cx+card_inset,value_y+2*g_details_line);
         ObjectSetString(0,JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_CARD_FIRST+i)),
                         OBJPROP_TOOLTIP,"Fórmula, insumos, proveniência e limites desta métrica.");
        }
      JPWRaizCreateLabel("PAGE","Cartões "+IntegerToString(g_cockpit_page+1)+"/"+
                          IntegerToString(pages),x,footer_y-g_details_line);
      if(g_cockpit_pref_invalid)
         JPWRaizCreateLabel("FEEDBACK","Preferência visual inválida · abra Ajustes",
                            x,footer_y-2*g_details_line);
     }
   else if(g_raiz_tab==JPW_ROUTE_STOPS)
     {
      JPWRenderStopsTable(x,body_y,inner,body_height,footer_y);
     }
   else if(g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES)
     {
      g_genetrix_cycle_button_count=0;
      const int stride=g_details_control+2*g_details_line+g_details_pad;
      const int rows=JPWPanelClamp(body_height/stride,1,16);
      const int total=(g_genetrix_ledger_available ? ArraySize(g_genetrix_cycles) : 0);
      const int pages=JPWPanelPageCount(total,rows);
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
      if(total==0)
         JPWRaizCreateLabel("LEDGER_EMPTY",JPWFitText("Ciclos indisponíveis · "+g_genetrix_ledger_reason,inner,g_details_font),x,body_y);
      for(int j=0;j<rows && g_cockpit_page*rows+j<total;j++)
        {
         const int i=g_cockpit_page*rows+j;
         JPWLedgerCycle cycle=g_genetrix_cycles[i];
         const int y=body_y+j*stride;
         g_genetrix_cycle_button_id[j]=cycle.cycle_id;
         g_genetrix_cycle_button_count=j+1;
         const string caption=(cycle.cycle_id==g_genetrix_selected_cycle ? "✓ " : "")+
            JPWGenetrixCycleScope(cycle)+" · "+(cycle.started_msc>0 ?
            TimeToString((datetime)(cycle.started_msc/1000),TIME_DATE|TIME_MINUTES) : "origem sem horário");
         JPWRaizCreateButton(JPW_ACTION_LEDGER_CYCLE_FIRST+j,caption,x,y,inner);
         if(body_height>=stride)
           {
            JPWRaizCreateLabel("LEDGER_STATE_"+IntegerToString(j),JPWFitText(JPWGenetrixCycleState(cycle)+" · "+
               JPWGenetrixCycleQuality(g_genetrix_view,cycle,GetTickCount64()),inner,g_details_font),x,y+g_details_control);
            JPWRaizCreateLabel("LEDGER_SCOPE_"+IntegerToString(j),JPWFitText("Gênese "+
               JPWGenetrixGenesisLabel(cycle)+" · "+
               IntegerToString(cycle.open_positions)+" posições / "+IntegerToString(cycle.pending_orders)+
               " pendentes",inner,g_details_font),x,y+g_details_control+g_details_line);
           }
        }
      JPWRaizCreateLabel("PAGE","Ciclos "+IntegerToString(g_cockpit_page+1)+"/"+IntegerToString(pages)+
         " · seleção visual",x,footer_y-g_details_line);
     }
   else if(g_raiz_tab==JPW_ROUTE_SETTINGS)
     {
      string names[JPW_COCKPIT_METRIC_COUNT]={"Leverage","Floating P/L","Genesis SL","Raiz N 1W","Raiz N 2W","Stop risk","Flutuante compensado"};
      const int row_height=g_details_control+g_details_pad;
      const int total=JPW_COCKPIT_METRIC_COUNT+2;
      const int rows=(body_height/row_height>0 ? body_height/row_height : 1);
      const int pages=(total+rows-1)/rows;
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
      for(int j=0;j<rows && g_cockpit_page*rows+j<total;j++)
        {
         const int item=g_cockpit_page*rows+j;
         string caption="";
         int button_id=0;
         if(item<JPW_COCKPIT_METRIC_COUNT)
           { button_id=60+item; caption=(JPWCockpitVisible(g_cockpit_draft,item) ? "✓ " : "○ ")+names[item]; }
         else if(item==JPW_COCKPIT_METRIC_COUNT)
           { button_id=30; caption="Canto: "+JPWCockpitCornerName(g_cockpit_draft.corner); }
         else
           { button_id=31; caption="Densidade: "+(g_cockpit_draft.density==0 ? "Compacta" : "Normal"); }
         JPWRaizCreateButton(button_id,caption,x,body_y+j*row_height,inner);
        }
      const string notice=(g_cockpit_pref_invalid ? g_cockpit_pref_notice :
         "Prévia imediata no gráfico. Aplicar salva neste gráfico; Cancelar restaura.");
      JPWRaizCreateLabel("FEEDBACK",notice,x,footer_y-2*g_details_line);
      JPWRaizCreateLabel("PAGE","Opções "+IntegerToString(g_cockpit_page+1)+"/"+
                          IntegerToString(pages),
                          x,footer_y-g_details_line);
     }
   else
     {
      string lines[];
      if(g_raiz_tab==JPW_ROUTE_METRIC)
        {
         const int i=g_cockpit_selected;
         JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
         JPWDetailsWrap(metric.title+": "+metric.value+" · "+JPWGenetrixMetricQuality(i,metric.quality),inner,lines);
         JPWDetailsWrap("Estado: "+metric.reason,inner,lines);
         JPWDetailsWrap("Amostra "+IntegerToString(metric.sample.id)+" · "+metric.sample.source+
            " · unidade "+metric.sample.unit+" · código "+IntegerToString((int)metric.sample.reason_code)+
            ". Observada em "+TimeToString((datetime)metric.sample.observed_utc,TIME_DATE|TIME_SECONDS)+
            " UTC (computador). Redesenhar não cria outra amostra.",inner,lines);
         string formulas[JPW_COCKPIT_METRIC_COUNT]={"Nocional bruto de todas as posições / último equity informado pelo terminal.",
           "100 × lucro flutuante / saldo.","Distância da cotação Bid (compra) ou Ask (venda) ao SL local da referência; percentual do preço.",
           "100 × ATR(55,H4) × √N(1W) × F / preço médio do mesmo tick.",
           "100 × ATR(55,H4) × √N(2W) × F / preço médio do mesmo tick.",
           "Soma do risco de posições abertas (execução até SL, piso zero) e reservas de pendentes ampliadoras atribuídas. Percentual informativo sobre balance atual.",
           "NET realizado desde a origem inferida + flutuante NET remanescente, incluindo custos atribuíveis sem duplicação. 100 × compensado / saldo da amostra."};
         JPWDetailsWrap("Fórmula: "+formulas[i],inner,lines);
         JPWDetailsWrap("Insumos, origem e horário: "+metric.detail,inner,lines);
         if(i==3 || i==4)
            JPWDetailsWrap("Limite: escala diagnóstica; Current qualifica os dados, não homologa P-21 nem decide stop, lote ou entrada.",inner,lines);
         if(i==2)
            JPWDetailsWrap("Limite: SL local sem confirmação de execução; referência inferida não certifica a Gênese.",inner,lines);
         if(i==5)
            JPWDetailsWrap("Limite: não é Risco Comprometido, limite de fase ou perda máxima garantida. Custos, perdas realizadas, gaps e slippage ficam fora.",inner,lines);
         if(i==6)
           {
            const int selected=JPWGenetrixSelectedIndex();
            if(selected>=0 && g_genetrix_ledger_available)
              {
               JPWLedgerCycle cycle=g_genetrix_cycles[selected];
               const string currency=g_genetrix_view.currency;
               const bool known=cycle.amount_valid;
               const bool partial=(cycle.partial || !cycle.history_complete || !cycle.costs_complete ||
                  !g_genetrix_view.history_complete || !g_genetrix_view.costs_complete);
               JPWDetailsWrap("Escopo: "+JPWGenetrixCycleScope(cycle)+" · "+JPWGenetrixCycleState(cycle)+
                  ". Seleção apenas visual; nenhuma conta operacional é trocada.",inner,lines);
               JPWDetailsWrap("Origem contábil "+JPWGenetrixGenesisLabel(cycle)+
                  "; não certifica tese, flag GÊNESE ou dupla confirmação. O ciclo subsiste com pendentes mesmo sem posições.",inner,lines);
               JPWDetailsWrap((partial ? "Subtotal conhecido · PARCIAL: " : "Snapshot datado: ")+
                  (known ? JPWGenetrixMoney(cycle.compensated,currency) : "N/A")+
                  "; percentual "+(known && cycle.percent_valid ? JPWGenetrixSignedNumber(cycle.percent)+"%" : "N/A")+
                  " sobre saldo da amostra "+JPWGenetrixMoney(g_genetrix_view.balance,currency)+
                  ", observada "+TimeToString((datetime)g_genetrix_view.observed_utc,TIME_DATE|TIME_SECONDS)+
                  " UTC. Histórico não é flutuante atual nem saldo no encerramento.",inner,lines);
               JPWDetailsWrap("Componentes "+(partial ? "CONHECIDOS · PARCIAIS" : "da leitura")+
                  ": realizado preço "+(known ? JPWGenetrixMoney(cycle.realized_price,currency) : "N/A")+
                  "; swap realizado "+(known ? JPWGenetrixMoney(cycle.realized_swap,currency) : "N/A")+
                  "; comissões "+(known ? JPWGenetrixMoney(cycle.commissions,currency) : "N/A")+
                  "; taxas "+(known ? JPWGenetrixMoney(cycle.fees,currency) : "N/A")+".",inner,lines);
               JPWDetailsWrap("Remanescente: preço "+(known ? JPWGenetrixMoney(cycle.unrealized_price,currency) : "N/A")+
                  "; swap "+(known ? JPWGenetrixMoney(cycle.unrealized_swap,currency) : "N/A")+
                  ". Valores projetados do ledger; a UI não soma parcelas nem presume custos ausentes iguais a zero.",inner,lines);
               JPWDetailsWrap("Histórico: "+(cycle.history_complete ? "completo declarado" : "incompleto")+
                  "; custos: "+(cycle.costs_complete ? "completos declarados" : "incompletos")+
                  "; "+IntegerToString(cycle.open_positions)+" posições / "+IntegerToString(cycle.pending_orders)+
                  " pendentes. "+cycle.reason,inner,lines);
               string member_ids[];
               const bool members_known=JPWGenetrixMemberIdentifiers(cycle,member_ids);
               JPWDetailsWrap("Membros da geração "+IntegerToString(g_genetrix_view.generation)+
                  ", observada "+TimeToString((datetime)g_genetrix_view.observed_utc,TIME_DATE|TIME_SECONDS)+
                  " UTC. Identificadores observados das posições, incluindo encerradas; não são tickets atuais.",inner,lines);
               if(!members_known)
                  JPWDetailsWrap("Membros indisponíveis nesta publicação; ausência da lista não comprova zero membros.",inner,lines);
               else if(ArraySize(member_ids)==0)
                  JPWDetailsWrap("Ciclo provisório antes da primeira execução; nenhum identificador de posição atribuído nesta geração.",inner,lines);
               else
                 {
                  JPWDetailsWrap("Lista observada: "+IntegerToString(ArraySize(member_ids))+
                     " identificadores. Cobertura histórica "+(cycle.history_complete ?
                     "completa declarada; não verificada automaticamente." :
                     "incompleta; a lista não comprova todos os membros desde a origem."),inner,lines);
                  for(int member=0;member<ArraySize(member_ids);member++)
                     JPWDetailsWrap("Membro "+IntegerToString(member+1)+
                        ": POSITION_IDENTIFIER "+member_ids[member],inner,lines);
                 }
              }
            JPWDetailsWrap(JPWGenetrixLedgerHealth(),inner,lines);
            JPWDetailsWrap("Limite: métrica contábil, distinta do Floating P/L global. Resultado positivo não abate perdas/custos negativos no RC nem financia ampliação de risco.",inner,lines);
           }
        }
      else if(g_raiz_tab==JPW_ROUTE_STOP_ROW)
        {
         if(g_position_detail_open)
           {
            const int index=JPWPositionsViewFind(g_position_detail_ticket,g_position_detail_identifier);
            if(index<0 || !JPWPositionsViewCurrent(g_sample_context,GetTickCount64()))
               JPWDetailsWrap("Posição indisponível nesta leitura; volte à tabela e atualize.",inner,lines);
            else
              {
               JPWPositionView row=g_position_views[index];
               JPWDetailsWrap(JPWPositionRole(row)+" · "+row.symbol+" · "+
                  (row.direction==POSITION_TYPE_BUY ? "BUY" : "SELL")+
                  " · ticket MT5 "+JPWPositionTicket(row.ticket),inner,lines);
               JPWDetailsWrap("Volume remanescente: "+DoubleToString(row.volume,row.volume_digits)+" lote.",inner,lines);
               JPWDetailsWrap("Leverage individual: "+JPWPositionLeverageText(row)+
                  " · "+JPWCockpitQualityText((JPW_VIEW_QUALITY)row.quality)+". "+row.reason,inner,lines);
               JPWDetailsWrap("Fórmula: nocional desta posição / último equity aceito da conta. "+
                  "Mesmos preços, conversões e escala contratual da leitura da conta; não é margem nem leverage da corretora.",inner,lines);
               JPWDetailsWrap("Amostra "+IntegerToString(g_positions_view.sample_id)+"; observada "+
                  TimeToString((datetime)g_positions_view.observed_utc,TIME_DATE|TIME_SECONDS)+" UTC (computador).",inner,lines);
               JPWDetailsWrap("Entrada: "+(row.entry_valid ? DoubleToString(row.entry,8) : "N/A")+
                  "; SL: "+(row.sl_valid ? (row.sl>0.0 ? DoubleToString(row.sl,8) : "Sem SL") : "N/A")+
                  "; TP: "+(row.tp_valid ? (row.tp>0.0 ? DoubleToString(row.tp,8) : "Sem TP") : "N/A")+".",inner,lines);
               string amount="",percent="",state="",reason=""; JPWPositionRiskView(row,amount,percent,state,reason);
               JPWDetailsWrap("Stop EA: "+amount+" · "+percent+" balance · "+state+". "+reason,inner,lines);
               JPWDetailsWrap("Risco EA e leverage têm origens/horários independentes. "+
                  "LAST · NOT ACTIVE não é risco atual. Conta lista todas as posições; o consolidado Stop risk preserva a operação atribuída.",inner,lines);
              }
           }
         else
           {
         JPWDetailsWrap(g_stop_selected_role+
            (g_stop_selected_row==-2 ? " · referência encerrada, memória" :
            (g_stop_table_historical ? " · última amostra, não atual" :
                                       " · amostra atual")),inner,lines);
         if(g_stop_selected_row==-2)
           {
            JPWDetailsWrap("Referência Gênese encerrada: ticket de origem "+
               IntegerToString(g_stop_genesis_ticket)+", identificador "+
               IntegerToString(g_stop_genesis_identifier)+". Nenhuma sucessora foi promovida.",inner,lines);
            JPWDetailsWrap("A linha é memória da referência; não soma risco aberto.",inner,lines);
           }
         else if(g_stop_selected_row>=0 &&
                 g_stop_selected_row<ArraySize(g_stop_table_rows))
           {
            JPWStopRiskRow row=g_stop_table_rows[g_stop_selected_row];
            JPWDetailsWrap((row.kind==JPW_STOP_RISK_PENDING ? "Pendente" : "Posição")+
               " · "+row.symbol+" · "+(row.side>0 ? "BUY" : "SELL")+
               " · ticket "+IntegerToString(row.ticket)+
               " · identificador "+IntegerToString(row.identifier),inner,lines);
            JPWDetailsWrap("Abertura/criação: "+
               TimeToString((datetime)(row.opened_msc/1000),TIME_DATE|TIME_SECONDS)+
               " (servidor). Volume remanescente: "+DoubleToString(row.volume,4),inner,lines);
            JPWDetailsWrap("Preço de execução/planejado: "+DoubleToString(row.entry,8)+
               "; SL vigente: "+DoubleToString(row.sl,8)+".",inner,lines);
            if(row.valid==1 && JPWFinitePositive(g_stop_table_sample.balance))
               JPWDetailsWrap("Stop aberto: "+JPWStopRiskMoney(row.risk_money)+" "+
                  g_stop_table_sample.currency+" · "+
                  JPWFormatPercent(100.0*row.risk_money/g_stop_table_sample.balance,false)+
                  " do balance atual.",inner,lines);
            else JPWDetailsWrap("Stop aberto: N/A · "+row.reason,inner,lines);
            if(row.kind==JPW_STOP_RISK_POSITION)
               JPWDetailsWrap("Preço atual→SL (medida separada): "+
                  (row.additional_valid==1 ? JPWStopRiskMoney(row.additional_money)+
                   " "+g_stop_table_sample.currency : "N/A · "+row.additional_reason),
                   inner,lines);
            JPWDetailsWrap(g_stop_table_sample.margin_mode==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING ?
               "Origem: EA observador; OrderCalcProfit em moeda da conta. Papel Gênese/Defesa inferido por identidade/antiguidade; tese não certificada no MT5." :
               "Posição netting agregada: MT5 não preserva risco individual por ordem com piso zero; consolidado Gênese/Defesa N/A.",
               inner,lines);
            JPWDetailsWrap("Estado: "+row.reason,inner,lines);
           }
           }
        }
      else if(g_raiz_tab==JPW_ROUTE_RAIZN)
        {
         JPWDetailsWrap("Raiz N diagnóstica: horizontes móveis de 7 e 14 dias civis do servidor.",inner,lines);
         JPWDetailsWrap("1W: "+g_cockpit_snapshot.metric[3].value+" · "+JPWCockpitQualityText(g_cockpit_snapshot.metric[3].quality)+". "+g_cockpit_snapshot.metric[3].reason,inner,lines);
         JPWDetailsWrap("2W: "+g_cockpit_snapshot.metric[4].value+" · "+JPWCockpitQualityText(g_cockpit_snapshot.metric[4].quality)+". "+g_cockpit_snapshot.metric[4].reason,inner,lines);
         JPWDetailsWrap("Insumos da última apuração (consulte o estado atual acima): P0, ATR, N, F e horários: "+g_raiz_tooltip+" "+g_scale2_tooltip,inner,lines);
         JPWDetailsWrap("F diagnóstico: "+(g_factor_state==JPW_RAIZN_VALID ?
                        DoubleToString(g_factor_preference.factor,1)+" salvo" :
                        (g_factor_state==JPW_RAIZN_ABSENT ? "1,5 padrão" : "N/A: "+g_factor_reason))+
                        ". P-21 estatutário permanece PENDING.",inner,lines);
         JPWDetailsWrap("A probabilidade teórica de primeiro não toque usa barreira hipotética fixa e premissas brownianas. Não mede o SL real, lucro ou cobertura empírica.",inner,lines);
        }
      else if(g_raiz_tab==JPW_ROUTE_EXPORT)
        {
         JPWDetailsWrap("Prévia de exportação técnica local. Não contém login, ticket, credenciais ou valores financeiros. Somente eventos essenciais, versões, códigos e contexto opaco.",inner,lines);
         JPWDetailsWrap(g_export_preview=="" ? "Aguardando prévia no próximo timer." : g_export_preview,inner,lines);
         JPWDetailsWrap(g_export_result,inner,lines);
        }
      else if(g_raiz_tab==JPW_ROUTE_SYSTEM)
        {
         JPWDetailsWrap(JPWGenetrixLedgerHealth(),inner,lines);
         JPWDetailsWrap(JPWGenetrixRiskSummary(),inner,lines);
         JPWDetailsWrap(JPW_PRODUCT_NAME+" "+JPW_PRODUCT_VERSION+" · cálculo "+JPW_CALCULATION_VERSION+
                         " · build "+JPW_BUILD_ID,inner,lines);
         JPWDetailsWrap(JPW_PRODUCT_TAGLINE,inner,lines);
         const ulong evidence_now=GetTickCount64();
         // Publisher evidence is independent of the financial total: a recent
         // verified generation may legitimately report N/A (e.g. missing SL).
         const bool observer_recent=g_stop_ready &&
            g_stop_sample.account_key==g_diagnostic_context &&
            g_stop_sample.observed_mono_ms>0 &&
            evidence_now>=(ulong)g_stop_sample.observed_mono_ms &&
            evidence_now-(ulong)g_stop_sample.observed_mono_ms<=30000;
         const JPW_TECHNICAL_HEALTH health=JPWTechnicalHealthEvaluate(g_sample_context!="",
            g_diagnostic_state==JPW_STORE_VALID,
            g_diagnostic_write_state==JPW_STORE_VALID,ArraySize(g_diagnostic_pending),
            g_diagnostic_queue_lost,observer_recent,g_last_cycle_duration_ms>=500 || g_refresh_requested);
         JPWDetailsWrap("Saúde técnica: "+(health==JPW_HEALTH_UNAVAILABLE ? "indisponível — contexto inválido" :
            (health==JPW_HEALTH_ATTENTION ? "atenção — armazenamento, fila, orçamento ou evidência do observador" :
             "normal nas evidências atuais"))+". Qualidade das métricas é independente; cobertura histórica permanece desconhecida ou incompleta.",inner,lines);
         JPWDetailsWrap("Eventos aguardando persistência: "+IntegerToString(ArraySize(g_diagnostic_pending))+
            (g_diagnostic_queue_lost ? "; lacuna da fila pendente" : "")+". Evidência recente do observador: "+
            (observer_recent ? "presente" : "não confirmada")+"; não prova atividade contínua.",inner,lines);
         string observer_state="sem sinal recente compatível";
         if(g_stop_observer_presence==JPW_OBSERVER_WAITING)
            observer_state="presente; aguardando primeira amostra";
         else if(g_stop_observer_presence==JPW_OBSERVER_FAILED)
            observer_state="presente; publicação falhou";
         else if(g_stop_observer_presence==JPW_OBSERVER_PUBLISHED)
            observer_state="presente; publicação sinalizada";
         JPWDetailsWrap("Sinal do EA observador: "+observer_state+
            ". Amostra financeira Stop risk: "+
            (g_stop_quality==JPW_VIEW_CURRENT ? "Current" : "N/A · "+g_stop_reason)+
            ". Um sinal não valida o total nem prova cobertura contínua.",inner,lines);
         JPWDetailsWrap("Ativação manual nesta instalação: Expert Advisors > JPWealth > " +
            "JPW_Alavancagem_Observer; anexe a um gráfico aberto, confira a mesma " +
            "versão e leia a aba Experts. Não precisa habilitar negociação.",inner,lines);
         JPWDetailsWrap("Trilha técnica: "+(g_diagnostic_state==JPW_STORE_VALID ? "acessível" :
            (g_diagnostic_state==JPW_STORE_ABSENT ? "ainda ausente" : "indisponível/atenção"))+
            ". "+g_diagnostic_summary+" "+g_diagnostic_reason,inner,lines);
         JPWDetailsWrap("Último ciclo observado: "+IntegerToString((long)g_last_cycle_duration_ms)+
            " ms. Timer solicitado não garante despacho. Compilação/integração nativas destes bytes exigem recibo separado.",inner,lines);
         JPWDetailsWrap("Registros locais pertencem à instalação e à conta. Nenhum histórico completo é inferido de uma amostra.",inner,lines);
         JPWDetailsWrap(g_mdd_summary+". "+g_mdd_context,inner,lines);
         JPWDetailsWrap(g_observer_summary+". "+g_observer_context,inner,lines);
         JPWDetailsWrap("A última captura do EA observador não prova que ele esteja ativo neste instante.",inner,lines);
         JPWDetailsWrap("Preferências visuais ficam no objeto deste gráfico; o modelo MT5 é salvo manualmente pelo usuário.",inner,lines);
        }
      else
        {
         JPWDetailsWrap("Amostra do cockpit: "+_Symbol+" · sequência "+IntegerToString(g_cockpit_snapshot.sequence),inner,lines);
         JPWDetailsWrap("Cadência: solicitada "+IntegerToString(InpUpdateSeconds)+
            " s; leitura completa no máximo a cada 30 s por frescor, Stop risk verificado no máximo a cada 5 s. O timer não garante intervalos exatos.",inner,lines);
         JPWDetailsWrap("Cotação: "+(g_live_sample.quote_time_msc>0 ?
            TimeToString((datetime)(g_live_sample.quote_time_msc/1000),TIME_DATE|TIME_SECONDS)+" (servidor)" :
            "indisponível")+". "+g_live_sample.reason,inner,lines);
         JPWDetailsWrap("ATR: "+(g_live_sample.atr>0.0 ? DoubleToString(g_live_sample.atr,8) : "N/A")+
            " · H4 encerrado "+(g_live_sample.bar_time>0 ?
               TimeToString(g_live_sample.bar_time,TIME_DATE|TIME_SECONDS)+" (servidor)" :
               "indisponível")+".",inner,lines);
         JPWDetailsWrap("Calendário: "+g_horizon_result.source+". 1W: "+g_horizon_result.reason_1w+
            ". 2W: "+g_horizon_result.reason_2w,inner,lines);
         JPWDetailsWrap("F: "+(g_factor_state==JPW_RAIZN_VALID ?
            DoubleToString(g_factor_preference.factor,1)+" gravado" :
            (g_factor_state==JPW_RAIZN_ABSENT ? "1,5 padrão não gravado" : "indisponível: "+g_factor_reason))+
            ". P-21 PENDING.",inner,lines);
         JPWDetailsWrap("DD atual: "+g_dd_line+". "+g_dd_tooltip,inner,lines);
         JPWDetailsWrap("MDD local: "+g_mdd_summary+". "+g_mdd_context,inner,lines);
         JPWDetailsWrap("EA observador: "+g_observer_summary+". "+g_observer_context+
            " Última captura conhecida não prova que o EA esteja ativo agora.",inner,lines);
        }
      const int rows=(body_height/g_details_line>0 ? body_height/g_details_line : 1);
      const int pages=JPWPanelPageCount(ArraySize(lines),rows);
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
      for(int j=0;j<rows && g_cockpit_page*rows+j<ArraySize(lines) && j<60;j++)
        {
         const string suffix="TEXT_"+IntegerToString(j);
         JPWRaizCreateLabel(suffix,lines[g_cockpit_page*rows+j],x,body_y+j*g_details_line);
         ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,"\n");
        }
      JPWRaizCreateLabel("PAGE","Página "+IntegerToString(g_cockpit_page+1)+"/"+
                          IntegerToString(pages),x,footer_y-g_details_line);
     }
   if(g_raiz_tab==JPW_ROUTE_SETTINGS)
     {
      JPWRaizCreateButton(JPW_ACTION_APPLY,"Aplicar",x,footer_y,footer_button);
      JPWRaizCreateButton(JPW_ACTION_CANCEL,"Cancelar",x+footer_button+g_details_pad,footer_y,footer_button);
      JPWRaizCreateButton(JPW_ACTION_RESET,"Restaurar",x+2*(footer_button+g_details_pad),footer_y,footer_button);
     }
   else
     {
      string first_action="Stops",second_action="Preparar mensagem";
      if(g_raiz_tab==JPW_ROUTE_METRIC)
        { first_action="Visão geral"; second_action=(g_cockpit_selected==6 ? "Selecionar ciclo" : "Proveniência"); }
      else if(g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES)
        { first_action="Compensado"; second_action="Visão geral"; }
      else if(g_raiz_tab==JPW_ROUTE_PROVENANCE)
        { first_action="Sistema"; second_action="Atualizar"; }
      else if(g_raiz_tab==JPW_ROUTE_STOP_ROW)
        { first_action="Preparar mensagem"; second_action="Pendentes"; }
      else if(g_raiz_tab==JPW_ROUTE_STOPS)
        { first_action=(g_stops_show_pending ? "Posições" :
            (g_positions_operation_only ? "Ver Conta" : "Ver Operação")); second_action="Pendentes"; }
      else if(g_raiz_tab==JPW_ROUTE_RAIZN)
        { first_action="F 1,5/1,8"; second_action="Avançado"; }
      else if(g_raiz_tab==JPW_ROUTE_SYSTEM)
        { first_action="Estado dos dados"; second_action="Exportar…"; }
      else if(g_raiz_tab==JPW_ROUTE_EXPORT)
        { first_action="Voltar"; second_action="Salvar exportação"; }
      JPWRaizCreateButton(JPW_ACTION_PRIMARY,first_action,x,footer_y,footer_button);
      JPWRaizCreateButton(JPW_ACTION_SECONDARY,second_action,x+footer_button+g_details_pad,footer_y,footer_button);
      JPWRaizCreateButton(JPW_ACTION_CLOSE,"Fechar",x+2*(footer_button+g_details_pad),footer_y,footer_button);
     }
   // Paging is visible on every screen; disabled end clicks are harmless.
   const int pager_width=(inner>180 ? 48 : 28);
   const bool position_scroll=(g_raiz_tab==JPW_ROUTE_STOPS && !g_stops_show_pending);
   const int previous_action=(position_scroll ? JPW_ACTION_POSITIONS_UP : JPW_ACTION_PREVIOUS);
   const int next_action=(position_scroll ? JPW_ACTION_POSITIONS_DOWN : JPW_ACTION_NEXT);
   JPWRaizCreateButton(previous_action,position_scroll ? "↑" : "‹",x+inner-2*pager_width-g_details_pad,
                        footer_y-g_details_line,pager_width);
   JPWRaizCreateButton(next_action,position_scroll ? "↓" : "›",x+inner-pager_width,
                        footer_y-g_details_line,pager_width);
   ObjectSetInteger(0,JPWActionObject(previous_action),OBJPROP_YSIZE,g_details_line);
   ObjectSetInteger(0,JPWActionObject(next_action),OBJPROP_YSIZE,g_details_line);
   g_raiz_panel_built=true; JPWFocusPaint();
  }

void JPWRenderRaizDetails()
  {
   if(!g_raiz_details_open || !JPWDetailsContextCurrent()) return;
   if(g_raiz_panel_built) return;
   if(g_raiz_tab>=JPW_ROUTE_OVERVIEW) { JPWRenderCockpit(); return; }
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   g_details_text=JPWPanelInk(background); g_details_surface=JPWPanelWindowSurface(background);
   g_details_chrome=JPWPanelChromeSurface(background);
   g_details_card=JPWPanelCardSurface(background);
   g_details_border=JPWPanelBorderColor(background);
   const int chart_width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int chart_height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   g_details_font=InpCockpitFontSize;
   uint text_width=0,text_height=0;
   if(!TextSetFont("Arial",-10*g_details_font,FW_NORMAL) ||
      !TextGetSize("Mg",text_width,text_height) || text_height==0) return;
   int content_y=0,content_height=0,footer_y=0;
   if(!JPWPanelDialog(chart_width,chart_height,(int)text_height,(int)text_width/2,
                     g_details_rect,g_details_pad,g_details_line,g_details_control,
                     content_y,content_height,footer_y)) return;
   const int left=g_details_rect.x,top=g_details_rect.y,width=g_details_rect.width;
   const int x=left+g_details_pad,inner=width-2*g_details_pad;
   const string bg=JPWRaizUI("BG");
   if(ObjectFind(0,bg)<0 && !ObjectCreate(0,bg,OBJ_RECTANGLE_LABEL,0,0,0)) return;
   ObjectSetInteger(0,bg,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,bg,OBJPROP_XDISTANCE,left);
   ObjectSetInteger(0,bg,OBJPROP_YDISTANCE,top);
   ObjectSetInteger(0,bg,OBJPROP_XSIZE,width);
   ObjectSetInteger(0,bg,OBJPROP_YSIZE,g_details_rect.height);
   ObjectSetInteger(0,bg,OBJPROP_BGCOLOR,g_details_surface);
   ObjectSetInteger(0,bg,OBJPROP_COLOR,g_details_border);
   ObjectSetInteger(0,bg,OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSetInteger(0,bg,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,bg,OBJPROP_BACK,false);
   ObjectSetInteger(0,bg,OBJPROP_ZORDER,1);
   ObjectSetInteger(0,bg,OBJPROP_HIDDEN,true);
   JPWRaizCreateSurface("HEADER",left+1,top+1,width-2,
                        g_details_line+g_details_pad-2,g_details_chrome);
   JPWRaizCreateSurface("FOOTER",left+1,footer_y-g_details_line,
                        width-2,top+g_details_rect.height-footer_y+g_details_line-2,
                        g_details_chrome);
   const int close_size=(g_details_control>24 ? g_details_control : 24);
   const string legacy_title=_Symbol+" · "+
      (g_raiz_tab==JPW_ROUTE_LEGACY_SUMMARY ? "Resumo" : (g_raiz_tab==JPW_ROUTE_LEGACY_NF ? "N/F legado" :
       (g_raiz_tab==JPW_ROUTE_FACTOR ? "F diagnóstico" : "Cenários avançados")));
   JPWGenetrixHeader(JPWRaizUI("BRAND_LOGO"),JPWRaizUI("TITLE"),x,top+g_details_pad,
      inner-close_size-g_details_pad,g_details_line,g_details_font,g_details_text,
      JPWPanelDarkBackground(chart_background),legacy_title,4);
   JPWRaizCreateButton(JPW_ACTION_HEADER_CLOSE,"×",
                       left+width-g_details_pad-close_size,top+g_details_pad,close_size);
   ObjectSetString(0,JPWActionObject(JPW_ACTION_HEADER_CLOSE),OBJPROP_TOOLTIP,"Fechar cockpit sem aplicar alterações");
   const int nav_y=top+g_details_pad+g_details_line;
   const int nav_width=(inner-3*g_details_pad)/4;
   const int action_width=(inner-2*g_details_pad)/3;
   if(nav_width>0 && content_height>0)
     {
      if(g_details_rect.compact && g_raiz_tab<=JPW_ROUTE_BIND)
        {
         JPWRaizCreateButton(JPW_ACTION_DECLARE,"Declarar",x,nav_y,action_width);
         JPWRaizCreateButton(JPW_ACTION_BIND,"Vincular",x+action_width+g_details_pad,nav_y,action_width);
         JPWRaizCreateButton(JPW_ACTION_COMPARE,"Comparar",x+2*(action_width+g_details_pad),nav_y,action_width);
        }
      else
        {
         JPWRaizCreateButton(JPW_ACTION_HOME,"← Cockpit",x,nav_y,nav_width);
         JPWRaizCreateButton(JPW_ACTION_FACTOR,"F 1,5/1,8",x+nav_width+g_details_pad,nav_y,nav_width);
         JPWRaizCreateButton(JPW_ACTION_LEGACY_NF,"N/F legado",x+2*(nav_width+g_details_pad),nav_y,nav_width);
         JPWRaizCreateButton(JPW_ACTION_ADVANCED,"Avançado",x+3*(nav_width+g_details_pad),nav_y,nav_width);
        }
      const int action_y=nav_y+g_details_control+g_details_pad;
      if(!g_details_rect.compact && g_raiz_tab<=JPW_ROUTE_BIND)
        {
         JPWRaizCreateButton(JPW_ACTION_DECLARE,"Declarar",x,action_y,action_width);
         JPWRaizCreateButton(JPW_ACTION_BIND,"Vincular",x+action_width+g_details_pad,action_y,action_width);
         JPWRaizCreateButton(JPW_ACTION_COMPARE,"Comparar",x+2*(action_width+g_details_pad),action_y,action_width);
        }
      else if(!g_details_rect.compact && g_raiz_tab==JPW_ROUTE_FACTOR)
        {
         const int choice_width=(inner-g_details_pad)/2;
         JPWRaizCreateButton(JPW_ACTION_FACTOR_15,(g_factor_draft==1.5 ? "✓ F 1,5" : "F 1,5"),
                              x,action_y,choice_width);
         JPWRaizCreateButton(JPW_ACTION_FACTOR_18,(g_factor_draft==1.8 ? "✓ F 1,8" : "F 1,8"),
                              x+choice_width+g_details_pad,action_y,choice_width);
        }
      else if(!g_details_rect.compact)
         JPWRaizCreateButton(JPW_ACTION_REFRESH,"Atualizar resumo",x,action_y,inner);
     }
   if(g_raiz_tab==JPW_ROUTE_FACTOR && g_details_rect.compact &&
      content_height>=g_details_control+g_details_pad)
     {
      const int choice_width=(inner-g_details_pad)/2;
      JPWRaizCreateButton(JPW_ACTION_FACTOR_15,(g_factor_draft==1.5 ? "✓ F 1,5" : "F 1,5"),
                           x,content_y,choice_width);
      JPWRaizCreateButton(JPW_ACTION_FACTOR_18,(g_factor_draft==1.8 ? "✓ F 1,8" : "F 1,8"),
                           x+choice_width+g_details_pad,content_y,choice_width);
      content_y+=g_details_control+g_details_pad;
      content_height-=g_details_control+g_details_pad;
     }
   if(g_details_rect.compact && g_raiz_feedback!="" && content_height>g_details_line)
     {
      JPWRaizCreateLabel("FEEDBACK",g_raiz_feedback,x,content_y);
      content_y+=g_details_line; content_height-=g_details_line;
     }
   string captions[21]={"P0 (preço)","Origem do P0","Decisão: AAAA.MM.DD HH:MM:SS (servidor)",
       "ATR: MT5 ou DECLARED","ATR declarado (>0)","Fonte do ATR","Variante do ATR",
       "Início H4 já encerrado: AAAA.MM.DD HH:MM:SS","N (candles H4)","Justificativa N",
       "F (>0)","F: DECLARED / ILLUSTRATIVE / SOURCED","Fonte de F","Justificativa F",
       "Lado: 1 BUY / -1 SELL / 0 sem lado","Motivo da revisão (obrigatório ao revisar)","Ticket aberto do símbolo exato",
       "N: horizonte em candles H4 (inteiro >0)","Justificativa do horizonte N",
       "F: fator diagnóstico (>0, use ponto decimal)","Justificativa de F (sem valor universal)"};
   const bool editing=(g_raiz_tab==JPW_ROUTE_DECLARE || g_raiz_tab==JPW_ROUTE_JUSTIFY || g_raiz_tab==JPW_ROUTE_BIND || g_raiz_tab==JPW_ROUTE_LEGACY_NF);
   int first=0,total=0,rows=0;
   string text_lines[];
   if(editing)
     {
      first=(g_raiz_tab==JPW_ROUTE_DECLARE ? 0 : (g_raiz_tab==JPW_ROUTE_JUSTIFY ? 8 : (g_raiz_tab==JPW_ROUTE_BIND ? 16 : 17)));
      total=(g_raiz_tab==JPW_ROUTE_BIND ? 1 : (g_raiz_tab==JPW_ROUTE_LEGACY_NF ? 4 : 8));
      rows=JPWPanelPageRows(content_height,g_details_line+g_details_control+g_details_pad);
     }
   else
     {
      if(g_raiz_tab==JPW_ROUTE_LEGACY_SUMMARY)
        {
         JPWDetailsWrap("Valores da abertura/atualização deste resumo. Use Atualizar resumo para uma nova consulta.",inner,text_lines);
         JPWDetailsWrap("Leverage: "+g_panel_value+"; "+g_panel_status,inner,text_lines);
         JPWDetailsWrap(g_floating_line+". "+g_floating_tooltip,inner,text_lines);
         JPWDetailsWrap(g_dd_line+". "+g_dd_tooltip,inner,text_lines);
         JPWDetailsWrap(g_mdd_summary+". "+g_mdd_context,inner,text_lines);
         JPWDetailsWrap(g_genesis_line+". "+g_genesis_tooltip,inner,text_lines);
         JPWDetailsWrap(g_raiz_line+". "+g_raiz_tooltip,inner,text_lines);
         JPWDetailsWrap(g_scale2_line+". "+g_scale2_tooltip,inner,text_lines);
         if(g_factor_state==JPW_RAIZN_VALID || g_factor_state==JPW_RAIZN_ABSENT)
           {
            const double active_factor=(g_factor_state==JPW_RAIZN_VALID ?
                                        g_factor_preference.factor : JPW_RAIZN_FACTOR_DEFAULT);
            double probability=0.0;
            if(JPWRaizNNoTouchProbability(active_factor,probability))
              JPWDetailsWrap("Primeiro não toque teórico de barreira adversa fixa: "+
                 JPWNoTouchPercentText(probability)+" para 1W e 2W com F "+
                 (active_factor==1.8 ? "1,8" : "1,5")+
                 ". A igualdade decorre de cada distância escalar com √N; os preços das barreiras diferem.",inner,text_lines);
            else JPWDetailsWrap("Primeiro não toque teórico: N/A; cálculo inválido.",inner,text_lines);
            JPWDetailsWrap((g_factor_state==JPW_RAIZN_ABSENT ?
               "F 1,5 é o padrão ainda não gravado." : "F escolhido foi gravado nesta instalação.")+
               " Aprovação de uso diagnóstico pelo proprietário; P-21 canônico permanece PENDING.",inner,text_lines);
           }
         else JPWDetailsWrap("F indisponível: "+g_factor_reason+
            " Registro preservado; não aplicamos F 1,5 por fallback.",inner,text_lines);
         JPWDetailsWrap("Referência browniana ideal sem drift e com volatilidade constante, aproximada pelo ATR. Não é a probabilidade remanescente de um SL real, chance de lucro ou cobertura empírica; não recomenda stop, lote ou entrada.",inner,text_lines);
         JPWDetailsWrap(g_observer_summary+". "+g_observer_context,inner,text_lines);
         if(g_live_config_state==JPW_RAIZN_VALID)
            JPWDetailsWrap("Configuração manual legada do símbolo: N="+
              IntegerToString(g_live_config.n)+", F="+
              DoubleToString(g_live_config.f,-16)+
              ". Declarada para diagnóstico anterior; NÃO aplicada às escalas 1W/2W.",inner,text_lines);
        }
      else if(g_raiz_tab==JPW_ROUTE_FACTOR)
        {
         if(g_factor_state==JPW_RAIZN_VALID || g_factor_state==JPW_RAIZN_ABSENT)
           {
            JPWDetailsWrap("Selecione F 1,5 ou F 1,8 acima. Aplicar grava apenas este fator para a conta, instalação e símbolo exato; Cancelar descarta o rascunho.",inner,text_lines);
            JPWDetailsWrap("F em rascunho: "+(g_factor_draft==1.8 ? "1,8" : "1,5")+
               (g_factor_state==JPW_RAIZN_ABSENT ?
                "; padrão inicial 1,5 ainda não gravado." :
                "; preferência gravada tem geração "+IntegerToString(g_factor_preference.generation)+"."),
               inner,text_lines);
            double probability=0.0;
            if(JPWRaizNNoTouchProbability(g_factor_draft,probability))
              JPWDetailsWrap("Prévia: primeiro não toque teórico de barreira adversa fixa = "+
                 JPWNoTouchPercentText(probability)+" para 1W e 2W. O mesmo F dá a mesma referência teórica porque cada distância usa √N; as distâncias em preço são diferentes.",inner,text_lines);
            else JPWDetailsWrap("Prévia de não toque teórico: N/A; cálculo inválido.",inner,text_lines);
           }
         else JPWDetailsWrap("Preferência de F indisponível: "+g_factor_reason+
            ". Não há fallback nem reparo automático; Aplicar fica bloqueado.",inner,text_lines);
         JPWDetailsWrap("Modelo browniano ideal: sem drift, volatilidade constante e aproximação ATR→dispersão. Isto não mede chance de lucro, cobertura observada ou probabilidade de o SL atual não ser tocado.",inner,text_lines);
         JPWDetailsWrap("F 1,5 é o padrão diagnóstico aprovado pelo proprietário; F 1,8 é alternativa selecionável. P-21 permanece PENDING e nenhum F homologa stop ou regra do Estatuto.",inner,text_lines);
        }
      else
        {
         JPWDetailsWrap("Cenários declarados 1.4: independentes do cálculo corrente, sem sobrescrita automática.",inner,text_lines);
         JPWDetailsWrap(g_saved_raiz_line+". "+g_saved_raiz_tooltip,inner,text_lines);
         JPWDetailsWrap(g_raiz_comparison,inner,text_lines);
         if(g_raiz_store_state==JPW_RAIZN_VALID)
           {
            double distance=0.0,percent=0.0;
            if(JPWRaizNCalculate(g_raiz_scenario.p0,g_raiz_scenario.atr,g_raiz_scenario.n_h4,g_raiz_scenario.factor,distance,percent)==JPW_RAIZN_OK)
               JPWDetailsWrap("Níveis aritméticos P0 ± D: "+DoubleToString(g_raiz_scenario.p0-distance,8)+
                  " / "+DoubleToString(g_raiz_scenario.p0+distance,8)+". Não são ordem ou novo SL.",inner,text_lines);
           }
         JPWDetailsWrap("Declarar/revisar preserva o cenário inicial. Vincular exige ticket explícito e direção coerente. Comparar grava recibo próprio; não altera o SL.",inner,text_lines);
        }
      total=ArraySize(text_lines); rows=JPWPanelPageRows(content_height,g_details_line);
     }
   // Destruction accounts for every visible row, including wrapped summaries.
   if(rows>60) rows=60;
   g_raiz_pages=JPWPanelPageCount(total,rows);
   g_raiz_page=JPWPanelClamp(g_raiz_page,0,g_raiz_pages-1);
   if(rows>0)
     {
      for(int j=0;j<rows && g_raiz_page*rows+j<total;j++)
        {
         const int item=g_raiz_page*rows+j;
         if(editing)
           {
            const int field=first+item,y=content_y+j*(g_details_line+g_details_control+g_details_pad);
            JPWRaizCreateLabel("LABEL_"+IntegerToString(field),captions[field],x,y);
            JPWRaizCreateEdit(field,x,y+g_details_line,inner);
           }
         else
           {
            const string suffix="TEXT_"+IntegerToString(j);
            JPWRaizCreateLabel(suffix,text_lines[item],x,content_y+j*g_details_line);
            // Full summary text is already wrapped and paged. A long hover
            // tooltip previously covered the dialog while the mouse moved.
            ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,"\n");
           }
        }
     }
   if(content_height>0 && !g_details_rect.compact)
     {
      JPWRaizCreateLabel("FEEDBACK",g_raiz_feedback,x,footer_y-2*g_details_line);
      JPWRaizCreateLabel("PAGE","Página "+IntegerToString(g_raiz_page+1)+"/"+IntegerToString(g_raiz_pages)+
        (rows==0 ? " · Amplie o gráfico para editar" : ""),x,footer_y-g_details_line);
     }
   if(g_details_rect.compact)
      JPWGenetrixHeader(JPWRaizUI("BRAND_LOGO"),JPWRaizUI("TITLE"),x,top+g_details_pad,
         inner-close_size-g_details_pad,g_details_line,g_details_font,g_details_text,
         JPWPanelDarkBackground(chart_background),_Symbol+" · "+IntegerToString(g_raiz_page+1)+"/"+IntegerToString(g_raiz_pages),4);
   // Footer remains inside the rectangle even when no body row fits.
   const int button_width=(inner-3*g_details_pad)/4;
   if(button_width>0)
     {
      JPWRaizCreateButton(JPW_ACTION_LEGACY_CANCEL,(editing || g_raiz_tab==JPW_ROUTE_FACTOR ? "Cancelar" : "Fechar"),x,footer_y,button_width);
      if(rows>0)
        {
         JPWRaizCreateButton(JPW_ACTION_LEGACY_PREVIOUS,"‹",x+button_width+g_details_pad,footer_y,button_width);
         JPWRaizCreateButton(JPW_ACTION_LEGACY_NEXT,"›",x+2*(button_width+g_details_pad),footer_y,button_width);
         const string action=(g_raiz_tab==JPW_ROUTE_DECLARE ? "Justif." :
                              (g_raiz_tab==JPW_ROUTE_JUSTIFY || g_raiz_tab==JPW_ROUTE_LEGACY_NF || g_raiz_tab==JPW_ROUTE_FACTOR ? "Aplicar" :
                               (g_raiz_tab==JPW_ROUTE_BIND ? "Vincular" : "F")));
         JPWRaizCreateButton(JPW_ACTION_LEGACY_APPLY,action,x+3*(button_width+g_details_pad),footer_y,button_width);
        }
     }
   g_raiz_panel_built=true; JPWFocusPaint();
  }
#endif

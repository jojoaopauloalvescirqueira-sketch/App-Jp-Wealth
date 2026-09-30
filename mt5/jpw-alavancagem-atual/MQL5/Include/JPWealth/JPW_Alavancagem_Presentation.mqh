#ifndef JPW_ALAVANCAGEM_PRESENTATION_MQH
#define JPW_ALAVANCAGEM_PRESENTATION_MQH
// Indicator runtime component; included after its instance state.

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
   const int available=chart_width-16-2*pad;
   if(available<30 || !TextSetFont("Arial",-10*InpFontSize,FW_NORMAL))
     { JPWClearPanel(); return; }
   const color chart_background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   JPWCockpitPrefs prefs=g_cockpit_prefs;
   if(g_raiz_details_open && g_raiz_tab==JPW_ROUTE_SETTINGS) prefs=g_cockpit_draft;
   const color foreground=JPWPanelTextColor(chart_background,InpFontColor);
   const color surface=JPWPanelSurface(chart_background);
   uint measured=0,text_height=0;
   if(!TextGetSize("Mg",measured,text_height) || text_height==0)
     { JPWClearPanel(); return; }
   const int gap=(prefs.density==0 ? 2 : (int)text_height/2+2);
   const int row_height=(int)text_height+gap;
   const int button_height=(int)text_height+8;
   string shown[JPW_COCKPIT_METRIC_COUNT];
   int active=0,max_text=0;
   string compact_title[JPW_COCKPIT_METRIC_COUNT]={"Lev","P/L","SL","RN1W","RN2W","Risk"};
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
     {
      shown[i]="";
      if(!JPWCockpitVisible(prefs,i)) continue;
      JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
      const bool observer_missing=(i==5 && metric.quality==JPW_VIEW_NA &&
         g_stop_observer_presence==JPW_OBSERVER_NOT_CONFIRMED);
      shown[i]=(observer_missing ? "Stop risk: N/A · Check Observer" :
         (i==0 ? "JPW: " : "")+metric.title+" "+metric.value+
         " · "+JPWCockpitQualityText(metric.quality));
      if(!TextGetSize(shown[i],measured,text_height) || (int)measured>available)
         shown[i]=(observer_missing ? "Risk: N/A · Check Observer" :
            compact_title[i]+": "+metric.value+" · "+JPWCockpitQualityText(metric.quality));
      if(!TextGetSize(shown[i],measured,text_height) || (int)measured>available)
        { active=-1; break; } // Show a complete summary instead of cutting values.
      if((int)measured>max_text) max_text=(int)measured;
      active++;
     }
   bool summary=(active<0 || active*row_height+button_height+3*pad>chart_height-8);
   g_hud_summary=summary || active==0;
   g_hud_summary_source=-1;
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
                         " · "+JPWCockpitQualityText(g_cockpit_snapshot.metric[i].quality));
             g_hud_summary_source=i; break; }
      if(!TextGetSize(shown[0],measured,text_height) || (int)measured>available)
         { shown[0]="JPW · Cockpit"; g_hud_summary_source=-1; }
      TextGetSize(shown[0],measured,text_height);
      max_text=(int)measured;
      active=1;
     }
   if(active==0)
     {
      shown[0]="JPW · Open Cockpit";
      TextGetSize(shown[0],measured,text_height);
      if((int)measured>available) { shown[0]="JPW · Cockpit"; g_hud_summary_source=-1; }
      TextGetSize(shown[0],measured,text_height);
      max_text=(int)measured;
      active=1;
     }
   uint button_text_width=0,button_text_height=0;
   TextGetSize("Cockpit",button_text_width,button_text_height);
   const int button_width=(int)button_text_width+2*pad;
   const int width=(max_text>button_width ? max_text : button_width)+2*pad;
   const int height=active*row_height+button_height+3*pad;
   JPWPanelRect hud;
   const bool lower=(prefs.corner==CORNER_LEFT_LOWER ||
                     prefs.corner==CORNER_RIGHT_LOWER);
   const bool right=(prefs.corner==CORNER_RIGHT_UPPER ||
                     prefs.corner==CORNER_RIGHT_LOWER);
   const int header_safe=((int)text_height*3+10>44 ? (int)text_height*3+10 : 44);
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
   ObjectSetInteger(0,bg,OBJPROP_COLOR,foreground);
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
   ObjectSetInteger(0,button,OBJPROP_FONTSIZE,InpFontSize);
   ObjectSetInteger(0,button,OBJPROP_COLOR,foreground);
   ObjectSetInteger(0,button,OBJPROP_BGCOLOR,surface);
   ObjectSetInteger(0,button,OBJPROP_ZORDER,4);
   ObjectSetInteger(0,button,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,button,OBJPROP_HIDDEN,true);
   ObjectSetString(0,button,OBJPROP_TEXT,"Cockpit");
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
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_text) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,font) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,3) &&
          ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) &&
          ObjectSetString(0,name,OBJPROP_FONT,"Arial") &&
          ObjectSetString(0,name,OBJPROP_TEXT,shown) &&
          ObjectSetString(0,name,OBJPROP_TOOLTIP,value));
  }

bool JPWCreateProtectedValue(const string suffix,const string value,const int x,
                              const int y,const int width)
  {
   uint measured=0,height=0;
   if(!TextSetFont("Arial",-10*g_details_font,FW_NORMAL) ||
      !TextGetSize(value,measured,height)) return(false);
   const string shown=((int)measured<=width ? value : "Ver valor no detalhe");
   const bool made=JPWRaizCreateLabel(suffix,shown,x,y);
   if(made) ObjectSetString(0,JPWRaizUI(suffix),OBJPROP_TOOLTIP,value);
   return(made);
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
          ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,C'160,160,160') &&
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
      ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,
                       g_focus_actions[i]==g_focus_action ? g_details_text : C'118,118,118');
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
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,width) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,g_details_control) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_details_font) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_text) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,g_details_surface) &&
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

void JPWRenderStopsTable(const int x,const int body_y,const int inner,
                         const int body_height,const int footer_y)
  {
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
   const int column_width=(inner-g_details_pad)/2;
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
      if(layout.value_lines==1)
        {
         JPWCreateProtectedValue("STOP_AMOUNT_"+IntegerToString(j),amount,
            x,table_y+j*row_height+g_details_control,column_width);
         JPWCreateProtectedValue("STOP_PERCENT_"+IntegerToString(j),percent+" balance",
            x+column_width+g_details_pad,
            table_y+j*row_height+g_details_control,column_width);
        }
      else if(layout.value_lines==2)
        {
         JPWCreateProtectedValue("STOP_AMOUNT_"+IntegerToString(j),amount,
            x,table_y+j*row_height+g_details_control,inner);
         JPWCreateProtectedValue("STOP_PERCENT_"+IntegerToString(j),percent+" balance",
            x,table_y+j*row_height+g_details_control+g_details_line,inner);
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
   const int chart_width=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int chart_height=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   g_details_font=InpCockpitFontSize;
   uint text_width=0,text_height=0;
   if(!TextSetFont("Arial",-10*g_details_font,FW_NORMAL) ||
      !TextGetSize("Mg",text_width,text_height) || text_height==0 ||
      !JPWPanelCockpit(chart_width,chart_height,760,620,g_details_rect)) return;
   g_details_pad=((int)text_height/2>6 ? (int)text_height/2 : 6);
   g_details_line=(int)text_height+g_details_pad;
   g_details_control=(int)text_height+2*g_details_pad;
   const color chart_background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   g_details_text=JPWPanelTextColor(chart_background,C'60,60,60');
   g_details_surface=JPWPanelSurface(chart_background);
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
   ObjectSetInteger(0,bg,OBJPROP_COLOR,g_details_text);
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
         JPWRaizCreateLabel("TITLE","JPW · amplie o gráfico",x,top+g_details_pad);
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
   const string section=(g_raiz_tab==JPW_ROUTE_OVERVIEW ? "Visão geral" :
      (g_raiz_tab==JPW_ROUTE_METRIC ? g_cockpit_snapshot.metric[g_cockpit_selected].title :
      (g_raiz_tab==JPW_ROUTE_PROVENANCE ? "Estado dos dados" :
      (g_raiz_tab==JPW_ROUTE_SETTINGS ? "Ajustes" :
      (g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW ? "Stops" :
      (g_raiz_tab==JPW_ROUTE_RAIZN ? "Raiz N" : "Sistema"))))));
   JPWRaizCreateLabel("TITLE",JPWFitText("JPW · "+_Symbol+" · "+section,
                       inner-g_details_control-g_details_pad,g_details_font),x,top+g_details_pad);
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
        { ObjectSetInteger(0,JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_TAB_FIRST+i)),OBJPROP_BGCOLOR,g_details_text);
          ObjectSetInteger(0,JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_TAB_FIRST+i)),OBJPROP_COLOR,g_details_surface); }
     }
   ObjectSetString(0,JPWActionObject(JPW_ACTION_TAB_FIRST),OBJPROP_TOOLTIP,
                   "Teclas 1–6: cartões; setas: páginas; Esc: fechar.");
   const int close_size=(g_details_control>24 ? g_details_control : 24);
   // The close button stays visible even when content has to paginate.
   JPWRaizCreateButton(JPW_ACTION_CLOSE,"×",left+g_details_rect.width-g_details_pad-close_size,
                       top+g_details_pad,close_size);
   const int body_y=nav_y+(stacked ? 2 : 1)*(g_details_control+g_details_pad);
   const int footer_y=top+g_details_rect.height-g_details_pad-g_details_control;
   const int reserved=(g_raiz_tab==JPW_ROUTE_SETTINGS || (g_raiz_tab==JPW_ROUTE_OVERVIEW && g_cockpit_pref_invalid) ?
                       2*g_details_line : g_details_line);
   const int body_height=footer_y-g_details_pad-body_y-reserved;
   const int footer_button=(inner-2*g_details_pad)/3;
   if(body_height<g_details_control || footer_button<35)
     {
      if(body_y+g_details_line<footer_y)
         JPWRaizCreateLabel("FEEDBACK","Amplie o gráfico para ver o cockpit",x,body_y);
      JPWRaizCreateButton(JPW_ACTION_CLOSE,"Fechar",x,footer_y,inner);
      g_raiz_panel_built=true;
      return;
     }
   if(g_raiz_tab==JPW_ROUTE_OVERVIEW)
     {
      const int columns=(inner>=600 ? 2 : 1);
      const int card_width=(inner-(columns-1)*g_details_pad)/columns;
      const int card_height=g_details_control+3*g_details_line+g_details_pad;
      const int rows=body_height/card_height;
      const int capacity=(rows>0 ? rows*columns : 1);
      const int pages=(JPW_COCKPIT_METRIC_COUNT+capacity-1)/capacity;
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
      for(int j=0;j<capacity && g_cockpit_page*capacity+j<JPW_COCKPIT_METRIC_COUNT;j++)
        {
         const int i=g_cockpit_page*capacity+j;
         const int cx=x+(j%columns)*(card_width+g_details_pad);
         const int y=body_y+(j/columns)*card_height;
         JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];
         JPWRaizCreateButton(JPW_ACTION_CARD_FIRST+i,metric.title+(rows==0 ? " · detalhe" : ""),cx,y,card_width);
         if(rows==0)
           {
            if(body_height>=g_details_control+g_details_line)
               JPWRaizCreateLabel("SMALL_CARD","Amplie para ver o cartão completo",cx,y+g_details_control);
            continue;
           }
         const string suffix="CARD_"+IntegerToString(i);
         JPWCreateProtectedValue(suffix+"_VALUE",metric.value,cx,
                                  y+g_details_control,card_width);
         JPWRaizCreateLabel(suffix+"_QUALITY",JPWCockpitQualityText(metric.quality),
                              cx,y+g_details_control+g_details_line);
         JPWRaizCreateLabel(suffix+"_REASON",JPWFitText(metric.reason,card_width,g_details_font),
                              cx,y+g_details_control+2*g_details_line);
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
   else if(g_raiz_tab==JPW_ROUTE_SETTINGS)
     {
      string names[JPW_COCKPIT_METRIC_COUNT]={"Leverage","Floating P/L","Genesis SL","Raiz N 1W","Raiz N 2W","Stop risk"};
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
         JPWDetailsWrap(metric.title+": "+metric.value+" · "+JPWCockpitQualityText(metric.quality),inner,lines);
         JPWDetailsWrap("Estado: "+metric.reason,inner,lines);
         JPWDetailsWrap("Amostra "+IntegerToString(metric.sample.id)+" · "+metric.sample.source+
            " · unidade "+metric.sample.unit+" · código "+IntegerToString((int)metric.sample.reason_code)+
            ". Observada em "+TimeToString((datetime)metric.sample.observed_utc,TIME_DATE|TIME_SECONDS)+
            " UTC (computador). Redesenhar não cria outra amostra.",inner,lines);
         string formulas[JPW_COCKPIT_METRIC_COUNT]={"Nocional bruto de todas as posições / último equity informado pelo terminal.",
           "100 × lucro flutuante / saldo.","Distância da cotação Bid (compra) ou Ask (venda) ao SL local da referência; percentual do preço.",
           "100 × ATR(55,H4) × √N(1W) × F / preço médio do mesmo tick.",
           "100 × ATR(55,H4) × √N(2W) × F / preço médio do mesmo tick.",
           "Soma do risco de posições abertas (execução até SL, piso zero) e reservas de pendentes ampliadoras atribuídas. Percentual informativo sobre balance atual."};
         JPWDetailsWrap("Fórmula: "+formulas[i],inner,lines);
         JPWDetailsWrap("Insumos, origem e horário: "+metric.detail,inner,lines);
         if(i==3 || i==4)
            JPWDetailsWrap("Limite: escala diagnóstica; Current qualifica os dados, não homologa P-21 nem decide stop, lote ou entrada.",inner,lines);
         if(i==2)
            JPWDetailsWrap("Limite: SL local sem confirmação de execução; referência inferida não certifica a Gênese.",inner,lines);
         if(i==5)
            JPWDetailsWrap("Limite: não é Risco Comprometido, limite de fase ou perda máxima garantida. Custos, perdas realizadas, gaps e slippage ficam fora.",inner,lines);
        }
      else if(g_raiz_tab==JPW_ROUTE_STOP_ROW)
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
         JPWDetailsWrap("JPW Cockpit "+JPW_PRODUCT_VERSION+" · cálculo "+JPW_CALCULATION_VERSION+
                         " · build "+JPW_BUILD_ID,inner,lines);
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
      string first_action="Stops",second_action="Raiz N";
      if(g_raiz_tab==JPW_ROUTE_METRIC)
        { first_action="Visão geral"; second_action="Proveniência"; }
      else if(g_raiz_tab==JPW_ROUTE_PROVENANCE)
        { first_action="Sistema"; second_action="Atualizar"; }
      else if(g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW)
        { first_action="Posições"; second_action="Pendentes"; }
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
   JPWRaizCreateButton(JPW_ACTION_PREVIOUS,"‹",x+inner-2*pager_width-g_details_pad,
                        footer_y-g_details_line,pager_width);
   JPWRaizCreateButton(JPW_ACTION_NEXT,"›",x+inner-pager_width,
                        footer_y-g_details_line,pager_width);
   ObjectSetInteger(0,JPWActionObject(JPW_ACTION_PREVIOUS),OBJPROP_YSIZE,g_details_line);
   ObjectSetInteger(0,JPWActionObject(JPW_ACTION_NEXT),OBJPROP_YSIZE,g_details_line);
   g_raiz_panel_built=true; JPWFocusPaint();
  }

void JPWRenderRaizDetails()
  {
   if(!g_raiz_details_open || !JPWDetailsContextCurrent()) return;
   if(g_raiz_panel_built) return;
   if(g_raiz_tab>=JPW_ROUTE_OVERVIEW) { JPWRenderCockpit(); return; }
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   g_details_text=JPWPanelTextColor(background,C'60,60,60'); g_details_surface=JPWPanelSurface(background);
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
   ObjectSetInteger(0,bg,OBJPROP_COLOR,C'118,118,118');
   ObjectSetInteger(0,bg,OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSetInteger(0,bg,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,bg,OBJPROP_BACK,false);
   ObjectSetInteger(0,bg,OBJPROP_ZORDER,1);
   ObjectSetInteger(0,bg,OBJPROP_HIDDEN,true);
   JPWRaizCreateLabel("TITLE","JPW · "+_Symbol+" · "+
      (g_raiz_tab==JPW_ROUTE_LEGACY_SUMMARY ? "Resumo" : (g_raiz_tab==JPW_ROUTE_LEGACY_NF ? "N/F legado" :
       (g_raiz_tab==JPW_ROUTE_FACTOR ? "F diagnóstico" : "Cenários avançados"))),x,top+g_details_pad);
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
      JPWRaizCreateLabel("TITLE","JPW · "+IntegerToString(g_raiz_page+1)+"/"+IntegerToString(g_raiz_pages)+" · "+_Symbol,x,top+g_details_pad);
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

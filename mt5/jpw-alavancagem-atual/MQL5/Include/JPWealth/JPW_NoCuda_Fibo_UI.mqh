#ifndef JPW_NOCUDA_FIBO_UI_MQH
#define JPW_NOCUDA_FIBO_UI_MQH

// Presentation only: receives accepted strings/identities from the controller.
// No account, candle, native-channel or study-store reads occur in this file.
#include <JPWealth/JPW_Genetrix_Brand.mqh>
#include <JPWealth/JPW_UI_Design.mqh>
#include <JPWealth/JPW_NoCuda_UI.mqh>

struct JPWNoCudaFiboUIItem
  { string id; string title; string detail; string state; bool selected; };
struct JPWNoCudaFiboUIMetric
  {
   bool valid; bool highlight;
   string label; string raw_level; string price; string nominal;
   string points; string percent; string state; string reason;
  };
struct JPWNoCudaFiboView
  {
   bool open; bool linked; bool preview; bool draft_pending;
   bool source_hidden; bool sync_paused;
   int tab;
   string symbol; string source_name; string source_tf; string status; string reason;
   string quote_text; string selected_text; string selected_value; string selected_distance;
   string projection_date; string justification; string observation_time; string observation_note;
   string record_detail; string provenance;
   string projection_labels[5]; string projection_values[5];
   JPWNoCudaFiboUIItem sources[]; JPWNoCudaFiboUIItem records[];
   JPWNoCudaFiboUIMetric below; JPWNoCudaFiboUIMetric above;
   JPWNoCudaFiboUIMetric nearest; JPWNoCudaFiboUIMetric selected;
  };
struct JPWNoCudaFiboUIPrefs
  {
   int x; int y; int width; int height;
   int font; int density; int launcher; int mesh; int preset;
  };
struct JPWNoCudaFiboUILayout
  {
   int x; int y; int width; int height; int pad; int line; int button;
   int body_y; int body_height; int footer_y; int inner; int nav_columns; int nav_rows;
   bool narrow; bool usable;
  };

JPWNoCudaFiboUIPrefs g_fc_pref,g_fc_draft;
JPWNoCudaFiboUILayout g_fc_layout;
bool g_fc_initialized=false,g_fc_pref_invalid=false,g_fc_settings_dirty=false;
bool g_fc_gesture=false,g_fc_resize=false,g_fc_mouse_down=false;
int g_fc_pointer_x=0,g_fc_pointer_y=0,g_fc_start_x=0,g_fc_start_y=0;
int g_fc_start_w=0,g_fc_start_h=0,g_fc_scroll=0,g_fc_scroll_max=0,g_fc_tab=-1;
string g_fc_notice="",g_fc_editing="",g_fc_focus="";
string g_fc_keep[],g_fc_actions[],g_fc_action_ids[];
int g_fc_line_cursor=0,g_fc_visible_lines=0;
bool g_fc_measure_pass=false;
color g_fc_ink,g_fc_muted,g_fc_surface,g_fc_chrome,g_fc_card,g_fc_border,g_fc_accent;

int JPWNoCudaFiboUIClamp(const int v,const int a,const int b)
  { return(MathMax(a,MathMin(v,b))); }
int JPWNoCudaFiboUITextWidth(const string value,const int font)
  {
   uint w=0,h=0;
   if(TextSetFont("Arial",-10*font) && TextGetSize(value,w,h)) return((int)w);
   return(StringLen(value)*MathMax(JPWUIDesignPx(5),JPWUIDesignPx(font*6/10)));
  }
int JPWNoCudaFiboUILine(const int font)
  {
   uint w=0,h=0;
   if(TextSetFont("Arial",-10*font) && TextGetSize("Ag",w,h) && h>0)
      return(MathMax(JPWUIDesignPx(font+4),(int)h+JPWUIDesignPx(8)));
   return(JPWUIDesignPx(font+12));
  }
bool JPWNoCudaFiboUIDark()
  {
   const int c=(int)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   return(299*(c&255)+587*((c>>8)&255)+114*((c>>16)&255)<140000);
  }
string JPWNoCudaFiboUIName(const string prefix,const string action)
  { return(prefix+"FC_"+action); }
void JPWNoCudaFiboUIKeep(const string name)
  { const int n=ArraySize(g_fc_keep); ArrayResize(g_fc_keep,n+1); g_fc_keep[n]=name; }
bool JPWNoCudaFiboUIEnsure(const string name,const ENUM_OBJECT type)
  {
   JPWNoCudaFiboUIKeep(name);
   if(ObjectFind(0,name)>=0)
     {
      if(ObjectGetInteger(0,name,OBJPROP_TYPE)==type) return(true);
      ObjectDelete(0,name);
     }
   return(ObjectCreate(0,name,type,0,0,0));
  }
void JPWNoCudaFiboUISetText(const string name,const ENUM_OBJECT_PROPERTY_STRING prop,const string value)
  { if(ObjectGetString(0,name,prop)!=value) ObjectSetString(0,name,prop,value); }
void JPWNoCudaFiboUIPosition(const string name,const int x,const int y,const int w,const int h,const int z)
  {
   ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x); ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);
   ObjectSetInteger(0,name,OBJPROP_XSIZE,w); ObjectSetInteger(0,name,OBJPROP_YSIZE,h);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true); ObjectSetInteger(0,name,OBJPROP_ZORDER,z);
  }
void JPWNoCudaFiboUIBox(const string name,const int x,const int y,const int w,const int h,
                       const color fill,const color border)
  {
   if(w<=0 || h<=0 || !JPWNoCudaFiboUIEnsure(name,OBJ_RECTANGLE_LABEL)) return;
   JPWNoCudaFiboUIPosition(name,x,y,w,h,990);
   ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill); ObjectSetInteger(0,name,OBJPROP_COLOR,border);
   ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
  }
string JPWNoCudaFiboUIFit(const string value,const int width,const int font)
  {
   if(JPWNoCudaFiboUITextWidth(value,font)<=width) return(value);
   int n=StringLen(value);
   while(n>0 && JPWNoCudaFiboUITextWidth(StringSubstr(value,0,n)+"…",font)>width) n--;
   return(StringSubstr(value,0,n)+"…");
  }
void JPWNoCudaFiboUILabel(const string name,const int x,const int y,const int w,
                         const string value,const int font,const color ink,const bool fit=true)
  {
   if(!JPWNoCudaFiboUIEnsure(name,OBJ_LABEL)) return;
   JPWNoCudaFiboUIPosition(name,x,y,w,JPWNoCudaFiboUILine(font),1000);
   ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   ObjectSetInteger(0,name,OBJPROP_FONTSIZE,font); ObjectSetInteger(0,name,OBJPROP_COLOR,ink);
   ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
   JPWNoCudaFiboUISetText(name,OBJPROP_FONT,"Arial");
   JPWNoCudaFiboUISetText(name,OBJPROP_TEXT,fit ? JPWNoCudaFiboUIFit(value,w,font) : value);
   JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,value);
  }
void JPWNoCudaFiboUIEdit(const string name,const int x,const int y,const int w,const int h,
                        const string value,const bool readonly=false)
  {
   const bool exists=ObjectFind(0,name)>=0;
   if(!JPWNoCudaFiboUIEnsure(name,OBJ_EDIT)) return;
   JPWNoCudaFiboUIPosition(name,x,y,w,h,1002);
   ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_fc_draft.font);
   ObjectSetInteger(0,name,OBJPROP_COLOR,g_fc_ink); ObjectSetInteger(0,name,OBJPROP_BGCOLOR,g_fc_card);
   ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,name==g_fc_focus ? g_fc_accent : g_fc_border);
   ObjectSetInteger(0,name,OBJPROP_READONLY,readonly);
   JPWNoCudaFiboUISetText(name,OBJPROP_FONT,"Arial");
   if(!exists || name!=g_fc_editing) JPWNoCudaFiboUISetText(name,OBJPROP_TEXT,value);
   JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,value);
  }
void JPWNoCudaFiboUIValue(const string name,const int x,const int y,const int w,const string value)
  {
   // Preserve the whole numeric string. A narrow read-only field supports
   // native horizontal selection, whose interaction remains a native gate.
   if(JPWNoCudaFiboUITextWidth(value,g_fc_draft.font)>w)
      JPWNoCudaFiboUIEdit(name,x,y,w,g_fc_layout.line,value,true);
   else JPWNoCudaFiboUILabel(name,x,y,w,value,g_fc_draft.font,g_fc_ink,false);
  }
void JPWNoCudaFiboUIButton(const string prefix,const string action,const int x,const int y,
                          const int w,const int h,const string text,const bool primary=false,
                          const string item_id="")
  {
   const string name=JPWNoCudaFiboUIName(prefix,action);
   if(w<=0 || h<=0 || !JPWNoCudaFiboUIEnsure(name,OBJ_BUTTON)) return;
   JPWNoCudaFiboUIPosition(name,x,y,w,h,1005);
   ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_fc_draft.font);
   ObjectSetInteger(0,name,OBJPROP_COLOR,primary ? C'255,255,255' : g_fc_ink);
   ObjectSetInteger(0,name,OBJPROP_BGCOLOR,primary ? g_fc_accent : g_fc_chrome);
   ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,name==g_fc_focus ? g_fc_accent : g_fc_border);
   ObjectSetInteger(0,name,OBJPROP_STATE,false);
   JPWNoCudaFiboUISetText(name,OBJPROP_FONT,"Arial");
   JPWNoCudaFiboUISetText(name,OBJPROP_TEXT,JPWNoCudaFiboUIFit(text,w-JPWUIDesignPx(24),g_fc_draft.font));
   JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,text);
   const int n=ArraySize(g_fc_actions); ArrayResize(g_fc_actions,n+1); ArrayResize(g_fc_action_ids,n+1);
   g_fc_actions[n]=action; g_fc_action_ids[n]=item_id;
  }
void JPWNoCudaFiboUIFinish(const string prefix)
  {
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,prefix+"FC_")!=0) continue;
      bool keep=false;
      for(int k=0;k<ArraySize(g_fc_keep);k++) if(g_fc_keep[k]==name) { keep=true; break; }
      if(!keep)
        { if(StringFind(name,"_DESIGN_ICON")>=0) JPWUIDesignDeleteIcon(name);
          else ObjectDelete(0,name); if(g_fc_focus==name) g_fc_focus="";
          if(g_fc_editing==name) g_fc_editing=""; }
     }
  }
void JPWNoCudaFiboUIClear(const string prefix)
  {
   ArrayResize(g_fc_keep,0); JPWNoCudaFiboUIFinish(prefix);
   g_fc_focus=""; g_fc_editing=""; g_fc_gesture=false; g_fc_mouse_down=false;
  }

void JPWNoCudaFiboUIDefault(JPWNoCudaFiboUIPrefs &p,const int preset=1)
  {
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   p.width=(preset==0 ? MathMin(680,cw-24) : preset==2 ? cw-16 : cw*9/10);
   p.height=(preset==0 ? MathMin(520,ch-24) : preset==2 ? ch-16 : ch*9/10);
   p.width=MathMax(24,p.width); p.height=MathMax(24,p.height);
   p.x=(cw-p.width)/2; p.y=(ch-p.height)/2;
   // Keep the initial launcher away from MT5's instrument header and HUD.
   p.font=11; p.density=0; p.launcher=2; p.mesh=1; p.preset=preset;
  }
void JPWNoCudaFiboUIBounds(JPWNoCudaFiboUIPrefs &p)
  {
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   p.width=JPWNoCudaFiboUIClamp(p.width,24,MathMax(24,cw-8));
   p.height=JPWNoCudaFiboUIClamp(p.height,24,MathMax(24,ch-8));
   p.x=JPWNoCudaFiboUIClamp(p.x,4,MathMax(4,cw-p.width-4));
   p.y=JPWNoCudaFiboUIClamp(p.y,4,MathMax(4,ch-p.height-4));
   p.font=JPWNoCudaFiboUIClamp(p.font,9,24);
  }
string JPWNoCudaFiboUIPrefName() { return("JPW_NOCUDA_FIBO_VISUAL_V1"); }
void JPWNoCudaFiboUILoadPrefs()
  {
   JPWNoCudaFiboUIDefault(g_fc_pref); g_fc_pref_invalid=false;
   const string name=JPWNoCudaFiboUIPrefName();
   if(ObjectFind(0,name)>=0)
     {
      string f[]; const string text=ObjectGetString(0,name,OBJPROP_TOOLTIP);
      bool valid=StringSplit(text,'|',f)==10 && f[0]=="V1";
      int v[9];
      if(valid) for(int i=0;i<9;i++)
        { v[i]=(int)StringToInteger(f[i+1]); if(f[i+1]!=IntegerToString(v[i])) valid=false; }
      if(valid) valid=v[0]>=0 && v[1]>=0 && v[2]>=24 && v[3]>=24 && v[4]>=9 && v[4]<=24 &&
         v[5]>=0 && v[5]<=1 && v[6]>=0 && v[6]<=3 && v[7]>=0 && v[7]<=1 && v[8]>=0 && v[8]<=2;
      if(valid)
        { g_fc_pref.x=v[0]; g_fc_pref.y=v[1]; g_fc_pref.width=v[2]; g_fc_pref.height=v[3];
          g_fc_pref.font=v[4]; g_fc_pref.density=v[5]; g_fc_pref.launcher=v[6]; g_fc_pref.mesh=v[7]; g_fc_pref.preset=v[8]; }
      else { g_fc_pref_invalid=true; g_fc_notice="Preferência visual inválida; objeto original preservado."; }
     }
   JPWNoCudaFiboUIBounds(g_fc_pref); g_fc_draft=g_fc_pref; g_fc_initialized=true;
  }
bool JPWNoCudaFiboUISavePrefs()
  {
   JPWNoCudaFiboUIBounds(g_fc_pref);
   const string name=JPWNoCudaFiboUIPrefName();
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_LABEL,0,0,0))
     { g_fc_notice="Não foi possível guardar a preferência visual."; return(false); }
   const string text="V1|"+IntegerToString(g_fc_pref.x)+"|"+IntegerToString(g_fc_pref.y)+"|"+
      IntegerToString(g_fc_pref.width)+"|"+IntegerToString(g_fc_pref.height)+"|"+
      IntegerToString(g_fc_pref.font)+"|"+IntegerToString(g_fc_pref.density)+"|"+
      IntegerToString(g_fc_pref.launcher)+"|"+IntegerToString(g_fc_pref.mesh)+"|"+IntegerToString(g_fc_pref.preset);
   ObjectSetInteger(0,name,OBJPROP_XDISTANCE,-10000); ObjectSetInteger(0,name,OBJPROP_YDISTANCE,-10000);
   ObjectSetInteger(0,name,OBJPROP_HIDDEN,true); ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false);
   if(!ObjectSetString(0,name,OBJPROP_TOOLTIP,text) || ObjectGetString(0,name,OBJPROP_TOOLTIP)!=text)
     { g_fc_notice="Preferência visual não confirmada."; return(false); }
   g_fc_pref_invalid=false; return(true);
  }
void JPWNoCudaFiboUICalculateLayout()
  {
   JPWNoCudaFiboUIBounds(g_fc_draft);
   g_fc_layout.x=g_fc_draft.x; g_fc_layout.y=g_fc_draft.y;
   g_fc_layout.width=g_fc_draft.width; g_fc_layout.height=g_fc_draft.height;
   g_fc_layout.line=JPWNoCudaFiboUILine(g_fc_draft.font);
   g_fc_layout.pad=JPWUIDesignPx(g_fc_draft.density==1 ? 8 : 12);
   g_fc_layout.button=JPWUIDesignControlHeight(g_fc_layout.line);
   g_fc_layout.inner=g_fc_layout.width-2*g_fc_layout.pad;
   g_fc_layout.narrow=g_fc_layout.inner<JPWUIDesignPx(650);
   string tabs[5]={"Canal","Agora","Projeção","Registro","Aparência"};
   const int gap=JPWUIDesignPx(8);
   g_fc_layout.nav_columns=JPWUIDesignNavColumns(tabs,5,g_fc_layout.inner,g_fc_draft.font,gap);
   g_fc_layout.nav_rows=(5+g_fc_layout.nav_columns-1)/g_fc_layout.nav_columns;
   const int header=g_fc_layout.button+JPWUIDesignPx(16)+
      (g_fc_layout.narrow ? 0 : g_fc_layout.line)+g_fc_layout.nav_rows*(g_fc_layout.button+gap)+gap;
   g_fc_layout.body_y=g_fc_layout.y+header;
   // Reserve an independent minimum target strip for the resize handle.
   g_fc_layout.footer_y=g_fc_layout.y+g_fc_layout.height-g_fc_layout.button-g_fc_layout.pad-JPWUIDesignPx(40);
   g_fc_layout.body_height=MathMax(0,g_fc_layout.footer_y-g_fc_layout.body_y-gap);
   g_fc_layout.usable=g_fc_layout.inner>=JPWUIDesignPx(140) &&
      JPWUIDesignButtonWidth("Aparência",g_fc_draft.font)<=g_fc_layout.inner &&
      g_fc_layout.body_height>=2*g_fc_layout.line;
   g_fc_visible_lines=MathMax(1,g_fc_layout.body_height/g_fc_layout.line);
  }
string JPWNoCudaFiboUIHitAction(const string prefix,const string object)
  {
   if(StringFind(object,prefix+"FC_FC_")!=0) return("");
   const string action=StringSubstr(object,StringLen(prefix+"FC_"));
   if(action=="FC_HEADER_CLOSE") return("FC_CLOSE");
   if(action=="FC_HEADER_MINIMIZE") return("FC_MINIMIZE");
   return(action);
  }
string JPWNoCudaFiboUIActionID(const string action)
  { for(int i=0;i<ArraySize(g_fc_actions);i++) if(g_fc_actions[i]==action) return(g_fc_action_ids[i]); return(""); }
string JPWNoCudaFiboUIFocusCycle(const string current,const bool reverse)
  {
   const int count=ArraySize(g_fc_keep); int at=(reverse ? 0 : -1);
   for(int i=0;i<count;i++) if(g_fc_keep[i]==current) { at=i; break; }
   for(int i=1;i<=count;i++)
     {
      const string name=g_fc_keep[(at+(reverse ? -i : i)+2*count)%count];
      const long kind=ObjectGetInteger(0,name,OBJPROP_TYPE);
      if(ObjectFind(0,name)>=0 && (kind==OBJ_BUTTON ||
         (kind==OBJ_EDIT && !ObjectGetInteger(0,name,OBJPROP_READONLY)))) return(name);
     }
   return("");
  }
void JPWNoCudaFiboUIFieldCapture(const string prefix,JPWNoCudaFiboView &v)
  {
   const string names[5]={"FC_DATE","FC_OBS_TIME","FC_OBS_NOTE","FC_JUST","FC_LEVEL_VALUE"};
   for(int i=0;i<5;i++)
     {
      const string name=JPWNoCudaFiboUIName(prefix,names[i]);
      if(ObjectFind(0,name)<0) continue;
      const string value=ObjectGetString(0,name,OBJPROP_TEXT);
      if(i==0) v.projection_date=value; if(i==1) v.observation_time=value;
      if(i==2) v.observation_note=value; if(i==3) v.justification=value;
      if(i==4) v.selected_value=value;
     }
  }
void JPWNoCudaFiboUIScroll(const int delta)
  { g_fc_scroll=JPWNoCudaFiboUIClamp(g_fc_scroll+delta,0,g_fc_scroll_max); }
bool JPWNoCudaFiboUIActions(const string action)
  {
   if(action=="FC_SCROLL_UP") { JPWNoCudaFiboUIScroll(-1); return(true); }
   if(action=="FC_SCROLL_DOWN") { JPWNoCudaFiboUIScroll(1); return(true); }
   if(StringFind(action,"FC_PRESET_")==0)
     {
      const int preset=(int)StringToInteger(StringSubstr(action,10));
      if(preset<0 || preset>2) return(false);
      const int font=g_fc_draft.font,density=g_fc_draft.density,corner=g_fc_draft.launcher,mesh=g_fc_draft.mesh;
      JPWNoCudaFiboUIDefault(g_fc_draft,preset);
      g_fc_draft.font=font; g_fc_draft.density=density; g_fc_draft.launcher=corner; g_fc_draft.mesh=mesh;
      g_fc_settings_dirty=true; return(true);
     }
   if(action=="FC_FONT_MINUS" || action=="FC_FONT_PLUS")
     { g_fc_draft.font=JPWNoCudaFiboUIClamp(g_fc_draft.font+(action=="FC_FONT_PLUS" ? 1 : -1),9,24); g_fc_settings_dirty=true; return(true); }
   if(action=="FC_DENSITY") { g_fc_draft.density=1-g_fc_draft.density; g_fc_settings_dirty=true; return(true); }
   if(action=="FC_LAUNCHER") { g_fc_draft.launcher=(g_fc_draft.launcher+1)%4; g_fc_settings_dirty=true; return(true); }
   if(action=="FC_MESH") { g_fc_draft.mesh=1-g_fc_draft.mesh; g_fc_settings_dirty=true; return(true); }
   if(action=="FC_SETTINGS_DEFAULT") { JPWNoCudaFiboUIDefault(g_fc_draft); g_fc_settings_dirty=true; return(true); }
   if(action=="FC_SETTINGS_CANCEL") { g_fc_draft=g_fc_pref; g_fc_settings_dirty=false; return(true); }
   if(action=="FC_SETTINGS_APPLY")
     { g_fc_pref=g_fc_draft; const bool saved=JPWNoCudaFiboUISavePrefs();
       g_fc_settings_dirty=!saved; g_fc_notice=(saved ? "Preferência visual aplicada; template exige salvamento manual." : g_fc_notice); return(true); }
   return(false);
  }

// Only a completed UI gesture may save geometry. Mouse movement and rendering
// retain a draft; the coordinator routes focus and wheel events. Whether the
// native chart also scrolls underneath these objects requires isolated MT5 QA.
bool JPWNoCudaFiboUIHandleGeometry(const string prefix,const int id,const long &lparam,
                                 const double &dparam,const string &sparam)
  {
   // Object-click arrives after the click, not at mouse-down. It consumes an
   // owned handle but must not arm a new financial or geometry gesture.
   if(id==CHARTEVENT_OBJECT_CLICK && (sparam==JPWNoCudaFiboUIName(prefix,"FC_DRAG") ||
                                    sparam==JPWNoCudaFiboUIName(prefix,"FC_RESIZE")))
      return(true);
   if(id!=CHARTEVENT_MOUSE_MOVE) return(false);
   const int x=(int)lparam,y=(int)dparam;
   const bool down=((int)StringToInteger(sparam)&1)!=0;
   if(down && !g_fc_mouse_down && !g_fc_gesture)
     {
      const string handles[2]={"FC_DRAG","FC_RESIZE"};
      for(int i=0;i<2;i++)
        {
         const string name=JPWNoCudaFiboUIName(prefix,handles[i]);
         if(ObjectFind(0,name)<0) continue;
         const int hx=(int)ObjectGetInteger(0,name,OBJPROP_XDISTANCE),hy=(int)ObjectGetInteger(0,name,OBJPROP_YDISTANCE);
         if(x<hx || y<hy || x>=hx+(int)ObjectGetInteger(0,name,OBJPROP_XSIZE) || y>=hy+(int)ObjectGetInteger(0,name,OBJPROP_YSIZE)) continue;
         g_fc_gesture=true; g_fc_resize=i==1; g_fc_pointer_x=x; g_fc_pointer_y=y;
         g_fc_start_x=g_fc_draft.x; g_fc_start_y=g_fc_draft.y;
         g_fc_start_w=g_fc_draft.width; g_fc_start_h=g_fc_draft.height; break;
        }
     }
   g_fc_mouse_down=down;
   if(!g_fc_gesture) return(false);
   if(g_fc_resize)
     { g_fc_draft.width=g_fc_start_w+x-g_fc_pointer_x; g_fc_draft.height=g_fc_start_h+y-g_fc_pointer_y; }
   else { g_fc_draft.x=g_fc_start_x+x-g_fc_pointer_x; g_fc_draft.y=g_fc_start_y+y-g_fc_pointer_y; }
   JPWNoCudaFiboUIBounds(g_fc_draft);
   if(!down)
     {
      g_fc_gesture=false;
      // A geometry gesture does not apply an unfinished Appearance form.
      g_fc_pref.x=g_fc_draft.x; g_fc_pref.y=g_fc_draft.y;
      g_fc_pref.width=g_fc_draft.width; g_fc_pref.height=g_fc_draft.height;
      JPWNoCudaFiboUISavePrefs();
     }
   return(true);
  }

bool JPWNoCudaFiboUIRowVisible(const int lines,int &y)
  {
   const int start=g_fc_line_cursor; g_fc_line_cursor+=lines;
   if(g_fc_measure_pass) return(false);
   if(start<g_fc_scroll || start+lines>g_fc_scroll+g_fc_visible_lines) return(false);
   y=g_fc_layout.body_y+(start-g_fc_scroll)*g_fc_layout.line; return(true);
  }
void JPWNoCudaFiboUIRow(const string prefix,const string id,const string label,
                      const string value,const bool numeric=false)
  {
   int y=0; const int lines=(g_fc_layout.narrow ? 2 : 1);
   if(!JPWNoCudaFiboUIRowVisible(lines,y)) return;
   const int x=g_fc_layout.x+g_fc_layout.pad,w=g_fc_layout.inner;
   if(g_fc_layout.narrow)
     {
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_LABEL"),x,y,w,label,g_fc_draft.font,g_fc_muted);
      if(numeric) JPWNoCudaFiboUIValue(JPWNoCudaFiboUIName(prefix,id+"_VALUE"),x,y+g_fc_layout.line,w,value);
      else JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_VALUE"),x,y+g_fc_layout.line,w,value,g_fc_draft.font,g_fc_ink);
     }
   else
     {
      const int split=w/3;
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_LABEL"),x,y,split-JPWUIDesignPx(8),label,g_fc_draft.font,g_fc_muted);
      if(numeric) JPWNoCudaFiboUIValue(JPWNoCudaFiboUIName(prefix,id+"_VALUE"),x+split,y,w-split,value);
      else JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_VALUE"),x+split,y,w-split,value,g_fc_draft.font,g_fc_ink);
     }
  }
void JPWNoCudaFiboUIBodyButton(const string prefix,const string action,const string text,
                              const bool primary=false,const string item_id="")
  {
   const int lines=(g_fc_layout.button+g_fc_layout.line-1)/g_fc_layout.line;
   int y=0; if(!JPWNoCudaFiboUIRowVisible(lines,y)) return;
   JPWNoCudaFiboUIButton(prefix,action,g_fc_layout.x+g_fc_layout.pad,y,g_fc_layout.inner,
      g_fc_layout.button,text,primary,item_id);
  }
void JPWNoCudaFiboUIBodyEdit(const string prefix,const string action,const string label,const string value)
  {
   int caption_y=0;
   if(JPWNoCudaFiboUIRowVisible(1,caption_y))
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,action+"_CAPTION"),g_fc_layout.x+g_fc_layout.pad,
         caption_y,g_fc_layout.inner,label,g_fc_draft.font,g_fc_muted);
   const int lines=(g_fc_layout.button+g_fc_layout.line-1)/g_fc_layout.line;
   int y=0; if(JPWNoCudaFiboUIRowVisible(lines,y))
      JPWNoCudaFiboUIEdit(JPWNoCudaFiboUIName(prefix,action),g_fc_layout.x+g_fc_layout.pad,y,
         g_fc_layout.inner,g_fc_layout.button,value);
  }
void JPWNoCudaFiboUIRenderMetric(const string prefix,const string id,const string title,
                          const JPWNoCudaFiboUIMetric &m)
  {
   JPWNoCudaFiboUIBodyButton(prefix,"FC_USE_"+id,title+(m.highlight ? " · Mais próxima" : ""),m.highlight);
   JPWNoCudaFiboUIRow(prefix,id+"_LINE","Linha / nível bruto",m.label+" / "+m.raw_level);
   JPWNoCudaFiboUIRow(prefix,id+"_PRICE","Preço",m.valid ? m.price : "N/A",true);
   JPWNoCudaFiboUIRow(prefix,id+"_DELTA","Distância nominal",m.valid ? m.nominal : "N/A",true);
   JPWNoCudaFiboUIRow(prefix,id+"_POINTS","Pontos",m.valid ? m.points : "N/A",true);
   JPWNoCudaFiboUIRow(prefix,id+"_PERCENT","Percentual",m.valid ? m.percent : "N/A",true);
   JPWNoCudaFiboUIRow(prefix,id+"_STATE","Estado",m.state+" · "+m.reason);
  }

void JPWNoCudaFiboUICard(const string prefix,const string id,const string title,
                       const JPWNoCudaFiboUIMetric &m,const int x,const int y,const int width)
  {
   const int line=g_fc_layout.line,font=g_fc_draft.font,pad=JPWUIDesignPx(8);
   const int control_rows=(g_fc_layout.button+line-1)/line,content_y=y+control_rows*line;
   JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,id+"_CARD"),x,y,width,(control_rows+7)*line,
      g_fc_card,m.highlight ? g_fc_accent : g_fc_border);
   JPWNoCudaFiboUIButton(prefix,"FC_USE_"+id,x+pad,y,width-2*pad,g_fc_layout.button,
      title+(m.highlight ? " · Mais próxima" : ""),m.highlight);
   JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_LINE"),x+pad,content_y,width-2*pad,
      m.label+" · nível "+m.raw_level,font,g_fc_muted);
   JPWNoCudaFiboUIValue(JPWNoCudaFiboUIName(prefix,id+"_PRICE"),x+pad,content_y+line,width-2*pad,m.valid ? m.price : "N/A");
   string captions[3]={"Nominal","Pontos","Distância %"};
   string values[3]={m.nominal,m.points,m.percent};
   for(int i=0;i<3;i++)
     {
      const int split=width/3;
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_CAP_"+IntegerToString(i)),
         x+pad,content_y+(i+2)*line,split-pad,captions[i],font,g_fc_muted);
      JPWNoCudaFiboUIValue(JPWNoCudaFiboUIName(prefix,id+"_VAL_"+IntegerToString(i)),
         x+split,content_y+(i+2)*line,width-split-pad,m.valid ? values[i] : "N/A");
     }
   JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_STATE"),x+pad,content_y+5*line,width-2*pad,m.state,font,g_fc_muted);
   JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_REASON"),x+pad,content_y+6*line,width-2*pad,m.reason,font,g_fc_muted);
  }

// Virtual body layout is measured before it is rendered. Changing the viewport
// never leaves a blank first frame because the former offset exceeded its size.
void JPWNoCudaFiboUIBody(const string prefix,const JPWNoCudaFiboView &v)
  {
   if(v.tab==0)
     {
      JPWNoCudaFiboUIRow(prefix,"LINK","Vínculo",v.status);
      JPWNoCudaFiboUIRow(prefix,"SOURCE","Objeto / fonte",v.source_name+" · "+v.source_tf);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_REFERENCE_TF","Período de referência · "+v.source_tf);
      JPWNoCudaFiboUIRow(prefix,"REASON","Conferência",v.reason);
      if(v.preview)
        {
         string f[]; const int count=StringSplit(v.record_detail,'|',f);
         const string anchors[3]={"A · âncora exata","B · âncora exata","C · âncora exata"};
         for(int i=0;i<count;i++)
            JPWNoCudaFiboUIRow(prefix,"PREVIEW_ANCHOR_"+IntegerToString(i),
               i<3 ? anchors[i] : "Informação da prévia",f[i],true);
         JPWNoCudaFiboUIRow(prefix,"PREVIEW_FRAME","Período / captura",v.source_tf+" · sem ajuste ao Close; confira o canal original");
        }
      for(int i=0;i<ArraySize(v.sources);i++)
        { JPWNoCudaFiboUIBodyButton(prefix,"FC_SOURCE_"+IntegerToString(i),v.sources[i].title,v.sources[i].selected,v.sources[i].id);
          JPWNoCudaFiboUIRow(prefix,"SOURCE_INFO_"+IntegerToString(i),v.sources[i].state,v.sources[i].detail); }
      JPWNoCudaFiboUIBodyButton(prefix,v.preview ? "FC_CONFIRM_IMPORT" : "FC_IMPORT",v.preview ? "Confirmar vínculo conferido" : "Importar canal selecionado",true);
      if(v.preview) JPWNoCudaFiboUIBodyButton(prefix,"FC_IMPORT_CANCEL","Cancelar prévia · preservar vínculo anterior");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_REFRESH_SOURCE","Conferir fonte novamente");
      JPWNoCudaFiboUIBodyButton(prefix,v.source_hidden ? "FC_SOURCE_SHOW" : "FC_SOURCE_HIDE",v.source_hidden ? "Mostrar canal original" : "Ocultar canal original");
      JPWNoCudaFiboUIBodyButton(prefix,v.sync_paused ? "FC_SYNC_RESUME" : "FC_SYNC_PAUSE",v.sync_paused ? "Retomar sincronização" : "Pausar sincronização");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_UNLINK","Desvincular · preservar registros");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_MANUAL","Abrir desenho manual legado");
      JPWNoCudaFiboUIBodyEdit(prefix,"FC_JUST","Justificativa / contexto",v.justification);
     }
   else if(v.tab==1)
     {
      JPWNoCudaFiboUIRow(prefix,"QUOTE","Cotação / referência",v.quote_text,true);
      if(g_fc_layout.narrow || g_fc_visible_lines<8)
        { JPWNoCudaFiboUIRenderMetric(prefix,"BELOW","Linha abaixo",v.below);
          JPWNoCudaFiboUIRenderMetric(prefix,"ABOVE","Linha acima",v.above); }
      else
        {
         int y=0; const int card_rows=(g_fc_layout.button+g_fc_layout.line-1)/g_fc_layout.line+7;
         if(JPWNoCudaFiboUIRowVisible(card_rows,y))
           {
            const int x=g_fc_layout.x+g_fc_layout.pad,gap=JPWUIDesignPx(12),w=(g_fc_layout.inner-gap)/2;
            JPWNoCudaFiboUICard(prefix,"BELOW","Linha abaixo",v.below,x,y,w);
            JPWNoCudaFiboUICard(prefix,"ABOVE","Linha acima",v.above,x+w+gap,y,w);
           }
        }
      JPWNoCudaFiboUIRow(prefix,"NEAREST","Mais próxima",v.nearest.label+" · nível "+v.nearest.raw_level+" · "+(v.nearest.valid ? v.nearest.price : "N/A"));
      JPWNoCudaFiboUIBodyEdit(prefix,"FC_LEVEL_VALUE","Selecionar nível bruto · −4 a +4, passo 0,125",v.selected_value);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_LEVEL_APPLY","Selecionar linha pelo nível",true);
      JPWNoCudaFiboUIRenderMetric(prefix,"SELECTED","Linha selecionada",v.selected);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_TOUCH_NEW","Registrar observação manual");
      JPWNoCudaFiboUIRow(prefix,"GEOMETRY","Geometria / dados",v.reason);
     }
   else if(v.tab==2)
     {
      JPWNoCudaFiboUIRow(prefix,"PROJ_LINE","Linha selecionada",v.selected.label+" · nível "+v.selected.raw_level);
      JPWNoCudaFiboUIBodyEdit(prefix,"FC_DATE","Data · horário do servidor",v.projection_date);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_QUERY_DAY","Consultar dia",true);
      for(int i=0;i<5;i++) JPWNoCudaFiboUIRow(prefix,"PROJECT_"+IntegerToString(i),v.projection_labels[i],v.projection_values[i],true);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_SHOW_REFERENCES","Mostrar / ocultar referências no gráfico");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_SAVE_PROJECTION","Registrar consulta conferida");
      JPWNoCudaFiboUIRow(prefix,"PROVENANCE","Origem e limites",v.provenance);
     }
   else if(v.tab==3)
     {
      JPWNoCudaFiboUIRow(prefix,"RECORD_INFO","Consulta / registro",v.record_detail,true);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_STUDIES","Estudos deste instrumento");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_VERSIONS","Versões e observações do estudo");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_REFRESH","Atualizar registros");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_PREV","Página anterior · registros");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_NEXT","Próxima página · registros");
      for(int i=0;i<ArraySize(v.records);i++)
        { JPWNoCudaFiboUIBodyButton(prefix,"FC_RECORD_"+IntegerToString(i),v.records[i].title,v.records[i].selected,v.records[i].id);
          JPWNoCudaFiboUIRow(prefix,"RECORD_ROW_"+IntegerToString(i),v.records[i].state,v.records[i].detail); }
      JPWNoCudaFiboUIBodyButton(prefix,"FC_RESTORE_RECORD","Restaurar versão selecionada");
      JPWNoCudaFiboUIBodyEdit(prefix,"FC_OBS_TIME","Instante informado / observado",v.observation_time);
      JPWNoCudaFiboUIBodyEdit(prefix,"FC_OBS_NOTE","Observação manual",v.observation_note);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_TOUCH_SAVE","Salvar observação conferida",true);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_TOUCH_CANCEL","Cancelar observação");
     }
   else
     {
      JPWNoCudaFiboUIRow(prefix,"PREF_STATE","Prévia visual",g_fc_settings_dirty ? "Não aplicada" : "Aplicada / padrão");
      const string presets[3]={"Compacta","Ampla · 90%","Maximizada"};
      for(int i=0;i<3;i++) JPWNoCudaFiboUIBodyButton(prefix,"FC_PRESET_"+IntegerToString(i),presets[i],g_fc_draft.preset==i);
      JPWNoCudaFiboUIRow(prefix,"FONT","Fonte do painel",IntegerToString(g_fc_draft.font),true);
      JPWNoCudaFiboUIBodyButton(prefix,"FC_FONT_MINUS","Diminuir fonte");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_FONT_PLUS","Aumentar fonte");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_DENSITY",g_fc_draft.density==1 ? "Densidade compacta" : "Densidade normal");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_LAUNCHER","Canto do botão · "+IntegerToString(g_fc_draft.launcher+1));
      JPWNoCudaFiboUIBodyButton(prefix,"FC_MESH",g_fc_draft.mesh==1 ? "Malha completa" : "Essencial");
      JPWNoCudaFiboUIBodyButton(prefix,"FC_SETTINGS_DEFAULT","Restaurar padrão na prévia");
      JPWNoCudaFiboUIRow(prefix,"PREF_NOTICE","Preferência",g_fc_notice);
     }
  }

void JPWNoCudaFiboUIDraw(const string prefix,const JPWNoCudaFiboView &v)
  {
   if(!g_fc_initialized) JPWNoCudaFiboUILoadPrefs();
   ArrayResize(g_fc_keep,0); ArrayResize(g_fc_actions,0); ArrayResize(g_fc_action_ids,0);
   const bool dark=JPWNoCudaFiboUIDark();
   g_fc_ink=dark ? C'232,236,241' : C'37,43,52'; g_fc_muted=dark ? C'181,189,200' : C'85,96,111';
   g_fc_surface=dark ? C'25,29,36' : C'248,250,252'; g_fc_chrome=dark ? C'39,45,54' : C'233,238,244';
   g_fc_card=dark ? C'32,38,48' : C'255,255,255'; g_fc_border=dark ? C'99,112,131' : C'128,135,147';
   g_fc_accent=dark ? C'72,96,130' : C'48,70,102';
   JPWNoCudaFiboUICalculateLayout();
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(!v.open)
     {
      const string label="NoCuda · Gráficos";
      const int bw=JPWUIDesignButtonWidth(label,g_fc_draft.font,true),bh=g_fc_layout.button;
      const int corner=g_fc_draft.launcher,gap=JPWUIDesignPx(8);
      JPWNoCudaUIRememberHUD(cw,ch);
      JPWNoCudaUIRect place;
      const int desired_x=(corner==1 || corner==3 ? cw-bw-gap : gap);
      const int desired_y=(corner>=2 ? ch-bh-gap : JPWUIDesignPx(40));
      if(!JPWNoCudaUILauncherAt(cw,ch,bw,bh,desired_x,desired_y,place))
        {
         g_fc_notice="NoCuda · Gráficos: espaço livre insuficiente; amplie o gráfico. Rascunho preservado.";
         JPWNoCudaFiboUIFinish(prefix); return;
        }
      if(g_fc_notice=="NoCuda · Gráficos: espaço livre insuficiente; amplie o gráfico. Rascunho preservado.") g_fc_notice="";
      JPWNoCudaFiboUIButton(prefix,"FC_OPEN",place.x,place.y,bw,bh,"");
      const int icon=JPWUIDesignPx(16),inset=JPWUIDesignPx(12);
      const string icon_name=JPWNoCudaFiboUIName(prefix,"FC_OPEN_DESIGN_ICON");
      JPWNoCudaFiboUIKeep(icon_name);
      JPWUIDesignIcon(icon_name,place.x+inset,place.y+(bh-icon)/2,icon,g_fc_ink,true);
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"FC_OPEN_LABEL"),
         place.x+inset+icon+gap,place.y+(bh-g_fc_layout.line)/2,
         bw-2*inset-icon-gap,label,g_fc_draft.font,g_fc_ink,false);
      JPWNoCudaFiboUISetText(JPWNoCudaFiboUIName(prefix,"FC_OPEN"),OBJPROP_TOOLTIP,label);
      JPWNoCudaFiboUIFinish(prefix); return;
     }
   const int x=g_fc_layout.x,y=g_fc_layout.y,w=g_fc_layout.width,h=g_fc_layout.height;
   const int pad=g_fc_layout.pad,bh=g_fc_layout.button,line=g_fc_layout.line,inner=g_fc_layout.inner;
   JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,"BACKGROUND"),x,y,w,h,g_fc_surface,g_fc_border);
   if(inner<2*bh+JPWUIDesignPx(16) || h<2*bh+JPWUIDesignPx(24) ||
      g_fc_layout.body_y+2*line>g_fc_layout.footer_y ||
      JPWUIDesignButtonWidth("Aparência",g_fc_draft.font)>inner)
     {
      // Preserve an escape hatch even when the user shrinks the frame beyond
      // the minimum content area. This is not a successful usable dashboard.
      g_fc_layout.usable=false; g_fc_scroll_max=0;
      const int small=MathMax(1,MathMin(JPWUIDesignPx(32),MathMin(w-JPWUIDesignPx(8),h-JPWUIDesignPx(8))));
      JPWNoCudaFiboUIButton(prefix,"FC_HEADER_CLOSE",x+w-small-JPWUIDesignPx(4),y+JPWUIDesignPx(4),small,small,"×");
      if(h>=small+2*line+JPWUIDesignPx(12) && inner>0)
         JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"UNUSABLE"),x+pad,y+small+JPWUIDesignPx(8),inner,
            "Área insuficiente · maximize a janela",g_fc_draft.font,g_fc_muted);
      JPWNoCudaFiboUIFinish(prefix); return;
     }
   JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,"HEADER"),x+1,y+1,w-2,g_fc_layout.body_y-y-2,g_fc_chrome,g_fc_chrome);
   const int gap=JPWUIDesignPx(8),close_w=bh,title_w=MathMax(0,inner-2*close_w-gap);
   JPWNoCudaFiboUIButton(prefix,"FC_HEADER_CLOSE",x+w-pad-close_w,y+gap,close_w,bh,"×");
   JPWNoCudaFiboUIButton(prefix,"FC_HEADER_MINIMIZE",x+w-pad-2*close_w-gap,y+gap,close_w,bh,"−");
   JPWNoCudaFiboUIButton(prefix,"FC_DRAG",x+pad,y+gap,title_w,bh,"");
   const string brand_logo=JPWNoCudaFiboUIName(prefix,"LOGO");
   const string brand_title=JPWNoCudaFiboUIName(prefix,"TITLE");
   JPWNoCudaFiboUIKeep(brand_logo); JPWNoCudaFiboUIKeep(brand_title);
   JPWGenetrixHeader(brand_logo,brand_title,x+pad+gap,y+gap+JPWUIDesignPx(4),MathMax(0,title_w-2*gap),
      MathMax(0,bh-JPWUIDesignPx(8)),g_fc_draft.font,g_fc_ink,dark,"NoCuda · Gráficos · Fibonacci · "+v.symbol,1006);
   if(!g_fc_layout.narrow)
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"STATUS"),x+pad,y+bh+2*gap,inner,v.status+" · "+v.source_name,g_fc_draft.font,g_fc_muted);
   const int ty=g_fc_layout.body_y-g_fc_layout.nav_rows*(bh+gap)-gap;
   string tabs[5]={"Canal","Agora","Projeção","Registro","Aparência"};
   const int columns=g_fc_layout.nav_columns,tw=(inner-(columns-1)*gap)/columns;
   for(int i=0;i<5;i++) JPWNoCudaFiboUIButton(prefix,"FC_TAB_"+IntegerToString(i),
      x+pad+(i%columns)*(tw+gap),ty+(i/columns)*(bh+gap),tw,bh,tabs[i],v.tab==i);
   if(g_fc_tab!=v.tab) { g_fc_scroll=0; g_fc_tab=v.tab; }
   g_fc_line_cursor=0;
   if(!g_fc_layout.usable)
     {
      g_fc_notice="Área insuficiente para um campo; amplie a janela ou reduza a fonte. Dados preservados.";
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"UNUSABLE"),x+pad,g_fc_layout.body_y,inner,g_fc_notice,g_fc_draft.font,g_fc_ink);
     }
   else
     {
      g_fc_measure_pass=true; g_fc_line_cursor=0; JPWNoCudaFiboUIBody(prefix,v);
      g_fc_scroll_max=MathMax(0,g_fc_line_cursor-g_fc_visible_lines);
      g_fc_scroll=JPWNoCudaFiboUIClamp(g_fc_scroll,0,g_fc_scroll_max);
      g_fc_measure_pass=false; g_fc_line_cursor=0; JPWNoCudaFiboUIBody(prefix,v);
     }
   const int arrow_w=MathMin(JPWUIDesignPx(40),inner/7),action_w=(inner-2*arrow_w-3*gap)/2;
   JPWNoCudaFiboUIButton(prefix,"FC_SCROLL_UP",x+pad,g_fc_layout.footer_y,arrow_w,bh,"↑");
   JPWNoCudaFiboUIButton(prefix,"FC_SCROLL_DOWN",x+pad+arrow_w+gap,g_fc_layout.footer_y,arrow_w,bh,"↓");
   const int fx=x+pad+2*arrow_w+2*gap;
   JPWNoCudaFiboUIButton(prefix,v.tab==4 ? "FC_SETTINGS_APPLY" : "FC_CLOSE",fx,g_fc_layout.footer_y,action_w,bh,v.tab==4 ? "Aplicar" : "Fechar",v.tab==4);
   JPWNoCudaFiboUIButton(prefix,v.tab==4 ? "FC_SETTINGS_CANCEL" : "FC_MINIMIZE",fx+action_w+gap,g_fc_layout.footer_y,action_w,bh,v.tab==4 ? "Cancelar" : "Recolher");
   const int handle=JPWUIDesignPx(32);
   JPWNoCudaFiboUIButton(prefix,"FC_RESIZE",x+w-handle-gap,y+h-handle-gap,handle,handle,"↘");
   JPWNoCudaFiboUIFinish(prefix);
  }

#endif

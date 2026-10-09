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
string g_fc_keep[],g_fc_previous[],g_fc_actions[],g_fc_action_ids[];
bool g_fc_force_clear=false,g_fc_deferred_prune=false;
// Both widget retention and action registration must be complete before pruning.
bool g_fc_inventory_complete=true;
string g_fc_render_prefix="";
int g_fc_line_cursor=0,g_fc_visible_lines=0;
bool g_fc_measure_pass=false;
color g_fc_ink,g_fc_muted,g_fc_surface,g_fc_chrome,g_fc_card,g_fc_border,g_fc_accent;

void JPWNoCudaFiboUIFail()
  {
   g_fc_inventory_complete=false;
   const string reason="NoCuda: preparação visual incompleta; controles e rascunho preservados.";
   if(g_fc_notice!=reason) Print(reason);
   g_fc_notice=reason;
   const string status=g_fc_render_prefix+"FC_STATUS";
   if(ObjectFind(0,status)>=0) JPWUIDesignSetString(status,OBJPROP_TEXT,reason+" Use Fechar.");
   for(int i=0;i<ArraySize(g_fc_actions);i++)
     {
      const string action=g_fc_actions[i];
      if(action=="FC_CLOSE" || action=="FC_HEADER_CLOSE" || action=="FC_MINIMIZE" || action=="FC_HEADER_MINIMIZE") continue;
      const string name=g_fc_render_prefix+"FC_"+action;
      if(ObjectFind(0,name)>=0)
        { JPWUIDesignSetString(name,OBJPROP_TEXT,"Indisponível"); JPWUIDesignSetString(name,OBJPROP_TOOLTIP,reason); }
     }
  }
bool JPWNoCudaFiboUISetInteger(const string name,const ENUM_OBJECT_PROPERTY_INTEGER property,const long value)
  { if(!g_fc_inventory_complete) return(false); const bool ok=JPWUIDesignSetInteger(name,property,value); if(!ok) JPWNoCudaFiboUIFail(); return(ok); }
bool JPWNoCudaFiboUISetString(const string name,const ENUM_OBJECT_PROPERTY_STRING property,const string value)
  { if(!g_fc_inventory_complete) return(false); const bool ok=JPWUIDesignSetString(name,property,value); if(!ok) JPWNoCudaFiboUIFail(); return(ok); }

int JPWNoCudaFiboUIClamp(const int v,const int a,const int b)
  { return(MathMax(a,MathMin(v,b))); }
int JPWNoCudaFiboUITextWidth(const string value,const int font)
  {
   return(JPWUIDesignTextWidth(value,font));
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
  {
   if(!g_fc_inventory_complete) return;
   const int n=ArraySize(g_fc_keep);
   if(ArrayResize(g_fc_keep,n+1)!=n+1)
     {
      JPWNoCudaFiboUIFail();
      return;
     }
   g_fc_keep[n]=name;
  }
bool JPWNoCudaFiboUIEnsure(const string name,const ENUM_OBJECT type)
  {
   JPWNoCudaFiboUIKeep(name);
   if(!g_fc_inventory_complete) return(false);
   if(ObjectFind(0,name)>=0 && ObjectGetInteger(0,name,OBJPROP_TYPE)!=type)
      JPWUIDesignDelete(name);
   const bool ready=JPWUIDesignEnsure(name,type);
   if(!ready) JPWNoCudaFiboUIFail();
   return(ready);
  }
void JPWNoCudaFiboUISetText(const string name,const ENUM_OBJECT_PROPERTY_STRING prop,const string value)
  { if(prop==OBJPROP_TEXT && ObjectGetInteger(0,name,OBJPROP_TYPE)==OBJ_EDIT &&
       ObjectGetString(0,name,prop)==value) return;
    JPWNoCudaFiboUISetString(name,prop,value); }
void JPWNoCudaFiboUIPosition(const string name,const int x,const int y,const int w,const int h,const int z)
  {
   JPWNoCudaFiboUISetInteger(name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_XDISTANCE,x); JPWNoCudaFiboUISetInteger(name,OBJPROP_YDISTANCE,y);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_XSIZE,w); JPWNoCudaFiboUISetInteger(name,OBJPROP_YSIZE,h);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_HIDDEN,true); JPWNoCudaFiboUISetInteger(name,OBJPROP_ZORDER,z);
  }
void JPWNoCudaFiboUIBox(const string name,const int x,const int y,const int w,const int h,
                       const color fill,const color border)
  {
   if(w<=0 || h<=0 || !JPWNoCudaFiboUIEnsure(name,OBJ_RECTANGLE_LABEL)) return;
   JPWNoCudaFiboUIPosition(name,x,y,w,h,990);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_BGCOLOR,fill); JPWNoCudaFiboUISetInteger(name,OBJPROP_COLOR,border);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_SELECTABLE,false);
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
   JPWNoCudaFiboUISetInteger(name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_FONTSIZE,font); JPWNoCudaFiboUISetInteger(name,OBJPROP_COLOR,ink);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_SELECTABLE,false);
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
   JPWNoCudaFiboUISetInteger(name,OBJPROP_FONTSIZE,g_fc_draft.font);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_COLOR,g_fc_ink); JPWNoCudaFiboUISetInteger(name,OBJPROP_BGCOLOR,g_fc_card);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_BORDER_COLOR,name==g_fc_focus ?
      JPWUIDesignFocusInk((color)ChartGetInteger(0,CHART_COLOR_BACKGROUND)) : g_fc_border);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_READONLY,readonly);
   JPWNoCudaFiboUISetText(name,OBJPROP_FONT,"Arial");
   // Read-only values belong to the current producer capture, not to a user
   // draft. Native selection may remain focused while the value becomes N/A.
   if(readonly || !exists || name!=g_fc_editing) JPWNoCudaFiboUISetText(name,OBJPROP_TEXT,value);
   JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,value);
  }
int JPWNoCudaFiboUIValueRows()
  {
   const int line=MathMax(1,g_fc_layout.line);
   return((JPWUIDesignControlHeight(line)+line-1)/line);
  }
int JPWNoCudaFiboUICardRows()
  {
   const int line=MathMax(1,g_fc_layout.line);
   return((g_fc_layout.button+line-1)/line+3+4*JPWNoCudaFiboUIValueRows());
  }
void JPWNoCudaFiboUIValue(const string name,const int x,const int y,const int w,const string value)
  {
   // Preserve the whole numeric string. A narrow read-only field supports
   // native horizontal selection, whose interaction remains a native gate.
   if(name==g_fc_editing || JPWNoCudaFiboUITextWidth(value,g_fc_draft.font)>w)
      JPWNoCudaFiboUIEdit(name,x,y,w,JPWUIDesignControlHeight(g_fc_layout.line),value,true);
   else JPWNoCudaFiboUILabel(name,x,y,w,value,g_fc_draft.font,g_fc_ink,false);
  }
void JPWNoCudaFiboUIButton(const string prefix,const string action,const int x,const int y,
                          const int w,const int h,const string text,const bool primary=false,
                          const string item_id="")
  {
   const string name=JPWNoCudaFiboUIName(prefix,action);
   if(w<=0 || h<=0 || !g_fc_inventory_complete) return;
   // Reserve the complete action pair before creating a seemingly ready control.
   const int n=ArraySize(g_fc_actions);
   if(ArrayResize(g_fc_actions,n+1)!=n+1 || ArrayResize(g_fc_action_ids,n+1)!=n+1)
     {
      ArrayResize(g_fc_actions,n); ArrayResize(g_fc_action_ids,n);
      JPWNoCudaFiboUIFail();
      return;
     }
   if(!JPWNoCudaFiboUIEnsure(name,OBJ_BUTTON))
     {
      ArrayResize(g_fc_actions,n); ArrayResize(g_fc_action_ids,n);
      return;
     }
   g_fc_actions[n]=action; g_fc_action_ids[n]=item_id;
   const color background=(color)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   if(name==g_fc_focus)
      JPWNoCudaFiboUIBox(name+"_FOCUS_FRAME",x-JPWUIDesignPx(2),y-JPWUIDesignPx(2),
         w+JPWUIDesignPx(4),h+JPWUIDesignPx(4),JPWUIDesignFocusInk(background),JPWUIDesignFocusInk(background));
   JPWNoCudaFiboUIPosition(name,x,y,w,h,1005);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_FONTSIZE,g_fc_draft.font);
   const bool selected_tab=primary && StringFind(action,"FC_TAB_")==0;
   const bool primary_action=primary && !selected_tab;
   JPWNoCudaFiboUISetInteger(name,OBJPROP_COLOR,primary_action ? C'255,255,255' : g_fc_ink);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_BGCOLOR,selected_tab ? JPWUIDesignSelectedFill(background) :
      primary_action ? g_fc_accent : g_fc_chrome);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_BORDER_COLOR,name==g_fc_focus ?
      (primary_action ? JPWUIDesignPrimaryInk(background) : JPWUIDesignFocusInk(background)) : g_fc_border);
   if(ObjectGetInteger(0,name,OBJPROP_STATE)!=0) JPWNoCudaFiboUISetInteger(name,OBJPROP_STATE,false);
   JPWNoCudaFiboUISetText(name,OBJPROP_FONT,"Arial");
   JPWNoCudaFiboUISetText(name,OBJPROP_TEXT,JPWNoCudaFiboUIFit(text,w-JPWUIDesignPx(24),g_fc_draft.font));
   JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,text);
  }
void JPWNoCudaFiboUIFinish(const string prefix)
  {
   // Preserve every existing widget/caret when preparation did not complete.
   if(!g_fc_inventory_complete) return;
   const int count=ArraySize(g_fc_keep);
   bool same=!g_fc_force_clear && !g_fc_deferred_prune && count==ArraySize(g_fc_previous);
   for(int k=0;same && k<count;k++) same=g_fc_keep[k]==g_fc_previous[k];
   if(same) return;
   if(ArrayResize(g_fc_previous,count)!=count)
     { JPWNoCudaFiboUIFail(); return; }
   for(int k=0;k<count;k++) g_fc_previous[k]=g_fc_keep[k];
   g_fc_deferred_prune=false;
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,prefix+"FC_")!=0) continue;
      bool listed=false;
      for(int k=0;k<ArraySize(g_fc_keep);k++) if(g_fc_keep[k]==name) { listed=true; break; }
      const bool active=!g_fc_force_clear && name==g_fc_editing;
      bool keep=listed || active;
      if(active && !listed) g_fc_deferred_prune=true;
      if(!keep)
        { bool removed=false;
          if(StringFind(name,"_DESIGN_ICON")>=0)
            { JPWUIDesignDeleteIcon(name); removed=(ObjectFind(0,name)<0); }
          else removed=JPWUIDesignDelete(name) && ObjectFind(0,name)<0;
          if(!removed)
            {
             // A cached desired inventory must not hide a refused deletion.
             g_fc_deferred_prune=true; JPWNoCudaFiboUIFail(); return;
            } if(g_fc_focus==name) g_fc_focus="";
          if(g_fc_editing==name) g_fc_editing=""; }
     }
  }
void JPWNoCudaFiboUIClear(const string prefix)
  {
   g_fc_render_prefix=prefix;
   ArrayResize(g_fc_keep,0); g_fc_inventory_complete=true; g_fc_force_clear=true;
   JPWNoCudaFiboUIFinish(prefix); g_fc_force_clear=false;
   if(!g_fc_inventory_complete)
     { g_fc_deferred_prune=true; return; }
   ArrayResize(g_fc_previous,0); ArrayResize(g_fc_actions,0); ArrayResize(g_fc_action_ids,0);
   g_fc_deferred_prune=false; g_fc_focus=""; g_fc_editing="";
   g_fc_gesture=false; g_fc_mouse_down=false;
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
   JPWNoCudaFiboUISetInteger(name,OBJPROP_XDISTANCE,-10000); JPWNoCudaFiboUISetInteger(name,OBJPROP_YDISTANCE,-10000);
   JPWNoCudaFiboUISetInteger(name,OBJPROP_HIDDEN,true); JPWNoCudaFiboUISetInteger(name,OBJPROP_SELECTABLE,false);
   if(!JPWNoCudaFiboUISetString(name,OBJPROP_TOOLTIP,text) || ObjectGetString(0,name,OBJPROP_TOOLTIP)!=text)
     { g_fc_notice="Preferência visual não confirmada."; return(false); }
   g_fc_pref_invalid=false; return(true);
  }
int JPWNoCudaFiboUIFooterRows(const int inner,const int font)
  {
   const int gap=JPWUIDesignPx(8);
   const int arrow=MathMax(JPWUIDesignPx(32),JPWUIDesignButtonWidth("↓",font));
   const int action=MathMax(JPWUIDesignButtonWidth("Recolher",font),JPWUIDesignButtonWidth("Cancelar",font));
   if(inner>=2*arrow+2*action+3*gap) return(1);
   if(inner>=2*action+gap) return(2);
   return(3);
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
   const int footer_rows=JPWNoCudaFiboUIFooterRows(g_fc_layout.inner,g_fc_draft.font);
   const int footer_height=footer_rows*(g_fc_layout.button+JPWUIDesignPx(8))-JPWUIDesignPx(8);
   g_fc_layout.footer_y=g_fc_layout.y+g_fc_layout.height-footer_height-g_fc_layout.pad-JPWUIDesignPx(40);
   g_fc_layout.body_height=MathMax(0,g_fc_layout.footer_y-g_fc_layout.body_y-gap);
   g_fc_layout.usable=g_fc_layout.inner>=JPWUIDesignPx(140) &&
      JPWUIDesignButtonWidth("Aparência",g_fc_draft.font)<=g_fc_layout.inner &&
      g_fc_layout.body_height>=MathMax(2*g_fc_layout.line,JPWUIDesignControlHeight(g_fc_layout.line));
   g_fc_visible_lines=MathMax(1,g_fc_layout.body_height/g_fc_layout.line);
  }
string JPWNoCudaFiboUIHitAction(const string prefix,const string object)
  {
   if(StringFind(object,prefix+"FC_FC_")!=0) return("");
   const string action=StringSubstr(object,StringLen(prefix+"FC_"));
   if(!g_fc_inventory_complete)
     {
      // Existing textual exit controls remain usable after a failed frame;
      // no study or preference action is authorized by a partial catalog.
      if(ObjectFind(0,object)<0 || ObjectGetInteger(0,object,OBJPROP_TYPE)!=OBJ_BUTTON) return("");
      if(action=="FC_CLOSE" || action=="FC_HEADER_CLOSE") return("FC_CLOSE");
      if(action=="FC_MINIMIZE" || action=="FC_HEADER_MINIMIZE") return("FC_MINIMIZE");
      return("");
     }
   bool registered=false;
   const int count=MathMin(ArraySize(g_fc_actions),ArraySize(g_fc_action_ids));
   for(int i=0;i<count;i++) if(g_fc_actions[i]==action) { registered=true; break; }
   if(!registered) return("");
   if(action=="FC_HEADER_CLOSE") return("FC_CLOSE");
   if(action=="FC_HEADER_MINIMIZE") return("FC_MINIMIZE");
   return(action);
  }
string JPWNoCudaFiboUIActionID(const string action)
  { for(int i=0;i<MathMin(ArraySize(g_fc_actions),ArraySize(g_fc_action_ids));i++)
       if(g_fc_actions[i]==action) return(g_fc_action_ids[i]); return(""); }
string JPWNoCudaFiboUIFocusCycle(const string current,const bool reverse)
  {
   if(!g_fc_inventory_complete)
      return(ObjectFind(0,g_fc_render_prefix+"FC_FC_CLOSE")>=0 ? g_fc_render_prefix+"FC_FC_CLOSE" :
         g_fc_render_prefix+"FC_FC_HEADER_CLOSE");
   const int count=ArraySize(g_fc_keep); int at=(reverse ? 0 : -1);
   for(int i=0;i<count;i++) if(g_fc_keep[i]==current) { at=i; break; }
   for(int i=1;i<=count;i++)
     {
      const string name=g_fc_keep[(at+(reverse ? -i : i)+2*count)%count];
      const long kind=ObjectGetInteger(0,name,OBJPROP_TYPE);
      if(ObjectFind(0,name)>=0 && (kind==OBJ_BUTTON ||
         kind==OBJ_EDIT)) return(name);
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
void JPWNoCudaFiboUIEndInteraction()
  {
   // The controller captures fields first. A closed editor must not retain an
   // editable object or complete an unfinished geometry gesture over another
   // module; the in-memory draft and unapplied preferences stay unchanged.
   if(g_fc_editing!="" && ObjectFind(0,g_fc_editing)>=0)
      ObjectSetInteger(0,g_fc_editing,OBJPROP_SELECTED,false);
   g_fc_editing=""; g_fc_focus="";
   g_fc_gesture=false; g_fc_mouse_down=false;
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
   int y=0;
   // Reserve the essential copy/select target even when this value currently
   // fits as a label; transitions cannot overlap the next row or jump its budget.
   const int value_rows=(numeric ? JPWNoCudaFiboUIValueRows() : 1);
   if(g_fc_layout.narrow && numeric)
     {
      // A viewport may fit the target alone but not caption+target together.
      // Reserve both parts independently, preserving their total scroll budget.
      int caption_y=0;
      if(JPWNoCudaFiboUIRowVisible(1,caption_y))
         JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_LABEL"),
            g_fc_layout.x+g_fc_layout.pad,caption_y,g_fc_layout.inner,label,g_fc_draft.font,g_fc_muted);
      int value_y=0;
      if(JPWNoCudaFiboUIRowVisible(value_rows,value_y))
        {
         const string name=JPWNoCudaFiboUIName(prefix,id+"_VALUE");
         JPWNoCudaFiboUIValue(name,g_fc_layout.x+g_fc_layout.pad,value_y,g_fc_layout.inner,value);
         JPWNoCudaFiboUISetText(name,OBJPROP_TOOLTIP,label+": "+value);
        }
      return;
     }
   const int lines=(g_fc_layout.narrow ? 1+value_rows : value_rows);
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
   const int value_rows=JPWNoCudaFiboUIValueRows();
   JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,id+"_CARD"),x,y,width,JPWNoCudaFiboUICardRows()*line,
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
         x+pad,content_y+(1+value_rows*(i+1))*line,split-pad,captions[i],font,g_fc_muted);
      JPWNoCudaFiboUIValue(JPWNoCudaFiboUIName(prefix,id+"_VAL_"+IntegerToString(i)),
         x+split,content_y+(1+value_rows*(i+1))*line,width-split-pad,m.valid ? values[i] : "N/A");
     }
   JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_STATE"),x+pad,content_y+(1+4*value_rows)*line,width-2*pad,m.state,font,g_fc_muted);
   JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,id+"_REASON"),x+pad,content_y+(2+4*value_rows)*line,width-2*pad,m.reason,font,g_fc_muted);
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
      if(g_fc_layout.narrow || g_fc_visible_lines<JPWNoCudaFiboUICardRows())
        { JPWNoCudaFiboUIRenderMetric(prefix,"BELOW","Linha abaixo",v.below);
          JPWNoCudaFiboUIRenderMetric(prefix,"ABOVE","Linha acima",v.above); }
      else
        {
         int y=0; const int card_rows=JPWNoCudaFiboUICardRows();
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
   JPWUIDesignBeginPass();
   g_fc_render_prefix=prefix;
   if(!g_fc_initialized) JPWNoCudaFiboUILoadPrefs();
   ArrayResize(g_fc_keep,0); ArrayResize(g_fc_actions,0); ArrayResize(g_fc_action_ids,0);
   g_fc_inventory_complete=true;
   if(g_fc_notice=="NoCuda: preparação visual incompleta; controles e rascunho preservados.") g_fc_notice="";
   const bool dark=JPWNoCudaFiboUIDark();
   g_fc_ink=dark ? C'232,236,241' : C'37,43,52'; g_fc_muted=dark ? C'181,189,200' : C'85,96,111';
   g_fc_surface=dark ? C'25,29,36' : C'248,250,252'; g_fc_chrome=dark ? C'39,45,54' : C'233,238,244';
   g_fc_card=dark ? C'32,38,48' : C'255,255,255'; g_fc_border=dark ? C'120,133,149' : C'112,123,138';
   g_fc_accent=JPWUIDesignPrimaryFill((color)ChartGetInteger(0,CHART_COLOR_BACKGROUND));
   JPWNoCudaFiboUICalculateLayout();
   if(g_fc_layout.usable && g_fc_notice=="NoCuda · área física insuficiente. Use Esc para fechar e amplie o gráfico.") g_fc_notice="";
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   if(!v.open)
     {
      const string full_label="NoCuda · Gráficos";
      string label=full_label;
      bool use_icon=true;
      int bw=JPWUIDesignButtonWidth(label,g_fc_draft.font,true);
      const int bh=g_fc_layout.button;
      const int corner=g_fc_draft.launcher,gap=JPWUIDesignPx(8);
      JPWNoCudaUIRememberHUD(cw,ch);
      JPWNoCudaUIRect place;
      const int desired_x=(corner==1 || corner==3 ? cw-bw-gap : gap);
      const int desired_y=(corner>=2 ? ch-bh-gap : JPWUIDesignPx(40));
      bool placed=JPWNoCudaUILauncherAt(cw,ch,bw,bh,desired_x,desired_y,place);
      for(int compact=1;!placed && compact<=2;compact++)
        {
         use_icon=false; label=(compact==1 ? full_label : "NoCuda");
         bw=JPWUIDesignButtonWidth(label,g_fc_draft.font,false);
         const int compact_x=(corner==1 || corner==3 ? cw-bw-gap : gap);
         placed=JPWNoCudaUILauncherAt(cw,ch,bw,bh,compact_x,desired_y,place);
        }
      if(!placed)
        {
         g_fc_notice="NoCuda · Gráficos: espaço livre insuficiente; amplie o gráfico. Rascunho preservado.";
         Print(g_fc_notice);
         JPWNoCudaFiboUIFinish(prefix); JPWUIDesignEndPass(); return;
        }
      if(g_fc_notice=="NoCuda · Gráficos: espaço livre insuficiente; amplie o gráfico. Rascunho preservado.") g_fc_notice="";
      JPWNoCudaFiboUIButton(prefix,"FC_OPEN",place.x,place.y,bw,bh,"");
      const int icon=JPWUIDesignPx(20),inset=JPWUIDesignPx(12);
      const string icon_name=JPWNoCudaFiboUIName(prefix,"FC_OPEN_DESIGN_ICON");
      if(use_icon) JPWNoCudaFiboUIKeep(icon_name);
      const bool decoration_attempted=use_icon && g_fc_inventory_complete;
      const bool decorated=decoration_attempted &&
         JPWUIDesignIcon(icon_name,place.x+inset,place.y+(bh-icon)/2,icon,g_fc_ink,true);
      if(decoration_attempted && !decorated)
        {
         JPWUIDesignDeleteIcon(icon_name);
         if(ObjectFind(0,icon_name)>=0)
           {
            g_fc_deferred_prune=true;
            JPWNoCudaFiboUIFail();
            JPWNoCudaFiboUIFinish(prefix); JPWUIDesignEndPass(); return;
           }
        }
      JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"FC_OPEN_LABEL"),
         place.x+inset+(decorated ? icon+gap : 0),place.y+(bh-g_fc_layout.line)/2,
         bw-2*inset-(decorated ? icon+gap : 0),label,g_fc_draft.font,g_fc_ink,false);
      JPWNoCudaFiboUISetText(JPWNoCudaFiboUIName(prefix,"FC_OPEN"),OBJPROP_TOOLTIP,full_label);
      JPWNoCudaFiboUIFinish(prefix); JPWUIDesignEndPass(); return;
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
       // The escape strip is bounded by the physical chart, independently of
       // an undersized saved frame. Compact typography is temporary and never
       // changes the user's font preference or the financial content.
       int safety_font=g_fc_draft.font,safety_gap=JPWUIDesignPx(8);
       int title_w=0,exit_w=0,exit_h=0,title_h=0,strip_w=0,strip_h=0;
       bool safety_ready=false,safety_vertical=false;
       string safety_title="NoCuda · Gráficos",exit_label="Fechar";
       // Prefer a compact horizontal escape row before using the full height
       // for a vertical stack, retaining room for the explicit limitation cue.
       for(int arrangement=0;arrangement<2 && !safety_ready;arrangement++)
          for(int font=g_fc_draft.font;font>=9 && !safety_ready;font--)
         {
          const int base_gap=JPWUIDesignPx(font==g_fc_draft.font ? 8 : 4);
          const int th=JPWNoCudaFiboUILine(font),eh=JPWUIDesignControlHeight(th);
          for(int variant=0;variant<3 && !safety_ready;variant++)
            {
             const int gap=(variant==2 ? JPWUIDesignPx(4) : base_gap);
             const string title=(variant==0 ? "NoCuda · Gráficos" : "NoCuda");
             const string label=(variant<2 ? "Fechar" : "×");
             const int tw=JPWNoCudaFiboUITextWidth(title,font);
             const int ew=MathMax(eh,JPWUIDesignButtonWidth(label,font));
             const int horizontal_w=tw+ew+3*gap,horizontal_h=MathMax(th,eh)+2*gap;
             const int vertical_w=MathMax(tw,ew)+2*gap,vertical_h=th+eh+3*gap;
             const bool horizontal=horizontal_w<=cw && horizontal_h<=ch;
             const bool vertical=vertical_w<=cw && vertical_h<=ch;
             if((arrangement==0 && !horizontal) || (arrangement==1 && !vertical)) continue;
             safety_ready=true; safety_vertical=(arrangement==1);
             safety_font=font; safety_gap=gap; safety_title=title; exit_label=label;
             title_w=tw; title_h=th; exit_w=ew; exit_h=eh;
             strip_w=(arrangement==0 ? horizontal_w : vertical_w);
             strip_h=(arrangement==0 ? horizontal_h : vertical_h);
            }
         }
       if(safety_ready)
         {
          if(g_fc_notice=="NoCuda · área física insuficiente. Use Esc para fechar e amplie o gráfico.") g_fc_notice="";
          const int strip_x=JPWNoCudaFiboUIClamp(x,0,MathMax(0,cw-strip_w));
          const int strip_y=JPWNoCudaFiboUIClamp(y,0,MathMax(0,ch-strip_h));
          const int title_x=strip_x+safety_gap;
          const int title_y=strip_y+safety_gap+(safety_vertical ? 0 : (exit_h-title_h)/2);
          const int exit_x=strip_x+safety_gap+(safety_vertical ? 0 : title_w+safety_gap);
          const int exit_y=strip_y+safety_gap+(safety_vertical ? title_h+safety_gap : 0);
          JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,"SAFETY_BG"),strip_x,strip_y,
             strip_w,strip_h,g_fc_surface,g_fc_border);
          JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"TITLE"),title_x,title_y,title_w,
             safety_title,safety_font,g_fc_ink,false);
          JPWNoCudaFiboUIButton(prefix,"FC_CLOSE",exit_x,exit_y,exit_w,exit_h,"");
          const string close_name=JPWNoCudaFiboUIName(prefix,"FC_CLOSE");
          JPWNoCudaFiboUISetInteger(close_name,OBJPROP_FONTSIZE,safety_font);
          JPWNoCudaFiboUISetText(close_name,OBJPROP_TEXT,exit_label);
          JPWNoCudaFiboUISetText(close_name,OBJPROP_TOOLTIP,"Fechar NoCuda · Gráficos · área insuficiente; amplie o gráfico");
          // Reserve a real, legible limitation cue. If a full sentence does
          // not fit below/above, a compact cue shares the title column; its
          // tooltip retains the complete cause and next action.
          string hints[3]={"Área insuficiente · amplie o gráfico","Área insuficiente","Amplie"};
          bool hint_ready=false;
          int hint_x=0,hint_y=0,hint_w=0,hint_h=0,hint_font=safety_font;
          string hint="";
          for(int variant=0;variant<3 && !hint_ready;variant++)
             for(int font=safety_font;font>=9 && !hint_ready;font--)
               {
                const int hw=JPWNoCudaFiboUITextWidth(hints[variant],font);
                const int hh=JPWNoCudaFiboUILine(font);
                if(hw>cw) continue;
                if(strip_y+strip_h+hh<=ch)
                  {
                   hint_ready=true; hint_x=JPWNoCudaFiboUIClamp(strip_x,0,MathMax(0,cw-hw));
                   hint_y=strip_y+strip_h; hint_w=hw; hint_h=hh;
                  }
                else if(strip_y>=hh)
                  {
                   hint_ready=true; hint_x=JPWNoCudaFiboUIClamp(strip_x,0,MathMax(0,cw-hw));
                   hint_y=strip_y-hh; hint_w=hw; hint_h=hh;
                  }
                else if(!safety_vertical && hw<=title_w)
                  {
                   // Labels are not input targets. Their actual text height,
                   // plus the common gap, can share the taller close row.
                   const int title_text_h=MathMax(1,JPWNoCudaFiboUILine(safety_font)-JPWUIDesignPx(8));
                   const int hint_text_h=MathMax(1,hh-JPWUIDesignPx(8));
                   const int group_h=title_text_h+safety_gap+hint_text_h;
                   if(group_h>exit_h) continue;
                   const int caption_y=strip_y+safety_gap+(exit_h-group_h)/2;
                   const string title_name=JPWNoCudaFiboUIName(prefix,"TITLE");
                   JPWNoCudaFiboUISetInteger(title_name,OBJPROP_YDISTANCE,caption_y);
                   JPWNoCudaFiboUISetInteger(title_name,OBJPROP_YSIZE,title_text_h);
                   hint_ready=true; hint_x=title_x; hint_y=caption_y+title_text_h+safety_gap;
                   hint_w=title_w; hint_h=hint_text_h;
                  }
                if(hint_ready) { hint=hints[variant]; hint_font=font; }
               }
          if(hint_ready)
            {
             const string hint_name=JPWNoCudaFiboUIName(prefix,"UNUSABLE");
             JPWNoCudaFiboUILabel(hint_name,hint_x,hint_y,hint_w,hint,hint_font,g_fc_muted,false);
             JPWNoCudaFiboUISetInteger(hint_name,OBJPROP_YSIZE,hint_h);
             JPWNoCudaFiboUISetText(hint_name,OBJPROP_TOOLTIP,"Área insuficiente · amplie o gráfico; Esc ou Fechar encerra a janela NoCuda · Gráficos");
            }
          else
            {
             const string reason="NoCuda · área física insuficiente. Use Esc para fechar e amplie o gráfico.";
             if(g_fc_notice!=reason) Print(reason);
             g_fc_notice=reason;
            }

         }
       else
         {
          const string reason="NoCuda · área física insuficiente. Use Esc para fechar e amplie o gráfico.";
          if(g_fc_notice!=reason) Print(reason);
          g_fc_notice=reason;
          // Never register a close target that lies outside the physical chart.
          // Esc remains available through the existing keyboard route.
          const int compact_font=9,compact_h=JPWNoCudaFiboUILine(compact_font);
          const string compact_hint="Esc · amplie o gráfico";
          if(JPWNoCudaFiboUITextWidth(compact_hint,compact_font)<=cw && compact_h<=ch)
             JPWNoCudaFiboUILabel(JPWNoCudaFiboUIName(prefix,"UNUSABLE"),0,0,cw,
                compact_hint,compact_font,g_fc_ink,false);
         }
      JPWNoCudaFiboUIFinish(prefix); JPWUIDesignEndPass(); return;
     }
   JPWNoCudaFiboUIBox(JPWNoCudaFiboUIName(prefix,"HEADER"),x+1,y+1,w-2,g_fc_layout.body_y-y-2,g_fc_chrome,g_fc_chrome);
   const int gap=JPWUIDesignPx(8),close_w=bh,title_w=MathMax(0,inner-2*close_w-gap);
   JPWNoCudaFiboUIButton(prefix,"FC_HEADER_CLOSE",x+w-pad-close_w,y+gap,close_w,bh,"×");
   JPWNoCudaFiboUIButton(prefix,"FC_HEADER_MINIMIZE",x+w-pad-2*close_w-gap,y+gap,close_w,bh,"−");
   JPWNoCudaFiboUIButton(prefix,"FC_DRAG",x+pad,y+gap,title_w,bh,"");
   const string brand_logo=JPWNoCudaFiboUIName(prefix,"LOGO");
   const string brand_title=JPWNoCudaFiboUIName(prefix,"TITLE");
   JPWNoCudaFiboUIKeep(brand_logo); JPWNoCudaFiboUIKeep(brand_title);
   // Compact title typography is a presentation fallback, never a preference
   // update. Keep the functional module visible before optional branding.
   const int header_width=MathMax(0,title_w-2*gap);
   int header_font=g_fc_draft.font;
   while(header_font>9 && JPWNoCudaFiboUITextWidth("NoCuda · Gráficos",header_font)>header_width)
      header_font--;
   if(g_fc_inventory_complete)
      JPWGenetrixHeader(brand_logo,brand_title,x+pad+gap,y+gap+JPWUIDesignPx(4),header_width,
         MathMax(0,bh-JPWUIDesignPx(8)),header_font,g_fc_ink,dark,"NoCuda · Gráficos · Fibonacci · "+v.symbol,1006);
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
   const int footer_rows=JPWNoCudaFiboUIFooterRows(inner,g_fc_draft.font);
   const int arrow_w=MathMax(JPWUIDesignPx(32),JPWUIDesignButtonWidth("↓",g_fc_draft.font));
   JPWNoCudaFiboUIButton(prefix,"FC_SCROLL_UP",x+pad,g_fc_layout.footer_y,arrow_w,bh,"↑");
   JPWNoCudaFiboUIButton(prefix,"FC_SCROLL_DOWN",x+pad+arrow_w+gap,g_fc_layout.footer_y,arrow_w,bh,"↓");
   const int fx=(footer_rows==1 ? x+pad+2*arrow_w+2*gap : x+pad);
   const int ay=g_fc_layout.footer_y+(footer_rows==1 ? 0 : bh+gap);
   const int action_w=(footer_rows==1 ? (inner-2*arrow_w-3*gap)/2 : footer_rows==2 ? (inner-gap)/2 : inner);
   JPWNoCudaFiboUIButton(prefix,v.tab==4 ? "FC_SETTINGS_APPLY" : "FC_CLOSE",fx,ay,action_w,bh,v.tab==4 ? "Aplicar" : "Fechar",v.tab==4);
   JPWNoCudaFiboUIButton(prefix,v.tab==4 ? "FC_SETTINGS_CANCEL" : "FC_MINIMIZE",
      footer_rows==3 ? fx : fx+action_w+gap,ay+(footer_rows==3 ? bh+gap : 0),action_w,bh,v.tab==4 ? "Cancelar" : "Recolher");
   const int handle=JPWUIDesignPx(32);
   JPWNoCudaFiboUIButton(prefix,"FC_RESIZE",x+w-handle-gap,y+h-handle-gap,handle,handle,"↘");
   JPWNoCudaFiboUIFinish(prefix); JPWUIDesignEndPass();
  }

#endif

#ifndef JPW_NOCUDA_UI_MQH
#define JPW_NOCUDA_UI_MQH
#include <JPWealth/JPW_Genetrix_Brand.mqh>
#include <JPWealth/JPW_UI_Design.mqh>

// Presentation only. No candle reads, study DB access or revision writes.
struct JPWNoCudaUIView
  {
   bool open;
   bool draft;
   bool channel_visible;
   bool full_mesh;
   bool geometry_valid;
   bool history_diverged;
   bool anchor_a;
   bool anchor_b;
   bool anchor_c;
   int tab;
   int page;
   int pick;
   int measure_page;
   int level_index;
   int revision;
   int head_revision;
   int study_index;
   int study_count;
   string symbol;
   string source_tf;
   string status;
   string a_text;
   string b_text;
   string c_text;
   string width_text;
   string width_price;
   string subdivision_price;
   string level_text;
   string level_input;
   string distance_text;
   string quote_text;
   string history_text;
   string study_id;
   string justification;
   string date;
   bool daily_valid;
   bool references;
   string daily_state;
   string daily_start;
   string daily_mid;
   string daily_end;
   string daily_mean;
   string daily_range;
   string daily_source;
   string daily_reason;
  };

string g_nocuda_ui_kept[];
string g_nocuda_ui_editing="",g_nocuda_ui_focus="";
int g_nocuda_ui_page=0,g_nocuda_ui_pages=1;

int JPWNoCudaUIMin(const int a,const int b) { return(a<b ? a : b); }
int JPWNoCudaUIMax(const int a,const int b) { return(a>b ? a : b); }
int JPWNoCudaUIWidth()
  { return(MathMin(JPWUIDesignPx(960),(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS)-JPWUIDesignPx(24))); }
int JPWNoCudaUIHeight()
  { return(MathMin(JPWUIDesignPx(700),(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS)-JPWUIDesignPx(24))); }
int JPWNoCudaUILineHeight()
  {
   uint width=0,height=0;
   if(TextSetFont("Arial",-110) && TextGetSize("Ag",width,height) && height>0)
      return(MathMax(JPWUIDesignPx(20),(int)height+JPWUIDesignPx(8)));
   return(JPWUIDesignPx(24));
  }
int JPWNoCudaUIButtonHeight()
  { return(JPWUIDesignControlHeight(JPWNoCudaUILineHeight())); }
int JPWNoCudaUINavColumns()
  {
   string tabs[3]={"Desenho","Medidas","Registro"};
   return(JPWUIDesignNavColumns(tabs,3,JPWNoCudaUIWidth()-JPWUIDesignPx(32),10,JPWUIDesignPx(8)));
  }
int JPWNoCudaUIHeaderHeight()
  {
   const int columns=JPWNoCudaUINavColumns(),rows=(3+columns-1)/columns;
   return(3*JPWNoCudaUILineHeight()+rows*(JPWNoCudaUIButtonHeight()+JPWUIDesignPx(8))+JPWUIDesignPx(24));
  }
int JPWNoCudaUIBodyHeight()
  { return(MathMax(0,JPWNoCudaUIHeight()-JPWNoCudaUIHeaderHeight()-JPWNoCudaUIButtonHeight()-JPWUIDesignPx(32))); }
int JPWNoCudaUIDailyCapacity()
  {
   const int row=JPWNoCudaUILineHeight();
   return(MathMax(1,MathMin(5,(JPWNoCudaUIBodyHeight()-row-JPWUIDesignPx(8))/(3*row+JPWUIDesignPx(16)))));
  }
int JPWNoCudaUIMeasurePages()
  { return((5+JPWNoCudaUIDailyCapacity()-1)/JPWNoCudaUIDailyCapacity()+
      (JPWNoCudaUIBodyHeight()>=2*JPWNoCudaUIButtonHeight()+2*JPWNoCudaUILineHeight()+JPWUIDesignPx(20) ? 1 : 2)+1); }

int JPWNoCudaUITextWidth(const string text,const int size)
  {
   uint width=0,height=0;
   if(TextSetFont("Arial",-size*10) && TextGetSize(text,width,height))
      return((int)width);
   return(StringLen(text)*MathMax(JPWUIDesignPx(6),JPWUIDesignPx(size*6/10)));
  }
string JPWNoCudaUIFit(const string value,const int available_pixels,
                     const int font_size)
  {
   if(JPWNoCudaUITextWidth(value,font_size)<=available_pixels) return(value);
   int chars=StringLen(value);
   while(chars>0 && JPWNoCudaUITextWidth(StringSubstr(value,0,chars)+"…",font_size)>available_pixels)
      chars--;
   return(StringSubstr(value,0,chars)+"…");
  }

bool JPWNoCudaUIDark()
  {
   const int c=(int)ChartGetInteger(0,CHART_COLOR_BACKGROUND);
   return(299*(c&255)+587*((c>>8)&255)+114*((c>>16)&255)<140000);
  }
void JPWNoCudaUIClear(const string prefix)
  {
   const string owned=prefix+"UI_";
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,owned)==0)
        { if(StringFind(name,"_DESIGN_ICON")>=0) JPWUIDesignDeleteIcon(name);
          else ObjectDelete(0,name); }
     }
   ArrayResize(g_nocuda_ui_kept,0);
   g_nocuda_ui_editing=""; g_nocuda_ui_focus="";
  }
void JPWNoCudaUIKeep(const string name)
  {
   const int count=ArraySize(g_nocuda_ui_kept);
   ArrayResize(g_nocuda_ui_kept,count+1);
   g_nocuda_ui_kept[count]=name;
  }
void JPWNoCudaUIFinish(const string prefix)
  {
   // Remove only obsolete widgets. Existing edits/buttons survive a redraw.
   const string owned=prefix+"UI_";
   for(int i=ObjectsTotal(0,0,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,0,-1);
      if(StringFind(name,owned)!=0) continue;
      bool keep=false;
      for(int k=0;k<ArraySize(g_nocuda_ui_kept);k++)
         if(g_nocuda_ui_kept[k]==name) { keep=true; break; }
      if(!keep)
        {
         if(StringFind(name,"_DESIGN_ICON")>=0) JPWUIDesignDeleteIcon(name);
         else ObjectDelete(0,name);
         if(g_nocuda_ui_editing==name) g_nocuda_ui_editing="";
         if(g_nocuda_ui_focus==name) g_nocuda_ui_focus="";
        }
     }
  }
bool JPWNoCudaUIEnsure(const string name,const ENUM_OBJECT type)
  {
   JPWNoCudaUIKeep(name);
   if(ObjectFind(0,name)>=0) return(true);
   return(ObjectCreate(0,name,type,0,0,0));
  }
void JPWNoCudaUIString(const string name,const ENUM_OBJECT_PROPERTY_STRING property,
                      const string value)
  {
   if(ObjectGetString(0,name,property)!=value)
      ObjectSetString(0,name,property,value);
  }
bool JPWNoCudaUIBox(const string name,const int x,const int y,
                    const int w,const int h,const color fill,const color border)
  {
   if(!JPWNoCudaUIEnsure(name,OBJ_RECTANGLE_LABEL)) return(false);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,w) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,h) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,border) &&
          ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true));
  }
bool JPWNoCudaUIText(const string name,const int x,const int y,
                     const string value,const int size,const color ink,
                     const string tooltip="")
  {
   if(!JPWNoCudaUIEnsure(name,OBJ_LABEL)) return(false);
   JPWNoCudaUIString(name,OBJPROP_FONT,"Arial");
   JPWNoCudaUIString(name,OBJPROP_TEXT,value);
   JPWNoCudaUIString(name,OBJPROP_TOOLTIP,tooltip=="" ? value : tooltip);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,size) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,ink) &&
          ObjectSetInteger(0,name,OBJPROP_SELECTABLE,false) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true));
  }
bool JPWNoCudaUIButton(const string name,const int x,const int y,
                       const int w,const int h,const string label,
                       const color ink,const color fill)
  {
   if(!JPWNoCudaUIEnsure(name,OBJ_BUTTON)) return(false);
   JPWNoCudaUIString(name,OBJPROP_FONT,"Arial");
   JPWNoCudaUIString(name,OBJPROP_TEXT,JPWNoCudaUIFit(label,w-JPWUIDesignPx(16),10));
   JPWNoCudaUIString(name,OBJPROP_TOOLTIP,label);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,w) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,h) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,10) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,ink) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill) &&
          ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,name==g_nocuda_ui_focus ? ink : fill) &&
          ObjectSetInteger(0,name,OBJPROP_STATE,false) &&
          ObjectSetInteger(0,name,OBJPROP_ZORDER,1005) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true));
  }
bool JPWNoCudaUIEdit(const string name,const int x,const int y,
                     const int w,const int h,const string value,
                     const color ink,const color fill)
  {
   const bool existed=(ObjectFind(0,name)>=0);
   if(!JPWNoCudaUIEnsure(name,OBJ_EDIT)) return(false);
   JPWNoCudaUIString(name,OBJPROP_FONT,"Arial");
   // Never replace the text/caret of a focused field during timer/resize.
   if(!existed || name!=g_nocuda_ui_editing)
      JPWNoCudaUIString(name,OBJPROP_TEXT,value);
   return(ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
          ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) &&
          ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
          ObjectSetInteger(0,name,OBJPROP_XSIZE,w) &&
          ObjectSetInteger(0,name,OBJPROP_YSIZE,h) &&
          ObjectSetInteger(0,name,OBJPROP_FONTSIZE,10) &&
          ObjectSetInteger(0,name,OBJPROP_COLOR,ink) &&
          ObjectSetInteger(0,name,OBJPROP_BGCOLOR,fill) &&
          ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,name==g_nocuda_ui_focus ? ink : fill) &&
          ObjectSetInteger(0,name,OBJPROP_HIDDEN,true));
  }
string JPWNoCudaUIFocusCycle(const string prefix,const string current,
                            const bool reverse)
  {
   const int count=ArraySize(g_nocuda_ui_kept);
   int at=(reverse ? 0 : -1);
   for(int i=0;i<count;i++) if(g_nocuda_ui_kept[i]==current) { at=i; break; }
   for(int step=1;step<=count;step++)
     {
      const int index=(at+(reverse ? -step : step)+2*count)%count;
      const string name=g_nocuda_ui_kept[index];
      if(StringFind(name,prefix+"UI_")==0 &&
         ObjectFind(0,name)>=0 &&
         (ObjectGetInteger(0,name,OBJPROP_TYPE)==OBJ_BUTTON ||
          (ObjectGetInteger(0,name,OBJPROP_TYPE)==OBJ_EDIT && !ObjectGetInteger(0,name,OBJPROP_READONLY))))
         return(name);
     }
   return("");
  }

void JPWNoCudaUIWrap(const string value,const int width,const int size,
                    string &lines[])
  {
   ArrayResize(lines,0);
   string pending=value;
   while(StringLen(pending)>0)
     {
      int end=StringLen(pending);
      while(end>1 && JPWNoCudaUITextWidth(StringSubstr(pending,0,end),size)>width)
         end--;
      if(end<StringLen(pending))
        {
         int space=end;
         while(space>0 && StringSubstr(pending,space,1)!=" ") space--;
         if(space>0) end=space;
        }
      const int count=ArraySize(lines);
      ArrayResize(lines,count+1);
      lines[count]=StringSubstr(pending,0,end);
      pending=StringSubstr(pending,end);
      while(StringLen(pending)>0 && StringSubstr(pending,0,1)==" ") pending=StringSubstr(pending,1);
     }
   if(ArraySize(lines)==0) { ArrayResize(lines,1); lines[0]="—"; }
  }
void JPWNoCudaUIParagraph(const string name,const int x,const int y,
                         const int width,const int row,const string value,
                         const int max_rows,const color ink)
  {
   string lines[];
   JPWNoCudaUIWrap(value,width,10,lines);
   for(int i=0;i<ArraySize(lines) && i<max_rows;i++)
      JPWNoCudaUIText(name+(i==0 ? "" : "_"+IntegerToString(i)),x,y+i*row,
                     lines[i],10,ink,value);
  }
void JPWNoCudaUIDataRow(const string name,const int x,const int y,
                       const int width,const int row,const string value,
                       const color ink,const string explanation)
  {
   const int divider=StringFind(value,": ");
   const int range=StringFind(value," / ",divider+2);
   if(JPWNoCudaUITextWidth(value,11)>width && divider>=0)
     {
      string label=StringSubstr(value,0,divider+1);
      if(JPWNoCudaUITextWidth(label,10)>width && StringFind(value,"Média dos extremos: ")==0) label="Média:";
      if(JPWNoCudaUITextWidth(label,10)>width && StringFind(value,"Largura / 1/8: ")==0) label="Larg. / 1/8:";
      JPWNoCudaUIText(name,x,y,label,10,ink,explanation);
      if(range>divider)
        {
         JPWNoCudaUIText(name+"_B",x,y+row,StringSubstr(value,divider+2,range-divider-2),11,ink,explanation);
         JPWNoCudaUIText(name+"_C",x,y+2*row,StringSubstr(value,range+3),11,ink,explanation);
        }
      else JPWNoCudaUIText(name+"_B",x,y+row,StringSubstr(value,divider+2),11,ink,explanation);
      return;
     }
   JPWNoCudaUIText(name,x,y,value,11,ink,explanation);
  }
void JPWNoCudaUIAppend(const string value,const int width,string &lines[])
  {
   string wrapped[]; JPWNoCudaUIWrap(value,width,10,wrapped);
   const int count=ArraySize(lines),extra=ArraySize(wrapped);
   ArrayResize(lines,count+extra+1);
   for(int i=0;i<extra;i++) lines[count+i]=wrapped[i];
   lines[count+extra]="";
  }

// The companion HUD is a visual reservation only. No configuration, sample
// or financial value is consulted; placement depends on rectangle/font/area.
struct JPWNoCudaUIRect
  { int x; int y; int width; int height; };
bool JPWNoCudaUIRectIntersects(const JPWNoCudaUIRect &a,const JPWNoCudaUIRect &b)
  { return(a.x<b.x+b.width && b.x<a.x+a.width && a.y<b.y+b.height && b.y<a.y+a.height); }
bool JPWNoCudaUICockpitHUD(const int cw,const int ch,JPWNoCudaUIRect &hud)
  {
   const string name=StringFormat("JPW_LEV_%I64d_HUD_BG",ChartID());
   if(ObjectFind(0,name)<0 || ObjectGetInteger(0,name,OBJPROP_TYPE)!=OBJ_RECTANGLE_LABEL ||
      ObjectGetInteger(0,name,OBJPROP_CORNER)!=CORNER_LEFT_UPPER) return(false);
   const int x=(int)ObjectGetInteger(0,name,OBJPROP_XDISTANCE);
   const int y=(int)ObjectGetInteger(0,name,OBJPROP_YDISTANCE);
   const int width=(int)ObjectGetInteger(0,name,OBJPROP_XSIZE);
   const int height=(int)ObjectGetInteger(0,name,OBJPROP_YSIZE);
   if(x<0 || y<0 || width<=0 || height<=0 || x>=cw || y>=ch) return(false);
   hud.x=x; hud.y=y; hud.width=MathMin(width,cw-x); hud.height=MathMin(height,ch-y);
   return(true);
  }
bool g_nocuda_ui_hud_seen=false,g_nocuda_ui_hud_valid=false;
JPWNoCudaUIRect g_nocuda_ui_hud_previous;
string g_nocuda_ui_launcher_reason="";
bool JPWNoCudaUILauncherReservationChanged()
  {
   JPWNoCudaUIRect hud;
   const bool valid=JPWNoCudaUICockpitHUD((int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS),
      (int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS),hud);
   if(!g_nocuda_ui_hud_seen || valid!=g_nocuda_ui_hud_valid) return(true);
   return(valid && (hud.x!=g_nocuda_ui_hud_previous.x || hud.y!=g_nocuda_ui_hud_previous.y ||
      hud.width!=g_nocuda_ui_hud_previous.width || hud.height!=g_nocuda_ui_hud_previous.height));
  }
void JPWNoCudaUIRememberHUD(const int cw,const int ch)
  {
   g_nocuda_ui_hud_valid=JPWNoCudaUICockpitHUD(cw,ch,g_nocuda_ui_hud_previous);
   g_nocuda_ui_hud_seen=true;
  }
// Placement is visual only: never rewrites the user's corner preference.
// The nearest fitting side of the observed HUD wins; exact ties keep this order.
bool JPWNoCudaUILauncherAt(const int cw,const int ch,const int width,const int height,
                           const int desired_x,const int desired_y,JPWNoCudaUIRect &place)
  {
   const int gap=JPWUIDesignPx(8);
   if(width<=0 || height<=0 || cw<width+2*gap || ch<height+2*gap) return(false);
   const int px=MathMax(gap,MathMin(desired_x,cw-width-gap));
   const int py=MathMax(gap,MathMin(desired_y,ch-height-gap));
   JPWNoCudaUIRect hud; const bool reserved=JPWNoCudaUICockpitHUD(cw,ch,hud);
   place.x=px; place.y=py; place.width=width; place.height=height;
   if(!reserved || !JPWNoCudaUIRectIntersects(place,hud)) return(true);
   int xs[4]={px,px,hud.x-width-gap,hud.x+hud.width+gap};
   int ys[4]={hud.y-height-gap,hud.y+hud.height+gap,py,py};
   bool found=false; long best=0;
   for(int i=0;i<4;i++)
     {
      JPWNoCudaUIRect candidate;
      candidate.x=MathMax(gap,MathMin(xs[i],cw-width-gap));
      candidate.y=MathMax(gap,MathMin(ys[i],ch-height-gap));
      candidate.width=width; candidate.height=height;
      if(JPWNoCudaUIRectIntersects(candidate,hud)) continue;
      const long dx=(long)candidate.x-px,dy=(long)candidate.y-py;
      const long distance=dx*dx+dy*dy;
      if(!found || distance<best) { found=true; best=distance; place=candidate; }
     }
   return(found);
  }
bool JPWNoCudaUILauncherPlacement(const int cw,const int ch,const int minimum_width,
                                 const int height,JPWNoCudaUIRect &place)
  { return(JPWNoCudaUILauncherAt(cw,ch,minimum_width,height,JPWUIDesignPx(12),ch-height-JPWUIDesignPx(12),place)); }

void JPWNoCudaUIRender(const string prefix,const JPWNoCudaUIView &v)
  {
   ArrayResize(g_nocuda_ui_kept,0);
   const int cw=(int)ChartGetInteger(0,CHART_WIDTH_IN_PIXELS);
   const int ch=(int)ChartGetInteger(0,CHART_HEIGHT_IN_PIXELS);
   JPWNoCudaUIRememberHUD(cw,ch);
   g_nocuda_ui_launcher_reason="";
   const bool dark=JPWNoCudaUIDark();
   const color ink=(dark ? C'232,234,238' : C'39,45,53');
   const color muted=(dark ? C'177,182,188' : C'96,103,112');
   const color surface=(dark ? C'28,31,37' : C'247,249,252');
   const color chrome=(dark ? C'39,45,54' : C'233,238,244');
   const color card=(dark ? C'34,39,47' : C'255,255,255');
   const color border=(dark ? C'102,110,122' : C'128,135,147');
   const color accent=(dark ? C'151,185,217' : C'48,79,112');
   const int line=JPWNoCudaUILineHeight(),bh=JPWNoCudaUIButtonHeight();
   const int candidate_inner=JPWNoCudaUIWidth()-JPWUIDesignPx(32);
   const int candidate_available=JPWNoCudaUIHeight()-JPWNoCudaUIHeaderHeight()-bh-JPWUIDesignPx(24);
   int minimum_body=2*line+bh;
   if(v.tab==0) minimum_body=MathMax(minimum_body,6*line+2*bh+JPWUIDesignPx(52));
   if(v.tab==1) minimum_body=MathMax(minimum_body,4*line+JPWUIDesignPx(16));
   if(v.tab==2) minimum_body=MathMax(minimum_body,(candidate_inner>=JPWUIDesignPx(500) ? bh+JPWUIDesignPx(8) : 2*(bh+JPWUIDesignPx(8)))+line+JPWUIDesignPx(24));
   if(!v.open || cw<JPWUIDesignPx(300) || ch<JPWUIDesignPx(260) || candidate_available<minimum_body)
     {
      const string launcher_text="NoCuda · Gráficos";
      const int button_width=JPWUIDesignButtonWidth(launcher_text,10,true);
      const int hint_count=(v.pick>0 ? 1 : 0)+(v.open ? 1 : 0);
      const int full_height=bh+hint_count*(line+JPWUIDesignPx(8));
      JPWNoCudaUIRect place;
      bool show_hints=JPWNoCudaUILauncherPlacement(cw,ch,button_width,full_height,place);
      if(!show_hints && !JPWNoCudaUILauncherPlacement(cw,ch,button_width,bh,place))
        {
         g_nocuda_ui_launcher_reason="NoCuda: espaço livre insuficiente; amplie o gráfico ou reposicione o HUD do Cockpit. Rascunho preservado.";
         JPWNoCudaUIFinish(prefix); return;
        }
      JPWNoCudaUIButton(prefix+"UI_OPEN",place.x,place.y,button_width,bh,"",ink,chrome);
      const int icon=JPWUIDesignPx(16),inset=JPWUIDesignPx(12);
      const string icon_name=prefix+"UI_OPEN_DESIGN_ICON";
      JPWNoCudaUIKeep(icon_name);
      JPWUIDesignIcon(icon_name,place.x+inset,place.y+(bh-icon)/2,icon,ink,true);
      JPWNoCudaUIText(prefix+"UI_OPEN_LABEL",place.x+inset+icon+JPWUIDesignPx(8),
         place.y+(bh-line)/2,launcher_text,10,ink);
      ObjectSetString(0,prefix+"UI_OPEN",OBJPROP_TOOLTIP,launcher_text);
      ObjectSetString(0,prefix+"UI_OPEN",OBJPROP_TOOLTIP,v.status+
         (v.open ? " · Amplie a altura do gráfico; rascunho preservado" : ""));
      int hint_y=place.y+bh+JPWUIDesignPx(8);
      if(show_hints && v.pick>0)
        {
         JPWNoCudaUIText(prefix+"UI_PICK_HINT",place.x,hint_y,
            JPWNoCudaUIFit(v.status,place.width,10),10,ink,v.status);
         hint_y+=line+JPWUIDesignPx(8);
        }
      if(show_hints && v.open) JPWNoCudaUIText(prefix+"UI_SMALL_HINT",place.x,hint_y,
         JPWNoCudaUIFit("Amplie a altura do gráfico · rascunho preservado",place.width,10),10,muted);
      JPWNoCudaUIFinish(prefix); return;
     }

   const int w=JPWNoCudaUIWidth(),h=JPWNoCudaUIHeight();
   const int x=(cw-w)/2,y=(ch-h)/2,pad=JPWUIDesignPx(16),inner=w-2*pad;
   const int title_y=y+JPWUIDesignPx(12),tab_y=y+JPWUIDesignPx(16)+2*line;
   const int body_y=y+JPWNoCudaUIHeaderHeight();
   const int footer_y=y+h-bh-JPWUIDesignPx(12),body_bottom=footer_y-JPWUIDesignPx(12);
   const string state=(v.history_diverged ? "Histórico divergente · revisão necessária" : v.draft ? (v.geometry_valid ? "Prévia · não salva" : "Rascunho · marque A → B → C") :
      (v.revision>0 ? (v.revision<v.head_revision ? "Revisão histórica · consulta" : "Confirmado · revisão "+IntegerToString(v.revision)) : "Nenhum canal confirmado"));
   JPWNoCudaUIBox(prefix+"UI_BG",x,y,w,h,surface,border);
   JPWNoCudaUIBox(prefix+"UI_HEADER",x+1,y+1,w-2,body_y-y-1,chrome,chrome);
   JPWNoCudaUIKeep(prefix+"UI_BRAND_LOGO"); JPWNoCudaUIKeep(prefix+"UI_TITLE");
   JPWGenetrixHeader(prefix+"UI_BRAND_LOGO",prefix+"UI_TITLE",x+pad,title_y,
      inner,line,13,ink,dark,"NoCuda · Gráficos · manual · "+v.symbol,4);
   JPWNoCudaUIText(prefix+"UI_STAGE",x+pad,title_y+line,
      JPWNoCudaUIFit(state+" · "+v.source_tf,inner,10),10,accent,state+" · "+v.source_tf);
   string tabs[3]={"Desenho","Medidas","Registro"};
   const int gap=JPWUIDesignPx(8),columns=JPWNoCudaUINavColumns(),rows=(3+columns-1)/columns;
   const int tw=(inner-(columns-1)*gap)/columns;
   for(int t=0;t<3;t++)
      JPWNoCudaUIButton(prefix+"UI_TAB_"+IntegerToString(t),x+pad+(t%columns)*(tw+gap),
         tab_y+(t/columns)*(bh+gap),tw,bh,tabs[t],t==v.tab ? (dark ? surface : card) : ink,t==v.tab ? accent : card);
   JPWNoCudaUIText(prefix+"UI_STATUS",x+pad,tab_y+rows*(bh+gap),
      JPWNoCudaUIFit(v.status,inner,10),10,muted,v.status);

   const int available=body_bottom-body_y;
   g_nocuda_ui_page=0; g_nocuda_ui_pages=1;
   if(available<2*line+bh || (v.tab==0 && available<6*line+2*bh+JPWUIDesignPx(52)) ||
      (v.tab==1 && available<4*line+JPWUIDesignPx(16)) ||
      (v.tab==2 && available<(inner>=JPWUIDesignPx(500) ? bh+JPWUIDesignPx(8) : 2*(bh+JPWUIDesignPx(8)))+line+JPWUIDesignPx(24)))
     {
      JPWNoCudaUIParagraph(prefix+"UI_SMALL",x+pad,body_y,inner,line,
         "Aumente a altura do gráfico para consultar ou editar. O rascunho é preservado.",MathMax(1,available/line),ink);
     }
   else if(v.tab==0)
     {
      const bool wide=(inner>=JPWUIDesignPx(650));
      const int columns=(wide ? 3 : 1);
      const int card_h=5*line+bh+JPWUIDesignPx(28);
      const int action_rows=1;
      const int actions_h=action_rows*(bh+JPWUIDesignPx(8));
      const int cards_space=available-actions_h-line-JPWUIDesignPx(12);
      const int anchors_per_page=MathMax(1,MathMin(3,columns*MathMax(1,cards_space/card_h)));
      const int anchor_pages=(3+anchors_per_page-1)/anchors_per_page;
      const int tools_per_page=MathMax(1,MathMin(3,(cards_space-line)/(bh+JPWUIDesignPx(8))));
      const int tool_pages=(wide ? 0 : (3+tools_per_page-1)/tools_per_page);
      g_nocuda_ui_pages=anchor_pages+1+tool_pages;
      g_nocuda_ui_page=(g_nocuda_ui_editing==prefix+"UI_JUST" ? anchor_pages : MathMax(0,MathMin(v.page,g_nocuda_ui_pages-1)));
      JPWNoCudaUIText(prefix+"UI_SOURCE",x+pad,body_y,
         JPWNoCudaUIFit("Fonte "+v.source_tf+" · Close de barras encerradas · A/B=0, C=1",inner,10),10,muted,
         "Close da barra-fonte é posicionado na abertura. Outro período é uma adaptação registrada.");
      const int content_y=body_y+line+JPWUIDesignPx(8);
      const int actions_y=body_bottom-actions_h;
      if(g_nocuda_ui_page<anchor_pages)
        {
         string values[3]; values[0]=v.a_text; values[1]=v.b_text; values[2]=v.c_text;
         bool complete[3]; complete[0]=v.anchor_a; complete[1]=v.anchor_b; complete[2]=v.anchor_c;
         string ids[3]={"A","B","C"};
         const int card_w=(inner-(columns-1)*JPWUIDesignPx(8))/columns;
         for(int i=0;i<anchors_per_page;i++)
           {
            const int a=g_nocuda_ui_page*anchors_per_page+i;
            if(a>=3) break;
            const int ax=x+pad+(i%columns)*(card_w+JPWUIDesignPx(8)),ay=content_y+(i/columns)*card_h;
            const int actual_h=MathMin(card_h-JPWUIDesignPx(8),actions_y-ay-JPWUIDesignPx(8));
            JPWNoCudaUIBox(prefix+"UI_ANCHOR_CARD_"+ids[a],ax,ay,card_w,actual_h,card,border);
            JPWNoCudaUIText(prefix+"UI_ANCHOR_TITLE_"+ids[a],ax+JPWUIDesignPx(12),ay+JPWUIDesignPx(8),
               JPWNoCudaUIFit(ids[a]+(a==2 ? " · largura" : " · principal")+(complete[a] ? " · ✓" : " · a marcar"),card_w-JPWUIDesignPx(20),10),10,accent);
            const string close_separator=" · Close ";
            const int close_at=StringFind(values[a],close_separator),date_at=StringFind(values[a],": ");
            if(complete[a] && close_at>=0 && date_at>=0)
              {
               const string price=StringSubstr(values[a],close_at+StringLen(close_separator));
               JPWNoCudaUIDataRow(prefix+"UI_"+ids[a],ax+JPWUIDesignPx(12),ay+line+JPWUIDesignPx(12),card_w-JPWUIDesignPx(20),line,
                  "Close: "+price,ink,values[a]);
               JPWNoCudaUIParagraph(prefix+"UI_DATE_"+ids[a],ax+JPWUIDesignPx(12),ay+3*line+JPWUIDesignPx(12),card_w-JPWUIDesignPx(20),line,
                  StringSubstr(values[a],date_at+2,close_at-date_at-2),2,muted);
              }
            else JPWNoCudaUIParagraph(prefix+"UI_"+ids[a],ax+JPWUIDesignPx(12),ay+line+JPWUIDesignPx(12),card_w-JPWUIDesignPx(20),line,
               values[a],MathMax(1,(actual_h-bh-line-JPWUIDesignPx(28))/line),ink);
            JPWNoCudaUIButton(prefix+"UI_PICK_"+ids[a],ax+JPWUIDesignPx(12),ay+actual_h-bh-JPWUIDesignPx(8),card_w-JPWUIDesignPx(20),bh,
               complete[a] ? "Refazer "+ids[a] : "Marcar "+ids[a],ink,chrome);
           }
        }
      else if(g_nocuda_ui_page==anchor_pages)
        {
         const int content_h=actions_y-content_y-JPWUIDesignPx(8);
         JPWNoCudaUIBox(prefix+"UI_CONFIRM_CARD",x+pad,content_y,inner,content_h,card,border);
         JPWNoCudaUIText(prefix+"UI_PREVIEW",x+pad+JPWUIDesignPx(12),content_y+JPWUIDesignPx(12),JPWNoCudaUIFit("Conferir e confirmar",inner-JPWUIDesignPx(24),11),11,accent);
         JPWNoCudaUIDataRow(prefix+"UI_WIDTH",x+pad+JPWUIDesignPx(12),content_y+line+JPWUIDesignPx(12),inner-JPWUIDesignPx(24),line,
            "Largura / 1/8: "+(v.geometry_valid ? v.width_price+" / "+v.subdivision_price : "N/A"),ink,v.width_text);
         JPWNoCudaUIText(prefix+"UI_JUST_LABEL",x+pad+JPWUIDesignPx(12),content_y+content_h-bh-line-JPWUIDesignPx(20),
            JPWNoCudaUIFit("Justificativa desta versão",inner-JPWUIDesignPx(24),10),10,muted);
         JPWNoCudaUIEdit(prefix+"UI_JUST",x+pad+JPWUIDesignPx(12),content_y+content_h-bh-JPWUIDesignPx(12),
            inner-JPWUIDesignPx(24),bh,v.justification,ink,chrome);
        }
      else
        {
         JPWNoCudaUIText(prefix+"UI_APPEARANCE",x+pad,content_y,JPWNoCudaUIFit("Aparência e período-fonte",inner,11),11,accent);
         const int tool_start=(g_nocuda_ui_page-anchor_pages-1)*tools_per_page;
         for(int tool=0;tool<tools_per_page && tool_start+tool<3;tool++)
           {
            const int ty=content_y+line+JPWUIDesignPx(8)+tool*(bh+JPWUIDesignPx(8)),index=tool_start+tool;
            if(index==0) JPWNoCudaUIButton(prefix+"UI_TF",x+pad,ty,inner,bh,"Fonte "+v.source_tf+" · mudar período",ink,card);
            if(index==1) JPWNoCudaUIButton(prefix+"UI_VIS",x+pad,ty,inner,bh,v.channel_visible ? "Ocultar canal" : "Mostrar canal",ink,card);
            if(index==2) JPWNoCudaUIButton(prefix+"UI_MESH",x+pad,ty,inner,bh,v.full_mesh ? "Malha completa · usar Essencial" : "Essencial · usar Malha completa",ink,card);
           }
        }
      const int aw=(inner-JPWUIDesignPx(8))/2;
      if(v.draft)
        {
         JPWNoCudaUIButton(prefix+"UI_CONFIRM",x+pad,actions_y,aw,bh,"Confirmar versão",v.geometry_valid ? (dark ? surface : card) : muted,v.geometry_valid ? accent : chrome);
         JPWNoCudaUIButton(prefix+"UI_CANCEL",x+pad+aw+JPWUIDesignPx(8),actions_y,aw,bh,"Cancelar rascunho",ink,chrome);
        }
      else
        {
         JPWNoCudaUIButton(prefix+"UI_NEW",x+pad,actions_y,aw,bh,"Novo canal",dark ? surface : card,accent);
         JPWNoCudaUIButton(prefix+"UI_EDIT",x+pad+aw+JPWUIDesignPx(8),actions_y,aw,bh,"Editar versão",ink,chrome);
        }
     }
   else if(v.tab==1)
     {
      const int capacity=JPWNoCudaUIDailyCapacity();
      const int query_pages=(available>=2*bh+2*line+JPWUIDesignPx(20) ? 1 : 2);
      const int result_pages=(5+capacity-1)/capacity;
      string provenance[];
      JPWNoCudaUIAppend("Origem e limites · "+v.daily_state,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend(v.daily_source,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend(v.daily_reason,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend(v.width_text,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend(v.distance_text,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend(v.quote_text,inner-JPWUIDesignPx(24),provenance);
      JPWNoCudaUIAppend("Faixa da linha, não previsão da cotação. 12h e média dos extremos são medidas distintas. Futuro até 30 dias: Estimated.",inner-JPWUIDesignPx(24),provenance);
      const int rows=MathMax(1,(available-JPWUIDesignPx(16))/line);
      const int provenance_pages=(ArraySize(provenance)+rows-1)/rows;
      g_nocuda_ui_pages=query_pages+result_pages+provenance_pages;
      g_nocuda_ui_page=MathMax(0,MathMin(v.measure_page,g_nocuda_ui_pages-1));
      if(g_nocuda_ui_editing==prefix+"UI_DATE" && query_pages==2) g_nocuda_ui_page=1;
      if(g_nocuda_ui_editing==prefix+"UI_LEVEL_INPUT") g_nocuda_ui_page=0;
      if(g_nocuda_ui_page<query_pages)
        {
         const bool level_page=(query_pages==1 || g_nocuda_ui_page==0);
         const bool date_page=(query_pages==1 || g_nocuda_ui_page==1);
         int cy=body_y;
         if(level_page)
           {
            JPWNoCudaUIText(prefix+"UI_LEVEL",x+pad,cy,JPWNoCudaUIFit("Linha selecionada · nível",inner,10),10,muted,v.level_text);
            const int qw=(inner-JPWUIDesignPx(24))/4;
            JPWNoCudaUIEdit(prefix+"UI_LEVEL_INPUT",x+pad,cy+line,qw,bh,
               v.level_input=="" ? DoubleToString(-4.0+(double)v.level_index/8.0,3) : v.level_input,ink,card);
            JPWNoCudaUIButton(prefix+"UI_LEVEL_APPLY",x+pad+qw+JPWUIDesignPx(8),cy+line,qw,bh,"Selecionar",ink,chrome);
            JPWNoCudaUIButton(prefix+"UI_LEVEL_PREV",x+pad+2*(qw+JPWUIDesignPx(8)),cy+line,qw,bh,"− nível",ink,chrome);
            JPWNoCudaUIButton(prefix+"UI_LEVEL_NEXT",x+pad+3*(qw+JPWUIDesignPx(8)),cy+line,qw,bh,"+ nível",ink,chrome);
            cy+=line+bh+JPWUIDesignPx(12);
           }
         if(date_page)
           {
            JPWNoCudaUIText(prefix+"UI_DATE_LABEL",x+pad,cy,JPWNoCudaUIFit("Data do servidor",inner,10),10,muted,"AAAA.MM.DD · 00h, 12h e 24h");
            const int fw=(inner-JPWUIDesignPx(8))/2;
            JPWNoCudaUIEdit(prefix+"UI_DATE",x+pad,cy+line,fw,bh,v.date,ink,card);
            JPWNoCudaUIButton(prefix+"UI_DAILY_QUERY",x+pad+fw+JPWUIDesignPx(8),cy+line,fw,bh,"Consultar dia",dark ? surface : card,accent);
            cy+=line+bh+JPWUIDesignPx(12);
           }
         if(cy+line<=body_bottom)
           { JPWNoCudaUIText(prefix+"UI_DAILY_STATE",x+pad,cy,JPWNoCudaUIFit("Projeção diária · "+v.daily_state,inner,10),10,accent,v.daily_reason); cy+=line+JPWUIDesignPx(8); }
         if(cy+bh<=body_bottom)
            JPWNoCudaUIButton(prefix+"UI_DAILY_REFS",x+pad,cy,inner,bh,
               v.references ? "Ocultar referências 00h / 12h / 24h" : "Mostrar referências 00h / 12h / 24h",ink,chrome);
        }
      else if(g_nocuda_ui_page<query_pages+result_pages)
        {
         const int page=g_nocuda_ui_page-query_pages;
         JPWNoCudaUIText(prefix+"UI_DAILY_STATE",x+pad,body_y,
            JPWNoCudaUIFit("Nível "+DoubleToString(-4.0+(double)v.level_index/8.0,3)+" · "+v.daily_state,inner,10),10,accent,v.daily_reason);
         string results[5]; results[0]=v.daily_start; results[1]=v.daily_mid; results[2]=v.daily_end;
         results[3]=v.daily_mean; results[4]=v.daily_range;
         for(int i=0;i<capacity && page*capacity+i<5;i++)
           {
            const int index=page*capacity+i;
            const int ry=body_y+line+JPWUIDesignPx(8)+i*(3*line+JPWUIDesignPx(16));
            JPWNoCudaUIBox(prefix+"UI_DAILY_CARD_"+IntegerToString(index),x+pad,ry,inner,3*line+JPWUIDesignPx(8),card,border);
            JPWNoCudaUIDataRow(prefix+"UI_DAILY_"+IntegerToString(index),x+pad+JPWUIDesignPx(12),ry+JPWUIDesignPx(8),
               inner-JPWUIDesignPx(24),line,results[index],ink,results[index]+" · "+v.daily_reason);
           }
        }
      else
        {
         const int start=(g_nocuda_ui_page-query_pages-result_pages)*rows;
         JPWNoCudaUIBox(prefix+"UI_PROVENANCE_CARD",x+pad,body_y,inner,available,card,border);
         for(int i=0;i<rows && start+i<ArraySize(provenance);i++)
            JPWNoCudaUIText(prefix+"UI_ORIGIN_"+IntegerToString(i),x+pad+JPWUIDesignPx(12),body_y+JPWUIDesignPx(8)+i*line,provenance[start+i],10,ink);
        }
     }
   else
     {
      string lines[];
      JPWNoCudaUIAppend("Estudo "+IntegerToString(v.study_count>0 ? v.study_index+1 : 0)+" de "+IntegerToString(v.study_count)+" · "+v.study_id,inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend(v.revision>0 ? "Revisão "+IntegerToString(v.revision)+" de "+IntegerToString(v.head_revision)+(v.revision<v.head_revision ? " · histórica, somente consulta" : " · confirmada") : "Nenhuma revisão confirmada",inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend(v.history_text,inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend(v.a_text,inner-JPWUIDesignPx(24),lines); JPWNoCudaUIAppend(v.b_text,inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend(v.c_text,inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend("Justificativa: "+v.justification,inner-JPWUIDesignPx(24),lines);
      JPWNoCudaUIAppend("Cada confirmação cria uma revisão. Consultar, navegar e redesenhar não alteram versões salvas.",inner-JPWUIDesignPx(24),lines);
      const int nav_rows=(inner>=JPWUIDesignPx(500) ? 1 : 2),nav_h=nav_rows*(bh+JPWUIDesignPx(8));
      const int rows=MathMax(1,(available-nav_h-JPWUIDesignPx(16))/line);
      g_nocuda_ui_pages=(ArraySize(lines)+rows-1)/rows;
      g_nocuda_ui_page=MathMax(0,MathMin(v.page,g_nocuda_ui_pages-1));
      JPWNoCudaUIBox(prefix+"UI_RECORD_CARD",x+pad,body_y,inner,available-nav_h-JPWUIDesignPx(8),card,border);
      for(int i=0;i<rows && g_nocuda_ui_page*rows+i<ArraySize(lines);i++)
         JPWNoCudaUIText(prefix+"UI_RECORD_LINE_"+IntegerToString(i),x+pad+JPWUIDesignPx(12),body_y+JPWUIDesignPx(8)+i*line,
            lines[g_nocuda_ui_page*rows+i],10,ink);
      const int nc=(inner>=JPWUIDesignPx(500) ? 4 : 2),nw=(inner-(nc-1)*JPWUIDesignPx(8))/nc,ny=body_bottom-nav_h;
      string names[4]={"STUDY_PREV","STUDY_NEXT","REV_PREV","REV_NEXT"};
      string labels[4]={"‹ Estudo","Estudo ›","‹ Revisão","Revisão ›"};
      for(int i=0;i<4;i++)
         JPWNoCudaUIButton(prefix+"UI_"+names[i],x+pad+(i%nc)*(nw+JPWUIDesignPx(8)),ny+(i/nc)*(bh+JPWUIDesignPx(8)),nw,bh,labels[i],ink,chrome);
     }

   const int close_w=MathMin(JPWUIDesignButtonWidth("Fechar",10),inner/3),nav_w=MathMin(JPWUIDesignPx(44),inner/6);
   JPWNoCudaUIButton(prefix+"UI_PAGE_PREV",x+pad,footer_y,nav_w,bh,"‹",ink,card);
   JPWNoCudaUIButton(prefix+"UI_PAGE_NEXT",x+pad+nav_w+JPWUIDesignPx(8),footer_y,nav_w,bh,"›",ink,card);
   JPWNoCudaUIText(prefix+"UI_PAGE",x+pad+2*nav_w+JPWUIDesignPx(20),footer_y+7,
      IntegerToString(g_nocuda_ui_page+1)+" / "+IntegerToString(g_nocuda_ui_pages),10,muted);
   JPWNoCudaUIButton(prefix+"UI_CLOSE",x+w-pad-close_w,footer_y,close_w,bh,"Fechar",ink,chrome);
   // Appearance/source tools remain available on the drawing footer, grouped
   // separately from immutable revision actions.
   if(v.tab==0 && inner>=JPWUIDesignPx(650))
     {
      const int tx=x+pad+2*nav_w+JPWUIDesignPx(80);
      const int tool_w=(x+w-pad-close_w-JPWUIDesignPx(8)-tx-JPWUIDesignPx(12))/3;
      JPWNoCudaUIButton(prefix+"UI_TF",tx,footer_y,tool_w,bh,"Fonte "+v.source_tf,ink,card);
      JPWNoCudaUIButton(prefix+"UI_VIS",tx+tool_w+JPWUIDesignPx(8),footer_y,tool_w,bh,v.channel_visible ? "Canal visível" : "Canal oculto",ink,card);
      JPWNoCudaUIButton(prefix+"UI_MESH",tx+2*(tool_w+JPWUIDesignPx(8)),footer_y,tool_w,bh,v.full_mesh ? "Malha completa" : "Essencial",ink,card);
     }
   JPWNoCudaUIFinish(prefix);
  }

#endif

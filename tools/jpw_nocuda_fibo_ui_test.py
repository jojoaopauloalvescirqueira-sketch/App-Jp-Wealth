#!/usr/bin/env python3
"""Replay the complete production NoCuda Fibonacci renderer with keyed objects.

Only chart-object, text-measurement and pointer boundaries are substituted.
This is not native compilation, clipboard, DPI or template evidence: those are
NOT_RUN until receipts from an isolated MT5 runtime verify these exact bytes.
"""
from pathlib import Path
import hashlib
import re
import shutil
import struct
import subprocess
import tempfile
from leverage_source import expanded_source

from leverage_host_shim import source_root, translate_arrays, complete_design_shim
ROOT = source_root()
SOURCE = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_UI.mqh'
LOGO = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp'

SHIM = r'''
#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
using string=std::string; using color=int; using uint=unsigned int;
using ENUM_OBJECT=int; using ENUM_OBJECT_PROPERTY_STRING=int;
constexpr int OBJ_LABEL=1,OBJ_EDIT=2,OBJ_BUTTON=3,OBJ_RECTANGLE_LABEL=4,OBJ_BITMAP_LABEL=5;
constexpr int OBJPROP_TYPE=0,OBJPROP_CORNER=1,OBJPROP_XDISTANCE=2,OBJPROP_YDISTANCE=3,
 OBJPROP_XSIZE=4,OBJPROP_YSIZE=5,OBJPROP_HIDDEN=6,OBJPROP_ZORDER=7,OBJPROP_BGCOLOR=8,
 OBJPROP_COLOR=9,OBJPROP_SELECTABLE=10,OBJPROP_ANCHOR=11,OBJPROP_FONTSIZE=12,
 OBJPROP_BORDER_COLOR=13,OBJPROP_READONLY=14,OBJPROP_STATE=15,OBJPROP_FONT=16,
 OBJPROP_TEXT=17,OBJPROP_TOOLTIP=18,OBJPROP_BMPFILE=19;
constexpr int CORNER_LEFT_UPPER=0,ANCHOR_LEFT_UPPER=0,CHART_COLOR_BACKGROUND=1,
 CHART_WIDTH_IN_PIXELS=2,CHART_HEIGHT_IN_PIXELS=3,CHARTEVENT_OBJECT_CLICK=1,CHARTEVENT_MOUSE_MOVE=2;
constexpr int OBJPROP_BACK=20,OBJPROP_SELECTED=21,TERMINAL_SCREEN_DPI=1;
struct Object { int type=0;std::map<int,long> number;std::map<int,string> text; };
std::map<string,Object> objects;
int chart_width=1440,chart_height=1000,dpi=100,measured_font=11,pref_writes=0;
int background=0xffffff;
long TerminalInfoInteger(int){return dpi*96/100;}
long long ChartID(){return 123456;}
string StringFormat(const string&,long long n){return "JPW_LEV_"+std::to_string(n)+"_HUD_BG";}
string DoubleToString(double v,int n){std::ostringstream s;s<<std::fixed<<std::setprecision(n)<<v;return s.str();}
double MathMax(double a,double b){return std::max(a,b);}
double MathMin(double a,double b){return std::min(a,b);}
template<class T>int ArraySize(const std::vector<T>&a){return (int)a.size();}
template<class T>int ArrayResize(std::vector<T>&a,int n){a.resize(n);return n;}
int StringLen(const string&s){return (int)s.size();}
int StringFind(const string&s,const string&n,int start=0){auto p=s.find(n,start);return p==string::npos?-1:(int)p;}
string StringSubstr(const string&s,int p,int count=-1){return p>(int)s.size()?"":s.substr(p,count<0?string::npos:(size_t)count);}
string IntegerToString(long n){return std::to_string(n);}
long StringToInteger(const string&s){try{return std::stol(s);}catch(...){return 0;}}
int StringSplit(const string&s,char delimiter,std::vector<string>&a){a.clear();std::stringstream ss(s);string v;while(std::getline(ss,v,delimiter))a.push_back(v);return (int)a.size();}
bool TextSetFont(const string&,int size){measured_font=std::abs(size)/10;return true;}
bool TextGetSize(const string&s,uint&w,uint&h){int chars=0;for(unsigned char c:s)if((c&0xc0)!=0x80)chars++;h=(uint)((measured_font*4*dpi+299)/300);w=(uint)(chars*h*.48);return true;}
long ChartGetInteger(int,int p){return p==CHART_WIDTH_IN_PIXELS?chart_width:p==CHART_HEIGHT_IN_PIXELS?chart_height:background;}
int ObjectFind(int,const string&n){return objects.count(n)?1:-1;}
bool ObjectCreate(int,const string&n,int type,int,int,int){objects[n]=Object{};objects[n].type=type;return true;}
bool ObjectDelete(int,const string&n){return objects.erase(n)>0;}
long ObjectGetInteger(int,const string&n,int p){auto i=objects.find(n);if(i==objects.end())return 0;return p==OBJPROP_TYPE?i->second.type:i->second.number[p];}
string ObjectGetString(int,const string&n,int p){auto i=objects.find(n);return i==objects.end()?"":i->second.text[p];}
bool ObjectSetInteger(int,const string&n,int p,long v){objects[n].number[p]=v;return true;}
bool ObjectSetString(int,const string&n,int p,const string&v){objects[n].text[p]=v;if(n=="JPW_NOCUDA_FIBO_VISUAL_V1"&&p==OBJPROP_TOOLTIP)pref_writes++;return true;}
int ObjectsTotal(int,int,int){return (int)objects.size();}
string ObjectName(int,int i,int,int){auto p=objects.begin();std::advance(p,i);return p->first;}
'''

MAIN = r'''
int checks=0,failures=0,usable=0,constrained=0;
void check(bool ok,const string&message){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<message<<"\n";}}
string P="SYNTHETIC_";
string name(const string&s){return JPWNoCudaFiboUIName(P,s);}
string txt(const string&s){return ObjectGetString(0,name(s),OBJPROP_TEXT);}
bool inside(const Object&o){
 for(int p:{OBJPROP_XDISTANCE,OBJPROP_YDISTANCE,OBJPROP_XSIZE,OBJPROP_YSIZE})if(!o.number.count(p))return false;
return o.number.at(OBJPROP_XDISTANCE)>=g_fc_layout.x&&o.number.at(OBJPROP_YDISTANCE)>=g_fc_layout.y&&
 o.number.at(OBJPROP_XDISTANCE)+o.number.at(OBJPROP_XSIZE)<=g_fc_layout.x+g_fc_layout.width&&
 o.number.at(OBJPROP_YDISTANCE)+o.number.at(OBJPROP_YSIZE)<=g_fc_layout.y+g_fc_layout.height;}
bool inside_name(const string& n){const auto at=objects.find(n);return at!=objects.end()&&inside(at->second);}
bool physical_name(const string&n){const auto it=objects.find(n);if(it==objects.end())return false;const auto&p=it->second.number;
 for(int key:{OBJPROP_XDISTANCE,OBJPROP_YDISTANCE,OBJPROP_XSIZE,OBJPROP_YSIZE})if(!p.count(key))return false;
 return p.at(OBJPROP_XSIZE)>0&&p.at(OBJPROP_YSIZE)>0&&p.at(OBJPROP_XDISTANCE)>=0&&p.at(OBJPROP_YDISTANCE)>=0&&
 p.at(OBJPROP_XDISTANCE)+p.at(OBJPROP_XSIZE)<=chart_width&&p.at(OBJPROP_YDISTANCE)+p.at(OBJPROP_YSIZE)<=chart_height;}
void reset(int width=1440,int height=1000,int font=11,int scale=100){
 chart_width=width;chart_height=height;dpi=scale;objects.clear();pref_writes=0;g_fc_initialized=false;
 g_fc_focus="";g_fc_editing="";g_fc_notice="";g_fc_tab=-1;g_fc_gesture=false;g_fc_mouse_down=false;g_fc_settings_dirty=false;g_fc_scroll=0;
 JPWNoCudaFiboUILoadPrefs();g_fc_pref.font=font;g_fc_draft=g_fc_pref;
}
JPWNoCudaFiboView fixture(){
 JPWNoCudaFiboView v{};v.open=true;v.tab=0;v.symbol="SYNTHETIC.H4";v.source_name="Fibo owner selected";v.source_tf="H4";
 v.status="Vínculo conferido · paridade nativa pendente";v.reason="UNVERIFIED_NATIVE · falta recibo dos bytes exatos";
 v.quote_text="Bid 1.12345678901234567890123456789 · servidor";
 v.selected_value="0.125";v.justification="Contexto sem alteração financeira";v.projection_date="2026.10.01";
 v.observation_time="2026.10.01 12:00:00 · servidor";v.observation_note="Observação manual sintética";
 v.record_detail="Versões imutáveis";v.provenance="Calendário H4 Estimated · não prevê a cotação";
 string labels[5]={"00h · início","12h · meio do dia","24h · fim","Média dos extremos","Faixa da linha"};
 for(int i=0;i<5;i++){v.projection_labels[i]=labels[i];v.projection_values[i]="N/A · UNVERIFIED_NATIVE "+std::to_string(i);}
 JPWNoCudaFiboUIItem item{};item.id="native-object-id-EXACT";item.title="Canal Fibonacci proprietário";item.state="Conferir";
 item.detail="Três âncoras + 65 níveis originais";item.selected=true;v.sources.push_back(item);
 item.id="revision-immutable-42";item.title="Revisão 42";v.records.push_back(item);
 JPWNoCudaFiboUIMetric m{};m.valid=true;m.label="17 · rótulo original";m.raw_level="0.125";
 m.price="1.12345678901234567890123456789";m.nominal="0.00001234567890123456789";m.points="12.34567890123456789";
 m.percent="0.0001234567890123456789%";m.state="UNVERIFIED_NATIVE";m.reason="Valor sintético de apresentação";
 v.below=m;v.above=m;v.above.raw_level="0.25";v.above.label="Rótulo acima";v.below.highlight=true;
 v.nearest=v.below;v.selected=v.above;return v;
}
bool seen_value(const string&value){for(auto&i:objects)if(i.second.text[OBJPROP_TEXT]==value)return true;return false;}
double linear(int c){double v=c/255.;return v<=.04045?v/12.92:std::pow((v+.055)/1.055,2.4);}
double lum(int c){return .2126*linear(c&255)+.7152*linear((c>>8)&255)+.0722*linear((c>>16)&255);}
double contrast(int a,int b){return (std::max(lum(a),lum(b))+.05)/(std::min(lum(a),lum(b))+.05);}
int main(){
 reset();auto v=fixture();JPWNoCudaFiboUIDraw(P,v);
 check(g_fc_layout.width==1296&&g_fc_layout.height==900,"default window occupies 90 percent of chart");
 check(txt("FC_HEADER_CLOSE")=="×"&&txt("FC_CLOSE")=="Fechar","header and footer have distinct close object names");
 check(ObjectGetInteger(0,name("FC_HEADER_CLOSE"),OBJPROP_YDISTANCE)<ObjectGetInteger(0,name("FC_CLOSE"),OBJPROP_YDISTANCE),"keyed object replay keeps header close pinned");
 check(JPWNoCudaFiboUIHitAction(P,name("FC_HEADER_CLOSE"))=="FC_CLOSE","header close maps to common controller action");
 check(JPWNoCudaFiboUIHitAction(P,"COCKPIT_FC_FC_CLOSE")=="","foreign UI click never becomes NoCuda action");
 check(JPWNoCudaFiboUIActionID("FC_SOURCE_0")=="native-object-id-EXACT","source action retains exact rendered identity");
 check(pref_writes==0,"draw and initial preference loading do not persist visual changes");
 auto rect=g_fc_layout;for(int i=0;i<20;i++)JPWNoCudaFiboUIDraw(P,v);
 check(g_fc_layout.width==rect.width&&g_fc_layout.height==rect.height&&pref_writes==0,"ticks and redraws preserve window geometry without preference writes");
 check(ObjectFind(0,name("LOGO"))>=0,"existing brand bitmap resource is rendered in large header");
 v.tab=1;JPWNoCudaFiboUIDraw(P,v);
 check(ObjectFind(0,name("BELOW_CARD"))>=0&&ObjectFind(0,name("ABOVE_CARD"))>=0,"adjacent lines share one comparison row on wide charts");
 check(ObjectGetInteger(0,name("BELOW_CARD"),OBJPROP_YDISTANCE)==ObjectGetInteger(0,name("ABOVE_CARD"),OBJPROP_YDISTANCE),"both neighbour cards align vertically");
 check(txt("BELOW_LINE").find("17")!=string::npos&&txt("BELOW_LINE").find("0.125")!=string::npos,"native label and raw geometric level stay separate");
 check(seen_value(v.below.price),"long numeric price is preserved intact rather than ellipsis");
 v.tab=2;JPWNoCudaFiboUIDraw(P,v);for(int i=0;i<5;i++)check(seen_value(v.projection_values[i]),"all five projection results fit the ample table");
 const string edit=name("FC_DATE");g_fc_editing=edit;ObjectSetString(0,edit,OBJPROP_TEXT,"2026.10.14");
 JPWNoCudaFiboUIDraw(P,v);check(ObjectGetString(0,edit,OBJPROP_TEXT)=="2026.10.14","redraw preserves in-progress date text/caret boundary");
 JPWNoCudaFiboUIFieldCapture(P,v);check(v.projection_date=="2026.10.14","date capture retrieves user draft only");
 g_fc_draft.height=200;JPWNoCudaFiboUIDraw(P,v);
 check(ObjectFind(0,edit)>=0&&g_fc_editing==edit&&ObjectGetString(0,edit,OBJPROP_TEXT)=="2026.10.14"&&g_fc_deferred_prune,"resize preserves active editor text and defers destructive pruning");
 JPWNoCudaFiboUIEndInteraction();JPWNoCudaFiboUIDraw(P,v);
 check(ObjectFind(0,edit)<0&&g_fc_editing.empty(),"ending edit permits safe removal of unavailable field");
 g_fc_draft.height=900;JPWNoCudaFiboUIDraw(P,v);
 check(ObjectGetString(0,edit,OBJPROP_TEXT)=="2026.10.14","captured draft survives a field disappearing and returning on resize");g_fc_editing="";
 const int before=pref_writes;long px=ObjectGetInteger(0,name("FC_DRAG"),OBJPROP_XDISTANCE)+8;double py=ObjectGetInteger(0,name("FC_DRAG"),OBJPROP_YDISTANCE)+8;string state="1";
 JPWNoCudaFiboUIHandleGeometry(P,CHARTEVENT_OBJECT_CLICK,px,py,name("FC_DRAG"));
 check(!g_fc_gesture,"object click does not arm a released gesture");
 JPWNoCudaFiboUIHandleGeometry(P,CHARTEVENT_MOUSE_MOVE,px,py,state);px+=30;py+=40;
 JPWNoCudaFiboUIHandleGeometry(P,CHARTEVENT_MOUSE_MOVE,px,py,state);check(pref_writes==before,"pointer move does not persist before gesture release");
 state="0";JPWNoCudaFiboUIHandleGeometry(P,CHARTEVENT_MOUSE_MOVE,px,py,state);check(pref_writes==before+1&&!g_fc_gesture,"released explicit UI gesture saves geometry once");
 const auto saved=g_fc_pref;JPWNoCudaFiboUIActions("FC_FONT_PLUS");JPWNoCudaFiboUIActions("FC_SETTINGS_CANCEL");
 check(g_fc_draft.font==saved.font,"cancel restores applied appearance");
 JPWNoCudaFiboUIActions("FC_PRESET_0");check(g_fc_draft.width==680&&g_fc_draft.height==520,"compact preset is explicit and bounded");
 JPWNoCudaFiboUIActions("FC_SETTINGS_APPLY");check(g_fc_pref.width==680,"apply commits visual preference only");
 reset();ObjectCreate(0,JPWNoCudaFiboUIPrefName(),OBJ_LABEL,0,0,0);ObjectSetString(0,JPWNoCudaFiboUIPrefName(),OBJPROP_TOOLTIP,"V99|CORRUPT");
 int writes=pref_writes;JPWNoCudaFiboUILoadPrefs();v=fixture();JPWNoCudaFiboUIDraw(P,v);
 check(g_fc_pref_invalid&&ObjectGetString(0,JPWNoCudaFiboUIPrefName(),OBJPROP_TOOLTIP)=="V99|CORRUPT"&&pref_writes==writes,"invalid visual object is warned and preserved until explicit apply");
 // Large catalogs retain their own scroll; controls and draft are independent.
 reset();v=fixture();v.sources.clear();for(int i=0;i<70;i++){JPWNoCudaFiboUIItem r{};r.id="native-"+std::to_string(i);r.title="Fibo "+std::to_string(i);r.detail="Três âncoras";v.sources.push_back(r);}
 JPWNoCudaFiboUIDraw(P,v);g_fc_scroll=g_fc_scroll_max;JPWNoCudaFiboUIDraw(P,v);
 check(JPWNoCudaFiboUIActionID("FC_IMPORT")==""&&ObjectFind(0,name("FC_IMPORT"))>=0,"long source catalog exposes import with internal scroll");
 v.sources.clear();JPWNoCudaFiboUIDraw(P,v);check(g_fc_scroll<=g_fc_scroll_max&&ArraySize(g_fc_actions)>5,"shrinking data clamps scroll before rendering first frame");
 // Every tab shares the pinned shell; no action identity changes on redraw.
 reset();v=fixture();
 for(int tab=0;tab<5;tab++){
  v.tab=tab;JPWNoCudaFiboUIDraw(P,v);
  check(txt("FC_HEADER_CLOSE")=="×","all five tabs retain one independent header close");
  std::vector<string> visited;
  string focus="";
  for(int i=0;i<(int)g_fc_keep.size();i++){
   focus=JPWNoCudaFiboUIFocusCycle(focus,false);if(focus.empty())break;visited.push_back(focus);
  }
  check(std::find(visited.begin(),visited.end(),name("FC_HEADER_CLOSE"))!=visited.end(),"keyboard cycle includes global close on every tab");
  for(const auto&o:objects)if(StringFind(o.first,P+"FC_")==0)check(inside(o.second),"full tab geometry remains inside ample window");
 }
 reset(180,180,24,200);v=fixture();JPWNoCudaFiboUIDraw(P,v);
 check(!g_fc_layout.usable&&physical_name(name("FC_CLOSE")),"impossible tiny frame preserves a close hatch without false usable status");
 reset();v=fixture();v.tab=1;v.below.valid=false;v.above.valid=false;v.selected.valid=false;
 JPWNoCudaFiboUIDraw(P,v);check(!seen_value(v.below.price)&&txt("BELOW_PRICE")=="N/A","unverified unavailable metrics do not reveal numerical candidates as accepted values");
 reset();v=fixture();v.preview=true;v.record_detail="2026.10.01 00:00:00 = 1.1234567890123456|2026.10.01 04:00:00 = 1.2345678901234567|2026.10.01 08:00:00 = 1.3456789012345678";
 JPWNoCudaFiboUIDraw(P,v);
 check(txt("PREVIEW_ANCHOR_0_VALUE")=="2026.10.01 00:00:00 = 1.1234567890123456"&&
       txt("PREVIEW_ANCHOR_2_VALUE")=="2026.10.01 08:00:00 = 1.3456789012345678","import preview shows all exact anchor bytes before confirmation");
 bool cancel_available=false;
 for(int at=0;at<=g_fc_scroll_max;at++){g_fc_scroll=at;JPWNoCudaFiboUIDraw(P,v);cancel_available|=ObjectFind(0,name("FC_IMPORT_CANCEL"))>=0;}
 check(cancel_available,"import preview exposes explicit cancel within same tab");
 for(int font:{18,19})for(int theme:{0,1}){
  reset(320,1080,font,150);background=theme?0x171b21:0xffffff;v=fixture();v.tab=0;JPWNoCudaFiboUIDraw(P,v);
  check(physical_name(name("TITLE"))&&txt("TITLE").find("NoCuda")!=string::npos,"narrow title regression: NoCuda caption remains visible at font18/19 and150percent");
 }
 int cases=0;
 for(int font=9;font<=24;font++)for(int scale:{100,125,150,200})for(int width:{320,390,800,1440})for(int height:{420,720,1080})for(int theme:{0,1}){
  reset(width,height,font,scale);background=theme?0x171b21:0xffffff;v=fixture();v.tab=2;JPWNoCudaFiboUIDraw(P,v);cases++;
  const string exit=physical_name(name("FC_HEADER_CLOSE"))?name("FC_HEADER_CLOSE"):name("FC_CLOSE");
  check(physical_name(exit),"responsive window retains a real physically bounded exit");
  check(JPWNoCudaFiboUIHitAction(P,exit)=="FC_CLOSE","responsive exit maps to actual close action");
  bool title=false;for(const auto&o:objects)if(o.second.type==OBJ_LABEL&&o.second.text.count(OBJPROP_TEXT)&&o.second.text.at(OBJPROP_TEXT).find("NoCuda")!=string::npos&&physical_name(o.first))title=true;
  check(title,"NoCuda title is visibly identifiable in every viewport");
  if(g_fc_layout.usable)check(inside_name(name("FC_CLOSE")),"usable window retains bounded footer exit");
  check(contrast(g_fc_ink,g_fc_surface)>=4.5&&contrast(g_fc_muted,g_fc_surface)>=4.5,"text theme contrast meets 4.5 to 1 threshold");
  check(contrast(0xffffff,g_fc_accent)>=4.5,"active button uses readable white ink in both themes");
  if(g_fc_layout.usable)check(inside_name(name("FC_RESIZE"))&&ObjectGetInteger(0,name("FC_RESIZE"),OBJPROP_YDISTANCE)>=ObjectGetInteger(0,name("FC_CLOSE"),OBJPROP_YDISTANCE)+g_fc_layout.button,"usable window resize handle does not overlap footer actions");
  if(!g_fc_layout.usable){constrained++;check(ObjectFind(0,name("UNUSABLE"))>=0,"infeasible viewport is explicitly unavailable, never counted as functional success");continue;}
  usable++;bool reached[5]={false,false,false,false,false};bool date_seen=false,query_seen=false;
  for(int at=0;at<=g_fc_scroll_max;at++){
   g_fc_scroll=at;JPWNoCudaFiboUIDraw(P,v);
   for(int i=0;i<5;i++)reached[i]|=seen_value(v.projection_values[i]);
   date_seen|=ObjectFind(0,name("FC_DATE"))>=0;query_seen|=ObjectFind(0,name("FC_QUERY_DAY"))>=0;
   for(const auto&i:objects)if(StringFind(i.first,P+"FC_")==0&&i.first!=name("BACKGROUND")&&i.first!=name("HEADER"))
     check(inside(i.second),"rendered object is contained in window across font/DPI/theme/scroll");
  }
  for(bool ok:reached)check(ok,"every projection value reachable within same tab without being erased or truncated");
  check(date_seen&&query_seen,"date field and query action remain reachable in each feasible viewport");
 }
 std::cout<<"NOCUDA_FIBO_UI_RENDER: "<<checks-failures<<" PASS / "<<failures<<" FAIL; "<<cases<<" font/DPI/viewport/theme cases; "<<usable<<" feasible / "<<constrained<<" explicitly constrained; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''


def main():
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        print('ENVIRONMENT_ERROR: C++ compiler unavailable')
        return 2
    source = expanded_source(SOURCE)
    if re.search(r'\b(AccountInfo\w*|CopyRates|CopyBuffer|Database\w*|File\w*|Order\w*|Position\w*)\s*\(', source):
        print('PRODUCT_FAIL: presentation reaches account/history/study storage boundary')
        return 1
    bmp = LOGO.read_bytes()
    if bmp[:2] != b'BM' or struct.unpack_from('<ii', bmp, 18) != (180, 16) or struct.unpack_from('<H', bmp, 28)[0] != 24:
        print('PRODUCT_FAIL: logo resource is not the traced 24-bit 180x16 BMP')
        return 1
    source = re.sub(r'^#(?:if.*|endif.*|resource.*)\n', '', source, flags=re.M)
    source = re.sub(r'^#define\s+(JPW_NOCUDA_FIBO_UI_MQH|JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n', '', source, flags=re.M)
    source = re.sub(r"C'(\d+),(\d+),(\d+)'", lambda m: str(int(m[1]) | int(m[2]) << 8 | int(m[3]) << 16), source)
    source = source.replace('JPWNoCudaFiboUIItem sources[];', 'std::vector<JPWNoCudaFiboUIItem> sources;').replace('JPWNoCudaFiboUIItem records[];', 'std::vector<JPWNoCudaFiboUIItem> records;')
    source = source.replace('string g_fc_keep[],g_fc_actions[],g_fc_action_ids[];', 'std::vector<string> g_fc_keep,g_fc_actions,g_fc_action_ids;')
    source = source.replace('string f[];', 'std::vector<string> f;')
    with tempfile.TemporaryDirectory(prefix='jpw-nocuda-fibo-ui-') as folder:
        path = Path(folder)
        (path / 'ui.cpp').write_text(complete_design_shim(SHIM) + translate_arrays(source) + MAIN)
        compiled = subprocess.run([compiler, '-std=c++17', '-O1', str(path / 'ui.cpp'), '-o', str(path / 'ui')], text=True, capture_output=True)
        if compiled.returncode:
            print(compiled.stderr)
            return compiled.returncode
        result = subprocess.run([str(path / 'ui')], text=True, capture_output=True)
        print(result.stdout, end='')
        print(result.stderr, end='')
        print('SOURCE_SHA256:', hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        print('LOGO_SHA256:', hashlib.sha256(bmp).hexdigest())
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())

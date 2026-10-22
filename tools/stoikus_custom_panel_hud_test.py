#!/usr/bin/env python3
"""Actual HUD rendering/event callbacks on deterministic chart/text/ARGB seams.

Breaks caught: missing configured metrics, clipped values, duplicate access,
implicit preference writes, missing collapse restore, escaped geometry.
Native glyph rasterization/event dispatch still require MetaEditor/MT5.
"""
from pathlib import Path
import re
import subprocess
import tempfile
from leverage_geometry_test import HUD_SHIM
from leverage_host_shim import translate_arrays

ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'

def flatten(name,seen=None):
    if seen is None: seen=set()
    if name in seen or name=='JPW_UI_Focus.mqh': return ''
    seen.add(name)
    source=(INC/name).read_text()
    return re.sub(r'#include <JPWealth/([^>]+)>',lambda m:flatten(m[1],seen),source)

def code(main):
    shim='extern double scale;\n'+HUD_SHIM
    shim=shim.replace('width=(uint)StringLen(value)*glyph;', 'width=(uint)(StringLen(value)*glyph*scale);')
    shim=shim.replace('height=(uint)(measured_font*3/2>12?measured_font*3/2:12);', 'height=(uint)((measured_font*3/2>12?measured_font*3/2:12)*scale);')
    shim=shim.replace('bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}', 'bool ObjectCreate(int,const string&name,int kind,int,int,int){objects[name]=Object{};objects[name].number[-1]=kind;return true;}')
    seams=r'''
#include <cstdio>
#define JPW_COCKPIT_PREF_OBJECT "JPW_COCKPIT_PREF_V3"
#define JPW_COCKPIT_PREF_V2_OBJECT "JPW_COCKPIT_PREF_V2"
#define JPW_COCKPIT_PREF_LEGACY_OBJECT "JPW_COCKPIT_PREF_V1"
#define JPW_COCKPIT_ALL_VISIBLE 127
#define JPW_COCKPIT_PREF_VERSION 3
template<typename... A>string StringFormat(const string &f,A...args){char b[256];std::snprintf(b,sizeof(b),f.c_str(),args...);return b;}
int StringSplit(const string&s,int separator,std::vector<string>&out){out.clear();size_t start=0;for(size_t i=0;i<=s.size();i++)if(i==s.size()||s[i]==separator){out.push_back(s.substr(start,i-start));start=i+1;}return out.size();}
double MathFloor(double value){return std::floor(value);}
const int TERMINAL_KEYSTATE_SHIFT=1001;
long TerminalInfoInteger(int){return 0;}
int ObjectsTotal(int,int,int){return objects.size();}
string ObjectName(int,int i,int,int){auto at=objects.begin();std::advance(at,i);return at->first;}
int account_minimizes=0;
void JPWAccountMinimize(){account_minimizes++;g_raiz_details_open=false;}
bool JPWUIOwns(const string &owner){return central_owner==owner;}
bool JPWUIAcquire(const string &owner){central_owner=owner;return true;}
void JPWUIRelease(const string &owner){if(central_owner==owner)central_owner="";}
bool EventChartCustom(long,int,long,double,const string&){return true;}
ulong GetMicrosecondCount(){return clock_ms*1000+1;}
color JPWPanelInk(color){return 0xffffff;}
color JPWPanelBorderColor(color){return 0x777777;}
color JPWPanelAccentColor(color){return 0x2222ee;}
color JPWPanelMutedText(color){return 0xaaaaaa;}
int JPWUIDesignTextWidth(const string &s,int f){TextSetFont("Arial",-10*f,0);uint w=0,h=0;TextGetSize(s,w,h);return w;}
'''
    cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
    codec=cockpit[cockpit.index('void JPWCockpitDefault('):cockpit.index('bool JPWCockpitVisible(')]
    actions=(INC/'JPW_Alavancagem_Actions.mqh').read_text()
    owners=actions[actions.index('bool JPWCockpitOwnedSuffix('):actions.index('bool JPWCockpitSavePrefs(')]
    card_start=actions.index('   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)\n      if(sparam==JPWRaizUI("BUTTON_"')
    card_end=actions.index('   if(g_raiz_tab==JPW_ROUTE_STOPS)',card_start)
    card_route='string JPWRaizUI(const string &s){return g_panel_prefix+"RAIZ_UI_"+s;}\nint g_cockpit_selected=-1,card_route=-1; const int JPW_ACTION_CARD_FIRST=50,JPW_ROUTE_METRIC=8;\nvoid JPWRaizSwitchTab(int r){card_route=r;}\nvoid actual_card_route(const string &sparam){\n'+actions[card_start:card_end]+'}\n'
    return translate_arrays(shim+(ROOT/'tools/stoikus_hud_fixture/native.hpp').read_text()+seams+codec+flatten('JPW_Stoikus_HUD.mqh')+owners+card_route+main)

MAIN=r'''
void JPWRenderHUD(){JPWStoikusHUDRender();}
void click(const string &suffix){
 clock_ms+=500;int at=JPWStoikusHUDSlot(g_panel_prefix+suffix);assert(g_stoikus_surfaces[at].live);
 long x=g_stoikus_surfaces[at].x+g_stoikus_surfaces[at].w/2;double y=g_stoikus_surfaces[at].y+g_stoikus_surfaces[at].h/2;string route;
 assert(JPWStoikusHUDEvent(CHARTEVENT_OBJECT_CLICK,x,y,g_panel_prefix+suffix,route));
}
void bounded(){
 for(int i=0;i<g_stoikus_surface_count;i++)if(g_stoikus_surfaces[i].live){
  auto &s=g_stoikus_surfaces[i];assert(s.x>=0&&s.y>=0&&s.w>0&&s.h>0);
  assert(s.x+s.w<=chart_width&&s.y+s.h<=chart_height);
 }
}
int main(){
 JPWStoikusVisualLoad(); chart_width=1200;chart_height=1800;
 ObjectCreate(0,g_panel_prefix,OBJ_LABEL,0,0,0);
 ObjectCreate(0,"JPW_LEV_999_HUD_NOCUDA",OBJ_BUTTON,0,0,0);
 ObjectCreate(0,"JPW_LEV_999_CUST_UP_4",OBJ_BUTTON,0,0,0);
 ObjectCreate(0,"JPW_LEV_999_UNKNOWN_MANUAL",OBJ_LABEL,0,0,0);
 JPWCockpitRemoveForeignHUD(g_panel_prefix);
 if(objects.count("JPW_LEV_999_HUD_NOCUDA")||objects.count("JPW_LEV_999_CUST_UP_4")){
  std::cerr<<"FAIL restored known panel controls from previous chart left duplicated\n";return 1;
 }
 assert(objects.count("JPW_LEV_999_UNKNOWN_MANUAL"));
 for(auto &m:g_cockpit_snapshot.metric){m.value="2.75x";m.reason="fixture";m.quality=JPW_VIEW_CURRENT;}
 JPWStoikusHUDRender();
 if(!objects.count(g_panel_prefix)){std::cerr<<"FAIL empty suffix must not delete an unknown prefix-only object\n";return 1;}
 if(!objects.count(g_panel_prefix+"3")||!objects.count(g_panel_prefix+"4")){
  std::cerr<<"FAIL default new chart must expose configured Raiz N 1W and 2W alongside leverage and risk\n";return 1;
 }
 assert(!objects.count(JPW_STOIKUS_PANEL_PREF_OBJECT));
 assert(objects.count(g_panel_prefix+"HUD_NOCUDA")&&objects.count(g_panel_prefix+"HUD_PERSONALIZE"));
 for(int i=0;i<7;i++)for(const string &suffix:{string("_TITLE"),string("_DETAILS"),string("_VALUE"),string("_QUALITY"),string("_REASON"),string("_REASON2")}){
  g_cockpit_selected=-1;card_route=-1;actual_card_route(JPWRaizUI("CARD_"+IntegerToString(i)+suffix));
  if(g_cockpit_selected!=i || card_route!=JPW_ROUTE_METRIC){std::cerr<<"FAIL Conta card access not routed metric="<<i<<" suffix="<<suffix<<"\n";return 1;}
 }
 int corefail=0;
 for(int i:{0,5,3,4}){
  auto &a=g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+IntegerToString(i))];
  auto &b=g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+IntegerToString(i)+"_META")];
  if(a.h+b.h<JPWUIDesignPx(36)){std::cerr<<"FAIL canonical joined metric target below36 logical pixels\n";corefail++;}
 }
 risk_scope=string(300,'W');JPWStoikusHUDRender();
 if(objects[g_panel_prefix+"5"].text[OBJPROP_TOOLTIP].find(risk_scope)==string::npos){std::cerr<<"FAIL full risk scope missing from tooltip\n";corefail++;}
 risk_scope="EURUSD · Compra";JPWStoikusHUDRender();
 if(corefail)return 1;
 // Retained Conta spacing setting must continue to affect chart geometry.
 g_cockpit_prefs.density=0;JPWStoikusHUDRender();
 int compact_stride=g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"5")].y-g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"0")].y;
 g_cockpit_prefs.density=1;JPWStoikusHUDRender();
 int normal_stride=g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"5")].y-g_stoikus_surfaces[JPWStoikusHUDSlot(g_panel_prefix+"0")].y;
 if(normal_stride<=compact_stride){std::cerr<<"FAIL retained Normal spacing must exceed Compact spacing\n";return 1;}
 g_cockpit_prefs.density=0;JPWStoikusHUDRender();
 bounded();int before=resource_writes;JPWStoikusHUDRender();assert(resource_writes==before);
 click("HUD_PERSONALIZE");assert(g_stoikus_panel_editor);assert(!objects.count(JPW_STOIKUS_PANEL_PREF_OBJECT));
 int top=JPWStoikusHUDSlot(g_panel_prefix+"CUST_APPLY");auto bounds=g_stoikus_surfaces[top];
 JPWStoikusHUDSurfacePaint("6",bounds.x,bounds.y,bounds.w,bounds.h,"Behind","",10,0xffffff,0,100,"fixture",3);
 if(JPWStoikusHUDHit(bounds.x+3,bounds.y+3)!=g_panel_prefix+"CUST_APPLY"){
  std::cerr<<"FAIL late-painted chart metric must not steal clicks from higher editor controls\n";return 1;
 }
 JPWStoikusHUDRender();
 int original=g_stoikus_panel_prefs.visible_mask;click("CUST_TOGGLE_1");assert(g_stoikus_panel_draft.visible_mask==(original^2));
 click("CUST_CANCEL");assert(!g_stoikus_panel_editor&&g_stoikus_panel_prefs.visible_mask==original);assert(!objects.count(JPW_STOIKUS_PANEL_PREF_OBJECT));
 click("HUD_PERSONALIZE");click("CUST_UP_3");assert(g_stoikus_panel_draft.order[1]==3);
 click("CUST_APPLY");assert(!g_stoikus_panel_editor&&g_stoikus_panel_prefs.order[1]==3);
 string saved=ObjectGetString(0,JPW_STOIKUS_PANEL_PREF_OBJECT,OBJPROP_TEXT);assert(saved=="V1|57|0354126");
 JPWStoikusPanelLoad();assert(JPWStoikusPanelPrefsEncode(g_stoikus_panel_prefs)==saved);
 click("HUD_PERSONALIZE");for(int i:{0,5,3,4})click("CUST_TOGGLE_"+IntegerToString(i));click("CUST_APPLY");
 assert(g_stoikus_panel_prefs.visible_mask==0);for(int i=0;i<7;i++)assert(!objects.count(g_panel_prefix+IntegerToString(i)));
 assert(objects.count(g_panel_prefix+"HUD_PERSONALIZE")&&objects.count(g_panel_prefix+"RAIZ_DETAILS_BUTTON"));
 click("HUD_PERSONALIZE");for(int i=0;i<7;i++)click("CUST_TOGGLE_"+IntegerToString(i));click("CUST_APPLY");
 assert(g_stoikus_panel_prefs.visible_mask==127);
 for(int opacity:{0,30,100}){
  g_stoikus_visual.transparency=opacity;JPWStoikusHUDRender();bounded();
  auto bg=resources.at(JPWStoikusHUDResource(g_panel_prefix+"HUD_BG"));assert((bg.at(bg.size()/2)>>24)==uint(JPWStoikusAlpha(opacity)));
  auto metric=resources.at(JPWStoikusHUDResource(g_panel_prefix+"0"));bool has_ink=false;
  for(auto pixel:metric){assert((pixel>>24)==0||(pixel>>24)==255);has_ink|=(pixel>>24)==255;}assert(has_ink);
 }
 // Restore must remain reachable after a moved chart becomes smaller.
 g_stoikus_visual.positioned=true;g_stoikus_visual.x=900;g_stoikus_visual.y=100;JPWStoikusHUDRender();click("HUD_MIN");
 chart_width=320;chart_height=500;JPWStoikusHUDRender();bounded();assert(objects.count(g_panel_prefix+"HUD_RESTORE"));
 click("HUD_RESTORE");bounded();assert(!g_stoikus_visual.collapsed);
 // Independent feasible viewport: the product cannot justify hiding metrics by choosing Restore.
 for(double dpi:{1.,1.25,1.5,2.})for(int f:{8,10,16,24,40}){
  scale=dpi;InpFontSize=f;chart_width=1920;chart_height=8000;g_stoikus_visual.collapsed=false;g_stoikus_visual.positioned=false;
  bool seen[7]={false,false,false,false,false,false,false};
  for(int page=0;page<7;page++){
   g_stoikus_metric_page=page;JPWStoikusHUDRender();bounded();
   assert(!objects.count(g_panel_prefix+"HUD_RESTORE"));
   for(int i=0;i<7;i++)if(objects.count(g_panel_prefix+IntegerToString(i)))seen[i]=true;
  }
  for(bool present:seen)assert(present);
 }
 // Every selected metric remains available via pages at unchanged font.
 for(double dpi:{1.,1.25,1.5,2.})for(int f:{8,10,20,40})for(int w:{240,640,1280}){
  scale=dpi;InpFontSize=f;chart_width=w;chart_height=1200;
  g_stoikus_visual.collapsed=false;g_stoikus_visual.positioned=false;JPWStoikusHUDRender();bounded();
  if(objects.count(g_panel_prefix+"HUD_RESTORE"))continue;
  bool seen[7]={false,false,false,false,false,false,false};
  for(int page=0;page<7;page++){
   g_stoikus_metric_page=page;JPWStoikusHUDRender();bounded();
   for(int i=0;i<7;i++)if(objects.count(g_panel_prefix+IntegerToString(i)))seen[i]=true;
  }
  for(int metric=0;metric<7;metric++)if(!seen[metric]){
   std::cerr<<"FAIL selected metric missing dpi="<<dpi<<" font="<<f<<" chart="<<w<<" metric="<<metric<<"\n";return 1;
  }
 }
 scale=1.;InpFontSize=10;chart_width=1280;chart_height=1800;g_stoikus_metric_page=0;
 g_cockpit_snapshot.metric[5].value="99999999999999999999,99 USC · 15,16% saldo";JPWStoikusHUDRender();bounded();
 int financial=JPWStoikusHUDSlot(g_panel_prefix+"5");assert(g_stoikus_surfaces[financial].key.find("99999999999999999999,99 USC · 15,16% saldo")!=string::npos);
 // Automatic lower-corner placement reserves the chart heading; manual drag remains free.
 scale=2.;InpFontSize=16;chart_width=1600;chart_height=1200;g_stoikus_visual.positioned=false;g_stoikus_visual.width=280;
 for(int corner:{CORNER_LEFT_LOWER,CORNER_RIGHT_LOWER})for(int offset:{220,2000}){
  g_cockpit_prefs.corner=corner;InpOffsetY=offset;JPWStoikusHUDRender();
  if(g_stoikus_hud.y<MathMin(JPWUIDesignPx(44),chart_height-g_stoikus_hud.height)){
   std::cerr<<"FAIL automatic lower corner intrudes chart heading\n";return 1;
  }
 }
 g_stoikus_visual.positioned=true;g_stoikus_visual.y=0;JPWStoikusHUDRender();assert(g_stoikus_hud.y==0);
 scale=1.;InpFontSize=10;chart_width=1280;chart_height=1800;g_stoikus_visual.positioned=false;g_cockpit_prefs.corner=CORNER_LEFT_UPPER;InpOffsetY=10;
 // A transient fit hint must disappear once the complete value fits again.
 chart_width=240;g_stoikus_visual.width=240;g_stoikus_panel_notice="";
 g_cockpit_snapshot.metric[5].value=string(200,'9')+" USD";JPWStoikusHUDRender();
 g_cockpit_snapshot.metric[5].value="12.50 USD";JPWStoikusHUDRender();
 if(objects[g_panel_prefix+"HUD_NOTICE"].text[OBJPROP_TOOLTIP].find("Valor integral disponível")!=string::npos){
  std::cerr<<"FAIL obsolete value fit hint survives a now legible quote\n";return 1;
 }
 g_stoikus_panel_notice="Erro ao salvar; confira o modelo";JPWStoikusHUDRender();
 assert(objects[g_panel_prefix+"HUD_NOTICE"].text[OBJPROP_TOOLTIP].find(g_stoikus_panel_notice)!=string::npos);
 g_stoikus_panel_notice="";chart_width=1280;g_stoikus_visual.width=280;JPWStoikusHUDRender();
 // Opening absent NoCuda is informational and never attaches/arms a program.
 click("HUD_NOCUDA");assert(g_stoikus_panel_notice.find("JPW_NoCuda_Channels")!=string::npos);
 if(g_stoikus_panel_notice.find("Navegador")==string::npos || g_stoikus_panel_notice.find("Ctrl+N")==string::npos || g_stoikus_panel_notice.find("arraste")==string::npos){std::cerr<<"FAIL absent NoCuda guidance must explain attaching from Navigator, not only list installed indicators\n";return 1;}
 // Keyboard acts on editor only, and Esc preserves the last applied bytes.
 click("HUD_PERSONALIZE");long escape=27;double zero=0;string route;
 assert(JPWStoikusHUDEvent(CHARTEVENT_KEYDOWN,escape,zero,"",route));assert(!g_stoikus_panel_editor);
 ObjectCreate(0,"FOREIGN_DRAWING",OBJ_LABEL,0,0,0);
 std::vector<string> owned_names;for(int i=0;i<g_stoikus_surface_count;i++)if(g_stoikus_surfaces[i].name!="")owned_names.push_back(g_stoikus_surfaces[i].name);
 JPWStoikusHUDCleanup();
 for(const string &name:owned_names){assert(!objects.count(name));assert(!resources.count(JPWStoikusHUDResource(name)));}
 assert(objects.count("FOREIGN_DRAWING")&&objects.count(g_panel_prefix)&&objects.count(JPW_STOIKUS_PANEL_PREF_OBJECT));
 std::cout<<"PASS customizable HUD: actual events, choices/order/apply/cancel/reload/empty/pages/DPI/ARGB/restore/cleanup; native NOT_RUN\n";
}
'''

def run(main=MAIN):
    with tempfile.TemporaryDirectory(prefix='stoikus-custom-hud-') as temp:
        source=Path(temp)/'test.cpp';source.write_text(code(main))
        subprocess.run(['clang++','-std=c++17','-O2','-Wno-deprecated-declarations',str(source),'-o',temp+'/test'],check=True)
        return subprocess.run([temp+'/test']).returncode

if __name__=='__main__':raise SystemExit(run())

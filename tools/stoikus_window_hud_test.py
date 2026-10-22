#!/usr/bin/env python3
"""Compiles actual production visual algorithms with native string/math seams only."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
def run():
 source=(INC/'JPW_Stoikus_Visual.mqh').read_text()
 shim=r'''#include <string>
#include <vector>
#include <cmath>
#include <cassert>
#include <iostream>
using string=std::string; using ushort=unsigned short;
int StringLen(string s){return s.size();} ushort StringGetCharacter(string s,int i){return s.at(i);}
string StringSubstr(string s,int a,int n=-1){return s.substr(a,n<0?string::npos:n);}
int StringFind(string s,string p,int a=0){auto x=s.find(p,a);return x==string::npos?-1:x;}
string IntegerToString(int i){return std::to_string(i);} long StringToInteger(string s){try{return std::stol(s);}catch(...){return 0;}}
int MathMin(int a,int b){return std::min(a,b);} int MathMax(int a,int b){return std::max(a,b);}
double MathRound(double a){return std::round(a);}
'''
 main=r'''int main(){
 JPWStoikusVisual p; JPWStoikusVisualDefault(p); assert(p.mode==0&&p.transparency==30&&p.width==280);
 string e=JPWStoikusVisualEncode(p); JPWStoikusVisual q; assert(JPWStoikusVisualDecode(e,q)); assert(JPWStoikusVisualEncode(q)==e);
 assert(!JPWStoikusVisualDecode(e+"|0",q));assert(!JPWStoikusVisualDecode("",q)); assert(!JPWStoikusVisualDecode("V1|x",q));
 assert(JPWStoikusAlpha(0)==255&&JPWStoikusAlpha(30)==179&&JPWStoikusAlpha(100)==0);
 for(int mask: {0,1,32,127}) for(int mode=0;mode<2;mode++) for(int i=0;i<7;i++)
 assert(JPWStoikusMetricVisible(mode,mask,i)==(((mask&(1<<i))!=0)&&(mode==1||i==0||i==5)));
 for(double scale: {1.,1.25,1.5,2.}) for(int cw: {60,240,800,1920}) {
 int w=JPWStoikusHUDWidth(cw,280,180,scale);assert(w<=cw&&w<=int(480*scale+.5));
 assert(JPWStoikusClamp(100000,0,cw-w)==cw-w);
 }
 p.account_positioned=true;p.account_x=23;p.account_y=45;p.account_width=720;p.account_height=560;p.account_minimized=true;
 assert(JPWStoikusVisualDecode(JPWStoikusVisualEncode(p),q));assert(q.account_minimized&&q.account_x==23);
 p.transparency=101;assert(JPWStoikusVisualEncode(p)=="");
 std::cout<<"PASS production visual codec/alpha/geometry/masks; native NOT_RUN\n";
}'''
 with tempfile.TemporaryDirectory(prefix='stoikus-hud-') as t:
  cpp=Path(t)/'test.cpp';cpp.write_text(shim+source+main)
  subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror',str(cpp),'-o',t+'/test'],check=True)
  subprocess.run([t+'/test'],check=True)
if __name__=='__main__':run()

def runtime():
 import sys,re
 sys.path.insert(0,str(ROOT/'tools'))
 from leverage_geometry_test import HUD_SHIM
 from leverage_host_shim import translate_arrays
 from leverage_panel_test import body_of
 shim=HUD_SHIM
 shim='extern double scale;\n'+shim
 shim=shim.replace('width=(uint)StringLen(value)*glyph;', 'width=(uint)(StringLen(value)*glyph*scale);')
 shim=shim.replace('height=(uint)(measured_font*3/2>12?measured_font*3/2:12);', 'height=(uint)((measured_font*3/2>12?measured_font*3/2:12)*scale);')
 shim=shim.replace('bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}','bool ObjectCreate(int,const string&name,int kind,int,int,int){objects[name]=Object{};objects[name].number[-1]=kind;return true;}')
 fixture=ROOT/'tools/stoikus_hud_fixture'
 reservation='bool JPWNoCudaUICockpitHUD(const int cw,const int ch,JPWNoCudaUIRect &hud)'
 reservation += '{'+body_of((INC/'JPW_NoCuda_UI.mqh').read_text(),reservation)+'}'
 accept='bool JPWCockpitAcceptChartEvent(const int id,const long &lparam,\n                                const double &dparam,const string &object_name)'
 accept += '{'+body_of((INC/'JPW_Alavancagem_Presentation.mqh').read_text(),accept)+'}'
 wrapper='void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)'
 wrapper += '{'+body_of((ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5').read_text(),wrapper)+'}'
 # Include the real new Account gesture boundary before replaying the wrapper.
 # Only external account rendering/field capture is a synthetic observable seam.
 account=(INC/'JPW_Alavancagem_Actions.mqh').read_text()
 presentation=(INC/'JPW_Alavancagem_Presentation.mqh').read_text()
 boundary=(INC/'JPW_Stoikus_Window.mqh').read_text()+r'''
JPWStoikusWindowGesture g_account_window_gesture;JPWPanelRect g_account_window_rect,g_details_rect;
int g_details_control=36,g_details_pad=8,account_captures=0,account_destroys=0,account_redraws=0;
bool g_jpw_focus_suspended=false;
void JPWRaizSaveVisibleFields(){account_captures++;}void JPWRaizPanelDestroy(){account_destroys++;}
void JPWInvalidateDialogContent(int=-1){}void JPWRenderRaizDetails(){account_redraws++;}
'''
 boundary+=re.search(r'const int JPW_ACTION_MINIMIZE=\d+;',presentation).group(0)+'\n'
 for source,signature in [(presentation,'string JPWRaizUI(const string suffix)'),(presentation,'string JPWActionObject(const int action)'),(account,'void JPWAccountMinimize()'),(account,'bool JPWAccountWindowEvent(const int id,const long &lp,const double &dp,const string &sp)')]:
  boundary+=signature+'{'+body_of(source,signature)+'}\n'
 from stoikus_window_host import production
 panel=(INC/'JPW_Alavancagem_Panel.mqh').read_text()
 ink=''
 for signature in ('bool JPWPanelDarkBackground(const color background)','color JPWPanelInk(const color background)'):
  ink+=signature+'{'+body_of(panel,signature)+'}\n'
 ink=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),ink)
 code=shim+"\n#define JPW_HUD_PANEL_NATIVE\n"+(fixture/'native.hpp').read_text()+(INC/'JPW_UI_Focus.mqh').read_text()+ink+production()+boundary+reservation+accept+wrapper+(fixture/'main.cpp').read_text()
 with tempfile.TemporaryDirectory(prefix='stoikus-runtime-') as t:
  cpp=Path(t)/'test.cpp';cpp.write_text(translate_arrays(code))
  subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Wno-unused-const-variable',str(cpp),'-o',t+'/test'],check=True)
  subprocess.run([t+'/test'],check=True)
if __name__=='__main__':runtime()

#!/usr/bin/env python3
"""Task2 presentation-only production helper replay; native MT5 NOT_RUN."""
import pathlib, re, subprocess, tempfile
from leverage_panel_test import body_of
ROOT=pathlib.Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
panel=(INC/'JPW_Alavancagem_Panel.mqh').read_text()
panel=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),panel)
cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
try:
    helper='int JPWCockpitPresentationIndex(const int slot){'+body_of(cockpit,'int JPWCockpitPresentationIndex(')+'}'
except ValueError:
    raise AssertionError('presentation index map must exist before layout can preserve actions')
presentation=(INC/'JPW_Alavancagem_Presentation.mqh').read_text()
actions=(INC/'JPW_Alavancagem_Actions.mqh').read_text()
nav_start=actions.index('   if(sparam==JPWActionObject(JPW_ACTION_SECTIONS))')
nav_end=actions.index('   if(JPWSignalHandleClick(sparam))',nav_start)
nav=actions[nav_start:nav_end]
# The exact production menu event branch runs with chart primitives as seams.
nav_runtime="""
using string=std::string;
const int JPW_ACTION_SECTIONS=160,JPW_ACTION_PREVIOUS=38,JPW_ACTION_NEXT=39;
bool g_cockpit_sections_open=false;int g_cockpit_section_page=0,g_cockpit_page=4,invalidates=0,draws=0;
string JPWActionObject(int n){return std::to_string(n);}
void JPWInvalidateDialogContent(){invalidates++;}
void JPWRenderRaizDetails(){draws++;}
void MenuEvent(const string sparam){
"""+nav+"}\n"
# Original action IDs and canonical qualities remain fixed; display translations are separate.
assert 'JPW_ACTION_TAB_FIRST=40' in cockpit and 'JPW_ACTION_TAB_HISTORY=120' in cockpit
assert 'return("Current")' in body_of(cockpit,'string JPWCockpitQualityText(')
assert 'JPWPersonalUIReady()' in body_of(presentation,'void JPWPersonalRenderBody(')
assert 'não demonstra isolamento exclusivo de tese' in presentation
assert 'Denominador: saldo da amostra' in presentation
monitor=r"""
#include <vector>
using ulong=unsigned long;
const int JPW_MONITOR_PREPARING=1;
struct JPWMonitorModuleStatus{int state=1,progress=45;string quality="Current",reason="captura pendente";long observed_utc=1,observed_mono_ms=1;};
string JPWMonitorUIStage(JPWMonitorModuleStatus&,bool,ulong){return "Em preparação";}
string JPWMonitorUIGuidance(JPWMonitorModuleStatus&,bool,bool){return "Aguardar captura";}
string JPWMonitorUITime(long,long,ulong){return "hora confirmada";}
string IntegerToString(int n){return std::to_string(n);}
void JPWDetailsWrap(const string text,int,std::vector<string>&lines){lines.push_back(text);}
void JPWMonitorAppendModule(const string label,JPWMonitorModuleStatus &module,const bool present,const ulong now_ms,const int inner,std::vector<string>&lines,const bool accounting=false,const bool technical=false){
"""+body_of(presentation,'void JPWMonitorAppendModule(')+"}\n"
cpp='''#include <cmath>
#include <algorithm>
#include <iostream>
using color=int;
'''+panel+helper+nav_runtime+monitor+'''
int main(){
JPWMonitorModuleStatus module;std::vector<string> lines;
JPWMonitorAppendModule("Monitor",module,true,100,400,lines);
if(lines.size()!=4||lines[0].find("Em preparação")==string::npos||lines[1].find("Motivo:")!=0||lines[2].find("Ação:")!=0)return 9;
JPWMonitorAppendModule("Monitor",module,true,100,400,lines,false,true);
if(lines.back().find("qualidade literal Current")==string::npos)return 10;
MenuEvent(JPWActionObject(JPW_ACTION_SECTIONS));if(!g_cockpit_sections_open||g_cockpit_page!=4)return 6;
MenuEvent(JPWActionObject(JPW_ACTION_NEXT));if(g_cockpit_section_page!=1||g_cockpit_page!=4)return 7;
MenuEvent(JPWActionObject(JPW_ACTION_SECTIONS));if(g_cockpit_sections_open||g_cockpit_page!=4)return 8;
for(int dpi:{96,120,144,192})for(int w:{320,640,900,1600})for(int h:{240,600,1000}){
 JPWPanelRect r;double scale=dpi/96.0;
 if(!JPWPanelAccount(w,h,scale,r))return 1;
 if(r.width>int(w*.85)||r.height>int(h*.85)||r.width>int(std::round(720*scale))||r.height>int(std::round(560*scale)))return 2;
 if(r.x<0||r.y<0||r.x+r.width>w||r.y+r.height>h)return 3;
}
int expected[7]={0,5,1,2,3,4,6};
for(int i=0;i<7;i++)if(JPWCockpitPresentationIndex(i)!=expected[i])return 4;
if(JPWCockpitPresentationIndex(-1)!=-1||JPWCockpitPresentationIndex(7)!=-1)return 5;
std::cout<<"TASK2_HELPERS_PASS geometry48/DPI/map7/menu-cancel/scope/monitor-order; native NOT_RUN\\n";
}
'''
with tempfile.TemporaryDirectory(prefix='stoikus-account-ui-') as d:
 p=pathlib.Path(d);(p/'case.cpp').write_text(cpp)
 subprocess.run(['clang++','-std=c++17',str(p/'case.cpp'),'-o',str(p/'case')],check=True)
 subprocess.run([str(p/'case')],check=True)

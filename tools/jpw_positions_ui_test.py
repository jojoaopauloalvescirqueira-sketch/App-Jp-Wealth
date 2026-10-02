#!/usr/bin/env python3
"""Replay the production positions renderer using keyed synthetic chart objects.

Native MetaEditor, fonts, clipping, clicks and templates remain NOT_RUN. Source
functions are extracted unchanged; only the MT5 object/text/clock boundary is
substituted. In particular two creates with one name really overwrite geometry.
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile
import sys
import tarfile
from leverage_panel_test import body_of
from leverage_geometry_test import HUD_SHIM
from leverage_source import expanded_source

ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
PRESENT=INC/'JPW_Alavancagem_Presentation.mqh'

SHIM=r'''
#include <vector>
#include <cmath>
#include <cstdio>
#include <sstream>
#include <iomanip>
#include <type_traits>
using ulong=unsigned long;
using datetime=long;
constexpr int JPW_SIGNAL_ROUTE=16,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2;
constexpr int POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1,JPW_STOP_RISK_POSITION=1,JPW_STOP_RISK_PENDING=2;
constexpr int OBJPROP_STATE=19,TIME_DATE=1,TIME_SECONDS=2;
constexpr int OBJ_BITMAP_LABEL=5,OBJPROP_BMPFILE=20,TERMINAL_SCREEN_DPI=1;
int InpCockpitFontSize=16,g_details_font=16,g_details_pad=16,g_details_line=48,g_details_control=64;
int text_override=32,dpi=150;
long TerminalInfoInteger(int){return dpi*96/100;}
bool TextSetFont(const string&face,int size){return TextSetFont(face,size,FW_NORMAL);}
int g_cockpit_selected=0,g_cockpit_page=0,g_focus_action=-1,g_focus_count=0,g_focus_actions[128];

double g_factor_draft=1.5;
bool g_cockpit_pref_invalid=false,g_raiz_panel_built=false;string g_cockpit_pref_notice;
JPWPanelRect g_details_rect;
color g_details_text,g_details_surface,g_details_chrome,g_details_card,g_details_border;
string _Symbol="SYNTHETIC.H1",g_sample_context="metric-hash",g_diagnostic_context="account-hash";
bool g_positions_operation_only=false,g_stops_show_pending=false;
int g_positions_scroll=0,g_positions_visible_rows=0,g_positions_total_rows=0,g_stop_button_count=0;
int g_position_button_row[16],g_stop_button_row[16];
ulong g_position_button_ticket[16];long g_position_button_identifier[16];
string g_stop_button_role[16];
long g_stop_genesis_identifier=0;bool g_stop_genesis_closed=false;
bool g_stop_scope_valid=false;string g_stop_scope_symbol="";int g_stop_scope_side=0;
bool g_stop_ready=false,g_stop_last_ready=false;
JPWStopRiskSample g_stop_sample,g_stop_last_sample;
std::vector<JPWStopRiskRow> g_stop_rows,g_stop_last_rows;
std::vector<JPWPositionView> g_position_views;
JPWPositionsView g_positions_view;
ulong clock_ms=1000;
ulong GetTickCount64(){return clock_ms;}
bool JPWPositionsViewCurrent(const string context,const ulong now);
template<class T>int ArraySize(const std::vector<T>&a){return (int)a.size();}
template<class T>int ArrayResize(std::vector<T>&a,int n){a.resize(n);return n;}
bool MathIsValidNumber(double v){return std::isfinite(v);}
bool JPWFinitePositive(double v){return std::isfinite(v)&&v>0;}
int StringCompare(const string&a,const string&b){return a==b?0:a<b?-1:1;}
int StringLen(const string&s){int n=0;for(unsigned char c:s)if((c&0xc0)!=0x80)n++;return n;}
string StringSubstr(const string&s,int from,int count){return s.substr(from,count);}
int StringFind(const string&s,const string&n){auto i=s.find(n);return i==string::npos?-1:(int)i;}
int StringReplace(string&s,const string&a,const string&b){int n=0;size_t at=0;while((at=s.find(a,at))!=string::npos){s.replace(at,a.size(),b);at+=b.size();n++;}return n;}
template<class T>string StringFormat(const char*fmt,T value){if(string(fmt)=="%I64u")return std::to_string((ulong)value);char out[128];std::snprintf(out,sizeof(out),fmt,value);return out;}
string DoubleToString(double v,int digits){std::ostringstream o;o<<std::fixed<<std::setprecision(digits)<<v;return o.str();}
string JPWFormatPercent(double v,bool){return DoubleToString(v,2)+"%";}
void ChartRedraw(int){}
void JPWSignalRenderBody(int,int,int,int,int){}
string TimeToString(long,int){return "synthetic time";}
'''

MAIN=r'''
int checks=0,failures=0;
void check(bool ok,const string&what){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<what<<'\n';}}
string text(const string&suffix){auto i=objects.find(JPWRaizUI(suffix));return i==objects.end()?"":i->second.text[OBJPROP_TEXT];}
void reset(int count=10){
 g_positions_view.catalog_valid=true;g_positions_view.context_key=g_sample_context;g_positions_view.account_key=g_diagnostic_context;g_positions_view.margin_mode=2;
 g_positions_view.sample_id=1;g_positions_view.accepted_monotonic_ms=1000;g_positions_view.quality=1;g_positions_view.valid_until_monotonic_ms=31000;clock_ms=1000;g_positions_operation_only=false;
 g_stop_button_count=0;g_stops_show_pending=false;g_stop_ready=false;g_stop_last_ready=false;g_stop_scope_valid=false;
 g_stop_genesis_identifier=0;g_stop_genesis_closed=false;g_positions_scroll=0;g_position_views.clear();
 for(int i=0;i<count;i++){JPWPositionView r{};r.ticket=12345678+i;r.identifier=100+i;r.symbol="NZDUSD.m";
  r.direction=0;r.volume=.08;r.volume_digits=2;r.opened_msc=1000+i;r.leverage=.275;r.leverage_valid=true;
  r.quality=1;r.entry=.57;r.sl=.55;r.entry_valid=true;r.sl_valid=true;g_position_views.push_back(r);}
}
void draw(int width=1198,int height=938,int font=16,int scale=150,int override_text=32){
 chart_width=width;chart_height=height;InpCockpitFontSize=font;dpi=scale;text_override=override_text;
 g_raiz_tab=JPW_ROUTE_STOPS;g_focus_count=0;objects.clear();RenderStopsWindow();
}
bool inside(const Object&o){auto p=o.number;return p[OBJPROP_XDISTANCE]>=g_details_rect.x&&
 p[OBJPROP_YDISTANCE]>=g_details_rect.y&&p[OBJPROP_XDISTANCE]+p[OBJPROP_XSIZE]<=g_details_rect.x+g_details_rect.width&&
 p[OBJPROP_YDISTANCE]+p[OBJPROP_YSIZE]<=g_details_rect.y+g_details_rect.height;}
int main(){
 reset();draw();
 check(g_stop_button_count==10,"reported 32px text / 1040x760 cockpit displays all ten positions in one tab");
 check(text("BUTTON_45")=="×"&&text("BUTTON_37")=="Fechar","keyed object map preserves two distinct close controls");
 check(objects[JPWActionObject(45)].number[OBJPROP_YDISTANCE]<objects[JPWActionObject(37)].number[OBJPROP_YDISTANCE],"header close is not moved into footer");
 check(inside(objects[JPWActionObject(45)])&&inside(objects[JPWActionObject(37)]),"both close controls remain inside cockpit");
 for(const auto&item:objects){
  if(item.first.find("POSITION_CELL_")==string::npos)continue;
  uint width=0,height=0;TextGetSize(item.second.text.at(OBJPROP_TEXT),width,height);
  const auto&pos=item.second.number;
  check(pos.at(OBJPROP_XDISTANCE)+width<=g_details_rect.x+g_details_rect.width-g_details_pad&&
        pos.at(OBJPROP_YDISTANCE)+height<=objects[JPWActionObject(37)].number[OBJPROP_YDISTANCE]-g_details_line,
        "rendered financial cell fits table content before pinned footer");
 }
 for(int i=0;i<10;i++){check(text("POSITION_CELL_"+IntegerToString(i)+"_1")==std::to_string(12345678+i),"ticket visible for every row");
  check(text("POSITION_CELL_"+IntegerToString(i)+"_2")=="0.08","remaining step precision visible");
  check(text("POSITION_CELL_"+IntegerToString(i)+"_3")=="0,28x","individual leverage visible even without EA");}
 check(g_cockpit_page==0&&g_positions_total_rows==10,"positions never turn the cockpit page");
 reset(1);g_position_views[0].quality=2;g_positions_view.quality=2;draw();
 check(text("POSITION_CELL_0_3")=="≈0,28x"&&text("POSITIONS_SUMMARY").find("Estimated")!=string::npos,"estimated leverage is explicit in the visible table");
 reset(80);draw();
 check(g_positions_total_rows==80&&g_stop_button_count<=16,"long catalogue uses bounded within-tab viewport");
 g_positions_scroll=10000;draw();
 check(g_positions_scroll==80-g_positions_visible_rows,"scroll clamps at last row");
 check(g_position_button_ticket[g_stop_button_count-1]==12345678+79,"last item reachable without page switching");
 reset(3);g_position_views[0].ticket=18446744073709551610UL;g_position_views[0].volume=.00001;g_position_views[0].volume_digits=5;
 g_position_views[0].leverage=.000001;draw();
 bool full_ticket=false,tiny_volume=false,tiny_leverage=false;
 for(const auto&o:objects){const string t=o.second.text.count(OBJPROP_TEXT)?o.second.text.at(OBJPROP_TEXT):"";
  full_ticket|=t.find("18446744073709551610")!=string::npos;tiny_volume|=t.find("0.00001")!=string::npos;tiny_leverage|=t.find("<0,01x")!=string::npos;}
 check(full_ticket&&tiny_volume&&tiny_leverage,"long tickets and small nonzero values retain full content");
 reset(3);g_position_views[1].symbol="EURUSD";g_stop_scope_valid=true;g_stop_scope_symbol="NZDUSD.m";g_stop_scope_side=1;
 g_positions_operation_only=true;draw(); // draw does not reset scope
 check(g_positions_total_rows==2,"operation filter does not expand to a different symbol");
 reset(1);g_stop_ready=true;g_stop_sample.account_key=g_diagnostic_context;g_stop_sample.balance=100;
 JPWStopRiskRow risk{};risk.kind=1;risk.ticket=g_position_views[0].ticket;risk.identifier=100;risk.symbol="NZDUSD.m";
 risk.side=1;risk.volume=.08;risk.entry=.57;risk.sl=.55;risk.valid=1;risk.risk_money=2;g_stop_rows={risk};
 g_stop_sample.currency="USD";draw();check(text("POSITION_CELL_0_4")=="2,00 USD","distinct account / presentation hashes accept compatible risk overlay");
 g_stop_rows[0].valid=0;g_stop_rows[0].reason="Sem SL válido";draw();
 string risk_amount,risk_pct,risk_state,risk_reason;
 JPWPositionRiskView(g_position_views[0],risk_amount,risk_pct,risk_state,risk_reason);
 check(risk_amount=="N/A"&&risk_state=="N/A","current EA presence does not mark invalid per-position risk Current");
 g_stop_rows[0].valid=1;g_stop_rows[0].reason="";
 g_stop_ready=false;g_stop_last_ready=true;g_stop_last_sample=g_stop_sample;g_stop_last_rows=g_stop_rows;draw();
 check(text("POSITIONS_SUMMARY").find("LAST · NOT ACTIVE")!=string::npos,"historical overlay stays explicitly inactive");
 g_position_views[0].sl=.54;draw();check(text("POSITION_CELL_0_4")=="N/A","SL change refuses stale overlay");
 clock_ms=31001;objects.clear();RenderStopsWindow();check(g_stop_button_count==0&&text("POSITIONS_EMPTY").find("N/A")!=string::npos,"redraw after expiry cannot show an active stale row");
 reset();g_position_views[0].symbol="ZZZ";g_position_views[9].symbol="AAA";draw();
 check(g_position_button_ticket[0]==12345687,"table groups exact symbols before chronological comparison");
 reset(2);g_stop_scope_valid=true;g_stop_scope_symbol="NZDUSD.m";g_stop_scope_side=1;g_position_views[1].opened_msc=g_position_views[0].opened_msc;
 check(JPWPositionRole(g_position_views[0]).find("empate")!=string::npos,"equal timestamps do not certify a Defence role");
 int cases=0;
 for(int font:{9,11,16,24})for(int scale:{100,125,150,200})for(int width:{320,390,1198})for(int corner:{0,1,2,3}){
  g_cockpit_prefs.corner=corner;
  reset(12);draw(width,938,font,scale,0);cases++;
  check(inside(objects[JPWActionObject(45)])||text("BUTTON_37")=="×","close accessible across measured fonts / DPI / narrow charts");
  check(g_stop_button_count>0,"at least one current position reachable in every feasible constrained chart");
  for(int j=0;j<g_stop_button_count;j++)check(g_position_button_ticket[j]!=0,"rendered row has immutable click identity");
 }
 std::cout<<"POSITIONS_UI_RENDER: "<<checks-failures<<" PASS / "<<failures<<" FAIL; "<<cases<<" font/DPI/viewports; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''

def main():
 compiler=shutil.which('clang++') or shutil.which('g++')
 if not compiler: print('ENVIRONMENT_ERROR: C++ compiler unavailable'); return 2
 source=PRESENT.read_text()
 brand=expanded_source(INC/'JPW_Genetrix_Brand.mqh')
 brand=re.sub(r'^#(?:if.*|endif.*|resource.*)\n','',brand,flags=re.MULTILINE)
 brand=re.sub(r'^#define\s+(JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n','',brand,flags=re.MULTILINE)
 # MQL concatenates string literals/macros directly. Preserve the production
 # values as host strings so C++ exercises the same header instead of a stub.
 brand=re.sub(r'^#define (JPW_PRODUCT_NAME|JPW_PRODUCT_TAGLINE) ("[^"\n]*")$',
              r'const string \1=\2;',brand,flags=re.MULTILINE)
 panel=(INC/'JPW_Alavancagem_Panel.mqh').read_text()
 panel=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),panel)
 cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
 enums=cockpit[cockpit.index('enum JPW_COCKPIT_ROUTE'):cockpit.index('string JPWCockpitCornerName')]
 model=(INC/'JPW_Alavancagem_Positions.mqh').read_text()
 structs=model[model.index('struct JPWPositionView'):model.index('JPWPositionView g_position_views')]
 risk=(INC/'JPW_Alavancagem_StopRisk_Core.mqh').read_text()
 riskstructs=risk[risk.index('struct JPWStopRiskRow'):risk.index('void JPWStopRiskClearSample')]
 shim=HUD_SHIM.replace('constexpr int JPW_COCKPIT_METRIC_COUNT=6,JPW_ROUTE_SETTINGS=10,JPW_OBSERVER_NOT_CONFIRMED=1','constexpr int JPW_COCKPIT_METRIC_COUNT=6,JPW_OBSERVER_NOT_CONFIRMED=1')
 shim=shim.replace('bool TextGetSize(const string&value,uint&width,uint&height){','extern int dpi,text_override;\nbool TextGetSize(const string&value,uint&width,uint&height){')
 shim=shim.replace('int glyph=measured_font>8?measured_font:8;\n width=(uint)value.size()*glyph;\n height=(uint)(measured_font*3/2>12?measured_font*3/2:12);', 'int count=0;for(unsigned char c:value)if((c&0xc0)!=0x80)count++;\n height=text_override>0?(uint)text_override:(uint)((measured_font*4*dpi+299)/300);\n width=(uint)(count*(height*0.48));')
 shim=shim.replace('bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}', 'bool ObjectCreate(int,const string&name,int type,int,int,int){objects[name]=Object{};objects[name].number[-1]=type;return true;}')
 signatures=[
 ('string JPWFitText','string JPWFitText(const string text,const int available,const int font_size)'),
 ('string JPWRaizUI','string JPWRaizUI(const string suffix)'),
 ('string JPWActionObject','string JPWActionObject(const int action)'),
 ('bool JPWRaizCreateLabel','bool JPWRaizCreateLabel(const string suffix,const string value,const int x,const int y,const int font_size=0)'),
 ('bool JPWCreateProtectedValue','bool JPWCreateProtectedValue(const string suffix,const string value,const int x,const int y,const int width,const int font_size=0)'),
 ('bool JPWRaizCreateSurface','bool JPWRaizCreateSurface(const string suffix,const int x,const int y,const int width,const int height,const color fill)'),
 ('void JPWFocusRegister','void JPWFocusRegister(const int action)'),('void JPWFocusPaint','void JPWFocusPaint()'),
 ('bool JPWRaizCreateButton','bool JPWRaizCreateButton(const int index,const string value,const int x,const int y,const int width)'),
 ('string JPWPositionTicket','string JPWPositionTicket(const ulong ticket)'),
 ('string JPWPositionLeverageText','string JPWPositionLeverageText(JPWPositionView &row)'),
 ('string JPWPositionRole','string JPWPositionRole(JPWPositionView &row)'),
 ('string JPWPositionRoleShort','string JPWPositionRoleShort(JPWPositionView &row)'),
 ('bool JPWPositionRiskView','bool JPWPositionRiskView(JPWPositionView &position,string &amount,string &percent,string &state,string &reason)'),
 ('bool JPWPositionInView','bool JPWPositionInView(JPWPositionView &row)'),
 ('void JPWRenderPositionsTable','void JPWRenderPositionsTable(const int x,const int body_y,const int inner,const int body_height,const int footer_y)')]
 creators=''
 for marker,sig in signatures:
  body=body_of(source,marker).replace('int indexes[];','std::vector<int> indexes;')
  creators+=sig+'{'+body+'}\n'
 creators='string JPWStopRiskMoney(double);\nstring JPWFormatLeverage(double);\n'+creators
 creators='bool JPWPositionsViewCurrent(const string context,const ulong now){'+body_of(model,'bool JPWPositionsViewCurrent(')+'}\n'+creators
 core=(INC/'JPW_Alavancagem_Core.mqh').read_text()
 creators+='string JPWFormatLeverage(const double leverage){'+body_of(core,'string JPWFormatLeverage(')+'}\n'
 creators+='string JPWStopRiskMoney(const double value){'+body_of(source,'string JPWStopRiskMoney(')+'}\n'
 baseline_mode=len(sys.argv)==3 and sys.argv[1]=='--baseline-close'
 if baseline_mode:
  with tarfile.open(sys.argv[2]) as archive:
   members=[m for m in archive.getmembers() if m.name.endswith('MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh')]
   if len(members)!=1:raise AssertionError('one exact baseline presentation required')
   baseline=archive.extractfile(members[0]).read().decode()
  # Every chart creator used for this old-close probe is byte-identical to the
  # frozen baseline; new positions helpers are compiled but never executed.
  for marker,_ in signatures[:9]:
   if body_of(source,marker)!=body_of(baseline,marker):raise AssertionError('baseline creator changed: '+marker)
  print('BASELINE_PRESENTATION_SHA256:',hashlib.sha256(baseline.encode()).hexdigest())
  renderer=body_of(baseline,'void JPWRenderCockpit()')
 else:renderer=body_of(source,'void JPWRenderCockpit()')
 prefix=renderer[:renderer.index('   if(g_raiz_tab==JPW_ROUTE_OVERVIEW)\n')]
 footer=renderer[renderer.index('   if(g_raiz_tab==JPW_ROUTE_SETTINGS)\n'):]
 creators+='void RenderStopsWindow(){'+prefix+('' if baseline_mode else 'JPWRenderPositionsTable(x,body_y,inner,body_height,footer_y);\n')+footer+'}\n'
 test_main=MAIN
 if baseline_mode:
  test_main=r"""
int main(){chart_width=1198;chart_height=938;g_raiz_tab=JPW_ROUTE_STOPS;objects.clear();RenderStopsWindow();
 const string old=JPWActionObject(JPW_ACTION_CLOSE),header=JPWActionObject(JPW_ACTION_HEADER_CLOSE);
 std::cout<<"BASELINE_CLOSE_OBJECT: "<<objects[old].text[OBJPROP_TEXT]<<" y="<<objects[old].number[OBJPROP_YDISTANCE]<<"; header exists="<<objects.count(header)<<"\n";
 if(!objects.count(header)){std::cout<<"BASELINE_CLOSE: PRODUCT_FAIL — production header close overwritten by footer on same object name; native NOT_RUN\n";return 1;}
 return 0;}
"""
 cpp='using ulong=unsigned long;\n'+shim+'\n'+panel+'\n'+enums+'\n'+structs+'\n'+riskstructs+'\n'+SHIM+'\n'+brand+'\n'+creators+'\n'+test_main
 with tempfile.TemporaryDirectory(prefix='jpw-positions-ui-') as tmp:
  src=Path(tmp)/'ui.cpp';exe=Path(tmp)/'ui';src.write_text(cpp)
  for cmd in ([compiler,'-std=c++17','-Wall','-Wextra',str(src),'-o',str(exe)],[str(exe)]):
   r=subprocess.run(cmd,text=True,capture_output=True,timeout=60);print(r.stdout,end='');print(r.stderr,end='')
   if r.returncode:return r.returncode
 print('SOURCE_SHA256:',hashlib.sha256(PRESENT.read_bytes()).hexdigest())
 return 0
if __name__=='__main__':raise SystemExit(main())

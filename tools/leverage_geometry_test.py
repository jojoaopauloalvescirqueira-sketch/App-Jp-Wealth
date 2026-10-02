#!/usr/bin/env python3
"""Run distributed MQL panel geometry and tests with a minimal host C++ shim.

No native MT5 rendering/click/DPI assertion is claimed. The supplied text metrics
represent a synthetic 12 px font at 100/125/150/200%; native text measurement and
control hit testing remain a separate required verification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from leverage_panel_test import body_of


ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
FILES = [MQL / "Include/JPWealth/JPW_Alavancagem_Panel.mqh",
         MQL / "Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5"]
PRESENTATION = MQL / "Include/JPWealth/JPW_Alavancagem_Presentation.mqh"


def cockpit_target(source: str) -> tuple[int, int]:
    match = re.search(
        r"JPWPanelCockpit\(chart_width,chart_height,(\d+),(\d+),g_details_rect\)",
        source,
    )
    if match is None:
        raise AssertionError("Cockpit renderer must pass a measurable size to JPWPanelCockpit")
    return int(match[1]), int(match[2])

SHIM = r'''
#include <cmath>
#include <iostream>
#include <string>
using string = std::string;
using color = int;
int MathAbs(int v) { return std::abs(v); }
template<class A,class B>A MathMax(A a,B b){return a>b?a:(A)b;}
template<class A,class B>A MathMin(A a,B b){return a<b?a:(A)b;}
template <typename... T> void Print(T... args) { (std::cout << ... << args) << '\n'; }
'''

MAIN = r'''
bool Inside(const JPWPanelRect &parent,int x,int y,int w,int h) {
  return w>0 && h>0 && x>=parent.x && y>=parent.y &&
         x+w<=parent.x+parent.width && y+h<=parent.y+parent.height;
}
double Channel(int byte) {
  const double value=byte/255.0;
  return value<=0.04045 ? value/12.92 : std::pow((value+0.055)/1.055,2.4);
}
double Luminance(color c) {
  return 0.2126*Channel(c&255)+0.7152*Channel((c>>8)&255)+
         0.0722*Channel((c>>16)&255);
}
double Contrast(color a,color b) {
  const double first=Luminance(a),second=Luminance(b);
  return (std::fmax(first,second)+0.05)/(std::fmin(first,second)+0.05);
}
int main() {
  OnStart();
  const int widths[]={240,320,390,1440};
  const int heights[]={240,480,900};
  const int scales[]={100,125,150,200};
  int cases=0,unusable=0;
  for(int width:widths) for(int height:heights) for(int dpi:scales) {
    ++cases;
    const int text=(12*dpi+99)/100;
    JPWPanelRect dialog;
    int pad=0,line=0,control=0,cy=0,ch=0,fy=0;
    Check(JPWPanelDialog(width,height,text,text/2,dialog,pad,line,control,cy,ch,fy),
          "host dialog defined");
    JPWPanelRect cockpit;
    Check(JPWPanelCockpit(width,height,__COCKPIT_WIDTH__,__COCKPIT_HEIGHT__,cockpit),"cockpit rectangle defined");
    const JPWPanelRect chart={0,0,width,height,false};
    Check(Inside(chart,cockpit.x,cockpit.y,cockpit.width,cockpit.height),
          "cockpit bounded at each synthetic viewport/DPI");
    Check(std::abs(cockpit.x*2+cockpit.width-width)<=1 &&
          std::abs(cockpit.y*2+cockpit.height-height)<=1,
          "cockpit centered at each viewport");
    Check(cockpit.compact==(cockpit.width<420 || cockpit.height<400),
          "compact navigation selected when width or height is limited");
    const int inner=dialog.width-2*pad;
    const int x=dialog.x+pad;
    const int footer_width=(inner-3*pad)/4;
    Check(Inside(dialog,x,dialog.y+pad,inner,text),"title bounded");
    const int nav_y=dialog.y+pad+line;
    const int nav_width=(inner-2*pad)/3;
    for(int button=0;button<3;button++)
      Check(Inside(dialog,x+button*(nav_width+pad),nav_y,nav_width,control),
            "navigation controls bounded");
    const int chrome_end=nav_y+control+(dialog.compact ? 0 : control+pad);
    Check(cy>=chrome_end,"content never overlaps navigation/action chrome");
    for(int button=0;button<4;button++)
      Check(Inside(dialog,x+button*(footer_width+pad),fy,footer_width,control),
            "Close/Cancel, previous, next and apply buttons bounded independently");
    // The editing row is the actual renderer's caption + edit box + padding.
    const int edit_row=line+control+pad;
    const int rows=JPWPanelPageRows(ch,edit_row);
    if(rows==0) {
      ++unusable;
      Print("UNUSABLE_EDIT_GEOMETRY: width=",width," height=",height," dpi=",dpi,
            " content_height=",ch," needed=",edit_row);
    }
    Check(rows>0,"at least one editable field fits; pagination cannot recover zero rows");
    if(rows>0) {
      const int count=JPWPanelPageCount(17,rows);
      int seen[17]={0};
      for(int page=0;page<count;page++) for(int row=0;row<rows;row++) {
        const int index=page*rows+row;
        if(index>=17) continue;
        ++seen[index];
        const int y=cy+row*edit_row;
        Check(Inside(dialog,x,y,inner,text),"paged field caption inside dialog");
        Check(Inside(dialog,x,y+line,inner,control),"paged edit control inside dialog");
        Check(y+line+control<=fy,"paged edit control never overlaps footer");
      }
      for(int index=0;index<17;index++) Check(seen[index]==1,"every field is reachable exactly once");
    }
    for(int corner=0;corner<4;corner++) {
      JPWPanelRect hud;
      const int gap=text/4>2 ? text/4 : 2;
      const int button_height=text+2*gap;
      const int full_height=5*(text+gap)+button_height;
      Check(JPWPanelHUD(width,height,180,full_height,16,40,(corner%2)==1,corner>=2,hud),
            "HUD group geometry");
      for(int row=0;row<5;row++)
        Check(Inside(chart,hud.x,hud.y+row*(text+gap),180,text),
              "actual HUD line bounded in each corner");
      Check(Inside(chart,hud.x,hud.y+5*(text+gap),70,button_height),
            "actual Details button bounded in each corner");
    }
  }
  JPWPanelRect rejected;
  JPWPanelRect roomy;
  Check(JPWPanelCockpit(1440,900,__COCKPIT_WIDTH__,__COCKPIT_HEIGHT__,roomy) &&
        roomy.width>=1000 && roomy.height>=700 && Inside({0,0,1440,900,false},
        roomy.x,roomy.y,roomy.width,roomy.height),
        "main cockpit grows beyond 760x620 while staying inside a desktop chart");
  for(int chart:{240,320,800,1440}) {
    const int reserved=JPWPanelHUDReservedWidth(chart,12,6,90);
    Check(reserved>=90 && reserved<=chart-16,
          "HUD width budget fits chart and launcher independent of live metric text");
  }
  Check(JPWPanelHUDReservedWidth(1440,24,6,90)>
        JPWPanelHUDReservedWidth(1440,12,6,90),
        "HUD reserves more room when measured text grows at high DPI");
  Check(!JPWPanelHUD(100,100,180,180,0,0,false,false,rejected),
        "oversized HUD rejected rather than claiming children fit a clamped container");
  const color white=255|(255<<8)|(255<<16);
  const color black=0;
  const color standard_gray=118|(118<<8)|(118<<16);
  const color cockpit_gray=60|(60<<8)|(60<<16);
  const color pale=JPWPanelSurface(white),dark=JPWPanelSurface(black);
  Check(Contrast(JPWPanelTextColor(white,standard_gray),pale)>=4.5,
        "small gray text meets 4.5:1 on default light HUD");
  Check(Contrast(JPWPanelTextColor(black,standard_gray),dark)>=4.5,
        "small gray text meets 4.5:1 on default dark HUD");
  Check(Contrast(JPWPanelTextColor(white,cockpit_gray),JPWPanelCardSurface(white))>=4.5 &&
        Contrast(JPWPanelTextColor(white,cockpit_gray),JPWPanelChromeSurface(white))>=4.5,
        "light Cockpit card and navigation surfaces retain text contrast");
  Check(Contrast(JPWPanelTextColor(black,cockpit_gray),JPWPanelCardSurface(black))>=4.5 &&
        Contrast(JPWPanelTextColor(black,cockpit_gray),JPWPanelChromeSurface(black))>=4.5,
        "dark Cockpit card and navigation surfaces retain text contrast");
  Check(!JPWPanelDarkBackground(white) && JPWPanelDarkBackground(black),
        "light and dark chart themes use distinct surfaces");
  for(color chart : {white,black}) {
    Check(Contrast(JPWPanelInk(chart),JPWPanelWindowSurface(chart))>=4.5 &&
          Contrast(JPWPanelInk(chart),JPWPanelCardSurface(chart))>=4.5,
          "shared window/card ink retains 4.5:1 contrast");
    Check(Contrast(JPWPanelMutedText(chart),JPWPanelWindowSurface(chart))>=4.5 &&
          Contrast(JPWPanelMutedText(chart),JPWPanelCardSurface(chart))>=4.5 &&
          Contrast(JPWPanelMutedText(chart),JPWPanelChromeSurface(chart))>=4.5,
          "secondary reasons and pagination retain 4.5:1 contrast");
    Check(Contrast(JPWPanelAccentColor(chart),JPWPanelSelectedSurface(chart))>=4.5 &&
          Contrast(JPWPanelAccentColor(chart),JPWPanelChromeSurface(chart))>=4.5,
          "selected tabs and state bands retain 4.5:1 contrast");
    Check(Contrast(JPWPanelPrimaryInk(chart),JPWPanelAccentColor(chart))>=4.5,
          "explicit primary actions retain 4.5:1 contrast");
  }
  Print("HOST_GEOMETRY: ",asserts-failures," PASS / ",failures," FAIL; ",cases," viewports; ",
        cases*4," corner cases; ",unusable," unusable edit cases");
  Print("NATIVE_MT5_GEOMETRY_CLICKS_DPI: NOT_RUN");
  return failures==0 ? 0 : 1;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler; native MT5 NOT_RUN")
        return 2
    sources = [p.read_text(encoding="utf-8") for p in FILES]
    desired_width, desired_height = cockpit_target(PRESENTATION.read_text(encoding="utf-8"))
    body = "\n".join(re.sub(r"^\s*#(?:include|property)\b[^\n]*", "", s,
                             flags=re.MULTILINE) for s in sources)
    body = re.sub(r"C'(\d+),(\d+),(\d+)'",
                  lambda m: str(int(m[1]) | (int(m[2]) << 8) | (int(m[3]) << 16)), body)
    print(json.dumps({"test": "leverage_geometry", "kind": "HOST_SYNTHETIC_NOT_MT5",
                      "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in FILES}, "compiler": compiler}, indent=2))
    version = subprocess.run([compiler, "--version"], text=True, capture_output=True, check=False)
    print(version.stdout, end="")
    print(version.stderr, end="")
    with tempfile.TemporaryDirectory(prefix="jpw-panel-geometry-synthetic-") as tmp:
        src = Path(tmp) / "geometry.cpp"
        exe = Path(tmp) / "geometry"
        geometry_main = (MAIN.replace("__COCKPIT_WIDTH__", str(desired_width))
                             .replace("__COCKPIT_HEIGHT__", str(desired_height)))
        src.write_text(SHIM + "\n" + body + "\n" + geometry_main, encoding="utf-8")
        result = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", str(src), "-o", str(exe)],
                                text=True, capture_output=True, check=False, timeout=60)
        print(result.stdout, end="")
        print(result.stderr, end="")
        if result.returncode:
            print(f"HOST_COMPILATION: PRODUCT_FAIL; exit={result.returncode}")
            return result.returncode
        result = subprocess.run([str(exe)], text=True, capture_output=True, check=False, timeout=30)
        print(result.stdout, end="")
        print(result.stderr, end="")
        print(f"EXIT_CODE: {result.returncode}")
        if result.returncode:
            return result.returncode
    result = presentation_layout_replay(compiler)
    if result:
        return result
    return hud_layout_replay(compiler)


LAYOUT_SHIM = r'''
#include <climits>
#include <vector>
using ulong=unsigned long;
bool MathIsValidNumber(double x){return std::isfinite(x);}
string IntegerToString(long x){return std::to_string(x);}
int g_details_control=24,g_details_line=18,g_details_pad=5,g_details_font=11,g_cockpit_page=0;
color g_details_card=0xffffff,g_details_chrome=0xf4eee9;
bool g_cockpit_pref_invalid=false;string g_cockpit_pref_notice;
int g_personal_live_count=0,g_personal_live_state=-1;string g_personal_live_notice;
JPWCockpitSnapshot g_cockpit_snapshot;
constexpr int OBJPROP_TOOLTIP=1,OBJPROP_ZORDER=2;
struct Drawn{int x,y,width,height;string type;};std::vector<Drawn> drawn;
bool JPWRaizCreateButton(int id,const string&,int x,int y,int w){drawn.push_back({x,y,w,g_details_control,"button"+std::to_string(id)});return true;}
bool JPWRaizCreateLabel(const string&,const string&,int x,int y,int=0){drawn.push_back({x,y,1,g_details_line,"label"});return true;}
bool JPWCreateProtectedValue(const string&,const string&,int x,int y,int w,int=0){drawn.push_back({x,y,w,g_details_line,"value"});return true;}
bool JPWRaizCreateSurface(const string&,int x,int y,int w,int h,color){drawn.push_back({x,y,w,h,"surface"});return true;}
string JPWFitText(const string&s,int,int){return s;}
string JPWCockpitQualityText(int){return "Current";}
string JPWGenetrixMetricQuality(int,int quality){return JPWCockpitQualityText(quality);}
string JPWRaizUI(const string&s){return s;}
bool ObjectSetString(int,const string&,int,const string&){return true;}
bool ObjectSetInteger(int,const string&,int,long){return true;}
int g_stop_button_count=0;
'''

LAYOUT_MAIN = r'''
int main(){
 int cases=0;
 for(int dpi: {100,125,150,200})for(int width:{240,390,720})for(int height:{24,29,42,50,70,87,100,140,240}){
   g_details_control=(24*dpi+99)/100;g_details_line=(18*dpi+99)/100;g_details_pad=(5*dpi+99)/100;
   if(height<g_details_control)continue;
   const int y=70,footer=y+height+g_details_line+g_details_pad;
   drawn.clear();g_cockpit_page=0;
   RenderOverview(10,y,width,height,footer);
   for(const auto&d:drawn){
     if(d.y<y||d.y+d.height>footer||d.x<10||d.x+d.width>10+width){
       std::cerr<<"FAIL real overview branch crossed content/footer bounds: "<<height<<" "<<width<<" "<<dpi<<" "<<d.type<<"\n";return 1;}}
   cases++;
   for(bool horizontal:{false,true}){
     JPWStopsLayout layout;
     JPWPanelStopsLayout(height,g_details_line,g_details_control,g_details_pad,
                         horizontal,true,layout);
     if(layout.rows_per_page>0){
       if(layout.rows_per_page>16||layout.row_height<=0||
          layout.table_offset+layout.rows_per_page*layout.row_height>height||
          (layout.value_lines!=(horizontal?1:2)&&layout.value_lines!=0)){
         std::cerr<<"FAIL Stops row geometry "<<height<<" "<<dpi<<"\n";return 1;}}
     else if(height>=g_details_control+g_details_pad){
       std::cerr<<"FAIL Stops did not provide a focusable row when controls fit\n";return 1;}
     JPWPanelStopsLayout(height,g_details_line,g_details_control,g_details_pad,
                         horizontal,false,layout);
     if(layout.table_offset+g_details_line<=height && layout.summary_lines>2){
       std::cerr<<"FAIL Stops no-row summary geometry\n";return 1;}
   }
 }
 // The enlarged desktop cockpit must show all seven overview cards (including the original six) at the
 // default measured font; larger text may paginate but never overlap chrome.
 JPWPanelRect desktop;
 if(!JPWPanelCockpit(1440,900,__COCKPIT_WIDTH__,__COCKPIT_HEIGHT__,desktop))return 1;
 for(int measured:{16,32}){
   g_details_pad=(measured/2>6?measured/2:6);
   g_details_line=measured+g_details_pad;
   g_details_control=measured+2*g_details_pad;
   const int inner=desktop.width-2*g_details_pad;
   const int x=desktop.x+g_details_pad;
   const int nav_y=desktop.y+g_details_pad+g_details_line;
   const int body_y=nav_y+g_details_control+g_details_pad;
   const int footer_y=desktop.y+desktop.height-g_details_pad-g_details_control;
   const int body_height=footer_y-g_details_pad-body_y-g_details_line;
   drawn.clear();g_cockpit_page=0;
   RenderOverview(x,body_y,inner,body_height,footer_y);
   int cards=0;
   for(const auto&item:drawn){
     if(item.type.rfind("button5",0)==0)cards++;
     if(item.y<body_y||item.y+item.height>footer_y||item.x<x||item.x+item.width>x+inner){
       std::cerr<<"FAIL enlarged overview content crossed body/footer at text="<<measured<<"\n";return 1;}}
   if((measured==16&&cards!=7)||(measured==32&&cards<1)){
     std::cerr<<"FAIL enlarged cockpit overview card capacity at text="<<measured<<"\n";return 1;}
 }
 // A 636 px chart still gives the enlarged renderer a 620 px cockpit. The
 // reported 32 px text case must remain usable in that constrained viewport.
 JPWPanelRect rect;
 if(!JPWPanelCockpit(1440,636,__COCKPIT_WIDTH__,__COCKPIT_HEIGHT__,rect)||rect.height!=620)return 1;
 const int text_height=32,pad=text_height/2,line=text_height+pad,control=text_height+2*pad;
 const int body=rect.height-2*pad-control-
                (pad+line+control+pad)-line;
 if(body!=332||body>=5*line+control+2*pad)return 1;
 JPWStopsLayout screenshot;
 JPWPanelStopsLayout(body,line,control,pad,true,true,screenshot);
 if(screenshot.rows_per_page<1||screenshot.value_lines!=1)return 1;
 int stop_cases=0;
 for(int font:{9,11,16,24})for(int dpi:{100,125,150,200}){
   const int measured=(font*4*dpi+299)/300;
   const int inset=(measured/2>6?measured/2:6),ln=measured+inset,ctl=measured+2*inset;
   const int available=620-(4*inset+2*ctl+2*ln);
   for(bool horizontal:{false,true}){
     JPWStopsLayout measured_layout;
     JPWPanelStopsLayout(available,ln,ctl,inset,horizontal,true,measured_layout);
     if(available>=ctl+inset&&measured_layout.rows_per_page<1)return 1;
     if(measured_layout.rows_per_page>0&&
        measured_layout.table_offset+measured_layout.rows_per_page*measured_layout.row_height>available)return 1;
     stop_cases++;
   }
 }
 std::cout<<"HOST_PRESENTATION_LAYOUT: "<<cases<<" constrained overview/Stops cases PASS; 32px/620px regression PASS; "<<stop_cases<<" font/DPI Stops cases PASS; native text metrics NOT_RUN\n";
 return 0;
}
'''


def presentation_layout_replay(compiler: str) -> int:
    include=MQL / "Include/JPWealth"
    source=(include / "JPW_Alavancagem_Presentation.mqh").read_text()
    samples=(include / "JPW_Alavancagem_Samples.mqh").read_text()
    cockpit=(include / "JPW_Alavancagem_Cockpit.mqh").read_text()
    cockpit=cockpit[:cockpit.index("string JPWCockpitCornerName")] + "\n#endif\n"
    cockpit=re.sub(r"^#include[^\n]*", "", cockpit, flags=re.MULTILINE)
    panel=(include / "JPW_Alavancagem_Panel.mqh").read_text()
    panel=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),panel)
    overview=body_of(source,"if(g_raiz_tab==JPW_ROUTE_OVERVIEW)")
    stops=body_of(source,"void JPWRenderStopsTable(const int x,const int body_y,const int inner,\n                         const int body_height,const int footer_y)")
    assert stops.index("if(g_stop_ready)") < stops.index("JPWPanelStopsLayout(")
    assert "Amplie para ler a tabela." not in stops
    assert "g_stop_reason" in stops and "LAST · NOT ACTIVE" in stops
    assert 'const string inactive_reason=' in stops
    assert '"Inactive: "+inactive_reason' in stops
    assert '" · LAST · "+inactive_reason' in stops
    assert "JPW_ACTION_STOP_ROW_FIRST+j" in stops
    signature="(const int x,const int body_y,const int inner,const int body_height,const int footer_y)"
    cpp=SHIM+"\n#include <climits>\nusing ulong=unsigned long;\nbool MathIsValidNumber(double x){return std::isfinite(x);}\n"+samples+cockpit+panel
    shim=LAYOUT_SHIM.replace("bool MathIsValidNumber(double x){return std::isfinite(x);}","")
    desired_width,desired_height=cockpit_target(source)
    layout_main=(LAYOUT_MAIN.replace("__COCKPIT_WIDTH__",str(desired_width))
                            .replace("__COCKPIT_HEIGHT__",str(desired_height)))
    cpp+=shim+"void RenderOverview"+signature+"{"+overview+"}\n"+layout_main
    print("PRESENTATION_LAYOUT_SOURCE_SHA256:",hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-presentation-layout-") as temporary:
        path,binary=Path(temporary)/"layout.cpp",Path(temporary)/"layout"
        path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,text=True,capture_output=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


HUD_SHIM = r'''
#include <iostream>
#include <map>
#include <string>
using string=std::string;
using color=int;
using uint=unsigned int;
constexpr int FW_NORMAL=0,BORDER_FLAT=0,ANCHOR_LEFT_UPPER=0;
constexpr int CORNER_LEFT_UPPER=0,CORNER_LEFT_LOWER=1,CORNER_RIGHT_UPPER=2,CORNER_RIGHT_LOWER=3;
constexpr int CHART_WIDTH_IN_PIXELS=1,CHART_HEIGHT_IN_PIXELS=2,CHART_COLOR_BACKGROUND=3;
constexpr int OBJ_RECTANGLE_LABEL=1,OBJ_LABEL=2,OBJ_BUTTON=3;
constexpr int OBJPROP_CORNER=1,OBJPROP_XDISTANCE=2,OBJPROP_YDISTANCE=3,
 OBJPROP_XSIZE=4,OBJPROP_YSIZE=5,OBJPROP_BGCOLOR=6,OBJPROP_COLOR=7,
 OBJPROP_BORDER_TYPE=8,OBJPROP_BACK=9,OBJPROP_ZORDER=10,OBJPROP_SELECTABLE=11,
 OBJPROP_HIDDEN=12,OBJPROP_ANCHOR=13,OBJPROP_FONTSIZE=14,OBJPROP_FONT=15,
 OBJPROP_TEXT=16,OBJPROP_TOOLTIP=17,OBJPROP_BORDER_COLOR=18;
int chart_width=800,chart_height=400;
long ChartGetInteger(int,int property){
 if(property==CHART_WIDTH_IN_PIXELS)return chart_width;
 if(property==CHART_HEIGHT_IN_PIXELS)return chart_height;
 return 0xffffff;
}
int measured_font=8;
bool TextSetFont(const string&,int size,int){measured_font=-size/10;return measured_font>0;}
bool TextGetSize(const string&value,uint&width,uint&height){
 int glyph=measured_font>8?measured_font:8;
 width=(uint)value.size()*glyph;
 height=(uint)(measured_font*3/2>12?measured_font*3/2:12);
 return true;
}
struct Object{std::map<int,long> number;std::map<int,string> text;};
std::map<string,Object> objects;
int ObjectFind(int,const string&name){return objects.count(name)?0:-1;}
bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}
bool ObjectDelete(int,const string&name){objects.erase(name);return true;}
bool ObjectSetInteger(int,const string&name,int property,long value){objects[name].number[property]=value;return true;}
bool ObjectSetString(int,const string&name,int property,const string&value){objects[name].text[property]=value;return true;}
string IntegerToString(int value){return std::to_string(value);}
template<class A,class B>A MathMax(A a,B b){return a>b?a:(A)b;}
template<class A,class B>A MathMin(A a,B b){return a<b?a:(A)b;}
constexpr int JPW_COCKPIT_METRIC_COUNT=7,JPW_ROUTE_SETTINGS=10,JPW_OBSERVER_NOT_CONFIRMED=1;
enum JPW_VIEW_QUALITY{JPW_VIEW_NA=0,JPW_VIEW_CURRENT=1,JPW_VIEW_ESTIMATED=2};
struct JPWCockpitPrefs{int visible_mask,corner,density;};
struct JPWCockpitMetric{string title,value,reason;JPW_VIEW_QUALITY quality;};
struct JPWCockpitSnapshot{JPWCockpitMetric metric[7];};
bool JPWCockpitVisible(JPWCockpitPrefs&prefs,int index){return (prefs.visible_mask&(1<<index))!=0;}
string JPWCockpitQualityText(JPW_VIEW_QUALITY quality){
 return quality==JPW_VIEW_CURRENT?"Current":quality==JPW_VIEW_ESTIMATED?"Estimated":"N/A";
}
// New seventh-metric boundary is verified in jpw_genetrix_ui_test; legacy HUD fixtures keep their original six rows.
string JPWGenetrixMetricQuality(int,JPW_VIEW_QUALITY quality){return JPWCockpitQualityText(quality);}
string g_panel_prefix="JPW_TEST_";
int InpFontSize=8,InpOffsetX=16,InpOffsetY=40,InpFontColor=0x767676;
JPWCockpitPrefs g_cockpit_prefs={63,0,0},g_cockpit_draft={63,0,0};
JPWCockpitSnapshot g_cockpit_snapshot;
bool g_raiz_details_open=false,g_hud_summary=false;
int g_raiz_tab=7,g_stop_observer_presence=0,g_hud_summary_source=-1,g_panel_count=0;
'''

HUD_MAIN = r'''
struct Shot{int x,y,width,height;bool summary;string text;};
Shot DrawHUD(int width,int height,int corner,int density,bool changed){
 chart_width=width;chart_height=height;objects.clear();g_panel_count=0;
 g_cockpit_prefs={63,corner,density};g_stop_observer_presence=changed?JPW_OBSERVER_NOT_CONFIRMED:0;
 const string titles[6]={"Leverage","Floating P/L","Genesis SL","Raiz N 1W","Raiz N 2W","Stop risk"};
 const string initial[6]={"2,75x","1,20%","0,85%","1,40%","2,10%","0,60%"};
 const string updated[6]={"12,34x","-7,89%","3,10%","2,60%","3,30%","N/A"};
 for(int i=0;i<6;i++){
   auto &metric=g_cockpit_snapshot.metric[i];
   metric.title=titles[i];metric.value=changed?updated[i]:initial[i];metric.reason="Synthetic sample";
   metric.quality=changed?(i==5?JPW_VIEW_NA:JPW_VIEW_ESTIMATED):JPW_VIEW_CURRENT;
 }
 JPWRenderHUD();
 const string bg=g_panel_prefix+"HUD_BG";
 if(!objects.count(bg))return {-1,-1,-1,-1,g_hud_summary,""};
 const auto&shape=objects[bg].number;
 const string label=g_panel_prefix+"0";
 return {(int)shape.at(OBJPROP_XDISTANCE),(int)shape.at(OBJPROP_YDISTANCE),
         (int)shape.at(OBJPROP_XSIZE),(int)shape.at(OBJPROP_YSIZE),g_hud_summary,
         objects.count(label)?objects[label].text[OBJPROP_TEXT]:""};
}
bool InBounds(const Shot&shot,int width,int height){
 return shot.x>=0&&shot.y>=0&&shot.width>0&&shot.height>0&&
        shot.x+shot.width<=width&&shot.y+shot.height<=height;
}
int main(){
 int scenarios=0;
 for(int density:{0,1})for(int corner:{0,1,2,3}){
   const Shot first=DrawHUD(800,400,corner,density,false);
   const Shot next=DrawHUD(800,400,corner,density,true);
   if(!InBounds(first,800,400)||!InBounds(next,800,400)||first.summary||next.summary||
      first.x!=next.x||first.y!=next.y||first.width!=next.width||
      first.height!=next.height||first.text==next.text){
     std::cerr<<"FAIL full HUD pulsed on data-only refresh; density="<<density<<" corner="<<corner
              <<" first="<<first.width<<"x"<<first.height<<" next="<<next.width<<"x"<<next.height<<"\n";
     return 1;
   }
   scenarios++;
 }
 const Shot compact=DrawHUD(220,95,CORNER_RIGHT_UPPER,0,false);
 const Shot compact_next=DrawHUD(220,95,CORNER_RIGHT_UPPER,0,true);
 if(!InBounds(compact,220,95)||!InBounds(compact_next,220,95)||
    !compact.summary||!compact_next.summary||compact.x!=compact_next.x||
    compact.y!=compact_next.y||compact.width!=compact_next.width||
    compact.height!=compact_next.height){
   std::cerr<<"FAIL summary HUD pulsed on data-only refresh\n";return 1;
 }
 const Shot resized=DrawHUD(340,180,CORNER_RIGHT_UPPER,0,false);
 if(!InBounds(resized,340,180)){
   std::cerr<<"FAIL HUD resize escaped chart bounds\n";return 1;
 }
 const Shot narrow=DrawHUD(400,240,CORNER_RIGHT_UPPER,0,false);
 if(!InBounds(narrow,400,240)||narrow.width>180){
   std::cerr<<"FAIL HUD obscures narrow chart width\n";return 1;
 }
 InpFontSize=40;
 const Shot large_font=DrawHUD(200,160,CORNER_RIGHT_UPPER,0,false);
 const string cockpit_button=g_panel_prefix+"RAIZ_DETAILS_BUTTON";
 if(!InBounds(large_font,200,160)||!objects.count(cockpit_button)){
   std::cerr<<"FAIL large-font HUD lost cockpit access\n";return 1;
 }
 const auto&button=objects[cockpit_button].number;
 if(button.at(OBJPROP_XDISTANCE)<large_font.x || button.at(OBJPROP_YDISTANCE)<large_font.y ||
    button.at(OBJPROP_XDISTANCE)+button.at(OBJPROP_XSIZE)>large_font.x+large_font.width ||
    button.at(OBJPROP_YDISTANCE)+button.at(OBJPROP_YSIZE)>large_font.y+large_font.height){
   std::cerr<<"FAIL large-font cockpit button escapes HUD\n";return 1;
 }
 InpFontSize=8;
 std::cout<<"HOST_HUD_STABILITY: "<<scenarios<<" full refresh pairs and one summary pair PASS; "
             "narrow and large-font bounds PASS; native MT5 redraw/DPI NOT_RUN\n";
 return 0;
}
'''


def hud_layout_replay(compiler: str) -> int:
    source = PRESENTATION.read_text(encoding="utf-8")
    panel = FILES[0].read_text(encoding="utf-8")
    panel = re.sub(r"C'(\d+),(\d+),(\d+)'",
                   lambda m: str(int(m[1]) | (int(m[2]) << 8) | (int(m[3]) << 16)), panel)
    renderer = "void JPWClearPanel(){" + body_of(source, "void JPWClearPanel()") + "}\n"
    renderer += "void JPWRenderHUD(){" + body_of(source, "void JPWRenderHUD()") + "}\n"
    cpp = HUD_SHIM + panel + renderer + HUD_MAIN
    print("HUD_RENDER_SOURCE_SHA256:", hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-hud-stability-") as temporary:
        path, binary = Path(temporary) / "hud.cpp", Path(temporary) / "hud"
        path.write_text(cpp, encoding="utf-8")
        for command in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)],
                        [str(binary)]):
            result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    return 0


def capture_overview(destination: Path) -> int:
    """Export actual renderer/creator calls, with synthetic native API metrics.

    This is an inspectable preview fixture, never native MT5 evidence. The
    existing geometry, numeric-value and event assertions remain independent.
    """
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no host C++ compiler")
        return 1
    source = PRESENTATION.read_text(encoding="utf-8")
    panel = FILES[0].read_text(encoding="utf-8")
    panel = re.sub(r"C'(\d+),(\d+),(\d+)'",
                   lambda m: str(int(m[1]) | (int(m[2]) << 8) | (int(m[3]) << 16)), panel)
    cockpit = (MQL / "Include/JPWealth/JPW_Alavancagem_Cockpit.mqh").read_text()
    enums = cockpit[cockpit.index("enum JPW_COCKPIT_ROUTE"):cockpit.index("string JPWCockpitCornerName")]
    shim = HUD_SHIM.replace(
        "JPW_COCKPIT_METRIC_COUNT=7,JPW_ROUTE_SETTINGS=10,JPW_OBSERVER_NOT_CONFIRMED=1",
        "JPW_COCKPIT_METRIC_COUNT=7,JPW_OBSERVER_NOT_CONFIRMED=1",
    ).replace("return 0xffffff;", "return capture_background;")
    shim = shim.replace(
        "bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}",
        "bool ObjectCreate(int,const string&name,int type,int,int,int){objects[name]=Object{};objects[name].number[-1]=type;return true;}",
    )
    # Preserve each production function body. Native APIs and text metrics are
    # the only substitutes; the theme/fit/card/chrome logic is not re-created.
    signatures = [
        ("string JPWFitText", "string JPWFitText(const string text,const int available,const int font_size)"),
        ("string JPWRaizUI", "string JPWRaizUI(const string suffix)"),
        ("string JPWActionObject", "string JPWActionObject(const int action)"),
        ("bool JPWRaizCreateLabel", "bool JPWRaizCreateLabel(const string suffix,const string value,const int x,const int y,const int font_size=0)"),
        ("bool JPWCreateProtectedValue", "bool JPWCreateProtectedValue(const string suffix,const string value,const int x,const int y,const int width,const int font_size=0)"),
        ("bool JPWRaizCreateSurface", "bool JPWRaizCreateSurface(const string suffix,const int x,const int y,const int width,const int height,const color fill)"),
        ("void JPWFocusRegister", "void JPWFocusRegister(const int action)"),
        ("void JPWFocusPaint", "void JPWFocusPaint()"),
        ("bool JPWRaizCreateButton", "bool JPWRaizCreateButton(const int index,const string value,const int x,const int y,const int width)"),
    ]
    creators = "\n".join(signature + "{" + body_of(source, marker) + "}\n"
                           for marker, signature in signatures)
    renderer = body_of(source, "void JPWRenderCockpit()")
    marker = "   if(g_raiz_tab==JPW_ROUTE_OVERVIEW)\n"
    prefix = renderer[:renderer.index(marker)]
    overview = body_of(source, "if(g_raiz_tab==JPW_ROUTE_OVERVIEW)")
    footer = renderer[renderer.index("   if(g_raiz_tab==JPW_ROUTE_SETTINGS)\n"):]
    creators += "void RenderOverviewCapture(){" + prefix + overview + footer + "}\n"
    globals_and_apis = r'''
#include <codecvt>
#include <locale>
#include <sstream>
constexpr int JPW_SIGNAL_ROUTE=16;
void JPWSignalRenderBody(int,int,int,int,int){}
bool g_stops_show_pending=false,g_positions_operation_only=false;
int g_stop_button_count=0;
int InpCockpitFontSize=11,g_details_font=11,g_details_pad=8,g_details_line=24,g_details_control=32;
int g_cockpit_selected=0,g_cockpit_page=0,g_focus_action=-1,g_focus_count=0,g_focus_actions[128];
double g_factor_draft=1.5;
bool g_cockpit_pref_invalid=false,g_raiz_panel_built=false;string g_cockpit_pref_notice;
JPWPanelRect g_details_rect;
color g_details_text,g_details_surface,g_details_chrome,g_details_card,g_details_border;
string _Symbol="SYNTHETIC.H1";
std::u32string Unicode(const string&s){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.from_bytes(s);}
int StringLen(const string&s){return static_cast<int>(Unicode(s).size());}
string StringSubstr(const string&s,int from,int size){std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> c;return c.to_bytes(Unicode(s).substr(from,size));}
int StringFind(const string&s,const string&needle){const size_t i=s.find(needle);return i==string::npos?-1:static_cast<int>(i);}
string Esc(const string&s){std::ostringstream o;for(unsigned char c:s){if(c=='"'||c=='\\')o<<'\\'<<c;else if(c=='\n')o<<"\\n";else if(c<32)o<<' ';else o<<c;}return o.str();}
string RGB(long c){std::ostringstream o;o<<"rgb("<<(c&255)<<","<<((c>>8)&255)<<","<<((c>>16)&255)<<")";return o.str();}
void EmitObjects(){
 bool first=true;std::cout<<"[";
 for(const auto&entry:objects){
  const auto&p=entry.second.number;const auto&t=entry.second.text;
  auto number=[&](int key,long fallback=0){auto i=p.find(key);return i==p.end()?fallback:i->second;};
  auto text=[&](int key){auto i=t.find(key);return i==t.end()?string(""):i->second;};
  int type=(int)number(-1);int w=(int)number(OBJPROP_XSIZE),h=(int)number(OBJPROP_YSIZE);
  if(type==OBJ_LABEL){uint ww=0,hh=0;TextSetFont("Arial",-10*(int)number(OBJPROP_FONTSIZE,11),0);TextGetSize(text(OBJPROP_TEXT),ww,hh);w=(int)ww;h=(int)hh;}
  if(!first)std::cout<<",";first=false;
  std::cout<<"{\"name\":\""<<Esc(entry.first)<<"\",\"type\":\""<<(type==OBJ_BUTTON?"button":type==OBJ_LABEL?"label":"surface")
   <<"\",\"x\":"<<number(OBJPROP_XDISTANCE)<<",\"y\":"<<number(OBJPROP_YDISTANCE)<<",\"width\":"<<w<<",\"height\":"<<h
   <<",\"text\":\""<<Esc(text(OBJPROP_TEXT))<<"\",\"tooltip\":\""<<Esc(text(OBJPROP_TOOLTIP))<<"\",\"font\":"<<number(OBJPROP_FONTSIZE,11)<<",\"color\":\""<<RGB(number(OBJPROP_COLOR))
   <<"\",\"bg\":\""<<RGB(number(OBJPROP_BGCOLOR))<<"\",\"border\":\""<<RGB(number(OBJPROP_BORDER_COLOR,number(OBJPROP_COLOR)))
   <<"\",\"z\":"<<number(OBJPROP_ZORDER)<<"}";
 }
 std::cout<<"]";
}
'''
    capture_main = r'''
#include <iostream>
int main(){
 const string titles[6]={"Leverage","Floating P/L","Genesis SL","Raiz N 1W","Raiz N 2W","Stop risk"};
 const string values[6]={"2,75x","-2,62%","3,83%","2,74% · F1,5","3,87% · F1,5","125,00 SYN · 1,25% balance"};
 for(int i=0;i<6;i++){g_cockpit_snapshot.metric[i].title=titles[i];g_cockpit_snapshot.metric[i].value=values[i];
   g_cockpit_snapshot.metric[i].reason=i==3||i==4?"Calendário semanal projetado":"Dados disponíveis na amostra";
   g_cockpit_snapshot.metric[i].quality=i==3||i==4?JPW_VIEW_ESTIMATED:JPW_VIEW_CURRENT;}
 std::cout<<"{\"kind\":\"HOST_OBJECT_CAPTURE_NOT_NATIVE_MT5\",\"cases\":[";
 bool first=true;
 for(int w:{1000,390})for(bool dark:{false,true}){
   chart_width=w;chart_height=w==390?720:820;capture_background=dark?0:0xffffff;
   g_cockpit_page=0;g_raiz_tab=JPW_ROUTE_OVERVIEW;g_focus_count=0;objects.clear();RenderOverviewCapture();
   if(!first)std::cout<<",";first=false;
   std::cout<<"{\"name\":\"cockpit-"<<w<<"-"<<(dark?"dark":"light")<<"\",\"width\":"<<w<<",\"height\":"<<chart_height
    <<",\"theme\":\""<<(dark?"dark":"light")<<"\",\"objects\":";EmitObjects();std::cout<<"}";
 }
 std::cout<<"]}\n";
}
'''
    cpp = "long capture_background=0xffffff;\n" + shim + panel + enums + globals_and_apis + creators + capture_main
    with tempfile.TemporaryDirectory(prefix="jpw-cockpit-capture-") as temporary:
        path, binary = Path(temporary) / "capture.cpp", Path(temporary) / "capture"
        path.write_text(cpp, encoding="utf-8")
        result = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)],
                                text=True, capture_output=True, check=False, timeout=60)
        if result.returncode:
            print(result.stdout, end=""); print(result.stderr, end="")
            return result.returncode
        result = subprocess.run([str(binary)], text=True, capture_output=True, check=False, timeout=30)
        if result.returncode:
            print(result.stderr, end="")
            return result.returncode
    captured = json.loads(result.stdout)
    captured["sources"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (PRESENTATION, FILES[0])}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(captured, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("COCKPIT_OBJECT_CAPTURE:", destination, ";", len(captured["cases"]), "synthetic cases; native NOT_RUN")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-overview":
        raise SystemExit(capture_overview(Path(sys.argv[2])))
    raise SystemExit(main())

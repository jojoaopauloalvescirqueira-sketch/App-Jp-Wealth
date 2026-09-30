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
import tempfile

from leverage_panel_test import body_of


ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
FILES = [MQL / "Include/JPWealth/JPW_Alavancagem_Panel.mqh",
         MQL / "Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5"]

SHIM = r'''
#include <cmath>
#include <iostream>
#include <string>
using string = std::string;
using color = int;
int MathAbs(int v) { return std::abs(v); }
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
    Check(JPWPanelCockpit(width,height,760,620,cockpit),"cockpit rectangle defined");
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
  Check(!JPWPanelHUD(100,100,180,180,0,0,false,false,rejected),
        "oversized HUD rejected rather than claiming children fit a clamped container");
  const color white=255|(255<<8)|(255<<16);
  const color black=0;
  const color standard_gray=118|(118<<8)|(118<<16);
  const color pale=JPWPanelSurface(white),dark=JPWPanelSurface(black);
  Check(Contrast(JPWPanelTextColor(white,standard_gray),pale)>=4.5,
        "small gray text meets 4.5:1 on default light HUD");
  Check(Contrast(JPWPanelTextColor(black,standard_gray),dark)>=4.5,
        "small gray text meets 4.5:1 on default dark HUD");
  Check(!JPWPanelDarkBackground(white) && JPWPanelDarkBackground(black),
        "light and dark chart themes use distinct surfaces");
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
        src.write_text(SHIM + "\n" + body + "\n" + MAIN, encoding="utf-8")
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
    return presentation_layout_replay(compiler)


LAYOUT_SHIM = r'''
#include <climits>
#include <vector>
using ulong=unsigned long;
bool MathIsValidNumber(double x){return std::isfinite(x);}
string IntegerToString(long x){return std::to_string(x);}
int g_details_control=24,g_details_line=18,g_details_pad=5,g_details_font=11,g_cockpit_page=0;
bool g_cockpit_pref_invalid=false;string g_cockpit_pref_notice;
JPWCockpitSnapshot g_cockpit_snapshot;
constexpr int OBJPROP_TOOLTIP=1;
struct Drawn{int x,y,width,height;string type;};std::vector<Drawn> drawn;
bool JPWRaizCreateButton(int,const string&,int x,int y,int w){drawn.push_back({x,y,w,g_details_control,"button"});return true;}
bool JPWRaizCreateLabel(const string&,const string&,int x,int y,int=0){drawn.push_back({x,y,1,g_details_line,"label"});return true;}
bool JPWCreateProtectedValue(const string&,const string&,int x,int y,int w){drawn.push_back({x,y,w,g_details_line,"value"});return true;}
string JPWFitText(const string&s,int,int){return s;}
string JPWCockpitQualityText(int){return "Current";}
string JPWRaizUI(const string&s){return s;}
bool ObjectSetString(int,const string&,int,const string&){return true;}
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
 // The reported screenshot: 32 px measured text in a 620 px cockpit. The
 // former five-line gate needed 336 px; the actual body has only 332 px.
 JPWPanelRect rect;
 if(!JPWPanelCockpit(1440,900,760,620,rect))return 1;
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
    cpp+=shim+"void RenderOverview"+signature+"{"+overview+"}\n"+LAYOUT_MAIN
    print("PRESENTATION_LAYOUT_SOURCE_SHA256:",hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-presentation-layout-") as temporary:
        path,binary=Path(temporary)/"layout.cpp",Path(temporary)/"layout"
        path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,text=True,capture_output=True,check=False,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""R2 sidecar for three structural oracles; R1 is immutable."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from leverage_panel_test import body_of
from leverage_source import expanded_source
import leverage_host_runtime as r1
INC = r1.INC
PRESENT = r1.PRESENT
DESIGN = r1.DESIGN


def fn(source, signature):
    return signature + "{" + body_of(source, signature) + "}\n"


def cockpit_target(source):
    match = re.search(r"JPWPanelCockpit\(chart_width,chart_height,JPWUIDesignPx\((\d+)\),JPWUIDesignPx\((\d+)\),g_details_rect\)", source)
    assert match, "R2 expects explicit logical sizes passed through the real DPI helper"
    return int(match[1]), int(match[2])


def geometry(geo=None):
    geo = geo or importlib.import_module("leverage_geometry_test")
    geo.cockpit_target = cockpit_target
    original_design = geo.design_helpers
    def design(full=False):
        code = original_design(full)
        if full:
            extra = "ushort StringGetCharacter(const string&s,int i){return (unsigned char)s.at(i);}\n"
            extra += "struct JPWUIDesignTextMeasure {string label;int font;int dpi;int width;bool ready;}; JPWUIDesignTextMeasure g_jpw_ui_text_measure[128];\n"
            extra += fn(DESIGN, "uint JPWUIDesignHash(const string value)")
            code = extra + code
        return code
    geo.design_helpers = design
    width, height = cockpit_target(PRESENT)
    geo.SHIM += "\nusing ushort=unsigned short;\n" + original_design(False)
    geo.MAIN = geo.MAIN.replace("++cases;", "++cases;mock_screen_dpi=96*dpi/100;")
    geo.MAIN = geo.MAIN.replace("__COCKPIT_WIDTH__", f"JPWUIDesignPx({width})").replace("__COCKPIT_HEIGHT__", f"JPWUIDesignPx({height})")
    # Shared helper is already in SHIM for core/overview. Keep full HUD's native
    # APIs and helper loading distinct to avoid duplicate state declarations.
    geo.design_helpers = lambda full=False: design(True) if full else ""
    geo.LAYOUT_SHIM += "\nbool g_details_inventory_complete=true,g_details_content_dirty=false; string g_details_render_reason;\n"
    geo.LAYOUT_SHIM += "using ENUM_OBJECT_PROPERTY_INTEGER=int;using ENUM_OBJECT_PROPERTY_STRING=int;\n"
    geo.LAYOUT_SHIM += "bool JPWUIDesignSetInteger(const string&n,int p,long v){return ObjectSetInteger(0,n,p,v);}\n"
    geo.LAYOUT_SHIM += "bool JPWUIDesignSetString(const string&n,int p,const string&v){return ObjectSetString(0,n,p,v);}\n"
    for sig in ("void JPWPresentationFailure(const string reason)",
                "bool JPWPresentationSetInteger(const string name,const ENUM_OBJECT_PROPERTY_INTEGER property,const long value)",
                "bool JPWPresentationSetString(const string name,const ENUM_OBJECT_PROPERTY_STRING property,const string value)"):
        geo.LAYOUT_SHIM += fn(PRESENT, sig)
    # The original fixture's overview creator APIs stay explicit boundaries.
    # The HUD, in contrast, receives the real retained-object implementation.
    geo.HUD_SHIM = geo.HUD_SHIM.replace("using uint=unsigned int;", "using uint=unsigned int;using ushort=unsigned short;using ulong=unsigned long;")
    geo.HUD_SHIM = geo.HUD_SHIM.replace("OBJPROP_BMPFILE=21;", "OBJPROP_BMPFILE=21,OBJPROP_STATE=22;")
    geo.HUD_SHIM = geo.HUD_SHIM.replace("bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]=Object{};return true;}",
        "bool ObjectCreate(int,const string&name,int type,int,int,int){objects[name]=Object{};objects[name].number[-1]=type;return true;}")
    # Setter failure is represented when the native object does not exist.
    geo.HUD_SHIM = geo.HUD_SHIM.replace("objects[name].number[property]=value;", "if(!objects.count(name))return false;objects[name].number[property]=value;")
    geo.HUD_SHIM = geo.HUD_SHIM.replace("objects[name].text[property]=value;", "if(!objects.count(name))return false;objects[name].text[property]=value;")
    geo.HUD_SHIM += "\nint StringFind(const string&s,const string&needle){auto p=s.find(needle);return p==string::npos?-1:(int)p;}\n"
    geo.HUD_SHIM += "\nbool g_details_content_dirty=false;\n" + PRESENT[PRESENT.index("const int JPW_FOCUS_SIGNAL_ROLE"):PRESENT.index("void JPWInvalidateDialogContent(")]
    geo.HUD_SHIM += "ushort StringGetCharacter(const string&s,int i){return (unsigned char)s.at(i);}\n" + r1.ui_primitives()
    # ui_primitives already supplies Hash; design measurement only needs cache.
    geo.design_helpers = lambda full=False: (design(True).replace("ushort StringGetCharacter(const string&s,int i){return (unsigned char)s.at(i);}\n", "").replace(fn(DESIGN,"uint JPWUIDesignHash(const string value)"), "") if full else "")
    for sig in ("bool JPWPresentationDialogObject(const string name)", "bool JPWPresentationKeep(const string name)",
                "bool JPWPresentationEnsure(const string name,const ENUM_OBJECT kind)",
                "void JPWPresentationFailure(const string reason)",
                "bool JPWPresentationSetInteger(const string name,const ENUM_OBJECT_PROPERTY_INTEGER property,const long value)",
                "bool JPWPresentationSetString(const string name,const ENUM_OBJECT_PROPERTY_STRING property,const string value)"):
        geo.HUD_SHIM += fn(PRESENT, sig)
    geo.HUD_SHIM += "void JPWClearPanel();void JPWUIDesignDeleteIcon(const string name);int JPWUIDesignPx(const int logical);color JPWPanelTextColor(const color chart_background,const color requested);\n" + fn(PRESENT, "void JPWHUDUnavailable(const string reason)")
    geo.HUD_MAIN = geo.HUD_MAIN.replace("16*8+24+24+2*8", "16*8+24+20+8+2*8")
    geo.HUD_MAIN = geo.HUD_MAIN.replace(
        'if(insufficient.width!=-1||objects.count(cockpit_button)||g_panel_count!=0)',
        'if(!InBounds(insufficient,200,160)||!objects.count(cockpit_button)||objects[g_panel_prefix+"RAIZ_UI_HUD_LABEL"].text[OBJPROP_TEXT]!="Conta")')
    geo.HUD_MAIN = geo.HUD_MAIN.replace("FAIL insufficient large-font HUD retained a stale click target", "FAIL compact account caption failed to preserve a bounded live access target")
    geo.HUD_MAIN = geo.HUD_MAIN.replace("chart_width=200;chart_height=160;JPWRenderHUD();", "chart_width=20;chart_height=20;JPWRenderHUD();")
    geo.HUD_MAIN = geo.HUD_MAIN.replace(' std::cout<<"HOST_HEADER_RESERVE:',r'''
 mock_screen_dpi=96;InpFontSize=8;DrawHUD(800,400,0,0,false);g_cockpit_prefs.visible_mask=0;JPWRenderHUD();
 if(!g_hud_summary||g_hud_summary_source!=-1||!objects.count(g_panel_prefix+"RAIZ_DETAILS_BUTTON")){
  std::cerr<<"FAIL all-hidden preference lost the real account launcher\n";return 1;}
 if(!VerifyTinyCockpit()){return 1;}
 int financial_cases=0;
 for(int percent:{100,125,150,200})for(int width:{160,200,320,800,1600})for(int corner:{0,1,2,3}){
  mock_screen_dpi=96*percent/100;InpFontSize=8;
  DrawHUD(width,1000,corner,0,false);
  g_cockpit_prefs.visible_mask=127;
  for(int i=0;i<7;i++){g_cockpit_snapshot.metric[i].value="123456789012345678901234567890,12";g_cockpit_snapshot.metric[i].quality=JPW_VIEW_CURRENT;}
  JPWRenderHUD();
  for(int i=0;i<7;i++){
   const string object=g_panel_prefix+IntegerToString(i);
   if(!objects.count(object))continue;
   const string shown=objects[object].text[OBJPROP_TEXT];
   const bool full=shown.find(g_cockpit_snapshot.metric[i].value)!=string::npos;
   const bool named=shown.find("Cockpit")!=string::npos||shown=="JPW"||shown=="JPW · Abrir Conta";
   if(!full&&!named){std::cerr<<"FAIL financial label was truncated or replaced with an unexplained number\n";return 1;}
   uint measured=0,h=0;TextSetFont("Arial",-10*InpFontSize,FW_NORMAL);TextGetSize(shown,measured,h);
   const int x=objects[object].number[OBJPROP_XDISTANCE];
   if(x<0||x+(int)measured>width){std::cerr<<"FAIL measured financial label escaped chart\n";return 1;}
  }
  if(g_panel_count>0&&!objects.count(g_panel_prefix+"RAIZ_DETAILS_BUTTON")){std::cerr<<"FAIL visible financial labels have no detail target\n";return 1;}
  financial_cases++;
 }
 std::cout<<"HUD_FINANCIAL_LABELS: "<<financial_cases<<" seven-metric/DPI/corner cases PASS\n";
 std::cout<<"HOST_HEADER_RESERVE:''')
    def hud_replay(compiler):
        panel=geo.FILES[0].read_text()
        panel=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),panel)
        # Same explicit bitmap boundary as the historical fixture.
        decoration='bool JPWUIDesignIcon(const string name,const int x,const int y,const int size,const color,const bool){ObjectCreate(0,name,4,0,0,0);ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x);ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y);ObjectSetInteger(0,name,OBJPROP_XSIZE,size);ObjectSetInteger(0,name,OBJPROP_YSIZE,size);return true;}\nvoid JPWUIDesignDeleteIcon(const string name){ObjectDelete(0,name);}\n'
        runtime=fn(PRESENT,"void JPWClearPanel()")+fn(PRESENT,"void JPWRenderHUDBody()")+fn(PRESENT,"void JPWRenderHUD()")
        cpp=geo.HUD_SHIM+geo.design_helpers(True)+decoration+panel+runtime+tiny_cockpit()+geo.HUD_MAIN
        return compile_cpp(cpp,"hud",compiler)
    geo.hud_layout_replay=hud_replay
    return geo


def tiny_cockpit():
    source=expanded_source(ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5')
    signatures=("string JPWRaizUI(const string suffix)","string JPWActionObject(const int action)",
                "string JPWFitText(const string text,const int available,const int font_size)",
                "void JPWFocusRegister(const int action)",
                "bool JPWRaizCreateButton(const int index,const string value,\n                          const int x,const int y,const int width)",
                "bool JPWRaizCreateLabel(const string suffix,const string value,\n                        const int x,const int y,const int font_size=0)")
    creators=''.join(fn(PRESENT,s) for s in signatures)
    constants=[]
    for name in sorted(set(re.findall(r'\bJPW_(?:ACTION|ROUTE|SIGNAL)_\w+',creators))|{'JPW_ACTION_CLOSE'}):
        if name=='JPW_ROUTE_SETTINGS':continue
        match=re.search(r'\b'+name+r'\s*(?:=\s*|\s+)(-?\d+)',source)
        assert match,name
        constants.append(f'constexpr int {name}={match[1]};')
    extra='\n'.join(constants)+r'''
int InpCockpitFontSize=11,g_details_font=11,g_details_control=32,g_details_pad=8,g_details_line=24;
int g_stop_button_count=0,g_details_focus_route=-1,g_focus_action=-1,g_focus_count=0,g_focus_actions[128];
bool g_raiz_panel_built=false,g_editing_field=false;double g_factor_draft=1.5;
color g_details_text=0,g_details_surface=0,g_details_chrome=0,g_details_card=0,g_details_border=0;
JPWPanelRect g_details_rect;
string StringSubstr(const string&s,int start,int count){return s.substr(start,count);}
'''
    for sig in ("color JPWUIDesignPrimaryFill(const color background)","color JPWUIDesignPrimaryInk(const color background)"):
        extra+=re.sub(r"C'(\d+),(\d+),(\d+)'",lambda m:str(int(m[1])|(int(m[2])<<8)|(int(m[3])<<16)),fn(DESIGN,sig))
    prefix=body_of(PRESENT,"void JPWRenderCockpit()")
    prefix=prefix[:prefix.index("   // Stable visual regions")]
    extra+=creators+"void RenderTinyCockpit(){"+prefix+"}\n"
    extra+=r'''
bool VerifyTinyCockpit(){
 int cases=0;
 for(int percent:{100,125,150,200})for(int width:{120,160,220})for(int height:{80,100,120}){
  mock_screen_dpi=96*percent/100;chart_width=width;chart_height=height;objects.clear();
  g_details_render_reason="";g_raiz_details_open=true;g_raiz_tab=7;g_focus_count=0;
  RenderTinyCockpit();const string name=JPWActionObject(JPW_ACTION_CLOSE);
  if(!objects.count(name)){std::cerr<<"FAIL tiny cockpit lost close control\n";return false;}
  const auto &n=objects[name].number;
  if(n.at(OBJPROP_XDISTANCE)<0||n.at(OBJPROP_YDISTANCE)<0||n.at(OBJPROP_XSIZE)<=0||n.at(OBJPROP_YSIZE)<=0||
     n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)>width||n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)>height){
    std::cerr<<"FAIL tiny cockpit close escapes viewport\n";return false;}
  bool registered=false;for(int i=0;i<g_focus_count;i++)if(g_focus_actions[i]==JPW_ACTION_CLOSE)registered=true;
  if(!registered||objects[name].number[-1]!=OBJ_BUTTON){std::cerr<<"FAIL tiny close lacks real button/focus registration\n";return false;}
  cases++;
 }
 g_raiz_details_open=false;
 std::cout<<"TINY_COCKPIT_ACCESS: "<<cases<<" DPI/viewport cases PASS\n";return true;
}
'''
    return extra


def compile_cpp(cpp,name,compiler=None):
    compiler=compiler or shutil.which("clang++") or shutil.which("g++")
    assert compiler,"ENVIRONMENT_ERROR: compiler missing"
    with tempfile.TemporaryDirectory(prefix=f"r2-{name}-") as folder:
        path=Path(folder)/f"{name}.cpp";binary=Path(folder)/name;path.write_text(cpp)
        for command in ([compiler,"-std=c++17","-Wall","-Wextra",str(path),"-o",str(binary)],[str(binary)]):
            result=subprocess.run(command,capture_output=True,text=True,timeout=60)
            print(result.stdout,end="");print(result.stderr,end="")
            if result.returncode:return result.returncode
    return 0


def stop_ui(module=None):
    module=module or importlib.import_module("leverage_stop_ui_test")
    # Versioned one-line criterion change. The old destroy-only assertion stays
    # in tools/. The replacement requires both refresh routes, with the actual
    # monitor->sample->presentation path independently executed below.
    code=inspect.getsource(module.main).replace("def main()", "def candidate_main()")
    old='assert "JPWRaizPanelDestroy();" in display'
    new='assert "JPWInvalidateDialogContent(JPW_ROUTE_STOPS);" in display and "JPWInvalidateDialogContent(JPW_ROUTE_STOP_ROW);" in display'
    assert code.count(old)==1;code=code.replace(old,new)
    state=PRESENT[PRESENT.index("const int JPW_FOCUS_SIGNAL_ROLE"):PRESENT.index("void JPWInvalidateDialogContent(")]
    module.SHIM+="\nbool g_details_content_dirty=false;\n"+state
    module.SHIM+="int ObjectFind(int,const string&name){for(auto&s:objects)if(s==name)return 0;return -1;}\n"
    module.SHIM+=DESIGN[DESIGN.index("#define JPW_UI_PROPERTY_SLOTS"):DESIGN.index("uint JPWUIDesignHash(")]
    for sig in ("void JPWUIDesignForget(const string name)","bool JPWUIDesignDelete(const string name)"):
        module.SHIM+=fn(DESIGN,sig)
    module.SHIM+=fn(PRESENT,"bool JPWPresentationDialogObject(const string name)")
    exec(compile(code,"<candidate-stop-ui-original-main>","exec"),module.__dict__)
    first=module.candidate_main()
    second=stop_refresh_replay()
    return first or second


def panel(module=None):
    module=module or importlib.import_module("leverage_panel_test")
    # Rewrite only the explicit versioned literals below in the candidate
    # functions. Source inspection remains source inspection, supplemented by
    # the actual geometry runtime; no false require is swallowed.
    replacements={
      'observer_missing ? "Risk: N/A · Check Observer"':'observer_missing ? "Risk: N/A · Ver Monitor"',
      "'Open Cockpit'":"'Abrir Conta'",
      'const int height=active*row_height+button_height+3*pad;':'int height=active*row_height+button_height+3*pad;',
      'ObjectSetString(0,name,OBJPROP_TEXT,shown[i])':'JPWPresentationSetString(name,OBJPROP_TEXT,shown[i])',
      "'Click for details.'":"'Clique para ver detalhes.'",
      'ObjectDelete(0,g_panel_prefix+IntegerToString(i))':'JPWUIDesignDelete(g_panel_prefix+IntegerToString(i))',
      'JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();':'JPWRaizSaveVisibleFields(); JPWInvalidateDialogContent();',
      'StringFind(name,owned)==0':'JPWPresentationDialogObject(name)',
    }
    for name in ('check_narrow_chart','check_six_labels_and_lifecycle','check_same_chart_dialog_cleanup','check_cockpit_navigation'):
        code=inspect.getsource(getattr(module,name))
        for before,after in replacements.items():code=code.replace(before,after)
        if name=='check_same_chart_dialog_cleanup':code=code.replace('ObjectDelete(0,name)','JPWUIDesignDelete(name)')
        if name=='check_cockpit_navigation':
            code=code.replace(r'JPWPanelCockpit\(chart_width,chart_height,(\d+),(\d+),g_details_rect\)',r'JPWPanelCockpit\(chart_width,chart_height,JPWUIDesignPx\((\d+)\),JPWUIDesignPx\((\d+)\),g_details_rect\)')
        exec(compile(code,'<candidate-panel-'+name+'>','exec'),module.__dict__)
    # Expand only real forwarding wrappers and retain wrapper text as evidence.
    original_body=module.body_of
    delegates={'void JPWRenderHUD()':'void JPWRenderHUDBody()',
               'void JPWHandleChartEvent(':'void JPWHandleChartEventBody(',
               'void JPWRenderRaizDetails()':'void JPWRenderRaizDetailsBody()'}
    def delegated(source,signature):
        result=original_body(source,signature)
        if signature in delegates:result+='\n'+original_body(source,delegates[signature])
        return result
    module.body_of=delegated
    module.main()
    # Runtime coverage is shared with geometry, not inferred from token checks.
    return geometry().main() or 0


def stop_refresh_replay():
    rel=r1.presentation_adapter()
    samples=(INC/'JPW_Alavancagem_Samples.mqh').read_text()
    source=expanded_source(ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5')
    runtime=rel.presentation_runtime(source,samples)
    coordinator=(INC/'JPW_Alavancagem_Coordinator.mqh').read_text()
    boundary=r'''
constexpr int JPW_ROUTE_OVERVIEW=7,JPW_ROUTE_SETTINGS=10,JPW_ROUTE_STOPS=11,JPW_ROUTE_STOP_ROW=14;
constexpr int JPW_OBSERVER_CONTEXT_UNAVAILABLE=2,JPW_DIAG_QUALITY_CHANGED=1,JPW_DIAG_DATA_UNAVAILABLE=2;
bool g_raiz_details_open=true,g_details_content_dirty=false,g_stop_ready=true,g_stop_scope_valid=true;
bool g_account_known=true,g_genetrix_ledger_available=false;
int g_raiz_tab=JPW_ROUTE_STOPS,g_stop_observer_presence=0;
double g_numeric_values[7]={},g_stop_total_money=0;bool g_numeric_valid[7]={};long g_source_times[7]={};int g_metric_last_quality[7]={};
int g_compensated_quality=0;
struct Stamp{long observed_utc=0,observed_mono_ms=0;}g_stop_sample,g_genetrix_view;
struct JPWAccount{int id=1;};JPWAccount g_account;
bool account_matches=true,inside_budget=true;
int history_reads=0,row_rebinds=0,identity_invalidations=0,ledger_reads=0,inventory_reads=0;
string g_diagnostic_context="synthetic-account";
bool JPWCoordinatorBudgetRemaining(){return inside_budget;}
bool JPWReadAccount(JPWAccount&a){a.id=account_matches?1:2;return true;}
bool JPWAccountsEqual(JPWAccount&a,JPWAccount&b){return a.id==b.id;}
void JPWInvalidateIdentityPresentation(){identity_invalidations++;}
void JPWPositionsMonitorInventory(){inventory_reads++;}
void JPWDetailsReadStopRisk(){history_reads++;}
void JPWStopRiskRefreshRowView(){row_rebinds++;}
void JPWGenetrixCollectLedger(){ledger_reads++;}
void JPWQueueDiagnostic(int){}
long TimeGMT(){return 1000;}
int g_focus_action=17;bool g_editing_field=true;string draft="unsaved exact draft";
struct Capture{bool ready;double money;string value;long observed;};
Capture fixture{true,10,"10,00",1000};
void JPWStopRiskUnavailable(const string reason);
void JPWCollectStopRisk(){
 if(!fixture.ready){JPWStopRiskUnavailable("fixture unavailable");return;}
 g_stop_ready=true;g_stop_scope_valid=true;g_stop_total_money=fixture.money;
 g_stop_value=fixture.value;g_stop_reason="synthetic observed source";g_stop_quality=JPW_VIEW_CURRENT;
 g_stop_sample.observed_utc=1000;g_stop_sample.observed_mono_ms=fixture.observed;
}
'''
    main=r'''
int checks=0,failures=0;void check(bool ok,const char*m){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<m<<"\n";}}
int main(){
 g_sample_context="synthetic-account";g_panel_prefix="synthetic";
 for(int route:{JPW_ROUTE_STOPS,JPW_ROUTE_STOP_ROW,JPW_ROUTE_SETTINGS}){
  g_raiz_tab=route;g_details_content_dirty=false;g_stop_ready=true;host_now=1000;
  fixture={true,10,"10,00",1000};JPWMonitorStopRisk();JPWRenderCurrentDisplay();
  check(g_cockpit_snapshot.metric[5].value=="10,00"&&g_cockpit_snapshot.metric[5].quality==JPW_VIEW_CURRENT&&g_cockpit_snapshot.metric[5].sample.numeric_value==10,"first capture reaches actual Stop presentation");
  g_details_content_dirty=false;fixture={true,25,"25,00",1100};host_now=1100;JPWMonitorStopRisk();JPWRenderCurrentDisplay();
  check(g_cockpit_snapshot.metric[5].value=="25,00"&&g_cockpit_snapshot.metric[5].sample.numeric_value==25,"new capture replaces old Stop number");
  check(g_details_content_dirty==(route==JPW_ROUTE_STOPS||route==JPW_ROUTE_STOP_ROW),"only Stops routes are marked for refresh");
  fixture.ready=false;g_details_content_dirty=false;JPWMonitorStopRisk();JPWRenderCurrentDisplay();
  check(g_cockpit_snapshot.metric[5].value=="N/A"&&g_cockpit_snapshot.metric[5].quality==JPW_VIEW_NA&&!g_cockpit_snapshot.metric[5].sample.has_value,"unavailable source removes stale Stop number and Current");
  check(g_focus_action==17&&g_editing_field&&draft=="unsaved exact draft","periodic monitor preserves editing focus and unsaved draft");
 }
 check(history_reads==2,"last-snapshot requests occur only on current-to-unavailable transition in Stops routes");
 g_raiz_tab=JPW_ROUTE_STOPS;g_details_content_dirty=false;g_raiz_details_open=false;
 fixture={true,50,"50,00",1200};host_now=1200;JPWMonitorStopRisk();JPWRenderCurrentDisplay();
 check(!g_details_content_dirty&&g_cockpit_snapshot.metric[5].value=="50,00","closed dialog still updates metric without invalidating hidden content");
 host_now=31201;JPWRenderCurrentDisplay();
 check(g_cockpit_snapshot.metric[5].value=="N/A"&&g_cockpit_snapshot.metric[5].quality==JPW_VIEW_NA,"expired observer sample cannot survive redraw as Current");
 std::cout<<"STOP_REFRESH_PRESENTATION: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native controls NOT_RUN\n";return failures?1:0;
}
'''
    cpp=rel.SHIM+runtime+boundary+r1.invalidate()
    for sig in ("void JPWStopRiskUnavailable(const string reason)","void JPWAcceptMetric(const int metric)","void JPWMonitorStopRisk()"):
        cpp+=fn(coordinator,sig)
    return compile_cpp(cpp+main,"stop-refresh")

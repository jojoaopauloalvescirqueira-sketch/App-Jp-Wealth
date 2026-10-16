#!/usr/bin/env python3
"""Real HUD/retained-object/click-branch replay; chart/text/raster APIs are host seams.
Catches bare-label targets, undersized/overlapping controls, stale owned objects,
mask reinterpretation, summary routing and financial token truncation. MT5 NOT_RUN.
"""
from pathlib import Path
import shutil
import leverage_host_layout as host
from leverage_panel_test import body_of

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'


def main():
    geo = host.geometry()
    actions = (INC/'JPW_Alavancagem_Actions.mqh').read_text()
    cockpit = (INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
    start = actions.index('   if(sparam==g_panel_prefix+"HUD_RISK_SCOPE")')
    stop = actions.index('   if(sparam==g_panel_prefix+"RAIZ_DETAILS_BUTTON")', start)
    routing = r'''
const int JPW_ROUTE_METRIC=6,JPW_ROUTE_OVERVIEW=7;
int g_cockpit_selected=-1,opened=-99;
void JPWOpenCockpit(int target){opened=target;g_cockpit_selected=target;g_raiz_details_open=true;}
void JPWRaizSwitchTab(int route){g_raiz_tab=route;}
'''
    routing += host.fn(cockpit, 'int JPWCockpitHUDTarget(const bool summary,const int summary_source,const int object_index)')
    routing += 'void HUDAction(const string sparam){\n'+actions[start:stop]+'}\n'
    routing += r'''
void HUDClick(const string sparam){
 scope_clock_ms+=300;string route;
 auto &n=objects[sparam].number;long x=n[OBJPROP_XDISTANCE]+n[OBJPROP_XSIZE]/2;double y=n[OBJPROP_YDISTANCE]+n[OBJPROP_YSIZE]/2;
 if(JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route)&&route!="")HUDAction(route);
}
'''
    routing += host.fn(actions, 'bool JPWCockpitOwnedSuffix(const string suffix)')
    geo.HUD_MAIN = geo.HUD_MAIN[:geo.HUD_MAIN.index('int main(){')] + routing + r'''
int failures=0,checks=0;bool oracle_negative=false;
void Check(bool ok,const string&why){checks++;if(!ok){if(!oracle_negative&&failures<12)std::cerr<<"FAIL "<<why<<"\n";failures++;}}
bool Interactive(const string&name){
 if(name==g_panel_prefix+"HUD_RISK_SCOPE"||name==g_panel_prefix+"RAIZ_DETAILS_BUTTON")return true;
 for(int i=0;i<7;i++)if(name==g_panel_prefix+IntegerToString(i))return true;
 return false;
}
void Targets(){
 const int minimum=(36*mock_screen_dpi+48)/96,space=(4*mock_screen_dpi+48)/96;
 std::vector<string> targets;
 for(const auto&kv:objects)if(Interactive(kv.first)){
  const auto &n=kv.second.number;
  Check(n.count(-1)&&(n.at(-1)==OBJ_BUTTON||n.at(-1)==OBJ_BITMAP_LABEL),"interactive object must have a sizeable native bitmap/button region: "+kv.first);
  if(!n.count(OBJPROP_XSIZE)||!n.count(OBJPROP_YSIZE)){Check(false,"interactive object lacks hit-region geometry: "+kv.first);continue;}
  const int x=n.at(OBJPROP_XDISTANCE),y=n.at(OBJPROP_YDISTANCE),w=n.at(OBJPROP_XSIZE),h=n.at(OBJPROP_YSIZE);
  Check(WindowTextValid(kv.first,space),"nonempty bitmap/native text with complete emitted extents and opaque ink: "+kv.first);
  Check(w>=minimum&&h>=minimum,"target is at least36 logical in both axes: "+kv.first);
  Check(x>=0&&y>=0&&x+w<=chart_width&&y+h<=chart_height,"hit region remains inside chart: "+kv.first);
  Check(objects.count(g_panel_prefix+"HUD_BG"),"interactive HUD has owned backdrop");
  if(objects.count(g_panel_prefix+"HUD_BG")){
   const auto &b=objects.at(g_panel_prefix+"HUD_BG").number;
   Check(x>=b.at(OBJPROP_XDISTANCE)&&y>=b.at(OBJPROP_YDISTANCE)&&x+w<=b.at(OBJPROP_XDISTANCE)+b.at(OBJPROP_XSIZE)&&y+h<=b.at(OBJPROP_YDISTANCE)+b.at(OBJPROP_YSIZE),"target contained in HUD backdrop");
  }
  for(const string&prior:targets){const auto&p=objects.at(prior).number;
   Check(x+w+space<=p.at(OBJPROP_XDISTANCE)||p.at(OBJPROP_XDISTANCE)+p.at(OBJPROP_XSIZE)+space<=x||y+h+space<=p.at(OBJPROP_YDISTANCE)||p.at(OBJPROP_YDISTANCE)+p.at(OBJPROP_YSIZE)+space<=y,"distinct target regions have4 logical separation");
  }
  targets.push_back(kv.first);
 }
}
int main(){
 // Adversarial oracle regressions: same real draw, corrupt only observations.
 mock_screen_dpi=96;InpFontSize=10;DrawHUD(1600,1200,0,0,false);
 const string victim=g_panel_prefix+"0",resource=victim+"_ARGB";
 const auto original_object=objects.at(victim);const auto original_text=host_window_text.at(resource);const auto original_pixels=host_window_resources.at(resource);
 auto rejected=[&](){int before=failures;oracle_negative=true;Targets();oracle_negative=false;bool detected=failures>before;failures=before;return detected;};
 host_window_text.erase(resource);Check(rejected(),"oracle rejects bitmap without emitted text");host_window_text[resource]=original_text;
 host_window_resources.erase(resource);Check(rejected(),"oracle rejects bitmap without resource");host_window_resources[resource]=original_pixels;
 objects[victim].number[-1]=OBJ_BUTTON;objects[victim].number[OBJPROP_FONTSIZE]=10;objects[victim].text[OBJPROP_TEXT]="";host_window_text.erase(resource);
 Check(rejected(),"oracle rejects empty native fallback text");
 objects[victim].text[OBJPROP_TEXT]=string(120,'9');Check(rejected(),"oracle rejects clipped native fallback text");
 objects[victim]=original_object;host_window_text[resource]=original_text;
 // Exact long financial payload in a valid rectangle must not excuse overflow.
 host_window_text[resource][0].text="123456789012345678901234567890,12";
 host_window_text[resource][0].font=40;
 Check(rejected(),"oracle rejects exact long numeric payload extending outside bitmap");host_window_text[resource]=original_text;
 if(failures)return 1;
 const int cached_text=host_window_text_calls,cached_resources=host_window_resource_calls;
 JPWRenderHUD();Targets();Check(host_window_text_calls==cached_text&&host_window_resource_calls==cached_resources,"cache reuse keeps original nonempty text/resource observations");
 for(int failure_kind:{0,1}){
  host_window_resource_fail=failure_kind==0;host_window_text_fail=failure_kind==1;
  DrawHUD(1600,1200,0,0,false);Targets();
  Check(objects[victim].number[-1]==OBJ_BUTTON,"native failure uses actual opaque button fallback");
  Check(objects[victim].text[OBJPROP_TOOLTIP].find("2,75x")!=string::npos,"fallback preserves exact leverage tooltip");
  Check(WindowTextValid(victim,4),"actual failure fallback text is nonempty and fits");
  host_window_resource_fail=false;host_window_text_fail=false;JPWRenderHUD();Targets();
  Check(objects[victim].number[-1]==OBJ_BITMAP_LABEL&&WindowTextValid(victim,4),"resource/text recovery restores observed bitmap text");
 }
 if(failures)return 1;
 // One large, default-font fixture guarantees the original defect is exercised.
 mock_screen_dpi=96;InpFontSize=10;DrawHUD(1600,1200,0,0,false);Targets();

 // Existing label IDs from the previous draw/version must become real targets.
 for(int i=0;i<7;i++)ObjectCreate(0,g_panel_prefix+IntegerToString(i),OBJ_LABEL,0,0,0);
 ObjectCreate(0,g_panel_prefix+"HUD_RISK_SCOPE",OBJ_LABEL,0,0,0);
 g_cockpit_prefs.visible_mask=127;JPWRenderHUD();Targets();
 int cases=0;
 for(int dpi:{96,120,144,192})for(int font:{8,10,24,40})for(int mask=0;mask<128;mask++)for(int viewport=0;viewport<4;viewport++){
  mock_screen_dpi=dpi;InpFontSize=font;g_raiz_details_open=false;
  int widths[4]={20,160,800,1600},heights[4]={20,100,400,1200};
  DrawHUD(widths[viewport],heights[viewport],mask%4,mask%2,false);
  g_cockpit_prefs.visible_mask=mask;
  g_stop_ready=true;g_stop_scope_valid=true;g_stop_scope_symbol="EURUSD";g_stop_scope_side=1;
  g_stop_sample.account_key=g_diagnostic_context;g_stop_sample.observed_mono_ms=1000;g_stop_sample.row_count=1;g_stop_rows={1};g_stop_quality=1;
  g_cockpit_snapshot.metric[5].value="125,50 USD · 1,25% balance";
  g_cockpit_snapshot.metric[6].title="Completeness";g_cockpit_snapshot.metric[6].value="N/A";
  JPWRenderHUD();Targets();
  Check(g_cockpit_prefs.visible_mask==mask,"paint respects every valid mask including zero");
  if(mask==0)Check(g_hud_summary_source==-1&&!objects.count(g_panel_prefix+"5")&&!objects.count(g_panel_prefix+"HUD_RISK_SCOPE"),"maskzero exposes no hidden numeric metric or risk scope");
  bool any_metric=false;for(int i=0;i<7;i++)any_metric=any_metric||objects.count(g_panel_prefix+IntegerToString(i));
  if(any_metric){
   int last_y=-1;int order[7]={0,5,1,2,3,4,6};
   for(int i:order){const string name=g_panel_prefix+IntegerToString(i);
    Check(bool(objects.count(name))==bool(mask&(1<<i)),"list respects canonical mask bits");
    if(objects.count(name)){int y=objects[name].number[OBJPROP_YDISTANCE];Check(y>last_y,"priority map retains0/5 then canonical remaining metrics");last_y=y;}
   }
  }
  const auto first=objects;JPWRenderHUD();
  Check(objects.size()==first.size(),"repeated draw creates no duplicate targets");
  for(const auto&kv:first)Check(objects.count(kv.first)&&objects.at(kv.first).number==kv.second.number&&objects.at(kv.first).text==kv.second.text,"retained redraw preserves target geometry and text");
  ObjectCreate(0,"FOREIGN_STUDY",OBJ_LABEL,0,0,0);JPWClearPanel();
  Check(objects.size()==1&&objects.count("FOREIGN_STUDY"),"close removes every owned target and preserves foreign study");
  JPWRenderHUD();Targets();ObjectDelete(0,"FOREIGN_STUDY");
  cases++;
 }
 // Short charts retain explicit Conta access, with no fabricated metric summary.
 for(int mask:{1,32}){
  mock_screen_dpi=96;InpFontSize=10;g_raiz_details_open=false;DrawHUD(800,105,0,0,false);g_cockpit_prefs.visible_mask=mask;JPWRenderHUD();
  Check(objects.count(g_panel_prefix+"RAIZ_DETAILS_BUTTON")&&!objects.count(g_panel_prefix+"0")&&!objects.count(g_panel_prefix+"5"),"short chart retains Conta without fabricated metric");
 }
 // Compact defaults expose only canonical0/5 according to unchanged mask bits.
 DrawHUD(1600,1200,0,0,false);JPWStoikusVisualDefault(g_stoikus_visual);g_cockpit_prefs.visible_mask=127;JPWRenderHUD();
 Check(g_stoikus_hud.width==280,"default logical width280 at DPI96");
 for(int i=0;i<7;i++)Check(bool(objects.count(g_panel_prefix+IntegerToString(i)))==(i==0||i==5),"default Compact subset0/5");
 g_raiz_details_open=false;DrawHUD(1600,1200,0,0,false);g_cockpit_prefs.visible_mask=127;JPWRenderHUD();
 for(int i=0;i<7;i++){g_raiz_details_open=false;HUDClick(g_panel_prefix+IntegerToString(i));Check(opened==i,"original metric ID routes to its canonical detail");}
 for(bool open:{false,true}){g_raiz_details_open=open;g_cockpit_selected=-1;HUDClick(g_panel_prefix+"HUD_RISK_SCOPE");Check(g_cockpit_selected==5,"risk scope click shares risk destination open or closed");}
 Check(JPWCockpitOwnedSuffix("HUD_RISK_SCOPE"),"scope target is recognized by stale-instance ownership cleanup");
 Check(!JPWCockpitOwnedSuffix("HUD_RISK_SCOPE_FOREIGN"),"ownership remains exact");
 std::cout<<"HUD_TARGETS: "<<cases<<" DPI/font/mask/viewport cases, "<<checks<<" checks, "<<failures<<" failures; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''
    return geo.hud_layout_replay(shutil.which('clang++') or shutil.which('g++'))


if __name__ == '__main__':
    raise SystemExit(main())

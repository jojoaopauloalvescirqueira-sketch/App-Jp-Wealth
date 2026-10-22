#!/usr/bin/env python3
"""Strict actual HUD caption extents, controls and opaque fallback. MT5 NOT_RUN.
Native text/raster APIs are observable host seams; render and surface code are real.
"""
import shutil
from pathlib import Path
import leverage_host_layout as host


def main():
    geo = host.geometry()
    inc=Path(__file__).resolve().parents[1]/"mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
    actions=(inc/"JPW_Alavancagem_Actions.mqh").read_text()
    cockpit=(inc/"JPW_Alavancagem_Cockpit.mqh").read_text()
    start=actions.index('   if(sparam==g_panel_prefix+"HUD_RISK_SCOPE")')
    stop=actions.index('   if(sparam==g_panel_prefix+"RAIZ_DETAILS_BUTTON")',start)
    routing='''
const int JPW_ROUTE_METRIC=6,JPW_ROUTE_OVERVIEW=7,JPW_ROUTE_SYSTEM=13;
int g_cockpit_selected=-1,opened=-99;
void JPWOpenCockpit(int target=-1){opened=target;g_cockpit_selected=target;g_raiz_details_open=true;}
void JPWRaizSwitchTab(int route){g_raiz_tab=route;}
'''
    routing+=host.fn(cockpit,'int JPWCockpitHUDTarget(const bool summary,const int summary_source,const int object_index)')
    routing+='void HUDAction(const string sparam){'+actions[start:stop]+'}\n'
    geo.HUD_MAIN = geo.HUD_MAIN[:geo.HUD_MAIN.index('int main(){')] + routing + r'''
int main(){
 int checks=0,failures=0,cases=0,expanded_cases=0,collapsed_cases=0;
 auto check=[&](bool ok,const string &why){checks++;if(!ok){if(failures<20)std::cerr<<"FAIL "<<why<<"\n";failures++;}};
 check(StringLen("ação → fim")==10&&StringGetCharacter("ação → fim",1)==231&&StringGetCharacter("ação → fim",5)==8594,"Unicode BMP length and character indexes");
 check(StringSubstr("ação → fim",1,3)=="ção"&&StringSubstr("ação → fim",7)=="fim"&&StringFind("ação → fim","fim",6)==7,"Unicode BMP substring and find indexes agree");
 check(StringLen("A😀é")==4&&StringGetCharacter("A😀é",1)==0xD83D&&StringGetCharacter("A😀é",2)==0xDE00&&StringSubstr("A😀é",1,2)=="😀"&&StringFind("A😀é","é")==3,"UTF16 surrogate pair indexing and whole-pair roundtrip");
 bool unicode_eviction_ok=true;
 for(int i=0;i<2050;i++){const string prefix="cache"+IntegerToString(i);const string sample=prefix+"😀é";unicode_eviction_ok=unicode_eviction_ok&&StringFind(sample,"😀")==StringLen(prefix)&&StringSubstr(sample,StringLen(prefix),2)=="😀";}
 check(unicode_eviction_ok,"bounded UTF16 cache eviction preserves substring and two-operand find results");
 for(int dpi:{96,120,144,192}){mock_screen_dpi=dpi;TextSetFont("Arial",-100,FW_NORMAL);uint w=0,h=0;TextGetSize("Conta",w,h);check(w==(uint)std::lround(50.0*dpi/96)&&h==(uint)std::lround(15.0*dpi/96),"native measurement scales glyphs and height by DPI exactly once");}
 bool pixels_match=true;int pixel_cases=0;
 for(int dpi:{96,192})for(int w:{0,1,32})for(int h:{0,1,24})for(int x:{-20,0,5,40})for(int y:{-10,0,7,30}){
  mock_screen_dpi=dpi;TextSetFont("Arial",-100,FW_NORMAL);
  std::vector<uint> actual(w*h,0x11223344),reference=actual;
  auto original_fill=[&](const string &text,int xx,int yy,uint ink){uint tw=0,th=0;TextGetSize(text,tw,th);for(int sy=yy;sy<yy+(int)th&&sy<h;sy++)for(int sx=xx;sx<xx+(int)tw&&sx<w;sx++)if(sx>=0&&sy>=0)reference[sy*w+sx]=ink;};
  original_fill("A😀é",x,y,0xFFABCDEF);TextOut("A😀é",x,y,TA_LEFT|TA_TOP,actual,w,h,0xFFABCDEF,COLOR_FORMAT_ARGB_NORMALIZE);
  original_fill("BB",x+2,y+3,0x80224466);TextOut("BB",x+2,y+3,TA_LEFT|TA_TOP,actual,w,h,0x80224466,COLOR_FORMAT_ARGB_NORMALIZE);
  pixels_match=pixels_match&&actual==reference;
  host_window_text_fail=true;pixels_match=pixels_match&&!TextOut("fail",x,y,TA_LEFT|TA_TOP,actual,w,h,0xFFFFFFFF,COLOR_FORMAT_ARGB_NORMALIZE)&&actual==reference&&host_window_pending.empty();host_window_text_fail=false;
  host_window_pending.clear();pixel_cases++;
 }
 check(pixels_match&&pixel_cases==288,"optimized native clipped fill exactly matches original pixels including negative/outside/two-line/overlap/ARGB/failure cases");
 // Independent feasible contract fixture: all seven metrics at every DPI,
 // configured font and native failure state. Eligibility never comes from a
 // product restore/compact decision: 4096x16384 accommodates seven full rows.
 int golden_cases=0;
 for(int dpi:{96,120,144,192})for(int font:{8,10,16,24,40})for(int native_failure:{0,1,2}){
  mock_screen_dpi=dpi;InpFontSize=font;g_raiz_details_open=false;
  host_window_resource_fail=native_failure==1;host_window_text_fail=native_failure==2;
  DrawHUD(4096,16384,0,0,false);g_stoikus_visual.collapsed=false;g_stoikus_visual.positioned=false;
  g_stoikus_panel_prefs.visible_mask=127;g_stoikus_metric_page=0;g_stoikus_visual.width=240;
  for(int i=0;i<7;i++){g_cockpit_snapshot.metric[i].value="2,75x";g_cockpit_snapshot.metric[i].quality=JPW_VIEW_CURRENT;}
  JPWRenderHUD();
  check(objects.count(g_panel_prefix+"HUD_BG")&&!objects.count(g_panel_prefix+"HUD_RESTORE"),"independent feasible golden must expand at every DPI/font/native state");
  for(const string suffix:{"RAIZ_DETAILS_BUTTON","HUD_NOCUDA","HUD_PERSONALIZE"})check(objects.count(g_panel_prefix+suffix)&&WindowTextValid(g_panel_prefix+suffix,JPWUIDesignPx(4)),"golden retains all measured shared accesses");
  for(int i=0;i<7;i++){
   const string name=g_panel_prefix+IntegerToString(i);
   check(objects.count(name)&&objects.count(name+"_META"),"golden all selected indices and metadata must remain visible");
   if(!objects.count(name))continue; // Failure above is retained, never a skip/pass.
   check(WindowTextValid(name,JPWUIDesignPx(4))&&WindowTextValid(name+"_META",JPWUIDesignPx(4)),"golden primary/meta captions fit with opaque ink");
   check(objects[name].text[OBJPROP_TOOLTIP].find("2,75x")!=string::npos,"golden full value/unit retained");
   const auto &n=objects[name].number;long x=n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)/2;double y=n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)/2;
   string route;scope_clock_ms+=300;opened=-99;
   bool correct=JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route)&&route==name;
   if(correct){HUDAction(route);correct=opened==i;g_raiz_details_open=false;}
   check(correct,"golden actual HUD/action opens canonical index");
  }
  golden_cases++;
 }
 check(golden_cases==60,"nonempty golden matrix covers four DPI/five fonts/three native states");
 host_window_resource_fail=false;host_window_text_fail=false;scope_clock_ms=1000;g_raiz_details_open=false;
 for(int dpi:{96,120,144,192})for(int font:{8,10,24,40})for(int width:{160,176,200,320,800})
 for(bool collapsed:{false,true})for(int failure_kind:{0,1,2})for(int state:{0,1,2,3}){
  mock_screen_dpi=dpi;InpFontSize=font;
  host_window_resource_fail=failure_kind==1;host_window_text_fail=failure_kind==2;
  g_stoikus_options=true;DrawHUD(width,2400,0,0,false);
  g_stoikus_visual.collapsed=collapsed;g_stoikus_panel_prefs.visible_mask=state==3?0:127;
  for(int i=0;i<7;i++){
   g_cockpit_snapshot.metric[i].value="123456789012345678901234567890,12";
   g_cockpit_snapshot.metric[i].quality=state==0?JPW_VIEW_CURRENT:(state==1?JPW_VIEW_ESTIMATED:JPW_VIEW_NA);
  }
  JPWRenderHUD();
  int text_targets=0;
  for(int i=0;i<g_stoikus_surface_count;i++){
   const auto &s=g_stoikus_surfaces[i];if(!s.live||s.name==g_panel_prefix+"HUD_BG")continue;
   text_targets++;
   check(WindowTextValid(s.name,JPWUIDesignPx(4)),"all caption ink fits: "+s.name+" dpi="+IntegerToString(dpi)+" width="+IntegerToString(width)+" font="+IntegerToString(font)+" failure="+IntegerToString(failure_kind));
   check(objects[s.name].text[OBJPROP_TOOLTIP]!="","short caption keeps full tooltip");
   if(failure_kind)check(objects[s.name].number[-1]==OBJ_BUTTON,"actual raster failure has native fallback");
   else check(objects[s.name].number[-1]==OBJ_BITMAP_LABEL||objects[s.name].number[-1]==OBJ_BUTTON,"successful native calls retain observed bitmap or measured opaque fallback");
  }
  check(text_targets>0,"small chart keeps visible account access");
  if(collapsed)collapsed_cases++;
  if(collapsed)check(WindowText(g_panel_prefix+"HUD_RESTORE")=="Stoikus"||objects[g_panel_prefix+"HUD_RESTORE"].text[OBJPROP_TEXT]=="Stoikus","collapsed caption is Stoikus");
  TextSetFont("Arial",-10*font,FW_NORMAL);uint measured_w=0,measured_h=0;TextGetSize("Mg",measured_w,measured_h);
  const int p=JPWUIDesignPx(8),control=JPWUIDesignPx(36),gap=JPWUIDesignPx(4);
  const bool compact=objects.count(g_panel_prefix+"HUD_RESTORE");
  const string access_name=g_panel_prefix+(compact?"HUD_RESTORE":"RAIZ_DETAILS_BUTTON");
  check(objects.count(access_name)&&WindowTextValid(access_name,JPWUIDesignPx(4)),"every feasible viewport retains measured essential access");
  check((WindowCaption(access_name))==(compact?"Stoikus":"Conta"),"measured access caption follows expanded/collapsed contract");
  if(!compact){
   expanded_cases++;
   for(const string &suffix:{"RAIZ_DETAILS_BUTTON","HUD_MIN","HUD_NOCUDA","HUD_PERSONALIZE","HUD_NOTICE","HUD_RESIZE"})
    check(objects.count(g_panel_prefix+suffix),"expanded HUD retains required control "+suffix+" dpi="+IntegerToString(dpi)+" font="+IntegerToString(font)+" width="+IntegerToString(width)+" failure="+IntegerToString(failure_kind)+" state="+IntegerToString(state));
   bool seen[7]={};
   const int original_page=g_stoikus_metric_page;
   for(int page=0;page<7;page++){
    g_stoikus_metric_page=page;JPWRenderHUD();
    for(int i=0;i<7;i++)if(objects.count(g_panel_prefix+IntegerToString(i)))seen[i]=true;
   }
   for(int i=0;i<7;i++)check(seen[i]==(state!=3),"all selected metrics reachable through pages without fabricated hidden metrics i="+IntegerToString(i)+" dpi="+IntegerToString(dpi)+" font="+IntegerToString(font)+" width="+IntegerToString(width)+" failure="+IntegerToString(failure_kind)+" state="+IntegerToString(state));
   g_stoikus_metric_page=original_page;JPWRenderHUD();
  }
  for(int i=0;i<7;i++){
   const string name=g_panel_prefix+IntegerToString(i);if(!objects.count(name))continue;
   const string shown=WindowCaption(name);
   const bool named_scope_access=i==0&&objects[name].number[-1]==OBJ_BUTTON&&(shown=="Conta inteira"||shown=="Toda a conta")&&objects[name].text[OBJPROP_TOOLTIP].find("Ver detalhes da alavancagem")!=string::npos;
   const string fallback_access[7]={"Alav. Ver","P/L Ver","SL Ver","RN1W Ver","RN2W Ver","Risco Ver","Comp. Ver"};
   const auto &region=objects[name].number;
   long hit_x=region.at(OBJPROP_XDISTANCE)+region.at(OBJPROP_XSIZE)/2;double hit_y=region.at(OBJPROP_YDISTANCE)+region.at(OBJPROP_YSIZE)/2;
   string metric_route;scope_clock_ms+=300;opened=-99;
   bool canonical_detail=JPWStoikusHUDEvent(CHARTEVENT_CLICK,hit_x,hit_y,"",metric_route)&&metric_route==name;
   if(canonical_detail){HUDAction(metric_route);canonical_detail=opened==i;g_raiz_details_open=false;}
   check(canonical_detail,"every emitted metric opens its actual canonical detail");
   const bool named_value_access=(shown==fallback_access[i]||shown=="Ver"||(i==0&&shown=="Conta")||shown.find("Detalhes")!=string::npos||shown.find("Ver detalhes")!=string::npos||shown.find("Abrir Conta")!=string::npos||named_scope_access)&&canonical_detail&&objects[name].text[OBJPROP_TOOLTIP].find(g_cockpit_snapshot.metric[i].value)!=string::npos;

   check(shown.find(g_cockpit_snapshot.metric[i].value)!=string::npos||named_value_access,"value complete or explicit details access i="+IntegerToString(i)+" dpi="+IntegerToString(dpi)+" font="+IntegerToString(font)+" width="+IntegerToString(width)+" fail="+IntegerToString(failure_kind)+" shown="+shown);
   check(objects[name].text[OBJPROP_TOOLTIP].find(g_cockpit_snapshot.metric[i].value)!=string::npos,"original financial value retained exactly");
   if(i==0){
    check(objects[name].text[OBJPROP_TOOLTIP].find("Conta inteira")!=string::npos,"full account scope retained");
    if(failure_kind){
     const auto &n=objects[name].number;long x=n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)/2;double y=n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)/2;
     string route;scope_clock_ms+=300;opened=-99;
     check(JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route)&&route==name,"native whole-account scope button dispatches canonical metric0");
     HUDAction(route);check(opened==0,"unchanged production action opens leverage details");g_raiz_details_open=false;
    }
    const string scope=WindowCaption(name+"_META");
    const bool compact_whole_scope=(scope=="Conta"||scope=="Atual Conta"||scope=="Estimado Conta"||scope=="Est. Conta"||scope=="N/A Conta"||shown=="Conta")&&canonical_detail&&objects[name].text[OBJPROP_TOOLTIP].find("Conta inteira")!=string::npos;
    check(compact_whole_scope||scope.find("Conta inteira")!=string::npos||scope.find("Toda a conta")!=string::npos||shown.find("Conta inteira")!=string::npos||shown.find("Toda a conta")!=string::npos,"whole-account scope remains visible in bitmap and opaque fallback dpi="+IntegerToString(dpi)+" font="+IntegerToString(font)+" width="+IntegerToString(width)+" failure="+IntegerToString(failure_kind)+" state="+IntegerToString(state)+" primary="+shown+" meta="+scope);
   }
   if(i==5)check(objects[name].text[OBJPROP_TOOLTIP].find(JPWRiskDisplayScope())!=string::npos,"full risk scope retained");
  }
  host_window_resource_fail=false;host_window_text_fail=false;JPWRenderHUD();
  for(int i=0;i<g_stoikus_surface_count;i++)if(g_stoikus_surfaces[i].live&&g_stoikus_surfaces[i].name!=g_panel_prefix+"HUD_BG"){
   check(WindowTextValid(g_stoikus_surfaces[i].name,JPWUIDesignPx(4)),"recovered bitmap caption remains complete");
   check(objects[g_stoikus_surfaces[i].name].number[-1]==OBJ_BITMAP_LABEL||objects[g_stoikus_surfaces[i].name].number[-1]==OBJ_BUTTON,"recovery retains bitmap or complete measured opaque caption");
  }
  cases++;
 }
 // Actual corrected-DPI regression: a1128px HUD must not be clamped into
 // the88px native heading reserve on a1200px chart.
 mock_screen_dpi=192;InpFontSize=16;InpOffsetY=0;g_stoikus_options=false;
 auto reserved=DrawHUD(1600,1200,0,0,false);
 check(reserved.y>=88&&InBounds(reserved,1600,1200),"DPI layout preserves heading and viewport bounds");
 for(int corner:{0,1,2,3})for(int offset:{0,40,220,2000}){
  InpOffsetY=offset;auto safe=DrawHUD(1600,1200,corner,0,false);
  check(safe.y>=88&&InBounds(safe,1600,1200),"default corners and oversized offsets preserve heading and bounded access");
 }
 InpOffsetY=0;
 g_stoikus_visual.positioned=true;g_stoikus_visual.x=16;g_stoikus_visual.y=0;JPWRenderHUD();
 check(g_stoikus_hud.y==0&&objects.count(g_panel_prefix+"0"),"explicitly moved anchor retains user placement and fitting full HUD");
 check(expanded_cases>100&&collapsed_cases>100,"matrix actually exercises expanded options and collapsed controls");
 std::cout<<"HUD_GOLDEN_EXPANDED: "<<golden_cases<<" independent DPI/font/native cases\n";
 std::cout<<"HUD_TEXT_FIT: "<<cases<<" all-caption DPI/font/viewport/state/failure cases, "<<checks<<" checks, "<<failures<<" failures; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''
    return geo.hud_layout_replay(shutil.which('clang++') or shutil.which('g++'))


if __name__ == '__main__':
    raise SystemExit(main())

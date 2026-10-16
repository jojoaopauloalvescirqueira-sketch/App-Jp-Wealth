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
const int JPW_ROUTE_METRIC=6,JPW_ROUTE_OVERVIEW=7;
int g_cockpit_selected=-1,opened=-99;
void JPWOpenCockpit(int target){opened=target;g_cockpit_selected=target;g_raiz_details_open=true;}
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
 for(int dpi:{96,120,144,192})for(int font:{8,10,24,40})for(int width:{160,176,200,320,800})
 for(bool collapsed:{false,true})for(int failure_kind:{0,1,2})for(int state:{0,1,2,3}){
  mock_screen_dpi=dpi;InpFontSize=font;
  host_window_resource_fail=failure_kind==1;host_window_text_fail=failure_kind==2;
  g_stoikus_options=true;DrawHUD(width,2400,0,0,false);
  g_stoikus_visual.collapsed=collapsed;g_cockpit_prefs.visible_mask=state==3?0:127;
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
   else check(objects[s.name].number[-1]==OBJ_BITMAP_LABEL,"successful raster mode keeps observed bitmap text");
  }
  check(text_targets>0,"small chart keeps visible account access");
  if(collapsed)collapsed_cases++;
  if(collapsed)check(WindowText(g_panel_prefix+"HUD_RESTORE")=="Conta"||objects[g_panel_prefix+"HUD_RESTORE"].text[OBJPROP_TEXT]=="Conta","collapsed caption is Conta");
  TextSetFont("Arial",-10*font,FW_NORMAL);uint measured_w=0,measured_h=0;TextGetSize("Mg",measured_w,measured_h);
  const int p=JPWUIDesignPx(8),control=JPWUIDesignPx(36),gap=JPWUIDesignPx(4);
  const int metric_rows=state==3?0:8;
  const int expected_height=2*p+2*control+metric_rows*(std::max(control,2*(int)measured_h+2*p)+gap)+3*(control+gap);
  const bool expanded_expected=!collapsed&&width>=4*control+4*p&&expected_height<=std::min(2400-2*p,2400-std::max(InpOffsetY,JPWUIDesignPx(44)));
  const string access_name=g_panel_prefix+(collapsed?"HUD_RESTORE":"RAIZ_DETAILS_BUTTON");
  check(objects.count(access_name)&&WindowTextValid(access_name,JPWUIDesignPx(4)),"every feasible viewport retains measured essential Conta access");
  if(!expanded_expected){
   const string access_caption=failure_kind?objects[access_name].text[OBJPROP_TEXT]:WindowText(access_name);
   check(access_caption=="Conta","constrained and collapsed views keep explicit Conta caption");
  }
  if(expanded_expected){
   for(const string &suffix:{"RAIZ_DETAILS_BUTTON","HUD_MIN","HUD_OPTIONS","HUD_MODE","HUD_OPACITY","HUD_RESET","HUD_NOTICE","HUD_RESIZE"})
    check(objects.count(g_panel_prefix+suffix),"fitting expanded HUD retains required control "+suffix);
   if(state!=3)for(int i=0;i<7;i++)check(objects.count(g_panel_prefix+IntegerToString(i)),"fitting full HUD retains each selected metric");
  }
  if(objects.count(g_panel_prefix+"HUD_MODE")){
   expanded_cases++;
   check(objects.count(g_panel_prefix+"HUD_OPACITY")&&objects.count(g_panel_prefix+"HUD_RESET")&&objects.count(g_panel_prefix+"HUD_NOTICE")&&objects.count(g_panel_prefix+"HUD_RESIZE"),"options and footer retain all controls");
   check(objects.count(g_panel_prefix+"HUD_MIN")&&objects.count(g_panel_prefix+"HUD_OPTIONS"),"header retains both controls");
  }
  for(int i=0;i<7;i++){
   const string name=g_panel_prefix+IntegerToString(i);if(!objects.count(name))continue;
   const string shown=failure_kind?objects[name].text[OBJPROP_TEXT]:WindowText(name);
   const bool named_scope_access=i==0&&failure_kind&&(shown=="Conta inteira"||shown=="Toda a conta")&&objects[name].text[OBJPROP_TOOLTIP].find("Ver detalhes da alavancagem")!=string::npos;
   check(shown.find("Detalhes")!=string::npos||shown.find("Ver detalhes")!=string::npos||shown.find(g_cockpit_snapshot.metric[i].value)!=string::npos||named_scope_access,"value complete or explicit details access");
   check(objects[name].text[OBJPROP_TOOLTIP].find(g_cockpit_snapshot.metric[i].value)!=string::npos,"original financial value retained exactly");
   if(i==0){
    check(objects[name].text[OBJPROP_TOOLTIP].find("Conta inteira")!=string::npos,"full account scope retained");
    if(failure_kind){
     const auto &n=objects[name].number;long x=n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)/2;double y=n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)/2;
     string route;scope_clock_ms+=300;opened=-99;
     check(JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route)&&route==name,"native whole-account scope button dispatches canonical metric0");
     HUDAction(route);check(opened==0,"unchanged production action opens leverage details");g_raiz_details_open=false;
    }
    check(shown.find("Conta inteira")!=string::npos||shown.find("Toda a conta")!=string::npos,"whole-account scope remains visible in bitmap and opaque fallback");
   }
   if(i==5)check(objects[name].text[OBJPROP_TOOLTIP].find(JPWRiskDisplayScope())!=string::npos,"full risk scope retained");
  }
  host_window_resource_fail=false;host_window_text_fail=false;JPWRenderHUD();
  for(int i=0;i<g_stoikus_surface_count;i++)if(g_stoikus_surfaces[i].live&&g_stoikus_surfaces[i].name!=g_panel_prefix+"HUD_BG"){
   check(WindowTextValid(g_stoikus_surfaces[i].name,JPWUIDesignPx(4)),"recovered bitmap caption remains complete");
   check(objects[g_stoikus_surfaces[i].name].number[-1]==OBJ_BITMAP_LABEL,"recovery restores bitmap resource for every caption");
  }
  cases++;
 }
 // Actual corrected-DPI regression: a1128px HUD must not be clamped into
 // the88px native heading reserve on a1200px chart.
 mock_screen_dpi=192;InpFontSize=16;InpOffsetY=0;g_stoikus_options=false;
 auto reserved=DrawHUD(1600,1200,0,0,false);
 check(reserved.y==88&&InBounds(reserved,1600,1200)&&!objects.count(g_panel_prefix+"0")&&WindowText(g_panel_prefix+"RAIZ_DETAILS_BUTTON")=="Conta","default upper layout falls back to Conta before intruding into native heading");
 for(int corner:{0,1,2,3})for(int offset:{0,40,220,2000}){
  InpOffsetY=offset;auto safe=DrawHUD(1600,1200,corner,0,false);
  check(safe.y>=88&&InBounds(safe,1600,1200)&&WindowText(g_panel_prefix+"RAIZ_DETAILS_BUTTON")=="Conta","all default corners and oversized legacy offsets preserve heading and bounded measured Conta access");
 }
 InpOffsetY=0;
 g_stoikus_visual.positioned=true;g_stoikus_visual.x=16;g_stoikus_visual.y=0;JPWRenderHUD();
 check(g_stoikus_hud.y==0&&objects.count(g_panel_prefix+"0"),"explicitly moved anchor retains user placement and fitting full HUD");
 check(expanded_cases>100&&collapsed_cases>100,"matrix actually exercises expanded options and collapsed controls");
 std::cout<<"HUD_TEXT_FIT: "<<cases<<" all-caption DPI/font/viewport/state/failure cases, "<<checks<<" checks, "<<failures<<" failures; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''
    return geo.hud_layout_replay(shutil.which('clang++') or shutil.which('g++'))


if __name__ == '__main__':
    raise SystemExit(main())

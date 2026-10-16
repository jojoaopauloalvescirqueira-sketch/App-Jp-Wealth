#!/usr/bin/env python3
"""R1 actual window/menu/target regressions. Chart primitives synthetic; native NOT_RUN."""
from pathlib import Path
import sys
import jpw_positions_ui_test as m
act=(m.INC/'JPW_Alavancagem_Actions.mqh').read_text()
a=act.index('   if(sparam==JPWActionObject(JPW_ACTION_SECTIONS))')
b=act.index('   if(JPWSignalHandleClick(sparam))',a)
nav=act[a:b]
a=act.index('      if(g_cockpit_sections_open && (lparam==37 || lparam==39))')
b=act.index('      if(g_personal_picker!=0',a)
key=act[a:b]
helpers=m.MAIN[:m.MAIN.index('int main(){')]
m.MAIN=helpers+'''
void JPWInvalidateDialogContent(){}
void JPWRenderRaizDetails(){objects.clear();g_focus_count=0;RenderStopsWindow();}
void TestedClick(const string sparam){
'''+nav+'''
 g_cockpit_page++; // explicit sentinel for normal body pager after production intercept
}
void TestedKey(const long lparam){
'''+key+'''
 g_cockpit_page++; // explicit sentinel for normal body keyboard after production intercept
}
int main(){
 reset(3);draw(720,900,11,100,0);
 TestedClick(JPWActionObject(JPW_ACTION_SECTIONS));
 check(g_cockpit_sections_open,"compact menu opens");
 g_cockpit_page=4;
 draw(1600,1000,11,100,0);
 check(!objects.count(JPWActionObject(JPW_ACTION_SECTIONS)),"wide layout has no compact chooser");
 check(!g_cockpit_sections_open&&g_cockpit_page==4,"resize cancels transient menu preserving body page");
 TestedClick(JPWActionObject(JPW_ACTION_NEXT));
 check(g_cockpit_page==5,"wide click reaches visible body pager");
 TestedKey(39);check(g_cockpit_page==6,"wide keyboard reaches visible body pager");
 for(int font:{9,11,16,24})for(int scale:{100,125,150,200})for(int width:{230,320,640,1600}){
  reset(3);g_cockpit_sections_open=false;draw(width,1000,font,scale,0);
  for(const auto& pair:objects){const auto& p=pair.second.number;
   if(!p.count(-1)||p.at(-1)!=OBJ_BUTTON)continue;
   check(p.at(OBJPROP_XSIZE)>=(36*scale+50)/100&&p.at(OBJPROP_YSIZE)>=(36*scale+50)/100,"target >=36 both axes: "+pair.first+" width="+std::to_string(p.at(OBJPROP_XSIZE))+" height="+std::to_string(p.at(OBJPROP_YSIZE))+" scale="+std::to_string(scale));
   check(inside(pair.second),"target stays inside capped window");
  }
 }
 std::cout<<"TASK2_R1_NAV_TARGET: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native NOT_RUN\\n";
 return failures?1:0;
}
'''
# Derived UI precondition:720 now has measured3columns;390 requires selector.
m.MAIN=m.MAIN.replace('reset(3);draw(720,900,11,100,0);','reset(3);draw(390,900,11,100,0);')
raise SystemExit(m.main())

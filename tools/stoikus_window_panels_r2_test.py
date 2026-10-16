#!/usr/bin/env python3
from pathlib import Path
import jpw_stoikus_brand_test as replay
from leverage_source import expanded_source
ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
def run():
 replay.MAIN=(ROOT/'tools/stoikus_panels_fixture/review_r2.cpp').read_text()
 replay.verify_header_render('clang++',expanded_source(INC/'JPW_NoCuda_UI.mqh'))
if __name__=='__main__':run()
def fibo():
 replay.MAIN=(ROOT/'tools/stoikus_panels_fixture/review_r2_fibo.cpp').read_text()
 replay.verify_header_render('clang++',expanded_source(INC/'JPW_UI_Focus.mqh')+expanded_source(INC/'JPW_NoCuda_Fibo_UI.mqh'))
if __name__=='__main__':fibo()

def owner_transfer():
 import subprocess,tempfile
 from stoikus_window_panels_test import function
 from leverage_panel_test import body_of
 source=(ROOT/'tools/stoikus_panels_fixture/native.hpp').read_text()
 source+='struct JPWPanelRect {int x,y,width,height;bool compact;};\nstruct JPWNoCudaFiboUIPrefs {int x,y,width,height,font,density,launcher,mesh,preset;};\n'
 source+=(ROOT/'tools/stoikus_panels_fixture/gesture.hpp').read_text()
 source+=(INC/'JPW_Stoikus_Window.mqh').read_text()
 source+=(ROOT/'tools/stoikus_panels_fixture/review_r2_owner.hpp').read_text()
 source+=function('JPW_Alavancagem_Actions.mqh','bool JPWAccountWindowEvent(')
 actions=(INC/'JPW_Alavancagem_Actions.mqh').read_text()
 prefix=body_of(actions,'void JPWHandleChartEventBody(').split('   JPWAccount event_account;')[0]
 source+='void JPWHandleChartEvent(int id,const long &lparam,const double &dparam,const string &sparam){'+prefix+'}\n'
 indicator=(ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5').read_text()
 source+='void OnChartEvent(int id,const long &lparam,const double &dparam,const string &sparam){'+body_of(indicator,'void OnChartEvent(')+'}\n'
 source+=r'''int main(){long x=110;double y=125;string down="1";OnChartEvent(CHARTEVENT_MOUSE_MOVE,x,y,down);
 if(!g_account_window_gesture.active||scroll_enabled)return 1;
 owner="OTHER";owns=false;OnChartEvent(CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT,x,y,owner);
 if(g_account_window_gesture.active||!scroll_enabled||g_raiz_details_open||!g_jpw_focus_suspended||destroyed!=1||draft!=edit){std::cerr<<"FAIL actual owner wrapper suspension/capture\n";return 1;}
 std::cout<<"PASS actual Account wrapper + actual owner-handler prefix: hidden/suspended/draft/scroll; native NOT_RUN\n";}
'''
 with tempfile.TemporaryDirectory(prefix='stoikus-owner-r2-') as temp:
  cpp=Path(temp)/'test.cpp';cpp.write_text(source)
  subprocess.run(['clang++','-std=c++17',str(cpp),'-o',temp+'/test'],check=True)
  subprocess.run([temp+'/test'],check=True)
if __name__=='__main__':owner_transfer()

def fibo_window_preferences():
 previous=replay.SHIM
 replay.SHIM=previous.replace('bool ObjectSetString(int,const string&n,int p,const string&v){','bool window_refuse=false;int window_writes=0;\nbool ObjectSetString(int,const string&n,int p,const string&v){if(n=="JPW_NOCUDA_FIBO_WINDOW_V1"){window_writes++;if(window_refuse)return false;}')
 replay.MAIN=r'''int main(){
   JPWNoCudaFiboUIWindowLoad();if(window_writes!=0)return 1;
   ObjectCreate(0,"JPW_NOCUDA_FIBO_VISUAL_V1",OBJ_LABEL,0,0,0);ObjectSetString(0,"JPW_NOCUDA_FIBO_VISUAL_V1",OBJPROP_TOOLTIP,"old physical units");
   if(!JPWNoCudaFiboUIWindowSave(true)||!g_fc_window_minimized)return 2;
   g_fc_window_loaded=false;g_fc_window_minimized=false;JPWNoCudaFiboUIWindowLoad();if(!g_fc_window_minimized)return 3;
   const string name="JPW_NOCUDA_FIBO_WINDOW_V1";int before=window_writes;
   objects[name].text[OBJPROP_TOOLTIP]="V1|0";if(JPWNoCudaFiboUIWindowSave(false)||window_writes!=before)return 4;
   objects[name].text[OBJPROP_TOOLTIP]="V1|1";objects[name].type=99;if(JPWNoCudaFiboUIWindowSave(false)||window_writes!=before)return 5;
   objects[name].type=OBJ_LABEL;window_refuse=true;if(JPWNoCudaFiboUIWindowSave(false)||!g_fc_window_minimized||objects[name].text[OBJPROP_TOOLTIP]!="V1|1")return 6;
   window_refuse=false;if(!JPWNoCudaFiboUIWindowSave(false)||g_fc_window_minimized)return 7;
   if(objects["JPW_NOCUDA_FIBO_VISUAL_V1"].text[OBJPROP_TOOLTIP]!="old physical units")return 8;
   std::cout<<"PASS Fibo separate collapsed flag/read-only load/restore/stale/foreign/failure/legacy preservation; native NOT_RUN\n";return 0;}
'''
 try:replay.verify_header_render('clang++',expanded_source(INC/'JPW_UI_Focus.mqh')+expanded_source(INC/'JPW_NoCuda_Fibo_UI.mqh'))
 finally:replay.SHIM=previous
if __name__=='__main__':fibo_window_preferences()

def fibo_geometry_preferences():
 previous=replay.SHIM
 replay.SHIM=previous.replace('bool ObjectSetString(int,const string&n,int p,const string&v){','bool geometry_corrupt_once=false;\nbool ObjectSetString(int,const string&n,int p,const string&v){if(n=="JPW_NOCUDA_FIBO_VISUAL_V1"&&p==OBJPROP_TOOLTIP&&geometry_corrupt_once){geometry_corrupt_once=false;objects[n].text[p]="unconfirmed write";return true;}')
 replay.MAIN=r'''int main(){int failed=0;auto check=[&](bool ok,string msg){if(!ok){failed++;std::cerr<<"FAIL "<<msg<<"\n";}};
   objects.clear();JPWNoCudaFiboUILoadPrefs();check(pref_writes==0,"legacy load no writes");
   check(JPWNoCudaFiboUISavePrefs(),"initial legacy visual save");const string name=JPWNoCudaFiboUIPrefName();string old=ObjectGetString(0,name,OBJPROP_TOOLTIP);
   objects[name].type=99;g_fc_pref.x+=10;check(!JPWNoCudaFiboUISavePrefs()&&ObjectGetString(0,name,OBJPROP_TOOLTIP)==old,"foreign legacy object preserved");
   objects[name].type=OBJ_LABEL;objects[name].text[OBJPROP_TOOLTIP]=old+"|foreign";g_fc_pref.x+=10;
   check(!JPWNoCudaFiboUISavePrefs()&&ObjectGetString(0,name,OBJPROP_TOOLTIP)==old+"|foreign","stale legacy visual payload preserved");
   objects[name].text[OBJPROP_TOOLTIP]=old;geometry_corrupt_once=true;g_fc_pref.x+=10;
   check(!JPWNoCudaFiboUISavePrefs()&&ObjectGetString(0,name,OBJPROP_TOOLTIP)==old,"legacy readback failure restores previous payload");
   objects[name].type=99;JPWNoCudaFiboUILoadPrefs();check(g_fc_pref_invalid,"legacy loader rejects foreign type");
   objects[name].type=OBJ_LABEL;objects[name].text[OBJPROP_TOOLTIP]="invalid retained payload";JPWNoCudaFiboUILoadPrefs();
   JPWNoCudaFiboUIActions("FC_SETTINGS_DEFAULT");g_fc_pref.x+=1;
   check(!JPWNoCudaFiboUISavePrefs()&&objects[name].text[OBJPROP_TOOLTIP]=="invalid retained payload","geometry cannot apply pending explicit reset");
   JPWNoCudaFiboUIActions("FC_SETTINGS_APPLY");check(!g_fc_pref_invalid&&StringFind(objects[name].text[OBJPROP_TOOLTIP],"V1|")==0,"explicit Default and Apply resets known invalid visual payload");
   std::cout<<"R2 Fibo geometry preference failures="<<failed<<"; native NOT_RUN\n";return failed?1:0;}
'''
 try:replay.verify_header_render('clang++',expanded_source(INC/'JPW_UI_Focus.mqh')+expanded_source(INC/'JPW_NoCuda_Fibo_UI.mqh'))
 finally:replay.SHIM=previous
if __name__=='__main__':fibo_geometry_preferences()

def fibo_escape_wrapper():
 from leverage_panel_test import body_of
 previous=replay.SHIM
 replay.SHIM=previous.replace('bool ObjectSetString(int,const string&n,int p,const string&v){','int all_writes=0;\nbool ObjectSetString(int,const string&n,int p,const string&v){all_writes++;')
 seams=r'''
const int CHARTEVENT_OBJECT_ENDEDIT=5,CHARTEVENT_MOUSE_WHEEL=6,TERMINAL_KEYSTATE_SHIFT=7,ACCOUNT_SERVER=8;
bool g_nocuda_initialized=true,g_nocuda_resources_admitted=true,g_ncf_mode=true,g_nocuda_panel_open=false,g_nocuda_pending_pick=false;
string g_nocuda_prefix="P",g_nocuda_symbol="EURUSD",_Symbol="EURUSD",g_nocuda_feed="server";
JPWNoCudaFiboView g_ncf_ui;struct Sync{bool mouse_down=false;}g_ncf_sync;
int action_calls=0,draws=0;
string AccountInfoString(int){return "server";}
void JPWNoCudaDrawUI(){}void JPWNoCudaReadJustification(){}void JPWNoCudaClearDaily(){}void JPWNoCudaPaint(){}
void JPWNCFDraw(){draws++;}
void JPWNCFAction(string action){action_calls++;if(action=="FC_CLOSE")g_ncf_ui.open=false;}
'''
 controller=(INC/'JPW_NoCuda_Fibo_Controller.mqh').read_text()
 route=body_of(controller,'bool JPWNCFHandleEvent(')
 start=route.index('   if(id==CHARTEVENT_MOUSE_MOVE) g_ncf_sync.mouse_down=')
 end=route.index('   if(id==CHARTEVENT_CHART_CHANGE)',start)
 seams+='bool JPWNCFHandleEvent(int id,const long &lparam,const double &dparam,const string &sparam){'+route[start:end]+'return true;}\n'
 indicator=(ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5').read_text()
 wrapper=body_of(indicator,'void OnChartEvent(')
 end=wrapper.index('   if(JPWNCFHandleEvent(id,lparam,dparam,sparam)) return;')+len('   if(JPWNCFHandleEvent(id,lparam,dparam,sparam)) return;')
 seams+='void OnChartEvent(int id,const long &lparam,const double &dparam,const string &sparam){'+wrapper[:end]+'}\n'
 replay.MAIN=seams+(ROOT/'tools/stoikus_panels_fixture/review_fibo_escape.cpp').read_text()
 try:replay.verify_header_render('clang++',expanded_source(INC/'JPW_UI_Focus.mqh')+expanded_source(INC/'JPW_NoCuda_Fibo_UI.mqh'))
 finally:replay.SHIM=previous
if __name__=='__main__':fibo_escape_wrapper()

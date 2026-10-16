#!/usr/bin/env python3
"""Replay production panel geometry with synthetic native measurement seams.
Native MetaEditor compilation, native fonts and runtime acceptance: NOT_RUN.
"""
from pathlib import Path
import subprocess, tempfile
from leverage_panel_test import body_of
ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'

def function(file,signature):
    source=(INC/file).read_text()
    start=source.index(signature)
    opening=source.index('{',start)
    return source[start:opening]+'{'+body_of(source,signature)+'}\n'

def run():
    source=(ROOT/'tools/stoikus_panels_fixture/native.hpp').read_text()
    source+='struct JPWPanelRect { int x,y,width,height; bool compact; };\n'
    source+='struct JPWNoCudaFiboUIPrefs { int x,y,width,height,font,density,launcher,mesh,preset; };\n'
    source+=(ROOT/'tools/stoikus_panels_fixture/gesture.hpp').read_text()
    source+=(INC/'JPW_Stoikus_Window.mqh').read_text()
    source+='JPWStoikusWindowGesture g_manual_gesture={};JPWPanelRect g_manual_rect={};\n'
    source+=function('JPW_Alavancagem_Panel.mqh','bool JPWPanelAccount(')
    for signature in ['int JPWUIDesignControlHeight(', 'int JPWUIDesignNavColumns(']:
        source+=function('JPW_UI_Design.mqh',signature).replace('string &labels[]','string labels[]')
    for signature in ['int JPWNoCudaUIWidth()', 'int JPWNoCudaUIHeight()', 'int JPWNoCudaUILineHeight()', 'int JPWNoCudaUIButtonHeight()']:
        source+=function('JPW_NoCuda_UI.mqh',signature)
    for signature in ['int JPWNoCudaFiboUIClamp(', 'void JPWNoCudaFiboUIDefault(', 'void JPWNoCudaFiboUIBounds(']:
        source+=function('JPW_NoCuda_Fibo_UI.mqh',signature)
    source+=function('JPW_NoCuda_Fibo_UI.mqh','void JPWNoCudaFiboUICancelGeometry()')
    source+=function('JPW_NoCuda_Fibo_UI.mqh','bool JPWNoCudaFiboUIHandleGeometry(')
    source+=(ROOT/'tools/stoikus_panels_fixture/main.cpp').read_text()
    with tempfile.TemporaryDirectory(prefix='stoikus-panels-') as temp:
        cpp=Path(temp)/'test.cpp'; cpp.write_text(source)
        subprocess.run(['clang++','-std=c++17','-Wall','-Wextra',str(cpp),'-o',temp+'/test'],check=True)
        subprocess.run([temp+'/test'],check=True)
if __name__=='__main__':run()

def brand():
    import jpw_stoikus_brand_test as original
    from leverage_source import expanded_source
    original.MAIN=r'''int main(){
      for(int d:{100,125,150,200}) for(int font:{9,11,16,24}) {
        dpi=d;objects.clear();int height=160;
        JPWGenetrixHeader("MARK","TITLE",10,20,2000,height,font,0,false,"Conta");
        uint w=0,h=0;TextSetFont("Arial",-10*font);TextGetSize("Ag",w,h);
        if(objects["TITLE"].number[OBJPROP_YDISTANCE]!=20+(height-(int)h)/2){std::cerr<<"FAIL measured title center\\n";return 1;}
      }
      std::cout<<"PASS measured title vertical alignment; native NOT_RUN\\n";return 0;
    }'''
    original.verify_header_render('clang++',expanded_source(INC/'JPW_Stoikus_Brand.mqh'))
if __name__=='__main__':brand()

def minimize():
    shim=r'''#include <string>
#include <cassert>
#include <iostream>
using string=std::string;
struct JPWStoikusVisual {bool account_minimized=false;int mode=1;int width=333;};
JPWStoikusVisual g_stoikus_visual;int g_account_window_gesture=0,g_account_window_rect=0;
bool g_jpw_focus_suspended=false,g_raiz_details_open=true,history_audit_active=true,signal_draft=true;
int captures=0,releases=0,destroys=0,renders=0,saves=0;string g_panel_prefix="P";
void JPWRaizSaveVisibleFields(){captures++;}void JPWStoikusWindowCancel(int&,int&){}
void JPWUIRelease(string){releases++;}void JPWRaizPanelDestroy(){destroys++;}
void JPWRenderHUD(){renders++;}bool JPWStoikusVisualSave(JPWStoikusVisual v){saves++;g_stoikus_visual=v;return true;}
'''
    code=shim+function('JPW_Alavancagem_Actions.mqh','void JPWAccountMinimize()')+r'''int main(){JPWAccountMinimize();assert(captures==1&&releases==1&&destroys==1&&renders==1&&saves==1);assert(g_jpw_focus_suspended&&!g_raiz_details_open&&history_audit_active&&signal_draft);assert(g_stoikus_visual.account_minimized&&g_stoikus_visual.width==333&&g_stoikus_visual.mode==1);std::cout<<"PASS actual minimize captures RAM/releases owner/preserves audit and visual fields; native NOT_RUN\n";}'''
    with tempfile.TemporaryDirectory(prefix='stoikus-minimize-') as temp:
        cpp=Path(temp)/'test.cpp';cpp.write_text(code)
        subprocess.run(['clang++','-std=c++17',str(cpp),'-o',temp+'/test'],check=True)
        subprocess.run([temp+'/test'],check=True)
if __name__=='__main__':minimize()

def manual_preferences():
    shim=r'''#include <string>
#include <vector>
#include <cassert>
#include <iostream>
using string=std::string;
const int OBJ_LABEL=1,OBJPROP_TOOLTIP=2,OBJPROP_TYPE=3,OBJPROP_XDISTANCE=4,OBJPROP_YDISTANCE=5,OBJPROP_HIDDEN=6,OBJPROP_SELECTABLE=7;
bool exists=false,refuse=false;int type=OBJ_LABEL,writes=0;string payload="";
bool g_manual_visual_loaded=false,g_manual_visual_valid=true,g_manual_positioned=false,g_manual_collapsed=false;
string g_manual_visual_seen="",g_manual_visual_notice="";int g_manual_x=0,g_manual_y=0,g_manual_width=680,g_manual_height=500;
int ObjectFind(int,string){return exists?0:-1;}string ObjectGetString(int,string,int){return payload;}int ObjectGetInteger(int,string,int){return type;}
bool ObjectCreate(int,string,int,int,int,int){exists=true;type=OBJ_LABEL;return true;}
bool ObjectSetInteger(int,string,int,int){return true;}
bool ObjectSetString(int,string,int,string p){writes++;if(refuse)return false;payload=p;return true;}
bool ObjectDelete(int,string){exists=false;payload="";return true;}
int StringToInteger(string s){try{return std::stoi(s);}catch(...){return 0;}}
string IntegerToString(int n){return std::to_string(n);}int MathMax(int a,int b){return a>b?a:b;}
int StringSplit(string s,char c,std::vector<string>&a){a.clear();size_t from=0,p;while((p=s.find(c,from))!=string::npos){a.push_back(s.substr(from,p-from));from=p+1;}a.push_back(s.substr(from));return a.size();}
'''
    code=shim
    for signature in ['string JPWNoCudaUIVisualName()', 'void JPWNoCudaUIVisualLoad()', 'bool JPWNoCudaUIVisualSave()']:
        code+=function('JPW_NoCuda_UI.mqh',signature).replace('string fields[]','std::vector<string> fields')
    code+=r'''int main(){
      JPWNoCudaUIVisualLoad();assert(writes==0);g_manual_x=123;g_manual_y=56;g_manual_width=777;g_manual_height=555;g_manual_positioned=true;g_manual_collapsed=true;
      assert(JPWNoCudaUIVisualSave());string saved=payload;g_manual_visual_loaded=false;g_manual_width=680;JPWNoCudaUIVisualLoad();assert(g_manual_width==777&&g_manual_collapsed&&g_manual_positioned);
      payload="V1|other";int before=writes;assert(!JPWNoCudaUIVisualSave()&&writes==before);payload=saved;type=99;assert(!JPWNoCudaUIVisualSave()&&writes==before);
      type=OBJ_LABEL;refuse=true;g_manual_width=888;assert(!JPWNoCudaUIVisualSave()&&payload==saved);
      refuse=false;payload="V1|1|2|0|500|1|0";g_manual_visual_loaded=false;JPWNoCudaUIVisualLoad();assert(!g_manual_visual_valid);
      std::cout<<"PASS actual manual visual prefs roundtrip/stale/foreign/write failure/no paint write; native NOT_RUN\n";
    }'''
    with tempfile.TemporaryDirectory(prefix='stoikus-manual-prefs-') as temp:
        cpp=Path(temp)/'test.cpp';cpp.write_text(code)
        subprocess.run(['clang++','-std=c++17',str(cpp),'-o',temp+'/test'],check=True)
        subprocess.run([temp+'/test'],check=True)
if __name__=='__main__':manual_preferences()

def manual_render():
    import jpw_stoikus_brand_test as original
    from leverage_source import expanded_source
    original.MAIN=r'''int main(){int failures=0,cases=0;
      for(int d:{100,125,150,200})for(int width:{120,320,720,1440})for(int height:{100,300,700,1120})for(int tab=0;tab<3;tab++){
        objects.clear();dpi=d;chart_width=width;chart_height=height;g_manual_positioned=false;g_manual_gesture.active=false;
        JPWNoCudaUIView v={};v.open=true;v.tab=tab;v.symbol="EURUSD";v.source_tf="H1";v.status="Rascunho preservado";
        JPWNoCudaUIRender("P",v);cases++;
        for(auto &entry:objects){auto&o=entry.second;if(o.type!=OBJ_BUTTON&&o.type!=OBJ_EDIT)continue;
          int x=o.number[OBJPROP_XDISTANCE],y=o.number[OBJPROP_YDISTANCE],w=o.number[OBJPROP_XSIZE],h=o.number[OBJPROP_YSIZE];
          if(x<0||y<0||x+w>width||y+h>height){std::cerr<<"OUT "<<entry.first<<" "<<width<<"x"<<height<<" dpi"<<d<<"\n";failures++;}
        }
      }
      std::cout<<"Manual production render "<<cases<<" cases / "<<failures<<" out of viewport; native NOT_RUN\n";return failures?1:0;
    }'''
    original.verify_header_render('clang++',expanded_source(INC/'JPW_NoCuda_UI.mqh'))
if __name__=='__main__':manual_render()

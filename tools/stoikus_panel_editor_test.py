#!/usr/bin/env python3
"""Behavioral replay of the production panel editor and actual VisualSave source.

Synthetic chart-object boundary only; native rendering, event routing, focus
notifications and template serialization still require MT5. Not in full runner.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
from leverage_panel_test import body_of
from leverage_host_shim import translate_arrays

ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
SHIM=r'''
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using string=std::string;using ushort=unsigned short;using color=int;
int StringLen(const string&s){return s.size();}ushort StringGetCharacter(const string&s,int i){return s.at(i);}
string StringSubstr(const string&s,int a,int n=-1){return s.substr(a,n<0?string::npos:n);}
int StringFind(const string&s,const string&n,int a=0){auto p=s.find(n,a);return p==string::npos?-1:p;}
string IntegerToString(int n){return std::to_string(n);}long StringToInteger(const string&s){try{return std::stol(s);}catch(...){return 0;}}
int MathMin(int a,int b){return std::min(a,b);}int MathMax(int a,int b){return std::max(a,b);}double MathRound(double a){return std::round(a);}
template<typename...A>string StringFormat(const string&f,A...a){char b[160];std::snprintf(b,sizeof(b),f.c_str(),a...);return b;}
const int OBJ_LABEL=1,OBJPROP_TYPE=-1,OBJPROP_TEXT=2,OBJPROP_XDISTANCE=4,OBJPROP_YDISTANCE=5,OBJPROP_HIDDEN=6,OBJPROP_SELECTABLE=7;
struct Obj{int kind=OBJ_LABEL;std::map<int,long> n;std::map<int,string>s;};std::map<string,Obj> objects;
int writes=0,creates=0,deletes=0,focus_acquires=0,minimizes=0;bool create_ok=true,int_ok=true,focus_ok=true;
string refuse_name="",corrupt_name="",delete_refuse="";bool corrupt_once=false,refuse_once=false;
int ObjectFind(int,const string&n){return objects.count(n)?0:-1;}
long ObjectGetInteger(int,const string&n,int p){return p==OBJPROP_TYPE?objects[n].kind:objects[n].n[p];}
string ObjectGetString(int,const string&n,int p){return objects[n].s[p];}
bool ObjectCreate(int,const string&n,int k,int,int,int){creates++;if(!create_ok)return false;objects[n].kind=k;return true;}
bool ObjectSetInteger(int,const string&n,int p,long v){writes++;if(!int_ok)return false;objects[n].n[p]=v;return true;}
bool ObjectSetString(int,const string&n,int p,const string&v){writes++;if(refuse_name==n){if(refuse_once){refuse_once=false;refuse_name="";}return false;}if(corrupt_name==n&&corrupt_once){corrupt_once=false;objects[n].s[p]="corrupt";return true;}objects[n].s[p]=v;return true;}
bool ObjectDelete(int,const string&n){deletes++;if(n==delete_refuse)return false;return objects.erase(n)>0;}
string owner="",g_panel_prefix="JPW_LEV_101_";bool g_raiz_details_open=false;
bool JPWUIOwns(const string&n){return owner==n;}bool JPWUIAcquire(const string&n){focus_acquires++;if(!focus_ok)return false;owner=n;return true;}
void JPWUIRelease(const string&n){if(owner==n)owner="";}
void JPWAccountMinimize(){minimizes++;g_raiz_details_open=false;}
int JPWUIDesignPx(int v){return v;}double JPWUIDesignScale(){return 1.;}
struct Paint{string suffix;int x,y,w,h,transparency;string caption;};std::vector<Paint> paint;
bool JPWStoikusHUDSurfacePaint(const string&s,int x,int y,int w,int h,const string&,const string&,int,color,color,int,const string&,int=3,const string&="");
'''
# Avoid C++ parsing ambiguity for a default reference argument.
SHIM=SHIM.replace('const string&=""','const string &caption=""')+r'''
bool JPWStoikusHUDSurfacePaint(const string&s,int x,int y,int w,int h,const string&caption,const string&,int,color,color,int transparency,const string&,int,const string&){paint.push_back({s,x,y,w,h,transparency,caption});return true;}
void JPWStoikusHUDCaptionPaint(const string&s,int x,int y,int w,int h,const string&caption,const string&,color,color,const string&,int=3){paint.push_back({s,x,y,w,h,100,caption});}
struct JPWCockpitPrefs{int visible_mask=127;int corner=0,density=0;};JPWCockpitPrefs g_cockpit_prefs;
#define JPW_COCKPIT_PREF_VERSION 3
#define JPW_COCKPIT_ALL_VISIBLE 127
int StringSplit(const string&s,char delimiter,std::vector<string>&out){out.clear();size_t start=0;for(size_t i=0;i<=s.size();i++)if(i==s.size()||s[i]==delimiter){out.push_back(s.substr(start,i-start));start=i+1;}return out.size();}
#define JPW_COCKPIT_PREF_OBJECT "JPW_COCKPIT_PREF_V3"
#define JPW_COCKPIT_PREF_V2_OBJECT "JPW_COCKPIT_PREF_V2"
#define JPW_COCKPIT_PREF_LEGACY_OBJECT "JPW_COCKPIT_PREF_V1"
'''
STATE=r'''
JPWStoikusVisual g_stoikus_visual;bool g_stoikus_visual_invalid=false;
string g_stoikus_visual_notice="",g_stoikus_visual_seen="";long g_stoikus_visual_seen_type=-1;
void JPWStoikusVisualLoad(){JPWStoikusVisualDefault(g_stoikus_visual);g_stoikus_visual_seen="";g_stoikus_visual_seen_type=-1;g_stoikus_visual_invalid=false;
 if(ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)>=0){g_stoikus_visual_seen=ObjectGetString(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TEXT);g_stoikus_visual_seen_type=ObjectGetInteger(0,JPW_STOIKUS_VISUAL_OBJECT,OBJPROP_TYPE);g_stoikus_visual_invalid=g_stoikus_visual_seen_type!=OBJ_LABEL||!JPWStoikusVisualDecode(g_stoikus_visual_seen,g_stoikus_visual);}}
'''
MAIN=r'''
int checks=0,failures=0;void check(bool ok,const string&why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}}
void reset(){objects.clear();writes=creates=deletes=focus_acquires=minimizes=0;create_ok=int_ok=focus_ok=true;refuse_name=corrupt_name=delete_refuse="";refuse_once=corrupt_once=false;owner="";g_raiz_details_open=false;g_cockpit_prefs.visible_mask=127;JPWStoikusVisualLoad();JPWStoikusPanelEditorCancel();JPWStoikusPanelLoad();}
void put(const string&name,const string&text,int kind=OBJ_LABEL){objects[name].kind=kind;objects[name].s[OBJPROP_TEXT]=text;}
int main(){
 reset();check(g_stoikus_panel_prefs.visible_mask==57&&writes==0&&creates==0,"fresh load defaults57 without writes");
 put(JPW_COCKPIT_PREF_OBJECT,"JPWCOCKPIT|3|95|0|0|374544");g_cockpit_prefs.visible_mask=95;JPWStoikusPanelLoad();
 check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_prefs)=="V1|1|0512346"&&writes==0,"compact compatibility preserves formerly visible selection");
 g_stoikus_visual.mode=1;put(JPW_STOIKUS_VISUAL_OBJECT,"V1|1|0|30|280|0|0|0|0|0|0|720|520|0");JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==95,"normal compatibility preserves old mask");
 reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|0|6543210");JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==0&&g_stoikus_panel_prefs.order[0]==6&&writes==0,"new empty selection decoded with no writes");
 for(string bad:{"V2|57|0534126","V1|057|0534126","bad"}){reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,bad);JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_APPLY");check(objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]==bad&&!g_stoikus_panel_notice.empty()&&writes==0,"invalid observed payload preserved until explicit default");}
 reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"foreign",99);JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_DEFAULT");JPWStoikusPanelEditorAction("CUST_APPLY");check(objects[JPW_STOIKUS_PANEL_PREF_OBJECT].kind==99&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="foreign"&&writes==0,"foreign object never overwritten even explicit default");
 reset();g_raiz_details_open=true;JPWStoikusPanelEditorOpen();check(g_stoikus_panel_editor&&minimizes==1&&owner==g_panel_prefix,"editor preserves account draft via minimize and acquires focus");
 JPWStoikusPanelEditorAction("CUST_TOGGLE_0");JPWStoikusPanelEditorAction("CUST_UP_3");JPWStoikusPanelEditorAction("CUST_OPACITY");
 check(g_stoikus_panel_draft.visible_mask==56&&g_stoikus_panel_prefs.visible_mask==57&&writes==0&&g_stoikus_visual.transparency==30,"selection/order/transparency preview write nothing");
 JPWStoikusPanelEditorCancel();check(!g_stoikus_panel_editor&&g_stoikus_panel_prefs.visible_mask==57&&g_stoikus_visual.transparency==30&&owner.empty()&&writes==0,"cancel restores saved preference without any writes");
 reset();JPWStoikusPanelEditorOpen();for(int i:{0,5,3,4})JPWStoikusPanelEditorAction("CUST_TOGGLE_"+IntegerToString(i));
 check(g_stoikus_panel_draft.visible_mask==0,"explicit zero selection");JPWStoikusPanelEditorAction("CUST_APPLY");
 check(!g_stoikus_panel_editor&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|0|0534126","apply saves empty selection and closes editor");
 JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==0,"reopen load retains explicit zero");JPWStoikusPanelEditorOpen();for(int i=0;i<7;i++)JPWStoikusPanelEditorAction("CUST_TOGGLE_"+IntegerToString(i));JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_prefs.visible_mask==127,"all127 selection saves");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");JPWStoikusPanelRecheck();int before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(writes==before&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210"&&!g_stoikus_panel_notice.empty(),"template new preference change blocks draft apply");JPWStoikusPanelEditorCancel();JPWStoikusPanelEditorOpen();check(g_stoikus_panel_draft.visible_mask==127&&g_stoikus_panel_draft.order[0]==6,"cancel reopen rechecks new template");
 for(string name:{string(JPW_COCKPIT_PREF_OBJECT),string(JPW_COCKPIT_PREF_V2_OBJECT),string(JPW_COCKPIT_PREF_LEGACY_OBJECT),string(JPW_STOIKUS_VISUAL_OBJECT)}){reset();JPWStoikusPanelEditorOpen();put(name,"template replacement");before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(writes==before&&ObjectFind(0,JPW_STOIKUS_PANEL_PREF_OBJECT)<0,"legacy/template changes block new preference write");}
 for(int fault=0;fault<4;fault++){reset();JPWStoikusPanelEditorOpen();if(fault==0)create_ok=false;if(fault==1)int_ok=false;if(fault==2){refuse_name=JPW_STOIKUS_PANEL_PREF_OBJECT;refuse_once=true;}if(fault==3){corrupt_name=JPW_STOIKUS_PANEL_PREF_OBJECT;corrupt_once=true;}JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_editor&&g_stoikus_panel_prefs.visible_mask==57&&ObjectFind(0,JPW_STOIKUS_PANEL_PREF_OBJECT)<0&&!g_stoikus_panel_notice.empty(),"creation/metadata/text/readback failure rolls back new object and keeps editor");}
 reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");corrupt_name=JPW_STOIKUS_PANEL_PREF_OBJECT;corrupt_once=true;JPWStoikusPanelEditorAction("CUST_APPLY");check(objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210"&&g_stoikus_panel_prefs.visible_mask==127,"readback failure restores existing payload and runtime");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_OPACITY");JPWStoikusPanelEditorAction("CUST_APPLY");check(!g_stoikus_panel_editor&&g_stoikus_visual.transparency==40&&ObjectFind(0,JPW_STOIKUS_PANEL_PREF_OBJECT)>=0&&ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)>=0,"joint apply saves transparency and selection");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_OPACITY");refuse_name=JPW_STOIKUS_VISUAL_OBJECT;refuse_once=true;JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_editor&&g_stoikus_visual.transparency==30&&ObjectFind(0,JPW_STOIKUS_PANEL_PREF_OBJECT)<0&&ObjectFind(0,JPW_STOIKUS_VISUAL_OBJECT)<0,"visual failure rolls panel back to absent state");
 reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");JPWStoikusPanelEditorAction("CUST_OPACITY");refuse_name=JPW_STOIKUS_VISUAL_OBJECT;refuse_once=true;JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_prefs.visible_mask==127&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210","joint failure restores existing panel payload");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_OPACITY");refuse_name=JPW_STOIKUS_VISUAL_OBJECT;refuse_once=true;delete_refuse=JPW_STOIKUS_PANEL_PREF_OBJECT;JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_editor&&!g_stoikus_panel_notice.empty(),"rollback refusal remains explicit and editor remains open");
 reset();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V2|57|0534126");g_cockpit_prefs.visible_mask=33;put(JPW_COCKPIT_PREF_OBJECT,"JPWCOCKPIT|3|33|0|0|310565");JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_DEFAULT");check(g_stoikus_panel_draft.visible_mask==33,"default respects prior hidden legacy metrics");JPWStoikusPanelEditorAction("CUST_APPLY");check(!g_stoikus_panel_editor&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|33|0534126","only explicit default and apply replace known invalid label");
 reset();JPWStoikusPanelEditorOpen();check(JPWStoikusPanelEditorAction("CUST_BG")&&JPWStoikusPanelEditorAction("CUST_TITLE")&&JPWStoikusPanelEditorAction("CUST_NOTICE")&&writes==0,"editor consumes its background and read-only caption hits");
 reset();JPWStoikusPanelPrefs saved_candidate=g_stoikus_panel_prefs;put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");before=writes;check(!JPWStoikusPanelSave(saved_candidate)&&writes==before&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210","direct save cannot silently refresh unseen template before overwrite");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");JPWStoikusPanelLoad();before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(writes==before&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210","direct load during edit cannot bypass template-change refusal");
 reset();owner=g_panel_prefix;JPWStoikusPanelEditorCancel();check(owner==g_panel_prefix,"inactive editor cancel leaves account-owned focus untouched");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_OPACITY");refuse_name=JPW_STOIKUS_VISUAL_OBJECT;refuse_once=true;delete_refuse=JPW_STOIKUS_VISUAL_OBJECT;JPWStoikusPanelEditorAction("CUST_APPLY");before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(writes==before&&g_stoikus_panel_editor&&g_stoikus_panel_notice.find("confira")!=string::npos,"failed visual rollback requires inspection before any retry");
 reset();focus_ok=false;JPWStoikusPanelEditorOpen();check(!g_stoikus_panel_editor&&writes==0,"focus admission failure does not open editor");
 reset();JPWStoikusPanelEditorOpen();owner="OTHER";before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(writes==before,"foreign focus cannot apply stale editor action");JPWStoikusPanelEditorCancel();check(owner=="OTHER","cancel does not release another module focus");
 reset();JPWStoikusPanelEditorOpen();for(int cw:{80,240,480,800})for(int ch:{60,240,420,900}){paint.clear();JPWStoikusPanelEditorRender(cw,ch,1,2);check(!paint.empty(),"editor always exposes at least a cancel control");for(const auto&p:paint)check(p.x>=0&&p.y>=0&&p.w>0&&p.h>0&&p.x+p.w<=cw&&p.y+p.h<=ch,"editor geometry contained in chart");}
 paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);before=g_stoikus_panel_draft.visible_mask;JPWStoikusPanelEditorAction("CUST_NEXT");JPWStoikusPanelEditorRender(800,420,1,2);check(g_stoikus_panel_draft.visible_mask==before&&writes==0,"pagination affects no selection or saved objects");
 reset();put(JPW_COCKPIT_PREF_OBJECT,"JPWCOCKPIT|3|95|0|0|374544");put(JPW_STOIKUS_VISUAL_OBJECT,"V1|1|0|30|280|0|0|0|0|0|0|720|520|0");g_cockpit_prefs.visible_mask=0;JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==95&&g_cockpit_prefs.visible_mask==0&&g_stoikus_visual.mode==0&&writes==0,"legacy object codecs override stale runtime globals without mutating them");
 reset();put(JPW_COCKPIT_PREF_V2_OBJECT,"JPWCOCKPIT|2|31|0|0|28158");put(JPW_COCKPIT_PREF_LEGACY_OBJECT,"JPWCOCKPIT|1|0|0|0|248085");JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==1,"legacy V2 takes precedence over V1 and projects compact effective bits");put(JPW_COCKPIT_PREF_OBJECT,"JPWCOCKPIT|3|0|0|0|744255");JPWStoikusPanelLoad();check(g_stoikus_panel_prefs.visible_mask==0,"legacy V3 takes canonical precedence and preserves zero");
 reset();put(JPW_COCKPIT_PREF_OBJECT,"corrupt original");JPWStoikusPanelLoad();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_APPLY");check(!g_stoikus_panel_notice.empty()&&writes==0&&objects[JPW_COCKPIT_PREF_OBJECT].s[OBJPROP_TEXT]=="corrupt original","invalid legacy codec remains preserved with warning and no silent apply");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");JPWStoikusPanelEditorAction("CUST_OPACITY");JPWStoikusPanelEditorSuspend();check(!g_stoikus_panel_editor&&owner.empty()&&writes==0&&g_stoikus_panel_draft.visible_mask==56,"suspend hides editor and preserves draft without writes");JPWStoikusPanelEditorOpen();check(g_stoikus_panel_editor&&g_stoikus_panel_draft.visible_mask==56&&JPWStoikusPanelTransparency()==40,"reopen resumes suspended selection and appearance draft");JPWStoikusPanelEditorCancel();JPWStoikusPanelEditorOpen();check(g_stoikus_panel_draft.visible_mask==57&&JPWStoikusPanelTransparency()==30,"explicit Cancel discards suspended draft");
 reset();JPWStoikusPanelEditorOpen();JPWStoikusPanelEditorAction("CUST_TOGGLE_0");JPWStoikusPanelEditorSuspend();put(JPW_STOIKUS_PANEL_PREF_OBJECT,"V1|127|6543210");JPWStoikusPanelRecheck();JPWStoikusPanelEditorOpen();check(g_stoikus_panel_editor&&g_stoikus_panel_stale&&g_stoikus_panel_draft.visible_mask==56&&writes==0,"changed template reopens suspended draft in blocked editor state without losing it");paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);bool stale_cancel_visible=false;for(const auto&p:paint)if(p.suffix=="CUST_CANCEL")stale_cancel_visible=true;check(stale_cancel_visible,"stale resumed draft exposes an actionable visible Cancel control");before=writes;JPWStoikusPanelEditorAction("CUST_APPLY");check(g_stoikus_panel_editor&&g_stoikus_panel_stale&&writes==before&&objects[JPW_STOIKUS_PANEL_PREF_OBJECT].s[OBJPROP_TEXT]=="V1|127|6543210","blocked resumed editor cannot apply over changed template");check(JPWStoikusPanelEditorAction("CUST_CANCEL")&&!g_stoikus_panel_editor&&!g_stoikus_panel_pending,"visible Cancel action exits stale resumed editor");JPWStoikusPanelEditorOpen();check(g_stoikus_panel_draft.visible_mask==127&&g_stoikus_panel_draft.order[0]==6&&!g_stoikus_panel_stale,"cancel suspended stale draft permits fresh reviewed reopen");
 reset();JPWStoikusPanelEditorOpen();paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);for(int i=0;i<20;i++)JPWStoikusPanelEditorAction("CUST_NEXT");check(!JPWStoikusPanelFocusAt(0).empty()&&g_stoikus_panel_page==1,"pagination clamps at last populated page even before redraw");
 reset();JPWStoikusPanelEditorOpen();paint.clear();JPWStoikusPanelEditorRender(800,900,1,2);bool solid=false,up_words=false,down_words=false;for(const auto&p:paint){if(p.suffix=="CUST_BG")solid=p.transparency==0;if(p.suffix=="CUST_UP_0")up_words=p.caption=="Subir";if(p.suffix=="CUST_DOWN_0")down_words=p.caption=="Descer";}check(solid&&up_words&&down_words,"solid editor background and explicit movement verbs on roomy charts");
 before=g_stoikus_panel_draft.visible_mask;check(JPWStoikusPanelEditorKey(9,false)&&JPWStoikusPanelEditorKey(13,false)&&g_stoikus_panel_draft.visible_mask==(before^1)&&writes==0,"Tab Enter selects canonical metric in draft without writes");
 check(JPWStoikusPanelEditorKey(9,true)&&JPWStoikusPanelEditorKey(32,false)&&!g_stoikus_panel_editor&&writes==0,"reverse Tab reaches Cancel and Space cancels without writes");
 check(!JPWStoikusPanelEditorKey(9,false),"keys outside editor remain untouched");JPWStoikusPanelEditorOpen();check(JPWStoikusPanelEditorKey(27,false)&&!g_stoikus_panel_editor&&writes==0,"Escape cancels active editor");
 JPWStoikusPanelEditorOpen();check(!JPWStoikusPanelEditorKey(65,false),"unassigned editor key not interpreted as action");owner="OTHER";before=writes;check(!JPWStoikusPanelEditorKey(13,false)&&writes==before,"keyboard cannot apply with foreign focus");
 reset();JPWStoikusPanelEditorOpen();paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);g_stoikus_panel_focus=14;check(JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_DOWN_1","keyboard down crossing starts on canonical metric1 at page edge");JPWStoikusPanelEditorKey(13,false);check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft)=="V1|57|0534216"&&g_stoikus_panel_page==1&&JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_DOWN_1","down across page boundary follows the same canonical metric and action");paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);JPWStoikusPanelEditorKey(13,false);check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft)=="V1|57|0534261"&&JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_DOWN_1"&&writes==0,"repeated Enter continues moving metric1 rather than its former page neighbor");JPWStoikusPanelEditorKey(13,false);check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft)=="V1|57|0534261"&&JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_DOWN_1","last-slot boundary keeps canonical keyboard focus without changing another metric");
 reset();JPWStoikusPanelEditorOpen();paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);JPWStoikusPanelEditorAction("CUST_NEXT");paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);g_stoikus_panel_focus=1;check(JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_UP_2","keyboard up crossing starts on first metric of second page");JPWStoikusPanelEditorKey(13,false);check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft)=="V1|57|0534216"&&g_stoikus_panel_page==0&&JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_UP_2","up across page boundary follows canonical metric2 and action");paint.clear();JPWStoikusPanelEditorRender(800,420,1,2);JPWStoikusPanelEditorKey(32,false);check(JPWStoikusPanelPrefsEncode(g_stoikus_panel_draft)=="V1|57|0532416"&&JPWStoikusPanelFocusAt(g_stoikus_panel_focus)=="CUST_UP_2"&&writes==0,"repeated Space after page crossing keeps moving metric2");
 check(!JPWStoikusPanelEditorAction("OTHER")&&!JPWStoikusPanelEditorAction("CUST_TOGGLE_7"),"unrelated and invalid actions ignored");
 std::cout<<"Stoikus panel editor checks="<<checks<<" failures="<<failures<<"; native NOT_RUN\n";return failures?1:0;
}
'''

def run():
    source=(INC/'JPW_Stoikus_PanelEditor.mqh').read_text()
    hud=(INC/'JPW_Stoikus_HUD.mqh').read_text()
    signature='bool JPWStoikusVisualSave(const JPWStoikusVisual &candidate,const bool restore=false)'
    visual_save=signature+'{'+body_of(hud,signature)+'}\n'
    cockpit=(INC/'JPW_Alavancagem_Cockpit.mqh').read_text()
    signatures=['void JPWCockpitDefault(JPWCockpitPrefs &prefs,const int initial_corner=0)', 'bool JPWCockpitValid(JPWCockpitPrefs &prefs)', 'int JPWCockpitChecksumVersion(JPWCockpitPrefs &prefs,const int version)', 'int JPWCockpitChecksum(JPWCockpitPrefs &prefs)', 'string JPWCockpitEncode(JPWCockpitPrefs &prefs)', 'bool JPWCockpitParseUnsigned(const string raw,int &value)', 'bool JPWCockpitDecode(const string encoded,JPWCockpitPrefs &prefs)']
    legacy_codec='\n'.join(sig+'{'+body_of(cockpit,sig)+'}' for sig in signatures)
    code=SHIM+legacy_codec+"\n"+(INC/'JPW_Stoikus_Visual.mqh').read_text()+(INC/'JPW_Stoikus_PanelPrefs.mqh').read_text()+STATE+visual_save+source+MAIN
    print('editor_sha256='+hashlib.sha256(source.encode()).hexdigest(),flush=True)
    with tempfile.TemporaryDirectory(prefix='stoikus-panel-editor-') as folder:
        cpp=Path(folder)/'test.cpp';binary=Path(folder)/'test';cpp.write_text(translate_arrays(code))
        subprocess.run([shutil.which('clang++'),'-std=c++17','-Wall','-Wextra','-Wno-unused-parameter',str(cpp),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
if __name__=='__main__':run()

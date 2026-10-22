#!/usr/bin/env python3
"""CHG-STOIKUS-PAINEL-PERSONALIZAVEL: actual bridge + UI host replays.
No native compilation, asynchronous MT5 queue or template acceptance claim.
Run directly; this new focal is outside the unchanged accumulated gate.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile
import re

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'


def launchers(mutant=""):
    import jpw_stoikus_brand_test as replay
    from leverage_source import expanded_source
    previous = replay.MAIN
    # The baseline has no flag; supply it to expose actual renderer behavior.
    source = expanded_source(INC / 'JPW_NoCuda_Fibo_UI.mqh')
    if 'bool g_nocuda_ui_shared_access=' not in source:
        source = 'bool g_nocuda_ui_shared_access=false;\n' + source
    source = expanded_source(INC / 'JPW_UI_Focus.mqh') + source
    if mutant == 'launchers':
        source = source.replace('if(g_nocuda_ui_shared_access)', 'if(false && g_nocuda_ui_shared_access)')
    replay.MAIN = r'''int main(){int failures=0;auto check=[&](bool ok,string m){if(!ok){failures++;std::cerr<<"FAIL "<<m<<"\n";}};
    chart_width=1440;chart_height=1120;dpi=100;
    JPWNoCudaUIView manual={};manual.symbol="EURUSD";manual.source_tf="H1";
    JPWNoCudaFiboView fibo={};fibo.symbol="EURUSD";
    ObjectCreate(0,"foreign-study",OBJ_LABEL,0,0,0);
    ObjectCreate(0,"OLDUI_OPEN",OBJ_BUTTON,0,0,0);
    g_nocuda_ui_shared_access=false;JPWNoCudaUIRender("P",manual);
    check(ObjectFind(0,"PUI_OPEN")>=0,"standalone manual launcher");
    g_nocuda_ui_shared_access=true;JPWNoCudaUIRender("P",manual);
    check(ObjectFind(0,"PUI_OPEN")<0,"live Account suppresses manual launcher");
    check(ObjectFind(0,"foreign-study")>=0&&ObjectFind(0,"OLDUI_OPEN")>=0,"foreign and unknown legacy resources preserved");
    manual.open=true;JPWNoCudaUIRender("P",manual);
    check(ObjectFind(0,"PUI_NEW")>=0,"shared access preserves manual workflow");
    chart_width=220;JPWNoCudaUIRender("P",manual);
    check(ObjectFind(0,"PUI_OPEN")<0,"shared access also suppresses undersized manual launcher");chart_width=1440;
    manual.open=false;g_nocuda_ui_shared_access=false;JPWNoCudaUIRender("P",manual);
    check(ObjectFind(0,"PUI_OPEN")>=0,"manual fallback returns");
    JPWNoCudaUIClear("P");g_nocuda_ui_shared_access=false;JPWNoCudaFiboUIDraw("P",fibo);
    check(ObjectFind(0,"PFC_FC_OPEN")>=0,"standalone Fibo launcher");
    g_nocuda_ui_shared_access=true;JPWNoCudaFiboUIDraw("P",fibo);
    check(ObjectFind(0,"PFC_FC_OPEN")<0,"live Account suppresses Fibo launcher");
    fibo.open=true;JPWNoCudaFiboUIDraw("P",fibo);
    check(ObjectFind(0,"PFC_FC_CLOSE")>=0,"shared access preserves Fibo window");
    fibo.open=false;g_nocuda_ui_shared_access=false;JPWNoCudaFiboUIDraw("P",fibo);
    check(ObjectFind(0,"PFC_FC_OPEN")>=0,"Fibo fallback returns");
    std::cout<<"launcher host failures="<<failures<<"; native NOT_RUN\n";return failures?1:0;}
    '''
    try:
        replay.verify_header_render('clang++', source)
    finally:
        replay.MAIN = previous




def bridge(mutant=''):
    """Compile the production header twice: separate indicator memory + queued events."""
    header = (INC / 'JPW_Stoikus_PanelBridge.mqh').read_text()
    if mutant == 'ttl':
        header = header.replace('now-g_jpw_panel_seen<=JPW_STOIKUS_PANEL_TTL_MS', 'true')
    header = re.sub(r'^#(?:ifndef|endif).*\n', '', header, flags=re.M)
    shim = r'''
#include <string>
#include <vector>
#include <cmath>
#include <iostream>
using string=std::string;using ulong=unsigned long;
const int CHARTEVENT_CUSTOM=1000;
ulong tick=100,micro=300;bool dispatch_ok=true;
ulong GetTickCount64(){return tick;}ulong GetMicrosecondCount(){return ++micro;}
int StringLen(const string&s){return s.size();}bool MathIsValidNumber(double v){return std::isfinite(v);}double MathFloor(double v){return std::floor(v);}
struct Event{int id;long lp;double dp;string sp;};std::vector<Event> queue;
bool EventChartCustom(int chart,int id,long lp,double dp,string sp){if(chart!=0||!dispatch_ok)return false;queue.push_back({CHARTEVENT_CUSTOM+id,lp,dp,sp});return true;}
'''
    source = shim + '\nnamespace account{\n' + header + '\n}\nnamespace nocuda{\n' + header + '\n}\n'
    source += r'''
const string ao="JPW_LEV_17_",no="JPWNC_17_14322_";int opens=0,checks=0,failed=0;
void check(bool ok,string msg){checks++;if(!ok){failed++;std::cerr<<"FAIL "<<msg<<"\n";}}
void pump(){int count=0;while(!queue.empty()){if(++count>100){check(false,"handshake bounded; no event storm");queue.clear();return;}auto e=queue.front();queue.erase(queue.begin());bool opened=false;
 check(account::JPWStoikusPanelReceive(e.id,e.lp,e.dp,e.sp,true,ao,opened),"account consumes bridge event");check(!opened,"account never handles open");
 check(nocuda::JPWStoikusPanelReceive(e.id,e.lp,e.dp,e.sp,false,no,opened),"NoCuda consumes bridge event");if(opened)opens++;}}
void cleanup(){account::JPWStoikusPanelDepart(true,ao);nocuda::JPWStoikusPanelDepart(false,no);queue.clear();}
int main(){
 for(bool account_first:{true,false}){
  cleanup();tick+=100;
  if(account_first){account::JPWStoikusPanelAnnounce(true,ao);pump();check(!account::JPWStoikusPanelPeerReady(true),"standalone Account absent NoCuda");nocuda::JPWStoikusPanelAnnounce(false,no);}
  else{nocuda::JPWStoikusPanelAnnounce(false,no);pump();check(!nocuda::JPWStoikusPanelPeerReady(false),"standalone NoCuda fallback");account::JPWStoikusPanelAnnounce(true,ao);}
  pump();check(account::JPWStoikusPanelPeerReady(true)&&nocuda::JPWStoikusPanelPeerReady(false),"both attach orders discover peer");
  int before=opens;check(account::JPWStoikusPanelOpenNoCuda(ao),"known NoCuda open enqueued");pump();check(opens==before+1,"one addressed open");
  account::JPWStoikusPanelOpenNoCuda(ao);pump();check(opens==before+2,"repeat request delivered; UI decides idempotence");
  bool requested=true;long open=5;int id=CHARTEVENT_CUSTOM+JPW_STOIKUS_PANEL_EVENT;
  double token=account::g_jpw_panel_token;
  check(nocuda::JPWStoikusPanelReceive(id,open,token,"OTHER",false,no,requested)&&!requested,"wrong target refused");
  token+=1;nocuda::JPWStoikusPanelReceive(id,open,token,no,false,no,requested);check(!requested,"unknown requester ticket refused");
  token=std::nan("");nocuda::JPWStoikusPanelReceive(id,open,token,no,false,no,requested);check(!requested,"nonfinite ticket refused");
  token=1.5;nocuda::JPWStoikusPanelReceive(id,open,token,no,false,no,requested);check(!requested,"fractional ticket refused");
  token=account::g_jpw_panel_token;
  check(!nocuda::JPWStoikusPanelReceive(id+1,open,token,no,false,no,requested),"unrelated custom route preserved");
  long depart=3;nocuda::JPWStoikusPanelReceive(id,depart,token,"OTHER",false,no,requested);check(nocuda::JPWStoikusPanelPeerReady(false),"foreign departure preserves peer");
  nocuda::JPWStoikusPanelDepart(false,"OTHER");check(nocuda::JPWStoikusPanelPeerReady(false),"wrong local cleanup preserves admitted resources");
  tick+=15000;check(nocuda::JPWStoikusPanelPeerReady(false),"TTL exact boundary accepted");
  tick++;check(!nocuda::JPWStoikusPanelPeerReady(false)&&!account::JPWStoikusPanelPeerReady(true),"lost departure times out with fallback");
  nocuda::JPWStoikusPanelReceive(id,open,token,no,false,no,requested);check(!requested,"stale open refused after timeout");
  check(!account::JPWStoikusPanelOpenNoCuda(ao),"stale peer cannot receive new request");
  account::JPWStoikusPanelAnnounce(true,ao);pump();check(nocuda::JPWStoikusPanelPeerReady(false)&&account::JPWStoikusPanelPeerReady(true),"timer rediscovers expired peers");
  tick=1;check(!nocuda::JPWStoikusPanelPeerReady(false),"clock rollback fails closed");tick+=20000;
  account::JPWStoikusPanelAnnounce(true,ao);pump();
  account::JPWStoikusPanelDepart(true,ao);pump();check(!nocuda::JPWStoikusPanelPeerReady(false),"Account departure restores fallback immediately");
  bool opened=false;nocuda::JPWStoikusPanelReceive(id,open,token,no,false,no,opened);check(!opened,"departed requester cannot open");
 }
 cleanup();tick+=100;account::JPWStoikusPanelAnnounce(true,ao);nocuda::JPWStoikusPanelAnnounce(false,no);pump();
 const double old=account::g_jpw_panel_token;account::JPWStoikusPanelDepart(true,ao);queue.clear();tick++;
 account::JPWStoikusPanelAnnounce(true,ao);pump();bool requested=false;long open=5;
 nocuda::JPWStoikusPanelReceive(CHARTEVENT_CUSTOM+JPW_STOIKUS_PANEL_EVENT,open,old,no,false,no,requested);
 check(!requested,"previous requester instance ticket rejected after restart");
 dispatch_ok=false;check(!account::JPWStoikusPanelOpenNoCuda(ao),"event enqueue failure reported");dispatch_ok=true;
 cleanup();int before=queue.size();account::JPWStoikusPanelDepart(true,ao);check(queue.size()==before,"failed/unadmitted init cannot depart another instance");
 account::JPWStoikusPanelAnnounce(true,string(64,'A'));check(queue.empty()&&!account::JPWStoikusPanelPeerReady(true),"overlength owner rejected without truncation");
 std::cout<<"actual bridge checks="<<checks<<" failures="<<failed<<"; native NOT_RUN\n";return failed?1:0;}
'''
    # Production objects are deliberately absent from this translation unit:
    # only live receive events can make peers ready.
    compile_run(source, 'bridge')


def compile_run(source, name):
    with tempfile.TemporaryDirectory(prefix='stoikus-panel-bridge-') as folder:
        cpp = Path(folder) / (name + '.cpp')
        binary = Path(folder) / name
        cpp.write_text(source)
        subprocess.run(['clang++', '-std=c++17', str(cpp), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


def actual_open():
    from leverage_panel_test import body_of
    indicator = (ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5').read_text()
    body = body_of(indicator, 'void JPWNoCudaOpenFromPanel(')
    source = r'''
#include <string>
#include <iostream>
using string=std::string;
bool g_nocuda_initialized=true,g_nocuda_resources_admitted=true,g_nocuda_panel_open=false,g_ncf_mode=false,context=true;
string g_nocuda_prefix="NC",focus="",draft="unsaved draft";struct View{bool open=false;}g_ncf_ui;int actions=0,draws=0;
string JPWUIOwner(){return focus;}bool JPWNCFContextCurrent(){return context;}
void JPWNCFAction(string a){if(a!="FC_OPEN")throw 1;actions++;focus=g_nocuda_prefix;g_ncf_mode=true;g_ncf_ui.open=true;}
void JPWNoCudaDrawUI(){draws++;}void ChartRedraw(int){}
'''
    source += 'void JPWNoCudaOpenFromPanel(){' + body + '}\n'
    source += r'''int main(){int failed=0;auto check=[&](bool ok,string m){if(!ok){failed++;std::cerr<<"FAIL "<<m<<"\n";}};
 focus="OTHER";JPWNoCudaOpenFromPanel();check(actions==0&&focus=="OTHER","unrelated editor focus respected");
 focus="";context=false;JPWNoCudaOpenFromPanel();check(actions==0,"context validation retained");context=true;
 g_nocuda_resources_admitted=false;JPWNoCudaOpenFromPanel();check(actions==0,"unadmitted init cannot open");g_nocuda_resources_admitted=true;
 g_nocuda_initialized=false;JPWNoCudaOpenFromPanel();check(actions==0,"failed init cannot open");g_nocuda_initialized=true;
 JPWNoCudaOpenFromPanel();check(actions==1&&g_ncf_ui.open&&focus=="NC","validated existing FC_OPEN route");
 JPWNoCudaOpenFromPanel();JPWNoCudaOpenFromPanel();check(actions==1&&g_ncf_ui.open,"repeat open never closes/reloads active window");
 g_ncf_ui.open=false;g_nocuda_panel_open=true;JPWNoCudaOpenFromPanel();check(actions==1&&g_nocuda_panel_open,"existing manual window preserved");
 check(draft=="unsaved draft","draft unchanged and no confirm action");
 std::cout<<"actual open flow failures="<<failed<<"; native NOT_RUN\n";return failed?1:0;}
'''
    compile_run(source, 'open')


def integrated_lifecycle():
    """Reuse the approved lifecycle builder and all its cases unchanged."""
    import sys
    import jpw_nocuda_lifecycle_test as lifecycle
    code, _, _ = lifecycle.build()
    with tempfile.TemporaryDirectory(prefix='stoikus-bridge-lifecycle-') as folder:
        cpp = Path(folder) / 'lifecycle.cpp'
        binary = Path(folder) / 'lifecycle'
        cpp.write_text(code)
        cmd = ['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-Wno-deprecated-declarations', str(cpp), '-o', str(binary), '-lsqlite3']
        if sys.platform != 'darwin':
            cmd.append('-lcrypto')
        subprocess.run(cmd, check=True)
        subprocess.run([str(binary), folder], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--launchers-only', action='store_true')
    parser.add_argument('--mutant', choices=['ttl', 'launchers'], default='')
    args = parser.parse_args()
    if not args.launchers_only:
        bridge(args.mutant)
        actual_open()
        integrated_lifecycle()
    launchers(args.mutant)

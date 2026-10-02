#!/usr/bin/env python3
"""Execute production Signal Copy controller/UI with synthetic terminal/widget APIs.

No real account, OS clipboard, Wine or MetaEditor is accessed. Pure message core
is production code; native reads/files/widgets are isolated compatibility APIs.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
import leverage_config_test as base
import jpw_signal_copy_test as core
ROOT=Path(__file__).resolve().parents[1]
MQL=ROOT/'mt5/jpw-alavancagem-atual/MQL5'
INC=MQL/'Include/JPWealth'
FILES=core.FILES[:4]+[INC/'JPW_SignalCopy_Controller.mqh',INC/'JPW_SignalCopy_UI.mqh']
SHIM=r'''
using color=int;
constexpr int CORNER_LEFT_UPPER=0,OBJ_EDIT=1,OBJPROP_CORNER=2,OBJPROP_XDISTANCE=3,
 OBJPROP_YDISTANCE=4,OBJPROP_XSIZE=5,OBJPROP_YSIZE=6,OBJPROP_COLOR=7,
 OBJPROP_BGCOLOR=8,OBJPROP_BORDER_COLOR=9,OBJPROP_FONTSIZE=10,
 OBJPROP_READONLY=11,OBJPROP_ZORDER=12,OBJPROP_HIDDEN=13,OBJPROP_FONT=14,
 OBJPROP_TEXT=15,OBJPROP_TOOLTIP=16,OBJPROP_STATE=17;
constexpr int JPW_ACTION_CLOSE=37,JPW_ACTION_PREVIOUS=38,JPW_ACTION_NEXT=39,
 JPW_ROUTE_OVERVIEW=7;
constexpr long InpGenesisTicket=0;
int g_raiz_tab=16,g_cockpit_page=0,g_details_font=11,g_details_line=20,
 g_details_control=30,g_details_pad=8,g_details_text=0,g_details_card=1,g_details_border=2;
bool g_raiz_details_open=true;
struct Widget{string text;int x=0,y=0,w=0,h=0;};
std::map<string,Widget> widgets;
std::map<string,std::map<int,string>> strings;
int reads=0,metric_reads=0,resets=0,draws=0;bool changed=false,fail_metrics=false;
bool deferred=false;JPWAccount account_fixture;JPWSignalCapture capture_fixture;
std::vector<JPWSignalRow> rows_fixture;
string JPWRaizUI(const string&s){return "UI_"+s;}
string JPWActionObject(int i){return JPWRaizUI("BUTTON_"+IntegerToString(i));}
void JPWRaizPanelDestroy(){widgets.clear();strings.clear();}
void JPWRenderRaizDetails(){draws++;}
void ChartRedraw(int){}
int JPWPanelClamp(int n,int lo,int hi){return std::min(std::max(n,lo),hi);}
bool JPWRaizCreateLabel(const string&s,const string&t,int x,int y,int f=0){
 widgets[JPWRaizUI(s)]={t,x,y,100,g_details_line};return true;}
bool JPWCreateProtectedValue(const string&s,const string&t,int x,int y,int w,int f=0){
 widgets[JPWRaizUI(s)]={t,x,y,w,g_details_line};return true;}
bool JPWRaizCreateButton(int id,const string&t,int x,int y,int w){
 widgets[JPWActionObject(id)]={t,x,y,w,g_details_control};return true;}
void JPWDetailsWrap(const string&s,int width,std::vector<string>&lines){
 const int size=std::max(1,width/8);for(size_t p=0;p<s.size();p+=size)lines.push_back(s.substr(p,size));}
int ObjectFind(int,const string&n){return widgets.count(n)?0:-1;}
bool ObjectCreate(int,const string&n,int,int,int,int){widgets[n]=Widget();return true;}
bool ObjectDelete(int,const string&n){widgets.erase(n);strings.erase(n);return true;}
bool ObjectSetInteger(int,const string&n,int p,long v){auto&w=widgets[n];
 if(p==OBJPROP_XDISTANCE)w.x=v;if(p==OBJPROP_YDISTANCE)w.y=v;
 if(p==OBJPROP_XSIZE)w.w=v;if(p==OBJPROP_YSIZE)w.h=v;return true;}
bool ObjectSetString(int,const string&n,int p,const string&s){strings[n][p]=s;return true;}
string ObjectGetString(int,const string&n,int p){return strings[n][p];}
// MQL5 ArrayCopy grows a destination if necessary but never shrinks it.
template<class T>int ArrayCopy(std::vector<T>&to,const std::vector<T>&from){
 if(to.size()<from.size())to.resize(from.size());
 std::copy(from.begin(),from.end(),to.begin());return (int)from.size();}
bool JPWReadAccount(JPWAccount&a){a=account_fixture;return a.login>0;}
void JPWSignalTerminalReset(){resets++;}
bool JPWSignalAdapterDeferred(){return deferred;}
bool JPWSignalCollect(JPWSignalCapture&c,std::vector<JPWSignalRow>&r,string&why,ulong){reads++;c=capture_fixture;r=rows_fixture;return true;}
bool JPWSignalRevalidate(JPWSignalCapture&,std::vector<JPWSignalRow>&,string&why,ulong,bool require_recent=true){reads++;why=changed?"TP mudou":"";return !changed;}
bool JPWSignalRenewCapture(JPWSignalCapture&c,std::vector<JPWSignalRow>&r,string&why,ulong started){return JPWSignalRevalidate(c,r,why,started);}
bool JPWSignalReadReference(JPWSignalCapture&,std::vector<JPWSignalRow>&,int,long,int&row,long&id,bool&closed,string&why,ulong){reads++;row=-1;id=0;closed=false;return true;}
bool JPWSignalCollectMetrics(JPWSignalCapture&,std::vector<JPWSignalRow>&,int,JPWSignalMetrics&m,string&why,ulong){
 reads++;metric_reads++;
 m.leverage_valid=m.scenario_valid=m.floating_valid=m.root_valid=m.stop_valid=!fail_metrics;
 m.leverage=2.75;m.scenario_leverage=3.5;m.floating_percent=-2.62;
 m.factor=1.5;m.n_1w=30;m.n_2w=60;m.atr=.004;
 m.root_1w=100*.004*std::sqrt(30.)*1.5/.5661;m.root_2w=100*.004*std::sqrt(60.)*1.5/.5661;
 m.bid=.566;m.ask=.5662;m.point=.00001;m.tick_size=.00001;
 m.quote_time_msc=1790875200000;m.atr_bar_time=1790860800;
 m.leverage_quality=m.root_quality=m.quote_quality=m.floating_quality=1;
 why=fail_metrics?"ATR indisponível":"";return !fail_metrics;}
datetime TimeGMT(){return 1790875200;}
'''
MAIN=r'''
void JPWRaizSwitchTab(const int tab){g_raiz_tab=tab;g_cockpit_page=0;}
int checks=0,failures=0;
void check(bool c,const string&s){checks++;if(!c){failures++;std::cerr<<"FAIL "<<s<<'\n';}}
JPWSignalRow row(int kind,int side,ulong ticket,long opened){JPWSignalRow r;
 r.kind=kind;r.side=side;r.ticket=ticket;r.identifier=kind==1?ticket:0;r.symbol="NZDUSD.m";
 r.opened_msc=opened;r.updated_msc=opened;r.order_type=side==0?ORDER_TYPE_BUY_LIMIT:ORDER_TYPE_SELL_LIMIT;
 r.order_state=1;r.volume=.08;r.initial_volume=.08;r.entry=.57585;r.sl=.54481;r.tp=.6285;
 r.stop_limit=0;r.expiration=0;r.digits=5;r.volume_digits=2;return r;}
void setup(){JPWSignalClear();g_raiz_tab=JPW_SIGNAL_ROUTE;g_raiz_details_open=true;
 account_fixture.login=77;account_fixture.server="SYNTHETIC";account_fixture.currency="USD";
 capture_fixture.account=account_fixture;capture_fixture.context="opaque-synthetic";
 capture_fixture.digest="rows-digest";capture_fixture.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
 capture_fixture.reference_closed=false;capture_fixture.reference_identifier=0;
 capture_fixture.balance=100;capture_fixture.equity=97.38;capture_fixture.profit=-2.62;capture_fixture.credit=0;
 capture_fixture.observed_utc=1790875200;capture_fixture.accepted_ms=GetTickCount64();
 rows_fixture={row(1,0,9007199254740991UL,100),row(1,0,92,200),row(2,1,93,300)};
 changed=false;fail_metrics=false;deferred=false;widgets.clear();strings.clear();}
void click(int action){JPWSignalHandleClick(JPWActionObject(action));}
void timer(){JPWSignalProcessRequests(GetTickCount64());}
void draw(int h=380,int line=20,int control=30,int pad=8){
 widgets.clear();strings.clear();g_details_line=line;g_details_control=control;g_details_pad=pad;
 JPWSignalRenderBody(10,100,500,h,100+h+40);}
int main(int argc,char**argv){file_root=argv[1];setup();
 JPWSignalOpen();check(reads==0&&g_signal_catalog_requested,"opening enqueues without financial read");
 timer();check(g_signal_known&&rows_fixture.size()==g_signal_rows.size(),"timer accepts direct catalogue");
 const int before=reads;draw();draw();check(reads==before,"redraw does not read financial data");
 check(widgets[JPWActionObject(JPW_SIGNAL_ROW_FIRST)].text.find("Buy")!=string::npos,"BUY=0 catalogue label correct");
 click(JPW_SIGNAL_PENDING_LIST);draw();check(widgets[JPWActionObject(JPW_SIGNAL_ROW_FIRST)].text.find("Sell")!=string::npos,"SELL=1 pending label correct");
 click(JPW_SIGNAL_POSITIONS);draw();click(JPW_SIGNAL_ROW_FIRST);
 check(reads==before&&g_signal_select_requested>=0,"selection requests reference read rather than collecting on click");
 timer();check(g_signal_stage==JPW_SIGNAL_STRUCTURE&&g_signal_members.size()==2,"selected exact group does not include other direction");
 draw();click(JPW_SIGNAL_INCLUDE_FIRST+1);check(!g_signal_members[1].included,"exclude another-thesis item transiently");
 click(JPW_SIGNAL_INCLUDE_FIRST);check(g_signal_members[0].included,"selected item cannot be excluded");
 click(JPW_SIGNAL_CONFIRM);check(g_signal_preview_requested,"conference requests production message calculation");
 timer();check(g_signal_stage==JPW_SIGNAL_PREVIEW&&!g_signal_message.empty(),"valid required metrics yield frozen preview");
 const string frozen=g_signal_message;const int mr=metric_reads;draw();draw();check(g_signal_message==frozen&&metric_reads==mr,"navigation/resize preserve frozen prices and bytes");
 click(JPW_SIGNAL_PREPARE);timer();check(g_signal_stage==JPW_SIGNAL_TEXT,"prepare revalidates before text field");
 draw();check(strings[JPWRaizUI("EDIT_SIGNAL_COPY")][OBJPROP_TEXT]==frozen,"copy object stores entire multiline source with accents/ticket, not OS clipboard proof");
 click(JPW_SIGNAL_SAVE);check(!fs::exists(file_root/"JPWealth"/"SignalCopy"),"export click writes no file until timer");
 timer();int files=0;string exported;
 for(auto&p:fs::directory_iterator(file_root/"JPWealth"/"SignalCopy")){
  files++;std::ifstream f(p.path(),std::ios::binary);exported.assign(std::istreambuf_iterator<char>(f),{});
  check(p.path().filename().string().find("9007199254740991")==string::npos,"export filename excludes ticket");}
 check(files==1&&exported==frozen,"explicit local export byte-exact UTF8 with no trailing NUL");
 draw(184,96,128,32);click(JPW_SIGNAL_INFO);draw(184,96,128,32);
 check(g_signal_show_notice&&widgets.count(JPWRaizUI("SIGNAL_LINE_0")),"compact mode provides accessible export path/result page");
 click(JPW_SIGNAL_INFO);
 string reason;inject_short_write=true;check(!JPWSignalExportText(reason),"partial write not reported as success");inject_short_write=false;
 changed=true;click(JPW_SIGNAL_SAVE);timer();check(g_signal_stale&&g_signal_message.empty(),"TP change blocks export and removes old copy field");
 setup();JPWSignalOpen();timer();draw();click(JPW_SIGNAL_ROW_FIRST);timer();draw();click(JPW_SIGNAL_CONFIRM);
 fail_metrics=true;timer();check(g_signal_message.empty()&&g_signal_notice.find("bloqueada")!=string::npos,"missing ATR strictly blocks preparation");
 setup();JPWSignalOpen();timer();account_fixture.login=88;timer();check(!g_signal_known&&g_signal_stale,"account switch invalidates copy context");
 setup();JPWSignalOpen();timer();g_signal_stage=JPW_SIGNAL_TEXT;g_signal_message="private draft";g_signal_export_requested=true;
 JPWSignalClear();timer();check(g_signal_message.empty()&&!g_signal_export_requested,"close/reset discards pending export and transient message");
 setup();JPWSignalOpen();timer();draw(184,96,128,32);
 for(auto&[n,w]:widgets)if(n.find("BUTTON_200")!=string::npos)check(w.y+w.h<=284,"DPI200/font24 catalogue control fits content rectangle");
 check(g_signal_button_count>=1&&widgets.count(JPWRaizUI("SIGNAL_VOLUME_0"))==0,"compact catalogue exposes a row without overlapping extra volume");
 click(JPW_SIGNAL_ROW_FIRST);timer();draw(184,96,128,32);
 check(g_signal_member_count==1,"compact structure retains paginated member access");
 g_cockpit_page=3;draw(184,96,128,32);check(widgets.count(JPWActionObject(JPW_SIGNAL_INCLUDE_FIRST))==1,"compact member include action reachable");
 g_cockpit_page=4;draw(184,96,128,32);check(widgets.count(JPWActionObject(JPW_SIGNAL_ROLE_FIRST))==1,"compact role action reachable");
 for(auto&[n,w]:widgets)if(n.find("BUTTON_280")!=string::npos)check(w.y+w.h<=284,"compact role control remains above footer");
 click(JPW_SIGNAL_ROLE_FIRST);draw(184,96,128,32);
 check(g_signal_role_edit==0,"role edit opens explicit transient number field");
 strings[JPWRaizUI("EDIT_SIGNAL_ROLE")][OBJPROP_TEXT]="4";click(JPW_SIGNAL_ROLE_APPLY);
 check(g_signal_members[0].role==5&&g_signal_role_edit==-1,"Defense4 can be selected even when other defenses no longer open");
 g_cockpit_page=4;draw(184,96,128,32);click(JPW_SIGNAL_ROLE_FIRST);draw();
 strings[JPWRaizUI("EDIT_SIGNAL_ROLE")][OBJPROP_TEXT]="22";JPWSignalSaveDraft();
 draw();check(strings[JPWRaizUI("EDIT_SIGNAL_ROLE")][OBJPROP_TEXT]=="22","resize preserves transient role draft");
 click(JPW_SIGNAL_ROLE_CANCEL);check(g_signal_members[0].role==5,"role Cancel preserves prior confirmed role");
 setup();JPWSignalOpen();timer();JPWSignalSetSelected(0,GetTickCount64());
 rows_fixture.erase(rows_fixture.begin());click(JPW_SIGNAL_UPDATE);timer();
 check(g_signal_known&&!g_signal_stale&&g_signal_rows.size()==2&&g_signal_rows[0].ticket==92&&g_signal_rows[1].ticket==93,
       "refresh after selected position closes replaces 3-row catalogue with exactly2 rows");
 check(g_signal_selected==-1&&g_signal_members.empty()&&g_signal_message.empty(),"catalogue refresh clears previous selection, roles and preview");
 check(!JPWSignalSetSelected(2,GetTickCount64()),"removed catalogue tail is not selectable");
 draw();check(g_signal_button_count==1,"remaining positions list excludes closed item and pending section");
 rows_fixture.clear();click(JPW_SIGNAL_UPDATE);timer();
 check(g_signal_known&&!g_signal_stale&&g_signal_rows.empty()&&g_signal_selected==-1,"refresh from2 rows to zero confirms empty current catalogue");
 draw();check(g_signal_button_count==0,"empty catalogue offers no stale position action");
 std::cout<<"HOST_SIGNAL_COPY_UI: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native clipboard/geometry NOT_RUN\n";return failures?1:0;
}
'''
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path);args=parser.parse_args()
    compiler=shutil.which('clang++') or shutil.which('g++')
    if not compiler: raise RuntimeError('host compiler absent')
    source='\n'.join(core.translate(p.read_text()) for p in FILES[:4])
    controller=core.translate(FILES[4].read_text()).replace('"%I64d"','"%ld"')
    ui=core.translate(FILES[5].read_text())
    identity={'kind':'HOST_SYNTHETIC_NOT_MT5','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES},'native_copy':'NOT_RUN'}
    if args.evidence_dir: args.evidence_dir.mkdir(parents=True,exist_ok=False)
    receipts=[]
    with tempfile.TemporaryDirectory(prefix='jpw-signal-ui-') as tmp:
        tmp=Path(tmp);cpp=tmp/'ui.cpp';binary=tmp/'ui';files=tmp/'isolated-files';files.mkdir()
        prefix=core.EXTRA_SHIM.split('int main(){')[0]
        cpp.write_text(base.SHIM+'\n'+prefix+'\n'+source+'\n'+SHIM+'\n'+controller+'\n'+ui+'\n'+MAIN)
        if args.evidence_dir: shutil.copy2(cpp,args.evidence_dir/'ui.cpp')
        for cmd in ([compiler,'-std=c++17','-Wno-deprecated-declarations',str(cpp),'-o',str(binary)]+([] if sys.platform=='darwin' else ['-lcrypto']),[str(binary),str(files)]):
            result=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
            print(result.stdout,end='');print(result.stderr,end='')
            receipts.append({'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
            if result.returncode: break
    identity['receipts']=receipts
    if args.evidence_dir:(args.evidence_dir/'receipt.json').write_text(json.dumps(identity,indent=2)+'\n')
    return receipts[-1]['returncode']
if __name__=='__main__': raise SystemExit(main())

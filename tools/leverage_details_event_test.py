#!/usr/bin/env python3
"""Run indicator event/draft functions with a synthetic host/UI boundary.

Covers stale-account guards, visual preference Apply/Cancel/reset, click and
keyboard routing, plus legacy F drafts. Native MQL/MT5 interaction is NOT_RUN.
"""
from pathlib import Path
from leverage_source import expanded_source
import hashlib
import json
import shutil
import subprocess
import tempfile
from leverage_panel_test import body_of

ROOT = Path(__file__).resolve().parents[1]
IND = ROOT/'mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5'
STORE = ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh'
COCKPIT = ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh'
SHIM = r'''
#include <string>
#include <climits>
#include <map>
#include <array>
#include <vector>
#include <cstdio>
#include <cmath>
#include <sstream>
#include <iomanip>
#include <iostream>
using string=std::string; using ushort=unsigned short;using ulong=unsigned long;
constexpr int CORNER_LEFT_LOWER=1,CORNER_RIGHT_UPPER=2,CORNER_RIGHT_LOWER=3;
constexpr int TERMINAL_KEYSTATE_SHIFT=1;
int TerminalInfoInteger(int){return 0;}
constexpr int CHARTEVENT_CHART_CHANGE=1, CHARTEVENT_OBJECT_ENDEDIT=2, CHARTEVENT_KEYDOWN=3,CHARTEVENT_OBJECT_CLICK=4;
constexpr int OBJPROP_TEXT=1,OBJPROP_STATE=2,JPW_RAIZN_VALID=1,JPW_RAIZN_ABSENT=0;
constexpr int OBJPROP_CORNER=3,OBJPROP_XDISTANCE=4,OBJPROP_YDISTANCE=5,OBJPROP_FONTSIZE=6;
constexpr int OBJPROP_SELECTABLE=7,OBJPROP_HIDDEN=8,OBJPROP_TYPE=9,OBJ_LABEL=1,CORNER_LEFT_UPPER=0,InpCorner=0;
constexpr double JPW_RAIZN_FACTOR_DEFAULT=1.5;
long StringToInteger(const string&s){try{return std::stol(s);}catch(...){return 0;}}
int StringFind(const string&s,const string& needle){auto pos=s.find(needle);return pos==string::npos?-1:(int)pos;}
string IntegerToString(long x){return std::to_string(x);}
int StringLen(const string &s){return (int)s.size();}
ushort StringGetCharacter(const string &s,int i){return (ushort)s.at(i);}
int StringSplit(const string &s,char delimiter,std::vector<string> &out){
 out.clear();size_t from=0;
 for(size_t i=0;i<=s.size();i++)if(i==s.size()||s[i]==delimiter){out.push_back(s.substr(from,i-from));from=i+1;}
 return (int)out.size();}
template<typename... A> string StringFormat(const char* fmt,A...args){char out[160];std::snprintf(out,sizeof(out),fmt,args...);return out;}
string StringFormat(const char*,const string &server,long login,const string &currency){
 return server+"|"+std::to_string(login)+"|"+currency;}
double StringToDouble(const string&s){try{return std::stod(s);}catch(...){return 0.;}}
bool MathIsValidNumber(double x){return std::isfinite(x);}
string DoubleToString(double v,int digits){std::ostringstream o; if(digits<0)o<<std::scientific<<std::setprecision(-digits)<<v; else o<<std::fixed<<std::setprecision(digits)<<v;return o.str();}
struct JPWAccount {long id=0;long login=42;string server="synthetic";string currency="USD";};
struct Config {long generation=0;int n=0;double f=0.;string n_reason,f_reason;};
struct FactorPreference {long generation=0;double factor=0.;};
struct Scenario {string scenario_id;};
JPWAccount g_account,g_raiz_draft_account,current_account;
Config g_live_config; Scenario g_raiz_scenario;
FactorPreference g_factor_preference;
bool g_refresh_requested=false,g_record_read_requested=false,g_editing_field=false;
int g_focus_action=-1,g_focus_count=0,g_hud_summary_source=-1;
string g_sample_context="synthetic-context",g_export_preview,g_export_result;
bool g_export_preview_requested=false,g_export_requested=false;
int g_diagnostic_pending=0;constexpr int JPW_DIAG_SETTINGS_APPLIED=8;
void JPWQueueDiagnostic(int code){g_diagnostic_pending|=(1<<code);}
void JPWFocusStep(bool){}
bool g_account_known=true,g_raiz_draft_account_known=false,g_raiz_details_open=false,g_raiz_panel_built=false;
int g_raiz_tab=4,g_raiz_page=0,g_raiz_pages=5,g_raiz_store_state=JPW_RAIZN_ABSENT,g_live_config_state=JPW_RAIZN_VALID;
int g_cockpit_selected=0,g_cockpit_page=0,g_cockpit_template_recheck=0;
int g_stop_button_count=0,g_stop_button_row[16],g_stop_selected_row=-1;
string g_stop_button_role[16],g_stop_selected_role;
bool g_cockpit_pref_invalid=false,g_cockpit_reset_requested=false,g_hud_summary=false,g_stops_show_pending=false;
string g_cockpit_pref_notice;
JPWCockpitPrefs g_cockpit_prefs,g_cockpit_draft;
JPWCockpitSnapshot g_cockpit_snapshot;
long g_live_draft_generation=0;
long g_factor_draft_generation=0;
double g_factor_draft=0.;
int g_factor_state=JPW_RAIZN_ABSENT;
std::array<string,21> g_raiz_fields;
string g_panel_prefix="INSTANCE_",_Symbol="NZDUSD.exact",g_raiz_draft_symbol,g_raiz_draft_expected_id,g_raiz_feedback,g_factor_reason,g_panel_value,g_panel_status;
std::map<string,string> objects;
int refreshes=0,apply=0,factor_apply=0,legacy_apply=0,bind=0,compare=0,drawn_account=0,metric_account=0,mdd_reads=0,destructions=0,hud_renders=0;
bool account_available=true,flip_after_mdd=false;
string JPWRaizUI(const string&s){return g_panel_prefix+"RAIZ_UI_"+s;}
bool JPWReadAccount(JPWAccount&a){a=current_account;return account_available;}
bool JPWAccountsEqual(JPWAccount&a,JPWAccount&b){return a.id==b.id;}
bool ObjectSetInteger(int,const string&,int,long){return true;}
int ObjectFind(int,const string&name){return objects.count(name)?0:-1;}
int ObjectGetInteger(int,const string&,int){return OBJ_LABEL;}
string ObjectGetString(int,const string&name,int){return objects[name];}
bool ObjectCreate(int,const string&name,int,int,int,int){objects[name]="";return true;}
bool ObjectSetString(int,const string&name,int,const string &value){objects[name]=value;return true;}
bool ObjectDelete(int,const string&name){objects.erase(name);return true;}
void ChartRedraw(int){}
int JPWPanelClamp(int v,int a,int b){return v<a?a:(v>b?b:v);}
void JPWRaizPanelDestroy(){for(auto i=objects.begin();i!=objects.end();){
 if(i->first.find("RAIZ_UI_")!=string::npos)i=objects.erase(i);else ++i;}
 g_raiz_panel_built=false;destructions++;}
bool JPWDetailsContextCurrent();
void JPWRenderRaizDetails(){if(g_raiz_details_open&&JPWDetailsContextCurrent()){drawn_account=metric_account;g_raiz_panel_built=true;}}
void JPWRender(const string&,const string&){JPWRenderRaizDetails();}
void JPWRenderHUD(){hud_renders++;}
void JPWRenderCurrentDisplay(){JPWRenderRaizDetails();}
void JPWInvalidateIdentityPresentation(){g_raiz_details_open=false;g_raiz_draft_account_known=false;g_sample_context="";JPWRaizPanelDestroy();}
string JPWActionObject(int action){return JPWRaizUI("BUTTON_"+IntegerToString(action));}
void JPWCollectRaizN(){}
void JPWCollectRaizScenario(){}
void JPWRaizPopulateFields(){for(int i=0;i<17;i++)g_raiz_fields[i]="";}
void JPWDetailsReadMDD(){mdd_reads++;if(flip_after_mdd)current_account.id++;}
void JPWDetailsReadObserver(){}
void JPWDetailsReadStopRisk(){}
void JPWBuildPresentation(const string&,const string&){
 g_cockpit_snapshot.symbol=_Symbol;
 g_cockpit_snapshot.account_key=g_account.server+"|"+std::to_string(g_account.login)+"|"+g_account.currency;}
void JPWRefresh(){refreshes++;g_account=current_account;metric_account=(int)current_account.id;
 if(g_raiz_details_open&&(!account_available||g_raiz_draft_account.id!=current_account.id)){
 g_raiz_details_open=false;JPWRaizPanelDestroy();}}
void JPWLiveApply(){apply++;}
bool JPWRaizNFactorAllowed(double f){return f==1.5||f==1.8;}
void JPWRaizFeedback(const string&m){g_raiz_feedback=m;}
void JPWFactorApply(){factor_apply++;g_factor_preference.factor=g_factor_draft;g_factor_preference.generation++;g_factor_state=JPW_RAIZN_VALID;}
void JPWRaizApply(){legacy_apply++;}
void JPWRaizBindTicket(){bind++;}
void JPWRaizRecordComparison(){compare++;}
'''
MAIN = r'''
int checks=0,failures=0;
void check(bool c,const string&m){checks++;if(!c){failures++;std::cerr<<"FAIL "<<m<<'\n';}}
void click(const string&s){OnChartEvent(CHARTEVENT_OBJECT_CLICK,0,0.,s);}
// A separately tested coordinator accepts a new synthetic snapshot between
// UI events. This helper is not invoked from any production event function.
void accept_current(){g_account=current_account;g_account_known=true;g_sample_context="synthetic-context";
 metric_account=(int)current_account.id;g_cockpit_snapshot.symbol=_Symbol;g_cockpit_snapshot.account_key=g_sample_context;g_refresh_requested=false;}
int main(){
 g_account.id=1;metric_account=1;current_account.id=2;g_live_config.n=30;g_live_config.f=1.123456789;
 g_live_config.generation=7;g_live_config.n_reason="synthetic N";g_live_config.f_reason="synthetic F";
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 check(!g_raiz_details_open&&g_refresh_requested&&refreshes==0,"A->B before opening invalidates and schedules collection");
 accept_current();click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 check(g_raiz_details_open&&drawn_account==2&&g_raiz_draft_account.id==2&&mdd_reads==0&&g_record_read_requested,
       "opening uses accepted snapshot and defers record reads to coordinator");
 double f=0.;check(JPWLivePositiveFactor(g_raiz_fields[19],f)&&f==g_live_config.f,"F reopen roundtrip all digits");
 g_raiz_fields[17]="31";check(JPWLivePositiveFactor(g_raiz_fields[19],f)&&f==1.123456789,"edit only N does not round F");
 g_live_config.f=1e-9;JPWLivePopulateFields();
 check(JPWLivePositiveFactor(g_raiz_fields[19],f)&&f==1e-9,"tiny positive F never reopens zero");
 check(JPWLivePositiveFactor("1.25",f)&&f==1.25,"ordinary decimal remains accepted");
 check(!JPWLivePositiveFactor("0",f)&&!JPWLivePositiveFactor("nan",f)&&!JPWLivePositiveFactor("1.2x",f),"invalid factor refused");
 check(g_factor_draft==1.5,"absent diagnostic preference defaults to F1.5 without writing");
 click(JPWRaizUI("BUTTON_11"));check(g_raiz_tab==6,"diagnostic F chooser opens");
 click(JPWRaizUI("BUTTON_16"));check(g_factor_draft==1.8&&factor_apply==0,"F1.8 is draft only before Apply");
 click(JPWRaizUI("BUTTON_5"));check(!g_raiz_details_open&&factor_apply==0,"Cancel discards unsaved F1.8");
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 check(g_factor_draft==1.5&&factor_apply==0,"reopen restores unsaved default F1.5");
 click(JPWRaizUI("BUTTON_11"));click(JPWRaizUI("BUTTON_16"));click(JPWRaizUI("BUTTON_2"));
 check(factor_apply==1&&g_factor_preference.factor==1.8,"diagnostic Apply saves only selected F1.8");
 click(JPWRaizUI("BUTTON_14"));check(g_raiz_tab==5,"legacy N/F remains separately reachable");
 objects[JPWRaizUI("EDIT_17")]="42";g_raiz_panel_built=true;
 OnChartEvent(CHARTEVENT_CHART_CHANGE,0,0.,"");
 check(g_raiz_fields[17]=="42"&&g_raiz_details_open,"resize captures draft before destroy");
 objects[JPWRaizUI("EDIT_18")]="new reason";g_raiz_panel_built=true;
 click(JPWRaizUI("BUTTON_8"));check(g_raiz_fields[18]=="new reason"&&g_raiz_page==1,"pagination preserves draft");
 click(JPWRaizUI("BUTTON_5"));check(!g_raiz_details_open&&apply==0&&legacy_apply==0&&factor_apply==1,"legacy Cancel writes neither config nor scenario");
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");click(JPWRaizUI("BUTTON_14"));click(JPWRaizUI("BUTTON_2"));
 check(apply==1&&legacy_apply==0&&factor_apply==1,"legacy setup Apply routes only to live config");
 click(JPWRaizUI("BUTTON_12"));click(JPWRaizUI("BUTTON_0"));click(JPWRaizUI("BUTTON_2"));click(JPWRaizUI("BUTTON_2"));
 check(legacy_apply==1&&apply==1,"advanced declaration remains independent");
 current_account.id=3;click(JPWRaizUI("BUTTON_13"));
 check(!g_raiz_details_open,"account switch during summary refresh closes stale draft");
 accept_current();click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 drawn_account=0;g_record_read_requested=false;click(JPWRaizUI("BUTTON_13"));
 check(g_record_read_requested&&g_refresh_requested&&mdd_reads==0&&refreshes==0,
       "explicit Refresh queues reads instead of executing in an event");
 current_account.id=4;click(JPWRaizUI("BUTTON_10"));
 check(!g_raiz_details_open,"account change before deferred refresh closes stale summary");
 accept_current();account_available=false;click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 check(!g_raiz_details_open,"unavailable account cannot open summary");
 account_available=true;accept_current();click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 OnChartEvent(CHARTEVENT_KEYDOWN,27,0.,"");check(!g_raiz_details_open&&apply==1&&factor_apply==1,"Escape is non-writing cancel");
 current_account.id=10;accept_current();flip_after_mdd=false;
 objects.erase(JPW_COCKPIT_PREF_OBJECT);JPWCockpitLoadPrefs();
 check(g_cockpit_prefs.visible_mask==63&&g_cockpit_prefs.density==0&&!g_cockpit_pref_invalid,
       "absent chart preference defaults to all six rows");
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 check(g_raiz_details_open&&g_raiz_tab==7,"launcher opens cockpit overview");
 click(g_panel_prefix+"2");
 check(g_raiz_tab==8&&g_cockpit_selected==2,"HUD metric click drills into Genesis card");
 g_hud_summary=true;g_hud_summary_source=5;click(g_panel_prefix+"0");
 check(g_raiz_tab==JPW_ROUTE_METRIC&&g_cockpit_selected==5,"summary click follows actual Stop risk metric");
 g_hud_summary_source=-1;click(g_panel_prefix+"0");
 check(g_raiz_tab==JPW_ROUTE_OVERVIEW,"generic all-hidden launcher opens overview");g_hud_summary=false;
 click(JPWRaizUI("BUTTON_43"));
 check(g_raiz_tab==13&&g_record_read_requested&&mdd_reads==0,"System requests records only on demand");
 click(JPWRaizUI("BUTTON_44"));
 check(g_raiz_tab==10&&g_cockpit_draft.visible_mask==63,"customize starts from saved preference");
 const int before_hud=hud_renders;
 click(JPWRaizUI("BUTTON_62"));click(JPWRaizUI("BUTTON_30"));click(JPWRaizUI("BUTTON_31"));
 check(g_cockpit_draft.visible_mask==59&&g_cockpit_draft.corner==CORNER_RIGHT_UPPER&&g_cockpit_draft.density==1,
       "visibility, corner and density are previewed in draft");
 check(g_cockpit_prefs.visible_mask==63&&objects.count(JPW_COCKPIT_PREF_OBJECT)==0&&hud_renders>before_hud,
       "preview neither writes chart object nor changes committed preference");
 click(JPWRaizUI("BUTTON_28"));
 check(g_raiz_tab==7&&g_cockpit_prefs.visible_mask==63&&g_cockpit_draft.visible_mask==63,
       "Cancel discards visual draft");
 click(JPWRaizUI("BUTTON_44"));
 for(int i=60;i<=65;i++)click(JPWRaizUI("BUTTON_"+std::to_string(i)));
 check(g_cockpit_draft.visible_mask==0&&g_cockpit_prefs.visible_mask==63,
       "all-hidden is a preview until Apply; launcher remains a separate control");
 click(JPWRaizUI("BUTTON_27"));
 JPWCockpitPrefs saved;
 check(g_cockpit_prefs.visible_mask==0&&objects.count(JPW_COCKPIT_PREF_OBJECT)==1&&
       JPWCockpitDecode(objects[JPW_COCKPIT_PREF_OBJECT],saved)&&saved.visible_mask==0,
       "Apply stores only visual settings in the chart object");
 click(JPWRaizUI("BUTTON_37"));
 objects[JPW_COCKPIT_PREF_OBJECT]="corrupt";JPWCockpitLoadPrefs();
 check(g_cockpit_pref_invalid&&g_cockpit_prefs.visible_mask==63&&
       objects[JPW_COCKPIT_PREF_OBJECT]=="corrupt",
       "corrupt object warns, preserves bytes and uses temporary default");
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");click(JPWRaizUI("BUTTON_44"));
 click(JPWRaizUI("BUTTON_27"));
 check(g_cockpit_pref_invalid&&objects[JPW_COCKPIT_PREF_OBJECT]=="corrupt",
       "Apply refuses silent overwrite of corrupt preference");
 click(JPWRaizUI("BUTTON_29"));
 check(g_cockpit_reset_requested&&g_cockpit_draft.visible_mask==63,
       "Restaurar prepares an explicit replacement draft");
 click(JPWRaizUI("BUTTON_27"));
 check(!g_cockpit_pref_invalid&&JPWCockpitDecode(objects[JPW_COCKPIT_PREF_OBJECT],saved)&&
       saved.visible_mask==63,"Apply after explicit reset replaces corrupt object");
 click(JPWRaizUI("BUTTON_44"));
 const string unchanged=objects[JPW_COCKPIT_PREF_OBJECT];
 current_account.id=11;click(JPWRaizUI("BUTTON_27"));
 check(!g_raiz_details_open&&objects[JPW_COCKPIT_PREF_OBJECT]==unchanged,
       "account switch closes draft and refuses preference write");
 accept_current();click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");click(JPWRaizUI("BUTTON_44"));
 const string prior_symbol=_Symbol;_Symbol="EURUSD.exact";click(JPWRaizUI("BUTTON_27"));
 check(!g_raiz_details_open&&objects[JPW_COCKPIT_PREF_OBJECT]==unchanged,
       "exact-symbol switch closes draft and refuses preference write");
 _Symbol=prior_symbol;accept_current();
 click(g_panel_prefix+"RAIZ_DETAILS_BUTTON");
 OnChartEvent(CHARTEVENT_KEYDOWN,50,0.,"");
 check(g_raiz_tab==8&&g_cockpit_selected==1,"key 2 opens Floating P/L card");
 const int old_page=g_cockpit_page;
 OnChartEvent(CHARTEVENT_KEYDOWN,39,0.,"");
 check(g_cockpit_page==old_page+1,"right arrow advances cockpit body page");
 OnChartEvent(CHARTEVENT_KEYDOWN,37,0.,"");
 check(g_cockpit_page==old_page,"left arrow returns cockpit body page");
 click(JPWRaizUI("BUTTON_42"));click(JPWRaizUI("BUTTON_20"));
 const int selected=g_cockpit_selected;
 OnChartEvent(CHARTEVENT_KEYDOWN,51,0.,"");
 check(g_raiz_tab==6&&g_cockpit_selected==selected,
       "number keys do not hijack legacy F edit page");
 OnChartEvent(CHARTEVENT_KEYDOWN,27,0.,"");
 check(!g_raiz_details_open,"Escape remains a non-writing cockpit close");
 std::cout<<"HOST_DETAILS_EVENT: "<<checks-failures<<" PASS / "<<failures<<" FAIL\n";
 return failures?1:0;
}
'''

def main():
    source=expanded_source(IND);store=STORE.read_text()
    cockpit=expanded_source(COCKPIT).replace('string part[];', 'std::vector<string> part;')
    sigs=['bool JPWDetailsContextCurrent()', 'void JPWCockpitLoadPrefs()',
          'bool JPWCockpitSavePrefs(JPWCockpitPrefs &candidate)',
          'void JPWRaizSaveVisibleFields()', 'void JPWRaizSwitchTab(const int tab)',
          'void JPWLivePopulateFields()', 'void JPWFactorPopulateDraft()',
          'void JPWFactorSelect(const double factor)',
          'bool JPWRaizPositiveNumber(const string raw,double &value)',
          'bool JPWLivePositiveFactor(const string raw,double &value)',
          'void JPWOpenCockpit(const int metric=-1)',
          'void JPWHandleChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)',
          'void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)']
    bodies=['bool JPWRaizNDouble(const string raw,double &value) {'+body_of(store,'bool JPWRaizNDouble(')+'}']
    bodies += [signature+'{'+body_of(source,signature).replace('g_raiz_feedback="F "+',
              'g_raiz_feedback=string("F ")+')+'}' for signature in sigs]
    print(json.dumps({'kind':'HOST_SYNTHETIC_NOT_MT5','source_sha256':hashlib.sha256(IND.read_bytes()).hexdigest()},indent=2),flush=True)
    with tempfile.TemporaryDirectory(prefix='jpw-details-') as folder:
        cpp=Path(folder)/'details.cpp';exe=Path(folder)/'details'
        cpp.write_text(SHIM.replace('struct JPWAccount',cockpit+'\nstruct JPWAccount',1)+'\n'.join(bodies)+MAIN)
        compiler=shutil.which('clang++') or shutil.which('g++')
        if not compiler: raise SystemExit('ENVIRONMENT_ERROR: no host C++ compiler')
        for cmd in [[compiler,'-std=c++17','-Wall','-Wextra',str(cpp),'-o',str(exe)],[str(exe)]]:
            proc=subprocess.run(cmd,capture_output=True,text=True);print(proc.stdout,end='');print(proc.stderr,end='')
            if proc.returncode: raise SystemExit(proc.returncode)
    print('NATIVE_MT5_CLICKS: NOT_RUN\nEXIT_CODE: 0')
if __name__=='__main__':main()

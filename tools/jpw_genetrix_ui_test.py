#!/usr/bin/env python3
"""Host verification of actual V3 codec, UI projection, collector and selector.

Only string/terminal/store/chart adapters are synthetic. This is not native
MQL compilation, a chart inspection, demo trading or ledger/risk validation.
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile
import sys, os
from leverage_host_shim import source_root, translate_arrays, complete_design_shim

from leverage_cockpit_test import SHIM
from leverage_panel_test import body_of

ROOT = source_root()
INC = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
IND = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"


def struct(text, name):
    match = re.search(r"struct\s+" + re.escape(name) + r"\s*\{.*?\};", text, re.S)
    if not match:
        raise ValueError("Missing production struct " + name)
    return match.group()


def host(text):
    text = re.sub(r"^\s*#include.*$", "", text, flags=re.M)
    text = re.sub(r"\b(\w+)\s*&\s*(\w+)\[\]", r"std::vector<\1> &\2", text)
    text = re.sub(r"\b(\w+)\s+(\w+)\[\]\s*;", r"std::vector<\1> \2;", text)
    # MQL promotes literals to string during concatenation. C++ needs that
    # conversion explicitly; no financial/state expression is rewritten.
    text = re.sub(r'"(?:\\.|[^"\\])*"', lambda m: "string(" + m.group() + ")", text)
    return text


ADAPTER = r'''
long fake_utc=100000;
ulong fake_mono=1000;
int TIME_DATE=1,TIME_SECONDS=2,TIME_MINUTES=4;
int CHARTEVENT_KEYDOWN=1,CHARTEVENT_OBJECT_CLICK=2,OBJPROP_STATE=3;
int OBJPROP_TOOLTIP=4,FW_NORMAL=0;
bool TextSetFont(const string&,int,int){return true;}
bool TextGetSize(const string&s,unsigned int&w,unsigned int&h){w=StringLen(s)*6;h=12;return true;}
double MathAbs(double x){return std::abs(x);}
ulong GetTickCount64(){return fake_mono;}
long TimeGMT(){return fake_utc;}
using datetime=long;
string StringSubstr(const string&s,int start,int count){return s.substr(start,count);}
string TimeToString(long n,int){return std::to_string(n);}
string IntegerToString(long n){return std::to_string(n);}
string DoubleToString(double n,int digits){char b[128];std::snprintf(b,sizeof(b),"%.*f",digits,n);return b;}
int StringReplace(string &s,const string &from,const string &to){int n=0;size_t at=0;while((at=s.find(from,at))!=string::npos){s.replace(at,from.size(),to);at+=to.size();n++;}return n;}
template<class T>int ArraySize(const std::vector<T>&v){return int(v.size());}
template<class T,size_t N>int ArraySize(const T(&)[N]){return int(N);}
template<class T>int ArrayResize(std::vector<T>&v,int n){v.resize(n);return n;}
template<class T>int ArrayCopy(std::vector<T>&d,const std::vector<T>&s){d=s;return int(s.size());}
template<class T>void ZeroMemory(T &v){v=T{};}
'''

STATE = r'''
JPWCockpitSnapshot g_cockpit_snapshot;
JPWMetricSample g_metric_samples[JPW_COCKPIT_METRIC_COUNT];
double g_numeric_values[JPW_COCKPIT_METRIC_COUNT]={};
bool g_numeric_valid[JPW_COCKPIT_METRIC_COUNT]={};
long g_source_times[JPW_COCKPIT_METRIC_COUNT]={};
int g_metric_last_quality[JPW_COCKPIT_METRIC_COUNT]={};
JPW_VIEW_QUALITY g_leverage_quality=JPW_VIEW_NA,g_floating_quality=JPW_VIEW_NA,
 g_genesis_quality=JPW_VIEW_NA,g_raiz_quality=JPW_VIEW_NA,g_scale2_quality=JPW_VIEW_NA,
 g_stop_quality=JPW_VIEW_NA,g_compensated_quality=JPW_VIEW_NA;
struct FakeStop {long observed_mono_ms=0;} g_stop_sample;
bool g_stop_ready=false;
long g_collection_sequence=0;
string g_sample_context="ctx",g_diagnostic_context="account-a";
string g_panel_prefix="ui-a",g_panel_value="2x",g_panel_status="",
 _Symbol="EURUSD";
int JPW_DIAG_QUALITY_CHANGED=1,JPW_DIAG_DATA_UNAVAILABLE=2;
int diag_calls=0;
void JPWQueueDiagnostic(int){diag_calls++;}
struct JPWAccount {int id=1;} g_account;
bool g_account_known=true,budget=true,bridge_ok=true,risk_ok=false,account_matches=true;
int bridge_reads=0,risk_reads=0;
JPWLedgerView fixture_view;
std::vector<JPWLedgerCycle> fixture_cycles;
bool JPWCoordinatorBudgetRemaining(){return budget;}
bool JPWLedgerBridgeRefresh(std::vector<JPWLedgerCycle>&c,JPWLedgerView&v,string&r){bridge_reads++;c=fixture_cycles;v=fixture_view;r=bridge_ok?"accepted":"store unavailable";return bridge_ok;}
bool JPWRiskReadView(JPWAccount&,JPWRiskView&v,string&r){risk_reads++;v=JPWRiskView{};r="no risk publisher";return risk_ok;}
'''

EVENT_ADAPTER = r'''
bool g_raiz_details_open=true,g_editing_field=false,g_refresh_requested=false,owns_ui=true;
bool target_exists=true;
int g_raiz_tab=JPW_ROUTE_METRIC,g_cockpit_selected=6,g_focus_action=-1,g_cockpit_page=0;
int g_details_control=24,g_details_line=18,g_details_pad=6,g_details_font=11;
int draws=0; string g_details_render_reason=""; bool g_details_inventory_complete=true;
void JPWInvalidateDialogContent(int=-1){}
void JPWRaizSaveVisibleFields(){}
bool JPWUIDesignSetInteger(const string&,int,bool){return true;}
bool g_details_frame_active=true;
void JPWPresentationFailure(const string&r){g_details_render_reason=r;g_details_inventory_complete=false;}
bool JPWFocusValid(int action){return target_exists;}
bool JPWPresentationSetString(const string&n,int p,const string&s){return true;}
bool JPWUIOwns(const string&){return owns_ui;}
bool JPWDetailsContextCurrent(){return true;}
bool JPWReadAccount(JPWAccount &a){a.id=account_matches?1:2;return true;}
bool JPWAccountsEqual(JPWAccount &a,JPWAccount &b){return a.id==b.id;}
string JPWActionObject(int i){return "BUTTON_"+std::to_string(i);}
string JPWRaizUI(const string&s){return s;}
bool ObjectSetInteger(int,const string&,int,bool){return true;}
bool ObjectSetString(int,const string&,int,const string&){return true;}
int ObjectFind(int,const string&){return target_exists?0:-1;}
void JPWBuildPresentation(const string&,const string&){JPWGenetrixPresentMetric();}
void JPWRaizSwitchTab(int tab){g_raiz_tab=tab;g_cockpit_page=0;draws++;}
void JPWRaizPanelDestroy(){}
void JPWRenderRaizDetails(){draws++;}
void ChartRedraw(int){}
void JPWRenderCurrentDisplay(){draws++;}
void JPWInvalidateIdentityPresentation(){JPWGenetrixInvalidate("identity changed");JPWSampleInvalidate(g_metric_samples[6],JPW_SAMPLE_CONTEXT_CHANGED);}
struct Draw {string kind,text;int y,height;};
std::vector<Draw> draw_items;
void JPWRaizCreateLabel(const string&kind,const string&text,int,int y){draw_items.push_back({kind,text,y,g_details_line});}
void JPWRaizCreateButton(int i,const string&text,int,int y,int){draw_items.push_back({"BUTTON_"+std::to_string(i),text,y,g_details_control});}
string JPWFitText(const string&s,int,int){return s;}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool good,const string&why){checks++;if(!good){failures++;std::cerr<<"FAIL "<<why<<'\n';}}
bool has(const string&s,const string&part){return s.find(part)!=string::npos;}
string joined_lines(const std::vector<string>&lines,bool remove_spaces=false){
 string text;for(const auto&line:lines)text+=line+(remove_spaces?"":" ");
 if(remove_spaces)StringReplace(text," ","");return text;
}
JPWLedgerCycle cycle(const string&id,const string&symbol="EURUSD",int side=1){
 JPWLedgerCycle c{};c.cycle_id=id;c.symbol=symbol;c.side=side;c.started_msc=100000;
 c.state=1;c.genesis_inferred=true;c.history_complete=c.costs_complete=true;
 c.amount_valid=c.percent_valid=true;c.compensated=67;c.percent=6.7;
 c.realized_price=150;c.realized_swap=-2;c.commissions=-3;c.fees=-1;
 c.unrealized_price=-75;c.unrealized_swap=-2;c.open_positions=2;
 c.members_available=true;c.member_identifiers="10,20,30";return c;
}
void fresh(){
 fake_mono=1000;fixture_view=JPWLedgerView{};fixture_view.account_key="account-a";
 fixture_view.currency="USD";fixture_view.observed_utc=fake_utc;fixture_view.observed_mono_ms=fake_mono;
 fixture_view.quality=1;fixture_view.balance=1000;fixture_view.generation=3;
 fixture_view.history_complete=fixture_view.costs_complete=fixture_view.healthy=true;
 fixture_cycles={cycle("a")};bridge_ok=true;budget=true;g_account_known=true;
 g_sample_context="ctx";g_diagnostic_context="account-a";JPWGenetrixInvalidate("reset");
 g_cockpit_snapshot.symbol=_Symbol;g_cockpit_snapshot.account_key=g_sample_context;
}
int main(){
 check(JPW_COCKPIT_METRIC_COUNT==7 && JPW_COCKPIT_PREF_VERSION==3,"seven metric V3 contract");
 JPWCockpitPrefs p;JPWCockpitDefault(p);check(p.visible_mask==127,"new chart displays all seven");
 for(int m=0;m<=127;m++)for(int c=0;c<4;c++)for(int d=0;d<2;d++){
  JPWCockpitPrefs a={m,c,d},b={-1,-1,-1};string encoded=JPWCockpitEncode(a);
  check(JPWCockpitDecode(encoded,b)&&b.visible_mask==m&&b.corner==c&&b.density==d,"V3 roundtrip");
  for(int i=0;i<7;i++)check(JPWCockpitVisible(b,i)==bool(m&(1<<i)),"seven independent visibility bits");
  check(!JPWCockpitVisible(b,-1)&&!JPWCockpitVisible(b,7),"range guard");
 }
 for(int version=1;version<=2;version++)for(int m=0;m<=(version==1?31:63);m++)for(int c=0;c<4;c++)for(int d=0;d<2;d++){
  JPWCockpitPrefs old={m,c,d},restored={-1,-1,-1};
  string packet=StringFormat("JPWCOCKPIT|%d|%d|%d|%d|%d",version,m,c,d,JPWCockpitChecksumVersion(old,version));
  check(JPWCockpitDecode(packet,restored)&&restored.visible_mask==(m==0?0:m|(version==1?96:64))&&restored.corner==c&&restored.density==d,"V1/V2 preserves all bits/layout; zero stays hidden");
 }
 JPWCockpitPrefs bad={128,0,0},target={5,1,1};
 check(JPWCockpitEncode(bad)=="","unknown eighth bit refused");
 const string corrupt[]={"JPWCOCKPIT|4|1|0|0|0","JPWCOCKPIT|2|64|0|0|0","JPWCOCKPIT|1|32|0|0|0","JPWCOCKPIT|3|-1|0|0|0","JPWCOCKPIT|3|1|0|0|0"};
 for(const auto&s:corrupt)check(!JPWCockpitDecode(s,target)&&target.visible_mask==5&&target.corner==1&&target.density==1,"bad packet does not partially apply");
 check(!has(JPWCockpitEncode(target),"account")&&!has(JPWCockpitEncode(target),"cycle"),"prefs carry no account/cycle");
 fresh();JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(g_genetrix_selected_cycle=="a"&&g_cockpit_snapshot.metric[6].value=="USD 67,00 · 6,70% saldo","unique current cycle NET comes from accepted ledger");
 check(g_metric_samples[6].value_kind==JPW_SAMPLE_STATE&&!g_metric_samples[6].has_value,"census STATE envelope does not borrow selected numeric result");
 check(JPWGenetrixMetricQuality(6,g_cockpit_snapshot.metric[6].quality)=="Current","current quality independent for new line");
 fixture_cycles[0].percent_valid=false;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(has(g_cockpit_snapshot.metric[6].value,"USD 67,00")&&has(g_cockpit_snapshot.metric[6].value,"N/A %"),"valid amount survives unavailable percentage");
 fixture_cycles[0].partial=true;fixture_cycles[0].costs_complete=false;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(g_cockpit_snapshot.metric[6].value=="N/A · Partial"&&JPWGenetrixMetricQuality(6,JPW_VIEW_CURRENT)=="Partial","partial subtotal never becomes complete Current NET");
 fresh();fixture_cycles[0].state=3;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(g_cockpit_snapshot.metric[6].value=="N/A · Historical"&&JPWGenetrixMetricQuality(6,JPW_VIEW_NA)=="Historical","closed cycle remains dated history");
 fresh();fixture_view.quality=2;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(JPWGenetrixMetricQuality(6,JPW_VIEW_CURRENT)=="Historical","historical publisher observation is not live");
 fresh();JPWGenetrixCollectLedger();fake_mono=31001;JPWGenetrixPresentMetric();
 check(g_cockpit_snapshot.metric[6].value=="N/A"&&JPWGenetrixMetricQuality(6,JPW_VIEW_CURRENT)=="N/A","old current value removed on age independently of render");
 fresh();fixture_cycles[0].state=4;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(JPWGenetrixMetricQuality(6,JPW_VIEW_CURRENT)=="N/A","unconfirmed cycle has no Current label");
 fixture_cycles[0].genesis_inferred=false;JPWGenetrixCollectLedger();
 check(JPWGenetrixGenesisLabel(g_genetrix_cycles[0])=="não identificada","provisional cycle does not invent inferred Genesis");
 fixture_cycles[0].genesis_ambiguous=true;JPWGenetrixCollectLedger();
 check(JPWGenetrixGenesisLabel(g_genetrix_cycles[0])=="AMBÍGUA","ambiguous origin stays explicit");
 fresh();fixture_cycles={cycle("a"),cycle("b","GBPUSD",-1)};JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(g_genetrix_selected_cycle==""&&has(g_cockpit_snapshot.metric[6].reason,"Selecione"),"multiple cycles require selection, no cross-cycle sum");
 g_raiz_tab=JPW_ROUTE_METRIC;int reads=bridge_reads;
 check(JPWGenetrixHandleCycleEvent(CHARTEVENT_OBJECT_CLICK,0,JPWActionObject(JPW_ACTION_SECONDARY))&&g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES,"cycle list route by click");
 draw_items.clear();render_selector(5,20,500,230,300);
 check(g_genetrix_cycle_button_count==2&&g_genetrix_cycle_button_id[1]=="b","selector maps exact stable IDs");
 check(JPWGenetrixHandleCycleEvent(CHARTEVENT_OBJECT_CLICK,0,JPWActionObject(101))&&g_genetrix_selected_cycle=="b"&&g_raiz_tab==JPW_ROUTE_METRIC,"click selects exact symbol/direction cycle");
 check(bridge_reads==reads,"selection does not read ledger or create collection");
 auto sample_id=g_metric_samples[6].id;JPWGenetrixPresentMetric();check(g_metric_samples[6].id==sample_id,"render does not create sample");
 g_raiz_tab=JPW_ROUTE_METRIC;g_focus_action=JPW_ACTION_SECONDARY;
 check(JPWGenetrixHandleCycleEvent(CHARTEVENT_KEYDOWN,13,"")&&g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES,"list accessible by Enter");
 g_focus_action=100;check(JPWGenetrixHandleCycleEvent(CHARTEVENT_KEYDOWN,13,"")&&g_genetrix_selected_cycle=="a","cycle selection by Enter");
 g_raiz_tab=JPW_ROUTE_METRIC;g_focus_action=JPW_ACTION_SECONDARY;target_exists=false;
 check(!JPWGenetrixHandleCycleEvent(CHARTEVENT_KEYDOWN,13,"")&&g_raiz_tab==JPW_ROUTE_METRIC,"removed control cannot activate a stale keyboard target");target_exists=true;
 owns_ui=false;check(!JPWGenetrixHandleCycleEvent(CHARTEVENT_OBJECT_CLICK,0,JPWActionObject(21)),"foreign focus cannot select");owns_ui=true;
 account_matches=false;check(JPWGenetrixHandleCycleEvent(CHARTEVENT_OBJECT_CLICK,0,JPWActionObject(21))&&!g_genetrix_ledger_available&&g_genetrix_selected_cycle=="","account change discards financial view and selection before event");account_matches=true;
 fresh();JPWGenetrixCollectLedger();bridge_ok=false;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(!g_genetrix_ledger_available&&g_cockpit_snapshot.metric[6].value=="N/A"&&g_compensated_quality==JPW_VIEW_NA,"failed store removes old current value, never zero");
 fresh();fixture_view.account_key="wrong-account";JPWGenetrixCollectLedger();check(!g_genetrix_ledger_available,"foreign identity refused");
 fresh();JPWGenetrixCollectLedger();fixture_cycles.clear();JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 check(g_genetrix_cycles.empty()&&g_genetrix_selected_cycle==""&&has(g_cockpit_snapshot.metric[6].reason,"Nenhum ciclo"),"confirmed shrink to empty removes rows without inventing zero NET");
 fresh();fixture_cycles[0].started_msc=0;JPWGenetrixCollectLedger();draw_items.clear();render_selector(5,20,500,230,300);
 check(has(draw_items[0].text,"origem sem horário"),"absent origin time is unavailable instead of a fabricated date");
 fresh();fixture_cycles.clear();for(int i=0;i<35;i++)fixture_cycles.push_back(cycle("id"+std::to_string(i)));
 JPWGenetrixCollectLedger();g_cockpit_page=2;draw_items.clear();render_selector(5,20,500,230,300);
 check(g_genetrix_cycle_button_count==3&&g_genetrix_cycle_button_id[0]=="id6","large list paginates without losing cycle identity");
 for(const auto&item:draw_items)if(item.kind!="PAGE")check(item.y>=20&&item.y+item.height<=250,"selector rows stay in measured viewport");
 draw_items.clear();g_cockpit_page=0;render_selector(5,20,150,24,80);
 check(g_genetrix_cycle_button_count==1&&draw_items[0].height==24,"short viewport retains focusable selection button");
 fresh();JPWGenetrixCollectLedger();std::vector<string> members;
 check(JPWGenetrixMemberIdentifiers(g_genetrix_cycles[0],members)&&members==std::vector<string>({"10","20","30"}),"member projection includes historical Genesis and closed identifiers, independently of two live positions");
 fixture_cycles[0].members_available=false;fixture_cycles[0].member_identifiers="";JPWGenetrixCollectLedger();
 auto detail=render_details_lines(500);auto text=joined_lines(detail);
 check(has(text,"Membros indisponíveis")&&!has(text,"Lista observada: 0")&&!has(text,"Membro 1:"),"old codec without list is unavailable, never proof of zero members");
 check(has(text,"Membros da geração 3")&&has(text,"100000 UTC"),"member data binds displayed generation and observation UTC");
 fixture_cycles[0].member_identifiers="10,20";JPWGenetrixCollectLedger();
 check(!JPWGenetrixMemberIdentifiers(g_genetrix_cycles[0],members)&&members.empty(),"availability flag is mandatory even when stale member text exists");
 fixture_cycles[0].members_available=true;
 for(const string &broken:std::vector<string>({"0","-1","01","10,,20","10,20,","10,x"})){
  fixture_cycles[0].member_identifiers=broken;JPWGenetrixCollectLedger();
  check(!JPWGenetrixMemberIdentifiers(g_genetrix_cycles[0],members)&&members.empty(),"malformed observed identifiers produce unavailable list instead of partial identity display");
 }
 fixture_cycles[0].member_identifiers="";fixture_cycles[0].state=4;fixture_cycles[0].genesis_inferred=false;
 fixture_cycles[0].amount_valid=fixture_cycles[0].percent_valid=false;JPWGenetrixCollectLedger();JPWGenetrixPresentMetric();
 text=joined_lines(render_details_lines(500));
 check(has(text,"antes da primeira execução")&&!has(text,"Membros indisponíveis")&&g_cockpit_snapshot.metric[6].value=="N/A","available empty projection is explicitly provisional and has no financial zero");
 fresh();fixture_cycles[0].state=3;fixture_view.quality=2;
 fixture_cycles[0].member_identifiers="1,9007199254740993,9223372036854775807";JPWGenetrixCollectLedger();
 text=joined_lines(render_details_lines(500),true);
 check(has(text,"POSITION_IDENTIFIER9007199254740993")&&has(text,"POSITION_IDENTIFIER9223372036854775807"),"historical identifiers retain all decimal digits, without floating-point or ticket conversion");
 check(has(text,"não são tickets atuais")||has(joined_lines(render_details_lines(500)),"não são tickets atuais"),"position identifiers are distinguished from current tickets");
 fixture_cycles[0].history_complete=false;fixture_cycles[0].amount_valid=false;fixture_cycles[0].partial=true;JPWGenetrixCollectLedger();
 text=joined_lines(render_details_lines(500));
 check(has(text,"a lista não comprova todos os membros")&&!has(text,"realizado preço USD 150"),"partial history preserves observed IDs but never claims complete ancestry or available monetary components");
 fresh();fixture_cycles[0].member_identifiers="";
 for(int i=0;i<95;i++)fixture_cycles[0].member_identifiers+=(i?",":"")+std::to_string(100000+i);
 JPWGenetrixCollectLedger();detail=render_details_lines(160);
 auto financial_sample=g_metric_samples[6].id;auto financial_value=g_genetrix_cycles[0].compensated;
 int reads_before_paging=bridge_reads,pages=JPWPanelPageCount(int(detail.size()),3);
 std::vector<string> observed;
 for(int page=0;page<pages;page++){
  g_cockpit_page=page;draw_items.clear();render_details_page(detail,5,20,54,110);
  for(const auto&item:draw_items)if(item.kind!="PAGE"){
   check(item.y>=20&&item.y+item.height<=74,"actual member detail pager keeps each visible row inside its body");
   observed.push_back(item.text);
  }
 }
 check(observed==detail,"all wrapped member lines are reachable once through actual detail pages, with no dropped final member");
 text=joined_lines(observed,true);
 for(int i=0;i<95;i++)check(has(text,"POSITION_IDENTIFIER"+std::to_string(100000+i)),"each projected identifier remains complete across narrow wrapped pages");
 g_cockpit_page=0;pager_branch(JPWActionObject(JPW_ACTION_NEXT));draw_items.clear();render_details_page(detail,5,20,54,110);
 check(g_cockpit_page==1,"actual next-button branch reaches the next member detail page");
 g_cockpit_page=0;pager_branch(JPWActionObject(JPW_ACTION_PREVIOUS));render_details_page(detail,5,20,54,110);
 check(g_cockpit_page==0,"actual previous-button branch clamps at first page");
 g_cockpit_page=pages-1;pager_branch(JPWActionObject(JPW_ACTION_NEXT));render_details_page(detail,5,20,54,110);
 check(g_cockpit_page==pages-1,"actual next-button branch clamps at final page");
 check(bridge_reads==reads_before_paging&&g_metric_samples[6].id==financial_sample&&g_genetrix_cycles[0].compensated==financial_value,"member reading/paging neither refreshes ledger nor changes sample or finance");
 fixture_cycles.push_back(cycle("b","GBPUSD",-1));fixture_cycles[1].member_identifiers="200001";JPWGenetrixCollectLedger();
 g_raiz_tab=JPW_ROUTE_LEDGER_CYCLES;g_cockpit_page=0;draw_items.clear();render_selector(5,20,500,230,300);
 g_cockpit_page=12;JPWGenetrixHandleCycleEvent(CHARTEVENT_OBJECT_CLICK,0,JPWActionObject(101));
 text=joined_lines(render_details_lines(500));
 check(g_genetrix_selected_cycle=="b"&&g_cockpit_page==0&&has(text,"200001")&&!has(text,"100094"),"actual cycle-selection event resets pagination and never carries another cycle's member list");
 g_genetrix_risk_available=false;check(has(JPWGenetrixRiskSummary(),"N/A"),"missing supervisor never shows leverage zero");
 std::cout<<"GENETRIX_UI_HOST: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native MT5 compile/chart/template/demo NOT_RUN\n";
 return failures?1:0;
}
'''


def main():
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no host C++ compiler; native MT5 NOT_RUN")
        return 2
    cockpit = (INC / "JPW_Alavancagem_Cockpit.mqh").read_text()
    samples = (INC / "JPW_Alavancagem_Samples.mqh").read_text()
    ui = (INC / "JPW_Genetrix_UI.mqh").read_text()
    ledger = (INC / "JPW_Genetrix_Ledger_Core.mqh").read_text()
    risk = (INC / "JPW_Genetrix_Risk_Store.mqh").read_text()
    coordinator = (INC / "JPW_Alavancagem_Coordinator.mqh").read_text()
    presentation = (INC / "JPW_Alavancagem_Presentation.mqh").read_text()
    indicator = IND.read_text()
    slices = "\n".join(signature + "{" + body_of(coordinator, signature) + "}" for signature in
       ("void JPWAcceptMetric(const int metric)", "void JPWGenetrixCollectLedger()"))
    event_signature = "bool JPWGenetrixHandleCycleEvent(const int id,const long key,const string object_name)"
    events = event_signature + "{" + body_of(indicator, event_signature) + "}"
    panel = (INC / "JPW_Alavancagem_Panel.mqh").read_text()
    geometry = "\n".join(signature + "{" + body_of(panel, signature) + "}" for signature in
       ("int JPWPanelClamp(const int value,const int low,const int high)",
        "int JPWPanelPageCount(const int total,const int rows)"))
    render = "void render_selector(int x,int body_y,int inner,int body_height,int footer_y){" + body_of(
        body_of(presentation,"void JPWRenderCockpit()"), "else if(g_raiz_tab==JPW_ROUTE_LEDGER_CYCLES)") + "}"
    wrapping = "\n".join(signature + "{" + body_of(presentation, signature) + "}" for signature in
        ("void JPWDetailsAppendLine(const string row,string &lines[])",
         "void JPWDetailsWrap(const string paragraph,const int width,string &lines[])"))
    details = "std::vector<string> render_details_lines(const int inner){string lines[];" + body_of(presentation, "         if(i==6)") + "return lines;}"
    page_start = presentation.index("      const int rows=(body_height/g_details_line>0 ? body_height/g_details_line : 1);")
    page_end = presentation.index("\n     }\n   JPWDialogFooterButtons(footer_actions", page_start)
    detail_pager = "void render_details_page(string &lines[],const int x,const int body_y,const int body_height,const int footer_y){" + presentation[page_start:page_end] + "}"
    actions = (INC / "JPW_Alavancagem_Actions.mqh").read_text()
    pager_event = "void pager_branch(const string sparam){" + body_of(actions, "   if(sparam==JPWActionObject(JPW_ACTION_PREVIOUS) || sparam==JPWActionObject(JPW_ACTION_NEXT))") + "}"
    # Integration contracts are inspected in addition to executing actual slices.
    assert "JPWGenetrixPresentMetric();" in body_of(presentation, "void JPWBuildPresentation(const string leverage_value,const string leverage_detail)")
    monitor = body_of(coordinator, "void JPWMonitorStopRisk()")
    assert monitor.index("JPWAcceptMetric(5);") < monitor.index("JPWGenetrixCollectLedger();")
    assert "JPWGenetrixInvalidate(" in body_of(coordinator, "void JPWInvalidateIdentityPresentation()")
    assert "JPWGenetrixHandleCycleEvent(" in body_of(indicator, "void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)")
    assert 'JPW_COCKPIT_PREF_V2_OBJECT' in indicator
    assert "100 × lucro flutuante / saldo." in presentation
    assert "g_floating_value" in body_of(presentation, "void JPWBuildPresentation(const string leverage_value,const string leverage_detail)")
    assert not any(token in ui for token in ("OrderSend(", "PositionClose(", "JPWRiskArm", "FileOpen(", "JPWLedgerStoreWrite"))
    pieces = [SHIM, ADAPTER, host(samples), host(cockpit),
              host(struct(ledger, "JPWLedgerCycle") + struct(ledger, "JPWLedgerView") + struct(risk, "JPWRiskView")),
              STATE, host(ui), host(slices), EVENT_ADAPTER, host(geometry), host(events), host(render),
              host(wrapping), host(details), host(detail_pager), host(pager_event), MAIN]
    for path in (INC / "JPW_Genetrix_UI.mqh", INC / "JPW_Alavancagem_Cockpit.mqh",
                 INC / "JPW_Alavancagem_Presentation.mqh", IND):
        print(path.name + " SHA256 " + hashlib.sha256(path.read_bytes()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-genetrix-ui-host-") as directory:
        source = Path(directory) / "ui.cpp"
        binary = Path(directory) / "ui"
        source.write_text("\n".join(pieces))
        for command in ((compiler, "-std=c++17", "-Wall", "-Wextra", str(source), "-o", str(binary)), (str(binary),)):
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

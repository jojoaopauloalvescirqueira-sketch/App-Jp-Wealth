#!/usr/bin/env python3
"""Execute the actual Stoikus opening script with unavoidable native API seams.

This is C++ host verification, never native MQL5 compilation or MT5 execution.
Only #property and the version include are adapted; production decisions and
control flow are compiled unchanged. Fixtures model indicator references and
chart state; they do not implement the script's presence or opening decisions.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MQL = Path('mt5/jpw-alavancagem-atual/MQL5')
SCRIPT = MQL / 'Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5'
VERSION = MQL / 'Include/JPWealth/JPW_Alavancagem_Version.mqh'
INPUTS = {
    'Experts/JPWealth/JPW_Stoikus_Monitor.mq5': [
        ['bool', 'InpHistoryCoverageConfirmed', 'false'],
        ['bool', 'InpCostCoverageConfirmed', 'false'],
        ['string', 'InpCoverageEvidence', '""']],
    'Indicators/JPWealth/JPW_Alavancagem_Atual.mq5': [
        ['int', 'InpUpdateSeconds', '1'], ['int', 'InpMaxQuoteAgeSeconds', '30'],
        ['ENUM_BASE_CORNER', 'InpCorner', 'CORNER_LEFT_UPPER'],
        ['int', 'InpOffsetX', '16'], ['int', 'InpOffsetY', '40'],
        ['int', 'InpFontSize', '10'], ['int', 'InpCockpitFontSize', '11'],
        ['color', 'InpFontColor', "C'118,118,118'"],
        ['long', 'InpGenesisTicket', '0'], ['string', 'InpPipSymbol', '""'],
        ['double', 'InpPipSize', '0.0'], ['bool', 'InpTechnicalLog', 'false']],
    'Indicators/JPWealth/JPW_NoCuda_Channels.mq5': [
        ['ENUM_TIMEFRAMES', 'InpSourceTimeframe', 'PERIOD_H1'],
        ['bool', 'InpFullMesh', 'true'], ['string', 'InpPipSymbol', '""'],
        ['double', 'InpPipSize', '0.0'], ['int', 'InpMaxQuoteAgeSeconds', '30']],
}

SHIM = r'''
#include <algorithm>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using string=std::string;
using ENUM_TIMEFRAMES=int;
constexpr int INVALID_HANDLE=-1,CHART_WINDOWS_TOTAL=1;
const long chart_id=717;
const string symbol="EURUSD";
const ENUM_TIMEFRAMES period=60;
struct Indicator {string name; string inputs; int handle; int owned_namespace=-1; bool handlers_active=true;};
struct Resource {string name; bool attached=false; int owned_namespace=-1;};
std::map<int,std::vector<Indicator>> windows;
std::map<int,Resource> resources;
std::map<string,string> objects;
std::vector<string> alerts,prints;
std::vector<string> created;
string ea="OwnerEA",supervisor="disarmed",persisted="unchanged studies";
int order_count=0,next_handle=100,last_error=0,redraws=0;
int fail_create=-1,fail_add=-1,fail_release=-1;
bool fail_scan=false,fail_names=false,fail_list=false,fail_list_zero=false,hidden_add=false;
bool caller_shadow=false;
int shadow_loaded=0;
const string account_path="\\Indicators\\JPWealth\\JPW_Alavancagem_Atual";
const string nocuda_path="\\Indicators\\JPWealth\\JPW_NoCuda_Channels";
const string relative_account_path="JPWealth\\JPW_Alavancagem_Atual";
const string relative_nocuda_path="JPWealth\\JPW_NoCuda_Channels";
void check(bool value,const string &message){if(!value)throw std::runtime_error(message);}
int kind(const string &path){if(path==account_path||path==relative_account_path)return 0;if(path==nocuda_path||path==relative_nocuda_path)return 1;return -1;}
int StringFind(const string &s,const string &needle,int start=0){auto at=s.find(needle,start);return at==string::npos?-1:int(at);}
int StringLen(const string &s){return int(s.size());}
string StringSubstr(const string &s,int start,int count=-1){return s.substr(start,count<0?string::npos:count);}
string IntegerToString(long value){return std::to_string(value);}
void ResetLastError(){last_error=0;}
int GetLastError(){return last_error;}
long ChartID(){return chart_id;}
string ChartSymbol(long chart){check(chart==chart_id,"wrong target symbol chart");return symbol;}
ENUM_TIMEFRAMES ChartPeriod(long chart){check(chart==chart_id,"wrong target period chart");return period;}
bool ChartGetInteger(long chart,int prop,int sub,long &value){
 check(chart==chart_id&&prop==CHART_WINDOWS_TOTAL&&sub==0,"wrong windows query");
 if(fail_scan){last_error=4101;return false;}value=windows.rbegin()->first+1;return true;}
int ChartIndicatorsTotal(long chart,int window){check(chart==chart_id,"wrong list chart");if(fail_list){last_error=4103;return -1;}if(fail_list_zero){last_error=4103;return 0;}return int(windows[window].size());}
string ChartIndicatorName(long chart,int window,int index){
 check(chart==chart_id,"wrong name chart");if(fail_names){last_error=4102;return "";}
 return windows.at(window).at(index).name;}
// iCustom starts indicator initialization before attachment. Deliberately model
// the destructive consequence of creating a second copy in an existing panel's
// namespace: only production's pre-creation presence decision prevents it.
int iCustom(const string &requested_symbol,ENUM_TIMEFRAMES requested_period,const string &path){
 check(requested_symbol==symbol&&requested_period==period,"indicator created for wrong context");
 int k=kind(path);check(k>=0,"wrong indicator path");created.push_back(path);
 // Documented native resolution: an unrooted name checks the caller's folder
 // before Indicators; rooted paths select the known Indicators artifact.
 if(caller_shadow&&(path==relative_account_path||path==relative_nocuda_path)){
  shadow_loaded++;int h=next_handle++;resources[h]={"Caller folder shadow",false,k};return h;}
 if(k==fail_create){last_error=4802;return INVALID_HANDLE;}
 for(const auto &window:windows)for(const auto &indicator:window.second)
  if(indicator.owned_namespace==k)
   objects["panel preference"]="damaged by duplicate init";
 int h=next_handle++;resources[h]={k==0?string("Stoikus · Cockpit ")+JPW_PRODUCT_VERSION:string("Stoikus · NoCuda Channels"),false,k};
 return h;}
bool ChartIndicatorAdd(long chart,int window,int handle){
 check(chart==chart_id&&window==0,"addition must target current main window");
 check(resources.count(handle),"unknown handle");
 int k=resources.at(handle).owned_namespace;
 if(k==fail_add){last_error=4114;return false;}
 if(!hidden_add){windows[0].push_back({resources.at(handle).name,"default",handle,k});resources.at(handle).attached=true;}
 return true;}
bool IndicatorRelease(int handle){
 check(resources.count(handle),"released existing or invalid handle");
 int k=resources.at(handle).owned_namespace;
 if(k==fail_release){last_error=4807;return false;}
 resources.erase(handle);return true;}
void ChartRedraw(long chart){check(chart==chart_id,"wrong redraw chart");redraws++;}
template<class... T>void Print(const T&... values){std::ostringstream s;((s<<values),...);prints.push_back(s.str());}
template<class... T>void Alert(const T&... values){std::ostringstream s;((s<<values),...);alerts.push_back(s.str());}
'''

CASES = [
    'caller_shadow', 'inactive_listed', 'empty', 'repeat', 'account_present', 'nocuda_present', 'both_present',
    'legacy', 'file_aliases', 'mixed_legacy', 'existing_subwindow', 'duplicates',
    'create_account_fail', 'create_nocuda_fail', 'attach_account_fail',
    'attach_nocuda_fail', 'partial_retry', 'scan_fail', 'name_fail',
    'attach_unconfirmed', 'release_fail', 'similar_unrelated', 'indicator_list_fail',
    'account_present_companion_fail', 'nocuda_present_companion_fail', 'indicator_list_zero_fail',
    'root_missing_with_shadow_fail', 'release_nocuda_warning', 'attach_release_fail',
]

MAIN = r'''
string chart_snapshot(){std::ostringstream out;for(const auto &w:windows)for(const auto &i:w.second)out<<w.first<<":"<<i.name<<":"<<i.inputs<<":"<<i.handle<<"|";return out.str();}
void install(int w,const string &name,int owned_namespace=-1,bool handlers_active=true){windows[w].push_back({name,"custom-owner-settings",42+int(windows[w].size()),owned_namespace,handlers_active});}
int main(int argc,char **argv){
 try{
 check(argc==2,"case required");string c=argv[1];windows[0]={};
 objects={{"manual Fibo","price anchors"},{"panel preference","owner font and tab"},{"NoCuda study","owner anchors"}};
 if(c=="caller_shadow")caller_shadow=true;
 if(c=="root_missing_with_shadow_fail"){caller_shadow=true;fail_create=0;}
 // This fixture represents a recognized list entry with inactive handlers;
 // it does not run the real indicators' OnInit/OnDeinit or prove native health.
 if(c=="inactive_listed"){install(0,"Stoikus · Cockpit 1.22.0",0,false);install(0,"Stoikus · NoCuda Channels",1,false);}
 if(c=="account_present"||c=="both_present"||c=="duplicates"||c=="account_present_companion_fail")install(0,"Stoikus · Cockpit 1.22.0",0);
 if(c=="nocuda_present"||c=="both_present"||c=="nocuda_present_companion_fail")install(0,"Stoikus · NoCuda Channels",1);
 if(c=="legacy"){install(0,"JPW GENETRIX · Cockpit 1.21.2",0);install(0,"JPW GENETRIX · NoCuda Channels",1);}
 if(c=="file_aliases"){install(0,"JPW_Alavancagem_Atual",0);install(0,"JPW_NoCuda_Channels",1);}
 if(c=="mixed_legacy"){install(0,"JPW GENETRIX · Cockpit 1.21.2",0);install(0,"Stoikus · NoCuda Channels",1);}
 if(c=="existing_subwindow"){install(1,"JPW GENETRIX · Cockpit 1.21.2",0);install(2,"Stoikus · NoCuda Channels",1);}
 if(c=="duplicates"){install(0,"JPW GENETRIX · Cockpit 1.21.2",0);install(0,"Stoikus · NoCuda Channels",1);}
 if(c=="similar_unrelated"){install(0,"Stoikus · CockpitExtra");install(0,"Custom NoCuda Channels");}
 if(c=="create_account_fail")fail_create=0;
 if(c=="create_nocuda_fail")fail_create=1;
 if(c=="account_present_companion_fail")fail_create=1;
 if(c=="nocuda_present_companion_fail")fail_create=0;
 if(c=="attach_account_fail")fail_add=0;
 if(c=="attach_nocuda_fail"||c=="partial_retry")fail_add=1;
 if(c=="scan_fail")fail_scan=true;
 if(c=="indicator_list_fail")fail_list=true;
 if(c=="indicator_list_zero_fail")fail_list_zero=true;
 if(c=="name_fail"){install(0,"RSI");fail_names=true;}
 if(c=="attach_unconfirmed")hidden_add=true;
 if(c=="release_fail")fail_release=0;
 if(c=="release_nocuda_warning")fail_release=1;
 if(c=="attach_release_fail"){fail_add=1;fail_release=1;}
 const auto before_objects=objects;const auto before_windows=windows;
 const string before_chart=chart_snapshot();
 OnStart();
 if(c=="caller_shadow"||c=="root_missing_with_shadow_fail")check(shadow_loaded==0,"unrooted iCustom loaded the caller-folder shadow instead of Indicators");
 check(ea=="OwnerEA"&&supervisor=="disarmed"&&order_count==0&&persisted=="unchanged studies","EA/trading/persistence changed");
 check(objects==before_objects,"manual object, preference or study changed");
 for(const auto &w:before_windows)for(size_t i=0;i<w.second.size();i++){
  const auto &old=w.second[i],&now=windows.at(w.first).at(i);
  check(old.name==now.name&&old.inputs==now.inputs&&old.handle==now.handle&&old.handlers_active==now.handlers_active,"existing indicator changed");}
 check(alerts.size()==1,"each execution must emit exactly one visible result");
 bool existing=c=="both_present"||c=="legacy"||c=="file_aliases"||c=="mixed_legacy"||c=="existing_subwindow"||c=="duplicates"||c=="inactive_listed";
 if(existing){check(created.empty(),"existing panel was initialized again");check(chart_snapshot()==before_chart,"existing chart changed");}
 else if(c=="scan_fail"||c=="name_fail"||c=="indicator_list_fail"||c=="indicator_list_zero_fail"){check(created.empty(),"uncertain scan created panels");check(chart_snapshot()==before_chart,"scan failure changed chart");}
 else if(c=="account_present"){check(created==std::vector<string>{nocuda_path},"account was recreated");check(windows[0].size()==2,"missing NoCuda addition");}
 else if(c=="nocuda_present"){check(created==std::vector<string>{account_path},"NoCuda was recreated");check(windows[0].size()==2,"missing account addition");}
 else if(c=="account_present_companion_fail"){check(created==std::vector<string>{nocuda_path},"existing account recreated on companion failure");check(chart_snapshot()==before_chart,"companion failure changed existing account");}
 else if(c=="nocuda_present_companion_fail"){check(created==std::vector<string>{account_path},"existing NoCuda recreated on companion failure");check(chart_snapshot()==before_chart,"companion failure changed existing NoCuda");}
 else if(c=="create_account_fail"||c=="attach_account_fail"||c=="root_missing_with_shadow_fail"){check(windows[0].size()==1&&windows[0][0].name=="Stoikus · NoCuda Channels","account failure must preserve successful NoCuda");}
 else if(c=="create_nocuda_fail"||c=="attach_nocuda_fail"||c=="partial_retry"||c=="attach_release_fail"){check(windows[0].size()==1&&windows[0][0].name.find("Stoikus · Cockpit ")==0,"NoCuda failure must preserve successful account");}
 else if(c=="attach_unconfirmed"){check(windows[0].empty(),"fixture unconfirmed addition created membership");}
 else {check(windows[0].size()==(c=="similar_unrelated"?4:2),"two panels missing");}
 bool failure=(c.find("fail")!=string::npos&&c!="release_fail")||c=="partial_retry"||c=="attach_unconfirmed";
 check((alerts.back().find("incompleta")!=string::npos)==failure,"result hides or invents partial failure");
 if(existing||c=="account_present"||c=="nocuda_present"){
  check(alerts.back().find("confira versão e dados")!=string::npos,"listed identity was treated as current data/version verification");
  check(alerts.back().find("não confirma funcionamento ou compatibilidade")!=string::npos,"listed inactive/unknown panel lacks health boundary");
  for(const auto &w:before_windows)for(const auto &i:w.second)check(alerts.back().find(i.name)!=string::npos,"found identity omitted from visible result");}
 if(c=="legacy"||c=="file_aliases"||c=="mixed_legacy"||c=="existing_subwindow"||c=="duplicates")
  check(alerts.back().find("Nome legado ou sem versão detectado")!=string::npos,"legacy mixture was silently accepted");
 if(c=="repeat"){
  auto one=chart_snapshot();auto creations=created;OnStart();
  check(chart_snapshot()==one&&created==creations&&objects==before_objects,"reexecution duplicated or reset panels");}
 if(c=="partial_retry"){
  fail_add=-1;OnStart();
  check(windows[0].size()==2&&std::count(created.begin(),created.end(),account_path)==1,"retry duplicated successful account");
  check(alerts.back().find("incompleta")==string::npos,"retry stayed partial");}
 if(c=="repeat"||c=="partial_retry")check(alerts.size()==2,"rerun did not emit exactly one additional result");
 if(c=="release_fail"||c=="release_nocuda_warning"||c=="attach_release_fail"){
  check(!resources.empty(),"release failure not exercised");
  const auto &message=alerts.back();auto role=message.find(c=="release_fail"?"Conta:":"NoCuda:");
  auto line_end=message.find("\n",role),warning=message.find("liberação do handle",role),error=message.find("4807",role);
  check(role!=string::npos&&warning<line_end&&error<line_end,
        "visible result omitted the specific handle release warning and native error");
  check(windows[0].size()==(c=="attach_release_fail"?1:2),"release warning removed an attached panel");}
 else check(resources.empty(),"script-owned handles leaked");
 std::cout<<"PASS "<<c<<" created="<<created.size()<<" main="<<windows[0].size()<<"\n";
 for(const auto &a:alerts)std::cout<<"ALERT "<<a<<"\n";
 return 0;
 }catch(const std::exception &e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<"\n";return 1;}
}
'''


def input_contract(root):
    found = {}
    for relative, expected in INPUTS.items():
        source = (root / MQL / relative).read_text()
        actual = [list(row) for row in re.findall(
            r'^input\s+(?!group\b)(\w+)\s+(\w+)\s*=\s*([^;]+);', source, re.M)]
        assert actual == expected, f'public input type/name/order/default changed: {relative}'
        found[relative] = actual
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    receipt = {'root': str(root), 'timestampUTC': datetime.now(timezone.utc).isoformat(),
               'nativeCompilation': 'NOT_RUN', 'nativeRuntime': 'NOT_RUN', 'cases': []}
    try:
        receipt['publicInputs'] = input_contract(root)
        assert (root / SCRIPT).is_file(), 'opening script absent: neither panel can be opened together'
        script = (root / SCRIPT).read_text()
        version = (root / VERSION).read_text()
        receipt['scriptSha256'] = hashlib.sha256(script.encode()).hexdigest()
        receipt['versionSha256'] = hashlib.sha256(version.encode()).hexdigest()
        compiler = shutil.which('clang++') or shutil.which('g++')
        assert compiler, 'C++ compiler unavailable for host script execution'
        receipt['compiler'] = subprocess.check_output([compiler, '--version'], text=True).splitlines()[0]
        # Version definitions come from the actual candidate. Every script
        # function is compiled unchanged; MQL's two metadata directives are
        # the only syntax removed. Any unseamed unsafe API fails compilation.
        program = re.sub(r'^\s*#property[^\n]*\n', '', script, flags=re.M)
        program = program.replace('#include <JPWealth/JPW_Alavancagem_Version.mqh>', '')
        with tempfile.TemporaryDirectory(prefix='jpw-stoikus-host-') as folder:
            cpp, exe = Path(folder) / 'startup.cpp', Path(folder) / 'startup'
            cpp.write_text(version + '\n' + SHIM + '\n' + program + '\n' + MAIN)
            command = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(exe)]
            result = subprocess.run(command, text=True, capture_output=True)
            receipt['hostCompile'] = {'exitCode': result.returncode, 'output': result.stdout + result.stderr}
            assert result.returncode == 0, f'host compilation failed:\n{result.stderr}'
            for case in CASES:
                result = subprocess.run([str(exe), case], text=True, capture_output=True)
                receipt['cases'].append({'case': case, 'exitCode': result.returncode,
                                         'output': result.stdout + result.stderr})
                assert result.returncode == 0, f'{case}: {result.stdout}{result.stderr}'
        receipt['outcome'] = 'PASS'
        print(f'PASS: actual opening script executed in {len(CASES)} host scenarios; '
              '20 original public inputs preserved. Native compile/runtime NOT_RUN.')
        return 0
    except (AssertionError, OSError) as error:
        receipt['outcome'] = 'FAIL'
        receipt['failure'] = str(error)
        print(f'FAIL: {error}')
        return 1
    finally:
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exercise the production operation-scope selector with synthetic MT5 rows.

This checks no account and no native MT5 chart. Native compilation/clicks remain
separate evidence.
"""

from __future__ import annotations

from pathlib import Path
from leverage_source import expanded_source
import hashlib
import shutil
import subprocess
import tempfile

from leverage_panel_test import body_of


ROOT = Path(__file__).resolve().parents[1]
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"

SHIM = r'''
#include <cmath>
#include <climits>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
using ulong=unsigned long;
using JPW_GENESIS_STORE_STATE=int;
constexpr int JPW_GENESIS_VALID=0,JPW_GENESIS_ABSENT=1,JPW_GENESIS_INVALID=2;
constexpr int JPW_GENESIS_ACTIVE=1,JPW_GENESIS_CLOSED=2,JPW_GENESIS_REVERSED=3;
constexpr int JPW_STOP_RISK_POSITION=1,JPW_STOP_RISK_PENDING=2;
constexpr int POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1;
constexpr int InpGenesisTicket=0;
const string JPW_GENESIS_FOLDER="synthetic";
struct JPWAccount {long login=17;};
struct JPWGenesisRecord {int reference_state=JPW_GENESIS_ACTIVE;string symbol;
 long direction=POSITION_TYPE_BUY,identifier=0,origin_ticket=0,opened_msc=0;};
struct JPWStopRiskRow {int kind=0,side=0;long ticket=0,identifier=0,opened_msc=0;string symbol;};
int saved_state=JPW_GENESIS_ABSENT;JPWGenesisRecord saved;
void JPWGenesisClear(JPWGenesisRecord&r){r=JPWGenesisRecord();}
int JPWGenesisRead(JPWAccount&,long,const string&,JPWGenesisRecord&r){r=saved;return saved_state;}
template<class T> int ArraySize(const std::vector<T>&v){return (int)v.size();}
bool MathIsValidNumber(double x){return std::isfinite(x);}
bool JPWFinitePositive(double x){return std::isfinite(x)&&x>0;}
int StringFind(const string&s,const string&needle){auto at=s.find(needle);
 return at==string::npos?-1:(int)at;}
int StringReplace(string&s,const string&a,const string&b){int count=0;size_t at=0;
 while((at=s.find(a,at))!=string::npos){s.replace(at,a.size(),b);at+=b.size();count++;}
 return count;}
template<class... A> string StringFormat(const char*fmt,A...args){char out[80];
 std::snprintf(out,sizeof(out),fmt,args...);return out;}
long g_stop_genesis_identifier=0,g_stop_genesis_ticket=0,g_stop_genesis_opened_msc=0;
bool g_stop_genesis_closed=false;
string g_panel_prefix="JPW_TEST_";
bool g_raiz_panel_built=true,g_editing_field=false;
int g_focus_count=0;
std::vector<string> objects;
int ObjectsTotal(int,int,int){return (int)objects.size();}
string ObjectName(int,int index,int,int){return objects.at(index);}
bool ObjectDelete(int,const string&name){
 for(size_t i=0;i<objects.size();i++){
  if(objects[i]==name){objects.erase(objects.begin()+i);return true;}
 }
 return false;
}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const string&message){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<message<<'\n';}}
JPWStopRiskRow position(long ticket,long identifier,long opened,const string&symbol,int side){
 JPWStopRiskRow r;r.kind=JPW_STOP_RISK_POSITION;r.ticket=ticket;r.identifier=identifier;
 r.opened_msc=opened;r.symbol=symbol;r.side=side;return r;}
JPWStopRiskRow pending(long ticket,long opened,const string&symbol,int side){
 JPWStopRiskRow r;r.kind=JPW_STOP_RISK_PENDING;r.ticket=ticket;
 r.opened_msc=opened;r.symbol=symbol;r.side=side;return r;}
int main(){
 JPWAccount account;string symbol,source,reason;int side=0;
 std::vector<JPWStopRiskRow> rows={position(9,90,100,"NZDUSD.m",1),
  position(10,100,200,"NZDUSD.m",1),pending(11,300,"EURUSD",1)};
 check(JPWStopRiskResolveScope(account,rows,symbol,side,source,reason)&&
       symbol=="NZDUSD.m"&&side==1&&source=="Inferred"&&
       g_stop_genesis_identifier==90,"unique open group chooses exact symbol/side and oldest identity");
 rows.push_back(position(12,120,300,"EURUSD",1));
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason)&&
       reason.find("Vários grupos")!=string::npos,"two open groups refuse inference");
 rows.pop_back();rows[1].opened_msc=100;
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason)&&
       reason.find("mais antiga")!=string::npos,"oldest timestamp tie refuses inferred Genesis");
 rows={pending(11,300,"NZDUSD.m",1)};
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason),
       "pending-only set does not invent an operation");
 saved_state=JPW_GENESIS_VALID;saved.symbol="NZDUSD.m";
 saved.direction=POSITION_TYPE_BUY;saved.identifier=90;saved.origin_ticket=9;
 saved.opened_msc=100;saved.reference_state=JPW_GENESIS_CLOSED;
 rows={position(10,100,200,"NZDUSD.m",1)};
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason)&&
       g_stop_genesis_closed&&g_stop_genesis_identifier==90&&
       reason.find("encerrada")!=string::npos,
       "closed Genesis refuses successor risk in same symbol/direction");
 rows.push_back(pending(11,300,"NZDUSD.m",1));
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason)&&
       g_stop_genesis_closed,
       "closed Genesis refuses later pending reserve in same symbol/direction");
 rows.pop_back();
 saved.reference_state=JPW_GENESIS_ACTIVE;
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason),
       "missing active recorded reference refuses unconfirmed closure");
 saved.reference_state=JPW_GENESIS_REVERSED;
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason),
       "netting reversal refuses recorded reference");
 saved_state=JPW_GENESIS_INVALID;
 check(!JPWStopRiskResolveScope(account,rows,symbol,side,source,reason),
       "invalid Genesis storage cannot fall back to inference");
 check(JPWStopRiskMoney(0.)=="0,00"&&JPWStopRiskMoney(0.001)=="<0,01"&&
       JPWStopRiskMoney(-1.)=="N/A","money formatter never rounds positive amount to zero");
 JPWStopRiskRow selected=position(9,90,100,"NZDUSD.m",1);
 std::vector<JPWStopRiskRow> next={position(10,100,200,"NZDUSD.m",1),
                                   position(9,90,100,"NZDUSD.m",1)};
 check(JPWStopRiskRebindIndex(selected,next)==1,
       "new EA generation preserves drilldown for the same open position");
 next[1].side=-1;
 check(JPWStopRiskRebindIndex(selected,next)<0,
       "reversal does not bind an old drilldown to a new direction");
 next[1].side=1;next[1].ticket=12;
 check(JPWStopRiskRebindIndex(selected,next)<0,
       "closed/replaced ticket cannot inherit old row detail");
 check(JPWStopRiskRowInScope(selected,true,"NZDUSD.m",1)&&
       !JPWStopRiskRowInScope(selected,false,"NZDUSD.m",1)&&
       !JPWStopRiskRowInScope(selected,true,"NZDUSD.m",-1),
       "rebind requires current attributed symbol and direction");
 check(!JPWFullRefreshDue(5001,1,3600)&&
       !JPWFullRefreshDue(30000,1,3600)&&
       JPWFullRefreshDue(30001,1,3600)&&
       JPWFullRefreshDue(5,100,3600),
       "one-hour input has five-second risk checks and full freshness cap at 30 seconds");
 check(JPWFullRefreshRequired(true,false,5001,1,3600)&&
       JPWFullRefreshRequired(false,true,5001,1,3600)&&
       !JPWFullRefreshRequired(false,false,5001,1,3600),
       "account or connection change forces full refresh even with one-hour setting");
 check(!JPWFullReadingExpired(30001,1)&&
       JPWFullReadingExpired(30002,1)&&
       JPWFullReadingExpired(3600000,1),
       "cached full-reading numbers expire after 30 seconds even with one-hour cadence");
 objects={"JPW_TEST_RAIZ_UI_BG","JPW_TEST_RAIZ_UI_BUTTON_40",
          "JPW_TEST_RAIZ_UI_BUTTON_60","JPW_TEST_RAIZ_UI_BUTTON_80",
          "JPW_TEST_RAIZ_UI_STOP_TOTAL","JPW_TEST_RAIZ_UI_STOP_SCOPE",
          "JPW_COCKPIT_PREF_V2","OTHER_RAIZ_UI_BUTTON_80"};
 JPWRaizPanelDestroy();
 check(objects.size()==2 && objects[0]=="JPW_COCKPIT_PREF_V2"&&
       objects[1]=="OTHER_RAIZ_UI_BUTTON_80"&&!g_raiz_panel_built,
       "production destroy removes all dialog objects including Stop buttons only");
 std::cout<<"STOP_UI_SCOPE: "<<checks-failures<<" PASS / "<<failures<<" FAIL; MT5 NOT_RUN\n";
 return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: C++ compiler unavailable; native MT5 NOT_RUN")
        return 2
    source = expanded_source(INDICATOR)
    extracted = (
        "string JPWStopRiskMoney(const double value){" +
        body_of(source, "string JPWStopRiskMoney(const double value)") + "}\n" +
        "bool JPWStopRiskResolveScope(JPWAccount &account,"
        "std::vector<JPWStopRiskRow> &rows,string &symbol,int &side,"
        "string &provenance,string &reason){" +
        body_of(source, "bool JPWStopRiskResolveScope(") + "}\n" +
        "int JPWStopRiskRebindIndex(JPWStopRiskRow &chosen,"
        "std::vector<JPWStopRiskRow> &rows){" +
        body_of(source, "int JPWStopRiskRebindIndex(") + "}\n" +
        "bool JPWStopRiskRowInScope(JPWStopRiskRow &row,const bool scope_valid,"
        "const string symbol,const int side){" +
        body_of(source, "bool JPWStopRiskRowInScope(") + "}\n" +
        "void JPWRaizPanelDestroy(){" +
        body_of(source, "void JPWRaizPanelDestroy()") + "}\n" +
        "bool JPWFullRefreshDue(const ulong now_ms,const ulong last_ms,"
        "const int requested_seconds){" +
        body_of(source, "bool JPWFullRefreshDue(") + "}\n" +
        "bool JPWFullRefreshRequired(const bool account_changed,"
        "const bool connection_changed,const ulong now_ms,const ulong last_ms,"
        "const int requested_seconds){" +
        body_of(source, "bool JPWFullRefreshRequired(") + "}\n" +
        "bool JPWFullReadingExpired(const ulong now_ms,const ulong last_ms){" +
        body_of(source, "bool JPWFullReadingExpired(") + "}\n"
    )
    display = body_of(source, "void JPWMonitorStopRisk()")
    timer = body_of(source, "void OnTimer()")
    init = body_of(source, "int OnInit()")
    cockpit = body_of(source, "void JPWRenderCockpit()")
    expire = body_of(source, "void JPWExpireTimedMetrics()")
    assert "const bool stop_was_ready=g_stop_ready;" in display
    assert "JPWDetailsReadStopRisk();" in display
    assert "JPWStopRiskRefreshRowView();" in display
    assert "JPWRaizPanelDestroy();" in display
    assert display.count("JPWInvalidateIdentityPresentation();") >= 2
    assert "JPWRender(" not in display
    assert "JPWFullRefreshRequired(account_changed,connection_changed," in timer
    assert "JPWExpireTimedMetrics();" in timer
    assert 'g_panel_value="N/D";' in expire and 'g_scale2_value="N/A";' in expire
    assert "g_last_full_refresh_utc" in expire and "JPW_VIEW_NA" in expire
    assert "JPWRenderCurrentDisplay();" in timer
    assert "const int timer_seconds=(InpUpdateSeconds<5 ? InpUpdateSeconds : 5);" in init
    assert "if(i==3 || i==4)" in cockpit
    assert "leitura completa no máximo a cada 30 s" in cockpit
    print("SOURCE_SHA256:", hashlib.sha256(INDICATOR.read_bytes()).hexdigest())
    with tempfile.TemporaryDirectory(prefix="jpw-stop-ui-") as directory:
        cpp = Path(directory) / "scope.cpp"
        binary = Path(directory) / "scope"
        cpp.write_text(SHIM + extracted + MAIN, encoding="utf-8")
        for command in ((compiler, "-std=c++17", "-Wall", "-Wextra", str(cpp), "-o", str(binary)),
                        (str(binary),)):
            result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                print("EXIT_CODE:", result.returncode)
                return result.returncode
    print("EXIT_CODE: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

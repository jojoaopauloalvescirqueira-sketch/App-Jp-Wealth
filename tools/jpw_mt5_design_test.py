#!/usr/bin/env python3
"""Replay Cockpit keyboard ownership using production helper and event wrapper.

Only the native API and downstream callback are substitutes here. The existing
details-event focal separately executes the production actions. These host
checks do not claim native MT5 focus, drawing, or event-order evidence.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from leverage_panel_test import body_of


ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh"
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"

SHIM = r'''
#include <cmath>
#include <iostream>
#include <string>
using string=std::string;using ulong=unsigned long;
constexpr int CHARTEVENT_KEYDOWN=1,CHARTEVENT_OBJECT_CLICK=2,CHARTEVENT_CLICK=3,
 CHARTEVENT_OBJECT_ENDEDIT=4,CHARTEVENT_CHART_CHANGE=5,CHARTEVENT_OBJECT_DRAG=6;
string g_panel_prefix="JPW_TEST_";
ulong clock_ms=1000;
ulong GetTickCount64(){return clock_ms;}
bool MathIsValidNumber(double n){return std::isfinite(n);}
long MathAbs(long n){return std::abs(n);}
int StringFind(const string& s,const string& part){const size_t p=s.find(part);return p==string::npos?-1:static_cast<int>(p);}
int calls=0,key_calls=0,edit_commits=0,applies=0;
bool editing=false;string edit_draft="original";
void JPWHandleChartEvent(const int id,const long& key,const double&,const string& name){
 calls++;
 if(id==CHARTEVENT_OBJECT_CLICK)editing=name=="JPW_TEST_RAIZ_UI_EDIT_17";
 if(id==CHARTEVENT_OBJECT_ENDEDIT&&name=="JPW_TEST_RAIZ_UI_EDIT_17"){
   editing=false;edit_commits++;edit_draft="confirmed draft";}
 if(id==CHARTEVENT_KEYDOWN){key_calls++;if(key==13&&!editing)applies++;}
}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool c,const string&why){checks++;if(!c){failures++;std::cerr<<"FAIL "<<why<<'\n';}}
void event(int id,long x=0,double y=0.,const string& name=""){OnChartEvent(id,x,y,name);}
void key(long k){event(CHARTEVENT_KEYDOWN,k);}
int main(){
 key(13);check(calls==0,"no keyboard ownership before an explicit click");
 event(CHARTEVENT_OBJECT_CLICK,12,34,"JPW_TEST_RAIZ_DETAILS_BUTTON");
 check(calls==1,"own launcher event retains downstream handling");
 key(9);key(13);check(key_calls==2&&applies==1,"own clicked component receives Tab and Enter");
 event(CHARTEVENT_OBJECT_CLICK,12,34,"JPWNC_UI_EDIT_DATE");
 const int foreign_calls=calls,foreign_keys=key_calls,foreign_applies=applies;
 for(long k:{9L,13L,27L,37L,39L,49L})key(k);
 check(calls==foreign_calls&&key_calls==foreign_keys&&applies==foreign_applies,
       "NoCuda editor owns all subsequent cockpit shortcuts");
 event(CHARTEVENT_OBJECT_CLICK,18,45,"JPW_TEST_RAIZ_UI_EDIT_17");
 key(13);check(editing&&applies==foreign_applies,"own editor preserves editing instead of activating action");
 event(CHARTEVENT_OBJECT_ENDEDIT,0,0.,"JPW_TEST_RAIZ_UI_EDIT_17");
 check(edit_commits==1&&!editing&&edit_draft=="confirmed draft","own ENDEDIT reaches existing field handling");
 key(13);check(applies==foreign_applies+1,"own editor retains ownership after commit");
 event(CHARTEVENT_OBJECT_CLICK,40,50,"JPWNC_UI_EDIT_DATE");
 event(CHARTEVENT_OBJECT_ENDEDIT,0,0.,"JPW_TEST_RAIZ_UI_EDIT_17");
 const int after_late=calls,after_late_applies=applies;
 key(13);check(calls==after_late&&applies==after_late_applies,
       "late own ENDEDIT cannot steal focus back from NoCuda");
 check(edit_commits==2,"late owned field data still commits through existing handler");
 event(CHARTEVENT_OBJECT_CLICK,90,100,"JPW_TEST_RAIZ_UI_BUTTON_40");
 event(CHARTEVENT_CLICK,90,100);const int paired_keys=key_calls;
 key(9);key(13);check(key_calls==paired_keys+2,"OBJECT_CLICK then matching CLICK keeps owned focus");
 event(CHARTEVENT_CLICK,140,160);
 event(CHARTEVENT_OBJECT_CLICK,140,160,"JPW_TEST_RAIZ_UI_BUTTON_40");
 const int reverse_keys=key_calls;key(9);key(13);
 check(key_calls==reverse_keys+2,"CLICK then OBJECT_CLICK acquires owned focus");
 event(CHARTEVENT_OBJECT_CLICK,140,160,"OTHER_CONTROL");
 event(CHARTEVENT_CLICK,140,160);const int foreign_pair=calls;key(13);
 check(calls==foreign_pair,"foreign OBJECT_CLICK then CLICK ends without cockpit focus");
 event(CHARTEVENT_CLICK,170,180);
 event(CHARTEVENT_OBJECT_CLICK,170,180,"OTHER_CONTROL");
 const int foreign_reverse=calls;key(13);
 check(calls==foreign_reverse,"foreign CLICK then OBJECT_CLICK ends without cockpit focus");
 event(CHARTEVENT_OBJECT_CLICK,200,220,"JPW_TEST_RAIZ_UI_BUTTON_40");
 event(CHARTEVENT_CLICK,201,222);const int tolerant_keys=key_calls;key(9);
 check(key_calls==tolerant_keys+1,"one paired gesture tolerates small coordinate difference");
 event(CHARTEVENT_CLICK,201,222);const int consumed_calls=calls;key(13);
 check(calls==consumed_calls,"a matched pair is consumed rather than exempting later background clicks");
 event(CHARTEVENT_OBJECT_CLICK,240,260,"JPW_TEST_RAIZ_UI_BUTTON_40");
 clock_ms+=1501;event(CHARTEVENT_CLICK,240,260);const int aged_calls=calls;key(13);
 check(calls==aged_calls,"an old object gesture does not own a later chart click");
 event(CHARTEVENT_OBJECT_CLICK,300,320,"JPW_TEST_RAIZ_UI_BUTTON_40");
 event(CHARTEVENT_CLICK,350,370);const int background_calls=calls;key(13);
 check(calls==background_calls,"separate background click releases ownership");
 event(CHARTEVENT_OBJECT_CLICK,380,390,"JPW_TEST_RAIZ_UI_BUTTON_40");
 clock_ms--;event(CHARTEVENT_CLICK,380,390);const int rollback_calls=calls;key(13);
 check(calls==rollback_calls,"clock rollback refuses click-pair retention");
 const int others_before=calls;
 event(CHARTEVENT_OBJECT_DRAG,0,0.,"OTHER_LINE");
 event(CHARTEVENT_CHART_CHANGE);event(CHARTEVENT_OBJECT_ENDEDIT,0,0.,"OTHER_EDIT");
 check(calls==others_before+3,"non-key event handling remains delegated unchanged");
 event(CHARTEVENT_OBJECT_CLICK,40,50,"JPW_TEST_RAIZ_UI_BUTTON_40");
 g_panel_prefix="";const int blank_calls=calls;key(13);
 check(calls==blank_calls,"empty runtime prefix cannot retain keyboard ownership");
 std::cout<<"HOST_MT5_UI_FOCUS: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native MT5 interaction NOT_RUN\n";
 return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no host C++ compiler")
        return 1
    helper_sig = "bool JPWCockpitAcceptChartEvent(const int id,const long &lparam,\n                                const double &dparam,const string &object_name)"
    wrapper_sig = "void OnChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)"
    helper = helper_sig + "{" + body_of(PRESENTATION.read_text(), helper_sig) + "}\n"
    wrapper = wrapper_sig + "{" + body_of(INDICATOR.read_text(), wrapper_sig) + "}\n"
    print(json.dumps({"kind": "HOST_SYNTHETIC_NOT_MT5", "source_sha256": {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (PRESENTATION, INDICATOR)
    }}, indent=2), flush=True)
    with tempfile.TemporaryDirectory(prefix="jpw-mt5-ui-focus-") as temporary:
        path, binary = Path(temporary) / "focus.cpp", Path(temporary) / "focus"
        path.write_text(SHIM + helper + wrapper + MAIN, encoding="utf-8")
        for cmd in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)], [str(binary)]):
            result = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=60)
            print(result.stdout, end=""); print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

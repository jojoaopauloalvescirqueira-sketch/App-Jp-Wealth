#!/usr/bin/env python3
"""Run the actual pure MQL panel preference module through the existing C++ shim pattern.

Source/oracle: docs/work/CHG-STOIKUS-PAINEL-PERSONALIZAVEL-20261021.md,
section Critérios congelados and its human-approved delegated interface.
Catches mask/order coupling, noncanonical decoding, partial mutation and lost
metrics during movement. Native MQL compilation, objects, UI and templates
remain NOT_RUN; this additive focal is not registered in the full runner.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

from leverage_source import expanded_source

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_PanelPrefs.mqh'
SHIM = r'''
#include <algorithm>
#include <climits>
#include <cstdio>
#include <iostream>
#include <string>
using string=std::string;
using ushort=unsigned short;
int StringLen(const string &s){return static_cast<int>(s.size());}
ushort StringGetCharacter(const string &s,int i){return static_cast<ushort>(s.at(i));}
string StringSubstr(const string &s,int start,int length){return s.substr(start,length);}
template<typename... A> string StringFormat(const string &fmt,A... args){
 char out[160];std::snprintf(out,sizeof(out),fmt.c_str(),args...);return out;
}
'''
MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const string &why){
 checks++;if(!ok){failures++;if(failures<=40)std::cerr<<"FAIL "<<why<<"\n";}
}
bool same(const JPWStoikusPanelPrefs &a,const JPWStoikusPanelPrefs &b){
 if(a.visible_mask!=b.visible_mask)return false;
 for(int i=0;i<7;i++)if(a.order[i]!=b.order[i])return false;
 return true;
}
int main(){
 JPWStoikusPanelPrefs defaults;
 JPWStoikusPanelPrefsDefault(defaults);
 const JPWStoikusPanelPrefs expected_default={57,{0,5,3,4,1,2,6}};
 const JPWStoikusPanelPrefs legacy_all={127,{0,5,1,2,3,4,6}};
 check(same(defaults,expected_default),"new default is mask 57 with order 0534126");
 check(JPWStoikusPanelPrefsValid(defaults),"default valid");
 check(JPWStoikusPanelPrefsEncode(defaults)=="V1|57|0534126","exact hand-derived default encoding");
 check(JPWStoikusPanelPrefsEncode(legacy_all)=="V1|127|0512346","exact hand-derived legacy full encoding");
 const JPWStoikusPanelPrefs reverse_empty={0,{6,5,4,3,2,1,0}};
 check(JPWStoikusPanelPrefsEncode(reverse_empty)=="V1|0|6543210","empty selection keeps complete nondefault order");
 JPWStoikusPanelPrefs target=legacy_all;
 check(JPWStoikusPanelPrefsDecode("V1|57|0534126",target)&&same(target,expected_default),"literal decode independent of encoder");
 check(JPWStoikusPanelPrefsDecode("V1|0|6543210",target)&&same(target,reverse_empty),"zero is valid and preserves full order");
 check(JPWStoikusPanelPrefsDecode("V1|127|0512346",target)&&same(target,legacy_all),"127 is valid");
 for(int mask=0;mask<128;mask++){
  JPWStoikusPanelPrefs p=expected_default;p.visible_mask=mask;
  JPWStoikusPanelPrefs out=reverse_empty;
  check(JPWStoikusPanelPrefsValid(p),"all seven-bit selections valid");
  check(JPWStoikusPanelPrefsDecode(JPWStoikusPanelPrefsEncode(p),out)&&same(p,out),"all masks roundtrip without changing order");
  JPWStoikusPanelPrefsLegacy(0,mask,out);
  check(out.visible_mask==(mask&33),"legacy compact preserves exactly previously displayed bits");
  for(int i=0;i<7;i++)check(out.order[i]==legacy_all.order[i],"legacy compact preserves old presentation order");
  JPWStoikusPanelPrefsLegacy(1,mask,out);
  check(out.visible_mask==mask,"legacy normal preserves every previous selection including zero");
  for(int i=0;i<7;i++)check(out.order[i]==legacy_all.order[i],"legacy normal order unchanged");
 }
 const string bad[]={"","V0|57|0534126","V2|57|0534126","v1|57|0534126","V01|57|0534126",
  "V1|057|0534126","V1|00|0534126","V1|+57|0534126","V1|-1|0534126",
  "V1|128|0534126","V1|99999999999999999999|0534126","V1|5.7|0534126",
  "V1||0534126","V1| 57|0534126"," V1|57|0534126","V1|57 |0534126",
  "V1|57|0534126 ","V1|57|0534126\n","V1|57|0534126|","V1|57|0534126|extra",
  "V1|57|053412","V1|57|05341260","V1|57|0534127","V1|57|053412-",
  "V1|57|053412a","V1|57|0534125","V1|57|0000000","V1|57|0,5,3,4,1,2,6",
  "V1|57|０５３４１２６","V1;57|0534126","V1|57;0534126","V1|57|"};
 for(const string &text:bad){
  target=legacy_all;
  check(!JPWStoikusPanelPrefsDecode(text,target),"reject malformed/noncanonical payload: "+text);
  check(same(target,legacy_all),"failed decode leaves all output fields unchanged");
 }
 const int invalid_masks[]={-1,128,INT_MIN,INT_MAX};
 for(int mask:invalid_masks){
  JPWStoikusPanelPrefs p=expected_default;p.visible_mask=mask;
  check(!JPWStoikusPanelPrefsValid(p)&&JPWStoikusPanelPrefsEncode(p)=="","invalid mask cannot serialize");
  JPWStoikusPanelPrefs before=p;
  check(!JPWStoikusPanelPrefsMove(p,3,1)&&same(p,before),"invalid mask cannot mutate via move");
 }
 for(int at=0;at<7;at++)for(int invalid:{-1,7,INT_MIN,INT_MAX}){
  JPWStoikusPanelPrefs p=expected_default;p.order[at]=invalid;
  check(!JPWStoikusPanelPrefsValid(p)&&JPWStoikusPanelPrefsEncode(p)=="","every slot rejects invalid metric");
  JPWStoikusPanelPrefs before=p;
  check(!JPWStoikusPanelPrefsMove(p,3,1)&&same(p,before),"invalid order leaves prefs unchanged on move");
 }
 for(int at=0;at<7;at++)for(int other=0;other<7;other++)if(at!=other){
  JPWStoikusPanelPrefs p=expected_default;p.order[at]=p.order[other];
  check(!JPWStoikusPanelPrefsValid(p)&&JPWStoikusPanelPrefsEncode(p)=="","duplicate metric rejected in every position");
 }
 JPWStoikusPanelPrefs p=expected_default;
 check(JPWStoikusPanelPrefsMove(p,3,-1)&&JPWStoikusPanelPrefsEncode(p)=="V1|57|0354126","up swaps requested metric with previous slot");
 check(JPWStoikusPanelPrefsMove(p,3,1)&&same(p,expected_default),"inverse move restores original");
 check(JPWStoikusPanelPrefsMove(p,1,-1)&&JPWStoikusPanelPrefsEncode(p)=="V1|57|0531426","hidden metric moves without changing selection");
 for(int metric:{-1,7,INT_MIN,INT_MAX}){
  p=expected_default;
  check(!JPWStoikusPanelPrefsMove(p,metric,1)&&same(p,expected_default),"invalid metric movement is atomic refusal");
 }
 for(int direction:{-2,0,2,INT_MIN,INT_MAX}){
  p=expected_default;
  check(!JPWStoikusPanelPrefsMove(p,3,direction)&&same(p,expected_default),"only single-step directions allowed");
 }
 int permutation[7]={0,1,2,3,4,5,6};int permutations=0;
 do{
  permutations++;
  for(int mask:{0,57,127}){
   JPWStoikusPanelPrefs initial;initial.visible_mask=mask;
   for(int i=0;i<7;i++)initial.order[i]=permutation[i];
   JPWStoikusPanelPrefs out=reverse_empty;
   check(JPWStoikusPanelPrefsValid(initial),"every complete permutation valid independently of visibility");
   check(JPWStoikusPanelPrefsDecode(JPWStoikusPanelPrefsEncode(initial),out)&&same(out,initial),"permutation roundtrip preserves all seven identities");
   for(int at=0;at<7;at++)for(int direction:{-1,1}){
    p=initial;const int next=at+direction;
    const bool moved=JPWStoikusPanelPrefsMove(p,permutation[at],direction);
    if(next<0||next>6){
     check(!moved&&same(p,initial),"first/last movement refuses and preserves all fields");
    }else{
     check(moved&&p.visible_mask==mask,"successful movement never changes visibility");
     for(int i=0;i<7;i++){
      const int expected=(i==at ? initial.order[next] : (i==next ? initial.order[at] : initial.order[i]));
      check(p.order[i]==expected,"move swaps adjacent slots only, preserving all other identities");
     }
     check(JPWStoikusPanelPrefsValid(p),"movement keeps a permutation");
    }
   }
  }
 }while(std::next_permutation(permutation,permutation+7));
 check(permutations==5040,"all 5040 seven-metric permutations executed");
 std::cout<<"Stoikus panel prefs checks="<<checks<<" permutations="<<permutations<<" failures="<<failures<<"; native NOT_RUN\n";
 return failures?1:0;
}
'''


def run() -> None:
    compiler = shutil.which('clang++') or shutil.which('g++')
    if compiler is None:
        raise SystemExit('ENVIRONMENT_ERROR: C++ compiler unavailable')
    source = expanded_source(INCLUDE)
    print(f'production_sha256={hashlib.sha256(INCLUDE.read_bytes()).hexdigest()}', flush=True)
    print(f'test_sha256={hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}', flush=True)
    with tempfile.TemporaryDirectory(prefix='stoikus-panel-prefs-') as directory:
        cpp = Path(directory) / 'test.cpp'
        binary = Path(directory) / 'test'
        cpp.write_text(SHIM + source + MAIN, encoding='utf-8')
        subprocess.run([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', str(cpp), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    run()

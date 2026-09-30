#!/usr/bin/env python3
"""Exercise the production Cockpit preference/quality code in a host shim.

Chart objects, template persistence, clicks and DPI still require native MT5.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from leverage_source import expanded_source
import shutil
import subprocess
import tempfile
from leverage_panel_test import body_of


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh"
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"

SHIM = r'''
#include <cstdio>
#include <cmath>
#include <climits>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using string=std::string;
using ushort=unsigned short;
using ulong=unsigned long;
bool MathIsValidNumber(double x){return std::isfinite(x);}
constexpr int CORNER_LEFT_UPPER=0,CORNER_LEFT_LOWER=1,CORNER_RIGHT_LOWER=3,CORNER_RIGHT_UPPER=2;
int StringLen(const string &s) { return static_cast<int>(s.size()); }
ushort StringGetCharacter(const string &s,int i) { return static_cast<ushort>(s.at(i)); }
int StringFind(const string &s,const string &needle) {
  const size_t at=s.find(needle); return at==string::npos ? -1 : static_cast<int>(at);
}
string StringSubstr(const string &s,int start) { return s.substr(start); }
std::map<long,std::map<string,string>> saved_chart_objects;
long active_chart=101;
int ObjectsTotal(int,int,int) { return static_cast<int>(saved_chart_objects[active_chart].size()); }
string ObjectName(int,int index,int,int) {
  auto iter=saved_chart_objects[active_chart].begin(); std::advance(iter,index); return iter->first;
}
bool ObjectDelete(int,const string &name) { return saved_chart_objects[active_chart].erase(name)>0; }
template<typename... A> string StringFormat(const string &fmt,A... args) {
  char result[160];
  std::snprintf(result,sizeof(result),fmt.c_str(),args...);
  return result;
}
int StringSplit(const string &s,char delimiter,std::vector<string> &out) {
  out.clear();
  size_t from=0;
  for(size_t i=0;i<=s.size();i++) if(i==s.size() || s[i]==delimiter) {
    out.push_back(s.substr(from,i-from)); from=i+1;
  }
  return static_cast<int>(out.size());
}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const string &why) {
  checks++;
  if(!ok) { failures++; std::cerr << "FAIL " << why << '\n'; }
}
int main() {
  check(JPWCockpitHUDTarget(true,5,0)==5 && JPWCockpitHUDTarget(true,-1,0)==-1 &&
        JPWCockpitHUDTarget(false,-1,2)==2,"summary routes its actual visible metric or generic launcher");
  check(JPWCockpitNextCorner(CORNER_LEFT_UPPER)==CORNER_RIGHT_UPPER &&
        JPWCockpitNextCorner(CORNER_RIGHT_UPPER)==CORNER_RIGHT_LOWER &&
        JPWCockpitNextCorner(CORNER_RIGHT_LOWER)==CORNER_LEFT_LOWER &&
        JPWCockpitNextCorner(CORNER_LEFT_LOWER)==CORNER_LEFT_UPPER,
        "visual clockwise corner cycle uses real MT5 enum order");
  check(JPWCockpitCornerName(CORNER_LEFT_LOWER)=="Inferior esquerdo" &&
        JPWCockpitCornerName(CORNER_RIGHT_UPPER)=="Superior direito", "corner labels agree with enum geometry");
  JPWCockpitPrefs defaults;
  JPWCockpitDefault(defaults);
  check(defaults.visible_mask==63 && defaults.corner==0 && defaults.density==0,
        "absent object defaults to six visible compact rows");
  check(JPWCockpitQualityText(JPW_VIEW_CURRENT)=="Current" &&
        JPWCockpitQualityText(JPW_VIEW_ESTIMATED)=="Estimated" &&
        JPWCockpitQualityText(JPW_VIEW_NA)=="N/A",
        "typed quality labels stay distinct");
  for(int mask=0;mask<=63;mask++) for(int corner=0;corner<4;corner++)
    for(int density=0;density<2;density++) {
      JPWCockpitPrefs initial={mask,corner,density};
      string encoded=JPWCockpitEncode(initial);
      JPWCockpitPrefs restored={-7,-7,-7};
      check(!encoded.empty() && JPWCockpitDecode(encoded,restored) &&
            restored.visible_mask==mask && restored.corner==corner &&
            restored.density==density,"valid preference roundtrip");
      for(int metric=0;metric<6;metric++)
        check(JPWCockpitVisible(restored,metric)==((mask & (1<<metric))!=0),
              "six visibility bits are independent");
      check(!JPWCockpitVisible(restored,-1) && !JPWCockpitVisible(restored,6),
            "out-of-range metric never leaks a row");
    }
  JPWCockpitPrefs none={0,3,1};
  check(!JPWCockpitEncode(none).empty() &&
        !JPWCockpitVisible(none,0) && !JPWCockpitVisible(none,4),
        "all-hidden remains valid so the indicator can retain its launcher");
  JPWCockpitPrefs invalid={64,0,0};
  check(JPWCockpitEncode(invalid).empty(),"unknown visibility bit refused");
  invalid={63,4,0};
  check(JPWCockpitEncode(invalid).empty(),"unknown corner refused");
  invalid={63,0,2};
  check(JPWCockpitEncode(invalid).empty(),"unknown density refused");
  JPWCockpitPrefs good={19,2,1};
  string packet=JPWCockpitEncode(good);
  JPWCockpitPrefs target={7,1,0};
  const string bad[]={"", "JPWCOCKPIT|3|19|2|1|0", "JPWCOCKPIT|1|19|2|1|0",
                      "JPWCOCKPIT|1|19|2|1|0|extra", "JPWCOCKPIT|1|-1|2|1|0",
                      "JPWCOCKPIT|1|19x|2|1|0", "JPWCOCKPIT|1|999999999|2|1|0"};
  for(const string &value:bad) {
    check(!JPWCockpitDecode(value,target),"corrupt or incompatible object refused");
    check(target.visible_mask==7 && target.corner==1 && target.density==0,
          "failed decode preserves prior in-memory preference");
  }
  string tampered=packet;
  const size_t pos=tampered.find("|19|");
  check(pos!=string::npos,"known fixture field found");
  if(pos!=string::npos) tampered.replace(pos,4,"|18|");
  check(!JPWCockpitDecode(tampered,target),"checksum catches changed visibility");
  check(target.visible_mask==7,"checksum failure does not partially apply settings");
  JPWCockpitPrefs old={31,2,1};
  string old_packet=StringFormat("JPWCOCKPIT|1|%d|%d|%d|%d",old.visible_mask,
                                 old.corner,old.density,JPWCockpitChecksumVersion(old,1));
  check(JPWCockpitDecode(old_packet,target) && target.visible_mask==63 &&
        target.corner==2 && target.density==1,
        "valid V1 five-row preference adds sixth row without changing layout");
  old.visible_mask=0;
  old_packet=StringFormat("JPWCOCKPIT|1|%d|%d|%d|%d",old.visible_mask,
                          old.corner,old.density,JPWCockpitChecksumVersion(old,1));
  check(JPWCockpitDecode(old_packet,target) && target.visible_mask==0,
        "V1 all-hidden preference remains all-hidden");
  std::map<long,string> chart_objects;
  chart_objects[101]=packet;
  JPWCockpitPrefs other={63,0,0}; chart_objects[202]=JPWCockpitEncode(other);
  JPWCockpitPrefs chart_a,chart_b;
  check(JPWCockpitDecode(chart_objects[101],chart_a) &&
        JPWCockpitDecode(chart_objects[202],chart_b) &&
        chart_a.visible_mask==19 && chart_b.visible_mask==63,
        "two chart-scoped objects retain independent preferences in host model");
  check(packet.find("account")==string::npos && packet.find("symbol")==string::npos,
        "serialized preference has no account or symbol data");
  saved_chart_objects[101]={{"JPW_LEV_101_0","current metric"},
                            {"JPW_LEV_101_HUD_BG","current HUD"},
                            {"JPW_LEV_101_12345_0","pre-1.8 orphan"},
                            {"JPW_LEV_202_0","foreign template HUD"},
                            {"JPW_LEV_notes","unrelated user object"},
                            {JPW_COCKPIT_PREF_OBJECT,"preference"},
                            {"ManualTrendline","user object"}};
  saved_chart_objects[202]={{"JPW_LEV_202_0","other chart HUD"}};
  JPWCockpitRemoveForeignHUD("JPW_LEV_101_");
  check(saved_chart_objects[101].count("JPW_LEV_101_0") &&
        saved_chart_objects[101].count("JPW_LEV_101_HUD_BG") &&
        !saved_chart_objects[101].count("JPW_LEV_101_12345_0") &&
        !saved_chart_objects[101].count("JPW_LEV_202_0"),
        "current chart UI retained; old/foreign template UI removed");
  check(saved_chart_objects[101].count(JPW_COCKPIT_PREF_OBJECT) &&
        saved_chart_objects[101].count("ManualTrendline") &&
        saved_chart_objects[101].count("JPW_LEV_notes"),
        "preference and unrelated user objects never deleted");
  check(saved_chart_objects[202].count("JPW_LEV_202_0"),
        "cleanup does not touch another chart's objects");
  std::cout << "HOST_COCKPIT: " << checks-failures << " PASS / " << failures
            << " FAIL; chart/template lifecycle and MT5 clicks NOT_RUN\n";
  return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: C++ host compiler unavailable; native MT5 NOT_RUN")
        return 2
    source = expanded_source(INCLUDE).replace("string part[];", "std::vector<string> part;")
    indicator = expanded_source(INDICATOR)
    cleanup = "\n".join(
        signature + "{" + body_of(indicator, signature) + "}"
        for signature in ("bool JPWCockpitOwnedSuffix(const string suffix)",
                          "bool JPWCockpitOwnedUIName(const string name)",
                          "void JPWCockpitRemoveForeignHUD(const string current_prefix)"))
    print(f"SOURCE_SHA256: {hashlib.sha256(INCLUDE.read_bytes()).hexdigest()}")
    print("HOST_SYNTHETIC: production Cockpit.mqh with C++ MQL string shim")
    with tempfile.TemporaryDirectory(prefix="jpw-cockpit-host-") as directory:
        path = Path(directory) / "cockpit.cpp"
        binary = Path(directory) / "cockpit"
        path.write_text(SHIM + source + cleanup + MAIN, encoding="utf-8")
        for command in ((compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-o", str(binary)),
                        (str(binary),)):
            result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                print(f"EXIT_CODE: {result.returncode}")
                return result.returncode
    print("EXIT_CODE: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Host execution of the distributed pure H4 calendar and scale functions.

Only MQL array syntax and terminal-only methods are adapted. This is not
MetaEditor compilation or MT5 chart/runtime evidence.
"""

from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
CORE = MQL / "JPW_Alavancagem_RaizN_Core.mqh"
HORIZON = MQL / "JPW_Alavancagem_RaizN_Horizon.mqh"

SHIM = r'''
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
using datetime=long;
constexpr int TIME_DATE=1,TIME_SECONDS=2;
bool MathIsValidNumber(double x){return std::isfinite(x);}
double MathSqrt(double x){return std::sqrt(x);}
double MathAbs(double x){return std::abs(x);}
int StringLen(const string&s){return (int)s.size();}
int StringGetCharacter(const string&s,int i){return (unsigned char)s.at(i);}
string StringSubstr(const string&s,int pos,int len=-1){return s.substr(pos,len<0?string::npos:len);}
int StringFind(const string&s,const string&v){auto p=s.find(v);return p==string::npos?-1:(int)p;}
bool StringToUpper(string&s){std::transform(s.begin(),s.end(),s.begin(),::toupper);return true;}
int StringSplit(const string&s,char separator,std::vector<string>&out){out.clear();size_t at=0;
 while(true){auto next=s.find(separator,at);out.push_back(s.substr(at,next==string::npos?string::npos:next-at));
 if(next==string::npos)break;at=next+1;}return (int)out.size();}
template<class T> int ArraySize(const std::vector<T>&x){return (int)x.size();}
template<class T> int ArrayResize(std::vector<T>&x,int n){x.resize(n);return (int)x.size();}
datetime StringToTime(const string&s){int y=0,m=0,d=0,h=0,minute=0,sec=0;
 if(std::sscanf(s.c_str(),"%d.%d.%d %d:%d:%d",&y,&m,&d,&h,&minute,&sec)!=6)return 0;
 std::tm t={};t.tm_year=y-1900;t.tm_mon=m-1;t.tm_mday=d;t.tm_hour=h;t.tm_min=minute;t.tm_sec=sec;
 return (datetime)timegm(&t);}
string TimeToString(datetime value,int){char buf[32];std::time_t t=value;
 std::tm* p=std::gmtime(&t);if(!p)return "";
 std::strftime(buf,sizeof(buf),"%Y.%m.%d %H:%M:%S",p);return buf;}
'''

MAIN = r'''
int failed=0,passed=0;
void check(bool yes,const string&label){if(yes)++passed;else{++failed;std::cerr<<"FAIL "<<label<<'\n';}}
void add(std::vector<JPWHorizonSession>&s,datetime a,datetime b){s.push_back({a,b});}
int main(){
 double price=0.,pct=0.;
 check(JPWRaizNTimeScale(100.,.40,30,price,pct)==JPW_RAIZN_OK&&
       std::abs(price-2.1908902300206643)<1e-10&&std::abs(pct-price)<1e-10,
       "uncalibrated ATR root N differs from F 1.25 example");
 check(JPWRaizNTimeScale(100.,.40,0,price,pct)==JPW_RAIZN_BAD_N&&price==0&&pct==0,
       "missing N never emits a false zero");
 const datetime ref=StringToTime("2026.09.28 00:00:00");datetime e1=0,e2=0;
 check(JPWHorizonEnds(ref,e1,e2)&&e1==StringToTime("2026.10.05 00:00:00")&&
       e2==StringToTime("2026.10.12 00:00:00"),"rolling 7/14 civil endpoints");
 std::vector<JPWHorizonSession> s;
 for(int d=0;d<14;d++)add(s,ref+d*86400,ref+(d+1)*86400);
 check(JPWHorizonCountSessions(ref,e1,s)==42&&JPWHorizonCountSessions(ref,e2,s)==84,
       "24/7 42/84 emerges from session coverage");
 s.clear();for(int d=0;d<14;d++)if(d%7<5)add(s,ref+d*86400,ref+(d+1)*86400);
 check(JPWHorizonCountSessions(ref,e1,s)==30&&JPWHorizonCountSessions(ref,e2,s)==60,
       "weekday 30/60 emerges from sessions, not defaults");
 s.clear();for(int d=0;d<7;d++)if(d!=2)add(s,ref+d*86400,ref+(d+1)*86400);
 check(JPWHorizonCountSessions(ref,e1,s)==36,
       "a synthetic holiday changes count instead of retaining a universal N");
 s.clear();add(s,StringToTime("2026.09.27 22:00:00"),ref);
 check(JPWHorizonCountSessions(StringToTime("2026.09.27 21:00:00"),ref,s)==1,
       "partial Sunday H4 bar close counted once");
 s.clear();add(s,StringToTime("2026.09.28 23:00:00"),StringToTime("2026.09.29 02:00:00"));
 check(JPWHorizonCountSessions(StringToTime("2026.09.28 22:00:00"),
       StringToTime("2026.09.29 04:00:00"),s)==2,"cross-midnight session");
 long normalized_to=0;
 check(JPWHorizonNormalizeSessionOffsets(23*3600,26*3600,normalized_to)&&
       normalized_to==26*3600,"native 26-hour session end retained");
 check(JPWHorizonNormalizeSessionOffsets(23*3600,2*3600,normalized_to)&&
       normalized_to==26*3600,"wrapped session end normalized");
 check(!JPWHorizonNormalizeSessionOffsets(23*3600,3*86400,normalized_to),
       "out-of-range session refused");
 s.clear();add(s,StringToTime("2026.09.27 08:00:00"),
                 StringToTime("2026.09.27 12:00:00"));
 check(JPWHorizonCountSessions(StringToTime("2026.09.27 07:00:00"),
       StringToTime("2026.09.27 16:00:00"),s)==1,
       "pre-shift quote session creates one H4 close");
 std::vector<datetime> observed={StringToTime("2026.09.20 20:00:00"),
                                  StringToTime("2026.09.27 08:00:00")};
 string mismatch;
 check(JPWHorizonBarsMatchSessions(ref,observed,s,mismatch),
       "observed bars agree with synthetic pre-shift schedule");
 s.clear();add(s,StringToTime("2026.09.27 09:00:00"),
                 StringToTime("2026.09.27 13:00:00"));
 check(JPWHorizonCountSessions(StringToTime("2026.09.27 07:00:00"),
       StringToTime("2026.09.27 16:00:00"),s)==2,
       "one-hour clock shift changes expected H4 closes");
 check(!JPWHorizonBarsMatchSessions(ref,observed,s,mismatch)&&!mismatch.empty(),
       "clock-shift inconsistency is unavailable, never exact");
 s.clear();
 check(!JPWHorizonBarsMatchSessions(ref,observed,s,mismatch),
       "missing schedule is unavailable");
 const string calendar="JPW_H4_CALENDAR_V1\n"
 "symbol=NZDUSD.m\nversion=synthetic\nauthority=SYNTHETIC\napproval_ref=test\n"
 "coverage_start=2026.09.28 00:00:00\ncoverage_end=2026.10.12 00:00:00\n"
 "close=2026.09.29 04:00:00\nclose=2026.10.01 08:00:00\nclose=2026.10.06 04:00:00\n";
 const string hash(64,'A');JPWHorizonResult out;string reason;
 check(JPWHorizonParseApprovedCalendar(calendar,"NZDUSD.m",ref,hash,out,reason)&&
       out.n_1w==2&&out.n_2w==3&&out.status_1w==JPW_HORIZON_EXACT,
       "preverified dated calendar exact counts");
 check(!JPWHorizonParseApprovedCalendar(calendar,"EURUSD",ref,hash,out,reason),
       "calendar refuses another exact symbol");
 check(!JPWHorizonParseApprovedCalendar(calendar,"NZDUSD.m",ref,"",out,reason),
       "calendar text cannot self-approve");
 check(!JPWHorizonParseApprovedCalendar(calendar+"close=2026.10.06 04:00:00\n",
       "NZDUSD.m",ref,hash,out,reason),"duplicate closes refused");
 string short_calendar=calendar;
 auto at=short_calendar.find("coverage_end=2026.10.12 00:00:00");
 short_calendar.replace(at,string("coverage_end=2026.10.12 00:00:00").size(),
                        "coverage_end=2026.10.11 00:00:00");
 check(!JPWHorizonParseApprovedCalendar(short_calendar,"NZDUSD.m",ref,hash,out,reason),
       "calendar without full dated 14-day coverage is unavailable");
 string offgrid=calendar;
 auto at_close=offgrid.find("close=2026.09.29 04:00:00");
 offgrid.replace(at_close,25,"close=2026.09.29 04:01:00");
 check(!JPWHorizonParseApprovedCalendar(offgrid,"NZDUSD.m",ref,hash,out,reason),
       "non-H4 close rejected");
 std::cout<<"HOST_HORIZON: "<<passed<<" PASS / "<<failed<<" FAIL\n";
 std::cout<<"MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN\n";
 return failed?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler")
        return 2
    core = re.sub(r"^\s*#(?:include|property)[^\n]*", "", CORE.read_text(), flags=re.M)
    horizon = HORIZON.read_text()
    horizon = horizon.replace("JPWHorizonSession &sessions[]",
                              "std::vector<JPWHorizonSession> &sessions")
    horizon = horizon.replace("const datetime &bar_opens[]",
                              "const std::vector<datetime> &bar_opens")
    horizon = horizon.replace("string lines[];", "std::vector<string> lines;")
    body = SHIM + "\n#define JPW_RAIZN_HORIZON_SYNTHETIC_ONLY\n" + core + horizon + MAIN
    print(json.dumps({"kind": "HOST_SYNTHETIC_NOT_MQL5", "source_sha256": {
        str(CORE.relative_to(ROOT)): hashlib.sha256(CORE.read_bytes()).hexdigest(),
        str(HORIZON.relative_to(ROOT)): hashlib.sha256(HORIZON.read_bytes()).hexdigest(),
    }}, indent=2), flush=True)
    with tempfile.TemporaryDirectory(prefix="jpw-horizon-") as folder:
        source = Path(folder) / "horizon.cpp"
        binary = Path(folder) / "horizon"
        source.write_text(body)
        for command in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(source), "-o", str(binary)],
                        [str(binary)]):
            result = subprocess.run(command, capture_output=True, text=True, timeout=45)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                print(f"EXIT_CODE: {result.returncode}")
                return result.returncode
    print("EXIT_CODE: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

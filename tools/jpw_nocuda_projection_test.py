#!/usr/bin/env python3
"""Replay the actual NoCuda projection core AND MT5 adapter with synthetic APIs.

The host executes production control flow, calendar corroboration, interpolation,
snapshot revalidation and cache. It is not a native MetaEditor/MT5 receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
INCLUDE = BASE / "Include/JPWealth"
SOURCES = [INCLUDE / "JPW_NoCuda_Core.mqh", INCLUDE / "JPW_NoCuda_Projection_Core.mqh",
           INCLUDE / "JPW_NoCuda_Projection.mqh",
           BASE / "Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5"]

SHIM = r'''
#include <algorithm>
#include <cmath>
#include <ctime>
#include <cstdio>
#include <iostream>
#include <limits>
#include <string>
#include <type_traits>
#include <vector>
using string=std::string;
using datetime=long long;
using uint=unsigned int;
using uchar=unsigned char;
using ENUM_TIMEFRAMES=int;
using ENUM_DAY_OF_WEEK=int;
constexpr int PERIOD_H1=16385,PERIOD_H4=16388,PERIOD_M15=15,PERIOD_W1=32769;
constexpr int SERIES_SYNCHRONIZED=1,ACCOUNT_SERVER=1;
constexpr int WHOLE_ARRAY=-1,CP_UTF8=65001,CRYPT_HASH_SHA256=1;
struct MqlDateTime { int day_of_week=0; };
template<typename T> int ArraySize(const std::vector<T>& values) { return int(values.size()); }
template<typename T> int ArrayResize(std::vector<T>& values,int size) {
  if(size<0) return -1;
  values.resize(size); return size;
}
template<typename A,typename B> auto MathMin(A a,B b) {
  using T=std::common_type_t<A,B>; return std::min(T(a),T(b));
}
template<typename A,typename B> auto MathMax(A a,B b) {
  using T=std::common_type_t<A,B>; return std::max(T(a),T(b));
}
double MathAbs(double value) { return std::abs(value); }
bool MathIsValidNumber(double value) { return std::isfinite(value); }
string IntegerToString(long long value) { return std::to_string(value); }
string StringFormat(const char* format,int value) {
  char buffer[32]; std::snprintf(buffer,sizeof(buffer),format,value); return buffer;
}
int StringToCharArray(const string& value,std::vector<uchar>& out,int,int,int) {
  out.assign(value.begin(),value.end()); out.push_back(0); return int(out.size());
}
// Deterministic stand-in at the native crypto boundary, NOT a SHA-256 proof.
int CryptEncode(int,const std::vector<uchar>& bytes,std::vector<uchar>&,std::vector<uchar>& out) {
  unsigned long long state=1469598103934665603ULL;
  for(auto byte:bytes) state=(state^byte)*1099511628211ULL;
  out.resize(32);
  for(int i=0;i<32;i++) { state^=state>>12; state^=state<<25; state^=state>>27; out[i]=uchar(state>>8); }
  return 32;
}
template<typename... T> void Print(const T&... args) { (std::cout << ... << args) << '\n'; }
bool TimeToStruct(datetime at,MqlDateTime& out) {
  std::time_t value=std::time_t(at); const std::tm* p=std::gmtime(&value);
  if(!p) return false;
  out.day_of_week=p->tm_wday; return true;
}
constexpr datetime MONDAY=1704672000LL; // 2024-01-08, server-civil synthetic Monday.
datetime mock_now=MONDAY+14*86400+12*3600;
std::vector<datetime> actual;
int schedule=0,copy_calls=0,session_calls=0,source_tf=PERIOD_H1,wrong_tf_calls=0;
bool synchronized=true,copy_fail=false,mutate_copy=false,mutate_session=false;
string mock_feed="synthetic-feed-A";
int weekday(datetime at) { MqlDateTime d; TimeToStruct(at,d); return d.day_of_week; }
bool expected_hour(datetime at) {
  const int d=weekday(at),hour=int((at%86400)/3600);
  if(schedule==0) return true;
  if(schedule==1) return d>=1 && d<=5;
  if(schedule==2) return (d>=1 && d<=5) || (d==0 && hour>=22);
  if(schedule==3) return hour>=6 && hour<14;
  if(schedule==4) return hour>=22 || hour<2;
  if(schedule==6) return hour==10 || hour==11;
  return false;
}
bool SymbolInfoSessionQuote(const string& symbol,int day,uint index,datetime& from,datetime& to) {
  ++session_calls;
  if(symbol!="EURUSD.synthetic" || index!=0 || schedule==5) return false;
  if(schedule==1 && (day==0 || day==6)) return false;
  if(schedule==2 && day==6) return false;
  from=0; to=86400;
  if(schedule==2 && day==0) from=22*3600;
  if(schedule==3) { from=6*3600; to=14*3600; }
  if(schedule==4) { from=22*3600; to=2*3600; } // wrapped overnight.
  if(schedule==6) { from=10*3600+1800; to=11*3600+900; }
  if(mutate_session && session_calls>80) from+=3600;
  return true;
}
datetime TimeTradeServer() { return mock_now; }
string AccountInfoString(int) { return mock_feed; }
int PeriodSeconds(int tf) { return tf==PERIOD_H1 ? 3600 : tf==PERIOD_H4 ? 14400 : tf==PERIOD_M15 ? 900 : tf==PERIOD_W1 ? 604800 : 0; }
bool SeriesInfoInteger(const string&,int,int,long& out) { out=synchronized ? 1 : 0; return true; }
datetime iTime(const string& symbol,int tf,int shift) {
  if(tf!=source_tf) { ++wrong_tf_calls; return 0; }
  if(symbol!="EURUSD.synthetic" || PeriodSeconds(tf)==0 || shift<0 || shift>=int(actual.size())) return 0;
  return actual[actual.size()-1-shift];
}
int iBarShift(const string& symbol,int tf,datetime at,bool exact) {
  if(tf!=source_tf) { ++wrong_tf_calls; return -1; }
  if(symbol!="EURUSD.synthetic" || PeriodSeconds(tf)==0) return -1;
  for(int i=int(actual.size())-1;i>=0;--i) {
    if(actual[i]==at) return int(actual.size())-1-i;
    if(!exact && actual[i]<at) return int(actual.size())-1-i;
  }
  return -1;
}
int Bars(const string&,int) { return int(actual.size()); }
int CopyTime(const string&,int tf,int start,int count,std::vector<datetime>& out) {
  ++copy_calls;
  if(tf!=source_tf) { ++wrong_tf_calls; return -1; }
  if(copy_fail || start<0 || count<1 || start+count>int(actual.size())) return -1;
  const int begin=int(actual.size())-start-count;
  out.assign(actual.begin()+begin,actual.begin()+begin+count);
  if(mutate_copy && copy_calls>=2 && !out.empty()) out[0]+=1;
  return count;
}
void reset(int mode,datetime now=MONDAY+14*86400+12*3600,int tf=PERIOD_H1) {
  schedule=mode;mock_now=now; actual.clear();
  synchronized=true;copy_fail=false;mutate_copy=false;mutate_session=false;
  mock_feed="synthetic-feed-A"; copy_calls=0;session_calls=0;
  source_tf=tf; wrong_tf_calls=0;
  const int seconds=PeriodSeconds(tf);
  const datetime first=MONDAY-7*86400;
  const datetime last=(now/seconds)*seconds;
  // Independent fixture oracle: union hourly overlaps into fixed server bins.
  // The production adapter receives only this timeframe's actual openings.
  for(datetime at=first;at<=last;at+=seconds) {
    bool overlap=false;
    for(int offset=0;offset<seconds;offset+=3600) overlap=overlap||expected_hour(at+offset);
    if(overlap) actual.push_back(at);
  }
}
int checks=0,failures=0;
void check(bool ok,const char* name) {
  ++checks; if(!ok) { ++failures; std::cerr << "FAIL: " << name << '\n'; }
}
void near(double a,double b,const char* name) { check(std::abs(a-b)<1e-8*std::max(1.0,std::abs(b)),name); }
'''

CASES = r'''
int main() {
  OnStart();
  const string symbol="EURUSD.synthetic";
  JPWNoCudaGeometry geometry;
  string reason;
  check(JPWNoCudaBuildGeometry(0,100,24,124,12,114,geometry,reason),"host geometry");
  reset(0);
  const datetime anchor=MONDAY+2*86400;
  JPWNoCudaTimePoint point;
  JPWNoCudaDailyResult day;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,anchor+1800,point,reason),
        "adapter historical intrabar uses actual right neighbor");
  near(point.price,102.5,"historical fractional price, not bar-start constant");
  check(!point.estimated && !point.outside_session,"observed point quality");
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,anchor+100,day),
        "adapter normalizes day to server midnight");
  near(day.start_price,102,"historical daily start");
  near(day.mid_price,114,"historical daily midday");
  near(day.end_price,126,"historical daily end at next day");
  near(day.mean_price,114,"adapter continuous midpoint equals mean");
  check(day.day==anchor && !day.estimated,"historical day metadata");
  const string stable_signature=day.source_signature;
  mock_now+=1;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,anchor+100,day) &&
        day.source_signature==stable_signature && stable_signature.size()==64,
        "transient source signature is stable when only generation time changes");
  const datetime holiday_day=anchor+86400;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,holiday_day,day),
        "observed H1 day before source correction");
  const string before_correction=day.source_signature;
  actual.erase(std::find(actual.begin(),actual.end(),holiday_day+10*3600));
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,
        holiday_day+10*3600+1800,point,reason) && !point.estimated && point.outside_session,
        "historical H1 holiday gap is actual source sequence, not current-grade veto");
  near(point.ordinal,33.75,"historical H1 holiday gap interpolates one source ordinal");
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,holiday_day,day) &&
        day.source_signature!=before_correction && !day.estimated,
        "historical day remains available and covered-opening correction changes signature");
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,
        (mock_now/86400)*86400+86400,day),
        "same unexplained gap inside recent 14 days still refuses future calendar");
  reset(0);
  actual.erase(std::remove_if(actual.begin(),actual.end(),[=](datetime at) {
    return at>=holiday_day && at<holiday_day+86400;
  }),actual.end());
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,holiday_day,day) &&
        day.no_session && !day.estimated && !day.valid,
        "fully observed holiday without source bars has no daily range");
  reset(0);
  const datetime old_anchor=MONDAY-6*86400;
  actual.erase(std::find(actual.begin(),actual.end(),MONDAY-3*86400+12*3600));
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,old_anchor,geometry,1,
        (mock_now/86400)*86400+86400,day) && day.estimated,
        "old holiday outside corroboration window does not veto coherent future grade");
  reset(0);
  const datetime newest=actual.back();
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,newest+1800,point,reason) &&
        point.estimated,"current intrabar needs projected right boundary and is Estimated");
  const double first_price=point.price;
  const int first_copies=copy_calls;
  mock_now+=1;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,newest+1801,point,reason),
        "current bucket can reuse five-second validated read cache");
  check(copy_calls==first_copies,"short cache avoids complete CopyTime every tick");
  near(point.price-first_price,1.0/3600.0,"cache still recomputes fractional price");
  mock_now+=6;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,newest+1802,point,reason) &&
        copy_calls>first_copies,"expired read cache forces full revalidation");
  const int before_feed=copy_calls;
  mock_feed="synthetic-feed-B";
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,newest+1803,point,reason) &&
        copy_calls>before_feed,"feed context change cannot reuse old cache");
  reset(0);
  mock_now+=2*3600;
  g_jpw_nocuda_projection_cache_created=0;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,
        (mock_now/86400)*86400+86400,day) && !day.valid,
        "stalled feed missing already-elapsed current-day bins cannot project them");
  reset(1,MONDAY+20*86400+12*3600); // Sunday: latest observed H1 is Friday.
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,
        (mock_now/86400)*86400+86400,day) && day.estimated,
        "weekend absence of expected bins permits Estimated Monday projection");
  reset(6,MONDAY+14*86400+10*3600+900);
  actual.pop_back(); // today's 10h bin cannot exist before the 10:30 session starts.
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor+10*3600,geometry,1,
        (mock_now/86400)*86400+86400,day) && day.estimated,
        "not-yet-open partial session does not create a missing elapsed bin");
  mock_now+=1800;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor+10*3600,geometry,1,
        (mock_now/86400)*86400+86400,day),
        "missing partial-session bin after known opening refuses projection");
  reset(0,MONDAY+14*86400);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,
        (mock_now/86400)*86400+86400,day),
        "exact midnight does not demand a nonempty current-day corroboration interval");
  reset(0,MONDAY+14*86400+12*3600+3598);
  g_jpw_nocuda_projection_cache_created=0;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,
        mock_now-1,point,reason),"cache fixture accepted before hour boundary");
  mock_now+=4;
  check(!JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,
        mock_now-3,point,reason),
        "short cache cannot fill a newly elapsed missing H1 bin at hour boundary");
  reset(0);
  g_jpw_nocuda_projection_cache_created=0;
  const datetime today=(mock_now/86400)*86400;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+30*86400,day) &&
        day.estimated,"day +30 includes its 24h endpoint and bracket margin");
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+31*86400,day) &&
        !day.valid,"day +31 refused, no budget clamp");
  source_tf=PERIOD_M15;
  check(!JPWNoCudaPriceAtTime(symbol,PERIOD_M15,anchor,geometry,1,mock_now+86400,point,reason) &&
        reason=="Projecao futura disponivel somente para fontes H1 e H4",
        "future source other than approved H1/H4 is explicitly unsupported");
  source_tf=PERIOD_H1;
  check(!JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,MONDAY-20*86400,point,reason),
        "missing earlier history cannot become an old bar fallback");
  reset(1);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+4*86400,day) &&
        day.estimated,"Friday 24h has Monday bracket across weekend");
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+30*86400,day),
        "weekday target +30 stays within target budget");
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+5*86400,day) &&
        day.no_session && !day.valid && day.estimated,
        "future Saturday has no daily range and remains Estimated");
  const auto remove=std::find(actual.begin(),actual.end(),today-3*86400+12*3600);
  check(remove!=actual.end(),"missing-bar test fixture selects expected weekday slot");
  actual.erase(remove);
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day),
        "holiday/unexplained missing expected H1 bar refuses projection");
  reset(3);
  const datetime partial_anchor=MONDAY+2*86400+6*3600;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,partial_anchor,geometry,1,today+86400,day),
        "partial-session daily interpolation");
  check(day.estimated && day.start_outside && !day.mid_outside && day.end_outside,
        "partial-session 00/12/24 outside flags are separate");
  check(std::abs(day.mid_price-day.mean_price)>0.01,
        "partial-session midpoint is not arithmetic endpoint mean");
  reset(4);
  const datetime overnight_anchor=MONDAY+2*86400;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,overnight_anchor,geometry,1,today+86400,day) &&
        !day.no_session && !day.start_outside && !day.end_outside && day.mid_outside,
        "wrapped overnight session carries through midnight correctly");
  reset(2);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+6*86400,day) &&
        day.estimated && day.start_outside && day.mid_outside,
        "partial Sunday is a session day with explicit outside points");
  reset(0);
  copy_fail=true;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day) && !day.valid,
        "CopyTime failure produces unavailable, not zero range");
  reset(0);
  mutate_copy=true;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day),
        "changed history during reread refuses result");
  reset(0);
  mutate_session=true;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day),
        "changed session metadata during reread refuses result");
  reset(5);
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day),
        "missing session grade refuses projection");
  reset(0);
  synchronized=false;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H1,anchor,geometry,1,today+86400,day),
        "unsynchronized source refuses result");
  reset(1);
  // Another timeframe preserves actual candle ordinals across a weekend.
  source_tf=PERIOD_H4;
  actual={MONDAY+4*86400+12*3600,MONDAY+4*86400+16*3600,
          MONDAY+7*86400,MONDAY+7*86400+4*3600};
  mock_now=MONDAY+7*86400+4*3600+1;
  const datetime h4_anchor=actual[0];
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H4,h4_anchor,geometry,1,
        MONDAY+5*86400,point,reason) && !point.estimated && point.outside_session,
        "historical H4 weekend interpolates observed source sequence, not civil hours");
  near(point.ordinal,1.0+8.0/56.0,"historical weekend uses one ordinal between neighbor openings");
  reset(0,MONDAY+14*86400+12*3600,PERIOD_H4);
  JPWNoCudaProjectionTimeline timeline;
  check(JPWNoCudaProjectionLoadTimeline(symbol,PERIOD_H4,anchor,today+86400,
        today+2*86400,timeline,reason),"actual H4 timeline supplies future daily endpoints");
  check(wrong_tf_calls==0,"H4 corroboration never reads an H1 series");
  check(timeline.source.find("H4:")==0 && timeline.observed_count==14*6+4,
        "H4 provenance and observed count come from six actual bars per day");
  bool aligned=true;
  for(const auto opened:timeline.opens) aligned=aligned && opened%14400==0;
  check(aligned,"all projected H4 vertices use server 00/04/08/12/16/20");
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day) && day.estimated,
        "H4 future day is Estimated even when sequence matches");
  near(day.end_price-day.start_price,6,"full H4 day advances six source ordinals");
  near(day.mid_price,day.mean_price,"continuous H4 12h equals endpoint mean");
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+30*86400,day),
        "H4 day +30 permitted with 24h delimiter");
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+31*86400,day),
        "H4 day +31 refused");
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H4,anchor,geometry,1,anchor+2*3600,point,reason),
        "H4 historical fractional query uses actual H4 neighbors");
  near(point.price,102.5,"half H4 candle means half ordinal, not two H1 ordinals");
  reset(0,today+12*3600+600,PERIOD_H4);
  g_jpw_nocuda_projection_cache_created=0;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H4,anchor,geometry,1,mock_now,point,reason),
        "current H4 bucket has explicit projected right delimiter");
  const int h4_cached_copy_calls=copy_calls;
  mock_now+=2;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H4,anchor,geometry,1,mock_now,point,reason) &&
        copy_calls==h4_cached_copy_calls && point.estimated,"H4 short cache remains Estimated");
  source_tf=PERIOD_H1;
  const int old_cache_copy_calls=copy_calls;
  check(!JPWNoCudaPriceAtTime(symbol,PERIOD_H1,anchor,geometry,1,mock_now,point,reason) &&
        copy_calls>old_cache_copy_calls,"cache cannot reuse H4 sequence under H1 key");
  reset(0,today+16*3600-2,PERIOD_H4);
  g_jpw_nocuda_projection_cache_created=0;
  check(JPWNoCudaPriceAtTime(symbol,PERIOD_H4,anchor,geometry,1,mock_now,point,reason),
        "H4 cache fixture accepted before next bucket opening");
  mock_now+=4;
  check(!JPWNoCudaPriceAtTime(symbol,PERIOD_H4,anchor,geometry,1,mock_now-3,point,reason),
        "H4 cache refuses newly elapsed missing 16h bar even within five seconds");
  reset(3,today+12*3600,PERIOD_H4);
  const datetime h4_partial_anchor=anchor+4*3600;
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,h4_partial_anchor,geometry,1,today+86400,day) &&
        day.estimated && day.start_outside && !day.mid_outside && day.end_outside,
        "partial H4 daily query identifies outside-session points");
  near(day.end_price-day.start_price,3,"06-14 session gives three H4 bins, not H1 eight divided by four");
  check(std::abs(day.mid_price-day.mean_price)>0.01,"partial H4 midday differs from endpoint mean");
  reset(4,today+12*3600,PERIOD_H4);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day) &&
        !day.start_outside && day.mid_outside && !day.end_outside,
        "H4 overnight sessions contribute 20h and 00h bins");
  near(day.end_price-day.start_price,2,"H4 wrapped session has two distinct bins");
  reset(2,today+12*3600,PERIOD_H4);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+6*86400,day) &&
        day.estimated && day.start_outside && day.mid_outside,
        "Sunday partial session contributes H4 20h bin despite first quote 22h");
  reset(1,today+12*3600,PERIOD_H4);
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+4*86400,day),
        "H4 Friday endpoint can use Monday delimiter across closed weekend");
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+5*86400,day) &&
        day.no_session && day.estimated,"H4 fully closed day has no range");
  reset(6,today+10*3600+900,PERIOD_H4);
  actual.pop_back(); // 08h bin is not yet observed before the 10:30 first quote.
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor+8*3600,geometry,1,today+86400,day),
        "partial H4 bucket can remain future before its first possible quote");
  mock_now=today+10*3600+1800;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor+8*3600,geometry,1,today+86400,day),
        "missing H4 bucket after partial-session opening refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  actual.erase(std::find(actual.begin(),actual.end(),today-3*86400+8*3600));
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "missing H4 observed bin in closed validation window refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  actual.insert(std::lower_bound(actual.begin(),actual.end(),today-3*86400+6*3600),
        today-3*86400+6*3600);
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "extra H4 observed bin refuses projection even with valid endpoints");
  reset(0,today+12*3600,PERIOD_H4);
  *std::find(actual.begin(),actual.end(),today-3*86400+8*3600)+=3600;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "same count with H4 hour misalignment refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  actual.back()+=3600;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "latest H4 bar not aligned to server grid refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  actual.erase(actual.begin(),std::lower_bound(actual.begin(),actual.end(),today-13*86400));
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,today-12*86400,geometry,1,today+86400,day),
        "H4 insufficient 14-day coverage refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  mutate_copy=true;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "H4 changed actual opening during reread refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  mutate_session=true;
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "H4 changing session metadata refuses projection");
  reset(0,today+12*3600,PERIOD_H4);
  const datetime older_anchor=MONDAY-7*86400;
  actual.erase(std::find(actual.begin(),actual.end(),MONDAY-3*86400+8*3600));
  check(JPWNoCudaProjectDay(symbol,PERIOD_H4,older_anchor,geometry,1,today+86400,day),
        "old H4 holiday outside last fourteen closed days preserves actual ordinal and allows projection");
  reset(5,today+12*3600,PERIOD_H4);
  // A real observed H4 sequence may exist when weekly metadata is unavailable.
  for(datetime opened=MONDAY-7*86400;opened<=mock_now;opened+=14400) actual.push_back(opened);
  check(!JPWNoCudaProjectDay(symbol,PERIOD_H4,anchor,geometry,1,today+86400,day),
        "H4 cannot invent a future calendar from history alone");
  for(int tf:{PERIOD_H1,PERIOD_H4}) {
    reset(3,today+12*3600,tf);
    const datetime boundary=today-14*86400;
    actual.erase(actual.begin(),std::lower_bound(actual.begin(),actual.end(),boundary));
    const datetime first_anchor=actual.front();
    check(first_anchor>boundary && JPWNoCudaProjectDay(symbol,tf,first_anchor,geometry,1,today+86400,day),
          "fourteen complete partial-session days need no artificial pre-midnight bar");
    actual.erase(actual.begin());
    check(!JPWNoCudaProjectDay(symbol,tf,actual.front(),geometry,1,today+86400,day),
          "missing first expected bucket remains refused after partial-session coverage fix");
  }
  reset(0,today+12*3600,PERIOD_W1);
  actual={MONDAY,MONDAY+7*86400,MONDAY+14*86400};
  check(JPWNoCudaProjectDay(symbol,PERIOD_W1,MONDAY,geometry,1,MONDAY+2*86400,day)&&
        day.valid&&!day.no_session&&!day.estimated,
        "covered historical weekday between W1 openings is geometry, not a fabricated closed session");
  check(day.reason.find("sessao diaria nao inferida")!=string::npos,
        "wide historical timeframe explicitly leaves daily market session unconfirmed");
  std::cout << "HOST_NOCUDA_PROJECTION: " << checks << " checks; " << failures << " failures\n";
  std::cout << "NATIVE_METAEDITOR: NOT_RUN; NATIVE_MT5: NOT_RUN\n";
  std::cout << "DIGEST_BOUNDARY: DETERMINISTIC_SYNTHETIC_CRYPTO_NOT_SHA256_PROOF\n";
  return failures+g_nocuda_projection_fail ? 1 : 0;
}
'''


def translated(path: Path) -> str:
    text = path.read_text()
    text = re.sub(r"^#include\s+<JPWealth/[^>]+>\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#property.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\bconst\s+(\w+)\s+&(\w+)\[\]", r"const std::vector<\1>& \2", text)
    text = re.sub(r"\b(\w+)\s+&(\w+)\[\]", r"std::vector<\1>& \2", text)
    text = re.sub(r"\b(\w+)\s+(\w+)\[\]", r"std::vector<\1> \2", text)
    return text


def run(evidence: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: C++ compiler unavailable; native NOT_RUN")
        return 2
    if evidence:
        evidence.mkdir(parents=True, exist_ok=False)
        (evidence / "identity.json").write_text(json.dumps({
            "kind": "ACTUAL_MQL_SOURCE_HOST_REPLAY_NOT_NATIVE",
            "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in SOURCES},
            "scope": "pure script and actual terminal adapter against synthetic APIs",
            "native_metaeditor": "NOT_RUN", "native_mt5": "NOT_RUN",
        }, indent=2) + "\n")
    adapter = SOURCES[2].read_text()
    forbidden = ("FileOpen", "Database", "GlobalVariableSet", "OrderSend", "AccountInfoDouble")
    for token in forbidden:
        if token in adapter:
            raise AssertionError(f"projection adapter crosses read-only boundary: {token}")
    with tempfile.TemporaryDirectory(prefix="jpw-nocuda-projection-") as directory:
        source, binary = Path(directory) / "test.cpp", Path(directory) / "test"
        source.write_text(SHIM + "\n" + "\n".join(translated(p) for p in SOURCES) + CASES)
        command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)]
        compilation = subprocess.run(command, text=True, capture_output=True, timeout=60, check=False)
        print(compilation.stdout, end="")
        print(compilation.stderr, end="")
        if evidence:
            (evidence / "compile-command.json").write_text(json.dumps(command) + "\n")
            (evidence / "compile-stdout.txt").write_text(compilation.stdout)
            (evidence / "compile-stderr.txt").write_text(compilation.stderr)
        if compilation.returncode:
            print("HOST_NOCUDA_PROJECTION: PRODUCT_FAIL; native NOT_RUN")
            return compilation.returncode
        result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=60, check=False)
        print(result.stdout, end="")
        print(result.stderr, end="")
        if evidence:
            (evidence / "run-stdout.txt").write_text(result.stdout)
            (evidence / "run-stderr.txt").write_text(result.stderr)
            (evidence / "result.json").write_text(json.dumps({
                "classification": "PASS" if result.returncode == 0 else "PRODUCT_FAIL",
                "exit_code": result.returncode, "native_metaeditor": "NOT_RUN", "native_mt5": "NOT_RUN",
            }, indent=2) + "\n")
        return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    raise SystemExit(run(parser.parse_args().evidence_dir))

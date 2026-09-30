#property copyright "JP Wealth"
#property version   "1.60"
#property description "Testes sinteticos da escala temporal H4 1W/2W. Sem conta ou ordem."

#define JPW_RAIZN_HORIZON_SYNTHETIC_ONLY
#include <JPWealth/JPW_Alavancagem_RaizN_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh>

int g_horizon_pass=0,g_horizon_fail=0;
void JPWHorizonAssert(const bool yes,const string label)
  {
   if(yes) g_horizon_pass++;
   else { g_horizon_fail++; Print("FAIL: ",label); }
  }

void JPWHorizonAppend(JPWHorizonSession &sessions[],const datetime from,
                      const datetime to)
  {
   const int count=ArraySize(sessions);
   ArrayResize(sessions,count+1);
   sessions[count].from_time=from;
   sessions[count].to_time=to;
  }

void JPWHorizonTestMath()
  {
   double price=0.0,percent=0.0;
   JPWHorizonAssert(JPWRaizNTimeScale(100.0,0.40,30,price,percent)==JPW_RAIZN_OK,
                    "uncalibrated scale calculates without F");
   JPWHorizonAssert(MathAbs(price-2.1908902300206643)<1e-9 &&
                    MathAbs(percent-2.1908902300206643)<1e-9,
                    "ATR times root 30 is distinct from illustrative F 1.25");
   JPWHorizonAssert(JPWRaizNTimeScale(0.0,0.40,30,price,percent)==JPW_RAIZN_BAD_P0 &&
                    price==0.0 && percent==0.0,"invalid P0 cannot make zero display");
   JPWHorizonAssert(JPWRaizNTimeScale(100.0,0.0,30,price,percent)==JPW_RAIZN_BAD_ATR,
                    "missing ATR refused");
   JPWHorizonAssert(JPWRaizNTimeScale(100.0,0.40,0,price,percent)==JPW_RAIZN_BAD_N,
                    "missing horizon refused");
  }

void JPWHorizonTestSessions()
  {
   const datetime reference=D'2026.09.28 00:00:00'; // Monday
   datetime one=0,two=0;
   JPWHorizonAssert(JPWHorizonEnds(reference,one,two) &&
                    one==D'2026.10.05 00:00:00' && two==D'2026.10.12 00:00:00',
                    "rolling server-civil 7/14 day endpoints");
   JPWHorizonSession sessions[];
   for(int day=0;day<14;day++)
     JPWHorizonAppend(sessions,(datetime)((long)reference+day*86400),
                      (datetime)((long)reference+(day+1)*86400));
   JPWHorizonAssert(JPWHorizonCountSessions(reference,one,sessions)==42 &&
                    JPWHorizonCountSessions(reference,two,sessions)==84,
                    "24/7 market counts actual expected H4 closes");
   ArrayResize(sessions,0);
   for(int day=0;day<14;day++)
      if(day%7<5)
         JPWHorizonAppend(sessions,(datetime)((long)reference+day*86400),
                          (datetime)((long)reference+(day+1)*86400));
   JPWHorizonAssert(JPWHorizonCountSessions(reference,one,sessions)==30 &&
                    JPWHorizonCountSessions(reference,two,sessions)==60,
                    "weekday-only is 30/60 because of sessions, not a hard-coded constant");
   ArrayResize(sessions,0);
   JPWHorizonAppend(sessions,D'2026.09.27 22:00:00',D'2026.09.28 00:00:00');
   JPWHorizonAssert(JPWHorizonCountSessions(D'2026.09.27 21:00:00',
                    D'2026.09.28 00:00:00',sessions)==1,
                    "partial Sunday quote session creates one H4 close");
   ArrayResize(sessions,0);
   JPWHorizonAppend(sessions,D'2026.09.28 23:00:00',D'2026.09.29 02:00:00');
   JPWHorizonAssert(JPWHorizonCountSessions(D'2026.09.28 22:00:00',
                    D'2026.09.29 04:00:00',sessions)==2,
                    "cross-midnight session overlaps two H4 bars");
   long normalized_to=0;
   JPWHorizonAssert(JPWHorizonNormalizeSessionOffsets(23*3600,26*3600,
                    normalized_to) && normalized_to==26*3600,
                    "native next-day quote-session end retains 26-hour offset");
   JPWHorizonAssert(JPWHorizonNormalizeSessionOffsets(23*3600,2*3600,
                    normalized_to) && normalized_to==26*3600,
                    "wrapped quote-session end normalizes to same interval");
   JPWHorizonAssert(!JPWHorizonNormalizeSessionOffsets(23*3600,3*86400,
                    normalized_to),"out-of-range quote session refused");
   ArrayResize(sessions,0);
   for(int day=0;day<7;day++) if(day!=2)
      JPWHorizonAppend(sessions,(datetime)((long)reference+day*86400),
                       (datetime)((long)reference+(day+1)*86400));
   JPWHorizonAssert(JPWHorizonCountSessions(reference,one,sessions)==36,
                    "dated holiday fixture removes six closes");
   // A one-hour server-session shift may change the H4-close count. Without
   // dated approval it cannot be promoted to an exact future calendar.
   ArrayResize(sessions,0);
   JPWHorizonAppend(sessions,D'2026.09.27 08:00:00',D'2026.09.27 12:00:00');
   JPWHorizonAssert(JPWHorizonCountSessions(D'2026.09.27 07:00:00',
                    D'2026.09.27 16:00:00',sessions)==1,
                    "pre-shift quote session overlaps one H4 close");
   string mismatch="";
   datetime observed[2]={D'2026.09.20 20:00:00',D'2026.09.27 08:00:00'};
   JPWHorizonAssert(JPWHorizonBarsMatchSessions(reference,observed,sessions,mismatch),
                    "observed bar agrees with unshifted synthetic schedule");
   ArrayResize(sessions,0);
   JPWHorizonAppend(sessions,D'2026.09.27 09:00:00',D'2026.09.27 13:00:00');
   JPWHorizonAssert(JPWHorizonCountSessions(D'2026.09.27 07:00:00',
                    D'2026.09.27 16:00:00',sessions)==2,
                    "one-hour clock shift changes expected H4 closes");
   JPWHorizonAssert(!JPWHorizonBarsMatchSessions(reference,observed,sessions,mismatch) &&
                    mismatch!="","shifted schedule inconsistent with observed bars is unavailable");
   ArrayResize(sessions,0);
   JPWHorizonAssert(!JPWHorizonBarsMatchSessions(reference,observed,sessions,mismatch),
                    "missing quote-session schedule is unavailable");
  }

void JPWHorizonTestDatedApproval()
  {
   const datetime reference=D'2026.09.28 00:00:00';
   const string calendar=
      "JPW_H4_CALENDAR_V1\n"
      "symbol=NZDUSD.m\nversion=synthetic-1\nauthority=SYNTHETIC_TEST\n"
      "approval_ref=synthetic-fixture\n"
      "coverage_start=2026.09.28 00:00:00\n"
      "coverage_end=2026.10.12 00:00:00\n"
      "close=2026.09.29 04:00:00\nclose=2026.10.01 08:00:00\n"
      "close=2026.10.06 04:00:00\n";
   const string digest="0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF";
   JPWHorizonResult result; string reason="";
   JPWHorizonAssert(JPWHorizonParseApprovedCalendar(calendar,"NZDUSD.m",reference,
                    digest,result,reason) && result.n_1w==2 && result.n_2w==3 &&
                    result.status_1w==JPW_HORIZON_EXACT &&
                    result.source_sha256==digest,
                    "pre-verified dated calendar counts closures and keeps provenance");
   JPWHorizonAssert(!JPWHorizonParseApprovedCalendar(calendar,"EURUSD",reference,
                    digest,result,reason),"exact symbol required");
   JPWHorizonAssert(!JPWHorizonParseApprovedCalendar(calendar,"NZDUSD.m",reference,
                    "",result,reason),"self-declared authority cannot replace external hash");
   string duplicated=calendar+"close=2026.10.06 04:00:00\n";
   JPWHorizonAssert(!JPWHorizonParseApprovedCalendar(duplicated,"NZDUSD.m",reference,
                    digest,result,reason),"unsorted or repeated closes refused");
   string short_coverage=calendar;
   StringReplace(short_coverage,"coverage_end=2026.10.12 00:00:00",
                 "coverage_end=2026.10.11 00:00:00");
   JPWHorizonAssert(!JPWHorizonParseApprovedCalendar(short_coverage,"NZDUSD.m",reference,
                    digest,result,reason),"missing fourteen-day coverage refused");
  }

void OnStart()
  {
   JPWHorizonTestMath();
   JPWHorizonTestSessions();
   JPWHorizonTestDatedApproval();
   PrintFormat("JPW_Alavancagem_RaizN_Horizon_Tests %s: %d asserts",
               (g_horizon_fail==0 ? "PASS" : "FAIL"),g_horizon_pass+g_horizon_fail);
  }

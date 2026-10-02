#property copyright "JP Wealth"
#property version "1.00"
#property description "Projecao NoCuda sintetica; nao le conta nem grava estudos."

#include <JPWealth/JPW_NoCuda_Projection_Core.mqh>

int g_nocuda_projection_pass=0;
int g_nocuda_projection_fail=0;

void JPWNoCudaProjectionAssert(const bool condition,const string label)
  {
   if(condition) g_nocuda_projection_pass++;
   else { g_nocuda_projection_fail++; Print("FAIL: ",label); }
  }

void JPWNoCudaProjectionNear(const double actual,const double expected,const string label)
  {
   JPWNoCudaProjectionAssert(MathIsValidNumber(actual) &&
      MathAbs(actual-expected)<=1e-10*MathMax(1.0,MathAbs(expected)),label);
  }

void JPWNoCudaProjectionTestContinuousAndDescending()
  {
   const datetime day=(datetime)172800;
   datetime opens[];
   ArrayResize(opens,25);
   for(int i=0;i<25;i++) opens[i]=(datetime)((long)day+i*3600);
   JPWNoCudaProjectionSession sessions[];
   ArrayResize(sessions,1);
   sessions[0].from_time=day; sessions[0].to_time=(datetime)((long)day+2*86400);
   JPWNoCudaGeometry geometry;
   string reason="";
   JPWNoCudaProjectionAssert(JPWNoCudaBuildGeometry(0,100,24,124,12,114,geometry,reason),
                            "continuous fixture builds same production geometry");
   JPWNoCudaTimePoint a,b,c;
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,25,day,geometry,1,
      day,3600,sessions,true,a,reason),"00h observed point");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,25,day,geometry,1,
      (datetime)((long)day+43200),3600,sessions,true,b,reason),"12h observed point");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,25,day,geometry,1,
      (datetime)((long)day+86400),3600,sessions,true,c,reason),"24h next-day point");
   JPWNoCudaDailyResult daily;
   JPWNoCudaProjectionAssert(JPWNoCudaDailyFromPoints(day,day+1,a,b,c,false,
      "synthetic observed",daily) && daily.valid && !daily.estimated,"continuous daily result");
   JPWNoCudaProjectionNear(daily.start_price,102,"continuous 00h");
   JPWNoCudaProjectionNear(daily.mid_price,114,"continuous 12h");
   JPWNoCudaProjectionNear(daily.end_price,126,"continuous 24h");
   JPWNoCudaProjectionNear(daily.mean_price,daily.mid_price,"continuous 12h equals endpoints mean");
   JPWNoCudaProjectionNear(daily.min_price,102,"ascending range min");
   JPWNoCudaProjectionNear(daily.max_price,126,"ascending range max");
   JPWNoCudaProjectionAssert(JPWNoCudaBuildGeometry(0,100,24,52,12,78,geometry,reason),
                            "descending fixture");
   JPWNoCudaProjectionResolve(opens,25,day,geometry,1,day,3600,sessions,true,a,reason);
   JPWNoCudaProjectionResolve(opens,25,day,geometry,1,day+43200,3600,sessions,true,b,reason);
   JPWNoCudaProjectionResolve(opens,25,day,geometry,1,day+86400,3600,sessions,true,c,reason);
   JPWNoCudaProjectionAssert(JPWNoCudaDailyFromPoints(day,day+1,a,b,c,false,"synthetic",daily),
                            "descending daily");
   JPWNoCudaProjectionNear(daily.start_price,102,"descending start");
   JPWNoCudaProjectionNear(daily.end_price,54,"descending end at next midnight");
   JPWNoCudaProjectionNear(daily.min_price,54,"descending range uses smaller endpoint");
   JPWNoCudaProjectionNear(daily.max_price,102,"descending range uses larger endpoint");
  }

void JPWNoCudaProjectionTestPartialAndLimits()
  {
   const datetime day=(datetime)172800;
   datetime opens[];
   ArrayResize(opens,4);
   opens[0]=day-3600; opens[1]=day+6*3600;
   opens[2]=day+12*3600; opens[3]=day+86400;
   JPWNoCudaProjectionSession sessions[];
   ArrayResize(sessions,1);
   sessions[0].from_time=day+6*3600; sessions[0].to_time=day+14*3600;
   JPWNoCudaGeometry geometry;
   string reason="";
   JPWNoCudaProjectionAssert(JPWNoCudaBuildGeometry(0,100,3,130,2,121,geometry,reason),
                            "partial session fixture");
   JPWNoCudaTimePoint a,b,c;
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,3,opens[0],geometry,1,
      day,3600,sessions,true,a,reason) && a.outside_session && !a.estimated,
      "00h interpolates across known observed closed gap");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,3,opens[0],geometry,1,
      day+43200,3600,sessions,true,b,reason) && !b.outside_session,"12h inside session");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionResolve(opens,3,opens[0],geometry,1,
      day+86400,3600,sessions,true,c,reason) && c.estimated && c.outside_session,
      "24h projected opening is Estimated");
   JPWNoCudaDailyResult daily;
   JPWNoCudaProjectionAssert(JPWNoCudaDailyFromPoints(day,day+1,a,b,c,false,"synthetic",daily),
                            "partial daily result");
   JPWNoCudaProjectionNear(daily.start_price,101+10.0/7.0,"partial start uses fractional source ordinal");
   JPWNoCudaProjectionNear(daily.mid_price,121,"partial midday");
   JPWNoCudaProjectionNear(daily.end_price,131,"partial end");
   JPWNoCudaProjectionAssert(MathAbs(daily.mid_price-daily.mean_price)>1.0,
                            "partial 12h is NOT endpoint mean");
   JPWNoCudaProjectionAssert(daily.estimated && daily.start_outside && daily.end_outside,
                            "partial flags retained");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionResolve(opens,3,opens[0],geometry,1,
      day+86401,3600,sessions,true,a,reason) && !a.valid && a.price==0,
      "no last-bar fallback after final bracket");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionResolve(opens,3,opens[0],geometry,1,
      day-7200,3600,sessions,true,a,reason),"no previous-history fallback");
   JPWNoCudaProjectionAssert(!JPWNoCudaDailyFromPoints(day,day+1,b,b,c,true,"synthetic",daily) &&
      daily.no_session && !daily.valid && daily.min_price==0,"closed day has no artificial range");
   double ordinal=0;
   JPWNoCudaProjectionAssert(JPWNoCudaSourceOpeningOrdinal(0,4,6,ordinal),
                            "earlier observed bar may evaluate before origin");
   JPWNoCudaProjectionNear(ordinal,-2,"negative evaluation ordinal preserved");
   JPWNoCudaProjectionAssert(!JPWNoCudaSourceOpeningOrdinal(0,-1,2,ordinal),
                            "invalid shift refused");
   opens[2]=opens[1];
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionValidateOpens(opens,3,reason),
                            "duplicate source opening refused");
  }

void JPWNoCudaProjectionTestSessions()
  {
   const datetime day=(datetime)172800;
   JPWNoCudaProjectionSession sessions[];
   ArrayResize(sessions,2);
   sessions[0].from_time=day+10*3600+1800;
   sessions[0].to_time=day+11*3600+900;
   sessions[1]=sessions[0]; // overlapping sessions must not duplicate bins.
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionExpectedH1(sessions,day+10*3600),
                            "partial first hour creates one expected H1 bin");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionExpectedH1(sessions,day+11*3600),
                            "partial second hour creates expected H1 bin");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionExpectedH1(sessions,day+12*3600),
                            "outside partial session does not invent a bin");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionExpectedH1By(sessions,day+10*3600,
      day+10*3600+900),"partial session first bin is not already known before opening");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionExpectedH1By(sessions,day+10*3600,
      day+10*3600+1800),"partial session first bin becomes expected at its opening");
   datetime opens[];
   ArrayResize(opens,2); opens[0]=day+10*3600; opens[1]=day+11*3600;
   string reason="";
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionCorroborateH1(opens,day,day+86400,sessions,reason),
                            "exact observed sequence corroborates partial sessions");
   opens[1]=day+12*3600;
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionCorroborateH1(opens,day,day+86400,sessions,reason),
                            "same count with shifted bar is not calendar corroboration");
   sessions[0].from_time=day-2*3600; sessions[0].to_time=day+2*3600;
   ArrayResize(sessions,1);
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionSessionOverlaps(sessions,day,day+86400),
                            "overnight carry prevents closed-day misclassification");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionSessionContains(sessions,day),
                            "midnight belongs to overnight quote session");
  }

void JPWNoCudaProjectionTestH4Buckets()
  {
   const datetime day=(datetime)172800;
   JPWNoCudaProjectionSession sessions[];
   ArrayResize(sessions,2);
   sessions[0].from_time=day+6*3600; sessions[0].to_time=day+14*3600;
   sessions[1]=sessions[0];
   datetime opens[];
   ArrayResize(opens,3);
   opens[0]=day+4*3600; opens[1]=day+8*3600; opens[2]=day+12*3600;
   string reason="";
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionExpectedH4(sessions,opens[0]),
      "H4 partial 06h session overlaps server 04h bin");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionExpectedH4(sessions,opens[2]),
      "H4 partial end overlaps server 12h bin");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionExpectedH4(sessions,day) &&
      !JPWNoCudaProjectionExpectedH4(sessions,day+16*3600),"H4 does not invent outside bins");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionExpectedH4(sessions,day+6*3600),
      "H4 refuses session-start anchor not aligned with server 00/04/08/12/16/20");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionExpectedH4By(sessions,opens[0],day+5*3600) &&
      JPWNoCudaProjectionExpectedH4By(sessions,opens[0],day+6*3600),
      "H4 current partial bin becomes expected only at first possible quote");
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 exact partial sequence is three bins, not eight H1 bins divided by four");
   opens[1]=day+9*3600;
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 count-preserving misalignment refused");
   opens[1]=day+8*3600;
   ArrayResize(opens,2);
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 missing expected bin refused");
   ArrayResize(opens,4); opens[2]=day+12*3600; opens[3]=day+16*3600;
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 extra observed bin refused");
   ArrayResize(sessions,1);
   sessions[0].from_time=day; sessions[0].to_time=day+86400;
   ArrayResize(opens,6);
   for(int i=0;i<6;i++) opens[i]=day+i*14400;
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 full day has six exact server buckets");
   JPWNoCudaProjectionAssert(!JPWNoCudaProjectionCorroborateBuckets(opens,day,day+86400,
      sessions,7200,reason),"unapproved future period cannot enter generic bucket branch");
   sessions[0].from_time=day-2*3600; sessions[0].to_time=day+2*3600;
   ArrayResize(opens,1); opens[0]=day;
   JPWNoCudaProjectionAssert(JPWNoCudaProjectionCorroborateH4(opens,day,day+86400,sessions,reason),
      "H4 overnight carry contributes midnight bucket exactly once");
  }

void OnStart()
  {
   JPWNoCudaProjectionTestContinuousAndDescending();
   JPWNoCudaProjectionTestPartialAndLimits();
   JPWNoCudaProjectionTestSessions();
   JPWNoCudaProjectionTestH4Buckets();
   Print("JPW_NoCuda_Projection_Tests: ",g_nocuda_projection_pass,
         " PASS / ",g_nocuda_projection_fail," FAIL");
  }

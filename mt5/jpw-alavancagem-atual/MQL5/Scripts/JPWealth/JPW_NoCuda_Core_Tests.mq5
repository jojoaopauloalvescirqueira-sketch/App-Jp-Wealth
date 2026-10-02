#property copyright "JP Wealth"
#property version   "1.00"
#property description "Testes sinteticos da geometria NoCuda; nao le conta nem envia ordens."

#include <JPWealth/JPW_NoCuda_Core.mqh>

int g_nocuda_pass=0;
int g_nocuda_fail=0;

void JPWNoCudaAssert(const bool condition,const string label)
  {
   if(condition) g_nocuda_pass++;
   else
     {
      g_nocuda_fail++;
      Print("FAIL: ",label);
     }
  }

void JPWNoCudaNear(const double actual,const double expected,const string label)
  {
   JPWNoCudaAssert(MathIsValidNumber(actual) &&
                   MathAbs(actual-expected)<=1e-10*MathMax(1.0,MathAbs(expected)),label);
  }

void JPWNoCudaTestArticleM()
  {
   JPWNoCudaGeometry geometry;
   string reason="";
   // Fechamentos H1: 08:00=A, 10:00=C e 12:00=B.
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(0,1.1000,4,1.1020,2,1.1050,
                                         geometry,reason) && reason=="",
                    "Article M geometry builds from bar ordinal, not clock hours");
   JPWNoCudaNear(geometry.slope,0.0005,"M slope is 0.0005 per H1 bar");
   JPWNoCudaNear(geometry.signed_offset,0.0040,"M signed width is 0.0040");
   JPWNoCudaNear(geometry.width,0.0040,"M width is 0.0040");
   JPWNoCudaNear(geometry.subdivision,0.0005,"M subdivision is 0.0005");
   double price=0.0;
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,0.0,2.0,price),"M base at C exists");
   JPWNoCudaNear(price,1.1010,"M base at C is linear interpolation");
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,0.5,2.0,price),"M midpoint exists");
   JPWNoCudaNear(price,1.1030,"M midpoint is base plus 0.0020");
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,1.0,2.0,price),"M outer line exists");
   JPWNoCudaNear(price,1.1050,"M outer line meets C exactly");
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,0.0,4.0,price),"M base at B exists");
   JPWNoCudaNear(price,1.1020,"M base meets B exactly");
  }

void JPWNoCudaTestGAndDirection()
  {
   JPWNoCudaGeometry geometry,swapped;
   string reason="";
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(0,1.1000,4,1.1020,2,1.1038,
                                         geometry,reason),"G fixture builds");
   JPWNoCudaNear(geometry.width,0.00280,"G width is 0.00280");
   double price=0.0;
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,0.5,2.0,price),"G midpoint exists");
   JPWNoCudaNear(price-1.1010,0.00140,"G midpoint offset is 0.00140");
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(4,1.1020,0,1.1000,2,1.1038,
                                         swapped,reason),"A/B order may be reversed");
   JPWNoCudaAssert(JPWNoCudaPriceAt(swapped,0.5,2.0,price),"reversed A/B projected");
   JPWNoCudaNear(price,1.1024,"reversed A/B preserves source geometry");
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(0,1.1000,4,1.0980,2,1.0950,
                                         geometry,reason),"descending C below builds");
   JPWNoCudaNear(geometry.slope,-0.0005,"descending principal preserves sign");
   JPWNoCudaNear(geometry.signed_offset,-0.0040,"C below preserves signed offset");
   JPWNoCudaAssert(JPWNoCudaPriceAt(geometry,0.5,2.0,price),"below midpoint exists");
   JPWNoCudaNear(price,1.0970,"below midpoint lies between principal and outer");
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(0,100.0,4,100.0,2,99.0,
                                         geometry,reason),"horizontal principal builds");
   JPWNoCudaNear(geometry.slope,0.0,"horizontal slope is exactly zero");
   JPWNoCudaNear(geometry.signed_offset,-1.0,"horizontal C below is signed");
  }

void JPWNoCudaTestGrid()
  {
   double level=0.0,previous=0.0;
   int count=0;
   for(int k=0;k<65;k++)
     {
      if(!JPWNoCudaLevelValue(k,level)) continue;
      count++;
      if(k>0) JPWNoCudaNear(level-previous,0.125,"adjacent grid levels are 0.125");
      if(k==0) JPWNoCudaNear(level,-4.0,"grid starts at -4");
      if(k==32) JPWNoCudaNear(level,0.0,"A/B is level 0");
      if(k==36) JPWNoCudaNear(level,0.5,"middle is level 0.5");
      if(k==40) JPWNoCudaNear(level,1.0,"C is level 1 after eight intervals");
      if(k==64) JPWNoCudaNear(level,4.0,"grid ends at +4");
      previous=level;
     }
   JPWNoCudaAssert(count==65,"exactly 65 grid levels");
   JPWNoCudaAssert(!JPWNoCudaLevelValue(-1,level) &&
                   !JPWNoCudaLevelValue(65,level),"grid rejects out-of-range indexes");
  }

void JPWNoCudaTestBadInputs()
  {
   JPWNoCudaGeometry geometry;
   string reason="";
   JPWNoCudaAssert(!JPWNoCudaBuildGeometry(2,1.0,2,1.1,3,1.2,
                                          geometry,reason) && reason=="SAME_AB_BAR" &&
                   geometry.width==0.0,"same source bar A/B refused without stale geometry");
   JPWNoCudaAssert(!JPWNoCudaBuildGeometry(0,1.0,2,1.2,1,1.1,
                                          geometry,reason) && reason=="ZERO_WIDTH",
                    "C on principal gives no channel");
   JPWNoCudaAssert(!JPWNoCudaBuildGeometry(-1,1.0,2,1.2,1,1.3,
                                          geometry,reason) && reason=="INVALID_ORDINAL",
                    "negative source ordinal refused");
   JPWNoCudaAssert(!JPWNoCudaBuildGeometry(0,1.0,2,1.2,9007199254740992,1.3,
                                          geometry,reason) && reason=="INVALID_ORDINAL",
                    "ordinal beyond double exact integer refused");
   const double not_a_number=MathSqrt(-1.0);
   JPWNoCudaAssert(!JPWNoCudaBuildGeometry(0,1.0,2,1.2,1,not_a_number,
                                          geometry,reason) && reason=="INVALID_CLOSE",
                    "nonfinite close refused");
   JPWNoCudaAssert(JPWNoCudaBuildGeometry(0,1.0,2,1.2,1,1.3,
                                         geometry,reason),"valid state rebuilt");
   double price=42.0;
   JPWNoCudaAssert(!JPWNoCudaPriceAt(geometry,not_a_number,1.0,price) && price==0.0,
                   "invalid level never leaks a prior price");
  }

void JPWNoCudaTestSourceTimeline()
  {
   double ordinal=0.0;
   const datetime friday=(datetime)1000000;
   const datetime monday=(datetime)1259200; // 72h later: calendar gap, one bar step.
   JPWNoCudaAssert(JPWNoCudaInterpolateOrdinal(friday,monday,
                                               friday+129600,17,ordinal),
                    "interpolation accepts an instant between known source openings");
   JPWNoCudaNear(ordinal,17.5,"72h calendar gap spans one source ordinal");
   JPWNoCudaAssert(JPWNoCudaInterpolateOrdinal(friday,monday,monday,17,ordinal),
                    "next source opening is next ordinal");
   JPWNoCudaNear(ordinal,18.0,"next opening increments exactly one candle");
   JPWNoCudaAssert(!JPWNoCudaInterpolateOrdinal(friday,monday,friday-1,17,ordinal),
                    "outside known source pair refused");
   JPWNoCudaAssert(!JPWNoCudaInterpolateOrdinal(monday,friday,monday,17,ordinal),
                    "reversed source times refused");
  }

void OnStart()
  {
   JPWNoCudaTestArticleM();
   JPWNoCudaTestGAndDirection();
   JPWNoCudaTestGrid();
   JPWNoCudaTestBadInputs();
   JPWNoCudaTestSourceTimeline();
   Print("JPW_NoCuda_Core_Tests: ",g_nocuda_fail==0 ? "PASS" : "FAIL",
         " (",g_nocuda_pass," asserts, ",g_nocuda_fail," failures)");
  }

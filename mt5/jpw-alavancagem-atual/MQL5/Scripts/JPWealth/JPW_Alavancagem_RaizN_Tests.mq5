#property copyright "JP Wealth"
#property version   "1.40"
#property description "Testes sinteticos puros do diagnostico Raiz N."

#include <JPWealth/JPW_Alavancagem_RaizN_Core.mqh>

// Nenhuma conta, cotacao, arquivo ou ordem e lida ou alterada por este script.
int g_raizn_passes=0;
int g_raizn_failures=0;

void JPWRaizNAssert(const bool condition,const string label)
  {
   if(condition) g_raizn_passes++;
   else
     {
      g_raizn_failures++;
      Print("FAIL: ",label);
     }
  }

void JPWRaizNNear(const double actual,const double expected,
                  const string label)
  {
   JPWRaizNAssert(MathIsValidNumber(actual) &&
                  MathAbs(actual-expected)<=
                  1e-9*MathMax(1.0,MathAbs(expected)),label);
  }

void JPWRaizNTestFormula()
  {
   double price=0.0,percent=0.0;
   // Valor independente conhecido do exemplo; nao repetir a formula como oraculo.
   const double expected=2.738612787525831;
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,30,1.25,
                                    price,percent)==JPW_RAIZN_OK,
                   "illustrative declaration calculates");
   JPWRaizNNear(price,expected,"Dprice is ATR times root N times F");
   JPWRaizNNear(percent,expected,"Dpercent is percentage points of P0");

   JPWRaizNAssert(JPWRaizNCalculate(100.0,2.0,4,2.0,
                                    price,percent)==JPW_RAIZN_OK,
                   "explicit F calculates");
   JPWRaizNNear(price,8.0,"F is outside square root");
   JPWRaizNNear(percent,8.0,"8 means 8 percent, not fraction .08");
   JPWRaizNAssert(JPWRaizNCalculate(200.0,2.0,4,2.0,
                                    price,percent)==JPW_RAIZN_OK,
                   "price base changes percentage only");
   JPWRaizNNear(price,8.0,"Dprice independent of P0");
   JPWRaizNNear(percent,4.0,"Dpercent uses declared P0");

   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,30,1.25,
                                    price,percent)==JPW_RAIZN_OK,
                   "same prices in USD and USC use same formula");
   JPWRaizNNear(percent,expected,"USC does not multiply price by 100");
  }

void JPWRaizNTestInvalid()
  {
   double price=123.0,percent=456.0;
   const double invalid=MathSqrt(-1.0);
   JPWRaizNAssert(JPWRaizNCalculate(0.0,0.4,30,1.25,
                                    price,percent)==JPW_RAIZN_BAD_P0 &&
                   price==0.0 && percent==0.0,
                   "missing P0 is unavailable, not an output zero");
   JPWRaizNAssert(JPWRaizNCalculate(invalid,0.4,30,1.25,
                                    price,percent)==JPW_RAIZN_BAD_P0,
                   "NaN P0 rejected");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.0,30,1.25,
                                    price,percent)==JPW_RAIZN_BAD_ATR,
                   "missing ATR rejected");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,invalid,30,1.25,
                                    price,percent)==JPW_RAIZN_BAD_ATR,
                   "NaN ATR rejected");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,0,1.25,
                                    price,percent)==JPW_RAIZN_BAD_N,
                   "N zero rejected, no default");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,-1,1.25,
                                    price,percent)==JPW_RAIZN_BAD_N,
                   "negative N rejected");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,30,0.0,
                                    price,percent)==JPW_RAIZN_BAD_F,
                   "F zero rejected, no default");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,0.4,30,invalid,
                                    price,percent)==JPW_RAIZN_BAD_F,
                   "NaN F rejected");
   JPWRaizNAssert(JPWRaizNCalculate(100.0,1.0e308,30,1.25,
                                    price,percent)==JPW_RAIZN_CALC_ERROR &&
                   price==0.0 && percent==0.0,
                   "overflow rejected without stale output");
  }

void JPWRaizNTestH4Reference()
  {
   const datetime opened=D'2026.09.28 04:00';
   JPWRaizNAssert(!JPWRaizNBarClosedBy(opened,D'2026.09.28 07:59:59'),
                   "open H4 candle cannot support declaration");
   JPWRaizNAssert(JPWRaizNBarClosedBy(opened,D'2026.09.28 08:00:00'),
                   "H4 close at reference is allowed");
   JPWRaizNAssert(JPWRaizNBarClosedBy(opened,D'2026.09.29 10:00:00'),
                   "historic closed bar remains closed");
   JPWRaizNAssert(!JPWRaizNBarClosedBy(D'2026.09.29 04:00',
                                        D'2026.09.28 08:00'),
                   "future bar cannot be used retrospectively");
   JPWRaizNAssert(!JPWRaizNBarClosedBy((datetime)0,
                                        D'2026.09.28 08:00'),
                   "missing bar time rejected");
   JPWRaizNAssert(!JPWRaizNBarClosedBy(opened,(datetime)0),
                   "missing reference time rejected");
  }

void JPWRaizNTestSLComparison()
  {
   double sl_price=0.0,sl_percent=0.0,gap_price=0.0,gap_percent=0.0;
   JPW_RAIZN_SL_RESULT result=JPWRaizNCompareSL(
      JPW_RAIZN_SIDE_BUY,1.10,1.08,0.03,
      sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_OK,"BUY adverse SL comparable");
   JPWRaizNNear(sl_price,0.02,"BUY SL distance based on P0, not Bid");
   JPWRaizNNear(sl_percent,100.0*0.02/1.10,
                "BUY SL percent has same P0 base");
   JPWRaizNNear(gap_price,-0.01,"negative gap means SL closer than Raiz N");
   JPWRaizNNear(gap_percent,100.0*(-0.01)/1.10,
                "gap percentage uses P0");

   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_SELL,1.10,1.12,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_OK,"SELL adverse SL comparable");
   JPWRaizNNear(sl_price,0.02,"SELL direction reversed correctly");

   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_BUY,1.10,1.11,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_PROTECTED &&
                   sl_price==0.0 && gap_price==0.0,
                   "BUY protected-profit SL not compared as adverse risk");
   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_SELL,1.10,1.09,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_PROTECTED,
                   "SELL protected-profit SL not compared as adverse risk");
   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_BUY,1.10,1.10,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_AT_P0,
                   "SL at P0 has a distinct state");
   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_BUY,1.10,0.0,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_NO_SL,
                   "missing SL remains missing");
   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_NONE,1.10,1.08,0.03,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_INVALID,
                   "unlinked side cannot be compared");
   result=JPWRaizNCompareSL(JPW_RAIZN_SIDE_BUY,1.10,1.08,0.0,
                            sl_price,sl_percent,gap_price,gap_percent);
   JPWRaizNAssert(result==JPW_RAIZN_SL_INVALID,
                   "invalid Raiz N distance cannot be compared");
  }

void OnStart()
  {
   JPWRaizNTestFormula();
   JPWRaizNTestInvalid();
   JPWRaizNTestH4Reference();
   JPWRaizNTestSLComparison();
   if(g_raizn_failures==0)
      PrintFormat("JPW_Alavancagem_RaizN_Tests PASS: %d asserts",
                  g_raizn_passes);
   else
      PrintFormat("JPW_Alavancagem_RaizN_Tests FAIL: %d of %d asserts",
                  g_raizn_failures,g_raizn_passes+g_raizn_failures);
  }

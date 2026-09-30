#property copyright "JP Wealth"
#property version   "1.20"
#property script_show_inputs

#include <JPWealth/JPW_Alavancagem_Core.mqh>

// Fixtures inteiramente sinteticas. Executar apenas em terminal isolado.
int g_passes=0;
int g_failures=0;
const long TEST_NOW_MS=1000000;

void JPWAssert(const bool condition,const string label)
  {
   if(condition)
     {
      g_passes++;
      return;
     }
   g_failures++;
   Print("FAIL: ",label);
  }

void JPWNear(const double actual,const double expected,const string label)
  {
   const double tolerance=1e-8*MathMax(1.0,MathAbs(expected));
   JPWAssert(MathIsValidNumber(actual) &&
             MathAbs(actual-expected)<=tolerance,label);
  }

void JPWPositionFixture(JPWPosition &position,const ulong ticket,
                        const string symbol,const double lots,const long direction)
  {
   position.ticket=ticket;
   position.identifier=(long)ticket;
   position.symbol=symbol;
   position.direction=direction;
   position.volume=lots;
  }

void JPWInstrumentFixture(JPWInstrument &instrument,const string symbol,
                          const int mode,const string base,const string profit,
                          const double contract,const bool underlying=false)
  {
   instrument.symbol=symbol;
   instrument.calc_mode=mode;
   instrument.base=base;
   instrument.profit=profit;
   instrument.contract_size=contract;
   instrument.underlying_verified=underlying;
  }

void JPWQuoteFixture(JPWQuote &quote,const string symbol,const string base,
                     const string profit,const double bid,const double ask,
                     const long time_msc=1000000,const bool forex_mode=true)
  {
   quote.symbol=symbol;
   quote.base=base;
   quote.profit=profit;
   quote.bid=bid;
   quote.ask=ask;
   quote.time_msc=time_msc;
   quote.conversion_pair=(forex_mode && JPWIsFiat(base) && JPWIsFiat(profit));
  }

void JPWPortfolioNear(const string label,JPWPosition &positions[],
                      JPWInstrument &instruments[],JPWQuote &quotes[],
                      const string currency,const double equity,
                      const double expected)
  {
   JPWRoute routes[];
   double gross=0.0;
   const JPW_RESULT result=JPWGross(positions,instruments,quotes,currency,
                                    TEST_NOW_MS,30,routes,gross);
   JPWAssert(result==JPW_OK,label+" gross status");
   if(result!=JPW_OK) return;
   double leverage=0.0;
   const JPW_RESULT final_result=JPWLeverage(gross,equity,leverage);
   JPWAssert(final_result==JPW_OK,label+" leverage status");
   if(final_result==JPW_OK) JPWNear(leverage,expected,label+" value");
  }

void JPWTestCanonical()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   ArrayResize(positions,0);
   ArrayResize(instruments,0);
   ArrayResize(quotes,0);
   JPWPortfolioNear("no positions",positions,instruments,quotes,"USD",1000,0.0);

   ArrayResize(positions,2);
   ArrayResize(instruments,2);
   ArrayResize(quotes,2);
   JPWPositionFixture(positions[0],1,"NZDUSD",0.01,POSITION_TYPE_BUY);
   JPWPositionFixture(positions[1],2,"XAUUSD",0.01,POSITION_TYPE_SELL);
   JPWInstrumentFixture(instruments[0],"NZDUSD",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",100000);
   JPWInstrumentFixture(instruments[1],"XAUUSD",SYMBOL_CALC_MODE_FOREX,
                        "XAU","USD",100);
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.59,0.61);
   JPWQuoteFixture(quotes[1],"XAUUSD","XAU","USD",3000,3000);
   JPWPortfolioNear("NZD plus XAU",positions,instruments,quotes,"USD",1000,3.60);
   JPWPortfolioNear("equity lower",positions,instruments,quotes,"USD",900,4.00);
   JPWPortfolioNear("equity higher",positions,instruments,quotes,"USD",1200,3.00);
   quotes[1].bid=3100;
   quotes[1].ask=3100;
   JPWPortfolioNear("gold price 3100",positions,instruments,quotes,"USD",1000,3.70);
   quotes[1].bid=3000;
   quotes[1].ask=3000;
   instruments[1].contract_size=10;
   JPWPortfolioNear("gold 10 ounces plus NZD",positions,instruments,quotes,
                    "USD",1000,0.90);
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   JPWPortfolioNear("NZD only",positions,instruments,quotes,"USD",1000,0.60);
   positions[0].volume=0.02;
   JPWPortfolioNear("double volume",positions,instruments,quotes,"USD",1000,1.20);
   positions[0].volume=0.005;
   JPWPortfolioNear("partial close",positions,instruments,quotes,"USD",1000,0.30);
   instruments[0].contract_size=50000;
   positions[0].volume=0.01;
   JPWPortfolioNear("forex contract 50000",positions,instruments,quotes,"USD",1000,0.30);
   instruments[0].contract_size=100000;
   positions[0].symbol="broker.NZDUSD.sfx";
   instruments[0].symbol="broker.NZDUSD.sfx";
   quotes[0].symbol="broker.NZDUSD.sfx";
   JPWPortfolioNear("symbol prefix and suffix",positions,instruments,quotes,
                    "USD",1000,0.60);
   positions[0].symbol="NZDUSD";
   instruments[0].symbol="NZDUSD";
   quotes[0].symbol="NZDUSD";
   ArrayResize(positions,2);
   ArrayResize(instruments,2);
   JPWPositionFixture(positions[1],3,"NZDUSD",0.01,POSITION_TYPE_SELL);
   instruments[1]=instruments[0];
   JPWPortfolioNear("opposite hedging gross",positions,instruments,quotes,
                    "USD",1000,1.20);
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   positions[0].volume=0.05;
   JPWPortfolioNear("netting current position",positions,instruments,quotes,
                    "USD",1000,3.00);
   ArrayResize(positions,2);
   ArrayResize(instruments,2);
   JPWPositionFixture(positions[0],4,"NZDUSD",0.0833333333333333,POSITION_TYPE_BUY);
   JPWPositionFixture(positions[1],5,"NZDUSD",0.0833333333333333,POSITION_TYPE_SELL);
   instruments[1]=instruments[0];
   JPWPortfolioNear("opposite hedging 5000 each",positions,instruments,quotes,
                    "USD",10000,1.00);
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   positions[0].volume=0.01;
   instruments[0].calc_mode=SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE;
   JPWPortfolioNear("contracted leverage independent",positions,instruments,
                    quotes,"USD",1000,0.60);
  }

void JPWTestGoldAndCFD()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   ArrayResize(quotes,1);
   JPWPositionFixture(positions[0],10,"XAUUSD",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"XAUUSD",SYMBOL_CALC_MODE_FOREX,
                        "XAU","USD",100);
   JPWQuoteFixture(quotes[0],"XAUUSD","XAU","USD",3000,3000);
   JPWPortfolioNear("XAU forex mode",positions,instruments,quotes,"USD",1000,3.00);
   instruments[0].calc_mode=SYMBOL_CALC_MODE_CFD;
   JPWPortfolioNear("XAU CFD mode",positions,instruments,quotes,"USD",1000,3.00);
   instruments[0].calc_mode=SYMBOL_CALC_MODE_CFDLEVERAGE;
   JPWPortfolioNear("XAU CFD leverage mode",positions,instruments,quotes,
                    "USD",1000,3.00);
   instruments[0].contract_size=10;
   JPWPortfolioNear("XAU 10-ounce contract",positions,instruments,quotes,
                    "USD",1000,0.30);
   JPWPositionFixture(positions[0],11,"ABC.share",1.0,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"ABC.share",SYMBOL_CALC_MODE_CFD,
                        "ABC","USD",2,true);
   JPWQuoteFixture(quotes[0],"ABC.share","ABC","USD",49,51);
   JPWPortfolioNear("verified linear CFD",positions,instruments,quotes,
                    "USD",1000,0.10);
   instruments[0].underlying_verified=false;
   JPWRoute routes[];
   double gross=0.0;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_UNSUPPORTED_CONTRACT,
             "CFD without verified underlying rejected");
   instruments[0].underlying_verified=true;
   instruments[0].calc_mode=SYMBOL_CALC_MODE_CFDINDEX;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_UNSUPPORTED_CONTRACT,
             "CFDINDEX excluded");
   JPWPositionFixture(positions[0],12,"EURUSD.cfd",1.0,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"EURUSD.cfd",SYMBOL_CALC_MODE_CFD,
                        "EUR","USD",100,true);
   JPWQuoteFixture(quotes[0],"EURUSD.cfd","EUR","USD",1.2,1.2,
                   TEST_NOW_MS,false);
   JPWAssert(JPWGross(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                      routes,gross)==JPW_NO_CONVERSION,
             "CFD quote cannot serve as fiat FX conversion");
  }

void JPWTestCurrencies()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   ArrayResize(quotes,2);
   JPWPositionFixture(positions[0],20,"USDJPY",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"USDJPY",SYMBOL_CALC_MODE_FOREX,
                        "USD","JPY",100000);
   JPWQuoteFixture(quotes[0],"USDJPY","USD","JPY",150,150);
   JPWPortfolioNear("USDJPY account USD",positions,instruments,quotes,
                    "USD",1000,1.00);
   JPWPositionFixture(positions[0],21,"EURJPY",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"EURJPY",SYMBOL_CALC_MODE_FOREX,
                        "EUR","JPY",100000);
   JPWQuoteFixture(quotes[0],"EURJPY","EUR","JPY",165,165);
   JPWQuoteFixture(quotes[1],"EURUSD","EUR","USD",1.10,1.10);
   JPWPortfolioNear("EURJPY account USD",positions,instruments,quotes,
                    "USD",1000,1.10);
   JPWPositionFixture(positions[0],22,"NZDUSD",0.01,POSITION_TYPE_SELL);
   JPWInstrumentFixture(instruments[0],"NZDUSD",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",100000);
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.60,0.60);
   JPWQuoteFixture(quotes[1],"EURUSD","EUR","USD",1.20,1.20);
   JPWPortfolioNear("inverse USD to EUR",positions,instruments,quotes,
                    "EUR",1000,0.50);
   JPWQuoteFixture(quotes[1],"USDCHF","USD","CHF",0.90,0.90);
   JPWPortfolioNear("two legs NZD USD CHF",positions,instruments,quotes,
                    "CHF",1000,0.54);
  }

void JPWTestRoutes()
  {
   JPWQuote quotes[];
   ArrayResize(quotes,4);
   JPWQuoteFixture(quotes[0],"z.NZDUSD","NZD","USD",0.6,0.6);
   JPWQuoteFixture(quotes[1],"a.NZDUSD","NZD","USD",0.6,0.6);
   JPWQuoteFixture(quotes[2],"USDCHF","USD","CHF",0.9,0.9);
   JPWQuoteFixture(quotes[3],"USDNZD","USD","NZD",1.6666666667,1.6666666667);
   JPWRoute previous;
   previous.valid=false;
   JPWRoute chosen;
   double rate=0.0;
   JPWAssert(JPWFindRoute("NZD","USD",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.first_symbol=="a.NZDUSD",
             "direct route lexical tie");
   JPWRoute same_currency_route;
   double same_currency_rate=0.0;
   JPWAssert(JPWFindRoute("USD","USD",quotes,TEST_NOW_MS,30,previous,
                          same_currency_route,same_currency_rate) &&
             same_currency_rate==1.0,
             "same-currency rate is one");
   previous=chosen;
   previous.first_symbol="z.NZDUSD";
   JPWAssert(JPWFindRoute("NZD","USD",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.first_symbol=="z.NZDUSD",
             "preferred valid route retained");
   quotes[0].time_msc=TEST_NOW_MS-31000;
   JPWAssert(JPWFindRoute("NZD","USD",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.first_symbol=="a.NZDUSD",
             "stale preferred route replaced");
   quotes[1].time_msc=TEST_NOW_MS-31000;
   previous.valid=false;
   JPWAssert(JPWFindRoute("NZD","USD",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.first_symbol=="USDNZD" &&
             chosen.first_direction==-1,"inverse alternative after stale direct");
   quotes[3].time_msc=TEST_NOW_MS-31000;
   JPWAssert(!JPWFindRoute("NZD","USD",quotes,TEST_NOW_MS,30,previous,
                            chosen,rate),"all conversion alternatives stale");
   quotes[1].time_msc=TEST_NOW_MS;
   JPWAssert(JPWFindRoute("NZD","CHF",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.intermediate=="USD",
             "two-step route uses fiat intermediate");
   quotes[1].base="XAU";
   JPWAssert(!JPWFindRoute("NZD","CHF",quotes,TEST_NOW_MS,30,previous,
                            chosen,rate),"metal cannot be conversion intermediate");
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.6,0.6);
   JPWQuoteFixture(quotes[1],"USDCHF","USD","CHF",0.9,0.9);
   JPWQuoteFixture(quotes[2],"NZDEUR","NZD","EUR",0.5,0.5);
   JPWQuoteFixture(quotes[3],"EURCHF","EUR","CHF",1.1,1.1);
   JPWAssert(JPWFindRoute("NZD","CHF",quotes,TEST_NOW_MS,30,previous,
                          chosen,rate) && chosen.intermediate=="EUR",
             "two-step lexical intermediary tie");
  }

void JPWTestFailures()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   JPWRoute routes[];
   ArrayResize(positions,1);
   ArrayResize(instruments,1);
   ArrayResize(quotes,1);
   JPWPositionFixture(positions[0],30,"NZDUSD",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"NZDUSD",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",100000);
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.6,0.6);
   double gross=0.0;
   double leverage=0.0;
   JPWAssert(JPWLeverage(600,0,leverage)==JPW_BAD_EQUITY,"zero equity");
   JPWAssert(JPWLeverage(600,-1,leverage)==JPW_BAD_EQUITY,"negative equity");
   JPWAssert(JPWLeverage(600,MathSqrt(-1),leverage)==JPW_BAD_EQUITY,
             "nonfinite equity");
   JPWAssert(JPWFormatLeverage(0.0)=="0,00x","confirmed zero format");
   JPWAssert(JPWFormatLeverage(0.001)=="<0,01x","small positive format");
   JPWAssert(JPWFormatLeverage(3.6)=="3,60x","two decimal format");
   positions[0].volume=0;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_CALC_ERROR,"zero volume");
   positions[0].volume=0.01;
   instruments[0].contract_size=0;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_UNSUPPORTED_CONTRACT,"zero contract");
   instruments[0].contract_size=100000;
   instruments[0].base="XAG";
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_UNSUPPORTED_CONTRACT,"unknown metal contract");
   instruments[0].base="NZD";
   quotes[0].bid=0;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_BAD_QUOTE,"zero bid");
   quotes[0].bid=0.61;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_BAD_QUOTE,"ask below bid");
   quotes[0].bid=0.6;
   quotes[0].time_msc=TEST_NOW_MS-31000;
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_BAD_QUOTE,"stale own quote");
   quotes[0].time_msc=TEST_NOW_MS;
   JPWAssert(JPWGross(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                      routes,gross)==JPW_NO_CONVERSION,"missing conversion");
   JPWAssert(JPWGross(positions,instruments,quotes,"USC",TEST_NOW_MS,30,
                      routes,gross)==JPW_CALC_ERROR,"cent account no guessed scale");
   positions[0].symbol="MISSING";
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_CALC_ERROR,"missing position metadata invalidates");
   positions[0].symbol="NZDUSD";
   ArrayResize(positions,2);
   ArrayResize(instruments,1);
   JPWAssert(JPWGross(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                      routes,gross)==JPW_CALC_ERROR,"one unread position invalidates total");
  }

void JPWTestSnapshotAndClock()
  {
   JPWPosition first[];
   JPWPosition second[];
   ArrayResize(first,2);
   ArrayResize(second,2);
   JPWPositionFixture(first[0],1,"NZDUSD",0.01,POSITION_TYPE_BUY);
   JPWPositionFixture(first[1],2,"NZDUSD",0.02,POSITION_TYPE_SELL);
   second[0]=first[1];
   second[1]=first[0];
   JPWAssert(JPWPositionsEqual(first,second),"reorder keeps same snapshot");
   second[1].ticket=3;
   JPWAssert(!JPWPositionsEqual(first,second),"same count replacement detected");
   second[1]=first[0];
   second[1].volume=0.005;
   JPWAssert(!JPWPositionsEqual(first,second),"partial close detected");
   JPWAccount a;
   JPWAccount b;
   a.login=1; a.server="server-a"; a.currency="USD";
   b=a;
   JPWAssert(JPWAccountsEqual(a,b),"account identity same");
   b.server="server-b";
   JPWAssert(!JPWAccountsEqual(a,b),"server change detected");
   b=a; b.currency="EUR";
   JPWAssert(!JPWAccountsEqual(a,b),"account currency change detected");
   b=a; b.login=2;
   JPWAssert(!JPWAccountsEqual(a,b),"account login change detected");

   JPWClock clock;
   JPWClockReset(clock,1000,0);
   long now=0;
   JPWAssert(!JPWClockObserve(clock,1000,1000,0,30,now),
             "startup old clock not anchored");
   JPWAssert(JPWClockObserve(clock,1001,1001,1000,30,now) && now==1001000,
             "new server quote anchors monotonic clock");
   JPWQuote quote;
   JPWQuoteFixture(quote,"NZDUSD","NZD","USD",0.6,0.6,900000);
   double mid=0.0;
   JPWAssert(!JPWQuoteMid(quote,now,30,mid),
             "old stored tick not refreshed on startup");
   quote.time_msc=1001000;
   JPWAssert(JPWQuoteMid(quote,now,30,mid),"new tick accepted");
   JPWAssert(JPWClockObserve(clock,1001,1002,2000,30,now) &&
             JPWQuoteMid(quote,now,30,mid),
             "reread same tick ages with monotonic time");
   JPWAssert(JPWClockObserve(clock,1001,1032,32000,30,now) &&
             !JPWQuoteMid(quote,now,30,mid),
             "closed market tick expires after threshold");
   quote.time_msc=1032000;
   JPWAssert(JPWQuoteMid(quote,now,30,mid),
             "same price new timestamp accepted");
   JPWAssert(!JPWClockObserve(clock,1001,1032,37000,30,now),
             "frozen estimated reference invalidates clock");
   JPWAssert(!JPWClockObserve(clock,999,1038,38000,30,now),
             "server time regression rejected");
   JPWClockReset(clock,1001,38000);
   JPWAssert(!JPWClockObserve(clock,1001,1039,39000,30,now),
             "reconnect requires new observation");
  }

void JPWTestUSC()
  {
   string currency="";
   double divisor=0.0;
   JPWAssert(JPWAccountUnits(" usc ",currency,divisor) && currency=="USD",
             "USC explicit currency normalized");
   JPWNear(divisor,100.0,"USC denominator exactly 100");
   const double equity_usd=10000.0/divisor;
   JPWNear(equity_usd,100.0,"10000 USC equals 100 USD");
   JPWAssert(JPWAccountUnits(" usd ",currency,divisor) && currency=="USD" &&
             divisor==1.0,"ordinary USD not rescaled");
   JPWAssert(!JPWAccountUnits("USCent",currency,divisor),"unknown cent alias refused");
   JPWAssert(!JPWAccountUnits(".m",currency,divisor),"symbol suffix is not currency");
   JPWAssert(!JPWAccountUnits("USD C",currency,divisor),"internal whitespace not guessed");

   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   JPWRoute routes[];
   double scales[];
   ArrayResize(positions,1); ArrayResize(instruments,1);
   ArrayResize(quotes,1); ArrayResize(scales,1);
   JPWPositionFixture(positions[0],100,"NZDUSD.cent",0.1,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"NZDUSD.cent",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",1000);
   JPWQuoteFixture(quotes[0],"NZDUSD.cent","NZD","USD",0.6,0.6);
   scales[0]=1.0;
   double gross=0.0;
   bool estimated=false;
   long oldest=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK,
             "USC physically small contract accepted with verified scale1");
   JPWNear(gross,60.0,"USC physical contract gross USD");
   double leverage=0.0;
   JPWAssert(JPWLeverage(gross,equity_usd,leverage)==JPW_OK,"USC normalized equity valid");
   JPWNear(leverage,0.60,"physical1000 contract yields0.60x");
   double usd_leverage=0.0;
   JPWAssert(JPWLeverage(gross,100,usd_leverage)==JPW_OK,"USD comparison valid");
   JPWNear(leverage,usd_leverage,"USD and USC same physical exposure");
   instruments[0].contract_size=100000;
   scales[0]=0.01;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK,
             "USC cent-base contract accepted with verified scale0.01");
   JPWNear(gross,60.0,"cent contract normalized once only");
   JPWAssert(JPWLeverage(gross,equity_usd,leverage)==JPW_OK,"cent contract ratio valid");
   JPWNear(leverage,0.60,"raw100000 cent contract yields0.60x");
   ArrayResize(positions,2); ArrayResize(instruments,2); ArrayResize(scales,2);
   JPWPositionFixture(positions[1],101,"NZDUSD.small",0.1,POSITION_TYPE_SELL);
   JPWInstrumentFixture(instruments[1],"NZDUSD.small",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",1000);
   ArrayResize(quotes,2);
   JPWQuoteFixture(quotes[1],"NZDUSD.small","NZD","USD",0.6,0.6);
   scales[1]=1.0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK,
             "heterogeneous verified contracts accepted independently");
   JPWNear(gross,120.0,"heterogeneous opposite positions remain gross");
   scales[1]=0.0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_UNVERIFIED_UNITS,
             "one unverified contract invalidates whole portfolio");
   JPWNear(gross,0.0,"failed total exposes no partial subtotal");
   scales[1]=2.0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_UNVERIFIED_UNITS,
             "scale outside approved1 and0.01 rejected");
   ArrayResize(scales,1);
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_UNVERIFIED_UNITS,
             "missing scale entry rejected");
  }

void JPWTestScaleVerification()
  {
   double expected[];
   double native[];
   ArrayResize(expected,4); ArrayResize(native,4);
   expected[0]=100; expected[1]=-100; expected[2]=200; expected[3]=-200;
   for(int i=0;i<4;i++) native[i]=expected[i];
   double scale=0.0;
   JPWAssert(JPWVerifyScale(expected,native,0.01,scale) && scale==1.0,
             "four native profits confirm scale1");
   for(int i=0;i<4;i++) native[i]=expected[i]*0.01;
   JPWAssert(JPWVerifyScale(expected,native,0.01,scale) && scale==0.01,
             "four native profits confirm scale0.01");
   native[0]=1.005;
   JPWAssert(JPWVerifyScale(expected,native,0.01,scale) && scale==0.01,
             "subpercent native rounding accepted");
   native[0]=1.02;
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale) && scale==0.0,
             "one sample beyond1percent invalidates scale");
   native[0]=0;
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"native zero not evidence");
   native[0]=1; native[1]=1;
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"negative movement sign must agree");
   native[1]=-1; native[3]=-1;
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"two distinct movement sizes required");
   native[3]=-2;
   JPWAssert(!JPWVerifyScale(expected,native,0.02,scale),"near monetary quantum refused");
   JPWAssert(!JPWVerifyScale(expected,native,0,scale),"unknown rounding unit refused");
   native[2]=MathSqrt(-1);
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"invalid native calculation refused");
   native[2]=200;
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"heterogeneous sample scale ambiguous");
   ArrayResize(native,3);
   JPWAssert(!JPWVerifyScale(expected,native,0.01,scale),"incomplete comparisons refused");
  }

void JPWTestReadings()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   JPWRoute routes[];
   double scales[];
   ArrayResize(positions,1); ArrayResize(instruments,1);
   ArrayResize(quotes,1); ArrayResize(scales,1);
   JPWPositionFixture(positions[0],200,"NZDUSD",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"NZDUSD",SYMBOL_CALC_MODE_FOREX,
                        "NZD","USD",100000);
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.6,0.6);
   scales[0]=1;
   double gross=0;
   bool estimated=false;
   long oldest=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             !estimated && oldest==TEST_NOW_MS,"recent reading classified current");
   JPWNear(gross,600,"current reading gross");
   quotes[0].time_msc=TEST_NOW_MS-31000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             estimated && oldest==TEST_NOW_MS-31000,"stale reading estimates with original date");
   JPWNear(gross,600,"stale quote still computes whole notional");
   quotes[0].bid=0.5; quotes[0].ask=0.5;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK,
             "estimate recomputed from current available terminal inputs");
   JPWNear(gross,500,"estimate is not previous600 total");
   quotes[0].time_msc=TEST_NOW_MS;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,false,scales,routes,gross,estimated,oldest)==JPW_OK &&
             estimated,"disconnected always estimated even recent timestamp");
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",0,30,
                             false,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             estimated && oldest==TEST_NOW_MS,"startup without trusted clock retains absolute date");
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             !estimated,"reconnection fresh trusted data restores current");
   quotes[0].time_msc=TEST_NOW_MS-30000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             !estimated,"30second boundary remains current");
   quotes[0].time_msc=TEST_NOW_MS+3000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_BAD_QUOTE,
             "future timestamp with trusted clock not accepted as estimate");
   quotes[0].time_msc=TEST_NOW_MS;
   quotes[0].bid=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",0,30,
                             false,false,scales,routes,gross,estimated,oldest)==JPW_BAD_QUOTE &&
             gross==0.0,"offline invalid price never becomes numeric estimate");
   quotes[0].bid=0.5;
   quotes[0].time_msc=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"USD",0,30,
                             false,false,scales,routes,gross,estimated,oldest)==JPW_BAD_QUOTE,
             "undated quote unavailable");
   quotes[0].time_msc=TEST_NOW_MS;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",0,30,
                             false,false,scales,routes,gross,estimated,oldest)==JPW_NO_CONVERSION &&
             gross==0.0,"missing conversion never produces partial estimate");
  }

void JPWTestReadingRoutes()
  {
   JPWQuote quotes[];
   ArrayResize(quotes,4);
   JPWQuoteFixture(quotes[0],"NZDUSD","NZD","USD",0.6,0.6,TEST_NOW_MS-90000);
   JPWQuoteFixture(quotes[1],"USDNZD","USD","NZD",2,2,TEST_NOW_MS-5000);
   JPWQuoteFixture(quotes[2],"NZDEUR","NZD","EUR",0.5,0.5,TEST_NOW_MS-10000);
   JPWQuoteFixture(quotes[3],"EURUSD","EUR","USD",1.1,1.1,TEST_NOW_MS-15000);
   JPWRoute previous;
   previous.valid=false;
   JPWRoute chosen;
   double rate=0;
   bool estimated=false;
   long oldest=0;
   JPWAssert(JPWFindRouteReading("NZD","USD",quotes,TEST_NOW_MS,30,true,true,
                                 previous,chosen,rate,estimated,oldest) &&
             chosen.first_symbol=="USDNZD" && !estimated && oldest==TEST_NOW_MS-5000,
             "fresh inverse outranks stale direct");
   JPWNear(rate,0.5,"fresh inverse rate");
   previous=chosen;
   previous.first_symbol="NZDUSD"; previous.first_direction=1;
   JPWAssert(JPWFindRouteReading("NZD","USD",quotes,TEST_NOW_MS,30,true,true,
                                 previous,chosen,rate,estimated,oldest) &&
             chosen.first_symbol=="USDNZD" && !estimated,
             "stale cached route replaced by current alternative");
   quotes[1].time_msc=TEST_NOW_MS-60000;
   JPWAssert(JPWFindRouteReading("NZD","USD",quotes,TEST_NOW_MS,30,true,true,
                                 previous,chosen,rate,estimated,oldest) &&
             chosen.intermediate=="EUR" && !estimated && oldest==TEST_NOW_MS-15000,
             "fresh twoleg route outranks stale direct and inverse");
   JPWNear(rate,0.55,"twoleg independent timestamps multiply correctly");
   quotes[2].time_msc=TEST_NOW_MS-120000;
   quotes[3].time_msc=TEST_NOW_MS-180000;
   previous.valid=false;
   JPWAssert(JPWFindRouteReading("NZD","USD",quotes,TEST_NOW_MS,30,true,true,
                                 previous,chosen,rate,estimated,oldest) &&
             chosen.first_symbol=="NZDUSD" && estimated && oldest==TEST_NOW_MS-90000,
             "only old routes yields explicit estimate with actual oldest date");
   JPWAssert(JPWFindRouteReading("NZD","USD",quotes,0,30,false,false,
                                 previous,chosen,rate,estimated,oldest) &&
             estimated && oldest==TEST_NOW_MS-90000,"offline route keeps timestamp without invented age");
   quotes[0].ask=0; quotes[1].ask=0; quotes[2].ask=0; quotes[3].ask=0;
   JPWAssert(!JPWFindRouteReading("NZD","USD",quotes,0,30,false,false,
                                  previous,chosen,rate,estimated,oldest),
             "structurally invalid routes never estimate");
  }

void JPWTestCompleteReading()
  {
   JPWPosition positions[];
   JPWInstrument instruments[];
   JPWQuote quotes[];
   JPWRoute routes[];
   double scales[];
   ArrayResize(positions,1); ArrayResize(instruments,1);
   ArrayResize(quotes,4); ArrayResize(scales,1);
   JPWPositionFixture(positions[0],300,"USDJPY",0.01,POSITION_TYPE_BUY);
   JPWInstrumentFixture(instruments[0],"USDJPY",SYMBOL_CALC_MODE_FOREX,
                        "USD","JPY",100000);
   JPWQuoteFixture(quotes[0],"USDJPY","USD","JPY",150,150,TEST_NOW_MS-3000);
   JPWQuoteFixture(quotes[1],"USDCHF","USD","CHF",0.9,0.9,TEST_NOW_MS-15000);
   JPWQuoteFixture(quotes[2],"CHFEUR","CHF","EUR",1,1,TEST_NOW_MS-20000);
   JPWQuoteFixture(quotes[3],"NZDUSD","NZD","USD",0.6,0.6,TEST_NOW_MS-90000);
   scales[0]=1.0;
   double gross=0;
   bool estimated=false;
   long oldest=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             !estimated && oldest==TEST_NOW_MS-20000,
             "oldest date covers used ownquote and both FXlegs only");
   JPWNear(gross,900,"twoleg complete reading gross EUR");
   quotes[0].time_msc=TEST_NOW_MS-25000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             oldest==TEST_NOW_MS-25000,"older ownquote included in oldest date");
   quotes[2].time_msc=TEST_NOW_MS-40000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_OK &&
             estimated && oldest==TEST_NOW_MS-40000,
             "single stale conversion leg makes entire reading estimated");
   quotes[2].time_msc=TEST_NOW_MS+3000;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_NO_CONVERSION,
             "trusted clock rejects future conversion even in fallback");
   quotes[2].time_msc=TEST_NOW_MS;
   quotes[0].profit="EUR";
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_BAD_QUOTE,
             "quote and instrument currency mismatch rejected");
   quotes[0].profit="JPY";
   positions[0].ticket=0;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_CALC_ERROR,
             "unselected position ticket cannot yield zero or estimate");
   positions[0].ticket=300;
   ArrayResize(positions,2); ArrayResize(instruments,2); ArrayResize(scales,2);
   positions[1]=positions[0]; instruments[1]=instruments[0]; scales[1]=1;
   JPWAssert(JPWGrossReading(positions,instruments,quotes,"EUR",TEST_NOW_MS,30,
                             true,true,scales,routes,gross,estimated,oldest)==JPW_CALC_ERROR &&
             gross==0.0,"same ticket cannot be counted twice");
  }

void JPWTestUnderflow()
  {
   double result=0.0;
   JPWAssert(JPWLeverage(1e-200,1e200,result)==JPW_CALC_ERROR,"positive exposure underflow must not become zero");
  }

void JPWTestBalanceMetrics()
  {
   double floating=0.0;
   double dd=0.0;
   JPWAssert(JPWFloatingPercent(10000.0,-300.0,floating),"A floating available");
   JPWNear(floating,-3.0,"A floating uses ACCOUNT_PROFIT over balance");
   JPWAssert(JPWBalanceDDPercent(10000.0,9700.0,dd),"A DD available");
   JPWNear(dd,3.0,"A equity deficit over balance");
   JPWAssert(JPWFormatPercent(floating,true)=="-3,00%","A negative signed display");

   JPWAssert(JPWFloatingPercent(10000.0,200.0,floating),"B positive floating available");
   JPWNear(floating,2.0,"B positive floating");
   JPWAssert(JPWBalanceDDPercent(10000.0,10200.0,dd),"B equity above balance available");
   JPWNear(dd,0.0,"B no equity deficit");
   JPWAssert(JPWFormatPercent(floating,true)=="+2,00%","B positive sign display");
   JPWAssert(JPWFloatingPercent(10000.0,0.0,floating) &&
             JPWBalanceDDPercent(10000.0,10000.0,dd),"C exact flat readings available");
   JPWNear(floating,0.0,"C zero floating");
   JPWNear(dd,0.0,"C zero DD");
   JPWAssert(JPWFormatPercent(floating,true)=="0,00%","C zero has no positive sign");

   JPWAssert(JPWFloatingPercent(10000.0,-500.0,floating) &&
             JPWBalanceDDPercent(10000.0,9500.0,dd),
             "E open loss readings available");
   JPWNear(floating,-5.0,"E open loss floating");
   JPWNear(dd,5.0,"E open loss DD");
   JPWAssert(JPWFloatingPercent(9500.0,0.0,floating) &&
             JPWBalanceDDPercent(9500.0,9500.0,dd),
             "E closed loss readings available");
   JPWNear(floating,0.0,"E closed loss floating resets");
   JPWNear(dd,0.0,"E closed loss current DD resets");

   const double credit=1000.0;
   const double balance=10000.0;
   const double profit=-500.0;
   const double equity=balance+credit+profit;
   JPWAssert(JPWFloatingPercent(balance,profit,floating) &&
             JPWBalanceDDPercent(balance,equity,dd),
             "F account credit fixture readings available");
   JPWNear(floating,-5.0,"F credit does not change floating formula");
   JPWNear(dd,0.0,"F terminal equity including credit yields zero DD");

   double usd_floating=0.0;
   double usd_dd=0.0;
   double usc_floating=0.0;
   double usc_dd=0.0;
   JPWAssert(JPWFloatingPercent(100.0,-3.0,usd_floating) &&
             JPWBalanceDDPercent(100.0,97.0,usd_dd) &&
             JPWFloatingPercent(10000.0,-300.0,usc_floating) &&
             JPWBalanceDDPercent(10000.0,9700.0,usc_dd),
             "G USD and USC account readings available");
   JPWNear(usc_floating,usd_floating,"G USC floating scale cancels");
   JPWNear(usc_dd,usd_dd,"G USC DD scale cancels");

   const double invalid=MathSqrt(-1);
   JPWAssert(!JPWFloatingPercent(0.0,-300.0,floating) &&
             !JPWBalanceDDPercent(0.0,9700.0,dd),"H zero balance unavailable");
   JPWAssert(!JPWFloatingPercent(-10000.0,-300.0,floating) &&
             !JPWBalanceDDPercent(-10000.0,9700.0,dd),"H negative balance unavailable");
   JPWAssert(!JPWFloatingPercent(invalid,-300.0,floating) &&
             !JPWBalanceDDPercent(invalid,9700.0,dd),"H nonfinite balance unavailable");
   JPWAssert(!JPWFloatingPercent(10000.0,invalid,floating),
             "H nonfinite profit affects floating only");
   JPWAssert(JPWBalanceDDPercent(10000.0,9700.0,dd),
             "H DD independent of invalid profit");
   JPWNear(dd,3.0,"H valid DD with invalid profit");
   JPWAssert(!JPWBalanceDDPercent(10000.0,invalid,dd),
             "H nonfinite equity affects DD only");
   JPWAssert(JPWFloatingPercent(10000.0,-300.0,floating),
             "H floating independent of invalid equity");
   JPWNear(floating,-3.0,"H valid floating with invalid equity");
   JPWAssert(JPWFormatPercent(invalid,true)=="N/D","H invalid display unavailable");

   JPWAssert(JPWBalanceDDPercent(1000.0,0.0,dd),"I zero equity DD available");
   JPWNear(dd,100.0,"I zero equity means 100 percent DD");
   JPWAssert(JPWBalanceDDPercent(1000.0,-100.0,dd),"I negative equity DD available");
   JPWNear(dd,110.0,"I negative equity allows DD above 100 percent");

   JPWAssert(JPWFloatingPercent(10000.0,0.1,floating) &&
             JPWBalanceDDPercent(10000.0,9999.9,dd),
             "small nonzero percentages available");
   JPWAssert(JPWFormatPercent(floating,true)=="+<0,01%",
             "small positive floating never displays false zero");
   JPWAssert(JPWFloatingPercent(10000.0,-0.1,floating),
             "small negative floating available");
   JPWAssert(JPWFormatPercent(floating,true)=="-<0,01%",
             "small negative floating keeps sign");
   JPWAssert(JPWFormatPercent(dd,false)=="<0,01%",
             "small DD never displays false zero");
   JPWAssert(JPWFormatPercent(0.0,false)=="0,00%","exact zero DD display");
   JPWAssert(JPWFormatPercent(2.5,false)=="2,50%","DD two decimals with comma");

   JPWAssert(JPWFloatingPercent(1e308,1e307,floating),
             "large raw account values avoid intermediate overflow");
   JPWNear(floating,10.0,"large raw account percentage");
   JPWAssert(!JPWFloatingPercent(1e-300,1e308,floating),
             "floating result overflow unavailable");
   JPWAssert(!JPWBalanceDDPercent(1e308,-1e308,dd),
             "DD deficit subtraction overflow unavailable");
   JPWAssert(!JPWFloatingPercent(1e200,1e-200,floating),
             "nonzero floating underflow cannot become false zero");
  }

void OnStart()
  {
   JPWTestCanonical();
   JPWTestGoldAndCFD();
   JPWTestCurrencies();
   JPWTestRoutes();
   JPWTestFailures();
   JPWTestSnapshotAndClock();
   PrintFormat("JPW r1 unchanged scenarios: %d PASS / %d FAIL",g_passes,g_failures);
   JPWTestUnderflow();
   JPWTestUSC();
   JPWTestScaleVerification();
   JPWTestReadings();
   JPWTestReadingRoutes();
   JPWTestCompleteReading();
   JPWTestBalanceMetrics();
   if(g_failures==0) PrintFormat("JPW_Alavancagem_Tests PASS: %d asserts",g_passes);
   else PrintFormat("JPW_Alavancagem_Tests FAIL: %d of %d asserts",
                    g_failures,g_passes+g_failures);
  }

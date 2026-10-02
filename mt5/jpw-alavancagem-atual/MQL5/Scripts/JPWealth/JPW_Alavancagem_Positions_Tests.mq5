#property copyright "JP Wealth"
#property version "1.150"
#property description "Synthetic-only positions readmodel and same-core leverage assertions."
#include <JPWealth/JPW_Alavancagem_Positions.mqh>
int g_positions_pass=0,g_positions_fail=0;
void PositionsCheck(const bool ok,const string name)
  {
   if(ok) { g_positions_pass++; Print("PASS: ",name); }
   else { g_positions_fail++; Print("FAIL: ",name); }
  }
void PositionsFixture(JPWPosition &position,JPWInstrument &instrument,JPWQuote &quote,
   const ulong ticket,const string symbol,const string base,const string profit,
   const double volume,const double mid,const long direction)
  {
   position.ticket=ticket; position.identifier=(long)ticket;
   position.symbol=symbol; position.volume=volume; position.direction=direction;
   instrument.symbol=symbol; instrument.base=base; instrument.profit=profit;
   instrument.calc_mode=SYMBOL_CALC_MODE_FOREX; instrument.contract_size=100000.0;
   instrument.underlying_verified=false;
   quote.symbol=symbol; quote.base=base; quote.profit=profit;
   quote.bid=mid; quote.ask=mid; quote.time_msc=1000000;
   quote.conversion_pair=true;
  }
void PositionsMetadata(JPWPosition &positions[],JPWPositionView &metadata[])
  {
   ArrayResize(metadata,ArraySize(positions));
   for(int i=0;i<ArraySize(positions);i++)
     {
      JPWPositionsClearRow(metadata[i]);
      metadata[i].ticket=positions[i].ticket; metadata[i].identifier=positions[i].identifier;
      metadata[i].symbol=positions[i].symbol; metadata[i].direction=positions[i].direction;
      metadata[i].volume=positions[i].volume; metadata[i].volume_digits=2;
      metadata[i].opened_msc=1000+i; metadata[i].updated_msc=1000+i;
      metadata[i].entry=1.1; metadata[i].entry_valid=true;
      metadata[i].sl=0; metadata[i].sl_valid=true; metadata[i].tp_valid=true;
     }
  }
void PositionsMathTests()
  {
   JPWPosition positions[]; JPWInstrument instruments[]; JPWQuote quotes[];
   double scales[],amounts[]; JPWRoute routes[];
   ArrayResize(positions,3); ArrayResize(instruments,3); ArrayResize(quotes,3); ArrayResize(scales,3);
   PositionsFixture(positions[0],instruments[0],quotes[0],1,"EURUSD","EUR","USD",0.1,1.1,POSITION_TYPE_BUY);
   PositionsFixture(positions[1],instruments[1],quotes[1],2,"EURUSD","EUR","USD",0.05,1.1,POSITION_TYPE_SELL);
   PositionsFixture(positions[2],instruments[2],quotes[2],3,"GBPUSD","GBP","USD",0.1,1.25,POSITION_TYPE_BUY);
   // A unique quote per exact symbol; duplicate position symbols reuse it.
   quotes[1]=quotes[2]; ArrayResize(quotes,2);
   for(int i=0;i<3;i++) scales[i]=1.0;
   bool estimated=false; long oldest=0; double gross=0;
   PositionsCheck(JPWGrossReading(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,estimated,oldest)==JPW_OK && JPWPositionsNear(gross,29000),"whole-account oracle 29000 USD");
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_OK && ArraySize(amounts)==3,"all positions use frozen production inputs");
   PositionsCheck(JPWPositionsNear(amounts[0],11000)&&JPWPositionsNear(amounts[1],5500)&&
      JPWPositionsNear(amounts[2],12500),"hedging directions do not compensate; multisymbol breakdown");
   double sum=0,value=0;
   for(int i=0;i<3;i++) { JPWLeverage(amounts[i],10000,value); sum+=value; }
   PositionsCheck(JPWPositionsNear(sum,2.9),"1.10x + 0.55x + 1.25x reconcile to 2.90x");
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,100,amounts)==JPW_CALC_ERROR && ArraySize(amounts)==0,"wrong total refuses partial breakdown");
   instruments[2].contract_size=0;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_UNSUPPORTED_CONTRACT && ArraySize(amounts)==0,"invalid instrument never publishes subtotal");
   instruments[2].contract_size=100000;
   positions[2].ticket=positions[0].ticket;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_CALC_ERROR,"duplicate ticket refuses breakdown");
   ArrayResize(positions,1); ArrayResize(instruments,1); ArrayResize(quotes,1); ArrayResize(scales,1);
   PositionsFixture(positions[0],instruments[0],quotes[0],10,"NZDUSD.m","NZD","USD",0.1,0.6,POSITION_TYPE_BUY);
   instruments[0].contract_size=1000; scales[0]=1;
   string fiat=""; double divisor=0;
   PositionsCheck(JPWAccountUnits(" usc ",fiat,divisor)&&fiat=="USD"&&divisor==100,"USC equity unit normalization");
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,60,amounts)==JPW_OK && JPWLeverage(amounts[0],10000/divisor,value)==JPW_OK &&
      JPWPositionsNear(value,0.6),"USC contract 1000 gives 0.60x without price scaling");
   instruments[0].contract_size=100000; scales[0]=0.01;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,60,amounts)==JPW_OK && JPWLeverage(amounts[0],100,value)==JPW_OK &&
      JPWPositionsNear(value,0.6),"USC cent contract 100000 x 0.01 gives same 0.60x");
   scales[0]=0;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,60,amounts)==JPW_UNVERIFIED_UNITS,"unverified USC scale remains unavailable");
   scales[0]=1; instruments[0].contract_size=1000; positions[0].volume=0.05;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,30,amounts)==JPW_OK,"remaining volume after partial close controls contribution");
   PositionsCheck(JPWLeverage(30,0,value)==JPW_BAD_EQUITY && JPWLeverage(30,-100,value)==JPW_BAD_EQUITY,
      "nonpositive equity is unavailable, not zero exposure");
   quotes[0].time_msc=100;
   PositionsCheck(JPWGrossReading(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,estimated,oldest)==JPW_OK&&estimated&&oldest==100,
      "old complete quote remains Estimated with source age");
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_OK,"Estimated breakdown preserves same quote");
   quotes[0].bid=0;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,30,amounts)==JPW_BAD_QUOTE&&ArraySize(amounts)==0,"missing quote is not a zero contribution");
   // Inverse route: the instrument quote validates price but isn't an FX route.
   ArrayResize(quotes,2); ArrayResize(routes,0);
   PositionsFixture(positions[0],instruments[0],quotes[0],20,"EURUSD","EUR","USD",0.1,1.2,POSITION_TYPE_BUY);
   quotes[0].conversion_pair=false;
   quotes[1]=quotes[0]; quotes[1].symbol="USDEUR"; quotes[1].base="USD"; quotes[1].profit="EUR";
   quotes[1].bid=0.8; quotes[1].ask=0.8; quotes[1].conversion_pair=true;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,12500,amounts)==JPW_OK,"inverse conversion reused from pure core");
   // Two legs EUR -> GBP -> USD, with different source timestamps.
   ArrayResize(routes,0);
   PositionsFixture(positions[0],instruments[0],quotes[0],21,"EURGBP","EUR","GBP",0.1,0.8,POSITION_TYPE_SELL);
   quotes[1]=quotes[0]; quotes[1].symbol="GBPUSD"; quotes[1].base="GBP"; quotes[1].profit="USD";
   quotes[1].bid=1.25; quotes[1].ask=1.25; quotes[1].time_msc=995000;
   PositionsCheck(JPWGrossReading(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,estimated,oldest)==JPW_OK&&JPWPositionsNear(gross,10000)&&oldest==995000,
      "two-step conversion and oldest leg are retained");
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_OK,"two-step frozen route reconciles");
   quotes[1].bid=0;
   PositionsCheck(JPWPositionsGrossBreakdown(positions,instruments,quotes,"USD",1000000,30,true,true,
      scales,routes,gross,amounts)==JPW_NO_CONVERSION&&ArraySize(amounts)==0,"failed conversion doesn't leak former amounts");
   PositionsCheck(!JPWPositionsNear(0,1e-300),"tiny nonzero exposure cannot reconcile to artificial zero");
  }
void PositionsReadmodelTests()
  {
   JPWPosition positions[]; JPWPositionView metadata[],reordered[];
   JPWInstrument instrument; JPWQuote quote;
   double amounts[]; ArrayResize(positions,3); ArrayResize(amounts,3);
   for(int i=0;i<3;i++)
     {
      PositionsFixture(positions[i],instrument,quote,(ulong)(i+1),"EURUSD","EUR","USD",0.1,1.1,POSITION_TYPE_BUY);
      amounts[i]=11000;
     }
   PositionsMetadata(positions,metadata);
   JPWPositionsInvalidate("synthetic start");
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",2,"opaque-account-A"),
      "live catalog stages without EA or a positive SL");
   PositionsCheck(JPWPositionsStageLeverage(10000,3.3,amounts),"contributions reconcile before acceptance");
   long sequence=100; JPWMetricSample sample;
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",3.3,true,"ratio",1,JPW_SAMPLE_CONFIRMED,
      "same-frozen-inputs",1000,1000000,10000);
   PositionsCheck(JPWPositionsPublish(sample,"N/A") && g_positions_view.sample_id==sample.id &&
      ArraySize(g_position_views)==3 && g_positions_view.account_key=="opaque-account-A",
      "catalog and financial contribution reuse accepted sample identity");
   PositionsCheck(g_position_views[0].sl==0&&g_position_views[0].sl_valid&&
      g_position_views[0].leverage_valid&&JPWPositionsNear(g_position_views[0].leverage,1.1),
      "missing SL does not invalidate leverage");
   const long kept=g_positions_view.sample_id;
   PositionsCheck(JPWPositionsViewCurrent("synthetic-chart-A",10001)&&
      !JPWPositionsViewCurrent("synthetic-chart-B",10001)&&sequence==101&&g_positions_view.sample_id==kept,
      "view lookup never mints samples and rejects changed chart context");
   ArrayResize(reordered,3); reordered[0]=metadata[2]; reordered[1]=metadata[0]; reordered[2]=metadata[1];
   PositionsCheck(JPWPositionsMetadataEqual(metadata,reordered)&&JPWPositionsMatchSnapshot(reordered,positions),
      "enumeration order does not change inventory identity");
   reordered[0].sl=0.9; reordered[0].updated_msc++;
   PositionsCheck(!JPWPositionsMetadataEqual(metadata,reordered),"SL update invalidates catalog overlay consistency");
   PositionsCheck(JPWPositionsViewFind(2,2)==1&&JPWPositionsViewFind(2,99)<0,"selection is ticket plus identifier");
   ArrayResize(positions,2); ArrayResize(metadata,2); ArrayResize(amounts,2);
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",2,"opaque-account-A")&&
      JPWPositionsStageLeverage(10000,2.2,amounts),"shrinking inventory stages 3 to 2");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",2.2,true,"ratio",1,JPW_SAMPLE_CONFIRMED,"terminal",1001,1000001,11000);
   PositionsCheck(JPWPositionsPublish(sample,"N/A")&&ArraySize(g_position_views)==2&&
      JPWPositionsViewFind(3,3)<0,"accepted shrink removes closed position instead of leaving ArrayCopy tail");
   ArrayResize(positions,0); ArrayResize(metadata,0); ArrayResize(amounts,0);
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",2,"opaque-account-A")&&
      JPWPositionsStageLeverage(10000,0,amounts),"confirmed empty inventory stages zero");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",0,true,"ratio",1,JPW_SAMPLE_CONFIRMED,"terminal",1002,1000002,12000);
   PositionsCheck(JPWPositionsPublish(sample,"N/A")&&ArraySize(g_position_views)==0&&
      g_positions_view.catalog_valid&&g_positions_view.leverage_valid&&g_positions_view.total_leverage==0,
      "accepted shrink 2 to 0 stays distinct from unavailable");
   ArrayResize(positions,1); ArrayResize(amounts,1); amounts[0]=11000;
   PositionsFixture(positions[0],instrument,quote,9007199254740991,"EURUSD","EUR","USD",0.125,1.1,POSITION_TYPE_BUY);
   PositionsMetadata(positions,metadata); metadata[0].volume_digits=3;
   metadata[0].entry_valid=false; metadata[0].sl_valid=false; metadata[0].tp_valid=false;
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",0,"opaque-account-A"),
      "netting catalog permits absent optional prices");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",0,false,"ratio",0,JPW_SAMPLE_UNAVAILABLE,"terminal",1003,0,13000);
   PositionsCheck(JPWPositionsPublish(sample,"Perfil USC indisponível")&&g_positions_view.catalog_valid&&
      !g_position_views[0].leverage_valid&&g_positions_view.margin_mode==0&&
      g_position_views[0].ticket==9007199254740991&&g_position_views[0].volume_digits==3,
      "failed finance keeps full ticket, volume and netting inventory visible");
   PositionsCheck(JPWPositionsViewCurrent("synthetic-chart-A",13001)&&
      !JPWPositionsViewCurrent("synthetic-chart-A",43001),"catalog expires independently of a financial number");
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",0,"opaque-account-A")&&
      !JPWPositionsStageLeverage(10000,10,amounts),"mismatched contributions cannot be published as complete");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",10,true,"ratio",1,JPW_SAMPLE_CONFIRMED,"terminal",1004,1000000,14000);
   PositionsCheck(JPWPositionsPublish(sample,"Reconciliação recusada")&&!g_positions_view.leverage_valid,
      "catalog survives refused numerical reconciliation");
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",0,"opaque-account-A")&&
      JPWPositionsStageLeverage(10000,1.1,amounts),"valid netting contribution stages aggregate");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",2.2,true,"ratio",1,JPW_SAMPLE_CONFIRMED,"terminal",1005,1000000,15000);
   PositionsCheck(JPWPositionsPublish(sample,"Outro total")&&!g_positions_view.leverage_valid,
      "different accepted account total does not reuse staged numbers");
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",0,"opaque-account-A")&&
      JPWPositionsStageLeverage(10000,1.1,amounts),"valid contribution can be re-staged");
   JPWSampleAccept(sample,sequence,"synthetic-chart-A",1.1,true,"ratio",2,JPW_SAMPLE_ESTIMATED,"terminal-cache",1006,999000,16000);
   PositionsCheck(JPWPositionsPublish(sample,"N/A")&&g_position_views[0].quality==2&&
      g_position_views[0].source_time_msc==999000,"Estimated quality and same source time propagate without becoming Current");
   PositionsCheck(JPWPositionsStageCatalog(metadata,positions,"synthetic-chart-A",0,"opaque-account-A"),"stage before account switch");
   JPWSampleAccept(sample,sequence,"synthetic-chart-B",1.1,true,"ratio",1,JPW_SAMPLE_CONFIRMED,"terminal",1007,1000000,17000);
   PositionsCheck(!JPWPositionsPublish(sample,"Conta alterada")&&ArraySize(g_position_views)==0&&
      !g_positions_view.catalog_valid,"account switch clears visible and staged old rows");
   JPWPositionsInvalidate("Vencido");
   PositionsCheck(!g_positions_view.catalog_valid&&ArraySize(g_position_views)==0,
      "expiry/context invalidation does not fabricate a zero catalog");
  }
void OnStart()
  {
   PositionsMathTests(); PositionsReadmodelTests();
   Print("JPW Positions: ",g_positions_pass," PASS / ",g_positions_fail," FAIL");
  }

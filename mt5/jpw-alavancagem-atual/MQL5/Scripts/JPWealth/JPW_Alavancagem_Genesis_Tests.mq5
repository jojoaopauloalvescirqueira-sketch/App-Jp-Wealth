#property copyright "JP Wealth"
#property version   "1.30"
#property description "Testes sinteticos puros da referencia Genesis e distancia ao SL."

#include <JPWealth/JPW_Alavancagem_Genesis_Core.mqh>

// Nenhuma leitura de conta, arquivo ou grafico; nenhuma negociacao.
int g_genesis_passes=0;
int g_genesis_failures=0;

void JPWGenesisAssert(const bool condition,const string label)
  {
   if(condition) g_genesis_passes++;
   else
     {
      g_genesis_failures++;
      Print("FAIL: ",label);
     }
  }

void JPWGenesisNear(const double actual,const double expected,
                    const string label)
  {
   JPWGenesisAssert(MathIsValidNumber(actual) &&
                    MathAbs(actual-expected)<=
                    1e-8*MathMax(1.0,MathAbs(expected)),label);
  }

void JPWGenesisFixture(JPWGenesisPosition &position,const ulong ticket,
                       const long identifier,const string symbol,
                       const long direction,const long opened_msc,
                       const double sl,const double volume=0.1,
                       const long updated_msc=0)
  {
   position.ticket=ticket;
   position.identifier=identifier;
   position.symbol=symbol;
   position.direction=direction;
   position.opened_msc=opened_msc;
   position.sl=sl;
   position.volume=volume;
   position.updated_msc=updated_msc;
  }

void JPWGenesisTestSelection()
  {
   JPWGenesisPosition positions[];
   JPWGenesisPosition chosen;
   ArrayResize(positions,0);
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_NONE && chosen.ticket==0,
                    "no positions never selects a reference");
   ArrayResize(positions,3);
   JPWGenesisFixture(positions[0],15,115,"NZDUSD",POSITION_TYPE_BUY,3000,0.54);
   JPWGenesisFixture(positions[1],17,117,"NZDUSD",POSITION_TYPE_BUY,1000,0.55);
   JPWGenesisFixture(positions[2],16,116,"NZDUSD",POSITION_TYPE_BUY,2000,0.56);
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_OK && chosen.ticket==17 &&
                    chosen.identifier==117 && chosen.opened_msc==1000,
                    "automatic selects unique oldest, not array order or SL");
   JPWGenesisAssert(JPWGenesisSelect(positions,16,chosen)==
                    JPW_GENESIS_SELECT_OK && chosen.ticket==16 &&
                    chosen.identifier==116,
                    "explicit ticket selects requested open position");
   JPWGenesisAssert(JPWGenesisSelect(positions,88,chosen)==
                    JPW_GENESIS_SELECT_NOT_FOUND && chosen.ticket==0,
                    "missing explicit ticket cannot fall back to automatic");

   positions[2].symbol="NZDUSD.m";
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_AMBIGUOUS,
                    "exact symbol suffix creates another group");
   JPWGenesisAssert(JPWGenesisSelect(positions,16,chosen)==
                    JPW_GENESIS_SELECT_OK && chosen.symbol=="NZDUSD.m",
                    "explicit ticket works across groups");
   positions[2].symbol="NZDUSD";
   positions[2].direction=POSITION_TYPE_SELL;
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_AMBIGUOUS,
                    "opposite direction creates another group");
   positions[2].direction=POSITION_TYPE_BUY;
   positions[2].opened_msc=1000;
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_AMBIGUOUS,
                    "oldest opening time tie is not broken by ticket");
   positions[2].opened_msc=0;
   JPWGenesisAssert(JPWGenesisSelect(positions,0,chosen)==
                    JPW_GENESIS_SELECT_INVALID,
                    "missing opening time blocks automatic selection");
   JPWGenesisAssert(JPWGenesisSelect(positions,16,chosen)==
                    JPW_GENESIS_SELECT_INVALID,
                    "missing time blocks explicit persistence too");
   positions[2].opened_msc=2000;
   positions[2].ticket=17;
   JPWGenesisAssert(JPWGenesisSelect(positions,17,chosen)==
                    JPW_GENESIS_SELECT_AMBIGUOUS,
                    "duplicate live ticket cannot select arbitrarily");
   positions[2].ticket=16;

   JPWGenesisPosition found;
   JPWGenesisAssert(JPWGenesisFindByIdentifier(positions,117,found) &&
                    found.ticket==17,
                    "persisted identifier finds selected position");
   positions[1].ticket=99;
   positions[1].volume=0.05;
   positions[1].updated_msc=4000;
   JPWGenesisAssert(JPWGenesisFindByIdentifier(positions,117,found) &&
                    found.ticket==99 && found.volume==0.05,
                    "ticket change and partial close retain identifier");
   positions[1].direction=POSITION_TYPE_SELL;
   JPWGenesisAssert(JPWGenesisFindByIdentifier(positions,117,found) &&
                    found.direction==POSITION_TYPE_SELL,
                    "netting reversal remains visible to caller for blocking");
   positions[2].identifier=117;
   JPWGenesisAssert(!JPWGenesisFindByIdentifier(positions,117,found),
                    "duplicate identifier cannot identify one reference");
   positions[2].identifier=116;
   ArrayResize(positions,0);
   JPWGenesisAssert(!JPWGenesisFindByIdentifier(positions,117,found),
                    "closed reference cannot be replaced by successor");
  }

void JPWGenesisTestDistance()
  {
   double distance=0.0,points=0.0,percent=0.0,pips=0.0;
   bool has_pips=false;
   JPW_GENESIS_DISTANCE state=JPWGenesisDistance(
      POSITION_TYPE_BUY,0.568,0.5682,0.548,0.00001,5,0.00001,
      "NZDUSD","NZDUSD",0.0001,distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && has_pips,
                    "buy uses Bid and exact pip configuration");
   JPWGenesisNear(distance,0.02,"buy price distance");
   JPWGenesisNear(points,2000.0,"buy points");
   JPWGenesisNear(percent,3.52112676056338,"buy percent of Bid");
   JPWGenesisNear(pips,200.0,"buy configured pips");

   state=JPWGenesisDistance(POSITION_TYPE_SELL,1.0998,1.1,1.12,
                            0.00001,5,0.00001,"EURUSD","EURUSD",0.0001,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && has_pips,
                    "sell uses Ask rather than Bid");
   JPWGenesisNear(percent,1.818181818181818,"sell percent of Ask");
   JPWGenesisNear(pips,200.0,"sell configured pips");

   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.09,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && !has_pips,
                    "default exposes points and percent, never guesses pips");
   JPWGenesisNear(distance,0.01,"buy spread does not use Ask");
   state=JPWGenesisDistance(POSITION_TYPE_SELL,1.1,1.1002,1.1102,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisNear(distance,0.01,"sell spread does not use Bid");

   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.11,1.1102,1.105,
                            0.00001,5,0.00001,"EURUSD","EURUSD.m",0.0001,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && !has_pips,
                    "SL moved above entry stays a price distance; suffix mismatch blocks pip");
   JPWGenesisNear(points,500.0,"protected-profit SL positive distance");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.11,1.1102,1.105,
                            0.00001,5,0.00001,"EURUSD","EURUSD",0.000015,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && !has_pips,
                    "pip size not aligned to tick stays disabled");

   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.1,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_REACHED,
                    "BUY at SL is level reached, not execution proof");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.099,1.0992,1.1,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_PASSED,
                    "BUY beyond SL is level passed, not execution proof");
   state=JPWGenesisDistance(POSITION_TYPE_SELL,1.0998,1.1,1.1,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_REACHED,
                    "SELL at SL is level reached");
   state=JPWGenesisDistance(POSITION_TYPE_SELL,1.1008,1.101,1.1,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_PASSED,
                    "SELL beyond SL is level passed");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,0.0,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_NO_SL,
                    "zero SL is retained reference without stop");

   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,-1.0,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_INVALID,
                    "negative SL is unavailable");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.0998,1.09,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_INVALID,
                    "crossed Bid Ask is unavailable");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.09,
                            0.0,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_INVALID,
                    "missing point is unavailable");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.09,
                            0.00001,5,0.0,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_INVALID,
                    "missing tick size is unavailable");
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.09,
                            0.00001,-1,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_INVALID,
                    "invalid precision is unavailable");

   const double tiny=1.0e-8;
   state=JPWGenesisDistance(POSITION_TYPE_BUY,1.1,1.1002,1.1-tiny,
                            0.00001,5,0.00001,"EURUSD","",0.0,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && points>0.0,
                    "positive sub-point distance is not a false zero");

   // USC changes account money units, never Bid/Ask, SL, points or pips.
   state=JPWGenesisDistance(POSITION_TYPE_BUY,0.568,0.5682,0.548,
                            0.00001,5,0.00001,"NZDUSD.m","NZDUSD.m",0.0001,
                            distance,points,percent,pips,has_pips);
   JPWGenesisAssert(state==JPW_GENESIS_DISTANCE_POSITIVE && has_pips,
                    "USC symbol price distance uses no cent multiplier");
   JPWGenesisNear(pips,200.0,"USC account still 200 pips");
  }

void OnStart()
  {
   JPWGenesisTestSelection();
   JPWGenesisTestDistance();
   if(g_genesis_failures==0)
      PrintFormat("JPW_Alavancagem_Genesis_Tests PASS: %d asserts",
                  g_genesis_passes);
   else
      PrintFormat("JPW_Alavancagem_Genesis_Tests FAIL: %d of %d asserts",
                  g_genesis_failures,g_genesis_passes+g_genesis_failures);
  }

#property script_show_inputs
#property description "Pure synthetic 7x supervisor planner tests. Does not access account or send requests."
#include <JPWealth/JPW_Genetrix_Risk_Core.mqh>
int g_risk_test_pass=0,g_risk_test_fail=0;
void JPWRiskAssert(const bool condition,const string name)
  { if(condition) { g_risk_test_pass++; Print("PASS ",name); }
    else { g_risk_test_fail++; Print("PRODUCT_FAIL ",name); } }
void JPWRiskFixturePosition(JPWRiskPosition &p,const ulong ticket,const long id,
                            const long opened,const double volume,const double gross)
  { p.ticket=ticket; p.identifier=id; p.opened_msc=opened; p.symbol="EURUSD.fixture";
    p.direction=POSITION_TYPE_BUY; p.volume=volume; p.gross=gross; }
void JPWRiskFixturePending(JPWRiskPending &p,const ulong ticket,const long time,const double gross)
  { p.ticket=ticket; p.setup_msc=time; p.symbol="EURUSD.fixture"; p.type=2;
    p.volume=0.01; p.entry=1.2; p.trigger=1.2; p.gross=gross; }
void JPWRiskFixtureSample(JPWRiskSnapshot &s,const double equity,const double gross,const double pg=0.0)
  { s.valid=true; s.current=true; s.pending_valid=true; s.hedging=true; s.fifo=false;
    s.equity=equity; s.gross=gross; s.pending_gross=pg; s.leverage=gross/equity;
    s.projected_leverage=(gross+pg)/equity; s.observed_utc=1000; }
void OnStart()
  {
   JPWRiskMachine m; JPWRiskReset(m); JPWRiskSnapshot s; JPWRiskAction a;
   JPWRiskPosition p[]; JPWRiskPending q[]; string why="";
   ArrayResize(p,1); ArrayResize(q,0);
   JPWRiskFixturePosition(p[0],10,10,100,0.1,6999); JPWRiskFixtureSample(s,1000,6999);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_NONE,"RIS-AC01 below7 none");
   p[0].gross=7000; JPWRiskFixtureSample(s,1000,7000);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_NONE,"RIS-AC02 exact7 none");
   p[0].gross=7000.01; JPWRiskFixtureSample(s,1000,7000.01);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CLOSE && a.volume==0.1,"RIS-AC03 raw above7 whole");
   p[0].gross=7000.0000001; JPWRiskFixtureSample(s,1000,7000.0000001);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CLOSE,"RIS-AC04 no display epsilon");
   ArrayResize(p,3);
   JPWRiskFixturePosition(p[0],10,10,100,0.1,2000); JPWRiskFixturePosition(p[1],20,20,200,0.2,2500);
   JPWRiskFixturePosition(p[2],30,30,300,0.3,2000); JPWRiskFixtureSample(s,900,6500);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.ticket==30 && a.volume==0.3,"RIS-AC05 newest whole not largest");
   ArrayResize(p,2); JPWRiskFixtureSample(s,900,4500);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_NONE && s.leverage==5.0,"RIS-AC05 confirmed static after5x");
   ArrayResize(p,1); JPWRiskFixturePosition(p[0],10,10,100,0.1,6000); ArrayResize(q,2);
   JPWRiskFixturePending(q[0],100,100,500); JPWRiskFixturePending(q[1],200,200,800);
   JPWRiskFixtureSample(s,1000,6000,1300);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CANCEL && a.ticket==200,"RIS-AC06 aggregate cancel newest");
   ArrayResize(q,1); JPWRiskFixtureSample(s,1000,6000,500);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_NONE,"RIS-AC06 minimal prefix stop preserve older");
   ArrayResize(q,2); JPWRiskFixturePending(q[0],100,100,100); JPWRiskFixturePending(q[1],200,200,200);
   p[0].gross=6500; JPWRiskFixtureSample(s,900,6500,300);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CANCEL && a.ticket==200,"RIS-AC07 zero budget newest pending first");
   ArrayResize(q,1); JPWRiskFixtureSample(s,900,6500,100);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CANCEL && a.ticket==100,"RIS-AC07 zero budget next pending");
   ArrayResize(q,0); JPWRiskFixtureSample(s,900,6500);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CLOSE,"RIS-AC07 then positions");
   ArrayResize(q,1); JPWRiskFixturePending(q[0],200,200,300); JPWRiskFixtureSample(s,900,6500,300);
   m.armed=true; a.kind=JPW_RISK_CANCEL; a.ticket=200; a.symbol=q[0].symbol;
   JPWRiskAssert(JPWRiskBegin(m,a,"nonce1",1000),"RIS-AC08 durable intent begin");
   JPWRiskApplyOutcome(m,JPW_RISK_REFUSED,0.0);
   JPWRiskAssert(m.cancel_refused && m.protection_incomplete && JPWRiskPlan(s,p,q,m,a,why) &&
                  a.kind==JPW_RISK_CLOSE,"RIS-AC08 cancel refused proceeds position");
   JPWRiskAssert(JPWRiskBegin(m,a,"nonce2",1001),"RIS-AC09 close intent begin");
   JPWRiskApplyOutcome(m,JPW_RISK_REFUSED,0.0);
   JPWRiskAssert(!m.armed && m.phase==JPW_RISK_PAUSED_LIFO && !JPWRiskPlan(s,p,q,m,a,why),
                  "RIS-AC09 refusal pause no older skip");
   JPWRiskReset(m); m.armed=true; ArrayResize(q,0); JPWRiskFixtureSample(s,900,6500);
   JPWRiskPlan(s,p,q,m,a,why); JPWRiskBegin(m,a,"nonce3",1002);
   JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why) && !JPWRiskBegin(m,a,"duplicate",1003),"RIS-AC10 unknown forbids all new requests");
   JPWRiskApplyOutcome(m,JPW_RISK_PARTIAL,0.05); p[0].volume=0.05; p[0].gross=3000;
   JPWRiskFixtureSample(s,900,3000);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.kind==JPW_RISK_CLOSE && a.ticket==10 && a.volume==0.05,
                  "RIS-AC11 finish residual even below7");
   JPWRiskReset(m); s.hedging=false;
   JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why),"RIS-AC12 netting unavailable");
   s.hedging=true; s.fifo=true;
   JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why),"RIS-AC12 FIFO conflict no fallback"); s.fifo=false;
   a.kind=JPW_RISK_CLOSE; a.ticket=10;
   JPWRiskAssert(!JPWRiskBegin(m,a,"observe",1004),"RIS-AC13 unarmed begin denied");
   s.current=false; JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why),"RIS-AC17 Estimated no action"); s.current=true;
   s.pending_valid=false; JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why),"RIS-AC17 missing pending no partial aggregate");
   s.pending_valid=true; s.equity=0.0;
   JPWRiskAssert(!JPWRiskPlan(s,p,q,m,a,why),"RIS-AC17 invalid equity no action");
   ArrayResize(p,2); JPWRiskFixturePosition(p[0],99,10,500,0.1,4000);
   JPWRiskFixturePosition(p[1],50,20,500,0.2,4000); JPWRiskFixtureSample(s,1000,8000);
   JPWRiskAssert(JPWRiskPlan(s,p,q,m,a,why) && a.ticket==50 && a.identifier==20,"RIS-AC18 tie by identifier not ticket");
   JPWPosition row; row.ticket=1; row.identifier=1; row.symbol="EURUSD.fixture"; row.direction=POSITION_TYPE_BUY; row.volume=1.0;
   JPWInstrument instrument; instrument.symbol=row.symbol; instrument.calc_mode=SYMBOL_CALC_MODE_FOREX;
   instrument.base="EUR"; instrument.profit="USD"; instrument.contract_size=100000; instrument.underlying_verified=false;
   JPWQuote quotes[]; JPWRoute routes[]; ArrayResize(quotes,1); ArrayResize(routes,0);
   quotes[0].symbol=row.symbol; quotes[0].base="EUR"; quotes[0].profit="USD";
   quotes[0].bid=1.10; quotes[0].ask=1.10; quotes[0].time_msc=1000000; quotes[0].conversion_pair=true;
   double gross=0.0; bool estimated=false;
   JPWRiskAssert(JPWRiskGrossAtEntry(row,instrument,quotes,"USD",1.20,1.0,1001000,true,true,routes,gross,estimated) &&
      MathAbs(gross-120000)<1e-8 && quotes[0].bid==1.10 && !estimated,"RIS-FX01 planned quote120k not current110k immutable quote");
   JPWRiskAssert(JPWRiskGrossAtEntry(row,instrument,quotes,"EUR",1.20,1.0,1001000,true,true,routes,gross,estimated) &&
      gross==100000,"RIS-FX02 account base notional invariant");
   Print("HOST/PURE_RESULTS ",g_risk_test_pass," PASS / ",g_risk_test_fail," FAIL; native compile/runtime NOT_RUN unless separately executed");
  }

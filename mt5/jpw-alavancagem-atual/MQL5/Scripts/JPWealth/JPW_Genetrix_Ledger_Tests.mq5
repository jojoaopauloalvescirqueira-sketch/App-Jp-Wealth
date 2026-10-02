#property strict
#property script_show_inputs
#include <JPWealth/JPW_Genetrix_Ledger_Core.mqh>
// Synthetic fixtures only. No account reads, files, prices or trade requests.
// The host runner compiles these same raw vectors and the production Core,
// then compares its results with the independently frozen Decimal oracles.
int JPWLedgerTestFailures=0;
void JPWLedgerTestAssert(const bool ok,const string label)
  { if(!ok) { JPWLedgerTestFailures++; Print("LEDGER_TEST_FAIL ",label); } }
void JPWLedgerTestDeal(JPWLedgerDeal &d[],const long ticket,const long order,const long id,
   const long time,const int side,const int entry,const double volume,
   const double profit,const double swap,const double comm,const double fee,
   const int kind=1,const int reason=0,const string symbol="TEST")
  {
   int n=ArraySize(d); ArrayResize(d,n+1);
   d[n].ticket=ticket; d[n].order_ticket=order; d[n].position_id=id; d[n].time_msc=time;
   d[n].symbol=symbol; d[n].kind=kind; d[n].side=side; d[n].entry=entry; d[n].reason=reason;
   d[n].volume=volume; d[n].profit=profit; d[n].swap=swap; d[n].commission=comm; d[n].fee=fee; d[n].deleted=0; d[n].adjustment_of=0;
  }
void JPWLedgerTestLive(JPWLedgerPosition &p[],const long id,const double volume,
   const double profit,const double swap,const long ticket=0,const string symbol="TEST",const int side=1)
  {
   int n=ArraySize(p); ArrayResize(p,n+1); p[n].identifier=id; p[n].ticket=(ticket>0 ? ticket : id);
   p[n].opened_msc=1000; p[n].symbol=symbol; p[n].side=side;
   p[n].volume=volume; p[n].profit=profit; p[n].swap=swap;
  }
void JPWLedgerTestOrder(JPWLedgerOrder &o[],const int state=1)
  {
   ArrayResize(o,1); o[0].ticket=2000; o[0].setup_msc=2000;
   o[0].done_msc=(state==1 ? 0 : 4000); o[0].symbol="TEST"; o[0].side=1; o[0].state=state; o[0].volume=0.02;
  }
void JPWLedgerTestView(JPWLedgerView &v,const double balance)
  {
   JPWLedgerClearView(v); v.account_key="synthetic"; v.currency="USD"; v.publisher_token="synthetic";
   v.margin_mode=JPW_LEDGER_HEDGING; v.balance=balance; v.quality=1; v.healthy=true;
   // Completeness is an explicit synthetic fixture precondition, NEVER a
   // conclusion from HistorySelect or an operator switch in the Accountant.
   v.history_complete=true; v.costs_complete=true; v.observed_utc=100; v.observed_mono_ms=100;
  }
string JPWLedgerTestFixture(const int n,JPWLedgerDeal &d[],JPWLedgerOrder &o[],
   JPWLedgerPosition &p[],JPWLedgerView &v)
  {
   ArrayResize(d,0); ArrayResize(o,0); ArrayResize(p,0); JPWLedgerTestView(v,1000);
   string id="";
   if(n==0 || n==15)
     {
      double scale=(n==15 ? 100.0 : 1.0); v.balance=997.8*scale;
      if(n==15) v.currency="USC";
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.1,0,0,-2*scale,-0.2*scale);
      JPWLedgerTestLive(p,700,0.1,50*scale,-0.5*scale);
      return(n==0 ? "LED-AC01" : "LED-AC12");
     }
   if(n==4 || n==5)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.1,0,0,0,0);
      JPWLedgerTestDeal(d,101,701,700,3000,-1,1,0.1,40,0,0,0);
      JPWLedgerTestOrder(o,n==4 ? 1 : 3); v.balance=(n==4 ? 1040 : 1038.9);
      if(n==5) { JPWLedgerTestDeal(d,102,2000,2000,4000,1,0,0.02,0,0,-1,-0.1); JPWLedgerTestLive(p,2000,0.02,8,0); }
      return(n==4 ? "LED-AC04" : "LED-AC04B");
     }
   if(n==6)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.01,0,0,-0.5,-0.05);
      JPWLedgerTestLive(p,700,0.01,0,0); v.balance=999.45; return("LED-AC05");
     }
   if(n==9 || n==10)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.1,0,0,-2,-0.2);
      JPWLedgerTestDeal(d,101,701,700,2000,-1,1,0.1,0,-1.5,0,0,1,1);
      JPWLedgerTestDeal(d,102,900,700,3000,1,0,0.1,0,0,n==9 ? 0 : -2,n==9 ? 0 : -0.2,1,1);
      JPWLedgerTestLive(p,700,0.1,40,0,755); v.balance=(n==9 ? 996.3 : 994.1);
      return(n==9 ? "LED-AC07" : "LED-AC07B");
     }
   if(n==14)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,-1,0,0.1,0,0,0,0);
      JPWLedgerTestDeal(d,101,701,700,2000,1,1,0.1,0,0,-1,0,5);
      JPWLedgerTestDeal(d,102,0,700,2100,0,0,0,20,0,0,0,3);
      d[2].adjustment_of=101; // explicit synthetic correction evidence
      v.balance=1019; return("LED-AC11");
     }
   if(n==16 || n==17)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.1,0,0,0,0,1,0,"GROUP-A");
      JPWLedgerTestDeal(d,101,800,800,1000,-1,0,0.1,0,0,0,0,1,0,"GROUP-B");
      JPWLedgerTestDeal(d,102,0,700,2000,0,0,0,10,0,0,0,2);
      JPWLedgerTestDeal(d,103,0,800,2000,0,0,0,20,0,0,0,2);
      JPWLedgerTestLive(p,700,0.1,-15,0,0,"GROUP-A",1);
      JPWLedgerTestLive(p,800,0.1,7,0,0,"GROUP-B",-1); v.balance=1030;
      return(n==16 ? "LED-AC13A" : "LED-AC13B");
     }
   if(n==18)
     {
      JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.01,0,0,-0.5,-0.05);
      JPWLedgerTestDeal(d,101,800,800,1000,1,0,0.01,0,0,-0.5,-0.05);
      JPWLedgerTestLive(p,700,0.01,0,0); JPWLedgerTestLive(p,800,0.01,0,0);
      v.balance=998.9; return("LED-AC14");
     }
   JPWLedgerTestDeal(d,100,700,700,1000,1,0,0.1,0,0,n==12 ? -2.4 : -2,-0.2);
   JPWLedgerTestDeal(d,101,701,700,2000,-1,1,0.04,20,-0.2,-0.8,-0.08);
   v.balance=(n==12 ? 1016.32 : 1016.72);
   if(n==2 || n==3)
     {
      JPWLedgerTestDeal(d,102,800,800,2500,1,0,0.02,0,0,-1,-0.1);
      JPWLedgerTestDeal(d,103,702,700,3000,-1,1,0.06,30,-0.3,-1.2,-0.12);
      JPWLedgerTestLive(p,800,0.02,-12,-0.4); v.balance=1044;
      if(n==3) { JPWLedgerTestDeal(d,104,900,900,4000,1,0,0.01,0,0,-0.5,-0.05);
         JPWLedgerTestLive(p,900,0.01,5,0); v.balance=1043.45; }
      return(n==2 ? "LED-AC03" : "LED-AC03B");
     }
   if(n==13)
     {
      JPWLedgerTestDeal(d,103,702,700,3000,-1,1,0.06,30,-0.3,-1.2,-0.12);
      v.balance=1045.1; return("LED-AC10");
     }
   JPWLedgerTestLive(p,700,0.06,30,-0.3,n==11 ? 755 : 700);
   if(n==7 || n==8) { JPWLedgerTestDeal(d,102,0,n==7 ? 0 : 700,3000,0,0,0,-3,0,0,0,2);
      v.balance=1013.72; return(n==7 ? "LED-AC06" : "LED-AC06B"); }
   if(n==11) return("LED-AC08"); if(n==12) return("LED-AC09");
   return("LED-AC02");
  }
void JPWLedgerTestEmit(const string id,JPWLedgerCycle &c,JPWLedgerView &v)
  {
   Print("LEDGER_VECTOR|",id,"|",DoubleToString(c.realized_price+c.realized_swap+c.commissions+c.fees,16),
      "|",DoubleToString(c.unrealized_price+c.unrealized_swap,16),"|",DoubleToString(c.compensated,16),
      "|",DoubleToString(c.percent,16),"|",DoubleToString(v.balance,16),"|",c.state,"|",c.amount_valid,"|",c.partial,"|",c.genesis_ambiguous,
      "|",c.members_available,"|",c.member_identifiers);
  }
void JPWLedgerTestNumeric(const int n,const string id,JPWLedgerCycle &c)
  {
   // Frozen oracle values copied for the optional native synthetic script.
   // The host compares actual outputs against the separate immutable JSON;
   // these arrays are not used as the host's independent reference.
   double expected_r[19]={-2.20,16.72,44,43.45,40,38.90,-0.55,16.72,13.72,-3.70,-5.90,16.72,16.32,45.10,19,-220,10,20,-1.10};
   double expected_u[19]={49.50,29.70,-12.40,-7.40,0,8,0,29.70,29.70,40,40,29.70,29.70,0,0,4950,-15,7,0};
   double expected_c[19]={47.30,46.42,31.60,36.05,40,46.90,-0.55,46.42,43.42,36.30,34.10,46.42,46.02,45.10,19,4730,-5,27,-1.10};
   double expected_pct[19]={4.74,4.57,3.03,3.45,3.85,4.51,-0.06,4.58,4.28,3.64,3.43,4.57,4.53,4.32,1.86,4.74,-0.49,2.62,-0.11};
   JPWLedgerTestAssert(JPWLedgerNear(c.realized_price+c.realized_swap+c.commissions+c.fees,expected_r[n]),id+" realized");
   JPWLedgerTestAssert(JPWLedgerNear(c.unrealized_price+c.unrealized_swap,expected_u[n]),id+" floating");
   JPWLedgerTestAssert(JPWLedgerNear(c.compensated,expected_c[n]),id+" compensated");
   JPWLedgerTestAssert(DoubleToString(c.percent,2)==DoubleToString(expected_pct[n],2),id+" percent display");
   JPWLedgerTestAssert(c.amount_valid && c.percent_valid && c.partial==(n==7) && c.genesis_ambiguous==(n==18),id+" flags");
   if(n==4) JPWLedgerTestAssert(c.state==2,id+" only pending");
   if(n==13 || n==14) JPWLedgerTestAssert(c.state==3,id+" accounting closed");
   if(n==2 || n==3 || n==5) JPWLedgerTestAssert(c.genesis_identifier==700,id+" original genesis");
   string expected_members="700";
   if(n==2 || n==18) expected_members="700,800";
   if(n==3) expected_members="700,800,900";
   if(n==5) expected_members="700,2000";
   if(n==17) expected_members="800";
   JPWLedgerTestAssert(c.members_available && JPWLedgerMemberListValid(c) &&
      c.member_identifiers==expected_members,id+" all observed identifiers");
  }
void OnStart()
  {
   JPWLedgerCycle empty_members; JPWLedgerClearCycle(empty_members);
   empty_members.members_available=true;
   JPWLedgerTestAssert(JPWLedgerMemberListValid(empty_members),"pre-execution provisional empty observed list");
   empty_members.state=1; empty_members.open_positions=1; empty_members.amount_valid=true;
   JPWLedgerTestAssert(JPWLedgerMemberListStructureValid(empty_members) && !JPWLedgerMemberListValid(empty_members),
      "final open projection cannot have available empty observed list");
   for(int n=0;n<19;n++)
     {
      JPWLedgerDeal d[]; JPWLedgerOrder o[]; JPWLedgerPosition p[]; JPWLedgerView v; JPWLedgerCycle c[]; string reason="";
      string id=JPWLedgerTestFixture(n,d,o,p,v);
      bool ok=JPWLedgerBuild(d,o,p,v,c,reason); JPWLedgerTestAssert(ok && ArraySize(c)>0,id);
      if(ok && ArraySize(c)>0) { int selected=(n==17 ? 1 : 0); JPWLedgerTestNumeric(n,id,c[selected]); JPWLedgerTestEmit(id,c[selected],v); }
     }
   Print("LEDGER_SYNTHETIC_RESULT failures=",JPWLedgerTestFailures,"; native terminal/account integration not exercised");
  }

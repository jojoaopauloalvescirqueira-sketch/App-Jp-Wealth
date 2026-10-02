#property strict
#property script_show_inputs
#include <JPWealth/JPW_PersonalHistory_Core.mqh>
// Synthetic Core assertions only; no terminal, account, trading or files.
int JPWPersonalTestFailures=0;
void JPWPersonalTestAssert(const bool ok,const string label)
  { if(!ok) { JPWPersonalTestFailures++; Print("PERSONAL_TEST_FAIL|",label); } }
void JPWPersonalTestCapture(JPWPersonalCapture &c,const long wall=1000,const ulong mono=1000000)
  {
   c.account_key="synthetic-account-A"; c.source="synthetic-fixture"; c.product_version="test";
   c.started_msc=wall*1000; c.finished_msc=wall*1000+1; c.wall_seconds=wall; c.mono_ms=mono;
   c.stable=true; c.connected=true; c.inventory_valid=true; c.quality=JPW_PERSONAL_CURRENT;
   c.balance=200; c.equity=200; c.credit=0; c.profit=0; c.margin=0; c.free_margin=200;
   c.margin_level=0; c.gross=1400; c.leverage_valid=true; c.units="USD"; c.details="synthetic";
  }
void JPWPersonalTestSubject(JPWPersonalSubject &s,const int kind=JPW_PERSONAL_POSITION,const string id="700",const double sl=0)
  {
   s.kind=kind; s.id=id; s.ticket=id; s.symbol="SYNTHETIC"; s.side=1; s.order_type=0;
   s.volume=0.1; s.price=1.1; s.sl=sl; s.tp=0; s.sl_readable=true; s.link_id=""; s.terminal_reason="";
  }
void OnStart()
  {
   JPWPersonalCapture c; JPWPersonalTestCapture(c);
   JPWPersonalSubject subjects[]; ArrayResize(subjects,1); JPWPersonalTestSubject(subjects[0]);
   JPWPersonalEpisode episodes[]; JPWPersonalEvent events[]; int due[];
   JPWPersonalTestAssert(JPWPersonalReconcile(c,subjects,episodes,events,due) && ArraySize(episodes)==1 && ArraySize(due)==1,
      "first observed absence");
   if(ArraySize(episodes)==1)
     {
      JPWPersonalMarkRequested(c,episodes[0]);
      c.wall_seconds=1059; c.mono_ms=1059000;
      JPWPersonalTestAssert(JPWPersonalReconcile(c,subjects,episodes,events,due) && ArraySize(due)==0,"no early repeat");
      c.wall_seconds=1060; c.mono_ms=1060000;
      JPWPersonalTestAssert(JPWPersonalReconcile(c,subjects,episodes,events,due) && ArraySize(due)==1,"repeat at sixty seconds");
      subjects[0].sl=1.05;
      JPWPersonalTestAssert(JPWPersonalReconcile(c,subjects,episodes,events,due) && ArraySize(due)==0 &&
         episodes[0].state==JPW_PERSONAL_SL_PRESENT,"stop placement resolves before repeat");
     }
   JPWPersonalPeak current,estimated; current.valid=false; estimated.valid=false; int changed=0;
   JPWPersonalTestCapture(c);
   JPWPersonalTestAssert(JPWPersonalPeakAccept(c,"synthetic-photo-1",current,estimated,changed) && current.leverage==7,
      "gross 1400 equity 200 equals seven");
   c.equity=175;
   JPWPersonalTestAssert(JPWPersonalPeakAccept(c,"synthetic-photo-2",current,estimated,changed) && current.leverage==8 &&
      current.snapshot=="synthetic-photo-2","equity falls without an entry");
   Print("PERSONAL_SYNTHETIC_RESULT|",JPWPersonalTestFailures,"|native terminal and notifications not exercised");
  }

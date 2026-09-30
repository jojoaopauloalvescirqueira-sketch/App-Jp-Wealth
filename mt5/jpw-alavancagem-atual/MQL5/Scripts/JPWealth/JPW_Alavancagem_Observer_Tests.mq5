#property copyright "JP Wealth"
#property version "1.60"
#property description "Testes sinteticos do observador; sem leitura de conta ou negocios reais."

#include <JPWealth/JPW_Alavancagem_RaizN_Observer.mqh>

int g_pass=0,g_fail=0;
void JPWObserverAssert(const bool condition,const string label)
  {
   if(condition) g_pass++;
   else { g_fail++; Print("FAIL: ",label); }
  }

void JPWTestDeal(JPWObserverDeal &deal,const long ticket,const int entry,
                 const int side,const double volume,const long time_msc)
  {
   deal.ticket=ticket; deal.order_ticket=(ticket==10 ? 555 : 1000+ticket);
   deal.position_id=555;
   deal.time_msc=time_msc; deal.entry=entry; deal.side=side;
   deal.symbol="SYNTH.EXACT"; deal.volume=volume; deal.price=100.0;
  }

void JPWObserverTestEpisodes()
  {
   JPWObserverDeal deals[];
   ArrayResize(deals,5);
   // Deliberately shuffled: arrival order is not an episode rule.
   JPWTestDeal(deals[0],12,DEAL_ENTRY_OUT,-1,0.4,120000);
   JPWTestDeal(deals[1],10,DEAL_ENTRY_IN,1,1.0,100000);
   JPWTestDeal(deals[2],14,DEAL_ENTRY_OUT,1,0.9,140000);
   JPWTestDeal(deals[3],13,DEAL_ENTRY_INOUT,-1,2.0,130000);
   JPWTestDeal(deals[4],11,DEAL_ENTRY_IN,1,0.5,110000);
   JPWObserverDeal start; string reason="";
   JPWObserverAssert(JPWObserverFindEpisode(deals,11,start,reason) &&
                     start.ticket==10,"addition retains first execution");
   JPWObserverAssert(JPWObserverFindEpisode(deals,12,start,reason) &&
                     start.ticket==10,"partial close retains first execution");
   JPWObserverAssert(JPWObserverFindEpisode(deals,13,start,reason) &&
                     start.ticket==13,"netting reversal begins new episode");
   string account="",first_key="",reverse_key="";
   JPWObserverAccountKey("SYNTH.SERVER",123,"USD","SYNTH.INSTALL",account);
   JPWObserverEpisodeKey(account,"SYNTH.EXACT",555,10,first_key);
   JPWObserverEpisodeKey(account,"SYNTH.EXACT",555,13,reverse_key);
   JPWObserverAssert(first_key!=reverse_key,
                     "netting reversal has a distinct immutable key");
   JPWObserverAssert(!JPWObserverFindEpisode(deals,14,start,reason),
                     "closed episode is not an open reference");
   JPWObserverDeal orphan[];
   ArrayResize(orphan,1);
   JPWTestDeal(orphan[0],99,DEAL_ENTRY_OUT,-1,1.0,100000);
   JPWObserverAssert(!JPWObserverFindEpisode(orphan,99,start,reason),
                     "missing opening history fails closed");
   JPWTestDeal(orphan[0],99,DEAL_ENTRY_IN,1,1.0,100000);
   orphan[0].order_ticket=555;
   orphan[0].price=0.0;
   JPWObserverAssert(!JPWObserverFindEpisode(orphan,99,start,reason),
                     "invalid executed price fails closed");
   JPWObserverDeal added_as_first[];
   ArrayResize(added_as_first,1);
   JPWTestDeal(added_as_first[0],150,DEAL_ENTRY_IN,1,0.5,150000);
   JPWObserverAssert(!JPWObserverFindEpisode(added_as_first,150,start,reason) &&
                     reason=="Ordem original de abertura ausente do historico",
                     "history beginning at an addition cannot become origin");
   added_as_first[0].order_ticket=555;
   JPWObserverAssert(JPWObserverFindEpisode(added_as_first,150,start,reason) &&
                     start.ticket==150,
                     "opening order anchor permits a complete initial deal");
   JPWObserverAssert(JPWObserverInitialPositionMatches(start,555,
                     "SYNTH.EXACT",1,150000),
                     "live initial position agrees with first deal");
   JPWObserverDeal truncated_same_order[];
   ArrayResize(truncated_same_order,1);
   JPWTestDeal(truncated_same_order[0],151,DEAL_ENTRY_IN,1,0.5,151000);
   truncated_same_order[0].order_ticket=555;
   JPWObserverAssert(JPWObserverFindEpisode(truncated_same_order,151,start,reason) &&
                     !JPWObserverInitialPositionMatches(start,555,
                        "SYNTH.EXACT",1,150000),
                     "omitted earlier fill of same order fails live-time witness");
   JPWObserverAssert(!JPWObserverInitialPositionMatches(start,555,
                     "SYNTH.EXACT",-1,151000),
                     "live direction mismatch fails initial witness");
   JPWObserverDeal simultaneous[];
   ArrayResize(simultaneous,2);
   JPWTestDeal(simultaneous[0],100,DEAL_ENTRY_IN,1,0.5,100000);
   JPWTestDeal(simultaneous[1],101,DEAL_ENTRY_IN,1,0.5,100000);
   JPWObserverAssert(!JPWObserverFindEpisode(simultaneous,100,start,reason) &&
                     reason=="Ordem de negocios no mesmo milissegundo ambigua",
                     "same-millisecond first execution is ambiguous");
  }

void JPWObserverTestDatabase()
  {
   string account_key="";
   JPWObserverAssert(JPWObserverAccountKey("SYNTH.SERVER",123,"USD",
                                               "SYNTH.INSTALL",account_key),
                     "synthetic opaque account key");
   const int db=DatabaseOpen(":memory:",DATABASE_OPEN_MEMORY|DATABASE_OPEN_READWRITE);
   JPWObserverAssert(db!=INVALID_HANDLE,"isolated in-memory SQLite available");
   if(db==INVALID_HANDLE) return;
   JPWObserverAssert(JPWObserverInitDatabase(db,account_key),
                     "initialize synthetic observer schema");
   string reason="";
   JPWObserverAssert(JPWObserverDatabaseCompatible(db,account_key,reason),
                     "schema and account identity verified");
   string wrong_key="";
   JPWObserverAccountKey("OTHER.SERVER",123,"USD","SYNTH.INSTALL",wrong_key);
   JPWObserverAssert(!JPWObserverDatabaseCompatible(db,wrong_key,reason),
                     "wrong account cannot read schema");
   JPWObserverSnapshot snapshot;
   JPWObserverClear(snapshot);
   snapshot.account_key=account_key; snapshot.symbol="SYNTH.EXACT";
   snapshot.position_id=555; snapshot.first_deal_ticket=10;
   snapshot.deal_time_msc=187200000;
   snapshot.side=1; snapshot.executed_p0=100.0; snapshot.atr55_h4=0.4;
   snapshot.atr_bar_open=172800;
   snapshot.n_1w=30; snapshot.n_2w=60;
   snapshot.status_1w=1; snapshot.status_2w=1;
   snapshot.horizon_source="SYNTH.WEEKLY"; snapshot.horizon_hash="";
   snapshot.horizon_observed_utc=200000;
   snapshot.observer_recorded_utc=200000;
   snapshot.event_arrival_utc=0;
   snapshot.event_processing_delay_ms=0;
   snapshot.provenance=JPW_OBSERVER_RECONSTRUCTED;
   JPWObserverEpisodeKey(account_key,snapshot.symbol,snapshot.position_id,
                         snapshot.first_deal_ticket,snapshot.episode_key);
   JPWObserverAssert(JPWObserverInsertImmutable(db,snapshot,reason),
                     "first immutable synthetic snapshot");
   JPWObserverAssert(JPWObserverInsertImmutable(db,snapshot,reason),
                     "duplicate event is idempotent");
   JPWObserverSnapshot saved;
   JPWObserverAssert(JPWObserverReadByKey(db,snapshot.episode_key,saved,reason) &&
                     saved.executed_p0==100.0 &&
                     saved.provenance==JPW_OBSERVER_RECONSTRUCTED,
                     "read back execution and explicit provenance");
   JPWObserverAssert(JPWObserverReadLatestInDb(db,account_key,"SYNTH.EXACT",
                                              saved,reason) &&
                     saved.first_deal_ticket==10,
                     "latest local snapshot does not require terminal account");
   snapshot.executed_p0=101.0;
   JPWObserverAssert(!JPWObserverInsertImmutable(db,snapshot,reason),
                     "same episode cannot overwrite first executed price");
   snapshot.executed_p0=100.0;
   snapshot.provenance=JPW_OBSERVER_CAPTURED_EVENT;
   snapshot.event_arrival_utc=199998;
   snapshot.event_processing_delay_ms=1500;
   JPWObserverAssert(JPWObserverInsertImmutable(db,snapshot,reason),
                     "same execution from second instance is idempotent");
   JPWObserverAssert(JPWObserverReadByKey(db,snapshot.episode_key,saved,reason) &&
                     saved.provenance==JPW_OBSERVER_RECONSTRUCTED &&
                     saved.event_arrival_utc==0,
                     "later event cannot promote first reconstructed snapshot");
   snapshot.executed_p0=101.0;
   JPWObserverAssert(!JPWObserverInsertImmutable(db,snapshot,reason),
                     "concurrent factual mismatch is rejected");
   JPWObserverAssert(DatabaseExecute(db,
                     "UPDATE observer_snapshots SET checksum='corrupted'"),
                     "synthetic corruption fixture");
   JPWObserverAssert(!JPWObserverReadByKey(db,snapshot.episode_key,saved,reason),
                     "corrupted snapshot is refused");
   JPWObserverAssert(DatabaseExecute(db,
                     "UPDATE observer_meta SET schema_version=3"),
                     "synthetic incompatible-version fixture");
   JPWObserverAssert(!JPWObserverDatabaseCompatible(db,account_key,reason),
                     "incompatible schema is refused");
   DatabaseClose(db);
  }

void OnStart()
  {
   JPWObserverTestEpisodes();
   JPWObserverTestDatabase();
   PrintFormat("JPW_Alavancagem_Observer_Tests %s: %d PASS / %d FAIL",
               (g_fail==0 ? "PASS" : "FAIL"),g_pass,g_fail);
  }

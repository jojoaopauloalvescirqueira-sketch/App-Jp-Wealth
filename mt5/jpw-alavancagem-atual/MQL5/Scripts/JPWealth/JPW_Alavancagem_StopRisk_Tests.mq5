#property copyright "JP Wealth"
#property version "1.90"
#property script_show_inputs
#property description "Testes sinteticos do motor de stop risk; nao le conta nem envia ordens."

#include <JPWealth/JPW_Alavancagem_StopRisk_Store.mqh>

int g_stop_asserts=0;
int g_stop_failures=0;

void JPWStopExpect(const bool condition,const string name)
  {
   g_stop_asserts++;
   if(!condition) { g_stop_failures++; Print("FAIL: ",name); }
  }

void JPWStopSynthetic(JPWStopRiskSample &sample,JPWStopRiskRow &rows[])
  {
   JPWStopRiskClearSample(sample);
   JPWRaizNHash("synthetic stop risk account",sample.account_key);
   JPWRaizNHash("synthetic stop risk writer",sample.publisher_token);
   sample.generation=1; sample.observed_utc=1000;
   sample.observed_mono_ms=1000; sample.currency="USD";
   sample.balance=10000.0;
   sample.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   ArrayResize(rows,3);
   for(int i=0;i<3;i++) JPWStopRiskClearRow(rows[i]);
   rows[0].kind=JPW_STOP_RISK_POSITION;
   rows[0].ticket=10; rows[0].identifier=100;
   rows[0].opened_msc=10000; rows[0].symbol="SYNTH_NZDUSD";
   rows[0].side=1; rows[0].order_type=-1; rows[0].valid=1;
   rows[0].volume=0.1; rows[0].entry=0.6; rows[0].sl=0.59;
   rows[0].risk_money=100.0; rows[0].additional_valid=1;
   rows[0].additional_money=4.0;
   rows[1]=rows[0]; rows[1].ticket=11; rows[1].identifier=101;
   rows[1].opened_msc=11000; rows[1].volume=0.05;
   rows[1].risk_money=0.0; rows[1].additional_money=5.0;
   rows[2].kind=JPW_STOP_RISK_PENDING;
   rows[2].ticket=12; rows[2].identifier=0;
   rows[2].opened_msc=12000; rows[2].symbol="SYNTH_NZDUSD";
   rows[2].side=1; rows[2].order_type=ORDER_TYPE_BUY_LIMIT;
   rows[2].valid=1; rows[2].volume=0.03;
   rows[2].entry=0.59; rows[2].sl=0.58;
   rows[2].risk_money=50.0;
   rows[2].additional_valid=0;
   rows[2].additional_reason="Nao se aplica a pendentes";
   sample.row_count=ArraySize(rows);
   JPWStopRiskRawDigest(sample,rows,sample.composition_digest);
   JPWStopRiskChecksum(sample,rows,sample.checksum);
  }

void OnStart()
  {
   JPWStopRiskSample sample;
   JPWStopRiskRow rows[];
   JPWStopSynthetic(sample,rows);
   string reason="",checksum="";
   double total=0.0,pct=0.0,positions=0.0,pending=0.0,additional=0.0;
   JPWStopExpect(JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                total,pct,positions,pending,additional,reason),
                "hedging aggregate available");
   JPWStopExpect(MathAbs(total-150.0)<1e-9 &&
                 MathAbs(pct-1.5)<1e-9 &&
                 MathAbs(positions-100.0)<1e-9 &&
                 MathAbs(pending-50.0)<1e-9 &&
                 MathAbs(additional-9.0)<1e-9,
                 "positions plus independent pending reserve");
   double money=0.0;
   JPWStopExpect(JPWStopRiskLossFromProfit(-60.0,money) && money==60.0,
                 "adverse stop is risk");
   JPWStopExpect(JPWStopRiskLossFromProfit(25.0,money) && money==0.0,
                 "profit protecting stop floors risk at zero");
   JPWStopExpect(JPWStopRiskChecksum(sample,rows,checksum) &&
                 checksum==sample.checksum,"synthetic checksum");
   string lease_token="";
   JPWRaizNHash("synthetic lease "+
                IntegerToString((long)GetMicrosecondCount()),lease_token);
   const string lease_name=JPWStopRiskLeaseName(lease_token);
   JPWStopExpect(lease_name!="" &&
                 !JPWStopRiskLeaseMatches(lease_token,1234),
                 "missing session lease refuses current sample");
   if(lease_name!="" && !GlobalVariableCheck(lease_name))
     {
      const bool created=GlobalVariableTemp(lease_name);
      JPWStopExpect(created,"synthetic session lease is temporary");
      if(created)
        {
         JPWStopExpect(GlobalVariableSetOnCondition(lease_name,1234.0,0.0) &&
                       JPWStopRiskLeaseMatches(lease_token,1234),
                       "exact observed millisecond matches session lease");
         JPWStopExpect(!JPWStopRiskLeaseMatches(lease_token,1235),
                       "other sample cannot reuse prior lease");
         GlobalVariableDel(lease_name);
         JPWStopExpect(!JPWStopRiskLeaseMatches(lease_token,1234),
                       "detached EA session lease invalidates current");
        }
     }

   string observer_token_a="",observer_token_b="",other_account="";
   JPWRaizNHash("synthetic observer presence a "+
                IntegerToString((long)GetMicrosecondCount()),observer_token_a);
   JPWRaizNHash("synthetic observer presence b "+
                IntegerToString((long)GetMicrosecondCount()),observer_token_b);
   JPWRaizNHash("synthetic other account",other_account);
   JPWStopExpect(JPWObserverPresenceName(sample.account_key,observer_token_a)!="" &&
                 StringLen(JPWObserverPresenceName(sample.account_key,
                           observer_token_a))<=63,
                 "opaque presence marker fits terminal name limit");
   JPWStopExpect(JPWObserverPresenceRead(sample.account_key)==
                 JPW_OBSERVER_NOT_CONFIRMED,
                 "EA never attached has no compatible presence");
   const string older_name=JPWObserverPresenceNameForVersion(
      sample.account_key,observer_token_b,"synthetic-previous-version");
   if(older_name!="" && !GlobalVariableCheck(older_name) &&
      GlobalVariableTemp(older_name))
     {
      double previous_signal=0.0;
      JPWStopExpect(JPWObserverPresenceEncode(GetTickCount64(),
                    JPW_OBSERVER_PUBLISHED,previous_signal) &&
                    GlobalVariableSetOnCondition(older_name,previous_signal,0.0) &&
                    JPWObserverPresenceRead(sample.account_key)==
                    JPW_OBSERVER_NOT_CONFIRMED,
                    "older product version cannot confirm compatible EA");
      GlobalVariableDel(older_name);
     }
   double observer_signal_a=0.0,observer_signal_b=0.0;
   const bool observer_started=JPWObserverPresenceStartOwned(sample.account_key,
                                            observer_token_a,observer_signal_a);
   JPWStopExpect(observer_started,"synthetic EA presence starts before sample");
   if(observer_started)
     {
      JPWStopExpect(JPWObserverPresenceRead(sample.account_key)==JPW_OBSERVER_WAITING,
                    "active EA can be waiting for first sample");
      JPWStopExpect(JPWObserverPresenceRead(other_account)==JPW_OBSERVER_NOT_CONFIRMED,
                    "other account cannot see presence");
      JPWStopExpect(JPWObserverPresenceBeatOwned(sample.account_key,observer_token_a,
                    JPW_OBSERVER_FAILED,observer_signal_a) &&
                    JPWObserverPresenceRead(sample.account_key)==JPW_OBSERVER_FAILED,
                    "failed publication remains distinct from absent EA");
      const bool second_started=JPWObserverPresenceStartOwned(sample.account_key,
                                           observer_token_b,observer_signal_b);
      JPWStopExpect(second_started,"second EA receives its own presence marker");
      if(second_started)
        {
         JPWStopExpect(JPWObserverPresenceBeatOwned(sample.account_key,observer_token_b,
                       JPW_OBSERVER_PUBLISHED,observer_signal_b) &&
                       JPWObserverPresenceRead(sample.account_key)==JPW_OBSERVER_PUBLISHED,
                       "one published EA outranks another failed instance");
         JPWObserverPresenceReleaseOwned(sample.account_key,observer_token_b,
                                         observer_signal_b);
         JPWStopExpect(JPWObserverPresenceRead(sample.account_key)==JPW_OBSERVER_FAILED,
                       "detached second EA leaves first failure visible");
        }
      JPWObserverPresenceReleaseOwned(sample.account_key,observer_token_a,
                                      observer_signal_a);
      JPWStopExpect(JPWObserverPresenceRead(sample.account_key)==
                    JPW_OBSERVER_NOT_CONFIRMED,
                    "detached EA no longer confirms presence");
      double reclaimed=0.0;
      JPWStopExpect(JPWObserverPresenceStartOwned(sample.account_key,
                    observer_token_a,reclaimed) && reclaimed>0.0,
                    "released temporary tombstone can be reclaimed by same EA");
      JPWObserverPresenceReleaseOwned(sample.account_key,observer_token_a,reclaimed);
      GlobalVariableDel(JPWObserverPresenceName(sample.account_key,observer_token_a));
      GlobalVariableDel(JPWObserverPresenceName(sample.account_key,observer_token_b));
     }
   string observer_token_owned="";
   JPWRaizNHash("synthetic observer owned "+
                IntegerToString((long)GetMicrosecondCount()),
                observer_token_owned);
   double owned_signal=0.0;
   const bool owned_started=JPWObserverPresenceStartOwned(sample.account_key,
                            observer_token_owned,owned_signal);
   JPWStopExpect(owned_started && owned_signal>0.0,
                 "EA keeps the exact value written to its temporary marker");
   if(owned_started)
     {
      const string owned_name=JPWObserverPresenceName(sample.account_key,
                                                     observer_token_owned);
      JPWStopExpect(JPWObserverPresenceBeatOwned(sample.account_key,
                    observer_token_owned,JPW_OBSERVER_PUBLISHED,owned_signal) &&
                    JPWObserverPresenceMarkerMatches(sample.account_key,
                    observer_token_owned,owned_signal),
                    "owned marker renews from its previous exact value");
      const double altered_signal=owned_signal+8.0;
      GlobalVariableSet(owned_name,altered_signal);
      JPWStopExpect(!JPWObserverPresenceBeatOwned(sample.account_key,
                    observer_token_owned,JPW_OBSERVER_FAILED,owned_signal) &&
                    !JPWObserverPresenceMarkerMatches(sample.account_key,
                    observer_token_owned,owned_signal),
                    "another writer's changed marker is never adopted");
      JPWObserverPresenceReleaseOwned(sample.account_key,
                                      observer_token_owned,owned_signal);
      double still_present=0.0;
      JPWStopExpect(GlobalVariableGet(owned_name,still_present) &&
                    still_present==altered_signal,
                    "release does not remove a changed marker");
      GlobalVariableDel(owned_name);
     }
   double encoded_presence=0.0;
   JPWObserverPresenceState decoded_presence=JPW_OBSERVER_NOT_CONFIRMED;
   JPWStopExpect(JPWObserverPresenceEncode(1000,JPW_OBSERVER_WAITING,
                 encoded_presence) &&
                 JPWObserverPresenceDecodeAt(encoded_presence,31000,
                                             decoded_presence) &&
                 decoded_presence==JPW_OBSERVER_WAITING &&
                 !JPWObserverPresenceDecodeAt(encoded_presence,31001,
                                              decoded_presence),
                 "presence expires after thirty seconds without heartbeat");
   JPWStopExpect(!JPWObserverPresenceDecodeAt(encoded_presence,999,
                                              decoded_presence) &&
                 !JPWObserverPresenceDecodeAt(8000.0,1000,
                                              decoded_presence) &&
                 JPWObserverPresenceName(sample.account_key,"not-a-hash")=="",
                 "future, unknown state and malformed identity do not confirm EA");

   JPWStopRiskSample usc=sample;
   JPWStopRiskRow usc_rows[];
   ArrayResize(usc_rows,ArraySize(rows));
   for(int i=0;i<ArraySize(rows);i++)
     { usc_rows[i]=rows[i]; usc_rows[i].risk_money*=100.0;
       usc_rows[i].additional_money*=100.0; }
   usc.currency="USC"; usc.balance*=100.0;
   usc.row_count=ArraySize(usc_rows);
   JPWStopRiskRawDigest(usc,usc_rows,usc.composition_digest);
   JPWStopExpect(JPWStopRiskAggregate(usc,usc_rows,"SYNTH_NZDUSD",1,
                 total,pct,positions,pending,additional,reason) &&
                 MathAbs(pct-1.5)<1e-9 && MathAbs(total-15000.0)<1e-9,
                 "USC numerator and denominator same account unit");

   JPWStopRiskRow other=rows[0];
   other.ticket=13; other.identifier=103; other.symbol="SYNTH_EURUSD";
   other.risk_money=100000.0;
   ArrayResize(rows,4); rows[3]=other; sample.row_count=4;
   JPWStopExpect(JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                 total,pct,positions,pending,additional,reason) &&
                 MathAbs(total-150.0)<1e-9,
                 "other exact instrument excluded");
   ArrayResize(rows,3); sample.row_count=3;

   rows[2].valid=0; rows[2].sl=0.0;
   rows[2].risk_money=0.0; rows[2].reason="Sem SL valido";
   JPWStopExpect(!JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                  total,pct,positions,pending,additional,reason),
                  "missing pending SL refuses partial total");
   rows[2].sl=0.58; rows[2].valid=1; rows[2].risk_money=50.0;
   rows[2].reason="";
   rows[2].order_type=ORDER_TYPE_BUY_STOP_LIMIT;
   rows[2].valid=0; rows[2].reason="Tipo nao suportado";
   JPWStopExpect(!JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                  total,pct,positions,pending,additional,reason),
                  "stop-limit cannot disappear from same-direction total");
   rows[2].order_type=ORDER_TYPE_BUY_LIMIT;
   rows[2].valid=1; rows[2].reason="";

   rows[0].additional_valid=0;
   rows[0].additional_money=0.0;
   rows[0].additional_reason="Cotacao antiga";
   JPWStopExpect(JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                 total,pct,positions,pending,additional,reason) &&
                 total==150.0 && additional==-1.0,
                 "stale market quote does not erase entry-to-SL risk");
   rows[0].additional_valid=1;
   rows[0].additional_money=4.0;
   rows[0].additional_reason="";

   sample.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_NETTING;
   JPWStopExpect(!JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                  total,pct,positions,pending,additional,reason),
                  "netting aggregate cannot impersonate Genesis defenses");
   sample.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   sample.balance=0.0;
   JPWStopExpect(!JPWStopRiskAggregate(sample,rows,"SYNTH_NZDUSD",1,
                  total,pct,positions,pending,additional,reason),
                  "nonpositive balance refuses percentage");

   JPWStopSynthetic(sample,rows);
   const int db=DatabaseOpen(":memory:",
                              DATABASE_OPEN_MEMORY|DATABASE_OPEN_READWRITE);
   JPWStopExpect(db!=INVALID_HANDLE,"synthetic in-memory SQLite opens");
   if(db!=INVALID_HANDLE)
     {
      bool empty_schema=false;
      JPWStopExpect(JPWStopRiskSchemaEmpty(db,empty_schema) &&
                    empty_schema,"empty SQLite file can initialize");
      JPWStopExpect(DatabaseTransactionBegin(db) &&
                    DatabaseExecute(db,"CREATE TABLE interrupted_setup (id INTEGER)") &&
                    DatabaseTransactionRollback(db),
                    "injected setup failure rolls back DDL");
      JPWStopExpect(JPWStopRiskSchemaEmpty(db,empty_schema) &&
                    empty_schema,"rolled-back empty schema can safely retry");
      JPWStopExpect(JPWStopRiskInitDatabase(db,sample.account_key),
                    "schema initializes without account file");
      JPWStopExpect(JPWStopRiskInsertSample(db,sample),
                    "sample inserts in memory");
      bool inserted=true;
      for(int i=0;i<ArraySize(rows);i++)
         inserted=inserted && JPWStopRiskInsertRow(db,1,rows[i]);
      JPWStopExpect(inserted,"rows insert in memory");
      JPWStopRiskSample read_sample;
      JPWStopRiskRow read_rows[];
      JPWStopExpect(JPWStopRiskReadLatestInDb(db,sample.account_key,
                    read_sample,read_rows,reason) &&
                    read_sample.checksum==sample.checksum &&
                    ArraySize(read_rows)==3,
                    "full SQLite roundtrip verified");
      JPWStopExpect(DatabaseExecute(db,
                    "UPDATE stop_risk_rows SET risk_money=999 WHERE ticket=10"),
                    "synthetic corruption applies");
      JPWStopExpect(!JPWStopRiskReadLatestInDb(db,sample.account_key,
                     read_sample,read_rows,reason),
                     "tampered row invalidates generation");
      DatabaseClose(db);
     }
   const int unknown=DatabaseOpen(":memory:",
                         DATABASE_OPEN_MEMORY|DATABASE_OPEN_READWRITE);
   if(unknown!=INVALID_HANDLE)
     {
      JPWStopExpect(DatabaseExecute(unknown,
                    "CREATE TABLE unrelated (id INTEGER)"),
                    "unknown schema fixture created");
      bool empty_schema=false;
      JPWStopExpect(JPWStopRiskSchemaEmpty(unknown,empty_schema) &&
                    !empty_schema,
                    "unknown nonempty schema cannot be auto initialized");
      DatabaseClose(unknown);
     }
   const int unknown_view=DatabaseOpen(":memory:",
                         DATABASE_OPEN_MEMORY|DATABASE_OPEN_READWRITE);
   if(unknown_view!=INVALID_HANDLE)
     {
      JPWStopExpect(DatabaseExecute(unknown_view,
                    "CREATE VIEW unrelated_view AS SELECT 1"),
                    "unknown view fixture created");
      bool empty_schema=false;
      JPWStopExpect(JPWStopRiskSchemaEmpty(unknown_view,empty_schema) &&
                    !empty_schema,
                    "unknown view also blocks auto initialization");
      DatabaseClose(unknown_view);
     }
   Print("JPW_Alavancagem_StopRisk_Tests ",
         (g_stop_failures==0 ? "PASS" : "FAIL"),": ",g_stop_asserts,
         " asserts, ",g_stop_failures," failures");
  }

#property copyright "JP Wealth"
#property version   "1.00"
#property script_show_inputs

#include <JPWealth/JPW_NoCuda_Store.mqh>

// Synthetic identities and files only. Run in an isolated MT5 terminal.
int g_nocuda_store_pass=0;
int g_nocuda_store_fail=0;

void JPWNoCudaStoreAssert(const bool condition,const string name)
  {
   if(condition) g_nocuda_store_pass++;
   else
     { g_nocuda_store_fail++; Print("FAIL NoCuda store: ",name); }
  }

bool JPWNoCudaStoreFixture(const string suffix,string &key,
                           JPWNoCudaRecord &record)
  {
   JPWNoCudaStoreClear(record);
   const string synthetic_installation="SYNTHETIC.NOCUDA."+suffix;
   if(!JPWNoCudaStoreKey(synthetic_installation,"SYNTHETIC.FEED",key))
      return(false);
   record.store_key=key;
   if(!JPWNoCudaStoreNewStudyId(key,"NZDUSD.synthetic",
                                1700000000,812345,record.study_id))
      return(false);
   record.symbol="NZDUSD.synthetic";
   record.feed="SYNTHETIC.FEED";
   record.source_tf=PERIOD_H1;
   record.convention=JPW_NOCUDA_GEOMETRY_CONVENTION;
   record.range_first_open=1700000000;
   record.range_last_open=1700014400;
   record.range_bar_count=5;
   if(!JPWNoCudaStoreHash("SYNTHETIC.H1.CLOSE.SEQUENCE",record.source_signature))
      return(false);
   record.a_open=1700000000;
   record.a_known=1700003600;
   record.a_ordinal=0;
   record.a_close=1.1000;
   record.b_open=1700014400;
   record.b_known=1700018000;
   record.b_ordinal=4;
   record.b_close=1.1020;
   record.c_open=1700007200;
   record.c_known=1700010800;
   record.c_ordinal=2;
   record.c_close=1.1050;
   record.confirmed_utc=1700020000;
   record.justification="Synthetic channel anchor review";
   return(true);
  }

void JPWNoCudaStoreCloseAndRemoveFixture(const string key)
  {
   // Only the synthetic hashed fixture path is touched; never clean user files.
   const string path=JPWNoCudaStorePath(key);
   if(path!="") FileDelete(path);
  }

void JPWNoCudaStoreTestLifecycle(const string suffix)
  {
   string key="";
   JPWNoCudaRecord first;
   JPWNoCudaStoreAssert(JPWNoCudaStoreFixture(suffix,key,first),"fixture");
   JPWNoCudaRecord readback;
   string reason="";
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(key,first.study_id,
                             readback,reason)==JPW_NOCUDA_STORE_ABSENT,
                             "first study absent");
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(first,0,reason)==
                             JPW_NOCUDA_STORE_VALID &&
                             first.revision==1 &&
                             first.previous_revision==0 &&
                             JPWNoCudaStoreIsHash(first.checksum),
                             "first immutable revision");
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(key,first.study_id,
                             readback,reason)==JPW_NOCUDA_STORE_VALID &&
                             readback.revision==1 &&
                             readback.c_close==1.1050,
                             "first revision survives read");
   string ids[];
   JPWNoCudaStoreAssert(JPWNoCudaStoreList(key,"NZDUSD.synthetic",0,
                             ids,reason)==JPW_NOCUDA_STORE_VALID &&
                             ArraySize(ids)==1 && ids[0]==first.study_id,
                             "study listed by exact symbol");
   string missing[];
   JPWNoCudaStoreAssert(JPWNoCudaStoreList(key,"EURUSD.synthetic",0,
                             missing,reason)==JPW_NOCUDA_STORE_ABSENT,
                             "other symbol excluded");
   // A cancelled draft and repeated reads do not advance the generation.
   JPWNoCudaRecord cancelled=readback;
   cancelled.c_close=1.1060;
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(key,first.study_id,
                             readback,reason)==JPW_NOCUDA_STORE_VALID &&
                             readback.revision==1 &&
                             readback.c_close==1.1050,
                             "cancelled draft never written");
   JPWNoCudaRecord stale=readback;
   JPWNoCudaRecord revised=cancelled;
   revised.confirmed_utc++;
   revised.justification="Synthetic second revision";
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(revised,1,reason)==
                             JPW_NOCUDA_STORE_VALID &&
                             revised.revision==2 &&
                             revised.previous_revision==1,
                             "second revision appended");
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadRevision(key,first.study_id,1,
                             readback,reason)==JPW_NOCUDA_STORE_VALID &&
                             readback.c_close==1.1050 &&
                             readback.revision==1,
                             "older revision remains immutable");
   stale.c_close=1.1040;
   stale.confirmed_utc+=2;
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(stale,1,reason)==
                             JPW_NOCUDA_STORE_CONFLICT,
                             "stale editor cannot overwrite");
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(key,first.study_id,
                             readback,reason)==JPW_NOCUDA_STORE_VALID &&
                             readback.revision==2 &&
                             readback.c_close==1.1060,
                             "conflict preserves newest revision");

   // No script can modify or delete a confirmed revision through SQL.
   const int db=DatabaseOpen(JPWNoCudaStorePath(key),DATABASE_OPEN_READWRITE);
   JPWNoCudaStoreAssert(db!=INVALID_HANDLE,"fixture DB opens");
   if(db!=INVALID_HANDLE)
     {
      JPWNoCudaStoreAssert(!DatabaseExecute(db,
         "UPDATE nocuda_revisions SET c_close=0 WHERE revision=1"),
         "immutable revision trigger rejects UPDATE");
      JPWNoCudaStoreAssert(!DatabaseExecute(db,
         "DELETE FROM nocuda_revisions WHERE revision=1"),
         "immutable revision trigger rejects DELETE");
      DatabaseClose(db);
     }
   JPWNoCudaStoreCloseAndRemoveFixture(key);
  }

void JPWNoCudaStoreTestInvalidAndContext(const string suffix)
  {
   string key="";
   JPWNoCudaRecord record;
   JPWNoCudaStoreAssert(JPWNoCudaStoreFixture(suffix,key,record),"invalid fixture");
   string reason="";
   record.b_ordinal=record.a_ordinal;
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)!=
                             JPW_NOCUDA_STORE_VALID,
                             "same A/B bar refused");
   record.b_ordinal=4;
   record.c_close=record.a_close+(record.b_close-record.a_close)/2.0;
   // Exactly on AB principal at ordinal 2.
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)!=
                             JPW_NOCUDA_STORE_VALID,
                             "zero width refused");
   record.c_close=1.1050;
   record.a_known=record.a_open;
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)!=
                             JPW_NOCUDA_STORE_VALID,
                             "forming source bar refused");
   record.a_known+=3600;
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)==
                             JPW_NOCUDA_STORE_VALID,
                             "valid fixture saved after refusals");
   string other_key="";
   JPWNoCudaStoreAssert(JPWNoCudaStoreKey("OTHER.SYNTHETIC.INSTALL",
                             "SYNTHETIC.FEED",other_key) &&
                             other_key!=key,"installation-separated key");
   JPWNoCudaRecord other;
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(other_key,record.study_id,
                             other,reason)==JPW_NOCUDA_STORE_ABSENT,
                             "other installation cannot load study");
   JPWNoCudaStoreCloseAndRemoveFixture(key);
  }

void JPWNoCudaStoreTestCorruptAndVersion(const string suffix)
  {
   string key="";
   JPWNoCudaRecord record;
   JPWNoCudaStoreAssert(JPWNoCudaStoreFixture(suffix,key,record),"corrupt fixture");
   string reason="";
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)==
                             JPW_NOCUDA_STORE_VALID,"corrupt fixture saved");
   const string path=JPWNoCudaStorePath(key);
   int db=DatabaseOpen(path,DATABASE_OPEN_READWRITE);
   JPWNoCudaStoreAssert(db!=INVALID_HANDLE,"corrupt DB opens");
   if(db!=INVALID_HANDLE)
     {
      JPWNoCudaStoreAssert(DatabaseExecute(db,
         "UPDATE nocuda_heads SET checksum='00000000000000000000000000000000'"),
         "synthetic header damaged");
      DatabaseClose(db);
     }
   JPWNoCudaRecord readback;
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(key,record.study_id,
                             readback,reason)==JPW_NOCUDA_STORE_CORRUPT,
                             "corrupt header refused");
   record.c_close=1.1060;
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,1,reason)==
                             JPW_NOCUDA_STORE_CORRUPT,
                             "corruption cannot be silently reset");
   JPWNoCudaStoreCloseAndRemoveFixture(key);

   string version_key="";
   JPWNoCudaRecord version_record;
   JPWNoCudaStoreAssert(JPWNoCudaStoreFixture(suffix+".VERSION",
                             version_key,version_record),"version fixture");
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(version_record,0,reason)==
                             JPW_NOCUDA_STORE_VALID,"version fixture saved");
   db=DatabaseOpen(JPWNoCudaStorePath(version_key),DATABASE_OPEN_READWRITE);
   if(db!=INVALID_HANDLE)
     {
      JPWNoCudaStoreAssert(DatabaseExecute(db,
         "UPDATE nocuda_meta SET schema_version=999"),
         "synthetic future version written");
      DatabaseClose(db);
     }
   JPWNoCudaStoreAssert(JPWNoCudaStoreLoadHead(version_key,
                             version_record.study_id,readback,reason)==
                             JPW_NOCUDA_STORE_INCOMPATIBLE,
                             "future schema refused");
   JPWNoCudaStoreCloseAndRemoveFixture(version_key);
  }

void JPWNoCudaStoreTestBusy(const string suffix)
  {
   string key="";
   JPWNoCudaRecord record;
   JPWNoCudaStoreAssert(JPWNoCudaStoreFixture(suffix,key,record),"busy fixture");
   string reason="";
   int db=INVALID_HANDLE;
   JPWNoCudaStoreAssert(JPWNoCudaStoreOpen(key,true,db,reason)==
                             JPW_NOCUDA_STORE_VALID,"busy DB initialized");
   if(db==INVALID_HANDLE) return;
   const bool locked=DatabaseTransactionBegin(db) &&
      DatabaseExecute(db,"UPDATE nocuda_meta SET schema_version=schema_version");
   JPWNoCudaStoreAssert(locked,"synthetic writer lock acquired");
   if(locked)
      JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)==
                             JPW_NOCUDA_STORE_BUSY,
                             "second instance cannot write through lock");
   DatabaseTransactionRollback(db);
   DatabaseClose(db);
   JPWNoCudaStoreAssert(JPWNoCudaStoreConfirm(record,0,reason)==
                             JPW_NOCUDA_STORE_VALID,
                             "write succeeds after lock release");
   JPWNoCudaStoreCloseAndRemoveFixture(key);
  }

void OnStart()
  {
   // A unique, synthetic namespace prevents contact with saved user studies.
   const string run="SYNTHETIC."+IntegerToString(TimeLocal())+"."+
                    IntegerToString((long)GetTickCount64());
   JPWNoCudaStoreTestLifecycle(run+".LIFECYCLE");
   JPWNoCudaStoreTestInvalidAndContext(run+".INVALID");
   JPWNoCudaStoreTestCorruptAndVersion(run+".CORRUPT");
   JPWNoCudaStoreTestBusy(run+".BUSY");
   PrintFormat("JPW_NoCuda_Store_Tests %s: %d asserts, %d failures",
               g_nocuda_store_fail==0 ? "PASS" : "FAIL",
               g_nocuda_store_pass+g_nocuda_store_fail,
               g_nocuda_store_fail);
  }

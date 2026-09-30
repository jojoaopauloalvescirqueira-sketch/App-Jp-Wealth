#property copyright "JP Wealth"
#property version   "1.21"
#property script_show_inputs

#include <JPWealth/JPW_Alavancagem_MDD.mqh>

// Executar somente em terminal isolado. Identidades e diretorios sinteticos.
int g_mdd_passes=0;
int g_mdd_failures=0;

void JPWMDDAssert(const bool condition,const string label)
  {
   if(condition) g_mdd_passes++;
   else
     {
      g_mdd_failures++;
      Print("FAIL: ",label);
     }
  }

void JPWMDDNear(const double actual,const double expected,const string label)
  {
   JPWMDDAssert(MathIsValidNumber(actual) &&
                MathAbs(actual-expected)<=1e-9*MathMax(1.0,MathAbs(expected)),
                label);
  }

void JPWMDDFixture(JPWAccount &account,const long login,
                   const string currency)
  {
   account.login=login;
   account.server="SYNTHETIC.MDD.TEST";
   account.currency=currency;
  }

JPW_MDD_STATE JPWMDDTestObserve(JPWAccount &account,const double balance,
                                 const double equity,const datetime at,
                                 const string folder,JPWMDDRecord &record)
  {
   double dd=0.0;
   if(!JPWBalanceDDPercent(balance,equity,dd)) return(JPW_MDD_INVALID);
   return(JPWMDDObserve(account,balance,equity,dd,at,"1.2.0",folder,record));
  }

void JPWMDDTestCodec()
  {
   JPWAccount account;
   JPWMDDFixture(account,901001,"USD");
   string key="";
   string currency="";
   double scale=0.0;
   JPWMDDAssert(JPWMDDAccountKey(account,key,currency,scale),"codec key");
   JPWMDDRecord candidate;
   JPWMDDClear(candidate);
   candidate.schema=1;
   candidate.metric_id=JPW_MDD_METRIC_ID;
   candidate.account_key=key;
   candidate.currency=currency;
   candidate.account_scale=scale;
   candidate.observation_started_at=(datetime)1000;
   candidate.max_percent=10.0;
   candidate.balance_at_max=1000.0;
   candidate.equity_at_max=900.0;
   candidate.observed_at_utc=(datetime)1100;
   candidate.time_basis=JPW_MDD_TIME_BASIS;
   candidate.producer_version="1.2.0";
   candidate.generation=1;
   string encoded="";
   JPWMDDAssert(JPWMDDEncode(candidate,encoded),"codec encode");
   JPWMDDRecord decoded;
   JPWMDDAssert(JPWMDDDecode(encoded,key,decoded)==JPW_MDD_VALID,
                "codec round trip");
   JPWMDDNear(decoded.max_percent,10.0,"codec maximum");
   JPWMDDAssert(decoded.time_basis==JPW_MDD_TIME_BASIS &&
                decoded.producer_version=="1.2.0" &&
                decoded.observation_started_at==(datetime)1000,
                "codec metadata");
   string altered=encoded;
   const int replacements=StringReplace(altered,"BALANCE|","BALANCE|9");
   JPWMDDAssert(replacements==1 &&
                JPWMDDDecode(altered,key,decoded)==JPW_MDD_INVALID,
                "codec checksum rejects changed balance");
   JPWAccount other;
   JPWMDDFixture(other,901002,"USD");
   string other_key="";
   JPWMDDAssert(JPWMDDAccountKey(other,other_key,currency,scale) &&
                other_key!=key &&
                JPWMDDDecode(encoded,other_key,decoded)==JPW_MDD_INVALID,
                "codec account isolation");
   JPWMDDAssert(JPWMDDDecode("JPW_MDD|2\nFUTURE|1",key,decoded)==
                JPW_MDD_INCOMPATIBLE,"future schema rejected");
  }

void JPWMDDTestPersistence(const string folder)
  {
   JPWAccount account;
   JPWMDDFixture(account,901101,"USD");
   JPWMDDRecord saved;
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,1200.0,(datetime)1000,
                                   folder,saved)==JPW_MDD_VALID,
                "first zero persisted");
   JPWMDDAssert(saved.generation==1 && saved.max_percent==0.0 &&
                saved.observation_started_at==(datetime)1000,
                "first zero receipt");
   JPWMDDRecord restarted;
   int active=-1;
   JPWMDDAssert(JPWMDDLoadState(account,folder,restarted,active)==JPW_MDD_VALID &&
                restarted.generation==1 && restarted.max_percent==0.0,
                "restart reads first sample");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,900.0,(datetime)1100,
                                   folder,saved)==JPW_MDD_VALID &&
                saved.generation==2,"higher sample advances generation");
   JPWMDDAssert(JPWMDDTestObserve(account,2000.0,1800.0,(datetime)1200,
                                   folder,saved)==JPW_MDD_VALID &&
                saved.generation==2 && saved.balance_at_max==1000.0 &&
                saved.observed_at_utc==(datetime)1100,
                "tie preserves first winning sample");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,950.0,(datetime)1300,
                                   folder,saved)==JPW_MDD_VALID &&
                saved.generation==2 && saved.max_percent==10.0,
                "stale instance cannot lower maximum");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,800.0,(datetime)1400,
                                   folder,saved)==JPW_MDD_VALID &&
                saved.generation==3 && saved.max_percent==20.0 &&
                saved.observation_started_at==(datetime)1000,
                "higher sample keeps observation start");
   // Uma estimativa nunca chama Observe. A leitura seguinte deve ser identica.
   JPWMDDRecord after_estimate;
   JPWMDDAssert(JPWMDDLoadState(account,folder,after_estimate,active)==
                JPW_MDD_VALID && after_estimate.generation==3 &&
                after_estimate.max_percent==20.0,
                "estimated sample does not mutate record");
   JPWMDDAssert(JPWMDDObserve(account,1000.0,800.0,19.0,(datetime)1500,
                               "1.2.0",folder,saved)==JPW_MDD_INVALID,
                "inconsistent percentage rejected");
   JPWMDDAssert(JPWMDDTestObserve(account,0.0,-100.0,(datetime)1500,
                                   folder,saved)==JPW_MDD_INVALID,
                "invalid balance rejected");
   JPWMDDAssert(JPWMDDLoadState(account,folder,after_estimate,active)==
                JPW_MDD_VALID && after_estimate.generation==3,
                "invalid sample leaves generation intact");

   JPWAccount other;
   JPWMDDFixture(other,901102,"USD");
   JPWMDDRecord separate;
   JPWMDDAssert(JPWMDDTestObserve(other,1000.0,700.0,(datetime)1600,
                                   folder,separate)==JPW_MDD_VALID &&
                separate.max_percent==30.0 && separate.generation==1,
                "another account has independent maximum");
   JPWAccount usc;
   JPWMDDFixture(usc,901101,"USC");
   JPWMDDAssert(JPWMDDTestObserve(usc,100000.0,90000.0,(datetime)1600,
                                   folder,separate)==JPW_MDD_VALID &&
                separate.max_percent==10.0 &&
                separate.account_scale==100.0 && separate.generation==1,
                "USC scale keeps separate key and raw units");
   JPWAccount normalized;
   JPWMDDFixture(normalized,901101," usc ");
   string usc_key="";
   string normalized_key="";
   string currency="";
   double scale=0.0;
   JPWMDDAssert(JPWMDDAccountKey(usc,usc_key,currency,scale) &&
                JPWMDDAccountKey(normalized,normalized_key,currency,scale) &&
                usc_key==normalized_key,
                "currency normalization preserves account key");
   JPWMDDAssert(JPWMDDLoadState(account,folder,restarted,active)==JPW_MDD_VALID &&
                restarted.max_percent==20.0,
                "switching account does not alter prior record");
   JPWAccount nonpositive;
   JPWMDDFixture(nonpositive,901103,"USD");
   JPWMDDAssert(JPWMDDTestObserve(nonpositive,1000.0,0.0,(datetime)1600,
                                   folder,separate)==JPW_MDD_VALID &&
                separate.max_percent==100.0,
                "zero equity still persists balance DD");
   JPWMDDAssert(JPWMDDTestObserve(nonpositive,1000.0,-100.0,(datetime)1700,
                                   folder,separate)==JPW_MDD_VALID &&
                MathAbs(separate.max_percent-110.0)<1e-9 &&
                separate.generation==2,
                "negative equity still advances balance DD");
   JPWAccount tiny;
   JPWMDDFixture(tiny,901104,"USD");
   JPWMDDAssert(JPWMDDTestObserve(tiny,1.0,0.9999999999999998,
                                   (datetime)1700,folder,separate)==JPW_MDD_VALID &&
                separate.max_percent>0.0 &&
                separate.max_percent<0.01,
                "tiny positive DD persists without rounding to zero");
   JPWMDDAssert(JPWMDDLoadState(tiny,folder,restarted,active)==JPW_MDD_VALID &&
                restarted.max_percent>0.0 &&
                restarted.max_percent==separate.max_percent,
                "tiny DD survives codec and restart");
  }

void JPWMDDTestRecovery(const string folder)
  {
   JPWAccount account;
   JPWMDDFixture(account,901201,"USD");
   JPWMDDRecord record;
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,900.0,(datetime)1000,
                                   folder,record)==JPW_MDD_VALID,
                "recovery fixture first slot");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,800.0,(datetime)1100,
                                   folder,record)==JPW_MDD_VALID,
                "recovery fixture second slot");
   string key="";
   string currency="";
   double scale=0.0;
   JPWMDDAssert(JPWMDDAccountKey(account,key,currency,scale),
                "recovery fixture key");
   JPWMDDAssert(JPWMDDWriteText(folder+key+".b","truncated"),
                "truncate one slot");
   int active=-1;
   JPWMDDAssert(JPWMDDLoadState(account,folder,record,active)==JPW_MDD_VALID &&
                record.generation==1 && record.max_percent==10.0 && active==0,
                "one corrupt slot recovers older valid slot");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,700.0,(datetime)1200,
                                   folder,record)==JPW_MDD_VALID &&
                record.generation==2 && record.max_percent==30.0,
                "write resumes from valid generation");
   JPWMDDAssert(JPWMDDWriteText(folder+key+".a","truncated") &&
                JPWMDDWriteText(folder+key+".b","truncated"),
                "truncate both slots");
   JPWMDDAssert(JPWMDDLoadState(account,folder,record,active)==JPW_MDD_INVALID,
                "both corrupt slots block load");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,600.0,(datetime)1300,
                                   folder,record)==JPW_MDD_INVALID,
                "both corrupt slots block replacement");
  }

void JPWMDDTestLockAndSchema(const string folder)
  {
   JPWAccount account;
   JPWMDDFixture(account,901301,"USD");
   string key="";
   string currency="";
   double scale=0.0;
   JPWMDDAssert(JPWMDDAccountKey(account,key,currency,scale),"lock key");
   const int lock=FileOpen(folder+key+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   JPWMDDAssert(lock!=INVALID_HANDLE,"fixture holds exclusive lock");
   JPWMDDRecord record;
   if(lock!=INVALID_HANDLE)
     {
      JPWMDDAssert(JPWMDDTestObserve(account,1000.0,900.0,(datetime)1000,
                                      folder,record)==JPW_MDD_BUSY,
                   "second instance defers while lock occupied");
      FileClose(lock);
     }
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,900.0,(datetime)1000,
                                   folder,record)==JPW_MDD_VALID,
                "sample persists after lock release");
   JPWMDDAssert(JPWMDDWriteText(folder+key+".b","JPW_MDD|2\nFUTURE|1"),
                "future schema fixture");
   int active=-1;
   JPWMDDAssert(JPWMDDLoadState(account,folder,record,active)==
                JPW_MDD_INCOMPATIBLE,
                "future schema blocks load even with old valid slot");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,500.0,(datetime)1100,
                                   folder,record)==JPW_MDD_INCOMPATIBLE,
                "future schema blocks overwrite");
  }

void JPWMDDTestReadOnlyViewer(const string folder)
  {
   JPWAccount account;
   JPWMDDFixture(account,901401,"USD");
   string key="";
   string currency="";
   double scale=0.0;
   JPWMDDAssert(JPWMDDAccountKey(account,key,currency,scale),"viewer key");
   JPWMDDRecord record;
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_ABSENT &&
                record.generation==0 &&
                !FileIsExist(folder+key+".lock"),
                "absent viewer does not create lock or fabricate zero");
   JPWMDDAssert(JPWMDDTestObserve(account,1000.0,900.0,(datetime)1000,
                                   folder,record)==JPW_MDD_VALID &&
                JPWMDDTestObserve(account,1000.0,800.0,(datetime)1100,
                                   folder,record)==JPW_MDD_VALID,
                "viewer two-slot fixture");
   string before_a="";
   string before_b="";
   JPWMDDAssert(JPWMDDReadText(folder+key+".a",before_a)==JPW_MDD_VALID &&
                JPWMDDReadText(folder+key+".b",before_b)==JPW_MDD_VALID,
                "viewer captures both slot bytes");
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_VALID &&
                record.generation==2 && record.max_percent==20.0 &&
                record.balance_at_max==1000.0 &&
                record.equity_at_max==800.0 &&
                record.observation_started_at==(datetime)1000 &&
                record.observed_at_utc==(datetime)1100 &&
                record.time_basis==JPW_MDD_TIME_BASIS,
                "viewer returns validated winning sample and start");
   string after_a="";
   string after_b="";
   JPWMDDAssert(JPWMDDReadText(folder+key+".a",after_a)==JPW_MDD_VALID &&
                JPWMDDReadText(folder+key+".b",after_b)==JPW_MDD_VALID &&
                before_a==after_a && before_b==after_b,
                "viewer leaves both record slots byte-identical");
   JPWAccount same;
   JPWMDDFixture(same,901401,"USD");
   JPWMDDAssert(JPWMDDConfirmAccount(account,same,JPW_MDD_VALID,record)==
                JPW_MDD_VALID && record.generation==2,
                "same account permits confirmed display");
   JPWAccount changed;
   JPWMDDFixture(changed,901402,"USD");
   JPWMDDAssert(JPWMDDConfirmAccount(account,changed,JPW_MDD_VALID,record)==
                JPW_MDD_ACCOUNT_UNAVAILABLE && record.generation==0,
                "account switch suppresses loaded record");
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_VALID,
                "viewer rereads before server-switch simulation");
   JPWMDDFixture(changed,901401,"USD");
   changed.server="OTHER.SYNTHETIC.SERVER";
   JPWMDDAssert(JPWMDDConfirmAccount(account,changed,JPW_MDD_VALID,record)==
                JPW_MDD_ACCOUNT_UNAVAILABLE && record.generation==0,
                "server switch suppresses loaded record");
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_VALID,
                "viewer rereads after account-switch simulations");
   JPWAccount unavailable;
   JPWMDDFixture(unavailable,0,"USD");
   JPWMDDAssert(JPWMDDConfirmAccount(account,unavailable,JPW_MDD_VALID,record)==
                JPW_MDD_ACCOUNT_UNAVAILABLE && record.generation==0,
                "unavailable account suppresses loaded record");
   const int lock=FileOpen(folder+key+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   JPWMDDAssert(lock!=INVALID_HANDLE,"viewer fixture holds writer lock");
   if(lock!=INVALID_HANDLE)
     {
      JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_BUSY &&
                   record.generation==0,
                   "viewer refuses busy record without stale value");
      FileClose(lock);
     }
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_VALID &&
                record.generation==2,
                "viewer reads again after lock release");
   JPWAccount usc;
   JPWMDDFixture(usc,901401,"USC");
   JPWMDDAssert(JPWMDDTestObserve(usc,100000.0,70000.0,(datetime)1200,
                                   folder,record)==JPW_MDD_VALID &&
                JPWMDDReadOnly(usc,folder,record)==JPW_MDD_VALID &&
                record.currency=="USC" && record.account_scale==100.0 &&
                record.max_percent==30.0 &&
                record.balance_at_max==100000.0 &&
                record.equity_at_max==70000.0,
                "viewer shows USC raw units from separate account key");
   JPWMDDAssert(JPWMDDReadOnly(account,folder,record)==JPW_MDD_VALID &&
                record.currency=="USD" && record.max_percent==20.0,
                "viewer cannot fall back across USD and USC keys");

   JPWAccount damaged;
   JPWMDDFixture(damaged,901403,"USD");
   string damaged_key="";
   JPWMDDAssert(JPWMDDAccountKey(damaged,damaged_key,currency,scale) &&
                JPWMDDTestObserve(damaged,1000.0,900.0,(datetime)1300,
                                   folder,record)==JPW_MDD_VALID &&
                JPWMDDTestObserve(damaged,1000.0,800.0,(datetime)1400,
                                   folder,record)==JPW_MDD_VALID,
                "viewer damaged fixture");
   JPWMDDAssert(JPWMDDWriteText(folder+damaged_key+".b","truncated") &&
                JPWMDDReadOnly(damaged,folder,record)==JPW_MDD_VALID &&
                record.generation==1 && record.max_percent==10.0,
                "viewer recovers older valid slot when newer is corrupt");
   JPWMDDAssert(JPWMDDWriteText(folder+damaged_key+".a","truncated") &&
                JPWMDDReadOnly(damaged,folder,record)==JPW_MDD_INVALID &&
                record.generation==0,
                "viewer rejects invalid record");
   JPWMDDAssert(JPWMDDWriteText(folder+damaged_key+".b",
                                  "JPW_MDD|2\nFUTURE|1") &&
                JPWMDDReadOnly(damaged,folder,record)==JPW_MDD_INCOMPATIBLE &&
                record.generation==0,
                "viewer distinguishes incompatible schema");
   JPWAccount orphan;
   JPWMDDFixture(orphan,901404,"USD");
   string orphan_key="";
   JPWMDDAssert(JPWMDDAccountKey(orphan,orphan_key,currency,scale) &&
                JPWMDDWriteText(folder+orphan_key+".a","truncated") &&
                JPWMDDReadOnly(orphan,folder,record)==JPW_MDD_IO_ERROR &&
                !FileIsExist(folder+orphan_key+".lock"),
                "viewer refuses slot without exclusive lock");
   JPWMDDAssert(JPWMDDReadOnly(unavailable,folder,record)==
                JPW_MDD_ACCOUNT_UNAVAILABLE && record.generation==0,
                "viewer distinguishes unavailable account");
  }

void OnStart()
  {
   const string fixture_root=JPW_MDD_FOLDER+"SyntheticTests\\";
   const string folder=fixture_root+
                       IntegerToString((long)TimeLocal())+"_"+
                       IntegerToString((long)GetTickCount64())+"\\";
   FolderCreate("JPWealth");
   FolderCreate("JPWealth\\Alavancagem");
   FolderCreate("JPWealth\\Alavancagem\\SyntheticTests");
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)))
     {
      Print("METRICS TESTS NOT_RUN: synthetic folder unavailable");
      return;
     }
   JPWMDDTestCodec();
   JPWMDDTestPersistence(folder);
   JPWMDDTestRecovery(folder);
   JPWMDDTestLockAndSchema(folder);
   JPWMDDTestReadOnlyViewer(folder);
   Print("JPW Metrics synthetic tests: ",g_mdd_passes," PASS / ",
         g_mdd_failures," FAIL");
  }

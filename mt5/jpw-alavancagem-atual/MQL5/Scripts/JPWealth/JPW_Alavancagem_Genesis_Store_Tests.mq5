#property copyright "JP Wealth"
#property version   "1.30"

#include <JPWealth/JPW_Alavancagem_Genesis_Store.mqh>

// Apenas identidades e arquivos sinteticos, em instalacao MT5 isolada.
int g_genesis_store_passes=0;
int g_genesis_store_failures=0;

void JPWGenesisStoreAssert(const bool condition,const string label)
  {
   if(condition) g_genesis_store_passes++;
   else
     {
      g_genesis_store_failures++;
      Print("FAIL: ",label);
     }
  }

void JPWGenesisStoreFixture(JPWAccount &account,const long login,
                            const string currency)
  {
   account.login=login;
   account.server="SYNTHETIC.GENESIS.TEST";
   account.currency=currency;
  }

void JPWGenesisStoreTestCodec()
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920001,"USD");
   string key="";
   JPWGenesisStoreAssert(JPWGenesisAccountKey(account,0,key),"codec key");
   JPWGenesisRecord record;
   JPWGenesisClear(record);
   record.schema=1;
   record.account_key=key;
   record.selector_ticket=0;
   record.origin_ticket=87101;
   record.identifier=88801;
   record.symbol="NZDUSD.synthetic";
   record.direction=POSITION_TYPE_BUY;
   record.opened_msc=1700000000123;
   record.reference_state=JPW_GENESIS_ACTIVE;
   record.generation=1;
   string encoded="";
   JPWGenesisStoreAssert(JPWGenesisEncode(record,encoded),"codec encode");
   JPWGenesisRecord decoded;
   JPWGenesisStoreAssert(JPWGenesisDecode(encoded,key,decoded)==
                         JPW_GENESIS_VALID &&
                         decoded.identifier==88801 &&
                         decoded.symbol=="NZDUSD.synthetic" &&
                         decoded.reference_state==JPW_GENESIS_ACTIVE,
                         "codec round trip");
   JPWGenesisStoreAssert(StringFind(encoded,"BALANCE|")<0 &&
                         StringFind(encoded,"EQUITY|")<0 &&
                         StringFind(encoded,"SL|")<0,
                         "record excludes financial values and SL");
   string damaged=encoded;
   StringReplace(damaged,"ORIGIN|87101","ORIGIN|87102");
   JPWGenesisStoreAssert(JPWGenesisDecode(damaged,key,decoded)==
                         JPW_GENESIS_INVALID,"checksum rejects changed ticket");
   JPWGenesisStoreAssert(JPWGenesisDecode("JPW_GENESIS|2\nFUTURE|1",key,
                                          decoded)==JPW_GENESIS_INCOMPATIBLE,
                         "future schema rejected");
   record.selector_ticket=87101;
   record.origin_ticket=87102;
   JPWGenesisStoreAssert(!JPWGenesisEncode(record,encoded),
                         "explicit selector must equal origin ticket");
  }

void JPWGenesisStoreTestLifecycle(const string folder)
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920101,"USD");
   JPWGenesisRecord record;
   JPWGenesisStoreAssert(JPWGenesisRead(account,0,folder,record)==
                         JPW_GENESIS_ABSENT,"first read absent");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID &&
                         record.generation==1 &&
                         record.reference_state==JPW_GENESIS_ACTIVE,
                         "first reference saved");
   JPWGenesisStoreAssert(JPWGenesisRead(account,0,folder,record)==
                         JPW_GENESIS_VALID && record.identifier==88801,
                         "reference survives reload");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID &&
                         record.generation==1,
                         "reattach does not rewrite reference");
   // O ticket corrente pode mudar; o identificador persistido continua
   // determinando a referencia, sem gravar o ticket novo.
   const long changed_current_ticket=87199;
   JPWGenesisStoreAssert(changed_current_ticket!=record.origin_ticket &&
                         record.identifier==88801,
                         "changed ticket retains identifier");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87102,88802,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000001123,record)==JPW_GENESIS_INVALID,
                         "automatic selector cannot promote successor");
   JPWGenesisStoreAssert(JPWGenesisTransition(account,0,folder,88802,
                         JPW_GENESIS_CLOSED,record)==JPW_GENESIS_INVALID,
                         "wrong identifier cannot close reference");
   JPWGenesisStoreAssert(JPWGenesisTransition(account,0,folder,88801,
                         JPW_GENESIS_CLOSED,record)==JPW_GENESIS_VALID &&
                         record.generation==2 &&
                         record.reference_state==JPW_GENESIS_CLOSED,
                         "confirmed close saves tombstone");
   JPWGenesisStoreAssert(JPWGenesisRead(account,0,folder,record)==
                         JPW_GENESIS_VALID &&
                         record.reference_state==JPW_GENESIS_CLOSED,
                         "closed tombstone survives reload");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID &&
                         record.reference_state==JPW_GENESIS_CLOSED &&
                         record.generation==2,
                         "reattach cannot reopen closed reference");
   JPWGenesisStoreAssert(JPWGenesisTransition(account,0,folder,88801,
                         JPW_GENESIS_CLOSED,record)==JPW_GENESIS_VALID &&
                         record.generation==2,
                         "repeated close is idempotent");
   JPWGenesisStoreAssert(JPWGenesisTransition(account,0,folder,88801,
                         JPW_GENESIS_REVERSED,record)==JPW_GENESIS_INVALID,
                         "terminal tombstone cannot change cause");
  }

void JPWGenesisStoreTestIsolation(const string folder,const string other_folder)
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920201,"USD");
   JPWGenesisRecord record;
   JPWGenesisStoreAssert(JPWGenesisCreate(account,87101,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID,
                         "explicit selector saved");
   JPWGenesisStoreAssert(JPWGenesisRead(account,0,folder,record)==
                         JPW_GENESIS_ABSENT,
                         "automatic selector has independent key");
   JPWGenesisStoreAssert(JPWGenesisRead(account,87102,folder,record)==
                         JPW_GENESIS_ABSENT,
                         "different explicit ticket has independent key");
   JPWGenesisStoreAssert(JPWGenesisRead(account,87101,other_folder,record)==
                         JPW_GENESIS_ABSENT,
                         "other installation folder is independent");
   JPWAccount other;
   JPWGenesisStoreFixture(other,920202,"USD");
   JPWGenesisStoreAssert(JPWGenesisRead(other,87101,folder,record)==
                         JPW_GENESIS_ABSENT,
                         "other account has independent key");
   JPWAccount usc;
   JPWGenesisStoreFixture(usc,920201,"USC");
   JPWGenesisStoreAssert(JPWGenesisRead(usc,87101,folder,record)==
                         JPW_GENESIS_ABSENT,
                         "USC and USD have separate keys");
   JPWGenesisStoreAssert(JPWGenesisCreate(usc,87101,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID,
                         "USC reference saved without price scaling");
   JPWAccount normalized;
   JPWGenesisStoreFixture(normalized,920201," usc ");
   JPWGenesisStoreAssert(JPWGenesisRead(normalized,87101,folder,record)==
                         JPW_GENESIS_VALID && record.identifier==88801,
                         "USC normalization addresses same record");
   JPWAccount switched;
   JPWGenesisStoreFixture(switched,920203,"USD");
   JPWGenesisStoreAssert(JPWGenesisRead(account,87101,folder,record)==
                         JPW_GENESIS_VALID &&
                         JPWGenesisConfirmAccount(account,switched,87101,
                           JPW_GENESIS_VALID,record)==
                         JPW_GENESIS_ACCOUNT_UNAVAILABLE &&
                         record.generation==0,
                         "account switch invalidates read result");
  }

void JPWGenesisStoreTestRecovery(const string folder)
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920301,"USD");
   JPWGenesisRecord record;
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID &&
                         JPWGenesisTransition(account,0,folder,88801,
                           JPW_GENESIS_REVERSED,record)==JPW_GENESIS_VALID &&
                         record.generation==2,
                         "reversal tombstone saved in second slot");
   string key="";
   JPWGenesisStoreAssert(JPWGenesisAccountKey(account,0,key),
                         "recovery key");
   const string base=JPWGenesisBase(folder,key);
   JPWGenesisStoreAssert(JPWGenesisWriteText(base+".b","truncated") &&
                         JPWGenesisRead(account,0,folder,record)==
                           JPW_GENESIS_VALID &&
                         record.generation==1 &&
                         record.reference_state==JPW_GENESIS_ACTIVE,
                         "valid older slot survives torn newer slot");
   JPWGenesisStoreAssert(JPWGenesisTransition(account,0,folder,88801,
                         JPW_GENESIS_REVERSED,record)==JPW_GENESIS_VALID &&
                         record.generation==2,
                         "recovered slot accepts terminal transition");
   JPWGenesisStoreAssert(JPWGenesisWriteText(base+".a","truncated") &&
                         JPWGenesisWriteText(base+".b","truncated") &&
                         JPWGenesisRead(account,0,folder,record)==
                           JPW_GENESIS_INVALID,
                         "both corrupt slots block read");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_INVALID,
                         "both corrupt slots block recreation");
   JPWAccount future;
   JPWGenesisStoreFixture(future,920302,"USD");
   JPWGenesisStoreAssert(JPWGenesisCreate(future,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID,
                         "future fixture starts valid");
   JPWGenesisStoreAssert(JPWGenesisAccountKey(future,0,key),"future key");
   JPWGenesisStoreAssert(JPWGenesisWriteText(
                         JPWGenesisBase(folder,key)+".b",
                         "JPW_GENESIS|2\nFUTURE|1") &&
                         JPWGenesisRead(future,0,folder,record)==
                           JPW_GENESIS_INCOMPATIBLE,
                         "future slot blocks old reader and writer");
   JPWGenesisStoreAssert(JPWGenesisCreate(future,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_INCOMPATIBLE,
                         "future schema blocks overwrite");
  }

void JPWGenesisStoreTestBusy(const string folder)
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920401,"USD");
   string key="";
   JPWGenesisStoreAssert(JPWGenesisAccountKey(account,0,key),"busy key");
   const string base=JPWGenesisBase(folder,key);
   const int lock=FileOpen(base+".lock",FILE_READ|FILE_WRITE|FILE_BIN);
   JPWGenesisStoreAssert(lock!=INVALID_HANDLE,"fixture holds exclusive lock");
   JPWGenesisRecord record;
   if(lock!=INVALID_HANDLE)
     {
      JPWGenesisStoreAssert(JPWGenesisRead(account,0,folder,record)==
                            JPW_GENESIS_BUSY,"read refuses occupied lock");
      JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                            "NZDUSD.synthetic",POSITION_TYPE_BUY,
                            1700000000123,record)==JPW_GENESIS_BUSY,
                            "create refuses occupied lock");
      FileClose(lock);
     }
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,folder,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID,
                         "create works after lock release");
  }

void JPWGenesisStoreTestFreshFolder(const string folder)
  {
   JPWAccount account;
   JPWGenesisStoreFixture(account,920501,"USD");
   JPWGenesisRecord record;
   const string fresh=folder+"FreshInstallation\\";
   // O teste nao cria a subpasta: a primeira selecao deve faze-lo.
   JPWGenesisStoreAssert(JPWGenesisRead(account,0,fresh,record)==
                         JPW_GENESIS_ABSENT,
                         "fresh installation read is side-effect-free");
   JPWGenesisStoreAssert(JPWGenesisCreate(account,0,fresh,87101,88801,
                         "NZDUSD.synthetic",POSITION_TYPE_BUY,
                         1700000000123,record)==JPW_GENESIS_VALID &&
                         JPWGenesisRead(account,0,fresh,record)==
                           JPW_GENESIS_VALID,
                         "first write creates local folder safely");
  }

void OnStart()
  {
   const string root=JPW_GENESIS_FOLDER+"SyntheticGenesisStoreTests\\";
   const string folder=root+IntegerToString((long)TimeLocal())+"_"+
                       IntegerToString((long)GetTickCount64())+"\\";
   const string other_folder=folder+"OtherInstallation\\";
   if(!FolderCreate(StringSubstr(folder,0,StringLen(folder)-1)) ||
      !FolderCreate(StringSubstr(other_folder,0,
                                 StringLen(other_folder)-1)))
     {
      Print("GENESIS STORE TESTS NOT_RUN: synthetic folder unavailable");
      return;
     }
   JPWGenesisStoreTestCodec();
   JPWGenesisStoreTestLifecycle(folder);
   JPWGenesisStoreTestIsolation(folder,other_folder);
   JPWGenesisStoreTestRecovery(folder);
   JPWGenesisStoreTestBusy(folder);
   JPWGenesisStoreTestFreshFolder(folder);
   Print("JPW Genesis store synthetic tests: ",g_genesis_store_passes,
         " PASS / ",g_genesis_store_failures," FAIL");
  }

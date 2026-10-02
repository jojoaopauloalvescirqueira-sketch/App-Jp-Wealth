#ifndef JPW_NOCUDA_STORE_MQH
#define JPW_NOCUDA_STORE_MQH

#include <JPWealth/JPW_NoCuda_Core.mqh>

// This database holds chart studies only. It never shares a file or schema
// with account, Stop Risk, Genesis, MDD or Raiz N records.
#define JPW_NOCUDA_STORE_SCHEMA 1
#define JPW_NOCUDA_STORE_FOLDER "JPWealth\\NoCuda\\"
#define JPW_NOCUDA_GEOMETRY_CONVENTION "AB0_C1_BARS_V1"

enum JPWNoCudaStoreResult
  {
   JPW_NOCUDA_STORE_VALID=0,
   JPW_NOCUDA_STORE_ABSENT=1,
   JPW_NOCUDA_STORE_BUSY=2,
   JPW_NOCUDA_STORE_CORRUPT=3,
   JPW_NOCUDA_STORE_INCOMPATIBLE=4,
   JPW_NOCUDA_STORE_IO_ERROR=5,
   JPW_NOCUDA_STORE_CONFLICT=6
  };

// Flat row order is intentional: DatabaseReadBind reads SELECT columns into
// this MQL5 structure in declaration order. Times are source-bar opens and
// close-availability timestamps in server time, never screen coordinates.
struct JPWNoCudaRecord
  {
   string store_key;
   string study_id;
   int revision;
   int previous_revision;
   string symbol;
   string feed;
   int source_tf;
   string convention;
   long range_first_open;
   long range_last_open;
   int range_bar_count;
   string source_signature;
   long a_open;
   long a_known;
   long a_ordinal;
   double a_close;
   long b_open;
   long b_known;
   long b_ordinal;
   double b_close;
   long c_open;
   long c_known;
   long c_ordinal;
   double c_close;
   long confirmed_utc;
   string justification;
   string checksum;
  };

struct JPWNoCudaStoreMeta
  {
   int schema_version;
   string store_key;
  };

struct JPWNoCudaStoreHead
  {
   string study_id;
   string symbol;
   string feed;
   int source_tf;
   int generation;
   int revision;
   string checksum;
  };

void JPWNoCudaStoreClear(JPWNoCudaRecord &record)
  {
   record.store_key=""; record.study_id="";
   record.revision=0; record.previous_revision=0;
   record.symbol=""; record.feed=""; record.source_tf=0;
   record.convention=""; record.range_first_open=0;
   record.range_last_open=0; record.range_bar_count=0;
   record.source_signature="";
   record.a_open=0; record.a_known=0; record.a_ordinal=0;
   record.a_close=0.0;
   record.b_open=0; record.b_known=0; record.b_ordinal=0;
   record.b_close=0.0;
   record.c_open=0; record.c_known=0; record.c_ordinal=0;
   record.c_close=0.0;
   record.confirmed_utc=0; record.justification="";
   record.checksum="";
  }

bool JPWNoCudaStoreHash(const string value,string &hex)
  {
   hex="";
   uchar source[]; uchar key[]; uchar digest[];
   const int copied=StringToCharArray(value,source,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<=0 || ArrayResize(source,copied-1)!=copied-1) return(false);
   if(CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) hex+=StringFormat("%02x",(int)digest[i]);
   return(StringLen(hex)==64);
  }

bool JPWNoCudaStoreIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     {
      const ushort c=StringGetCharacter(value,i);
      if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false);
     }
   return(true);
  }

string JPWNoCudaStoreFrame(const string value)
  { return(IntegerToString(StringLen(value))+":"+value); }

bool JPWNoCudaStoreKey(const string installation_id,const string feed,
                       string &key)
  {
   key="";
   if(installation_id=="" || feed=="" || StringLen(feed)>256)
      return(false);
   return(JPWNoCudaStoreHash(JPWNoCudaStoreFrame(installation_id)+
          JPWNoCudaStoreFrame(feed)+JPWNoCudaStoreFrame("nocuda_store_v1"),key));
  }

bool JPWNoCudaStoreNewStudyId(const string store_key,const string symbol,
                              const long created_utc,const long nonce,
                              string &study_id)
  {
   study_id="";
   if(!JPWNoCudaStoreIsHash(store_key) || symbol=="" ||
      created_utc<=0 || nonce<=0) return(false);
   return(JPWNoCudaStoreHash(JPWNoCudaStoreFrame(store_key)+
          JPWNoCudaStoreFrame(symbol)+
          JPWNoCudaStoreFrame(IntegerToString(created_utc))+
          JPWNoCudaStoreFrame(IntegerToString(nonce))+
          JPWNoCudaStoreFrame("nocuda_study_v1"),study_id));
  }

string JPWNoCudaStorePath(const string store_key)
  {
   if(!JPWNoCudaStoreIsHash(store_key)) return("");
   return(JPW_NOCUDA_STORE_FOLDER+"channels_"+store_key+".sqlite");
  }

bool JPWNoCudaStoreSafeText(const string text,const int max_chars)
  {
   if(text=="" || StringLen(text)>max_chars ||
      StringFind(text,"\r")>=0 || StringFind(text,"\n")>=0) return(false);
   return(true);
  }

bool JPWNoCudaStoreAnchorValid(const long opened,const long known,
                              const long ordinal,const double closed,
                              const JPWNoCudaRecord &record)
  {
   return(opened>=record.range_first_open &&
          opened<=record.range_last_open && known>opened &&
          ordinal>=0 && ordinal<record.range_bar_count &&
          MathIsValidNumber(closed) && closed>0.0);
  }

bool JPWNoCudaStoreRecordValid(const JPWNoCudaRecord &record)
  {
   if(!JPWNoCudaStoreIsHash(record.store_key) ||
      !JPWNoCudaStoreIsHash(record.study_id) ||
      !JPWNoCudaStoreIsHash(record.source_signature) ||
      !JPWNoCudaStoreSafeText(record.symbol,128) ||
      !JPWNoCudaStoreSafeText(record.feed,256) ||
      !JPWNoCudaStoreSafeText(record.justification,1024) ||
      record.convention!=JPW_NOCUDA_GEOMETRY_CONVENTION ||
      record.source_tf<=0 ||
      PeriodSeconds((ENUM_TIMEFRAMES)record.source_tf)<=0 ||
      record.revision<=0 ||
      record.previous_revision!=record.revision-1 ||
      record.range_first_open<=0 ||
      record.range_last_open<record.range_first_open ||
      record.range_bar_count<3 || record.range_bar_count>1000000 ||
      record.confirmed_utc<=0) return(false);
   if(!JPWNoCudaStoreAnchorValid(record.a_open,record.a_known,
                                record.a_ordinal,record.a_close,record) ||
      !JPWNoCudaStoreAnchorValid(record.b_open,record.b_known,
                                record.b_ordinal,record.b_close,record) ||
      !JPWNoCudaStoreAnchorValid(record.c_open,record.c_known,
                                record.c_ordinal,record.c_close,record))
      return(false);
   // One completed source bar has one Close. Three differently priced anchors
   // cannot claim the same source ordinal.
   if(record.a_ordinal==record.c_ordinal ||
      record.b_ordinal==record.c_ordinal)
      return(false);
   if((record.a_ordinal<record.b_ordinal && record.a_open>=record.b_open) ||
      (record.a_ordinal>record.b_ordinal && record.a_open<=record.b_open) ||
      (record.a_ordinal<record.c_ordinal && record.a_open>=record.c_open) ||
      (record.a_ordinal>record.c_ordinal && record.a_open<=record.c_open) ||
      (record.b_ordinal<record.c_ordinal && record.b_open>=record.c_open) ||
      (record.b_ordinal>record.c_ordinal && record.b_open<=record.c_open))
      return(false);
   JPWNoCudaGeometry geometry;
   string geometry_reason="";
   return(JPWNoCudaBuildGeometry(record.a_ordinal,record.a_close,
                                record.b_ordinal,record.b_close,
                                record.c_ordinal,record.c_close,
                                geometry,geometry_reason));
  }

bool JPWNoCudaStoreChecksum(const JPWNoCudaRecord &record,string &hex)
  {
   hex="";
   if(!JPWNoCudaStoreRecordValid(record)) return(false);
   const string body=
      JPWNoCudaStoreFrame(record.store_key)+
      JPWNoCudaStoreFrame(record.study_id)+
      JPWNoCudaStoreFrame(IntegerToString(record.revision))+
      JPWNoCudaStoreFrame(IntegerToString(record.previous_revision))+
      JPWNoCudaStoreFrame(record.symbol)+
      JPWNoCudaStoreFrame(record.feed)+
      JPWNoCudaStoreFrame(IntegerToString(record.source_tf))+
      JPWNoCudaStoreFrame(record.convention)+
      JPWNoCudaStoreFrame(IntegerToString(record.range_first_open))+
      JPWNoCudaStoreFrame(IntegerToString(record.range_last_open))+
      JPWNoCudaStoreFrame(IntegerToString(record.range_bar_count))+
      JPWNoCudaStoreFrame(record.source_signature)+
      JPWNoCudaStoreFrame(IntegerToString(record.a_open))+
      JPWNoCudaStoreFrame(IntegerToString(record.a_known))+
      JPWNoCudaStoreFrame(IntegerToString(record.a_ordinal))+
      JPWNoCudaStoreFrame(DoubleToString(record.a_close,-16))+
      JPWNoCudaStoreFrame(IntegerToString(record.b_open))+
      JPWNoCudaStoreFrame(IntegerToString(record.b_known))+
      JPWNoCudaStoreFrame(IntegerToString(record.b_ordinal))+
      JPWNoCudaStoreFrame(DoubleToString(record.b_close,-16))+
      JPWNoCudaStoreFrame(IntegerToString(record.c_open))+
      JPWNoCudaStoreFrame(IntegerToString(record.c_known))+
      JPWNoCudaStoreFrame(IntegerToString(record.c_ordinal))+
      JPWNoCudaStoreFrame(DoubleToString(record.c_close,-16))+
      JPWNoCudaStoreFrame(IntegerToString(record.confirmed_utc))+
      JPWNoCudaStoreFrame(record.justification);
   return(JPWNoCudaStoreHash(body,hex));
  }

JPWNoCudaStoreResult JPWNoCudaStoreErrorStatus(const int error)
  {
   if(error==ERR_DATABASE_BUSY || error==ERR_DATABASE_LOCKED)
      return(JPW_NOCUDA_STORE_BUSY);
   if(error==ERR_DATABASE_CORRUPT || error==ERR_DATABASE_NOTADB)
      return(JPW_NOCUDA_STORE_CORRUPT);
   return(JPW_NOCUDA_STORE_IO_ERROR);
  }

bool JPWNoCudaStoreExecutePrepared(const int q)
  {
   if(q==INVALID_HANDLE) return(false);
   ResetLastError();
   DatabaseRead(q);
   return(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
  }

bool JPWNoCudaStoreSchemaEmpty(const int db,bool &empty)
  {
   empty=false;
   const int q=DatabasePrepare(db,
      "SELECT COUNT(*) FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'");
   if(q==INVALID_HANDLE) return(false);
   int count=-1;
   bool ok=DatabaseRead(q) && DatabaseColumnInteger(q,0,count);
   if(ok)
     {
      ResetLastError();
      ok=!DatabaseRead(q) && GetLastError()==ERR_DATABASE_NO_MORE_DATA;
     }
   DatabaseFinalize(q);
   if(!ok || count<0) return(false);
   empty=(count==0);
   return(true);
  }

bool JPWNoCudaStoreInit(const int db,const string store_key)
  {
   if(!DatabaseTransactionBegin(db)) return(false);
   bool ok=DatabaseExecute(db,
      "CREATE TABLE nocuda_meta (schema_version INTEGER NOT NULL,"
      "store_key TEXT NOT NULL PRIMARY KEY)") &&
      DatabaseExecute(db,
      "CREATE TABLE nocuda_heads (study_id TEXT PRIMARY KEY,"
      "symbol TEXT NOT NULL,feed TEXT NOT NULL,source_tf INTEGER NOT NULL,"
      "generation INTEGER NOT NULL,revision INTEGER NOT NULL,"
      "checksum TEXT NOT NULL)") &&
      DatabaseExecute(db,
      "CREATE TABLE nocuda_revisions ("
      "store_key TEXT NOT NULL,study_id TEXT NOT NULL,"
      "revision INTEGER NOT NULL,previous_revision INTEGER NOT NULL,"
      "symbol TEXT NOT NULL,feed TEXT NOT NULL,source_tf INTEGER NOT NULL,"
      "convention TEXT NOT NULL,range_first_open INTEGER NOT NULL,"
      "range_last_open INTEGER NOT NULL,range_bar_count INTEGER NOT NULL,"
      "source_signature TEXT NOT NULL,a_open INTEGER NOT NULL,"
      "a_known INTEGER NOT NULL,a_ordinal INTEGER NOT NULL,a_close REAL NOT NULL,"
      "b_open INTEGER NOT NULL,b_known INTEGER NOT NULL,"
      "b_ordinal INTEGER NOT NULL,b_close REAL NOT NULL,"
      "c_open INTEGER NOT NULL,c_known INTEGER NOT NULL,"
      "c_ordinal INTEGER NOT NULL,c_close REAL NOT NULL,"
      "confirmed_utc INTEGER NOT NULL,justification TEXT NOT NULL,"
      "checksum TEXT NOT NULL,PRIMARY KEY(study_id,revision))") &&
      DatabaseExecute(db,
      "CREATE TRIGGER nocuda_revision_no_update BEFORE UPDATE ON "
      "nocuda_revisions BEGIN SELECT RAISE(ABORT,'immutable revision'); END") &&
      DatabaseExecute(db,
      "CREATE TRIGGER nocuda_revision_no_delete BEFORE DELETE ON "
      "nocuda_revisions BEGIN SELECT RAISE(ABORT,'immutable revision'); END");
   if(ok)
     {
      const int q=DatabasePrepare(db,"INSERT INTO nocuda_meta VALUES(?1,?2)");
      ok=q!=INVALID_HANDLE;
      if(ok)
        {
         ok=DatabaseBind(q,0,JPW_NOCUDA_STORE_SCHEMA) &&
            DatabaseBind(q,1,store_key) &&
            JPWNoCudaStoreExecutePrepared(q);
         DatabaseFinalize(q);
        }
     }
   if(ok && DatabaseTransactionCommit(db)) return(true);
   DatabaseTransactionRollback(db);
   return(false);
  }

JPWNoCudaStoreResult JPWNoCudaStoreCheckMeta(const int db,
                                              const string store_key,
                                              string &reason)
  {
   if(!DatabaseTableExists(db,"nocuda_meta") ||
      !DatabaseTableExists(db,"nocuda_heads") ||
      !DatabaseTableExists(db,"nocuda_revisions"))
     { reason="Estrutura do estudo ausente ou incompleta";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   const int q=DatabasePrepare(db,
      "SELECT schema_version,store_key FROM nocuda_meta LIMIT 2");
   if(q==INVALID_HANDLE)
     { reason="Metadados indisponiveis"; return(JPW_NOCUDA_STORE_IO_ERROR); }
   JPWNoCudaStoreMeta meta;
   ResetLastError();
   bool ok=DatabaseReadBind(q,meta);
   const int first_error=GetLastError();
   if(ok)
     {
      JPWNoCudaStoreMeta duplicate;
      ResetLastError();
      ok=!DatabaseReadBind(q,duplicate) &&
         GetLastError()==ERR_DATABASE_NO_MORE_DATA;
     }
   DatabaseFinalize(q);
   if(!ok)
     { reason=(first_error==ERR_DATABASE_NO_MORE_DATA ?
               "Metadados de estudo ausentes" :
               "Metadados de estudo incompletos");
       return(JPW_NOCUDA_STORE_CORRUPT); }
   if(meta.schema_version!=JPW_NOCUDA_STORE_SCHEMA)
     { reason="Versao futura ou incompativel do estudo";
       return(JPW_NOCUDA_STORE_INCOMPATIBLE); }
   if(meta.store_key!=store_key)
     { reason="Identidade do armazenamento diverge";
       return(JPW_NOCUDA_STORE_INCOMPATIBLE); }
   const int trigger=DatabasePrepare(db,
      "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND "
      "name IN ('nocuda_revision_no_update','nocuda_revision_no_delete')");
   if(trigger==INVALID_HANDLE)
     { reason="Protecao das revisoes indisponivel";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int trigger_count=0;
   const bool protected_revisions=DatabaseRead(trigger) &&
      DatabaseColumnInteger(trigger,0,trigger_count) && trigger_count==2;
   DatabaseFinalize(trigger);
   if(!protected_revisions)
     { reason="Protecao das revisoes ausente";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   const int orphan=DatabasePrepare(db,
      "SELECT COUNT(*) FROM nocuda_revisions r LEFT JOIN nocuda_heads h "
      "ON h.study_id=r.study_id WHERE h.study_id IS NULL");
   if(orphan==INVALID_HANDLE)
     { reason="Cadeia de revisoes indisponivel";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int orphan_count=0;
   const bool linked=DatabaseRead(orphan) &&
      DatabaseColumnInteger(orphan,0,orphan_count) && orphan_count==0;
   DatabaseFinalize(orphan);
   if(!linked)
     { reason="Revisoes isoladas detectadas";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   const int missing=DatabasePrepare(db,
      "SELECT COUNT(*) FROM nocuda_heads h LEFT JOIN nocuda_revisions r "
      "ON r.study_id=h.study_id AND r.revision=h.revision "
      "WHERE r.study_id IS NULL");
   if(missing==INVALID_HANDLE)
     { reason="Integridade dos cabecalhos indisponivel";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int missing_count=0;
   const bool complete=DatabaseRead(missing) &&
      DatabaseColumnInteger(missing,0,missing_count) && missing_count==0;
   DatabaseFinalize(missing);
   if(!complete)
     { reason="Revisao principal de estudo ausente";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   return(JPW_NOCUDA_STORE_VALID);
  }

JPWNoCudaStoreResult JPWNoCudaStoreOpen(const string store_key,
                                        const bool write,int &db,
                                        string &reason)
  {
   db=INVALID_HANDLE; reason="";
   const string path=JPWNoCudaStorePath(store_key);
   if(path=="")
     { reason="Chave do armazenamento invalida";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   // Remember existence before DatabaseOpen(CREATE): a preexisting zero-byte
   // or truncated file is damaged user state, not a new installation.
   const bool existed=FileIsExist(path);
   if(!existed && !write)
     { reason="Nenhum estudo salvo"; return(JPW_NOCUDA_STORE_ABSENT); }
   // Existing directories may be reported as already present by FolderCreate;
   // DatabaseOpen is the authoritative accessibility check in either case.
   if(write)
     { FolderCreate("JPWealth"); FolderCreate("JPWealth\\NoCuda"); }
   ResetLastError();
   db=DatabaseOpen(path,write ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE :
                              DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE)
     { const JPWNoCudaStoreResult result=JPWNoCudaStoreErrorStatus(GetLastError());
       reason="Banco de estudos indisponivel"; return(result); }
   // A concurrent editor is reported promptly. No implicit wait/retry can
   // turn an old draft into a newly accepted revision.
   if(!DatabaseExecute(db,"PRAGMA busy_timeout=0"))
     { const JPWNoCudaStoreResult result=JPWNoCudaStoreErrorStatus(GetLastError());
       DatabaseClose(db); db=INVALID_HANDLE;
       reason="Configuracao de acesso ao estudo falhou";
       return(result); }
   bool empty=false;
   const bool tested=JPWNoCudaStoreSchemaEmpty(db,empty);
   JPWNoCudaStoreResult result=JPW_NOCUDA_STORE_VALID;
   if(tested && empty && write && !existed)
     {
      if(!JPWNoCudaStoreInit(db,store_key))
        { reason="Criacao do banco de estudos nao confirmada";
          result=JPWNoCudaStoreErrorStatus(GetLastError()); }
     }
   else if(!tested || empty)
     { reason="Banco de estudos vazio ou ilegivel";
       result=JPW_NOCUDA_STORE_CORRUPT; }
   else
      result=JPWNoCudaStoreCheckMeta(db,store_key,reason);
   if(result!=JPW_NOCUDA_STORE_VALID)
     { DatabaseClose(db); db=INVALID_HANDLE; }
   return(result);
  }

JPWNoCudaStoreResult JPWNoCudaStoreReadRevisionInDb(
                            const int db,const string store_key,
                            const string study_id,const int revision,
                            JPWNoCudaRecord &record,string &reason)
  {
   JPWNoCudaStoreClear(record);
   const int q=DatabasePrepare(db,
      "SELECT store_key,study_id,revision,previous_revision,symbol,feed,"
      "source_tf,convention,range_first_open,range_last_open,"
      "range_bar_count,source_signature,a_open,a_known,a_ordinal,a_close,"
      "b_open,b_known,b_ordinal,b_close,c_open,c_known,c_ordinal,c_close,"
      "confirmed_utc,justification,checksum FROM nocuda_revisions "
      "WHERE study_id=?1 AND revision=?2");
   if(q==INVALID_HANDLE)
     { reason="Consulta da revisao falhou";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   if(!DatabaseBind(q,0,study_id) || !DatabaseBind(q,1,revision))
     { DatabaseFinalize(q); reason="Filtro da revisao falhou";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   ResetLastError();
   const bool found=DatabaseReadBind(q,record);
   const int read_error=GetLastError();
   bool single=found;
   if(found)
     {
      JPWNoCudaRecord duplicate;
      ResetLastError();
      single=!DatabaseReadBind(q,duplicate) &&
             GetLastError()==ERR_DATABASE_NO_MORE_DATA;
     }
   DatabaseFinalize(q);
   if(!found)
     { reason=(read_error==ERR_DATABASE_NO_MORE_DATA ?
               "Revisao nao encontrada" : "Falha ao ler revisao");
       return(read_error==ERR_DATABASE_NO_MORE_DATA ?
              JPW_NOCUDA_STORE_ABSENT : JPW_NOCUDA_STORE_IO_ERROR); }
   string expected="";
   if(!single || record.store_key!=store_key ||
      record.study_id!=study_id || record.revision!=revision ||
      !JPWNoCudaStoreChecksum(record,expected) ||
      record.checksum!=expected)
     { JPWNoCudaStoreClear(record);
       reason="Revisao incompleta ou checksum invalido";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   return(JPW_NOCUDA_STORE_VALID);
  }

JPWNoCudaStoreResult JPWNoCudaStoreReadHeadInDb(
                            const int db,const string store_key,
                            const string study_id,JPWNoCudaRecord &record,
                            string &reason)
  {
   JPWNoCudaStoreClear(record);
   const int q=DatabasePrepare(db,
      "SELECT study_id,symbol,feed,source_tf,generation,revision,checksum "
      "FROM nocuda_heads WHERE study_id=?1");
   if(q==INVALID_HANDLE)
     { reason="Cabecalho do estudo indisponivel";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   if(!DatabaseBind(q,0,study_id))
     { DatabaseFinalize(q); reason="Filtro do estudo falhou";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   JPWNoCudaStoreHead head;
   ResetLastError();
   const bool found=DatabaseReadBind(q,head);
   const int read_error=GetLastError();
   DatabaseFinalize(q);
   if(!found)
     {
      if(read_error!=ERR_DATABASE_NO_MORE_DATA)
        { reason="Leitura do cabecalho falhou";
          return(JPW_NOCUDA_STORE_IO_ERROR); }
      // A missing head with orphaned immutable revisions is corruption,
      // never permission to silently restart a saved study.
      const int orphan=DatabasePrepare(db,
         "SELECT COUNT(*) FROM nocuda_revisions WHERE study_id=?1");
      if(orphan==INVALID_HANDLE)
        { reason="Consulta de revisoes isoladas falhou";
          return(JPW_NOCUDA_STORE_IO_ERROR); }
      int count=-1;
      const bool ok=DatabaseBind(orphan,0,study_id) &&
                    DatabaseRead(orphan) &&
                    DatabaseColumnInteger(orphan,0,count);
      DatabaseFinalize(orphan);
      if(!ok || count<0)
        { reason="Revisoes isoladas indisponiveis";
          return(JPW_NOCUDA_STORE_IO_ERROR); }
      reason=(count==0 ? "Estudo ainda nao confirmado" :
                         "Revisoes sem cabecalho; reparo necessario");
      return(count==0 ? JPW_NOCUDA_STORE_ABSENT :
                        JPW_NOCUDA_STORE_CORRUPT);
     }
   if(head.study_id!=study_id || head.generation<=0 ||
      head.revision!=head.generation ||
      !JPWNoCudaStoreIsHash(head.checksum))
     { reason="Cabecalho do estudo invalido";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   const JPWNoCudaStoreResult result=JPWNoCudaStoreReadRevisionInDb(
      db,store_key,study_id,head.revision,record,reason);
   if(result!=JPW_NOCUDA_STORE_VALID)
     { if(result==JPW_NOCUDA_STORE_ABSENT)
         { reason="Revisao principal ausente";
           return(JPW_NOCUDA_STORE_CORRUPT); }
       return(result); }
   if(record.symbol!=head.symbol || record.feed!=head.feed ||
      record.source_tf!=head.source_tf ||
      record.checksum!=head.checksum)
     { JPWNoCudaStoreClear(record);
       reason="Cabecalho e revisao divergem";
       return(JPW_NOCUDA_STORE_CORRUPT); }
   return(JPW_NOCUDA_STORE_VALID);
  }

JPWNoCudaStoreResult JPWNoCudaStoreLoadHead(
                            const string store_key,const string study_id,
                            JPWNoCudaRecord &record,string &reason)
  {
   JPWNoCudaStoreClear(record); reason="";
   if(!JPWNoCudaStoreIsHash(study_id))
     { reason="Identidade do estudo invalida";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int db=INVALID_HANDLE;
   const JPWNoCudaStoreResult opened=JPWNoCudaStoreOpen(
      store_key,false,db,reason);
   if(opened!=JPW_NOCUDA_STORE_VALID) return(opened);
   const JPWNoCudaStoreResult result=JPWNoCudaStoreReadHeadInDb(
      db,store_key,study_id,record,reason);
   DatabaseClose(db);
   return(result);
  }

JPWNoCudaStoreResult JPWNoCudaStoreLoadRevision(
                            const string store_key,const string study_id,
                            const int revision,JPWNoCudaRecord &record,
                            string &reason)
  {
   JPWNoCudaStoreClear(record); reason="";
   if(!JPWNoCudaStoreIsHash(study_id) || revision<=0)
     { reason="Numero ou identidade da revisao invalida";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int db=INVALID_HANDLE;
   const JPWNoCudaStoreResult opened=JPWNoCudaStoreOpen(
      store_key,false,db,reason);
   if(opened!=JPW_NOCUDA_STORE_VALID) return(opened);
   JPWNoCudaRecord head;
   JPWNoCudaStoreResult result=JPWNoCudaStoreReadHeadInDb(
      db,store_key,study_id,head,reason);
   if(result==JPW_NOCUDA_STORE_VALID)
     {
      if(revision>head.revision)
        { reason="Revisao futura nao existe";
          result=JPW_NOCUDA_STORE_ABSENT; }
      else
        {
         result=JPWNoCudaStoreReadRevisionInDb(
            db,store_key,study_id,revision,record,reason);
         if(result==JPW_NOCUDA_STORE_ABSENT)
           { reason="Revisao da cadeia ausente";
             result=JPW_NOCUDA_STORE_CORRUPT; }
         else if(result==JPW_NOCUDA_STORE_VALID &&
                 (record.symbol!=head.symbol || record.feed!=head.feed ||
                  record.source_tf!=head.source_tf))
           { JPWNoCudaStoreClear(record);
             reason="Contexto de revisao diverge";
             result=JPW_NOCUDA_STORE_CORRUPT; }
        }
     }
   DatabaseClose(db);
   return(result);
  }

JPWNoCudaStoreResult JPWNoCudaStoreList(
                            const string store_key,const string symbol,
                            const int source_tf,string &study_ids[],
                            string &reason)
  {
   ArrayResize(study_ids,0); reason="";
   if(!JPWNoCudaStoreSafeText(symbol,128) || source_tf<0)
     { reason="Filtro dos estudos invalido";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int db=INVALID_HANDLE;
   const JPWNoCudaStoreResult opened=JPWNoCudaStoreOpen(
      store_key,false,db,reason);
   if(opened!=JPW_NOCUDA_STORE_VALID) return(opened);
   const int q=DatabasePrepare(db,
      "SELECT h.study_id FROM nocuda_heads h JOIN nocuda_revisions r "
      "ON r.study_id=h.study_id AND r.revision=h.revision "
      "WHERE h.symbol=?1 AND (?2=0 OR h.source_tf=?2) "
      "ORDER BY r.confirmed_utc DESC,h.study_id");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,symbol) ||
      !DatabaseBind(q,1,source_tf))
     { if(q!=INVALID_HANDLE) DatabaseFinalize(q);
       DatabaseClose(db); reason="Lista de estudos indisponivel";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   JPWNoCudaStoreResult result=JPW_NOCUDA_STORE_VALID;
   ResetLastError();
   while(DatabaseRead(q))
     {
      string id="";
      if(!DatabaseColumnText(q,0,id) || !JPWNoCudaStoreIsHash(id))
        { result=JPW_NOCUDA_STORE_CORRUPT; break; }
      const int count=ArraySize(study_ids);
      if(count>=1000 || ArrayResize(study_ids,count+1)!=count+1)
        { result=JPW_NOCUDA_STORE_IO_ERROR; break; }
      study_ids[count]=id;
     }
   const int last_error=GetLastError();
   DatabaseFinalize(q);
   if(result==JPW_NOCUDA_STORE_VALID &&
      last_error!=ERR_DATABASE_NO_MORE_DATA)
      result=JPWNoCudaStoreErrorStatus(last_error);
   for(int i=0;result==JPW_NOCUDA_STORE_VALID &&
       i<ArraySize(study_ids);i++)
     {
      JPWNoCudaRecord record;
      result=JPWNoCudaStoreReadHeadInDb(db,store_key,
                                       study_ids[i],record,reason);
      if(result==JPW_NOCUDA_STORE_VALID && record.symbol!=symbol)
        { result=JPW_NOCUDA_STORE_CORRUPT;
          reason="Lista e estudo divergem"; }
     }
   DatabaseClose(db);
   if(result!=JPW_NOCUDA_STORE_VALID) ArrayResize(study_ids,0);
   if(result==JPW_NOCUDA_STORE_VALID && ArraySize(study_ids)==0)
     { reason="Nenhum estudo salvo para o simbolo";
       return(JPW_NOCUDA_STORE_ABSENT); }
   return(result);
  }

bool JPWNoCudaStoreInsertRevision(const int db,const JPWNoCudaRecord &record)
  {
   const int q=DatabasePrepare(db,
      "INSERT INTO nocuda_revisions VALUES("
      "?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,"
      "?16,?17,?18,?19,?20,?21,?22,?23,?24,?25,?26,?27)");
   if(q==INVALID_HANDLE) return(false);
   const bool ok=
      DatabaseBind(q,0,record.store_key) &&
      DatabaseBind(q,1,record.study_id) &&
      DatabaseBind(q,2,record.revision) &&
      DatabaseBind(q,3,record.previous_revision) &&
      DatabaseBind(q,4,record.symbol) &&
      DatabaseBind(q,5,record.feed) &&
      DatabaseBind(q,6,record.source_tf) &&
      DatabaseBind(q,7,record.convention) &&
      DatabaseBind(q,8,record.range_first_open) &&
      DatabaseBind(q,9,record.range_last_open) &&
      DatabaseBind(q,10,record.range_bar_count) &&
      DatabaseBind(q,11,record.source_signature) &&
      DatabaseBind(q,12,record.a_open) &&
      DatabaseBind(q,13,record.a_known) &&
      DatabaseBind(q,14,record.a_ordinal) &&
      DatabaseBind(q,15,record.a_close) &&
      DatabaseBind(q,16,record.b_open) &&
      DatabaseBind(q,17,record.b_known) &&
      DatabaseBind(q,18,record.b_ordinal) &&
      DatabaseBind(q,19,record.b_close) &&
      DatabaseBind(q,20,record.c_open) &&
      DatabaseBind(q,21,record.c_known) &&
      DatabaseBind(q,22,record.c_ordinal) &&
      DatabaseBind(q,23,record.c_close) &&
      DatabaseBind(q,24,record.confirmed_utc) &&
      DatabaseBind(q,25,record.justification) &&
      DatabaseBind(q,26,record.checksum) &&
      JPWNoCudaStoreExecutePrepared(q);
   DatabaseFinalize(q);
   return(ok);
  }

bool JPWNoCudaStoreWriteHead(const int db,
                             const JPWNoCudaRecord &record,
                             const JPWNoCudaRecord &previous)
  {
   if(record.revision==1)
     {
      const int q=DatabasePrepare(db,
         "INSERT INTO nocuda_heads VALUES(?1,?2,?3,?4,?5,?6,?7)");
      if(q==INVALID_HANDLE) return(false);
      const bool ok=DatabaseBind(q,0,record.study_id) &&
         DatabaseBind(q,1,record.symbol) &&
         DatabaseBind(q,2,record.feed) &&
         DatabaseBind(q,3,record.source_tf) &&
         DatabaseBind(q,4,record.revision) &&
         DatabaseBind(q,5,record.revision) &&
         DatabaseBind(q,6,record.checksum) &&
         JPWNoCudaStoreExecutePrepared(q);
      DatabaseFinalize(q);
      return(ok);
     }
   const int q=DatabasePrepare(db,
      "UPDATE nocuda_heads SET generation=?1,revision=?2,checksum=?3 "
      "WHERE study_id=?4 AND generation=?5 AND checksum=?6");
   if(q==INVALID_HANDLE) return(false);
   const bool ok=DatabaseBind(q,0,record.revision) &&
      DatabaseBind(q,1,record.revision) &&
      DatabaseBind(q,2,record.checksum) &&
      DatabaseBind(q,3,record.study_id) &&
      DatabaseBind(q,4,previous.revision) &&
      DatabaseBind(q,5,previous.checksum) &&
      JPWNoCudaStoreExecutePrepared(q);
   DatabaseFinalize(q);
   if(!ok) return(false);
   const int check=DatabasePrepare(db,"SELECT changes()");
   if(check==INVALID_HANDLE) return(false);
   int changed=0;
   const bool one=DatabaseRead(check) &&
                  DatabaseColumnInteger(check,0,changed) && changed==1;
   DatabaseFinalize(check);
   return(one);
  }

// Confirm is the only path that creates a revision. `expected_generation` is
// the head generation shown when the draft was opened (0 for a new study).
// Concurrent editors must reload; this function never overwrites a revision.
JPWNoCudaStoreResult JPWNoCudaStoreConfirm(
                            JPWNoCudaRecord &candidate,
                            const int expected_generation,string &reason)
  {
   reason="";
   if(expected_generation<0 || expected_generation>=2147483647 ||
      !JPWNoCudaStoreIsHash(candidate.store_key) ||
      !JPWNoCudaStoreIsHash(candidate.study_id))
     { reason="Identidade ou geracao invalida";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   JPWNoCudaRecord next=candidate;
   next.revision=expected_generation+1;
   next.previous_revision=expected_generation;
   next.checksum="";
   if(!JPWNoCudaStoreChecksum(next,next.checksum))
     { reason="Estudo incompleto ou geometria invalida";
       return(JPW_NOCUDA_STORE_IO_ERROR); }
   int db=INVALID_HANDLE;
   JPWNoCudaStoreResult result=JPWNoCudaStoreOpen(
      next.store_key,true,db,reason);
   if(result!=JPW_NOCUDA_STORE_VALID) return(result);
   ResetLastError();
   bool begun=DatabaseTransactionBegin(db);
   if(!begun)
     { result=JPWNoCudaStoreErrorStatus(GetLastError());
       reason="Banco ocupado ou indisponivel"; DatabaseClose(db);
       return(result); }
   // SQLite's first write obtains the writer lock before read/compare/write.
   ResetLastError();
   bool ok=DatabaseExecute(db,
      "UPDATE nocuda_meta SET schema_version=schema_version");
   if(!ok)
     { result=JPWNoCudaStoreErrorStatus(GetLastError());
       reason="Outro editor ocupa o banco"; }
   JPWNoCudaRecord previous;
   JPWNoCudaStoreResult previous_result=JPW_NOCUDA_STORE_IO_ERROR;
   if(ok)
     {
      previous_result=JPWNoCudaStoreReadHeadInDb(db,next.store_key,
                                                 next.study_id,previous,reason);
      if(previous_result!=JPW_NOCUDA_STORE_VALID &&
         previous_result!=JPW_NOCUDA_STORE_ABSENT)
        { ok=false; result=previous_result; }
     }
   if(ok && ((previous_result==JPW_NOCUDA_STORE_ABSENT &&
              expected_generation!=0) ||
             (previous_result==JPW_NOCUDA_STORE_VALID &&
              expected_generation!=previous.revision)))
     { ok=false; result=JPW_NOCUDA_STORE_CONFLICT;
       reason="Outra instancia confirmou uma revisao; atualize o estudo"; }
   if(ok && previous_result==JPW_NOCUDA_STORE_VALID &&
      (next.symbol!=previous.symbol || next.feed!=previous.feed ||
       next.source_tf!=previous.source_tf ||
       next.convention!=previous.convention))
     { ok=false; result=JPW_NOCUDA_STORE_INCOMPATIBLE;
       reason="Revisao mudou o simbolo, feed ou periodo-fonte"; }
   if(ok)
     {
      ResetLastError();
      ok=JPWNoCudaStoreInsertRevision(db,next) &&
         JPWNoCudaStoreWriteHead(db,next,previous);
      if(!ok)
        { result=JPWNoCudaStoreErrorStatus(GetLastError());
          reason="Gravacao da revisao recusada"; }
     }
   JPWNoCudaRecord verified;
   if(ok)
     {
      const JPWNoCudaStoreResult reread=JPWNoCudaStoreReadHeadInDb(
         db,next.store_key,next.study_id,verified,reason);
      ok=reread==JPW_NOCUDA_STORE_VALID &&
         verified.revision==next.revision &&
         verified.checksum==next.checksum;
      if(!ok)
        { result=(reread==JPW_NOCUDA_STORE_VALID ?
                  JPW_NOCUDA_STORE_CORRUPT : reread);
          if(reason=="") reason="Releitura da revisao falhou"; }
     }
   if(ok)
     {
      ResetLastError();
      ok=DatabaseTransactionCommit(db);
      if(!ok)
        { result=JPWNoCudaStoreErrorStatus(GetLastError());
          reason="Commit da revisao nao confirmado"; }
     }
   if(!ok) DatabaseTransactionRollback(db);
   DatabaseClose(db);
   if(!ok) return(result);
   JPWNoCudaRecord durable;
   const JPWNoCudaStoreResult after=JPWNoCudaStoreLoadHead(
      next.store_key,next.study_id,durable,reason);
   if(after!=JPW_NOCUDA_STORE_VALID ||
      durable.revision!=next.revision ||
      durable.checksum!=next.checksum)
     { if(reason=="") reason="Resultado da gravacao desconhecido; releia o estudo";
       return(after==JPW_NOCUDA_STORE_VALID ?
              JPW_NOCUDA_STORE_IO_ERROR : after); }
   candidate=durable;
   reason="";
   return(JPW_NOCUDA_STORE_VALID);
  }

#endif

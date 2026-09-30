#ifndef JPW_ALAVANCAGEM_STOP_RISK_STORE_MQH
#define JPW_ALAVANCAGEM_STOP_RISK_STORE_MQH

#include <JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh>
#include <JPWealth/JPW_Alavancagem_Store_Result.mqh>
#include <JPWealth/JPW_Alavancagem_Observer_Presence.mqh>

// Separate transactional SQLite store. It never changes the immutable Raiz N
// observer snapshots, MDD, Genesis, USC or user presentation preferences.
#define JPW_STOP_RISK_SCHEMA 1
#define JPW_STOP_RISK_FOLDER "JPWealth\\Alavancagem\\"
#define JPW_STOP_RISK_MAX_AGE_MS 30000
#define JPW_STOP_RISK_PUBLISHER_LEASE_MS 30000

struct JPWStopRiskMeta
  {
   int schema_version;
   string account_key;
   string owner_token;
   int active;
   long heartbeat_utc;
   long heartbeat_mono_ms;
  };

string JPWStopRiskDatabasePath(const string account_key)
  {
   if(!JPWRaizNIsHash(account_key)) return("");
   return(JPW_STOP_RISK_FOLDER+"stop_risk_"+
          StringSubstr(account_key,0,24)+".sqlite");
  }

// The SQLite heartbeat survives a terminal restart, while this terminal
// global variable does not. The EA must create it with GlobalVariableTemp
// before publishing; the indicator only reads it and never creates it.
string JPWStopRiskLeaseName(const string publisher_token)
  {
   if(!JPWRaizNIsHash(publisher_token)) return("");
   return("JPWSR_"+StringSubstr(publisher_token,0,48));
  }

bool JPWStopRiskLeaseMatches(const string publisher_token,
                             const long observed_mono_ms)
  {
   const string name=JPWStopRiskLeaseName(publisher_token);
   if(name=="" || observed_mono_ms<=0) return(false);
   double observed=0.0;
   return(GlobalVariableGet(name,observed) &&
          observed==(double)observed_mono_ms);
  }

bool JPWStopRiskChecksum(JPWStopRiskSample &sample,
                         JPWStopRiskRow &rows[],string &hash)
  {
   hash="";
   if(!JPWRaizNIsHash(sample.account_key) || sample.generation<=0 ||
      sample.observed_utc<=0 || sample.observed_mono_ms<=0 ||
      sample.currency=="" ||
      sample.currency!=JPWNormalizeCurrency(sample.currency) ||
      !JPWFinitePositive(sample.balance) ||
      sample.row_count!=ArraySize(rows) ||
      sample.row_count>JPW_STOP_RISK_MAX_ROWS ||
      !JPWRaizNIsHash(sample.composition_digest) ||
      !JPWRaizNIsHash(sample.publisher_token)) return(false);
   string raw_digest="";
   if(!JPWStopRiskRawDigest(sample,rows,raw_digest) ||
      raw_digest!=sample.composition_digest) return(false);
   string body=JPWRaizNFrame(sample.account_key)+
      JPWRaizNFrame(IntegerToString(sample.generation))+
      JPWRaizNFrame(IntegerToString(sample.observed_utc))+
      JPWRaizNFrame(IntegerToString(sample.observed_mono_ms))+
      JPWRaizNFrame(sample.currency)+
      JPWRaizNFrame(DoubleToString(sample.balance,-16))+
      JPWRaizNFrame(IntegerToString(sample.margin_mode))+
      JPWRaizNFrame(sample.composition_digest)+
      JPWRaizNFrame(IntegerToString(sample.row_count))+
      JPWRaizNFrame(sample.publisher_token);
   for(int i=0;i<ArraySize(rows);i++)
     {
      JPWStopRiskRow row=rows[i];
      if(!JPWStopRiskRowValid(row) ||
         (i>0 && JPWStopRiskCompareRows(rows[i-1],row)>=0))
         return(false);
      body+=JPWRaizNFrame(IntegerToString(row.kind))+
            JPWRaizNFrame(IntegerToString(row.ticket))+
            JPWRaizNFrame(IntegerToString(row.identifier))+
            JPWRaizNFrame(IntegerToString(row.opened_msc))+
            JPWRaizNFrame(row.symbol)+
            JPWRaizNFrame(IntegerToString(row.side))+
            JPWRaizNFrame(IntegerToString(row.order_type))+
            JPWRaizNFrame(IntegerToString(row.valid))+
            JPWRaizNFrame(DoubleToString(row.volume,-16))+
            JPWRaizNFrame(DoubleToString(row.entry,-16))+
            JPWRaizNFrame(DoubleToString(row.sl,-16))+
            JPWRaizNFrame(DoubleToString(row.risk_money,-16))+
            JPWRaizNFrame(DoubleToString(row.additional_money,-16))+
            JPWRaizNFrame(row.reason)+
            JPWRaizNFrame(IntegerToString(row.additional_valid))+
            JPWRaizNFrame(row.additional_reason);
     }
   return(JPWRaizNHash(body,hash));
  }

bool JPWStopRiskExecutePrepared(const int q)
  {
   if(q==INVALID_HANDLE) return(false);
   ResetLastError();
   DatabaseRead(q);
   return(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
  }

bool JPWStopRiskInitDatabase(const int db,const string account_key)
  {
   if(db==INVALID_HANDLE || !JPWRaizNIsHash(account_key) ||
      !DatabaseTransactionBegin(db)) return(false);
   bool ok=DatabaseExecute(db,
      "CREATE TABLE stop_risk_meta (schema_version INTEGER NOT NULL,"
      "account_key TEXT NOT NULL,owner_token TEXT NOT NULL,"
      "active INTEGER NOT NULL,heartbeat_utc INTEGER NOT NULL,"
      "heartbeat_mono_ms INTEGER NOT NULL)") &&
      DatabaseExecute(db,
      "CREATE TABLE stop_risk_samples (account_key TEXT NOT NULL,"
      "generation INTEGER PRIMARY KEY,observed_utc INTEGER NOT NULL,"
      "observed_mono_ms INTEGER NOT NULL,currency TEXT NOT NULL,"
      "balance REAL NOT NULL,margin_mode INTEGER NOT NULL,"
      "composition_digest TEXT NOT NULL,row_count INTEGER NOT NULL,"
      "publisher_token TEXT NOT NULL,checksum TEXT NOT NULL)") &&
      DatabaseExecute(db,
      "CREATE TABLE stop_risk_rows (generation INTEGER NOT NULL,"
      "kind INTEGER NOT NULL,ticket INTEGER NOT NULL,identifier INTEGER NOT NULL,"
      "opened_msc INTEGER NOT NULL,symbol TEXT NOT NULL,side INTEGER NOT NULL,"
      "order_type INTEGER NOT NULL,valid INTEGER NOT NULL,volume REAL NOT NULL,"
      "entry REAL NOT NULL,sl REAL NOT NULL,risk_money REAL NOT NULL,"
      "additional_money REAL NOT NULL,reason TEXT NOT NULL,"
      "additional_valid INTEGER NOT NULL,additional_reason TEXT NOT NULL,"
      "PRIMARY KEY (generation,kind,ticket))");
   if(ok)
     {
      const int q=DatabasePrepare(db,
         "INSERT INTO stop_risk_meta VALUES(?1,?2,'',0,0,0)");
      ok=q!=INVALID_HANDLE;
      if(ok)
        { ok=DatabaseBind(q,0,JPW_STOP_RISK_SCHEMA) &&
             DatabaseBind(q,1,account_key) &&
             JPWStopRiskExecutePrepared(q);
          DatabaseFinalize(q); }
     }
   if(ok && DatabaseTransactionCommit(db)) return(true);
   DatabaseTransactionRollback(db);
   return(false);
  }

bool JPWStopRiskReadMeta(const int db,const string account_key,
                         JPWStopRiskMeta &meta,string &reason)
  {
   reason="";
   if(db==INVALID_HANDLE ||
      !DatabaseTableExists(db,"stop_risk_meta") ||
      !DatabaseTableExists(db,"stop_risk_samples") ||
      !DatabaseTableExists(db,"stop_risk_rows"))
     { reason="Schema de stops ausente ou corrompido"; return(false); }
   const int q=DatabasePrepare(db,
      "SELECT schema_version,account_key,owner_token,active,"
      "heartbeat_utc,heartbeat_mono_ms FROM stop_risk_meta LIMIT 2");
   if(q==INVALID_HANDLE)
     { reason="Metadados de stops indisponiveis"; return(false); }
   ResetLastError();
   bool ok=DatabaseReadBind(q,meta);
   if(ok)
     { JPWStopRiskMeta duplicate; ResetLastError();
       ok=!DatabaseReadBind(q,duplicate) &&
          GetLastError()==ERR_DATABASE_NO_MORE_DATA; }
   DatabaseFinalize(q);
   if(!ok || meta.schema_version!=JPW_STOP_RISK_SCHEMA ||
      meta.account_key!=account_key ||
      (meta.active!=0 && meta.active!=1) ||
      (meta.active==1 &&
       (!JPWRaizNIsHash(meta.owner_token) ||
        meta.heartbeat_utc<=0 || meta.heartbeat_mono_ms<=0)))
     { reason="Versao ou identidade de stops incompativel"; return(false); }
   return(true);
  }

// A failed first CREATE can leave a valid but empty SQLite file. It is safe
// to retry initialization only when sqlite_master has no user objects at all.
// Any partial/unknown schema is preserved and refused, never deleted.
bool JPWStopRiskSchemaEmpty(const int db,bool &empty)
  {
   empty=false;
   if(db==INVALID_HANDLE) return(false);
   const int q=DatabasePrepare(db,
      "SELECT COUNT(*) FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'");
   if(q==INVALID_HANDLE) return(false);
   int count=-1;
   bool ok=DatabaseRead(q) && DatabaseColumnInteger(q,0,count);
   if(ok)
     { ResetLastError();
       ok=!DatabaseRead(q) && GetLastError()==ERR_DATABASE_NO_MORE_DATA; }
   DatabaseFinalize(q);
   if(!ok || count<0) return(false);
   empty=(count==0);
   return(true);
  }

bool JPWStopRiskOpen(const string account_key,const bool write,
                     int &db,string &reason)
  {
   db=INVALID_HANDLE; reason="";
   const string path=JPWStopRiskDatabasePath(account_key);
   if(path=="") { reason="Identidade de stops invalida"; return(false); }
   const bool exists=FileIsExist(path);
   if(!exists && !write)
     { reason="Ainda nao ha amostra local de stops"; return(false); }
   if(write && !FolderCreate("JPWealth\\Alavancagem"))
     { reason="Pasta local de stops indisponivel"; return(false); }
   db=DatabaseOpen(path,write ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE :
                              DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE)
     { reason="Banco local de stops indisponivel"; return(false); }
   bool empty_schema=false;
   const bool can_initialize=write &&
      JPWStopRiskSchemaEmpty(db,empty_schema) && empty_schema;
   if(can_initialize)
     {
      if(JPWStopRiskInitDatabase(db,account_key)) return(true);
      reason="Criacao do banco de stops nao confirmada; schema vazio preservado para retry";
     }
   else
     { JPWStopRiskMeta meta;
       if(JPWStopRiskReadMeta(db,account_key,meta,reason)) return(true); }
   DatabaseClose(db); db=INVALID_HANDLE;
   return(false);
  }

JPWStoreResult JPWStopRiskReadLatestInDbStatus(const int db,const string account_key,
                               JPWStopRiskSample &sample,
                               JPWStopRiskRow &rows[],string &reason)
  {
   JPWStopRiskClearSample(sample); ArrayResize(rows,0); reason="";
   const int q=DatabasePrepare(db,
      "SELECT account_key,generation,observed_utc,observed_mono_ms,"
      "currency,balance,margin_mode,composition_digest,row_count,"
      "publisher_token,checksum FROM stop_risk_samples "
      "ORDER BY generation DESC LIMIT 1");
   if(q==INVALID_HANDLE)
     { reason="Consulta da amostra de stops indisponivel"; return(JPW_STORE_IO_ERROR); }
   ResetLastError();
   const bool found=DatabaseReadBind(q,sample);
   const int read_error=GetLastError();
   DatabaseFinalize(q);
   if(!found)
     { reason=(read_error==ERR_DATABASE_NO_MORE_DATA ?
               "Ainda nao ha amostra local de stops" :
               "Leitura da amostra de stops falhou");
       return(read_error==ERR_DATABASE_NO_MORE_DATA ? JPW_STORE_ABSENT : JPW_STORE_IO_ERROR); }
   if(sample.account_key!=account_key || sample.row_count<0 ||
      sample.row_count>JPW_STOP_RISK_MAX_ROWS ||
      ArrayResize(rows,sample.row_count)!=sample.row_count)
     { reason="Amostra de stops invalida"; return(JPW_STORE_CORRUPT); }
   const int r=DatabasePrepare(db,
      "SELECT kind,ticket,identifier,opened_msc,symbol,side,order_type,"
      "valid,volume,entry,sl,risk_money,additional_money,reason,"
      "additional_valid,additional_reason FROM stop_risk_rows "
      "WHERE generation=?1 ORDER BY kind,ticket");
   if(r==INVALID_HANDLE)
     { reason="Linhas de stops indisponiveis"; return(JPW_STORE_IO_ERROR); }
   bool ok=DatabaseBind(r,0,sample.generation);
   for(int i=0;ok && i<sample.row_count;i++)
      ok=DatabaseReadBind(r,rows[i]);
   if(ok)
     { JPWStopRiskRow duplicate; ResetLastError();
       ok=!DatabaseReadBind(r,duplicate) &&
          GetLastError()==ERR_DATABASE_NO_MORE_DATA; }
   DatabaseFinalize(r);
   string checksum="";
   if(!ok || !JPWStopRiskChecksum(sample,rows,checksum) ||
      checksum!=sample.checksum)
     { JPWStopRiskClearSample(sample); ArrayResize(rows,0);
       reason="Amostra de stops incompleta ou checksum invalido";
       return(JPW_STORE_CORRUPT); }
   return(JPW_STORE_VALID);
  }

bool JPWStopRiskReadLatestInDb(const int db,const string account_key,
                               JPWStopRiskSample &sample,
                               JPWStopRiskRow &rows[],string &reason)
  {
   return(JPWStopRiskReadLatestInDbStatus(db,account_key,sample,rows,reason)==JPW_STORE_VALID);
  }

// Historical last sample remains consultable after the EA is detached. The
// caller must label it by observation time, never as the current account risk.
bool JPWStopRiskReadCurrent(const string account_key,
                            JPWStopRiskSample &sample,
                            JPWStopRiskRow &rows[],string &reason)
  {
   JPWStopRiskClearSample(sample); ArrayResize(rows,0);
   int db=INVALID_HANDLE;
   if(!JPWStopRiskOpen(account_key,false,db,reason)) return(false);
   const bool ok=JPWStopRiskReadLatestInDb(db,account_key,sample,rows,reason);
   DatabaseClose(db);
   return(ok);
  }

// Current demands a living EA publisher, same terminal monotonic epoch,
// connection and unchanged account/balance/positions/pending orders.
bool JPWStopRiskReadLiveCurrent(const string account_key,
                                JPWStopRiskSample &sample,
                                JPWStopRiskRow &rows[],string &reason)
  {
   JPWStopRiskClearSample(sample); ArrayResize(rows,0); reason="";
   if(TerminalInfoInteger(TERMINAL_CONNECTED)==0)
     { reason="Sem conexao do terminal"; return(false); }
   if(!JPWStopRiskReadCurrent(account_key,sample,rows,reason)) return(false);
   const ulong now=GetTickCount64();
   if(now<(ulong)sample.observed_mono_ms ||
      now-(ulong)sample.observed_mono_ms>JPW_STOP_RISK_MAX_AGE_MS)
     { reason="Amostra de stops vencida"; return(false); }
   if(!JPWStopRiskLeaseMatches(sample.publisher_token,
                                sample.observed_mono_ms))
     { reason="EA observador sem lease da sessao atual"; return(false); }
   int db=INVALID_HANDLE;
   if(!JPWStopRiskOpen(account_key,false,db,reason)) return(false);
   JPWStopRiskMeta meta;
   const bool meta_ok=JPWStopRiskReadMeta(db,account_key,meta,reason);
   DatabaseClose(db);
   if(!meta_ok) return(false);
   if(meta.active!=1 || meta.owner_token!=sample.publisher_token ||
      now<(ulong)meta.heartbeat_mono_ms ||
      now-(ulong)meta.heartbeat_mono_ms>JPW_STOP_RISK_MAX_AGE_MS)
     { reason="EA observador sem amostra ativa"; return(false); }
   string digest="";
   if(!JPWStopRiskLiveDigest(account_key,digest,reason) ||
      digest!=sample.composition_digest)
     { reason="Composicao da conta mudou desde a amostra"; return(false); }
   JPWStopRiskSample verify;
   JPWStopRiskRow verify_rows[];
   if(!JPWStopRiskReadCurrent(account_key,verify,verify_rows,reason) ||
      verify.generation!=sample.generation ||
      verify.checksum!=sample.checksum)
     { reason="Amostra alterou durante leitura"; return(false); }
   return(true);
  }

bool JPWStopRiskPublisherToken(const string account_key,
                               const long chart_id,string &token)
  {
   token="";
   if(!JPWRaizNIsHash(account_key) || chart_id<=0) return(false);
   return(JPWRaizNHash(JPWRaizNFrame(account_key)+
      JPWRaizNFrame(IntegerToString(chart_id))+
      JPWRaizNFrame(IntegerToString((long)GetTickCount64()))+
      JPWRaizNFrame(IntegerToString((long)TimeGMT()))+
      JPWRaizNFrame("stop_risk_writer_v1"),token));
  }

bool JPWStopRiskUpdateMeta(const int db,const string owner_token,
                           const int active,const long utc,const long mono)
  {
   const int q=DatabasePrepare(db,
      "UPDATE stop_risk_meta SET owner_token=?1,active=?2,"
      "heartbeat_utc=?3,heartbeat_mono_ms=?4");
   if(q==INVALID_HANDLE) return(false);
   const bool ok=DatabaseBind(q,0,owner_token) &&
      DatabaseBind(q,1,active) && DatabaseBind(q,2,utc) &&
      DatabaseBind(q,3,mono) && JPWStopRiskExecutePrepared(q);
   DatabaseFinalize(q);
   return(ok);
  }

bool JPWStopRiskInsertSample(const int db,JPWStopRiskSample &s)
  {
   const int q=DatabasePrepare(db,
      "INSERT INTO stop_risk_samples VALUES(?1,?2,?3,?4,?5,?6,?7,"
      "?8,?9,?10,?11)");
   if(q==INVALID_HANDLE) return(false);
   const bool ok=DatabaseBind(q,0,s.account_key) &&
      DatabaseBind(q,1,s.generation) &&
      DatabaseBind(q,2,s.observed_utc) &&
      DatabaseBind(q,3,s.observed_mono_ms) &&
      DatabaseBind(q,4,s.currency) &&
      DatabaseBind(q,5,s.balance) &&
      DatabaseBind(q,6,s.margin_mode) &&
      DatabaseBind(q,7,s.composition_digest) &&
      DatabaseBind(q,8,s.row_count) &&
      DatabaseBind(q,9,s.publisher_token) &&
      DatabaseBind(q,10,s.checksum) &&
      JPWStopRiskExecutePrepared(q);
   DatabaseFinalize(q);
   return(ok);
  }

bool JPWStopRiskInsertRow(const int db,const long generation,
                          JPWStopRiskRow &r)
  {
   const int q=DatabasePrepare(db,
      "INSERT INTO stop_risk_rows VALUES(?1,?2,?3,?4,?5,?6,?7,?8,"
      "?9,?10,?11,?12,?13,?14,?15,?16,?17)");
   if(q==INVALID_HANDLE) return(false);
   const bool ok=DatabaseBind(q,0,generation) &&
      DatabaseBind(q,1,r.kind) && DatabaseBind(q,2,r.ticket) &&
      DatabaseBind(q,3,r.identifier) &&
      DatabaseBind(q,4,r.opened_msc) &&
      DatabaseBind(q,5,r.symbol) && DatabaseBind(q,6,r.side) &&
      DatabaseBind(q,7,r.order_type) && DatabaseBind(q,8,r.valid) &&
      DatabaseBind(q,9,r.volume) && DatabaseBind(q,10,r.entry) &&
      DatabaseBind(q,11,r.sl) && DatabaseBind(q,12,r.risk_money) &&
      DatabaseBind(q,13,r.additional_money) &&
      DatabaseBind(q,14,r.reason) &&
      DatabaseBind(q,15,r.additional_valid) &&
      DatabaseBind(q,16,r.additional_reason) &&
      JPWStopRiskExecutePrepared(q);
   DatabaseFinalize(q);
   return(ok);
  }

bool JPWStopRiskDeleteOlder(const int db,const long oldest_kept)
  {
   const int rows=DatabasePrepare(db,
      "DELETE FROM stop_risk_rows WHERE generation<?1");
   if(rows==INVALID_HANDLE) return(false);
   bool ok=DatabaseBind(rows,0,oldest_kept) &&
           JPWStopRiskExecutePrepared(rows);
   DatabaseFinalize(rows);
   if(!ok) return(false);
   const int samples=DatabasePrepare(db,
      "DELETE FROM stop_risk_samples WHERE generation<?1");
   if(samples==INVALID_HANDLE) return(false);
   ok=DatabaseBind(samples,0,oldest_kept) &&
      JPWStopRiskExecutePrepared(samples);
   DatabaseFinalize(samples);
   return(ok);
  }

// A no-op UPDATE obtains SQLite's writer lock before checking the owner and
// max generation. Two EA instances cannot both publish the same generation.
// A clean OnDeinit deactivates immediately; a crashed owner expires after 30s.
bool JPWStopRiskPublish(JPWStopRiskSample &candidate,
                        JPWStopRiskRow &rows[],string &reason)
  {
   reason="";
   if(!JPWRaizNIsHash(candidate.account_key) ||
      !JPWRaizNIsHash(candidate.publisher_token) ||
      candidate.observed_utc<=0 || candidate.observed_mono_ms<=0 ||
      candidate.row_count!=ArraySize(rows))
     { reason="Amostra a publicar incompleta"; return(false); }
   int db=INVALID_HANDLE;
   if(!JPWStopRiskOpen(candidate.account_key,true,db,reason)) return(false);
   bool ok=DatabaseTransactionBegin(db);
   if(!ok) reason="Banco de stops ocupado";
   if(ok) ok=DatabaseExecute(db,
      "UPDATE stop_risk_meta SET active=active");
   if(!ok && reason=="") reason="Publicador de stops ocupado";
   JPWStopRiskMeta meta;
   if(ok) ok=JPWStopRiskReadMeta(db,candidate.account_key,meta,reason);
   if(ok && meta.active==1 &&
      meta.owner_token!=candidate.publisher_token)
     {
      const long elapsed=candidate.observed_mono_ms-
                         meta.heartbeat_mono_ms;
      const long wall_elapsed=candidate.observed_utc-meta.heartbeat_utc;
      // A terminal/OS restart can reset a monotonic epoch. Give the prior
      // owner its full lease by wall time; after that, a new EA can recover.
      if((elapsed>=0 && elapsed<=JPW_STOP_RISK_PUBLISHER_LEASE_MS) ||
         (elapsed<0 &&
          (wall_elapsed<0 || wall_elapsed<=30)))
        { ok=false; reason="Outra instancia do EA publica stops"; }
     }
   JPWStopRiskSample previous;
   JPWStopRiskRow previous_rows[];
   string read_reason="";
   JPWStoreResult previous_status=JPW_STORE_IO_ERROR;
   if(ok)
     {
      previous_status=JPWStopRiskReadLatestInDbStatus(db,candidate.account_key,
                                                     previous,previous_rows,read_reason);
      if(previous_status!=JPW_STORE_VALID && previous_status!=JPW_STORE_ABSENT)
        { ok=false; reason=read_reason; }
     }
   if(ok)
     {
      candidate.generation=(previous_status==JPW_STORE_ABSENT ? 1 : previous.generation+1);
      if(candidate.generation<=0 ||
         !JPWStopRiskChecksum(candidate,rows,candidate.checksum))
        { ok=false; reason="Amostra de stops estruturalmente invalida"; }
     }
   if(ok) ok=JPWStopRiskInsertSample(db,candidate);
   for(int i=0;ok && i<ArraySize(rows);i++)
      ok=JPWStopRiskInsertRow(db,candidate.generation,rows[i]);
   if(ok) ok=JPWStopRiskUpdateMeta(db,candidate.publisher_token,1,
                                    candidate.observed_utc,
                                    candidate.observed_mono_ms);
   if(ok && candidate.generation>2)
      ok=JPWStopRiskDeleteOlder(db,candidate.generation-1);
   JPWStopRiskSample verified;
   JPWStopRiskRow verified_rows[];
   string verify_reason="";
   if(ok) ok=JPWStopRiskReadLatestInDb(db,candidate.account_key,verified,
                                        verified_rows,verify_reason) &&
             verified.generation==candidate.generation &&
             verified.checksum==candidate.checksum;
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok)
     { DatabaseTransactionRollback(db);
       if(reason=="") reason="Publicacao de stops nao confirmada"; }
   DatabaseClose(db);
   return(ok);
  }

bool JPWStopRiskDeactivate(const string account_key,
                           const string publisher_token,string &reason)
  {
   reason="";
   if(!JPWRaizNIsHash(account_key) ||
      !JPWRaizNIsHash(publisher_token))
     { reason="Identidade do publicador indisponivel"; return(false); }
   int db=INVALID_HANDLE;
   if(!JPWStopRiskOpen(account_key,true,db,reason)) return(false);
   bool ok=DatabaseTransactionBegin(db);
   if(ok) ok=DatabaseExecute(db,
      "UPDATE stop_risk_meta SET active=active");
   JPWStopRiskMeta meta;
   if(ok) ok=JPWStopRiskReadMeta(db,account_key,meta,reason);
   if(ok && meta.owner_token==publisher_token && meta.active==1)
      ok=JPWStopRiskUpdateMeta(db,publisher_token,0,
                                meta.heartbeat_utc,
                                meta.heartbeat_mono_ms);
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok)
     { DatabaseTransactionRollback(db);
       if(reason=="") reason="Desativacao do publicador nao confirmada"; }
   DatabaseClose(db);
   return(ok);
  }

#endif

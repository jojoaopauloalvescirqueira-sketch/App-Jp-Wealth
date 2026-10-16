#ifndef JPW_PERSONAL_HISTORY_STORE_MQH
#define JPW_PERSONAL_HISTORY_STORE_MQH
#include <JPWealth/JPW_PersonalHistory_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Store_Result.mqh>
#define JPW_PERSONAL_SCHEMA 1
#define JPW_PERSONAL_FOLDER "JPWealth\\Genetrix\\PersonalHistory\\"
#define JPW_PERSONAL_LEASE_MS 15000
#define JPW_PERSONAL_SLICE_ROWS 1024
#define JPW_PERSONAL_SLICE_MS 25
enum JPWPersonalPhase
  { JPW_PH_IDLE=0,JPW_PH_WAIT_OWNER,JPW_PH_TRANSACTION,JPW_PH_META,JPW_PH_SQLITE,
    JPW_PH_EPISODES,JPW_PH_PEAKS,JPW_PH_ROWS,JPW_PH_OWNER,JPW_PH_OWNER_COMMIT,JPW_PH_READY,JPW_PH_FAILED };
struct JPWPersonalStoreContext
  {
   int db,query; string account_key,owner_token; bool writer,read_snapshot,requested_writer,transaction_active,audit_complete;
   bool generation_changed,owner_lost; JPWPersonalPhase phase; JPWStoreResult result; string reason;
   long expected_sequence,snapshot_sequence,started_wall,last_wall,data_version,active_episodes,total_episodes,gaps;
   JPWPersonalEpisode recovered[]; JPWPersonalPeak current,estimated;
   JPWPersonalStoreContext() { db=INVALID_HANDLE; query=INVALID_HANDLE; writer=false; read_snapshot=false; requested_writer=false;
      transaction_active=false; audit_complete=false; generation_changed=false; owner_lost=false; phase=JPW_PH_IDLE; result=JPW_STORE_ABSENT;
      expected_sequence=0; snapshot_sequence=0; started_wall=0; last_wall=0; data_version=0; active_episodes=0; total_episodes=0; gaps=0;
      current.valid=false; estimated.valid=false; }
  };
struct JPWPersonalRow
  { long sequence; string category; string item_id; long wall; string payload; string digest; };
bool JPWPersonalReadRow(const int query,JPWPersonalRow &row,const string key);
struct JPWPersonalSummary
  {
   JPWStoreResult result; string reason; string account_key; long sequence;
   long started_wall; long last_wall; long active_episodes; long total_episodes; long gaps;
   JPWPersonalPeak current; JPWPersonalPeak estimated;
  };
bool JPWPersonalHash(const string value,string &hex)
  {
   hex=""; uchar source[],key[],digest[];
   int count=StringToCharArray(value,source,0,WHOLE_ARRAY,CP_UTF8);
   if(count<=0 || ArrayResize(source,count-1)!=count-1 || CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) hex+=StringFormat("%02x",(int)digest[i]); return(StringLen(hex)==64);
  }
bool JPWPersonalHashValid(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++) if(JPWPersonalHexDigit(StringGetCharacter(value,i))<0) return(false);
   return(true);
  }
// Schema 1 digests seal payloads only. Validate the typed envelope separately;
// never rewrite a legacy digest or claim that it seals every scalar field.
bool JPWPersonalCategoryValid(const string category)
  { return(category=="EPISODE" || category=="PEAK" || category=="EVENT" || category=="ALERT" ||
      category=="SESSION" || category=="COVERAGE"); }
bool JPWPersonalEnvelopeValid(const string category,const string item,const long wall,const string raw,const string key="")
  {
   if(!JPWPersonalCategoryValid(category) || item=="" || wall<=0) return(false);
   if(category=="EPISODE")
     {
      JPWPersonalEpisode episode;
      return(JPWPersonalDecodeEpisode(raw,episode) && episode.episode_id==item &&
         (key=="" || episode.account_key==key));
     }
   if(category=="PEAK")
     {
      JPWPersonalPeak peak;
      return(JPWPersonalDecodePeak(raw,peak) && JPWPersonalInt(peak.quality)==item && peak.wall==wall &&
         (key=="" || peak.account_key==key));
     }
   string parts[],detail="";
   if(StringSplit(raw,'|',parts)!=2 || !JPWPersonalUnhex(parts[1],detail) ||
      parts[0]+"|"+JPWPersonalHex(detail)!=raw) return(false);
   if(category=="EVENT")
     {
      // Include every event emitted by Core and Controller. A consumer-only
      // whitelist must not reject the producer's ordinary first observation.
      if(parts[0]=="INVENTORY_CONTEXT")
        { string observation=""; return(JPWPersonalHash(detail,observation) && observation==item); }
      return(parts[0]=="NO_SL_DETECTED" || parts[0]=="NO_LONGER_PRESENT" ||
         parts[0]=="RESOLVED_SL_PRESENT" || parts[0]=="CLOCK_INCONSISTENT" ||
         parts[0]=="RECOVERY_EPISODE_LINK" || parts[0]=="NOTIFICATION_CHANNEL_ERROR");
     }
   if(category=="ALERT") return(parts[0]=="INTENT" || parts[0]=="CALLED" || parts[0]=="RESULT");
   if(!JPWPersonalHashValid(item)) return(false);
   if(category=="SESSION") return(parts[0]=="SESSION_START" || parts[0]=="SESSION_END");
   return(parts[0]=="GAP" || parts[0]=="RESUMED" || parts[0]=="CLOCK_INCONSISTENT");
  }
string JPWPersonalPath(const string key)
  { return(JPWPersonalHashValid(key) ? JPW_PERSONAL_FOLDER+"history_"+key+".sqlite" : ""); }
bool JPWPersonalDone(const int query)
  { ResetLastError(); bool row=DatabaseRead(query); return(!row && GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
bool JPWPersonalFail(JPWPersonalStoreContext &ctx,const JPWStoreResult result,const string reason)
  { ctx.result=result; ctx.reason=reason; return(false); }
bool JPWPersonalSchemaCreate(const int db,const string key,const long wall)
  {
   if(!DatabaseTransactionBegin(db)) return(false);
   bool ok=DatabaseExecute(db,"CREATE TABLE ph_meta(id INTEGER PRIMARY KEY CHECK(id=1),schema_version INTEGER NOT NULL,account_key TEXT NOT NULL,sequence INTEGER NOT NULL,started_wall INTEGER NOT NULL,last_wall INTEGER NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE ph_owner(id INTEGER PRIMARY KEY CHECK(id=1),token TEXT NOT NULL,mono INTEGER NOT NULL,wall INTEGER NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE ph_rows(sequence INTEGER PRIMARY KEY,category TEXT NOT NULL,item_id TEXT NOT NULL,wall INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE ph_episodes(episode_id TEXT PRIMARY KEY,state INTEGER NOT NULL,sequence INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE ph_peaks(quality INTEGER PRIMARY KEY,sequence INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL)") &&
      DatabaseExecute(db,"CREATE INDEX ph_rows_category ON ph_rows(category,sequence)") &&
      DatabaseExecute(db,"INSERT INTO ph_owner VALUES(1,'',0,0)");
   int q=DatabasePrepare(db,"INSERT INTO ph_meta VALUES(1,?1,?2,0,?3,?3)");
   ok=ok && q!=INVALID_HANDLE && DatabaseBind(q,0,JPW_PERSONAL_SCHEMA) && DatabaseBind(q,1,key) && DatabaseBind(q,2,wall) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(ok) ok=DatabaseTransactionCommit(db); if(!ok) DatabaseTransactionRollback(db); return(ok);
  }
bool JPWPersonalPreparing(JPWPersonalStoreContext &ctx)
  { return(ctx.db!=INVALID_HANDLE && ctx.phase!=JPW_PH_IDLE && ctx.phase!=JPW_PH_READY && ctx.phase!=JPW_PH_FAILED && !ctx.owner_lost); }
bool JPWPersonalReady(JPWPersonalStoreContext &ctx)
  { return(ctx.db!=INVALID_HANDLE && ctx.phase==JPW_PH_READY && ctx.audit_complete && !ctx.generation_changed && !ctx.owner_lost); }
bool JPWPersonalNeedsReaudit(JPWPersonalStoreContext &ctx) { return(ctx.generation_changed); }
bool JPWPersonalOwnerLost(JPWPersonalStoreContext &ctx) { return(ctx.owner_lost); }
JPWStoreResult JPWPersonalErrorResult(const int error)
  {
   if(error==ERR_DATABASE_BUSY || error==ERR_DATABASE_LOCKED) return(JPW_STORE_BUSY);
   if(error==ERR_DATABASE_CORRUPT || error==ERR_DATABASE_NOTADB) return(JPW_STORE_CORRUPT);
   return(JPW_STORE_IO_ERROR);
  }
void JPWPersonalOpenCancel(JPWPersonalStoreContext &ctx)
  {
   if(ctx.query!=INVALID_HANDLE) DatabaseFinalize(ctx.query); ctx.query=INVALID_HANDLE;
   if(ctx.db!=INVALID_HANDLE && ctx.transaction_active) DatabaseTransactionRollback(ctx.db);
   if(ctx.db!=INVALID_HANDLE) DatabaseClose(ctx.db);
   ctx.db=INVALID_HANDLE; ctx.writer=false; ctx.read_snapshot=false; ctx.transaction_active=false; ctx.audit_complete=false;
   ctx.data_version=0; ctx.phase=JPW_PH_IDLE; ArrayResize(ctx.recovered,0); ctx.current.valid=false; ctx.estimated.valid=false;
  }
void JPWPersonalContextReset(JPWPersonalStoreContext &ctx)
  {
   // Callers cancel owned handles before resetting a reusable context.
   ctx.db=INVALID_HANDLE; ctx.query=INVALID_HANDLE; ctx.account_key=""; ctx.owner_token=""; ctx.writer=false;
   ctx.read_snapshot=false; ctx.requested_writer=false; ctx.transaction_active=false; ctx.audit_complete=false;
   ctx.generation_changed=false; ctx.owner_lost=false; ctx.phase=JPW_PH_IDLE; ctx.result=JPW_STORE_ABSENT; ctx.reason="";
   ctx.expected_sequence=0; ctx.snapshot_sequence=0; ctx.started_wall=0; ctx.last_wall=0; ctx.data_version=0;
   ctx.active_episodes=0; ctx.total_episodes=0; ctx.gaps=0; ArrayResize(ctx.recovered,0); ctx.current.valid=false; ctx.estimated.valid=false;
  }
JPWStoreResult JPWPersonalAuditFail(JPWPersonalStoreContext &ctx,const JPWStoreResult result,const string reason)
  { JPWPersonalOpenCancel(ctx); ctx.phase=JPW_PH_FAILED; ctx.result=result; ctx.reason=reason; return(result); }
bool JPWPersonalDataVersion(const int db,long &version)
  {
   int q=DatabasePrepare(db,"PRAGMA data_version");
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnType(q,0)==DATABASE_FIELD_TYPE_INTEGER && DatabaseColumnLong(q,0,version) && version>0 && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalOwnerRead(const int db,string &token,long &mono,long &wall)
  {
   int q=DatabasePrepare(db,"SELECT token,mono,wall,(typeof(id)='integer' AND typeof(token)='text' AND typeof(mono)='integer' AND typeof(wall)='integer') FROM ph_owner WHERE id=1"); int typed=0;
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnText(q,0,token) && DatabaseColumnLong(q,1,mono) &&
      DatabaseColumnLong(q,2,wall) && DatabaseColumnInteger(q,3,typed) && typed==1 && mono>=0 && wall>=0 &&
      (token=="" || JPWPersonalHashValid(token)) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalLeaseAvailable(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   string token=""; long previous=0,previous_wall=0;
   if(!JPWPersonalOwnerRead(ctx.db,token,previous,previous_wall)) return(JPWPersonalFail(ctx,JPW_STORE_CORRUPT,"Titular/relógio histórico corrompido; nenhum reset"));
   bool expired=(mono>=(ulong)previous && mono-(ulong)previous>JPW_PERSONAL_LEASE_MS) ||
      (mono<(ulong)previous && wall>previous_wall+15);
   if(token!="" && token!=ctx.owner_token && !expired) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Outro escritor ativo; aguardando titularidade"));
   return(true);
  }
bool JPWPersonalAuditBegin(JPWPersonalStoreContext &ctx)
  {
   if(ctx.db==INVALID_HANDLE || !ctx.transaction_active || ctx.query!=INVALID_HANDLE) return(false);
   ctx.writer=false; ctx.audit_complete=false; ctx.read_snapshot=false; ctx.phase=JPW_PH_META; ctx.result=JPW_STORE_BUSY;
   ctx.reason="Auditoria integral em preparação"; ctx.expected_sequence=0; ctx.snapshot_sequence=0; ctx.active_episodes=0;
   ctx.total_episodes=0; ctx.gaps=0; ctx.current.valid=false; ctx.estimated.valid=false; ArrayResize(ctx.recovered,0); return(true);
  }
JPWStoreResult JPWPersonalOpenBegin(const string key,const bool writer,const string token,const long wall,const ulong mono,JPWPersonalStoreContext &ctx)
  {
   if(ctx.db!=INVALID_HANDLE || ctx.query!=INVALID_HANDLE) { JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Contexto já possui trabalho; cancele antes de abrir"); return(ctx.result); }
   JPWPersonalContextReset(ctx); ctx.account_key=key; ctx.owner_token=token; ctx.requested_writer=writer;
   string path=JPWPersonalPath(key); if(path=="" || (writer && (!JPWPersonalHashValid(token) || wall<=0 || mono==0)))
      { JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Identidade/titular/relógio inválido"); return(ctx.result); }
   bool exists=FileIsExist(path); if(!exists && !writer) { JPWPersonalFail(ctx,JPW_STORE_ABSENT,"Histórico ainda não iniciado nesta instalação"); return(ctx.result); }
   if(writer) { FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\PersonalHistory"); }
   ResetLastError(); ctx.db=DatabaseOpen(path,writer ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE : DATABASE_OPEN_READONLY);
   if(ctx.db==INVALID_HANDLE) { JPWPersonalFail(ctx,JPWPersonalErrorResult(GetLastError()),"Banco indisponível; nenhum reset"); return(ctx.result); }
   if(!exists && !JPWPersonalSchemaCreate(ctx.db,key,wall)) return(JPWPersonalAuditFail(ctx,JPWPersonalErrorResult(GetLastError()),"Inicialização não confirmada; preservar arquivo"));
   if(!DatabaseExecute(ctx.db,"PRAGMA busy_timeout=0")) return(JPWPersonalAuditFail(ctx,JPWPersonalErrorResult(GetLastError()),"Política de espera indisponível"));
   ctx.phase=(writer ? JPW_PH_WAIT_OWNER : JPW_PH_TRANSACTION); ctx.result=JPW_STORE_BUSY; ctx.reason="Auditoria integral em preparação"; return(ctx.result);
  }
// All phase cursors retain the same transaction. No filter authorizes unseen rows.
JPWStoreResult JPWPersonalAuditStep(JPWPersonalStoreContext &ctx,const ulong started,const int budget_ms,const int max_rows)
  {
   if(ctx.db==INVALID_HANDLE || !ctx.transaction_active || max_rows<1 || budget_ms<1) return(ctx.result);
   int units=0;
   while(units<max_rows)
     {
      ulong now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
      if(ctx.phase==JPW_PH_META)
        {
         int q=DatabasePrepare(ctx.db,"SELECT schema_version,account_key,sequence,started_wall,last_wall,(typeof(id)='integer' AND typeof(schema_version)='integer' AND typeof(account_key)='text' AND typeof(sequence)='integer' AND typeof(started_wall)='integer' AND typeof(last_wall)='integer') FROM ph_meta WHERE id=1");
         long version=0; int typed=0; string key="";
         bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,version) && DatabaseColumnText(q,1,key) &&
            DatabaseColumnLong(q,2,ctx.snapshot_sequence) && DatabaseColumnLong(q,3,ctx.started_wall) && DatabaseColumnLong(q,4,ctx.last_wall) &&
            DatabaseColumnInteger(q,5,typed) && typed==1 && ctx.snapshot_sequence>=0 && ctx.started_wall>0 && ctx.last_wall>=ctx.started_wall && JPWPersonalDone(q);
         if(q!=INVALID_HANDLE) DatabaseFinalize(q);
         if(!ok) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Metadados/tipos históricos corrompidos; nenhum reset"));
         if(version!=JPW_PERSONAL_SCHEMA || key!=ctx.account_key) return(JPWPersonalAuditFail(ctx,JPW_STORE_INCOMPATIBLE,"Schema/conta incompatível; nenhum reset"));
         string owner=""; long owner_mono=0,owner_wall=0;
         if(!JPWPersonalOwnerRead(ctx.db,owner,owner_mono,owner_wall)) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Tipos/identidade do titular corrompidos; nenhum reset"));
         if(ctx.requested_writer && !JPWPersonalDataVersion(ctx.db,ctx.data_version)) return(JPWPersonalAuditFail(ctx,JPW_STORE_IO_ERROR,"Geração da conexão não verificável"));
         ctx.phase=JPW_PH_SQLITE; units++; continue;
        }
      if(ctx.phase<JPW_PH_SQLITE || ctx.phase>JPW_PH_ROWS) return(ctx.audit_complete ? JPW_STORE_VALID : ctx.result);
      if(ctx.query==INVALID_HANDLE)
        {
         string sql="";
         if(ctx.phase==JPW_PH_SQLITE) sql="PRAGMA quick_check";
         if(ctx.phase==JPW_PH_EPISODES) sql="SELECT r.sequence,r.category,r.item_id,r.wall,r.payload,r.digest,p.episode_id,p.state,p.sequence,p.payload,p.digest,(typeof(p.episode_id)='text' AND typeof(p.state)='integer' AND p.state IN(1,2,3) AND typeof(p.sequence)='integer' AND typeof(p.payload)='text' AND typeof(p.digest)='text' AND typeof(r.sequence)='integer' AND typeof(r.category)='text' AND typeof(r.item_id)='text' AND typeof(r.wall)='integer' AND typeof(r.payload)='text' AND typeof(r.digest)='text') FROM ph_episodes p LEFT JOIN ph_rows r ON r.sequence=p.sequence ORDER BY p.episode_id";
         if(ctx.phase==JPW_PH_PEAKS) sql="SELECT r.sequence,r.category,r.item_id,r.wall,r.payload,r.digest,p.quality,p.sequence,p.payload,p.digest,(typeof(p.quality)='integer' AND p.quality IN(1,2) AND typeof(p.sequence)='integer' AND typeof(p.payload)='text' AND typeof(p.digest)='text' AND typeof(r.sequence)='integer' AND typeof(r.category)='text' AND typeof(r.item_id)='text' AND typeof(r.wall)='integer' AND typeof(r.payload)='text' AND typeof(r.digest)='text') FROM ph_peaks p LEFT JOIN ph_rows r ON r.sequence=p.sequence ORDER BY p.quality";
         if(ctx.phase==JPW_PH_ROWS) sql="SELECT r.sequence,r.category,r.item_id,r.wall,r.payload,r.digest,(typeof(r.sequence)='integer' AND typeof(r.category)='text' AND typeof(r.item_id)='text' AND typeof(r.wall)='integer' AND typeof(r.payload)='text' AND typeof(r.digest)='text'),e.sequence,p.sequence,(typeof(e.sequence)='integer'),(typeof(p.sequence)='integer') FROM ph_rows r LEFT JOIN ph_episodes e ON r.category='EPISODE' AND e.episode_id=r.item_id LEFT JOIN ph_peaks p ON r.category='PEAK' AND CAST(p.quality AS TEXT)=r.item_id ORDER BY r.sequence";
         ctx.query=DatabasePrepare(ctx.db,sql);
         if(ctx.query==INVALID_HANDLE) return(JPWPersonalAuditFail(ctx,JPWPersonalErrorResult(GetLastError()),"Cursor de auditoria indisponível; nenhum dado parcial"));
        }
      ResetLastError(); bool present=DatabaseRead(ctx.query); int error=GetLastError(); units++;
      if(!present)
        {
         if(error!=ERR_DATABASE_NO_MORE_DATA) return(JPWPersonalAuditFail(ctx,JPWPersonalErrorResult(error),"Leitura interrompida; não é EOF histórico"));
         DatabaseFinalize(ctx.query); ctx.query=INVALID_HANDLE;
         if(ctx.phase==JPW_PH_ROWS)
           {
            if(ctx.expected_sequence!=ctx.snapshot_sequence) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Sequência/contagem histórica divergente"));
            ctx.audit_complete=true; return(JPW_STORE_VALID);
           }
         ctx.phase=(JPWPersonalPhase)((int)ctx.phase+1); continue;
        }
      if(ctx.phase==JPW_PH_SQLITE)
        { string value=""; if(!DatabaseColumnText(ctx.query,0,value) || value!="ok") return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Integridade SQLite recusada; nenhum reset")); continue; }
      JPWPersonalRow row; int typed=0;
      if(!JPWPersonalReadRow(ctx.query,row,ctx.account_key)) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Envelope/payload histórico corrompido; nenhum reset"));
      if(ctx.phase==JPW_PH_EPISODES)
        {
         string id="",raw="",digest=""; int state=0; long seq=0; JPWPersonalEpisode episode;
         bool ok=DatabaseColumnText(ctx.query,6,id) && DatabaseColumnInteger(ctx.query,7,state) && DatabaseColumnLong(ctx.query,8,seq) &&
            DatabaseColumnText(ctx.query,9,raw) && DatabaseColumnText(ctx.query,10,digest) && DatabaseColumnInteger(ctx.query,11,typed) && typed==1 &&
            state>=1 && state<=3 && seq>0 && seq<=ctx.snapshot_sequence && row.category=="EPISODE" && row.sequence==seq && row.item_id==id && row.payload==raw && row.digest==digest &&
            JPWPersonalDecodeEpisode(raw,episode) && episode.state==state;
         if(!ok) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Projeção/testemunha de episódio divergente"));
         ctx.total_episodes++;
         if(state==JPW_PERSONAL_ACTIVE)
           { int n=ArraySize(ctx.recovered); if(n>=JPW_PERSONAL_MAX_SUBJECTS || ArrayResize(ctx.recovered,n+1)!=n+1) return(JPWPersonalAuditFail(ctx,JPW_STORE_IO_ERROR,"Recuperação ativa sem capacidade; histórico preservado"));
             ctx.recovered[n]=episode; ctx.active_episodes++; }
        }
      else if(ctx.phase==JPW_PH_PEAKS)
        {
         int quality=0; long seq=0; string raw="",digest=""; JPWPersonalPeak peak;
         bool ok=DatabaseColumnInteger(ctx.query,6,quality) && DatabaseColumnLong(ctx.query,7,seq) && DatabaseColumnText(ctx.query,8,raw) &&
            DatabaseColumnText(ctx.query,9,digest) && DatabaseColumnInteger(ctx.query,10,typed) && typed==1 && (quality==1 || quality==2) &&
            seq>0 && seq<=ctx.snapshot_sequence && row.category=="PEAK" && row.sequence==seq && row.item_id==JPWPersonalInt(quality) && row.payload==raw && row.digest==digest &&
            JPWPersonalDecodePeak(raw,peak) && peak.quality==quality;
         if(!ok) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Projeção/testemunha de máximo divergente"));
         if(quality==1) ctx.current=peak; else ctx.estimated=peak;
        }
      else
        {
         bool ok=DatabaseColumnInteger(ctx.query,6,typed) && typed==1 && row.sequence==ctx.expected_sequence+1;
         if(row.category=="EPISODE" || row.category=="PEAK")
           { long projection=0; int projection_typed=0; int column=(row.category=="EPISODE" ? 7 : 8);
             ok=ok && DatabaseColumnLong(ctx.query,column,projection) && DatabaseColumnInteger(ctx.query,column+2,projection_typed) && projection_typed==1 && projection>=row.sequence && projection<=ctx.snapshot_sequence; }
         if(!ok) return(JPWPersonalAuditFail(ctx,JPW_STORE_CORRUPT,"Tipo/sequência/latest histórico divergente"));
         if(row.category=="COVERAGE" && StringFind(row.payload,"GAP|")==0) ctx.gaps++;
         ctx.expected_sequence++;
        }
     }
   return(JPW_STORE_BUSY);
  }
JPWStoreResult JPWPersonalOpenStep(JPWPersonalStoreContext &ctx,const ulong started,const int budget_ms,const int max_rows,const long wall,const ulong mono)
  {
   if(JPWPersonalReady(ctx)) return(JPW_STORE_VALID);
   if(!JPWPersonalPreparing(ctx) || ctx.generation_changed || budget_ms<1 || max_rows<1) return(ctx.result);
   ulong now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
   if(ctx.phase==JPW_PH_WAIT_OWNER)
     {
      if(!JPWPersonalLeaseAvailable(ctx,wall,mono))
        { if(ctx.result!=JPW_STORE_BUSY) return(JPWPersonalAuditFail(ctx,ctx.result,ctx.reason)); return(ctx.result); }
      ctx.phase=JPW_PH_TRANSACTION;
     }
   if(ctx.phase==JPW_PH_TRANSACTION)
     {
      if(!DatabaseExecute(ctx.db,ctx.requested_writer ? "BEGIN IMMEDIATE" : "BEGIN"))
        { ctx.result=JPWPersonalErrorResult(GetLastError()); ctx.reason="Reserva histórica ocupada/indisponível";
          if(ctx.result!=JPW_STORE_BUSY) return(JPWPersonalAuditFail(ctx,ctx.result,ctx.reason)); return(ctx.result); }
      ctx.transaction_active=true;
      if(ctx.requested_writer && !JPWPersonalLeaseAvailable(ctx,wall,mono))
        { DatabaseTransactionRollback(ctx.db); ctx.transaction_active=false; ctx.phase=JPW_PH_WAIT_OWNER;
          if(ctx.result!=JPW_STORE_BUSY) return(JPWPersonalAuditFail(ctx,ctx.result,ctx.reason)); return(ctx.result); }
      JPWPersonalAuditBegin(ctx);
     }
   if(ctx.phase>=JPW_PH_META && ctx.phase<=JPW_PH_ROWS)
     {
      JPWStoreResult audit=JPWPersonalAuditStep(ctx,started,budget_ms,max_rows); if(audit!=JPW_STORE_VALID) return(audit);
      if(!ctx.requested_writer) { ctx.read_snapshot=true; ctx.phase=JPW_PH_READY; ctx.result=JPW_STORE_VALID; ctx.reason=""; return(ctx.result); }
      ctx.phase=JPW_PH_OWNER;
     }
   now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
   if(ctx.phase==JPW_PH_OWNER)
     {
      if(!JPWPersonalLeaseAvailable(ctx,wall,mono)) return(JPWPersonalAuditFail(ctx,ctx.result,ctx.reason));
      int q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET token=?1,mono=?2,wall=?3 WHERE id=1");
      bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,ctx.owner_token) && DatabaseBind(q,1,(long)mono) && DatabaseBind(q,2,wall) && JPWPersonalDone(q);
      int error=GetLastError(); if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(!ok) return(JPWPersonalAuditFail(ctx,JPWPersonalErrorResult(error),"Aquisição de titularidade não confirmada")); ctx.phase=JPW_PH_OWNER_COMMIT;
     }
   if(ctx.phase==JPW_PH_OWNER_COMMIT)
     {
      if(!DatabaseTransactionCommit(ctx.db))
        { JPWStoreResult error=JPWPersonalErrorResult(GetLastError()); if(error==JPW_STORE_BUSY) { ctx.result=error; ctx.reason="Titularidade aguardando COMMIT; nenhum canal autorizado"; return(error); }
          return(JPWPersonalAuditFail(ctx,error,"COMMIT de titularidade não confirmado")); }
      ctx.transaction_active=false; ctx.writer=true; ctx.phase=JPW_PH_READY; ctx.result=JPW_STORE_VALID; ctx.reason="";
     }
   return(ctx.result);
  }
bool JPWPersonalLoadAuditedFrom(JPWPersonalStoreContext &ctx,JPWPersonalEpisode &episodes[],JPWPersonalPeak &current,JPWPersonalPeak &estimated)
  {
   ArrayResize(episodes,0); current.valid=false; estimated.valid=false; if(!JPWPersonalReady(ctx)) return(false);
   int n=ArraySize(ctx.recovered); if(ArrayResize(episodes,n)!=n) return(false);
   for(int i=0;i<n;i++) episodes[i]=ctx.recovered[i]; current=ctx.current; estimated=ctx.estimated; return(true);
  }
// Every mutation checks token and same-connection generation under its reserve.
bool JPWPersonalWriteBegin(JPWPersonalStoreContext &ctx)
  {
   if(!JPWPersonalReady(ctx) || !ctx.writer) return(false);
   if(!DatabaseExecute(ctx.db,"BEGIN IMMEDIATE")) return(JPWPersonalFail(ctx,JPWPersonalErrorResult(GetLastError()),"Histórico ocupado/indisponível"));
   ctx.transaction_active=true; string token=""; long previous=0,wall=0,version=0;
   bool owner=JPWPersonalOwnerRead(ctx.db,token,previous,wall);
   if(owner && token!=ctx.owner_token)
     { ctx.owner_lost=true; ctx.writer=false; ctx.audit_complete=false; ctx.phase=JPW_PH_FAILED;
       DatabaseTransactionRollback(ctx.db); ctx.transaction_active=false; return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Titularidade perdida; avisos/gravações suspensos")); }
   bool version_ok=owner && JPWPersonalDataVersion(ctx.db,version);
   if(!version_ok || version!=ctx.data_version)
     { DatabaseTransactionRollback(ctx.db); ctx.transaction_active=false; ctx.writer=false; ctx.audit_complete=false;
       ctx.generation_changed=true; ctx.phase=JPW_PH_TRANSACTION; ctx.data_version=0; ArrayResize(ctx.recovered,0);
       ctx.current.valid=false; ctx.estimated.valid=false;
       return(JPWPersonalFail(ctx,version_ok ? JPW_STORE_BUSY : JPW_STORE_IO_ERROR,"Geração histórica mudou/não verificável; reauditoria integral necessária")); }
   return(true);
  }
bool JPWPersonalOwner(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   if(!ctx.writer || !ctx.transaction_active || !ctx.audit_complete) return(false);
   string token=""; long previous=0,old_wall=0;
   if(!JPWPersonalOwnerRead(ctx.db,token,previous,old_wall) || token!=ctx.owner_token || mono<(ulong)previous)
     { ctx.owner_lost=true; ctx.writer=false; ctx.audit_complete=false; return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Titularidade perdida; avisos/gravações suspensos")); }
   int q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET mono=?1,wall=?2 WHERE id=1 AND token=?3");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,(long)mono) && DatabaseBind(q,1,wall) && DatabaseBind(q,2,ctx.owner_token) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalWriteFinish(JPWPersonalStoreContext &ctx,const bool complete,const string reason)
  {
   bool ok=complete && DatabaseTransactionCommit(ctx.db); int error=GetLastError();
   if(!ok) DatabaseTransactionRollback(ctx.db); ctx.transaction_active=false;
   if(ok) { ctx.result=JPW_STORE_VALID; ctx.reason=""; return(true); }
   if(ctx.owner_lost) return(false);
   ctx.writer=false; ctx.audit_complete=false; ctx.generation_changed=false; ctx.phase=JPW_PH_FAILED; ctx.data_version=0;
   return(JPWPersonalFail(ctx,JPWPersonalErrorResult(error),reason));
  }
bool JPWPersonalKeepAlive(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  { if(!JPWPersonalWriteBegin(ctx)) return(false); return(JPWPersonalWriteFinish(ctx,JPWPersonalOwner(ctx,wall,mono),"Heartbeat não confirmado")); }
bool JPWPersonalReadFinish(JPWPersonalStoreContext &ctx,const bool complete)
  {
   if(!JPWPersonalReady(ctx) || ctx.writer || !ctx.read_snapshot || !ctx.transaction_active || ctx.query!=INVALID_HANDLE)
      return(JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Snapshot de consulta não confirmado"));
   bool ok=complete && DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
   ctx.read_snapshot=false; ctx.transaction_active=false;
   if(!ok) { ctx.audit_complete=false; return(JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Conclusão do snapshot não confirmada")); }
   return(true);
  }
void JPWPersonalClose(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   if(ctx.db!=INVALID_HANDLE && ctx.writer && JPWPersonalWriteBegin(ctx))
     {
      int q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET token='',mono=0,wall=?1 WHERE id=1 AND token=?2");
      bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,wall) && DatabaseBind(q,1,ctx.owner_token) && JPWPersonalDone(q);
      if(q!=INVALID_HANDLE) DatabaseFinalize(q); JPWPersonalWriteFinish(ctx,ok,"Liberação de titularidade não confirmada");
     }
   JPWPersonalOpenCancel(ctx);
  }
bool JPWPersonalAppend(const int db,const string category,const string item,const long wall,const string payload,long &sequence)
  {
   sequence=0; string digest=""; if(!JPWPersonalHash(payload,digest)) return(false);
   int q=DatabasePrepare(db,"SELECT sequence,account_key FROM ph_meta WHERE id=1"); long old=0; string key="";
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,old) && DatabaseColumnText(q,1,key) &&
      old>=0 && old<LONG_MAX-1 && JPWPersonalEnvelopeValid(category,item,wall,payload,key);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); if(!ok) return(false); sequence=old+1;
   q=DatabasePrepare(db,"INSERT INTO ph_rows VALUES(?1,?2,?3,?4,?5,?6)");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,sequence) && DatabaseBind(q,1,category) && DatabaseBind(q,2,item) &&
      DatabaseBind(q,3,wall) && DatabaseBind(q,4,payload) && DatabaseBind(q,5,digest) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) return(false);
   q=DatabasePrepare(db,"UPDATE ph_meta SET sequence=?1,last_wall=MAX(last_wall,?2) WHERE id=1");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,sequence) && DatabaseBind(q,1,wall) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalPutEpisode(const int db,JPWPersonalEpisode &episode,const long wall)
  {
   string raw=JPWPersonalEncodeEpisode(episode),digest="",old="";
   int q=DatabasePrepare(db,"SELECT payload FROM ph_episodes WHERE episode_id=?1");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,episode.episode_id); if(!ok) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(false); }
   ResetLastError(); bool present=DatabaseRead(q);
   ok=present ? DatabaseColumnText(q,0,old) : GetLastError()==ERR_DATABASE_NO_MORE_DATA;
   DatabaseFinalize(q); if(!ok) return(false); if(present && old==raw) return(true);
   long seq=0; if(!JPWPersonalAppend(db,"EPISODE",episode.episode_id,wall,raw,seq) || !JPWPersonalHash(raw,digest)) return(false);
   q=DatabasePrepare(db,"INSERT OR REPLACE INTO ph_episodes VALUES(?1,?2,?3,?4,?5)");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,episode.episode_id) && DatabaseBind(q,1,episode.state) &&
      DatabaseBind(q,2,seq) && DatabaseBind(q,3,raw) && DatabaseBind(q,4,digest) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalPutPeak(const int db,JPWPersonalPeak &peak)
  {
   string raw=JPWPersonalEncodePeak(peak),digest=""; long seq=0;
   if(!JPWPersonalAppend(db,"PEAK",JPWPersonalInt(peak.quality),peak.wall,raw,seq) || !JPWPersonalHash(raw,digest)) return(false);
   int q=DatabasePrepare(db,"INSERT OR REPLACE INTO ph_peaks VALUES(?1,?2,?3,?4)");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,peak.quality) && DatabaseBind(q,1,seq) && DatabaseBind(q,2,raw) && DatabaseBind(q,3,digest) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
bool JPWPersonalLoad(JPWPersonalStoreContext &ctx,JPWPersonalEpisode &episodes[],JPWPersonalPeak &current,JPWPersonalPeak &estimated)
  {
   ArrayResize(episodes,0); current.valid=false; estimated.valid=false;
   if(!JPWPersonalReady(ctx) || (!ctx.writer && (!ctx.read_snapshot || !ctx.transaction_active))) return(false);
   bool reserved=ctx.writer; if(reserved && !JPWPersonalWriteBegin(ctx)) return(false);
   int q=DatabasePrepare(ctx.db,"SELECT payload,digest FROM ph_episodes WHERE state=1 ORDER BY episode_id"); bool ok=q!=INVALID_HANDLE;
   if(!ok) { if(reserved) JPWPersonalWriteFinish(ctx,false,"Leitura recusada"); return(JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Leitura recusada")); } ResetLastError();
   while(DatabaseRead(q))
     {
      string raw="",digest="",actual=""; JPWPersonalEpisode episode; int count=ArraySize(episodes);
      ok=DatabaseColumnText(q,0,raw) && DatabaseColumnText(q,1,digest) && JPWPersonalHash(raw,actual) && actual==digest &&
         JPWPersonalDecodeEpisode(raw,episode) && episode.account_key==ctx.account_key && count<JPW_PERSONAL_MAX_SUBJECTS && ArrayResize(episodes,count+1)==count+1;
      if(!ok) break; episodes[count]=episode; ResetLastError();
     }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA; DatabaseFinalize(q);
   q=DatabasePrepare(ctx.db,"SELECT quality,payload,digest FROM ph_peaks ORDER BY quality"); ok=ok && q!=INVALID_HANDLE; ResetLastError();
   if(q!=INVALID_HANDLE) while(ok && DatabaseRead(q))
     {
      int quality=0; string raw="",digest="",actual=""; JPWPersonalPeak peak;
      ok=DatabaseColumnInteger(q,0,quality) && DatabaseColumnText(q,1,raw) && DatabaseColumnText(q,2,digest) &&
         JPWPersonalHash(raw,actual) && digest==actual && JPWPersonalDecodePeak(raw,peak) && quality==peak.quality && peak.account_key==ctx.account_key;
      if(ok) { if(quality==1) current=peak; else if(quality==2) estimated=peak; else ok=false; } ResetLastError();
     }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA; if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(reserved) ok=JPWPersonalWriteFinish(ctx,ok,"Registro financeiro não confirmado");
   if(!ok) { ArrayResize(episodes,0); current.valid=false; estimated.valid=false; return(JPWPersonalFail(ctx,JPW_STORE_CORRUPT,"Registro financeiro corrompido; nenhum reset")); } return(true);
  }
bool JPWPersonalCommit(JPWPersonalStoreContext &ctx,JPWPersonalCapture &capture,JPWPersonalEpisode &episodes[],
                        JPWPersonalEvent &events[],JPWPersonalPeak &current,JPWPersonalPeak &estimated,const int changed)
  {
   if(capture.account_key!=ctx.account_key) return(JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Contexto alterado; escrita recusada"));
   if(!JPWPersonalWriteBegin(ctx)) return(false);
   bool ok=JPWPersonalOwner(ctx,capture.wall_seconds,capture.mono_ms);
   for(int i=0;ok && i<ArraySize(episodes);i++) ok=episodes[i].account_key==ctx.account_key && JPWPersonalPutEpisode(ctx.db,episodes[i],capture.wall_seconds);
   long seq=0;
   for(int i=0;ok && i<ArraySize(events);i++)
      ok=JPWPersonalAppend(ctx.db,"EVENT",events[i].episode_id,events[i].wall,
         events[i].type+"|"+JPWPersonalHex(events[i].payload),seq);
   if(ok && changed==1) ok=current.valid && current.account_key==ctx.account_key && JPWPersonalPutPeak(ctx.db,current);
   if(ok && changed==2) ok=estimated.valid && estimated.account_key==ctx.account_key && JPWPersonalPutPeak(ctx.db,estimated);
   ok=JPWPersonalWriteFinish(ctx,ok,"Histórico incompleto — gravação não confirmada");
   if(ok) { ctx.result=JPW_STORE_VALID; ctx.reason=""; return(true); }
   return(false);
  }
// Distinct immutable stages. Stage INTENT precedes the external call; CALLED
// and RESULT never claim the human saw/heard an alert. Missing stages remain
// explicitly uncertain after a crash. Each stage shares its group_id.
bool JPWPersonalNotify(JPWPersonalStoreContext &ctx,const string group_id,const string stage,const long wall,const ulong mono,
                        const string payload,JPWPersonalEpisode &episodes[])
  {
   if(stage!="INTENT" && stage!="CALLED" && stage!="RESULT") return(false);
   if(!JPWPersonalWriteBegin(ctx)) return(false);
   bool ok=JPWPersonalOwner(ctx,wall,mono); long seq=0;
   if(ok) ok=JPWPersonalAppend(ctx.db,"ALERT",group_id,wall,stage+"|"+JPWPersonalHex(payload),seq);
   if(stage=="INTENT") for(int i=0;ok && i<ArraySize(episodes);i++) ok=JPWPersonalPutEpisode(ctx.db,episodes[i],wall);
   ok=JPWPersonalWriteFinish(ctx,ok,"Histórico incompleto — gravação não confirmada");
   return(ok);
  }
bool JPWPersonalCoverage(JPWPersonalStoreContext &ctx,const string type,const long wall,const ulong mono,const string detail)
  {
   if(type!="SESSION_START" && type!="SESSION_END" && type!="GAP" && type!="RESUMED" && type!="CLOCK_INCONSISTENT") return(false);
   if(!JPWPersonalWriteBegin(ctx)) return(false);
   bool ok=JPWPersonalOwner(ctx,wall,mono); long seq=0;
   if(ok) ok=JPWPersonalAppend(ctx.db,type=="GAP" || type=="RESUMED" || type=="CLOCK_INCONSISTENT" ? "COVERAGE" : "SESSION",
      ctx.owner_token,wall,type+"|"+JPWPersonalHex(detail),seq);
   ok=JPWPersonalWriteFinish(ctx,ok,"Histórico incompleto — gravação não confirmada");
   return(ok);
  }
bool JPWPersonalReadRow(const int query,JPWPersonalRow &row,const string key="")
  {
   string actual="";
   return(DatabaseColumnType(query,0)==DATABASE_FIELD_TYPE_INTEGER && DatabaseColumnType(query,3)==DATABASE_FIELD_TYPE_INTEGER &&
      DatabaseColumnType(query,1)==DATABASE_FIELD_TYPE_TEXT && DatabaseColumnType(query,2)==DATABASE_FIELD_TYPE_TEXT &&
      DatabaseColumnType(query,4)==DATABASE_FIELD_TYPE_TEXT && DatabaseColumnType(query,5)==DATABASE_FIELD_TYPE_TEXT &&
      DatabaseColumnLong(query,0,row.sequence) && DatabaseColumnText(query,1,row.category) && DatabaseColumnText(query,2,row.item_id) &&
      DatabaseColumnLong(query,3,row.wall) && DatabaseColumnText(query,4,row.payload) && DatabaseColumnText(query,5,row.digest) &&
      row.sequence>0 && JPWPersonalEnvelopeValid(row.category,row.item_id,row.wall,row.payload,key) &&
      JPWPersonalHash(row.payload,actual) && actual==row.digest);
  }
// Consumers stay on the audited reader snapshot; never open a second connection.
bool JPWPersonalReadSummaryFrom(JPWPersonalStoreContext &ctx,JPWPersonalSummary &summary)
  {
   summary.account_key=ctx.account_key; summary.result=ctx.result; summary.reason=ctx.reason; summary.current.valid=false; summary.estimated.valid=false;
   if(!JPWPersonalReady(ctx) || ctx.writer || !ctx.read_snapshot || !ctx.transaction_active) return(false);
   summary.sequence=ctx.snapshot_sequence; summary.started_wall=ctx.started_wall; summary.last_wall=ctx.last_wall;
   summary.active_episodes=ctx.active_episodes; summary.total_episodes=ctx.total_episodes; summary.gaps=ctx.gaps;
   summary.current=ctx.current; summary.estimated=ctx.estimated; summary.result=JPW_STORE_VALID; summary.reason=""; return(true);
  }
bool JPWPersonalReadPageFrom(JPWPersonalStoreContext &ctx,const string category,const long before_seq,const int limit,JPWPersonalRow &rows[],string &reason)
  {
   ArrayResize(rows,0); reason="";
   if(!JPWPersonalReady(ctx) || ctx.writer || !ctx.read_snapshot || !ctx.transaction_active || limit<1 || limit>100 || before_seq<0 ||
      (category!="" && !JPWPersonalCategoryValid(category))) { reason="Snapshot/pedido de página não confirmado"; return(false); }
   int q=DatabasePrepare(ctx.db,"SELECT sequence,category,item_id,wall,payload,digest,(typeof(sequence)='integer' AND typeof(category)='text' AND typeof(item_id)='text' AND typeof(wall)='integer' AND typeof(payload)='text' AND typeof(digest)='text') FROM ph_rows WHERE (?1='' OR category=?1) AND (?2=0 OR sequence<?2) ORDER BY sequence DESC LIMIT ?3");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,category) && DatabaseBind(q,1,before_seq) && DatabaseBind(q,2,limit);
   ResetLastError(); if(ok) while(DatabaseRead(q))
     { int n=ArraySize(rows),typed=0; JPWPersonalRow row; ok=JPWPersonalReadRow(q,row,ctx.account_key) && DatabaseColumnInteger(q,6,typed) && typed==1 && ArrayResize(rows,n+1)==n+1;
       if(!ok) break; rows[n]=row; ResetLastError(); }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA; if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) { ArrayResize(rows,0); reason="Página recusada/corrompida"; } return(ok);
  }
bool JPWPersonalReadDetailFrom(JPWPersonalStoreContext &ctx,const long seq,JPWPersonalRow &row,string &reason)
  {
   reason=""; if(!JPWPersonalReady(ctx) || ctx.writer || !ctx.read_snapshot || !ctx.transaction_active || seq<1) { reason="Snapshot de detalhe não confirmado"; return(false); }
   int q=DatabasePrepare(ctx.db,"SELECT sequence,category,item_id,wall,payload,digest,(typeof(sequence)='integer' AND typeof(category)='text' AND typeof(item_id)='text' AND typeof(wall)='integer' AND typeof(payload)='text' AND typeof(digest)='text') FROM ph_rows WHERE sequence=?1"); int typed=0;
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,seq) && DatabaseRead(q) && JPWPersonalReadRow(q,row,ctx.account_key) && DatabaseColumnInteger(q,6,typed) && typed==1 && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); if(!ok) { row.sequence=0; row.payload=""; reason="Detalhe ausente/corrompido"; } return(ok);
  }
bool JPWPersonalListAccounts(string &keys[])
  {
   ArrayResize(keys,0); string found=""; long handle=FileFindFirst(JPW_PERSONAL_FOLDER+"history_*.sqlite",found);
   if(handle==INVALID_HANDLE) return(true);
   do
     {
      string key=StringSubstr(found,8,64); if(StringLen(found)!=79 || !JPWPersonalHashValid(key)) continue;
      int n=ArraySize(keys); if(ArrayResize(keys,n+1)!=n+1) { FileFindClose(handle); return(false); } keys[n]=key;
     }
   while(FileFindNext(handle,found)); FileFindClose(handle); return(true);
  }
#endif

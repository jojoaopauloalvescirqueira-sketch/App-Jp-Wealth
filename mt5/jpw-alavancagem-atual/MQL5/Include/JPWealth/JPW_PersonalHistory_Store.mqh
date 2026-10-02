#ifndef JPW_PERSONAL_HISTORY_STORE_MQH
#define JPW_PERSONAL_HISTORY_STORE_MQH
#include <JPWealth/JPW_PersonalHistory_Core.mqh>
#include <JPWealth/JPW_Alavancagem_Store_Result.mqh>
#define JPW_PERSONAL_SCHEMA 1
#define JPW_PERSONAL_FOLDER "JPWealth\\Genetrix\\PersonalHistory\\"
#define JPW_PERSONAL_LEASE_MS 15000
struct JPWPersonalStoreContext
  { int db; string account_key; string owner_token; bool writer; JPWStoreResult result; string reason; };
struct JPWPersonalRow
  { long sequence; string category; string item_id; long wall; string payload; string digest; };
struct JPWPersonalSummary
  {
   JPWStoreResult result; string reason; string account_key; long sequence;
   long started_wall; long last_wall; int active_episodes; int total_episodes; int gaps;
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
string JPWPersonalPath(const string key)
  { return(JPWPersonalHashValid(key) ? JPW_PERSONAL_FOLDER+"history_"+key+".sqlite" : ""); }
bool JPWPersonalDone(const int query)
  { ResetLastError(); bool row=DatabaseRead(query); return(!row && GetLastError()==ERR_DATABASE_NO_MORE_DATA); }
bool JPWPersonalFail(JPWPersonalStoreContext &ctx,const JPWStoreResult result,const string reason)
  { ctx.result=result; ctx.reason=reason; return(false); }
bool JPWPersonalOpenFail(JPWPersonalStoreContext &ctx,const JPWStoreResult result,const string reason)
  { if(ctx.db!=INVALID_HANDLE) DatabaseClose(ctx.db); ctx.db=INVALID_HANDLE; ctx.writer=false; return(JPWPersonalFail(ctx,result,reason)); }
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
bool JPWPersonalEpisodeProjectionIntegrity(const int db,string &reason)
  {
   reason="";
   // The SQL state is a selector, therefore it must be audited even for rows
   // excluded from the active projection. A valid payload cannot authorize a
   // different scalar state to hide an unresolved no-SL episode.
   int q=DatabasePrepare(db,"SELECT p.episode_id,p.state,p.payload,p.digest,m.account_key,(typeof(p.state)='integer' AND p.state IN(1,2,3)) FROM ph_episodes p CROSS JOIN ph_meta m WHERE m.id=1 ORDER BY p.episode_id");
   if(q==INVALID_HANDLE) { reason="Projeção de episódios indisponível"; return(false); }
   bool ok=true; ResetLastError();
   while(DatabaseRead(q))
     {
      int state=0,type_valid=0; string id="",raw="",digest="",key="",actual=""; JPWPersonalEpisode episode;
      ok=DatabaseColumnText(q,0,id) && DatabaseColumnInteger(q,1,state) && DatabaseColumnText(q,2,raw) &&
         DatabaseColumnText(q,3,digest) && DatabaseColumnText(q,4,key) && DatabaseColumnInteger(q,5,type_valid) && type_valid==1 &&
         JPWPersonalHash(raw,actual) && actual==digest &&
         JPWPersonalDecodeEpisode(raw,episode) && episode.episode_id==id && episode.state==state && episode.account_key==key;
      if(!ok) break; ResetLastError();
     }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA; DatabaseFinalize(q);
   if(!ok) reason="Estado/identidade da projeção diverge do episódio íntegro; nenhum reset";
   return(ok);
  }
bool JPWPersonalIntegrity(const int db,string &reason)
  {
   reason=""; int q=DatabasePrepare(db,"PRAGMA quick_check"); string status="";
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnText(q,0,status) && status=="ok";
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) { reason="Integridade SQLite recusada; nenhum reset"; return(false); }
   if(!JPWPersonalEpisodeProjectionIntegrity(db,reason)) return(false);
   // Every mutable projection must point to an immutable journal witness.
   q=DatabasePrepare(db,"SELECT COUNT(*) FROM ph_episodes p LEFT JOIN ph_rows r ON r.sequence=p.sequence WHERE r.sequence IS NULL OR r.category<>'EPISODE' OR r.item_id<>p.episode_id OR r.payload<>p.payload OR r.digest<>p.digest"); int bad=0;
   ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,bad) && bad==0;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   q=DatabasePrepare(db,"SELECT COUNT(*) FROM ph_peaks p LEFT JOIN ph_rows r ON r.sequence=p.sequence WHERE r.sequence IS NULL OR r.category<>'PEAK' OR r.payload<>p.payload OR r.digest<>p.digest");
   ok=ok && q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,bad) && bad==0;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   q=DatabasePrepare(db,"SELECT COUNT(*) FROM (SELECT item_id,MAX(sequence) latest FROM ph_rows WHERE category='EPISODE' GROUP BY item_id) r LEFT JOIN ph_episodes p ON p.episode_id=r.item_id WHERE p.episode_id IS NULL OR p.sequence<>r.latest");
   ok=ok && q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,bad) && bad==0;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   q=DatabasePrepare(db,"SELECT COUNT(*) FROM (SELECT item_id,MAX(sequence) latest FROM ph_rows WHERE category='PEAK' GROUP BY item_id) r LEFT JOIN ph_peaks p ON CAST(p.quality AS TEXT)=r.item_id WHERE p.quality IS NULL OR p.sequence<>r.latest");
   ok=ok && q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,bad) && bad==0;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   q=DatabasePrepare(db,"SELECT sequence,(SELECT COUNT(*) FROM ph_rows),(SELECT COALESCE(MAX(sequence),0) FROM ph_rows) FROM ph_meta WHERE id=1");
   long sequence=0,count=0,maximum=0;
   ok=ok && q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,sequence) && DatabaseColumnLong(q,1,count) &&
      DatabaseColumnLong(q,2,maximum) && sequence>=0 && count==sequence && maximum==sequence;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) reason="Histórico/projeção/sequência divergente; escrita recusada";
   return(ok);
  }
// Full startup audit is bounded and never repeated by the Cockpit readers.
// Exceeding capacity is unavailable, not corruption or permission to reset.
#define JPW_PERSONAL_STARTUP_AUDIT_MAX_ROWS 100000
#define JPW_PERSONAL_STARTUP_AUDIT_MAX_MS 2000
JPWStoreResult JPWPersonalAuditRows(const int db,string &reason)
  {
   reason=""; ulong started=GetTickCount64();
   int q=DatabasePrepare(db,"SELECT sequence,wall,payload,digest FROM ph_rows ORDER BY sequence");
   if(q==INVALID_HANDLE) { reason="Auditoria histórica indisponível"; return(JPW_STORE_IO_ERROR); }
   long expected=0; bool ok=true,capacity=false; ResetLastError();
   while(DatabaseRead(q))
     {
      if(expected>=JPW_PERSONAL_STARTUP_AUDIT_MAX_ROWS || GetTickCount64()-started>JPW_PERSONAL_STARTUP_AUDIT_MAX_MS)
        { capacity=true; ok=false; break; }
      long seq=0,wall=0; string raw="",digest="",actual="";
      ok=DatabaseColumnLong(q,0,seq) && DatabaseColumnLong(q,1,wall) && DatabaseColumnText(q,2,raw) &&
         DatabaseColumnText(q,3,digest) && seq==expected+1 && wall>0 && JPWPersonalHash(raw,actual) && digest==actual;
      if(!ok) break; expected++; ResetLastError();
     }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA; DatabaseFinalize(q);
   if(capacity) { reason="Auditoria inicial excede capacidade; histórico preservado e escrita indisponível"; return(JPW_STORE_IO_ERROR); }
   if(!ok) { reason="Payload histórico corrompido; escrita recusada, nenhum reset"; return(JPW_STORE_CORRUPT); }
   return(JPW_STORE_VALID);
  }
bool JPWPersonalOpen(const string key,const bool writer,const string token,const long wall,const ulong mono,JPWPersonalStoreContext &ctx)
  {
   ctx.db=INVALID_HANDLE; ctx.account_key=key; ctx.owner_token=token; ctx.writer=false; ctx.result=JPW_STORE_ABSENT; ctx.reason="";
   string path=JPWPersonalPath(key); if(path=="") return(JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Identidade opaca inválida"));
   bool exists=FileIsExist(path);
   if(!exists && !writer) return(JPWPersonalFail(ctx,JPW_STORE_ABSENT,"Histórico ainda não iniciado nesta instalação"));
   if(writer && (!JPWPersonalHashValid(token) || wall<=0 || mono==0)) return(JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Titular/relógio inválido"));
   if(writer) { FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\PersonalHistory"); }
   ResetLastError(); ctx.db=DatabaseOpen(path,writer ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE : DATABASE_OPEN_READONLY);
   if(ctx.db==INVALID_HANDLE) return(JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Banco indisponível; nenhum reset"));
   if(!exists && !JPWPersonalSchemaCreate(ctx.db,key,wall))
     { DatabaseClose(ctx.db); ctx.db=INVALID_HANDLE; return(JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Inicialização não confirmada; preservar arquivo")); }
   DatabaseExecute(ctx.db,"PRAGMA busy_timeout=0");
   int q=DatabasePrepare(ctx.db,"SELECT schema_version,account_key FROM ph_meta WHERE id=1"); int version=0; string stored="";
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,version) && DatabaseColumnText(q,1,stored);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok || version!=JPW_PERSONAL_SCHEMA || stored!=key)
     { DatabaseClose(ctx.db); ctx.db=INVALID_HANDLE; return(JPWPersonalFail(ctx,ok ? JPW_STORE_INCOMPATIBLE : JPW_STORE_CORRUPT,"Schema/conta incompatível ou corrompido; nenhum reset")); }
   string reason="";
   if(!JPWPersonalIntegrity(ctx.db,reason))
     { DatabaseClose(ctx.db); ctx.db=INVALID_HANDLE; return(JPWPersonalFail(ctx,JPW_STORE_CORRUPT,reason)); }
   ctx.result=JPW_STORE_VALID;
   if(!writer) return(true);
   JPWStoreResult audit=JPWPersonalAuditRows(ctx.db,reason);
   if(audit!=JPW_STORE_VALID) return(JPWPersonalOpenFail(ctx,audit,reason));
   if(!DatabaseTransactionBegin(ctx.db)) return(JPWPersonalOpenFail(ctx,JPW_STORE_BUSY,"Histórico ocupado; não emitir avisos como outro titular"));
   q=DatabasePrepare(ctx.db,"SELECT token,mono,wall FROM ph_owner WHERE id=1"); string owner=""; long last_mono=0,last_wall=0;
   ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnText(q,0,owner) && DatabaseColumnLong(q,1,last_mono) && DatabaseColumnLong(q,2,last_wall);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   // Token is a fence. Each subsequent transaction verifies it again.
   bool expired=(mono>=(ulong)last_mono && mono-(ulong)last_mono>JPW_PERSONAL_LEASE_MS) ||
      (mono<(ulong)last_mono && wall>last_wall+15);
   if(!ok || (owner!="" && owner!=token && !expired))
     { DatabaseTransactionRollback(ctx.db); return(JPWPersonalOpenFail(ctx,ok ? JPW_STORE_BUSY : JPW_STORE_CORRUPT,"Outro escritor ativo ou relógio não verificável")); }
   q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET token=?1,mono=?2,wall=?3 WHERE id=1");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,token) && DatabaseBind(q,1,(long)mono) && DatabaseBind(q,2,wall) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(ok) ok=DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
   if(!ok) return(JPWPersonalOpenFail(ctx,JPW_STORE_IO_ERROR,"Aquisição de titularidade não confirmada"));
   ctx.writer=true; return(true);
  }
bool JPWPersonalOwner(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   if(!ctx.writer || ctx.db==INVALID_HANDLE) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Sem titularidade de escrita"));
   int q=DatabasePrepare(ctx.db,"SELECT token,mono FROM ph_owner WHERE id=1"); string token=""; long previous=0;
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnText(q,0,token) && DatabaseColumnLong(q,1,previous) &&
      token==ctx.owner_token && mono>=(ulong)previous;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) { ctx.writer=false; return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Titularidade perdida; avisos/gravações suspensos")); }
   q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET mono=?1,wall=?2 WHERE id=1 AND token=?3");
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,(long)mono) && DatabaseBind(q,1,wall) && DatabaseBind(q,2,ctx.owner_token) && JPWPersonalDone(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   return(ok || JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Heartbeat não confirmado"));
  }
bool JPWPersonalKeepAlive(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   if(!DatabaseTransactionBegin(ctx.db)) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Histórico ocupado"));
   bool ok=JPWPersonalOwner(ctx,wall,mono); if(ok) ok=DatabaseTransactionCommit(ctx.db);
   if(!ok) DatabaseTransactionRollback(ctx.db); return(ok);
  }
void JPWPersonalClose(JPWPersonalStoreContext &ctx,const long wall,const ulong mono)
  {
   if(ctx.db!=INVALID_HANDLE && ctx.writer && DatabaseTransactionBegin(ctx.db))
     {
      int q=DatabasePrepare(ctx.db,"UPDATE ph_owner SET token='',mono=0,wall=?1 WHERE id=1 AND token=?2");
      bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,wall) && DatabaseBind(q,1,ctx.owner_token) && JPWPersonalDone(q);
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(ok) ok=DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
     }
   if(ctx.db!=INVALID_HANDLE) DatabaseClose(ctx.db); ctx.db=INVALID_HANDLE; ctx.writer=false;
  }
bool JPWPersonalAppend(const int db,const string category,const string item,const long wall,const string payload,long &sequence)
  {
   sequence=0; string digest=""; if(!JPWPersonalHash(payload,digest)) return(false);
   int q=DatabasePrepare(db,"SELECT sequence FROM ph_meta WHERE id=1"); long old=0;
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,old) && old>=0 && old<LONG_MAX-1;
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
   if(ctx.db==INVALID_HANDLE) return(false);
   int q=DatabasePrepare(ctx.db,"SELECT payload,digest FROM ph_episodes WHERE state=1 ORDER BY episode_id"); bool ok=q!=INVALID_HANDLE;
   if(!ok) return(JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Leitura recusada")); ResetLastError();
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
   if(!ok) return(JPWPersonalFail(ctx,JPW_STORE_CORRUPT,"Registro financeiro corrompido; nenhum reset")); return(true);
  }
bool JPWPersonalCommit(JPWPersonalStoreContext &ctx,JPWPersonalCapture &capture,JPWPersonalEpisode &episodes[],
                        JPWPersonalEvent &events[],JPWPersonalPeak &current,JPWPersonalPeak &estimated,const int changed)
  {
   if(capture.account_key!=ctx.account_key) return(JPWPersonalFail(ctx,JPW_STORE_INCOMPATIBLE,"Contexto alterado; escrita recusada"));
   if(!DatabaseTransactionBegin(ctx.db)) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Histórico ocupado"));
   bool ok=JPWPersonalOwner(ctx,capture.wall_seconds,capture.mono_ms);
   for(int i=0;ok && i<ArraySize(episodes);i++) ok=episodes[i].account_key==ctx.account_key && JPWPersonalPutEpisode(ctx.db,episodes[i],capture.wall_seconds);
   long seq=0;
   for(int i=0;ok && i<ArraySize(events);i++)
      ok=JPWPersonalAppend(ctx.db,"EVENT",events[i].episode_id,events[i].wall,
         events[i].type+"|"+JPWPersonalHex(events[i].payload),seq);
   if(ok && changed==1) ok=current.valid && current.account_key==ctx.account_key && JPWPersonalPutPeak(ctx.db,current);
   if(ok && changed==2) ok=estimated.valid && estimated.account_key==ctx.account_key && JPWPersonalPutPeak(ctx.db,estimated);
   if(ok) ok=DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
   if(ok) { ctx.result=JPW_STORE_VALID; ctx.reason=""; return(true); }
   return(JPWPersonalFail(ctx,ctx.writer ? JPW_STORE_IO_ERROR : JPW_STORE_BUSY,"Histórico incompleto — gravação não confirmada"));
  }
// Distinct immutable stages. Stage INTENT precedes the external call; CALLED
// and RESULT never claim the human saw/heard an alert. Missing stages remain
// explicitly uncertain after a crash. Each stage shares its group_id.
bool JPWPersonalNotify(JPWPersonalStoreContext &ctx,const string group_id,const string stage,const long wall,const ulong mono,
                        const string payload,JPWPersonalEpisode &episodes[])
  {
   if(stage!="INTENT" && stage!="CALLED" && stage!="RESULT") return(false);
   if(!DatabaseTransactionBegin(ctx.db)) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Aviso sem confirmação de gravação"));
   bool ok=JPWPersonalOwner(ctx,wall,mono); long seq=0;
   if(ok) ok=JPWPersonalAppend(ctx.db,"ALERT",group_id,wall,stage+"|"+JPWPersonalHex(payload),seq);
   if(stage=="INTENT") for(int i=0;ok && i<ArraySize(episodes);i++) ok=JPWPersonalPutEpisode(ctx.db,episodes[i],wall);
   if(ok) ok=DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
   return(ok || JPWPersonalFail(ctx,ctx.writer ? JPW_STORE_IO_ERROR : JPW_STORE_BUSY,"Histórico incompleto — aviso não confirmado"));
  }
bool JPWPersonalCoverage(JPWPersonalStoreContext &ctx,const string type,const long wall,const ulong mono,const string detail)
  {
   if(type!="SESSION_START" && type!="SESSION_END" && type!="GAP" && type!="RESUMED" && type!="CLOCK_INCONSISTENT") return(false);
   if(!DatabaseTransactionBegin(ctx.db)) return(JPWPersonalFail(ctx,JPW_STORE_BUSY,"Cobertura não confirmada"));
   bool ok=JPWPersonalOwner(ctx,wall,mono); long seq=0;
   if(ok) ok=JPWPersonalAppend(ctx.db,type=="GAP" || type=="RESUMED" || type=="CLOCK_INCONSISTENT" ? "COVERAGE" : "SESSION",
      ctx.owner_token,wall,type+"|"+JPWPersonalHex(detail),seq);
   if(ok) ok=DatabaseTransactionCommit(ctx.db); if(!ok) DatabaseTransactionRollback(ctx.db);
   return(ok || JPWPersonalFail(ctx,JPW_STORE_IO_ERROR,"Cobertura incompleta — gravação não confirmada"));
  }
bool JPWPersonalReadRow(const int query,JPWPersonalRow &row)
  {
   string actual="";
   return(DatabaseColumnLong(query,0,row.sequence) && DatabaseColumnText(query,1,row.category) && DatabaseColumnText(query,2,row.item_id) &&
      DatabaseColumnLong(query,3,row.wall) && DatabaseColumnText(query,4,row.payload) && DatabaseColumnText(query,5,row.digest) &&
      row.sequence>0 && row.wall>0 && JPWPersonalHash(row.payload,actual) && actual==row.digest);
  }
bool JPWPersonalReadPage(const string key,const string category,const long before_seq,const int limit,JPWPersonalRow &rows[],string &reason)
  {
   ArrayResize(rows,0); reason=""; if(limit<1 || limit>100 || before_seq<0) return(false);
   JPWPersonalStoreContext ctx; if(!JPWPersonalOpen(key,false,"",0,0,ctx)) { reason=ctx.reason; return(false); }
   string sql="SELECT sequence,category,item_id,wall,payload,digest FROM ph_rows WHERE (?1='' OR category=?1) AND (?2=0 OR sequence<?2) ORDER BY sequence DESC LIMIT ?3";
   int q=DatabasePrepare(ctx.db,sql); bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,category) && DatabaseBind(q,1,before_seq) && DatabaseBind(q,2,limit);
   ResetLastError(); if(ok) while(DatabaseRead(q))
     { int n=ArraySize(rows); JPWPersonalRow row; if(!JPWPersonalReadRow(q,row) || ArrayResize(rows,n+1)!=n+1) { ok=false; break; }
       rows[n]=row; ResetLastError(); }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); JPWPersonalClose(ctx,0,0);
   if(!ok) { reason="Página recusada/corrompida"; ArrayResize(rows,0); } return(ok);
  }
bool JPWPersonalReadDetail(const string key,const long seq,JPWPersonalRow &row,string &reason)
  {
   JPWPersonalStoreContext ctx; reason=""; if(!JPWPersonalOpen(key,false,"",0,0,ctx)) { reason=ctx.reason; return(false); }
   int q=DatabasePrepare(ctx.db,"SELECT sequence,category,item_id,wall,payload,digest FROM ph_rows WHERE sequence=?1");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,seq) && DatabaseRead(q) && JPWPersonalReadRow(q,row);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); JPWPersonalClose(ctx,0,0); if(!ok) reason="Detalhe ausente/corrompido"; return(ok);
  }
bool JPWPersonalReadSummary(const string key,JPWPersonalSummary &summary)
  {
   summary.account_key=key; summary.current.valid=false; summary.estimated.valid=false;
   summary.sequence=0; summary.started_wall=0; summary.last_wall=0; summary.active_episodes=0; summary.total_episodes=0; summary.gaps=0;
   JPWPersonalStoreContext ctx; if(!JPWPersonalOpen(key,false,"",0,0,ctx)) { summary.result=ctx.result; summary.reason=ctx.reason; return(false); }
   int q=DatabasePrepare(ctx.db,"SELECT sequence,started_wall,last_wall,(SELECT COUNT(*) FROM ph_episodes WHERE state=1),(SELECT COUNT(*) FROM ph_episodes),(SELECT COUNT(*) FROM ph_rows WHERE category='COVERAGE' AND payload LIKE 'GAP|%') FROM ph_meta WHERE id=1");
   bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,summary.sequence) && DatabaseColumnLong(q,1,summary.started_wall) &&
      DatabaseColumnLong(q,2,summary.last_wall) && DatabaseColumnInteger(q,3,summary.active_episodes) && DatabaseColumnInteger(q,4,summary.total_episodes) && DatabaseColumnInteger(q,5,summary.gaps);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   JPWPersonalEpisode episodes[]; if(ok) ok=JPWPersonalLoad(ctx,episodes,summary.current,summary.estimated);
   summary.result=ok ? JPW_STORE_VALID : (ctx.result==JPW_STORE_VALID ? JPW_STORE_IO_ERROR : ctx.result);
   summary.reason=ok ? "" : (ctx.reason=="" ? "Resumo histórico não confirmado" : ctx.reason); JPWPersonalClose(ctx,0,0); return(ok);
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

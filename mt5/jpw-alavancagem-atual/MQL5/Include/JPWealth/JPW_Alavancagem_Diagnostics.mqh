#ifndef JPW_ALAVANCAGEM_DIAGNOSTICS_MQH
#define JPW_ALAVANCAGEM_DIAGNOSTICS_MQH
#include <JPWealth/JPW_Alavancagem_Diagnostics_Core.mqh>
#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>

// Technical-only namespace: never reads/deletes the sibling financial stores.
// One installation-wide database and export; no identifiers/tickets/values in
// free text. All callers pass enum codes, an opaque hash and a collection id.
#define JPW_DIAG_FOLDER "JPWealth\\Alavancagem\\Diagnostics\\"
#define JPW_DIAG_SELECT "id,context_key,component,code,sample_id,first_utc,last_utc,mono_ms,repetitions,product_version,calculation_version,build_id,checksum"
// This terminal-session counter is technical only. Never reset/delete it:
// another program on the same chart may still own an earlier ordinal.
#define JPW_DIAG_INSTANCE_SEQUENCE "JPW_DIAG_INSTANCE_SEQ_V1"
bool JPWDiagFailureKey(const string context,const int component,long &instance_id,
                        string &key,string &reason)
  {
   key=""; reason="";
   if(!JPWRaizNIsHash(context) || component<JPW_DIAG_INDICATOR ||
      component>JPW_DIAG_SUPERVISOR || instance_id<0 ||
      instance_id>9007199254740991)
     { reason="Identidade da instancia de diagnostico invalida"; return(false); }
   if(instance_id==0)
     {
      // GlobalVariableTemp preserves an existing variable. In particular, do
      // not initialize through GlobalVariableSet(...,0): that would race.
      if(!GlobalVariableCheck(JPW_DIAG_INSTANCE_SEQUENCE) &&
         !GlobalVariableTemp(JPW_DIAG_INSTANCE_SEQUENCE) &&
         !GlobalVariableCheck(JPW_DIAG_INSTANCE_SEQUENCE))
        { reason="Contador temporario de diagnostico indisponivel"; return(false); }
      for(int attempt=0;attempt<8 && instance_id==0;attempt++)
        {
         double previous=0.0;
         if(!GlobalVariableGet(JPW_DIAG_INSTANCE_SEQUENCE,previous) ||
            !MathIsValidNumber(previous) || previous<0.0 ||
            previous!=MathFloor(previous) || previous>=9007199254740991.0)
           { reason="Contador de diagnostico invalido ou esgotado"; return(false); }
         if(GlobalVariableSetOnCondition(JPW_DIAG_INSTANCE_SEQUENCE,previous+1.0,previous))
            instance_id=(long)(previous+1.0);
        }
      if(instance_id==0)
        { reason="Identidade da instancia ocupada; alocacao adiada"; return(false); }
     }
   // At most 53 characters. ChartID alone is not an instance identity: an EA
   // and several indicators can share the same chart and opaque account key.
   key="JPW_DIAG_FAIL_"+StringSubstr(context,0,20)+"_"+
      IntegerToString(component)+"_"+IntegerToString(instance_id);
   return(StringLen(key)<=63);
  }
bool JPWDiagSetTemporaryMarker(const string key)
  {
   if(!GlobalVariableCheck(key) && !GlobalVariableTemp(key) && !GlobalVariableCheck(key))
      return(false);
   return(GlobalVariableSet(key,(double)TimeGMT())!=0);
  }
bool JPWDiagMarkFailure(const string context,const int component,long &instance_id,
                         string &reason)
  {
   string key="";
   if(!JPWDiagFailureKey(context,component,instance_id,key,reason))
     {
      // Allocation failure must not fall back to a colliding ChartID key.
      // This conservative context notice remains for the terminal session;
      // no successful writer is allowed to erase it.
      if(JPWRaizNIsHash(context))
         if(!JPWDiagSetTemporaryMarker("JPW_DIAG_FAIL_"+
                  StringSubstr(context,0,20)+"_ALLOCATION_FAILED"))
            reason+="; aviso temporario tambem indisponivel";
      return(false);
     }
   if(!JPWDiagSetTemporaryMarker(key))
     { reason="Marcador de falha de diagnostico indisponivel"; return(false); }
   return(true);
  }
bool JPWDiagClearFailure(const string context,const int component,const long instance_id,
                          string &reason)
  {
   reason="";
   if(instance_id==0) return(true); // Success never allocates a writer identity.
   long own_id=instance_id;
   string key="";
   if(!JPWDiagFailureKey(context,component,own_id,key,reason)) return(false);
   if(GlobalVariableCheck(key) && !GlobalVariableDel(key))
     { reason="Marcador da propria instancia nao foi liberado"; return(false); }
   return(true);
  }
struct JPWDiagEvent
  {
   long id;
   string context_key;
   int component;
   int code;
   long sample_id;
   long first_utc;
   long last_utc;
   long mono_ms;
   long repetitions;
   string product_version;
   string calculation_version;
   string build_id;
   string checksum;
  };
bool JPWDiagFolderValid(const string folder)
  {
   return(folder==JPW_DIAG_FOLDER ||
      (StringFind(folder,JPW_DIAG_FOLDER+"Synthetic\\")==0 &&
       JPWRaizNFolderValid(folder)));
  }
bool JPWDiagExecute(const int q)
  {
   ResetLastError(); DatabaseRead(q);
   return(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
  }
bool JPWDiagScalar(const int db,const string sql,long &value)
  {
   value=0;
   const int q=DatabasePrepare(db,sql);
   if(q==INVALID_HANDLE) return(false);
   bool ok=DatabaseRead(q) && DatabaseColumnLong(q,0,value);
   DatabaseFinalize(q);
   return(ok);
  }
bool JPWDiagSafeVersion(const string value)
  {
   if(StringLen(value)<1 || StringLen(value)>32) return(false);
   for(int i=0;i<StringLen(value);i++)
     { const ushort c=StringGetCharacter(value,i);
       if(!((c>='0' && c<='9') || c=='.')) return(false); }
   return(true);
  }
bool JPWDiagSafeBuild(const string value)
  {
   if(StringLen(value)<1 || StringLen(value)>80) return(false);
   for(int i=0;i<StringLen(value);i++)
     { const ushort c=StringGetCharacter(value,i);
       if(!((c>='0' && c<='9') || (c>='a' && c<='z') || c=='-' || c=='.'))
          return(false); }
   return(true);
  }
bool JPWDiagChecksum(JPWDiagEvent &e,string &checksum)
  {
   checksum="";
   if(e.id<=0 || !JPWRaizNIsHash(e.context_key) ||
      !JPWDiagEventValid(e.component,e.code,e.sample_id,e.first_utc,e.mono_ms) ||
      e.last_utc<e.first_utc || e.repetitions<1 ||
      !JPWDiagSafeVersion(e.product_version) ||
      !JPWDiagSafeVersion(e.calculation_version) || !JPWDiagSafeBuild(e.build_id))
      return(false);
   const string body=IntegerToString(JPW_DIAG_SCHEMA)+"|"+
      IntegerToString(e.id)+"|"+e.context_key+"|"+IntegerToString(e.component)+"|"+
      IntegerToString(e.code)+"|"+IntegerToString(e.sample_id)+"|"+
      IntegerToString(e.first_utc)+"|"+IntegerToString(e.last_utc)+"|"+
      IntegerToString(e.mono_ms)+"|"+IntegerToString(e.repetitions)+"|"+
      e.product_version+"|"+e.calculation_version+"|"+e.build_id;
   return(JPWRaizNHash(body,checksum));
  }
JPWStoreResult JPWDiagRead(const int q,JPWDiagEvent &e)
  {
   ResetLastError();
   const bool ok=DatabaseReadBind(q,e);
   const int error=GetLastError();
   if(!ok) return(error==ERR_DATABASE_NO_MORE_DATA ? JPW_STORE_ABSENT : JPW_STORE_IO_ERROR);
   string checksum="";
   if(!JPWDiagChecksum(e,checksum) || checksum!=e.checksum) return(JPW_STORE_CORRUPT);
   return(JPW_STORE_VALID);
  }
bool JPWDiagFileBounded(const string path,const long bound)
  {
   if(!FileIsExist(path)) return(true);
   const int file=FileOpen(path,FILE_READ|FILE_BIN|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(file==INVALID_HANDLE) return(false);
   const ulong size=FileSize(file); FileClose(file);
   return(size<=(ulong)bound);
  }
void JPWDiagClose(const int db,const int lock)
  {
   if(db!=INVALID_HANDLE) DatabaseClose(db);
   if(lock!=INVALID_HANDLE) FileClose(lock);
  }
JPWStoreResult JPWDiagOpen(const string folder,const bool write,int &db,int &lock,string &reason)
  {
   db=INVALID_HANDLE; lock=INVALID_HANDLE; reason="";
   if(!JPWDiagFolderValid(folder))
     { reason="Namespace de diagnostico invalido"; return(JPW_STORE_IO_ERROR); }
   const string path=folder+"events_v1.sqlite";
   if(!FileIsExist(path) && !write)
     { reason="Ainda nao ha eventos tecnicos locais"; return(JPW_STORE_ABSENT); }
   if(write && !FolderCreate(folder))
     { reason="Pasta de diagnostico indisponivel"; return(JPW_STORE_IO_ERROR); }
   // Exclusive non-sharing file lock; no spin/sleep. Readers also release it
   // before UI rendering. The empty lock file is not a retained event record.
   lock=FileOpen(folder+"events_v1.lock",FILE_READ|FILE_WRITE|FILE_BIN);
   if(lock==INVALID_HANDLE)
     { reason="Trilha tecnica ocupada; tentar em outro ciclo"; return(JPW_STORE_BUSY); }
   if(!JPWDiagFileBounded(path,JPW_DIAG_DB_LIMIT_BYTES) ||
      !JPWDiagFileBounded(path+"-journal",JPW_DIAG_DB_LIMIT_BYTES+65536) ||
      !JPWDiagFileBounded(folder+"diagnostics_export.txt",JPW_DIAG_EXPORT_LIMIT_BYTES) ||
      FileIsExist(path+"-wal") || FileIsExist(path+"-shm"))
     { reason="Limite ou modo de armazenamento tecnico divergente";
       JPWDiagClose(db,lock); lock=INVALID_HANDLE; return(JPW_STORE_INCOMPATIBLE); }
   db=DatabaseOpen(path,write ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE : DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE)
     { reason="Banco tecnico indisponivel"; JPWDiagClose(db,lock); lock=INVALID_HANDLE;
       return(JPW_STORE_IO_ERROR); }
   long table_count=0;
   bool ok=JPWDiagScalar(db,"SELECT COUNT(*) FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'",table_count);
   if(ok && table_count==0 && write)
     {
      // 8 MiB DB + DELETE journal (at most DB pages plus headers) + 64 KiB
      // fixed export stays below the 20 MiB installation-wide limit.
      ok=DatabaseExecute(db,"PRAGMA page_size=4096") &&
         DatabaseExecute(db,"PRAGMA journal_mode=DELETE") &&
         DatabaseExecute(db,"PRAGMA synchronous=FULL") &&
         DatabaseExecute(db,"PRAGMA max_page_count=2048") &&
         DatabaseExecute(db,"PRAGMA temp_store=MEMORY") &&
         DatabaseExecute(db,"PRAGMA busy_timeout=0") && DatabaseTransactionBegin(db);
      if(ok) ok=DatabaseExecute(db,"CREATE TABLE diag_meta(schema_version INTEGER NOT NULL)") &&
         DatabaseExecute(db,"INSERT INTO diag_meta VALUES(1)") &&
         DatabaseExecute(db,"CREATE TABLE diag_events(id INTEGER PRIMARY KEY,context_key TEXT NOT NULL,component INTEGER NOT NULL,code INTEGER NOT NULL,sample_id INTEGER NOT NULL,first_utc INTEGER NOT NULL,last_utc INTEGER NOT NULL,mono_ms INTEGER NOT NULL,repetitions INTEGER NOT NULL,product_version TEXT NOT NULL,calculation_version TEXT NOT NULL,build_id TEXT NOT NULL,checksum TEXT NOT NULL)") &&
         DatabaseExecute(db,"CREATE INDEX diag_context ON diag_events(context_key,last_utc)");
      if(ok) ok=DatabaseTransactionCommit(db);
      if(!ok) DatabaseTransactionRollback(db);
     }
   long schema=0,meta_count=0,page_size=0;
   ok=ok && JPWDiagScalar(db,"SELECT COUNT(*) FROM diag_meta",meta_count) && meta_count==1 &&
      JPWDiagScalar(db,"SELECT schema_version FROM diag_meta",schema) &&
      JPWDiagScalar(db,"PRAGMA page_size",page_size);
   if(!ok || schema!=JPW_DIAG_SCHEMA || page_size!=4096)
     { reason="Schema tecnico corrompido ou incompativel";
       JPWDiagClose(db,lock); db=INVALID_HANDLE; lock=INVALID_HANDLE;
       return(ok ? JPW_STORE_INCOMPATIBLE : JPW_STORE_CORRUPT); }
   // These are connection-specific; reapply for every writer. Reject other
   // journal modes rather than silently migrating a modified database.
   const int mode_query=DatabasePrepare(db,"PRAGMA journal_mode");
   string mode="";
   ok=mode_query!=INVALID_HANDLE && DatabaseRead(mode_query) && DatabaseColumnText(mode_query,0,mode);
   if(mode_query!=INVALID_HANDLE) DatabaseFinalize(mode_query);
   if(!ok || mode!="delete")
     { reason="Modo do banco tecnico incompativel"; JPWDiagClose(db,lock);
       db=INVALID_HANDLE; lock=INVALID_HANDLE; return(JPW_STORE_INCOMPATIBLE); }
   if(write) ok=DatabaseExecute(db,"PRAGMA synchronous=FULL") &&
      DatabaseExecute(db,"PRAGMA max_page_count=2048") &&
      DatabaseExecute(db,"PRAGMA temp_store=MEMORY") &&
      DatabaseExecute(db,"PRAGMA busy_timeout=0");
   if(!ok)
     { reason="Limites da trilha tecnica nao confirmados"; JPWDiagClose(db,lock);
       db=INVALID_HANDLE; lock=INVALID_HANDLE; return(JPW_STORE_IO_ERROR); }
   return(JPW_STORE_VALID);
  }
bool JPWDiagBindEvent(const int q,JPWDiagEvent &e)
  {
   return(DatabaseBind(q,0,e.id) && DatabaseBind(q,1,e.context_key) &&
      DatabaseBind(q,2,e.component) && DatabaseBind(q,3,e.code) &&
      DatabaseBind(q,4,e.sample_id) && DatabaseBind(q,5,e.first_utc) &&
      DatabaseBind(q,6,e.last_utc) && DatabaseBind(q,7,e.mono_ms) &&
      DatabaseBind(q,8,e.repetitions) && DatabaseBind(q,9,e.product_version) &&
      DatabaseBind(q,10,e.calculation_version) && DatabaseBind(q,11,e.build_id) &&
      DatabaseBind(q,12,e.checksum));
  }
// Explicit times make the exact production path replayable with synthetic
// clocks. Runtime wrapper below supplies UTC computer time + monotonic time.
JPWStoreResult JPWDiagRecordAt(const string context,const int component,const int code,
                                const long sample_id,const long utc,const long mono,
                                string &reason,const string folder=JPW_DIAG_FOLDER)
  {
   reason="";
   if(!JPWRaizNIsHash(context) || !JPWDiagEventValid(component,code,sample_id,utc,mono))
     { reason="Evento tecnico invalido"; return(JPW_STORE_IO_ERROR); }
   int db=INVALID_HANDLE,lock=INVALID_HANDLE;
   JPWStoreResult status=JPWDiagOpen(folder,true,db,lock,reason);
   if(status!=JPW_STORE_VALID) return(status);
   bool ok=DatabaseTransactionBegin(db);
   // Only diagnostic events rotate. Free SQLite pages are reused; no VACUUM
   // or copying large files on a timer. Page count is a hard allocation cap.
   if(ok) ok=DatabaseExecute(db,"DELETE FROM diag_events WHERE last_utc<"+
                              IntegerToString(utc-JPW_DIAG_RETENTION_SECONDS));
   long count=0,max_id=0;
   if(ok) ok=JPWDiagScalar(db,"SELECT COUNT(*) FROM diag_events",count) &&
             JPWDiagScalar(db,"SELECT COALESCE(MAX(id),0) FROM diag_events",max_id);
   if(ok && count>=JPW_DIAG_MAX_ROWS)
      ok=DatabaseExecute(db,"DELETE FROM diag_events WHERE id IN (SELECT id FROM diag_events ORDER BY last_utc,id LIMIT 256)");
   if(ok && max_id>=LONG_MAX) ok=false;
   JPWDiagEvent e;
   e.id=(max_id<LONG_MAX ? max_id+1 : 0); e.context_key=context; e.component=component; e.code=code;
   e.sample_id=sample_id; e.first_utc=utc; e.last_utc=utc; e.mono_ms=mono;
   e.repetitions=1; e.product_version=JPW_PRODUCT_VERSION;
   e.calculation_version=JPW_CALCULATION_VERSION; e.build_id=JPW_BUILD_ID;
   bool update=false;
   int q=INVALID_HANDLE;
   if(ok) q=DatabasePrepare(db,"SELECT "+JPW_DIAG_SELECT+
      " FROM diag_events WHERE context_key=?1 AND component=?2 ORDER BY id DESC LIMIT 1");
   if(ok && q==INVALID_HANDLE) ok=false;
   if(ok) ok=DatabaseBind(q,0,context) && DatabaseBind(q,1,component);
   if(ok)
     {
      JPWDiagEvent previous;
      status=JPWDiagRead(q,previous);
      if(status!=JPW_STORE_VALID && status!=JPW_STORE_ABSENT) ok=false;
      if(ok && status==JPW_STORE_VALID &&
         JPWDiagCanCoalesce(component,code,context,utc,previous.component,previous.code,
                            previous.context_key,previous.last_utc) &&
         previous.build_id==JPW_BUILD_ID && previous.repetitions<LONG_MAX)
        { e.id=previous.id; e.first_utc=previous.first_utc;
          e.repetitions=previous.repetitions+1; update=true; }
     }
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(ok) ok=JPWDiagChecksum(e,e.checksum);
   q=INVALID_HANDLE;
   if(ok) q=DatabasePrepare(db,update ?
      "UPDATE diag_events SET context_key=?2,component=?3,code=?4,sample_id=?5,first_utc=?6,last_utc=?7,mono_ms=?8,repetitions=?9,product_version=?10,calculation_version=?11,build_id=?12,checksum=?13 WHERE id=?1" :
      "INSERT INTO diag_events VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13)");
   if(ok) ok=q!=INVALID_HANDLE && JPWDiagBindEvent(q,e) && JPWDiagExecute(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   // Read back the serialized row before committing; a failed append cannot
   // be described as durable merely because DatabaseBind succeeded.
   q=INVALID_HANDLE;
   if(ok) q=DatabasePrepare(db,"SELECT "+JPW_DIAG_SELECT+" FROM diag_events WHERE id=?1");
   if(ok)
     { JPWDiagEvent verified;
       ok=q!=INVALID_HANDLE && DatabaseBind(q,0,e.id) &&
          JPWDiagRead(q,verified)==JPW_STORE_VALID && verified.checksum==e.checksum; }
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) DatabaseTransactionRollback(db);
   JPWDiagClose(db,lock);
   if(!ok)
     { reason="Trilha tecnica nao gravada; calculos continuam independentes";
       return(status==JPW_STORE_CORRUPT ? status : JPW_STORE_IO_ERROR); }
   return(JPW_STORE_VALID);
  }
JPWStoreResult JPWDiagRecord(const string context,const int component,const int code,
                             const long sample_id,string &reason,
                             const string folder=JPW_DIAG_FOLDER)
  {
   return(JPWDiagRecordAt(context,component,code,sample_id,(long)TimeGMT(),
                          (long)GetTickCount64(),reason,folder));
  }
// Read latest technical rows for UI/export. All rows are checksum-validated;
// no SQL field containing account financial data exists in this namespace.
JPWStoreResult JPWDiagPreview(const string context,string &preview,string &reason,
                              const string folder=JPW_DIAG_FOLDER)
  {
   preview=""; reason="";
   if(!JPWRaizNIsHash(context))
     { reason="Contexto tecnico indisponivel"; return(JPW_STORE_IO_ERROR); }
   int db=INVALID_HANDLE,lock=INVALID_HANDLE;
   JPWStoreResult status=JPWDiagOpen(folder,false,db,lock,reason);
   if(status!=JPW_STORE_VALID) return(status);
   const int q=DatabasePrepare(db,"SELECT "+JPW_DIAG_SELECT+
      " FROM diag_events WHERE context_key=?1 AND last_utc>=?2 ORDER BY id DESC LIMIT 128");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,context) &&
      DatabaseBind(q,1,(long)TimeGMT()-JPW_DIAG_RETENTION_SECONDS);
   preview="JPW technical diagnostics / "+JPW_PRODUCT_VERSION+" / "+JPW_BUILD_ID+
      "\nUTC=computer; mono_ms=OS monotonic; retained events, not financial history.\n"+
      "Last 128 events at most; absence never proves full historical coverage.\n"+
      "context;component;code;sample;first_utc;last_utc;mono_ms;repeats;product;calculation;build\n";
   int rows=0;
   while(ok && rows<128)
     {
      JPWDiagEvent e;
      status=JPWDiagRead(q,e);
      if(status==JPW_STORE_ABSENT) break;
      if(status!=JPW_STORE_VALID) { ok=false; break; }
      preview+=e.context_key+";"+IntegerToString(e.component)+";"+JPWDiagCodeLabel(e.code)+";"+
         IntegerToString(e.sample_id)+";"+IntegerToString(e.first_utc)+";"+
         IntegerToString(e.last_utc)+";"+IntegerToString(e.mono_ms)+";"+
         IntegerToString(e.repetitions)+";"+e.product_version+";"+
         e.calculation_version+";"+e.build_id+"\n";
      rows++;
      if(StringLen(preview)>JPW_DIAG_EXPORT_LIMIT_BYTES) ok=false;
     }
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   JPWDiagClose(db,lock);
   if(!ok) { preview=""; reason="Eventos tecnicos invalidos ou ilegíveis";
             return(status==JPW_STORE_CORRUPT ? status : JPW_STORE_IO_ERROR); }
   if(rows==0) { reason="Nenhum evento tecnico retido para o contexto"; return(JPW_STORE_ABSENT); }
   return(JPW_STORE_VALID);
  }
JPWStoreResult JPWDiagSummary(const string context,string &summary,string &reason,
                              const string folder=JPW_DIAG_FOLDER)
  {
   summary="Cobertura historica: desconhecida. Nenhuma prova de atividade continua.";
   reason="";
   if(!JPWRaizNIsHash(context)) return(JPW_STORE_IO_ERROR);
   int db=INVALID_HANDLE,lock=INVALID_HANDLE;
   JPWStoreResult status=JPWDiagOpen(folder,false,db,lock,reason);
   if(status!=JPW_STORE_VALID) return(status);
   const int q=DatabasePrepare(db,"SELECT "+JPW_DIAG_SELECT+
      " FROM diag_events WHERE context_key=?1 AND code IN (4,5,6,14,15) AND last_utc>=?2 ORDER BY id DESC LIMIT 1");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,context) &&
      DatabaseBind(q,1,(long)TimeGMT()-JPW_DIAG_RETENTION_SECONDS);
   JPWDiagEvent gap;
   status=(ok ? JPWDiagRead(q,gap) : JPW_STORE_IO_ERROR);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   JPWDiagClose(db,lock);
   if(status!=JPW_STORE_VALID && status!=JPW_STORE_ABSENT)
     { reason="Lacuna tecnica invalida ou ilegivel"; return(status); }
   summary=(status==JPW_STORE_VALID ? "Cobertura historica: incompleta (lacuna registrada)." :
      "Cobertura historica: desconhecida; eventos retidos nao provam completude.");
   const string failure_prefix="JPW_DIAG_FAIL_"+StringSubstr(context,0,20)+"_";
   bool failed_writer=false;
   const int variable_count=GlobalVariablesTotal();
   for(int i=0;i<variable_count;i++)
      if(StringFind(GlobalVariableName(i),failure_prefix)==0)
        { failed_writer=true; break; }
   if(failed_writer)
      summary+="\nAtencao: uma instancia manteve falha de escrita ou de identidade do diagnostico nesta sessao.";
   summary+="\nTrilha tecnica: eventos essenciais, 30 dias, limite total inferior a 20 MiB.\n"+
      "Versao "+JPW_PRODUCT_VERSION+" | calculo "+JPW_CALCULATION_VERSION+" | "+JPW_BUILD_ID;
   return(JPW_STORE_VALID);
  }
// The exporter accepts the PREVIEWED snapshot only. It re-reads sanitized
// fields and refuses a changed preview, so no arbitrary text or financial
// payload can be smuggled through an export filename/text parameter.
JPWStoreResult JPWDiagExport(const string context,const string expected_preview,
                             string &path,string &reason,const string folder=JPW_DIAG_FOLDER)
  {
   path=""; string current="";
   JPWStoreResult status=JPWDiagPreview(context,current,reason,folder);
   if(status!=JPW_STORE_VALID) return(status);
   if(current!=expected_preview)
     { reason="Eventos mudaram; revise a previa antes de exportar"; return(JPW_STORE_BUSY); }
   uchar bytes[];
   const int copied=StringToCharArray(current,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(copied<1 || copied-1>JPW_DIAG_EXPORT_LIMIT_BYTES)
     { reason="Exportacao tecnica excede limite"; return(JPW_STORE_IO_ERROR); }
   int db=INVALID_HANDLE,lock=INVALID_HANDLE;
   status=JPWDiagOpen(folder,false,db,lock,reason);
   if(status!=JPW_STORE_VALID) return(status);
   const string target=folder+"diagnostics_export.txt";
   const int out=FileOpen(target,FILE_WRITE|FILE_BIN);
   bool ok=out!=INVALID_HANDLE;
   if(ok) { ok=FileWriteArray(out,bytes,0,copied-1)==(uint)(copied-1);
             FileFlush(out); FileClose(out); }
   // A flush call has no success return. Confirm bytes by independent reopen.
   if(ok)
     {
      const int verify=FileOpen(target,FILE_READ|FILE_BIN);
      ok=verify!=INVALID_HANDLE;
      if(ok)
        {
         const ulong size=FileSize(verify);
         uchar actual[];
         ok=size==(ulong)(copied-1) && ArrayResize(actual,copied-1)==copied-1 &&
            FileReadArray(verify,actual,0,copied-1)==(uint)(copied-1);
         for(int i=0;ok && i<copied-1;i++) if(actual[i]!=bytes[i]) ok=false;
         FileClose(verify);
        }
     }
   JPWDiagClose(db,lock);
   if(!ok) { reason="Exportacao tecnica nao confirmada"; return(JPW_STORE_IO_ERROR); }
   path=target; return(JPW_STORE_VALID);
  }
#endif

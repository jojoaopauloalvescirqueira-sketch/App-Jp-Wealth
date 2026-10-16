#ifndef JPW_PERSONAL_HISTORY_EXPORT_MQH
#define JPW_PERSONAL_HISTORY_EXPORT_MQH
#include <JPWealth/JPW_PersonalHistory_Store.mqh>
// Explicit local exports. Existing files are never silently replaced. Backup
// schema transports the immutable journal and reconstructs its projections.
#define JPW_PERSONAL_BACKUP_MAX_CHARS 33554432
bool JPWPersonalWriteText(const int file,const string value)
  {
   // FILE_TXT adds CR before an unpaired LF. Normalize explicitly so byte
   // counts match documented native behavior, independently of host shims.
   string wire=value; StringReplace(wire,"\r\n","\n"); StringReplace(wire,"\n","\r\n");
   uchar bytes[]; int count=StringToCharArray(wire,bytes,0,WHOLE_ARRAY,CP_UTF8)-1;
   return(count>=0 && FileWriteString(file,wire)==(uint)count);
  }
string JPWPersonalCSV(const string value)
  {
   string safe=value;
   if(StringLen(safe)>0)
     { ushort c=StringGetCharacter(safe,0); if(c=='=' || c=='+' || c=='-' || c=='@' || c==9 || c==10 || c==13) safe="'"+safe; }
   StringReplace(safe,"\"","\"\""); return("\""+safe+"\"");
  }
string JPWPersonalCSVRow(const string key,JPWPersonalRow &row)
  {
   string subject_kind="",subject_id="",ticket="",symbol="",state="",leverage="",quality="";
   if(row.category=="EPISODE")
     {
      JPWPersonalEpisode episode;
      if(JPWPersonalDecodeEpisode(row.payload,episode))
        {
         subject_kind=episode.subject.kind==1 ? "POSITION" : "PENDING";
         // Apostrophe is deliberate CSV text typing for spreadsheet readers;
         // the lossless canonical identifiers remain in the journal payload.
         subject_id="'"+episode.subject.id; ticket="'"+episode.subject.ticket; symbol=episode.subject.symbol;
         state=episode.state==1 ? "ACTIVE" : (episode.state==2 ? "RESOLVED_SL_PRESENT" : episode.resolution);
        }
     }
   if(row.category=="PEAK")
     { JPWPersonalPeak peak; if(JPWPersonalDecodePeak(row.payload,peak))
        { leverage=JPWPersonalNum(peak.leverage); quality=peak.quality==1 ? "Current" : "Estimated"; } }
   return(JPWPersonalCSV(key)+";"+JPWPersonalCSV(JPWPersonalInt(row.sequence))+";"+JPWPersonalCSV(row.category)+";"+
      JPWPersonalCSV(row.item_id)+";"+JPWPersonalCSV(JPWPersonalInt(row.wall))+";"+JPWPersonalCSV(subject_kind)+";"+
      JPWPersonalCSV(subject_id)+";"+JPWPersonalCSV(ticket)+";"+JPWPersonalCSV(symbol)+";"+JPWPersonalCSV(state)+";"+
      JPWPersonalCSV(leverage)+";"+JPWPersonalCSV(quality)+";"+JPWPersonalCSV(row.payload)+";"+JPWPersonalCSV(row.digest)+"\r\n");
  }
string JPWPersonalBackupRow(JPWPersonalRow &row)
  {
   return("{\"seq\":\""+JPWPersonalInt(row.sequence)+"\",\"category_hex\":\""+JPWPersonalHex(row.category)+
      "\",\"item_hex\":\""+JPWPersonalHex(row.item_id)+"\",\"wall\":\""+JPWPersonalInt(row.wall)+
      "\",\"payload_hex\":\""+JPWPersonalHex(row.payload)+"\",\"sha256\":\""+row.digest+"\"}");
  }
string JPWPersonalBackupHead(const string key,const long sequence,const long started,const long last)
  {
   return("{\n\"schema\":\"jpw-personal-history/v1\",\n\"account_key\":\""+key+
      "\",\n\"sequence\":\""+JPWPersonalInt(sequence)+"\",\n\"started_wall\":\""+JPWPersonalInt(started)+
      "\",\n\"last_wall\":\""+JPWPersonalInt(last)+"\",\n\"rows\":[\n");
  }
bool JPWPersonalBackupValue(const string line,const string name,string &value)
  {
   value=""; string marker="\""+name+"\":\"";
   int start=StringFind(line,marker); if(start<0) return(false); start+=StringLen(marker);
   int end=StringFind(line,"\"",start); if(end<start) return(false); value=StringSubstr(line,start,end-start); return(true);
  }
bool JPWPersonalBackupParse(const string json,string &key,long &started,long &last,JPWPersonalRow &rows[],string &reason)
  {
   ArrayResize(rows,0); key=""; started=0; last=0; reason="";
   if(StringLen(json)>JPW_PERSONAL_BACKUP_MAX_CHARS+512) { reason="Backup excede capacidade"; return(false); }
   string lines[]; int total=StringSplit(json,'\n',lines); if(total<11) { reason="Backup truncado"; return(false); }
   string sequence_text="",started_text="",last_text="",digest="";
   if(lines[0]!="{" || lines[1]!="\"schema\":\"jpw-personal-history/v1\"," ||
      !JPWPersonalBackupValue(lines[2],"account_key",key) || !JPWPersonalHashValid(key) ||
      !JPWPersonalBackupValue(lines[3],"sequence",sequence_text) || !JPWPersonalDigits(sequence_text) ||
      !JPWPersonalBackupValue(lines[4],"started_wall",started_text) || !JPWPersonalDigits(started_text) ||
      !JPWPersonalBackupValue(lines[5],"last_wall",last_text) || !JPWPersonalDigits(last_text) ||
      lines[6]!="\"rows\":[" || lines[total-3]!="]," || lines[total-1]!="}" ||
      !JPWPersonalBackupValue(lines[total-2],"sha256",digest) || !JPWPersonalHashValid(digest))
      { reason="Backup incompatível/malformado"; return(false); }
   long sequence=StringToInteger(sequence_text); started=StringToInteger(started_text); last=StringToInteger(last_text);
   if(sequence<0 || started<=0 || last<started || JPWPersonalInt(sequence)!=sequence_text ||
      JPWPersonalInt(started)!=started_text || JPWPersonalInt(last)!=last_text) { reason="Sequência/horário inválido"; return(false); }
   string body=JPWPersonalBackupHead(key,sequence,started,last); long count=0;
   for(int i=7;i<total-3;i++)
     {
      if(lines[i]=="" && sequence==0 && i==7) continue;
      JPWPersonalRow row; string seq="",wall="",category="",item="",payload="";
      bool ok=JPWPersonalBackupValue(lines[i],"seq",seq) && JPWPersonalDigits(seq) &&
         JPWPersonalBackupValue(lines[i],"category_hex",category) && JPWPersonalUnhex(category,row.category) &&
         JPWPersonalBackupValue(lines[i],"item_hex",item) && JPWPersonalUnhex(item,row.item_id) &&
         JPWPersonalBackupValue(lines[i],"wall",wall) && JPWPersonalDigits(wall) &&
         JPWPersonalBackupValue(lines[i],"payload_hex",payload) && JPWPersonalUnhex(payload,row.payload) &&
         JPWPersonalBackupValue(lines[i],"sha256",row.digest);
      row.sequence=StringToInteger(seq); row.wall=StringToInteger(wall); string actual="";
      string canonical=JPWPersonalBackupRow(row)+(i<total-4 ? "," : "");
      ok=ok && row.sequence==count+1 && JPWPersonalEnvelopeValid(row.category,row.item_id,row.wall,row.payload,key) &&
         JPWPersonalHash(row.payload,actual) && actual==row.digest && canonical==lines[i];
      if(!ok) { ArrayResize(rows,0); reason="Linha/sequência/checksum do backup recusada"; return(false); }
      int n=ArraySize(rows); if(ArrayResize(rows,n+1)!=n+1) { ArrayResize(rows,0); reason="Capacidade de recuperação"; return(false); }
      rows[n]=row; if(count>0) body+=",\n"; body+=JPWPersonalBackupRow(row); count++;
     }
   body+="\n]"; string actual="";
   if(count!=sequence || !JPWPersonalHash(body,actual) || actual!=digest || body+",\n\"sha256\":\""+digest+"\"\n}"!=json)
     { ArrayResize(rows,0); reason="Integridade global recusada"; return(false); }
   return(true);
  }
// Reconstruction is intentionally restricted to a new sandbox filename. It
// cannot target PersonalHistory/history_<account>.sqlite or an existing file.
bool JPWPersonalRestoreSandbox(const string json,const string sandbox_id,string &path,string &reason)
  {
   path=""; reason=""; string key=""; long started=0,last=0; JPWPersonalRow rows[];
   if(!JPWPersonalHashValid(sandbox_id) || !JPWPersonalBackupParse(json,key,started,last,rows,reason)) return(false);
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\Genetrix"); FolderCreate("JPWealth\\Genetrix\\PersonalHistorySandbox");
   path="JPWealth\\Genetrix\\PersonalHistorySandbox\\restored_"+sandbox_id+".sqlite";
   if(FileIsExist(path)) { path=""; reason="Sandbox existente preservado"; return(false); }
   int db=DatabaseOpen(path,DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE);
   if(db==INVALID_HANDLE) { path=""; reason="Sandbox indisponível"; return(false); }
   bool ok=JPWPersonalSchemaCreate(db,key,started) && DatabaseTransactionBegin(db);
   long seq=0;
   for(int i=0;ok && i<ArraySize(rows);i++)
     {
      JPWPersonalRow row=rows[i];
      ok=JPWPersonalAppend(db,row.category,row.item_id,row.wall,row.payload,seq) && seq==row.sequence;
      if(!ok) break;
      if(row.category=="EPISODE")
        {
         JPWPersonalEpisode episode; ok=JPWPersonalDecodeEpisode(row.payload,episode) && episode.account_key==key && episode.episode_id==row.item_id;
         int q=DatabasePrepare(db,"INSERT OR REPLACE INTO ph_episodes VALUES(?1,?2,?3,?4,?5)");
         ok=ok && q!=INVALID_HANDLE && DatabaseBind(q,0,row.item_id) && DatabaseBind(q,1,episode.state) && DatabaseBind(q,2,row.sequence) &&
            DatabaseBind(q,3,row.payload) && DatabaseBind(q,4,row.digest) && JPWPersonalDone(q);
         if(q!=INVALID_HANDLE) DatabaseFinalize(q);
        }
      if(row.category=="PEAK")
        {
         JPWPersonalPeak peak; ok=JPWPersonalDecodePeak(row.payload,peak) && peak.account_key==key && JPWPersonalInt(peak.quality)==row.item_id;
         int q=DatabasePrepare(db,"INSERT OR REPLACE INTO ph_peaks VALUES(?1,?2,?3,?4)");
         ok=ok && q!=INVALID_HANDLE && DatabaseBind(q,0,peak.quality) && DatabaseBind(q,1,row.sequence) && DatabaseBind(q,2,row.payload) && DatabaseBind(q,3,row.digest) && JPWPersonalDone(q);
         if(q!=INVALID_HANDLE) DatabaseFinalize(q);
        }
     }
   int q=DatabasePrepare(db,"UPDATE ph_meta SET last_wall=?1 WHERE id=1");
   ok=ok && q!=INVALID_HANDLE && DatabaseBind(q,0,last) && JPWPersonalDone(q); if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   JPWPersonalStoreContext audited; audited.db=db; audited.account_key=key; audited.transaction_active=ok;
   if(ok) ok=JPWPersonalAuditBegin(audited);
   while(ok && !audited.audit_complete)
     { JPWStoreResult result=JPWPersonalAuditStep(audited,GetTickCount64(),JPW_PERSONAL_SLICE_MS,JPW_PERSONAL_SLICE_ROWS);
       if(result!=JPW_STORE_BUSY && result!=JPW_STORE_VALID) { reason=audited.reason; ok=false; } }
   // This standalone synchronous helper drives the same complete phases. It is
   // deliberately outside the runtime timer; SQL/global parse is indivisible.
   if(audited.db==INVALID_HANDLE) { db=INVALID_HANDLE; ok=false; }
   if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) { if(db!=INVALID_HANDLE) DatabaseTransactionRollback(db); if(reason=="") reason="Reconstrução não confirmada; sandbox preservado para diagnóstico"; }
   if(db!=INVALID_HANDLE) DatabaseClose(db); audited.db=INVALID_HANDLE; return(ok);
  }
enum JPWPersonalExportPhase { JPW_PH_EXPORT_IDLE=0,JPW_PH_EXPORT_AUDIT,JPW_PH_EXPORT_ROWS,JPW_PH_EXPORT_FINISH,JPW_PH_EXPORT_VERIFY,JPW_PH_EXPORT_READY,JPW_PH_EXPORT_FAILED };
struct JPWPersonalExportJob
  {
   JPWPersonalStoreContext ctx; JPWPersonalExportPhase phase; JPWStoreResult result;
   bool active,backup; string account_key,path,reason,body,json,saved; int query,file; long count;
   JPWPersonalExportJob() { active=false; backup=false; phase=JPW_PH_EXPORT_IDLE; result=JPW_STORE_ABSENT; query=INVALID_HANDLE; file=INVALID_HANDLE; count=0; }
  };
void JPWPersonalExportCancel(JPWPersonalExportJob &job)
  {
   if(job.query!=INVALID_HANDLE) DatabaseFinalize(job.query); job.query=INVALID_HANDLE;
   if(job.file!=INVALID_HANDLE) FileClose(job.file); job.file=INVALID_HANDLE;
   JPWPersonalOpenCancel(job.ctx); job.active=false; job.phase=JPW_PH_EXPORT_IDLE;
   job.body=""; job.json=""; job.saved="";
   job.result=JPW_STORE_BUSY; job.reason="Exportação cancelada; eventual arquivo parcial preservado sem confirmação";
  }
JPWStoreResult JPWPersonalExportFail(JPWPersonalExportJob &job,const JPWStoreResult result,const string reason)
  { JPWPersonalExportCancel(job); job.phase=JPW_PH_EXPORT_FAILED; job.result=result; job.reason=reason; return(result); }
JPWStoreResult JPWPersonalExportBegin(const string key,const bool backup,JPWPersonalExportJob &job)
  {
   if(job.active || job.ctx.db!=INVALID_HANDLE || job.query!=INVALID_HANDLE || job.file!=INVALID_HANDLE) return(JPW_STORE_INCOMPATIBLE);
   job.account_key=key; job.backup=backup; job.count=0; job.body=""; job.json=""; job.saved=""; job.reason="";
   string suffix=JPWPersonalInt((long)TimeGMT())+"_"+JPWPersonalInt((long)GetTickCount64());
   job.path=JPW_PERSONAL_FOLDER+"Exports\\"+(backup ? "backup_" : "history_")+key+"_"+suffix+(backup ? ".json" : ".csv");
   JPWStoreResult opened=JPWPersonalOpenBegin(key,false,"",0,0,job.ctx);
   if(opened!=JPW_STORE_BUSY) return(JPWPersonalExportFail(job,opened,job.ctx.reason));
   job.active=true; job.phase=JPW_PH_EXPORT_AUDIT; job.result=JPW_STORE_BUSY; job.reason="Auditoria integral antes da exportação"; return(job.result);
  }
bool JPWPersonalExportCreateFile(JPWPersonalExportJob &job)
  {
   FolderCreate("JPWealth\\Genetrix\\PersonalHistory\\Exports");
   if(FileIsExist(job.path)) { job.reason="Destino existente preservado; tente outra captura"; return(false); }
   job.file=FileOpen(job.path,FILE_WRITE|FILE_TXT|FILE_ANSI,0,CP_UTF8);
   if(job.file==INVALID_HANDLE) { job.reason="Arquivo de exportação indisponível"; return(false); } return(true);
  }
JPWStoreResult JPWPersonalExportStep(JPWPersonalExportJob &job,const ulong started,const int budget_ms,const int max_rows)
  {
   if(!job.active || max_rows<1 || budget_ms<1) return(job.result);
   ulong now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
   if(job.phase==JPW_PH_EXPORT_AUDIT)
     {
      JPWStoreResult audit=JPWPersonalOpenStep(job.ctx,started,budget_ms,max_rows,0,0);
      if(audit==JPW_STORE_BUSY && JPWPersonalPreparing(job.ctx)) return(audit);
      if(audit!=JPW_STORE_VALID) return(JPWPersonalExportFail(job,audit,job.ctx.reason));
      job.phase=JPW_PH_EXPORT_ROWS;
      // Consume rows on a later slice: the same snapshot remains retained.
      return(JPW_STORE_BUSY);
     }
   if(job.phase==JPW_PH_EXPORT_ROWS && job.query==INVALID_HANDLE)
     {
      if(job.backup) job.body=JPWPersonalBackupHead(job.account_key,job.ctx.snapshot_sequence,job.ctx.started_wall,job.ctx.last_wall);
      else
        {
         if(!JPWPersonalExportCreateFile(job)) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,job.reason));
         if(!JPWPersonalWriteText(job.file,"account_key;sequence;category;item_id;observed_utc_seconds;subject_kind;subject_id_text;ticket_text;symbol;state;leverage;quality;payload;sha256\r\n"))
            return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Exportação incompleta; header não confirmado, parcial preservado"));
        }
      job.query=DatabasePrepare(job.ctx.db,"SELECT sequence,category,item_id,wall,payload,digest,(typeof(sequence)='integer' AND typeof(category)='text' AND typeof(item_id)='text' AND typeof(wall)='integer' AND typeof(payload)='text' AND typeof(digest)='text') FROM ph_rows ORDER BY sequence");
      if(job.query==INVALID_HANDLE) return(JPWPersonalExportFail(job,JPWPersonalErrorResult(GetLastError()),"Cursor de exportação indisponível; parcial preservado"));
     }
   int units=0;
   while(job.phase==JPW_PH_EXPORT_ROWS && units<max_rows)
     {
      now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
      ResetLastError(); bool row_present=DatabaseRead(job.query); int error=GetLastError(); units++;
      if(!row_present)
        {
         if(error!=ERR_DATABASE_NO_MORE_DATA || job.count!=job.ctx.snapshot_sequence)
            return(JPWPersonalExportFail(job,error==ERR_DATABASE_NO_MORE_DATA ? JPW_STORE_CORRUPT : JPWPersonalErrorResult(error),"Exportação incompleta; EOF/contagem não confirmados, parcial preservado"));
         DatabaseFinalize(job.query); job.query=INVALID_HANDLE; job.phase=JPW_PH_EXPORT_FINISH; break;
        }
      JPWPersonalRow row; int typed=0;
      if(!JPWPersonalReadRow(job.query,row,job.account_key) || !DatabaseColumnInteger(job.query,6,typed) || typed!=1 || row.sequence!=job.count+1)
         return(JPWPersonalExportFail(job,JPW_STORE_CORRUPT,"Exportação recusada por linha/tipo/sequência; parcial preservado"));
      if(job.backup)
        {
         if(job.count>0) job.body+=",\n"; job.body+=JPWPersonalBackupRow(row);
         if(StringLen(job.body)>JPW_PERSONAL_BACKUP_MAX_CHARS)
            return(JPWPersonalExportFail(job,JPW_STORE_INCOMPATIBLE,"Capacidade JSON excedida (MAX_CHARS do corpo canônico); dados preservados e CSV integral disponível"));
        }
      else if(!JPWPersonalWriteText(job.file,JPWPersonalCSVRow(job.account_key,row)))
         return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Exportação incompleta; linha não confirmada, parcial preservado"));
      job.count++;
     }
   now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
   if(job.phase==JPW_PH_EXPORT_FINISH)
     {
      if(job.backup)
        {
         job.body+="\n]";
         if(StringLen(job.body)>JPW_PERSONAL_BACKUP_MAX_CHARS) return(JPWPersonalExportFail(job,JPW_STORE_INCOMPATIBLE,"Capacidade JSON excedida (MAX_CHARS do corpo canônico); CSV integral disponível"));
         string digest=""; if(!JPWPersonalHash(job.body,digest)) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Checksum global não confirmado"));
         job.json=job.body+",\n\"sha256\":\""+digest+"\"\n}";
         if(!JPWPersonalExportCreateFile(job)) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,job.reason));
         if(!JPWPersonalWriteText(job.file,job.json)) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Backup escrito parcialmente, sem confirmação"));
        }
      ResetLastError(); FileFlush(job.file); int error=GetLastError(); FileClose(job.file); job.file=INVALID_HANDLE;
      if(error!=0) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Flush da exportação não confirmado; parcial preservado"));
      if(!JPWPersonalReadFinish(job.ctx,true)) return(JPWPersonalExportFail(job,job.ctx.result,job.ctx.reason));
      JPWPersonalOpenCancel(job.ctx);
      if(job.backup)
        {
         job.file=FileOpen(job.path,FILE_READ|FILE_TXT|FILE_ANSI,0,CP_UTF8);
         if(job.file==INVALID_HANDLE) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Backup escrito sem releitura confirmada"));
         job.phase=JPW_PH_EXPORT_VERIFY; return(JPW_STORE_BUSY);
        }
      job.phase=JPW_PH_EXPORT_READY; job.result=JPW_STORE_VALID; job.active=false; job.reason=""; return(job.result);
     }
   units=0;
   while(job.phase==JPW_PH_EXPORT_VERIFY && units<max_rows)
     {
      now=GetTickCount64(); if(now<started || now-started>=(ulong)budget_ms) return(JPW_STORE_BUSY);
      ResetLastError(); bool end=FileIsEnding(job.file);
      if(GetLastError()!=0) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Releitura do backup interrompida"));
      if(end)
        {
         FileClose(job.file); job.file=INVALID_HANDLE; string key="",reason=""; long first=0,last=0; JPWPersonalRow rows[];
         if(job.saved!=job.json || !JPWPersonalBackupParse(job.saved,key,first,last,rows,reason) || key!=job.account_key || ArraySize(rows)!=job.count)
            return(JPWPersonalExportFail(job,JPW_STORE_CORRUPT,"Releitura/verificação global do backup recusada"));
         job.phase=JPW_PH_EXPORT_READY; job.result=JPW_STORE_VALID; job.active=false; job.reason=""; job.saved=""; job.body=""; return(job.result);
        }
      string line=FileReadString(job.file); if(GetLastError()!=0) return(JPWPersonalExportFail(job,JPW_STORE_IO_ERROR,"Releitura do backup interrompida"));
      if(job.saved!="") job.saved+="\n"; job.saved+=line; units++;
     }
   return(JPW_STORE_BUSY);
  }

#endif

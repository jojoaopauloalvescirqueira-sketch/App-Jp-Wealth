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
bool JPWPersonalBackupBuild(const string key,string &json,string &reason)
  {
   json=""; reason=""; JPWPersonalStoreContext ctx;
   if(!JPWPersonalOpen(key,false,"",0,0,ctx)) { reason=ctx.reason; return(false); }
   bool valid=JPWPersonalIntegrity(ctx.db,reason);
   int q=DatabasePrepare(ctx.db,"SELECT sequence,started_wall,last_wall FROM ph_meta WHERE id=1");
   long sequence=0,started=0,last=0;
   bool ok=valid && q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnLong(q,0,sequence) && DatabaseColumnLong(q,1,started) && DatabaseColumnLong(q,2,last) && started>0 && last>=started;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   string body=JPWPersonalBackupHead(key,sequence,started,last); long count=0;
   q=DatabasePrepare(ctx.db,"SELECT sequence,category,item_id,wall,payload,digest FROM ph_rows ORDER BY sequence");
   ok=ok && q!=INVALID_HANDLE; ResetLastError();
   if(q!=INVALID_HANDLE) while(ok && DatabaseRead(q))
     {
      JPWPersonalRow row; ok=JPWPersonalReadRow(q,row,key) && row.sequence==count+1;
      if(!ok) break;
      if(count>0) body+=",\n"; body+=JPWPersonalBackupRow(row); count++;
      if(StringLen(body)>JPW_PERSONAL_BACKUP_MAX_CHARS) { reason="Backup excede capacidade desta exportação; dados preservados"; ok=false; break; }
      ResetLastError();
     }
   if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA && count==sequence;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   body+="\n]"; string digest=""; if(ok) ok=JPWPersonalHash(body,digest);
   ok=JPWPersonalReadFinish(ctx,ok);
   JPWPersonalClose(ctx,0,0);
   if(ok) json=body+",\n\"sha256\":\""+digest+"\"\n}";
   else if(reason=="") reason="Backup não confirmado; integridade/seq recusada";
   return(ok);
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
   if(ok) ok=JPWPersonalIntegrity(db,reason);
   if(ok) ok=JPWPersonalAuditRows(db,reason)==JPW_STORE_VALID; if(ok) ok=DatabaseTransactionCommit(db);
   if(!ok) { DatabaseTransactionRollback(db); if(reason=="") reason="Reconstrução não confirmada; sandbox preservado para diagnóstico"; }
   DatabaseClose(db); return(ok);
  }
bool JPWPersonalExport(const string key,const bool backup,string &path,string &reason)
  {
   path=""; reason=""; if(!JPWPersonalHashValid(key)) { reason="Identidade inválida"; return(false); }
   string suffix=JPWPersonalInt((long)TimeGMT())+"_"+JPWPersonalInt((long)GetTickCount64());
   FolderCreate("JPWealth\\Genetrix\\PersonalHistory\\Exports");
   path=JPW_PERSONAL_FOLDER+"Exports\\"+(backup ? "backup_" : "history_")+key+"_"+suffix+(backup ? ".json" : ".csv");
   if(FileIsExist(path)) { path=""; reason="Destino existente preservado; tente outra captura"; return(false); }
   string json=""; if(backup && !JPWPersonalBackupBuild(key,json,reason)) { path=""; return(false); }
   int file=FileOpen(path,FILE_WRITE|FILE_TXT|FILE_ANSI,0,CP_UTF8);
   if(file==INVALID_HANDLE) { reason="Arquivo de exportação indisponível"; return(false); }
   bool ok=true;
   if(backup) ok=JPWPersonalWriteText(file,json);
   else
     {
      JPWPersonalStoreContext ctx;
      ok=JPWPersonalOpen(key,false,"",0,0,ctx);
      string header="account_key;sequence;category;item_id;observed_utc_seconds;subject_kind;subject_id_text;ticket_text;symbol;state;leverage;quality;payload;sha256\r\n";
      if(ok) ok=JPWPersonalWriteText(file,header);
      int q=ok ? DatabasePrepare(ctx.db,"SELECT sequence,category,item_id,wall,payload,digest FROM ph_rows ORDER BY sequence") : INVALID_HANDLE;
      ok=ok && q!=INVALID_HANDLE; ResetLastError();
      if(q!=INVALID_HANDLE) while(ok && DatabaseRead(q))
        {
         JPWPersonalRow row; ok=JPWPersonalReadRow(q,row,key); if(!ok) break;
         string line=JPWPersonalCSVRow(key,row);
         ok=JPWPersonalWriteText(file,line); ResetLastError();
        }
      if(ok) ok=GetLastError()==ERR_DATABASE_NO_MORE_DATA;
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(ctx.db!=INVALID_HANDLE) { ok=JPWPersonalReadFinish(ctx,ok); JPWPersonalClose(ctx,0,0); }
     }
   ResetLastError(); FileFlush(file); if(GetLastError()!=0) ok=false; FileClose(file);
   if(!ok) { reason="Exportação incompleta; arquivo parcial preservado, sem confirmação de backup"; return(false); }
   if(backup)
     {
      int checked=FileOpen(path,FILE_READ|FILE_TXT|FILE_ANSI,0,CP_UTF8); string saved="";
      if(checked==INVALID_HANDLE) { reason="Exportação escrita sem releitura confirmada"; return(false); }
      while(!FileIsEnding(checked)) { string line=FileReadString(checked); if(saved!="") saved+="\n"; saved+=line; }
      FileClose(checked); string parsed_key=""; long started=0,last=0; JPWPersonalRow rows[];
      if(saved!=json || !JPWPersonalBackupParse(saved,parsed_key,started,last,rows,reason) || parsed_key!=key)
         { reason="Releitura/verificação do backup recusada"; return(false); }
     }
   return(true);
  }
#endif

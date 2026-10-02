#ifndef JPW_NOCUDA_FIBO_STORE_MQH
#define JPW_NOCUDA_FIBO_STORE_MQH
#include <JPWealth/JPW_NoCuda_Fibo_Core.mqh>
#define JPW_NCF_STORE_SCHEMA 2
// Exclusive database. Never opens manual NoCuda or any financial record.
struct JPWNCFHead
  { string study_id; int generation,revision; bool paused; string checksum; };
struct JPWNCFRevisionRow
  { string study_id; int revision,previous_revision; string payload,justification; long confirmed_utc; string checksum; };
struct JPWNCFMetaRow { int schema_version; string store_key; };
struct JPWNCFHeadRow { string study_id; int generation,revision,paused; string checksum; };
struct JPWNCFNoteRow
  { int note_version; string note_id,study_id; int revision,generation;
    string kind,payload; long observed_utc; string checksum; };
// Metadata index: no payload or opening sequence is read by CatalogPage.
// linked_checksum is a query-only join result, excluded from its own digest.
struct JPWNCFCatalogRow
  {
   string kind,entry_id,study_id,symbol,source_name;
   int source_tf,revision,generation,paused;
   long captured_utc,confirmed_utc;
   string label,record_checksum,checksum,linked_checksum;
  };
void JPWNCFHeadClear(JPWNCFHead &h)
  { h.study_id=""; h.generation=0; h.revision=0; h.paused=true; h.checksum=""; }
bool JPWNCFHash(const string text,string &hex)
  {
   hex=""; uchar source[],key[],digest[];
   int count=StringToCharArray(text,source,0,WHOLE_ARRAY,CP_UTF8);
   if(count<1 || ArrayResize(source,count-1)!=count-1 ||
      CryptEncode(CRYPT_HASH_SHA256,source,key,digest)!=32) return(false);
   for(int i=0;i<32;i++) hex+=StringFormat("%02x",(int)digest[i]);
   return(StringLen(hex)==64);
  }
bool JPWNCFIsHash(const string value)
  {
   if(StringLen(value)!=64) return(false);
   for(int i=0;i<64;i++)
     { ushort c=StringGetCharacter(value,i); if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return(false); }
   return(true);
  }
bool JPWNCFStoreKey(const string installation,const string feed,string &key)
  {
   key=""; if(installation=="" || feed=="") return(false);
   return(JPWNCFHash(JPWNCFFrame("nocuda_fibonacci_store_v1")+JPWNCFFrame(installation)+JPWNCFFrame(feed),key));
  }
bool JPWNCFNewStudyId(const string key,const string symbol,const long utc,const long nonce,string &id)
  {
   id=""; if(!JPWNCFIsHash(key) || symbol=="" || utc<=0 || nonce<=0) return(false);
   return(JPWNCFHash(JPWNCFFrame(key)+JPWNCFFrame(symbol)+JPWNCFFrame(IntegerToString(utc))+
                    JPWNCFFrame(IntegerToString(nonce))+JPWNCFFrame("fibo_study_v1"),id));
  }
string JPWNCFStorePath(const string key)
  { return(JPWNCFIsHash(key) ? "JPWealth\\NoCuda\\Fibonacci\\fibo_"+key+".sqlite" : ""); }
JPWNCFStatus JPWNCFDatabaseError(const int error)
  {
   if(error==ERR_DATABASE_BUSY || error==ERR_DATABASE_LOCKED) return(JPW_NCF_BUSY);
   if(error==ERR_DATABASE_CORRUPT || error==ERR_DATABASE_NOTADB) return(JPW_NCF_CORRUPT);
   return(JPW_NCF_IO_ERROR);
  }
bool JPWNCFExecutePrepared(const int q)
  {
   if(q==INVALID_HANDLE) return(false);
   ResetLastError(); DatabaseRead(q); return(GetLastError()==ERR_DATABASE_NO_MORE_DATA);
  }
bool JPWNCFStoreInit(const int db,const string key)
  {
   if(!DatabaseExecute(db,"BEGIN IMMEDIATE")) return(false);
   bool ok=DatabaseExecute(db,"CREATE TABLE fibo_meta(schema_version INTEGER NOT NULL,store_key TEXT PRIMARY KEY)") &&
      DatabaseExecute(db,"CREATE TABLE fibo_heads(study_id TEXT PRIMARY KEY,generation INTEGER NOT NULL CHECK(generation>0),revision INTEGER NOT NULL CHECK(revision>0),paused INTEGER NOT NULL CHECK(paused IN(0,1)),checksum TEXT NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE fibo_revisions(study_id TEXT NOT NULL,revision INTEGER NOT NULL,previous_revision INTEGER NOT NULL,payload TEXT NOT NULL,justification TEXT NOT NULL,confirmed_utc INTEGER NOT NULL,checksum TEXT NOT NULL,PRIMARY KEY(study_id,revision))") &&
      DatabaseExecute(db,"CREATE TABLE fibo_notes(note_version INTEGER NOT NULL,note_id TEXT PRIMARY KEY,study_id TEXT NOT NULL,revision INTEGER NOT NULL,generation INTEGER NOT NULL,kind TEXT NOT NULL CHECK(kind IN('observation','projection')),payload TEXT NOT NULL,observed_utc INTEGER NOT NULL,checksum TEXT NOT NULL)") &&
      DatabaseExecute(db,"CREATE TABLE fibo_catalog(kind TEXT NOT NULL CHECK(kind IN('study','revision','observation')),entry_id TEXT NOT NULL,study_id TEXT NOT NULL,symbol TEXT NOT NULL,source_name TEXT NOT NULL,source_tf INTEGER NOT NULL,revision INTEGER NOT NULL,generation INTEGER NOT NULL,paused INTEGER NOT NULL,captured_utc INTEGER NOT NULL,confirmed_utc INTEGER NOT NULL,label TEXT NOT NULL,record_checksum TEXT NOT NULL,checksum TEXT NOT NULL,PRIMARY KEY(kind,entry_id))") &&
      DatabaseExecute(db,"CREATE INDEX fibo_catalog_studies ON fibo_catalog(kind,symbol,confirmed_utc DESC,revision DESC,entry_id)") &&
      DatabaseExecute(db,"CREATE INDEX fibo_catalog_records ON fibo_catalog(study_id,confirmed_utc DESC,revision DESC,entry_id)") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_catalog_no_update BEFORE UPDATE ON fibo_catalog WHEN OLD.kind<>'study' BEGIN SELECT RAISE(ABORT,'immutable catalog record'); END") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_catalog_no_delete BEFORE DELETE ON fibo_catalog BEGIN SELECT RAISE(ABORT,'catalog record retained'); END") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_revision_no_update BEFORE UPDATE ON fibo_revisions BEGIN SELECT RAISE(ABORT,'immutable revision'); END") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_revision_no_delete BEFORE DELETE ON fibo_revisions BEGIN SELECT RAISE(ABORT,'immutable revision'); END") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_note_no_update BEFORE UPDATE ON fibo_notes BEGIN SELECT RAISE(ABORT,'immutable note'); END") &&
      DatabaseExecute(db,"CREATE TRIGGER fibo_note_no_delete BEFORE DELETE ON fibo_notes BEGIN SELECT RAISE(ABORT,'immutable note'); END");
   if(ok)
     {
      int q=DatabasePrepare(db,"INSERT INTO fibo_meta VALUES(?1,?2)");
      ok=q!=INVALID_HANDLE && DatabaseBind(q,0,JPW_NCF_STORE_SCHEMA) && DatabaseBind(q,1,key) && JPWNCFExecutePrepared(q);
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
     }
   if(ok && DatabaseExecute(db,"COMMIT")) return(true);
   DatabaseExecute(db,"ROLLBACK"); return(false);
  }
JPWNCFStatus JPWNCFStoreOpen(const string key,const bool write,int &db,string &reason)
  {
   db=INVALID_HANDLE; reason=""; string path=JPWNCFStorePath(key);
   if(path=="") { reason="Chave local invalida"; return(JPW_NCF_INVALID); }
   bool existed=FileIsExist(path);
   if(!write && !existed) { reason="Nenhum estudo Fibonacci salvo"; return(JPW_NCF_ABSENT); }
   if(write) { FolderCreate("JPWealth"); FolderCreate("JPWealth\\NoCuda"); FolderCreate("JPWealth\\NoCuda\\Fibonacci"); }
   ResetLastError();
   db=DatabaseOpen(path,write ? DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE : DATABASE_OPEN_READONLY);
   if(db==INVALID_HANDLE) { reason="Banco Fibonacci indisponivel"; return(JPWNCFDatabaseError(GetLastError())); }
   if(!DatabaseExecute(db,"PRAGMA busy_timeout=0"))
     { JPWNCFStatus failure=JPWNCFDatabaseError(GetLastError()); DatabaseClose(db); db=INVALID_HANDLE; return(failure); }
   if(!existed && write && !JPWNCFStoreInit(db,key))
     { JPWNCFStatus failure=JPWNCFDatabaseError(GetLastError()); DatabaseClose(db); db=INVALID_HANDLE; reason="Criacao nao confirmada"; return(failure); }
   JPWNCFStatus status=JPW_NCF_VALID;
   if(!DatabaseTableExists(db,"fibo_meta")) status=JPW_NCF_CORRUPT;
   if(status==JPW_NCF_VALID)
     {
      int q=DatabasePrepare(db,"SELECT schema_version,store_key FROM fibo_meta LIMIT 2");
      JPWNCFMetaRow meta,extra; bool ok=q!=INVALID_HANDLE && DatabaseReadBind(q,meta);
      if(ok)
        { ResetLastError(); ok=!DatabaseReadBind(q,extra) && GetLastError()==ERR_DATABASE_NO_MORE_DATA; }
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(!ok) status=JPW_NCF_CORRUPT;
      else if(meta.schema_version!=JPW_NCF_STORE_SCHEMA || meta.store_key!=key) status=JPW_NCF_INCOMPATIBLE;
     }
   if(status==JPW_NCF_VALID && (!DatabaseTableExists(db,"fibo_heads") ||
      !DatabaseTableExists(db,"fibo_revisions") || !DatabaseTableExists(db,"fibo_notes") ||
      !DatabaseTableExists(db,"fibo_catalog"))) status=JPW_NCF_CORRUPT;
   if(status==JPW_NCF_VALID)
     {
      int q=DatabasePrepare(db,"SELECT COUNT(*) FROM sqlite_master WHERE type='trigger' AND name IN('fibo_revision_no_update','fibo_revision_no_delete','fibo_note_no_update','fibo_note_no_delete','fibo_catalog_no_update','fibo_catalog_no_delete')");
      int count=0; bool ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,count) && count==6;
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
      if(!ok) status=JPW_NCF_CORRUPT;
     }
   if(status!=JPW_NCF_VALID)
     { DatabaseClose(db); db=INVALID_HANDLE; reason="Banco Fibonacci corrompido ou incompativel; nao reinicializado"; }
   return(status);
  }
bool JPWNCFCatalogHash(const string key,const JPWNCFCatalogRow &r,string &hash)
  {
   if((r.kind!="study" && r.kind!="revision" && r.kind!="observation") ||
      r.entry_id=="" || StringLen(r.entry_id)>160 || !JPWNCFIsHash(r.study_id) ||
      r.symbol=="" || StringLen(r.symbol)>128 || StringLen(r.source_name)>256 ||
      r.source_tf<=0 || r.revision<1 || r.generation<1 || (r.paused!=0 && r.paused!=1) ||
      r.captured_utc<=0 || r.confirmed_utc<=0 || StringLen(r.label)>256 || !JPWNCFIsHash(r.record_checksum)) return(false);
   return(JPWNCFHash(JPWNCFFrame("fibo_catalog_v1")+JPWNCFFrame(key)+JPWNCFFrame(r.kind)+
      JPWNCFFrame(r.entry_id)+JPWNCFFrame(r.study_id)+JPWNCFFrame(r.symbol)+JPWNCFFrame(r.source_name)+
      JPWNCFFrame(IntegerToString(r.source_tf))+JPWNCFFrame(IntegerToString(r.revision))+
      JPWNCFFrame(IntegerToString(r.generation))+JPWNCFFrame(IntegerToString(r.paused))+
      JPWNCFFrame(IntegerToString(r.captured_utc))+JPWNCFFrame(IntegerToString(r.confirmed_utc))+
      JPWNCFFrame(r.label)+JPWNCFFrame(r.record_checksum),hash));
  }
bool JPWNCFWriteCatalog(const int db,const string key,JPWNCFCatalogRow &r)
  {
   if(!JPWNCFCatalogHash(key,r,r.checksum)) return(false);
   int q=DatabasePrepare(db,"SELECT kind,entry_id,study_id,symbol,source_name,source_tf,revision,generation,paused,captured_utc,confirmed_utc,label,record_checksum,checksum,'' FROM fibo_catalog WHERE kind=?1 AND entry_id=?2");
   bool bound=q!=INVALID_HANDLE && DatabaseBind(q,0,r.kind) && DatabaseBind(q,1,r.entry_id);
   JPWNCFCatalogRow prior; ResetLastError(); bool exists=bound && DatabaseReadBind(q,prior); int error=GetLastError();
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!bound || (!exists && error!=ERR_DATABASE_NO_MORE_DATA)) return(false);
   if(exists)
     {
      string hash="";
      if(!JPWNCFCatalogHash(key,prior,hash) || hash!=prior.checksum) return(false);
      if(r.kind!="study") return(prior.checksum==r.checksum);
     }
   q=DatabasePrepare(db,exists ?
      "UPDATE fibo_catalog SET study_id=?3,symbol=?4,source_name=?5,source_tf=?6,revision=?7,generation=?8,paused=?9,captured_utc=?10,confirmed_utc=?11,label=?12,record_checksum=?13,checksum=?14 WHERE kind=?1 AND entry_id=?2" :
      "INSERT INTO fibo_catalog(kind,entry_id,study_id,symbol,source_name,source_tf,revision,generation,paused,captured_utc,confirmed_utc,label,record_checksum,checksum) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14)");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,r.kind) && DatabaseBind(q,1,r.entry_id) &&
      DatabaseBind(q,2,r.study_id) && DatabaseBind(q,3,r.symbol) && DatabaseBind(q,4,r.source_name) &&
      DatabaseBind(q,5,r.source_tf) && DatabaseBind(q,6,r.revision) && DatabaseBind(q,7,r.generation) &&
      DatabaseBind(q,8,r.paused) && DatabaseBind(q,9,r.captured_utc) && DatabaseBind(q,10,r.confirmed_utc) &&
      DatabaseBind(q,11,r.label) && DatabaseBind(q,12,r.record_checksum) && DatabaseBind(q,13,r.checksum) && JPWNCFExecutePrepared(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) return(false);
   q=DatabasePrepare(db,"SELECT checksum FROM fibo_catalog WHERE kind=?1 AND entry_id=?2");
   string stored="";
   ok=q!=INVALID_HANDLE && DatabaseBind(q,0,r.kind) && DatabaseBind(q,1,r.entry_id) &&
      DatabaseRead(q) && DatabaseColumnText(q,0,stored) && stored==r.checksum;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
void JPWNCFCatalogFromSnapshot(const JPWNCFSnapshot &s,const JPWNCFHead &h,
                              const long confirmed,JPWNCFCatalogRow &r)
  {
   r.kind="study"; r.entry_id=h.study_id; r.study_id=h.study_id; r.symbol=s.symbol;
   r.source_name=s.source_name; r.source_tf=s.reference_tf; r.revision=h.revision;
   r.generation=h.generation; r.paused=(int)h.paused; r.captured_utc=s.captured_utc;
   r.confirmed_utc=confirmed; r.label="Estudo Fibonacci"; r.record_checksum=h.checksum;
   r.checksum=""; r.linked_checksum="";
  }
JPWNCFStatus JPWNCFCatalogPage(const string key,const string symbol,const string study_id,
                             const int offset,const int limit,JPWNCFCatalogRow &rows[],
                             bool &has_more,string &reason)
  {
   ArrayResize(rows,0); has_more=false; reason="";
   if(symbol=="" || offset<0 || offset>1000000 || limit<1 || limit>20 ||
      (study_id!="" && !JPWNCFIsHash(study_id))) return(JPW_NCF_INVALID);
   int db=INVALID_HANDLE; JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason);
   if(status!=JPW_NCF_VALID) return(status);
   // JOIN selects only fixed-size metadata and existing checksum columns.
   // The opening sequence is verified only upon selecting LoadHead/LoadRevision.
   const string fields="SELECT c.kind,c.entry_id,c.study_id,c.symbol,c.source_name,c.source_tf,c.revision,c.generation,c.paused,c.captured_utc,c.confirmed_utc,c.label,c.record_checksum,c.checksum,COALESCE(h.checksum,r.checksum,n.checksum,'') FROM fibo_catalog c LEFT JOIN fibo_heads h ON c.kind='study' AND h.study_id=c.study_id LEFT JOIN fibo_revisions r ON c.kind='revision' AND r.study_id=c.study_id AND r.revision=c.revision LEFT JOIN fibo_notes n ON c.kind='observation' AND n.note_id=c.entry_id ";
   const string filter=study_id=="" ? "WHERE c.kind='study' AND c.symbol=?1 AND ?2='' " :
      "WHERE c.study_id=?2 AND c.kind<>'study' AND c.symbol=?1 ";
   int q=DatabasePrepare(db,fields+filter+"ORDER BY c.confirmed_utc DESC,c.revision DESC,c.entry_id LIMIT ?3 OFFSET ?4");
   bool bound=q!=INVALID_HANDLE && DatabaseBind(q,0,symbol) && DatabaseBind(q,1,study_id) &&
      DatabaseBind(q,2,limit+1) && DatabaseBind(q,3,offset);
   if(!bound) { if(q!=INVALID_HANDLE) DatabaseFinalize(q); DatabaseClose(db); return(JPW_NCF_IO_ERROR); }
   JPWNCFCatalogRow row; ResetLastError();
   while(DatabaseReadBind(q,row))
     {
      string hash="";
      if(row.symbol!=symbol || (study_id!="" && row.study_id!=study_id) ||
         !JPWNCFCatalogHash(key,row,hash) || hash!=row.checksum || row.record_checksum!=row.linked_checksum)
        { status=JPW_NCF_CORRUPT; reason="Indice do catalogo diverge do registro; selecao bloqueada"; break; }
      const int count=ArraySize(rows);
      if(count==limit) { has_more=true; break; }
      if(ArrayResize(rows,count+1)!=count+1) { status=JPW_NCF_IO_ERROR; break; }
      rows[count]=row; ResetLastError();
     }
   if(status==JPW_NCF_VALID && !has_more && GetLastError()!=ERR_DATABASE_NO_MORE_DATA) status=JPWNCFDatabaseError(GetLastError());
   DatabaseFinalize(q); DatabaseClose(db);
   if(status!=JPW_NCF_VALID) { ArrayResize(rows,0); has_more=false; }
   return(status);
  }
bool JPWNCFRevisionHash(const string key,const JPWNCFRevisionRow &r,string &hash)
  { return(JPWNCFHash(JPWNCFFrame(key)+JPWNCFFrame(r.study_id)+JPWNCFFrame(IntegerToString(r.revision))+
       JPWNCFFrame(IntegerToString(r.previous_revision))+JPWNCFFrame(r.payload)+JPWNCFFrame(r.justification)+JPWNCFFrame(IntegerToString(r.confirmed_utc)),hash)); }
bool JPWNCFHeadHash(const string key,const JPWNCFHead &h,const string revision_hash,string &hash)
  { return(JPWNCFHash(JPWNCFFrame(key)+JPWNCFFrame(h.study_id)+JPWNCFFrame(IntegerToString(h.generation))+
       JPWNCFFrame(IntegerToString(h.revision))+JPWNCFFrame(IntegerToString((int)h.paused))+JPWNCFFrame(revision_hash),hash)); }
JPWNCFStatus JPWNCFReadRevision(const int db,const string key,const string id,const int revision,
                               JPWNCFSnapshot &s,string &revision_hash,string &reason)
  {
   JPWNCFClear(s); revision_hash="";
   int q=DatabasePrepare(db,"SELECT study_id,revision,previous_revision,payload,justification,confirmed_utc,checksum FROM fibo_revisions WHERE study_id=?1 AND revision=?2");
   if(q==INVALID_HANDLE) return(JPWNCFDatabaseError(GetLastError()));
   bool bound=DatabaseBind(q,0,id) && DatabaseBind(q,1,revision);
   JPWNCFRevisionRow r; ResetLastError(); bool found=bound && DatabaseReadBind(q,r); int error=GetLastError();
   DatabaseFinalize(q);
   if(!found) return(error==ERR_DATABASE_NO_MORE_DATA ? JPW_NCF_ABSENT : JPWNCFDatabaseError(error));
   string hash="";
   if(r.study_id!=id || r.revision!=revision || r.previous_revision<0 || r.previous_revision>=r.revision || r.confirmed_utc<=0 ||
      !JPWNCFRevisionHash(key,r,hash) || hash!=r.checksum)
     { reason="Checksum da revisao invalido"; return(JPW_NCF_CORRUPT); }
   JPWNCFStatus status=JPWNCFUnpack(r.payload,s,reason);
   if(status==JPW_NCF_VALID) revision_hash=hash;
   return(status);
  }
JPWNCFStatus JPWNCFReadHead(const int db,const string key,const string id,
                           JPWNCFHead &h,JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFHeadClear(h); JPWNCFClear(s);
   int q=DatabasePrepare(db,"SELECT study_id,generation,revision,paused,checksum FROM fibo_heads WHERE study_id=?1");
   if(q==INVALID_HANDLE) return(JPWNCFDatabaseError(GetLastError()));
   bool bound=DatabaseBind(q,0,id); JPWNCFHeadRow r;
   ResetLastError(); bool found=bound && DatabaseReadBind(q,r); int error=GetLastError(); DatabaseFinalize(q);
   if(!found) return(error==ERR_DATABASE_NO_MORE_DATA ? JPW_NCF_ABSENT : JPWNCFDatabaseError(error));
   if(r.study_id!=id || r.generation<1 || r.revision<1 || (r.paused!=0 && r.paused!=1)) return(JPW_NCF_CORRUPT);
   h.study_id=r.study_id; h.generation=r.generation; h.revision=r.revision; h.paused=r.paused!=0; h.checksum=r.checksum;
   string rh="",hash=""; JPWNCFStatus status=JPWNCFReadRevision(db,key,id,h.revision,s,rh,reason);
   if(status==JPW_NCF_ABSENT) status=JPW_NCF_CORRUPT;
   if(status==JPW_NCF_VALID && (!JPWNCFHeadHash(key,h,rh,hash) || hash!=h.checksum)) status=JPW_NCF_CORRUPT;
   if(status!=JPW_NCF_VALID) { JPWNCFHeadClear(h); JPWNCFClear(s); reason="Cabecalho/revisao sem integridade"; }
   return(status);
  }
JPWNCFStatus JPWNCFLoadHead(const string key,const string id,JPWNCFHead &head,JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFHeadClear(head); JPWNCFClear(s); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason);
   if(status!=JPW_NCF_VALID) return(status);
   // Read transaction prevents head/revision changing between the two reads.
   if(!DatabaseExecute(db,"BEGIN")) { DatabaseClose(db); return(JPW_NCF_BUSY); }
   status=JPWNCFReadHead(db,key,id,head,s,reason); DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status);
  }
JPWNCFStatus JPWNCFLoadRevision(const string key,const string id,const int revision,JPWNCFSnapshot &s,string &reason)
  {
   JPWNCFClear(s); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason); if(status!=JPW_NCF_VALID) return(status);
   string checksum=""; status=JPWNCFReadRevision(db,key,id,revision,s,checksum,reason); DatabaseClose(db); return(status);
  }
bool JPWNCFWriteHead(const int db,const string key,JPWNCFHead &h,const string revision_hash,const int expected)
  {
   if(!JPWNCFHeadHash(key,h,revision_hash,h.checksum)) return(false);
   int q=DatabasePrepare(db,expected==0 ?
      "INSERT INTO fibo_heads(study_id,generation,revision,paused,checksum) VALUES(?1,?2,?3,?4,?5)" :
      "UPDATE fibo_heads SET generation=?2,revision=?3,paused=?4,checksum=?5 WHERE study_id=?1 AND generation=?6");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,h.study_id) && DatabaseBind(q,1,h.generation) &&
      DatabaseBind(q,2,h.revision) && DatabaseBind(q,3,(int)h.paused) && DatabaseBind(q,4,h.checksum);
   if(expected!=0) ok=ok && DatabaseBind(q,5,expected);
   ok=ok && JPWNCFExecutePrepared(q); if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!ok) return(false);
   q=DatabasePrepare(db,"SELECT changes()"); int changed=0;
   ok=q!=INVALID_HANDLE && DatabaseRead(q) && DatabaseColumnInteger(q,0,changed) && changed==1;
   if(q!=INVALID_HANDLE) DatabaseFinalize(q); return(ok);
  }
JPWNCFStatus JPWNCFSaveInternal(const string key,const string id,const int expected_generation,
                       const JPWNCFSnapshot &s,const string justification,const bool force_paused,JPWNCFHead &head,string &reason)
  {
   JPWNCFHeadClear(head); reason="";
   JPWNCFStatus valid=JPWNCFValidate(s,reason); if(valid!=JPW_NCF_VALID) return(valid);
   if(!JPWNCFIsHash(id) || expected_generation<0 || StringLen(justification)<1 || StringLen(justification)>2048)
      return(JPW_NCF_INVALID);
   string payload=JPWNCFPack(s); if(payload=="") return(JPW_NCF_INVALID);
   int db=INVALID_HANDLE; JPWNCFStatus status=JPWNCFStoreOpen(key,true,db,reason); if(status!=JPW_NCF_VALID) return(status);
   if(!DatabaseExecute(db,"BEGIN IMMEDIATE"))
     { status=JPWNCFDatabaseError(GetLastError()); DatabaseClose(db); return(status); }
   JPWNCFHead current; JPWNCFSnapshot previous;
   status=JPWNCFReadHead(db,key,id,current,previous,reason);
   bool accepted=(status==JPW_NCF_ABSENT && expected_generation==0) ||
      (status==JPW_NCF_VALID && current.generation==expected_generation);
   if(!accepted)
     { DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db);
       reason="Outra instancia alterou o estudo ou o registro esta invalido";
       return(status==JPW_NCF_VALID || status==JPW_NCF_ABSENT ? JPW_NCF_CONFLICT : status); }
   if(status==JPW_NCF_VALID && (previous.symbol!=s.symbol || previous.feed!=s.feed || previous.reference_tf!=s.reference_tf))
     { DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); reason="Identidade do estudo nao pode mudar"; return(JPW_NCF_INCOMPATIBLE); }
   int q=DatabasePrepare(db,"SELECT COALESCE(MAX(revision),0) FROM fibo_revisions WHERE study_id=?1");
   int highest=0; bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,id) && DatabaseRead(q) && DatabaseColumnInteger(q,0,highest);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(highest>=2147483646 || expected_generation>=2147483646) ok=false;
   JPWNCFRevisionRow row; row.study_id=id; row.revision=highest+1;
   row.previous_revision=current.revision; row.payload=payload; row.justification=justification; row.confirmed_utc=(long)TimeGMT();
   ok=ok && JPWNCFRevisionHash(key,row,row.checksum);
   if(ok)
     {
      q=DatabasePrepare(db,"INSERT INTO fibo_revisions(study_id,revision,previous_revision,payload,justification,confirmed_utc,checksum) VALUES(?1,?2,?3,?4,?5,?6,?7)");
      ok=q!=INVALID_HANDLE && DatabaseBind(q,0,id) && DatabaseBind(q,1,row.revision) &&
         DatabaseBind(q,2,row.previous_revision) && DatabaseBind(q,3,row.payload) &&
         DatabaseBind(q,4,row.justification) && DatabaseBind(q,5,row.confirmed_utc) && DatabaseBind(q,6,row.checksum) && JPWNCFExecutePrepared(q);
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
     }
   JPWNCFHead proposed; proposed.study_id=id; proposed.generation=expected_generation+1;
   proposed.revision=row.revision; proposed.paused=current.paused;
   if(expected_generation==0) proposed.paused=false;
   if(force_paused) proposed.paused=true;
   ok=ok && JPWNCFWriteHead(db,key,proposed,row.checksum,expected_generation);
   JPWNCFCatalogRow catalog; JPWNCFCatalogFromSnapshot(s,proposed,row.confirmed_utc,catalog);
   ok=ok && JPWNCFWriteCatalog(db,key,catalog);
   catalog.kind="revision"; catalog.entry_id=id+":"+IntegerToString(row.revision);
   catalog.label="Revisao "+IntegerToString(row.revision); catalog.record_checksum=row.checksum;
   ok=ok && JPWNCFWriteCatalog(db,key,catalog);
   // Verify newly serialized payload and checksum under the same transaction.
   JPWNCFHead checked; JPWNCFSnapshot reloaded;
   ok=ok && JPWNCFReadHead(db,key,id,checked,reloaded,reason)==JPW_NCF_VALID && JPWNCFPack(reloaded)==payload;
   if(ok && DatabaseExecute(db,"COMMIT")) { head=proposed; DatabaseClose(db); return(JPW_NCF_VALID); }
   status=JPWNCFDatabaseError(GetLastError()); DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db);
   reason="Revisao nao gravada; rascunho preservado"; return(status);
  }
JPWNCFStatus JPWNCFSave(const string key,const string id,const int expected_generation,
                       const JPWNCFSnapshot &s,const string justification,JPWNCFHead &head,string &reason)
  { return(JPWNCFSaveInternal(key,id,expected_generation,s,justification,false,head,reason)); }
// Metadata-only pause uses the same CAS contract. Rollback below creates a new
// immutable revision and pauses within that single save transaction.
JPWNCFStatus JPWNCFMoveHead(const string key,const string id,const int expected_generation,
                           const int target_revision,const bool paused,JPWNCFHead &head,string &reason)
  {
   JPWNCFHeadClear(head); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,true,db,reason); if(status!=JPW_NCF_VALID) return(status);
   if(!DatabaseExecute(db,"BEGIN IMMEDIATE")) { status=JPWNCFDatabaseError(GetLastError()); DatabaseClose(db); return(status); }
   JPWNCFHead current; JPWNCFSnapshot s;
   status=JPWNCFReadHead(db,key,id,current,s,reason);
   if(status!=JPW_NCF_VALID || current.generation!=expected_generation || current.generation>=2147483646)
     { DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status==JPW_NCF_VALID ? JPW_NCF_CONFLICT : status); }
   string rh=""; int revision=target_revision>0 ? target_revision : current.revision;
   status=JPWNCFReadRevision(db,key,id,revision,s,rh,reason);
   if(status!=JPW_NCF_VALID) { DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status); }
   current.generation++; current.revision=revision; current.paused=paused;
   // Preserve the revision's confirmation timestamp while changing pause metadata.
   int cq=DatabasePrepare(db,"SELECT confirmed_utc FROM fibo_revisions WHERE study_id=?1 AND revision=?2");
   long confirmed=0;
   bool ok=cq!=INVALID_HANDLE && DatabaseBind(cq,0,id) && DatabaseBind(cq,1,revision) &&
      DatabaseRead(cq) && DatabaseColumnLong(cq,0,confirmed);
   if(cq!=INVALID_HANDLE) DatabaseFinalize(cq);
   ok=ok && JPWNCFWriteHead(db,key,current,rh,expected_generation);
   JPWNCFCatalogRow catalog; JPWNCFCatalogFromSnapshot(s,current,confirmed,catalog);
   ok=ok && JPWNCFWriteCatalog(db,key,catalog);
   if(ok && DatabaseExecute(db,"COMMIT")) { head=current; DatabaseClose(db); return(JPW_NCF_VALID); }
   status=JPWNCFDatabaseError(GetLastError()); DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status);
  }
JPWNCFStatus JPWNCFRollback(const string key,const string id,const int expected_generation,const int target_revision,
                           JPWNCFHead &head,string &reason)
  {
   JPWNCFSnapshot previous;
   JPWNCFStatus status=JPWNCFLoadRevision(key,id,target_revision,previous,reason);
   if(status!=JPW_NCF_VALID) { JPWNCFHeadClear(head); return(status); }
   return(JPWNCFSaveInternal(key,id,expected_generation,previous,
      "Restauracao explicita da revisao "+IntegerToString(target_revision),true,head,reason));
  }
JPWNCFStatus JPWNCFSetPaused(const string key,const string id,const int expected_generation,const bool paused,
                            JPWNCFHead &head,string &reason)
  { return(JPWNCFMoveHead(key,id,expected_generation,0,paused,head,reason)); }
JPWNCFStatus JPWNCFListStudies(const string key,const string symbol,string &ids[],string &reason)
  {
   ArrayResize(ids,0); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason); if(status!=JPW_NCF_VALID) return(status);
   int q=DatabasePrepare(db,"SELECT study_id FROM fibo_heads ORDER BY study_id");
   if(q==INVALID_HANDLE) { DatabaseClose(db); return(JPW_NCF_IO_ERROR); }
   while(DatabaseRead(q))
     {
      string id=""; JPWNCFHead h; JPWNCFSnapshot s;
      if(!DatabaseColumnText(q,0,id)) { status=JPW_NCF_CORRUPT; break; }
      status=JPWNCFReadHead(db,key,id,h,s,reason); if(status!=JPW_NCF_VALID) break;
      if(s.symbol==symbol)
        { int n=ArraySize(ids); if(n>=10000 || ArrayResize(ids,n+1)!=n+1) { status=JPW_NCF_IO_ERROR; break; } ids[n]=id; }
     }
   if(status==JPW_NCF_VALID && GetLastError()!=ERR_DATABASE_NO_MORE_DATA) status=JPWNCFDatabaseError(GetLastError());
   DatabaseFinalize(q); DatabaseClose(db);
   if(status!=JPW_NCF_VALID) ArrayResize(ids,0);
   return(status);
  }
// Explicitly requested notes only. Payload is UTF text with a versioned caller
// contract; never executable SQL. A projection marked verified is refused until
// the native measurement gate has a separately audited implementation.
JPWNCFStatus JPWNCFSaveNote(const string key,const string id,const int expected_generation,
                           const int revision,const string kind,const string payload,const long observed_utc,
                           string &note_id,string &reason)
  {
   note_id="";
   if(!JPWNCFIsHash(id) || expected_generation<1 || revision<1 || observed_utc<=0 ||
      (kind!="observation" && kind!="projection") || StringLen(payload)<1 || StringLen(payload)>65536)
      return(JPW_NCF_INVALID);
   // Projection publication is fail-closed until native parity is available.
   if(kind=="projection") { reason="Projecao importada sem paridade nativa comprovada"; return(JPW_NCF_UNVERIFIED_NATIVE); }
   string body=JPWNCFFrame("fibo_note_v1")+JPWNCFFrame(key)+JPWNCFFrame(id)+JPWNCFFrame(IntegerToString(revision))+
      JPWNCFFrame(IntegerToString(expected_generation))+JPWNCFFrame(kind)+JPWNCFFrame(payload)+JPWNCFFrame(IntegerToString(observed_utc));
   string hash=""; if(!JPWNCFHash(body,hash)) return(JPW_NCF_IO_ERROR);
   int db=INVALID_HANDLE; JPWNCFStatus status=JPWNCFStoreOpen(key,true,db,reason); if(status!=JPW_NCF_VALID) return(status);
   if(!DatabaseExecute(db,"BEGIN IMMEDIATE")) { status=JPWNCFDatabaseError(GetLastError()); DatabaseClose(db); return(status); }
   JPWNCFHead h; JPWNCFSnapshot s; status=JPWNCFReadHead(db,key,id,h,s,reason);
   if(status!=JPW_NCF_VALID || h.generation!=expected_generation || h.revision!=revision)
     { DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status==JPW_NCF_VALID ? JPW_NCF_CONFLICT : status); }
   int q=DatabasePrepare(db,"INSERT OR IGNORE INTO fibo_notes(note_version,note_id,study_id,revision,generation,kind,payload,observed_utc,checksum) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9)");
   bool ok=q!=INVALID_HANDLE && DatabaseBind(q,0,1) && DatabaseBind(q,1,hash) && DatabaseBind(q,2,id) &&
      DatabaseBind(q,3,revision) && DatabaseBind(q,4,expected_generation) && DatabaseBind(q,5,kind) &&
      DatabaseBind(q,6,payload) && DatabaseBind(q,7,observed_utc) && DatabaseBind(q,8,hash) && JPWNCFExecutePrepared(q);
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   // Re-read even on an idempotent INSERT OR IGNORE. A conflicting/corrupt row
   // must not be reported as a saved observation.
   if(ok)
     {
      q=DatabasePrepare(db,"SELECT note_version,note_id,study_id,revision,generation,kind,payload,observed_utc,checksum FROM fibo_notes WHERE note_id=?1");
      JPWNCFNoteRow reread;
      ok=q!=INVALID_HANDLE && DatabaseBind(q,0,hash) && DatabaseReadBind(q,reread) &&
         reread.note_version==1 && reread.note_id==hash && reread.study_id==id &&
         reread.revision==revision && reread.generation==expected_generation && reread.kind==kind &&
         reread.payload==payload && reread.observed_utc==observed_utc && reread.checksum==hash;
      if(q!=INVALID_HANDLE) DatabaseFinalize(q);
     }
   JPWNCFCatalogRow catalog; JPWNCFCatalogFromSnapshot(s,h,observed_utc,catalog);
   catalog.kind="observation"; catalog.entry_id=hash; catalog.record_checksum=hash;
   catalog.label="Observacao manual";
   ok=ok && JPWNCFWriteCatalog(db,key,catalog);
   if(ok && DatabaseExecute(db,"COMMIT")) { note_id=hash; DatabaseClose(db); return(JPW_NCF_VALID); }
   status=JPWNCFDatabaseError(GetLastError()); DatabaseExecute(db,"ROLLBACK"); DatabaseClose(db); return(status);
  }
JPWNCFStatus JPWNCFListRevisions(const string key,const string id,int &revisions[],string &reason)
  {
   ArrayResize(revisions,0); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason); if(status!=JPW_NCF_VALID) return(status);
   int q=DatabasePrepare(db,"SELECT revision FROM fibo_revisions WHERE study_id=?1 ORDER BY revision DESC");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,id))
     { if(q!=INVALID_HANDLE) DatabaseFinalize(q); DatabaseClose(db); return(JPW_NCF_IO_ERROR); }
   ResetLastError();
   while(DatabaseRead(q))
     {
      int revision=0; JPWNCFSnapshot s; string hash="";
      if(!DatabaseColumnInteger(q,0,revision)) { status=JPW_NCF_CORRUPT; break; }
      status=JPWNCFReadRevision(db,key,id,revision,s,hash,reason); if(status!=JPW_NCF_VALID) break;
      int n=ArraySize(revisions);
      if(n>=10000 || ArrayResize(revisions,n+1)!=n+1) { status=JPW_NCF_IO_ERROR; break; }
      revisions[n]=revision; ResetLastError();
     }
   if(status==JPW_NCF_VALID && GetLastError()!=ERR_DATABASE_NO_MORE_DATA) status=JPWNCFDatabaseError(GetLastError());
   DatabaseFinalize(q); DatabaseClose(db); if(status!=JPW_NCF_VALID) ArrayResize(revisions,0);
   return(status);
  }
JPWNCFStatus JPWNCFLoadNotes(const string key,const string id,JPWNCFNoteRow &notes[],string &reason)
  {
   ArrayResize(notes,0); int db=INVALID_HANDLE;
   JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason); if(status!=JPW_NCF_VALID) return(status);
   int q=DatabasePrepare(db,"SELECT note_version,note_id,study_id,revision,generation,kind,payload,observed_utc,checksum FROM fibo_notes WHERE study_id=?1 ORDER BY observed_utc DESC,note_id");
   if(q==INVALID_HANDLE || !DatabaseBind(q,0,id))
     { if(q!=INVALID_HANDLE) DatabaseFinalize(q); DatabaseClose(db); return(JPW_NCF_IO_ERROR); }
   JPWNCFNoteRow row; ResetLastError();
   while(DatabaseReadBind(q,row))
     {
      string body=JPWNCFFrame("fibo_note_v1")+JPWNCFFrame(key)+JPWNCFFrame(id)+JPWNCFFrame(IntegerToString(row.revision))+
         JPWNCFFrame(IntegerToString(row.generation))+JPWNCFFrame(row.kind)+JPWNCFFrame(row.payload)+JPWNCFFrame(IntegerToString(row.observed_utc));
      string hash="",rh=""; JPWNCFSnapshot snapshot;
      if(row.note_version!=1) { status=JPW_NCF_INCOMPATIBLE; break; }
      if(row.study_id!=id || row.revision<1 || row.generation<1 || row.observed_utc<=0 ||
         (row.kind!="observation" && row.kind!="projection") || StringLen(row.payload)<1 || StringLen(row.payload)>65536 ||
         !JPWNCFHash(body,hash) || hash!=row.checksum || row.note_id!=hash ||
         JPWNCFReadRevision(db,key,id,row.revision,snapshot,rh,reason)!=JPW_NCF_VALID)
        { status=JPW_NCF_CORRUPT; break; }
      int n=ArraySize(notes);
      if(n>=10000 || ArrayResize(notes,n+1)!=n+1) { status=JPW_NCF_IO_ERROR; break; }
      notes[n]=row; ResetLastError();
     }
   if(status==JPW_NCF_VALID && GetLastError()!=ERR_DATABASE_NO_MORE_DATA) status=JPWNCFDatabaseError(GetLastError());
   DatabaseFinalize(q); DatabaseClose(db); if(status!=JPW_NCF_VALID) ArrayResize(notes,0);
   return(status);
  }
// Selection-only full validation of one note and its referenced revision.
JPWNCFStatus JPWNCFLoadNote(const string key,const string id,const string note_id,
                          JPWNCFNoteRow &row,string &reason)
  {
   if(!JPWNCFIsHash(id) || !JPWNCFIsHash(note_id)) return(JPW_NCF_INVALID);
   int db=INVALID_HANDLE; JPWNCFStatus status=JPWNCFStoreOpen(key,false,db,reason);
   if(status!=JPW_NCF_VALID) return(status);
   int q=DatabasePrepare(db,"SELECT note_version,note_id,study_id,revision,generation,kind,payload,observed_utc,checksum FROM fibo_notes WHERE note_id=?1 AND study_id=?2");
   bool bound=q!=INVALID_HANDLE && DatabaseBind(q,0,note_id) && DatabaseBind(q,1,id);
   ResetLastError(); bool found=bound && DatabaseReadBind(q,row); int error=GetLastError();
   if(q!=INVALID_HANDLE) DatabaseFinalize(q);
   if(!found) { DatabaseClose(db); return(error==ERR_DATABASE_NO_MORE_DATA ? JPW_NCF_ABSENT : JPWNCFDatabaseError(error)); }
   string body=JPWNCFFrame("fibo_note_v1")+JPWNCFFrame(key)+JPWNCFFrame(id)+JPWNCFFrame(IntegerToString(row.revision))+
      JPWNCFFrame(IntegerToString(row.generation))+JPWNCFFrame(row.kind)+JPWNCFFrame(row.payload)+JPWNCFFrame(IntegerToString(row.observed_utc));
   string hash="",rh=""; JPWNCFSnapshot snapshot;
   if(row.note_version!=1) status=JPW_NCF_INCOMPATIBLE;
   else if(row.note_id!=note_id || row.study_id!=id || row.revision<1 || row.generation<1 ||
      row.observed_utc<=0 || (row.kind!="observation" && row.kind!="projection") ||
      StringLen(row.payload)<1 || StringLen(row.payload)>65536 || !JPWNCFHash(body,hash) ||
      hash!=row.checksum || row.note_id!=hash ||
      JPWNCFReadRevision(db,key,id,row.revision,snapshot,rh,reason)!=JPW_NCF_VALID) status=JPW_NCF_CORRUPT;
   DatabaseClose(db); return(status);
  }
#endif

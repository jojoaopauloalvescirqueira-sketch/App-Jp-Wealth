#!/usr/bin/env python3
"""Run production MQL store control flow with host SQLite / SHA256 API adapters.
Native MQL bindings and native chart interaction are still NOT_RUN.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Core.mqh'
STORE=CORE.with_name('JPW_NoCuda_Fibo_Store.mqh')
spec=importlib.util.spec_from_file_location('coretest',ROOT/'tools/jpw_nocuda_fibo_test.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
DBSHIM=r'''
#include <sqlite3.h>
#include <filesystem>
#include <map>
#include <type_traits>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using uchar=unsigned char;
long TimeGMT();
#define INVALID_HANDLE -1
#define WHOLE_ARRAY -1
#define CP_UTF8 65001
#define CRYPT_HASH_SHA256 1
#define DATABASE_OPEN_READONLY 1
#define DATABASE_OPEN_READWRITE 2
#define DATABASE_OPEN_CREATE 4
#define ERR_DATABASE_BUSY 5
#define ERR_DATABASE_LOCKED 6
#define ERR_DATABASE_CORRUPT 11
#define ERR_DATABASE_NOTADB 26
#define ERR_DATABASE_NO_MORE_DATA 101
int payload_selects=0,catalog_reads=0;int last_error=0,next_handle=1;bool fail_next_commit=false;
std::map<int,sqlite3*> databases;
std::map<int,sqlite3_stmt*> statements;
string root_path;
void ResetLastError(){last_error=0;}
int GetLastError(){return last_error;}
ushort StringGetCharacter(const string&s,int i){return static_cast<unsigned char>(s.at(i));}
int StringToCharArray(const string&s,std::vector<uchar>&out,int,int,int){out.assign(s.begin(),s.end());out.push_back(0);return (int)out.size();}
int CryptEncode(int,const std::vector<uchar>&src,const std::vector<uchar>&,std::vector<uchar>&out){out.resize(32);
#ifdef __APPLE__
CC_SHA256(src.data(),(CC_LONG)src.size(),out.data());
#else
SHA256(src.data(),src.size(),out.data());
#endif
return 32;}
string path_for(string s){std::replace(s.begin(),s.end(),'\\','/');return root_path+"/"+s;}
bool FileIsExist(const string&s){return std::filesystem::exists(path_for(s));}
bool FolderCreate(const string&s){std::filesystem::create_directories(path_for(s));return true;}
int DatabaseOpen(const string&name,int flags){sqlite3*db=nullptr;int f=(flags&DATABASE_OPEN_READWRITE)?SQLITE_OPEN_READWRITE:SQLITE_OPEN_READONLY;if(flags&DATABASE_OPEN_CREATE)f|=SQLITE_OPEN_CREATE;int r=sqlite3_open_v2(path_for(name).c_str(),&db,f,nullptr);last_error=r;if(r!=SQLITE_OK){if(db)sqlite3_close(db);return -1;}int h=next_handle++;databases[h]=db;return h;}
void DatabaseClose(int h){if(databases.count(h)){sqlite3_close(databases[h]);databases.erase(h);}}
bool DatabaseExecute(int h,const string&q){if(q=="COMMIT"&&fail_next_commit){fail_next_commit=false;last_error=SQLITE_IOERR;return false;}last_error=sqlite3_exec(databases.at(h),q.c_str(),nullptr,nullptr,nullptr);return last_error==SQLITE_OK;}
int DatabasePrepare(int h,const string&q){if(q.rfind("SELECT",0)==0&&q.find("payload")!=string::npos)payload_selects++;sqlite3_stmt*s=nullptr;last_error=sqlite3_prepare_v2(databases.at(h),q.c_str(),-1,&s,nullptr);if(last_error!=SQLITE_OK)return -1;int handle=next_handle++;statements[handle]=s;return handle;}
void DatabaseFinalize(int h){if(statements.count(h)){sqlite3_finalize(statements[h]);statements.erase(h);}}
bool DatabaseBind(int q,int i,const string&v){last_error=sqlite3_bind_text(statements.at(q),i+1,v.c_str(),(int)v.size(),SQLITE_TRANSIENT);return last_error==SQLITE_OK;}
bool DatabaseBind(int q,int i,long v){last_error=sqlite3_bind_int64(statements.at(q),i+1,v);return last_error==SQLITE_OK;}
bool DatabaseBind(int q,int i,int v){return DatabaseBind(q,i,(long)v);}
bool DatabaseRead(int q){int rc=sqlite3_step(statements.at(q));last_error=rc==SQLITE_ROW?0:rc;return rc==SQLITE_ROW;}
bool DatabaseColumnInteger(int q,int i,int&out){if(sqlite3_column_type(statements.at(q),i)!=SQLITE_INTEGER)return false;out=sqlite3_column_int(statements.at(q),i);return true;}
bool DatabaseColumnLong(int q,int i,long&out){if(sqlite3_column_type(statements.at(q),i)!=SQLITE_INTEGER)return false;out=(long)sqlite3_column_int64(statements.at(q),i);return true;}
bool DatabaseColumnText(int q,int i,string&out){if(sqlite3_column_type(statements.at(q),i)!=SQLITE_TEXT)return false;const char*v=(const char*)sqlite3_column_text(statements.at(q),i);out=v?v:"";return true;}
bool DatabaseTableExists(int db,const string&table){int q=DatabasePrepare(db,"SELECT name FROM sqlite_master WHERE type='table' AND name=?1");bool ok=q>=0&&DatabaseBind(q,0,table)&&DatabaseRead(q);if(q>=0)DatabaseFinalize(q);return ok;}
template<class T>bool DatabaseReadBind(int q,T&row);
'''
DBREAD=r'''
template<class T>bool DatabaseReadBind(int q,T&r){
if(!DatabaseRead(q))return false;int i=0;
auto text=[&](string&x){return DatabaseColumnText(q,i++,x);};
auto integer=[&](int&x){return DatabaseColumnInteger(q,i++,x);};
if constexpr(std::is_same_v<T,JPWNCFMetaRow>)return integer(r.schema_version)&&text(r.store_key);
if constexpr(std::is_same_v<T,JPWNCFHeadRow>)return text(r.study_id)&&integer(r.generation)&&integer(r.revision)&&integer(r.paused)&&text(r.checksum);
if constexpr(std::is_same_v<T,JPWNCFRevisionRow>){bool ok=text(r.study_id)&&integer(r.revision)&&integer(r.previous_revision)&&text(r.payload)&&text(r.justification);r.confirmed_utc=sqlite3_column_int64(statements.at(q),i++);return ok&&text(r.checksum);}
if constexpr(std::is_same_v<T,JPWNCFCatalogRow>){catalog_reads++;bool ok=text(r.kind)&&text(r.entry_id)&&text(r.study_id)&&text(r.symbol)&&text(r.source_name)&&integer(r.source_tf)&&integer(r.revision)&&integer(r.generation)&&integer(r.paused);ok=ok&&DatabaseColumnLong(q,i++,r.captured_utc)&&DatabaseColumnLong(q,i++,r.confirmed_utc);return ok&&text(r.label)&&text(r.record_checksum)&&text(r.checksum)&&text(r.linked_checksum);}
if constexpr(std::is_same_v<T,JPWNCFNoteRow>){bool ok=integer(r.note_version)&&text(r.note_id)&&text(r.study_id)&&integer(r.revision)&&integer(r.generation)&&text(r.kind)&&text(r.payload);r.observed_utc=sqlite3_column_int64(statements.at(q),i++);return ok&&text(r.checksum);}
return false;}
'''
TEST=r'''
long synthetic_utc=1800000000;long TimeGMT(){return synthetic_utc;}
int main(int argc,char**argv){if(argc!=2)return 2;root_path=argv[1];
JPWNCFSnapshot s,loaded;NCFFixture(s);string reason,key,id;JPWNCFHead head;
NCFCheck(JPWNCFStoreKey("SYNTHETIC_INSTALLATION","TEST_ONLY",key),"store key");
NCFCheck(JPWNCFNewStudyId(key,"SYNTHETIC",1800000000,1,id),"study id");
NCFCheck(JPWNCFLoadHead(key,id,head,loaded,reason)==JPW_NCF_ABSENT,"absent no implicit create");
NCFCheck(JPWNCFSave(key,id,0,s,"initial synthetic import",head,reason)==JPW_NCF_VALID,"first revision saved");
NCFCheck(head.generation==1&&head.revision==1&&!head.paused,"initial head");
NCFCheck(JPWNCFLoadHead(key,id,head,loaded,reason)==JPW_NCF_VALID&&JPWNCFPack(s)==JPWNCFPack(loaded),"exact source roundtrip");
NCFCheck(JPWNCFSave(key,id,0,s,"stale writer",head,reason)==JPW_NCF_CONFLICT,"CAS stale create");
s.anchor_price[2]+=0.005;
NCFCheck(JPWNCFSave(key,id,1,s,"explicit second gesture",head,reason)==JPW_NCF_VALID&&head.revision==2,"second revision");
synthetic_utc++;NCFCheck(JPWNCFRollback(key,id,2,1,head,reason)==JPW_NCF_VALID&&head.revision==3&&head.paused,"rollback creates revision and pauses");
NCFCheck(JPWNCFLoadRevision(key,id,1,loaded,reason)==JPW_NCF_VALID&&loaded.anchor_price[2]!=s.anchor_price[2],"old revision immutable");
NCFCheck(JPWNCFLoadHead(key,id,head,loaded,reason)==JPW_NCF_VALID&&head.revision==3,"rollback head");
int audit_db=-1;JPWNCFStoreOpen(key,false,audit_db,reason);int audit_q=DatabasePrepare(audit_db,"SELECT confirmed_utc FROM fibo_revisions WHERE revision=3");int confirmed=0;
NCFCheck(DatabaseRead(audit_q)&&DatabaseColumnInteger(audit_q,0,confirmed)&&confirmed==1800000001&&loaded.captured_utc==1800000000,"restoration confirmation distinct from original capture");DatabaseFinalize(audit_q);DatabaseClose(audit_db);
NCFCheck(JPWNCFSetPaused(key,id,3,false,head,reason)==JPW_NCF_VALID&&head.generation==4&&!head.paused,"explicit resume");
std::vector<int> revisions;NCFCheck(JPWNCFListRevisions(key,id,revisions,reason)==JPW_NCF_VALID&&revisions.size()==3&&revisions[0]==3,"list revisions");
std::vector<string> ids;NCFCheck(JPWNCFListStudies(key,"SYNTHETIC",ids,reason)==JPW_NCF_VALID&&ids.size()==1&&ids[0]==id,"list studies");
NCFCheck(JPWNCFListStudies(key,"OTHER",ids,reason)==JPW_NCF_VALID&&ids.empty(),"exact symbol isolation");
string note;NCFCheck(JPWNCFSaveNote(key,id,4,3,"observation","v1 manual OHLC fixture",1800000001,note,reason)==JPW_NCF_VALID,"observation save");
NCFCheck(JPWNCFSaveNote(key,id,4,3,"observation","v1 manual OHLC fixture",1800000001,note,reason)==JPW_NCF_VALID,"observation idempotence");
std::vector<JPWNCFNoteRow> notes;NCFCheck(JPWNCFLoadNotes(key,id,notes,reason)==JPW_NCF_VALID&&notes.size()==1,"notes verify and load");
NCFCheck(JPWNCFSaveNote(key,id,3,3,"observation","stale",1800000002,note,reason)==JPW_NCF_CONFLICT,"stale observation refused");
NCFCheck(JPWNCFSaveNote(key,id,4,3,"projection","unverified",1800000002,note,reason)==JPW_NCF_UNVERIFIED_NATIVE,"projection guard");
int db=-1;NCFCheck(JPWNCFStoreOpen(key,true,db,reason)==JPW_NCF_VALID,"open for synthetic lock");
NCFCheck(DatabaseExecute(db,"BEGIN IMMEDIATE"),"first writer lock");
NCFCheck(JPWNCFSave(key,id,4,s,"locked",head,reason)==JPW_NCF_BUSY,"second writer nonwaiting busy");
DatabaseExecute(db,"ROLLBACK");DatabaseClose(db);
fail_next_commit=true;NCFCheck(JPWNCFSave(key,id,4,s,"failed commit",head,reason)==JPW_NCF_IO_ERROR,"commit failure explicit");
NCFCheck(JPWNCFLoadHead(key,id,head,loaded,reason)==JPW_NCF_VALID&&head.generation==4&&head.revision==3,"failed commit preserves prior head");
NCFCheck(JPWNCFSave(key,id,4,s,"post lock",head,reason)==JPW_NCF_VALID&&head.revision==4,"recovered save");
for(int i=0;i<25;i++){synthetic_utc++;s.anchor_price[2]+=0.00001;NCFCheck(JPWNCFSave(key,id,head.generation,s,"catalog pagination fixture",head,reason)==JPW_NCF_VALID,"catalog fixture revision");}
std::vector<JPWNCFCatalogRow>page;bool has_more=false;payload_selects=0;catalog_reads=0;
NCFCheck(JPWNCFCatalogPage(key,"SYNTHETIC","",0,20,page,has_more,reason)==JPW_NCF_VALID&&page.size()==1&&!has_more,"study metadata page");
NCFCheck(payload_selects==0&&catalog_reads==1,"study page reads no geometry payload");payload_selects=0;catalog_reads=0;
NCFCheck(JPWNCFCatalogPage(key,"SYNTHETIC",id,0,20,page,has_more,reason)==JPW_NCF_VALID&&page.size()==20&&has_more,"first bounded record page");
NCFCheck(payload_selects==0&&catalog_reads==21,"page reads limit plus one metadata rows only");
NCFCheck(JPWNCFCatalogPage(key,"SYNTHETIC",id,20,20,page,has_more,reason)==JPW_NCF_VALID&&page.size()==10&&!has_more,"second page includes remaining revisions and note");
NCFCheck(JPWNCFCatalogPage(key,"SYNTHETIC",id,0,21,page,has_more,reason)==JPW_NCF_INVALID,"oversize page rejected");
JPWNCFNoteRow single_note;payload_selects=0;NCFCheck(JPWNCFLoadNote(key,id,notes[0].note_id,single_note,reason)==JPW_NCF_VALID&&single_note.payload==notes[0].payload,"single note selection validates exact content");
NCFCheck(payload_selects==2,"single note validates only note plus its one revision");
string old_key;JPWNCFStoreKey("OLD_SYNTHETIC","TEST_ONLY",old_key);int old_db=DatabaseOpen(JPWNCFStorePath(old_key),DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE);DatabaseExecute(old_db,"CREATE TABLE fibo_meta(schema_version INTEGER,store_key TEXT)");int old_q=DatabasePrepare(old_db,"INSERT INTO fibo_meta VALUES(1,?1)");DatabaseBind(old_q,0,old_key);JPWNCFExecutePrepared(old_q);DatabaseFinalize(old_q);DatabaseClose(old_db);
NCFCheck(JPWNCFStoreOpen(old_key,false,old_db,reason)==JPW_NCF_INCOMPATIBLE&&old_db==INVALID_HANDLE,"old schema explicitly incompatible without migration");
NCFCheck(JPWNCFStoreOpen(key,true,db,reason)==JPW_NCF_VALID,"reopen corruption fixture");
DatabaseExecute(db,"UPDATE fibo_catalog SET label='tampered metadata' WHERE kind='study'");
NCFCheck(JPWNCFCatalogPage(key,"SYNTHETIC","",0,20,page,has_more,reason)==JPW_NCF_CORRUPT&&page.empty(),"corrupt metadata cannot be presented as intact");
NCFCheck(!DatabaseExecute(db,"UPDATE fibo_revisions SET payload='tampered'"),"SQLite trigger rejects edit");
DatabaseExecute(db,"UPDATE fibo_heads SET checksum='invalid'");DatabaseClose(db);
NCFCheck(JPWNCFLoadHead(key,id,head,loaded,reason)==JPW_NCF_CORRUPT,"head corruption not accepted");
NCFCheck(JPWNCFSave(key,id,5,s,"must not reset",head,reason)==JPW_NCF_CORRUPT,"corruption not reinitialized");
NCFCheck(databases.empty()&&statements.empty(),"all handles released");
NCFCheck(JPWNCFStoreOpen(key,true,db,reason)==JPW_NCF_VALID,"open metadata fixture");DatabaseExecute(db,"UPDATE fibo_meta SET schema_version=3");DatabaseClose(db);
NCFCheck(JPWNCFStoreOpen(key,false,db,reason)==JPW_NCF_INCOMPATIBLE&&db==INVALID_HANDLE,"future schema refused without replacement");
Print("Store production flow: ",jpw_ncf_asserts," asserts; failures=",jpw_ncf_failed,"; native NOT_RUN");return jpw_ncf_failed?1:0;}
'''
def transform(s):
    s=re.sub(r'^#include[^\n]*\n','',s,flags=re.M)
    s=s.replace('long opens[];', 'std::vector<long> opens;').replace('uchar source[],key[],digest[];', 'std::vector<uchar> source,key,digest;')
    s=re.sub(r'\b(string|int|JPWNCFNoteRow|JPWNCFCatalogRow) &([a-zA-Z_]\w*)\[\]',r'std::vector<\1> &\2',s)
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');args=ap.parse_args();compiler=shutil.which('clang++')or shutil.which('g++')
    if not compiler:raise SystemExit('NOT_RUN compiler unavailable')
    shim=module.SHIM.replace('string StringFormat(const char* fmt,double value)', 'template<class T> string StringFormat(const char* fmt,T value)')
    fixture=re.sub(r'^#(?:include|property).*\n','',module.SCRIPT.read_text(),flags=re.M)
    code=shim+DBSHIM+transform(CORE.read_text())+transform(STORE.read_text())+DBREAD+fixture+TEST
    with tempfile.TemporaryDirectory(prefix='jpw-ncf-store-flow-')as tmp:
        src=Path(tmp)/'store.cpp';src.write_text(code);exe=Path(tmp)/'store';flags=['-lsqlite3']
        if __import__('sys').platform!='darwin':flags+=['-lcrypto']
        compile_result=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations',str(src),'-o',str(exe),*flags],text=True,capture_output=True)
        run=subprocess.run([str(exe),tmp],text=True,capture_output=True)if compile_result.returncode==0 else None
        report={'status':'PASS'if run and run.returncode==0 else 'PRODUCT_FAIL','scope':'production MQL store control flow; host SQLite+SHA256 API adapters','native':'NOT_RUN','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[CORE,STORE]},'compiler_log':compile_result.stdout+compile_result.stderr,'output':run.stdout+run.stderr if run else''}
        if args.evidence_dir:
            out=Path(args.evidence_dir);out.mkdir(parents=True,exist_ok=True);(out/'fibo-store-runtime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())

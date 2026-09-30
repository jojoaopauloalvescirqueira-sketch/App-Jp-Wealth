#!/usr/bin/env python3
"""Replay production diagnostics against real SQLite and synthetic file/clock APIs.

The MQL statements, transaction/retention logic, binding order and checksum
serialization are executed unchanged. The host bridge is not native MT5 proof.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from leverage_reliability_test import presentation_runtime
from leverage_source import expanded_source

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"

SHIM = r'''
#include <algorithm>
#include <climits>
#include <cstdint>
#include <cmath>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sqlite3.h>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using string=std::string;using ushort=unsigned short;using ulong=unsigned long;
bool MathIsValidNumber(double value){return std::isfinite(value);}
double MathFloor(double value){return std::floor(value);}
long TimeGMT(){return 10000000;}
string StringSubstr(const string&value,int start,int count){return value.substr(start,count);}
std::map<string,double> terminal_globals;
bool GlobalVariableCheck(const string&key){return terminal_globals.count(key);}
bool GlobalVariableTemp(const string&key){terminal_globals.emplace(key,0);return true;}
bool GlobalVariableGet(const string&key,double&value){if(!terminal_globals.count(key))return false;value=terminal_globals.at(key);return true;}
bool GlobalVariableSetOnCondition(const string&key,double value,double expected){
 if(!terminal_globals.count(key)||terminal_globals.at(key)!=expected)return false;terminal_globals[key]=value;return true;}
long GlobalVariableSet(const string&key,double value){terminal_globals[key]=value;return 1;}
bool GlobalVariableDel(const string&key){return terminal_globals.erase(key);}
constexpr int INVALID_HANDLE=-1,ERR_DATABASE_NO_MORE_DATA=5126;
constexpr int FILE_READ=1,FILE_WRITE=2,FILE_BIN=4,FILE_SHARE_READ=8,FILE_SHARE_WRITE=16;
constexpr int DATABASE_OPEN_READONLY=1,DATABASE_OPEN_READWRITE=2,DATABASE_OPEN_CREATE=4;
int last_error=0,next_id=100;bool fail_insert=false,fail_commit=false,fail_readback=false;
std::map<int,sqlite3*> databases;std::map<int,sqlite3_stmt*> queries;std::map<int,string> query_sql;
std::map<int,int> files;string sandbox;
string local_path(string value){std::replace(value.begin(),value.end(),'\\','/');return sandbox+"/"+value;}
int StringLen(const string& value){return (int)value.size();}
ushort StringGetCharacter(const string& value,int index){return (ushort)value.at(index);}
int StringFind(const string& value,const string& needle){auto p=value.find(needle);return p==string::npos?-1:(int)p;}
string IntegerToString(long value){return std::to_string(value);}
void ResetLastError(){last_error=0;}int GetLastError(){return last_error;}
bool JPWRaizNFolderValid(const string& folder){return folder.find("..") == string::npos && folder.find(':')==string::npos&&folder.find('/')==string::npos&&folder.back()=='\\';}
bool JPWRaizNIsHash(const string& value){return value.size()==64&&value.find_first_not_of("0123456789abcdef")==string::npos;}
bool JPWRaizNHash(const string& value,string& hash){unsigned char bytes[32];
#ifdef __APPLE__
 CC_SHA256(value.data(),(CC_LONG)value.size(),bytes);
#else
 SHA256((const unsigned char*)value.data(),value.size(),bytes);
#endif
 std::ostringstream out;for(unsigned char byte:bytes)out<<std::hex<<std::setw(2)<<std::setfill('0')<<(int)byte;hash=out.str();return true;}
bool FileIsExist(const string& path){return std::filesystem::exists(local_path(path));}
bool FolderCreate(const string& path){std::error_code ec;std::filesystem::create_directories(local_path(path),ec);return !ec;}
int FileOpen(const string& path,int flags){int fd=open(local_path(path).c_str(),(flags&FILE_WRITE)?O_RDWR|O_CREAT:O_RDONLY,0600);
 if(fd<0)return INVALID_HANDLE;
 if(!(flags&(FILE_SHARE_READ|FILE_SHARE_WRITE))&&flock(fd,LOCK_EX|LOCK_NB)!=0){close(fd);return INVALID_HANDLE;}
 int id=next_id++;files[id]=fd;return id;}
ulong FileSize(int id){struct stat st{};return fstat(files.at(id),&st)==0?(ulong)st.st_size:ULONG_MAX;}
void FileClose(int id){if(files.count(id)){close(files[id]);files.erase(id);}}
int DatabaseOpen(const string& path,int flags){sqlite3* db=nullptr;int mode=(flags&DATABASE_OPEN_READONLY)?SQLITE_OPEN_READONLY:SQLITE_OPEN_READWRITE;
 if(flags&DATABASE_OPEN_CREATE)mode|=SQLITE_OPEN_CREATE;
 if(sqlite3_open_v2(local_path(path).c_str(),&db,mode,nullptr)!=SQLITE_OK){if(db)sqlite3_close(db);return INVALID_HANDLE;}
 int id=next_id++;databases[id]=db;return id;}
void DatabaseClose(int id){if(databases.count(id)){sqlite3_close(databases[id]);databases.erase(id);}}
bool DatabaseExecute(int id,const string& sql){return sqlite3_exec(databases.at(id),sql.c_str(),nullptr,nullptr,nullptr)==SQLITE_OK;}
bool DatabaseTransactionBegin(int id){return DatabaseExecute(id,"BEGIN");}
bool DatabaseTransactionCommit(int id){return !fail_commit&&DatabaseExecute(id,"COMMIT");}
bool DatabaseTransactionRollback(int id){return DatabaseExecute(id,"ROLLBACK");}
int DatabasePrepare(int id,const string& sql){sqlite3_stmt* q=nullptr;
 if((fail_insert&&(sql.find("INSERT INTO diag_events")!=string::npos||sql.find("UPDATE diag_events")!=string::npos))||
    (fail_readback&&sql.find("WHERE id=?1")!=string::npos))return INVALID_HANDLE;
 if(sqlite3_prepare_v2(databases.at(id),sql.c_str(),-1,&q,nullptr)!=SQLITE_OK)return INVALID_HANDLE;
 int key=next_id++;queries[key]=q;query_sql[key]=sql;return key;}
void DatabaseFinalize(int id){if(queries.count(id)){sqlite3_finalize(queries[id]);queries.erase(id);query_sql.erase(id);}}
bool DatabaseBind(int id,int index,const string& value){return sqlite3_bind_text(queries.at(id),index+1,value.c_str(),-1,SQLITE_TRANSIENT)==SQLITE_OK;}
bool DatabaseBind(int id,int index,long value){return sqlite3_bind_int64(queries.at(id),index+1,value)==SQLITE_OK;}
bool DatabaseRead(int id){int status=sqlite3_step(queries.at(id));last_error=status==SQLITE_DONE?ERR_DATABASE_NO_MORE_DATA:(status==SQLITE_ROW?0:status);return status==SQLITE_ROW;}
bool DatabaseColumnLong(int id,int index,long& value){value=(long)sqlite3_column_int64(queries.at(id),index);return true;}
bool DatabaseColumnText(int id,int index,string& value){const unsigned char* data=sqlite3_column_text(queries.at(id),index);if(!data)return false;value=(const char*)data;return true;}
template<class T>bool DatabaseReadBind(int id,T& e){if(!DatabaseRead(id))return false;auto q=queries.at(id);
 e.id=sqlite3_column_int64(q,0);DatabaseColumnText(id,1,e.context_key);e.component=sqlite3_column_int(q,2);
 e.code=sqlite3_column_int(q,3);e.sample_id=sqlite3_column_int64(q,4);e.first_utc=sqlite3_column_int64(q,5);
 e.last_utc=sqlite3_column_int64(q,6);e.mono_ms=sqlite3_column_int64(q,7);e.repetitions=sqlite3_column_int64(q,8);
 return DatabaseColumnText(id,9,e.product_version)&&DatabaseColumnText(id,10,e.calculation_version)&&
        DatabaseColumnText(id,11,e.build_id)&&DatabaseColumnText(id,12,e.checksum);}
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const char* why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<'\n';}}
long scalar(const string& folder,const string& sql){int db=DatabaseOpen(folder+"events_v1.sqlite",DATABASE_OPEN_READWRITE);long value=-1;
 if(db!=INVALID_HANDLE){JPWDiagScalar(db,sql,value);DatabaseClose(db);}return value;}
void mutate(const string& folder,const string& sql){int db=DatabaseOpen(folder+"events_v1.sqlite",DATABASE_OPEN_READWRITE);check(db!=INVALID_HANDLE&&DatabaseExecute(db,sql),"synthetic mutation applied");DatabaseClose(db);}
int main(int argc,char** argv){sandbox=argv[1];string context(64,'a'),other(64,'b'),reason;
 string folder=string(JPW_DIAG_FOLDER)+"Synthetic\\replay\\";
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_START,1,10000000,1000,reason,folder)==JPW_STORE_VALID,"first event commits and validates checksum");
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_START,2,10000030,2000,reason,folder)==JPW_STORE_VALID&&
       scalar(folder,"SELECT COUNT(*) FROM diag_events")==1&&scalar(folder,"SELECT repetitions FROM diag_events")==2,
       "same essential event coalesces within 60s without raw samples");
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_QUEUE_OVERFLOW,3,10000031,3000,reason,folder)==JPW_STORE_VALID&&
       scalar(folder,"SELECT COUNT(*) FROM diag_events")==2,"changed event records durable gap");
 check(JPWDiagCreatesCoverageGap(JPW_DIAG_QUEUE_OVERFLOW)&&JPWDiagCreatesCoverageGap(JPW_DIAG_RETRY_EXHAUSTED)&&
       !JPWDiagCreatesCoverageGap(JPW_DIAG_CAPTURE_RESUMED),"capture resumed is not proof of complete coverage");
 check(JPWDiagRecordAt(other,JPW_DIAG_OBSERVER,JPW_DIAG_QUEUE_OVERFLOW,4,10000032,4000,reason,folder)==JPW_STORE_VALID&&
       scalar(folder,"SELECT COUNT(*) FROM diag_events")==3,"different opaque context is not coalesced");
 long count=scalar(folder,"SELECT COUNT(*) FROM diag_events");
 fail_insert=true;
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_RETRY_EXHAUSTED,5,10000033,5000,reason,folder)==JPW_STORE_IO_ERROR,
       "failed SQL append is explicitly unavailable");fail_insert=false;
 check(scalar(folder,"SELECT COUNT(*) FROM diag_events")==count,"failed append rolls back");
 fail_readback=true;
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_RETRY_EXHAUSTED,5,10000033,5000,reason,folder)==JPW_STORE_IO_ERROR,
       "failed readback is not claimed durable");fail_readback=false;
 check(scalar(folder,"SELECT COUNT(*) FROM diag_events")==count,"readback failure rolls back serialized row");
 fail_commit=true;
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_RETRY_EXHAUSTED,5,10000033,5000,reason,folder)==JPW_STORE_IO_ERROR,
       "failed commit is not claimed durable");fail_commit=false;
 check(scalar(folder,"SELECT COUNT(*) FROM diag_events")==count,"commit failure rolls back");
 int held=FileOpen(folder+"events_v1.lock",FILE_READ|FILE_WRITE|FILE_BIN);
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_RETRY_EXHAUSTED,5,10000033,5000,reason,folder)==JPW_STORE_BUSY,
       "busy store returns immediately without consuming financial state");FileClose(held);
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_CAPTURE_RESUMED,5,10000090,5000,reason,folder)==JPW_STORE_VALID,
       "new event can follow transient failures");
 mutate(folder,"UPDATE diag_events SET checksum='corrupt' WHERE context_key='"+context+"'");
 count=scalar(folder,"SELECT COUNT(*) FROM diag_events");
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_END,6,10000100,6000,reason,folder)==JPW_STORE_CORRUPT&&
       scalar(folder,"SELECT COUNT(*) FROM diag_events")==count,"corrupt prior row is preserved and append refused");
 string retention=string(JPW_DIAG_FOLDER)+"Synthetic\\retention\\";
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_START,1,1,0,reason,retention)==JPW_STORE_VALID&&
       JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_END,2,JPW_DIAG_RETENTION_SECONDS+2,1,reason,retention)==JPW_STORE_VALID&&
       scalar(retention,"SELECT COUNT(*) FROM diag_events")==1,"30-day rotation only retains in-range events");
 string foreign=string(JPW_DIAG_FOLDER)+"Synthetic\\foreign\\";FolderCreate(foreign);
 int db=DatabaseOpen(foreign+"events_v1.sqlite",DATABASE_OPEN_READWRITE|DATABASE_OPEN_CREATE);
 check(DatabaseExecute(db,"CREATE VIEW sqliteXforeign AS SELECT 1"),"foreign view fixture");DatabaseClose(db);
 int lock=INVALID_HANDLE;db=INVALID_HANDLE;
 check(JPWDiagOpen(foreign,true,db,lock,reason)!=JPW_STORE_VALID,"unknown preexisting view cannot be overwritten as an empty DB");
 JPWDiagClose(db,lock);
 check(scalar(foreign,"SELECT COUNT(*) FROM sqlite_master WHERE name='diag_events'")==0,"foreign schema remains untouched");
 string cap=string(JPW_DIAG_FOLDER)+"Synthetic\\cap\\";
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_START,1,10000000,1,reason,cap)==JPW_STORE_VALID,"cap fixture creates exact schema");
 mutate(cap,"DELETE FROM diag_events");
 mutate(cap,"WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<8192) INSERT INTO diag_events SELECT x,'"+other+"',2,1,1,10000000,10000000,1,1,'1.10.0','1.9.0','synthetic','filler' FROM n");
 check(JPWDiagRecordAt(context,JPW_DIAG_OBSERVER,JPW_DIAG_SESSION_START,2,10000001,2,reason,cap)==JPW_STORE_VALID&&
       scalar(cap,"SELECT COUNT(*) FROM diag_events")<=JPW_DIAG_MAX_ROWS,"row cap rotates a bounded batch before append");
 check(!JPWDiagEventValid(0,JPW_DIAG_SESSION_START,1,100,1)&&!JPWDiagEventValid(1,99,1,100,1)&&
       !JPWDiagEventValid(1,1,-1,100,1),"unknown codes and invalid sample IDs rejected");
 check(!JPWDiagCanCoalesce(1,1,context,99,1,1,context,100),"clock regression cannot merge events");
 JPWDiagTiming timing{};JPWDiagTimingRecord(timing,40,false);JPWDiagTimingRecord(timing,600,true);JPWDiagTimingRecord(timing,-1,true);
 check(timing.cycles==2&&timing.deferred==1&&timing.max_duration_ms==600,"timing records measured cycles and deferrals");
 check(databases.empty()&&queries.empty()&&files.empty(),"all read/write/failure paths release handles");
 // Linked replay: accepted production sample -> real SQLite -> pure renderer
 // -> failed write/invalid presentation -> recovery -> fresh read connection.
 string linked=string(JPW_DIAG_FOLDER)+"Synthetic\\linked\\";
 g_sample_context=context;g_panel_prefix="synthetic";g_panel_value="2.50x";
 check(JPWSampleAccept(g_metric_samples[0],g_collection_sequence,context,2.5,true,"x",1,
       JPW_SAMPLE_CONFIRMED,"terminal",10000000,10000000000,1000)&&
       JPWDiagRecordAt(context,JPW_DIAG_INDICATOR,JPW_DIAG_QUALITY_CHANGED,g_collection_sequence,
                      10000000,1000,reason,linked)==JPW_STORE_VALID,"linked accepted sample persists its exact identity");
 for(int i=0;i<10;i++){host_now+=100;JPWRender("ignored","redraw");}
 check(g_collection_sequence==1&&g_cockpit_snapshot.metric[0].sample.id==1&&
       g_cockpit_snapshot.metric[0].value=="2.50x"&&scalar(linked,"SELECT COUNT(*) FROM diag_events")==1,
       "ten production redraws preserve sample identity and create no SQLite events");
 JPWSampleInvalidate(g_metric_samples[0],JPW_SAMPLE_UNAVAILABLE);JPWRender("","failed observation");
 fail_insert=true;
 check(JPWDiagRecordAt(context,JPW_DIAG_INDICATOR,JPW_DIAG_DATA_UNAVAILABLE,1,10000001,2000,reason,linked)==JPW_STORE_IO_ERROR&&
       g_cockpit_snapshot.metric[0].quality==JPW_VIEW_NA&&g_cockpit_snapshot.metric[0].value=="N/A"&&
       scalar(linked,"SELECT COUNT(*) FROM diag_events")==1,
       "failed observation removes current value while refused event leaves no false durable row");
 fail_insert=false;
 check(JPWDiagRecordAt(context,JPW_DIAG_INDICATOR,JPW_DIAG_WRITE_FAILED,1,10000002,2100,reason,linked)==JPW_STORE_VALID&&
       JPWSampleAccept(g_metric_samples[0],g_collection_sequence,context,2.75,true,"x",1,
           JPW_SAMPLE_CONFIRMED,"terminal",10000003,10000003000,2200)&&
       JPWDiagRecordAt(context,JPW_DIAG_INDICATOR,JPW_DIAG_CAPTURE_RESUMED,2,10000003,2200,reason,linked)==JPW_STORE_VALID,
       "recovery retains a write-failure gap and accepts a distinct sample");
 host_now=2300;g_panel_value="2.75x";JPWRender("","recovered");
 check(g_cockpit_snapshot.metric[0].quality==JPW_VIEW_CURRENT&&g_cockpit_snapshot.metric[0].sample.id==2&&
       scalar(linked,"SELECT COUNT(*) FROM diag_events")==3,"recovered display is bound to the new accepted sample");
 db=INVALID_HANDLE;lock=INVALID_HANDLE;
 bool reopened=JPWDiagOpen(linked,false,db,lock,reason)==JPW_STORE_VALID;
 int fresh_query=reopened?DatabasePrepare(db,"SELECT "+JPW_DIAG_SELECT+" FROM diag_events WHERE code=6"):INVALID_HANDLE;
 JPWDiagEvent persisted_gap;
 check(fresh_query!=INVALID_HANDLE&&JPWDiagRead(fresh_query,persisted_gap)==JPW_STORE_VALID&&
       persisted_gap.sample_id==1&&persisted_gap.context_key==context,
       "fresh SQLite connection revalidates the retained gap and original identity checksum");
 if(fresh_query!=INVALID_HANDLE)DatabaseFinalize(fresh_query);JPWDiagClose(db,lock);
 check(databases.empty()&&queries.empty()&&files.empty(),"linked replay releases every reopened handle");
 std::cout<<"HOST_DIAGNOSTICS_SQLITE: "<<checks-failures<<" PASS / "<<failures<<" FAIL\n";
 return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("JPW_TEST_RESULT: ENVIRONMENT_ERROR")
        return 2
    paths = [INCLUDE / f"JPW_Alavancagem_{part}.mqh" for part in ("Version", "Store_Result", "Diagnostics_Core", "Diagnostics")]
    source = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    source = source[:source.index("JPWStoreResult JPWDiagRecord(const")]
    # The prefix is complete through RecordAt; close its original header guard.
    source += "\n#endif\n"
    source = re.sub(r"^\s*#include[^\n]*$", "", source, flags=re.MULTILINE)
    source = re.sub(r'^(#define\s+\w+\s+)("(?:[^"\\]|\\.)*")\s*$', r'\1string(\2)', source, flags=re.MULTILINE)
    print(json.dumps({"kind": "HOST_PRODUCTION_SQLITE_REPLAY", "source_sha256": {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}}, indent=2))
    indicator=expanded_source(ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5")
    samples=(INCLUDE / "JPW_Alavancagem_Samples.mqh").read_text()
    print("LINKED_REPLAY_INDICATOR_SHA256:",hashlib.sha256(indicator.encode()).hexdigest())
    runtime=presentation_runtime(indicator,samples)
    with tempfile.TemporaryDirectory(prefix="jpw-diagnostics-") as directory:
        path, binary = Path(directory) / "diagnostics.cpp", Path(directory) / "diagnostics"
        path.write_text(SHIM + source + runtime + MAIN, encoding="utf-8")
        command = [compiler, "-std=c++17", "-Wall", "-Wextra", str(path), "-lsqlite3", "-o", str(binary)]
        if sys.platform != "darwin":
            command.append("-lcrypto")
        for command in (command, [str(binary), str(Path(directory) / "files")]):
            result = subprocess.run(command, text=True, capture_output=True, timeout=60, check=False)
            print(result.stdout, end=""); print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    print("NATIVE_MT5_SQLITE_AND_LOCKS: NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

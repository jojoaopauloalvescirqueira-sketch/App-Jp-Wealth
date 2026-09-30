#!/usr/bin/env python3
"""Host execution of the distributed Raiz N config store and synthetic script.

The MQL function bodies and assertions are loaded from current sources. Only
metadata/includes, dynamic-array syntax, typed string macros and date literals
are translated.
MQL primitives use a compatibility layer and isolated files; this is NOT a
MetaEditor build, native MT5 execution, or proof of OS crash durability/locks.
The fixtures use ASCII identities/text, so native UTF-16/UTF-8 behavior is not
claimed. --evidence-dir preserves the generated apparatus and complete receipts.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
FILES = [
    MQL / "Include/JPWealth/JPW_Alavancagem_Core.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh",
    MQL / "Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
    MQL / "Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5",
]

SHIM = r'''
#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using string=std::string;
using uchar=unsigned char;
using ushort=unsigned short;
using uint=unsigned int;
using ulong=unsigned long;
using datetime=long;
constexpr int WHOLE_ARRAY=-1,CP_UTF8=65001,CRYPT_HASH_SHA256=1;
constexpr double EMPTY_VALUE=2147483647.0;
constexpr int INVALID_HANDLE=-1;
enum {SYMBOL_CALC_MODE_FOREX,SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE,
      SYMBOL_CALC_MODE_CFD,SYMBOL_CALC_MODE_CFDLEVERAGE,SYMBOL_CALC_MODE_CFDINDEX};
enum {POSITION_TYPE_BUY=0,POSITION_TYPE_SELL=1};
enum {FILE_READ=1,FILE_WRITE=2,FILE_BIN=4,FILE_REWRITE=8,
      FILE_SHARE_READ=16,FILE_SHARE_WRITE=32};
template<class T> int ArraySize(const std::vector<T>& v){return (int)v.size();}
template<class T> int ArrayResize(std::vector<T>& v,int n){
  if(n<0)return -1; try{v.resize(n);return n;}catch(...){return -1;}
}
bool MathIsValidNumber(double v){return std::isfinite(v);}
double MathAbs(double v){return std::abs(v);}
double MathSqrt(double v){return std::sqrt(v);}
int StringLen(const string& s){return (int)s.size();}
int StringFind(const string& s,const string& sub){auto p=s.find(sub);return p==s.npos?-1:(int)p;}
int StringCompare(const string& a,const string& b){return a.compare(b);}
int StringReplace(string& s,const string& a,const string& b){
  if(a.empty())return 0; int count=0;size_t p=0;
  while((p=s.find(a,p))!=s.npos){s.replace(p,a.size(),b);p+=b.size();++count;}return count;
}
void StringTrimLeft(string& s){while(!s.empty()&&std::isspace((uchar)s.front()))s.erase(s.begin());}
void StringTrimRight(string& s){while(!s.empty()&&std::isspace((uchar)s.back()))s.pop_back();}
void StringToUpper(string& s){for(char& c:s)c=(char)std::toupper((uchar)c);}
string StringSubstr(const string& s,int from,int count=-1){
  if(from<0||(size_t)from>s.size())return "";
  return s.substr((size_t)from,count<0?s.npos:(size_t)count);
}
ushort StringGetCharacter(const string& s,int n){return n>=0&&(size_t)n<s.size()?(uchar)s[n]:0;}
string IntegerToString(long n){return std::to_string(n);}
string DoubleToString(double n,int digits=8){
  std::ostringstream out;
  if(digits<0)out<<std::scientific<<std::setprecision(-digits);
  else out<<std::fixed<<std::setprecision(digits);
  out<<n;return out.str();
}
double StringToDouble(const string& s){try{return std::stod(s);}catch(...){return 0.;}}
long StringToInteger(const string& s){try{return std::stol(s);}catch(...){return 0;}}
template<class...T> string StringFormat(const char* f,T... args){
  char buffer[8192];std::snprintf(buffer,sizeof buffer,f,args...);return buffer;
}
template<class...T> void PrintFormat(const char* f,T... args){std::cout<<StringFormat(f,args...)<<'\n';}
template<class...T> void Print(T... args){(std::cout<<...<<args)<<'\n';}
int StringSplit(const string& s,ushort delimiter,std::vector<string>& out){
  out.clear();size_t start=0;
  while(true){size_t p=s.find((char)delimiter,start);
    out.push_back(s.substr(start,p==s.npos?s.npos:p-start));if(p==s.npos)break;start=p+1;}
  return (int)out.size();
}
int StringToCharArray(const string& s,std::vector<uchar>& out,int start=0,
                      int count=WHOLE_ARRAY,uint cp=CP_UTF8){
  if(start!=0||cp!=CP_UTF8)return 0;out.assign(s.begin(),s.end());out.push_back(0);
  if(count>=0&&(size_t)count<out.size())out.resize(count);return (int)out.size();
}
string CharArrayToString(const std::vector<uchar>& v,int start=0,
                         int count=WHOLE_ARRAY,uint cp=CP_UTF8){
  if(start<0||(size_t)start>v.size()||cp!=CP_UTF8)return "";
  size_t n=count<0?v.size()-start:std::min((size_t)count,v.size()-start);
  return string(v.begin()+start,v.begin()+start+n);
}
int CryptEncode(int method,const std::vector<uchar>& data,
                 const std::vector<uchar>& key,std::vector<uchar>& out){
  if(method!=CRYPT_HASH_SHA256||!key.empty())return 0;out.resize(32);
#ifdef __APPLE__
  CC_SHA256(data.data(),(CC_LONG)data.size(),out.data());
#else
  SHA256(data.data(),data.size(),out.data());
#endif
  return 32;
}
long ChartID(){return 12345;}
ulong GetTickCount64(){static ulong value=100000;return ++value;}
datetime TimeLocal(){return 1790679600;}
datetime TimeCurrent(){return 1790679600;}

namespace fs=std::filesystem;
fs::path file_root;
struct Handle{fs::path path;int flags;std::fstream stream;};
std::map<int,std::unique_ptr<Handle>> handles;
int next_handle=1;
bool inject_short_write=false,inject_move_failure=false;
bool inject_post_move_readback_failure=false;
fs::path fail_next_read_of;
int post_move_readback_failures=0;
fs::path LocalPath(string name){
  for(char& c:name)if(c=='\\')c='/';fs::path p(name);
  if(p.is_absolute())throw std::runtime_error("absolute MQL path refused");
  for(const auto& part:p)if(part=="..")throw std::runtime_error("path traversal refused");
  return file_root/p;
}
int FileOpen(const string& name,int flags){
  const fs::path path=LocalPath(name);
  // The rename has already succeeded: fail only the first destination read.
  // Temporary write/read verification and the prior active slot are untouched.
  if((flags&FILE_READ)&&!fail_next_read_of.empty()&&path==fail_next_read_of){
    fail_next_read_of.clear();++post_move_readback_failures;
    Print("INJECTED_FAULT: post-FileMove destination readback FileOpen refused");
    return INVALID_HANDLE;
  }
  for(const auto& entry:handles)if(entry.second->path==path){const int old=entry.second->flags;
    if((flags&FILE_WRITE)&&!(old&FILE_SHARE_WRITE))return INVALID_HANDLE;
    if((flags&FILE_READ)&&!(old&FILE_SHARE_READ))return INVALID_HANDLE;
    if((old&FILE_WRITE)&&!(flags&FILE_SHARE_WRITE))return INVALID_HANDLE;
    if((old&FILE_READ)&&!(flags&FILE_SHARE_READ))return INVALID_HANDLE;
  }
  std::error_code error;
  if(flags&FILE_WRITE)fs::create_directories(path.parent_path(),error);
  if(error||fs::is_directory(path))return INVALID_HANDLE;
  auto handle=std::make_unique<Handle>();handle->path=path;handle->flags=flags;
  auto mode=std::ios::binary;
  if(flags&FILE_READ)mode|=std::ios::in;
  if(flags&FILE_WRITE)mode|=std::ios::out;
  if((flags&FILE_WRITE)&&!(flags&FILE_READ))mode|=std::ios::trunc;
  if((flags&(FILE_READ|FILE_WRITE))==(FILE_READ|FILE_WRITE)&&!fs::exists(path)){
    std::ofstream create(path,std::ios::binary);if(!create)return INVALID_HANDLE;
  }
  handle->stream.open(path,mode);if(!handle->stream)return INVALID_HANDLE;
  int id=next_handle++;handles.emplace(id,std::move(handle));return id;
}
void FileClose(int handle){handles.erase(handle);}
void FileFlush(int handle){auto it=handles.find(handle);if(it!=handles.end())it->second->stream.flush();}
ulong FileSize(int handle){
  auto it=handles.find(handle);if(it==handles.end())return 0;
  std::error_code error;return fs::file_size(it->second->path,error);
}
uint FileReadArray(int handle,std::vector<uchar>& values,int start=0,int count=WHOLE_ARRAY){
  auto it=handles.find(handle);if(it==handles.end()||!(it->second->flags&FILE_READ))return 0;
  int n=count<0?(int)values.size()-start:count;
  if(n<0||start<0||(size_t)(start+n)>values.size())return 0;
  it->second->stream.read((char*)values.data()+start,n);return (uint)it->second->stream.gcount();
}
uint FileWriteArray(int handle,const std::vector<uchar>& values,int start=0,int count=WHOLE_ARRAY){
  auto it=handles.find(handle);if(it==handles.end()||!(it->second->flags&FILE_WRITE))return 0;
  int n=count<0?(int)values.size()-start:count;
  if(n<0||start<0||(size_t)(start+n)>values.size())return 0;
  if(inject_short_write){inject_short_write=false;n/=2;}
  it->second->stream.write((const char*)values.data()+start,n);
  return it->second->stream?(uint)n:0;
}
bool FileIsExist(const string& name,int common=0){
  if(common!=0)throw std::runtime_error("shared file area forbidden");
  std::error_code error;return fs::is_regular_file(LocalPath(name),error);
}
bool FileDelete(const string& name,int common=0){
  if(common!=0)throw std::runtime_error("shared file area forbidden");
  auto p=LocalPath(name);for(const auto& item:handles)if(item.second->path==p)return false;
  std::error_code error;return fs::remove(p,error)&&!error;
}
bool FileMove(const string& from,int common,const string& to,int flags){
  if(common!=0)throw std::runtime_error("shared file area forbidden");
  if(inject_move_failure){inject_move_failure=false;return false;}
  auto a=LocalPath(from),b=LocalPath(to);
  for(const auto& item:handles)if(item.second->path==a||item.second->path==b)return false;
  if(fs::exists(b)&&!(flags&FILE_REWRITE))return false;
  std::error_code error;fs::rename(a,b,error);
  if(!error&&inject_post_move_readback_failure){
    inject_post_move_readback_failure=false;fail_next_read_of=b;
  }
  return !error;
}
bool FolderCreate(const string& name,int common=0){
  if(common!=0)throw std::runtime_error("shared file area forbidden");
  std::error_code error;
  return fs::create_directories(LocalPath(name),error)||(!error&&fs::is_directory(LocalPath(name)));
}
'''

MAIN = r'''
void HostFaultTests(){
  const string folder=JPW_RAIZN_FOLDER+"SyntheticHostFaults\\";
  const string symbol="SYNTH.EURUSD";
  string key="",reason="",before="",after="";
  ConfigAssert(ConfigKey(993999,symbol,key),"host fault synthetic key");
  JPWRaizNConfig value,loaded;ConfigFixture(key,symbol,value);
  ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,0,value,reason)==JPW_RAIZN_VALID,
               "host fault baseline generation saved");
  const string base=JPWRaizNConfigBase(folder,key);
  ConfigAssert(JPWRaizNReadText(base+".a",before)==JPW_RAIZN_VALID,"host baseline bytes captured");
  value.n=44;
  inject_short_write=true;
  ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_short_write && value.generation==1,"short temp write is refused without success");
  ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.n==30 && loaded.generation==1 &&
               JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID && after==before,
               "short write leaves prior config readable and byte-identical");
  inject_move_failure=true;
  ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_move_failure && value.generation==1,"failed FileMove is refused without success");
  ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.n==30 && loaded.generation==1 &&
               JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID && after==before,
               "failed move leaves prior config readable and byte-identical");
  string caller_before="",caller_after="";
  ConfigAssert(JPWRaizNConfigEncode(value,caller_before),"post-move fault caller captured");
  inject_post_move_readback_failure=true;
  ConfigAssert(JPWRaizNConfigSave(folder,key,symbol,1,value,reason)==JPW_RAIZN_IO_ERROR &&
               !inject_post_move_readback_failure && fail_next_read_of.empty() &&
               post_move_readback_failures==1,
               "successful move followed by failed destination readback reports IO_ERROR");
  ConfigAssert(JPWRaizNConfigEncode(value,caller_after)&&caller_after==caller_before &&
               value.generation==1,"uncertain post-move outcome leaves caller object unmutated");
  ConfigAssert(JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID && after==before,
               "uncertain post-move outcome preserves prior slot bytes");
  ConfigAssert(handles.empty(),"post-move readback error releases the exclusive lock");
  ConfigAssert(JPWRaizNConfigLoad(folder,key,symbol,loaded,reason)==JPW_RAIZN_VALID &&
               loaded.n==44 && loaded.generation==2,
               "later successful load can activate new generation despite earlier IO_ERROR");
  ConfigAssert(JPWRaizNReadText(base+".a",after)==JPW_RAIZN_VALID && after==before,
               "new generation reload does not erase the preserved prior slot");
  Print("POST_MOVE_READBACK_FAULT: IO_ERROR; caller generation=",value.generation,
        "; later loaded generation=",loaded.generation,"; prior slot bytes preserved");
  bool temporaries=false;
  for(const auto& entry:fs::recursive_directory_iterator(file_root))
    if(entry.path().extension()==".tmp")temporaries=true;
  ConfigAssert(!temporaries&&handles.empty(),"fault branches release handles and clean only synthetic temp files");
}
int main(int argc,char** argv){
  if(argc!=2)return 2;
  file_root=fs::path(argv[1]);fs::create_directories(file_root);
  string hash="";
  if(!JPWRaizNHash("abc",hash)||hash!="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"){
    std::cerr<<"TEST_HARNESS_FAIL: SHA256 compatibility primitive\n";return 2;
  }
  OnStart();
  HostFaultTests();
  Print("HOST_CONFIG: ",g_cfg_pass," PASS / ",g_cfg_fail," FAIL");
  Print("MQL5_NATIVE_COMPILATION: NOT_RUN; MQL5_NATIVE_EXECUTION: NOT_RUN");
  return g_cfg_fail==0?0:1;
}
'''


def translate(source: str) -> str:
    source = re.sub(r"^\s*#(?:include|property)\b[^\n]*", "", source, flags=re.MULTILINE)
    source = re.sub(r'^(#define\s+\w+\s+)("(?:[^"\\]|\\.)*")\s*$', r'\1string(\2)',
                    source, flags=re.MULTILINE)
    source = re.sub(r"\b(\w+)\s+&(\w+)\[\]", r"std::vector<\1> &\2", source)
    source = re.sub(r"\b(\w+)\s+(\w+)\[\];", r"std::vector<\1> \2;", source)

    def date_literal(match: re.Match) -> str:
        value = datetime.strptime(match[1], "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return str(int(value.timestamp()))

    return re.sub(r"D'([0-9.]+ [0-9:]+)'", date_literal, source)


def run(output: Path | None) -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: no existing C++ compiler; native MT5 NOT_RUN")
        return 2
    identity = {
        "test": "leverage_config",
        "kind": "HOST_SYNTHETIC_NOT_MQL5",
        "compiler": compiler,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES},
        "limitations": "Synthetic file primitives and ASCII fixtures; no native MT5, interprocess OS lock, Unicode codec or crash durability evidence.",
    }
    print(json.dumps(identity, indent=2))
    receipts = []
    if output:
        output.mkdir(parents=True, exist_ok=False)
        (output / "source-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="jpw-raizn-config-synthetic-") as tmp:
        source = Path(tmp) / "config.cpp"
        binary = Path(tmp) / "config"
        source.write_text(SHIM + "\n" + "\n".join(translate(p.read_text()) for p in FILES) + "\n" + MAIN)
        if output:
            shutil.copy2(source, output / "config.cpp")
        commands = [
            [compiler, "--version"],
            [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wno-unused-parameter",
             "-Wno-deprecated-declarations", str(source), "-o", str(binary)] +
            ([] if sys.platform == "darwin" else ["-lcrypto"]),
            [str(binary), str(Path(tmp) / "files")],
        ]
        for index, command in enumerate(commands):
            result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            receipts.append({"command": command, "exit_code": result.returncode})
            if output:
                (output / f"{index}-stdout.txt").write_text(result.stdout)
                (output / f"{index}-stderr.txt").write_text(result.stderr)
                (output / "commands.json").write_text(json.dumps(receipts, indent=2) + "\n")
            if result.returncode:
                print(f"HOST_STAGE_{index}: FAILURE; EXIT_CODE: {result.returncode}; native MT5 NOT_RUN")
                return result.returncode
        print("HOST_CONFIG_RESULT: PASS; EXIT_CODE: 0")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.evidence_dir))

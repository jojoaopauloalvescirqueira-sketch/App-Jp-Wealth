#!/usr/bin/env python3
"""Independent production-body scheduler/diagnostic test; not native MT5 QA."""
import argparse, hashlib, json, re, subprocess, tempfile, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
PRE=r'''
#include <algorithm>
#include <climits>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif
using string=std::string; using uchar=unsigned char; using ushort=unsigned short; using ulong=unsigned long;
constexpr int INVALID_HANDLE=-1,WHOLE_ARRAY=-1,CP_UTF8=65001;
constexpr int FILE_READ=1,FILE_WRITE=2,FILE_BIN=4,FILE_SHARE_READ=8,FILE_REWRITE=16;
template<class T> int ArrayResize(std::vector<T>& a,int n){if(n<0)return -1;a.resize(n);return n;}
int StringLen(const string& s){return (int)s.size();}
int StringToCharArray(const string& s,std::vector<uchar>& b,int,int,int){b.assign(s.begin(),s.end());b.push_back(0);return (int)b.size();}
string CharArrayToString(const std::vector<uchar>& b,int p,int n,int){return string(b.begin()+p,b.begin()+p+n);}
ushort StringGetCharacter(const string& s,int n){return (uchar)s.at(n);}
string StringSubstr(const string& s,int p,int n=-1){return s.substr(p,n<0?string::npos:(size_t)n);}
string StringFormat(const char* f,int n){char b[80];std::snprintf(b,sizeof(b),f,n);return b;}
long StringToInteger(const string& s){try{return std::stol(s);}catch(...){return 0;}}
string IntegerToString(long n){return std::to_string(n);}
int StringSplit(const string& s,ushort sep,std::vector<string>& out){out.clear();size_t p=0,n;while((n=s.find((char)sep,p))!=string::npos){out.push_back(s.substr(p,n-p));p=n+1;}out.push_back(s.substr(p));return out.size();}
bool JPWRaizNIsHash(const string& s){return s.size()==64&&s.find_first_not_of("0123456789abcdef")==string::npos;}
bool JPWRaizNHash(const string& s,string& out){uchar b[32];
#ifdef __APPLE__
CC_SHA256(s.data(),(CC_LONG)s.size(),b);
#else
SHA256((const unsigned char*)s.data(),s.size(),b);
#endif
out="";for(int i=0;i<32;i++)out+=StringFormat("%02x",b[i]);return true;}
ulong host_now=1000; std::map<string,double> host_leases;
ulong GetTickCount64(){return host_now;}
bool GlobalVariableGet(const string& s,double& out){auto i=host_leases.find(s);if(i==host_leases.end())return false;out=i->second;return true;}
string host_root; int host_handle=0;std::map<int,std::fstream*> host_files;
string host_path(string p){std::replace(p.begin(),p.end(),'\\','/');return host_root+"/"+p;}
bool FolderCreate(const string& s){std::error_code e;std::filesystem::create_directories(host_path(s),e);return !e;}
int FileOpen(const string& p,int flags){auto f=new std::fstream(host_path(p),std::ios::binary|((flags&FILE_WRITE)?(std::ios::out|std::ios::trunc):std::ios::in));if(!*f){delete f;return -1;}host_files[++host_handle]=f;return host_handle;}
ulong FileSize(int h){auto f=host_files.at(h);auto p=f->tellg();f->seekg(0,std::ios::end);auto n=f->tellg();f->seekg(p);return n;}
uint FileReadArray(int h,std::vector<uchar>& b,int p,int n){auto f=host_files.at(h);f->read((char*)&b.at(p),n);return f->gcount();}
uint FileWriteArray(int h,const std::vector<uchar>& b,int p,int n){auto f=host_files.at(h);f->write((const char*)&b.at(p),n);return *f?n:0;}
void FileFlush(int h){host_files.at(h)->flush();}
void FileClose(int h){host_files.at(h)->close();delete host_files.at(h);host_files.erase(h);}
bool FileMove(const string& a,int,const string& b,int){std::error_code e;std::filesystem::rename(host_path(a),host_path(b),e);return !e;}
int assertions=0;void CHECK(bool b,const string& label){assertions++;if(!b)throw std::runtime_error(label);}
'''
TEST=r'''
int main(int argc,char** argv){host_root=argv[1];try{
JPWMonitorScheduler s;JPWMonitorSchedulerReset(s);CHECK(s.cycles==0&&s.cursor==2,"reset deterministic");
JPWMonitorSchedulerBegin(s,15);CHECK(JPWMonitorSchedulerNext(s,100,100,15,0)==0,"stops priority");
JPWMonitorSchedulerServiced(s,0,110);CHECK(JPWMonitorSchedulerNext(s,100,110,15,1)==1,"history second");
CHECK(JPWMonitorSchedulerNext(s,100,600,15,0)==-1,"500ms exact budget no dispatch");
CHECK(JPWMonitorSchedulerNext(s,100,99,15,0)==-1,"clock rollback no dispatch");
JPWMonitorSchedulerFinish(s,100,601,15,1);CHECK(s.overruns==1&&s.deferred_cycles==1,"overrun measured not hidden");
JPWMonitorSchedulerReset(s);int served[4]={0,0,0,0};
for(int round=0;round<24;round++){JPWMonitorSchedulerBegin(s,15);int i=JPWMonitorSchedulerNext(s,100,100,15,0);CHECK(i>=0,"finite priority work progresses");served[i]++;JPWMonitorSchedulerServiced(s,i,610);JPWMonitorSchedulerFinish(s,100,610,15,1<<i);}
for(int i=0;i<4;i++)CHECK(served[i]>=3,"accounting/reconstruction cannot be starved by long stops");
JPWMonitorSchedulerReset(s);for(int round=0;round<12;round++){JPWMonitorSchedulerBegin(s,12);int i=JPWMonitorSchedulerNext(s,100,100,12,0);served[i]++;JPWMonitorSchedulerServiced(s,i,105);CHECK(i>=2,"disabled modules skipped");}
JPWMonitorSnapshot v;JPWMonitorSnapshotClear(v);v.account_key=string(64,'a');v.publisher_token=string(64,'b');v.build_id=string(64,'c');v.role="monitor";v.product_version="1.20.0";v.chart_id=99;v.active=true;v.heartbeat_utc=100;v.heartbeat_mono_ms=1000;
v.stop_risk.state=JPW_MONITOR_CURRENT;v.stop_risk.quality="Current";v.stop_risk.reason="ok";v.stop_risk.observed_utc=100;v.stop_risk.observed_mono_ms=1000;
v.ledger.state=JPW_MONITOR_PREPARING;v.ledger.quality="N/A";v.ledger.reason="preparing|50%";v.ledger.progress=50;
string raw=JPWMonitorStatusEncode(v),why;JPWMonitorSnapshot out;
CHECK(!raw.empty()&&JPWMonitorStatusDecode(raw,out),"codec round trip incl delimiter escaped");CHECK(out.ledger.reason==v.ledger.reason&&out.chart_id==99,"text chart state preserved");
CHECK(!JPWMonitorStatusDecode(raw+"junk",out),"checksum refuses tampering");
CHECK(!JPWMonitorStatusDecode("",out),"empty diagnostic refused");
host_leases[JPWMonitorLeaseName(v.publisher_token)]=1000;
CHECK(JPWMonitorWriteStatus(v,why),"atomic diagnostic publish host filesystem");
CHECK(JPWMonitorReadStatus(v.account_key,out,why)&&out.live&&out.stop_risk.state==JPW_MONITOR_CURRENT,"live presence plus current capture");
host_now=31000;CHECK(JPWMonitorReadStatus(v.account_key,out,why)&&out.live,"lease exact 30s boundary");
host_now=31001;CHECK(JPWMonitorReadStatus(v.account_key,out,why)&&!out.live&&out.stop_risk.state==JPW_MONITOR_HISTORICAL,"heartbeat stale => historical capture");
host_now=1000;host_leases.clear();CHECK(JPWMonitorReadStatus(v.account_key,out,why)&&!out.live,"old record never proves live owner");
host_leases[JPWMonitorLeaseName(v.publisher_token)]=1000;v.stop_risk.observed_mono_ms=1;v.heartbeat_mono_ms=1000;host_now=30001;
CHECK(JPWMonitorWriteStatus(v,why)&&JPWMonitorReadStatus(v.account_key,out,why)&&out.live&&out.stop_risk.state==JPW_MONITOR_CURRENT,"valid capture at own <=30s boundary");
host_now=31002;v.heartbeat_mono_ms=31002;host_leases[JPWMonitorLeaseName(v.publisher_token)]=31002;
CHECK(JPWMonitorWriteStatus(v,why)&&JPWMonitorReadStatus(v.account_key,out,why)&&out.live&&out.stop_risk.state==JPW_MONITOR_HISTORICAL,"current heartbeat cannot refresh old capture");
v.active=false;CHECK(JPWMonitorWriteStatus(v,why)&&JPWMonitorReadStatus(v.account_key,out,why)&&!out.live,"deinit inactive even valid lease");
v.active=true;host_now=10;CHECK(JPWMonitorReadStatus(v.account_key,out,why)&&!out.live,"monotonic reset not live");
CHECK(!JPWMonitorReadStatus(string(64,'d'),out,why),"account isolated no fallback");
std::ofstream(host_path(JPWMonitorStatusPath(v.account_key)))<<"broken";CHECK(!JPWMonitorReadStatus(v.account_key,out,why)&&!out.live,"corrupt diagnostic not reconstructed");
std::cout<<"MONITOR_JUDGE|PASS|"<<assertions<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<"PRODUCT_FAIL|"<<e.what()<<'\n';return 1;}}
'''
def translate(s):
    s=re.sub(r'^\s*#include.*$', '', s, flags=re.M)
    s=re.sub(r'\b(\w+)\s+&(\w+)\[\]',r'std::vector<\1> &\2',s)
    s=re.sub(r'\b(\w+)\s+(\w+)\[\]\s*;',r'std::vector<\1> \2;',s)
    return s.replace('JPW_MONITOR_FOLDER+"status_"','string(JPW_MONITOR_FOLDER)+"status_"')
def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,default=ROOT/"tools/.artifacts"/"core_monitor_judge.json");a=p.parse_args();compiler=shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("JPW_TEST_RESULT: ENVIRONMENT_ERROR");return 2
    files=[INC/'JPW_Genetrix_Monitor_Core.mqh',INC/'JPW_Genetrix_Monitor_Status.mqh',Path(__file__).resolve()]
    receipt={'scope':'production MQL function bodies, synthetic native seams, host filesystem; not MT5 GUI or native ABI','sources':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files},'native':'NOT_RUN'}
    with tempfile.TemporaryDirectory(prefix='core-monitor-judge-') as d:
        d=Path(d);cpp=d/'judge.cpp';binary=d/'judge';cpp.write_text(PRE+'\n'+translate(files[0].read_text())+'\n'+translate(files[1].read_text())+'\n'+TEST)
        build=subprocess.run([compiler,'-std=c++17','-Wno-deprecated-declarations',str(cpp),'-o',str(binary)]+([] if sys.platform=='darwin' else ['-lcrypto']),capture_output=True,text=True)
        receipt['compile_returncode']=build.returncode;receipt['compile_log']=build.stderr
        if not build.returncode:
            (d/'files').mkdir();run=subprocess.run([str(binary),str(d/'files')],capture_output=True,text=True);receipt.update(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,status='PASS' if run.returncode==0 else 'PRODUCT_FAIL')
        else:receipt.update(status='JUDGE_ERROR')
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

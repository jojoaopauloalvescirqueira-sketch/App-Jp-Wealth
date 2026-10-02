#!/usr/bin/env python3
"""Execute production MQL Fibo core under a C++ API shim; native != host."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Core.mqh'
SCRIPT=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5'
SHIM=r'''
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
using ushort=unsigned short;
template<class T> int ArrayResize(std::vector<T>& a,int n){if(n<0)return -1;a.resize(n);return n;}
template<class T> int ArraySize(const std::vector<T>& a){return (int)a.size();}
template<class T,size_t N> int ArraySize(const T (&)[N]){return (int)N;}
int StringLen(const string& s){return (int)s.size();}
int StringFind(const string& s,const string& sub,int pos=0){auto n=s.find(sub,pos);return n==string::npos?-1:(int)n;}
string StringSubstr(const string& s,int pos,int len=-1){return s.substr(pos,len<0?string::npos:(size_t)len);}
string IntegerToString(long n){return std::to_string(n);}
long StringToInteger(const string& s){char* end=nullptr;return std::strtol(s.c_str(),&end,10);}
double StringToDouble(const string& s){return std::strtod(s.c_str(),nullptr);}
string StringFormat(const char* fmt,double value){char buf[128];std::snprintf(buf,sizeof(buf),fmt,value);return buf;}
bool MathIsValidNumber(double x){return std::isfinite(x);}
double MathRound(double x){return std::round(x);}
double MathAbs(double x){return std::abs(x);}
template<class... T> void Print(const T&... x){(std::cout<<...<<x)<<"\n";}
'''
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');args=ap.parse_args()
    compiler=shutil.which('clang++') or shutil.which('g++')
    if not compiler: raise SystemExit('C++ compiler unavailable; NOT_RUN')
    core=CORE.read_text().replace('long opens[];', 'std::vector<long> opens;')
    script=re.sub(r'^#(?:property|include).*\n','',SCRIPT.read_text(),flags=re.M)
    code=SHIM+'\n'+core+'\n'+script+'\nint main(){OnStart();return jpw_ncf_failed ? 1:0;}\n'
    with tempfile.TemporaryDirectory(prefix='jpw-ncf-core-') as tmp:
        src=Path(tmp)/'core.cpp';exe=Path(tmp)/'core';src.write_text(code)
        compile_result=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror',str(src),'-o',str(exe)],text=True,capture_output=True)
        run=subprocess.run([str(exe)],text=True,capture_output=True) if compile_result.returncode==0 else None
        report={'status':'PASS' if run and run.returncode==0 else 'PRODUCT_FAIL','scope':'production MQL core via host API shim','native':'NOT_RUN','parity':'UNVERIFIED_NATIVE','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CORE,SCRIPT]},'compiler_log':compile_result.stdout+compile_result.stderr,'output':run.stdout+run.stderr if run else ''}
        if args.evidence_dir:
            dest=Path(args.evidence_dir);dest.mkdir(parents=True,exist_ok=True);(dest/'fibo-core.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())

#!/usr/bin/env python3
"""Exercise actual MQL capture/clone adapter through deterministic chart API seams.
Synthetic seams do not emulate native Fibo geometry and never unlock parity.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1];INC=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'
spec=importlib.util.spec_from_file_location('ct',ROOT/'tools/jpw_nocuda_fibo_test.py');ct=importlib.util.module_from_spec(spec);spec.loader.exec_module(ct)
SHIM=r'''
#include <map>
using datetime=long;
using ulong=unsigned long;
using ENUM_TIMEFRAMES=int;
enum ENUM_OBJECT_PROPERTY_INTEGER{OBJPROP_TYPE,OBJPROP_LEVELS,OBJPROP_CREATETIME,OBJPROP_TIME,OBJPROP_COLOR,OBJPROP_STYLE,OBJPROP_WIDTH,OBJPROP_RAY_LEFT,OBJPROP_RAY_RIGHT,OBJPROP_BACK,OBJPROP_HIDDEN,OBJPROP_SELECTABLE,OBJPROP_TIMEFRAMES,OBJPROP_LEVELCOLOR,OBJPROP_LEVELSTYLE,OBJPROP_LEVELWIDTH};
enum ENUM_OBJECT_PROPERTY_DOUBLE{OBJPROP_PRICE,OBJPROP_LEVELVALUE};
enum ENUM_OBJECT_PROPERTY_STRING{OBJPROP_LEVELTEXT};
#define OBJ_FIBOCHANNEL 77
#define OBJ_CHANNEL 44
struct FakeObject{std::map<std::pair<int,int>,long>ints;std::map<std::pair<int,int>,double>doubles;std::map<std::pair<int,int>,string>strings;};
std::map<string,FakeObject>objects;
std::vector<long> times;
int error=0,period=60,copy_count=0,mode=0;
string symbol="SYNTHETIC";unsigned long elapsed=0;
void ResetLastError(){error=0;}int GetLastError(){return error;}
unsigned long GetTickCount64(){if(mode==4)elapsed+=501;return elapsed;}
long TimeGMT(){return 1800000000;}
int ChartPeriod(long){return period;}string ChartSymbol(long){return symbol;}
int PeriodSeconds(int tf){return tf>0?3600:0;}
int ObjectFind(long,const string&n){return objects.count(n)?0:-1;}
int ObjectsTotal(long,int,int type){int n=0;for(auto&i:objects)if(i.second.ints[{OBJPROP_TYPE,0}]==type)n++;return n;}
string ObjectName(long,int index,int,int type){for(auto&i:objects)if(i.second.ints[{OBJPROP_TYPE,0}]==type&&index--==0)return i.first;return "";}
bool ObjectGetInteger(long,const string&n,ENUM_OBJECT_PROPERTY_INTEGER p,int i,long&v){if(!objects.count(n)){error=1;return false;}v=objects[n].ints[{p,i}];return true;}
bool ObjectGetDouble(long,const string&n,ENUM_OBJECT_PROPERTY_DOUBLE p,int i,double&v){if(!objects.count(n)){error=1;return false;}v=objects[n].doubles[{p,i}];return true;}
bool ObjectGetString(long,const string&n,ENUM_OBJECT_PROPERTY_STRING p,int i,string&v){if(!objects.count(n)){error=1;return false;}v=objects[n].strings[{p,i}];return true;}
bool ObjectSetInteger(long,const string&n,int p,int i,long v){if(!objects.count(n))return false;objects[n].ints[{p,i}]=v;return true;}
bool ObjectSetInteger(long c,const string&n,int p,long v){return ObjectSetInteger(c,n,p,0,v);}
bool ObjectSetDouble(long,const string&n,int p,int i,double v){if(!objects.count(n))return false;objects[n].doubles[{p,i}]=v;return true;}
bool ObjectSetString(long,const string&n,int p,int i,const string&v){if(!objects.count(n))return false;objects[n].strings[{p,i}]=v;return true;}
bool ObjectCreate(long,const string&n,int type,int,long t0,double p0,long t1,double p1,long t2,double p2){if(objects.count(n))return false;auto&o=objects[n];o.ints[{OBJPROP_TYPE,0}]=type;o.ints[{OBJPROP_CREATETIME,0}]=1799999000;o.ints[{OBJPROP_TIME,0}]=t0;o.ints[{OBJPROP_TIME,1}]=t1;o.ints[{OBJPROP_TIME,2}]=t2;o.doubles[{OBJPROP_PRICE,0}]=p0;o.doubles[{OBJPROP_PRICE,1}]=p1;o.doubles[{OBJPROP_PRICE,2}]=p2;return true;}
bool ObjectDelete(long,const string&n){return objects.erase(n)>0;}
double ObjectGetValueByTime(long,const string&,long,int){return 1.23;}
int iBarShift(const string&,int,long when,bool){for(int i=(int)times.size()-1;i>=0;i--)if(times[i]<=when)return (int)times.size()-1-i;return -1;}
template<class T>bool ArraySetAsSeries(std::vector<T>&,bool){return true;}
int CopyTime(const string&,int,int,int count,std::vector<long>&out){copy_count++;if(mode==3&&copy_count==1)return 0;if(mode==1&&copy_count==1)objects["native"].doubles[{OBJPROP_PRICE,1}]+=0.0001;if(mode==2&&copy_count==2)times[3]++;if(count>(int)times.size())return 0;out.assign(times.end()-count,times.end());return count;}
'''
TEST=r'''
int main(){JPWNCFSnapshot s,a;NCFFixture(s);times=s.opens;string reason;
NCFCheck(JPWNCFClone(0,"JPWNCF_seed",s,reason)==JPW_NCF_VALID,"clone exact properties");
objects["native"]=objects["JPWNCF_seed"];objects.erase("JPWNCF_seed");
std::vector<string>names;NCFCheck(JPWNCFCatalog(0,names)==1&&names[0]=="native","catalog native only");
NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_VALID,"capture bounded twice");
NCFCheck(a.anchor_time[0]==s.anchor_time[0]&&a.anchor_price[0]==s.anchor_price[0],"arbitrary anchor unchanged");
NCFCheck(a.levels[0].value==4&&a.levels[64].value==-4,"native level array preserved");
NCFCheck(a.source_created==1799999000,"creation identity read");
NCFCheck(JPWNCFClone(0,"JPWNCF_clone",a,reason)==JPW_NCF_VALID,"verified property readback");
NCFCheck(JPWNCFCatalog(0,names)==1,"managed clone excluded from catalog");
NCFCheck(JPWNCFClone(0,"native",a,reason)==JPW_NCF_CONFLICT,"source not overwritten");
period=15;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_CHANGED,"wrong TF suspends capture");
NCFCheck(JPWNCFClone(0,"JPWNCF_other",s,reason)==JPW_NCF_CHANGED,"wrong TF clone refused");period=60;
symbol="OTHER";NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_CHANGED,"symbol context refused");symbol=s.symbol;
mode=1;copy_count=0;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_CHANGED,"anchor changed between reads");
mode=2;copy_count=0;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_CHANGED,"history changed between reads");times=s.opens;
mode=3;copy_count=0;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_INVALID,"history incomplete");
mode=4;copy_count=0;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_CHANGED,"budget exceeded defers");mode=0;
objects["native"].ints[{OBJPROP_LEVELS,0}]=64;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_INVALID,"wrong grid count");
objects["native"].ints[{OBJPROP_LEVELS,0}]=65;
objects["native"].ints[{OBJPROP_TIME,1}]=times.back()+1;NCFCheck(JPWNCFCapture(0,"native",60,s.symbol,s.feed,a,reason)==JPW_NCF_INVALID,"undelimited future anchor refused");
Print("Terminal adapter: ",jpw_ncf_asserts," asserts; failures=",jpw_ncf_failed,"; native NOT_RUN");return jpw_ncf_failed?1:0;}
'''
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');args=ap.parse_args();compiler=shutil.which('clang++')or shutil.which('g++')
    core=ct.CORE.read_text().replace('long opens[];','std::vector<long> opens;');terminal=(INC/'JPW_NoCuda_Fibo_Terminal.mqh').read_text()
    terminal=re.sub(r'^#include.*\n','',terminal,flags=re.M).replace('string &names[]','std::vector<string> &names').replace('datetime times[];','std::vector<datetime> times;').replace('datetime verify[];','std::vector<datetime> verify;')
    fixture=re.sub(r'^#(?:include|property).*\n','',ct.SCRIPT.read_text(),flags=re.M)
    code=ct.SHIM+SHIM+core+terminal+fixture+TEST
    with tempfile.TemporaryDirectory(prefix='jpw-ncf-terminal-')as tmp:
        src=Path(tmp)/'terminal.cpp';src.write_text(code);exe=Path(tmp)/'terminal'
        compiled=subprocess.run([compiler,'-std=c++17','-Wall','-Wextra','-Werror',str(src),'-o',str(exe)],text=True,capture_output=True)
        run=subprocess.run([str(exe)],text=True,capture_output=True)if compiled.returncode==0 else None
        report={'status':'PASS'if run and run.returncode==0 else'PRODUCT_FAIL','scope':'actual production MQL terminal adapter; deterministic chart API seams','native':'NOT_RUN','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[ct.CORE,INC/'JPW_NoCuda_Fibo_Terminal.mqh']},'compiler_log':compiled.stdout+compiled.stderr,'output':run.stdout+run.stderr if run else''}
        if args.evidence_dir:
            dest=Path(args.evidence_dir);dest.mkdir(parents=True,exist_ok=True);(dest/'fibo-terminal.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())

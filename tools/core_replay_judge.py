#!/usr/bin/env python3
"""Independent replay differential and declared maximum-size numeric references."""
import argparse,hashlib,importlib.util,json,re,subprocess,tempfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'mt5/jpw-alavancagem-atual/MQL5'
spec=importlib.util.spec_from_file_location('legacyjudge',ROOT/'tools/jpw_genetrix_ledger_test.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
EXTRA=r'''
using ulong=unsigned long;ulong host_clock=1;
ulong GetTickCount64(){return host_clock++;}
template<class T,class U> int ArrayInitialize(std::vector<T>& a,U n){std::fill(a.begin(),a.end(),(T)n);return a.size();}
'''
TEST=r'''
void replay(std::vector<JPWLedgerDeal>& d,std::vector<JPWLedgerOrder>& o,std::vector<JPWLedgerPosition>& p,JPWLedgerView& v,std::vector<JPWLedgerCycle>& c){
CJPWLedgerReplay r;REQUIRE(r.Begin(d,o),"replay Begin");bool ready=false;int steps=0;
while(!ready){ulong start=GetTickCount64();REQUIRE(r.Step(d,o,start+100,ready),"replay Step "+r.reason);REQUIRE(++steps<20000,"replay bounded progress");}
REQUIRE(r.BeginLive(p),"replay BeginLive "+r.reason);ready=false;
while(!ready){ulong start=GetTickCount64();REQUIRE(r.LiveStep(p,v,start+100,ready),"replay LiveStep "+r.reason);REQUIRE(++steps<20000,"live bounded progress");}
c=r.cycles;
}
void equal(std::vector<JPWLedgerDeal> d,std::vector<JPWLedgerOrder> o,std::vector<JPWLedgerPosition> p,JPWLedgerView v,const string& label){
std::vector<JPWLedgerCycle> a,b;JPWLedgerView v2=v;string why;REQUIRE(JPWLedgerBuild(d,o,p,v,a,why),"legacy valid "+label+" "+why);replay(d,o,p,v2,b);
REQUIRE(a.size()==b.size(),"cycle count parity "+label);REQUIRE(v.costs_complete==v2.costs_complete,"cost coverage parity "+label);
for(size_t i=0;i<a.size();i++){string x=JPWLedgerEncodeCycle(a[i]),y=JPWLedgerEncodeCycle(b[i]);if(x!=y){std::cerr<<"DIFF "<<label<<" cycle="<<i<<"\nOLD "<<x<<"\nNEW "<<y<<'\n';}REQUIRE(x==y,"all encoded fields canonical parity "+label);}
}
unsigned int seed=0x1200;unsigned int rng(){seed=seed*1664525u+1013904223u;return seed;}
int main(int argc,char**argv){host_root=argv[1];try{
for(int n=0;n<=18;n++){std::vector<JPWLedgerDeal>d;std::vector<JPWLedgerOrder>o;std::vector<JPWLedgerPosition>p;JPWLedgerView v;string id=JPWLedgerTestFixture(n,d,o,p,v);equal(d,o,p,v,id);}
for(int n=0;n<300;n++){
std::vector<JPWLedgerDeal>d;std::vector<JPWLedgerOrder>o;std::vector<JPWLedgerPosition>p;JPWLedgerView v;JPWLedgerTestView(v,1000);long clock=1000,ticket=100,id=700;double vol=0;bool open=false;
for(int k=0;k<20;k++){clock+=(rng()%3);if(!open){id+=10;JPWLedgerTestDeal(d,ticket++,id,id,clock,1,0,.02,0,0,-.2,-.01);vol=.02;open=true;}else if(rng()%3==0){JPWLedgerTestDeal(d,ticket++,id+1,id,clock,-1,1,vol,((int)(rng()%21)-10)*.1,-.03,-.1,-.01);vol=0;open=false;}else{JPWLedgerTestDeal(d,ticket++,id,id,clock,1,0,.01,0,0,-.1,-.005);vol+=.01;}}
if(open)JPWLedgerTestLive(p,id,vol,-3,-.2);if(n%3==0)v.costs_complete=false;if(n%5==0)v.history_complete=false;
equal(d,o,p,v,"fixed-seed-generated-"+IntegerToString(n));
}
// Independently specified scale inputs and arithmetic, not a second copy of
// the production replay. Deals and pending orders are tested separately.
std::vector<JPWLedgerDeal>d;std::vector<JPWLedgerOrder>o;std::vector<JPWLedgerPosition>p;std::vector<JPWLedgerCycle>c;JPWLedgerView v;JPWLedgerTestView(v,1000);
for(int i=0;i<50000;i++)JPWLedgerTestDeal(d,100000+i,700,700,1000+i,1,0,.01,0,0,-.0002,0);
JPWLedgerTestLive(p,700,500,17.25,-2);replay(d,o,p,v,c);REQUIRE(c.size()==1,"50k deals one cycle");REQUIRE(std::abs(c[0].commissions-(-10.0))<1e-7,"50k deals independent -10 costs");REQUIRE(std::abs(c[0].compensated-5.25)<1e-7,"50k deals independent 5.25 compensated");REQUIRE(c[0].amount_valid&&c[0].percent_valid&&!c[0].partial,"50k deals financial quality");
d.clear();p.clear();JPWLedgerTestView(v,1000);o.resize(50000);for(int i=0;i<50000;i++){o[i].ticket=200000+i;o[i].setup_msc=1000+i;o[i].done_msc=0;o[i].symbol="TEST";o[i].side=1;o[i].state=1;o[i].volume=.01;}
replay(d,o,p,v,c);REQUIRE(c.size()==1&&c[0].pending_orders==50000&&c[0].state==4&&!c[0].genesis_inferred&&!c[0].amount_valid,"50k orders pending no invented genesis/amount");
o.resize(50001);CJPWLedgerReplay over;REQUIRE(!over.Begin(d,o),"50001 orders refused");o.clear();d.resize(50001);REQUIRE(!over.Begin(d,o),"50001 deals refused");
std::cout<<"REPLAY_JUDGE|PASS|"<<host_asserts<<"|19 legacy vectors|300 generated scenarios|50000 deals|50000 orders\n";return 0;
}catch(const std::exception&e){std::cerr<<"PRODUCT_FAIL|"<<e.what()<<'\n';return 1;}}
'''
def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,default=ROOT/"tools/.artifacts"/"core_replay_judge.json");a=p.parse_args();compiler=shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("JPW_TEST_RESULT: ENVIRONMENT_ERROR");return 2
    files=[BASE/'Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh',BASE/'Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh',BASE/'Include/JPWealth/JPW_Genetrix_Ledger_Preparation.mqh',BASE/'Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5',Path(__file__).resolve(),ROOT/'tools/jpw_genetrix_ledger_test.py']
    receipt={'scope':'actual private replay vs unchanged legacy builder; synthetic data/clock, real host SQLite wrappers but this test does not exercise commit; native MT5 NOT_RUN','sources':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}}
    def translated(x):
        raw=x.read_text()
        if x.name=='JPW_Genetrix_Ledger_Preparation.mqh' and 'class CJPWLedgerPreparation' in raw:
            # Scope is the complete unchanged replay class and its indexes,
            # not the later terminal collector which needs different seams.
            raw=raw.split('class CJPWLedgerPreparation',1)[0]+'\n#endif\n'
        raw=re.sub(r'\b(\w+)\s+(\w+\[\](?:,\w+\[\])+)\s*;',lambda m:'std::vector<'+m[1]+'> '+m[2].replace('[]','')+';',raw)
        return legacy.translate(raw)
    source=legacy.SHIM+'\n'+EXTRA+'\n'+'\n'.join(translated(x) for x in files[:4])+'\n'+TEST
    with tempfile.TemporaryDirectory(prefix='core-replay-judge-') as d:
        d=Path(d);cpp=d/'judge.cpp';binary=d/'judge';cpp.write_text(source)
        build=subprocess.run([compiler,'-std=c++17','-Wno-deprecated-declarations',str(cpp),'-lsqlite3','-o',str(binary)]+([] if sys.platform=='darwin' else ['-lcrypto']),capture_output=True,text=True)
        receipt['compile_returncode']=build.returncode;receipt['compile_log']=build.stderr
        if not build.returncode:
            run=subprocess.run([str(binary),str(d/'files')],capture_output=True,text=True,timeout=120);receipt.update(status='PASS' if run.returncode==0 else 'PRODUCT_FAIL',returncode=run.returncode,stdout=run.stdout,stderr=run.stderr)
        else:receipt.update(status='JUDGE_ERROR')
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

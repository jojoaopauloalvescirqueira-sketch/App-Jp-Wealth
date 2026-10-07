#!/usr/bin/env python3
"""Independent complete preparation/commit test with real SQLite and controlled source."""
import argparse,hashlib,importlib.util,json,re,subprocess,tempfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'mt5/jpw-alavancagem-atual/MQL5'
spec=importlib.util.spec_from_file_location('legacy',ROOT/'tools/jpw_genetrix_ledger_test.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
EXTRA=r'''
using uint=unsigned int;using ulong=unsigned long;using datetime=long;
ulong clock_ms=1000;ulong GetTickCount64(){return clock_ms++;}
template<class T,class U> void ArrayInitialize(std::vector<T>& a,U n){std::fill(a.begin(),a.end(),(T)n);}
double MathMin(double a,double b){return std::min(a,b);}
string JPWRaizNFrame(const string&s){return IntegerToString(s.size())+":"+s;}
enum{ACCOUNT_BALANCE=1,ACCOUNT_MARGIN_MODE=2,ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2,TERMINAL_CONNECTED=3};
string current_key;double current_balance=1000;bool disconnected=false;int selection=0,select_calls=0;
std::vector<JPWLedgerDeal> native_deals;std::vector<JPWLedgerOrder> native_orders,live_orders;std::vector<JPWLedgerPosition> live_positions;
bool JPWLedgerIdentity(string&key,string&currency){key=current_key;currency="USD";return true;}
bool JPWLedgerAccountDouble(int,double&v){v=current_balance;return true;}
long AccountInfoInteger(int){return ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;}
long TerminalInfoInteger(int){return disconnected?0:1;}
long TimeTradeServer(){return 1000;}long TimeCurrent(){return 1000;}long TimeGMT(){return 100;}
bool HistorySelect(long,long){selection=0;select_calls++;return true;}
int HistoryDealsTotal(){return selection==0?native_deals.size():1;}
int HistoryOrdersTotal(){return selection==0?native_orders.size():0;}
ulong HistoryDealGetTicket(int n){return native_deals.at(n).ticket;}
ulong HistoryOrderGetTicket(int n){return native_orders.at(n).ticket;}
bool JPWLedgerReadDeal(ulong ticket,JPWLedgerDeal&out){for(auto&d:native_deals)if(d.ticket==(long)ticket){out=d;return true;}return false;}
bool JPWLedgerReadOrder(ulong ticket,bool,JPWLedgerOrder&out,bool&relevant){relevant=true;for(auto&o:native_orders)if(o.ticket==(long)ticket){out=o;return true;}return false;}
bool JPWLedgerReadLive(std::vector<JPWLedgerPosition>&p,std::vector<JPWLedgerOrder>&o,bool&fresh,string&reason){p=live_positions;o=live_orders;fresh=!disconnected;return true;}
'''
TEST=r'''
void fixture(int n){JPWLedgerView v;JPWLedgerTestFixture(n,native_deals,native_orders,live_positions,v);live_orders.clear();for(auto&o:native_orders)if(o.state==1||o.state==4)live_orders.push_back(o);current_balance=v.balance;}
bool prepare(CJPWLedgerPreparation&r,int db,const string&key,const string&token,bool complete=true,int mutation=0){std::vector<long>deletes;REQUIRE(r.Begin(db,key,token,key,complete,complete,"synthetic origin and costs evidence",deletes,false),"Begin");bool ready=false,changed=false;int steps=0;
while(!ready){if(mutation==1&&!changed&&r.stage>=14){native_deals[0].commission-=.5;changed=true;}if(mutation==2&&!changed&&r.stage>=18){native_deals[0].commission-=.5;changed=true;}if(mutation==3&&!changed&&r.stage>=5){current_key=string(64,'d');changed=true;}
selection=1;bool ok=r.Step(GetTickCount64()+5,ready);REQUIRE(host_statements.empty(),"no query survives timer slice");REQUIRE(sqlite3_get_autocommit(host_dbs.at(db))!=0,"no main transaction survives timer slice");if(!ok)return false;REQUIRE(++steps<30000,"finite stable preparation progresses");}
return true;}
int main(int argc,char**argv){host_root=argv[1];try{
string key,token,why;JPWRaizNHash("core-preparation-synthetic-account",key);JPWRaizNHash("publisher",token);current_key=key;FolderCreate("JPWealth/Genetrix");int db=-1;REQUIRE(JPWLedgerOpen(key,true,db,why),"open actual SQLite");
fixture(1);CJPWLedgerPreparation first;REQUIRE(prepare(first,db,key,token),"full source prepare after external history selection resets");REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==0,"staging never changes generation");REQUIRE(first.Publish(),"atomic publish first generation");REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==1,"one accepted generation");
JPWLedgerView view;std::vector<JPWLedgerCycle>cycles;string composition;REQUIRE(JPWLedgerReadProjection(db,key,view,cycles,composition,why),"read accepted projection");REQUIRE(cycles.size()==1&&JPWLedgerNear(cycles[0].compensated,46.42)&&!cycles[0].partial,"independent 46.42 amount complete evidence");
CJPWLedgerPreparation replay;REQUIRE(prepare(replay,db,key,token)&&replay.Publish(),"replay accepted");REQUIRE(scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"replay no duplicate revisions");
long generation=scalar(db,"SELECT generation FROM ledger_meta");fixture(1);CJPWLedgerPreparation correction;REQUIRE(!prepare(correction,db,key,token,true,1),"cost correction same counts during second content pass refused");REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==generation,"failed source reconciliation preserves generation");
fixture(1);CJPWLedgerPreparation correction_late;REQUIRE(!prepare(correction_late,db,key,token,true,2),"cost correction during final projection refused by third full pass");REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==generation,"late correction preserves generation");
fixture(1);CJPWLedgerPreparation switched;REQUIRE(!prepare(switched,db,key,token,true,3),"account switch refuses draft");current_key=key;REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==generation,"account isolation no write");
fixture(1);CJPWLedgerPreparation stale;REQUIRE(prepare(stale,db,key,token),"prepare base conflict fixture");REQUIRE(DatabaseExecute(db,"UPDATE ledger_meta SET generation=generation+1"),"synthetic competing base change");REQUIRE(!stale.Publish(),"base generation change refuses commit");REQUIRE(DatabaseExecute(db,"UPDATE ledger_meta SET generation=generation-1"),"restore synthetic base for later distinct case");
fixture(1);CJPWLedgerPreparation failed;REQUIRE(prepare(failed,db,key,token),"prepare forced write failure");REQUIRE(DatabaseExecute(db,"CREATE TRIGGER fail_projection BEFORE INSERT ON ledger_projection BEGIN SELECT RAISE(ABORT,'fixture'); END"),"inject fixture failure");REQUIRE(!failed.Publish(),"commit failure reported");REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==generation&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"atomic rollback raw audit meta projection");REQUIRE(DatabaseExecute(db,"DROP TRIGGER fail_projection"),"remove synthetic test trigger");
fixture(1);CJPWLedgerPreparation busy;REQUIRE(prepare(busy,db,key,token),"prepare busy fixture");int competitor=-1;REQUIRE(JPWLedgerOpen(key,false,competitor,why),"open independent competing SQLite connection");REQUIRE(DatabaseExecute(competitor,"BEGIN EXCLUSIVE"),"hold competing lock");REQUIRE(!busy.Publish(),"busy commit refused");REQUIRE(DatabaseExecute(competitor,"ROLLBACK"),"release competing lock");DatabaseClose(competitor);REQUIRE(scalar(db,"SELECT generation FROM ledger_meta")==generation&&scalar(db,"SELECT COUNT(*) FROM ledger_deal_revisions")==2,"busy refusal no financial mutation");
fixture(1);CJPWLedgerPreparation after_busy;REQUIRE(prepare(after_busy,db,key,token)&&after_busy.Publish(),"stable preparation recovers after busy release");generation=scalar(db,"SELECT generation FROM ledger_meta");
fixture(1);CJPWLedgerPreparation partial;REQUIRE(prepare(partial,db,key,token,false)&&partial.Publish(),"default coverage false still safe partial publication");REQUIRE(JPWLedgerReadProjection(db,key,view,cycles,composition,why)&&!view.history_complete&&!view.costs_complete&&cycles[0].partial&&!cycles[0].amount_valid,"coverage false not invented complete amount");
fixture(1);CJPWLedgerPreparation historical;REQUIRE(prepare(historical,db,key,token),"prepare disconnection fixture");disconnected=true;REQUIRE(historical.RevalidateLive()&&historical.view.quality==2,"disconnection lowers freshness no zero");disconnected=false;
DatabaseClose(db);std::cout<<"PREPARATION_JUDGE|PASS|"<<host_asserts<<"|source_selection_calls="<<select_calls<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<"PRODUCT_FAIL|"<<e.what()<<'\n';return 1;}}
'''
def translated(raw):
 raw=re.sub(r'\b(\w+)\s+(\w+\[\](?:,\w+\[\])+)\s*;',lambda m:'std::vector<'+m[1]+'> '+m[2].replace('[]','')+';',raw)
 return legacy.translate(raw)
def extract(source,name,kind='bool'):
 start=source.index(kind+' '+name+'(');opening=source.index('{',start);depth=1;i=opening+1
 while depth:depth+=(source[i]=='{')-(source[i]=='}');i+=1
 return source[start:i]
def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,default=ROOT/"tools/.artifacts"/"core_preparation_judge.json");a=p.parse_args();compiler=shutil.which("clang++") or shutil.which("g++")
 if not compiler:
  print("JPW_TEST_RESULT: ENVIRONMENT_ERROR");return 2
 inc=BASE/'Include/JPWealth'
 paths=[inc/'JPW_Genetrix_Ledger_Core.mqh',inc/'JPW_Genetrix_Ledger_Store.mqh',inc/'JPW_Genetrix_Ledger_Preparation.mqh',inc/'JPW_Genetrix_Ledger_Terminal.mqh',BASE/'Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5',Path(__file__).resolve()]
 receipt={'scope':'complete production preparation and SQLite commit; source/API/clock controlled; no MT5 runtime or broker','sources':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in paths},'native':'NOT_RUN'}
 source='\n'.join([legacy.SHIM,translated(paths[0].read_text()),translated(paths[1].read_text()),EXTRA,translated(extract(paths[3].read_text(),'JPWLedgerComposition')),translated(paths[2].read_text()),translated(paths[4].read_text()),TEST])
 with tempfile.TemporaryDirectory(prefix='core-preparation-judge-') as d:
  d=Path(d);cpp=d/'judge.cpp';binary=d/'judge';cpp.write_text(source);build=subprocess.run([compiler,'-std=c++17','-Wno-deprecated-declarations',str(cpp),'-lsqlite3','-o',str(binary)]+([] if sys.platform=='darwin' else ['-lcrypto']),capture_output=True,text=True);receipt.update(compile_returncode=build.returncode,compile_log=build.stderr)
  if not build.returncode:
   run=subprocess.run([str(binary),str(d/'files')],capture_output=True,text=True,timeout=90);receipt.update(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,status='PASS' if run.returncode==0 else 'PRODUCT_FAIL')
  else:receipt['status']='JUDGE_ERROR'
 a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

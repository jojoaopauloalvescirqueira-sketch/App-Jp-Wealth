#!/usr/bin/env python3
"""Execute actual canonical Core + Risk_Core + MQL test bodies through a safe host shim.

No broker API, EA runtime, native locks or native MT5 execution. Core/state and
store bodies execute against host primitives; this does not certify the EA
orchestration or crash durability. Includes/date/array syntax only are
translated; policy/math/state function bodies are not replaced by Python.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / 'mt5/jpw-alavancagem-atual/MQL5'
FILES = [MQL/'Include/JPWealth/JPW_Alavancagem_Core.mqh',
         MQL/'Include/JPWealth/JPW_Genetrix_Risk_Core.mqh',
         MQL/'Include/JPWealth/JPW_Genetrix_Risk_Store.mqh',
         MQL/'Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5']
PROFILE = MQL/'Include/JPWealth/JPW_Alavancagem_Profile.mqh'
ORACLES = ROOT/'tests/fixtures/genetrix/risk-oracles-v1.json'
EA = MQL/'Experts/JPWealth/JPW_Genetrix_Supervisor.mq5'
TERMINAL = MQL/'Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh'

def actual_function(text: str, name: str) -> str:
    match=re.search(r'^(?:bool|string) '+re.escape(name)+r'\(',text,re.M)
    if not match: raise RuntimeError('existing function unavailable: '+name)
    opening=text.index('{',match.start()); depth=0
    for i in range(opening,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0: return text[match.start():i+1]
    raise RuntimeError('function extraction failed: '+name)

STORE_SHIM = r'''
constexpr int FILE_COMMON=256,FILE_TXT=512,FILE_ANSI=1024,TERMINAL_DATA_PATH=1;
string TerminalInfoString(int property){if(property!=TERMINAL_DATA_PATH)throw std::runtime_error("bad property");return "HOST-SYNTHETIC-INSTALL";}
datetime TimeGMT(){return TimeLocal();}
int GetLastError(){return 0;}
void ResetLastError(){}
template<class T>void ZeroMemory(T& v){v=T{};}
int StringFind(const string& s,const string& part,int offset){auto p=s.find(part,offset);return p==s.npos?-1:(int)p;}
int FileOpen(const string& p,int flags,ushort delimiter,uint cp){
  if(delimiter!=0||cp!=CP_UTF8)throw std::runtime_error("unexpected file encoding");
  return FileOpen(p,flags&~(FILE_COMMON|FILE_TXT|FILE_ANSI));
}
uint FileWriteString(int h,const string& s){std::vector<uchar>b(s.begin(),s.end());return FileWriteArray(h,b);}
string FileReadString(int h){auto it=handles.find(h);if(it==handles.end())return "";string s;std::getline(it->second->stream,s);if(!s.empty()&&s.back()=='\r')s.pop_back();return s;}
bool FileIsEnding(int h){auto it=handles.find(h);return it!=handles.end()&&it->second->stream.peek()==EOF;}
bool FileSeek(int h,long offset,int origin){auto it=handles.find(h);if(it==handles.end())return false;
  auto& s=it->second->stream;s.clear();auto o=origin==SEEK_END?std::ios::end:std::ios::beg;
  s.seekg(offset,o);s.seekp(offset,o);return bool(s);}
double MathMax(double a,double b){return std::max(a,b);}
'''

STORE_TESTS = r'''
void HostRiskStoreTests(){
  JPWAccount account;account.login=42;account.server="SYNTHETIC-DEMO";account.currency="USD";
  string key,why;JPWRiskAssert(JPWRiskAccountKey(account,key),"RIS-STORE01 opaque installation-bound identity");
  JPWRiskRecord r{};JPWRiskReset(r.machine);r.view.schema=1;r.view.account_key=key;r.view.generation=0;
  r.view.observed_utc=TimeGMT();r.view.quality="Current";r.view.state="OBSERVE";r.view.reason="SYNTHETIC";
  r.view.gross=6000;r.view.equity=1000;r.view.leverage=6;r.view.projected_leverage=6.5;
  r.view.pending_projection_valid=true;r.view.pending_count=1;r.view.position_count=1;r.view.session_challenge="challenge";
  JPWRiskAssert(JPWRiskSaveRecord(r,why)&&r.view.generation==1,"RIS-STORE02 save readback generation1");
  JPWRiskRecord read{};JPWRiskAssert(JPWRiskLoadRecord(key,read,why)&&read.view.gross==6000&&read.view.generation==1,"RIS-STORE03 canonical roundtrip no implicit defaults");
  JPWRiskAction a;JPWRiskClearAction(a);a.kind=JPW_RISK_CLOSE;a.ticket=10;a.identifier=10;a.symbol="EURUSD.fixture";a.direction=0;a.volume=.1;
  r.machine.armed=true;JPWRiskBegin(r.machine,a,"nonce-durable",TimeGMT());r.view.state="ACTION_UNKNOWN";
  JPWRiskAssert(JPWRiskSaveRecord(r,why)&&JPWRiskLoadRecord(key,read,why)&&read.machine.phase==JPW_RISK_UNKNOWN&&read.machine.active.ticket==10,"RIS-STORE04 durable unknown intent survives new object load");
  string damaged=JPWRiskEncode(r);damaged.back()=damaged.back()=='0'?'1':'0';
  JPWRiskAssert(!JPWRiskDecode(damaged,read),"RIS-STORE05 checksum rejects corruption");
  inject_short_write=true;
  JPWRiskAssert(!JPWRiskSaveRecord(r,why)&&r.view.generation==2,"RIS-STORE06 short write not confirmed");
  JPWRiskAssert(!JPWRiskLoadRecord(key,read,why)&&why=="INTERRUPTED_WRITE_REVIEW_REQUIRED","RIS-STORE07 interrupted latest write blocks old clean fallback");
  JPWRiskAssert(FileDelete(JPWRiskStorePath(key,1)+".tmp",FILE_COMMON),"RIS-STORE08 fixture-only interrupted write cleanup");
  JPWRiskAssert(JPWRiskAppendReceipt(r,"SYNTHETIC_INTENT",why),"RIS-STORE09 structured receipt append readback");
  inject_short_write=true;
  JPWRiskAssert(!JPWRiskAppendReceipt(r,"SYNTHETIC_SHORT",why),"RIS-STORE10 receipt short write rejected");
  string lock=JPW_RISK_FOLDER+key+".lock";
  int h1=FileOpen(lock,FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);
  int h2=FileOpen(lock,FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);
  JPWRiskAssert(h1!=INVALID_HANDLE&&h2==INVALID_HANDLE,"RIS-AC16 lock primitive synthetic exclusive owner");
  FileClose(h1);h2=FileOpen(lock,FILE_READ|FILE_WRITE|FILE_BIN|FILE_COMMON);
  JPWRiskAssert(h2!=INVALID_HANDLE,"RIS-AC16 lock primitive synthetic release");FileClose(h2);
}
'''

CANCEL_HISTORY_SHIM = r'''
enum {ORDER_STATE_FILLED=101,ORDER_STATE_CANCELED=102,ORDER_STATE_REJECTED=103,ORDER_STATE_EXPIRED=104,
 ORDER_TYPE_BUY_LIMIT=201,ORDER_TYPE_SELL_LIMIT=202,ORDER_TYPE_BUY_STOP=203,ORDER_TYPE_SELL_STOP=204,
 ORDER_TYPE_BUY_STOP_LIMIT=205,ORDER_TYPE_SELL_STOP_LIMIT=206,
 ORDER_STATE=301,ORDER_TYPE=302,ORDER_POSITION_ID=303,ORDER_VOLUME_INITIAL=304,ORDER_VOLUME_CURRENT=305,ORDER_SYMBOL=306,
 DEAL_TYPE=401,DEAL_ORDER=402,DEAL_POSITION_ID=403,DEAL_ENTRY=404,DEAL_VOLUME=405,DEAL_SYMBOL=406,
 DEAL_TYPE_BUY=501,DEAL_TYPE_SELL=502,DEAL_TYPE_BUY_CANCELED=503,DEAL_TYPE_SELL_CANCELED=504,
 DEAL_ENTRY_IN=601,DEAL_ENTRY_OUT=602,DEAL_ENTRY_OUT_BY=603};
JPWRiskRecord g_supervisor_record{};
struct SyntheticDeal {ulong ticket=0,order=0;long identifier=0,type=DEAL_TYPE_BUY,entry=DEAL_ENTRY_IN;double volume=0;string symbol="EURUSD.fixture";};
std::vector<SyntheticDeal> history_deals;
bool history_available=true,history_budget=true,order_still_active=false,history_fields=true,persist_allowed=true;
long history_state=ORDER_STATE_FILLED,history_type=ORDER_TYPE_BUY_LIMIT,history_identifier=900;
double history_initial=.2,history_residual=0;
int history_count_override=-1,persist_calls=0;bool durable_link_witness=false;
bool JPWWithinBudget(ulong){return history_budget;}
bool OrderSelect(ulong){return order_still_active;}
bool HistoryOrderSelect(ulong){return history_available;}
bool HistorySelectByPosition(long id){return history_available&&id==history_identifier;}
int HistoryDealsTotal(){return history_count_override<0?int(history_deals.size()):history_count_override;}
ulong HistoryDealGetTicket(int i){return i>=0&&i<int(history_deals.size())?history_deals[i].ticket:0;}
bool HistoryOrderGetInteger(ulong ticket,int field,long &value){if(ticket!=200||!history_fields)return false;
 if(field==ORDER_STATE)value=history_state;else if(field==ORDER_TYPE)value=history_type;else if(field==ORDER_POSITION_ID)value=history_identifier;else return false;return true;}
bool HistoryOrderGetDouble(ulong ticket,int field,double &value){if(ticket!=200||!history_fields)return false;
 if(field==ORDER_VOLUME_INITIAL)value=history_initial;else if(field==ORDER_VOLUME_CURRENT)value=history_residual;else return false;return true;}
bool HistoryOrderGetString(ulong ticket,int field,string &value){if(ticket!=200||field!=ORDER_SYMBOL||!history_fields)return false;value="EURUSD.fixture";return true;}
SyntheticDeal* find_history(ulong ticket){for(auto &d:history_deals)if(d.ticket==ticket)return &d;return nullptr;}
bool HistoryDealGetInteger(ulong ticket,int field,long &value){auto d=find_history(ticket);if(!d||!history_fields)return false;
 if(field==DEAL_TYPE)value=d->type;else if(field==DEAL_ORDER)value=(long)d->order;else if(field==DEAL_POSITION_ID)value=d->identifier;else if(field==DEAL_ENTRY)value=d->entry;else return false;return true;}
bool HistoryDealGetDouble(ulong ticket,int field,double &value){auto d=find_history(ticket);if(!d||field!=DEAL_VOLUME||!history_fields)return false;value=d->volume;return true;}
bool HistoryDealGetString(ulong ticket,int field,string &value){auto d=find_history(ticket);if(!d||field!=DEAL_SYMBOL||!history_fields)return false;value=d->symbol;return true;}
bool JPWSupervisorPersist(const string &reason,const string &event=""){
 persist_calls++;g_supervisor_record.view.reason=reason;
 if(event=="ENTRY_FILL_LINK_CONFIRMED")durable_link_witness=g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN&&
   g_supervisor_record.machine.active.identifier==900&&g_supervisor_record.machine.request_order==200&&g_supervisor_record.machine.request_deal>0;
 return persist_allowed;}
'''

CANCEL_HISTORY_TESTS = r'''
void CancelHistoryFixture(JPWRiskAction &action,std::vector<JPWRiskPosition> &positions){
 history_available=history_budget=history_fields=persist_allowed=true;order_still_active=false;
 history_state=ORDER_STATE_FILLED;history_type=ORDER_TYPE_BUY_LIMIT;history_identifier=900;
 history_initial=.2;history_residual=0;history_count_override=-1;persist_calls=0;durable_link_witness=false;
 history_deals.clear();JPWRiskReset(g_supervisor_record.machine);g_supervisor_record.machine.armed=true;
 JPWRiskClearAction(action);action.kind=JPW_RISK_CANCEL;action.ticket=200;action.symbol="EURUSD.fixture";action.volume=.2;
 JPWRiskBegin(g_supervisor_record.machine,action,"cancel-race",TimeGMT());
 positions.resize(1);JPWRiskFixturePosition(positions[0],901,900,100,.2,2000);
}
void HostCancelHistoryTests(){
 JPWRiskAction action;std::vector<JPWRiskPosition> positions;
 CancelHistoryFixture(action,positions);
 JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN&&persist_calls==0,
  "RIS-AC15 FILLED alone keeps unknown no new request");
 history_deals={{701,999,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.2,"EURUSD.fixture"}};
 JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 wrong order link keeps unknown");
 history_deals[0].order=200;history_deals[0].identifier=999;
 JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 wrong position identifier keeps unknown");
 history_deals[0].identifier=900;positions.clear();
 JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 entry not yet in inventory keeps unknown");
 positions.resize(1);JPWRiskFixturePosition(positions[0],901,900,100,.2,2000);
 JPWRiskAssert(JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_READY&&
   durable_link_witness&&persist_calls==2&&g_supervisor_record.machine.protection_incomplete,
  "RIS-AC15 linked order deal live identifier releases only after durable witness");
 CancelHistoryFixture(action,positions);positions.clear();
 history_deals={{701,200,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.2,"EURUSD.fixture"},
                {702,300,900,DEAL_TYPE_SELL,DEAL_ENTRY_OUT,.2,"EURUSD.fixture"}};
 JPWRiskAssert(JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_READY&&durable_link_witness,
  "RIS-AC15 positively closed subsequent chain reconciles flat");
 CancelHistoryFixture(action,positions);history_state=ORDER_STATE_CANCELED;history_residual=.1;positions[0].volume=.1;
 history_deals={{701,200,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.1,"EURUSD.fixture"}};
 JPWRiskAssert(JPWSupervisorCancelTerminalOutcome(action,positions,1)&&durable_link_witness&&g_supervisor_record.machine.protection_incomplete,
  "RIS-AC15 partial entry cancel needs linked residual");
 CancelHistoryFixture(action,positions);history_deals={{701,200,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.2,"EURUSD.fixture"}};
 history_budget=false;JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 budget incomplete keeps unknown");
 history_budget=true;history_count_override=2049;JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 truncated history limit keeps unknown");
 history_count_override=-1;history_deals[0].type=DEAL_TYPE_BUY_CANCELED;
 JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 canceled deal correction keeps unknown");
 CancelHistoryFixture(action,positions);history_deals={{701,200,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.2,"EURUSD.fixture"}};
 positions[0].volume=.1;JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 incoherent live volume keeps unknown");
 CancelHistoryFixture(action,positions);history_state=ORDER_STATE_CANCELED;history_identifier=0;history_residual=history_initial;
 JPWRiskAssert(JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_READY&&!durable_link_witness,
  "RIS-AC15 zero fill canceled pending confirmed without invented deal");
 CancelHistoryFixture(action,positions);history_deals={{701,200,900,DEAL_TYPE_BUY,DEAL_ENTRY_IN,.2,"EURUSD.fixture"}};
 persist_allowed=false;JPWRiskAssert(!JPWSupervisorCancelTerminalOutcome(action,positions,1)&&g_supervisor_record.machine.phase==JPW_RISK_UNKNOWN,
  "RIS-AC15 unconfirmed durable witness cannot release unknown");
}
'''

def run(evidence: Path | None) -> int:
    spec = importlib.util.spec_from_file_location('risk_existing_host_shim', ROOT/'tools/leverage_config_test.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        print('ENVIRONMENT_ERROR: existing C++ compiler unavailable; native NOT_RUN')
        return 2
    # Existing file primitives are redirected exclusively to a temporary fixture root.
    shim=base.SHIM.replace('constexpr double EMPTY_VALUE=2147483647.0;','')
    shim=shim.replace('using string=std::string;','constexpr int FILE_COMMON=256;\nusing string=std::string;')
    shim=shim.replace('if(common!=0)throw std::runtime_error("shared file area forbidden");',
                      'if(common!=0&&common!=FILE_COMMON)throw std::runtime_error("unknown file area");')
    store_shim=STORE_SHIM.replace('constexpr int FILE_COMMON=256,','constexpr int ')
    profile=PROFILE.read_text()
    helpers='\n'.join(actual_function(profile,n) for n in ['JPWProfileHash','JPWProfileIsHash','JPWProfileFrame','JPWProfileAccountHash'])
    source=shim+'\n'+store_shim+'\n'+base.translate(FILES[0].read_text())+'\n'+base.translate(helpers)+'\n'
    source+='\n'.join(base.translate(p.read_text()) for p in FILES[1:])+'\n'+STORE_TESTS
    source+='\n'+CANCEL_HISTORY_SHIM+'\n'+base.translate(actual_function(TERMINAL.read_text(),'JPWRiskEntryType'))+'\n'
    source+=base.translate(actual_function(EA.read_text(),'JPWSupervisorTerminalOrder'))+'\n'
    source+=base.translate(actual_function(EA.read_text(),'JPWSupervisorCancelTerminalOutcome'))+'\n'+CANCEL_HISTORY_TESTS
    source+='\nint main(int argc,char**argv){if(argc!=2)return 2;file_root=argv[1];fs::create_directories(file_root);OnStart();HostRiskStoreTests();HostCancelHistoryTests();Print("HOST_TOTAL ",g_risk_test_pass," PASS / ",g_risk_test_fail," FAIL");return g_risk_test_fail==0?0:1;}\n'
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES+[PROFILE,EA,TERMINAL,Path(__file__),ROOT/'tools/leverage_config_test.py']}
    with tempfile.TemporaryDirectory(prefix='jpw-risk-host-') as folder:
        work = Path(folder)
        cpp = work/'risk.cpp'; exe = work/'risk-tests'; cpp.write_text(source)
        compile_command = [compiler,'-std=c++17','-Wall','-Wextra','-Werror',str(cpp),'-o',str(exe)]
        compilation = subprocess.run(compile_command,text=True,capture_output=True)
        execution = None if compilation.returncode else subprocess.run([str(exe),str(work/'synthetic-files')],text=True,capture_output=True)
        result = {'test':'jpw_genetrix_risk_pure','scope':'CORE_STORE_AND_CANCEL_TERMINAL_REAL_BODY_SYNTHETIC_APIS',
                  'execution_state':'NOT_RUN' if execution is None else 'EXECUTED_HOST',
                  'hashes':hashes,'compile_command':compile_command,'compile_exit':compilation.returncode,
                  'execute_exit':None if execution is None else execution.returncode,
                  'native_compile':'NOT_RUN','native_execution':'NOT_RUN','ea_orchestration':'NOT_RUN',
                  'store_codec':'NOT_RUN' if execution is None else 'EXECUTED_HOST',
                  'cancel_terminal_adapter':'NOT_RUN' if execution is None else 'EXECUTED_HOST_SYNTHETIC_HISTORY',
                  'local_lock_primitive':'NOT_RUN' if execution is None else 'EXECUTED_HOST_SYNTHETIC',
                  'store_crash_durability':'NOT_RUN','cross_terminal_coordination':'NOT_PROVIDED'}
        passed=[] if execution is None else re.findall(r'^PASS (.+)$',execution.stdout,re.M)
        reference=json.loads(ORACLES.read_text())
        oracle_by_id={case['id']:case for case in reference['cases']}
        result['frozen_oracle_reference']={'path':str(ORACLES.relative_to(ROOT)),
            'sha256':hashlib.sha256(ORACLES.read_bytes()).hexdigest(),
            'usage':'AUDIT_REFERENCE_ONLY; executable author fixtures are in the distributed MQL script. Independent JSON-driven numeric execution is a separate root-owned check.'}
        coverage=[]
        for i in range(1,19):
            case=f'RIS-AC{i:02d}'
            names=[name for name in passed if name.startswith(case+' ')]
            coverage.append({'case':case,'host_assertions':names,
                'frozen_oracle':oracle_by_id.get(case),
                'host_component_state':'EXECUTED_HOST' if names else 'NOT_RUN',
                'native_case_state':'NOT_RUN','whole_case_verdict':'NOT_RUN',
                'limit':'Core/state, Store or cancel-terminal real body with synthetic history only; full EA orchestration, native permissions/lifecycle/broker evidence NOT_RUN'})
        result['coverage']=coverage
        result['passed_assertions']=passed
        result['outcome']='PASS' if execution is not None and execution.returncode==0 else 'TEST_HARNESS_FAIL' if execution is None else 'PRODUCT_FAIL'
        if evidence:
            evidence.mkdir(parents=True,exist_ok=True)
            (evidence/'host-risk.cpp').write_text(source)
            (evidence/'compile.log').write_text(compilation.stdout+compilation.stderr)
            (evidence/'execution.log').write_text('' if execution is None else execution.stdout+execution.stderr)
            (evidence/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        print(compilation.stdout+compilation.stderr,end='')
        if execution: print(execution.stdout+execution.stderr,end='')
        print(json.dumps(result,indent=2))
        if compilation.returncode:
            print('TEST_HARNESS_FAIL: host compilation failed; MQL_NATIVE NOT_RUN')
            return 1
        return execution.returncode

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-dir',type=Path)
    args=parser.parse_args()
    raise SystemExit(run(args.evidence_dir))

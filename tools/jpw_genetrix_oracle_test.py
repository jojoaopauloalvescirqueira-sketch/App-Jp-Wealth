#!/usr/bin/env python3
"""Independent frozen-fixture input/output check of actual MQL risk core.

Synthetic rows exercise planning only. No broker, EA orchestration, native
compiler or server execution. Expected numbers are never derived from product.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,tempfile
from decimal import Decimal,localcontext
import leverage_config_test as base
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/genetrix'
EXPECTED_HASH={'risk-oracles-v1.json':'1c3e9488dd4fe1825d439efc8ea71e83cd34762639ef12770bf33e0cd83f4b7e','ledger-oracles-v1.json':'a26fe59b37edfd4dbc4d8759e87dc6a9f6ffffce74d427e950c5e2bfd434fc1f'}
CORE=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth'

def run(dest):
    fixture={}
    for name,wanted in EXPECTED_HASH.items():
        p=FIX/name
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=wanted:raise RuntimeError('FIXTURE_CHANGED: '+name)
        fixture[name]=json.loads(p.read_text())
    # Decimal reference consistency is independently checked, not a product test.
    with localcontext() as ctx:
        ctx.prec=28
        for c in fixture['ledger-oracles-v1.json']['cases']:
            r,u,b,C=map(Decimal,[c['realized_posted'],c['floating_remaining'],c['balance'],c['compensated']])
            assert r+u==C,(c['id'],'frozen subtotal inconsistent')
            assert abs(100*C/b-Decimal(c['percent_exact']))<Decimal('1e-24'),c['id']
    cases=fixture['risk-oracles-v1.json']['cases'][:7]
    reference=fixture['risk-oracles-v1.json']['cases'][4]['positions_oldest_first']
    cpp=base.SHIM+'\ndouble MathMax(double a,double b){return std::max(a,b);}\n'
    cpp+=base.translate((CORE/'JPW_Alavancagem_Core.mqh').read_text())
    cpp+=base.translate((CORE/'JPW_Genetrix_Risk_Core.mqh').read_text())
    cpp+='\nint main(){\n'
    for case in cases:
        ident=case['id'];assert re.fullmatch('RIS-AC[0-9]{2}',ident)
        rows=case.get('positions_oldest_first',reference if ident=='RIS-AC07' else [{'ticket':30,'notional':case['gross']}])
        cpp+=' { JPWRiskPosition p;std::vector<JPWRiskPosition> positions;std::vector<JPWRiskPending> pending;\n'
        for i,row in enumerate(rows):
            cpp+=f'p.ticket={row["ticket"]};p.identifier={row["ticket"]};p.opened_msc={1000+i};p.symbol="EURUSD.fixture";p.direction=0;p.volume=1;p.gross={row["notional"]};positions.push_back(p);\n'
        for i,row in enumerate(case.get('pending_oldest_first',[])):
            cpp+=f'{{JPWRiskPending q{{}};q.ticket={row["ticket"]};q.setup_msc={1000+i};q.symbol="EURUSD.fixture";q.type=2;q.volume=1;q.entry=1;q.gross={row["notional"]};pending.push_back(q);}}\n'
        cpp+=f'JPWRiskSnapshot s{{}};s.valid=true;s.current=true;s.pending_valid=true;s.hedging=true;s.equity={case["equity"]};s.gross={case["gross"]};\n'
        cpp+='JPWRiskMachine m;JPWRiskReset(m);JPWRiskAction a;string why;std::vector<ulong> canceled;\n'
        cpp+='for(int step=0;step<8;step++){s.pending_gross=0;for(auto&q:pending)s.pending_gross+=q.gross;JPWLeverage(s.gross,s.equity,s.leverage);JPWLeverage(s.gross+s.pending_gross,s.equity,s.projected_leverage);if(!JPWRiskPlan(s,positions,pending,m,a,why))return 2;if(a.kind!=JPW_RISK_CANCEL)break;canceled.push_back(a.ticket);for(auto it=pending.begin();it!=pending.end();++it)if(it->ticket==a.ticket){pending.erase(it);break;}}\n'
        cpp+=f'std::cout<<"{ident}|"<<(int)a.kind<<"|"<<a.ticket<<"|";for(auto t:canceled)std::cout<<t<<",";std::cout<<"|"<<std::setprecision(17)<<s.leverage<<"|"<<s.projected_leverage<<"\\n";}}\n'
    cpp+='return 0;}\n'
    compiler=shutil.which('clang++') or shutil.which('g++')
    if not compiler:raise RuntimeError('ENVIRONMENT_ERROR: no C++ compiler')
    with tempfile.TemporaryDirectory(prefix='jpw-independent-oracle-') as folder:
        source=Path(folder)/'oracle.cpp';exe=Path(folder)/'oracle';source.write_text(cpp)
        cc=subprocess.run([compiler,'-std=c++17',str(source),'-o',str(exe)],capture_output=True,text=True)
        result=None if cc.returncode else subprocess.run([str(exe)],capture_output=True,text=True)
        failures=[];actual_rows=[]
        if result and result.returncode==0:
            output=result.stdout.splitlines()
            for case,line in zip(cases,output):
                ident,kind,ticket,canceled,ratio,projected=line.split('|')
                kind,ticket=int(kind),int(ticket);canceled=[int(x) for x in canceled.split(',') if x]
                expected_kind=2 if (case.get('expected_action')=='CLOSE_NEWEST_WHOLE' or 'expected_ticket'in case or 'then_close'in case) else 0
                expected_ticket=case.get('expected_ticket',case.get('then_close',30 if expected_kind==2 else 0))
                if (kind,ticket,canceled)!=(expected_kind,expected_ticket,case.get('expected_cancel_tickets',[])):failures.append(case['id'])
                if abs(float(ratio)-float(Decimal(case['gross'])/Decimal(case['equity'])))>1e-13:failures.append(ident+':ratio')
                if 'remaining_projected'in case and abs(float(projected)*float(case['equity'])-float(case['remaining_projected']))>1e-9:failures.append(ident+':projected')
                actual_rows.append({'id':ident,'kind':kind,'ticket':ticket,'canceled':canceled,'actualLeverage':ratio,'actualProjected':projected,'result':'FAIL' if ident in failures else 'PASS'})
            if len(output)!=len(cases):failures.append('OUTPUT_COUNT')
        else:failures.append('COMPILE_OR_EXECUTION')
        receipt={'scope':'FROZEN_INPUTS_VS_EFFECTIVE_MQL_PURE_PLANNER','fixtureHashes':EXPECTED_HASH,'sourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CORE/'JPW_Alavancagem_Core.mqh',CORE/'JPW_Genetrix_Risk_Core.mqh',Path(__file__)]},'compileExit':cc.returncode,'executionExit':None if result is None else result.returncode,'rows':actual_rows,'ledgerDecimalReferenceCount':19,'failures':failures,'outcome':'PASS'if not failures else'FAIL','native':'NOT_RUN'}
        if dest:
            dest.mkdir(parents=True,exist_ok=True);(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(dest/'source.cpp').write_text(cpp);(dest/'compile.log').write_text(cc.stdout+cc.stderr);(dest/'execution.log').write_text(''if result is None else result.stdout+result.stderr)
        if failures:print(cc.stderr)
        print(json.dumps(receipt,indent=2))
        return bool(failures)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path);args=parser.parse_args();raise SystemExit(run(args.evidence_dir))

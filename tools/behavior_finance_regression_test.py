#!/usr/bin/env python3
"""FIN-01/02/03 behavioral regressions, served sources and disposable Chromium.

--root permits the same assertions against a preserved baseline. Only synthetic
commands and disposable browser storage are written; the served tree is read-only.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import Server, Quiet, ready, SEED
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['src/js/30-accounting/01-daily-ledger.js',
           'src/js/30-accounting/02-accounting-engine.js',
           'src/js/30-accounting/06-planning/01-engine.js',
           'src/js/30-accounting/06-planning/02-state.js',
           'src/js/30-accounting/06-planning/03-ui.js',
           'src/js/10-domain/00-forex-state.js', 'src/js/10-domain/02-risk-calculations.js',
           'src/js/10-domain/07-reserve-requirements.js']


def snapshot(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),
      writes:window.__financeWrites.length})""")


def unchanged(page, before):
    after = snapshot(page)
    assert after == before, {'before': before, 'after': after}


def instrument(page):
    page.evaluate("""() => {
      window.__financeWrites=[];
      const set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
      Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)__financeWrites.push('set');return set.call(this,k,v);};
      Storage.prototype.removeItem=function(k){if(this===localStorage&&k===LSKEY)__financeWrites.push('remove');return remove.call(this,k);};
    }""")


def query_b_while_a(page, scope):
    result = page.evaluate("""a => {
      const api=JPWForex.state,yes=r=>{if(!r.ok)throw Error(JSON.stringify(r));return r;};
      yes(JPWLedger.record({data:'2026-09-03',resultado:120,saldo:12120}));
      S.accounts.push({forexAccountId:'FIN-B',nome:'Synthetic account B',tipo:'PRÓPRIA',platformCurrency:'USD'});
      yes({ok:save()===true});
      yes(api.recordAccountPeriod({accountId:'FIN-B',startedAt:'2026-09-01',currency:'USD',si:3000,openingBook:3000,source:'Synthetic B opening',activateCurrentPeriod:true},{reason:'Synthetic B fixture'}));
      const b={accountId:'FIN-B',periodId:S.forex.accountContexts.accounts['FIN-B'].currentPeriodId};
      yes(api.selectOperationalContext(b.accountId,b.periodId));
      yes(JPWLedger.record({data:'2026-09-02',resultado:30,saldo:3030}));
      const expected=JPWLedger.monthlyActual('2026-09',{...b,complete:true});
      yes(api.selectOperationalContext(a.accountId,a.periodId));
      const before={state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length};
      const actual=JPWLedger.monthlyActual('2026-09',{...b,complete:true});
      const active=JPWLedger.rows(),missing=JPWLedger.monthlyActual('2026-09',{accountId:'MISSING',periodId:'MISSING',complete:true});
      const wrongWrite=JPWLedger.record({data:'2026-09-04',resultado:1,saldo:3031},{context:b});
      const wrongCorrection=JPWLedger.correct(expected.source.rows[0].id,{data:'2026-09-02',resultado:31,saldo:3031},{reason:'Must refuse',context:b,expectedVersion:1});
      const wrongVoid=JPWLedger.void(expected.source.rows[0].id,{reason:'Must refuse',expectedVersion:1});
      return {a,b,expected,actual,active,missing,wrongWrite,wrongCorrection,wrongVoid,before,
        after:{state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length},selected:api.operationalSelection()};
    }""", scope)
    assert result['actual'] == result['expected'], result
    assert result['actual']['status'] == 'COMPLETE' and result['actual']['profitUsd'] == 30
    assert all(row['accountId'] == scope['accountId'] for row in result['active'])
    assert result['selected']['accountId'] == scope['accountId'] and result['selected']['periodId'] == scope['periodId']
    assert result['missing']['status'] == 'PARTIAL' and result['missing']['source']['rows'] == []
    assert all(not result[key]['ok'] for key in ['wrongWrite', 'wrongCorrection', 'wrongVoid'])
    assert result['before'] == result['after'], result
    return {'profitB': 30, 'rowsA': len(result['active']), 'selection': result['selected'], 'readAndWrongWritesUnchanged': True}


def independent_planning(page, scope):
    before=snapshot(page)
    result=page.evaluate("""() => {
      const api=JPWPlanning,roots={forex:JSON.stringify(S.forex),ledger:JSON.stringify(S.ledger),legacy:JSON.stringify(S.fxPlanning),pf:JSON.stringify(S.personalFinance),alladin:JSON.stringify(S.alladin)};
      const made=api.commands.execute('createAccount',{name:'Synthetic independent FIN',startMonth:'2026-09',initialUsd:12000,profileId:'base',monthlyContributionUsd:10,goals:{adequate:null,ideal:{value:500,currency:'USD'}}},api.queries.token());
      if(!made.ok)throw Error(JSON.stringify(made));
      const prior={state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length};
      const denied=api.commands.execute('importLedgerActual',{accountId:made.accountId,month:'2026-09'},api.queries.token(made.accountId));
      return {denied,prior,after:{state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length},roots,
        rootsAfter:{forex:JSON.stringify(S.forex),ledger:JSON.stringify(S.ledger),legacy:JSON.stringify(S.fxPlanning),pf:JSON.stringify(S.personalFinance),alladin:JSON.stringify(S.alladin)}};
    }""")
    assert result['denied']['status']=='INVALID',result
    assert result['prior']==result['after'] and result['roots']==result['rootsAfter'],result
    assert snapshot(page)['writes']==before['writes']+1,'Only explicit account create may write'
    page.evaluate("JPWNavigation.navigate('planning')")
    assert page.locator('#fxpLedgerImportBtn').count()==0,'Retired import UI is still active'
    return {'retiredImportRefused':True,'adjacentFinancialRootsUnchanged':True,'explicitCreateWrites':1}


def reserves(page, scope, kind):
    result=page.evaluate("""({a,kind}) => {
      const api=JPWForex.state,yes=r=>{if(!r.ok)throw Error(JSON.stringify(r));return r;};
      const input={capitalNominal:10000,fcrConstituted:1234,feoConstituted:432,sixMonthExpenseAmount:432,
        determinationRecorded:true,expensesApproved:true,expensePeriod:'Synthetic six months',determinationReference:'Synthetic documented method',source:'Synthetic old period'};
      yes(api.recordReserves(input,{reason:'Preserved old global observation'}));
      const old=structuredClone(S.forex.reserves);
      yes(api.recordAccountPeriod({accountId:a.accountId,startedAt:'2026-10-01',currency:'USD',si:10000,openingBook:12000,source:'Synthetic new period',activateCurrentPeriod:true},{reason:'Synthetic next period'}));
      const next={accountId:a.accountId,periodId:S.forex.accountContexts.accounts[a.accountId].currentPeriodId};
      yes(api.selectOperationalContext(next.accountId,next.periodId));
      yes(api.recordAccountFacts({accountIndex:0,periodId:next.periodId,si:10000,equity:12000,netCashflow:0,
        cashflowAdjustmentRecorded:true,currency:'USD',capitalNominal:kind==='conflict'?9000:null,
        source:'Synthetic new equity',observedAt:'2026-10-02T12:00:00Z'},{reason:'Synthetic next equity'}));
      if(kind!=='absent')yes(api.recordReserves({...input,fcrConstituted:kind==='zero'?0:2222,
        feoConstituted:kind==='zero'?0:666,sixMonthExpenseAmount:kind==='zero'?0:666,source:'Synthetic new period reserves'},
        {target:next,reason:'Synthetic period-specific reserve',expectedEpoch:jpWealthPersistenceEpoch()}));
      const before={state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length};
      const model=api.read(),planning=fxReservePanelData();
      return {kind,old,globalAfter:S.forex.reserves,next,modelReserve:model.reserves,planning,before,
        after:{state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),writes:__financeWrites.length}};
    }""", {'a': scope, 'kind': kind})
    expected = None if kind == 'absent' else 0 if kind == 'zero' else 2222
    assert result['planning']['fcrCur'] == expected, result
    assert result['planning']['feoCur'] == (None if kind == 'absent' else 0 if kind == 'zero' else 666), result
    assert result['before'] == result['after'] and result['old'] == result['globalAfter'], result
    assert result['planning']['status'] == 'PENDING_GOVERNANCE'
    codes = [item['code'] for item in result['planning']['findings']]
    if kind == 'conflict':
        assert result['planning']['capital'] is None and result['planning']['fcrReq'] is None
        assert 'NOMINAL_CAPITAL_DIVERGENCE' in codes, codes
    return {key: result[key] for key in ['kind', 'next', 'planning', 'modelReserve']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args(); root=args.root.resolve(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=[]
    cases=[('FIN-01 explicit B query and scoped A writes',query_b_while_a),
           ('FIN-02 independent planning refuses retired ledger import',independent_planning)]
    cases.extend(('FIN-03 '+kind+' current period reserve',lambda p,a,k=kind:reserves(p,a,k)) for kind in ['recorded','absent','zero','conflict'])
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options())
            for index,(name,fn) in enumerate(cases):
                ctx=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000}); install_bootstrap(ctx)
                page=ctx.new_page(); page.finance_evidence=out; page.finance_case=f'case-{index+1:02d}'
                errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/index.html'); ready(page)
                    # Empty-profile boot schedules its welcome after 350 ms.
                    # Close the visible welcome before installing the financial
                    # fixture so that a late callback cannot cover its controls.
                    page.locator('#jpwWelcomeClose').click(timeout=5000)
                    scope=page.evaluate(SEED); instrument(page)
                    detail=fn(page,scope); assert_fixture_requests(ctx); assert not errors, errors
                    row={'name':name,'status':'PASS','detail':detail,'pageErrors':errors}
                except AssertionError as error:
                    row={'name':name,'status':'PRODUCT_FAIL','error':str(error),'traceback':traceback.format_exc(),'pageErrors':errors}
                except Exception as error:
                    row={'name':name,'status':'TEST_HARNESS_FAIL','error':str(error),'traceback':traceback.format_exc(),'pageErrors':errors}
                rows.append(row)
                (out/'results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
                print(json.dumps({'name':name,'status':row['status'],'error':row.get('error','')[:500]},ensure_ascii=False),flush=True)
                ctx.close()
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    counts=dict(Counter(row['status'] for row in rows))
    metadata={'root':str(root),'time':datetime.now(timezone.utc).isoformat(),'syntheticOnly':True,
              'servedTreeReadOnly':True,'browser':'Disposable Chromium; service workers blocked',
              'sourceHashes':{path:hashlib.sha256((root/path).read_bytes()).hexdigest() for path in SOURCES},
              'testHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'counts':counts}
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False))
    print(json.dumps(counts),flush=True)
    return 0 if len(rows)==len(cases) and all(row['status']=='PASS' for row in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())

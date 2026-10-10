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
           'src/js/30-accounting/05-fx-planning/03-fx-state.js',
           'src/js/30-accounting/05-fx-planning/05-fx-ui.js',
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


def import_setup(page, profit=120):
    page.evaluate("""profit => {
      const yes=r=>{if(!r.ok)throw Error(JSON.stringify(r));return r;};
      yes(JPWLedger.record({data:'2026-09-02',resultado:profit,saldo:12000+profit}));
      yes(JPWFx.state.fxPlanCreate({name:'Synthetic FIN import',assumptions:{startMonth:'2026-09',horizonMonths:3,initialBalanceUsd:12000,defaultMonthlyReturn:.01}}));
      JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('actuals');
    }""", profit)
    settle(page)


def reviewed(page):
    assert page.locator('#fxpLedgerContributionsConfirmed').count() == 1, 'ACTUAL import lacks explicit contribution review'
    page.locator('#fxpLedgerComplete').check()
    page.locator('#fxpLedgerContributionsConfirmed').check()
    page.locator('#fxpLedgerPreviewBtn').click()
    assert page.locator('#fxpLedgerImportBtn').is_enabled(), page.locator('#fxpLedgerPreview').inner_text()
    geometry=page.locator('#fxpLedgerPreview').evaluate('el => ({width:el.clientWidth,content:el.scrollWidth})')
    assert geometry['width']>0 and geometry['content']<=geometry['width']+1, ('Financial preview overflows',geometry)
    page.locator('.fxp-ledger-import').screenshot(path=str(page.finance_evidence / (page.finance_case + '.png')))


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


def import_success(page, scope, profit):
    import_setup(page, profit)
    reviewed(page)
    before = snapshot(page)
    page.locator('#fxpLedgerImportBtn').click()
    settle(page)
    actual = page.evaluate("JPWFx.state.fxActivePlan().actuals['2026-09']||null")
    assert actual is not None and actual['profitUsd'] == profit, page.locator('#fxpLedgerImportErr').inner_text()
    assert actual['closureStatus'] == 'FINALIZED' and actual['contributionsConfirmed'] is True
    assert actual['source']['accountId'] == scope['accountId'] and actual['source']['periodId'] == scope['periodId']
    assert actual['confirmedSnapshot']['close'] == 12000 + profit
    assert snapshot(page)['writes'] == before['writes'] + 1, 'Import must cross the writer exactly once'
    disk = page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).fxPlanning.plan.actuals['2026-09']")
    assert disk == actual
    page.reload(); ready(page)
    restored = page.evaluate("JPWFx.state.fxActivePlan().actuals['2026-09']||null")
    assert restored == actual, 'Reload changed the confirmed ACTUAL'
    return {'profitUsd': profit, 'closingUsd': 12000 + profit, 'sourceRows': actual['source']['rows'], 'reloadExact': True}


def missing_confirmation(page, scope):
    import_setup(page)
    before = snapshot(page)
    page.locator('#fxpLedgerComplete').check(); page.locator('#fxpLedgerPreviewBtn').click()
    assert page.locator('#fxpLedgerContributionsConfirmed').count() == 1, 'Missing contribution control'
    assert page.locator('#fxpLedgerImportBtn').is_disabled(), 'Import enabled before contributions explicitly reviewed'
    refused = page.evaluate("""a => {const p=JPWLedger.monthlyActual('2026-09',{...a,complete:true});
      return JPWFx.state.fxPlanImportLedgerActual('2026-09',{...a,complete:true,sourceVersion:p.source.version});}""", scope)
    assert refused['ok'] is False and any('depósitos' in error for error in refused['errors']), refused
    unchanged(page, before)
    return {'domainRefusal': refused, 'buttonDisabled': True, 'noWrite': True}


def preview_invalidated(page, scope):
    import_setup(page); reviewed(page)
    before = snapshot(page)
    page.locator('#fxpLedgerContributionsConfirmed').focus(); page.keyboard.press('Space')
    assert not page.locator('#fxpLedgerContributionsConfirmed').is_checked()
    assert page.locator('#fxpLedgerImportBtn').is_disabled()
    assert page.evaluate('fxpLedgerPreview') is None
    page.keyboard.press('Space')
    assert page.locator('#fxpLedgerContributionsConfirmed').is_checked()
    assert page.locator('#fxpLedgerImportBtn').is_disabled(), 'Changed confirmation reused earlier preview'
    page.locator('#fxpLedgerPreviewBtn').click()
    page.locator('#fxpLedgerPeriod').select_option('')
    assert page.locator('#fxpLedgerImportBtn').is_disabled() and page.evaluate('fxpLedgerPreview') is None
    unchanged(page, before)
    return {'confirmationAndPeriodInvalidatePreview': True, 'noWrite': True}


def stale_preview(page, scope):
    import_setup(page); reviewed(page)
    page.evaluate("""() => {const r=JPWLedger.rows()[0];const corrected=JPWLedger.correct(r.id,{data:r.data,resultado:121,saldo:12121},{reason:'Synthetic corrected source',expectedVersion:r.version});if(!corrected.ok)throw Error(JSON.stringify(corrected));}""")
    before = snapshot(page)
    page.locator('#fxpLedgerImportBtn').click(); settle(page)
    assert page.evaluate("JPWFx.state.fxActivePlan().actuals['2026-09']||null") is None
    error = page.locator('#fxpLedgerImportErr').inner_text()
    assert 'origem mudou' in error, error
    unchanged(page, before)
    return {'error': error, 'noWrite': True}


def contributions_refused(page, scope):
    import_setup(page)
    added=page.evaluate("""() => JPWFx.state.fxPlanAddContribution({month:'2026-09',source:'prop',originalCurrency:'USD',originalAmount:10,usdAmount:10,affectsFxCostBasis:false})""")
    assert added['ok'], added
    page.evaluate("renderFxPlanning()"); reviewed(page)
    before = snapshot(page)
    page.locator('#fxpLedgerImportBtn').click(); settle(page)
    error = page.locator('#fxpLedgerImportErr').inner_text()
    assert 'não discrimina fluxos' in error, error
    unchanged(page, before)
    return {'error': error, 'nonzeroContributionRefused': True, 'noWrite': True}


def storage_refused(page, scope):
    import_setup(page); reviewed(page)
    before = snapshot(page)
    page.evaluate("""() => {const original=Storage.prototype.setItem;window.__financeSet=original;
      Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)throw new DOMException('Synthetic quota refusal','QuotaExceededError');return original.call(this,k,v);};}""")
    page.locator('#fxpLedgerImportBtn').click(); settle(page)
    error = page.locator('#fxpLedgerImportErr').inner_text()
    assert 'recusada' in error.lower(), error
    unchanged(page, before)
    assert page.evaluate("JPWFx.state.fxActivePlan().actuals['2026-09']||null") is None
    page.evaluate('() => { Storage.prototype.setItem=window.__financeSet; }')
    return {'error': error, 'rollbackExact': True, 'noWrite': True}


def mobile_import(page, scope, theme):
    page.set_viewport_size({'width':390,'height':900})
    page.evaluate("theme => { S.theme=theme; applyTheme(); }",theme)
    return import_success(page,scope,120)


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
      const model=api.read(),planning=JPWFx.state.fxReservePanelData();
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
    cases=[('FIN-01 explicit B query and scoped A writes', query_b_while_a),
           ('FIN-02 zero result UI import and reload',lambda p,a:import_success(p,a,0)),
           ('FIN-02 nonzero result UI import and reload',lambda p,a:import_success(p,a,120)),
           ('FIN-02 mobile light import and reload',lambda p,a:mobile_import(p,a,'light')),
           ('FIN-02 mobile dark import and reload',lambda p,a:mobile_import(p,a,'dark')),
           ('FIN-02 missing contribution confirmation',missing_confirmation),
           ('FIN-02 context and confirmation invalidate preview',preview_invalidated),
           ('FIN-02 corrected ledger invalidates source version',stale_preview),
           ('FIN-02 nonzero contributions remain refused',contributions_refused),
           ('FIN-02 refused write restores ACTUAL and storage',storage_refused)]
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

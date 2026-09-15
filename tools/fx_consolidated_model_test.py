#!/usr/bin/env python3
"""Consolidado FX model contracts. Synthetic fixtures, isolated browser, all network blocked."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import notes_launcher_test as launcher

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'src/js/10-domain/17-fx-consolidated-model.js'
FIXTURES = ROOT / 'tools/fixtures/mt5-consolidated'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence')
    args = parser.parse_args()
    expected = json.loads((FIXTURES / 'expected.json').read_text())
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(**launcher.launch_options())
        context = browser.new_context(service_workers='block')
        requests = []
        context.route('**/*', lambda route: (requests.append(route.request.url), route.abort()))
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<!doctype html><title>Synthetic model harness</title>')
        page.add_script_tag(content=MODEL.read_text())
        page.evaluate('(fixtures) => {window.F=fixtures;window.M=JPWFXConsolidated;}', {
            'en': (FIXTURES / 'classic-en.html').read_text(),
            'pt': (FIXTURES / 'classic-pt.html').read_text()})

        def check(name, script, predicate=lambda value: value is True):
            value = page.evaluate(script)
            assert predicate(value), f'{name}: {value!r}'
            checks.append(name)

        check('empty schema and unknown schema refusal', "() => M.validateState(M.emptyState()).ok && !M.validateState({schemaVersion:2}).ok")
        check('EN classic parser and fields', "() => {window.R=M.parseHTML(F.en);return {orders:R.orders.length,deals:R.deals.length,login:R.identity.login,currency:R.identity.currency,format:R.format};}", lambda v: v == {'orders':1,'deals':8,'login':'900001','currency':'USD','format':'mt5-classic-html-v1'})
        check('PT localized decimal and large ticket preservation', "() => {const r=M.parseHTML(F.pt),d=r.deals[0];return {ticket:d.ticket,netProfit:d.netResult,volume:d.volume};}", lambda v: v == expected['pt'])
        check('unknown HTML fails closed', "() => M.parseHTML('<table><tr><td>100</td></tr></table>').issues.some(x=>x.severity==='error')")
        check('impossible date refused', "() => M.parseHTML(F.en.replace('2026.01.02 10:00:00','2026.02.31 10:00:00')).issues.some(x=>x.severity==='error')")
        check('missing cost remains unknown', "() => {const r=M.parseHTML(F.pt.replace('<td>-1,20</td>','<td></td>'));return r.deals[0].commission===null && r.deals[0].netResult===null;}")
        check('safe inert parser malicious resources', "() => {window.__fxAttack=0;const r=M.parseHTML(F.en.replace('<body>', '<body><script>window.__fxAttack=1</scr'+'ipt><img src=\"https://invalid.example/image\" onerror=\"window.__fxAttack=2\"><iframe src=\"https://invalid.example/frame\"></iframe><style>@import url(https://invalid.example/css);</style>'));return r.deals.length===8 && window.__fxAttack===0;}")
        check('preview pure and first apply', "() => {window.A={id:'synthetic-en',name:'Synthetic',type:'demo',...R.identity};window.S0=M.emptyState();const before=JSON.stringify(S0);window.P=M.previewImport(S0,A,R,{fileHash:'fixture-en',importedAt:'2026-02-01T00:00:00Z'});window.AP=M.applyImport(S0,P,{});window.S1=AP.state;return P.ok && AP.ok && JSON.stringify(S0)===before && S1.accounts.length===1 && S1.receipts.length===1;}")
        check('exact repeat no-op', "() => {const p=M.previewImport(S1,A,R,{fileHash:'fixture-en',importedAt:'2026-02-02T00:00:00Z'}),a=M.applyImport(S1,p,{});return p.duplicate && a.ok && JSON.stringify(a.state)===JSON.stringify(S1);}")
        check('overlap without duplicate ledger', "() => {const p=M.previewImport(S1,A,R,{fileHash:'overlap',importedAt:'2026-02-02T00:00:00Z'}),a=M.applyImport(S1,p,{});return a.ok && a.state.accounts[0].deals.length===8 && p.counts.newDeals===0;}")
        check('cross-account identity mismatch blocks', "() => !M.previewImport(S1,{...A,login:'wrong'},R,{}).ok")
        check('missing identity requires explicit confirmation', "() => {const r=structuredClone(R);r.identity.server=null;const p=M.previewImport(S1,A,r,{fileHash:'missing-server'});return p.ok && p.requiresIdentityConfirmation && !M.applyImport(S1,p,{}).ok && M.applyImport(S1,p,{confirmIdentity:true}).ok;}")
        check('conflicting ticket requires revision and preserves before', "() => {const r=structuredClone(R);r.deals[2].profit=121;r.deals[2].netResult=119;const p=M.previewImport(S1,A,r,{fileHash:'revision',importedAt:'2026-02-03T00:00:00Z'});const x=M.applyImport(S1,p,{}),a=M.applyImport(S1,p,{acceptRevision:true});return p.conflicts.length===1 && !x.ok && a.ok && a.state.revisions.length===1 && S1.accounts[0].deals[2].profit===120;}")
        check('stale preview rejected', "() => {const s=structuredClone(S1);s.defaultAccountId='changed';return !M.applyImport(s,P,{}).ok;}")
        check('projection pure and independently calculated', "() => {const before=JSON.stringify(S1);window.PR=M.project(S1,[],{source:'mt5',accountId:A.id});return {unchanged:before===JSON.stringify(S1),metrics:Object.fromEntries(Object.entries(PR.metrics).map(([k,v])=>[k,v.value]))};}", lambda v: v['unchanged'] and all(abs(v['metrics'][k]-n)<1e-8 for k,n in expected['en'].items() if k not in ['orders','deals']))
        check('intraposition risks absent', "() => ['sharpe','tradingActivityPct','maxDepositLoadPct','mfe','mae'].every(k=>PR.metrics[k].value===null) && PR.series.equity.length===0 && PR.series.load.length===0")
        check('partial report cannot invent growth or balance path', "() => {const r=M.parseHTML(F.pt),a={id:'pt',...r.identity};const s=M.applyImport(M.emptyState(),M.previewImport(M.emptyState(),a,r,{}),{}).state;const p=M.project(s,[],{source:'mt5',accountId:'pt'});return p.metrics.growthPct.value===null && p.series.balance.length===0;}")
        check('summary is snapshot not ledger', "() => {const r={format:'mt5-summary-pdf-v1',identity:R.identity,period:{from:'2026-01-01',to:'2026-01-31',declared:true},orders:[],deals:[],positions:[],summary:{netProfit:85,equity:1585,sharpe:1.2},issues:[]};const s=M.applyImport(M.emptyState(),M.previewImport(M.emptyState(),A,r,{fileHash:'pdf'}),{}).state;const p=M.project(s,[],{source:'mt5',accountId:A.id});return p.records.length===0 && p.coverage.kind==='summary' && p.metrics.netProfit.value===85 && p.metrics.netProfit.availability==='imported' && p.series.balance.length===0;}")
        check('manual account and currency stay historical', "() => {const rows=[{operationId:'m1',accountId:'manual-a',currency:'USD',closedAt:'2026-01-04T00:00:00Z',netResult:100,instrument:'EURUSD',direction:'BUY'},{operationId:'m2',accountId:'manual-a',currency:'USD',closedAt:'2026-01-05T00:00:00Z',netResult:-20,instrument:'GBPUSD',direction:'SELL'},{operationId:'legacy',accountId:null,currency:null,netResult:500}];window.MR=rows;const p=M.project(S1,rows,{source:'manual',accountId:'manual-a',account:{id:'manual-a',currency:'BRL'}}),u=M.project(S1,rows,{source:'manual',accountId:'unassigned'});return p.metrics.netProfit.value===80 && p.records.length===2 && p.records.every(x=>x.currency==='USD') && p.metrics.balance.value===null && u.metrics.netProfit.value===null && u.records.length===1 && rows.length===3;}")
        check('mixed currencies never summed', "() => M.project(S1,[...MR,{operationId:'brl',accountId:'manual-a',currency:'BRL',netResult:20}],{source:'manual',accountId:'manual-a'}).metrics.netProfit.value===null")
        check('manual and MT5 never combine', "() => M.project(S1,MR,{source:'mt5',accountId:A.id}).metrics.netProfit.value===85")
        check('reversal and CloseBy retained distinctly', "() => {const r=M.parseHTML(F.pt.replace('saída','in/out'));const c=M.parseHTML(F.pt.replace('saída','out by'));return r.deals[0].entry==='inout' && c.deals[0].entry==='out_by';}")
        check('duplicate differing rows in one file rejected', "() => {const r=structuredClone(R);r.deals.push({...r.deals[2],profit:999});return !M.previewImport(S0,A,r,{}).ok;}")
        check('invalid report numeric refused', "() => {const r=structuredClone(R);r.deals[0].profit=Infinity;return !M.previewImport(S0,A,r,{}).ok;}")
        check('unknown source refused', "() => M.project(S1,MR,{source:'all'}).issues.some(x=>x.severity==='error')")
        check('trade distribution and cash flow metrics', "() => Object.fromEntries(['wins','losses','neutral','bestTrade','worstTrade','averageWin','averageLoss','maxWinStreak','maxLossStreak','initialBalance','deposits','withdrawals'].map(k=>[k,PR.metrics[k].value]))", lambda v: v == {'wins':2,'losses':1,'neutral':0,'bestTrade':118,'worstTrade':-103,'averageWin':98.5,'averageLoss':-103,'maxWinStreak':2,'maxLossStreak':1,'initialBalance':1000,'deposits':1500,'withdrawals':0})
        check('manual cumulative realized is not balance', "() => {const p=M.project(S1,MR,{source:'manual',accountId:'manual-a'});return p.series.realized.map(x=>x.value).join(',')==='100,80' && p.series.balance.length===0;}")
        check('summary-only multiaccount refuses implicit aggregate', "() => {const r={format:'mt5-summary-pdf-v1',identity:structuredClone(R.identity),period:{from:null,to:null,declared:false},orders:[],deals:[],positions:[],summary:{netProfit:85},issues:[]};let s=M.applyImport(M.emptyState(),M.previewImport(M.emptyState(),A,r,{}),{}).state;const b={...A,id:'second',login:'900003'};r.identity.login='900003';s=M.applyImport(s,M.previewImport(s,b,r,{}),{}).state;return M.project(s,[],{source:'mt5'}).metrics.netProfit.value===null;}")
        check('strict restored summary validation', "() => {const s=structuredClone(S1);s.accounts[0].summaries[0].values.netProfit='wrong';return !M.validateState(s).ok;}")
        check('unknown deal type cannot invent net performance', "() => {const r=structuredClone(R);r.deals[2].type='unknown_operation';const p=M.previewImport(S0,A,r,{});return !p.ok;}")
        check('exact decimal accumulation', "() => {const rows=[{operationId:'a',accountId:'decimal',currency:'USD',netResult:0.1},{operationId:'b',accountId:'decimal',currency:'USD',netResult:0.2}];return M.project(S1,rows,{source:'manual',accountId:'decimal'}).metrics.netProfit.value===0.3;}")
        check('previously seen report cannot bypass a newer revision', "() => {const r=structuredClone(R);r.deals[2].profit=121;const changed=M.applyImport(S1,M.previewImport(S1,A,r,{fileHash:'rev2'}),{acceptRevision:true}).state;const back=M.previewImport(changed,A,R,{fileHash:'fixture-en'});return !back.duplicate && back.conflicts.length===1 && M.applyImport(changed,back,{acceptRevision:true}).state.accounts[0].deals[2].profit===120;}")
        check('server punctuation preserves identity', "() => !M.previewImport(S1,{...A,server:'Synthetic Demo'},R,{}).ok")
        check('same-period PDF changes require explicit revision', "() => {const r={format:'mt5-summary-pdf-v1',identity:R.identity,period:{from:'2026-01-01',to:'2026-01-31',declared:true},orders:[],deals:[],positions:[],summary:{netProfit:85},issues:[]};const s=M.applyImport(S0,M.previewImport(S0,A,r,{importedAt:'2026-02-01T00:00:00Z'}),{}).state;r.summary.netProfit=99;const p=M.previewImport(s,A,r,{importedAt:'2026-02-02T00:00:00Z'});const a=M.applyImport(s,p,{acceptRevision:true});return p.conflicts.length===1 && !M.applyImport(s,p,{}).ok && a.ok && a.state.revisions.length===1 && M.project(a.state,[],{source:'mt5',accountId:A.id}).metrics.netProfit.value===99;}")
        check('manual projection whitelists historical context', "() => {const r={operationId:'secret-fixture',accountId:'safe',currency:'USD',netResult:10,investorPassword:'SYNTHETIC-DO-NOT-EXPOSE',recordContext:{accountInputs:{password:'SYNTHETIC-DO-NOT-EXPOSE'}}};return !JSON.stringify(M.project(S1,[r],{source:'manual',accountId:'safe'})).includes('SYNTHETIC-DO-NOT-EXPOSE');}")
        check('methodology and metric units explicit', "() => PR.methodologyVersion==='fx-descriptive-v1' && PR.metrics.profitFactor.unit==='ratio' && PR.metrics.tradeCount.unit==='count' && PR.metrics.winRate.unit==='%' && PR.metrics.netProfit.unit==='USD'")
        check('working orders remain distinct facts', "() => {const h=F.en.replace('<tr><th colspan=\"10\">Orders</th>','<tr><th colspan=\"10\">Working Orders</th>');const r=M.parseHTML(h);return r.orders.length===1 && r.orders[0].orderScope==='active' && r.deals.length===8;}")
        check('snapshot outside selected period not borrowed', "() => {const p=M.project(S1,[],{source:'mt5',accountId:A.id,from:'2026-01-02',to:'2026-01-03'});return p.metrics.equity.value===null && p.metrics.tradeCount.value===1 && p.metrics.netProfit.value===116;}")
        check('external identity cannot be duplicated under a new local ID', "() => M.previewImport(S1,{...A,id:'duplicate-link'},R,{}).error==='identity_already_linked'")
        check('absent report login always blocks even after confirmation', "() => {const r=structuredClone(R);r.identity.login=null;const p=M.previewImport(S0,A,r,{});return !p.ok && p.error==='account_number_required' && !M.applyImport(S0,p,{confirmIdentity:true}).ok;}")
        check('unassigned manual facts stay outside monetary aggregates', "() => {const p=M.project(S1,[{operationId:'unlinked',accountId:null,currency:'USD',netResult:10,closedAt:'2026-01-01T00:00:00Z'}],{source:'manual',accountId:'unassigned'});return p.records.length===1 && p.metrics.tradeCount.value===1 && p.metrics.netProfit.value===null && p.metrics.grossProfit.value===null && p.series.realized.length===0 && p.breakdowns.monthly[0].netProfit===null;}")
        check('complete history cannot extend past its proven bound', "() => {const r=structuredClone(R);r.coverage.completeHistory=false;r.period={from:'2026-03-01',to:'2026-03-01',declared:true};r.generatedAt='2026-03-02T00:00:00';r.summary={};r.orders=[];r.deals=[{...R.deals[2],ticket:'900',time:'2026-03-01T12:00:00',profit:100}];const s=M.applyImport(S1,M.previewImport(S1,A,r,{importedAt:'2026-03-02T00:00:00Z'}),{}).state;const p=M.project(s,[],{source:'mt5',accountId:A.id});return !p.coverage.completeHistory && p.coverage.partial && p.metrics.balance.value===null && p.metrics.growthPct.value===null && p.series.balance.length===0 && p.series.growth.length===0;}")
        check('new complete report may establish a later proven bound', "() => {const r=structuredClone(R);r.generatedAt='2026-03-02T00:00:00';r.summary={};r.deals.push({...R.deals[2],ticket:'900',time:'2026-03-01T12:00:00',profit:100});const s=M.applyImport(S1,M.previewImport(S1,A,r,{importedAt:'2026-03-02T00:00:00Z'}),{}).state;const p=M.project(s,[],{source:'mt5',accountId:A.id});return p.coverage.completeHistory && p.metrics.balance.value===1683;}")
        check('declared balance mismatch visible before and after import', "() => {const r=structuredClone(R);r.summary.balance=999999;const p=M.previewImport(S0,A,r,{});const a=M.applyImport(S0,p,{});const view=M.project(a.state,[],{source:'mt5',accountId:A.id});return p.ok && p.issues.some(x=>x.code==='balance_reconciliation_mismatch'&&x.message.includes('999999')&&x.message.includes('1585')) && p.reconciliation.status==='mismatch' && a.receipt.reconciliation.status==='mismatch' && view.issues.some(x=>x.code==='balance_reconciliation_mismatch') && view.metrics.balance.value===1585 && a.state.accounts[0].summaries[0].values.balance===999999;}")
        check('matching declared balance reconciliation is explicit', "() => M.previewImport(S0,A,R,{}).reconciliation.status==='matched'")
        check('missing account selection refuses all source aggregates', "() => {const rows=[{operationId:'a',accountId:'a',currency:'USD',netResult:10},{operationId:'b',accountId:'b',currency:'USD',netResult:20}];return ['manual','mt5'].every(source=>{const p=M.project(S1,rows,{source});return p.issues.some(x=>x.code==='account_required'&&x.severity==='error') && p.records.length===0 && p.metrics.netProfit.value===null && p.metrics.tradeCount.value===null;});}")
        check('profit factor explanation matches available result', "() => {const p=M.project(S1,[],{source:'mt5',accountId:A.id});return p.metrics.profitFactor.value===2 && p.metrics.profitFactor.reason.includes('antes') && !p.metrics.profitFactor.reason.includes('Sem perdas');}")
        check('manual win-rate explanation names manual operations', "() => {const p=M.project(S1,MR,{source:'manual',accountId:'manual-a'});return p.metrics.winRate.reason.includes('manuais') && !p.metrics.winRate.reason.includes('deal');}")
        check('partial new event inside old complete interval invalidates proof', "() => {const r=structuredClone(R);r.coverage.completeHistory=false;r.period={from:'2026-01-15',to:'2026-01-15',declared:true};r.summary={};r.orders=[];r.deals=[{...R.deals[2],ticket:'retroactive',time:'2026-01-15T12:00:00',profit:100}];const s=M.applyImport(S1,M.previewImport(S1,A,r,{}),{}).state;const p=M.project(s,[],{source:'mt5',accountId:A.id});return !p.coverage.completeHistory && p.series.balance.length===0 && p.metrics.growthPct.availability==='unavailable';}")
        check('partial revised event invalidates earlier complete proof', "() => {const r=structuredClone(R);r.coverage.completeHistory=false;r.period={from:'2026-01-03',to:'2026-01-03',declared:true};r.summary={};r.orders=[];r.deals=[{...R.deals[2],profit:121}];const s=M.applyImport(S1,M.previewImport(S1,A,r,{}),{acceptRevision:true}).state;const p=M.project(s,[],{source:'mt5',accountId:A.id});return !p.coverage.completeHistory && p.series.balance.length===0 && p.metrics.growthPct.availability==='unavailable';}")
        check('restored subset cannot claim original complete coverage', "() => {const s=structuredClone(S1);s.accounts[0].deals.splice(2,1);const p=M.project(s,[],{source:'mt5',accountId:A.id});return !p.coverage.completeHistory && p.series.balance.length===0;}")
        page.wait_for_timeout(100)
        assert not requests, f'Parser attempted network: {requests}'
        assert not errors, errors
        checks.append('zero network requests and page errors')
        context.close()
        browser.close()
    result = {'status':'PASS','checks':checks,'count':len(checks),'syntheticOnly':True,
              'realOwnerHTML':'NOT_RUN — unavailable','networkRequests':len(requests),
              'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [MODEL,Path(__file__),*sorted(FIXTURES.iterdir())]}}
    if args.evidence:
        Path(args.evidence).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()

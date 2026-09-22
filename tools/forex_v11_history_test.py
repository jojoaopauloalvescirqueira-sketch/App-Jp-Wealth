#!/usr/bin/env python3
"""Synthetic, read-only history oracles; no current account supplies past facts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import os

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'src/js/20-ui/16-operation-history.js'
HELPERS = 'src/js/00-core/05-helpers.js'
CASES = r"""() => {
  const results=[];
  const test=(name,fn)=>{try{fn();results.push({name,pass:true});}catch(e){results.push({name,pass:false,error:e.message});}};
  const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
  const record=(extra={})=>({operationId:'synthetic_history',instrument:'EURUSD',direction:'BUY',
    netResult:100,referenceBalance:10000,defenseCount:0,maxAccountPhaseReached:1,maxGridPhaseReached:1,
    openedAt:'2026-09-01T10:00:00Z',closedAt:'2026-09-02T10:00:00Z',
    ordersSnapshot:[{label:'synthetic_order',phase:1,gridIndex:0,status:'Fechada',result:100}],...extra});
  const usd=record({accountId:'account_A',periodId:'period_A',currency:'USD'});
  const brl=record({operationId:'synthetic_brl',recordContext:{accountId:'account_B',periodId:'period_B',
    accountInputs:{currency:'BRL'}},policySnapshot:{version:'JPW-FOREX-V11-T03-1',statuteVersion:'V11'}});
  const before=JSON.stringify(S);
  test('mixed currencies never sum or rank',()=>{const s=histStats([usd,brl]);
    assert(s.acumulado===null&&s.maior===null&&s.menor===null,JSON.stringify(s));});
  test('same currency across accounts and periods remains comparable',()=>{
    const s=histStats([usd,record({accountId:'account_C',periodId:'period_C',currency:'USD',netResult:-20})]);
    assert(s.acumulado===80&&s.maior===100&&s.menor===-20,JSON.stringify(s));});
  test('missing currency never borrows current selection',()=>{const s=histStats([record()]);
    const html=histRenderDetail(record());assert(s.acumulado===null&&!html.includes('$')&&html.includes('unidade ausente'),html);});
  test('null blank pending and boolean are not zero',()=>{for(const value of [null,undefined,'','PENDING',false]){
    const r=record({netResult:value});assert(histResultClass(r)!=='Neutra'&&histReturnPct(r)===null,'absent result '+value);
    const s=histStats([usd,r]);assert(s.acumulado===null&&s.maior===null&&s.menor===null,JSON.stringify(s));}});
  test('unknown result has explicit rate denominator',()=>{const s=histStats([usd,record({netResult:null})]);
    assert(s.n===2&&s.resultadosConhecidos===1&&s.taxaPositivas===100,JSON.stringify(s));});
  test('legacy phase never reads current matrix',()=>{assert(histPhaseName(1,record())==='LEGACY · Fase 2',histPhaseName(1,record()));});
  test('V11 phase uses captured policy version',()=>{assert(histPhaseName(1,brl)==='V11 · Fase 2',histPhaseName(1,brl));});
  test('unobserved phase remains unavailable',()=>{assert(histPhaseName(null,brl)==='—','null phase');});
  test('captured BRL displayed in detail and copied with identity',()=>{const detail=histRenderDetail(brl),copy=operationCopyProjection(brl);
    assert(detail.includes('R$')&&copy.includes('BRL')&&copy.includes('account_B')&&copy.includes('period_B'),copy);
    assert(!copy.includes('Conta, perfil, período e métricas finais não foram capturados'),'false blanket absence');});
  test('finalization captured context supported without current fallback',()=>{const r=record({finalizationContext:{
    accountId:'account_F',periodId:'period_F',accountInputs:{currency:'EUR'}}});
    const copy=operationCopyProjection(r);assert(copy.includes('EUR')&&copy.includes('account_F')&&copy.includes('period_F'),copy);});
  test('conflicting captured currencies are unavailable',()=>{const r={...usd,recordContext:{currency:'BRL'}};
    const s=histStats([r]);assert(s.acumulado===null&&!histRenderDetail(r).includes('$'),JSON.stringify(s));});
  test('explicit null currency blocks later captured-context fallback',()=>{const r=record({currency:null,
    policySnapshot:{policyVersion:'LEGACY_UNRESOLVED'},recordContext:{accountId:'A',periodId:'P',accountInputs:{currency:'USD'}},
    finalizationContext:{accountId:'A',periodId:'P',accountInputs:{currency:'USD'}}});
    assert(histCapturedContext(r).currency===null&&histStats([r]).acumulado===null,'null overwritten by context currency');
    assert(!histRenderDetail(r).includes('$')&&!operationCopyProjection(r).includes('$'),'unit invented in detail/copy');});
  test('unknown historical result and order copy do not fabricate zero',()=>{const r=record({netResult:null,ordersSnapshot:[{phase:1,gridIndex:0,status:'Fechada',result:null}]});
    const html=histRenderDetail(r),copy=operationCopyProjection(r);assert(!html.includes('$0,00')&&!copy.includes('Resultado líquido registrado:'),copy);});
  test('historical copy excludes account secrets and final equity inference',()=>{const r=record({...brl,
    recordContext:{...brl.recordContext,accountInputs:{currency:'BRL',equity:9876,password:'SECRET_SYNTHETIC'}}});
    const copy=operationCopyProjection(r);assert(!copy.includes('SECRET_SYNTHETIC')&&!copy.includes('9876')&&!copy.includes('DD:'),copy);});
  test('all projections preserve raw state',()=>{assert(JSON.stringify(S)===before,'state mutated');});
  test('opaque broker HASH survives detail copy and exact search',()=>{
    const hash='0009007199254740993123456789-XyZ';
    const r=record({ordersSnapshot:[{label:'INTERNAL-1',brokerHash:hash,phase:1,status:'Fechada',result:0}]});
    assert(histRenderDetail(r).includes(hash)&&operationCopyProjection(r).includes(hash),'HASH missing');
    histState.query=hash;assert(histFilter([r]).length===1,'HASH cannot be found');histState.query='';
  });
  test('legacy missing broker HASH stays absent and is never inferred',()=>{
    const r=record();const prior=JSON.stringify(r);const html=histRenderDetail(r),copy=operationCopyProjection(r);
    assert(html.includes('Não informado')&&!copy.includes('HASH da corretora:'),'legacy HASH inferred');
    assert(JSON.stringify(r)===prior,'history rewritten');
  });
  return results;
}"""


def browser_cases():
    import operation_history_test as history
    from playwright.sync_api import sync_playwright
    os.chdir(ROOT)
    server,url=history.serve()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**history.launcher.launch_options())
            context,page,observed=history.prepare_page(browser,url)
            build=page.evaluate("typeof JP_WEALTH_BUILD_ID==='undefined'?null:JP_WEALTH_BUILD_ID")
            results=page.evaluate(CASES)
            page.evaluate("""() => {
              S.operationHistory={schemaVersion:1,records:[
                {operationId:'synthetic_usd',accountId:'A',periodId:'P1',currency:'USD',netResult:100,ordersSnapshot:[]},
                {operationId:'synthetic_brl',accountId:'B',periodId:'P2',currency:'BRL',netResult:200,ordersSnapshot:[]},
                {operationId:'synthetic_unknown',netResult:null,ordersSnapshot:[]} ]};
              histState={instrument:'all',direction:'all',result:'all',query:'',selected:null};
              window.__historyBefore={state:JSON.stringify(S),storage:JSON.stringify({...localStorage})};
              JPWNavigation.navigateLocal('exec','history');
            }""")
            page.locator('#histResult').select_option('Não informado')
            row=page.locator('[data-hist-id="synthetic_unknown"]')
            row.focus();page.keyboard.press('Enter')
            shown=page.locator('[data-hist-detail="synthetic_unknown"]').is_visible()
            amount=page.locator('#histStats .hist-stat').filter(has=page.locator('.hist-stat-l',has_text='Resultado líquido acumulado')).locator('.hist-stat-v').inner_text()
            preserved=page.evaluate("JSON.stringify(S)===__historyBefore.state && JSON.stringify({...localStorage})===__historyBefore.storage")
            results.extend([{'name':'unknown-result filter and keyboard detail','pass':shown},
                            {'name':'unknown-result displayed aggregate unavailable','pass':amount=='—'},
                            {'name':'browser navigation filter and detail preserve state and storage','pass':preserved},
                            {'name':'browser zero page or console errors','pass':not observed['pageerror'] and not observed['console']}])
            context.close();browser.close()
            return {'buildId':build,'results':results,'observed':observed}
    finally:server.shutdown()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--browser',action='store_true')
    args=ap.parse_args()
    script="""const fs=require('fs'),vm=require('vm');
const ctx={window:{},S:{matrix:[{nome:'CURRENT'}, {nome:'CURRENT MUTABLE PHASE'}]},Intl,Date,Number,JSON,
  JPWForex:{state:{operationalSelection:()=>({accountId:null,periodId:null}),accountContext:()=>({status:'NOT_COMPUTABLE',value:null})}}};
ctx.window=ctx;vm.createContext(ctx);
let helper=fs.readFileSync(process.argv[1],'utf8');
vm.runInContext(helper.slice(0,helper.indexOf('const fmtPct=')),ctx);
vm.runInContext(`function esc(s){return String(s??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));}`,ctx);
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),ctx);
process.stdout.write(JSON.stringify(vm.runInContext('('+process.argv[3]+')()',ctx)));
"""
    paths=[SOURCE,HELPERS]
    if args.browser:
        paths=['index.html','build-id.js']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'src').rglob('*.js'))]+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'src').rglob('*.css'))]
    before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    run=subprocess.run(['node','-e',script,str(ROOT/HELPERS),str(ROOT/SOURCE),CASES],text=True,capture_output=True)
    results=json.loads(run.stdout) if run.returncode==0 else []
    browser=browser_cases() if args.browser else None
    if browser:results.extend(browser['results'])
    after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in before}
    passed=run.returncode==0 and all(r['pass'] for r in results) and before==after
    report={'kind':'node-and-chromium' if args.browser else 'isolated-node-source','sourcesBefore':before,'sourcesAfter':after,'stable':before==after,
            'browser':browser,
            'rawExit':run.returncode,'stderr':run.stderr,'results':results,'pass':passed}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence')
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    for r in results:print(('PASS ' if r['pass'] else 'FAIL ')+r['name']+('' if r['pass'] else ': '+r['error'][:250]))
    if run.stderr:print(run.stderr)
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':main()

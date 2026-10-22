#!/usr/bin/env python3
"""Real current Planning renderer with synthetic prepared read-model rows.

The query boundary supplies prepared points for this presentation-only test.
Actual SVG generation, finite/missing handling and DOM are unchanged.
USD/BRL conversion is tested by the pure engine; the chart now displays USD.
"""
import argparse, hashlib, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from fx_planning_test import ROOT,serve,prepare_page

PROBE=r'''() => {
 const api=JPWPlanning,results=[],check=(name,ok,detail)=>results.push({name,status:ok?'PASS':'PRODUCT_FAIL',detail});
 const made=api.commands.execute('createAccount',{name:'Synthetic chart',startMonth:'2026-01',initialUsd:100,profileId:'base',monthlyContributionUsd:0,goals:{adequate:null,ideal:{value:30,currency:'USD'}}},api.queries.token());
 if(!made.ok)throw Error(JSON.stringify(made));
 JPWNavigation.navigate('planning');
 const before=JSON.stringify(S),disk=JSON.stringify(localStorage),old=api.queries.view;
 const months=['2026-01','2026-02','2026-03','2026-04','2026-05'];
 const rows=months.map((month,i)=>({month,openUsd:100,rate:0,resultUsd:0,contributionUsd:0,withdrawalUsd:0,closeUsd:[100,105,null,0,null][i],closeBrl:null,phase:i===3?'confirmed':'projected',finalized:i===3,issues:[]}));
 const model={rows,referenceRows:months.map(month=>({month,closeUsd:100})),goals:{},confirmed:{balanceUsd:null,contributionsUsd:0,resultUsd:0},accounts:[],issues:[]};
 try{
  api.queries.view=()=>structuredClone(model);api.ui.render();
  const host=document.querySelector('#planning'),svg=host.querySelector('svg[data-pl-chart]'),curve=svg?.querySelector('.pl-line-projected'),d=curve?.getAttribute('d')||'';
  check('missing month splits the real SVG path',!!svg&&(d.match(/M/g)||[]).length===2&&(d.match(/L/g)||[]).length===1,d);
  check('genuine zero remains a visible confirmed point',svg?.querySelectorAll('[data-pl-confirmed-point]').length===1&&svg.querySelector('[data-pl-confirmed-point]').getAttribute('cy')==='240.00');
  check('SVG coordinates are finite',!!svg&&!/(NaN|Infinity|undefined|null)/.test(svg.outerHTML));
  const metrics=[...host.querySelectorAll('.pl-metric')];
  check('missing final balance is unavailable, never the last known zero',metrics.find(m=>m.textContent.includes('Último saldo projetado'))?.querySelector('strong')?.textContent==='—');
  model.rows=months.map(month=>({month,closeUsd:null,phase:'pending',issues:[]}));model.referenceRows=[];api.ui.render();
  check('all absent values produce no fabricated curve',!host.querySelector('svg[data-pl-chart]')&&host.textContent.includes('Trajetória indisponível'));
  model.rows=[{month:'2026-01',closeUsd:0,phase:'confirmed',issues:[]}];api.ui.render();
  check('all-zero trajectory is available and finite',!!host.querySelector('svg[data-pl-chart]')&&!/(NaN|Infinity|undefined|null)/.test(host.querySelector('svg[data-pl-chart]').outerHTML));
  check('presentation does not mutate financial state or storage',before===JSON.stringify(S)&&disk===JSON.stringify(localStorage));
 }finally{api.queries.view=old;api.ui.render();}
 return results;
}'''
def main():
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,default=ROOT/'tools/.artifacts/monthly-charts');a=p.parse_args();a.artifacts.mkdir(parents=True,exist_ok=True)
    paths=['src/js/30-accounting/06-planning/01-engine.js','src/js/30-accounting/06-planning/03-ui.js']
    before={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}
    server,url=serve();results=[]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):opts['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**opts);context,page,observed=prepare_page(browser,url)
            results.extend(page.evaluate(PROBE))
            if observed['pageerror']:results.append({'name':'browser page errors','status':'PRODUCT_FAIL','detail':observed['pageerror']})
            context.close();browser.close()
    finally:server.shutdown()
    after={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}
    status='PASS' if results and before==after and all(r['status']=='PASS' for r in results) else 'PRODUCT_FAIL'
    (a.artifacts/'receipt.json').write_text(json.dumps({'status':status,'sourceHashes':before,'sourceHashesAfter':after,'results':results},ensure_ascii=False,indent=2)+'\n')
    for r in results:print('['+r['status']+'] '+r['name'],flush=True)
    return 0 if status=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

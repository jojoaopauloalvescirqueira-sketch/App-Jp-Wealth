#!/usr/bin/env python3
"""Presentation regression: real planning chart renderer, disposable browser.

Synthetic ready-made series exercise the real SVG and currency presentation.
No financial formulas or chart helpers are replaced and nothing is persisted.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from fx_planning_test import serve, prepare_page, ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', type=Path, default=ROOT / 'tools/.artifacts/monthly-charts')
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    paths = ['src/js/30-accounting/05-fx-planning/04-fx-charts.js',
             'src/js/20-ui/06-chart-terminal-chrome.js']
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
    server, url = serve()
    results = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context, page, observed = prepare_page(browser, url)
            result = page.evaluate('''() => {
              const c=JPWFx.charts, results=[];
              const check=(name,ok,detail)=>results.push({name,status:ok?'PASS':'PRODUCT_FAIL',detail});
              const before=JSON.stringify(S), storage=JSON.stringify(localStorage);
              check('absence is unavailable in USD and BRL',
                [null,undefined,NaN,Infinity,false].every(close=>
                  c.fxChartConvert({close},'usd',{})===null &&
                  c.fxChartConvert({close},'brl',{projectedRate:5})===null));
              check('genuine zero remains a plotted value',
                c.fxChartConvert({close:0},'usd',{})===0 &&
                c.fxChartConvert({close:0},'brl',{projectedRate:5})===0);
              const groups=c.fxChartSegments([
                {i:0,y:100},{i:1,y:105},{i:2,y:null},{i:3,y:110},{i:4,y:115},{i:6,y:120}]);
              check('gaps split observed sequences',JSON.stringify(groups.map(g=>g.map(p=>p.i)))==='[[0,1],[3,4],[6]]',groups);
              const plan={baseline:{projectedFxRate:5},current:{projectedFxRate:5}};
              const months=['2026-01','2026-02','2026-03','2026-04','2026-05'];
              const forecast=months.map((month,i)=>({month,close:[100,105,null,120,null][i],phase:'forecast'}));
              const ov={forecast,baseline:forecast.map(r=>({...r})),actual:[],lastClosedMonth:null};
              const box=document.createElement('div'); document.body.append(box);
              c.fxDrawMainChart(box,plan,ov,'usd');
              const dotted=[...box.querySelectorAll('path[data-fan-series="plan"]')].map(p=>p.getAttribute('d'));
              const isolated=box.querySelectorAll('circle[data-fan-series="plan"]').length;
              check('SVG never bridges a missing month',dotted.length===1 && isolated===1 &&
                dotted[0].split('L').length===2,{paths:dotted,isolated});
              check('missing end of horizon is not the last known balance',
                c.fxMainChartSummaryText(plan,ov,'usd').includes('projeção vigente indisponível') &&
                c.fxMainChartSummaryText(plan,ov,'usd').includes('Cobertura incompleta'));
              check('SVG contains only finite coordinates',!/(NaN|Infinity|undefined|null)/.test(box.innerHTML));
              c.fxDrawReturnsChart(box,{baseline:[{month:'2026-01',rate:null}],actual:[{month:'2026-01',rate:0}]});
              check('missing planned rate is not a zero-return bar',
                box.querySelectorAll('rect[fill="var(--violet)"]').length===0 &&
                box.textContent.includes('planejado indisponível') && box.textContent.includes('0,00%'));
              box.remove();
              check('presentation does not mutate financial state or storage',
                JSON.stringify(S)===before && JSON.stringify(localStorage)===storage);
              return results;
            }''')
            results.extend(result)
            if observed['pageerror']:
                results.append({'name':'browser errors','status':'PRODUCT_FAIL','detail':observed['pageerror']})
            context.close()
            browser.close()
    finally:
        server.shutdown()
    after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
    receipt={'sourceHashes':hashes,'sourceHashesAfter':after,'results':results,
             'status':'PASS' if all(r['status']=='PASS' for r in results) and hashes==after else 'PRODUCT_FAIL'}
    (args.artifacts/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    for row in results:
        print(f"[{row['status']}] {row['name']}")
    raise SystemExit(0 if receipt['status']=='PASS' else 1)


if __name__=='__main__':
    main()

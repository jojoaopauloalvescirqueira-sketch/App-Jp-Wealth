#!/usr/bin/env python3
"""JPW Scenario Fan: real renderer/engine/commands in synthetic browser profiles.

No financial producer is replaced. Public feeds alone use the established
bootstrap fixture. Screenshots never contain a personal account or workbook.
"""
import argparse
import hashlib
import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from fx_planning_test import ROOT, serve, prepare_page

PATHS = ['src/js/20-ui/08-scenario-fan.js', 'src/styles/app.css']

CORE = r'''() => {
  const before=JSON.stringify(S), disk=JSON.stringify(localStorage), results=[];
  const check=(name,ok,detail)=>results.push({name,status:ok?'PASS':'PRODUCT_FAIL',detail});
  const box=document.createElement('div');box.style.width='800px';document.body.append(box);
  const points=values=>values.map((value,i)=>({month:['2026-01','2026-02','2026-03','2026-04'][i],value,state:'PROJECTED',origin:'Fixture sintética',reason:value===null?'Previsão retirada':''}));
  const model=series=>({identity:'synthetic-component',revision:'test',unit:'USD',title:'Trajetórias sintéticas',months:['2026-01','2026-02','2026-03','2026-04'],projectionStartMonth:'2026-01',series});
  const plan={id:'plan',kind:'plan',name:'PLAN',points:points([100,110,null,0])};
  JPWScenarioFan.render(box,model([plan]));
  check('PLAN sozinho não fabrica uma faixa',box.querySelectorAll('[data-fan-band]').length===0);
  const curves=[...box.querySelectorAll('[data-fan-series="plan"]')];
  check('Lacuna interrompe a curva; zero continua disponível',curves.length===2&&box.querySelector('.sf-endpoints').textContent.includes('0 USD'),curves.map(el=>el.outerHTML));
  box.querySelector('select').value='2026-03';box.querySelector('select').dispatchEvent(new Event('change',{bubbles:true}));
  check('Consulta de lacuna não reutiliza o mês anterior',box.querySelector('[data-fan-reading]').textContent.includes('N/A')&&!box.querySelector('[data-fan-reading]').textContent.includes('110 USD'));
  const baseline={id:'baseline',kind:'baseline',name:'Baseline',points:points([80,80,80,80])};
  JPWScenarioFan.render(box,model([plan,baseline]));
  check('Baseline não cria nem compõe uma faixa',box.querySelectorAll('[data-fan-band]').length===0);
  const crossing=model([{id:'plan',kind:'plan',name:'PLAN',points:points([0,10,null,null])},{id:'s1',kind:'scenario',name:'Cruza PLAN',points:points([10,0,null,null])}]);
  JPWScenarioFan.render(box,crossing);
  const polygon=box.querySelector('[data-fan-band]');
  const coordinates=polygon?[...polygon.points].map(p=>({x:p.x,y:p.y})):[];
  check('Faixa respeita a interseção entre segmentos',coordinates.length===6&&Math.abs(coordinates[1].x-(coordinates[0].x+coordinates[2].x)/2)<.02&&Math.abs(coordinates[1].y-coordinates[4].y)<.02,coordinates);
  crossing.series.push({id:'s2',kind:'scenario',name:'Ausente',points:points([null,5,null,null])});
  JPWScenarioFan.render(box,crossing);
  check('Faixa não oculta lacuna de uma hipótese selecionada',box.querySelectorAll('[data-fan-band]').length===0);
  const hostile=model([{id:'unsafe',kind:'plan',name:'<img src=x onerror="window.__injected=true">',points:points([-1234567890.12,0,null,1234567890.12])}]);
  JPWScenarioFan.render(box,hostile);
  check('Nomes são texto; valores negativos e longos permanecem acessíveis',!box.querySelector('img')&&!window.__injected&&box.querySelector('.sf-endpoints').textContent.includes('1.234.567.890,12'));
  check('Coordenadas do SVG são finitas',!/(NaN|Infinity|undefined|null)/.test(box.querySelector('svg').outerHTML));
  const empty=model([{id:'plan',kind:'plan',name:'PLAN',points:points([null,null,null,null])}]);
  JPWScenarioFan.render(box,empty);
  check('Ausência completa tem motivo e tabela, sem curva falsa',box.textContent.includes('Trajetória indisponível')&&!box.querySelector('svg')&&box.querySelector('table'));
  let calls=0;const handle=JPWScenarioFan.render(box,model([plan]),{onInspect:()=>calls++});
  const old=box.querySelector('select');handle.destroy();old.value='2026-02';old.dispatchEvent(new Event('change'));
  check('Descarte remove interações da instância anterior',calls===0);
  box.remove();check('Renderização e consulta não escrevem estado financeiro ou preferências',before===JSON.stringify(S)&&disk===JSON.stringify(localStorage));
  return results;
}'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',type=Path,default=ROOT/'tools/.artifacts/scenario-fan');args=parser.parse_args();args.artifacts.mkdir(parents=True,exist_ok=True)
    source={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS};results=[];server,url=serve()
    try:
        with sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):options['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**options);context,page,observed=prepare_page(browser,url)
            results.extend(page.evaluate(CORE))
            # Generic component remains independently tested. The retired
            # planning adapter and named-scenario UI are no longer its consumer.
            layout=page.evaluate(MATRIX)
            results.extend(layout)
            if observed['pageerror']:results.append({'name':'Erros do navegador','status':'PRODUCT_FAIL','detail':observed['pageerror']})
            context.close();browser.close()
    finally:server.shutdown()
    after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS}
    receipt={'scope':'generic shared scenario-fan component; retired planning adapter explicitly removed','sourceHashes':source,'sourceHashesAfter':after,'results':results,'status':'PASS' if source==after and results and all(x['status']=='PASS' for x in results) else 'PRODUCT_FAIL'}
    (args.artifacts/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    for row in results:print('['+row['status']+'] '+row['name']+(' '+str(row.get('detail')) if row['status']!='PASS' else ''))
    raise SystemExit(0 if receipt['status']=='PASS' else 1)

MATRIX=r'''() => {
 const before={state:JSON.stringify(S),disk:JSON.stringify(localStorage)},box=document.createElement('div');document.body.append(box);
 box.style.cssText='width:100%;max-width:900px;';
 const model={identity:'generic-component',revision:'test',unit:'USD',title:'Synthetic shared component',months:['2026-01','2026-02'],projectionStartMonth:'2026-01',series:[{id:'plan',kind:'plan',name:'PLAN',points:[{month:'2026-01',value:0},{month:'2026-02',value:1234567890.12}]}]};
 const handle=JPWScenarioFan.render(box,model),plot=box.querySelector('svg');plot.focus();plot.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));
 const end=box.querySelector('select').value;plot.dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));
 const keyboard=end==='2026-02'&&box.querySelector('select').value==='2026-01';
 const results=[{name:'Generic component keyboard Home/End preserves exact month',status:keyboard?'PASS':'PRODUCT_FAIL'}];
 for(const theme of ['light','dark']){
  document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme;
  for(const width of [320,390,768,1024,1440]){
   box.style.width=width+'px';
   const values=[...box.querySelectorAll('.sf-endpoint strong')].map(el=>({font:parseFloat(getComputedStyle(el).fontSize),width:el.clientWidth,scroll:el.scrollWidth}));
   results.push({name:'Shared component finite accessible values '+theme+' '+width,status:values.length>0&&values.every(v=>v.font>=12&&v.scroll<=v.width+1)&&!/(NaN|Infinity)/.test(plot.outerHTML)?'PASS':'PRODUCT_FAIL',detail:values});
  }
 }
 handle.destroy();box.remove();results.push({name:'Component keyboard/size/theme probes do not write',status:before.state===JSON.stringify(S)&&before.disk===JSON.stringify(localStorage)?'PASS':'PRODUCT_FAIL'});
 return results;
}'''
if __name__=='__main__':main()

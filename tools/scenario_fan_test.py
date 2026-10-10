#!/usr/bin/env python3
"""JPW Scenario Fan: real renderer/engine/commands in synthetic browser profiles.

No financial producer is replaced. Public feeds alone use the established
bootstrap fixture. Screenshots never contain a personal account or workbook.
"""
import argparse
import hashlib
import json
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from fx_planning_test import ROOT, serve, prepare_page

PATHS = ['src/js/20-ui/08-scenario-fan.js', 'src/styles/app.css',
         'src/js/30-accounting/05-fx-planning/04-fx-charts.js',
         'src/js/30-accounting/05-fx-planning/05-fx-ui.js']

SEED = r'''() => {
  S.fxPlanning={schemaVersion:1,plan:null,auditLog:[]};
  const state=JPWFx.state;
  const made=state.fxPlanCreate({name:'Demonstração sintética — trajetórias',assumptions:{
    startMonth:'2026-01',horizonMonths:24,initialBalanceUsd:1000,
    defaultMonthlyReturn:.01,projectedFxRate:5,
    recurringContributions:{personalUsd:20,propUsd:10}}});
  if(!made.ok)throw Error(JSON.stringify(made));
  for(const month of ['2026-01','2026-02','2026-03']){
    const r=state.fxPlanFinalizeMonth(month,{inputType:'rate',returnRate:.008,valuationFxRate:5,contributionsConfirmed:true});
    if(!r.ok)throw Error(JSON.stringify(r));
  }
  const ids=[];
  for(const [name,rate,deposit] of [['Hipótese A · depósitos maiores',.012,45],['Hipótese B · rentabilidade menor',.005,20],['Hipótese C · não selecionada',0,10]]){
    const r=state.fxScenarioSave({name});if(!r.ok)throw Error(JSON.stringify(r));ids.push(r.id);
    const revised=state.fxPlanReviseFromMonth('2026-04',{rate,personalUsd:deposit,propUsd:10},'Premissas fictícias para prova de apresentação',r.id);
    if(!revised.ok)throw Error(JSON.stringify(revised));
  }
  JPWNavigation.navigate('forex-planning');JPWFx.ui.selectView('overview');
  return ids;
}'''

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
    source={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS}; results=[]; server,url=serve()
    def case(name,fn):
        try:
            detail=fn();results.append({'name':name,'status':'PASS','detail':detail})
        except Exception:
            results.append({'name':name,'status':'PRODUCT_FAIL','detail':traceback.format_exc()})
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch();context,page,observed=prepare_page(browser,url)
            results.extend(page.evaluate(CORE));ids=page.evaluate(SEED)
            def adapters():
                return page.evaluate('''ids=>{
                  const p=JPWFx.state.fxActivePlan(),ov=JPWFx.engine.fxOverview(p),c=JPWFx.charts;
                  const before=JSON.stringify(p),model=c.fxScenarioFanModel(p,ov,'usd',{scenarioIds:ids,baseline:true});
                  if(model.series.filter(s=>s.kind==='scenario').length!==2)throw Error('more than two');
                  for(const s of model.series){
                    const rows=s.kind==='scenario'?JPWFx.engine.fxScenarioTimeline(p,p.scenarios.find(x=>x.id===s.id)):s.kind==='baseline'?ov.baseline:ov.forecast;
                    for(const pt of s.points){if(pt.value!==null){const row=rows.find(r=>r.month===pt.month);if(!row||pt.value!==row.close)throw Error(s.id+' value mismatch '+pt.month);}}
                  }
                  const brl=c.fxScenarioFanModel(p,ov,'brl',{scenarioIds:ids.slice(0,2)});
                  for(const s of brl.series){if(s.kind==='actual')continue;const scenario=p.scenarios.find(x=>x.id===s.id);const rate=scenario?scenario.assumptions.projectedFxRate:p.current.projectedFxRate;
                    const usd=model.series.find(x=>x.id===s.id);for(const pt of s.points){if(pt.value!==null){const row=usd.points.find(x=>x.month===pt.month);if(Math.abs(pt.value-row.value*(pt.state==='FINALIZED'?5:rate))>1e-8)throw Error('FX context '+s.id);}}
                  }
                  if(JSON.stringify(p)!==before)throw Error('mutated plan');return {months:model.months.length,series:model.series.map(s=>s.name)};
                }''',ids)
            case('Adapter corresponde aos produtores reais, em USD e BRL, sem mutação',adapters)
            def compare():
                page.locator('#fxpChartCompare').evaluate('(el)=>el.open=true') if page.locator('#fxpChartCompare').count() else page.locator('[data-fxp-compare-scenario]').first.evaluate('(el)=>el.closest("details").open=true')
                before=page.evaluate('({state:JSON.stringify(S),disk:JSON.stringify(localStorage)})')
                for item in ids[:2]:page.locator('[data-fxp-compare-scenario][value="'+item+'"]').check()
                assert page.locator('[data-fxp-compare-scenario][value="'+ids[2]+'"]').is_disabled()
                assert page.locator('[data-fxp-compare-scenario]:checked').count()==2
                assert page.locator('#fxpMainChart [data-fan-band]').count()>0
                assert before==page.evaluate('({state:JSON.stringify(S),disk:JSON.stringify(localStorage)})')
            case('Selecionar duas hipóteses limita a terceira e não grava',compare)
            def keyboard():
                plot=page.locator('#fxpMainChart svg');plot.focus();plot.press('End');assert page.locator('#fxpMainChart select').input_value()=='2027-12';plot.press('Home');assert page.locator('#fxpMainChart select').input_value()=='2026-01'
            case('Consulta do gráfico acessível por teclado',keyboard)
            def draft():
                page.locator('#fxpMainChart select[aria-label="Mês da consulta"]').select_option('2026-06')
                page.evaluate("JPWFx.ui.selectView('table')")
                assert page.locator('#fxpMainChart select[aria-label="Mês da consulta"]').input_value()=='2026-06'
                field=page.locator('#fxpMonth-2026-04-rate');field.fill('2,75');field.evaluate('(el)=>el.setSelectionRange(1,3)')
                before=page.evaluate('({state:JSON.stringify(S),disk:JSON.stringify(localStorage)})');node=field.element_handle()
                page.locator('[data-fxp-compare-scenario]').first.evaluate('(el)=>el.closest("details").open=true')
                page.locator('[data-fxp-compare-baseline]').check()
                assert node.evaluate('(el)=>el===document.querySelector("#fxpMonth-2026-04-rate")')
                assert field.input_value()=='2,75';assert before==page.evaluate('({state:JSON.stringify(S),disk:JSON.stringify(localStorage)})')
                page.evaluate("JPWFx.ui.selectView('overview');JPWFx.ui.selectView('table')")
                assert page.locator('#fxpMainChart select[aria-label="Mês da consulta"]').input_value()=='2026-06'
                assert page.locator('[data-fxp-compare-scenario]:checked').count()==2
                assert page.locator('#fxpMonth-2026-04-rate').input_value()=='2,75'
            case('Comparação, baseline e navegação preservam campo e rascunho mensal',draft)
            def matrix():
                page.evaluate("JPWFx.ui.selectView('overview')")
                measurements=[]
                for layout in ['sidebar','topbar','glass','submenu']:
                    page.evaluate('(layout)=>mountNavigationLayout(layout)',layout)
                    for width in [320,390,768,1024,1440]:
                        page.set_viewport_size({'width':width,'height':1000})
                        for theme in ['light','dark']:
                            page.evaluate('(theme)=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme;}',theme)
                            page.locator('#fxpMainChart').scroll_into_view_if_needed();page.wait_for_timeout(100)
                            item=page.evaluate('''()=>({pageWidth:innerWidth,scroll:document.documentElement.scrollWidth,plot:document.querySelector('#fxpMainChart svg')?.getBoundingClientRect().height,font:getComputedStyle(document.querySelector('#fxpMainChart .sf-endpoint strong')).fontSize})''')
                            assert item['scroll']<=width+1,item;assert item['plot']>=239,item;assert float(item['font'][:-2])>=12,item
                            if layout=='sidebar':page.locator('#fxpMainChart').screenshot(path=str(args.artifacts/f'fan-{width}-{theme}.png'))
                            measurements.append({'layout':layout,'width':width,'theme':theme,**item})
                return measurements
            case('Responsividade em quatro layouts, cinco larguras e dois temas',matrix)
            if observed['pageerror']:results.append({'name':'Erros do navegador','status':'PRODUCT_FAIL','detail':observed['pageerror']})
            context.close();browser.close()
    finally:server.shutdown()
    after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS};receipt={'sourceHashes':source,'sourceHashesAfter':after,'results':results,'status':'PASS' if source==after and all(x['status']=='PASS' for x in results) else 'PRODUCT_FAIL'}
    (args.artifacts/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    for row in results:print('['+row['status']+'] '+row['name']+(' '+str(row['detail']) if row['status']!='PASS' else ''))
    raise SystemExit(0 if receipt['status']=='PASS' else 1)

if __name__=='__main__':main()

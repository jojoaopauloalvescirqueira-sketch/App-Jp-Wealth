#!/usr/bin/env python3
"""CHG-JPW-FOREX-VISUAL-RISK-TEST-20261005: presentation-only focal.

Disposable synthetic contexts; real account/order/import writers and real domain
projections. Existing financial judges and canonical fixtures are not modified.
"""
import argparse
import base64
from datetime import datetime
from functools import partial
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import (Server, Quiet, ready, persisted, projection,
    field, set_field, near, prepare_drafts, SEED)
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['index.html','build-id.js','src/js/manifest.json','src/styles/app.css',
    'src/js/20-ui/28-fx-consolidated.js','src/js/20-ui/30-execution-board.js',
    'src/js/10-domain/17-fx-consolidated-model.js','src/js/10-domain/18-execution-board-model.js',
    'src/js/10-domain/00-forex-engine.js','src/js/10-domain/00-forex-state.js',
    'src/js/10-domain/11-operation-lifecycle.js','src/js/40-app/24-fx-consolidated-import.js']


def hashes(root):
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in SOURCES}


def financial(page):
    value = persisted(page)
    return {'state': value['state'], 'raw': value['raw']}


def shot(page,out,name,target=None):
    if target: page.locator(target).scroll_into_view_if_needed()
    settle(page)
    page.screenshot(path=str(out/(name+'.png')))


def shown_body(page):
    button=page.locator('#ebRiskChartToggle')
    if button.get_attribute('aria-expanded')!='true': button.click()
    settle(page)
    assert page.locator('#ebRiskChartBody').is_visible()


def risk_seed(page,count=1,patches=None):
    page.evaluate(SEED)
    settle(page)
    prepare_drafts(page)
    saved=page.evaluate("""({count,patches})=>{
      const require=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
      const scope=JPWForex.state.operationalSelection();
      const edits=[];
      for(let n=0;n<count;n++){
        const pi=n%6,oi=Math.floor(n/6);
        while(JPWForex.state.accountContext(scope).value.phases[pi].orders.length<=oi)require(operationAddDraft(pi));
        edits.push({pi,oi,changes:{id:'VISUAL-'+String(n+1).padStart(3,'0'),
          brokerHash:'SYNTHETIC-VISUAL-'+String(n+1).padStart(6,'0'),
          par:'EURUSD',tipo:'BUY',role:n===0?'GENESIS':'DEFENSE',lote:.02*(n+1),
          entry:1.2,sl:1.17,tp:1.26,result:null,status:'Aberta',costs:0,
          costBasis:'SEPARATE_FROM_RESULT',stopValidated:true,...(patches[n]||{})}});
      }
      if(edits.length)require(operationRecordOrders(edits,{reason:'Synthetic visual-risk factual fixture'}));
      JPWForex.executionBoardUI.render();return JPWForex.executionBoard.read();
    }""",{'count':count,'patches':patches or {}})
    settle(page)
    assert len([r for r in saved['rows'] if r['order']['status']=='Aberta'])==sum(1 for i in range(count) if (patches or {}).get(str(i),{}).get('status','Aberta')=='Aberta')
    return saved


def risk_dom(page):
    return page.locator('[data-eb-risk-row]:visible').evaluate_all("""rows=>rows.map(e=>({
      key:e.dataset.ebRiskRow,value:Number(e.dataset.riskValue),
      percent:e.dataset.riskPercent===''?null:Number(e.dataset.riskPercent),
      text:e.innerText,width:e.querySelector('[aria-hidden="true"] span')?.getAttribute('style')||null
    }))""")


def assert_risk_values(page,model,expected_count=None):
    rows={f"{r['pi']}:{r['oi']}":r for r in model['rows'] if r['order']['status']=='Aberta'}
    actual=risk_dom(page)
    if expected_count is not None: assert len(actual)==expected_count,(len(actual),expected_count)
    for value in actual:
        row=rows[value['key']]
        assert row['order']['recordStatus']=='recorded'
        risk=row['operationalRisk']
        assert risk['status']=='OK' and risk['value'] is not None
        near(value['value'],risk['value'])
        if risk['percent'] is None: assert value['percent'] is None
        else: near(value['percent'],risk['percent'])
        workbook=page.locator(f'[data-eb-row="{value["key"]}"] [data-eb-calc="riskValue"]').inner_text()
        assert workbook in value['text'],('Risk chart differs from workbook value',workbook,value)
    assert [r['value'] for r in actual]==sorted((r['value'] for r in actual),reverse=True),'Bars not sorted by confirmed risk'
    return actual


def risk_populations(page,out,observed):
    observed['populations']=[]
    for count in [1,10,30]:
        model=risk_seed(page,count)
        before=financial(page)
        shown_body(page)
        assert page.locator('#ebRiskChart').get_attribute('data-eb-risk-state')=='complete'
        values=assert_risk_values(page,model,min(6,count))
        if count>6:
            button=page.locator('#ebRiskShowAll')
            assert button.is_visible() and button.get_attribute('aria-expanded')=='false'
            button.click();settle(page)
            assert button.get_attribute('aria-expanded')=='true'
            assert_risk_values(page,model,count)
            button.click();settle(page)
            assert_risk_values(page,model,6)
        assert financial(page)==before,'Expand/collapse wrote financial facts'
        shot(page,out,'risk-'+str(count)+'-orders','#ebRiskChart')
        observed['populations'].append({'count':count,'top':values,'canonicalTotal':model['operational']['exposure']})


def risk_coverage(page,out,observed):
    model=risk_seed(page,4,{'1':{'sl':0,'stopValidated':False},'2':{'sl':1.21},
        '3':{'status':'Pendente','pendingActive':True,'amplifiesExposure':True}})
    before=financial(page);shown_body(page)
    assert page.locator('#ebRiskChart').get_attribute('data-eb-risk-state')=='partial'
    values=assert_risk_values(page,model,2)
    assert any(v['value']==0 for v in values),'Protected stop must remain known zero'
    assert page.locator('[data-eb-risk-unavailable="1:0"]').count()==1
    page.locator('.eb-risk-unavailable summary').click()
    assert page.locator('#ebRiskUnavailable').inner_text().strip()
    assert page.locator('#ebRiskPending').is_visible()
    assert page.locator('[data-eb-risk-row="3:0"]').count()==0,'Pending order leaked into opened-position ranking'
    assert model['operational']['exposure']['value'] is None,'Partial total must not be computed as subtotal'
    assert 'parcial' in page.locator('#ebRiskChart').inner_text().lower()
    assert financial(page)==before
    observed['partial']={'bars':values,'pending':model['risk']['pending'],'unavailable':page.locator('#ebRiskUnavailable').inner_text()}
    shot(page,out,'risk-partial-zero-pending','#ebRiskChart')
    model=risk_seed(page,1,{'0':{'sl':0,'stopValidated':False}});shown_body(page)
    assert page.locator('#ebRiskChart').get_attribute('data-eb-risk-state')=='unavailable'
    assert not risk_dom(page)
    model=risk_seed(page,0);shown_body(page)
    assert page.locator('#ebRiskChart').get_attribute('data-eb-risk-state')=='empty'
    assert not risk_dom(page)
    observed['empty']=model['operational']['exposure']


def risk_draft_detail(page,out,observed):
    model=risk_seed(page,10);shown_body(page)
    before=financial(page);bars=risk_dom(page)
    set_field(page,'sl','1.199')
    editor=field(page,'sl').element_handle()
    editor.evaluate('e=>e.setSelectionRange(2,5)')
    assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    assert risk_dom(page)==bars,'RAM draft changed confirmed bar values/widths'
    key=bars[0]['key']
    details=page.locator(f'[data-eb-detail="{key}"]')
    detail_node=details.element_handle()
    page.locator(f'[data-eb-risk-detail="{key}"]').click();settle(page)
    assert details.evaluate('e=>e.open') and details.is_visible()
    assert detail_node.evaluate('e=>e.isConnected'),'Chart created a duplicate detail editor'
    assert editor.evaluate('e=>e.isConnected&&e.value==="1.199"&&e.selectionStart===2&&e.selectionEnd===5'),'Chart navigation discarded another row draft or cursor selection'
    assert financial(page)==before
    assert_risk_values(page,model,6)
    page.locator('[data-eb-cancel-row="0:0"]').click();settle(page)
    assert financial(page)==before and field(page,'sl').input_value()=='1.17'
    observed.update(draftRetained=True,existingDetail=True,unchangedRisk=bars)
    shot(page,out,'risk-detail-retained-draft')


def risk_context(page,out,observed):
    page.set_viewport_size({'width':390,'height':844})
    risk_seed(page,10)
    shown_body(page)
    assert len(risk_dom(page))==6
    # A second synthetic, explicitly registered account/period. Every displayed
    # fact goes through the existing writers; presentation never applies a scope.
    second=page.evaluate("""()=>{
      const require=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
      S.accounts.push({forexAccountId:'VISUAL-B',nome:'Outro contexto sintético',tipo:'MESTRE',platformCurrency:'USD',platform:'MT5',platformLogin:'TEST-002'});
      if(save()!==true)throw Error('Synthetic second account refused');
      const api=JPWForex.state;
      require(api.recordAccountPeriod({accountId:'VISUAL-B',startedAt:'2026-08-01',currency:'USD',si:10000,openingBook:12000,source:'Synthetic B opening',activateCurrentPeriod:true},{reason:'Synthetic isolated scope'}));
      require(api.selectOperationalAccount('VISUAL-B'));
      const scope=api.operationalSelection(),at='2026-09-22T12:00:00Z';
      require(api.recordAccountFacts({accountIndex:1,periodId:scope.periodId,si:10000,equity:12000,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'Synthetic B equity',observedAt:at},{reason:'Synthetic observation'}));
      require(api.recordInstrumentContext({...scope,instrumentId:'EURUSD',expectedRevision:0,componentChanges:{
        price:{value:1.3,source:'Synthetic B price',observedAt:at},
        atr:{short:.002,long:.001,timeframe:'H4',unit:'PRICE',source:'Synthetic B ATR',observedAt:at},
        contract:{contractSize:100000,source:'Synthetic B contract',observedAt:at},
        conversion:{baseToAccountRate:1.2,quoteToAccountRate:1,source:'Synthetic B conversion',observedAt:at}
      }},{reason:'Synthetic B references',expectedEpoch:jpWealthPersistenceEpoch()}));
      require(operationRecordOrder(0,0,{id:'OTHER-SCOPE',brokerHash:'SYNTHETIC-OTHER-SCOPE',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:.01,entry:1.2,sl:1.17,tp:1.26,result:null,status:'Aberta',costs:0,costBasis:'SEPARATE_FROM_RESULT',stopValidated:true},{reason:'Synthetic factual B order'}));
      return JPWForex.executionBoard.read();
    }""")
    before=financial(page)
    page.evaluate('JPWForex.executionBoardUI.render()');settle(page)
    assert page.locator('#ebRiskChartToggle').get_attribute('aria-expanded')=='true','Explicit session expansion lost on context change'
    values=assert_risk_values(page,second,1)
    assert 'OTHER-SCOPE' in values[0]['text'] and 'VISUAL-00' not in page.locator('#ebRiskChart').inner_text()
    assert second['selection']['accountId']=='VISUAL-B'
    assert financial(page)==before,'Presenting second context wrote facts'
    result=page.evaluate("JPWForex.state.selectOperationalAccount('TABLE-A')")
    assert result['ok'],result
    page.evaluate('JPWForex.executionBoardUI.render()');settle(page)
    assert page.locator('#ebRiskChartToggle').get_attribute('aria-expanded')=='true'
    assert len(risk_dom(page))==6
    assert 'OTHER-SCOPE' not in page.locator('#ebRiskChart').inner_text()
    assert financial(page)==before,'Context selection/presentation wrote financial facts'
    observed.update(secondAccount='VISUAL-B',secondBars=values,returnedAccount='TABLE-A',expansionRetained=True)
    shot(page,out,'risk-context-expansion','#ebRiskChart')


def overview_seed(page):
    page.evaluate(SEED);settle(page)
    page.evaluate("""()=>{
      S.accounts.push({forexAccountId:'VISUAL-A',nome:'Consulta sintética',tipo:'PRÓPRIA',broker:'Synthetic Broker',
        platform:'MT5',platformLogin:'900001',server:'Synthetic-Demo',currency:'USD',sini:1000,satu:1000});
      S.forex.accounts['VISUAL-A']={currency:'USD'};
      S.fxConsolidated=JPWFXConsolidated.emptyState();
      S.operationHistory={schemaVersion:DEFAULTS.operationHistory.schemaVersion,records:[]};
      if(save()!==true)throw Error('Synthetic overview setup refused');
      markSessionCheckpoint();JPWFXConsolidated.reset();JPWNavigation.navigate('forex-consolidated');
    }""")
    settle(page)
    page.locator('#fxcAccount').select_option('VISUAL-A')
    page.locator('#fxcOpenImport').click()
    page.locator('#fxcFile').set_input_files(str(ROOT/'tools/fixtures/mt5-consolidated/classic-en.html'))
    page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
    page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click()
    page.wait_for_function("S.fxConsolidated.receipts.length===1")
    settle(page)
    return page.evaluate("JPWFXConsolidated.project(S.fxConsolidated,S.operationHistory.records,{source:'mt5',accountId:'VISUAL-A'})")


def overview_integration(page,out,observed):
    model=overview_seed(page);before=financial(page)
    chart=page.locator('figure.fxc-chart[data-fxc-series="main"]')
    assert chart.count()==1,'Overview must have exactly one main trajectory'
    assert page.locator('#fxcIdentity .fxc-chart').count()==0,'Identity duplicates the trajectory'
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-A'
    assert len(model['series']['growth'])>1 and not model['series']['equity']
    # PROFESSIONAL-TEST: the approved integrated panel adds the canonical
    # balance-DD strip; it still must never infer an equity series.
    assert page.locator('#fxcPanel-account .fxc-chart').count()==2,'Expected growth and canonical balance drawdown only'
    assert page.locator('#fxcPanel-account [data-fxc-series="drawdown"]').count()==1
    assert page.locator('#fxcPanel-account [data-fxc-series="equity"]').count()==0
    assert chart.get_attribute('data-point-count')==str(len(model['series']['growth']))
    points=chart.locator('svg [data-fxc-point]').evaluate_all('els=>els.map(e=>({value:Number(e.dataset.value),x:Number(e.dataset.x)}))')
    assert [p['value'] for p in points]==[p['value'] for p in model['series']['growth']]
    times=[datetime.fromisoformat(p['time'].replace('Z','+00:00')).timestamp() for p in model['series']['growth']]
    near((points[1]['x']-points[0]['x'])/(points[-1]['x']-points[0]['x']),(times[1]-times[0])/(times[-1]-times[0]))
    assert chart.locator('svg path').evaluate_all("els=>els.some(e=>e.getTotalLength()>0&&getComputedStyle(e).stroke!=='none')"),'Primary curve has no painted path'
    chart.locator('svg [data-fxc-point]').last.hover();settle(page)
    assert chart.get_attribute('data-selected-point')==str(len(points)-1)
    chart.locator('details.fxc-chart-values summary').click()
    assert chart.locator('tbody tr').count()==len(model['series']['growth'])
    assert chart.locator('tbody td[data-value]').evaluate_all('els=>els.map(e=>Number(e.dataset.value))')==[p['value'] for p in model['series']['growth']]
    assert financial(page)==before

    observed['model']={'coverage':model['coverage'],'growth':model['series']['growth'],'equity':model['series']['equity']}
    shot(page,out,'overview-mt5-single-curve','#fxcPanel-account')
    page.locator('[data-fxc-chart="balance"]').click();settle(page)
    assert page.locator('figure[data-fxc-series="main"]').count()==1
    assert page.locator('figure[data-fxc-series="main"] svg [data-fxc-point]').evaluate_all('els=>els.map(e=>Number(e.dataset.value))')==[p['value'] for p in model['series']['balance']]
    assert financial(page)==before
    page.locator('#fxcAccount').select_option('TABLE-A');settle(page)
    assert not page.locator('figure.fxc-chart[data-fxc-series="main"] svg').count()
    assert financial(page)==before,'Account consultation altered facts or operational context'
    page.locator('#fxcAccount').select_option('VISUAL-A')
    page.locator('#fxcManual').click();settle(page)
    assert not page.locator('figure.fxc-chart[data-fxc-series="main"] svg').count(),'Manual borrowed MT5 history'
    assert financial(page)==before


def overview_geometry(page,out,observed):
    cases=[
        ('irregular',[{'time':'2026-01-01','value':10},{'time':'2026-01-02','value':11},{'time':'2026-01-11','value':7}],'time'),
        ('server',[{'time':'2026-01-01T04:00:00','value':10},{'time':'2026-01-01T05:00:00','value':11},{'time':'2026-01-01T14:00:00','value':7}],'time'),
        ('ambiguous',[{'time':'01/02/2026','value':10},{'time':'02/03/2026','value':11}],'sequence'),
        ('invalid-date',[{'time':'2026-02-30','value':10},{'time':'2026-03-01','value':11}],'sequence'),
        ('duplicate',[{'time':'2026-01-01','value':10},{'time':'2026-01-01','value':11},{'time':'2026-01-02','value':12}],'time'),
        ('coincident',[{'time':'2026-01-01T00:00:00Z','value':10},{'time':'2026-01-01T00:00:00Z','value':11}],'time'),
        ('out-of-order',[{'time':'2026-01-11','value':10},{'time':'2026-01-01','value':11}],'sequence'),
        ('mixed-time-bases',[{'time':'2026-01-01T00:00:00Z','value':10},{'time':'2026-01-02T00:00:00','value':11}],'sequence'),
        ('missing',[{'time':'2026-01-01','value':0},{'time':'2026-01-02','value':None},{'time':'2026-01-03','value':-3}],'time'),
        ('one',[{'time':'2026-01-01','value':1.2345678901234}],'time'),
        ('empty',[],'sequence'),
        ('long-values',[{'time':'2026-01-01','value':-123456789012.125},{'time':'2026-01-02','value':123456789012.125}],'time'),
        ('constant',[{'time':'2026-01-01','value':-100},{'time':'2026-01-02','value':-100}],'time')]
    before=financial(page);observed['geometry']=[]
    for name,points,mode in cases:
        result=page.evaluate("""points=>{
          const api=JPWFXConsolidated.visual;
          if(!api||typeof api.series!=='function'||typeof api.geometry!=='function')throw Error('Production chart geometry API unavailable');
          const series=api.series(points);return {series,geometry:api.geometry(series,900,240)};
        }""",points)
        series=result['series'];geometry=result['geometry']
        assert series['axisMode']==mode,(name,series)
        assert len(series['points'])==len(points),(name,'Missing observations were removed')
        known=[p for p in points if p['value'] is not None]
        assert series['validCount']==len(known)
        assert len(geometry['coords'])==len(known),(name,geometry)
        assert series['gapCount']==len(points)-len(known)
        assert all(math.isfinite(c[k]) for c in geometry['coords'] for k in ['x','y']),name
        assert [p['value'] for p in series['points']]==[p['value'] for p in points],'Presentation altered full-precision values'
        if name in ['irregular','server']:
            coords=geometry['coords'];near((coords[1]['x']-coords[0]['x'])/(coords[2]['x']-coords[0]['x']),.1)
        if name in ['duplicate','coincident']:
            near(geometry['coords'][0]['x'],geometry['coords'][1]['x'])
            if name=='duplicate':assert geometry['coords'][2]['x']>geometry['coords'][0]['x']
        if name=='missing':
            assert len(geometry['segments'])==2,geometry
            assert all(not ({0,2}<=set(s['indices'])) for s in geometry['segments']),'Line connects across missing observation'
            assert geometry['coords'][0]['value']==0,'Known zero treated as absence'
        if name=='one':
            assert all(len(s['indices'])<=1 for s in geometry['segments']),'One observation became a trend'
        observed['geometry'].append({'name':name,**result})
    assert financial(page)==before,'Chart geometry wrote application state'


def overview_manual_keyboard(page,out,observed):
    overview_seed(page)
    page.evaluate("""()=>{
      S.operationHistory={schemaVersion:DEFAULTS.operationHistory.schemaVersion,records:[
        {operationId:'SYNTH-MANUAL-1',accountId:'VISUAL-A',periodId:'SYNTH-PERIOD',currency:'USD',netResult:10,closedAt:'2026-01-01T00:00:00Z'},
        {operationId:'SYNTH-MANUAL-2',accountId:'VISUAL-A',periodId:'SYNTH-PERIOD',currency:'USD',netResult:-5,closedAt:'2026-01-02T00:00:00Z'},
        {operationId:'SYNTH-MANUAL-3',accountId:'VISUAL-A',periodId:'SYNTH-PERIOD',currency:'USD',netResult:20,closedAt:'2026-01-11T00:00:00Z'}]};
      if(save()!==true)throw Error('Synthetic historical fixture refused');markSessionCheckpoint();JPWFXConsolidated.render();
    }""")
    page.locator('#fxcManual').click();settle(page)
    before=financial(page)
    model=page.evaluate("JPWFXConsolidated.project(S.fxConsolidated,S.operationHistory.records,{source:'manual',accountId:'VISUAL-A'})")
    assert [p['value'] for p in model['series']['realized']]==[10,5,25]
    chart=page.locator('figure.fxc-chart[data-fxc-series="main"]')
    assert chart.get_attribute('data-axis-mode')=='time'
    assert chart.get_attribute('data-point-count')=='3'
    assert 'realizado' in chart.inner_text().lower()
    cursor=chart.locator('input.fxc-chart-cursor')
    cursor.focus();page.keyboard.press('End');settle(page)
    assert cursor.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
    assert cursor.input_value()=='2'
    assert '25' in chart.locator('output.fxc-chart-value').inner_text()
    page.keyboard.press('Home');settle(page)
    assert cursor.input_value()=='0'
    assert '10' in chart.locator('output.fxc-chart-value').inner_text()
    page.keyboard.press('ArrowRight');settle(page)
    assert cursor.input_value()=='1'
    chart.locator('details.fxc-chart-values summary').click()
    assert chart.locator('tbody tr').count()==3
    assert financial(page)==before
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-A'
    shot(page,out,'overview-manual-keyboard','#fxcPanel-account')
    observed['manual']={'series':model['series']['realized'],'keyboard':'Home/End/Right and table'}
    page.evaluate("""()=>{S.operationHistory.records=S.operationHistory.records.slice(0,1);if(save()!==true)throw Error('Synthetic singleton refused');markSessionCheckpoint();JPWFXConsolidated.render();}""")
    settle(page)
    singleton=page.locator('figure.fxc-chart[data-fxc-series="main"]')
    assert singleton.get_attribute('data-point-count')=='1'
    assert singleton.locator('svg [data-fxc-point]').count()==1
    assert 'Uma observação' in singleton.inner_text()
    shot(page,out,'overview-single-observation','#fxcPanel-account')


def layout_matrix(page,out,observed,layout):
    risk_seed(page,10)
    page.evaluate('l=>mountNavigationLayout(l)',layout);settle(page)
    before=financial(page);observed['riskDimensions']=[]
    for width in [1440,1024,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}",theme);settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(layout,width,theme,'Global horizontal overflow')
            geometry=page.locator('#executionBoardRisk').evaluate("""e=>({width:e.clientWidth,scroll:e.scrollWidth,
              expanded:document.querySelector('#ebRiskChartToggle').getAttribute('aria-expanded'),
              chartWidth:document.querySelector('#ebRiskChart').getBoundingClientRect().width})""")
            assert geometry['scroll']<=geometry['width']+1,(layout,width,theme,geometry)
            assert (geometry['expanded']=='true')==(geometry['width']>=768),(layout,width,theme,'Useful-width default',geometry)
            assert page.locator('[data-eb-row="0:0"] td').count()==20
            assert financial(page)==before
            observed['riskDimensions'].append({'width':width,'theme':theme,**geometry})
            if width in [1440,390]:shot(page,out,f'risk-{layout}-{width}-{theme}','#ebRiskChart')
    overview_seed(page);page.evaluate('l=>mountNavigationLayout(l)',layout);settle(page)
    before=financial(page);observed['overviewDimensions']=[]
    for width in [1440,1024,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}",theme);settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(layout,width,theme,'Overview overflow')
            chart=page.locator('figure.fxc-chart[data-fxc-series="main"]')
            geometry=chart.evaluate("""e=>{const svg=e.querySelector('svg'),r=svg.getBoundingClientRect(),vb=svg.viewBox.baseVal;
              return {width:e.clientWidth,scroll:e.scrollWidth,svgWidth:r.width,svgHeight:r.height,viewWidth:vb.width,viewHeight:vb.height,preserve:svg.getAttribute('preserveAspectRatio')};}""")
            assert geometry['scroll']<=geometry['width']+1,(layout,width,theme,geometry)
            assert geometry['svgWidth']>100 and geometry['svgHeight']>=120,(layout,width,theme,geometry)
            assert geometry['preserve']!='none','SVG is being stretched independently on each axis'
            assert abs(geometry['svgWidth']/geometry['svgHeight']-geometry['viewWidth']/geometry['viewHeight'])<.08,(layout,width,theme,geometry)
            assert financial(page)==before
            observed['overviewDimensions'].append({'width':width,'theme':theme,**geometry})
            if width in [1440,390]:shot(page,out,f'overview-{layout}-{width}-{theme}','#fxcPanel-account')


def touch(page,out,observed):
    page.set_viewport_size({'width':390,'height':844})
    risk_seed(page,10)
    assert page.evaluate("matchMedia('(pointer:coarse)').matches")
    before=financial(page)
    toggle=page.locator('#ebRiskChartToggle')
    assert toggle.get_attribute('aria-expanded')=='false'
    toggle.tap();settle(page)
    assert toggle.get_attribute('aria-expanded')=='true'
    page.locator('#ebRiskShowAll').tap();settle(page)
    assert len(risk_dom(page))==10
    for locator in [toggle,page.locator('#ebRiskShowAll'),page.locator('[data-eb-risk-detail]').first]:
        r=locator.bounding_box();assert r['height']>=44 and r['width']>=44,r
    page.set_viewport_size({'width':1440,'height':1000});settle(page)
    page.set_viewport_size({'width':390,'height':844});settle(page)
    assert toggle.get_attribute('aria-expanded')=='true','Explicit visual expansion did not survive resize'
    assert financial(page)==before
    overview_seed(page);before=financial(page)
    chart=page.locator('figure.fxc-chart[data-fxc-series="main"]')
    cursor=chart.locator('input.fxc-chart-cursor')
    initial=cursor.input_value()
    cursor.tap();settle(page)
    # A native range changes its value on touch without necessarily becoming
    # activeElement. Keyboard focus remains separately required and tested.
    selection=cursor.evaluate("""e=>{const f=e.closest('figure'),index=Number(e.value),point=JSON.parse(f.dataset.fxcPoints)[index];
      return {value:e.value,selected:f.dataset.selectedPoint,date:point.date,exact:String(point.value),
        output:f.querySelector('output.fxc-chart-value').textContent,aria:e.getAttribute('aria-valuetext')};}""")
    assert selection['value']!=initial,'Touch did not change the selected observation'
    assert selection['selected']==selection['value'],'Touch cursor and selected point disagree'
    assert selection['aria']==selection['output']
    assert selection['date'] in selection['output'] and selection['exact'] in selection['output'],selection
    assert financial(page)==before,'Touch inspection wrote financial facts'
    observed['touchSelection']=selection
    chart.locator('details.fxc-chart-values summary').tap();settle(page)
    assert chart.locator('tbody tr').count()>0
    assert financial(page)==before
    shot(page,out,'overview-touch','#fxcPanel-account')
    observed['touch']='390px coarse: risk disclosure/all rows, resize retention, chart cursor/table'


def native_zoom(pw,url,out,observed):
    profile=Path(tempfile.mkdtemp(prefix='forex-visual-native-200-',dir=out))
    (profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options()
    options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    context=pw.chromium.launch_persistent_context(str(profile),**options)
    errors=[]
    try:
        context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
        page=context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('dialog',lambda dialog:dialog.accept())
        page.bring_to_front();page.goto(url);ready(page)
        ratio=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
        if abs(ratio['outer']/ratio['inner']-2)>=.01 or ratio['css']!='1':
            raise RuntimeError('Native zoom200 unavailable: '+str(ratio))
        risk_seed(page,10);before=financial(page)
        assert page.locator('#ebRiskChartToggle').get_attribute('aria-expanded')=='false'
        shown_body(page);assert len(risk_dom(page))==6
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert financial(page)==before
        page.locator('#ebRiskChart').scroll_into_view_if_needed();settle(page)
        cdp=context.new_cdp_session(page)
        (out/'risk-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        overview_seed(page);before=financial(page)
        chart=page.locator('figure.fxc-chart[data-fxc-series="main"]')
        cursor=chart.locator('input.fxc-chart-cursor');cursor.focus();page.keyboard.press('End');settle(page)
        assert cursor.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert financial(page)==before
        chart.scroll_into_view_if_needed();settle(page)
        (out/'overview-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        assert not errors,errors
        assert_fixture_requests(context)
        observed['nativeZoom']=ratio
    finally:
        context.close();shutil.rmtree(profile)


def main():
    global ROOT
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cases',help='Comma-separated focused cases; omitted runs all')
    parser.add_argument('--native-zoom',action='store_true')
    args=parser.parse_args();ROOT=args.root.resolve();args.out.mkdir(parents=True,exist_ok=True)
    before=hashes(ROOT)
    report={'root':str(ROOT),'source_sha256':before,'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases':[],'classification':'NOT_RUN','limits':{'Safari':'NOT_RUN','physical_touch':'NOT_RUN','screen_reader':'NOT_RUN','native_zoom':'requested' if args.native_zoom else 'NOT_RUN'}}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'
    cases=[('overview-geometry',overview_geometry),('overview-import-context',overview_integration),
        ('overview-manual-keyboard',overview_manual_keyboard),('risk-populations',risk_populations),
        ('risk-coverage',risk_coverage),('risk-draft-detail',risk_draft_detail),('risk-context',risk_context)]
    cases += [('layout-'+layout,partial(layout_matrix,layout=layout)) for layout in ['sidebar','topbar','glass','submenu']]
    cases += [('touch',touch)]
    chosen=set(args.cases.split(',')) if args.cases else None
    try:
        if chosen and chosen.difference(name for name,_ in cases):raise ValueError('Unknown cases '+str(chosen))
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
            for name,check in cases:
                if chosen and name not in chosen:continue
                case={'name':name,'classification':'NOT_RUN','pageerrors':[]};report['cases'].append(case)
                context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',has_touch=name=='touch',reduced_motion='reduce')
                context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
                page=context.new_page();page.set_default_timeout(15000)
                page.on('pageerror',lambda error,c=case:c['pageerrors'].append(str(error)))
                page.on('dialog',lambda dialog:dialog.accept())
                try:
                    page.goto(url);ready(page);check(page,args.out,case)
                    assert not case['pageerrors'],case['pageerrors']
                    assert_fixture_requests(context)
                    case['classification']='PASS'
                except AssertionError as error:
                    case.update(classification='PRODUCT_FAIL',error=str(error),trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/(name+'-failure.png')),full_page=True)
                except BaseException as error:
                    case.update(classification='TEST_HARNESS_FAIL',error=str(error),trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/(name+'-failure.png')),full_page=True)
                finally:context.close()
            browser.close()
            if args.native_zoom:
                case={'name':'native-200-percent','classification':'NOT_RUN'};report['cases'].append(case)
                try:native_zoom(pw,url,args.out,case);case['classification']='PASS'
                except AssertionError as error:case.update(classification='PRODUCT_FAIL',error=str(error),trace=traceback.format_exc())
                except BaseException as error:case.update(classification='ENVIRONMENT_ERROR',error=str(error),trace=traceback.format_exc())
        assert before==hashes(ROOT),'Sources changed during focal; evidence must be rerun on frozen bytes'
        failures=[case for case in report['cases'] if case['classification']!='PASS']
        report['classification']=failures[0]['classification'] if failures else 'PASS'
    except BaseException as error:
        report.update(classification='ENVIRONMENT_ERROR',error=str(error),trace=traceback.format_exc())
    finally:
        server.shutdown()
        (args.out/'visual-risk-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['classification']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())

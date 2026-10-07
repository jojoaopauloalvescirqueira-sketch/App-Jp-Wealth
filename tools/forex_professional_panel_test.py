#!/usr/bin/env python3
"""Professional Forex panel: canonical producers, actual imports, disposable UI.

CHG-JPW-FOREX-PROFESSIONAL-TEST-20261005. Financial oracles and gates remain
unchanged. Synthetic histories are imported by the real HTML/PDF workflow;
state writes occur only in explicit fixture setup and real record commands.
"""
import argparse
import base64
from datetime import date
from functools import partial
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import Server, Quiet, ready, field, set_field, near, SEED
from forex_visual_risk_test import financial, risk_seed, shot, overview_seed
from fx_consolidated_pdf_test import synthetic_pdf
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['index.html', 'build-id.js', 'src/js/manifest.json', 'src/styles/app.css',
    'src/js/20-ui/28-fx-consolidated.js', 'src/js/20-ui/30-execution-board.js',
    'src/js/10-domain/17-fx-consolidated-model.js', 'src/js/10-domain/18-execution-board-model.js',
    'src/js/10-domain/00-forex-engine.js', 'src/js/10-domain/00-forex-state.js',
    'src/js/10-domain/11-operation-lifecycle.js', 'src/js/40-app/24-fx-consolidated-import.js']


def hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}


def long_report(partial=False):
    # Distinct missing March, known-zero July, costs, funding and withdrawal.
    rows = [
        ['2024.01.01 00:00:00','100','','balance','','','','','0','0','0','1000'],
        ['2024.02.02 10:00:00','101','EURUSD','buy','in','1','1.1','200','-2','0','0','0'],
        ['2024.02.03 11:00:00','102','EURUSD','sell','out','0.40','1.103','201','-1','0','-1','120'],
        ['2025.04.04 11:00:00','103','EURUSD','sell','out','0.60','1.10133','202','-1','0','0','80'],
        ['2026.06.05 00:00:00','104','','balance','','','','','0','0','0','500'],
        ['2026.07.06 10:00:00','105','GBPUSD','buy','out','1','1.25','203','0','0','0','0'],
        ['2026.08.07 00:00:00','106','','balance','','','','','0','0','0','-250'],
        ['2026.09.08 10:00:00','107','GBPUSD','buy','out','1','1.251','204','-2','0','-1','-100'],
        ['2026.09.09 00:00:00','108','','commission','','','','','0','0','0','-5'],
        ['2026.09.30 10:00:00','109','EURUSD','sell','out','1','1.12','205','-2','0','0','90']]
    if partial:
        rows = rows[5:]
    meta = [('Company:','Synthetic Broker'),('Account:','900001'),('Currency:','USD'),
        ('Server:','Synthetic-Demo'),('Period:','2026.07.01 - 2026.09.30' if partial else 'All history'),
        ('Date:','2026.09.30 23:59:59')]
    tr = lambda values: '<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in values)+'</tr>'
    headers=['Time','Deal','Symbol','Type','Direction','Volume','Price','Order','Commission','Fee','Swap','Profit']
    return ('<!doctype html><html><title>MetaTrader 5 Account History Report — SYNTHETIC</title><table>'+
        ''.join(tr(x) for x in meta)+'<tr><th colspan="12">Deals</th></tr><tr>'+''.join('<th>'+v+'</th>' for v in headers)+'</tr>'+
        ''.join(tr(x) for x in rows)+'<tr><th colspan="2">Summary</th></tr>'+tr(['Balance:','1425'])+tr(['Equity:','1425'])+'</table></html>').encode()


def setup_account(page, account='PANEL-A', login='900001'):
    page.evaluate(SEED); settle(page)
    page.evaluate("""({account,login})=>{
      S.accounts.push({forexAccountId:account,nome:'Conta analítica sintética',tipo:'PRÓPRIA',broker:'Synthetic Broker',
        platform:'MT5',platformLogin:login,server:'Synthetic-Demo',currency:'USD',sini:1000,satu:1000});
      S.forex.accounts[account]={currency:'USD'};S.fxConsolidated=JPWFXConsolidated.emptyState();
      S.operationHistory={schemaVersion:DEFAULTS.operationHistory.schemaVersion,records:[]};
      if(save()!==true)throw Error('Synthetic account seed refused');markSessionCheckpoint();
      JPWFXConsolidated.reset();JPWNavigation.navigate('forex-consolidated');
    }""", {'account':account,'login':login})
    settle(page);page.locator('#fxcAccount').select_option(account);settle(page)


def import_report(page, content, pdf=False):
    page.locator('#fxcOpenImport').click()
    page.locator('#fxcFile').set_input_files({'name':'synthetic-panel.'+('pdf' if pdf else 'html'),
        'mimeType':'application/pdf' if pdf else 'text/html','buffer':content})
    if pdf:
        page.locator('#fxcImportFrom').fill('2026-01-01');page.locator('#fxcImportTo').fill('2026-01-31')
    page.locator('#fxcAnalyze').click();page.locator('#fxcConfirmImport').wait_for()
    page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click()
    page.wait_for_function('S.fxConsolidated.receipts.length===1');settle(page)


def seed(page, partial=False):
    setup_account(page);import_report(page,long_report(partial));return model(page)


def model(page,source='mt5',account='PANEL-A'):
    return page.evaluate("""({source,account})=>JPWFXConsolidated.project(S.fxConsolidated,S.operationHistory.records,
      {source,accountId:account,from:document.querySelector('#fxcFrom').value,to:document.querySelector('#fxcTo').value})""",
      {'source':source,'account':account})


def curve(page,key='main'):
    return page.locator('figure.fxc-chart[data-fxc-series="'+key+'"]')


def values(page,key='main'):
    return curve(page,key).locator('svg [data-fxc-point]').evaluate_all('els=>els.map(e=>Number(e.dataset.value))')


def assert_curves(page, projected, key='growth'):
    assert values(page)==[p['value'] for p in projected['series'][key]],'Primary values differ from canonical series'
    assert values(page,'drawdown')==[p['value'] for p in projected['series']['drawdown']],'DD values differ from canonical series'
    main=curve(page);dd=curve(page,'drawdown')
    mainx=main.locator('svg [data-fxc-point]').evaluate_all('els=>els.map(e=>Number(e.dataset.x))')
    ddx=dd.locator('svg [data-fxc-point]').evaluate_all('els=>els.map(e=>Number(e.dataset.x))')
    assert len(mainx)==len(ddx)
    for left,right in zip(mainx,ddx):near(left,right)
    assert not page.locator('#fxcPanel-account [data-fxc-series="equity"]').count(),'Snapshot became equity history'


def integrated(page,out,case):
    projected=seed(page);before=financial(page)
    assert projected['coverage']['completeHistory'] is True
    near(projected['metrics']['netProfit']['value'],175)
    near(projected['metrics']['balance']['value'],1425)
    assert_curves(page,projected)
    assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='TABLE-A'
    assert page.locator('#fxcTab-account').inner_text()=='Painel'
    assert page.locator('#fxcTab-history').inner_text()=='Movimentos'
    assert page.locator('#fxcTab-statistics').inner_text()=='Estatísticas'
    assert page.locator('#fxcTab-risks').inner_text()=='Risco'
    text=page.locator('#fxcPanel-account').inner_text().lower()
    assert 'saldo' in text and ('desde a origem' in text or 'desde o início' in text)
    assert 'caixa' in page.locator('#fxcRiskBasis').text_content().lower(),'Balance DD must disclose cashflow effects'
    main=curve(page);main.locator('svg [data-fxc-point]').nth(4).hover();settle(page)
    assert main.get_attribute('data-selected-point')==curve(page,'drawdown').get_attribute('data-selected-point')=='4'
    assert main.get_attribute('data-selected-ticket')==curve(page,'drawdown').get_attribute('data-selected-ticket')
    cursor=main.locator('.fxc-chart-cursor');cursor.focus();page.keyboard.press('End');settle(page)
    assert cursor.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
    assert main.get_attribute('data-selected-point')==curve(page,'drawdown').get_attribute('data-selected-point')=='9'
    page.keyboard.press('Home');page.keyboard.press('ArrowRight');settle(page)
    assert main.get_attribute('data-selected-point')==curve(page,'drawdown').get_attribute('data-selected-point')=='1'
    for key,series in [('main','growth'),('drawdown','drawdown')]:
        c=curve(page,key);c.locator('details.fxc-chart-values summary').click()
        assert c.locator('tbody td[data-value]').evaluate_all('els=>els.map(e=>Number(e.dataset.value))')==[p['value'] for p in projected['series'][series]]
    page.locator('#fxcCashflows').check();settle(page)
    assert page.locator('[data-fxc-cashflow]').count()==3,'Markers must contain only the two actual deposits and withdrawal'
    assert financial(page)==before,'Inspection wrote financial facts'
    case['canonical']={'metrics':projected['metrics'],'coverage':projected['coverage'],'series':projected['series']}
    shot(page,out,'integrated-panel','#fxcPanel-account')


def filters(page,out,case):
    full=seed(page);before=financial(page);case['filters']=[]
    latest='2026-09-30'
    for preset,months in [('12m',12),('3m',3)]:
        page.locator('[data-fxc-preset="'+preset+'"]').click();settle(page)
        start=page.locator('#fxcFrom').input_value();end=page.locator('#fxcTo').input_value()
        assert end==latest,(preset,start,end,'Preset did not anchor to final observation')
        days=(date.fromisoformat(end)-date.fromisoformat(start)).days
        assert (360<=days<=366) if months==12 else (89<=days<=93),(preset,start,end)
        projected=model(page);assert_curves(page,projected)
        selected=[p for p in full['series']['growth'] if start<=p['time'][:10]<=end]
        assert values(page)==[p['value'] for p in selected],'Date filter silently rebased the lifetime curve'
        assert values(page)[0]!=0,'Filtered curve restarted at zero'
        case['filters'].append({'preset':preset,'from':start,'to':end,'growthMetric':projected['metrics']['growthPct'],'curve':projected['series']['growth']})
    page.locator('[data-fxc-preset="custom"]').click();settle(page)
    page.locator('#fxcFrom').fill('2026-09-08');page.locator('#fxcFrom').dispatch_event('change')
    page.locator('#fxcTo').fill('2026-09-30');page.locator('#fxcTo').dispatch_event('change');settle(page)
    projected=model(page);assert_curves(page,projected)
    near(projected['metrics']['netProfit']['value'],-20)
    page.locator('[data-fxc-preset="all"]').click();settle(page)
    assert page.locator('#fxcFrom').input_value()=='' and page.locator('#fxcTo').input_value()==''
    assert_curves(page,full)
    assert financial(page)==before
    shot(page,out,'filtered-panel','#fxcPanel-account')


def monthly(page,out,case):
    projected=seed(page);before=financial(page)
    page.locator('[data-fxc-month-mode="nominal"]').click();settle(page)
    cell=page.locator('[data-fxc-month="2026-07"]');assert cell.count()==1
    assert cell.locator('..').get_attribute('data-availability')!='unavailable'
    assert '0' in cell.inner_text() and 'USD' in cell.inner_text(),cell.inner_text()
    missing=page.locator('td[data-month="2026-03"]')
    assert missing.count()==1 and missing.get_attribute('data-availability')=='unavailable'
    assert '—' in missing.inner_text() and not missing.locator('button').count()
    month=next(m for m in projected['breakdowns']['monthly'] if m['month']=='2026-09')
    case['september']=month
    page.locator('[data-fxc-month="2026-09"]').click();settle(page)
    assert page.locator('#fxcPanel-history').is_visible()
    assert '2026-09' in page.locator('#fxcHistoryFilter').inner_text()
    rows=page.locator('#fxcPanel-history tbody tr')
    assert rows.count()==3,'Month drilldown did not select exactly the recorded events'
    assert all('2026-09' in text for text in rows.all_text_contents())
    page.locator('[data-fxc-clear-history]').click();settle(page)
    page.locator('#fxcTab-account').click();page.locator('[data-fxc-month-mode="growth"]').click();settle(page)
    assert '%' in page.locator('[data-fxc-month="2026-09"]').inner_text()
    assert financial(page)==before
    shot(page,out,'monthly-map','#fxcPanel-account')


def statistics(page,out,case):
    projected=seed(page);before=financial(page)
    page.locator('#fxcTab-statistics').click();settle(page)
    assert not page.locator('#fxcPanel-statistics .fxc-radar').count(),'Radar still primary analytical surface'
    assert not page.locator('#fxcPanel-statistics .fxc-bars [data-metric="equity"]').count()
    bars=page.locator('[data-fxc-drill-field="symbol"]')
    actual=bars.evaluate_all('els=>els.map(e=>({key:e.dataset.fxcDrillValue,value:Number(e.dataset.value)}))')
    expected={r['symbol']:r['netProfit'] for r in projected['breakdowns']['symbols'] if r['netProfit'] is not None}
    assert {r['key']:r['value'] for r in actual}==expected,(actual,expected)
    assert 'deals' in page.locator('#fxcPanel-statistics').inner_text().lower()
    assert 'parciais' in page.locator('#fxcPanel-statistics').inner_text().lower()
    page.locator('#fxcDistributionSort').select_option('name');settle(page)
    names=bars.evaluate_all('els=>els.map(e=>e.dataset.fxcDrillValue)');assert names==sorted(names)
    page.locator('[data-fxc-drill-field="symbol"][data-fxc-drill-value="EURUSD"]').click();settle(page)
    assert page.locator('#fxcPanel-history').is_visible()
    assert 'EURUSD' in page.locator('#fxcHistoryFilter').inner_text()
    assert page.locator('#fxcPanel-history tbody tr').count()==4
    detail=page.locator('#fxcPanel-history .fxc-record-detail').first
    detail.locator('summary').first.click();settle(page)
    assert 'execução' in detail.inner_text().lower() and 'origem' in detail.inner_text().lower()
    assert detail.locator('details.fxc-record-raw').count()==1
    assert not detail.locator('details.fxc-record-raw').evaluate('e=>e.open')
    page.locator('[data-fxc-clear-history]').click();settle(page)
    page.locator('#fxcSearch').fill('107');settle(page)
    assert page.locator('#fxcPanel-history tbody tr').count()==1
    page.locator('#fxcTab-account').click();settle(page)
    assert_curves(page,projected)
    assert financial(page)==before,'Table filtering changed account data'
    case['symbolBars']=actual
    shot(page,out,'statistics-structured-movement','#fxcPanel-account')


def missing_summary_manual(page,out,case):
    partial=seed(page,True);before=financial(page)
    assert not partial['coverage']['completeHistory']
    assert not values(page),'Partial ledger fabricated a full growth trajectory'
    assert not values(page,'drawdown'),'Partial ledger fabricated balance DD'
    assert financial(page)==before
    shot(page,out,'partial-ledger','#fxcPanel-account')
    setup_account(page,'PANEL-PDF','900004')
    page.evaluate("()=>{S.accounts.find(a=>a.forexAccountId==='PANEL-PDF').broker='Synthetic Broker Ltd.';save();markSessionCheckpoint();}")
    import_report(page,synthetic_pdf(login='900004'),True)
    before=financial(page)
    summary=page.evaluate("S.fxConsolidated.accounts.find(a=>a.id==='PANEL-PDF')")
    assert not summary['deals'] and len(summary['summaries'])==1
    assert not values(page) and not values(page,'drawdown')
    page.locator('[data-fxc-preset="custom"]').click();settle(page)
    page.locator('#fxcFrom').fill('2026-01-10');page.locator('#fxcFrom').dispatch_event('change')
    page.locator('#fxcTo').fill('2026-01-15');page.locator('#fxcTo').dispatch_event('change');settle(page)
    sub=model(page,account='PANEL-PDF')
    assert sub['metrics']['netProfit']['value'] is None,'Summary fabricated partial-period net result'
    assert not values(page) and not values(page,'drawdown')
    assert financial(page)==before
    case['summaryPeriod']=summary['summaries'][0]['period']
    setup_account(page)
    page.evaluate("""()=>{S.operationHistory.records=[
      {operationId:'MAN-1',accountId:'PANEL-A',periodId:'MAN-P',currency:'BRL',netResult:10,closedAt:'2026-01-01T00:00:00Z'},
      {operationId:'MAN-2',accountId:'PANEL-A',periodId:'MAN-P',currency:'BRL',netResult:0,closedAt:'2026-07-01T00:00:00Z'},
      {operationId:'MAN-3',accountId:'PANEL-A',periodId:'MAN-P',currency:'BRL',netResult:-5,closedAt:'2026-09-30T00:00:00Z'}];
      if(save()!==true)throw Error('Synthetic manual refused');markSessionCheckpoint();JPWFXConsolidated.render();}""")
    page.locator('#fxcManual').click();settle(page);before=financial(page)
    manual=model(page,'manual');assert values(page)==[10,10,5]
    assert 'BRL' in curve(page).inner_text() and not values(page,'drawdown')
    assert not manual['series']['balance'] and not manual['series']['equity']
    assert financial(page)==before
    case['manual']=manual['series']
    shot(page,out,'manual-no-fabricated-dd','#fxcPanel-account')


def records_draft(page,out,case):
    risk_seed(page,1)
    # The older table seed uses envelope 2, whereas current DEFAULTS declares
    # envelope 1 and lifecycle emits individual records at version 2. Exercise
    # the actual supported envelope; do not alter either production schema.
    page.evaluate("""()=>{S.operationHistory=structuredClone(DEFAULTS.operationHistory);
      if(save()!==true)throw Error('Synthetic supported history refused');markSessionCheckpoint();}""")
    revised=page.evaluate("""()=>{
      const r=operationRecordOrder(0,0,{sl:1.18},{reason:'Synthetic revised stop'});
      if(!r.ok)throw Error(JSON.stringify(r));JPWForex.executionBoardUI.render();return JPWForex.executionBoard.read();
    }""")
    settle(page);before=financial(page)
    records=revised['operationRecords'];assert records['source']=='JPW_LOCAL_RECORDS'
    assert len(records['operations'])==1
    kinds=[event['kind'] for event in records['operations'][0]['events']]
    assert 'OPERATION_CREATED' in kinds and 'ORDER_RECORDED' in kinds and 'ORDER_REVISED' in kinds,kinds
    assert page.locator('#ebRecordsList [data-eb-record-kind]').count()==len(kinds)
    page.locator('#ebRecordsDisclosure > summary').click();settle(page)
    set_field(page,'sl','1.199');editor=field(page,'sl').element_handle()
    editor.evaluate('e=>e.setSelectionRange(2,5)')
    initial=page.locator('#ebRecordsList').inner_text()
    page.locator('[data-eb-record-detail]').last.click();settle(page)
    dialog=page.locator('dialog[open]');assert dialog.count()==1
    assert 'Synthetic revised stop' in dialog.inner_text()
    page.keyboard.press('Escape');settle(page)
    assert editor.evaluate('e=>e.isConnected&&e.value==="1.199"&&e.selectionStart===2&&e.selectionEnd===5')
    assert page.locator('#ebRecordsList').inner_text()==initial
    assert financial(page)==before
    page.locator('[data-eb-cancel-row="0:0"]').click();settle(page)
    assert field(page,'sl').input_value()=='1.18'
    assert financial(page)==before
    case['records']=records
    shot(page,out,'operation-records','#ebOperationRecords')
    closed=page.evaluate("""()=>{
      const require=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
      require(operationRecordOrder(0,0,{status:'Fechada',result:50,costs:0},{reason:'Synthetic recorded close'}));
      const api=JPWForex.state,scope=api.operationalSelection(),ctx=api.accountContext(scope);
      const snapshot=require(operationBuildSnapshot(structuredClone(ctx.value.activeOperation),{defenseCount:0}));
      require(api.finalizeAccountOperation(snapshot.record,{...scope,expectedRevision:ctx.revision,
        expectedEpoch:jpWealthPersistenceEpoch(),reason:'Synthetic formal closing'}));
      JPWForex.executionBoardUI.discard();JPWForex.executionBoardUI.render();
      return JPWForex.executionBoard.read();
    }""")
    settle(page);before=financial(page)
    closed_record=closed['operationRecords']['operations'][0]
    assert closed_record['status']=='CLOSED'
    closed_events=closed_record['events'];assert sum(e['kind']=='OPERATION_CLOSED' for e in closed_events)==1
    assert any(e['kind']=='ORDER_CLOSED' for e in closed_events)
    assert all(e.get('at') for e in closed_events),'Missing dates were invented instead of surfaced'
    if not page.locator('#ebRecordsDisclosure').evaluate('e=>e.open'):
        page.locator('#ebRecordsDisclosure > summary').click();settle(page)
    page.locator('[data-eb-record-detail]').last.click();settle(page)
    assert page.locator('dialog[open]').count()==1
    page.keyboard.press('Escape');settle(page)
    assert financial(page)==before
    assert page.evaluate('S.operationHistory.records.length')==1
    assert page.evaluate('S.operationHistory.schemaVersion===DEFAULTS.operationHistory.schemaVersion')
    assert page.evaluate('S.operationHistory.records[0].schemaVersion')==2,'Finalized record uses lifecycle version 2'
    case['closedRecords']=closed['operationRecords']
    shot(page,out,'operation-records-closed','#ebOperationRecords')
    page.evaluate("""()=>{S.operationHistory.schemaVersion=2;
      if(save()!==true)throw Error('Synthetic future envelope refused');markSessionCheckpoint();}""")
    before=financial(page)
    future=page.evaluate('()=>{JPWForex.executionBoardUI.render();return JPWForex.executionBoard.read();}')
    settle(page)
    assert future['operationRecords']['operations']==[],'Future envelope must remain opaque'
    assert future['operationRecords']['coverage'] in ['PARTIAL','UNAVAILABLE']
    assert future['operationRecords']['issues']
    assert financial(page)==before,'Unsupported history was normalized or rewritten'
    case['futureEnvelope']=future['operationRecords']


def matrix(page,out,case,layout):
    projected=seed(page);page.evaluate('l=>mountNavigationLayout(l)',layout);settle(page)
    before=financial(page);case['geometry']=[]
    for width in [1440,1024,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme);settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(layout,width,theme,'Global overflow')
            for tab in ['account','history','statistics','risks']:
                page.locator('#fxcTab-'+tab).click();settle(page)
                dimensions=page.locator('#fxcPanel-'+tab).evaluate('e=>({width:e.clientWidth,scroll:e.scrollWidth})')
                assert dimensions['scroll']<=dimensions['width']+1,(layout,width,theme,tab,dimensions)
            page.locator('#fxcTab-account').click();settle(page)
            assert_curves(page,projected)
            geometry=page.locator('#fxcPanel-account figure.fxc-chart').evaluate_all("""els=>els.map(e=>{const svg=e.querySelector('svg'),r=svg?.getBoundingClientRect(),v=svg?.viewBox.baseVal;
              return {key:e.dataset.fxcSeries,width:e.clientWidth,scroll:e.scrollWidth,svgWidth:r?.width,svgHeight:r?.height,viewWidth:v?.width,viewHeight:v?.height,preserve:svg?.getAttribute('preserveAspectRatio')};})""")
            for g in geometry:
                assert g['scroll']<=g['width']+1,(layout,width,theme,g)
                assert g['preserve']!='none' and g['svgWidth']>90 and g['svgHeight']>=80,g
                assert abs(g['svgWidth']/g['svgHeight']-g['viewWidth']/g['viewHeight'])<.08,g
            assert financial(page)==before
            case['geometry'].append({'width':width,'theme':theme,'plots':geometry})
            if width in [1440,390]:shot(page,out,f'panel-{layout}-{width}-{theme}','#fxcPanel-account')


def touch(page,out,case):
    page.set_viewport_size({'width':390,'height':844});seed(page);before=financial(page)
    assert page.evaluate("matchMedia('(pointer:coarse)').matches")
    cursor=curve(page).locator('.fxc-chart-cursor');old=cursor.input_value();cursor.tap();settle(page)
    assert cursor.input_value()!=old
    assert curve(page).get_attribute('data-selected-point')==curve(page,'drawdown').get_attribute('data-selected-point')
    for selector in ['[data-fxc-preset="3m"]','#fxcTab-statistics','[data-fxc-month-mode="nominal"]']:
        rect=page.locator(selector).bounding_box();assert rect['height']>=44 and rect['width']>=44,(selector,rect)
    page.locator('[data-fxc-month-mode="nominal"]').tap();page.locator('[data-fxc-month="2026-07"]').tap();settle(page)
    assert page.locator('#fxcPanel-history').is_visible()
    assert financial(page)==before
    case['touch']='Coarse pointer emulation: synchronized cursor, month drilldown and targets'
    shot(page,out,'touch-month-movements','#fxcPanel-history')


def native_zoom(pw,url,out,case):
    profile=Path(tempfile.mkdtemp(prefix='professional-native-200-',dir=out));(profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options();options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    context=pw.chromium.launch_persistent_context(str(profile),**options)
    try:
        context.add_init_script('window.__onbShown=true;');install_bootstrap(context)
        page=context.pages[0] if context.pages else context.new_page();page.set_default_timeout(15000)
        page.on('dialog',lambda d:d.accept());page.goto(url);ready(page);seed(page)
        ratio=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
        if abs(ratio['outer']/ratio['inner']-2)>=.01 or ratio['css']!='1':raise RuntimeError('Native zoom unavailable: '+str(ratio))
        before=financial(page)
        for tab in ['account','history','statistics','risks']:
            page.locator('#fxcTab-'+tab).click();settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),tab
        page.locator('#fxcTab-account').click();cursor=curve(page).locator('.fxc-chart-cursor')
        cursor.focus();page.keyboard.press('End');settle(page)
        assert cursor.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
        assert curve(page).get_attribute('data-selected-point')==curve(page,'drawdown').get_attribute('data-selected-point')
        assert financial(page)==before
        curve(page).scroll_into_view_if_needed();settle(page)
        cdp=context.new_cdp_session(page)
        (out/'professional-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        assert_fixture_requests(context);case['nativeZoom']=ratio
    finally:context.close();shutil.rmtree(profile)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cases');parser.add_argument('--native-zoom',action='store_true');args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True);before=hashes()
    report={'root':str(ROOT),'source_sha256':before,'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'classification':'NOT_RUN','cases':[],'limits':{'Safari':'NOT_RUN','physical_touch':'NOT_RUN','screen_reader':'NOT_RUN','native_zoom':'requested' if args.native_zoom else 'NOT_RUN'}}
    cases=[('integrated',integrated),('filters',filters),('monthly',monthly),('statistics',statistics),
        ('missing-summary-manual',missing_summary_manual),('records-draft',records_draft)]
    cases += [('layout-'+layout,partial(matrix,layout=layout)) for layout in ['sidebar','topbar','glass','submenu']]
    cases += [('touch',touch)]
    chosen=set(args.cases.split(',')) if args.cases else None
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'
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
                page.on('pageerror',lambda error,c=case:c['pageerrors'].append(str(error)));page.on('dialog',lambda d:d.accept())
                try:
                    page.goto(url);ready(page);check(page,args.out,case)
                    assert not case['pageerrors'],case['pageerrors'];assert_fixture_requests(context);case['classification']='PASS'
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
        assert before==hashes(),'Sources changed during focal; rerun on frozen bytes'
        failed=[case for case in report['cases'] if case['classification']!='PASS']
        report['classification']=failed[0]['classification'] if failed else 'PASS'
    except BaseException as error:report.update(classification='ENVIRONMENT_ERROR',error=str(error),trace=traceback.format_exc())
    finally:
        server.shutdown();(args.out/'professional-panel-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['classification']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())

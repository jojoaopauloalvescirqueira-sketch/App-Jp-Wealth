#!/usr/bin/env python3
"""Behavioral edit-cost contract using real UI and disposable synthetic state.
Counters delegate to original domain APIs; no financial projection is replaced.
"""
import argparse
from functools import partial
import json
import hashlib
from pathlib import Path
import threading
import traceback
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_execution_table_test import Server, Quiet, ready
from forex_execution_workbook_test import seed
from forex_clarity_test import SEED, save_example_order
from notes_launcher_test import launch_options, settle
ROOT=Path(__file__).resolve().parents[1]
INSTRUMENT=r"""() => {
  window.__cost={read:0,context:0,selection:0,orderChecks:0,preview:0,measure:0,writes:0};
  const wrap=(object,name,key)=>{const original=object[name];return (...args)=>{__cost[key]++;return original.apply(object,args);};};
  const board=JPWForex.executionBoard,state=JPWForex.state;
  JPWForex.executionBoard={...board,read:wrap(board,'read','read'),previewOrder:wrap(board,'previewOrder','preview')};
  JPWForex.state={...state,accountContext:wrap(state,'accountContext','context'),operationalSelection:wrap(state,'operationalSelection','selection')};
  // supported() uses lexical domain references, so API wrappers alone cannot
  // detect its traversal. Observe actual array validation callbacks without
  // changing any fixture array, value or financial result.
  const watched=new Set();
  for(const account of Object.values(S.forex.accountContexts.accounts))for(const period of Object.values(account.periods))
    for(const phase of period.phases){watched.add(phase.orders);for(const order of phase.orders)if(order.revisions)watched.add(order.revisions);}
  const every=Array.prototype.every;
  Array.prototype.every=function(callback,thisArg){
    return every.call(this,watched.has(this)?function(...args){__cost.orderChecks++;return callback.apply(thisArg,args);}:callback,thisArg);
  };
  const measure=CanvasRenderingContext2D.prototype.measureText;
  CanvasRenderingContext2D.prototype.measureText=function(...args){__cost.measure++;return measure.apply(this,args);};
  const set=Storage.prototype.setItem;
  Storage.prototype.setItem=function(...args){if(this===localStorage)__cost.writes++;return set.apply(this,args);};
  window.__resetCost=()=>Object.keys(__cost).forEach(k=>__cost[k]=0);
  JPWForex.executionBoardUI.render();
}"""

NAV_INSTRUMENT=r"""() => {
  window.__navCost={reads:0,clones:0,globalClones:0};let inside=0;
  const api=JPWForex.executionBoardUI,paint=api.render,board=JPWForex.executionBoard,read=board.read,clone=window.structuredClone;
  api.render=function(...args){inside++;try{return paint.apply(this,args)}finally{inside--}};
  JPWForex.executionBoard={...board,read:function(...args){__navCost.reads++;const value=read.apply(this,args);if(inside)window.__lastNavPaintModel=value;return value}};
  window.structuredClone=function(value,...args){if(inside){__navCost.clones++;if(value===S||value===S.forex||value?.phases||value?.accountContexts||Array.isArray(value)&&value.some(x=>Array.isArray(x?.orders)))__navCost.globalClones++;}return clone.call(this,value,...args)};
  window.__resetNavCost=()=>{Object.keys(__navCost).forEach(k=>__navCost[k]=0);window.__lastNavPaintModel=null;};
}"""

def navigation_checks(page,check):
    page.evaluate(NAV_INSTRUMENT)
    def warm():
        page.evaluate('JPWForex.executionBoardUI.discard()');page.evaluate(SEED);settle(page)
        page.wait_for_function("JPWNavigation.current().canonical==='forex-operation' && JPWExec.ui.getView()==='panel'")
        # Navigation needs only row 0:0. Keep the authorized anonymous-slot
        # preparation and real Add control, without adding five unused rows
        # and scrolling six distant phase controls on every invalidation case.
        assert page.locator('.eb-order-row').count()==0
        page.evaluate("""()=>{const scope=JPWForex.state.operationalSelection(),phases=S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].phases;
          const anonymous=o=>!o.id&&!o.par&&!o.brokerHash&&!o.orderId&&!o.recordStatus&&!o.status&&o.lote===0&&o.entry===0&&o.sl===0&&o.tp===0&&o.result===null;
          if(!phases.every(p=>p.orders.length===1&&anonymous(p.orders[0])))throw Error('Synthetic navigation setup expected untouched anonymous zero slots');
          phases.forEach(p=>{p.orders=[]});if(save()!==true)throw Error('Synthetic navigation empty layout refused');renderPhases();}""")
        page.locator('[data-addorder="0"]').click();settle(page)
        assert page.locator('[data-eb-row="0:0"]').is_visible()
        page.evaluate('JPWForex.executionBoardUI.render()');settle(page)
    def enter():
        page.evaluate('__resetNavCost();JPWNavigation.navigate("forex-operation")')
        page.evaluate('async()=>{await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')
        return page.evaluate('({...__navCost})')
    warm()
    page.evaluate("window.__navEditor=document.querySelector('[data-p=\"0\"][data-o=\"0\"][data-f=entry]');window.__navTable=document.querySelector('#ebOrderScroll table');__resetNavCost();JPWNavigation.navigate('forex-history');JPWNavigation.navigate('forex-operation')")
    settle(page);cost=page.evaluate('({...__navCost})')
    preserved=page.evaluate("__navEditor===document.querySelector('[data-p=\"0\"][data-o=\"0\"][data-f=entry]')&&__navTable===document.querySelector('#ebOrderScroll table')")
    check('navigation unchanged: zero Board reads/global clones and mounted editor',cost['reads']==0 and cost['globalClones']==0 and preserved,cost)
    for repeat in range(3):
        page.evaluate('__resetNavCost();JPWNavigation.navigate("forex-history");JPWNavigation.navigate("forex-operation")');settle(page);cost=page.evaluate('({...__navCost})')
        check('repeated settled navigation '+str(repeat)+': zero Board reads/clones',cost['reads']==0 and cost['clones']==0,cost)
    page.evaluate('__resetNavCost();render()');settle(page);cost=page.evaluate('({...__navCost})')
    check('explicit root render always refreshes Board',cost['reads']>0,cost)
    for partial in [False,True]:
        warm();page.evaluate("JPWNavigation.navigate('forex-history')")
        writer=page.evaluate("""()=>{const scope=JPWForex.state.operationalSelection();return JPWForex.state.recordAccountFacts({accountIndex:0,periodId:scope.periodId,si:10000,equity:9500,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'Synthetic hidden navigation equity',observedAt:'2026-09-22T13:00:00Z'},{reason:'Synthetic hidden writer'})}""")
        assert writer['ok'] and writer['persistido'],writer
        if partial:page.evaluate('JPWForex.executionBoardUI.renderPhases()')
        cost=enter();equity=page.locator('#executionBoardAccount .eb-metric').filter(has=page.locator('span',has_text='Equity observada')).locator('strong').inner_text()
        expected=page.evaluate("fmtForexMoney(9500,{currency:'USD'},2)")
        check(('public table-only render' if partial else 'confirmed hidden writer')+': full current Board on entry',cost['reads']>0 and equity==expected,{'writer':writer,'cost':cost,'equity':equity,'expected':expected})
    mutations={
      'revision':"const s=JPWForex.state.operationalSelection();S.forex.accountContexts.accounts[s.accountId].periods[s.periodId].revision++",
      'persisted raw without epoch':"S.protocolBreaches++;if(save()!==true)throw Error('Synthetic raw save refused')",
      'instrument in-place input':"S.instruments[0].preco=(S.instruments[0].preco||1)+.01",
      'quotes event':"window.dispatchEvent(new Event('jpwealth:forex-quotes'))",
      'session rotation':"sessionEpochRotate()",
      'discard/reset':"JPWForex.executionBoardUI.discard()",
      'public table-only refresh':"JPWForex.executionBoardUI.renderPhases()",
      'DOM displayed text replacement':"const n=document.querySelector('#executionBoardAccount strong');n.textContent='Synthetic stale display'",
      'DOM child replacement':"const n=document.querySelector('#executionBoardAccount .eb-capital-strip');n.replaceWith(n.cloneNode(true))",
      'DOM replacement':"const n=document.getElementById('ebExposureSummary');n.replaceWith(n.cloneNode(true))",
      'RAM operation history':"S.operationHistory={schemaVersion:1,records:[]}",
      'RAM legacy operation':"S.activeOperation={operationId:'SYNTHETIC-LEGACY-NAV'}",
      'RAM quarantine':"S.quarantine={releasedAt:null}",
      'RAM profile reference':"S.profiles={...S.profiles}",
      'support version':"S.forex.schemaVersion=999",
      'programmatic selection':"const s=JPWForex.state.operationalSelection(),id=Object.keys(S.forex.accountContexts.accounts).find(id=>id!==s.accountId),a=S.forex.accountContexts.accounts[id];const r=JPWForex.state.selectOperationalContext(id,a.currentPeriodId);if(!r.ok)throw Error(JSON.stringify(r))"
    }
    for name,mutation in mutations.items():
        warm();page.evaluate("JPWNavigation.navigate('forex-history')");page.evaluate('()=>{'+mutation+'}')
        cost=enter();check('navigation invalidation '+name+': full refresh',cost['reads']>0,cost)
    # Direct RAM child replacement is conservative invalidation, even without
    # a confirmed write changing raw, parent identity or period revision.
    for child in ['account facts','period grid','period reserves']:
        warm()
        if child=='period grid':save_example_order(page)
        page.evaluate('JPWForex.executionBoardUI.render()');settle(page)
        page.evaluate("JPWNavigation.navigate('forex-history')")
        expected=page.evaluate("""child=>{const s=JPWForex.state.operationalSelection(),f=S.forex,p=f.accountContexts.accounts[s.accountId].periods[s.periodId],before={raw:jpWealthLastPersistedRawGet(),epoch:jpWealthPersistenceEpoch(),revision:p.revision};
          if(child==='account facts')f.accounts[s.accountId]={...f.accounts[s.accountId],equity:9400};
          if(child==='period grid')p.grid={...p.grid,operationId:p.activeOperation.operationId,declaredPhase:3,structureKnown:true};
          if(child==='period reserves')p.reserves={accountId:s.accountId,periodId:s.periodId,currency:p.currency,fcrConstituted:1234,feoConstituted:1234,fcrLiquidityDays:0,feoLiquidityDays:0,verifiedAt:'2026-09-22T13:00:00Z',verificationRecorded:true};
          const m=JPWForex.executionBoard.read();return {equity:fmtForexMoney(m.capital.equity.value,{currency:m.scope.currency},2),grid:m.risk.activeGridPhase.value,findings:m.findings.map(x=>x.message||x.reason||x.code||String(x)),unchanged:before.raw===jpWealthLastPersistedRawGet()&&before.epoch===jpWealthPersistenceEpoch()&&before.revision===p.revision};}""",child)
        cost=enter();observed=page.evaluate("""()=>({equity:[...document.querySelectorAll('#executionBoardAccount .eb-metric')].find(x=>x.querySelector('span')?.textContent==='Equity observada')?.querySelector('strong').textContent,findings:[...document.querySelectorAll('#ebExposureSummary li')].map(x=>x.textContent),grid:window.__lastNavPaintModel?.risk.activeGridPhase.value??null})""")
        current=observed['equity']==expected['equity'] and observed['findings']==expected['findings'] and (child!='period grid' or observed['grid']==expected['grid'])
        check('RAM child '+child+': refresh and current painted values',expected['unchanged'] and cost['reads']>0 and current,{'cost':cost,'expected':expected,'observed':observed})
    # A failed full paint must never leave the previous certificate reusable.
    warm();page.evaluate("""()=>{const original=JPWForex.executionBoard.read;JPWForex.executionBoard.read=()=>{throw Error('Synthetic paint failure')};try{JPWForex.executionBoardUI.render()}catch(e){if(e.message!=='Synthetic paint failure')throw e}finally{JPWForex.executionBoard.read=original}JPWNavigation.navigate('forex-history')}""")
    cost=enter();check('failed full refresh invalidates complete-view certificate',cost['reads']>0,cost)
    warm();page.evaluate("""()=>{const original=renderHeaderReadout;renderHeaderReadout=()=>{throw Error('Synthetic late paint failure')};try{JPWForex.executionBoardUI.render()}catch(e){if(e.message!=='Synthetic late paint failure')throw e}finally{renderHeaderReadout=original}JPWNavigation.navigate('forex-history')}""")
    cost=enter();check('failed final painter invalidates complete-view certificate',cost['reads']>0,cost)
    warm();page.evaluate("""()=>{const original=JPWForex.executionBoard.read;JPWForex.executionBoard.read=(...args)=>{const result=original(...args),s=JPWForex.state.operationalSelection();S.forex.accountContexts.accounts[s.accountId].periods[s.periodId].revision++;return result};try{JPWForex.executionBoardUI.render()}finally{JPWForex.executionBoard.read=original}JPWNavigation.navigate('forex-history')}""")
    cost=enter();check('source change during complete paint prevents certification',cost['reads']>0,cost)
    # Inspection established no time expiry in current Board financial readers.
    # A future expiry added to the model must break this characterization.
    warm();page.clock.set_fixed_time(1791979200000)
    before=page.evaluate('JSON.stringify(JPWForex.executionBoard.read())');page.evaluate('JPWForex.executionBoardUI.render();JPWNavigation.navigate("forex-history")')
    page.clock.set_fixed_time(1792065600000);cost=enter();after=page.evaluate('JSON.stringify(JPWForex.executionBoard.read())')
    check('clock-only change: current Board model has no temporal expiry',before==after and cost['reads']==0,{'equivalent':before==after,'cost':cost})
    # Existing dialog returns focus but resets the reason selection to 0/0.
    # Preserve its measured before-source behavior; editing caret is checked above.
    warm();page.locator('[data-eb-open-detail="0:0"]').click();page.locator('[data-eb-reason="0:0"]').wait_for(state='visible');page.evaluate("""()=>{const e=document.querySelector('[data-eb-reason="0:0"]');e.focus();e.value='Synthetic navigation draft';e.setSelectionRange(2,5);e.dispatchEvent(new Event('input',{bubbles:true}));window.__navDraft=e;window.__navAccepted=JPWNavigation.navigate('forex-history');}""")
    page.locator('#ebLeaveStay').click();settle(page)
    guarded=page.evaluate("""()=>({accepted:__navAccepted,current:JPWNavigation.current().canonical,same:__navDraft===document.querySelector('[data-eb-reason="0:0"]'),focused:document.activeElement===__navDraft,value:__navDraft.value,start:__navDraft.selectionStart,end:__navDraft.selectionEnd})""")
    check('navigation guard preserves focused draft and existing dialog caret',guarded['accepted'] is False and guarded['current']=='forex-operation' and guarded['same'] and guarded['focused'] and guarded['value']=='Synthetic navigation draft' and guarded['start']==0 and guarded['end']==0,guarded)
    page.evaluate('JPWForex.executionBoardUI.discard();JPWForex.executionBoardUI.render();JPWNavigation.navigate("forex-history");markJPWealthPersistenceOutcomeUnknown("Synthetic navigation unknown outcome")')
    cost=enter();check('unknown persistence outcome never reuses mounted certificate',cost['reads']>0,cost)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',type=Path,required=True);args=parser.parse_args()
    args.artifacts.mkdir(parents=True,exist_ok=True)
    sources=['src/js/20-ui/30-execution-board.js','src/js/20-ui/03-main-render.js','src/js/40-app/01-navigation.js','src/js/10-domain/00-forex-state.js']
    fingerprints=lambda:{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources}
    report={'checks':[],'source_sha256':fingerprints(),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};failures=[]
    def check(name,condition,observed):
        report['checks'].append({'name':name,'pass':bool(condition),'observed':observed})
        if not condition:failures.append(name)
    server=None
    try:
      server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
      threading.Thread(target=server.serve_forever,daemon=True).start()
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options());context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
        install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
        page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');ready(page);seed(page)
        page.evaluate(INSTRUMENT);settle(page)
        # A projection repaint must not remeasure unchanged workbook strings.
        for repaint in range(2):
          page.evaluate('__resetCost();JPWForex.executionBoardUI.render()')
          settle(page)
          cost=page.evaluate('({...__cost})')
          check('unchanged repaint '+str(repaint)+': zero text measurement',cost['measure']==0,cost)
        # Same mounted control receives both native event families. The geometry
        # tuple is identical on change; its second preview has no useful work.
        for name,value,limit in [('id','SYNTHETIC-ID',0),('lote','0.2',0),('tipo','SELL',0),('role','OTHER',0),('par','EURUSD',1),('entry','1.25',1),('sl','1.1',1),('tp','1.5',1)]:
          page.evaluate('__resetCost()')
          page.evaluate("""({name,value})=>{const e=document.querySelector(`[data-p="0"][data-o="0"][data-f="${name}"]`);
            window.__editor=e;e.focus();e.value=value;
            if(e.tagName==='INPUT')e.setSelectionRange(1,Math.min(2,value.length));
            const scroll=document.getElementById('ebOrderScroll');
            window.__editorBefore={start:e.selectionStart,end:e.selectionEnd,left:scroll.scrollLeft,top:scroll.scrollTop};
            e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));
          }""",{'name':name,'value':value})
          # Drain microtasks and two animation frames before ALL assertions.
          # Moving expensive work or writes to an async callback cannot pass.
          page.evaluate('() => Promise.resolve().then(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))))')
          observed=page.evaluate("""name=>({cost:{...__cost},
            mounted:__editor===document.querySelector(`[data-p="0"][data-o="0"][data-f="${name}"]`),
            focused:document.activeElement===__editor,caret:__editor.selectionStart===__editorBefore.start&&__editor.selectionEnd===__editorBefore.end,
            scroll:document.getElementById('ebOrderScroll').scrollLeft===__editorBefore.left&&document.getElementById('ebOrderScroll').scrollTop===__editorBefore.top})""",name)
          check(name+': no full projection/context read per keystroke',observed['cost']['read']==0 and observed['cost']['context']==0 and observed['cost']['selection']==0 and observed['cost']['orderChecks']==0,observed)
          check(name+': preview only once for geometry',observed['cost']['preview']==limit,observed)
          check(name+': RAM-only mounted focused editor',observed['cost']['writes']==0 and observed['mounted'] and observed['focused'] and observed['caret'] and observed['scroll'],observed)
          # Six visible rows, twenty columns: an edit must measure at most one
          # row, independent of total workbook height.
          check(name+': sizing proportional to edited row',observed['cost']['measure']<=20,observed)
        # A fresh projection object with identical confirmed inputs must reuse
        # the existing draft geometry; repainting is not a new edit.
        for repaint in range(2):
          page.evaluate('__resetCost();JPWForex.executionBoardUI.render()')
          settle(page)
          cost=page.evaluate('({...__cost})')
          check('unchanged draft repaint '+str(repaint)+': no new geometry preview',cost['preview']==0,cost)
          check('unchanged draft repaint '+str(repaint)+': zero text measurement',cost['measure']==0,cost)
        # Change a confirmed instrument observation through the existing writer.
        # Its ATR changes only the draft EURUSD row's displayed diagnostics;
        # unrelated rows must not be measured during the projection refresh.
        before_rows=page.locator('.eb-order-row').evaluate_all("""rows=>Object.fromEntries(rows.map(row=>
          [row.dataset.ebRow,[...row.querySelectorAll('[data-eb-calc]')].map(cell=>cell.textContent)]))""")
        observation=page.evaluate("""() => {
          const scope={...JPWForex.state.operationalSelection(),instrumentId:'EURUSD'};
          return JPWForex.state.recordInstrumentContext({...scope,
            expectedRevision:JPWForex.state.instrumentContext(scope).revision,componentChanges:{
              atr:{short:.004,long:.001,timeframe:'H4',unit:'PRICE',source:'Synthetic dirty-row observation',observedAt:'2026-09-22T12:00:00Z'}
            }},{reason:'Synthetic measured repaint',expectedEpoch:jpWealthPersistenceEpoch()});
        }""")
        assert observation['ok'],observation
        page.evaluate('__resetCost();JPWForex.executionBoardUI.render()')
        settle(page)
        after_rows=page.locator('.eb-order-row').evaluate_all("""rows=>Object.fromEntries(rows.map(row=>
          [row.dataset.ebRow,[...row.querySelectorAll('[data-eb-calc]')].map(cell=>cell.textContent)]))""")
        cost=page.evaluate('({...__cost})')
        changed_rows=[key for key,values in after_rows.items() if before_rows.get(key)!=values]
        check('confirmed observation: only one row changes displayed diagnostics',changed_rows==['0:0'],changed_rows)
        check('confirmed observation: measure only changed presentation rows',0<cost['measure']<=20*len(changed_rows),{'cost':cost,'changed_rows':changed_rows})
        # Direct fixture mutation deliberately retains S and Forex references.
        # A save may refresh the persisted raw token without advancing epoch.
        # A subsequent edit must use fresh confirmed geometry in both cases.
        for marker in ['revision','save-without-epoch']:
          baseline=page.evaluate("""() => {
            JPWForex.executionBoardUI.discard();const selected=JPWForex.state.operationalSelection();
            const period=S.forex.accountContexts.accounts[selected.accountId].periods[selected.periodId];
            const order=period.phases[0].orders[0];order.par='EURUSD';order.entry=1.25;order.sl=1;order.tp=2;
            JPWForex.executionBoardUI.render();window.__sameS=S;window.__sameForex=S.forex;
            return {epoch:jpWealthPersistenceEpoch(),raw:jpWealthLastPersistedRawGet()};
          }""")
          settle(page)
          changed=page.evaluate("""marker => {
            const selected=JPWForex.state.operationalSelection();
            const period=S.forex.accountContexts.accounts[selected.accountId].periods[selected.periodId];
            period.phases[0].orders[0].sl=1.1;
            if(marker==='revision')period.revision++;else if(save()!==true)throw Error('Synthetic save refused');
            return {same:S===__sameS&&S.forex===__sameForex,epoch:jpWealthPersistenceEpoch(),raw:jpWealthLastPersistedRawGet()};
          }""",marker)
          check(marker+': setup retains references and epoch',changed['same'] and changed['epoch']==baseline['epoch'],changed['same'])
          if marker=='save-without-epoch':check(marker+': persisted token changed',changed['raw']!=baseline['raw'],True)
          page.evaluate("""() => {
            const e=document.querySelector('[data-p="0"][data-o="0"][data-f="entry"]');
            e.value='1.5';e.dispatchEvent(new Event('input',{bubbles:true}));
          }""")
          settle(page)
          observed=page.locator('[data-eb-row="0:0"] [data-eb-calc="stopDistance"]').text_content()
          check(marker+': fresh confirmed stop used by next preview',observed.strip()=='0,4',observed)
        selected=page.evaluate("""() => {
          JPWForex.executionBoardUI.discard();const selected=JPWForex.state.operationalSelection();
          const other=Object.keys(S.forex.accountContexts.accounts).find(id=>id!==selected.accountId);
          const account=S.forex.accountContexts.accounts[other],period=account.periods[account.currentPeriodId];
          Object.assign(period.phases[0].orders[0],{par:'EURUSD',entry:1.25,sl:1.2,tp:2});
          if(save()!==true)throw Error('Synthetic second context save refused');
          JPWForex.executionBoardUI.render();
          const before=jpWealthLastPersistedRawGet(),epoch=jpWealthPersistenceEpoch();
          const result=JPWForex.state.selectOperationalContext(other,period.periodId);
          if(!result.ok)throw Error('Synthetic programmatic selection refused');
          return {sameRaw:before===jpWealthLastPersistedRawGet(),sameEpoch:epoch===jpWealthPersistenceEpoch()};
        }""")
        check('programmatic selection: no save or epoch change',selected['sameRaw'] and selected['sameEpoch'],selected)
        page.evaluate("""() => {const e=document.querySelector('[data-p="0"][data-o="0"][data-f="entry"]');
          e.value='1.5';e.dispatchEvent(new Event('input',{bubbles:true}));}""")
        settle(page)
        fresh=page.locator('[data-eb-row="0:0"] [data-eb-calc="stopDistance"]').text_content()
        check('programmatic selection without render: fresh context preview',fresh.strip()=='0,3',fresh)
        navigation_checks(page,check)
        assert_fixture_requests(context);context.close();browser.close()
        check('sources frozen throughout focal',fingerprints()==report['source_sha256'],fingerprints())
    except BaseException as error:
      report['result']='HARNESS_ERROR';report['error']=str(error);report['traceback']=traceback.format_exc()
      print(json.dumps({'result':'HARNESS_ERROR','error':str(error),'artifacts':str(args.artifacts)},ensure_ascii=False),flush=True)
      raise
    finally:
      if server is not None:server.shutdown()
      report.setdefault('result','FAIL' if failures else 'PASS');report['failures']=failures
      (args.artifacts/'focal-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert not failures,failures
if __name__=='__main__':main()

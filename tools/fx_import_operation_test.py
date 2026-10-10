#!/usr/bin/env python3
"""Synthetic account/phase workflow through the real UI; no operator storage."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

SEED="""() => {
  window.__onbShown=true;closeModal();S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
  S.accounts=[];S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
  if(!save())throw Error('Seed not persisted');render();
  JPWNavigation.navigate('forex-operation');JPWNavigation.navigateLocal('exec','panel');renderPhases();
}"""
CONTEXT="""() => {
  S.accounts=[{forexAccountId:'TEST_PHASE_A',nome:'TESTE — Conta A',tipo:'MESTRE',platform:'MT5',platformLogin:'90001',platformCurrency:'USD'},
    {forexAccountId:'TEST_PHASE_B',nome:'TESTE — Conta B',tipo:'PRÓPRIA',platform:'MT5',platformLogin:'90002',platformCurrency:'USD'}];
  if(!save())throw Error('Seed registration not persisted');
  for(const [id,si] of [['TEST_PHASE_A',10000],['TEST_PHASE_B',5000]]){
    const r=JPWForex.state.recordAccountPeriod({accountId:id,startedAt:'2026-09-01',currency:'USD',si,openingBook:si,source:'TESTE — fixture determinística',activateCurrentPeriod:true},{reason:'TESTE — contexto',expectedEpoch:jpWealthPersistenceEpoch()});
    if(!r.ok)throw Error(JSON.stringify(r));
  }
  JPWForex.state.selectOperationalAccount('TEST_PHASE_A');render();renderPhases();
}"""

def run(page,out,tag,checks):
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('dialog',lambda d:d.accept())
    wait_bootstrap(page);page.evaluate(SEED)
    def ok(name,condition):
        assert condition,name
        checks.append({'scenario':tag+' / '+name,'result':'PASS'})
    before=page.evaluate('JSON.stringify(S.forex.accountContexts)')
    ok('empty account exposes six phase groups and refuses unconfirmed order editors',page.locator('.eb-phase-group').count()==6 and page.locator('[data-addorder]').count()==0)
    ok('empty account has actionable setup',page.locator('.eb-setup-prompt [data-eb-manage]').is_visible())
    page.evaluate('()=>{for(let i=0;i<3;i++){render();renderPhases();}}')
    ok('empty render creates no account facts',before==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    page.evaluate(CONTEXT)
    before=page.evaluate('JSON.stringify(S.forex.accountContexts)')
    page.evaluate('()=>{render();renderPhases();}')
    ok('confirmed render does not write',before==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    ok('six confirmed phase groups',page.locator('.eb-phase-group').count()==6)
    page.locator('[data-eb-phase-jump="5"]').click()
    ok('phase shortcut focuses the chosen section',page.evaluate("document.activeElement===document.querySelector('#ebPhase-5')"))
    ok('six real order editors',page.locator('.eb-phase-group [data-addorder]').count()==6)
    for pi in range(6):
        page.locator(f'[data-eb-phase-jump="{pi}"]').click()
        page.locator(f'[data-addorder="{pi}"]').click()
        page.locator(f'[data-eb-open-detail="{pi}:1"]').click()
        def field(f):return page.locator(f'[data-p="{pi}"][data-o="1"][data-f="{f}"]')
        field('id').fill(f'TEST-{pi+1}');field('brokerHash').fill(f'0000-HASH-{pi+1}')
        field('par').select_option('EURUSD');field('tipo').select_option('BUY')
        field('role').select_option('GENESIS' if pi==0 else 'OTHER')
        for f,value in [('lote','0.01'),('entry','1.1'),('sl','1.09'),('tp','1.2')]:field(f).fill(value)
        field('status').select_option('Aberta')
        assert page.locator(f'[data-eb-detail="{pi}:1"]').evaluate('(d)=>d.open')
        field('stopValidated').check()
        page.locator(f'[data-eb-save-row="{pi}:1"]').click()
        record=page.evaluate('(pi)=>JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[pi].orders[1]',pi)
        ok(f'phase {pi+1} records UI values in account A',record['id']==f'TEST-{pi+1}' and record['lote']==.01 and record['entry']==1.1 and record['accountId']=='TEST_PHASE_A')
    # More than one blank draft remains visible (legacy CSS used to hide it).
    page.locator('[data-eb-phase-jump="1"]').click()
    for _ in range(2):page.locator('[data-addorder="1"]').click()
    ok('additional blank draft stays visible and receives focus',page.locator('[data-p="1"][data-o="3"][data-f="id"]').is_visible() and page.evaluate("document.activeElement.dataset.o==='3'"))
    saved=page.evaluate('JSON.stringify(S.forex.accountContexts)')
    # Unsaved edits must be cancelable and navigation must guard them.
    page.locator('[data-eb-phase-jump="0"]').click()
    page.locator('[data-p="0"][data-o="1"][data-f="entry"]').fill('2.5')
    page.locator('[data-eb-manage]').first.click()
    ok('preparation guards unsaved order',page.locator('#ebLeaveStay').is_visible())
    page.locator('#ebLeaveStay').click();page.locator('[data-eb-cancel-row="0:1"]').click()
    ok('cancel preserves confirmed values',page.locator('[data-p="0"][data-o="1"][data-f="entry"]').input_value()=='1.1')
    ok('cancel creates no persisted edit',saved==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    page.locator('[data-eb-manage]').first.click()
    page.locator('[data-fx-examine="TEST_PHASE_B"]').click()
    page.locator('#fxAccountsUse').click()
    ok('switch account isolates six other drafts',page.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases.every(p=>p.orders.every(o=>!o.id))"))
    page.locator('[data-eb-manage]').first.click()
    page.locator('[data-fx-examine="TEST_PHASE_A"]').click()
    page.locator('#fxAccountsUse').click()
    page.reload();wait_bootstrap(page)
    page.evaluate("()=>{closeModal();JPWNavigation.navigate('forex-operation');JPWNavigation.navigateLocal('exec','panel');renderPhases();}")
    ok('all six orders survive reload',page.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases.every((p,i)=>p.orders[1].id==='TEST-'+(i+1))"))
    # Native backup contract: export then import in a different browser context.
    payload=page.evaluate("async()=>JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-09-16T12:00:10Z').text())")
    (out/(tag+'-export-payload.json')).write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    target=page.context.browser.new_context(service_workers='block');target.add_init_script('window.__onbShown=true');install_bootstrap(target)
    restored=target.new_page();restored.on('dialog',lambda d:d.accept());restored.goto(page.url);wait_bootstrap(restored)
    restored.evaluate("data=>importFullBackupFile(new File([JSON.stringify(data)],'TESTE.json',{type:'application/json'}))",payload)
    restored.wait_for_function("()=>S.accounts?.some(a=>a.forexAccountId==='TEST_PHASE_A')&&S.workspaceRecovery?.pending===false")
    restored.reload();wait_bootstrap(restored)
    original_context=json.loads(page.evaluate('JSON.stringify(S.forex.accountContexts)'));restored_context=json.loads(restored.evaluate('JSON.stringify(S.forex.accountContexts)'))
    (out/(tag+'-backup-contexts.json')).write_text(json.dumps({'original':original_context,'restored':restored_context},ensure_ascii=False,indent=2))
    ok('complete backup restores account operations exactly',restored_context==original_context)
    target.close()
    if page.locator('#dgBannerClose').count():page.locator('#dgBannerClose').click()
    # A draft enables the final save action, without recording another edit.
    page.locator('[data-p="0"][data-o="1"][data-f="entry"]').fill('1.1001')
    editor_snapshot=page.evaluate_handle('''() => {
      const row=document.querySelector('[data-eb-row="0:1"]');
      return {row,cells:[...row.cells],controls:[...row.querySelectorAll('input,select,button')].map(node=>({node,value:node.value}))};
    }''')
    # Field layout and keyboard jump on desktop, tablet, mobile in both themes.
    for width in (1440,768,390):
        page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
        for theme in ('light','dark'):
            page.evaluate('(theme)=>{S.theme=theme;applyTheme();}',theme)
            page.locator('[data-eb-phase-jump="0"]').click()
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            table=page.locator('.eb-workbook-table')
            scroll=page.locator('#ebOrderScroll')
            ok(f'{theme} {width}px preserves 20 approved workbook columns',table.locator('thead tr').last.locator('th').count()==20)
            geometry=page.evaluate('''snapshot => {
              const e=document.querySelector('#ebOrderScroll'),row=document.querySelector('[data-eb-row="0:1"]'),area=e.getBoundingClientRect();
              const scale=parseFloat(getComputedStyle(e).getPropertyValue('--fs-scale'))||1;
              const frozenWidth=[...e.querySelectorAll('col')].slice(0,2).reduce((sum,col)=>sum+parseFloat(col.style.width.match(/([\\d.]+)px/)[1])*scale,0);
              const rect=node=>{const b=node.getBoundingClientRect();return {left:b.left,right:b.right,width:b.width,height:b.height};};
              return {scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,
                area:{left:area.left,right:area.right},frozenWidth,narrow:document.querySelector('#execPhaseGridsCard').classList.contains('eb-narrow'),
                sameEditors:row===snapshot.row&&snapshot.cells.every((node,index)=>row.cells[index]===node)&&snapshot.controls.every(({node,value})=>node.isConnected&&row.contains(node)&&node.value===value),
                cells:[...row.cells].map(node=>({...rect(node),label:node.dataset.label||''})),controls:[...row.querySelectorAll('input,select,button')].map(rect)};
            }''',editor_snapshot)
            (out/f'{tag}-{width}-{theme}-geometry.json').write_text(json.dumps(geometry,indent=2))
            # FOREX-EXECUTION-BOARD.md:114,135: useful area below 768px,
            # or less than 320px after frozen columns, presents the same controls as a list.
            narrow_eligible=geometry['clientWidth']<768 or geometry['clientWidth']-geometry['frozenWidth']<320
            ok(f'{theme} {width}px responsive mode matches useful area',geometry['narrow']==narrow_eligible)
            ok(f'{theme} {width}px mounted editors and draft values preserved',geometry['sameEditors'] and len(geometry['cells'])==20)
            if narrow_eligible:
                visible_bounds=lambda b:b['width']>0 and b['height']>0 and b['left']>=geometry['area']['left']-2 and b['right']<=geometry['area']['right']+2
                ok(f'{theme} {width}px twenty labeled cells and controls fit the list',all(c['label'] and visible_bounds(c) for c in geometry['cells']) and all(visible_bounds(c) for c in geometry['controls']) and geometry['scrollWidth']<=geometry['clientWidth']+2 and geometry['documentWidth']<=geometry['viewport']+2)
            else:
                ok(f'{theme} {width}px localized horizontal scrolling',geometry['scrollWidth']>geometry['clientWidth'] and geometry['documentWidth']<=geometry['viewport']+2)
            last=page.locator('[data-eb-save-row="0:1"]');last.scroll_into_view_if_needed()
            ok(f'{theme} {width}px final action reachable',last.is_visible() and last.is_enabled())
            scroll.evaluate('e=>e.scrollLeft=0')
            page.locator('#ebPhase-0').screenshot(path=str(out/f'{tag}-{width}-{theme}.png'))
    editor_snapshot.dispose()
    page.locator('[data-eb-cancel-row="0:1"]').click()
    ok('layout draft cancellation preserves confirmed order',page.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[0].orders[1].entry===1.1"))
    ok('no JavaScript errors',not errors)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT.parent/'evidence'/'operation');ap.add_argument('--mode',choices=['modular','portable','all'],default='all');args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    checks=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            paths=['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'] if args.mode=='all' else ['index.html' if args.mode=='modular' else 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']
            for path in paths:
                tag='modular' if path=='index.html' else 'portable'
                for protocol in ('file','http'):
                    context=browser.new_context(viewport={'width':390,'height':844},service_workers='block');context.add_init_script('window.__onbShown=true');install_bootstrap(context)
                    page=context.new_page();page.goto((ROOT/path).as_uri() if protocol=='file' else f'http://127.0.0.1:{server.server_port}/{path}')
                    run(page,args.out,tag+'-'+protocol,checks);context.close();print('PASS',tag,protocol,flush=True)
            browser.close()
    finally:
        server.shutdown();(args.out/'report.json').write_text(json.dumps({'checks':checks},ensure_ascii=False,indent=2))
    print('PASS',len(checks),'behavior assertions')
if __name__=='__main__':main()

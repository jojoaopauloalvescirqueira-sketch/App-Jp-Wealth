#!/usr/bin/env python3
"""Synthetic account/phase workflow through the real UI; no operator storage."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
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
    ok('empty account exposes six phases',page.locator('.eb-phase').count()==6)
    ok('empty account has actionable setup',page.locator('.eb-setup-prompt [data-eb-setup]').is_visible())
    page.locator('[data-eb-phase-jump="5"]').click()
    ok('phase shortcut focuses the chosen section',page.evaluate("document.activeElement===document.querySelector('#ebPhase-5>summary')"))
    page.evaluate('()=>{for(let i=0;i<3;i++){render();renderPhases();}}')
    ok('empty render creates no account facts',before==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    page.evaluate(CONTEXT)
    before=page.evaluate('JSON.stringify(S.forex.accountContexts)')
    page.evaluate('()=>{render();renderPhases();}')
    ok('confirmed render does not write',before==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    ok('six real order editors',page.locator('.eb-phase [data-addorder]').count()==6)
    for pi in range(6):
        page.locator(f'[data-eb-phase-jump="{pi}"]').click()
        def field(f):return page.locator(f'[data-p="{pi}"][data-o="0"][data-f="{f}"]')
        field('id').fill(f'TEST-{pi+1}')
        field('par').select_option('EURUSD');field('tipo').select_option('BUY')
        field('role').select_option('GENESIS' if pi==0 else 'OTHER')
        for f,value in [('lote','0.01'),('entry','1.1'),('sl','1.09'),('tp','1.2')]:field(f).fill(value)
        field('status').select_option('Aberta')
        page.locator(f'[data-eb-detail="{pi}:0"]').evaluate('(d)=>d.open=true')
        field('stopValidated').check()
        page.locator(f'[data-eb-save-row="{pi}:0"]').click()
        record=page.evaluate('(pi)=>JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[pi].orders[0]',pi)
        ok(f'phase {pi+1} records UI values in account A',record['id']==f'TEST-{pi+1}' and record['lote']==.01 and record['entry']==1.1 and record['accountId']=='TEST_PHASE_A')
    # More than one blank draft remains visible (legacy CSS used to hide it).
    page.locator('[data-eb-phase-jump="1"]').click()
    for _ in range(2):page.locator('[data-addorder="1"]').click()
    ok('additional blank draft stays visible and receives focus',page.locator('[data-p="1"][data-o="2"][data-f="id"]').is_visible() and page.evaluate("document.activeElement.dataset.o==='2'"))
    saved=page.evaluate('JSON.stringify(S.forex.accountContexts)')
    # Unsaved edits must be cancelable and navigation must guard them.
    page.locator('[data-eb-phase-jump="0"]').click()
    page.locator('[data-p="0"][data-o="0"][data-f="entry"]').fill('2.5')
    page.locator('[data-eb-setup]').first.click()
    ok('preparation guards unsaved order',page.locator('#ebLeaveStay').is_visible())
    page.locator('#ebLeaveStay').click();page.locator('[data-eb-cancel-row="0:0"]').click()
    ok('cancel preserves confirmed values',page.locator('[data-p="0"][data-o="0"][data-f="entry"]').input_value()=='1.1')
    ok('cancel creates no persisted edit',saved==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    page.locator('#ebAccountSelect').select_option('TEST_PHASE_B')
    ok('switch account isolates six other drafts',page.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases.every(p=>!p.orders[0].id)"))
    page.locator('#ebAccountSelect').select_option('TEST_PHASE_A')
    page.reload();wait_bootstrap(page)
    page.evaluate("()=>{closeModal();JPWNavigation.navigate('forex-operation');JPWNavigation.navigateLocal('exec','panel');renderPhases();}")
    ok('all six orders survive reload',page.evaluate("JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases.every((p,i)=>p.orders[0].id==='TEST-'+(i+1))"))
    # Native backup contract: export then import in a different browser context.
    payload=page.evaluate("async()=>JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-09-16T12:00:00Z').text())")
    target=page.context.browser.new_context(service_workers='block');target.add_init_script('window.__onbShown=true');install_bootstrap(target)
    restored=target.new_page();restored.on('dialog',lambda d:d.accept());restored.goto(page.url);wait_bootstrap(restored)
    restored.evaluate("data=>importFullBackupFile(new File([JSON.stringify(data)],'TESTE.json',{type:'application/json'}))",payload)
    restored.wait_for_function("()=>S.accounts?.some(a=>a.forexAccountId==='TEST_PHASE_A')&&S.workspaceRecovery?.pending===false")
    restored.reload();wait_bootstrap(restored)
    ok('complete backup restores account operations exactly',restored.evaluate('JSON.stringify(S.forex.accountContexts)')==page.evaluate('JSON.stringify(S.forex.accountContexts)'))
    target.close()
    if page.locator('#dgBannerClose').count():page.locator('#dgBannerClose').click()
    # Field layout and keyboard jump on desktop, tablet, mobile in both themes.
    for width in (1440,768,390):
        page.set_viewport_size({'width':width,'height':1000 if width>390 else 844})
        for theme in ('light','dark'):
            page.evaluate('(theme)=>{S.theme=theme;applyTheme();}',theme)
            page.locator('[data-eb-phase-jump="0"]').click()
            bounds=page.locator('#ebPhase-0 .eb-order-row').evaluate('row=>{const r=row.getBoundingClientRect();return {width:r.width,view:innerWidth,fields:[...row.querySelectorAll("input,select,button")].map(el=>{const b=el.getBoundingClientRect();return {x:b.x,right:b.right,w:b.width,h:b.height};})}}')
            if width==390:
                ok(f'{theme} mobile fields fit without horizontal scrolling',all(x['x']>=0 and x['right']<=width+1 and x['h']>=43 for x in bounds['fields']))
            else:ok(f'{theme} {width}px order layout present',bounds['width']>0)
            # Only the current phase is expanded in evidence images.
            page.evaluate('()=>document.querySelectorAll("details[data-phase]").forEach(d=>d.open=d.dataset.phase==="0")')
            page.locator('#ebPhase-0').screenshot(path=str(out/f'{tag}-{width}-{theme}.png'))
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

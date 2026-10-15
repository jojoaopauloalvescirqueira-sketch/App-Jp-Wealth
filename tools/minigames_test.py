#!/usr/bin/env python3
"""MiniGames: real hub/game navigation, persistent board and hidden lifecycle.

Synthetic browser context only. Existing Galton numerical/backup/finalization
oracles remain in their dedicated suites; this verifies the new host contract.
"""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from playwright.sync_api import sync_playwright
from galton_board_test import prepare_page, serve
from research_navigation_test import launch_browser


def check(page):
    # Finalizar normally bootstraps its legacy epoch on first open. Establish it
    # in the synthetic fixture, then require byte-identical state and every key.
    assert page.evaluate('sessionEpochCurrent()')
    before = page.evaluate("JSON.stringify({state:S,storage:{...localStorage}})")
    children = page.evaluate("JPWNavigation.children('tools').map(x=>x.id)")
    assert children == ['tools-calendar','tools-nocuda','tools-leverage','tools-normative','tools-minigames'], ('MiniGames must be the last Tools destination', children)
    assert page.evaluate("JPWNavigation.navigate('tools-minigames')") is True
    assert page.evaluate("JPWNavigation.current().localView.view") == 'minigames'
    assert page.locator('#tools').get_by_role('heading', name='MiniGames', exact=True).is_visible()
    capture_dir=Path(tempfile.mkdtemp(prefix='test-minigames-visual-',dir=Path(__file__).resolve().parent/'.artifacts/minigames-work'))
    page.screenshot(path=str(capture_dir/'hub-desktop.png'),animations='disabled')
    assert page.locator('[data-galton-root]').count() == 0, 'catalog must not mount the game'
    opener = page.locator('#tools').get_by_role('button', name='Abrir', exact=True)
    assert opener.count() == 1
    opener.focus(); opener.press('Enter')
    page.wait_for_function("document.querySelector('[data-galton-root]')?.__galtonController?.active")
    assert page.evaluate("JPWNavigation.current().primary==='tools' && JPWNavigation.current().child==='tools-minigames' && JPWNavigation.current().localView.view==='galton'")
    assert page.locator('#tools').get_by_role('heading', name='Galton Board', exact=True).evaluate('(e)=>e===document.activeElement')
    assert page.locator('#settingsModal [data-galton-root]').count() == 0
    assert page.locator('[data-settings-panel="probability-lab"],#settingsGaltonSlot').count() == 0
    page.evaluate("""() => {
      window.__mini=document.querySelector('[data-galton-root]').__galtonController;
      __mini.root.querySelector('[data-galton-add="100"]').click();
      __mini.root.querySelector('[data-galton-action="execute"]').click();
      __mini.cancelFrame();
      for(let i=0;i<6000&&!__mini.snapshot().settledCount;i++)__mini.engine.tickFixed(1);
      __mini.root.querySelector('[data-galton-add="10"]').click();
    }""")
    prepared=page.evaluate("({snapshot:__mini.snapshot(),staged:__mini.staged})")
    assert prepared['snapshot']['settledCount'] > 0 and prepared['staged'] == 10, prepared
    for _ in range(3):
        page.locator('#tools').get_by_role('button',name='Voltar para MiniGames',exact=True).click()
        hidden=page.evaluate("""() => ({same:document.querySelector('[data-galton-root]').__galtonController===__mini,
          active:__mini.active,paused:__mini.manualPaused,raf:__mini.raf,observers:__galtonDebug.resizeObservers,
          mounts:__galtonDebug.mounts,roots:document.querySelectorAll('[data-galton-root]').length,
          snapshot:JSON.stringify(__mini.snapshot()),staged:__mini.staged})""")
        assert hidden['same'] and not hidden['active'] and hidden['paused'] and hidden['raf']==hidden['observers']==0, hidden
        assert hidden['mounts']==hidden['roots']==1 and hidden['staged']==10, hidden
        assert opener.evaluate('(e)=>e===document.activeElement')
        page.wait_for_timeout(60)
        assert page.evaluate('JSON.stringify(__mini.snapshot())')==hidden['snapshot']
        opener.press('Enter')
        assert page.evaluate("document.querySelector('[data-galton-root]').__galtonController===__mini && __mini.active && __mini.manualPaused && __mini.raf===0")
        assert page.locator('[data-galton-action="pause"]').inner_text()=='Continuar'
    for call, close in [("openSettingsModal('general')","closeSettingsModal()"),
                        ('openMvpNotesDrawer()',"document.getElementById('mvpNotesCloseBtn').click()"),
                        ('openFinalizeSessionFlow()',"document.getElementById('sessionCancel').click()")]:
        page.locator('[data-galton-action="pause"]').click()
        page.evaluate(call)
        assert page.evaluate('!__mini.active && __mini.manualPaused && __mini.raf===0 && __galtonDebug.resizeObservers===0')
        page.evaluate(close)
        assert page.evaluate('__mini.active && __mini.manualPaused && __mini.raf===0')
    after=page.evaluate("JSON.stringify({state:S,storage:{...localStorage}})")
    assert after==before, {'error':'hub/game/dialog navigation mutated financial state or storage','before':json.loads(before),'after':json.loads(after)}
    matrix=[]
    for mode in ['sidebar','topbar','glass','submenu']:
        for width in [1440,390]:
            page.set_viewport_size({'width':width,'height':900 if width==1440 else 844})
            page.evaluate('(mode)=>mountNavigationLayout(mode)',mode)
            for theme in ['dark','light']:
                page.evaluate('(theme)=>document.documentElement.dataset.theme=theme',theme)
                for zoom in [1,1.25]:
                    page.evaluate('(zoom)=>document.documentElement.style.zoom=zoom',zoom)
                    assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
                    opener.focus();opener.press('Enter')
                    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
                    facts=page.evaluate("""() => {
                      const a=document.querySelector('[data-galton-canvas]').getBoundingClientRect();
                      return {overflow:document.documentElement.scrollWidth-innerWidth,
                        left:a.left,right:a.right,width:a.width,viewport:innerWidth,
                        same:document.querySelector('[data-galton-root]').__galtonController===__mini,
                        paused:__mini.manualPaused,raf:__mini.raf,roots:document.querySelectorAll('[data-galton-root]').length};
                    }""")
                    assert facts['same'] and facts['paused'] and facts['raf']==0 and facts['roots']==1,facts
                    assert facts['overflow']<=1 and facts['width']>0 and facts['left']>=-1 and facts['right']<=facts['viewport']+1,(mode,width,theme,zoom,facts)
                    if mode=='sidebar' and width==390 and theme=='dark' and zoom==1:
                        page.screenshot(path=str(capture_dir/'galton-mobile.png'),animations='disabled')
                    matrix.append([mode,width,theme,zoom])
    page.evaluate('document.documentElement.style.zoom=1')
    assert not page.jpwealth_observed['pageerror'], page.jpwealth_observed
    return {'children':children,'mounts':page.evaluate('__galtonDebug.mounts'),'cycles':3,'dialogs':3,'presentations':len(matrix),'screenshots':str(capture_dir)}



def check_guide_from_game(page):
    cursor={'schemaVersion':1,'catalogVersion':1,'trackId':'general',
            'stepId':'general-settings-probability-lab','paused':True,'steps':{}}
    page.evaluate('(raw)=>localStorage.setItem("jpwealth_learning_guide_v1",raw)',json.dumps(cursor))
    page.reload(wait_until='load')
    from browser_bootstrap_fixture import wait_bootstrap
    wait_bootstrap(page)
    assert page.evaluate("JPWNavigation.navigate('galton-board')")
    page.evaluate('JPWLearningGuide.resume()')
    page.locator('#jpwLearningGo').wait_for(state='visible')
    page.locator('#jpwLearningGo').click()
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    facts=page.evaluate("""() => ({view:JPWNavigation.current().localView?.view,
      visible:!!document.getElementById('minigamesHub').getClientRects().length,
      guide:JPWLearningGuide.snapshot(),roots:document.querySelectorAll('[data-galton-root]').length,
      active:document.querySelector('[data-galton-root]')?.__galtonController?.active})""")
    assert facts['view']=='minigames' and facts['visible'] and not facts['active'],facts
    assert facts['guide']['stepId']=='general-settings-probability-lab' and not facts['guide']['paused'],facts
    assert facts['guide']['progress']['catalogVersion']==1 and facts['roots']==1,facts
    return {'stepId':facts['guide']['stepId'],'view':facts['view'],'catalogVersion':1}


def check_distributions(browser,url):
    from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap,assert_fixture_requests
    root=Path(__file__).resolve().parents[1]
    rows=[]
    with tempfile.TemporaryDirectory(prefix='jpw-minigames-portable-') as temp:
        detached=Path(temp)/'standalone.html'
        shutil.copyfile(root/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html',detached)
        assert list(Path(temp).iterdir())==[detached], 'portable fixture must contain only its HTML'
        for mode,target in [('modular-file',(root/'index.html').as_uri()),
                            ('portable-alone',detached.as_uri()),('pwa-offline',url)]:
            context=browser.new_context(service_workers='allow' if mode=='pwa-offline' else 'block',
                                        viewport={'width':390,'height':844},reduced_motion='reduce')
            install_bootstrap(context)
            context.add_init_script('window.__onbShown=true;')
            page=context.new_page();errors=[];sw_responses=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda response:sw_responses.append(response.url) if response.from_service_worker else None)
            try:
                page.goto(target,wait_until='load');wait_bootstrap(page)
                page.evaluate('closeModal()')
                if mode=='pwa-offline':
                    page.evaluate('navigator.serviceWorker.ready')
                    page.reload(wait_until='load');wait_bootstrap(page)
                    page.wait_for_function('navigator.serviceWorker.controller!==null')
                    sw_responses.clear();context.set_offline(True)
                    response=page.reload(wait_until='load');wait_bootstrap(page)
                    assert response.from_service_worker, 'offline HTML must come from Service Worker'
                    assert any('/src/js/' in item for item in sw_responses), ('offline classic scripts must come from SW',sw_responses)
                    assert page.evaluate('navigator.serviceWorker.controller.state')=='activated'
                    page.evaluate('closeModal()')
                financial=page.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),pref:localStorage.getItem(JPWGalton.persistence.STORAGE_KEY)})')
                assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
                assert page.locator('#minigamesHub').is_visible()
                assert page.locator('[data-galton-root]').count()==0
                page.locator('#minigamesOpenGalton').click()
                assert page.locator('#minigamesGaltonTitle').is_visible()
                assert page.evaluate("document.querySelector('[data-galton-root]').__galtonController.snapshot().running===false")
                page.locator('[data-galton-add="10"]').click()
                page.locator('[data-galton-action="execute"]').click()
                page.wait_for_function("document.querySelector('[data-galton-root]').__galtonController.snapshot().spawnedCount>0")
                page.evaluate("window.__distributionController=document.querySelector('[data-galton-root]').__galtonController")
                page.locator('#minigamesBack').click()
                hidden=page.evaluate("({snapshot:JSON.stringify(__distributionController.engine.snapshot()),active:__distributionController.active,raf:__distributionController.raf,observer:__distributionController.resizeObserverActive})")
                assert not hidden['active'] and hidden['raf']==0 and not hidden['observer'],hidden
                page.wait_for_timeout(60)
                assert page.evaluate('JSON.stringify(__distributionController.engine.snapshot())')==hidden['snapshot']
                page.locator('#minigamesOpenGalton').click()
                assert page.evaluate("document.querySelector('[data-galton-root]').__galtonController===__distributionController && __distributionController.manualPaused && !__distributionController.snapshot().running")
                assert page.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),pref:localStorage.getItem(JPWGalton.persistence.STORAGE_KEY)})')==financial
                assert not errors,errors
                assert_fixture_requests(context)
                rows.append({'mode':mode,'controllerSame':True,'motorSpawned':True,'hiddenRaf':0,'swResponses':len(sw_responses)})
                print('MINIGAMES_DISTRIBUTION_PASS '+json.dumps(rows[-1]),flush=True)
            finally:context.close()
    return rows


def run(guide_only=False,distribution_only=False):
    server,url=serve()
    try:
        with sync_playwright() as p:
            browser=launch_browser(p)
            try:
                if not distribution_only:
                    page=prepare_page(browser,url)
                    try:
                        if not guide_only: print('MINIGAMES_PASS '+json.dumps(check(page)),flush=True)
                        print('MINIGAMES_GUIDE_PASS '+json.dumps(check_guide_from_game(page)),flush=True)
                    finally: page.jpwealth_context.close()
                if not guide_only: check_distributions(browser,url)
            finally: browser.close()
    finally: server.shutdown();server.server_close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-only',action='store_true')
    parser.add_argument('--distribution-only',action='store_true')
    args=parser.parse_args()
    run(args.guide_only,args.distribution_only)

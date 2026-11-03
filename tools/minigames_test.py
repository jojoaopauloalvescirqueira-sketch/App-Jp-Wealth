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


def check_settings_host(page):
    """Real-source regression: Settings owns identity, guards and lifecycle."""
    background=page.evaluate('JPWNavigation.current()')
    assert 'tools-minigames' not in page.evaluate("JPWNavigation.children('tools').map(x=>x.id)"), 'MiniGames must leave Tools submenu'
    assert page.locator('#toolsNavSubmenu [data-nav-child="tools-minigames"]').count()==0
    assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
    assert page.evaluate('JPWNavigation.current()')==background
    assert page.locator('#settingsMenu [data-settings-category="minigames"]').count()==1
    assert page.locator('#settingsModal #minigamesHub').is_visible()
    assert page.locator('#appMain #minigamesHub').count()==0
    assert page.locator('[data-galton-root],[data-time-twins-root],[data-capital-currents-root]').count()==0
    for button,slot,root,alias,title in [
        ('minigamesOpenGalton','toolsGaltonSlot','[data-galton-root]','galton-board','minigamesGaltonTitle'),
        ('minigamesOpenTimeTwins','toolsTimeTwinsSlot','[data-time-twins-root]','time-twins','minigamesTimeTwinsTitle'),
        ('minigamesOpenCapitalCurrents','toolsCapitalCurrentsSlot','[data-capital-currents-root]','capital-currents','minigamesCapitalCurrentsTitle')]:
        page.locator('#'+button).click()
        assert page.locator('#'+title).evaluate('e=>e===document.activeElement')
        assert page.locator('#settingsModal #'+slot+' '+root).count()==1
        assert page.evaluate('JPWNavigation.current()')==background
        page.evaluate("""([slot,root])=>{const host=document.getElementById(slot);window.__host=host;window.__game=host.querySelector(root);window.__controller=__game.__galtonController||host.__timeTwinsController||host.__capitalCurrentsController;}""",[slot,root])
        assert page.evaluate("!(__controller.snapshot().running)")
        for _ in range(2):
            assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
            assert page.evaluate("!(__controller.active??__controller.snapshot().active)")
            assert page.evaluate('(alias)=>JPWNavigation.navigate(alias)',alias)
            assert page.evaluate('(root)=>__host.querySelector(root)===__game',root)
            assert page.evaluate("!(__controller.snapshot().running)")
        page.evaluate("settingsNavigate('knowledge')")
        assert page.evaluate("!(__controller.active??__controller.snapshot().active)")
        history=page.evaluate('({stack:[...settingsState.navStack],index:settingsState.navIndex})')
        page.locator('#settingsBackBtn').click()
        assert page.locator('#'+title).is_visible()
        assert page.evaluate('({stack:[...settingsState.navStack],index:settingsState.navIndex})')=={'stack':history['stack'],'index':history['index']-1}
        page.locator('#settingsForwardBtn').click()
        assert page.evaluate('settingsState.active')=='knowledge'
        assert page.evaluate('(alias)=>JPWNavigation.navigate(alias)',alias)
        page.evaluate("window.__cover=document.createElement('dialog');__cover.innerHTML='<button>Close</button>';document.body.append(__cover);__cover.showModal()")
        page.wait_for_timeout(50)
        assert page.evaluate("!(__controller.active??__controller.snapshot().active)")
        refused=page.evaluate('(alias)=>JPWNavigation.navigate(alias)',alias)
        assert refused is False
        page.evaluate('__cover.close();__cover.remove()');page.wait_for_timeout(50)
        assert page.evaluate("!(__controller.snapshot().running)")
        page.evaluate('closeSettingsModal()');page.wait_for_timeout(30)
        assert page.evaluate("!(__controller.active??__controller.snapshot().active)")
        assert page.evaluate('(alias)=>JPWNavigation.navigate(alias)',alias)
        # An observer cannot resurrect disposed instances. A new accepted entry can.
        page.evaluate('__controller.destroy();document.getElementById("settingsModal").style.setProperty("--probe","1")')
        page.wait_for_timeout(50)
        assert page.evaluate('__controller.destroyed??__controller.snapshot().destroyed')
        assert page.evaluate('(root)=>__host.querySelector(root)===__game||!__host.querySelector(root)',root)
        assert page.evaluate('(alias)=>JPWNavigation.navigate(alias)',alias)
        assert page.evaluate('(root)=>{const host=__host,game=host.querySelector(root);return (game.__galtonController||host.__timeTwinsController||host.__capitalCurrentsController)!==__controller}',root)
        assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
    page.evaluate('closeSettingsModal()')
    # Every MiniGames entry must run the execution/accounts guards before opening.
    for guard,reason in [('executionBoardUI','unsaved-operation-draft'),('accountsUI','unsaved-account-draft')]:
        page.evaluate("""guard=>{window.__originalGuardUI=JPWForex[guard];window.__guardCalls=0;JPWForex[guard]={...__originalGuardUI,guardNavigation:()=>{__guardCalls++;return false;}}}""",guard)
        before=page.evaluate('({route:JPWNavigation.current(),focus:document.activeElement.id,html:document.getElementById("settingsContent").innerHTML})')
        assert page.evaluate("JPWNavigation.navigate('time-twins')") is False
        assert page.evaluate('navLastResult.reason')==reason
        assert page.evaluate('__guardCalls')==1
        assert not page.locator('#settingsOverlay').is_visible()
        assert page.evaluate('({route:JPWNavigation.current(),focus:document.activeElement.id,html:document.getElementById("settingsContent").innerHTML})')==before
        page.evaluate('guard=>{JPWForex[guard]=__originalGuardUI}',guard)
    assert not page.jpwealth_observed['pageerror'],page.jpwealth_observed
    return {'settingsOwnsNodes':True,'games':3,'guards':2,'observerResurrection':False}


def check_real_dirty_guards(page):
    # Existing anonymous account fixture, real drafts and original refusal dialogs.
    from forex_accounts_workspace_test import SEED
    page.evaluate(SEED)
    page.locator('[data-fx-examine="CONTA-A"]').click()
    page.locator('#fxAccountFacts').evaluate("e=>e.closest('details').open=true")
    page.locator('#fxAccountFacts [name=reason]').fill('Rascunho sintético preservado')
    entries=["JPWNavigation.navigate('time-twins')","JPWNavigation.navigateLocal('tools','capital-currents')","openSettingsModal('probability-lab')"]
    for field,stay,reason in [('#fxAccountFacts [name=reason]','#fxAccountsStay','unsaved-account-draft'),('[data-p="0"][data-f="id"]','#ebLeaveStay','unsaved-operation-draft')]:
        for entry in entries:
            before=page.evaluate('({route:JPWNavigation.current(),state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),roots:document.querySelectorAll("[data-galton-root],[data-time-twins-root],[data-capital-currents-root]").length})')
            text=page.locator(field).input_value();page.locator(field).focus()
            assert page.evaluate(entry) is False,(reason,entry)
            assert page.evaluate('navLastResult.reason')==reason
            assert not page.locator('#settingsOverlay').is_visible()
            assert page.locator(stay).is_visible()
            page.locator(stay).click()
            assert page.locator(field).evaluate('e=>e===document.activeElement')
            assert page.locator(field).input_value()==text
            assert page.evaluate('({route:JPWNavigation.current(),state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),roots:document.querySelectorAll("[data-galton-root],[data-time-twins-root],[data-capital-currents-root]").length})')==before
        # Ordinary Settings can coexist with the unsaved underlying form;
        # entering MiniGames from that owner still uses the original guard.
        page.evaluate("openSettingsModal('knowledge')")
        def owned_snapshot():
            return page.evaluate('({route:JPWNavigation.current(),state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),stack:[...settingsState.navStack],index:settingsState.navIndex,active:settingsState.active,mainInert:appMain.inert,modalInert:settingsModal.inert})')
        def refuse_owned(trigger,opener):
            page.locator(opener).focus();before=owned_snapshot();text=page.locator(field).input_value()
            trigger()
            assert page.evaluate('navLastResult.reason')==reason
            assert owned_snapshot()==before
            assert page.locator(stay).is_visible()
            page.locator('#settingsBackBtn').evaluate('e=>e.focus()')
            assert page.locator(stay).evaluate('e=>e===document.activeElement'), 'native guard must own focus'
            page.locator(stay).click()
            assert page.locator(opener).evaluate('e=>e===document.activeElement')
            assert owned_snapshot()==before and page.locator(field).input_value()==text
        refuse_owned(lambda:page.evaluate("settingsNavigateToLeaf('galton-board')"),'#settingsMenu [data-settings-category="minigames"]')
        # Build history through an accepted entry and the original Discard control.
        assert page.evaluate("settingsNavigate('galton-board')") is False
        page.locator('#fxAccountsDiscard' if reason=='unsaved-account-draft' else '#ebLeaveDiscard').click()
        assert page.evaluate("settingsState.active==='galton'")
        page.evaluate("settingsNavigate('knowledge')")
        def restore_background_draft():
            # A synthetic concurrent background input exercises the real listener;
            # it neither bypasses guards nor creates an invented dirty flag.
            page.locator(field).evaluate("e=>{e.value='Rascunho sintético concorrente';e.dispatchEvent(new Event('input',{bubbles:true}));}")
            assert page.evaluate('JPWForex.'+('accountsUI' if reason=='unsaved-account-draft' else 'executionBoardUI')+'.hasDrafts()')
        restore_background_draft()
        refuse_owned(lambda:page.locator('#settingsBackBtn').click(),'#settingsBackBtn')
        page.locator('#settingsBackBtn').click()
        page.locator('#fxAccountsDiscard' if reason=='unsaved-account-draft' else '#ebLeaveDiscard').click()
        page.locator('#settingsBackBtn').click()
        assert page.evaluate("settingsState.active==='minigames'")
        restore_background_draft()
        refuse_owned(lambda:page.locator('#settingsForwardBtn').click(),'#settingsForwardBtn')
        page.evaluate('closeSettingsModal()')
        if reason=='unsaved-account-draft':
            assert page.evaluate("JPWNavigation.navigate('forex-operation')") is False
            page.locator('#fxAccountsDiscard').click()
            assert page.evaluate('operationAddDraft(0).ok')
            page.evaluate('JPWForex.executionBoardUI.render()')
            page.locator('[data-p="0"][data-f="id"]').fill('NÃO SALVO')
    return {'realAccountRefusals':6,'realExecutionRefusals':6,'entryTypes':['route alias','tools local alias','legacy Settings open','own Settings leaf','Settings Back','Settings Forward'],'draftFocusBytesHistoryAndNativeFocusPreserved':True}


def check(page):
    # Finalizar normally bootstraps its legacy epoch on first open. Establish it
    # in the synthetic fixture, then require byte-identical state and every key.
    assert page.evaluate('sessionEpochCurrent()')
    before = page.evaluate("JSON.stringify({state:S,storage:{...localStorage}})")
    children = page.evaluate("JPWNavigation.children('tools').map(x=>x.id)")
    assert children == ['tools-calendar','tools-leverage','tools-normative','tools-prop-firms'], ('MiniGames belongs to Settings', children)
    assert page.evaluate("JPWNavigation.navigate('tools-minigames')") is True
    assert page.evaluate("settingsState.active") == 'minigames'
    assert page.locator('#minigamesTitle').is_visible()
    capture_root=Path(__file__).resolve().parent/'.artifacts/minigames-work'
    capture_root.mkdir(parents=True,exist_ok=True)
    capture_dir=Path(tempfile.mkdtemp(prefix='test-minigames-visual-',dir=capture_root))
    page.screenshot(path=str(capture_dir/'hub-desktop.png'),animations='disabled')
    assert page.locator('[data-galton-root]').count() == 0, 'catalog must not mount the game'
    assert page.locator('#minigamesHub article').count() == 3
    assert page.locator('#minigamesHub').get_by_role('button',name='Abrir',exact=True).count() == 3
    assert page.locator('#minigamesHub').get_by_role('heading',name='Galton Board',exact=True).count() == 1
    assert page.locator('#minigamesTimeTwinsCard').get_by_role('heading',name='Gêmeos do Tempo',exact=True).count() == 1
    assert page.locator('#minigamesCapitalCurrentsCard').get_by_role('heading',name='Correntes de Capital',exact=True).count() == 1
    opener = page.locator('#minigamesOpenGalton')
    assert opener.count() == 1
    opener.focus(); opener.press('Enter')
    page.wait_for_function("document.querySelector('[data-galton-root]')?.__galtonController?.active")
    assert page.evaluate("JPWNavigation.current().primary==='dashboard' && settingsState.active==='galton'")
    assert page.locator('#minigamesGaltonTitle').evaluate('(e)=>e===document.activeElement')
    assert page.locator('#settingsModal [data-galton-root]').count() == 1
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
        page.locator('#minigamesGame').get_by_role('button',name='Voltar para MiniGames',exact=True).click()
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
        assert page.evaluate("JPWNavigation.navigate('galton-board')")
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
    page.locator('#jpwLearningStatus').wait_for(state='visible')
    assert 'feche' in page.locator('#jpwLearningStatus').inner_text().lower()
    page.locator('#settingsCloseBtn').click()
    page.locator('#jpwLearningGo').wait_for(state='visible')
    page.locator('#jpwLearningGo').click()
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    facts=page.evaluate("""() => ({view:settingsState.active,
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
                        if not guide_only:
                            print('MINIGAMES_SETTINGS_HOST_PASS '+json.dumps(check_settings_host(page)),flush=True)
                            page.jpwealth_context.close();page=prepare_page(browser,url)
                            print('MINIGAMES_REAL_DIRTY_GUARDS_PASS '+json.dumps(check_real_dirty_guards(page)),flush=True)
                            page.jpwealth_context.close();page=prepare_page(browser,url)
                            print('MINIGAMES_PASS '+json.dumps(check(page)),flush=True)
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

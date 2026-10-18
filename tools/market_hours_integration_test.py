#!/usr/bin/env python3
"""Real host/distribution proof with synthetic application storage only."""
import argparse, json, os, shutil, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from galton_board_test import serve, prepare_page
from research_navigation_test import launch_browser
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

ROOT=Path(__file__).resolve().parents[1]

def _inspect(page):
    lazy_requests=[]
    def observe_lazy(request):
        if request.url.split('?')[0].endswith('/aisol-globe.iife.js'):
            lazy_requests.append(request.url)
    page.on('request',observe_lazy)
    assert page.evaluate("JPWNavigation.resolve('tools-market-hours').accepted"), 'PRODUCT_FAIL: Bolsas Globais route absent'
    assert page.locator('[data-nav-child="tools-market-hours"]').count()==1, 'PRODUCT_FAIL: visible submenu entry absent'
    assert page.evaluate("!window.JPWAisolGlobeRuntime"), 'renderer executed at bootstrap'
    assert page.locator('.market-hours').count()==0
    assert page.evaluate('sessionEpochCurrent()')
    before=page.evaluate('JSON.stringify({state:S,storage:{...localStorage}})')
    # Denied navigation must not publish an entry or request the lazy resources.
    page.evaluate("window.__marketGuard=JPWForex.executionBoardUI.guardNavigation;JPWForex.executionBoardUI.guardNavigation=()=>false")
    try:
        assert not page.evaluate("JPWNavigation.navigate('tools-market-hours')")
        assert page.locator('.market-hours').count()==0 and page.evaluate('!window.JPWAisolGlobeRuntime')
    finally:page.evaluate('JPWForex.executionBoardUI.guardNavigation=window.__marketGuard')
    # Accepted programmatic entry behind a dialog waits for its original close.
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate("openSettingsModal('general')")
    assert page.evaluate("JPWNavigation.navigate('tools-market-hours')")
    page.wait_for_timeout(80)
    assert page.locator('.market-hours').count()==0 and page.evaluate('!window.JPWAisolGlobeRuntime')
    page.evaluate('closeSettingsModal()')
    page.wait_for_selector('[data-venue-id="b3"] button',state='attached',timeout=4000)
    assert page.locator('[data-mh-quick=open]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-mh-quick]').evaluate_all('(els)=>els.map(e=>e.dataset.mhQuick)')==['open','all','unknown']
    # The distribution matrix inspects all16 venues, explicitly including those currently closed.
    page.locator('[data-mh-quick=all]').click()
    # A cold mobile entry answers the list first and must not execute the renderer.
    toggle=page.locator('[data-mh="map-toggle"]')
    assert toggle.is_visible() and toggle.get_attribute('aria-expanded')=='false'
    assert page.locator('[data-mh="map-content"]').is_hidden()
    assert page.evaluate('!window.JPWAisolGlobeRuntime'), 'collapsed mobile map executed renderer'
    page.wait_for_timeout(1200)
    assert page.evaluate('!window.JPWAisolGlobeRuntime'), 'delayed renderer executed behind collapsed mobile map'
    assert not lazy_requests, ('collapsed mobile map requested renderer',lazy_requests)
    assert page.locator('.jpw-aisol-root').count()==0
    first=page.locator('[data-venue-id]:visible button').first
    assert first.is_visible()
    assert first.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0 && r.bottom<=innerHeight;}'), 'no venue name visible on first mobile screen'
    assert page.locator('[data-mh="schedules"]').get_attribute('open') is None
    assert page.locator('[data-mh="sources"]').get_attribute('open') is None
    # Approved minimalist help crosses the real host/portal boundary, including
    # distributions. It is nonmodal and must not load a collapsed mobile map.
    calendar_help=page.locator('[data-mh=info-button][data-mh-help=calendar]')
    calendar_help.click()
    assert page.locator('#jpPopoverLayer [data-mh=info-popover]').is_visible()
    assert page.locator('[data-mh=info-popover]').get_attribute('role')=='region'
    assert page.evaluate('!window.JPWAisolGlobeRuntime')
    page.keyboard.press('Escape')
    assert calendar_help.evaluate('e=>e===document.activeElement')
    toggle.click()
    page.wait_for_selector('.jpw-aisol-root canvas')
    assert toggle.get_attribute('aria-expanded')=='true'
    toggle.click()
    assert page.locator('[data-mh="map-content"]').is_hidden()
    page.set_viewport_size({'width':1440,'height':900})
    page.wait_for_selector('[data-mh="map-content"]',state='visible')
    assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
    assert page.locator('[data-venue-id]').count()==16
    assert page.evaluate("JPWNavigation.current().child==='tools-market-hours'")
    assert page.evaluate("JPWNavigation.navigate('tools-market-hours')")
    assert page.locator('#marketHoursTitle').evaluate('e=>e===document.activeElement')
    page.locator('[data-venue-id="nyse"] button').click()
    assert page.locator('[data-mh="detail-title"]').inner_text()=='NYSE'
    for opening,closing in [("openSettingsModal('general')","closeSettingsModal()"),('openMvpNotesDrawer()',"document.getElementById('mvpNotesCloseBtn').click()")]:
        calendar_help.click()
        assert page.locator('[data-mh=info-popover]').is_visible()
        page.evaluate(opening)
        page.wait_for_timeout(100)
        assert page.locator('[data-mh=info-popover]').count()==0, 'Covered tool left its help in the shared portal'
        clock=page.locator('[data-mh="clock"]').get_attribute('datetime')
        page.wait_for_timeout(1150)
        assert page.locator('[data-mh="clock"]').get_attribute('datetime')==clock, 'covered tool clock did not pause'
        page.evaluate(closing)
        page.wait_for_timeout(1150)
        assert page.locator('[data-mh="clock"]').get_attribute('datetime')!=clock, 'uncovered tool clock did not resume'
    calendar_help.click()
    assert page.evaluate("JPWNavigation.navigate('tools-minigames')")
    assert page.locator('[data-mh=info-popover]').count()==0
    clock=page.locator('[data-mh="clock"]').get_attribute('datetime')
    page.wait_for_timeout(1150)
    assert page.locator('[data-mh="clock"]').get_attribute('datetime')==clock, 'hidden tool clock did not pause'
    assert page.locator('#minigamesHub article').count()==3
    assert page.evaluate("JPWNavigation.navigateLocal('tools','market-hours')")
    assert page.locator('[data-mh="detail-title"]').inner_text()=='NYSE'
    assert page.locator('.jpw-aisol-root').count()==1
    presentations=[];reflow=[];baseline_issues=[];zoom_cases=[]
    for layout in ['sidebar','topbar','submenu','glass']:
        page.evaluate('document.documentElement.style.zoom=1;window.dispatchEvent(new Event("resize"))')
        page.set_viewport_size({'width':1440,'height':900})
        page.evaluate('(v)=>mountNavigationLayout(v)',layout)
        page.evaluate("shellSubmenu()?submenuOpenSurface(document.getElementById('toolsNavTrigger'),{focus:true}):openNavSub('tools',{focus:true})")
        entry=page.locator('[data-nav-child="tools-market-hours"]')
        assert entry.is_visible(),('Bolsas Globais submenu hidden',layout)
        entry.focus();entry.press('Enter')
        assert page.evaluate("JPWNavigation.current().child==='tools-market-hours'")
        assert entry.get_attribute('aria-current')=='page'
        page.wait_for_timeout(50)
        for width in [1440,390]:
            page.set_viewport_size({'width':width,'height':900})
            for theme in ['dark','light']:
                page.evaluate('(v)=>document.documentElement.dataset.theme=v',theme)
                for zoom in [1,1.25,2]:
                    page.evaluate('(v)=>{document.documentElement.style.zoom=v;window.dispatchEvent(new Event(\"resize\"));}',zoom)
                    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
                    assert page.locator('.market-hours').is_visible()
                    if zoom==2:
                        # CSS scaling is a stress fixture, not native browser zoom. Compare
                        # the unchanged shared shell before judging this local tool delta.
                        assert page.evaluate("JPWNavigation.navigate('dashboard')")
                        page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
                        baseline_geometry=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,header:document.querySelector("header").getBoundingClientRect().toJSON()})')
                        baseline_width=baseline_geometry['scroll']
                        assert page.evaluate("JPWNavigation.navigate('tools-market-hours')")
                        page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
                        geometry=page.locator('.market-hours').evaluate('e=>({scroll:e.scrollWidth,client:e.clientWidth,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})')
                        assert geometry['scroll']<=geometry['client']+1, (layout,width,theme,zoom,'local tool overflow',geometry)
                        assert geometry['left']>=-1 and geometry['right']<=width+1, (layout,width,theme,zoom,geometry)
                        assert page.evaluate('document.documentElement.scrollWidth')<=max(width,baseline_width)+1, (layout,width,theme,zoom,'tool worsened shared-shell overflow')
                        zoom_cases.append({'layout':layout,'width':width,'theme':theme,'cssZoom':zoom,'localResult':'PASS','sharedShellResult':'BASELINE_FAIL' if baseline_width>width+1 else 'PASS','beforeTool':baseline_geometry,'afterGlobalWidth':page.evaluate('document.documentElement.scrollWidth'),'tool':geometry})
                        if baseline_width>width+1:
                            baseline_issues.append({'result':'BASELINE_FAIL','layout':layout,'width':width,'theme':theme,'cssZoom':zoom,'sharedBeforeToolWidth':baseline_width,'tool':geometry})
                    else:
                        # Preserve original strict global oracles at 100% and 125%.
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (layout,width,theme,zoom)
                    presentations.append([layout,width,theme,zoom])
        # Equivalent 1440px/200% layout viewport; CSS zoom alone does not alter media queries.
        # This proves responsive reflow, not native browser-zoom activation.
        page.evaluate('document.documentElement.style.zoom=1;window.dispatchEvent(new Event("resize"))')
        page.set_viewport_size({'width':720,'height':900})
        for theme in ['dark','light']:
            page.evaluate('(v)=>document.documentElement.dataset.theme=v',theme)
            page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            assert page.locator('[data-mh="map-toggle"]').is_visible()
            assert page.locator('[data-mh="map-toggle"]').get_attribute('aria-expanded')=='false'
            assert page.locator('[data-mh="map-content"]').is_hidden()
            assert page.locator('[data-venue-id]:visible').count()==16
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), ('200%-equivalent reflow',layout,theme)
            reflow.append([layout,720,theme])
    page.evaluate('document.documentElement.style.zoom=1')
    assert page.evaluate('JSON.stringify({state:S,storage:{...localStorage}})')==before, 'financial state or local preferences changed'
    page.evaluate('sessionResetAuxiliarySurfaces()')
    assert page.locator('.market-hours').count()==0
    page.evaluate("JPWNavigation.navigate('dashboard');JPWNavigation.navigate('tools-market-hours')")
    page.wait_for_timeout(100)
    assert page.locator('.market-hours').count()==0, 'finalized controller resurrected'
    page.remove_listener('request',observe_lazy)
    return {'venues':16,'mobileColdMapLazy':True,'mobileFirstNameVisible':True,'presentations':len(presentations),'equivalent200Reflow':len(reflow),'nativeZoom':'NOT_RUN','sharedShellBaselineIssues':baseline_issues,'css200Cases':zoom_cases,'financialStateUnchanged':True,'singleInstance':True,'finalized':True}

def inspect(page, output):
    try:
        return _inspect(page)
    except Exception:
        page.screenshot(path=str(output/'failure.png'),full_page=True)
        geometry=page.evaluate("""()=>({viewport:{width:innerWidth,height:innerHeight,zoom:document.documentElement.style.zoom,visual:visualViewport?{scale:visualViewport.scale,x:visualViewport.offsetLeft,y:visualViewport.offsetTop}:null},scrollWidth:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('body *')].map(e=>({e,r:e.getBoundingClientRect()})).filter(({e,r})=>r.width>0&&(r.left< -1||r.right>innerWidth+1)&&getComputedStyle(e).position!=='fixed').slice(0,60).map(({e,r})=>({tag:e.tagName,id:e.id,cls:String(e.className),left:r.left,right:r.right,width:r.width}))})""")
        (output/'failure-geometry.json').write_text(json.dumps(geometry,ensure_ascii=False,indent=2)+'\n')
        raise

def run(args):
    output=ROOT/args.out_dir;output.mkdir(parents=True,exist_ok=True)
    result={'status':'PRODUCT_FAIL','modes':[]};server,url=serve()
    try:
        with sync_playwright() as p:
            browser=launch_browser(p)
            try:
                if not args.distributions:
                    page=prepare_page(browser,url)
                    try:
                        result['modes'].append({'mode':'http',**inspect(page,output)})
                        assert not page.jpwealth_observed['pageerror'],page.jpwealth_observed['pageerror']
                    finally:page.jpwealth_context.close()
                else:
                    with tempfile.TemporaryDirectory(prefix='jpw-markets-portable-') as temp:
                        portable=Path(temp)/'JPWealth.html';shutil.copyfile(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html',portable)
                        for mode,target in [('modular-file',(ROOT/'index.html').as_uri()),('portable-alone',portable.as_uri()),('pwa-offline',url)]:
                            context=browser.new_context(viewport={'width':1440,'height':900},service_workers='allow' if mode=='pwa-offline' else 'block',reduced_motion='reduce')
                            install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
                            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                            try:
                                page.goto(target,wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()')
                                if mode=='pwa-offline':
                                    page.evaluate('navigator.serviceWorker.ready');page.reload(wait_until='load');wait_bootstrap(page)
                                    page.wait_for_function('!!navigator.serviceWorker.controller');context.set_offline(True)
                                    response=page.reload(wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()')
                                    assert response.from_service_worker
                                result['modes'].append({'mode':mode,**inspect(page,output)})
                                assert not errors,errors
                            finally:context.close()
                result['status']='PASS'
            finally:browser.close()
    except Exception as error:
        result['error']=str(error)
    finally:
        server.shutdown();server.server_close()
        (output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out-dir',default='tools/.artifacts/market-hours/integration');parser.add_argument('--distributions',action='store_true')
    raise SystemExit(run(parser.parse_args()))

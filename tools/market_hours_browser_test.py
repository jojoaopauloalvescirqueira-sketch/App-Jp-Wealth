#!/usr/bin/env python3
"""Real browser proof: broken identity mapping, remount/ticks, stale lifecycle and fallback must fail.
Only the future asset loader boundary is supplied by this offline fixture.
"""
import argparse, hashlib, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def catalog():
    start=1792065600000  # 2026-10-15 12:00 UTC
    specs=[('b3','B3','São Paulo',-23.55,-46.63),('nyse','NYSE','New York',40.71,-74),('nasdaq','Nasdaq','New York',40.71,-74),('nse','NSE','Mumbai',19.08,72.88),('bse','BSE','Mumbai',19.08,72.88)]
    venues=[]
    for id,name,city,lat,lng in specs:
        coverage=dict(fromUtc=start-86400000,untilUtc=start+86400000,verifiedAt='2026-10-15',sourceIds=['official'])
        groups=[dict(id='equities',label='Ações',coverage=coverage,periods=[dict(startUtc=start-86400000,endUtc=start+2000,phase='continuous',reason='Sessão regular de teste'),dict(startUtc=start+2000,endUtc=start+86400000,phase='closed',reason='Fechamento do calendário de teste')])]
        venues.append(dict(id=id,name=name,city=city,country='Teste',region='Américas' if id in ['b3','nyse','nasdaq'] else 'Ásia',timeZone='UTC',lat=lat,lng=lng,groups=groups))
    return dict(schemaVersion=1,tzdbVersion='fixture-UTC',sources=[dict(id='official',title='Fonte oficial sintética',url='https://www.b3.com.br/',publishedAt=None,verifiedAt='2026-10-15')],venues=venues)

def recovery(page, result):
    failures=[]
    def check(name, fn):
        page.reload()
        try:
            fn()
            result['checks'].append(name)
        except Exception as exc:
            failures.append(name+': '+str(exc))
    def focus():
        page.evaluate('JPWMarketHoursAssets.getRenderer=()=>Promise.reject(Error("offline"));JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_selector('[data-venue-id="nasdaq"] button')
        page.locator('[data-venue-id="nasdaq"] button').click()
        city=page.locator('[data-mh="city-venues"] button').filter(has_text='NYSE')
        city.focus();page.evaluate('window.__city=document.activeElement');city.press('Enter')
        assert page.evaluate('__city.isConnected && document.activeElement===__city'), 'city Enter removed focused button'
        page.evaluate('__now+=3000');page.wait_for_timeout(1100)
        assert page.locator('[data-venue-id="nyse"]').get_attribute('data-phase')=='closed'
        assert page.evaluate('__city.isConnected && document.activeElement===__city'), 'phase transition removed focused city button'
    check('city Enter and calendar transition retain the same focused button',focus)
    def filtered_tick_focus():
        page.evaluate('JPWMarketHoursAssets.getRenderer=()=>Promise.reject(Error("offline"));JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_selector('[data-venue-id="b3"] button')
        page.locator('[data-mh="phase-options"] summary').click();phase_filter=page.locator('[data-mh="filter"]');phase_filter.select_option('continuous')
        page.locator('[data-venue-id="b3"] button').focus()
        page.evaluate('__now+=3000');page.wait_for_timeout(1100)
        assert page.locator('[data-venue-id="b3"]').get_attribute('data-phase')=='closed'
        assert page.locator('[data-venue-id="b3"]').is_hidden()
        assert page.locator('[data-mh="search"]').evaluate('e=>e===document.activeElement && e.isConnected && !!e.getClientRects().length'), 'phase tick hid focused row without moving focus to search'
        assert phase_filter.input_value()=='continuous'
        assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
    check('calendar transition hiding focused row transfers focus to search and preserves phase filter/selection',filtered_tick_focus)
    def source_tick_focus():
        page.evaluate('JPWMarketHoursAssets.getRenderer=()=>Promise.reject(Error("offline"));JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_selector('[data-venue-id="b3"] button')
        page.locator('[data-mh="sources"] summary').click();source=page.locator('.mh-group a').first;source.focus()
        old_href=source.get_attribute('href');old_text=source.inner_text()
        page.evaluate('__now+=3000');page.wait_for_timeout(1100)
        assert page.locator('[data-venue-id="b3"]').get_attribute('data-phase')=='closed'
        assert source.evaluate('e=>e===document.activeElement && e.isConnected && !!e.getClientRects().length'), 'phase tick discarded focused source link'
        assert source.get_attribute('href')==old_href and source.inner_text()==old_text
        assert page.locator('[data-mh="filter"]').input_value()=='all'
        assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
    check('calendar transition restores focused equivalent source link without moving focus to another control',source_tick_focus)
    def catalog_retry():
        page.evaluate('window.__calls=0;JPWMarketHoursAssets.getCatalog=()=>{__calls++;return __calls===1?Promise.reject(Error("transient catalog failure")):Promise.resolve(__catalog)};void 0')
        assert page.evaluate('JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"))') is False
        page.evaluate('JPWMarketHours.activate()');page.wait_for_timeout(1100)
        assert page.evaluate('__calls')==1, 'catalog auto-retried after error'
        retry=page.locator('[data-mh="catalog-retry"]')
        assert retry.count()==1 and retry.is_visible(), 'catalog error offers no retry button'
        retry.focus();retry.press('Enter');page.wait_for_selector('[data-venue-id="b3"] button')
        assert page.evaluate('__calls')==2
        assert page.evaluate('JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"))') is True
        assert page.evaluate('__calls')==2 and page.locator('.market-hours').count()==1
        assert page.locator('[data-venue-id="b3"] button').evaluate('e=>e===document.activeElement'), 'catalog retry loses keyboard position'
    check('catalog error stays stable; semantic keyboard retry recovers once; healthy mount idempotent',catalog_retry)
    def renderer_retry():
        page.evaluate('window.__calls=0;JPWMarketHoursAssets.getRenderer=()=>{__calls++;return __calls===1?Promise.reject(Error("transient renderer failure")):Promise.resolve(JPWAisolGlobeRuntime)};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_selector('[data-venue-id="b3"] button');page.wait_for_timeout(1100)
        page.locator('[data-venue-id="nasdaq"] button').click()
        assert page.evaluate('__calls')==1, 'renderer auto-retried after error'
        retry=page.locator('[data-mh="renderer-retry"]')
        assert retry.count()==1 and retry.is_visible(), 'renderer error offers no retry button'
        retry.focus();retry.press('Enter');page.wait_for_selector('.jpw-aisol-root canvas')
        assert page.evaluate('__calls')==2 and page.locator('[data-venue-id]').count()==5
        assert page.locator('[data-mh="detail-title"]').inner_text()=='Nasdaq'
        assert page.locator('[data-venue-id="nasdaq"] button').evaluate('e=>e===document.activeElement'), 'renderer retry loses keyboard position'
    check('renderer error preserves table/selection; explicit keyboard retry recovers once',renderer_retry)
    def hidden_renderer_retry(mode):
        page.evaluate('window.__calls=0;JPWMarketHoursAssets.getRenderer=()=>{__calls++;return __calls===1?Promise.reject(Error("transient renderer failure")):Promise.resolve(JPWAisolGlobeRuntime)};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        retry=page.locator('[data-mh="renderer-retry"]');retry.wait_for(state='visible')
        search=page.locator('[data-mh="search"]');phase_filter=page.locator('[data-mh="filter"]')
        if mode=='search':
            search.fill('New York')
        else:
            page.locator('[data-mh="phase-options"] summary').click();phase_filter.select_option('closed')
        old_search=search.input_value();old_filter=phase_filter.input_value()
        assert page.locator('[data-venue-id="b3"]').is_hidden()
        retry.focus();retry.press('Enter');page.wait_for_selector('.jpw-aisol-root canvas')
        assert search.evaluate('e=>e===document.activeElement && e.isConnected && !e.closest("[hidden],[inert]")'), 'retry lost focus when selected row was hidden by '+mode
        assert search.input_value()==old_search and phase_filter.input_value()==old_filter, 'retry changed search/filter'
        assert page.locator('[data-venue-id="b3"]').is_hidden()
        assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
        assert page.locator('[data-venue-id="b3"] button').get_attribute('aria-pressed')=='true'
        assert page.evaluate('__calls')==2
    check('renderer retry with selected row excluded by search focuses visible search without changing state',lambda:hidden_renderer_retry('search'))
    check('renderer retry with selected row excluded by phase filter focuses visible search without changing state',lambda:hidden_renderer_retry('filter'))
    def renderer_cancel():
        page.evaluate('window.__calls=0;window.__signals=[];JPWMarketHoursAssets.getRenderer=({signal}={})=>{__calls++;__signals.push(signal);return __calls===1?new Promise((r,j)=>{window.__lateRenderer=r;signal?.addEventListener("abort",()=>j(new DOMException("cancelled","AbortError"))) }):Promise.resolve(JPWAisolGlobeRuntime)};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_function('typeof __lateRenderer==="function"')
        page.evaluate('JPWMarketHours.deactivate()')
        assert page.evaluate('!!__signals[0] && __signals[0].aborted'), 'deactivate did not abort renderer consumer'
        page.evaluate('__lateRenderer(JPWAisolGlobeRuntime)');page.wait_for_timeout(50)
        assert page.locator('.jpw-aisol-root').count()==0, 'late renderer ran while inactive'
        page.evaluate('JPWMarketHours.activate()');page.wait_for_selector('.jpw-aisol-root canvas')
        assert page.evaluate('__calls')==2
    check('deactivate aborts renderer consumer; ignores stale return; activation retries cancelled work',renderer_cancel)
    def catalog_cancel():
        page.evaluate('window.__calls=0;window.__signals=[];JPWMarketHoursAssets.getCatalog=({signal}={})=>{__calls++;__signals.push(signal);return __calls===1?new Promise(r=>window.__lateCatalog=r):Promise.resolve(__catalog)};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
        page.wait_for_function('typeof __lateCatalog==="function"')
        page.evaluate('document.querySelector("#toolsMarketHoursSlot").hidden=true');page.wait_for_timeout(50)
        assert page.evaluate('!!__signals[0] && __signals[0].aborted'), 'hidden host did not abort catalog consumer'
        page.evaluate('__lateCatalog(__catalog)');page.wait_for_timeout(50)
        assert page.locator('[data-venue-id]').count()==0, 'late catalog mounted hidden host'
        page.evaluate('document.querySelector("#toolsMarketHoursSlot").hidden=false;JPWMarketHours.activate()')
        page.wait_for_selector('[data-venue-id="b3"] button')
        assert page.evaluate('__calls')==2
    check('hidden exit aborts catalog; stale return never mounts; reentry recovers',catalog_cancel)
    def disposal(kind):
        page.evaluate('(kind)=>{window.__signal=null;JPWMarketHoursAssets[kind]=({signal}={})=>{__signal=signal;return new Promise((r,j)=>{window.__late=r;signal?.addEventListener("abort",()=>j(new DOMException("cancelled","AbortError")))})};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()}',kind)
        page.wait_for_function('typeof __late==="function"')
        page.evaluate('JPWMarketHours.dispose()')
        assert page.evaluate('!!__signal && __signal.aborted'), kind+' consumer not aborted by dispose'
        page.evaluate('(kind)=>{__late(kind==="getCatalog"?__catalog:JPWAisolGlobeRuntime);JPWMarketHours.activate();JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"))}',kind)
        page.wait_for_timeout(100)
        assert page.locator('.market-hours').count()==0 and page.locator('.jpw-aisol-root').count()==0, 'disposed controller resurrected'
    check('dispose aborts catalog and stays terminal',lambda:disposal('getCatalog'))
    check('dispose aborts renderer and stays terminal',lambda:disposal('getRenderer'))
    result['failures']=failures
    assert not failures, '; '.join(failures)

def run(args):
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    scripts=['src/js/40-app/31-market-hours/01-sessions.js','src/vendor/aisol-dot-globe/aisol-globe.iife.js','src/js/40-app/31-market-hours/03-view.js','src/js/40-app/31-market-hours/04-controller.js']
    fixture=out/'interaction-fixture.html'
    fixture.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="'+(ROOT/'src/styles/app.css').as_uri()+'"></head><body><main id="fixture" style="grid-area:main;padding:16px;min-width:0"><div id="toolsMarketHoursSlot"></div></main>'+''.join('<script src="'+(ROOT/p).as_uri()+'"></script>' for p in scripts)+'<script>window.__now=1792065600000;Date.now=()=>__now;window.__catalog='+json.dumps(catalog())+';window.__rendererUpdates=[];window.__createOptions=[];window.JPWMarketHoursAssets={getCatalog:()=>Promise.resolve(__catalog),getRenderer:()=>Promise.resolve({create:(h,o)=>{__createOptions.push(o);const real=JPWAisolGlobeRuntime.create(h,o);return {...real,update:v=>{__rendererUpdates.push(v);return real.update(v)}}}})};</script></body></html>')
    result={'status':'PRODUCT_FAIL','checks':[],'errors':[],'screenshots':[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce',service_workers='block');ctx.set_offline(True)
        page=ctx.new_page();page.on('pageerror',lambda e:result['errors'].append(str(e)))
        try:
            page.goto(fixture.as_uri())
            if args.case=='recovery':
                recovery(page,result)
            else:
                assert page.evaluate('!!window.JPWMarketHours && typeof JPWMarketHours.mount==="function"'), 'PRODUCT_FAIL: market hours controller absent'
                page.evaluate('JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                page.wait_for_selector('[data-venue-id="b3"] button')
                assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
                assert 'Aberta' in page.locator('[data-venue-id="b3"]').inner_text()
                assert page.locator('[data-mh-quick=open]').get_attribute('aria-pressed')=='true'
                page.locator('[data-mh-quick=all]').click()
                page.wait_for_selector('.jpw-aisol-root canvas');page.wait_for_timeout(100)
                page.locator('[data-venue-id="nyse"] button').click()
                assert page.locator('[data-mh="detail-title"]').inner_text()=='NYSE'
                page.locator('[data-venue-id="b3"] button').click()
                assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
                assert page.locator('[data-venue-id="b3"] button').evaluate('e=>e===document.activeElement')
                assert page.evaluate('__createOptions[0].motion.autoRotate===false && __createOptions[0].look.arcs===false && __createOptions[0].declutterLabels===true')
                initial_updates=page.evaluate('__rendererUpdates.length')
                page.wait_for_timeout(1100)
                assert page.evaluate('__rendererUpdates.length')==initial_updates, 'idle clock tick rebuilt renderer markers'
                # Real pointer hit-test uses projected marker center, not an invoked callback.
                page.locator('[data-venue-id="nyse"] button').click();page.wait_for_timeout(100)
                pos=page.locator('[data-marker-id="city-sao-paulo"]').evaluate('e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top),visible:getComputedStyle(e).opacity})')
                rootbox=page.locator('.jpw-aisol-root').bounding_box()
                page.mouse.click(rootbox['x']+pos['x'],rootbox['y']+pos['y'])
                assert page.locator('[data-mh="detail-title"]').inner_text()=='B3', 'real B3 pin failed to change NYSE selection'
                result['checks'].append('B3 initial; real table selection and pointer marker selection')
                page.locator('[data-venue-id="nasdaq"] button').click()
                assert page.locator('[data-mh="city-venues"] button').count()==2
                page.locator('[data-mh="city-venues"] button').filter(has_text='NYSE').click()
                assert page.locator('[data-mh="detail-title"]').inner_text()=='NYSE'
                page.locator('[data-venue-id="nse"] button').click()
                assert page.locator('[data-mh="city-venues"] button').count()==2
                result['checks'].append('New York and Mumbai use distinct city/venue identities')
                search=page.locator('[data-mh="search"]');search.fill('zzzz-no-result')
                assert page.locator('[data-mh="empty"]').is_visible()
                search.fill('');search.focus()
                page.evaluate('document.querySelector(".mh-table-wrap").scrollTop=45;window.__scroll=document.querySelector(".mh-table-wrap").scrollTop')
                page.evaluate('window.__row=document.querySelector("[data-venue-id=b3]");window.__now+=3000')
                page.wait_for_timeout(1100)
                assert 'Fechada' in page.locator('[data-venue-id="b3"]').inner_text()
                assert search.evaluate('e=>e===document.activeElement')
                assert page.evaluate('__row===document.querySelector("[data-venue-id=b3]")')
                assert page.evaluate('document.querySelector(".mh-table-wrap").scrollTop===__scroll')
                assert page.evaluate('__rendererUpdates.at(-1).markers.every(m=>m.phase==="closed")'), 'table/marker phase diverged'
                page.locator('[data-mh="phase-options"] summary').click()
                page.locator('[data-mh="filter"]').select_option('continuous')
                assert page.locator('[data-mh="empty"]').is_visible()
                page.locator('[data-mh="filter"]').select_option('all')
                result['checks'].append('filter empty state; real calendar boundary updates existing rows without focus loss')
                # Lifecycle stops clocks; reactivation catches up instead of resuming market time.
                page.evaluate('JPWMarketHours.deactivate();window.__before=document.querySelector("[data-mh=clock]").textContent;__now+=60000')
                page.wait_for_timeout(1100);assert page.locator('[data-mh="clock"]').inner_text()==page.evaluate('__before')
                page.evaluate('JPWMarketHours.activate()');assert page.locator('[data-mh="clock"]').inner_text()!=page.evaluate('__before')
                assert page.locator('.jpw-aisol-root').count()==1
                page.evaluate('document.querySelector("#toolsMarketHoursSlot").hidden=true;window.__before=document.querySelector("[data-mh=clock]").textContent;__now+=60000')
                page.wait_for_timeout(1100)
                assert page.locator('[data-mh="clock"]').inner_text()==page.evaluate('__before')
                page.evaluate('document.querySelector("#toolsMarketHoursSlot").hidden=false')
                page.wait_for_timeout(80)
                assert page.locator('[data-mh="clock"]').inner_text()!=page.evaluate('__before')
                result['checks'].append('one mount; inactive/hidden clock stops; activation uses current instant; no idle renderer updates')
                for layout in ['sidebar','topbar','submenu','glass']:
                    page.evaluate('(v)=>document.documentElement.dataset.navigation=v',layout)
                    for theme in ['light','dark']:
                        page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
                        page.wait_for_timeout(80)
                        assert page.locator('.market-hours').bounding_box()['width']>600, 'desktop fixture/content collapsed'
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'desktop horizontal overflow'
                        # Approved macOS composition: consultation list left, wider inspector right.
                        # Compare actual host geometry, independent of a chosen CSS percentage.
                        box=page.locator('.mh-aside').bounding_box();listbox=page.locator('.mh-list').bounding_box()
                        assert listbox['x']+listbox['width']<=box['x']+1, 'desktop list must precede inspector'
                        assert box['width']>listbox['width']>0, 'desktop inspector must be wider than the list'
                        shot=out/('desktop-'+layout+'-'+theme+'.png');page.screenshot(path=str(shot));result['screenshots'].append(str(shot))
                result['checks'].append('four layout attributes in both themes; list left and wider selected inspector; mobile maximum text scale without horizontal overflow')
                page.set_viewport_size({'width':390,'height':844});page.evaluate('document.documentElement.dataset.fs="2"')
                page.wait_for_timeout(100)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'mobile page horizontal overflow'
                shot=out/'mobile-zoom.png';page.screenshot(path=str(shot),full_page=True);result['screenshots'].append(str(shot))
                page.set_viewport_size({'width':1280,'height':900})
                # Terminal disposal, including a renderer resolving after dispose.
                page.evaluate('JPWMarketHours.dispose();JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                assert page.locator('.jpw-aisol-root').count()==0 and page.locator('[data-venue-id]').count()==0
                page.reload();page.evaluate('JPWMarketHoursAssets.getRenderer=()=>Promise.reject(Error("offline renderer failure"));JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                page.wait_for_selector('[data-venue-id="b3"] button');page.locator('[data-venue-id="nyse"] button').click()
                assert page.locator('[data-mh="detail-title"]').inner_text()=='NYSE'
                assert page.locator('[data-mh="globe-status"]').is_visible()
                page.reload()
                page.evaluate('const realContext=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...a){return kind==="webgl2"?null:realContext.call(this,kind,...a)};JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                page.wait_for_selector('.jpw-aisol-root[data-state="fallback"]')
                assert page.locator('[data-mh="globe-status"]').is_visible(), 'renderer failure message was hidden after synchronous fallback'
                page.locator('[data-venue-id="nasdaq"] button').click()
                assert page.locator('[data-mh="detail-title"]').inner_text()=='Nasdaq'
                page.reload()
                page.evaluate('JPWMarketHoursAssets.getRenderer=()=>new Promise(r=>window.__lateRenderer=r);JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                page.wait_for_function('typeof __lateRenderer==="function"')
                page.evaluate('JPWMarketHours.dispose();__lateRenderer(JPWAisolGlobeRuntime)')
                page.wait_for_timeout(100)
                assert page.locator('.jpw-aisol-root').count()==0 and page.locator('[data-venue-id]').count()==0
                page.reload()
                page.evaluate('JPWMarketHoursAssets.getCatalog=()=>new Promise(r=>window.__lateCatalog=r);JPWMarketHours.mount(document.querySelector("#toolsMarketHoursSlot"));JPWMarketHours.activate()')
                page.wait_for_function('typeof __lateCatalog==="function"')
                page.evaluate('JPWMarketHours.dispose();__lateCatalog(__catalog)')
                page.wait_for_timeout(100)
                assert page.locator('.jpw-aisol-root').count()==0 and page.locator('[data-venue-id]').count()==0
                result['checks'].append('dispose terminal; pending catalog/renderer canceled; loader/render failure preserves functional table')
            assert not result['errors'],result['errors']
            result['status']='PASS';result['browser']=browser.version
        except Exception as exc:
            result['failure']=str(exc)
            result['viewport_diagnostics']=page.evaluate('''()=>({viewport:{width:innerWidth,height:innerHeight,scale:visualViewport?.scale,offsetTop:visualViewport?.offsetTop},scroll:{x:scrollX,y:scrollY},table:Array.from(document.querySelectorAll(".mh-table-wrap")).map(e=>({rect:e.getBoundingClientRect().toJSON(),scrollTop:e.scrollTop})),nyse:Array.from(document.querySelectorAll("[data-venue-id=nyse] button")).map(e=>({rect:e.getBoundingClientRect().toJSON(),focused:e===document.activeElement}))})''')
            page.screenshot(path=str(out/'failure.png'),full_page=True)
        finally:
            ctx.close();browser.close()
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in scripts+['src/styles/app.css','tools/market_hours_browser_test.py']}
    (out/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['interaction','recovery'],default='interaction');ap.add_argument('--out-dir',default='tools/.artifacts/market-hours/interaction');raise SystemExit(run(ap.parse_args()))

#!/usr/bin/env python3
"""Consultation-first DOM/lifecycle proof against current source, with synthetic assets."""
import argparse, copy, hashlib, json, os, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from market_hours_browser_test import catalog
ROOT = Path(__file__).resolve().parents[1]
START = 1792065600000
SOURCES = ['src/js/40-app/31-market-hours/01-sessions.js', 'src/js/40-app/31-market-hours/03-view.js', 'src/js/40-app/31-market-hours/04-controller.js', 'src/styles/app.css']

def fixture_catalog():
    data = catalog()
    for v in data['venues']:
        v['groups'][0]['periods'][0]['endUtc'] = START + 60000
        v['groups'][0]['periods'][1]['startUtc'] = START + 60000
    # Known partial opening is open; an unknown segment must not be counted.
    for ident, phase in [('nyse', 'break'), ('nasdaq', 'unknown')]:
        v = next(v for v in data['venues'] if v['id'] == ident)
        group = copy.deepcopy(v['groups'][0]);group.update(id='secondary', label='Segundo segmento')
        group['periods'][0]['phase'] = phase
        v['groups'].append(group)
    data['venues'][3]['groups'][0]['periods'][0]['phase'] = 'auction'
    data['venues'][4]['groups'][0]['periods'][0]['phase'] = 'closed'
    # Continuous -> break must never promise a close.
    data['venues'][0]['groups'][0]['periods'][1]['phase'] = 'break'
    data['venues'][0]['groups'][0]['periods'][0]['transitionWindow'] = dict(earliestUtc=START+50000,latestUtc=START+60000,nextPhase='break')
    return data

def run(args):
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    fixture=out/'fixture.html'
    fixture.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="'+(ROOT/SOURCES[-1]).as_uri()+'"></head><body><main style="grid-area:main;padding:16px;min-width:0"><div id="slot"></div></main>'+''.join('<script src="'+(ROOT/p).as_uri()+'"></script>' for p in SOURCES[:-1])+'''<script>
    window.__now=1792065600000;Date.now=()=>__now;
    window.__catalog='''+json.dumps(fixture_catalog())+''';
    window.__creates=0;window.__loads=0;window.__disposed=0;window.__active=[];window.__signals=[];
    window.__factory={create(h,o){__creates++;window.__options=o;const e=document.createElement('div');e.className='fixture-renderer';h.append(e);return {update(v){window.__markers=v.markers},focusMarker(){},focusLocation(){},setActive(v){__active.push(v)},dispose(){__disposed++;e.remove()}}}};
    window.JPWMarketHoursAssets={getCatalog:()=>Promise.resolve(__catalog),getRenderer:({signal})=>{__loads++;__signals.push(signal);return Promise.resolve(__factory)}};
    window.__finance={accounts:[{balance:1234.5}],backupVersion:4};window.S=__finance;window.__beforeFinance=JSON.stringify(S);
    window.__mount=()=>{JPWMarketHours.mount(document.querySelector('#slot'));JPWMarketHours.activate()};
    </script></body></html>''')
    result={'status':'PRODUCT_FAIL','checks':[],'failures':[],'errors':[],'screenshots':[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
        context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce',service_workers='block')
        context.set_offline(True);page=context.new_page();page.set_default_timeout(2500)
        page.on('pageerror',lambda error:result['errors'].append(str(error)))
        def boot(mobile=False, before=None):
            page.set_viewport_size({'width':390 if mobile else 1280,'height':844 if mobile else 900})
            page.goto(fixture.as_uri())
            if before:page.evaluate("()=>{"+before+"}")
            page.evaluate('__mount()');page.wait_for_selector('[data-venue-id="b3"] button',state='attached')
        def check(name, fn):
            if args.only and args.only not in name:return
            try:fn();result['checks'].append(name)
            except Exception as exc:
                result['failures'].append(name+': '+traceback.format_exc());page.screenshot(path=str(out/('failure-'+str(len(result['failures']))+'.png')),full_page=True)
        def grouping():
            boot()
            assert page.locator('[data-mh=summary]').inner_text()=='2 bolsas abertas agora'
            # Approved minimalist presentation moves the calendar explanation
            # into a dedicated help balloon; regular-open facts stay visible.
            assert page.locator('[data-mh=info-button][data-mh-help=calendar]').count()==1
            assert page.get_by_text('Pelo calendário de ações',exact=True).count()==0
            assert page.locator('[data-mh-quick=all]').inner_text()=='Todas 5'
            assert page.locator('[data-mh-quick=open]').inner_text()=='Abertas 2'
            assert page.locator('[data-mh-quick=unknown]').inner_text()=='Sem confirmação 1'
            # The new approved default is Open; exercise whole-catalog grouping explicitly.
            assert page.locator('[data-mh-quick=open]').get_attribute('aria-pressed')=='true'
            page.locator('[data-mh-quick=all]').click()
            assert page.locator('[data-venue-id=nyse]').inner_text().count('Parcialmente aberta')==1
            assert 'Sem confirmação' in page.locator('[data-venue-id=nasdaq]').inner_text()
            assert page.locator('[data-venue-id]').evaluate_all('(els)=>els.map(e=>e.dataset.venueId)')==['b3','nyse','nse','bse','nasdaq']
            assert page.locator('[data-venue-id] .mh-local').all_text_contents()==['12:00']*5
            page.locator('[data-mh-quick=open]').focus();page.locator('[data-mh-quick=open]').press('Enter')
            assert page.locator('[data-venue-id]:visible').count()==2
            page.locator('[data-mh-quick=unknown]').click()
            assert page.locator('[data-venue-id]:visible').evaluate_all('(els)=>els.map(e=>e.dataset.venueId)')==['nasdaq']
        check('literal counts, grouping, mixed known/unknown, local HH:mm and quickfilters',grouping)
        def excluded():
            boot();page.locator('[data-mh=search]').fill('Mumbai')
            assert page.locator('[data-mh=detail-title]').inner_text()=='B3'
            assert page.locator('[data-mh=selection-outside]').is_visible()
            page.locator('[data-mh=phase-options] summary').click();page.locator('[data-mh=filter]').select_option('closed')
            page.locator('[data-mh=show-selected]').click()
            assert page.locator('[data-venue-id=b3]').is_visible()
            assert page.locator('[data-mh=search]').input_value()=='' and page.locator('[data-mh=filter]').input_value()=='all'
            assert page.locator('[data-mh-quick=all]').get_attribute('aria-pressed')=='true'
            assert page.locator('[data-venue-id=b3] button').evaluate('e=>e===document.activeElement')
        check('B3 remains selected outside filters; explicit reveal resets filters and focuses row',excluded)
        def evidence():
            boot()
            assert page.locator('[data-mh=schedules]').count()==1 and not page.locator('[data-mh=schedules]').evaluate('e=>e.open')
            assert page.locator('[data-mh=sources]').count()==1 and not page.locator('[data-mh=sources]').evaluate('e=>e.open')
            assert 'Intervalo' in page.locator('[data-mh=next-transition]').inner_text()
            assert 'Janela' in page.locator('[data-mh=next-transition]').inner_text()
            assert 'Fecha' not in page.locator('[data-mh=next-transition]').inner_text()
            assert page.locator('[data-mh=clock]').get_attribute('datetime')=='2026-10-15T12:00:00.000Z'
            assert 'revis' not in page.locator('[data-mh=clock]').inner_text().lower()
            page.locator('[data-mh=sources] summary').click()
            assert 'Revisão da fonte: 2026-10-15' in page.locator('[data-mh=sources]').inner_text()
            assert page.locator('[data-mh=sources] a').count()==1
            page.locator('[data-mh=schedules] summary').click()
            assert page.locator('[data-mh=schedules] [data-mh=next-transition]').count()==0,'single-group repeats headline transition'
        check('reference separate from review; true transition window; collapsed evidence without single-group duplication',evidence)
        def stability():
            boot();page.locator('[data-mh=schedules] summary').click();page.locator('[data-mh=sources] summary').click()
            search=page.locator('[data-mh=search]');search.fill('B');search.evaluate('e=>{e.focus();e.setSelectionRange(1,1)}')
            page.evaluate('window.__row=document.querySelector("[data-venue-id=b3]");window.__detail=document.querySelector("[data-mh=sources]");window.__scroll=scrollY;__now+=1000')
            page.wait_for_timeout(1100)
            assert search.input_value()=='B' and search.evaluate('e=>e===document.activeElement && e.selectionStart===1')
            assert page.evaluate('__row===document.querySelector("[data-venue-id=b3]") && __detail===document.querySelector("[data-mh=sources]") && scrollY===__scroll')
            source=page.locator('[data-mh=sources] a');source.focus();page.evaluate('window.__source=document.activeElement;__now+=60000');page.wait_for_timeout(1100)
            assert page.evaluate('__source===document.activeElement && __source.isConnected')
            assert page.locator('[data-mh=sources]').evaluate('e=>e.open') and page.locator('[data-mh=schedules]').evaluate('e=>e.open')
            assert page.locator('[data-mh=summary]').inner_text()=='Nenhuma bolsa aberta agora'
        check('search/caret/scroll/node identity and evidence focus survive tick and regrouping transition',stability)
        def scroll_stability():
            boot(before="for(let i=0;i<24;i++){const v=structuredClone(__catalog.venues[0]);v.id='extra-'+i;v.name='Bolsa '+i;__catalog.venues.push(v)}")
            # Keep every row displayed across the boundary to isolate scroll preservation.
            page.locator('[data-mh-quick=all]').click()
            page.evaluate("const wrap=document.querySelector('.mh-table-wrap');wrap.scrollTop=230;window.__scrollTop=wrap.scrollTop;__now+=1000")
            assert page.evaluate('__scrollTop')==230
            page.wait_for_timeout(1100)
            assert page.locator('.mh-table-wrap').evaluate('e=>e.scrollTop')==230
            page.evaluate('__now+=60000');page.wait_for_timeout(1100)
            assert page.locator('.mh-table-wrap').evaluate('e=>e.scrollTop')==230
        check('nonzero list scroll survives idle tick and actual group movement with 29 synthetic venues',scroll_stability)
        def reveal_scrolled_selection():
            boot(before="for(let i=0;i<24;i++){const v=structuredClone(__catalog.venues[0]);v.id='extra-'+i;v.name='Bolsa '+i;__catalog.venues.push(v)}")
            page.locator('[data-venue-id=extra-23] button').click()
            page.locator('[data-mh=search]').fill('no-match')
            page.locator('[data-mh=show-selected]').click()
            assert page.locator('[data-venue-id=extra-23] button').evaluate("e=>{const b=e.getBoundingClientRect(),r=e.closest('.mh-table-wrap').getBoundingClientRect();return b.top>=Math.max(0,r.top) && b.bottom<=Math.min(innerHeight,r.bottom)}"),'explicit reveal did not scroll selected row into view'
            assert page.locator('[data-venue-id=extra-23]').evaluate("e=>{const b=e.getBoundingClientRect(),r=e.closest('.mh-table-wrap').getBoundingClientRect();return b.top>=Math.max(0,r.top) && b.bottom<=Math.min(innerHeight,r.bottom)}"),'explicit reveal clipped part of the selected exchange row'
        check('explicit reveal brings an offscreen selected row into the table and page viewport',reveal_scrolled_selection)
        def mobile():
            boot(True)
            assert page.evaluate('__loads===0 && __creates===0'),'hidden mobile map loaded renderer'
            assert page.locator('[data-mh=map-toggle]').get_attribute('aria-expanded')=='false'
            assert page.locator('[data-mh=globe]').is_hidden()
            assert page.locator('[data-venue-id=b3] button').bounding_box()['y']<600
            page.screenshot(path=str(out/'mobile-initial.png'));result['screenshots'].append(str(out/'mobile-initial.png'))
            page.locator('[data-venue-id=nyse] button').click()
            assert page.locator('[data-mh=detail-title]').inner_text()=='NYSE'
            assert page.locator('.mh-inline-detail').evaluate('e=>e.previousElementSibling.dataset.venueId==="nyse"')
            page.locator('[data-mh=map-toggle]').click();page.wait_for_function('__creates===1')
            page.locator('[data-mh=map-toggle]').click();assert page.evaluate('__active.at(-1)===false')
            page.evaluate('window.__time=document.querySelector("[data-mh=clock]").dateTime;__now+=60000');page.wait_for_timeout(1100)
            assert page.locator('[data-mh=clock]').get_attribute('datetime')!=page.evaluate('__time')
            page.locator('[data-mh=map-toggle]').click();page.wait_for_timeout(60)
            assert page.evaluate('__loads===1 && __creates===1')
            assert page.locator('[data-mh=detail-title]').inner_text()=='NYSE'
            page.screenshot(path=str(out/'mobile.png'),full_page=True);result['screenshots'].append(str(out/'mobile.png'))
        check('mobile names first, map lazy closed, detail adjacent, clock continues and renderer singleton on reopen',mobile)
        def resizing():
            boot(True);page.set_viewport_size({'width':1280,'height':900});page.wait_for_function('__creates===1')
            assert page.locator('[data-mh=globe]').is_visible()
            assert page.locator('.mh-list').bounding_box()['x']<page.locator('.mh-globe-panel').bounding_box()['x']
            page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(80)
            assert page.locator('[data-mh=globe]').is_hidden() and page.evaluate('__active.at(-1)===false')
            page.locator('[data-mh=map-toggle]').click();page.set_viewport_size({'width':1280,'height':900});page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(80)
            assert page.locator('[data-mh=globe]').is_visible() and page.evaluate('__creates===1')
            for size in [320,390,800,1280]:
                page.set_viewport_size({'width':size,'height':900});page.evaluate('document.documentElement.dataset.fs="2"');page.wait_for_timeout(50)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),str(size)+'px overflow'
            page.screenshot(path=str(out/'desktop.png'));result['screenshots'].append(str(out/'desktop.png'))
        check('resize default/explicit mobile state, desktop map right, text scaling and no overflow at 320/390/800/1280',resizing)
        def resize_focus():
            boot(True)
            page.locator('[data-mh=map-toggle]').focus()
            assert page.locator('[data-mh=map-toggle]').evaluate('e=>e===document.activeElement')
            page.set_viewport_size({'width':1280,'height':900});page.wait_for_timeout(80)
            assert page.evaluate("(()=>{const e=document.activeElement,r=e.getBoundingClientRect();return e!==document.body && !e.closest('[hidden],[inert]') && r.width>0 && r.height>0 && r.bottom>0 && r.top<innerHeight})()"),'resize left focus on hidden mobile map toggle'
        check('focused mobile map toggle transfers focus to a visible control when desktop hides it',resize_focus)
        def narrow_zoom():
            boot(True)
            page.evaluate("const root=document.querySelector('.market-hours');root.style.width='155px';root.style.zoom='2';document.documentElement.dataset.fs='2'")
            # The approved integrated surface adds a border. Verify the same155CSSpx
            # outer fixture at2x and preserve the content-overflow and HH:mm oracles.
            assert page.locator('.market-hours').evaluate('e=>Math.abs(e.getBoundingClientRect().width-310)<1 && e.scrollWidth<=e.clientWidth+1'),'155px consultation panel overflows at CSS zoom 2'
            assert page.locator('[data-venue-id=b3] .mh-local').inner_text()=='12:00'
            assert page.locator('[data-venue-id=b3] .mh-local').evaluate("e=>{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect(),c=e.getBoundingClientRect();return r.getClientRects().length===1 && b.left>=c.left && b.right<=c.right}"),'HH:mm does not fit its own column on one line'
            page.screenshot(path=str(out/'narrow-zoom.png'));result['screenshots'].append(str(out/'narrow-zoom.png'))
        check('narrow mobile panel at 155 CSS px and zoom 2 contains HH:mm without local overflow',narrow_zoom)
        def cancel():
            boot(True,'JPWMarketHoursAssets.getRenderer=({signal})=>{__loads++;__signals.push(signal);return new Promise(r=>window.__late=r)}')
            assert page.evaluate('__loads')==0
            page.locator('[data-mh=map-toggle]').click();page.wait_for_function('typeof __late==="function"')
            page.locator('[data-mh=map-toggle]').click();assert page.evaluate('__signals[0].aborted')
            page.evaluate('__late(__factory)');page.wait_for_timeout(50);assert page.evaluate('__creates')==0
            page.evaluate('JPWMarketHoursAssets.getRenderer=()=>Promise.resolve(__factory)');page.locator('[data-mh=map-toggle]').click();page.wait_for_function('__creates===1')
            page.evaluate('JPWMarketHours.dispose();window.dispatchEvent(new Event("resize"));JPWMarketHours.activate()')
            assert page.evaluate('__disposed')==1 and page.locator('.market-hours').count()==0
        check('closing aborts delayed map load, ignores late resolution, reopen succeeds and dispose removes resize subscription',cancel)
        def lifecycle():
            boot();page.wait_for_function('__creates===1')
            for hide,show in [('document.querySelector("#slot").inert=true','document.querySelector("#slot").inert=false'),('window.dispatchEvent(new Event("blur"))','window.dispatchEvent(new Event("focus"))'),('JPWMarketHours.deactivate()','JPWMarketHours.activate()')]:
                page.evaluate(hide);page.wait_for_timeout(50);page.evaluate('window.__time=document.querySelector("[data-mh=clock]").dateTime;__now+=60000');page.wait_for_timeout(1100)
                assert page.locator('[data-mh=clock]').get_attribute('datetime')==page.evaluate('__time') and page.evaluate('__active.at(-1)===false')
                page.evaluate(show);page.wait_for_timeout(60)
                assert page.locator('[data-mh=clock]').get_attribute('datetime')!=page.evaluate('__time') and page.evaluate('__active.at(-1)===true')
            assert page.evaluate('__creates===1 && JSON.stringify(S)===__beforeFinance')
        check('modal/inert, window blur, route suspension and current-time resume preserve financial state',lifecycle)
        def unknown():
            boot(before='__now+=172800000')
            assert page.locator('[data-mh=summary]').inner_text()=='Nenhuma bolsa aberta agora'
            assert page.locator('[data-mh-quick=unknown]').inner_text()=='Sem confirmação 5'
            assert 'não confirmada' in page.locator('[data-mh=next-transition]').inner_text()
            page.locator('[data-mh-quick=open]').click()
            assert page.locator('[data-mh=empty]').is_hidden(), 'An unrestricted empty Open filter is not an unsuccessful search'
            assert page.locator('[data-mh=upcoming-empty]').is_visible()
            assert page.locator('[data-mh=selection-outside]').is_visible()
        check('expired catalog is unknown, zero open remains explicit and empty filter retains selected detail',unknown)
        def literal():
            boot(before='__catalog.venues[0].name="<img src=x onerror=alert(1)>";__catalog.venues[0].groups[0].periods[0].reason="<script>window.__injected=true</script>"')
            assert page.locator('[data-venue-id=b3] button').inner_text()=='<img src=x onerror=alert(1)>'
            assert page.locator('.market-hours img,.market-hours script').count()==0 and page.evaluate('!window.__injected'), 'executable content inserted'
        check('catalog names/reasons are literal text without executable markup',literal)
        def human_labels():
            boot(before="__catalog.venues[1].groups[0].periods[0].phase='auction';__catalog.venues[3].groups[0].periods[0].phase='extended'")
            assert 'Em leilão / Intervalo' in page.locator('[data-venue-id=nyse] .mh-phase').inner_text()
            assert 'Sessão estendida' in page.locator('[data-venue-id=nse] .mh-phase').inner_text()
            assert 'Fases distintas' not in page.locator('.market-hours').inner_text()
        check('known mixed non-open phases and extended session use explicit human labels',human_labels)
        def precision():
            boot(before="const p=__catalog.venues[0].groups[0].periods;p[0].endUtc=__now+59999;p[1].startUtc=__now+59999;p[0].transitionWindow={earliestUtc:__now+50000,latestUtc:__now+59999,nextPhase:'break'}")
            assert '12:00:50–12:00:59' in page.locator('[data-mh=next-transition]').inner_text()
            assert page.locator('[data-venue-id=b3] .mh-local').inner_text()=='12:00'
            boot(before="__catalog.venues[1].groups[0].periods[0].phase='closed';const p=__catalog.venues[0].groups[0].periods;delete p[0].transitionWindow;p[0].endUtc=__now+43260000;p[1].startUtc=__now+43260000")
            assert page.locator('[data-mh=summary]').inner_text()=='1 bolsa aberta agora'
            assert '16/10/2026' in page.locator('[data-mh=next-transition]').inner_text()
        check('subminute window retains precision; singular count and next-day transition date remain honest',precision)
        context.close();browser.close()
    result['status']='PASS' if result['checks'] and not result['failures'] and not result['errors'] else 'PRODUCT_FAIL'
    result['selection']=args.only or 'all'
    result['hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES+['tools/market_hours_redesign_test.py']}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',help='Run cases whose behavior name contains this text');parser.add_argument('--out-dir',default='tools/.artifacts/market-hours/redesign-20261016/green');raise SystemExit(run(parser.parse_args()))

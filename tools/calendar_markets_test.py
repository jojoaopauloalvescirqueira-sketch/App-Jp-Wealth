#!/usr/bin/env python3
"""CALENDAR-MARKETS: approved combined host and collapsed consultation contracts.

Oracle: human-approved 2026-10-24 calendar/markets plan. Real modular HTTP host
plus offline synthetic schedules exercising the production session/view/controller.
No operator browser profile, financial inputs or storage are used.
"""
import argparse
import hashlib
import json
import math
import re
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright
from galton_board_test import serve, prepare_page
from research_navigation_test import launch_browser
from market_hours_upcoming_test import catalog, START, HOUR
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    'src/js/40-app/31-market-hours/01-sessions.js',
    'src/js/40-app/31-market-hours/03-view.js',
    'src/js/40-app/31-market-hours/04-controller.js',
    'src/styles/app.css',
]
INPUTS = SOURCES + ['index.html', 'src/js/40-app/01-navigation.js',
    'src/js/20-ui/31-tools-services.js', 'tools/calendar_markets_test.py',
    'docs/superpowers/plans/2026-10-24-calendar-markets.md']


def write_fixture(out, mutant=None):
    scripts = SOURCES[:-1].copy()
    mutations = {
        'eager-full': (2, 'expanded=options?.collapsed!==true', 'expanded=true'),
        'second-cadence': (2, 'let delay=expanded ? 1000:60000-now%60000', 'let delay=1000'),
        'exclusive-horizon': (1, 'v.nextRegularOpen.latestUtc<=snapshot.asOf+86400000', 'v.nextRegularOpen.latestUtc<snapshot.asOf+86400000'),
    }
    if mutant in mutations:
        index, before, after = mutations[mutant]
        source = (ROOT / scripts[index]).read_text()
        assert source.count(before) == 1, 'TEST_HARNESS_FAIL: mutation anchor must match exactly once'
        mutated = out / ('mutant-' + mutant + '.js')
        mutated.write_text(source.replace(before, after, 1))
        scripts[index] = str(mutated)
    fixture = out / 'fixture.html'
    fixture.write_text('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<link rel="stylesheet" href="' + (ROOT / SOURCES[-1]).as_uri() + '">'
        + ('<style>#tools [data-mh="expansion-toggle"]{padding-top:16px!important;padding-bottom:4px!important}</style>' if mutant == 'misaligned-content' else '')
        +
        '</head><body><main id="tools" class="active" style="grid-area:main;padding:16px;min-width:0">'
        '<h2 id="marketHoursTitle" tabindex="-1">Bolsas globais</h2><div id="slot"></div></main>'
        + ''.join('<script src="' + (ROOT / p).as_uri() + '"></script>' for p in scripts)
        + '<script>window.__now=' + str(START) + ';Date.now=()=>__now;window.__catalog='
        + json.dumps(catalog()) + ''';
        window.__catalogLoads=0;window.__rendererLoads=0;window.__creates=0;window.__active=[];
        window.__finance={accounts:[{balance:1234.5}],backupVersion:4};window.S=__finance;
        window.__beforeFinance=JSON.stringify(S);window.__writes=[];
        const realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){__writes.push(k);return realSet.call(this,k,v)};
        const realRemove=Storage.prototype.removeItem;Storage.prototype.removeItem=function(k){__writes.push(k);return realRemove.call(this,k)};
        window.__atCalls=0;window.__failSnapshot=false;window.__realAt=JPWMarketSessions.at;
        window.JPWMarketSessions={...JPWMarketSessions,at(...a){__atCalls++;if(__failSnapshot)throw Error('SYN snapshot unavailable');return __realAt(...a)}};
        window.__factory={create(h,o){__creates++;const node=document.createElement('div');node.className='fixture-renderer';h.append(node);
          return {update(){},focusMarker(){},focusLocation(){},setActive(v){__active.push(v)},dispose(){node.remove()}}}};
        window.JPWMarketHoursAssets={getCatalog:()=>{__catalogLoads++;return Promise.resolve(__catalog)},
          getRenderer:()=>{__rendererLoads++;return Promise.resolve(__factory)}};
        window.__mount=(collapsed=true)=>{JPWMarketHours.mount(document.querySelector('#slot'),{collapsed});JPWMarketHours.activate()};
        </script></body></html>''', encoding='utf-8')
    return fixture


def run(args):
    out = (ROOT / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    fixture = write_fixture(out, args.mutant)
    result = dict(status='PRODUCT_FAIL', checks=[], failures=[], errors=[],
                  oracle='docs/superpowers/plans/2026-10-24-calendar-markets.md', mutant=args.mutant,
                  sources={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS})
    server, url = serve()
    try:
        with sync_playwright() as pw:
            browser = launch_browser(pw)
            context = browser.new_context(viewport={'width': 1280, 'height': 900},
                                          reduced_motion='reduce', service_workers='block')
            context.set_offline(True)
            page = context.new_page()
            page.set_default_timeout(3000)
            page.clock.install(time=datetime.fromtimestamp(START / 1000, timezone.utc))
            page.clock.pause_at(datetime.fromtimestamp((START + HOUR) / 1000, timezone.utc))
            page.on('pageerror', lambda e: result['errors'].append(str(e)))

            def check(ident, name, fn):
                if args.only and args.only not in ident + ' ' + name:
                    return
                print('RUN ' + ident, flush=True)
                try:
                    fn()
                    result['checks'].append(dict(id=ident, case=name))
                    print('PASS ' + ident, flush=True)
                except Exception:
                    result['failures'].append(dict(id=ident, case=name, trace=traceback.format_exc()))
                    print('PRODUCT_FAIL ' + ident, flush=True)

            def host(fn):
                current = prepare_page(browser, url)
                current.set_default_timeout(3000)
                try:
                    if args.mutant == 'duplicate-nav':
                        current.evaluate("(()=>{const b=document.createElement('button');b.dataset.navChild='tools-market-hours';b.textContent='Bolsas Globais';document.querySelector('[data-nav-child=tools-calendar]').after(b)})()")
                    fn(current)
                    assert not current.jpwealth_observed['pageerror'], current.jpwealth_observed['pageerror']
                finally:
                    current.jpwealth_context.close()

            def boot(before=None, collapsed=True, width=1280):
                page.set_viewport_size({'width': width, 'height': 900 if width > 700 else 844})
                page.goto(fixture.as_uri())
                if before:
                    page.evaluate('()=>{' + before + '}')
                page.evaluate('__mount', collapsed)
                page.wait_for_selector('[data-mh=summary-clock][datetime]', state='attached')

            def advance(ms):
                page.evaluate('(ms)=>__now+=ms', ms)
                page.clock.run_for(ms)

            def ids(group):
                return page.locator('[data-mh=summary-' + group + '-list] [data-mh-summary-venue]').evaluate_all('es=>es.map(e=>e.dataset.mhSummaryVenue)')

            def unchanged():
                assert page.evaluate('JSON.stringify(S)===__beforeFinance && __writes.length===0'), 'PRODUCT_FAIL: market consultation changed financial state/storage'

            def names(p):
                entry = p.locator('[data-nav-child=tools-calendar]')
                assert entry.count() == 1 and entry.locator('.nav-sub-item-title').inner_text().strip() == 'Calendário e Mercados', 'PRODUCT_FAIL: combined submenu name absent'
                assert p.locator('[data-nav-child=tools-market-hours]').count() == 0, 'PRODUCT_FAIL: duplicate market-hours submenu remains'
            check('CM-HOST-01', 'single named calendar and markets submenu', lambda: host(names))

            def canonical(p):
                assert p.evaluate("(()=>{const r=JPWNavigation.resolve('tools-market-hours');return r.accepted&&r.child==='tools-calendar'&&r.localView?.view==='market-hours'})()"), 'PRODUCT_FAIL: legacy market route does not canonicalize to calendar child'
                assert p.evaluate("JPWNavigation.navigate('tools-calendar')")
                assert p.locator('#calendarMarketsTitle').is_visible(), 'PRODUCT_FAIL: combined view heading absent'
                assert p.locator('#calendarMarketsJump').is_visible(), 'PRODUCT_FAIL: quicklink absent'
                assert p.evaluate("(()=>{const a=document.querySelector('#execEcal'),b=document.querySelector('#marketHoursTool');return a&&b&&a.parentElement===b.parentElement&&a.dataset.toolsView==='calendar'&&b.dataset.toolsView==='calendar'})()"), 'PRODUCT_FAIL: calendar and markets are not sibling calendar panels'
            check('CM-HOST-02', 'canonical legacy destination, heading, quicklink and sibling panels', lambda: host(canonical))

            def host_overview(p):
                assert p.evaluate("JPWNavigation.navigate('tools-calendar')")
                assert p.locator('#marketHoursTool').is_visible(), 'PRODUCT_FAIL: market overview absent from calendar'
                assert p.locator('#toolsMarketHoursSlot [data-mh=summary]').is_visible(), 'PRODUCT_FAIL: collapsed overview absent'
                assert p.locator('#toolsMarketHoursSlot .market-hours').count() == 0, 'PRODUCT_FAIL: full consultation mounted before expansion'
            check('CM-HOST-03', 'normal calendar entry exposes collapsed market overview', lambda: host(host_overview))

            def api():
                page.goto(fixture.as_uri())
                assert page.evaluate("typeof JPWMarketHours.setExpanded==='function'"), 'PRODUCT_FAIL: public setExpanded API absent'
                page.evaluate('__mount(true)')
                page.wait_for_selector('[data-mh=summary]', state='attached')
                assert page.locator('.market-hours').count() == 0, 'PRODUCT_FAIL: collapsed mount created full view'
                assert page.locator('[data-mh=expansion-toggle]').get_attribute('aria-expanded') == 'false'
            check('CM-API-01', 'collapsed mount and public expansion API', api)

            def overview():
                boot()
                assert ids('open') == ['b3', 'open0', 'open1'], 'Open preview must preserve catalog order and cap at three'
                assert ids('upcoming') == ['active-window', 'active-resume', 'soon'], 'Upcoming preview must preserve engine order and cap at three'
                for group, count in [('open', 36), ('upcoming', 9), ('unknown', 2)]:
                    text = page.locator('[data-mh=summary-' + group + '-count]').inner_text()
                    assert re.search(r'\b' + str(count) + r'\b', text), (group, count, text)
                assert page.locator('[data-mh=summary-clock]').get_attribute('datetime') == '2026-10-15T12:00:00.000Z'
                assert page.locator('.market-hours').count() == 0 and page.evaluate('__rendererLoads===0 && __creates===0')
                unchanged()
            check('CM-SUM-01', 'catalog ordered three-open and three-upcoming preview with total and unknown counts', overview)

            def boundaries():
                boot("__catalog.venues=__catalog.venues.filter(v=>['b3','boundary','outside','straddling','unknown','partial','blocked'].includes(v.id))")
                assert ids('open') == ['b3']
                assert ids('upcoming') == ['boundary'], '24h is inclusive; outside, straddling window, blocked and unknown must be excluded'
                advance(25)
                assert ids('upcoming') == ['boundary', 'outside'], 'Horizon entry must refresh before the next minute'
                unchanged()
            check('CM-SUM-02', 'inclusive 24h horizon, uncertain window and unknown exclusions with horizon entry', boundaries)

            def summary_selection():
                boot()
                page.locator('[data-mh-summary-venue=soon]').click()
                assert page.locator('.market-hours').is_visible()
                assert page.locator('[data-mh=detail-title]').inner_text() == 'Soon'
                assert page.locator('[data-mh=summary]').is_hidden()
                assert page.locator('[data-mh=expansion-toggle]').get_attribute('aria-expanded') == 'true'
                page.locator('[data-mh=search]').fill('Later')
                page.locator('[data-mh=phase-options] summary').click()
                page.locator('[data-mh=filter]').select_option('closed')
                page.evaluate("window.__full=document.querySelector('.market-hours');window.__search=document.querySelector('[data-mh=search]');window.__row=document.querySelector('[data-venue-id=later]');document.querySelector('.mh-table-wrap').scrollTop=100;window.__scroll=document.querySelector('.mh-table-wrap').scrollTop")
                page.locator('[data-mh=expansion-toggle]').click()
                assert page.locator('.market-hours').is_hidden()
                assert ids('open') == ['b3', 'open0', 'open1'], 'Exploration filters leaked into preview'
                page.locator('[data-mh-summary-venue=b3]').click()
                assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
                assert page.locator('[data-mh=search]').input_value() == 'Later'
                assert page.locator('[data-mh=filter]').input_value() == 'closed'
                assert page.evaluate("__full===document.querySelector('.market-hours') && __search===document.querySelector('[data-mh=search]') && __row===document.querySelector('[data-venue-id=later]')"), 'Reopening recreated stable exploration nodes'
                assert page.evaluate("document.querySelector('.mh-table-wrap').scrollTop===__scroll"), 'Reopening lost internal scroll'
                assert page.evaluate('__catalogLoads===1') and page.locator('.market-hours').count() == 1
                unchanged()
            check('CM-EXP-01', 'summary click expands/selects and reopening retains nodes filters selection and scroll', summary_selection)

            def scheduler():
                boot("__catalog.venues=__catalog.venues.filter(v=>v.id==='b3')")
                calls = page.evaluate('__atCalls')
                advance(59000)
                assert page.evaluate('__atCalls') == calls, 'Collapsed consultation still recalculates once per second'
                advance(1000)
                assert 1 <= page.evaluate('__atCalls') - calls <= 2, 'Minute boundary did not use one shared snapshot'
                page.locator('[data-mh=expansion-toggle]').click()
                calls = page.evaluate('__atCalls')
                advance(1000)
                assert 1 <= page.evaluate('__atCalls') - calls <= 2, 'Exploration lost its second cadence'
                page.locator('[data-mh=expansion-toggle]').click()
                calls = page.evaluate('__atCalls')
                page.evaluate('JPWMarketHours.deactivate()')
                advance(120000)
                assert page.evaluate('__atCalls') == calls, 'Inactive consultation still recalculates'
                page.evaluate('JPWMarketHours.activate()')
                assert page.evaluate('__atCalls') > calls
                unchanged()
            check('CM-LIFE-01', 'one adaptive minute scheduler while collapsed, seconds full, and inactive pause', scheduler)

            def windows():
                boot("__catalog.venues=__catalog.venues.filter(v=>['b3','uncertain'].includes(v.id))")
                text = page.locator('[data-mh=summary-upcoming-list]').inner_text()
                assert '12:00:30' in text and '12:01:30' in text, 'Summary must expose both precise local uncertainty bounds'
                calls = page.evaluate('__atCalls')
                advance(29999)
                assert page.evaluate('__atCalls') == calls
                advance(1)
                assert 'andamento' in page.locator('[data-mh=summary-upcoming-list]').inner_text(), 'Earliest window boundary was missed'
                advance(60000)
                assert ids('open') == ['b3', 'uncertain'] and ids('upcoming') == [], 'Latest window boundary was missed'
                unchanged()
            check('CM-LIFE-02', 'precise uncertainty bounds and earliest/latest window boundaries', windows)

            def retry():
                page.goto(fixture.as_uri())
                page.evaluate("__catalogLoads=0;JPWMarketHoursAssets.getCatalog=()=>{__catalogLoads++;return __catalogLoads===1?Promise.reject(Error('SYN catalog unavailable')):Promise.resolve(__catalog)};__mount(true)")
                retry_button = page.locator('[data-mh=catalog-retry]')
                retry_button.wait_for(state='visible')
                assert retry_button.is_visible(), 'Collapsed catalog failure hides recovery'
                assert 'indisponível' in page.locator('#slot').inner_text().lower()
                assert page.locator('.market-hours').count() == 0
                advance(120000)
                assert page.evaluate('__catalogLoads') == 1, 'Failure silently retried'
                retry_button.focus()
                retry_button.press('Enter')
                page.wait_for_selector('[data-mh-summary-venue=b3]', state='attached')
                assert page.evaluate('__catalogLoads') == 2 and ids('open') == ['b3', 'uncertain', 'active-window'], 'Retry must consult current time, after the two-minute pause'
                assert page.locator('.market-hours').count() == 0 and page.evaluate('__rendererLoads') == 0
                unchanged()
            check('CM-FAIL-01', 'collapsed catalog failure stays visible and explicit retry preserves collapsed mode', retry)

            def stale_snapshot():
                boot("__catalog.venues=__catalog.venues.filter(v=>v.id==='b3')")
                old_clock = page.locator('[data-mh=summary-clock]').get_attribute('datetime')
                page.evaluate('__failSnapshot=true')
                advance(60000)
                status = page.locator('#slot [role=status]').filter(has_text=re.compile('indisponível', re.I))
                assert status.is_visible() and 'indisponível' in status.inner_text().lower()
                assert re.search(r'desatualiz|última referência', status.inner_text(), re.I), 'Failure presented old market facts as current'
                assert page.locator('[data-mh=summary-clock]').get_attribute('datetime') == old_clock
                assert ids('open') == ['b3'] and page.locator('[data-mh=summary-open-count]').inner_text().startswith('1 '), 'Snapshot failure replaced last facts with zero'
                page.evaluate('__failSnapshot=false')
                page.locator('[data-mh=catalog-retry]').click()
                page.wait_for_function("document.querySelector('[data-mh=summary-clock]').dateTime===new Date(__now).toISOString()")
                assert status.count() == 0 and page.evaluate('__catalogLoads===1 && __rendererLoads===0')
                unchanged()
            check('CM-FAIL-02', 'snapshot failure marks last facts stale and explicit retry recovers without false zero', stale_snapshot)

            def retry_focus_departure():
                page.goto(fixture.as_uri())
                page.evaluate("()=>{JPWMarketHoursAssets.getCatalog=()=>{__catalogLoads++;return __catalogLoads===1?Promise.reject(Error('SYN first failure')):new Promise(r=>window.__retryResolve=r)};__mount(true)}")
                retry_button = page.locator('[data-mh=catalog-retry]')
                retry_button.wait_for(state='visible')
                retry_button.click()
                page.wait_for_function("typeof __retryResolve==='function'")
                page.evaluate("()=>{const b=document.createElement('button');b.id='SYN_retry_external';b.textContent='Controle externo';document.body.append(b);b.focus();__retryResolve(__catalog)}")
                page.wait_for_selector('[data-mh-summary-venue=b3]', state='attached')
                assert page.evaluate('document.activeElement.id==="SYN_retry_external"'), 'PRODUCT_FAIL: late catalog retry stole focus after the user left its button'
                unchanged()
            check('CM-P2-01', 'pending catalog retry must not steal focus after user moves to an external control', retry_focus_departure)

            def expanded_mobile_failure():
                boot("__catalog.venues=__catalog.venues.filter(v=>v.id==='b3')", width=390)
                page.locator('[data-mh=expansion-toggle]').click()
                assert page.locator('[data-mh=map-toggle]').get_attribute('aria-expanded') == 'false'
                assert page.locator('[data-mh=map-content]').is_hidden()
                page.evaluate('__failSnapshot=true')
                advance(1000)
                status = page.locator('#slot [role=status]:visible').filter(has_text=re.compile('indisponível', re.I))
                assert status.count() >= 1, 'PRODUCT_FAIL: expanded mobile consultation silently displays stale facts with the map collapsed'
                retry_button = page.locator('#slot button:visible').filter(has_text=re.compile('Tentar.*novamente', re.I))
                assert retry_button.count() == 1, 'PRODUCT_FAIL: expanded mobile snapshot failure has no visible retry'
                assert 'desatualiz' in status.first.inner_text().lower() or 'última referência' in status.first.inner_text().lower()
                page.evaluate('__failSnapshot=false')
                retry_button.click()
                assert status.count() == 0
                assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
                unchanged()
            check('CM-P2-02', 'expanded mobile snapshot failure and recovery remain visible with the map collapsed', expanded_mobile_failure)

            def cold_alias_anchor():
                def at_width(p, width):
                    p.set_viewport_size({'width': width, 'height': 844 if width < 700 else 900})
                    p.evaluate("mountNavigationLayout('sidebar')")
                    assert p.evaluate("JPWNavigation.navigate('tools-market-hours')")
                    p.wait_for_selector('.market-hours', state='visible')
                    p.wait_for_timeout(250)
                    box = p.locator('#marketHoursTitle').bounding_box()
                    assert 0 <= box['y'] <= 200, ('PRODUCT_FAIL: cold legacy alias did not keep its section anchored after lazy full DOM grew', width, box)
                    assert p.locator('#marketHoursTitle').evaluate('e=>e===document.activeElement')
                for width in [390, 1440]:
                    host(lambda p: at_width(p, width))
            check('CM-P2-03', 'cold legacy alias anchors its heading after lazy full DOM grows on mobile and desktop', cold_alias_anchor)

            def summary_focus_migration():
                boot()
                page.locator('[data-mh-summary-venue=soon]').focus()
                page.evaluate('__now+=3000;JPWMarketHours.activate()')
                assert page.locator('[data-mh=expansion-toggle]').evaluate('e=>e===document.activeElement'), 'Removed preview row did not return focus to the expansion control'
                boot()
                page.locator('[data-mh-summary-venue=active-resume]').focus()
                page.evaluate('window.__summaryFocus=document.activeElement;__now+=3000;JPWMarketHours.activate()')
                assert page.evaluate('__summaryFocus.isConnected && __summaryFocus===document.activeElement && !!__summaryFocus.getClientRects().length'), 'PRODUCT_FAIL: changing another preview row discarded focus on a surviving row'
                assert ids('upcoming') == ['active-window', 'active-resume', 'uncertain']
                unchanged()
            check('CM-P2-04', 'preview transitions preserve focus on surviving nodes and recover focus when a row is removed', summary_focus_migration)

            def viewport_and_late_renderer():
                boot("document.querySelector('main').style.paddingTop='2000px';JPWMarketHoursAssets.getRenderer=()=>{__rendererLoads++;return new Promise(r=>window.__lateRenderer=r)}")
                page.evaluate('JPWMarketHours.setExpanded(true)')
                page.wait_for_timeout(60)
                assert page.evaluate('__rendererLoads===0 && __creates===0'), 'Offscreen map requested the renderer'
                page.locator('[data-mh=globe]').scroll_into_view_if_needed()
                page.wait_for_function("typeof __lateRenderer==='function'")
                page.evaluate("JPWMarketHours.setExpanded(false);const b=document.createElement('button');b.id='SYN_external_focus';b.textContent='Foco externo';document.body.append(b);b.focus();__lateRenderer(__factory)")
                page.wait_for_timeout(60)
                assert page.evaluate('__creates===0 && document.activeElement.id==="SYN_external_focus"'), 'Late renderer resurrected collapsed map or stole focus'
                page.evaluate('JPWMarketHoursAssets.getRenderer=()=>{__rendererLoads++;return Promise.resolve(__factory)};JPWMarketHours.setExpanded(true)')
                page.locator('[data-mh=globe]').scroll_into_view_if_needed()
                page.wait_for_function('__creates===1 && __active.at(-1)===true')
                page.evaluate('scrollTo(0,0)')
                page.wait_for_function('__active.at(-1)===false')
                assert page.evaluate('__creates===1'), 'Viewport changes created a second renderer'
                unchanged()
            check('CM-LIFE-04', 'viewport gates renderer and late resolution after collapse cannot create or steal focus', viewport_and_late_renderer)

            def no_resurrection():
                page.goto(fixture.as_uri())
                page.evaluate("JPWMarketHoursAssets.getCatalog=()=>new Promise(r=>window.__lateCatalog=r);__mount(true)")
                page.wait_for_function("typeof __lateCatalog==='function'")
                page.evaluate('JPWMarketHours.dispose();__lateCatalog(__catalog);JPWMarketHours.activate();JPWMarketHours.mount(document.querySelector("#slot"),{collapsed:true})')
                page.wait_for_timeout(10)
                assert page.locator('[data-mh=summary],.market-hours').count() == 0
                assert page.evaluate('__creates===0 && __rendererLoads===0')
                unchanged()
            check('CM-LIFE-03', 'late catalog after disposal cannot resurrect summary or full view', no_resurrection)

            def keyboard_reflow():
                for width in [320, 390, 720, 1440]:
                    for theme in ['light', 'dark']:
                        boot(width=width)
                        page.evaluate('(theme)=>document.documentElement.dataset.theme=theme', theme)
                        controls = page.locator('[data-mh=summary] button:visible,[data-mh=expansion-toggle]:visible')
                        assert controls.count() >= 7
                        bounds = controls.evaluate_all('es=>es.map(e=>({width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))')
                        assert all(b['width'] >= 44 and b['height'] >= 44 for b in bounds), (width, theme, bounds)
                        assert page.locator('#slot').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), (width, theme, 'overview overflow')
                        assert page.evaluate('__rendererLoads===0 && __creates===0'), 'Collapsed map loaded renderer'
                        toggle = page.locator('[data-mh=expansion-toggle]')
                        toggle.focus()
                        toggle.press('Enter')
                        assert toggle.get_attribute('aria-expanded') == 'true'
                        toggle.press('Space')
                        assert toggle.get_attribute('aria-expanded') == 'false'
                        assert page.evaluate('__active.length===0 || __active.at(-1)===false'), 'Collapsed renderer remains active'
                        unchanged()
            check('CM-UI-01', '320 to 1440 reflow, themes, 44px controls and native expansion keyboard', keyboard_reflow)

            def text_geometry(element):
                return element.evaluate('''e=>{
                  const box=e.getBoundingClientRect(),walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT),rects=[];
                  while(walker.nextNode()){if(!walker.currentNode.textContent.trim())continue;
                    const range=document.createRange();range.selectNodeContents(walker.currentNode);
                    rects.push(...[...range.getClientRects()].filter(r=>r.width>0&&r.height>0));}
                  if(!rects.length)return null;
                  const text={left:Math.min(...rects.map(r=>r.left)),top:Math.min(...rects.map(r=>r.top)),right:Math.max(...rects.map(r=>r.right)),bottom:Math.max(...rects.map(r=>r.bottom))};
                  return {box:box.toJSON(),text,dx:(text.left+text.right-box.left-box.right)/2,dy:(text.top+text.bottom-box.top-box.bottom)/2};
                }''')

            def internal_alignment():
                for width in [320, 390, 720, 1440]:
                    boot(width=width)
                    geometry = text_geometry(page.locator('[data-mh=expansion-toggle]'))
                    assert geometry and abs(geometry['dx']) <= 2 and abs(geometry['dy']) <= 2, ('PRODUCT_FAIL: expansion content is not centered within 2 CSS px', width, geometry)
                    for name in page.locator('[data-mh-summary-venue]').all():
                        geometry = text_geometry(name)
                        assert geometry and abs(geometry['text']['left'] - geometry['box']['left']) <= 2, ('Preview name lost declared left alignment', width, geometry)
                        assert geometry['text']['top'] >= geometry['box']['top'] - 2 and geometry['text']['bottom'] <= geometry['box']['bottom'] + 2
                    rows = page.locator('.mh-overview-list li').evaluate_all('''es=>es.map(e=>{
                      const parts=[...e.children].map(c=>c.getBoundingClientRect());
                      return {parts:parts.map(r=>r.toJSON()),overlap:parts.some((r,i)=>i>0&&r.top<parts[i-1].bottom-1)};
                    })''')
                    assert rows and not any(row['overlap'] for row in rows), ('Preview content overlaps vertically', width, rows)

                def quicklink(p):
                    assert p.evaluate("JPWNavigation.navigate('tools-calendar')")
                    for width in [320, 390, 720, 1440]:
                        p.set_viewport_size({'width': width, 'height': 900})
                        geometry = text_geometry(p.locator('#calendarMarketsJump'))
                        assert geometry and abs(geometry['dx']) <= 2 and abs(geometry['dy']) <= 2, ('Quicklink text and arrow union is not centered within 2 CSS px', width, geometry)
                host(quicklink)
            check('CM-UI-02', 'internal text alignment within two CSS pixels and preview content without overlap', internal_alignment)

            def native_zoom_200():
                # Browser-level preferences change the layout viewport itself.
                # Headless avoids changing the operator's desktop focus while
                # the required ratio/CSS oracle distinguishes this from CSS zoom.
                with tempfile.TemporaryDirectory(prefix='native200-profile-', dir=out) as profile:
                    defaults = Path(profile) / 'Default'
                    defaults.mkdir()
                    preference_zoom = 1 if args.mutant == 'css-native-substitute' else 2
                    (defaults / 'Preferences').write_text(json.dumps({'partition': {'default_zoom_level': {'x': math.log(preference_zoom) / math.log(1.2)}}}))
                    options = launch_options()
                    options.update(headless=True, no_viewport=True, args=['--window-size=1440,1000', '--no-sandbox'],
                                   service_workers='block', reduced_motion='reduce', timezone_id='UTC')
                    result['nativeZoomEnvironment'] = dict(headless=True, noViewportOverride=True,
                        preferenceZoom=preference_zoom, executable=options.get('executable_path'), window=[1440, 1000])
                    native = pw.chromium.launch_persistent_context(profile, **options)
                    try:
                        install_bootstrap(native)
                        native.add_init_script('window.__onbShown=true;')
                        p = native.new_page()
                        p.set_default_timeout(4000)
                        p.on('pageerror', lambda e: result['errors'].append(str(e)))
                        p.clock.set_fixed_time(datetime.fromtimestamp(START / 1000, timezone.utc))
                        p.goto(url, wait_until='load')
                        wait_bootstrap(p)
                        p.evaluate('closeModal()')
                        p.evaluate('(raw)=>{window.JPWMarketHoursAssets={...JPWMarketHoursAssets,getCatalog:()=>Promise.resolve(raw)}}', catalog())
                        if args.mutant == 'css-native-substitute':
                            p.evaluate("document.documentElement.style.zoom='2'")
                        before = p.evaluate('JSON.stringify({state:S,storage:{...localStorage}})')
                        result['nativeZoomCases'] = []

                        def native_oracle():
                            zoom = p.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom,dpr:devicePixelRatio})')
                            assert abs(zoom['outer'] / zoom['inner'] - 2) < .01 and zoom['css'] == '1', ('PRODUCT_FAIL: native200 needs browser zoom, CSS scaling is not a substitute', zoom)
                            return zoom

                        def local_geometry(selector):
                            geometry = p.locator(selector).evaluate('e=>({scroll:e.scrollWidth,client:e.clientWidth,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,viewport:innerWidth})')
                            assert geometry['scroll'] <= geometry['client'] + 1 and geometry['left'] >= -1 and geometry['right'] <= geometry['viewport'] + 1, ('Native200 local market overflow', selector, geometry)
                            return geometry

                        native_oracle()
                        for layout in ['sidebar', 'topbar', 'submenu', 'glass']:
                            for theme in ['light', 'dark']:
                                p.evaluate('(layout)=>mountNavigationLayout(layout)', layout)
                                p.evaluate('(theme)=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                                assert p.evaluate("JPWNavigation.navigate('tools-calendar')")
                                p.evaluate('JPWMarketHours.setExpanded(false)')
                                p.wait_for_selector('[data-mh=summary-clock][datetime]')
                                assert p.locator('[data-mh=summary]').is_visible() and p.locator('.market-hours:visible').count() == 0
                                zoom = native_oracle()
                                summary = local_geometry('#toolsMarketHoursSlot')
                                controls = p.locator('[data-mh=summary] button:visible,[data-mh=expansion-toggle]:visible')
                                dimensions = controls.evaluate_all('es=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))')
                                assert dimensions and all(b['w'] >= 44 and b['h'] >= 44 for b in dimensions), ('Native200 target under44 CSS px', layout, theme, dimensions)
                                toggle = p.locator('[data-mh=expansion-toggle]')
                                geometry = text_geometry(toggle)
                                assert geometry and abs(geometry['dx']) <= 2 and abs(geometry['dy']) <= 2, ('Native200 expansion content exceeds2 CSS px', layout, theme, geometry)
                                toggle.focus()
                                toggle.press('Enter')
                                p.wait_for_selector('.market-hours', state='visible')
                                assert toggle.get_attribute('aria-expanded') == 'true'
                                exploration = local_geometry('.market-hours')
                                p.locator('[data-mh-quick=all]').click()
                                p.locator('[data-venue-id=later] button').click()
                                assert p.locator('[data-mh=detail-title]').inner_text() == 'Later'
                                assert p.locator('[data-venue-id=later] button').evaluate('e=>e===document.activeElement')
                                p.locator('[data-mh=search]').fill('Later')
                                p.evaluate('window.__nativeSearch=document.querySelector("[data-mh=search]");JPWMarketHours.setExpanded(false)')
                                assert toggle.evaluate('e=>e===document.activeElement'), 'Native200 collapse left focus in hidden exploration'
                                toggle.press('Enter')
                                assert p.locator('[data-mh=detail-title]').inner_text() == 'Later' and p.locator('[data-mh=search]').input_value() == 'Later'
                                assert p.evaluate('__nativeSearch===document.querySelector("[data-mh=search]")'), 'Native200 reopening recreated exploration'
                                assert p.evaluate("JPWNavigation.navigate('tools-market-hours')")
                                assert p.evaluate("JPWNavigation.current().child==='tools-calendar'")
                                assert p.locator('#marketHoursTitle').evaluate('e=>e===document.activeElement'), 'Native200 compatible route lost its focus anchor'
                                local_geometry('.market-hours')
                                native_oracle()
                                p.screenshot(path=str(out / ('native200-' + layout + '-' + theme + '.png')))
                                result['nativeZoomCases'].append(dict(layout=layout, theme=theme, zoom=zoom, summary=summary, exploration=exploration, states=['summary', 'full'], selectionAndFocus='PASS'))
                                p.locator('[data-mh=search]').fill('')
                                assert p.evaluate("JPWNavigation.navigate('dashboard')")
                        assert p.evaluate('JSON.stringify({state:S,storage:{...localStorage}})') == before, 'Native200 markets consultation changed state/storage'
                        assert_fixture_requests(native)
                    finally:
                        native.close()
            check('CM-UI-03', 'native engine zoom200 across four layouts two themes summary exploration selection and focus', native_zoom_200)

            def independent(p):
                assert p.evaluate("JPWNavigation.navigate('tools-calendar')")
                p.wait_for_selector('#execEcal [data-calendar-date]')
                p.wait_for_selector('#toolsMarketHoursSlot [data-mh=summary-clock]')
                before = p.locator('[data-mh=summary-clock]').get_attribute('datetime')
                p.locator('#execEcal [data-calendar-date]').first.click()
                p.evaluate("window.__calendarPanel=document.querySelector('#execEcal .calendar-panel');window.__calendarDate=document.querySelector('#execEcal [aria-selected=true]').dataset.calendarDate;window.__agenda=document.querySelector('#execEcal .calendar-agenda');window.__agendaHTML=__agenda.innerHTML;window.__financeBefore=JSON.stringify(S)")
                p.locator('#calendarMarketsJump').click()
                assert p.locator('#marketHoursTitle').evaluate('e=>e===document.activeElement'), 'Quicklink did not anchor the market section'
                if p.locator('.market-hours:visible').count() == 0:
                    p.locator('[data-mh=expansion-toggle]').click()
                p.wait_for_selector('.market-hours', state='visible')
                p.wait_for_timeout(1100)
                assert p.evaluate("__calendarPanel===document.querySelector('#execEcal .calendar-panel') && __agenda===document.querySelector('#execEcal .calendar-agenda') && __agendaHTML===__agenda.innerHTML && __calendarDate===document.querySelector('#execEcal [aria-selected=true]').dataset.calendarDate"), 'Market expansion/tick reconstructed or changed selected calendar agenda'
                assert p.evaluate('JSON.stringify(S)===__financeBefore'), 'Market tick changed financial state'
                p.locator('[data-mh=expansion-toggle]').click()
                after = p.locator('[data-mh=summary-clock]').get_attribute('datetime')
                assert after >= before and after[:10] != p.evaluate('__calendarDate'), 'Selected calendar date replaced market now reference'
            check('CM-HOST-04', 'calendar selected date and agenda nodes remain independent of current market time', lambda: host(independent))

            context.close()
            browser.close()
    except Exception:
        result['environmentError'] = traceback.format_exc()
        result['status'] = 'ENVIRONMENT_ERROR'
    finally:
        server.shutdown()
    if result['status'] != 'ENVIRONMENT_ERROR' and not result['failures'] and not result['errors'] and result['checks']:
        result['status'] = 'PASS'
    result['inputsAfter'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS}
    result['stableInputs'] = result['sources'] == result['inputsAfter']
    if not result['stableInputs'] and result['status'] == 'PASS':
        result['status'] = 'TEST_HARNESS_FAIL'
    (out / 'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='/private/tmp/jpw-calendar-markets-20261024/tests')
    parser.add_argument('--only')
    parser.add_argument('--mutant', choices=['eager-full', 'second-cadence', 'exclusive-horizon', 'duplicate-nav', 'misaligned-content', 'css-native-substitute'])
    raise SystemExit(run(parser.parse_args()))

#!/usr/bin/env python3
"""Permanent browser contracts for the approved minimalist market consultation.

Oracle: docs/superpowers/plans/2026-10-16-market-minimal.md (human approved).
Uses the existing synthetic sessions and real view/controller/CSS, offline. This
focal is intentionally standalone: it neither changes gate criteria nor claims
native zoom, shipped renderer, full-host integration or screen-reader validation.
"""
import argparse
import base64
import hashlib
import json
import os
import re
import traceback

from playwright.sync_api import sync_playwright
from market_hours_redesign_test import ROOT, SOURCES, fixture_catalog


def run(args):
    out = (ROOT / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    fixture = out / 'fixture.html'
    fixture.write_text(
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<link rel="stylesheet" href="' + (ROOT / SOURCES[-1]).as_uri() + '">'
        '</head><body style="display:block"><main style="padding:16px;min-width:0;max-width:1400px;margin:auto">'
        '<h2>Bolsas Globais</h2><div id="slot"></div></main>'
        '<div id="jpPopoverLayer"></div>'
        '<button id="outside" type="button">Controle externo sintético</button>'
        + ''.join('<script src="' + (ROOT / p).as_uri() + '"></script>' for p in SOURCES[:-1])
        + '<script>window.__catalog=' + json.dumps(fixture_catalog()) + ''';
        window.__now=1792065600000;Date.now=()=>__now;
        window.__creates=0;window.__disposed=0;window.__camera=[];window.__updates=[];
        window.__finance={accounts:[{balance:1234.5}],backupVersion:4};window.S=__finance;
        window.__beforeFinance=JSON.stringify(S);window.__beforeStorage=[];
        try{__beforeStorage=Object.entries(localStorage)}catch(_){}
        window.__factory={create(h,o){__creates++;window.__options=o;
          const e=document.createElement('div');e.className='fixture-renderer';h.append(e);
          return {update(v){__updates.push(v)},focusMarker(...v){__camera.push(['marker',...v])},
            focusLocation(...v){__camera.push(['location',...v])},setActive(){},
            dispose(){__disposed++;e.remove()}}}};
        window.JPWMarketHoursAssets={getCatalog:()=>Promise.resolve(__catalog),
          getRenderer:()=>Promise.resolve(__factory)};
        window.__mount=()=>{JPWMarketHours.mount(document.querySelector('#slot'));JPWMarketHours.activate()};
        </script></body></html>''', encoding='utf-8')
    result = {'status': 'PRODUCT_FAIL', 'checks': [], 'failures': [], 'errors': [], 'screenshots': [],
              'selection': args.only or 'all', 'oracle': 'docs/superpowers/plans/2026-10-16-market-minimal.md'}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
            context = browser.new_context(viewport={'width': 1280, 'height': 1000},
                                          reduced_motion='reduce', service_workers='block')
            context.set_offline(True)
            page = context.new_page()
            page.set_default_timeout(2500)
            page.on('pageerror', lambda error: result['errors'].append(str(error)))

            def boot(width=1280, before=None, theme='light'):
                page.set_viewport_size({'width': width, 'height': 844 if width < 800 else 1000})
                page.goto(fixture.as_uri())
                page.evaluate('(t)=>document.documentElement.dataset.theme=t', theme)
                if before:
                    page.evaluate('()=>{' + before + '}')
                page.evaluate('__mount()')
                page.wait_for_selector('[data-venue-id=b3] button', state='attached')
                page.wait_for_timeout(60)

            def check(ident, name, fn):
                if args.only and args.only not in ident + ' ' + name:
                    return
                try:
                    fn()
                    result['checks'].append({'id': ident, 'case': name})
                except Exception:
                    result['failures'].append({'id': ident, 'case': name, 'trace': traceback.format_exc()})
                    path = out / ('failure-' + ident + '.png')
                    page.screenshot(path=str(path), full_page=True)
                    result['screenshots'].append(str(path))

            def button(kind):
                el = page.locator('[data-mh=info-button][data-mh-help=' + kind + ']')
                # An immediate assertion makes a missing feature RED independently
                # of Playwright timeouts or browser-environment availability.
                assert el.count() == 1, 'Missing dedicated ' + kind + ' help button (expected exactly one)'
                assert el.is_visible() and el.evaluate('e=>e.tagName==="BUTTON" && !e.matches(".note-i,[data-info]")')
                return el

            def popup():
                el = page.locator('#jpPopoverLayer [data-mh=info-popover]:visible')
                assert el.count() == 1, 'Expected one visible contextual help in the portal'
                return el

            def closed():
                assert page.locator('[data-mh=info-popover]:visible').count() == 0, 'Contextual help remained open'
                assert page.locator('[data-mh=info-button][aria-expanded=true]').count() == 0

            def unchanged():
                assert page.evaluate('JSON.stringify(S)===__beforeFinance'), 'Help changed synthetic financial state'
                assert page.evaluate('(()=>{try{return JSON.stringify(Object.entries(localStorage))===JSON.stringify(__beforeStorage)}catch(_){return true}})()'), 'Help wrote localStorage'

            def semantics():
                boot()
                assert page.locator('[data-mh=info-button]').count() == 2, 'Exactly two dedicated help buttons required'
                for kind in ['calendar', 'map']:
                    trigger = button(kind)
                    assert trigger.get_attribute('aria-label') or trigger.inner_text().strip(), 'Help control needs an accessible name'
                    assert trigger.get_attribute('aria-expanded') == 'false'
                    trigger.click()
                    pop = popup()
                    assert trigger.get_attribute('aria-expanded') == 'true'
                    assert trigger.get_attribute('aria-controls') == pop.get_attribute('id') and pop.get_attribute('id')
                    assert pop.get_attribute('role') not in ['dialog', 'menu', 'tooltip']
                    assert pop.get_attribute('aria-label') or pop.get_attribute('aria-labelledby'), 'Help needs a name as a region'
                    assert page.get_by_role('region').filter(has=page.locator('[data-mh=info-close]')).count() == 1, 'Help must expose a named semantic region'
                    assert page.locator('[role=dialog],[role=menu],[role=tooltip]').count() == 0, 'Help must not participate in global modal semantics'
                    close = pop.locator('[data-mh=info-close]')
                    assert close.count() == 1 and close.is_visible()
                    assert re.search('fechar', close.get_attribute('aria-label') or close.inner_text(), re.I)
                    close.click()
                    closed()
                unchanged()
            check('MIN-01', 'two dedicated named nonmodal help regions with explicit close and ARIA state', semantics)

            def keyboard():
                boot()
                trigger = button('calendar')
                trigger.focus()
                trigger.press('Enter')
                popup()
                page.keyboard.press('Escape')
                closed()
                assert trigger.evaluate('e=>e===document.activeElement'), 'Escape must restore focus to the opener'
                trigger.press('Space')
                pop = popup()
                controls = pop.locator('button,a[href],input,select,textarea,[tabindex="0"]')
                assert controls.count() > 0
                controls.last.focus()
                page.keyboard.press('Tab')
                assert not pop.evaluate('e=>e.contains(document.activeElement)'), 'Help traps Tab focus'
                page.keyboard.press('Escape')
                closed()
                assert trigger.evaluate('e=>e===document.activeElement')
            check('MIN-02', 'native Enter and Space, Escape focus return and Tab may leave help', keyboard)

            def dismiss():
                boot()
                first, second = button('calendar'), button('map')
                first.click()
                popup()
                first.click()
                closed()
                first.click()
                second.click()
                pop = popup()
                assert first.get_attribute('aria-expanded') == 'false' and second.get_attribute('aria-expanded') == 'true'
                assert page.locator('[data-mh=info-popover]:visible').count() == 1
                pop.click(position={'x': 5, 'y': 5})
                popup()
                page.locator('#outside').click()
                closed()
                assert page.locator('#outside').evaluate('e=>e===document.activeElement'), 'Outside click must keep its target focus'
                unchanged()
            check('MIN-03', 'own toggle, one help at a time, inside click retained, outside click closes', dismiss)

            def stability():
                boot()
                page.wait_for_function('__creates===1')
                button('calendar').click()
                pop = popup()
                pop.locator('[data-mh=info-close]').focus()
                page.evaluate('window.__pop=document.querySelector("[data-mh=info-popover]");window.__focus=document.activeElement;window.__cameraBefore=JSON.stringify(__camera);window.__updateBefore=JSON.stringify(__updates);window.__selected=document.querySelector("[data-mh=detail-title]").textContent;__now+=1000')
                page.wait_for_timeout(1150)
                assert page.evaluate('__pop===document.querySelector("[data-mh=info-popover]") && __pop.isConnected && document.activeElement===__focus'), 'Tick recreated help or discarded focused close control'
                assert page.evaluate('JSON.stringify(__camera)===__cameraBefore && JSON.stringify(__updates)===__updateBefore && document.querySelector("[data-mh=detail-title]").textContent===__selected'), 'Help/tick changed selection or camera within the same reference minute'
                page.keyboard.press('Escape')
                # Exercise the camera through its real controller callbacks. Help
                # open/close must not restart the approved 10-second deadline.
                page.evaluate('__options.onInteraction({type:"key"});window.__manualStart=performance.now()')
                page.wait_for_timeout(6000)
                button('map').click()
                popup()
                page.keyboard.press('Escape')
                page.wait_for_timeout(4200)
                assert page.evaluate('performance.now()-__manualStart>=10000 && __camera.at(-1)[0]==="location" && __camera.length>JSON.parse(__cameraBefore).length'), 'Opening help reset or cancelled the manual camera deadline'
                unchanged()
            check('MIN-04', 'tick retains help DOM/focus and help preserves selection, state and camera deadline', stability)

            def lifecycle():
                for hide, show in [
                    ('JPWMarketHours.deactivate()', 'JPWMarketHours.activate()'),
                    ('document.querySelector("#slot").hidden=true', 'document.querySelector("#slot").hidden=false'),
                    ('document.querySelector("#slot").inert=true', 'document.querySelector("#slot").inert=false'),
                    ('window.dispatchEvent(new Event("blur"))', 'window.dispatchEvent(new Event("focus"))'),
                    ('Object.defineProperty(document,"hidden",{configurable:true,value:true});document.dispatchEvent(new Event("visibilitychange"))', 'Object.defineProperty(document,"hidden",{configurable:true,value:false});document.dispatchEvent(new Event("visibilitychange"))'),
                ]:
                    boot()
                    button('calendar').click()
                    popup()
                    page.evaluate(hide)
                    page.wait_for_timeout(80)
                    closed()
                    page.evaluate(show)
                    page.wait_for_timeout(80)
                    closed()
                    button('map').click()
                    popup()
                    unchanged()
                page.evaluate('JPWMarketHours.dispose()')
                closed()
                assert page.locator('[data-mh=info-popover]').count() == 0, 'Dispose left an orphan help region in the global portal'
                page.evaluate('window.dispatchEvent(new Event("resize"));document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));document.querySelector("#outside").click()')
                assert page.locator('.market-hours').count() == 0
                boot(390)
                page.locator('[data-mh=map-toggle]').click()
                button('map').click()
                popup()
                page.locator('[data-mh=map-toggle]').click()
                closed()
            check('MIN-05', 'deactivate, hidden/inert dialog, blur, visibility and dispose close portal help', lifecycle)

            def containment():
                for width, scale, theme in [(390, 1, 'light'), (390, 1, 'dark'), (390, 2, 'light'), (1280, 1, 'dark')]:
                    boot(width, theme=theme)
                    if scale == 2:
                        page.evaluate('document.body.style.zoom="2";window.dispatchEvent(new Event("resize"))')
                    for kind in ['calendar', 'map']:
                        if kind == 'map' and page.locator('[data-mh=info-button][data-mh-help=map]').is_hidden():
                            page.locator('[data-mh=map-toggle]').click()
                        button(kind).click()
                        pop = popup()
                        assert pop.evaluate('e=>{const r=e.getBoundingClientRect();return r.left>=-1 && r.top>=-1 && r.right<=innerWidth+1 && r.bottom<=innerHeight+1 && e.scrollWidth<=e.clientWidth+1}'), 'Help escaped viewport or horizontally overflowed at ' + str((width, scale, theme, kind))
                        close = pop.locator('[data-mh=info-close]')
                        assert close.evaluate('e=>{const r=e.getBoundingClientRect();return r.width>0 && r.height>0 && r.left>=0 && r.right<=innerWidth+1 && r.top>=0 && r.bottom<=innerHeight+1}'), 'Help close control is not reachable within viewport'
                        path = out / ('help-' + kind + '-' + str(width) + '-scale' + str(scale) + '-' + theme + '.png')
                        page.screenshot(path=str(path), full_page=True)
                        result['screenshots'].append(str(path))
                        page.keyboard.press('Escape')
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'Help caused page horizontal overflow'
            check('MIN-06', 'help containment and close reachability on mobile, themes and CSS zoom 200 percent', containment)

            def content():
                boot()
                assert page.locator('[data-mh=summary]').inner_text() == '2 bolsas abertas agora'
                assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
                detail = page.locator('[data-mh=detail-title]').locator('xpath=ancestor::section[1]')
                assert 'São Paulo' in detail.inner_text() and 'Aberta' in detail.inner_text()
                assert page.locator('[data-mh=detail-time]').inner_text() == '12:00'
                assert 'Intervalo' in page.locator('[data-mh=next-transition]').inner_text()
                clock = page.locator('[data-mh=clock]')
                assert re.search(r'\b12:00\s*UTC\b', clock.inner_text()) and not re.search(r'\d{2}/\d{2}/\d{4}', clock.inner_text()), 'Reference should retain HH:mm UTC with full date in contextual help'
                for key in ['sources', 'schedules']:
                    assert not page.locator('[data-mh=' + key + ']').evaluate('e=>e.open'), 'Sources and schedule start collapsed'
                button('calendar').click()
                text = popup().inner_text()
                assert 'calendário' in text.lower() and re.search(r'cotaç|confirmação operacional', text, re.I)
                assert '15/10/2026' in text, 'Calendar help lost the full snapshot date'
                assert re.search(r'revis', text, re.I) and ('2026-10-15' in text or '15/10/2026' in text), 'Calendar help lost review metadata'
                page.keyboard.press('Escape')
                button('map').click()
                text = popup().inner_text()
                for word in ['meio-dia', 'aproximad', '10', 'marcador', '●', '◐', '○', '?']:
                    assert word in text.lower(), 'Map help lost contextual fact: ' + word
                page.keyboard.press('Escape')
                page.locator('[data-mh=sources] summary').click()
                assert page.locator('[data-mh=sources] a').count() > 0
                assert '2026-10-15' in page.locator('[data-mh=sources]').inner_text()
                unchanged()
            check('MIN-07', 'selected facts, single compact UTC reference, collapsed evidence and complete contextual facts', content)

            def empty_states():
                closed_catalog = 'for(const v of __catalog.venues)for(const g of v.groups)for(const p of g.periods){p.phase="closed";delete p.transitionWindow}'
                boot(before=closed_catalog)
                assert page.locator('[data-mh=summary]').inner_text() == 'Nenhuma bolsa aberta agora'
                assert page.locator('[data-mh=upcoming-empty]').is_visible()
                assert 'Nenhuma abertura confirmada' in page.locator('[data-mh=upcoming-empty]').inner_text()
                assert page.locator('[data-mh=empty]').is_hidden(), 'No open/upcoming sessions is not an unsuccessful search'
                page.locator('[data-mh=search]').fill('bolsa inexistente sintética')
                assert page.locator('[data-mh=empty]').is_visible(), 'An additional unmatched search needs its own empty message'
                page.locator('[data-mh=search]').fill('')
                assert page.locator('[data-mh=empty]').is_hidden()
                page.locator('[data-mh=phase-options] summary').click()
                page.locator('[data-mh=filter]').select_option('auction')
                assert page.locator('[data-mh=empty]').is_visible(), 'An additional phase restriction with no matches needs its own empty message'
                page.locator('[data-mh=filter]').select_option('all')
                page.locator('[data-mh-quick=unknown]').click()
                empty = page.locator('[data-mh=empty]')
                assert empty.is_hidden() or not re.search('pesquisa|filtros', empty.inner_text(), re.I), 'Zero unconfirmed sessions without an extra restriction must not claim unmatched search'
                boot(before=closed_catalog + ';__catalog.venues[0].groups[0].periods=[{startUtc:__now-86400000,endUtc:__now+3600000,phase:"closed",reason:"Antes da abertura sintética"},{startUtc:__now+3600000,endUtc:__now+86400000,phase:"continuous",reason:"Abertura sintética"}]')
                assert page.locator('[data-mh=summary]').inner_text() == 'Nenhuma bolsa aberta agora'
                assert page.locator('[data-mh=upcoming-empty]').is_hidden() and page.locator('[data-mh=empty]').is_hidden(), 'A confirmed future opening is not an empty open filter'
                assert page.locator('[data-venue-id=b3]').is_visible()
                assert page.locator('[data-venue-id=b3]').get_attribute('data-view-group') == 'upcoming'
                assert 'Abre' in page.locator('[data-venue-id=b3] .mh-next').inner_text()
                boot(before='__now+=172800000')
                assert page.locator('[data-mh=summary]').inner_text() == 'Nenhuma bolsa aberta agora'
                assert page.locator('[data-mh-quick=unknown]').inner_text() == 'Sem confirmação 5'
                assert page.locator('[data-mh=upcoming-empty]').is_visible() and page.locator('[data-mh=empty]').is_hidden()
                assert 'não confirmada' in page.locator('[data-mh=next-transition]').inner_text()
                page.locator('[data-mh-quick=unknown]').click()
                assert page.locator('[data-venue-id]:visible').count() == 5
            check('MIN-08', 'closed, unconfirmed, no upcoming and unmatched additional search remain truthful distinct states', empty_states)

            def compact_help_focus():
                boot()
                button('map').click()
                assert popup().evaluate('e=>e===document.activeElement || e.contains(document.activeElement)'), 'Opened help must own focus for this resize scenario'
                page.evaluate('document.querySelector("#slot").style.width="600px"')
                page.wait_for_timeout(120)
                closed()
                toggle = page.locator('[data-mh=map-toggle]')
                assert toggle.is_visible() and toggle.evaluate('e=>e===document.activeElement'), 'Closing portal help on compact map collapse must transfer focus to the visible map toggle'
            check('MIN-09', 'host-only resize closes focused map help and transfers focus to visible map toggle', compact_help_focus)

            def rounded_surface():
                # Oracle: approved user feedback rejects a square outer window.
                # Inspect rendered pixels and usable inset, not an exact CSS radius.
                samples = []
                for width, scale, theme in [(1280,1,'light'),(1280,1,'dark'),(390,1,'light'),(390,1,'dark'),(390,2,'light'),(390,2,'dark')]:
                    boot(width, theme=theme)
                    if scale == 2:
                        page.evaluate('document.body.style.zoom="2";window.dispatchEvent(new Event("resize"))')
                        page.wait_for_timeout(80)
                    panel = page.locator('.market-hours')
                    shot = panel.screenshot(animations='disabled')
                    pixels = page.evaluate("""src=>new Promise((resolve,reject)=>{
                      const image=new Image();image.onerror=()=>reject(new Error('Screenshot decode failed'));
                      image.onload=()=>{const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
                        const ctx=c.getContext('2d');ctx.drawImage(image,0,0);const w=c.width,h=c.height;
                        const at=(x,y)=>Array.from(ctx.getImageData(x,y,1,1).data).slice(0,3);
                        const corners=[at(1,1),at(w-2,1),at(1,h-2),at(w-2,h-2)];
                        const edges=[at(Math.floor(w/2),1),at(Math.floor(w/2),1),at(Math.floor(w/2),h-2),at(Math.floor(w/2),h-2)];
                        resolve({width:w,height:h,corners,edges,distances:corners.map((p,i)=>p.reduce((s,v,j)=>s+Math.abs(v-edges[i][j]),0))});};
                      image.src=src;
                    })""", 'data:image/png;base64,' + base64.b64encode(shot).decode())
                    samples.append({'width':width,'scale':scale,'theme':theme,**pixels})
                    result['surface_samples'] = samples
                    assert min(pixels['distances']) > 8, 'Painted outer corners remained square or were overpainted: ' + str(samples[-1])
                    assert panel.evaluate("""e=>{const r=e.getBoundingClientRect(),f=e.querySelector('.mh-filters').getBoundingClientRect();
                      return f.left-r.left>=4 && r.right-f.right>=4 && f.top-r.top>=4;}"""), 'Controls need visible inset from the outer window'
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'Rounded surface caused horizontal page overflow'
                    button('calendar').focus()
                    assert button('calendar').evaluate('e=>e===document.activeElement'), 'Surface must preserve keyboard focus'
                    unchanged()
                    path = out / ('surface-' + str(width) + '-scale' + str(scale) + '-' + theme + '.png')
                    page.screenshot(path=str(path), full_page=True)
                    result['screenshots'].append(str(path))
            check('MIN-10', 'painted rounded outer surface, usable inset and reflow across themes and zoom', rounded_surface)


            context.close()
            browser.close()
        result['status'] = 'PASS' if result['checks'] and not result['failures'] and not result['errors'] else 'PRODUCT_FAIL'
    except Exception:
        result['status'] = 'ENVIRONMENT_ERROR'
        result['errors'].append(traceback.format_exc())
    result['hashes'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                        for p in SOURCES + ['tools/market_hours_minimal_test.py', result['oracle']]}
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', help='Select case ID or behavior substring; no selection never passes')
    parser.add_argument('--out-dir', default='tools/.artifacts/market-hours/minimal-20261016/green')
    raise SystemExit(run(parser.parse_args()))

#!/usr/bin/env python3
"""Approved macOS composition: real DOM interactions and container lifecycle.
Oracles: CHG-JPW-MARKET-MACOS-20261016 / approved PROPOSTA.md, not CSS constants.
Synthetic calendar and instrumented renderer isolate behavioral failures; screenshots
use the shipped renderer with the same synthetic snapshot in both revisions.
"""
import argparse, hashlib, json, os, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from market_hours_redesign_test import ROOT, SOURCES, fixture_catalog


def run(args):
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    fixture=out/'fixture.html'
    fixture.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="'+(ROOT/SOURCES[-1]).as_uri()+'"></head><body style="display:block"><main style="padding:24px;min-width:0;max-width:1400px;margin:auto"><header style="position:static;display:block;height:auto;background:none;padding:0 0 20px;border:0"><h2 style="margin:0">Bolsas Globais</h2></header><div id="slot"></div></main>'+''.join('<script src="'+(ROOT/p).as_uri()+'"></script>' for p in SOURCES[:-1])+ '<script src="'+(ROOT/'src/vendor/aisol-dot-globe/aisol-globe.iife.js').as_uri()+'"></script>'+'''<script>
    window.__now=1792065600000;Date.now=()=>__now;
    window.__catalog='''+json.dumps(fixture_catalog())+''';
    window.__creates=0;window.__loads=0;window.__disposed=0;window.__active=[];window.__selects=[];
    window.__factory={create(h,o){__creates++;window.__options=o;const e=document.createElement('div');h.append(e);return {update(){},focusMarker(){},focusLocation(){},setActive(v){__active.push(v)},dispose(){__disposed++;e.remove()}}}};
    window.JPWMarketHoursAssets={getCatalog:()=>Promise.resolve(__catalog),getRenderer:()=>{__loads++;return Promise.resolve(__factory)}};
    const originalCreate=JPWMarketHoursView.create;
    window.JPWMarketHoursView={create(h,c,s,...rest){return originalCreate(h,c,(...args)=>{__selects.push(args);s(...args)},...rest)}};
    window.__mount=()=>{JPWMarketHours.mount(document.querySelector('#slot'));JPWMarketHours.activate()};
    </script></body></html>''')
    result={'status':'PRODUCT_FAIL','checks':[],'failures':[],'errors':[],'screenshots':[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',service_workers='block');context.set_offline(True)
        page=context.new_page();page.set_default_timeout(3000);page.on('pageerror',lambda e:result['errors'].append(str(e)))
        def boot(width=1440,host=None,theme='light',real=False):
            page.set_viewport_size({'width':width,'height':844 if width<800 else 1000});page.goto(fixture.as_uri())
            page.evaluate('({host,theme,real})=>{document.documentElement.dataset.theme=theme;if(host)document.querySelector("#slot").style.width=host+"px";if(real)__factory=JPWAisolGlobeRuntime}',dict(host=host,theme=theme,real=real))
            page.evaluate('__mount()');page.wait_for_selector('[data-venue-id=b3] button');page.wait_for_timeout(80)
        def check(name,fn):
            try:fn();result['checks'].append(name)
            except Exception:result['failures'].append({'case':name,'trace':traceback.format_exc()});page.screenshot(path=str(out/('failure-'+str(len(result['failures']))+'.png')),full_page=True)
        def row():
            boot();page.locator('[data-venue-id=nyse] .mh-local').click()
            assert page.locator('[data-mh=detail-title]').inner_text()=='NYSE','Clicking the hour must select its exchange'
            assert page.evaluate('__selects.length')==1
            for index,selector in enumerate(['[data-venue-id=b3] .mh-city','[data-venue-id=nyse] .mh-phase','[data-venue-id=b3] th','[data-venue-id=nyse] button'],2):
                page.locator(selector).click();assert page.evaluate('__selects.length')==index,'Every row click must select exactly once'
            page.locator('[data-venue-id=nyse] button').focus();page.keyboard.press('Enter');assert page.evaluate('__selects.length')==6
            page.keyboard.press('Space');assert page.evaluate('__selects.length')==7
            colors=page.locator('[data-venue-id=nyse]').evaluate('e=>[...e.children].map(c=>getComputedStyle(c).backgroundColor)')
            assert len(set(colors))==1 and colors[0] not in ['rgba(0, 0, 0, 0)','rgb(255, 255, 255)'],'Selection must cover every cell'
        check('entire row selects, native button selects once, keyboard works, full row highlight',row)
        def inspector():
            boot();title=page.locator('[data-mh=detail-title]').bounding_box();globe=page.locator('[data-mh=globe]').bounding_box()
            assert title['y']<globe['y'],'Selected exchange must precede map'
            assert page.locator('.mh-detail').inner_text().count('12:00')>=1,'Selected inspector must show local HH:mm'
        check('selected facts and local time precede globe',inspector)
        def container():
            boot(host=600)
            assert page.locator('[data-mh=globe]').is_hidden() and page.evaluate('__loads===0'),'Narrow host in wide viewport must start with lazy closed map'
            assert page.locator('.mh-inline-detail').evaluate('e=>e.previousElementSibling.dataset.venueId==="b3"')
            page.locator('[data-mh=search]').fill('B');page.locator('[data-mh=search]').evaluate('e=>{e.focus();e.setSelectionRange(1,1)}')
            page.evaluate('window.__row=document.querySelector("[data-venue-id=b3]");document.querySelector("#slot").style.width="1100px"');page.wait_for_timeout(120)
            assert page.evaluate('__creates===1') and page.locator('[data-mh=globe]').is_visible()
            assert page.locator('[data-mh=search]').evaluate('e=>e.value==="B" && e===document.activeElement && e.selectionStart===1')
            page.evaluate('document.querySelector("#slot").style.width="600px"');page.wait_for_timeout(120)
            assert page.locator('[data-mh=globe]').is_hidden() and page.evaluate('__active.at(-1)===false && __row===document.querySelector("[data-venue-id=b3]")')
            page.locator('[data-mh=map-toggle]').click();assert page.evaluate('__creates===1')
            page.evaluate('JPWMarketHours.dispose();document.querySelector("#slot").style.width="1100px"');page.wait_for_timeout(120)
            assert page.evaluate('__disposed===1') and page.locator('.market-hours').count()==0
        check('actual host width controls list-first mode, lazy renderer, state and observer cleanup',container)
        def mobile():
            boot(390);box=page.locator('[data-venue-id=b3]').bounding_box()
            assert box['y']+box['height']<500,'First exchange must be comfortably visible before fold'
            assert page.locator('[data-mh=globe]').is_hidden() and page.evaluate('__loads===0')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        check('mobile first exchange visible and no map work or horizontal overflow',mobile)
        def preserved_resize():
            boot()
            page.evaluate("JPWMarketHours.dispose()")
            # A fresh fixture permits a large synthetic list without changing product data.
            page.goto(fixture.as_uri());page.evaluate("for(let i=0;i<24;i++){const v=structuredClone(__catalog.venues[0]);v.id='extra-'+i;v.name='Bolsa '+i;__catalog.venues.push(v)};__mount()")
            page.wait_for_selector('[data-venue-id=b3] button')
            page.locator('[data-mh=sources] summary').click();page.locator('[data-mh=sources] a').focus()
            page.evaluate("window.__source=document.activeElement;window.__canvasHost=document.querySelector('[data-mh=globe]');document.querySelector('.mh-table-wrap').scrollTop=230")
            for width in [600,1100,600,1100]:
                page.evaluate('w=>document.querySelector("#slot").style.width=w+"px"',width);page.wait_for_timeout(100)
                assert page.evaluate('__source===document.activeElement && __source.isConnected'), 'Source focus must survive layout movement'
                assert page.locator('[data-mh=sources]').evaluate('e=>e.open')
                assert page.evaluate('__canvasHost===document.querySelector("[data-mh=globe]") && __creates===1')
            assert page.locator('.mh-table-wrap').evaluate('e=>e.scrollTop')==230,'Desktop list scroll must survive compact round trip'
        check('repeated host resize preserves source focus, disclosure, renderer and nonzero list scroll',preserved_resize)
        def inline_controls():
            boot(390);page.locator('[data-venue-id=nyse] .mh-city').click()
            page.locator('[data-mh=sources] summary').click()
            assert page.evaluate('__selects.length')==1,'Inline detail controls must not trigger row selection'
            assert page.locator('[data-mh=detail-title]').inner_text()=='NYSE'
        check('inline disclosure does not bubble into another selection',inline_controls)
        def narrow_zoom():
            boot(390);page.evaluate("const e=document.querySelector('.market-hours');e.style.width='155px';e.style.zoom='2';document.documentElement.dataset.fs='2'")
            assert page.locator('.market-hours').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            assert page.locator('[data-venue-id=b3] .mh-local').evaluate("e=>{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect(),c=e.getBoundingClientRect();return r.getClientRects().length===1 && b.left>=c.left && b.right<=c.right}"),'HH:mm must fit own cell at 155px and 200%'
        check('155px border-box at 200 percent contains local time and all content',narrow_zoom)
        if args.capture:
            for theme in ['light','dark']:
                for label,width,host in [('desktop',1440,None),('mobile',390,None),('narrow-host',1440,600)]:
                    boot(width,host,theme,True);page.wait_for_timeout(700)
                    path=out/(label+'-'+theme+'.png');page.screenshot(path=str(path),full_page=True);result['screenshots'].append(str(path))
        context.close();browser.close()
    result['status']='PASS' if result['checks'] and not result['failures'] and not result['errors'] else 'PRODUCT_FAIL'
    result['hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES+['tools/market_hours_macos_test.py']}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',default='tools/.artifacts/market-hours/macos-20261016/green');parser.add_argument('--capture',action='store_true');raise SystemExit(run(parser.parse_args()))

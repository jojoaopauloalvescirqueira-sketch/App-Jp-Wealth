#!/usr/bin/env python3
"""Synthetic UI acceptance for the approved four indicative FX centres plus separate B3."""
import argparse,json,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
result={'status':'PRODUCT_FAIL','checks':[],'errors':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce')
  page=context.new_page();page.on('pageerror',lambda e: result['errors'].append(str(e)))
  page.route('http://127.0.0.1:53339/**',lambda route:route.fulfill(content_type='text/html',body='<main><div id="slot"></div></main><div id="jpPopoverLayer"></div>'));page.goto('http://127.0.0.1:53339/synthetic')
  page.add_style_tag(content=(ROOT/'src/styles/app.css').read_text());page.add_style_tag(content='body{display:block}main{max-width:1200px;margin:auto;padding:16px;box-sizing:border-box}#slot{min-width:0;width:100%}')
  for path in ['01-sessions.js','03-view.js']:page.add_script_tag(content=(ROOT/'src/js/40-app/31-market-hours'/path).read_text())
  page.evaluate('([equities,fx])=>{window.__equities=JPWMarketSessions.prepare(equities);window.__fx=JPWForexSessions.prepare(fx);window.__now=Date.parse("2026-10-28T14:00:00Z");window.__view=JPWMarketHoursView.create(document.querySelector("#slot"),__equities,()=>{},()=>{},()=>{},{forexCatalog:__fx});__view.render(JPWMarketSessions.at(__equities,__now),"b3");}',[json.loads((ROOT/'src/data/market-hours/calendar-v1.json').read_text()),json.loads((ROOT/'src/data/market-hours/forex-sessions-v1.json').read_text())])
  assert page.locator('[data-fx-session]').count()==4,'Missing four indicative FX session rows'
  assert page.locator('[data-b3-session]').count()==1,'B3 must be a separate equity section'
  assert page.get_by_text('Sessões Forex · horários indicativos',exact=True).is_visible()
  assert page.locator('[data-mh=timezone]').is_visible()
  assert page.locator('[data-fx-session]').evaluate_all('(els)=>els.every(e=>e.getBoundingClientRect().height>=56)')
  result['checks'].append('four indicative centres, separate B3, timezone, row geometry')
  zone=page.locator('[data-mh=timezone]');zone.select_option('UTC');assert zone.input_value()=='UTC'
  page.get_by_role('button',name='Sobre as sessões Forex e B3').click();assert page.get_by_role('region',name='Sobre as sessões Forex e B3').is_visible();page.keyboard.press('Escape');assert page.get_by_role('button',name='Sobre as sessões Forex e B3').evaluate('(e)=>e===document.activeElement')
  result['checks'].append('timezone and contextual explanation keyboard lifecycle')
  for width in [320,390,768,1280]:
   page.set_viewport_size({'width':width,'height':900});page.wait_for_function('document.querySelector(".mh-sessions").dataset.compact===String(document.querySelector(".mh-sessions").clientWidth<600)');page.evaluate('__view.render(JPWMarketSessions.at(__equities,__now),"b3")')
   assert page.locator('[data-fx-session]').count()==4
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Overflow at {width}'
   page.screenshot(path=str(out/f'fx-{width}.png'),full_page=True)
  result['checks'].append('320/390/768/1280 no viewport overflow')
  page.evaluate("()=>{window.__originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error('quota fixture')};}")
  zone.select_option('Europe/London');assert zone.input_value()=='UTC'
  assert page.get_by_text('Não foi possível salvar o fuso. A preferência anterior foi preservada.',exact=True).is_visible()
  page.evaluate("Storage.prototype.setItem=window.__originalSet;__view.dispose();localStorage.setItem('jpwealth_market_sessions_view_v1','{invalid-record');window.__view=JPWMarketHoursView.create(document.querySelector('#slot'),__equities,()=>{},()=>{},()=>{},{forexCatalog:__fx});__view.render(JPWMarketSessions.at(__equities,__now),'b3')")
  assert page.locator('[data-mh=timezone]').is_disabled()
  assert page.evaluate("localStorage.getItem('jpwealth_market_sessions_view_v1')")=='{invalid-record'
  result['checks'].append('quota refusal preserves previous selection; corrupt preference stays opaque and is not rewritten')
  assert not result['errors'],result['errors']
  browser.close();result['status']='PASS'
except Exception as error:result['errors'].append(str(error))
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));raise SystemExit(result['status']!='PASS')

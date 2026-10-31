#!/usr/bin/env python3
"""Permanent review regressions: unknown, concurrent preference writes, delayed focus and measured new-view geometry."""
import argparse,json,math,os,tempfile,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
report={'status':'PRODUCT_FAIL','checks':[],'failures':[],'limits':['Synthetic profiles only; native Safari, physical touch and screen reader NOT_RUN.']}
equities=json.loads((ROOT/'src/data/market-hours/calendar-v1.json').read_text());fx=json.loads((ROOT/'src/data/market-hours/forex-sessions-v1.json').read_text())
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 def boot(context=None,zone='UTC',now='2026-10-28T14:00:00Z'):
  ctx=context or browser.new_context(viewport={'width':1280,'height':900},timezone_id=zone,reduced_motion='reduce');page=ctx.new_page()
  page.route('http://127.0.0.1:53339/**',lambda r:r.fulfill(content_type='text/html',body='<main><div id="slot"></div></main><div id="jpPopoverLayer"></div>'))
  page.goto('http://127.0.0.1:53339/synthetic');page.add_style_tag(content=(ROOT/'src/styles/app.css').read_text());page.add_style_tag(content='body{display:block}main{max-width:1200px;margin:auto;padding:16px;box-sizing:border-box}#slot{width:100%;min-width:0}')
  for path in ['01-sessions.js','03-view.js']:page.add_script_tag(content=(ROOT/'src/js/40-app/31-market-hours'/path).read_text())
  page.evaluate('([eq,fx,now])=>{window.__eq=JPWMarketSessions.prepare(eq);window.__fx=JPWForexSessions.prepare(fx);window.__now=Date.parse(now);window.__make=()=>{window.__v=JPWMarketHoursView.create(document.querySelector("#slot"),__eq,()=>{},()=>{},()=>{},{forexCatalog:__fx});__v.render(JPWMarketSessions.at(__eq,__now),"b3")};__make()}',[equities,fx,now]);return ctx,page
 def check(name,fn):
  try:fn();report['checks'].append(name)
  except Exception as e:report['failures'].append({'case':name,'error':str(e),'traceback':traceback.format_exc()})
 def unknown():
  ctx,page=boot(now='2027-01-05T12:00:00Z')
  try:
   text=page.locator('.mh-session-summary').inner_text();assert 'Horários não confirmados para esta data' in text,('expanded unknown misreported',text)
   page.evaluate('window.__o=JPWMarketHoursView.createOverview(document.querySelector("#slot"),()=>{},()=>{},()=>{},{forexCatalog:__fx});__o.render(JPWMarketSessions.at(__eq,__now))')
   text=page.locator('.mh-overview-shell').inner_text();assert 'Horários não confirmados para esta data' in text and '0 janelas' not in text,('collapsed unknown misreported',text)
   page.evaluate('__now=Date.parse("2025-12-31T22:00:00Z");__v.render(JPWMarketSessions.at(__eq,__now),"b3");__o.render(JPWMarketSessions.at(__eq,__now))')
   assert 'Cobertura parcial' in page.locator('.mh-session-summary').inner_text()
   assert 'Cobertura parcial' in page.locator('.mh-overview-shell').inner_text()
  finally:ctx.close()
 check('unknown and partial coverage stay distinct from known zero in expanded/collapsed view',unknown)
 def changed_invalid():
  for raw in ['{"schemaVersion":2,"timeZone":"UTC"}','{corrupt']:
   ctx,page=boot()
   try:
    page.evaluate('(raw)=>localStorage.setItem(JPWMarketSessionsViewPreference.key,raw)',raw)
    page.locator('[data-mh=timezone]').select_option('Europe/London')
    assert page.evaluate('localStorage.getItem(JPWMarketSessionsViewPreference.key)')==raw,'Post-mount invalid preference overwritten'
    assert page.locator('[data-mh=timezone]').is_disabled()
   finally:ctx.close()
 check('future/corrupt preference introduced after mount remains opaque and blocks writes',changed_invalid)
 def changed_valid():
  ctx,page=boot()
  try:
   raw='{"schemaVersion":1,"timeZone":"Europe/London"}'
   page.evaluate('(raw)=>localStorage.setItem(JPWMarketSessionsViewPreference.key,raw)',raw)
   page.locator('[data-mh=timezone]').select_option('Asia/Tokyo')
   assert page.evaluate('localStorage.getItem(JPWMarketSessionsViewPreference.key)')==raw,'Concurrent valid preference overwritten'
   assert page.locator('[data-mh=timezone]').input_value()=='Europe/London'
   assert 'outra aba' in page.locator('.mh-sessions').inner_text()
  finally:ctx.close()
 check('expected raw rejects a concurrent valid preference instead of silent overwrite',changed_valid)
 def readback():
  for raw in ['{concurrent-corruption','{"schemaVersion":1,"timeZone":"Europe/London"}']:
   ctx,page=boot()
   try:
    page.evaluate("(raw)=>{window.__set=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){__set.call(this,k,v);if(k===JPWMarketSessionsViewPreference.key)__set.call(this,k,raw)}}",raw)
    page.locator('[data-mh=timezone]').select_option('Asia/Tokyo')
    assert page.evaluate('localStorage.getItem(JPWMarketSessionsViewPreference.key)')==raw
    if raw.startswith('{concurrent'):
     assert page.locator('[data-mh=timezone]').is_disabled(),'Readback failed to detect post-write incompatible record'
    else:
     assert page.locator('[data-mh=timezone]').input_value()=='Europe/London'
     assert not page.locator('[data-mh=timezone]').is_disabled()
    assert 'preservado' in page.locator('.mh-sessions').inner_text()
   finally:ctx.close()
 check('readback detects competing valid/invalid writes without rollback over the other record',readback)
 def focus():
  ctx,page=boot()
  try:
   page.evaluate('__v.dispose();window.__onbShown=true;window.__assets={getCatalog:()=>new Promise(r=>window.__release=()=>r(__eq)),getForexCatalog:()=>Promise.resolve(__fx),getRenderer:()=>Promise.reject(Error("not requested"))};window.JPWMarketHoursAssets=__assets')
   page.add_script_tag(content=(ROOT/'src/js/40-app/31-market-hours/04-controller.js').read_text())
   page.evaluate('window.__load=JPWMarketHours.mount(document.querySelector("#slot"),{collapsed:true});JPWMarketHours.activate()')
   page.wait_for_function('typeof __release==="function"');button=page.locator('[data-mh=expansion-toggle]');button.focus();page.evaluate('__release()');page.evaluate('()=>__load')
   assert page.locator('[data-mh=expansion-toggle]').evaluate('(e)=>e===document.activeElement && !!e.getClientRects().length'),'Catalog completion removed the focused overview action'
  finally:ctx.close()
 check('delayed catalog completion preserves focused keyboard overview action',focus)
 def device():
  for zone in ['Europe/Paris','Asia/Kolkata']:
   ctx,page=boot(zone=zone)
   try:
    resolved=page.evaluate('Intl.DateTimeFormat().resolvedOptions().timeZone')
    assert resolved in page.locator('.mh-sessions-list').inner_text()
    expected='15:00' if zone=='Europe/Paris' else '19:30'
    assert expected in page.locator('.mh-sessions-list').inner_text()
    day=page.evaluate('(zone)=>JPWForexSessions.timeline(__fx,__now,zone,{device:true})',resolved)
    if zone=='Asia/Kolkata':assert day['ticks'][0]['offset']=='+0530' and day['fromUtc']==1793125800000
    page.locator('[data-mh=timezone]').select_option('device')
    assert page.evaluate('JSON.parse(localStorage.getItem(JPWMarketSessionsViewPreference.key)).timeZone')=='device'
    assert 'Exibindo UTC' not in page.locator('.mh-sessions').inner_text()
   finally:ctx.close()
  ctx,page=boot()
  try:
   page.evaluate("()=>{const Native=Intl.DateTimeFormat;Intl.DateTimeFormat=function(locale,options){if(arguments.length===0)return {resolvedOptions:()=>({timeZone:'Invalid/Zone'})};return new Native(locale,options)};__v.dispose();__make()}")
   assert 'Exibindo UTC' in page.locator('.mh-sessions').inner_text()
   assert 'não reconhecido' in page.locator('.mh-sessions').inner_text()
   assert '· UTC ·' in page.locator('.mh-sessions-list').inner_text()
   assert page.evaluate('localStorage.getItem(JPWMarketSessionsViewPreference.key)') is None
  finally:ctx.close()
 check('device IANA Paris/Kolkata uses real civil timezone; only invalid Intl zone falls back explicitly to UTC',device)
 def lifecycle():
  ctx,page=boot()
  try:
   page.evaluate("()=>{__v.dispose();const engine=JPWMarketSessions;window.__snapshots=0;window.JPWMarketSessions=Object.freeze({...engine,at(...args){__snapshots++;return engine.at(...args)}});window.JPWMarketHoursAssets={getCatalog:()=>Promise.resolve(__eq),getForexCatalog:()=>Promise.resolve(__fx),getRenderer:()=>Promise.reject(Error('synthetic renderer unavailable'))}}")
   page.add_script_tag(content=(ROOT/'src/js/40-app/31-market-hours/04-controller.js').read_text())
   page.evaluate('window.__load=JPWMarketHours.mount(document.querySelector("#slot"));JPWMarketHours.activate()');page.evaluate('()=>__load')
   page.wait_for_selector('[data-fx-session]')
   page.evaluate('document.querySelector("#slot").hidden=true');page.wait_for_timeout(80);before=page.evaluate('__snapshots');page.wait_for_timeout(1100);assert page.evaluate('__snapshots')==before,'Hidden new view kept updating'
   page.evaluate('document.querySelector("#slot").hidden=false');page.wait_for_function('(before)=>__snapshots>before',arg=before)
   page.evaluate("dispatchEvent(new Event('blur'))");before=page.evaluate('__snapshots');page.wait_for_timeout(1100);assert page.evaluate('__snapshots')==before,'Blurred new view kept updating'
   page.evaluate("dispatchEvent(new Event('focus'))");page.wait_for_function('(before)=>__snapshots>before',arg=before)
   page.evaluate('JPWMarketHours.deactivate()');before=page.evaluate('__snapshots');page.wait_for_timeout(1100);assert page.evaluate('__snapshots')==before
   page.evaluate('JPWMarketHours.activate()');page.wait_for_function('(before)=>__snapshots>before',arg=before)
   page.evaluate('JPWMarketHours.dispose();JPWMarketHours.activate()');before=page.evaluate('__snapshots');page.wait_for_timeout(1100);assert page.evaluate('__snapshots')==before and page.locator('.mh-sessions').count()==0
  finally:ctx.close()
 check('new-view controller pauses hidden/blur/deactivated, resumes focus, and dispose is terminal',lifecycle)
 def geometry(page):
  measurements=page.locator('[data-fx-session]').evaluate_all('''els=>els.map(e=>{const b=e.querySelector('button'),flag=e.querySelector('.mh-session-flag'),track=e.querySelector('.mh-session-track'),now=e.querySelector('.mh-session-now');const r=b.getBoundingClientRect(),f=flag.getBoundingClientRect(),t=track.getBoundingClientRect(),n=now.getBoundingClientRect();return {row:e.getBoundingClientRect().height,flag:f.width,flagH:f.height,track:t.height,now:n.width,targetW:r.width,targetH:r.height,flagCenterDelta:Math.abs((f.top+f.height/2)-(r.top+r.height/2)),nowCenterDelta:Math.abs((n.top+n.height/2)-(t.top+t.height/2))}})''')
  assert all(m['row']>=56 and abs(m['flag']-24)<=2 and abs(m['flagH']-24)<=2 and abs(m['track']-12)<=2 and abs(m['now']-2)<=.1 and m['targetW']>=44 and m['targetH']>=44 and m['flagCenterDelta']<=2 and m['nowCenterDelta']<=2 for m in measurements),measurements
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert page.locator('.mh-sessions').evaluate('root=>Array.from(root.querySelectorAll("button,select")).filter(e=>e.getClientRects().length).every(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44})'),'A visible interactive target is smaller than44px'
  return measurements
 def visuals():
  ctx,page=boot()
  try:
   report['measurements']=[]
   for theme in ['light','dark']:
    page.evaluate('(t)=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
    for width in [320,390,768,1280]:
     page.set_viewport_size({'width':width,'height':900});page.wait_for_function('document.querySelector(".mh-sessions").dataset.compact===String(document.querySelector(".mh-sessions").clientWidth<600)')
     report['measurements'].append({'theme':theme,'width':width,'rows':geometry(page)})
     page.screenshot(path=str(out/f'review-{theme}-{width}.png'),full_page=True)
   page.locator('.mh-session-flag').first.evaluate("e=>{e.style.width='32px';e.style.flexBasis='32px'}")
   rejected=False
   try:geometry(page)
   except AssertionError:rejected=True
   assert rejected,'The same geometry oracle accepted an oversized flag'
   page.locator('.mh-session-flag').first.evaluate("e=>{e.style.removeProperty('width');e.style.removeProperty('flex-basis')}")
   page.set_viewport_size({'width':390,'height':900});page.wait_for_selector('[data-mh=map-toggle]:visible');toggle=page.locator('[data-mh=map-toggle]');toggle.focus();page.set_viewport_size({'width':1280,'height':900});page.wait_for_function('document.querySelector("[data-mh=map-toggle]").hidden');assert page.locator('[data-mh=timezone]').evaluate('(e)=>e===document.activeElement')
   page.get_by_role('button',name='Sobre as sessões Forex e B3').click();page.evaluate('__v.setExpanded(false)');assert page.get_by_role('region',name='Sobre as sessões Forex e B3').count()==0
   page.evaluate('__v.setExpanded(true);__v.dispose()');assert page.locator('.mh-sessions').count()==0
  finally:ctx.close()
 check('2px alignment, flag24/track12/now2, targets44, light/dark and keyboard cleanup of new view',visuals)
 def help_geometry(page):
  page.get_by_role('button',name='Sobre as sessões Forex e B3').click()
  help=page.get_by_role('region',name='Sobre as sessões Forex e B3')
  targets=help.locator('a,button,input,select,textarea,[tabindex]').evaluate_all('''els=>els.filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,text:e.textContent,width:r.width,height:r.height}})''')
  assert targets and any(t['tag']=='A' for t in targets) and any(t['tag']=='BUTTON' for t in targets)
  assert all(t['width']>=44 and t['height']>=44 for t in targets),targets
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Help causes horizontal overflow'
  help.get_by_role('link').focus();page.keyboard.press('Escape')
  assert page.get_by_role('region',name='Sobre as sessões Forex e B3').count()==0
  assert page.get_by_role('button',name='Sobre as sessões Forex e B3').evaluate('(e)=>e===document.activeElement')
  return targets
 def help_targets():
  ctx,page=boot()
  try:
   report['helpMeasurements']=[]
   for theme in ['light','dark']:
    page.evaluate('(t)=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
    for width in [320,390,768,1280]:
     page.set_viewport_size({'width':width,'height':900})
     targets=help_geometry(page)
     report['helpMeasurements'].append({'theme':theme,'width':width,'targets':targets})
  finally:ctx.close()
 check('help layer links and controls outside sessions root have 44px targets in both themes and four widths',help_targets)
 def native():
  with tempfile.TemporaryDirectory(prefix='fx-native200-') as folder:
   profile=Path(folder);(profile/'Default').mkdir();(profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
   ctx=pw.chromium.launch_persistent_context(folder,headless=True,no_viewport=True,executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),args=['--window-size=1440,1000'],reduced_motion='reduce')
   try:
    _,page=boot(ctx);actual=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})');assert abs(actual['outer']/actual['inner']-2)<.01 and actual['css']=='1',actual
    report['native200']=actual;report['nativeMeasurements']=[];report['nativeHelpMeasurements']=[]
    for theme in ['light','dark']:
     page.evaluate('(t)=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme);report['nativeMeasurements'].append({'theme':theme,'rows':geometry(page)});page.screenshot(path=str(out/f'native200-{theme}.png'),full_page=True);report['nativeHelpMeasurements'].append({'theme':theme,'targets':help_geometry(page)})
   finally:ctx.close()
 check('native browser zoom200 in isolated headless profile, both themes',native)
 browser.close()
report['status']='PASS' if not report['failures'] else 'PRODUCT_FAIL';(out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));raise SystemExit(report['status']!='PASS')

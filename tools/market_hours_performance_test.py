#!/usr/bin/env python3
"""Observe real globe draw cadence/selection latency; no performance gain claim."""
import argparse,json,time,hashlib,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from galton_board_test import serve,prepare_page
from research_navigation_test import launch_browser
ROOT=Path(__file__).resolve().parents[1]
def percentile(values,q):return sorted(values)[min(len(values)-1,int((len(values)-1)*q))]
def run(out_dir='tools/.artifacts/market-hours/performance'):
 out=ROOT/out_dir;out.mkdir(parents=True,exist_ok=True)
 report={'status':'NOT_RUN','environment':'headless Chromium; native WebGL backend reported below; desktop1440x900 DPR2; reduced_motion=reduce; automatic rotation off; OS shader cache not reset'}
 server,url=serve()
 try:
  with sync_playwright() as p:
   browser=launch_browser(p)
   try:
    page=prepare_page(browser,url)
    try:
     page.evaluate('''()=>{window.__mhDraws=[];window.__mhLatency=[];window.__mhRequest=null;const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){const gl=get.call(this,type,...args);if(type==='webgl2'&&gl&&!gl.__mhProbe){gl.__mhProbe=true;const clear=gl.clear.bind(gl);gl.clear=(...v)=>{const t=performance.now();__mhDraws.push(t);if(__mhRequest!==null){__mhLatency.push(t-__mhRequest);__mhRequest=null;}return clear(...v);};}return gl;};}''')
     # Freeze wall time between reference updates; monotonic interaction timing remains real.
     page.evaluate('window.__mhWall=Date.now();Date.now=()=>__mhWall')
     started=time.perf_counter();assert page.evaluate("JPWNavigation.navigate('tools-market-hours')")
     page.wait_for_selector('.jpw-aisol-root[data-state="ready"]');page.wait_for_function('__mhDraws.length>0')
     report['coldEntryMs']=(time.perf_counter()-started)*1000
     report['renderer']=page.evaluate('''()=>{const gl=document.querySelector('.jpw-aisol-root canvas').getContext('webgl2');const ext=gl.getExtension('WEBGL_debug_renderer_info');return ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)}''')
     page.mouse.move(1,1);page.wait_for_timeout(250)
     before=page.evaluate('__mhDraws.length');page.wait_for_timeout(5000)
     report['idleDraws5s']=page.evaluate('__mhDraws.length')-before
     assert report['idleDraws5s']==0,report
     # Selection benchmark requires both venues regardless of their current market phases.
     page.locator('[data-mh-quick=all]').click()
     # Timestamp the actual button click, then first subsequent WebGL render.
     page.evaluate('''()=>{document.querySelector('.market-hours').addEventListener('click',e=>{if(e.target.closest('[data-venue-id] button'))__mhRequest=performance.now();},true);}''')
     for i in range(30):
      page.locator('[data-venue-id="'+('nyse' if i%2 else 'b3')+'"] button').click()
      page.wait_for_function('(n)=>__mhLatency.length>=n',arg=i+1)
     latency=page.evaluate('__mhLatency');report['selectionMs']={'samples':len(latency),'median':percentile(latency,.5),'p95':percentile(latency,.95)}
     globe=page.locator('.jpw-aisol-root');box=globe.bounding_box();page.mouse.move(box['x']+box['width']*.4,box['y']+box['height']*.5);page.wait_for_timeout(200)
     index=page.evaluate('__mhDraws.length');page.mouse.down()
     for i in range(45):page.mouse.move(box['x']+box['width']*(.4+.25*i/44),box['y']+box['height']*.5);page.wait_for_timeout(16)
     page.mouse.up();draws=page.evaluate('__mhDraws.slice('+str(index)+')');intervals=[b-a for a,b in zip(draws,draws[1:]) if b-a>1]
     report['dragFrameIntervalMs']={'samples':len(intervals),'median':percentile(intervals,.5),'p95':percentile(intervals,.95)}
     page.screenshot(path=str(out/'desktop.png'),animations='disabled')
     assert page.evaluate("JPWNavigation.navigate('dashboard')");page.wait_for_timeout(150)
     before=page.evaluate('__mhDraws.length');page.wait_for_timeout(5000);report['hiddenDraws5s']=page.evaluate('__mhDraws.length')-before;assert report['hiddenDraws5s']==0
     # Freeze wall time between reference updates; monotonic interaction timing remains real.
     page.evaluate('window.__mhWall=Date.now();Date.now=()=>__mhWall')
     started=time.perf_counter();assert page.evaluate("JPWNavigation.navigate('tools-market-hours')");page.wait_for_selector('.market-hours');report['warmEntryMs']=(time.perf_counter()-started)*1000
     page.set_viewport_size({'width':390,'height':844});page.evaluate('document.documentElement.style.zoom=1.25;window.dispatchEvent(new Event("resize"));window.visualViewport?.dispatchEvent(new Event("resize"))');page.wait_for_timeout(150);page.screenshot(path=str(out/'mobile.png'),animations='disabled')
     page.evaluate("window.__retainedRoot=document.querySelector('.jpw-aisol-root');window.__retainedCanvas=__retainedRoot.querySelector('canvas')")
     toggle=page.locator('[data-mh="map-toggle"]')
     if toggle.get_attribute('aria-expanded')=='true':toggle.click()
     assert page.locator('[data-mh="map-content"]').is_hidden()
     page.wait_for_timeout(150)
     before=page.evaluate('__mhDraws.length');page.wait_for_timeout(5000)
     report['collapsedMobileDraws5s']=page.evaluate('__mhDraws.length')-before
     assert report['collapsedMobileDraws5s']==0,report
     original=page.locator('[data-mh="detail-title"]').inner_text()
     toggle.click();page.wait_for_selector('[data-mh="map-content"]',state='visible')
     assert page.locator('.jpw-aisol-root').count()==1 and page.locator('[data-mh="detail-title"]').inner_text()==original
     assert page.evaluate("__retainedRoot===document.querySelector('.jpw-aisol-root') && __retainedCanvas===__retainedRoot.querySelector('canvas')"), 'collapse/reopen replaced renderer or canvas'
     page.wait_for_timeout(150)
     draws=page.evaluate('__mhDraws.length')
     page.locator('[data-venue-id="b3"] button').click()
     page.wait_for_function('(n)=>__mhDraws.length>n',arg=draws)
     assert page.locator('[data-mh="detail-title"]').inner_text()=='B3'
     report['expandedInteractionDraws']=page.evaluate('__mhDraws.length')-draws
     report['rendererAndCanvasRetained']=True
     report['targetSelectionP95Met']=report['selectionMs']['p95']<=100
     report['targetDragP95Met']=report['dragFrameIntervalMs']['p95']<=33.3
     report['status']='PASS' if report['targetSelectionP95Met'] and report['targetDragP95Met'] else 'PRODUCT_FAIL'
     assert not page.jpwealth_observed['pageerror'],page.jpwealth_observed['pageerror']
    finally:page.jpwealth_context.close()
   finally:browser.close()
 except AssertionError as error:report['status']='PRODUCT_FAIL';report['error']=str(error)
 except Exception as error:report['status']='ENVIRONMENT_ERROR';report['error']=str(error)
 finally:
  server.shutdown();server.server_close();report['sourceHashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['build-id.js','src/js/40-app/31-market-hours/04-controller.js','src/vendor/aisol-dot-globe/aisol-globe.iife.js']};(out/'result.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(report,ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out-dir',default='tools/.artifacts/market-hours/performance')
 raise SystemExit(run(parser.parse_args().out_dir))

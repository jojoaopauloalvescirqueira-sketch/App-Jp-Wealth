#!/usr/bin/env python3
"""Real-byte download matrix; synthetic app state; isolated browser contexts."""
import argparse, hashlib, json, shutil, tempfile, threading, time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--browser');p.add_argument('--out-dir',default='tools/.artifacts/download-assets');args=p.parse_args()
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True);checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
# Observe the actual async click handlers without replacing their dependencies.
# Completion is awaited after the held real resource has finished and passed SHA.
HANDLER_PROBE = r"""(() => {
  window.__downloadHandlers=[];
  const add=EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener=function(type,listener,options){
    if(type==='click'&&typeof listener==='function'&&this instanceof Element&&
      (this.id==='nocudaEditable'||this.matches('[data-nocuda-file]'))){
      const original=listener;
      listener=function(...args){
        const record={settled:false,async:false};window.__downloadHandlers.push(record);
        const result=original.apply(this,args);record.async=!!result?.then;
        record.completion=Promise.resolve(result).then(()=>{record.settled=true},error=>{record.settled=true;record.error=String(error)});
        return result;
      };
    }
    return add.call(this,type,listener,options);
  };
})();"""
RESOURCE_PATTERN='**/downloads/nocuda/Nocuda_Tool.pine'
def hold_action(page,selector):
    held=[]
    page.route(RESOURCE_PATTERN,lambda route:held.append(route))
    page.locator(selector).click()
    deadline=time.monotonic()+10
    while not held and time.monotonic()<deadline:
        page.wait_for_timeout(10)  # Pump browser events until the intercepted request exists.
    assert len(held)==1,'Action did not request the real resource'
    state=page.evaluate("__downloadHandlers.map(r=>({async:r.async,settled:r.settled}))")
    assert state==[{'async':True,'settled':False}],state
    # A second, uncancelled consumer shares the UI resource job. Its bytes prove
    # transport, arrayBuffer, integrity validation and the loader promise finished.
    page.evaluate("window.__sharedResource=JPWDownloadAssets.getBytes('nocuda/Nocuda_Tool.pine');void 0")
    return held[0]
def finish_action(page,route,scenario):
    with page.expect_request_finished(lambda request:request.url.endswith('/downloads/nocuda/Nocuda_Tool.pine')):
        route.fulfill(path=str(ROOT/'downloads/nocuda/Nocuda_Tool.pine'))
    result=page.evaluate("""async()=>{
      const bytes=await __sharedResource;
      await Promise.all(__downloadHandlers.map(r=>r.completion));
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      await new Promise(r=>setTimeout(r,0));
      return {bytes:Array.from(bytes),handlers:__downloadHandlers.map(r=>({async:r.async,settled:r.settled,error:r.error||null}))};
    }""")
    check(scenario+' real resource completes with original bytes',bytes(result['bytes'])==(ROOT/'downloads/nocuda/Nocuda_Tool.pine').read_bytes())
    check(scenario+' actual action handler settled',result['handlers']==[{'async':True,'settled':True,'error':None}])

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
portable=ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
with tempfile.TemporaryDirectory(prefix='jpw-portable-downloads-') as directory, sync_playwright() as pw:
    detached=Path(directory)/'standalone.html';shutil.copyfile(portable,detached)
    opts=launch_options()
    if args.browser:opts['executable_path']=args.browser
    browser=pw.chromium.launch(**opts)
    try:
      for mode,target in [('http',base+'/index.html'),('file',(ROOT/'index.html').as_uri()),('portable-file',detached.as_uri()),('portable-http',base+'/dist/'+portable.name),('pwa-offline',base+'/index.html')]:
        ctx=browser.new_context(service_workers='allow' if mode=='pwa-offline' else 'block',accept_downloads=True)
        install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true;window.__downloadDecodes=0;const original=window.atob;window.atob=function(v){window.__downloadDecodes++;return original(v)};')
        page=ctx.new_page();errors=[];requests=[];page.on('pageerror',lambda error:errors.append(str(error)));page.on('request',lambda request:requests.append(request.url))
        page.goto(target);wait_bootstrap(page);page.evaluate('closeModal();S.onboarding.done=true')
        page.evaluate("JPWNavigation.navigate('tools-nocuda')")
        check(mode+' zero download transport before action',not any('/src/vendor/downloads/' in u or '/downloads/nocuda/' in u or u.endswith('.zip') for u in requests) if mode!='pwa-offline' else True)
        before=page.evaluate('window.__downloadDecodes');check(mode+' zero base64 decode before action',before==0)
        if mode=='pwa-offline':
            page.evaluate('navigator.serviceWorker.ready');page.reload();wait_bootstrap(page)
            page.wait_for_function('navigator.serviceWorker.controller!==null');ctx.set_offline(True);page.reload();wait_bootstrap(page);page.evaluate("closeModal();JPWNavigation.navigate('tools-nocuda')")
        # Every listed NoCuda file must be the exact original, not only a resolved Promise.
        for name in ['Nocuda_Tool.pine','Nocuda_Tool.mq5','Nocuda_Tool.ex5','TRADINGVIEW-LEIA-ME.md','MT5-LEIA-ME.md']:
            with page.expect_download() as info:page.locator('[data-nocuda-file="'+name+'"]').click()
            artifact=info.value;check(mode+' filename '+name,artifact.suggested_filename==name)
            check(mode+' original bytes '+name,Path(artifact.path()).read_bytes()==(ROOT/'downloads/nocuda'/name).read_bytes())
        source=page.evaluate("async()=>await JPWTools.generateEditable(null,JPWNocudaTransfer.example())")
        check(mode+' awaited editable content','const bool PRECONFIGURED = true // NOCUDA_PRECONFIGURED' in source)
        page.evaluate("JPWNavigation.navigate('tools-leverage')")
        page.evaluate("JPWTools.genetrix.open('install');document.querySelectorAll('#jpwLeveragePage details').forEach(n=>n.open=true)")
        metadata=page.evaluate('JPW_LEVERAGE_MANIFEST.downloads')
        for kind,entry in metadata.items():
            if not entry['available']:continue
            with page.expect_download() as info:page.locator('[data-jpw-leverage-download="'+kind+'"]:visible').first.click()
            artifact=info.value;check(mode+' original ZIP '+kind,hashlib.sha256(Path(artifact.path()).read_bytes()).hexdigest()==entry['sha256'])
        check(mode+' no runtime errors',not errors);ctx.close()
      # Hold the response until navigation/invalidation happened, then release
      # it and await both the real resource and the actual UI async handler.
      for scenario in ['navigation','hash','size','draft-reset','draft-clear','draft-input','session','pagehide']:
        ctx=browser.new_context(service_workers='block',accept_downloads=True);install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true;');ctx.add_init_script(HANDLER_PROBE)
        page=ctx.new_page();page.goto(base+'/index.html');wait_bootstrap(page)
        page.evaluate("closeModal();S.onboarding.done=true;JPWNavigation.navigate('tools-nocuda');document.getElementById('nocudaExample').click()")
        downloaded=[];page.on('download',lambda value:downloaded.append(value))
        if scenario in ['hash','size']:
            raw=(ROOT/'downloads/nocuda/Nocuda_Tool.pine').read_bytes()
            corrupt=(bytes([raw[0]^1])+raw[1:]) if scenario=='hash' else raw+b'x'
            page.route(RESOURCE_PATTERN,lambda route:route.fulfill(body=corrupt))
            page.locator('[data-nocuda-file="Nocuda_Tool.pine"]').click()
            page.wait_for_function("document.getElementById('nocudaStatus').dataset.state==='error'")
            page.evaluate("async()=>await Promise.all(__downloadHandlers.map(r=>r.completion))")
            check(scenario+' mismatch blocks real download',not downloaded)
        else:
            selector='[data-nocuda-file="Nocuda_Tool.pine"]' if scenario=='navigation' else '#nocudaEditable'
            held=hold_action(page,selector)
            if scenario=='navigation':
                page.evaluate("JPWNavigation.navigate('tools-calendar')")
                check('navigation accepted before resource completes',page.evaluate("JPWNavigation.current().canonical==='tools-calendar'"))
            elif scenario=='draft-clear':page.locator('#nocudaClear').click()
            elif scenario=='draft-input':page.locator('#nocudaPayload').fill('SYN changed draft')
            else:
                mutation={'draft-reset':"jpwWorkspaceDraftProviders.get('nocuda-transfer')(true)",
                          'session':"sessionEpochRotate()",'pagehide':"window.dispatchEvent(new Event('pagehide'))"}[scenario]
                page.evaluate(mutation)
            baseline_status=page.locator('#nocudaStatus').inner_text()
            finish_action(page,held,scenario)
            check(scenario+' blocks late action after completion',not downloaded)
            check(scenario+' blocks late status after completion',page.locator('#nocudaStatus').inner_text()==baseline_status)
        ctx.close()
      for scenario in ['transport-retry','transport-timeout']:
        ctx=browser.new_context(service_workers='block');install_bootstrap(ctx);page=ctx.new_page();page.goto(base+'/index.html');wait_bootstrap(page)
        if scenario=='transport-retry':page.route('**/downloads/nocuda/Nocuda_Tool.pine',lambda route:route.abort())
        else:
            held=[]
            page.route('**/downloads/nocuda/Nocuda_Tool.pine',lambda route:held.append(route))
            page.evaluate("window.__originalTimeout=window.setTimeout;window.setTimeout=(fn,ms,...args)=>window.__originalTimeout(fn,ms===15000?20:ms,...args)")
        failed=page.evaluate("async()=>{try{await JPWDownloadAssets.getBytes('nocuda/Nocuda_Tool.pine');return false}catch(e){return true}}")
        check(scenario+' rejects initial attempt',failed)
        if scenario=='transport-timeout':
            for route in held:route.abort()
        page.unroute('**/downloads/nocuda/Nocuda_Tool.pine')
        page.evaluate("if(window.__originalTimeout)window.setTimeout=window.__originalTimeout")
        result=page.evaluate("async()=>Array.from(await JPWDownloadAssets.getBytes('nocuda/Nocuda_Tool.pine'))")
        check(scenario+' next action returns original bytes',bytes(result)==(ROOT/'downloads/nocuda/Nocuda_Tool.pine').read_bytes());ctx.close()
    finally:browser.close();server.shutdown()
(out/'result.json').write_text(json.dumps({'checks':checks,'count':len(checks)},indent=2));print('PASS',len(checks),'download browser checks')

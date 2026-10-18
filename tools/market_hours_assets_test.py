#!/usr/bin/env python3
"""Exercise lazy verified market assets through real browser transports."""
import argparse,hashlib,json,os,shutil,sys,tempfile,threading,traceback
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BROWSER=os.environ.get('JP_WEALTH_CHROMIUM') or None
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--out-dir',default='tools/.artifacts/market-hours/assets');a=p.parse_args();out=ROOT/a.out_dir;out.mkdir(parents=True,exist_ok=True)
    report={'status':'NOT_RUN','checks':[],'scope':'real browser, synthetic public catalog, HTTP/file/portable payload'}
    try:
      with tempfile.TemporaryDirectory(prefix='jpw-market-assets-') as tmp,sync_playwright() as pw:
        base=Path(tmp)
        paths={'catalog':'src/data/market-hours/calendar-v1.json','renderer':'src/vendor/aisol-dot-globe/aisol-globe.iife.js'}
        resources={}
        for key,path in paths.items():
          data=(ROOT/path).read_bytes();target=base/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);resources[key]={'path':path,'bytes':len(data),'sha256':sha(data)}
        metadata={'schemaVersion':1,'buildId':'assets-test','resources':resources,'payload':{'path':'src/vendor/market-hours/runtime-payload.js','elementId':'jpw-market-hours-payload'}}
        envelope={'schemaVersion':1,'buildId':'assets-test','files':{k:(base/path).read_text() for k,path in paths.items()}}
        encoded=json.dumps(envelope,ensure_ascii=True,separators=(',',':')).replace('<','\\u003c')
        payload=base/metadata['payload']['path'];payload.parent.mkdir(parents=True,exist_ok=True);payload.write_text('JPWMarketHoursAssets.register('+encoded+');')
        sources=['src/js/40-app/31-market-hours/01-sessions.js','src/js/40-app/31-market-hours/02-assets.js']
        tags=''
        for path in sources:
          target=base/path;target.parent.mkdir(parents=True,exist_ok=True)
          if (ROOT/path).is_file():shutil.copyfile(ROOT/path,target)
          tags+='<script src="'+path+'"></script>'
        boot='<script>const JP_WEALTH_BUILD_ID="assets-test";window.JPW_MARKET_HOURS_MANIFEST='+json.dumps(metadata)+';</script>'
        (base/'index.html').write_text('<!doctype html><title>Assets fixture</title>'+boot+tags)
        (base/'portable.html').write_text('<!doctype html><title>Portable fixture</title>'+boot+'<script type="application/json" id="jpw-market-hours-payload">'+encoded+'</script>'+tags)
        class Quiet(SimpleHTTPRequestHandler):
          def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=tmp));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        browser=pw.chromium.launch(executable_path=BROWSER,headless=True,args=['--enable-unsafe-swiftshader'])
        try:
          url='http://127.0.0.1:'+str(server.server_port)+'/index.html'
          for mode,target in [('http',url),('file',(base/'index.html').as_uri()),('portable',(base/'portable.html').as_uri())]:
            page=browser.new_page();requests=[];errors=[];page.on('request',lambda req:requests.append(req.url));page.on('pageerror',lambda e:errors.append(str(e)));page.goto(target)
            assert page.evaluate('typeof window.JPWMarketHoursAssets?.getCatalog==="function"'),'PRODUCT_FAIL: market asset loader absent'
            assert page.evaluate('!window.JPWAisolGlobeRuntime'),'runtime parsed before action'
            assert not any(u.endswith(('calendar-v1.json','aisol-globe.iife.js','runtime-payload.js')) for u in requests),'asset requested before action'
            result=page.evaluate('''async()=>{const a=JPWMarketHoursAssets;const catalog=await a.getCatalog();const factory=await a.getRenderer();return {venues:catalog.venues.map(x=>x.id),frozen:Object.isFrozen(catalog),factory:typeof factory.create,noThree:!window.THREE,noReact:!window.React};}''')
            assert all(x in result['venues'] for x in ['b3','nyse','jpx']) and result['frozen'] and result['factory']=='function' and result['noThree'] and result['noReact'],result
            assert not errors,errors
            report['checks'].append(mode+' lazy catalog + actual verified IIFE; no remote frameworks');page.close()
          page=browser.new_page();page.goto(url)
          renderer_url='**/src/vendor/aisol-dot-globe/aisol-globe.iife.js'
          page.route(renderer_url,lambda route:route.fulfill(status=200,body='window.corruptExecuted=true;'))
          result=page.evaluate('''async()=>{try{await JPWMarketHoursAssets.getRenderer();return {ok:true};}catch(e){return {ok:false,message:e.message,executed:!!window.corruptExecuted};}}''')
          assert not result['ok'] and not result['executed'],result
          page.unroute(renderer_url)
          assert page.evaluate('''async()=>typeof (await JPWMarketHoursAssets.getRenderer()).create''')=='function'
          report['checks'].append('corrupt source refused before execution; retry succeeds');page.close()
          page=browser.new_page();page.goto(url)
          result=page.evaluate('''async()=>{const c=new AbortController();const p=JPWMarketHoursAssets.getRenderer({signal:c.signal}).then(()=>"resolved",e=>e.name);const other=JPWMarketHoursAssets.getRenderer();c.abort();return {cancelled:await p,other:typeof (await other).create};}''')
          assert result=={'cancelled':'AbortError','other':'function'},result
          report['checks'].append('one consumer cancellation preserves shared renderer job');page.close()
          page=browser.new_page();requests=[];page.on('request',lambda req:requests.append(req.url));page.goto((base/'index.html').as_uri())
          result=page.evaluate('''async()=>{const c=new AbortController();const task=JPWMarketHoursAssets.getRenderer({signal:c.signal}).then(()=>"resolved",e=>e.name);c.abort();return await task;}''')
          page.wait_for_timeout(150)
          assert result=='AbortError' and not any(u.endswith('runtime-payload.js') for u in requests),('cancelled request started local payload',requests)
          assert page.evaluate('''async()=>typeof (await JPWMarketHoursAssets.getRenderer()).create''')=='function'
          report['checks'].append('last consumer aborted before transport; file retry succeeds');page.close()
          page=browser.new_page();page.goto(url)
          pending=[];page.route(renderer_url,lambda route:pending.append(route))
          result=page.evaluate('''async()=>{const started=performance.now();try{await JPWMarketHoursAssets.getRenderer();return {ok:true};}catch(e){return {ok:false,message:e.message,elapsed:performance.now()-started,executed:!!window.JPWAisolGlobeRuntime};}}''')
          assert not result['ok'] and 'Tempo' in result['message'] and result['elapsed']>=14900 and not result['executed'],result
          for route in pending:
            try:route.abort()
            except Exception:pass
          page.unroute(renderer_url)
          assert page.evaluate('''async()=>typeof (await JPWMarketHoursAssets.getRenderer()).create''')=='function'
          report['checks'].append('actual 15s HTTP timeout does not execute; explicit retry succeeds');page.close()
          page=browser.new_page();page.goto(url)
          result=page.evaluate('''async()=>{JPW_MARKET_HOURS_MANIFEST.buildId="wrong";try{await JPWMarketHoursAssets.getCatalog();return false;}catch(e){return !window.JPWAisolGlobeRuntime;}}''')
          assert result,'build mismatch must be rejected';report['checks'].append('incompatible build rejected');page.close()
          report['status']='PASS';report['browser']=browser.version
        finally:browser.close();server.shutdown();server.server_close()
    except AssertionError as error:report['status']='PRODUCT_FAIL';report['error']=str(error)
    except Exception as error:report['status']='ENVIRONMENT_ERROR';report['error']=str(error);traceback.print_exc()
    (out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())

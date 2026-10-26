from pathlib import Path
import sys,json,functools,threading,hashlib,traceback,os
root=Path.cwd();out=Path('/private/tmp/jpw-dante-20261024/avatar-startup-proposal');sys.path.insert(0,str(root/'tools'))
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap
from browser_fixture_server import BrowserFixtureServer
import settings_modal_test as profile
from http.server import SimpleHTTPRequestHandler
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*_):pass
avatar=json.loads((out/'synthetic-stored-avatars.json').read_text());candidate=(out/'09-settings-modal.proposed.js').read_text()
files=['src/js/40-app/09-settings-modal.js','src/js/40-app/09-profile-avatar-catalog.js','tools/download_assets_browser_test.py','tools/settings_modal_test.py','build-id.js'];identity=lambda:{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files};before=identity();rows=[]
server=BrowserFixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
  for name,patched,stored,expected in [('RED-default-startup',False,None,'PRODUCT_FAIL'),('GREEN-default-startup',True,None,'PASS'),('personal-portrait-still-validates',True,avatar['jeremy'],'PASS'),('explicitly-stored-Dante-still-validates',True,avatar['dante'],'PASS'),('invalid-stored-photo-still-rejected',True,'data:image/jpeg;base64,broken','PASS'),('invalid-empty-photo-stays-initials',True,'','PASS')]:
   ctx=b.new_context(service_workers='block');install_bootstrap(ctx)
   seed=None if stored is None else json.dumps({'schemaVersion':1,'displayName':'Synthetic startup','avatarDataUrl':stored})
   ctx.add_init_script("window.__onbShown=true;window.__downloadDecodes=0;window.__startupDecodeStacks=[];const original=window.atob;window.atob=function(v){window.__downloadDecodes++;window.__startupDecodeStacks.push(new Error().stack);return original(v)};")
   if seed is not None:ctx.add_init_script('localStorage.setItem("jpwealth_local_profile_v1",'+json.dumps(seed)+');')
   if patched:ctx.route('**/src/js/40-app/09-settings-modal.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=candidate))
   page=ctx.new_page();requests=[];page.on('request',lambda r:requests.append(r.url));row={'case':name,'expected':expected,'result':'NOT_RUN'}
   try:
    page.goto(url);wait_bootstrap(page);page.evaluate("closeModal();S.onboarding.done=true;JPWNavigation.navigate('tools-nocuda')")
    facts=page.evaluate("""() => ({decodes:__downloadDecodes,stacks:__startupDecodeStacks.slice(0,2),profileRaw:localStorage.getItem(SETTINGS_PROFILE_KEY),confirmed:settingsProfileState.confirmed,
      images:['settingsProfileAvatar','headerProfileAvatar'].map(id=>{const el=document.getElementById(id),img=el?.querySelector('img');return {id,count:el?.querySelectorAll('img').length||0,sourceDante:img?.getAttribute('src')===SETTINGS_PROFILE_AVATARS.find(x=>x.id==='dante-mascote').avatarDataUrl,sourcePersonal:img?.getAttribute('src')===settingsProfileState.confirmed.avatarDataUrl};})})""")
    row['facts']={**facts,'profileRaw':{'present':facts['profileRaw'] is not None,'sha256':hashlib.sha256(facts['profileRaw'].encode()).hexdigest() if facts['profileRaw'] else None},'confirmed':{'displayName':facts['confirmed']['displayName'],'avatarPresent':facts['confirmed']['avatarDataUrl'] is not None}}
    assert not any('/src/vendor/downloads/' in u or '/downloads/nocuda/' in u or u.endswith('.zip') for u in requests),'download transport before action'
    assert facts['profileRaw']==seed,'Startup must not materialize or overwrite identity'
    if stored is None:
     assert facts['decodes']==0,'zero base64 decode before action'
     assert facts['confirmed']=={'displayName':'','avatarDataUrl':None}
     assert all(x['count']==1 and x['sourceDante'] for x in facts['images'])
    elif stored in avatar.values():
     assert facts['decodes']>0,'Untrusted persisted content must still pass the original byte validator'
     assert all(x['count']==1 and x['sourcePersonal'] for x in facts['images'])
    else:
     assert all(x['count']==0 for x in facts['images']),'Malformed stored content must not use the trusted fallback route'
    row['result']='PASS'
   except AssertionError as e:row.update(result='PRODUCT_FAIL',error=str(e),traceback=traceback.format_exc())
   except Exception as e:row.update(result='TEST_HARNESS_FAIL',error=str(e),traceback=traceback.format_exc())
   finally:ctx.close();rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
  # Existing complete profile safety contract: same original test, one routed JS
  # source candidate, no altered validator, writer, normalizer or oracle.
  routed=b.new_context
  def route_candidate(**kwargs):
   ctx=routed(**kwargs);ctx.route('**/src/js/40-app/09-settings-modal.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=candidate));return ctx
  b.new_context=route_candidate
  row={'case':'existing-complete-profile-safety-oracles','expected':'PASS','result':'NOT_RUN'}
  try:profile.run_profile_contract(b,url);row['result']='PASS'
  except Exception as e:row.update(result='PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL',error=str(e),traceback=traceback.format_exc())
  finally:
   for context in b.contexts:context.close()
   rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
  b.close()
finally:server.shutdown();server.server_close()
report={'cases':rows,'source_before':before,'source_after':identity(),'source_unchanged':before==identity(),'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'limits':['Scratch source-route candidate, not applied.','Original zero-atob startup oracle kept; original complete profile-safety test reused unchanged.','Synthetic disposable contexts, Chromium headless only.']}
(out/'replay-receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['source_unchanged']
assert all(r['result']==r['expected'] for r in rows),[(r['case'],r['result']) for r in rows]
print('PROPOSAL PASS: startup RED rejected; GREEN and unmodified personal profile safety checks passed',flush=True)

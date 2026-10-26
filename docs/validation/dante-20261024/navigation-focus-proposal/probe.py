import sys,json,hashlib,subprocess,time
from pathlib import Path
root=Path.cwd();out=Path('/private/tmp/jpw-dante-20261024/navigation-focus-proposal')
sys.path.insert(0,str(root/'tools'))
import navigation_ia_test as nav
from playwright.sync_api import sync_playwright
files=['src/js/40-app/01-navigation.js','src/js/40-app/11-operational-shell.js','tools/navigation_ia_test.py','build-id.js','index.html']
hashes=lambda:{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files}
before=hashes();baseline=json.loads(Path('/private/tmp/jpw-dante-20261024/baseline.json').read_text())
report={'source_before':before,'scope':'A0; production files untouched; real Playwright clicks, no forced click, no timing delays or RAF suppression','repetitions':[],'baselineComparison':{}}
for f in files:
 old=baseline.get('hashes',{}).get(f)
 if old:report['baselineComparison'][f]={'initialSha256':old,'currentSha256':before[f],'same':old==before[f]}
for f in ['src/js/40-app/11-operational-shell.js','tools/navigation_ia_test.py']:
 previous=subprocess.run(['git','show','HEAD:'+f],capture_output=True).stdout
 report['baselineComparison'][f]={'headSha256':hashlib.sha256(previous).hexdigest(),'currentSha256':before[f],'same':hashlib.sha256(previous).hexdigest()==before[f]}
script="""()=>{
 window.__focusTrace=[];
 window.__focusSnapshot=()=>({at:performance.now(),activeId:document.activeElement?.id,activeTag:document.activeElement?.tagName,activeText:document.activeElement?.textContent?.trim().slice(0,70),focusInside:document.getElementById('alladin').contains(document.activeElement),activeInert:!!document.activeElement?.closest('[inert]'),menu:document.documentElement.dataset.shellMenu||null,route:JPWNavigation.current()});
 const save=kind=>__focusTrace.push({kind,...__focusSnapshot()});
 for(const capture of [true,false])document.addEventListener('click',event=>{if(event.target.closest('#nav > .tab[data-route="alladin"]'))save(capture?'click-capture':'click-bubble');},capture);
 document.addEventListener('focusin',event=>save('focusin'),true);
 const native=requestAnimationFrame;
 window.requestAnimationFrame=function(callback){const traced=/shellNavigationApplied/.test(new Error().stack);if(traced)save('navigation-RAF-scheduled');return native.call(window,t=>{if(traced)save('navigation-RAF-before');const result=callback(t);if(traced)save('navigation-RAF-after');return result;});};
}"""
server,url=nav.serve()
try:
 with sync_playwright() as pw:
  browser=nav.launch_browser(pw)
  for i in range(5):
   ctx,page,observed=nav.boot(browser,url,{'width':390,'height':844})
   try:
    page.evaluate("JPWNavigation.navigate('research-forex')")
    page.click('[data-shell-menu-toggle]')
    assert page.evaluate('appSidebar.contains(document.activeElement)')
    page.evaluate(script)
    page.click('#nav > .tab[data-route="alladin"]')
    state=nav.active_state(page)
    immediate=page.evaluate('__focusSnapshot()')
    after=page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>resolve(__focusSnapshot())))')
    events=page.evaluate('__focusTrace')
    assert state['screen']=='alladin' and state['primary']=='alladin'
    assert after['focusInside'],after
    report['repetitions'].append({'iteration':i+1,'state':state,'immediate':immediate,'afterNextRAF':after,'events':events,'observed':observed})
    print(json.dumps({'iteration':i+1,'immediate':immediate['focusInside'],'afterNextRAF':after['focusInside'],'events':[e['kind'] for e in events]}),flush=True)
   finally:ctx.close()
  ctx,page,observed=nav.boot(browser,url,{'width':390,'height':844})
  try:
   page.evaluate("JPWNavigation.navigate('research-forex')")
   page.click('[data-shell-menu-toggle]');page.evaluate(script)
   page.evaluate("shellFocusCurrentScreen=function(){__focusTrace.push({kind:'fault-missing-destination-focus',...__focusSnapshot()})}")
   page.click('#nav > .tab[data-route="alladin"]')
   state=nav.active_state(page);after=page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>resolve(__focusSnapshot())))')
   assert state['screen']=='alladin' and state['primary']=='alladin'
   rejected=not after['focusInside'];assert rejected,'missing-focus counterproof unexpectedly passed'
   report['counterproof']={'mutation':'only in isolated runtime: shellFocusCurrentScreen no-op; native RAF/click/nav unchanged','state':state,'afterNextRAF':after,'sameFocusCriterionRejected':rejected,'events':page.evaluate('__focusTrace'),'observed':observed}
   print('counterproof missing-focus rejected='+str(rejected),flush=True)
  finally:ctx.close()
  browser.close()
finally:
 server.shutdown();server.server_close()
 report['source_after']=hashes();report['source_unchanged']=report['source_before']==report['source_after']
 (out/'receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('source_unchanged='+str(report['source_unchanged']),flush=True)

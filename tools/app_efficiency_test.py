#!/usr/bin/env python3
"""Disposable synthetic characterization. Public API wrappers retain original behavior."""
import argparse,json,time,statistics,math,hashlib,threading,traceback
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright
from forex_execution_table_test import SEED,ready,prepare_drafts,Quiet,Server
from browser_bootstrap_fixture import install_bootstrap,assert_fixture_requests
from notes_launcher_test import launch_options

PROBE=r'''() => {
 const p=window.__eff={counts:{},mutations:0,hiddenMutations:0,installed:[]};
 for(const k of ['executionBoard','state'])JPWForex[k]={...JPWForex[k]};
 for(const k of ['JPWAlladin','JPWPersonalFinance','JPWNotifications'])if(window[k])window[k]={...window[k]};
 if(window.JPWAlladin?.leitura)JPWAlladin.leitura={...JPWAlladin.leitura};
 const hit=k=>p.counts[k]=(p.counts[k]||0)+1;
 const wrap=(obj,k,name)=>{if(typeof obj?.[k]!=='function')return;const f=obj[k];try{obj[k]=function(...a){hit(name);return f.apply(this,a)};if(obj[k]===f)throw Error('Cannot instrument '+name);p.installed.push(name);}catch(e){throw Error('Instrumentation rejected '+name+': '+e.message)}};
 wrap(JPWForex.executionBoard,'read','executionBoard.read');wrap(JPWForex.executionBoard,'previewOrder','previewOrder');
 for(const k of ['read','accountContext','operationalSelection','supported'])wrap(JPWForex.state,k,'state.'+k);
 for(const k of ['compute','pfWriteBlockReason','pfPendingBefore','pfCreditLineDerived'])wrap(window,k,'collectorDependency.'+k);
 if(window.JPWAlladin?.leitura)for(const k of Object.keys(JPWAlladin.leitura))wrap(JPWAlladin.leitura,k,'alladin.leitura.'+k);
 const clone=window.structuredClone;window.structuredClone=function(value,...rest){hit('structuredClone');if(value===S||value===S.forex||value?.accountContexts||value?.phases||Array.isArray(value)&&value.some(x=>Array.isArray(x?.orders)))hit('structuredClone.global');return clone.call(this,value,...rest)};p.installed.push('structuredClone');wrap(JSON,'stringify','JSON.stringify');wrap(Storage.prototype,'setItem','Storage.setItem');
 for(const [obj,prefix] of [[window.JPWPersonalFinance,'personalFinance'],[window.JPWAlladin,'alladin'],[window.JPWNotifications,'notifications']])if(obj)for(const k of Object.keys(obj))if(typeof obj[k]==='function')wrap(obj,k,prefix+'.'+k);
 const roots=['fxconsolidated','forexEnginePanel','forexReservesPanel','forexV11Overview','execOverview','phaseContainer','dashMacroGrid','dashCharts','dashCyclePace','dashRiskDetail'];
 const visible=e=>{if(!e?.isConnected)return false;for(let a=e;a;a=a.parentElement){const c=getComputedStyle(a);if(a.hidden||a.inert||a.getAttribute('aria-hidden')==='true'||c.display==='none'||c.visibility==='hidden'||c.visibility==='collapse'||c.contentVisibility==='hidden')return false;if(a.tagName==='DETAILS'&&!a.open&&e!==a&&!a.querySelector(':scope > summary')?.contains(e))return false;}return !!e.getClientRects().length};
 const empty=()=>({childList:0,characterData:0,attributes:0});
 p.activity=performance.now();p.byType=empty();p.hiddenByType=empty();p.hiddenContentRebuilds={};p.examples=[];
 const consume=rs=>{for(const r of rs){const e=r.target.nodeType===1?r.target:r.target.parentElement;if(!e||e.closest('template,[data-eff-ignore]'))continue;p.activity=performance.now();p.mutations++;p.byType[r.type]++;if(!visible(e)){p.hiddenMutations++;p.hiddenByType[r.type]++;}
  const root=roots.map(id=>document.getElementById(id)).filter(Boolean).find(root=>root.contains(e));const inner=e.closest('.card,.exec-view,.screen,[role=tabpanel]');const panel=root&&(inner&&root.contains(inner)&&!visible(inner)?inner:root);
  // Gate only content reconstruction; hidden/inert/ARIA/context attributes are separately observed.
  if(panel&&!visible(panel)&&r.type==='childList'&&[...r.addedNodes,...r.removedNodes].some(node=>node.nodeType===1)){
   const ignored=e.closest('[role=status],[aria-live],#fxReserveFormContext,#fxBudgetContext');
   if(!ignored){p.hiddenContentRebuilds[panel.id]=(p.hiddenContentRebuilds[panel.id]||0)+1;if(p.examples.length<12)p.examples.push({panel:panel.id,target:e.id||e.tagName,type:r.type});}
  }
 }};
 p.observer=new MutationObserver(consume);
 p.observer.observe(document.body,{childList:true,characterData:true,attributes:true,subtree:true});
 p.reset=()=>{p.observer.takeRecords();p.counts={};p.mutations=0;p.hiddenMutations=0;p.byType=empty();p.hiddenByType=empty();p.hiddenContentRebuilds={};p.examples=[];p.activity=performance.now()};
 p.stabilize=async(start)=>{let previous='',stableAt=performance.now();const deadline=start+10000;while(performance.now()<deadline){await new Promise(r=>setTimeout(r,25));consume(p.observer.takeRecords());const key=Object.entries(p.counts).map(([k,v])=>k+':'+v).join('|')+';'+p.mutations;if(key!==previous){previous=key;stableAt=performance.now();}if(performance.now()-Math.max(stableAt,p.activity)>=300&&performance.now()-start>=500)return {total_ms:performance.now()-start,stabilized:true};}return {total_ms:performance.now()-start,stabilized:false};};
 if(!['executionBoard.read','previewOrder','state.read','state.accountContext','state.operationalSelection','state.supported'].every(k=>p.installed.includes(k)))throw Error('Incomplete mandatory instrumentation');
 p.snapshot=()=>({installed:p.installed,counts:{...p.counts},mutations:p.mutations,hiddenMutations:p.hiddenMutations,mutationTypes:{...p.byType},hiddenMutationTypes:{...p.hiddenByType},hiddenContentRebuilds:{...p.hiddenContentRebuilds},hiddenContentExamples:p.examples,panelVisibility:Object.fromEntries(roots.map(id=>[id,visible(document.getElementById(id))]))});
}'''
FIXTURE=r'''n=>{
 const scope=JPWForex.state.operationalSelection(),p=S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId];
 const templates=p.phases.map(ph=>structuredClone(ph.orders[0]));
 p.phases.forEach((ph,pi)=>{ph.orders=Array.from({length:n/6},(_,i)=>({...structuredClone(templates[pi]),id:'SYN-'+pi+'-'+i,orderId:'synthetic-order-'+pi+'-'+i,accountId:scope.accountId,periodId:scope.periodId,currency:'USD',par:'EURUSD',tipo:'BUY',entry:1.2,sl:1.17,tp:1.26,lote:.01}));});
 S.operationHistory={schemaVersion:1,records:Array.from({length:n},(_,i)=>({schemaVersion:1,accountId:scope.accountId,periodId:scope.periodId,currency:'USD',operationId:'synthetic-history-'+i,instrument:'EURUSD',direction:'BUY',openedAt:null,openedAtSource:null,closedAt:'2026-06-20T10:00:00.000Z',closedAtSource:'formal_confirmation',referenceBalance:10000,referenceBalanceType:'cycle_initial_balance',netResult:-300,defenseCount:1,defenseCountSource:'manual',maxAccountPhaseReached:null,maxAccountPhaseIntegrity:'observed',phaseCaptureFault:null,maxGridPhaseReached:null,ordersSnapshot:[],finalizedAt:'2026-06-20T10:00:00.000Z'}))};
 p.ledger=Array.from({length:n},(_,i)=>({accountId:scope.accountId,periodId:scope.periodId,currency:'USD',data:'2026-09-22',resultado:0,saldo:12000}));
 if(p.phases.reduce((a,x)=>a+x.orders.length,0)!==n||p.ledger.some(x=>!Number.isFinite(x.saldo)))throw Error('fixture shape');
 if(new Set(p.phases.flatMap(ph=>ph.orders.map(o=>o.orderId))).size!==n||!JPWForex.state.supported())throw Error('fixture domain shape');
 if(save()!==true)throw Error('fixture rejected by production persistence validation');
 render();renderPhases();return {orders:n,ledger:p.ledger.length,history:S.operationHistory.records.length,domainSupported:true,persistenceAccepted:true};
}'''
def stats(xs):
 s=sorted(xs);return {'n':len(xs),'median_ms':statistics.median(xs),'p95_ms':s[min(len(s)-1,math.ceil(.95*len(s))-1)],'samples_ms':xs}
def pwa_startup(browser, url, root, samples):
 """Fresh profile per pair; activated install implies install waitUntil completed."""
 cold=[];offline=[];preparation=[];evidence=[]
 for sample in range(samples):
  context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='allow')
  context.add_init_script('window.__onbShown=true');install_bootstrap(context)
  page=context.new_page();page.set_default_timeout(60000)
  responses=[]
  page.on('response',lambda response: responses.append({'url':response.url,'status':response.status,'from_service_worker':response.from_service_worker}))
  try:
   t=time.perf_counter();page.goto(url);ready(page);cold.append((time.perf_counter()-t)*1000)
   prepare=time.perf_counter()
   registration=page.evaluate("""async()=>{const r=await Promise.race([navigator.serviceWorker.ready,new Promise((_,reject)=>setTimeout(()=>reject(Error('SW ready timeout')),60000))]);const worker=r.active;if(!worker)throw Error('SW active missing');if(worker.state!=='activated')await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('SW activation timeout: '+worker.state)),60000);const check=()=>{if(worker.state==='activated'){clearTimeout(timer);worker.removeEventListener('statechange',check);resolve();}else if(worker.state==='redundant'){clearTimeout(timer);reject(Error('SW became redundant'));}};worker.addEventListener('statechange',check);check();});return {scope:r.scope,state:worker.state,scriptURL:worker.scriptURL}}""")
   assert registration['state']=='activated', registration
   controlled_reload=False
   try:page.wait_for_function('!!navigator.serviceWorker.controller',timeout=3000)
   except Exception:
    page.reload();ready(page);controlled_reload=True
    page.wait_for_function('!!navigator.serviceWorker.controller',timeout=30000)
   cache=page.evaluate("""async()=>{
    const required=[new URL('index.html',location.href).href,new URL('build-id.js',location.href).href,...[...document.scripts].filter(s=>s.src&&new URL(s.src).origin===location.origin).map(s=>s.src)];
    const names=await caches.keys(), details=[];
    for(const name of names){const c=await caches.open(name),keys=await c.keys();details.push({name,count:keys.length,required:await Promise.all([...new Set(required)].map(async url=>({url,present:!!(await c.match(url))})))});}
    return {controller:navigator.serviceWorker.controller?.scriptURL,caches:details};
   }""")
   assert cache['controller'] and any(c['name'].startswith('jp-wealth-') and all(r['present'] for r in c['required']) for c in cache['caches']), cache
   preparation.append((time.perf_counter()-prepare)*1000)
   context.set_offline(True);responses.clear()
   t=time.perf_counter();response=page.reload(wait_until='load');ready(page);offline.append((time.perf_counter()-t)*1000)
   assert response and response.from_service_worker, 'Offline document was not served by SW'
   # Fetch proves the actual offline build bytes; outside reload timing.
   build=page.evaluate("async()=>{const r=await fetch(new URL('build-id.js',location.href),{cache:'no-store'});if(!r.ok)throw Error('offline build-id '+r.status);return await r.text()}")
   assert hashlib.sha256(build.encode()).hexdigest()==hashlib.sha256((root/'build-id.js').read_bytes()).hexdigest(), 'Offline build-id bytes differ'
   build_responses=[r for r in responses if r['url'].split('?')[0].endswith('/build-id.js')]
   assert build_responses and all(r['from_service_worker'] for r in build_responses), build_responses
   scripts=[r for r in responses if r['url'].split('?')[0].endswith('.js')]
   assert scripts and all(r['from_service_worker'] for r in scripts if r['url'].startswith(url.rsplit('/',1)[0]+'/')), scripts
   evidence.append({'sample':sample,'registration':registration,'cache':cache,'controlled_reload_outside_timing':controlled_reload,'offline_responses':list(responses),'offline_build_sha256':hashlib.sha256(build.encode()).hexdigest()})
   assert_fixture_requests(context)
  finally:context.close()
 return {'fresh_context_cold_open':stats(cold),'sw_cache_offline_reload':stats(offline),'preparation_excluded':stats(preparation),'evidence':evidence,'limits':['Each pair uses a fresh context and one offline controlled reload.','Routing disables HTTP cache, while SW CacheStorage remains real. This is offline SW reuse, not a warm HTTP/network measurement.','Activated registration requires successful install waitUntil; explicit cache probes verify HTML/build-id/script entries. Preparation and byte-verification fetch are excluded from reload timing.']}

def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--mode',choices=['characterize','verify'],default='characterize');a.add_argument('--suite',choices=['interactive','startup','all'],default='all');a.add_argument('--samples',type=int,default=11);a.add_argument('--pwa-startup',action='store_true');args=a.parse_args();assert args.samples>=3, '--samples must be >=3';args.out.mkdir(parents=True,exist_ok=True)
 root=args.root.resolve();files=[root/'index.html',root/'sw.js',root/'build-id.js',root/'src/js/manifest.json',root/'src/styles/app.css',*sorted((root/'src/js').rglob('*.js'))];hashes=lambda:{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 report={'mode':args.mode,'suite':args.suite,'pwa_startup_requested':args.pwa_startup,'samples':args.samples,'source_sha256':hashes(),'timings':{},'scenarios':[],'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'limitations':['Open/navigation timing uses automation wall time. Bootstrap context.route disables normal HTTP caching: same_context_reload is not a PWA/cache-warm measurement.','Closure-private notification collectors and lexical state.supported calls are not directly wrapped; exported dependencies and state.operationalSelection calls are observed. state.supported counter covers public calls only.','Synthetic history follows operation_history_test.py canonical schema; production save validates persistence. Timing reports dispatch through two requestAnimationFrame callbacks and total until 300ms quiet after minimum500ms, capped10s. DOM attributes/text/children observed separately; only hidden content-root reconstruction gates. Quiet-window observation cannot exclude arbitrary work delayed beyond500ms.']};server=Server(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
   cold=[];warm=[]
   for i in range(args.samples if args.suite in ['startup','all'] else 0):
    c=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block');c.add_init_script('window.__onbShown=true');install_bootstrap(c);page=c.new_page();t=time.perf_counter();page.goto(url);ready(page);cold.append((time.perf_counter()-t)*1000)
    t=time.perf_counter();page.reload();ready(page);warm.append((time.perf_counter()-t)*1000);assert_fixture_requests(c);c.close()
   if cold:report['timings'].update(cold_open=stats(cold),same_context_reload=stats(warm))
   for n in ([6,60,600] if args.suite in ['interactive','all'] else []):
    c=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block');c.add_init_script('window.__onbShown=true');install_bootstrap(c);page=c.new_page();page.goto(url);ready(page);page.evaluate(SEED);prepare_drafts(page);fixture=page.evaluate(FIXTURE,n);page.evaluate(PROBE)
    for name,selector in [('reason','[data-eb-reason="0:0"]'),('entry','[data-p="0"][data-o="0"][data-f="entry"]')]:
     samples=[];totals=[];observations=[];confirmed=page.evaluate('({state:JSON.stringify(S),stored:localStorage.getItem(LSKEY)})')
     for j in range(args.samples):
      result=page.evaluate('''async ({selector,value})=>{const e=document.querySelector(selector);if(!e)throw Error(selector);__eff.reset();const t=performance.now();e.value=value;e.dispatchEvent(new Event('input',{bubbles:true}));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const elapsed=performance.now()-t;const settled=await __eff.stabilize(t);return {...__eff.snapshot(),elapsed,...settled};}''',{'selector':selector,'value':str(1.21+j*.001) if name=='entry' else 'Synthetic reason '+str(j)})
      samples.append(result.pop('elapsed'));totals.append(result.pop('total_ms'));observations.append(result)
     assert confirmed==page.evaluate('({state:JSON.stringify(S),stored:localStorage.getItem(LSKEY)})'), 'Draft input mutated confirmed state or storage'
     report['scenarios'].append({'orders':n,'fixture':fixture,'confirmed_unchanged':True,'input':name,'dispatch_two_raf':stats(samples),'settled_total':stats(totals),'observations':observations})
    page.evaluate("JPWForex.executionBoardUI.discardAll?.();")
    # Draft cancellation via actual UI keeps navigation guard semantics.
    page.locator('[data-eb-cancel-row="0:0"]').click();nav=[]
    for j in range(args.samples):
     t=time.perf_counter();page.evaluate("JPWNavigation.navigate('forex-history');JPWNavigation.navigate('forex-operation')");nav.append((time.perf_counter()-t)*1000)
    report['timings']['navigation_'+str(n)]=stats(nav)
    ordinary=page.evaluate('''async()=>{const e=document.createElement('input');e.id='effSyntheticOrdinaryInput';document.body.append(e);__eff.reset();const t=performance.now();e.value='Synthetic ordinary input';e.dispatchEvent(new Event('input',{bubbles:true}));const timing=await __eff.stabilize(t);return {...__eff.snapshot(),...timing};}''');report['scenarios'].append({'orders':n,'input':'ordinary-outside-forex','observation':ordinary});page.evaluate("document.getElementById('effSyntheticOrdinaryInput').remove()");
    general=page.evaluate('async()=>{__eff.reset();const t=performance.now();render();const timing=await __eff.stabilize(t);return {...__eff.snapshot(),...timing};}');report['scenarios'].append({'orders':n,'input':'general-render','observation':general})
    page.screenshot(path=str(args.out/f'board-{n}.png'))
    # An exposed Consolidado must leave its inactive internal tabs untouched.
    page.evaluate("JPWNavigation.navigate('forex-consolidated')")
    for j in range(args.samples):
     consolidated=page.evaluate('async()=>{__eff.reset();const t=performance.now();render();render();const timing=await __eff.stabilize(t);return {...__eff.snapshot(),...timing};}')
     report['scenarios'].append({'orders':n,'input':'consolidated-repeated-render','sample':j,'observation':consolidated})
    assert_fixture_requests(c);c.close()
   if args.pwa_startup:report['pwa_startup']=pwa_startup(browser,url,root,args.samples)
   browser.close()
  report['source_unchanged']=report['source_sha256']==hashes();assert report['source_unchanged']
  failures=[]
  for s in report['scenarios']:
   if 'observations' in s:
    for i,o in enumerate(s['observations']):
     if not o['stabilized']:failures.append([s['orders'],s['input'],i,'stabilization-timeout'])
     for panel,count in o['hiddenContentRebuilds'].items():
      if count:failures.append([s['orders'],s['input'],i,'hiddenContentRebuilds',panel,count])
     for k in ['executionBoard.read','state.read','state.accountContext','state.operationalSelection','structuredClone.global','Storage.setItem']:
      if o['counts'].get(k,0)>0:failures.append([s['orders'],s['input'],i,k,o['counts'][k]])
     if o['counts'].get('previewOrder',0)>(1 if s['input']=='entry' else 0):failures.append([s['orders'],s['input'],i,'previewOrder',o['counts']['previewOrder']])
   elif s['input']=='ordinary-outside-forex':
    if not s['observation']['stabilized']:failures.append([s['orders'],s['input'],'stabilization-timeout'])
    for panel,count in s['observation']['hiddenContentRebuilds'].items():
     if count:failures.append([s['orders'],s['input'],'hiddenContentRebuilds',panel,count])
    for k,v in s['observation']['counts'].items():
     if k.startswith(('collectorDependency.','alladin.leitura.')) and v:failures.append([s['orders'],s['input'],k,v])
   else:
    if not s['observation']['stabilized']:failures.append([s['orders'],s['input'],'stabilization-timeout'])
    for panel,count in s['observation']['hiddenContentRebuilds'].items():
     if count:failures.append([s['orders'],s['input'],'hiddenContentRebuilds',panel,count])
  report['gate_failures']=failures;report['result']='CAPTURED' if args.mode=='characterize' else ('PASS' if not failures else 'FAIL')
 except BaseException as e:report.update(result='ERROR',error=str(e),trace=traceback.format_exc())
 finally:
  (args.out/'results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');server.shutdown()
 print(json.dumps({k:report[k] for k in ['result','timings','error'] if k in report},indent=2));return 0 if report['result'] in ['CAPTURED','PASS'] else 1
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Controlled-clock controller regressions for CHG-JPW-MARKET-NOON-20261016.

The real classic controller runs in a Node VM. Its renderer boundary is observed
without a GPU; DOM layout, native interaction acceptance and rendering remain the
separate browser/adapter lane. UTC and monotonic time advance independently.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'src/js/40-app/31-market-hours/04-controller.js'
SCRIPT = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1]+'/src/js/40-app/31-market-hours/04-controller.js','utf8');
const checks=[],failures=[];
const START=Date.parse('2026-10-16T12:00:00.000Z');
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject};}
async function settle(){for(let i=0;i<16;i++)await Promise.resolve();}
function fixture(options={}){
  let wall=options.utc??START,mono=0,seq=0,disposed=0,rendererLoads=0,renderCount=0,rendererOptions=null,selection='';
  const jobs=new Map(),calls=[],observers=[],signals=[],renders=[];
  class Events{constructor(){this.listeners=new Map()}addEventListener(n,fn){if(!this.listeners.has(n))this.listeners.set(n,new Set());this.listeners.get(n).add(fn)}removeEventListener(n,fn){this.listeners.get(n)?.delete(fn)}emit(n){for(const fn of this.listeners.get(n)||[])fn({type:n})}}
  class Element extends Events{constructor(){super();this.children=[];this.dataset={};this.isConnected=true;this.hidden=false;this.inert=false;this.parentElement=null;}append(...els){for(const el of els){this.children.push(el);el.parentElement=this}}remove(){this.isConnected=false;if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(x=>x!==this)}closest(){for(let e=this;e;e=e.parentElement)if(e.hidden||e.inert)return e;return null}setAttribute(){}get firstChild(){return this.children[0]}get lastChild(){return this.children.at(-1)}}
  const document=new Events();document.hidden=!!options.hidden;document.documentElement=new Element();document.documentElement.dataset.theme='light';document.createElement=()=>new Element();
  const host=new Element();host.parentElement=document.documentElement;const globalEvents=new Events();
  const venues=[{id:'b3',city:'São Paulo',country:'Brasil',lat:-23.55,lng:-46.63},{id:'nyse',city:'Nova York',country:'EUA',lat:40.71,lng:-74.01}];
  const factory={create(el,opts){rendererOptions=opts;calls.push({kind:'create',mono,wall});return {update(data){calls.push({kind:'update',data,mono,wall})},focusMarker(id,data){calls.push({kind:'marker',id,data,mono,wall})},focusLocation(location,data){calls.push({kind:'location',location,data,mono,wall})},setActive(active){calls.push({kind:'active',active,mono,wall})},dispose(){disposed++;calls.push({kind:'dispose',mono,wall})}}}};
  // Match the new view lifecycle surface; real help cleanup is exercised by
  // market_hours_minimal_test.py, while these existing camera oracles remain.
  const view={root:new Element(),globe:new Element(),mapVisible:options.mapVisible!==false,render(s,id){renderCount++;selection=id;renders.push({s,id,mono,wall})},globeStatus(){},focusSelected(){},closeHelp(){},dispose(){this.root.remove()}};
  let viewSelect,viewSync;
  const context={console,AbortController,HTMLElement:Element,document,Map,Promise,Math,JSON,Error,
    Date:class extends Date{constructor(...args){super(...(args.length?args:[wall]))}static now(){return wall}},performance:{now:()=>mono},
    setTimeout(fn,delay){const id=++seq;jobs.set(id,{fn,due:mono+Math.max(0,delay)});return id},clearTimeout(id){jobs.delete(id)},
    MutationObserver:class{constructor(fn){this.fn=fn;observers.push(this)}observe(){}disconnect(){this.off=true}},
    getComputedStyle:()=>({getPropertyValue:()=> '#526071'}),matchMedia:()=>({matches:!!options.reducedMotion}),
    addEventListener:globalEvents.addEventListener.bind(globalEvents),removeEventListener:globalEvents.removeEventListener.bind(globalEvents),
    JPWMarketSessions:{prepare:raw=>raw,at:(catalog,now)=>({asOf:now,venues:catalog.venues.map(v=>({...v,phase:'continuous',nextTransition:null}))})},
    JPWMarketHoursView:{create(h,c,select,retry,sync){viewSelect=select;viewSync=sync;return view}},
    JPWMarketHoursAssets:{getCatalog:()=>Promise.resolve({venues}),getRenderer:({signal})=>{rendererLoads++;signals.push(signal);return options.rendererJob?options.rendererJob.promise:Promise.resolve(factory)}}};
  vm.createContext(context);vm.runInContext(source,context,{filename:'04-controller.js'});
  const api=context.JPWMarketHours;
  async function advance(ms){const end=mono+ms;let count=0;while(true){let next=null;for(const [id,job] of jobs)if(job.due<=end&&(!next||job.due<next.job.due))next={id,job};if(!next)break;if(++count>20000)throw Error('unbounded scheduled work');const delta=next.job.due-mono;mono+=delta;wall+=delta;jobs.delete(next.id);next.job.fn();await settle()}const delta=end-mono;mono=end;wall+=delta;await settle()}
  function notify(){for(const observer of observers)if(!observer.off)observer.fn([])}
  return {api,view,host,factory,calls,signals,jobs,renders,
    async boot(){api.mount(host);api.activate();await settle();},advance,
    select(id,source='table'){viewSelect(id,source)},interact(type){assert.equal(typeof rendererOptions?.onInteraction,'function','renderer must receive accepted-interaction observer');rendererOptions.onInteraction({type})},
    marker(){rendererOptions.onSelectMarker({markerId:'city-nova-york'})},
    hidden(value){document.hidden=value;document.emit('visibilitychange')},blur(){globalEvents.emit('blur')},focus(){globalEvents.emit('focus')},
    collapse(value){view.mapVisible=!value;viewSync()},dialog(value){host.inert=value;notify()},routeHidden(value){host.hidden=value;notify()},
    passive(){globalEvents.emit('pointermove');globalEvents.emit('focusin');document.emit('mouseover')},jumpWall(ms){wall+=ms},
    get wall(){return wall},get mono(){return mono},get selection(){return selection},get disposed(){return disposed},get rendererLoads(){return rendererLoads},get renderCount(){return renderCount},
    locations(){return calls.filter(c=>c.kind==='location')},markers(){return calls.filter(c=>c.kind==='marker')},camera(){return calls.filter(c=>c.kind==='location'||c.kind==='marker')}};
}
async function check(name,run){try{await run();checks.push(name)}catch(error){failures.push({case:name,error:error.stack})}}
async function boot(options){const f=fixture(options);await f.boot();return f}
function location(f,lng){const last=f.locations().at(-1);assert.ok(last,'expected observable geographic focus');assert.equal(last.location.lat,0);assert.ok(Math.abs(last.location.lng-lng)<1e-7,`${last.location.lng} != ${lng}`);return last}
(async()=>{
  for(const [stamp,lng] of [['00:00:00.000',-180],['06:00:00.000',90],['12:00:00.000',0],['18:00:00.000',-90],['06:30:00.000',82.5],['23:59:59.000',-179.99583333333334]])await check('UTC '+stamp+' uses equatorial mean solar noon',async()=>{const f=await boot({utc:Date.parse('2026-10-16T'+stamp+'Z')});location(f,lng);assert.equal(f.selection,'b3');assert.equal(f.markers().length,0,'initial orientation must not refocus selected B3');assert.equal(f.locations()[0].data.animate,false);f.api.dispose()});
  await check('reference changes once per visible UTC minute, with no continuous camera calls',async()=>{const f=await boot();await f.advance(59999);assert.equal(f.locations().length,1);await f.advance(1);assert.equal(f.locations().length,2);location(f,-0.25);await f.advance(60000);assert.equal(f.locations().length,3);f.api.dispose()});
  await check('accepted held gesture blocks return beyond ten seconds and release starts a fresh ten seconds',async()=>{const f=await boot();f.interact('start');await f.advance(25000);assert.equal(f.locations().length,1);f.interact('end');await f.advance(9999);assert.equal(f.locations().length,1);await f.advance(1);assert.equal(f.locations().length,2);location(f,-0.1458333333333428);f.api.dispose()});
  await check('accepted cancel ends hold through the same end contract',async()=>{const f=await boot();f.interact('start');await f.advance(15000);f.interact('end');await f.advance(10000);assert.equal(f.locations().length,2);f.api.dispose()});
  await check('last manipulating key restarts the monotonic deadline',async()=>{const f=await boot();f.interact('key');await f.advance(9000);f.interact('key');await f.advance(9999);assert.equal(f.locations().length,1);await f.advance(1);assert.equal(f.locations().length,2);f.api.dispose()});
  await check('new accepted input interrupts a return and defers the next return',async()=>{const f=await boot();f.interact('key');await f.advance(10000);assert.equal(f.locations().length,2);f.interact('start');await f.advance(20000);assert.equal(f.locations().length,2);f.interact('end');await f.advance(10000);assert.equal(f.locations().length,3);f.api.dispose()});
  await check('explicit list selection focuses its city for ten seconds without changing back selection',async()=>{const f=await boot();f.select('nyse');assert.equal(f.selection,'nyse');assert.equal(f.markers().length,1);assert.equal(f.markers()[0].id,'city-nova-york');await f.advance(9999);assert.equal(f.locations().length,1);await f.advance(1);assert.equal(f.locations().length,2);assert.equal(f.selection,'nyse');f.api.dispose()});
  await check('marker selection preserves manual camera and does not restart the deadline',async()=>{const f=await boot();f.interact('key');await f.advance(9000);f.marker();assert.equal(f.selection,'nyse');assert.equal(f.markers().length,0);await f.advance(1000);assert.equal(f.locations().length,2);f.api.dispose()});
  await check('hover focus and calendar ticks do not postpone manual return',async()=>{const f=await boot();f.interact('key');await f.advance(9000);f.passive();await f.advance(1000);assert.equal(f.locations().length,2);assert.ok(f.renderCount>=10);f.api.dispose()});
  await check('wall-clock jumps do not shorten or extend the exploration deadline',async()=>{for(const jump of [3600000,-3600000]){const f=await boot();f.interact('key');await f.advance(2000);f.jumpWall(jump);await f.advance(7999);assert.equal(f.locations().length,1);await f.advance(1);assert.equal(f.locations().length,2);location(f,jump>0?-15.041666666666657:14.958333333333343);f.api.dispose()}});
  for(const mode of ['hidden','blur','collapse','dialog','routeHidden'])await check(mode+' cancels work; resume before deadline preserves manual and expires normally',async()=>{const f=await boot();f.interact('key');await f.advance(4000);const cameras=f.camera().length,rendered=f.renderCount;if(mode==='blur')f.blur();else f[mode](true);assert.equal(f.jobs.size,mode==='collapse'?1:0,'only collapsed visible list may keep its calendar timer');await f.advance(2000);assert.equal(f.camera().length,cameras);if(mode!=='collapse')assert.equal(f.renderCount,rendered);if(mode==='blur')f.focus();else f[mode](false);await settle();assert.equal(f.camera().length,cameras,'resume with future deadline preserves current manual angle');await f.advance(3999);assert.equal(f.camera().length,cameras);await f.advance(1);assert.equal(f.locations().length,2);f.api.dispose()});
  for(const mode of ['hidden','blur','collapse','dialog','routeHidden'])await check(mode+' resumed after deadline uses current noon immediately',async()=>{const f=await boot();f.interact('key');if(mode==='blur')f.blur();else f[mode](true);await f.advance(70000);assert.equal(f.locations().length,1);if(mode==='blur')f.focus();else f[mode](false);await settle();assert.equal(f.locations().length,2);location(f,-0.2916666666666572);f.api.dispose()});
  await check('route deactivate cancels a held gesture and activation respects its original deadline',async()=>{for(const pause of [2000,70000]){const f=await boot();f.interact('start');await f.advance(4000);f.api.deactivate();assert.equal(f.jobs.size,0);await f.advance(pause);assert.equal(f.locations().length,1);f.api.activate();await settle();assert.equal(f.locations().length,pause===2000?1:2);if(pause===2000){await f.advance(4000);assert.equal(f.locations().length,2)}f.api.dispose()}});
  await check('collapsed map selection stores no camera timer or work and late expansion uses current noon',async()=>{const f=await boot({mapVisible:false});assert.equal(f.rendererLoads,0);f.select('nyse');assert.equal(f.jobs.size,1);await f.advance(11000);f.collapse(false);await settle();assert.equal(f.markers().length,0);location(f,-0.04583333333334849);assert.equal(f.selection,'nyse');f.api.dispose()});
  await check('selection before delayed renderer focuses chosen city only while its deadline remains',async()=>{const job=deferred(),f=await boot({rendererJob:job});f.select('nyse');await f.advance(5000);job.resolve(f.factory);await settle();assert.equal(f.markers().length,1);assert.equal(f.locations().length,0);await f.advance(5000);location(f,-0.04166666666665719);f.api.dispose()});
  await check('hidden pending renderer is aborted, ignored when late, and safely reloaded on resume',async()=>{const job=deferred(),f=await boot({rendererJob:job});assert.equal(f.rendererLoads,1);f.hidden(true);assert.equal(f.signals[0].aborted,true);assert.equal(f.jobs.size,0);job.resolve(f.factory);await settle();assert.equal(f.calls.filter(c=>c.kind==='create').length,0);f.hidden(false);await settle();assert.equal(f.rendererLoads,2);assert.equal(f.calls.filter(c=>c.kind==='create').length,1);location(f,0);f.api.dispose()});
  await check('hidden before renderer request cancels queued acquisition entirely',async()=>{const f=fixture();f.api.mount(f.host);f.api.activate();f.hidden(true);await settle();assert.equal(f.rendererLoads,0);assert.equal(f.camera().length,0);assert.equal(f.jobs.size,0);f.hidden(false);await settle();assert.equal(f.rendererLoads,1);location(f,0);f.api.dispose()});
  await check('reduced motion disables explicit city and return animation',async()=>{const f=await boot({reducedMotion:true});f.select('nyse');assert.equal(f.markers().at(-1).data.animate,false);await f.advance(10000);assert.equal(f.locations().at(-1).data.animate,false);f.api.dispose()});
  await check('disposal cancels all timers and callbacks; late jobs cannot recreate renderer',async()=>{const job=deferred(),f=await boot({rendererJob:job});f.api.dispose();assert.equal(f.jobs.size,0);assert.equal(f.signals[0].aborted,true);job.resolve(f.factory);await settle();f.api.activate(f.host);f.hidden(false);f.focus();await f.advance(120000);assert.equal(f.calls.filter(c=>c.kind==='create').length,0);assert.equal(f.jobs.size,0)});
  await check('disposed ready controller ignores stale accepted events and tears renderer down once',async()=>{const f=await boot();f.interact('key');f.api.dispose();f.api.dispose();const cameras=f.camera().length;f.interact('end');f.select('nyse');await f.advance(120000);assert.equal(f.jobs.size,0);assert.equal(f.disposed,1);assert.equal(f.camera().length,cameras)});
  const result={status:failures.length?'PRODUCT_FAIL':'PASS',checks,failures};console.log(JSON.stringify(result));process.exitCode=failures.length?1:0;
})().catch(error=>{console.log(JSON.stringify({status:'TEST_HARNESS_FAIL',checks,failures,error:error.stack}));process.exitCode=2});
"""


def run(args):
    out = (ROOT / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    node = os.environ.get('JP_WEALTH_NODE') or shutil.which('node')
    if not node:
        bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        node = str(bundled) if bundled.exists() else None
    if not node:
        result = {'status': 'ENVIRONMENT_ERROR', 'error': 'Node runtime unavailable'}
        returncode = 2
    else:
        completed = subprocess.run([node, '-e', SCRIPT, str(ROOT)], capture_output=True, text=True, timeout=30)
        (out / 'stdout.log').write_text(completed.stdout)
        (out / 'stderr.log').write_text(completed.stderr)
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            result = {'status': 'TEST_HARNESS_FAIL', 'error': completed.stderr or completed.stdout}
        returncode = completed.returncode
    result['hashes'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                        for p in [SOURCE, 'tools/market_hours_noon_test.py']}
    result['scope'] = 'real controller; synthetic DOM/view/calendar and observable renderer boundary; no browser/GPU'
    result['node'] = node
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='tools/.artifacts/market-hours/noon-openings-20261016/controller-green')
    raise SystemExit(run(parser.parse_args()))

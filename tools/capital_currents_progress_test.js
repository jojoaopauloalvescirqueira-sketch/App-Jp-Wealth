#!/usr/bin/env node
'use strict';
const fs = require('fs'), vm = require('vm'), assert = require('assert/strict'), path = require('path');
const sandbox = { window: {}, Map, Set, JSON, Object, Array, String, Error, TypeError, RangeError };
const file = path.join(__dirname, '../src/js/40-app/30-capital-currents/03-progress.js');
if (fs.existsSync(file)) vm.runInNewContext(fs.readFileSync(file, 'utf8'), sandbox);
const api = sandbox.window.JPWCapitalCurrents?.progress;
assert.ok(api, 'Independent simulated-game progress API must exist');
assert.equal(api.KEY, 'jpwealth_capital_field_v1');
function storage(raw) {
  const data = new Map([['jpwealth_v9_state', 'protected-financial-bytes'], ['jpwealth_capital_currents_v1', 'old progress untouched']]);
  if (raw !== undefined) data.set(api.KEY, raw);
  return {data, writes: [], getItem(k) {return data.has(k) ? data.get(k) : null;},
    setItem(k,v) {this.writes.push(k); data.set(k,String(v));}, removeItem(k) {this.writes.push(k); data.delete(k);}};
}
let count = 0;
function test(name, run) {run(); count++; console.log('[PASS] '+name);}
test('fresh reads never write and contain only version plus step states', () => {
  const s=storage(), p=api.load(s); assert.equal(p.mode,'ok');
  assert.equal(JSON.stringify(p.value), '{"version":1,"steps":{}}'); assert.equal(s.writes.length,0);
});
test('all six IDs and three statuses persist without scenario fields', () => {
  const ids=['intro-field','intro-pressure','intro-depth','release-pressure','same-pulse-depth','shallow-band'];
  const s=storage(); let p=api.load(s).value;
  ids.forEach((id,i) => {p=api.mark(p,id,['seen','practiced','skipped'][i%3]);});
  assert.ok(api.save(p,s).ok); assert.equal(JSON.stringify(api.load(s).value),JSON.stringify(p));
  assert.deepEqual(s.writes,[api.KEY]); assert.equal(s.data.get('jpwealth_v9_state'),'protected-financial-bytes'); assert.equal(s.data.get('jpwealth_capital_currents_v1'),'old progress untouched');
});
test('demonstration cannot be downgraded by help, replay or skip', () => {
  let p=api.mark(api.load(storage()).value,'intro-field','practiced');
  p=api.mark(p,'intro-field','seen'); p=api.mark(p,'intro-field','skipped');
  assert.equal(p.steps['intro-field'],'practiced');
});
test('mark clones the record and rejects unknown IDs or statuses', () => {
  const p=api.load(storage()).value; const next=api.mark(p,'intro-field','seen');
  assert.equal(p.steps['intro-field'],undefined); assert.equal(next.steps['intro-field'],'seen');
  assert.throws(()=>api.mark(p,'financial-account','practiced')); assert.throws(()=>api.mark(p,'intro-field','won-money'));
});
for (const raw of ['{broken','null','[]','{"version":2,"steps":{}}','{"version":1,"steps":{"unknown":"seen"}}','{"version":1,"steps":{},"holdings":{"a":1000}}']) {
  test('incompatible bytes preserved until explicit restart: '+raw, () => {
    const s=storage(raw), result=api.load(s); assert.equal(result.mode,'incompatible');
    assert.equal(s.data.get(api.KEY),raw); assert.equal(s.writes.length,0);
    assert.equal(api.save(result.value,s).ok,false); assert.equal(s.data.get(api.KEY),raw);
    assert.equal(api.restart(s,raw).mode,'ok'); assert.equal(api.load(s).mode,'ok');
    assert.equal(s.data.get('jpwealth_v9_state'),'protected-financial-bytes'); assert.equal(s.data.get('jpwealth_capital_currents_v1'),'old progress untouched');
  });
}
test('storage failures permit temporary use without false success', () => {
  const denied={getItem(){throw Error('read denied');},setItem(){throw Error('quota');}};
  const p=api.load(denied); assert.equal(p.mode,'temporary'); assert.ok(p.message);
  assert.equal(api.save(p.value,denied).ok,false); assert.equal(api.restart(denied).mode,'temporary');
});
test('financial and laboratory payloads cannot enter saved progress', () => {
  const s=storage(); assert.equal(api.save({version:1,steps:{},seed:42},s).ok,false);
  assert.equal(api.save({version:1,steps:{'intro-field':{cash:300}}},s).ok,false);
  assert.equal(s.writes.length,0);
});
test('stale tab cannot save or restart over newer step progress', () => {
  const s=storage(), old=api.load(s), newer=api.mark(old.value,'release-pressure','practiced');
  api.save(newer,s); const raw=s.data.get(api.KEY);
  assert.equal(api.save(api.mark(old.value,'intro-field','seen'),s,old.raw).ok,false);
  assert.equal(api.restart(s,old.raw).mode,'conflict'); assert.equal(s.data.get(api.KEY),raw);
});
test('a successful setter is insufficient when another tab replaces bytes', () => {
  const s=storage(); const original=s.setItem;
  s.setItem=function(k,v){original.call(this,k,v);this.data.set(k,'newer tab bytes');};
  assert.equal(api.save(api.load(s).value,s).ok,false);
  assert.equal(s.data.get(api.KEY),'newer tab bytes');
});
test('read denial cannot trigger a blind save or restart', () => {
  let writes=0; const denied={getItem(){throw Error('denied');},setItem(){writes++;}};
  assert.equal(api.save({version:1,steps:{}},denied).mode,'temporary');
  assert.equal(api.restart(denied).mode,'temporary'); assert.equal(writes,0);
});
test('quota and after-write read failures never confirm', () => {
  const s=storage(); s.setItem=()=>{throw Error('quota');};
  assert.equal(api.save(api.load(s).value,s).mode,'temporary');
  const t=storage(); t.setItem=function(k,v){this.data.set(k,v); this.getItem=()=>{throw Error('after write');};};
  assert.equal(api.save({version:1,steps:{}},t).mode,'conflict');
});
test('restart readback mismatch is conflict and incompatible restart needs matching CAS', () => {
  const s=storage('{bad'); assert.equal(api.restart(s).mode,'conflict'); assert.equal(s.writes.length,0);
  assert.equal(api.restart(s,'{bad').mode,'ok');
  const t=storage(); t.setItem=function(k,v){this.data.set(k,'other tab');};
  assert.equal(api.restart(t,null).mode,'conflict');
});
test('denied browser storage getter remains temporary', () => {
  Object.defineProperty(sandbox.window,'localStorage',{get(){throw Error('getter denied');}});
  assert.equal(api.load().mode,'temporary'); assert.equal(api.save({version:1,steps:{}}).ok,false);
});
test('strict records reject date containers and hidden extra keys', () => {
  const s=storage(); const odd={version:1,steps:new Date(0)};
  assert.equal(api.save(odd,s).ok,false);
  const hidden={version:1,steps:{}}; Object.defineProperty(hidden,'params',{value:{u:.4}});
  assert.equal(api.save(hidden,s).ok,false); assert.equal(s.writes.length,0);
});
test('restart after-write read failure remains unconfirmed conflict', () => {
  const s=storage(); s.setItem=function(k,v){this.data.set(k,v);this.getItem=()=>{throw Error('readback');};};
  assert.equal(api.restart(s,null).mode,'conflict');
});
test('inherited version and steps cannot substitute for exact record keys', () => {
  const odd=Object.create({version:1,steps:{}});odd.a=1;odd.b=2;
  assert.equal(api.save(odd,storage()).ok,false);
});
test('required schema and step properties must be enumerable data, never accessors', () => {
  const s=storage(); let calls=0;
  const hidden={steps:{}}; Object.defineProperty(hidden,'version',{value:1});
  const hiddenSteps={version:1};Object.defineProperty(hiddenSteps,'steps',{value:{}});
  const accessor={version:1,get steps(){calls++;return {};}};
  const stepAccessor={version:1,steps:{}};Object.defineProperty(stepAccessor.steps,'intro-field',{enumerable:true,get(){calls++;return 'seen';}});
  const stepHidden={version:1,steps:{}};Object.defineProperty(stepHidden.steps,'intro-field',{value:'seen'});
  for(const v of [hidden,hiddenSteps,accessor,stepAccessor,stepHidden]) assert.equal(api.save(v,s).ok,false);
  assert.equal(calls,0);assert.equal(s.writes.length,0);
});
test('inherited serializers cannot write foreign payload', () => {
  const s=storage();const v=Object.assign(Object.create({toJSON(){return {financial:123};}}),{version:1,steps:{}});
  const result=api.save(v,s);
  if(result.ok)assert.equal(s.data.get(api.KEY),'\{"version":1,"steps":{}}');
  else assert.equal(s.writes.length,0);
});
for(const action of ['save','restart'])for(const outcome of ['changed','unknown','unchanged'])test(action+' throwing setter outcome '+outcome,()=>{
 const old='{"version":1,"steps":{"intro-field":"seen"}}',s=storage(old);
 let reads=0;const get=s.getItem;
 s.getItem=function(k){reads++;if(outcome==='unknown'&&reads>1)throw Error('unknown');return get.call(this,k);};
 s.setItem=function(k,v){this.writes.push(k);if(outcome==='changed')this.data.set(k,v);throw Error('write threw');};
 const result=action==='save'?api.save({version:1,steps:{}},s,old):api.restart(s,old);
 assert.equal(result.mode,outcome==='unchanged'?'temporary':'conflict');
 if(action==='save')assert.equal(result.ok,false);
 assert.equal(s.writes.length,1);
 if(outcome==='unchanged')assert.equal(s.data.get(api.KEY),old);
});
console.log(`PASS ${count}/${count} simulated progress contracts`);

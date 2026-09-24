#!/usr/bin/env python3
"""Synthetic preference contract in Node/vm: no DOM, browser profile or financial runtime."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/js/00-core/08-module-availability.js'

SCRIPT = r"""
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8');
const key='jpw_module_availability_v1';
const raw=modules=>JSON.stringify({schemaVersion:1,modules});
const clean=value=>JSON.parse(JSON.stringify(value));
let passed=0,failed=0;
function test(name,fn){
  try{fn();passed++;console.log('PASS '+name);}
  catch(error){failed++;console.error('PRODUCT_FAIL '+name+'\n'+error.stack);}
}
function fixture(initial=null,setup){
  const map=new Map([['jpwealth_v9_state','synthetic-financial-sentinel'],['unrelated-key','preserved']]);
  if(initial!==null)map.set(key,initial);
  const events={},errors=[],writes=[];
  let reads=0;
  const storage={
    getItem(k){reads++;return storage.read?storage.read(k,reads):(map.has(k)?map.get(k):null);},
    setItem(k,v){writes.push([k,v]);if(storage.write)return storage.write(k,v);map.set(k,v);}
  };
  const context={localStorage:storage,console:{error(...args){errors.push(args);}},
    addEventListener(type,handler){(events[type]||(events[type]=[])).push(handler);}};
  context.window=context;
  if(setup)setup(storage,map);
  vm.createContext(context);vm.runInContext(source,context);
  return {api:context.JPWModuleAvailability,context,map,storage,writes,errors,events,
    reads:()=>reads,dispatch(event){(events.storage||[]).forEach(fn=>fn(event));}};
}
test('Absent preference defaults to frozen Alladin with no incidental writes',()=>{
  const f=fixture();assert.equal(f.api.KEY,key);
  assert.deepEqual(clean(f.api.snapshot().states),{research:'active',forex:'active','personal-finance':'active',alladin:'frozen'});
  assert.equal(f.api.snapshot().writable,true);assert.equal(f.api.snapshot().confirmed,true);
  assert.equal(f.writes.length,0);assert.equal(f.map.has(key),false);
  ['dashboard','tools','settings','editor','notes','backup'].forEach(id=>assert.equal(f.api.canAccess(id),true));
  assert.equal(f.api.canAccess('alladin'),false);
});
test('Sparse valid choices preserve defaults and survive reload',()=>{
  const f=fixture(raw({alladin:'active',research:'frozen'}));
  assert.equal(f.api.canAccess('alladin'),true);assert.equal(f.api.canAccess('research'),false);
  assert.equal(f.api.getState('forex'),'active');assert.equal(f.api.reload().confirmed,true);assert.equal(f.writes.length,0);
  assert.equal(fixture(f.map.get(key)).api.getState('alladin'),'active');
});
test('Inspector is pure and validator accepts null and sparse v1',()=>{
  const f=fixture(),n=f.reads();
  assert.equal(f.api.inspect(null).valid,true);assert.equal(f.api.validate(raw({})).valid,true);
  assert.equal(f.api.inspect(raw({forex:'frozen'})).states.forex,'frozen');
  assert.equal(f.api.getState('forex'),'active');assert.equal(f.reads(),n);assert.equal(f.writes.length,0);
});
test('Invalid field fallback does not reset other valid fields or rewrite raw',()=>{
  const input=raw({research:'frozen',forex:'invalid',alladin:'active'}),f=fixture(input);
  assert.equal(f.api.getState('research'),'frozen');assert.equal(f.api.getState('alladin'),'active');assert.equal(f.api.getState('forex'),'active');
  assert.equal(f.api.snapshot().confirmed,false);assert.equal(f.api.snapshot().writable,false);
  assert.equal(f.api.setState('forex','frozen').reason,'invalid-preference');
  assert.equal(f.map.get(key),input);assert.equal(f.writes.length,0);assert.throws(()=>f.api.validate(input));
});
test('Malformed, future, unknown IDs/fields and hostile keys fail strict import without writes',()=>{
  const invalid=['','{','null','[]','true','0',raw(null),raw([]),'{"modules":{}}',
    '{"schemaVersion":2,"modules":{"alladin":"active"}}',
    '{"schemaVersion":1,"modules":{},"future":true}',raw({tools:'frozen'}),
    raw({forex:null}),raw({forex:1}),raw({forex:true}),raw({forex:{state:'active'}}),
    '{"schemaVersion":1,"modules":{"__proto__":{"polluted":true}}}',
    '{"schemaVersion":1,"modules":{"constructor":"active"}}'];
  invalid.forEach(input=>{const f=fixture(input);assert.equal(f.api.inspect(input).valid,false,input);assert.throws(()=>f.api.validate(input));
    assert.equal(f.api.setState('alladin','active').ok,false);assert.equal(f.map.get(key),input);assert.equal(f.writes.length,0);});
  const f=fixture();[undefined,1,false,{},[]].forEach(input=>assert.throws(()=>f.api.validate(input)));
  assert.equal({}.polluted,undefined);
});
test('Explicit change writes only auxiliary key and confirms through read-back',()=>{
  const f=fixture(raw({research:'frozen'})),before=f.map.get(key),calls=[];
  f.api.subscribe((snap,reason)=>calls.push([reason,snap.states.alladin]));
  const result=f.api.setState('alladin','active',{expectedRaw:before});
  assert.equal(result.ok,true);assert.equal(result.reason,'confirmed');assert.equal(f.writes.length,1);
  assert.deepEqual(JSON.parse(f.map.get(key)),{schemaVersion:1,modules:{research:'frozen',alladin:'active'}});
  assert.deepEqual(calls,[['change','active']]);assert.equal(f.map.get('jpwealth_v9_state'),'synthetic-financial-sentinel');assert.equal(f.map.get('unrelated-key'),'preserved');
  assert.equal(f.api.snapshot().lastConfirmedRaw,f.map.get(key));
});
test('Already effective state, invalid module and invalid state never write',()=>{
  const f=fixture();assert.equal(f.api.setState('alladin','frozen').reason,'unchanged');
  assert.equal(f.api.setState('dashboard','frozen').reason,'invalid-module');assert.equal(f.api.setState('forex','disabled').reason,'invalid-state');
  assert.equal(f.writes.length,0);assert.equal(f.map.has(key),false);
});
test('All four managed IDs support both states with preserved independent choices',()=>{
  const f=fixture();f.api.IDS.forEach(id=>{assert.equal(f.api.setState(id,'frozen').ok,true);assert.equal(f.api.getState(id),'frozen');});
  f.api.IDS.forEach(id=>assert.equal(f.api.canAccess(id),false));
  f.api.IDS.forEach(id=>{assert.equal(f.api.setState(id,'active').ok,true);assert.equal(f.api.getState(id),'active');});
  assert.equal(f.map.get('jpwealth_v9_state'),'synthetic-financial-sentinel');
});
test('Snapshots and pure inspect results cannot mutate the live state',()=>{
  const f=fixture(raw({alladin:'active'})),snap=f.api.snapshot();
  assert.throws(()=>{snap.states.alladin='frozen';});snap.document.modules.alladin='frozen';
  f.api.inspect(raw({alladin:'active'})).states.alladin='frozen';
  assert.equal(f.api.getState('alladin'),'active');assert.equal(f.api.snapshot().document.modules.alladin,'active');
});
test('Write exception with unchanged read-back is a refusal and safe retry remains explicit',()=>{
  const f=fixture();f.storage.write=()=>{throw new Error('synthetic quota');};
  assert.equal(f.api.setState('alladin','active').reason,'write-refused');assert.equal(f.api.getState('alladin'),'frozen');
  assert.equal(f.api.snapshot().writable,true);assert.equal(f.writes.length,1);
  f.storage.write=null;assert.equal(f.api.setState('alladin','active').ok,true);assert.equal(f.writes.length,2);
});
test('Silent refused write cannot be announced as success',()=>{
  const f=fixture();f.storage.write=()=>{};
  assert.equal(f.api.setState('alladin','active').reason,'write-refused');assert.equal(f.api.getState('alladin'),'frozen');assert.equal(f.writes.length,1);
});
test('Write that commits and then throws is confirmed only by equal read-back',()=>{
  const f=fixture();f.storage.write=(k,v)=>{f.map.set(k,v);throw new Error('after write');};
  const r=f.api.setState('alladin','active');assert.equal(r.ok,true);assert.equal(r.writeThrew,true);assert.equal(f.api.getState('alladin'),'active');
});
test('Initial inaccessible storage keeps safe in-memory defaults and prohibits writes',()=>{
  const f=fixture(null,storage=>{storage.read=()=>{throw new Error('read denied');};});
  assert.equal(f.api.snapshot().readable,false);assert.equal(f.api.snapshot().confirmed,false);assert.equal(f.api.getState('alladin'),'frozen');
  assert.equal(f.api.setState('alladin','active').reason,'read-error');assert.equal(f.writes.length,0);
  f.storage.read=null;assert.equal(f.api.reload().writable,true);assert.equal(f.writes.length,0);
});
test('Subsequent read failure preserves last confirmed choices including frozen modules',()=>{
  const f=fixture(raw({alladin:'active',forex:'frozen'}));
  f.storage.read=()=>{throw new Error('read denied');};f.api.reload();
  assert.equal(f.api.getState('alladin'),'active');assert.equal(f.api.getState('forex'),'frozen');assert.equal(f.api.snapshot().confirmed,false);assert.equal(f.writes.length,0);
});
test('Failed pre-write read does not attempt persistence',()=>{
  const f=fixture();f.storage.read=()=>{throw new Error('read denied');};
  assert.equal(f.api.setState('alladin','active').reason,'read-error');assert.equal(f.writes.length,0);
});
test('Unreadable write result stays UNKNOWN, blocks retry and requires safe reload',()=>{
  const f=fixture();f.storage.write=(k,v)=>{f.map.set(k,v);f.storage.read=()=>{throw new Error('read-back denied');};};
  assert.equal(f.api.setState('alladin','active').reason,'unknown');assert.equal(f.api.getState('alladin'),'frozen');assert.equal(f.api.snapshot().confirmed,false);
  f.api.reload();assert.equal(f.api.snapshot().blocked,'unknown');f.storage.read=null;f.storage.write=null;
  assert.equal(f.api.setState('alladin','active').reason,'unknown');assert.equal(f.writes.length,1);
  assert.equal(f.api.reload().blocked,'');assert.equal(f.api.getState('alladin'),'active');assert.equal(f.writes.length,1);
});
test('Divergent read-back retains confirmed state until explicit observation',()=>{
  const f=fixture(raw({research:'frozen'}));f.storage.write=()=>f.map.set(key,raw({forex:'frozen',alladin:'active'}));
  assert.equal(f.api.setState('alladin','active').reason,'unknown');assert.equal(f.api.getState('alladin'),'frozen');assert.equal(f.api.getState('research'),'frozen');
  assert.equal(f.api.setState('research','active').reason,'unknown');assert.equal(f.writes.length,1);
  f.api.reload();assert.equal(f.api.getState('alladin'),'active');assert.equal(f.api.getState('forex'),'frozen');assert.equal(f.api.getState('research'),'active');
});
test('Concurrent change before write is adopted without overwriting it',()=>{
  const f=fixture();f.map.set(key,raw({forex:'frozen'}));
  assert.equal(f.api.setState('alladin','active',{expectedRaw:null}).reason,'conflict');assert.equal(f.writes.length,0);assert.equal(f.api.getState('forex'),'frozen');
});
test('Stale confirmation token is rejected even after state was refreshed',()=>{
  const f=fixture();f.map.set(key,raw({research:'frozen'}));f.api.reload();
  assert.equal(f.api.setState('alladin','active',{expectedRaw:null}).reason,'conflict');assert.equal(f.writes.length,0);
});
test('Concurrent malformed value stays intact and blocks follow-up writes',()=>{
  const f=fixture();f.map.set(key,'invalid raw');assert.equal(f.api.setState('alladin','active').reason,'conflict');
  assert.equal(f.api.snapshot().blocked,'invalid-preference');assert.equal(f.api.setState('alladin','active').ok,false);assert.equal(f.map.get(key),'invalid raw');assert.equal(f.writes.length,0);
});
test('Storage changes re-read actual storage, including removal, with no writes',()=>{
  const f=fixture(),calls=[];f.api.subscribe((snap,reason)=>calls.push([reason,snap.states.alladin]));
  f.map.set(key,raw({alladin:'active'}));f.dispatch({key,newValue:'ignored',storageArea:f.storage});assert.equal(f.api.getState('alladin'),'active');
  f.map.delete(key);f.dispatch({key:null,storageArea:f.storage});assert.equal(f.api.getState('alladin'),'frozen');
  assert.deepEqual(calls,[['storage','active'],['storage','frozen']]);assert.equal(f.writes.length,0);
});
test('Unrelated and sessionStorage events do not change availability',()=>{
  const f=fixture(),reads=f.reads();f.map.set(key,raw({alladin:'active'}));
  f.dispatch({key:'unrelated-key',storageArea:f.storage});f.dispatch({key,storageArea:{}});
  assert.equal(f.reads(),reads);assert.equal(f.api.getState('alladin'),'frozen');
});
test('Subscription disposal and duplicate script evaluation do not duplicate delivery',()=>{
  const f=fixture(),same=f.api;let count=0;const dispose=f.api.subscribe(()=>count++);
  vm.runInContext(source,f.context);assert.equal(f.context.JPWModuleAvailability,same);assert.equal(f.events.storage.length,1);
  f.api.reload();dispose();f.api.reload();assert.equal(count,1);assert.equal(f.writes.length,0);
  assert.throws(()=>f.api.subscribe(null));
});
test('Broken consumer is observable and does not hide changes from other consumers',()=>{
  const f=fixture();let seen=false;f.api.subscribe(()=>{throw new Error('synthetic consumer');});f.api.subscribe(()=>{seen=true;});
  assert.equal(f.api.setState('alladin','active').ok,true);assert.equal(seen,true);assert.equal(f.errors.length,1);assert.equal(f.api.snapshot().listenerErrors,1);
});
console.log(JSON.stringify({classification:failed?'PRODUCT_FAIL':'PASS',pass:passed,fail:failed,runtime:process.version,scope:'synthetic core only; browser/backup/gate not exercised'}));
process.exitCode=failed?1:0;
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', help='Existing Node executable; no installation is performed.')
    args = parser.parse_args()
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    node = args.node or shutil.which('node') or (str(bundled) if bundled.is_file() else None)
    if not node:
        print('ENVIRONMENT_ERROR: Node unavailable; provide --node pointing to an existing executable.', file=sys.stderr)
        return 2
    try:
        result = subprocess.run([node, '-e', SCRIPT, str(SOURCE)], cwd=ROOT, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f'ENVIRONMENT_ERROR: {error}', file=sys.stderr)
        return 2
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())

/* Planning primary route must remain independent from frozen Forex. No state/IO. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const c={document:{querySelectorAll:()=>[],getElementById:()=>null},console};c.window=c;
vm.createContext(c);vm.runInContext(fs.readFileSync('src/js/40-app/01-navigation.js','utf8'),c);
const nav=c.JPWNavigation;
for(const target of ['planning','forex-planning','fxplan']){
 const r=nav.resolve(target);assert.equal(r.accepted,true,target);assert.equal(r.primary,'planning',target);
 assert.equal(r.canonical,'planning',target);assert.equal(r.screen,'planning',target);
}
assert(nav.routes().some(r=>r.id==='planning'));
assert(!nav.children('forex').some(r=>r.id==='forex-planning'));
assert.equal(nav.resolve('tools-minigames').primary,'tools');
console.log('PASS planning independent primary and legacy aliases');
const source=fs.readFileSync('src/js/20-ui/12-nav-style.js','utf8');
let raw=null;const d={localStorage:{getItem:()=>raw}};vm.createContext(d);
const constant=source.match(/const NAV_ORDER_DEFAULT=.*;/)[0];
const fn=n=>source.slice(source.indexOf('function '+n+'('),source.indexOf('\n}',source.indexOf('function '+n+'('))+2);
vm.runInContext("const NAV_ORDER_KEY='jpw_nav_order';"+constant+fn('navOrderValid')+fn('navOrderRead'),d);
assert.deepEqual(Array.from(vm.runInContext('navOrderRead().order',d)),['dashboard','research','planning','forex','personal-finance','alladin','tools']);
raw=JSON.stringify(['tools','alladin','dashboard','forex','research','personal-finance']);
assert.deepEqual(Array.from(vm.runInContext('navOrderRead().order',d)),['tools','alladin','dashboard','forex','research','planning','personal-finance']);
assert.equal(raw,JSON.stringify(['tools','alladin','dashboard','forex','research','personal-finance']));
console.log('PASS planning default order and legacy six-module preference projection without writes');

'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
(async()=>{
let calls=0,resolve;const store=new Map();
const c={console,Date,AbortController,setTimeout,clearTimeout,URLSearchParams,localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)},addEventListener(){},fetch:url=>{calls++;return new Promise(r=>resolve=()=>r({ok:true,json:async()=>({base:'USD',quote:'BRL',date:'2026-09-30',rate:5})}));}};c.window=c;vm.createContext(c);vm.runInContext(fs.readFileSync('src/js/10-domain/08-usd-brl-quote.js','utf8'),c);
assert.equal(typeof c.JPWMarket.usdBrl.historical,'function');
const ctrl=new AbortController();const a=c.JPWMarket.usdBrl.historical('2026-09',{signal:ctrl.signal}),b=c.JPWMarket.usdBrl.historical('2026-09');ctrl.abort();resolve();
assert.equal((await a).status,'unavailable');assert.equal((await b).rate,5);assert.equal(calls,1);
assert.equal((await c.JPWMarket.usdBrl.historical('2026-09')).referenceDate,'2026-09-30');assert.equal(calls,1);
assert.equal((await c.JPWMarket.usdBrl.historical('2099-01')).status,'unavailable');assert.equal((await c.JPWMarket.usdBrl.historical('bad')).rate,null);assert.equal(calls,1);
console.log('PASS historical month identity, shared fetch, consumer cancellation, cache and future rejection');
})().catch(e=>{console.error(e);process.exitCode=1;});

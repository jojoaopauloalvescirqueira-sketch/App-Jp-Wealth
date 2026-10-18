'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync('src/js/40-app/30-capital-currents/01-engine.js', 'utf8'), context);
const e = context.window.JPWCapitalCurrents.engine;
const params = {u:0,tau:1,kappa:2,depth:1,profile:'uniform'};
const near = (a,b,tol=1e-9) => assert.ok(Math.abs(a-b)<tol, `${a} != ${b}`);
function evolve(s,p,n,dt) { for(let i=0;i<n;i++) s=e.advance(s,p,dt); return s; }
// Catches replacement API missing, mutable configuration, and wrong default forcing.
test('field exposes frozen defaults and independent derivatives', () => {
  assert.equal(typeof e.fieldAt,'function'); assert.ok(Object.isFrozen(e)); assert.ok(Object.isFrozen(e.DEFAULTS));
  const v=e.fieldAt({q:0,p:0,t:0},e.DEFAULTS); near(v.dq,.4); near(v.dp,0);
});
// Independent closed-form solution to constant-depth release; catches sign, depth, and decay errors.
test('released pressure matches analytic price and pressure at one second', () => {
  for(const [depth,price] of [[1,.7585446705942692],[.5,1.5170893411885384]]) {
    const s=evolve({q:.6,p:0,t:0},{...params,depth},60,1/60);
    near(s.q,.2207276647028654); near(s.p,price); near(s.t,1);
    const neg=evolve({q:-.6,p:0,t:0},{...params,depth},60,1/60);
    near(neg.q,-s.q); near(neg.p,-s.p);
  }
});
test('zero pressure has no drift even away from reference price', () => {
  const s=e.advance({q:0,p:4,t:3},params,1); near(s.p,4); near(s.q,0); near(s.t,4);
});
// Catches p-stage evaluation frozen at initial p; refinement must approach same band solution.
test('band RK4 converges under step refinement', () => {
  const p={...params,u:.7,profile:'band'};
  const start={q:.1,p:.3,t:0};
  const a=evolve(start,p,10,.1), b=evolve(start,p,20,.05), c=evolve(start,p,40,.025);
  assert.ok(Math.abs(b.p-c.p)<Math.abs(a.p-b.p)/5);
  assert.ok(Math.abs(b.p-c.p)<.0001);
  const v=e.fieldAt({q:.5,p:1,t:0},p); near(v.depth,.4); near(v.dp,2.5);
});
test('calls preserve inputs and expose no clock randomness or storage dependencies', () => {
  const s=Object.freeze({q:.6,p:7,t:0}), p=Object.freeze({...params});
  const a=e.advance(s,p); const b=e.advance(s,p); assert.notEqual(a,s);
  assert.equal(JSON.stringify(a),JSON.stringify(b)); near(s.p,7); assert.ok(a.p>7);
  const z=e.advance(s,p,0); assert.notEqual(z,s); assert.equal(JSON.stringify(z),JSON.stringify(s));
});
test('fixed ticks yield identical results across frame partitions', () => {
  function frames(parts) { let s={q:.6,p:0,t:0}; for(const n of parts) s=evolve(s,params,n,e.DT); return s; }
  assert.equal(JSON.stringify(frames([60])),JSON.stringify(frames([1,2,7,13,37])));
});
test('trace returns fresh bounded states and stops before leaving plot', () => {
  const s={q:.9,p:5.99,t:0}; const path=e.trace(s,{...params,u:1},{steps:1000});
  assert.ok(Array.isArray(path)); assert.ok(path.length<=1001); assert.notEqual(path[0],s);
  assert.ok(path.every(x=>Math.abs(x.p)<=6 && Math.abs(x.q)<=1));
  const stationary=e.trace({q:0,p:0,t:0},params,{steps:3}); assert.equal(stationary.length,4);
  assert.throws(()=>e.trace(s,params,{steps:10001})); assert.throws(()=>e.trace(s,params,{steps:1.5}));
});
test('invalid and missing numeric inputs never silently become zero', () => {
  const s={q:0,p:0,t:0};
  for(const x of [undefined,null,'',NaN,Infinity]) {
    for(const key of ['q','p','t']) assert.throws(()=>e.advance({...s,[key]:x},params));
    for(const key of ['u','tau','kappa','depth']) assert.throws(()=>e.advance(s,{...params,[key]:x}));
    if(x!==undefined) assert.throws(()=>e.advance(s,params,x));
  }
  for(const patch of [{q:1.1},{q:-1.1},{t:-1}]) assert.throws(()=>e.advance({...s,...patch},params));
  for(const patch of [{u:2},{tau:0},{kappa:-1},{depth:.7},{profile:'other'}]) assert.throws(()=>e.advance(s,{...params,...patch}));
  for(const dt of [-1,1.1]) assert.throws(()=>e.advance(s,params,dt));
});

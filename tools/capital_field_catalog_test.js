#!/usr/bin/env node
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const box={window:{}};
for(const f of ['01-engine.js','02-scenarios.js']) vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../src/js/40-app/30-capital-currents',f),'utf8'),box);
const {catalog:c,engine:e}=box.window.JPWCapitalCurrents;
let count=0;function test(name,run){run();count++;console.log('[PASS] '+name);}
function near(a,b,tol=1e-8){assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);}
const ids=['intro-field','intro-pressure','intro-depth','release-pressure','same-pulse-depth','shallow-band'];
test('six stable frozen educational entries',()=>{
 assert.ok(Array.isArray(c.items));assert.equal(JSON.stringify(c.items.map(x=>x.id)),JSON.stringify(ids));
 assert.ok(Object.isFrozen(c.items));for(const x of c.items){assert.ok(Object.isFrozen(x));for(const key of ['title','explanation','goal','instruction','expected'])assert.ok(typeof x[key]==='string'&&x[key].length>10);assert.equal(c.get(x.id),x);}
 assert.equal(c.get('other'),null); for(const id of [...ids.slice(0,3),'other']) assert.throws(()=>c.experiment(id),/./);
});
for(const id of ids.slice(3))test('matched fresh controlled series: '+id,()=>{
 const x=c.experiment(id),y=c.experiment(id);assert.equal(x.id,id);assert.notEqual(x.a,y.a);
 assert.equal(x.a.length,x.b.length);assert.equal(JSON.stringify(x.a[0]),JSON.stringify(x.initial));assert.equal(JSON.stringify(x.b[0]),JSON.stringify(x.initial));
 near(x.a.at(-1).t,x.duration);near(x.b.at(-1).t,x.duration);
 x.a.forEach((s,i)=>{near(s.t,x.b[i].t);assert.ok(Number.isFinite(s.p));assert.ok(s.q>=-1&&s.q<=1);});
 x.a[0].p=100;assert.notEqual(c.experiment(id).a[0].p,100);
});
test('release matches analytic pressure and displacement; maintained pressure differs',()=>{
 const x=c.experiment('release-pressure');assert.equal(x.a.length,61);
 near(x.a.at(-1).q,.6*Math.exp(-1));near(x.a.at(-1).p,1.2*(1-Math.exp(-1)));
 near(x.b.at(-1).q,.6);near(x.b.at(-1).p,1.2);assert.equal(x.paramsA.u,0);assert.equal(x.paramsB.u,.6);
});
test('same pulse differs only by depth and doubles price at every tick',()=>{
 const x=c.experiment('same-pulse-depth');assert.equal(x.a.length,271);near(x.duration,4.5);
 x.a.forEach((s,i)=>{near(s.q,x.b[i].q);near(2*s.p,x.b[i].p);});
 near(x.a[90].q,.8*(1-Math.exp(-1.5)));near(x.a.at(-1).q,.8*(1-Math.exp(-1.5))*Math.exp(-3));
 near(x.a.at(-1).p,2*.8*(1.5-(1-Math.exp(-1.5))*Math.exp(-3)));
 assert.match(x.labelA,/0[,.]8/);assert.match(x.labelA,/1[,.]5/);assert.match(x.labelA,/3/);
});
test('shallow band follows independent depth integral and local velocity',()=>{
 const x=c.experiment('shallow-band');assert.equal(x.a.length,301);near(x.a.at(-1).p,3);
 // Composite Simpson integral of D(p) equals kappa*q*elapsed for constant q.
 const lo=-1,hi=x.b.at(-1).p,n=20000,h=(hi-lo)/n;
 const d=p=>1-.6*Math.exp(-(((p-1)/.8)**2));let total=d(lo)+d(hi);
 for(let i=1;i<n;i++)total+=(i%2?4:2)*d(lo+i*h);
 near(total*h/3,4,2e-7);assert.ok(x.b.at(-1).p>x.a.at(-1).p);
 const s={q:.4,p:1,t:0};near(e.fieldAt(s,x.paramsB).depth,.4);near(e.fieldAt(s,x.paramsB).dp,2);
 near(e.fieldAt({q:0,p:1,t:0},{...x.paramsB,u:0}).dp,0);
});
console.log(`PASS ${count}/${count} field catalog contracts`);

'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const context={console,Intl,Date,Object,Map,Set,WeakMap,WeakSet,Number,JSON,Error};context.globalThis=context;vm.createContext(context);
vm.runInContext(fs.readFileSync('src/js/40-app/31-market-hours/01-sessions.js','utf8'),context);
assert.ok(context.JPWForexSessions,'Approved four-centre FX session model is missing');
const model=context.JPWForexSessions,pref=context.JPWMarketSessionsViewPreference;
assert.ok(pref,'Backup-compatible view preference validator is missing');
assert.equal(pref.key,'jpwealth_market_sessions_view_v1');
for(const zone of ['device','UTC','Australia/Sydney','Asia/Tokyo','Europe/London','America/New_York','America/Sao_Paulo'])assert.equal(pref.validate(JSON.stringify({schemaVersion:1,timeZone:zone})).timeZone,zone);
for(const raw of ['{}','null','[]','{"schemaVersion":2,"timeZone":"UTC"}','{"schemaVersion":1,"timeZone":"EST"}','{"schemaVersion":1,"timeZone":"UTC","token":"secret"}'])assert.throws(()=>pref.validate(raw));
const original=JSON.parse(fs.readFileSync('src/data/market-hours/forex-sessions-v1.json')),before=JSON.stringify(original),catalog=model.prepare(original);
assert.equal(JSON.stringify(original),before);assert.ok(Object.isFrozen(catalog));
const ids=['fx-sydney','fx-tokyo','fx-london','fx-new-york'];assert.deepEqual(Array.from(catalog.venues,v=>v.id),ids);
function state(iso,id){return model.at(catalog,Date.parse(iso)).venues.find(v=>v.id===id);}
assert.equal(state('2026-10-26T07:59:59Z','fx-london').phase,'closed');
assert.equal(state('2026-10-26T08:00:00Z','fx-london').phase,'continuous');
assert.equal(state('2026-10-26T16:00:00Z','fx-london').phase,'closed');
assert.equal(state('2026-10-23T07:00:00Z','fx-london').phase,'continuous');
assert.equal(state('2026-10-30T12:00:00Z','fx-new-york').phase,'continuous');
assert.equal(state('2026-11-02T12:59:59Z','fx-new-york').phase,'closed');
assert.equal(state('2026-11-02T13:00:00Z','fx-new-york').phase,'continuous');
assert.equal(state('2026-11-01T20:00:00Z','fx-sydney').phase,'continuous');
assert.equal(state('2026-10-31T08:00:00Z','fx-london').phase,'closed');
assert.equal(state('2027-01-05T08:00:00Z','fx-london').phase,'unknown');
const fall=model.timeline(catalog,Date.parse('2026-11-01T14:00:00Z'),'America/New_York');assert.equal(fall.untilUtc-fall.fromUtc,25*3600000);assert.equal(fall.ticks.filter(t=>t.label.startsWith('01:00')).length,2);
const spring=model.timeline(catalog,Date.parse('2026-03-08T14:00:00Z'),'America/New_York');assert.equal(spring.untilUtc-spring.fromUtc,23*3600000);
const utc=model.timeline(catalog,Date.parse('2026-11-02T01:00:00Z'),'UTC');const syd=utc.rows.find(r=>r.id==='fx-sydney');assert.ok(syd.segments.some(s=>s.fromUtc===utc.fromUtc),'Cross-midnight FX must continue from previous local date');
assert.equal(model.timeline(catalog,Date.parse('2027-01-05T00:00:00Z'),'UTC'),null);assert.throws(()=>model.timeline(catalog,Date.now(),'Invalid/Zone'));
assert.equal(Object.hasOwn(model.at(catalog,Date.parse('2026-11-02T14:00:00Z')),'marketOpen'),false,'No universal tradability assertion');
const parisSpring=model.timeline(catalog,Date.parse('2026-03-29T12:00:00Z'),'Europe/Paris',{device:true});assert.equal(parisSpring.untilUtc-parisSpring.fromUtc,23*3600000);
const parisFall=model.timeline(catalog,Date.parse('2026-10-25T12:00:00Z'),'Europe/Paris',{device:true});assert.equal(parisFall.untilUtc-parisFall.fromUtc,25*3600000);assert.equal(parisFall.ticks.filter(t=>t.label==='02:00').length,2);
const kolkata=model.timeline(catalog,Date.parse('2026-10-28T14:00:00Z'),'Asia/Kolkata',{device:true});assert.equal(kolkata.fromUtc,Date.parse('2026-10-27T18:30:00Z'));assert.equal(kolkata.untilUtc,Date.parse('2026-10-28T18:30:00Z'));assert.equal(kolkata.ticks[0].offset,'+0530');
const civilBoundaryFailures=[];
for(const [zone,start,end] of [['Europe/Paris','2025-12-31T23:00:00Z','2026-12-31T23:00:00Z'],['Asia/Kolkata','2025-12-31T18:30:00Z','2026-12-31T18:30:00Z']]){
  for(const [instant,expected] of [[Date.parse(start)-1,null],[Date.parse(start),'2026-01-01'],[Date.parse(end)-1,'2026-12-31'],[Date.parse(end),null]]){
    const actual=model.timeline(catalog,instant,zone,{device:true})?.date??null;
    if(actual!==expected)civilBoundaryFailures.push({zone,instant:new Date(instant).toISOString(),expected,actual});
  }
}
assert.deepEqual(civilBoundaryFailures,[],'Device timeline horizon must follow the projected civil date, not the UTC calendar year');
assert.equal(model.timeline(catalog,Date.parse('2025-12-31T23:30:00Z'),'Europe/Paris',{device:true}).date,'2026-01-01');
assert.equal(state('2025-12-31T23:30:00Z','fx-sydney').phase,'continuous');
assert.throws(()=>model.timeline(catalog,Date.parse('2026-10-28T14:00:00Z'),'Asia/Kolkata'));
assert.throws(()=>pref.validate('{"schemaVersion":1,"timeZone":"Asia/Kolkata"}'));
console.log('PASS forex sessions: conventions, boundaries, DST, Sunday, horizon, timezone projection and preference validation');
